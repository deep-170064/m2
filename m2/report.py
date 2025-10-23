# report.py
import pandas as pd
from sqlalchemy import create_engine, text
from tabulate import tabulate
from db import get_connection_string 
import datetime

# ------------------ Setup Engine ------------------
engine = create_engine(get_connection_string(), echo=False, future=True)

# ------------------ Helper Function ------------------
def fetch_report(query, report_name, file_name, params=None):
    """
    Fetches data from DB, pretty-prints it, and optionally exports to CSV/Excel/JSON.
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)

        if df.empty:
            print(f"\n⚠️ No data found for {report_name}!\n")
            return

        # Pretty print table
        print(f"\n📊 {report_name}\n")
        print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

        # Ask before exporting
        choice = input("\n💾 Do you want to export this report? (y/n): ").strip().lower()
        if choice == "y":
            answer = input("Choose export format [csv/txt/json]: ").strip().lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"report_{answer}_{timestamp}"
            if answer=="csv":
                df.to_csv(f"{file_name}.csv", index=False)
                print(f"\n✅ Exported to {file_name}.csv\n")
            elif answer == "txt":
                with open(f"{file_name}.txt", "w", encoding="utf-8") as f:
                    f.write(df.to_markdown(index=False))
                print(f"\n✅ Exported to {file_name}.txt \n")
            elif answer=="json":
                df.to_json(f"{file_name}.json", orient="records", indent=2)
                print(f"\n✅ Exported to {file_name}.json\n")
            else:
                print("❌ Unsupported export type! Please choose csv, txt or json.")
        else:
            print("⚡ Skipped exporting.\n")

    except Exception as e:
        print("❌ Error while fetching report:", e)

# ------------------ Report Functions ------------------
def daily_sales_report(start_date=None, end_date=None):
    query = "SELECT * FROM daily_sales_report"
    params = None
    if start_date and end_date:
        query += " WHERE date BETWEEN :start AND :end"
        params = {"start": start_date, "end": end_date}
    fetch_report(query, "Daily Sales Report", "daily_sales_report", params)

def best_selling_products(top_n=10):
    query = "SELECT * FROM best_selling_products LIMIT :limit"
    fetch_report(query, f"Top {top_n} Best Selling Products", "best_selling_products", {"limit": top_n})

def low_stock_report(threshold=10):
    query = """
        SELECT * FROM low_stock_products
        WHERE stock_quantity < :threshold
        ORDER BY stock_quantity ASC
    """
    fetch_report(query, f"Low Stock (<{threshold}) Report", "low_stock_report", {"threshold": threshold})

# ------------------ Enhanced Report Mode ------------------
def enhanced_report_mode():
    """Extended reporting with new analytics"""
    from analytics import (category_sales_report, supplier_performance, 
                         peak_hours_analysis, customer_analytics, employee_performance,
                         predictive_restocking, seasonal_trends, customer_lifetime_value)
    
    while True:
        print("\n=== 📊 ENHANCED REPORT MODE ===")
        print("1. Daily Sales Report")
        print("2. Best Selling Products") 
        print("3. Low Stock Report")
        print("4. Category Sales Report")
        print("5. Employee Performance")
        print("6. Customer Analytics")
        print("7. Peak Hours Analysis")
        print("8. Supplier Performance")
        print("9. Predictive Restocking")
        print("10. Seasonal Trends")
        print("11. Customer Lifetime Value")
        print("12. Back to Main Menu")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            start = input("Start date (YYYY-MM-DD or leave blank): ").strip() or None
            end = input("End date (YYYY-MM-DD or leave blank): ").strip() or None
            daily_sales_report(start, end)
        elif choice == "2":
            try:
                n = int(input("How many top products? (default 10): ").strip() or 10)
            except ValueError:
                n = 10
            best_selling_products(n)
        elif choice == "3":
            try:
                threshold = int(input("Enter stock threshold (default 10): ").strip() or 10)
            except ValueError:
                threshold = 10
            low_stock_report(threshold)
        elif choice == "4":
            category_sales_report()
        elif choice == "5":
            employee_performance()
        elif choice == "6":
            customer_analytics()
        elif choice == "7":
            peak_hours_analysis()
        elif choice == "8":
            supplier_performance()
        elif choice == "9":
            predictive_restocking()
        elif choice == "10":
            seasonal_trends()
        elif choice == "11":
            customer_lifetime_value()
        elif choice == "12":
            print("👋 Exiting Enhanced Report Mode...")
            break
        else:
            print("❌ Invalid choice, try again!")

# ------------------ Run ------------------
if __name__ == "__main__":
    enhanced_report_mode()