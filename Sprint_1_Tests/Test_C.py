import mailchimp_marketing as MailchimpMarketing
from datetime import datetime, timedelta

def test_message_list():
    # This will check if the list view renders and populates with 
    # revelent information. We can use Selenium for these checks
    # if we have enough time, but a manual test by the development
    # team will assess the correct rendering and validity of all
    # data on the app.
    pass

def test_calander_view_rendering():
    # This will test if the calander view renders properly with all
    # information populated correctly. However, we expect a manual to be
    # performed, although if time permits we can use Selenium on our app.
    pass

def test_mailchimp_schedule():
    # This is where we would send requests to the mailchimp server, 
    # our test would be successful if we get a response on the client 
    # end with the intended message/reminder.
    pass