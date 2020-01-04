#!/usr/bin/python2
# -*- coding: utf-8 -*-
################################################################################
#				yt.py - Teil von Kodi-Addon-ARDundZDF
# 	Vorlage https://github.com/nficano/pytube von Nick Ficano (nficano) - die
#	Javascript-bezogenen Anteile spielen bisher keine Rolle (Phoenix-Videos),
#	die Signaturen sind Bestandteile der einzelnen ytplayer-Urls
#	Test-Videos: Augstein und Blome
################################################################################
#	Stand: 03.01.2020
#
#	03.01.2020Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse, urlsplit, parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError

#import urllib2,urllib
#from urllib2 import urlopen
import ssl
import re
import time
import json
from collections import defaultdict	

import resources.lib.util as util	# (util_imports.py)
PLog=util.PLog; get_page=util.get_page; stringextract=util.stringextract;
blockextract=util.blockextract; RSave=util.RSave; make_filenames=util.make_filenames;
seconds_translate=util.seconds_translate; addDir=util.addDir; 

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

Videos = []

# li=ListItem, url=Youtube embed-url aus einer Phoenixseite, vid=Video-ID an url
# width=Breite, height=Höhe, thumb=img-url
# Bsp.: https://www.youtube.com/watch?v=VmsRcGMWHaw
def yt(li, url, vid, width, height, thumb):
	PLog('yt - embed-url: ' + url)
	url = 'https://www.youtube.com/watch?v=' + vid + '&app=mobile'
	PLog('yt - neue url: ' + url)
	PLog(width); PLog(height);PLog(thumb);
	
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}"
	headers=quote(headers)					# headers ohne quotes in get_page leer 
	html, msg = get_page(path=url, header=headers)	
	if html == '':						
		msg1 = 'Fehler in SingleBeitrag: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return 
	PLog(len(html))
	
	
#	pos1 = html.find('"videoDetails"') 	# -> "videoDetails":{"videoId":"VmsRcGMWHaw"
	pos1 = html.find('"assets"') 		# -> "assets":{"js":"\/yts\/jsbin\/player_ia..
	pos2 = html.find('"uploadDate"')	# -> "ownerChannelName":"phoenix","uploadDate":"2019-04-28"}}
	video_data = html[pos1:pos2-1]
	PLog(video_data[:100])
	RSave("/tmp/x.html", video_data, withcodec=True) # Debug
	html = html.replace('\\/', '/')
	

#	title = video_data.get("args", {}).get("title")
	title = stringextract('title":"', '"', html)
	PLog(title)
#	js_partial_url = video_data.get("assets", {}).get("js")
	js_partial_url = stringextract('js":"', '"', html)
	# Rewrite and add the url to the javascript file, we'll need to fetch
	# this if YouTube doesn't provide us with the signature.
	if js_partial_url.startswith('//'):
		js_url = 'http:' + js_partial_url
	elif js_partial_url.startswith('/'):
		js_url = 'https://youtube.com' + js_partial_url
	PLog("js_partial_url: " + js_partial_url)

	filename = title						# 
	filename = make_filenames(title)		# für ev. Download-Erweiterung
	PLog(filename)
	
	SecureUrl = stringextract('"flashSecureUrl":', '"ownerProfileUrl', video_data)
	title = stringextract('title":{"simpleText":"', '"}', SecureUrl)
	summ = stringextract('description":{"simpleText":"', '"}', SecureUrl)
	sec = stringextract('lengthSeconds":"', '"', SecureUrl)	# Bsp. 2683
	duration = seconds_translate(sec)
	PLog('SecureUrl: %s' % (SecureUrl))
	PLog(title); PLog(summ); PLog(duration)
	summ = u"Dauer %s\n\n%s" % (duration, summ)
	summ_par = summ.replace('\n', '||')
	

	stream_map = stringextract('"streamingData', '"videostatsPlaybackUrl"', html)
	stream_map = stream_map.replace('\\', '')
	PLog(len(stream_map))
	video_urls = blockextract('"itag', stream_map)
	PLog(len(video_urls))
	PLog(video_urls[0])
	sigs = blockextract('signature=', html)
	sig = stringextract('signature=', '\\', sigs[-1])	# aus letztem Block (von 4)
	PLog('sig: ' + sig)

	build_videolist(video_urls, url, filename)
	PLog(len(Videos))
	Videos.sort()		# sortiert invers - größter Wert am Schluss
	PLog('Ausgabe:')
	PLog(Videos[0])

	i=1
	for video in Videos:					
		url = video[0]						# kompl.: stream_url + Metadaten
		PLog('url: ' + url[:100])
		# filename = video[1]       		# s.o. - hier nicht benötigt
		stream_url =  stringextract('url":"', '"', url)
		if "signature=" not in stream_url:	
			stream_url = "{0}&signature={1}".format(stream_url, sig)
		quality = stringextract('quality":"', '"', url)
		mimeType = stringextract('mimeType":"', ';', url)
		# codecs = stringextract('codecs=', '"', url)
		bitrate = "Bitrate: " + stringextract('bitrate":', ',', url)
		
		tag='Youtube-Video: %s | %s | %s'	% (quality, mimeType, bitrate)
		PLog(stream_url); PLog(title); PLog(tag);		
			
		stream_url=py2_encode(stream_url); title=py2_encode(title); thumb=py2_encode(thumb)
		summ_par=py2_encode(summ_par)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % \
			(quote(stream_url), quote(title), quote_plus(thumb), quote_plus(summ_par))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, 
			thumb=thumb, fparams=fparams, tagline=tag, summary=summ, mediatype='video')			
	
			
		i=i+1

	xbmcplugin.endOfDirectory(HANDLE)

