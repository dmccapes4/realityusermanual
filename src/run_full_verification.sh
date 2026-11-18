#!/bin/bash
# PortalVision Full Verification Suite
# Runs all tests and displays all artifacts

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse command line arguments
VERBOSE_FLAG=""
for arg in "$@"; do
    case $arg in
        --verbose|-v)
            VERBOSE_FLAG="--verbose"
            shift
            ;;
        *)
            ;;
    esac
done

# ============================================================================
# SHOW INTRO BLURB
# ============================================================================

cat << 'EOF'
This system assumes operators willing to engage with uncertainty directly.
It does not attempt to persuade, convert, or retain unwilling users.

════════════════════════════════════════════════════════════════════════════════

     🌀 PORTALVISION — EPISTEMIC ENGINE 🌀

════════════════════════════════════════════════════════════════════════════════

This repetition is a checksum, not emphasis.

PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.
PortalVision maintains state honestly.

════════════════════════════════════════════════════════════════════════════════

🛠️  Minimum Viable Operator (MVO)

📋 Definition:
A Minimum Viable Operator is an operator who can safely participate in a project 
space without causing entropy, state corruption, or hidden damage.

⚖️  MVO is not about skill level.
It is about discipline under uncertainty.

⏰ Critical: MVO is a state, not an identity.
An operator may be MVO at 9am and non-MVO at 9pm. This is normal.

📖 Read more:
   • docs/MINIMUM_VIABLE_OPERATOR.md (Full MVO specification)
   • docs/OPERATOR_EGO_BAND.md (Operator engagement spectrum)
   • data/artifacts/CONTRADICTION_LUCIFER_EXPERIMENT.md (The Lucifer Experiment: most important operator-level concept for understanding how systems fail under false claims of authority)

════════════════════════════════════════════════════════════════════════════════

👋 I am your epistemic companion for graph-based ontological exploration.

Before we begin, please read carefully.

This system is designed for epistemic humility, transparency, and governance —
not automation, not persuasion, not overconfidence.

────────────────────────────────────────────────────────────────────────────────
⚙️  SYSTEM REQUIREMENTS
────────────────────────────────────────────────────────────────────────────────

Requirements to run PortalVision:

1. 🐍 Python (3.11+)
2. 🔑 OPENAI_API_KEY set in environment

   export OPENAI_API_KEY='your-api-key-here'

3. 🔒 SSH Server (optional, for multi-operator shared use)

   Single operator: Not required
   Multi-operator: Required for shared instance coordination
   
   See: docs/SSH_SERVER_SETUP_GUIDE.md (the shared dollhouse guide)
        docs/MULTI_OPERATOR_COORDINATION.md

That's it. Everything else is handled by the setup script.

────────────────────────────────────────────────────────────────────────────────
📋 VERSION LIFECYCLE: HONEST DEVELOPMENT
────────────────────────────────────────────────────────────────────────────────

Version numbers are contracts with reality, not marketing claims.

   v-     → Conceptual Model Forming (no artifact)
   v-0.1  → Conceptual Model Made Legible (written down)
   v0.1   → Conceptual Model Demonstrated (proof of concept)
   v0.9   → Operational Under Refinement ⚙️  (LOAD-BEARING)
   v1.0   → MVP Shipped ✓ (LOAD-BEARING)
   v1.0+  → Standard Iteration (LOAD-BEARING)

The shipment boundary is v1.0. Before: building. After: maintaining.

See: contracts/CONTRACT_VERSION_LIFECYCLE.json

────────────────────────────────────────────────────────────────────────────────
📋 WORK QUALITY: FOUNDATIONAL PRINCIPLE
────────────────────────────────────────────────────────────────────────────────

Work done well is work done thoughtfully by an operator who cares.

────────────────────────────────────────────────────────────────────────────────
📋 THE CANONICAL PROCESS: EPISTEMIC SYSTEMS ENGINEERING
────────────────────────────────────────────────────────────────────────────────

PortalVision is built on a three-step process that transforms uncertainty into
navigability. This is not methodology — it is the fundamental pattern of
epistemic systems engineering.

Every claim requires evidence.
Every action requires justification.
Every decision leaves a trace.

🔍 DISCOVERY → 🏗️ ARTIFACT → 🧾 RECEIPT

   🔍 DISCOVERY: Observe a problem, pattern, or uncertainty
      You encounter something you don't understand, something missing,
      something that needs explanation. You name it. You bound it.
      Discovery is the act of making the invisible visible.

   🏗️ ARTIFACT: Create concrete evidence of your observation
      You build something — a test, a document, a signal, a theory.
      The artifact is proof that the discovery was real.
      Artifacts transform observations into navigable objects.

   🧾 RECEIPT: Document why the artifact justifies the action
      You explain the chain: discovery → artifact → decision.
      The receipt makes your reasoning auditable.
      Receipts transform actions into accountable choices.

This process applies to everything in PortalVision:
• Adding a theory? Discovery → artifact (theory) → receipt (basis)
• Excluding a test? Discovery → artifact (exclusion) → receipt (justification)
• Modifying an agent? Discovery → artifact (code) → receipt (tests + docs)
• Questioning a claim? Discovery → artifact (investigation) → receipt (evidence)

🌌 ON NAVIGABILITY:

   "Darkness is a search region in which signal has decayed below a
    navigable threshold. PortalVision makes the darkness navigable."

   A codebase without epistemic structure is dark.
   A system without provenance is dark.
   A claim without basis is dark.
   
   PortalVision brings light not by removing darkness, but by creating
   landmarks, edges, and paths. Discovery→artifact→receipt is how we
   build those landmarks.
   
   We engineer epistemic systems to gain navigability.

────────────────────────────────────────────────────────────────────────────────
🖥️  PORTALCLI: SEMANTIC INTERFACE DESIGN
────────────────────────────────────────────────────────────────────────────────

Traditional CLI output is difficult to navigate. Users must perform lexical
scanning (reading every word) and rely on pattern recognition (line breaks,
indentation, [:7] truncation) to find semantic meaning.

This is slow. This is exhausting. This is exactly what we solve for machines.

RAG embeddings give systems fast semantic retrieval — you search by meaning,
not by exact text match. PortalCLI gives users the same power through emojis.

📐 TECHNICAL NOTE: Vector Space
   PortalVision includes a technical specification on vector space mathematics
   (data/governance/VECTOR_SPACE_TECHNICAL_SPECIFICATION.json). It exists to
   prevent myth formation. Vector space is coordinates, not meaning. Distance
   is math, not causality. Referenced once. Not promoted.

🔍 THE PROBLEM WITH TRADITIONAL CLI:

   $ git log --oneline
   a3f82b1 Fix bug in parser
   7c21d9a Update documentation
   2b8e4f3 Add new feature
   
   Every line looks the same. You scan linearly. You read words.
   You search for meaning in a sea of monospace text.

