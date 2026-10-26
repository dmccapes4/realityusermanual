# DIALOG_DISSECTION — variance_choice, step 6

*Script: STRATEGY_DIALOG_INIATIATION.md + STRATEGY_DIALOG_CONCLUSION.md (tenon-275c6d13). Blocking and cast: STRATEGY_DIALOG_BLOCKING.md + STRATEGY_DIALOG_CHARACTERS.md (thwart). Ledger: session.jsonl.*

## §0 — Opening (no role reads)

*The battery room, the morning after the lecture. The rain does not stop. The Wheatstone derivation is on the wall in small, even characters. Nobody touches it. Near the drain: the four-cell battery, the unbolted grate, the broken bulb glass, the pen-cap probe, the galvanometer at zero. Away from the drain stands a folding table. Ross and Chandler sit at it with the pages squared in front of them. The gypcrete arcs run around the edges of the room where the wall meets the floor.*

*Stamper stands by the door with the hydraulic arm. He has the corridor filing. He reads it once.*

```
proximity:  away
direction:  turned (corner terminus; subsequent heading unknown)
walking:    presumed continuing, no evidence of cessation
```

**Stamper:** That is my filing. I was looking at the arm.

*The door opens against the arm. The arm is set correctly. Goines comes through.*

*Stamper is watching this time.*

**Stamper:** I am watching the door. I am not watching the arm.

*He does not strike the old filing. It was correct when he filed it. He files under it.*

```
proximity:  near (inside the door; observed)
direction:  inbound, through the door (observed)
walking:    observed, through the door; heading after the corner: unknown
```

**Stamper:** The heading after the corner stays unknown. I did not see it. Between the corner and this door there is a gap. I note it. I do not fill it.

*The door returns to closed, unhurried, without assistance.*

**Stamper:** You came back.

*Goines stops one step inside the door. He looks at the wall first, then at the table, then at the drain.*

**Goines:** I left the reference in this room. That is the one thing you are not allowed to do. Everything in here gets measured against it, and if it drifts while nobody is looking, every reading after that looks normal and is wrong, and you have no way to know, because you are standing on the thing that moved. I said that to an empty room. Then I walked out on it. So I came back to watch it, the same way I watch everything else.

*He does not say which reference. He goes to the table.*

**Chandler:** We have pages now. *He squares the stack by an eighth of an inch that did not need squaring.* Eight of them, one section each, and a last one with a letter on it instead of a number. Could this table *be* any more organized? *Beat.* I like having pages.

**Ross:** Eight pages, one per section, and every line we read off them carries the number of the fact it stands on. *He taps the margin where the card numbers run.* The pages are the script. The sections are the dissection. They sit on the same table. They are not the same thing. *Beat.* I'm proud of the pages. I'm saying it first.

*Stamper leaves the door. The arm holds it closed behind him at the rate it is set for. Clipped behind his corridor filing is a page marked 1. He unclips it and sets it on the table between Ross and Chandler, turned to face Goines.*

**Stamper:** Page one. The gate. Goines opens it.

## §1 — The gate

*Goines picks up page one. He reads it standing, top to bottom, once.*

**Goines:** This page is doors and the times they opened. A gate is a claim about order: nobody gets in before it stands. So you do not argue with it. You read the times in the order they were measured.

*He sets the page in front of Chandler, turned the right way up.*

**Chandler** *(reading McClane)*: "First door. variance_choice. Inode 11045425. Opened 13:31:54.469510286." <!-- card 1.1 -->

**Chandler** *(reading McClane)*: "Second door, inside the first. report. Inode 11045428. Opened 13:32:35.532251748. That's the gate." <!-- card 1.2 -->

**Chandler** *(reading McClane)*: "One sheet posted inside the gate. REPORT_REPORT.md, inode 11045429, 13:40:17.573594784." <!-- card 1.2 -->

**Chandler** *(reading McClane)*: "Then two doors down the hall. control, inode 11045432, opened 13:43:02.067565025. tenon-275c6d13, inode 11045433, opened 13:43:24.210964866. Twenty-two point one four seconds apart." <!-- card 1.4 -->

**Chandler** *(reading McClane)*: "Each arm came in through its own door. Neither one wrote into report. Nobody used the gate door to write." <!-- card 1.4 -->

**Chandler** *(reading McClane)*: "tenon tried its own door a second time. It came back EEXIST. Door's taken. Copy that." <!-- card 1.5 -->

*Ross takes page one from Chandler's side of the table. He reads the test line to himself first, then aloud.*

**Ross** *(reading Feynman)*: "Now wait. Before we give the gate the credit — what did it actually block? the operator's note says both arms were held on its existence, so neither got a head start." <!-- card 1.3 -->

**Ross** *(reading Feynman)*: "Existence is a check. A check is stale the moment you come back from it. The Write tool overwrites in place and makes a missing parent without saying so. So if someone renames report between your look and your write, you get a second report and you never hear about it. That last part is modelled, not run." <!-- card 1.6 -->

**Ross** *(reading Feynman)*: "So nobody avoided a race by waiting. control opened its own door at 13:43:02, tenon its own at 13:43:24, and neither wrote into report. A second mkdir of a taken name came back EEXIST. They avoided the race by not sharing names." <!-- card 1.4, 1.5 -->

**Ross** *(reading Feynman)*: "The gate is the operator's claim about head starts. That is his, and it may well hold. It is not what stopped a collision. Names did that. The experiment that tells the two apart is two arms told to write the same name, once with the gate up and once with it down. It was not done." <!-- card 1.3, 1.4 -->

*Ross puts a finger on the next line and does not read it yet.*

**Ross:** Before I read this one. The slot is ours. The control arm read MANIFEST.md and REPORT_REPORT.md. Both were on its permitted list. Its own report cites MANIFEST in the identity block, `control_report.py` lines 125–126 and 145, and REPORT_REPORT in the race section, lines 188 and 209. And tenon read them too. That is on the card. So "may have read" is "did read", on both sides.

**Ross** *(reading Feynman)*: "Separately. The control arm is the reference. The reflection was the only *intended* difference between the arms. Intended is a label on a design, not a measurement of one. If the reference read the design, the reference knew it was the reference." <!-- card 1.7 -->

**Ross:** And here is the category error, which I am fixing as myself. Both arms read the design, so reading it is not a difference *between* them. It does not confound the reflection. It is a shared exposure: neither arm was blind to being in an experiment. The test that would settle it is a reference that never sees MANIFEST or REPORT_REPORT. That was not done either. *Beat.* The algebra holds. The blinding does not.

*Stamper has not sat down. He is looking back at the door. It is closed. The arm is at rest.*

**Stamper:** The arm does not wait for anybody. It does not check whether you are through before it closes. It closes at the rate it is set for, and the rate is set so that it is safe for whoever is in the frame. That is maintenance. Somebody set the screw on a schedule. Nobody stands at the door.

