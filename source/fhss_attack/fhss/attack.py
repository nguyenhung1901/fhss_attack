#!/usr/bin/env python3
import argparse
import wave
import random
import os

def clamp16(x):
    return max(-32768, min(32767, int(x)))

def read_wav(path):
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

def write_wav(path, params, samples):
    data = bytearray()
    for s in samples:
        s = clamp16(s)
        data.extend(int(s).to_bytes(2, byteorder="little", signed=True))

    with wave.open(path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(bytes(data))

def quantize(samples, step):
    out = []
    for s in samples:
        q = round(s / step) * step
        out.append(clamp16(q))
    return out

def add_noise(samples, amplitude, seed):
    random.seed(seed)
    out = []
    for s in samples:
        n = random.randint(-amplitude, amplitude)
        out.append(clamp16(s + n))
    return out

def clear_lsb(samples, bits):
    if bits < 1 or bits > 8:
        raise ValueError("bits must be between 1 and 8")

    mask = ~((1 << bits) - 1)
    out = []

    for s in samples:
        if s >= 0:
            out.append(clamp16(s & mask))
        else:
            mag = abs(s)
            cleared = mag & mask
            out.append(clamp16(-cleared))

    return out

def main():
    parser = argparse.ArgumentParser(
        description="Apply controlled attacks to an FHSS stego WAV file."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="attacked.wav")
    parser.add_argument("--method", choices=["quantize", "noise", "lsb-clear"], required=True)
    parser.add_argument("--step", type=int, default=8, help="Quantization step for quantize method")
    parser.add_argument("--amplitude", type=int, default=4, help="Noise amplitude for noise method")
    parser.add_argument("--bits", type=int, default=3, help="Number of low bits to clear")
    parser.add_argument("--seed", type=int, default=12345, help="Seed for noise method")
    args = parser.parse_args()

    params, samples = read_wav(args.input)

    if args.method == "quantize":
        attacked = quantize(samples, args.step)
        desc = f"method=quantize step={args.step}"
    elif args.method == "noise":
        attacked = add_noise(samples, args.amplitude, args.seed)
        desc = f"method=noise amplitude={args.amplitude} seed={args.seed}"
    else:
        attacked = clear_lsb(samples, args.bits)
        desc = f"method=lsb-clear bits={args.bits}"

    write_wav(args.output, params, attacked)

    if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
        print("ATTACK_CREATED")
        print(f"INPUT_FILE={args.input}")
        print(f"OUTPUT_FILE={args.output}")
        print(desc)
    else:
        print("ATTACK_FAIL")

if __name__ == "__main__":
    main()
