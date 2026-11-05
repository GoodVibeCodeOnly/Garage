// lemon-camera: one photo a day of the lemon tree.
// Board: M5Stack Timer Camera X (ESP32, OV3660, BM8563 RTC, 8 MB PSRAM, 4 MB flash)
//
// One wake, top to bottom:
//   1. Grab the power latch, LED off, start the hard time limit.
//   2. Read the real-time clock, and at once arm a fallback alarm so that even
//      if this wake hangs, the board still wakes tomorrow.
//   3. Take the picture (if this is a photo wake), save it to flash, camera off.
//   4. Join wifi (with a time limit), set the clock from the internet, send
//      every held picture to the PC, delete each one the PC accepts.
//   5. Arm the RTC alarm for the next wake and release the power latch.
//      On battery that cuts power to everything except the RTC.
//
// Pins and the BM8563 register map are from M5Stack's published docs and the
// BM8563/PCF8563 datasheet. THIS FILE HAS NOT BEEN COMPILED OR RUN ON THE BOARD
// YET - see README.md, "What is not verified".

#if __has_include("config.h")
#include "config.h"
#else
#error "Missing config.h: copy config.example.h to config.h and fill it in (see SETUP.md step 4)."
#endif

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <LittleFS.h>
#include <esp_camera.h>
#include <esp_sleep.h>
#include <esp_timer.h>
#include <esp_sntp.h>
#include <sys/time.h>
#include <vector>
#include <algorithm>

#include "lemon_logic.h"

using namespace lemon;

// ---- Timer Camera X wiring (M5Stack docs) --------------------------------
static const int PIN_POWER_HOLD = 33;  // HIGH keeps the battery connected
static const int PIN_LED        = 2;   // status LED, HIGH = on
static const int PIN_BATTERY    = 38;  // battery through a resistor divider
static const int PIN_RTC_SDA    = 12;
static const int PIN_RTC_SCL    = 14;

static const uint8_t RTC_ADDR = 0x51;  // BM8563

// ---- small helpers ---------------------------------------------------------
static void logf(const char* fmt, ...) {
  char buf[200];
  va_list ap;
  va_start(ap, fmt);
  vsnprintf(buf, sizeof buf, fmt, ap);
  va_end(ap);
  Serial.printf("[%6lu ms] %s\n", (unsigned long)millis(), buf);
}

// ---- BM8563 real-time clock ---------------------------------------------
static bool rtcWrite(uint8_t reg, const uint8_t* data, size_t n) {
  Wire.beginTransmission(RTC_ADDR);
  Wire.write(reg);
  Wire.write(data, n);
  return Wire.endTransmission() == 0;
}
static bool rtcWrite1(uint8_t reg, uint8_t v) { return rtcWrite(reg, &v, 1); }
static bool rtcRead(uint8_t reg, uint8_t* data, size_t n) {
  Wire.beginTransmission(RTC_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)RTC_ADDR, (int)n) != (int)n) return false;
  for (size_t i = 0; i < n; i++) data[i] = Wire.read();
  return true;
}

// Control/Status 2 (0x01): bit3 AF alarm flag, bit2 TF timer flag,
// bit1 AIE alarm interrupt enable, bit0 TIE timer interrupt enable.
// Clearing the flags releases the interrupt line that switched the board on.
static void rtcClearAndDisable() {
  rtcWrite1(0x01, 0x00);
  rtcWrite1(0x0E, 0x03);  // timer off (TE=0), slowest source
  uint8_t alarmsOff[4] = {0x80, 0x80, 0x80, 0x80};
  rtcWrite(0x09, alarmsOff, 4);
}

// Returns UTC epoch, or 0 if the RTC lost power / was never set (VL bit).
static time_t rtcGetUtc() {
  uint8_t r[7];
  if (!rtcRead(0x02, r, 7)) return 0;
  if (r[0] & 0x80) return 0;  // VL: clock integrity not guaranteed
  time_t epoch = utcFromFields(2000 + fromBcd(r[6]), fromBcd(r[5] & 0x1F), fromBcd(r[3] & 0x3F),
                               fromBcd(r[2] & 0x3F), fromBcd(r[1] & 0x7F), fromBcd(r[0] & 0x7F));
  return clockIsSane(epoch) ? epoch : 0;
}

static void rtcSetUtc(time_t utc) {
  struct tm u;
  gmtime_r(&utc, &u);
  uint8_t r[7] = {
    toBcd(u.tm_sec), toBcd(u.tm_min), toBcd(u.tm_hour), toBcd(u.tm_mday),
    (uint8_t)u.tm_wday, toBcd(u.tm_mon + 1), toBcd(u.tm_year % 100)};
  rtcWrite(0x02, r, 7);
}

