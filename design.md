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

---

## Asset Log #03: Traditional Japanese Katakuchi Matcha Chawan (片口茶碗)

- **Date:** 2026-10-09
- **Category:** Japanese Ceramic Tableware / Tea Ceremony Vessel (Chawan)
- **Source:** Image Reference (`/mnt/c/Users/Pongo/Downloads/chawan-matcha.png` / `C:\Users\Pongo\Downloads\chawan-matcha.png`)
- **Asset Name in Scene:** `Katakuchi_Chawan`

### 1. Geometric Architecture & Dimensions
- **Physical Proportions:**
  - **Rim Diameter:** 15.2 cm (Radius $R = 0.076\text{ m}$)
  - **Total Height:** 6.45 cm ($Z = 0.0645\text{ m}$)
  - **Foot Ring (Kodai) Outer Diameter:** 7.8 cm (Radius $R = 0.039\text{ m}$, Height $Z = 0.0035\text{ m}$, Width $\approx 4.2\text{ mm}$)
  - **Wall Thickness:** Uniform $4.2\text{ mm}$ across the entire body, preserving authentic hand-thrown stoneware cross-section.
- **Topology & Construction:**
  - **Lathe Profile Generation:** 34 sampled profile coordinate points revolved along 128 radial subdivisions, generating clean quad strips.
  - **Center Tea Pool (Chadamari):** Non-polar manifold topology at $(0, 0, 0.0095\text{ m})$ to avoid high-valence Catmull-Clark pole creasing rings.
  - **Pouring Spout (Katakuchi Lip):**
    - Centered at $\theta = \pi$ ($-X$ axis) with an angular half-span of $25^\circ$.
    - $C^1$-continuous cosine bell-curve azimuthal falloff $W_{\theta} = \cos(\frac{\Delta \theta}{\theta_{max}} \frac{\pi}{2})^2$ coupled with vertical smoothstep height weighting $W_z = t_z^2 (3 - 2t_z)$ for $Z \in [0.035, 0.0645]\text{ m}$.
    - Coherent 3D space radial flare $\Delta r = +13.5\text{ mm}$ combined with vertical pour trough depression $\Delta z = -7.5\text{ mm}$. Preserves uniform ceramic wall thickness and prevents edge creasing or thin-blade shearing.
  - **Wheel-Thrown Concentric Ridges (Rokuro-me):**
    - 5 tactile horizontal steps and groove depressions on the exterior lower half ($Z = 0.012\text{ m}$ to $0.038\text{ m}$).
  - **Modifiers:** Subdivision Surface (`Subsurf`) Level 2 viewport and render.
  - **Shading:** Full smooth shading with consistently recalculated outward normals.

### 2. Shader & PBR Material Specification
- **Material Name:** `Katakuchi_Ceramic_Master`
- **Surface Domain Mapping:**
  - Dual coordinate integration: BMesh Vertex Color Attribute (`CeramicAttrs`) containing:
    - **Red channel:** `GlazeFactor` ($1.0$ interior glaze, $0.4$ rim crest, $0.0$ exterior clay).
    - **Green channel:** `GrooveFactor` ($1.0$ in recessed throwing grooves for localized shadow darkening).
    - **Blue channel:** `ProfileV` (normalized arc-length along revolved profile curve).
  - High-frequency micro-domain warping perturbing transitions by $\pm 6\%$ to emulate natural hand-dipped kiln glaze breaks (*wabi-sabi* aesthetic).
- **Multi-Layer PBR Architecture:**
  1. **Interior Base Glaze:**
     - Toasted oatmeal / almond cream palette: Base Color gradient from `#C8B698` (`RGB: 0.75, 0.65, 0.51`) to `#DECFA8` (`RGB: 0.88, 0.82, 0.70`).
     - Procedural tonal noise ($Scale: 16.0, Detail: 5.0$) simulating ash glaze pooling.
  2. **Kuro-ten (Iron Spots & Flecks):**
     - Triple-scale Voronoi distance networks perturbed by 3D vector noise:
       - Large irregular spots ($Scale: 120.0, Randomness: 1.0$)
       - Medium flecks ($Scale: 240.0, Randomness: 1.0$)
       - Fine pepper dust ($Scale: 520.0, Randomness: 1.0$)
     - Spot color: Deep burnt umber / iron oxide (`RGB: 0.08, 0.04, 0.018`).
  3. **Hidasuki Toasted Golden-Amber Rim Band:**
     - Concentrated along the upper interior wall and rim crest ($V \in [0.06, 0.18]$).
     - Color gradient: Deep toasted caramel (`RGB: 0.34, 0.16, 0.06`) to golden amber (`RGB: 0.58, 0.32, 0.12`).
     - Integrated micro-mottled noise ($Scale: 85.0, Detail: 6.0, Roughness: 0.75$) with cream micro-flecks (`RGB: 0.76, 0.66, 0.48`) simulating glaze breaking over the edge during kiln firing.
  4. **Exterior Stoneware Terracotta Clay Body:**
     - Rich chocolate / umber terracotta clay: Base Color `#382012` (`RGB: 0.22, 0.13, 0.075`).
     - Groove darkening: Green channel groove factor subtracts albedo in throwing rings down to deep umber `#1E0F07` (`RGB: 0.065, 0.032, 0.016`).
  5. **Surface Finish & Optical Parameters:**
     - **Glaze Roughness:** Satin ceramic sheen ($Roughness \approx 0.35$).
     - **Clay Roughness:** Earthy tactile matte stoneware ($Roughness \approx 0.72$).
     - **Specular IOR Level:** $0.55$.
     - **Subsurface Scattering:** Subtle ceramic warmth ($Weight: 0.07, Radius: (0.35, 0.25, 0.15)$).
     - **Micro-Relief Normal Mapping:** Multi-octave bump ($Strength: 0.035, Distance: 0.002\text{ m}, Scale: 130.0$) simulating ceramic orange-peel waviness and clay grog texture.

