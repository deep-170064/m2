# inventory_optimization.py - FIXED VERSION
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission
from datetime import datetime, timedelta
import decimal

engine = get_engine()

def safe_decimal_multiply(a, b):
    """Safely multiply decimal values handling None cases"""
    if a is None or b is None:
        return decimal.Decimal('0')
    return decimal.Decimal(str(a)) * decimal.Decimal(str(b))

def safe_float_convert(value):
    """Safely convert any value to float for calculations"""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def dead_stock_identification():
    """Identify slow-moving and dead stock items"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # Dead Stock Analysis (no sales in 90 days but have stock)
            dead_stock = conn.execute(text("""
                SELECT 
                    p.product_id,
                    p.name as product_name,
                    c.name as category,
                    p.stock_quantity,
                    p.low_stock_threshold,
                    p.price,
                    MAX(s.sale_time) as last_sale_date,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    CASE 
                        WHEN MAX(s.sale_time) IS NULL THEN 'Never Sold'
                        WHEN MAX(s.sale_time) < CURRENT_DATE - INTERVAL '90 days' THEN '90+ Days'
                        WHEN MAX(s.sale_time) < CURRENT_DATE - INTERVAL '60 days' THEN '60+ Days'
                        ELSE 'Active'
                    END as sales_status,
                    (p.stock_quantity * p.price) as inventory_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                WHERE p.stock_quantity > 0
                GROUP BY p.product_id, p.name, c.name, p.stock_quantity, p.low_stock_threshold, p.price
                HAVING MAX(s.sale_time) IS NULL OR MAX(s.sale_time) < CURRENT_DATE - INTERVAL '60 days'
                ORDER BY last_sale_date NULLS FIRST, total_sold ASC
            """)).fetchall()
            
            # Slow Moving Analysis (low sales velocity)
            slow_moving = conn.execute(text("""
                SELECT 
                    p.product_id,
                    p.name as product_name,
                    c.name as category,
                    p.stock_quantity,
                    p.price,
                    COALESCE(SUM(si.quantity), 0) as units_sold_90d,
                    COALESCE(SUM(si.quantity * si.unit_price), 0) as revenue_90d,
                    CASE 
                        WHEN p.stock_quantity = 0 THEN 0
                        WHEN COALESCE(SUM(si.quantity), 0) = 0 THEN 999
                        ELSE ROUND(p.stock_quantity / NULLIF(SUM(si.quantity), 0) * 90, 1)
                    END as days_of_supply,
                    (p.stock_quantity * p.price) as inventory_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_time >= CURRENT_DATE - INTERVAL '90 days' OR s.sale_time IS NULL
                GROUP BY p.product_id, p.name, c.name, p.stock_quantity, p.price
                HAVING COALESCE(SUM(si.quantity), 0) > 0  -- Has some sales
                ORDER BY days_of_supply DESC NULLS LAST
                LIMIT 20
            """)).fetchall()
            
            # Inventory Age Analysis
            inventory_age = conn.execute(text("""
                SELECT 
                    p.product_id,
                    p.name as product_name,
                    c.name as category,
                    p.stock_quantity,
                    p.price,
                    MAX(s.sale_time) as last_sale_date,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    CASE 
                        WHEN MAX(s.sale_time) IS NULL THEN 999
                        ELSE EXTRACT(DAY FROM CURRENT_DATE - MAX(s.sale_time))
                    END as days_since_last_sale,
                    (p.stock_quantity * p.price) as inventory_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                WHERE p.stock_quantity > 0
                GROUP BY p.product_id, p.name, c.name, p.stock_quantity, p.price
                ORDER BY days_since_last_sale DESC, inventory_value DESC
            """)).fetchall()
            
        print("\n" + "="*100)
        print("📦 DEAD STOCK IDENTIFICATION & INVENTORY OPTIMIZATION")
        print("="*100)
        
        # Display Dead Stock
        print("\n💀 DEAD STOCK ALERT (No sales in 60+ days)")
        print("-" * 100)
        
        if dead_stock:
            dead_stock_table = []
            total_dead_value = decimal.Decimal('0')
            
            for product in dead_stock:
                status_icon = "🔴" if product[8] == 'Never Sold' else "🟡" if product[8] == '90+ Days' else "🟠"
                last_sale = "Never" if not product[6] else product[6].strftime('%Y-%m-%d')
                
                # Safe decimal handling for inventory value
                inventory_value = product[9] or decimal.Decimal('0')
                total_dead_value += inventory_value
                
                dead_stock_table.append({
                    'Product ID': product[0],
                    'Product Name': product[1],
                    'Category': product[2],
                    'Stock Qty': product[3],
                    'Price': f"₹{safe_float_convert(product[5]):.2f}",
                    'Last Sale': last_sale,
                    'Total Sold': product[7],
                    'Status': f"{status_icon} {product[8]}",
                    'Inventory Value': f"₹{safe_float_convert(inventory_value):,.2f}"
                })
            
            print(tabulate(dead_stock_table, headers="keys", tablefmt="grid"))
            print(f"\n💰 **TOTAL DEAD STOCK VALUE: ₹{safe_float_convert(total_dead_value):,.2f}**")
        else:
            print("✅ No dead stock identified! Great inventory management!")
        
        # Display Slow Moving Inventory
        print("\n🐢 SLOW MOVING INVENTORY (High Days of Supply)")
        print("-" * 100)
        
        if slow_moving:
            slow_moving_table = []
            for product in slow_moving:
                days_supply = product[7] or 0
                if days_supply > 365:
                    risk_level = "🔴 Critical"
                elif days_supply > 180:
                    risk_level = "🟡 High" 
                elif days_supply > 90:
                    risk_level = "🟠 Medium"
                else:
                    risk_level = "🔵 Low"
                
                slow_moving_table.append({
                    'Product ID': product[0],
                    'Product Name': product[1],
                    'Category': product[2],
                    'Stock Qty': product[3],
                    'Units Sold (90d)': product[5],
                    'Revenue (90d)': f"₹{safe_float_convert(product[6]):.2f}",
                    'Days Supply': f"{days_supply}",
                    'Risk Level': risk_level,
                    'Inventory Value': f"₹{safe_float_convert(product[8]):,.2f}"
                })
            
            print(tabulate(slow_moving_table, headers="keys", tablefmt="grid"))
        
        # Display Inventory Age Analysis
        print("\n📅 INVENTORY AGE ANALYSIS")
        print("-" * 80)
        
        aged_table = []
        for product in inventory_age[:15]:  # Show top 15 oldest
            days_old = product[7]
            if days_old == 999:
                age_status = "🆕 Never Sold"
            elif days_old > 180:
                age_status = "🔴 Very Old"
            elif days_old > 90:
                age_status = "🟡 Old"
            elif days_old > 30:
                age_status = "🟠 Aging"
            else:
                age_status = "✅ Fresh"
            
            aged_table.append({
                'Product ID': product[0],
                'Product Name': product[1][:30] + '...' if len(product[1]) > 30 else product[1],
                'Category': product[2],
                'Stock': product[3],
                'Days Since Sale': days_old if days_old != 999 else 'Never',
                'Status': age_status,
                'Total Sold': product[6]
            })
        
        print(tabulate(aged_table, headers="keys", tablefmt="simple"))
        
        # Generate Action Recommendations
        print("\n🎯 RECOMMENDED ACTIONS")
        print("-" * 50)
        
        if dead_stock:
            dead_count = len(dead_stock)
            print(f"1. **Immediate Clearance**: {dead_count} dead stock items need promotion/discount")
            print(f"   • Total value: ₹{safe_float_convert(total_dead_value):,.2f}")
            print(f"   • Consider 20-50% discounts to clear inventory")
        
        if slow_moving:
            critical_slow = [p for p in slow_moving if (p[7] or 0) > 180]
            if critical_slow:
                print(f"2. **Restocking Review**: {len(critical_slow)} items with 180+ days supply")
                print("   • Reduce future order quantities")
                print("   • Consider supplier returns if possible")
        
        # Identify never-sold items
        never_sold = [p for p in dead_stock if p[8] == 'Never Sold']
        if never_sold:
            print(f"3. **Product Evaluation**: {len(never_sold)} items never sold")
            print("   • Review product viability")
            print("   • Consider discontinuation")
            
    except Exception as e:
        print(f"❌ Error analyzing dead stock: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")

def generate_clearance_recommendations():
    """Generate specific clearance pricing recommendations"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # Get candidates for clearance
            clearance_candidates = conn.execute(text("""
                SELECT 
                    p.product_id,
                    p.name,
                    c.name as category,
                    p.stock_quantity,
                    p.price as current_price,
                    MAX(s.sale_time) as last_sale,
                    COALESCE(SUM(si.quantity), 0) as total_sold,
                    CASE 
                        WHEN MAX(s.sale_time) IS NULL THEN 999
                        ELSE EXTRACT(DAY FROM CURRENT_DATE - MAX(s.sale_time))
                    END as days_unsold
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                WHERE p.stock_quantity > 0
                GROUP BY p.product_id, p.name, c.name, p.stock_quantity, p.price
                HAVING MAX(s.sale_time) IS NULL OR MAX(s.sale_time) < CURRENT_DATE - INTERVAL '60 days'
                ORDER BY days_unsold DESC, p.stock_quantity DESC
            """)).fetchall()
            
        print("\n🎪 CLEARANCE PRICING RECOMMENDATIONS")
        print("=" * 80)
        
        if clearance_candidates:
            recommendations = []
            total_potential = decimal.Decimal('0')
            
            for product in clearance_candidates:
                days_unsold = product[7]
                current_price = product[4] or decimal.Decimal('0')
                stock_quantity = product[3] or 0
                
                # Calculate recommended discount
                if days_unsold >= 180:
                    discount = decimal.Decimal('0.5')  # 50% off
                elif days_unsold >= 120:
                    discount = decimal.Decimal('0.4')  # 40% off
                elif days_unsold >= 90:
                    discount = decimal.Decimal('0.3')  # 30% off
                else:
                    discount = decimal.Decimal('0.2')  # 20% off
                
                # Safe decimal calculations
                new_price = current_price * (decimal.Decimal('1') - discount)
                potential_revenue = new_price * decimal.Decimal(str(stock_quantity))
                total_potential += potential_revenue
                
                recommendations.append({
                    'Product ID': product[0],
                    'Product Name': product[1][:25] + '...' if len(product[1]) > 25 else product[1],
                    'Category': product[2],
                    'Current Stock': stock_quantity,
                    'Current Price': f"₹{safe_float_convert(current_price):.2f}",
                    'Days Unsold': days_unsold if days_unsold != 999 else 'Never',
                    'Recommended Price': f"₹{safe_float_convert(new_price):.2f}",
                    'Discount': f"{safe_float_convert(discount)*100:.0f}%",
                    'Potential Revenue': f"₹{safe_float_convert(potential_revenue):,.2f}"
                })
            
            print(tabulate(recommendations, headers="keys", tablefmt="grid"))
            
            print(f"\n💰 **TOTAL POTENTIAL CLEARANCE REVENUE: ₹{safe_float_convert(total_potential):,.2f}**")
            
            # Action steps
            print("\n📋 **NEXT STEPS:**")
            print("1. Implement recommended pricing in system")
            print("2. Create 'Clearance Section' promotional display")
            print("3. Train staff on clearance items")
            print("4. Monitor sales velocity weekly")
            
        else:
            print("✅ No clearance candidates identified! Inventory is well-managed.")
            
    except Exception as e:
        print(f"❌ Error generating clearance recommendations: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")

