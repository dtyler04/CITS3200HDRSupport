#!/usr/bin/env python3
"""
Test script for the Weekly Digest System
Tests various components of the digest email functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import User, Message, EnrollmentUpdate
from app.services.weekly_digest_service import WeeklyDigestService
from app.services.scheduled_task_manager import task_manager
from datetime import datetime

def test_weekly_digest_system():
    """Test the weekly digest system components."""
    
    print("🧪 Testing Weekly Digest System")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Check if services can be imported and initialized
        print("\n1. Testing Service Initialization...")
        try:
            digest_service = WeeklyDigestService()
            print("   ✅ WeeklyDigestService initialized successfully")
        except Exception as e:
            print(f"   ❌ Failed to initialize WeeklyDigestService: {e}")
            return False
        
        try:
            schedule_info = task_manager.get_schedule_info()
            print(f"   ✅ Task Manager initialized - Running: {schedule_info['is_running']}")
        except Exception as e:
            print(f"   ❌ Failed to initialize Task Manager: {e}")
            return False
        
        # Test 2: Check database models
        print("\n2. Testing Database Models...")
        try:
            user_count = User.query.count()
            message_count = Message.query.count()
            enrollment_count = EnrollmentUpdate.query.count()
            print(f"   ✅ Database accessible - Users: {user_count}, Messages: {message_count}, Enrollments: {enrollment_count}")
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
        
        # Test 3: Check if there are any users to test with
        print("\n3. Testing User Data...")
        try:
            test_user = User.query.filter(User.email_verified_at.isnot(None)).first()
            if test_user:
                print(f"   ✅ Found verified test user: {test_user.email}")
                
                # Test user progression calculation
                try:
                    current_week = digest_service._get_user_current_week(test_user)
                    print(f"   ✅ User current week calculation: Week {current_week}")
                except Exception as e:
                    print(f"   ⚠️  Week calculation error: {e}")
                
                # Test enrollment details
                try:
                    enrollment = digest_service._get_user_enrollment_details(test_user)
                    if enrollment:
                        print(f"   ✅ User enrollment found: {enrollment.degree_code}")
                    else:
                        print(f"   ⚠️  No enrollment details for user")
                except Exception as e:
                    print(f"   ⚠️  Enrollment details error: {e}")
                
            else:
                print("   ⚠️  No verified users found for testing")
        except Exception as e:
            print(f"   ❌ User data error: {e}")
        
        # Test 4: Test message filtering
        print("\n4. Testing Message Filtering...")
        try:
            messages = Message.query.limit(5).all()
            if messages:
                print(f"   ✅ Found {len(messages)} messages for testing")
                for msg in messages[:3]:
                    print(f"      - '{msg.title}' (Week {msg.week_released}, Degree: {msg.degree_code})")
            else:
                print("   ⚠️  No messages found in database")
        except Exception as e:
            print(f"   ❌ Message query error: {e}")
        
        # Test 5: Test preview functionality (if we have a test user)
        if 'test_user' in locals() and test_user:
            print("\n5. Testing Preview Functionality...")
            try:
                preview_data = digest_service.preview_digest_for_user(test_user.user_id, week_override=1)
                if "error" in preview_data:
                    print(f"   ⚠️  Preview error: {preview_data['error']}")
                else:
                    print(f"   ✅ Preview generated for {preview_data['user_email']}")
                    print(f"      - Week: {preview_data['current_week']}")
                    print(f"      - Messages: {preview_data['message_count']}")
                    print(f"      - Subject: {preview_data['subject']}")
            except Exception as e:
                print(f"   ❌ Preview error: {e}")
        
        # Test 6: Test scheduler status
        print("\n6. Testing Scheduler...")
        try:
            status = task_manager.get_schedule_info()
            print(f"   ✅ Scheduler status: {status}")
            
            if not status['is_running']:
                print("   📝 Scheduler is not running - this is normal for testing")
            else:
                print(f"   ✅ Scheduler is running with {len(status['jobs'])} jobs")
        except Exception as e:
            print(f"   ❌ Scheduler error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Weekly Digest System Test Complete!")
    print("\nNext Steps:")
    print("1. Install the 'schedule' package: pip install schedule")
    print("2. Configure MailChimp API credentials in your environment")
    print("3. Create some test messages with targeting for testing")
    print("4. Use the admin dashboard to manage the weekly digest system")
    print("5. Test the preview functionality with real user data")
    
    return True

if __name__ == "__main__":
    test_weekly_digest_system()