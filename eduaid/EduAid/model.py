from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ---------- User for authentication ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'ngo'

    # For teacher-specific info
    teacher_name = db.Column(db.String(150))
    teacher_identifier = db.Column(db.String(2), index=True)  # exactly 2 digits (e.g. '01')

    # For linking to student profile
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    csv_row_index = db.Column(db.Integer) 
    # New fields
    student_identifier = db.Column(db.String(4), index=True)  # exactly 4 digits (e.g. '0101')
    student_name = db.Column(db.String(150))

    # Automatically extracted from student_identifier first two digits:
    teacher_identifier = db.Column(db.String(2), index=True)  # matches Teacher.teacher_id

    # Academic fields
    attendance_percent = db.Column(db.Integer)
    absences = db.Column(db.Integer)
    courses_enrolled = db.Column(db.Text)
    grades = db.Column(db.Text)

    # All your other existing fields…
    marital_status = db.Column(db.Integer)
    application_mode = db.Column(db.Integer)
    daytime_evening = db.Column(db.Integer)
    prev_qualification = db.Column(db.Integer)
    mother_qualification = db.Column(db.Integer)
    father_qualification = db.Column(db.Integer)
    mother_occupation = db.Column(db.Integer)
    father_occupation = db.Column(db.Integer)
    displaced = db.Column(db.Integer)
    special_needs = db.Column(db.Integer)
    debtor = db.Column(db.Integer)
    fees_up_to_date = db.Column(db.Integer)
    scholarship = db.Column(db.Integer)
    age_enrollment = db.Column(db.Integer)
    sem1_enrolled = db.Column(db.Integer)
    sem1_approved = db.Column(db.Integer)
    sem1_grade = db.Column(db.Float)
    sem2_enrolled = db.Column(db.Integer)
    sem2_approved = db.Column(db.Integer)
    sem2_grade = db.Column(db.Float)
    dropout_prediction = db.Column(db.Float, default=0.0)


# ---------- Teacher Table ----------
class Teacher(db.Model):
    teacher_id = db.Column(db.String(2), primary_key=True)  # exactly 2 digits
    teacher_name = db.Column(db.String(150), nullable=False)

    # Relationship to Student (below)
    students = db.relationship("Student", backref="teacher", lazy=True)


# ---------- Student Table ----------
class Student(db.Model):
    student_id = db.Column(db.String(4), primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    teacher_identifier = db.Column(db.String(2))
    teacher_id = db.Column(db.String(2), db.ForeignKey("teacher.teacher_id"), nullable=False)

# Add this to your model.py file

class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    contact_info = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationship to contact requests
    contact_requests = db.relationship("ContactRequest", backref="ngo", lazy=True)

class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ngo_id = db.Column(db.Integer, db.ForeignKey("ngo.id"))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to student
    student = db.relationship("User", backref="contact_requests")
