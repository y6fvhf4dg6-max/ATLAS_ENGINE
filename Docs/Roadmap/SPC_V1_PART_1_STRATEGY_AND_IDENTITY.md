# ATLAS — Stylized Personalized Collectible Program V1
## PART 1 — Strategy, Identity and 2D Foundation

**Status:** `PIVOT_VALIDATION_ACTIVE`

**Program code:** `SPC_V1`

**Commercial product development order:**

1. Chibi / Cute Personalized Figurine
2. Stylized Bust / Mini Sculpture
3. Bobblehead / Character Figurine

This corresponds to the user-selected priority:

`1 -> 3 -> 2`

---

# 0. STRATEGIC BOUNDARY

## 0.1 New commercial objective

ATLAS shall validate a new commercial direction:

> Create recognizable, stylized, aesthetically coherent and physically manufacturable personalized 3D collectible products from customer photographs.

The commercial MVP shall NOT require:

- biometric identity reconstruction;
- photorealistic one-to-one facial reconstruction;
- metrically exact recovery of the person's real head;
- exact physical reproduction of unseen anatomy.

The commercial target function becomes:

`RECOGNIZABILITY`
+
`STYLE QUALITY`
+
`EMOTIONAL APPEAL`
+
`PRODUCT QUALITY`
+
`PRINTABILITY`
+
`REPEATABILITY`
+
`ACCEPTABLE UNIT ECONOMICS`

---

# 0.2 Existing ATLAS roadmap continuity

The existing 15-item ATLAS roadmap shall NOT be:

- deleted;
- rewritten;
- historically reinterpreted;
- silently replaced.

Current treatment:

## Items 1–10

Preserve their verified technical and historical status.

## Item 11

Preserve all implementation, evidence and decisions.

The exact-likeness branch reached under:

`Item 11 -> 11.15 -> R7.8-D3 -> Layer A`

shall be classified:

- `RESEARCH_PARKED`
- `NON_MVP_BLOCKING`

Its failure evidence remains valid and preserved.

The conclusion shall not be rewritten as success.

## Items 12–15

Status:

- `NOT_CANCELLED`
- `HOLD_PENDING_SPC_VALIDATION`

Their future relationship to SPC shall be evaluated individually as evidence accumulates.

## Phase 9

Remains:

- `NOT_AUTHORIZED`
- `NOT_STARTED`

SPC does not silently authorize Phase 9.

---

# 0.3 Pivot-lock rule

SPC is currently:

`PIVOT_VALIDATION_ACTIVE`

SPC shall become:

`PRIMARY_COMMERCIAL_TRACK`

only after BOTH:

1. technical feasibility;
2. commercial feasibility

are demonstrated.

Until then:

Exact Identity Track:

`RESEARCH_PARKED / NON_MVP_BLOCKING`

SPC V1:

`PIVOT_VALIDATION_ACTIVE`

---

# 0.4 Development sequence

Product implementation order is locked:

## Product 1

`CHIBI`

This is the only product authorized for initial end-to-end feasibility.

## Product 3

`STYLIZED_BUST`

Implementation begins only after the Chibi path establishes sufficient reusable evidence.

## Product 2

`BOBBLEHEAD`

Implementation follows Bust.

Initial Bobblehead shall use:

`FIXED_HEAD`

Spring/bobble mechanics are a later option.

They shall not complicate the first product validation.

---

# 1. CORE OPERATING MODEL — AI + ATLAS + HUMAN

The new system shall not assume that one algorithm must solve the entire personalization problem.

Authority is divided by role.

---

# 1.1 AI AUTHORITY — GENERATE

AI / learned-prior systems may:

- analyze source photographs;
- extract identity-related attributes;
- produce stylized 2D identity proposals;
- generate bounded style variations;
- infer plausible unseen appearance;
- generate identity-consistent multi-view references;
- propose initial 3D geometry;
- generate hair concepts;
- generate clothing concepts;
- generate accessories;
- assist semantic analysis;
- assist character-style conversion.