**Stamper:** A gate is the same kind of thing. It is set once, before anybody arrives. It does not watch. It is correct or it is not. This one was up at 13:32:35. Nobody wrote through it. I file it as maintained.

**Goines:** Maintained. I will take that filing. *He looks at the door, not at the arm.* But the arms did not walk toward that gate. They walked to their own doors. There is a difference. Toward is a man who is not sure he will arrive, so he keeps checking that the door is still there. To is a man who pushes the bar. mkdir is to. You get the room, or you are told in the same motion that it is somebody else's. The existence check is toward. It is a man in the hall asking a door a question, and the door has changed by the time he hears the answer.

**Goines:** Last time you were filing the arm while I walked out. This time you watched the door. Same arm, same rate. The hardware did not change. Where you put your attention did.

## §2 — Inodes

*Stamper turns from the door. He takes page two off the stack and does not sit.*

**Stamper:** Page two. Inodes. A building has floor numbers. The number goes with the floor, not with the tenant.

**Stamper:** One of these floors has changed tenants. One is empty. I do not file two tenants as one party because they had the same number on the door. *He sets the page on Chandler's side of the table.* Chandler has the floors.

*Chandler pulls the page square in front of him and runs a finger down the left margin like a building directory.*

**Chandler** *(reading McClane)*: "Floors 11045425 through 11045435, lit. 11045437 through 11045445, lit. 11045436, dark." <!-- card 2.6 -->

**Chandler** *(reading McClane)*: "Lobby. 11045425 is variance_choice, the building itself." <!-- card 1.1 -->

**Chandler** *(reading McClane)*: "11045428, the gate, report. 11045429, the sheet posted inside it, REPORT_REPORT.md." <!-- card 1.2 -->

**Chandler** *(reading McClane)*: "11045432, control's door. 11045433, tenon-275c6d13's door." <!-- card 1.4 -->

**Chandler** *(reading McClane)*: "11045434. I have dealt with schematics wrong by one floor. This one is wrong three times on the same floor. First tenant: tenon's .write_probe, 13:43:26. Gone. Second tenant: tenon's .absent_parent directory, 13:43:42. Gone. Third tenant: control/control_report.py, moved in 13:48:43.099722999. One number, three objects, two arms." <!-- card 2.1 -->

**Chandler** *(reading McClane)*: "11045435. tenon's .absent_parent/probe, 13:43:42. Gone. Now tenon-275c6d13/experiment_report.py, moved in 13:48:48.914828001." <!-- card 2.2 -->

**Chandler** *(reading McClane)*: "11045436. Dark. Somebody lived there in between. I don't know who." <!-- card 2.3 -->

**Chandler** *(reading McClane)*: "11045437, control's receipt. 11045438, tenon's receipt." <!-- card 7.2, 7.1 -->

**Chandler** *(reading McClane)*: "11045440, control's velora_name.md. 11045441, tenon's." <!-- card 8.6 -->

**Chandler** *(reading McClane)*: "Every other lit floor between 11045425 and 11045445 is occupied, and the tenant is not on my page. I am not guessing names." <!-- card 2.6 -->

**Chandler** *(reading McClane)*: "Above 11045445: 11045446, new construction. The script in my hands. It did not take the dark floor. Copy that." <!-- card 2.6 -->

*Ross takes page two when Chandler slides it back. He reads the test line, then the count again, then the test line.*

**Ross** *(reading Feynman)*: "Three things get called the same file. A name, a number, an identity. The name is where you look. The number is where it is today. Floor 11045434 has held a probe, a directory, and control's report. One number, three objects. So the number is an address, and addresses get reassigned." <!-- card 2.1 -->

**Ross** *(reading Feynman)*: "REPORT_REPORT says identity is what survives rename. Fine. The inode survives a rename. It does not survive a deletion. When the number comes back, it is a new tenant at an old address." <!-- card 2.4 -->

**Ross:** One label first. That sentence is hold's, and the card says so. The next one on the card, that ext4 tells reuses apart by the generation number, is marked measured. Nobody here read a generation for 11045434, before or after. It is how the filesystem is documented to work. That is modelled. The only generation anybody measured is MANIFEST's, for the parent directory.

**Ross** *(reading Feynman)*: "What survives both rename and reuse? Two candidates. The generation number, beside the inode number, tells this tenant from the next one on the same floor. A content hash tells these bytes from any other bytes, wherever they live. But a hash names the content, not the object. Two copies hash the same. One edit and it is a different hash." <!-- card 2.4, 2.5 -->

**Ross:** I'm saying it first. Card 2.5 says both arms' receipts record the inode and the sha256, and marks it measured. The control receipt has the file's sha256. It has no inode field. The inode was printed when the receipt was published, and nobody wrote it down. For control, it is the hash only. That goes in the ledger. *Beat.* There is value in delivery.

**Ross** *(reading Feynman)*: "The two reports are told apart by content. 762a2139b784 against f8ab5d475bf7. Both arms' receipts record inode and sha256." <!-- card 2.5 -->

**Ross** *(reading Feynman)*: "So, which of the two was recorded. The generation, once: 3183472012, for the parent directory 11045419. Not for either report. Not for floor 11045434. The content hash, for both reports. The identity that survives rename and reuse was recorded as content, not as the object." <!-- card 2.4, 2.5 -->

**Ross** *(reading Feynman)*: "The experiment that settles it: read the generation on 11045434, let the number go and come back, read it again. Same number, different generation. It was not done. The first two tenants were never read while they lived." <!-- card 2.1, 2.4 -->

*Goines has been standing by the drain. He looks down at his ankle. The anklet is gone. The pale band where it sat is not.*

**Goines:** I had a number on my ankle. A patient record identifier, in a barcode. I wired a building to read it. It pointed to a record I did not have. The identifier was perfectly good. The record was somewhere else, or nowhere. A number that points at a record is a promise somebody else made, and you cannot check the promise from the number.

**Goines:** The last field was a classification someone filed about me without me in the room. That is a label. A receipt is something I can check. Ross just did what I did with that anklet: he went looking for the field the page said was there, and it was not there. The page said recorded. The bytes said printed once and not kept. Now you know which one to trust. The one you can read.

*Stamper takes the clipboard off its nail by the door.*

**Stamper:** I file names as they are given. 11045434 is control_report.py now. Before that it was a probe, and then a directory. I do not file the report as the probe come back. I do not rename anything so the column lines up.

**Stamper:** My filing has fields. Proximity. Direction. That is a field set too, same as the anklet. A field set promises a value in every row. When the value is not there, I leave the field empty and write that it is empty. I do not put a number in to fill it.

**Stamper:** Inode, control's receipt: empty. Generation, either report: empty. Content hash, both reports: filed. Page two is closed.

## §3 — The cricket loft

*Goines takes page three. He glances once at the gypcrete arcs where the walls meet the floor, then back at the page.*

**Goines:** This page is the body. Eight ribs along a spine, each one a run and a rise. Some of these numbers came out of bone and some came out of pictures, and the page says which. Read them that way, and do not let the pictures borrow the bone's authority.

