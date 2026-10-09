"""
05_thermoformed_pet_plastic_cup.py
----------------------------------
Procedural generation recipe for a high-fidelity thermoformed disposable PET
plastic cold-drink cup (16 oz capacity) in Blender 4.x / 5.x.

Key Technical Highlights:
1. Closed 2D Meridian Revolve: Revolved continuous double-walled contour
   (outer wall -> toroidal rolled rim bead -> inward normal offset wall -> inner base)
   guaranteeing a 100% watertight, manifold mesh without Solidify modifier explosion.
2. Thermoforming Anatomy:
   - Recessed base floor with center injection dimple and concentric stiffening step
   - Table contact foot ring and vertical base skirt
   - Stacking recess waist crease (~11 mm)
   - Conical sidewall with draft angle
   - Stacking indexing rib (~118 mm)
   - Curled toroidal rolled rim bead lip (124 mm)
3. Optical Plastic PBR Shader:
   - Layer Weight (Facing) Fresnel network driving Base Color & Alpha
   - Delivers crisp dark refraction silhouettes at grazing angles and crystal
     transparency across facing normals with zero stochastic raytracing noise.
"""

import bpy
import math
import numpy as np

def create_pet_plastic_cup():
    # 1. Clean existing scene objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # 2. Outer Profile Curve Definition (in millimeters)
    outer_pts = [
        # Bottom Center Sprue / Injection Dimple (Outer)
        (0.0, 4.8),
        (2.0, 5.0),
        (4.5, 4.6),
        (6.5, 3.8),
        # Base outer floor
        (11.0, 3.4),
        (15.0, 3.4),
        # Stiffening concentric step (outer)
        (17.5, 4.2),
        (19.5, 4.2),
        (22.0, 3.4),
        (26.0, 3.0),
        # Curve to outer foot ring
        (28.8, 1.8),
        (30.2, 0.8),
        (30.8, 0.0),   # Foot contact line (Z = 0.0)
        (31.4, 0.0),
        (31.6, 0.6),
        # Base skirt wall (outer)
        (31.8, 2.5),
        (32.0, 5.5),
        (32.1, 8.5),
        (32.2, 10.2),  # Skirt upper corner
        # Stacking recess step (inward indent crease)
        (31.5, 11.0),
        (30.6, 11.8),  # Crease notch
        (30.8, 12.6),
        (31.3, 14.0),  # Blend into tapered sidewall
        # Main conical sidewall (smooth straight taper)
        (32.5, 25.0),
        (34.2, 42.0),
        (36.0, 60.0),
        (38.0, 80.0),
        (40.0, 98.0),
        (41.6, 112.0),
        # Upper stacking indexing rib (10mm below rim)
        (42.2, 116.5),
        (43.2, 117.8),  # Rib bead crest
        (42.8, 118.8),  # Rib valley
        (43.5, 120.5),  # Upper collar
        (44.5, 122.2),
        # Rolled rim lip (toroidal rolled bead)
        (45.5, 123.4),
        (46.5, 124.0),
        (47.5, 124.4),  # Top crest
        (48.5, 124.2),
        (49.0, 123.5),  # Outer apex of rolled lip
        (48.8, 122.4),  # Rolling down
        (48.2, 121.6),  # Under curl
        (47.5, 121.8),  # Tucked lip interior edge
    ]

    # Sample dense outer curve
    def sample_path(pts, ds=0.6):
        res = []
        for i in range(len(pts) - 1):
            p0 = np.array(pts[i])
            p1 = np.array(pts[i+1])
            d = np.linalg.norm(p1 - p0)
            n = max(2, int(d / ds))
            for step in range(n):
                res.append((1 - step / n) * p0 + (step / n) * p1)
        res.append(np.array(pts[-1]))
        return np.array(res)

    outer_dense = sample_path(outer_pts, ds=0.6)

    # Inward normal offset for realistic wall thickness (t = 0.55 mm)
    t = 0.55
    tangents = np.gradient(outer_dense, axis=0)
    normals = np.zeros_like(tangents)
    for i in range(len(tangents)):
        dr, dz = tangents[i]
        length = math.hypot(dr, dz)
        if length > 1e-6:
            normals[i] = (-dz / length, dr / length)
        else:
            normals[i] = (0, 1)

    inner_dense = []
    for i in reversed(range(len(outer_dense))):
        p = outer_dense[i]
        n = normals[i]
        p_in = p + t * n
        if p_in[0] < 0:
            p_in[0] = 0.0
        inner_dense.append(p_in)
    inner_dense = np.array(inner_dense)
    inner_dense[-1, 0] = 0.0

    full_profile_mm = np.vstack([outer_dense, inner_dense])
    profile_m = [(p[0] * 0.001, p[1] * 0.001) for p in full_profile_mm]

    # 3. Construct Revolved Mesh
    mesh = bpy.data.meshes.new("PET_PlasticCup_Mesh")
    cup_obj = bpy.data.objects.new("PET_PlasticCup", mesh)
    bpy.context.collection.objects.link(cup_obj)

    N_radial = 84
    N_prof = len(profile_m)

    verts = []
    for p_idx, (r, z) in enumerate(profile_m):
        if r < 1e-5:
            verts.append((0.0, 0.0, z))
        else:
            for rad_idx in range(N_radial):
                th = 2.0 * math.pi * rad_idx / N_radial
                verts.append((r * math.cos(th), r * math.sin(th), z))

    def get_v_idx(p_idx, rad_idx):
        r, _ = profile_m[p_idx]
        if r < 1e-5:
            return 0 if p_idx == 0 else len(verts) - 1
        return 1 + (p_idx - 1) * N_radial + (rad_idx % N_radial)

    faces = []
    # Outer base center fan
    for rad_idx in range(N_radial):
        v0 = 0
        v1 = 1 + rad_idx
        v2 = 1 + ((rad_idx + 1) % N_radial)
        faces.append((v0, v1, v2))

    # Meridian quad rings
    for p_idx in range(1, N_prof - 2):
        for rad_idx in range(N_radial):
            v1 = get_v_idx(p_idx, rad_idx)
            v2 = get_v_idx(p_idx, rad_idx + 1)
            v3 = get_v_idx(p_idx + 1, rad_idx + 1)
            v4 = get_v_idx(p_idx + 1, rad_idx)
            faces.append((v1, v2, v3, v4))

    # Inner base center fan
    v_center_in = len(verts) - 1
    for rad_idx in range(N_radial):
        v1 = get_v_idx(N_prof - 2, rad_idx)
        v2 = get_v_idx(N_prof - 2, rad_idx + 1)
        faces.append((v2, v1, v_center_in))

    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Subdivision Surface Modifier
    subsurf = cup_obj.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2

    # 4. Optical Transparent PET Material Setup
    mat = bpy.data.materials.new(name="PET_Clear_Plastic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_out.location = (500, 0)

    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.location = (150, 0)
    node_bsdf.inputs["Roughness"].default_value = 0.015
    node_bsdf.inputs["IOR"].default_value = 1.54
    if "Specular IOR Level" in node_bsdf.inputs:
        node_bsdf.inputs["Specular IOR Level"].default_value = 0.95

    # Layer Weight Fresnel Network
    node_lw = nodes.new('ShaderNodeLayerWeight')
    node_lw.location = (-450, 0)
    node_lw.inputs["Blend"].default_value = 0.22

    # Grazing Edge Dark Refraction Tint
    ramp_col = nodes.new('ShaderNodeValToRGB')
    ramp_col.location = (-150, 150)
    ramp_col.color_ramp.elements[0].position = 0.0
    ramp_col.color_ramp.elements[0].color = (0.20, 0.24, 0.28, 1.0)
    ramp_col.color_ramp.elements[1].position = 0.30
    ramp_col.color_ramp.elements[1].color = (0.98, 0.99, 1.0, 1.0)

    # Transparency Alpha Ramp (Clear Body, Crisp Outline)
    ramp_alpha = nodes.new('ShaderNodeValToRGB')
    ramp_alpha.location = (-150, -150)
    ramp_alpha.color_ramp.elements[0].position = 0.0
    ramp_alpha.color_ramp.elements[0].color = (0.92, 0.92, 0.92, 1.0)
    ramp_alpha.color_ramp.elements[1].position = 0.38
    ramp_alpha.color_ramp.elements[1].color = (0.05, 0.05, 0.05, 1.0)

    links.new(node_lw.outputs["Facing"], ramp_col.inputs["Fac"])
    links.new(ramp_col.outputs["Color"], node_bsdf.inputs["Base Color"])
    links.new(node_lw.outputs["Facing"], ramp_alpha.inputs["Fac"])
    links.new(ramp_alpha.outputs["Color"], node_bsdf.inputs["Alpha"])
    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    mat.blend_method = 'BLEND'
    mat.show_transparent_back = True
    mat.use_backface_culling = False
    cup_obj.data.materials.append(mat)

    # 5. Studio Lighting Rig
    # Key Light
    key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
    key_data.energy = 10.0
    key_data.size = 0.18
    key_data.size_y = 0.25
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.20, -0.25, 0.22)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-40))
    bpy.context.collection.objects.link(key_obj)

    # Fill Light
    fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
    fill_data.energy = 6.0
    fill_data.size = 0.18
    fill_data.size_y = 0.25
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.20, -0.25, 0.22)
    fill_obj.rotation_euler = (math.radians(50), math.radians(-10), math.radians(55))
    bpy.context.collection.objects.link(fill_obj)

    # Top Rim Light
    top_data = bpy.data.lights.new(name="TopRim", type='AREA')
    top_data.energy = 8.0
    top_data.size = 0.20
    top_obj = bpy.data.objects.new("TopRim", top_data)
    top_obj.location = (0.0, -0.05, 0.28)
    bpy.context.collection.objects.link(top_obj)

    # 6. Studio Camera
    cam_data = bpy.data.cameras.new("CupCamera")
    cam_data.lens = 78.0
    cam_obj = bpy.data.objects.new("CupCamera", cam_data)
    cam_obj.location = (0.0, -0.42, 0.155)
    dz = 0.155 - 0.065
    dy = 0.42
    pitch = math.pi / 2 - math.atan2(dz, dy)
    cam_obj.rotation_euler = (pitch, 0.0, 0.0)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 7. Configure Viewport
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

    print("Thermoformed PET Plastic Cup generated successfully!")

if __name__ == "__main__":
    create_pet_plastic_cup()
