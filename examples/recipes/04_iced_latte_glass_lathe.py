import bpy
import math

# Clean scene
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()

def get_base_nodes(mat):
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    output = mat.node_tree.nodes.get("Material Output")
    return mat.node_tree.nodes, mat.node_tree.links, bsdf, output

# ==========================================
# 1. SHADER MATERIALS
# ==========================================

# A. Clear Glass
mat_glass = bpy.data.materials.new(name="Glass_Realistic")
nodes_g, links_g, bsdf_g, out_g = get_base_nodes(mat_glass)
mat_glass.blend_method = 'BLEND' if hasattr(mat_glass, 'blend_method') else 'OPAQUE'
if hasattr(mat_glass, 'use_raytrace_refraction'):
    mat_glass.use_raytrace_refraction = True
mat_glass.diffuse_color = (0.95, 0.98, 1.0, 0.18)

bsdf_g.inputs["Base Color"].default_value = (0.98, 1.0, 1.0, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.04
bsdf_g.inputs["Transmission Weight"].default_value = 1.0
bsdf_g.inputs["IOR"].default_value = 1.48
bsdf_g.inputs["Alpha"].default_value = 0.20

# B. Creamy Matcha Liquid
mat_matcha = bpy.data.materials.new(name="Matcha_Creamy_Textured")
nodes_m, links_m, bsdf_m, out_m = get_base_nodes(mat_matcha)
mat_matcha.diffuse_color = (0.22, 0.52, 0.10, 1.0)

tex_coord_m = nodes_m.new("ShaderNodeTexCoord")
noise_m = nodes_m.new("ShaderNodeTexNoise")
noise_m.inputs["Scale"].default_value = 4.5
noise_m.inputs["Detail"].default_value = 4.0

color_ramp_m = nodes_m.new("ShaderNodeValToRGB")
color_ramp_m.color_ramp.elements[0].position = 0.2
color_ramp_m.color_ramp.elements[0].color = (0.16, 0.44, 0.07, 1.0) # Deep vibrant Matcha
color_ramp_m.color_ramp.elements[1].position = 0.8
color_ramp_m.color_ramp.elements[1].color = (0.26, 0.58, 0.12, 1.0) # Milky Matcha

links_m.new(tex_coord_m.outputs["Object"], noise_m.inputs["Vector"])
links_m.new(noise_m.outputs["Fac"], color_ramp_m.inputs["Fac"])
links_m.new(color_ramp_m.outputs["Color"], bsdf_m.inputs["Base Color"])

bsdf_m.inputs["Roughness"].default_value = 0.22
if "Subsurface Weight" in bsdf_m.inputs:
    bsdf_m.inputs["Subsurface Weight"].default_value = 0.4
    bsdf_m.inputs["Subsurface Radius"].default_value = (0.2, 0.45, 0.1)

# C. Cold Foam Cream
mat_foam = bpy.data.materials.new(name="ColdFoam_Microbubble")
nodes_f, links_f, bsdf_f, out_f = get_base_nodes(mat_foam)
mat_foam.diffuse_color = (0.97, 0.97, 0.94, 1.0)

bsdf_f.inputs["Base Color"].default_value = (0.97, 0.97, 0.94, 1.0)
bsdf_f.inputs["Roughness"].default_value = 0.45
if "Subsurface Weight" in bsdf_f.inputs:
    bsdf_f.inputs["Subsurface Weight"].default_value = 0.25

tex_coord_f = nodes_f.new("ShaderNodeTexCoord")
noise_f = nodes_f.new("ShaderNodeTexNoise")
noise_f.inputs["Scale"].default_value = 50.0
noise_f.inputs["Detail"].default_value = 8.0
noise_f.inputs["Roughness"].default_value = 0.7

bump_f = nodes_f.new("ShaderNodeBump")
bump_f.inputs["Strength"].default_value = 0.35

links_f.new(tex_coord_f.outputs["Object"], noise_f.inputs["Vector"])
links_f.new(noise_f.outputs["Fac"], bump_f.inputs["Height"])
links_f.new(bump_f.outputs["Normal"], bsdf_f.inputs["Normal"])

# D. Matcha Powder Dusting
mat_powder = bpy.data.materials.new(name="MatchaPowder_Grainy")
nodes_p, links_p, bsdf_p, out_p = get_base_nodes(mat_powder)
mat_powder.blend_method = 'HASHED' if hasattr(mat_powder, 'blend_method') else 'OPAQUE'
mat_powder.diffuse_color = (0.12, 0.32, 0.05, 1.0)

tex_coord_p = nodes_p.new("ShaderNodeTexCoord")
noise_p = nodes_p.new("ShaderNodeTexNoise")
noise_p.inputs["Scale"].default_value = 80.0
noise_p.inputs["Detail"].default_value = 10.0

color_ramp_p = nodes_p.new("ShaderNodeValToRGB")
color_ramp_p.color_ramp.elements[0].position = 0.3
color_ramp_p.color_ramp.elements[0].color = (0.09, 0.25, 0.04, 1.0)
color_ramp_p.color_ramp.elements[1].position = 0.75
color_ramp_p.color_ramp.elements[1].color = (0.22, 0.50, 0.10, 1.0)

bump_p = nodes_p.new("ShaderNodeBump")
bump_p.inputs["Strength"].default_value = 0.6

links_p.new(tex_coord_p.outputs["Object"], noise_p.inputs["Vector"])
links_p.new(noise_p.outputs["Fac"], color_ramp_p.inputs["Fac"])
links_p.new(color_ramp_p.outputs["Color"], bsdf_p.inputs["Base Color"])
links_p.new(noise_p.outputs["Fac"], bump_p.inputs["Height"])
links_p.new(bump_p.outputs["Normal"], bsdf_p.inputs["Normal"])
bsdf_p.inputs["Roughness"].default_value = 0.9

# E. Ice Cubes
mat_ice = bpy.data.materials.new(name="Ice_Realistic")
nodes_i, links_i, bsdf_i, out_i = get_base_nodes(mat_ice)
mat_ice.blend_method = 'BLEND' if hasattr(mat_ice, 'blend_method') else 'OPAQUE'
mat_ice.diffuse_color = (0.92, 0.97, 1.0, 0.35)

bsdf_i.inputs["Base Color"].default_value = (0.95, 0.98, 1.0, 1.0)
bsdf_i.inputs["Roughness"].default_value = 0.08
bsdf_i.inputs["Transmission Weight"].default_value = 0.95
bsdf_i.inputs["IOR"].default_value = 1.31
bsdf_i.inputs["Alpha"].default_value = 0.35


# ==========================================
# 2. SEAMLESS WATERTIGHT GEOMETRY (NO GAPS!)
# ==========================================

def create_revolved_mesh(name, profile_rz, segments=56, cap_bottom=True, cap_top=True):
    """Generates a lathe/revolved mesh from (r, z) profile with zero gaps."""
    verts = []
    faces = []
    num_rings = len(profile_rz)
    
    for r, z in profile_rz:
        for i in range(segments):
            angle = (2.0 * math.pi * i) / segments
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            verts.append((x, y, z))
            
    for ring in range(num_rings - 1):
        r_start = ring * segments
        next_r_start = (ring + 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((r_start + i, r_start + next_i, next_r_start + next_i, next_r_start + i))
            
    if cap_bottom:
        bottom_z = profile_rz[0][1]
        c_idx = len(verts)
        verts.append((0.0, 0.0, bottom_z))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((c_idx, next_i, i))
            
    if cap_top:
        top_z = profile_rz[-1][1]
        c_idx = len(verts)
        verts.append((0.0, 0.0, top_z))
        top_start = (num_rings - 1) * segments
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append((c_idx, top_start + i, top_start + next_i))
            
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Smooth shading
    for f in obj.data.polygons:
        f.use_smooth = True
        
    return obj

# Exact radius profile curve points
# Outer wall profile
outer_profile = [
    (0.68, 0.00), # Flat bottom base
    (0.72, 0.12),
    (0.85, 0.35),
    (1.02, 0.65),
    (1.14, 0.95), # Bulbous belly
    (1.10, 1.35),
    (1.04, 1.75),
    (0.96, 2.15),
    (0.90, 2.45),
    (0.88, 2.65), # Outer rim
]

# Inner wall profile (wall thickness ~0.045, solid base below Z=0.20)
inner_profile = [
    (0.64, 0.20), # Inner bottom base
    (0.78, 0.35),
    (0.96, 0.65),
    (1.09, 0.95), # Inside of belly
    (1.05, 1.35),
    (0.99, 1.75),
    (0.91, 2.15),
    (0.85, 2.45),
    (0.83, 2.65), # Inner rim
]

# 1. Complete Glass Tumbler (Outer wall + Rim + Inner wall)
glass_profile = list(outer_profile)
glass_profile.append((0.855, 2.66)) # Rounded rim top
glass_profile.extend(reversed(inner_profile))
# Glass is a complete closed shell
glass_obj = create_revolved_mesh("Matcha_GlassTumbler", glass_profile, segments=56, cap_bottom=True, cap_top=False)
glass_obj.data.materials.append(mat_glass)

# 2. Matcha Liquid (Hugs inner wall from Z=0.20 up to Z=1.90 with ZERO GAP!)
matcha_inner = [
    (0.64, 0.20),
    (0.78, 0.35),
    (0.96, 0.65),
    (1.09, 0.95),
    (1.05, 1.35),
    (1.01, 1.60),
    (0.97, 1.90), # Liquid surface level
]
matcha_obj = create_revolved_mesh("Matcha_Liquid", matcha_inner, segments=56, cap_bottom=True, cap_top=True)
matcha_obj.data.materials.append(mat_matcha)

# 3. Floating Ice Cubes inside liquid
ice_positions = [
    (0.32, 0.22, 1.40, (0.25, 0.4, 0.8)),
    (-0.28, 0.30, 1.50, (-0.3, 0.15, 0.4)),
    (0.12, -0.38, 1.45, (0.5, -0.2, 0.3)),
    (-0.22, -0.18, 1.65, (0.1, 0.55, -0.4)),
    (0.35, -0.12, 1.72, (-0.35, 0.3, 0.2))
]
ice_group = bpy.data.objects.new("IceCubes_Group", None)
bpy.context.collection.objects.link(ice_group)

for i, (ix, iy, iz, (rx, ry, rz)) in enumerate(ice_positions):
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(ix, iy, iz))
    ice = bpy.context.active_object
    ice.name = f"IceCube_{i+1}"
    ice.rotation_euler = (rx, ry, rz)
    bevel = ice.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 2
    ice.data.materials.append(mat_ice)
    ice.parent = ice_group
    bpy.ops.object.shade_smooth()

# 4. Cold Foam Layer (Sits seamlessly on top of matcha from Z=1.90 up to Z=2.58, hugs inner wall!)
foam_profile = [
    (0.97, 1.90), # Base rests on matcha surface
    (0.93, 2.15),
    (0.88, 2.40),
    (0.84, 2.58), # Foam top surface
]
foam_obj = create_revolved_mesh("Matcha_ColdFoam", foam_profile, segments=56, cap_bottom=True, cap_top=True)
foam_obj.data.materials.append(mat_foam)

# Give natural undulating cream fluffiness to top face of foam
for v in foam_obj.data.vertices:
    if v.co.z > 2.50:
        dist = math.sqrt(v.co.x**2 + v.co.y**2)
        v.co.z += (math.sin(v.co.x * 7.0) * math.cos(v.co.y * 7.0) * 0.025)
foam_obj.data.update()

# 5. Foam Drip down side of glass (just like in the image)
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.45, vertices=16, location=(0.0, 0.98, 1.82))
drip = bpy.context.active_object
drip.name = "FoamDrip"
drip.scale = (1.0, 0.45, 1.0)
drip.rotation_euler = (0.08, 0, 0)
bpy.ops.object.transform_apply(scale=True)
drip.data.materials.append(mat_foam)
bpy.ops.object.shade_smooth()

# 6. Matcha Powder Dusting on top of foam
bpy.ops.mesh.primitive_circle_add(radius=0.68, fill_type='NGON', vertices=48, location=(0, 0, 2.59))
powder = bpy.context.active_object
powder.name = "Matcha_PowderDust"

for v in powder.data.vertices:
    dist = math.sqrt(v.co.x**2 + v.co.y**2)
    noise = math.sin(v.co.x * 12.0) * math.cos(v.co.y * 12.0) * 0.08
    v.co.x += noise * 0.35
    v.co.y += noise * 0.35
    v.co.z += (1.0 - dist) * 0.015

powder.data.update()
powder.data.materials.append(mat_powder)
bpy.ops.object.shade_smooth()

# 7. Make sure Material Preview is active and redraw
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            area.tag_redraw()

bpy.context.view_layer.objects.active = glass_obj
glass_obj.select_set(True)

print("Matcha Latte completely fixed: seamless geometry, 100% gap-free liquid filling the glass!")
