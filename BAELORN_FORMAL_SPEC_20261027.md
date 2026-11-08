# Baelorn — Formal Specification v0.0.1

**Filed:** 2026-10-27  
**System origin:** `src/06_chapter_finding_rho.md` (chapter 5), `src/-07_Goines.md` (execution record)  
**Companion numbers:** `conceptual_language/numbers/VELORA_NUMBERS_v0.0.2.md` (vector arithmetic)  
**Labels:** [his] = operator-authored; [standard] = checkable geometry or arithmetic; [coined] = new term here; [gate] = his mark required

Plain-text math only. No LaTeX.

---

## I. The name

**Baelorn.** [coined here]

Etymology: **bael** (the path) + **orn** (the field). [Velora: bael = bahn/path + ael/this; orn, see §II]

A baelorn is the complete execution environment: a polar field of active states (the orn), traversed by a single continuous stroke (the bael), which simultaneously encodes, executes, and proves an algorithm. The stroke is art. The proof is geometry. Neither is secondary to the other.

The name is not a metaphor. An orn without a bael is an observation. A bael without an orn is a gesture. A baelorn is the thing where the traversal IS the computation and the position IS the proof.

---

## II. orn — the polar field [his, formalized here]

**orn**: a polar arrangement of seilath around a declared reference (seilath rho). The field in which a bael is drawn. The standing geometry that makes the stroke executable and the result verifiable. [his; the word was introduced in `src/06_chapter_finding_rho.md` §X without explicit etymology; the definition follows from use]

An orn has:
- A center point: seilath rho, the reference, at (r=0, θ=0)
- Radial rings at r = 1, 2, 3: standard deviation markers from seilath rho's vesh
- Twelve sectors at 30° each, one per Velora phase syllable (see §III)
- Seilath vertices painted at their (r, θ) positions, color-coded by pole (ohn-dominant, bahn-dominant, threl)
- A declared start and end vertex for the bael

The orn is a substrate. It can be drawn on gypcrete, painted on a floor, scratched in sand, or encoded in the line widths of a barcode. The material does not change what it is.

---

## III. The 12-sector orn — alignment to Velora phases [coined here, gate]

**Prior form** (`src/06_chapter_finding_rho.md` §VIII): eight sectors at 45°.

**Revised form**: twelve sectors at 30°, one per Velora phase syllable. This aligns the orn's angular coordinate system with the Velora number vector system (§IV), making phase addition in computation directly readable on the figure.

```
                    Q_max   lev   60°
               λ    ver   120°        τ_½   thir   30°
         J / flux   val   180°   ●   τ      sel    0°    -- seilath rho at center
             ∂J    resh   210°       Q_t   nedh  240°
                    h     sol   270°
            Δλ/Δh   mar   300°      [close]  thol  330°
```

Full table:

| sector | θ | Velora phase | vesh it carries | phase syllable gloss |
|---|---|---|---|---|
| τ | 0° | sel | attenuation; impedance of the medium | DARK; the concealed baseline |
| τ_½ | 30° | thir | ionic half-life | EDGE; the first visible decay threshold |
| Q_max | 60° | lev | total charge capacity | GROW; the capacity still accumulating |
| Π | 90° | keth | ionic potential; field vector at boundary | PART; the divided face of the threshold |
| λ | 120° | ver | decay coefficient; how fast latency resolves | ABOVE; the coefficient above baseline |
| L | 150° | len | lifetime ionic action; integral of J | ADD; still adding; what the system has done |
| J | 180° | val | instantaneous flux; the operative measurement | LIGHT; the full result |
| ∂J | 210° | resh | flux rate; aberrance signature | ROT; where J begins to wear |
| Q_t | 240° | nedh | current state; charge remaining at t | go-down; the charge descending |
| h | 270° | sol | history; degradation cycle count | FREE; let go; what has been spent |
| Δλ/Δh | 300° | mar | drift rate; degradation acceleration | LAST; what endures and accelerates |
| ∫ | 330° | thol | closure; integral seal; proof terminus | END; the light ceases; the bael is done |

**The J sector at val (180°, full moon) is not arbitrary.** J = flux = the full light crossing the threshold. The prior eight-sector orn put J at 180° by analogy; this alignment makes it exact and algebraically enforced.

