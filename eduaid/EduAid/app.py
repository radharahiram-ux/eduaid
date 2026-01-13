from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import joblib
import json
from flask import jsonify
import datetime
import random
import pandas as pd
from model import db, User, StudentProfile, Teacher, Student, NGO, ContactRequest
from data import USERS
import random
from sqlalchemy import func, text

import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret123")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://", 1)

db.init_app(app)
login_manager = LoginManager(app)

try:
    model = joblib.load("dropout_model.pkl")
except Exception:
    model = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def preload_data():
    try:
        df = pd.read_csv("student_data.csv")
        app.config["STUDENT_CSV"] = df
    except Exception:
        app.config["STUDENT_CSV"] = pd.DataFrame()

def get_unassigned_csv_index():
    df = app.config.get("STUDENT_CSV")
    if df is None or df.empty:
        return None
    assigned = {
        idx for (idx,) in db.session.query(StudentProfile.csv_row_index).filter(StudentProfile.csv_row_index.isnot(None)).all()
    }
    for i in range(len(df)):
        if i not in assigned:
            return i
    return None

def compute_dropout_probability_from_row(row):
    try:
        features = [[
            int(row["Marital status"]),
            int(row["Application mode"]),
            int(row["Daytime/evening attendance"]),
            int(row["Previous qualification"]),
            int(row["Mother's qualification"]),
            int(row["Father's qualification"]),
            int(row["Mother's occupation"]),
            int(row["Father's occupation"]),
            int(row["Displaced"]),
            int(row["Educational special needs"]),
            int(row["Debtor"]),
            int(row["Tuition fees up to date"]),
            int(row["Scholarship holder"]),
            int(row["Age at enrollment"]),
            int(row["Curricular units 1st sem (enrolled)"]),
            int(row["Curricular units 1st sem (approved)"]),
            float(row["Curricular units 1st sem (grade)"]),
            int(row["Curricular units 2nd sem (enrolled)"]),
            int(row["Curricular units 2nd sem (approved)"]),
            float(row["Curricular units 2nd sem (grade)"]),
        ]]
        if model:
            try:
                return float(model.predict_proba(features)[0][1] * 100)
            except Exception:
                pass
    except Exception:
        pass

    try:
        label = str(row.get("Target", "")).strip().lower()
        return 80.0 if label == "dropout" else 20.0
    except Exception:
        return random.uniform(10, 90)

def compute_gpa_from_sem_grades(sem1_grade, sem2_grade):
    try:
        avg20 = ((sem1_grade or 0.0) + (sem2_grade or 0.0)) / 2.0
        return round(max(0.0, min(10.0, avg20 / 2.0)), 1)
    except Exception:
        return 7.0

def ensure_sqlite_columns():
    try:
        # Ensure columns on user table
        result = db.session.execute(text("PRAGMA table_info('user')"))
        user_cols = {row[1] for row in result}
        if 'teacher_name' not in user_cols:
            db.session.execute(text("ALTER TABLE user ADD COLUMN teacher_name VARCHAR(150)"))
        if 'teacher_identifier' not in user_cols:
            db.session.execute(text("ALTER TABLE user ADD COLUMN teacher_identifier VARCHAR(10)"))

        # Ensure columns on student_profile table
        result_sp = db.session.execute(text("PRAGMA table_info('student_profile')"))
        sp_cols = {row[1] for row in result_sp}
        if 'teacher_identifier' not in sp_cols:
            db.session.execute(text("ALTER TABLE student_profile ADD COLUMN teacher_identifier VARCHAR(10)"))

        db.session.commit()
    except Exception:
        db.session.rollback()

def validate_teacher_id(tid: str) -> bool:
    return bool(tid) and len(tid) == 2 and tid.isdigit()

