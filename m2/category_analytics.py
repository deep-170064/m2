# category_analytics.py
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission
from report import fetch_report

engine = get_engine()

def category_performance_dashboard():
    """Comprehensive category performance analytics"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # Category Performance Metrics
            performance_data = conn.execute(text("""
                SELECT 
                    c.category_id,
                    c.name as category_name,
                    c.description,
                    COUNT(p.product_id) as total_products,
                    SUM(p.stock_quantity) as total_stock,
                    COALESCE(SUM(si.quantity * si.unit_price), 0) as total_revenue,
                    COALESCE(COUNT(DISTINCT s.sale_id), 0) as total_transactions,
                    COALESCE(SUM(si.quantity), 0) as total_units_sold,
                    CASE 
                        WHEN COALESCE(SUM(si.quantity), 0) = 0 THEN 0
                        ELSE ROUND(COALESCE(SUM(si.quantity * si.unit_price), 0) / SUM(si.quantity), 2)
                    END as avg_unit_price,
                    CASE 
                        WHEN COUNT(p.product_id) = 0 THEN 0
                        ELSE ROUND(COALESCE(SUM(si.quantity * si.unit_price), 0) / COUNT(p.product_id), 2)
                    END as revenue_per_product
                FROM categories c
                LEFT JOIN products p ON c.category_id = p.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                GROUP BY c.category_id, c.name, c.description
                ORDER BY total_revenue DESC
            """)).fetchall()
            
            # Stock Health Analysis
            stock_health = conn.execute(text("""
                SELECT 
                    c.name as category_name,
                    COUNT(p.product_id) as total_products,
                    SUM(CASE WHEN p.stock_quantity = 0 THEN 1 ELSE 0 END) as out_of_stock,
                    SUM(CASE WHEN p.stock_quantity < p.low_stock_threshold THEN 1 ELSE 0 END) as low_stock,
                    SUM(CASE WHEN p.stock_quantity > p.low_stock_threshold * 3 THEN 1 ELSE 0 END) as over_stock,
                    ROUND(AVG(p.stock_quantity::decimal / NULLIF(p.low_stock_threshold, 0)), 2) as avg_stock_health
                FROM categories c
                JOIN products p ON c.category_id = p.category_id
                GROUP BY c.category_id, c.name
                ORDER BY avg_stock_health
            """)).fetchall()
            
            # Monthly Trend Analysis
            monthly_trends = conn.execute(text("""
                SELECT 
                    c.name as category_name,
                    TO_CHAR(s.sale_time, 'YYYY-MM') as month,
                    SUM(si.quantity * si.unit_price) as monthly_revenue,
                    SUM(si.quantity) as monthly_units
                FROM categories c
                JOIN products p ON c.category_id = p.category_id
                JOIN sale_items si ON p.product_id = si.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_time >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY c.category_id, c.name, TO_CHAR(s.sale_time, 'YYYY-MM')
                ORDER BY c.name, month DESC
            """)).fetchall()
            
        print("\n" + "="*80)
        print("📊 CATEGORY PERFORMANCE DASHBOARD")
        print("="*80)
        
        # Display Performance Summary
        print("\n🎯 PERFORMANCE SUMMARY (All Time)")
        print("-" * 80)
        
        performance_table = []
        for cat in performance_data:
            # Convert decimals to floats for display
            total_revenue = float(cat[5])
            avg_price = float(cat[8]) if cat[8] else 0.0
            rev_per_product = float(cat[9]) if cat[9] else 0.0
            
            performance_table.append({
                'Category ID': cat[0],
                'Category Name': cat[1],
                'Products': cat[3],
                'Total Stock': cat[4],
                'Revenue': f"₹{total_revenue:,.2f}",
                'Transactions': cat[6],
                'Units Sold': cat[7],
                'Avg Price': f"₹{avg_price:.2f}",
                'Rev/Product': f"₹{rev_per_product:.2f}"
            })
        
        print(tabulate(performance_table, headers="keys", tablefmt="grid"))
        
        # Display Stock Health
        print("\n⚡ STOCK HEALTH ANALYSIS")
        print("-" * 80)
        
        health_table = []
        for health in stock_health:
            health_icon = "✅" if health[5] >= 1.0 else "⚠️" if health[5] >= 0.5 else "❌"
            health_table.append({
                'Category': health[0],
                'Total Products': health[1],
                'Out of Stock': health[2],
                'Low Stock': health[3],
                'Over Stock': health[4],
                'Stock Health': f"{health_icon} {health[5]}"
            })
        
        print(tabulate(health_table, headers="keys", tablefmt="grid"))
        
        # Display Trends
        print("\n📈 RECENT TRENDS (Last 6 Months)")
        print("-" * 80)
        
        trends_table = []
        current_category = ""
        for trend in monthly_trends[:12]:  # Show top 12 records
            if trend[0] != current_category:
                current_category = trend[0]
                trends_table.append({
                    'Category': current_category, 
                    'Month': trend[1], 
                    'Revenue': f"₹{float(trend[2]):,.2f}", 
                    'Units': trend[3]
                })
            else:
                trends_table.append({
                    'Category': '', 
                    'Month': trend[1], 
                    'Revenue': f"₹{float(trend[2]):,.2f}", 
                    'Units': trend[3]
                })
        
        print(tabulate(trends_table, headers="keys", tablefmt="simple"))
        
        # Key Insights
        print("\n💡 KEY INSIGHTS")
        print("-" * 40)
        
        total_revenue = sum(float(cat[5]) for cat in performance_data)
        for cat in performance_data[:3]:  # Top 3 categories
            if float(cat[5]) > 0:
                percentage = (float(cat[5]) / total_revenue) * 100
                print(f"• {cat[1]}: {percentage:.1f}% of total revenue (₹{float(cat[5]):,.2f})")
        
        # Identify categories needing attention
        low_performers = [cat for cat in performance_data if float(cat[5]) == 0]
        if low_performers:
            print(f"\n⚠️  Categories with no sales: {', '.join([cat[1] for cat in low_performers])}")
            
    except Exception as e:
        print(f"❌ Error loading category dashboard: {e}")
        import traceback
        print(f"🔍 Detailed error: {traceback.format_exc()}")

def set_category_thresholds():
    """Set bulk low-stock thresholds by category"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            categories = conn.execute(text("""
                SELECT category_id, name, description 
                FROM categories 
                ORDER BY name
            """)).fetchall()
            
            print("\n📋 AVAILABLE CATEGORIES")
            print("-" * 50)
            for cat in categories:
                print(f"{cat[0]}. {cat[1]} - {cat[2]}")
            
            category_id = input("\nEnter Category ID to update: ").strip()
            new_threshold = input("Enter new default low-stock threshold: ").strip()
            
            if not category_id or not new_threshold:
                print("❌ Category ID and threshold are required")
                return
                
            # Update all products in this category
            result = conn.execute(text("""
                UPDATE products 
                SET low_stock_threshold = :threshold
                WHERE category_id = :cat_id
                RETURNING COUNT(*)
            """), {"threshold": int(new_threshold), "cat_id": int(category_id)})
            
            updated_count = result.fetchone()[0]
            category_name = next((cat[1] for cat in categories if cat[0] == int(category_id)), "Unknown")
            
            print(f"✅ Updated {updated_count} products in '{category_name}' to threshold: {new_threshold}")
            
    except Exception as e:
        print(f"❌ Error updating category thresholds: {e}")

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