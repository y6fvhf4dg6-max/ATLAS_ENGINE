# ATLAS — Stylized Personalized Collectible Program V1
## PART 2 — 3D Generation, ATLAS Control and Physical Product

**Parent program:** `SPC_V1`

**Required predecessor:**

`SPC_V1_PART_1_STRATEGY_AND_IDENTITY.md`

---

# 9. PROGRAM 6 — 2D / MULTI-VIEW TO 3D BENCHMARK

3D generation begins only after an acceptable stylized identity and usable multi-view evidence exist.

---

# 9.1 Candidate 3D generators

Benchmark a bounded set of:

- commercial image-to-3D systems;
- multi-view-to-3D systems;
- locally runnable/open models where relevant;
- specialist character/head systems if commercially eligible.

Avoid vendor lock-in at architecture level.

ATLAS should eventually accept more than one upstream generator where practical.

---

# 9.2 Primary benchmark question

Do NOT ask only:

> Which system produces the prettiest render?

Ask:

> Which system produces the best input for an ATLAS-controlled physical product?

---

# 9.3 Appearance evaluation

Measure qualitatively and where possible systematically:

- likeness to approved 2D identity;
- style retention;
- head silhouette;
- face width;
- nose character;
- nose profile;
- jaw;
- chin;
- ears;
- hair;
- age;
- glasses;
- beard;
- expression.

---

# 9.4 Geometry evaluation

Inspect:

- head completeness;
- rear-head plausibility;
- hair completeness;
- ear geometry;
- eye geometry;
- mouth geometry;
- neck;
- disconnected components;
- holes;
- non-manifold geometry;
- self-intersections;
- mesh density;
- topology;
- texture availability;
- UV quality where relevant.

---

# 9.5 Operational evaluation

Measure:

- generation latency;
- API/compute cost;
- failure rate;
- regeneration rate;
- service reliability;
- output formats;
- automation suitability;
- commercial licensing;
- data-handling constraints.

---

# 9.6 Human correction measurement

From the FIRST candidate onward record:

- whether intervention was required;
- intervention category;
- minutes spent;
- whether identity improved;
- whether geometry improved;
- whether the candidate was eventually rejected.

---

# GATE SPC-G3 — 3D IDENTITY TRANSFER

Question:

> Does the approved stylized identity survive the transition into usable 3D geometry?

A beautiful generic character is a FAIL if it no longer represents the approved person.

A geometrically clean mesh is also a FAIL if identity is lost.

PASS requires sufficient:

`IDENTITY + STYLE + GEOMETRIC USABILITY`

---

# 10. PROGRAM 7 — ATLAS AI-MESH NORMALIZATION

This is a core ATLAS responsibility.

Goal:

> Convert heterogeneous generative meshes into an ATLAS-controlled intermediate representation.

---

# 10.1 Input provenance

Every imported mesh should record:

- generator;
- generator version;
- request/configuration identity;
- source 2D identity reference;
- source multi-view set;
- output format;
- generation timestamp;
- commercial/license status where relevant.

---

# 10.2 Orientation normalization

Determine and normalize:

- up axis;
- front direction;
- center;
- ground reference;
- coordinate convention.

---

# 10.3 Scale normalization

Generative output scale shall not be trusted.

ATLAS establishes:

- canonical processing scale;
- target product scale;
- head/body dimensions;
- downstream unit contract.

---

# 10.4 Component analysis

Detect:

- disconnected hair;
- floating eyes;
- floating accessories;
- duplicate shells;
- internal components;
- unintended geometry;
- isolated fragments.

Classify components before automatic removal.

---

# 10.5 Hole / manifold analysis

Detect:

- open boundaries;
- holes;
- non-manifold edges;
- non-manifold vertices;
- invalid topology.

Repair only where the repair preserves intended form.

---

# 10.6 Normal consistency

Detect and correct where safe:

- inverted normals;
- inconsistent winding;
- invalid normal fields.

---

# 10.7 Self-intersection

Detect:

- face-face intersections;
- intersecting hair/head shells;
- accessory penetration;
- internal collision.