AI does NOT have final authority over:

- customer likeness acceptance;
- printability;
- metric scale;
- minimum thickness;
- manifold validity;
- self-intersections;
- fragile geometry;
- final product dimensions;
- production safety;
- final STL approval.

Summary:

> **AI = GENERATE**

---

# 1.2 ATLAS AUTHORITY — CONTROL

ATLAS progressively owns deterministic control.

## Geometry authority

ATLAS controls:

- orientation;
- scale;
- topology validation;
- component analysis;
- disconnected geometry;
- hole detection;
- hole repair where safe;
- normal consistency;
- self-intersection detection;
- remeshing;
- simplification;
- mesh density;
- minimum physical feature sizes;
- fragile-feature rules;
- head/body connection;
- neck interface;
- base attachment;
- production-safe geometry.

## Identity authority

ATLAS monitors salient identity cues rather than requiring exact biometric geometry.

Examples:

- head silhouette;
- face width/height character;
- forehead;
- jaw;
- chin;
- nose;
- ear openness;
- eye spacing;
- hairline;
- hairstyle;
- hair volume;
- beard;
- moustache;
- glasses;
- age/life-line cues;
- distinctive visual characteristics.

## Product authority

ATLAS controls:

- target product dimensions;
- head/body ratio;
- body class;
- pose contract;
- base;
- stand;
- label;
- date/name/location personalization;
- color rules;
- packaging interface;
- production preset.

## Evidence authority

ATLAS records:

- source evidence;
- input quality;
- 2D candidates;
- 2D approval;
- multi-view consistency;
- 3D generation;
- corrections;
- human intervention;
- physical validation;
- production QA.

Summary:

> **ATLAS = CONTROL**

---

# 1.3 HUMAN AUTHORITY — JUDGE / CORRECT EXCEPTIONS

Human participation is explicitly allowed.

It is not treated as system failure.

Three human roles exist.

## H1 — Customer / identity judge

Primary question:

> “Is this recognizably me / the intended person?”

Human visual judgment is authoritative for perceived likeness.

## H2 — Internal operator

Used for:

- QA;
- bounded corrections;
- edge cases;
- review of automated output.

All interventions must be classified and timed.

## H3 — Specialist artist

Reserved for:

- difficult edge cases;
- premium products;
- style development;
- reference asset creation;
- training/reference data generation.

A specialist artist is NOT intended to manually sculpt every standard order.

Summary:

> **HUMAN = JUDGE / CORRECT EXCEPTIONS**

---

# 1.4 Production authority

Final physical production remains a distinct responsibility.

> **PRODUCTION = MANUFACTURE**

The full authority model is therefore:

`GENERATE -> CONTROL -> JUDGE -> MANUFACTURE`

---

# 2. PRIMARY ARCHITECTURAL HYPOTHESIS

The preferred architecture is:

CUSTOMER PHOTOS
        |
        v
INPUT QUALITY GATE
        |
        v
IDENTITY ANCHOR EXTRACTION
        |
        v
MASTER STYLIZED 2D IDENTITY
        |
        v
HUMAN / CUSTOMER 2D APPROVAL
        |
        v
IDENTITY-LOCKED MULTI-VIEW 2D TURNAROUND
        |
        v
MULTI-VIEW CONSISTENCY GATE
        |
        v
AI 3D GENERATION
        |
        v
ATLAS NORMALIZATION / CONTROL
        |
        v
IDENTITY + STYLE PRESERVATION
        |
        v
PRODUCTIZATION
        |
        v
PRINTABILITY
        |
        v
3D PRODUCT APPROVAL
        |
        v
PHYSICAL PRODUCTION
        |
        v
PHYSICAL QA
        |
        v
PACKAGING / SHIPPING
        |
        v
FEEDBACK LOOP

The preferred production principle is:

> `Photos -> approved stylized identity -> consistent multi-view -> AI 3D -> ATLAS control -> physical product`

