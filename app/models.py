# models.py
# Define your database models here


from app import db
from datetime import datetime, timedelta

class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)

    rights = db.relationship('Right', backref='user', lazy='select', cascade="all, delete-orphan", passive_deletes=False)
    updates = db.relationship('EnrollmentUpdate', backref='user', lazy='select', cascade="all, delete-orphan", passive_deletes=False)
    user_units = db.relationship("Unit", backref="user", cascade="all, delete-orphan", lazy="select")
    
    def is_verified(self):
        return self.email_verified_at is not None
    
    def get_current_enrollment_status(self):
        """Get the most recent enrollment history record"""
        current_history = EnrollmentHistory.query.filter_by(
            user_id=self.user_id,
            end_date=None
        ).first()
        return current_history
    
    def calculate_progression_day(self, target_date=None):
        """Calculate the progression day number based on enrollment history"""
        if target_date is None:
            target_date = datetime.utcnow()
        
        history_records = EnrollmentHistory.query.filter_by(
            user_id=self.user_id
        ).order_by(EnrollmentHistory.start_date).all()
        
        if not history_records:
            return 0
        
        total_days = 0
        
        for record in history_records:
            # Determine the end date for this record
            end_date = record.end_date if record.end_date else target_date
            
            # Skip if this record starts after our target date
            if record.start_date > target_date:
                break
            
            # Calculate actual calendar days in this period
            period_start = record.start_date
            period_end = min(end_date, target_date)
            
            if period_end > period_start:
                calendar_days = (period_end - period_start).days
                # Apply FTE multiplier (full-time = 1.0, part-time = 0.5)
                effective_days = calendar_days * record.fte_multiplier
                total_days += effective_days
        
        return int(total_days)
    
    def get_progression_timeline(self, weeks=52):
        """Generate timeline data for the progression chart"""
        history_records = EnrollmentHistory.query.filter_by(
            user_id=self.user_id
        ).order_by(EnrollmentHistory.start_date).all()
        
        if not history_records:
            return []
        
        timeline = []
        current_day = 0
        
        for record in history_records:
            if not record.end_date:  # Current status
                # Calculate days from start_date to now
                days_in_period = (datetime.utcnow() - record.start_date).days
                # Add remaining days for full timeline
                remaining_days = (weeks * 7) - current_day
                effective_days = min(days_in_period, remaining_days)
            else:
                days_in_period = (record.end_date - record.start_date).days
                effective_days = days_in_period * record.fte_multiplier
            
            timeline.append({
                'start_day': current_day,
                'end_day': current_day + int(effective_days),
                'study_mode': record.study_mode,
                'location': record.location,
                'stage': record.stage,
                'fte_multiplier': record.fte_multiplier,
                'start_date': record.start_date,
                'end_date': record.end_date
            })
            
            current_day += int(effective_days)
            
            if current_day >= weeks * 7:
                break
        
        return timeline
    
    def calculate_current_week(self, target_date=None):
        """Calculate the current week number based on progression"""
        current_day = self.calculate_progression_day(target_date)
        return (current_day // 7) + 1 if current_day > 0 else 1
    
    def get_program_start_date(self):
        """Get the actual start date of the program from the first enrollment history"""
        first_record = EnrollmentHistory.query.filter_by(
            user_id=self.user_id
        ).order_by(EnrollmentHistory.start_date).first()
        
        return first_record.start_date if first_record else datetime.utcnow()
    
    def get_timeline_with_dates(self, weeks=52):
        """Generate enhanced timeline data with real calendar dates"""
        program_start = self.get_program_start_date()
        timeline_data = self.get_progression_timeline(weeks)
        current_day = self.calculate_progression_day()
        current_week = self.calculate_current_week()
        
        # Generate week data with simple calendar dates
        # Each week starts exactly 7 calendar days after the previous week
        weeks_data = []
        for week_num in range(1, weeks + 1):
            week_start_day = (week_num - 1) * 7
            week_end_day = week_start_day + 6
            
            # Simple calendar calculation: each week is exactly 7 days after program start
            calendar_date = program_start + timedelta(days=week_start_day)
            
            # Determine status for this week based on progression
            status = 'future'
            if week_start_day <= current_day <= week_end_day:
                status = 'current'
            elif week_end_day < current_day:
                status = 'completed'
            
            # Find which enrollment period this week falls into for study mode
            week_enrollment = None
            for period in timeline_data:
                if period['start_day'] <= week_start_day <= period['end_day']:
                    week_enrollment = period
                    break
            
            weeks_data.append({
                'week_number': week_num,
                'start_day': week_start_day,
                'end_day': week_end_day,
                'real_date': calendar_date,
                'status': status,
                'study_mode': week_enrollment['study_mode'] if week_enrollment else 'unknown',
                'fte_multiplier': week_enrollment['fte_multiplier'] if week_enrollment else 1.0
            })
        
        return {
            'weeks': weeks_data,
            'current_day': current_day,
            'current_week': current_week,
            'program_start': program_start,
            'timeline_periods': timeline_data
        }
    
    def _calculate_real_date_for_progression_day(self, target_progression_day, program_start):
        """Calculate the real calendar date for a given progression day"""
        history_records = EnrollmentHistory.query.filter_by(
            user_id=self.user_id
        ).order_by(EnrollmentHistory.start_date).all()
        
        if not history_records:
            # If no history, assume full-time progression
            return program_start + timedelta(days=target_progression_day)
        
        current_progression_days = 0
        current_calendar_date = program_start
        
        for record in history_records:
            record_start_date = max(record.start_date, current_calendar_date)
            
            if record.end_date:
                # Completed enrollment period
                calendar_days_in_period = (record.end_date - record_start_date).days
                progression_days_in_period = calendar_days_in_period * record.fte_multiplier
                
                if current_progression_days + progression_days_in_period >= target_progression_day:
                    # Target falls within this period
                    remaining_progression_needed = target_progression_day - current_progression_days
                    calendar_days_needed = remaining_progression_needed / record.fte_multiplier
                    return record_start_date + timedelta(days=calendar_days_needed)
                
                # Move past this period
                current_progression_days += progression_days_in_period
                current_calendar_date = record.end_date
            else:
                # Current/ongoing enrollment period
                remaining_progression_needed = target_progression_day - current_progression_days
                calendar_days_needed = remaining_progression_needed / record.fte_multiplier
                return record_start_date + timedelta(days=calendar_days_needed)
        
        # If we get here, target is beyond all records - extrapolate with last known FTE
        if history_records:
            last_record = history_records[-1]
            remaining_progression = target_progression_day - current_progression_days
            calendar_days_needed = remaining_progression / last_record.fte_multiplier
            return current_calendar_date + timedelta(days=calendar_days_needed)
        
        return program_start + timedelta(days=target_progression_day)
class Right(db.Model):
    __tablename__ = 'Rights'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False, primary_key=True)
    permission_number = db.Column(db.Integer, db.ForeignKey('Admin.permission_number'), primary_key=True)
    
