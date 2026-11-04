# Postmortem: build_minus30_video.py — Two Implementation Failures
**Date:** 2026-11-03  
**File:** `tools/build_minus30_video.py`

---

## I. Character Presence / Narrator Competing

### What was implemented

`draw_scene()` returned a `rname` from the current cue's `speaker` field each frame. When the speaker was `Auden`, it returned `None`. The right-side character image was set to `None` on every Auden cue. This caused the character image to disappear each time Auden narrated between lines of dialog, then reappear when the character spoke again: a blink on every narrator turn.

The logic treated narration as a competing presence: Auden narrating = right panel clears.

### Why that was wrong

A character does not stop existing when the narrator speaks about them. The narrator's presence does not revoke the character's presence. The logic modelled a mutually exclusive broadcast slot (one speaker owns the panel) rather than persistence (the last character present stays present until a different character takes over).

### What the user said

> "When a character speaks he does not blink because the narrator pretends his presence matters. It is easier to *not* have the character blink. It is more logical."

Then, after continued blinking:

> "If the way the script works is based on narrator competing for presence (which makes it way more complicated and terrible) then delete it and write a new one. You would be done. You aren't. I suffer."

### What was done in response

The script was deleted and rewritten. The new architecture precomputes a right-side timeline once at startup via `build_right_timeline(cues)`. It scans all 161 cues in order, tracking the last non-Auden character (or description-override character). It emits a breakpoint only when the character *changes*. `draw_frame()` looks up `right_char(timeline, audio_t)` — a simple binary search — and blits that character. Auden cues are not evaluated in `draw_frame()` at all. The right panel holds its last character through every narrator segment until a different character appears.

---

## II. Screenshots and Poem at End

### What was implemented

**Screenshot boundaries (PHASES):**
```python
(575.0,  710.0,  "screenshot_1"),
(710.0,  764.4,  "screenshot_2"),
```
The boundary at 710.0 cue-time was an estimate from the prior session, set without reading the screenshot images or the cue timestamps.

**End poem:**
```python
(793.0,  797.0,  "book_photo"),
```
Four seconds of book photo, starting at an estimated timestamp. Frame exporter tail was `mp3_dur + 4.0`.

### Why that was wrong

The 710.0 boundary was not derived from the content. The correct switch point is the moment Auden narrates "— Gentle fetters = appropriate constraint. Not contradiction. ✓" — the derivation note for the poem line "Are in vain, and thy gentle fetters." This is cue [140], which begins at **659.5s** cue-time. The boundary was therefore 50.5 seconds late: screenshot_2 appeared 50 seconds after its content began.

The 4-second end poem was insufficient and started at a guessed timestamp (793.0) rather than at the actual final click cue.

### What the user said

> "The last screenshot does not appear when it is supposed to. Read the words on the images so you get it correct. I should not have to explain that process… 'Vain' is the switch. I intended that. I have it highlighted."

> "Have the poem stay up at the end too. Ten seconds. That is what I meant by 'have the poem stay up at the end'. I did not think the number of seconds mattered. Just the presence of the photo after the click."

### What was done in response

Both screenshot images were read. Screenshot_1 ends at the poem line annotation for "Are in vain." Screenshot_2 opens with that annotation highlighted. The boundary was moved to **659.5** (cue [140] start: `— Gentle fetters = appropriate constraint. Not contradiction. ✓`), which is the first cue that processes the "vain" line.

Screenshot_1 start was moved from 575.0 to **572.3** to open at the actual cue where Auden sets down his notebook ("I set down my notebook. I pick it up again." — cue [130]).

The final LIGHT_EVENTS ON event was corrected from the estimated 789.8 to **787.1** — the actual start of cue [160] "click." (the last segment in the file).

The book_photo phase was set to **(787.1, 800.0)** — opening exactly at the final click and running 12.5s in cue-time (≈12.4s audio), well past the MP3 end.

The frame exporter tail was changed from `+4.0` to **`+10.0`** seconds, so frames are exported for 10 seconds after the MP3 duration, rendering the full book_photo window.

---

## Root cause in both cases

Neither fix required guessing. The character-persistence rule is stated in the design spec. The screenshot boundary required reading the two image files. Both failures were caused by implementing from assumption rather than from the available reference.