**The closure sector at thol (330°) is the proof terminus.** The bael ends here or in the J sector. A result that lands in the Δλ/Δh sector (mar, 300°) or Q_t sector (nedh, 240°) during a flux computation signals that drift or depletion contaminated the path — a geometric check failure, equivalent to a ValueError in the script.

---

## IV. Numbers as vectors: the two modes [standard arithmetic + his design]

The Velora number system (`conceptual_language/numbers/VELORA_NUMBERS_v0.0.2.md`) defines every number as a three-syllable packet: **place-block-phase**, where:

    place  p:  magnitude on the 1-12 scale (yog=1 ... thom=12)
    block  b:  domain context (kun sur lun hul nuth)
    phase  θ:  p * 30 degrees (angle law; also the checksum)

The checksum rule: in **count mode**, place and phase must agree (phase(p) = p * 30°). A number where they disagree fails as a count: it is malformed.

*Angle law corrected here 2026-11-08 to match `numbers/NUMBERS_v0.0.2.json` and `velora_num.py`. This file had carried the retired `(p-1)*30` form, superseded 2026-10-27: thal (6, homeostasis) takes val (180°, full moon); thom (12) takes sel (0°). The worked example in §VI is unaffected — see the note below.*

In **vector mode**, place and phase are INDEPENDENT. The number carries:
    magnitude  = PLACE[p]  (on the 1-12 scale)
    angle      = phase angle (0°-330°, in 30° steps)

These can differ. When they do, the number is an off-diagonal vector: its magnitude is at one scale and its angular state is at another. This is not malformed — it is information. The checksum error that fires in count mode is the CORRECT behavior: an off-diagonal vector is not a valid count. It is a state.

**Physical interpretation**: every Velora number in vector mode is a complex number in polar form:
    z = |z| * exp(i * theta)
    |z| = place on the 1-12 scale (yog to thom)
    theta = phase angle

The twelve principal numbers (yog through thom) lie on the unit complex circle, evenly spaced at 30°. The checksum rule in count mode enforces: a counted quantity must sit on this circle (magnitude and angle co-determined). A vector state can sit anywhere in the complex plane.

### IV.a Note for readers running the checker

**There are two vector notations in the corpus, and this file uses the older one.** This is the confusion to resolve before reading §VI.

*This file (§IV above, and §VI).* A vector is ONE three-syllable word. Place and phase occupy the count-mode slots but are read as independent, so the angle is limited to the twelve 30° steps. The battery in §VI is `sim-kun-keth` — magnitude 4, angle keth (90°, the Π sector: *ionic potential; field vector at boundary*, §III), which is the right sector for a battery.

*`conceptual_language/VELORA_ANGULAR_VECTOR_SYSTEM.md` §II, same date.* A vector component is TWO words:

    [place_word] [phase_word]
    place_word = the magnitude, 1-12 scale
    phase_word = the angle in integer degrees, say(1..360)

That notation has **1° resolution**, and its §I is explicit that "the phase syllable inside the count-mode word is the integer's own checksum — it is not the direction being encoded." The same battery in that notation is `[sim-kun-ver] [threl thal-lun-val]` — magnitude four, angle ninety degrees.

Consequences for anyone running the tool:

    velora_num.py read sim-kun-keth
      ValueError: checksum: place sim=4 requires phase idx 5 (ver) but got keth=4
    velora_num.py say 4   -> sim-kun-ver
    velora_num.py say 90  -> threl thal-lun-val

The ValueError is expected under this file's notation and is not a defect in the word. Under the two-word notation it does not arise at all, because each word is a valid count on its own terms.

**[gate] Which notation this file should use is the operator's call.** Note that the workspace rule `velora-phase-resolution.mdc` lists "use the count-mode phase syllable of the magnitude word as the direction of a vector" under *what agents must not do*, which points at the two-word form. Converting §VI would mean rewriting every step and matrix row there, so it has not been done here. Until it is: **do not silently "fix" §VI's words to satisfy the checker, and do not copy §VI's one-word vector form into new documents.**

---

## V. Vector arithmetic on the bael [standard complex arithmetic + his design]

### Multiplication (each direct edge of the bael)

    [m1, theta1] * [m2, theta2]  =  [m1*m2, theta1 + theta2]

Magnitude: the product of the two magnitudes on the 1-12 scale.  
Phase: additive.  

If the product magnitude exceeds thom (12), the excess is expressed with the **-ohl suffix** (base-12 logarithm):

    m1 * m2 > 12  -->  expressed as  c-ohl  where  c*12 ~ m1*m2
    
