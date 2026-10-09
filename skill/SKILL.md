---
name: blender-bridge
description: Live Blender 3D desktop bridge. On activation or start, ALWAYS STOP and immediately ask the user the 3 input options (1. Local Image via File Explorer, 2. File Path, 3. Text Prompt) before writing any code. Do NOT auto-generate any default object.
---

# Blender Desktop Bridge Skill

## ABSOLUTE CONTEXT-RESET RULE: TREAT EVERY INVOCATION AS A FRESH BLANK-SLATE!

**CRITICAL OVERRIDE INSTRUCTION FOR THE AGENT (APPLIES TO FIRST RUN AND ANY RE-INVOCATION):**
Whenever this skill is triggered, invoked (e.g. via `/skill blender-bridge`, `/skill gemini-bridge`, or `/skill gemini-desktop-bridge`), or selected at ANY point—whether at the very beginning of a session or in the middle of an ongoing conversation:

1. **FORBIDDEN: DO NOT INHERIT OR ITERATE ON PREVIOUS CHAT CONTEXT:**
   - **Completely IGNORE any previous 3D model, object, task, or render discussed earlier in the chat history.**
   - **DO NOT** continue modifying, refining, or editing past objects (do NOT touch past chairs, drinks, fruits, or previous models).
   - **DO NOT** read old preview files (e.g. `preview.png`), do NOT write refinement scripts, and do NOT execute `send_to_blender.py` right away.

2. **MANDATORY: ALWAYS RESET AND PRESENT THE 3 INPUT OPTIONS:**
   - Every single time `/skill` is invoked, treat it as a brand-new, fresh interaction from scratch.
   - Your VERY FIRST AND ONLY response to the user must be to STOP immediately and present the 3 input options:

   "Halo! Gemini Desktop Blender Bridge aktif. Bagaimana Anda ingin memberikan referensi untuk model 3D baru?
   1. 📂 **Pilih Gambar dari Komputer (File Explorer)**: Membuka jendela dialog untuk memilih gambar referensi.
   2. 📁 **Ketik Path File Gambar**: Masukkan path file gambar secara langsung (misal: `C:\Users\...\gambar.png`).
   3. ✏️ **Deskripsi Teks / Prompt**: Jelaskan langsung objek 3D apa yang ingin Anda buat."

3. **WAIT FOR EXPLICIT USER RESPONSE:**
   - You MUST wait for the user to choose option 1, 2, or 3 before generating any code, writing any file, or touching Blender.

## How the Bridge Works

1. **Blender Listener:** An active listener script (`blender_bridge.py`) runs inside the user's Blender desktop session. It receives Python `bpy` scripts via:
   - HTTP POST (`http://localhost:9876/execute`)
   - Shared file watcher (`~/.blender_bridge/task.py`)
2. **Sender Utility:** The agent executes `python3 <skill_dir>/scripts/send_to_blender.py` with generated Python code.
3. **Execution & Immediate Redraw:** Blender runs the code in its main thread using `bpy.app.timers` and immediately redraws the 3D Viewport.

## Execution Workflow

Whenever the user invokes the skill or asks to generate 3D assets in Blender:

1. **Mandatory Input Triage (Always Offer the 3 Input Methods):**
   Whenever the user invokes this skill or asks to create/generate a 3D asset in Blender (unless they already provided the exact image path or full text specification upfront in their prompt), **ALWAYS ask the user to choose from these 3 options**:
   - **1. Pick Image from Local (File Explorer GUI):** The agent executes `python3 <skill_dir>/scripts/pick_image.py --dialog` to launch a native Windows/system File Explorer dialog so the user can easily click and select an image file with their mouse.
   - **2. Specify Image File Path:** The user provides a direct file path to an image file (e.g., `C:\Users\Pongo\Pictures\reference.png`).
   - **3. Text Prompt Description:** The user describes the desired 3D object directly using natural language text prompts (e.g., "Create a low-poly medieval chest").

   **Handling the Selection:**
   - If **Option 1** is selected: execute `pick_image.py --dialog`, capture the returned image path, and use the `read` tool to inspect the image.
   - If **Option 2** is selected: take the user-provided file path and use the `read` tool to inspect the image.
   - If **Option 3** is selected: proceed directly to modeling based on the user's text description.

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

