#coding:utf8
import re
import sys

f = open('nmap.txt','r')
string = ""
matchIp = re.compile(r'(?<![\.\d])((?:(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(?:2[0-4]\d|25[0-5]|[01]?\d\d?))(?![\.\d])')
matchPort = re.compile(r'\d+/tcp\s+open')
matchSer = re.compile(r'open\s+\w+.+')
matchCVE = re.compile(r'\bCVE[\d-]+')
for line in f.readlines():
	#print (line)
        if "(0 hosts up)" in line:
                print("ERROR: Host appears to be down")
                sys.exit(1)
	m = ''.join(matchIp.findall(line))
	n = ''.join(matchPort.findall(line))[:-4]
	s = ''.join(matchCVE.findall(line))[0:]
	if(m <> ''):
		string +=  m
	if(n <> ''):
		string += 'port:' + n
	if(s <> ''):
		string += s
	if(m <> '' or n <> '' or s <> ''):
		string += '\n'
r = open('vul_info.txt','w')
r.write(string)
r.close()
f.close()
