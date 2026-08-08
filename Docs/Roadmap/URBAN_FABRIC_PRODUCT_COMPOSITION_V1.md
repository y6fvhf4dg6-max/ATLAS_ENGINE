# ATLAS ENGINE — Urban Fabric & Product Composition V1

**Status:** ACTIVE ROADMAP
**Date:** 7 August 2026
**Baseline safe commit:** `50daf58a00e31dd99f403af5eb8a6ac2edef3bba`
**Previous locked package:** Automatic Print Optimization and Reporting V1
**Current first step:** 8.7 Avenue Tree Row Engine

---

# 1. Purpose

This roadmap defines the next major ATLAS_ENGINE development package:

**Urban Fabric & Product Composition V1**

The objective is not to copy a competitor's geometry or visual styling.

The objective is to make ATLAS city products read as coherent physical cities
at product scale while preserving ATLAS's existing strengths in:

- semantic landmarks
- architectural grammar
- terrain
- LoD
- printability analysis
- multicolor product generation
- physical production validation

The roadmap was created after a direct visual product comparison with
Lichtbild city models.

Only externally visible product behavior was analyzed.

No claim is made about Lichtbild's internal software implementation.

---

# 2. Strategic finding

The central competitive finding is:

> Lichtbild's visible strength is not primarily individual building detail.
> Its strength is coherent urban, landscape and infrastructure composition.

Visible Lichtbild products consistently make the following readable as one
system:

- road hierarchy
- urban blocks
- parks
- forests
- avenues
- railway corridors
- waterways
- bridges
- terrain
- settlement density
- landcover
- generic buildings

ATLAS currently has stronger potential in semantic landmark intelligence but
the generic fabric surrounding those landmarks is not yet equally coherent.

The target is therefore:

> Lichtbild-level urban fabric coherence
> +
> ATLAS semantic architectural intelligence
> +
> ATLAS LoD and print-production infrastructure.

---

# 3. Target rendering architecture

Urban products should no longer be treated as one homogeneous class of
geometry.

The target composition model has three conceptual levels.

## 3.1 Generic city fabric

Primarily controlled low-relief / cartographic physical geometry:

- roads
- paths
- rail
- plazas
- park surfaces
- vegetation masses
- generic blocks
- water edges
- infrastructure corridors

These elements must prioritize physical readability over unnecessary
micro-geometry.

## 3.2 Semantic buildings

Buildings with meaningful architectural properties may retain stronger
3D form:

- roof grammar
- height
- footprint identity
- building type
- visible semantic components

## 3.3 Landmark grammar

Important landmarks remain full ATLAS semantic landmarks.

Examples include:

- churches
- mosques
- towers
- castles
- bridges
- ancient theatres
- other cataloged landmark families

Urban-fabric work must not weaken landmark grammar.


# 4. Exact Bonn competitor benchmark

The first controlled benchmark is Bonn.

Lichtbild customer configuration observed:

- physical size: `14 × 14 cm`
- displayed coverage: `0.44 km²`
- selected center:
  - latitude: `50.733270`
  - longitude: `7.100440`

For an approximately square 0.44 km² footprint:

- approximate side length: `663.3 m`
- equivalent ATLAS physical scale: approximately `1:4738`

Exact ATLAS benchmark bbox used:

