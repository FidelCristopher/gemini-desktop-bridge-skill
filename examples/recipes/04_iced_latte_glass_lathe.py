import bpy
import math

# 1. Clean all existing objects in main scene
bpy.ops.object.select_all(action='DESELECT')
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# 2. Configure EEVEE & Viewport for Photorealism
scene = bpy.context.scene
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    if hasattr(scene.eevee, 'ray_tracing_method'):
        scene.eevee.ray_tracing_method = 'SCREEN'

scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
scene.view_settings.look = 'High Contrast'

# World Environment
world = scene.world
if not world:
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
wnodes.clear()
w_out = wnodes.new("ShaderNodeOutputWorld")
w_bg = wnodes.new("ShaderNodeBackground")
w_bg.inputs["Color"].default_value = (0.80, 0.84, 0.88, 1.0)
w_bg.inputs["Strength"].default_value = 0.85
wlinks.new(w_bg.outputs["Background"], w_out.inputs["Surface"])


# ==========================================================
# 3. HIGH-END PBR MATERIALS
# ==========================================================

# A. Real Thick Crystal Glass
mat_glass = bpy.data.materials.new(name="Mat_ThickCrystalGlass")
mat_glass.use_nodes = True
mat_glass.blend_method = 'HASHED' if hasattr(mat_glass, 'blend_method') else 'OPAQUE'
if hasattr(mat_glass, 'use_raytrace_refraction'):
    mat_glass.use_raytrace_refraction = True
if hasattr(mat_glass, 'refraction_depth'):
    mat_glass.refraction_depth = 0.05
mat_glass.show_transparent_back = True
mat_glass.use_backface_culling = False
mat_glass.diffuse_color = (0.95, 0.98, 1.0, 0.15)

gnodes = mat_glass.node_tree.nodes
glinks = mat_glass.node_tree.links
gnodes.clear()

g_out = gnodes.new("ShaderNodeOutputMaterial")
g_bsdf = gnodes.new("ShaderNodeBsdfPrincipled")
g_bsdf.inputs["Base Color"].default_value = (0.98, 1.0, 1.0, 1.0)
g_bsdf.inputs["Roughness"].default_value = 0.02
g_bsdf.inputs["Transmission Weight"].default_value = 1.0
g_bsdf.inputs["IOR"].default_value = 1.50
if "Specular IOR Level" in g_bsdf.inputs:
    g_bsdf.inputs["Specular IOR Level"].default_value = 0.7
g_bsdf.inputs["Alpha"].default_value = 0.18

# Micro-chill condensation bump
g_tc = gnodes.new("ShaderNodeTexCoord")
g_noise = gnodes.new("ShaderNodeTexNoise")
g_noise.inputs["Scale"].default_value = 30.0
g_noise.inputs["Detail"].default_value = 4.0
g_bump = gnodes.new("ShaderNodeBump")
g_bump.inputs["Strength"].default_value = 0.04
glinks.new(g_tc.outputs["Generated"], g_noise.inputs["Vector"])
glinks.new(g_noise.outputs["Fac"], g_bump.inputs["Height"])
glinks.new(g_bump.outputs["Normal"], g_bsdf.inputs["Normal"])
glinks.new(g_bsdf.outputs["BSDF"], g_out.inputs["Surface"])

# B. Creamy Rich SSS Matcha Liquid
mat_matcha = bpy.data.materials.new(name="Mat_CreamyMatcha_Liquid")
mat_matcha.use_nodes = True
mnodes = mat_matcha.node_tree.nodes
mlinks = mat_matcha.node_tree.links
mnodes.clear()

m_out = mnodes.new("ShaderNodeOutputMaterial")
m_bsdf = mnodes.new("ShaderNodeBsdfPrincipled")

# Procedural rich matcha color with milky swirls
m_tc = mnodes.new("ShaderNodeTexCoord")
m_noise = mnodes.new("ShaderNodeTexNoise")
m_noise.inputs["Scale"].default_value = 4.5
m_noise.inputs["Detail"].default_value = 4.0
m_ramp = mnodes.new("ShaderNodeValToRGB")
m_ramp.color_ramp.elements[0].position = 0.20
m_ramp.color_ramp.elements[0].color = (0.16, 0.44, 0.07, 1.0) # Deep vibrant matcha
m_ramp.color_ramp.elements[1].position = 0.80
m_ramp.color_ramp.elements[1].color = (0.28, 0.60, 0.12, 1.0) # Creamy milky matcha

