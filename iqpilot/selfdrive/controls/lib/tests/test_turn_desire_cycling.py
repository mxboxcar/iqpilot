from types import SimpleNamespace

import numpy as np
import pytest

from iqpilot.cereal import custom, log
from iqpilot.selfdrive.controls.lib.desire_helper import (
  DesireHelper,
  TURN_DESIRE_PULSE_CYCLE_FRAMES,
  TURN_DESIRE_PULSE_HOLD_FRAMES,
)


TurnDirection = custom.IQTurnSignalDirection
MODEL_HISTORY_FRAMES = 100


def helper(v_ego=0.0, yaw_rate=0.0):
  result = DesireHelper.__new__(DesireHelper)
  result._last_carstate = SimpleNamespace(vEgo=v_ego, yawRate=yaw_rate)
  result.turn_desire_frames = 0
  result.turn_desire_cycle_input = log.Desire.none
  result.nav_turn_direction = TurnDirection.none
  result.lane_turn_direction = TurnDirection.none
  result.lane_change_direction = log.LaneChangeDirection.none
  result.lane_change_state = log.LaneChangeState.off
  result.desire = log.Desire.none
  return result


def visible_pulses(outputs):
  previous = log.Desire.none
  rising = []
  for output in outputs:
    rising.append(output != log.Desire.none and previous != output)
    previous = output
  rising = np.array(rising)
  return np.array([rising[max(0, i - MODEL_HISTORY_FRAMES + 1):i + 1].sum() for i in range(len(rising))])


@pytest.mark.parametrize("source", ["manual", "nav"])
@pytest.mark.parametrize("v_ego,yaw_rate", [(0.0, 0.0), (6.0, 0.0), (4.0, 0.3)])
def test_turn_desire_keeps_exactly_one_pulse_in_model_history(source, v_ego, yaw_rate):
  h = helper(v_ego, yaw_rate)
  if source == "manual":
    h.lane_turn_direction = TurnDirection.turnLeft
  else:
    h.nav_turn_direction = TurnDirection.turnLeft

  outputs = []
  for _ in range(4 * TURN_DESIRE_PULSE_CYCLE_FRAMES):
    h._pick_desire_output()
    outputs.append(h.desire)

  gaps = [i for i, output in enumerate(outputs) if output == log.Desire.none]
  assert gaps[0] == TURN_DESIRE_PULSE_HOLD_FRAMES
  assert np.diff(gaps).tolist() == [TURN_DESIRE_PULSE_CYCLE_FRAMES] * (len(gaps) - 1)
  assert set(visible_pulses(outputs)[MODEL_HISTORY_FRAMES:].tolist()) == {1}


def test_new_turn_direction_restarts_pulse_immediately():
  h = helper()
  for _ in range(TURN_DESIRE_PULSE_HOLD_FRAMES // 2):
    assert h._pulse_turn_desire(log.Desire.turnLeft) == log.Desire.turnLeft
  assert h._pulse_turn_desire(log.Desire.turnRight) == log.Desire.turnRight
  assert h.turn_desire_cycle_input == log.Desire.turnRight
  assert h.turn_desire_frames == 1


def test_lane_change_desires_pass_through_and_reset_pulse():
  h = helper()
  h._pulse_turn_desire(log.Desire.turnLeft)
  assert h._pulse_turn_desire(log.Desire.laneChangeLeft) == log.Desire.laneChangeLeft
  assert h.turn_desire_frames == 0
  assert h.turn_desire_cycle_input == log.Desire.none
