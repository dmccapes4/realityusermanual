# Strategy — coda.c Narration Script
*Filed: 2026-11-02.*

## The problem

`truth/coda.c` contains 611 lines of C. The code is correct and should appear on the page as code. But ElevenLabs cannot narrate C — it produces gibberish on `uint64_t`, `fseek`, `>>`, `NO_NEXT`, and everything else that is syntax rather than English.

The narration script is a prose translation of the code, spoken by the Narrator, placed in the page adjacent to the code block so the reader/listener gets both.

---

## Source hierarchy

Three layers are already in the code:

1. **Danish 1648 comments** — the law. Structural meaning of each section.
2. **English `puts(">> ...")` statements** — what the system reports at runtime. These are the skeleton of the narration script.
3. **The C code itself** — the precise operations. The narration expands on the puts statements using the code as ground truth.

**Rule**: when the puts statement is sufficient, use it. When the C code adds precision the puts statement elides, name the operation. Never add meaning that is not in the code.

---

## Translation rules

| C construct | Narration form |
|---|---|
| Function name | Role description. "the rotation" not "rotate_address_space" |
| Variable name | Role description. "the new head address" not "new_a_head" |
| `uint64_t` | "an eight-byte file offset" or just "the offset" |
| `NO_NEXT` / `UINT64_MAX` | "the sentinel value" |
| `fseek` / `fread` / `fwrite` | "read" / "write" — location implicit |
| `unlink` | "the directory entry is removed" |
| `execv` | "this process image is replaced with the new binary" |
| `sleep(1)` | "one second passes" |
| `system(CC_CMD)` | "the source is recompiled" |
| `for (int i = 0; i < N; i++)` | "for each of the N positions" |
| `while (filled[j])` | "if the slot is occupied, advance to the next free slot" |
| `cos30`, `sin30` | "cosine thirty" / "sine thirty" |
| Struct field | Named by role. `s.iteration` → "the iteration count" |
| `printf` / `log_line` | The content of the log entry, named |
| `#include`, `#define` constants | Stated as facts when relevant: "nine bytes per node" |
| Type assertions / casts | Ignored unless semantically significant |

---

## Structure

Follow the execution order of `main()` with helper functions narrated inline at the call site — not as separate sections.

```
init()              → narrated only if first run (step 0 triggers it)
step 0  — first run check
step 1  — read secrets
step 2  — flip coin, log, write back
step 3  — traverse A
step 4  — rotate A (includes full rotation narration inline)
step 5  — carry new A head, re-traverse
step 6  — B follows A (rotation narrated by reference to step 4)
step 7  — presence check A-in-B (includes full check narration inline)
step 8  — presence check B-in-A (by reference to step 7)
step 9  — log result
        → discrepancy exit (conditional — narrated as a branch)
step 10 — delete, recompile
step 11 — sleep
step 12 — exec new binary
```

---

## Format in the page

The narration script appears in `-09.md` as italic Narrator lines (`*...*`), one paragraph per step or logical block. It is placed **between the closing `"""` of the code block and the `---` separator before the scene**, so:

```
[tombstone]
---
[code block inside """ and ```]
"""
---
[narration script — italic Narrator lines]
---
[scene — Happy, Stamper, Carter dialogue]
```

The parser (`parse_minus09`) uses the content after the first `---` that follows the code block. The narration and scene are in the same parsed section, separated by nothing but a blank line — the parser handles both transparently.

---

## What the narration is not

- Not a summary. Every step named in the code is named in the narration.
- Not an interpretation. The narration states what the code does, not what it means. Meaning is in the scene.
- Not simplified. The matrix terms are named. The skip list is described. The sentinel value is named.
- Not moralizing. The Narrator reads the code. The Narrator does not editorialize.
