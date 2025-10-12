from .check import login_required

from .forms import LoginForm, StudentSignUpForm, UnitEnrollmentForm, CSRFOnlyForm, ResetPasswordRequestForm, ResetPasswordForm
from .check import login_required
from .models import *
from flask import render_template, redirect, url_for, flash, session, current_app, Blueprint
from werkzeug.security import check_password_hash

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
        password = login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and not user.email_verified_at:
            session["pending_verify_email"] = user.email
            flash("Please verify your email first.", "warning")
            return redirect(url_for("otp.verify_page"))
        
        if user and check_password_hash(user.password,password):
            session.clear()
            session.permanent = True # Lifetime based on config 
            session['uid'] = user.user_id  
            session['email'] = user.email
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
                "password": signup_form.password.data,  
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
    user = User.query.filter_by(user_id=session.get('uid')).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login_page"))

    # Get user's latest enrollment update for targeting
    enrollment_update = EnrollmentUpdate.query.filter_by(user_id=user.user_id).order_by(EnrollmentUpdate.update_id.desc()).first()
    degree_type = None
    location = None
    stage = None
    start_date = None
    progress_percentage = 0

    if enrollment_update:
        degree = Enrollment.query.filter_by(degree_code=enrollment_update.degree_code).first()
        degree_type = degree.degree_type if degree else None
        location = enrollment_update.location
        stage = None  # Update if stage is stored elsewhere

        # Estimate start date from earliest EnrollmentUpdate
        earliest_update = EnrollmentUpdate.query.filter_by(user_id=user.user_id).order_by(EnrollmentUpdate.update_id.asc()).first()
        if earliest_update:
            # Assume update_id is a timestamp (as per signup route)
            start_date = datetime.fromtimestamp(earliest_update.update_id)
            # Calculate progress based on degree type
            current_date = datetime.utcnow()
            duration_years = 2 if degree_type == 'masters' else 3
            total_days = duration_years * 365
            days_passed = (current_date - start_date).days
            progress_percentage = min(100, max(0, (days_passed / total_days) * 100))

    # Filter reminders/messages for this user
    reminders = Reminder.query.filter(
        (Reminder.degree_type_target == None) | (Reminder.degree_type_target == degree_type),
        (Reminder.location_target == None) | (Reminder.location_target == location),
        (Reminder.stage_target == None) | (Reminder.stage_target == stage)
    ).order_by(Reminder.scheduled_at.asc()).all()

    messages = Message.query.filter(
        (Message.degree_type_target == None) | (Message.degree_type_target == degree_type),
        (Message.location_target == None) | (Message.location_target == location),
        (Message.stage_target == None) | (Message.stage_target == stage)
    ).order_by(Message.scheduled_at.asc().nullslast()).all()

    wellbeing_posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
    contacts = SupportContact.query.order_by(SupportContact.service_type).all()
    user_units = Unit.query.filter_by(user_id=user.user_id).all()

    return render_template(
        "student_dashboard.html",
        first_name=user.first_name,
        user=user,
        enrollment_update=enrollment_update,
        degree_type=degree_type,
        start_date=start_date,
        progress_percentage=round(progress_percentage, 1),
        reminders=reminders,
        messages=messages,
        wellbeing_posts=wellbeing_posts,
        contacts=contacts,
        user_units=user_units,
        unit_enroll_form=UnitEnrollmentForm(),
        unit_unenroll_form=CSRFOnlyForm()
    )

@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", first_name="John", last_name="Doe")

@main_bp.route("/preview_emails/<int:user_id>")
@login_required
def preview_email(user_id):
    def get_student_updates(user_id, lookahead_weeks=2):
        user = User.query.get(user_id)
        if not user:
            return None, None

        enrollment_update = EnrollmentUpdate.query.filter_by(user_id=user_id).first()
        if not enrollment_update:
            return None, None

        degree_code = enrollment_update.degree_code
        current_week = enrollment_update.current_week

        messages = Message.query.filter(
            Message.degree_code == degree_code,
            Message.week_released > current_week,
            Message.week_released <= current_week + lookahead_weeks
        ).order_by(Message.week_released.asc()).all()

        assessments = Assessments.query.filter(
            Assessments.degree_code == degree_code,
            Assessments.due_week > current_week,
            Assessments.due_week <= current_week + lookahead_weeks
        ).order_by(Assessments.due_week.asc()).all()

        return messages, assessments
    messages, assessments = get_student_updates(user_id)
    return render_template("weekly_email.html", messages=messages, assessments=assessments)

# Show reset password request form
@main_bp.get("/reset-password")
def reset_password():
    return render_template("reset_password.html", form=ResetPasswordRequestForm())

# Handle reset password form submission
@main_bp.post("/reset-password")
def reset_password_submit():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        svc = current_app.extensions["email_otp"]
        svc.send_otp(form.email.data)
        session["password_verify_email"] = form.email.data
        
        flash("We emailed you a 6-digit verification code.", "info")
        return redirect(url_for("otp.verify_password_page"))   # <-- go to OTP input page
    return render_template("reset_password.html", form=form)
    
@main_bp.get("/update-password")
def update_password_page():
    if "password_verify_email" not in session:
        flash("Unauthorized access. Please request a new password reset.", "danger")
        return redirect(url_for("main.reset_password"))
    return render_template("update_password.html", form=ResetPasswordForm())

@main_bp.post("/update-password")
def update_password_submit():
    form = ResetPasswordForm()
    if not form.validate_on_submit():
        return render_template("update_password.html", form=form)

    if form.password.data != form.confirm_password.data:
        flash("Passwords do not match.", "danger")
        return render_template("update_password.html", form=form)

    email = session.get("password_verify_email")
    if not email:
        flash("Session expired. Please request password reset again.", "warning")
        return redirect(url_for("main.reset_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("main.reset_password"))

    # Save new password
    user.password = generate_password_hash(form.password.data)
    db.session.commit()

    # Clear session state
    session.pop("password_verify_email", None)

    flash("Password updated successfully. You can now log in.", "success")
    return redirect(url_for("main.login_page"))