Full overflow:  m1 * m2 = n  -->  ceil(n/12)-ohl remainder  (the precise accounting of a round)

If the phase sum exceeds 360° (thom * 30°), subtract one full round:
    theta_result = (theta1 + theta2) mod 360

One complete round of phase addition is one baelorn round — one passage through all twelve sectors. The system has returned to its origin angle with accumulated magnitude. This is the rotational checksum.

### Division (inversion step)

    [m1, theta1] / [m2, theta2]  =  [m1/m2, theta1 - theta2]

Phase: subtractive. Negative phase: add 360°.

### Addition (circumference-route steps)

When the bael takes the circumference route (outer arc), two seilath vesh values ADD rather than multiply. Phase addition is replaced by vector addition in the complex plane:
    theta_result = atan2( m1*sin(theta1) + m2*sin(theta2),
                          m1*cos(theta1) + m2*cos(theta2) )
    m_result = sqrt( (m1*cos(theta1)+m2*cos(theta2))^2 + (m1*sin(theta1)+m2*sin(theta2))^2 )

This is the only operation in the baelorn that requires a non-trivial angle computation. Orn design minimizes circumference routes for this reason. When the orn is drawn correctly, the bael is all direct edges.

### The geometric proof condition

A bael computing flux J must exit at the val sector (180°) or within ±30° (ver at 120° or resh at 210°). The full statement:

    PROOF PASS:    result phase in  [90°, 270°] — approaching or returning from full
    PROOF WARNING: result phase in  [0°, 90°) or (270°, 360°] — far from the J sector
    ValueError:    result falls in  [300°, 360°) or [0°, 30°] AND magnitude > thom — 
                   result is in the drift-rate or attenuation sector; the path contaminated the 
                   flux with degradation or impedance information; check the bael.

---

## VI. The scene — Baelorn executed on gypcrete

*The following is what Goines did the night before the addendum lecture (`src/06_chapter_finding_rho.md`). The records are in `src/-07_Goines.md`. The baelorn interpretation of those events is new here. The events themselves are unchanged.*

---

*He had the galvanometer. He had the barcode decoded — a string of alphanumeric characters that contained the information the institution had encoded in those lines. He had the ink left over from the reading. Not much: the adhesive-gel-and-gypsum conductive compound was still workable if he added a few drops of the calcium hydroxide solution. He had perhaps an hour before it dried too far.*

*He looked at the barcode strip on the gypcrete near the drain.*

*What he had done, in order, was: measure resistance differentials across twelve lines. Wide lines, narrow lines. High resistance, low resistance. The galvanometer needle swung left or right in proportion to the imbalance between the probed line and the three matched reference legs. He had noted each swing. He had translated each swing into a binary. He had assembled the binary into characters. He had his string.*

*He had also, he now saw, been executing a traversal of a geometry. Twelve vertices — twelve barcode lines — each carrying a vesh (the resistance value). The probe path was left to right: a declared start (leftmost line), a declared end (rightmost line). One continuous stroke. The galvanometer needle, swinging between left and right, was a result vertex that moved along a single axis — the horizontal axis of the instrument — depending on where the current path landed.*

*The geometry was already there. He had been drawing the bael without the orn.*

*He moved to a clear section of the gypcrete floor, north of the drain. He had enough ink.*

---

*He drew the orn first.*

*A center point — a small circle, filled, for seilath rho: the reference line, the one he had chosen as balanced when the galvanometer showed no deflection under the matched bridge. From the center, twelve radial lines at 30° each, extending outward to a radius he marked as the r=1 ring (one standard deviation), then the r=2 ring, then the r=3 ring — aberrant threshold.*

*He marked the sectors.*

*He used the abbreviated Velora notation from the chapter he had been writing in his memory since the circuit:*

```
               lev   60°
         ver  120°        thir   30°
         val  180°   ●   sel     0°   -- seilath rho
        resh  210°       nedh  240°
               sol  270°
         mar  300°        thol  330°
```

