from .forms import LoginForm, StudentSignUpForm
from app import db
from .models import *
from flask import render_template, redirect, url_for, flash, session, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .check import login_required

main_bp = Blueprint("main", __name__, url_prefix='')

@main_bp.get("/")
def index():
    return render_template("welcome.html")

@main_bp.get("/logout")
def logout():
    session.pop("uid", None)
    flash("Logged out.", "info")
    return redirect(url_for("main.login_page"))

@main_bp.get("/login")
def login_page():
    return render_template("login.html", login_form=LoginForm())

@main_bp.get("/signup")
def sign_up():
    return render_template("signup.html", signup_form=StudentSignUpForm())

@main_bp.post("/login")
def login():	
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_id = login_form.user_id.data
        password= login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and not user.email_verified_at:
            session["pending_verify_email"] = user.email
            flash("Please verify your email first.", "warning")
            return redirect(url_for("otp.verify_page"))
        
        if user and check_password_hash(user.password,password):
            session.clear()
            session.permanent = True # Lifetime based on config 
            session['uid'] = user.user_id  
            has_admin_right = Right.query.filter_by(
                                    user_id=user.user_id,
                                    permission_number=1 # Put admin number according(.e.g admin)
            ).first() is not None
            flash("Login successful", "success")
            return redirect(url_for("admin.admin_dashboard" if has_admin_right else "main.student_dashboard"))
        
    flash("Invalid username or password", "danger")
    return redirect(url_for("main.login_page"))

@main_bp.post("/signup")
def signup():
    signup_form = StudentSignUpForm()

    if signup_form.validate_on_submit():
        # Uniqueness checks
        if User.query.filter_by(user_id=signup_form.user_id.data).first():
            signup_form.user_id.errors.append("ID has already taken or unvalid.")
        if User.query.filter_by(email=signup_form.email.data).first():
            signup_form.email.errors.append("Email already registered.")

        if not (signup_form.user_id.errors or signup_form.email.errors):
            session["pending_signup"] = {
                "user_id": signup_form.user_id.data,
                "first_name": signup_form.first_name.data,
                "last_name": signup_form.last_name.data,
                "email": signup_form.email.data,
                "password": signup_form.password.data,  # hash later
                "degree_code": signup_form.degree_code.data,
                "location": signup_form.location.data,
                "enrollment_status": signup_form.enrollment_status.data,
            }
            
            # OTP
            svc = current_app.extensions["email_otp"]
            svc.send_otp(signup_form.email.data)
            session["pending_verify_email"] = signup_form.email.data
            flash("We emailed you a 6-digit verification code.", "info")
            return redirect(url_for("otp.verify_page"))

    # Failed validation
    flash("Invalid or existing credentials!", "danger")
    return render_template("signup.html", signup_form=signup_form)

@main_bp.route("/student-dashboard")
@login_required
def student_dashboard():     
    return render_template("student_dashboard.html")

# Helper Function to fetch messages+assessments for a user
def get_student_updates(user_id, lookahead_weeks=2):
    user = User.query.get(user_id)
    if not user:
        return None, None

    enrollment_update = EnrollmentUpdate.query.filter_by(user_id=user_id).first()
    if not enrollment_update:
        return None, None

    degree_code = enrollment_update.degreeCode
    current_week = enrollment_update.current_week

    messages = Message.query.filter(
        Message.degreeCode == degree_code,
        Message.week_released > current_week,
        Message.week_released <= current_week + lookahead_weeks
    ).order_by(Message.week_released.asc()).all()

    assessments = Assessments.query.filter(
        Assessments.degreeCode == degree_code,
        Assessments.due_week > current_week,
        Assessments.due_week <= current_week + lookahead_weeks
    ).order_by(Assessments.due_week.asc()).all()

    return messages, assessments

@main_bp.route("/preview_emails/<int:user_id>")
@login_required
def preview_email(user_id):
    messages, assessments = get_student_updates(user_id)
    return render_template("weekly_email.html", messages=messages, assessments=assessments)
