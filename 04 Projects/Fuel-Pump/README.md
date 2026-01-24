# Fuel Pump Management System

A full-stack web application for managing fuel station operations, including inventory management, customer management, fuel dispensing transactions, and invoicing.

## Features

### Core Functionality
- **User Management**: Role-based access control (Admin, Cashier, Customer)
- **Customer Management**: Manage registered and walk-in customers with credit limits
- **Product Management**: Manage fuel types (Petrol, HSD, HOBC) and lubricants with pricing
- **Inventory Tracking**: Real-time fuel stock monitoring with low-stock alerts
- **Transaction Processing**: Liter-based and amount-based fuel dispensing with multiple payment modes
- **Meter Reading Management**: Daily pump meter opening/closing with reconciliation
- **Invoice Generation**: Automated billing for credit customers with payment tracking
- **JWT Authentication**: Secure token-based authentication with refresh tokens

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115.0
- **Database**: SQLite (with async support via aiosqlite)
- **ORM**: SQLAlchemy 2.0.35 (async)
- **Migrations**: Alembic 1.13.3
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **Validation**: Pydantic 2.10.1

### Frontend
- **Framework**: React 19.2.0 with TypeScript
- **Build Tool**: Vite 7.2.4
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **State Management**: React Context API

## Project Structure

```
Fuel-Pump/
├── backend/
│   ├── app/
│   │   ├── api/          # API route endpoints
│   │   ├── core/         # Security and configuration
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── database.py   # Database configuration
│   │   └── main.py       # FastAPI application entry point
│   ├── alembic/          # Database migrations
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── api/          # API client and endpoints
│   │   ├── components/   # Reusable components
│   │   ├── contexts/     # React Context providers
│   │   ├── layout/       # Layout components
│   │   ├── pages/        # Page components
│   │   ├── types/        # TypeScript types
│   │   └── App.tsx       # Main app component with routing
│   ├── package.json      # Node.js dependencies
│   └── .env             # Environment variables
└── README.md            # This file
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (`.env` is already configured):
```env
DATABASE_URL=sqlite+aiosqlite:///./fuel_pump.db
SYNC_DATABASE_URL=sqlite:///./fuel_pump.db
SECRET_KEY=fuel-pump-secret-key-change-in-production-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Configure environment variables (`.env` is already configured):
```env
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Creating Initial Users

After starting the backend, you'll need to create users via the API or database. Here are some example user creation commands using the API:

### Create Admin User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123",
    "role": "ADMIN"
  }'
```

Or use Python:
```python
from app.core.security import get_password_hash
from app.models.user import User
from app.database import AsyncSessionLocal

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@test.com",
            password_hash=get_password_hash("admin123"),
            role="ADMIN"
        )
        db.add(admin)
        await db.commit()
```

### Demo Accounts (for testing)
- Admin: `admin@test.com` / `admin123`
- Cashier: `cashier@test.com` / `cashier123`
- Customer: `customer@test.com` / `customer123`

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## User Roles & Permissions

### Admin
- Create and manage users
- Manage customers and credit limits
- Manage products and pricing
- Approve/reject pending transactions
- Generate and manage invoices
- View all reports

### Cashier
- Create fueling transactions
- Manage pump meter readings
- View own pending transactions

### Customer
- View profile and statements
- View invoices and payment history
- Update personal information

## Database Schema

The application uses the following main tables:
- `users` - User accounts and authentication
- `customers` - Customer profiles and credit limits
- `products` - Fuel products and lubricants
- `inventory` - Current stock levels
- `fueling_transactions` - All fueling transactions
- `meter_readings` - Daily pump meter readings
- `invoices` - Customer billing invoices
- `invoice_items` - Invoice line items
- `payments` - Payment records
- `price_history` - Product price change history

## Development

### Backend Development
- Run tests: `pytest`
- Format code: `black .`
- Lint code: `flake8`
- Create migration: `alembic revision --autogenerate -m "description"`
- Apply migration: `alembic upgrade head`

### Frontend Development
- Run tests: `npm test`
- Build for production: `npm run build`
- Preview production build: `npm run preview`

## Production Deployment

For production deployment:

1. **Change the SECRET_KEY** in `.env` to a secure random value
2. **Use PostgreSQL** instead of SQLite for production
3. **Set DEBUG=False** in backend config
4. **Use a production WSGI server** like Gunicorn
5. **Set up CORS** properly for your frontend domain
6. **Enable HTTPS** for secure communication

## License

This project is for educational purposes.

## Support

For issues or questions, please contact the development team.