6. **MANDATORY: Update `design.md` & `README.md` in Official Repository:**
   - Every time a 3D asset is generated, significantly refined, or modified, the agent **MUST** automatically update the documentation directly within the official repository:
     - **Target Repo (Windows):** `C:\Users\Pongo\gemini-desktop-bridge-skill\`
     - **Target Repo (WSL):** `/mnt/c/Users/Pongo/gemini-desktop-bridge-skill/` (and mirror to `~/gemini-desktop-bridge-skill/`)
     - **GitHub Remote:** `https://github.com/FidelCristopher/gemini-desktop-bridge-skill`
   - **Updating `design.md`:**
     - Append the complete architectural entry for the asset:
       - Asset Name / Title & Timestamp
       - Category & Source (text prompt or image reference file path)
       - Geometric Architecture (primitives, lathe profiles, modifiers, vertex count, key dimensions)
       - Shader & PBR Parameters (Base Color, Roughness, Metallic, Transmission, IOR, SSS, bump nodes)
       - Lighting Rig & Viewport Shading Settings
       - Refinement Notes & Specific Geometric Corrections applied
   - **Updating `README.md`:**
     - When new features, recipe scripts, or major asset categories are added, keep the repository `README.md` updated and in sync.
   - **Auto Git Commit:**
     - Stage and commit the updated `.md` files in the repository with a clean commit message (e.g., `docs: update design.md for <asset_name>`), ensuring the repository is always clean and ready for `git push origin main`.
   - **MANDATORY LANGUAGE:** All documentation entries in `design.md` and `README.md` must be written strictly in professional technical English.

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

### 5. Mandatory 2K PBR Texture Baking & GLB Exporting
When the user requests a `.glb` or `.gltf` file, or when exporting finished 3D assets:
**NEVER export raw procedural materials directly**, as glTF 2.0 strips procedural nodes resulting in empty `textures: []`.
Always execute automated 2K PBR texture baking (Base Color, Roughness, Tangent Normal Map) before export:
```bash
python3 <skill_dir>/scripts/bake_pbr_export_glb.py --object <ObjectName> --output "C:\Users\Pongo\Downloads\<filename>.glb" --resolution 2048
```
This automatically unwraps UVs, bakes 2K PBR bitmap textures via Cycles, re-wires a clean PBR Principled BSDF material, and exports a self-contained `.glb` binary with embedded textures and applied modifiers.

### 6. Mandatory 2K Standard Resolution (2048 x 2048) for All Renders & Previews
Whenever generating preview renders, OpenGL snapshots, product showcases, or texture bakes:
**ALWAYS set the render resolution to 2K (2048 x 2048)** (or 2K aspect ratio equivalent):
```python
bpy.context.scene.render.resolution_x = 2048
bpy.context.scene.render.resolution_y = 2048
```
Never generate low-resolution 512x512 or 800x800 renders. High-resolution 2K guarantees that fine procedural textures, glaze gradients, micro-bumps, and iron flecks are crisply resolved.


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

### 9. Full-Volume Beverage Filling & Solid Glass Wall/Base Thickness
- **Problem:** Attempting to patch sliced/cut 3D scan meshes often causes harsh color steps or hollow air gaps where the liquid fails to reach the glass base.
- **Rule:**
  1. **Solid 1-Piece Glass Shell:** Generate the glass tumbler as a contiguous revolved profile featuring a solid, thick crystal base ($Z = 0.00$ to $0.24$) and consistent realistic wall thickness (~0.055 units) with a rounded rim lip.
  2. **100% Watertight Liquid Volume:** Liquid geometry must start directly upon the inner solid glass floor ($Z = 0.24$) and fill upward to the foam line ($Z = 1.95$), matching the inner glass wall coordinates exactly.
  3. **Continuous Layering:** The cold foam layer sits directly on the liquid surface, extending upward to the top rim. This guarantees that the beverage fills 100% of the interior volume with zero holes, zero sharp edge artifacts, and realistic glass wall refraction.

### 10. Hybrid Asset Synthesis (Preserving High-Fidelity Textured Assets with Outer Glass Shells)
- **Insight:** When working with 3D models that already possess high-fidelity baked 4K textures and sculpted organic details, slicing them into disconnected layers can introduce seam gaps or destroy baked lighting.
- **Rule:**
  1. **Watertight Drink Core:** Keep the unified high-resolution textured asset as the internal drink core, heal any open bottom boundary scan holes, and add Subsurface Scattering (`Subsurface Weight: ~0.35`) so light penetrates the volume naturally.
  2. **Tailored Outer Glass Shell:** Build a dedicated, contiguous revolved glass tumbler mesh enveloping the drink core. Provide a thick solid crystal bottom base extending below the drink floor and uniform wall thickness with a rounded top rim lip.
  3. **Optical Refraction Layer:** Apply the crystal glass shader (`Transmission: 1.0`, `Roughness: 0.02`, `IOR: 1.50`, `Alpha: 0.18`, Raytrace Refraction enabled) to the outer shell. This achieves the best of both worlds: photorealistic baked 4K beverage textures inside, encased within a physically accurate, thick crystal glass tumbler that casts crisp specular highlights and refractions in real-time.

