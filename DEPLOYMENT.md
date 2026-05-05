# Production Deployment Guide - Mustian Face MVP

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest` for backend, `npm test` for frontend)
- [ ] Environment variables configured securely
- [ ] Secrets (SECRET_KEY) changed from defaults
- [ ] Database migrated to production-ready solution (PostgreSQL recommended)
- [ ] HTTPS configured
- [ ] Backup strategy implemented

## Production Environment Setup

### 1. Server Requirements
- **OS**: Ubuntu 22.04 LTS or newer
- **RAM**: Minimum 4GB (8GB+ recommended for face recognition workloads)
- **CPU**: 4+ cores (for concurrent face processing)
- **Storage**: 20GB+ SSD
- **Docker**: Docker Engine 24.0+ and Docker Compose V2

### 2. Environment Configuration

#### Backend (.env file)
Create `backend/.env` from the example:
```bash
cp backend/.env.example backend/.env
```

Update with production values:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/mustian_prod
SECRET_KEY=your-very-secure-random-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FACE_CONFIDENCE_THRESHOLD=0.6
ATTENDANCE_WINDOW_MINUTES=30
UPLOAD_DIR=uploads/faces
```

Generate secure SECRET_KEY:
```bash
openssl rand -hex 32
```

#### Frontend (Environment Variable)
For production, set `REACT_APP_API_URL` to your backend domain:
```bash
export REACT_APP_API_URL=https://api.yourdomain.com
```

### 3. Database Setup (Production)

Switch from SQLite to PostgreSQL:

1. Install PostgreSQL:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Create database and user:
```bash
sudo -u postgres psql
CREATE DATABASE mustian_prod;
CREATE USER mustian_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE mustian_prod TO mustian_user;
\q
```

3. Update backend requirements.txt to include PostgreSQL driver:
```
psycopg2-binary==2.9.9
```

4. Update `backend/database.py` to use PostgreSQL URL format.

### 4. Docker Production Configuration

Update `docker-compose.yml` for production:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mustian-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/data:/app/data  # Persistent storage
    environment:
      - DATABASE_URL=postgresql://mustian_user:strong_password@db:5432/mustian_prod
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - FACE_CONFIDENCE_THRESHOLD=0.6
      - ATTENDANCE_WINDOW_MINUTES=30
    restart: always
    networks:
      - mustian-network
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    container_name: mustian-db
    environment:
      - POSTGRES_USER=mustian_user
      - POSTGRES_PASSWORD=strong_password
      - POSTGRES_DB=mustian_prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    networks:
      - mustian-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        REACT_APP_API_URL: https://api.yourdomain.com
    container_name: mustian-frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: always
    networks:
      - mustian-network

networks:
  mustian-network:
    driver: bridge

volumes:
  postgres_data:
```

### 5. HTTPS/SSL Configuration

Use Let's Encrypt with Nginx for HTTPS:

1. Update frontend nginx config to include SSL:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

2. Obtain SSL certificates:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 6. Deployment Steps

1. Clone repository on production server:
```bash
git clone <your-repo-url> /opt/mustian
cd /opt/mustian
```

2. Create and configure .env files:
```bash
cp backend/.env.example backend/.env
nano backend/.env  # Update with production values
```

3. Build and start containers:
```bash
docker-compose up -d --build
```

4. Run database migrations (if applicable):
```bash
docker-compose exec backend python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

5. Create initial admin user:
```bash
docker-compose exec backend python -c "
from database import SessionLocal
from models import User
from services.auth_service import get_password_hash
db = SessionLocal()
admin = User(email='admin@yourdomain.com', name='Admin', role='admin', hashed_password=get_password_hash('secure_password'))
db.add(admin)
db.commit()
"
```

### 7. Monitoring and Maintenance

- **Logs**: `docker-compose logs -f`
- **Backup database**: 
  ```bash
  docker-compose exec db pg_dump -U mustian_user mustian_prod > backup_$(date +%Y%m%d).sql
  ```
- **Update application**:
  ```bash
  git pull
  docker-compose up -d --build
  ```

### 8. Security Considerations

- [ ] Change all default passwords
- [ ] Restrict database access to internal network only
- [ ] Set up firewall (UFW):
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] Enable automatic security updates
- [ ] Regularly update Docker images

### 9. Scaling Considerations

For high load:
- Use managed PostgreSQL (AWS RDS, DigitalOcean Managed DB)
- Add load balancer for frontend
- Increase backend workers: Update uvicorn command to `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
- Consider using Redis for caching and session storage

## Deploy to Render (Easiest - Recommended)

Render supports Docker-based deployments with managed PostgreSQL.

### Option A: One-Click Blueprint (render.yaml)

1. Push code to GitHub/GitLab repo
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your repo
5. Render auto-detects `render.yaml` and creates all services

**Services created:**
- `mustian-backend` — FastAPI backend (Docker)
- `mustian-frontend` — React frontend (Docker + nginx)
- `mustian-db` — Managed PostgreSQL

**URLs after deploy:**
- Frontend: `https://mustian-frontend.onrender.com`
- Backend API: `https://mustian-backend.onrender.com`
- API Docs: `https://mustian-backend.onrender.com/docs`

### Option B: Manual Setup (No render.yaml)

**1. Create PostgreSQL Database:**
- Dashboard → **New +** → **PostgreSQL**
- Name: `mustian-db`
- User: `mustian_user`
- Plan: Free (or paid for production)

**2. Create Backend Service:**
- Dashboard → **New +** → **Web Service**
- Connect repo
- Runtime: **Docker**
- Instance: Free (or paid)
- Environment Variables:
  ```
  DATABASE_URL=[from database connection string]
  SECRET_KEY=[generate a secure key]
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  FACE_CONFIDENCE_THRESHOLD=0.6
  USE_SIMPLE_FACE_RECOGNITION=True
  ATTENDANCE_WINDOW_MINUTES=30
  CORS_ORIGINS=["https://mustian-frontend.onrender.com"]
  ```

**3. Create Frontend Service:**
- Dashboard → **New +** → **Web Service**
- Connect repo
- Runtime: **Docker**
- Instance: Free
- Build Command: `docker build --build-arg REACT_APP_API_URL=https://mustian-backend.onrender.com -t mustian-frontend .`
- Environment Variables:
  ```
  REACT_APP_API_URL=https://mustian-backend.onrender.com
  ```

### Render-Specific Notes

- **Free tier spins down** after 15 min inactivity — cold start ~30s
- **Seed script** runs on startup, creates admin user automatically
- **Admin credentials** after first deploy:
  - Email: `admin@mustian.edu`
  - Password: `admin123` (change immediately!)
- **Custom domain**: Settings → Custom Domain
- **HTTPS**: Auto-provisioned by Render

### Update CORS After Deploy

Once you know your frontend URL, update backend env var:
```
CORS_ORIGINS=["https://your-frontend.onrender.com"]
```

Then **Manual Deploy** in backend service dashboard.

---

## Troubleshooting

- **Containers won't start**: Check logs with `docker-compose logs`
- **Database connection issues**: Verify DATABASE_URL and network connectivity
- **Face recognition errors**: Ensure all system dependencies are installed in Docker image
- **CORS issues**: Update CORS middleware in `backend/main.py` to allow production domains