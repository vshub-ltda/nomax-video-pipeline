#!/usr/bin/env python3
"""verify_playback — Gap 4 implementation.

Generate a contact sheet of N frames distributed across a video, optionally
emphasizing specific user-supplied timestamps. Output is one tall image with
each frame labeled by its timestamp. This is the closest thing the assistant
has to "watching" the video — every iteration's QC pass should go through
this before declaring success.

Usage:
  verify_playback.py <video.mp4> <out.png> [--n 12] [--cols 4] [--times "1.5,5,12,29"]
"""
import argparse
import subprocess
import sys
from pathlib import Path

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"


def get_duration(video: Path) -> float:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--n", type=int, default=12, help="Number of evenly distributed frames")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--times", type=str, default=None,
                    help="Comma-separated specific timestamps to include (e.g. '1.5,5.7,12,29')")
    ap.add_argument("--scale-w", type=int, default=540,
                    help="Per-frame width (height auto-derived from source aspect)")
    args = ap.parse_args()

    duration = get_duration(args.video)

    # Decide timestamps
    if args.times:
        timestamps = sorted(set(float(t) for t in args.times.split(",")))
    else:
        # Evenly distributed, excluding boundaries to avoid black-frame edge cases
        step = duration / (args.n + 1)
        timestamps = [round((i + 1) * step, 2) for i in range(args.n)]

    # Extract each frame to a temp file
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = args.out.parent / f".verify_tmp_{args.video.stem}"
    tmp_dir.mkdir(exist_ok=True)
    frame_files = []
    for i, t in enumerate(timestamps):
        f = tmp_dir / f"f_{i:02d}.png"
        cmd = [
            FFMPEG, "-y", "-ss", f"{t:.3f}", "-i", str(args.video),
            "-frames:v", "1",
            "-vf", f"scale={args.scale_w}:-2,drawtext=text='{t:5.2f}s':fontcolor=white:fontsize=24:"
                   f"box=1:boxcolor=black@0.7:boxborderw=8:x=12:y=h-th-12",
            str(f),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        frame_files.append(f)

    # Build contact sheet by tiling frames in a grid
    rows = (len(frame_files) + args.cols - 1) // args.cols
    cmd = [FFMPEG, "-y"]
    for f in frame_files:
        cmd += ["-i", str(f)]
    # Use xstack to compose grid
    if len(frame_files) == 1:
        cmd += ["-c:v", "copy", str(args.out)]
    else:
        # xstack layout string
        positions = []
        for i in range(len(frame_files)):
            r = i // args.cols
            c = i % args.cols
            x = "+".join([f"w{j}" for j in range(c)]) if c > 0 else "0"
            y = "+".join([f"h{j*args.cols}" for j in range(r)]) if r > 0 else "0"
            positions.append(f"{x}_{y}")
        layout = "|".join(positions)
        filter_complex = f"xstack=inputs={len(frame_files)}:layout={layout}:fill=black"
        cmd += ["-filter_complex", filter_complex, "-frames:v", "1", str(args.out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("xstack failed; falling back to vertical tiling")
        # Fallback: just stack vertically
        cmd2 = [FFMPEG, "-y"]
        for f in frame_files:
            cmd2 += ["-i", str(f)]
        cmd2 += ["-filter_complex", f"vstack=inputs={len(frame_files)}", "-frames:v", "1", str(args.out)]
        subprocess.run(cmd2, capture_output=True, check=True)

    # Cleanup temp frames
    for f in frame_files:
        f.unlink(missing_ok=True)
    tmp_dir.rmdir()

    print(f"contact sheet → {args.out}")
    print(f"  {len(timestamps)} frames at: {', '.join(f'{t:.2f}s' for t in timestamps)}")


if __name__ == "__main__":
    main()
