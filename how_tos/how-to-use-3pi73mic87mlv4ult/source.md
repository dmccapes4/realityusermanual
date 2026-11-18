# HOW TO USE 3Pi$73MiC87MLV4ULT

**What:** Simple tool for organizing health questions and observations  
**Where:** https://2ndopinionmd.ai  
**Who:** Anyone with ongoing health questions or scattered notes  
**Cost:** Free to use

**Not medical advice. Not a diagnosis tool. Just a way to write things down clearly.**

---

## Quick Start (Main Info Up Front)

### 1. Go to https://2ndopinionmd.ai

Open the link. You'll see a single-page interface with a text box.

---

### 2. Choose Your Mode

You have three main modes:

#### **ASK Mode** (Asking Questions)
- Select ASK mode from interface options (extremely clear UI)
- Type your health question in plain language
- Example: "What could cause joint pain that moves around?"
- System retrieves relevant medical information
- Shows you sources and reasoning
- **You decide what to do with the information**
- **Stream endpoint:** `/ask_stream` (can lock to URL if desired)

#### **CODING Mode** (Writing Things Down)
- Select CODING mode from interface options (extremely clear UI)
- Document symptoms, observations, timeline
- Example: "Morning stiffness, worse in winter, better after movement"
- System organizes your notes
- Creates timeline automatically
- **Nothing is lost or forgotten**
- **Stream endpoint:** `/coding_stream` (can lock to URL if desired)

#### **EoH Mode** (Ethos of Health Framework)
- Select EoH mode from interface options (extremely clear UI)
- For values-aligned health reasoning
- System considers your personal health values and preferences
- Generates reasoning that respects your approach to care
- Useful when you want health information filtered through your ethos
- Example use: "I prefer minimal pharmaceutical intervention - what are non-drug approaches for managing inflammation?"
- **What makes this different:** Standard medical advice often assumes standard preferences. EoH mode calibrates to YOUR values.
- **How it works:**
  - You provide context about your health philosophy (once)
  - System remembers your values for the session
  - All subsequent reasoning respects those boundaries
  - Still evidence-based, just filtered through your lens
- **Example values you might specify:**
  - Preference for lifestyle interventions before medication
  - Comfort level with various intervention types
  - Religious or cultural health practices
  - Risk tolerance (conservative vs. aggressive treatment)
- **Stream endpoint:** `/eoh_stream` (can lock to URL if desired)
- **Note:** This is NOT about replacing medical advice with ideology. It's about organizing medical information in a way that aligns with how you want to approach your health.

#### **EoHD Mode** (Detective Investigation)
- For complex situations with lots of history
- System runs multi-step investigation
- Looks at timeline, patterns, contradictions
- Generates comprehensive report
- **Good for preparing for doctor appointments**
- **How it works:**
  - You provide your medical timeline (symptoms, diagnoses, treatments, outcomes)
  - System runs `/eoh_detective_stream` - a multi-step orchestrated investigation
  - Analyzes temporal patterns, diagnostic landscape, treatment responses
  - Identifies gaps, contradictions, and under-explored areas
  - Generates comprehensive report with structured reasoning
- **Currently available by request:** Email your timeline as PDF to dylan@2ndopinionmd.ai
- **What you'll receive:**
  - Full detective report (HTML export)
  - Timeline analysis with pattern recognition
  - Diagnostic landscape mapping
  - Treatment response analysis
  - Suggested questions for your doctor
  - All reasoning transparent and verifiable
- **Why email for now:** This mode requires more setup and takes longer to run (10-15 minutes). It's orchestrated through multiple analysis steps to ensure thoroughness.
- **Future:** Will be available directly in the interface, but manual processing ensures quality for early users.

---

### 3. Use the Tool

**Example 1: Simple Question (ASK mode)**
1. Select "Ask" mode from interface (or navigate to `/ask_stream`)
2. Type: "What are common causes of morning joint stiffness?"
3. Read the response
4. Click "Export" to save the answer (HTML file downloads)

**Example 2: Document Your Experience (CODING mode)**
1. Select "Code" mode from interface (or navigate to `/coding_stream`)
2. Type: "June 2024: Started noticing right knee pain after walks"
3. Add more observations over time
4. System keeps everything organized in timeline

**Example 2a: Values-Aligned Inquiry (EoH mode)**
1. Select "EoH" mode from interface (or navigate to `/eoh_stream`)
2. Specify your health values: "I prefer non-pharmaceutical approaches first"
3. Ask your question: "What are evidence-based options for managing chronic inflammation?"
4. System filters medical information through your stated values
5. Export response that respects your approach while remaining evidence-based

**Example 3: Deep Investigation (EoHD mode)**
1. Compile your medical timeline (symptoms, diagnoses, treatments, outcomes)
2. Save as PDF or organized document
3. Email to dylan@2ndopinionmd.ai with subject: "EoHD Investigation Request"
4. System runs `/eoh_detective_stream` (multi-step orchestrated analysis)
5. Receive comprehensive HTML report (typically within 24 hours)
6. Review detective analysis, timeline patterns, suggested questions for doctor

---

### 4. Export Your Work

**Every query generates an HTML receipt.**
- Click "Export" after any query
- HTML file downloads (named with timestamp)
- Contains full reasoning, sources, and your query
- Share with doctor, save for your records, or both

**What's in an export:**
- Your original question/observation
- System's reasoning process (transparent)
- Sources cited (verifiable)
- Timestamp (when you ran it)
- Everything preserved permanently

---

### 5. That's It

No account required. No login. No data stored on servers.

**Use it when you need it. Ignore it when you don't.**

---

## Common Use Cases

### For Chronic Conditions
- Track symptom patterns over time
- Document what helps vs what doesn't
- Prepare for doctor appointments with organized timeline
- Keep everything in one place instead of scattered notes

