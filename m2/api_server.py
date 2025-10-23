from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import text
from db_config import get_engine
import bcrypt
import datetime

app = FastAPI(title="SuperMarket Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = get_engine()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    employee_id: int
    name: str
    role: str
    message: str

class Product(BaseModel):
    name: str
    barcode: Optional[str] = None
    price: float
    stock_quantity: int
    category_id: int
    supplier_id: int
    low_stock_threshold: int = 10

class SaleItem(BaseModel):
    product_id: int
    quantity: int

class Sale(BaseModel):
    items: List[SaleItem]
    payment_method: str
    customer_id: Optional[int] = None
    employee_id: int

class Customer(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class Employee(BaseModel):
    name: str
    role: str
    username: str
    password: str

class StockUpdate(BaseModel):
    product_id: int
    quantity: int

@app.get("/")
async def root():
    return {"message": "SuperMarket Management API", "version": "1.0"}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    try:
        with engine.connect() as conn:
            res = conn.execute(text("""
                SELECT employee_id, name, role, password
                FROM employees
                WHERE username = :uname
            """), {"uname": credentials.username})
            row = res.fetchone()
        
        if not row:
            raise HTTPException(status_code=401, detail="Invalid username")
        
        emp_id, name, role, stored_password = row
        
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), stored_password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        return LoginResponse(
            employee_id=emp_id,
            name=name,
            role=role,
            message=f"Welcome {name}!"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def get_products():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT p.product_id, p.name, p.barcode, p.price, p.stock_quantity, 
                       p.low_stock_threshold, c.name as category, s.name as supplier
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
                ORDER BY p.product_id
            """))
            rows = result.fetchall()
        
        products = [
            {
                "product_id": r[0],
                "name": r[1],
                "barcode": r[2],
                "price": float(r[3]) if r[3] else 0,
                "stock_quantity": r[4],
                "low_stock_threshold": r[5],
                "category": r[6],
                "supplier": r[7]
            }
            for r in rows
        ]
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products")
async def add_product(product: Product):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO products (name, barcode, price, stock_quantity, category_id, supplier_id, low_stock_threshold)
                VALUES (:name, :barcode, :price, :stock, :category_id, :supplier_id, :threshold)
                RETURNING product_id
            """), {
                "name": product.name,
                "barcode": product.barcode,
                "price": product.price,
                "stock": product.stock_quantity,
                "category_id": product.category_id,
                "supplier_id": product.supplier_id,
                "threshold": product.low_stock_threshold
            })
            product_id = result.fetchone()[0]
        return {"message": "Product added successfully", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT category_id, name, description FROM categories ORDER BY name"))
            rows = result.fetchall()
        
        categories = [
            {"category_id": r[0], "name": r[1], "description": r[2]}
            for r in rows
        ]
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suppliers")
async def get_suppliers():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT supplier_id, name, phone, email, address FROM suppliers ORDER BY name"))
            rows = result.fetchall()
        
        suppliers = [
            {"supplier_id": r[0], "name": r[1], "phone": r[2], "email": r[3], "address": r[4]}
            for r in rows
        ]
        return {"suppliers": suppliers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales")
async def create_sale(sale: Sale):
    try:
        total = 0.0
        cart = []
        
        with engine.connect() as conn:
            for item in sale.items:
                result = conn.execute(text("""
                    SELECT name, price, stock_quantity
                    FROM products
                    WHERE product_id = :pid
                """), {"pid": item.product_id})
                product_data = result.fetchone()
                
                if not product_data:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                
                if product_data[2] < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Only {product_data[2]} units in stock for {product_data[0]}")
                
                item_total = float(product_data[1]) * item.quantity
                cart.append({
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': float(product_data[1]),
                    'subtotal': item_total
                })
                total += item_total
        
        with engine.begin() as conn:
            if sale.customer_id:
                res = conn.execute(text("SELECT 1 FROM customers WHERE customer_id = :cid"), {"cid": sale.customer_id})
                if res.fetchone() is None:
                    raise HTTPException(status_code=404, detail="Customer not found")
            
            result = conn.execute(text("""
                INSERT INTO sales (total_amount, payment_method, customer_id, employee_id)
                VALUES (:total, :pm, :cid, :eid)
                RETURNING sale_id
            """), {
                "total": round(total, 2),
                "pm": sale.payment_method,
                "cid": sale.customer_id,
                "eid": sale.employee_id
            })
            sale_id = result.fetchone()[0]
            
            for item in cart:
                conn.execute(text("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
                    VALUES (:sale_id, :pid, :qty, :price, :subtotal)
                """), {
                    "sale_id": sale_id,
                    "pid": item['product_id'],
                    "qty": item['quantity'],
                    "price": item['price'],
                    "subtotal": item['subtotal']
                })
                
                conn.execute(text("""
                    UPDATE products 
                    SET stock_quantity = stock_quantity - :qty
                    WHERE product_id = :pid
                """), {"qty": item['quantity'], "pid": item['product_id']})
        
        return {"message": "Sale completed successfully", "sale_id": sale_id, "total": total}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales")
async def get_sales(limit: int = 50):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT s.sale_id, s.sale_time, s.total_amount, s.payment_method, 
                       c.name as customer, e.name as employee
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.customer_id
                LEFT JOIN employees e ON s.employee_id = e.employee_id
                ORDER BY s.sale_time DESC
                LIMIT :limit
            """), {"limit": limit})
            rows = result.fetchall()
        
        sales = [
            {
                "sale_id": r[0],
                "sale_time": str(r[1]),
                "total_amount": float(r[2]),
                "payment_method": r[3],
                "customer": r[4],
                "employee": r[5]
            }
            for r in rows
        ]
        return {"sales": sales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales/{sale_id}")
async def get_sale_details(sale_id: int):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT si.product_id, p.name, si.quantity, si.unit_price, si.subtotal
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = :sid
            """), {"sid": sale_id})
            rows = result.fetchall()
        
        items = [
            {
                "product_id": r[0],
                "product_name": r[1],
                "quantity": r[2],
                "unit_price": float(r[3]),
                "subtotal": float(r[4]) if r[4] else 0
            }
            for r in rows
        ]
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
async def get_customers():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT customer_id, name, phone, email FROM customers ORDER BY name"))
            rows = result.fetchall()
        
        customers = [
            {"customer_id": r[0], "name": r[1], "phone": r[2], "email": r[3]}
            for r in rows
        ]
        return {"customers": customers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers")
async def add_customer(customer: Customer):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO customers (name, phone, email)
                VALUES (:name, :phone, :email)
                RETURNING customer_id
            """), {
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email
            })
            customer_id = result.fetchone()[0]
        return {"message": "Customer added successfully", "customer_id": customer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/employees")
async def get_employees():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT employee_id, name, role, username FROM employees ORDER BY name"))
            rows = result.fetchall()
        
        employees = [
            {"employee_id": r[0], "name": r[1], "role": r[2], "username": r[3]}
            for r in rows
        ]
        return {"employees": employees}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/employees")
async def add_employee(employee: Employee):
    try:
        hashed_password = bcrypt.hashpw(employee.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO employees (name, role, username, password)
                VALUES (:name, :role, :username, :password)
                RETURNING employee_id
            """), {
                "name": employee.name,
                "role": employee.role,
                "username": employee.username,
                "password": hashed_password
            })
            employee_id = result.fetchone()[0]
        return {"message": "Employee added successfully", "employee_id": employee_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}/stock")
async def update_stock(product_id: int, stock_update: StockUpdate):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE products 
                SET stock_quantity = stock_quantity + :qty
                WHERE product_id = :pid
                RETURNING name, stock_quantity
            """), {"qty": stock_update.quantity, "pid": product_id})
            
            updated = result.fetchone()
            if not updated:
                raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": f"Stock updated for {updated[0]}", "new_stock": updated[1]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    try:
        with engine.connect() as conn:
            total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            total_sales = conn.execute(text("SELECT COUNT(*) FROM sales")).scalar()
            total_revenue = conn.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM sales")).scalar()
            low_stock_count = conn.execute(text("""
                SELECT COUNT(*) FROM products 
                WHERE stock_quantity <= low_stock_threshold
            """)).scalar()
            
            recent_sales = conn.execute(text("""
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM sales 
                WHERE DATE(sale_time) = DATE('now')
            """)).scalar()
        
        return {
            "total_products": total_products,
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "low_stock_count": low_stock_count,
            "today_sales": float(recent_sales)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notifications")
async def get_notifications():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT n.notification_id, n.message, n.status, n.notification_type, 
                       n.created_at, p.name as product_name
                FROM notifications n
                LEFT JOIN products p ON n.product_id = p.product_id
                ORDER BY n.created_at DESC
                LIMIT 50
            """))
            rows = result.fetchall()
        
        notifications = [
            {
                "notification_id": r[0],
                "message": r[1],
                "status": r[2],
                "type": r[3],
                "created_at": str(r[4]),
                "product_name": r[5]
            }
            for r in rows
        ]
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/sales-by-date")
async def get_sales_by_date(days: int = 7):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT DATE(sale_time) as sale_date, COUNT(*) as count, SUM(total_amount) as total
                FROM sales
                WHERE sale_time >= DATE('now', :days_ago)
                GROUP BY DATE(sale_time)
                ORDER BY sale_date DESC
            """), {"days_ago": f"-{days} days"})
            rows = result.fetchall()
        
        data = [
            {"date": str(r[0]), "count": r[1], "total": float(r[2])}
            for r in rows
        ]
        return {"sales_by_date": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
