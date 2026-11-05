"""lemon-camera receiver: waits for photos from the camera and saves them.

Standard library only (Python 3.8+). Double-click "Start Lemon Receiver.bat"
to run it; close the window to stop it.

Where things go (default folder: Pictures\\LemonTree):
    LemonTree\\2026-11\\2026-11-05.jpg       the day's photo (never overwritten)
    LemonTree\\2026-11\\extras\\...          any further photo for a day that
                                             already has one
    LemonTree\\aim\\aim-2026-11-05_143001.jpg pictures from aiming mode
    LemonTree\\battery-log.csv               one row per upload (opens in Excel)
    LemonTree\\uploads.jsonl                 everything the camera sent, one
                                             JSON object per line (future
                                             sensors show up here untouched)
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

DEFAULT_PORT = 8080
MAX_BYTES = 8 * 1024 * 1024  # a full-resolution photo is well under 1 MB
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CSV_COLUMNS = ["received_at", "photo_date", "kind", "battery_v", "saved_as", "other"]

_lock = threading.Lock()  # one save at a time, so "first photo wins" is exact


def default_folder() -> Path:
    return Path.home() / "Pictures" / "LemonTree"


def photo_date(meta: dict, now: dt.datetime) -> str:
    """The day the photo belongs to: the camera's date if it sent a valid one,
    otherwise the PC's date when it arrived."""
    d = meta.get("date", "")
    if DATE_RE.match(d):
        try:
            dt.date.fromisoformat(d)
            return d
        except ValueError:
            pass
    return now.date().isoformat()


def _unique(path: Path) -> Path:
    """path, or path with _2, _3... added, whichever does not exist yet."""
    if not path.exists():
        return path
    n = 2
    while True:
        p = path.with_name(f"{path.stem}_{n}{path.suffix}")
        if not p.exists():
            return p
        n += 1


def _write_new(path: Path, data: bytes) -> bool:
    """Create path with data. Returns False (writes nothing) if it exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # "x" mode fails if the file is already there: the OS guarantees we
        # never overwrite, even if two uploads race.
        with open(path, "xb") as f:
            f.write(data)
        return True
    except FileExistsError:
        return False


def save_photo(root: Path, data: bytes, meta: dict, now: dt.datetime = None) -> dict:
    """Save one upload. Returns a dict describing what happened."""
    now = now or dt.datetime.now()
    kind = meta.get("kind", "daily")
    day = photo_date(meta, now)
    stamp = now.strftime("%Y-%m-%d_%H%M%S")

    with _lock:
        if kind == "aim":
            dest = _unique(root / "aim" / f"aim-{stamp}.jpg")
            _write_new(dest, data)
            status = "aim"
        else:
            dest = root / day[:7] / f"{day}.jpg"
            if _write_new(dest, data):
                status = "saved"
            else:
                dest = _unique(dest.parent / "extras" / f"{day}_extra-{stamp}.jpg")
                _write_new(dest, data)
                status = "extra"
        _log(root, now, day, kind, meta, dest)
    return {"status": status, "path": str(dest), "date": day}


def _log(root: Path, now: dt.datetime, day: str, kind: str, meta: dict, dest: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(dest, root)
    known = {"kind", "battery_v", "date"}
    other = " ".join(f"{k}={v}" for k, v in sorted(meta.items()) if k not in known)

    csv_path = root / "battery-log.csv"
    new = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(CSV_COLUMNS)
        w.writerow([now.isoformat(timespec="seconds"), day, kind,
                    meta.get("battery_v", ""), rel, other])

    record = {"received_at": now.isoformat(timespec="seconds"), "saved_as": rel}
    record.update(meta)
    with open(root / "uploads.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def make_handler(root: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "LemonReceiver/1"

        def _reply(self, code: int, body: dict) -> None:
            raw = (json.dumps(body) + "\n").encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # handy check from a browser: http://<pc>:8080/
            self._reply(200, {"ok": True, "app": "lemon-camera receiver"})

        def do_POST(self):
            url = urlsplit(self.path)
            if url.path != "/upload":
                return self._reply(404, {"error": "unknown path"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0 or length > MAX_BYTES:
                return self._reply(400, {"error": "bad length"})
            data = self.rfile.read(length)
            if len(data) != length or not data.startswith(b"\xff\xd8"):
                return self._reply(400, {"error": "not a JPEG"})
            meta = dict(parse_qsl(url.query, keep_blank_values=True))
            result = save_photo(root, data, meta)
            say(f"{result['status']:>5}: {result['path']}"
                f"   battery {meta.get('battery_v', '?')} V")
            self._reply(200, result)

        def log_message(self, fmt, *args):  # keep the window readable
            pass

    return Handler


def say(msg: str) -> None:
    print(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def local_ip() -> str:
    """The PC's address on the home network (no traffic is actually sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))  # TEST-NET address, never routed
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def make_server(root: Path, port: int, host: str = "0.0.0.0") -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(root))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Receive lemon-camera photos.")
    ap.add_argument("--folder", type=Path, default=default_folder())
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args(argv)
    args.folder.mkdir(parents=True, exist_ok=True)
    try:
        server = make_server(args.folder, args.port)
    except OSError as e:
        print(f"\nCould not start on port {args.port}: {e}")
        print("Is the receiver already running in another window?")
        return 1
    ip = local_ip()
    print("=" * 60)
    print("  Lemon camera receiver is running.")
    print(f"  This PC's address:  {ip}    port: {args.port}")
    print(f"  (put {ip} in config.h as RECEIVER_HOST)")
    print(f"  Photos go to:       {args.folder}")
    print("  Leave this window open. Close it to stop.")
    print("=" * 60, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
