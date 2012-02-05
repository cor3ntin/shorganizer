#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re, string, sys


wiki = sys.argv[1]


shows = set()

try:
	with open(out, 'r') as f:
		for line in f:
			set.add(string.strip(line))
except:
	pass

with open(wiki, 'r') as f:
	for line in f:
		#print line
		result = re.match('\\*\'\'\\[\\[(?:.+)\\|(.+)\\]\\]\'\'.*', line, re.I) or re.match('\\*\'\'\\[\\[(.+)\\]\\]\'\'.*', line, re.I)
		if result:
			print result.group(1)
		#set.add(string.strip(line))
