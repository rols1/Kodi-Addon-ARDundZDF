# -*- coding: utf-8 -*-
################################################################################
#				yt.py - Teil von Kodi-Addon-ARDundZDF
#	vorherige pytube-library von Nick Ficano (nficano) wieder entfernt
# 	(https://github.com/nficano/pytube) - für die frei zugänglichen
#	phoenix-Videos entfällt die Dechiffrierung der Youtube-Signaturen.
#	Damit entfallen auch Importprobleme und die laufende Anpassung an
#	die pytube-library.
#	Test-Videos: Rubriken/Bundestag
#
#	März 2022: ergänzt mit MediathekViewWeb-Funktionen, basierend auf
#		dem api von Dev. bagbag (https://github.com/bagbag), 
#		https://github.com/mediathekview/mediathekviewweb,
#		https://mediathekview.de/news/mediathekviewweb/,
#		https://github.com/mediathekview 
#
#	April 2023: phoenix-Youtube-Videos nicht mehr zugänglich, phoenix-
#		Modul umgestellt auf ARD-new-Funktionen. Youtube-Funktionen
#		yt_get und get_stream_details vorerst nicht mehr genutzt.
#
################################################################################
#
#	17.03.2020 Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	
# 	<nr>4</nr>								# Numerierung für Einzelupdate
#	Stand: 17.05.2024
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
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass


import ardundzdf					# -> test_downloads, Main, start_script, build_Streamlists_buttons
from resources.lib.util import *

ICON_MEHR 		= "icon-mehr.png"
ICON_DIR_WATCH	= "Dir-watch.png"

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])
NAME			= 'ARD und ZDF'
MVW_DATA 		= '{"queries":[{"fields":["title","topic"],"query":"%s"},{"fields":["channel"],"query":"%s"}],"sortBy":"timestamp","sortOrder":"desc","future":false,"offset":%d,"size":%d}'
MVW_DATA_ALL 	= '{"queries":[{"fields":["title","topic"],"query":"%s"}],"sortBy":"timestamp","sortOrder":"desc","future":false,"offset":%d,"size":%d}'

#----------------------------------------------------------------
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
		title_org = "%s\n\n[B]Hinweis:[/B] Download seit 02/2023 nur noch  für Audio (mp4a.40.2) möglich." % title_org
		#title_org = title_org.replace("\n", "||")		# replace in test_downloads
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
		duration = re.search(r'Ms":"(\d+)"', millisecs).group(1)
		duration = seconds_translate(int(int(duration) / 1000))
	except Exception as exception:	
		PLog(str(exception))
		duration = ''			
	
	return duration
	
