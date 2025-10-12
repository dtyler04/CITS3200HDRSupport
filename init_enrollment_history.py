#!/usr/bin/env python3
"""
Initialize enrollment history for existing users
Run this script to create initial enrollment history records
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, EnrollmentUpdate, EnrollmentHistory, Enrollment
from datetime import datetime, timedelta

def init_enrollment_history():
    """Create initial enrollment history records for users who don't have them"""
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Find users with enrollment updates but no enrollment history
        users_without_history = db.session.query(User).filter(
            ~User.user_id.in_(
                db.session.query(EnrollmentHistory.user_id).distinct()
            )
        ).all()
        
        for user in users_without_history:
            # Get the user's latest enrollment update
            latest_update = EnrollmentUpdate.query.filter_by(
                user_id=user.user_id
            ).order_by(EnrollmentUpdate.update_id.desc()).first()
            
            if latest_update:
                # Create initial enrollment history record
                # Default to full-time if not specified
                study_mode = getattr(latest_update, 'study_mode', 'full-time')
                fte_multiplier = 1.0 if study_mode == 'full-time' else 0.5
                
                # Default start date to 30 days ago if no specific date
                start_date = datetime.utcnow() - timedelta(days=30)
                
                history_record = EnrollmentHistory(
                    user_id=user.user_id,
                    degree_code=latest_update.degree_code,
                    study_mode=study_mode,
                    location=getattr(latest_update, 'location', 'online'),
                    stage='commencing',  # Default stage
                    start_date=start_date,
                    fte_multiplier=fte_multiplier
                )
                
                db.session.add(history_record)
                print(f"Created enrollment history for user {user.user_id}")
        
        # Also create a test user with a more complex enrollment history
        test_user = User.query.filter_by(user_id=999).first()
        if not test_user:
            # Create test enrollment for demo
            test_enrollment = Enrollment(
                degree_code='TEST1234',
                degree_type='masters'
            )
            db.session.add(test_enrollment)
            
            # Create test user
            test_user = User(
                user_id=999,
                first_name='Test',
                last_name='Student',
                email='test@example.com',
                password='hashed_password'
            )
            db.session.add(test_user)
            
            # Create enrollment update
            test_update = EnrollmentUpdate(
                user_id=999,
                degree_code='TEST1234',
                initialisation=True,
                study_mode='full-time',
                current_week=1,
                location='online'
            )
            db.session.add(test_update)
            
            # Create progression timeline: start full-time, switch to part-time after 6 weeks
            # Start the program on September 12, 2025 (recent start date)
            program_start_date = datetime(2025, 9, 12)
            
            # Full-time period (first 6 weeks = 42 days)
            history1 = EnrollmentHistory(
                user_id=999,
                degree_code='TEST1234',
                study_mode='full-time',
                location='online',
                stage='commencing',
                start_date=program_start_date,
                end_date=program_start_date + timedelta(days=42),
                fte_multiplier=1.0
            )
            db.session.add(history1)
            
            # Part-time period (ongoing)
            history2 = EnrollmentHistory(
                user_id=999,
                degree_code='TEST1234',
                study_mode='part-time',
                location='online',
                stage='commencing',
                start_date=program_start_date + timedelta(days=42),
                fte_multiplier=0.5
            )
            db.session.add(history2)
            
            print("Created test user (ID: 999) with complex enrollment history")
        
        try:
            db.session.commit()
            print("Enrollment history initialization completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during initialization: {e}")

if __name__ == "__main__":
    init_enrollment_history()