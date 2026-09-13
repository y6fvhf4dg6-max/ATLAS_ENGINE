import bpy, numpy as np
from collections import defaultdict, deque

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"

TARGET={336977,336979,4334,4337,4333,4340,4338}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=P)

verts=[]
faces=[]

for obj in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
    M=obj.matrix_world
    off=len(verts)
    verts.extend([tuple(M @ v.co) for v in obj.data.vertices])

    for poly in obj.data.polygons:
        ids=list(poly.vertices)
        if len(ids)==3:
            faces.append(tuple(off+i for i in ids))
        elif len(ids)>3:
            a=ids[0]
            for k in range(1,len(ids)-1):
                faces.append((off+a,off+ids[k],off+ids[k+1]))

V=np.asarray(verts,dtype=np.float64)
F=np.asarray(faces,dtype=np.int64)

# Exact-coordinate IDs: duplicate GLB vertices representing the same
# physical point receive the same key.
coord_key=[tuple(x) for x in V]

coord_faces=defaultdict(list)
for fi,f in enumerate(F):
    for vi in f:
        coord_faces[coord_key[vi]].append(fi)

seen=set()

for seed in sorted(TARGET):
    if seed in seen:
        continue

    q=deque([seed])
    comp=set([seed])
    seen.add(seed)

    while q:
        fi=q.popleft()
        for vi in F[fi]:
            for nb in coord_faces[coord_key[vi]]:
                if nb not in comp:
                    comp.add(nb)
                    q.append(nb)

    hit=sorted(TARGET & comp)

    coords=np.unique(V[F[list(comp)].reshape(-1)],axis=0)

    print(
        f"TARGET_HITS={hit}|"
        f"COMPONENT_FACES={len(comp)}|"
        f"COMPONENT_COORDS={len(coords)}|"
        f"BBOX_MIN={coords.min(axis=0).tolist()}|"
        f"BBOX_MAX={coords.max(axis=0).tolist()}"
    )

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