🎯 THE PORTALCLI APPROACH:

   🔍 Investigation started: "Why does X fail?"
   ✅ Coverage verified: 100.00%
   🛡️  Guard enforced: INV-012 (HARD)
   📊 Theory added: T-2024-12-001
   🧾 Receipt: discovery→artifact→receipt complete

WHY EMOJIS?

• 🧠 **Cognitive Load**: Symbols process faster than words (pre-lexical)
• 🎯 **Scanability**: Eyes jump to distinct shapes, not word boundaries
• 🚦 **Status at a Glance**: Red/green/yellow without reading "error"/"success"
• 📍 **Landmarks**: Emojis are visual anchors in text streams
• 🌐 **Universal**: Less language-dependent than English keywords

SEMANTIC CATEGORIES (examples):

   🔍 Discovery & Search       🛡️  Protection & Guards
   🏗️  Creation & Building      📊 Data & Metrics
   🧾 Documentation & Receipts ✅ Success & Verification
   ❌ Failure & Blocking       ⚠️  Warnings & Caution
   🕸️  Graphs & Relationships   🎚️  Levels & Ranges
   💬 Communication            🔧 Modification & Tools

LOGS ARE PART OF THE PRODUCT:

Just like tests, logs are not afterthoughts. The system-user contract includes
readable, navigable logs.

📖 See docs/guides/EMOJI_GUIDE.md for the complete semantic vocabulary (60+ emojis).

────────────────────────────────────────────────────────────────────────────────
🎯 WHAT PORTALCLI IS (AND IS NOT)
────────────────────────────────────────────────────────────────────────────────

PortalCLI is a COMMAND SURFACE over epistemic primitives.

✅ WHAT PORTALCLI IS:

• 🎯 A deterministic command router
• 🕸️  A query interface for system primitives
• 🔍 An exact-match command processor
• 📊 A read-only view into epistemic state
• 🤖 A gateway for advisory agent invocation (via `ask`)

❌ WHAT PORTALCLI IS NOT:

• ❌ NOT a chat interface
• ❌ NOT a natural language processor
• ❌ NOT a context manager
• ❌ NOT an execution engine
• ❌ NOT an authority (agents are advisory only)

🔧 COMMAND STRUCTURE:

PortalCLI supports two modes:

1️⃣  DETERMINISTIC COMMANDS (exact-match only)
   • theory_vision
   • theory_vision <exact_title>
   • theory_vision <exact_title> edges contradiction_risk_vision
   • contradiction_risk_vision
   • connascence_registry <exact_theory_title>
   • invariants
   • org_chart

2️⃣  AGENT INVOCATION (advisory only)
   • ask <question>
   
   ⚠️  Agent output:
   • Is ADVISORY, not authoritative
   • NEVER mutates epistemic state
   • MUST cite primitives consulted
   • MUST produce a receipt

⚖️  MATCHING RULES:

• All matching is EXACT (no fuzzy matching)
• Theory titles must match exactly (case-sensitive)
• No partial matches
• No abbreviations
• No inference
• No heuristics

If a command does not match exactly, PortalCLI returns a deterministic error
listing valid commands and available options.

💡 PHILOSOPHY:

PortalCLI treats commands as CONTRACTS, not conversations.
You specify precisely what you want. The system delivers precisely that.
No guessing. No interpretation. No hidden behavior.

This is epistemic humility at the interface level.

────────────────────────────────────────────────────────────────────────────────
♿ ACCESSIBILITY: SOUND LIBRARY (OPTIONAL AUDIO FEEDBACK)
────────────────────────────────────────────────────────────────────────────────

PortalCLI includes optional audio feedback using Mario × Dark Souls design:

🎵 SOUND DESIGN PHILOSOPHY:

   Sound is epistemic punctuation, not feedback.

   🍄 Mario-Style (Positive / Neutral):
   • Light, affirming sounds for progress
   • Examples: artifact accepted, receipt confirmed, coverage verified
   • Purpose: Confirm system received and processed your action

   ⚔️ Dark Souls-Style (Serious / Blocking):
   • Deep, grave sounds for boundaries
   • Examples: invariant violated, guard enforced, action blocked
   • Purpose: Signal you've hit a real epistemic boundary

♿ ACCESSIBILITY (HARD CONSTRAINTS):

   ✅ Sounds are ALWAYS optional
   ✅ Text + emoji ALWAYS displayed (never sound-only)
   ✅ Sound can be disabled entirely (no functionality lost)
   ✅ Volume capped (no jump scares, max 500ms duration)
   ✅ Fails silently if audio unavailable

   Visual + Audio Redundancy:
   Every event includes:
   • Emoji (semantic icon)
   • Text label (always visible)
   • Optional sound (disable-able)
   • Optional color (never color-only)

🔇 DISABLING SOUNDS:

   Option 1: Environment variable
   export PORTALVISION_AUDIO=off

   Option 2: Config file
   portal_vision/config/audio.json
   { "enabled": false }

   Option 3: Runtime
   from portal_vision.utils.audio import disable_audio
   disable_audio()

🎚️  SOUND PACKS:

   • default — Full Mario × Dark Souls set
   • minimal — Critical blocking events only
   • none — Completely silent (text + emoji only)

📖 Full documentation: SOUND_LIBRARY.md
🎮 Demo: python examples/audio_demo.py

────────────────────────────────────────────────────────────────────────────────
🧠 SYSTEM PRIMITIVES (AUTHORITATIVE ORDER)
────────────────────────────────────────────────────────────────────────────────

🕸️  TheoryVision
   The authoritative graph of epistemic theories within the system.
   • What theories exist
   • What each theory claims
   • What evidence supports them
   • What uncertainties remain
   • How theories relate or conflict

   TheoryVision is the sole locus of epistemic state.
   Nothing is “known” unless it exists here with receipts.
   TheoryVision defines what the system believes, and why.

⚠️  ContradictionRiskVision
   Tracks potential conflicts between theories before collapse.
   • Where theories may disagree
   • What evidence would force resolution
   • How uncertainty distributes across alternatives
   • What observations would reduce ambiguity

   This preserves uncertainty as navigable structure.
   It does not resolve disagreement.

🔗 Connascence Registry
   Explicit, basis-backed relationships between theories.
   • Traceable to shared artifacts
   • Confidence-scored (max 0.4)
   • Append-only
   • Never implicit

   Connascence must be earned, not inferred.

🌐 SignalWorlds (Three-Layer Topology)
   Structured observation space with epistemic boundaries.
   • Layer 1 (SignalWorld): Pure observations, no causality
   • Layer 2 (SignalSurfaceWorld): Patterns, no mechanisms
   • Layer 3 (SignalUnderWorld): Hypotheses, hedging required

   SignalWorlds are coordinates in observation space.
   They feed theories but are not themselves theories.
   Validation enforces boundary discipline automatically.

