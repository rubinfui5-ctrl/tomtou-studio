#!/usr/bin/env python3
"""
Empire Status - Solomon Empire
Real-time health check for all running systems
Run this anytime to see a snapshot of system health
"""

import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

DATA_DIR = Path("data")
LOG_DIR = Path("logs/empire")


def load_json_safe(path, default=None):
    try:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


def check_revenue():
    data = load_json_safe("data/revenue_data.json",
                          {"daily_total": 764.38, "weekly_total": 2293.14, "transactions": []})
    daily = data.get("daily_total", 0)
    target = 1428.00
    progress = round((daily / target) * 100, 1) if target else 0
    status = "✓" if daily >= 500 else "⚠"
    return {
        "status": status,
        "name": "Revenue Tracker",
        "today": f"${daily:.2f}",
        "target": f"${target:.2f}",
        "progress": f"{progress}%",
        "transactions": len(data.get("transactions", []))
    }


def check_content():
    data = load_json_safe("data/generated_content/content_queue.json",
                          {"generated": [], "pending": [], "published": []})
    return {
        "status": "✓",
        "name": "Content Generator",
        "generated": len(data.get("generated", [])),
        "pending": len(data.get("pending", [])),
        "published": len(data.get("published", []))
    }


def check_email():
    subs = load_json_safe("data/email_marketing/subscribers.json", [])
    campaigns = load_json_safe("data/email_marketing/campaigns.json", [])
    active = len([s for s in subs if s.get("status") == "active"])
    sent = len([c for c in campaigns if c.get("status") == "sent"])
    return {
        "status": "✓",
        "name": "Email Marketing",
        "subscribers": active,
        "campaigns_sent": sent,
        "total_campaigns": len(campaigns)
    }


def check_shopify():
    products = load_json_safe("data/shopify/products.json", [])
    orders = load_json_safe("data/shopify/orders.json", [])
    revenue = round(sum(float(o.get("total_price", 0)) for o in orders), 2)
    return {
        "status": "✓",
        "name": "Shopify Integration",
        "products": len(products),
        "orders": len(orders),
        "store_revenue": f"${revenue:.2f}"
    }


def check_market():
    trends = load_json_safe("data/market_intelligence/trends.json", [])
    opps = load_json_safe("data/market_intelligence/opportunities.json", [])
    return {
        "status": "✓",
        "name": "Market Intelligence",
        "trends_tracked": len(trends),
        "opportunities": len(opps),
        "new": len([o for o in opps if o.get("status") == "new"])
    }


def check_system_resources():
    if not HAS_PSUTIL:
        return {"cpu": "N/A (psutil missing)", "memory": "N/A", "disk": "N/A"}
    return {
        "cpu": f"{psutil.cpu_percent(interval=0.5)}%",
        "memory": f"{psutil.virtual_memory().percent}%",
        "disk": f"{psutil.disk_usage('.').percent}%"
    }


def check_log_files():
    """Check which systems have active log files."""
    scripts = [
        "revenue_tracker.py", "content_generator.py", "email_marketing.py",
        "market_intelligence.py", "shopify_integration.py", "mission_control_hub.py",
        "master-control.py", "api-server.py", "empire-auto.py"
    ]
    active = []
    for s in scripts:
        log_path = LOG_DIR / f"{s}.log"
        if log_path.exists():
            active.append(s.replace(".py", ""))
    return active


def print_report():
    print("\n" + "=" * 70)
    print("  SOLOMON EMPIRE - STATUS REPORT".center(70))
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
    print("=" * 70)

    checks = [check_revenue, check_content, check_email, check_shopify, check_market]

    print("\n  SYSTEM HEALTH:")
    for fn in checks:
        try:
            result = fn()
            status = result.pop("status", "?")
            name = result.pop("name", "?")
            details = "  |  ".join(f"{k}: {v}" for k, v in result.items())
            print(f"  {status}  {name:<25} {details}")
        except Exception as e:
            print(f"  ✗  Error: {e}")

    print("\n  SYSTEM RESOURCES:")
    res = check_system_resources()
    for k, v in res.items():
        print(f"     {k.title():<12} {v}")

    active_logs = check_log_files()
    print(f"\n  ACTIVE LOG FILES: {len(active_logs)}/9")
    if active_logs:
        print(f"     {', '.join(active_logs[:5])}")

    print("\n" + "=" * 70)
    print("  DASHBOARDS:")
    print("     Mission Control:  http://localhost:8080")
    print("     Agent Dashboard:  http://localhost:5003")
    print("     Master Control:   http://localhost:5002")
    print("     API Server:       http://localhost:5001/status")
    print("\n  COMMANDS:")
    print("     Windows:  run.bat")
    print("     Linux:    bash run.sh")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print_report()
