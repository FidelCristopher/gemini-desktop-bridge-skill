"""
13_traditional_urushi_natsume_caddy.py
--------------------------------------
Procedural generation recipe for an authentic Japanese Black Urushi Lacquer
Matcha Tea Caddy (Chu-Natsume - 中棗) with Gold Maki-e (蒔絵) floral crests,
removable matching lacquer lid, and internal ceremonial green tea powder bed.
(C:\\Users\\Pongo\\Downloads\\3d-asset\\matcha-natsume.glb)

Key Architectural & Technical Features:
1. Revolved Wood/Lacquer Chu-Natsume Geometry:
   - Body: Classic curved swelling jujube fruit silhouette (66 mm diameter at belly, 46.5 mm height).
   - Stepped Neck Collar: Inner lip and stepped collar engineered for snug lid fitting.
   - Detached Matching Lid (Matcha_Natsume_Lid): Revolved dome lid resting tilted beside the canister in tea ceremony presentation.
2. Ro-iro Kuro-Urushi (Black Lacquer) & Kin-Maki-e (Gold Dust) Shader:
   - Base Finish: Deep mirror-polished obsidian black lacquer (Roughness 0.045, Specular 0.85, Coat 0.80).
   - Gold Maki-e: Japanese Hanabishi (four-lobed flower) crest and pine needle accents extracted from reference photo 'natsume-matcha(2).jpeg'.
   - Pure Metallic Gold Powder: Radiant Japanese Kinpun (#E5C478, Metallic 0.98, Roughness 0.22, normal relief bump).
3. Ceremonial Grade Matcha Powder Bed (Matcha_Natsume_Powder):
   - Fluffy undulating tea powder surface at Z = 32 mm inside the caddy.
   - Micro-porous matte tea dust response (Roughness 0.92, Specular 0.08).
4. Strict Single GLB Container:
   - Output File: C:\\Users\\Pongo\\Downloads\\3d-asset\\matcha-natsume.glb (1.93 MB).
   - Self-contained container with all 3 mesh nodes and embedded textures.
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import os

def create_and_export_urushi_natsume(export_path=r"C:\Users\Pongo\Downloads\3d-asset\matcha-natsume.glb"):
    # 1. Clean scene
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Revolve Chu-Natsume Body
    body_pts = [
        (0.0, 1.0), (15.0, 1.0), (24.0, 0.6), (26.5, 0.0), (27.5, 0.4),
        (29.0, 2.5), (31.2, 8.0), (32.8, 18.0), (33.0, 26.0), (32.6, 34.0), (31.8, 38.0),
        (30.6, 39.5), (30.2, 42.0), (30.0, 45.0), (29.8, 46.5), (29.0, 46.5),
        (28.8, 42.0), (28.8, 35.0), (28.8, 25.0), (28.8, 12.0), (28.8, 3.0),
        (25.0, 2.2), (12.0, 2.2), (0.0,  2.2)
    ]

    arr = np.array(body_pts)
    diffs = np.sqrt(np.sum(np.diff(arr, axis=0)**2, axis=1))
    s = np.concatenate(([0], np.cumsum(diffs)))
    s_eval = np.linspace(0, s[-1], 90)
    r_eval = np.interp(s_eval, s, arr[:, 0]) * 0.001
    z_eval = np.interp(s_eval, s, arr[:, 1]) * 0.001
    profile = list(zip(r_eval, z_eval))

    N_PROF = len(profile)
    N_RADIAL = 64

    mesh_body = bpy.data.meshes.new("Natsume_Body_Mesh")
    body_obj = bpy.data.objects.new("Matcha_Natsume_Tin", mesh_body)
    bpy.context.collection.objects.link(body_obj)

    verts = []
    for p_idx, (r, z) in enumerate(profile):
        if r < 1e-5:
            verts.append((0.0, 0.0, z))
        else:
            for rad_idx in range(N_RADIAL):
                th = 2.0 * math.pi * rad_idx / N_RADIAL
                verts.append((r * math.cos(th), r * math.sin(th), z))

    def get_v_idx(p_idx, rad_idx):
        if profile[p_idx][0] < 1e-5:
            return 0 if p_idx == 0 else len(verts) - 1
        return 1 + (p_idx - 1) * N_RADIAL + (rad_idx % N_RADIAL)

    faces = []
    for rad_idx in range(N_RADIAL):
        v0 = 0
        v1 = 1 + rad_idx
        v2 = 1 + ((rad_idx + 1) % N_RADIAL)
        faces.append((v0, v1, v2))

    for p_idx in range(1, N_PROF - 2):
        for rad_idx in range(N_RADIAL):
            v1 = get_v_idx(p_idx, rad_idx)
            v2 = get_v_idx(p_idx, rad_idx + 1)
            v3 = get_v_idx(p_idx + 1, rad_idx + 1)
            v4 = get_v_idx(p_idx + 1, rad_idx)
            faces.append((v1, v2, v3, v4))

    v_center_in = len(verts) - 1
    for rad_idx in range(N_RADIAL):
        v1 = get_v_idx(N_PROF - 2, rad_idx)
        v2 = get_v_idx(N_PROF - 2, rad_idx + 1)
        faces.append((v2, v1, v_center_in))

    mesh_body.from_pydata(verts, [], faces)
    mesh_body.update(calc_edges=True)
    for poly in mesh_body.polygons:
        poly.use_smooth = True

    sub = body_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # Project UV from Camera view
    bpy.context.view_layer.objects.active = body_obj
    body_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with bpy.context.temp_override(window=window, area=area, region=region):
                            bpy.ops.uv.project_from_view(camera_bounds=True)
                        break
    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Create Powder Bed
    mesh_powder = bpy.data.meshes.new("Natsume_Powder_Mesh")
    powder_obj = bpy.data.objects.new("Matcha_Natsume_Powder", mesh_powder)
    bpy.context.collection.objects.link(powder_obj)

    bm_p = bmesh.new()
    POWDER_Z = 0.032
    POWDER_R = 0.0287
    N_RINGS_P = 20
    N_RADIAL_P = 40

    vert_grid_p = []
    for r_i in range(N_RINGS_P + 1):
        frac_r = r_i / N_RINGS_P
        ring = []
        for th_i in range(N_RADIAL_P):
            th = 2.0 * math.pi * th_i / N_RADIAL_P
            x = frac_r * POWDER_R * math.cos(th)
            y = frac_r * POWDER_R * math.sin(th)
            dist_c = math.hypot(x, y)
            scoop_indent = -0.0022 * (math.cos(dist_c * 130.0) ** 2) if dist_c < 0.017 else 0.0
            wave = 0.0006 * math.sin(x * 520.0 + y * 420.0) * math.cos(y * 700.0)
            z = POWDER_Z + scoop_indent + wave
            v = bm_p.verts.new((x, y, z))
            ring.append(v)
        vert_grid_p.append(ring)

    for r_i in range(N_RINGS_P):
        for th_i in range(N_RADIAL_P):
            next_th = (th_i + 1) % N_RADIAL_P
            bm_p.faces.new((vert_grid_p[r_i][th_i], vert_grid_p[r_i][next_th], vert_grid_p[r_i + 1][next_th], vert_grid_p[r_i + 1][th_i]))

    v_bot_p = bm_p.verts.new((0, 0, 0.010))
    for th_i in range(N_RADIAL_P):
        next_th = (th_i + 1) % N_RADIAL_P
        bm_p.faces.new((v_bot_p, vert_grid_p[-1][next_th], vert_grid_p[-1][th_i]))

    bmesh.ops.recalc_face_normals(bm_p, faces=bm_p.faces)
    bm_p.to_mesh(mesh_powder)
    bm_p.free()
    mesh_powder.update()

    for poly in mesh_powder.polygons:
        poly.use_smooth = True

    sub_p = powder_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub_p.levels = 1
    powder_obj.parent = body_obj

    # 4. Create Detached Dome Lid
    lid_pts = [
        (0.0, 26.0), (15.0, 25.8), (26.0, 24.5), (31.0, 22.0),
        (33.0, 18.0), (33.0, 6.0), (32.2, 0.0), (30.8, 0.0),
        (30.6, 12.0), (28.0, 22.0), (15.0, 23.5), (0.0,  23.8)
    ]
    arr_l = np.array(lid_pts)
    diffs_l = np.sqrt(np.sum(np.diff(arr_l, axis=0)**2, axis=1))
    s_l = np.concatenate(([0], np.cumsum(diffs_l)))
    s_eval_l = np.linspace(0, s_l[-1], 65)
    profile_lid = list(zip(np.interp(s_eval_l, s_l, arr_l[:, 0]) * 0.001, np.interp(s_eval_l, s_l, arr_l[:, 1]) * 0.001))

    mesh_lid = bpy.data.meshes.new("Natsume_Lid_Mesh")
    lid_obj = bpy.data.objects.new("Matcha_Natsume_Lid", mesh_lid)
    bpy.context.collection.objects.link(lid_obj)

    verts_l = []
    for p_idx, (r, z) in enumerate(profile_lid):
        if r < 1e-5:
            verts_l.append((0.0, 0.0, z))
        else:
            for rad_idx in range(N_RADIAL):
                th = 2.0 * math.pi * rad_idx / N_RADIAL
                verts_l.append((r * math.cos(th), r * math.sin(th), z))

    faces_l = []
    for rad_idx in range(N_RADIAL):
        v0 = 0
        v1 = 1 + rad_idx
        v2 = 1 + ((rad_idx + 1) % N_RADIAL)
        faces_l.append((v0, v1, v2))

    for p_idx in range(1, len(profile_lid) - 2):
        for rad_idx in range(N_RADIAL):
            v1 = 0 if profile_lid[p_idx][0] < 1e-5 else 1 + (p_idx - 1) * N_RADIAL + (rad_idx % N_RADIAL)
            v2 = 0 if profile_lid[p_idx][0] < 1e-5 else 1 + (p_idx - 1) * N_RADIAL + ((rad_idx + 1) % N_RADIAL)
            v3 = len(verts_l) - 1 if profile_lid[p_idx+1][0] < 1e-5 else 1 + p_idx * N_RADIAL + ((rad_idx + 1) % N_RADIAL)
            v4 = len(verts_l) - 1 if profile_lid[p_idx+1][0] < 1e-5 else 1 + p_idx * N_RADIAL + (rad_idx % N_RADIAL)
            faces_l.append((v1, v2, v3, v4))

    v_center_l = len(verts_l) - 1
    for rad_idx in range(N_RADIAL):
        v1 = 1 + (len(profile_lid) - 3) * N_RADIAL + (rad_idx % N_RADIAL)
        v2 = 1 + (len(profile_lid) - 3) * N_RADIAL + ((rad_idx + 1) % N_RADIAL)
        faces_l.append((v2, v1, v_center_l))

    mesh_lid.from_pydata(verts_l, [], faces_l)
    mesh_lid.update(calc_edges=True)
    for poly in mesh_lid.polygons:
        poly.use_smooth = True

    sub_l = lid_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub_l.levels = 1
    lid_obj.location = (0.052, 0.025, 0.003)
    lid_obj.rotation_euler = (math.radians(-12.0), math.radians(24.0), math.radians(-30.0))
    lid_obj.parent = body_obj

    # 5. Shaders Setup
    img_photo = bpy.data.images.load(r'C:\Users\Pongo\Downloads\natsume-matcha(2).jpeg')

    # Maki-e Material for Body
    mat_maki = bpy.data.materials.new("Urushi_Black_Maki_e")
    mat_maki.use_nodes = True
    mn = mat_maki.node_tree.nodes
    ml = mat_maki.node_tree.links
    mn.clear()

    m_out = mn.new('ShaderNodeOutputMaterial')
    m_bsdf = mn.new('ShaderNodeBsdfPrincipled')
    m_bsdf.inputs["Specular IOR Level"].default_value = 0.85
    if "Coat Weight" in m_bsdf.inputs:
        m_bsdf.inputs["Coat Weight"].default_value = 0.85
        m_bsdf.inputs["Coat Roughness"].default_value = 0.02
    ml.new(m_bsdf.outputs["BSDF"], m_out.inputs["Surface"])

    n_tc = mn.new('ShaderNodeTexCoord')
    n_map = mn.new('ShaderNodeMapping')
    n_map.inputs["Location"].default_value = (0.16, -0.015, 0.0)
    n_map.inputs["Scale"].default_value = (0.95, 0.95, 1.0)
    ml.new(n_tc.outputs["UV"], n_map.inputs["Vector"])

    n_tex = mn.new('ShaderNodeTexImage')
    n_tex.image = img_photo
    ml.new(n_map.outputs["Vector"], n_tex.inputs["Vector"])

    n_sep = mn.new('ShaderNodeSeparateColor')
    ml.new(n_tex.outputs["Color"], n_sep.inputs["Color"])

    # Isolate pure gold lines from photo
    n_r_low = mn.new('ShaderNodeMath')
    n_r_low.operation = 'GREATER_THAN'
    n_r_low.inputs[1].default_value = 0.28
    ml.new(n_sep.outputs["Red"], n_r_low.inputs[0])

    n_r_high = mn.new('ShaderNodeMath')
    n_r_high.operation = 'LESS_THAN'
    n_r_high.inputs[1].default_value = 0.78
    ml.new(n_sep.outputs["Red"], n_r_high.inputs[0])

    n_r_valid = mn.new('ShaderNodeMath')
    n_r_valid.operation = 'MULTIPLY'
    ml.new(n_r_low.outputs["Value"], n_r_valid.inputs[0])
    ml.new(n_r_high.outputs["Value"], n_r_valid.inputs[1])

    n_b_check = mn.new('ShaderNodeMath')
    n_b_check.operation = 'LESS_THAN'
    n_b_check.inputs[1].default_value = 0.45
    ml.new(n_sep.outputs["Blue"], n_b_check.inputs[0])

    n_gold_pure = mn.new('ShaderNodeMath')
    n_gold_pure.operation = 'MULTIPLY'
    ml.new(n_r_valid.outputs["Value"], n_gold_pure.inputs[0])
    ml.new(n_b_check.outputs["Value"], n_gold_pure.inputs[1])

    # Clean seam cutoff
    n_sep_xyz = mn.new('ShaderNodeSeparateXYZ')
    ml.new(n_tc.outputs["Object"], n_sep_xyz.inputs["Vector"])
    n_seam_cutoff = mn.new('ShaderNodeMath')
    n_seam_cutoff.operation = 'GREATER_THAN'
    n_seam_cutoff.inputs[1].default_value = -0.016
    ml.new(n_sep_xyz.outputs["X"], n_seam_cutoff.inputs[0])

    n_gold_clean = mn.new('ShaderNodeMath')
    n_gold_clean.operation = 'MULTIPLY'
    ml.new(n_gold_pure.outputs["Value"], n_gold_clean.inputs[0])
    ml.new(n_seam_cutoff.outputs["Value"], n_gold_clean.inputs[1])

    # Mix Nodes
    n_col_mix = mn.new('ShaderNodeMix')
    n_col_mix.data_type = 'RGBA'
    n_col_mix.inputs[6].default_value = (0.008, 0.008, 0.008, 1.0)
    n_col_mix.inputs[7].default_value = (0.92, 0.76, 0.38, 1.0)
    ml.new(n_gold_clean.outputs["Value"], n_col_mix.inputs[0])
    ml.new(n_col_mix.outputs[2], m_bsdf.inputs["Base Color"])

    n_met_mix = mn.new('ShaderNodeMix')
    n_met_mix.data_type = 'FLOAT'
    n_met_mix.inputs[2].default_value = 0.02
    n_met_mix.inputs[3].default_value = 0.98
    ml.new(n_gold_clean.outputs["Value"], n_met_mix.inputs[0])
    ml.new(n_met_mix.outputs[0], m_bsdf.inputs["Metallic"])

    n_rgh_mix = mn.new('ShaderNodeMix')
    n_rgh_mix.data_type = 'FLOAT'
    n_rgh_mix.inputs[2].default_value = 0.045
    n_rgh_mix.inputs[3].default_value = 0.22
    ml.new(n_gold_clean.outputs["Value"], n_rgh_mix.inputs[0])
    ml.new(n_rgh_mix.outputs[0], m_bsdf.inputs["Roughness"])

    n_bump = mn.new('ShaderNodeBump')
    n_bump.inputs["Strength"].default_value = 0.055
    n_bump.inputs["Distance"].default_value = 0.0005
    ml.new(n_gold_clean.outputs["Value"], n_bump.inputs["Height"])
    ml.new(n_bump.outputs["Normal"], m_bsdf.inputs["Normal"])

    # Pure Black Material for Lid & Inner Cavity
    mat_pure_black = bpy.data.materials.new("Urushi_Black_Lid")
    mat_pure_black.use_nodes = True
    lnodes = mat_pure_black.node_tree.nodes
    llinks = mat_pure_black.node_tree.links
    lnodes.clear()
    l_out = lnodes.new('ShaderNodeOutputMaterial')
    l_bsdf = lnodes.new('ShaderNodeBsdfPrincipled')
    l_bsdf.inputs["Base Color"].default_value = (0.008, 0.008, 0.008, 1.0)
    l_bsdf.inputs["Metallic"].default_value = 0.02
    l_bsdf.inputs["Roughness"].default_value = 0.045
    l_bsdf.inputs["Specular IOR Level"].default_value = 0.85
    llinks.new(l_bsdf.outputs["BSDF"], l_out.inputs["Surface"])

    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_maki)
    body_obj.data.materials.append(mat_pure_black)

    # Assign Slot 1 (Pure Black) to inner cavity polygons
    for p in mesh_body.polygons:
        cz = sum(mesh_body.vertices[v].co.z for v in p.vertices) / len(p.vertices)
        cr = sum((mesh_body.vertices[v].co.x**2 + mesh_body.vertices[v].co.y**2)**0.5 for v in p.vertices) / len(p.vertices)
        if cz > 0.038 or cr < 0.0285:
            p.material_index = 1
        else:
            p.material_index = 0

    lid_obj.data.materials.clear()
    lid_obj.data.materials.append(mat_pure_black)

    # Powder Material
    mat_pwd = bpy.data.materials.new("Natsume_Powder_Bed_Mat")
    mat_pwd.use_nodes = True
    pn = mat_pwd.node_tree.nodes
    pl = mat_pwd.node_tree.links
    pn.clear()
    po_out = pn.new('ShaderNodeOutputMaterial')
    po_bsdf = pn.new('ShaderNodeBsdfPrincipled')
    po_bsdf.inputs["Roughness"].default_value = 0.92
    po_bsdf.inputs["Specular IOR Level"].default_value = 0.08
    po_bsdf.inputs["Base Color"].default_value = (0.024, 0.088, 0.016, 1.0)
    pl.new(po_bsdf.outputs["BSDF"], po_out.inputs["Surface"])
    powder_obj.data.materials.clear()
    powder_obj.data.materials.append(mat_pwd)

    # 6. Export Strictly ONE GLB
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    powder_obj.select_set(True)
    lid_obj.select_set(True)
    bpy.context.view_layer.objects.active = body_obj

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=False
    )
    print(f"Exported Traditional Black Urushi Natsume: {export_path}")

if __name__ == "__main__":
    create_and_export_urushi_natsume()