// Wake at a UTC instant (minute resolution): alarm on day + hour + minute.
static void rtcArmAlarm(time_t wakeUtc) {
  AlarmFields a = alarmFieldsFor(wakeUtc);
  rtcClearAndDisable();
  uint8_t r[4] = {toBcd(a.minute), toBcd(a.hour), toBcd(a.day), 0x80 /* weekday ignored */};
  rtcWrite(0x09, r, 4);
  rtcWrite1(0x01, 0x02);  // AIE on, flags cleared
}

// Wake after a number of seconds (up to 255 minutes) with the countdown timer.
static void rtcArmCountdown(int seconds) {
  rtcClearAndDisable();
  if (seconds < 1) seconds = 1;
  if (seconds <= 255) {
    rtcWrite1(0x0F, (uint8_t)seconds);
    rtcWrite1(0x0E, 0x82);  // TE=1, source 1 Hz
  } else {
    int minutes = (seconds + 59) / 60;
    if (minutes > 255) minutes = 255;
    rtcWrite1(0x0F, (uint8_t)minutes);
    rtcWrite1(0x0E, 0x83);  // TE=1, source 1/60 Hz
  }
  rtcWrite1(0x01, 0x01);  // TIE on, flags cleared
}

// ---- settings --------------------------------------------------------------
static Settings settings() {
  Settings s;
  s.photoHour = PHOTO_HOUR;
  s.photoMinute = PHOTO_MINUTE;
  s.aimIntervalSeconds = 60;
  s.retryAfterMinutes = RETRY_AFTER_MINUTES;
  s.maxRetriesPerDay = MAX_RETRIES_PER_DAY;
  s.unknownClockRetrySeconds = 60 * 60;
  return s;
}

// ---- power -----------------------------------------------------------------
// Seconds until the planned wake; used only when on USB power (see below).
static volatile int64_t gFallbackSleepSeconds = 3600;

static void armPlan(const Plan& p, time_t now) {
  if (p.wakeAt != 0) {
    rtcArmAlarm(p.wakeAt);
    gFallbackSleepSeconds = (int64_t)(p.wakeAt - now);
  } else {
    rtcArmCountdown(p.countdownSeconds);
    gFallbackSleepSeconds = p.countdownSeconds;
  }
  if (gFallbackSleepSeconds < 1) gFallbackSleepSeconds = 1;
}

// Cut power. On battery the board goes dark here and the RTC switches it back
// on at the alarm. On USB the board cannot switch itself off, so we fall back
// to ESP32 deep sleep for the same length of time.
static void powerOff() {
  digitalWrite(PIN_LED, LOW);
  digitalWrite(PIN_POWER_HOLD, LOW);
  delay(300);
  // Still running, so USB is plugged in.
  esp_sleep_enable_timer_wakeup((uint64_t)gFallbackSleepSeconds * 1000000ULL);
  esp_deep_sleep_start();
}

static void hardLimitHit(void*) {
  // Called from the esp_timer task if this wake runs too long (wifi hang,
  // slow PC...). The fallback alarm is already armed.
  Serial.println("Hard time limit reached - powering off.");
  powerOff();
}

// ---- camera ----------------------------------------------------------------
static bool cameraStart() {
  camera_config_t c = {};
  c.pin_pwdn = -1;
  c.pin_reset = 15;
  c.pin_xclk = 27;
  c.pin_sccb_sda = 25;
  c.pin_sccb_scl = 23;
  c.pin_d7 = 19;
  c.pin_d6 = 36;
  c.pin_d5 = 18;
  c.pin_d4 = 39;
  c.pin_d3 = 5;
  c.pin_d2 = 34;
  c.pin_d1 = 35;
  c.pin_d0 = 32;
  c.pin_vsync = 22;
  c.pin_href = 26;
  c.pin_pclk = 21;
  c.xclk_freq_hz = 20000000;
  c.ledc_timer = LEDC_TIMER_0;
  c.ledc_channel = LEDC_CHANNEL_0;
  c.pixel_format = PIXFORMAT_JPEG;
  c.frame_size = FRAMESIZE_QXGA;  // 2048x1536, the OV3660's full resolution
  c.jpeg_quality = JPEG_QUALITY;
  c.fb_count = 1;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.grab_mode = CAMERA_GRAB_LATEST;
  esp_err_t err = esp_camera_init(&c);
  if (err != ESP_OK) {
    logf("camera init failed: 0x%x", err);
    return false;
  }
  sensor_t* s = esp_camera_sensor_get();
  if (s) {
    s->set_vflip(s, FLIP_VERTICAL);
    s->set_hmirror(s, MIRROR_HORIZONTAL);
  }
  return true;
}

