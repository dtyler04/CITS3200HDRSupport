from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Length, Email, Regexp, NumberRange

class LoginForm(FlaskForm):
    user_id = StringField('UserID', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class StudentSignUpForm(FlaskForm):
    user_id = StringField(
        'Student ID',
        validators=[DataRequired(), Regexp(r'^\d{8}$', message='Enter exactly 8 digits.')]
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

class EmailEditor(FlaskForm):
    message_id = HiddenField()
    message_content = HiddenField(
        validators=[DataRequired(message="Content cannot be empty.")],
        render_kw={"id": "message_content"} 
    )

    degreeCode = StringField(
        "degreeCode",
        validators=[DataRequired(), Length(max=64)],
        render_kw={"placeholder": "Degree Code", "required": True}
    )
    week_released = IntegerField(
        "week_released",
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={"placeholder": "Week Released", "required": True}
    )

    save = SubmitField("Save", render_kw={"class": "btn btn-primary me-2"})

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