A single frontal stylized image directly converted to 3D may be benchmarked.

It is NOT initially designated as the preferred production architecture.

---

# 3. RESEARCH FOUNDATION

The architectural direction is supported by multiple evidence classes.

---

# 3.1 AgileAvatar principle

Relevant conceptual sequence:

`REAL PHOTO`
->
`STYLIZED 2D IDENTITY`
->
`CONTROLLED / PARAMETERIZED 3D`

Key transferable principle:

Do not force a direct jump from unrestricted real photography to the final stylized 3D representation if an intermediate stylized identity representation reduces the domain gap.

For ATLAS this supports the 2D approval stage.

---

# 3.2 3DCaricShop principle

Relevant sequence:

`GENERATED STYLIZED 3D`
->
`TEMPLATE / PRIOR CONSTRAINT`
->
`CONTROLLED TOPOLOGY`

Key transferable principle:

Generated geometry does not automatically become final production geometry.

ATLAS may occupy the deterministic control layer after generative 3D creation.

---

# 3.3 3D-CariGAN principle

Relevant evidence:

Normal face photographs can be transformed into stylized 3D caricature representations using learned shape priors and controlled post-processing.

Key transferable principle:

Neural generation and deterministic completion/control can coexist.

---

# 3.4 Contemporary implementation evidence

Modern practical systems demonstrate that:

- photo -> stylized 2D -> 3D is feasible;
- general image-to-3D remains imperfect for human identity;
- unseen geometry is inferred;
- multi-view guidance can improve geometric consistency;
- AI meshes commonly require cleanup;
- visually attractive geometry is not necessarily printable geometry.

---

# 3.5 ATLAS interpretation

ATLAS shall not treat generative inference as metric reconstruction.

Instead:

> AI supplies plausible stylized identity proposals.

> ATLAS supplies geometric and product authority.

> Human perception supplies identity judgment.

This is the fundamental SPC division of responsibility.

---

# 4. PROGRAM 1 — COMMERCIAL AND LEGAL ELIGIBILITY

This begins BEFORE sending real customer photographs to external services.

---

# 4.1 Competitive benchmark

Primary geographic scope:

- European Union;
- relevant wider European markets;
- Turkey.

Record:

- company;
- country;
- product;
- style;
- price;
- customization;
- photo requirements;
- preview process;
- revisions;
- production technique;
- delivery;
- positioning;
- apparent physical quality.

---

# 4.2 Initial willingness-to-pay hypotheses

Establish preliminary price hypotheses for:

- Chibi;
- Stylized Bust;
- Bobblehead.

Competitor prices are inputs.

They are NOT proof of viable ATLAS economics.

---

# 4.3 AI commercial eligibility audit

Before serious vendor selection verify, where relevant:

- commercial-use permission;
- output ownership;
- API/model terms;
- image retention;
- deletion;
- training on uploaded images;
- GDPR/DPA position;
- processing geography;
- subcontractors;
- minors policy;
- customer-data restrictions;
- model license;
- output-license restrictions.

A technically excellent service can still be rejected for commercial/legal reasons.

---

# 4.4 Initial cost envelope

Track from the beginning:

- AI API cost;
- local compute;
- regeneration cost;
- human time;
- image processing;
- 3D generation;
- preliminary printing assumptions.

---

# GATE SPC-C0 — COMMERCIAL/LEGAL ELIGIBILITY

Question:

> Is there at least one legally and commercially plausible technology path worth benchmarking?

PASS:
continue.

FAIL:
revise technology/vendor/data architecture before deeper implementation.

---

# 5. PROGRAM 2 — CHIBI PRODUCT DEFINITION

Only Product 1 enters full feasibility.

---

# 5.1 Chibi Style Bible V0

Define:

- head/body ratio;
- exaggeration range;
- realism/stylization range;
- eye style;
- nose treatment;
- ear treatment;
- jaw/chin treatment;
- age treatment;
- wrinkle treatment;
- hair mass;
- hair silhouette;
- beard/moustache;
- glasses;
- hands;
- feet;
- clothing detail;
- surface language;
- color language;
- expression range.

