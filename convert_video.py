#!/usr/bin/env python3
"""
Convert a video or image frames to a packed numpy array for OLED playback.

Usage:
    python convert_video.py video.mp4           # from video file (needs ffmpeg)
    python convert_video.py frames/             # from directory of images
    python convert_video.py video.mp4 out.npy   # custom output path
"""

import sys
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image

W, H = 128, 64


def _from_video(path):
    cmd = [
        "ffmpeg", "-i", path,
        "-vf", f"scale={W}:{H},format=gray",
        "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    size = W * H
    while chunk := proc.stdout.read(size):
        if len(chunk) < size:
            break
        yield np.frombuffer(chunk, dtype=np.uint8).reshape(H, W) > 128


def _from_dir(path):
    exts = {".png", ".jpg", ".jpeg", ".bmp"}
    files = sorted(f for f in Path(path).iterdir() if f.suffix.lower() in exts)
    for f in files:
        img = Image.open(f).convert("L").resize((W, H), Image.LANCZOS)
        yield np.array(img) > 128


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    src_path = Path(src)
    default_out = src_path.parent / (src_path.stem + ".npy")
    out = sys.argv[2] if len(sys.argv) > 2 else str(default_out)

    source = _from_dir(src) if Path(src).is_dir() else _from_video(src)

    rows = []
    for i, frame in enumerate(source):
        rows.append(np.packbits(frame))
        if i % 200 == 0:
            print(f"\r  {i} frames", end="", flush=True)

    data = np.array(rows, dtype=np.uint8)  # shape: (n_frames, W*H//8) = (n, 1024)
    np.save(out, data)
    print(f"\n  {len(rows)} frames → {out}  ({data.nbytes / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
