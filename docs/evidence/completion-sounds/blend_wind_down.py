"""Layer auditions 1 and 3 simultaneously, preserving their pitches and timing."""
import array
import json
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parent
SOURCES = ("08-descending-soft-pluck.wav", "10-descending-open-tones.wav")


def read(path):
    with wave.open(str(path), "rb") as source:
        assert (source.getnchannels(), source.getsampwidth(), source.getframerate()) == (1, 2, 44100)
        samples = array.array("h", source.readframes(source.getnframes()))
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


if __name__ == "__main__":
    layers = [read(ROOT / name) for name in SOURCES]
    # Equal layer gains; pad the shorter pluck with silence. No extra notes.
    mixed = [sum(layer[index] * .5 for layer in layers if index < len(layer))
             for index in range(max(map(len, layers)))]
    scale = .18 * 32767 / max(map(abs, mixed))
    pcm = array.array("h", (round(sample * scale) for sample in mixed))
    if sys.byteorder != "little":
        pcm.byteswap()
    path = ROOT / "11-pluck-and-open-tones.wav"
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, 44100, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())
    checked = read(path)
    assert len(checked) == 194040
    assert checked[0] == checked[-1] == 0
    assert max(map(abs, checked)) < 32767
    assert max(map(abs, checked[-882:])) < 10
    result = dict(file=path.name, sources=SOURCES, blend="simultaneous equal gains",
                  duration_seconds=len(checked) / 44100,
                  checks="PCM readback; 4.4s; no clipping; silent endpoints/tail")
    (ROOT / "blend-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
