#!/usr/bin/env bash
set -e

SKILL_NAME="blender-bridge"
PI_SKILLS_DIR="$HOME/.pi/agent/skills/$SKILL_NAME"

echo "============================================="
echo "Installing Pi Desktop Blender Bridge Skill"
echo "============================================="

# Create skills directory
mkdir -p "$PI_SKILLS_DIR/scripts"

# Copy skill files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/skill/SKILL.md" "$PI_SKILLS_DIR/SKILL.md"
cp "$SCRIPT_DIR/skill/scripts/send_to_blender.py" "$PI_SKILLS_DIR/scripts/send_to_blender.py"
chmod +x "$PI_SKILLS_DIR/scripts/send_to_blender.py"

echo "[OK] Skill installed successfully to: $PI_SKILLS_DIR"
echo ""
echo "Quick Start:"
echo "1. Open Blender Desktop"
echo "2. In Blender, go to Scripting tab, open 'blender_addon/blender_bridge.py', and click 'Run Script'"
echo "3. In Pi, just ask: 'Create a low poly car in Blender'!"
echo "============================================="
