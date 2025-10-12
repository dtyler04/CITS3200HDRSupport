from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app, send_from_directory, make_response, session
from .forms import ChangeRightForm, EmailEditor, DeleteAccountForm, AdminMessageForm, AdminReminderForm, SupportPostForm, SupportContactForm, CSRFOnlyForm, AssessmentForm
from .models import Right, Message, User, Reminder, SupportPost, SupportContact, Assessments
from .check import login_and_rights_required, login_required
from . import db
from werkzeug.utils import secure_filename
from datetime import datetime
import random, os

# Name the blueprint
admin_bp = Blueprint('admin', __name__,url_prefix='/admin')

@admin_bp.get("/admin-dashboard")
@login_and_rights_required(1) # Put permission number according(.e.g admin)
def admin_dashboard():
    messages = Message.query.order_by(Message.scheduled_at.desc().nullslast()).all()
    reminders = Reminder.query.order_by(Reminder.scheduled_at.desc()).all()
    posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
    contacts = SupportContact.query.order_by(SupportContact.service_type).all()
    assessments = Assessments.query.order_by(Assessments.due_week).all()

    return render_template("admin/admin_dashboard.html", 
                           csrf_form=CSRFOnlyForm(),
                           form=EmailEditor(), 
                           form_right=ChangeRightForm(),
                           form_delete=DeleteAccountForm(),
                           msg_form=AdminMessageForm(), rem_form=AdminReminderForm(), post_form=SupportPostForm(), contact_form=SupportContactForm(),
                           assessment_form=AssessmentForm(),
                           messages=messages, reminders=reminders, posts=posts, contacts=contacts, assessments=assessments
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
    return render_template("admin/admin_dashboard.html", form=email_form, form_right=form)

@admin_bp.get("/messages/select")
@login_and_rights_required(1) # Put permission number according(.e.g admin)
def select_message():
    messages = Message.query.order_by(Message.week_released.asc()).all()
    if not messages:
        flash("No messages available. Please create a new message.", "info")
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("select_message.html", messages=messages)

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

@admin_bp.post("/message/create")
@login_and_rights_required(1)
def admin_create_message():
    form = AdminMessageForm()
    created_ok = False
    if form.validate_on_submit():
        try:
            sched = None
            if form.scheduled_at.data:
                try:
                    sched = datetime.fromisoformat(form.scheduled_at.data)
                except ValueError:
                    current_app.logger.warning(f"Invalid datetime format: {form.scheduled_at.data}")
                    sched = None

            m = Message(
                title=form.title.data,
                content=form.message_content.data,
                degree_code="ALL",  # Placeholder, adjust as needed
                week_released=1,  # Placeholder, adjust as needed
                scheduled_at=sched,
                degree_type_target=form.degree_type_target.data or None,
                location_target=form.location_target.data or None,
                stage_target=form.stage_target.data or None
            )

            db.session.add(m)
            db.session.commit()

            flash("Message created successfully.", "success")
            current_app.logger.info(f"Message created: {m.title} by user {session.get('uid')}")
            created_ok = True

        except Exception as e:
            db.session.rollback()
            flash("Error creating message. Please try again.", "danger")
            current_app.logger.error(f"Error creating message: {e}")
    else:
        flash("Invalid message data.", "danger")
        current_app.logger.warning(f"Invalid form data for message creation: {form.errors}")

    # If HTMX request, return the updated history partial
    if request.headers.get("HX-Request") == "true":
        messages = Message.query.order_by(Message.scheduled_at.desc().nullslast()).all()
        reminders = Reminder.query.order_by(Reminder.scheduled_at.desc()).all()
        html = render_template("admin/_history.html", messages=messages, reminders=reminders) + \
               render_template("admin/_flashes.html")
        resp = make_response(html)
        if created_ok:
            resp.headers["HX-Trigger"] = "form-success"
        return resp

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/reminder/create")
@login_and_rights_required(1)
def admin_create_reminder():
    form = AdminReminderForm()
    created_ok = False
    if form.validate_on_submit():
        try:
            sched = datetime.fromisoformat(form.scheduled_at.data)
        except Exception:
            flash("Invalid datetime format for reminder.", "danger")
            return redirect(url_for("admin.admin_dashboard"))
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
        created_ok = True
    else:
        flash("Invalid reminder data.", "danger")
    # HTMX request -> return updated history list
    if request.headers.get("HX-Request") == "true":
        messages = Message.query.order_by(Message.scheduled_at.desc().nullslast()).all()
        reminders = Reminder.query.order_by(Reminder.scheduled_at.desc()).all()
        html = render_template("admin/_history.html", messages=messages, reminders=reminders) + \
               render_template("admin/_flashes.html")
        resp = make_response(html)
        if created_ok:
            resp.headers["HX-Trigger"] = "form-success"
        return resp
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/support_post/create")
@login_and_rights_required(1)
def admin_create_post():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    form = SupportPostForm()
    created_ok = False
    if form.validate_on_submit():
        filename = None
        file = form.image.data
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, fname))
            filename = fname

        units = getattr(form.unit_target, "unit_list", None)
        unit_target_str = "" if units is None else " ".join(units) # None means "all units"
        post = SupportPost(title=form.title.data, content=form.content.data, image_filename=filename,unit_target=unit_target_str)
        db.session.add(post)
        db.session.commit()
        flash("Support post created.", "success")
        created_ok = True
    else:
        flash("Invalid support post.", "danger")
    # HTMX request -> return updated support content partial
    if request.headers.get("HX-Request") == "true":
        posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
        contacts = SupportContact.query.order_by(SupportContact.service_type).all()
        html = render_template("admin/_support_content.html", posts=posts, contacts=contacts, csrf_form=CSRFOnlyForm()) + \
                render_template("admin/_flashes.html")
        resp = make_response(html)
        if created_ok:
            resp.headers["HX-Trigger"] = "form-success"
        return resp
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/support_post/<int:post_id>/delete")
@login_and_rights_required(1)
def admin_delete_post(post_id):
    form = CSRFOnlyForm()
    if not form.validate_on_submit():
        flash("Invalid delete request.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    post = db.session.get(SupportPost, post_id)
    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    # optional: remove image file from disk
    if post.image_filename:
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], post.image_filename)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    db.session.delete(post)
    db.session.commit()
    flash("Support post deleted.", "success")
    return "", 200 # Return empty response for HTMX

