from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Length, Email, NumberRange, Optional, ValidationError
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField, RadioField, TextAreaField, FileField, HiddenField
import re

class UnitListValidator:
    UNIT_RE = re.compile(r'^[A-Za-z]{4}\d{4}$')
    ALL_TOKENS = {'', 'ALL', '*', 'ANY'}

    def __init__(self, max_units=10):
        self.max_units = max_units

    @staticmethod
    def parse_units(s):
        # split on spaces/commas/semicolons/newlines
        parts = re.split(r'[\s,;]+', (s or '').strip())
        # uppercase + de-duplicate (preserve order)
        out, seen = [], set()
        for p in parts:
            u = p.upper()
            if u and u not in seen:
                seen.add(u)
                out.append(u)
        return out

    def __call__(self, form, field):
        # handle special tokens(e.g. "ALL")
        raw = (field.data or '').strip().upper()
        if raw in self.ALL_TOKENS:
            field.unit_list = None       
            field.data = ''              
            return
        
        units = self.parse_units(field.data)
        if not units:
            raise ValidationError("Enter at least one unit code.")
        bad = [u for u in units if not self.UNIT_RE.fullmatch(u)]
        if bad:
            raise ValidationError(f"Invalid unit(s): {', '.join(bad)}")
        if self.max_units and len(units) > self.max_units:
            raise ValidationError(f"Please enter at most {self.max_units} unit codes.")
        # expose the parsed list and normalise the field text
        field.unit_list = units
        field.data = " ".join(units)

class LoginForm(FlaskForm):
    user_id = IntegerField('UserID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class StudentSignUpForm(FlaskForm):
    user_id = IntegerField(
        'Student ID',
        validators=[DataRequired()]
    )
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    location = RadioField('Location', choices=[('online', 'Online'), ('on-campus', 'On-campus')], validators=[DataRequired()], render_kw={'style': 'list-style: none;'} )#this removes the bullet points from the <ul>
    degree_type = SelectField('Degree Type', choices=[('masters', 'Masters'), ('phd', 'PhD')], validators=[DataRequired()])
    degree_code = StringField('Degree Code', validators=[DataRequired(), Length(min=8, max=8)])
    support_needs = SelectField('Support Needs', choices=[('personal', 'Personal Wellbeing'), ('academic', 'Academic Support'), ('both', 'Both')], validators=[DataRequired()])
    enrollment_status = RadioField('Enrollment Status', choices=[('full-time', 'Full-time'), ('part-time', 'Part-time')], validators=[DataRequired()], render_kw={'style': 'list-style: none;'})
    stage = SelectField('Stage of Candidature', choices=[
        ('commencing', 'Commencing'),
        ('mid-candidature', 'Mid-candidature'),
        ('late-candidature', 'Late-candidature'),
        ('thesis-submission', 'Thesis Submission')
    ], validators=[DataRequired()])
    additional_info = TextAreaField('Additional Information')
    submit = SubmitField('Sign Up')

class ChangeRightForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    permission_number = SelectField(
        "Permission",
        coerce=int,
        choices=[(0, "Student (0)"), (1, "Admin (1)")],  # add more if you use them
        validators=[InputRequired()]
    )
    submit = SubmitField('Change Right')

class DeleteAccountForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Delete Account', render_kw={"class": "btn btn-danger", "onclick": "return confirm('Are you sure you want to delete this account? This action cannot be undone.');"})

class VerifyOTPForm(FlaskForm):
    code = IntegerField('Verification Code', 
                        validators=[
                            InputRequired(message="Enter your code."),
                            NumberRange(min=100000, max=999999, message="Enter a 6-digit code."),
                        ]
    )
    submit = SubmitField('Verify')
    
class ResendOTPForm(FlaskForm):
    resend = SubmitField("Resend code")

class AdminMessageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    message_content = TextAreaField('Message', validators=[DataRequired()])
    scheduled_at = StringField('Schedule (datetime-local)', validators=[Optional()])  # expects ISO "YYYY-MM-DDTHH:MM"
    degree_type_target = SelectField('Degree type target', choices=[('', 'All'), ('masters','Masters'), ('phd','PhD')], validators=[Optional()])
    location_target = SelectField('Location target', choices=[('', 'All'), ('online','Online'), ('on-campus','On-campus')], validators=[Optional()])
    stage_target = SelectField('Stage target', choices=[('', 'All'), ('commencing','Commencing'), ('mid-candidature','Mid-candidature'), ('late-candidature','Late-candidature'), ('thesis-submission','Thesis Submission')], validators=[Optional()])
    submit = SubmitField('Create Message')

class AdminReminderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Details', validators=[Optional()])
    scheduled_at = StringField('Schedule (datetime-local)', validators=[DataRequired()])
    degree_type_target = SelectField('Degree type target', choices=[('', 'All'), ('masters','Masters'), ('phd','PhD')], validators=[Optional()])
    location_target = SelectField('Location target', choices=[('', 'All'), ('online','Online'), ('on-campus','On-campus')], validators=[Optional()])
    stage_target = SelectField('Stage target', choices=[('', 'All'), ('commencing','Commencing'), ('mid-candidature','Mid-candidature'), ('late-candidature','Late-candidature'), ('thesis-submission','Thesis Submission')], validators=[Optional()])
    submit = SubmitField('Create Reminder')

class SupportPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    unit_target = StringField('Unit-target', validators=[DataRequired(), UnitListValidator(max_units=10)], render_kw={'placeholder': 'all for ALL, or enter codes e.g. CITS3001 CITS3002'})
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image (optional)', validators=[Optional()])
    submit = SubmitField('Post')

class SupportContactForm(FlaskForm):
    service_type = StringField('Service type', validators=[DataRequired()])
    unit_target = StringField('Unit-target', validators=[DataRequired(), UnitListValidator(max_units=10)], render_kw={'placeholder': 'all for ALL, or enter codes e.g. CITS3001 CITS3002'})
    name = StringField('Name', validators=[DataRequired()])
    info = StringField('Contact info', validators=[DataRequired()])
    submit = SubmitField('Save Contact')

class UnitEnrollmentForm(FlaskForm):
    unit_code = StringField('Unit Code', validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Enroll')

class CSRFOnlyForm(FlaskForm):
    submit = SubmitField("Unenroll")

# Class for resetting password containing user id, email, and submit button
class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Reset")

# Create a class for new password containing new password, confirm password, submit button
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters.")],
        render_kw={"placeholder": "Enter new password"}
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), Length(min=6),],
        render_kw={"placeholder": "Confirm new password"}
    )
    submit = SubmitField("Update Password")

class WeeklyForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    unit_code = StringField('Unit Code', validators=[Optional(), UnitListValidator(max_units=20)], render_kw={'placeholder': 'Enter a single unit code e.g. CITS3001 or all'})
    degree_type_target = SelectField('Degree type target', choices=[('','None'),('masters','Masters'), ('phd','PhD')], validators=[Optional()])
    week_released = IntegerField("week_released",validators=[DataRequired(), NumberRange(min=1,max=52)])
    submit = SubmitField("Save Content")

    # Customic validation: ensure exactly one of degree_type_target or unit_code is set
    def validate(self, **kwargs):
        rv = super().validate(**kwargs)
        if not rv:
            return False
        
        degree_val = (self.degree_type_target.data or '').strip().lower()
        unit_val = (self.unit_code.data or '').strip().upper()
        has_degree = degree_val in ['masters', 'phd']
        has_unit = bool(unit_val and unit_val not in ['ALL', '*'])

        if has_degree and has_unit:
            self.degree_type_target.errors.append("Choose either Degree Type or Unit Code — not both.")
            self.degree_type_target.errors.append("Cannot use both fields at once.")
            return False

        if not has_degree and not has_unit:
            self.degree_type_target.errors.append("Please select at least one targeting option (Degree or Unit).")
            return False

        return True

class EnrollmentUpdateForm(FlaskForm):
    """Form for students to update their enrollment status"""
    study_mode = SelectField(
        'Study Mode',
        choices=[('full-time', 'Full-time'), ('part-time', 'Part-time')],
        validators=[DataRequired()]
    )
    location = SelectField(
        'Location',
        choices=[('online', 'Online'), ('on-campus', 'On-campus')],
        validators=[DataRequired()]
    )
    stage = SelectField(
        'Stage of Candidature',
        choices=[
            ('commencing', 'Commencing'),
            ('mid-candidature', 'Mid-candidature'),
            ('late-candidature', 'Late-candidature'),
            ('thesis-submission', 'Thesis Submission')
        ],
        validators=[DataRequired()]
    )
    effective_date = StringField(
        'Effective Date',
        validators=[DataRequired()],
        render_kw={'type': 'date', 'placeholder': 'YYYY-MM-DD'}
    )
    submit = SubmitField('Update Enrollment')

class AssessmentForm(FlaskForm):
    """Form for admins to create assessments"""
    title = StringField(
        'Assessment Title',
        validators=[DataRequired(), Length(max=120)],
        render_kw={'placeholder': 'e.g., Research Proposal'}
    )
    description = TextAreaField(
        'Description',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Detailed description of the assessment requirements', 'rows': 4}
    )
    degree_code = StringField(
        'Degree Code',
        validators=[DataRequired(), Length(min=8, max=8)],
        render_kw={'placeholder': 'e.g., CITS3200'}
    )
    due_week = IntegerField(
        'Due Week',
        validators=[DataRequired(), NumberRange(min=1, max=52, message="Week must be between 1 and 52")],
        render_kw={'placeholder': 'Week number (1-52)'}
    )
    submit = SubmitField('Create Assessment')