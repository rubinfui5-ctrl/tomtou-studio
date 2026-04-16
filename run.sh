#!/bin/bash
# ============================================================
#  SOLOMON EMPIRE - LINUX/MAC LAUNCHER
#  Run this to start ALL 10 systems in the background
# ============================================================

clear

echo ""
echo "  ============================================================"
echo "   SOLOMON EMPIRE - LAUNCHING ALL SYSTEMS"
echo "   Daily Target: \$1,428  |  Weekly Target: \$10,000"
echo "   @rubinfuimaono  |  deals.thatsonmeandyou.com"
echo "  ============================================================"
echo ""

# --- Pre-flight check ---
python3 startup-check.py || {
    echo ""
    echo "  Pre-flight failed. Run ./setup.sh first!"
    exit 1
}

echo ""
echo "  Starting all systems in background..."
echo ""

start_system() {
    local num="$1"
    local name="$2"
    local script="$3"
    local log="logs/empire/${script}.log"
    echo "  [$num/10] $name"
    nohup python3 "$script" >"$log" 2>&1 &
    echo "          PID: $!  Log: $log"
    sleep 1
}

start_system "1"  "Revenue Tracker"      "revenue_tracker.py"
start_system "2"  "Content Generator"    "content_generator.py"
start_system "3"  "Email Marketing"      "email_marketing.py"
start_system "4"  "Market Intelligence"  "market_intelligence.py"
start_system "5"  "Shopify Integration"  "shopify_integration.py"
start_system "6"  "API Server"           "api-server.py"
start_system "7"  "Mission Control Hub"  "mission_control_hub.py"
start_system "8"  "Master Control"       "master-control.py"
start_system "9"  "Agent Dashboard"      "mission_control_dashboard.py"
start_system "10" "Empire Auto"          "empire-auto.py"

echo ""
echo "  ============================================================"
echo "   ALL SYSTEMS STARTED (running in background)"
echo "  ============================================================"
echo ""
echo "  Open these in your browser:"
echo ""
echo "    Main Dashboard:  http://localhost:8080"
echo "    Agent Monitor:   http://localhost:5003"
echo "    Master Control:  http://localhost:5002"
echo "    API Status:      http://localhost:5001/status"
echo ""
echo "  To view logs:  tail -f logs/empire/revenue_tracker.py.log"
echo "  To stop all:   pkill -f 'python3 revenue_tracker.py' (etc)"
echo "                 Or run: bash stop.sh"
echo ""
echo "  ============================================================"
echo ""