@admin_bp.post("/contact/create")
@login_and_rights_required(1)
def admin_create_contact():
    form = SupportContactForm()
    created_ok = False
    if form.validate_on_submit():
        units = getattr(form.unit_target, "unit_list", None)
        unit_target_str = "" if units is None else " ".join(units)
        contact = SupportContact(
            contact_id=random.randint(1, 10000), # Double check, temporary
            service_type=form.service_type.data.strip(),
            name=form.name.data.strip(), 
            info=form.info.data.strip(),
            unit_target=unit_target_str
        )
        db.session.add(contact)
        db.session.commit()
        flash("Support contact created.", "success")
        created_ok = True
    else:
        flash("Invalid support contact.", "danger")
    # HTMX request -> return updated support content partial
    if request.headers.get("HX-Request") == "true":
        posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
        contacts = SupportContact.query.order_by(SupportContact.service_type).all()
        html = render_template("admin/_support_content.html", posts=posts, contacts=contacts, csrf_form=CSRFOnlyForm()) + \
               render_template("admin/_flashes.html")
        resp = make_response(html)
        if created_ok:
            resp.headers["HX-Trigger"] = "form-success"
        return resp
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/assessment/create")
@login_and_rights_required(1)
def admin_create_assessment():
    form = AssessmentForm()
    if form.validate_on_submit():
        try:
            assessment = Assessments(
                title=form.title.data,
                description=form.description.data,
                degree_code=form.degree_code.data,
                due_week=form.due_week.data
            )
            db.session.add(assessment)
            db.session.commit()
            flash(f"Assessment '{form.title.data}' created successfully for week {form.due_week.data}!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating assessment: {str(e)}", "danger")
    else:
        flash("Invalid assessment data. Please check your input.", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/assessment/<int:assessment_id>/delete")
@login_and_rights_required(1)
def admin_delete_assessment(assessment_id):
    assessment = Assessments.query.get_or_404(assessment_id)
    try:
        db.session.delete(assessment)
        db.session.commit()
        flash(f"Assessment '{assessment.title}' deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting assessment: {str(e)}", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.post("/contact/<int:contact_id>/delete")
@login_and_rights_required(1)
def admin_delete_contact(contact_id):
    form = CSRFOnlyForm()
    if not form.validate_on_submit():
        flash("Invalid delete request.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    c = db.session.get(SupportContact, contact_id)
    if not c:
        flash("Contact not found.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    db.session.delete(c)
    db.session.commit()
    flash("Support contact deleted.", "success")
    return "", 200 # Return empty response for HTMX

@admin_bp.get("uploads/<path:filename>")
@login_and_rights_required(1)
def uploaded_file(filename):
    return send_from_directory(current_app.config.get('UPLOAD_FOLDER'), filename)

@admin_bp.get("/tinymce-editor")
@login_and_rights_required(1)
def tinymce_editor():
    """TinyMCE rich text editor page"""
    return render_template("tinyMCE.html")

@admin_bp.post("/tinymce-editor")
@login_and_rights_required(1)
def save_tinymce_content():
    """Handle TinyMCE form submission"""
    # Validate CSRF token
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash("CSRF token validation failed. Please try again.", "error")
        return redirect(url_for('main.admin_dashboard'))
    
    content = request.form.get('content', '')
    title = request.form.get('title', 'Untitled')
    degree_code = request.form.get('degree_code', 'GENERAL')
    week_released = request.form.get('week_released', 1)
    
    # Handle new targeting fields
    scheduled_at = request.form.get('scheduled_at', None)
    degree_type_target = request.form.get('degree_type_target', None)
    location_target = request.form.get('location_target', None)
    stage_target = request.form.get('stage_target', None)
    
    # Convert scheduled_at to datetime if provided
    scheduled_datetime = None
    if scheduled_at:
        try:
            from datetime import datetime
            scheduled_datetime = datetime.fromisoformat(scheduled_at)
        except Exception:
            flash("Invalid datetime format for scheduling.", "warning")
    
    # Create message object (you may want to save to database here)
    message_data = {
        'title': title,
        'content': content,
        'degree_code': degree_code,
        'week_released': int(week_released) if week_released else 1,
        'scheduled_at': scheduled_datetime,
        'degree_type_target': degree_type_target if degree_type_target else None,
        'location_target': location_target if location_target else None,
        'stage_target': stage_target if stage_target else None
    }
    
    # Process the content and redirect back
    targeting_info = []
    if degree_type_target:
        targeting_info.append(f"Degree: {degree_type_target}")
    if location_target:
        targeting_info.append(f"Location: {location_target}")
    if stage_target:
        targeting_info.append(f"Stage: {stage_target}")
    
    targeting_str = " | ".join(targeting_info) if targeting_info else "All students"
    schedule_str = f" | Scheduled: {scheduled_datetime}" if scheduled_datetime else ""
    
    flash(f"Content saved! Title: {title} | Targeting: {targeting_str}{schedule_str} | Content length: {len(content)} characters", "success")
    current_app.logger.info(f"TinyMCE Message Data: {message_data}")
    
    return redirect(url_for('admin.admin_dashboard'))