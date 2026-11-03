# lynx — personal fork notes

This branch (`lynx`) is the single source of truth for the customizations running on the car.

## Workflow (no computer needed)
1. Edit files on GitHub (web / mobile app).
2. SSH into the comma from the phone (car parked) and run:
   - `bash /data/lynx_personal/lynx-update.sh --check`    what is new (changes nothing)
   - `bash /data/lynx_personal/lynx-update.sh --apply`    fast-forward + syntax check + auto rollback
   - `bash /data/lynx_personal/lynx-update.sh --rollback` back to before the last update
   - `bash /data/lynx_personal/lynx-update.sh --params` / `--apply-params`  show / apply `lynx/params.json`
3. Turn the car off and on so the new code is loaded.

## Rules the update script enforces
- fast-forward only, car must be off (offroad), tracked files must be clean
- native code (.cc .h .pyx .so .capnp SConscript params_keys.h) is refused: the car cannot rebuild safely
- files touching control/safety paths need an explicit `--allow-control`
- never kill `soundd` on a running car: the manager does not restart it and openpilot becomes unavailable

## Not in git
- the `iqdbc` package edits in the venv (HW4_GEN2 fix, vehicle_bus_seen)
- anything outside `lynx/params.json` (only whitelisted params are ever applied)

## Conventions
- `CameraOffset`: NEGATIVE = right (the shear sign is inverted vs the old code comment)
- `ModelLatSmoothSec`: centiseconds, 0..20 on the on-screen toggle (8 = 0.08 s); needs `ModelSmoothingEnabled=1`
