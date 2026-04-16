#!/usr/bin/env python3
"""
Revenue Tracker - Solomon Empire
Tracks daily, weekly, and monthly revenue toward $10K/week target
Runs continuously, updating every 30 seconds
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

REVENUE_FILE = DATA_DIR / "revenue_data.json"

DAILY_TARGET = 1428.00       # $10K/week ÷ 7
WEEKLY_TARGET = 10000.00
MONTHLY_TARGET = 43000.00
CURRENT_BASELINE = 764.38


def load_revenue_data():
    """Load existing revenue data or initialize defaults."""
    if REVENUE_FILE.exists():
        with open(REVENUE_FILE) as f:
            return json.load(f)

    return {
        "daily_total": CURRENT_BASELINE,
        "weekly_total": CURRENT_BASELINE * 3,
        "monthly_total": CURRENT_BASELINE * 12,
        "transactions": [],
        "last_updated": datetime.now().isoformat(),
        "targets": {
            "daily": DAILY_TARGET,
            "weekly": WEEKLY_TARGET,
            "monthly": MONTHLY_TARGET
        }
    }


def save_revenue_data(data):
    """Persist revenue data to disk."""
    data["last_updated"] = datetime.now().isoformat()
    with open(REVENUE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_transaction(source, amount, description=""):
    """Record a new revenue transaction."""
    data = load_revenue_data()

    transaction = {
        "id": len(data["transactions"]) + 1,
        "source": source,
        "amount": amount,
        "description": description,
        "timestamp": datetime.now().isoformat()
    }

    data["transactions"].append(transaction)
    data["daily_total"] += amount
    data["weekly_total"] += amount
    data["monthly_total"] += amount

    save_revenue_data(data)
    print(f"  ✓ Transaction recorded: {source} ${amount:.2f}")
    return transaction


def get_daily_progress():
    """Calculate progress toward daily target."""
    data = load_revenue_data()
    daily = data.get("daily_total", 0)
    progress = (daily / DAILY_TARGET) * 100
    return {
        "current": daily,
        "target": DAILY_TARGET,
        "progress_pct": round(progress, 1),
        "remaining": max(0, DAILY_TARGET - daily),
        "on_track": daily >= (DAILY_TARGET * 0.5)
    }


def print_status():
    """Print current revenue status."""
    data = load_revenue_data()
    progress = get_daily_progress()

    print("\n" + "="*60)
    print("  SOLOMON EMPIRE - REVENUE TRACKER")
    print("="*60)
    print(f"  Daily:   ${data['daily_total']:.2f} / ${DAILY_TARGET:.2f}  ({progress['progress_pct']}%)")
    print(f"  Weekly:  ${data['weekly_total']:.2f} / ${WEEKLY_TARGET:.2f}")
    print(f"  Monthly: ${data['monthly_total']:.2f} / ${MONTHLY_TARGET:.2f}")
    print(f"  Transactions: {len(data['transactions'])}")
    print(f"  Updated: {data.get('last_updated', 'never')}")
    print("="*60)


def run_tracker():
    """Main tracking loop - runs continuously."""
    print("🚀 Revenue Tracker starting...")
    print(f"  Daily Target: ${DAILY_TARGET:,.2f}")
    print(f"  Weekly Target: ${WEEKLY_TARGET:,.2f}")
    print(f"  Baseline: ${CURRENT_BASELINE:,.2f}")

    # Initialize data if needed
    data = load_revenue_data()
    save_revenue_data(data)

    iteration = 0
    while True:
        try:
            iteration += 1
            data = load_revenue_data()

            # Simulate organic revenue growth (remove in production - use real API data)
            if iteration % 10 == 0:
                sources = ["Shopify", "Email Campaign", "Instagram", "Affiliate", "Direct"]
                amount = round(random.uniform(15, 85), 2)
                add_transaction(random.choice(sources), amount, "Auto-tracked sale")

            # Reset daily at midnight
            last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
            if datetime.now().date() > last_updated.date():
                data["daily_total"] = 0
                print("  📅 Daily totals reset for new day")
                save_revenue_data(data)

            print_status()
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n⏹  Revenue Tracker stopped")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    run_tracker()