The objective:

> a recognizable ATLAS product language.

Not:

> random AI aesthetics.

---

# 5.2 Identity Anchor Contract

## Geometric anchors

- cranial silhouette;
- head width/height character;
- face width/height;
- forehead;
- jaw;
- chin;
- nose character;
- nose profile;
- ear openness;
- eye spacing.

## Semantic anchors

- hairline;
- hairstyle;
- hair mass;
- beard;
- moustache;
- glasses;
- age;
- characteristic wrinkles;
- distinctive marks where appropriate.

## Character anchors

- characteristic expression;
- hairstyle personality;
- clothing cues;
- occupation cues;
- hobby cues.

The contract does NOT demand exact geometry.

It demands preservation of recognizable identity information.

---

# 5.3 Initial physical Chibi contract

Define preliminary:

- product heights;
- head/body ratio;
- body abstraction;
- pose family;
- base;
- center-of-gravity assumptions;
- fragile-feature policy;
- color strategy;
- packaging assumptions.

---

# GATE SPC-C1 — PRODUCT DEFINITION

Question:

> Is Chibi defined precisely enough that different AI systems can be compared against the same ATLAS product target?

PASS:
continue.

FAIL:
do not benchmark uncontrolled styles.

---

# 6. PROGRAM 3 — CUSTOMER CAPTURE CONTRACT

---

# 6.1 Minimum input

Initial preferred minimum:

- front;
- left 3/4;
- right 3/4.

---

# 6.2 Supplemental evidence

Preferred where useful:

- left profile;
- right profile;
- rear hair view;
- full-body/outfit image;
- glasses reference;
- accessories;
- clothing reference.

These are identity-conditioning inputs.

They are NOT a promise of metric reconstruction.

---

# 6.3 Input quality checks

Progressively automate:

- resolution;
- blur;
- focus;
- overexposure;
- underexposure;
- lighting;
- crop;
- occlusion;
- face visibility;
- pose suitability;
- hair visibility;
- conflicting source appearance;
- accessories obscuring identity.

Bad input should fail early.

The customer should be asked to recapture rather than allowing weak source data to propagate downstream.

---

# 7. PROGRAM 4 — 2D STYLIZED IDENTITY FEASIBILITY

This is the first major technical kill gate.

---

# 7.1 Candidate systems

Benchmark multiple commercially eligible:

- commercial APIs;
- commercial applications;
- open-source systems;
- locally hosted systems where practical.

Do not select technology based only on vendor showcase images.

---

# 7.2 Initial benchmark subjects

Use a bounded but deliberately varied set.

Include differences in:

- age;
- sex;
- face morphology;
- hairstyle;
- hair volume;
- facial hair;
- glasses;
- distinctive facial characteristics.

---

# 7.3 Candidate generation

Use a bounded protocol.

Example:

- limited number of styles;
- limited number of regenerations;
- same source evidence;
- comparable instructions.

Do NOT permit infinite prompting until a good result appears.

That would destroy benchmark validity and hide actual operating cost.

---

# 7.4 Evaluation

## Identity

Assess:

- recognizable person;
- head character;
- jaw/chin;
- nose;
- ears;
- hair;
- age;
- glasses;
- beard;
- distinctive cues.

## Style

Assess:

- deliberate stylization;
- internal coherence;
- consistency with Style Bible;
- avoidance of malformed semi-realistic output.

## Commercial

Assess:

- emotional appeal;
- giftability;
- desirability;
- apparent value.

---

# GATE SPC-G1 — 2D IDENTITY

Initial benchmark proposal:

> At least 8 of 10 subjects shall obtain at least one acceptable stylized identity under the bounded protocol.

If FAIL:

Do not proceed into full 3D product development.

First solve:

