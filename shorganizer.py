#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import string
import difflib

import urllib
import urllib2
import hashlib
import urlparse
import json
import argparse

video_extensions = ['.mkv', '.avi', '.wmv', ".mp4"]
subtitles_extensions = ['.srt']

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


class BetaSeries:
	def __init__( self, key="05ae1d0e581b", user_agent="Shorganizer"):
		self.key = str(key)
		self.user_agent = str(user_agent)
		self.build = BetaSeriesBuilder(self.key, self.user_agent)
		self.shows = dict()

	def all_shows(self):
		if len(self.shows) == 0:
			self.load_shows()
		return self.shows.keys()
			
	def load_shows(self):
		lst = self.build.data(self.build.url("/shows/display/all"))['shows']
		for k, v in lst.iteritems():
				self.shows[v['title'].title()] = v['url']
				
	def shows_display(self, show):
		if not show in self.shows:
			return None
		url = self.build.url("/shows/display/%s" % self.shows[show])
		return self.build.data(url)
		
	def shows_episodes(self, show):
		if not show in self.shows:
			return None
		params = urllib.urlencode({'summary': 1})
		url = self.build.url("/shows/episodes/%s" % self.shows[show], params)
		return self.build.data(url)

	def subtitles_last(self, number="", language=""):
		params = urllib.urlencode({'number': number,  'language': language})
		url = self.build.url("/subtitles/last", params)
		return self.build.data(url)

	def subtitles_show(self, serie, season="", episode="", language="", file_=""):
		if file_: 
			params = urllib.urlencode({'file': file_, 'language': language})
			url = self.build.url("/subtitles/show", params)
		else:
			params = urllib.urlencode({'season': season, 'episode': episode, 'language': language})
			url = self.build.url("/subtitles/show/%s" % serie, params)
		return self.build.data(url)

class BetaSeriesBuilder:
	def __init__(self,  key=None, user_agent=None):
		self.key = key
		self.user_agent = user_agent

	def url(self, method, params=None):
		scheme = 'http'
		netloc = 'api.betaseries.com'
		path = '%s.json' % (method)
		param_key = "key=%s" % self.key
		query = '%s&%s' % (param_key, params)
		return urlparse.urlunparse((scheme, netloc, path, None, query, None))

	def get_source(self, url):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', self.user_agent)]
		source = opener.open(url)
		return source.read()
	def data(self, url):
		#print url
		source = self.get_source(url)
		json_data = json.loads(source)
		return json_data['root']

debug = False
bs = BetaSeries()
shows = dict()
shows_names = dict()


#load shows name
for show in bs.all_shows():
	shows_names[show] = show
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
	show = ''
	season = 0
	number = 0
	videos = dict()
	subtitles = dict()
	name = ''

def clean_name(show):
	for char in ['_', '.', '+']:
		show = string.replace(show, char, ' ')
		show = show.title()
	cn = difflib.get_close_matches(show, shows_names.keys())
	if len(cn) > 0:
		return shows_names[cn[0]]
	return None
	
def episode(show, season, episode):
	if not show in shows:
		shows[show] = dict()
	if not season in shows[show]:
		shows[show][season] = dict()
	if not episode in shows[show][season]:
		ep = Episode()
		ep.show = show
		ep.season = season
		ep.number = episode
		ep.videos = dict()
		ep.subtitles = dict()
		shows[show][season][episode] = ep
		return ep
	return shows[show][season][episode]
	
def add_episode(show, season, number, file):
	ep = episode(show, season, number)
	ep.videos[file] = os.path.getsize(file)
	return ep
	
def set_shows_info():
	for show, seasons, in sorted(shows.iteritems()):
		print 'Downloading list of \'%s\' episodes' % show
		show_info = bs.shows_episodes(show)
		if show_info:
			#print show, show_info
			for season, episodes in sorted(seasons.iteritems()):
				for num, episode in sorted(episodes.iteritems()):
					try:
						episode.name = show_info['seasons'][str(season-1)]['episodes'][str(num-1)]['title']
					except:
						pass
	
