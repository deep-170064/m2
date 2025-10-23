# customer_management.py
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission

engine = get_engine()

def manage_customers():
    """Customer management system"""
    while True:
        print("\n👥 CUSTOMER MANAGEMENT")
        print("1. View All Customers")
        print("2. Add New Customer")
        print("3. Customer Purchase History")
        print("4. Back to Main Menu")
        
        choice = input("Choose: ").strip()
        
        if choice == '1':
            view_customers()
        elif choice == '2':
            add_customer()
        elif choice == '3':
            customer_purchase_history()
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice")

def view_customers():
    """Display all customers"""
    try:
        with engine.connect() as conn:
            customers = conn.execute(text("""
                SELECT customer_id, name, phone, email, 
                       address, created_at
                FROM customers 
                ORDER BY customer_id
            """)).fetchall()
            
            if not customers:
                print("📭 No customers found")
                return
                
            data = [dict(customer_id=r[0], name=r[1], phone=r[2], 
                        email=r[3], address=r[4], joined=r[5].strftime('%Y-%m-%d')) 
                    for r in customers]
            print(tabulate(data, headers="keys", tablefmt="psql"))
            
    except Exception as e:
        print(f"❌ Error: {e}")

def add_customer():
    """Add new customer to database"""
    try:
        name = input("Full Name: ").strip()
        phone = input("Phone: ").strip()
        email = input("Email (optional): ").strip() or None
        address = input("Address (optional): ").strip() or None
        
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO customers (name, phone, email, address)
                VALUES (:name, :phone, :email, :address)
            """), {
                "name": name, "phone": phone, 
                "email": email, "address": address
            })
            print("✅ Customer added successfully!")
            
    except Exception as e:
        print(f"❌ Error adding customer: {e}")

def customer_purchase_history():
    """View customer purchase history"""
    try:
        customer_id = input("Enter Customer ID: ").strip()
        if not customer_id:
            return
            
        with engine.connect() as conn:
            # Verify customer exists
            customer = conn.execute(text("""
                SELECT name FROM customers WHERE customer_id = :cid
            """), {"cid": int(customer_id)}).fetchone()
            
            if not customer:
                print("❌ Customer not found")
                return
                
            # Get purchase history
            history = conn.execute(text("""
                SELECT s.sale_id, s.sale_time, s.total_amount, 
                       s.payment_method, e.name as cashier
                FROM sales s
                JOIN employees e ON s.employee_id = e.employee_id
                WHERE s.customer_id = :cid
                ORDER BY s.sale_time DESC
                LIMIT 20
            """), {"cid": int(customer_id)}).fetchall()
            
            print(f"\n🛒 Purchase History for: {customer[0]}")
            if not history:
                print("No purchases found")
                return
                
            data = [dict(sale_id=r[0], date=r[1].strftime('%Y-%m-%d %H:%M'),
                        amount=f"₹{r[2]:.2f}", method=r[3], cashier=r[4])
                    for r in history]
            print(tabulate(data, headers="keys", tablefmt="psql"))
            
    except Exception as e:
        print(f"❌ Error: {e}")