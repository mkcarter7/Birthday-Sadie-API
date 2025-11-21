# Railway Quick Start Guide

## 🎯 Frontend Recommendation

**Best Option: Keep using Vercel for frontend, Railway for backend**

- ✅ Vercel is optimized for Next.js (your frontend)
- ✅ Railway provides persistent storage (your backend needs)
- ✅ Both have excellent free tiers
- ✅ Just update `NEXT_PUBLIC_API_URL` in Vercel to point to Railway

## 🚀 5-Minute Setup

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `Birthday-Sadie-API`

### Step 2: Add Database
1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway automatically sets `DATABASE_URL`

### Step 3: Add Persistent Storage (Important!)
1. Click **"+ New"** → **"Volume"**
2. Name: `media-storage`
3. Mount path: `/media` (or check your `MEDIA_ROOT` in settings.py)
4. Link to your web service

### Step 4: Set Environment Variables
Go to your web service → **"Variables"** tab:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*.up.railway.app
FIREBASE_PROJECT_ID=birthday-sadie
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}  # Full JSON as one line
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Step 5: Run Migrations
After first deployment:
1. Go to **"Deployments"** → Click on deployment → **"View Logs"**
2. Or use Railway CLI: `railway run python manage.py migrate`

### Step 6: Update Frontend
In Vercel, update environment variable:
```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

## ✅ Done!

Your backend is now on Railway with persistent storage. Media files will persist across redeploys!

## 📚 Full Guide

See `RAILWAY_DEPLOY.md` for detailed instructions.

