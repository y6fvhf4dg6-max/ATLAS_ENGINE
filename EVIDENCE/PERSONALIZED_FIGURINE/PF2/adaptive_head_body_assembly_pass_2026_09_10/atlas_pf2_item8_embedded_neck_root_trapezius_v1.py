import bpy, bmesh, os, heapq
import numpy as np
from collections import defaultdict
from mathutils import Vector

CASES=[
 ("MALE","Chibi Base Mesh 3HT (MFT)",os.environ["MALE_HEAD"],0.38,0.6150),
 ("FEMALE","Chibi Base Mesh 3HT (FFT)",os.environ["FEMALE_HEAD"],0.35,0.6135),
]

NECK_WIDTH_RATIO=0.38
TERMINAL_RING_N=24

def boundary_ids_faces(faces):
    cnt=defaultdict(int)
    for f in faces:
        for i,a in enumerate(f):
            b=f[(i+1)%len(f)]
            cnt[tuple(sorted((a,b)))] += 1
    return sorted({v for e,n in cnt.items() if n==1 for v in e})

def angle_order(v,ids):
    ids=np.asarray(ids,int)
    p=v[ids]
    c=p[:,:2].mean(axis=0)
    a=np.arctan2(p[:,1]-c[1],p[:,0]-c[0])
    return ids[np.argsort(a)].tolist()

def bridge(a,b):
    n,m=len(a),len(b)
    out=[]; i=j=0
    while i<n or j<m:
        ni=(i+1)/n if i<n else 1e99
        nj=(j+1)/m if j<m else 1e99
        a0=a[i%n]; b0=b[j%m]
        if ni < nj:
            out.append((a0,a[(i+1)%n],b0)); i+=1
        elif nj < ni:
            out.append((a0,b[(j+1)%m],b0)); j+=1
        else:
            out.append((a0,a[(i+1)%n],b[(j+1)%m]))
            out.append((a0,b[(j+1)%m],b0))
            i+=1; j+=1
    return out

def geodesic(v,faces,seeds):
    adj=[{} for _ in range(len(v))]
    for f in faces:
        for i,a in enumerate(f):
            b=f[(i+1)%len(f)]
            w=float(np.linalg.norm(v[a]-v[b]))
            if b not in adj[a] or w<adj[a][b]:
                adj[a][b]=w; adj[b][a]=w
    d=np.full(len(v),np.inf)
    q=[]
    for s in seeds:
        d[s]=0.; heapq.heappush(q,(0.,s))
    while q:
        du,u=heapq.heappop(q)
        if du!=d[u]: continue
        for z,w in adj[u].items():
            nd=du+w
            if nd<d[z]:
                d[z]=nd
                heapq.heappush(q,(nd,z))
    return d

def import_head(path):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    objs=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    if len(objs)>1: bpy.ops.object.join()
    return bpy.context.object

def resample_closed(points,n):
    p=np.asarray(points,float)
    q=np.vstack([p,p[0]])
    seg=np.linalg.norm(np.diff(q,axis=0),axis=1)
    cum=np.concatenate([[0.],np.cumsum(seg)])
    total=cum[-1]
    ts=np.linspace(0,total,n,endpoint=False)
    out=[]
    for t in ts:
        k=np.searchsorted(cum,t,side="right")-1
        k=min(k,len(p)-1)
        u=(t-cum[k])/max(seg[k],1e-12)
        out.append(q[k]*(1-u)+q[k+1]*u)
    return np.asarray(out)

