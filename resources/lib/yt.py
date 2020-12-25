# -*- coding: utf-8 -*-
################################################################################
#				yt.py - Teil von Kodi-Addon-ARDundZDF
#	vorherige pytube-library von Nick Ficano (nficano) wieder entfernt
# 	(https://github.com/nficano/pytube) - für die frei zugänglichen
#	phoenix-Videos entfällt die Dechiffrierung der Youtube-Signaturen.
#	Damit entfallen auch Importprobleme und die laufende Anpassung an
#	die pytube-library.
#
#	Test-Videos: Rubriken/Bundestag
################################################################################
#
#	06.01.2020 Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	
#	Stand: 19.11.2020

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
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass


import ardundzdf					# -> test_downloads 
from resources.lib.util import *


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

# 19.12.2020 ytplayer.config nicht mehr vor itag's positioniert - Block-
#	bildung direkt mit itag (s.u.)
def yt_get(url, vid, title, tag, summ, thumb):
	PLog('yt_embed_url: ' + url)
	watch_url = 'https://www.youtube.com/watch?v=' + vid
	PLog('yt_watch_url: ' + watch_url)
	PLog(tag); PLog(summ);PLog(thumb);
	title_org=title; tag_org=tag; summ_org=summ
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')				# Home-Button

	page, msg = get_page(path=watch_url)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 

	#pos1 = page.find('ytplayer.config')	# entf. - s.o.
	
	# String-Behandl. (Verzicht auf json-Funktionen)
	page = page.replace('\\"', '"')
	page = page.replace('\\u0026', '&')
	page = page.replace('\\', '')
	
	duration=''
	if 'approxDurationMs' in page:			# Extrakt aus Webseite 
		duration = get_duration(page)			
	PLog("duration: %s" % duration)
	
	# Video-Konfigs mit loudnessDb begrenzen (n.verw.):
	Videos = blockextract('"itag":', page, '"loudnessDb":') 
	PLog(len(Videos))
	if len(Videos) == 0:
		msg1 = u"Youtube-Video nicht verfügbar."
		msg2 = 'Muster "itag" nicht gefunden'
		msg3 = "Video-ID: watch?v=%s" %	vid	
		MyDialog(msg1, msg2, msg3)
		# return li							# Absturz möglich
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
	if SETTINGS.getSetting('pref_video_direct') == 'true': 
		PLog('Sofortstart: yt_get')
		# itag 22 i.d.R.: 1280x720, mime: video/mp4, codecs: avc1.64001F, mp4a.40.2
		for stream in Videos:
			yt_url, res,fps,bitrate,mime,codecs,itag = get_stream_details(stream)	 
			if '22' in itag:
				break
		if summ == '':
			summ = tag

		summ="%s\n\n%s" % (summ, 'Youtube-Video: Format %s | fps: %s | bit: %s | %s | %s' %\
			(res, fps, bitrate, mime, codecs))	
		PlayVideo(url=yt_url, title=title, thumb=thumb, Plot=summ, sub_path="")
		return
		
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	i=1
	for v in Videos:
		itag 		= stringextract('itag="', '"', v)	
		yt_url,res,fps,bitrate,mime,codecs,itag = get_stream_details(v)
		
		# mime: video/mp4, codecs: avc1.64001F, mp4a.40.2 
		if 'mp4' not in mime or 'mp4' not in codecs:			
			continue
		PLog('itag: ' + itag); 
		PLog('yt_url: ' + yt_url[:100])
		PLog(res); PLog(fps); PLog(bitrate); PLog(mime); PLog(codecs);

		if res == '' and fps == '':
			summ='%s. Youtube-Video (nur Audio): %s'	% (str(i), codecs)
		else:
			summ='%s. Format: %s | fps: %s | bit: %s | %s | %s'	% (str(i), res, fps, bitrate, mime, codecs)
		
		download_list.append(summ + '#' + yt_url)	# Download-Liste füllen	(Qual.#Url)
			
		if duration:
			tag = u"Dauer %s | %s" % (duration, tag_org)
		
		summ_par = "%s||||%s||||%s" % (tag, summ, title_org) 
		title = "%s. %s" % (str(i),title_org)
		PLog("Satz:")	
		PLog(title); PLog(tag); PLog(summ)		
			
		yt_url=py2_encode(yt_url); title=py2_encode(title); thumb=py2_encode(thumb)
		summ_par=py2_encode(summ_par)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % \
			(quote(yt_url), quote(title), quote_plus(thumb), quote_plus(summ_par))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, 
			thumb=thumb, fparams=fparams, tagline=tag, summary=summ, mediatype='video')			
			
		i=i+1

	if 	download_list:	# Downloadbutton(s), high=0: 1. Video = höchste Qualität
		PLog(len(download_list))	
		# Qualitäts-Index high: hier Basis Bitrate (s.o.)
		title_org = title_org
		summary_org = ''
		tagline_org = repl_json_chars(tag)
		# PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = ardundzdf.test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=0)  

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
#  str(stream) durch Aufrufer
def get_stream_details(stream):	
	PLog('get_stream_details:') 
	# PLog(stream)
	
	yt_url		= stringextract('url":"', '"', stream)
	res	= ''
	
	width		= stringextract('width":', ',', stream)
	height		= stringextract('height":', ',', stream)
	if width and height:
		res	= "%sx%s" % (width, height)
	
	fps 		= stringextract('fps":', ',', stream)				
	bitrate		= stringextract('bitrate":', ',', stream)				
	mime 		= stringextract('mimeType":"', ';', stream)
	codecs 		= stringextract('codecs="', '"', stream)				
	itag 		= stringextract('itag":', ',', stream)	
	
	PLog("yt_url: %s,res: %s,fps: %s,bitrate: %s,mime: %s,codecs: %s,itag: %s" %\
		(yt_url,res,fps,bitrate,mime,codecs,itag))
	return 	yt_url,res,fps,bitrate,mime,codecs,itag
# ----------------------------------------------------------------------
# yt_init.length() klappt nicht, daher	
# 	Extrakt aus Webseite (id="player-api" ..)
#	# Bsp. : \"approxDurationMs\":\"4000055\"
# Auf die Sekunden verzichten wir hier.
# 25.05.2020 Anpassung class YouTube (self.millisecs),
#	get_duration entfällt vorerst
def get_duration(page):
	PLog('get_duration:') 

	millisecs = stringextract('"approxDuration', ',', page)
	millisecs = millisecs.replace('\\', '')
	try:
		duration = re.search(u'Ms":"(\d+)"', millisecs).group(1)
		duration = seconds_translate(int(int(duration) / 1000))
	except Exception as exception:	
		PLog(str(exception))
		duration = ''			
	
	return duration
	
	
	
	
	
	
	
	
	
	
	
	
	
	


