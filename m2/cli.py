# cli.py - MAIN ENTRY POINT
import datetime
from auth import login, logout, get_current_role, get_current_name

# Import all management modules
try:
    from product_management import add_product, view_products, set_stock_thresholds
    from sales_management import process_sale
    from employee_management import manage_employees
    from analytics import notification_center, alert_dashboard
    from report import enhanced_report_mode
    from inventory_management import restock_products, bulk_stock_update
    from customer_management import manage_customers
    from system_admin import system_health_check, system_backup, purge_old_data
    from inventory_optimization import apply_clearance_pricing,inventory_health_dashboard
    # New analytics modules
    from category_analytics import category_performance_dashboard, set_category_thresholds
    from supplier_analytics import supplier_scorecard_system, update_supplier_reliability
    from inventory_optimization import dead_stock_identification, generate_clearance_recommendations
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all module files are in the same directory.")
    exit(1)


# ----------------- Main Menu -----------------
def main_menu():
    """Display the role-based main menu. Requires login first."""
    if not login():
        return

    while True:
        current_role = get_current_role()
        current_name = get_current_name()
        
        print("\n" + "="*60)
        print("=== 🏪 SuperMarket Inventory & Billing System ===")
        print("="*60)
        print(f"👤 User: {current_name} | 🎯 Role: {current_role}")
        print(f"🕒 Logged in: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)
        
        if current_role == "CASHIER":
            print("1. 📋 View Products")
            print("2. 💰 Process Sale") 
            print("3. 🔔 My Notifications")
            print("4. 🚪 Logout / Exit")

            choice = input("Enter choice: ").strip()
            if choice == '1':
                view_products()
            elif choice == '2':
                process_sale()
            elif choice == '3':
                # Simple notification view for cashiers
                from analytics import notification_center
                notification_center()
            elif choice == '4':
                logout()
                break
            else:
                print("❌ Invalid choice, try again!")

        elif current_role == "MANAGER":
            print("1. 📋 View Products")
            print("2. 💰 Process Sale")
            print("3. 📊 View Reports")
            print("4. 🔔 Notification Center")
            print("5. 🚨 Alert Dashboard") 
            print("6. 📦 Restock Products")
            print("7. 📈 Category Performance")
            print("8. 🏆 Supplier Scorecards") 
            print("9. 📦 Dead Stock Analysis")
            print("10. 👥 Manage Customers")
            print("11. 🏥 System Health Check")
            print("12. 🚪 Logout / Exit")

            choice = input("Enter choice: ").strip()
            if choice == '1':
                view_products()
            elif choice == '2':
                process_sale()
            elif choice == '3':
                enhanced_report_mode()
            elif choice == '4':
                notification_center()
            elif choice == '5':
                alert_dashboard()
            elif choice == '6':
                restock_products()
            elif choice == '7':
                category_performance_dashboard()
            elif choice == '8':
                supplier_scorecard_system()
            elif choice == '9':
                dead_stock_identification()
            elif choice == '10':
                manage_customers()
            elif choice == '11':
                system_health_check()
            elif choice == '12':
                logout()
                break
            else:
                print("❌ Invalid choice, try again!")

        elif current_role == "ADMIN":
            print("1. 📦 Add Product")
            print("2. 📋 View Products")
            print("3. 💰 Process Sale")
            print("4. 📊 View Reports")
            print("5. 👥 Manage Employees")
            print("6. 🔔 Notification Center")
            print("7. 🚨 Alert Dashboard")
            print("8. ⚙️ Set Stock Thresholds")
            print("9. 📦 Restock Products")
            print("10. 🔄 Bulk Stock Update")
            print("11. 📈 Category Performance")
            print("12. 🏆 Supplier Scorecards")
            print("13. 📦 Dead Stock Analysis") 
            print("14. 🎪 Clearance Recommendations")
            print("15. ⚙️ Category Thresholds")
            print("16. 🔄 Supplier Reliability")
            print("17. 👥 Manage Customers")
            print("18. 🏥 System Health Check")
            print("19. 🔧 System Backup")
            print("20. 🗑️ Purge Old Data")
            print("21. 🚪 Logout / Exit")
            print("22. 🏥 Inventory Health Dashboard")
            print("23. 🎪 Apply Clearance Pricing")
            choice = input("Enter choice: ").strip()
            if choice == '1':
                add_product()
            elif choice == '2':
                view_products()
            elif choice == '3':
                process_sale()
            elif choice == '4':
                enhanced_report_mode()
            elif choice == '5':
                manage_employees()
            elif choice == '6':
                notification_center()
            elif choice == '7':
                alert_dashboard()
            elif choice == '8':
                set_stock_thresholds()
            elif choice == '9':
                restock_products()
            elif choice == '10':
                bulk_stock_update()
            elif choice == '11':
                category_performance_dashboard()
            elif choice == '12':
                supplier_scorecard_system()
            elif choice == '13':
                dead_stock_identification()
            elif choice == '14':
                generate_clearance_recommendations()
            elif choice == '15':
                set_category_thresholds()
            elif choice == '16':
                update_supplier_reliability()
            elif choice == '17':
                manage_customers()
            elif choice == '18':
                system_health_check()
            elif choice == '19':
                system_backup()
            elif choice == '20':
                purge_old_data()
            elif choice == '21':
                logout()
            elif choice == '22':
                inventory_health_dashboard()
            elif choice == '23':
                
                apply_clearance_pricing()  
                break
            else:
                print("❌ Invalid choice, try again!")

        else:
            print("🚫 Unknown role. Exiting.")
            break


# ----------------- Quick Start Helper -----------------
def quick_start_guide():
    """Display quick start guide for new users"""
    print("\n" + "="*60)
    print("🚀 QUICK START GUIDE")
    print("="*60)
    print("For Demo Purposes, use these credentials:")
    print("👤 ADMIN:     username='alicej'     password='admin123'")
    print("👤 MANAGER:   username='carold'     password='manager123'") 
    print("👤 CASHIER:   username='emma'       password='cashier123'")
    print("-"*60)
    print("💡 Recommended First Steps:")
    print("1. Login as ADMIN for full system access")
    print("2. View Products to see current inventory")
    print("3. Try Category Performance for analytics")
    print("4. Check Supplier Scorecards for vendor insights")
    print("="*60)


# ----------------- System Info -----------------
def system_info():
    """Display system information"""
    print("\n" + "="*60)
    print("🏪 SUPERMARKET MANAGEMENT SYSTEM v2.0")
    print("="*60)
    print("📊 MODULES INCLUDED:")
    print("  ✅ Inventory Management with Auto-stock tracking")
    print("  ✅ Point-of-Sale (POS) System") 
    print("  ✅ Customer Relationship Management (CRM)")
    print("  ✅ Employee Management with Role-based access")
    print("  ✅ Advanced Analytics & Reporting")
    print("  ✅ Automated Notifications & Alerts")
    print("  ✅ Supplier Performance Tracking")
    print("  ✅ Category Performance Analytics")
    print("  ✅ Dead Stock Identification")
    print("  ✅ System Administration Tools")
    print("="*60)


# ----------------- Main Execution -----------------
if __name__ == "__main__":
    try:
        # Display welcome information
        system_info()
        quick_start_guide()
        
        # Start main application
        main_menu()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application interrupted by user")
        logout()
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        print("Please check your database connection and try again.")
    finally:
        print("\n👋 Thank you for using SuperMarket Management System!")