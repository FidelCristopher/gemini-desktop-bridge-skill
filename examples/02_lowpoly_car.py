import bpy

# Clean existing meshes
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()

def make_mat(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

car_body_mat = make_mat("CarBodyRed", (0.85, 0.08, 0.08, 1.0), 0.3, 0.25)
cabin_mat = make_mat("CarGlass", (0.1, 0.2, 0.3, 1.0), 0.1, 0.1)
wheel_mat = make_mat("RubberBlack", (0.05, 0.05, 0.05, 1.0), 0.0, 0.8)
rim_mat = make_mat("RimSilver", (0.8, 0.8, 0.8, 1.0), 0.9, 0.2)
light_mat = make_mat("HeadlightYellow", (1.0, 0.9, 0.3, 1.0), 0.0, 0.1)

# Lower Chassis
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.6))
chassis = bpy.context.active_object
chassis.name = "CarChassis"
chassis.scale = (3.6, 1.8, 0.6)
bpy.ops.object.transform_apply(scale=True)
chassis.data.materials.append(car_body_mat)

# Cabin
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.2, 0, 1.25))
cabin = bpy.context.active_object
cabin.name = "CarCabin"
cabin.scale = (1.8, 1.5, 0.7)
bpy.ops.object.transform_apply(scale=True)
cabin.data.materials.append(cabin_mat)

# 4 Wheels
wheel_positions = [
    (1.1, 1.0, 0.4),
    (1.1, -1.0, 0.4),
    (-1.1, 1.0, 0.4),
    (-1.1, -1.0, 0.4),
]

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.42, depth=0.3, vertices=16,
        location=pos,
        rotation=(1.5708, 0, 0)
    )
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    wheel.data.materials.append(wheel_mat)

# Headlights
for y_pos in (0.6, -0.6):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.18, depth=0.1, vertices=16,
        location=(1.82, y_pos, 0.6),
        rotation=(0, 1.5708, 0)
    )
    light = bpy.context.active_object
    light.name = f"Headlight_{y_pos}"
    light.data.materials.append(light_mat)

print("🚗 Low-poly car created successfully!")
