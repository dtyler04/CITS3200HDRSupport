import random, datetime
from flask_mail import Message
from flask import current_app

class EmailOTPService:
    def __init__(self, mail):
        self.mail = mail
        self.otp_store = {}

    def _generate_code(self):
        return random.randint(100000, 999999)

    def send_otp(self, email, subject="Your Verification Code"):
        try:
            code = self._generate_code()
            expiry = datetime.datetime.now() + datetime.timedelta(minutes=10)
            self.otp_store[email] = (code, expiry)

            msg = Message(subject, recipients=[email])
            msg.sender = ("HDR Support", current_app.config["MAIL_USERNAME"])
            msg.body = f"Your 6-digit verification code is: {code}\n\nIt will expire in 10 minutes."
            self.mail.send(msg)
            return True
        except Exception:
            return False

    def verify_otp(self, email, code):
        if email not in self.otp_store:
            return False

        stored_code, expiry = self.otp_store[email]
        if datetime.datetime.now() > expiry:
            del self.otp_store[email]
            return False

        if stored_code == code:
            del self.otp_store[email] 
            return True

        return False