#---------------------------------------------------------------- 
#		Youtube-Funktionen 
#---------------------------------------------------------------- 
QUALITY_PROFILES = {
    # flash
    5: ("flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"),

    # 3gp
    17: ("3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"),
    36: ("3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"),

    # webm
    43: ("webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"),
    100: ("webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"),

    # mpeg4
    18: ("mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"),
    22: ("mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"),
    82: ("mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"),
    83: ("mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"),
    84: ("mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"),
    85: ("mp4", "1080p", "H.264", "3D", "2-2.9", "AAC", "152"),

    160: ("mp4", "144p", "H.264", "Main", "0.1", "", ""),
    133: ("mp4", "240p", "H.264", "Main", "0.2-0.3", "", ""),
    134: ("mp4", "360p", "H.264", "Main", "0.3-0.4", "", ""),
    135: ("mp4", "480p", "H.264", "Main", "0.5-1", "", ""),
    136: ("mp4", "720p", "H.264", "Main", "1-1.5", "", ""),
    298: ("mp4", "720p HFR", "H.264", "Main", "3-3.5", "", ""),

    137: ("mp4", "1080p", "H.264", "High", "2.5-3", "", ""),
    299: ("mp4", "1080p HFR", "H.264", "High", "5.5", "", ""),
    264: ("mp4", "2160p-2304p", "H.264", "High", "12.5-16", "", ""),
    266: ("mp4", "2160p-4320p", "H.264", "High", "13.5-25", "", ""),

    242: ("webm", "240p", "vp9", "n/a", "0.1-0.2", "", ""),
    243: ("webm", "360p", "vp9", "n/a", "0.25", "", ""),
    244: ("webm", "480p", "vp9", "n/a", "0.5", "", ""),
    247: ("webm", "720p", "vp9", "n/a", "0.7-0.8", "", ""),
    248: ("webm", "1080p", "vp9", "n/a", "1.5", "", ""),
    271: ("webm", "1440p", "vp9", "n/a", "9", "", ""),
    278: ("webm", "144p 15 fps", "vp9", "n/a", "0.08", "", ""),
    302: ("webm", "720p HFR", "vp9", "n/a", "2.5", "", ""),
    303: ("webm", "1080p HFR", "vp9", "n/a", "5", "", ""),
    308: ("webm", "1440p HFR", "vp9", "n/a", "10", "", ""),
    313: ("webm", "2160p", "vp9", "n/a", "13-15", "", ""),
    315: ("webm", "2160p HFR", "vp9", "n/a", "20-25", "", "")
}