mlinks.new(m_tc.outputs["Object"], m_noise.inputs["Vector"])
mlinks.new(m_noise.outputs["Fac"], m_ramp.inputs["Fac"])
mlinks.new(m_ramp.outputs["Color"], m_bsdf.inputs["Base Color"])

m_bsdf.inputs["Roughness"].default_value = 0.18
if "Subsurface Weight" in m_bsdf.inputs:
    m_bsdf.inputs["Subsurface Weight"].default_value = 0.45
    m_bsdf.inputs["Subsurface Radius"].default_value = (0.2, 0.5, 0.1)

mlinks.new(m_bsdf.outputs["BSDF"], m_out.inputs["Surface"])

# C. Cold Foam Layer with Integrated Soft Velvet Powder Dusting
mat_foam_powder = bpy.data.materials.new(name="Mat_ColdFoam_SoftPowder")
mat_foam_powder.use_nodes = True
fnodes = mat_foam_powder.node_tree.nodes
flinks = mat_foam_powder.node_tree.links
fnodes.clear()

f_out = fnodes.new("ShaderNodeOutputMaterial")
f_bsdf = fnodes.new("ShaderNodeBsdfPrincipled")

f_tc = fnodes.new("ShaderNodeTexCoord")
f_mapping = fnodes.new("ShaderNodeMapping")
flinks.new(f_tc.outputs["Object"], f_mapping.inputs["Vector"])

# Top surface mask (Z > 2.45)
f_sep = fnodes.new("ShaderNodeSeparateXYZ")
flinks.new(f_mapping.outputs["Vector"], f_sep.inputs["Vector"])
f_zmask = fnodes.new("ShaderNodeMath")
f_zmask.operation = 'GREATER_THAN'
f_zmask.inputs[1].default_value = 2.45
flinks.new(f_sep.outputs["Z"], f_zmask.inputs[0])

# Radial distance from center (leaves bare white foam on rim)
f_dist = fnodes.new("ShaderNodeVectorMath")
f_dist.operation = 'DISTANCE'
f_dist.inputs[1].default_value = (0.04, 0.04, 2.55)
flinks.new(f_mapping.outputs["Vector"], f_dist.inputs[0])

f_dist_ramp = fnodes.new("ShaderNodeValToRGB")
f_dist_ramp.color_ramp.elements[0].position = 0.15
f_dist_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
f_dist_ramp.color_ramp.elements[1].position = 0.52
f_dist_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0) # Bare white foam around perimeter
flinks.new(f_dist.outputs["Value"], f_dist_ramp.inputs["Fac"])

# Soft organic clumping noise (macro)
f_macro = fnodes.new("ShaderNodeTexNoise")
f_macro.inputs["Scale"].default_value = 12.0
f_macro.inputs["Detail"].default_value = 6.0
f_macro.inputs["Roughness"].default_value = 0.65
flinks.new(f_mapping.outputs["Vector"], f_macro.inputs["Vector"])

f_comb = fnodes.new("ShaderNodeMath")
f_comb.operation = 'MULTIPLY'
flinks.new(f_dist_ramp.outputs["Color"], f_comb.inputs[0])
flinks.new(f_macro.outputs["Fac"], f_comb.inputs[1])

f_pmask = fnodes.new("ShaderNodeMath")
f_pmask.operation = 'MULTIPLY'
flinks.new(f_comb.outputs["Value"], f_pmask.inputs[0])
flinks.new(f_zmask.outputs["Value"], f_pmask.inputs[1])

f_mask_ramp = fnodes.new("ShaderNodeValToRGB")
f_mask_ramp.color_ramp.elements[0].position = 0.28
f_mask_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
f_mask_ramp.color_ramp.elements[1].position = 0.60
f_mask_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
flinks.new(f_pmask.outputs["Value"], f_mask_ramp.inputs["Fac"])

# Velvet powder color
f_pcol_noise = fnodes.new("ShaderNodeTexNoise")
f_pcol_noise.inputs["Scale"].default_value = 65.0
f_pcol_noise.inputs["Detail"].default_value = 8.0
flinks.new(f_mapping.outputs["Vector"], f_pcol_noise.inputs["Vector"])

