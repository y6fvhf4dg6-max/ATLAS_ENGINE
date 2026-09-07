# P-3 Authorized Local Male/Female Identity Benchmark Evidence

**Decision date:** `2026-09-07`

**User confirmation:** `APPROVED`

## Subject mapping

- `subject_01 = USER / MALE_REFERENCE`
- `subject_02 = USER_SPOUSE / FEMALE_REFERENCE`

The user confirmed that both depicted persons authorize use of these photographs
for local ATLAS research and benchmark evaluation.

## Authorization boundary

`LOCAL_ATLAS_RESEARCH_AUTHORIZED = YES`

`EXTERNAL_PROVIDER_UPLOAD_AUTHORIZED = NO`

`REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_APPROVED_VENDOR_ROUTE`

This record does not authorize publication, repository inclusion of the source
photographs, model training, commercial provider transfer or unrestricted reuse.

Any later external transfer requires:

1. a formally approved provider route;
2. provider-specific privacy, licensing and retention verification;
3. a new explicit transfer authorization naming that provider.

## Local evidence files

| Subject | View | Local path | SHA-256 |
|---|---|---|---|
| subject_01 | front | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_01_front.jpeg` | `c44586f9eff8b44a604639c68c3e7544a8238ad58086d669cf3a3ff1870cdbf7` |
| subject_01 | side_a | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_01_side_a.jpeg` | `61a33585448b02f3a2bea36a45cf8ca2d9ee289caf9186552eae878077d1ef52` |
| subject_01 | side_b | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_01_side_b.jpeg` | `2085a2d38a52e17f131cceca4436234c05c3ae2b63ba1d3d46ecd50b4248de93` |
| subject_02 | front | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_02_front.jpeg` | `8361003b873969f56e43541a113aed3fb1b03aea31de8d62b6df87b1af24c7af` |
| subject_02 | side_a | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_02_side_a.jpeg` | `f45ad6e89e493d6ad2bfad3de7645706c0ef79a71aafa6c57d1e06ad504e74df` |
| subject_02 | side_b | `Data/PORTRAIT/phase8_10_flame_multiview_benchmark/subject_02_side_b.jpeg` | `0605fb71c142bf35af789c51ad98aaf5d8f586962aebc81e5a3278350e91436b` |

## P-3 use

- male and female performance shall be evaluated separately;
- a provider cannot pass solely because it succeeds for one subject;
- identity, hair, age character, profile consistency and correction burden
  shall be recorded independently;
- these real-person files remain local-only while provider approval is pending.

`EVIDENCE_SET_STATUS = AUTHORIZED_FOR_LOCAL_P3_BENCHMARK_ONLY`

## User-approved capture qualification

**Qualification decision:** `2026-09-07`

**User decision:** `APPROVED`

`SUBJECT_01_CAPTURE_CLASS = MULTIVIEW_PARTIAL`

`SUBJECT_02_CAPTURE_CLASS = MULTIVIEW_PARTIAL`

`LOCAL_REAL_SUBJECT_REFERENCE = USABLE_WITH_LIMITATIONS`

The two sets contain one frontal view and two oblique/three-quarter views per
subject. They do not contain verified true-profile views and therefore shall not
be represented as preferred complete multiview capture.

Verified supporting evidence:

- every image is 1536 by 1152 pixels;
- MediaPipe produced 478 landmarks with recorded confidence 1.0 for every view;
- landmark source-image hashes match all six authorized local photographs;
- raw diagnostic luminance, clipping, landmark bounding-box and uncalibrated
  Laplacian measurements were produced without modifying the source files.

The raw diagnostic measurements are not ATLAS gate scores because no implemented
metric producer currently owns the required calibrated face-coverage, occlusion,
blur and perspective-distortion observations.

`PREFERRED_MULTIVIEW_CLAIM = NO`

`FUTURE_RECAPTURE = TRUE_LEFT_AND_RIGHT_PROFILE_RECOMMENDED`

Equivalent external-provider comparison shall use standardized synthetic male
and female evidence until a provider route and a new explicit transfer
authorization are approved.

`EXTERNAL_PROVIDER_BENCHMARK_INPUT = STANDARDIZED_SYNTHETIC_MALE_AND_FEMALE`

`EXTERNAL_REAL_PERSON_TRANSFER = NOT_AUTHORIZED`