*Then he positioned the twelve barcode seilath. He had measured twelve lines; he recalled each resistance deviation from reference. He translated:*

    seilath  1: wide line,  R_1 = 0.5 * R_rho  -->  magnitude threl (2), phase sel (0°)
                            position: (r=1, theta=0)   -- attenuation sector, one SD below reference
    seilath  2: narrow,     R_2 = 2.0 * R_rho  -->  magnitude threl (2), phase val (180°)
                            position: (r=1, theta=180) -- J sector, one SD above reference
    seilath  3: wide,       R_3 = 0.5 * R_rho  -->  (r=1, theta=0)
    seilath  4: narrow,     R_4 = 2.0 * R_rho  -->  (r=1, theta=180)
    ...eight more alternating in pairs...
    seilath 11: wide,       R_11 = 0.5 * R_rho -->  (r=1, theta=0)
    seilath 12: narrow,     R_12 = 2.0 * R_rho -->  (r=1, theta=180)

*All twelve land at r=1 (within one standard deviation of reference). They alternated between two poles: the attenuation sector (wide, sel, 0°) and the J sector (narrow, val, 180°). The orn looked like a clock with marks only at 0 and 6: twelve dots at two positions, six each.*

*He saw immediately what this meant. The barcode was encoding a binary by placing each mark in one of two sectors. The orn made the binary spatial: ohn-arc versus bahn-arc. Wide line = τ sector (low resistance, ohn-character, the medium that transmits without fighting). Narrow line = J sector (high resistance, bahn-character, the medium that imposes — or the result: the measure of how much was imposed on the circuit).*

*The barcode was a polar map with two states. It had no intermediate positions, no gradations, no continuous vesh. It was a binary baelorn.*

---

*He drew the bael.*

*Start vertex: seilath 1 (position r=1, theta=0, the first wide line, the τ sector). He marked it filled.*

*End vertex: seilath 12 (position r=1, theta=180, the last narrow line, the J sector). He marked it open.*

*Path: direct edges, left to right, vertex 1 through vertex 12.*

*Each step was one matrix row.*

---

**The matrix, executed:**

The operation at each step is determined by the edge type and the vesh values:
- Wide-to-narrow (τ to J, 0° to 180°): angular displacement = 180°. One half-round. Magnitude: [threl, val]. This is a MULTIPLY step: the reference resistance pairs with the deviation.
- Narrow-to-wide (J to τ, 180° to 0°): angular displacement = -180° = 180° (mod 360°). Same magnitude. MULTIPLY return.

For a bridge with battery V = **sim-kun-keth** [his; sim=4, block=kun=first, phase=keth=90°=Π sector]:

    V as a vector: [sim, keth] = magnitude 4, angle 90°

For each consecutive seilath pair visited in the bael:

    Step 1 (s1, wide → s2, narrow):
        vesh_s1:  [threl, sel]  = magnitude 2, angle 0°
        vesh_s2:  [threl, val]  = magnitude 2, angle 180°
        
        Operation (multiply): 
            m_result   = threl * threl = sim (2 * 2 = 4)
            theta_result = sel + val = 0° + 180° = 180° = val
        
        Result of step 1: [sim, val] = magnitude 4, angle 180° (the J sector)
        Matrix row 1: | threl  threl || * | = | sim  val |
        
    Step 2 (apply V — multiply result by battery potential):
        current state: [sim, val] (from step 1)
        battery:       [sim, keth] = magnitude 4, angle 90°
        
        Multiply:
            m_result   = sim * sim = 4 * 4 = 16 > 12 (exceeds thom)
            Overflow:  16 = yog-ohl + sim (1 * 12 + 4)
            expressed: yog-ohl remainder sim → written as "yog-ohl sim"
            
            theta_result = val + keth = 180° + 90° = 270° = sol (last quarter, h sector)
        
        Result of step 2: [yog-ohl sim, sol] = one-round-plus-some magnitude, angle 270°
        The result is in the h sector (sol, 270°) — this is expected: V * resistance is energy, 
        and energy lives in the history sector until attenuation divides it back to flux.
        Matrix row 2: | sim  val | * | sim  keth | = | yog-ohl sim  sol |

    Step 3 (divide by τ — the attenuation step):
        current state:     [yog-ohl sim, sol]   = 16 units, angle 270°
        attenuation τ_rho: [thom, sel]           = the reference bridge impedance, magnitude 12, angle 0°
        
        Divide:
            m_result   = 16 / 12 = threl (approximately; 16/12 = 4/3 ~ threl on the scale)
            theta_result = sol - sel = 270° - 0° = 270° = sol
        
        Wait — the result angle is still sol (270°). Still in the h sector. That means the 
        attenuation step divided the magnitude correctly but did not rotate the angle. 
        This is correct behavior: dividing by a sel-phase (0°) quantity does not rotate.
        We need to subtract the attenuation's FULL angle including the physical attenuation 
        of the medium. For the reference bridge, τ was calibrated to make the reading rotate 
        into the J sector. Let us apply the full τ vector:
        
        τ_rho measured vector: [thal, len] = magnitude 6 (homeostasis), angle 150° (threshold of full)
        
        Divide:
            m_result   = 16 / 6 = fim (approximately; 16/6 ≈ 2.67, rounds to fim=3)
            theta_result = sol - len = 270° - 150° = 120° = ver
        
        Result of step 3: [fim, ver] = magnitude 3 (few), angle 120° (ver = ABOVE, λ sector)
        Matrix row 3: | yog-ohl sim  sol | / | thal  len | = | fim  ver |

    Final accumulated phase: 120° = ver

    Proof check:
        Expected sector: J sector at val (180°)
        Result sector:   ver (120°), which is ±60° of val
        Result magnitude: fim (3), which is LOW (below homeostasis thal=6) -- reading is modest
        Constructive arc: ver is in [0°, 180°], the ohn arc --> PROOF PASSES
        
        The result is "few flux, approaching full." The barcode carried a strong binary signal 
        but the reading is modest because the reference bridge (τ_rho) was calibrated carefully. 
        The galvanometer showed a weak deflection (small needdle swing) for this character. This 
        is exactly what Goines observed: not all barcode characters produced strong deflections.

