---
name: blender-bridge
description: Generate and manipulate 3D models, scenes, materials, and animations directly inside an active Blender desktop session in real-time, and export to GLB/GLTF. Use whenever the user asks to create 3D assets, model objects in Blender, or render 3D scenes.
---

# Blender Desktop Bridge Skill

This skill allows the agent to generate 3D models, procedural assets, PBR materials, lighting, and animations directly inside a running Blender desktop session in real-time.

## How the Bridge Works

1. **Blender Listener:** An active listener script (`blender_bridge.py`) runs inside the user's Blender desktop session. It receives Python `bpy` scripts via:
   - HTTP POST (`http://localhost:9876/execute`)
   - Shared file watcher (`~/.blender_bridge/task.py`)
2. **Sender Utility:** The agent executes `python3 <skill_dir>/scripts/send_to_blender.py` with generated Python code.
3. **Execution & Immediate Redraw:** Blender runs the code in its main thread using `bpy.app.timers` and immediately redraws the 3D Viewport.

## Execution Workflow

Whenever the user asks to generate or modify a 3D asset in Blender:

1. **Image Reference (Optional):**
   - If the user provides a path to an image file (e.g., `.png`, `.jpg`, `.webp`), use the `read` tool to inspect the image.
   - Deconstruct the image visually: identify primitive geometric components, proportions, color palette, roughness/metallicity, and lighting.
   - Translate the visual breakdown into corresponding Blender meshes and PBR materials.

2. **Write the Blender Python Script:**
   - Create a temporary script file (e.g., `/tmp/blender_task.py`).
   - Use standard Blender Python API (`bpy`).
3. **Execute via Sender Tool:**
   ```bash
   python3 ~/.pi/agent/skills/blender-bridge/scripts/send_to_blender.py --file /tmp/blender_task.py
   ```
4. **Check Output:**
   - If success: inform the user that the model is now visible in their Blender viewport.
   - If connection error: prompt the user to make sure `blender_bridge.py` is running in Blender.

## Blender `bpy` Scripting Guidelines

### 1. Scene Management
When creating a new model from scratch, clean up existing default shapes or create an organized collection:
```python
import bpy

# Optional: Clean existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.ops.object.delete()
```

### 2. Creating PBR Materials
Always create PBR materials using Principled BSDF nodes:
```python
def create_pbr_material(name, color_rgba, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Blender 4.0+ socket names
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color_rgba
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
    return mat
```

### 3. Assigning Materials to Objects
```python
# Create mesh and assign material
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
obj = bpy.context.active_object
obj.name = "MyObject"
mat = create_pbr_material("RedGlossy", (0.8, 0.1, 0.1, 1.0), metallic=0.2, roughness=0.2)
obj.data.materials.append(mat)
```

### 4. Modifiers & Smooth Shading
- Smooth shading: `bpy.ops.object.shade_smooth()`
- Subsurf modifier:
```python
subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2
```
- Bevel modifier:
```python
bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.05
bevel.segments = 3
```

### 5. GLB / glTF Exporting
When the user specifically requests a `.glb` or `.gltf` file:
```python
import os
export_path = os.path.expanduser("~/output_model.glb")
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    use_selection=False
)
print(f"Exported to {export_path}")
```
