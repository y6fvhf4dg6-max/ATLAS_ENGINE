# P-3/P-4 Male Head/Body Bridge Evidence — 2026-09-07

## Scope

This directory preserves the authorized technical bridge experiment using:

- the identity-surviving Rodin V2.5 synthetic male candidate; and
- a newly verified generic male MakeHuman technical body donor.

This checkpoint does not select Rodin as a production provider and does not
authorize production geometry, a real-customer upload, product launch or
Phase 9.

## Corrected source boundary

An earlier temporary dry-fit mistakenly used the locked Meshy V7 female head
as if it were the male subject. That dry-fit is rejected and must not be
resumed:

`WRONG_MESHY_FEMALE_DRYFIT = REJECTED / WRONG_SUBJECT`

The correct identity source is:

`RODIN_MALE_SOURCE = VERIFIED`

Canonical Rodin PBR SHA-256:

`7c77a4e915d6b6a6a34b0dadad962c4874f88eb53b499d1f82d378ab7a12c50d`

Geometry-equivalent shaded SHA-256:

`c71e85f39ee8aa61fd5288a7f10813e354fc9ea516c2fd76504a822d8f371dac`

## MakeHuman male body donor

The earlier compact MakeHuman body was not accepted as male because the raw
MakeHuman default is gender `0.5`, which is neutral.

The replacement body was built with the verified default ethnicity blend:

- African male young: `1/3`;
- Asian male young: `1/3`;
- Caucasian male young: `1/3`;
- average muscle and weight;
- the previously measured compact normal-proportion target stack.

Output:

`atlas_p3_p4_makehuman_generic_male_compact_body_v1.glb`

SHA-256:

`273fb03792ea7078f6a018139ee0511659d6bfdf7df44b10c42052a81bc418ad`

Measured result:

- vertices: `13380`;
- faces: `26756`;
- connected components: `1`;
- watertight: `YES`;
- winding consistent: `YES`.

Human decision:

`MALE_BODY_VISUAL_DECISION = PASS_AS_TECHNICAL_DONOR`

This is a generic male technical donor. It is not evidence of subject-specific
body likeness.

## Rodin male geometry findings

PBR and shaded variants contain exactly equal vertex and face arrays.

Geometry signature:

`6ef6bdfcb088d06d83a8fc3341675b79e9f18d035dda04cc3bdea005c3ec6bb4`

Measured source:

- vertices: `45116`;
- faces: `50000`;
- vertical axis: `Y`;
- raw apparent components: `4781`, caused by duplicated export seams;
- exact-position diagnostic weld vertices: `24996`;
- diagnostic-weld components: `1`;
- diagnostic-weld boundary edges: `0`;
- diagnostic-weld non-manifold edges: `0`;
- diagnostic-weld watertight: `YES`;
- diagnostic-weld winding consistent: `YES`.

No diagnostic weld was exported over the source.

## Visual envelope and neck-plane state

The Rodin source contains:

- head and hair;
- natural neck;
- shirt collar;
- shoulders;
- squared bust base.

The current candidate route is to retain the head and natural neck while
excluding the shirt, shoulders and bust base.

Lower-neck section audit:

- `Y=-0.350`: single closed loop and numeric minimum;
- `Y=-0.325`: rejected because a secondary loop appears;
- `Y=-0.300`: single closed loop but materially greater section depth;
- `Y=-0.375`: lower visual comparison candidate.

Current state:

`NUMERIC_CUT_LEADER = Y_-0.350`

`HUMAN_CUT_PLANE_DECISION = PENDING`

`CUT_PERFORMED = NO`

`MAKEHUMAN_BODY_ATTACHED = NO`

## Evidence files

The directory contains:

- reproducible MakeHuman male body build and render scripts;
- the male MakeHuman GLB candidate;
- male body visual evidence;
- lightweight Rodin GLB structure evidence;
- texture-free Rodin geometry evidence;
- Rodin four-view source evidence;
- lower-neck cross-section evidence;
- the three-plane visual decision image;
- associated execution logs;
- `SHA256SUMS.txt`.

## Exact resume point

At the next session, begin with the saved cut-plane comparison image:

`atlas_p3_p4_rodin_male_neck_cut_plane_candidates_v1.png`

Ask the user to visually select or reject:

1. `Y=-0.375`;
2. `Y=-0.350` — current numeric recommendation;
3. `Y=-0.300`.

Only after the human cut-plane decision may a new temporary cropped Rodin
head-and-natural-neck candidate be generated. That candidate must remain
diagnostic and must not be described as production geometry.

## Authority boundary

`CURRENT_WORK_PROGRAM = P-3/P-4 TECHNICAL BRIDGE EXPERIMENT`

`PRIMARY_PROVIDER_ROUTE = NOT_SELECTED`

`FALLBACK_PROVIDER_ROUTE = NOT_SELECTED`

`REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_APPROVED_VENDOR_ROUTE`

`PRODUCTION_GEOMETRY_AUTHORIZATION = NO`

`PRODUCT_LAUNCH_AUTHORIZATION = NO`

`PHASE9 = NOT_AUTHORIZED / NOT_STARTED`

`EXTERNAL_PROVIDER_CALL = NO`
