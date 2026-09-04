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
