# ATLAS — Stylized Personalized Collectible Program V1
## PART 3 — Business, Pilot, Expansion and Governance

**Parent program:** `SPC_V1`

**Required predecessors:**

- `SPC_V1_PART_1_STRATEGY_AND_IDENTITY.md`
- `SPC_V1_PART_2_3D_ATLAS_AND_PRODUCT.md`

---

# 18. PROGRAM 11 — UNIT ECONOMICS

Unit economics shall be based on measured production data.

Not optimistic assumptions.

---

# 18.1 Cost structure

For every SKU track:

## AI / digital

- 2D generation;
- regeneration;
- multi-view generation;
- 3D generation;
- API charges;
- cloud compute;
- local compute where meaningful.

## Human

- visual review;
- correction;
- mesh cleanup;
- customer support;
- revisions;
- physical QA.

## Physical production

- filament;
- resin if relevant;
- purge;
- support material;
- electricity;
- machine occupancy;
- failed-print reserve;
- post-processing;
- assembly.

## Packaging

- gift box;
- protective insert;
- labels;
- print material;
- packing labor.

## Commercial

- payment fees;
- marketplace fees;
- storefront costs;
- refund/reprint reserve;
- fulfillment preparation.

Shipping shall be tracked separately and/or incorporated according to the actual offer structure.

---

# 18.2 Human cost

For every order:

`HUMAN_MINUTES`

must be known.

Human time shall not disappear into hidden founder labor.

---

# 18.3 AI cost

Record separately:

- successful generation cost;
- failed generations;
- regeneration;
- candidate generation;
- API overhead.

The cheapest model is not necessarily the cheapest model per successful order.

---

# GATE SPC-G6 — ECONOMIC FEASIBILITY

Question:

> Can the product achieve commercially acceptable economics at a price customers plausibly accept?

If FAIL investigate:

- product size;
- AI vendor;
- number of variants;
- human intervention;
- material;
- print technology;
- packaging;
- SKU complexity;
- selling price.

Do not attempt to solve a structurally unprofitable SKU by hiding labor.

---

# 19. PROGRAM 12 — EARLY MARKET VALIDATION

Market validation runs IN PARALLEL with engineering.

It does not wait until the technology is complete.

---

# 19.1 Questions to answer

Determine:

- which style people prefer;
- whether the product feels personal;
- whether it looks gift-worthy;
- what occasions trigger purchase;
- acceptable price bands;
- acceptable delivery times;
- revision expectations;
- whether preview increases confidence;
- common objections;
- whether Chibi vs Bust vs Bobblehead appeals to different customers.

---

# 19.2 Progressive validation

Start approximately:

## Stage 1

10 observations.

Goal:

Detect major product/style rejection quickly.

## Stage 2

Approximately 25 observations.

Goal:

Test:

- style;
- price;
- preview;
- purchase intent.

## Stage 3

Approximately 100 customer/order-equivalent observations where justified.

Goal:

Estimate repeatable demand signals rather than anecdotes.

These numbers are guides.

Each stage must answer a defined uncertainty.

---

# 19.3 Landing-page validation

Before full-scale production software, test a realistic offer.

Show:

- product images;
- before/after;
- customization;
- 2D preview promise;
- 3D preview;
- price;
- delivery;
- gift scenarios.

Measure behavior rather than only asking:

> “Do you like this?”

---

# 19.4 Willingness to pay

Test actual price reactions.

Do not assume that a competitor selling at a particular price proves ATLAS can successfully sell at the same price.

---

# 20. PROGRAM 13 — CONTROLLED COMMERCIAL PILOT

Pilot begins only after sufficient upstream feasibility.

---

# 20.1 Pilot objective

Test the entire operational chain under conditions approximating real commerce.

Initial target:

approximately 25 real paid orders or sufficiently realistic equivalent orders.

Paid orders are preferable once legally and operationally appropriate because stated interest is weaker evidence than payment.

---

# 20.2 Record per order

## Input

- photo quality;
- recapture required;
- number of source images.

## 2D

- candidates generated;
- selected candidate;
- regeneration count;
- correction request;
- time to approval.

## Multi-view

- consistency problems;
- regeneration;
- manual intervention.

## 3D

- generator;
- generation count;
- failures;
- mesh quality;
- identity quality.

## ATLAS

- automatic repairs;
- failed gates;
- manual corrections;
- processing time.

## Human

- intervention class H0–H4;
- exact minutes;
- correction categories.

## Production

- slice time;
- print time;
- filament/material;
- color changes;
- failures;
- reprints;
- post-processing.

## Commercial

