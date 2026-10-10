"""
12_matcha_natsume_caddy.py
--------------------------
Procedural generation recipe for an authentic Japanese Matcha Tea Canister
(Natsume / Tea Caddy - 棗) containing ceremonial green tea powder.
(C:\\Users\\Pongo\\Downloads\\3d-asset\\matcha-natsume.glb)

Key Architectural & Technical Features:
1. Revolved Tin Canister Geometry with Dual-Material Slots:
   - Outer Body: Mirror-polished shiny chrome/silver aluminum (Metallic 0.98, Roughness 0.07)
   - Inner Wall & Cavity: Satin obsidian black lacquer (Roughness 0.22, Specular 0.60)
   - Body Diameter: 60 mm (radius 30.0 mm), Height: 56 mm
   - Wide-Mouth Collar: 50 mm diameter with rolled rim lip & thread bead
2. Internal Ceremonial Matcha Powder Bed (Matcha_Natsume_Powder):
   - Fluffy undulating tea powder surface at Z = 36 mm (radius 28.7 mm)
   - Gentle natural scoop indentations & fine micro-crevices
   - Velvet absorbent matte PBR (Roughness 0.92, Specular 0.08)
3. Curved Front Label Decal (Natsume_Front_Label):
   - Conforming cylindrical decal panel with clean white paperboard finish
   - Japanese Kanji & 'NATSUME MATCHA' typography
4. Strict Single GLB Container:
   - Output File: C:\\Users\\Pongo\\Downloads\\3d-asset\\matcha-natsume.glb
   - Self-contained container with all 3 mesh nodes and embedded textures.
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import os

def create_and_export_natsume_caddy(export_path=r"C:\Users\Pongo\Downloads\3d-asset\matcha-natsume.glb"):
    # 1. Clean scene
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Revolve Tin Profile
    outer_pts = [
        (0.0, 1.0), (15.0, 1.0), (26.0, 0.6), (29.0, 0.0), (29.8, 0.2), (30.0, 1.2),
        (30.0, 12.0), (30.0, 25.0), (30.0, 36.0), (30.0, 39.0),
        (29.0, 41.5), (27.0, 43.5), (25.5, 44.5),
        (25.5, 49.0), (25.7, 52.0), (25.5, 54.5), (25.3, 55.4), (24.8, 55.8), (24.2, 55.5), (23.8, 54.8),
        (23.8, 48.0), (23.8, 44.0),
        (26.5, 41.5), (28.8, 38.5),
        (28.8, 25.0), (28.8, 12.0), (28.8, 2.2),
        (25.0, 1.8), (12.0, 1.8), (0.0,  1.8),
    ]

    arr = np.array(outer_pts)
    diffs = np.sqrt(np.sum(np.diff(arr, axis=0)**2, axis=1))
    s = np.concatenate(([0], np.cumsum(diffs)))
    s_eval = np.linspace(0, s[-1], 95)
    r_eval = np.interp(s_eval, s, arr[:, 0]) * 0.001
    z_eval = np.interp(s_eval, s, arr[:, 1]) * 0.001
    profile = list(zip(r_eval, z_eval))

    N_PROF = len(profile)
    N_RADIAL = 64

    mesh_tin = bpy.data.meshes.new("Natsume_Tin_Mesh")
    tin_obj = bpy.data.objects.new("Matcha_Natsume_Tin", mesh_tin)
    bpy.context.collection.objects.link(tin_obj)

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

    mesh_tin.from_pydata(verts, [], faces)
    mesh_tin.update(calc_edges=True)
    for poly in mesh_tin.polygons:
        poly.use_smooth = True

    sub = tin_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # Material 0: Shiny Polished Silver
    mat_silver = bpy.data.materials.new("Natsume_Shiny_Silver")
    mat_silver.use_nodes = True
    bsdf_s = mat_silver.node_tree.nodes.get("Principled BSDF")
    bsdf_s.inputs["Base Color"].default_value = (0.94, 0.96, 0.98, 1.0)
    bsdf_s.inputs["Metallic"].default_value = 0.98
    bsdf_s.inputs["Roughness"].default_value = 0.07
    bsdf_s.inputs["Specular IOR Level"].default_value = 0.90

    # Material 1: Glossy Black Interior
    mat_black = bpy.data.materials.new("Natsume_Black_Interior")
    mat_black.use_nodes = True
    bsdf_b = mat_black.node_tree.nodes.get("Principled BSDF")
    bsdf_b.inputs["Base Color"].default_value = (0.015, 0.015, 0.015, 1.0)
    bsdf_b.inputs["Metallic"].default_value = 0.10
    bsdf_b.inputs["Roughness"].default_value = 0.22

    tin_obj.data.materials.append(mat_silver)
    tin_obj.data.materials.append(mat_black)

    # Assign materials based on geometry:
    for p in mesh_tin.polygons:
        cz = sum(mesh_tin.vertices[v].co.z for v in p.vertices) / len(p.vertices)
        cr = sum((mesh_tin.vertices[v].co.x**2 + mesh_tin.vertices[v].co.y**2)**0.5 for v in p.vertices) / len(p.vertices)
        if cz >= 0.042 and cr <= 0.0256:
            p.material_index = 1 # Black inner collar
        elif cz < 0.040 and cr < 0.029:
            p.material_index = 1 # Black inner cavity
        else:
            p.material_index = 0 # Shiny silver exterior

    # 3. Create Powder Bed
    mesh_p = bpy.data.meshes.new("Natsume_Powder_Mesh")
    powder_obj = bpy.data.objects.new("Matcha_Natsume_Powder", mesh_p)
    bpy.context.collection.objects.link(powder_obj)

    bm_p = bmesh.new()
    POWDER_Z = 0.036
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

    v_bot_p = bm_p.verts.new((0, 0, 0.015))
    for th_i in range(N_RADIAL_P):
        next_th = (th_i + 1) % N_RADIAL_P
        bm_p.faces.new((v_bot_p, vert_grid_p[-1][next_th], vert_grid_p[-1][th_i]))

    bmesh.ops.recalc_face_normals(bm_p, faces=bm_p.faces)
    bm_p.to_mesh(mesh_p)
    bm_p.free()
    mesh_p.update()

    for poly in mesh_p.polygons:
        poly.use_smooth = True

    sub_p = powder_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub_p.levels = 1

    powder_obj.parent = tin_obj
    powder_obj.matrix_local = mathutils.Matrix.Identity(4)

    # Powder Material
    mat_pwd = bpy.data.materials.new("Natsume_Powder_Mat")
    mat_pwd.use_nodes = True
    bsdf_p = mat_pwd.node_tree.nodes.get("Principled BSDF")
    bsdf_p.inputs["Base Color"].default_value = (0.024, 0.088, 0.016, 1.0)
    bsdf_p.inputs["Roughness"].default_value = 0.92
    powder_obj.data.materials.append(mat_pwd)

    # 4. Create Curved Front Label Decal
    R_LABEL = 0.03018
    Z_BOT = 0.007
    Z_TOP = 0.035
    N_STEPS = 32
    SPAN_ANGLE = math.radians(130.0)
    CENTER_ANGLE = -math.pi / 2.0
    START_ANGLE = CENTER_ANGLE - SPAN_ANGLE / 2.0

    mesh_label = bpy.data.meshes.new("Natsume_Label_Mesh")
    label_obj = bpy.data.objects.new("Natsume_Front_Label", mesh_label)
    bpy.context.collection.objects.link(label_obj)

    bm_l = bmesh.new()
    bot_v = []
    top_v = []
    for i in range(N_STEPS + 1):
        u = i / N_STEPS
        th = START_ANGLE + u * SPAN_ANGLE
        x = R_LABEL * math.cos(th)
        y = R_LABEL * math.sin(th)
        bot_v.append(bm_l.verts.new((x, y, Z_BOT)))
        top_v.append(bm_l.verts.new((x, y, Z_TOP)))

    for i in range(N_STEPS):
        bm_l.faces.new((bot_v[i], bot_v[i+1], top_v[i+1], top_v[i]))

    U_MIN, U_MAX = 0.22, 0.78
    V_MIN, V_MAX = 0.148, 0.375
    uv_layer = bm_l.loops.layers.uv.new("UVMap")
    for f in bm_l.faces:
        for loop in f.loops:
            th = math.atan2(loop.vert.co.y, loop.vert.co.x)
            u_norm = (th - START_ANGLE) / SPAN_ANGLE
            v_norm = (loop.vert.co.z - Z_BOT) / (Z_TOP - Z_BOT)
            loop[uv_layer].uv = (U_MIN + u_norm * (U_MAX - U_MIN), V_MIN + v_norm * (V_MAX - V_MIN))

    bm_l.to_mesh(mesh_label)
    bm_l.free()
    mesh_label.update()
    for poly in mesh_label.polygons:
        poly.use_smooth = True

    label_obj.parent = tin_obj
    label_obj.matrix_local = mathutils.Matrix.Identity(4)

    # Label Material
    img = bpy.data.images.load(r'C:\Users\Pongo\Downloads\matcha-natsume.png')
    mat_lbl = bpy.data.materials.new("Natsume_Label_Mat")
    mat_lbl.use_nodes = True
    l_nodes = mat_lbl.node_tree.nodes
    l_links = mat_lbl.node_tree.links
    bsdf_l = l_nodes.get("Principled BSDF")
    bsdf_l.inputs["Roughness"].default_value = 0.78
    tex_l = l_nodes.new('ShaderNodeTexImage')
    tex_l.image = img
    l_links.new(tex_l.outputs["Color"], bsdf_l.inputs["Base Color"])
    label_obj.data.materials.append(mat_lbl)

    # Export strictly ONE GLB
    bpy.ops.object.select_all(action='DESELECT')
    tin_obj.select_set(True)
    powder_obj.select_set(True)
    label_obj.select_set(True)
    bpy.context.view_layer.objects.active = tin_obj

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=False
    )
    print(f"Exported Natsume Tea Caddy: {export_path}")

if __name__ == "__main__":
    create_and_export_natsume_caddy()
