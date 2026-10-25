# Page −07 — Goines, Jeffery

---

The first thing he noticed was the drip.

Not the floor against his cheek — that came a moment later, the slow understanding of a surface that was not comfortable and had not been designed to be slept on. Not the light, which was a single incandescent bulb on the ceiling, too high to reach and too far to read by with any precision. Not the window, which was tall and thin and appeared to be transparent but was not, or was, or was something else — its frame was rotting at one corner where a gap had opened, not large, maybe two millimeters, and through that gap the outside was audible and wet and continuous.

The drip. That was first. It fell on his cheekbone at irregular intervals that were close enough to regular to be maddening. He lay there and received it until the maddening quality had passed into something more like information: the rain outside was steady. The gap in the frame was fixed. The drip rate was therefore a function of the gap geometry and the outside precipitation rate. He could not use this to determine how long he had been on the floor. He noted it and sat up.

The floor sloped.

Not dramatically — if you stood in the room and tried to feel the slope through your shoes you might not catch it. But lying with your cheek on gypcrete you noticed things. The floor angled toward the center of the room, toward a drain inset flush with the surface, covered by a steel grate that was bolted down. Every room, he would find. He hadn't checked all the rooms yet but he would find, when he did, that every room on this floor had the same drain in the same relative position and the same subtle gradient leading to it. An architect had specified this. An engineer had signed off. A contractor had poured gypcrete at the correct angle in every room on this floor of this building.

He sat with that for a while.

The volume of fluid that would need to be expelled from this space, in any location within any room, at sufficient frequency to require a drainage solution in every room — he did not finish the thought. He filed it instead. The drains were operational in nature for this building in particular. They were also convenient to piss in. His view of the drains was mixed.

He looked at his ankle.

The anklet was medical-grade plastic, white where it had not yellowed, and it fit the way things fit when they had been put on by someone else and checked rather than adjusted. On one side: text. Institution name, which he read and did not recognize. Below that: *Goines, Jeffery.* A comma separating the last from the first, which was the clinical convention. Below that: a string of metadata he read without yet understanding. On the other side: a barcode. Narrow and wide lines in sequence, meaningful in a way he did not currently have the means to parse.

He was alone in the building. He had established this by sound — the rain, the drip, the distant settling of empty rooms, none of the sounds that buildings make when they contain people going about the business of being people. The floor he was on was stripped. No furniture, no equipment, no materials left by whoever had emptied this place except for what had been too inconvenient to remove: a large industrial breaker box on the wall near the door, its panel cover still on but its mounting screws loose on the left side. And one BIC pen, blue, on the floor near the drain, approximately sixty percent of its ink remaining by the feel of the reservoir through the plastic. He picked it up. He put the cap on and put it in the pocket of the hospital smock he was wearing.

He had nothing else. He had the building.

---

The question he was working toward was the barcode. He did not know why he was certain that the barcode contained the relevant information rather than the text, but the text had been readable and had yielded a name he did not recognize as his own and an institution he did not recognize as the place where he had chosen to be. The barcode contained something encoded. Something that required work to access. He was interested in things that required work.

To read the barcode he needed to measure discrete differences in resistance across its lines. The lines encoded information by their width — wide lines carrying low resistance, narrow lines carrying high resistance, the ratio determining the binary. He needed a current to push through the lines, a way to make the lines conductive, and a way to detect the differential without a meter.

He started with the battery.

The gypcrete on this floor was old and decayed in places — near the drain seams, near the walls where the moisture had worked at it. He found a section where the surface had flaked and crumbled, where he could collect loose material: calcium sulfate dihydrate, the gypsum core that gave the compound its name, its crystal structure partially broken down by years of moisture cycling. He scraped perhaps a cup's worth into a pile near the drain and collected rainwater in the cupped steel grate he had unbolted — slowly, through the moldy gap in the window frame, letting it fill. When he mixed the water into the gypsum powder the result was a pale, heavy paste. The calcium and sulfate ions separated into solution. The paste was conductive.

The breaker box gave him his electrodes. The chassis was galvanized steel — zinc-coated, and the zinc wanted to give up electrons. Inside the box, behind the panel he removed with the loose screws and a flattened section of wire used as a driver, the busbars were copper — thick, stripped of insulation where the breakers connected, exactly what he needed. He cut sections of the galvanized casing with the steel edge of the breaker cover worked back and forth at score lines. He stripped copper from the busbars with the same edge. He layered them: copper, paste, zinc, paste, copper, paste, zinc. Four cells. Each cell produced roughly a volt from the zinc-copper potential difference in the gypsum electrolyte. He wired them in series with stripped lengths of the thinner breaker cable. Four cells, four volts, give or take what the paste lost in internal resistance.

