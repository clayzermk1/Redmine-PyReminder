#!/bin/bash
#Cron task for redmine_pyreminder, place in "/etc/cron.daily/".

#get today's date
TODAY=`date +"%w"`

#send reminders mon-fri only
if [[ "$TODAY" != "0" ]] && [[ "$TODAY" != "6" ]] ; then
   logger "Sending Redmine email reminder."
   cd /path/to/redmine_pyreminder/src && python pyreminder.py -o -c -s -w --web_host="redmine.example.com" --db_password="password" --smtp_host="smtp.example.com" --redmine_email="redmine@example.com"
fi
