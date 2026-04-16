#!/usr/bin/env python3
"""
Master Control - Solomon Empire
Orchestrates all autonomous agents and provides control dashboard
Runs on port 5002
"""

import json
import os
import subprocess
import threading
import time
import signal
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

try:
    from business_memory import (
        add_business_opportunity,
        add_conversation,
        get_memory_snapshot,
        get_openclaw_payload,
        initialize_database,
    )
except ImportError:
    print("⚠️  business_memory not found - using stubs")
    def initialize_database(): pass
    def get_memory_snapshot(): return {"status": "memory not loaded"}
    def get_openclaw_payload(): return {}
    def add_business_opportunity(*a, **kw): return {}
    def add_conversation(*a, **kw): return {}

ROOT_DIR = Path(__file__).parent
PORT = 5002

AGENTS = {
    "revenue_tracker": {
        "name": "Revenue Tracker",
        "script": "revenue_tracker.py",
        "process": None,
        "status": "stopped",
        "restarts": 0,
    },
    "content_generator": {
        "name": "Content Generator",
        "script": "content_generator.py",
        "process": None,
        "status": "stopped",
        "restarts": 0,
    },
    "email_marketing": {
        "name": "Email Marketing",
        "script": "email_marketing.py",
        "process": None,
        "status": "stopped",
        "restarts": 0,
    },
    "market_intelligence": {
        "name": "Market Intelligence",
        "script": "market_intelligence.py",
        "process": None,
        "status": "stopped",
        "restarts": 0,
    },
    "shopify_integration": {
        "name": "Shopify Integration",
        "script": "shopify_integration.py",
        "process": None,
        "status": "stopped",
        "restarts": 0,
    },
}

LOGS = []
app = Flask(__name__)
CORS(app)


def log_event(msg, level="info"):
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "msg": msg,
        "level": level,
    }
    LOGS.append(entry)
    print(f"  [{level.upper()}] {msg}")
    if len(LOGS) > 500:
        LOGS.pop(0)


def start_agent(key):
    agent = AGENTS[key]
    script = ROOT_DIR / agent["script"]
    if not script.exists():
        log_event(f"Script not found: {script}", "warning")
        agent["status"] = "missing"
        return

    if agent["process"] and agent["process"].poll() is None:
        log_event(f"{agent['name']} already running (PID {agent['process'].pid})")
        return

    agent["process"] = subprocess.Popen(
        ["python", str(script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(ROOT_DIR),
    )
    agent["status"] = "running"
    log_event(f"Started {agent['name']} (PID {agent['process'].pid})")


def stop_agent(key):
    agent = AGENTS[key]
    if agent["process"] and agent["process"].poll() is None:
        agent["process"].terminate()
        agent["status"] = "stopped"
        log_event(f"Stopped {agent['name']}")


def monitor_loop():
    """Watch agents and restart crashed ones."""
    while True:
        for key, agent in AGENTS.items():
            proc = agent["process"]
            if proc and proc.poll() is not None and agent["status"] == "running":
                agent["status"] = "crashed"
                agent["restarts"] += 1
                log_event(f"{agent['name']} crashed (restart #{agent['restarts']})", "error")
                time.sleep(2)
                start_agent(key)
        time.sleep(5)


@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Master Control - Solomon Empire</title>
        <style>
            body { font-family: monospace; background: #0a0a0a; color: #00ff88; padding: 20px; }
            h1 { letter-spacing: 3px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #1a3a2a; padding: 10px; text-align: left; }
            th { background: #001a0d; color: #00ffcc; }
            .running { color: #00ff88; }
            .stopped { color: #888; }
            .crashed { color: #ff4444; }
            .missing { color: #ffdd00; }
        </style>
    </head>
    <body>
        <h1>🎛️ MASTER CONTROL</h1>
        <p>Orchestrating Solomon Empire agents &nbsp;|&nbsp; <a href='/api/agents' style='color:#00ffcc'>JSON API</a></p>
        <table>
            <tr><th>Agent</th><th>Status</th><th>Restarts</th></tr>
            {% for key, agent in agents.items() %}
            <tr>
                <td>{{ agent.name }}</td>
                <td class="{{ agent.status }}">{{ agent.status.upper() }}</td>
                <td>{{ agent.restarts }}</td>
            </tr>
            {% endfor %}
        </table>
        <p style='margin-top:20px; color:#444; font-size:0.8em'>Auto-refreshes every 10s</p>
        <script>setTimeout(() => location.reload(), 10000);</script>
    </body>
    </html>
    """, agents=AGENTS)


@app.route("/api/agents")
def api_agents():
    return jsonify({
        k: {"name": v["name"], "status": v["status"], "restarts": v["restarts"]}
        for k, v in AGENTS.items()
    })


@app.route("/api/logs")
def api_logs():
    return jsonify(LOGS[-100:])


@app.route("/api/memory")
def api_memory():
    return jsonify(get_memory_snapshot())


@app.route("/api/start/<key>", methods=["POST"])
def api_start(key):
    if key in AGENTS:
        start_agent(key)
        return jsonify({"ok": True, "status": AGENTS[key]["status"]})
    return jsonify({"error": "unknown agent"}), 404


@app.route("/api/stop/<key>", methods=["POST"])
def api_stop(key):
    if key in AGENTS:
        stop_agent(key)
        return jsonify({"ok": True})
    return jsonify({"error": "unknown agent"}), 404


if __name__ == "__main__":
    initialize_database()
    log_event("Master Control starting...")

    # Start monitoring thread
    threading.Thread(target=monitor_loop, daemon=True).start()

    print(f"\n🚀 Master Control running at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
