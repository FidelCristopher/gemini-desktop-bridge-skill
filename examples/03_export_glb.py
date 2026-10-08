import bpy
import os

# Clean existing meshes
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()

# Procedural gem/crystal
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.2, location=(0, 0, 1.2))
crystal = bpy.context.active_object
crystal.name = "MagicCrystal"
crystal.scale = (0.8, 0.8, 1.6)
bpy.ops.object.transform_apply(scale=True)

# Emissive crystal material
mat = bpy.data.materials.new(name="CrystalGlow")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.2, 0.8, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.1
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (0.1, 0.6, 1.0, 1.0)
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 2.0

crystal.data.materials.append(mat)

# Export to GLB in user's home folder
export_path = os.path.expanduser("~/.blender_bridge/crystal_model.glb")
os.makedirs(os.path.dirname(export_path), exist_ok=True)

bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    use_selection=False
)

print(f"✨ Model created and exported to GLB: {export_path}")
