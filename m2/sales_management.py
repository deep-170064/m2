# sales_management.py
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission, get_current_user, get_current_name

engine = get_engine()

# ----------------- Process Sale (Cashier/Manager/Admin) -----------------
def process_sale():
    """Process a new sale. Uses currently logged-in employee as employee_id."""
    if not has_permission(["CASHIER", "MANAGER", "ADMIN"]):
        return

    cart = []
    total = 0.0
    current_user = get_current_user()
    current_name = get_current_name()

    while True:
        # Import here to avoid circular import
        from product_management import view_products
        view_products()
        
        product_id = input("Enter Product ID (or 'done' to finish): ").strip()
        if product_id.lower() == 'done':
            break

        try:
            pid = int(product_id)
        except ValueError:
            print("❌ Invalid Product ID. Try again.")
            continue

        try:
            quantity = int(input("Enter quantity: ").strip())
            if quantity <= 0:
                print("❌ Quantity must be positive.")
                continue
        except ValueError:
            print("❌ Invalid number. Try again.")
            continue

        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT name, price, stock_quantity
                    FROM products
                    WHERE product_id = :pid
                """), {"pid": pid})
                product_data = result.fetchone()

            if not product_data:
                print("❌ Product ID not found.")
                continue
            if product_data[2] < quantity:
                print(f"❌ Only {product_data[2]} units in stock.")
                continue

            item_total = float(product_data[1]) * quantity
            cart.append({
                'product_id': pid,
                'name': product_data[0],
                'price': float(product_data[1]),
                'quantity': quantity,
                'item_total': item_total
            })
            total += item_total
            print(f"✅ Added {quantity} x {product_data[0]}. Item Total: ₹{item_total:.2f}")

        except Exception as e:
            print(f"❌ Database error: {e}")
            return

    if not cart:
        print("❌ Cart is empty. Sale cancelled.")
        return

    # Payment
    print(f"\nTotal Amount: ₹{total:.2f}")
    payment_method = input("Enter payment method (CASH/CARD/UPI/WALLET): ").strip().upper()
    if payment_method not in ('CASH', 'CARD', 'UPI', 'WALLET'):
        print("❌ Invalid payment method. Sale cancelled.")
        return

    customer_id = input("Enter customer ID (or leave blank if walk-in): ").strip() or None

    try:
        with engine.begin() as conn:
            # Validate customer if provided
            if customer_id:
                res = conn.execute(text("SELECT 1 FROM customers WHERE customer_id = :cid"), {"cid": customer_id})
                if res.fetchone() is None:
                    print("❌ Invalid customer ID. Sale cancelled.")
                    return

            # Insert sale using the current_user as employee_id
            result = conn.execute(text("""
                INSERT INTO sales (total_amount, payment_method, customer_id, employee_id)
                VALUES (:total, :pm, :cid, :eid)
                RETURNING sale_id
            """), {
                "total": round(total, 2),
                "pm": payment_method,
                "cid": customer_id,
                "eid": current_user
            })
            sale_id_row = result.fetchone()
            if not sale_id_row:
                raise RuntimeError("Failed to create sale record.")
            sale_id = sale_id_row[0]

            # Insert sale items
            for item in cart:
                conn.execute(text("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price)
                    VALUES (:sale_id, :pid, :qty, :price)
                """), {
                    "sale_id": sale_id,
                    "pid": item['product_id'],
                    "qty": item['quantity'],
                    "price": item['price']
                })

        print("🎉 Sale completed successfully!")
        print(f"🧾 Sale ID: {sale_id} | Total: ₹{total:.2f} | Cashier: {current_name}")

    except Exception as e:
        print(f"❌ Transaction cancelled due to error: {e}")