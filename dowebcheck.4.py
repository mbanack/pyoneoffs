#!/usr/local/bin/python
# dowebcheck.4.py
#   Web host enumerator
#   Parses the apache conf to determine which hosts are still on the
#     server based on a DNS lookup.
#   Assumes a monolithic httpd.conf, but wouldn't take much to adapt
#     to vhosts.d style
import re
import os
import string

httpdconffile = open('/usr/local/apache2/conf/httpd.conf','r')
httpdconf = httpdconffile.readlines()
httpdconffile.close()

vhostlines = []

for line in httpdconf:
	if "vaddhost" in line:
		chomp = line[:-1]
		vhostlines.append(chomp)

domains = []
ips = {}
multsfile = open('webcheck-mults.txt','w')
for line in vhostlines:
	match = re.match('.*\((\S+)\) at ([.0-9]+)\:(.*)',line)
	if match is not None:
		domain = match.group(1)
		port = match.group(3)
		print("port is { " + port + " }")
		if domain not in domains:
			domains.append(domain)
			ips[domain] = match.group(2)
		else:
			multsfile.write(domain + " already in domains for vhostline " + line + "\n")
		print(domain)

multsfile.close()
weblocalfile = open('webcheck-local.txt','w')
webnonlocalfile = open('webcheck-nonlocal.txt','w')

wls = []
wnls = []

real_ips = {}
for domain in domains:
	check = os.popen('host -v ' + domain + ' | grep -v \; | grep A | head -n 1').readlines()
	for line in check:
		linechomp = line[:-1]
		domainwords = string.split(linechomp,'\t')
		if ips[domain] == domainwords[-1]:
			print(domain + " at " + ips[domain] + " checks out")
			wls.append(domain)
			weblocalfile.write(domain + "\n")
		else:
			print("{!!} " + domain + " at " + domainwords[-1] + " doesnt match httpd.conf " + ips[domain])
			wnls.append(domain)
			webnonlocalfile.write(domain + "\n")

weblocalfile.close()
webnonlocalfile.close()

print("\n\n\n")

for w in wls:
	if w in wnls:
		print(w + "  " + "in locals and nonlocals")
