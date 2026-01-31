# Cloud Deployment Guide - Lubricant Inventory Management System

This guide will help you deploy your inventory management system to the cloud for **FREE** using:
- **Render** (Backend API + PostgreSQL Database)
- **Vercel** (Frontend Next.js Application)

---

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Render account (free at https://render.com)
3. Vercel account (free at https://vercel.com)
4. Supabase account (optional, for free PostgreSQL database)

---

## Step 1: Prepare Your Code

### 1.1 Push Code to GitHub

If you haven't already, push your code to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## Step 2: Set Up Supabase Database (Free PostgreSQL)

### 2.1 Create Supabase Account
1. Go to https://supabase.com
2. Sign up for a free account
3. Click "New Project"

### 2.2 Create Database
1. Project name: `lubricant-inventory`
2. Database password: (generate a strong password and save it)
3. Region: Choose closest to your users

### 2.3 Get Database Connection String
1. Go to your project in Supabase
2. Click "Settings" → "Database"
3. Scroll to "Connection string"
4. Copy the **URI** format (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`)
5. Save this connection string - you'll need it for Render

**Important**: Replace `[YOUR-PASSWORD]` with your actual database password.

---

## Step 3: Deploy Backend to Render

### 3.1 Create Render Account
1. Go to https://render.com
2. Sign up/login with GitHub

### 3.2 Create PostgreSQL Database

**Option A: Use Supabase (Recommended - Free)**
1. Skip database creation in Render
2. You'll use Supabase database instead

**Option B: Use Render Database ($7/month)**
1. Click "New" → "PostgreSQL"
2. Name: `lubricant-inventory-db`
3. Database: `lubricant_inventory`
4. User: `lubricant_user`
5. Region: Singapore (or closest)
6. Click "Create Database"

### 3.3 Create Web Service (Backend API)

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `lubricant-inventory-api`
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables:
   - Click "Advanced" → "Add Environment Variable"
   - **DATABASE_URL**: (Your Supabase or Render connection string)
     - Supabase: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
     - Render: From Render database dashboard

5. Click "Deploy Web Service"

### 3.4 Wait for Deployment
- Render will take 5-10 minutes to deploy
- You'll get a URL like: `https://lubricant-inventory-api.onrender.com`
- Save this URL - you'll need it for Vercel

### 3.5 Test Backend
- Visit: `https://your-api-url.onrender.com/api/health`
- You should see: `{"status":"healthy","message":"Lubricant Inventory API is running"}`

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up/login with GitHub

### 4.2 Import Project
1. Click "Add New" → "Project"
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend`
   - **Build Command**: (auto-detected, keep default)
   - **Output Directory**: (auto-detected, keep default)

### 4.3 Add Environment Variable
1. Click "Environment Variables"
2. Add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your Render backend URL (e.g., `https://lubricant-inventory-api.onrender.com`)
3. Click "Add"

### 4.4 Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Your app will be live at: `https://your-project-name.vercel.app`

---

## Step 5: Test Your Deployed Application

### 5.1 Access Your App
1. Open your Vercel URL
2. You should see the login page
3. Login with:
   - Username: `admin`
   - Password: `admin123`

### 5.2 Create Default Users (First Time Only)

If you need to create default users in the database:

**Using Supabase:**
1. Go to Supabase dashboard
2. Click "Table Editor" → "users"
3. Insert records:
   ```sql
   -- For cashier1 (password: cashier123)
   INSERT INTO users (username, password_hash, full_name, role)
   VALUES ('cashier1', '$2b$12$YourHashedPasswordHere', 'Cashier 1', 'cashier');

   -- For cashier2 (password: cashier123)
   INSERT INTO users (username, password_hash, full_name, role)
   VALUES ('cashier2', '$2b$12$YourHashedPasswordHere', 'Cashier 2', 'cashier');

   -- For admin (password: admin123)
   INSERT INTO users (username, password_hash, full_name, role)
   VALUES ('admin', '$2b$12$YourHashedPasswordHere', 'Administrator', 'admin');
   ```

**Note**: To generate password hashes, you can use a bcrypt generator online or run this locally:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("your_password"))
```

---

## Important Notes

### Database Migration
Your current code uses SQLite. The cloud deployment uses PostgreSQL. The main differences:
- PostgreSQL uses `%s` instead of `?` for query parameters
- PostgreSQL uses `SERIAL` instead of `AUTOINCREMENT`
- PostgreSQL connection strings are different

**Your current code needs to be updated to support PostgreSQL.** Here's what you need to do:

1. Update all database queries to use parameterized queries compatible with PostgreSQL
2. OR use an ORM like SQLAlchemy that handles both databases

### Quick Fix for Deployment

Since your current code is SQLite-specific, here are your options:

**Option 1: Stay with SQLite (Use a VPS)**
- Use a VPS provider like DigitalOcean ($4-6/month)
- You can keep using SQLite
- More setup but familiar code

**Option 2: Update Code for PostgreSQL**
- I can help update the code to support PostgreSQL
- More work but better for cloud deployment

**Option 3: Use Railway (Simpler)**
- Railway supports SQLite through file storage
- Easier deployment
- Still has free tier

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Render (Web Service) | Free | $0 |
| Supabase (Database) | Free | $0 |
| Vercel (Frontend) | Free | $0 |
| **Total** | | **$0/month** |

**Free Tier Limits:**
- Render: 750 hours/month (enough for full-time operation)
- Supabase: 500MB database, 1GB bandwidth/month
- Vercel: Unlimited deployments, 100GB bandwidth/month

---

## Troubleshooting

### Backend Issues

**"Module not found" error**
- Make sure `requirements.txt` is in the `backend` folder
- Check that all dependencies are listed

**Database connection error**
- Verify DATABASE_URL is correct
- Check Supabase/Render database is active
- Ensure password in connection string is correct

**CORS errors in frontend**
- Add your Vercel domain to CORS allowed origins in `main.py`
- Update line 27 in `backend/main.py`:
  ```python
  allow_origins=["https://your-project.vercel.app", "http://localhost:3000"],
  ```

### Frontend Issues

**"API not responding"**
- Check NEXT_PUBLIC_API_URL environment variable
- Verify backend is deployed and running
- Check browser console for errors

**Build fails**
- Ensure all dependencies are in `package.json`
- Check for TypeScript errors

---

## Maintenance

### Updating Your App

1. Make changes locally
2. Test thoroughly
3. Commit to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
4. Render and Vercel will auto-deploy

### Monitoring

- **Render**: Check dashboard for logs, metrics
- **Vercel**: Check deployments tab for build logs
- **Supabase**: Monitor database usage in dashboard

---

## Next Steps

1. Set up custom domain (optional)
2. Configure automatic backups
3. Set up monitoring/alerts
4. Add more users to your team

---

## Need Help?

- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs
- Supabase docs: https://supabase.com/docs

---

**Note**: This deployment guide assumes you want to migrate to PostgreSQL. If you prefer to keep SQLite, consider using a VPS provider like DigitalOcean instead.
