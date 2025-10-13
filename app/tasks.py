from celery import shared_task
from datetime import datetime, timedelta
from app import db
from app.models import User, WeeklyContent, EmailLog
from flask import current_app

@shared_task
def daily_progression_check():
    """Runs daily, checks user progression, and sends a Mailchimp campaign for new week."""
    mailchimp = current_app.extensions.get("mailchimp")
    logger = current_app.logger
    today = datetime.utcnow().date()

    logger.info("Starting daily progression check...")

    # Group users who moved into a new week
    users = User.query.all()
    week_map = {}

    for user in users:
        try:
            prev_week = user.calculate_current_week(today - timedelta(days=1))
            curr_week = user.calculate_current_week(today)
            if curr_week > prev_week:
                week_map.setdefault(curr_week, []).append(user.email)
        except Exception as e:
            logger.error(f"Error calculating progression for {user.email}: {e}")

    for week_num, emails in week_map.items():
        contents = WeeklyContent.query.filter_by(week_released=week_num).all()
        if not contents:
            logger.info(f"No WeeklyContent found for week {week_num}")
            continue

        for content in contents:
            logger.info(f"Sending week {week_num} campaign: {content.title}")
            tag_to_use = None
            if content.unit_code:
                tag_to_use = content.unit_code.strip().lower()
            elif content.degree_type_target and content.degree_type_target.lower() != "all":
                tag_to_use = content.degree_type_target.capitalize()

            if not tag_to_use:
                logger.warning(
                    f"⚠️ No tag or degree_type_target set for Week {week_num} content '{content.title}'. Skipping."
                )
                continue

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
                logger.info(f"Sent campaign for tag '{tag_to_use}' (Week {week_num})")
            except Exception as e:
                logger.error(f"Mailchimp send failed for tag '{tag_to_use}' (Week {week_num}): {e}")

    logger.info("Daily progression check complete.")

@shared_task
def test_task():
    print("Celery test_task executed successfully!")
    return "ok"