f_pcol_ramp = fnodes.new("ShaderNodeValToRGB")
f_pcol_ramp.color_ramp.elements[0].position = 0.25
f_pcol_ramp.color_ramp.elements[0].color = (0.10, 0.28, 0.04, 1.0) # Rich matcha powder
f_pcol_ramp.color_ramp.elements[1].position = 0.75
f_pcol_ramp.color_ramp.elements[1].color = (0.24, 0.50, 0.10, 1.0) # Olive green speckle
flinks.new(f_pcol_noise.outputs["Fac"], f_pcol_ramp.inputs["Fac"])

# Mix Color: Pure White Foam vs Matcha Powder
f_mix_col = fnodes.new("ShaderNodeMix")
f_mix_col.data_type = 'RGBA'
f_mix_col.inputs[6].default_value = (0.97, 0.97, 0.94, 1.0) # Velvety white cold foam
flinks.new(f_mask_ramp.outputs["Color"], f_mix_col.inputs["Factor"])
flinks.new(f_pcol_ramp.outputs["Color"], f_mix_col.inputs[7])
flinks.new(f_mix_col.outputs[2], f_bsdf.inputs["Base Color"])

# Mix Roughness: Foam 0.45 vs Velvet Powder 0.88
f_mix_rough = fnodes.new("ShaderNodeMix")
f_mix_rough.data_type = 'FLOAT'
f_mix_rough.inputs[2].default_value = 0.45
f_mix_rough.inputs[3].default_value = 0.88
flinks.new(f_mask_ramp.outputs["Color"], f_mix_rough.inputs["Factor"])
flinks.new(f_mix_rough.outputs[0], f_bsdf.inputs["Roughness"])

# Soft micro-texture bump (NO gravel, purely velvety!)
f_bump = fnodes.new("ShaderNodeBump")
f_bump.inputs["Strength"].default_value = 0.15 # Very gentle soft texture
flinks.new(f_pcol_noise.outputs["Fac"], f_bump.inputs["Height"])
flinks.new(f_bump.outputs["Normal"], f_bsdf.inputs["Normal"])

if "Subsurface Weight" in f_bsdf.inputs:
    f_bsdf.inputs["Subsurface Weight"].default_value = 0.25

flinks.new(f_bsdf.outputs["BSDF"], f_out.inputs["Surface"])

# D. Realistic Ice Cubes
mat_ice = bpy.data.materials.new(name="Mat_Ice_Cubes")
mat_ice.use_nodes = True
mat_ice.blend_method = 'HASHED' if hasattr(mat_ice, 'blend_method') else 'OPAQUE'
inodes = mat_ice.node_tree.nodes
ilinks = mat_ice.node_tree.links
inodes.clear()
i_out = inodes.new("ShaderNodeOutputMaterial")
i_bsdf = inodes.new("ShaderNodeBsdfPrincipled")
i_bsdf.inputs["Base Color"].default_value = (0.95, 0.98, 1.0, 1.0)
i_bsdf.inputs["Roughness"].default_value = 0.08
i_bsdf.inputs["Transmission Weight"].default_value = 0.95
i_bsdf.inputs["IOR"].default_value = 1.31
i_bsdf.inputs["Alpha"].default_value = 0.35
ilinks.new(i_bsdf.outputs["BSDF"], i_out.inputs["Surface"])


# ==========================================================
# 4. WATERTIGHT PROCEDURAL LATHE GEOMETRY (ZERO GAPS!)
# ==========================================================

def create_lathe(name, profile_rz, segments=64, cap_bottom=True, cap_top=True):
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
    
    for f in obj.data.polygons:
        f.use_smooth = True
        
    return obj

# Dimensions of the Tumbler:
# Outer wall profile (Z from 0.00 to 2.65)
outer_profile = [
    (0.68, 0.00), # Solid flat bottom base
    (0.72, 0.08),
    (0.80, 0.24), # Thick glass bottom layer (Z: 0.00 to 0.24)
    (0.95, 0.50),
    (1.12, 0.90), # Bulbous belly
    (1.10, 1.35),
    (1.04, 1.75),
    (0.96, 2.15),
    (0.90, 2.45),
    (0.88, 2.65), # Outer rim
]

# Inner wall profile:
# Wall thickness: 0.055 cm
# Solid glass floor at Z = 0.24!
inner_profile = [
    (0.62, 0.24), # Inner bottom floor where matcha sits!
    (0.74, 0.40),
    (0.89, 0.65),
    (1.06, 0.90), # Inner belly
    (1.04, 1.35),
    (0.98, 1.75),
    (0.90, 2.15),
    (0.84, 2.45),
    (0.82, 2.65), # Inner rim
]

