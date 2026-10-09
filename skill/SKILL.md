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

Whenever the user invokes the skill or asks to generate 3D assets in Blender:

1. **Reference Input Options:**
   If the user asks to model from an image or if they want to provide an image reference:
   Offer or execute one of these input methods:
   - **File Explorer GUI Dialog:** Run `python3 <skill_dir>/scripts/pick_image.py --dialog` to open a native Windows/system file selector window where the user can click and select an image file.
   - **System Clipboard:** Run `python3 <skill_dir>/scripts/pick_image.py --clipboard` if the user copied an image or took a screenshot (e.g., Win + Shift + S).
   - **Direct File Path:** If the user already provided an image path, proceed directly.
   - **Direct Text Prompt:** If the user provided a text description, proceed directly to modeling.

2. **Image Inspection & Deconstruction (When Image is Provided):**
   - Use the `read` tool on the image path returned by `pick_image.py` or provided by user.
   - Visually deconstruct the reference: primitive geometric meshes, proportions, color palette (RGB/Hex), surface roughness/metallicity, and sub-components.
   - Formulate the corresponding Blender Python `bpy` script.

3. **Write the Blender Python Script:**
   - Create a temporary script file (e.g., `/tmp/blender_task.py`).
   - Use standard Blender Python API (`bpy`).
4. **Execute via Sender Tool:**
   ```bash
   python3 ~/.pi/agent/skills/blender-bridge/scripts/send_to_blender.py --file /tmp/blender_task.py
   ```
5. **Check Output:**
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

## Continuous Learning & Revision Recording Scheme

Whenever the user requests a correction, refinement, or reports an issue/artifact with a generated 3D model:

1. **Diagnose Root Cause:** Determine why the visual artifact occurred (e.g., modifier collapse, lighting, missing refraction, node type mismatches).
2. **Apply Live Correction:** Generate the corrected `bpy` script, test it, and update Blender desktop immediately.
3. **Record Lesson Learned (Strict English Auto-Translation):**
   - Automatically extract the generalized rule, technical constraint, and modeling best practices.
   - **MANDATORY AUTO-TRANSLATION TO ENGLISH:** Regardless of the language used by the user in the prompt or conversation (e.g., Indonesian, Japanese, etc.), **ALWAYS automatically translate, synthesize, and record every new lesson, guideline, and code comment strictly into clear, professional technical English.** This guarantees that `SKILL.md` remains 100% globally consistent and language-standardized.
   - Append the newly synthesized rule to the `## Lessons Learned & Best Practices (Memory Bank)` section below.
4. **Save Reusable Recipe:** If the object represents a distinct category (e.g., drink container, vehicle, procedural architecture), save the verified script into `examples/recipes/` with all comments and documentation written in English.

This ensures that the agent permanently learns from every mistake across all future sessions without ever needing heavy model retraining.

## Lessons Learned & Best Practices (Memory Bank)

### 1. Liquids in Containers & Glasses (Zero-Gap Watertight Rule)
- **Problem:** Applying a Subdivision Surface modifier (`SUBSURF`) to a standalone cylinder liquid causes the top and bottom circular caps to shrink/collapse inward into an egg/capsule shape, leaving an unnatural air gap between the liquid and the glass wall.
- **Rule:** Never use raw Subsurf on cylinder liquids inside containers. Always generate liquid geometry using a shared **Lathe / Revolved Profile** whose outer radius matches the container's inner wall coordinates exactly. Both liquid and foam must hug the inner glass wall seamlessly from base to surface.

### 2. Glass Transparency & Visibility in EEVEE / Material Preview
- **Problem:** By default in EEVEE Material Preview, pure glass with `Transmission = 1.0` can render as an opaque reflective shell, obscuring the liquid, ice cubes, and contents inside.
- **Rule:** Always configure transparent glass materials with:
  - `mat.blend_method = 'BLEND'`
  - `mat.use_raytrace_refraction = True` (if supported by Blender version)
  - `bsdf.inputs['Alpha'].default_value = 0.20` to `0.25`
  - Viewport display color: `mat.diffuse_color = (0.95, 0.98, 1.0, 0.20)`
  This ensures the glass is crystal clear in the viewport and all internal contents are vividly visible.

### 3. Creamy Beverages & Organic Foam Texturing
- **Rule for Liquids:** For milky beverages (matcha latte, milk tea, coffee), add Subsurface Scattering (`Subsurface Weight: 0.35 - 0.45`, `Roughness: ~0.22`) and a procedural Noise Texture (`Scale: 4 - 6`) piped through a ColorRamp (`ShaderNodeValToRGB`) for subtle swirl variations.
- **Rule for Foam/Cream:** Use high-frequency Noise (`Scale: 50.0`, `Detail: 8.0`) connected to a Bump node (`Strength: 0.35`) into the Principled BSDF `Normal` socket to produce realistic micro-bubble foam porosity.
- **Rule for Powder Dusting:** Use micro-noise (`Scale: 80.0`) with a Bump node (`Strength: 0.6`) and ColorRamp (`ShaderNodeValToRGB`) to produce granular powder flakes instead of a flat disc.

