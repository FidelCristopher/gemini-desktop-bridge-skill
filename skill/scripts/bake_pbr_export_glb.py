#!/usr/bin/env python3
"""
bake_pbr_export_glb.py
----------------------
Automated 2K PBR Texture Baking & Self-Contained GLB Export Tool.

Converts Blender procedural materials (Noise, Voronoi, ColorRamp, Attributes, Mix)
into high-resolution 2K/4K bitmap textures (Base Color, Roughness, Normal Map)
and exports a self-contained, fully textured .glb binary file.
"""

import sys
import os
import argparse
from pathlib import Path

# When executed via send_to_blender inside Blender:
def run_bake_and_export_inside_blender(obj_name=None, export_path=None, resolution=2048):
    import bpy
    import math
    import time

    # 1. Target Object Resolution
    obj = None
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
    if not obj:
        obj = bpy.context.active_object or next((o for o in bpy.data.objects if o.type == 'MESH'), None)

    if not obj or obj.type != 'MESH':
        raise RuntimeError(f"No valid mesh object found for baking (specified: {obj_name})")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if not obj.data.materials:
        raise RuntimeError(f"Object '{obj.name}' has no material to bake!")

    mat = obj.data.materials[0]
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 2. Ensure Clean UV Coordinates
    if not obj.data.uv_layers:
        print(f"[Bake Tool] Generating Smart UV Map for '{obj.name}'...")
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.01)
        bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Setup Cycles Baking
    old_engine = bpy.context.scene.render.engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.use_adaptive_sampling = False
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.margin = 16

    RES = int(resolution)
    print(f"[Bake Tool] Initializing {RES}x{RES} PBR Texture Maps for '{obj.name}'...")

    # Image textures
    prefix = f"{obj.name}_Bake"
    img_basecolor = bpy.data.images.new(f"{prefix}_BaseColor", width=RES, height=RES, alpha=False, float_buffer=False)
    img_roughness = bpy.data.images.new(f"{prefix}_Roughness", width=RES, height=RES, alpha=False, float_buffer=False)
    img_normal    = bpy.data.images.new(f"{prefix}_Normal",    width=RES, height=RES, alpha=False, float_buffer=False)

    tex_bake_node = nodes.new('ShaderNodeTexImage')
    node_emit = nodes.new('ShaderNodeEmission')
    node_out = nodes.get("Material Output") or next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    bsdf = nodes.get("Principled BSDF") or next(n for n in nodes if n.type in ('BSDF_PRINCIPLED', 'ShaderNodeBsdfPrincipled'))

    # Locate active socket connections
    base_col_link = bsdf.inputs["Base Color"].links[0] if bsdf.inputs["Base Color"].links else None
    rough_link = bsdf.inputs["Roughness"].links[0] if bsdf.inputs["Roughness"].links else None

    # --- BAKE 1: Base Color (Fast 1-Sample Emission Bake) ---
    print(f"[Bake Tool] Baking 2K Base Color (Albedo)...")
    t0 = time.time()
    tex_bake_node.image = img_basecolor
    nodes.active = tex_bake_node
    if base_col_link:
        links.new(base_col_link.from_socket, node_emit.inputs["Color"])
    else:
        node_emit.inputs["Color"].default_value = bsdf.inputs["Base Color"].default_value
    links.new(node_emit.outputs["Emission"], node_out.inputs["Surface"])
    bpy.context.scene.cycles.samples = 1
    bpy.ops.object.bake(type='EMIT')
    print(f"[Bake Tool] Base Color finished in {time.time() - t0:.2f}s")

    # --- BAKE 2: Roughness (Fast 1-Sample Emission Bake) ---
    print(f"[Bake Tool] Baking 2K Roughness Map...")
    t0 = time.time()
    tex_bake_node.image = img_roughness
    nodes.active = tex_bake_node
    if rough_link:
        links.new(rough_link.from_socket, node_emit.inputs["Color"])
    else:
        val = bsdf.inputs["Roughness"].default_value
        node_emit.inputs["Color"].default_value = (val, val, val, 1.0)
    bpy.context.scene.cycles.samples = 1
    bpy.ops.object.bake(type='EMIT')
    print(f"[Bake Tool] Roughness finished in {time.time() - t0:.2f}s")

    # --- BAKE 3: Tangent Normal Map ---
    print(f"[Bake Tool] Baking 2K Tangent-Space Normal Map...")
    t0 = time.time()
    tex_bake_node.image = img_normal
    nodes.active = tex_bake_node
    links.new(bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.render.bake.normal_space = 'TANGENT'
    bpy.ops.object.bake(type='NORMAL')
    print(f"[Bake Tool] Normal Map finished in {time.time() - t0:.2f}s")

    # Cleanup temporary bake nodes
    nodes.remove(node_emit)
    nodes.remove(tex_bake_node)
    bpy.context.scene.render.engine = old_engine

    # 4. Construct Clean Export PBR Material
    print(f"[Bake Tool] Rewiring PBR Image Textures...")
    mat_export = bpy.data.materials.new(f"{obj.name}_PBR_Export")
    mat_export.use_nodes = True
    exp_nodes = mat_export.node_tree.nodes
    exp_links = mat_export.node_tree.links
    exp_nodes.clear()

    exp_out = exp_nodes.new('ShaderNodeOutputMaterial')
    exp_out.location = (800, 0)

    exp_bsdf = exp_nodes.new('ShaderNodeBsdfPrincipled')
    exp_bsdf.location = (450, 0)
    exp_bsdf.inputs["Specular IOR Level"].default_value = 0.55
    exp_links.new(exp_bsdf.outputs["BSDF"], exp_out.inputs["Surface"])

    # Base Color Texture
    tex_col = exp_nodes.new('ShaderNodeTexImage')
    tex_col.location = (50, 200)
    tex_col.image = img_basecolor
    exp_links.new(tex_col.outputs["Color"], exp_bsdf.inputs["Base Color"])

    # Roughness Texture (Non-Color)
    tex_rough = exp_nodes.new('ShaderNodeTexImage')
    tex_rough.location = (50, -50)
    tex_rough.image = img_roughness
    img_roughness.colorspace_settings.name = 'Non-Color'
    exp_links.new(tex_rough.outputs["Color"], exp_bsdf.inputs["Roughness"])

    # Normal Map Texture (Non-Color)
    tex_norm = exp_nodes.new('ShaderNodeTexImage')
    tex_norm.location = (-250, -300)
    tex_norm.image = img_normal
    img_normal.colorspace_settings.name = 'Non-Color'

    norm_node = exp_nodes.new('ShaderNodeNormalMap')
    norm_node.location = (100, -300)
    norm_node.inputs["Strength"].default_value = 0.35
    exp_links.new(tex_norm.outputs["Color"], norm_node.inputs["Color"])
    exp_links.new(norm_node.outputs["Normal"], exp_bsdf.inputs["Normal"])

    # Assign to object
    obj.data.materials.clear()
    obj.data.materials.append(mat_export)

    # 5. Export to GLB
    if not export_path:
        home_dir = Path.home()
        export_path = str(home_dir / "Downloads" / f"{obj.name}.glb")

    print(f"[Bake Tool] Exporting self-contained GLB to {export_path}...")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_lights=True
    )

    size_mb = os.path.getsize(export_path) / (1024 * 1024)
    print(f"[Bake Tool] SUCCESS! Exported {size_mb:.2f} MB GLB file with embedded 2K PBR textures to:\n  {export_path}")
    return export_path

