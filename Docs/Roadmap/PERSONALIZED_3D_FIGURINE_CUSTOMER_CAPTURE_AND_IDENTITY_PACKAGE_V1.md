# ATLAS — Personalized 3D Figurine Customer Capture and Identity Package V1

Status: APPROVED_CONTRACT_BASELINE
Production authorization: NO
Legal status: OPERATIONAL_BASELINE_REQUIRES_PROFESSIONAL_LEGAL_REVIEW

## 1. Customer capture package

### Required minimum for one person

1. clear frontal face photograph;
2. left three-quarter face photograph;
3. right three-quarter face photograph;
4. full-body or requested-pose photograph;
5. clothing reference or explicit approved catalog-clothing selection.

### Strongly recommended

- left and right true profiles;
- rear hair/head photograph;
- neutral-expression face;
- smiling/expression reference when requested;
- close hairline, ears, glasses, beard or distinctive-mark references;
- separate color reference under neutral lighting.

A single photograph may be accepted only as:

`LIMITED_EVIDENCE / HIGHER_UNCERTAINTY`

It shall not be represented as equivalent to preferred multiview capture.

### Multi-person products

PF-3 requires an independently approved capture and identity package for every
depicted person. A group photograph may support relationship, pose and scale,
but shall not replace individual identity photographs.

## 2. Automated input-quality gate

Existing ATLAS owners:

- AtlasPortraitInputEvidence;
- AtlasPortraitInputEvidenceSet;
- AtlasPortraitInputQualityObservation;
- AtlasPortraitInputUsabilityGate.

The gate evaluates:

- required view coverage;
- face detection;
- resolution and face-size ratio;
- blur;
- occlusion;
- exposure;
- cross-file evidence correspondence.

The gate must return one of:

- `PREFERRED_MULTIVIEW`;
- `PARTIAL_MULTIVIEW`;
- `SINGLE_VIEW_FALLBACK`;
- `RECAPTURE_REQUIRED`;
- `REJECTED_INPUT`.

Missing rear, profile, hair, clothing or body evidence must be declared. ATLAS
must not silently invent missing observations as source truth.

## 3. Customer declaration and authorization

Before external processing, the customer must actively confirm that:

1. the photographs were provided lawfully;
2. the customer is the depicted person or has authority/permission from every
   depicted person;
3. the photographs may be processed to design, preview, manufacture and deliver
   the personalized figurine;
4. the photographs and derived working assets may be transferred to the named
   approved external 3D provider for this purpose;
5. ATLAS may create and edit derived 2D/3D working files;
6. the approved physical figurine may be manufactured;
7. the customer understands that AI/artist interpretation may require review
   and revision;
8. the final production-intent preview requires explicit approval.

No pre-ticked box is permitted.

The consent record must preserve:

- order ID;
- subject ID(s);
- customer ID;
- exact consent-text version;
- timestamp;
- affirmative action;
- provider named at the time of consent;
- withdrawal/request state;
- evidence that additional depicted-person authority was asserted.

Children/minors require a separately reviewed guardian/parent authorization
route before processing.

This is an operational contract, not final legal advice. German/EU consumer,
privacy and data-protection text requires professional legal review before
commercial launch.

## 4. Provider transfer gate

External upload is allowed only if all are true:

- customer authorization is recorded;
- provider is on the approved-provider register;
- commercial output rights are documented;
- input/output training policy is documented;
- privacy and subprocessors are documented;
- retention and deletion conditions are documented;
- transfer region and applicable safeguards are documented;
- requested asset privacy mode is enabled;
- vendor job ID is captured;
- deletion request/receipt can be recorded.

Possible states:

- `BLOCKED_NO_CUSTOMER_AUTHORIZATION`;
- `BLOCKED_PROVIDER_NOT_APPROVED`;
- `BLOCKED_MINOR_ROUTE`;
- `APPROVED_PRIVATE_EXTERNAL_PROCESSING`;
- `LOCAL_PRIVATE_PROCESSING`;
- `DELETION_PENDING`;
- `DELETION_CONFIRMED`.

Current state remains:

`REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_APPROVED_VENDOR_ROUTE`

Authorized synthetic and explicitly approved pilot evidence may be used for
technical benchmarking and must be labelled accordingly.

## 5. PERSONAL_IDENTITY_PACKAGE

One package is created per approved subject.

### Package identity

- package ID and version;
- subject ID;
- order/customer linkage with access control;
- creation/update timestamps;
- package status;
- provenance manifest.

### Source evidence

- hashed source photographs;
- view type and capture metadata;
- quality observations;
- coverage classification;
- rights/consent record reference;
- missing or rejected evidence;
- color-reference reliability.

### Approved personal identity

- approved facial/head geometry reference;
- approved neutral front, left/right three-quarter and profile renders;
- skull/head silhouette character;
- forehead, cheek, jaw and chin character;
- eye, nose and mouth anchors;
- approved age-related character;
- approved asymmetry;
- approved hair/hairline;
- ears;
- facial hair;
- glasses and characteristic marks;
- color references.

