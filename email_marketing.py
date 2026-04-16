#!/usr/bin/env python3
"""
Email Marketing Engine - Solomon Empire
Manages subscribers, campaigns, and automated sequences
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data/email_marketing")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"
SEQUENCES_FILE = DATA_DIR / "sequences.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"


def load_json(path, default=None):
    if default is None:
        default = []
    if Path(path).exists():
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_subscribers():
    return load_json(SUBSCRIBERS_FILE, [])


def save_subscribers(subs):
    save_json(SUBSCRIBERS_FILE, subs)


def add_subscriber(email, name="", tags=None):
    """Add a new subscriber."""
    subs = load_subscribers()

    # Check for duplicates
    if any(s["email"] == email for s in subs):
        print(f"  ℹ️  Subscriber already exists: {email}")
        return None

    sub = {
        "id": len(subs) + 1,
        "email": email,
        "name": name,
        "tags": tags or ["general"],
        "status": "active",
        "subscribed_at": datetime.now().isoformat(),
        "open_count": 0,
        "click_count": 0
    }
    subs.append(sub)
    save_subscribers(subs)
    print(f"  ✓ Subscriber added: {email}")
    return sub


def get_subscriber_count():
    return len([s for s in load_subscribers() if s.get("status") == "active"])


def create_campaign(name, subject, body, tags=None):
    """Create a new email campaign."""
    campaigns = load_json(CAMPAIGNS_FILE, [])

    campaign = {
        "id": len(campaigns) + 1,
        "name": name,
        "subject": subject,
        "body": body,
        "tags": tags or ["general"],
        "status": "draft",
        "sent": 0,
        "opens": 0,
        "clicks": 0,
        "open_rate": 0.0,
        "click_rate": 0.0,
        "created_at": datetime.now().isoformat(),
        "sent_at": None
    }

    campaigns.append(campaign)
    save_json(CAMPAIGNS_FILE, campaigns)
    print(f"  ✓ Campaign created: {name}")
    return campaign


def send_campaign(campaign_id):
    """Simulate sending a campaign."""
    campaigns = load_json(CAMPAIGNS_FILE, [])
    subs = [s for s in load_subscribers() if s.get("status") == "active"]

    for camp in campaigns:
        if camp["id"] == campaign_id:
            camp["status"] = "sent"
            camp["sent"] = len(subs)
            camp["sent_at"] = datetime.now().isoformat()

            # Simulate realistic open/click rates
            open_rate = random.uniform(0.18, 0.35)
            click_rate = random.uniform(0.02, 0.08)
            camp["opens"] = int(len(subs) * open_rate)
            camp["clicks"] = int(len(subs) * click_rate)
            camp["open_rate"] = round(open_rate * 100, 1)
            camp["click_rate"] = round(click_rate * 100, 1)

            save_json(CAMPAIGNS_FILE, campaigns)
            print(f"  ✓ Campaign sent to {len(subs)} subscribers")
            print(f"    Open rate: {camp['open_rate']}% | Click rate: {camp['click_rate']}%")
            return camp

    print(f"  ⚠️  Campaign {campaign_id} not found")
    return None


def get_analytics():
    """Get email marketing analytics summary."""
    campaigns = load_json(CAMPAIGNS_FILE, [])
    subs = load_subscribers()

    active_subs = len([s for s in subs if s.get("status") == "active"])
    sent_campaigns = [c for c in campaigns if c.get("status") == "sent"]

    avg_open_rate = 0.0
    avg_click_rate = 0.0
    total_sent = 0

    if sent_campaigns:
        avg_open_rate = sum(c.get("open_rate", 0) for c in sent_campaigns) / len(sent_campaigns)
        avg_click_rate = sum(c.get("click_rate", 0) for c in sent_campaigns) / len(sent_campaigns)
        total_sent = sum(c.get("sent", 0) for c in sent_campaigns)

    return {
        "active_subscribers": active_subs,
        "total_campaigns": len(campaigns),
        "sent_campaigns": len(sent_campaigns),
        "total_emails_sent": total_sent,
        "avg_open_rate": round(avg_open_rate, 1),
        "avg_click_rate": round(avg_click_rate, 1)
    }


def run_email_engine():
    """Main email marketing loop."""
    print("🚀 Email Marketing Engine starting...")

    # Seed some demo subscribers if empty
    if get_subscriber_count() == 0:
        demo_emails = [
            ("demo1@example.com", "Alex"),
            ("demo2@example.com", "Sam"),
            ("demo3@example.com", "Jordan"),
        ]
        for email, name in demo_emails:
            add_subscriber(email, name)
        print(f"  ✓ Seeded {len(demo_emails)} demo subscribers")

    iteration = 0
    while True:
        try:
            iteration += 1
            analytics = get_analytics()

            print(f"\n  📧 Email Marketing Status:")
            print(f"     Subscribers: {analytics['active_subscribers']}")
            print(f"     Campaigns sent: {analytics['sent_campaigns']}")
            print(f"     Avg open rate: {analytics['avg_open_rate']}%")
            print(f"     Avg click rate: {analytics['avg_click_rate']}%")

            # Auto-create and send a campaign periodically
            if iteration % 12 == 0:
                subjects = [
                    "🔥 New opportunity you can't miss",
                    "💰 This week's top performing strategy",
                    "📈 Revenue update from Solomon Empire",
                ]
                camp = create_campaign(
                    f"Auto Campaign #{iteration}",
                    random.choice(subjects),
                    "This is an automated campaign from Solomon Empire.",
                    tags=["auto"]
                )
                send_campaign(camp["id"])

            time.sleep(300)

        except KeyboardInterrupt:
            print("\n⏹  Email Marketing Engine stopped")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    run_email_engine()