Do not silently repair if identity or style may be materially changed.

---

# 10.8 Mesh-density control

Generated meshes may be:

- unnecessarily dense;
- locally under-resolved;
- irregular.

Benchmark:

- simplification;
- remeshing;
- adaptive preservation of identity-critical regions.

---

# 10.9 Fragile feature detection

Identify physical risks:

- thin ears;
- glasses temples;
- hair strands;
- fingers;
- thin accessories;
- narrow neck;
- unsupported protrusions.

ATLAS may thicken or redesign features according to product rules.

Such modifications must remain visibly acceptable.

---

# 10.10 Hair/head integration

Handle:

- disconnected hair;
- buried hair;
- weak hair roots;
- ultra-thin sheets;
- inaccessible cavities.

Hair is treated as an identity-bearing product feature, not merely decoration.

---

# 10.11 Neck and body interface

Define deterministic interfaces between:

- generated head;
- Chibi body;
- later Bust;
- later Bobblehead.

Avoid arbitrary per-order manual attachment.

---

# 10.12 Semantic mapping

Where feasible map regions such as:

- cranium;
- forehead;
- eyes;
- nose;
- cheeks;
- ears;
- mouth;
- jaw;
- chin;
- hair;
- neck;
- glasses/accessory.

This allows region-specific product and identity rules.

---

# 10.13 Identity anchor preservation during repair

Every normalization operation must be evaluated for damage to:

- silhouette;
- jaw/chin;
- nose;
- ears;
- hair;
- age cues;
- other salient identity anchors.

A technically cleaner mesh that loses identity may be rejected.

---

# GATE SPC-G4 — NORMALIZATION FEASIBILITY

On a bounded representative set record:

- issues detected;
- issues automatically fixed;
- issues unresolved;
- human correction minutes;
- identity damage;
- printability improvement.

Goal:

Not zero human intervention immediately.

Goal:

> Demonstrate that recurring AI-mesh problems can progressively become deterministic ATLAS rules.

---

# 11. PROGRAM 8 — HUMAN-IN-THE-LOOP LEARNING SYSTEM

Human work is explicitly measured.

---

# 11.1 Intervention levels

`H0`
- no human correction.

`H1`
- less than 5 minutes.

`H2`
- 5 to 15 minutes.

`H3`
- 15 to 30 minutes.

`H4`
- more than 30 minutes or candidate rejected.

---

# 11.2 Correction taxonomy

Initial categories:

- `HAIR_VOLUME`
- `HAIR_STYLE`
- `HAIRLINE`
- `EAR_OPENNESS`
- `JAW`
- `CHIN`
- `NOSE`
- `AGE`
- `WRINKLE_DETAIL`
- `GLASSES`
- `EYE`
- `MOUTH`
- `STYLE_DRIFT`
- `MULTIVIEW_DRIFT`
- `MESH_REPAIR`
- `HOLE_REPAIR`
- `SELF_INTERSECTION`
- `THIN_FEATURE`
- `PRODUCT_INTERFACE`
- `POSE`
- `BODY`
- `ACCESSORY`
- `OTHER_RECORDED`

---

# 11.3 Automation feedback loop

For every recurring human correction ask:

> Can this become an ATLAS rule?

Possible destinations:

- deterministic correction;
- candidate ranking;
- automatic rejection;
- better capture instruction;
- prompt/control adjustment;
- learned correction model;
- style-prior refinement.

---

# 11.4 Human labor target

Do NOT artificially impose 5-minute operation during initial feasibility.

Measure reality first.

Long-term objective:

Increase:

`H0 + H1`

share.

Reduce:

`H3 + H4`

share.

---

# 12. PROGRAM 9 — CHIBI PRODUCTIZATION

A successful 3D head is not yet a product.

---

# 12.1 Body system

Develop reusable Chibi body architecture.

Possible dimensions:

- generic neutral;
- male/female-neutral where desired;
- child/adult class if commercially justified;
- clothing-compatible body;
- pose-compatible skeleton/structure.

Avoid creating hundreds of body types before market evidence.

