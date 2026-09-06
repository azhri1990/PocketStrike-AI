#!/usr/bin/env python3
# ==============================================
# POCKETSTRIKE-AI — ULTIMATE JARVIS COMMANDER
# ==============================================

import os
import json
import subprocess
import shlex
import time
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration ---
CONFIG_PATH = os.path.expanduser("~/PocketStrike-AI/config.json")
OMNIROUTE_KEY = "sk-5f238e76072d7926-92f903-faf6b924xE"
OMNIROUTE_URL = "http://localhost:20128/v1"

# --- Default Config ---
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {
        "ai_provider": "openai",
        "openai": {
            "api_key": OMNIROUTE_KEY,
            "base_url": OMNIROUTE_URL,
            "model": "qoder/qoder"
        }
    }

config = load_config()

# --- Command Execution ---
def run_shell_command(command, timeout=60):
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            executable="/data/data/com.termux/files/usr/bin/bash"
        )
        if result.stdout:
            return result.stdout.strip()
        elif result.stderr:
            return f"⚠️ Error: {result.stderr.strip()}"
        else:
            return "✅ Command executed (no output)"
    except subprocess.TimeoutExpired:
        return "⏰ Command timed out after 60 seconds"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Jarvis Commander ---
def jarvis_commander(command):
    """Main command router for Ultimate Jarvis."""
    command = command.lower().strip()
    
    # --- HELP ---
    if command in ["help", "?"]:
        return """
╔═══════════════════════════════════════════════╗
║         JARVIS COMMANDER — HELP               ║
╠═══════════════════════════════════════════════╣
║  🔹 SYSTEM CONTROL                            ║
║    run automator          - Open automator    ║
║    status / check status  - Show system      ║
║    stop pocketstrike      - Stop Strike      ║
║    restart strike         - Restart Strike   ║
║                                               ║
║  🔹 MODEL CONTROL                             ║
║    switch to MODEL        - Switch AI model  ║
║    list models            - Show models      ║
║    current model          - Show current     ║
║                                               ║
║  🔹 LAUNCH PROJECTS                           ║
║    launch rehan           - RehanIlyas       ║
║    launch isair           - isair-jarvis     ║
║    launch offgrid         - Off Grid APK     ║
║    launch automator       - Automator        ║
║    launch omniroute       - OmniRoute        ║
║                                               ║
║  🔹 OMNROUTE                                  ║
║    omniroute status       - Check OmniRoute  ║
║    omniroute restart      - Restart          ║
║                                               ║
║  🔹 GENERAL                                   ║
║    help / ?               - Show this menu   ║
╚═══════════════════════════════════════════════╝
"""
    
    # --- AUTOMATOR ---
    if command == "run automator" or command == "automator":
        return run_shell_command("cd ~/my-automator && ./automator.sh")
    
    # --- STATUS ---
    if command in ["status", "check status"]:
        status = "╔═══════════════════════════════════════════════╗\n"
        status += "║         JARVIS SYSTEM STATUS                 ║\n"
        status += "╠═══════════════════════════════════════════════╣\n"
        
        # OmniRoute
        omniroute = run_shell_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:20128 2>/dev/null")
        if omniroute == "200":
            status += "║  ✅ OmniRoute:             Running            ║\n"
        else:
            status += "║  ❌ OmniRoute:             Not running        ║\n"
        
        # PocketStrike
        ps = run_shell_command("pgrep -f 'python server.py'")
        if ps:
            status += f"║  ✅ PocketStrike-AI:       Running (PID: {ps.strip()}) ║\n"
        else:
            status += "║  ❌ PocketStrike-AI:       Not running        ║\n"
        
        # Current Model
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            model = cfg.get('openai', {}).get('model', 'Unknown')
            status += f"║  🧠 Current Model:        {model[:30]} ║\n"
        except:
            status += "║  🧠 Current Model:        Unknown            ║\n"
        
        # Automator
        if os.path.exists(os.path.expanduser("~/my-automator/automator.sh")):
            status += "║  ✅ Automator:             Available          ║\n"
        else:
            status += "║  ❌ Automator:             Not found          ║\n"
        
        # OmniRoute key
        status += f"║  🔑 OmniRoute Key:        {'✅ Set' if OMNIROUTE_KEY else '❌ Missing'} ║\n"
        
        status += "╚═══════════════════════════════════════════════╝"
        return status
    
    # --- STOP POCKETSTRIKE ---
    if command == "stop pocketstrike" or command == "stop":
        run_shell_command("pkill -f 'python server.py'")
        return "🛑 PocketStrike-AI stopped. Run 'restart strike' to start again."
    
    # --- RESTART POCKETSTRIKE ---
    if command == "restart strike":
        run_shell_command("pkill -f 'python server.py'")
        time.sleep(1)
        run_shell_command("cd ~/PocketStrike-AI && python server.py &")
        return "🔄 Restarting PocketStrike-AI..."
    
    # --- CURRENT MODEL ---
    if command == "current model":
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            model = cfg.get('openai', {}).get('model', 'Unknown')
            provider = cfg.get('ai_provider', 'Unknown')
            return f"🧠 Current Model: {model}\n📡 Provider: {provider}"
        except:
            return "❌ Could not read config."
    
    # --- LIST MODELS ---
    if command == "list models":
        result = run_shell_command(
            f"curl -s {OMNIROUTE_URL}/models -H 'Authorization: Bearer {OMNIROUTE_KEY}' | grep -o '\"id\":\"[^\"]*\"' | head -30 | sed 's/\"id\":\"//g' | sed 's/\"//g'"
        )
        if result:
            models = result.split('\n')
            output = "📋 Available Models:\n"
            for i, m in enumerate(models, 1):
                if m:
                    output += f"  {i}. {m}\n"
            return output
        return "❌ No models found or OmniRoute not running."
    
    # --- SWITCH MODEL ---
    if command.startswith("switch to "):
        model = command.replace("switch to", "").strip()
        if not model:
            return "❌ Usage: switch to MODEL_NAME (e.g., switch to qoder/qoder)"
        
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            cfg['openai']['model'] = model
            with open(CONFIG_PATH, 'w') as f:
                json.dump(cfg, f, indent=2)
            
            # Restart to apply changes
            run_shell_command("pkill -f 'python server.py'")
            time.sleep(1)
            run_shell_command("cd ~/PocketStrike-AI && python server.py &")
            return f"✅ Switched to model: {model}\n🔄 Restarting PocketStrike-AI..."
        except Exception as e:
            return f"❌ Error switching model: {str(e)}"
    
    # --- LAUNCH PROJECTS ---
    if command.startswith("launch ") or command.startswith("start "):
        project = command.replace("launch", "").replace("start", "").strip()
        
        projects = {
            "rehan": "cd ~/jarvis-mega-repo/assistants/RehanIlyas-JARVIS && python main.py",
            "isair": "cd ~/jarvis-mega-repo/assistants/isair-jarvis && python jarvis.py",
            "offgrid": "termux-open ~/downloads/offgrid.apk",
            "automator": "cd ~/my-automator && ./automator.sh",
            "omniroute": "omniroute",
            "llama": "cd ~/llama.cpp && ./build/bin/llama-server -m Phi-3-mini-4k-instruct-Q4_K_M.gguf --host 127.0.0.1 --port 11434 -t 4 --ctx-size 2048",
        }
        
        if project in projects:
            run_shell_command(projects[project] + " &")
            return f"🚀 Launching {project.title()}..."
        else:
            available = ", ".join(projects.keys())
            return f"❌ Unknown project: {project}\n📋 Available: {available}"
    
    # --- OMNROUTE STATUS ---
    if command == "omniroute status":
        return run_shell_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:20128 2>/dev/null")
    
    # --- OMNROUTE RESTART ---
    if command == "omniroute restart":
        run_shell_command("pkill -f omniroute")
        time.sleep(2)
        run_shell_command("omniroute &")
        return "🔄 Restarting OmniRoute..."
    
    # --- GENERATE IMAGE ---
    if command.startswith("draw ") or command.startswith("generate image "):
        prompt = command.replace("draw", "").replace("generate image", "").strip()
        if not prompt:
            return "❌ Please specify what to draw."
        
        result = run_shell_command(
            f"curl -s -X POST {OMNIROUTE_URL}/chat/completions -H 'Content-Type: application/json' -H 'Authorization: Bearer {OMNIROUTE_KEY}' -d '{{\"model\":\"aihorde/SDXL 1.0\",\"messages\":[{{\"role\":\"user\",\"content\":\"Generate an image: {prompt}\"}}]}}' | grep -o 'https://[^\"]*' | head -1"
        )
        if result and result.startswith("http"):
            return f"🖼️ Image generated:\n{result}"
        return "❌ Could not generate image. Check OmniRoute and AI Horde connection."
    
    # --- UNKNOWN ---
    return f"❓ Unknown command: {command}\nType 'help' for available commands."

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        # Check for Jarvis commands first
        if user_message.startswith(("run ", "switch to ", "list ", "launch ", "start ", "stop ", "status", "check ", "help", "?", "draw ", "generate image", "current model", "omniroute ", "restart strike")):
            response = jarvis_commander(user_message)
            return jsonify({"response": response})
        
        # Otherwise, send to AI via OmniRoute
        try:
            import requests
            payload = {
                "model": config.get('openai', {}).get('model', 'qoder/qoder'),
                "messages": [{"role": "user", "content": user_message}],
                "stream": False
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.get('openai', {}).get('api_key', OMNIROUTE_KEY)}"
            }
            url = config.get('openai', {}).get('base_url', OMNIROUTE_URL) + "/chat/completions"
            
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            if resp.status_code == 200:
                result = resp.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', "No response")
                return jsonify({"response": ai_response})
            else:
                return jsonify({"response": f"⚠️ AI Error: {resp.status_code} - {resp.text[:100]}"})
        except Exception as e:
            return jsonify({"response": f"❌ AI Connection Error: {str(e)}"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(config)

@app.route('/config', methods=['POST'])
def update_config():
    global config
    data = request.json
    config = data
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    # Ensure config exists
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    
    print("""
╔═══════════════════════════════════════════════╗
║         ULTIMATE JARVIS COMMANDER              ║
╠═══════════════════════════════════════════════╣
║  🚀 Strike is now your full commander!        ║
║  📋 Type 'help' in the chat for commands      ║
║  🎙️  Voice: "Hey Strike" + command            ║
║                                               ║
║  🌐 Web UI: http://127.0.0.1:5000             ║
╚═══════════════════════════════════════════════╝
""")
    app.run(host='0.0.0.0', port=5000, debug=False)