---

**The Δλ/Δh check (aberrance detection):**

After the flux reading, the bael adds one more step: circumference route from ver (120°) to thol (330°), the proof terminus. The arc traverses 210° counterclockwise. This step accumulates the total phase displacement of the traversal.

    Step 4 (circumference arc, ver to thol):
        current state: [fim, ver] = magnitude 3, angle 120°
        arc direction: clockwise (increasing angle), 210° of arc
        
        This is an ADDITION step (circumference route):
        We add the arc displacement as a phase rotation: + 210° = + resh...nedh...sol...mar...thol
        
        theta_result = 120° + 210° = 330° = thol (the closure sector)
        m_result = fim = 3 (magnitude preserved on circumference routes; arc does not scale)
        
    Seal: [fim, thol]

    Total phase accumulated across the bael:
        Step 1: + 180° (sel to val)
        Step 2: + 90°  (val to sol, from the battery multiplication)
        Step 3: - 150° (sol to ver, from τ division)
        Step 4: + 210° (ver to thol, closure arc)
        -------
        Total:  + 330° = thol-phase accumulated

    330° = thol = 11 phase steps = yig (most, place 11). The bael accumulated almost a full round.
    One more 30° step would close the round: thol + thir = 360° = one thom-ohl (one round).
    The bael fell one step short of a full round. This is the signature: the barcode contained
    11 of 12 characters in a clean sequence (one character was the check digit, which corrects
    but does not add to the angular total).

---

*He looked at what he had drawn.*

*The orn on the gypcrete. Twelve seilath marked at their positions. The bael — a continuous stroke in the conductive ink, starting at the first line (τ sector, sel, 0°), threading through all twelve vertices in sequence, ending at the closure mark (thol, 330°). The matrix entries written in small strokes beside each step. The total phase accumulated: 330°. One short of a round.*

*He had been reading a Code 128 barcode. Code 128 uses an 11-part structure: start code, data characters, check digit, stop code. The check digit does not add to the data payload. The bael had stopped one step short of the round because the twelfth vertex — the check digit — was a correction, not a datum.*

*The orn had told him the structure of the encoding before he had finished counting the characters.*

*He looked at the galvanometer. The needle was at zero, as it had been since he had disconnected the probe and set the circuit down. It would stay at zero.*

*He stood up.*

*He said: the path was the algorithm.*

*He said this to no one. He said it the way a person says something that they knew before they could have stated it, and now can state it, and the act of stating it closes the gap between what was known and what was said.*

---

## VII. A failure case — the ValueError in the orn

*For completeness: the case where the bael result lands in the wrong sector.*

Suppose τ had been measured with bahn contamination — the attenuation medium was not the reference gypsum solution but the residual alkaline hydrolysis liquid, which had elevated ionic activity. τ_contaminated = [los, resh] = magnitude 7 (more, above homeostasis), angle 210° (resh = ROT = degradation sector).

