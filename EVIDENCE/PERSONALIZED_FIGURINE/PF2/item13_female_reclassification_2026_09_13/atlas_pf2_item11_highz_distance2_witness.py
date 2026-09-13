import bpy, numpy as np
from collections import defaultdict

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"

PAIRS=[
    (4334,4337),
    (4333,4337),
    (4337,4340),
]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=P)

V=[]
F=[]

for obj in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
    M=obj.matrix_world
    off=len(V)
    V.extend([tuple(M @ v.co) for v in obj.data.vertices])

    for poly in obj.data.polygons:
        ids=list(poly.vertices)
        if len(ids)==3:
            F.append(tuple(off+i for i in ids))
        elif len(ids)>3:
            a=ids[0]
            for k in range(1,len(ids)-1):
                F.append((off+a,off+ids[k],off+ids[k+1]))

V=np.asarray(V,float)
F=np.asarray(F,np.int64)

coord_faces=defaultdict(set)
for fi,f in enumerate(F):
    for vi in f:
        coord_faces[tuple(V[vi])].add(fi)

def neighbors(fi):
    out=set()
    for vi in F[fi]:
        out.update(coord_faces[tuple(V[vi])])
    out.discard(fi)
    return out

for a,b in PAIRS:
    na=neighbors(a)
    nb=neighbors(b)
    common=sorted(na & nb)

    print(
        f"PAIR={a},{b}|"
        f"COMMON_INTERMEDIATE_COUNT={len(common)}|"
        f"COMMON_INTERMEDIATE_FACES={common[:20]}"
    )

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
