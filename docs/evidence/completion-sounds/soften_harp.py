"""Soften the user-selected Alexander harp recording; Python stdlib only.

Input: orange-harp-decoded.wav (macOS afconvert, 16-bit PCM).
Source/license/commands are recorded in README.md. No pitch or speed change.
"""

import array
import json
import math
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parent
with wave.open(str(ROOT / "orange-harp-decoded.wav"), "rb") as source:
    channels, width, rate, frames, _, _ = source.getparams()
    assert width == 2
    samples = array.array("h", source.readframes(frames))
if sys.byteorder != "little":
    samples.byteswap()
duration = frames / rate
assert duration <= 5

# Butterworth low-pass at 3.2 kHz reduces the sharp upper edge of each pluck.
omega = math.tau * 3200 / rate
cosine = math.cos(omega)
alpha = math.sin(omega) / (2 / math.sqrt(2))
b0 = (1 - cosine) / 2 / (1 + alpha)
b1 = (1 - cosine) / (1 + alpha)
b2 = b0
a1 = -2 * cosine / (1 + alpha)
a2 = (1 - alpha) / (1 + alpha)
gain = 10 ** (-5 / 20)
output = [0] * len(samples)
for channel in range(channels):
    x1 = x2 = y1 = y2 = 0.0
    for frame in range(frames):
        index = frame * channels + channel
        x = samples[index]
        y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y
        time = frame / rate
        attack = .5 - .5 * math.cos(math.pi * min(1, time / .025))
        remaining = (frames - 1 - frame) / rate
        fade = .5 - .5 * math.cos(math.pi * min(1, remaining / 1.2))
        output[index] = round(y * gain * attack * fade)
assert max(abs(value) for value in output) < 32767
pcm = array.array("h", output)
if sys.byteorder != "little":
    pcm.byteswap()
destination = ROOT / "07-orange-harp-softened.wav"
with wave.open(str(destination), "wb") as target:
    target.setparams((channels, 2, rate, 0, "NONE", "not compressed"))
    target.writeframes(pcm.tobytes())
with wave.open(str(destination), "rb") as check:
    assert check.getnframes() == frames
    decoded = array.array("h", check.readframes(frames))
    if sys.byteorder != "little":
        decoded.byteswap()
    assert decoded[:channels] == decoded[-channels:] == array.array("h", [0] * channels)
result = {"file": destination.name, "seconds": duration, "channels": channels,
          "sample_rate": rate, "gain_db": -5, "lowpass_hz": 3200,
          "fade_in_seconds": .025, "fade_out_seconds": 1.2,
          "peak_dbfs": 20 * math.log10(max(abs(x) for x in output) / 32768),
          "checks": "PCM readback; unchanged frame count; <=5s; no clipping; zero endpoints"}
(ROOT / "softened-checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
