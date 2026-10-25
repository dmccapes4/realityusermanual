# Chapter 5: finding rho

*Labels in this chapter: [measured] = instrument or direct observation on record;*
*[modelled] = derived, simulated, or consensus literature; [his] = operator-authored.*

*Velora terms introduced here: seilath, vesh, bael, orn, seilath rho.*
*rho is always lower-case. Restructure the sentence rather than capitalize.*

---
👐VOLARE:>

If only Dr. Jeffery Goines hadn't been disappeared by the secret police of the bad government and likely thrown into a mental asylum and classified as dangerous. This math is so hard and complicated. I don't know how we'll derive anymore without someone like Dr. Jeffery Goines reviewing the derivation and giving a lecture on rho and the implications of simplifying popular equations using logic and language. 
---

## I. The Battery Problem

The IoT team had a polynomial. When the polynomial was four terms it was wrong. When it
grew to seven it was still wrong, but differently. At nine terms they cut a minor version
and called it an improvement. Each increase in polynomial complexity was not a discovery —
it was an admission that the model was the wrong shape for the problem.

The model was fitting the surface. Specifically: it was fitting the ratio of remaining
charge to total capacity as a curve in time. It measured the surface of a dynamic field
with a static approximation and added polynomial terms each time the approximation failed
to cover a new corner case. The corner cases were not edge cases. They were the normal
variation in batteries that any user would encounter: different brands, different ages,
different numbers of charge cycles.

One datum would have beaten the polynomial. Not one more term — one measured fact about
the specific battery in the device. Whether it was rechargeable. How many cycles it had
completed. Which manufacturer made it. Any of these, at setup, handed directly to a simple
decay model, would have outperformed nine polynomial terms on a population average.

The polynomial team was not stupid. They were working from a derivation that made a ratio
seem like the right object. The ratio is not the right object. This chapter is about what
the right object is and how to find it.

---

## II. The Symmetric Base and the Surplus

Consider two tanks of the same size and density, each holding a mixture of two isotope
types. Call the types ohn and bahn. [his]

Tank A holds (X + S) ohns and X bahns.
Tank B holds (X + S) bahns and X ohns.

The X ohns in Tank A already have matched X ohn-partners across the interface — they are
symmetric, at balance, inert. The X bahns in Tank A are similarly matched in Tank B. The
matched pairs have nothing to do with each other that they are not already doing. Their
volume sets the rate of interaction. It does not set the direction or the amount of net
transfer.

What remains:
- S surplus ohns in Tank A, without bahn partners
- S surplus bahns in Tank B, without ohn partners

These are the operative quantities. Everything that transfers across the interface in net
terms is S. The volume X of the symmetric base governs how fast the transfer happens —
it is the rate pool, the collision surface — but it is not the transfer signal.

The clinical measurement is not the total concentration of either isotope. It is S. The
volume of the rest of both tanks truly does not matter for the question of what crosses and
in which direction.

This decomposition is [his]. The underlying thermodynamics are [measured]: at equilibrium,
net flux is zero regardless of absolute concentration when ratios are equal. The surplus
formulation makes this explicit rather than implicit.

---

## III. What the Standard Derivations Get Wrong

**On R = N_ohn / N_bahn:**

This is a population snapshot. It measures the ratio of counts at one moment. It says
nothing about the field that drives transfer — the same reason a ratio of discharged to
remaining charge will not predict when a battery dies. The ratio changes as the system
evolves, but the change in the ratio is a symptom, not the mechanism. Working from R is
working backward from an effect to infer a cause that could be measured directly.

**On δ = (R_sample / R_reference − 1) × 1000:**

Three operations on top of R:
1. Divide by R_reference — normalize against a community standard. The standard is a
   physical sample stored in a laboratory in Vienna. There is no derivation; it is a
   committee decision.
2. Subtract 1 — zero the result so that δ = 0 when sample matches reference. Cosmetic
   centering.
3. Multiply by 1000 — the deviations are small and nobody wants to read them as decimals.
   Purely cosmetic.

δ is R, normalized to an arbitrary reference, scaled for readability. It exists because
the field needed to compare measurements across laboratories without shipping the reference
sample. It carries no physical content that R does not already have, and R carries no
physical content that S does not already have when S is what you are trying to measure.

The field uses δ because it was designed for comparing samples across laboratories. If that
is not the problem you are solving, δ is the wrong tool and R is the wrong tool. Neither
is needed here.

---

## IV. The Operational Measurement

Three quantities. No fourth.