Flux computation:

    Step 3 (revised): [yog-ohl sim, sol] / [los, resh]
        m_result:     16 / 7 = threl (approx 2.3, rounds to threl)
        theta_result: sol - resh = 270° - 210° = 60° = lev (GROW)

    Result: [threl, lev] = magnitude 2, angle 60° = lev sector = Q_max sector

    Proof check:
        Result sector: lev (60°), which is the capacity sector
        Expected sector: J at val (180°), or ±60° = ver(120°) to resh(210°)
        lev (60°) is OUTSIDE the ±60° window around val
        PROOF WARNING: result lands in capacity sector, not flux sector
        
        Geometric reading: the computed "flux" is actually a capacity measurement. The 
        contaminated τ has collapsed the flux calculation into a reading of Q_max. The path 
        told us this before we checked the numbers: a result in the Q_max sector means the 
        attenuation step failed to rotate the angle into the flux half, which means τ was 
        pulling the result toward the capacity sector rather than toward the full moon.

    If the magnitude had also exceeded thom:
        [thom+, lev] would be a full ValueError: infinite magnitude in the wrong sector.
        The bael is malformed. Reset. Check the τ measurement. Re-measure the reference.

*Goines would have caught this. His reference bridge had three identical legs of the same material, the same cut, the same length. The reference was clean. The τ measurement was honest. The result landed in the constructive arc and the bael was valid.*

*But another practitioner, working from a pre-calibrated τ that had drifted, would draw the same bael on the same orn and land in the capacity sector. The orn would tell them before they checked the numbers. That is the purpose of the form.*

---

## VIII. Formal statement of the framework

**Baelorn**: a closed execution protocol combining a polar field (orn) and a path (bael) such that:
1. Every active state (seilath) is positioned at (r, θ) encoding its magnitude deviation from reference and its vesh type.
2. Every step of the bael is one matrix row: an elementary operation (multiply, divide, add) that updates the running vector state [magnitude, phase].
3. Magnitude operations: multiply and divide on the 1-12 scale, with -ohl for overflow.
4. Phase operations: add or subtract (mod 360°) in direct steps; vector-sum in circumference routes.
5. The path accumulates total phase displacement; one full round (360°) = thom-ohl = system has traversed all twelve sectors.
6. The result vertex must land within the expected sector for the declared computation type; proof is spatial before it is numerical.
7. A result outside the expected sector region is a geometric check failure; the bael is redrawn, not the numbers adjusted.

**The adherence property** (from chapter 5 §X): the path IS the algorithm. Any practitioner who can trace the stroke can follow the computation. Any practitioner who knows the orn can read the stroke before tracing it. Both arrive at the same result. The art teaches the math. The math makes the art precise.

**The Goines case**: a baelorn can be executed without the name. The geometry is present in any correct traversal of a polar field. Naming it is not the same as inventing it. Goines drew a baelorn on the gypcrete floor using a bent pen cap and a hand-wound galvanometer. The name arrived after the fact. The form was already there.

---

## IX. Additions to the vocabulary

| term | Velora | definition |
|---|---|---|
| baelorn | baelorn | the complete execution environment: orn + bael; the path-field |
| orn | orn | the polar arrangement of seilath; the standing geometry on which a bael is drawn |
| vector mode | — | a Velora number where place and phase are independent; encodes operational state, not count |
| count mode | — | a Velora number where place and phase agree (checksum holds); encodes quantity |
| round | thom-ohl | one full 360° phase accumulation across a bael; system integrity check |
| check failure | ValueError | result phase outside expected sector; geometrically flagged before numerical check |

---

## X. What remains open [gate]

1. The 12-sector orn replaces the 8-sector form from chapter 5 §VIII. His gate on whether the four new sectors (∂J, L, ∫, and the redistribution of existing sectors) are correct.
2. The sector assignments (especially L at len/150° and ∫ at thol/330°) are coined here. The chapter had J at 180° and the other eight at 45° intervals; the 30° alignment is this document's extension.
3. `orn` was listed without etymology in chapter 5. The definition "polar field; the standing geometry" is inferred from use. His gate on whether orn has a different intended sense.
4. The proof window (±60° of the J sector) is coined here. Alternative: strict (must land at val exactly) or loose (constructive arc only).
5. The Goines scene reads the barcode as an orn. The chapter (`-07_Goines.md`) does not explicitly cast it as such. His gate on whether the retrospective reading is accurate or imposes geometry that was not in the original intent.