def print_list():
	e = 0
	s = 0
	size = 0
	for show, seasons, in sorted(shows.iteritems()):
		for season, episodes in sorted(seasons.iteritems()):
			s = s+1
			for num, episode in sorted(episodes.iteritems()):
				e = e+1
				#size += episode.size
				print show, "S%02dE%02d" %(season,num),episode.name, "      // %d files" %len(episode.videos), " - %d subtitles" % len(episode.subtitles)
				for k, v in episode.videos.iteritems(): size += v 
	print "%d shows - %d seasons %d episodes - %s" % ( len(shows), s, e, prettySize(size))
	
def relocate(dir, pattern):
	for show, seasons, in sorted(shows.iteritems()):
		for season, episodes in sorted(seasons.iteritems()):
			for num, episode in sorted(episodes.iteritems()):
				ctx = {
					"show": show, 
					"season" : season, 
					"episode":num, 
					"episode_str": "S%02dE%02d" % (season,num), 
					"episode_name": episode.name
					}
				i = 0
				for file in episode.videos:
					i++
					name, ext = os.path.splitext(file)
					#print file, "->" , os.path.join(dir, (pattern % ctx)+ext)
					print os.path.join(dir, (pattern % ctx)+ext)+(("."+str(i))if i>1 else "")
				i = 0
				for file, lang in episode.subtitles.iteritems():
					i++
					name, ext = os.path.splitext(file)
					#print file, "->" , os.path.join(dir, (pattern % ctx)+"."+lang+ext)
					print os.path.join(dir, (pattern % ctx)+"."+lang+ext)+(("."+str(i))if i>1 else "")
	
def match_and_add(name, pattern, path):
	for flag in useless_name_flags:
		name = string.replace(name, flag, '')
	date_check = re.match('.*(20\\d{2}).*', name) or re.match('.*(19\\d{2}).*', name)
	if date_check:
		name = string.replace(name, date_check.group(1), '.');
	result = result = re.match(pattern, name, re.I)
	#print name, pattern, result is not None
	if not result : return None
	name = clean_name(result.group(1))
	if not name:
		return False
	return add_episode(name, int(result.group(2)), int(result.group(3)), path)
	
def find_subtitles(dirname, ep, movie_name):
	origin_name = [k for k, v in shows_names.iteritems() if v == ep.show][0]
	regex = ".*(?:%s|%s).*\\D0?%d.0?%d\\D.*?(en|fr|)\\.srt" %  (  #TODO Add more languages
		string.replace(ep.show, " ", "[. +-_]"), string.replace(origin_name, " ", "[. +-_]"), ep.season, ep.number)
	for root, dirs, files in os.walk(dirname):
		for file in files:
			name, ext = os.path.splitext(file)
			if not ext in subtitles_extensions: continue 
			result = re.match(regex, file, re.I)
			if not result : continue
			ep.subtitles[file] = 'en' if not result.group(1) or len(result.group(1)) == 0 else result.group(1) #TODO guess the language by reading the file

def explore_dir(dirname):
	for root, dirs, files in os.walk(dirname):
		for file in files:
			name, ext = os.path.splitext(file)
			if ext in video_extensions : 
				#print "------------------"
				path = os.path.join(root, file)
				ep = None
				movie = False
				
				for mf in movies_flag:
					if mf in name:
						movie = True
						break
				
				if not movie:
					for pattern in show_file_patterns:
						ep = match_and_add(name, pattern, path)
						if ep: break
					
					if not ep:
						for pattern in show_dir_patterns:
							ep = match_and_add(path, pattern, path)
							if ep: break
				if ep:
					find_subtitles(root, ep, name)
				elif debug:
					print path, "Is certainly not an episode"
					

parser = argparse.ArgumentParser()
parser.add_argument('--in', action='append', dest='input',
                    default=[],
                    help='Input path',
                    )
parser.add_argument('--out', action='store', dest='output',
                    help='Output path',
                    )
parser.add_argument('--pattern', action='store', dest='pattern',
                    default='%(show)s/Season %(season)d/%(show)s-%(episode_str)s')
parser.add_argument('--list', action='store_true')
parser.add_argument('--relocate', action='store_true')
parser.add_argument('--debug', action='store_true')
options = parser.parse_args()					

debug = options.debug
						
for dirname in options.input:
	print "Exploring directory " + dirname 
	explore_dir(dirname)
print "--------------------------------"
set_shows_info()
print "--------------------------------"

if options.list:
	print_list()
print "--------------------------------"
if options.relocate and options.output:
	relocate(options.output, options.pattern)
