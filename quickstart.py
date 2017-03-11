from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Scheduler'

def get_credentials():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,'calendar-python-quickstart.json')
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def createEventBody(course,desc,days,startt,startd,endt,endd,notes):
	event = {
		"summary" : desc,
		"description" : notes,
		"start" : {
			"dateTime" : startd+"T"+startt,
			"timeZone" : "America/Los_Angeles",
		},
		"end" : {
			"dateTime" : startd+"T"+endt,
			"timeZone" : "America/Los_Angeles",
		},
		"recurrence" : [
			"RRULE:FREQ=WEEKLY;UNTIL="+endd+"T235900Z;BYDAY="+days,
		],
	}
	return event




def main():
	"""Shows basic usage of the Google Calendar API.

	Creates a Google Calendar API service object and outputs a list of the next
	10 events on the user's calendar.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)
	page_token = None
	dupCalFound = False
	calendarid=""
	while True:
		calendar_list = service.calendarList().list(pageToken=page_token).execute()
		for calendar_list_entry in calendar_list['items']:
			if calendar_list_entry['summary'] == "2017 Spring Schedule":
				calendarid = calendar_list_entry['id']
				dupCalFound = True
		page_token = calendar_list.get('nextPageToken')
		if not page_token:
			break
	if not dupCalFound:
		calendar = {
			'summary' : '2017 Spring Schedule',
			'timeZone' : 'America/Los_Angeles'
		}
		created_calendar = service.calendars().insert(body=calendar).execute()
		calendarid = created_calendar['id']
	event = createEventBody("CS-102","Introduction to Programming in C++","MO,WE","09:00:00-08:00","2017-03-05","11:00:00-08:00","20170415","3 credits")
	event = service.events().insert(calendarId=str(calendarid), body=event).execute()
	print ('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
	main()