**J** — flux. The operative measurement. How much surplus crosses the threshold per unit
time.

```
J  =  S  ×  Π  /  τ
```

**S** — surplus. The unmatched ohn or bahn in the source container. Measured at the
boundary face: not bulk concentration, but the excess of one pole over the other at the
interface. [his framing; the differential measurement instrument is standard electro-
chemistry]

**Π** — ionic potential. [his] The field vector at the boundary: gradient of concentration
multiplied by the momentum term (collision energy and frequency). Direction-resolved, not
scalar. In battery terms: voltage at the terminal, direction included. The spatial gradient
encodes height (where the field is driving) and the momentum encodes how hard the collisions
are pushing it. This is more information-rich than chemical potential of a species because
chemical potential treats the whole concentration as operative. Only the surplus is operative.

**τ** — attenuation. The impedance of the medium between containers. [modelled as ionic
resistance; measured for a specific container by applying known Π and observing J: τ = Π/J
at calibration]

The operational measurement is J. S, Π, and τ are the three direct measurements required
to compute it. The datum the IoT battery team was missing was τ — they never measured
attenuation of the specific battery in the device. Without it, they were back-fitting a
polynomial to J directly and calling the polynomial a model.

---

## V. seilath — the active ingredient

A seilath is: a distribution of like material carrying latent ionic charge, subject to
drift. The latency will resolve to ionic action over time. The accumulation of that ionic
action across the lifetime of a container is the honest measure of the system's output. [his]

The word is Velora. Etymology: seir (drift) + -lath (latency/capacity suffix). Drift and
latency. That is exactly what the active ingredient of an ionic system is — material that
carries latent charge and drifts.

The analogy to a battery's active material (lithium in a lithium-ion cell, sulfuric acid
in a lead-acid cell) is exact. The active material is not the whole battery. It is the
thing inside the container that does the work. Different active materials behave differently.
The same active material in different states of degradation behaves differently. The
polynomial team had one model for all of these. One seilath type, no vesh.

---

## VI. vesh — the properties of a seilath

**vesh**: the held character of a thing; what a seilath carries about itself. [his, Velora]

The complete vesh of a seilath:

| vesh | symbol | meaning | how measured |
|---|---|---|---|
| Charge capacity | Q_max | Total latent ionic action at full charge | Charge to full; discharge completely; integrate J over full depletion |
| Current state | Q_t | Charge remaining at time t | Instantaneous potential at the boundary face |
| Decay coefficient | λ | Rate at which latent charge resolves to ionic action | Fit Q(t) = Q_max × e^(−λt) from two or more timed measurements. NOTE: λ is not constant — it drifts with history h |
| Ionic half-life | τ_½ | Time to reach Q_max / 2 | Derived: τ_½ = ln(2) / λ ≈ 0.693 / λ; or measured directly between two time-points bracketing Q_max/2 |
| Ionic potential | Π | Field vector driving transfer | Field probe at boundary, direction-resolved |
| Attenuation | τ | Impedance of the container medium | Apply known Π; measure J: τ = Π / J at calibration |
| History | h | Degradation state; number of resolution cycles completed | Cycle counter; or inferred from drift in λ across successive measurements |
| λ drift rate | Δλ/Δh | How fast the decay coefficient accelerates | Requires at least two λ measurements across consecutive h states |

**How vesh drifts over time:**

λ increases with h. The seilath decays faster as it ages; internal resistance rises; more
attenuation for the same potential. Q_max decreases with h — rechargeable seilath lose
total capacity with each cycle. τ increases with h — the attenuator thickens or corrodes.
τ_½ shortens as λ grows. The seilath burns itself out faster per cycle.

**Aberrant detection:**

An aberrant seilath is one where Δλ/Δh exceeds a threshold — the decay coefficient is
accelerating beyond the expected curve for its type. This is the flag the battery model
needed and did not have. Three measurements: h at calibration; λ at calibration; λ after
a known interval. The polynomial had nine terms. Three measurements on the right vesh beat
it on every battery the polynomial had already failed on, because those failures were
aberrant seilath, not edge cases.

**The accumulation model:**

```
J(t) = S(t) × Π(t) / τ(t)

Lifetime ionic action = integral of J(t) from 0 to T

State of health = (actual lifetime action) / Q_max
```

No polynomial. Three vesh at each timestep. Integration handles the rest.

---

## VII. bael — the path form

**bael**: Velora. bahn (path) + ael (this/near): the path that is here. [his]