### 3. Lighting & Viewport Staging
- **Camera Configuration:**
  - Focal Length: $62.0\text{ mm}$ (flattering perspective with zero wide-angle distortion).
  - Location: $(-0.16, -0.26, 0.235)\text{ m}$, Target: $(-0.005, 0.0, 0.025)\text{ m}$.
  - Elevation Angle: $\approx 38^\circ$ elevated $3/4$ view matching the reference photo perspective.
- **Studio 3-Point Illumination:**
  - **Key Area Light:** Soft warm daylight ($1.0, 0.97, 0.92$), Energy $8.5\text{ W}$, Size $0.35\text{ m}$, Position $(-0.20, -0.20, 0.28)\text{ m}$.
  - **Fill Area Light:** Soft cool fill ($0.95, 0.97, 1.0$), Energy $2.8\text{ W}$, Size $0.45\text{ m}$, Position $(0.24, -0.16, 0.22)\text{ m}$.
  - **Rim Area Light:** Warm rim highlight ($1.0, 0.96, 0.90$), Energy $5.2\text{ W}$, Size $0.30\text{ m}$, Position $(0.0, 0.26, 0.26)\text{ m}$.
- **Color Management:** Filmic View Transform with Medium High Contrast for authentic ceramic dynamic range.

### 4. PBR Texture Baking & glTF / GLB Export Pipeline
- **Problem Resolved:** Standard procedural Blender node networks (`Noise`, `Voronoi`, `Separate Color`, `Attribute`, `Mix`) cannot be translated by glTF 2.0 specifications, resulting in blank `textures: []` upon raw `.glb` export (252 KB empty container).
- **UV Layout:** Smart UV Project with angular threshold $66^\circ$ and island margin $0.01$ generating clean non-overlapping coordinates (`UVMap`).
- **2K Texture Baking:**
  - **Base Color (Albedo) Map (2048 x 2048 PNG):** Fast 1-sample emission baking of toasted caramel rim, golden amber band, almond cream floor, Kuro-ten iron specks, and chocolate terracotta clay.
  - **Roughness Map (2048 x 2048 PNG, Non-Color):** Mapped satin glaze ($\approx 0.36$) to matte terracotta exterior ($\approx 0.78$).
  - **Tangent-Space Normal Map (2048 x 2048 PNG, Non-Color):** 16-sample tangent normal baking of ceramic orange-peel waviness and 5 rokuro-me throwing grooves.
- **Binary GLB Packaging:**
  - Output File: `C:\Users\Pongo\Downloads\chawan-matcha.glb` (22.05 MB).
  - Packed with 3 embedded 2K PBR bitmap textures and fully evaluated Level 2 subdivision geometry for universal Three.js, Godot, Unreal, Unity, and AR viewing.


---

## Asset: Thermoformed Disposable PET Plastic Cup (16 oz)
**Timestamp:** 2026-10-09 17:03:27  
**Category:** Beverage Packaging & Disposable Ware  
**Source:** Reference Image (`/mnt/c/Users/Pongo/Downloads/plastic-cup.png`)

### 1. Geometric Architecture & Dimensions
- **Anatomy & Dimensions:**
  - Total Height: $124.9\text{ mm}$ ($0.1249\text{ m}$)
  - Top Rim Outer Diameter: $98.8\text{ mm}$ (Radius $49.4\text{ mm}$)
  - Base Contact Diameter: $61.6\text{ mm}$ (Radius $30.8\text{ mm}$)
  - Aspect Ratio (Height / Rim Width): $\approx 1.26$
  - Wall Thickness: Uniform $0.55\text{ mm}$ ($0.00055\text{ m}$) thermoformed polymer shell.
