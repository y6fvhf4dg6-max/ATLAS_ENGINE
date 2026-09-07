# ATLAS P-3 — Rodin V2.5 Synthetic Benchmark Evidence

**Execution date:** `2026-09-07`

**Provider route:** `fal-ai/hyper3d/rodin/v2.5`

`BENCHMARK_INPUT_CLASS = STANDARDIZED_SYNTHETIC`

`REAL_PERSON_IMAGE_INCLUDED = NO`

## Male execution

- input: five approved synthetic male views;
- tier: `Gen-2.5-Minimum`;
- geometry format: `glb`;
- material: `All`;
- quality mesh option: `50K Quad`;
- texture mode: `high`;
- creative mode: off;
- HD texture: off;
- HighPack: off;
- charged cost: `USD 0.40`.

Downloaded output:

- one PBR GLB;
- one shaded GLB;
- one provider preview.

Measured geometry:

- source vertices: `45116`;
- faces: `50000`;
- coincident vertices after diagnostic weld: `24996`;
- boundary edges after diagnostic weld: `0`;
- non-manifold edges after diagnostic weld: `0`;
- watertight after diagnostic weld: `YES`;
- winding consistent: `YES`;
- degenerate triangles: `0`.

## Human identity decision

**User decision:** `BORDERLINE ACCEPT+`

`MALE_HUMAN_IDENTITY_DECISION = BORDERLINE_ACCEPT_PLUS`

`MALE_IDENTITY_SURVIVING_CANDIDATE = YES`

`MALE_PRODUCTION_READY = NO`

`MALE_CORRECTION_BURDEN = MATERIAL_HAIR_AND_FACIAL_DETAIL`

This result survives the initial identity gate for continued benchmark analysis.
It does not authorize route selection, production geometry or commercial launch.

## Synthetic female benchmark

The same locked Rodin V2.5 configuration used for the synthetic male benchmark was used:

- tier: `Gen-2.5-Minimum`;
- geometry: `GLB`;
- material: `All`;
- mesh option: `50K Quad`;
- texture mode: `high`;
- creative mode: `OFF`;
- HD texture: `OFF`;
- Texture Delight: `OFF`;
- prompt: blank;
- charged cost: `USD 0.40`.

Downloaded output:

- one PBR GLB;
- one shaded GLB;
- one provider preview.

Measured geometry:

- source vertices: `43854`;
- faces: `50000`;
- vertices after diagnostic weld: `27014`;
- merged vertices: `16840`;
- boundary edges after diagnostic weld: `3920`;
- non-manifold edges after diagnostic weld: `0`;
- watertight after diagnostic weld: `NO`;
- winding consistent: `YES`;
- degenerate triangles: `0`.

## Female human identity decision

**User decision:** `REJECT`

`FEMALE_HUMAN_IDENTITY_DECISION = REJECT`

`FEMALE_IDENTITY_SURVIVING_CANDIDATE = NO`

`FEMALE_PRODUCTION_READY = NO`

`FEMALE_PRIMARY_FAILURE = IDENTITY_LOSS_AND_OPEN_TOPOLOGY`

The neutral geometry loses material age characteristics and distinguishing facial identity.
The female result does not survive the identity gate and cannot authorize route selection,
production geometry or commercial launch.