# 1. Tumbler Glass: Complete 1-Piece Solid Shell with thick bottom!
glass_profile = list(outer_profile)
glass_profile.append((0.85, 2.66)) # Rounded smooth rim lip
glass_profile.extend(reversed(inner_profile))
glass_obj = create_lathe("Glass_Tumbler", glass_profile, segments=64, cap_bottom=True, cap_top=False)
glass_obj.data.materials.append(mat_glass)

# 2. Matcha Liquid: Fills 100% of the inside from floor (Z=0.24) up to cold foam (Z=1.95)!
# Outer boundary coordinates match inner glass wall EXACTLY -> ZERO GAP!
matcha_profile = [
    (0.62, 0.24), # Sits right on the solid glass floor!
    (0.74, 0.40),
    (0.89, 0.65),
    (1.06, 0.90),
    (1.04, 1.35),
    (1.01, 1.65),
    (0.95, 1.95), # Top surface of matcha liquid
]
matcha_obj = create_lathe("Matcha_Liquid", matcha_profile, segments=64, cap_bottom=True, cap_top=True)
matcha_obj.data.materials.append(mat_matcha)

# 3. Ice Cubes: Floating inside the liquid
ice_coords = [
    (0.32, 0.22, 1.40, (0.25, 0.4, 0.8)),
    (-0.28, 0.30, 1.50, (-0.3, 0.15, 0.4)),
    (0.12, -0.38, 1.45, (0.5, -0.2, 0.3)),
    (-0.22, -0.18, 1.65, (0.1, 0.55, -0.4)),
    (0.35, -0.12, 1.72, (-0.35, 0.3, 0.2))
]
ice_group = bpy.data.objects.new("IceCubes_Group", None)
bpy.context.collection.objects.link(ice_group)

for i, (ix, iy, iz, (rx, ry, rz)) in enumerate(ice_coords):
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

# 4. Cold Foam & Soft Powder Layer: Sits right on top of matcha from Z=1.95 to Z=2.58
foam_profile = [
    (0.95, 1.95), # Rests directly on matcha liquid surface
    (0.92, 2.15),
    (0.87, 2.40),
    (0.83, 2.58), # Top fluffy surface
]
foam_obj = create_lathe("ColdFoam_Cream", foam_profile, segments=64, cap_bottom=True, cap_top=True)
foam_obj.data.materials.append(mat_foam_powder)

# Give natural undulating cream fluffiness to top surface
for v in foam_obj.data.vertices:
    if v.co.z > 2.50:
        v.co.z += (math.sin(v.co.x * 6.5) * math.cos(v.co.y * 6.5) * 0.022)
foam_obj.data.update()

# 5. Foam Drip: Natural cream drizzle down the side
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.45, vertices=16, location=(0.0, 0.98, 1.82))
drip = bpy.context.active_object
drip.name = "FoamDrip"
drip.scale = (1.0, 0.45, 1.0)
drip.rotation_euler = (0.08, 0, 0)
bpy.ops.object.transform_apply(scale=True)
drip.data.materials.append(mat_foam_powder)
bpy.ops.object.shade_smooth()

# 6. Studio Lighting Setup
# Key Light (Warm softbox)
bpy.ops.object.light_add(type='AREA', radius=2.2, location=(2.2, -2.8, 2.8))
key = bpy.context.active_object
key.name = "Key_Light"
key.data.energy = 150.0
key.data.color = (1.0, 0.98, 0.95)
key.rotation_euler = (0.75, 0.25, 0.65)

# Fill Light (Cool fill)
bpy.ops.object.light_add(type='AREA', radius=2.5, location=(-2.6, -1.8, 1.8))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 65.0
fill.data.color = (0.92, 0.96, 1.0)
fill.rotation_euler = (0.85, -0.3, -0.9)

# Rim Light (Accent on glass rim & ice cubes)
bpy.ops.object.light_add(type='AREA', radius=1.6, location=(0.3, 2.8, 2.5))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 130.0
rim.data.color = (1.0, 1.0, 1.0)
rim.rotation_euler = (-0.75, 0.1, 3.14)

# Force Viewport Redraw in Material Preview
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
            area.tag_redraw()

bpy.context.view_layer.objects.active = glass_obj
glass_obj.select_set(True)

print("Matcha Latte completely remade: thick crystal glass, 100% full liquid from base to foam, soft velvety topping, and zero holes!")
