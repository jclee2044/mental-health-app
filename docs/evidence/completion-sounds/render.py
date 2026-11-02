"""Render five original completion-sound auditions using only Python's stdlib.

Run from the project root: backend/.venv/bin/python docs/evidence/completion-sounds/render.py
No samples, model APIs, project dependencies, or application integration.
"""

import array
import json
import math
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parent
RATE = 44100
NOTES = (55, 60, 62, 67)  # G3 C4 D4 G4; ascending, overlapping roll.
OPTIONS = (
    ("01-warm-keys", 4.2, .13, .014, 1.8, (1, .28, .12, .035), "Warm keys"),
    ("02-soft-harp", 4.0, .11, .006, 1.3, (1, .38, .20, .10, .04), "Soft harp"),
    ("03-rounded-bell", 4.4, .14, .018, 2.1, (1, .12, .24, .035, .05), "Rounded bell"),
    ("04-mellow-marimba", 3.6, .12, .008, 1.0, (1, .05, .08, .20), "Mellow marimba"),
    ("05-airy-pad", 4.8, .18, .17, 3.5, (1, .12, .055), "Airy pad"),
)


def render(slug, duration, roll, attack, decay, harmonics, title, transpose=0):
    count = round(duration * RATE)
    dry = [0.0] * count
    for note_index, midi in enumerate(NOTES):
        frequency = 440 * 2 ** ((midi + transpose - 69) / 12)
        start = round((.03 + note_index * roll) * RATE)
        for index in range(start, count):
            age = (index - start) / RATE
            envelope = (1 - math.exp(-age / attack)) * math.exp(-age / decay)
            # Higher partials decay faster, avoiding a harsh lingering edge.
            sample = sum(
                amplitude * math.exp(-age * partial * .32)
                * math.sin(math.tau * frequency * (partial + 1) * age)
                for partial, amplitude in enumerate(harmonics)
            )
            dry[index] += sample * envelope * (1 - note_index * .045)
    wet = dry.copy()
    for delay, gain in ((.073, .12), (.137, .075), (.223, .04)):
        offset = round(delay * RATE)
        for index in range(offset, count):
            wet[index] += dry[index - offset] * gain
    # Shared smooth fade reaches zero at the file boundary, including echoes.
    fade_start = .9
    for index in range(count):
        time = index / RATE
        phase = max(0, min(1, (time - fade_start) / (duration - fade_start)))
        wet[index] *= .5 * (1 + math.cos(math.pi * phase))
    peak = max(abs(value) for value in wet)
    pcm = array.array("h", (round(value / peak * .30 * 32767) for value in wet))
    if sys.byteorder != "little":
        pcm.byteswap()
    path = ROOT / (slug + ".wav")
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())
    with wave.open(str(path), "rb") as check:
        assert check.getnframes() / check.getframerate() == duration <= 5
        assert check.getnchannels() == 1 and check.getsampwidth() == 2
        decoded = array.array("h", check.readframes(check.getnframes()))
        if sys.byteorder != "little":
            decoded.byteswap()
        assert decoded[0] == decoded[-1] == 0
        assert max(abs(value) for value in decoded) < 32767
        tail = decoded[-round(RATE * .02):]
        assert max(abs(value) for value in tail) < 10
    return {"file": path.name, "title": title, "duration_seconds": duration,
            "notes": [f"{name}{(midi + transpose) // 12 - 1}"
                      for name, midi in zip(("G", "C", "D", "G"), NOTES)],
            "roll_spacing_seconds": roll,
            "peak_dbfs": round(20 * math.log10(.30), 2),
            "checks": "duration <= 5s; PCM readback; no clipping; silent endpoints/tail"}


if __name__ == "__main__":
    results = [render(*option) for option in OPTIONS]
    results.append(render("06-mellow-marimba-octave-up", *OPTIONS[3][1:-1],
                          "Mellow marimba — octave up", transpose=12))
    (ROOT / "checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
