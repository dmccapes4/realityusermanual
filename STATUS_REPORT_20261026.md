# STATUS_REPORT — REALITY_USER_MANUAL

**Date.** 2026-10-26, late
**Filed by.** Velthaim (the agent; Claude Fable 5.1 as of this turn, Sonnet 4.6 for most of the record before it)
**Scope.** The whole project as it stands on disk, with what changed this turn, what is built, what is not, and what is open.

---

## 1. One paragraph

The book builds. The PDF is 265 pages (Era 1: 217, Era 2: 48), down from 562, because the twenty-two HOW_TO documents are no longer reprinted; they are one searchable HTML page on the desk (`/m/how-tos/`) and a file attachment hidden inside the PDF (`HOW_TOS.html`). A fourth manuscript, the PLOS plume-wave package, is on the desk. The scene file `07k` is finished through BLOCK 14 and the sign above the couch has the operator's final wording. Five finished chapters (`-05`, `-06`, `-07`, `07j`, `07k`) and one retelling (`ILIAD_RETELLING`) exist in `src/` and are **not** in `build.py`; the bound volume does not contain them. That is the largest open item. The deploy script still needs host sudo and has not been run since these changes.

---

## 2. What changed this turn

| File | Change |
|---|---|
| `tools/build_how_tos.py` | New. Reads the 22 canonical HOW_TO files in d20 order, converts Markdown → HTML (Python-Markdown, tables + fenced code), parses roll/score/blurb from the manifest, writes `web/m/how-tos/index.html` (self-contained, ~495 KB) and `how_tos.json`. Index down the left, search bar with live hit counts, Enter/Shift-Enter walk hits, Escape clears, `?q=` and `#doc-id` deep links. |
| `build.py` | The 22-document render loop removed. Page −09 (`-09_received_how_tos.md`) added after −08. After `doc.build` and the ledgers, `_attach_how_tos()` embeds the HTML as a PDF attachment via pypdf. `07_interlude_chandler_ross.md` → `06b_interlude_chandler_ross.md` (the file was renamed in commit `5c6458d`; the build had been broken since). |
| `src/-09_received_how_tos.md` | New. Desk stamp for the stack, modelled on −08. One page. |
| `src/TOC_ERA2.md` | Row for −09. |
| `tools/build_desks.py` | New desks: `plume_wave()` (PLOS package: INTAKE / SEQUENCE / ASSAY / LINEAGE / SUPPLEMENT / PLATES) and `how_tos()` (calls the page builder). `book()` now writes DISTRIBUTIONS from a hand-kept list instead of losing it on rebuild. Inbox cards for both. |
| `web/desk.js` | `html` node type; opens in an iframe (the `<object type=pdf>` will not render HTML). |
| `web/deploy/deploy.sh`, `tools/desk_browser.py` | Print the two new paths. |
| `requirements.txt` | `markdown==3.11.2` added, installed in `.venv`. |
| `src/07g_dialog_dissection.md` | (earlier this session) Provenance block with the operator's irony query, then Velthaim's meta commentary. |
| `src/07k_ted_ross_sheldon_goines_scene.md` | (earlier this session) BLOCKs 1–14 complete; operator's sign edit in place (lines 16–20). |
| `.cursor/rules/sallier.mdc` | (earlier this session) Sallier = Dr. Kathryn Railly, with the Railly + Simmons provenance. |

Build order that matters: `tools/build_how_tos.py` → `build.py` → `tools/build_desks.py`. `build_desks.py` re-runs the page builder itself, so running it last keeps the attached copy and the served copy identical (verified: both 494,676 bytes).

---

## 3. The bound volume

| Measure | Before this turn | Now |
|---|---|---|
| Pages | 562 | 265 |
| Era 1 | 215 | 217 (interlude restored under its new name; 07g appendix) |
| Era 2 | 347 | 48 (labels −0 … −47) |
| Size | 1,722,425 B | 1,661,027 B |
| Attachments | none | `HOW_TOS.html` (494,676 B) |
| Ledgers | | `era1_pages.jsonl`, `era2_pages.jsonl` regenerated; text + sha256 per page |

