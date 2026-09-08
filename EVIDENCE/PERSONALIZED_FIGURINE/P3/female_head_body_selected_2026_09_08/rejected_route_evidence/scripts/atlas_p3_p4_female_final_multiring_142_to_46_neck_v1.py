from pathlib import Path
from collections import defaultdict
import hashlib, math
import numpy as np
import trimesh

HEAD = Path("/private/tmp/atlas_p3_p4_zero_deformation_female_head_for_dp_v1.glb")
BODY = Path("/private/tmp/atlas_p3_p4_zero_deformation_female_body_for_dp_v1.glb")
OUT  = Path("/private/tmp/atlas_p3_p4_female_final_multiring_142_to_46_single_body_v1.glb")
CONTRACT_NPZ = Path("/private/tmp/atlas_p3_p4_female_head_underside_ring2_preservation_contract_v1.npz")
COLLAR_NPZ = Path("/private/tmp/atlas_p3_p4_female_vertical_neck_collar_y5280_contract_v1.npz")

HEAD_TX = 0.0
HEAD_TY = 0.0
HEAD_TZ = 0.0
INTERFACE_Y = 5.148177623749
TOL = 1e-6
ZERO = 1e-12

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def uedge(a,b):
    return tuple(sorted((int(a),int(b))))

def dedges(t):
    a,b,c=map(int,t)
    return [(a,b),(b,c),(c,a)]

def incidence(faces):
    d=defaultdict(list)
    for fi,t in enumerate(faces):
        for a,b in dedges(t):
            d[uedge(a,b)].append((fi,a,b))
    return d

def boundary_map(faces):
    return {e:o[0] for e,o in incidence(faces).items() if len(o)==1}

def ordered_cycle(bmap, allowed=None):
    items=bmap.items() if allowed is None else [(e,x) for e,x in bmap.items() if e in allowed]
    nxt={}
    for e,(_,a,b) in items:
        if a in nxt and nxt[a]!=b:
            raise RuntimeError(f"BOUNDARY_DIRECTION_CONFLICT_{a}")
        nxt[a]=b
    if not nxt:
        raise RuntimeError("EMPTY_BOUNDARY")
    start=min(nxt); out=[start]; cur=start
    while True:
        if cur not in nxt:
            raise RuntimeError("BROKEN_BOUNDARY")
        n=nxt[cur]
        if n==start: break
        if n in out: raise RuntimeError("PREMATURE_CYCLE")
        out.append(n); cur=n
    if len(out)!=len(nxt):
        raise RuntimeError(f"NOT_SINGLE_CYCLE_{len(out)}_{len(nxt)}")
    return np.asarray(out,dtype=np.int64)

def normal(v,t):
    p=v[np.asarray(t,dtype=np.int64)]
    return np.cross(p[1]-p[0],p[2]-p[0])

def unit(x):
    n=float(np.linalg.norm(x))
    return None if n<=1e-15 else x/n

def area(v,t):
    return .5*float(np.linalg.norm(normal(v,t)))

def compact(v,t):
    p=v[np.asarray(t,dtype=np.int64)]
    l2=(np.sum((p[1]-p[0])**2)+np.sum((p[2]-p[1])**2)+np.sum((p[0]-p[2])**2))
    a=area(v,t)
    return float("inf") if a<=ZERO else float(l2/(4*math.sqrt(3)*a))

def dih(n0,n1):
    a,b=unit(n0),unit(n1)
    if a is None or b is None: return float("inf")
    return math.degrees(math.acos(float(np.clip(np.dot(a,b),-1,1))))

def better(a,b):
    if b is None: return True
    if a[0] < b[0]-1e-12: return True
    if abs(a[0]-b[0])<=1e-12:
        if a[1] < b[1]-1e-12: return True
        if abs(a[1]-b[1])<=1e-12 and a[2] < b[2]-1e-12: return True
    return False

head=trimesh.load(HEAD,force="mesh",process=False)
body=trimesh.load(BODY,force="mesh",process=False)

