"""Tests for the PC side. Run:  python -m unittest discover -s tests"""
import datetime as dt
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "receiver"))

import lemon_receiver as rx  # noqa: E402
import timelapse as tl  # noqa: E402


def fake_jpeg(w=64, h=48, tag=b""):
    """Smallest thing our code treats as a JPEG: SOI, SOF0 with a size, EOI."""
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, h, w, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + b"\xff\xe0\x00\x04" + b"\x00\x00" + sof + tag + b"\xff\xd9"


NOW = dt.datetime(2026, 11, 5, 12, 0, 5)


class SavePhoto(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_daily_goes_to_dated_folder(self):
        r = rx.save_photo(self.root, fake_jpeg(), {"kind": "daily", "date": "2026-11-05"}, NOW)
        self.assertEqual(r["status"], "saved")
        self.assertTrue((self.root / "2026-11" / "2026-11-05.jpg").exists())

    def test_first_picture_of_day_is_never_overwritten(self):
        first, second = fake_jpeg(tag=b"first"), fake_jpeg(tag=b"second")
        rx.save_photo(self.root, first, {"date": "2026-11-05"}, NOW)
        r = rx.save_photo(self.root, second, {"date": "2026-11-05"}, NOW)
        self.assertEqual(r["status"], "extra")
        self.assertEqual((self.root / "2026-11" / "2026-11-05.jpg").read_bytes(), first)
        self.assertEqual(Path(r["path"]).read_bytes(), second)
        self.assertIn("extras", r["path"])
        # and a third in the same second does not overwrite the second
        r3 = rx.save_photo(self.root, fake_jpeg(tag=b"third"), {"date": "2026-11-05"}, NOW)
        self.assertNotEqual(r3["path"], r["path"])
        self.assertEqual(Path(r["path"]).read_bytes(), second)

    def test_held_photo_keeps_its_own_date(self):
        later = dt.datetime(2026, 11, 7, 12, 0)
        rx.save_photo(self.root, fake_jpeg(), {"kind": "held", "date": "2026-11-05"}, later)
        self.assertTrue((self.root / "2026-11" / "2026-11-05.jpg").exists())

    def test_missing_or_bad_date_uses_pc_date(self):
        for bad in ({}, {"date": "garbage"}, {"date": "2026-13-45"}, {"date": "../../x"}):
            d = self.root / "2026-11" / "2026-11-05.jpg"
            if d.exists():
                d.unlink()
            rx.save_photo(self.root, fake_jpeg(), bad, NOW)
            self.assertTrue(d.exists(), bad)

    def test_aim_photos_do_not_take_the_day_slot(self):
        r = rx.save_photo(self.root, fake_jpeg(), {"kind": "aim", "date": "2026-11-05"}, NOW)
        self.assertEqual(r["status"], "aim")
        self.assertFalse((self.root / "2026-11" / "2026-11-05.jpg").exists())
        r2 = rx.save_photo(self.root, fake_jpeg(), {"kind": "aim"}, NOW)
        self.assertNotEqual(r["path"], r2["path"])

    def test_battery_and_unknown_fields_are_logged(self):
        rx.save_photo(self.root, fake_jpeg(),
                      {"kind": "daily", "date": "2026-11-05", "battery_v": "3.912",
                       "boot": "7", "temp_c": "4.5"}, NOW)
        rows = (self.root / "battery-log.csv").read_text().splitlines()
        self.assertEqual(rows[0].split(","), rx.CSV_COLUMNS)
        self.assertIn("3.912", rows[1])
        self.assertIn("temp_c=4.5", rows[1])
        rec = json.loads((self.root / "uploads.jsonl").read_text().splitlines()[0])
        self.assertEqual(rec["temp_c"], "4.5")
        self.assertEqual(rec["battery_v"], "3.912")


class ServerEndToEnd(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.server = rx.make_server(self.root, 0, "127.0.0.1")
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.root)

    def post(self, path, body):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data=body,
                                     method="POST", headers={"Content-Type": "image/jpeg"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_upload_like_the_camera(self):
        # Exactly the path format the firmware builds (see test_logic.cpp).
        path = ("/upload?v=1&kind=daily&taken=2026-11-05T12%3A00%3A03-05%3A00"
                "&date=2026-11-05&battery_v=3.950&boot=12&held=0")
        code, body = self.post(path, fake_jpeg())
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "saved")
        self.assertTrue((self.root / "2026-11" / "2026-11-05.jpg").exists())
        rec = json.loads((self.root / "uploads.jsonl").read_text())
        self.assertEqual(rec["taken"], "2026-11-05T12:00:03-05:00")
        # a duplicate is still a 200, so the camera deletes its copy
        code, body = self.post(path, fake_jpeg(tag=b"2"))
        self.assertEqual((code, body["status"]), (200, "extra"))

    def test_rejects_non_jpeg_and_wrong_path(self):
        self.assertEqual(self.post("/upload?date=2026-11-05", b"hello")[0], 400)
        self.assertEqual(self.post("/elsewhere", fake_jpeg())[0], 404)
        self.assertFalse(any(self.root.glob("*/*.jpg")))

    def test_get_says_hello(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=5) as r:
            self.assertTrue(json.loads(r.read())["ok"])


class Timelapse(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_jpeg_size(self):
        self.assertEqual(tl.jpeg_size(fake_jpeg(2048, 1536)), (2048, 1536))
        self.assertIsNone(tl.jpeg_size(b"\xff\xd8nothing"))

    def test_picks_only_day_photos_in_order(self):
        for name in ["2026-12/2026-12-01.jpg", "2026-11/2026-11-30.jpg",
                     "2026-11/extras/2026-11-30_extra-x.jpg", "aim/aim-1.jpg"]:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(fake_jpeg())
        names = [p.name for p in tl.find_photos(self.root)]
        self.assertEqual(names, ["2026-11-30.jpg", "2026-12-01.jpg"])

    def test_avi_structure(self):
        frames = [fake_jpeg(tag=bytes([i])) for i in range(5)]
        out = self.root / "t.avi"
        tl.write_mjpeg_avi(frames, out, 10)
        b = out.read_bytes()
        self.assertEqual(b[:4], b"RIFF")
        self.assertEqual(struct.unpack("<I", b[4:8])[0], len(b) - 8)
        self.assertEqual(b[8:12], b"AVI ")
        self.assertEqual(b.count(b"00dc"), 10)  # 5 chunks + 5 index entries
        self.assertIn(b"idx1", b)

    def test_skips_odd_sized_photos(self):
        for i, size in enumerate([(64, 48), (64, 48), (32, 32)]):
            p = self.root / "2026-11" / f"2026-11-0{i + 1}.jpg"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(fake_jpeg(*size))
        count, skipped = tl.build(self.root, self.root / "o.avi", 10)
        self.assertEqual(count, 2)
        self.assertEqual(len(skipped), 1)

    @unittest.skipUnless(shutil.which("ffprobe") and shutil.which("ffmpeg"), "needs ffmpeg")
    def test_real_players_can_read_it(self):
        src = self.root / "src"
        src.mkdir()
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc=size=320x240:rate=1", "-frames:v", "3",
                        str(src / "f%d.jpg")], check=True)
        frames = [(src / f"f{i}.jpg").read_bytes() for i in (1, 2, 3)]
        out = self.root / "real.avi"
        tl.write_mjpeg_avi(frames, out, 10)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=codec_name,width,height,nb_read_frames",
             "-of", "default=nw=1", str(out)], capture_output=True, text=True, check=True)
        self.assertIn("codec_name=mjpeg", probe.stdout)
        self.assertIn("width=320", probe.stdout)
        self.assertIn("nb_read_frames=3", probe.stdout)


if __name__ == "__main__":
    unittest.main()
