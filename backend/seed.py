"""
Seed script to create initial admin user and sample data
"""
from backend.database import User, SessionLocal, create_tables
from backend.routers.auth import pwd_context
from backend.database import UserRole, Status


def seed_admin():
    """Create initial admin user if not exists"""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@mustian.edu").first()
        if not admin:
            admin = User(
                name="System Admin",
                email="admin@mustian.edu",
                password=pwd_context.hash("admin123"),  # CHANGE IN PRODUCTION!
                role=UserRole.admin,
                status=Status.active
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created:")
            print("   Email: admin@mustian.edu")
            print("   Password: admin123")
            print("   ⚠️  CHANGE PASSWORD IN PRODUCTION!")
        else:
            print("ℹ️  Admin user already exists: admin@mustian.edu")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def seed_sample_data():
    """Create sample data for testing (optional)"""
    db = SessionLocal()
    
    try:
        from backend.database import Student, Doctor, Course
        
        # Check if sample data already exists
        if db.query(Student).count() > 0:
            print("ℹ️  Sample data already exists")
            return
        
        # Create sample student
        student = Student(
            student_id="2021001",
            full_name="Ahmed Mohamed",
            email="ahmed@student.mustian.edu",
            faculty="Engineering",
            department="Computer Science",
            academic_level="Year 3",
            program="Bachelor of Computer Science",
            status=Status.active
        )
        db.add(student)
        
        # Create sample doctor user
        doctor_user = User(
            name="Dr. Sarah Ahmed",
            email="sarah@mustian.edu",
            password=pwd_context.hash("doctor123"),
            role=UserRole.doctor,
            status=Status.active
        )
        db.add(doctor_user)
        db.flush()  # Get doctor_user.id
        
        # Create sample doctor profile
        doctor = Doctor(
            user_id=doctor_user.id,
            staff_id="D001",
            full_name="Dr. Sarah Ahmed",
            email="sarah@mustian.edu",
            faculty="Engineering",
            department="Computer Science",
            academic_title="Associate Professor",
            status=Status.active
        )
        db.add(doctor)
        
        # Create sample course
        course = Course(
            course_name="Introduction to Artificial Intelligence",
            course_code="CS301",
            description="Fundamentals of AI and machine learning",
            faculty="Engineering",
            department="Computer Science",
            academic_year="2025-2026",
            semester="Fall",
            status=Status.active
        )
        db.add(course)
        
        db.commit()
        print("✅ Sample data created:")
        print("   Student: ahmed@student.mustian.edu")
        print("   Doctor: sarah@mustian.edu / doctor123")
        print("   Course: CS301 - Introduction to AI")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database...")
    create_tables()
    seed_admin()
    
    # Uncomment to create sample data for testing
    # seed_sample_data()
    
    print("✅ Seeding complete!")