### 4. Blender Shader Node Python API Identifiers
- Principled BSDF node type is `'ShaderNodeBsdfPrincipled'` (NOT `'ShaderNodePrincipledBSDF'`).
- ColorRamp node type is `'ShaderNodeValToRGB'` (NOT `'ShaderNodeColorRamp'`).
- In Blender 4.0+, `mat.use_nodes = True` automatically generates `'Principled BSDF'` and `'Material Output'`. Always access them via `nodes.get("Principled BSDF")` rather than recreating them from scratch.

### 5. Dusted Powder Toppings (Matcha, Cocoa, Cinnamon)
- **Problem:** Modeling powdered toppings as a flat standalone disc/circle creates an artificial floating cut-out, unnatural sharp borders, and completely obscures the cream/foam.
- **Rule:** Never use flat solid discs for dusted powder toppings:
  1. **Integrated Procedural Mask:** Blend the powder directly onto the top surface of the cream/foam shader using a radial falloff multiplied by multi-octave noise.
  2. **Selective Coverage:** Concentrate powder toward the center/upper-middle, leaving clear bare cream/foam visible around the outer perimeter and rims.
  3. **Chalky Matte vs Velvety Foam:** Powder must have high roughness (`~0.95`) and strong micro-noise bump relief (`Strength: 0.7+`) contrasting against the softer foam underneath (`Roughness: 0.45`).

### 6. Photorealistic Beverage Structure & Soft Powdery Velvet Toppings (Showcase Standard)
- **Problem:** Adding sharp or discrete 3D particles to powder toppings can look like rigid gravel, stones, or pebbles instead of soft, fluffy matcha/cocoa powder.
- **Rule:**
  1. **Soft Velvet Powder:** Never use chunky stone/pebble particles for food powders. Powder must look soft and seamlessly dusted: use smooth undulating organic mesh folds with soft micro-gradient dusting, high roughness (`0.85 - 0.90`), and low specular (`~0.2`) to simulate velvety light absorption.
  2. **Layered Asset Hierarchy:** Separate beverage assets into clean functional layers (`base_glass`, `liquid_contents`, `topping_cream`) so each layer can have independent optical properties (crisp glass reflection vs milky subsurface vs matte cream).
  3. **Studio 3-Point Lighting:** Always illuminate beverage scenes with a 3-point lighting setup (Key Light, Fill Light, Rim Light) to make glass specular reflections, ice depth, and rich beverage colors pop in the viewport.

### 7. Photorealistic Optical Glass & Separated Material Shaders
- **Problem:** Multi-mesh imports often share a single generic material slot. If the glass tumbler shares the same material as the liquid/topping, the glass renders as an opaque plastic shell (`Roughness ~0.85, Transmission 0.0`), losing all transparency, Fresnel reflection, and refraction.
- **Rule:**
  1. **Independent Shader Assignment:** Always split materials into separate specialized shaders:
     - **Optical Glass (`base_glass`):** Dedicated glass shader with `Transmission: 1.0`, `Roughness: 0.025`, `IOR: 1.50`, `Alpha: 0.18`, and subtle micro-condensation bump (`Strength: ~0.05`).
     - **Creamy Liquid (`matcha_isi`):** Boost texture saturation/contrast, set `Roughness: 0.18`, and add `Subsurface Weight: 0.45` (`Subsurface Radius: (0.2, 0.5, 0.1)`) so light scatters realistically through the liquid and ice.
     - **Velvety Topping (`matcha_topping`):** High diffuse roughness (`0.88`), low specular (`0.15`), and ultra-fine micro-grain bump (`Strength: 0.12`) for a soft powder feel.
  2. **Enable EEVEE Real-Time Raytracing:** In Blender 5.x / 4.2+, enable `scene.eevee.use_raytracing = True`, `mat.use_raytrace_refraction = True`, and set `refraction_depth = 0.04`.
  3. **Studio World Environment:** Provide an active ambient World background (`Strength: ~0.85`) so glass surfaces have environment light to reflect, and enable `use_scene_lights = True` and `use_scene_world = True` in 3D viewport shading.

### 8. Handling 3D Scan / Extracted Assets (Open Base Hole Repair)
- **Problem:** 3D scan or photogrammetry assets (e.g. models captured sitting on a tabletop) often have open, unmeshed boundary seams at the bottom. When rendered with an opaque material, the missing base is hidden; however, applying a transparent optical glass shader immediately exposes the open void, making the bottom of the glass look hollow/broken.
- **Rule:**
  1. **Inspect for Open Boundaries:** Whenever assigning transparent glass materials to imported assets, verify whether the mesh is open at the base (`is_boundary` edges).
  2. **Construct Solid Beveled Base:** Seal open bottom loops by creating a solid beveled glass bottom disc matching the base diameter and joining it directly into the glass mesh to simulate real thick tumbler glassware.
  3. **Avoid Backface Clipping:** Set glass materials to `blend_method = 'HASHED'` and ensure backface culling is disabled (`show_transparent_back = True`) to maintain full depth perception and eliminate angle-dependent disappearing faces.

