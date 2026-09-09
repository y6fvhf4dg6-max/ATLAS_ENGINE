# Female Identity + Anatomical Neck — Rodin V2.5 Approved

DATE=2026-09-09
PROVIDER=fal.ai
ENDPOINT=fal-ai/hyper3d/rodin/v2.5
TIER=Gen-2.5-High
COST_USD=0.40
SEED=42
OUTPUT_FORMAT=glb
MATERIAL=All
QUALITY_MESH=Auto
TEXTURE_MODE=Default
CREATIVE_MODE=OFF
HD_TEXTURE=OFF
TEXTURE_DELIGHT=OFF
T_A_POSE=OFF
BBOX_WIDTH=0
BBOX_HEIGHT=0
BBOX_LENGTH=0
HIGH_PACK=OFF
PREVIEW_RENDER=OFF

## Ordered inputs

1. inputs/01_front.png
2. inputs/02_left_three_quarter.png
3. inputs/03_right_three_quarter.png
4. inputs/04_left_profile.png
5. inputs/05_rear.png

## Exact accepted prompt

Create an identity-faithful 3D head-and-neck bust of the exact mature woman in these five views. Preserve her real age, asymmetry, eyelids, eye spacing, long prominent nose, cheeks, mouth, jaw, chin, ears and oval-long skull. Do not beautify, rejuvenate, stylize, flatten or deform her face or skull. Keep her gray-white hair in the same compact high bun, fully exposing the nape and rear neck. Create a narrow anatomical human neck with a short natural transition to the clavicles and upper shoulders. No wide neck shelf, funnel, floating head, clothing, jewelry or accessories. Neutral closed mouth, upright centered head, continuous geometry.

## Human gates

IDENTITY_AND_SKULL=PASS
ANATOMICAL_NECK=PASS
NAPE_AND_REAR_NECK_VISIBILITY=PASS
EXACT_WELD_SHAPE_PRESERVATION=PASS

## Geometry audit

SOURCE_VERTICES=346450
SOURCE_FACES=500000
SOURCE_EXACT_DUPLICATE_VERTICES=96458
SOURCE_NONMANIFOLD_EDGES=0
WELDED_VERTICES=249992
WELDED_FACES=500000
WELDED_BOUNDARY_EDGES=0
WELDED_NONMANIFOLD_EDGES=0
WELDED_WATERTIGHT=True
WELDED_WINDING_CONSISTENT=True
MAX_VERTEX_DELTA=0
SHAPE_PRESERVATION_GATE=True

## Safety

SOURCE_TEXTURED_GLB=REFERENCE_AND_ARCHIVE
GEOMETRY_ONLY_EXACT_WELD=APPROVED_PRODUCTION_GEOMETRY
OLD_170_LOOP_RETOPO=REJECTED_DO_NOT_REOPEN
PHASE9_AUTHORIZATION=NO
STAGE_OR_COMMIT_PERFORMED=NO

See SHA256SUMS.txt for locked hashes.
