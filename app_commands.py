#!/data/data/com.termux/files/usr/bin/python3
import subprocess
import json

def launch_app(app_name):
    """Launch any app by name"""
    try:
        result = subprocess.run(
            ["~/bin/app_launcher", "launch", app_name],
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"

def list_apps():
    """List all available apps"""
    apps = {
        "ai": ["ChatGPT", "Claude", "Gemini", "DeepSeek", "Kimi", "Perplexity", "Copilot", "Manus"],
        "image": ["BananaAI", "NanoBanana", "StickerMaker", "GPTImage", "NanoAI", "NanoImageGen", "AIReel", "Snapseed"],
        "git": ["Gitflow", "GitSync", "GitNomad", "Gitmux"],
        "termux": ["TermuxToolbox", "TermuxPowerTools", "SpckEditor", "VSCodroid", "TermuxTutor", "TermuxNinja", "TermuxHandbook"]
    }
    return apps

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            print(json.dumps(list_apps(), indent=2))
        elif sys.argv[1] == "launch":
            print(launch_app(" ".join(sys.argv[2:])))
