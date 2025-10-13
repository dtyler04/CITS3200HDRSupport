"""
Weekly Digest Service
Handles the collection and sending of weekly digest emails to HDR students.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import and_
from app import db
from app.models import User, Message, EnrollmentUpdate, EnrollmentHistory, Enrollment
from app.services.mailchimp_service import MailchimpService
from app.services.message_personalisation import MessagePersonalisationService

class WeeklyDigestService:
    """Service for generating and sending weekly digest emails."""
    
    def __init__(self):
        self.mailchimp = MailchimpService()
        self.personalisation = MessagePersonalisationService()
        self.logger = logging.getLogger(__name__)
    
    def send_weekly_digests(self):
        """
        Send weekly digest emails to all active students.
        This should be called every Monday morning.
        """
        try:
            # Get all verified users
            users = User.query.filter(User.email_verified_at.isnot(None)).all()
            
            digest_count = 0
            error_count = 0
            
            for user in users:
                try:
                    if self._send_user_digest(user):
                        digest_count += 1
                    else:
                        self.logger.info(f"No digest sent to {user.email} - no messages for current week")
                        
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Failed to send digest to {user.email}: {e}")
            
            self.logger.info(f"Weekly digest batch complete: {digest_count} sent, {error_count} errors")
            return {"sent": digest_count, "errors": error_count}
            
        except Exception as e:
            self.logger.error(f"Failed to process weekly digest batch: {e}")
            raise
    
    def _send_user_digest(self, user):
        """
        Send weekly digest email to a specific user.
        
        Args:
            user: User object
            
        Returns:
            bool: True if digest was sent, False if no messages to send
        """
        # Calculate user's current week
        current_week = self._get_user_current_week(user)
        
        if current_week <= 0:
            self.logger.info(f"User {user.email} has invalid current week: {current_week}")
            return False
        
        # Get user's degree code and enrollment details
        user_enrollment = self._get_user_enrollment_details(user)
        if not user_enrollment:
            self.logger.warning(f"No enrollment details found for user {user.email}")
            return False
        
        # Get messages for this week
        messages = self._get_messages_for_week(user_enrollment, current_week)
        
        if not messages:
            # No messages for this week - optionally send "no messages" digest
            # For now, we'll skip sending if there are no messages
            return False
        
        # Prepare user data for personalization
        user_data = self._prepare_user_data(user, user_enrollment, current_week)
        
        # Personalize message content
        personalized_messages = []
        for message in messages:
            personalized_content = self.personalisation.personalise_content(
                message.content, 
                user_data
            )
            
            personalized_messages.append({
                'title': message.title,
                'content': personalized_content,
                'week_released': message.week_released
            })
        
        # Create digest email content
        html_content = self.mailchimp.create_digest_template(personalized_messages, user_data)
        
        # Create subject line
        subject = f"HDR Support Weekly Digest - Week {current_week}"
        
        # Send the digest email
        try:
            campaign_id = self.mailchimp.send_digest_email(
                email=user.email,
                subject=subject,
                html_content=html_content
            )
            
            self.logger.info(f"Weekly digest sent to {user.email} for week {current_week}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send digest email to {user.email}: {e}")
            raise
    
    def _get_user_current_week(self, user):
        """Calculate the user's current week in their candidature."""
        try:
            # Get the current progression day
            current_day = user.calculate_progression_day()
            
            # Convert to week (1-based)
            current_week = max(1, (current_day // 7) + 1)
            
            return current_week
            
        except Exception as e:
            self.logger.error(f"Failed to calculate current week for user {user.email}: {e}")
            return 0
    
    def _get_user_enrollment_details(self, user):
        """Get the user's current enrollment details from EnrollmentHistory."""
        try:
            # Get the current enrollment status (no end_date)
            current_enrollment = EnrollmentHistory.query.filter_by(
                user_id=user.user_id,
                end_date=None
            ).first()
            
            if current_enrollment:
                return current_enrollment
            
            # Fallback: get the most recent enrollment history
            latest_enrollment = EnrollmentHistory.query.filter_by(
                user_id=user.user_id
            ).order_by(EnrollmentHistory.start_date.desc()).first()
            
            if latest_enrollment:
                return latest_enrollment
            
            # Last fallback: try to get from EnrollmentUpdate (legacy)
            legacy_enrollment = EnrollmentUpdate.query.filter_by(
                user_id=user.user_id
            ).order_by(EnrollmentUpdate.update_id.desc()).first()
            
            return legacy_enrollment
            
        except Exception as e:
            self.logger.error(f"Failed to get enrollment details for user {user.email}: {e}")
            return None
    
    def _get_messages_for_week(self, user_enrollment, current_week):
        """
        Get all messages scheduled for the user's current week.
        
        Args:
            user_enrollment: EnrollmentHistory or EnrollmentUpdate object with user's details
            current_week: Current week number
            
        Returns:
            List of Message objects
        """
        try:
            # Build query to find messages for this week and degree
            # Include messages with degree_code matching user's degree OR degree_code = 'ALL'
            query = Message.query.filter(
                and_(
                    (Message.degree_code == user_enrollment.degree_code) | 
                    (Message.degree_code == 'ALL'),
                    Message.week_released == current_week
                )
            )
            
            # Get degree_type from the Enrollment table
            enrollment_info = Enrollment.query.filter_by(
                degree_code=user_enrollment.degree_code
            ).first()
            
            # Apply targeting filters if they exist
            if enrollment_info and hasattr(enrollment_info, 'degree_type'):
                query = query.filter(
                    (Message.degree_type_target == enrollment_info.degree_type) |
                    (Message.degree_type_target.is_(None))
                )
            
            # Check for location attribute (exists in both models)
            if hasattr(user_enrollment, 'location') and user_enrollment.location:
                query = query.filter(
                    (Message.location_target == user_enrollment.location) |
                    (Message.location_target.is_(None))
                )
            
            # Check for stage attribute (only in EnrollmentHistory)
            if hasattr(user_enrollment, 'stage') and user_enrollment.stage:
                query = query.filter(
                    (Message.stage_target == user_enrollment.stage) |
                    (Message.stage_target.is_(None))
                )
            
            messages = query.all()
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to get messages for week {current_week}: {e}")
            return []
    
    def _prepare_user_data(self, user, enrollment, current_week):
        """Prepare user data dictionary for message personalization."""
        # Get degree type from Enrollment table
        degree_type = 'HDR'
        enrollment_info = None
        
        try:
            enrollment_info = Enrollment.query.filter_by(
                degree_code=enrollment.degree_code
            ).first()
            if enrollment_info and hasattr(enrollment_info, 'degree_type'):
                degree_type = enrollment_info.degree_type
        except Exception as e:
            self.logger.warning(f"Could not get degree type: {e}")
        
        # Get study mode - could be in different attributes
        study_mode = 'your enrollment'
        if hasattr(enrollment, 'study_mode') and enrollment.study_mode:
            study_mode = enrollment.study_mode
        elif hasattr(enrollment, 'enrollment_status') and enrollment.enrollment_status:
            study_mode = enrollment.enrollment_status
        
        # Get location
        location = 'your location'
        if hasattr(enrollment, 'location') and enrollment.location:
            location = enrollment.location
        
        # Get stage
        stage = 'your current stage'
        if hasattr(enrollment, 'stage') and enrollment.stage:
            stage = enrollment.stage
        
        # Get support needs (might not exist in current models)
        support_needs = 'your needs'
        if hasattr(enrollment, 'support_needs') and enrollment.support_needs:
            support_needs = enrollment.support_needs
        
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'degree_type': degree_type,
            'location': location,
            'enrollment_status': study_mode,
            'stage': stage,
            'support_needs': support_needs,
            'current_week': current_week,
            'unit_codes': 'your units'  # Could be enhanced to get actual units
        }
    
    def preview_digest_for_user(self, user_id, week_override=None):
        """
        Generate a preview of the weekly digest for a specific user.
        Useful for testing and admin preview.
        
        Args:
            user_id: User ID to generate preview for
            week_override: Optional week number to preview (defaults to current week)
            
        Returns:
            Dictionary with preview information
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get current week or use override
            if week_override:
                current_week = week_override
            else:
                current_week = self._get_user_current_week(user)
            
            if current_week <= 0:
                return {"error": "Invalid current week"}
            
            # Get user enrollment details
            user_enrollment = self._get_user_enrollment_details(user)
            if not user_enrollment:
                return {"error": "No enrollment details found"}
            
            # Get messages for this week
            messages = self._get_messages_for_week(user_enrollment, current_week)
            
            # Prepare user data
            user_data = self._prepare_user_data(user, user_enrollment, current_week)
            
            # Personalize messages
            personalized_messages = []
            for message in messages:
                personalized_content = self.personalisation.personalise_content(
                    message.content, 
                    user_data
                )
                
                personalized_messages.append({
                    'title': message.title,
                    'content': personalized_content,
                    'week_released': message.week_released
                })
            
            # Generate HTML content
            html_content = self.mailchimp.create_digest_template(personalized_messages, user_data)
            
            return {
                "user_email": user.email,
                "current_week": current_week,
                "message_count": len(messages),
                "messages": personalized_messages,
                "html_content": html_content,
                "subject": f"HDR Support Weekly Digest - Week {current_week}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate preview for user {user_id}: {e}")
            return {"error": str(e)}
    
    def is_monday(self):
        """Check if today is Monday (when digests should be sent)."""
        return datetime.now().weekday() == 0  # Monday = 0
    
    def get_next_monday(self):
        """Get the date of the next Monday."""
        today = datetime.now()
        days_ahead = 0 - today.weekday()  # Monday = 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + timedelta(days_ahead)