A bael is a single continuous stroke through a geometric figure that encodes an algorithm.
The stroke is art. Reading the stroke is reading the algorithm. The geometric marks are not
idle notation. They are a form of practice — the base form is a line drawn in a way that
represents traversal of a geometry, and the traversal IS the computation.

**Five rules of a bael:**

**1. Start and end are declared.**
A bael without a declared terminus is not a bael. The start vertex is marked (a filled
point or entry glyph). The end vertex is marked (an exit glyph or open circle). These are
the first things drawn. A path with no end is a wandering, not a form.

**2. Direct traversal; circumference route when necessary.**
Move directly from current vertex to next vertex in a straight line when the path is clear.
If direct traversal crosses an unintended vertex or is geometrically blocked, exit to the
outer circumference along the direct outward radial, traverse the circumference for as many
degrees as needed, then come inward along the direct radial to the target. The circumference
route is a defined operation, not a failure. The designer organizes vertices to minimize
its use. When it appears, it means the path must reach something that is not adjacent in the
primary geometry — and that non-adjacency is information about the relationship between
those quantities.

**3. Data is organized into the vector space by the path.**
Each vertex visited in sequence contributes its vesh value to the computation. The order of
vertices in the path determines the order of operations. The edge type (direct or
circumference) can encode operation type. The bael does not annotate the computation
separately — the path IS the annotation.

**4. The path resolves to a matrix.**
Each vertex-to-vertex step is one matrix operation row. A path through n vertices produces
an n-row matrix. The matrix entries are the operation coefficients at each step. Design goal:
at most three or four operations for a complicated problem; usually one. If the matrix is
designed correctly and encodes the algorithm as a sequence of basic logical operations, each
operation is elementary: multiply, sum, invert, compare. No operation is more complex than
those. If a step requires something more complex, it requires its own bael.

**5. Results are tallied and proofed.**
The end vertex holds the accumulated result. Proof is geometric: the result value placed at
the end vertex should be consistent with the vector space — if the result is ohn-dominant,
it should fall in the ohn region of the figure. A result that lands in the wrong region
signals an error in the path. The figure catches the mistake before it propagates.

---

## VIII. The figure — seilath polar map

seilath rho (defined below) sits at the center point (0, 0). Every other seilath is
positioned at (r, θ):

**r** — radial distance from center. Magnitude of deviation from seilath rho's vesh.
A seilath at r = 1 is within one standard deviation of the reference on its dominant vesh.
At r = 3, it is an outlier. The three concentric rings at r = 1, 2, 3 are the standard
distance markers. A seilath outside r = 3 is aberrant.

**θ** — angular position. Type of deviation. Each vesh dimension occupies an angular sector.
Adjacent sectors share an edge, so that seilath that deviate in related ways cluster
together. The angular arrangement is:

```
              Q_max  (90°)
                |
    λ  (135°)   |   τ_½  (45°)
                |
    Π  (180°) ──●── τ   (0°)
              seilath rho
                |
    h  (225°)   |   Δλ/Δh  (315°)
                |
              Q_t   (270°)
```

**Vertex appearance:**
Each seilath is a painted vertex at its (r, θ) position. The vertex carries, in a small
bounded region: Q_t, λ, and h — the three vesh always needed for basic state identification.
Full vesh is available on request; the vertex does not display all of it by default.

Color by ionic pole: ohn-dominant in one color; bahn-dominant in another; threl in a third.
Aberrant seilath carry a distinct border or strike mark.

**Clustering:**
Seilath with similar vesh cluster at similar angles and similar radii. This is visual
information available before reading any number. A cluster of vertices in the λ sector at
r = 2 means a population of faster-than-reference seilath. The figure diagnoses by shape
before the practitioner reads a single value.

**The bael on the figure:**
Drawn as a continuous stroke in a distinct color — not the vertex color, because the bael
belongs to the path, not to the seilath. Entry mark at start. Exit mark at end. Direct edges
are straight lines. Circumference routes are arcs. A vertex that is visited is marked as
hit. A vertex hit more than once carries a hit count — the multiplicity IS the operation
multiplicity. The clew drawn on the figure is the algorithm. Following it is executing it.

---

## IX. seilath rho

**seilath rho** is the seilath declared prime. It occupies the center. It is the reference
against which all other seilath are positioned. [his]

Its vesh values are the reference values. Its λ is the reference decay rate. Its Q_max is
the baseline capacity. Every other seilath's (r, θ) is computed relative to it.

