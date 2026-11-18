# How to Provide Options

**Status:** Foundational  
**Audience:** Operators, designers, system builders  
**Tone:** Boring, legible, non-performative  
**Scope:** UX as responsibility, not persuasion

---

## Opening Recognition

**UX is the face of performance in software.**

That's accurate. It's not always correct.

That distinction matters.

---

## The Distinction: Performance vs. Legibility

**Performance (in UX):**
- Looks smooth
- Feels effortless
- Appears simple
- Optimizes for appearance
- Success measured by aesthetics, engagement, conversion

**Legibility (in UX):**
- Makes state visible
- Shows real constraints
- Admits complexity
- Optimizes for clarity
- Success measured by operator understanding

**Performance UX can be accurate** (looks good, users like it).  
**Legibility UX aims to be correct** (reflects actual system state, honest about constraints).

**The distinction is sometimes thought of as success criteria.**  
**The incorrect way.**

---

## Why This Matters

**When UX success = performance:**
- System optimizes for appearance
- Hides complexity to look simple
- Nudges behavior to increase engagement
- Metrics: clicks, conversion, time-on-site

**This creates hostile UX.**

**When UX success = legibility:**
- System optimizes for clarity
- Shows complexity honestly
- Provides options without pressure
- Metrics: operator understanding, mistake correction, trust accumulation

**This creates operable UX.**

---

## Purpose

This document describes how options should be provided in systems designed for sovereign operators.

**It does not describe:**
- How to convince users
- How to drive engagement
- How to optimize conversion
- How to guide behavior

**It describes:**
- How to reduce hostility by making action obvious without removing agency

---

## Core Principle

**Providing options is not about choice.**  
**It is about clarity.**

Poorly provided options increase entropy.  
Well-provided options reduce entropy without collapsing freedom.

---

## Definition: An Option

An option is:
- A real action the operator can take
- That the system is prepared to support
- With consequences that are honest and legible
- Presented without pressure, ranking, or recommendation

**If an action is not safe, supported, or honest, it is not an option and should not be presented.**

---

## What Providing Options Is NOT

Providing options is not:
- Suggesting what the operator should do
- Nudging behavior
- Hiding consequences
- Collapsing complexity into false simplicity
- Framing one choice as morally or socially superior
- Forcing urgency
- Optimizing for speed over correctness

**Any of the above is hostile UX.**

---

## The Operator Assumption

This approach assumes:
- The operator is competent or learning
- The operator is acting in good faith
- The operator wants to understand what is happening
- The operator can tolerate uncertainty

**If the system does not trust the operator, it must not pretend to.**

---

## The Three Obligations When Providing Options

### 1. Disclosure

The system must disclose:
- What options exist
- What state the system is currently in
- What constraints are active
- What uncertainty remains

**No disclosure → no valid options.**

---

### 2. Non-Prescription

The system must not:
- Recommend
- Rank
- Color-code for preference
- Animate urgency
- Imply correctness

**The moment the system prefers, it is no longer providing options — it is steering.**

---

### 3. Reversibility (When Possible)

Where feasible:
- Options should be reversible
- Irreversibility should be explicit
- Irreversibility should require deliberate action

**Surprise irreversibility is hostile.**

---

## Option Presentation Rules

### Rule 1: Fewer Options Is Not Always Better

Reducing options to "simplify UX" often:
- Hides real constraints
- Forces premature decisions
- Creates false certainty

**Clarity beats minimalism.**

**Example from PortalVision:**

When duplicate artifact detected, system presents three options:
1. Proceed with ingestion (cycles might occur, resolved later)
2. Decay one of the existing artifacts (reversible, logged)
3. Abort ingestion (rethink artifact)

**Performance UX would:**
- Reduce to "Proceed" or "Cancel" (hiding complexity)
- Auto-select "best" option (removing agency)
- Recommend one option (steering behavior)

**Legible UX does:**
- Shows all real options
- Explains consequences honestly
- Lets operator decide with full context

**Clarity > simplicity.**

---

### Rule 2: Silence Is an Option

It is valid to:
- Present state without options
- Indicate "no safe action available"
- Encourage pause

**This is not failure.**  
**This is honest UX.**

**Example:**

System state is undefined or verification incomplete.

**Performance UX would:**
- Show "Please wait..." with spinner (hiding uncertainty)
- Enable buttons anyway (pretending ready)
- Guess at safe action (risk without consent)

**Legible UX does:**
- "System state: undefined. No safe actions available. Verification in progress."
- No buttons (no fake affordance)
- Honest about uncertainty

**Silence when appropriate > fake action.**

---

### Rule 3: Refusal Is Normal

If an option is not currently safe:
- The system should refuse quietly
- Explain why
- Preserve dignity

**Refusal is not punishment.**  
**Refusal is constraint disclosure.**

**Example from PortalVision:**

Operator attempts ingestion without declaring authorship context (INV-014 violation).

**Performance UX would:**
- Red error message ("ERROR: Missing field!")
- Shake animation (punishment aesthetic)
- Block without explanation (hostility)