def validate_student_id(sid: str) -> bool:
    return bool(sid) and len(sid) == 4 and sid.isdigit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]  # student, teacher, ngo

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.", "danger")
            return render_template("signup.html", error="Email already registered")

        # Optional fields
        student_name = request.form.get("student_name")
        student_id = request.form.get("student_id")
        teacher_name = request.form.get("teacher_name")
        teacher_id = request.form.get("teacher_id")
        ngo_name = request.form.get("ngo_name")
        ngo_description = request.form.get("ngo_description")
        ngo_contact = request.form.get("ngo_contact")
        

        # Validate role-specific fields
        if role == "teacher":
            if not teacher_id or not validate_teacher_id(teacher_id):
                flash("Teacher ID must be exactly 2 digits.", "danger")
                return render_template("signup.html", error="Invalid Teacher ID")
            if not teacher_name:
                flash("Teacher name is required.", "danger")
                return render_template("signup.html", error="Teacher name is required")
            # Check if teacher ID already exists
            if Teacher.query.get(teacher_id):
                flash("Teacher ID already exists.", "danger")
                return render_template("signup.html", error="Teacher ID already exists")
                
        if role == "student":
            if student_id and not validate_student_id(student_id):
                flash("Student ID must be exactly 4 digits.", "danger")
                return render_template("signup.html", error="Invalid Student ID")
            # If student ID provided, check if teacher exists for the prefix
            if student_id:
                inferred_tid = student_id[:2]
                teacher = Teacher.query.get(inferred_tid)
                if not teacher:
                    flash("No teacher exists for the given Student ID prefix.", "danger")
                    return render_template("signup.html", error="No teacher for this Student ID prefix")
            # Check if student ID already exists
            if student_id and Student.query.get(student_id):
                flash("Student ID already exists.", "danger")
                return render_template("signup.html", error="Student ID already exists")
        elif role == "ngo":
            if not ngo_name:
                flash("Organization name is required.", "danger")
                return render_template("signup.html", error="Organization name is required")
        
        # Create user
        user = User(email=email, password=password, role=role)
        
        if role == "teacher":
            user.teacher_name = teacher_name
            user.teacher_identifier = teacher_id
            
            # Create teacher record
            teacher = Teacher(teacher_id=teacher_id, teacher_name=teacher_name)
            db.session.add(teacher)
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing

        if role == "ngo":
            ngo = NGO(
                user_id=user.id,
                name=ngo_name,
                email=email,
                description=ngo_description,
                contact_info=ngo_contact,
                is_approved=True  # Auto-approve for now, can change to False for admin approval
            )
            db.session.add(ngo)
        
        db.session.add(user)
        db.session.flush() 

        if role == "student":
            # Create student record if ID provided
            if student_id:
                student = Student(student_id=student_id, student_name=student_name or email, teacher_id=student_id[:2])
                db.session.add(student)
            
            # Create student profile
            profile_kwargs = {}
            if student_name:
                profile_kwargs["student_name"] = student_name
            if student_id:
                profile_kwargs["student_identifier"] = student_id
                profile_kwargs["teacher_identifier"] = student_id[:2]

            df = app.config.get("STUDENT_CSV")
            idx = get_unassigned_csv_index()
            if df is not None and not df.empty and idx is not None:
                row = df.iloc[idx]
                prob = compute_dropout_probability_from_row(row)
                profile = StudentProfile(
                    user_id=user.id,
                    csv_row_index=idx,
                    **profile_kwargs,
                    marital_status=int(row["Marital status"]),
                    application_mode=int(row["Application mode"]),
                    daytime_evening=int(row["Daytime/evening attendance"]),
                    prev_qualification=int(row["Previous qualification"]),
                    mother_qualification=int(row["Mother's qualification"]),
                    father_qualification=int(row["Father's qualification"]),
                    mother_occupation=int(row["Mother's occupation"]),
                    father_occupation=int(row["Father's occupation"]),
                    displaced=int(row["Displaced"]),
                    special_needs=int(row["Educational special needs"]),
                    debtor=int(row["Debtor"]),
                    fees_up_to_date=int(row["Tuition fees up to date"]),
                    scholarship=int(row["Scholarship holder"]),
                    age_enrollment=int(row["Age at enrollment"]),
                    sem1_enrolled=int(row["Curricular units 1st sem (enrolled)"]),
                    sem1_approved=int(row["Curricular units 1st sem (approved)"]),
                    sem1_grade=float(row["Curricular units 1st sem (grade)"]),
                    sem2_enrolled=int(row["Curricular units 2nd sem (enrolled)"]),
                    sem2_approved=int(row["Curricular units 2nd sem (approved)"]),
                    sem2_grade=float(row["Curricular units 2nd sem (grade)"]),
                    dropout_prediction=float(prob),
                )
                db.session.add(profile)
            else:
                profile = StudentProfile(
                    user_id=user.id,
                    **profile_kwargs,
                    marital_status=random.randint(1,3),
                    application_mode=random.randint(1, 17),
                    daytime_evening=random.randint(1, 2),
                    prev_qualification=random.randint(1, 6),
                    mother_qualification=random.randint(1, 6),
                    father_qualification=random.randint(1, 6),
                    mother_occupation=random.randint(1, 6),
                    father_occupation=random.randint(1, 6),
                    displaced=random.randint(0, 1),
                    special_needs=random.randint(0, 1),
                    debtor=random.randint(0, 1),
                    fees_up_to_date=random.randint(0, 1),
                    scholarship=random.randint(0, 1),
                    age_enrollment=random.randint(17, 30),
                    sem1_enrolled=random.randint(4, 8),
                    sem1_approved=random.randint(2, 8),
                    sem1_grade=random.uniform(8, 16),
                    sem2_enrolled=random.randint(4, 8),
                    sem2_approved=random.randint(2, 8),
                    sem2_grade=random.uniform(8, 16),
                    dropout_prediction=random.uniform(0, 100)
                )
                db.session.add(profile)

        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", error="Email and password are required")
        
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user)
            if user.role == "student":
                return redirect(url_for("student_dashboard"))
            elif user.role == "teacher":
                # Set teacher session
                session["teacher_id"] = user.teacher_identifier
                session["teacher_name"] = user.teacher_name
                return redirect(url_for("teacher_dashboard"))
            elif user.role == "ngo":
                return redirect(url_for("ngo_dashboard"))
        else:
            # Check if it's a persona login
            persona_entry = USERS.get(email)
            if persona_entry and persona_entry.get("password") == password:
                # Create user for persona
                user = User(email=email, password=password, role="student")
                db.session.add(user)
                db.session.flush()

                # Create profile for persona
                persona = persona_entry["data"]
                sem1_enrolled = random.randint(4, 8)
                sem1_approved = max(0, min(sem1_enrolled, int(round((persona["gpa"]/10) * sem1_enrolled))))
                sem1_grade = float(persona["gpa"]) + random.uniform(-1.0, 1.0)
                sem2_enrolled = random.randint(4, 8)
                sem2_approved = max(0, min(sem2_enrolled, int(round((persona["gpa"]/10) * sem2_enrolled))))
                sem2_grade = float(persona["gpa"]) + random.uniform(-1.0, 1.0)
                
                features = [[
                    1, 1, 1, 1,
                    2, 2, 2, 2,
                    0, 0, 0, 1,
                    0, 19,
                    sem1_enrolled,
                    sem1_approved,
                    sem1_grade,
                    sem2_enrolled,
                    sem2_approved,
                    sem2_grade,
                ]]
                
                try:
                    prob = float(model.predict_proba(features)[0][1] * 100) if model else random.uniform(0, 100)
                except Exception:
                    prob = random.uniform(0, 100)
                    
                profile = StudentProfile(
                    user_id=user.id,
                    marital_status=features[0][0],
                    application_mode=features[0][1],
                    daytime_evening=features[0][2],
                    prev_qualification=features[0][3],
                    mother_qualification=features[0][4],
                    father_qualification=features[0][5],
                    mother_occupation=features[0][6],
                    father_occupation=features[0][7],
                    displaced=features[0][8],
                    special_needs=features[0][9],
                    debtor=features[0][10],
                    fees_up_to_date=features[0][11],
                    scholarship=features[0][12],
                    age_enrollment=features[0][13],
                    sem1_enrolled=features[0][14],
                    sem1_approved=features[0][15],
                    sem1_grade=features[0][16],
                    sem2_enrolled=features[0][17],
                    sem2_approved=features[0][18],
                    sem2_grade=features[0][19],
                    dropout_prediction=prob,
                )
                db.session.add(profile)
                db.session.commit()

                login_user(user)
                return redirect(url_for("student_dashboard"))

            flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("login"))

