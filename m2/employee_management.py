# employee_management.py
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
import getpass
from auth import has_permission, hash_password
from report import fetch_report

engine = get_engine()

# ----------------- Admin: Manage Employees -----------------
def manage_employees():
    """Admin can list and add employees (with username & password)."""
    if not has_permission(["ADMIN"]):
        return

    while True:
        print("\n--- Employee Management (Admin) ---")
        print("1. List Employees")
        print("2. Add Employee")
        print("3. Employee Performance")
        print("4. Back to Main Menu")
        choice = input("Choose: ").strip()

        if choice == '1':
            list_employees()
        elif choice == '2':
            add_employee()
        elif choice == '3':
            employee_performance()
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice.")


def list_employees():
    """List all employees"""
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT employee_id, name, username, role FROM employees ORDER BY employee_id;"))
            rows = res.fetchall()
        if not rows:
            print("\n⚠️ No employees found.\n")
            return
        data = [dict(employee_id=r[0], name=r[1], username=r[2], role=r[3]) for r in rows]
        print(tabulate(data, headers="keys", tablefmt="psql"))
    except Exception as e:
        print("❌ Error listing employees:", e)


def add_employee():
    """Add a new employee"""
    try:
        name = input("Name: ").strip()
        role = input("Role (ADMIN/CASHIER/MANAGER): ").strip().upper()
        if role not in ('ADMIN', 'CASHIER', 'MANAGER'):
            print("❌ Invalid role. Must be ADMIN, CASHIER or MANAGER.")
            return
        username = input("Username (unique): ").strip()
        password = getpass.getpass("Password: ").strip()
        if not (name and username and password):
            print("❌ All fields required.")
            return

        stored_password = hash_password(password)
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO employees (name, role, username, password)
                VALUES (:name, :role, :username, :password)
            """), {
                "name": name,
                "role": role,
                "username": username,
                "password": stored_password
            })
        print("✅ Employee added successfully!")
    except Exception as e:
        print("❌ Error adding employee:", e)


def employee_performance():
    """Track sales performance by employee"""
    query = """
        SELECT e.employee_id, e.name, e.role,
               COUNT(s.sale_id) as sales_processed,
               SUM(s.total_amount) as total_revenue,
               ROUND(AVG(s.total_amount), 2) as avg_sale_value
        FROM employees e
        LEFT JOIN sales s ON e.employee_id = s.employee_id
        WHERE s.sale_time >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY e.employee_id, e.name, e.role
        ORDER BY total_revenue DESC
    """
    fetch_report(query, "Employee Performance (Last 30 Days)", "employee_performance")