class Admin(db.Model):
    __tablename__ = 'Admin'
    permission_number = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(50), nullable=False)

    rights = db.relationship('Right', backref='admin', lazy=True)
class EnrollmentUpdate(db.Model):
    __tablename__ = 'EnrollmentUpdates'
    update_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    degree_code = db.Column(db.String(8), db.ForeignKey('Enrollments.degree_code'), nullable=False)
    initialisation = db.Column(db.Boolean, nullable=False)
    study_mode = db.Column(db.String, nullable=False)
    current_week = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String, nullable=False)

class EnrollmentHistory(db.Model):
    """Track enrollment status changes over time for progression timeline"""
    __tablename__ = 'EnrollmentHistory'
    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    degree_code = db.Column(db.String(8), db.ForeignKey('Enrollments.degree_code'), nullable=False)
    study_mode = db.Column(db.String, nullable=False)  # 'full-time', 'part-time'
    location = db.Column(db.String, nullable=False)   # 'online', 'on-campus'
    stage = db.Column(db.String, nullable=False)      # 'commencing', 'mid-candidature', etc.
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)  # NULL if current status
    fte_multiplier = db.Column(db.Float, nullable=False, default=1.0)  # 1.0 for full-time, 0.5 for part-time
    
    # Relationships
    user = db.relationship('User', backref='enrollment_history', lazy='select')
    enrollment = db.relationship('Enrollment', backref='history_records', lazy='select')
    
    def __repr__(self):
        return f'<EnrollmentHistory {self.user_id}: {self.study_mode} from {self.start_date}>'
