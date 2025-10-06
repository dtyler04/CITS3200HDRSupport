from flask import Blueprint, request, jsonify
from app import db
from app.models import Engagement

mailchimp_bp = Blueprint("mailchimp", __name__, url_prefix="/webhook/mailchimp")

@mailchimp_bp.route("/", methods=["POST"])
def handle_webhook():
    data = request.json or request.form.to_dict()
    event_type = data.get("type")

    if event_type == "open":
        email = data["data"]["email"]
        campaign_id = data["data"].get("campaign_id")

        # Save engagement record
        engagement = Engagement(
            email=email,
            event="open",
            campaign_id=campaign_id,
            timestamp=data["fired_at"]
        )
        db.session.add(engagement)
        db.session.commit()

        return jsonify({"status": "open tracked"}), 200
    return jsonify({"status": "ignored"}), 200