- identity conditioning;
- style definition;
- model/vendor;
- capture quality;
- candidate-selection process.

---

# 8. PROGRAM 5 — IDENTITY-LOCKED 2D MULTI-VIEW

This is a critical stage.

The approved 2D master identity becomes the visual authority.

---

# 8.1 Target turnaround

Generate as appropriate:

- front;
- left 3/4;
- right 3/4;
- left profile;
- right profile;
- rear/hair guidance where useful.

---

# 8.2 Multi-view identity requirements

Across views preserve:

- same character;
- head proportions;
- face width;
- nose;
- jaw/chin;
- ears;
- hairline;
- hairstyle;
- age;
- beard;
- glasses;
- style intensity.

---

# GATE SPC-G2 — MULTI-VIEW CONSISTENCY

Question:

> Do all required views represent the same approved stylized identity?

PASS:
3D benchmark authorized.

FAIL:
do not trust the views for production 3D.

Resolve identity drift first.

---

# END OF PART 1

Next authority document:

`SPC_V1_PART_2_3D_ATLAS_AND_PRODUCT.md`

---

<!-- SPC_C0_COMMERCIAL_LEGAL_ELIGIBILITY_PASS_2026_09_04 -->

# SPC-C0 — Commercial / Legal Eligibility Closure

**Decision date:** `2026-09-04`

**Gate:** `SPC-C0 — Commercial / Legal Eligibility`

**Result:** `PASS`

## Decision

SPC-C0 is closed as PASS because at least one commercially and technically plausible architecture exists for continuing SPC validation.

The preferred initial architecture class is:

`REAL CUSTOMER PHOTO(S)`
->
`LOCAL / PRIVATE 2D IDENTITY PROCESSING`
->
`APPROVED STYLIZED MASTER 2D`
->
`IDENTITY-CONSISTENT MULTI-VIEW`
->
`APPROVED EXTERNAL OR LOCAL 3D GENERATION`
->
`ATLAS CONTROL`

## 2D direction

The preferred first-line 2D strategy is:

`LOCAL / SELF-HOSTED WHERE PRACTICAL`

Rationale:

- reduce unnecessary external transfer of raw customer photographs;
- improve privacy-by-design;
- reduce vendor dependence;
- reduce per-order API cost where technically feasible;
- allow ATLAS-controlled identity and style experiments.

A Qwen-class self-hosted image-editing / identity-consistency system is currently a strong initial benchmark candidate.

This is a benchmark preference, not a permanent vendor lock.

Alternative local or commercially eligible systems may be evaluated.

## 3D direction

Initial 3D benchmark candidates include commercially available multi-image / image-to-3D systems such as:

- Rodin-class systems;
- Tripo-class systems.

These are benchmark candidates only.

Selection must consider:

- identity retention;
- multi-view handling;
- geometry quality;
- output topology;
- automation suitability;
- latency;
- real cost per successful order;
- commercial license;
- data processing terms;
- customer-data handling.

## Customer data restriction

The following rule is active:

`REAL_CUSTOMER_EXTERNAL_UPLOAD = BLOCKED_PENDING_VENDOR_DPA_OR_WRITTEN_CONFIRMATION`

This means:

- SPC-C0 PASS does NOT authorize unrestricted upload of real customer face photographs to external AI vendors;
- real customer raw face images shall not be sent to an external 3D service merely because that service passed a technical benchmark;
- vendor-specific DPA, SCC, contractual language, written confirmation, or equivalent sufficient legal/privacy basis must be verified before such use;
- synthetic, stylized, consented benchmark data may be used according to the applicable test protocol and legal basis;
- local/private processing remains preferred for raw identity evidence where practical.

## Important interpretation

`SPC-C0 = PASS`

means:

> A commercially plausible technology and legal architecture exists and the SPC program may proceed to product-definition validation.

It does NOT mean:

> Every identified vendor is approved for production use with real customer photographs.

Vendor approval remains service-specific.

## Current candidate cost interpretation

