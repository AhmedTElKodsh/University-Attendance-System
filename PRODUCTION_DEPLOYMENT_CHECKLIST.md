# Production Deployment Checklist

**Date**: 2026-05-06  
**Version**: 1.0.0  
**Status**: Ready for Production Deployment

---

## Pre-Deployment Checklist

### 1. ✅ Generate Secure SECRET_KEY

**On your production server**, generate a secure SECRET_KEY:

```bash
# Method 1: Using Python (recommended)
python -c "import secrets; print(secrets.token_hex(32))"

# Method 2: Using OpenSSL (if available)
openssl rand -hex 32
```

**Example output**: `e21d411b0e56f70cc3134ca9f4d585d9bad53ea44ed9539739d10ad6ab7c112a`

⚠️ **NEVER commit this key to git or share it publicly!**

---

### 2. ✅ Configure Production Environment

**On your production server**, create `backend/.env`:

```bash
cd /path/to/your/app
cp backend/.env.production.example backend/.env
nano backend/.env  # or use your preferred editor
```

**Update these critical values:**

```env
# REQUIRED: Set to production
ENVIRONMENT=production

# REQUIRED: Use the SECRET_KEY you generated in step 1
SECRET_KEY=e21d411b0e56f70cc3134ca9f4d585d9bad53ea44ed9539739d10ad6ab7c112a

# REQUIRED: PostgreSQL connection string
DATABASE_URL=postgresql://mustian_user:YOUR_DB_PASSWORD@localhost:5432/mustian_prod

# REQUIRED: Your production domain(s)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

---

### 3. ✅ Set Up PostgreSQL Database

**Install PostgreSQL** (if not already installed):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Create database and user:**

```bash
sudo -u postgres psql

-- In PostgreSQL prompt:
CREATE DATABASE mustian_prod;
CREATE USER mustian_user WITH PASSWORD 'YOUR_SECURE_DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE mustian_prod TO mustian_user;
\q
```

**Test connection:**

```bash
psql -h localhost -U mustian_user -d mustian_prod
# Enter password when prompted
# If successful, you'll see the PostgreSQL prompt
\q
```

---

### 4. ✅ Install Dependencies

**On your production server:**

```bash
cd /path/to/your/app/backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlalchemy, slowapi; print('✅ All packages installed')"
```

---

### 5. ✅ Initialize Database

**Create tables:**

```bash
cd /path/to/your/app/backend
source venv/bin/activate

# Run database initialization
python -c "from database import create_tables; create_tables(); print('✅ Tables created')"
```

**Create admin user:**

```bash
python seed.py
```

**Output should show:**
```
✅ Admin user created:
   Email: admin@mustian.edu
   Password: admin123
   ⚠️  CHANGE PASSWORD IN PRODUCTION!
```

---

### 6. ✅ Change Default Admin Password

**CRITICAL: Change the default admin password immediately!**

**Method 1: Using Python script**

Create `change_admin_password.py`:

```python
from database import SessionLocal, User
from routers.auth import pwd_context

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@mustian.edu").first()

if admin:
    new_password = input("Enter new admin password: ")
    admin.hashed_password = pwd_context.hash(new_password)
    db.commit()
    print("✅ Admin password changed successfully!")
else:
    print("❌ Admin user not found")

db.close()
```

Run it:
```bash
python change_admin_password.py
```

**Method 2: Using PostgreSQL directly**

```bash
# Generate password hash
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('YOUR_NEW_PASSWORD'))"

# Update in database
psql -h localhost -U mustian_user -d mustian_prod
UPDATE users SET hashed_password = 'PASTE_HASH_HERE' WHERE email = 'admin@mustian.edu';
\q
```

---

### 7. ✅ Configure CORS for Production Domain

**Update `backend/.env`:**

```env
# Replace with your actual production domain(s)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com", "https://api.yourdomain.com"]
```

**Verify CORS configuration:**

```bash
python -c "from config import settings; print('CORS Origins:', settings.CORS_ORIGINS)"
```

---

### 8. ✅ Test Application Startup

**Start the backend:**

```bash
cd /path/to/your/app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test endpoints:**

```bash
# In another terminal
curl http://localhost:8000/
# Should return: {"message": "Mustian Face MVP API is running", ...}

curl http://localhost:8000/docs
# Should return the API documentation page
```

**Stop the test server** (Ctrl+C)

---

### 9. ✅ Verify Rate Limiting

**Test login rate limiting:**

```bash
# Try 6 login attempts rapidly (should block after 5)
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' \
    -w "\nAttempt $i: %{http_code}\n"
  sleep 0.5
done
```

**Expected result:**
- Attempts 1-5: HTTP 401 (Unauthorized)
- Attempt 6: HTTP 429 (Too Many Requests)

✅ **Rate limiting is working!**