### 11. Preserving Standard Viewport Background (Avoiding Blinding White Viewport)
- **Problem:** Toggling `space.shading.use_scene_world = True` with a bright environment background color replaces Blender's default neutral grey theme background with a glaring white canvas.
- **Rule:**
  1. **Preserve Theme Background:** In Material Preview shading, keep `space.shading.use_scene_world = False` and ensure `space.shading.background_type = 'THEME'`. This lets Blender use its built-in studio reflection environment while keeping the comfortable neutral dark-grey viewport background.
  2. **Dark Neutral Scene World:** When custom scene world shaders are defined, set the background color to a dark studio tone (`Color: (0.08, 0.08, 0.09)`) instead of bright white, preventing eye strain and overexposed viewport backgrounds.

### 12. Localized Protrusion Smoothing via Cosine Radial Falloff
- **Problem:** Photogrammetry or composite drink meshes can possess localized outward bulges or angular "shoulders" along the lower taper, disrupting the smooth curvature of surrounding glass walls.
- **Rule:** To eliminate localized protrusions without affecting toppings, UV coordinates, or overall geometry:
  1. **Identify the Exact Bulge Range:** Locate the specific $Z$-center and half-width where the mesh juts out.
  2. **Apply a Smooth Bell-Curve Falloff:** Use a Cosine falloff (`weight = 0.5 * (1.0 + cos(pi * dist / width))`) to smoothly taper vertex $X$ and $Y$ radii inward by a modest factor (~5% to 7%).
  3. **Zero Disturbance to Surrounding Areas:** Vertices outside the falloff zone remain 100% untouched, producing a monotonically smooth silhouette that flows naturally along the curvature of the glass.

### 13. Spouted Ceramics (Katakuchi Chawan) & Wabi-Sabi Dual-Material Glaze Mapping
- **Problem:**
  1. Deforming a pouring spout by naive Cartesian offset (`v.co.x -= ...` and `v.co.y *= ...`) collapses wall thickness into a paper-thin knife blade, causes sharp horizontal creasing, and shears inner and outer faces apart.
  2. Relying on vertical height ($Z$) alone to separate glazed interiors from unglazed/clay exteriors fails at spouts because the spout dips below the normal rim height, creating jagged diagonal color cutoffs.
  3. A single center vertex fan (pole with high valence, e.g. 128 edges) creates a severe central pinching/dimple ring artifact under Subdivision Surface (`Subsurf`).
- **Rule:**
  1. **Coherent Polar Spout Deformation:** Displace vertices radially in polar coordinates ($\Delta r = +D_r \cdot W_{\theta} \cdot W_z$, where $W_{\theta} = \cos(\frac{\Delta \theta}{\theta_{max}} \frac{\pi}{2})^2$ and $W_z$ is smoothstep height weighting). Because displacement is applied purely along the radial normal $\hat{r}$, both inner and outer walls expand outward together, maintaining 100% uniform ceramic wall thickness.
  2. **Pouring Channel U-Trough:** Combine the radial flare with a quadratic vertical dip ($\Delta z = -D_z \cdot W_{\theta}^{1.6} \cdot W_z$) to form a natural rounded pouring notch.
  3. **Vertex Color Attribute Glaze Separation:** Store a dedicated float/color attribute (`CeramicAttrs`) on loops during profile lathe generation. Encode interior glaze as $1.0$, rim crest as $0.4$, and exterior clay as $0.0$. When the spout is deformed, the attribute moves coherently with the geometry, ensuring the inner trough stays glazed while the outer spout chin stays clay without any projection artifacts.
  4. **Multi-Scale Kuro-ten (Iron Spots) & Hidasuki Rim:** Combine triple-scale Voronoi noise with domain-warped coordinates for organic dark iron flecks, and blend a golden-amber toasted caramel gradient over the upper rim with micro-mottled noise for authentic Japanese kiln-fired ceramic aesthetics.

### 14. Thermoformed Thin Plastic Containers & Avoiding Normal Explosion on Lathed Profiles
- **Problem:**
  1. Applying a `Solidify` modifier with `use_even_offset = True` or subdividing a standalone open surface with high-valence center poles (e.g. 80-96 radial fans meeting at a single $(0, 0, z)$ vertex) causes vertex normal calculation degeneracy. The normal computation divides by degenerate cross-product angles, projecting the center pole vertices outward into giant horizontal wedge wings/planes across the scene.
  2. Attempting to render transparent thin plastic cups with stochastic refraction (`Transmission = 1.0` in EEVEE screen-space raytracing) across semi-transparent alpha blends generates severe grain/noise in real-time viewports.
