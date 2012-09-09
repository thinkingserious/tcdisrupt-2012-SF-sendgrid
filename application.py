import flask
import urllib 
import simplejson
import requests
from flask import render_template, request
from configobj import ConfigObj
from twilio.rest import TwilioRestClient

application = flask.Flask(__name__)

#Set application.debug=True to enable tracebacks on Beanstalk log output.
#Make sure to remove this line before deploying to production.
#application.debug=True

config = ConfigObj('./config.ini')

#Default route
@application.route('/')
def hello_world():
	return render_template('search.html')

#Load the search form
@application.route('/search')
def search():
	return render_template('search.html')

#This function processes the search form
@application.route('/location', methods=['POST'])
def location_search():
	base_url = 'http://api.crunchbase.com/v/1/company/'
	zip_code = request.form['zip_code']
	#Distance in miles
	range = .5
	#Query the CrunchBase API
	url = 'http://api.crunchbase.com/v/1/search.js?geo=' + zip_code + '&range=' + str(range)
	result = simplejson.load(urllib.urlopen(url))
		num_companies = result['total']
	count = 0
	nonfunded = 0
	output = ""

	#I have not implemented pagination, so I'm limiting the results
	if num_companies > 5:
		num_companies = 5 

	if num_companies == 0:
		output = "There are no companies nearby."
		return output

	while (count <= num_companies):
		new_url = base_url + result['results'][count]['permalink'] + '.js'
		#Grab the CrunchBase results for the particular company
		new_result = simplejson.load(urllib.urlopen(new_url))
		#Gather the data requested
        name = new_result['name']
		crunchbase_url = new_result['crunchbase_url']
		overview = new_result['overview']
		number_of_employees = new_result['number_of_employees']
		address1 = new_result['offices'][0]['address1']
		address2 = new_result['offices'][0]['address2']

		#Sometimes we get null return values for the address
		if address1 == None:
			address1 = ""

		if address2 == None:
			address2 = ""

		zip_code = new_result['offices'][0]['zip_code']
		city = new_result['offices'][0]['city']
		state_code = new_result['offices'][0]['state_code'] 
		total_money_raised = new_result['total_money_raised']

		#We don't care about companies who have not raised funding
		if total_money_raised != "$0":
			output += "<strong>Name: " + name + "</strong></br></br>\r\n\r\n"
			output += "Crunchbase URL: " + "<a href=\"" + crunchbase_url + "\">" + crunchbase_url + "</a></br></br>"
			output += "Total Money Raised: " + total_money_raised + "</br></br>"
			output += "Overview: " + overview 
			output += "Number of Employees: " + str(number_of_employees) + "</br></br>"
			output += "Address: </br>" + address1 + " " + address2 + "</br>"
			output += city + ", " + state_code + ", " + zip_code + "</br></br></hr>"  
		else:
			nonfunded = nonfunded + 1

		count = count + 1

	if output == "":
		output = "There are no well funded companies in your area."
		return output

	#The user wants the data to be emailed
	if request.form['action'] == "Email":
		subject = "Crunch Funnel Notification"
		payload = {'to': request.form['email'], 'from': config["from_email"], 'subject': subject, 'html': output, 'api_user': config["api_user"], 'api_key': config["api_key"]}
		r = requests.get("http://sendgrid.com/api/mail.send.json", params=payload)
		output = "Results sent to " + request.form['email']

	#The user wants to the date to sent via SMS. We also send an email with the details
	if request.form['action'] == "Text":
		account_sid = config["account_sid"]
		auth_token = config["auth_token"]
		client = TwilioRestClient(account_sid, auth_token)
		num_companies = (num_companies - nonfunded) + 1
		to_number = request.form['phone']
		text_message = "There are " + str(num_companies) + " near that zip code. Check email for details." 
		message = client.sms.messages.create(to=to_number, from_=config["return_phone_number"], body=text_message)
		subject = "Crunch Funnel Notification"
		payload = {'to': request.form['email'], 'from': config["from_email"], 'subject': subject, 'html': output, 'api_user': config["api_user"], 'api_key': config["api_key"]}
		r = requests.get("http://sendgrid.com/api/mail.send.json", params=payload)
		output = "Results sent to " + request.form['email'] + " and SMS."

	return output

if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=True)
