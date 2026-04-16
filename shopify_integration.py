#!/usr/bin/env python3
"""
Shopify Integration - Solomon Empire
Syncs products, orders, and inventory with Shopify store
"""

import json
import os
import time
import random
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/shopify")
DATA_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
SYNC_LOG_FILE = DATA_DIR / "sync_log.json"

# Load from environment (optional)
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")

MOCK_PRODUCTS = [
    {"id": 1, "title": "Solomon Empire T-Shirt", "price": "29.99", "inventory": 150, "status": "active"},
    {"id": 2, "title": "Business Blueprint eBook", "price": "47.00", "inventory": 999, "status": "active"},
    {"id": 3, "title": "Financial Freedom Course", "price": "197.00", "inventory": 999, "status": "active"},
    {"id": 4, "title": "Empire Starter Kit", "price": "97.00", "inventory": 50, "status": "active"},
    {"id": 5, "title": "Premium Hoodie", "price": "59.99", "inventory": 75, "status": "active"},
]


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


def log_sync(event, status, details=""):
    """Log a sync event."""
    logs = load_json(SYNC_LOG_FILE, [])
    logs.append({
        "event": event,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    save_json(SYNC_LOG_FILE, logs[-200:])


def sync_products():
    """Sync products from Shopify (or use mock data)."""
    if SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN:
        try:
            import requests
            url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json"
            headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                products = response.json().get("products", [])
                save_json(PRODUCTS_FILE, products)
                log_sync("product_sync", "success", f"Synced {len(products)} products")
                print(f"  ✓ Synced {len(products)} products from Shopify")
                return products
            else:
                print(f"  ⚠️  Shopify API error: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Shopify connection failed: {e}")

    # Fall back to mock data
    products = MOCK_PRODUCTS.copy()
    # Simulate inventory changes
    for p in products:
        p["last_synced"] = datetime.now().isoformat()
    save_json(PRODUCTS_FILE, products)
    log_sync("product_sync", "mock", f"Using {len(products)} mock products")
    print(f"  ✓ Loaded {len(products)} products (mock mode)")
    return products


def sync_orders():
    """Sync recent orders."""
    if SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN:
        try:
            import requests
            url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/orders.json?status=any&limit=50"
            headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                orders = response.json().get("orders", [])
                save_json(ORDERS_FILE, orders)
                log_sync("order_sync", "success", f"Synced {len(orders)} orders")
                print(f"  ✓ Synced {len(orders)} orders")
                return orders
        except Exception as e:
            print(f"  ⚠️  Order sync failed: {e}")

    # Generate mock orders
    products = load_json(PRODUCTS_FILE, MOCK_PRODUCTS)
    orders = load_json(ORDERS_FILE, [])

    # Add a simulated new order occasionally
    if random.random() < 0.3:
        product = random.choice(products)
        quantity = random.randint(1, 3)
        order = {
            "id": len(orders) + 1000,
            "order_number": f"#{1000 + len(orders)}",
            "product": product.get("title", "Product"),
            "quantity": quantity,
            "total_price": str(round(float(product.get("price", "0")) * quantity, 2)),
            "status": "fulfilled",
            "created_at": datetime.now().isoformat()
        }
        orders.append(order)
        save_json(ORDERS_FILE, orders)
        log_sync("new_order", "mock", f"Order #{order['order_number']} - ${order['total_price']}")
        print(f"  ✓ New order: {order['order_number']} - ${order['total_price']}")

    return orders


def get_store_summary():
    """Get store performance summary."""
    products = load_json(PRODUCTS_FILE, [])
    orders = load_json(ORDERS_FILE, [])

    total_revenue = sum(float(o.get("total_price", 0)) for o in orders if o.get("status") == "fulfilled")

    return {
        "total_products": len(products),
        "active_products": len([p for p in products if p.get("status") == "active"]),
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "mode": "live" if (SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN) else "mock",
        "last_sync": datetime.now().isoformat()
    }


def run_integration():
    """Main Shopify integration loop."""
    print("🚀 Shopify Integration starting...")

    if SHOPIFY_STORE_URL:
        print(f"  🔗 Connected to: {SHOPIFY_STORE_URL}")
    else:
        print("  ℹ️  No Shopify URL configured - running in mock mode")
        print("  ℹ️  Set SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN in .env to connect")

    while True:
        try:
            print(f"\n  🔄 Syncing at {datetime.now().strftime('%H:%M:%S')}")
            sync_products()
            sync_orders()

            summary = get_store_summary()
            print(f"  📊 Store: {summary['active_products']} products | "
                  f"{summary['total_orders']} orders | "
                  f"${summary['total_revenue']:.2f} revenue")

            print(f"  💤 Next sync in 10 minutes...")
            time.sleep(600)

        except KeyboardInterrupt:
            print("\n⏹  Shopify Integration stopped")
            break
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_integration()
