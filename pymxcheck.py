#!/usr/local/bin/python
import os

lhnf = open('/etc/mail/local-host-names','r')
lhnc = lhnf.readlines()
lhnf.close()

mapping = {}

for l_pre in lhnc:
	l = l_pre.rstrip()
	dom_to_mx = os.popen("host -v " + l + " | grep -v ^\; | grep MX").readlines()
	if len(dom_to_mx) == 0:
		print("no MX for " + l)
	else:
		dtm = dom_to_mx[0].strip()
		print("dtm is " + dtm)
		mx = dtm.split("\t")[-1].split(" ")[-1]
		mapping[l] = [mx]

for dom in mapping:
	mx = mapping[dom][0]
	mx_to_ip = os.popen("host -v " + mx + " | grep -v ^\; | grep A").readlines()
	if len(mx_to_ip) == 0:
		print("no IP for MX " + mx)
	else:
		mti = mx_to_ip[0].strip()
		if "not found" not in mti:
			print("mti is " + mti)
			ip = mti.split("\t")[-1].split(" ")[-1]
			mapping[dom].append(ip)
		else:
			print("{!!} " + dom + " not found in mx-to-ip lookup")
	ip_to_ptr = os.popen("host -v " + ip + " | grep -v ^\; | grep PTR").readlines()
	if len(ip_to_ptr) == 0:
		print("no PTR for IP " + ip)
	else:
		itp = ip_to_ptr[0].strip()
		print("itp is " + itp)
		ptr = itp.split("\t")[-1].split(" ")[-1]
		mapping[dom].append(ptr)

for i in mapping:
	print(i + " " + str(mapping[i]))

desired_host = raw_input("What host do we want:")

mxdomfile = open('/root/enum/mx-domains','w')

for dom in mapping:
	while len(mapping[dom]) < 3:
		print("{!!} " + dom + " failed: " + str(mapping[dom]) + " ... assuming its here")
		mapping[dom].append(desired_host)
	host = mapping[dom][2]
	if host == desired_host:
		mxdomfile.write(dom + "\n")
	else:
		print("dropping " + dom + " " + str(mapping[dom]))

mxdomfile.close()
