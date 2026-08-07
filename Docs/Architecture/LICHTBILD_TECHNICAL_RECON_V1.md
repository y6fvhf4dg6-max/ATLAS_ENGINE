# Lichtbild Technical Recon V1

**Date:** 7 August 2026

## Purpose and boundary

This document records passive black-box observations from publicly visible
Lichtbild product behavior, browser network traffic and public web assets.

ATLAS must not copy Lichtbild implementation details. Findings are used only
to extract general product and software architecture lessons for independent
ATLAS development.

## Verified findings

### Web application and backend

Observed public assets include `_buildManifest.js`, `_ssgManifest.js` and `_app-...js`.

Observed API responses include `Server: Vercel` and `x-matched-path`, with routes such as `/api/createCity`, `/api/previewCacheCheck` and `/api/sendPreview`.

### Selection map

The location-selection interface exposes attribution for Stadia Maps, OpenMapTiles, OpenStreetMap, CNES, Airbus DS, PlanetObserver and Copernicus-derived imagery.

This confirms the selection-map stack only. It does not prove that the same sources are used for final production geometry.

### City preview configuration

`POST /api/createCity` receives a product-state JSON containing center latitude/longitude, size preset, terrain state, color scheme, frame color and building-edit state.

Observed building-edit fields include `markedBuildings`, `customBuildings`, `editedBuildings` and `deletedBuildings`.

### Preview polling and progress

`POST /api/previewCacheCheck` is called repeatedly while preview generation is running.

Observed responses expose backend progress values from `null` through numeric percentages up to `100`.

### Preview persistence and follow-up

`POST /api/sendPreview` receives a recoverable city-model link, a preview screenshot URL and language information.

The city-model link carries serialized configurator state, while the screenshot is served separately through `/api/image?id=...webp`.

## Strong inferences

Preview generation is asynchronous and server-backed rather than a single synchronous browser operation.

Preview reuse appears to depend on normalized product configuration and persistent product state.

## Unknowns

The production building-data source and production elevation/DEM source are not established.

The internal mesh-generation, LoD, slicer and repair implementations are not established.