hv=np.asarray(head.vertices,dtype=np.float64).copy()
hf=np.asarray(head.faces,dtype=np.int64).copy()
bv=np.asarray(body.vertices,dtype=np.float64).copy()
bf=np.asarray(body.faces,dtype=np.int64).copy()

hv[:,0]+=HEAD_TX
hv[:,1]+=HEAD_TY
hv[:,2]+=HEAD_TZ

# Contract-locked removal of head underside rings 0..2
with np.load(CONTRACT_NPZ) as contract:
    removed_head_face_ids=np.asarray(contract["removed_face_ids"],dtype=np.int64)
    expected_retained_face_ids=np.asarray(contract["retained_face_ids"],dtype=np.int64)
    expected_frontier_edges=np.asarray(contract["frontier_edges"],dtype=np.int64)

if len(removed_head_face_ids)!=810:
    raise RuntimeError(f"HEAD_REMOVED_FACE_CONTRACT_{len(removed_head_face_ids)}")

head_keep=np.ones(len(hf),dtype=bool)
head_keep[removed_head_face_ids]=False
hret=hf[head_keep]
actual_retained_face_ids=np.flatnonzero(head_keep).astype(np.int64)
if not np.array_equal(actual_retained_face_ids,expected_retained_face_ids):
    raise RuntimeError("HEAD_RETAINED_FACE_IDS_CONTRACT_FAIL")

hb=boundary_map(hret)
hl=ordered_cycle(hb)
if len(hl)!=142:
    raise RuntimeError(f"HEAD_FRONTIER_LOOP_{len(hl)}")
if set(hb)!=set(map(tuple,expected_frontier_edges.tolist())):
    raise RuntimeError("HEAD_FRONTIER_EDGE_CONTRACT_FAIL")


# Contract-bounded body rings 0..3; ring 4 and below remain exactly fixed.
bb0=boundary_map(bf)
bplane={e for e in bb0 if abs(bv[e[0],1]-INTERFACE_Y)<=TOL and abs(bv[e[1],1]-INTERFACE_Y)<=TOL}
body_ring0=ordered_cycle(bb0,bplane)
if len(body_ring0)!=96:
    raise RuntimeError(f"BODY_RING0_{len(body_ring0)}")

adj=[set() for _ in range(len(bv))]
for tri in bf:
    a,b,c=map(int,tri)
    adj[a].update((b,c)); adj[b].update((a,c)); adj[c].update((a,b))

rings=[set(map(int,body_ring0))]
seen=set(rings[0])
for _ in range(3):
    nxt=set()
    for x in rings[-1]:
        nxt.update(adj[x])
    nxt-=seen
    rings.append(nxt)
    seen.update(nxt)

if [len(x) for x in rings] != [96,48,48,46]:
    raise RuntimeError(f"BODY_RING_COUNTS_{[len(x) for x in rings]}")

body_domain=set().union(*rings)
removed_body_face_ids=np.asarray(
    [fi for fi,t in enumerate(bf) if all(int(x) in body_domain for x in t)],
    dtype=np.int64
)
if len(removed_body_face_ids)!=334:
    raise RuntimeError(f"BODY_REMOVED_FACES_{len(removed_body_face_ids)}")

body_keep=np.ones(len(bf),dtype=bool)
body_keep[removed_body_face_ids]=False
bret=bf[body_keep]
bb=boundary_map(bret)
bl=ordered_cycle(bb)
if len(bl)!=46 or len(bb)!=46:
    raise RuntimeError(f"BODY_FIXED_FRONTIER_{len(bl)}_{len(bb)}")

def reverse_cycle(x):
    return np.concatenate((x[:1],x[:0:-1]))

def resample_closed(points,count):
    p=np.asarray(points,dtype=np.float64)
    q=np.vstack([p,p[:1]])
    seg=np.linalg.norm(np.diff(q,axis=0),axis=1)
    total=float(seg.sum())
    if total<=ZERO:
        raise RuntimeError("ZERO_LOOP_LENGTH")
    cumulative=np.concatenate([[0.0],np.cumsum(seg)])
    samples=np.arange(count,dtype=np.float64)*total/count
    out=[]
    k=0
    for s in samples:
        while k+1<len(cumulative)-1 and cumulative[k+1]<=s:
            k+=1
        u=(s-cumulative[k])/seg[k] if seg[k]>ZERO else 0.0
        out.append(q[k]*(1.0-u)+q[k+1]*u)
    return np.asarray(out,dtype=np.float64)