##################### MediathekViewWeb-Funktionen ######################
# Aufruf aus den div. Hauptmenüs (Setting pref_use_mvw)
# 	
# func-Bsp. (Fallback bei Absturz nach Sofortstart-Abbruch): 
#	resources.lib.ARDnew.Main_NEW
#
def MVWSearch(title, sender, offset=0, query='', home_id='', myfunc=''):
	PLog('MVWSearch:') 
	PLog(title); PLog(sender); PLog(offset); PLog(query); 
	PLog(home_id); PLog(myfunc);
		
	if sender == '':								# Sender gewählt?
		CurSender = Dict("load", 'CurSender')		
		sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)
	
	if query == '':
		query = get_keyboard_input() 
		if query == None or query.strip() == '': 	# None bei Abbruch
			# return								# Absturz nach Sofortstart-Abbruch					
			if myfunc == '':
				myfunc = ardundzdf.Main 
			import importlib
			fparams="{}"  
			fparams = quote(fparams)
			ardundzdf.start_script(myfunc, fparams, is_dict=False)	# Fallback zu myfunc
			return									# ohne return wird hier fortgesetzt
			
	query = query.strip()
	query_org = query
	lsize = 20								# Anzahl pro Liste
	offset=int(offset)
	 
	if "ARD|ZDF" in sender:					# Suche in ARD und ZDF
		data = MVW_DATA_ALL  % (query, offset, lsize)
	else:									# Suche in einz. Sender / Channel
		data = MVW_DATA % (query, sender, offset, lsize)
	PLog("data: " + data)
	
	page, msg = get_mvw_page(data)
	if page == '':	
		msg1 = "Fehler in MVWSearch:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	PLog(type(page))
	page = json.dumps(page)					# tuple -> string
	page = transl_json(page)
	
	page = page.replace('\\"', '"')			# dumps-doublequotes
	page = page.replace('\\"', '*')			# doublequotes			
	#RSave('/tmp/x.json', py2_encode(page)) # Debug
	
	items = blockextract('"channel"', page)
	queryInfo = stringextract('"queryInfo"', '"err"', page)	
	PLog(len(items))
	if len(items) == 0:	
		msg1 = u"Suchwort >%s< leider nicht gefunden" % py2_decode(query)
		MyDialog(msg1, '', '')	
		return	
		
	li = xbmcgui.ListItem()
	if home_id:
		li = home(li, home_id)				# Home-Button
	else:
		li = home(li, NAME)					# Hauptmenü
	
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
		mediatype='video'
	
	PLog("Mark0")
	mark = query
	img = R("suche_mv.png"); cnt=0
	page = py2_decode(page)
	page = transl_json(page)
	totalResults = stringextract('"totalResults":', '}', page)
	PLog(totalResults)
	totalResults = int(totalResults)
	for item in items:
		channel 	= stringextract('"channel":"', '"', item)
		topic 		= stringextract('"topic":"', '"', item)
		title 		= stringextract('"title":"', '"', item)
		title 		= make_mark(mark, title, "", bold=True)	# farbige Markierung
		
		descr 		= stringextract('"description":"', '"', item)
		timestamp 	= stringextract('"timestamp":', ',', item)
		duration 	= stringextract('"duration":', ',', item)
		size 		= stringextract('"size":', ',', item)
		url_website	= stringextract('"url_website":"', '"', item)
		sended 		= stringextract('"filmlisteTimestamp":"', '"', item)
		sid 		= stringextract('"id":"', '"', item)
		
		url_sub 	= stringextract('"url_subtitle":"', '"', item)
		url_med 	= stringextract('"url_video":"', '"', item)		# med?
		url_low 	= stringextract('"url_video_low":"', '"', item)
		url_hd 		= stringextract('"url_video_hd":"', '"', item)

		PLog(timestamp); PLog(sended);
		tstamp = datetime.datetime.fromtimestamp(int(timestamp))
		tstamp = tstamp.strftime("%d. %b. %Y %R")
		sended = datetime.datetime.fromtimestamp(int(sended))
		sended = sended.strftime("%d. %b. %Y %R")
		tstamp = py2_decode(tstamp); sended = py2_decode(sended)
		
		dauer="?"
		if duration != '""':										# z.B. Livestream 
			dauer = seconds_translate(duration)
			
		title = transl_json(title)
		title = repl_json_chars(title)
		descr = transl_json(descr); 
		summ = repl_json_chars(descr)
		
		ut = u"nein"
		if url_sub:
			ut = u"ja"
		tag = u"Dauer: %s | [B]%s[/B] | am: [B]%s[/B] | [B]%s[/B] | UT: %s | Filmliste: %s" % \
			(dauer, channel, sended, topic, ut, tstamp)
		tag = repl_json_chars(tag)
		Plot = "%s||||%s" % (tag, summ)
		
		PLog("Satz2:")
		PLog(title); PLog(url_med); PLog(Plot[:80]); PLog(url_sub)
		
		title=py2_encode(title); Plot=py2_encode(Plot);
		url_sub=py2_encode(url_sub); url_low=py2_encode(url_low); 
		url_med=py2_encode(url_med); url_hd=py2_encode(url_hd)
		fparams="&fparams={'title': '%s','Plot': '%s','home_id': '%s','url_sub': '%s','url_low': '%s','url_med': '%s','url_hd': '%s'}" %\
			(quote(title),quote(Plot),home_id,quote(url_sub),quote(url_low),quote(url_med),quote(url_hd))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSingleVideo",
			fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
		cnt=cnt+1	
	
	PLog(offset); PLog(lsize)										# Mehr-Button
	new_offset = offset + lsize
	PLog("new_offset: %d" % offset)	
	li = xbmcgui.ListItem()											# Kontext-Doppel verhindern
	if new_offset < totalResults:
		title = "Mehr zu: [B]%s[/B]" % query
		tag = "weiter ab  %d | gesamt: %d" % (new_offset+1, totalResults)
		fparams="&fparams={'title': '%s','sender': '%s','offset': '%s','query': '%s','home_id': '%s','myfunc': '%s'}" %\
			(quote(title),sender,str(new_offset),quote(query),home_id,quote(myfunc))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch",
			fanart=img, thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)

	title = u"Merkliste -> MVW-Suche %s: [B]%s[/B]" % (sender,query)# Merkliste-Button	
	tag = "[B]Button für die Merkliste via Kontextmenü[/B]"
	summ = u"%s (ab Suchindex 1).\n\n" % title
	summ = u"%sZur Nutzung in der Merkliste bitte den Button via Kontextmenü hinzufügen" % summ
	fparams="&fparams={'title': '%s','sender': '%s','offset': '%s','query': '%s','home_id': '%s','myfunc': '%s'}" %\
		(quote(title),sender,str(0),quote(query),home_id,quote(myfunc))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch",
		fanart=img, thumb=R(ICON_DIR_WATCH), fparams=fparams, tagline=tag, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# Aufruf: MVWSearch
