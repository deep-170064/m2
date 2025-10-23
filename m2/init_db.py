import sqlite3
import os
import bcrypt

DB_PATH = "supermarket.db"

def init_database():
    """Initialize SQLite database with schema"""
    
    if os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' already exists")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE,
        email VARCHAR(100) UNIQUE,
        address TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        barcode VARCHAR(50) UNIQUE,
        price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        category_id INTEGER NOT NULL REFERENCES categories(category_id),
        low_stock_threshold INTEGER DEFAULT 10,
        supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) UNIQUE,
        email VARCHAR(100) UNIQUE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN','CASHIER','MANAGER')),
        username VARCHAR(50) UNIQUE NOT NULL, 
        password TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
        payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('CASH','CARD','UPI','WALLET')),
        customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
        employee_id INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE sale_items (
        sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(product_id),
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
        subtotal DECIMAL(10,2)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE purchase_orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
        order_date DATE DEFAULT CURRENT_DATE,
        status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RECEIVED', 'CANCELLED'))
    )
    """)
    
    cursor.execute("""
    CREATE TABLE purchase_order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES purchase_orders(order_id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(product_id),
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE notifications (
        notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER REFERENCES products(product_id),
        message TEXT NOT NULL,
        status VARCHAR(10) DEFAULT 'unread',
        notification_type VARCHAR(20) DEFAULT 'low_stock',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP
    )
    """)
    
    employees = [
        ('Alice Johnson', 'ADMIN', 'alicej', bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')),
        ('Bob Smith', 'CASHIER', 'bobs', bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')),
        ('Carol Davis', 'MANAGER', 'carold', bcrypt.hashpw('manager123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')),
        ('Emma Wilson', 'CASHIER', 'emma', bcrypt.hashpw('cashier123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
    ]
    cursor.executemany("""
    INSERT INTO employees (name, role, username, password) VALUES (?, ?, ?, ?)
    """, employees)
    
    cursor.execute("""
    INSERT INTO categories (name, description) VALUES
    ('Beverages', 'Drinks and beverages'),
    ('Snacks', 'Chips and snacks'),
    ('Dairy', 'Milk products'),
    ('Groceries', 'General groceries'),
    ('Electronics', 'Electronic items')
    """)
    
    cursor.execute("""
    INSERT INTO suppliers (name, phone, email, address) VALUES
    ('ABC Suppliers', '1234567890', 'abc@supply.com', '123 Main St'),
    ('XYZ Wholesale', '0987654321', 'xyz@wholesale.com', '456 Oak Ave'),
    ('Global Trade Co', '5551234567', 'global@trade.com', '789 Pine Rd')
    """)
    
    cursor.execute("""
    INSERT INTO products (name, barcode, price, stock_quantity, category_id, supplier_id, low_stock_threshold) VALUES
    ('Coca Cola 500ml', 'CC500', 40.00, 100, 1, 1, 20),
    ('Lays Classic 50g', 'LC50', 20.00, 150, 2, 1, 30),
    ('Milk 1L', 'M1L', 60.00, 80, 3, 2, 15),
    ('Bread Loaf', 'BL001', 35.00, 120, 4, 2, 25),
    ('USB Cable', 'USB001', 150.00, 50, 5, 3, 10)
    """)
    
    cursor.execute("""
    INSERT INTO customers (name, phone, email) VALUES
    ('John Doe', '1111111111', 'john@email.com'),
    ('Jane Smith', '2222222222', 'jane@email.com'),
    ('Mike Brown', '3333333333', 'mike@email.com')
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database '{DB_PATH}' created successfully with sample data!")

if __name__ == "__main__":
    init_database()
