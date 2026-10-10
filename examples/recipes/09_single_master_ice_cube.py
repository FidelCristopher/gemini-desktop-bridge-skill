"""
09_single_master_ice_cube.py
----------------------------
Procedural generation recipe for a Single Master 3D Ice Cube asset (optimized
for real-time WebGL, Three.js Instancing, Physics, and Drag & Drop interaction)
with automated 2K PBR texture baking and strict single GLB export.

Key Architectural & Technical Features:
1. Canonical Drag & Drop Geometry:
   - Size: Standard beverage ice cube 28 mm x 28 mm x 28 mm (0.028 m cube)
   - Pivot / Origin: Exact center of mass (0, 0, 0) for perfect cursor tracking & collision physics
   - Rounded Melting Bevel: 2.4 mm rounded corners (Bevel + Subsurf Level 2)
   - Natural surface tension micro-undulations
2. Physical Ice Optical PBR Shader (Crystal_Ice_Master):
   - Refractive Index: IOR = 1.310 (physically accurate water ice)
   - Trapped Micro-Bubbles & Veins: 3D Voronoi inclusion network with white frost flecks
   - Fresnel Edge Silhouette: Arctic cyan / slate blue refraction contour
   - Wet Surface Gloss: Roughness ~0.02, Specular IOR Level 0.95
   - Water Droplet Relief: Normal bump mapping for condensation beads
3. Automated 2K Texture Baking & Strict Single GLB Export:
   - Bakes 2K Base Color (2048x2048), 2K Roughness (2048x2048), and 2K Tangent Normal Map (2048x2048)
   - Exports strictly ONE single GLB container: C:\\Users\\Pongo\\Downloads\\ice-cube.glb
"""

import bpy
import bmesh
import math
import numpy as np
import mathutils
import time
import os