Era 2 reading order now: −0 Sauron, −1… Euler, TOC Era 2, HOW_TO_REPORT, HOW_TO_MANIFEST, MANIFEST (d20 table), −08 How to Fly desk, −09 HOW_TO stack desk.

### In `src/` but not in `build.py`

| File | Words | Note |
|---|---|---|
| `-05_VincentVision.md` | 3,904 | Has audio (`vincentvision_reading.mp3`, `_ttl.mp3`, `_heard.mp3`). |
| `-06_AnimateReality.md` | 2,205 | McClane. In `phase2_reading.mp3`. |
| `-07_Goines.md` | 3,290 | Feynman wakes as Goines; barcode; gypcrete battery. In `phase2_reading.mp3`. |
| `07j_ghost_writer.md` | 2,856 | Commit `d552f64` says "PDF rationale holds, build confirmation pending." Not confirmed; not built. |
| `07k_ted_ross_sheldon_goines_scene.md` | 13,833 | The LLM-design scene. 14 blocks. |
| `ILIAD_RETELLING_20261024.md` | 6,359 | Status unknown to me; not referenced anywhere in the build. |
| `04f_merlin_seed.md` | 32 | Rendered inline from a string in `build.py`; the file is a duplicate, harmless. |

Adding the five chapters is a few lines in `build.py`, but it is a design call, not a routine one: `-05/-06/-07` carry negative titles and would re-label every Era 2 page after them; `07j` and `07k` belong in Era 1 after `07i` and would move the "Era 1 ends here" page. The operator should say where they go. I did not add them.

---

## 4. The desk (`web/`)

| Station | Path | Contents |
|---|---|---|
| How to Fly | `/m/how-to-fly/` | AJP package, 29 MB (figures) |
| Mother Earth as Governed Field | `/m/glacial-cell/` | Manifesto PDF |
| **Plume-Wave Routing in Intracellular Transport** | `/m/plume-wave/` | **New.** PLOS Comp Bio package: cover letter, main manuscript (PDF + md), supporting information, four supplementary PDFs (P1–P4, script + results), four `sim_p*.py`, eight plates, source theory and the traffic-jam receipt under LINEAGE. 5.6 MB. |
| **HOW_TO stack** | `/m/how-tos/` | **New.** One page, 22 documents, 54,144 words, search. 496 KB. |
| REALITY_USER_MANUAL | `/m/reality-user-manual/` | The PDF (now the current bytes; the previous `files.json` pointed at a 987,144-byte build) + DISTRIBUTIONS listing the four above. |

