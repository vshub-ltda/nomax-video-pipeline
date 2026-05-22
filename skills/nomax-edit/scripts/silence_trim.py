#!/usr/bin/env python3
"""Silence trim: from a Scribe transcript + clip range, find silences and produce
a keep-segments list + adjusted word timeline (timestamps in the trimmed output's frame).

Output JSON:
{
  "raw_segments": [[raw_s, raw_e], ...],   # input file ranges (absolute, for ffmpeg -ss/-t)
  "adjusted_words": [{start, end, word}, ...],  # timestamps in the OUTPUT (trimmed) clock
  "input_duration": 32.06,
  "output_duration": 30.52,
  "saved_seconds": 1.54
}

Usage:
    silence_trim.py <scribe.json> <start> <end> <out.json> [--min-silence 0.5]
"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scribe", type=Path)
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("out", type=Path)
    ap.add_argument("--min-silence", type=float, default=0.5)
    ap.add_argument("--pad", type=float, default=0.05, help="Padding kept on each side of silence")
    ap.add_argument("--extra-cut", action="append", default=[],
                    help="Extra raw [start,end] ranges to cut (e.g. stutters). Can repeat. Format: 'start,end'")
    ap.add_argument("--drop-token", action="append", default=[],
                    help="Drop words containing this substring from the adjusted transcript (e.g. '--')")
    args = ap.parse_args()

    scribe = json.loads(args.scribe.read_text())
    words = [w for w in scribe.get("words", [])
             if w.get("type") == "word" and args.start <= w["start"] < args.end]
    if not words:
        raise SystemExit("no words in range")

    # Find silences between consecutive word ends
    silences = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]
        if gap >= args.min_silence:
            silences.append((words[i-1]["end"] + args.pad, words[i]["start"] - args.pad))

    # Merge user-supplied extra cuts (stutters etc.) into the silences list
    for spec in args.extra_cut:
        a, b = spec.split(",")
        silences.append((float(a), float(b)))
    silences.sort()

    # Build keep segments: [start, sil1_start], [sil1_end, sil2_start], ..., [silN_end, end]
    keep = []
    cursor = args.start
    for sil_s, sil_e in silences:
        keep.append((cursor, sil_s))
        cursor = sil_e
    keep.append((cursor, args.end))
    # Filter zero-length
    keep = [(s, e) for s, e in keep if e > s + 0.05]

    # Compute adjusted word timestamps in OUTPUT clock; drop tokens matching any --drop-token
    adjusted = []
    raw_kept_so_far = 0.0
    for seg_s, seg_e in keep:
        seg_dur = seg_e - seg_s
        for w in words:
            text = w["text"].strip()
            if any(tok in text for tok in args.drop_token):
                continue
            if w["start"] >= seg_s and w["end"] <= seg_e:
                new_start = round(w["start"] - seg_s + raw_kept_so_far, 3)
                new_end = round(w["end"] - seg_s + raw_kept_so_far, 3)
                adjusted.append({"start": new_start, "end": new_end, "word": text})
        raw_kept_so_far += seg_dur

    input_dur = args.end - args.start
    output_dur = sum(e - s for s, e in keep)
    payload = {
        "raw_segments": [[round(s, 3), round(e, 3)] for s, e in keep],
        "adjusted_words": adjusted,
        "input_duration": round(input_dur, 3),
        "output_duration": round(output_dur, 3),
        "saved_seconds": round(input_dur - output_dur, 3),
        "n_silences_removed": len(silences),
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"silences ≥{args.min_silence}s: {len(silences)}")
    print(f"input dur:  {input_dur:.2f}s")
    print(f"output dur: {output_dur:.2f}s")
    print(f"saved:      {payload['saved_seconds']:.2f}s")
    print(f"segments to keep:")
    for s, e in keep:
        print(f"  [{s:7.2f}, {e:7.2f}]  ({e-s:.2f}s)")


if __name__ == "__main__":
    main()