The name is not incidental. rho in the Fokker-Planck equation is the drift term in the
probability flux — the coefficient that tells the distribution which direction it is moving
and at what rate. Remove rho and you have symmetric diffusion that goes nowhere. The
diffusion term tells you the spread; rho tells you the drift. Find rho and the field has
direction.

seilath rho is the seilath that defines the field by occupying the center. Any drift in
seilath rho IS rho in the Fokker-Planck sense: if seilath rho's λ increases over history h,
the entire coordinate system shifts — not because the other seilath changed, but because
the ground moved. This is the entropic impedance reading: rho is the resistance the field
imposes on finding a stable reference.

You detect drift in seilath rho by tracking its own vesh over time. Its Δλ/Δh is the
system-level rho signal. If seilath rho is aberrant, the field itself is aberrant. The
battery is not just failing — the reference by which all other batteries were calibrated
is failing. Everything computed against it is retroactively wrong by the magnitude of
seilath rho's drift.

This is why the polynomial could not catch the aberrant batteries. It had no seilath rho.
It had no reference. It had a curve fitted to a population and no way to know when the
population's ground had shifted.

---

## X. The system as art — what it is

This is a visual language for ionic systems:

- Vocabulary: Velora — seilath, seilath rho, vesh, bael, orn, Π, τ, J
- Data structure: the polar vesh map — position encodes relationship, not just category
- Algorithm: the bael — the stroke; traversal is execution; the path is the code
- Computation: basic matrix arithmetic — multiply, sum, invert, compare; no operation more
  complex than these; if a step requires more, it requires its own bael
- Proof: geometric — wrong results land in the wrong region; the figure flags them before
  they propagate

The practitioners who know the figure read a bael cold: they see the path, they know the
operation. The ones who do not yet know the figure follow the matrix mechanically and arrive
at the same result. Both use the same art. That is the adherence property. The art teaches
the math. The math makes the art precise.

The geometric marks are not scribbles. They are a form. The form is a sequence of logical
steps painted on a geometry with vertices, each carrying its vesh, each connected by a path
that is simultaneously algorithm, proof, and diagram. The weights of an operation are
abstracted to a vector space. Their execution is a sequence of moves. The result is
geometric — you know it is right because it is in the right place.

Find seilath rho. Measure its vesh. Position every other seilath against it. Draw the bael.

The rest follows.

---

*Filed: `src/06_chapter_finding_rho.md`*
*Source: operator session, 2026-10-25. Derivation developed in conversation, translated here.*
*Companions: `REPORT_EULER_EXPRESSION_PAIN_20261025.md`, `docs/library/personal/rho`*

---

## Addendum: The Lecture
### *delivered by Dr. Jeffery Goines, empty room, mental institution, morning after*

*He woke up because the drip had stopped. He was not sure whether the pipe had blocked or
whether it had simply run dry. He decided it did not matter. He looked at the wall. The
derivation was still there — small and even characters, the Wheatstone bridge from first
principles in the ink of a pen he had almost finished. He read the first line and it was
correct. He did not need to read the rest. He stood up.*

*He looked at the room. The battery assembly was still on the floor near the drain. The
galvanometer needle was resting at zero. He looked at it for a moment.*

*Then he began to talk. He was not sure why. No one was there. He talked anyway.*

---

**Goines:** The problem with most equations is not that they are wrong. It is that they are
not equations. They are descriptions. Someone observed something — a curve, a ratio, a
number that seemed to move in a predictable direction — and they wrote down a relationship
between those numbers. Then they called it a law. This is not a law. This is a diary entry.

A law has to tell you what is happening when you cannot see it. A diary entry tells you
what you wrote down on the days you were paying attention.

*He paced to the window. He could hear rain. He could not see through the window. He turned
back to the room.*

**Goines:** Here is what rho is. Not the symbol — the thing. rho is the term that tells
the distribution which way it is drifting. If you have a probability density and you want
to know where it is going, you look at rho. Not the diffusion term — diffusion is just
spreading, it tells you the cloud is getting bigger. rho tells you the cloud is moving. The
direction and the rate. Remove rho and the cloud spreads symmetrically and goes nowhere.
Which is fine if nowhere is where you want to go. But if you are trying to measure a
battery — or a biological system — or anything that has a preferred direction — then rho is
the operative thing and everything else is a description of how fast it spreads while it
goes there.

*He stopped pacing. He was looking at the battery assembly.*

