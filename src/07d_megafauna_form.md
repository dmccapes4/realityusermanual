# Reflection — megafauna as geometric form

Kangaroo Park is not a research toy that happened to get a dinosaur. It is the long way around a phone.

The operator’s son asked to see dinosaurs on the phone. The phone is a rooted Moto G Play 2024. The operator had already outlawed the usual videos, and still does. The reason is specific. A height-comparison clip — dinosaur against modern animal — opened on weigh-ins. The title was accurate. The inference from title plus first minutes was that the video compared scale. It did not. It became combat. A velociraptor’s killing blow to the neck of a polar bear already on its knees. So much blood. The kids enjoyed it. Providing that video after watching only the weigh-in was careless parenting. The title told a true kind of truth and a dishonest one at the same time.

The park is the replacement. A controlled safari. Godot on that phone. High-fidelity enough that the animal is an animal, not a weigh-in that turns into a kill. The geometry has to be good enough that a child can look at Diamantinasaurus and see a body, not a cartoon of combat.

We are mid-process. The geometry is being built so that the geometry can be expressed so that Godot can render a simulation the operator calls Kangaroo Park.

## What we actually built

One animal is one JSONL spec. The factory (`poly_factory.py`) reads segments and builds a mesh in Blender. Spec is Y-up, +Z forward, metres. Blender is Z-up, +Y forward. Skin is a generated tile (AODF 0888 hexagons, measured on this genus). TLRD is one-shot review. No agentic loop that lets one model edit another model’s spec. That loop was tried (TartarusLoop, 2026-10-11) and spent money to get worse.

Australotitan came first: 27 m modelled, femur EMF164 2.146 m measured. Twenty-two segments. Three torso ellipsoids overlapping on purpose. It looked like three beads.

Diamantinasaurus (Matilda) was the second animal. Holotype AODF 0603. Measured: femur 1.345 m, humerus 1.068 m, ulna 0.700 m. Body 16 m modelled (2009). The first cut was Australotitan × 16/27. the operator said: that is the Australotitan. Correct. Uniform scale of a template is not a second animal.

Then the factory fused hip / body / chest as metaballs. First hull was a pill. Second was a peanut. The three-blob problem was not a threshold setting. Three ellipsoids cannot be a sauropod.

Then a cricket wall — not the chimney saddle (two planes, IRC table, 30-inch trigger). The one that spans a wall that drops a level: 2×4s farther out on the sides, bowed. On a flat roof that is a perimeter / hogback cricket. The useful object was the rib: run `r`, rise `h`, angle `atan(h/r)`. Conform the cricket to the animal, not to municipal code.

v0.0.6 put eight stations along Matilda’s spine from the side and above paleoart. One hull. First numbers were a sausage. Second numbers deepened the belly and raised the withers. the operator: “that is looking much more natural.” It is still a plump bean. Neck and tail are still sticks. The torso is no longer three blobs. That is the mid-process we are in.

## What the form is for

The safari cannot be the weigh-in video with the killing blow removed. It has to be a different object. A child looking at a titanosaur should see a body that was walked by a real animal, rebuilt from measured bones and modelled length, with the modelled parts labelled. Combat is not a measurement. Scale comparison that turns into blood is not education. The geometry is the refusal of that video, written in metres.

offset_spine and belly_rho, if they are built, are not a treatise on rooftop drainage as biology. They are variance as choice: the cricket rib can be pressed, the spine can leave a straight line, calcium can be appended off the template. rho stays lower-case. It is a drift coefficient, not a name.

This reflection is the journey. It is not the derivation. The derivation is a later file, written by someone who is not hold, against `poly_factory.py` and `art/specs/diamantinasaurus.jsonl`.