# Select the spatially closest cyclic correspondence once, then keep it for every layer.
best_match=None
for hd,H in enumerate((hl.copy(),reverse_cycle(hl))):
    hp=hv[H]
    for bd,B in enumerate((bl.copy(),reverse_cycle(bl))):
        sampled=resample_closed(bv[B],len(H))
        for shift in range(len(H)):
            candidate=np.roll(sampled,-shift,axis=0)
            cost=float(np.mean(np.sum((candidate-hp)**2,axis=1)))
            key=(cost,hd,bd,shift)
            if best_match is None or key<best_match[0]:
                best_match=(key,H.copy(),B.copy(),candidate.copy())

(match_score,head_direction,body_direction,body_shift),H,B,body_sampled=best_match
head_positions=hv[H]
layer_t=np.asarray([0.16,0.34,0.52,0.70,0.86],dtype=np.float64)
layer_positions=[]
for t in layer_t:
    s=t*t*(3.0-2.0*t)
    layer_positions.append(body_sampled*(1.0-s)+head_positions*s)

BODY_OFF=len(hv)
NEW_OFF=BODY_OFF+len(bv)
layer_ids=[]
cursor=NEW_OFF
for positions in layer_positions:
    ids=np.arange(cursor,cursor+len(positions),dtype=np.int64)
    layer_ids.append(ids)
    cursor+=len(positions)

V=np.vstack([hv,bv]+layer_positions)
head_faces=hret.copy()
body_faces=bret+BODY_OFF
body_fixed_ids=B+BODY_OFF

def tri_compact(ids):
    return compact(V,tuple(map(int,ids)))

def unequal_stitch(lower,upper):
    lower=np.asarray(lower,dtype=np.int64)
    upper=np.asarray(upper,dtype=np.int64)
    M,N=len(lower),len(upper)
    cost=np.full((M+1,N+1),np.inf)
    prev=np.full((M+1,N+1),-1,dtype=np.int8)
    cost[0,0]=0.0
    for i in range(M+1):
        for j in range(N+1):
            if not np.isfinite(cost[i,j]):
                continue
            if i<M:
                tri=(lower[i%M],lower[(i+1)%M],upper[j%N])
                value=cost[i,j]+tri_compact(tri)
                if value<cost[i+1,j]:
                    cost[i+1,j]=value; prev[i+1,j]=1
            if j<N:
                tri=(upper[j%N],upper[(j+1)%N],lower[i%M])
                value=cost[i,j]+tri_compact(tri)
                if value<cost[i,j+1]:
                    cost[i,j+1]=value; prev[i,j+1]=2
    moves=[]
    i,j=M,N
    while i or j:
        move=int(prev[i,j])
        if move==1:
            moves.append(1); i-=1
        elif move==2:
            moves.append(2); j-=1
        else:
            raise RuntimeError(f"STITCH_BACKTRACE_{i}_{j}")
    moves.reverse()
    faces=[]
    i=j=0
    for move in moves:
        if move==1:
            faces.append((lower[i%M],lower[(i+1)%M],upper[j%N])); i+=1
        else:
            faces.append((upper[j%N],upper[(j+1)%N],lower[i%M])); j+=1
    return faces,float(cost[M,N])

new_faces=[]
base_faces,base_cost=unequal_stitch(body_fixed_ids,layer_ids[0])
new_faces.extend(base_faces)

for lower,upper in zip(layer_ids[:-1],layer_ids[1:]):
    for i in range(len(lower)):
        j=(i+1)%len(lower)
        new_faces.append((int(lower[i]),int(lower[j]),int(upper[j])))
        new_faces.append((int(lower[i]),int(upper[j]),int(upper[i])))

