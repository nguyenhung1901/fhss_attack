#!/usr/bin/env python3
import subprocess
import sys
import os

EXPECTED = "FHSSHARD1"

if not os.path.exists("attacked.wav"):
    print("DAMAGE_FAIL")
    print("Missing attacked.wav")
    sys.exit(1)

cmd = [
    "./recover.py",
    "--cover", "cover.wav",
    "--input", "attacked.wav",
    "--output", "attacked_result.txt",
    "--log", "attacked.log",
    "--key", "31873",
    "--frame-size", "1024",
    "--msg-len", "9"
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)

if not os.path.exists("attacked_result.txt"):
    print("DAMAGE_FAIL")
    sys.exit(1)

with open("attacked_result.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read().strip()

print(f"ATTACKED_RECOVERED_TEXT={text}")

if text != EXPECTED:
    print("DAMAGE_OK")
else:
    print("DAMAGE_FAIL")
    print("The hidden message is still recoverable.")