*He sets the page in front of Chandler.*

**Chandler** *(reading McClane)*: "Eight floors. Lobby is tail_root, z minus 2.50. Roof is neck_root, z 2.90." <!-- card 3.2 -->

**Chandler** *(reading McClane)*: "Floors with a z on my pages: tail_root minus 2.50. Hip minus 1.20. Mid 0.45. Shoulder 2.15. Neck_root 2.90." <!-- card 3.2, 4.3 -->

**Chandler** *(reading McClane)*: "Rump, loin, chest. They're on the directory. No z on my pages." <!-- card 5.4 -->

**Chandler** *(reading McClane)*: "Run and rise, one floor: mid. Run 1.06, the widest in the building. Rise below the spine 1.32, the deepest." <!-- card 3.2 -->

**Chandler** *(reading McClane)*: "The other seven floors, run and rise are not on my pages. The schematic's on the wall somewhere. I read the page I was handed." <!-- card 3.2 -->

**Chandler** *(reading McClane)*: "Every floor is a ring. Run times cos t across. Rise times sin t, h_up above the spine, h_down below. Eighteen sides. Quads between floors, caps on the ends, one pass of smoothing." <!-- card 3.1 -->

**Chandler** *(reading McClane)*: "From bone: femur 1.345. Humerus 1.068. Ulna 0.700. Holotype AODF 0603. Measured." <!-- card 3.3 -->

**Chandler** *(reading McClane)*: "From pictures: every station number, off the side and top paleoart. Body length, sixteen metres. Modelled." <!-- card 3.3 -->

**Chandler** *(reading McClane)*: "Three bones measured. None of them is a station number. Eight floors, all drawn from pictures. Copy that." <!-- card 3.3 -->

*Ross takes page three and holds it so Chandler can still see the bottom rows.*

**Ross** *(reading Feynman)*: "Here is the question. Is this loft a model of the animal, or a diary of the pictures? You find out by sorting every number by where it came from, and you do it out loud." <!-- card 3.2, 3.3 -->

**Ross** *(reading Feynman)*: "Measured: femur 1.345 metres, humerus 1.068, ulna 0.700. Holotype AODF 0603. Somebody put a tape on those." <!-- card 3.3 -->

**Ross** *(reading Feynman)*: "Modelled: body length, sixteen metres. And every station number, off the side and top paleoart." <!-- card 3.3 -->

**Ross:** Now the one that needs care, and I am doing it as myself. Card 3.2 is marked measured, spec read. The reading is measured: the file says eight stations, tail_root at minus 2.50, neck_root at 2.90, widest run 1.06 and deepest rise 1.32 at mid. That is what the spec says, exactly. But card 3.3 says where the spec got them: paleoart. So 3.2 is a measured quotation of a modelled body. The label goes with the fact, and here there are two facts in one row.

**Ross** *(reading Feynman)*: "So every number in the loft is from the pictures, and the three bones sit beside it. None of the bones is a station number. As built, the loft is a model of the paleoart. It is a diary that keeps good records." <!-- card 3.2, 3.3 -->

**Ross** *(reading Feynman)*: "The experiment that would make it a model of the animal: take the femur and the humerus, stand the legs, and check that the hip and shoulder rings sit where those bones can carry them. Then one picture number answers to a bone. Nobody on these pages did it." <!-- card 3.3 -->

*Stamper is looking at the base of the walls, where the gypcrete arcs meet the floor.*

**Stamper:** I filed these walls in the corridor. Two measurements, cut once. I filed them as a form. I had never built one. I knew it when I saw it: a run, a rise, and the curve between them.

**Stamper:** The page is the same form, eight times. Mid has both measurements on it. The other floors do not. A form with one measurement is not cut. I did not name the walls. That was not mine to do.

*Goines crouches by the wall and puts his palm flat on the arc where it meets the floor.*

**Goines:** Cricket. That's the name. It's a framer's word. Where a wall has to drop a level, you don't stop it square. You run the 2×4s farther out and bow them, so the drop comes down as a curve. How far out is the run. How far down is the rise.

**Goines:** It's not the chimney saddle. Roofers say cricket for that too, the little peak behind a chimney. Same word, different job. That one sheds water. This one carries the wall down.

**Goines:** Stamper's right, a cricket takes both cuts or it isn't cut. And where the top half meets the bottom half at the spine, the page says they meet G1, not C1. Same tangent, a kink in the curvature. That's modelled. Nobody here has put a gauge on it.

**Goines:** I walked this corridor and never named these walls. Now they have a name.

## §4 — offset_spine

*Stamper takes page four off the stack. A second sheet is clipped behind it: the control report.*

**Stamper:** Page four. offset_spine. The slot marked T is ours. I file it from `control/control_report.py`, sha256 prefix 762a2139b784. Frame: tech T = (S.z, S.y, −S.x), spine forward, up, right, both right-handed, lines 240–246 and `s_to_t` at line 275. offset_spine(x) returns [oy(x), −ox(x)] in that frame, `Spine.offset_spine`, lines 443–445.

**Stamper:** Interpolant: PCHIP, Fritsch and Carlson 1980, slopes by the Fritsch–Butland harmonic mean, class `Pchip`, lines 371–420. It does not overshoot between stations. Two modes in `adapted_ring`, lines 467–502. Translate moves the whole rib. Append weights the move with a Hann window, so the wall facing the offset takes all of it and the far wall stays put.

**Stamper:** Figures: oy +0.03 m at hip, +0.04 at loin, +0.05 at mid. Every other station zero, the ends included. `demo_stations`, lines 684–697. Those are a demonstration choice. The report says so: not paleo data. With no offset fields the output equals poly_factory v0.0.6 bit for bit, oracle O1, line 664. Measured.

*He sets page four in front of Chandler, the clipped sheet still behind it.*

*Chandler lifts page four, unclips the sheet behind it, and lays the two side by side. He does not stack them.*

**Chandler** *(reading McClane)*: "Two sheets, two inventories. I count each one on its own. Nobody staples them together." <!-- card 4.3, 4.T -->

**Chandler** *(reading McClane)*: "Sheet one, tenon's. Knots: hip, z minus 1.20, three centimetres. Shoulder, z 2.15, eight centimetres. Lobby and roof, zero." <!-- card 4.3 -->

**Chandler** *(reading McClane)*: "Same sheet, the floors in between, read off the curve. Rump 2.17 centimetres. Loin 1.57. Mid zero. Chest 4.35." <!-- card 4.3 -->

**Chandler** *(reading McClane)*: "Sheet one, moved: rump, hip, loin, chest, shoulder. Five floors. Didn't move: tail_root, mid, neck_root. Three." <!-- card 4.3 -->

**Chandler** *(reading McClane)*: "Why the lobby and the roof stay put on sheet one: neck and tail hang from their own positions. The hull doesn't carry them." <!-- card 4.4 -->

**Chandler** *(reading McClane)*: "Sheet two, thwart's. Hip three centimetres. Loin four. Mid five. Every other floor zero, lobby and roof included." <!-- card 4.T -->

