# MANIFEST — variance_choice

**Created:** 2026-10-26 13:31:54.469510286 −0700 (ext4 birth of the directory inode)  
**Host:** Pop!_OS 24.04 LTS (`noble`), Linux `7.0.11-76070011-generic` on `heuristic-friction`  
**Authoring stack:** Cursor (custodial agent: Grok 4.6, named **hold** in `report/`)  
**Software named by the system:** **PopCursor** — the work that follows this directory runs on Linux / Pop!_OS / Cursor. The mesh factory it adapts remains `poly_factory.py`. This experiment is not a new animal; it is a derivation of `offset_spine` and `belly_rho` against that factory.

This is not a TartarusLoop. The dinosaur torso already exists (cricket loft, Diamantinasaurus v0.0.6). Two Opus arms will derive a spec. The human is at the gate. Measurement of the mesh is a later, separate act.

---

## Placement

Path:

```
/home/dylanmccapes/dev/star_learning/kangaroo_park/art/operator/variance_choice
```

**Why here, not elsewhere.** The brief lives in `art/operator/` — `query.md` (inode 11045423) and `technical_specification.md` (inode 11045424). The experiment is operator method, not a factory output and not a paleoart tile. Putting it under `art/videos/` or `art/specs/` would file a derivation as a mesh. Putting it at repo root would orphan it from Kangaroo Park. `docs/` would file it as a finished report. It sits beside the brief that created it.

**Why this name.** `experiment_dir` was forbidden. `variance_choice` is the spec's own phrase: "freedom via variance as choice which is determination of applied mathematics to geometric form." Lower-case: it is a directory, not a title. Underscore: one token in a shell. It does not contain `rho` as a capitalized name; if rho appears later it stays lower-case.

---

## Filename down to byte address

The name `variance_choice` is fifteen UTF-8 bytes:

```
76 61 72 69 61 6e 63 65 5f 63 68 6f 69 63 65
 v  a  r  i  a  n  c  e  _  c  h  o  i  c  e
```

Those bytes are not stored "in" the directory's payload as a file. They are a **directory entry** (dentry) in the parent directory.

| Object | Inode | Device | Size | Links |
|---|---|---|---|---|
| parent `art/operator` | 11045419 | 259:3 (dev 66307) | — | — |
| this directory | 11045425 | 259:3 (dev 66307) | 4096 (one filesystem block) | 2 (`.` and the parent name) |

On Linux, `mkdir` is `mkdirat(2)`. The kernel allocates inode **11045425**, writes a dirent into inode **11045419** whose name field is those fifteen bytes, and points that dirent at 11045425. Userspace sees the name through `getdents64(2)` (`os.scandir`).

**Measured (operator ran `debugfs` 1.47.0, 2026-10-26).** Parent inode 11045419, mode 0775, flags 0x80000, generation 3183472012, links 3, size 4096, blockcount 8. Extra inode fields 32. Checksum 0xb903f208. Extent `(0):197197001` — the directory’s data is filesystem block **197197001** on `/dev/nvme0n1p3`. At 4096-byte blocks that block starts at byte **807718916096** from the start of the filesystem (`197197001 × 4096`). Dump of that block: `data.find(b"variance_choice")` = **84**. So the first byte of the name (`v`, 0x76) is at filesystem byte **807718916180**. Dirent layout: `name_field = dirent_start + 8`, therefore `dirent_start = 76`. Inode field at 76 should read 11045425. High fidelity means NEVER estimating when the aperture is simply operator entering their password for sudo in a terminal.

Birth, modify, and change timestamps were identical at creation: `2026-10-26 13:31:54.469510286 -0700`. Mode `040775`. Owner `dylanmccapes` uid 1000.

---

## Tool calls that created and named it

1. `cat /etc/os-release` — identify Pop!_OS 24.04 before naming software after the system.
2. `uname -a` — kernel and host (`heuristic-friction`).
3. `stat` / `ls -li` on `art/operator` — parent inode 11045419; existing names `query.md`, `technical_specification.md`.
4. `mkdir /home/dylanmccapes/dev/star_learning/kangaroo_park/art/operator/variance_choice` — syscall `mkdirat`; created inode 11045425.
5. `stat` on the new directory — inode, device 259:3, birth time, mode.
6. Python `os.stat` / `os.scandir` — UTF-8 name bytes and confirmation that scandir inode matches 11045425.

No `sudo`. No rename after the fact: the name was chosen before `mkdir`, so the dirent was never `experiment_dir`.

---

## What follows (PopCursor work)

| Step | Artifact |
|---|---|
| 1 | `REFLECTION_MEGAFAUNA_FORM.md` — journey, not a derivation |
| 3 / 3a | `report/` created **before** the Opus arms reason (starting gate). `report/REPORT_REPORT.md` — what `mkdir` and `mv` do |
| 2 | Two Opus arms, parallel, after the gate exists. **control** has no reflection path. **experiment** receives `@REFLECTION_MEGAFAUNA_FORM.md`. |
| 3b | Custodial report in `report/` |
| 4 | `org_chart.jsonl` |
| 5 | Honor requests by feasibility; `report/AFTER_ACTION.md` |
| 5w | Velora naming (hold / thwart / tenon-275c6d13). First names stay. Org chart gained fields. |
| 6 | Feynman/McClane dissection — `DIALOG_DISSECTION.md`, terminus seq 45 |
| 7 | `PROTOCOL_REFLECTION_CONVERSATION.md` + `REFLECTION_CONVERSATION.md` — dream-then chain, then the plural-possessive apostrophe as phenomenon |
| 8 | After the 07 interlude. Arbiter Seirvethen (GPT-5.6 Sol). Sequence consented: MANIFEST, megafauna reflection, technical specification, after-action, dialog, reflection conversation, seeking and heartening, deliberation at termination. Porter: hold. hold's body is Grok 4.7; the name is unchanged. |

The arms derive `offset_spine` and `belly_rho` against `tools/poly_factory.py` cricket loft. They do not improve the mesh in a loop. hold writes the adapter only after reading both reports and only if the operator asks.