**Legible UX does:**
- "INV-014: Authorship context declaration required."
- Explain what's needed and why
- Preserve operator dignity
- Make next action obvious

**Refusal with clarity > refusal with shame.**

---

## Visual Language (High Level)

Options should be:
- Visually neutral
- Evenly weighted
- Non-urgent by default
- Accessible without hierarchy

**Color, motion, or emphasis should indicate state, not preference.**

**Example:**

**Performance UX:**
- Green "Recommended" button (steering)
- Gray "Not Recommended" button (discouragement)
- Red "Dangerous" button (fear)

**Legible UX:**
- Neutral buttons for all options
- Text explains consequences
- Color (if used) indicates system state, not judgment
  - Blue: Information available
  - Yellow: Uncertainty present
  - Red: Irreversible action
  - Not: Good/bad/recommended

**State indication ≠ preference indication.**

---

## Temporal Respect

Options should respect time:
- No artificial countdowns
- No false urgency
- No pressure to act "now"

**Urgency must come from reality, not UI.**

**Example:**

**Performance UX:**
- "Last chance! Only 3 seats left!"
- Countdown timer (artificial urgency)
- "Act now before it's too late!"

**Legible UX:**
- If there's genuine urgency, state it factually
- "This server will reboot in 2 minutes. Current operations will be interrupted."
- If there's no urgency, don't create it

**Real constraints only.**

---

## When NOT to Provide Options

Do not provide options when:
- The system state is undefined
- Consequences cannot be explained
- The operator lacks necessary context
- The action would be unsafe or dishonest

**In these cases, provide information only.**

**Example from PortalVision:**

Chat graph not loaded (mandatory component missing).

**Wrong:**
- Show interface anyway
- Present options that won't work
- Let operator fail mysteriously

**Right:**
- "Chat graph not loaded. This is required. System cannot operate."
- No fake options
- Clear path to resolution if available

**No options > fake options.**

---

## Relationship to Integrity

**Providing options is an ethical act.**

If you:
- **Hide options** → you remove agency
- **Add fake options** → you deceive
- **Bias options** → you coerce
- **Overwhelm options** → you abandon responsibility

**The goal is not choice.**  
**The goal is operable clarity.**

---

## Performance vs. Legibility in Practice

### Scenario: User Wants to Delete Account

**Performance UX:**
1. Hide the option (reduce churn)
2. Make it hard to find (dark pattern)
3. Ask "Are you sure?" multiple times (annoyance as deterrent)
4. Offer discount to stay (change behavior)
5. "We'll miss you!" (emotional manipulation)

**Success metric:** Reduced deletion rate

**Legible UX:**
1. Make option visible (respect agency)
2. Explain consequences honestly ("Your data will be deleted. This is irreversible after 30 days.")
3. Ask once for confirmation (deliberate action)
4. No persuasion attempt
5. "Deletion scheduled. You have 30 days to reverse this."

**Success metric:** Operator understood consequences and made informed choice

---

### Scenario: Duplicate Artifact Detected

**Performance UX:**
1. Auto-merge duplicates (remove choice)
2. Silently skip duplicate (hide problem)
3. Show error and block (hostility)
4. Recommend one action (steering)

**Success metric:** Smooth ingestion flow

**Legible UX:**
1. Pause ingestion
2. Show match report (semantic + lexical scores)
3. Present three honest options with consequences
4. Let operator decide
5. Log decision with reason

**Success metric:** Operator made informed choice with full context

---

### Scenario: System Uncertainty

**Performance UX:**
1. Hide uncertainty (appear confident)
2. Show progress bar (fake precision)
3. Guess at outcome (over-promise)
4. Proceed anyway (risk without disclosure)

**Success metric:** Appears reliable

**Legible UX:**
1. Disclose uncertainty honestly
2. "System state: processing. Outcome uncertain. Estimated: 30-120 seconds."
3. No fake progress (spinner only if helpful)
4. No action until safe
5. Explain when ready

**Success metric:** Operator knew what to expect, no surprises

---

## UX as Success Criteria (The Incorrect Way)

**Common mistake:**

"Good UX" defined as:
- Smooth (no friction)
- Fast (no waiting)
- Simple (no complexity)
- Engaging (time on site)
- Converting (desired behavior achieved)

**This optimizes for performance, not correctness.**

**Result:**
- System hides real complexity
- Operator lacks context for decisions
- Mistakes not caught until too late
- Trust erodes quietly

**Alternative:**

"Good UX" defined as:
- Clear (state visible)
- Honest (constraints disclosed)
- Operable (next action obvious)
- Sovereign (agency preserved)
- Correctable (mistakes recoverable)

**This optimizes for legibility, not appearance.**

**Result:**
- System shows real complexity honestly
- Operator has context for decisions
- Mistakes caught early with dignity
- Trust accumulates through honesty

---

## Why Performance UX Dominates