### Product integration

- safe lower-head attachment region when known;
- neck/interface confidence;
- permitted identity-safe transformations;
- prohibited identity-changing transformations;
- known fragile features;
- compatible product families;
- family-specific derived versions;
- approved production scale evidence when available.

### Uncertainty and history

- observed versus inferred fields;
- unresolved fields;
- external provider and generation job;
- human corrections;
- customer revisions;
- approval version/timestamp;
- superseded versions;
- physical evidence references;
- known failures.

## 6. Package lifecycle

States:

1. `CAPTURE_PENDING`
2. `INPUT_QUALITY_REVIEW`
3. `RECAPTURE_REQUIRED`
4. `GENERATION_AUTHORIZED`
5. `IDENTITY_CANDIDATE`
6. `HUMAN_REVIEW`
7. `CUSTOMER_REVISION`
8. `IDENTITY_APPROVED`
9. `PRODUCT_DERIVATIVE_ACTIVE`
10. `WITHDRAWAL_OR_DELETION_REQUESTED`
11. `RESTRICTED_ARCHIVE`
12. `DELETED`

An identity candidate cannot become `IDENTITY_APPROVED` without explicit human
judgment and a versioned customer approval.

## 7. Reuse boundary

An approved identity package may be reused for PF-1 through PF-5 only:

- for the same approved subject;
- within the recorded consent/use scope;
- without replacing approved identity geometry silently;
- with a new product-specific preview and approval;
- while preserving provenance and version history.

`IDENTITY_PACKAGE_REUSE` does not mean that one final mesh is blindly reused.
It means one controlled identity authority can produce family-specific derived
geometry.

## 8. Retention and deletion baseline requiring legal review

Proposed operational baseline:

- rejected/unusable uploads: delete within 30 days;
- raw customer photographs after identity approval/order completion: 90 days;
- approved identity package and derived production files: retain only under the
  agreed reuse/order-support scope;
- external-provider assets: request deletion after accepted transfer/output,
  subject to provider capability and documented terms;
- customer withdrawal or deletion request: restrict further use immediately,
  then execute applicable deletion workflow unless a legal retention duty
  overrides it;
- retain minimal transaction/accounting records separately where legally
  required, without treating them as permission to retain source photographs.

No commercial retention period is final until German/EU legal review.

## 9. P-2 acceptance conditions

GATE-P2 may pass when:

- required/preferred capture sets are locked;
- quality-gate mapping is locked;
- customer authorization fields are locked;
- provider transfer states are locked;
- identity package fields and lifecycle are locked;
- uncertainty is explicit;
- reuse does not bypass product-specific customer approval;
- legal-review boundaries remain explicit;
- no unsupported production or privacy claim is introduced.

## 10. Approved P-2 decisions

**Decision date:** `2026-09-06`

**User decision:** `APPROVED`

1. `PREFERRED_CAPTURE = FRONT + LEFT_THREE_QUARTER + RIGHT_THREE_QUARTER + FULL_BODY_OR_POSE + CLOTHING_REFERENCE`

2. `SINGLE_PHOTO_FALLBACK = ALLOWED_WITH_HIGHER_UNCERTAINTY_AND_PRODUCT_LIMITS`
   PF-1 may require recapture or additional views.

3. `PF-3_IDENTITY_PACKAGE = ONE_SEPARATE_PACKAGE_PER_PERSON`

4. `PROVISIONAL_RETENTION_BASELINE = UNUSABLE_UPLOAD_30_DAYS / POST_ORDER_RAW_PHOTO_90_DAYS`
   These periods require German/EU professional legal review before commercial launch.

5. `IDENTITY_PACKAGE_REUSE = CONSENT_SCOPE_PLUS_NEW_PRODUCT_PREVIEW_AND_APPROVAL`

6. `REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_APPROVED_VENDOR_ROUTE`

## 11. GATE-P2 final decision

`GATE_P2 = PASS / REUSABLE_IDENTITY_PACKAGE_CONTRACT_LOCKED`

`CUSTOMER_CAPTURE_CONTRACT = USER_APPROVED`

`PERSONAL_IDENTITY_PACKAGE_CONTRACT = USER_APPROVED`

`PRODUCT_LAUNCH_AUTHORIZATION = NO`

`PRODUCTION_GEOMETRY_AUTHORIZATION = NO`

`CURRENT_WORK_PROGRAM = P-3`

`CURRENT_GATE = GATE-P3`

`EXACT_NEXT = BENCHMARK_COMMERCIALLY_ADMISSIBLE_GENERATION_ROUTES`

P-3 shall compare external generation routes using authorized pilot evidence and shall select a primary and fallback route from identity, geometry, cost, latency, privacy and revision evidence.
