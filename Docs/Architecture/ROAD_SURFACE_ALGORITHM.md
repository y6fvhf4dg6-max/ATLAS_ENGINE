# ATLAS ROAD SURFACE ALGORITHM
Version: 0.1
Date: 2026-07-06

---

# Purpose

This document defines the future road surface architecture of ATLAS.

The goal is to generate clean, readable, production-ready recessed roads without grid artifacts, duplicate meshes, or excessive triangle count.

---

# Current Confirmed State

ATLAS currently confirms:

- OSM road data is readable
- Road footprints are generated
- Road polygons are generated
- Road polygon clipping works
- Road polygon triangulation works
- Road surface meshes can be generated
- Base plate and road polygons can be aligned to the same XY coordinate system

Current verified test:

```text
Road polygons : 53
Road surfaces : 53
Triangles     : 336