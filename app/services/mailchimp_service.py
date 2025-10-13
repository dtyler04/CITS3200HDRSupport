from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
import hashlib, os
from dotenv import load_dotenv
import logging

class MailchimpService:
    def __init__(self):
        load_dotenv()
        self.client = Client()
        self.list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.client.set_config({
            "api_key": os.getenv("MAILCHIMP_API_KEY"),
            "server": os.getenv("MAILCHIMP_SERVER_PREFIX"),
        })

    # Hash mail adress as required by Maichimp API
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
    
    def add_degree_type_tag(self, email, degree_type):
        sub_hash = self._subscriber_hash(email)
        body = {
            "tags": [{"name": degree_type, "status": "active"}]
        }
        try:
            return self.client.lists.update_list_member_tags(self.list_id, sub_hash, body)
        except ApiClientError as e:
            logging.error(f"Mailchimp API error (add_degree_type_tag) for {email} - {degree_type}: {e.text}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error adding degree type tag for {email} - {degree_type}: {e}")
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

    def send_weekly_campaign(self, subject, html_content, segment_opts=None):
        """
        Create and send a Mailchimp campaign to all subscribers
        (or a filtered segment if segment_opts provided).

        Args:
            subject (str): Subject/title of the email.
            html_content (str): HTML or plain content for the campaign body.
            segment_opts (dict, optional): Mailchimp segment options
                                           e.g. filter by tag, location, etc.
        Returns:
            campaign_id (str): The ID of the created Mailchimp campaign.
        """
        try:
            # Create the campaign
            campaign_data = {
                "type": "regular",
                "recipients": {
                    "list_id": self.list_id
                },
                "settings": {
                    "subject_line": subject,
                    "title": f"HDR Weekly Campaign - {subject}",
                    "from_name": "HDR Support",
                    "reply_to": "noreply@hdrsupport.uwa.edu.au"
                },
            }

            # If filtering segment (e.g. tag for week number, degree type)
            if segment_opts:
                campaign_data["recipients"]["segment_opts"] = segment_opts

            campaign = self.client.campaigns.create(campaign_data)
            campaign_id = campaign["id"]

            # Add the content
            self.client.campaigns.set_content(campaign_id, {
                "html": html_content
            })

            # Step 3️⃣ – Send immediately
            self.client.campaigns.send(campaign_id)

            logging.info(f"✅ Weekly campaign '{subject}' sent successfully (ID: {campaign_id})")
            return campaign_id

        except ApiClientError as e:
            logging.error(f"❌ Mailchimp API error sending weekly campaign: {e.text}")
            raise
        except Exception as e:
            logging.error(f"❌ Unexpected error sending weekly campaign: {e}")
            raise