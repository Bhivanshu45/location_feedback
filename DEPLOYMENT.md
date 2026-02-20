# Location Safety RAG API - Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (free tier works)
3. PostgreSQL database (Render provides free tier)

## Step 1: Push to GitHub

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit - Location Safety RAG API"

# Create a new repository on GitHub
# Then connect and push:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/location-feedback-api.git
git push -u origin main
```

## Step 2: Setup PostgreSQL on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **PostgreSQL**
3. Fill details:
   - Name: `location-safety-db`
   - Database: `location_safety`
   - User: (auto-generated)
   - Region: Choose closest
   - Plan: **Free**
4. Click **"Create Database"**
5. Copy the **External Database URL** (will look like: `postgresql://user:pass@host/database`)

## Step 3: Deploy API on Render

1. Click **"New +"** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - Name: `location-feedback-api`
   - Environment: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `DATABASE_URL` = (paste the PostgreSQL URL from Step 2)
   - `GROQ_API_KEY` = (your Groq API key from https://console.groq.com)
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `False`
5. Click **"Create Web Service"**

## Step 4: Wait for Deployment

- Render will automatically:
  - Pull your code from GitHub
  - Install dependencies
  - Start the application
- Check logs for any errors
- First deploy takes ~5-10 minutes (embedding model download)

## Step 5: Access Your API

Once deployed, your API will be available at:
```
https://location-feedback-api.onrender.com
```

API Documentation:
```
https://location-feedback-api.onrender.com/docs
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| GROQ_API_KEY | Groq API key | `gsk_...` |
| ENVIRONMENT | App environment | `production` |
| DEBUG | Debug mode | `False` |
| LLM_MODEL | LLM model name | `mixtral-8x7b-32768` |

## Auto-Deploy on Push

Render automatically redeploys when you push to `main` branch:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correct (including URL encoding for special chars)
- Check if Render PostgreSQL database is running

### Embedding Model Download
- First request will be slow (~2-3 min) due to model download
- Model is cached after first download
- Check logs: "Loading embedding model"

### API Not Responding
- Check Render logs for errors
- Verify all environment variables are set
- Ensure PostgreSQL database is active

## Free Tier Limits

**Render Free Tier:**
- API sleeps after 15 min inactivity
- First request after sleep: ~30 sec wake-up time
- 750 hours/month free

**PostgreSQL Free Tier:**
- 1 GB storage
- Expires after 90 days (data deleted)
- For production: upgrade to paid plan

## Cost-Effective Production Setup

For long-term production:
1. Upgrade PostgreSQL to paid plan ($7/month)
2. Keep API on free tier (good for low traffic)
3. Or upgrade API to paid for always-on service ($7/month)

## Monitoring

Check these regularly:
- Render dashboard for uptime
- Database storage usage
- API logs for errors
- Response times

---

**🚀 You're ready to deploy!**
