
# product_management.py
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission, get_current_user, get_current_name

engine = get_engine()

# ----------------- Add Product (Admin only) -----------------
def add_product():
    """Adds a new product to the inventory. Admin only."""
    if not has_permission(["ADMIN"]):
        return
        
    try:
        name = input("Enter product name: ").strip()
        barcode = input("Enter product barcode (optional, press Enter to skip): ").strip() or None
        price = float(input("Enter product price: ").strip())
        stock = int(input("Enter initial stock quantity: ").strip())
        category_id = int(input("Enter category ID: ").strip())
        supplier_id = int(input("Enter supplier ID: ").strip())
        low_stock_threshold = int(input("Enter low stock threshold (default 10): ").strip() or 10)
    except ValueError:
        print("❌ Invalid input. Please enter numbers for price, stock, and IDs.")
        return

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO products (name, barcode, price, stock_quantity, category_id, supplier_id, low_stock_threshold)
                VALUES (:name, :barcode, :price, :stock, :category_id, :supplier_id, :threshold)
            """), {
                "name": name,
                "barcode": barcode,
                "price": price,
                "stock": stock,
                "category_id": category_id,
                "supplier_id": supplier_id,
                "threshold": low_stock_threshold
            })
        print("✅ Product added successfully!")
    except Exception as e:
        print(f"❌ Error adding product: {e}")


# ----------------- View Products (All roles) -----------------
def view_products():
    """Displays product inventory in a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT product_id, name, price, stock_quantity, low_stock_threshold 
                FROM products ORDER BY product_id;
            """))
            rows = result.fetchall()

        if not rows:
            print("\n⚠️ No products found.\n")
            return

        df = [dict(product_id=r[0], name=r[1], price=float(r[2]), stock_quantity=r[3], low_stock_threshold=r[4]) for r in rows]
        print("\n--- Product Inventory ---")
        print(tabulate(df, headers="keys", tablefmt="psql"))
        print("-------------------------\n")
    except Exception as e:
        print(f"❌ Error fetching products: {e}")


# ----------------- Set Stock Thresholds -----------------
def set_stock_thresholds():
    """Allow managers to set custom low-stock thresholds"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        view_products()
        product_id = input("Enter product ID to update threshold: ").strip()
        new_threshold = input("Enter new low stock threshold: ").strip()
        
        if not product_id or not new_threshold:
            print("❌ Product ID and threshold are required.")
            return
            
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE products 
                SET low_stock_threshold = :threshold 
                WHERE product_id = :pid
                RETURNING name
            """), {"threshold": int(new_threshold), "pid": int(product_id)})
            
            updated_product = result.fetchone()
            if updated_product:
                print(f"✅ Threshold updated for '{updated_product[0]}' to {new_threshold}")
            else:
                print("❌ Product not found.")
                
    except ValueError:
        print("❌ Please enter valid numbers.")
    except Exception as e:
        print(f"❌ Error updating threshold: {e}")