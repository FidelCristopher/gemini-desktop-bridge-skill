"""
08_gable_top_milk_carton.py
---------------------------
Procedural generation recipe for an authentic Gable-Top Milk Carton with an
open pouring spout mechanism, 2K PBR texture baking, and single GLB export.

Key Architectural & Technical Features:
1. Papercraft Gable-Top Folding Geometry:
   - Footprint: 68 mm x 68 mm square base
   - Body Eave Height: 60 mm
   - Roof Ridge Peak: 102 mm
   - Sealed Fin Crest: 114 mm
   - Open Pouring Spout Mechanism (-X gable end):
     * Outward-flaring diamond beak (juts 12.5 mm past sidewall eave)
     * Split top fin ears flaring outward into open pouring chute
     * Authentic unbleached kraft paperboard interior on backfaces
     * Opposite gable end (+X) remains inward-folded and heat-sealed with top fin
2. Paperboard PBR Material:
   - Base Color: 2K composite of printed hand-drawn blue graphics on off-white paperboard
   - Roughness: Matte coated polyethylene paperboard (0.85)
   - Specular IOR Level: 0.20 (low-specular paper finish)
   - Subtle normal creasing along score lines
3. Automated 2K Texture Baking & Single GLB Export:
   - Bakes 2K Base Color (2048x2048), 2K Roughness (2048x2048), and 2K Normal Map (2048x2048)
   - Exports strictly ONE single GLB container: C:\\Users\\Pongo\\Downloads\\carton-milk.glb
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import time
import os

def create_and_export_milk_carton(export_path=r"C:\Users\Pongo\Downloads\carton-milk.glb", resolution=2048):
    # 1. Clean existing scene objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Dimensions (in meters)
    W = 0.068
    D = 0.068
    H_BODY = 0.060
    H_RIDGE = 0.102
    H_FIN = 0.114

    hx = W / 2.0
    hy = D / 2.0

    bm = bmesh.new()

    # Base Vertices
    vb_fl = bm.verts.new((-hx, -hy, 0.0))
    vb_fr = bm.verts.new(( hx, -hy, 0.0))
    vb_br = bm.verts.new(( hx,  hy, 0.0))
    vb_bl = bm.verts.new((-hx,  hy, 0.0))
    bm.faces.new((vb_bl, vb_br, vb_fr, vb_fl))

    # Eaves Vertices
    ve_fl = bm.verts.new((-hx, -hy, H_BODY))
    ve_fr = bm.verts.new(( hx, -hy, H_BODY))
    ve_br = bm.verts.new(( hx,  hy, H_BODY))
    ve_bl = bm.verts.new((-hx,  hy, H_BODY))

    bm.faces.new((vb_fl, vb_fr, ve_fr, ve_fl))
    bm.faces.new((vb_fr, vb_br, ve_br, ve_fr))
    bm.faces.new((vb_br, vb_bl, ve_bl, ve_br))
    bm.faces.new((vb_bl, vb_fl, ve_fl, ve_bl))

    # Sealed Right Half (+X)
    vr_mid = bm.verts.new((0.000, 0.0, H_RIDGE))
    vr_r   = bm.verts.new((hx,    0.0, H_RIDGE))
    vf_mid = bm.verts.new((0.000, 0.0, H_FIN))
    vf_r   = bm.verts.new((hx,    0.0, H_FIN))

    vg_r = bm.verts.new((hx * 0.74, 0.0, H_BODY + (H_RIDGE - H_BODY) * 0.40))
    ve_fm = bm.verts.new((0.000, -hy, H_BODY))
    ve_bm = bm.verts.new((0.000,  hy, H_BODY))

    bm.faces.new((ve_fr, vr_r, vr_mid, ve_fm))
    bm.faces.new((vr_r, ve_br, ve_bm, vr_mid))
    bm.faces.new((vr_mid, vr_r, vf_r, vf_mid))

    bm.faces.new((ve_fr, vg_r, vr_r))
    bm.faces.new((ve_br, vr_r, vg_r))
    bm.faces.new((ve_fr, ve_br, vg_r))

    # Open Pouring Spout Half (-X)
    X_BEAK = -hx - 0.0125
    Z_BEAK = H_BODY + (H_RIDGE - H_BODY) * 0.85
    v_beak = bm.verts.new((X_BEAK, 0.0, Z_BEAK))

    ve_lm = bm.verts.new((-hx, 0.0, H_BODY))
    bm.faces.new((ve_fl, ve_lm, v_beak))
    bm.faces.new((ve_lm, ve_bl, v_beak))

    vf_spout_f = bm.verts.new((-hx * 0.50, -0.012, H_FIN + 0.001))
    v_ear_f    = bm.verts.new((X_BEAK * 0.88, -0.010, H_FIN))
    vf_spout_b = bm.verts.new((-hx * 0.50,  0.012, H_FIN + 0.001))
    v_ear_b    = bm.verts.new((X_BEAK * 0.88,  0.010, H_FIN))

    bm.faces.new((ve_fm, vr_mid, vf_mid, vf_spout_f, ve_fl))
    bm.faces.new((vr_mid, ve_bm, ve_bl, vf_spout_b, vf_mid))
    bm.faces.new((ve_fl, vf_spout_f, v_ear_f, v_beak))
    bm.faces.new((v_beak, v_ear_b, vf_spout_b, ve_bl))

    mesh = bpy.data.meshes.new("MilkCarton_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    carton_obj = bpy.data.objects.new("MilkCarton", mesh)
    bpy.context.collection.objects.link(carton_obj)

    for poly in mesh.polygons:
        poly.use_smooth = True

    solidify = carton_obj.modifiers.new("Solidify", 'SOLIDIFY')
    solidify.thickness = 0.00065
    solidify.offset = -1.0
    solidify.use_even_offset = True

    bevel = carton_obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.00065
    bevel.segments = 2

    # Camera Setup matching drawing angle
    cam_data = bpy.data.cameras.new("CartonCam")
    cam_data.lens = 65.0
    cam_obj = bpy.data.objects.new("CartonCam", cam_data)
    cam_pos = np.array([-0.21, -0.21, 0.17])
    target = np.array([-0.005, -0.005, 0.065])
    forward = (target - cam_pos) / np.linalg.norm(target - cam_pos)
    up = np.array([0, 0, 1])
    right = np.cross(forward, up) / np.linalg.norm(np.cross(forward, up))
    cam_up = np.cross(right, forward)

    mat4 = mathutils.Matrix([
        [right[0], cam_up[0], -forward[0], 0],
        [right[1], cam_up[1], -forward[1], 0],
        [right[2], cam_up[2], -forward[2], 0],
        [0, 0, 0, 1]
    ])
    cam_obj.matrix_world = mat4
    cam_obj.location = tuple(cam_pos)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Studio Lighting
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 8.5
    key_data.size = 0.35
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.20, -0.25, 0.25)
    bpy.context.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 3.5
    fill_data.size = 0.45
    fill_data.color = (0.95, 0.97, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.22, -0.15, 0.20)
    bpy.context.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 6.0
    rim_data.size = 0.30
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.05, 0.22, 0.25)
    bpy.context.collection.objects.link(rim_obj)

    # UV Projection from Camera View
    bpy.context.view_layer.objects.active = carton_obj
    carton_obj.select_set(True)
    uv_proj = carton_obj.data.uv_layers.active
    uv_proj.name = "UVMap_Projected"

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

    # Secondary Atlas UV map for 2K baking
    uv_atlas = carton_obj.data.uv_layers.new(name="UVMap_Atlas")
    carton_obj.data.uv_layers.active = uv_atlas
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Assign Initial Projected Shader
    img_ref = bpy.data.images.load(r'C:\Users\Pongo\Downloads\carton-milk.png')
    mat_init = bpy.data.materials.new("Carton_Init_Mat")
    mat_init.use_nodes = True
    nodes = mat_init.node_tree.nodes
    links = mat_init.node_tree.links
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
    n_bsdf.inputs["Roughness"].default_value = 0.85
    n_bsdf.inputs["Specular IOR Level"].default_value = 0.20
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])

    uv_in = nodes.new('ShaderNodeUVMap')
    uv_in.uv_map = "UVMap_Projected"
    n_tex = nodes.new('ShaderNodeTexImage')
    n_tex.image = img_ref
    links.new(uv_in.outputs["UV"], n_tex.inputs["Vector"])

    n_tc = nodes.new('ShaderNodeTexCoord')
    n_s_xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(n_tc.outputs["Object"], n_s_xyz.inputs["Vector"])

    n_ramp = nodes.new('ShaderNodeValToRGB')
    n_ramp.color_ramp.elements[0].position = 0.022
    n_ramp.color_ramp.elements[0].color = (0.043, 0.365, 0.66, 1.0)
    n_ramp.color_ramp.elements[1].position = 0.026
    n_ramp.color_ramp.elements[1].color = (0.94, 0.935, 0.915, 1.0)
    links.new(n_s_xyz.outputs["Z"], n_ramp.inputs["Fac"])

    _, a_fac, a_bg, a_fg, col_front = make_color_mix()
    links.new(n_tex.outputs["Alpha"], a_fac)
    links.new(n_ramp.outputs["Color"], a_bg)
    links.new(n_tex.outputs["Color"], a_fg)

    n_geom = nodes.new('ShaderNodeNewGeometry')
    _, b_fac, b_fr, b_kr, col_final = make_color_mix()
    b_kr.default_value = (0.86, 0.82, 0.75, 1.0)
    links.new(n_geom.outputs["Backfacing"], b_fac)
    links.new(col_front, b_fr)
    links.new(col_final, n_bsdf.inputs["Base Color"])

    carton_obj.data.materials.append(mat_init)

    # 3. Cycles 2K PBR Baking
    old_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.margin = 16
    uv_atlas.active_render = True

    RES = int(resolution)
    img_basecolor = bpy.data.images.new("Carton_BaseColor", width=RES, height=RES, alpha=False, float_buffer=False)
    img_roughness = bpy.data.images.new("Carton_Roughness", width=RES, height=RES, alpha=False, float_buffer=False)
    img_normal    = bpy.data.images.new("Carton_Normal",    width=RES, height=RES, alpha=False, float_buffer=False)

    tex_bake = nodes.new('ShaderNodeTexImage')
    node_emit = nodes.new('ShaderNodeEmission')

    # Bake Base Color
    tex_bake.image = img_basecolor
    nodes.active = tex_bake
    links.new(col_final, node_emit.inputs["Color"])
    links.new(node_emit.outputs["Emission"], n_out.inputs["Surface"])
    bpy.ops.object.bake(type='EMIT')

    # Bake Roughness
    tex_bake.image = img_roughness
    nodes.active = tex_bake
    node_emit.inputs["Color"].default_value = (0.85, 0.85, 0.85, 1.0)
    bpy.ops.object.bake(type='EMIT')

    # Bake Normal
    tex_bake.image = img_normal
    nodes.active = tex_bake
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.render.bake.normal_space = 'TANGENT'
    bpy.ops.object.bake(type='NORMAL')

    nodes.remove(node_emit)
    nodes.remove(tex_bake)
    bpy.context.scene.render.engine = old_engine

    # 4. Clean PBR Export Material
    mat_exp = bpy.data.materials.new("Carton_Milk_PBR_Export")
    mat_exp.use_nodes = True
    e_nodes = mat_exp.node_tree.nodes
    e_links = mat_exp.node_tree.links
    e_nodes.clear()

    e_out = e_nodes.new('ShaderNodeOutputMaterial')
    e_bsdf = e_nodes.new('ShaderNodeBsdfPrincipled')
    e_bsdf.inputs["Roughness"].default_value = 0.85
    e_bsdf.inputs["Specular IOR Level"].default_value = 0.20
    e_links.new(e_bsdf.outputs["BSDF"], e_out.inputs["Surface"])

    t_col = e_nodes.new('ShaderNodeTexImage')
    t_col.image = img_basecolor
    e_links.new(t_col.outputs["Color"], e_bsdf.inputs["Base Color"])

    t_rgh = e_nodes.new('ShaderNodeTexImage')
    t_rgh.image = img_roughness
    img_roughness.colorspace_settings.name = 'Non-Color'
    e_links.new(t_rgh.outputs["Color"], e_bsdf.inputs["Roughness"])

    t_nrm = e_nodes.new('ShaderNodeTexImage')
    t_nrm.image = img_normal
    img_normal.colorspace_settings.name = 'Non-Color'
    n_map = e_nodes.new('ShaderNodeNormalMap')
    n_map.inputs["Strength"].default_value = 0.10
    e_links.new(t_nrm.outputs["Color"], n_map.inputs["Color"])
    e_links.new(n_map.outputs["Normal"], e_bsdf.inputs["Normal"])

    carton_obj.data.materials.clear()
    carton_obj.data.materials.append(mat_exp)
    carton_obj.data.uv_layers["UVMap_Atlas"].active = True
    carton_obj.data.uv_layers["UVMap_Atlas"].active_render = True

    # 5. Export strictly ONE single GLB
    bpy.ops.object.select_all(action='DESELECT')
    carton_obj.select_set(True)
    bpy.context.view_layer.objects.active = carton_obj

    for l_name in ['KeyLight', 'FillLight', 'RimLight']:
        if l_name in bpy.data.objects:
            bpy.data.objects[l_name].select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=True
    )
    print(f"Exported strictly ONE GLB: {export_path}")

if __name__ == "__main__":
    create_and_export_milk_carton()
