#!/bin/bash
# ============================================================
#  SOLOMON EMPIRE - STOP ALL SYSTEMS (Linux/Mac)
# ============================================================

echo ""
echo "  Stopping all Solomon Empire systems..."
echo ""

scripts=(
    "revenue_tracker.py"
    "content_generator.py"
    "email_marketing.py"
    "market_intelligence.py"
    "shopify_integration.py"
    "api-server.py"
    "mission_control_hub.py"
    "master-control.py"
    "mission_control_dashboard.py"
    "empire-auto.py"
)

for script in "${scripts[@]}"; do
    if pgrep -f "$script" >/dev/null 2>&1; then
        pkill -f "$script"
        echo "  Stopped: $script"
    else
        echo "  Not running: $script"
    fi
done

echo ""
echo "  All systems stopped."
echo ""