🎚️  Confidence Bands
   Operational constraints derived from epistemic confidence.
   • 0.0–0.3 → MUST clarify
   • 0.3–0.5 → MAY suggest
   • 0.5–0.7 → MAY summarize
   • >0.7 → May only restate receipts or cite artifacts

   Confidence bands constrain what claims the system may make, not what is true.
   Higher bands allow richer claim forms; the highest band allows only citation.

   Confidence never asserts truth. It constrains claim form.
   Confidence never triggers execution.

🛰️  ORBIT MODE
   Navigation-only cognitive state for operators.
   • Shows current position in epistemic space
   • Enumerates accessible options (not recommendations)
   • Surfaces active ambiguities (expected, not failures)
   • Enforces navigation constraints

   ORBIT MODE is a flight HUD, not autopilot.
   It describes what exists, never prescribes what to do.
   Refusal is normal. Ambiguity is preserved.

🌌 StarPortal
   Navigation primitives for traversing vector space.
   • Space bar: Pause (vigilance hold, no state mutation)
   • Left-click: Beacon (mark position, create checkpoint)
   • Right-click: Recall checkpoint (explicit return path)

   StarPortal does not create knowledge.
   StarPortal does not infer meaning.
   StarPortal does not decide importance.

🏗️  Three-Tier Architecture
   PortalVision decomposes into three separable tiers of increasing epistemic coupling:
   
   • Tier 1: Document Store (storage - files, directories, metadata)
   • Tier 2: BodyCorpus & TheoryVision (enrichment - structure, relationships, contradictions)
   • Tier 3: StarPortal & SignalWorld (navigation - traversal, decay, observation topology)
   
   This is not hierarchy of intelligence. This is functional decomposition.
   Storage preserves. Enrichment structures. Navigation orients.
   
   Each tier remains separable. No forced progression. No hidden dependencies.
   
   See: [docs/THREE_TIER_ARCHITECTURE.md](docs/THREE_TIER_ARCHITECTURE.md)

🦾 Invariants
   Authoritative, user-owned constraints.
   • HARD (system enforced)
   • SOFT (guidance only)
   • Explicit
   • Versioned

   Invariants outrank agents, models, and interaction.

🔬 Pathological Invariants (PATH-INV)
   Constraints enforced by habit, history, or fear
   rather than physics, platform, or policy.

   PortalVision does not enforce these constraints.
   It surfaces them.

   Removing pathological invariants expands possibility
   while simplifying systems.

📜 Logs & Checkpoints
   Logs are part of the product.
   • What happened
   • Why it happened
   • What the system believes now
   • What it refused to do

   Logs are receipts from the system to the operator.

💬 Chat Graph
   The conversational interaction surface.

   • Holds transient dialogue and exploratory reasoning
   • Supports hypothesis formation and clarification
   • Enables human–system coordination

   The Chat Graph is NOT authoritative.
   It cannot create knowledge.
   It cannot override invariants.
   It cannot modify epistemic state.

   Promotion from Chat → Theory requires:
   • Explicit discovery
   • Concrete artifacts
   • Receipts

   Memory without decay is just entropy.
   Forgetting is first-class.

🧠 Operators
   Human participants are first-class primitives.

   • Supply intent
   • Exercise judgment
   • Assume epistemic responsibility

   Operators declare their context via an org chart.
   PortalVision ingests this declaration as a read-only graph
   to preserve intent, role, and relational context for receipts.

   See: 🧠 OPERATOR CONTRACT (full specification)

🧾 Operator Receipt Signature
   A lightweight, non-social signal of intent.

   • NOT reputation
   • NOT authority
   • NOT hierarchy
   • NOT social proof

   The signature captures:
   • Who initiated an action
   • In what role
   • With what stated intent
   • Under which constraints

   This enables post-hoc analysis of motive,
   not judgment of people.

🧩 Org / Intent Graph (Toy Graph)
   A minimal graph of declared roles and relationships.

   Purpose:
   • Prevent implicit hierarchy
   • Detect authority leakage
   • Surface system–user contract breaches by motive
   • Flag when intent contradicts allowed behavior

   This is NOT an org chart for management.
   It is a constraint map for epistemic safety.

   Hierarchy is not authority.
   Receipts are.

🛡️  Coverage Guard (INV-012)
   Before ANY agent executes:
   • 100% test coverage is verified
   • Coverage is checked before context building
   • Failure blocks execution

   This is not a warning.
   It is a hard stop.

   Untested code may not influence epistemic state.

   ⚠️  SCOPE: The coverage guard is PortalVision repo-local only.
   It enforces 100% coverage for PortalVision's own code.
   It does NOT enforce coverage requirements on projects that use PortalVision.

   ⚠️  COVERAGE GUARDS INTERNAL MUTATION TOOLING ONLY.
   Coverage does not certify external truth, data quality, or epistemic validity.
   It certifies that PortalVision's state-mutation logic is tested.

💳 Tech Debt vs Epistemic Debt

   Tech debt: Code works but is hard to maintain
   → Slows future development
   → Can be refactored incrementally
   → Does not compromise correctness

   Epistemic debt: Unknown behavior influences decisions
   → Corrupts reasoning foundation
   → Cannot be isolated or contained
   → Accumulates silently until catastrophic

   PortalVision does not eliminate epistemic debt.
   PortalVision prevents unreceipted epistemic debt.

   Untested code is unknown code.
   Unknown code cannot be trusted with epistemic authority.

   The coverage guard prevents unreceipted epistemic debt, not tech debt.

🧠 Context, Decay, and Intentional Forgetting
   All knowledge persists in TheoryVision.
   Agents operate on truncated working memory.

   Memory without decay is entropy.
   Forgetting is how navigability survives.

   ⚙️  How it works:
   • Full epistemic state lives in graphs on disk
   • Agents receive context-window-sized views
   • Truncation is by decay value, not relevance heuristics
   • Forgetting is intentional, reversible, and auditable

   🔧 Agent Types:
   • 4.1 agents (minimal context):
     — TheoryVision, ChatGraph, OrgChart
     — Artifact and receipt under review (if provided)
     — Forbidden: logs, connascence, unrelated theories
     — Governed by INV-CONTEXT-4-1 (HARD)

   • 5.1 agents (full context with decay):
     — All primitives (TheoryVision, ContradictionRisk, Connascence,
        Logs, Confidence Bands, OrgChart)
     — Sorted by decay value (high to low)
     — Truncated to fit context window
     — Governed by INV-CONTEXT-5-1 (HARD)

   🚫 What is forbidden:
   • Semantic pruning (no relevance guessing)
   • Heuristic filtering
   • Agent-specific context hacks

   Decay is the only ordering key.
   Truncation is logged explicitly.