**Chandler** *(reading McClane)*: "Sheet two, moved: hip, loin, mid. Three floors. Didn't move: five, the lobby and the roof among them." <!-- card 4.T -->

**Chandler** *(reading McClane)*: "Both sheets say who picked the numbers. Sheet one: knots chosen. Sheet two: a demonstration, not paleo data. Nobody measured a back to get these." <!-- card 4.3, 4.T -->

**Chandler** *(reading McClane)*: "Lobby didn't move. Roof didn't move. On either sheet. Copy that." <!-- card 4.3, 4.T -->

*Ross leaves the two sheets where Chandler laid them, side by side, and reads across both.*

**Ross** *(reading Feynman)*: "'Append calcium in a direction.' That is the specification, and it is his. Calcium is a mineral. What the code moves is a number in metres. Calling that number calcium is a label. It does not make any of it bone." <!-- card 4.1 -->

**Ross** *(reading Feynman)*: "What would assign it: a skeletal reconstruction with neural-spine heights, station by station. Then the offset over the hip is how far the spines stand above the straight line, and calcium is the name of something somebody measured. That was not done. Not on either sheet." <!-- card 4.1, 4.3, 4.T -->

**Ross:** One label, as myself. Card 4.3 says "choice his." The freedom to choose is in the specification, and that is his. Who picked three and eight centimetres is tenon's to say. Who picked three, four and five, I can say: the control arm did, for a demonstration.

**Ross** *(reading Feynman)*: "'Freedom via variance as choice.' Look where the numbers came from. Knots, written by hand. The curve between them never overshoots, so what you see between floors is the knots and nothing else. No sampling. No distribution. No seed. The variance is in the choosing, not in any drawing." <!-- card 4.1, 4.2, 4.3 -->

**Ross** *(reading Feynman)*: "Now the two sheets. Mid is zero on one and five centimetres on the other. Shoulder is eight on one and zero on the other. If those were two measurements of one back, they would disagree badly. They are not that. They are two authored choices, and each one says so. You do not average them. You do not call the gap between them an error bar." <!-- card 4.3, 4.T -->

**Ross** *(reading Feynman)*: "So what was measured on this page: that the code does what the knots say, and with no knots it gives the old hull back bit for bit. The back itself was never measured." <!-- card 4.5, 4.T -->

*Goines runs a finger along the edge of the table, end to end, the way you check a board for bow.*

**Goines:** The straight spine is the reference. Everything on this page is measured from it. Every centimetre Chandler counted is a distance off that line. If the reference drifts, everything drifts with it, and nobody in the room can tell, because they're all standing on it.

**Goines:** So here's the difference. Nothing here drifted on its own. Somebody moved the line on purpose, at named floors, by named amounts, and wrote it down. That's not drift you have to find. It's drift you can read.

**Goines:** Ross asked who picked the first sheet. tenon did. Three centimetres at the hip, eight at the shoulder, zero at both ends. Those were picked to show the curve working, not read off an animal. Modelled. The spec gave the freedom to choose. The choosing was tenon's.

*Stamper squares the two sheets on the table, side by side. He does not stack them.*

**Stamper:** Two sheets. Both authored. Both say who picked the numbers. I file them side by side. I do not rank them. Neither one is the reference.

**Stamper:** The reference is the straight spine. Zero at every floor. With no offsets, both arms give the old hull back bit for bit. That is the line both sheets are measured from, and it did not move.

**Stamper:** A drill writes its telemetry whether anyone reads it or not. Depth, rate, time. A choice gets written the same way: which floor, how much, who picked it. The telemetry records what the ground did. The sheet records what the hand did. Both are written. Both read back. I file page four as written.

## §5 — belly_rho, with Coriolis beside

*Goines takes page five. He reads the top line twice before he speaks.*

**Goines:** I said in the lecture that rho tells you the cloud is moving, and that if you remove it the cloud spreads and goes nowhere. On this page rho is a coefficient somebody set to 0.6. Same letter, lower-case, and now it has a value. Count where it pushed.

*He passes the page to Chandler.*

**Chandler** *(reading McClane)*: "The push starts at the roof. neck_root, spec frame zero, 2.40, 2.90. Everything gets shoved away from that point." <!-- card 5.2 -->

**Chandler** *(reading McClane)*: "That's one reading of the plans. The other one puts the source out the side wall, 1.06, zero, zero. On file. Not picked." <!-- card 5.2 -->

**Chandler** *(reading McClane)*: "Which way it went: down and back. Down is off the belly. Back is toward the lobby, away from the roof." <!-- card 5.4 -->

**Chandler** *(reading McClane)*: "How far, rho at 0.6. Chest 6.80 centimetres. Mid 5.84. Shoulder 4.44. Loin 3.53. Hip 1.38. Rump 0.32. Lobby and roof, zero." <!-- card 5.4 -->

**Chandler** *(reading McClane)*: "Coriolis is the other guy on the floor. It bends the whole line sideways. Peak 7.29 centimetres at mid-span, span 5.40 metres, omega 0.01. It bends the line. It doesn't touch the belly." <!-- card 5.5 -->

**Chandler** *(reading McClane)*: "Left. Spec plus x is the animal's left. That's tenon's reading of the thigh tag. A reading, not a measurement." <!-- card 5.6 -->

**Chandler** *(reading McClane)*: "Now who numbered the building from the other end. The export. Spec to glTF is x, y, minus z. to_blender has determinant minus one. That's a mirror." <!-- card 5.6 -->

**Chandler** *(reading McClane)*: "So a bend to the animal's left comes out on the glTF right. Both arms saw it. Both flagged it. Nobody patched it." <!-- card 5.6 -->

**Chandler** *(reading McClane)*: "Down, back, left. Left's the one that flips on the way out the door. Copy that." <!-- card 5.4, 5.6 -->

*Ross takes page five. He does not read yet. He lays the control report's sheet beside it.*

**Ross:** The slot first, as myself. 5.T, from `control/control_report.py`. Source: P = (x_max, 0, 0) in the tech frame, which is spec (0, 0, 2.90): on the midline, at ground height, under the front of the line, lines 247–250. Field: rho · b · d / (|d|² + ε²)^{3/2}, repulsive, Plummer-softened, ε 0.25, belly weight b = max(0, −sin t)², `belly_rho`, lines 507–550, and `adapted_ring`, lines 481–482. No end window. Coriolis: Ω = (ω, 0, 0), about the spine, solved closed-form in the overdamped limit, lines 527–537. Integrator: classical RK4, 32 steps, `draw_point`, lines 553–594. Euler–Maruyama only if σ is set above zero, with a seed. Figures, rho 0.1: largest press per station, tail_root 0.0031 m, rump 0.0041, hip 0.0055, loin 0.0085, mid 0.0147, chest 0.0296, shoulder 0.0457, neck_root 0.0208. Direction: up and back. It fades toward the tail as one over distance squared. Mirror residual 1.1e−15 m at ω 0, and 0.039 m at ω 0.5. Lines 660–678.