for i in range(len(layer_ids[-1])):
    j=(i+1)%len(layer_ids[-1])
    new_faces.append((int(layer_ids[-1][i]),int(layer_ids[-1][j]),int(H[j])))
    new_faces.append((int(layer_ids[-1][i]),int(H[j]),int(H[i])))

new_faces=np.asarray(new_faces,dtype=np.int64)
expected_new_faces=(46+142)+4*(2*142)+(2*142)
if len(new_faces)!=expected_new_faces:
    raise RuntimeError(f"NEW_FACE_COUNT_{len(new_faces)}_{expected_new_faces}")

# Orient only new faces. Retained head/body face ordering is never changed.
retained_faces=np.vstack([head_faces,body_faces])
retained_inc=incidence(retained_faces)

def directed_edges(t):
    a,b,c=map(int,t)
    return ((a,b),(b,c),(c,a))

new_occ={}
for fi,t in enumerate(new_faces):
    for a,b in directed_edges(t):
        new_occ.setdefault(uedge(a,b),[]).append((fi,a,b))

flip=[None]*len(new_faces)
queue=[]
for e,occ in new_occ.items():
    if e not in retained_inc:
        continue
    if len(occ)!=1 or len(retained_inc[e])!=1:
        raise RuntimeError("SEAM_INCIDENCE_PREORIENT_FAIL")
    fi,a,b=occ[0]
    _,ra,rb=retained_inc[e][0]
    required=(a==ra and b==rb)
    if flip[fi] is not None and flip[fi]!=required:
        raise RuntimeError("ORIENTATION_SEED_CONFLICT")
    flip[fi]=required
    queue.append(fi)

face_neighbors=[[] for _ in range(len(new_faces))]
for e,occ in new_occ.items():
    if len(occ)==2:
        (f0,a0,b0),(f1,a1,b1)=occ
        same=(a0==a1 and b0==b1)
        face_neighbors[f0].append((f1,same))
        face_neighbors[f1].append((f0,same))
    elif len(occ)>2:
        raise RuntimeError("NEW_NONMANIFOLD_PREORIENT")

from collections import deque
q=deque(queue)
while q:
    fi=q.popleft()
    for fj,xor_value in face_neighbors[fi]:
        required=bool(flip[fi]) ^ bool(xor_value)
        if flip[fj] is None:
            flip[fj]=required; q.append(fj)
        elif flip[fj]!=required:
            raise RuntimeError("ORIENTATION_PROPAGATION_CONFLICT")

for start in range(len(new_faces)):
    if flip[start] is not None:
        continue
    flip[start]=False
    q=deque([start])
    while q:
        fi=q.popleft()
        for fj,xor_value in face_neighbors[fi]:
            required=bool(flip[fi]) ^ bool(xor_value)
            if flip[fj] is None:
                flip[fj]=required; q.append(fj)
            elif flip[fj]!=required:
                raise RuntimeError("ORIENTATION_COMPONENT_CONFLICT")

for fi,do_flip in enumerate(flip):
    if do_flip:
        new_faces[fi,[1,2]]=new_faces[fi,[2,1]]

faces=np.vstack([head_faces,body_faces,new_faces])
candidate=trimesh.Trimesh(vertices=V.copy(),faces=faces.copy(),process=False)
final_inc=incidence(faces)
boundary=sum(len(x)==1 for x in final_inc.values())
nonmanifold=sum(len(x)>2 for x in final_inc.values())
new_areas=np.asarray([area(V,t) for t in new_faces])
all_areas=np.asarray([area(V,t) for t in faces])
degenerate=int(np.sum(all_areas<=ZERO))

gate=(
    boundary==0 and nonmanifold==0 and degenerate==0
    and candidate.is_watertight and candidate.is_winding_consistent
    and len(bl)==46 and len(hl)==142
)
if not gate:
    print("=== FINAL MULTI-RING NUMERICAL GATE ===")
    print(f"BOUNDARY_EDGES={boundary}")
    print(f"NONMANIFOLD_EDGES={nonmanifold}")
    print(f"DEGENERATE_FACES={degenerate}")
    print(f"IS_WATERTIGHT={candidate.is_watertight}")
    print(f"IS_WINDING_CONSISTENT={candidate.is_winding_consistent}")
    print("FINAL_CANDIDATE_EXPORTED=NO")
    raise SystemExit(7)

