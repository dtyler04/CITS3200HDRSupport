#!/usr/bin/env python3
"""
HDR Support Manual Digest Email Sender

PRODUCTION SCRIPT: Use for manual email sending and testing

This script sends digest emails to all subscribers based on their current week progression.
Unlike the automatic daily task, this sends emails based on current week, not progression between days.

Usage:
  python send_digest_emails.py           # Send to all users based on their current week
  python send_digest_emails.py 1         # Send Week 1 content to all subscribers
  python send_digest_emails.py 2         # Send Week 2 content to all subscribers

Note: The automatic daily emails are handled by the celery task in app/tasks.py
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, WeeklyContent, Message
from app.services.mailchimp_service import MailchimpService
from app.tasks import send_weekly_content, send_admin_message
from flask import current_app

def send_digest_to_all_subscribers():
    """Send digest emails to all subscribers based on their current week"""
    app = create_app()
    
    with app.app_context():
        print("📧 Sending Digest Emails to All Subscribers")
        print("=" * 60)
        
        mailchimp = current_app.extensions.get("mailchimp")
        logger = current_app.logger
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        # Group users by their current week
        week_map = {}
        
        for user in users:
            try:
                current_week = user.calculate_current_week()
                week_map.setdefault(current_week, []).append(user.email)
                print(f"User {user.email}: Week {current_week}")
            except Exception as e:
                print(f"❌ Error calculating week for {user.email}: {e}")
        
        print(f"\nUsers by week: {week_map}")
        
        # Send content for each week that has users
        total_sent = 0
        
        for week_num, emails in week_map.items():
            print(f"\n📤 Processing Week {week_num} ({len(emails)} users)")
            
            # Get WeeklyContent for this week
            weekly_contents = WeeklyContent.query.filter_by(week_released=week_num).all()
            print(f"  WeeklyContent items: {len(weekly_contents)}")
            
            # Get admin Messages for this week
            admin_messages = Message.query.filter_by(week_released=week_num).all()
            print(f"  Admin Messages: {len(admin_messages)}")
            
            if not weekly_contents and not admin_messages:
                print(f"  ⚠️ No content found for week {week_num} - skipping")
                continue
            
            # Send WeeklyContent
            for content in weekly_contents:
                try:
                    print(f"  📨 Sending WeeklyContent: {content.title}")
                    send_weekly_content(content, week_num, mailchimp, logger)
                    total_sent += 1
                except Exception as e:
                    print(f"  ❌ Failed to send WeeklyContent '{content.title}': {e}")
            
            # Send admin Messages
            for message in admin_messages:
                try:
                    print(f"  📨 Sending admin Message: {message.title}")
                    send_admin_message(message, week_num, emails, mailchimp, logger)
                    total_sent += 1
                except Exception as e:
                    print(f"  ❌ Failed to send admin Message '{message.title}': {e}")
        
        print(f"\n✅ Digest email process completed!")
        print(f"📊 Total emails sent: {total_sent}")
        print(f"👥 Users processed: {len(users)}")
        
        return total_sent

def send_specific_week_digest(week_number):
    """Send digest for a specific week to all subscribers"""
    app = create_app()
    
    with app.app_context():
        print(f"📧 Sending Week {week_number} Digest to All Subscribers")
        print("=" * 60)
        
        mailchimp = current_app.extensions.get("mailchimp")
        logger = current_app.logger
        
        # Get content for the specific week
        weekly_contents = WeeklyContent.query.filter_by(week_released=week_number).all()
        admin_messages = Message.query.filter_by(week_released=week_number).all()
        
        print(f"Week {week_number} content:")
        print(f"  WeeklyContent items: {len(weekly_contents)}")
        for content in weekly_contents:
            print(f"    - {content.title}")
        
        print(f"  Admin Messages: {len(admin_messages)}")
        for msg in admin_messages:
            print(f"    - {msg.title}")
        
        if not weekly_contents and not admin_messages:
            print(f"❌ No content found for week {week_number}")
            return 0
        
        # Get all subscriber emails (we'll send to everyone)
        all_emails = ["all_subscribers"]  # This will use no segment filtering
        
        total_sent = 0
        
        # Send WeeklyContent
        for content in weekly_contents:
            try:
                print(f"📨 Sending WeeklyContent: {content.title}")
                send_weekly_content(content, week_number, mailchimp, logger)
                total_sent += 1
            except Exception as e:
                print(f"❌ Failed to send WeeklyContent '{content.title}': {e}")
        
        # Send admin Messages
        for message in admin_messages:
            try:
                print(f"📨 Sending admin Message: {message.title}")
                send_admin_message(message, week_number, all_emails, mailchimp, logger)
                total_sent += 1
            except Exception as e:
                print(f"❌ Failed to send admin Message '{message.title}': {e}")
        
        print(f"\n✅ Week {week_number} digest sent!")
        print(f"📊 Total emails sent: {total_sent}")
        
        return total_sent

def main():
    """Main function with options"""
    print("📧 HDR Support Digest Email Sender")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Specific week mode
        try:
            week_num = int(sys.argv[1])
            print(f"Mode: Send Week {week_num} digest to all subscribers")
            send_specific_week_digest(week_num)
        except ValueError:
            print("❌ Invalid week number. Please provide a number.")
            sys.exit(1)
    else:
        # All users mode
        print("Mode: Send digest to all users based on their current week")
        print("(To send a specific week to all subscribers, use: python script.py WEEK_NUMBER)")
        
        try:
            confirm = input("\nProceed with sending digest emails? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled by user")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Cancelled by user")
            sys.exit(0)
        
        send_digest_to_all_subscribers()

if __name__ == "__main__":
    main()