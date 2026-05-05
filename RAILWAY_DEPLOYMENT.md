# Railway Deployment Guide - Mustian Face MVP

## Overview
This guide covers deploying the Mustian Face MVP (face recognition attendance system) to Railway. The backend and frontend are deployed as separate services.

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository with your code
- Railway CLI installed (optional): `npm install -g @railway/cli`

## Backend Deployment (API Service)

### Step 1: Create New Project on Railway
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect the backend service

### Step 2: Configure Backend Service
1. In the Railway project, go to the service settings
2. Set the following:
   - **Root Directory**: `backend` (if monorepo) or leave empty if backend is at root
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Port**: Railway auto-assigns this via `$PORT` environment variable

### Step 3: Add PostgreSQL Database
1. Click "New Service" → "Database" → "PostgreSQL"
2. Railway will automatically set `DATABASE_URL` environment variable
3. The backend is configured to use this variable via `backend/config.py`

### Step 4: Set Environment Variables
Go to the backend service → "Variables" tab and add:

```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FACE_CONFIDENCE_THRESHOLD=0.6
ATTENDANCE_WINDOW_MINUTES=30
UPLOAD_DIR=uploads/faces
```

Generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

### Step 5: Deploy
1. Railway auto-deploys on git push to main branch
2. Monitor the deploy logs in the Railway dashboard
3. The backend should be accessible at: `https://<your-service-name>.up.railway.app`

## Frontend Deployment (Static Site)

### Option A: Deploy Frontend on Railway (Separate Service)
1. Create another service in the same or new Railway project
2. Set root directory to `frontend`
3. Add build command: `npm install && npm run build`
4. Set start command: Use the Dockerfile (nginx serve)

**Environment Variable for Frontend:**
```env
REACT_APP_API_URL=https://<your-backend-service>.up.railway.app
```

### Option B: Deploy Frontend to Vercel/Netlify (Recommended)
Railway is optimized for backend services. For the React frontend, consider:
- **Vercel**: Connect GitHub repo, set root to `frontend`, add `REACT_APP_API_URL`
- **Netlify**: Similar setup with build command `npm run build` and publish directory `build`

## Database Migration

After deploying backend with PostgreSQL:

1. Railway's PostgreSQL addon sets `DATABASE_URL` automatically
2. The app creates tables automatically on startup (see `backend/main.py` startup event)
3. To create an admin user, use Railway's shell:

```bash
# In Railway service → "Shell" tab
python -c "
from backend.database import SessionLocal
from backend.models import User
from backend.services.auth_service import get_password_hash
db = SessionLocal()
admin = User(email='admin@school.edu', name='Admin', role='admin', hashed_password=get_password_hash('your_password'))
db.add(admin)
db.commit()
"
```

## Verify Deployment

### Backend Health Check
```bash
curl https://<your-backend>.up.railway.app/
```
Expected response:
```json
{
  "message": "Mustian Face MVP API is running",
  "docs": "/docs",
  ...
}
```

### API Documentation
Visit: `https://<your-backend>.up.railway.app/docs`

## Important Notes for Railway

### Port Configuration
- ✅ Backend configured to use `$PORT` environment variable (see `backend/main.py`)
- Railway automatically injects the PORT variable

### Database
- ✅ PostgreSQL supported via `psycopg2-binary` in requirements.txt
- ✅ Database URL automatically handled via `DATABASE_URL` env var
- ✅ Connection args handle both SQLite (dev) and PostgreSQL (prod)

### File Uploads
- Face images upload to `uploads/faces` directory
- **Warning**: Railway uses ephemeral filesystem. Uploads may be lost on restart.
- **Solution**: Use Railway's volumes or cloud storage (AWS S3, Cloudinary) for production

### Docker Build Context
- Backend Dockerfile is at `backend/Dockerfile`
- `railway.json` configures the build to use this Dockerfile
- Ensure Dockerfile is in the correct path relative to repository root

## Troubleshooting

### Build Fails
- Check build logs in Railway dashboard
- Ensure all system dependencies are in `backend/Dockerfile`
- Face recognition libraries need: `cmake`, `libopenblas-dev`, etc. (already included)

### Database Connection Error
- Verify PostgreSQL addon is added to project
- Check `DATABASE_URL` is automatically set (Railway does this)
- Review logs: `railway logs`

### CORS Errors
- Update `backend/main.py` CORS middleware to allow frontend domain:
```python
allow_origins=[
    "https://your-frontend.vercel.app",
    "https://your-frontend.up.railway.app"
]
```

### Port Already in Use
- Ensure `main.py` uses `os.environ.get("PORT", 8000)` (already configured)

## Cost Considerations
- Railway charges for usage (compute + database)
- PostgreSQL addon has separate pricing
- Monitor usage in Railway dashboard

## Next Steps After Deployment
1. Update CORS settings with actual frontend URL
2. Set up file storage for production (S3/Cloudinary)
3. Configure custom domain (optional)
4. Set up monitoring and alerts
5. Review security settings (firewall, secrets management)