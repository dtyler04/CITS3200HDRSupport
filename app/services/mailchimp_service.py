from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
import hashlib, os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

class MailchimpService:
    def __init__(self):
        load_dotenv()
        self.client = Client()
        self.list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.client.set_config({
            "api_key": os.getenv("MAILCHIMP_API_KEY"),
            "server": os.getenv("MAILCHIMP_SERVER_PREFIX"),
        })

    # Hash mail address as required by Mailchimp API
    def _subscriber_hash(self, email):
        return hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()

    # Ping Mailchimp server to check connection
    def ping(self):
        return self.client.ping.get()

    # Add or update a member in the mailing list
    def upsert_member(self, email, first_name="", last_name="", status_if_new="subscribed", status='subscribed'):
        sub_hash = self._subscriber_hash(email)
        body = {
            "email_address": email,
            "status_if_new": status_if_new,
            "status": status,
            "merge_fields": {"FNAME": first_name, "LNAME": last_name}
        }
        try:
            return self.client.lists.set_list_member(self.list_id, sub_hash, body)
        except ApiClientError as e:
            # Use logging instead of print
            import logging
            logging.error(f"Mailchimp API error: {e.text}")
            raise

    def get_member(self, email):
        sub_hash = self._subscriber_hash(email)
        try:
            return self.client.lists.get_list_member(self.list_id, sub_hash)
        except ApiClientError as error:
            if error.status_code == 404:
                return None
            raise
    

    def add_member(self, email, first_name="", last_name="", status="subscribed"):
            body = {
                "email_address": email,
                "status": status,
                "merge_fields": {"FNAME": first_name, "LNAME": last_name}
            }
            return self.client.lists.add_list_member(self.list_id, body)

    def delete_member(self, email):
        sub_hash = self._subscriber_hash(email)
        try:
            return self.client.lists.delete_list_member(self.list_id, sub_hash)
        except ApiClientError as e:
            import logging
            logging.error(f"Mailchimp delete member error: {e.text}")
            return False
        except Exception as e:
            return False

    # Use this when a student enrolls/starts a unit  
    def add_unit_tag(self, email, unit_code):
        sub_hash = self._subscriber_hash(email)
        body = {
            "tags": [{"name": unit_code, "status": "active"}]
        }
        try:
            return self.client.lists.update_list_member_tags(self.list_id, sub_hash, body)
        except ApiClientError as e:
            logging.error(f"Mailchimp API error (add_unit_tag) for {email} - {unit_code}: {e.text}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error adding unit tag for {email} - {unit_code}: {e}")
            raise

    # Use this when a student unenrolls/finishes from a unit
    def remove_unit_tag(self, email, unit_code):
        sub_hash = self._subscriber_hash(email)
        body = {"tags": [{"name": unit_code, "status": "inactive"}]}
        try:
            return self.client.lists.update_list_member_tags(self.list_id, sub_hash, body)
        except ApiClientError as e:
            logging.error(f"Mailchimp API error (remove_unit_tag) for {email} - {unit_code}: {getattr(e, 'text', str(e))}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error removing unit tag for {email} - {unit_code}: {e}")
            raise

    def send_digest_email(self, email, subject, html_content, text_content=None):
        """
        Send a weekly digest email to a specific user using Mailchimp Transactional API
        
        Args:
            email: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            text_content: Plain text version (optional)
        """
        try:
            # Create a campaign for the digest email
            campaign_body = {
                "type": "regular",
                "recipients": {
                    "list_id": self.list_id,
                    "segment_opts": {
                        "match": "all",
                        "conditions": [
                            {
                                "condition_type": "EmailAddress",
                                "field": "EMAIL",
                                "op": "is",
                                "value": email
                            }
                        ]
                    }
                },
                "settings": {
                    "subject_line": subject,
                    "title": f"Weekly Digest - {datetime.now().strftime('%Y-%m-%d')}",
                    "from_name": "HDR Support",
                    "reply_to": os.getenv("MAIL_DEFAULT_SENDER", "noreply@uwa.edu.au"),
                    "use_conversation": False,
                    "authenticate": True,
                    "auto_footer": False,
                    "inline_css": True
                }
            }
            
            # Create the campaign
            campaign = self.client.campaigns.create(campaign_body)
            campaign_id = campaign["id"]
            
            # Set the campaign content
            content_body = {
                "html": html_content,
                "text": text_content or self._html_to_text(html_content)
            }
            
            self.client.campaigns.set_content(campaign_id, content_body)
            
            # Send the campaign
            self.client.campaigns.send(campaign_id)
            
            logging.info(f"Weekly digest sent successfully to {email}")
            return campaign_id
            
        except ApiClientError as e:
            logging.error(f"Mailchimp API error sending digest to {email}: {e.text}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error sending digest to {email}: {e}")
            raise

    def _html_to_text(self, html_content):
        """
        Convert HTML content to plain text for text version of email
        Simple implementation - could be enhanced with proper HTML parsing
        """
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def create_digest_template(self, messages, user_data):
        """
        Create HTML content for weekly digest email
        
        Args:
            messages: List of messages for the current week
            user_data: User information for personalization
            
        Returns:
            HTML content for the digest email
        """
        current_week = user_data.get('current_week', 1)
        first_name = user_data.get('first_name', 'Student')
        
        # Start building the HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weekly Digest - Week {current_week}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1f2937; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
                .week-info {{ background-color: #f3f4f6; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .message {{ background-color: white; border: 1px solid #e5e7eb; padding: 20px; margin-bottom: 15px; border-radius: 5px; }}
                .message-title {{ font-size: 18px; font-weight: bold; color: #1f2937; margin-bottom: 10px; }}
                .message-content {{ margin-bottom: 10px; }}
                .footer {{ background-color: #f9fafb; padding: 15px; text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }}
                .no-messages {{ text-align: center; padding: 40px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HDR Support Weekly Digest</h1>
                <p>Week {current_week} - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="week-info">
                <h2>Hello {first_name}!</h2>
                <p>Here are your personalized messages and updates for this week.</p>
            </div>
        """
        
        if messages:
            html_content += f"<h3>Messages for Week {current_week}:</h3>"
            
            for message in messages:
                html_content += f"""
                <div class="message">
                    <div class="message-title">{message.get('title', 'Important Update')}</div>
                    <div class="message-content">{message.get('content', '')}</div>
                </div>
                """
        else:
            html_content += """
            <div class="no-messages">
                <h3>No new messages this week</h3>
                <p>You're all caught up! Check back next week for new updates.</p>
            </div>
            """
        
        # Add footer
        html_content += """
            <div class="footer">
                <p>This is an automated weekly digest from HDR Support at UWA.</p>
                <p>If you have any questions, please contact your HDR support team.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
