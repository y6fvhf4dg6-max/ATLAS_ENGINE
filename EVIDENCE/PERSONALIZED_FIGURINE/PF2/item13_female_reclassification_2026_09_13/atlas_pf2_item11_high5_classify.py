import bpy, sys, numpy as np

sys.path.insert(0,"/Users/Kubi/ATLAS_ENGINE")
from CORE.atlas_pf2_geometric_validator import AtlasPF2GeometricValidator as VLD

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"
D=np.load("/tmp/atlas_pf2_item11_exact_defect_mask.npz")
pairs=np.asarray(D["high_pairs"],dtype=np.int64)
EPS=1e-9

BODY_END=1767
HEAD_END=338704

def domain(i):
    if i < BODY_END: return "BODY"
    if i < HEAD_END: return "HEAD"
    return "TRANSITION"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=P)

verts=[]; faces=[]
for o in [x for x in bpy.context.scene.objects if x.type=="MESH"]:
    off=len(verts); M=o.matrix_world
    verts.extend([tuple(M@v.co) for v in o.data.vertices])
    for p in o.data.polygons:
        ids=list(p.vertices)
        if len(ids)==3:
            faces.append(tuple(off+i for i in ids))
        elif len(ids)>3:
            a=ids[0]
            for k in range(1,len(ids)-1):
                faces.append((off+a,off+ids[k],off+ids[k+1]))

V=np.asarray(verts,float)
F=np.asarray(faces,np.int64)
T=V[F]

print("=== ITEM11 HIGH-Z 5 PAIRS ===")

for n,(ia,ib) in enumerate(pairs,1):
    a=T[ia]; b=T[ib]
    pts=[]
    pts += VLD._edge_plane_intersection_points(a,b,EPS)
    pts += VLD._edge_plane_intersection_points(b,a,EPS)
    pts=VLD._deduplicate_points(pts,EPS)

    L=0.0
    if len(pts)>=2:
        q=np.asarray(pts,float)
        for i in range(len(q)):
            for j in range(i+1,len(q)):
                L=max(L,float(np.linalg.norm(q[i]-q[j])))

    xyz=np.vstack((a,b))
    print(
        f"{n}|PAIR={ia},{ib}|DOMAIN={domain(int(ia))}__{domain(int(ib))}|"
        f"LEN_MM={L:.9f}|"
        f"BBOX_MIN={xyz.min(axis=0).tolist()}|"
        f"BBOX_MAX={xyz.max(axis=0).tolist()}"
    )

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
