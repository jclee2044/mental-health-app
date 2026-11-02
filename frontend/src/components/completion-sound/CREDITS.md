# Completion harp

“Harp Notification Sound” by Alexander / Orange Free Sounds, January 17, 2024.

- Source: https://orangefreesounds.com/harp-notification-sound/
- Original MP3: https://orangefreesounds.com/wp-content/uploads/2024/01/Harp-notification-sound.mp3
- License: CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/.
- Modified for this noncommercial localhost coursework prototype: −5dB gain,
  3.2kHz Butterworth low-pass, 25ms fade-in and 1.2s fade-out; no speed/pitch
  changes. User auditioned and selected the softened edit November 2, 2026.
- `harp-softened.wav` is the exact approved 4.1012s stereo PCM preview from
  `docs/evidence/completion-sounds/07-orange-harp-softened.wav`. Reproduction:
  `docs/evidence/completion-sounds/soften_harp.py` and its README.

Shared sound infrastructure resides in the existing interface `components`
checkpoint scope. Features own their triggers and controls; no sibling imports.
Inline Vite import keeps the cue with the cached JS bundle. Playback is optional
and never blocks saving, timing or visible confirmation. Context/decode/autoplay
failures remain silent; there is no delayed replay or automatic retry.

November 2 revision: this harp remains the emotion-save default. Breathing
completion now supplies its own original warm keys asset; see the breathing
README for provenance. The shared player and global mute behavior are unchanged.
