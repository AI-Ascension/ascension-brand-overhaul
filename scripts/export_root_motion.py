#!/usr/bin/env python3
"""Assemble the recorded generated title still; never create artwork or audio."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from art_policy import safe_file

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default=shutil.which('ffmpeg'))
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error('Supply an installed FFmpeg executable with --ffmpeg.')
    recipe_path = ROOT / 'brand/provenance/root-motion-recipe.json'
    recipe = json.loads(recipe_path.read_text())
    if recipe.get('operations') != ['assemble_unchanged_frames', 'fade_generated_frames',
                                     'encode', 'metadata_strip']:
        raise ValueError('The recipe must explicitly record frame assembly, fades and encoding.')
    source = safe_file(ROOT, recipe['raw_source_path'])
    still = safe_file(ROOT, recipe['still_path'])
    if digest(source) != recipe['raw_source_sha256'] or digest(still) != recipe['still_sha256']:
        raise ValueError('Recorded generated source or reduced-motion still changed.')
    if (recipe['width'], recipe['height'], recipe['fps'], recipe['frames'],
            recipe['duration_seconds'], recipe['fade_in_seconds'],
            recipe['fade_out_start_seconds'], recipe['fade_out_seconds'],
            recipe['codec'], recipe['pixel_format'], recipe['audio']) != (
            1920, 1080, 30, 45, 1.5, 0.3, 1.2, 0.3, 'libvpx-vp9', 'yuv420p', False):
        raise ValueError('Unsupported motion recipe; review an explicit implementation change.')
    with Image.open(still) as im:
        if im.size != (1920, 1080) or im.mode != 'RGB':
            raise ValueError('The title still must be the recorded 1920x1080 RGB export.')
    output = safe_file(ROOT, recipe['output_path'])
    output.parent.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([args.ffmpeg, '-version'], check=True, capture_output=True,
                             text=True).stdout.splitlines()[0]
    with tempfile.TemporaryDirectory(prefix='ascension-motion-') as temp:
        candidate = Path(temp) / 'title-transition.webm'
        command = [args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin',
                   '-loop', '1', '-framerate', '30', '-i', str(still),
                   '-vf', 'fade=t=in:st=0:d=0.3,fade=t=out:st=1.2:d=0.3',
                   '-frames:v', '45', '-an', '-c:v', 'libvpx-vp9', '-lossless', '1',
                   '-pix_fmt', 'yuv420p', '-threads', '1', '-map_metadata', '-1',
                   '-fflags', '+bitexact', '-flags:v', '+bitexact', str(candidate)]
        subprocess.run(command, check=True, capture_output=True)
        decoded = subprocess.run(
            [args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin',
             '-i', str(candidate), '-vf', 'scale=64:36', '-pix_fmt', 'rgb24',
             '-f', 'rawvideo', '-'], check=True, capture_output=True).stdout
        frame_bytes = 64 * 36 * 3
        if len(decoded) != frame_bytes * 45:
            raise ValueError('Decoded transition does not contain exactly 45 frames.')
        means = [sum(decoded[i:i + frame_bytes]) / frame_bytes
                 for i in range(0, len(decoded), frame_bytes)]
        if means[0] > 1 or max(means[9:36]) - min(means[9:36]) > 0.2:
            raise ValueError('Unexpected start or non-static hold in decoded transition: ' + repr(means))
        if any(b + 0.2 < a for a, b in zip(means[:9], means[1:10])):
            raise ValueError('Fade-in is not monotonic.')
        if any(b > a + 0.2 for a, b in zip(means[36:44], means[37:45])):
            raise ValueError('Fade-out is not monotonic.')
        shutil.copyfile(candidate, output)
    receipt = {**recipe, 'recipe_sha256': digest(recipe_path),
               'output_sha256': digest(output), 'output_bytes': output.stat().st_size,
               'ffmpeg_version': version, 'decoded_frame_count': 45,
               'decoded_rgb_sample_size': [64, 36, 3],
               'decoded_mean_rgb': [round(value, 4) for value in means],
               'validation': 'source hashes, still geometry, full decode, static hold and monotonic fades passed',
               'limits': 'Mechanical media check only; independent visual and consumer playback review remain separate.'}
    (ROOT / 'execution/reviews/root-motion-export.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'output': recipe['output_path'], 'sha256': receipt['output_sha256'],
                      'bytes': receipt['output_bytes'], 'frames': 45, 'seconds': 1.5}))


if __name__ == '__main__':
    main()
