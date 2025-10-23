# inventory_management.py
from sqlalchemy import text
from db import get_engine
from auth import has_permission

engine = get_engine()

def restock_products():
    """Manage product restocking with supplier coordination"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
    
    try:
        # Show products needing restock
        with engine.connect() as conn:
            low_stock = conn.execute(text("""
                SELECT p.product_id, p.name, p.stock_quantity, 
                       p.low_stock_threshold, s.name as supplier,
                       s.contact_info
                FROM products p
                JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE p.stock_quantity < p.low_stock_threshold
                ORDER BY p.stock_quantity ASC
            """)).fetchall()
            
            if not low_stock:
                print("✅ All products are sufficiently stocked!")
                return
            
            print("\n🔄 PRODUCTS NEEDING RESTOCK:")
            for product in low_stock:
                print(f"📦 {product[1]} - Stock: {product[2]}/{product[3]}")
                print(f"   Supplier: {product[4]} | Contact: {product[5]}")
                print(f"   Product ID: {product[0]}")
                print("-" * 50)
                
            # Restock interface
            product_id = input("Enter Product ID to restock (or 'cancel'): ").strip()
            if product_id.lower() == 'cancel':
                return
                
            quantity = int(input("Enter restock quantity: ").strip())
            
            # Update stock
            conn.execute(text("""
                UPDATE products 
                SET stock_quantity = stock_quantity + :qty
                WHERE product_id = :pid
            """), {"qty": quantity, "pid": int(product_id)})
            
            print(f"✅ Restocked {quantity} units successfully!")
            
    except Exception as e:
        print(f"❌ Restock error: {e}")

def bulk_stock_update():
    """Update multiple products stock at once"""
    if not has_permission(["ADMIN"]):
        return
    
    print("\n📦 BULK STOCK UPDATE")
    print("Enter product ID and new quantity (enter 'done' to finish)")
    
    updates = []
    while True:
        pid = input("Product ID: ").strip()
        if pid.lower() == 'done':
            break
        try:
            qty = int(input("New Quantity: ").strip())
            updates.append((int(pid), qty))
        except ValueError:
            print("❌ Invalid input")
            
    if updates:
        try:
            with engine.begin() as conn:
                for pid, qty in updates:
                    conn.execute(text("""
                        UPDATE products SET stock_quantity = :qty 
                        WHERE product_id = :pid
                    """), {"qty": qty, "pid": pid})
                print(f"✅ Updated {len(updates)} products!")
        except Exception as e:
            print(f"❌ Bulk update failed: {e}")