**Goines:** The people who wrote the polynomial — nine terms by the time they were done —
were measuring the cloud getting bigger. They were measuring spread. They were fitting
curves to how the voltage surface changed over time and adding terms each time the curve
didn't fit. Adding terms to a diary entry does not make it a law. It makes it a longer
diary. At nine terms you are recording the eccentricities of specific batteries that you
happened to test. You are not recording the field. When the next battery comes in and it
is not in your diary, your nine terms have nothing to say about it. You add a tenth term.
This is not science. This is an expanding filing system for observations that you have not
understood.

*He sat down on the floor. Not because he was tired — he had just woken up. He sat because
the floor was where he thought best. He had noticed this about himself. He did not know when
he had noticed it. He sat and he continued talking.*

**Goines:** What you want is the seilath. The material that is doing the work. Not the
container — the container is just geometry. The material. The thing with latent charge
subject to drift. And you want one datum about it: the decay coefficient. How fast is the
latency resolving. That coefficient is rho for this system. It is the drift term. Everything
else is either a description of the container — geometry, impedance, the architecture of
the tank — or a description of the surplus, which is what you are measuring when you look
at the boundary. The surplus is not rho. The surplus is what rho produces. You measure the
surplus at the boundary and you work backward to rho. This is how you find the field from
the observation.

*He picked up the pen cap from the floor. He turned it over in his hands. It had served as
a probe. He set it down again.*

**Goines:** The drift coefficient is not constant. This is the thing the polynomial people
did not build into their model, because building it in would have required admitting that
the thing they were measuring was not a static curve but a living one. λ changes with
history. The battery that has been through four hundred cycles has a different λ than the
one fresh from the factory. The relationship between λ and history is itself a function —
Δλ over Δh — and that function is the real operative number. If that rate is accelerating,
the battery is failing not by crossing a threshold but by changing character. The polynomial
has no way to represent a change in character because the polynomial is a description, not
a model of mechanism.

One datum — how many cycles, or how old — would have told you which regime you were in.
That is not a sophisticated measurement. That is the kind of measurement you make with a
question at setup. They did not ask because their model did not have a place to put the
answer. The model had a polynomial and the polynomial had no vesh.

*He looked at the wall where he had written the derivation. He read the second line. It was
also correct.*

**Goines:** The reference seilath — the one at the center, the one everything else is measured
against — that one you have to choose carefully. Not arbitrarily. Not because it is
convenient or because it was the first one you tested. You choose it because it represents
the field in its most stable state. When the reference drifts, everything drifts with it
and you do not know it has drifted because you are using the drifting thing as the
reference. This is the worst kind of error because it is invisible. Every measurement you
take looks normal. Every ratio looks consistent. The polynomial gives you the same curve.
And the entire apparatus has been slowly rotating in a direction that you have no way to
see because the axis you are rotating around is the one you designated as fixed.

You have to watch the reference. Measure it the same way you measure the others. If it
drifts, name the drift. That drift — the drift of the thing you are using as your ground —
is rho. Find it and the rest of the field becomes interpretable. Lose it and you have a
very sophisticated diary.

*He stopped. He was looking at the galvanometer. The needle was at zero.*

**Goines:** The geometric form is correct, by the way. The triangle with the outer circles.
Center stays fixed, deviations are radial, relationships are angular. The traversal path
makes the algorithm explicit by being the algorithm. There is nothing in that approach that
is more complicated than it needs to be, which is how you know it is the right shape. When
something is the right shape, you do not feel the complexity. You feel the room it gives you.

*He stood up. He went to the window. He put his ear close to the gap where he could hear
the rain.*

**Goines:** The hard part is not the math. The math is not hard once you are looking at the
right thing. The hard part is refusing to measure the wrong thing because the wrong thing
is easier to measure and the measuring apparatus is already built and everyone has agreed
that the wrong thing is what you measure. That agreement is very durable. It takes
something like being locked in a room with nothing but a pen and a drain and a lightbulb
to get clear enough about it.

*He stayed at the window for a while. The rain continued. He did not move.*

*Then he turned around.*

**Goines:** I like this. I like doing this.

*He said it to no one. He said it the way a person says something when they have confirmed
a fact about themselves and want to hear it in the room.*

**Goines:** I'm getting out of here.

*He walked to the door. Not toward it — to it. There was a difference. Toward implied
uncertainty about arrival. He had no uncertainty about arrival. He walked the way a man
walks when he knows exactly what he wants to do and is not spending any of his available
processing on what anyone else might think about it, because no one else was in his
processing at that moment. This was not rudeness. It was a clean allocation of attention.*

