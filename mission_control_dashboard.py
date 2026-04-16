#!/usr/bin/env python3
"""
Mission Control Dashboard - Solomon Empire
Agent status monitor running on port 5003
"""

import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
BASE_DIR = Path(__file__).resolve().parent

AGENTS = [
    ("Revenue Tracker",     "revenue_tracker.py"),
    ("Content Generator",   "content_generator.py"),
    ("Email Marketing",     "email_marketing.py"),
    ("Market Intelligence", "market_intelligence.py"),
    ("Shopify Integration", "shopify_integration.py"),
    ("Mission Control Hub", "mission_control_hub.py"),
    ("Master Control",      "master-control.py"),
    ("API Server",          "api-server.py"),
    ("Empire Auto",         "empire-auto.py"),
]

status_data = {name: "unknown" for name, _ in AGENTS}
last_checked = {"time": "Never"}


def read_last_line(log_path: Path) -> str:
    try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return lines[-1].strip() if lines else ""
    except OSError:
        return ""


def monitor_agents():
    while True:
        for name, script in AGENTS:
            # Check if the script file exists
            script_path = BASE_DIR / script
            if not script_path.exists():
                status_data[name] = "not found"
                continue

            # Check log file
            log_path = BASE_DIR / "logs" / "empire" / f"{script}.log"
            if log_path.exists():
                last_line = read_last_line(log_path)
                if not last_line:
                    status_data[name] = "idle"
                elif any(t in last_line.lower() for t in ["error", "traceback", "exception", "crashed"]):
                    status_data[name] = "error"
                else:
                    status_data[name] = "running"
            else:
                status_data[name] = "ready"  # File exists, no log yet = ready to start

        last_checked["time"] = datetime.now().strftime("%H:%M:%S")
        time.sleep(10)


@app.route("/")
def dashboard():
    rows = "".join(
        f"""<tr>
            <td>{name}</td>
            <td class="{st}">{st.upper()}</td>
            <td>{'✓' if st == 'running' else '—'}</td>
        </tr>"""
        for name, st in status_data.items()
    )
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Dashboard - Solomon Empire</title>
        <style>
            body {{ font-family: monospace; background: #0a0a0a; color: #00ff88; padding: 20px; }}
            h1 {{ letter-spacing: 3px; margin-bottom: 4px; }}
            p {{ color: #888; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #1a3a2a; padding: 10px; text-align: left; }}
            th {{ background: #001a0d; color: #00ffcc; }}
            .running {{ color: #00ff88; }}
            .ready {{ color: #00aaff; }}
            .idle {{ color: #888; }}
            .error {{ color: #ff4444; }}
            .unknown {{ color: #ffdd00; }}
            .not.found {{ color: #ff8800; }}
        </style>
    </head>
    <body>
        <h1>📊 AGENT DASHBOARD</h1>
        <p>Last checked: {last_checked['time']} &nbsp;|&nbsp; Auto-refresh every 10s</p>
        <table>
            <tr><th>Agent</th><th>Status</th><th>Active</th></tr>
            {rows}
        </table>
        <script>setTimeout(() => location.reload(), 10000);</script>
    </body>
    </html>
    """)


@app.route("/api/status")
def api_status():
    return jsonify({
        "agents": status_data,
        "last_checked": last_checked["time"],
        "timestamp": datetime.now().isoformat()
    })


if __name__ == "__main__":
    threading.Thread(target=monitor_agents, daemon=True).start()
    print("🚀 Agent Dashboard running at http://localhost:5003")
    app.run(host="0.0.0.0", port=5003, debug=False)
