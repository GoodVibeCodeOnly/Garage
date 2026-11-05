// lemon_logic.h - the decisions the camera makes, with no hardware in them.
//
// Everything here is plain C++ so it can be tested on a PC
// (tests/firmware/test_logic.cpp). The .ino file does the hardware work and
// asks this file what to do.
#pragma once

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <string>

namespace lemon {

// Anything before this is "the clock was never set" (2024-01-01 UTC).
static const time_t kSaneEpoch = 1704067200;

inline bool clockIsSane(time_t t) { return t >= kSaneEpoch; }

inline uint8_t toBcd(int v) { return (uint8_t)(((v / 10) << 4) | (v % 10)); }
inline int fromBcd(uint8_t b) { return ((b >> 4) & 0x0F) * 10 + (b & 0x0F); }

// UTC epoch from calendar fields, without needing timegm() (not in every
// libc). Howard Hinnant's days-from-civil algorithm.
inline time_t utcFromFields(int y, int m, int d, int hh, int mm, int ss) {
  y -= m <= 2;
  const long era = (y >= 0 ? y : y - 399) / 400;
  const long yoe = y - era * 400;
  const long doy = (153L * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  const long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  const long days = era * 146097 + doe - 719468;
  return (time_t)days * 86400 + hh * 3600 + mm * 60 + ss;
}

// Sets the process time zone. Both the ESP32 (newlib) and Linux honour TZ.
inline void useTimezone(const char* posixTz) {
  setenv("TZ", posixTz, 1);
  tzset();
}

// Next moment, strictly more than minLeadSeconds after `now`, when the local
// wall clock reads hour:minute:00. Caller must have called useTimezone().
// On the spring-forward day a time that does not exist (02:30) is pushed
// forward by mktime(); on the fall-back day the first 01:30 is used.
inline time_t nextLocalTime(time_t now, int hour, int minute, int minLeadSeconds) {
  struct tm lt;
  localtime_r(&now, &lt);
  for (int addDays = 0; addDays < 3; ++addDays) {
    struct tm want = lt;
    want.tm_mday += addDays;
    want.tm_hour = hour;
    want.tm_min = minute;
    want.tm_sec = 0;
    want.tm_isdst = -1;
    time_t t = mktime(&want);
    if (t > now + minLeadSeconds) return t;
  }
  return now + 24 * 3600;  // unreachable in practice
}

// The BM8563 alarm compares day-of-month, hour and minute (seconds are not
// compared). We keep the RTC in UTC, so the alarm is in UTC too.
struct AlarmFields {
  int day;     // 1-31
  int hour;    // 0-23
  int minute;  // 0-59
};

inline AlarmFields alarmFieldsFor(time_t wakeUtc) {
  struct tm u;
  gmtime_r(&wakeUtc, &u);
  AlarmFields a = {u.tm_mday, u.tm_hour, u.tm_min};
  return a;
}

// Local calendar date ("2026-11-05") for a UTC instant, using the current TZ.
inline std::string localDate(time_t t) {
  struct tm lt;
  localtime_r(&t, &lt);
  char buf[16];
  strftime(buf, sizeof buf, "%Y-%m-%d", &lt);
  return std::string(buf);
}

// ISO 8601 local time with UTC offset: 2026-11-05T12:00:03-05:00
inline std::string isoLocal(time_t t) {
  struct tm lt;
  localtime_r(&t, &lt);
  char buf[40];
  strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%S%z", &lt);
  // strftime gives -0500; insert the colon for strict ISO 8601.
  std::string s(buf);
  if (s.size() >= 5) s.insert(s.size() - 2, ":");
  return s;
}

// ---------------------------------------------------------------------------
// What the upload says about itself.
//
// The photo goes as the raw request body; everything else rides in the query
// string as key=value pairs. The receiver logs every key it gets, so a future
// sensor only has to add a field here (e.g. temp_c) - nothing else breaks.
struct UploadInfo {
  std::string kind;      // "daily", "aim" or "held"
  time_t taken;          // UTC; 0 if the clock was unknown
  float batteryVolts;    // < 0 if unknown
  long boot;             // wake counter
  int held;              // photos still waiting on the board after this one
  std::string extra;     // already-encoded "&key=value" pairs for the future
};

inline std::string urlEncode(const std::string& s) {
  static const char* hex = "0123456789ABCDEF";
  std::string out;
  for (unsigned char c : s) {
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
      out += (char)c;
    } else {
      out += '%';
      out += hex[c >> 4];
      out += hex[c & 15];
    }
  }
  return out;
}

inline std::string uploadPath(const UploadInfo& u) {
  std::string p = "/upload?v=1&kind=" + urlEncode(u.kind);
  if (clockIsSane(u.taken)) {
    p += "&taken=" + urlEncode(isoLocal(u.taken));
    p += "&date=" + localDate(u.taken);
  }
  if (u.batteryVolts >= 0) {
    char b[16];
    snprintf(b, sizeof b, "%.3f", u.batteryVolts);
    p += "&battery_v=";
    p += b;
  }
  p += "&boot=" + std::to_string(u.boot);
  p += "&held=" + std::to_string(u.held);
  p += u.extra;
  return p;
}

// ---------------------------------------------------------------------------
// Held photos: when the PC can't be reached the picture is written to the
// board's flash as /held/<unix-time>.jpg and sent on a later wake, oldest
// first. Unknown time is stored as 0 plus a counter to keep names unique.
inline std::string heldName(time_t taken, long boot) {
  char buf[48];
  snprintf(buf, sizeof buf, "/held/%010lld-%06ld.jpg", (long long)(clockIsSane(taken) ? taken : 0), boot % 1000000);
  return std::string(buf);
}

// Returns the taken time encoded in a held file name (0 if unknown/garbled).
inline time_t heldTaken(const char* name) {
  const char* base = strrchr(name, '/');
  base = base ? base + 1 : name;
  char* end = nullptr;
  long long v = strtoll(base, &end, 10);
  if (end == base || *end != '-') return 0;
  return (time_t)v;
}

// Battery: the ADC pin sees the battery through a resistor divider. M5Stack's
// TimerCam code divides the pin millivolts by 0.661. UNVERIFIED against a meter;
// see POWER.md. Returns volts.
inline float batteryVoltsFromPinMillivolts(int pinMv, float calibration) {
  if (pinMv <= 0) return -1.0f;
  return (pinMv / 0.661f) / 1000.0f * calibration;
}

// ---------------------------------------------------------------------------
// The plan for the next wake.
enum class WakeKind { Daily, Aim, Retry };

struct State {
  long boot = 0;
  int aimShotsLeft = 0;
  int retriesUsedToday = 0;
  std::string retryDate;   // local date retries were counted for
  std::string firmwareId;  // build stamp; a new one restarts aiming
};

struct Plan {
  WakeKind kind;
  time_t wakeAt;          // UTC; 0 = unknown clock, use the countdown timer
  int countdownSeconds;   // used when wakeAt == 0, or for aim mode
};

struct Settings {
  int photoHour, photoMinute;
  int aimIntervalSeconds;   // 60
  int retryAfterMinutes;
  int maxRetriesPerDay;
  int unknownClockRetrySeconds;  // how long to sleep if time is unknown
};

// Decide when to wake next.
//   now           - current UTC (may be insane if never synced)
//   s             - persistent state (aim counter / retry counter are updated)
//   somethingHeld - photos are still waiting on the board
inline Plan planNextWake(time_t now, State& s, const Settings& cfg, bool somethingHeld) {
  if (s.aimShotsLeft > 0) {
    Plan p = {WakeKind::Aim, 0, cfg.aimIntervalSeconds};
    return p;
  }
  if (!clockIsSane(now)) {
    // Never got the time from the internet: try again after a while.
    Plan p = {WakeKind::Retry, 0, cfg.unknownClockRetrySeconds};
    return p;
  }
  time_t daily = nextLocalTime(now, cfg.photoHour, cfg.photoMinute, 90);
  std::string today = localDate(now);
  if (s.retryDate != today) {
    s.retryDate = today;
    s.retriesUsedToday = 0;
  }
  if (somethingHeld && s.retriesUsedToday < cfg.maxRetriesPerDay) {
    time_t retry = now + (time_t)cfg.retryAfterMinutes * 60;
    // Round up to the next whole minute: the RTC alarm has minute resolution.
    retry = ((retry + 59) / 60) * 60;
    if (retry + 300 < daily) {  // don't bother if the daily wake is near
      s.retriesUsedToday++;
      Plan p = {WakeKind::Retry, retry, 0};
      return p;
    }
  }
  Plan p = {WakeKind::Daily, daily, 0};
  return p;
}

// Was this wake the daily photo, or only a retry? We decide by how close we
// are to the scheduled photo time (the alarm has minute resolution and boot
// takes a second or two, so "within 10 minutes after" is generous).
inline bool isDailyPhotoTime(time_t now, int hour, int minute) {
  if (!clockIsSane(now)) return true;  // unknown time: take a photo to be safe
  // First scheduled time after (now - 10 min). If it is no later than
  // now + 2 min, we are in the photo window.
  time_t scheduled = nextLocalTime(now - 600, hour, minute, 0);
  return scheduled <= now + 120;
}

// ---- tiny key=value state file -------------------------------------------
inline std::string serializeState(const State& s) {
  std::string o;
  o += "boot=" + std::to_string(s.boot) + "\n";
  o += "aim=" + std::to_string(s.aimShotsLeft) + "\n";
  o += "retries=" + std::to_string(s.retriesUsedToday) + "\n";
  o += "retry_date=" + s.retryDate + "\n";
  o += "firmware=" + s.firmwareId + "\n";
  return o;
}

inline State parseState(const std::string& text) {
  State s;
  size_t pos = 0;
  while (pos < text.size()) {
    size_t nl = text.find('\n', pos);
    if (nl == std::string::npos) nl = text.size();
    std::string line = text.substr(pos, nl - pos);
    pos = nl + 1;
    size_t eq = line.find('=');
    if (eq == std::string::npos) continue;
    std::string k = line.substr(0, eq), v = line.substr(eq + 1);
    if (k == "boot") s.boot = atol(v.c_str());
    else if (k == "aim") s.aimShotsLeft = atoi(v.c_str());
    else if (k == "retries") s.retriesUsedToday = atoi(v.c_str());
    else if (k == "retry_date") s.retryDate = v;
    else if (k == "firmware") s.firmwareId = v;
  }
  return s;
}

}  // namespace lemon