# The keys corresponding to the quality/codec map above.
QUALITY_PROFILE_KEYS = (
    "extension",
    "resolution",
    "video_codec",
    "profile",
    "video_bitrate",
    "audio_codec",
    "audio_bitrate"
)

# aktuelle itags:
ITAGS = {
    5: ('240p', '64kbps'),
    6: ('270p', '64kbps'),
    13: ('144p', None),
    17: ('144p', '24kbps'),
    18: ('360p', '96kbps'),
    22: ('720p', '192kbps'),
    34: ('360p', '128kbps'),
    35: ('480p', '128kbps'),
    36: ('240p', None),
    37: ('1080p', '192kbps'),
    38: ('3072p', '192kbps'),
    43: ('360p', '128kbps'),
    44: ('480p', '128kbps'),
    45: ('720p', '192kbps'),
    46: ('1080p', '192kbps'),
    59: ('480p', '128kbps'),
    78: ('480p', '128kbps'),
    82: ('360p', '128kbps'),
    83: ('480p', '128kbps'),
    84: ('720p', '192kbps'),
    85: ('1080p', '192kbps'),
    91: ('144p', '48kbps'),
    92: ('240p', '48kbps'),
    93: ('360p', '128kbps'),
    94: ('480p', '128kbps'),
    95: ('720p', '256kbps'),
    96: ('1080p', '256kbps'),
    100: ('360p', '128kbps'),
    101: ('480p', '192kbps'),
    102: ('720p', '192kbps'),
    132: ('240p', '48kbps'),
    151: ('720p', '24kbps'),

    # DASH Video
    133: ('240p', None),
    134: ('360p', None),
    135: ('480p', None),
    136: ('720p', None),
    137: ('1080p', None),
    138: ('2160p', None),
    160: ('144p', None),
    167: ('360p', None),
    168: ('480p', None),
    169: ('720p', None),
    170: ('1080p', None),
    212: ('480p', None),
    218: ('480p', None),
    219: ('480p', None),
    242: ('240p', None),
    243: ('360p', None),
    244: ('480p', None),
    245: ('480p', None),
    246: ('480p', None),
    247: ('720p', None),
    248: ('1080p', None),
    264: ('1440p', None),
    266: ('2160p', None),
    271: ('1440p', None),
    272: ('2160p', None),
    278: ('144p', None),
    298: ('720p', None),
    299: ('1080p', None),
    302: ('720p', None),
    303: ('1080p', None),
    308: ('1440p', None),
    313: ('2160p', None),
    315: ('2160p', None),
    330: ('144p', None),
    331: ('240p', None),
    332: ('360p', None),
    333: ('480p', None),
    334: ('720p', None),
    335: ('1080p', None),
    336: ('1440p', None),
    337: ('2160p', None),

    # DASH Audio
    139: (None, '48kbps'),
    140: (None, '128kbps'),
    141: (None, '256kbps'),
    171: (None, '128kbps'),
    172: (None, '256kbps'),
    249: (None, '50kbps'),
    250: (None, '70kbps'),
    251: (None, '160kbps'),
    256: (None, None),
    258: (None, None),
    325: (None, None),
    328: (None, None),
}

# The keys corresponding to the quality/codec map above.
ITAG_KEYS = (
    "resolution",
    "video_bitrate",
)

#---------------------------------------------------------------- 
def get_video_data(url):		# html = urllib.urlopen(url).read()
	PLog(sys.platform)
	req = urllib2.Request(url)
	if sys.platform == 'linux2':
		try:
			cafile="/etc/ssl/ca-bundle.pem"
			r = urllib2.urlopen(req, cafile=cafile)
			page =  r.read()				
			r.close()
			PLog('urllib2.urlopen linux2 erfolgreich, cafile: ' + cafile)		
		except:
			gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
			r = urllib2.urlopen(req, context=gcontext)
			page =  r.read()				
			r.close()	# Verbindung schließt auch autom.	
			PLog('urllib2.urlopen linux2 Fallback ohne cafile')		
	else:	
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
		r = urllib2.urlopen(req, context=gcontext)
		page =  r.read()				
		r.close()	# Verbindung schließt auch autom.	
		PLog('urllib2.urlopen Windows + andere')
	return page