- **Thermoformed Structural Profile:**
  - **Recessed Base Floor & Injection Sprue:** Elevated floor disc ($Z = 3.4\text{ mm}$ to $5.2\text{ mm}$) with a central push-up dimple mark and concentric circular stiffening bead ($R = 17.5\text{ mm}$ to $19.5\text{ mm}$) to resist hydro-static pressure.
  - **Foot Contact Ring & Skirt:** Smooth transition to flat contact circle ($Z = 0.0\text{ mm}, R = 30.8\text{ mm}$) ascending into an outer vertical kick-up skirt ($Z = 0.0$ to $10.2\text{ mm}$).
  - **Stacking Recess Crease:** Inward indentation step ($Z = 10.2$ to $12.6\text{ mm}$, inward radius decrease to $R = 30.6\text{ mm}$) providing vertical stacking clearance for nested cups.
  - **Conical Sidewall:** Linear draft angle taper ($R = 31.3\text{ mm}$ at $Z = 14.0\text{ mm}$ to $R = 41.6\text{ mm}$ at $Z = 112.0\text{ mm}$).
  - **Upper Stacking Indexing Bead:** Circumferential outward rib bead ($R = 43.2\text{ mm}$ at $Z = 117.8\text{ mm}$) acting as an indexing stop for takeaway lids and nested packaging.
  - **Toroidal Rolled Rim Lip:** Fully curled bead crest curving smoothly upward, outward to $R = 49.0\text{ mm}$ at $Z = 123.5\text{ mm}$, tucking downward to $Z = 121.6\text{ mm}$ and turning back under to seal the rim lip.
- **Topology & Mesh Generation:**
  - Continuous closed 2D meridian contour (outer shell $\to$ rolled lip $\to$ inward normal-offset inner wall $\to$ inner base floor).
  - Revolved with $84$ radial segments around the $Z$-axis into a contiguous quad grid mesh (546 meridian steps $\times$ 84 radial rings $\approx$ 45,000 polygons post-subdivision).
  - Watertight, 100% manifold, double-walled topology eliminating `Solidify` modifier normal-division explosions on polar fans.
  - Modifier Stack: Subdivision Surface (`Subsurf`) Level 1 Viewport / Level 2 Render.

### 2. Optical Plastic PBR Material Architecture
- **Material Identity:** `PET_Clear_Plastic`
- **PBR & Shader Nodes:**
  - **Principled BSDF:**
    - Roughness: $0.015$ (high-gloss optical clarity).
    - Refractive Index (IOR): $1.540$ (physically verified PET polymer refractive index).
    - Specular IOR Level: $0.95$ (accentuated surface Fresnel highlights).
  - **Fresnel Silhouette Definition (`Layer Weight` Network):**
    - `Layer Weight (Facing)` node with Blend factor $0.22$.
    - **Base Color Ramp:** Transitions smoothly from crisp clear neutral (`RGB: 0.98, 0.99, 1.0`) at normal angles ($Fac > 0.30$) to dark slate refraction tone (`RGB: 0.20, 0.24, 0.28`) at glancing silhouette edges ($Fac = 0.0$).
    - **Alpha Ramp:** Maps facing normals to high transparency ($\text{Alpha} \approx 0.05$) while building opacity to $\text{Alpha} \approx 0.92$ along grazing edges.
  - **Viewport Transparency Settings:**
    - `mat.blend_method = 'BLEND'`
    - `mat.show_transparent_back = True`
    - `mat.use_backface_culling = False`
    - Delivers noise-free, crystal-clear real-time transmission showing internal base geometry, rear wall depth, and crisp rim highlights.

### 3. Studio Lighting Rig & Viewport Staging
- **Camera Staging:**
  - Focal Length: $78.0\text{ mm}$ (product photography telephoto compression).
  - Location: $(0.0, -0.42, 0.155)\text{ m}$, pointing directly at cup geometric center $(0.0, 0.0, 0.065)\text{ m}$.
  - Tilt: $\approx 12.0^\circ$ downward pitch, framing the elliptical top rim opening and revealing the depth of the recessed bottom floor.
- **Studio 3-Point Illumination:**
  - **Key Softbox:** Warm white ($1.0, 0.98, 0.95$), Energy $10.0\text{ W}$, Size $0.18 \times 0.25\text{ m}$, Position $(-0.20, -0.25, 0.22)\text{ m}$.
  - **Fill Softbox:** Soft cool fill ($0.94, 0.97, 1.0$), Energy $6.0\text{ W}$, Size $0.18 \times 0.25\text{ m}$, Position $(0.20, -0.25, 0.22)\text{ m}$.
  - **Top Rim Light:** Neutral white ($1.0, 1.0, 1.0$), Energy $8.0\text{ W}$, Size $0.20\text{ m}$, Position $(0.0, -0.05, 0.28)\text{ m}$.
- **Viewport Shading Configuration:**
  - Material Preview with Blender default neutral dark-grey theme background (`space.shading.background_type = 'THEME'`).
  - Active scene lights enabled (`use_scene_lights = True`) to illuminate reflections and rim highlights.