Initial evidence indicates that external AI generation cost is not currently expected to be the dominant SPC unit-economics risk.

The primary economic risks to measure later are:

- human correction time;
- regeneration burden;
- print time;
- material use;
- multicolor purge/waste;
- failed prints;
- finishing;
- packaging;
- customer revisions.

No final unit-cost assumption is locked at SPC-C0.

## Gate transition

`SPC-C0 = PASS`

Next unresolved gate:

`SPC-C1 — Chibi Product Definition`

Immediate next work:

1. Chibi Style Bible V0.
2. Identity Anchor Contract.
3. Initial Physical Chibi Contract.

No 3D production implementation shall bypass SPC-C1.

---

<!-- SPC_C1_CHIBI_PRODUCT_DEFINITION_BASELINE_2026_09_04 -->

# SPC-C1 — Chibi Product Definition Baseline

**Decision date:** `2026-09-04`

**Gate:** `SPC-C1 — Chibi Product Definition`

**Status:** `ACTIVE / BASELINE_DEFINED`

This section defines the initial V0 benchmark product contract for the first SPC Chibi feasibility path.

`SPC-C1` is NOT closed by this update.

The purpose is to establish a controlled physical and visual baseline before 2D stylized identity benchmarking begins.

## Product positioning

`STYLE = PREMIUM_STYLIZED_PERSONAL_SCULPTURE`

The intended product character is:

- premium desktop collectible / mini sculpture;
- personalized;
- recognizable as the real subject;
- clearly stylized;
- not photo-real;
- not strongly toy-like;
- not anime / super-deformed by default.

The dominant design rule is:

`IDENTITY_BEFORE_STYLE`

A visually attractive stylization that destroys recognizability is a FAIL.

## V0 physical benchmark dimensions

Initial benchmark target:

`CHIBI_V0_TOTAL_HEIGHT_MM = 150`

Initial head-to-total-height band:

`HEAD_TO_TOTAL_HEIGHT_RATIO = 0.35–0.40`

Nominal starting point:

`HEAD_TO_TOTAL_HEIGHT_RATIO_NOMINAL = ~0.38`

Initial integrated base target:

`BASE_DIAMETER_MM = 70–75`

`BASE_HEIGHT_MM = 7–8`

These are V0 benchmark parameters, not immutable production constants.

They may be revised after physical evidence for:

- stability;
- visual balance;
- print time;
- material use;
- detail readability;
- packaging;
- customer preference.

## Pose contract

`POSE_CLASS = COMPACT_NATURAL_STANDING`

Initial V0 pose rules:

- both feet attached to the base;
- center of mass kept near the base center;
- mild natural shoulder / hip asymmetry allowed;
- arms may separate from the torso but shall remain compact;
- extreme arm extension is not part of the initial benchmark;
- running, jumping, single-leg and highly dynamic poses are excluded from V0;
- long fragile accessories are excluded from the initial benchmark;
- head rotation should remain mild for the initial benchmark;
- the overall silhouette should read as a small sculpture rather than an action toy.

## Facial stylization contract

`FACIAL_STYLIZATION = LOW_TO_MODERATE`

The style may simplify or gently exaggerate selected forms, but identity-carrying proportions shall remain dominant.

Design intent:

- stylization should remain visibly present;
- facial geometry should not collapse to a generic character template;
- age and character should not be erased merely to increase cuteness;
- subject-specific asymmetry may be preserved where it contributes to identity.

The approximate design direction is:

- identity retention visually dominant;
- stylization secondary;
- no numeric recognition score is implied by this wording.

## Identity Anchor Contract

Identity anchors are grouped by preservation priority.

### CRITICAL

The following identity anchors shall receive the highest preservation priority:

- overall head / skull silhouette;
- forehead width and cranial character;
- temporal width;
- cheekbone width;
- jaw width;
- chin shape;
- head length-to-width character;
- eye spacing;
- eye inclination / orientation;
- nose character;
- mouth width and mouth form;
- jaw / chin relationship;
- hairline.

