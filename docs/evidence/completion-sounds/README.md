# Completion sound audition — November 2, 2026

User requested five happy completion-sound auditions, no longer than five
seconds, preferably G C D G rolled upward, held and faded to silence. These are
original additive-synthesis sketches, not sampled instruments or downloaded
stock recordings. The common voicing is G3 C4 D4 G4 (A4 = 440 Hz); octave was
unspecified. Instrument names describe intended timbres, not actual recordings.

| Preview | Duration | Intended character |
| --- | --- | --- |
| 01-warm-keys.wav | 4.2s | Rounded, soft electric-key-like tone |
| 02-soft-harp.wav | 4.0s | Clearer plucked attack and overlapping ringing notes |
| 03-rounded-bell.wav | 4.4s | More prominent upper partials and a longer ring |
| 04-mellow-marimba.wav | 3.6s | Shorter, woody attack with a fading tail |
| 05-airy-pad.wav | 4.8s | Softest onset and longest sustained envelope |

All are mono 44.1 kHz / 16-bit WAV with common peak level −10.46 dBFS;
equal peak levels do not imply equal perceived loudness. Notes overlap during
the roll; all voices and short synthetic echoes share the final smooth fade.
No samples, paid generation, microphone, dependencies or app changes were used.
TODO: user audition and selection, perceived loudness/device checks, and any
later application integration/mute/trigger behavior. Nothing is wired to saves
or breathing completion yet. No subjective listening verification is claimed.

## Search provenance

Web search found related stock directions, but did not verify the requested
pitch sequence, so the five auditions were synthesized to match it exactly:

- [Wyzowl SFX Kit](https://wyzowl.com/sfx-kit/) describes a warm rising three-note
  marimba notification; that description differs from the requested four notes.
- [Orange Free Sounds harp notification](https://orangefreesounds.com/harp-notification-sound/)
  is a related harp candidate; exact pitch/fade fit was not verified.
- [Freesound harp-motif2 by DaVince21](https://freesound.org/people/DaVince21/sounds/563311/)
  is described as a short app-notification harp motif; exact fit was not verified.

These links are discovery references; none of their audio is included here.

## Reproduction and observed checks

Command: `backend/.venv/bin/python docs/evidence/completion-sounds/render.py`.
The script uses only the Python standard library and writes these five WAVs and
`checks.json`. Readback confirmed lengths 3.6–4.8 seconds, PCM format, no sample
clipping, zero endpoints and near-silent last 20ms. These numeric checks do not
establish pleasantness, natural-instrument realism or playback compatibility.
Application tests were not rerun for these unintegrated audition artifacts.

## Marimba octave-up follow-up — November 2, 2026

User requested the same marimba one octave higher. Added
`06-mellow-marimba-octave-up.wav`: G4 C5 D5 G5, 3.6 seconds. The renderer
uses transpose=12 with the original marimba envelope, roll spacing, harmonics,
echoes and peak target. Original auditions are preserved. Reran the render
command and PCM readback checks successfully; subjective playback remains for
user audition. No application integration.

## Softer original stock harp — November 2, 2026

At the user's request, downloaded Alexander's “Harp Notification Sound” from
https://orangefreesounds.com/harp-notification-sound/ (January 17, 2024),
direct MP3 https://orangefreesounds.com/wp-content/uploads/2024/01/Harp-notification-sound.mp3.
Source license: CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/.
Attribution: “Harp Notification Sound” by Alexander / Orange Free Sounds,
modified by reducing gain 5 dB, Butterworth low-pass at 3.2 kHz, 25ms fade-in
and 1.2s fade-out. Original pitch/speed/duration preserved; derivative remains
noncommercial with attribution. This supersedes the earlier no-stock-audio
statement for these newly added stock files only.

Files: orange-harp-original.mp3 (unedited source), orange-harp-decoded.wav
(PCM working copy), 07-orange-harp-softened.wav (edited preview),
soften_harp.py (stdlib processing), softened-checks.json (numeric results).
Commands: curl --fail --location --max-time 30 [direct URL] --output [original];
afconvert -f WAVE -d LEI16 [original] [decoded];
backend/.venv/bin/python docs/evidence/completion-sounds/soften_harp.py.
Network access needed approved escalation after sandbox DNS failure; afconvert
needed approved escalation after sandbox codec failure. No installs.
Observed duration 4.1012s; stereo 44.1kHz PCM readback, unchanged frame count,
no clipping and zero endpoints passed. User audition remains the subjective
quality check. No application integration or application tests.

## Application selection — November 2, 2026

User approved the softened original harp for successful emotion logging and
completed guided breathing. The exact approved WAV is copied to
frontend/src/components/completion-sound/harp-softened.wav, with source/license
credits alongside it. The prior audition-only statements describe earlier work;
this cue is now integrated. Other audition variants remain unintegrated.

## Sparse descending auditions — November 2, 2026

User rejected the linked glissandos and clarified: much fewer notes, arpeggiated
high to low, subdued/winding down rather than positive or exciting. Added three
original additive-synthesis sketches, not sampled harps or found recordings:

- `08-descending-soft-pluck.wav`: four notes G4 D4 C4 G3, 4.0s.
- `09-descending-warm-keys.wav`: three notes E4 C4 A3, 4.2s.
- `10-descending-open-tones.wav`: three notes D4 A3 D3, 4.4s.

Notes overlap and decrease in voice gain; no repeated pattern or glissando.
All previews peak at −14.89 dBFS and fade to silence. Timbre names describe
synthetic intentions; user audition is still needed to judge tone/loudness.
Search found [Arpeggios Descending by livingroomClassics](https://motionarray.com/sound-effects/arpeggios-descending-82260/),
described as five smartphone-game notification arpeggios. It was not sampled,
downloaded or independently listened to; search descriptions did not establish
the requested sparse/subdued character.

Command: `backend/.venv/bin/python docs/evidence/completion-sounds/render_wind_down.py`.
`wind-down-checks.json` records successful PCM readback, durations, no sample
clipping, zero endpoints and near-silent last 20ms. No dependencies, provider
calls, microphone use, app integration or application test runs. Proposed early
end message/Return home behavior and final sound choice remain pending.


### November 2, 2026 — combined descending audition

User requested combining the first and third sparse previews. Codex added
`11-pluck-and-open-tones.wav`, layering soft pluck and open tones simultaneously
at equal gains, with original timing/pitches and a shared −14.89 dBFS peak target.
Reproduction: `backend/.venv/bin/python docs/evidence/completion-sounds/blend_wind_down.py`.
Added the stdlib renderer and blend-checks.json alongside the preview. PCM
readback verified 4.4s, no clipping and silent endpoints/tail. Subjective audition
is pending. No app integration, dependencies, provider calls or app test runs.