```text
(
    50.73029066115702,
    7.09573279357563,
    50.736249338842974,
    7.10514720642437
)
Source PBF:

Data/OSM/bonn-muensterplatz-test.osm.pbf

Generated ATLAS comparison artifact:

OUTPUT/STL/bonn_lichtbild_14cm_exact_0_44km2.stl

Generation result:

* terrain: approximately 140 × 140 mm
* XY scale: 1:4738
* meshes: 922
* triangles: 70798

This benchmark is the initial Urban Fabric V1 reference fixture.

It is not sufficient by itself for final general acceptance.


# 5. Visible Lichtbild findings

These observations are based only on externally visible Lichtbild products.
No assumption is made about Lichtbild's internal implementation.

## 5.1 Roads

Roads form a clear visual hierarchy.

Major corridors remain readable even inside dense urban fabric.

## 5.2 Urban blocks

Buildings read as coherent blocks and street walls rather than as unrelated
individual extrusions.

Courtyards and block morphology remain legible.

## 5.3 Parks

Parks read as complete systems combining:

- ground surfaces
- paths
- lawns
- tree rows
- vegetation clusters
- boundaries

## 5.4 Avenue trees

Repeated tree rows reinforce roads, promenades and formal park geometry.

Trees act as urban-structure signals, not merely decoration.

## 5.5 Forests

Dense forests read as continuous vegetation masses.

Forest representation is visually distinct from isolated-tree scattering.

## 5.6 Water

Water is treated as a major composition layer.

Visible examples show strong readability of:

- rivers
- canals
- shorelines
- islands
- bridges
- embankments
- waterfront infrastructure

## 5.7 Railway and infrastructure

Rail corridors visibly contribute to city morphology.

Parallel rail and infrastructure patterns remain readable at product scale.

## 5.8 Terrain

Terrain prominence changes according to scene morphology.

Dense urban scenes suppress terrain.

Rural, mountain and natural scenes allow terrain to become more dominant.

## 5.9 Semantic surface language

Open land is not always left visually empty.

Shallow physical patterns can communicate:

- farmland
- grass
- forest
- slope or contour structure

## 5.10 Physical cartographic exaggeration

Small features remain readable even at small product sizes.

ATLAS must therefore distinguish strict geometric scale from
product-readable physical dimensions.


# 6. ATLAS current competitive strengths

Urban Fabric V1 must preserve existing ATLAS advantages.

These include:

- semantic landmark catalog architecture
- worship grammar
- church grammar
- facade/window/ornament systems
- architectural relief
- bridge systems
- castle systems
- terrain pipeline
- roof grammar
- official LoD infrastructure
- semantic multicolor output
- Automatic Print Optimization and Reporting V1
- real Bambu 3MF production validation

The goal is not to replace these systems.

The goal is to build coherent urban fabric around them.


# 7. Current visible ATLAS weaknesses to investigate

The Bonn benchmark suggests the following areas require controlled audit.

These are hypotheses until 8.0 proves their causes.

- weak road hierarchy
- roads insufficiently structuring the city
- fragmented generic building appearance
- weak urban-block continuity
- park surfaces not visually dominant enough
- Hofgarten composition not reading as a complete park system
- isolated tree clutter
- missing or weak avenue-tree rhythm
- forest/cluster vegetation not differentiated from isolated trees
- railway and transport corridors visually underrepresented
- possible generic building-height outliers
- terrain may dominate dense urban scenes
- generic landcover surfaces can appear visually empty
- physical widths may be scale-correct but product-unreadable

No corrective implementation should be started before 8.0 identifies which
items are:

- actual data problems
- pipeline bugs
- missing semantic classifications
- missing product-composition policies
- intentionally absent features


# 8. Development rules

Urban Fabric V1 follows the normal ATLAS_ENGINE development discipline.

## 8.1 Test-first

Each behavioral package begins with a focused failing test.

## 8.2 General solutions only

Do not add:

- Bonn-specific hacks
- Hofgarten-specific hacks
- Lichtbild-specific geometry imitation
- coordinate-specific exceptions
- landmark-specific fixes inside generic urban systems

## 8.3 Preserve existing architecture

Do not bypass existing:

- semantic architecture
- landmark catalog
- LoD
- terrain
- color scene
- print optimization systems

Integrate through general contracts.

## 8.4 One narrow package at a time

Do not implement several roadmap items in one uncontrolled change.

## 8.5 Regression sequence

For each meaningful package:

1. focused tests
2. related regression
3. full regression
4. documentation
5. scoped staging
6. commit
7. push
8. verify HEAD equals origin/main

## 8.6 Documentation

Meaningful milestones update:

- Docs/STATUS/CURRENT_STATUS.md
- Docs/START_HERE.md

This roadmap is the authoritative long-form design reference for package 8.


# 9. Roadmap

## 8.0 — Bonn Urban Fabric Ground-Truth Audit

**Status: COMPLETED — 7 August 2026**

**No production behavior changes were made during this audit.**

Exact benchmark:

- center: `50.733270, 7.100440`
- product: `140 × 140 mm`
- coverage: `0.44 km²`
- effective scale: approximately `1:4738`
- final benchmark: `922` meshes / `70798` triangles

Verified findings:

- Railway source exists but is not collected by `AtlasLocalOSMReader`.
  Exact bbox contains `27` railway ways; surface candidates are `3` tram
  ways and `2` Hauptbahnhof platforms. Tunnel/proposed/disused records
  require separate policy. This is a true missing capability.
- Highway-line source contains `353` records. `62` are accepted by the
  current road builder and `291` are rejected:
  `144 footway`, `118 pedestrian`, `23 steps`, `6 path`.
  Vehicle-road width hierarchy already exists; pedestrian fabric does not.
- Major Bonn plazas such as Münsterplatz and Markt are predominantly
  represented by line-based `highway=pedestrian` source geometry, not one
  closed plaza polygon. Existing source is therefore present but currently
  not expressed in production geometry.
- Hofgarten source geometry is present end-to-end. OSM way `102199952`
  (`leisure=park`) becomes a final terrain-following park mesh, but its
  semantic/product expression is weak rather than missing.
- Vegetation clutter is primarily composition-related. Exact bbox contains
  `146` OSM trees and `276` WorldCover samples. Inside Hofgarten the split
  is `6` OSM trees versus `75` WorldCover-derived trees.
- WorldCover tree-cover is currently sampled into isolated tree objects
  without urban-context semantics. `AtlasGreenAreaTreeSampler` exists but
  is not integrated into production. `tree_rows` exists in the nature
  contract but has neither a producer nor a production consumer.
- No building-part vertical-interval double-counting bug was found.
  Elevated parts correctly use `bottom = foundation + min_height` and
  `top = foundation + height`.
- High Bonn building-part records inspected during the audit belong to
  Bonner Münster and Kreuzkirche and are not generic-height outliers.
- Generic building height handling is broadly coherent. The notable
  Universitätshauptgebäude outlier is source-valid historic castle
  semantics combined with product-scale castle exaggeration:
  `6.0 mm` castle-wing body minimum plus `4.4 mm` multi-gable roof.
  This is a morphology/product-composition policy issue, not a source or
  height-parser bug.
- Inland water source contains `4` records and produces `3` final meshes.
  `Kaiserbrunnen` is deterministically excluded because `amenity=fountain`
  alone is outside current surface-water policy. Water source identity and
  names are lost before final mesh output.
- Terrain generation requested SRTM but local `N50E007.hgt` was absent, so
  the benchmark used the existing OpenTopography COP30 fallback.
  No obvious terrain scaling bug was found. Actual provider/fallback
  provenance is not preserved in final result metadata.
- Bonn contains `435` main building polygons. Proximity grouping produces
  `43` clusters at `2 m`, `39` at `4 m`, `24` at `6 m`, and `6` at `10 m`,
  confirming a naturally dense block morphology.
- At `1:4738`, many source footprints are physically tiny:
  `59` below `1 mm²`, `201` below `4 mm²`, and `340` below `9 mm²`.
- Existing building printability filtering is already intentional:
  scene rejection counts are `48` area-below-minimum,
  `47` width-below-minimum, `6` depth-below-minimum, and
  `1` triangulation failure.
  Therefore 8.4 must be block-aware composition/LoD, not a replacement
  minimum-size filter or uncontrolled building merge.

Audit conclusion:

**The principal Bonn gap is not missing OSM source truth. It is the absence
of one coherent product-scale semantic composition layer connecting existing
roads, pedestrian fabric, blocks, parks, vegetation, rail, water, terrain,
generic buildings and landmark priorities.**

8.0 therefore validates the later roadmap packages while separating
confirmed missing capabilities from existing behavior that merely needs
product/morphology-aware composition policy.


## 8.1 — Urban Fabric Scene Contract

**Status: COMPLETED — 7 August 2026**

Implemented:

- `CORE/atlas_urban_fabric_scene_contract.py`
- `Test/test_urban_fabric_scene_contract.py`

Core immutable contracts:

- `AtlasUrbanFabricElement`
- `AtlasUrbanFabricRelationship`
- `AtlasUrbanFabricScene`

The contract preserves:

- source identity
- semantic class
- product priority
- LoD eligibility
- geometry reference
- element relationships
- typed relationships
- scene-level referential integrity

Required core semantic classes are:

- road
- railway
- pedestrian_path
- urban_block
- generic_building
- park
- plaza
- vegetation
- water
- infrastructure_corridor
- terrain

The semantic-class system remains extensible; the required classes are the
minimum Urban Fabric V1 coverage, not a closed enum.

Scene behavior includes:

- deterministic element lookup
- semantic-class filtering
- duplicate element-ID rejection
- duplicate relationship-ID rejection
- relationship endpoint validation
- legacy related-element reference validation
- deterministic present-class reporting
- deterministic missing-required-class reporting

Validation:

- focused: `40 passed`
- related regression: `120 passed in 0.53s`
- full regression: `2913 passed in 12.75s`

8.1 changes classification/scene contracts only.

**No final production geometry behavior was changed.**


## 8.2 — Road Hierarchy Engine

**Status: COMPLETED — 7 August 2026**

Implemented:

- `CORE/atlas_urban_road_hierarchy_resolver.py`
- `Test/test_urban_road_hierarchy_resolver.py`
- `Test/test_road_foundation_builder_urban_hierarchy.py`
- `Test/test_foundation_first_road_hierarchy_integration.py`

Integrated with:

- `CORE/atlas_road_foundation_builder.py`
- `CORE/atlas_foundation_first_engine.py`

Core immutable product contract:

- `AtlasUrbanRoadProfile`

Core resolver:

- `AtlasUrbanRoadHierarchyResolver`

Source highway classes are resolved into product-semantic classes:

- motorway / trunk / primary / secondary / tertiary -> `major_road`
- residential / living_street / unclassified / road -> `local_road`
- service -> `service_road`
- footway / path / pedestrian / steps -> `pedestrian_path`
- cycleway -> `cycleway`
- bridleway -> `bridleway`

`cycleway` and `bridleway` are recognized semantically but their physical
corridor profiles are intentionally deferred to 8.3 Linear Infrastructure
Engine.

Road product profiles carry:

- semantic priority
- physical width
- minimum printable width
- vertical treatment
- LoD eligibility
- simplification priority

Physical-width resolution preserves source truth while supporting product
readability:

- valid OSM `width=*` is used when available
- existing ATLAS vehicle-class default widths are preserved when source width
  is absent or invalid
- real width is scaled to product millimeters
- minimum printable width is enforced
- pedestrian paths do not invent a real-world fallback width; absent or invalid
  source width falls directly to the explicit printable minimum

Relative visual hierarchy is validated for:

`major_road > local_road > service_road > pedestrian_path`

The hierarchy is enforced for semantic priority, physical width and
simplification priority when profiles are compared.

Production integration is opt-in and backward compatible:

- `AtlasRoadFoundationBuilder.build_roads(...)` accepts optional
  `minimum_printable_width_mm`
- when omitted, legacy vehicle-road behavior is preserved
- when provided, semantic road profiles can include pedestrian paths
- `AtlasFoundationFirstEngine.generate_city_stl(...)` exposes optional
  `road_minimum_printable_width_mm`
- its default is `None`, so existing products are not silently changed

No Bonn-specific widths, coordinates or landmark-specific exceptions were
introduced.

Validation:

- focused + integration: `69 passed`
- related regression: `82 passed in 1.25s`
- full regression: `2982 passed in 12.70s`


## 8.3 — Linear Infrastructure Engine

**Status: COMPLETED / LOCKED — 7 August 2026**

Create a general product-semantic system for linear infrastructure.

The engine must support at least:

- railway
- tram
- cycle corridors
- pedestrian paths
- embankments
- major infrastructure strips

Railway must not be treated as an incidental decorative line.

The engine must resolve:

- semantic class
- visual priority
- physical width
- printable minimum width
- parallel-line representation where appropriate
- LoD eligibility
- interaction with roads, bridges and surrounding urban fabric

Rail corridors must remain readable when they are important to city morphology.

The implementation must remain general and source-driven.

Do not add location-specific infrastructure rules.

Locked 8.3 implementation includes:

- source-driven semantic resolution for railway, light rail, tram,
  cycle corridors, bridleway corridors, pedestrian paths, embankments and
  infrastructure corridors
- active / proposed / disused operational-state resolution
- explicit surface-visibility and product-surface eligibility
- surface / bridge-elevated / subsurface vertical treatment
- immutable infrastructure product profiles
- source width scaling without invented real-world fallback widths
- explicit printable minimum widths
- gauge-aware parallel-line readability
- `linear_strip` and `area_strip` geometry contracts
- source geometry to product-space footprint conversion
- terrain-following closed infrastructure solids
- `AtlasLocalOSMReader` collection and public result exposure
- cycleway separation from the legacy pedestrian-path bucket
- Bonn exact-benchmark validation preserving three active surface tram
  corridors and one closed railway land-use corridor

Validation at final pre-commit lock:

- focused 8.3 package: `102 passed in 0.09s`
- related regression: `105 passed in 0.35s`
- full regression: `3085 passed in 12.59s`


## 8.4 — Urban Block Resolver

Improve generic city coherence without falsifying source building footprints.

The resolver must reason about:

- road-defined urban blocks
- buildings belonging to the same block
- street-wall continuity
- courtyard and internal void readability
- block density
- local building-height relationships
- landmark proximity
- block-level LoD decisions

The purpose is not to merge all nearby buildings into one mesh.

The purpose is to make groups of generic buildings read as coherent urban
fabric while preserving source geometry and semantic identity.

The resolver must avoid:

- merging unrelated buildings
- closing real courtyards
- suppressing semantic landmarks
- inventing missing building footprints
- location-specific block rules

Primary acceptance principle:

> Dense city areas should read as urban blocks and street structure, not as a
> collection of disconnected individual extrusions.


## 8.5 — Park & Plaza Semantic Surface Engine

Create explicit product semantics for parks, plazas and related open urban
spaces.

The engine must distinguish at least:

- park
- garden
- plaza
- pedestrian square
- courtyard
- grass area
- cemetery
- sports field

A park must not be represented only as a colored ground polygon.

Where source data supports it, park composition should include:

- ground surface
- internal paths
- open lawns
- tree rows
- vegetation clusters
- clearings
- borders and edges

Plazas and pedestrian squares must remain visually distinct from parks and
generic terrain.

Hofgarten is the initial Bonn validation example, not a special case.

Primary acceptance principle:

> A major park must read immediately as one coherent park system at product
> scale.


## 8.6 — Vegetation Composition Engine

Differentiate vegetation by semantic role instead of treating all trees as
independent repeated objects.

The engine must support at least:

- isolated_tree
- tree_row
- tree_cluster
- forest_canopy

The representation mode must depend on source context and product scale.

Examples:

- important isolated trees may remain individual objects
- avenue trees should resolve into ordered rows
- park vegetation may resolve into controlled clusters
- forests should read as continuous canopy mass

The engine must avoid:

- uncontrolled isolated-tree scattering
- excessive tree density
- loss of important formal tree alignments
- converting forests into uniform decorative dots

Primary acceptance principle:

> Fewer but semantically organized vegetation elements should create stronger
> landscape and urban readability than uncontrolled tree count.


## 8.7 — Avenue Tree Row Engine

Detect and resolve formal tree alignments along urban and landscape structure.

Candidate contexts include:

- roads
- boulevards
- promenades
- park axes
- formal park boundaries
- pedestrian corridors

The engine must reason about:

- row direction
- spacing regularity
- source-tree continuity
- gaps
- product-scale minimum spacing
- relationship to adjacent roads and paths

Source trees should remain the evidence base.

The engine may regularize spacing for product readability, but it must not
invent arbitrary tree rows where no supporting source pattern exists.

Primary acceptance principle:

> Formal tree alignments should read as intentional urban rhythm rather than
> as unrelated individual trees.


## 8.8 — Semantic Surface Texture Engine

Create shallow printable geometric surface language for open land and
non-building urban surfaces.

Candidate semantic treatments include:

- farmland rows
- grass texture
- forest ground texture
- park lawn texture
- urban plaza texture
- controlled contour or slope texture

These treatments must be physical geometry, not image textures.

The engine must preserve:

- semantic surface identity
- product readability
- printability
- restrained relief depth
- compatibility with LoD

Surface texture must not overpower roads, buildings, landmarks or terrain.

The engine must avoid decorative noise added without semantic source evidence.

Primary acceptance principle:

> Open surfaces should communicate what kind of place they represent without
> becoming visually or physically noisy.


## 8.9 — Morphology-Aware Terrain Product Resolver

Terrain presentation must adapt to the character of the product area.

The existing terrain pipeline remains the source of terrain truth.

This resolver changes only product-facing terrain emphasis.

Candidate morphology behavior:

### dense urban

- strong vertical compression
- terrain remains secondary to roads and blocks

### historic core

- terrain restrained
- landmark and street structure remain dominant

### suburban

- moderate terrain emphasis

### rural

- terrain becomes more important to scene identity

### mountain

- terrain may become a dominant product feature

### landscape / nature

- terrain may carry the primary physical narrative

The resolver must reason about:

- source elevation range
- product size
- scene morphology
- urban density
- landmark presence
- physical relief range
- printability

The resolver must not modify source elevation data.

It must apply a deterministic product-profile transformation.

Primary acceptance principle:

> Terrain should support the identity of the place without overpowering the
> semantic content that matters most for that morphology.


## 8.10 — Water & Shoreline Composition Engine

Create a general product-composition system for water and waterfront structure.

The engine must support at least:

- rivers
- canals
- lakes
- coastlines
- islands
- shorelines
- embankments
- quays
- piers
- marina structures

Water must be treated as a first-class semantic scene layer.

The engine must reason about:

- water-surface continuity
- shoreline readability
- physical separation from surrounding terrain
- interaction with bridges
- interaction with roads and rail
- embankment and quay structure
- product-scale simplification
- LoD eligibility

The system must preserve source geometry and avoid inventing artificial
shoreline detail.

Primary acceptance principle:

> Water and shoreline structure should contribute clearly to city morphology
> instead of appearing as an optional flat polygon.


## 8.11 — Bridge / Infrastructure Urban Integration

Reuse existing ATLAS bridge capabilities inside the urban-fabric composition
system.

Do not rewrite the bridge engine.

The integration must connect bridge geometry with:

- road hierarchy
- railway where applicable
- water surfaces
- shorelines
- embankments
- surrounding urban blocks
- terrain placement

The system must preserve existing bridge topology and landmark behavior.

Urban integration must improve:

- approach-road continuity
- bridge-to-water relationship
- bridge-to-embankment relationship
- visual priority inside the city scene
- LoD coordination with surrounding infrastructure

The integration must remain general.

Do not add bridge rules specific to Bonn, Galata or any other single landmark.

Primary acceptance principle:

> Bridges should read as part of the complete transport and water system,
> not as isolated standalone geometry.


## 8.12 — Building Height Product Normalizer

Normalize generic building height for product readability without destroying
architecturally meaningful height information.

This package must begin only after 8.0 determines whether suspicious building
heights come from:

- explicit source height
- building:levels
- fallback height
- building-part hierarchy
- landmark-specific height
- terrain or foundation placement
- another pipeline error

The normalizer must be able to reason about:

- generic building height
- local block context
- product scale
- physical minimum readable height
- excessive background height
- statistical height outliers
- landmark proximity
- semantic building importance

Semantic landmarks must retain their own architecture and height policy.

The system must not blindly flatten real city structure.

Primary acceptance principle:

> Generic buildings should form a coherent background height field while
> meaningful landmarks remain visually dominant.


## 8.13 — Physical Cartographic Exaggeration Resolver

Create an explicit system for features that become physically unreadable when
strict real-world scale is applied.

The resolver must support at least:

- roads
- railway
- pedestrian paths
- cycleways
- narrow waterways
- shoreline edges
- vegetation elements

The resolver must reason about:

- physical product size
- map scale
- nozzle diameter
- print profile
- semantic feature class
- LoD level
- minimum printable width
- relative visual hierarchy

The goal is not arbitrary enlargement.

The goal is controlled cartographic exaggeration that preserves semantic
relationships while making important features physically readable.

Strict scale must remain available as source truth.

Product geometry may use deterministic physical minimums where necessary.

Primary acceptance principle:

> Features that matter to city readability should remain physically visible
> without destroying their relative hierarchy or spatial relationships.


## 8.14 — City Composition LoD

Extend the existing ATLAS LoD system from individual mesh complexity toward
whole-city composition.

Do not rewrite the current LoD architecture.

The system must use urban semantics to decide which elements remain important
at a given product scale.

Candidate decisions include:

- preserve landmarks at higher LoD
- simplify generic urban blocks
- suppress very minor paths when necessary
- retain major road hierarchy
- generalize tree rows
- collapse excessive vegetation detail
- simplify small isolated buildings
- preserve important railway corridors
- retain major park and water structure

LoD decisions must consider:

- semantic importance
- physical product scale
- scene morphology
- landmark proximity
- printability
- visual hierarchy

Primary acceptance principle:

> LoD must control the narrative hierarchy of the city, not only triangle
> count.


## 8.15 — Scene Morphology Classifier

Classify the product area according to its dominant urban and landscape
character.

Initial candidate classes:

- dense_urban
- historic_core
- suburban
- rural
- forest
- river_city
- coastal
- mountain
- mixed

Classification must be deterministic and evidence-driven.

Candidate evidence includes:

- building density
- road density
- block compactness
- vegetation coverage
- forest coverage
- water coverage
- railway presence
- terrain relief
- landmark density
- landcover distribution

The classifier must not use location names as shortcuts.

It must describe scene morphology, not city identity.

Primary acceptance principle:

> Two geographically different areas with similar morphology should resolve to
> similar composition behavior.


## 8.16 — Morphology Composition Policy

Apply product-composition behavior according to the resolved scene morphology.

The policy must control relative emphasis without changing source truth.

Candidate behavior:

### dense_urban

- suppress terrain prominence
- prioritize road hierarchy
- strengthen urban-block readability
- control vegetation clutter
- preserve important infrastructure corridors

### historic_core

- prioritize street structure
- preserve compact urban fabric
- retain landmark dominance
- restrain terrain and generic vegetation

### suburban

- balance buildings, roads, vegetation and moderate terrain

### forest

- prioritize canopy and clearings
- reduce isolated-tree noise
- preserve important paths and roads

### rural

- prioritize terrain, landcover and settlement structure
- reduce unnecessary urban-style detail

### river_city / coastal

- prioritize water
- shorelines
- bridges
- embankments
- waterfront infrastructure

### mountain

- preserve terrain dominance
- simplify secondary urban detail where necessary

### mixed

- combine policies according to measured scene evidence without arbitrary
  location-specific rules

The policy must be deterministic and profile-driven.

Primary acceptance principle:

> Scene composition should reflect the dominant physical character of the
> place instead of applying one universal visual recipe everywhere.


## 8.17 — Semantic Color / Material Hierarchy

Create a product-level material hierarchy for urban scenes.

Color and material decisions must communicate semantic role rather than act as
pure decoration.

Candidate semantic roles include:

- generic buildings
- landmark walls
- landmark roofs or accents
- vegetation
- water
- roads and hardscape
- terrain
- frame
- label elements

The system must remain configurable by product family and production profile.

It must preserve the ATLAS multicolor strategy and the maximum practical
physical color count.

Do not hard-code Lichtbild's palette.

The hierarchy must still work when several semantic classes share the same
physical filament color.

In those cases, geometry, relief depth and surface treatment must preserve
readability.

Primary acceptance principle:

> Materials should reinforce scene hierarchy while preserving ATLAS product
> identity and production constraints.


## 8.18 — Customer Preview Parity

Customer-facing preview must use the same semantic composition policy as the
physical production scene.

Preview and production must agree on:

- road hierarchy
- building importance
- landmark dominance
- park and vegetation composition
- water hierarchy
- terrain emphasis
- LoD decisions
- material and color roles

The preview may use rendering-specific visual techniques, but it must not
promise geometry or hierarchy that the physical product does not contain.

The system should support:

- consistent camera framing
- product-size awareness
- morphology-aware scene composition
- semantic color preview
- landmark highlighting where the product profile allows it

Primary acceptance principle:

> The customer should receive a physical product whose composition matches the
> scene hierarchy shown in the preview.


## 8.19 — Urban Fabric Quality Report

Create a read-only quality report for urban composition.

The report must measure scene quality without silently changing geometry.

Candidate metrics include:

- road hierarchy coverage
- major-road continuity
- railway coverage
- park semantic coverage
- vegetation mode distribution
- isolated-tree clutter ratio
- avenue tree-row count
- forest continuity
- urban-block continuity
- generic building-density metrics
- building-height outlier count
- terrain prominence ratio
- water completeness
- semantic surface coverage
- composition LoD statistics
- landmark-to-background prominence ratio

The report should identify both:

- missing semantic content
- visually weak but technically present content

Where practical, metrics should be deterministic and reproducible from the
same scene input.

The report must not automatically:

- modify geometry
- suppress features
- normalize heights
- change LoD
- alter material assignments

Primary acceptance principle:

> Urban Fabric quality must become measurable enough that regressions can be
> detected before relying only on visual inspection.


## 8.20 — Multi-Morphology Acceptance Benchmarks

Bonn is the first controlled Urban Fabric benchmark.

Final V1 acceptance must not rely on Bonn alone.

The system must also be validated against contrasting scene morphologies.

Required benchmark families:

- dense urban
- historic core
- river or water city
- forest or suburban
- rural or mountain

Existing ATLAS locations may be reused where they provide appropriate source
data and morphology.

Each benchmark must verify that the same general systems behave correctly
without location-specific exceptions.

The purpose is to prevent overfitting to:

- Bonn
- Hofgarten
- one road pattern
- one vegetation pattern
- one terrain profile
- one landmark family

Acceptance must confirm that improvements to one morphology do not degrade
another.

Primary acceptance principle:

> Urban Fabric V1 is complete only when the same general architecture improves
> multiple fundamentally different city and landscape types.


# 10. Bonn V1 acceptance criteria

The exact Bonn benchmark must ultimately satisfy the following visible product
criteria.

## 10.1 Roads

- primary road structure is immediately readable
- secondary hierarchy remains visible
- minor paths do not overpower roads

## 10.2 Hofgarten

- reads clearly as one coherent park system
- park surface is visible
- internal paths are visible
- vegetation composition is structured
- tree rows are preserved where source evidence supports them

## 10.3 Vegetation

- uncontrolled isolated-tree clutter is reduced
- formal rows read as rows
- dense vegetation reads as cluster or canopy mass

## 10.4 Buildings

- generic city fabric reads as coherent blocks
- destructive generic height outliers are eliminated
- Bonner Münster landmark dominance is preserved

## 10.5 Railway and infrastructure

- important railway or infrastructure corridors contribute visibly to city
  morphology when present in source data

## 10.6 Terrain

- terrain supports the Bonn city scene
- terrain does not visually overpower urban fabric

## 10.7 Water

- water is represented correctly when present in the benchmark area

## 10.8 Product readability

At `140 × 140 mm`:

- major roads remain physically readable
- minor details follow explicit printable minimums
- generic detail does not compete with semantic landmarks


# 11. What must NOT happen

Urban Fabric V1 must not become:

- a Lichtbild clone
- a Bonn-only renderer
- a collection of coordinate-specific exceptions
- a collection of Hofgarten-specific fixes
- a replacement for source truth
- an automatic invention of missing buildings
- an uncontrolled geometry merger
- an excuse to weaken landmark architecture
- a rewrite of working terrain systems
- a rewrite of working bridge systems
- a rewrite of the existing LoD architecture
- a second Automatic Print Optimization package

Generic Urban Fabric systems must remain:

- source-driven
- deterministic
- test-first
- morphology-aware
- product-scale aware
- compatible with existing ATLAS semantic architecture

Competitor observations may define acceptance targets.

They must not become hard-coded implementation rules.

Primary rule:

> Improve ATLAS through general architecture, not competitor-specific imitation.


# 12. Competitive target

The product goal can be summarized in two complementary principles.

First:

> Every square millimeter should communicate what kind of place this is.

Second:

> Important places should also remain architecturally recognizable.

The final ATLAS competitive target is therefore:

- coherent cartographic urban fabric
- semantic architectural landmarks
- physically readable product-scale geometry
- morphology-aware composition
- controlled LoD
- validated print production
- faithful customer preview
- deterministic recoverable product configuration
- asynchronous preview generation with backend progress
- preview caching based on deterministic product state
- explicit preview-to-production parity contract

The intended differentiation is:

> best-in-class urban coherence
> +
> ATLAS-level landmark intelligence
> +
> ATLAS print and LoD infrastructure

This roadmap should strengthen ATLAS without removing the architectural and
semantic systems already developed.


# 13. Immediate next action

8.6 Vegetation Composition Engine is complete and ready to lock.

Final validation:

- focused vegetation resolver: `51 passed in 0.07s`
- vegetation + engine integration: `57 passed in 0.16s`
- related regression: `154 passed in 0.36s`
- full regression: `3217 passed in 12.60s`

The next and only development step is:

## 8.7 — Avenue Tree Row Engine

8.7 must proceed test-first. Do not start 8.8 or later behavior until
8.7 is complete.
