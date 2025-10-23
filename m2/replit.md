# SuperMarket Inventory & Billing System

## Overview
A comprehensive full-stack web application for supermarket management with inventory tracking, point-of-sale (POS) system, customer and employee management, and advanced analytics.

## Project Structure

### Backend (Python/FastAPI)
- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: SQLite (for development, can be switched to PostgreSQL)
- **Key Files**:
  - `api_server.py` - Main FastAPI application with REST endpoints
  - `db_config.py` - Database configuration and connection management
  - `init_db.py` - Database initialization with schema and sample data
  - Legacy CLI modules: `cli.py`, `auth.py`, `product_management.py`, `sales_management.py`, etc.

### Frontend (React)
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **API Communication**: Axios
- **Location**: `/frontend` directory
- **Key Features**:
  - Authentication with role-based access (Admin, Manager, Cashier)
  - Dashboard with real-time statistics
  - Product management (add, view, restock)
  - Point-of-sale (POS) for processing sales
  - Customer and employee management
  - Responsive design with modern UI

### Database Schema
The system uses the following main tables:
- `employees` - User authentication and role management
- `products` - Product inventory with stock tracking
- `categories` - Product categorization
- `suppliers` - Supplier information
- `customers` - Customer records
- `sales` - Sales transactions
- `sale_items` - Individual items in each sale
- `purchase_orders` - Inventory restocking orders
- `notifications` - System alerts and notifications

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm

### Running the Application

#### Development Mode
The application runs two workflows:
1. **Backend API**: Runs on http://localhost:8000
2. **Frontend**: Runs on http://localhost:5000 (accessible via web preview)

Both workflows start automatically when the Repl runs.

#### Demo Credentials
- **Admin**: 
  - Username: `alicej`
  - Password: `admin123`
  - Access: Full system access

- **Manager**: 
  - Username: `carold`
  - Password: `manager123`
  - Access: Product management, sales, reports, customers

- **Cashier**: 
  - Username: `emma`
  - Password: `cashier123`
  - Access: View products, process sales, notifications

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login

#### Products
- `GET /api/products` - List all products
- `POST /api/products` - Add new product (Admin only)
- `PUT /api/products/{id}/stock` - Update stock

#### Sales
- `GET /api/sales` - List sales
- `POST /api/sales` - Create new sale
- `GET /api/sales/{id}` - Get sale details

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

#### Others
- `/api/customers` - Customer management
- `/api/employees` - Employee management
- `/api/categories` - Product categories
- `/api/suppliers` - Supplier information
- `/api/notifications` - System notifications
- `/api/reports/sales-by-date` - Sales reports

## Features

### Role-Based Access Control
- **Admin**: Full access to all features including employee management
- **Manager**: Product management, sales, reports, customer management
- **Cashier**: View products, process sales, view notifications

### Core Functionality
1. **Inventory Management**
   - Add/view products
   - Stock tracking with low-stock alerts
   - Category and supplier organization

2. **Point of Sale (POS)**
   - Quick product selection
   - Cart management
   - Multiple payment methods (Cash, Card, UPI, Wallet)
   - Customer association

3. **Customer Management**
   - Customer records with contact information
   - Purchase history tracking

4. **Employee Management**
   - Role-based user accounts
   - Secure authentication

5. **Dashboard & Analytics**
   - Real-time statistics
   - Sales tracking
   - Low stock alerts
   - Revenue reporting

## Tech Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- Pydantic - Data validation
- Uvicorn - ASGI server
- SQLite/PostgreSQL - Database

### Frontend
- React 18 - UI framework
- React Router - Client-side routing
- Axios - HTTP client
- Vite - Build tool and dev server

## Database
- Currently using SQLite for portability
- Can easily switch to PostgreSQL by updating `db_config.py`
- Includes sample data for testing

## Recent Changes
- Migrated from CLI-based application to full-stack web application
- Created RESTful API with FastAPI
- Built modern React frontend with role-based access
- Configured for Replit deployment
- Set up dual workflows for frontend and backend

## Deployment
The application is configured for deployment with:
- Frontend build process
- Backend API server on port 5000
- Autoscale deployment target for optimal performance

## Future Enhancements
- Advanced analytics and reporting
- Inventory optimization
- Supplier performance tracking
- Mobile app support
- Real-time notifications via WebSockets
