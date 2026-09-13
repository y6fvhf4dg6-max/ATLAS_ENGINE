import bpy, numpy as np
from collections import defaultdict, deque

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"

PAIRS=[
    (4334,4337),
    (4333,4337),
    (4337,4340),
    (4338,4340),
]

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

V=np.asarray(verts,float)
F=np.asarray(faces,np.int64)

keys=[[tuple(V[v]) for v in F[f]] for f in range(len(F))]

coord_faces=defaultdict(set)
for fi in {x for p in PAIRS for x in p}:
    for k in keys[fi]:
        coord_faces[k].add(fi)

# Add only immediate neighbors of target faces.
targets={x for p in PAIRS for x in p}
neighbor_faces=set(targets)

for fi in list(targets):
    for k in keys[fi]:
        for fj,f in enumerate(F):
            pass

# Efficient global exact-coordinate ownership once.
coord_faces=defaultdict(list)
for fi,f in enumerate(F):
    for vi in f:
        coord_faces[tuple(V[vi])].append(fi)

def neighbors(fi):
    out=set()
    for vi in F[fi]:
        out.update(coord_faces[tuple(V[vi])])
    out.discard(fi)
    return out

def graph_distance(a,b,max_depth=3):
    if a==b: return 0
    seen={a}
    q=deque([(a,0)])
    while q:
        x,d=q.popleft()
        if d>=max_depth:
            continue
        for y in neighbors(x):
            if y==b:
                return d+1
            if y not in seen:
                seen.add(y)
                q.append((y,d+1))
    return None

print("=== HIGH-Z MAIN-SURFACE LOCAL TOPOLOGY ===")

for a,b in PAIRS:
    sa=set(keys[a]); sb=set(keys[b])
    shared=len(sa & sb)
    dist=graph_distance(a,b,3)
    print(
        f"PAIR={a},{b}|"
        f"SHARED_EXACT_COORDS={shared}|"
        f"FACE_GRAPH_DISTANCE_LE3={dist if dist is not None else 'GT3'}"
    )

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