---

# 12.2 Pose system

Initial pose library should remain bounded.

Examples:

- neutral standing;
- hands at side;
- hands in front;
- simple celebratory pose;
- profession/hobby-specific poses later.

Every pose must satisfy:

- stability;
- printability;
- recognizability;
- product aesthetics.

---

# 12.3 Clothing

Options may include:

- source-photo-based clothing;
- standardized themes;
- profession;
- sport;
- wedding;
- graduation;
- casual;
- premium custom clothing.

Clothing detail must match physical scale.

---

# 12.4 Props

Potential later examples:

- football;
- guitar;
- briefcase;
- graduation cap;
- flowers;
- hobby objects.

All props require minimum-thickness and attachment rules.

---

# 12.5 Pet integration

Potential upsell.

Not required for initial physical feasibility.

---

# 12.6 Base system

Base shall be standardized where possible.

Consider:

- geometry;
- footprint;
- stability;
- name;
- date;
- location;
- short message;
- brand identity.

---

# 12.7 Personalization fields

Possible:

- name;
- date;
- location;
- profession;
- hobby;
- event;
- short text.

Do not overload the first MVP.

---

# 12.8 Color system

Determine:

- full multicolor vs limited palette;
- FDM practical limits;
- face/skin handling;
- hair;
- clothing;
- base.

Current Bambu P2S constraints must be measured physically rather than assumed.

---

# 12.9 Packaging interface

Product geometry should consider:

- gift box;
- protection;
- orientation;
- fragile projections;
- shipping.

Packaging must not be an afterthought.

---

# 13. PROGRAM 10 — PRINTABILITY AND PHYSICAL PROOF

No commercial launch before physical validation.

---

# 13.1 First physical proof set

Initial bounded validation:

**3 Chibi subjects**

Choose intentionally different identity/production risks.

Suggested diversity:

- different ages;
- different hair structures;
- different head/face morphology;
- glasses/beard where useful;
- different clothing.

---

# 13.2 Size benchmark

Potential initial physical sizes:

- approximately 50 mm;
- approximately 70 mm;
- approximately 100 mm.

Exact sizes are not locked until tested.

Determine where:

- face stops reading;
- hair becomes too crude;
- ears fail;
- accessories become fragile;
- print time becomes unattractive.

---

# 13.3 Face readability

Evaluate physically:

- silhouette;
- eyes;
- nose;
- mouth;
- jaw;
- ears;
- hair;
- age cues.

Digital render acceptance does not guarantee physical readability.

---

# 13.4 Fragility

Test:

- ears;
- hair projections;
- glasses;
- fingers;
- accessories;
- neck;
- body joints;
- base connection.

---

# 13.5 FDM benchmark

Current first-line machine:

`Bambu Lab P2S Combo`

Measure:

- layer height;
- nozzle options where relevant;
- print time;
- supports;
- support scars;
- filament;
- AMS changes;
- purge;
- failure;
- post-processing.

---

# 13.6 Resin/SLA comparison

At least one external high-detail resin/SLA comparison should be considered.

Purpose:

Not immediately to change production technology.

Purpose:

> Establish whether product quality is limited by geometry generation or by FDM physical resolution.

This prevents endless software tuning when the physical process is the ceiling.

---

# 13.7 Shipping durability

Physical proof must eventually include:

- packaging;
- handling;
- vibration;
- fragile features;
- arrival condition.

---

# GATE SPC-G5 — PHYSICAL PRODUCT

Primary question:

> Is this a physical object that a reasonable customer could want to buy?

Not:

> Did the slicer accept the STL?

Technical printability alone is insufficient.

---

# 14. IDENTITY / STYLE PRESERVATION GATE

Before commercial product approval compare:

SOURCE PERSON
        |
        v
APPROVED 2D CHARACTER
        |
        v
APPROVED 3D CHARACTER
        |
        v
PHYSICAL PRINT

At each transition ask:

- is identity preserved?
- is style preserved?
- is age preserved?
- is hair preserved?
- are defining features preserved?