- sale price;
- discounts;
- COGS;
- fulfillment time.

## Customer

- likeness rating;
- style rating;
- product-quality rating;
- emotional response;
- recommendation intent;
- complaint;
- revision;
- refund.

---

# GATE SPC-G7 — PIVOT LOCK

SPC becomes:

`PRIMARY_COMMERCIAL_TRACK`

only if BOTH technical and commercial evidence support it.

Required evidence classes:

## Technical

- 2D identity = PASS;
- multi-view consistency = PASS;
- 3D identity transfer = PASS;
- ATLAS normalization = PASS;
- physical Chibi quality = PASS;
- operational burden acceptable.

## Commercial

- product desirability supported;
- price acceptance supported;
- unit economics plausible;
- revision rate manageable;
- customer satisfaction sufficient.

Only after this gate is the master ATLAS commercial direction formally pivoted.

---

# 21. PRODUCT EXPANSION ORDER

Product order remains:

`1 -> 3 -> 2`

---

# 21.1 Product 1 — Chibi

First end-to-end proof.

Chibi establishes reusable infrastructure for:

- capture;
- identity;
- 2D approval;
- multi-view;
- 3D;
- ATLAS normalization;
- physical production;
- commercial workflow.

---

# 21.2 Product 3 — Stylized Bust

Development begins after Chibi establishes sufficient reusable infrastructure.

Bust-specific work focuses on:

- crop level;
- shoulders;
- neck;
- pedestal;
- premium composition;
- hair;
- wrinkles;
- age/life-line detail;
- surface finish;
- presentation;
- premium packaging.

Potential strategic advantage:

A Bust gives the head more physical area and may support stronger facial readability than a small full-body Chibi.

It therefore may become the premium likeness-oriented product.

---

# 21.3 Product 2 — Bobblehead

Begins after sufficient Chibi/Bust evidence.

Initial Bobblehead:

`FIXED_HEAD`

Focus:

- recognizable head;
- standardized stylized body;
- pose;
- clothing;
- accessories;
- base.

Spring/bobble mechanism is later.

Only implement it if product demand justifies:

- additional assembly;
- tolerance requirements;
- durability complexity;
- packaging risk.

---

# 22. OFFER ARCHITECTURE

Potential structure to validate.

No price is locked by this roadmap.

---

# 22.1 Entry product

Possible:

`CHIBI SINGLE`

Features:

- one person;
- standard style;
- bounded outfit;
- standard base.

---

# 22.2 Mid product

Possible:

- enhanced Chibi;
- custom outfit;
- hobby/profession;
- pet;
- later Bobblehead.

---

# 22.3 Premium product

Possible:

- Stylized Bust;
- couple;
- custom scene;
- enhanced personalization;
- premium base;
- premium packaging.

---

# 22.4 Upsells

Potential:

- additional person;
- pet;
- custom clothing;
- custom pose;
- accessory;
- premium base;
- engraving;
- name;
- date;
- location;
- scene;
- rush production;
- gift packaging.

All upsells require unit-economics validation.

---

# 23. BUILD VS BUY

The initial goal is product validation.

Not unnecessary foundational-model development.

---

# 23.1 Buy / API initially where useful

Potential external capability:

- 2D stylization;
- identity-conditioned image generation;
- multi-view generation;
- image/multi-view-to-3D;
- temporary specialist cleanup.

Reasons:

- faster validation;
- lower initial engineering cost;
- ability to benchmark several technologies.

---

# 23.2 Own in ATLAS

ATLAS should own core product authority:

- contracts;
- identity semantics;
- evidence;
- candidate evaluation;
- mesh normalization;
- mesh safety;
- printability;
- scale;
- product templates;
- personalization;
- production rules;
- QA;
- cost accounting;
- approval-workflow logic.

---

# 23.3 Internalize later

Reconsider externally purchased capabilities when:

- API cost becomes material;
- quality becomes limiting;
- privacy is unacceptable;
- licensing creates risk;
- latency matters;
- vendor dependence becomes strategic;
- enough proprietary data exists to justify internal capability.

Do not internalize simply because building technology is technically interesting.

---

# 24. KPI FRAMEWORK

KPIs must prioritize product outcomes.

Not only engineering metrics.

---

# 24.1 2D identity success

Initial experimental target:

At least 8/10 benchmark subjects obtain an acceptable stylized identity under bounded generation.

---

# 24.2 Multi-view consistency

Measure percentage of approved 2D identities that can produce an acceptable coherent multi-view set.

---

# 24.3 3D identity retention

Measure percentage of approved 2D identities that remain recognizable after 3D generation.