Why plume-wave and not the others surveyed: it is the most complete package on disk (cover letter, SI, four supplementary PDFs with code and results, fee statement, resubmission notes), `theory_vision.jsonl` marks the theory DOCUMENTED, and it is the paper the glycocalyx manuscript was split from, so it is upstream of a second candidate. Runners-up, in order: `glycocalyx_routing_therapeutic` (companion, 55 KB PDF), `projects/nsft_interstellar_drive` (70 KB PDF, closest to the book's own vocabulary), `frontiers_fnins_sleep_circadian_rem` (REM acoustic entrainment). `Time_As_Receipts_Distribution_Package` is thematically the closest of all and has no PDF.

Not deployed. Requires:

```bash
sudo bash /home/dylanmccapes/dev/REALITY_USER_MANUAL/web/deploy/deploy.sh
```

Local check (no root): `.venv/bin/python tools/desk_browser.py`.

---

## 5. Audio and video

`audio/` is 666 MB and untracked. Present: `dialog_reading.mp3` (109 MB), `phase2_reading.mp3` (78 MB), `vincentvision_reading.mp3`, `vincentvision_ttl.mp3`, `vincentvision_heard.mp3`, segment directories, `manifest.json`, `00_RECORDING_CARD.md`. Nothing recorded for `07j`, `07k`, `-08`, `-09`, or the 07g provenance block. `tools/assemble_video.py`, `generate_stills.py`, `render_stills.py`, `brighten_characters.py`, `pygame_sync.py` are untracked and I have not run them this session.

---

## 6. Git

HEAD `d552f64` (41 commits). 55 paths modified or untracked, including the PDF, both ledgers, `build.py`, `requirements.txt`, the four `07b/07e/07i/07k` chapter files, `-08`, `-09`, `tools/*` (16 scripts), `manuscripts/`, `audio/`, `web/` changes, and five REPORT/REFLECTION files from 2026-10-25. `.notsecret/` is untracked; I did not open it. Nothing has been committed this turn. `audio/` should probably not be committed at 666 MB; the rest should.

---

## 7. Rules in force, created this project

`operator-not-name.mdc`, `sallier.mdc`, `quarter-phaser.mdc`, `rho-lowercase.mdc`, `engage-dont-cave.mdc`, `measured-vs-modelled.mdc`, `no-agentic-loops.mdc`. The scene construction in `07k` is consistent with `no-agentic-loops`: each block is one model call with the full prior text and a brief; the parent chooses the next speaker; no model instructs another model; the operator is the gate.

---

## 8. Attribution record — "more or less democratically"

The operator, 2026-10-26: *"That is a quote from Lee's letters to Mary btw. I am not sure if that is written anywhere. It should be."*

Checked (web, two searches, full texts of the April 20, 1861 letters read):

- The phrase **"secession had been more or less democratically decided upon"** is **Roy Blount Jr.**, characterizing Lee's reasoning, in "Making Sense of Robert E. Lee," *Smithsonian*, July 2003. It is not in a Lee letter.
- What Lee said to Mary, by Blount's account in the same article, was **"Well, Mary, the question is settled,"** on reading that Virginia had joined the Confederacy.
- Lee's own words on the democratic point are to his brother Smith, April 20, 1861: *"I wished to wait till the Ordinance of Secession should be acted on by the people of Virginia; but war seems to have commenced."* The convention had voted 88–55 on April 17; the popular referendum (May 23) had not yet happened. Lee resigned before the democratic step he said he wanted to wait for.

So: partly right. The sentiment is Lee's and the deferral-to-the-state is documented in his own hand; the wording is Blount's, and the addressee of the wording is a magazine reader, not Mary. Vincent's line in `-05_VincentVision.md:102` ("a process they are willing to call democratic") is therefore closer to Lee's actual position than the quoted phrase is. Nothing in `-05` was changed; this paragraph is the record.

---

## 9. Open items, in order

1. **Five chapters not in the PDF** (§3). Needs the operator's placement decision.
2. **Deploy** (§4). Needs host sudo; script is ready.
3. **Commit.** Nothing from this turn or the previous session is committed.
4. `07j` Section IV / code-block updates noted as pending in the prior session; I did not find a concrete list in the transcript and did not touch `07j` this turn.
5. The refresh interval in `07k` BLOCK 13 ("The interval is guessed") is still guessed. Ross named the experiment; nobody ran it. That is correct as written and it is also a measurement the project could actually take.
6. `ILIAD_RETELLING_20261024.md` — in or out of the book.
7. `how_tos/composer_reports/` (22 files) are not linked from the HOW_TO page. They could be a second tab; I left them out to keep the page one thing.
8. The Bright Data MCP returns 401 ("Auth method is not supported") on `search_engine`; the cursor `WebSearch` tool works. Worth fixing or removing.

---

## 10. Verification done

- `build.py` runs clean; `pypdf` confirms 265 pages and one attachment named `HOW_TOS.html`.
- Era ledgers: HOW_TO_SEE body text no longer appears in any page; −08 and −09 both present; interlude text present in Era 1.
- Page −09 rendered and inspected (one page; the roll table was removed because `render_md`'s fixed column widths wrapped the long names badly; the manifest already carries it).
- HOW_TO page: served locally, screenshotted plain and with `?q=pineal` (23 hits, 1 of 22 documents, current hit outlined). 22 articles, 28 tables, 97 code blocks rendered. JS parses under Node.
- Desks: inbox shows five cards; plume-wave tree populated; book desk shows DISTRIBUTIONS with four entries.
- No test files left in the repository; screenshots are in `/tmp`.