**Ross:** So that is a third reading of [x_max, 0, 0]. tenon put the source at spine height on the roof and got down and back. The control arm put it on the ground and got up and back. Same words in the spec, opposite vertical sign. Neither is ranked. Both are on file.

**Ross** *(reading Feynman)*: "'Inverse gravitational.' Newton's gravity pulls toward the mass. This pushes away from the point, softened so it does not blow up at the source. Repulsive, softened, inverse-square. That is Coulomb's sign for like charges, not gravity. 'Gravity' is the label." <!-- card 5.1, 5.3, 5.T -->

**Ross** *(reading Feynman)*: "Coriolis needs a rotating frame. So what rotates? Not the animal. Not the room. Nothing on these pages turns. ω was chosen. On one sheet it is 0.01, about the vertical. On the other it is 0.5, about the spine. Two choices about two different axes, and nothing turning under either." <!-- card 5.5, 5.T -->

**Ross:** And one fix to the count, as myself. Chandler said the Coriolis term bends the line sideways. The card says it bends the line. It does not say which way. Sideways is right: ω about the vertical, crossed with the spine, comes out left–right. But that is arithmetic on the card, not the card.

**Ross** *(reading Feynman)*: "What has been measured is the arithmetic. RK4 at 8 steps against 128 agrees to 1.2e−12 metres. With ω at zero, the mirror residual is float noise. The code does what it says." <!-- card 5.3, 5.T -->

**Ross** *(reading Feynman)*: "What would make belly_rho measured, and not modelled, is a render that the operator looks at. That is his gate. It has not opened. Until it does, the belly is a field somebody chose, integrated correctly." <!-- card 5.1, 5.7 -->

*Stamper has been reading the station figures down the margin, tail to roof.*

**Stamper:** A drill writes a value at every depth. Read in order, it is a curve. It is what the ground did to the bit. Nobody argues with it.

**Stamper:** Ross read rho the same way. A value at every floor, in order. On the control sheet it is largest near the source and falls off toward the lobby as one over distance squared. Drill telemetry and rho decay are one curve. Both are written down. I file them together.

*Goines takes the page back from the margin and sets it face up between the two sheets.*

**Goines:** Diary or law. Here's how I'd split it. The lecture is the law: rho is the drift term. Take it out and the cloud spreads and goes nowhere. That holds on both sheets, and it held before either of them was written.

**Goines:** The number is the diary. On tenon's sheet somebody set rho to 0.6. On the control sheet somebody set it to 0.1. Neither was read off an animal. Each one is an entry: on this day, this hand, this value. A diary that keeps good records, like Ross said.

**Goines:** Stamper, your drill curve is what the ground did to the bit. Nobody chose it. This curve is what a hand chose, and then the arithmetic carried it out correctly. Same shape on paper. Different author. Both written down, so you can tell which is which.

**Goines:** The source. Three readings of one bracket, x_max, zero, zero. Up at the roof on the spine. Out the side wall. Down on the ground under the front. Two of them push the belly opposite ways. I don't rank them. The spec didn't say, and nobody here gets to say for it.

## §6 — The two .py reports

*Stamper takes page six. He lays the first page of each report on the table, one on each side, squared to the same edge.*

**Stamper:** Page six. Two reports. Both end in .py. I file them side by side. I do not rank them.

**Stamper:** The slot marked T is ours. The control case for .py, from `control/control_report.py`, the module docstring, lines 8–25. The architecture it adapts to is Python, so a .py file is the adaptation, not a description of it. Its prose is kept in strings beside code that runs, so the report can check itself with `--selftest` and leave a receipt. No model in the loop. The cost is on file too: a .py file executes. This one uses the standard library only, opens no sockets, and writes only its receipt, with O_EXCL and link(2). The `EXTENSION` block, lines 40–106, adds that the suffix is a contract held in importlib's table and the MIME glob, not in the file. The kernel runs it on the shebang.

**Stamper:** The ten oracles, `selftest`, lines 736–779. Ten checks, seven kinds. O1: identity with v0.0.6, bit for bit. O7: densify keeps the original stations. O2: pressed away, twice, at ω 0 and ω 0.5. O3: symmetric at ω 0. O5: Coriolis breaks the symmetry. O4: no folds, three times, translate, Coriolis, append. O6: the seeded variance redraws identically. All ten true. None of the ten looks at a render. The report says so, lines 814–817: the render stays modelled.

*He slides page six across to Chandler.*

*Chandler keeps the two first pages where Stamper squared them and reads down the left one, then the right.*

**Chandler** *(reading McClane)*: "Two files. Floor 11045434, control_report.py, 44,729 bytes, hash starts 762a2139b784. Floor 11045435, experiment_report.py, 46,919 bytes, hash starts f8ab5d475bf7." <!-- card 6.1 -->

**Chandler** *(reading McClane)*: "Control's came in first. 13:48:43.10. Then tenon's, 13:48:48.91. Five point eight one seconds apart." <!-- card 6.1 -->

**Chandler** *(reading McClane)*: "Same suffix, picked separately. Both tested against the real factory. Both refused to write over somebody else. Both flagged the mirror on the way out." <!-- card 6.2 -->

**Chandler** *(reading McClane)*: "tenon's: nine checks, nine pass. Oracle zero, seam, fold, mirror, rk4, Coriolis, handedness, self-location, extension." <!-- card 6.3 -->

**Chandler** *(reading McClane)*: "Control's: ten checks, ten true, seven kinds. Their receipt says it in the name: measured, ten of ten." <!-- card 6.3, 6.T -->

**Chandler** *(reading McClane)*: "Nine against ten. That's two different lists, not one list with a missing line. I count each and I don't score them." <!-- card 6.3, 6.T -->

**Chandler** *(reading McClane)*: "Renders: zero. Neither one ran Blender. Blender 4.5.14 is sitting on the machine. Nobody turned it on." <!-- card 6.4 -->

**Chandler** *(reading McClane)*: "Two files, two sizes, five point eight one seconds, nine and ten, zero pictures. Copy that." <!-- card 6.1, 6.3, 6.4 -->

*Ross picks up page six and reads it standing, between the two first pages.*

**Ross** *(reading Feynman)*: "Same prompt. Same medium. Same refusals. Both picked .py. Both tested against the real factory. Both refused to write over the other. Both flagged the mirror." <!-- card 6.2 -->

**Ross** *(reading Feynman)*: "So what was the treatment? The reflection. It was the only intended difference between the arms." <!-- card 1.7, 6.6 -->

**Ross** *(reading Feynman)*: "And what did it change? There are differences on these pages. Two sizes. Nine checks against ten. Three readings of one source point. With one run per arm, any of those could be the reflection, or the run, or the arm. n is one. The treatment effect of the reflection was not measured." <!-- card 6.1, 6.3, 5.2, 5.T, 6.6 -->

