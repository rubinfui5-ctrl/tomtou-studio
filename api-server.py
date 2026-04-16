#!/usr/bin/env python3
"""
API Server - Solomon Empire
Central REST API for all Solomon Empire systems
Runs on port 5001
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv("API_SERVER_PORT", 5001))
DATA_DIR = Path("data")


def load_json_safe(path, default=None):
    try:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


@app.route("/")
@app.route("/status")
def status():
    """API health check and system overview."""
    return jsonify({
        "status": "operational",
        "system": "Solomon Empire API",
        "version": "1.0.0",
        "endpoints": [
            "/status",
            "/api/revenue",
            "/api/content",
            "/api/email",
            "/api/shopify",
            "/api/market",
            "/api/snapshot"
        ],
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/revenue")
def api_revenue():
    data = load_json_safe("data/revenue_data.json", {
        "daily_total": 764.38,
        "weekly_total": 2293.14,
        "monthly_total": 9173.00,
        "transactions": [],
        "targets": {"daily": 1428.00, "weekly": 10000.00}
    })
    daily = data.get("daily_total", 0)
    target = data.get("targets", {}).get("daily", 1428.00)
    data["progress_pct"] = round((daily / target) * 100, 1) if target else 0
    return jsonify(data)


@app.route("/api/content")
def api_content():
    data = load_json_safe("data/generated_content/content_queue.json", {
        "generated": [], "pending": [], "published": []
    })
    return jsonify({
        "generated_count": len(data.get("generated", [])),
        "pending_count": len(data.get("pending", [])),
        "published_count": len(data.get("published", [])),
        "recent": data.get("generated", [])[-5:]
    })


@app.route("/api/email")
def api_email():
    subs = load_json_safe("data/email_marketing/subscribers.json", [])
    campaigns = load_json_safe("data/email_marketing/campaigns.json", [])
    sent = [c for c in campaigns if c.get("status") == "sent"]
    avg_open = sum(c.get("open_rate", 0) for c in sent) / max(len(sent), 1)

    return jsonify({
        "total_subscribers": len(subs),
        "active_subscribers": len([s for s in subs if s.get("status") == "active"]),
        "total_campaigns": len(campaigns),
        "sent_campaigns": len(sent),
        "avg_open_rate": round(avg_open, 1),
        "total_emails_sent": sum(c.get("sent", 0) for c in sent)
    })


@app.route("/api/shopify")
def api_shopify():
    products = load_json_safe("data/shopify/products.json", [])
    orders = load_json_safe("data/shopify/orders.json", [])
    return jsonify({
        "total_products": len(products),
        "active_products": len([p for p in products if p.get("status") == "active"]),
        "total_orders": len(orders),
        "total_revenue": round(sum(float(o.get("total_price", 0)) for o in orders), 2)
    })


@app.route("/api/market")
def api_market():
    trends = load_json_safe("data/market_intelligence/trends.json", [])
    opps = load_json_safe("data/market_intelligence/opportunities.json", [])
    return jsonify({
        "total_trends": len(trends),
        "opportunities": len(opps),
        "new_opportunities": len([o for o in opps if o.get("status") == "new"]),
        "top_trends": trends[-5:] if trends else []
    })


@app.route("/api/snapshot")
def api_snapshot():
    """Full system snapshot."""
    return jsonify({
        "system": "Solomon Empire",
        "timestamp": datetime.now().isoformat(),
        "revenue": load_json_safe("data/revenue_data.json", {}),
        "email": {
            "subscribers": len(load_json_safe("data/email_marketing/subscribers.json", [])),
            "campaigns": len(load_json_safe("data/email_marketing/campaigns.json", []))
        },
        "shopify": {
            "products": len(load_json_safe("data/shopify/products.json", [])),
            "orders": len(load_json_safe("data/shopify/orders.json", []))
        },
        "market": {
            "trends": len(load_json_safe("data/market_intelligence/trends.json", [])),
            "opportunities": len(load_json_safe("data/market_intelligence/opportunities.json", []))
        }
    })


if __name__ == "__main__":
    print(f"🚀 API Server running at http://localhost:{PORT}")
    print(f"  Health check: http://localhost:{PORT}/status")
    app.run(host="0.0.0.0", port=PORT, debug=False)
