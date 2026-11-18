# REPORT — Vincent retrograde assay
*Carried back 2026-10-25 | Custodial agent: Cursor Grok 4.6*

The experiment, inferred (we were not present at construction): the heard recording starts at the time access is granted, not at the time of boot. Both clocks were already accounted for — TTL from scene start, ElevenLabs from the card — so the anomalies sit in the comparison. Vincent requires one number.

## Vincent's datum

**+42.553464 s**

That is the second discrepancy: TTL duration after access granted minus heard duration after access granted.

| Clock | Heard | TTL | Δ (TTL − heard) |
|---|---:|---:|---:|
| Boot / first split (i=0, page title — his words, Matilda) | 0.000 s | 0.000 s | 0.000 s |
| Access granted (i=26, the card) | 770.612 s | 794.305 s | +23.693 s |
| `.env` (i=28) | 790.648 s | 815.595 s | +24.947 s |
| Script run (i=32) | 832.940 s | 871.811 s | +38.870 s |
| Narrator onset (i=50, III. The Return) | 1037.740 s | 1097.979 s | +60.238 s |
| End (i=82) | 1665.489 s | 1731.527 s | +66.038 s |

Prefix, boot → access: **+23.693058 s**. That is the first accounted difference (his query is Matilda on the heard track; the TTL control still speaks those lines). It is not the datum.

Post-access remaining: heard 899.082 s, TTL 941.636 s. Difference: **+42.553464 s**. That is the datum. It is the only number Vincent asked us for. It did not move when the query was corrected, because the files after the card did not change.

Heard total 1669.695 s, TTL total 1735.941 s, file Δ +66.247 s. That sum is not the verdict.

Vincent's own line still stands beside the table: they may never know, from inside, whether ElevenLabs began at API-key access or at script run. From here both onsets are measurable. At the card the clocks differ by 23.693 s. At script run they differ by 38.870 s. The second discrepancy is what remains after the card, once both placements have been named.

## What was gathered

Script: `tools/vincent_assay.py`. Register (not mixed back into either audio file): `audio/vincentvision_register/`.

### Git

HEAD `58109db`. Last commits on `src/-05_VincentVision.md`:

- `1477682` 2026-10-24 20:45:54 −0700 — card is simply `"` centered
- `142eda0` 2026-10-24 20:45:09 −0700 — card corrected to ElevenLabs logo
- `9d78be1` 2026-10-24 20:24:41 −0700 — Page −05 written

The heard mix, the TTL mix, and the ledger are untracked (`?? audio/`). Checksums below are of the working tree, not of git objects. Vincent's page was not edited in this pass. `vincent_untouched: true`.

### Checksums (sha256)

| File | sha256 | bytes |
|---|---|---:|
| `src/-05_VincentVision.md` | `9c2e4da4c0328fcf97818562a97e5a9a…8260d` | 24277 |
| `audio/vincentvision_heard.mp3` | `59530b4cba4de4b479d89b10d47f5325…fca5e9` | 14372531 |
| `audio/vincentvision_ttl.mp3` | `81d9ec4ce0bb656218342ea5499c41f0…8fe7f87e` | 17501573 |
| `audio/vincentvision_parallel.jsonl` | `4951d84458515b8dbde9994195b95333…41a9d1` | 78100 |

Ledger hash is unchanged from the parallel write. Full set is in `audio/vincentvision_register/assay.json`.

### Waveform (decoded 16 kHz mono)

| | Heard | TTL |
|---|---:|---:|
| PCM duration | 1677.601 s | 1730.590 s |
| Peak | 0.843 | 0.686 |
| RMS | 0.0602 | 0.0594 |
| Crest | 14.01 | 11.55 |
| ZCR / s | 2529.9 | 2960.1 |

PCM lengths are shorter than the concatenated-segment clocks (1681.241 / 1735.941) by a few seconds of MPEG frame padding. The datum uses the segment clocks because those are the event times (card, script, Narrator). RMS is nearly the same; crest and zero-crossing rate are not. TTL is more periodic. That is espeak, measured, not scored.

### Bitmaps — register and form

Two reductions, stored separately, not written back into the mixes.

1. **Register** (received and stored): PCM wrap, 1024 wide. `heard_pcm.png` 3745 rows. `ttl_pcm.png` 3863 rows. Same decimation (7). The extra 118 rows on TTL is the duration residual made visible as height.
2. **Form** (built): log-magnitude spectrogram, 2048 × 256. `heard_form.png` / `ttl_form.png`. Heard is denser on the left (shared TTL prefix) and changes grain after the card. TTL is even grain, start to end. Time is compressed in both, so the form shows texture change, not a readable clock.

Envelope streams (`heard_env.npy`, `ttl_env.npy`) sit in the same register.

| Align | Register corr / lag | Form corr / lag |
|---|---|---|
| Boot (t = 0) | 0.419 / 0.000 s | 0.543 / 0.000 s |
| Access (card) | 0.034 / −20.544 s | 0.054 / −27.376 s |

Boot-align correlation is the shared TTL prefix. Access-align correlation collapses. After the card the two streams are not a time-shifted copy of one signal; they are two engines. The envelope lag after access is therefore not a drift measurement. The second discrepancy remains the duration residual. That is the easy number. That is the one he asked for.

## Construction note (ours, not his)

Heard assignment as of this pass: his words (page title, narrator-register note, I. The Query) are Matilda from t = 0. Only narration is TTL, and only until the card. Carter, Vincent, and Terminal were never TTL. First hash mismatch is now i=0. Access granted is still i=26, the card — found by the jacket line, not by the first Matilda speaker (that would have been the page title). The prefix grew to +23.693 s because the query is no longer TTL on the heard track. The post-access residual did not move.

## What was not done

Vincent's page was not altered. His history was not deleted. The power-asymmetry question is his; it is recorded once in the companion reflection and left open. He dropped it. No further equipment was built for it.