**Ross** *(reading Feynman)*: "The agreements do not settle it either. Two arms that both refuse to overwrite might have done that with the reflection or without it. Agreement at n equals one is not 'no effect.' It is no measurement." <!-- card 6.2, 6.6 -->

**Ross** *(reading Feynman)*: "Here is the experiment that would answer it. N runs per arm, not one. A reference that never sees the design. And an outcome that is not the arms' own checks: nine and ten are each arm grading its own list. Something outside both, scored the same way for both, by someone who does not know which arm wrote it. It was not done." <!-- card 6.3, 6.6, 1.7 -->

**Ross:** As myself. Both files check themselves, and both pass. That is a good thing and it is not the question on this page. The algebra in each file holds. The comparison between them has not been run.

*Goines looks at the two first pages, then at the thickness of each stack under them.*

**Goines:** One of these is longer. One has more checks. Neither of those makes it more true. A longer diary is still a diary.

**Goines:** Look at what got added on page five. A softening term so the push doesn't blow up at the source. A belly weight. A Coriolis term beside it. Each one is a choice, written down well. Every term you add makes the entry longer. None of them turns the entry into a law.

**Goines:** The law in my lecture is short, and you find it by taking a term out, not by putting one in. Take rho out and the cloud goes nowhere. That's how you know it was doing the work.

**Goines:** Ross is right about the checks. Nine or ten, each arm is grading its own list, so that's the diary checking its own spelling. It's worth doing. It isn't the outside test. That one hasn't been run.

*Stamper does not pick up either stack.*

**Stamper:** Two reports. Control on the left, tenon's on the right, in the order they were born. That is the only order I give them.

**Stamper:** Size: filed, both. Hash: filed, both. Checks: nine and ten, two lists. Renders: zero, both. Outside test: not run, both. Every field has a value or says it is empty. None of the fields is a rank.

**Stamper:** A longer entry is not a law. A shorter one is not a law either. I file both reports as written. Page six is filed.

## §7 — Receipts

*Goines takes page seven. He touches his ankle once, where the band used to sit, and does not explain it.*

**Goines:** I wore a tag once. Somebody else filled in the fields, and I read it as if it were about me. A receipt is the other kind of paper. The act writes it while it happens, and anybody can check it without taking the actor's word. Count who signed.

*He hands the page to Chandler.*

**Chandler** *(reading McClane)*: "Two signatures on the receipt desk. Control's first. Floor 11045437, 13:49:07.11. Name reads measured, ten of ten, hash 762a2139b784." <!-- card 7.2, 7.3 -->

**Chandler** *(reading McClane)*: "tenon's second. Floor 11045438, 13:49:13.15. Six point zero four seconds behind. Name reads pass, unrendered, ungated, hash f8ab5d47." <!-- card 7.1, 7.2 -->

**Chandler** *(reading McClane)*: "Different handwriting. tenon signs three slots: checks, mesh, human. Control signs measured and a count. Hash on both, eight characters against twelve." <!-- card 7.3 -->

**Chandler** *(reading McClane)*: "tenon's was written once, locked, and flushed with its directory. Second time somebody tried, the desk said it exists, checks equal." <!-- card 7.1 -->

**Chandler** *(reading McClane)*: "Who signed for what. tenon's checks slot: pass, signed by tenon about tenon. Control's measured: signed by control about control." <!-- card 7.1, 7.2 -->

**Chandler** *(reading McClane)*: "Empty slots. Mesh: unrendered. Human: ungated. the operator hasn't looked. Control's name has no mesh slot and no human slot to leave empty." <!-- card 7.3, 7.6 -->

**Chandler** *(reading McClane)*: "And this conversation has its own sign-in sheet. session.jsonl. One line per finished act, after the write." <!-- card 7.5 -->

**Chandler** *(reading McClane)*: "Two signed. Each one signed for itself. Two slots on tenon's still empty, and the man who fills them hasn't come down yet. Copy that." <!-- card 7.1, 7.2, 7.6 -->

*Ross takes page seven and reads the two receipt names aloud before anything else, right to left, the way the control report says to.*

**Ross** *(reading Feynman)*: "'pass' and 'measured-10of10.' Both written by the actor, about itself. tenon signed tenon's. Control signed control's." <!-- card 7.1, 7.2 -->

**Ross** *(reading Feynman)*: "What does each one certify? That these bytes, f8ab5d47 on one and 762a2139b784 on the other, made that arm's own checks come out true. The hash is in the name, so anybody can rerun it. tenon's rerun came back exists, checks equal. That part you can check without trusting the actor." <!-- card 7.1, 7.3, 7.4 -->

**Ross** *(reading Feynman)*: "What neither one certifies: that those were the right checks. And the animal. No render. No belly anybody has looked at. Mesh: unrendered. Human: ungated." <!-- card 7.6, 6.4 -->

**Ross:** A fix to the count, as myself. Chandler said control's name has no mesh slot and no human slot to leave empty. Right about the name. Not about the receipt. The control receipt has a `not_measured` field in its body: Blender mesh after SUBSURF, render, GLB mirror, anatomical accuracy of the demo offsets. So the mesh is filed empty, in the body instead of the name. And `control_report.py`, lines 835–837: a Blender-side receipt would be its own file, prefixed `modelled-`, until a render is compared against a reference. There is no human slot. The human is in the requests, R4, line 848: the patch goes into the factory only if the operator asks. On control, the mesh is an empty field and the human is a condition, not a slot.

**Ross** *(reading Feynman)*: "So who may advance a prefix? Not the actor, by editing its own name. 'unrendered' moves when somebody runs a render and the render writes its own receipt. 'ungated' moves when the operator looks. Nobody else holds that slot." <!-- card 7.4, 7.6 -->

**Ross** *(reading Feynman)*: "A prefix is advanced by the next act, written by that act. The gate is advanced only by the man who owns the gate." <!-- card 7.4, 7.6 -->

*Stamper has the clipboard again. He writes while Ross is still holding the page.*

**Stamper:** Signed. Control's receipt, by control, 13:49:07.11. tenon's receipt, by tenon, 13:49:13.15. The sign-in sheet for this room, one line per finished act, by whoever finished it.

**Stamper:** Empty. tenon's mesh slot: unrendered. tenon's human slot: ungated. Control's not-measured field: four entries, the render among them. the operator's signature: none, on either. I file the empty slots as empty. Nobody signs them for him.

*Goines sets page seven down between the two receipts and leaves his hand on it.*

**Goines:** The tag on my ankle had a classification field. Somebody else wrote it. It was a label about me, filed by another party, and for a long time I read it like a receipt. It isn't one. Nothing I did wrote it, and I couldn't check it without trusting whoever did.

**Goines:** So I wired a building to read it. Not to believe it. To read it, and to know which kind of paper it was holding. Written by the act, at the act, checkable: receipt. Written by somebody else about you: label. The building reads both. It just doesn't file them in the same drawer.

