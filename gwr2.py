#!/usr/bin/python3
# ./gwr2.py HOST PORT STREAM_PATH OUTFILE_PREFIX
# ./gwr2.py ice.somafm.com 80 /groovesalad groovesalad
#
# generic web radio archiver
#   Save streaming web radio in hourly chunks for later listening
#
# the idea here is .. if the net connection drops,
#  we want to keep recording at some point.
# that will need some kind of connection-health check or something...
#
# for now, just archive the stream in hourly chunks.
#  if we lose half an hour, at least we get the next 4...
# .. note: if the connection is still good, theres no reason to close it.

import time
import http.client
import io
import sys


if ( len(sys.argv) < 5 ):
	print("invalid arguments given")
	quit()

HOST = sys.argv[1]
PORT = sys.argv[2]
STREAM_PATH = sys.argv[3]
OUTFILE_PREFIX = sys.argv[4]

waystart = time.localtime()
ws_yr = waystart.tm_year
ws_mon = waystart.tm_mon
ws_day = waystart.tm_mday
ws_hr = waystart.tm_hour

while(1):
	# also need to check if ws_day < now_day
	# when it rolls over ... otherwise the next day will
	# all dump to ..-23

	try:
		now = time.localtime()
		now_yr = now.tm_year
		now_mon = now.tm_mon
		now_day = now.tm_mday
		now_hr = now.tm_hour
		next_hr = now_hr + 1
		
		conn = http.client.HTTPConnection(HOST,PORT)
		conn.request("GET", STREAM_PATH)
		r1 = conn.getresponse()
		print( r1.status, r1.reason )
	
		save_file_name = OUTFILE_PREFIX + \
				"."+str(now_yr)+ \
				"."+str(now_mon)+ \
				"."+str(now_day)+ \
				"-"+str(now_hr)
	
		f = open(save_file_name, 'ab')
	
		while now_hr < next_hr:
			# should add condition: and connection.[alive]
			#						[ or r1.status == 200 ]
			#		otherwise, re-make the connection...
	
			data1 = r1.read(2048)
			f.write(data1)
			now = time.localtime()
			now_hr = now.tm_hour
		
		f.close()
		conn.close()
	except:
		# oh noes!  things went wonky on us...
		# wait a minute, then reopen the connection
		if not f.closed:
			f.close()
		conn.close()
		time.sleep(60)
		