def inventory_health_dashboard():
    """Comprehensive inventory health overview"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            # Overall Inventory Metrics
            overall_metrics = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_units,
                    SUM(stock_quantity * price) as total_inventory_value,
                    AVG(stock_quantity) as avg_stock_per_product,
                    COUNT(CASE WHEN stock_quantity = 0 THEN 1 END) as out_of_stock_count,
                    COUNT(CASE WHEN stock_quantity < low_stock_threshold THEN 1 END) as low_stock_count,
                    COUNT(CASE WHEN stock_quantity > low_stock_threshold * 3 THEN 1 END) as over_stock_count
                FROM products
            """)).fetchone()
            
            # Category-wise inventory distribution
            category_inventory = conn.execute(text("""
                SELECT 
                    c.name as category,
                    COUNT(p.product_id) as product_count,
                    SUM(p.stock_quantity) as total_stock,
                    SUM(p.stock_quantity * p.price) as category_value,
                    ROUND(SUM(p.stock_quantity * p.price) * 100.0 / NULLIF((
                        SELECT SUM(stock_quantity * price) FROM products
                    ), 0), 2) as value_percentage
                FROM categories c
                LEFT JOIN products p ON c.category_id = p.category_id
                GROUP BY c.category_id, c.name
                ORDER BY category_value DESC
            """)).fetchall()
            
            # Stock Turnover Analysis
            turnover_analysis = conn.execute(text("""
                SELECT 
                    p.product_id,
                    p.name as product_name,
                    c.name as category,
                    p.stock_quantity,
                    COALESCE(SUM(si.quantity), 0) as units_sold_30d,
                    CASE 
                        WHEN p.stock_quantity = 0 THEN 0
                        WHEN COALESCE(SUM(si.quantity), 0) = 0 THEN 999
                        ELSE ROUND(p.stock_quantity / NULLIF(SUM(si.quantity), 0) * 30, 1)
                    END as days_of_supply,
                    CASE 
                        WHEN COALESCE(SUM(si.quantity), 0) = 0 THEN 'No Sales'
                        WHEN (p.stock_quantity / NULLIF(SUM(si.quantity), 0) * 30) > 90 THEN 'Slow'
                        WHEN (p.stock_quantity / NULLIF(SUM(si.quantity), 0) * 30) > 30 THEN 'Moderate'
                        ELSE 'Fast'
                    END as turnover_rate
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_time >= CURRENT_DATE - INTERVAL '30 days' OR s.sale_time IS NULL
                GROUP BY p.product_id, p.name, c.name, p.stock_quantity
                ORDER BY days_of_supply DESC
                LIMIT 15
            """)).fetchall()
            
        print("\n" + "="*100)
        print("🏥 INVENTORY HEALTH DASHBOARD")
        print("="*100)
        
        # Display Overall Metrics
        print("\n📊 OVERALL INVENTORY METRICS")
        print("-" * 80)
        
        metrics_table = [{
            'Total Products': overall_metrics[0],
            'Total Units': overall_metrics[1],
            'Total Value': f"₹{safe_float_convert(overall_metrics[2]):,.2f}",
            'Avg Stock/Product': f"{safe_float_convert(overall_metrics[3]):.1f}",
            'Out of Stock': f"🔴 {overall_metrics[4]}",
            'Low Stock': f"🟡 {overall_metrics[5]}",
            'Over Stock': f"🟠 {overall_metrics[6]}"
        }]
        
        print(tabulate(metrics_table, headers="keys", tablefmt="grid"))
        
        # Display Category Distribution
        print("\n📈 CATEGORY INVENTORY DISTRIBUTION")
        print("-" * 80)
        
        category_table = []
        for category in category_inventory:
            # FIXED: Safe percentage calculation
            percentage = safe_float_convert(category[4])
            
            category_table.append({
                'Category': category[0],
                'Products': category[1],
                'Total Stock': category[2],
                'Value': f"₹{safe_float_convert(category[3]):,.2f}",
                'Percentage': f"{percentage:.1f}%" if percentage is not None else "0.0%"
            })
        
        print(tabulate(category_table, headers="keys", tablefmt="grid"))
        
        # Display Turnover Analysis
        print("\n🔄 STOCK TURNOVER ANALYSIS (Last 30 Days)")
        print("-" * 100)
        
        turnover_table = []
        for product in turnover_analysis:
            days_supply = product[5] or 0
            if days_supply == 999:
                turnover_icon = "💤"
                turnover_status = "No Sales"
            elif days_supply > 90:
                turnover_icon = "🐢"
                turnover_status = "Slow"
            elif days_supply > 30:
                turnover_icon = "🚶"
                turnover_status = "Moderate"
            else:
                turnover_icon = "⚡"
                turnover_status = "Fast"
            
            turnover_table.append({
                'Product ID': product[0],
                'Product Name': product[1][:20] + '...' if len(product[1]) > 20 else product[1],
                'Category': product[2],
                'Stock': product[3],
                'Sold (30d)': product[4],
                'Days Supply': f"{days_supply}",
                'Turnover': f"{turnover_icon} {turnover_status}"
            })
        
        print(tabulate(turnover_table, headers="keys", tablefmt="grid"))
        
        # Health Assessment
        print("\n💡 INVENTORY HEALTH ASSESSMENT")
        print("-" * 50)
        
        total_products = overall_metrics[0] or 1  # Avoid division by zero
        out_of_stock_percentage = (safe_float_convert(overall_metrics[4]) / total_products) * 100
        low_stock_percentage = (safe_float_convert(overall_metrics[5]) / total_products) * 100
        over_stock_percentage = (safe_float_convert(overall_metrics[6]) / total_products) * 100
        
        if out_of_stock_percentage > 10:
            print("🔴 **CRITICAL**: High out-of-stock items (>10%) - Urgent restocking needed!")
        elif low_stock_percentage > 20:
            print("🟡 **WARNING**: Many low-stock items (>20%) - Plan restocking")
        else:
            print("✅ **HEALTHY**: Inventory levels are well maintained")
            
        print(f"   • Out of Stock: {out_of_stock_percentage:.1f}% of products")
        print(f"   • Low Stock: {low_stock_percentage:.1f}% of products")
        print(f"   • Over Stock: {over_stock_percentage:.1f}% of products")
        
    except Exception as e:
        print(f"❌ Error loading inventory health dashboard: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")

