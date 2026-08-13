from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'campusora-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campusora.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===== DATABASE MODELS (FIXED - Proper order with relationships) =====

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    roll_number = db.Column(db.String(20), unique=True)
    enrollment_number = db.Column(db.String(30), unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    admission_year = db.Column(db.Integer)

    # Relationship
    user = db.relationship('User', backref='student_profile', foreign_keys=[user_id])

class Teacher(db.Model):
    __tablename__ = 'teachers'
    teacher_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    employee_id = db.Column(db.String(20), unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(50))
    phone = db.Column(db.String(15))

    # Relationship
    user = db.relationship('User', backref='teacher_profile', foreign_keys=[user_id])

class Subject(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))
    credits = db.Column(db.Integer, default=3)

    # Relationships
    teacher = db.relationship('Teacher', backref='subjects', foreign_keys=[teacher_id])

class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='absent')
    marked_by = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref='attendance_records', foreign_keys=[student_id])
    subject = db.relationship('Subject', backref='attendance_records', foreign_keys=[subject_id])
    teacher = db.relationship('Teacher', backref='marked_attendance', foreign_keys=[marked_by])

class Marks(db.Model):
    __tablename__ = 'marks'
    marks_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    internal_marks = db.Column(db.Float, default=0)
    assignment_marks = db.Column(db.Float, default=0)
    exam_marks = db.Column(db.Float, default=0)
    total_marks = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    grade = db.Column(db.String(2))
    semester = db.Column(db.Integer)
    academic_year = db.Column(db.String(20))

    # Relationships
    student = db.relationship('Student', backref='marks_records', foreign_keys=[student_id])
    subject = db.relationship('Subject', backref='marks_records', foreign_keys=[subject_id])

class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    max_marks = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject = db.relationship('Subject', backref='assignments', foreign_keys=[subject_id])
    teacher = db.relationship('Teacher', backref='assignments', foreign_keys=[teacher_id])

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime)
    marks_obtained = db.Column(db.Float)
    feedback = db.Column(db.Text)

    # Relationships
    assignment = db.relationship('Assignment', backref='submissions', foreign_keys=[assignment_id])
    student = db.relationship('Student', backref='assignment_submissions', foreign_keys=[student_id])

class Timetable(db.Model):
    __tablename__ = 'timetable'
    timetable_id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))
    room = db.Column(db.String(20))

    # Relationship
    subject = db.relationship('Subject', backref='timetable_entries', foreign_keys=[subject_id])

class Notice(db.Model):
    __tablename__ = 'notices'
    notice_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), default='General')
    posted_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    posted_by_role = db.Column(db.String(20))
    expiry_date = db.Column(db.Date)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='notices', foreign_keys=[posted_by])

# ===== HELPER FUNCTIONS =====
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Access denied. Student only.', 'error')
            return redirect(url_for('dashboard_redirect'))
        return f(*args, **kwargs)
    return decorated

