"""
11_chawan_matcha_powder_piles_pack.py
------------------------------------
Procedural generation recipe for Phase 2 Interactive Matcha Asset:
All-in-One Katakuchi Chawan with Hidden Multi-Scoop Matcha Powder Piles
(C:\\Users\\Pongo\\Downloads\\3d-asset\\chawan-matcha.glb).

Key Architectural & Technical Features:
1. Hierarchical Multi-Node Architecture (Designed for 2-Scoop Drag & Drop Interaction):
   - Parent Node: 'Katakuchi_Chawan' (Hand-thrown Japanese ceramic tea bowl with pouring spout)
   - Child Node 1: 'Matcha_Chawan_Pile_1' (First scoop mound, radius ~16 mm, height ~8.5 mm)
   - Child Node 2: 'Matcha_Chawan_Pile_2' (Second scoop mound, overlapping organic cluster)
   - Initial State: Both piles have initial scale set to (0.0001, 0.0001, 0.0001) so the bowl starts completely clean/empty!
2. Interactive WebGL / Three.js Implementation:
   - Scoop 1 dropped: tween pile1.scale from (0,0,0) -> (1,1,1)
   - Scoop 2 dropped: tween pile2.scale from (0,0,0) -> (1,1,1)
3. Independent 2K PBR Shaders:
   - Katakuchi_Ceramic: Satin glaze inside, iron spots, toasted rim, matte chocolate terracotta outside (2K PBR).
   - Chawan_Powder: Ceremonial grade velvety matte green powder with micro-granular bump & clump relief (Roughness 0.92, Specular 0.08).
4. 2K Texture Baking & Strict Single GLB Container:
   - 6 embedded 2K PBR bitmap textures:
     * Chawan_BaseColor, Chawan_Roughness, Chawan_Normal
     * Chawan_Powder_BaseColor, Chawan_Powder_Roughness, Chawan_Powder_Normal
   - Strict Single File Export: C:\\Users\\Pongo\\Downloads\\3d-asset\\chawan-matcha.glb.
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import time
import os

def create_and_export_chawan_powder_pack(export_path=r"C:\Users\Pongo\Downloads\3d-asset\chawan-matcha.glb", resolution=2048):
    # 1. Clean scene
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Import Base Chawan
    bpy.ops.import_scene.gltf(filepath=export_path)
    chawan = bpy.data.objects['Katakuchi_Chawan']

    # 3. Create Powder Piles
    FLOOR_Z = 0.0095

    def build_rich_powder_mound(name, center_xy, radius_xy, peak_height, seed=42):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        bm = bmesh.new()
        N_RINGS = 32
        N_RADIAL = 40
        cx, cy = center_xy
        rx, ry = radius_xy
        np.random.seed(seed)
        vert_grid = []

        for r in range(N_RINGS + 1):
            frac_r = r / N_RINGS
            h_profile = peak_height * ((1.0 - frac_r ** 1.3) ** 1.4)
            ring_verts = []
            for th in range(N_RADIAL):
                theta = 2.0 * math.pi * th / N_RADIAL
                perim_noise = 1.0 + 0.12 * math.sin(theta * 3.0 + seed) + 0.06 * math.cos(theta * 5.0 + 1.2)
                cur_r = frac_r * perim_noise
                x = cx + cur_r * rx * math.cos(theta)
                y = cy + cur_r * ry * math.sin(theta)
                clump = 0.14 * math.sin(x * 550.0 + y * 450.0) * math.cos(y * 850.0) if frac_r < 0.85 else 0.0
                clump += 0.06 * math.sin(x * 1200.0) if frac_r < 0.6 else 0.0
                z = FLOOR_Z + h_profile * (1.0 + clump)
                v = bm.verts.new((x, y, z))
                ring_verts.append(v)
            vert_grid.append(ring_verts)

        for r in range(N_RINGS):
            for th in range(N_RADIAL):
                next_th = (th + 1) % N_RADIAL
                bm.faces.new((vert_grid[r][th], vert_grid[r][next_th], vert_grid[r + 1][next_th], vert_grid[r + 1][th]))

        v_bot = bm.verts.new((cx, cy, FLOOR_Z - 0.0002))
        for th in range(N_RADIAL):
            next_th = (th + 1) % N_RADIAL
            bm.faces.new((v_bot, vert_grid[-1][next_th], vert_grid[-1][th]))

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        for poly in mesh.polygons:
            poly.use_smooth = True

        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = 1
        sub.render_levels = 2
        return obj

    pile1 = build_rich_powder_mound("Matcha_Chawan_Pile_1", center_xy=(-0.004, -0.003), radius_xy=(0.0165, 0.0150), peak_height=0.0085, seed=101)
    pile2 = build_rich_powder_mound("Matcha_Chawan_Pile_2", center_xy=(0.006, 0.004), radius_xy=(0.0150, 0.0140), peak_height=0.0078, seed=303)

    pile1.parent = chawan
    pile2.parent = chawan
    pile1.matrix_local = mathutils.Matrix.Identity(4)
    pile2.matrix_local = mathutils.Matrix.Identity(4)

    # 4. Bake 2K PBR Textures
    bpy.ops.object.select_all(action='DESELECT')
    pile1.select_set(True)
    bpy.context.view_layer.objects.active = pile1

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    pile2.select_set(True)
    pile1.select_set(False)
    bpy.context.view_layer.objects.active = pile2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    pile1.select_set(True)
    pile2.select_set(False)
    bpy.context.view_layer.objects.active = pile1

    # Procedural bake material
    mat_p = bpy.data.materials.new("Ceremonial_Matcha_Chawan_Powder")
    mat_p.use_nodes = True
    nodes = mat_p.node_tree.nodes
    links = mat_p.node_tree.links
    nodes.clear()

    def make_color_mix(loc=(0, 0)):
        n = nodes.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        n.location = loc
        fac = [i for i in n.inputs if i.name == 'Factor' and i.type == 'VALUE'][0]
        a = [i for i in n.inputs if i.type == 'RGBA'][0]
        b = [i for i in n.inputs if i.type == 'RGBA'][1]
        res = [o for o in n.outputs if o.type == 'RGBA'][0]
        return n, fac, a, b, res

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

    _, m_fac, m_a, m_b, m_col = make_color_mix()
    m_a.default_value = (0.016, 0.065, 0.010, 1.0)
    m_b.default_value = (0.038, 0.125, 0.024, 1.0)
    links.new(n_noise.outputs["Fac"], m_fac)
    links.new(m_col, n_bsdf.inputs["Base Color"])

    n_bump = nodes.new('ShaderNodeBump')
    n_bump.inputs["Strength"].default_value = 0.08
    n_bump.inputs["Distance"].default_value = 0.0008
    links.new(n_noise.outputs["Fac"], n_bump.inputs["Height"])
    links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])

    pile1.data.materials.append(mat_p)

    old_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.margin = 16

    RES = int(resolution)
    img_col = bpy.data.images.new("Chawan_Powder_BaseColor", width=RES, height=RES, alpha=False, float_buffer=False)
    img_rgh = bpy.data.images.new("Chawan_Powder_Roughness", width=RES, height=RES, alpha=False, float_buffer=False)
    img_nrm = bpy.data.images.new("Chawan_Powder_Normal",    width=RES, height=RES, alpha=False, float_buffer=False)

    tex_bake = nodes.new('ShaderNodeTexImage')
    node_emit = nodes.new('ShaderNodeEmission')

    # Bake Base Color
    tex_bake.image = img_col
    nodes.active = tex_bake
    links.new(m_col, node_emit.inputs["Color"])
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

    # Clean PBR Export Material
    mat_exp = bpy.data.materials.new("Chawan_Powder_PBR_Export")
    mat_exp.use_nodes = True
    p_nodes = mat_exp.node_tree.nodes
    p_links = mat_exp.node_tree.links
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

    pile1.data.materials.clear()
    pile1.data.materials.append(mat_exp)
    pile2.data.materials.clear()
    pile2.data.materials.append(mat_exp)

    # Initial State: Scale = 0 (clean empty bowl)
    pile1.scale = (0.0001, 0.0001, 0.0001)
    pile2.scale = (0.0001, 0.0001, 0.0001)

    # Export GLB Pack
    bpy.ops.object.select_all(action='DESELECT')
    chawan.select_set(True)
    pile1.select_set(True)
    pile2.select_set(True)
    bpy.context.view_layer.objects.active = chawan

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=True
    )
    print(f"Exported Phase 2 Chawan + Matcha Powder Piles Pack: {export_path}")

if __name__ == "__main__":
    create_and_export_chawan_powder_pack()
