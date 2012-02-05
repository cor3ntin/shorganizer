#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import string
import difflib

video_extensions = ['.mkv', '.avi']
subtitles_extensions = ['srt']

show_file_patterns = [
'(?:[\\.\\ \\- _\\+]*)(?:\\[.*\\])*(?:[\\.\\ \\- _\\+]*)([0-9A-Z\\.\\- _\\+]+[0-9A-Z])(?:[\\.\\ \\- _\\+\\[]?)S(\\d{1,2}).?[EexX]\D*(\\d{2})\D*',
'(?:[\\.\\ \\- _\\+]*)(?:\\[.*\\])*(?:[\\.\\ \\- _\\+]*)([0-9A-Z\\.\\- _\\+]+[0-9A-Z])(?:[\\.\\ \\- _\\+\\[]?)S(\\d{1,2})-(\\d{2})\D*',
'(?:[\\.\\ \\- _\\+]*)(?:\\[.*\\])*(?:[\\.\\ \\- _\\+]*)([0-9A-Z\\.\\- _\\+]+[A-Z])(?:[\\.\\ \\- _\\+\\[])(\\d)(\\d{2})\D*', #show.104 // season 1 ep 04
'(?:[\\.\\ \\- _\\+]*)(?:\\[.*\\])*(?:[\\.\\ \\- _\\+]*)([0-9A-Z\\.\\- _\\+]+[A-Z])(?:[\\.\\ \\- _\\+\\[])(\\d)(\\d{2})\Z',
'(?:[\\.\\ \\- _\\+]*)(?:\\[.*\\])*(?:[\\.\\ \\- _\\+]*)([0-9a-zA-Z\\. _\\-\\+]+?)(?:[\\.\\ \\- _\\+\\[]?)(?:Season|Saison) (\\d+)(?:[\\.\\ \\- _\\+]*)Episode (\\d+).*',
]
show_dir_patterns = [
'.*\\/([0-9a-zA-Z\\. _\\-\\+]+?)(?:[\\.\\ \\- _\\+\\/\\[]?)(?:Season|Saison) (\\d{1,2})\\/(?:\\d?)(\\d{1,2})[^0-9p].*', #/foo/bar/Show Season 1/01, #/foo/bar/Show Season 1/101...., /foo/bar/Show/Season 1/101....
'.*\\/([0-9a-zA-Z\\. _\\-\\+]+?)(?:[\\.\\ \\- _\\+\\/\\[]?)(?:Season|Saison) (\\d{1,2})\\/\\[?(?:\\d+)[Ex\\-](\\d{1,2})[^0-9p].*', #/foo/bar/Show Season 1/1x01
'.*\\/([0-9a-zA-Z\\. _\\-\\+]+?)(?:[\\.\\ \\- _\\+\\/\\[]?)(?:Season|Saison) (\\d{1,2})\\/.*(\\d+)' # #/foo/bar/Show Season 1/balaba-101
]

useless_name_flags = [
'download at superseeds.org', 'Epz-', 'EPZ-', 'H264', 'x264', 'X264', '720p'
]

movies_flag = [
'BluRay', 'DVDRIP', 'TS', 'R5', 'DVDSRC'
]

shows = dict()


#load shows name
shows_names = dict()
try:
	with open('shows', 'r') as f:
		for line in f:
			if line.startswith('#') : continue
			if '=' in line:
				k, s, v = line.partition('=')
				shows_names[string.strip(k)] = string.strip(v)
				continue
			n = string.strip(line)
			shows_names[n] = n
except e:
	print e

def prettySize(size):
	suffixes = [("B",2**10), ("K",2**20), ("M",2**30), ("G",2**40), ("T",2**50)]
	for suf, lim in suffixes:
		if size > lim:
			continue
		else:
			return round(size/float(lim/2**10),2).__str__()+suf

class Episode:
	movie_file = ''
	pattern = ''
	size = 0

def clean_name(show):
	for char in ['_', '.', '+']:
		show = string.replace(show, char, ' ')
	cn = difflib.get_close_matches(show, shows_names.keys())
	if len(cn) > 0:
		return shows_names[cn[0]].title()
	return show.title()

def add_episode(show, season, episode, file, pattern):
	if not show in shows:
		shows[show] = dict()
	if not season in shows[show]:
		shows[show][season] = dict()
	if not episode in shows[show][season]:
		shows[show][season][episode] = Episode()
	shows[show][season][episode].movie_file = file
	shows[show][season][episode].size = os.path.getsize(file)
	shows[show][season][episode].pattern = pattern
	
def print_list():
	e = 0
	s = 0
	size = 0
	for show, seasons, in shows.iteritems():
		for season, episodes in seasons.iteritems():
			s = s+1
			for num, episode in episodes.iteritems():
				e = e+1
				size += episode.size
				print show, "S"+season+"E"+num ,episode.movie_file## os.path.split(episode.movie_file)[1]
	print "%d shows - %d seasons %d episodes - %s" % ( len(shows), s, e, prettySize(size))
	
def match_and_add(name, pattern, path):
	for flag in useless_name_flags:
		name = string.replace(name, flag, '')
	date_check = re.match('.*(20\\d{2}).*', name) or re.match('.*(19\\d{2}).*', name)
	if date_check:
		name = string.replace(name, date_check.group(1), '.');
	result = result = re.match(pattern, name, re.I)
	#print name, pattern, result is not None
	if not result : return False
	add_episode(clean_name(result.group(1)), result.group(2), result.group(3), path, pattern )
	return True

def explore_dir(dirname):
	for root, dirs, files in os.walk(dirname):
		for file in files:
			name, ext = os.path.splitext(file)
			if ext in video_extensions : 
				#print "------------------"
				path = os.path.join(root, file)
				found = False
				movie = False
				
				for mf in movies_flag:
					if mf in name:
						movie = True
						break
				
				if not movie:
					for pattern in show_file_patterns:
						found = match_and_add(name, pattern, path)
						if found: break
					
					if found:
						continue
					
					for pattern in show_dir_patterns:
						found = match_and_add(path, pattern, path)
						if found: break
				
				if not found:
					pass #print path
						
for dirname in [
#'/home/coco',
#'/media'
'/home/coco/qBT_dir/', 
'/media/3d67c614-f864-4ec0-b333-db61756cf437/Download',
'/media/3d67c614-f864-4ec0-b333-db61756cf437/Shows',
'/media/My Passport/',
'/media/IOMEGA_HDD'
]:
	explore_dir(dirname)
print "--------------------------------"
print_list()