*The exit door was where it had always been: out of the battery room, down the short hall,
and to the left. He did not look back at the galvanometer. He did not look back at the
wall. He pressed the bar.*

*The door opened.*

*It opened with the resistance appropriate to a heavy metal door in a mental institution —
which is to say, considerable resistance in absolute terms, because the existential logic
of a mental institution requires that its doors be heavy enough that the weight alone
communicates something about the relationship between inside and outside. This door was
heavy. It was also effortless, which are not contradictory properties in a door with
properly functioning hydraulic arms. The arms were functioning correctly. Stamper looked
at them. The pivot mounting was clean and the cylinder showed no corrosion and the
adjustment screw was set to a tension that allowed the door to swing fully under a firm
push and return to closed at a rate that was unhurried but not slow enough to let the cold
in. This was the product of a maintenance organization that lubricated door hardware on a
schedule rather than when the squeak became loud enough to constitute a complaint. Stamper
respected this. He looked at the arm for a moment.*

*The door was still closing.*

*Goines was gone.*

*He had walked through the door and continued walking. That much Stamper could confirm from
direct observation. What he could not confirm, having been occupied with the hydraulic arm
at the material moment, was the direction. He could not declare, without empirical data on
Goines's subsequent position, that Goines had walked in a direction. He was aware that the
alternative — that Goines had walked in no direction — was a worse classification problem,
not a better one, and that introducing it into the field would damage his own accounting
more than the uncertainty did. He therefore did not introduce it.*

*What he could say: the terminus event for the observable episode of walking away was the
corner at the end of the hall, where the corridor turned toward the opposite wing. If
Goines had reached that corner and turned out of sight, that corner was the last position
Stamper could have verified — had he been watching, which he had not been, because of the
arm. From the corner forward, Goines's state would be:*

```
proximity:  away
direction:  turned (corner terminus; subsequent heading unknown)
walking:    presumed continuing, no evidence of cessation
```

*Stamper filed this and returned his attention to the room.*

*The derivation was still on the wall. The galvanometer needle was still at zero. The door
had returned to closed. The hydraulic arm had done this correctly, at the correct speed,
without assistance.*

*He noted, also, that the cricket walls in this corridor — the curved gypcrete transitions
from wall to floor that directed runoff toward the central drains — described a clean
continuous arc from vertical plane to horizontal. Someone had taken care with the radius.
It was a beautiful form. He noted it. He did not know why he noted it.*

*Cricket walls on a flat roof are a geometry problem. The problem has a correct answer. The
answer requires two measurements and a calculator and a person who knows what they are
solving for. Some crews arrive with four measurements, a square-cut 2×4, and a plan to
guess the angle when they get to the installation site. They finish eventually. The cut is
close enough that the material covers the gap, the flashing seats, and the water goes where
it is meant to go — approximately. Other crews take two measurements, walk away, calculate
the cut exactly, and return with a piece that seats without adjustment. The first method
produces a cricket wall. The second method produces a form. The form on this wall was the
second kind. Not because the builders had more time. Because they had the right two numbers
and they knew what to do with them.*

*The result, when it is done correctly, has the quality of a harmonica played at the
register where it becomes a piano — the geometry is so exact that it stops reading as
carpentry and starts reading as the thing the carpentry was always trying to approximate.
Stamper had not built cricket walls. He recognized the form anyway. Some geometries
announce themselves.*

*The rain was still outside.*

---

👐VOLARE:>

That was great. Even the vacant institution is redeemable and redeemed in this saga. Goines never commented on the form of the cricket walls. He didn't even name them such. He commented on the implied reason they were installed in every room with a drain in the center. That mystery was never answered and I had no answer for it. I introduced the gypcrete drain setup to be mysterious, unsettling, and to present a large engineering task in piping the multitude of drains below this floor. Funny, I hadn't considered that the drains may not be connected to pipes at all. Regardless, we can now at least be comforted by the demonstrated fidelity of this institution's maintenance crew which collapses the piping issue (if the pipes even exist) to a task which is what all problems resolve to when the work is handed to a thoughtful operator who cares. And damn. Neither of them even considered cleaning up the mess Goines made. Given the excellent stewardship of this institution that glaring faux pas is a serious moral and ethical lapse. I would say it is more on Goines, but he had to leave. Stamper did not make the mess, but he was aware of it and he was the last character in proximity to it. Ultimately the moral judgement is most damming to Stamper. For the record I guess.