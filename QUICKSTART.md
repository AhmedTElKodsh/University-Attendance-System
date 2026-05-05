# Mustian Face MVP - Quick Start Guide

## 🚀 Fastest Way to Get Running (5 minutes)

**Simple face recognition (imagehash) - COMMITTED APPROACH**
- ✅ Fast development and deployment
- ✅ Works on all platforms (no compilation needed)
- ✅ Medium accuracy (~80%) - good enough for supervised classroom
- ✅ Installation takes seconds, not minutes
- ✅ No dlib dependency

#### Step 1: Install Dependencies
```bash
# Uses lightweight deps (no dlib)
pip install -r backend/requirements.txt
```

#### Step 2: Configure Environment
```bash
# backend/.env already has USE_SIMPLE_FACE_RECOGNITION=True
# No changes needed - simple mode is default
```

#### Step 3: Run Backend
```bash
cd backend
python seed.py  # Creates admin user
uvicorn main:app --reload
```

#### Step 4: Run Frontend
```bash
cd frontend
npm install
npm start
```

#### Step 5: Login
- URL: http://localhost:3000
- Email: `admin@mustian.edu`
- Password: `admin123` (change this!)

---

## 🐳 Docker Quick Start (Easiest)

```bash
# Build and run everything (simple mode enabled by default)
docker-compose up --build

# Access:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 📝 Initial Setup Checklist

After starting the application:

### 1. Login as Admin
- Email: `admin@mustian.edu`
- Password: `admin123`

### 2. Create a Doctor
1. Go to "Doctor Management"
2. Click "Add Doctor"
3. Fill in details
4. Note: You'll need to create a User account first with role="doctor"

### 3. Create Students
1. Go to "Student Management"
2. Click "Add Student"
3. Fill in student details

### 4. Register Student Faces
1. Go to "Student Management"
2. Click on a student
3. Upload their photo
4. System will extract face hash

### 5. Create Courses and CRNs
1. Go to "Course Management"
2. Create a course
3. Create CRN (Course Reference Number) for the course
4. Assign doctor to CRN

### 6. Enroll Students
1. Go to "Course Management"
2. Select a course
3. Enroll students in the CRN

### 7. Schedule Lectures
1. Go to "Lecture Management"
2. Create lecture for a CRN
3. Set date, time, and attendance window

### 8. Test Attendance
1. Open attendance screen: http://localhost:3000/attendance/{crn_id}
2. Students can mark attendance using webcam
3. Doctor can view attendance in their dashboard

---

## 🔧 Troubleshooting

### "Could not validate credentials"
**Solution:** Check if admin user was created:
```bash
cd backend
python seed.py
```

### "Face not recognized"
**Solutions:**
1. Ensure student face is registered
2. Check lighting (face should be well-lit)
3. Try re-registering the face

### Docker build fails
**Solution:** Simple mode has no special deps - should work on all platforms.

### Camera not working
**Solutions:**
1. Check browser permissions (allow camera access)
2. Use HTTPS (required for camera on some browsers)
3. Try different browser (Chrome works best)

---

## 🔐 Security Notes

### Before Production:
1. ✅ Change admin password
2. ✅ Set strong SECRET_KEY in .env
3. ✅ Configure specific CORS origins (not "*")
4. ✅ Use PostgreSQL instead of SQLite
5. ✅ Enable HTTPS
6. ✅ Add rate limiting
7. ✅ Review all default credentials

---

## 📚 Next Steps

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
2. Read [README.md](README.md) for full documentation
3. Check [implementation-gap-analysis.md](_bmad-output/implementation-artifacts/implementation-gap-analysis.md) for detailed analysis

---

## 💡 Recommendation

**Simple face recognition (imagehash) is COMMITTED.**

- Get it working in 5 minutes
- Test with real users
- 80% accuracy sufficient for supervised classroom

**Why simple?**
- Teacher is present
- Students motivated to mark attendance correctly
- Manual override available
- Fast deployment, no headaches

**Start simple, iterate fast!** 🚀
