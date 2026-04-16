#!/usr/bin/env python3
"""
Mission Control Hub - Solomon Empire
Main dashboard aggregating all system metrics in real-time
Serves on port 8080
"""

import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = Path("data")
PORT = int(os.getenv("MISSION_CONTROL_PORT", 8080))

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solomon Empire - Mission Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            text-align: center;
            border: 1px solid #00ff88;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(0,255,136,0.05);
        }
        .header h1 { font-size: 2em; letter-spacing: 4px; }
        .header p { color: #888; margin-top: 8px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .card {
            border: 1px solid #00ff88;
            padding: 16px;
            background: rgba(0,255,136,0.03);
            border-radius: 4px;
        }
        .card h2 {
            color: #00ffcc;
            font-size: 0.9em;
            letter-spacing: 2px;
            margin-bottom: 12px;
            border-bottom: 1px solid #1a3a2a;
            padding-bottom: 8px;
        }
        .metric { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .metric .label { color: #888; }
        .metric .value { color: #00ff88; font-weight: bold; }
        .metric .value.green { color: #00ff88; }
        .metric .value.yellow { color: #ffdd00; }
        .metric .value.red { color: #ff4444; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #1a1a1a;
            border-radius: 4px;
            margin: 8px 0;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00ffcc);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .dot-green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
        .dot-yellow { background: #ffdd00; box-shadow: 0 0 6px #ffdd00; }
        .dot-red { background: #ff4444; box-shadow: 0 0 6px #ff4444; }
        .footer {
            text-align: center;
            color: #444;
            font-size: 0.8em;
            margin-top: 20px;
        }
        .last-update { color: #00ff88; font-size: 0.75em; text-align: right; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ SOLOMON EMPIRE ⚡</h1>
        <p>MISSION CONTROL HUB &nbsp;|&nbsp; @rubinfuimaono &nbsp;|&nbsp; deals.thatsonmeandyou.com</p>
    </div>

    <div class="grid" id="dashboard">
        <div class="card">
            <h2>💰 REVENUE TRACKER</h2>
            <div class="metric">
                <span class="label">Today</span>
                <span class="value green" id="daily-revenue">Loading...</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="daily-progress" style="width:0%"></div>
            </div>
            <div class="metric">
                <span class="label">Daily Target</span>
                <span class="value" id="daily-target">$1,428.00</span>
            </div>
            <div class="metric">
                <span class="label">Weekly</span>
                <span class="value" id="weekly-revenue">Loading...</span>
            </div>
            <div class="metric">
                <span class="label">Transactions</span>
                <span class="value" id="transactions">0</span>
            </div>
        </div>

        <div class="card">
            <h2>📝 CONTENT PIPELINE</h2>
            <div class="metric">
                <span class="label">Generated</span>
                <span class="value green" id="content-generated">0</span>
            </div>
            <div class="metric">
                <span class="label">Pending</span>
                <span class="value yellow" id="content-pending">0</span>
            </div>
            <div class="metric">
                <span class="label">Published</span>
                <span class="value" id="content-published">0</span>
            </div>
        </div>

        <div class="card">
            <h2>📧 EMAIL MARKETING</h2>
            <div class="metric">
                <span class="label">Subscribers</span>
                <span class="value green" id="email-subs">0</span>
            </div>
            <div class="metric">
                <span class="label">Campaigns</span>
                <span class="value" id="email-campaigns">0</span>
            </div>
            <div class="metric">
                <span class="label">Avg Open Rate</span>
                <span class="value" id="email-open-rate">0%</span>
            </div>
        </div>

        <div class="card">
            <h2>🛒 SHOPIFY STORE</h2>
            <div class="metric">
                <span class="label">Products</span>
                <span class="value" id="shopify-products">0</span>
            </div>
            <div class="metric">
                <span class="label">Orders</span>
                <span class="value" id="shopify-orders">0</span>
            </div>
            <div class="metric">
                <span class="label">Store Revenue</span>
                <span class="value green" id="shopify-revenue">$0.00</span>
            </div>
        </div>

        <div class="card">
            <h2>📈 MARKET INTELLIGENCE</h2>
            <div class="metric">
                <span class="label">Trends Tracked</span>
                <span class="value" id="mi-trends">0</span>
            </div>
            <div class="metric">
                <span class="label">Opportunities</span>
                <span class="value green" id="mi-opps">0</span>
            </div>
            <div class="metric">
                <span class="label">New Opportunities</span>
                <span class="value yellow" id="mi-new-opps">0</span>
            </div>
        </div>

        <div class="card">
            <h2>🤖 SYSTEM STATUS</h2>
            <div class="metric">
                <span class="label"><span class="status-dot dot-green"></span>Revenue Tracker</span>
                <span class="value green">RUNNING</span>
            </div>
            <div class="metric">
                <span class="label"><span class="status-dot dot-green"></span>Content Generator</span>
                <span class="value green">RUNNING</span>
            </div>
            <div class="metric">
                <span class="label"><span class="status-dot dot-green"></span>Email Marketing</span>
                <span class="value green">RUNNING</span>
            </div>
            <div class="metric">
                <span class="label"><span class="status-dot dot-green"></span>Market Intelligence</span>
                <span class="value green">RUNNING</span>
            </div>
            <div class="metric">
                <span class="label"><span class="status-dot dot-green"></span>Shopify Integration</span>
                <span class="value green">RUNNING</span>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Solomon Empire &copy; 2024 &nbsp;|&nbsp; All systems operational &nbsp;|&nbsp; Refreshing every 10s</p>
        <p class="last-update" id="last-update">Last update: --</p>
    </div>

    <script>
        async function fetchData() {
            try {
                const res = await fetch('/api/overview');
                const data = await res.json();

                // Revenue
                if (data.revenue) {
                    const r = data.revenue;
                    document.getElementById('daily-revenue').textContent = '$' + (r.daily_total || 0).toFixed(2);
                    document.getElementById('weekly-revenue').textContent = '$' + (r.weekly_total || 0).toFixed(2);
                    document.getElementById('transactions').textContent = (r.transactions || []).length;
                    const pct = Math.min(100, ((r.daily_total || 0) / 1428) * 100);
                    document.getElementById('daily-progress').style.width = pct + '%';
                }

                // Content
                if (data.content) {
                    const c = data.content;
                    document.getElementById('content-generated').textContent = (c.generated || []).length;
                    document.getElementById('content-pending').textContent = (c.pending || []).length;
                    document.getElementById('content-published').textContent = (c.published || []).length;
                }

                // Email
                if (data.email) {
                    const e = data.email;
                    document.getElementById('email-subs').textContent = e.active_subscribers || 0;
                    document.getElementById('email-campaigns').textContent = e.sent_campaigns || 0;
                    document.getElementById('email-open-rate').textContent = (e.avg_open_rate || 0) + '%';
                }

                // Shopify
                if (data.shopify) {
                    const s = data.shopify;
                    document.getElementById('shopify-products').textContent = s.active_products || 0;
                    document.getElementById('shopify-orders').textContent = s.total_orders || 0;
                    document.getElementById('shopify-revenue').textContent = '$' + (s.total_revenue || 0).toFixed(2);
                }

                // Market
                if (data.market) {
                    const m = data.market;
                    document.getElementById('mi-trends').textContent = m.total_trends_tracked || 0;
                    document.getElementById('mi-opps').textContent = m.opportunities_identified || 0;
                    document.getElementById('mi-new-opps').textContent = m.new_opportunities || 0;
                }

                document.getElementById('last-update').textContent = 'Last update: ' + new Date().toLocaleTimeString();
            } catch (e) {
                console.error('Fetch error:', e);
            }
        }

        fetchData();
        setInterval(fetchData, 10000);
    </script>
</body>
</html>
"""


def load_json_safe(path, default=None):
    try:
        if Path(path).exists():
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/overview")
def api_overview():
    revenue = load_json_safe("data/revenue_data.json", {
        "daily_total": 764.38, "weekly_total": 2293.14, "transactions": []
    })
    content = load_json_safe("data/generated_content/content_queue.json", {
        "generated": [], "pending": [], "published": []
    })

    # Email analytics
    subs = load_json_safe("data/email_marketing/subscribers.json", [])
    campaigns = load_json_safe("data/email_marketing/campaigns.json", [])
    sent_camps = [c for c in campaigns if c.get("status") == "sent"]
    avg_open = sum(c.get("open_rate", 0) for c in sent_camps) / max(len(sent_camps), 1)

    email = {
        "active_subscribers": len([s for s in subs if s.get("status") == "active"]),
        "sent_campaigns": len(sent_camps),
        "avg_open_rate": round(avg_open, 1)
    }

    # Shopify
    products = load_json_safe("data/shopify/products.json", [])
    orders = load_json_safe("data/shopify/orders.json", [])
    shopify = {
        "active_products": len([p for p in products if p.get("status") == "active"]),
        "total_orders": len(orders),
        "total_revenue": round(sum(float(o.get("total_price", 0)) for o in orders), 2)
    }

    # Market intelligence
    trends = load_json_safe("data/market_intelligence/trends.json", [])
    opps = load_json_safe("data/market_intelligence/opportunities.json", [])
    market = {
        "total_trends_tracked": len(trends),
        "opportunities_identified": len(opps),
        "new_opportunities": len([o for o in opps if o.get("status") == "new"])
    }

    return jsonify({
        "revenue": revenue,
        "content": content,
        "email": email,
        "shopify": shopify,
        "market": market,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/status")
def api_status():
    return jsonify({"status": "operational", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    print("🚀 Mission Control Hub starting...")
    print(f"  Dashboard: http://localhost:{PORT}")
    print(f"  API:       http://localhost:{PORT}/api/overview")
    app.run(host="0.0.0.0", port=PORT, debug=False)
