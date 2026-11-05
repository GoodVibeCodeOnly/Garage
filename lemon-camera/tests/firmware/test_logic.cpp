// Host tests for firmware/lemon_camera/lemon_logic.h (no hardware needed).
// Build and run:  sh tests/firmware/run.sh
#include "../../firmware/lemon_camera/lemon_logic.h"

#include <cstdio>
#include <string>

using namespace lemon;

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { \
  std::printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)
#define CHECK_EQ(a, b) do { auto _a = (a); auto _b = (b); if (!(_a == _b)) { \
  std::printf("FAIL %s:%d  %s == %s\n", __FILE__, __LINE__, #a, #b); failures++; } } while (0)

static const char* ET = "EST5EDT,M3.2.0,M11.1.0";

// UTC epoch from Y-M-D h:m:s (UTC).
static time_t utc(int y, int mo, int d, int h, int mi, int s = 0) {
  struct tm t = {};
  t.tm_year = y - 1900; t.tm_mon = mo - 1; t.tm_mday = d;
  t.tm_hour = h; t.tm_min = mi; t.tm_sec = s;
  return timegm(&t);
}

static Settings cfg() {
  Settings s;
  s.photoHour = 12; s.photoMinute = 0;
  s.aimIntervalSeconds = 60;
  s.retryAfterMinutes = 60;
  s.maxRetriesPerDay = 2;
  s.unknownClockRetrySeconds = 3600;
  return s;
}

static void test_bcd() {
  for (int v = 0; v < 100; v++) CHECK_EQ(fromBcd(toBcd(v)), v);
  CHECK_EQ(toBcd(59), 0x59);
}

static void test_next_local_time() {
  useTimezone(ET);
  // 5 Nov 2026 is EST (UTC-5). 09:00 local -> noon local is 17:00 UTC same day.
  CHECK_EQ(nextLocalTime(utc(2026, 11, 5, 14, 0), 12, 0, 90), utc(2026, 11, 5, 17, 0));
  // Just after noon local -> tomorrow.
  CHECK_EQ(nextLocalTime(utc(2026, 11, 5, 17, 0, 30), 12, 0, 90), utc(2026, 11, 6, 17, 0));
  // In summer (EDT, UTC-4) noon is 16:00 UTC.
  CHECK_EQ(nextLocalTime(utc(2026, 7, 1, 10, 0), 12, 0, 90), utc(2026, 7, 1, 16, 0));
  // Across fall-back: Sat 31 Oct 2026 noon EDT -> Sun 1 Nov noon EST (25 h later).
  CHECK_EQ(nextLocalTime(utc(2026, 10, 31, 16, 1), 12, 0, 90), utc(2026, 11, 1, 17, 0));
  // Across spring-forward (Sun 14 Mar 2027): Sat noon EST -> Sun noon EDT (23 h).
  CHECK_EQ(nextLocalTime(utc(2027, 3, 13, 17, 1), 12, 0, 90), utc(2027, 3, 14, 16, 0));
  CHECK_EQ(nextLocalTime(utc(2027, 3, 14, 16, 1), 12, 0, 90), utc(2027, 3, 15, 16, 0));
  // A photo time that does not exist that night (02:30 on 14 Mar) still wakes.
  time_t odd = nextLocalTime(utc(2027, 3, 14, 5, 0), 2, 30, 90);
  CHECK(odd > utc(2027, 3, 14, 5, 0) && odd <= utc(2027, 3, 14, 8, 0));
  // Late-evening local time whose UTC is the next calendar day.
  CHECK_EQ(nextLocalTime(utc(2026, 11, 5, 14, 0), 22, 30, 90), utc(2026, 11, 6, 3, 30));
}

static void test_utc_from_fields() {
  CHECK_EQ(utcFromFields(2026, 11, 5, 17, 0, 3), utc(2026, 11, 5, 17, 0, 3));
  CHECK_EQ(utcFromFields(2028, 2, 29, 23, 59, 59), utc(2028, 2, 29, 23, 59, 59));
  CHECK_EQ(utcFromFields(2000, 1, 1, 0, 0, 0), (time_t)946684800);
  for (time_t t = utc(2025, 1, 1, 0, 0); t < utc(2031, 1, 1, 0, 0); t += 86400 * 7 + 3671) {
    struct tm g; gmtime_r(&t, &g);
    CHECK_EQ(utcFromFields(g.tm_year + 1900, g.tm_mon + 1, g.tm_mday, g.tm_hour, g.tm_min, g.tm_sec), t);
  }
}

static void test_alarm_fields() {
  AlarmFields a = alarmFieldsFor(utc(2026, 11, 6, 3, 30));
  CHECK_EQ(a.day, 6); CHECK_EQ(a.hour, 3); CHECK_EQ(a.minute, 30);
}

static void test_dates_and_iso() {
  useTimezone(ET);
  CHECK_EQ(localDate(utc(2026, 11, 6, 3, 0)), std::string("2026-11-05"));  // 22:00 EST
  CHECK_EQ(isoLocal(utc(2026, 11, 5, 17, 0, 3)), std::string("2026-11-05T12:00:03-05:00"));
  CHECK_EQ(isoLocal(utc(2026, 7, 1, 16, 0)), std::string("2026-07-01T12:00:00-04:00"));
}

static void test_upload_path() {
  useTimezone(ET);
  UploadInfo u = {"daily", utc(2026, 11, 5, 17, 0, 3), 3.95f, 12, 0, ""};
  // Must match the path the receiver test posts (tests/test_receiver.py).
  CHECK_EQ(uploadPath(u), std::string("/upload?v=1&kind=daily&taken=2026-11-05T12%3A00%3A03-05%3A00"
                                      "&date=2026-11-05&battery_v=3.950&boot=12&held=0"));
  UploadInfo unknown = {"held", 0, -1.0f, 3, 2, "&temp_c=4.5"};
  CHECK_EQ(uploadPath(unknown), std::string("/upload?v=1&kind=held&boot=3&held=2&temp_c=4.5"));
}

static void test_held_names() {
  std::string n = heldName(1793984403, 42);
  CHECK_EQ(n, std::string("/held/1793984403-000042.jpg"));
  CHECK_EQ(heldTaken(n.c_str()), (time_t)1793984403);
  CHECK_EQ(heldTaken("1793984403-000042.jpg"), (time_t)1793984403);
  CHECK_EQ(heldTaken("/held/0000000000-000007.jpg"), (time_t)0);
  CHECK_EQ(heldTaken("/held/garbage.jpg"), (time_t)0);
  // Name order is time order (zero padded), which is how the oldest goes first.
  CHECK(heldName(1793984403, 99) < heldName(1793984404, 1));
  // Unknown time sorts first.
  CHECK(heldName(0, 5) < heldName(1793984403, 1));
}

static void test_battery() {
  float v = batteryVoltsFromPinMillivolts(2644, 1.0f);  // ~4.0 V battery
  CHECK(v > 3.99f && v < 4.01f);
  CHECK(batteryVoltsFromPinMillivolts(0, 1.0f) < 0);
  CHECK(batteryVoltsFromPinMillivolts(2644, 1.05f) > 4.19f);
}

static void test_plan() {
  useTimezone(ET);
  Settings c = cfg();
  time_t noonish = utc(2026, 11, 5, 17, 0, 20);

  State s;
  s.aimShotsLeft = 3;
  Plan p = planNextWake(noonish, s, c, false);
  CHECK(p.kind == WakeKind::Aim); CHECK_EQ(p.wakeAt, (time_t)0); CHECK_EQ(p.countdownSeconds, 60);

  State u;
  p = planNextWake(1000, u, c, true);  // clock never set
  CHECK(p.kind == WakeKind::Retry); CHECK_EQ(p.wakeAt, (time_t)0); CHECK_EQ(p.countdownSeconds, 3600);

  State d;
  p = planNextWake(noonish, d, c, false);  // all sent -> tomorrow noon
  CHECK(p.kind == WakeKind::Daily); CHECK_EQ(p.wakeAt, utc(2026, 11, 6, 17, 0));

  // Nothing got through: two retries an hour apart, then wait for tomorrow.
  State r;
  p = planNextWake(noonish, r, c, true);
  CHECK(p.kind == WakeKind::Retry); CHECK_EQ(p.wakeAt, utc(2026, 11, 5, 18, 1));
  p = planNextWake(utc(2026, 11, 5, 18, 1, 15), r, c, true);
  CHECK(p.kind == WakeKind::Retry); CHECK_EQ(r.retriesUsedToday, 2);
  p = planNextWake(utc(2026, 11, 5, 19, 2, 15), r, c, true);
  CHECK(p.kind == WakeKind::Daily); CHECK_EQ(p.wakeAt, utc(2026, 11, 6, 17, 0));
  // Next day the retry budget is fresh again.
  p = planNextWake(utc(2026, 11, 6, 17, 0, 20), r, c, true);
  CHECK(p.kind == WakeKind::Retry); CHECK_EQ(r.retriesUsedToday, 1);

  // No retry if it would land within 5 minutes of the daily photo.
  State late;
  p = planNextWake(utc(2026, 11, 6, 16, 2), late, c, true);  // 11:02 local, retry 12:02
  CHECK(p.kind == WakeKind::Daily);
}

static void test_is_daily_photo_time() {
  useTimezone(ET);
  CHECK(isDailyPhotoTime(utc(2026, 11, 5, 17, 0, 2), 12, 0));
  CHECK(isDailyPhotoTime(utc(2026, 11, 5, 16, 59, 30), 12, 0));   // RTC a bit fast
  CHECK(isDailyPhotoTime(utc(2026, 11, 5, 17, 9, 0), 12, 0));
  CHECK(!isDailyPhotoTime(utc(2026, 11, 5, 18, 1, 0), 12, 0));    // a retry wake
  CHECK(!isDailyPhotoTime(utc(2026, 11, 5, 16, 50, 0), 12, 0));
  CHECK(isDailyPhotoTime(100, 12, 0));                             // unknown clock
}

static void test_state_roundtrip() {
  State s;
  s.boot = 123; s.aimShotsLeft = 4; s.retriesUsedToday = 1;
  s.retryDate = "2026-11-05"; s.firmwareId = "Nov  5 2026 02:00:00";
  State t = parseState(serializeState(s));
  CHECK_EQ(t.boot, 123L); CHECK_EQ(t.aimShotsLeft, 4); CHECK_EQ(t.retriesUsedToday, 1);
  CHECK_EQ(t.retryDate, s.retryDate); CHECK_EQ(t.firmwareId, s.firmwareId);
  State e = parseState("");
  CHECK_EQ(e.boot, 0L); CHECK_EQ(e.firmwareId, std::string(""));
  State g = parseState("junk\nboot=5\n=x\nunknown=1");
  CHECK_EQ(g.boot, 5L);
}

int main() {
  test_bcd();
  test_next_local_time();
  test_utc_from_fields();
  test_alarm_fields();
  test_dates_and_iso();
  test_upload_path();
  test_held_names();
  test_battery();
  test_plan();
  test_is_daily_photo_time();
  test_state_roundtrip();
  if (failures) { std::printf("%d failure(s)\n", failures); return 1; }
  std::printf("all firmware logic tests passed\n");
  return 0;
}