---

### 10. ✅ Set Up Production Server (Systemd Service)

**Create systemd service file:**

```bash
sudo nano /etc/systemd/system/mustian-backend.service
```

**Add this content:**

```ini
[Unit]
Description=Mustian Face MVP Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app/backend
Environment="PATH=/path/to/your/app/backend/venv/bin"
ExecStart=/path/to/your/app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable mustian-backend
sudo systemctl start mustian-backend
sudo systemctl status mustian-backend
```

---

### 11. ✅ Set Up Nginx Reverse Proxy

**Install Nginx:**

```bash
sudo apt install nginx
```

**Create Nginx configuration:**

```bash
sudo nano /etc/nginx/sites-available/mustian
```

**Add this content:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Frontend (if serving from same domain)
    location / {
        root /path/to/your/app/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

**Enable the site:**

```bash
sudo ln -s /etc/nginx/sites-available/mustian /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

---

### 12. ✅ Set Up SSL with Let's Encrypt

**Install Certbot:**

```bash
sudo apt install certbot python3-certbot-nginx
```

**Obtain SSL certificate:**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Test auto-renewal:**

```bash
sudo certbot renew --dry-run
```

---

### 13. ✅ Set Up Firewall

**Configure UFW:**

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
sudo ufw status
```

---

### 14. ✅ Set Up Monitoring and Logging

**View application logs:**

```bash
# Systemd service logs
sudo journalctl -u mustian-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**Set up log rotation:**

```bash
sudo nano /etc/logrotate.d/mustian
```

Add:
```
/var/log/mustian/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

---

### 15. ✅ Set Up Database Backups

**Create backup script:**

```bash
sudo nano /usr/local/bin/backup-mustian-db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mustian"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U mustian_user mustian_prod | gzip > $BACKUP_DIR/mustian_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "mustian_*.sql.gz" -mtime +30 -delete

echo "Backup completed: mustian_$DATE.sql.gz"
```

**Make executable and schedule:**

```bash
sudo chmod +x /usr/local/bin/backup-mustian-db.sh
sudo crontab -e
```

Add:
```
0 2 * * * /usr/local/bin/backup-mustian-db.sh
```

---

## Post-Deployment Verification

### ✅ Checklist

- [ ] Application starts without errors
- [ ] Can access API at https://yourdomain.com/api/
- [ ] API documentation accessible at https://yourdomain.com/api/docs
- [ ] Can login with new admin password
- [ ] Rate limiting is working (test with multiple requests)
- [ ] Database is PostgreSQL (not SQLite)
- [ ] CORS allows only production domains
- [ ] SSL certificate is valid
- [ ] Logs are being written
- [ ] Backups are running

### Test Commands

```bash
# 1. Check application is running
sudo systemctl status mustian-backend

# 2. Test API endpoint
curl https://yourdomain.com/api/

# 3. Test rate limiting
for i in {1..10}; do curl -I https://yourdomain.com/api/ 2>/dev/null | grep "HTTP/"; done

# 4. Check database connection
psql -h localhost -U mustian_user -d mustian_prod -c "SELECT COUNT(*) FROM users;"

# 5. Verify SSL
curl -I https://yourdomain.com/api/ | grep "HTTP/2 200"

# 6. Check logs
sudo journalctl -u mustian-backend --since "10 minutes ago"
```

---

## Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u mustian-backend -n 50

# Common issues:
# 1. SECRET_KEY not set or using default
# 2. Database connection failed
# 3. Port 8000 already in use
```

### Database connection errors

```bash
# Test PostgreSQL connection
psql -h localhost -U mustian_user -d mustian_prod

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL
```

### Rate limiting not working

```bash
# Check slowapi is installed
python -c "import slowapi; print('✅ slowapi installed')"

# Check logs for rate limit messages
sudo journalctl -u mustian-backend | grep "rate limit"
```

---

## Security Hardening (Optional but Recommended)

1. **Disable root SSH login**
2. **Set up fail2ban**
3. **Enable automatic security updates**
4. **Use a secrets manager for sensitive data**
5. **Set up intrusion detection (OSSEC, Wazuh)**
6. **Regular security audits**

---

## Rollback Plan

If deployment fails:

```bash
# Stop the service
sudo systemctl stop mustian-backend

# Restore database from backup
gunzip < /var/backups/mustian/mustian_YYYYMMDD_HHMMSS.sql.gz | psql -U mustian_user mustian_prod

# Revert to previous git commit
cd /path/to/your/app
git checkout <previous-commit-hash>

# Restart service
sudo systemctl start mustian-backend
```

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u mustian-backend -f`
- Review CODE_REVIEW_FIXES.md for known issues
- Check DEFERRED_WORK.md for planned improvements

---

**✅ Deployment checklist complete! Your application is production-ready.**
