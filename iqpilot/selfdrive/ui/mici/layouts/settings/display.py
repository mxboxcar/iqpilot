from iqpilot.common.ui_settings import DISPLAY_BRIGHTNESS_VALUES, SLEEP_TIMER_VALUES
from iqpilot.selfdrive.ui.mici.layouts.settings.iq_widgets import MappedParamToggle
from iqpilot.selfdrive.ui.ui_state import NIGHT_MODE_BASE
from iqpilot.system.ui.widgets.scroller import NavScroller
from iqpilot.system.ui.lib.multilang import tr

# lynx: "driving brightness" = auto (light sensor), or "auto / night N%": light sensor by day,
# a fixed N% after sunset. Values NIGHT_MODE_BASE.. (see ui_state.NIGHT_MODE_BASE).
_NIGHT_BRIGHT_OPTIONS = [f"auto / night {p}%" for p in range(5, 101, 5)]
_ONROAD_BRIGHT_OPTIONS = ["auto"] + _NIGHT_BRIGHT_OPTIONS
_ONROAD_BRIGHT_VALUES = [0] + list(range(NIGHT_MODE_BASE, NIGHT_MODE_BASE + len(_NIGHT_BRIGHT_OPTIONS)))


class DisplayLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    brightness = list(DISPLAY_BRIGHTNESS_VALUES.values())
    self._display_bright = MappedParamToggle(tr("display brightness"), "Brightness",
                                             [tr("default") if v == 0 else f"{v}%" for v in brightness], brightness)
    self._onroad_bright = MappedParamToggle(tr("driving brightness"), "OnroadScreenOffBrightness",
                                            [tr(o) if o == "auto" else o for o in _ONROAD_BRIGHT_OPTIONS],
                                            _ONROAD_BRIGHT_VALUES)
    self._interact = MappedParamToggle(tr("sleep timer"), "InteractivityTimeout",
                                       [tr("default"), "30s", "1m", "2m"], list(SLEEP_TIMER_VALUES.values()))
    self._items = [self._display_bright, self._onroad_bright, self._interact]
    self._scroller.add_widgets(self._items)

  def show_event(self):
    super().show_event()
    for item in self._items:
      item.refresh()
