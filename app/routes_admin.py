from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app 
from .forms import ChangeRightForm, EmailEditor, DeleteAccountForm
from .models import Right, Message, User
from .check import login_and_rights_required
from . import db

# Name the blueprint
admin_bp = Blueprint('admin', __name__,url_prefix='/admin')

@admin_bp.get("/admin-dashboard")
@login_and_rights_required(1) # Put permission number according(.e.g admin)
def admin_dashboard():
    return render_template("admin_dashboard.html", 
                           form=EmailEditor(), 
                           form_right=ChangeRightForm(),
                           form_delete=DeleteAccountForm()
                           )

@admin_bp.post("/admin-dashboard")
@login_and_rights_required(1)
def admin_dashboard_post():
    if request.method == "POST":
        flash("Message updated!", "success")
        message_content = request.form["message"]

@admin_bp.post("/admin-dashboard/change_right")
@login_and_rights_required(1)
def change_right():
    form = ChangeRightForm()
    if form.validate_on_submit():
        uid = form.user_id.data
        new_right = form.permission_number.data

        row = Right.query.filter_by(user_id=uid).first()
        if row:
            row.permission_number = new_right
            msg = f"Updated user {uid} to permission {new_right}."
        else:
            db.session.add(Right(user_id=uid, permission_number=new_right))
            msg = f"Added permission {new_right} for user {uid}."
        db.session.commit()
        flash(msg, "success")
        return redirect(url_for("admin.admin_dashboard"))

    email_form = EmailEditor()
    return render_template("admin_dashboard.html", form=email_form, form_right=form)

@admin_bp.get("/messages/select")
@login_and_rights_required(1) # Put permission number according(.e.g admin)
def select_message():
    messages = Message.query.order_by(Message.week_released.asc()).all()
    if not messages:
        flash("No messages available. Please create a new message.", "info")
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("select_message.html", messages=messages)

@admin_bp.post("/email-editor")
@login_and_rights_required(1)
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
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.get("/email-editor")
@login_and_rights_required(1) # Put permission number according(.e.g admin)
def email_editor():
    message_id = request.args.get("message_id")
    message_content = ""
    if message_id:
        message = Message.query.get(message_id)
        if message:
            message_content = message.content
    return render_template("email_editor.html", message_content=message_content)

@admin_bp.post("/delete_account")
@login_and_rights_required(1)  
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if user:
            # Remove from Mailchimp
            mailchimp = current_app.extensions["mailchimp"]
            mailchimp.delete_member(user.email)
            # Remove from DB
            db.session.delete(user)
            db.session.commit()
            flash("User deleted from database and Mailchimp.", "success")
        else:
            flash("User not found.", "danger")
    else:
        flash("Invalid form submission.", "danger")
    return redirect(url_for("admin.admin_dashboard"))