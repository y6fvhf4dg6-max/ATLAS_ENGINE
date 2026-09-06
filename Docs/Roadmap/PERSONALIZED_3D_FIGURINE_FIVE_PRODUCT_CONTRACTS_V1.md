# ATLAS — Personalized 3D Figurine Five Product and Style Contracts V1

Status: APPROVED_PRODUCT_CONTRACT_BASELINE
Production authorization: NO
Protected global rule: IDENTITY_BEFORE_STYLE

## Common contract shared by PF-1 through PF-5

PROTECTED / NOT CUSTOMER-OVERRIDABLE:
- approved personal identity and critical identity anchors;
- source rights, consent and provenance;
- safe printable topology;
- minimum structural thickness;
- stable center of mass and base contact;
- truthful preview corresponding to the production geometry;
- ATLAS scale, orientation, manifold and export validation;
- no unapproved substitution of another face, hairstyle or body;
- no printing before customer approval.

CUSTOMER-SELECTABLE WITHIN PRODUCT LIMITS:
- product family;
- size tier;
- pose from an approved catalog or custom-pose surcharge;
- clothing and profession/theme;
- hair/facial-hair/accessory description;
- base shape, color and inscription;
- one-color, part-color, full-color or hand-painted finish;
- approved props and pets;
- facial expression within identity-preserving limits;
- packaging/gift options.

## Five-family comparison

| Field | PF-1 Premium Realistic | PF-2 Modern Chibi | PF-3 Couple / Family | PF-4 Natural Keepsake | PF-5 Bobblehead / Character |
|---|---|---|---|---|---|
| Primary promise | Lifelike premium personal sculpture | Recognizable premium cute sculpture | Relationship and shared-memory composition | Warm recognizable everyday keepsake | Fun personalized character |
| Facial stylization | Very low | Low–moderate | Product-dependent; low–soft | Low–soft | Moderate; recognizable exaggeration |
| Body proportion | Natural, approximately 7–8 heads tall | Enlarged head, compact body | Coordinated by selected sub-style | Between realistic and Chibi | Strongly enlarged head, simplified body |
| V0 total-height candidate | 150–200 mm | 150 mm nominal | 140–170 mm adult reference | 120–150 mm | 140–160 mm |
| Head/total candidate | 0.13–0.16 | 0.35–0.40; nominal 0.38 | Determined by selected shared style | 0.22–0.30 | 0.35–0.45 |
| Body route | Custom or premium parametric body | Reusable stylized body library | Coordinated reusable bodies plus composition | Reusable softly stylized body | Template-assisted body preferred |
| Pose V0 | Natural standing; mild gesture | Compact natural standing | Relationship-specific interaction | Natural relaxed standing/seated later | Profession/theme pose |
| Base V0 | Integrated discreet base | Integrated 70–75 × 7–8 mm candidate | Shared composition base sized by person count | Integrated compact base | Integrated base; spring excluded initially |
| Clothing | High-detail and identity-relevant | Simplified but characteristic | Coordinated per subject/event | Characteristic everyday clothing | Template or profession costume |
| Accessories | Controlled premium detail | Limited robust props | Wedding/family/memorial props | Limited memory-bearing props | Strong thematic props allowed |
| First production mode | One-color/resin candidate; finish study required | One-color FDM pilot first | After single-person assembly proof | After PF-2 reusable identity proof | Fixed head first |
| Mechanical movement | None | None | None | None | NOT IN V0; bobble spring only after fixed-head pass |
| Complexity risk | Surface/detail and likeness | Head/body integration | Multiple identities and interaction | Style balance | Exaggeration, neck interface and later mechanism |
| Development priority | Later expansion | FIRST FULL-BODY PILOT | After repeatable single-subject flow | After shared foundation | Fixed-head after reusable body/assembly |

## Identity-anchor policy

CRITICAL ACROSS ALL FAMILIES:
- overall skull and head silhouette;
- forehead/temporal/cheek/jaw/chin character;
- head length-to-width character;
- eye spacing and inclination;
- nose character;
- mouth width/form;
- hairline and dominant hair mass.

HIGH:
- eyebrow and eye-opening character;
- bridge, tip and nostril character;
- nose-to-mouth spacing;
- lip and chin projection;
- ear openness/silhouette;
- age-related character;
- facial fullness and recognizable asymmetry;
- hair parting, curl, wave and volume.

CONTEXTUAL WHEN IDENTITY-RELEVANT:
- beard, moustache, glasses;
- moles, scars and characteristic marks;
- signature accessories.

No style profile may erase age, ethnicity, characteristic asymmetry or another
identity-bearing feature merely to make the result prettier or cuter.

## Required approval views

EVERY PRODUCT:
1. front;
2. left three-quarter;
3. right three-quarter;
4. left or right true profile as identity requires;
5. back;
6. top/cranial-hair view;
7. underside and base contact;
8. production-scale neutral render;
9. color/material render when applicable.

ADDITIONAL FOR PF-3:
- full composition front;
- both outer profiles;
- top view showing spacing/contact;
- each identity isolated at readable scale.

ADDITIONAL FOR PF-5 MECHANICAL FUTURE VERSION:
- fixed-head reference;
- neck/spring section;
- movement-clearance views;
- stability view.

## Customer proof and revision baseline

- Customer sees the production-intent 3D model before printing.
- Approval is versioned and tied to order ID.
- Face/identity correction is separated from optional style changes.
- A revision cannot silently replace already approved identity geometry.
- Initial commercial candidate: one included consolidated revision round.
- Additional customer preference changes may become paid revisions.
- ATLAS/artist-caused mismatch remains correctable without treating it as a
  customer preference change.
- Final approval freezes geometry, pose, inscription, color plan and size.
- Production begins only after explicit final approval.

## Approved product decisions

**Decision date:** `2026-09-06`

**User decision:** `APPROVED`

1. `PF-1_LAUNCH_FINISH = PREMIUM_ONE_COLOR_RESIN_WITH_OPTIONAL_HAND_FINISH`
   Full color is not mandatory at initial launch.

2. `PF-3_TECHNICAL_FAMILY = COUPLE_AND_FAMILY_SHARED_CONTRACT`
   Commercial presentation may use separate Couple Figurine and Family Figurine offers.

3. `PF-4_DEFAULT_HEIGHT_MM = 150`
   A 120 mm economy tier may be evaluated later.

4. `PF-5_V0_HEAD_MODE = FIXED_HEAD_ONLY`
   A spring/mechanical bobble version requires a later independent physical gate.

5. `BASE_INSCRIPTION = OPTIONAL_ACROSS_PF1_TO_PF5`

6. `INCLUDED_CUSTOMER_REVISION = ONE_CONSOLIDATED_ROUND`
   ATLAS/artist-caused identity or production mismatch is corrected separately and is not counted as a customer preference revision.

7. `PF-2_V0_NOMINAL_TOTAL_HEIGHT_MM = 150`

## P-1 gate recommendation

`GATE_P1 = PASS / FIVE_PRODUCT_CONTRACTS_LOCKED`

`FIVE_PRODUCT_CONTRACTS = USER_APPROVED`

`PRODUCT_LAUNCH_AUTHORIZATION = NO`

`PRODUCTION_GEOMETRY_AUTHORIZATION = NO`

`CURRENT_WORK_PROGRAM = P-2`

`CURRENT_GATE = GATE-P2`

`EXACT_NEXT = DEFINE_CUSTOMER_CAPTURE_AND_REUSABLE_IDENTITY_PACKAGE`

The next program is P-2 Customer Capture and Reusable Identity Package.