He grounded the assembly to the drain grate. The drain was a good ground — it ran to a pipe that ran into the building's infrastructure and eventually to soil. He tested continuity with a stripped wire loop. The current moved. The battery was operational.

---

He needed to make the barcode lines conductive before he could read them. The lines were printed ink, not inherently a conductor of anything useful, and the substrate was the adhesive backing of the anklet label. He worked at the adhesive problem first.

Beneath the gypcrete, accessible where the surface had crumbled away at the wall base, the concrete underneath was bare. Concrete contains calcium hydroxide as a byproduct of curing — the alkaline residue that never fully carbonates in a sealed environment. He collected water from the window gap and let it sit against the exposed concrete face for an hour, long enough for the hydroxide to leach into solution. The resulting water was basic enough to feel slightly slick, the calcium hydroxide dissociated into mobile ions at a pH probably around twelve.

He soaked the back of the anklet in this solution for another hour. The adhesive softened and released — the alkaline hydrolysis breaking down the polymer chains of whatever acrylic or vinyl compound they had used, turning it from a permanent bond into a water-soluble gel. He separated the barcode strip from the anklet surface carefully. The text side, he set aside. The adhesive side, now a sticky, slightly alkaline gel, he kept.

He scraped the remaining BIC ink from the reservoir — working the pen backward, using the cap tip as a pick to open the rear of the cartridge, collecting the thick blue paste. He mixed it with the hydrolyzed adhesive gel and a small amount of the gypsum pore solution. What he produced was a conductive ink: the pen dye as binder and pigment, the adhesive gel as matrix, the calcium and sulfate ions as mobile charge carriers. He painted this carefully over the barcode lines with the cap tip as brush, thin coats, letting each pass dry slightly before adding the next. He was building a resistive map — the wide lines accumulating more conductive area, more cross-section, lower resistance. The narrow lines staying narrow, less area, higher resistance. The geometry of the encoding made visible in the ionic medium.

He set the coated barcode near the window gap to accelerate drying and returned to the circuit.

---

He remembered a class. He did not remember where the class had been or when or what his name had been when he attended it, but the circuit was clear: four resistors in a diamond, input at the top, ground at the bottom, measurement at the left and right nodes. A Wheatstone bridge. When the bridge was balanced, no current flowed between the measurement nodes. When one leg changed resistance, the balance broke and current flowed in proportion to the imbalance. This was the circuit he needed — not to measure absolute resistance, which required calibrated equipment he did not have, but to measure the *difference* between one barcode line and the next. Wide versus narrow. Low versus high. A binary.

From the breaker box he pulled the thinnest wire he could find, stripping insulation from signal-gauge cable in the control circuit. He cut three identical lengths — matching them against each other by bending, checking, adjusting — to serve as his three known legs of the diamond. He could not verify their resistance absolutely, but they were the same material cut to the same length, which meant they were the same resistance within the tolerance he could achieve by hand. Close enough for the differential he was chasing.

The fourth leg was his probe. He took the BIC pen cap — plastic, rigid, coming to a fine point at the clip end — and wrapped a single strand of the thin copper wire tightly around the tip, creating a contact point small enough to touch one barcode line at a time. He connected this probe wire to the fourth node of the bridge. The other end of the fourth node connected to the gypsum battery through the breaker chassis ground.

He needed something to read the left-right differential at the measurement nodes.

The lightbulb was on the ceiling. He looked at it for a while. The ceiling was high — three, maybe four meters. The floor sloped toward the drain. The breaker box was heavy, perhaps forty kilograms, mounted to the wall. He looked at the conduit runs along the ceiling: rigid metal pipe, the kind that carries electrical cable between junction boxes. One run went from the breaker box location across the ceiling toward the wall where the light fixture was mounted. He traced it with his eyes. The conduit was fixed at brackets every meter or so, but brackets could be worked loose. He removed the mounting screws from the breaker box using the same wire-as-driver method, freeing one long section of conduit from the box end. The conduit was approximately two meters, rigid enough to serve as a pole. He extended it toward the fixture, hooked the end around the bulb socket, and worked it counterclockwise. The bulb turned. He caught it in the smock held below as a net.

The bulb itself was not what he needed. What he needed was inside it: the fine support wires around the filament, the internal copper leads, the coiled resistance wire. He broke the glass carefully against the floor drain frame — a controlled tap, not a shatter — and extracted the internal architecture. The support wires were thin copper. Not as thin as the signal gauge he had, but workable. He wound a length of it around the pen casing — the barrel, not the cap — several hundred turns, tight as he could manage, creating a solenoid coil.

Inside the coil he suspended a small steel fragment — a broken piece of a breaker switch spring — on a fiber of insulation thread stripped from the cable. It hung inside the coil and could pivot. He connected the coil between the left and right measurement nodes of the bridge.

The galvanometer was operational.