---

# 24.4 Human intervention

Track:

- H0;
- H1;
- H2;
- H3;
- H4.

Long-term objective:

increase H0 + H1.

---

# 24.5 Revision burden

Track:

- 2D revisions;
- multi-view revisions;
- 3D revisions;
- customer-requested changes.

---

# 24.6 Generation failure

Track failure by:

- vendor;
- style;
- source quality;
- identity characteristics.

---

# 24.7 Print failure

Track actual:

- failed prints;
- broken parts;
- support damage;
- cosmetic rejects;
- shipping damage.

---

# 24.8 Customer perception

Track:

- likeness;
- style;
- emotional appeal;
- quality;
- giftability;
- recommendation.

For SPC commercial products:

customer perception outranks pure geometric reconstruction error.

---

# 24.9 Economics

Track per SKU:

- COGS;
- contribution margin;
- human minutes;
- machine hours;
- reprint reserve;
- average order value.

---

# 25. MASTER KILL RULES

---

# KILL-1 — 2D identity

If stylized 2D repeatedly loses identity:

Do NOT move downstream.

---

# KILL-2 — Multi-view

If the character changes identity across views:

Do NOT trust multi-view 3D generation.

---

# KILL-3 — 3D transfer

If approved 2D consistently becomes generic 3D:

Change generator/architecture.

Do not hide the problem with manual sculpting unless economics explicitly support premium manual work.

---

# KILL-4 — Human labor

If normal orders require more than approximately 30 minutes of routine manual cleanup:

Production architecture is suspect.

Reassess:

- upstream AI;
- ATLAS automation;
- product style;
- pricing.

---

# KILL-5 — Physical ceiling

If FDM quality cannot support the product:

Do not endlessly optimize digital geometry.

Test:

- larger product;
- modified style;
- resin;
- external production.

---

# KILL-6 — Economics

If COGS destroys viable margin:

Change:

- SKU;
- size;
- AI;
- human process;
- manufacturing;
- price.

---

# KILL-7 — Customer rejection

If bounded preview plus revision still yields repeated rejection:

Do not launch that product configuration.

---

# 26. DATA AND LEARNING STRATEGY

Subject to legal basis, privacy policy and explicit customer permissions where required, operational signals may become valuable.

Potential pattern:

`CANDIDATE`
->
`REJECTION REASON`
->
`CORRECTION`
->
`APPROVAL`
->
`PHYSICAL RESULT`

Future uses may include:

- candidate ranking;
- quality prediction;
- correction automation;
- improved capture guidance;
- style-prior improvement;
- vendor selection;
- ATLAS rule development.

No commercial customer-data reuse is automatically authorized.

Privacy/legal authority governs such use.

---

# 27. STRATEGIC MOAT

ATLAS should NOT compete solely on:

> “We can make an AI figurine.”

That capability will increasingly commoditize.

The intended moat is:

# AI-TO-PHYSICAL PERSONALIZED PRODUCT ENGINE

Combining:

- identity-aware generation;
- deliberate style;
- customer approval;
- consistent multi-view;
- 3D generation;
- ATLAS deterministic control;
- mesh safety;
- printability;
- product architecture;
- physical manufacturing;
- personalization;
- evidence;
- operational learning;
- European-focused quality/fulfillment.

---

# 28. RELATIONSHIP TO MY LIFE MAP

The new people/character engine may later combine with ATLAS location products.

Potential examples:

- couple figurine + wedding location;
- graduate figurine + university map;
- family + home/city relief;
- traveller + destination;
- parent/grandparent + meaningful place;
- character + memory scene.

This may connect two ATLAS asset classes:

`PEOPLE`
+
`PLACE`

Do NOT add these combined products to first Chibi feasibility.

They are future expansion.

---

# 29. MASTER EXECUTION SEQUENCE

The current high-level order is:

1. Preserve old roadmap continuity.
2. Classify exact-likeness research as parked/non-MVP-blocking.
3. Commercial/legal AI eligibility.
4. Chibi Style Bible.
5. Identity Anchor Contract.
6. Physical Chibi preliminary contract.
7. Customer Capture Contract.
8. 2D stylized identity benchmark.
9. Human 2D identity gate.
10. Identity-locked multi-view.
11. Multi-view consistency gate.
12. 2D/multi-view-to-3D benchmark.
13. Human-time measurement from first candidate onward.
14. ATLAS mesh normalization feasibility.
15. Chibi productization.
16. Three-subject physical proof.
17. FDM/resin comparison if needed.
18. Measured unit economics.
19. Parallel market validation.
20. Controlled commercial pilot.
21. Pivot-lock decision.
22. Stylized Bust.
23. Bobblehead.
24. Later people + location combined products if justified.

