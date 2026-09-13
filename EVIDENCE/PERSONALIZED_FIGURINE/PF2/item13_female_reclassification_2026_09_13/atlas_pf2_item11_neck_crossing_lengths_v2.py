import bpy, sys, numpy as np

sys.path.insert(0,"/Users/Kubi/ATLAS_ENGINE")
from CORE.atlas_pf2_geometric_validator import AtlasPF2GeometricValidator as VLD

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"
MASK="/tmp/atlas_pf2_item11_exact_defect_mask.npz"
EPS=1e-9

pairs=np.asarray(np.load(MASK)["neck_pairs"],dtype=np.int64)

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
T=V[F]

lengths=[]

for ia,ib in pairs:
    a=T[ia]
    b=T[ib]

    pts=[]
    pts.extend(VLD._edge_plane_intersection_points(a,b,EPS))
    pts.extend(VLD._edge_plane_intersection_points(b,a,EPS))
    pts=VLD._deduplicate_points(pts,EPS)

    if len(pts) < 2:
        continue

    pts=np.asarray(pts,dtype=np.float64)

    dmax=0.0
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            dmax=max(
                dmax,
                float(np.linalg.norm(pts[i]-pts[j]))
            )

    if dmax > EPS:
        lengths.append(dmax)

L=np.asarray(lengths,dtype=np.float64)

print("=== ITEM11 FEMALE NECK CROSSING LENGTHS V2 ===")
print(f"NECK_PAIRS={len(pairs)}")
print(f"MEASURED_POSITIVE_LENGTH={len(L)}")

if len(L):
    print(f"LENGTH_MIN_MM={L.min():.9f}")
    print(f"LENGTH_P50_MM={np.percentile(L,50):.9f}")
    print(f"LENGTH_P95_MM={np.percentile(L,95):.9f}")
    print(f"LENGTH_P99_MM={np.percentile(L,99):.9f}")
    print(f"LENGTH_MAX_MM={L.max():.9f}")

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