### HIGH

The following anchors are high-priority:

- eye opening character;
- eyebrow shape;
- eyebrow-to-eye spacing;
- nose length;
- bridge character;
- nose tip character;
- nostril width;
- nose-to-mouth spacing;
- lip form;
- philtrum character;
- chin projection;
- ear openness;
- ear height;
- ear silhouette;
- facial fullness;
- age-related facial character;
- nasolabial character;
- periocular character;
- recognizable facial asymmetry;
- hair volume;
- hair parting direction;
- characteristic curl / wave / mass.

### CONTEXTUAL

The following anchors shall be preserved when identity-relevant for the subject:

- beard;
- moustache;
- glasses;
- moles;
- scars;
- distinctive marks;
- characteristic accessories;
- other subject-specific signature features.

## Identity acceptance principle

If the stylized result is aesthetically successful but the combined anchor pattern no longer clearly carries the subject's identity:

`RESULT = FAIL`

Style quality cannot override identity failure.

## Initial Physical Chibi Contract

Primary physical output:

`FINAL_PRODUCTION_GEOMETRY = STL`

Accepted intermediate/source formats may include:

- `GLB`
- `OBJ`

ATLAS shall not constrain upstream AI generation to STL if a richer intermediate format provides better geometry or material handling.

For multicolor production, ATLAS may output separate print components such as:

- skin;
- hair;
- clothing;
- accessories;
- base;
- other color-separated geometry.

Therefore:

`MULTICOLOR_OUTPUT = PART_BASED_STL_ALLOWED`

## Physical safety and printability rules

The V0 benchmark shall prefer:

- two-foot base attachment;
- integrated base;
- flat base underside;
- compact pose;
- reduced thin-ankle risk;
- reduced thin-wrist risk;
- reduced unsupported long appendages;
- reduced fragile accessory risk;
- manifold geometry;
- slicer-safe geometry;
- controlled support requirement;
- readable facial and hair detail at approximately 150 mm total height.

The design shall prioritize physical reliability without destroying visual quality.

## Stability requirement

The first V0 product shall not be accepted if it is prone to ordinary tabletop tipping.

The current base band is intentionally conservative:

`BASE_DIAMETER_MM = 70–75`

This band may be adjusted after physical stability testing.

Possible future variants may include smaller or larger bases if evidence supports them.

## Initial physical acceptance criteria

A first physical Chibi candidate may proceed only if all of the following are sufficiently satisfied:

1. the person is recognizable;
2. the object reads as a premium stylized personal sculpture;
3. the result does not read as an overly toy-like generic character;
4. the figure is stable on a tabletop;
5. facial and hair detail remain readable;
6. the mesh is manifold / slicer-safe;
7. support and cleanup burden remain operationally reasonable;
8. fragile regions remain acceptable for handling and packaging;
9. multicolor separation is feasible where the product requires it;
10. the result remains compatible with ATLAS-controlled production.

## Parameter-change policy

The following are explicitly treated as tunable product parameters:

- total height;
- head ratio;
- base diameter;
- base height;
- base shape;
- pose;
- accessory dimensions;
- color-part segmentation.

These may be changed after physical evidence without redefining the entire SPC architecture.

The following are more fundamental and require stronger justification before changing:

- premium stylized sculpture positioning;
- identity-before-style principle;
- identity anchor preservation logic;
- facial stylization philosophy;
- customer identity acceptance logic.

## Current SPC-C1 state

`SPC-C1 = ACTIVE`

Current baseline components defined:

1. `CHIBI STYLE BIBLE V0`
2. `IDENTITY ANCHOR CONTRACT`
3. `INITIAL PHYSICAL CHIBI CONTRACT`

This update does NOT declare:

`SPC-C1 = PASS`

SPC-C1 closure requires a dedicated closure check / decision after the baseline definition is reviewed for completeness and internal consistency.

---

