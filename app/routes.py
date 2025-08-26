from .forms import LoginForm, StudentSignUpForm
from app import app, db
from .models import *
from flask import render_template, redirect, url_for, flash, request
import time

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():	
    login_form = LoginForm()
    signup_form = StudentSignUpForm()

    if request.method == "POST" and login_form.validate_on_submit():
        user_id = login_form.user_id.data
        password = login_form.password.data

        user = User.query.filter_by(user_id=user_id).first()
        if user and user.password == password:  
            flash("Login successful", "success")
            return redirect(url_for("student_dashboard"))
        flash("Invalid username or password", "danger")

    return render_template("login.html",
                           login_form=login_form,
                           signup_form=signup_form,
                           show_tab="login")


@app.route("/signup", methods=["POST"])
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
                degree_code = signup_form.degree_code.data,
                location = signup_form.location.data,
                initialisation = False, # Need verfications
                study_mode = signup_form.enrollment_status.data,
                current_week = 0, # Need verifications 
                locaion = signup_form.location
            )

            enrollment = Enrollment(
                degreeCode = signup_form.degree_code.data,
                degree_type = signup_form.degree_type
            )

            try:
                db.session.add(user)
                db.session.add(enrollment_update)
                db.session.add(enrollment)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("DB ERROR:", e)
                
            return redirect(url_for("login"))

    # Failed validation
    return render_template("login.html",
                           login_form=LoginForm(),
                           signup_form=signup_form,
                           show_tab="signup")

@app.route("/student-dashboard", methods=["GET"])
def student_dashboard():         
    return render_template("student_dashboard.html")