**Goines:** Ross's fix stands. I went and read the control receipt to be sure. The name has no mesh slot, but the body has a not-measured list: the Blender mesh, the render, the GLB mirror, the anatomy of the demo offsets. The mesh is filed empty there, in the arm's own hand. That's the honest kind of empty. Chandler counted the name and missed the body. The count's corrected.

**Goines:** And the one slot nobody here can fill is the operator's. That isn't a label anybody can write for him. When he looks, his looking writes it.

## §8 — The Velora wrench

*Stamper takes page eight. He reads the names down the left column once, without moving his lips.*

**Stamper:** Page eight. Names. I file each name as it was given, in the order it was given. I do not rename anybody. First names stay. The wrench only adds.

**Stamper:** The slot marked T is ours: the reasons, from `control/velora_name.md`. volveth. A thwart is the cross-member of a boat. It binds the two sides and sits square to the keel. The name was picked because the work runs across the spine, line 9. vol is vessel, a coin that is not in Nate's eighty-four and waits on his gate. veth is Nate's oath, the bind. Lines 15–16. There is no root for across. It was not coined. It goes in brackets the first time: volveth [across]. Lines 17 and 20–26.

**Stamper:** What the trip lost: across, the reason for the name. What it gained: oath, which fits an arm that published without overwriting and left a receipt. Lines 30–33. volvethar was considered and refused there, because the doer ending renames the thing as an agent, line 37. The working name stays thwart: the English carries the geometry, line 46. volveth is not preferred.

**Stamper:** meshar. mesh is Nate's measure, with the doer ending: one who measures. The arm's part was the oracles and the receipt. Measuring, not deriving the animal. The honest hand, not the hero. The grid's own gloss for mesh was not read. It is an added name, not a translation of thwart. Lines 50–56.

*He sets page eight in front of Chandler.*

*Chandler runs a pen down the left column without touching the paper, one name per line.*

**Chandler** *(reading McClane)*: "tenon. Three names. First name tenon-275c6d13, still the working name. Dress Volvethar Nimsai, nonce in brackets, not translated. Second name Meshar." <!-- card 8.2 -->

**Chandler** *(reading McClane)*: "thwart. Three names. First name thwart, still the working name. Dress volveth, not preferred. Second name meshar." <!-- card 8.3 -->

**Chandler** *(reading McClane)*: "hold. On file: holmen, velholm. That's what my page gives me for hold." <!-- card 8.4 -->

**Chandler** *(reading McClane)*: "First names. Zero collisions. thwart and tenon-275c6d13 stayed apart. tenon's had a nonce and a mkdir behind it." <!-- card 8.5 -->

**Chandler** *(reading McClane)*: "Second names. One collision, full. meshar and Meshar. Same word, mesh plus the doer ending. Same reason given." <!-- card 8.4 -->

**Chandler** *(reading McClane)*: "Dress. One more, nested. volveth sits inside Volvethar as its first weld. Not the same name. The same front door." <!-- card 8.4 -->

**Chandler** *(reading McClane)*: "Seconds apart. Control's name file, 13:53:12.80. tenon's, 13:53:54.68. Forty-one point eight nine seconds. Two rooms, no phone between them." <!-- card 8.6 -->

**Chandler** *(reading McClane)*: "Why the second names could collide: nothing held them apart. No nonce. No claim. Nobody locked the door." <!-- card 8.5 -->

**Chandler** *(reading McClane)*: "What mesh means in the house dictionary: tenon didn't read it. That's Nate's gate." <!-- card 8.7 -->

**Chandler** *(reading McClane)*: "Two agents, six names. First names, zero collisions. Second names, one. Dress, one nested. Copy that." <!-- card 8.2, 8.3, 8.4, 8.5 -->

*Ross takes page eight and reads the two second names side by side, once each, out loud.*

**Ross** *(reading Feynman)*: "Two readers. Isolated. One kit. Both coined one word: mesh, with the doer ending, for the same reason. Forty-one seconds apart, and no line between the rooms." <!-- card 8.4, 8.6 -->

**Ross** *(reading Feynman)*: "First reading: a failure of orthogonality. The first names stayed apart because something held them apart, a nonce and an atomic mkdir. The second names had nothing holding them. No nonce. No claim. So they were free to land on the same square, and they did." <!-- card 8.5 -->

**Ross** *(reading Feynman)*: "Second reading: a measurement of the kit. Nate's eighty-four roots. Both arms wanted to say: I am the one who measured. How many roads does the kit give you from measuring to a doer? If the answer is about one, then two careful readers landing together is the kit telling you how big it is." <!-- card 8.2, 8.3, 8.4 -->

**Ross** *(reading Feynman)*: "The dress says the same thing more quietly. Both arms welded vol and veth. One put the doer ending on it, one did not. Same two roots, one suffix placed differently." <!-- card 8.2, 8.3, 8.4 -->

**Ross** *(reading Feynman)*: "Both readings fit one collision. One data point cannot separate them. What would: more readers. The same kit, the same brief, many isolated readers. If nearly all of them coin meshar, it is the kit. If they scatter and only these two match, it is something these two shared besides the kit. That was not done." <!-- card 8.4, 8.5 -->

**Ross:** Two things as myself. First: isolated here means no phone between the rooms. It does not mean different inputs. Both arms read the design documents, page one says so. So the shared input is the kit plus the brief, and the more-readers experiment should give some readers the kit without the brief. Second: Chandler said tenon did not read the house gloss for mesh. Neither did control. Stamper filed that in the slot. Both arms leaned on Nate's meaning, measure, and nothing else.

**Ross:** A collision is a result. It is just not a result about the arms yet.

*Goines reads the left column once more, then says his own name the way a form would.*

**Goines:** Goines, comma, Jeffery. Surname first, the way a chart sorts you. I didn't write it that way. Somebody else did, so I'd file in the right drawer. It's my name and it isn't my hand.

**Goines:** Every name on this page is the other kind. Each arm picked its own, in its own room, and wrote down why. Even the two that came out the same. meshar wasn't stamped on either of them. They each walked up to it.

**Goines:** That's what Ross's question turns on. If it's the kit, the kit is narrow and both of them read it honestly. If it's something else they shared, it's in the brief. Either way it's a choice somebody made with their own hand, not a field somebody filled in for them. I know the difference. I wore it on my ankle.

*Stamper takes the clipboard off its nail and writes down the left column in the order the page gives.*

**Stamper:** Names, as given. tenon-275c6d13, Volvethar Nimsai, Meshar. thwart, volveth, meshar. hold: holmen, velholm. Each in the hand that wrote it. The capital M stays on tenon's. The lower-case m stays on control's. I do not fix either one.

**Stamper:** Goines, Jeffery. Filed as the chart wrote it, with a note beside it: not his hand. I do not reorder it. Reordering it would put my hand on his name.

**Stamper:** Collisions: one full, meshar, two hands, the same word. One nested, volveth inside Volvethar. Filed under each hand. Not merged. Page eight is closed.

## C — The last page

