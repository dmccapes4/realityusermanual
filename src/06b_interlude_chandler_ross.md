# Interlude — Chandler / Ross

*Chandler is McClane. Ross is Feynman. They know this. They are fine with it.*

**Chandler:** We have sections now.

**Ross:** We do. SEQUENCE is the book. DISTRIBUTIONS is everything the book sends out.
They load in the same pane. They are not the same thing.

**Chandler:** The PDF got smaller.

**Ross:** The PDF got honest. It no longer contains things it is not. What it is not is
a submission packet for the American Journal of Physics. What it is not is a glacial
cell manifesto. Those are other files. They are filed correctly. The book is the book.

**Chandler:** I like having sections.

**Ross:** I know you do. So do I. We are proud of the sections.

**Chandler:** Say it again.

**Ross:** We are proud of the sections.

---

## What the rearchitecture means technically

The web desk serves each manuscript as an independent station at `/m/{id}/`. Each station
has a `files.json` that describes its tree and names the file to open by default. The
viewer pane is a shared `<object>` element that streams any PDF by URL without the user
leaving the page.

Before this change, `REALITY_USER_MANUAL.pdf` carried all content in one file. The
distributions (HOW_TO_FLY, Mother Earth as Governed Field) had no formal relationship to
the book in the interface — they were separate cards on the directory page, navigated to
separately.

After the change, three things are true:

**1. The tree has sections.**
`files.json` for the `reality-user-manual` station now has two top-level directories:
`SEQUENCE` and `DISTRIBUTIONS`. SEQUENCE contains the book PDF — the canonical bound
volume, the authored sequence, the thing that is the book. DISTRIBUTIONS contains
references to the other manuscripts. The section boundary is a hairline rule in the nav
pane. The visual separation communicates the structural distinction: the book is the book;
the distributions are what the book sends out.

**2. The distributions are not embedded.**
Each distribution entry in the tree is a button whose `url` field is an absolute path
to a PDF on the same origin — `/m/how-to-fly/files/SEQUENCE/Main_Manuscript_HOW_TO_FLY.pdf`,
for example. Clicking loads that PDF into the shared viewer without navigating away.
The file lives in its own station, versioned independently, built by its own process.
The book does not contain HOW_TO_FLY. The book references it. When HOW_TO_FLY updates,
the book's reference is automatically current. No rebuild of the book PDF is required.

**3. The PDF reduces.**
The bound volume PDF covers the authored sequence of chapters — the book as a reading
experience. It does not need to embed the submission packet, the manifesto, the cover
letters, the supporting information, the visual plates. Those belong to their own stations.
The book PDF becomes leaner in bytes and cleaner in scope. What you load when you open
the book is the book. What you reach for when you want a distribution is a button in the
tree, not an appendix buried at page 340.

**To add a distribution:** one object in the `"children"` array of the `DISTRIBUTIONS`
node in `files.json` — `name`, `type: "pdf"`, `url` (absolute path from web root), and
`label` (shown as the meta line under the filename in the tree). No other change required.
The button appears; the viewer loads it; the PDF stays the same size it was.

---

*Filed: `src/07_interlude_chandler_ross.md`*