#---------------------------------------------------------------- 
def parse_stream_map(blob):
	# decode YouTube's stream map.

	# str blob: An encoded blob of text containing the stream map data.

	dct = defaultdict(list)

	# Split the comma separated videos.
	videos = blob.split(",")

	# Unquote the characters and split to parameters.
	videos = [video.split("&") for video in videos]

	# Split at the equals sign so we can break this key value pairs and
	# toss it into a dictionary.
	for video in videos:
		for kv in video:
			key, value = kv.split("=")
			dct[key].append(unquote(value))
			# keys: url, quality, itag, type 
			# print 'key: ' + key			# ohne signature
	# print("decoded stream map: %s", dct)
	return dct
#---------------------------------------------------------------- 
def get_json_data(html):	# html = Textformat
	PLog('get_json_data:'); 
	html = py2_encode(html)
	
	html=stringextract('>var ytplayer', '</script>', html)
	PLog(html[:100])
	# json_start_pattern = bytes("ytplayer.config = ")  # bytes in akt. Plex-Python-Version nicht erlaubt
	json_start_pattern = "ytplayer.config = "
	pattern_idx = html.find(json_start_pattern)
	# In case video is unable to play
	if(pattern_idx == -1):
		print ("Unable to find start pattern.")
	start = pattern_idx + 18					# 
	html = html[start:]

	offset = get_json_offset(html)
	if not offset:
		print ("Unable to extract json.")
	PLog(html[:100]); PLog(offset); PLog(len(html))	
	json_content = json.loads(html[:offset])
	PLog(json_content[:100])
	return json_content

#---------------------------------------------------------------- 
def get_json_offset(html):
	"""Find where the json object starts.
	Fund-Bsp. {"args":{"fexp":"23720702,23735348,..
	:param str html:
		The raw html of the YouTube page.
	"""
	unmatched_brackets_num = 0
	index = 1
	for i, ch in enumerate(html):
		if isinstance(ch, int):
			ch = chr(ch)
		if ch == "{":
			unmatched_brackets_num += 1
		elif ch == "}":
			# unmatched_brackets_num -= 1		# in akt. Plex-Python-Version nicht erlaubt
			unmatched_brackets_num = unmatched_brackets_num -1
			if unmatched_brackets_num == 0:
				break
	else:
		print("Unable to determine json offset.")
	return index + i
#---------------------------------------------------------------- 
def get_cipher(signature, url):											# z.Z. nicht vewendet
	"""Gets the signature using the cipher.

	:param str signature:
		The url signature.
	:param str url:
		The url of the javascript file.
	"""
	reg_exp = re.compile(r'"signature",\s?([a-zA-Z0-9$]+)\(')
	# Cache the js since `_get_cipher()` will be called for each video.
	if not js_cache:
		response = urlopen(url)
		if not response:
			PLog("Unable to open url: {0}".format(url))
		js_cache = response.read().decode()
	try:
		matches = reg_exp.search(js_cache)
		if matches:
			# Return the first matching group.
			func = next(g for g in matches.groups() if g is not None)
		# Load js into JS Python interpreter.
		jsi = JSInterpreter(js_cache)
		initial_function = jsi.extract_function(func)
		return initial_function([signature])
	except Exception as e:
		PLog("Couldn't cipher the signature. Maybe YouTube "
						  "has changed the cipher algorithm. Notify this "
						  "issue on GitHub: {0}".format(e))
	return False
#---------------------------------------------------------------- 
def get_quality_profile_from_url(video_url):
	PLog('get_quality_profile_from_url:'); # PLog(video_url)
	"""Gets the quality profile given a video url. Normally we would just
	use `urlparse` since itags are represented as a get parameter, but
	YouTube doesn't pass a properly encoded url.

	:param str video_url:
		The malformed url-encoded video_url.
	"""
	video_url=py2_encode(video_url)
	reg_exp = re.compile('itag=(\d+)')
	itag = reg_exp.findall(video_url)
	PLog("itag: " + str(itag))
	if itag and len(itag) == 1:
		itag = int(itag[0])
		PLog("itag: " + str(itag))
		# Given an itag, refer to the YouTube quality profiles to get the
		# properties (media type, resolution, etc.) of the video.
