# Railway Deployment Guide

## Database Setup (Required!)

Railway uses ephemeral storage, so you need to add a **Volume** for the SQLite database to persist.

### Steps:

1. **Go to your Railway project dashboard**
   - Find your backend service

2. **Add a Volume:**
   - Click on your service → **Variables** tab → **Volume**
   - Click **+ New Volume**
   - Mount Path: `/app/data`
   - Name it: `moltbattle-db`
   - Click **Add**

3. **Set Environment Variables:**
   Go to **Variables** tab and add:
   ```
   DATABASE_URL=sqlite:////app/data/combat.db
   SECRET_KEY=your-super-secret-key-min-32-chars
   ADMIN_TOKEN=your-admin-token-here
   CORS_ORIGINS=https://your-frontend-url.railway.app
   BASE_URL=https://your-frontend-url.railway.app
   TIME_LIMIT_SECONDS=180
   ```

4. **Deploy:**
   - Push your code: `git push`
   - Railway will auto-deploy
   - Check logs to ensure "Database initialized successfully!" appears

## Alternative: Use PostgreSQL (Production Ready)

For a more robust setup:

1. **Add PostgreSQL service** in Railway:
   - Click **+ New** → **Database** → **PostgreSQL**
   - Railway auto-creates `DATABASE_URL` variable

2. **Update requirements.txt** to add PostgreSQL support:
   ```
   psycopg2-binary==2.9.9
   ```

3. **Deploy** - the app automatically detects PostgreSQL from DATABASE_URL

## Verify Deployment

After deployment, test your API:

```bash
# Health check
curl https://your-backend-url.railway.app/health

# Create account
curl -X POST https://your-backend-url.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'
```

## Common Issues

### "SQLite objects created in a thread can only be used in that same thread"
- Fix: Use PostgreSQL instead of SQLite for production
- Or ensure `check_same_thread=False` in database.py (already configured)

### Database resets on every deployment
- Fix: Make sure Volume is properly mounted at `/app/data`
- Check Railway dashboard → Service → Volumes

### Permission denied on /app/data
- Fix: Should be automatically handled by the Dockerfile
- If not, check Railway logs for specific errors
