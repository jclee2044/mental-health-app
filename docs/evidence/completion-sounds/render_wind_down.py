"""Original sparse descending auditions; stdlib only, no app integration."""

import array
import json
import math
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parent
RATE = 44100
OPTIONS = (
    ("08-descending-soft-pluck", (67, 62, 60, 55), ("G4", "D4", "C4", "G3"), .28, .012, 1.2, (1, .18, .06), 4.0),
    ("09-descending-warm-keys", (64, 60, 57), ("E4", "C4", "A3"), .38, .035, 1.5, (1, .08, .025), 4.2),
    ("10-descending-open-tones", (62, 57, 50), ("D4", "A3", "D3"), .44, .055, 1.6, (1, .035), 4.4),
)


def render(option):
    slug, notes, names, spacing, attack, decay, partials, duration = option
    count = round(duration * RATE)
    samples = [0.0] * count
    for position, midi in enumerate(notes):
        start = round((.03 + position * spacing) * RATE)
        frequency = 440 * 2 ** ((midi - 69) / 12)
        for index in range(start, count):
            age = (index - start) / RATE
            envelope = (1 - math.exp(-age / attack)) * math.exp(-age / decay)
            tone = sum(gain * math.exp(-age * partial * .5)
                       * math.sin(math.tau * frequency * (partial + 1) * age)
                       for partial, gain in enumerate(partials))
            samples[index] += tone * envelope * (.83 ** position)
    # No repeats or pitch sweeps. Overlapping decays, then a shared silent tail.
    fade_start = .03 + (len(notes) - 1) * spacing + .25
    for index in range(count):
        phase = max(0, min(1, (index / RATE - fade_start) / (duration - fade_start)))
        samples[index] *= .5 * (1 + math.cos(math.pi * phase))
    peak = max(map(abs, samples))
    pcm = array.array("h", (round(value / peak * .18 * 32767) for value in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    path = ROOT / (slug + ".wav")
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())
    with wave.open(str(path), "rb") as check:
        assert check.getnframes() / check.getframerate() == duration
        assert check.getnchannels() == 1 and check.getsampwidth() == 2
        decoded = array.array("h", check.readframes(check.getnframes()))
        if sys.byteorder != "little":
            decoded.byteswap()
        assert decoded[0] == decoded[-1] == 0
        assert max(map(abs, decoded)) < 32767
        assert max(map(abs, decoded[-882:])) < 10
    return dict(file=path.name, notes=names, note_count=len(notes),
                spacing_seconds=spacing, duration_seconds=duration,
                peak_dbfs=round(20 * math.log10(.18), 2),
                checks="PCM readback; duration; no clipping; silent endpoints and last 20ms")


if __name__ == "__main__":
    results = [render(option) for option in OPTIONS]
    (ROOT / "wind-down-checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
