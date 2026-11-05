"""Build a time-lapse video from the lemon tree photos.

Standard library only. Writes an MJPEG .avi: the daily JPEGs are copied into
the video as-is, no re-encoding, so nothing is lost and no extra software is
needed to make it. VLC plays it. Windows' own Media Player / "Movies & TV"
is expected to (MJPEG is a standard AVI codec) but that is UNVERIFIED.

If ffmpeg happens to be installed, pass --mp4 to also get a smaller .mp4.

Only the day photos (LemonTree\\YYYY-MM\\YYYY-MM-DD.jpg) are used; aiming shots
and extras are skipped.
"""

import argparse
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.jpg$", re.IGNORECASE)


def default_folder() -> Path:
    return Path.home() / "Pictures" / "LemonTree"


def find_photos(root: Path):
    """Day photos, oldest first. Only YYYY-MM folders, so extras/aim are skipped."""
    photos = [p for p in root.glob("????-??/*.jpg") if DAY_RE.match(p.name)]
    return sorted(photos, key=lambda p: p.name)


def jpeg_size(data: bytes):
    """(width, height) from a JPEG's SOF marker, or None."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + seg_len
    return None


def _chunk(fourcc: bytes, payload: bytes) -> bytes:
    pad = b"\x00" if len(payload) % 2 else b""
    return fourcc + struct.pack("<I", len(payload)) + payload + pad


def _list(kind: bytes, payload: bytes) -> bytes:
    return b"LIST" + struct.pack("<I", len(payload) + 4) + kind + payload


def write_mjpeg_avi(frames, out: Path, fps: int) -> None:
    """frames: list of JPEG bytes, all the same size. Writes an AVI 1.0 file
    (fine below 1 GB, i.e. several years of daily photos)."""
    if not frames:
        raise ValueError("no frames")
    size = jpeg_size(frames[0])
    if not size:
        raise ValueError("first photo is not a readable JPEG")
    w, h = size
    biggest = max(len(f) for f in frames)
    n = len(frames)
    usec = int(1_000_000 / fps)

    avih = struct.pack("<IIIIIIIIIIIIII", usec, biggest * fps, 0, 0x10, n, 0, 1,
                       biggest, w, h, 0, 0, 0, 0)
    strh = struct.pack("<4s4sIHHIIIIIIIIhhhh", b"vids", b"MJPG", 0, 0, 0, 0,
                       1, fps, 0, n, biggest, 0xFFFFFFFF, 0, 0, 0, w, h)
    strf = struct.pack("<IiiHH4sIiiII", 40, w, h, 1, 24, b"MJPG", w * h * 3, 0, 0, 0, 0)
    hdrl = _list(b"hdrl", _chunk(b"avih", avih) +
                 _list(b"strl", _chunk(b"strh", strh) + _chunk(b"strf", strf)))

    movi_parts, index, offset = [], [], 4  # offsets are from the 'movi' fourcc
    for f in frames:
        c = _chunk(b"00dc", f)
        index.append(struct.pack("<4sIII", b"00dc", 0x10, offset, len(f)))
        movi_parts.append(c)
        offset += len(c)
    movi = _list(b"movi", b"".join(movi_parts))
    idx1 = _chunk(b"idx1", b"".join(index))
    body = b"AVI " + hdrl + movi + idx1
    out.write_bytes(b"RIFF" + struct.pack("<I", len(body)) + body)


def build(root: Path, out: Path, fps: int):
    photos = find_photos(root)
    if not photos:
        return None, "No daily photos found in " + str(root)
    frames, skipped = [], []
    first_size = None
    for p in photos:
        data = p.read_bytes()
        s = jpeg_size(data)
        if s is None:
            skipped.append(p.name + " (unreadable)")
            continue
        if first_size is None:
            first_size = s
        if s != first_size:
            skipped.append(f"{p.name} (size {s[0]}x{s[1]})")
            continue
        frames.append(data)
    write_mjpeg_avi(frames, out, fps)
    return len(frames), skipped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Make a time-lapse of the lemon tree.")
    ap.add_argument("--folder", type=Path, default=default_folder())
    ap.add_argument("--fps", type=int, default=10, help="photos per second (default 10)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--mp4", action="store_true", help="also make an .mp4 with ffmpeg")
    args = ap.parse_args(argv)
    out = args.out or args.folder / "lemon-timelapse.avi"
    count, skipped = build(args.folder, out, args.fps)
    if count is None:
        print(skipped)
        return 1
    print(f"Made {out} from {count} photos ({count / args.fps:.1f} seconds).")
    for s in skipped:
        print("  skipped", s)
    if args.mp4:
        ff = shutil.which("ffmpeg")
        if not ff:
            print("ffmpeg not found; only the .avi was made.")
        else:
            mp4 = out.with_suffix(".mp4")
            subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(mp4)], check=False)
            print(f"Made {mp4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
