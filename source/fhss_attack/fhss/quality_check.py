#!/usr/bin/env python3
import wave
import os
import sys

MAX_AVG_DIFF = 20.0
MAX_PEAK_DIFF = 200

def read_samples(path):
    with wave.open(path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())

    if params.nchannels != 1 or params.sampwidth != 2:
        raise ValueError("Only mono 16-bit PCM WAV is supported")

    data = bytearray(frames)
    samples = []
    for i in range(0, len(data), 2):
        value = int.from_bytes(bytes([data[i], data[i+1]]), byteorder="little", signed=True)
        samples.append(value)

    return params, samples

if not os.path.exists("attacked.wav"):
    print("QUALITY_FAIL")
    print("Missing attacked.wav")
    sys.exit(1)

try:
    stego_params, stego = read_samples("stego.wav")
    attacked_params, attacked = read_samples("attacked.wav")
except Exception as e:
    print("QUALITY_FAIL")
    print(f"ERROR={e}")
    sys.exit(1)

if stego_params != attacked_params:
    print("QUALITY_FAIL")
    print("WAV parameters changed.")
    sys.exit(1)

if len(stego) != len(attacked):
    print("QUALITY_FAIL")
    print("Sample count changed.")
    sys.exit(1)

diffs = [abs(a - s) for s, a in zip(stego, attacked)]
avg_diff = sum(diffs) / len(diffs)
peak_diff = max(diffs)

print(f"AVG_DIFF={avg_diff:.4f}")
print(f"PEAK_DIFF={peak_diff}")

if avg_diff > 0 and avg_diff <= MAX_AVG_DIFF and peak_diff <= MAX_PEAK_DIFF:
    print("QUALITY_OK")
else:
    print("QUALITY_FAIL")
    print("The attack is either too small or too destructive.")
