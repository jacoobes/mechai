
#!/usr/bin/env python3
"""
video_splicer.py: Slice a video file into labeled audio segments using ffmpeg.

Usage:
    python video_splicer.py <input_video> <timestamp_file> [-o output_dir]

Example timestamp file (each line):
    chicken-jockey 1:00.000-1:54.500
    zombie 1:55-2:30

This will extract two MP3 files: chicken-jockey.mp3 and zombie.mp3

Requirements:
    - Python 3.6+
    - ffmpeg installed and on PATH
"""
import argparse
import subprocess
import re
import sys
from pathlib import Path

def parse_timestamp_file(ts_path):
    """
    Parse a timestamp file into a list of tuples: (label, start_time, end_time).
    Lines must follow:
        <label> <start>-<end>
    where times are H:MM:SS(.SSS), M:SS(.SSS), or S(.SSS)
    """
    entries = []
    pattern = re.compile(r"^(?P<label>\S+)\s+(?P<start>\d{1,2}:(?:\d{2}:)?\d{2}(?:\.\d{1,3})?)-(?P<end>\d{1,2}:(?:\d{2}:)?\d{2}(?:\.\d{1,3})?)$")
    with open(ts_path, 'r') as f:
        for lineno, line in enumerate(f, 1):
            text = line.strip()
            if not text or text.startswith('#'):
                continue
            m = pattern.match(text)
            if not m:
                print(f"[Warning] Skipping invalid format on line {lineno}: '{text}'", file=sys.stderr)
                continue
            entries.append((m.group('label'), m.group('start'), m.group('end')))
    return entries

def slice_audio(input_file, output_dir, segments):
    """
    Use ffmpeg to slice out audio segments.
    """
    input_path = Path(input_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for label, start, end in segments:
        out_file = out_dir / f"{label}.mp3"
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-ss', start,
            '-to', end,
            '-vn',  # no video
            '-acodec', 'pcm_s16le',
            '-ar', '48000',
            '-ac', '1',
            str(out_file)
        ]
        print(f"Extracting '{label}': {start} -> {end} to {out_file}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[Error] ffmpeg failed for label '{label}': {e}", file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Slice a video into labeled audio segments using ffmpeg"
    )
    parser.add_argument('input_video', help="Path to the input video file")
    parser.add_argument('timestamp_file', help="Path to the timestamp file")
    parser.add_argument('-o', '--output-dir', default='output_segments',
                        help="Directory to save sliced audio files")
    args = parser.parse_args()

    segments = parse_timestamp_file(args.timestamp_file)
    if not segments:
        print("No valid entries found in timestamp file.", file=sys.stderr)
        sys.exit(1)

    slice_audio(args.input_video, args.output_dir, segments)

