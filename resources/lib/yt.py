#!/usr/bin/python2
# -*- coding: utf-8 -*-
################################################################################
#				yt.py - Teil von Kodi-Addon-ARDundZDF
#	Basiert wesentlich auf die pytube-library von Nick Ficano (nficano)
# 	Quelle: https://github.com/nficano/pytube, Lizens siehe Verzeichnis
#	../resources/lib/pytube/LICENSE (MIT License).
#	Die Library wurde für die Verwendung im Kodi-Addon leicht modifiziert,
#	nicht benötigte Teile wurden entfernt.
#	Test-Videos: Augstein und Blome
################################################################################
#	Stand: 07.01.2020
#
#	03.01.2020Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	

from __future__ import absolute_import

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


import ardundzdf					# -> test_downloads 
import resources.lib.util as util
PLog=util.PLog; get_page=util.get_page; stringextract=util.stringextract;
blockextract=util.blockextract; RSave=util.RSave; make_filenames=util.make_filenames;
seconds_translate=util.seconds_translate; addDir=util.addDir; PlayVideo=util.PlayVideo;
repl_json_chars=util.repl_json_chars;

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])


# Enviroment anpassen zum Laden von pytube (Altern.: importlib):
lib_path = os.path.join(ADDON_PATH,'resources','lib')
PLog(lib_path)
sys.path.append(lib_path)
from pytube.__main__ import YouTube
from resources.lib.pytube.streams import Stream
PLog('pytube geladen - V%s | %s | %s' %\
	('9.5.3', 'MIT License', 'Copyright 2019 Nick Ficano'))


# Bsp.: https://www.youtube.com/watch?v=9xfBbAZtcA0 OK
def yt(li, url, vid, title, tag, summ, thumb):
	PLog('yt_embed_url: ' + url)
	watch_url = 'https://www.youtube.com/watch?v=' + vid
	PLog('yt_neue_url: ' + watch_url)
	PLog(tag); PLog(summ);PLog(thumb);
	title_org = title
	
	yt 		= YouTube(watch_url)
	# nur mp4-Videos laden
	Videos 	= yt.streams.filter(file_extension='mp4').all()
	PLog(len(Videos)); PLog(str(Videos))
	
	if SETTINGS.getSetting('pref_video_direct') == 'true': 
		PLog('Sofortstart: yt')
		#  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" 
		#	vcodec="avc1.64001F" acodec="mp4a.40.2">:
		stream = yt.streams.get_by_itag(22) 		 
		yt_url = stream.download(only_url=True)	
		if summ == '':
			summ = tag
		PlayVideo(url=yt_url, title=title, thumb=thumb, Plot=summ, sub_path="")
		return
		
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	i=1
	for video in Videos:
		v = str(video)
		itag 		= stringextract('itag="', '"', v)	
		mime_type 	= stringextract('mime_type="', '"', v)				
		res			= stringextract('res="', '"', v)				
		fps 		= stringextract('fps="', '"', v)				
		vcodec 		= stringextract('vcodec="', '"', v)				
		acodec 		= stringextract('acodec="', '"', v)				
		PLog(video); PLog('itag: ' + itag)
		PLog(res); PLog(fps); PLog(vcodec); PLog(acodec);

		try:									# Videolänge kann fehlen
			duration	= yt.length()
			duration = seconds_translate(sec)
		except:
			duration = ''

		stream = yt.streams.get_by_itag(itag) 
		yt_url = stream.download(only_url=True)				
		PLog('yt_url: ' + yt_url[:100])

		if res == '' and fps == '':
			summ='%s. Youtube-Video (nur Audio): %s'	% (str(i), acodec)
		else:
			if acodec:	
				summ='%s. Youtube-Video: %s | %s | %s | %s'	% (str(i), res, fps, vcodec, acodec)
			else:
				summ='%s. Youtube-Video: %s | %s | %s'	% (str(i), res, fps, vcodec)
		
		download_list.append(summ + '#' + yt_url)	# Download-Liste füllen	(Qual.#Url)
			
		if duration:
			tag = u"Dauer %s | %s" % (duration, tag)
		
		summ_par = "%s||||%s" % (tag, summ) 
		title = "%s. %s" % (str(i),title_org)	
		PLog(title); PLog(tag); PLog(summ)		
			
		yt_url=py2_encode(yt_url); title=py2_encode(title); thumb=py2_encode(thumb)
		summ_par=py2_encode(summ_par)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % \
			(quote(yt_url), quote(title), quote_plus(thumb), quote_plus(summ_par))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, 
			thumb=thumb, fparams=fparams, tagline=tag, summary=summ, mediatype='video')			
			
		i=i+1
		
	if 	download_list:	# Downloadbutton(s), high=0: 1. Video = höchste Qualität	
		# Qualitäts-Index high: hier Basis Bitrate (s.o.)
		title_org = title_org
		summary_org = ''
		tagline_org = repl_json_chars(tag)
		# PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = ardundzdf.test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=0)  

	return li



