#!/usr/bin/env python3
"""news-image-20261119 v2 entrypoint (Python 3.13, standard library only).

The finished front page lives in this repository as entry.png: 46 stories
from Thursday 19 November 2026, drawn by render.py. This program checks
that image and places an exact copy at the grader's output path, so the
judge sees the same bytes that were reviewed locally.

Run it outside the grader with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE_NAME = "entry.png"
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_image():
    """Return the entry bytes after checking magic, size and dimensions."""
    path = HERE / IMAGE_NAME
    blob = path.read_bytes()
    if blob[:8] != PNG_MAGIC:
        sys.exit("entry image is not a PNG file: %s" % path)
    if len(blob) > MAX_BYTES:
        sys.exit("entry image is %d bytes, over the 1 MiB limit" % len(blob))
    width, height = struct.unpack(">II", blob[16:24])
    if (width, height) != (1024, 1024):
        sys.exit("entry image is %dx%d, expected 1024x1024"
                 % (width, height))
    bit_depth, colour_type = blob[24], blob[25]
    if (bit_depth, colour_type) != (8, 2):
        sys.exit("entry image is not 8-bit truecolour PNG")
    if blob[-12:] != struct.pack(">I", 0) + b"IEND" + struct.pack(
            ">I", 0xAE426082):
        sys.exit("entry image is missing its IEND chunk")
    return blob


def place_copy(blob):
    """Write blob to the output directory and prove the copy matches."""
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / IMAGE_NAME
    target.write_bytes(blob)
    check = target.read_bytes()
    if hashlib.sha256(check).hexdigest() != hashlib.sha256(blob).hexdigest():
        sys.exit("written entry.png does not match the repository image")
    return target


def main():
    blob = read_image()
    target = place_copy(blob)
    print("wrote %s (%d bytes, 1024x1024 PNG)" % (target, len(blob)))


if __name__ == "__main__":
    main()
