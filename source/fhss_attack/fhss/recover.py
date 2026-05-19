#!/usr/bin/env python3
import argparse
import wave
import random

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

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        chars.append(chr(int(chunk, 2)))
    return ''.join(chars)

def recover_message(cover_path, input_path, key, frame_size, msg_len, log_path):
    _, cover = read_samples(cover_path)
    _, stego = read_samples(input_path)

    total_bits = msg_len * 8
    random.seed(key)

    bits = []
    lines = []

    for frame_idx in range(total_bits):
        frame_start = frame_idx * frame_size
        hop_offset = random.randint(0, frame_size - 1)
        sample_index = frame_start + hop_offset

        cover_value = cover[sample_index]
        stego_value = stego[sample_index]
        diff = stego_value - cover_value

        bit = "1" if diff > 0 else "0"
        bits.append(bit)

        lines.append(
            f"frame={frame_idx} hop_offset={hop_offset} sample={sample_index} "
            f"cover={cover_value} stego={stego_value} diff={diff} recovered_bit={bit}"
        )

    text = bits_to_text(''.join(bits))

    with open(log_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover", default="cover.wav")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="recovered.txt")
    parser.add_argument("--log", default="recover.log")
    parser.add_argument("--key", type=int, required=True)
    parser.add_argument("--frame-size", type=int, required=True)
    parser.add_argument("--msg-len", type=int, required=True)
    args = parser.parse_args()

    text = recover_message(
        args.cover,
        args.input,
        args.key,
        args.frame_size,
        args.msg_len,
        args.log
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)

    print("RECOVER_RUN_OK")
    print(f"INPUT_FILE={args.input}")
    print(f"OUTPUT_FILE={args.output}")
    print(f"RECOVERED_TEXT={text}")

if __name__ == "__main__":
    main()
