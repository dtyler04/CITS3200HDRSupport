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

    def upsert_member(self, email, first_name="", last_name="", status_if_new="pending"):
        sub_hash = self._subscriber_hash(email)
        body = {
            "email_address": email,
            "status_if_new": status_if_new,
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