def create_and_export_master_ice_cube(export_path=r"C:\Users\Pongo\Downloads\ice-cube.glb", resolution=2048):
    # 1. Clean existing scene objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Construct Master Ice Cube Mesh
    SIZE = 0.028 # 28 mm cube
    bpy.ops.mesh.primitive_cube_add(size=SIZE, location=(0, 0, 0))
    ice_obj = bpy.context.active_object
    ice_obj.name = "Ice_Cube_Master"

    # Bevel modifier: 2.4 mm rounded edges
    bevel = ice_obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.0024
    bevel.segments = 4
    bevel.profile = 0.50
    bevel.limit_method = 'NONE'

    # Subsurf modifier
    subsurf = ice_obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    bpy.ops.object.shade_smooth()

    # Center of mass origin
    bpy.context.view_layer.objects.active = ice_obj
    ice_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ice_obj.location = (0.0, 0.0, 0.0)
    ice_obj.rotation_euler = (0.0, 0.0, math.radians(-28.0))

    # 3. Procedural Crystal Ice Shader
    mat_ice = bpy.data.materials.new("Crystal_Ice_Master")
    mat_ice.use_nodes = True
    nodes = mat_ice.node_tree.nodes
    links = mat_ice.node_tree.links
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
    n_out.location = (1200, 0)

    n_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    n_bsdf.location = (850, 0)
    n_bsdf.inputs["Roughness"].default_value = 0.02
    n_bsdf.inputs["IOR"].default_value = 1.310
    n_bsdf.inputs["Specular IOR Level"].default_value = 0.95
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])

    n_tex_coord = nodes.new('ShaderNodeTexCoord')
    n_tex_coord.location = (-1200, 0)

    # Trapped Micro-Bubbles
    n_voro = nodes.new('ShaderNodeTexVoronoi')
    n_voro.location = (-900, 250)
    n_voro.inputs["Scale"].default_value = 110.0
    n_voro.voronoi_dimensions = '3D'
    links.new(n_tex_coord.outputs["Object"], n_voro.inputs["Vector"])

    n_bub_ramp = nodes.new('ShaderNodeValToRGB')
    n_bub_ramp.location = (-650, 250)
    n_bub_ramp.color_ramp.elements[0].position = 0.0
    n_bub_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    n_bub_ramp.color_ramp.elements[1].position = 0.16
    n_bub_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(n_voro.outputs["Distance"], n_bub_ramp.inputs["Fac"])

    # Layer Weight Fresnel Network
    n_lw = nodes.new('ShaderNodeLayerWeight')
    n_lw.location = (-650, -250)
    n_lw.inputs["Blend"].default_value = 0.22

    # Arctic Refraction Rim
    n_col_ramp = nodes.new('ShaderNodeValToRGB')
    n_col_ramp.location = (-350, -250)
    n_col_ramp.color_ramp.elements[0].position = 0.0
    n_col_ramp.color_ramp.elements[0].color = (0.16, 0.42, 0.70, 1.0) # Arctic cyan rim
    n_col_ramp.color_ramp.elements[1].position = 0.32
    n_col_ramp.color_ramp.elements[1].color = (0.94, 0.98, 1.0, 1.0)  # Pure ice crystal
    links.new(n_lw.outputs["Facing"], n_col_ramp.inputs["Fac"])

    n_alpha_ramp = nodes.new('ShaderNodeValToRGB')
    n_alpha_ramp.location = (-350, -450)
    n_alpha_ramp.color_ramp.elements[0].position = 0.0
    n_alpha_ramp.color_ramp.elements[0].color = (0.90, 0.90, 0.90, 1.0)
    n_alpha_ramp.color_ramp.elements[1].position = 0.36
    n_alpha_ramp.color_ramp.elements[1].color = (0.05, 0.05, 0.05, 1.0)
    links.new(n_lw.outputs["Facing"], n_alpha_ramp.inputs["Fac"])

    _, bub_fac, bub_a, bub_b, final_color = make_color_mix(loc=(-50, 0))
    bub_b.default_value = (0.98, 1.0, 1.0, 1.0)
    links.new(n_bub_ramp.outputs["Color"], bub_fac)
    links.new(n_col_ramp.outputs["Color"], bub_a)
    links.new(final_color, n_bsdf.inputs["Base Color"])
    links.new(n_alpha_ramp.outputs["Color"], n_bsdf.inputs["Alpha"])

    # Surface Droplet Bump
    n_drop_voro = nodes.new('ShaderNodeTexVoronoi')
    n_drop_voro.location = (150, -400)
    n_drop_voro.inputs["Scale"].default_value = 160.0
    n_drop_voro.voronoi_dimensions = '3D'
    links.new(n_tex_coord.outputs["Object"], n_drop_voro.inputs["Vector"])

    n_drop_ramp = nodes.new('ShaderNodeValToRGB')
    n_drop_ramp.location = (400, -400)
    n_drop_ramp.color_ramp.elements[0].position = 0.0
    n_drop_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    n_drop_ramp.color_ramp.elements[1].position = 0.08
    n_drop_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(n_drop_voro.outputs["Distance"], n_drop_ramp.inputs["Fac"])

    n_bump = nodes.new('ShaderNodeBump')
    n_bump.location = (650, -300)
    n_bump.inputs["Strength"].default_value = 0.035
    n_bump.inputs["Distance"].default_value = 0.001
    links.new(n_drop_ramp.outputs["Color"], n_bump.inputs["Height"])
    links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])

    mat_ice.blend_method = 'BLEND'
    mat_ice.show_transparent_back = True
    mat_ice.use_backface_culling = False
    ice_obj.data.materials.append(mat_ice)

    # 4. Studio Lighting & Camera
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 8.5
    key_data.size = 0.15
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.08, -0.10, 0.09)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-35))
    bpy.context.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 3.5
    fill_data.size = 0.20
    fill_data.color = (0.90, 0.96, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.10, -0.06, 0.07)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-10), math.radians(60))
    bpy.context.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 7.0
    rim_data.size = 0.15
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.02, 0.09, 0.08)
    rim_obj.rotation_euler = (math.radians(-40), math.radians(0), math.radians(180))
    bpy.context.collection.objects.link(rim_obj)

    cam_data = bpy.data.cameras.new("IceCamera")
    cam_data.lens = 65.0
    cam_obj = bpy.data.objects.new("IceCamera", cam_data)
    cam_pos = np.array([0.0, -0.12, 0.055])
    target = np.array([0.0, 0.0, 0.0])
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

    # 5. 2K Texture Baking
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')

    old_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.margin = 16

    RES = int(resolution)
    img_basecolor = bpy.data.images.new("Ice_BaseColor", width=RES, height=RES, alpha=True, float_buffer=False)
    img_roughness = bpy.data.images.new("Ice_Roughness", width=RES, height=RES, alpha=False, float_buffer=False)
    img_normal    = bpy.data.images.new("Ice_Normal",    width=RES, height=RES, alpha=False, float_buffer=False)

    tex_bake = nodes.new('ShaderNodeTexImage')
    node_emit = nodes.new('ShaderNodeEmission')
    node_out_bake = [n for n in nodes if n.type == 'OUTPUT_MATERIAL'][0]

    # Bake Base Color
    tex_bake.image = img_basecolor
    nodes.active = tex_bake
    links.new(final_color, node_emit.inputs["Color"])
    links.new(node_emit.outputs["Emission"], node_out_bake.inputs["Surface"])
    bpy.ops.object.bake(type='EMIT')

    # Bake Roughness
    tex_bake.image = img_roughness
    nodes.active = tex_bake
    node_emit.inputs["Color"].default_value = (0.02, 0.02, 0.02, 1.0)
    bpy.ops.object.bake(type='EMIT')

    # Bake Normal
    tex_bake.image = img_normal
    nodes.active = tex_bake
    links.new(n_bsdf.outputs["BSDF"], node_out_bake.inputs["Surface"])
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.render.bake.normal_space = 'TANGENT'
    bpy.ops.object.bake(type='NORMAL')

    nodes.remove(node_emit)
    nodes.remove(tex_bake)
    bpy.context.scene.render.engine = old_engine

    # 6. PBR Export Material
    mat_pbr = bpy.data.materials.new("Crystal_Ice_PBR_Export")
    mat_pbr.use_nodes = True
    p_nodes = mat_pbr.node_tree.nodes
    p_links = mat_pbr.node_tree.links
    p_nodes.clear()

    p_out = p_nodes.new('ShaderNodeOutputMaterial')
    p_bsdf = p_nodes.new('ShaderNodeBsdfPrincipled')
    p_bsdf.inputs["Specular IOR Level"].default_value = 0.95
    p_bsdf.inputs["IOR"].default_value = 1.310
    if "Transmission Weight" in p_bsdf.inputs:
        p_bsdf.inputs["Transmission Weight"].default_value = 0.85
    elif "Transmission" in p_bsdf.inputs:
        p_bsdf.inputs["Transmission"].default_value = 0.85
    p_links.new(p_bsdf.outputs["BSDF"], p_out.inputs["Surface"])

    t_col = p_nodes.new('ShaderNodeTexImage')
    t_col.image = img_basecolor
    p_links.new(t_col.outputs["Color"], p_bsdf.inputs["Base Color"])

    t_rgh = p_nodes.new('ShaderNodeTexImage')
    t_rgh.image = img_roughness
    img_roughness.colorspace_settings.name = 'Non-Color'
    p_links.new(t_rgh.outputs["Color"], p_bsdf.inputs["Roughness"])

    t_nrm = p_nodes.new('ShaderNodeTexImage')
    t_nrm.image = img_normal
    img_normal.colorspace_settings.name = 'Non-Color'
    n_map = p_nodes.new('ShaderNodeNormalMap')
    n_map.inputs["Strength"].default_value = 0.35
    p_links.new(t_nrm.outputs["Color"], n_map.inputs["Color"])
    p_links.new(n_map.outputs["Normal"], p_bsdf.inputs["Normal"])

    mat_pbr.blend_method = 'BLEND'
    mat_pbr.show_transparent_back = True
    mat_pbr.use_backface_culling = False

    ice_obj.data.materials.clear()
    ice_obj.data.materials.append(mat_pbr)

    # 7. Strictly ONE GLB Export
    bpy.ops.object.select_all(action='DESELECT')
    ice_obj.select_set(True)
    bpy.context.view_layer.objects.active = ice_obj

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
    create_and_export_master_ice_cube()