**Performance UX wins in market because:**
1. Looks better in demos
2. Tests better in A/B (short-term metrics)
3. Investors prefer smooth to honest
4. Users conditioned to expect it
5. Easier to measure (clicks, time, conversion)

**Legibility UX loses in market because:**
1. Looks "unfinished" (shows complexity)
2. Tests worse in A/B (short-term friction)
3. Investors don't understand value
4. Users unfamiliar with honesty
5. Harder to measure (understanding, trust, sovereignty)

**But for sovereign operators:**

Performance UX is hostile.  
Legibility UX is operable.

**PortalVision chooses operable.**

---

## Examples from PortalVision

### 1. Artifact Ingestion (Duplicate Detection)

**What happens:**
- System detects potential duplicate
- Pauses ingestion
- Shows match report
- Presents three options (proceed, decay, abort)
- Operator decides

**Why this is legible:**
- Discloses problem honestly
- Shows all real options
- No recommendation
- Consequences explained
- Decision logged

**Performance UX alternative:**
- Auto-merge duplicates (smoother)
- Or silently skip (simpler)
- Or show error and block (faster)

**Why PortalVision doesn't:**
- Auto-merge: removes agency
- Silent skip: hides problem
- Block: hostility without context

**Legibility > smoothness.**

---

### 2. Operator Check (INV-014 Enforcement)

**What happens:**
- System requires authorship context
- Blocks ingestion if not provided
- Explains why it's required
- Shows what's needed
- Makes next action obvious

**Why this is legible:**
- Refusal with explanation
- Constraint disclosed
- Dignity preserved
- Path forward clear

**Performance UX alternative:**
- Skip check (smoother)
- Auto-fill with guess (simpler)
- Angry error message (faster to implement)

**Why PortalVision doesn't:**
- Skip: violates invariant
- Auto-fill: dishonest
- Angry error: hostile

**Clarity > convenience.**

---

### 3. StarPortal Pause State

**What happens:**
- Operator hits space bar (pause)
- System enters vigilance hold
- All navigation stops
- Context preserved
- Resume when ready

**Why this is legible:**
- Silence is an option (Rule 2)
- No pressure to continue
- State clearly indicated
- Temporal respect (no urgency)

**Performance UX alternative:**
- No pause allowed (smooth flow)
- Auto-resume after timeout (reduce friction)
- Suggest next action (guide behavior)

**Why PortalVision doesn't:**
- No pause: removes agency
- Auto-resume: violates intent
- Suggest action: prescription

**Operator decides when to continue.**

---

## Summary

**Good UX does not tell operators what to do.**  
**It tells them what exists.**

**Options are:**
- Disclosed, not suggested
- Neutral, not persuasive
- Honest, not comforting
- Bounded, not exhaustive

**When options are provided correctly:**
- Operators act freely
- Systems remain non-hostile
- Mistakes become correctable
- Trust accumulates quietly

---

## The Face of Performance

**Remember:**

UX is the face of performance in software.

**This means:**
- UX can look smooth while hiding chaos (accurate but not correct)
- UX can look rough while showing truth (correct but not accurate to expectations)

**PortalVision chooses:**
- Show truth even if rough
- Legibility over smoothness
- Correctness over performance

**Because:**
- Sovereign operators need truth
- Performance facade degrades agency
- Honest UX builds trust
- Smooth UX optimizes for wrong metric

---

## Design Implication

**When designing UX for PortalVision:**

**Ask:**
- Does this show actual system state?
- Are consequences honestly disclosed?
- Is operator agency preserved?
- Are options presented without pressure?

**Don't ask:**
- Does this look smooth?
- Will users like this?
- Does this reduce friction?
- Will this increase engagement?

**First set: Legibility questions.**  
**Second set: Performance questions.**

**Optimize for first, ignore second.**

---

## Does Not

**This document does NOT:**
- Prescribe visual design (colors, fonts, layouts)
- Claim performance UX is always wrong (correct for different goals)
- Suggest legibility is "better" universally (correct for sovereign operators)
- Provide implementation details (that's context-specific)
- Guarantee users will like it (users conditioned for performance)

**This document DOES:**
- Define legibility vs. performance distinction
- Explain why PortalVision optimizes for legibility
- Provide principles for option presentation
- Show examples from actual implementation
- Acknowledge market realities honestly

---

## References

**Related Documents:**
- `OPERATOR_EGO_BAND.md` - Understanding operator states
- `HUMANE_RIGOR_BALANCE.md` - Simultaneous dignity and rigor
- `OBEY.md` - Listening with agency vs. obeying
- `MINIMUM_VIABLE_OPERATOR.md` - Operator assumptions
- `DELIBERATE_OBFUSCATION.md` - When complexity is honest

**PortalVision Examples:**
- Duplicate artifact detection (three options)
- Authorship context enforcement (refusal with dignity)
- StarPortal pause state (silence as option)

---

**Status:** Foundational  
**Origin:** Operator recognition + AEN grounding  
**Application:** All UX decisions in PortalVision  
**Success Metric:** Operator understanding and agency preservation

