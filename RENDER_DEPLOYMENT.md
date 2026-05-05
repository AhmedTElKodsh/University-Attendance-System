# Render Deployment Guide

## Overview
This guide explains how to deploy the University Attendance System to Render.

## Fixed Issues
- ✅ Updated Dockerfiles to use repository root as build context
- ✅ Fixed path references in backend/Dockerfile and frontend/Dockerfile
- ✅ Updated docker-compose.yml to match new build context

## Deployment Steps

### 1. Backend Service (Web Service)

**Service Configuration:**
- **Name**: `university-attendance-backend`
- **Environment**: `Docker`
- **Region**: Choose closest to your users
- **Branch**: `master` (or your main branch)
- **Root Directory**: Leave empty (uses repo root)
- **Dockerfile Path**: `backend/Dockerfile`

**Environment Variables:**
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=<generate with: openssl rand -hex 32>
ENVIRONMENT=production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FACE_CONFIDENCE_THRESHOLD=0.7
USE_SIMPLE_FACE_RECOGNITION=True
ATTENDANCE_WINDOW_MINUTES=30
CORS_ORIGINS=https://your-frontend-url.onrender.com
```

**Important Notes:**
- Use PostgreSQL database (add from Render dashboard)
- Generate a secure SECRET_KEY: `openssl rand -hex 32`
- Set CORS_ORIGINS to your frontend URL
- The build context is the repository root, so paths in Dockerfile use `backend/` prefix

### 2. Frontend Service (Static Site or Web Service)

**Option A: Static Site (Recommended)**
- **Name**: `university-attendance-frontend`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/build`

**Option B: Docker Web Service**
- **Name**: `university-attendance-frontend`
- **Environment**: `Docker`
- **Dockerfile Path**: `frontend/Dockerfile`
- **Build Arguments**:
  ```
  REACT_APP_API_URL=https://your-backend-url.onrender.com
  ```

### 3. Database (PostgreSQL)

**Database Configuration:**
- **Name**: `university-attendance-db`
- **Database**: `attendance_db`
- **User**: `attendance_user`
- **Region**: Same as backend service

**After Creation:**
- Copy the Internal Database URL
- Add it to backend service as `DATABASE_URL` environment variable

## Build Context Explanation

The Dockerfiles now assume the build context is the **repository root**:

**Backend Dockerfile:**
```dockerfile
COPY backend/requirements.txt .
COPY backend/ .
```

**Frontend Dockerfile:**
```dockerfile
COPY frontend/package*.json ./
COPY frontend/ .
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
```

**Docker Compose (for local development):**
```yaml
backend:
  build:
    context: .              # Repository root
    dockerfile: backend/Dockerfile
```

This configuration works for:
- ✅ Render deployment (uses repo root as context)
- ✅ Local Docker Compose (explicitly sets context to root)
- ✅ Manual Docker builds: `docker build -f backend/Dockerfile .`

## Verification

After deployment, verify:

1. **Backend Health Check:**
   ```bash
   curl https://your-backend-url.onrender.com/docs
   ```
   Should return FastAPI documentation page

2. **Frontend Access:**
   Visit `https://your-frontend-url.onrender.com`
   Should load the login page

3. **Database Connection:**
   Check backend logs for successful database connection

## Troubleshooting

### Build Fails with "requirements.txt not found"
- ✅ **Fixed**: Dockerfiles now use correct paths with `backend/` prefix
- Verify Dockerfile Path is set to `backend/Dockerfile` (not just `Dockerfile`)
- Ensure Root Directory is empty (uses repo root)

### CORS Errors
- Add frontend URL to `CORS_ORIGINS` environment variable in backend
- Format: `https://your-frontend-url.onrender.com` (no trailing slash)

### Database Connection Errors
- Verify `DATABASE_URL` format: `postgresql://user:password@host:5432/dbname`
- Use Internal Database URL from Render dashboard
- Check database service is in same region as backend

### Frontend Can't Connect to Backend
- Set `REACT_APP_API_URL` build argument for frontend
- Use full backend URL: `https://your-backend-url.onrender.com`
- Check CORS configuration in backend

## Post-Deployment Tasks

1. **Change Default Admin Password:**
   - Login with: `admin@mustian.edu.eg` / `admin123`
   - Immediately change password in admin dashboard

2. **Monitor Logs:**
   - Check backend logs for errors
   - Monitor database connection pool
   - Watch for rate limiting triggers

3. **Set Up Backups:**
   - Enable automatic backups in Render dashboard
   - Schedule regular database backups

4. **Performance Monitoring:**
   - Monitor response times
   - Check memory usage
   - Watch for face recognition performance

## Security Checklist

- ✅ SECRET_KEY is randomly generated (not default)
- ✅ ENVIRONMENT=production
- ✅ PostgreSQL database (not SQLite)
- ✅ CORS_ORIGINS configured
- ✅ Admin password changed from default
- ✅ Rate limiting enabled (20 req/min for auth, 10 req/min for attendance)
- ✅ File upload validation (max 5MB, image types only)
- ✅ Face recognition threshold = 0.7

## Cost Optimization

**Free Tier:**
- Backend: Free tier available (spins down after inactivity)
- Frontend: Free for static sites
- Database: Free tier available (limited storage)

**Paid Tier Recommendations:**
- Backend: $7/month (always on, better performance)
- Database: $7/month (more storage, better performance)
- Frontend: Free (static site)

## Support

For issues:
1. Check Render build logs
2. Review backend application logs
3. Verify environment variables
4. Check database connectivity
5. Review CORS configuration

## Additional Resources

- [Render Docker Deployment](https://render.com/docs/docker)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/databases)
