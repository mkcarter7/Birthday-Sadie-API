# Railway Deployment Guide

This guide will help you deploy the Birthday Sadie API to Railway, which provides **persistent disk storage** so your media files won't be lost on redeploy.

## 🚀 Quick Start

### 1. Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended) or email
3. Click "New Project"

### 2. Deploy Backend

1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your `Birthday-Sadie-API` repository
3. Railway will auto-detect it's a Python project

### 3. Add PostgreSQL Database

1. In your Railway project, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically:
   - Create the database
   - Set `DATABASE_URL` environment variable
   - Link it to your web service

### 4. Add Persistent Disk Storage (for media files)

1. In your Railway project, click **"+ New"** → **"Volume"**
2. Name it `media-storage` (or similar)
3. Set mount path to `/media` (or `/opt/render/project/src/media`)
4. Link it to your web service

**Important:** The volume mount path should match your `MEDIA_ROOT` in `settings.py`. By default, it's `BASE_DIR / 'media'`, which translates to `/opt/render/project/src/media` on Railway.

### 5. Set Environment Variables

In your Railway web service, go to **"Variables"** and add:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=birthday-sadie-api.up.railway.app,your-custom-domain.com

# Firebase (from your .env file)
FIREBASE_PROJECT_ID=birthday-sadie
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}  # Your full JSON as a single line

# CORS (your frontend URL)
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.railway.app

# Python Version (optional, Railway auto-detects)
PYTHON_VERSION=3.11.9
```

**Note:** For `FIREBASE_SERVICE_ACCOUNT_JSON`, paste the entire JSON as a single line (no newlines).

### 6. Run Migrations

After deployment, run migrations:

1. Go to your web service in Railway
2. Click **"Deployments"** → **"View Logs"**
3. Or use Railway CLI:
   ```bash
   railway run python manage.py migrate
   ```

### 7. Load Fixtures (Optional)

```bash
railway run python manage.py loaddata birthdayapi/fixtures/party.json
railway run python manage.py loaddata birthdayapi/fixtures/timeline_events.json
railway run python manage.py loaddata birthdayapi/fixtures/trivia_questions.json
```

### 8. Create Superuser (Optional)

```bash
railway run python manage.py createsuperuser
```

## 📁 Frontend Options

Railway works great with **any frontend**:

### Option 1: Keep Using Vercel (Recommended)
- **Pros:** Vercel is excellent for Next.js, free tier, great performance
- **Cons:** Two separate services to manage
- **Setup:** Just update `NEXT_PUBLIC_API_URL` in Vercel to point to your Railway backend URL

### Option 2: Deploy Frontend to Railway
- **Pros:** Everything in one place, easier to manage
- **Cons:** Railway's Next.js support is good but Vercel is optimized for Next.js
- **Setup:** Add your frontend repo as a second service in Railway

### Option 3: Deploy Frontend to Railway (Monorepo)
- **Pros:** Single deployment, shared environment variables
- **Cons:** More complex setup
- **Setup:** Use Railway's monorepo support

**Recommendation:** Keep using Vercel for frontend (it's the best for Next.js), and use Railway for backend (persistent storage).

## 🔧 Configuration Details

### Media Files Storage

With Railway's persistent volumes, your media files will:
- ✅ Persist across redeploys
- ✅ Survive service restarts
- ✅ Be accessible via `/media/` URLs

The volume should be mounted at the same path as `MEDIA_ROOT` in your Django settings.

### Static Files

Static files are handled by WhiteNoise and collected during build. They're served from the application, not from a volume.

### Database

Railway automatically provides PostgreSQL and sets `DATABASE_URL`. No additional configuration needed.

## 🌐 Custom Domain (Optional)

1. In Railway, go to your web service → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"** or **"Custom Domain"**
3. Update `ALLOWED_HOSTS` to include your custom domain

## 🔍 Troubleshooting

### Media Files Not Persisting

- Check that the volume is mounted correctly
- Verify `MEDIA_ROOT` path matches volume mount path
- Check volume size (upgrade if needed)

### Static Files 404

- Ensure `collectstatic` runs during build (it's in `railway.json`)
- Check WhiteNoise middleware is enabled in `settings.py`

### Database Connection Issues

- Verify `DATABASE_URL` is set automatically by Railway
- Check database service is running
- Run migrations: `railway run python manage.py migrate`

### CORS Errors

- Update `CORS_ALLOWED_ORIGINS` with your frontend URL
- Ensure no trailing slashes in URLs
- Check frontend is using correct `NEXT_PUBLIC_API_URL`

## 📊 Monitoring

Railway provides:
- **Logs:** Real-time application logs
- **Metrics:** CPU, memory, network usage
- **Deployments:** History of all deployments

## 💰 Pricing

- **Free Tier:** $5 credit/month
- **Starter Plan:** ~$5/month (includes persistent storage)
- **Pro Plan:** $20/month (more resources)

## 🔗 Useful Links

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Django on Railway](https://docs.railway.app/guides/django)

## ✅ Migration Checklist

- [ ] Create Railway account
- [ ] Deploy backend from GitHub
- [ ] Add PostgreSQL database
- [ ] Add persistent volume for media files
- [ ] Set all environment variables
- [ ] Run migrations
- [ ] Load fixtures (optional)
- [ ] Update frontend `NEXT_PUBLIC_API_URL`
- [ ] Test API endpoints
- [ ] Test media file uploads
- [ ] Verify files persist after redeploy

