import pandas as pd
from sqlalchemy import create_engine

# ── Connection ───────────────────────────────────────────
engine = create_engine(
    "postgresql+psycopg2://postgres:Deadshotff%40152@localhost:5432/retail_profit_leak"
)

print("=" * 55)
print("   GREAT EXPECTATIONS — DATA VALIDATION REPORT")
print("=" * 55)

results = []

def check(table, rule, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append((table, rule, status, details))
    print(f"\n{status}")
    print(f"  Table : {table}")
    print(f"  Rule  : {rule}")
    if details:
        print(f"  Detail: {details}")

# ═══════════════════════════════════════════════════════
# TABLE 1 — orders
# ═══════════════════════════════════════════════════════
df_orders = pd.read_sql("SELECT * FROM orders", engine)

# Rule 1: order_id must never be null
null_count = df_orders['order_id'].isnull().sum()
check(
    table   = "orders",
    rule    = "order_id must never be null",
    passed  = null_count == 0,
    details = f"{null_count} nulls found"
)

# Rule 2: order_id must be unique
dupe_count = df_orders['order_id'].duplicated().sum()
check(
    table   = "orders",
    rule    = "order_id must be unique",
    passed  = dupe_count == 0,
    details = f"{dupe_count} duplicates found"
)

# Rule 3: order_status must only contain known values
known_statuses = {
    'delivered', 'shipped', 'canceled',
    'unavailable', 'invoiced', 'processing',
    'approved', 'created'
}
unknown = df_orders[~df_orders['order_status'].isin(known_statuses)]
check(
    table   = "orders",
    rule    = "order_status must be a known value",
    passed  = len(unknown) == 0,
    details = f"{len(unknown)} unknown status values found"
)

# ═══════════════════════════════════════════════════════
# TABLE 2 — order_items
# ═══════════════════════════════════════════════════════
df_items = pd.read_sql("SELECT * FROM order_items", engine)

# Rule 4: price must be greater than 0
bad_price = df_items[df_items['price'] <= 0]
check(
    table   = "order_items",
    rule    = "price must be greater than 0",
    passed  = len(bad_price) == 0,
    details = f"{len(bad_price)} rows with price <= 0"
)

# Rule 5: freight_value must be 0 or more
bad_freight = df_items[df_items['freight_value'] < 0]
check(
    table   = "order_items",
    rule    = "freight_value must be >= 0",
    passed  = len(bad_freight) == 0,
    details = f"{len(bad_freight)} rows with negative freight"
)

# Rule 6: order_id must never be null
null_order = df_items['order_id'].isnull().sum()
check(
    table   = "order_items",
    rule    = "order_id must never be null",
    passed  = null_order == 0,
    details = f"{null_order} nulls found"
)

# ═══════════════════════════════════════════════════════
# TABLE 3 — products
# ═══════════════════════════════════════════════════════
df_products = pd.read_sql("SELECT * FROM products", engine)

# Rule 7: product_weight_g must be greater than 0
bad_weight = df_products[
    df_products['product_weight_g'].isnull() |
    (df_products['product_weight_g'] <= 0)
]
check(
    table   = "products",
    rule    = "product_weight_g must be > 0",
    passed  = len(bad_weight) == 0,
    details = f"{len(bad_weight)} rows with missing or zero weight"
)

# Rule 8: report how many products have no category
null_cat = df_products['product_category_name'].isnull().sum()
check(
    table   = "products",
    rule    = "product_category_name null count (info only)",
    passed  = True,
    details = f"{null_cat} products have no category name"
)

# ═══════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("   SUMMARY")
print("=" * 55)
total   = len(results)
passed  = sum(1 for r in results if "PASS" in r[2])
failed  = total - passed
print(f"   Total checks : {total}")
print(f"   Passed       : {passed}")
print(f"   Failed       : {failed}")
print("=" * 55)