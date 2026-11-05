# Setting up the lemon camera

This takes about an hour the first time. You only do it once. Nothing here
needs a command window: it's all downloads, double-clicks, and menus.

You need: the Timer Camera X, its USB-C cable, the Windows PC, and your
wifi name and password. The wifi must be **2.4 GHz** (most home routers have
both; if yours lists two names, use the one *without* "5G").

---

## Part A — the PC side

### 1. Install Python (free)

1. Go to **python.org**, click **Downloads**, then the yellow
   **Download Python 3.x** button.
2. Run the downloaded file. **On the first screen, tick "Add python.exe to
   PATH"**, then click **Install Now**.

### 2. Get this project onto the PC

1. On the GitHub page for this project, click the green **Code** button, then
   **Download ZIP**.
2. In your Downloads folder, right-click the ZIP → **Extract All…** → choose
   your **Documents** folder.
3. You now have `Documents\Garage-…\lemon-camera\`. Everything below is in
   there.

### 3. Start the receiver

1. Open `lemon-camera\receiver\` and double-click **Start Lemon Receiver.bat**.
2. A black window opens and says *"Lemon camera receiver is running"*, with
   **This PC's address** — something like `192.168.1.50`. **Write that
   address down.**
3. Windows may ask whether to allow Python through the firewall. Tick
   **Private networks**, click **Allow**. (If you said no by mistake: Start →
   "Allow an app through Windows Firewall" → find Python → tick Private.)
4. Check it: on the same PC, open a web browser and go to
   `http://localhost:8080/`. You should see `{"ok": true, ...}`.

Leave this window open whenever you want photos to arrive. To start it
automatically: press Win+R, type `shell:startup`, Enter, and drag a
**shortcut** of the .bat into that folder (right-drag → Create shortcut here).

**Keep the PC's address from changing:** the camera remembers the address
from step 3. Routers usually hand out the same address, but not always. In
your router's settings page, look for "DHCP reservation" or "reserved IP" and
reserve that address for this PC. If you can't, and photos stop arriving one
day, check whether the address in the black window has changed.

**The PC must be awake at the photo time** (noon by default). If it sleeps,
the camera holds the photo and tries again an hour later, twice, then
tomorrow. To stop the PC sleeping: Settings → System → Power → Screen and
sleep → "When plugged in, put my device to sleep after" → **Never**.

---

## Part B — the camera

### 4. Put your settings in

1. Open `lemon-camera\firmware\lemon_camera\`.
2. Windows hides file endings, which causes trouble here. In File Explorer,
   click **View** → **Show** → tick **File name extensions**.
3. Copy `config.example.h` and paste it in the same folder. Rename the copy to
   exactly **`config.h`** (not `config.h.txt`, not `config.example - Copy.h`).
4. Right-click `config.h` → **Open with** → **Notepad**. Change:
   - `your-wifi-name` → your wifi name (keep the quote marks)
   - `your-wifi-password` → your wifi password (keep the quote marks)
   - `192.168.1.50` → the address from step 3
   - `PHOTO_HOUR` / `PHOTO_MINUTE` if you want a time other than noon
5. Save and close.

`config.h` stays on your PC only; it is never uploaded to GitHub.

### 5. Install the Arduino program (free)

1. Go to **arduino.cc** → **Software** → download **Arduino IDE 2** for
   Windows and install it with the default answers. Allow it to install the
   USB drivers it offers.
2. Open Arduino IDE. **File → Preferences**. In
   **Additional boards manager URLs** paste:
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   and click OK.
3. Click the second icon down the left edge (**Boards Manager**). Search
   **esp32**. Find **"esp32 by Espressif Systems"** and click **Install**.
   This is a large download; wait for it to finish.

No other libraries are needed: the camera, wifi, and storage code all come
with that install.

### 6. Plug in the camera

1. Connect the camera to the PC with the USB-C cable.
2. In Arduino IDE: **Tools → Port** — pick the **COM** port that appeared
   when you plugged it in (unplug and replug to see which one appears).
   **If no COM port appears:** the board's USB chip needs a driver. M5Stack
   provides it on the Timer Camera X documentation page
   (docs.m5stack.com → Timer Camera X → "Driver"; it's the CH9102 driver).
   Install it, unplug, replug.

### 7. Load the program onto the camera

1. **File → Open…** → `lemon-camera\firmware\lemon_camera\lemon_camera.ino`.
2. **Tools → Board → esp32 → M5Stack-Timer-CAM** (type "timer" in the board
   search box to find it).
3. **Tools → PSRAM → Enabled** (if that menu is there).
4. Ignore **Tools → Partition Scheme**: the project brings its own
   (`partitions.csv`) and Arduino uses it automatically.
5. Click the **→ arrow** (Upload) at the top left. It compiles for a minute or
   two, then says *"Writing at …"* and finally *"Hard resetting via RTS pin…"*.
   That means it worked.

If it says **"Missing config.h"**, go back to step 4 — the file is missing
or misnamed. If it fails to connect, unplug, replug, check the Port menu, and
try again.

### 8. Aim it

After every upload, the camera spends its first 30 pictures (about one a
minute, half an hour) in **aiming mode**.

- Watch `Pictures\LemonTree\aim\` on the PC. A new picture should arrive
  every minute or so.
- Move the camera until the tree is framed how you like it.
- If the picture is upside down, change `FLIP_VERTICAL` in `config.h` from 1
  to 0 and upload again (step 7). That restarts aiming.
- Optional: **Tools → Serial Monitor**, set to **115200 baud**, to watch what
  the camera is doing. Every line has a millisecond count.

Aiming pictures never take the day's slot.

After aiming, the camera takes **one picture a day** at the time you set. It
lands in `Pictures\LemonTree\2026-11\2026-11-05.jpg` (year-month folder, then
the date).

### 9. Go cordless

Let it charge on USB for an hour or so first (the battery is small). Then
unplug it. It stays off until the next scheduled picture, then switches
itself on, takes it, sends it, and switches itself off again. **The LED stays
off on purpose.**

The board's side button: hold it ~2 seconds to switch the board on by hand.
You shouldn't need it.

---

## Every day after

- **Photos:** `Pictures\LemonTree\` (by month).
- **Battery:** open `Pictures\LemonTree\battery-log.csv` in Excel. The
  `battery_v` column is the battery voltage at each picture. Around 4.1 V is
  full. **Bring it in to charge when it gets to about 3.5 V.** (Charging over
  USB takes about an hour. After charging and unplugging it carries on by
  itself.)
- **Time-lapse:** double-click **Make Time-lapse.bat** in the `receiver`
  folder. It makes `Pictures\LemonTree\lemon-timelapse.avi`. It plays in VLC
  (free, videolan.org); the Windows player probably plays it too, but that
  isn't checked yet.
- **A second picture on the same day** (for example after re-aiming) goes into
  the month's `extras` folder. The first one of the day is never replaced.

## If photos stop arriving

1. Is the black receiver window open? Is the PC awake at the photo time?
2. Has the PC's address changed? Compare the window's address with `config.h`.
3. Is the battery flat? Look at the last `battery_v` in the log; charge it.
4. Missed photos are not lost straight away: the camera keeps several days of
   photos in its own memory (about 3–5, see README) and sends them, oldest
   first, the next time it reaches the PC. When its memory is full it drops
   the oldest.
