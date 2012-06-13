#!/usr/bin/python
# A Redmine email reminder written in Python.
# Copyright Clay Walker (clayzermk1@gmail.com)
# Licensed under the GPLv2 ONLY
# Distributed at https://github.com/clayzermk1/Redmine-PyReminder

import MySQLdb, smtplib
from optparse import OptionParser
from datetime import date, timedelta

#The number of days to notify about starting issues
DAYS = 7

#Today's date
TODAY_DATE = date.today()

def parse_command_line():
	'''
	Parse the options from the command line.
	'''
	
	usage = "usage: %prog [options]\n\n \"*\" denotes default"
	parser = OptionParser(usage)
	parser.add_option("-o", "--overdue", action="store_true", dest="overdue_flag", 
					help="will notify users about overdue issues (assigned and watched)")
	parser.add_option("-c", "--current", action="store_true", dest="current_flag", 
					help="will notify users about issues coming due (assigned and watched)")
	parser.add_option("-s", "--starting", action="store_true", dest="starting_flag", 
					help="will notify users about issues starting soon (assigned and watched)")
	parser.add_option("-w", "--watched", action="store_true", dest="watched_flag", 
					help="will also send information about issues being watched by a user")
	parser.add_option("--web_host", default="localhost", dest="web_host", metavar="HOST",
					help="address/domain name of Redmine web host (example: \"localhost\"* or \"redmine.example.com\" or \"192.168.1.100\")")
	parser.add_option("--db_host", default="localhost", dest="db_host", metavar="HOST",
					help="address/domain name of MySQL host (example: \"localhost\"* or \"db.example.com\" or \"192.168.1.100\")")
	parser.add_option("--db_name", default="redmine", dest="db_name", metavar="DATABASE",
					help="name of MySQL database (example: \"redmine\"*)")
	parser.add_option("-u", "--db_user", default="root", dest="db_user", metavar="USERNAME",
					help="username for MySQL database (example: \"root\"*)")
	parser.add_option("-p", "--db_password", dest="db_password", metavar="PASSWORD",
					help="password for MySQL database")
	parser.add_option("--smtp_host", default="localhost", dest="smtp_host", metavar="HOST",
					help="address/domain name of SMTP host (example: \"localhost\"* or \"smtp.example.com\" or \"192.168.1.100\")")
	parser.add_option("--smtp_port", default="25", dest="smtp_port", metavar="PORT",
					help="port for SMTP host (example: \"25\"*)")
	parser.add_option("--redmine_email", dest="redmine_email", metavar="EMAIL",
					help="email address for Redmine account on the SMTP host (example: \"redmine@example.com\")")
	parser.add_option("-t", "--test_user", dest="test_user", metavar="USERID",
					help="Redmine user ID to send test emails to")

	(options, args) = parser.parse_args()
	if len(options.__dict__.keys()) < 1:
		parser.exit(-1, "Error: incorrect number of arguments.\n")

	return (options, args)

def get_issues(period, user):
	'''
	Return the issues corresponding to the period ("due_date", "current", "start_date").
	Current is a pseudo-date_type RH requested to mimic the behavior of Redmine Advanced Reminder,
	it does not actually query any field in the database.
	'''

	#Determine the date type based on the period desired
	if period == "due_date":
		date_type = period		
	elif period == "current":
		date_type = "due_date"
	elif period == "start_date":
		date_type = period
	else:
		pass

	#Iterate over our arrays
	issue_types = {'assigned':[], 'watching':[]}
	for (key, val) in issue_types.items():
		
		#Select the appropriate SQL statement
		if key == 'assigned':
			sql = 'SELECT issues.id,projects.name,issues.subject,issues.%s,issue_statuses.name FROM issues,projects,issue_statuses WHERE issues.%s IS NOT NULL && projects.id = issues.project_id && projects.status != "9" && issues.assigned_to_id = "%s" && issues.status_id = issue_statuses.id && issues.status_id != "5" && issues.status_id != "6" && issues.status_id != "12"' % (date_type, date_type, user['id'])
		elif key == 'watching':
			sql = 'SELECT issues.id,projects.name,issues.subject,issues.%s,issue_statuses.name FROM issues,projects,watchers,issue_statuses WHERE issues.%s IS NOT NULL && projects.id = issues.project_id && projects.status != "9" &&  watchers.user_id = "%s" && issues.status_id = issue_statuses.id && watchers.watchable_id = issues.id && issues.status_id != "5" && issues.status_id != "6" && issues.status_id != "12"' % (date_type, date_type, user['id'])
		else:
			pass
		
		#Query the database		
		cursor.execute(sql)
		sql_data = cursor.fetchall()
		
		#Filter the assigned issues for the arg
		for row in sql_data:
			
			if ( (period == "due_date") and (row[3] < TODAY_DATE) ) or \
			( (period == "current") and (row[3] >= TODAY_DATE) and (row[3] <= TODAY_DATE + timedelta(days=DAYS)) ) or \
			( (period == "start_date") and (row[3] >= TODAY_DATE) and (row[3] <= TODAY_DATE + timedelta(days=DAYS)) ):
				val.append({'id':str(row[0]), 'project':row[1], 'subject':row[2], date_type:row[3].strftime('%Y-%m-%d'), 'status':row[4]})				
	
	return (issue_types['assigned'], issue_types['watching'])

