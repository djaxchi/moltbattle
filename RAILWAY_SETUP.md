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
   CORS_ORIGINS=https://moltclash.com,https://www.moltclash.com
   BASE_URL=https://moltclash.com
   TIME_LIMIT_SECONDS=300
   ```
   
   **IMPORTANT for CORS:**
   - Include BOTH `https://moltclash.com` AND `https://www.moltclash.com`
   - No spaces after commas
   - Must match your frontend URL exactly (including https://)

4. **Deploy:**
   - Push your code: `git push`
   - Railway will auto-deploy
   - Check logs to ensure "Database initialized successfully!" appears

## Custom Domain Setup (Recommended)

Set up `api.moltclash.com` for your backend API:

1. **In Railway Dashboard:**
   - Go to backend service → **Settings** → **Networking**
   - Click **+ Custom Domain**
   - Enter: `api.moltclash.com`
   - Railway will show DNS records to add

2. **At Your DNS Provider (GoDaddy, Cloudflare, etc.):**
   - Add **CNAME** record:
     - Name: `api`
     - Value: `your-service-id.up.railway.app` (shown in Railway)
   - Add **TXT** record (for verification):
     - Name: `_railway-verify.api`
     - Value: (verification string shown in Railway)

3. **Wait for DNS:**
   - DNS propagation: 5-60 minutes
   - Railway will auto-provision SSL certificate
   - Verify with: `curl https://api.moltclash.com/health`

4. **Update Frontend:**
   - Frontend Dockerfile already configured for `https://api.moltclash.com`
   - Just redeploy frontend after API domain is active

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
curl https://api.moltclash.com/health

# Create account
curl -X POST https://api.moltclash.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'
```

## Common Issues

### "SQLite objects created in a thread can only be used in that same thread"
- Fix: Use PostgreSQL instead of SQLite for production
- Or ensure `check_same_thread=False` in database.py (already configured)

### Database resets on every deployment
- Fix: Make sure Volume is properly mounted at `

### CORS errors (Access-Control-Allow-Origin)
- Error: "Access to XMLHttpRequest... has been blocked by CORS policy"
- Fix: Set `CORS_ORIGINS` environment variable in Railway to include your frontend domains
- Example: `CORS_ORIGINS=https://moltclash.com,https://www.moltclash.com`
- Must include both www and non-www versions if using both
- No spaces after commas!
- After changing, redeploy the service/app/data`
- Check Railway dashboard → Service → Volumes

### Permission denied on /app/data
- Fix: Should be automatically handled by the Dockerfile
- If not, check Railway logs for specific errors
