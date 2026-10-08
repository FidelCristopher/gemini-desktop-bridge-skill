import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()

def make_mat(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

ceramic_mat = make_mat("CeramicWhite", (0.9, 0.9, 0.9, 1.0), 0.0, 0.15)
coffee_mat = make_mat("CoffeeLiquid", (0.08, 0.04, 0.02, 1.0), 0.1, 0.2)

# Cup body (Cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=2.0, vertices=32, location=(0, 0, 1.0))
cup = bpy.context.active_object
cup.name = "CoffeeCup"
cup.data.materials.append(ceramic_mat)

# Solidify modifier to give thickness
solid = cup.modifiers.new(name="Solidify", type='SOLIDIFY')
solid.thickness = 0.12
solid.offset = -1

# Bevel modifier for smooth rim
bevel = cup.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.03
bevel.segments = 3

# Handle (Torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.7,
    minor_radius=0.15,
    major_segments=24,
    minor_segments=12,
    location=(1.0, 0, 1.0),
    rotation=(0, math.pi / 2, 0)
)
handle = bpy.context.active_object
handle.name = "CupHandle"
handle.data.materials.append(ceramic_mat)

# Coffee liquid (Cylinder inside)
bpy.ops.mesh.primitive_cylinder_add(radius=0.86, depth=0.1, vertices=32, location=(0, 0, 1.5))
coffee = bpy.context.active_object
coffee.name = "CoffeeLiquid"
coffee.data.materials.append(coffee_mat)

print("Coffee cup created successfully!")
