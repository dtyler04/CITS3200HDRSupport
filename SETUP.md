# Flask-Mail and Mailchimp Setup Guide

This guide explains how to configure Flask-Mail and Mailchimp for this project.

## 1. Create a `.env` File

Create a `.env` file in the `CITS3200HDRSupport/app/` directory. This file will store your environment variables. **Do not commit this file to version control.**

### Example `.env` file:

```
# Flask settings
SECRET_KEY=your_secret_key

# Flask-Mail settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# Mailchimp settings
MAILCHIMP_API_KEY=your_mailchimp_api_key
MAILCHIMP_SERVER_PREFIX=usX  # e.g., us21
MAILCHIMP_LIST_ID=your_mailchimp_list_id
```

## Important Notes

### App Password (Gmail)
- For Gmail, you **must** use an [App Password](https://support.google.com/accounts/answer/185833?hl=en) instead of your regular email password. This is required for security reasons and to allow the app to send emails on your behalf.
- Generate an app password in your Google Account settings under Security > App passwords.
- Never share your app password or commit it to version control.

### Mailchimp
- You can find your API key and server prefix in your Mailchimp account under Account > Extras > API keys.
- The `MAILCHIMP_LIST_ID` is the unique ID of your audience/list.

---

If you have any issues, please contact the team lead or check the README for troubleshooting tips.