class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    degree_code = db.Column(db.String(8), primary_key=True)
    degree_type = db.Column(db.String, nullable=False)

    updates = db.relationship('EnrollmentUpdate', backref='enrollment', lazy=True)
    messages = db.relationship('Message', backref='enrollment', lazy=True)

class Unit(db.Model):
    __tablename__ = 'Units'
    user_id   = db.Column(db.Integer,
                          db.ForeignKey("Users.user_id", ondelete="CASCADE"),
                          primary_key=True, index=True)
    unit_code = db.Column(db.String(8), primary_key=True)
    enrolled_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class Message(db.Model):
    __tablename__ = 'Messages'
    message_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)               # new
    degree_code = db.Column(db.String(8), db.ForeignKey('Enrollments.degree_code'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    week_released = db.Column(db.Integer, nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=True)            # new: schedule time
    degree_type_target = db.Column(db.String(20), nullable=True)    # 'masters','phd' or NULL for all
    location_target = db.Column(db.String(20), nullable=True)       # 'online','on-campus' or NULL
    stage_target = db.Column(db.String(30), nullable=True)          # 'commencing' etc or NULL

    def __init__(self, **kwargs):
        # Validate targeting fields
        valid_degree_types = ['masters', 'phd', None, '']
        valid_locations = ['online', 'on-campus', None, '']
        valid_stages = ['commencing', 'mid-candidature', 'late-candidature', 'thesis-submission', None, '']
        
        if 'degree_type_target' in kwargs:
            if kwargs['degree_type_target'] not in valid_degree_types:
                raise ValueError(f"Invalid degree_type_target: {kwargs['degree_type_target']}")
        
        if 'location_target' in kwargs:
            if kwargs['location_target'] not in valid_locations:
                raise ValueError(f"Invalid location_target: {kwargs['location_target']}")
                
        if 'stage_target' in kwargs:
            if kwargs['stage_target'] not in valid_stages:
                raise ValueError(f"Invalid stage_target: {kwargs['stage_target']}")
        
        super().__init__(**kwargs)

class Reminder(db.Model):
    __tablename__ = 'Reminders'
    reminder_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    degree_type_target = db.Column(db.String(20), nullable=True)
    location_target = db.Column(db.String(20), nullable=True)
    stage_target = db.Column(db.String(30), nullable=True)

class SupportPost(db.Model):
    __tablename__ = 'SupportPosts'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    unit_target = db.Column(db.String(500), nullable=True)  # comma-separated unit codes, or NULL for all
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportContact(db.Model):
    __tablename__ = 'SupportContacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100), nullable=False)   # e.g. 'Mental Health'
    unit_target = db.Column(db.String(500), nullable=False)    # comma-separated unit codes, or NULL for all
    name = db.Column(db.String(200), nullable=False)
    info = db.Column(db.String(300), nullable=False)
class Assessments(db.Model):
    __tablename__ = 'Assessments'
    assessment_id = db.Column(db.Integer, primary_key=True)
    degree_code = db.Column(db.String(8), db.ForeignKey('Enrollments.degree_code'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_week = db.Column(db.Integer, nullable=False)

    enrollment = db.relationship('Enrollment', backref='assessments', lazy=True)
class EmailLog(db.Model):
    __tablename__ = 'EmailLogs'
    email_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False)
    mailchimp_id = db.Column(db.String(255), nullable=True)  # To store Mailchimp message ID for reference
    
    user = db.relationship('User', backref='email_logs', lazy=True)

class WeeklyContent(db.Model):
    __tablename__ = "weekly_content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    unit_code = db.Column(db.String(50), nullable=True, default=None) # e.g. CITS3001,etc or None
    degree_type_target = db.Column(db.String(50), nullable=True)  # Masters, PhD or None.
    week_released = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=True)
    creator = db.relationship("User", backref=db.backref("weekly_contents", lazy=True))