candidate.export(OUT)

print("=== ACTIVE CHECKLIST: P-3/P-4 — FEMALE FINAL MULTI-RING ASSEMBLY ===")
print("FINAL_ALLOWED_ROUTE=ONE_CONTROLLED_UPPER_NECK_RECONSTRUCTION")
print("ARCHITECTURE=FIVE_GRADUAL_MATCHED_RINGS_142_TO_46")
print("ATTEMPT_BUDGET_CONSUMED=YES")
print()
print("=== LOCKED INPUT DOMAINS ===")
print(f"HEAD_RETAINED_FRONTIER_VERTICES={len(hl)}")
print(f"REMOVED_HEAD_UNDERSIDE_FACES={len(removed_head_face_ids)}")
print(f"BODY_RECONSTRUCTION_DOMAIN_VERTICES={len(body_domain)}")
print(f"REMOVED_BODY_UPPER_NECK_FACES={len(removed_body_face_ids)}")
print(f"BODY_FIXED_FRONTIER_VERTICES={len(bl)}")
print("FIRST_FIXED_BODY_RING=4")
print()
print("=== MULTI-RING CONSTRUCTION ===")
print(f"INTERMEDIATE_RING_COUNT={len(layer_ids)}")
print(f"VERTICES_PER_INTERMEDIATE_RING={len(layer_ids[0])}")
print(f"NEW_VERTICES={sum(len(x) for x in layer_ids)}")
print(f"NEW_FACES={len(new_faces)}")
print(f"BASE_UNEQUAL_STITCH_FACES={len(base_faces)}")
print(f"MATCH_HEAD_DIRECTION={head_direction}")
print(f"MATCH_BODY_DIRECTION={body_direction}")
print(f"MATCH_BODY_RESAMPLED_SHIFT={body_shift}")
print(f"MATCH_MEAN_SQUARED_DISTANCE={match_score:.12e}")
print(f"BASE_STITCH_COMPACTNESS_TOTAL={base_cost:.12f}")
print()
print("=== QUALITY ===")
print(f"NEW_FACE_AREA_MIN={new_areas.min():.12e}")
print(f"NEW_FACE_AREA_P05={np.percentile(new_areas,5):.12e}")
print(f"NEW_FACE_AREA_MEDIAN={np.median(new_areas):.12e}")
print(f"NEW_FACE_AREA_MAX={new_areas.max():.12e}")
print()
print("=== FINAL TOPOLOGY ===")
print(f"VERTICES={len(candidate.vertices)}")
print(f"FACES={len(candidate.faces)}")
print(f"BOUNDARY_EDGES={boundary}")
print(f"NONMANIFOLD_EDGES={nonmanifold}")
print(f"DEGENERATE_FACES={degenerate}")
print(f"IS_WATERTIGHT={candidate.is_watertight}")
print(f"IS_WINDING_CONSISTENT={candidate.is_winding_consistent}")
print(f"EULER_NUMBER={candidate.euler_number}")
print()
print("HEAD_VISIBLE_VERTEX_DISPLACEMENT=ZERO")
print("BODY_RING4_PLUS_VERTEX_DISPLACEMENT=ZERO")
print("ARM_SHOULDER_TORSO_VERTEX_DISPLACEMENT=ZERO")
print("FINAL_MULTI_RING_NUMERICAL_GATE=PASS")
print(f"OUTPUT={OUT}")
print(f"OUTPUT_SHA256={sha(OUT)}")
print("HUMAN_VISUAL_GATE=PENDING")
print("PRODUCTION_GEOMETRY_AUTHORIZATION=NO")
print("NEXT=INDEPENDENT_PRESERVATION_CHECK_THEN_ONE_FINAL_VISUAL_DECISION")
