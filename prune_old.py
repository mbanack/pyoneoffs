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
        if date in keep_backups[servername]:
            print("keeping " + file)
        else:
            print("PRUNING " + BAK_DIR + file)
            os.unlink(BAK_DIR + file)
