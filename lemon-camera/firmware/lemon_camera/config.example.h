// lemon-camera settings.
//
// HOW TO USE: make a copy of this file in the same folder, name the copy
// exactly  config.h  , and change the values in the copy. config.h is
// ignored by git, so your wifi password never ends up on GitHub.
#pragma once

// ---- Your wifi (2.4 GHz only: the ESP32 cannot see 5 GHz networks) ----
#define WIFI_SSID      "your-wifi-name"
#define WIFI_PASSWORD  "your-wifi-password"

// ---- The Windows PC running the receiver ----
// The PC's local address. The receiver window shows it when it starts.
// Ask your router to always give the PC this same address
// ("DHCP reservation"), or the camera will lose it.
#define RECEIVER_HOST  "192.168.1.50"
#define RECEIVER_PORT  8080

// ---- When to take the daily picture (local time on the deck) ----
#define PHOTO_HOUR     12   // 0-23. Noon gives the most even light.
#define PHOTO_MINUTE   0    // 0-59

// Time zone rule. This one is US Eastern with daylight saving (Durham, NC).
// Format is POSIX TZ; leave it alone unless the camera moves time zones.
#define TIMEZONE       "EST5EDT,M3.2.0,M11.1.0"

// ---- Aiming mode ----
// After every new upload of this firmware, the camera takes one picture a
// minute for this many minutes so you can aim it, then switches to once a day.
// Set to 0 to skip aiming.
#define AIM_MODE_SHOTS 30

// ---- Bad-night limits (protect the battery) ----
// Longest the board may stay awake on one wake, wifi included. After this the
// power is cut no matter what.
#define MAX_AWAKE_SECONDS      45
// Time allowed for joining wifi on one wake.
#define WIFI_TIMEOUT_SECONDS   20
// If wifi or the PC fails, wake again this many minutes later just to resend...
#define RETRY_AFTER_MINUTES    60
// ...but at most this many extra wakes per day. 0 = just wait for tomorrow.
#define MAX_RETRIES_PER_DAY    2

// ---- Picture ----
// JPEG quality, 4 (best, biggest) to 63 (worst). 10 is a good balance.
#define JPEG_QUALITY   10

// ---- Battery reading calibration ----
// Multiply the raw battery reading by this. If the PC log disagrees with a
// multimeter on the battery, adjust: new = old * (meter volts / logged volts).
#define BATTERY_CALIBRATION    1.0f

// ---- Picture orientation ----
// Check the aiming pictures. If they are upside down, change 1 to 0 (or 0 to 1).
#define FLIP_VERTICAL     1
#define MIRROR_HORIZONTAL 0
