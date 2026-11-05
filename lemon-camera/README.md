# lemon-camera

One photo a day of the potted lemon tree on the deck, sent over wifi to the
Windows PC. Battery powered. No app, no cloud, no subscription.

- **Setting it up:** [SETUP.md](SETUP.md) — step by step, no command window.
- **Battery life:** [POWER.md](POWER.md) — estimate with sources, and what to
  measure.
- **Outdoor box:** [ENCLOSURE.md](ENCLOSURE.md) — sealing, condensation, cold.

```
firmware/lemon_camera/     the camera program (Arduino)
  lemon_camera.ino           hardware: camera, clock chip, wifi, power
  lemon_logic.h              decisions: when to wake, what to send (tested on a PC)
  config.example.h           copy to config.h and fill in (config.h is git-ignored)
  partitions.csv             flash layout with room for held photos
receiver/                  the PC side (Python 3.8+, standard library only)
  Start Lemon Receiver.bat   double-click: waits for photos
  Make Time-lapse.bat        double-click: builds the video
  lemon_receiver.py, timelapse.py
tests/                     everything that runs without the camera
```

## How a day goes

At the set time (noon by default) the board's clock chip (BM8563) switches the
board on. The firmware latches the power, arms a *fallback* wake for tomorrow
straight away (so a hang can't strand it), takes one 2048×1536 JPEG after
four warm-up frames for exposure, saves it to flash, switches the camera off,
reads the battery, joins wifi, sets its clock from the internet, posts every
saved photo to the PC oldest first, deletes each one the PC accepts, arms the
next alarm, and releases the power latch. On battery that cuts power to
everything except the clock chip. The LED is never turned on.

**Limits on a bad night:** wifi gets 20 s; the whole wake gets 45 s, then a
timer cuts power regardless; a failed send gets at most 2 retry wakes an hour
apart that day, then waits for tomorrow. All four numbers are in `config.h`.

**Aiming mode:** after every new upload of the firmware, the first 30 wakes
are one a minute and send pictures to `LemonTree\aim\`. Aiming pictures that
fail to send are dropped, not held.

## Upload format (extensible)

`POST http://<pc>:8080/upload?<key=value&...>` with the raw JPEG as the body.

| key | example | meaning |
|---|---|---|
| `v` | `1` | format version |
| `kind` | `daily`, `held`, `aim` | `held` = a photo from an earlier day sent late |
| `taken` | `2026-11-05T12:00:03-05:00` | local time with UTC offset (absent if the clock was unknown) |
| `date` | `2026-11-05` | the day the photo belongs to (absent if unknown → PC date used) |
| `battery_v` | `3.950` | battery volts, read before wifi starts |
| `boot` | `12` | wake counter |
| `held` | `0` | photos still waiting on the board after this one |

The receiver saves the photo, writes known columns to `battery-log.csv`, puts
any other keys in that file's `other` column, and writes *every* key to
`uploads.jsonl`. A temperature sensor later only needs to add e.g.
`&temp_c=4.5` (there's an `extra` field in `UploadInfo` for this); the
receiver needs no change. Any 2xx reply means "got it, delete your copy".
A second photo for a day that already has one goes to `extras\` and still gets
200, so the board doesn't keep resending it.

## Decisions, and why

- **Arduino core + the bundled `esp32-camera` driver, not M5Stack's TimerCam
  library.** As far as I know the library's `timerSleep(seconds)` uses the
  BM8563's countdown timer, which tops out at 255 minutes, so it can't
  express "once a day". A daily wake needs the chip's alarm registers, so I
  wrote a ~60-line BM8563 driver from the datasheet's register map (the chip is
  PCF8563-compatible). That leaves no third-party library to install, which
  makes SETUP.md shorter. ESP-IDF would also work but is a much harder flashing
  story for a non-technical owner.
- **Clock chip runs in UTC; the time zone rule is applied in software**, so
  daylight-saving changes need no attention (tested across both 2026/27
  changes).
- **Every daily photo is written to flash before any wifi**, and sent from
  flash. That leaves one path for "send now" and "send later", and a photo
  survives a hang or a cut-off mid-upload.
- **Video without dependencies:** the time-lapse is an MJPEG AVI written with
  the standard library; the daily JPEGs go in unchanged. The test suite checks
  it with ffprobe when that's installed.

## Can it hold a photo when the PC is unreachable? (researched)

Yes, in flash, and only in flash:

- **PSRAM (8 MB) and the ESP32's RTC memory don't help.** On battery the
  board's power is completely cut between wakes, so both are wiped. (RTC
  memory only survives ESP32 deep sleep, which this board doesn't use on
  battery.)
- **Flash is 4 MB** (M5Stack docs). The program needs well under 1.5 MB, so
  `partitions.csv` gives 2.375 MB to a LittleFS storage area. A QXGA JPEG at
  quality 10 is typically 300–600 KB (estimate — check the real files), and the
  firmware keeps 664 KB free for the next one, so **about 3–5 days of photos**
  can wait. When it's full, the oldest is dropped.
- Flash wear isn't a concern at one write a day; LittleFS spreads the wear.

## What is not verified

Be clear on this before the first plug-in:

1. **The firmware has never been compiled.** The Arduino toolchain download
   wasn't permitted in the environment this was written in. The logic in
   `lemon_logic.h` is compiled and tested on Linux with g++. The `.ino` passes
   a g++ syntax check against hand-written stand-ins for the Arduino/ESP32
   headers. That catches typos and type mistakes in this code, but it can't
   prove the real library signatures match. Expect possibly a small compile fix the first
   time (most likely spots: `camera_config_t` field names, which changed between
   esp32-camera versions — `pin_sccb_sda` vs `pin_sscb_sda` — and
   `ADC_11db` deprecation warnings on core 3.x).
2. **The power-off / RTC wake sequence is from M5Stack's docs**, not from
   running it: G33 high holds power, releasing it cuts power on battery, the
   BM8563 interrupt switches it back on. The docs confirm the board stays on
   while USB is connected, so on USB the firmware falls back to ESP32 deep
   sleep for the same duration.
3. **Pins** (G33 hold, G38 battery, G12/G14 clock, G2 LED, camera pins) are
   from M5Stack's docs; the camera pin list matches the commonly published
   Timer Camera X map.
4. **Battery voltage factor** (÷0.661) is from M5Stack's TimerCam code, from
   memory, not checked against a meter. Calibrate it (POWER.md).
5. **Image orientation** (`FLIP_VERTICAL 1`) is a guess; aiming mode shows it.
6. **That Arduino picks up `partitions.csv` from the sketch folder.** That's
   how arduino-esp32 has worked since 2.0, but it's not checked with the
   M5Stack-Timer-CAM board entry. If the Serial Monitor shows "flash storage
   could not be mounted", it didn't.
7. **Power figures** — estimates, see POWER.md.
8. The receiver and time-lapse are tested on Linux with Python 3.13, not yet on
   Windows. They use nothing platform-specific except the `.bat` files.

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

```bash
sh tests/firmware/run.sh
```