# Add this import at the top
import random

# Update the student_dashboard route
@app.route("/student")
@login_required
def student_dashboard():
    # Get the student's profile from database
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get the student's real name from the database
    student_name = None
    student_id = None
    
    if profile:
        student_name = profile.student_name
        student_id = profile.student_identifier
    
    # Fallback to email if name not available
    if not student_name:
        student_name = current_user.email
    
    # Fallback to user ID if student ID not available
    if not student_id:
        student_id = f"{current_user.id:08d}"
    
    # Get approved NGOs from database
    ngos_from_db = NGO.query.filter_by(is_approved=True).all()
    
    # Format NGOs for template
    ngos_data = []
    for ngo in ngos_from_db:
        ngos_data.append({
            'id': ngo.id,
            'name': ngo.name,
            'desc': ngo.description or "Support organization for students",
            'cta': 'Contact'
        })
    
    # If no NGOs in DB, use sample data from personas
    if not ngos_data:
        persona_keys = list(USERS.keys())
        if persona_keys:
            chosen_key = random.choice(persona_keys)
            persona = USERS[chosen_key]["data"]
            ngos_data = persona.get("ngos", [])
    
    # Calculate GPA from semester grades
    gpa = 7.0  # Default GPA
    last_gpa = 6.8  # Default last semester GPA
    
    if profile:
        try:
            gpa = compute_gpa_from_sem_grades(profile.sem1_grade, profile.sem2_grade)
            last_gpa = max(0.0, gpa - random.uniform(0.2, 0.5))  # Simulate improvement
        except:
            pass
    
    # Calculate attendance based on risk level
    attendance_percent = 90
    absences = 2
    
    if profile and profile.dropout_prediction:
        if profile.dropout_prediction > 70:  # High risk
            attendance_percent = random.randint(75, 85)
            absences = random.randint(5, 8)
        elif profile.dropout_prediction > 50:  # Medium risk
            attendance_percent = random.randint(85, 92)
            absences = random.randint(3, 5)
        else:  # Low risk
            attendance_percent = random.randint(92, 98)
            absences = random.randint(1, 3)
    
    # Determine next exam based on current month
    import datetime
    now = datetime.datetime.now()
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    next_exam_subject = "Mathematics"
    next_exam_date = f"{months[(now.month) % 12]} {random.randint(10, 28)}, {now.year}"
    
    # Subjects for performance rows
    subjects = ["Mathematics", "Science", "English", "History", "Physics", 
                "Chemistry", "Biology", "Computer Science", "Geography", "Economics"]
    
    # Generate performance rows based on GPA
    performance_rows = []
    for i in range(4):
        subject = subjects[i] if i < len(subjects) else f"Subject {i+1}"
        
        # Convert GPA to letter grade
        if gpa >= 9.0:
            grade = "A+"
            feedback = "Excellent performance"
        elif gpa >= 8.0:
            grade = "A"
            feedback = "Very good work"
        elif gpa >= 7.0:
            grade = "B+"
            feedback = "Good effort"
        elif gpa >= 6.0:
            grade = "B"
            feedback = "Satisfactory"
        elif gpa >= 5.0:
            grade = "C+"
            feedback = "Needs improvement"
        else:
            grade = "C"
            feedback = "Requires attention"
        
        performance_rows.append({
            "subject": subject,
            "grade": grade,
            "feedback": feedback
        })
    
    # Generate attendance data based on attendance percentage
    attendance_rows = []
    current_month = now.month
    for i in range(3):
        month_idx = (current_month - i - 1) % 12
        month_name = months[month_idx]
        
        # Calculate days based on attendance percentage
        total_days = 22  # Approximate school days per month
        present_days = int(total_days * (attendance_percent / 100))
        absent_days = total_days - present_days - random.randint(0, 2)  # Some leave days
        leave_days = total_days - present_days - absent_days
        
        attendance_rows.append({
            "month": month_name,
            "present": present_days,
            "absent": absent_days,
            "leave": leave_days
        })
    
    # Reverse to show most recent first
    attendance_rows.reverse()
    
    # Determine number of available NGOs based on risk level
    ngo_available = len(ngos_data)
    if profile and profile.dropout_prediction:
        if profile.dropout_prediction > 70:  # High risk - more NGOs available
            ngo_available = min(5, len(ngos_data))
        elif profile.dropout_prediction > 50:  # Medium risk
            ngo_available = min(3, len(ngos_data))
        else:  # Low risk
            ngo_available = min(1, len(ngos_data))
    
    # Prepare context for template
    context = {
        "profile": profile,
        "student_name": student_name,
        "student_id": student_id,
        "gpa": round(gpa, 1),
        "last_gpa": round(last_gpa, 1),
        "attendance_percent": attendance_percent,
        "absences": absences,
        "next_exam_subject": next_exam_subject,
        "next_exam_date": next_exam_date,
        "ngo_available": ngo_available,
        "performance_rows": performance_rows,
        "attendance_rows": attendance_rows,
        "ngos": ngos_data[:ngo_available],  # Only show available NGOs based on risk
    }
    
    return render_template("student_dashboard.html", **context)

