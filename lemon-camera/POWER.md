# Power budget

**Everything below is an estimate built from published figures. None of it
has been measured on this board yet.** The last section lists what to measure
and how.

## Published figures used

| Figure | Value | Source |
|---|---|---|
| Battery | 140 mAh, 3.7 V LiPo | M5Stack Timer Camera X docs [1] |
| Board "off" current (RTC running, ESP32 unpowered) | 2 µA | M5Stack docs [1]; repeated by Pimoroni [2]. The CircuitPython board page says ~10 µA [3] — treat 2–10 µA as the range |
| ESP32 Wi-Fi transmit, 802.11b @ +19.5 dBm | 240 mA | ESP32 datasheet RF current table [4] (read from a secondary copy [5]; I could not open Espressif's PDF directly) |
| ESP32 Wi-Fi receive / listen | 95–100 mA | same table [4][5] |
| M5Stack's own battery claim | one timed photo per hour, "more than one month" | M5Stack docs [1] |

Not found as a published figure: the OV3660's current during capture on this
board, and the ESP32 + PSRAM current while compressing a full-resolution
JPEG. I've estimated these below at 150 mA total while awake without Wi-Fi.
That number is a guess.

## One normal day (estimate)

| Phase | Time | Average current | Charge |
|---|---|---|---|
| Boot, camera warm-up (4 throw-away frames), capture, write to flash | ~4 s | ~150 mA (guess) | 0.17 mAh |
| Join Wi-Fi, get time, upload ~0.5 MB, wait for reply | ~6 s | ~120 mA (mostly receive, bursts of 240 mA) | 0.20 mAh |
| Off for the rest of the day | 24 h | 2–10 µA | 0.05–0.24 mAh |
| **Total per day** | | | **≈ 0.4–0.6 mAh** |

Cross-check: M5Stack's claim works out to ≤ 0.19 mAh per wake (24 wakes a day
for 30 days on 140 mAh), probably with smaller pictures. My 0.37 mAh per wake
is about twice that, which is reasonable for a full 3 MP photo plus four
warm-up frames.

### What that means

- Usable capacity, allowing for the battery not being run flat: about 110 mAh.
- **Load alone: roughly 6–9 months.**
- **But LiPo self-discharge is about as big as the load.** Commonly quoted
  rates are 2–5 % a month, i.e. 3–7 mAh a month on this battery (about
  0.1–0.2 mAh a day). Counting that, **expect around 3–5 months per charge,
  less in cold weather.**
- **Cold:** a lithium battery gives noticeably less of its capacity near
  freezing, and its voltage sags under the Wi-Fi bursts. A Durham winter
  night is fine for an off board, but a cold noon wake may show a lower
  voltage in the log than a warm one at the same charge. Never charge it below
  0 °C (it only charges from USB, so bring it inside to charge).

### Bad nights (the reason for the limits)

- A wake that fails is cut off at `MAX_AWAKE_SECONDS` (45 s): at most
  ~45 s × 150 mA ≈ **1.9 mAh**.
- With `MAX_RETRIES_PER_DAY = 2`, the worst day is 3 such wakes ≈ **5.6 mAh**.
  A whole week of the router being down costs about a third of the battery,
  not all of it. Set retries to 0 to make a bad day cost ~1.9 mAh.
- **Aiming mode** (30 pictures, one a minute) costs roughly 30 × 0.4 mAh ≈
  **12 mAh**. Do the aiming with USB plugged in if you can.

## What must be measured on the real board

1. **Off current.** Battery connected, board asleep, meter in series with the
   battery. Needs a meter that reads microamps (a µCurrent, Nordic PPK2, or a
   good multimeter on its µA range — the board won't boot through the µA
   range, so switch ranges after it is asleep). 2 µA vs 10 µA is the
   difference between 0.05 and 0.24 mAh a day.
2. **Charge per wake.** Ideally a PPK2 or similar on the battery side for a
   whole wake. Cheaper: the serial log prints milliseconds at every step, so
   you get the time per phase, and a USB meter gives the rough current.
   A USB-port meter does **not** measure the battery path and over-reads
   because of the charger.
3. **Real awake time.** From the serial log: how long Wi-Fi join takes from the
   deck, and how long the upload takes. If Wi-Fi join is slow, a fixed IP for
   the camera (router DHCP reservation) usually shortens it.
4. **Battery voltage calibration.** The firmware uses M5Stack's divider factor
   (pin mV ÷ 0.661). Compare the logged `battery_v` with a multimeter across
   the battery and set `BATTERY_CALIBRATION` in `config.h`.
5. **Photo size.** Look at the saved JPEGs. If they are much bigger than
   0.6 MB, upload time and flash storage both change.
6. **Discharge curve.** Simplest real test: let it run, and watch
   `battery-log.csv`. Recharge around 3.5 V; it will likely brown out around
   3.3 V.

## Sources

1. M5Stack, Timer Camera X documentation — https://docs.m5stack.com/en/unit/timercam_x
2. Pimoroni, Timer Camera X product page — https://shop.pimoroni.com/products/esp32-psram-timer-camera-x-ov3660
3. CircuitPython, M5Stack Timer Camera X board page — https://circuitpython.org/board/m5stack_timer_camera_x
4. Espressif, ESP32 Series Datasheet, RF power-consumption table — https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
5. Mischianti, "ESP32 practical power saving: manage WiFi and CPU – 1" (reproduces the datasheet table) — https://mischianti.org/esp32-practical-power-saving-manage-wifi-and-cpu-1
