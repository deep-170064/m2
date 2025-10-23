

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- Added NOT NULL
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    address TEXT

);


-- Categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);



CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,              -- product name required
    barcode VARCHAR(50) UNIQUE,              -- must be unique
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),  -- price can’t be negative
    stock_quantity INT NOT NULL DEFAULT 0,   -- default stock is 0
    category_id INT NOT NULL REFERENCES categories(category_id),
    low_stock_threshold INT DEFAULT 10,      -- default threshold for stock alert
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id)
);



-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE
);

-- Employees
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN','CASHIER','MANAGER')),
    username VARCHAR(50) UNIQUE NOT NULL, 
    password TEXT NOT NULL
);

-- Sales
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0  CHECK (total_amount >= 0), -- Added NOT NULL and DEFAULT
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('CASH','CARD','UPI','WALLET')),
    customer_id INT REFERENCES customers(customer_id) ON DELETE SET NULL,
    employee_id INT REFERENCES employees(employee_id) ON DELETE SET NULL

);

-- Sale Items
CREATE TABLE sale_items (
    sale_item_id SERIAL PRIMARY KEY,
    sale_id INT NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);


-- Purchase Orders
CREATE TABLE purchase_orders (
    order_id SERIAL PRIMARY KEY,
    supplier_id INT NOT NULL REFERENCES suppliers(supplier_id),
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RECEIVED', 'CANCELLED'))

);

-- Purchase Order Items
CREATE TABLE purchase_order_items (
    order_item_id SERIAL PRIMARY KEY,
order_id INT NOT NULL REFERENCES purchase_orders(order_id) ON DELETE CASCADE,
product_id INT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    message TEXT NOT NULL,
    status VARCHAR(10) DEFAULT 'unread', -- unread / read
    notification_type VARCHAR(20) DEFAULT 'low_stock',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

