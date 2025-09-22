from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
import hashlib, os
from dotenv import load_dotenv

class MailchimpService:
    def __init__(self):
        load_dotenv()
        self.client = Client()
        self.list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.client.set_config({
            "api_key": os.getenv("MAILCHIMP_API_KEY"),
            "server": os.getenv("MAILCHIMP_SERVER"),
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
            print("Mailchimp API error:", e.text)
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
            print("Mailchimp API error:", e.text)
            raise

    # Use this when a student unenrolls/finishes from a unit
    def remove_unit_tag(self, email, unit_code):
        sub_hash = self._subscriber_hash(email)
        body = {"tags": [{"name": unit_code, "status": "inactive"}]}
        try:
            return self.client.lists.update_list_member_tags(self.list_id, sub_hash, body)
        except ApiClientError as e:
            print("Mailchimp API error (remove_unit_tag):", getattr(e, "text", str(e)))
            raise