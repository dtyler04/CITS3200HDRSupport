from celery import shared_task
from datetime import datetime, timedelta
from app import db
from app.models import User, WeeklyContent, EmailLog, Message
from flask import current_app

@shared_task
def daily_progression_check():
    """Runs daily, checks user progression, and sends a Mailchimp campaign for new week."""
    mailchimp = current_app.extensions.get("mailchimp")
    logger = current_app.logger
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)

    logger.info("Starting daily progression check...")

    # Group users who moved into a new week
    users = User.query.all()
    week_map = {}

    for user in users:
        try:
            prev_week = user.calculate_current_week(yesterday)
            curr_week = user.calculate_current_week(today)
            logger.info(f"User {user.email}: prev_week={prev_week}, curr_week={curr_week}")
            if curr_week > prev_week:
                week_map.setdefault(curr_week, []).append(user.email)
                logger.info(f"User {user.email} progressed to week {curr_week}")
        except Exception as e:
            logger.error(f"Error calculating progression for {user.email}: {e}")

    logger.info(f"Users progressing to new weeks: {week_map}")
    
    for week_num, emails in week_map.items():
        # Send WeeklyContent (existing system)
        contents = WeeklyContent.query.filter_by(week_released=week_num).all()
        for content in contents:
            send_weekly_content(content, week_num, mailchimp, logger)
        
        # Send admin Messages (NEW!)
        messages = Message.query.filter_by(week_released=week_num).all()
        for message in messages:
            send_admin_message(message, week_num, emails, mailchimp, logger)
        
        if not contents and not messages:
            logger.info(f"No WeeklyContent or Messages found for week {week_num}")

    logger.info("Daily progression check complete.")


def send_weekly_content(content, week_num, mailchimp, logger):
    """Send WeeklyContent (existing logic)"""
    logger.info(f"Sending WeeklyContent: {content.title}")
    tag_to_use = None
    if content.unit_code:
        tag_to_use = content.unit_code.strip().lower()
    elif content.degree_type_target and content.degree_type_target.lower() != "all":
        tag_to_use = content.degree_type_target.capitalize()

    if not tag_to_use:
        logger.warning(
            f"⚠️ No tag or degree_type_target set for Week {week_num} WeeklyContent '{content.title}'. Skipping."
        )
        return

    segment_opts = {
        "match": "any",
        "conditions": [
            {
                "condition_type": "StaticSegment",
                "field": "static_segment",
                "op": "static_is",
                "value": tag_to_use,
            }
        ],
    }

    try:
        mailchimp.send_weekly_campaign(
            subject=f"Week {week_num} - {content.title}",
            html_content=content.content,
            segment_opts=segment_opts,
        )
        logger.info(f"Sent WeeklyContent campaign for tag '{tag_to_use}' (Week {week_num})")
    except Exception as e:
        logger.error(f"WeeklyContent send failed for tag '{tag_to_use}' (Week {week_num}): {e}")


def send_admin_message(message, week_num, emails, mailchimp, logger):
    """Send admin Message (NEW functionality)"""
    logger.info(f"Sending admin Message: {message.title}")
    
    # Build segment options based on message targeting
    segment_conditions = []
    
    # Check if message has specific targeting
    has_targeting = False
    
    # Add degree type targeting
    if message.degree_type_target and message.degree_type_target.lower() not in ['none', 'all', '']:
        segment_conditions.append({
            "condition_type": "StaticSegment",
            "field": "static_segment", 
            "op": "static_is",
            "value": message.degree_type_target.lower()
        })
        has_targeting = True
        logger.info(f"Message targeting degree type: {message.degree_type_target}")
    
    # Add location targeting  
    if message.location_target and message.location_target.lower() not in ['none', 'all', '']:
        segment_conditions.append({
            "condition_type": "StaticSegment",
            "field": "static_segment",
            "op": "static_is", 
            "value": message.location_target.lower()
        })
        has_targeting = True
        logger.info(f"Message targeting location: {message.location_target}")
    
    # Add stage targeting
    if message.stage_target and message.stage_target.lower() not in ['none', 'all', '']:
        segment_conditions.append({
            "condition_type": "StaticSegment",
            "field": "static_segment",
            "op": "static_is", 
            "value": message.stage_target.lower().replace('-', '_')  # Convert "mid-candidature" to "mid_candidature"
        })
        has_targeting = True
        logger.info(f"Message targeting stage: {message.stage_target}")
    
    # If no specific targeting, send to all users (use degree code as fallback)
    if not has_targeting:
        if message.degree_code and message.degree_code.upper() != 'ALL':
            segment_conditions.append({
                "condition_type": "StaticSegment",
                "field": "static_segment",
                "op": "static_is",
                "value": message.degree_code.lower()
            })
            logger.info(f"Message using degree code targeting: {message.degree_code}")
        else:
            # Send to all subscribers (no segment filtering)
            logger.info(f"Message has no targeting - sending to all subscribers")
            segment_conditions = None
    
    # Build segment options
    segment_opts = None
    if segment_conditions:
        segment_opts = {
            "match": "all" if len(segment_conditions) > 1 else "any",
            "conditions": segment_conditions
        }

    try:
        mailchimp.send_weekly_campaign(
            subject=f"Week {week_num} - {message.title}",
            html_content=message.content,
            segment_opts=segment_opts,
        )
        logger.info(f"Sent admin Message campaign: '{message.title}' (Week {week_num})")
    except Exception as e:
        logger.error(f"Admin Message send failed for '{message.title}' (Week {week_num}): {e}")

@shared_task
def test_task():
    print("Celery test_task executed successfully!")
    return "ok"