# Fertigung der Videolisten - bisher nur MP4-Formate gefunden
# 	-> build_Streamlists_buttons (mit opt. Sofortstart)
def MVWSingleVideo(title,Plot,home_id,url_sub='',url_low='',url_med='',url_hd=''):
	PLog('MVWSingleVideo:')
	PLog(url_sub) 
	
	HLS_List=[]; MP4_List=[]; HBBTV_List=[];
	track_add = "MediathekView"
	if url_low:
		title_url = u"%s#%s" % (title, url_low)
		item = u"MP4, %s | %s ** Auflösung %s ** %s" %\
			(track_add, "LOW", "480x270", title_url)
		MP4_List.append(item)
		PLog("item: " + item)
	if url_med:
		title_url = u"%s#%s" % (title, url_med)
		item = u"MP4, %s | %s ** Auflösung %s ** %s" %\
			(track_add, "MED", "640x360", title_url)
		MP4_List.append(item)
		PLog("item: " + item)
	if url_hd:
		title_url = u"%s#%s" % (title, url_hd)
		item = u"MP4, %s | %s ** Auflösung %s ** %s" %\
			(track_add, "HD", "1920x1080", title_url)
		MP4_List.append(item)
		PLog("item: " + item)
	
	ID="MVW"	
	PLog("MP4_List: " + str(len(MP4_List)))
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	Dict("store", '%s_MP4_List' % ID, MP4_List) 
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	
	li = xbmcgui.ListItem(); thumb = R("suche_mv.png")
	geoblock=''; sub_path=url_sub; HOME_ID=home_id
	ardundzdf.build_Streamlists_buttons(li,title,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# get_page in util wegen Post-Daten nicht geeignet
#
def get_mvw_page(data):
	PLog('get_mvw_page:') 
	
	path = "https://mediathekviewweb.de/api/query"
	header = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36", \
		"content-type": "text/plain;charset=UTF-8", "accept": "*/*"}
	data = data.encode('utf-8')

	msg = ''; page = ''	
	try:
		req = Request(path, data=data, headers=header)
		r = urlopen(req)
		PLog(r.info())
		page = r.read()		
	except Exception as e:
		page=''
		msg=str(e)
		PLog(msg)
	
	page = page.decode('utf-8')
	PLog(len(page))
	PLog(page[:100])
	return page,msg

# ----------------------------------------------------------------------
	
	
	
	