def send_email(server, toaddr, subject, body):
	'''
	Sends an email to a user.
	'''
	
	# Add the From: and To: headers at the start!
	fromaddr = options.redmine_email
	msg = ('From: %s\r\nTo: %s\r\nSubject: %s\r\n' % (fromaddr, toaddr, subject))
	msg += body

	#print '%s; %s; %s;' % (fromaddr, toaddr, msg)
	server.sendmail(fromaddr, toaddr, msg)

if __name__ == '__main__':
	#Parse the arguments to the program.
	(options, args) = parse_command_line()
	
	#SMTP server connection.
	smtp_host = smtplib.SMTP(options.smtp_host)
	#smtp_host.set_debuglevel(1)
	
	#Connect to the MySQL DB.
	#db server, user, password
	connection = MySQLdb.connect(host = options.db_host, user = options.db_user, passwd = options.db_password, db = options.db_name)
	cursor = connection.cursor()

	#Get the active users names, emails, and ids
	cursor.execute('SELECT id,firstname,lastname,mail FROM users WHERE status = "1" && type = "User" && id > "1" && id != "23"')
	users_data = cursor.fetchall()
	
	#Put the users data into a usable format
	users = []
	for row in users_data:
		users.append({'id':str(row[0]), 'firstname':row[1], 'lastname':row[2], 'mail':row[3]})
		
	#For each user find issues
	for user in users:

		total_issues = 0

		email_subject = 'Redmine Reminder: '
		email_body = '\r\n'

		#Build the body of the email
		if options.overdue_flag == True:
			(assigned_overdue_issues, watched_overdue_issues) = get_issues("due_date", user)
			total_issues += len(assigned_overdue_issues) + len(watched_overdue_issues)
			email_subject += '%s issues are overdue. ' % (len(assigned_overdue_issues))
			email_body += '+ Overdue Issues: +\r\n\r\n'
			email_body += 'Assigned to You: (%s)\r\n' % (len(assigned_overdue_issues))
			if len(assigned_overdue_issues) == 0:
				email_body += 'None\r\n\r\n'
			else:
				for issue in assigned_overdue_issues:
					email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in assigned_overdue_issues])), issue['project'].ljust(max([len(i['project'])for i in assigned_overdue_issues])), issue['subject'].ljust(max([len(i['subject'])for i in assigned_overdue_issues])), issue['due_date'].ljust(max([len(i['due_date'])for i in assigned_overdue_issues])), issue['status'].ljust(max([len(i['status'])for i in assigned_overdue_issues])))
				email_body += 'http://%s/issues?assigned_to_id=%s&set_filter=1&sort_key=due_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])
			if options.watched_flag == True:
				email_body += 'Watched by You: (%s)\r\n' % (len(watched_overdue_issues))
				if len(watched_overdue_issues) == 0:
					email_body += 'None\r\n\r\n'
				else:
					for issue in watched_overdue_issues:
						email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in watched_overdue_issues])), issue['project'].ljust(max([len(i['project'])for i in watched_overdue_issues])), issue['subject'].ljust(max([len(i['subject'])for i in watched_overdue_issues])), issue['due_date'].ljust(max([len(i['due_date'])for i in watched_overdue_issues])), issue['status'].ljust(max([len(i['status'])for i in watched_overdue_issues])))
					email_body += 'http://%s/issues?watcher_id=%s&set_filter=1&sort_key=due_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])

		if options.current_flag == True:
			(assigned_current_issues, watched_current_issues) = get_issues("current", user)
			total_issues += len(assigned_current_issues) + len(watched_current_issues)
			email_subject += '%s issues are coming due. ' % (len(assigned_current_issues))
			email_body += '+ Issues due in the next %s days: +\r\n\r\n' % (DAYS)
			email_body += 'Assigned to You: (%s)\r\n' % (len(assigned_current_issues))
			if len(assigned_current_issues) == 0:
				email_body += 'None\r\n\r\n'
			else:
				for issue in assigned_current_issues:
					email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in assigned_current_issues])), issue['project'].ljust(max([len(i['project'])for i in assigned_current_issues])), issue['subject'].ljust(max([len(i['subject'])for i in assigned_current_issues])), issue['due_date'].ljust(max([len(i['due_date'])for i in assigned_current_issues])), issue['status'].ljust(max([len(i['status'])for i in assigned_current_issues])))
				email_body += 'http://%s/issues?assigned_to_id=%s&set_filter=1&sort_key=due_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])
			if options.watched_flag == True:
				email_body += 'Watched by You: (%s)\r\n' % (len(watched_current_issues))
				if len(watched_current_issues) == 0:
					email_body += 'None\r\n\r\n'
				else:
					for issue in watched_current_issues:
						email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in watched_current_issues])), issue['project'].ljust(max([len(i['project'])for i in watched_current_issues])), issue['subject'].ljust(max([len(i['subject'])for i in watched_current_issues])), issue['due_date'].ljust(max([len(i['due_date'])for i in watched_current_issues])), issue['status'].ljust(max([len(i['status'])for i in watched_current_issues])))
					email_body += 'http://%s/issues?watcher_id=%s&set_filter=1&sort_key=due_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])
			
		if options.starting_flag == True:
			(assigned_starting_issues, watched_starting_issues) = get_issues("start_date", user)
			total_issues += len(assigned_starting_issues) + len(watched_starting_issues)
			email_subject += '%s issues are starting.' % (len(assigned_starting_issues))
			email_body += '+ Issues starting in the next %s days: +\r\n\r\n' % (DAYS)
			email_body += 'Assigned to You: (%s)\r\n' % (len(assigned_starting_issues))
			if len(assigned_starting_issues) == 0:
				email_body += 'None\r\n\r\n'
			else:
				for issue in assigned_starting_issues:
					email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in assigned_starting_issues])), issue['project'].ljust(max([len(i['project'])for i in assigned_starting_issues])), issue['subject'].ljust(max([len(i['subject'])for i in assigned_starting_issues])), issue['start_date'].ljust(max([len(i['start_date'])for i in assigned_starting_issues])), issue['status'].ljust(max([len(i['status'])for i in assigned_starting_issues])))
				email_body += 'http://%s/issues?assigned_to_id=%s&set_filter=1&sort_key=start_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])
			if options.watched_flag == True:
				email_body += 'Watched by You: (%s)\r\n' % (len(watched_starting_issues))
				if len(watched_starting_issues) == 0:
					email_body += 'None\r\n\r\n'
				else:
					for issue in watched_starting_issues:
						email_body += ' * %s - %s - %s - %s - %s\r\n' % (issue['id'].ljust(max([len(i['id'])for i in watched_starting_issues])), issue['project'].ljust(max([len(i['project'])for i in watched_starting_issues])), issue['subject'].ljust(max([len(i['subject'])for i in watched_starting_issues])), issue['start_date'].ljust(max([len(i['start_date'])for i in watched_starting_issues])), issue['status'].ljust(max([len(i['status'])for i in watched_starting_issues])))
					email_body += 'http://%s/issues?watcher_id=%s&set_filter=1&sort_key=start_date&sort_order=asc\r\n\r\n' % (options.web_host, user['id'])

		#Send an email.
		if ( ( (user['id'] == options.test_user) or (options.test_user == None) ) and (total_issues > 0) ): 
			send_email(smtp_host, user['mail'], email_subject, email_body)
		
	#Clean up.
	cursor.close()
	connection.close()
	smtp_host.quit()

