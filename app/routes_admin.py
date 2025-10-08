from flask import Blueprint, request, redirect, url_for, flash, render_template, render_template_string, current_app, send_from_directory
from .forms import ChangeRightForm, EmailEditor, DeleteAccountForm, AdminMessageForm, AdminReminderForm, SupportPostForm, SupportContactForm, CSRFOnlyForm
from .models import Right, Message, User, Reminder, SupportPost, SupportContact
from .check import login_and_rights_required
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

    return render_template("admin/admin_dashboard.html", 
                           csrf_form=CSRFOnlyForm(),
                           form=EmailEditor(), 
                           form_right=ChangeRightForm(),
                           form_delete=DeleteAccountForm(),
                           msg_form=AdminMessageForm(), rem_form=AdminReminderForm(), post_form=SupportPostForm(), contact_form=SupportContactForm(),
                           messages=messages, reminders=reminders, posts=posts, contacts=contacts
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

@admin_bp.post("/message/create")
@login_and_rights_required(1)
def admin_create_message():
    form = AdminMessageForm()
    if form.validate_on_submit():
        sched = None
        if request.form.get("scheduled_at"):
            try:
                sched = datetime.fromisoformat(request.form.get("scheduled_at"))
            except Exception:
                sched = None

        # pick the right form field name
        if hasattr(form, "message_content"):
            content_value = form.message_content.data
        elif hasattr(form, "content"):
            content_value = form.content.data
        else:
            content_value = ""

        m = Message(
            title = form.title.data,
            content = content_value,
            degreeCode = "ALL",
            week_released = 1,
            scheduled_at = sched,
            degree_type_target = form.degree_type_target.data or None,
            location_target = form.location_target.data or None,
            stage_target = form.stage_target.data or None
        )
        db.session.add(m)
        db.session.commit()
        messages = Message.query.order_by(Message.scheduled_at.desc().nullslast()).all()
        if request.headers.get("HX-Request"):
            return render_template_string("""
<ul id="messages-list" class="list-group list-group-flush">
  {% for m in messages %}
    <li class="list-group-item">
      <strong>{{ m.title }}</strong>
      <div class="small text-muted">{{ m.scheduled_at if m.scheduled_at else 'Now' }}</div>
      <div>{{ m.content if m.content else (m.message_content if getattr(m, 'message_content', None) else '') }}</div>
    </li>
  {% else %}
    <li class="list-group-item text-muted">No messages.</li>
  {% endfor %}
</ul>
""", messages=messages)
        flash("Message created.", "success")
    else:
        if request.headers.get("HX-Request"):
            return render_template_string('<div class="alert alert-danger">Invalid message data.</div>'), 400
        flash("Invalid message data.", "danger")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.post("/reminder/create")
@login_and_rights_required(1)
def admin_create_reminder():
    form = AdminReminderForm()
    if form.validate_on_submit():
        sched = None
        if request.form.get("scheduled_at"):
            try:
                sched = datetime.fromisoformat(request.form.get("scheduled_at"))
            except Exception:
                if request.headers.get("HX-Request"):
                    return render_template_string('<div class="alert alert-danger">Invalid datetime format.</div>'), 400
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
        reminders = Reminder.query.order_by(Reminder.scheduled_at.desc()).all()
        if request.headers.get("HX-Request"):
            return render_template_string("""
<ul id="reminders-list" class="list-group list-group-flush">
  {% for r in reminders %}
    <li class="list-group-item">
      <strong>{{ r.title }}</strong>
      <div class="small text-muted">{{ r.scheduled_at if r.scheduled_at else 'No date' }}</div>
      <div>{{ r.content }}</div>
    </li>
  {% else %}
    <li class="list-group-item text-muted">No reminders.</li>
  {% endfor %}
</ul>
""", reminders=reminders)
        flash("Reminder scheduled.", "success")
    else:
        if request.headers.get("HX-Request"):
            return render_template_string('<div class="alert alert-danger">Invalid reminder data.</div>'), 400
        flash("Invalid reminder data.", "danger")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.post("/support_post/create")
@login_and_rights_required(1)
def admin_create_post():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    form = SupportPostForm()
    if form.validate_on_submit():
        filename = None
        file = form.image.data if hasattr(form, "image") else request.files.get("image")
        if file and getattr(file, "filename", None) and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, '..', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, fname))
            filename = fname

        units = getattr(form.unit_target, "unit_list", None)
        unit_target_str = "" if units is None else " ".join(units)
        post = SupportPost(title=form.title.data, content=form.content.data, image_filename=filename, unit_target=unit_target_str, created_at=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        posts = SupportPost.query.order_by(SupportPost.created_at.desc()).all()
        if request.headers.get("HX-Request"):
            return render_template_string("""
<ul id="support-posts-list" class="list-group list-group-flush">
  {% for p in posts %}
    <li class="list-group-item">
      <strong>{{ p.title }}</strong>
      <div class="small text-muted">{{ p.created_at }}</div>
      <div class="mt-1">{{ p.content }}</div>
      {% if p.image_filename %}
        <img src="{{ url_for('admin.uploaded_file', filename=p.image_filename) }}" class="img-fluid mt-2" style="max-height:220px;">
      {% endif %}
    </li>
  {% else %}
    <li class="list-group-item text-muted">No support posts.</li>
  {% endfor %}
</ul>
""", posts=posts)
        flash("Support post created.", "success")
    else:
        if request.headers.get("HX-Request"):
            return render_template_string('<div class="alert alert-danger">Invalid support post.</div>'), 400
        flash("Invalid support post.", "danger")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.post("/contact/create")
@login_and_rights_required(1)
def admin_create_contact():
    form = SupportContactForm()
    if form.validate_on_submit():
        units = getattr(form.unit_target, "unit_list", None)
        unit_target_str = "" if units is None else " ".join(units)
        contact = SupportContact(
            contact_id=random.randint(1, 10000),
            service_type=form.service_type.data.strip(),
            name=form.name.data.strip(), 
            info=form.info.data.strip(),
            unit_target=unit_target_str
        )
        db.session.add(contact)
        db.session.commit()
        contacts = SupportContact.query.order_by(SupportContact.service_type).all()
        if request.headers.get("HX-Request"):
            return render_template_string("""
<ul id="support-contacts-list" class="list-group list-group-flush">
  {% for c in contacts %}
    <li class="list-group-item">
      <strong>{{ c.service_type }}</strong>: {{ c.name }} — <span class="text-muted">{{ c.info }}</span>
    </li>
  {% else %}
    <li class="list-group-item text-muted">No contacts.</li>
  {% endfor %}
</ul>
""", contacts=contacts)
        flash("Support contact created.", "success")
    else:
        if request.headers.get("HX-Request"):
            return render_template_string('<div class="alert alert-danger">Invalid support contact.</div>'), 400
        flash("Invalid support contact.", "danger")
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