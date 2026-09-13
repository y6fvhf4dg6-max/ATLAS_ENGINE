import bpy, sys, numpy as np

sys.path.insert(0,"/Users/Kubi/ATLAS_ENGINE")
from CORE.atlas_pf2_geometric_validator import AtlasPF2GeometricValidator as VLD

P="/Users/Kubi/ATLAS_PF2_PERSISTENT_GEOMETRY/item11_150mm_normalization_2026_09_11/atlas_pf2_item11_female_normalized_150mm_v1.glb"
MASK="/tmp/atlas_pf2_item11_exact_defect_mask.npz"
EPS=1e-9

BODY_END=1767
HEAD_END=338704

def domain(fid):
    if fid < BODY_END: return "BODY"
    if fid < HEAD_END: return "HEAD"
    return "TRANSITION"

pairs=np.asarray(np.load(MASK)["neck_pairs"],dtype=np.int64)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=P)

verts=[]; faces=[]
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
T=V[F]

rows=[]

for ia,ib in pairs:
    a=T[ia]; b=T[ib]
    pts=[]
    pts.extend(VLD._edge_plane_intersection_points(a,b,EPS))
    pts.extend(VLD._edge_plane_intersection_points(b,a,EPS))
    pts=VLD._deduplicate_points(pts,EPS)
    if len(pts)<2:
        continue

    pts=np.asarray(pts,float)
    best=(0.0,None,None)
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            d=float(np.linalg.norm(pts[i]-pts[j]))
            if d>best[0]:
                best=(d,pts[i],pts[j])

    if best[1] is not None:
        mid=0.5*(best[1]+best[2])
        rows.append((best[0],int(ia),int(ib),domain(int(ia)),domain(int(ib)),mid))

rows.sort(key=lambda x:x[0],reverse=True)

print("=== TOP 20 ITEM11 FEMALE NECK CROSSINGS ===")
for n,(L,a,b,da,db,mid) in enumerate(rows[:20],1):
    print(
        f"{n:02d}|LEN_MM={L:.9f}|PAIR={a},{b}|"
        f"DOMAIN={da}__{db}|MID={mid.tolist()}"
    )

print("GEOMETRY_MUTATION=NO")
print("REPO_MUTATION=NO")