This allows identification of where identity degradation occurs.

---

# 15. CUSTOMER APPROVAL MODEL

Recommended future commercial flow:

PHOTO UPLOAD
      |
      v
2D CANDIDATES
      |
      v
CUSTOMER SELECTS / REVISES
      |
      v
APPROVED MASTER 2D
      |
      v
3D GENERATION
      |
      v
ATLAS CONTROL
      |
      v
3D PRODUCT PREVIEW
      |
      v
FINAL APPROVAL
      |
      v
PRINT

---

# 15.1 Revision policy

Revision economics must be bounded.

Possible future policy:

- limited free 2D regeneration;
- limited 3D correction;
- additional complex customization charged separately.

No exact commercial revision count is locked yet.

Measure actual customer behavior first.

---

# 16. KILL / STOP RULES — TECHNICAL

## KILL-1

If bounded 2D generation cannot preserve recognizable identity:

STOP before full 3D product development.

---

## KILL-2

If approved 2D identity repeatedly collapses in 3D:

Do not compensate with endless cleanup.

Change:

- 3D model;
- input architecture;
- multi-view process;
- generator/vendor.

---

## KILL-3

If average required human cleanup remains above approximately 30 minutes/order:

Treat the production architecture as commercially suspect unless premium pricing demonstrably supports it.

---

## KILL-4

If FDM is the limiting factor:

Do not endlessly tune upstream geometry.

Benchmark:

- different physical design;
- larger size;
- resin/SLA;
- outsourced production.

---

## KILL-5

If normalization repeatedly destroys identity:

ATLAS repair policy must be redesigned.

Do not prioritize watertightness over recognizability blindly.

---

# 17. PART 2 SUCCESS CONDITION

PART 2 succeeds when Chibi has demonstrated:

- acceptable approved stylized identity;
- coherent multi-view identity;
- usable generated 3D;
- bounded human correction;
- ATLAS normalization;
- product integration;
- printability;
- a physical result judged commercially plausible.

Only then does the program proceed toward broad pilot and product expansion.

---

# END OF PART 2

Next authority document:

`SPC_V1_PART_3_BUSINESS_PILOT_AND_GOVERNANCE.md`


<!-- SPC_G4_PRODUCTION_NORMALIZATION_CHECKPOINT_2026_09_05 -->
## SPC-G4 Checkpoint — Production Topology + 150 mm Normalization — 2026-09-05

**Status:** `ACTIVE / NOT YET CLOSED`

### Closed in this checkpoint

1. **Source-preserving topology cleanup — PASS**
   - Exact-weld Tripo mesh retained as G4 source route.
   - 4 components reduced to 1 by removing only 3 microscopic debris components.
   - Faces: 1,428,723 → 1,428,718.
   - Removed faces: 5.
   - Main geometry: watertight and winding consistent.
   - No smoothing, remeshing, or facial reshaping performed.

2. **150 mm production normalization — PASS**
   - Final dimensions: 117.293457 × 150.000000 × 123.782516 mm.
   - Y = vertical axis.
   - Lowest Y = 0 mm.
   - X/Z centered at origin.
   - Uniform scale only.
   - Output SHA256: `29d56b1f1cdba6be9f5d9b77b6a3280baa1e90d1ac9509ca3aef8b8a0f73c667`.

### Explicitly parked

- Facial micro-artifact cleanup is `PARKED / NON-BLOCKING`.
- G4.22 spatial-cluster diagnostic is cancelled/not required for the current commercial path.
- No additional cheek-mask or micro-surface tuning should be performed unless a later physical/visual production test demonstrates a real blocker.

### Remaining G4 work

Only production-relevant checks remain: printability / fragile-feature feasibility and product integration needed to decide the final G4 gate.

`SPC-G5 = NOT STARTED`.

`Phase 9 = NOT AUTHORIZED / NOT STARTED`.

Persistent evidence:
`EVIDENCE/SPC_G4/production_normalization_2026_09_05/`
<!-- /SPC_G4_PRODUCTION_NORMALIZATION_CHECKPOINT_2026_09_05 -->