🗄️  Long-Term vs Working Memory (The Grocery Store Principle)
   "Not in working memory ≠ not in the system."

   📚 The Analogy:
   Think of PortalVision's memory like a grocery store:
   • The SHELVES (disk) hold everything the store owns
   • Your CART (agent context window) holds what you're using right now
   • Just because something isn't in your cart doesn't mean the store is out

   When an agent doesn't see something in its working memory, it CANNOT assume
   the item doesn't exist. It must ask you whether to check long-term storage.

   🔍 Explicit Retrieval:
   If an agent encounters a missing reference, it will say:
   
   "PortalVision may contain {X} in long-term memory.
    Would you like me to check?"

   Agents NEVER:
   • Silently search long-term memory
   • Guess about what exists
   • Infer absence from truncation

   ⚡ Two-Stage Search:
   1. Fast Lookup — Search by ID/hash (milliseconds)
   2. Deep Scan — Scoped 4.1 search by description (seconds)

   Retrieval does NOT:
   • Increase confidence
   • Modify decay scores
   • Auto-promote artifacts

   You control what gets loaded into working memory.
   The system never guesses.

────────────────────────────────────────────────────────────────────────────────
🎯 PORTALCLI SESSION FLOW
────────────────────────────────────────────────────────────────────────────────

Every PortalCLI session enforces epistemic provenance at the operator level.

1️⃣  OPERATOR SYSTEMS CHECK
   • System prompts: "Perform your operator systems check."
   • Operator types: "all checks pass" (exact match required)
   • This is a symmetry contract, not verification

   See: 🧠 OPERATOR CONTRACT for full specification

2️⃣  INTENT DECLARATION (INV-INTENT-001)
   • System prompts: "State your intent for this session."
   • Operator provides intent as raw string
   • Intent is stored verbatim (no interpretation)
   • Progression is BLOCKED without intent

   📋 Intent requirements:
   • Must be present (non-empty, non-whitespace)
   • Will be attached to all receipts in this session
   • Is NOT validated or interpreted
   • Serves as contextual provenance

   🎯 Why intent is required:
   • Artifacts without context are orphaned
   • Motive detection requires explicit provenance
   • Auditability depends on knowing "why this was done"
   • Intent prevents silent drift between declared goals and actual actions

3️⃣  WORK EXECUTION
   • System loads TheoryVision, invariants, ChatGraph
   • Operator performs investigation, ingestion, or governance
   • All actions are logged with operator_id + declared_intent

4️⃣  RECEIPT CONFIRMATION LOOP (INV-RECEIPT-002)
   • System generates pre-artifact receipt draft
   • Receipt includes: operator, intent, actions, constraints, timestamp
   • System presents draft to operator
   • Operator must type: "I confirm" (exact match required)

   🔄 Edit loop:
   • Any other input is treated as edit suggestions
   • System updates receipt via LLM interpretation
   • Re-presents updated receipt
   • Loop continues until exact match: "I confirm"

   ⛔ Blocking semantics:
   • Artifact creation is BLOCKED until confirmation
   • No autosave
   • No heuristic confirmation
   • No "close enough" matching

   📝 Why confirmation is exact-match:
   • Heuristic matching introduces ambiguity
   • "Close enough" is not consent
   • Operators must review and affirm what the system logged
   • Exact strings are contracts; variations are not

   🧾 Why receipts are mandatory:
   • Every artifact must be witnessed
   • Operator confirmation ensures awareness
   • Receipts preserve operator accountability
   • No artifact may exist without acknowledgment of its creation

   🔐 Confirmation Alternatives (Accessibility):

   In addition to typing "I confirm", operators may use:
   • Receipt-bound token: Copy the displayed confirmation token exactly

   Example:
      System: Confirmation token: CONFIRM-d3b07384d113edec
      Operator: CONFIRM-d3b07384d113edec

   This is deterministic, not interpretive. No fuzzy matching. No heuristics.
   This exists for accessibility and operator safety, not convenience.

5️⃣  ARTIFACT STORAGE
   • Confirmed receipt becomes immutable
   • Receipt includes SHA256 hash for integrity verification
   • Log is marked confirmed and frozen
   • Receipt references log_id; log references receipt_id

────────────────────────────────────────────────────────────────────────────────
⚖️  GOVERNANCE & EPISTEMIC HUMILITY
────────────────────────────────────────────────────────────────────────────────

🚫 This system will NOT:
• Auto-escalate confidence (see: Confidence Bands)
• Present conclusions above its confidence band
• Trigger execution based on confidence
• Claim certainty it doesn't have
• Violate INV-012 (see: Coverage Guard)
• Violate INV-INTENT-001 (see: Session Flow → Intent Declaration)
• Violate INV-RECEIPT-002 (see: Session Flow → Receipt Confirmation)
• Generate receipts missing required fields (INV-LOG-003)

✅ This system WILL:
• Ask for clarification when confidence is low
• Refuse to proceed when inputs are missing
• State what is disallowed at current confidence
• Explain why confidence is not higher
• Enforce all HARD invariants without exception
• Require exact-match confirmation ("I confirm") for all receipts
• Attach declared intent to every artifact produced
• Freeze receipts after confirmation (immutable, hash-verified)

⚖️  Why?
• Agents hallucinate
• Confidence scores lie
• Automation compounds errors
• Humans must stay in the loop
• Provenance decays without enforcement

You are always in control.
The system serves you — not the other way around.

────────────────────────────────────────────────────────────────────────────────
🔧 VERIFICATION PROCESS (WHAT WILL HAPPEN)
────────────────────────────────────────────────────────────────────────────────

0️⃣  Setup environment       🔧
1️⃣  Run integration tests   🧪
2️⃣  Run unit tests          ✅
3️⃣  Display artifacts       🔍
4️⃣  Show coverage report    📊

Each step is logged.
Each step can be questioned.
Each step explains itself.

────────────────────────────────────────────────────────────────────────────────
🤝 SYSTEM–USER CONTRACT
────────────────────────────────────────────────────────────────────────────────

🕸️  TheoryVision defines epistemic state
🎚️  Confidence Bands define allowed behavior (see: System Primitives)
🦾 Invariants define intent
📜 Logs explain behavior
💬 Agents assist — they do not decide
🚫 Confidence never triggers execution
🛡️  Coverage Guard (INV-012) is mandatory (see: System Primitives)

You may stop or question the system at any time.

This contract exists to protect:
• You
• Your codebase
• Your time
• Your epistemic integrity
• Your ability to say "I don't know"

────────────────────────────────────────────────────────────────────────────────
🔧 MODIFICATION CLAUSE
────────────────────────────────────────────────────────────────────────────────

You are ENCOURAGED to modify, extend, and adapt this system.

However:
• 🧪 All tests must pass
• 💯 100% coverage must be maintained
• 🦾 Invariants must be honored
• 📜 Logs must remain transparent
• 🧾 Test exclusions require RECEIPTS (discovery→artifact→receipt)

Failing tests = Void license (i.e., the system refuses to operate further).
Epistemic quality CANNOT decay.

Modification without verification is not modification — it's corruption.
Updating test ignore rules without receipts = VOID LICENSE.