// Takes a picture and writes it straight to `path` on flash.
// The first frames after power-up are dark/green while auto-exposure and
// white balance settle, so we throw a few away.
static bool capturePhotoTo(const char* path, std::vector<uint8_t>* keepInRam) {
  if (!cameraStart()) return false;
  for (int i = 0; i < 4; i++) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (fb) esp_camera_fb_return(fb);
    delay(150);
  }
  camera_fb_t* fb = esp_camera_fb_get();
  bool ok = false;
  if (fb && fb->len > 0) {
    logf("photo %ux%u, %u bytes", fb->width, fb->height, (unsigned)fb->len);
    if (keepInRam) {
      keepInRam->assign(fb->buf, fb->buf + fb->len);
      ok = true;
    } else {
      File f = LittleFS.open(path, FILE_WRITE, true);
      if (f) {
        ok = f.write(fb->buf, fb->len) == fb->len;
        f.close();
        if (!ok) LittleFS.remove(path);
      }
    }
  } else {
    logf("no frame from camera");
  }
  if (fb) esp_camera_fb_return(fb);
  esp_camera_deinit();  // camera stops; full power-off happens with the board
  return ok;
}

// ---- held photos -----------------------------------------------------------
static std::vector<String> heldPhotos() {
  std::vector<String> names;
  File dir = LittleFS.open("/held");
  if (!dir || !dir.isDirectory()) return names;
  for (File f = dir.openNextFile(); f; f = dir.openNextFile()) {
    if (!f.isDirectory()) names.push_back(String("/held/") + f.name());
  }
  std::sort(names.begin(), names.end());  // names start with the time: oldest first
  return names;
}

// Make room for `bytes` by dropping the oldest held photos if flash is full.
static void makeRoom(size_t bytes) {
  const size_t margin = 64 * 1024;
  while (LittleFS.totalBytes() - LittleFS.usedBytes() < bytes + margin) {
    std::vector<String> held = heldPhotos();
    if (held.empty()) return;
    logf("flash full, dropping oldest held photo %s", held.front().c_str());
    LittleFS.remove(held.front());
  }
}

// ---- wifi + upload --------------------------------------------------------
static bool wifiJoin() {
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  uint32_t deadline = millis() + WIFI_TIMEOUT_SECONDS * 1000UL;
  int attempt = 0;
  while ((int32_t)(deadline - millis()) > 0) {
    attempt++;
    logf("wifi attempt %d", attempt);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    uint32_t tryUntil = min(deadline, (uint32_t)(millis() + 8000));
    while (WiFi.status() != WL_CONNECTED && (int32_t)(tryUntil - millis()) > 0) delay(100);
    if (WiFi.status() == WL_CONNECTED) {
      logf("wifi up, ip %s, rssi %d", WiFi.localIP().toString().c_str(), WiFi.RSSI());
      return true;
    }
    WiFi.disconnect(true);
    delay(200);
  }
  logf("wifi failed");
  return false;
}

static void wifiOff() {
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}

// Ask the internet for the time; up to 5 s. Returns true if synced.
static bool syncClock() {
  configTzTime(TIMEZONE, "pool.ntp.org", "time.google.com");
  uint32_t until = millis() + 5000;
  while (sntp_get_sync_status() != SNTP_SYNC_STATUS_COMPLETED && (int32_t)(until - millis()) > 0) delay(100);
  bool ok = sntp_get_sync_status() == SNTP_SYNC_STATUS_COMPLETED && clockIsSane(time(nullptr));
  if (ok) {
    rtcSetUtc(time(nullptr));
    logf("clock set from internet: %s", isoLocal(time(nullptr)).c_str());
  } else {
    logf("internet time not available");
  }
  return ok;
}

static int postBody(const std::string& path, Stream* stream, const uint8_t* buf, size_t size) {
  HTTPClient http;
  http.setConnectTimeout(5000);
  http.setTimeout(15000);
  if (!http.begin(RECEIVER_HOST, RECEIVER_PORT, path.c_str())) return -1;
  http.addHeader("Content-Type", "image/jpeg");
  int code = stream ? http.sendRequest("POST", stream, size)
                    : http.sendRequest("POST", (uint8_t*)buf, size);
  http.end();
  return code;
}

// ---- state file -----------------------------------------------------------
static State loadState() {
  File f = LittleFS.open("/state.txt", FILE_READ);
  if (!f) return State();
  String text = f.readString();
  f.close();
  return parseState(std::string(text.c_str()));
}

static void saveState(const State& s) {
  File f = LittleFS.open("/state.txt", FILE_WRITE, true);
  if (!f) return;
  std::string text = serializeState(s);
  f.write((const uint8_t*)text.data(), text.size());
  f.close();
}

static float readBatteryVolts() {
  analogSetPinAttenuation(PIN_BATTERY, ADC_11db);
  uint32_t sum = 0;
  for (int i = 0; i < 16; i++) sum += analogReadMilliVolts(PIN_BATTERY);
  return batteryVoltsFromPinMillivolts((int)(sum / 16), BATTERY_CALIBRATION);
}

