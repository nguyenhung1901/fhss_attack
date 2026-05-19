#!/usr/bin/env python3
import subprocess
import sys
import os

EXPECTED = "FHSSHARD1"

cmd = [
    "./recover.py",
    "--cover", "cover.wav",
    "--input", "stego.wav",
    "--output", "original.txt",
    "--log", "original.log",
    "--key", "31873",
    "--frame-size", "1024",
    "--msg-len", "9"
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)

if not os.path.exists("original.txt"):
    print("BASELINE_FAIL")
    sys.exit(1)

with open("original.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read().strip()

if text == EXPECTED:
    print("BASELINE_OK")
else:
    print("BASELINE_FAIL")
    print(f"EXPECTED={EXPECTED}")
    print(f"GOT={text}")