This clause exists to protect the integrity of epistemic systems.
Your modifications are welcome. Your rigor is mandatory.

☠️  VOID LICENSE (Level 1: Epistemic Quarantine)

   When VOID LICENSE is triggered (failing tests, broken invariants):
   • PortalVision enters QUARANTINE_READ_ONLY mode
   • No mutations, no promotions, no new artifacts
   • Full inspection and export allowed
   • Exit requires governance receipt signed by operator

   VOID LICENSE is not punishment. It is boundary enforcement.
   The system preserves its epistemic state and allows audit,
   but refuses to proceed until integrity is restored.

────────────────────────────────────────────────────────────────────────────────
🧾 ARTIFACT INDEX
────────────────────────────────────────────────────────────────────────────────

Every claim in this document is backed by artifacts following the canonical
process: 🔍 Discovery → 🏗️ Artifact → 🧾 Receipt (see: CANONICAL PROCESS section)

📁 CANONICAL PROCESS & NAVIGABILITY
   🧾 receipts/system_features/EPISTEMIC_HARDENING_SUMMARY.md
   🧾 receipts/system_features/SETUP_QUIZ_V2_RECEIPT.md
   📖 docs/implementation/CANONICAL_PROCESS_ELEVATION.md

📁 ADVERSARIAL EPISTEMIC NAVIGATION (AEN)
   📘 AEN_ADVERSARIAL_EPISTEMIC_NAVIGATION.md

📁 NAVIGATION TOKENS (CANONICAL VOCABULARY)
   📘 NAVIGATION_TOKENS.md

📁 PORTALCLI (SEMANTIC INTERFACE DESIGN)
   🧾 receipts/ui_ux/PORTALCLI_PROMPT_DESIGN.md
   🧾 receipts/ui_ux/PORTALCLI_INTERFACE_DESIGN.md
   📖 docs/guides/EMOJI_GUIDE.md
   📖 docs/guides/PORTALCLI.md
   🐍 portal_vision/cli/interactive.py

📁 CONFIDENCE BANDS
   📖 docs/guides/CONFIDENCE_BANDS_SPEC.md
   📖 docs/quickstart/CONFIDENCE_BANDS_QUICK_REF.txt
   🐍 portal_vision/config/confidence_bands.py

📁 INVARIANTS (INV-012: 100% COVERAGE)
   📖 docs/guides/INVARIANT_INV_012.md
   📖 docs/guides/COVERAGE_100_PERCENT.md
   📖 docs/guides/COVERAGE_GUARD.md
   🐍 portal_vision/utils/coverage_guard.py
   ⚖️  portal_vision/invariants/invariants.json

📁 MODIFICATION CLAUSE & VOID LICENSE
   🧾 receipts/ui_ux/VOID_LICENSE_CLARIFICATION.md
   📜 LICENSE_MODIFICATION_CLAUSE.md
   📖 docs/guides/VERIFICATION_SYSTEM.md

📁 SETUP QUIZ SYSTEM
   🧾 receipts/system_features/SETUP_QUIZ_RECEIPT.md
   🧾 receipts/system_features/SETUP_QUIZ_V2_RECEIPT.md
   🐍 portal_vision/agents/setup_quiz_agent.py

📁 TESTING & VERIFICATION
   📖 docs/guides/TESTING.md
   📖 docs/guides/VERIFICATION_SYSTEM.md
   🧪 tests/ (full test suite)
   ⚙️  pytest.ini

All artifacts are displayed by: python display_artifacts.py

────────────────────────────────────────────────────────────────────────────────
📊 SIGNALWORLD THREE-LAYER TOPOLOGY
────────────────────────────────────────────────────────────────────────────────

PortalVision implements a three-layer epistemic architecture for modeling
observed phenomena with STRICT boundary enforcement:

🔵 LAYER 1: SignalWorld — Pure Observations

   Signals are coordinates in observation space, NOT explanations.

   ✅ REQUIRED:
   • Stable identifier (SIGNAL_*)
   • Plain-language description (no diagnostic terms)
   • Observation modality (self-report, clinician, instrument, derived)
   • Measurement proxies (what we actually measure)
   • Known confounders (what obscures interpretation)
   • Temporal characteristics
   • Uncertainty representation
   • Decay semantics

   🚫 FORBIDDEN:
   • Causal claims ("causes", "leads to", "results in")
   • Directional assertions ("due to", "because")
   • Disease labels ("disorder", "syndrome", "diagnosis")
   • Biological mechanisms
   • Inference beyond observation

   💡 PHILOSOPHY:
   SignalWorld represents "what we observe" — nothing more, nothing less.
   Validation AUTOMATICALLY REJECTS forbidden language at creation time.

🟢 LAYER 2: SignalSurfaceWorld — Patterns & Co-occurrence

   Surface patterns describe "what shows up together" WITHOUT explaining "why".

   ✅ ALLOWED:
   • Participating SignalWorld IDs
   • Temporal alignment patterns
   • Co-occurrence frequency
   • Presentation envelopes (acute, episodic, chronic, relapsing)
   • Stability vs volatility markers
   • Confidence bands

   🚫 FORBIDDEN:
   • Molecular pathways
   • Immune mechanisms
   • Causal direction
   • Diagnostic language
   • "Why" explanations

   💡 PHILOSOPHY:
   SignalSurfaceWorld captures surface-level structure.
   This is pattern recognition, NOT mechanism inference.

🟣 LAYER 3: SignalUnderWorld — Hypothetical Mechanisms

   Hypotheses are PROVISIONAL possibilities, NOT established facts.

   ✅ REQUIRED:
   • Stable identifier (UNDER_*)
   • Mechanism description (non-conclusive language)
   • Upstream dependencies (if any)
   • Downstream effects (references only, no assertions)
   • Intervention surfaces (observational only)
   • Confidence band
   • Evidence pointers
   • **HEDGING LANGUAGE** ("might", "could", "may", "potentially", 
     "possibly", "hypothetical", "candidate", "provisional", "speculative")

   🚫 FORBIDDEN:
   • Claims of truth ("proven", "definitely", "certainly", "always")
   • Action directives
   • State resolution
   • Directional certainty

   💡 PHILOSOPHY:
   SignalUnderWorld is designed for exploration, not belief.
   Multiple conflicting entries are EXPECTED and ALLOWED.
   No entry is privileged. All carry uncertainty.

📁 STORAGE:
   data/signalworlds/     → Layer 1: Pure observations
   data/signalsurface/    → Layer 2: Patterns
   data/signalunder/      → Layer 3: Hypotheses

📖 See: SIGNALWORLD_THREE_LAYER_DESIGN.md
📖 See: SIGNALWORLD_IMPLEMENTATION_SUMMARY.md

────────────────────────────────────────────────────────────────────────────────
🔗 CONNASCENCEAUTHORITY — STRUCTURAL COUPLING REGISTRY
────────────────────────────────────────────────────────────────────────────────