def apply_clearance_pricing():
    """Apply clearance pricing to selected products"""
    if not has_permission(["ADMIN"]):
        return
        
    try:
        # First show clearance recommendations
        generate_clearance_recommendations()
        
        product_id = input("\nEnter Product ID to apply clearance pricing (or 'cancel'): ").strip()
        if product_id.lower() == 'cancel':
            return
            
        new_price = input("Enter new clearance price: ").strip()
        
        if not product_id or not new_price:
            print("❌ Product ID and price are required")
            return
            
        with engine.begin() as conn:
            # Get current product info
            product_info = conn.execute(text("""
                SELECT name, price FROM products WHERE product_id = :pid
            """), {"pid": int(product_id)}).fetchone()
            
            if not product_info:
                print("❌ Product not found")
                return
                
            # Update price
            conn.execute(text("""
                UPDATE products SET price = :new_price WHERE product_id = :pid
            """), {"new_price": decimal.Decimal(new_price), "pid": int(product_id)})
            
            old_price = product_info[1]
            discount = ((old_price - decimal.Decimal(new_price)) / old_price) * 100
            
            print(f"✅ Price updated for '{product_info[0]}'")
            print(f"   Old Price: ₹{safe_float_convert(old_price):.2f}")
            print(f"   New Price: ₹{safe_float_convert(new_price):.2f}")
            print(f"   Discount: {safe_float_convert(discount):.1f}%")
            
    except Exception as e:
        print(f"❌ Error applying clearance pricing: {e}")

# Export functions for use in other modules
__all__ = [
    'dead_stock_identification',
    'generate_clearance_recommendations', 
    'inventory_health_dashboard',
    'apply_clearance_pricing'
]

if __name__ == "__main__":
    # Test the module
    print("🧪 Testing Inventory Optimization Module...")
    dead_stock_identification()
    print("\n" + "="*100)
    generate_clearance_recommendations()
    print("\n" + "="*100)
    inventory_health_dashboard()