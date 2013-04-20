#!/usr/bin/python3
# prune_old.py: prune extraneous old backups
#  save daily backups for 1 week,
#    weekly backups for 1 month,
#    monthly backups for 1 year
#    yearly backups for 4 years
import os
import time #whooosh
import re
import datetime
import math
import subprocess

BAK_DIR = "/mnt/serverbak/automatic/sql/"

backups = {}
backup_dates = {}
fnparser = re.compile('^([^\.]+)\.([^\.]+)\.sql$')
for file in os.listdir(BAK_DIR):
    match = fnparser.match(file)
    if match:
        servername = match.group(1)
        date = match.group(2)
        if servername in backups:
            backups[servername].append(date)
        else:
            backups[servername] = [date]

for servername in backups:
    list.sort(backups[servername])
    list.reverse(backups[servername])

keep_backups = {}
# track deltas btwn successive dates, allow 7 @ < 7
# 4 in [7,30]
# 12 in [31,365]
# 4 in [366..]
for servername in backups:
    num_daily_left = 7
    num_weekly_left = 4
    num_monthly_left = 12
    num_yearly_left = 4
    keep_backups[servername] = []
    last_date = datetime.date.today()
    for timestamp in backups[servername]:
        if len(timestamp) != 8:
            print("bad timestamp " + str(timestamp))
            continue
        y = int(timestamp[0:4])
        m = int(timestamp[4:6])
        d = int(timestamp[6:8])
        delta = last_date - datetime.date(y, m, d)
        if delta.days < 7 and num_daily_left > 0:
            keep_backups[servername].append(timestamp)
            num_daily_left -= 1
        elif delta.days < 31 and num_weekly_left > 0:
            keep_backups[servername].append(timestamp)
            num_weekly_left -= 1
        elif delta.days < 366 and num_monthly_left > 0:
            keep_backups[servername].append(timestamp)
            num_monthly_left -= 1
        elif num_yearly_left > 0:
            keep_backups[servername].append(timestamp)
            num_yearly_left -= 1

# now prune any files that do not have their timestamp in keep_backups
for file in os.listdir(BAK_DIR):
    match = fnparser.match(file)
    if match:
        servername = match.group(1)
        date = match.group(2)
        if date not in keep_backups[servername]:
            os.unlink(BAK_DIR + file)

# send a mail every sunday (through system MTA)
today = datetime.date.today()
if today.weekday() == 6:
    mail_body = "SQL backup pruner run " + today.strftime("%A %B %d, %Y") + "\nThe following backups are being saved:\n\n"
    for servername in keep_backups:
        mail_body += servername + ": " + ",".join(keep_backups[servername]) + "\n"
    mail_body += "\nBackups can be accessed at hypnos:/mnt/serverbak/automatic/sql"
    recipient = 'hosting@22tech.com'
    subject = 'SQL backup report ' + today.strftime("%b %d")
    p = subprocess.Popen(["/usr/bin/mail", "-s", subject, recipient],
			 stdin=subprocess.PIPE)
    p.communicate(mail_body.encode())