for label,bname,hpath,ratio,frac in CASES:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # ---- evaluated Dreamloft body ----
    with bpy.data.libraries.load(os.environ["DREAM"],link=False) as (src,dst):
        dst.objects=[bname]
    raw=dst.objects[0]
    bpy.context.collection.objects.link(raw)

    dg=bpy.context.evaluated_depsgraph_get()
    ev=raw.evaluated_get(dg)
    sme=ev.to_mesh()
    body_me=sme.copy()
    ev.to_mesh_clear()
    bpy.data.objects.remove(raw,do_unlink=True)

    bv0=np.array([v.co[:] for v in body_me.vertices],float)
    z0,z1=bv0[:,2].min(),bv0[:,2].max()
    cut=z0+frac*(z1-z0)

    bm=bmesh.new()
    bm.from_mesh(body_me)
    geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
    bmesh.ops.bisect_plane(
        bm,geom=geom,dist=1e-6,
        plane_co=(0,0,float(cut)),
        plane_no=(0,0,1),
        clear_outer=True,clear_inner=False)
    bm.to_mesh(body_me); bm.free(); body_me.update()

    body_v=np.array([v.co[:] for v in body_me.vertices],float)
    body_f=[tuple(p.vertices) for p in body_me.polygons]
    bid=angle_order(body_v,boundary_ids_faces(body_f))
    bp=body_v[bid]
    bc=bp.mean(axis=0)

    # ---- accepted prepared head ----
    head=import_head(hpath)
    head_f=[tuple(p.vertices) for p in head.data.polygons]
    hid0=boundary_ids_faces(head_f)

    hv0=np.array([tuple(head.matrix_world @ v.co) for v in head.data.vertices],float)
    raw_h=np.ptp(hv0[:,2])
    body_h=bc[2]-z0
    target_h=(ratio/(1-ratio))*body_h
    s=target_h/raw_h
    head.scale=(s,s,s)
    bpy.context.view_layer.update()

    hv=np.array([tuple(head.matrix_world @ v.co) for v in head.data.vertices],float)
    hid=angle_order(hv,hid0)
    hc0=hv[hid].mean(axis=0)

    # No explicit neck lift: embed head root at torso opening level.
    head.location += Vector((bc-hc0).tolist())
    bpy.context.view_layer.update()

    head_v=np.array([tuple(head.matrix_world @ v.co) for v in head.data.vertices],float)
    hid=angle_order(head_v,hid)
    hp=head_v[hid]
    hc=hp.mean(axis=0)
    head_height=float(np.ptp(head_v[:,2]))

    # ---- robust lower-face width ----
    lo=hc[2] + 0.12*head_height
    hi=hc[2] + 0.30*head_height
    band=head_v[(head_v[:,2]>=lo)&(head_v[:,2]<=hi)]
    if len(band)<20:
        raise RuntimeError(f"{label}: insufficient lower-face band")
    cx=float(np.median(band[:,0]))
    lower_face_width=2.0*float(np.percentile(np.abs(band[:,0]-cx),90))

    target_w=NECK_WIDTH_RATIO*lower_face_width
    target_d=0.90*target_w

    # ---- local Rodin terminal-neck morph ----
    head_w=float(np.ptp(hp[:,0]))
    head_d=float(np.ptp(hp[:,1]))
    sx=target_w/max(head_w,1e-12)
    sy=target_d/max(head_d,1e-12)

    head_influence=target_w
    gd=geodesic(head_v,head_f,hid)

    morphed=head_v.copy()
    active=np.where(gd<head_influence)[0]

    for i in active:
        t=np.clip(gd[i]/head_influence,0.,1.)
        q=t*t*(3.-2.*t)
        ax=sx+(1.-sx)*q
        ay=sy+(1.-sy)*q
        morphed[i,0]=hc[0]+(head_v[i,0]-hc[0])*ax
        morphed[i,1]=hc[1]+(head_v[i,1]-hc[1])*ay

    protected=np.where(gd>=head_influence)[0]
    protected_delta=(
        float(np.abs(morphed[protected]-head_v[protected]).max())
        if len(protected) else 0.0
    )

    # ---- embedded upper-torso / trapezius adaptation ----
    adapted=body_v.copy()

    body_w=float(np.ptp(bp[:,0]))
    body_d=float(np.ptp(bp[:,1]))
    wx=target_w/max(body_w,1e-12)
    wy=target_d/max(body_d,1e-12)

    # One target-neck width downward influence.
    vertical_span=target_w

    # Shoulder/trapezius lateral influence deliberately wider than neck.
    lateral_span=2.25*target_w
    center=bc.copy()

    local_z=adapted[:,2] >= (cut-vertical_span)

    for i in np.where(local_z)[0]:
        dz=np.clip((cut-body_v[i,2])/max(vertical_span,1e-12),0.,1.)
        vz=dz*dz*(3.-2.*dz)   # 0 at cut, 1 at lower edge

        # Width/depth expansion strongest at neck opening, fades downward.
        ax=wx+(1.-wx)*vz
        ay=wy+(1.-wy)*vz
        adapted[i,0]=center[0]+(body_v[i,0]-center[0])*ax
        adapted[i,1]=center[1]+(body_v[i,1]-center[1])*ay

        # Trapezius lift: strongest near center, fades laterally + downward.
        rx=abs(adapted[i,0]-center[0])/max(lateral_span,1e-12)
        lateral=np.clip(1.-rx,0.,1.)
        lateral=lateral*lateral*(3.-2.*lateral)

        vertical=np.clip(1.-dz,0.,1.)
        vertical=vertical*vertical*(3.-2.*vertical)

        # Raise upper torso toward the embedded head root.
        max_lift=0.42*target_w
        adapted[i,2] += max_lift*lateral*vertical

    body_nonlocal=np.where(~local_z)[0]
    body_nonlocal_delta=(
        float(np.abs(adapted[body_nonlocal]-body_v[body_nonlocal]).max())
        if len(body_nonlocal) else 0.0
    )

    # Exact adapted body boundary and morphed head boundary.
    abp=adapted[bid]
    mhp=morphed[hid]

    # Terminal retopology only. No vertical neck tube.
    body24=resample_closed(abp,TERMINAL_RING_N)
    head24=resample_closed(mhp,TERMINAL_RING_N)

    # Single embedded transition ring centered between both interfaces.
    mid24=0.5*(body24+head24)

    # Keep transition geometrically embedded, not a raised connector.
    mid24[:,2]=0.5*(abp[:,2].mean()+mhp[:,2].mean())

    verts=adapted.tolist()
    head_offset=len(verts)
    verts.extend(morphed.tolist())

    mid_offset=len(verts)
    verts.extend(mid24.tolist())

    faces=[]
    faces.extend(body_f)
    faces.extend(tuple(head_offset+i for i in f) for f in head_f)

    body_loop=bid
    mid_loop=list(range(mid_offset,mid_offset+TERMINAL_RING_N))
    head_loop=[head_offset+i for i in hid]

    faces.extend(bridge(body_loop,mid_loop))
    faces.extend(bridge(mid_loop,head_loop))

    me=bpy.data.meshes.new(f"PF2_{label}_EMBEDDED_NECK_ROOT_V1")
    me.from_pydata(verts,[],faces)
    me.update()

    obj=bpy.data.objects.new(
        f"PF2_{label}_EMBEDDED_NECK_ROOT_TRAPEZIUS_V1",me)
    bpy.context.collection.objects.link(obj)

    out=(
        f"/private/tmp/"
        f"atlas_pf2_item8_{label.lower()}_embedded_neck_root_trapezius_v1.glb"
    )

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format='GLB',
        use_selection=True)

    print(
        f"{label}"
        f"|LOWER_FACE_WIDTH={lower_face_width:.9f}"
        f"|TARGET_NECK_WIDTH={target_w:.9f}"
        f"|TARGET_NECK_WIDTH_RATIO={target_w/lower_face_width:.9f}"
        f"|TARGET_NECK_DEPTH={target_d:.9f}"
        f"|EXPLICIT_NECK_HEIGHT=0"
        f"|BODY_LOOP_N={len(bid)}"
        f"|HEAD_LOOP_N={len(hid)}"
        f"|TERMINAL_RING_N={TERMINAL_RING_N}"
        f"|HEAD_LOCAL_MORPH_VERTICES={len(active)}"
        f"|HEAD_PROTECTED_VERTICES={len(protected)}"
        f"|HEAD_PROTECTED_MAX_DELTA={protected_delta:.12e}"
        f"|BODY_LOCAL_ADAPTED_VERTICES={int(local_z.sum())}"
        f"|BODY_NONLOCAL_MAX_DELTA={body_nonlocal_delta:.12e}"
        f"|OUTPUT={out}"
    )

print("ARCHITECTURE=EMBEDDED_NECK_ROOT_PLUS_LOCAL_TRAPEZIUS_SURFACE")
print("NECK_WIDTH_TARGET_RATIO=0.38")
print("EXPLICIT_NECK_HEIGHT_PARAMETER=NOT_USED")
print("VERTICAL_NECK_CONNECTOR=NOT_USED")
print("OLD_TINY_BODY_OPENING_TARGET=NOT_USED")
print("PARAMETER_SWEEP=NO")