---

# 30. INITIAL 90-DAY VALIDATION STRUCTURE

This is a planning framework.

It is NOT a requirement to consume exactly 90 days.

Fast PASS allows acceleration.

FAIL invokes the relevant stop rule.

---

# DAYS 1–14 — FOUNDATION + 2D PROOF

Focus:

- legal/commercial eligibility;
- Chibi Style Bible;
- Identity Anchor Contract;
- Capture Contract;
- 2D generator benchmark;
- initial market-style testing.

Primary question:

> Can we reliably create a stylized 2D character that people recognize as the intended person?

If NO:

Do not proceed into expensive 3D product development.

---

# DAYS 15–35 — MULTI-VIEW + 3D FEASIBILITY

Focus:

- identity-consistent turnaround;
- multi-view consistency;
- 3D generator benchmark;
- license/cost/latency;
- human intervention measurement.

Primary question:

> Can an approved stylized identity survive into 3D?

---

# DAYS 36–60 — ATLAS PRODUCTIZATION

Focus:

- mesh normalization;
- identity preservation;
- Chibi body/product integration;
- printability;
- initial physical proofs;
- manufacturing comparison if necessary.

Primary question:

> Can ATLAS turn generative 3D into a reliable physical product?

---

# DAYS 61–75 — OPERATIONS + ECONOMICS

Focus:

- human labor;
- production time;
- API cost;
- material;
- packaging;
- failure;
- pricing;
- unit economics.

Primary question:

> Can we produce it repeatably at plausible economics?

---

# DAYS 76–90 — CONTROLLED COMMERCIAL VALIDATION

Focus:

- customer workflow;
- real pricing;
- approval;
- production;
- delivery;
- satisfaction;
- margin.

Primary question:

> Will real customers pay for and accept the product?

---

# 31. CURRENT STATUS AT SPC ROADMAP CREATION

Existing 15-item roadmap:

`PRESERVED`

Items 1–10:

`HISTORICAL_VERIFIED_STATUS_PRESERVED`

Item 11 exact-likeness branch:

`RESEARCH_PARKED`

`NON_MVP_BLOCKING`

Items 12–15:

`HOLD_PENDING_SPC_VALIDATION`

Phase 9:

`NOT_AUTHORIZED`

`NOT_STARTED`

SPC V1:

`PIVOT_VALIDATION_ACTIVE`

First product:

`CHIBI`

Stylized Bust:

`NOT_IMPLEMENTATION_AUTHORIZED_YET`

Bobblehead:

`NOT_IMPLEMENTATION_AUTHORIZED_YET`

Primary architecture candidate:

`PHOTO(S)`
->
`STYLIZED 2D`
->
`HUMAN APPROVAL`
->
`CONSISTENT MULTI-VIEW`
->
`AI 3D`
->
`ATLAS CONTROL`
->
`HUMAN EXCEPTION HANDLING`
->
`PHYSICAL PRODUCT`

Authority model:

`AI = GENERATE`

`ATLAS = CONTROL`

`HUMAN = JUDGE / CORRECT EXCEPTIONS`

`PRODUCTION = MANUFACTURE`

---

# 32. ROADMAP UPDATE DISCIPLINE

This is a living authority set.

As work progresses:

- every meaningful gate receives PASS / FAIL / HOLD;
- evidence is referenced;
- historical results are not silently rewritten;
- architecture changes require recorded decisions;
- product-order changes require explicit approval;
- old roadmap Items 12–15 are updated only when SPC evidence justifies reassessment;
- exact-likeness research remains available for future reopening;
- Phase 9 requires separate explicit authorization;
- START_HERE / CURRENT_STATUS / devir files shall eventually reflect validated state rather than speculative assumptions.

The relationship between SPC and the original 15-item roadmap shall be reviewed and updated progressively as validated work is completed.

---

# 33. CORE STRATEGIC PRINCIPLE

The old commercial question was effectively:

> Can ATLAS reconstruct the person's exact 3D head accurately enough?

The new validation question is:

> Can ATLAS create a recognizable, desirable stylized identity and reliably convert it into a physical personalized product?

The preferred sequence is:

`IDENTITY`
->
`STYLE`
->
`APPROVAL`
->
`3D`
->
`CONTROL`
->
`PRODUCT`
->
`ECONOMICS`
->
`CUSTOMER`

This sequence shall govern SPC V1 unless new evidence justifies an explicit architecture change.

---

# END OF SPC V1 ROADMAP