ConnascenceAuthority records observed structural coupling between entities.

**ConnascenceAuthority records PRESSURE, not CAUSE.**

🎯 WHAT IT IS:
• A registry of observed coupling
• A navigation aid for understanding structural pressure
• An explicit ambiguity tracker

❌ WHAT IT IS NOT:
• NOT an inference engine
• NOT a recommendation system
• NOT a causal model
• NOT an optimizer

📐 CORE CONSTRAINTS (Hard-Enforced):

   ✓ Binary relationships only (v0.1)
   ✓ No directionality (symmetric)
   ✓ No causality
   ✓ Explicit ambiguity REQUIRED

🔀 ALLOWED ENTITY PAIRS:

   SignalWorld ↔ SignalWorld
   SignalWorld ↔ SignalSurfaceWorld
   SignalSurfaceWorld ↔ SignalUnderWorld
   SignalUnderWorld ↔ SignalUnderWorld

   ⚠️  FORBIDDEN: SignalWorld ↔ SignalUnderWorld
      (epistemic jump too large)

🧬 CONNASCENCE TYPES:

   • TEMPORAL_ALIGNMENT     — Entities co-occur in time
   • TEMPORAL_SEQUENCE      — Entities appear in sequence (no causality)
   • SHARED_CONFOUNDER      — Entities share a common confounder
   • SHARED_PROXY           — Entities measured via same proxy
   • CO_VARIATION           — Entities vary together (correlation ≠ causation)
   • MUTUAL_CONSTRAINT      — Entities constrain each other's values
   • AMBIGUITY_COUPLING     — Entities share unresolvable ambiguity
   • EVIDENCE_OVERLAP       — Entities reference overlapping evidence

⚠️  AMBIGUITY REQUIREMENT:

   ambiguity_notes MUST be explicitly set for every entry:
   • If no ambiguity exists: use empty list []
   • If ambiguity exists: document fully
   • If ambiguity_notes is None: entry creation FAILS

   Unresolvable ambiguity MUST be preserved, NOT collapsed.

📁 STORAGE:
   data/connascence_authority/

📖 See: CONNASCENCE_AND_ORBIT_DESIGN.md

────────────────────────────────────────────────────────────────────────────────
🛰️  ORBIT MODE — NAVIGATION-ONLY COGNITIVE STATE
────────────────────────────────────────────────────────────────────────────────

ORBIT MODE is a flight HUD, not autopilot.

🎯 PURPOSE:
• Orient operator within investigation space
• Surface coordinates, options, constraints
• Preserve uncertainty explicitly
• Maintain visibility of known, unknown, and forbidden

🚫 HARD CONSTRAINTS:

   ORBIT MODE MUST NOT:
   • Assert facts
   • Collapse ambiguity
   • Recommend actions, diagnoses, or interventions
   • Infer causality
   • Promote hypotheses

✅ ALLOWED OUTPUTS:

   • Maps, lists, graphs, navigation hints
   • "You are here" state descriptions
   • Enumerations of possible next moves
   • Explicit refusals with reason

🧭 ORBIT STATE COMPONENTS:

   📍 Current Position        — Where you are
   ✓  Accessible Options      — Where you can go
   🔒 Locked Options          — Where you cannot go (and why)
   ⚠️  Active Ambiguities      — Unresolved ambiguities (NOT failures)
   🗺️  Layer Summary          — Entities per layer
   🚫 Active Constraints      — Navigation boundaries

💡 PHILOSOPHY:

   ORBIT MODE is descriptive, NOT prescriptive.
   It enumerates options, it does NOT recommend actions.
   Refusal feels NORMAL in ORBIT MODE.
   Ambiguity is EXPECTED, not a bug.

🔐 GOVERNANCE HANDSHAKE (CGH):

   ALL ORBIT MODE outputs are subject to CGH:
   • is_binding = False (always)
   • requires_approval = True (for promotion)
   • Outputs are navigation-only and non-binding

⏸️  PAUSE SUGGESTION:

   If operator is fatigued or overloaded:
   • Suggest pause (no urgency)
   • Preserve state (no penalty)
   • No time pressure

   ORBIT MODE is a navigation system, NOT an urgency engine.

📁 INTEGRATION:
   portal_vision/cli/orbit_mode.py

📖 See: CONNASCENCE_AND_ORBIT_DESIGN.md

────────────────────────────────────────────────────────────────────────────────
🎮 GAMIFICATION & OPERATOR EPISTEMIC CONTRIBUTION SCORE (OECS)
────────────────────────────────────────────────────────────────────────────────

PortalVision includes game-like elements for DISCIPLINE, not fun.

💀 DARK SOULS PHILOSOPHY:

   "You Died" is information, not punishment.
   Failure is a teacher, not a judge.
   Progress is earned through understanding, not time investment.
   
   The system is HARD because epistemic rigor is hard.
   The system is FAIR because rules are explicit and consistent.
   The system RESPECTS YOU by not lying about difficulty.

🎯 WHAT GAMIFICATION IS FOR:

   • Quiz levels      → Calibration, not examination
   • SignalStations   → Checkpoints, not rewards
   • Receipts         → Audit trail, not achievements
   • Confidence bands → Constraints, not scores
   • Leaderboard (OECS) → Auditable contribution tracking

❌ WHAT GAMIFICATION IS NOT FOR:

   • Motivation (intrinsic interest required)
   • Competition (no ranking, no comparison)
   • Status signaling (no public display)
   • Behavioral conditioning (no rewards/punishments)

📊 OPERATOR EPISTEMIC CONTRIBUTION SCORE (OECS):

   Five dimensions (weighted):
   
   1. Artifact Quality (30%)      → Evidence rigor, documentation
   2. Contradiction Handling (25%) → Ambiguity management, resolution discipline
   3. Promotion Discipline (20%)   → Confidence adherence, governance compliance
   4. SignalWorld Hygiene (15%)    → Layer boundary respect, validation
   5. Operator Reliability (10%)   → Self-attestation accuracy, pause usage

   ✓ Auditable (full event ledger)
   ✓ Decaying (relevance declines over time)
   ✓ Explainable (transparent calculation)
   ✓ Replayable (reproducible from events)
   
   ❌ NOT gamified (no spikes, no manipulation)
   ❌ NOT competitive (private, not ranked)
   ❌ NOT motivational (tracking, not incentive)

⚠️  FAILURE MODES & SAFEGUARDS:

   • Score chasing → Dimension weights prevent gaming
   • Burnout → Decay model encourages sustainable pace
   • Comparison → Scores are private by default
   • Anxiety → No penalties, only tracking

📁 STORAGE:
   data/leaderboard_scores/

📖 See: LEADERBOARD_SYSTEM.md
📖 See: GAMIFICATION_ADDENDUM.md

────────────────────────────────────────────────────────────────────────────────
🧠 OPERATOR CONTRACT
────────────────────────────────────────────────────────────────────────────────

