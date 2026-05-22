#!/usr/bin/env python3
"""inspect_audio — Gap 2 implementation.

Given a video file + time range + (optional) Scribe + Whisper transcripts, produce
a forensic dossier so the EDITOR (human) can pick exact cut timestamps without the
assistant having to guess.

Outputs:
  - waveform.png         visual waveform with 100ms grid
  - silences.txt         silencedetect output (ranges where audio is silent)
  - scribe_words.txt     Scribe words in range with timestamps + speaker
  - whisper_words.txt    Whisper words in range with timestamps + probability
  - divergence.txt       zones where Scribe and Whisper disagree (likely stutters)
  - summary.md           human-readable summary linking all of the above

Usage:
  inspect_audio.py <video.mp4> <start_sec> <end_sec> <out_dir> \
      [--scribe <path>] [--whisper <path>] [--silence-db -30] [--silence-min 0.20]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
WAVEFORM_W = 2400
WAVEFORM_H = 480


def run(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True)


def make_waveform(video: Path, start: float, end: float, out: Path):
    duration = end - start
    cmd = [
        FFMPEG, "-y",
        "-ss", f"{start:.3f}",
        "-i", str(video),
        "-t", f"{duration:.3f}",
        "-filter_complex",
        f"[0:a]showwavespic=s={WAVEFORM_W}x{WAVEFORM_H}:colors=#C7F232|white:split_channels=0,"
        f"drawgrid=w=iw/10:h=ih:t=1:c=#444444@0.4",
        "-frames:v", "1",
        str(out),
    ]
    run(cmd)


def detect_silences(video: Path, start: float, end: float, db: float, min_dur: float):
    duration = end - start
    cmd = [
        FFMPEG, "-y",
        "-ss", f"{start:.3f}",
        "-i", str(video),
        "-t", f"{duration:.3f}",
        "-af", f"silencedetect=n={db}dB:d={min_dur}",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    silences = []
    sstart = None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([0-9.]+)", line)
        if m:
            sstart = float(m.group(1))
            continue
        m = re.search(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", line)
        if m and sstart is not None:
            silences.append((round(sstart, 3), round(float(m.group(1)), 3), round(float(m.group(2)), 3)))
            sstart = None
    return silences


def filter_scribe(scribe_path: Path, video_start_abs: float, start: float, end: float):
    """Scribe times are absolute (in source PARTE_1). Convert to clip-relative."""
    d = json.loads(scribe_path.read_text())
    out = []
    for w in d.get("words", []):
        if w.get("type") != "word":
            continue
        rel_s = w["start"] - video_start_abs
        rel_e = w["end"] - video_start_abs
        if rel_s >= start and rel_e <= end:
            out.append({
                "start": round(rel_s - start, 3),  # clip-relative time
                "end": round(rel_e - start, 3),
                "word": w["text"].strip(),
                "speaker": w.get("speaker_id", "?"),
                "logprob": w.get("logprob", 0),
            })
    return out


def filter_whisper(whisper_path: Path, start: float, end: float):
    d = json.loads(whisper_path.read_text())
    out = []
    for seg in d.get("segments", []):
        for w in seg.get("words", []):
            ws, we = w.get("start"), w.get("end")
            if ws is None or we is None:
                continue
            if ws >= start and we <= end:
                out.append({
                    "start": round(ws - start, 3),
                    "end": round(we - start, 3),
                    "word": w.get("word", "").strip(),
                    "probability": round(float(w.get("probability", 0)), 3),
                })
    return out


def find_divergence(scribe_words, whisper_words, window=0.5):
    """Identify time ranges where Scribe and Whisper disagree on content.
    Heuristic: bucket by 1s windows; if Scribe text vs Whisper text differ
    by more than the trivial article-difference threshold, flag the range.
    """
    if not scribe_words or not whisper_words:
        return []
    max_t = max(scribe_words[-1]["end"], whisper_words[-1]["end"])
    bins = []
    t = 0.0
    while t < max_t:
        sb = " ".join(w["word"] for w in scribe_words if t <= w["start"] < t + 1.0)
        wb = " ".join(w["word"] for w in whisper_words if t <= w["start"] < t + 1.0)
        if sb and wb:
            s_norm = re.sub(r"[^\w]", "", sb).lower()
            w_norm = re.sub(r"[^\w]", "", wb).lower()
            if s_norm and w_norm:
                shorter, longer = sorted([s_norm, w_norm], key=len)
                if longer and (len(longer) - len(shorter)) / len(longer) > 0.4 or shorter not in longer and longer not in shorter:
                    bins.append((round(t, 2), round(t + 1.0, 2), sb, wb))
        t += 1.0
    return bins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--scribe", type=Path, default=None)
    ap.add_argument("--scribe-video-start", type=float, default=0.0,
                    help="Absolute time in Scribe source where THIS video starts (subtract to make clip-relative)")
    ap.add_argument("--whisper", type=Path, default=None)
    ap.add_argument("--silence-db", type=float, default=-30)
    ap.add_argument("--silence-min", type=float, default=0.20)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"inspect_audio {args.video.name} [{args.start:.2f}-{args.end:.2f}s]")
    print(f"  waveform → {args.out_dir/'waveform.png'}")
    make_waveform(args.video, args.start, args.end, args.out_dir / "waveform.png")

    print(f"  silencedetect (n={args.silence_db}dB, d={args.silence_min}s)")
    silences = detect_silences(args.video, args.start, args.end, args.silence_db, args.silence_min)
    (args.out_dir / "silences.txt").write_text(
        "\n".join(f"  {s:6.2f} - {e:6.2f}  ({d:.2f}s)" for s, e, d in silences) or "(none)"
    )

    scribe_words = []
    if args.scribe and args.scribe.exists():
        scribe_words = filter_scribe(args.scribe, args.scribe_video_start, args.start, args.end)
        (args.out_dir / "scribe_words.txt").write_text(
            "\n".join(f"  {w['start']:6.3f} - {w['end']:6.3f}  [{w['speaker']:8s}]  {w['word']!r}" for w in scribe_words) or "(none)"
        )

    whisper_words = []
    if args.whisper and args.whisper.exists():
        whisper_words = filter_whisper(args.whisper, args.start, args.end)
        (args.out_dir / "whisper_words.txt").write_text(
            "\n".join(f"  {w['start']:6.3f} - {w['end']:6.3f}  (p={w['probability']:.2f})  {w['word']!r}" for w in whisper_words) or "(none)"
        )

    divergence = find_divergence(scribe_words, whisper_words)
    if divergence:
        (args.out_dir / "divergence.txt").write_text(
            "\n".join(f"  {a:5.2f} - {b:5.2f}\n    scribe : {s}\n    whisper: {w}" for a, b, s, w in divergence)
        )

    # Summary markdown
    summary = [
        f"# inspect_audio — {args.video.name} [{args.start:.2f}-{args.end:.2f}s]",
        "",
        f"![waveform](waveform.png)",
        "",
        f"## Silences (n={args.silence_db}dB, ≥{args.silence_min}s)",
        "```",
        "\n".join(f"  {s:6.2f} - {e:6.2f}  ({d:.2f}s)" for s, e, d in silences) or "  (none)",
        "```",
    ]
    if scribe_words:
        summary += ["", "## Scribe words", "```", "\n".join(f"  {w['start']:6.3f} - {w['end']:6.3f}  [{w['speaker']:>8s}]  {w['word']}" for w in scribe_words), "```"]
    if whisper_words:
        summary += ["", "## Whisper words", "```", "\n".join(f"  {w['start']:6.3f} - {w['end']:6.3f}  (p={w['probability']:.2f})  {w['word']}" for w in whisper_words), "```"]
    if divergence:
        summary += ["", "## Divergence zones (likely stutters)", "```", "\n".join(f"  [{a:5.2f}-{b:5.2f}]\n    scribe : {s}\n    whisper: {w}" for a, b, s, w in divergence), "```"]
    (args.out_dir / "summary.md").write_text("\n".join(summary))

    print(f"\nsummary → {args.out_dir/'summary.md'}")
    print(f"silences: {len(silences)}  scribe words: {len(scribe_words)}  whisper words: {len(whisper_words)}  divergence zones: {len(divergence)}")


if __name__ == "__main__":
    main()
