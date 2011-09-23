#!/bin/bash
#Cron task for redmine_pyreminder.

#get today's date
TODAY=`date +"%w"`

#send reminders mon-fri only
if [[ "$TODAY" != "0" ]] && [[ "$TODAY" != "6" ]] ; then
   logger "Sending Redmine email reminder."
   cd /opt/redmine_pyreminder/src && python pyreminder.py -o -c -s -w --db_host="localhost" --db_user="root" --db_password="password" --smtp_host="192.168.0.100"
fi

