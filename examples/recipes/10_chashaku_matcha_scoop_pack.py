"""
10_chashaku_matcha_scoop_pack.py
---------------------------------
Procedural generation recipe for Phase 1 Interactive Matcha Asset:
All-in-One Chashaku + Modular Matcha Scoop Heap Pack (C:\\Users\\Pongo\\Downloads\\chashaku.glb).

Key Architectural & Technical Features:
1. Hierarchical Dual-Node Architecture (Designed for Drag & Drop Interaction):
   - Parent Node: 'Bamboo_Chashaku' (Authentic split-culm bamboo spoon with node & kitte butt)
   - Child Node:  'Matcha_Scoop_Heap' (Fluffy ceremonial-grade green powder mound seated in scoop cradle)
   - Interaction Ready: In Three.js / WebGL engines, developer can toggle or animate the child
     powder node (e.g. powder.scale.set(0,0,0) -> powder.scale.set(1,1,1)) when dipping into natsume tea caddy!
2. Independent 2K PBR Shaders:
   - Bamboo_Chashaku: Satin cured honey bamboo with longitudinal vascular fibers & toasted node ring (Roughness 0.36, Specular 0.50).
   - Matcha_Scoop_Heap: Ceremonial grade velvety matte green powder with micro-granular bump & clump undulations (Roughness 0.92, Specular 0.08).
3. 2K Texture Baking & Strict Single GLB Container:
   - 6 embedded 2K PBR bitmap textures:
     * Chashaku_BaseColor, Chashaku_Roughness, Chashaku_Normal
     * Matcha_Heap_BaseColor, Matcha_Heap_Roughness, Matcha_Heap_Normal
   - Strict Single File Export: C:\\Users\\Pongo\\Downloads\\chashaku.glb (7.61 MB).
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import time
import os

def create_and_export_chashaku_matcha_pack(export_path=r"C:\Users\Pongo\Downloads\chashaku.glb", resolution=2048):
    # 1. Clean scene
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Import / Load Base Chashaku
    # Load previously perfected Chashaku GLB
    bpy.ops.import_scene.gltf(filepath=export_path)
    chashaku = bpy.data.objects['Bamboo_Chashaku']

    # 3. Create Matcha Scoop Heap Mesh
    mesh_heap = bpy.data.meshes.new("Matcha_Heap_Mesh")
    heap_obj = bpy.data.objects.new("Matcha_Scoop_Heap", mesh_heap)
    bpy.context.collection.objects.link(heap_obj)

    Y_START = 0.063
    Y_END   = 0.088
    Y_LEN   = Y_END - Y_START
    N_RING = 48
    N_RADIAL = 32

    bm = bmesh.new()
    vert_grid = []

    for r_idx in range(N_RING + 1):
        v_param = r_idx / N_RING
        y = Y_START + v_param * Y_LEN
        ny = -1.0 + 2.0 * v_param
        width_envelope = math.sqrt(max(0.0, 1.0 - ny * ny)) * (1.0 + 0.18 * ny)
        max_rx = 0.0036 * width_envelope
        z_floor = 0.0004 + 0.0056 * (v_param ** 1.35)
        peak_lift = 0.0050 * (math.sin(v_param * math.pi) ** 0.75) * (1.0 + 0.10 * math.sin(v_param * 2 * math.pi))

        ring_verts = []
        for th_idx in range(N_RADIAL):
            theta = 2.0 * math.pi * th_idx / N_RADIAL
            sin_th = math.sin(theta)
            cos_th = math.cos(theta)
            x = max_rx * sin_th

            if cos_th >= 0:
                clump_1 = 0.12 * math.sin(x * 900.0 + y * 650.0) * math.cos(y * 1200.0)
                clump_2 = 0.06 * math.cos(x * 1600.0 - y * 1400.0)
                crest_pinch = (cos_th ** 0.70) * (1.0 - 0.20 * abs(sin_th))
                z = z_floor + peak_lift * crest_pinch * (1.0 + clump_1 + clump_2)
            else:
                z_curve = 0.0010 * ((x / (max_rx + 1e-6)) ** 2)
                z = z_floor + (0.0002 * cos_th) + z_curve

            v = bm.verts.new((x, y, z))
            ring_verts.append(v)
        vert_grid.append(ring_verts)

    for r_idx in range(N_RING):
        for th_idx in range(N_RADIAL):
            next_th = (th_idx + 1) % N_RADIAL
            v0 = vert_grid[r_idx][th_idx]
            v1 = vert_grid[r_idx][next_th]
            v2 = vert_grid[r_idx + 1][next_th]
            v3 = vert_grid[r_idx + 1][th_idx]
            bm.faces.new((v0, v1, v2, v3))

    v_rear_center = bm.verts.new((0.0, Y_START - 0.0003, 0.0004))
    for th_idx in range(N_RADIAL):
        next_th = (th_idx + 1) % N_RADIAL
        bm.faces.new((v_rear_center, vert_grid[0][th_idx], vert_grid[0][next_th]))

    v_front_center = bm.verts.new((0.0, Y_END + 0.0003, 0.0068))
    for th_idx in range(N_RADIAL):
        next_th = (th_idx + 1) % N_RADIAL
        bm.faces.new((v_front_center, vert_grid[-1][next_th], vert_grid[-1][th_idx]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_heap)
    bm.free()
    mesh_heap.update()

    for poly in mesh_heap.polygons:
        poly.use_smooth = True

    subsurf = heap_obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2

    # Parent to Chashaku
    heap_obj.parent = chashaku
    heap_obj.matrix_local = mathutils.Matrix.Identity(4)

    # 4. Bake 2K PBR Textures for Heap
    bpy.ops.object.select_all(action='DESELECT')
    heap_obj.select_set(True)
    bpy.context.view_layer.objects.active = heap_obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Assign procedural bake shader
    mat_matcha = bpy.data.materials.new("Ceremonial_Matcha_Powder")
    mat_matcha.use_nodes = True
    nodes = mat_matcha.node_tree.nodes
    links = mat_matcha.node_tree.links
    nodes.clear()

    n_out = nodes.new('ShaderNodeOutputMaterial')
    n_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    n_bsdf.inputs["Roughness"].default_value = 0.92
    n_bsdf.inputs["Specular IOR Level"].default_value = 0.08
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])

    n_tc = nodes.new('ShaderNodeTexCoord')
    n_noise = nodes.new('ShaderNodeTexNoise')
    n_noise.inputs["Scale"].default_value = 280.0
    n_noise.inputs["Detail"].default_value = 8.0
    links.new(n_tc.outputs["Object"], n_noise.inputs["Vector"])

    n_mix = nodes.new('ShaderNodeMix')
    n_mix.data_type = 'RGBA'
    n_mix.inputs[6].default_value = (0.016, 0.065, 0.010, 1.0)
    n_mix.inputs[7].default_value = (0.038, 0.125, 0.024, 1.0)
    links.new(n_noise.outputs["Fac"], n_mix.inputs[0])
    links.new(n_mix.outputs[2], n_bsdf.inputs["Base Color"])

    n_bump = nodes.new('ShaderNodeBump')
    n_bump.inputs["Strength"].default_value = 0.08
    n_bump.inputs["Distance"].default_value = 0.0008
    links.new(n_noise.outputs["Fac"], n_bump.inputs["Height"])
    links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])
    heap_obj.data.materials.append(mat_matcha)

    old_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.margin = 16

    RES = int(resolution)
    img_col = bpy.data.images.new("Matcha_Heap_BaseColor", width=RES, height=RES, alpha=False, float_buffer=False)
    img_rgh = bpy.data.images.new("Matcha_Heap_Roughness", width=RES, height=RES, alpha=False, float_buffer=False)
    img_nrm = bpy.data.images.new("Matcha_Heap_Normal",    width=RES, height=RES, alpha=False, float_buffer=False)

    tex_bake = nodes.new('ShaderNodeTexImage')
    node_emit = nodes.new('ShaderNodeEmission')

    # Bake Base Color
    tex_bake.image = img_col
    nodes.active = tex_bake
    links.new(n_mix.outputs[2], node_emit.inputs["Color"])
    links.new(node_emit.outputs["Emission"], n_out.inputs["Surface"])
    bpy.ops.object.bake(type='EMIT')

    # Bake Roughness
    tex_bake.image = img_rgh
    nodes.active = tex_bake
    node_emit.inputs["Color"].default_value = (0.92, 0.92, 0.92, 1.0)
    bpy.ops.object.bake(type='EMIT')

    # Bake Normal
    tex_bake.image = img_nrm
    nodes.active = tex_bake
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.render.bake.normal_space = 'TANGENT'
    bpy.ops.object.bake(type='NORMAL')

    nodes.remove(node_emit)
    nodes.remove(tex_bake)
    bpy.context.scene.render.engine = old_engine

    # Final Export Material for Heap
    mat_pbr = bpy.data.materials.new("Matcha_Heap_PBR_Export")
    mat_pbr.use_nodes = True
    p_nodes = mat_pbr.node_tree.nodes
    p_links = mat_pbr.node_tree.links
    p_nodes.clear()

    po_out = p_nodes.new('ShaderNodeOutputMaterial')
    po_bsdf = p_nodes.new('ShaderNodeBsdfPrincipled')
    po_bsdf.inputs["Roughness"].default_value = 0.92
    po_bsdf.inputs["Specular IOR Level"].default_value = 0.08
    p_links.new(po_bsdf.outputs["BSDF"], po_out.inputs["Surface"])

    t_col = p_nodes.new('ShaderNodeTexImage')
    t_col.image = img_col
    p_links.new(t_col.outputs["Color"], po_bsdf.inputs["Base Color"])

    t_rgh = p_nodes.new('ShaderNodeTexImage')
    t_rgh.image = img_rgh
    img_rgh.colorspace_settings.name = 'Non-Color'
    p_links.new(t_rgh.outputs["Color"], po_bsdf.inputs["Roughness"])

    t_nrm = p_nodes.new('ShaderNodeTexImage')
    t_nrm.image = img_nrm
    img_nrm.colorspace_settings.name = 'Non-Color'
    n_map = p_nodes.new('ShaderNodeNormalMap')
    n_map.inputs["Strength"].default_value = 0.65
    p_links.new(t_nrm.outputs["Color"], n_map.inputs["Color"])
    p_links.new(n_map.outputs["Normal"], po_bsdf.inputs["Normal"])

    heap_obj.data.materials.clear()
    heap_obj.data.materials.append(mat_pbr)

    # 5. Export strictly ONE GLB Pack
    bpy.ops.object.select_all(action='DESELECT')
    chashaku.select_set(True)
    heap_obj.select_set(True)
    bpy.context.view_layer.objects.active = chashaku

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=True
    )
    print(f"Exported Phase 1 Chashaku + Matcha Pack: {export_path}")

if __name__ == "__main__":
    create_and_export_chashaku_matcha_pack()
