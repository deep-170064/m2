# analytics.py
from sqlalchemy import text
from db import get_engine
from auth import has_permission
from report import fetch_report

engine = get_engine()

# ----------------- Notification Center -----------------
def notification_center():
    """Display and manage all system notifications"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.begin() as conn:
            # Get unread notifications
            notifications = conn.execute(text("""
                SELECT notification_id, message, created_at, notification_type
                FROM notifications 
                WHERE status = 'unread'
                ORDER BY created_at DESC
            """)).fetchall()
            
            if not notifications:
                print("\n📭 No new notifications!")
                return
            
            print("\n🔔 UNREAD NOTIFICATIONS")
            print("=" * 50)
            for notif in notifications:
                print(f"📌 {notif[1]}")
                print(f"   ⏰ {notif[2].strftime('%Y-%m-%d %H:%M')} | Type: {notif[3]}")
                print("-" * 40)
            
            # Mark as read when viewed
            conn.execute(text("""
                UPDATE notifications 
                SET status = 'read', read_at = CURRENT_TIMESTAMP 
                WHERE status = 'unread'
            """))
            print(f"\n✅ Marked {len(notifications)} notifications as read")
            
    except Exception as e:
        print(f"❌ Error accessing notifications: {e}")


# ----------------- Alert Dashboard -----------------
def alert_dashboard():
    """Show critical alerts to managers/admins"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # Low stock alerts
            low_stock = conn.execute(text("""
                SELECT p.product_id, p.name, p.stock_quantity, p.low_stock_threshold
                FROM products p
                WHERE p.stock_quantity < p.low_stock_threshold
                ORDER BY p.stock_quantity ASC
            """)).fetchall()
            
            # Zero stock alerts
            zero_stock = conn.execute(text("""
                SELECT product_id, name FROM products 
                WHERE stock_quantity = 0
            """)).fetchall()
            
            print("\n🚨 CRITICAL ALERTS DASHBOARD")
            print("=" * 60)
            
            if zero_stock:
                print("\n❌ OUT OF STOCK ITEMS:")
                for product in zero_stock:
                    print(f"   • {product[1]} (ID: {product[0]})")
            
            if low_stock:
                print("\n⚠️  LOW STOCK ITEMS:")
                for product in low_stock:
                    print(f"   • {product[1]} - Only {product[2]} left (Threshold: {product[3]})")
            
            if not zero_stock and not low_stock:
                print("✅ No critical alerts! All stock levels are good.")
                
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Error loading alerts: {e}")


# ----------------- Analytics Reports -----------------
def category_sales_report():
    """Sales breakdown by category"""
    query = """
        SELECT c.name as category, 
               COUNT(si.sale_item_id) as items_sold,
               SUM(si.quantity * si.unit_price) as revenue
        FROM sale_items si
        JOIN products p ON si.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_id, c.name
        ORDER BY revenue DESC
    """
    fetch_report(query, "Category Sales Report", "category_sales")


def supplier_performance():
    """Analyze supplier performance and reliability"""
    query = """
        SELECT s.supplier_id, s.name, s.contact_info,
               COUNT(p.product_id) as products_supplied,
               SUM(p.stock_quantity) as current_stock_value
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        GROUP BY s.supplier_id, s.name, s.contact_info
        ORDER BY products_supplied DESC
    """
    fetch_report(query, "Supplier Performance", "supplier_report")


def peak_hours_analysis():
    """Identify busiest store hours"""
    query = """
        SELECT EXTRACT(HOUR FROM sale_time) as hour_of_day,
               COUNT(sale_id) as transaction_count,
               ROUND(AVG(total_amount), 2) as avg_sale_amount,
               SUM(total_amount) as total_revenue
        FROM sales
        GROUP BY EXTRACT(HOUR FROM sale_time)
        ORDER BY transaction_count DESC
    """
    fetch_report(query, "Peak Hours Analysis", "peak_hours")


def customer_analytics():
    """Customer purchase patterns and loyalty"""
    query = """
        SELECT c.customer_id, c.name, c.phone, c.email,
               COUNT(s.sale_id) as total_visits,
               SUM(s.total_amount) as total_spent,
               MAX(s.sale_time) as last_visit
        FROM customers c
        LEFT JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id, c.name, c.phone, c.email
        HAVING COUNT(s.sale_id) > 0
        ORDER BY total_spent DESC
    """
    fetch_report(query, "Customer Analytics", "customer_analytics")


def predictive_restocking():
    """Predict which products will need restocking soon"""
    query = """
        SELECT p.product_id, p.name, p.stock_quantity, 
               p.low_stock_threshold,
               COALESCE(SUM(si.quantity), 0) as weekly_sales,
               CASE 
                   WHEN COALESCE(SUM(si.quantity), 0) = 0 THEN 999
                   ELSE ROUND(p.stock_quantity / NULLIF(SUM(si.quantity), 0) * 7, 2)
               END as days_remaining
        FROM products p
        LEFT JOIN sale_items si ON p.product_id = si.product_id
        LEFT JOIN sales s ON si.sale_id = s.sale_id
        WHERE s.sale_time >= CURRENT_DATE - INTERVAL '7 days' OR s.sale_time IS NULL
        GROUP BY p.product_id, p.name, p.stock_quantity, p.low_stock_threshold
        ORDER BY days_remaining ASC
    """
    fetch_report(query, "Predictive Restocking Analysis", "predictive_restock")


def seasonal_trends():
    """Analyze seasonal sales trends"""
    query = """
        SELECT EXTRACT(MONTH FROM s.sale_time) as month,
               EXTRACT(YEAR FROM s.sale_time) as year,
               COUNT(s.sale_id) as transaction_count,
               SUM(s.total_amount) as total_revenue,
               ROUND(AVG(s.total_amount), 2) as avg_sale
        FROM sales s
        GROUP BY EXTRACT(YEAR FROM s.sale_time), EXTRACT(MONTH FROM s.sale_time)
        ORDER BY year, month
    """
    fetch_report(query, "Seasonal Sales Trends", "seasonal_trends")


def customer_lifetime_value():
    """Calculate customer lifetime value"""
    query = """
        SELECT c.customer_id, c.name, c.phone,
               COUNT(s.sale_id) as total_visits,
               SUM(s.total_amount) as lifetime_value,
               ROUND(SUM(s.total_amount) / COUNT(s.sale_id), 2) as avg_visit_value,
               MAX(s.sale_time) as last_visit
        FROM customers c
        JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id, c.name, c.phone
        ORDER BY lifetime_value DESC
    """
    fetch_report(query, "Customer Lifetime Value Analysis", "clv_analysis")


def create_notification(product_id, message, notification_type="low_stock"):
    """Create system notifications programmatically"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO notifications (product_id, message, notification_type)
                VALUES (:pid, :msg, :type)
            """), {"pid": product_id, "msg": message, "type": notification_type})
    except Exception as e:
        print(f"❌ Error creating notification: {e}")


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
    from report import fetch_report
    fetch_report(query, "Employee Performance (Last 30 Days)", "employee_performance")