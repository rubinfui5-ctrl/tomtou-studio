#!/usr/bin/env python3
"""
Market Intelligence - Solomon Empire
Scans for trending opportunities, monitors competitors, analyzes market data
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/market_intelligence")
DATA_DIR.mkdir(parents=True, exist_ok=True)

TRENDS_FILE = DATA_DIR / "trends.json"
OPPORTUNITIES_FILE = DATA_DIR / "opportunities.json"
COMPETITOR_FILE = DATA_DIR / "competitors.json"

TRENDING_NICHES = [
    {"niche": "AI productivity tools", "growth": "+340%", "revenue_potential": "$5K-$50K/mo"},
    {"niche": "Pet wellness supplements", "growth": "+180%", "revenue_potential": "$2K-$20K/mo"},
    {"niche": "Home gym equipment", "growth": "+220%", "revenue_potential": "$3K-$30K/mo"},
    {"niche": "Sustainable packaging", "growth": "+290%", "revenue_potential": "$4K-$40K/mo"},
    {"niche": "Digital planners & templates", "growth": "+160%", "revenue_potential": "$1K-$15K/mo"},
    {"niche": "Crypto & NFT education", "growth": "+400%", "revenue_potential": "$5K-$60K/mo"},
    {"niche": "Remote work accessories", "growth": "+250%", "revenue_potential": "$3K-$35K/mo"},
    {"niche": "Mindfulness & meditation apps", "growth": "+190%", "revenue_potential": "$2K-$25K/mo"},
    {"niche": "Plant-based food delivery", "growth": "+310%", "revenue_potential": "$4K-$45K/mo"},
    {"niche": "Personalized nutrition", "growth": "+270%", "revenue_potential": "$3K-$40K/mo"},
]

PLATFORMS = ["TikTok", "Instagram", "YouTube", "Pinterest", "Twitter", "LinkedIn"]


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


def scan_trends():
    """Scan and identify trending market opportunities."""
    print("  🔍 Scanning market trends...")

    # Simulate trend scanning (replace with real API calls in production)
    trends = []
    sample = random.sample(TRENDING_NICHES, min(5, len(TRENDING_NICHES)))

    for niche_data in sample:
        trend = {
            "id": f"trend_{int(time.time())}_{random.randint(100, 999)}",
            "niche": niche_data["niche"],
            "growth_rate": niche_data["growth"],
            "revenue_potential": niche_data["revenue_potential"],
            "trending_on": random.sample(PLATFORMS, random.randint(2, 4)),
            "confidence_score": round(random.uniform(0.65, 0.95), 2),
            "action_required": "Research and validate",
            "scanned_at": datetime.now().isoformat()
        }
        trends.append(trend)
        print(f"    ✓ Found trend: {niche_data['niche']} ({niche_data['growth']} growth)")

    # Save trends
    existing = load_json(TRENDS_FILE, [])
    existing.extend(trends)
    # Keep last 100 trends
    save_json(TRENDS_FILE, existing[-100:])

    return trends


def identify_opportunities(trends):
    """Convert high-confidence trends into actionable opportunities."""
    opportunities = []

    for trend in trends:
        if trend["confidence_score"] >= 0.75:
            opp = {
                "id": f"opp_{int(time.time())}_{random.randint(100, 999)}",
                "title": f"{trend['niche']} opportunity",
                "description": f"High-growth niche with {trend['growth_rate']} growth trending on {', '.join(trend['trending_on'])}",
                "revenue_potential": trend["revenue_potential"],
                "confidence": trend["confidence_score"],
                "status": "new",
                "created_at": datetime.now().isoformat()
            }
            opportunities.append(opp)

    if opportunities:
        existing = load_json(OPPORTUNITIES_FILE, [])
        existing.extend(opportunities)
        save_json(OPPORTUNITIES_FILE, existing[-50:])
        print(f"  ✓ Identified {len(opportunities)} new opportunities")

    return opportunities


def get_market_summary():
    """Get a summary of current market intelligence."""
    trends = load_json(TRENDS_FILE, [])
    opportunities = load_json(OPPORTUNITIES_FILE, [])

    return {
        "total_trends_tracked": len(trends),
        "opportunities_identified": len(opportunities),
        "new_opportunities": len([o for o in opportunities if o.get("status") == "new"]),
        "top_niches": [t["niche"] for t in trends[-5:]] if trends else [],
        "last_scan": trends[-1]["scanned_at"] if trends else "Never",
        "summary_time": datetime.now().isoformat()
    }


def run_intelligence():
    """Main market intelligence loop."""
    print("🚀 Market Intelligence starting...")

    while True:
        try:
            print(f"\n  📊 Running market scan at {datetime.now().strftime('%H:%M:%S')}")
            trends = scan_trends()
            opportunities = identify_opportunities(trends)

            summary = get_market_summary()
            print(f"  📈 Summary: {summary['total_trends_tracked']} trends tracked, "
                  f"{summary['opportunities_identified']} opportunities identified")

            print(f"  💤 Next scan in 15 minutes...")
            time.sleep(900)

        except KeyboardInterrupt:
            print("\n⏹  Market Intelligence stopped")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_intelligence()
