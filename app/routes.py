from .forms import LoginForm, StudentSignUpForm
from app import app, db
from .models import *
from flask import render_template, redirect, url_for, flash
import time

@app.get("/")
def index():
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
        password = login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and user.password == password:  
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

        if not (signup_form.user_id.errors or signup_form.email.errors):
            user = User(
                user_id = signup_form.user_id.data,
                first_name = signup_form.first_name.data,
                last_name = signup_form.last_name.data,
                email = signup_form.email.data,
                password = signup_form.password.data,
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

            enrollment = Enrollment(
                degreeCode = signup_form.degree_code.data,
                degree_type = signup_form.degree_type.data
            )

            db.session.add(user)
            db.session.add(enrollment_update)
            db.session.add(enrollment)
            db.session.commit()  
            flash("Account created successfully. You can log in now.", "success")
            return redirect(url_for("login_page"))

    # Failed validation
    flash("Invalid or existing credentials!", "danger")
    return render_template("signup.html", signup_form=signup_form)

@app.route("/student-dashboard", methods=["GET"])
def student_dashboard():         
    return render_template("student_dashboard.html")