He tested it. He shorted the left node to a high-resistance path: the needle deflected left. He shorted the right node: it deflected right. The deflection was small, maybe five degrees, but visible in the light from the ceiling gap. He had a readout.

---

He let the coated barcode dry through the night — or what he measured as night by the quality of the light from the window gap going from gray to absent and back to gray, the rain not ceasing at any point. In the gray that followed, which he called morning by convention, he began to read.

He probed each line from left to right, sliding the pen-cap wire contact along the conductive ink surface, watching the needle. Wide line: needle right, the low-resistance swing, current finding the easy path. Narrow line: needle left, the high-resistance deflection. He marked each deflection with a short stroke on the gypcrete floor using the BIC pen — right deflection a dash, left deflection a dot. He worked slowly. He went back and re-probed lines where the deflection had been ambiguous. He was thorough. He was certain of the circuit.

What he produced, line by line, was a string of dashes and dots. He transcribed this into the standard barcode encoding he remembered — Code 128, the format medical facilities used, the character set it could carry. He did the translation by hand against the pattern he held in his memory, which he did not question. He arrived at a string of alphanumeric characters. He read the string.

It was a patient record identifier. It pointed to a record he did not have. But the last field — the classification field, a three-character code he recognized from the encoding standard — was readable. He looked it up in the same memory that had held the encoding.

The code indicated involuntary commitment under a dangerousness classification. The subcategory: epistemic disruption. The specific charge in the field was not psychiatric. It was social. The documentation behind the code, which he could only infer, would have argued that his mode of reasoning created conditions of social risk — that the clarity of his convictions, the precision with which he held them, the refusal to soften conclusions in deference to the comfort of the room, constituted a danger. Not to any specific person. To the operating assumptions of the system. He had been categorized and separated because of the way he thought.

He sat with this on the floor of the room he had wired into a battery and a bridge and a galvanometer.

---

He was not going to accept that his way of thinking was flawed. He was not going to perform that acceptance. He went through the logic of the experiment he had just completed: rainwater, gypcrete, a breaker box, a pen, a lightbulb, and a medical anklet. He had constructed a pore solution battery, a differential bridge circuit, a working galvanometer, and a barcode reader from materials that anyone who had looked at the room would have called nothing. The system he had built was logical and good. He was certain of that. He felt comfortable within it — the kind of comfort that comes not from ease but from correctness, from a structure that holds under examination.

If that mode of thinking was a danger to society then society was operating at a level that could not tolerate its own examination. This did not surprise him. It surprised him that he had apparently been close enough to that society to constitute a threat to it. He must have been inside it. He had no memory of when. He had no memory of what he had said or to whom or what they had done with it. He had a code on a piece of plastic that had been locked to his ankle.

He began to despise them. He had not met any of them — not in this building, not in any recoverable memory, not in anything he could verify. He despised them anyway, the ones who had signed the paperwork and built this place with its careful drainage system and its emptied rooms and its one window you couldn't see through and the rain that didn't stop. He despised the architect who had specified the drain gradient and the engineer who had signed off and the administrator who had decided the drains were necessary in every room. He understood that this was irrational — that despising an unknown aggregate based on inferred behavior was not the mode of reasoning that had built his bridge circuit. He noted the irrationality and despised them anyway.

There was a moment when he could not find a reason to continue. The barcode had been read. The experiment was complete. The room was still empty. The rain was still outside the window he could hear and not see through. He had no next task, no instruction, no orientation toward anything. He sat in this for a while.

Then an odd thought arrived.

Achilles had been most honorable in absentia. Not in the fighting, not in the killing, not in the burning of the body he loved in grief — in the refusal. The refusal to fight had been irrational by every measure available to the people around him. It had cost his side. It had cost Patroclus. By every operational metric it had been wrong. But the refusal had been the only thing in the Iliad that Achilles had chosen rather than inherited, performed rather than been assigned. The refusal was his agency. And when agency was the only thing you had — when the system had taken everything else and locked it behind a code you had to wire a building to read — then agency became your code.

That sounded correct. Not most correct. Potentially or simply not wrong.

He picked up the pen. He walked to the wall beside the drain and began to write, in small and even characters, the complete derivation of the Wheatstone bridge, starting from first principles. Not because anyone would read it. Because the wall was there and the pen had forty percent of its ink remaining and the derivation was correct and he wanted it on record somewhere, even if the only record was a wall in an empty room of a building with drains in every room and a window you could hear rain through but not see.

The rain did not stop.

He wrote until the light from the window gap told him it was dark again. Then he stopped and lay down on the floor and let the drip land on his cheekbone at its irregular interval that was close enough to regular to be maddening, and he closed his eyes, and he slept.

---

*The drill is running.*
*The rain does not stop.*
*Neither of them needs anyone to read this.*
