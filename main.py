#!/usr/bin/env python3
"""Entry point: copy the pre-rendered front-page image to /output/entry.png.

Standard library only. The image is rendered by generate.py at build time
and shipped in the repository; this program just places it where the
harness expects it, so both runs write byte-identical output.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(OUT, "entry.png"))
