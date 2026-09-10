# PF-2 Item 8 — Adaptive Head/Body Assembly PASS

Date: 2026-09-10

## Decision

PF-2 Item 8 `Adaptive head/body assembly` is PASS / CLOSED.

Human visual gate:
- Male: PASS
- Female: PASS

Accepted architecture:

`EMBEDDED_NECK_ROOT_PLUS_LOCAL_TRAPEZIUS_SURFACE`

## Locked geometry contract

- Male Dreamloft body: 3HT MFT
- Female Dreamloft body: 3HT FFT
- Male accepted Rodin identity/head ratio: 0.38
- Female accepted Rodin identity/head ratio: 0.35
- Neck width target: 0.38 × robust lower-face width
- Explicit vertical neck-height parameter: NOT USED
- Vertical neck connector: NOT USED
- Tiny-body-opening target strategy: REJECTED
- Direct 249/324 → 10 head/body stitch strategy: REJECTED
- Local upper torso / trapezius adaptation: ACCEPTED
- Identity-bearing head region outside local lower-neck influence: unchanged
- Body outside local upper-torso influence: unchanged
- Parameter sweep: NO

## Accepted build metrics

Male:
- lower-face width: 0.581262726
- target neck width: 0.220879836
- target neck width ratio: 0.380000000
- target neck depth: 0.198791852
- explicit neck height: 0
- body loop: 10
- head loop: 249
- terminal transition ring: 24
- protected head max delta: 0
- body non-local max delta: 0

Female:
- lower-face width: 0.485909449
- target neck width: 0.184645591
- target neck width ratio: 0.380000000
- target neck depth: 0.166181032
- explicit neck height: 0
- body loop: 10
- head loop: 324
- terminal transition ring: 24
- protected head max delta: 0
- body non-local max delta: 0

## Accepted temporary assembly hashes

Male GLB:
`9b9156456438fb237fad626a7309a91595a5d0f76608f914dab779fd9fa3e3d6`

Female GLB:
`3325680137fc67248876c197444c1e525370e77812a9ad82ce14ec1e4e9656d3`

The GLB assemblies are intentionally NOT persisted in the repository because they contain modified Dreamloft third-party geometry. The repository persists ATLAS-owned procedure, provenance, hashes, and visual decision evidence only.

## Evidence hashes

Assembly script:
`5a36e7b42ccfb7088743f95ee9d72c7b07c1b4900db6d2553118c9007a87eacc`

Male 4-view human-gate sheet:
`21d7997cf856cc22367dcb6bce6e8a9aa6c1e69cab293e02209450154175f07a`

Female 4-view human-gate sheet:
`f1fdbeba68eab149ab2e7fa43986071df6eec44e7a9954340d1db9d1f7e5647a`

## Visual conclusion

The accepted candidate removes the previously rejected long/thin neck, coplanar collar, fan-stitch, and explicit vertical neck-tube failure modes. The head root reads as embedded into a locally adapted short/wide neck and upper trapezius surface for both male and female candidates.

Later PF-2 topology, geometric, printability, physical-print, and slicer gates remain independent and NOT STARTED by this closure.
