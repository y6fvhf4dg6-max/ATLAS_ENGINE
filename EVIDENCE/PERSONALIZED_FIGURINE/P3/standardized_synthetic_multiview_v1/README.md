# P-3 Standardized Synthetic Male/Female Multiview Benchmark V1

**Decision date:** `2026-09-07`

**User decision:** `MALE_AND_FEMALE_SETS_APPROVED`

`STATUS = LOCKED_SYNTHETIC_BENCHMARK_INPUT`

## Assets

- one entirely synthetic adult male identity contact sheet and five extracted views;
- one entirely synthetic adult female identity contact sheet and five extracted views.

Each extracted view is a lossless 432 by 724 pixel PNG derived from its accepted
2172 by 724 pixel five-panel contact sheet.

## View contract

1. `profile_left`
2. `three_quarter_left`
3. `front`
4. `three_quarter_right`
5. `profile_right`

Both subjects use the same view ordering and extracted image dimensions.

## Provenance

- both identities were generated specifically as fictional benchmark subjects;
- no real customer photograph was used as generation input;
- the user visually reviewed and accepted both multiview contact sheets;
- `SHA256SUMS.txt` locks all ten extracted provider-input files.

`REAL_PERSON_IMAGE_INCLUDED = NO`

`EXTERNAL_REAL_PERSON_TRANSFER = NOT_AUTHORIZED`

## Use boundary

- the set may be used for equivalent technical comparison of candidate providers;
- male and female provider results shall be evaluated separately;
- success for only one subject cannot establish a passing generation route;
- generated output remains subject to identity, geometry, cost, latency, privacy,
  licensing and human-correction review.

This evidence set authorizes benchmark comparison only. It does not authorize
production geometry, commercial launch or real-customer transfer.

`GATE_P3 = NOT_YET_DECIDED`

`GENERATION_ROUTE_SELECTED = NO`

`NEXT_P3_ACTION = RUN_EQUIVALENT_SYNTHETIC_PROVIDER_BENCHMARKS`
