from .forms import LoginForm, StudentSignUpForm
from app import app, db
from .models import *
from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
import time
from functools import wraps #decorators behave
from flask_wtf.csrf import generate_csrf


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
    return render_template("welcome.html")

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
        user_id = login_form.user_id.data
        password= login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and check_password_hash(user.password,password):
            session.clear()
            session.permanent = True # Lifetime based on config 
            session['uid'] = user_id  
            flash("Login successful", "success")
            return redirect(url_for("student_dashboard"))
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

        '''
        Future checks for degree code existence
        '''
        
        if not (signup_form.user_id.errors or signup_form.email.errors):
            user = User(
                user_id = signup_form.user_id.data,
                first_name = signup_form.first_name.data,
                last_name = signup_form.last_name.data,
                email = signup_form.email.data,
                password = generate_password_hash(signup_form.password.data),
            )

            enrollment_update = EnrollmentUpdate(
                update_id = int(time.time()), # Need verifications
                user_id = signup_form.user_id.data,
                degreeCode = signup_form.degree_code.data,
                location = signup_form.location.data,
                initialisation = False, # Need verfications
                study_mode = signup_form.enrollment_status.data,
                current_week = 0, # Need verifications 
            )

            db.session.add(user)
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
    return render_template("student_dashboard.html")


@app.get("/admin-dashboard")
def admin_dashboard():
    messages = Message.query.order_by(Message.week_released.asc()).all() #this is because the select messages is rendered internally
    return render_template("admin_dashboard.html", csrf_token=generate_csrf(), messages=messages)

@app.post("/admin-dashboard")
def admin_dashboard_post():
    if request.method == "POST":
        flash("Message updated!", "success")
        message_content = request.form["message"]


@app.post("/email-editor")
def save_email_message():
    message_id = request.form.get("message_id")
    content = request.form.get("message_content")
    if message_id:
        # Update existing message
        message = Message.query.get(message_id)
        if message:
            message.content = content
            db.session.commit()
            flash("Message updated!", "success")
        else:
            flash("Message not found.", "danger")
    else:
        # Create new message
        degreeCode = request.form.get("degreeCode")
        week_released = request.form.get("week_released")
        if degreeCode and week_released:
            new_message = Message(degreeCode=degreeCode, content=content, week_released=week_released)
            db.session.add(new_message)
            db.session.commit()
            flash("New message created!", "success")
        else:
            flash("Degree code and week are required for new messages.", "danger")
    return redirect(url_for("admin_dashboard"))

@app.get("/messages/select")
def select_message():

    messages = Message.query.order_by(Message.week_released.asc()).all()
    if not messages:
        flash("No messages available. Please create a new message.", "info")
        return redirect(url_for("admin_dashboard"))
    return render_template("select_message.html", messages=messages)

@app.get("/email-editor")
def email_editor():
    message_id = request.args.get("message_id")
    message_content = ""
    if message_id:
        message = Message.query.get(message_id)
        if message:
            message_content = message.content
    return render_template("email_editor.html", message_content=message_content)