#		quality_profile = QUALITY_PROFILES.get(itag)
		quality_profile = ITAGS.get(itag)
		PLog("quality_profile: " + str(quality_profile))
		if not quality_profile:
			return itag, None
		# Here we just combine the quality profile keys to the
		# corresponding quality profile, referenced by the itag.
		return itag, dict(list(zip(QUALITY_PROFILE_KEYS, quality_profile)))
	if not itag:
		PLog("Unable to get encoding profile, no itag found.")
	elif len(itag) > 1:
		PLog("Multiple itags found: %s", itag)
		PLog("Unable to get encoding profile, multiple itags "
						  "found.")
	return None, None
#---------------------------------------------------------------- 
def add_video(url, filename, quality_profile):
	PLog('add_video:')
	"""Adds new video object to videos.

	:param str url:
		The signed url to the video.
	:param str filename:
		The filename for the video.
	:param kwargs:
		Additional properties to set for the video object.
	"""
	# video = Video(url, filename, **kwargs)
	# videos.append(video)
	video = [url, filename, quality_profile]
	Videos.append(video)
	return True
#---------------------------------------------------------------- 
def build_videolist(video_urls, url, filename):		# api.py ab 200
	PLog('build_videolist:')
	# For each video url, identify the quality profile and add it to list
	# of available videos.
	PLog(url)
	for i, url in enumerate(video_urls):
		PLog("get quality profile from url: %s"  % (i + 1))
		endterm = '"audioChannels"'
		pos = url.find(endterm)
		if pos:
			url = url[:pos+len(endterm)+4]
#		try:
		itag, quality_profile = get_quality_profile_from_url(url)
		if not quality_profile:
			PLog("unable to identify profile for itag=%s", itag)
			continue
#		except (TypeError, KeyError) as e:
#			PLog("passing on exception %s", str(e))
#
		# Check if we have the signature, otherwise we'll need to get the
		# cipher from the js.
#		if url.find("signature=") < 0:
#			PLog("signature not in url, attempting to resolve the "
#					  "cipher.")
#			signature = get_cipher(stream_map["s"][i], js_url)		# z.Z. nicht verwendet
#			signature = get_cipher(url, js_url)		# z.Z. nicht verwendet
#			url = "{0}&signature={1}".format(url, signature)
#		else:
#			signature = stringextract('signature=', '&', url)
#			# PLog("signature: " + signature)
		
		if itag:
			add_video(url, filename, quality_profile)
	# Clear the cached js. Make sure to keep this at the end of
	# `from_url()` so we can mock inject the js in unit tests.
	js_cache = None
	return True
#---------------------------------------------------------------- 
# durationToSeconds - ISO 8601 time format
# siehe http://stackoverflow.com/questions/16742381/how-to-convert-youtube-api-duration-to-seconds
# examples :
#	'P1W2DT6H21M32S' - 1 week, 2 days, 6 hours, 21 mins, 32 secs,
#	'PT7M15S' - 7 mins, 15 secs
#
def durationToSeconds(duration):
	try:
		split   = duration.split('T')
		period  = split[0]
		time    = split[1]
	except:
		PLog('durationToSeconds: split >%s< failed' % duration)
		return '?'

	timeD   = {}
	# days & weeks
	if len(period) > 1:
		timeD['days']  = int(period[-2:-1])
	if len(period) > 3:
		timeD['weeks'] = int(period[:-3].replace('P', ''))

	# hours, minutes & seconds
	if len(time.split('H')) > 1:
		timeD['hours'] = int(time.split('H')[0])
		time = time.split('H')[1]
	if len(time.split('M')) > 1:
		timeD['minutes'] = int(time.split('M')[0])
		time = time.split('M')[1]    
	if len(time.split('S')) > 1:
		timeD['seconds'] = int(time.split('S')[0])

	# convert to seconds
	timeS = timeD.get('weeks', 0)   * (7*24*60*60) + \
			timeD.get('days', 0)    * (24*60*60) + \
			timeD.get('hours', 0)   * (60*60) + \
			timeD.get('minutes', 0) * (60) + \
			timeD.get('seconds', 0)

	return timeS
#----------------------------------------------------------------  