@app.route("/teacher")
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        flash("Access denied. Teacher role required.", "danger")
        return redirect(url_for("student_dashboard"))
    
    # Get teacher's students
    teacher_id = current_user.teacher_identifier
    students = StudentProfile.query.filter_by(teacher_identifier=teacher_id).all()
    
    # Calculate stats
    total_students = len(students)
    high_risk_count = len([s for s in students if s.dropout_prediction >= 70])
    
    # Calculate average GPA
    gpa_sum = 0
    for s in students:
        gpa_sum += compute_gpa_from_sem_grades(s.sem1_grade, s.sem2_grade)
    avg_gpa = round(gpa_sum / total_students, 2) if total_students > 0 else 0
    
    sort = request.args.get("sort", "risk_desc")
    min_risk = float(request.args.get("min_risk", 0) or 0)
    
    # Apply filters
    filtered_students = students
    if min_risk:
        filtered_students = [s for s in filtered_students if s.dropout_prediction >= min_risk]
    
    # Apply sorting
    if sort == "risk_asc":
        filtered_students.sort(key=lambda x: x.dropout_prediction)
    elif sort == "gpa_desc":
        filtered_students.sort(key=lambda x: compute_gpa_from_sem_grades(x.sem1_grade, x.sem2_grade), reverse=True)
    elif sort == "gpa_asc":
        filtered_students.sort(key=lambda x: compute_gpa_from_sem_grades(x.sem1_grade, x.sem2_grade))
    else:  # risk_desc (default)
        filtered_students.sort(key=lambda x: x.dropout_prediction, reverse=True)
    
    return render_template("teacher_dashboard.html", 
                         students=filtered_students, 
                         total_students=total_students, 
                         high_risk_count=high_risk_count, 
                         avg_gpa=avg_gpa, 
                         sort=sort, 
                         min_risk=min_risk)

