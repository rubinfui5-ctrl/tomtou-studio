#!/bin/bash
# ============================================================
#  SOLOMON EMPIRE - LINUX/MAC SETUP (run this ONCE)
# ============================================================

set -e
clear

echo ""
echo "  ============================================================"
echo "   SOLOMON EMPIRE - SETUP"
echo "  ============================================================"
echo ""

# --- Check Python ---
echo "  [1/4] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found."
    echo "  Mac:   brew install python3"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi
python3 --version
echo ""

# --- Install packages ---
echo "  [2/4] Installing required packages..."
pip3 install -r requirements.txt
echo "  Packages installed."
echo ""

# --- Create directories ---
echo "  [3/4] Creating data directories..."
mkdir -p data/generated_content data/email_marketing \
         data/market_intelligence data/shopify data/reports \
         logs/empire memory
echo "  Directories ready."
echo ""

# --- Pre-flight check ---
echo "  [4/4] Running pre-flight check..."
python3 startup-check.py || {
    echo ""
    echo "  Fix the issues above then run ./setup.sh again."
    exit 1
}

echo ""
echo "  ============================================================"
echo "   SETUP COMPLETE!"
echo "  ============================================================"
echo ""
echo "  Next: Run   bash run.sh   to start all 10 systems."
echo ""
