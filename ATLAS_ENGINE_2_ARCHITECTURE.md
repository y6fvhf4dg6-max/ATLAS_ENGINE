# ATLAS ENGINE 2.0 MASTER ARCHITECTURE

## Core Rule

ATLAS is not a collection of scripts.

ATLAS is a pipeline-based 3D city generation engine.

---

## Main Principle

No engine writes STL directly.

Engines produce mesh data.

Only Export Engine writes final files.

---

## Central Data Object

All shared data lives in:

AtlasContext

Context stores:

- address
- product
- model size
- coordinates
- bounds
- terrain mesh
- terrain sampler
- building mesh
- road mesh
- water mesh
- park mesh
- final scene mesh

---

## Pipeline

Address

↓

Geocoder

↓

Area Engine

↓

Terrain Engine

↓

Terrain Sampler

↓

Building Engine

↓

Road Engine

↓

Water Engine

↓

Park Engine

↓

Scene Engine

↓

Export Engine

---

## Engine Responsibilities

### AtlasCore

Controls the full pipeline.

Does not create geometry directly.

---

### AtlasContext

Stores shared state.

All engines read from and write to context.

---

### TerrainEngine

Creates terrain mesh once.

Never exports STL.

---

### TerrainSampler

Returns terrain height for any X/Y point.

Used by buildings, roads, water, parks, bridges and future details.

---

### BuildingEngine

Creates building meshes.

Uses context bounds, OSM data, model space, height engine and terrain sampler.

---

### RoadEngine

Creates road meshes.

Uses context bounds, OSM data, model space and terrain sampler.

---

### WaterEngine

Creates rivers, lakes and sea surfaces.

Uses context bounds and terrain sampler.

---

### ParkEngine

Creates park and green area surfaces.

Uses context bounds and terrain sampler.

---

### SceneEngine

Combines all mesh layers into one scene.

---

### ExportEngine

Exports final scene as:

- STL
- later 3MF
- later OBJ / GLB

---

## Product Logic

ATLAS supports product tiers:

- Basic
- Realistic
- Museum
- Ultra

These tiers control:

- detail level
- vertical scale
- minimum printable height
- roof detail
- road detail
- water detail
- park detail
- color / finish
- memory highlight options

---

## Design Principle

Real data is respected.

But ATLAS optimizes geometry for:

- printability
- durability
- readability
- aesthetics

The goal is not blind copying.

The goal is the best physical collectible model.

---

## Memory Product Vision

Every important memory has a location.

ATLAS turns meaningful places into physical collectible models.

Product lines:

- My Life Map
- Our Love Map
- Family Heritage
- Memory Highlight

---

## Internal Motto

Şeytan ayrıntıda.

The devil is in the details.

---

## Immediate Refactor Plan

1. Keep existing working files.
2. Build AtlasContext as shared memory.
3. Build AtlasCore as central controller.
4. Move terrain generation into Core.
5. Move buildings into BuildingEngine.
6. Move roads into RoadEngine.
7. All engines write mesh into context.
8. Export only once at the end.

---

## Current Priority

ATLAS Engine 2.0 foundation.

Goal:

One address.

One context.

One terrain.

One scene.

One export.