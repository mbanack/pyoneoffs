#!/usr/bin/python3
from subprocess import Popen,PIPE
import re
import time #whoosh

domains = []
with open('/home/vorok/download/missingdomains.csv','r') as f:
    domains = [line.strip() for line in f.readlines()]

oup = open('/home/vorok/22tech/registrars.csv','a')

cutout_early = 1
for dom in domains:
    if cutout_early > 0:
        #print("~~~ " + dom)
        cmd = "whois " + dom
        p = Popen(cmd, shell=True, stdout=PIPE)
        out, err = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            print("! non-0 return code for " + dom)
        lines = out.splitlines()
        registrar = ""
        ns = []
        for line in lines:
            line = line.decode('utf-8')
            rmatch = re.match("^   Registrar: (.*)",line)
            if rmatch:
                print("matched registrar: " + rmatch.group(1))
                registrar = rmatch.group(1)
            else:
                rmatch2 = re.match(".*Registrar:(.*)$",line);
                if rmatch2:
                    registrar = rmatch2.group(1)
            nsmatch = re.match("^   Name Server: (.*)",line)
            if nsmatch:
                print("matched NS : " + nsmatch.group(1))
                ns.append(nsmatch.group(1))
            else:
                nsmatch2 = re.match("Name Server:(.*)",line)
                if nsmatch2:
                    if len(nsmatch2.group(1).split()) > 0:
                        ns.append(nsmatch2.group(1))
        print(dom + ",\"" + registrar + "\"," + ",".join(ns))
        oup.write(dom + ",\"" + registrar + "\"," + ",".join(ns) + "\r\n")
        oup.flush()
        cutout_early += 1
        time.sleep(20)

oup.close()
