from flask import Blueprint, url_for, redirect, flash, session, current_app
from .check import login_required
from .forms import UnitEnrollmentForm, CSRFOnlyForm
from .models import Unit, db

unit_bp = Blueprint("unit", __name__, url_prefix="/units")
@unit_bp.post("/enroll")
@login_required
def enroll():
    form = UnitEnrollmentForm()
    mailchimp = current_app.extensions["mailchimp"]
    if form.validate_on_submit():
        unit_code = form.unit_code.data.strip().upper()
        if Unit.query.filter_by(user_id=session['uid'], unit_code=unit_code).first():
            flash(f"Already enrolled in {unit_code}.", "info")
            return redirect(url_for("main.student_dashboard"))
        unit_add = Unit(user_id=session['uid'], unit_code=unit_code)
        db.session.add(unit_add)
        db.session.commit()
        print(session['email'], unit_code)
        mailchimp.add_unit_tag(session['email'], unit_code)
        flash(f"Enrolled in {unit_code} successfully!", "success")
    return redirect(url_for("main.student_dashboard"))

@unit_bp.post("/unenroll/<string:unit_code>")
@login_required
def unenroll(unit_code):
    print('hello',flush=True)
    form = CSRFOnlyForm()
    mailchimp = current_app.extensions["mailchimp"]
    if form.validate_on_submit():
        code = unit_code.strip().upper()
        print(code)
        link = Unit.query.filter_by(user_id=session['uid'], unit_code=code).first()
        print(link)
        if link:
            db.session.delete(link)
            db.session.commit()
            print(session['email'], unit_code)
            mailchimp.remove_unit_tag(session['email'], unit_code)
        flash(f"Unenrolled from {unit_code} successfully!", "success")
    else:
        flash(f"Unit {unit_code} not found in your enrollments.", "danger")
    return redirect(url_for("main.student_dashboard"))