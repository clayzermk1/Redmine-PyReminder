# Redmine PyReminder

A Redmine email reminder written in python.

## About
Originally, I used the Advanced Reminder plugin
(http://www.redmine.org/plugins/advanced_reminder) which worked very well.
Colleagues began requesting features of the reminder. Unfortunately, I do not
know Ruby and despite trying my best to decipher the plugin's code, could not
fully grasp the workings of the rake script. So I set about building one in
Python that included the requested features.

PyReminder will send emails to each Redmine user reminding them of a
configurable set of issues.

PyReminder is a Python script that is set up as a cron task. All configuration
options are passed via the command line. The script will make several queries
to the Redmine database and send out emails based on the results.

## Getting Started
### Requirements
Tested against:
python 2.4.3
MySQL-python 1.2.1-1
Redmine 1.2.1
mysql Ver 14.12 Distrib 5.0.77, for redhat-linux-gnu (x86_64) using readline 5.1

### Installation
On EL5 Linux:
cd /etc/cron.daily
ln -s /path/to/redmine_pyreminder_cron.sh redmine_pyreminder

Edit redmine_pyreminder_cron.sh and configure it for your database,
SMTP server, and desired notificaitons.

## Documentation
The script has built in help that is accessible by passing it the ``-h`` or ``--help`` 
options.

There are three catagories of issues: overdue, current, and starting.
Overdue issues are issues that have assigned due dates in the past that are
still "open".
Current issues are issues that have an assigned due date from today through the
next 7 days (i.e. issues that will be due within 7 days).
Starting issues are issues that have an assigned start date between today
through the next 7 days (i.e. issues that will be starting within 7 days).

Optionally you can enable or disable watched issues matching the same criteria.

If you would like to test the script without blasting every user in your
database, you can use the ``-t USERID``, ``--test_user=USERID`` options to specify a
single user to send the email to.

## Release History
Nothing yet

## License
Copyright (c) 2011 Clay Walker  
Licensed under the GPLv2 only license.