- **Rule:**
  1. **Contiguous Closed-Profile Revolve:** Never rely on raw `Solidify` modifiers over high-density polar caps. Revolve a continuous, closed 2D meridian contour containing both outer and inner boundaries: outer base dimple $\to$ foot ring $\to$ kick-up skirt $\to$ stacking recess crease $\to$ tapered conical sidewall $\to$ stacking rib $\to$ toroidal rolled rim bead $\to$ inward normal offset inner wall ($t \approx 0.55\text{ mm}$) $\to$ inner floor disc.
  2. **Watertight Manifold Geometry:** The closed revolved mesh is 100% manifold, double-walled, and naturally handles Subdivision Surface (`Subsurf`) level 1 without any modifier explosion or pinching artifacts.
  3. **Fresnel Silhouette Outlines for Clear Polymers:** Drive transparent plastic materials with a `Layer Weight (Facing)` Fresnel node connected to both Base Color and Alpha ramps. Normal-facing angles stay transparent ($\text{Alpha} \approx 0.05$), while glancing angles transition to dark slate refraction tones ($\text{RGB} \approx 0.20, \text{Alpha} \approx 0.92$). This accurately replicates studio black-flag refraction outlines seen in commercial glassware/beverage packaging photography without stochastic raytracing noise.

### 15. glTF / GLB Export Pipeline & Procedural Shader Texture Baking
- **Problem:** Exporting procedural Blender shader materials directly to `.glb` / `.gltf` strips all procedural mathematical nodes (`Noise`, `Voronoi`, `Mix`, `Attribute`, `ColorRamp`), resulting in a blank/empty material (`textures: []`) because runtime glTF 2.0 specifications strictly mandate bitmap image textures connected to Principled BSDF.
- **Rule:**
  1. **UV Unwrap Verification:** Verify or generate clean, non-overlapping UV coordinates (`bpy.ops.uv.smart_project(island_margin=0.01)`) prior to baking.
  2. **High-Speed Zero-Noise Emission Baking:**
     - To bake pure unshaded Base Color (Albedo) and scalar Roughness maps without stochastic noise or long render times, route the evaluated color/scalar output into a temporary `ShaderNodeEmission` shader and bake using Cycles `bake_type = 'EMIT'` with `samples = 1`.
     - Bake tangent-space normal maps using `bake_type = 'NORMAL'` with `normal_space = 'TANGENT'`.
  3. **PBR Export Shader Rewiring:** Replace the procedural node tree with standard `ShaderNodeTexImage` nodes piped into Principled BSDF sockets (`Base Color` sRGB, `Roughness` Non-Color, and `Normal Map` Non-Color).
  4. **Self-Contained GLB Export:** Call `bpy.ops.export_scene.gltf` with `export_materials = 'EXPORT'`, `export_image_format = 'AUTO'`, and `export_apply = True`. This guarantees that all 2K/4K PBR textures are packed and embedded directly inside the binary `.glb` container for universal web, game engine, and AR compatibility.


### 15. glTF / GLB Export Pipeline & Procedural Shader Texture Baking
- **Problem:** Exporting procedural Blender shader materials directly to `.glb` / `.gltf` strips all procedural mathematical nodes (`Noise`, `Voronoi`, `Mix`, `Attribute`, `ColorRamp`), resulting in a blank/empty material (`textures: []`) because runtime glTF 2.0 specifications strictly mandate bitmap image textures connected to Principled BSDF.
- **Rule:**
  1. **UV Unwrap Verification:** Verify or generate clean, non-overlapping UV coordinates (`bpy.ops.uv.smart_project(island_margin=0.01)`) prior to baking.
  2. **High-Speed Zero-Noise Emission Baking:**
     - To bake pure unshaded Base Color (Albedo) and scalar Roughness maps without stochastic noise or long render times, route the evaluated color/scalar output into a temporary `ShaderNodeEmission` shader and bake using Cycles `bake_type = 'EMIT'` with `samples = 1`.
     - Bake tangent-space normal maps using `bake_type = 'NORMAL'` with `normal_space = 'TANGENT'`.
  3. **PBR Export Shader Rewiring:** Replace the procedural node tree with standard `ShaderNodeTexImage` nodes piped into Principled BSDF sockets (`Base Color` sRGB, `Roughness` Non-Color, and `Normal Map` Non-Color).
  4. **Self-Contained GLB Export:** Call `bpy.ops.export_scene.gltf` with `export_materials = 'EXPORT'`, `export_image_format = 'AUTO'`, and `export_apply = True`. This guarantees that all 2K/4K PBR textures are packed and embedded directly inside the binary `.glb` container for universal web, game engine, and AR compatibility.




