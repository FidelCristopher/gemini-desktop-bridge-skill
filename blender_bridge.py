bl_info = {
    "name": "Pi Desktop Blender Bridge",
    "author": "Fidel Cristopher & Pi Agent",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > Pi Bridge / Scripting",
    "description": "Live bidirectional bridge between Pi Coding Agent and Blender desktop",
    "category": "Development",
}

import bpy
import http.server
import socketserver
import threading
import json
import queue
import io
import sys
import os
import time
import traceback
from pathlib import Path

DEFAULT_PORT = 9876
BRIDGE_DIR = Path.home() / ".blender_bridge"
TASK_FILE = BRIDGE_DIR / "task.py"
RESULT_FILE = BRIDGE_DIR / "result.json"

# State
task_queue = queue.Queue()
server_instance = None
server_thread = None
is_running = False

def ensure_bridge_dir():
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)

class BlenderRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy standard HTTP logs, keep console clean
        pass

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "online",
                "blender_version": bpy.app.version_string,
                "scene": bpy.context.scene.name if bpy.context.scene else None,
                "objects_count": len(bpy.data.objects),
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path in ("/execute", "/run"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            code = ""
            try:
                payload = json.loads(body)
                code = payload.get("code", "")
            except Exception:
                code = body # Fallback to raw script text

            if not code.strip():
                self.send_response(400)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Empty code"}).encode("utf-8"))
                return

            done_event = threading.Event()
            result_box = {}
            task_queue.put((code, result_box, done_event))

            # Wait for main thread execution
            finished = done_event.wait(timeout=60.0)
            self.send_response(200 if finished else 504)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            if finished:
                self.wfile.write(json.dumps(result_box).encode("utf-8"))
            else:
                self.wfile.write(json.dumps({
                    "status": "timeout",
                    "error": "Execution timed out after 60 seconds"
                }).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def execute_code_safely(code):
    """Executes Python code in Blender's main thread and captures logs."""
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    exec_globals = {
        "__name__": "__main__",
        "bpy": bpy,
    }

    status = "success"
    err_msg = ""
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        exec(code, exec_globals)
    except Exception:
        status = "error"
        err_msg = traceback.format_exc()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    # Force viewport redraw so user sees immediate results
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass

    return {
        "status": status,
        "output": stdout_capture.getvalue(),
        "error": err_msg or stderr_capture.getvalue()
    }

def bridge_timer_loop():
    """Timer running inside Blender main thread every 0.1s."""
    global is_running
    if not is_running:
        return None

    # 1. Process tasks from HTTP queue
    while not task_queue.empty():
        try:
            code, result_box, done_event = task_queue.get_nowait()
            res = execute_code_safely(code)
            result_box.update(res)
            done_event.set()
        except queue.Empty:
            break
        except Exception as e:
            print(f"[Pi Bridge] HTTP task error: {e}")

    # 2. Process tasks from File Watcher fallback (~/.blender_bridge/task.py)
    try:
        if TASK_FILE.exists():
            time.sleep(0.05) # Brief buffer to ensure atomic file write completion
            code = TASK_FILE.read_text(encoding="utf-8")
            try:
                TASK_FILE.unlink()
            except Exception:
                pass
            
            if code.strip():
                res = execute_code_safely(code)
                try:
                    RESULT_FILE.write_text(json.dumps(res, indent=2), encoding="utf-8")
                except Exception as e:
                    print(f"[Pi Bridge] Failed to write result.json: {e}")
    except Exception as e:
        print(f"[Pi Bridge] File watcher error: {e}")

    return 0.1 # Repeat every 100ms

def start_bridge(port=DEFAULT_PORT):
    global server_instance, server_thread, is_running
    if is_running:
        print("[Pi Bridge] Already running.")
        return

    ensure_bridge_dir()
    is_running = True

    try:
        server_instance = ThreadedHTTPServer(("0.0.0.0", port), BlenderRequestHandler)
        server_thread = threading.Thread(target=server_instance.serve_forever, daemon=True)
        server_thread.start()
        print(f"==================================================")
        print(f"[Pi Bridge] Active & Listening!")
        print(f"HTTP Endpoint: http://localhost:{port}/run")
        print(f"File Watcher: {BRIDGE_DIR}")
        print(f"==================================================")
    except Exception as e:
        print(f"[Pi Bridge] WARNING: HTTP Server could not bind port {port}: {e}")
        print(f"[Pi Bridge] File Watcher fallback remains ACTIVE on {BRIDGE_DIR}")

    # Register main thread timer
    if not bpy.app.timers.is_registered(bridge_timer_loop):
        bpy.app.timers.register(bridge_timer_loop, first_interval=0.1)

def stop_bridge():
    global server_instance, server_thread, is_running
    is_running = False
    if server_instance:
        try:
            server_instance.shutdown()
            server_instance.server_close()
        except Exception:
            pass
        server_instance = None
    server_thread = None

    if bpy.app.timers.is_registered(bridge_timer_loop):
        bpy.app.timers.unregister(bridge_timer_loop)
    print("[Pi Bridge] Stopped.")

# UI Panel inside 3D Viewport Sidebar (N-Panel)
class VIEW3D_PT_pi_bridge(bpy.types.Panel):
    bl_label = "Pi Agent Bridge"
    bl_idname = "VIEW3D_PT_pi_bridge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pi Bridge'

    def draw(self, context):
        layout = self.layout
        global is_running
        if is_running:
            layout.label(text="Status: Active (Port 9876)")
            layout.operator("wm.pi_bridge_stop", text="Stop Bridge")
        else:
            layout.label(text="Status: Inactive")
            layout.operator("wm.pi_bridge_start", text="Start Bridge")

class WM_OT_pi_bridge_start(bpy.types.Operator):
    bl_idname = "wm.pi_bridge_start"
    bl_label = "Start Pi Bridge"
    def execute(self, context):
        start_bridge()
        return {'FINISHED'}

class WM_OT_pi_bridge_stop(bpy.types.Operator):
    bl_idname = "wm.pi_bridge_stop"
    bl_label = "Stop Pi Bridge"
    def execute(self, context):
        stop_bridge()
        return {'FINISHED'}

classes = (
    VIEW3D_PT_pi_bridge,
    WM_OT_pi_bridge_start,
    WM_OT_pi_bridge_stop,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    # Auto-start on load / execution
    start_bridge()

def unregister():
    stop_bridge()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

# If executed directly in Blender's Text Editor:
if __name__ == "__main__":
    register()
