from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def log_tasks(service):
	def save_task(start,end,name):
		event = {
			"summary": name,
			"start": {
				"dateTime": start.isoformat(),
				"timeZone": "America/Los_Angeles"
			},
			"end": {
				"dateTime": end.isoformat(),
				"timeZone": "America/Los_Angeles"
			}
		}

		event = service.events().insert(calendarId='c_dh0f562rhjq4js0jc1mri27qh4@group.calendar.google.com',
			body=event).execute()

	def time_convert(sec):
		mins = sec // 60
		sec = sec % 60
		hours = mins // 60
		mins = mins % 60
		return int(hours),int(mins),int(sec)

	def incr_task(task_initial, time_elapsed):
		for task_name in time_per_task.keys():
			initial = task_name[0]
			if initial == task_initial.lower():
				time_per_task[task_name] += time_elapsed
				return task_name
		return 0

	time_per_task = {
		"meetings": 0,
		"learning": 0,
		"experiments": 0,
		"writing": 0,
		"coursework": 0,
		"teaching": 0,
		"break": 0
	}

	prev_task = input("Current task (M/L/E/W/C/T/B/Q): ")
	start_time = datetime.datetime.now()

	while True:
		task = input("Current task (M/L/E/W/C/T/B/Q): ")
		end_time = datetime.datetime.now()

		time_elapsed = int((end_time - start_time).total_seconds())
		
		result = incr_task(prev_task, time_elapsed)

		prev_task = task

		if task.lower() == "q":
			save_task(start_time,end_time,result)
			break
		elif result == 0:
			print("Didn't recognize that, try again.")
		else:
			save_task(start_time,end_time,result)
			start_time = datetime.datetime.now()

	for task,time in time_per_task.items():
		print(f'{task}:\t{time_convert(time)}')

def main():
	creds = None

	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	try:
		service = build('calendar', 'v3', credentials=creds)
		log_tasks(service)

	except HttpError as error:
		print('An error occurred: %s' % error)


if __name__ == '__main__':
	main()