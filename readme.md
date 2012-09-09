This program was a hack we ([Adria](twitter.com/adriarichards) and I) created at the [TechCrunch Disrupt Hackathon 2012 in SF](http://sendgrid.com/blog/sendgrid-at-techcrunch-disrupt-sf-hackathon/).

You can enter your zip code to discover what companies have been funded within a half mile radius. This data can be emailed and/or text messaged to you. This data is useful for job seekers and service providers.

For python library dependencies, see requirements.txt

You will need to create a configuration file (config.ini) in the same directory as the application.py file. See below for a sample.

=== config.ini ===

//[SendGrid API](http://docs.sendgrid.com/documentation/api/) credentials
api_user = your_sendgrid_user_name 
api_key = your_sendgrid_password
from_email = email_you_want_to_show_up_in_the_from_field
//[Twilio API](http://www.twilio.com/docs) credentials
return_phone_number = twilio_return_phone_number
account_sid = twilio_account_sid
auth_token = twilio_auth_token

=== end ===