# supplier_analytics.py - FIXED VERSION
from sqlalchemy import text
from tabulate import tabulate
from db import get_engine
from auth import has_permission
from datetime import datetime, timedelta
import decimal

engine = get_engine()

def safe_float_convert(value):
    """Safely convert any value to float for calculations"""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def supplier_scorecard_system():
    """Comprehensive supplier performance rating system"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        # Use separate connections for each query to avoid connection issues
        with engine.connect() as conn:
            # Supplier Performance Metrics
            supplier_data = conn.execute(text("""
                SELECT 
                    s.supplier_id,
                    s.name as supplier_name,
                    s.contact_info,
                    s.reliability_score,
                    COUNT(p.product_id) as products_supplied,
                    SUM(p.stock_quantity) as current_stock_value,
                    COALESCE(SUM(si.quantity * si.unit_price), 0) as total_revenue_generated,
                    COALESCE(COUNT(DISTINCT si.sale_item_id), 0) as total_items_sold,
                    MAX(s.last_delivery_date) as last_delivery,
                    CASE 
                        WHEN MAX(s.last_delivery_date) IS NULL THEN 'No Deliveries'
                        WHEN MAX(s.last_delivery_date) >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
                        WHEN MAX(s.last_delivery_date) >= CURRENT_DATE - INTERVAL '90 days' THEN 'Moderate'
                        ELSE 'Inactive'
                    END as activity_status
                FROM suppliers s
                LEFT JOIN products p ON s.supplier_id = p.supplier_id
                LEFT JOIN sale_items si ON p.product_id = si.product_id
                LEFT JOIN sales s2 ON si.sale_id = s2.sale_id
                GROUP BY s.supplier_id, s.name, s.contact_info, s.reliability_score
                ORDER BY total_revenue_generated DESC
            """)).fetchall()
        
        # Use a new connection for the second query
        with engine.connect() as conn2:
            # Delivery Performance 
            delivery_metrics = conn2.execute(text("""
                SELECT 
                    s.supplier_id,
                    s.name,
                    COUNT(p.product_id) as active_products,
                    AVG(p.stock_quantity) as avg_stock_level,
                    SUM(CASE WHEN p.stock_quantity = 0 THEN 1 ELSE 0 END) as out_of_stock_items,
                    ROUND(COUNT(p.product_id) * 100.0 / NULLIF((
                        SELECT COUNT(*) FROM products WHERE supplier_id = s.supplier_id
                    ), 0), 2) as product_coverage
                FROM suppliers s
                LEFT JOIN products p ON s.supplier_id = p.supplier_id
                GROUP BY s.supplier_id, s.name
            """)).fetchall()
            
        print("\n" + "="*100)
        print("🏆 SUPPLIER SCORECARD SYSTEM")
        print("="*100)
        
        # Display Supplier Scorecards
        print("\n📊 SUPPLIER PERFORMANCE RANKINGS")
        print("-" * 100)
        
        scorecard_table = []
        for supplier in supplier_data:
            # SAFE CALCULATIONS - Convert everything to float first
            reliability = safe_float_convert(supplier[3] or 80)  # Default if null
            revenue = safe_float_convert(supplier[6])
            revenue_score = min(100.0, (revenue / 10000.0) * 10.0) if revenue > 0 else 0.0
            
            activity_bonus = 20.0 if supplier[9] == 'Active' else 10.0 if supplier[9] == 'Moderate' else 0.0
            
            # FIXED: Use float arithmetic instead of decimal * float
            composite_score = min(100.0, reliability * 0.6 + revenue_score * 0.3 + activity_bonus)
            
            # Grade assignment
            if composite_score >= 90:
                grade = "A+ 🏅"
            elif composite_score >= 80:
                grade = "A 👍"
            elif composite_score >= 70:
                grade = "B ✅"
            elif composite_score >= 60:
                grade = "C ⚠️"
            else:
                grade = "D ❌"
            
            scorecard_table.append({
                'Supplier ID': supplier[0],
                'Supplier Name': supplier[1],
                'Products': supplier[4],
                'Total Revenue': f"₹{revenue:,.2f}",
                'Items Sold': supplier[7],
                'Reliability': f"{supplier[3] or 'N/A'}",
                'Last Delivery': supplier[8].strftime('%Y-%m-%d') if supplier[8] else 'Never',
                'Activity': supplier[9],
                'Composite Score': f"{composite_score:.1f}",
                'Grade': grade
            })
        
        print(tabulate(scorecard_table, headers="keys", tablefmt="grid"))
        
        # Display Delivery Metrics
        print("\n🚚 SUPPLIER DELIVERY & STOCK METRICS")
        print("-" * 80)
        
        delivery_table = []
        for delivery in delivery_metrics:
            stock_health = "✅ Good" if delivery[4] == 0 else "⚠️ Warning" if delivery[4] <= 2 else "❌ Critical"
            avg_stock = safe_float_convert(delivery[3])
            coverage = safe_float_convert(delivery[5])
            
            delivery_table.append({
                'Supplier': delivery[1],
                'Active Products': delivery[2],
                'Avg Stock': f"{avg_stock:.0f}",
                'Out of Stock': delivery[4],
                'Stock Health': stock_health,
                'Coverage': f"{coverage:.1f}%"
            })
        
        print(tabulate(delivery_table, headers="keys", tablefmt="grid"))
        
        # Supplier Recommendations
        print("\n💡 SUPPLIER MANAGEMENT RECOMMENDATIONS")
        print("-" * 50)
        
        # Identify top performers
        top_suppliers = [s for s in scorecard_table if 'A' in s['Grade']]
        if top_suppliers:
            print("🎯 **TOP PERFORMERS** (Consider expanding partnerships):")
            for supplier in top_suppliers[:3]:
                print(f"   • {supplier['Supplier Name']} - {supplier['Grade']} (Score: {supplier['Composite Score']})")
        
        # Identify underperformers
        low_suppliers = [s for s in scorecard_table if 'D' in s['Grade'] or 'C' in s['Grade']]
        if low_suppliers:
            print("\n⚠️  **NEEDS ATTENTION** (Consider review/replacement):")
            for supplier in low_suppliers:
                print(f"   • {supplier['Supplier Name']} - {supplier['Grade']} (Score: {supplier['Composite Score']})")
        
        # Inactive suppliers
        inactive_suppliers = [s for s in scorecard_table if s['Activity'] == 'Inactive']
        if inactive_suppliers:
            print(f"\n💤 **INACTIVE SUPPLIERS** ({len(inactive_suppliers)} found)")
            print("   Consider archiving or re-engaging these suppliers")
            
    except Exception as e:
        print(f"❌ Error loading supplier scorecards: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")

def update_supplier_reliability():
    """Manually update supplier reliability scores"""
    if not has_permission(["MANAGER", "ADMIN"]):
        return
        
    try:
        with engine.connect() as conn:
            suppliers = conn.execute(text("""
                SELECT supplier_id, name, reliability_score 
                FROM suppliers 
                ORDER BY name
            """)).fetchall()
            
            print("\n📋 SUPPLIER LIST")
            print("-" * 50)
            for supplier in suppliers:
                current_score = supplier[2] or "Not Set"
                print(f"{supplier[0]}. {supplier[1]} - Current Score: {current_score}")
            
            supplier_id = input("\nEnter Supplier ID to update: ").strip()
            new_score = input("Enter new reliability score (0-100): ").strip()
            
            if not supplier_id or not new_score:
                print("❌ Supplier ID and score are required")
                return
                
            score = int(new_score)
            if not (0 <= score <= 100):
                print("❌ Score must be between 0 and 100")
                return
                
            result = conn.execute(text("""
                UPDATE suppliers 
                SET reliability_score = :score
                WHERE supplier_id = :sup_id
                RETURNING name
            """), {"score": score, "sup_id": int(supplier_id)})
            
            updated_supplier = result.fetchone()
            if updated_supplier:
                print(f"✅ Updated reliability score for '{updated_supplier[0]}' to {score}")
            else:
                print("❌ Supplier not found")
                
    except Exception as e:
        print(f"❌ Error updating supplier score: {e}")