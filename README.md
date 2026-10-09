# Gemini Desktop Blender Bridge (Pi Agent Skill)

[![Blender](https://img.shields.io/badge/Blender-4.x%20%7C%205.x-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/)
[![Pi Agent](https://img.shields.io/badge/Agent-Pi%20Coding%20Agent-6C5CE7)](https://github.com/earendil-works/pi)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)

A real-time bidirectional bridge connecting the **Pi Terminal Coding Agent (powered by Gemini / LLM)** directly to an active **Blender Desktop** application.

Simply prompt the agent in your Pi terminal, such as *"Create a low-poly red sports car in Blender"*, and the 3D model will be generated and updated instantly in your Blender 3D Viewport.

---

## System Architecture

```
+-----------------------------------------------------------------+
|                    Terminal / Pi Coding Agent                   |
|                                                                 |
|   User Prompt: "Create a wooden chair in Blender"               |
|       |                                                         |
|       v                                                         |
|   [Gemini / LLM Agent] ----> Generates bpy Python Script        |
|       |                                                         |
|       v                                                         |
|   [send_to_blender.py] (Client CLI)                             |
+-------------------------------+---------------------------------+
                                |
             +------------------+------------------+
             |                                     |
   (Primary: HTTP REST POST)             (Fallback: File Watcher)
   http://localhost:9876/execute         ~/.blender_bridge/task.py
             |                                     |
             v                                     v
+-----------------------------------------------------------------+
|                      Blender Desktop GUI                        |
|                                                                 |
|   [blender_bridge.py] (Threaded Server + Modal Timer)           |
|       |                                                         |
|       v                                                         |
|   bpy.app.timers (Main Thread Execution)                        |
|       |                                                         |
|       +---> Executes bpy script (Mesh, Materials, Modifiers)    |
|       +---> Triggers 3D Viewport Redraw                         |
|                                                                 |
|   3D Asset appears live in your Blender Viewport!               |
+-----------------------------------------------------------------+
```

### Key Advantages of the Dual-Transport Architecture:
1. **HTTP REST (Fast):** Sends code directly over a local HTTP endpoint (`http://localhost:9876/execute`) for immediate response.
2. **Shared File Watcher (Zero-Config Fallback):** Ideal for WSL2 to Windows Desktop workflows where firewalls or NAT often block network ports. The client writes to `~/.blender_bridge/task.py`, which Blender polls and executes every 100ms.

---

## Features

- **Real-Time Viewport Sync:** Meshes, lights, and materials appear immediately without saving or reloading files.
- **Image-to-3D Reference Modeling:** Easily insert images into the terminal via native Windows/Desktop File Picker Dialog (`pick_image.py --dialog`) or straight from your Clipboard (`pick_image.py --clipboard`, e.g. Win + Shift + S screenshot). Gemini analyzes geometry, proportions, and materials to recreate the 3D model in Blender.
- **PBR Materials & Modifiers:** Automatically configures *Principled BSDF*, Base Color, Roughness, Metallic, Bevel, and Subdivision Surface modifiers.
- **Direct GLB Export:** Supports exporting generated 3D scenes directly to standard `.glb` / `.gltf` binary formats.
- **Continuous Learning Memory:** Automatically records visual corrections, geometry rules, and shader fixes into the skill's persistent memory bank (`SKILL.md`) and recipe library, preventing recurring modeling errors across future sessions.
- **Cross-Platform & WSL2 Ready:** Seamlessly works on native Linux, macOS, native Windows, and WSL2 talking to Windows desktop.
- **Thread-Safe Execution:** Scripts run on Blender's main event loop using `bpy.app.timers` to eliminate context errors and crashes.

---

## Repository Structure

```bash
gemini-desktop-bridge-skill/
├── README.md                      # Documentation and usage guide
├── blender_bridge.py              # Main bridge script executed in Blender
├── install.sh                     # One-click installer for Pi Agent
├── blender_addon/
│   └── blender_bridge.py          # Add-on formatted bridge script
├── skill/
│   ├── SKILL.md                   # Skill prompt and instructions for Pi Agent
│   └── scripts/
│       ├── send_to_blender.py     # Sender CLI tool (HTTP + File Watcher)
│       └── pick_image.py          # Native File Picker Dialog & Clipboard image tool
└── examples/
    ├── 01_coffee_cup.py           # Example: Procedural ceramic coffee cup
    ├── 02_lowpoly_car.py          # Example: Low-poly vehicle with wheels
    ├── 03_export_glb.py           # Example: Glowing crystal + GLB export
    └── recipes/
        └── 04_iced_latte_glass_lathe.py  # Verified Recipe: Seamless watertight glass & beverage lathe
```

---

## Installation & Setup

### Step 1: Install the Skill into Pi Coding Agent
Run the installation script in your terminal:

```bash
git clone https://github.com/FidelCristopher/gemini-desktop-bridge-skill.git
cd gemini-desktop-bridge-skill
./install.sh
```
*This installs the skill permanently to `~/.pi/agent/skills/blender-bridge/` for all future sessions.*

---

### Step 2: Run the Bridge in Blender Desktop
1. Open **Blender** on your desktop.
2. Switch to the **Scripting** tab at the top.
3. Click **Open**, and select `blender_bridge.py` from this repository directory.
4. Click **Run Script** (or press `Alt + P`).
5. In the 3D Viewport (press `N` to open the sidebar), you will see the **Pi Bridge** panel displaying:
   ```
   Status: Active (Port 9876)
   ```

---

### Step 3: Prompt the Pi Agent
Interact naturally with the Pi Agent in your terminal:

> **User:** *"Create a low-poly wooden dining table with four legs in Blender"*
> 
> **Pi Agent:** *(Generates the bpy script and dispatches it to Blender)*
> 
> **Result:** The 3D model appears instantly in your Blender viewport!

---

## Example Prompts

- *"Create a 3D model in Blender from an image"* -> The agent offers a native File Picker dialog or grabs from your clipboard.
- *"Model this chair in Blender based on C:\Users\Pongo\Pictures\chair.png"*
- *"Create a ceramic coffee cup with steam and a handle"*
- *"Build a low-poly sports car with silver rims and a metallic red body"*
- *"Generate a low-poly pine tree with an icosphere foliage canopy"*
- *"Clear the scene and create a frosted pink donut with sprinkles"*
- *"Model a sci-fi energy blade with neon blue emission and export it to a .glb file"*

---

## Manual CLI Testing

You can test the connection manually without prompting the agent:

```bash
# Check Blender connection status
python3 skill/scripts/send_to_blender.py --status

# Send the procedural coffee cup example
python3 skill/scripts/send_to_blender.py --file examples/01_coffee_cup.py

# Send the low-poly car example
python3 skill/scripts/send_to_blender.py --file examples/02_lowpoly_car.py
```

---

## Contributions

Created by [Fidel Cristopher](https://github.com/FidelCristopher).
Issues, feature requests, and pull requests are welcome!