// ===========================================================================
void setup() {
  // 1. Hold the power on before anything else, LED off.
  pinMode(PIN_POWER_HOLD, OUTPUT);
  digitalWrite(PIN_POWER_HOLD, HIGH);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  Serial.begin(115200);
  logf("lemon-camera awake");

  esp_timer_handle_t limit;
  esp_timer_create_args_t args = {};
  args.callback = &hardLimitHit;
  args.name = "hard_limit";
  esp_timer_create(&args, &limit);
  esp_timer_start_once(limit, (uint64_t)MAX_AWAKE_SECONDS * 1000000ULL);

  // 2. Clock.
  Wire.begin(PIN_RTC_SDA, PIN_RTC_SCL);
  useTimezone(TIMEZONE);
  time_t rtcNow = rtcGetUtc();
  rtcClearAndDisable();  // releases the wake-up line
  if (rtcNow) {
    struct timeval tv = {rtcNow, 0};
    settimeofday(&tv, nullptr);
    logf("RTC time %s", isoLocal(rtcNow).c_str());
  } else {
    logf("RTC time unknown (first start or battery was flat)");
  }

  if (!LittleFS.begin(true)) logf("flash storage could not be mounted");
  LittleFS.mkdir("/held");

  const Settings cfg = settings();
  State state = loadState();
  const String fw = String(__DATE__ " " __TIME__);
  if (state.firmwareId != fw.c_str()) {
    logf("new firmware: aiming mode for %d shots", AIM_MODE_SHOTS);
    state.firmwareId = fw.c_str();
    state.aimShotsLeft = AIM_MODE_SHOTS;
    state.retriesUsedToday = 0;
  }
  state.boot++;

  // Arm a fallback wake right now, so a hang later still ends in a wake-up.
  {
    State scratch = state;
    if (scratch.aimShotsLeft > 0) scratch.aimShotsLeft--;  // as if this shot is done
    armPlan(planNextWake(time(nullptr), scratch, cfg, true), time(nullptr));
  }

  // 3. Picture.
  const bool aim = state.aimShotsLeft > 0;
  const bool daily = !aim && isDailyPhotoTime(time(nullptr), PHOTO_HOUR, PHOTO_MINUTE);
  const time_t taken = time(nullptr);
  const float battery = readBatteryVolts();  // before wifi loads the battery
  logf("battery %.2f V, %s wake", battery, aim ? "aiming" : daily ? "daily" : "retry");

  std::vector<uint8_t> aimPhoto;
  String todayFile;
  if (aim) {
    capturePhotoTo(nullptr, &aimPhoto);
    state.aimShotsLeft--;
  } else if (daily) {
    todayFile = heldName(taken, state.boot).c_str();
    makeRoom(600 * 1024);  // a QXGA JPEG at quality 10 is typically 300-600 KB
    if (!capturePhotoTo(todayFile.c_str(), nullptr)) todayFile = "";
  }
  saveState(state);  // the photo is safe on flash now; record that we took it

  // 4. Send.
  if (wifiJoin()) {
    syncClock();
    if (aim && !aimPhoto.empty()) {
      UploadInfo u = {"aim", clockIsSane(taken) ? taken : time(nullptr), battery, state.boot, 0, ""};
      int code = postBody(uploadPath(u), nullptr, aimPhoto.data(), aimPhoto.size());
      logf("aim photo upload -> %d", code);
    }
    std::vector<String> held = heldPhotos();
    for (size_t i = 0; i < held.size(); i++) {
      const String& name = held[i];
      File f = LittleFS.open(name, FILE_READ);
      if (!f) continue;
      time_t t = heldTaken(name.c_str());
      bool isToday = (name == todayFile);
      // A first-ever photo has no time in its name; it was taken seconds ago.
      if (isToday && !clockIsSane(t)) t = time(nullptr);
      UploadInfo u = {isToday ? "daily" : "held", t, battery, state.boot,
                      (int)(held.size() - i - 1), ""};
      int code = postBody(uploadPath(u), &f, nullptr, f.size());
      f.close();
      logf("upload %s -> %d", name.c_str(), code);
      if (code >= 200 && code < 300) {
        LittleFS.remove(name);
      } else {
        break;  // PC not answering: keep the rest for next time
      }
    }
  }
  wifiOff();

  // 5. Next wake.
  time_t now = time(nullptr);
  Plan plan = planNextWake(now, state, cfg, !heldPhotos().empty());
  saveState(state);
  armPlan(plan, now);
  if (plan.wakeAt) logf("next wake %s", isoLocal(plan.wakeAt).c_str());
  else logf("next wake in %d s", plan.countdownSeconds);
  LittleFS.end();
  Serial.flush();
  powerOff();
}

void loop() {
  // Never reached: setup() always ends in powerOff().
  powerOff();
}