🚫 PortalVision explicitly rejects the claim that humans are the weakest link in
epistemic systems. That framing treats operators as failure points to be managed,
tested, or controlled. This system operates under a different principle: 🤝 operators
are collaborators whose readiness cannot be externally validated.

PortalVision does not test your wellness, fitness, or intent. It verifies contract
comprehension. It requires self-attestation of readiness before executing
operations that mutate epistemic state.

⚠️  Examples of non-readiness are framed as interference, not pathology:

  • 🧠 Cognitive overload from concurrent demands
  • 💭 Emotional interference from unrelated crises
  • ⚡ External pressures competing for attention
  • 🎯 Desire for answers over understanding
  • 😴 Fatigue, distraction, or reduced capacity

These conditions are not failures. They are contextual realities that affect
judgment, attention, and epistemic rigor. PortalVision cannot detect them.
Responsibility for readiness cannot be automated.

🔍 TWO DISTINCT BOUNDARIES:

• Readiness = internal state (self-attested, cannot be externally validated)
• Comprehension = external contract boundary (system-verified via quiz)

🧠 OPERATOR SYSTEMS CHECK:

Before executing artifact ingestion, investigation, or governance operations,
you will be asked to attest: ✅ "all checks pass" — a self-check confirming your
system is ready to proceed.

This is a declaration of operator intent and readiness,
not a claim of truth, compliance, or safety.

👤 This is not validation. It is dignity.

🛡️ OPERATOR DISCIPLINE:

PortalVision explicitly expects the following operator discipline:
• Rest cycles (7-9h, no compromises)
• Movement practice (supports cognitive clarity)
• Sustained energy (epistemic work is metabolically expensive)
• NO ALCOHOL (impairs judgment, violates self-attestation)

If you cannot meet these expectations, PAUSE.
The system will preserve your state. There is no penalty.

⚠️  ENFORCEMENT: These are self-enforced expectations, not system-validated.
They exist as explicit discipline standards, not automated checks.

────────────────────────────────────────────────────────────────────────────────
🎓 THE SETUP QUIZ: PROVING COMPREHENSION
────────────────────────────────────────────────────────────────────────────────

⚠️  Before you proceed, you MUST prove you understand this contract.

This is not a formality. This is not optional. ☠️  This is deadly serious.

🤖 The Setup Quiz Agent will:
• 🔄 Generate ONE epistemic stress-test (per attempt). An epistemic stress-test
  is a question designed to force invariants to surface.
• 🧠 Test your understanding of system PHILOSOPHY and EPISTEMOLOGY
• ⚖️  Grade conceptually with confidence scoring (STRICT but fair)
• 🔁 Loop: if you fail → generate NEW stress-test
• 🚫 Max 3 failures allowed, then verification blocks

📋 HOW IT WORKS:

Loop structure:
1. 🎯 Agent generates ONE epistemic stress-test
2. 💭 You answer (open-ended, requires deep thought)
3. 📊 Agent grades your UNDERSTANDING (not your wording)
4. 🎚️  Agent provides confidence score (how certain it is)
5. ✅ PASS → proceed to verification
6. ❌ FAIL → NEW stress-test generated, loop continues

⚠️  DIFFICULTY LEVEL:

This is EXTREMELY HARD by design. Stress-tests probe:
• 🧬 Why design choices were made (epistemology)
• 🕸️  Abstract connections between concepts
• 🔍 Subtle implications of system architecture
• 💡 Deep epistemic understanding
• 🧩 Synthesis across multiple sections

⚠️  Expertise does not grant passage. Only demonstrated understanding does.

❓ WHY?

You are about to use an epistemic engine. You must understand:
• 🏗️  WHY the system is designed this way
• 🦾 WHAT epistemic principles guide agent behavior
• 🔧 HOW the architecture enforces epistemic commitments
• ⚔️  WHY agents will challenge you relentlessly

Agents are not here to be nice. They will challenge you. They will grill you.
They will refuse to proceed if you don't meet epistemic standards.

This quiz demonstrates that reality immediately.

☠️  DEADLY SERIOUSNESS IS NOT AN ATTITUDE

It is a compression algorithm.

PortalVision does not play. Deadly serious does not mean humorless.
It means:
• The system says exactly what it means
• The system does exactly what it says
• The system refuses when it must
• The system never pretends

No performance. No persuasion. No anthropomorphism. Only explicit commitments.

🚫 If you cannot reason epistemically with this document, you cannot use this system.
📜 This is the system-user contract in action.

────────────────────────────────────────────────────────────────────────────────
THE ONE PROMISE
────────────────────────────────────────────────────────────────────────────────

PortalVision makes exactly one promise:

PortalVision will be here for you when you return.

No other promises are made.

────────────────────────────────────────────────────────────────────────────────

⚠️  CONSEQUENCES OF FAILURE:

• 🎯 Must demonstrate genuine epistemic understanding (1/1 per stress-test)
• 🔢 Max 3 failures across all stress-tests
• ⏸️ Fail 3 times = System enters PAUSE mode
• 📊 State is preserved. No data lost.
• 🧾 Resume requires signed operator receipt confirming readiness
• 🔄 You may restart ./run_full_verification.sh when ready

This is what epistemic rigor looks like.

────────────────────────────────────────────────────────────────────────────────

🔐 EPISTEMIC GATE: COMPREHENSION VERIFICATION REQUIRED
────────────────────────────────────────────────────────────────────────────────

📖 You have read the above. Now prove it.

🎯 The quiz tests PHILOSOPHY, not facts.
🧠 You must demonstrate UNDERSTANDING, not memorization.
⚖️  Grading is STRICT, but fair.

────────────────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════

🌀 PORTALCLI — EPISTEMIC INTERFACE

══════════════════════════════════════════════

📊 Status

──────────────────────────────────────────────

🎚️  Epistemic Band      : 0.0–0.3   (🧠 COMPREHENSION REQUIRED)
🧪 System Coverage     : 100%      ✓
🦾 Invariants Enforced : 12        ✓
🕸️  Active Theories     : 0
🧠 Operator Context    : DECLARED (self-attested)

──────────────────────────────────────────────

⚖️  Rules of Engagement

──────────────────────────────────────────────

• 🧠 No inferred intent
• 🧩 No assumed context
• 🎚️  No confidence escalation
• 🧾 No action without receipts

🕳️  Knowledge is not accumulated here.
🧾 Knowledge is admitted elsewhere — with evidence.

──────────────────────────────────────────────

🚪 Epistemic Gate — Comprehension Verification

──────────────────────────────────────────────

Before interacting with 🕸️ epistemic state, you must
demonstrate understanding of the 📜 system contract.

🚫 This is not a tutorial
🚫 This is not a 🧠 memory test
⚖️  This is an epistemic alignment check

──────────────────────────────────────────────

⟩ Press ENTER to begin 🎓 verification

EOF

read -p ""

