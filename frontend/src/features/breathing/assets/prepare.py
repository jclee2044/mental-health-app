"""Trim selected CC0 cues; slow inhale to 4s and exhale to 5s, followed by 1s of quiet."""
from array import array
from pathlib import Path
import struct
import sys
import wave

RATE = 48000

with wave.open(sys.argv[1]) as original:
    assert (original.getnchannels(), original.getsampwidth(), original.getframerate()) == (2, 2, RATE)
    samples = array('h', original.readframes(original.getnframes()))
    if sys.byteorder != 'little':
        samples.byteswap()

for name, start, end, seconds in [('inhale', 7.00, 10.00, 4), ('exhale', 25.35, 28.90, 6)]:
    # Retain source samples/level with 10ms source-edge fades.
    # Sample clocks slow inhale 3s -> 4s and exhale 3.55s -> 5s.
    output_rate = 36000 if name == 'inhale' else 34080
    clip = samples[round(start * RATE) * 2:round(end * RATE) * 2]
    frames, fade = len(clip) // 2, round(.01 * RATE)
    for frame in range(frames):
        gain = min(1, frame / fade, (frames - 1 - frame) / fade)
        for channel in range(2):
            index = frame * 2 + channel
            clip[index] = round(clip[index] * gain)
    clip.extend([0] * (seconds * output_rate * 2 - len(clip)))
    with wave.open(str(Path(__file__).parent / f'{name}.wav'), 'wb') as target:
        target.setparams((2, 2, output_rate, 0, 'NONE', 'not compressed'))
        target.writeframes(struct.pack('<' + 'h' * len(clip), *clip))