# CLI wrapper for executing from terminal via send_to_blender
def main():
    parser = argparse.ArgumentParser(description="Automated 2K PBR Texture Baking & GLB Exporter for Blender")
    parser.add_argument("--object", "-o", type=str, help="Target object name in Blender")
    parser.add_argument("--output", "-f", type=str, help="Output .glb filepath")
    parser.add_argument("--resolution", "-r", type=int, default=2048, help="Bake resolution (default: 2048)")
    args = parser.parse_args()

    # Build Blender code snippet
    code = f"""
import sys
sys.path.append(r"{os.path.dirname(os.path.abspath(__file__))}")
import bake_pbr_export_glb
bake_pbr_export_glb.run_bake_and_export_inside_blender(
    obj_name={repr(args.object)},
    export_path={repr(args.output)},
    resolution={args.resolution}
)
"""
    # Dispatch via send_to_blender
    send_script = Path(__file__).parent / "send_to_blender.py"
    if not send_script.exists():
        send_script = Path.home() / ".pi/agent/skills/blender-bridge/scripts/send_to_blender.py"

    import subprocess
    cmd = [sys.executable, str(send_script), "--code", code]
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    # Check if running inside Blender
    try:
        import bpy
        # Running inside Blender:
        # Default run on active object
        run_bake_and_export_inside_blender()
    except ImportError:
        # Running as CLI wrapper
        main()