### For Research & Questions
- Ask structured health questions
- Get medical information with sources
- Explore without rushing to conclusions
- Build understanding gradually

### For Medical Appointments
- Run EoHD investigation before appointment
- Export report to share with doctor
- Have organized timeline ready
- Don't forget important details

### For Family Health Management
- Track multiple people's health questions
- Organize medical history
- Keep receipts of what was tried
- Share exports with family members

---

## Tips for Best Results

### 1. Be Specific
**Vague:** "I don't feel good"  
**Specific:** "Fatigue after lunch, worse on days when I eat bread"

### 2. Include Timeline
**Without:** "Joint pain"  
**With:** "Joint pain started March 2024, worse in mornings, improves with movement"

### 3. Document Everything
- Symptoms
- What you tried
- What helped
- What didn't help
- Questions that arose

### 4. Export Frequently
- Save your work
- Build a personal health record
- Have documentation for doctors
- Nothing gets lost

### 5. Don't Rush
- Clarity first, decisions later
- Use tool to organize, not to diagnose
- Take your time
- Revisit when needed

---

## What You'll See in the Interface

### The Text Box
- Type your question or observation here
- Plain language works fine
- No special formatting needed

### The Mode Selection (Extremely Clear UI)
- **Ask:** Select for questions (ASK mode - `/ask_stream`)
- **Code:** Select for documenting observations (CODING mode - `/coding_stream`)
- **EoH:** Select for values-aligned inquiry (EoH mode - `/eoh_stream`)
- **Investigate (EoHD mode):** Currently available by emailing timeline to dylan@2ndopinionmd.ai
- **Export:** Save your work as HTML
- **Note:** Mode selection is very clear in the interface. Stream endpoints (`/{mode}_stream`) can be used to lock to a specific URL if desired.

### The Response Area
- Shows system's reasoning
- Includes sources cited
- Displays timeline if relevant
- Updates in real-time (you can watch it work)

### The Export
- HTML file downloads automatically
- Named with timestamp
- Open in any browser
- Print, share, or archive

---

## Troubleshooting

**Q: Nothing happens when I click Ask**  
A: Check internet connection, refresh page, try again

**Q: Export doesn't download**  
A: Check browser's download settings, may need to allow downloads

**Q: Response seems generic**  
A: Be more specific in your question, include more context

**Q: How do I find my old exports?**  
A: Check your Downloads folder, they're HTML files named with timestamps

**Q: Can I use this on my phone?**  
A: Yes, works in any browser

**Q: Is my data private?**  
A: Nothing is stored on servers, everything is local to your browser session

---

## Important Reminders

**This is NOT:**
- Medical advice
- A diagnosis tool
- A replacement for doctors
- A treatment protocol
- A promise of outcomes

**This IS:**
- An organizational tool
- A way to write things down clearly
- A method for keeping track of observations
- A structure for preparing questions
- A system for not losing context

**Always consult with qualified healthcare providers for medical decisions.**

---

## Framework Context (Optional Background)

*The following is background on the design philosophy. You don't need to read this to use the tool effectively. Main instructions are above.*

### The Core Idea: discovery → artifact → receipt → repeat

**Discovery:** You notice something, have a question, observe a pattern

**Artifact:** You write it down (create an artifact)

**Receipt:** You get a response, result, or outcome (receipt of what you did)

**Repeat:** You continue this cycle, building understanding over time

This framework prevents:
- Losing track of what you tried
- Forgetting important observations
- Collapsing assumptions prematurely
- Rushing to conclusions without clarity

### Why This Structure

**Most health management tools are:**
- Symptom trackers (limited)
- Diagnosis engines (dangerous)
- Treatment protocols (prescriptive)

**This tool is:**
- A notebook that thinks
- An organizer that preserves context
- A structure that enforces clarity

**The goal is not to solve your problem immediately.**  
**The goal is to help you understand your problem clearly.**

### The Modes Explained (Deeper)

**ASK Mode:**
- Medical question answering
- Source-backed responses
- Transparent reasoning
- Export for verification
- Stream endpoint: `/ask_stream`

**CODING Mode:**
- Observation documentation
- Timeline construction
- Pattern recognition
- Context preservation
- Stream endpoint: `/coding_stream`

**EoH Mode (Ethos of Health Framework):**
- Values-aligned health reasoning
- Respects personal health philosophy
- Filters medical information through your lens
- Evidence-based but calibrated to your preferences
- Stream endpoint: `/eoh_stream`

**EoHD Mode (Ethos of Health Detective):**
- Multi-step orchestrated investigation via `/eoh_detective_stream`
- Timeline analysis and pattern recognition
- Diagnostic landscape mapping
- Treatment response analysis
- Comprehensive reporting
- Currently available by emailing timeline to dylan@2ndopinionmd.ai

### What "3Pi$73MiC87MLV4ULT" Means

**Translation:** Epistemic Vault

**Pronunciation:** Three-Pi-Seven-Three-Mic-Vault (or just "the tool")

**Why this name:**
- "Epistemic" = knowledge-related
- "Vault" = secure storage
- The numbers/symbols are stylistic (can be ignored)

**You can just call it "2OPMD" (2nd Opinion MD).**

---

## Contact & Support

**Questions:** Use the tool to ask (it can explain itself)

**Problems:** Email Dylan (if you have his contact) or ask Peter to forward

**Feedback:** Optional, not required, but welcome if you have thoughts

---

## Final Note

This tool exists because organizing health questions is hard. Scattered notes, forgotten observations, lost context—these are real problems that create real confusion.

**If this helps you think more clearly about your health, use it.**  
**If it doesn't, that's fine too.**

No pressure. No obligation. Just a tool, available when you need it.

**:repo-vision-cool** 😎

