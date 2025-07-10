import os
import time
from datetime import datetime
from pathlib import Path
import subprocess

LOG_DIR = "/var/log"
OUTPUT_FILE = f"/var/log/ollama_digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
MODEL = "mistral"  # change to your preferred Ollama model

# --- Step 1: Read Logs ---
def collect_logs():
    logs = {}
    for file in ["syslog", "auth.log", "kern.log", "boot.log"]:
        path = os.path.join(LOG_DIR, file)
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    logs[file] = f.read()[-5000:]  # only last 5000 chars to avoid overload
            except Exception as e:
                logs[file] = f"Failed to read: {e}"
    return logs

# --- Step 2: Send to Ollama ---
def run_ollama_prompt(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode(),
            capture_output=True,
            timeout=60
        )
        return result.stdout.decode(errors="ignore")
    except Exception as e:
        return f"Error running ollama: {e}"

# --- Step 3: Main Logic ---
def main():
    logs = collect_logs()
    with open(OUTPUT_FILE, "w") as out:
        out.write(f"🧠 OLLAMA SYSTEM LOG DIGEST - {datetime.now()}\n\n")
        for name, content in logs.items():
            prompt = f"""
You are a Linux system admin AI assistant. Analyze the following log file ({name}). Identify:

1. Any major issues (failures, errors)
2. Their likely cause
3. Suggested shell commands to fix

Log:
