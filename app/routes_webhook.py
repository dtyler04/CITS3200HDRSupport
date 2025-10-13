from flask import Blueprint, jsonify
from app.models import User
from .check import login_and_rights_required

mailchimp_bp = Blueprint("mailchimp", __name__, url_prefix="/webhook/mailchimp")

@mailchimp_bp.get("/api/user/<int:user_id>/current-week")
@login_and_rights_required(1)
def get_user_current_week(user_id):
    """Return current progression week, day, and timeline for a given user."""
    user = User.query.get_or_404(user_id)

    current_week = user.calculate_current_week()
    current_day = user.calculate_progression_day()
    timeline_info = user.get_progression_timeline(weeks=52)
    enrollment_status = user.get_current_enrollment_status()

    return jsonify({
        "user_id": user.user_id,
        "name": f"{user.first_name} {user.last_name}",
        "current_week": current_week,
        "current_day": current_day,
        "program_start": user.get_program_start_date().isoformat(),
        "fte_multiplier": enrollment_status.fte_multiplier if enrollment_status else 1.0,
        "timeline": timeline_info
    })


def get_all_user_progression():
    """Return progression summary for all users."""
    data = []
    users = User.query.all()
    for u in users:
        enrollment_status = u.get_current_enrollment_status()
        if not enrollment_status:
            continue  # skip users without enrollment history

        data.append({
            "user_id": u.user_id,
            "email": u.email,
            "degree_type": enrollment_status.enrollment.degree_type if enrollment_status.enrollment else None,
            "current_week": u.calculate_current_week(),
            "location": enrollment_status.location,
            "stage": enrollment_status.stage,
        })
    return data