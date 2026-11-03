# lynx r2 — port onto IQ.Pilot Prebuilt Release @ 09660bc (11fcd74)

lynx r1 was built on the source release d237c37 (needs a compile); this branch re-applies the
same changes on top of the current prebuilt release so it boots on a freshly installed device.
Merge decisions: upstream jerk curve kept (+ lynx up-only throttle cap J_CRUISE_UP=0.6);
upstream's own Chill/follow-distance handling kept (lynx's equivalent edits were dropped);
steering page: upstream turn guards kept, NNFF toggle removed upstream, lane offset + smoothing added;
display page: "driving brightness" = auto or "auto / night N%"; Tesla scroll-wheel cancel moved to
artifacts/package_runtime/iqdbc/lvbs/car/tesla/iq_carstate.py. Not yet tested on a car.

---

# lynx — บันทึกการแก้ไข (fork ของ mxboxcar)

Fork ส่วนตัวของ IQ.Pilot สำหรับ **Tesla Model 3 (ไม่มีก้านเกียร์) บน comma four**
Branch: `tesla-scrollwheel-cancel` · Base: IQ.Pilot release (prebuilt `b073c51`)

> ขอบเขต: การแก้ทั้งหมด**ไม่แตะ panda safety และค่าจำกัดการเร่ง/เบรก**

## สรุปการแก้ 5 อย่าง

| # | commit | เรื่อง | ไฟล์ |
|---|--------|--------|------|
| 1 | `0790916` | ลูกกลิ้งขวา = cancel/disengage (ไม่ต้องเหยียบเบรก) | `artifacts/package_runtime/iqdbc/lvbs/car/tesla/iq_carstate.py` |
| 2 | `c855010` | ปิดเสียงไม่วิกฤต (รวม blind spot) | `iqpilot/selfdrive/ui/soundd.py` |
| 3 | `a6b1e68` | ความสว่าง กลางวัน auto / กลางคืน N% | `iqpilot/selfdrive/ui/ui_state.py`, `.../mici/layouts/settings/display.py` |
| 4 | `1e1292a` | lane offset (ชิดขวา) + ชื่อ fork "lynx 1.0" | `.../mici/layouts/settings/steering.py`, `iqpilot/common/version.h` |

---

### 1. ลูกกลิ้งขวา = cancel (`0790916`)
- อ่าน `VCLEFT_swcRightPressed` (ค่า 2 = กด) จาก **vehicle bus** (`Bus.adas`) ส่งเป็น `ButtonType.cancel` → `EventName.buttonCancel` → disengage ทั้งพวงมาลัย+longitudinal
- **ต้องมี vehicle bus tap** (`HAS_VEHICLE_BUS`) ถ้ากดแล้วไม่มีผล = harness ไม่มี tap → ต้องเปลี่ยนไปใช้ party-bus `UI_warning.scrollWheelPressed` แทน (แม่นน้อยกว่า: จับทุกลูกกลิ้ง/ทิศ)

### 2. ปิดเสียงไม่วิกฤต (`c855010`)
- `MUTED_ALERTS` ใน `soundd.py` เงียบ: engage, disengage, refuse, prompt, promptRepeat, promptSingleLow/High
- **คงเสียงวิกฤตไว้**: warningSoft, warningImmediate, promptDistracted
- blind spot ใช้ `AudibleAlert.prompt` → เงียบด้วย (alert บนจอยังแสดง)

### 3. ความสว่าง กลางวัน auto / กลางคืน N% (`a6b1e68`)
- ต่อยอดค่า param เดิม `OnroadScreenOffBrightness`: ค่า ≥ `NIGHT_MODE_BASE (22)` = "กลางวัน auto / กลางคืน (ค่า−21)×5 %"
- **ตั้งค่า:** Settings → Display → "driving brightness" → เลือก `auto / night 40%` (ปรับ 5–100%)
- ทำแบบนี้เพราะเพิ่ม param ใหม่ไม่ได้ (`params_pyx.so` เป็น binary ไม่มี source)

### 4. lane offset ชิดขวา (`1e1292a`)
- เพิ่ม UI ให้ param เดิม `CameraOffset` (เมตรจากกลางเลน, **บวก = ขวา**, clamp ±0.35 m)
- ทำงานโดย **shear ภาพเข้าโมเดล** (`iqmodeld`) ไม่ใช่ inject curvature → ไม่ส่าย
- **ตั้งค่า:** Settings → Steering → "lane offset" → `right 0.10 m` (ปรับ ±0.30 m ทีละ 0.05)
- ⚠️ ทดสอบทิศที่ความเร็วเดินเท้าในลานจอดก่อน ยืนยันว่าเบี่ยงขวาจริง

### 4b. ชื่อ fork (`1e1292a`)
- `version.h`: `COMMA_VERSION "lynx 1.0"` (แสดงบนจอ)

---

## การติดตั้ง (comma four, IQ.OS)
```
ssh iq@<device-ip>
git remote add lynx https://github.com/mxboxcar/iqpilot && iq switch lynx tesla-scrollwheel-cancel
```
เครื่อง compile ใหม่ตอน boot → จอขึ้น "lynx 1.0" = สำเร็จ

## การย้อนกลับ
- ย้อนทีละอย่าง: `git revert <commit-hash>`
- กลับ IQ.Pilot official: `iq switch <remote> release` หรือติดตั้งใหม่ผ่าน `installer.iqlvbs.com/release`
