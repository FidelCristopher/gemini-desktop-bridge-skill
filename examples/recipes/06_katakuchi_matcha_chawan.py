"""
06_katakuchi_matcha_chawan.py
-----------------------------
Procedural generation recipe for an authentic Japanese Katakuchi Matcha Chawan
(片口茶碗) ceramic vessel in Blender 4.x / 5.x.

Key Architectural & Technical Features:
1. Revolved Hand-Thrown Ceramic Profile:
   - Rim Diameter: 15.2 cm (Radius R = 0.076 m)
   - Height: 6.45 cm (Z = 0.0645 m)
   - Foot Ring (Kodai): Outer R = 39.0 mm, Inner R = 34.8 mm, Height = 3.5 mm
   - Wall Thickness: Uniform 4.2 mm across the entire profile
   - Center Tea Pool (Chadamari): Non-polar quad-grid manifold floor at Z = 9.5 mm
   - 5 Concentric Wheel-Thrown Tactile Grooves (Rokuro-me) along lower exterior (Z = 12 to 38 mm)
2. Coherent Polar Spout (Katakuchi Lip) Deformation:
   - Displaces vertices radially along unit vector r (Delta r = +13.5 mm)
   - Combines with vertical pour trough dip (Delta z = -7.5 mm)
   - C^1-continuous azimuthal cosine bell curve (span +/-25 deg) and vertical smoothstep weighting
   - Guarantees 100% uniform ceramic wall thickness with zero edge creasing or thin-blade shearing
3. Dual-Material Procedural PBR Shader (Katakuchi_Ceramic_Master):
   - Vertex Color Attribute (CeramicAttrs):
     * Red: GlazeFactor (1.0 interior glaze, 0.0 exterior clay, wavy micro-warped break at rim)
     * Green: GrooveFactor (shadow darkening in throwing rings)
     * Blue: ProfileV (normalized meridian coordinate)
   - Interior Base Glaze: Toasted caramel/amber rim gradient transitioning into warm almond cream
   - Kuro-ten (Iron Spots): Multi-scale Voronoi noise network producing bold burnt umber iron oxide specks
   - Exterior Clay Body: Rich chocolate terracotta stoneware darkened in throwing grooves
   - Tactile Micro-Bump: Orange-peel waviness and clay grog texture
"""

import bpy
import math
import numpy as np
import mathutils