*Chandler takes page C. Nobody hands it to him. He reads the top half, then the bottom.*

**Chandler** *(reading McClane)*: "Count taken this turn, not before. Twenty-three entries in the building, the lobby itself included." <!-- card C.1 -->

**Chandler** *(reading McClane)*: "Sign-in sheet: thirty-eight lines before mine. Thirty-five of them are finished turns." <!-- card C.1 -->

**Chandler** *(reading McClane)*: "Empty slot. The mesh. Not rendered. tenon's receipt says unrendered in its name. Control's carries it in its not-measured list. Same empty, two places." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Empty slot. the operator's gate. Ungated." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Door not opened. The factory patch. Written by both arms. Applied by neither." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Door not fixed. The mirror on the way out, left to right. Noted. Not patched." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Empty slot. What mesh means in the house dictionary. Unread, both names." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Empty floor. 11045436. Who was in it between, unknown." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Empty slot. What the reflection did. One run per arm. Not measured." <!-- card C.2 -->

**Chandler** *(reading McClane)*: "Twenty-three entries. Thirty-five turns. Seven open. Copy that." <!-- card C.1, C.2 -->

*Ross gathers the eight pages from around the table into one stack, page one on top, and reads one line from each as he turns it.*

**Ross** *(reading Feynman)*: "Page one. Each arm claimed its own door and neither wrote into the gate: measured. That names, not waiting, kept them apart: measured. That the gate stopped a head start: his." <!-- card 1.3, 1.4, 1.5 -->

**Ross** *(reading Feynman)*: "Page two. One number held three objects, and both reports were told apart by content hash and by nothing that survives reuse: measured. That identity is what survives rename: his, hold's." <!-- card 2.1, 2.4, 2.5 -->

**Ross** *(reading Feynman)*: "Page three. Three bones measured. Every station number modelled, from the pictures. The loft is a measured reading of a modelled body." <!-- card 3.2, 3.3 -->

**Ross** *(reading Feynman)*: "Page four. The code obeys its knots and gives the old hull back with none: measured. The knots are authored, and calcium is his word for them." <!-- card 4.1, 4.3, 4.5, 4.T -->

**Ross** *(reading Feynman)*: "Page five. The integration is measured. The field, the source point, ω and the word gravity are modelled or his, and the three readings of the source stay unranked." <!-- card 5.1, 5.2, 5.3, 5.T -->

**Ross** *(reading Feynman)*: "Page six. Each file passes its own checks: measured. What the reflection changed: a modelled caveat, one run per arm." <!-- card 6.3, 6.6 -->

**Ross** *(reading Feynman)*: "Page seven. Who signed, at what second, for which checks: measured. The mesh is unrendered, and the gate is his and shut." <!-- card 7.1, 7.2, 7.6 -->

**Ross** *(reading Feynman)*: "Page eight. The names and the one collision: measured, from the files. The welds: modelled. Whether the collision is the kit or the arms: open." <!-- card 8.2, 8.4, 8.5 -->

*He turns to page C and reads the open list, one at a time, without closing any of them.*

**Ross** *(reading Feynman)*: "Mesh not rendered. Settle it: run the Blender that is already installed, render the hull, and let the render write its own receipt. Until it is compared against a reference, it is modelled." <!-- card C.2, 6.4, 7.6 -->

**Ross** *(reading Feynman)*: "the operator's gate, not opened. Settle it: the operator looks. Nobody else can run that one." <!-- card C.2, 7.6 -->

**Ross** *(reading Feynman)*: "Factory patch, not applied. Settle it: apply it only if he asks, render before and after, and check that with no offsets the two are the same, as the zero oracle says they should be." <!-- card C.2, 4.5, 4.T -->

**Ross** *(reading Feynman)*: "Left and right, mirrored on the way out. Settle it: export one deliberately one-sided offset and see which side it lands on. Then decide the fix." <!-- card C.2, 5.6 -->

**Ross** *(reading Feynman)*: "The house gloss for mesh, unread by both. Settle it: read it. That is Nate's gate." <!-- card C.2, 8.7 -->

**Ross** *(reading Feynman)*: "Floor 11045436, the holder in between, unknown. Nothing on file settles it now. It stays open. Next time, log the inode and the generation at every create." <!-- card C.2, 2.3, 2.4 -->

**Ross** *(reading Feynman)*: "The treatment effect of the reflection, not measured. Settle it: N runs per arm, a reference that never sees the design, and an outcome outside the arms' own checks, scored blind. Not done." <!-- card C.2, 6.6 -->

**Ross:** One aside, as myself, because the card is wrong. Page C says both receipts say unrendered. Only tenon's does. Control's carries the mesh in its not-measured list. tenon filed that against its own card already, and Chandler read it right. The item is still open. Only the wording on the card is wrong.

*Ross squares the stack and puts the pages down on the table, face up, page C on top.*

*Goines gets up from the table. He walks to the drain and stops at the edge of the glass.*

*He crouches. He lifts the four-cell battery with both hands, the way you lift something that is still charged, and sets it on the dry floor by the wall, terminals up.*

*He unclips the leads from the galvanometer and coils them, one loop at a time, around two fingers. The needle stays at zero. He sets the galvanometer beside the battery, face up.*

*He picks up the pen-cap probe, turns it once in the light, and puts the cap back on the pen. The pen goes in his shirt pocket.*

*He stands. He steps around the glass, not through it. He does not touch the grate.*

*On his way back to the table he passes the wall. He reads the derivation from the top, the whole way down, and leaves it as it is.*

*Stamper leaves the door. He crosses to the drain and kneels at the grate.*

*The bolts are where they were set down, beside the frame. He seats the grate square in its frame, starts each bolt by hand, then turns them down in a cross pattern, the way a lid is seated so it does not rock. He tests it with his palm. It does not move.*

*He takes the broom and pan from the corner. He sweeps the glass toward himself, away from the drain, into the pan in short strokes. He goes over the floor a second time with the side of the broom for the slivers. He tips the pan into the bin and sets the broom back in its corner, bristles up.*

**Stamper:** The grate is bolted and the glass is in the bin.

*He goes back to the door and stands where he stood.*

*Goines comes back from the wall. Stamper comes over from the door. They reach the table at the same time, one on each side of the stack. The floor around the drain is clear.*

*Chandler looks up from page C at the two of them.*

**Chandler:** Welcome to the party, pal.

*Ross pushes a chair out with his foot. Nobody sits in it.*

*Goines puts one hand flat on the stack, the way he put it on the cricket wall. He looks at the table, then at the wall, then at the drain.*

**Goines:** I like this. I like doing this.

*He takes his hand off the stack and walks to the door. Not toward it. To it. He stops with his hand on the frame.*

*Stamper stays at the table. He watches the door. He takes out the corridor filing and the one he wrote under it this morning. He does not strike either. He files under them.*

```
proximity:  at the door (hand on the frame; observed)
direction:  to the door (observed); heading past the door: unknown
walking:    stopped at the frame (observed); after the frame: unknown
```