<!-- SPC_C1_CHIBI_PRODUCT_DEFINITION_PASS_2026_09_04 -->

# SPC-C1 — Chibi Product Definition Closure

**Decision date:** `2026-09-04`

**Gate:** `SPC-C1 — Chibi Product Definition`

**Result:** `PASS`

SPC-C1 is closed because the initial Chibi V0 product definition is sufficiently complete and internally consistent to support the next feasibility gate.

## Closure basis

The following baseline components are defined:

1. `CHIBI STYLE BIBLE V0`
2. `IDENTITY ANCHOR CONTRACT`
3. `INITIAL PHYSICAL CHIBI CONTRACT`

The approved V0 direction includes:

- `STYLE = PREMIUM_STYLIZED_PERSONAL_SCULPTURE`
- `IDENTITY_BEFORE_STYLE`
- `CHIBI_V0_TOTAL_HEIGHT_MM = 150`
- `HEAD_TO_TOTAL_HEIGHT_RATIO = 0.35–0.40`
- nominal starting point approximately `0.38`
- `BASE_DIAMETER_MM = 70–75`
- `BASE_HEIGHT_MM = 7–8`
- `POSE_CLASS = COMPACT_NATURAL_STANDING`
- `FACIAL_STYLIZATION = LOW_TO_MODERATE`
- identity-anchor preservation priorities;
- integrated stable base;
- two-foot support;
- manifold / slicer-safe physical geometry;
- STL as final production geometry;
- GLB / OBJ allowed as richer intermediate formats;
- part-based STL allowed for multicolor production.

## V0 interpretation

The above dimensional values are benchmark standards, not immutable product constants.

The following may be revised after physical and commercial evidence:

- total height;
- head ratio;
- base diameter;
- base height;
- base shape;
- pose;
- accessory dimensions;
- color-part segmentation.

Such revisions do not by themselves reopen SPC-C1 if the underlying product identity remains intact.

## Protected product principles

The following are more fundamental and shall not be changed casually:

- premium stylized personal sculpture positioning;
- identity-before-style principle;
- recognizable subject identity;
- identity anchor preservation;
- low-to-moderate facial stylization direction;
- customer/human identity judgment as an acceptance authority;
- physical stability and production reliability.

## Closure Challenge

The dedicated SPC-C1 closure challenge passed on `2026-09-04`.

Therefore:

`SPC-C1 = PASS`

## Gate transition

Closed:

`SPC-C1 — CHIBI PRODUCT DEFINITION`

Next active gate:

`SPC-G1 — 2D STYLIZED IDENTITY`

The next work shall validate whether approved customer/source identity can be converted into a recognizable, premium stylized 2D master while preserving the defined identity anchors.

No downstream 3D production implementation shall bypass SPC-G1.

## Phase policy

`PHASE9 = NOT_AUTHORIZED / NOT_STARTED`

SPC progression does not authorize Phase 9.


<!-- SPC_CHIBI_MAINLINE_RECONFIRMED_2026_09_05 -->
### SPC_V1 — Chibi Mainline Reconfirmed (2026-09-05)

- The 150 mm Meshy V7 bust is retained only as an **intermediate identity + physical-production proof specimen**; it is not the final SPC product.
- The locked SPC-C1 product target remains unchanged: **150 mm stylized/chibi full-body figurine**, identity-first, compact body, integrated base.
- Meshy V7 is the currently selected successful 3D identity/head source for this pilot subject.
- SPC-G4 remains **ACTIVE**.
- **Exact next mainline task:** preserve the successful Meshy V7 identity/head while integrating it into the locked 150 mm chibi full-body product.
- After the chibi full-body milestone, continue with reusable/ready-made 3D asset integration, followed by the model/diorama base ("maket ayağı") product layer.
- SPC-G5, SPC-G6 and SPC-G7 retain their existing order; this checkpoint does not insert or reorder main gates.
<!-- /SPC_CHIBI_MAINLINE_RECONFIRMED_2026_09_05 -->
