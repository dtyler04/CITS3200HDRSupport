# app/routes_OTP.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import db
from .models import User, Right, EnrollmentUpdate
from .forms import VerifyOTPForm, ResendOTPForm  

otp_bp = Blueprint("otp", __name__, url_prefix="/otp")

def _svc():
    return current_app.extensions["email_otp"]

@otp_bp.get("/verify")
def verify_page():
    email = session.get("pending_verify_email")
    if not email:
        flash("No email pending verification. Please sign up first.", "warning")
        return redirect(url_for("main.signup_page"))
    return render_template("verify_email.html",
                           form=VerifyOTPForm(),
                           resend_form=ResendOTPForm())

@otp_bp.post("/verify")
def verify_submit():
    form = VerifyOTPForm()
    resend_form = ResendOTPForm()

    if not form.validate_on_submit():
        flash("Enter the 6-digit code.", "danger")
        return render_template("verify_email.html", form=form, resend_form=resend_form)

    email = session.get("pending_verify_email") or resend_form.email.data
    if not email:
        flash("No email pending verification. Please sign up again.", "warning")
        return redirect(url_for("main.signup_page"))

    if not _svc().verify_otp(email, form.code.data):
        flash("Invalid or expired code.", "danger")
        return render_template("verify_email.html", form=form, resend_form=resend_form)

    pending = session.pop("pending_signup", None)
    if not pending or pending.get("email") != email:
        flash("Session expired or invalid. Please sign up again.", "danger")
        return redirect(url_for("main.signup_page"))

    user = User(
        user_id=pending["user_id"],
        first_name=pending["first_name"],
        last_name=pending["last_name"],
        email=pending["email"],
        password=generate_password_hash(pending["password"]),
        email_verified_at=datetime.utcnow()
    )
    right = Right(
        user_id=user.user_id,
        permission_number=0  # 0 for student
    )

    enrollment_update = EnrollmentUpdate(
        user_id=user.user_id,
        degreeCode=pending["degree_code"],
        location=pending["location"],
        initialisation=False,
        study_mode=pending["enrollment_status"],
        current_week=0
    )

    db.session.add_all([user, right, enrollment_update])
    db.session.commit()
    session.pop("pending_verify_email", None)

    mailchimp = current_app.extensions["mailchimp"]
    try:
        mailchimp.add_member(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status="subscribed"
        )
    except Exception as e:
        flash("Warning: Could not subscribe to mailing list.", "warning")

    flash("Email verified! You can now log in.", "success")
    return redirect(url_for("main.login_page"))

@otp_bp.post("/resend")
def resend_submit():
    resend_form = ResendOTPForm()

    if not resend_form.validate_on_submit():
        flash("Something went wrong. Please try again.", "danger")
        return redirect(url_for("otp.verify_page"))

    email = session.get("pending_verify_email")
    if not email:
        flash("No email to resend to.", "warning")
        return redirect(url_for("main.signup_page"))

    if not _svc().send_otp(email):
        flash("Could not resend verification code. Please try again.", "danger")
        return redirect(url_for("otp.verify_page"))

    flash("We sent you a new 6-digit code.", "info")
    return redirect(url_for("otp.verify_page"))

@otp_bp.post("/verify-code")
def verify_code():
    form = VerifyOTPForm()
    if form.validate_on_submit():
        email = session.get("pending_verify_email")
        if not email:
            flash("No email pending verification. Please sign up first.", "warning")
            return redirect(url_for("main.signup_page"))

        if _svc().verify_otp(email, form.code.data):
            flash("Code verified successfully!", "success")
            return redirect(url_for("main.login_page"))
        else:
            flash("Invalid or expired code.", "danger")
    else:
        flash("Enter the 6-digit code.", "danger")
    return redirect(url_for("otp.verify_page"))

# Create another route for verifying reset password
# When approved, send a request form to reset password
@otp_bp.post("/verify-reset")
def verify_reset_submit():
    """Verify OTP for password reset."""
    form = VerifyOTPForm()

    if not form.validate_on_submit():
        flash("Enter the 6-digit code.", "danger")
        return redirect(url_for("main.reset_password"))

    email = session.get("pending_verify_email")
    if not email:
        flash("No email pending verification. Please request reset again.", "warning")
        return redirect(url_for("main.reset_password"))

    if not _svc().verify_otp(email, form.code.data):
        flash("Invalid or expired code.", "danger")
        return redirect(url_for("main.reset_password"))

    # OTP verified → allow user to set new password
    session["reset_password_email"] = email
    session.pop("pending_verify_email", None)
    flash("OTP verified. Please set your new password.", "success")
    return redirect(url_for("main.update_password"))