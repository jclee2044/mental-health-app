# Recorded breathing cues

Source: **relaxing-breath-inhale-exhale.wav** by **beerre**, March 1, 2022.

- Creator page: https://freesound.org/people/beerre/sounds/622601/
- License: **CC0 1.0 Universal**, https://creativecommons.org/publicdomain/zero/1.0/
- Downloaded October 21, 2026 from the public HQ MP3 preview: https://cdn.freesound.org/previews/622/622601_2967993-hq.mp3
- The user auditioned this recording and selected it over the second candidate.

These files are adaptations of the human recording. **Inhale: 7.00–10.00s**, explicitly identified by the user after listening. **Exhale: 25.35–28.90s**, one of the clips the user confirmed as an exhale. The other candidate, 12.50–15.60s, was also confirmed as an exhale and is not used for inhale. User listening feedback establishes these phase labels; the agent has not independently heard the clips.

Preparation: macOS's built-in `afconvert -f WAVE -d LEI16 <preview.mp3> <review.wav>`, then `backend/.venv/bin/python frontend/src/features/breathing/assets/prepare.py <review.wav>` from the repository root. The script uses Python's standard library and retains the source stereo samples/level with 10ms source-edge fades. At the user's request, the inhale uses a 36 kHz sample clock for the original 48 kHz samples: 75% speed, three seconds becoming four seconds, with a slightly lower pitch and no added silence. This is ordinary slowdown, not granular/overlap-add stretching. The exhale uses a 34.08 kHz clock (71% speed): its 3.55s source cut becomes 5s, followed by 1s of silence to complete the six-second phase. Both slowdowns lower pitch slightly. AAC encoding resamples the slowed signal to standard 48 kHz with built-in `afconvert -f m4af -d aac@48000 -b 96000 <phase.wav> <phase.m4a>`; this preserves the prepared four/six-second phase durations. Web Audio uses a 0.65 gain and short click-prevention fades, including on resume.

Revised approach: the first implementation stretched 80ms recorded grains with overlap-add to fill each phase. The user reported a weird sound, and this processing was removed. The initial cuts also wrongly used the opening noise; user feedback first directed the waveform scan after 10s, then specifically identified the inhale at 7–10s. The final cuts follow those listening identifications. Waveform analysis and later cuts (both subsequently confirmed as exhales) are recorded under `docs/evidence/audio-previews/waveform-analysis.json` and `.svg`. The agent cannot hear browser playback in this environment. Waveform analysis and technical playback checks cannot establish phase identity, smoothness or subjective sound quality. User listening review remains the source of those judgments.

The AAC clips are imported inline into the production JS bundle, which the existing service worker caches. No external requests, microphone, speech model or new dependency are needed during an exercise. The full audition recordings under docs are not part of the application bundle. Credit is retained for provenance despite CC0 not requiring attribution. No Headspace audio was copied.
