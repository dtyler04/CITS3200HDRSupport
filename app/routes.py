from .forms import LoginForm, StudentSignUpForm, AdminMessageForm, AdminReminderForm, SupportPostForm, SupportContactForm
from app import app, db
from .models import *
from flask import render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import time
from functools import wraps #decorators behave
import os
from datetime import datetime
from flask import request, current_app, send_from_directory
from werkzeug.utils import secure_filename

ALLOWED_EXT = {'png','jpg','jpeg','gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'uid' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    return wrapped

@app.get("/")
def index():
    return redirect(url_for("login_page"))

@app.get("/logout")
def logout():
    session.pop("uid", None)
    flash("Logged out.", "info")
    return redirect(url_for("login_page"))

@app.get("/login")
def login_page():
    login_form = LoginForm()
    return render_template("login.html", login_form=login_form)

@app.get("/signup")
def sign_up():
    signup_form = StudentSignUpForm()
    return render_template("signup.html", signup_form=signup_form)


@app.post("/login")
def login():	
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_id = login_form.user_id.data           # changed code: cast to int
        password = login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and check_password_hash(user.password,password):
            session.clear()
            session.permanent = True # Lifetime based on config
            session['uid'] = user.user_id  
            has_admin_right = Right.query.filter_by(
                                    user_id=user.user_id,
                                    permission_number=1 # Put admin number according(.e.g admin)
            ).first() is not None
            flash("Login successful", "success")
            return redirect(url_for("admin_dashboard" if has_admin_right else "student_dashboard"))
 
    flash("Invalid username or password", "danger")
    return redirect(url_for("login_page"))

@app.post("/signup")
def signup():
    signup_form = StudentSignUpForm()

    if signup_form.validate_on_submit():
        # Uniqueness checks
        if User.query.filter_by(user_id=signup_form.user_id.data).first():
            signup_form.user_id.errors.append("ID has already taken or unvalid.")
        if User.query.filter_by(email=signup_form.email.data).first():
            signup_form.email.errors.append("Email already registered.")

        if not (signup_form.user_id.errors or signup_form.email.errors):
            user = User(
                user_id = signup_form.user_id.data,              # changed code: cast to int
                first_name = signup_form.first_name.data,
                last_name = signup_form.last_name.data,
                email = signup_form.email.data,
                password = generate_password_hash(
                    signup_form.password.data,
                    method='pbkdf2:sha256'                            # changed code: force PBKDF2
                ),
        )

            enrollment_update = EnrollmentUpdate(
                update_id = int(time.time()), # Need verifications
                user_id = signup_form.user_id.data,             # changed code: cast to int
                degreeCode = signup_form.degree_code.data,
                location = signup_form.location.data,
                initialisation = False, # Need verfications
                study_mode = signup_form.enrollment_status.data,
                current_week = 0, # Need verifications 
            )
            x = Right(user_id=signup_form.user_id.data, permission_number=0)
            db.session.add(user)
            db.session.add(x)
            db.session.add(enrollment_update)
            db.session.commit()  
            flash("Account created successfully. You can log in now.", "success")
            return redirect(url_for("login_page"))

    # Failed validation
    flash("Invalid or existing credentials!", "danger")
    return render_template("signup.html", signup_form=signup_form)


@app.route("/student-dashboard")
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
    if enrollment_update:
        degree = Enrollment.query.filter_by(degreeCode=enrollment_update.degreeCode).first()
        degree_type = degree.degree_type if degree else None
        location = enrollment_update.location
        # You may want to store 'stage' in EnrollmentUpdate or elsewhere
        stage = None  # Set this if you have it

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

    return render_template(
        "student_dashboard.html",
        first_name=user.first_name,
        reminders=reminders,
        messages=messages,
        wellbeing_posts=wellbeing_posts,
        contacts=contacts
    )

@app.route("/profile")
def profile():
    return render_template("profile.html", first_name="John", last_name="Doe")


@app.get("/admin")
@login_required
def admin_dashboard():
    # rudimentary admin check (in future use permissions). For now assume any logged-in user is admin if they have a Right with Admin permission
    user = User.query.filter_by(user_id=session.get('uid')).first()
    # load forms
    msg_form = AdminMessageForm()
    rem_form = AdminReminderForm()
    post_form = SupportPostForm()
    contact_form = SupportContactForm()

    messages = Message.query.order_by(Message.scheduled_at.desc().nullslast()).all()
    reminders = Reminder.query.order_by(Reminder.scheduled_at.desc()).all()
    posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
    contacts = SupportContact.query.order_by(SupportContact.service_type).all()

    return render_template("admin_dashboard.html",
                           msg_form=msg_form, rem_form=rem_form, post_form=post_form, contact_form=contact_form,
                           messages=messages, reminders=reminders, posts=posts, contacts=contacts)

@app.post("/admin/message/create")
@login_required
def admin_create_message():
    form = AdminMessageForm()
    if form.validate_on_submit():
        sched = None
        if form.scheduled_at.data:
            try:
                sched = datetime.fromisoformat(form.scheduled_at.data)
            except Exception:
                sched = None
        m = Message(
            title = form.title.data,
            message_content = form.message_content.data,
            scheduled_at = sched,
            degree_type_target = form.degree_type_target.data or None,
            location_target = form.location_target.data or None,
            stage_target = form.stage_target.data or None
        )
        db.session.add(m)
        db.session.commit()
        flash("Message created.", "success")
    else:
        flash("Invalid message data.", "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/reminder/create")
@login_required
def admin_create_reminder():
    form = AdminReminderForm()
    if form.validate_on_submit():
        try:
            sched = datetime.fromisoformat(form.scheduled_at.data)
        except Exception:
            flash("Invalid datetime format for reminder.", "danger")
            return redirect(url_for("admin_dashboard"))
        r = Reminder(
            title=form.title.data,
            content=form.content.data,
            scheduled_at=sched,
            degree_type_target = form.degree_type_target.data or None,
            location_target = form.location_target.data or None,
            stage_target = form.stage_target.data or None
        )
        db.session.add(r)
        db.session.commit()
        flash("Reminder scheduled.", "success")
    else:
        flash("Invalid reminder data.", "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/support/post/create")
@login_required
def admin_create_post():
    form = SupportPostForm()
    if form.validate_on_submit():
        filename = None
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, fname))
            filename = fname
        post = SupportPost(title=form.title.data, content=form.content.data, image_filename=filename)
        db.session.add(post)
        db.session.commit()
        flash("Support post created.", "success")
    else:
        flash("Invalid support post.", "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/contact/create")
@login_required
def admin_create_contact():
    form = SupportContactForm()
    if form.validate_on_submit():
        c = SupportContact(service_type=form.service_type.data, name=form.name.data, info=form.info.data)
        db.session.add(c)
        db.session.commit()
        flash("Contact saved.", "success")
    else:
        flash("Invalid contact data.", "danger")
    return redirect(url_for("admin_dashboard"))

# serve uploaded files (optional)
@app.get('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config.get('UPLOAD_FOLDER'), filename)