@app.route("/student/<int:user_id>")
@login_required
def student_detail(user_id):
    if current_user.role != "teacher":
        flash("Access denied. Teacher role required.", "danger")
        return redirect(url_for("student_dashboard"))
        
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        flash("Student profile not found.", "warning")
        return redirect(url_for("teacher_dashboard"))
    
    # Verify the student belongs to the teacher
    if profile.teacher_identifier != current_user.teacher_identifier:
        flash("Access denied. You can only view your own students.", "danger")
        return redirect(url_for("teacher_dashboard"))
        
    gpa = compute_gpa_from_sem_grades(profile.sem1_grade, profile.sem2_grade)
    return render_template("student_detail.html", profile=profile, gpa=gpa)

@app.route("/ngo")
@login_required
def ngo_dashboard():
    if current_user.role != "ngo":
        flash("Access denied. NGO role required.", "danger")
        return redirect(url_for("login")) # Or student_dashboard
        
    # Find the NGO profile linked to the currently logged-in user
    ngo_profile = NGO.query.filter_by(user_id=current_user.id).first_or_404()
    

    student_requests = ContactRequest.query.filter_by(ngo_id=ngo_profile.id).order_by(ContactRequest.created_at.desc()).all()
    
    # Pass the list of requests to the template
    return render_template("ngo_dashboard.html",
                       contact_requests=student_requests,
                       students=[],  # or your actual list of supported students
                       ngo_name=ngo_profile.name)


@app.route("/contact_ngo", methods=["POST"])
@login_required
def contact_ngo():
    if current_user.role != "student":
        return jsonify({"success": False, "message": "Only students can contact NGOs"}), 403

    ngo_id = request.form.get("ngo_id")
    message = request.form.get("message", "").strip()

    if not ngo_id or not message:
        return jsonify({"success": False, "message": "Missing NGO or message"}), 400

    # Make sure NGO exists
    ngo = NGO.query.get(ngo_id)
    if not ngo:
        return jsonify({"success": False, "message": "NGO not found"}), 404

    # Create a new contact request
    contact = ContactRequest(
        ngo_id=ngo.id,
        student_id=current_user.id,
        message=message,
        status="pending"
    )
    db.session.add(contact)
    db.session.commit()

    return jsonify({"success": True, "message": "Your request has been sent to the NGO!"})

@app.route("/update_request_status", methods=["POST"])
@login_required
def update_request_status():
    if current_user.role != "ngo":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    req_id = request.form.get("request_id")
    status = request.form.get("status")

    contact_request = ContactRequest.query.get(req_id)
    if not contact_request:
        return jsonify({"success": False, "message": "Request not found"}), 404

    # Ensure NGO owns this request
    ngo_profile = NGO.query.filter_by(user_id=current_user.id).first()
    if contact_request.ngo_id != ngo_profile.id:
        return jsonify({"success": False, "message": "Not your request"}), 403

    # Update
    if status in ["approved", "rejected"]:
        contact_request.status = status
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid status"}), 400


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_sqlite_columns()
        preload_data()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
config