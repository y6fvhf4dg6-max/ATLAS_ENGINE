# ATLAS SURFACE COMPOSITION PIPELINE
Version: 1.0
Date: 2026-07-06

---

# Philosophy

ATLAS does not generate independent meshes.

ATLAS generates one coherent world.

Buildings, roads, water, parks and terrain are not separate products.

They are semantic layers composing one printable city model.

---

# Surface Layers

The city is constructed from ordered layers.

```text
Frame
↓

Base Shell
↓

Terrain
↓

Water
↓

Road Surface
↓

Squares

↓

Parks
↓

Buildings
↓

Trees
↓

POIs
```

Every layer has a defined responsibility.

No layer should generate duplicate geometry.

---

# Layer Responsibilities

## Frame

Provides structural rigidity.

Never intersects semantic geometry.

---

## Base Shell

Provides printable foundation.

Completely watertight.

Never contains duplicated upper surfaces.

---

## Terrain

Defines elevation.

Everything else references terrain.

Terrain owns Z.

---

## Water

Carves the terrain.

Water is always recessed.

Never floats.

---

## Roads

Roads modify the terrain surface.

Roads are not objects.

Roads are terrain.

Road hierarchy controls:

- width
- depth
- smoothing
- intersection behaviour

---

## Parks

Parks replace terrain material.

Parks remain flush with terrain.

Only texture changes visually.

---

## Squares

City squares behave like roads.

Large continuous surfaces.

No internal fragmentation.

---

## Buildings

Buildings sit on the composed surface.

Buildings never intersect road walls.

Buildings never float.

---

## Trees

Trees reference terrain height.

Trees never determine terrain.

---

## POIs

POIs behave like buildings.

Higher detail allowed.

Independent LOD possible.

---

# Ownership Rules

Every XY coordinate belongs to exactly one surface owner.

Example:

```text
Road
↓

owns XY

Terrain removed there
```

Example:

```text
Water
↓

owns XY

Terrain removed there
```

No duplicated ownership.

---

# Boolean Philosophy

Avoid expensive CAD boolean operations.

Prefer semantic ownership.

Instead of:

```text
Terrain
Boolean Difference
Road
```

Prefer:

```text
Road owns polygon

Terrain simply does not generate triangles there.
```

This is faster.

Cleaner.

Deterministic.

---

# Triangle Budget

Production quality requires controlled triangle counts.

Targets:

Small model

< 50k triangles

Medium

< 150k triangles

Large

< 400k triangles

Only landmarks may exceed normal density.

---

# Coordinate System

Everything works in product coordinates.

No module should internally assume geographic coordinates.

Pipeline:

```text
Lat/Lon

↓

Projected coordinates

↓

Product millimeters

↓

Surface composition

↓

STL
```

---

# Module Responsibilities

AtlasReader

↓

imports data

---

AtlasScaler

↓

creates product coordinates

---

AtlasRoadEngine

↓

creates road polygons

---

AtlasPolygonTriangulator

↓

creates triangles

---

AtlasSurfaceComposer

↓

decides ownership

↓

creates printable surface

---

AtlasBuildingEngine

↓

creates buildings

---

AtlasExporter

↓

writes STL

---

# Forbidden

No duplicated surfaces.

No overlapping triangles.

No floating roads.

No floating parks.

No duplicated water.

No grid carving.

No hidden meshes inside base.

No STL repair requirements.

---

# Commercial Quality Goal

The final printed city should appear as if it were designed directly as one object.

The customer must never perceive:

- independent meshes
- seams
- artifacts
- duplicated surfaces
- construction shortcuts

Instead they should perceive:

One city.

One landscape.

One product.

---

# ATLAS Principle

Geometry follows semantics.

Not the other way around.