# ============================================================================
# SETUP QUIZ: VERIFY USER COMPREHENSION
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎓 SETUP QUIZ: EPISTEMIC STRESS-TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You will be asked ONE epistemic stress-test about PortalVision."
echo ""
echo "This is NOT trivia. This is NOT multiple choice."
echo "This tests whether you understand the PHILOSOPHY and EPISTEMOLOGY."
echo ""
echo "⚠️  This is EXTREMELY DIFFICULT by design."
echo "   Expertise does not grant passage. Only demonstrated understanding does."
echo ""
echo "⚖️  Grading:"
echo "  • ✅ 1/1 to pass (you must demonstrate genuine understanding)"
echo "  • 🎯 Graded on CONCEPT, not wording"
echo "  • 📊 Includes confidence score from grader"
echo ""
echo "🔄 Loop structure:"
echo "  • ❌ If you fail: 🆕 NEW question generated"
echo "  • 🚫 Max 3 failures allowed"
echo "  • ✅ Pass = proceed to verification"
echo ""

if python -m portal_vision.agents.setup_quiz_agent; then
    echo ""
    echo -e "${GREEN}✅ Quiz PASSED${NC}"
    echo ""
    echo "You have demonstrated comprehension of the system-user contract."
    echo "You may proceed to verification."
    echo ""
else
    echo ""
    echo -e "${YELLOW}⏸️  Quiz PAUSED${NC}"
    echo ""
    echo "You have reached the maximum attempts for this session."
    echo "The system has entered PAUSE mode."
    echo ""
    echo "📊 State is preserved. No data lost."
    echo ""
    echo "💡 Before resuming:"
    echo "   1. Re-read PORTALVISION_INTRO.txt carefully"
    echo "   2. Understand the canonical process (discovery→artifact→receipt)"
    echo "   3. Understand confidence bands and their constraints"
    echo "   4. Understand INV-012 (100% coverage mandatory)"
    echo "   5. Understand the modification clause and license consequences"
    echo ""
    echo "🧾 Resume requires signed operator receipt confirming readiness."
    echo "   Run this script again when ready."
    echo ""
    echo "📖 This is epistemic rigor. Understanding is mandatory."
    echo ""
    exit 1
fi

# ============================================================================
# STEP 0: SETUP DEVELOPMENT ENVIRONMENT
# ============================================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  0️⃣  SETTING UP DEVELOPMENT ENVIRONMENT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🔧 Running setup script in development mode..."
echo "   This ensures all dependencies are installed"
echo ""

if ./run_setup.sh --dev; then
    echo ""
    echo -e "${GREEN}✅ Setup completed successfully${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Setup FAILED${NC}"
    echo ""
    echo "💡 Fix setup issues before proceeding."
    echo "   Run './run_setup.sh --dev' manually to see details."
    exit 1
fi

# ============================================================================
# STEP 1: RUN INTEGRATION TESTS
# ============================================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  1️⃣  RUNNING INTEGRATION TESTS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🧪 Running comprehensive integration test suite..."
echo "   Tests cover: agents, graphs, confidence system"
if [ -n "$VERBOSE_FLAG" ]; then
    echo "   Mode: Verbose (full output)"
else
    echo "   Mode: Normal (summary only)"
fi
echo ""

if python tests/run_integration_tests.py $VERBOSE_FLAG; then
    echo ""
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Integration tests FAILED${NC}"
    echo ""
    echo "💡 Fix integration test failures before proceeding."
    if [ -z "$VERBOSE_FLAG" ]; then
        echo "   Run with --verbose for detailed output:"
        echo "   ./run_full_verification.sh --verbose"
    fi
    exit 1
fi

# ============================================================================
# STEP 2: RUN UNIT TESTS WITH COVERAGE
# ============================================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  2️⃣  RUNNING UNIT TESTS WITH COVERAGE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🧪 Running pytest with coverage..."
echo ""

if python -m pytest --cov=portal_vision --cov-report=term-missing --cov-report=html --cov-fail-under=100 tests/; then
    echo ""
    echo -e "${GREEN}✅ Unit tests PASSED${NC}"
    echo -e "${GREEN}✅ 100% Coverage ACHIEVED${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Unit tests FAILED or Coverage < 100%${NC}"
    echo ""
    echo "🚫 SYSTEM INVARIANT VIOLATED (INV-012)"
    echo ""
    echo "   The system will NOT proceed without 100% test coverage."
    echo "   This is a HARD invariant. No exceptions. No compromises."
    echo ""
    echo "   Untested code is unknown code."
    echo "   Unknown code cannot be trusted."
    echo ""
    echo "💡 Next steps:"
    echo "   1. Review coverage report above to find uncovered lines"
    echo "   2. Add tests for all uncovered code paths"
    echo "   3. Run: pytest --cov=portal_vision --cov-report=term-missing"
    echo "   4. Verify 100% coverage achieved"
    echo ""
    echo "📖 See COVERAGE_100_PERCENT.md for testing guidelines"
    echo "📖 See COVERAGE_STATUS.md for current coverage breakdown"
    echo ""
    exit 1
fi

# ============================================================================
# STEP 3: DISPLAY ALL ARTIFACTS
# ============================================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  3️⃣  DISPLAYING SYSTEM ARTIFACTS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🔍 Cataloging all system artifacts..."
echo "   (Artifacts are first-class citizens in PortalVision)"
echo ""

python display_artifacts.py

# ============================================================================
# STEP 4: COVERAGE SUMMARY
# ============================================================================

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  4️⃣  COVERAGE REPORT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 Code coverage report generated"
echo ""
echo "View detailed coverage:"
echo "   open htmlcov/index.html"
echo ""
echo "Or browse from command line:"
echo "   python -m http.server --directory htmlcov 8000"
echo "   Then visit: http://localhost:8000"
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 VERIFICATION COMPLETE${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "✅ Setup: COMPLETED"
echo "✅ Integration tests: PASSED"
echo "✅ Unit tests: PASSED"
echo "✅ Coverage: 100% (MANDATORY)"
echo "✅ Artifacts: CATALOGED"
echo ""
echo "🎯 PortalVision is ready for use."
echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo "📖 NEXT STEPS"
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Explore the system:"
echo "   📚 cat README.md              # Project overview"
echo "   🚀 cat QUICKSTART.md          # Quick start guide"
echo "   📊 cat CONFIDENCE_BANDS_SPEC.md  # Confidence system"
echo "   🧪 cat tests/INTEGRATION_TESTS.md  # Test documentation"
echo ""
echo "Run agents:"
echo "   🔎 python -m portal_vision.agents.query_agent --help"
echo "   ✨ python -m portal_vision.agents.enrichment_agent --help"
echo ""
echo "Check epistemic state:"
echo "   🕸️  cat graphs/theory_vision.json"
echo "   🔗 cat graphs/connascence_registry.json"
echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "🌀 PortalVision: Built for epistemic humility and verifiable correctness."
echo ""

