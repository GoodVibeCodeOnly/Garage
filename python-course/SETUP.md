# Setup — assuming nothing

This gets you from "fresh Windows PC" to "running the course" with no terminal.
Roughly ten minutes, once.

## 1. Get the course folder onto your PC

If you already have this repository on your machine (GitHub Desktop, or a zip),
skip to step 2.

Otherwise: on the GitHub page for this repository, click the green **Code**
button → **Download ZIP**. Open your Downloads folder, right-click the zip →
**Extract All…** → **Extract**. Inside, find the `python-course` folder. Move it
somewhere permanent, e.g. `Documents\python-course`.

> Don't run things from inside the zip without extracting — Windows lets you
> look inside, but the scripts can't write files there.

## 2. Install Python (skip if you already have it)

1. Go to <https://www.python.org/downloads/>.
2. Click the big yellow **Download Python 3.x.x** button.
3. Run the downloaded installer.
4. **On the very first screen, tick "Add python.exe to PATH"** (bottom of the
   window). This is the one step people miss.
5. Click **Install Now**. Accept the Windows permission prompt. Wait. Close.

Don't know if you have it? Skip this step; step 3 will tell you.

## 3. Run setup

Open the `python-course` folder and **double-click `setup.bat`**.

A black window appears, finds Python, creates a private environment in a
folder called `.venv` and installs the libraries the course uses (pandas,
numpy, matplotlib, scipy, pytest, requests). When it says **Setup complete**,
press a key to close it.

If Windows shows a blue "Windows protected your PC" box: click **More info**
→ **Run anyway**. The `.bat` files are plain text — right-click → **Edit** to
read exactly what they do.

## 4. Use the course

**Double-click `course.bat`.** You get a menu:

```
  1  Check my exercises for a lesson
  2  Open a lesson (README, example, exercises) in the editor
  3  Run a lesson's worked example
  4  Show my progress across all lessons
  5  Verify the model solutions (sanity check)
```

Option **2** opens the lesson in **IDLE**, the editor that ships with Python.
In IDLE: edit, `Ctrl+S` to save, `F5` to run the file you're looking at.

Shortcuts if you don't want the menu: `check.bat` (asks for a lesson number,
tests it) and `progress.bat` (one line per lesson).

### A better editor, when you want one (optional)

IDLE is fine for the whole course. When you want more — tabs, autocomplete,
inline errors — install **VS Code** (<https://code.visualstudio.com/>), add the
**Python** extension (Microsoft), then *File → Open Folder* → `python-course`.
Bottom-right, choose the interpreter that mentions `.venv`. The `.bat` files
keep working either way.

## If setup fails

| Symptom | Fix |
|---|---|
| "Python was not found" | Do step 2. If you did, you probably missed the PATH tickbox: re-run the installer, choose **Modify** → **Next** → tick **Add Python to environment variables** → **Install**. |
| The Microsoft Store opens | Windows has a fake `python` shortcut. Install from python.org as in step 2; the real one wins. |
| Errors mentioning `pip`, SSL or proxy | Usually a network blocker (work VPN, firewall). Try on a home network, then run `setup.bat` again. |
| Something else | Delete the `.venv` folder and run `setup.bat` again. It's safe; it only rebuilds the environment. |

## Mac or Linux?

Same course, no `.bat`. Open Terminal in the folder and run once:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

then use the menu with:

```bash
.venv/bin/python tools/course.py
```
