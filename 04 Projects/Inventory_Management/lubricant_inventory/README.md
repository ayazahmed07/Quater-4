# Lubricant Inventory Management System - Next.js

A complete inventory management system for fuel pump lubricant businesses with a modern Next.js frontend and FastAPI backend.

## Features

- **Modern UI**: Built with Next.js 14, TypeScript, and shadcn/ui components
- **JWT Authentication**: Secure login system for cashiers
- **Dashboard**: Real-time statistics and stock overview
- **Item Management**: CRUD operations with Excel import
- **Purchase Entry**: Track purchases from PSO
- **Sales Entry**: Record sales by cashier with shift tracking
- **Physical Stock**: Weekly physical stock verification
- **Reports**: Stock comparison, sales, and purchase reports with Excel export

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- TanStack Query (React Query)
- Axios

### Backend
- Python FastAPI
- SQLite database
- JWT authentication
- Pydantic for validation

## Project Structure

```
lubricant_inventory/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLite setup
│   ├── models.py            # Pydantic models
│   ├── crud.py              # Database operations
│   ├── reports.py           # Report generation
│   ├── auth.py              # JWT authentication
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Dashboard
│   │   ├── login/           # Login page
│   │   ├── items/           # Items page
│   │   ├── purchases/       # Purchases page
│   │   ├── sales/           # Sales page
│   │   ├── physical-stock/  # Physical stock page
│   │   └── reports/         # Reports page
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   └── sidebar.tsx      # Navigation sidebar
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── query.tsx        # React Query setup
│   │   └── utils.ts
│   └── package.json
│
└── data/
    └── inventory.db         # SQLite database
```

## Installation

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python database.py  # Initialize database and create default users
```

**Default Login Credentials:**
- Cashier 1: `cashier1` / `cashier123`
- Cashier 2: `cashier2` / `cashier123`
- Admin: `admin` / `admin123`

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Environment Configuration

The frontend uses `.env.local` (already created):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will run at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

Frontend will run at: http://localhost:3000

## Usage

### 1. Login
- Open http://localhost:3000
- You'll be redirected to the login page
- Use one of the default credentials

### 2. Dashboard
- View statistics: total items, purchases, sales, current stock
- See current stock overview table

### 3. Manage Items
- Add new lubricant items
- Edit existing items
- Import items from Excel (columns: Item Name, Grade, Pack Size, Purchase Price, Sale Price, Opening Stock)

### 4. Record Purchases
- Add purchases from PSO
- Stock automatically increases

### 5. Record Sales
- Add sales with cashier and shift
- Stock automatically decreases
- Prevents negative stock

### 6. Physical Stock
- Record weekly physical counts
- See comparison with system stock

### 7. Reports
- Stock Comparison: System vs Physical with shortage/excess
- Current Stock: All items with current levels
- Sales Report: Filter by date range
- Purchase Report: Filter by date range

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Dashboard
- `GET /api/dashboard/stats` - Get statistics

### Items
- `GET /api/items` - List all items
- `POST /api/items` - Create item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item
- `POST /api/items/import` - Import from Excel

### Purchases
- `GET /api/purchases` - List all purchases
- `POST /api/purchases` - Create purchase

### Sales
- `GET /api/sales` - List all sales
- `POST /api/sales` - Create sale
- `GET /api/sales/summary` - Cashier performance

### Physical Stock
- `GET /api/physical-stock` - List all entries
- `POST /api/physical-stock` - Create entry

### Reports
- `GET /api/reports/stock-comparison` - System vs Physical
- `GET /api/reports/current-stock` - Current stock levels
- `GET /api/reports/sales` - Sales report
- `GET /api/reports/purchases` - Purchase report

## Database Schema

### USERS
- user_id, username, password_hash, full_name, role

### ITEMS
- item_id, item_name, grade, pack_size, purchase_price, sale_price, opening_stock

### PURCHASES
- purchase_id, date, invoice_no, item_id, quantity, rate

### SALES
- sale_id, date, cashier_name, shift, item_id, quantity

### PHYSICAL_STOCK
- entry_id, date, item_id, physical_quantity

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
cd frontend
npm run build
npm start
```

## Troubleshooting

### Backend Issues
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Reinitialize database: `python database.py`

### Frontend Issues
- Clear browser cache and localStorage
- Make sure backend is running on port 8000
- Check `.env.local` has correct API URL
- Run `npm install` to ensure all dependencies are installed

### CORS Issues
- If you see CORS errors, check backend CORS settings in `main.py`
- Ensure frontend URL (http://localhost:3000) is in allowed origins

## License

MIT
