# system_admin.py
from sqlalchemy import text
from db import get_engine
from auth import has_permission
import datetime

engine = get_engine()

def system_backup():
    """Create database backup"""
    if not has_permission(["ADMIN"]):
        return
        
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_supermarket_{timestamp}.sql"
        
        # This would use pg_dump in production
        print(f"🔧 Backup functionality would create: {backup_file}")
        print("💡 In production, implement pg_dump command here")
        
        # For now, export critical tables
        tables = ['products', 'sales', 'customers', 'employees']
        print(f"📦 Would backup tables: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Backup error: {e}")

def system_health_check():
    """Check system health and statistics"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # System statistics
            stats = conn.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM products) as total_products,
                    (SELECT COUNT(*) FROM sales WHERE DATE(sale_time) = CURRENT_DATE) as today_sales,
                    (SELECT COUNT(*) FROM employees) as total_employees,
                    (SELECT COUNT(*) FROM customers) as total_customers,
                    (SELECT COUNT(*) FROM notifications WHERE status = 'unread') as unread_alerts,
                    (SELECT SUM(stock_quantity) FROM products) as total_inventory
            """)).fetchone()
            
            print("\n🏥 SYSTEM HEALTH CHECK")
            print("=" * 40)
            print(f"📦 Total Products: {stats[0]}")
            print(f"💰 Today's Sales: {stats[1]}")
            print(f"👥 Total Employees: {stats[2]}")
            print(f"🤝 Total Customers: {stats[3]}")
            print(f"🔔 Unread Alerts: {stats[4]}")
            print(f"📊 Total Inventory Value: {stats[5]} units")
            print("=" * 40)
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

def purge_old_data():
    """Archive or purge old data"""
    if not has_permission(["ADMIN"]):
        return
        
    try:
        print("🗑️  DATA PURGE MANAGEMENT")
        print("WARNING: This will permanently delete old data!")
        
        confirm = input("Type 'DELETE' to confirm: ").strip()
        if confirm != 'DELETE':
            print("❌ Cancelled")
            return
            
        days = int(input("Delete sales older than (days): ").strip())
        
        with engine.begin() as conn:
            # Count records to be deleted
            count = conn.execute(text("""
                SELECT COUNT(*) FROM sales 
                WHERE sale_time < CURRENT_DATE - INTERVAL ':days days'
            """), {"days": days}).fetchone()[0]
            
            if count == 0:
                print("✅ No old data found")
                return
                
            print(f"⚠️  Will delete {count} sales records")
            final_confirm = input("Type 'CONFIRM' to proceed: ").strip()
            
            if final_confirm == 'CONFIRM':
                conn.execute(text("""
                    DELETE FROM sales 
                    WHERE sale_time < CURRENT_DATE - INTERVAL ':days days'
                """), {"days": days})
                print(f"✅ Deleted {count} old sales records")
            else:
                print("❌ Cancelled")
                
    except Exception as e:
        print(f"❌ Purge error: {e}")