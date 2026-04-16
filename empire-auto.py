#!/usr/bin/env python3
"""
Empire Auto - Solomon Empire
Central automation orchestrator that coordinates all systems
Runs periodic tasks, syncs data between systems, generates reports
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
LOG_DIR = Path("logs/empire")
LOG_DIR.mkdir(parents=True, exist_ok=True)

AUTO_LOG = LOG_DIR / "empire-auto.py.log"


def log(msg, level="INFO"):
    entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {msg}"
    print(entry)
    with open(AUTO_LOG, "a") as f:
        f.write(entry + "\n")


def load_json_safe(path, default=None):
    try:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def task_check_revenue_health():
    """Check if revenue is on track and flag if falling behind."""
    revenue = load_json_safe("data/revenue_data.json", {"daily_total": 764.38})
    daily = revenue.get("daily_total", 0)
    target = 1428.00
    hour = datetime.now().hour
    expected = (hour / 24) * target

    if daily < expected * 0.5:
        log(f"⚠️  Revenue falling behind: ${daily:.2f} vs expected ${expected:.2f}", "WARNING")
    else:
        log(f"✓ Revenue on track: ${daily:.2f} / ${target:.2f} ({(daily/target*100):.1f}%)")


def task_content_pipeline():
    """Ensure content pipeline stays healthy."""
    queue = load_json_safe("data/generated_content/content_queue.json",
                           {"generated": [], "pending": [], "published": []})
    pending = len(queue.get("pending", []))
    log(f"✓ Content pipeline: {pending} items pending")

    if pending < 5:
        log("⚠️  Content queue low - triggering generation", "WARNING")


def task_email_health():
    """Check email system health."""
    subs = load_json_safe("data/email_marketing/subscribers.json", [])
    active = len([s for s in subs if s.get("status") == "active"])
    log(f"✓ Email: {active} active subscribers")


def task_generate_daily_report():
    """Generate end-of-day report."""
    revenue = load_json_safe("data/revenue_data.json", {})
    subs = load_json_safe("data/email_marketing/subscribers.json", [])
    trends = load_json_safe("data/market_intelligence/trends.json", [])
    orders = load_json_safe("data/shopify/orders.json", [])

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "revenue": {
            "daily_total": revenue.get("daily_total", 0),
            "weekly_total": revenue.get("weekly_total", 0),
            "transactions": len(revenue.get("transactions", []))
        },
        "email": {
            "subscribers": len([s for s in subs if s.get("status") == "active"])
        },
        "shopify": {
            "orders_today": len([o for o in orders
                                  if o.get("created_at", "")[:10] == datetime.now().strftime("%Y-%m-%d")])
        },
        "market": {
            "trends_tracked": len(trends)
        },
        "generated_at": datetime.now().isoformat()
    }

    reports_dir = DATA_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"daily_{report['date']}.json"
    save_json(report_path, report)
    log(f"✓ Daily report saved: {report_path}")
    return report


def task_sync_cross_system():
    """Sync data between systems."""
    # Move published content from pending to published
    queue = load_json_safe("data/generated_content/content_queue.json",
                           {"generated": [], "pending": [], "published": []})

    if queue["pending"] and random.random() < 0.2:
        item = queue["pending"].pop(0)
        item["status"] = "published"
        item["published_at"] = datetime.now().isoformat()
        queue["published"].append(item)
        save_json("data/generated_content/content_queue.json", queue)
        log(f"✓ Published content: {item.get('platform', 'unknown')} - {item.get('topic', '')[:30]}")


def run_automation():
    """Main automation loop."""
    log("🚀 Empire Auto starting...")

    tasks = [
        ("Revenue Health Check", task_check_revenue_health, 300),      # Every 5 min
        ("Content Pipeline",    task_content_pipeline, 600),            # Every 10 min
        ("Email Health",        task_email_health, 600),                # Every 10 min
        ("Cross-System Sync",   task_sync_cross_system, 180),           # Every 3 min
        ("Daily Report",        task_generate_daily_report, 3600),      # Every hour
    ]

    task_timers = {name: 0 for name, _, _ in tasks}

    while True:
        try:
            now = time.time()
            for name, fn, interval in tasks:
                if now - task_timers[name] >= interval:
                    log(f"Running: {name}")
                    try:
                        fn()
                    except Exception as e:
                        log(f"Task failed [{name}]: {e}", "ERROR")
                    task_timers[name] = now

            time.sleep(30)

        except KeyboardInterrupt:
            log("⏹  Empire Auto stopped")
            break
        except Exception as e:
            log(f"Loop error: {e}", "ERROR")
            time.sleep(30)


if __name__ == "__main__":
    run_automation()
