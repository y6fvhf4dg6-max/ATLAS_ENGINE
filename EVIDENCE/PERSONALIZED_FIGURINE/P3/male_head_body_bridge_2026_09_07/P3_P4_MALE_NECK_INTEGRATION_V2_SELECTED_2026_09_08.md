# P-3/P-4 Male Neck Integration — V2 Selected

Date: 2026-09-08

## Decision

`V2_NECK_INTEGRATION = PASS / SELECTED`

Selected persistent geometry:

`EVIDENCE/PERSONALIZED_FIGURINE/P3/male_head_body_bridge_2026_09_07/atlas_p3_p4_rodin_makehuman_neck_integration_v2_SELECTED_2026_09_08.glb`

SHA256:

`40fe3757ea28c23d30260f9977db403a5a894f4837c99e48edc7833e42312c1c`

## Locked Geometry State

- Rodin male head source retained.
- Rodin true cut plane: `Y=-0.350`.
- MakeHuman body true neck cut: `Y=6.500`.
- Head rigid pose: `DZ=-0.125` relative to V1 baseline.
- Global head pose is locked.
- Head/body joined through seam-aware local `249 -> 46` retriangulation.
- Candidate is watertight and winding-consistent.
- No production geometry authorization.
- Phase 9 remains NOT AUTHORIZED.

## Accepted Technical Gates

- Rodin true cut: PASS.
- MakeHuman true cut: PASS.
- Local body upper-neck interface correction: PASS.
- Exact contour coincidence diagnosis: PASS.
- Body first inner-ring topology gate: PASS.
- Seam-aware retriangulation V2: PASS.
- Final topology:
  - boundary edges: `0`
  - nonmanifold edges: `0`
  - zero/near-zero faces: `0`
  - watertight: `True`
  - winding consistent: `True`

## Seam-Aware V2 Metrics

Upper Rodin seam:

- mean: `12.483651 deg`
- P95: `30.768255 deg`
- max: `41.874131 deg`

Lower MakeHuman seam:

- mean: `9.055577 deg`
- P95: `22.035626 deg`
- max: `27.648179 deg`
- edges >30 deg: `0`

The prior lower-front pathological folds were removed:

- V1 lower max: `167.296 deg`
- V2 lower max: `27.648179 deg`

## 150 mm Physical-Scale Verification

Correct native vertical axis: `Y`.

V2 native height:

`16.154171944`

True scale at nominal 150 mm figure height:

`9.285527016 mm/native-unit`

Earlier temporary `100 mm/native-unit` working assumption overstated dimensions by:

`10.769448x`

Rescaled neck/interface quantities at 150 mm:

- previous posterior mean overhang: `0.411906 mm`
- previous posterior max overhang: `0.547475 mm`
- boundary correction mean: `0.244209 mm`
- boundary correction P95: `0.544875 mm`
- boundary correction max: `0.742656 mm`
- seam-to-inner-ring mean transition height: `0.552832 mm`

## Visual Decision

- Front: PASS.
- Profile: PASS.
- Back: PASS with minor sub-millimeter residual.
- Smooth shading demonstrated that most front fan/triangle appearance was shading-related rather than a critical geometric seam failure.
- Overall 150 mm neck-integration gate: PASS.

## Rejected / Inactive Experiments

### Back-sector controlled fairing V1

Rejected because it worsened upper Rodin seam continuity:

- V2 upper P95: `30.768255 deg`
- fairing upper P95: `36.486196 deg`
- V2 upper max: `41.874131 deg`
- fairing upper max: `50.927859 deg`

### Single tangent-support ring V1

Rejected / no export because discontinuity was transferred downward:

- upper Rodin seam improved strongly,
- support seam P95 became `105.576350 deg`,
- lower MakeHuman seam P95 became `142.428329 deg`,
- lower max became `144.006152 deg`.

Therefore the authoritative selected neck-integration geometry remains seam-aware V2.

## Status

`P3_P4_MALE_NECK_INTEGRATION_V2_SELECTED_2026_09_08`

Production geometry: NOT AUTHORIZED.

Phase 9: NOT AUTHORIZED.
