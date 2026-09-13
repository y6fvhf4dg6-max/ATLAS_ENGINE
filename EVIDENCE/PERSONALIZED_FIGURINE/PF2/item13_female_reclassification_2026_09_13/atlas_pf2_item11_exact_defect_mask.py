import bpy, sys, numpy as np
from mathutils.bvhtree import BVHTree

sys.path.insert(0,"/Users/Kubi/ATLAS_ENGINE")
from CORE.atlas_pf2_geometric_validator import AtlasPF2GeometricValidator as VLD

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"
EPS=1e-9

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=P)

verts=[]
faces=[]

for obj in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
    M=obj.matrix_world
    offset=len(verts)
    verts.extend([tuple(M @ v.co) for v in obj.data.vertices])

    for poly in obj.data.polygons:
        ids=list(poly.vertices)
        if len(ids)==3:
            faces.append(tuple(offset+i for i in ids))
        elif len(ids)>3:
            a=ids[0]
            for k in range(1,len(ids)-1):
                faces.append((offset+a,offset+ids[k],offset+ids[k+1]))

V=np.asarray(verts,dtype=np.float64)
F=np.asarray(faces,dtype=np.int64)
T=V[F]

bvh=BVHTree.FromPolygons(
    [tuple(x) for x in V],
    [tuple(map(int,f)) for f in F],
    all_triangles=True,
    epsilon=0.0,
)

pairs=set()
for a,b in bvh.overlap(bvh):
    if a==b:
        continue
    if a>b:
        a,b=b,a
    pairs.add((a,b))

defects=[]
for a_id,b_id in pairs:
    a=T[a_id]
    b=T[b_id]

    if VLD._triangles_are_exactly_coincident(a,b,EPS):
        defects.append((a_id,b_id))
        continue

    if VLD._share_full_edge_geometry(a,b,EPS):
        continue

    if VLD._coplanar_state(a,b,EPS):
        if VLD._coplanar_overlap_has_positive_area(a,b,EPS):
            defects.append((a_id,b_id))
        continue

    if VLD._non_coplanar_intersection_has_positive_length(a,b,EPS):
        defects.append((a_id,b_id))

neck=[]
high=[]

for a,b in defects:
    zmax=max(T[a,:,2].max(),T[b,:,2].max())
    (neck if zmax<=105.0 else high).append((a,b))

def unique_coords(pair_list):
    if not pair_list:
        return np.empty((0,3),dtype=np.float64)

    face_ids=sorted({f for p in pair_list for f in p})
    coords=V[F[face_ids].reshape(-1)]
    return np.unique(coords,axis=0)

neck_coords=unique_coords(neck)
high_coords=unique_coords(high)
all_coords=np.unique(
    np.vstack([x for x in (neck_coords,high_coords) if len(x)]),
    axis=0
)

np.savez(
    "/tmp/atlas_pf2_item11_exact_defect_mask.npz",
    defect_pairs=np.asarray(defects,dtype=np.int64),
    neck_pairs=np.asarray(neck,dtype=np.int64),
    high_pairs=np.asarray(high,dtype=np.int64),
    neck_coords=neck_coords,
    high_coords=high_coords,
    all_coords=all_coords,
)

print("=== ITEM11 EXACT DEFECT MASK ===")
print(f"TRIANGLES={len(F)}")
print(f"BVH_CANDIDATES={len(pairs)}")
print(f"TOTAL_DEFECT_PAIRS={len(defects)}")
print(f"NECK_PAIRS_Z_LE_105={len(neck)}")
print(f"HIGH_Z_PAIRS={len(high)}")
print(f"NECK_UNIQUE_COORDS={len(neck_coords)}")
print(f"HIGH_Z_UNIQUE_COORDS={len(high_coords)}")
print(f"ALL_UNIQUE_COORDS={len(all_coords)}")

if len(neck_coords):
    print(f"NECK_BBOX_MIN={neck_coords.min(axis=0).tolist()}")
    print(f"NECK_BBOX_MAX={neck_coords.max(axis=0).tolist()}")

if len(high_coords):
    print(f"HIGH_BBOX_MIN={high_coords.min(axis=0).tolist()}")
    print(f"HIGH_BBOX_MAX={high_coords.max(axis=0).tolist()}")

print("MASK=/tmp/atlas_pf2_item11_exact_defect_mask.npz")
print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