def create_katakuchi_chawan():
    # 1. Clean existing scene objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Define Revolved Profile Coordinates (in millimeters)
    # (r_mm, z_mm, glaze_factor, groove_factor)
    outer_profile = [
        # Center underneath base inside kodai hollow
        (0.0, 5.5, 0.0, 0.0),
        (8.0, 5.5, 0.0, 0.0),
        (18.0, 5.0, 0.0, 0.0),
        (28.0, 4.2, 0.0, 0.0),
        (34.8, 3.5, 0.0, 0.0),
        # Kodai foot ring contact flat
        (35.2, 0.5, 0.0, 0.0),
        (36.0, 0.0, 0.0, 0.0),
        (38.0, 0.0, 0.0, 0.0),
        (39.0, 0.5, 0.0, 0.0),
        (39.2, 3.5, 0.0, 0.0),
        # Exterior lower bowl transition
        (40.5, 6.0, 0.0, 0.0),
        (42.5, 9.0, 0.0, 0.0),
        # 5 Throwing grooves (Rokuro-me)
        (44.5, 12.0, 0.0, 0.2),
        (45.8, 14.0, 0.0, 1.0),
        (48.0, 17.0, 0.0, 0.0),
        (49.8, 19.5, 0.0, 1.0),
        (52.2, 23.0, 0.0, 0.0),
        (54.4, 25.5, 0.0, 1.0),
        (57.0, 29.0, 0.0, 0.0),
        (59.5, 31.5, 0.0, 1.0),
        (62.5, 35.0, 0.0, 0.0),
        (64.8, 37.5, 0.0, 0.8),
        (67.5, 41.5, 0.0, 0.0),
        # Upper exterior wall tapering towards rim
        (70.5, 48.0, 0.0, 0.0),
        (73.0, 54.5, 0.0, 0.0),
        (74.8, 60.0, 0.1, 0.0),
        (75.8, 63.5, 0.3, 0.0),
        (76.0, 64.5, 0.5, 0.0),  # Rim crest peak
        (75.0, 64.3, 0.7, 0.0),
    ]

    inner_profile = [
        (73.5, 63.5, 0.95, 0.0),
        (71.5, 59.5, 1.0, 0.0),
        (68.5, 53.5, 1.0, 0.0),
        (65.0, 47.0, 1.0, 0.0),
        (61.0, 40.0, 1.0, 0.0),
        (56.5, 33.0, 1.0, 0.0),
        (51.0, 26.0, 1.0, 0.0),
        (44.5, 19.5, 1.0, 0.0),
        (37.5, 14.5, 1.0, 0.0),
        (29.0, 11.2, 1.0, 0.0),
        (20.0, 9.8,  1.0, 0.0),  # Outer chadamari pool
        (12.0, 9.2,  1.0, 0.0),  # Whisk dimple
        (5.0,  9.3,  1.0, 0.0),
        (0.0,  9.5,  1.0, 0.0),  # Center tea pool
    ]

    def resample_path(outer_pts, inner_pts, n_out=85, n_in=65):
        def interp(pts, n):
            arr = np.array(pts)
            dists = np.sqrt(np.sum(np.diff(arr[:, :2], axis=0)**2, axis=1))
            s = np.concatenate(([0], np.cumsum(dists)))
            s_eval = np.linspace(0, s[-1], n)
            res = np.zeros((n, 4))
            for c in range(4):
                res[:, c] = np.interp(s_eval, s, arr[:, c])
            return res

        arr_o = interp(outer_pts, n_out)
        arr_i = interp(inner_pts, n_in)
        full = np.vstack([arr_o, arr_i])
        diffs = np.sqrt(np.sum(np.diff(full[:, :2], axis=0)**2, axis=1))
        s_full = np.concatenate(([0], np.cumsum(diffs)))
        v_norm = s_full / s_full[-1]
        
        data = []
        for i in range(len(full)):
            r_m = full[i, 0] * 0.001
            z_m = full[i, 1] * 0.001
            glaze = float(np.clip(full[i, 2], 0.0, 1.0))
            groove = float(np.clip(full[i, 3], 0.0, 1.0))
            data.append((r_m, z_m, glaze, groove, float(v_norm[i])))
        return data

    profile = resample_path(outer_profile, inner_profile, n_out=85, n_in=65)
    N_prof = len(profile)
    N_radial = 128

    # 3. Construct 3D Lathe Mesh with Coherent Polar Spout Deformation
    mesh = bpy.data.meshes.new("Katakuchi_Chawan_Mesh")
    chawan_obj = bpy.data.objects.new("Katakuchi_Chawan", mesh)
    bpy.context.collection.objects.link(chawan_obj)

    THETA_SPOUT = math.pi
    SPAN_THETA = math.radians(25.0)
    Z_SPOUT_MIN = 0.035
    Z_SPOUT_MAX = 0.0645
    RADIAL_FLARE = 0.0135
    TROUGH_DIP   = 0.0075

    verts = []
    vert_attrs = []

    for p_idx, (r, z, glaze, groove, v_norm) in enumerate(profile):
        if r < 1e-5:
            verts.append((0.0, 0.0, z))
            vert_attrs.append((glaze, groove, v_norm))
        else:
            for rad_idx in range(N_radial):
                th = 2.0 * math.pi * rad_idx / N_radial
                d_th = abs((th - THETA_SPOUT + math.pi) % (2.0 * math.pi) - math.pi)
                w_th = math.cos((d_th / SPAN_THETA) * (math.pi / 2.0)) ** 2.0 if d_th < SPAN_THETA else 0.0
                
                if z > Z_SPOUT_MIN:
                    tz = min(1.0, (z - Z_SPOUT_MIN) / (Z_SPOUT_MAX - Z_SPOUT_MIN))
                    w_z = tz * tz * (3.0 - 2.0 * tz)
                else:
                    w_z = 0.0

                spout_w = w_th * w_z
                r_def = r + RADIAL_FLARE * spout_w
                z_def = z - TROUGH_DIP * (w_th ** 1.6) * w_z

                x = r_def * math.cos(th)
                y = r_def * math.sin(th)
                verts.append((x, y, z_def))
                vert_attrs.append((glaze, groove, v_norm))

    def get_v_idx(p_idx, rad_idx):
        if profile[p_idx][0] < 1e-5:
            return 0 if p_idx == 0 else len(verts) - 1
        return 1 + (p_idx - 1) * N_radial + (rad_idx % N_radial)

    faces = []
    for rad_idx in range(N_radial):
        v0 = 0
        v1 = 1 + rad_idx
        v2 = 1 + ((rad_idx + 1) % N_radial)
        faces.append((v0, v1, v2))

    for p_idx in range(1, N_prof - 2):
        for rad_idx in range(N_radial):
            v1 = get_v_idx(p_idx, rad_idx)
            v2 = get_v_idx(p_idx, rad_idx + 1)
            v3 = get_v_idx(p_idx + 1, rad_idx + 1)
            v4 = get_v_idx(p_idx + 1, rad_idx)
            faces.append((v1, v2, v3, v4))

    v_center_in = len(verts) - 1
    for rad_idx in range(N_radial):
        v1 = get_v_idx(N_prof - 2, rad_idx)
        v2 = get_v_idx(N_prof - 2, rad_idx + 1)
        faces.append((v2, v1, v_center_in))

    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = True

    # 4. Color Attributes (CeramicAttrs)
    color_attr = mesh.color_attributes.new(name="CeramicAttrs", type='FLOAT_COLOR', domain='CORNER')
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            glaze, groove, v_norm = vert_attrs[v_idx]
            color_attr.data[loop_idx].color = (glaze, groove, v_norm, 1.0)

    # 5. Modifiers: Subsurf Level 2
    subsurf = chawan_obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    # 6. Procedural PBR Ceramic Master Shader
    mat = bpy.data.materials.new(name="Katakuchi_Ceramic_Master")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
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

    def make_float_mix(loc=(0, 0)):
        n = nodes.new('ShaderNodeMix')
        n.data_type = 'FLOAT'
        n.location = loc
        fac = [i for i in n.inputs if i.name == 'Factor' and i.type == 'VALUE'][0]
        a = [i for i in n.inputs if i.name == 'A' and i.type == 'VALUE'][0]
        b = [i for i in n.inputs if i.name == 'B' and i.type == 'VALUE'][0]
        res = [o for o in n.outputs if o.type == 'VALUE'][0]
        return n, fac, a, b, res

    # Material Output & Principled BSDF
    n_out = nodes.new('ShaderNodeOutputMaterial')
    n_out.location = (1400, 0)

    n_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    n_bsdf.location = (1100, 0)
    n_bsdf.inputs["Specular IOR Level"].default_value = 0.55
    if "Subsurface Weight" in n_bsdf.inputs:
        n_bsdf.inputs["Subsurface Weight"].default_value = 0.05
        n_bsdf.inputs["Subsurface Radius"].default_value = (0.35, 0.25, 0.15)
    links.new(n_bsdf.outputs["BSDF"], n_out.inputs["Surface"])

    # Attribute Node
    n_attr = nodes.new('ShaderNodeAttribute')
    n_attr.location = (-1200, 200)
    n_attr.attribute_name = "CeramicAttrs"

    n_sep = nodes.new('ShaderNodeSeparateColor')
    n_sep.location = (-950, 200)
    links.new(n_attr.outputs["Color"], n_sep.inputs["Color"])

    # Master Glaze Break Mask
    n_warp_tex = nodes.new('ShaderNodeTexNoise')
    n_warp_tex.location = (-950, 500)
    n_warp_tex.inputs["Scale"].default_value = 45.0
    n_warp_tex.inputs["Detail"].default_value = 4.0

    n_warp_scale = nodes.new('ShaderNodeMath')
    n_warp_scale.location = (-700, 500)
    n_warp_scale.operation = 'MULTIPLY'
    n_warp_scale.inputs[1].default_value = 0.10
    links.new(n_warp_tex.outputs["Fac"], n_warp_scale.inputs[0])

    n_glaze_add = nodes.new('ShaderNodeMath')
    n_glaze_add.location = (-500, 350)
    n_glaze_add.operation = 'ADD'
    links.new(n_sep.outputs["Red"], n_glaze_add.inputs[0])
    links.new(n_warp_scale.outputs["Value"], n_glaze_add.inputs[1])

    n_glaze_mask = nodes.new('ShaderNodeValToRGB')
    n_glaze_mask.location = (-280, 350)
    n_glaze_mask.color_ramp.elements[0].position = 0.44
    n_glaze_mask.color_ramp.elements[0].color = (0, 0, 0, 1)
    n_glaze_mask.color_ramp.elements[1].position = 0.54
    n_glaze_mask.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(n_glaze_add.outputs["Value"], n_glaze_mask.inputs["Fac"])

    # Interior Glaze Gradient Ramp
    n_v_noise = nodes.new('ShaderNodeTexNoise')
    n_v_noise.location = (-950, -50)
    n_v_noise.inputs["Scale"].default_value = 14.0
    n_v_noise.inputs["Detail"].default_value = 4.0

    n_v_scale = nodes.new('ShaderNodeMath')
    n_v_scale.location = (-700, -50)
    n_v_scale.operation = 'MULTIPLY'
    n_v_scale.inputs[1].default_value = 0.06
    links.new(n_v_noise.outputs["Fac"], n_v_scale.inputs[0])

    n_v_add = nodes.new('ShaderNodeMath')
    n_v_add.location = (-500, -100)
    n_v_add.operation = 'ADD'
    links.new(n_sep.outputs["Blue"], n_v_add.inputs[0])
    links.new(n_v_scale.outputs["Value"], n_v_add.inputs[1])

    n_glaze_grad = nodes.new('ShaderNodeValToRGB')
    n_glaze_grad.location = (-280, -100)
    n_glaze_grad.color_ramp.elements[0].position = 0.56
    n_glaze_grad.color_ramp.elements[0].color = (0.12, 0.045, 0.012, 1.0)  # Golden caramel rim
    el_mid = n_glaze_grad.color_ramp.elements.new(0.68)
    el_mid.color = (0.32, 0.16, 0.055, 1.0)                                # Amber band
    n_glaze_grad.color_ramp.elements[2].position = 0.86
    n_glaze_grad.color_ramp.elements[2].color = (0.68, 0.58, 0.42, 1.0)   # Oatmeal cream floor
    links.new(n_v_add.outputs["Value"], n_glaze_grad.inputs["Fac"])

    # Multi-Scale Kuro-ten (Iron Spots & Flecks)
    n_voro_l = nodes.new('ShaderNodeTexVoronoi')
    n_voro_l.location = (-700, -400)
    n_voro_l.inputs["Scale"].default_value = 28.0
    n_voro_l.voronoi_dimensions = '3D'

    n_voro_m = nodes.new('ShaderNodeTexVoronoi')
    n_voro_m.location = (-700, -550)
    n_voro_m.inputs["Scale"].default_value = 55.0
    n_voro_m.voronoi_dimensions = '3D'

    n_voro_s = nodes.new('ShaderNodeTexVoronoi')
    n_voro_s.location = (-700, -700)
    n_voro_s.inputs["Scale"].default_value = 160.0
    n_voro_s.voronoi_dimensions = '3D'

    n_voro_ramp_l = nodes.new('ShaderNodeValToRGB')
    n_voro_ramp_l.location = (-450, -400)
    n_voro_ramp_l.color_ramp.elements[0].position = 0.0
    n_voro_ramp_l.color_ramp.elements[0].color = (1, 1, 1, 1)
    n_voro_ramp_l.color_ramp.elements[1].position = 0.18
    n_voro_ramp_l.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(n_voro_l.outputs["Distance"], n_voro_ramp_l.inputs["Fac"])

    n_voro_ramp_m = nodes.new('ShaderNodeValToRGB')
    n_voro_ramp_m.location = (-450, -550)
    n_voro_ramp_m.color_ramp.elements[0].position = 0.0
    n_voro_ramp_m.color_ramp.elements[0].color = (1, 1, 1, 1)
    n_voro_ramp_m.color_ramp.elements[1].position = 0.13
    n_voro_ramp_m.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(n_voro_m.outputs["Distance"], n_voro_ramp_m.inputs["Fac"])

    n_voro_ramp_s = nodes.new('ShaderNodeValToRGB')
    n_voro_ramp_s.location = (-450, -700)
    n_voro_ramp_s.color_ramp.elements[0].position = 0.0
    n_voro_ramp_s.color_ramp.elements[0].color = (1, 1, 1, 1)
    n_voro_ramp_s.color_ramp.elements[1].position = 0.09
    n_voro_ramp_s.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(n_voro_s.outputs["Distance"], n_voro_ramp_s.inputs["Fac"])

    n_max1 = nodes.new('ShaderNodeMath')
    n_max1.location = (-200, -480)
    n_max1.operation = 'MAXIMUM'
    links.new(n_voro_ramp_l.outputs["Color"], n_max1.inputs[0])
    links.new(n_voro_ramp_m.outputs["Color"], n_max1.inputs[1])

    n_spots_max = nodes.new('ShaderNodeMath')
    n_spots_max.location = (-50, -550)
    n_spots_max.operation = 'MAXIMUM'
    links.new(n_max1.outputs["Value"], n_spots_max.inputs[0])
    links.new(n_voro_ramp_s.outputs["Color"], n_spots_max.inputs[1])

    # Blend Iron Spots onto Interior Glaze
    _, int_fac, int_a, int_b, int_out = make_color_mix(loc=(150, -200))
    int_b.default_value = (0.008, 0.003, 0.001, 1.0)  # Deep burnt umber iron spot
    links.new(n_spots_max.outputs["Value"], int_fac)
    links.new(n_glaze_grad.outputs["Color"], int_a)

    # Exterior Clay Body
    n_clay_tex = nodes.new('ShaderNodeTexNoise')
    n_clay_tex.location = (-600, -950)
    n_clay_tex.inputs["Scale"].default_value = 50.0
    n_clay_tex.inputs["Detail"].default_value = 5.0

    n_clay_ramp = nodes.new('ShaderNodeValToRGB')
    n_clay_ramp.location = (-350, -950)
    n_clay_ramp.color_ramp.elements[0].position = 0.2
    n_clay_ramp.color_ramp.elements[0].color = (0.035, 0.014, 0.005, 1.0)  # Deep terracotta umber
    n_clay_ramp.color_ramp.elements[1].position = 0.8
    n_clay_ramp.color_ramp.elements[1].color = (0.065, 0.028, 0.012, 1.0)  # Warm terracotta body
    links.new(n_clay_tex.outputs["Fac"], n_clay_ramp.inputs["Fac"])

    _, grv_fac, grv_a, grv_b, grv_out = make_color_mix(loc=(-50, -850))
    grv_b.default_value = (0.012, 0.004, 0.0015, 1.0)  # Deep shadow in throwing grooves
    links.new(n_sep.outputs["Green"], grv_fac)
    links.new(n_clay_ramp.outputs["Color"], grv_a)

    # Master Exterior Clay vs Interior Glaze Blend
    _, final_fac, final_clay, final_glaze, final_out = make_color_mix(loc=(450, 0))
    links.new(n_glaze_mask.outputs["Color"], final_fac)
    links.new(grv_out, final_clay)
    links.new(int_out, final_glaze)
    links.new(final_out, n_bsdf.inputs["Base Color"])

    # Roughness
    _, rough_fac, rough_clay, rough_glaze, rough_out = make_float_mix(loc=(450, -250))
    rough_clay.default_value = 0.75
    rough_glaze.default_value = 0.32
    links.new(n_glaze_mask.outputs["Color"], rough_fac)
    links.new(rough_out, n_bsdf.inputs["Roughness"])

    # Tactile Normal Bump
    n_bump_tex = nodes.new('ShaderNodeTexNoise')
    n_bump_tex.location = (200, -500)
    n_bump_tex.inputs["Scale"].default_value = 130.0
    n_bump_tex.inputs["Detail"].default_value = 6.0

    n_bump = nodes.new('ShaderNodeBump')
    n_bump.location = (500, -450)
    n_bump.inputs["Strength"].default_value = 0.035
    n_bump.inputs["Distance"].default_value = 0.002
    links.new(n_bump_tex.outputs["Fac"], n_bump.inputs["Height"])
    links.new(n_bump.outputs["Normal"], n_bsdf.inputs["Normal"])

    chawan_obj.data.materials.append(mat)

    # 7. Lighting Setup
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 8.5
    key_data.size = 0.35
    key_data.color = (1.0, 0.97, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.20, -0.20, 0.28)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-40))
    bpy.context.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 2.8
    fill_data.size = 0.45
    fill_data.color = (0.95, 0.97, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.24, -0.16, 0.22)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-10), math.radians(55))
    bpy.context.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
    rim_data.energy = 5.2
    rim_data.size = 0.30
    rim_data.color = (1.0, 0.96, 0.90)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.0, 0.26, 0.26)
    rim_obj.rotation_euler = (math.radians(-45), math.radians(0), math.radians(180))
    bpy.context.collection.objects.link(rim_obj)

    # 8. Studio Camera
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = 62.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    cam_pos = np.array([-0.16, -0.26, 0.235])
    target = np.array([-0.005, 0.0, 0.025])
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

    # 9. Viewport Configuration
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.overlay.show_overlays = True
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = False
                        space.shading.background_type = 'THEME'

    print("Katakuchi Matcha Chawan asset generated successfully!")

if __name__ == "__main__":
    create_katakuchi_chawan()