def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'teacher':
            flash('Access denied. Teacher only.', 'error')
            return redirect(url_for('dashboard_redirect'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin only.', 'error')
            return redirect(url_for('dashboard_redirect'))
        return f(*args, **kwargs)
    return decorated

def get_student():
    return Student.query.filter_by(user_id=session['user_id']).first()

def get_teacher():
    return Teacher.query.filter_by(user_id=session['user_id']).first()

# ===== ROUTES =====
@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Campusora</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0a0e27, #1a1a4e, #2d1b69); min-height:100vh; color:white; }
nav { padding:20px 50px; display:flex; justify-content:space-between; align-items:center; background:rgba(0,0,0,0.3); backdrop-filter:blur(10px); }
.logo { font-size:28px; font-weight:bold; color:#a78bfa; }
.logo span { color:white; }
.nav-links a { color:#c4b5fd; text-decoration:none; margin-left:30px; }
.nav-links a:hover { color:white; }
.hero { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:80px 20px; min-height:70vh; }
.hero h1 { font-size:64px; font-weight:800; background:linear-gradient(to right,#a78bfa,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p { font-size:22px; color:#c4b5fd; margin:20px 0 40px; max-width:600px; }
.btn { padding:14px 40px; border-radius:50px; text-decoration:none; font-weight:600; transition:all 0.3s; border:none; cursor:pointer; font-size:16px; }
.btn-primary { background:#7c3aed; color:white; }
.btn-primary:hover { background:#6d28d9; transform:translateY(-2px); }
.btn-outline { background:transparent; color:white; border:2px solid #7c3aed; }
.btn-outline:hover { background:#7c3aed; }
.features { padding:60px 50px; background:rgba(255,255,255,0.05); }
.features h2 { text-align:center; font-size:36px; margin-bottom:40px; color:#a78bfa; }
.feature-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:30px; max-width:1200px; margin:0 auto; }
.feature-card { background:rgba(255,255,255,0.08); padding:30px; border-radius:16px; text-align:center; border:1px solid rgba(255,255,255,0.1); transition:all 0.3s; }
.feature-card:hover { transform:translateY(-5px); border-color:#7c3aed; }
.feature-card .icon { font-size:40px; margin-bottom:15px; }
.feature-card h3 { color:#c4b5fd; margin-bottom:10px; }
.feature-card p { color:#9ca3af; font-size:14px; }
footer { text-align:center; padding:30px; color:#6b7280; border-top:1px solid rgba(255,255,255,0.05); }
.btn-group { display:flex; gap:20px; flex-wrap:wrap; justify-content:center; }
@media(max-width:768px){ nav{flex-direction:column;gap:15px;padding:20px;} .hero h1{font-size:36px;} .features{padding:40px 20px;} }
</style>
</head>
<body>
<nav><div class="logo">CAMPUS<span>ORA</span></div><div class="nav-links"><a href="#features">Features</a><a href="/login">Login</a></div></nav>
<section class="hero">
<h1>CAMPUSORA</h1>
<p>One Campus. One Connected Experience.</p>
<p style="font-size:18px;color:#c4b5fd;max-width:700px;">A unified digital platform for students, teachers and administrators.</p>
<div class="btn-group">
<a href="/login" class="btn btn-primary">Student Login</a>
<a href="/login" class="btn btn-outline">Teacher Login</a>
<a href="/login" class="btn btn-outline">Admin Login</a>
</div>
</section>
<section class="features" id="features">
<h2>✨ Key Features</h2>
<div class="feature-grid">
<div class="feature-card"><div class="icon">📊</div><h3>Smart Attendance</h3><p>Track attendance with alerts</p></div>
<div class="feature-card"><div class="icon">📈</div><h3>Academic Performance</h3><p>View marks and grades</p></div>
<div class="feature-card"><div class="icon">📝</div><h3>Assignments</h3><p>Manage assignments digitally</p></div>
<div class="feature-card"><div class="icon">📅</div><h3>Timetable</h3><p>Access class schedule</p></div>
<div class="feature-card"><div class="icon">📢</div><h3>Digital Notices</h3><p>Stay updated</p></div>
<div class="feature-card"><div class="icon">🎯</div><h3>Centralized Management</h3><p>All in one place</p></div>
</div>
</section>
<footer><p>&copy; 2026 Campusora. All rights reserved.</p></footer>
</body>
</html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_redirect'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.role != role:
                flash(f'Please login as {user.role}', 'error')
                return render_template_string(LOGIN_TEMPLATE)
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['username'] = user.username
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome {user.username}!', 'success')
            return redirect(url_for('dashboard_redirect'))
        flash('Invalid credentials.', 'error')

    return render_template_string(LOGIN_TEMPLATE)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Login - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#0a0e27,#1a1a4e,#2d1b69);min-height:100vh;display:flex;justify-content:center;align-items:center;}
.login-container{background:rgba(255,255,255,0.08);backdrop-filter:blur(20px);padding:50px 40px;border-radius:24px;width:100%;max-width:420px;border:1px solid rgba(255,255,255,0.1);}
.logo{text-align:center;font-size:32px;font-weight:bold;color:#a78bfa;margin-bottom:8px;}
.logo span{color:white;}
.subtitle{text-align:center;color:#9ca3af;margin-bottom:30px;font-size:14px;}
.form-group{margin-bottom:20px;}
label{display:block;color:#c4b5fd;margin-bottom:6px;font-size:14px;}
input,select{width:100%;padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);color:white;font-size:15px;}
input:focus{outline:none;border-color:#7c3aed;}
.btn{width:100%;padding:14px;border:none;border-radius:12px;background:#7c3aed;color:white;font-size:16px;font-weight:600;cursor:pointer;}
.btn:hover{background:#6d28d9;}
.flash{padding:12px 16px;border-radius:10px;margin-bottom:10px;font-size:14px;}
.flash-success{background:rgba(34,197,94,0.2);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.flash-error{background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.role-selector{display:flex;gap:10px;margin-bottom:20px;}
.role-option{flex:1;padding:10px;text-align:center;border-radius:10px;border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;background:rgba(255,255,255,0.05);color:#9ca3af;}
.role-option:hover{border-color:#7c3aed;}
.role-option.active{border-color:#7c3aed;background:rgba(124,58,237,0.2);color:white;}
.role-option input{display:none;}
.links{text-align:center;margin-top:20px;color:#6b7280;font-size:14px;}
</style>
</head>
<body>
<div class="login-container">
<div class="logo">CAMPUS<span>ORA</span></div>
<div class="subtitle">Sign in to your account</div>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="flash flash-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
<form method="POST">
<div class="form-group"><label>Username</label><input type="text" name="username" placeholder="Enter username" required></div>
<div class="form-group"><label>Password</label><input type="password" name="password" placeholder="Enter password" required></div>
<div class="form-group"><label>Login as</label>
<div class="role-selector">
<label class="role-option active"><input type="radio" name="role" value="student" checked>👨‍🎓 Student</label>
<label class="role-option"><input type="radio" name="role" value="teacher">👨‍🏫 Teacher</label>
<label class="role-option"><input type="radio" name="role" value="admin">🛡️ Admin</label>
</div></div>
<button type="submit" class="btn">Sign In</button>
</form>
<div class="links"><p>Demo: student / teacher / admin | password123</p></div>
</div>
<script>document.querySelectorAll('.role-option').forEach(el=>{el.addEventListener('click',function(){document.querySelectorAll('.role-option').forEach(r=>r.classList.remove('active'));this.classList.add('active');this.querySelector('input').checked=true;});});</script>
</body>
</html>
'''

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard-redirect')
def dashboard_redirect():
    role = session.get('role')
    if role == 'student': return redirect(url_for('student_dashboard'))
    elif role == 'teacher': return redirect(url_for('teacher_dashboard'))
    elif role == 'admin': return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

# ===== STUDENT ROUTES =====
@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    student = get_student()
    if not student:
        flash('Student profile not found.', 'error')
        return redirect(url_for('logout'))

    subjects = Subject.query.filter_by(branch=student.branch, semester=student.semester).all()
    total_att = Attendance.query.filter_by(student_id=student.student_id).count()
    present_att = Attendance.query.filter_by(student_id=student.student_id, status='present').count()
    overall = round((present_att/total_att)*100,2) if total_att>0 else 0

    subject_att = []
    for s in subjects:
        total = Attendance.query.filter_by(student_id=student.student_id, subject_id=s.subject_id).count()
        present = Attendance.query.filter_by(student_id=student.student_id, subject_id=s.subject_id, status='present').count()
        perc = round((present/total)*100,2) if total>0 else 0
        status = 'good' if perc>=75 else 'warning' if perc>=60 else 'danger'
        subject_att.append({'name':s.subject_name,'percentage':perc,'status':status})

    pending = 0
    for s in subjects:
        for a in Assignment.query.filter_by(subject_id=s.subject_id).all():
            sub = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id, student_id=student.student_id).first()
            if not sub or sub.status=='pending':
                if a.due_date >= datetime.now().date():
                    pending += 1

    notices = Notice.query.order_by(Notice.created_at.desc()).limit(4).all()

    return render_template_string(STUDENT_DASHBOARD_TEMPLATE,
        student=student, overall_attendance=overall, subject_attendance=subject_att,
        pending_count=pending, latest_notices=notices, subjects_count=len(subjects))

STUDENT_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Student Dashboard - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);position:sticky;top:0;height:100vh;overflow-y:auto;}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;overflow-y:auto;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.greeting{color:#c4b5fd;margin-bottom:30px;font-size:18px;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:35px;}
.stat-card{background:rgba(255,255,255,0.05);padding:24px 20px;border-radius:16px;border:1px solid rgba(255,255,255,0.06);}
.stat-card .label{color:#9ca3af;font-size:13px;text-transform:uppercase;letter-spacing:0.5px;}
.stat-card .value{font-size:32px;font-weight:700;margin-top:8px;color:#a78bfa;}
.section-title{font-size:20px;margin-bottom:20px;color:#c4b5fd;}
.progress-list{display:grid;gap:12px;margin-bottom:35px;}
.progress-item{display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.03);padding:12px 18px;border-radius:12px;}
.progress-item .name{color:#c4b5fd;}
.progress-bar{width:200px;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden;}
.progress-bar .fill{height:100%;border-radius:4px;transition:width 0.6s;}
.fill-good{background:#22c55e;}
.fill-warning{background:#eab308;}
.fill-danger{background:#ef4444;}
.progress-item .perc{font-weight:600;min-width:50px;text-align:right;}
.perc-good{color:#22c55e;}
.perc-warning{color:#eab308;}
.perc-danger{color:#ef4444;}
.notice-item{background:rgba(255,255,255,0.03);padding:16px 20px;border-radius:12px;border-left:3px solid #7c3aed;margin-bottom:10px;}
.notice-item .title{font-weight:600;}
.notice-item .meta{color:#6b7280;font-size:12px;margin-top:4px;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;}
.badge-urgent{background:#ef4444;color:white;}
.badge-events{background:#8b5cf6;color:white;}
.badge-academic{background:#3b82f6;color:white;}
.badge-general{background:#6b7280;color:white;}
@media(max-width:768px){.sidebar{display:none;}.main{padding:20px;}.stats{grid-template-columns:1fr 1fr;}.progress-bar{width:100px;}}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard" class="active"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main">
<div class="header"><h1>Student <span>Dashboard</span></h1><span style="color:#9ca3af;">{{ student.full_name }}</span></div>
<div class="greeting">👋 Good Morning, <strong>{{ student.full_name }}</strong></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:25px;background:rgba(255,255,255,0.03);padding:16px 20px;border-radius:12px;">
<div><span style="color:#6b7280;">Roll:</span> {{ student.roll_number }}</div>
<div><span style="color:#6b7280;">Branch:</span> {{ student.branch }}</div>
<div><span style="color:#6b7280;">Semester:</span> {{ student.semester }}</div>
<div><span style="color:#6b7280;">Section:</span> {{ student.section }}</div>
</div>
<div class="stats">
<div class="stat-card"><div class="label">Overall Attendance</div><div class="value">{{ overall_attendance }}%</div></div>
<div class="stat-card"><div class="label">Pending Assignments</div><div class="value">{{ pending_count }}</div></div>
<div class="stat-card"><div class="label">Subjects</div><div class="value">{{ subjects_count }}</div></div>
<div class="stat-card"><div class="label">Latest Notices</div><div class="value">{{ latest_notices|length }}</div></div>
</div>
<div class="section-title">📊 Academic Overview</div>
<div class="progress-list">
{% for item in subject_attendance %}
<div class="progress-item">
<span class="name">{{ item.name }}</span>
<div class="progress-bar"><div class="fill {% if item.status=='good' %}fill-good{% elif item.status=='warning' %}fill-warning{% else %}fill-danger{% endif %}" style="width:{{ item.percentage }}%"></div></div>
<span class="perc {% if item.status=='good' %}perc-good{% elif item.status=='warning' %}perc-warning{% else %}perc-danger{% endif %}">{{ item.percentage }}%</span>
</div>
{% endfor %}
</div>
<div class="section-title">📢 Latest Notices</div>
{% for notice in latest_notices %}
<div class="notice-item"><div class="title">{{ notice.title }}</div>
<div style="color:#9ca3af;font-size:14px;">{{ notice.content[:100] }}{% if notice.content|length>100 %}...{% endif %}</div>
<div class="meta"><span class="badge badge-{{ notice.category|lower }}">{{ notice.category }}</span> {{ notice.created_at.strftime('%b %d, %Y') }}</div></div>
{% endfor %}
</div>
</body>
</html>
'''

@app.route('/student/profile')
@login_required
@student_required
def student_profile():
    s = get_student()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Profile - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.profile-card{background:rgba(255,255,255,0.05);border-radius:16px;padding:30px;max-width:600px;border:1px solid rgba(255,255,255,0.06);}
.profile-row{display:flex;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);}
.profile-row .label{color:#6b7280;width:150px;}
.profile-row .value{color:#c4b5fd;}
.back-link{color:#a78bfa;text-decoration:none;margin-bottom:20px;display:inline-block;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile" class="active"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>My <span>Profile</span></h1></div>
<a href="/student/dashboard" class="back-link">← Back</a>
<div class="profile-card">
<div style="text-align:center;margin-bottom:25px;"><div style="font-size:72px;background:rgba(124,58,237,0.2);width:100px;height:100px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto;border:2px solid #7c3aed;">👤</div></div>
<div class="profile-row"><span class="label">Full Name</span><span class="value">{{ s.full_name }}</span></div>
<div class="profile-row"><span class="label">Roll Number</span><span class="value">{{ s.roll_number }}</span></div>
<div class="profile-row"><span class="label">Branch</span><span class="value">{{ s.branch }}</span></div>
<div class="profile-row"><span class="label">Semester</span><span class="value">{{ s.semester }}</span></div>
<div class="profile-row"><span class="label">Section</span><span class="value">{{ s.section }}</span></div>
<div class="profile-row"><span class="label">Email</span><span class="value">{{ s.user.email }}</span></div>
</div></div>
</body>
</html>
    ''', s=s)

@app.route('/student/attendance')
@login_required
@student_required
def student_attendance():
    s = get_student()
    subjects = Subject.query.filter_by(branch=s.branch, semester=s.semester).all()
    data = []
    for sub in subjects:
        total = Attendance.query.filter_by(student_id=s.student_id, subject_id=sub.subject_id).count()
        present = Attendance.query.filter_by(student_id=s.student_id, subject_id=sub.subject_id, status='present').count()
        perc = round((present/total)*100,2) if total>0 else 0
        status = 'Good' if perc>=75 else 'Warning' if perc>=60 else 'Low'
        needed = max(0, int(4*(0.75*total - present))) if perc<75 and total>0 else 0
        data.append({'subject':sub.subject_name,'subject_code':sub.subject_code,'present':present,'total':total,'absent':total-present,'percentage':perc,'status':status,'needed':needed})
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Attendance - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
table{width:100%;border-collapse:collapse;background:rgba(255,255,255,0.03);border-radius:12px;overflow:hidden;}
th,td{padding:14px 18px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05);}
th{background:rgba(124,58,237,0.15);color:#c4b5fd;font-weight:600;font-size:14px;}
.badge{display:inline-block;padding:3px 12px;border-radius:20px;font-size:12px;font-weight:600;}
.badge-good{background:rgba(34,197,94,0.2);color:#22c55e;}
.badge-warning{background:rgba(234,179,8,0.2);color:#eab308;}
.badge-low{background:rgba(239,68,68,0.2);color:#ef4444;}
.warning-msg{background:rgba(239,68,68,0.1);padding:12px 18px;border-radius:10px;border-left:3px solid #ef4444;margin-top:15px;color:#fca5a5;}
.back-link{color:#a78bfa;text-decoration:none;display:inline-block;margin-bottom:20px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance" class="active"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Attendance <span>Record</span></h1></div>
<a href="/student/dashboard" class="back-link">← Back</a>
<table><thead><tr><th>Subject</th><th>Present</th><th>Total</th><th>Absent</th><th>%</th><th>Status</th></tr></thead>
<tbody>
{% for item in data %}
<tr><td><strong>{{ item.subject }}</strong><br><small style="color:#6b7280;">{{ item.subject_code }}</small></td>
<td>{{ item.present }}</td><td>{{ item.total }}</td><td>{{ item.absent }}</td>
<td><strong>{{ item.percentage }}%</strong></td>
<td><span class="badge badge-{{ item.status|lower }}">{{ item.status }}</span>{% if item.status=='Low' and item.needed>0 %}<br><small style="color:#ef4444;">Need {{ item.needed }} more</small>{% endif %}</td></tr>
{% endfor %}
</tbody></table>
{% for item in data %}{% if item.status=='Low' %}<div class="warning-msg">⚠️ {{ item.subject }} attendance is below 75%.</div>{% endif %}{% endfor %}
</div>
</body>
</html>
    ''', data=data)

@app.route('/student/marks')
@login_required
@student_required
def student_marks():
    s = get_student()
    subjects = Subject.query.filter_by(branch=s.branch, semester=s.semester).all()
    marks_list = []
    for sub in subjects:
        m = Marks.query.filter_by(student_id=s.student_id, subject_id=sub.subject_id).first()
        if m:
            marks_list.append({'subject':sub.subject_name,'subject_code':sub.subject_code,'internal':m.internal_marks,'assignment':m.assignment_marks,'exam':m.exam_marks,'total':m.total_marks,'percentage':m.percentage,'grade':m.grade})
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Marks - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
table{width:100%;border-collapse:collapse;background:rgba(255,255,255,0.03);border-radius:12px;overflow:hidden;}
th,td{padding:14px 18px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05);}
th{background:rgba(124,58,237,0.15);color:#c4b5fd;font-weight:600;}
.grade-a{color:#22c55e;font-weight:700;}
.grade-b{color:#3b82f6;font-weight:700;}
.grade-c{color:#eab308;font-weight:700;}
.grade-d{color:#f97316;font-weight:700;}
.grade-f{color:#ef4444;font-weight:700;}
.back-link{color:#a78bfa;text-decoration:none;display:inline-block;margin-bottom:20px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks" class="active"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Academic <span>Marks</span></h1></div>
<a href="/student/dashboard" class="back-link">← Back</a>
<table><thead><tr><th>Subject</th><th>Internal(20)</th><th>Assignment(10)</th><th>Exam(100)</th><th>Total</th><th>%</th><th>Grade</th></tr></thead>
<tbody>
{% for m in marks_list %}
<tr><td><strong>{{ m.subject }}</strong><br><small style="color:#6b7280;">{{ m.subject_code }}</small></td>
<td>{{ m.internal }}</td><td>{{ m.assignment }}</td><td>{{ m.exam }}</td><td>{{ m.total }}</td>
<td><strong>{{ m.percentage }}%</strong></td>
<td><span class="grade-{{ m.grade|lower }}">{{ m.grade }}</span></td></tr>
{% else %}<tr><td colspan="7" style="text-align:center;color:#6b7280;padding:30px;">No marks available.</td></tr>
{% endfor %}
</tbody></table>
</div>
</body>
</html>
    ''', marks_list=marks_list)

@app.route('/student/assignments')
@login_required
@student_required
def student_assignments():
    s = get_student()
    subjects = Subject.query.filter_by(branch=s.branch, semester=s.semester).all()
    subject_ids = [sub.subject_id for sub in subjects]
    assignments = Assignment.query.filter(Assignment.subject_id.in_(subject_ids)).all()
    data = []
    for a in assignments:
        sub = AssignmentSubmission.query.filter_by(assignment_id=a.assignment_id, student_id=s.student_id).first()
        status = 'Pending'
        if sub:
            if sub.status == 'submitted': status = 'Submitted'
            elif sub.status == 'graded': status = 'Graded'
        is_overdue = a.due_date < datetime.now().date() and status != 'Graded'
        data.append({
            'title': a.title,
            'description': a.description or 'No description',
            'subject': a.subject.subject_name,
            'teacher': a.teacher.full_name if a.teacher else 'Unknown',
            'due_date': a.due_date.strftime('%Y-%m-%d'),
            'max_marks': a.max_marks,
            'status': status,
            'is_overdue': is_overdue
        })
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Assignments - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.assignment-card{background:rgba(255,255,255,0.05);padding:16px 20px;border-radius:12px;margin-bottom:12px;border:1px solid rgba(255,255,255,0.06);}
.assignment-card .title{font-weight:600;color:#c4b5fd;font-size:17px;}
.assignment-card .meta{display:flex;gap:15px;font-size:13px;color:#6b7280;margin-top:6px;flex-wrap:wrap;}
.assignment-card .desc{color:#9ca3af;font-size:14px;margin-top:6px;}
.badge{display:inline-block;padding:2px 12px;border-radius:20px;font-size:11px;font-weight:600;}
.badge-pending{background:rgba(234,179,8,0.2);color:#eab308;}
.badge-submitted{background:rgba(59,130,246,0.2);color:#3b82f6;}
.badge-graded{background:rgba(34,197,94,0.2);color:#22c55e;}
.back-link{color:#a78bfa;text-decoration:none;display:inline-block;margin-bottom:20px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments" class="active"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>My <span>Assignments</span></h1></div>
<a href="/student/dashboard" class="back-link">← Back</a>
{% for a in assignments %}
<div class="assignment-card" {% if a.is_overdue %}style="border-color:#ef4444;"{% endif %}>
<div class="title">{{ a.title }}</div>
<div class="meta">
<span>📚 {{ a.subject }}</span>
<span>👨‍🏫 {{ a.teacher }}</span>
<span>📅 Due: {{ a.due_date }}</span>
<span>📊 {{ a.max_marks }} marks</span>
</div>
<div class="desc">{{ a.description[:150] }}{% if a.description|length>150 %}...{% endif %}</div>
<div style="margin-top:10px;"><span class="badge badge-{{ a.status|lower }}">{{ a.status }}</span>{% if a.is_overdue %} <span style="color:#ef4444;font-size:13px;">⚠️ Overdue!</span>{% endif %}</div>
</div>
{% else %}<div style="text-align:center;color:#6b7280;padding:40px;">No assignments.</div>{% endfor %}
</div>
</body>
</html>
    ''', assignments=data)

@app.route('/student/timetable')
@login_required
@student_required
def student_timetable():
    s = get_student()
    entries = Timetable.query.filter_by(branch=s.branch, semester=s.semester, section=s.section).order_by(Timetable.day_of_week, Timetable.start_time).all()
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    timetable = {day: [] for day in days}
    for e in entries:
        timetable[e.day_of_week].append({
            'subject': e.subject.subject_name,
            'teacher': e.subject.teacher.full_name if e.subject.teacher else 'TBA',
            'room': e.room or 'TBA',
            'start': e.start_time.strftime('%I:%M %p'),
            'end': e.end_time.strftime('%I:%M %p')
        })
    current_day = datetime.now().strftime('%A')
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Timetable - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.timetable-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;}
.day-card{background:rgba(255,255,255,0.05);padding:16px;border-radius:12px;border:1px solid rgba(255,255,255,0.06);}
.day-card .day-name{font-weight:600;color:#a78bfa;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:12px;}
.day-card .day-name.today{color:#22c55e;}
.class-item{padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.03);font-size:13px;}
.class-item:last-child{border-bottom:none;}
.class-item .subj{color:#c4b5fd;font-weight:500;}
.class-item .teacher{color:#6b7280;font-size:12px;}
.class-item .time{color:#9ca3af;font-size:12px;}
.back-link{color:#a78bfa;text-decoration:none;display:inline-block;margin-bottom:20px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable" class="active"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Class <span>Timetable</span></h1><span style="color:#9ca3af;">{{ current_day }}</span></div>
<a href="/student/dashboard" class="back-link">← Back</a>
<div class="timetable-grid">
{% for day, classes in timetable.items() %}
<div class="day-card"><div class="day-name {% if day==current_day %}today{% endif %}">{{ day }} {% if day==current_day %}⭐ Today{% endif %}</div>
{% if classes %}{% for c in classes %}<div class="class-item"><div class="subj">{{ c.subject }}</div><div class="teacher">👨‍🏫 {{ c.teacher }}</div><div class="time">🕐 {{ c.start }} - {{ c.end }}</div></div>{% endfor %}{% else %}<div style="color:#6b7280;font-size:13px;padding:10px 0;">No classes</div>{% endif %}</div>
{% endfor %}
</div></div>
</body>
</html>
    ''', timetable=timetable, current_day=current_day)

@app.route('/student/notices')
@login_required
@student_required
def student_notices():
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Notices - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.notice-item{background:rgba(255,255,255,0.05);padding:16px 20px;border-radius:12px;margin-bottom:12px;border-left:4px solid #7c3aed;}
.notice-item.urgent{border-left-color:#ef4444;background:rgba(239,68,68,0.05);}
.notice-item .title{font-weight:600;color:#c4b5fd;font-size:17px;}
.notice-item .content{color:#9ca3af;margin-top:4px;}
.notice-item .meta{display:flex;gap:12px;font-size:12px;color:#6b7280;margin-top:8px;flex-wrap:wrap;}
.badge{display:inline-block;padding:2px 12px;border-radius:20px;font-size:11px;font-weight:600;}
.badge-urgent{background:rgba(239,68,68,0.2);color:#ef4444;}
.badge-examination{background:rgba(234,179,8,0.2);color:#eab308;}
.badge-events{background:rgba(139,92,246,0.2);color:#8b5cf6;}
.badge-academic{background:rgba(59,130,246,0.2);color:#3b82f6;}
.badge-general{background:rgba(107,114,128,0.2);color:#9ca3af;}
.back-link{color:#a78bfa;text-decoration:none;display:inline-block;margin-bottom:20px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/student/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/student/profile"><span class="icon">👤</span> My Profile</a>
<a href="/student/attendance"><span class="icon">📋</span> Attendance</a>
<a href="/student/marks"><span class="icon">📈</span> Marks</a>
<a href="/student/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/student/timetable"><span class="icon">📅</span> Timetable</a>
<a href="/student/notices" class="active"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Notice <span>Board</span></h1></div>
<a href="/student/dashboard" class="back-link">← Back</a>
{% for n in notices %}
<div class="notice-item {% if n.category=='Urgent' %}urgent{% endif %}">
<div class="title">{{ n.title }}</div>
<div class="content">{{ n.content }}</div>
<div class="meta">
<span class="badge badge-{{ n.category|lower }}">{{ n.category }}</span>
<span>👤 {{ n.posted_by_role }}</span>
<span>📅 {{ n.created_at.strftime('%b %d, %Y') }}</span>
{% if n.is_pinned %}<span style="color:#eab308;">📌 Pinned</span>{% endif %}
</div>
</div>
{% else %}<div style="text-align:center;color:#6b7280;padding:40px;">No notices.</div>{% endfor %}
</div>
</body>
</html>
    ''', notices=notices)

# ===== TEACHER ROUTES =====
@app.route('/teacher/dashboard')
@login_required
@teacher_required
def teacher_dashboard():
    t = get_teacher()
    if not t:
        flash('Teacher profile not found.', 'error')
        return redirect(url_for('logout'))
    subjects = Subject.query.filter_by(teacher_id=t.teacher_id).all()
    total_students = Student.query.count()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Teacher Dashboard - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;margin-bottom:30px;}
.stat-card{background:rgba(255,255,255,0.05);padding:20px;border-radius:16px;text-align:center;}
.stat-card .value{font-size:28px;font-weight:700;color:#a78bfa;}
.stat-card .label{color:#6b7280;font-size:13px;margin-top:4px;}
.actions{display:flex;gap:12px;flex-wrap:wrap;}
.action-btn{padding:12px 24px;background:rgba(124,58,237,0.2);color:#a78bfa;border:1px solid rgba(124,58,237,0.3);border-radius:12px;text-decoration:none;transition:all 0.3s;font-size:14px;}
.action-btn:hover{background:#7c3aed;color:white;transform:translateY(-2px);}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/teacher/dashboard" class="active"><span class="icon">📊</span> Dashboard</a>
<a href="/teacher/attendance"><span class="icon">📋</span> Mark Attendance</a>
<a href="/teacher/marks"><span class="icon">📈</span> Enter Marks</a>
<a href="/teacher/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/teacher/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main">
<div class="header"><h1>Teacher <span>Dashboard</span></h1><span style="color:#9ca3af;">{{ t.full_name }}</span></div>
<div style="color:#c4b5fd;margin-bottom:25px;font-size:18px;">👋 Welcome, {{ t.full_name }}</div>
<div class="stats">
<div class="stat-card"><div class="value">{{ subjects|length }}</div><div class="label">Subjects</div></div>
<div class="stat-card"><div class="value">{{ total_students }}</div><div class="label">Students</div></div>
<div class="stat-card"><div class="value">{{ t.department }}</div><div class="label">Department</div></div>
</div>
<h3 style="color:#c4b5fd;margin-bottom:15px;">Quick Actions</h3>
<div class="actions">
<a href="/teacher/attendance" class="action-btn">📋 Mark Attendance</a>
<a href="/teacher/marks" class="action-btn">📈 Enter Marks</a>
<a href="/teacher/assignments" class="action-btn">📝 Create Assignment</a>
<a href="/teacher/notices" class="action-btn">📢 Post Notice</a>
</div>
<div style="margin-top:30px;"><h3 style="color:#c4b5fd;margin-bottom:15px;">Assigned Subjects</h3>
{% for s in subjects %}<div style="background:rgba(255,255,255,0.03);padding:12px 18px;border-radius:10px;margin-bottom:8px;display:flex;justify-content:space-between;"><span>{{ s.subject_name }}</span><span style="color:#6b7280;">{{ s.subject_code }}</span></div>{% endfor %}</div>
</div>
</body>
</html>
    ''', t=t, subjects=subjects, total_students=total_students)

@app.route('/teacher/attendance', methods=['GET','POST'])
@login_required
@teacher_required
def teacher_attendance():
    t = get_teacher()
    if not t:
        flash('Teacher not found.', 'error')
        return redirect(url_for('logout'))
    subjects = Subject.query.filter_by(teacher_id=t.teacher_id).all()
    students = Student.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        for s in students:
            status = request.form.get(f'status_{s.student_id}', 'absent')
            att = Attendance(student_id=s.student_id, subject_id=subject_id, date=date, status=status, marked_by=t.teacher_id)
            db.session.add(att)
        db.session.commit()
        flash('Attendance marked!', 'success')
        return redirect(url_for('teacher_attendance'))

    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Mark Attendance - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.flash{padding:12px 16px;border-radius:10px;margin-bottom:10px;}
.flash-success{background:rgba(34,197,94,0.2);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.flash-error{background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.form-group{margin-bottom:16px;}
label{display:block;color:#c4b5fd;margin-bottom:4px;font-size:14px;}
select,input{width:100%;max-width:300px;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:white;}
.btn{padding:10px 24px;background:#7c3aed;border:none;border-radius:10px;color:white;cursor:pointer;}
.btn:hover{background:#6d28d9;}
table{width:100%;border-collapse:collapse;margin-top:20px;}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05);}
th{color:#c4b5fd;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/teacher/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/teacher/attendance" class="active"><span class="icon">📋</span> Mark Attendance</a>
<a href="/teacher/marks"><span class="icon">📈</span> Enter Marks</a>
<a href="/teacher/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/teacher/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Mark <span>Attendance</span></h1></div>
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for cat,msg in messages %}<div class="flash flash-{{ cat }}">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}
<form method="POST">
<div class="form-group"><label>Subject</label><select name="subject_id">{% for s in subjects %}<option value="{{ s.subject_id }}">{{ s.subject_name }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Date</label><input type="date" name="date" value="{{ datetime.now().strftime('%Y-%m-%d') }}" required></div>
<h3 style="color:#c4b5fd;margin:20px 0 10px;">Students</h3>
<table><thead><tr><th>Roll</th><th>Name</th><th>Status</th></tr></thead>
<tbody>{% for s in students %}<tr><td>{{ s.roll_number }}</td><td>{{ s.full_name }}</td><td><select name="status_{{ s.student_id }}"><option value="present">Present</option><option value="absent" selected>Absent</option><option value="leave">Leave</option></select></td></tr>{% endfor %}</tbody></table>
<button type="submit" class="btn" style="margin-top:20px;">Submit</button>
</form>
</div>
</body>
</html>
    ''', subjects=subjects, students=students, datetime=datetime)

@app.route('/teacher/marks', methods=['GET','POST'])
@login_required
@teacher_required
def teacher_marks():
    t = get_teacher()
    if not t:
        flash('Teacher not found.', 'error')
        return redirect(url_for('logout'))
    subjects = Subject.query.filter_by(teacher_id=t.teacher_id).all()
    students = Student.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        student_id = request.form.get('student_id')
        internal = float(request.form.get('internal', 0))
        assignment = float(request.form.get('assignment', 0))
        exam = float(request.form.get('exam', 0))
        semester = int(request.form.get('semester', 3))

        if internal > 20 or assignment > 10 or exam > 100:
            flash('Marks exceed maximum!', 'error')
            return redirect(url_for('teacher_marks'))
        if internal < 0 or assignment < 0 or exam < 0:
            flash('Marks cannot be negative!', 'error')
            return redirect(url_for('teacher_marks'))

        total = internal + assignment + exam
        percentage = (total / 130) * 100
        grade = 'A' if percentage>=90 else 'B' if percentage>=80 else 'C' if percentage>=70 else 'D' if percentage>=60 else 'F'

        marks = Marks.query.filter_by(student_id=student_id, subject_id=subject_id, semester=semester).first()
        if marks:
            marks.internal_marks = internal
            marks.assignment_marks = assignment
            marks.exam_marks = exam
            marks.total_marks = total
            marks.percentage = round(percentage, 2)
            marks.grade = grade
        else:
            marks = Marks(student_id=student_id, subject_id=subject_id, internal_marks=internal, assignment_marks=assignment, exam_marks=exam, total_marks=total, percentage=round(percentage,2), grade=grade, semester=semester, academic_year='2025-2026')
            db.session.add(marks)
        db.session.commit()
        flash('Marks entered!', 'success')
        return redirect(url_for('teacher_marks'))

    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Enter Marks - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.flash{padding:12px 16px;border-radius:10px;margin-bottom:10px;}
.flash-success{background:rgba(34,197,94,0.2);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.flash-error{background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.form-group{margin-bottom:16px;}
label{display:block;color:#c4b5fd;margin-bottom:4px;font-size:14px;}
select,input{width:100%;max-width:300px;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:white;}
.btn{padding:10px 24px;background:#7c3aed;border:none;border-radius:10px;color:white;cursor:pointer;}
.btn:hover{background:#6d28d9;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/teacher/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/teacher/attendance"><span class="icon">📋</span> Mark Attendance</a>
<a href="/teacher/marks" class="active"><span class="icon">📈</span> Enter Marks</a>
<a href="/teacher/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/teacher/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Enter <span>Marks</span></h1></div>
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for cat,msg in messages %}<div class="flash flash-{{ cat }}">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}
<form method="POST">
<div class="form-group"><label>Subject</label><select name="subject_id">{% for s in subjects %}<option value="{{ s.subject_id }}">{{ s.subject_name }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Student</label><select name="student_id">{% for s in students %}<option value="{{ s.student_id }}">{{ s.full_name }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Internal (out of 20)</label><input type="number" name="internal" step="0.5" min="0" max="20" required></div>
<div class="form-group"><label>Assignment (out of 10)</label><input type="number" name="assignment" step="0.5" min="0" max="10" required></div>
<div class="form-group"><label>Exam (out of 100)</label><input type="number" name="exam" step="0.5" min="0" max="100" required></div>
<div class="form-group"><label>Semester</label><input type="number" name="semester" value="3" required></div>
<button type="submit" class="btn">Submit Marks</button>
</form>
</div>
</body>
</html>
    ''', subjects=subjects, students=students)

@app.route('/teacher/assignments', methods=['GET','POST'])
@login_required
@teacher_required
def teacher_assignments():
    t = get_teacher()
    if not t:
        flash('Teacher not found.', 'error')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        max_marks = int(request.form.get('max_marks', 10))

        if not title or not subject_id:
            flash('Title and subject required.', 'error')
            return redirect(url_for('teacher_assignments'))

        assignment = Assignment(title=title, description=description, subject_id=subject_id, teacher_id=t.teacher_id, due_date=due_date, max_marks=max_marks)
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created!', 'success')
        return redirect(url_for('teacher_assignments'))

    subjects = Subject.query.filter_by(teacher_id=t.teacher_id).all()
    subject_ids = [s.subject_id for s in subjects]
    assignments = Assignment.query.filter(Assignment.subject_id.in_(subject_ids)).all()

    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Assignments - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.flash{padding:12px 16px;border-radius:10px;margin-bottom:10px;}
.flash-success{background:rgba(34,197,94,0.2);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.flash-error{background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.form-group{margin-bottom:16px;}
label{display:block;color:#c4b5fd;margin-bottom:4px;font-size:14px;}
select,input,textarea{width:100%;max-width:400px;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:white;}
textarea{min-height:80px;}
.btn{padding:10px 24px;background:#7c3aed;border:none;border-radius:10px;color:white;cursor:pointer;}
.btn:hover{background:#6d28d9;}
.assignment-card{background:rgba(255,255,255,0.05);padding:16px 20px;border-radius:12px;margin-bottom:10px;}
.assignment-card .title{font-weight:600;color:#c4b5fd;}
.assignment-card .meta{color:#6b7280;font-size:13px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/teacher/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/teacher/attendance"><span class="icon">📋</span> Mark Attendance</a>
<a href="/teacher/marks"><span class="icon">📈</span> Enter Marks</a>
<a href="/teacher/assignments" class="active"><span class="icon">📝</span> Assignments</a>
<a href="/teacher/notices"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Manage <span>Assignments</span></h1></div>
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for cat,msg in messages %}<div class="flash flash-{{ cat }}">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}
<h3 style="color:#c4b5fd;margin:20px 0 15px;">Create New</h3>
<form method="POST">
<div class="form-group"><label>Title</label><input type="text" name="title" required></div>
<div class="form-group"><label>Description</label><textarea name="description"></textarea></div>
<div class="form-group"><label>Subject</label><select name="subject_id">{% for s in subjects %}<option value="{{ s.subject_id }}">{{ s.subject_name }}</option>{% endfor %}</select></div>
<div class="form-group"><label>Due Date</label><input type="date" name="due_date" required></div>
<div class="form-group"><label>Max Marks</label><input type="number" name="max_marks" value="10"></div>
<button type="submit" class="btn">Create</button>
</form>
<h3 style="color:#c4b5fd;margin:30px 0 15px;">Existing</h3>
{% for a in assignments %}<div class="assignment-card"><div class="title">{{ a.title }}</div><div class="meta">{{ a.subject.subject_name }} | Due: {{ a.due_date.strftime('%Y-%m-%d') }}</div></div>{% else %}<div style="color:#6b7280;">No assignments.</div>{% endfor %}
</div>
</body>
</html>
    ''', subjects=subjects, assignments=assignments)

@app.route('/teacher/notices', methods=['GET','POST'])
@login_required
@teacher_required
def teacher_notices():
    t = get_teacher()
    if not t:
        flash('Teacher not found.', 'error')
        return redirect(url_for('logout'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'General')
        if not title or not content:
            flash('Title and content required.', 'error')
            return redirect(url_for('teacher_notices'))
        notice = Notice(title=title, content=content, category=category, posted_by=session['user_id'], posted_by_role='teacher')
        db.session.add(notice)
        db.session.commit()
        flash('Notice posted!', 'success')
        return redirect(url_for('teacher_notices'))

    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Notices - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.flash{padding:12px 16px;border-radius:10px;margin-bottom:10px;}
.flash-success{background:rgba(34,197,94,0.2);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.flash-error{background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.form-group{margin-bottom:16px;}
label{display:block;color:#c4b5fd;margin-bottom:4px;font-size:14px;}
select,input,textarea{width:100%;max-width:400px;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:white;}
textarea{min-height:80px;}
.btn{padding:10px 24px;background:#7c3aed;border:none;border-radius:10px;color:white;cursor:pointer;}
.btn:hover{background:#6d28d9;}
.notice-item{background:rgba(255,255,255,0.05);padding:16px 20px;border-radius:12px;margin-bottom:10px;border-left:3px solid #7c3aed;}
.notice-item .title{font-weight:600;color:#c4b5fd;}
.notice-item .meta{color:#6b7280;font-size:13px;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/teacher/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/teacher/attendance"><span class="icon">📋</span> Mark Attendance</a>
<a href="/teacher/marks"><span class="icon">📈</span> Enter Marks</a>
<a href="/teacher/assignments"><span class="icon">📝</span> Assignments</a>
<a href="/teacher/notices" class="active"><span class="icon">📢</span> Notices</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Post <span>Notices</span></h1></div>
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for cat,msg in messages %}<div class="flash flash-{{ cat }}">{{ msg }}</div>{% endfor %}{% endif %}{% endwith %}
<form method="POST">
<div class="form-group"><label>Title</label><input type="text" name="title" required></div>
<div class="form-group"><label>Content</label><textarea name="content" required></textarea></div>
<div class="form-group"><label>Category</label><select name="category"><option>General</option><option>Academic</option><option>Examination</option><option>Events</option><option>Urgent</option></select></div>
<button type="submit" class="btn">Post</button>
</form>
<h3 style="color:#c4b5fd;margin:30px 0 15px;">Recent Notices</h3>
{% for n in notices %}<div class="notice-item"><div class="title">{{ n.title }}</div><div style="color:#9ca3af;">{{ n.content[:150] }}{% if n.content|length>150 %}...{% endif %}</div><div class="meta">{{ n.category }} | {{ n.created_at.strftime('%b %d, %Y') }}</div></div>{% else %}<div style="color:#6b7280;">No notices.</div>{% endfor %}
</div>
</body>
</html>
    ''', notices=notices)

# ===== ADMIN ROUTES =====
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Admin Dashboard - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px;margin-bottom:30px;}
.stat-card{background:rgba(255,255,255,0.05);padding:20px;border-radius:16px;text-align:center;}
.stat-card .value{font-size:32px;font-weight:700;color:#a78bfa;}
.stat-card .label{color:#6b7280;font-size:13px;margin-top:4px;}
.quick-links{display:flex;gap:12px;flex-wrap:wrap;}
.quick-btn{padding:12px 24px;background:rgba(124,58,237,0.2);color:#a78bfa;border:1px solid rgba(124,58,237,0.3);border-radius:12px;text-decoration:none;transition:all 0.3s;font-size:14px;}
.quick-btn:hover{background:#7c3aed;color:white;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/admin/dashboard" class="active"><span class="icon">📊</span> Dashboard</a>
<a href="/admin/students"><span class="icon">👨‍🎓</span> Students</a>
<a href="/admin/teachers"><span class="icon">👨‍🏫</span> Teachers</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Admin <span>Dashboard</span></h1></div>
<div class="stats">
<div class="stat-card"><div class="value">{{ Student.query.count() }}</div><div class="label">Students</div></div>
<div class="stat-card"><div class="value">{{ Teacher.query.count() }}</div><div class="label">Teachers</div></div>
<div class="stat-card"><div class="value">{{ Subject.query.count() }}</div><div class="label">Subjects</div></div>
<div class="stat-card"><div class="value">{{ Notice.query.count() }}</div><div class="label">Notices</div></div>
</div>
<h3 style="color:#c4b5fd;margin-bottom:15px;">Quick Management</h3>
<div class="quick-links">
<a href="/admin/students" class="quick-btn">👨‍🎓 Manage Students</a>
<a href="/admin/teachers" class="quick-btn">👨‍🏫 Manage Teachers</a>
</div>
</div>
</body>
</html>
    ''', Student=Student, Teacher=Teacher, Subject=Subject, Notice=Notice)

@app.route('/admin/students')
@login_required
@admin_required
def admin_students():
    students = Student.query.all()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Students - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
table{width:100%;border-collapse:collapse;}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05);}
th{color:#c4b5fd;font-weight:600;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/admin/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/admin/students" class="active"><span class="icon">👨‍🎓</span> Students</a>
<a href="/admin/teachers"><span class="icon">👨‍🏫</span> Teachers</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Manage <span>Students</span></h1></div>
<table><thead><tr><th>Roll</th><th>Name</th><th>Branch</th><th>Semester</th><th>Section</th></tr></thead>
<tbody>{% for s in students %}<tr><td>{{ s.roll_number }}</td><td>{{ s.full_name }}</td><td>{{ s.branch }}</td><td>{{ s.semester }}</td><td>{{ s.section }}</td></tr>{% else %}<tr><td colspan="5" style="text-align:center;color:#6b7280;">No students.</td></tr>{% endfor %}</tbody></table>
</div>
</body>
</html>
    ''', students=students)

@app.route('/admin/teachers')
@login_required
@admin_required
def admin_teachers():
    teachers = Teacher.query.all()
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>Teachers - Campusora</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;background:#0a0e27;color:white;display:flex;}
.sidebar{width:260px;min-height:100vh;background:rgba(255,255,255,0.05);padding:30px 20px;border-right:1px solid rgba(255,255,255,0.05);}
.sidebar .logo{font-size:24px;font-weight:bold;color:#a78bfa;padding-bottom:30px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:30px;}
.sidebar .logo span{color:white;}
.sidebar nav a{display:flex;align-items:center;padding:12px 16px;color:#9ca3af;text-decoration:none;border-radius:12px;margin-bottom:4px;transition:all 0.3s;font-size:14px;}
.sidebar nav a:hover{background:rgba(124,58,237,0.15);color:white;}
.sidebar nav a.active{background:rgba(124,58,237,0.2);color:#a78bfa;}
.sidebar nav a .icon{margin-right:12px;}
.main{flex:1;padding:30px 40px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;}
.header h1{font-size:28px;}
.header h1 span{color:#a78bfa;}
table{width:100%;border-collapse:collapse;}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05);}
th{color:#c4b5fd;font-weight:600;}
</style>
</head>
<body>
<div class="sidebar"><div class="logo">CAMPUS<span>ORA</span></div>
<nav>
<a href="/admin/dashboard"><span class="icon">📊</span> Dashboard</a>
<a href="/admin/students"><span class="icon">👨‍🎓</span> Students</a>
<a href="/admin/teachers" class="active"><span class="icon">👨‍🏫</span> Teachers</a>
<a href="/logout"><span class="icon">🚪</span> Logout</a>
</nav></div>
<div class="main"><div class="header"><h1>Manage <span>Teachers</span></h1></div>
<table><thead><tr><th>Employee ID</th><th>Name</th><th>Department</th></tr></thead>
<tbody>{% for t in teachers %}<tr><td>{{ t.employee_id }}</td><td>{{ t.full_name }}</td><td>{{ t.department }}</td></tr>{% else %}<tr><td colspan="3" style="text-align:center;color:#6b7280;">No teachers.</td></tr>{% endfor %}</tbody></table>
</div>
</body>
</html>
    ''', teachers=teachers)

# ===== CREATE DATABASE & RUN =====
if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate (fix for foreign key issues)
        db.drop_all()
        db.create_all()

        if User.query.count() == 0:
            print("📦 Creating sample data...")
            admin = User(username='admin', email='admin@campusora.edu', role='admin')
            admin.set_password('password123')
            db.session.add(admin)

            t_user = User(username='teacher', email='teacher@campusora.edu', role='teacher')
            t_user.set_password('password123')
            db.session.add(t_user)
            db.session.flush()

            teacher = Teacher(user_id=t_user.user_id, employee_id='TCH001', full_name='Dr. Sarah Johnson', department='Computer Science', designation='Professor')
            db.session.add(teacher)

            s_user = User(username='student', email='student@campusora.edu', role='student')
            s_user.set_password('password123')
            db.session.add(s_user)
            db.session.flush()

            student = Student(user_id=s_user.user_id, roll_number='CS2023001', enrollment_number='EN2023001', full_name='John Doe', branch='CSE', semester=3, section='A')
            db.session.add(student)
            db.session.flush()

            subjects = []
            for code, name in [('CS101','Java'),('CS102','DBMS'),('CS103','DSA'),('CS104','Maths'),('CS105','Networks')]:
                s = Subject(subject_code=code, subject_name=name, branch='CSE', semester=3, teacher_id=teacher.teacher_id)
                db.session.add(s)
                subjects.append(s)
            db.session.flush()

            import random
            today = datetime.now().date()
            for i in range(20):
                date = today - timedelta(days=i)
                for sub in subjects:
                    status = 'present' if random.random() > 0.2 else 'absent'
                    db.session.add(Attendance(student_id=student.student_id, subject_id=sub.subject_id, date=date, status=status, marked_by=teacher.teacher_id))

            for sub in subjects:
                m = Marks(student_id=student.student_id, subject_id=sub.subject_id, internal_marks=random.randint(12,19), assignment_marks=random.randint(6,10), exam_marks=random.randint(60,95), semester=3, academic_year='2025-2026')
                m.total_marks = m.internal_marks + m.assignment_marks + m.exam_marks
                m.percentage = round((m.total_marks/130)*100, 2)
                m.grade = 'A' if m.percentage>=90 else 'B' if m.percentage>=80 else 'C' if m.percentage>=70 else 'D' if m.percentage>=60 else 'F'
                db.session.add(m)

            for notice in [('Welcome to Campusora','Campusora is live!','General',False),('Mid-Term Exams','March 1st','Examination',True),('Campus Fest','April 10-12','Events',False)]:
                db.session.add(Notice(title=notice[0], content=notice[1], category=notice[2], is_pinned=notice[3], posted_by=admin.user_id, posted_by_role='admin'))

            db.session.commit()
            print("✅ Database ready!")
            print("   Admin: admin / password123")
            print("   Teacher: teacher / password123")
            print("   Student: student / password123")

    print("🚀 Campusora running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
