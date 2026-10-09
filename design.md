# 3D Asset Design & Architecture Log (`design.md`)

This living document tracks every 3D asset designed, generated, and refined using the **Gemini Desktop Blender Bridge Skill**. It records geometric specifications, PBR shader parameters, lighting rigs, and evolutionary design revisions.

---

## Asset Log #01: Japanese Red Strawberry (Tochiotome / Amaou)

- **Date:** 2026-10-09
- **Category:** Organic Food / Fruit Prop
- **Source:** Text Prompt ("3d asset strawberry jepang berwarna merah")

### 1. Geometric Structure
- **Main Body (`JapaneseStrawberry_Body`):**
  - UV Sphere base deformed via normalized height factor: tapered bottom cone ($Z < 0$), wide plump belly ($Z \approx 0.85$), gentle top indentation.
  - Modifiers: Subdivision Surface (Levels 2), Smooth Shading.
- **Seeds (`Strawberry_Seeds`):**
  - Instanced flattened icospheres arranged in 6 concentric radial rings along the strawberry surface with outward normal yaw.
- **Calyx Leaves (`CalyxLeaf_1..7`):**
  - 7 elongated diamond cone meshes radiating outward and draping over the crown with downward tilt angles.
- **Stem (`StrawberryStem`):**
  - Beveled cylinder with an organic natural lean.

### 2. Shader & PBR Parameters
- **Berry Skin:** `Principled BSDF` (Base Color: `(0.88, 0.03, 0.06)`, Roughness: `0.22`, Specular: `0.80`).
- **Achenes / Seeds:** Golden metallic tint (Base Color: `(0.95, 0.82, 0.25)`, Roughness: `0.30`, Specular: `0.60`).
- **Leaves & Stem:** Fresh vibrant leafy green (Base Color: `(0.07, 0.48, 0.12)`, Roughness: `0.35`).

---

## Asset Log #02: Iced Matcha Latte with Cold Foam & Crystal Glass Tumbler

- **Date:** 2026-10-09
- **Category:** Photorealistic Beverage & Drinkware
- **Source:** Image Reference (`Hops-2025-11-10T130655549-4167125760-removebg-preview.png`) + Showcase Asset Synthesis (`matcha.glb`)

### 1. Geometric Architecture
- **Thick Crystal Glass Tumbler (`Thick_Crystal_Glass_Tumbler`):**
  - 64-segment revolved lathe shell with uniform wall thickness (~0.045 units).
  - Solid crystal base plate from $Z = -0.585$ to $Z = -0.538$ (5 mm thick base).
  - Bulbous belly curve tapering upward to a smooth rounded lip rim at $Z = 0.545$.
- **Matcha Drink Core (`Matcha_Drink_Asset`):**
  - High-fidelity unified asset (26,270 vertices) seated directly on the inner solid glass floor ($Z = -0.538$).
  - Bottom boundary scan hole sealed seamlessly using BMesh.
  - Lower lateral protrusion ($Z \approx -0.28$) smoothly tapered using a targeted Cosine bell-curve falloff ($6.8\%$ radial reduction) to follow the glass silhouette continuously.
- **Cold Foam & Velvet Powder Topping:**
  - Soft undulating sculpted cream foam.
  - Selective powder distribution concentrated in center/upper-middle with bare white foam perimeter.
  - High diffuse roughness (`0.88`) and low specular (`0.15`) for a soft velvety matcha dust finish.

### 2. Shader & Material Hierarchy
- **Optical Glass:**
  - `Transmission Weight = 1.0`, `Roughness = 0.02`, `IOR = 1.50`, `Alpha = 0.18`.
  - Blender 5.2 EEVEE Raytraced Screen Refraction enabled (`refraction_depth = 0.04`, `blend_method = 'HASHED'`).
  - Subtle procedural condensation bump (`Scale: 35.0, Strength: 0.035`).
- **Creamy Matcha Liquid:**
  - 4K UV-mapped texture atlas + Subsurface Scattering (`Subsurface Weight: 0.35`, `Radius: (0.2, 0.5, 0.1)`).
- **Cold Foam:**
  - Soft velvety PBR (`Roughness: 0.88`, `Specular: 0.15`, Subsurface Scattering: `0.22`, fine micro-grain bump).

### 3. Studio Lighting & Viewport Configuration
- **Lighting Rig:** 3-Point Studio Softbox System:
  - Key Light: Area 1.8m, Energy 140W, Color `(1.0, 0.98, 0.95)`, location `(1.8, -2.2, 2.2)`.
  - Fill Light: Area 2.2m, Energy 60W, Color `(0.92, 0.96, 1.0)`, location `(-2.0, -1.5, 1.5)`.
  - Rim Light: Area 1.4m, Energy 120W, Color `(1.0, 1.0, 1.0)`, location `(0.2, 2.2, 2.0)`.
- **Viewport:** Material Preview shading with `use_scene_world = False` and `background_type = 'THEME'` to preserve the comfortable dark neutral grey interface.
