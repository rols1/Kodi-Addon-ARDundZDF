# -*- coding: utf-8 -*-
################################################################################
#				arte.py - Teil von Kodi-Addon-ARDundZDF
#		Kategorien der ArteMediathek auf https://www.arte.tv/de/
#
#	Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	Auswertung via Strings statt json (Performance)
#
################################################################################
# 	<nr>16</nr>										# Numerierung für Einzelupdate
#	Stand: 18.07.2022

# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys, subprocess
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


import ardundzdf					# -> get_query,test_downloads, get_ZDFstreamlinks, build_Streamlists_buttons
from resources.lib.util import *
from resources.lib.phoenix import getOnline

# Globals
ArteKatCacheTime	= 3600					# 1 Std.: 60*60

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 			# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_ARTE		= 'https://www.arte.tv'		# + /de/ nach Bedarf
PLAYLIST 		= 'livesenderTV.xml'	  	# enth. Link für arte-Live											

# Icons
ICON 			= 'icon.png'				# ARD + ZDF
ICON_ARTE		= 'icon-arte_kat.png'		# Bitstream Charter Bold, 60p			
ICON_ARTE_NEW	= 'icon-arte-new.png'		# Bitstream Charter Bold, 60p			
ICON_ARTE_START	= 'icon-arte-start.png'		# Bitstream Charter Bold, 60p				
ICON_DIR_FOLDER	= 'Dir-folder.png'
ICON_MEHR 		= 'icon-mehr.png'
ICON_SEARCH 	= 'arte-suche.png'				
ICON_TVLIVE		= 'tv-arte.png'						
ICON_DIR_FOLDER	= "Dir-folder.png"

# ----------------------------------------------------------------------			
def Main_arte(title='', summ='', descr='',href=''):
	PLog('Main_arte:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button

	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = 'gesucht wird in [B]ARTE.DE[/B]'
		title=py2_encode(title);
		func = "resources.lib.arte.Main_arte"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARTE.DE", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_ARTE), 
			thumb=R("suche_mv.png"), tagline=tag, fparams=fparams)

	title="Suche in Arte-Kategorien"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.arte_Search", fanart=R(ICON_ARTE), 
		thumb=R(ICON_SEARCH), fparams=fparams)
	# ------------------------------------------------------
			
	tag='[B]Arte Livestream[/B]'
	title, summ, descr, vonbis, img, href = get_live_data('ARTE')
	title = repl_json_chars(title)
	
	if img == '':
		img = R(ICON_TVLIVE)
	summ_par = summ.replace('\n', '||')
	summ_par = repl_json_chars(summ_par)
	title=py2_encode(title); href=py2_encode(href); summ_par=py2_encode(summ_par);
	img=py2_encode(img)
	fparams="&fparams={'href': '%s', 'title': '%s', 'Plot': '%s', 'img': '%s'}" %\
		(quote(href), quote(title), quote(summ_par), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.arte_Live", fanart=R(ICON_ARTE),
		thumb=img, fparams=fparams, tagline=tag, summary=summ)

	# ------------------------------------------------------
	title="Kategorien"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Kategorien", fanart=R(ICON_ARTE), 
		thumb=R(ICON_ARTE), fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
# ----------------------------------------------------------------------
# Nutzung EPG-Modul, Daten von tvtoday		
# die json-Seite enthält ca. 4 Tage EPG - 1. Beitrag=aktuell
# 24.06.2020 Nutzung neue Funktion get_ZDFstreamlinks
#
def get_live_data(name):
	PLog('get_live_data:')

	import resources.lib.EPG as EPG
	rec = EPG.EPG(ID='ARTE', mode='OnlyNow')		# Daten holen
	PLog(len(rec))

	if len(rec) == 0:			
		msg1 = 'Sender %s:' % name 
		msg2 = 'keine EPG-Daten gefunden'
		MyDialog(msg1, msg2, '')
		return li
	
	title='Arte'; summ=''; descr=''; vonbis=''; img=''; href=''
	if len(rec) > 0:
		# href (PRG-Seite) hier n.b.
		img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];
		sname = unescape(sname)
		title = sname
		summ = unescape(summ); 
		PLog("title: " + title); 
		summ = "[B]LAUFENDE SENDUNG (%s Uhr) [/B]\n\n%s" % (vonbis, summ)
		title= sname
		try:										# 'list' object in summ möglich - Urs. n.b.
			descr = summ.replace('\n', '||')		# \n aus summ -> ||
		except Exception as exception:	
			PLog(str(exception))
			descr = ''
		PLog(title); PLog(img); PLog(sname); PLog(stime); PLog(vonbis); 

	ard_streamlinks = get_ARDstreamlinks(skip_log=True)
	# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
	for line in ard_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('Arte') in up_low(webtitle): 
			href = href
			break
					
	if href == '':
		PLog('%s: Streamlink fehlt' % 'Arte ')
	if img == '':
		img = thumb									# Fallback Senderlogo (+ in Main_arte)				
	
	return title, summ, descr, vonbis, img, href

####################################################################################################
# arte - TV-Livestream mit akt. PRG
# 23.04.2022 Parseplaylist entfernt (ungeeignet für Mehrkanal-Streams)
def arte_Live(href, title, Plot, img):	
	PLog('arte_Live:')

	li = xbmcgui.ListItem()
	li = home(li, ID='arte')			# Home-Button

	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true'	# Sofortstart
		PLog('Sofortstart: arte_Live')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot)
		return	
							
	Plot_par = Plot.replace('\n', '||')
	
	title=py2_encode(title); href=py2_encode(href); img=py2_encode(img);
	Plot_par=py2_encode(Plot_par);
	label = "Bandbreite und Auflösung automatisch (HLS)"
	tag = Plot.replace('||', '\n')
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': 'false'}" %\
		(quote_plus(href), quote_plus(title), quote_plus(img), quote_plus(Plot_par))
	addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
		fparams=fparams, mediatype='video', tagline=tag) 		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# Webaufruf: BASE_ARTE + '/de/search/?q=%s
# 	Seite html / json gemischt, Blöcke im html-Bereich ohne img-Url's
# 	Problem: Folgeseiten via Web nicht erreichbar
# Api-Call s.u. (div. Varianten, nur 1 ohne Error 401 / 403)
# 27.07.2021 neuer Api-Call
#
def arte_Search(query='', nextpage=''):
	PLog("arte_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='phoenix')	# unbehandelt
	PLog(query)
	query = py2_decode(query)
	if  query == None or query == '':
		return ""
				
	query=py2_encode(query);
	if nextpage == '':
		nextpage = '1'

									
	path = 'https://www.arte.tv/api/rproxy/emac/v3/de/web/pages/SEARCH/?query=%s&mainZonePage=1&page=%s&limit=20' %\
		(quote(query), nextpage)
	if nextpage != '1':									# ab page 2 leicht abweichend
		path = path.replace('pages/SEARCH', 'data/SEARCH_LISTING')
		
	aktpage = stringextract('page=', '&', path)

	page, msg = get_page(path=path, do_safe=False)		# ohne quote in get_page (api-Call)
	if page == '':						
		msg1 = 'Fehler in Suche: %s' % query
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
				
		
	li = xbmcgui.ListItem()
	li = home(li, ID='arte')				# Home-Button

	PLog(len(page))
	# page = page.replace('\\u002F', '/')	# hier nicht erf.	
	page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""

	nexturl = stringextract('"nextPage":"', '"', page)		# letzte Seite: ""
	nextpage = stringextract('page=', '&', nexturl)
	PLog("nextpage: " + nextpage)	

	li,cnt = GetContent(li, page, ID='SEARCH')
	if 	cnt == 0:
		msg1 = "leider keine Treffer zu:"
		msg2 = query
		MyDialog(msg1, msg2, '')	
		return li
		
	
	if nextpage and  int(nextpage) > int(aktpage):			# letzte Seite = akt. Seite
		li = xbmcgui.ListItem()								# Kontext-Doppel verhindern
		img = R(ICON_MEHR)
		title = u"Weitere Beiträge"
		tag = u"weiter zu Seite %s" % nextpage

		query=py2_encode(query); 
		fparams="&fparams={'query': '%s', 'nextpage': '%s'}" % (quote(query), nextpage)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.arte_Search", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Einzel- und Folgebeiträge auch bei Suche möglich. Viele Einzelbeiträge
#	liegen in der Zukunft, bieten aber kleinen Teaser 
#
def GetContent(li, page, ID):
	PLog("GetContent: " + ID)
	
	pre_items=[]; max_pre=0
	if ID == 'SEARCH':
		items = blockextract('"programId"',  page)
	else:
		pos = page.find(u'Auch interessant für Sie')
		if  pos > 0:					# Trennung: Leithema vom Rest
			pre_items = blockextract('"title":"',  page[:pos])			# "{" entf. hier
			max_pre = len(pre_items)
			page = page[pos:]
		items = blockextract('{"title":"',  page)
	if 	len(items) == 0:
		items = blockextract('"programId"',  page)						# Fallback 1		 
	PLog("pre_items: %d, items: %d" % (len(pre_items), len(items)))
	if max_pre > 0:														# Blöcke zusammenlegen
		items = pre_items + items
	
	
	mediatype=''; cnt=0													# Default für mehrfach
	
	for item in items:
		mehrfach=False; katurl=''			
			
		title = stringextract('title":"', '"', item)
		title_raw = title 												# für Abgleich in Kategorien
		pid = stringextract('programId":"', '"', item)		
		url = stringextract('url":"', '"', item)	
		subtitle = stringextract('subtitle":"', '"', item)				# null möglich -> ''
		summ = stringextract('Description":"', '"', item)				# shortDescription, Alt.: teaserText
		img_alt = stringextract('caption":"', '"', item)
		
		if subtitle:													# arte verbindet mit -
			title  = "%s - %s" % (title, subtitle)
		
		img = get_img(item)			
								
		dur = stringextract('duration":', ',', item)					# 5869,
		PLog('dur: ' + dur)
		if dur != "null":
			dur = seconds_translate(dur)
		else:
			mehrfach = True												# ohne Dauer -> Mehrfachbeitrag
		if item.find('isCollection":true') >= 0:						# auch mit Dauer möglich
			mehrfach = True	
			
		geo = stringextract('geoblocking":', '},', item)
		geo = "Geoblock-Info: %s" % stringextract('code":"', '"', geo)	# "DE_FR", "ALL"
		
		start=''; end=''
		start_end = stringextract(u'Verfügbar vom', '"', item)			# kann fehlen
		if start_end:													# beide Zeiten bei Suche, o. Uhrzeit
			# start_end = u'[B]Verfügbar vom %s [/B]' % start_end		# Anzeige vereinheitlichen:
			s = start_end.split()
			if len(s) > 0:
				start = s[0]; end = s[2];
		else:															# Zeiten getrennt, mit Uhrzeit
			start = stringextract('start":"', '"', item)				# hier ohne UTC-Zusatz	
			end = stringextract('end":"', '"', item)					# dto.
			start=time_translate(start)
			end=time_translate(end)
		if start and end:
			start_end = u'[B]Verfügbar vom [COLOR green]%s[/COLOR] bis [COLOR darkgoldenrod]%s[/COLOR][/B]' % (start, end)	

		upcoming  = stringextract('upcomingDate":"', '"', item)			# null möglich -> ''
		if upcoming:													# check Zukunft
			upcoming = getOnline(upcoming, onlycheck=True)
			PLog("upcoming: " + upcoming)
			if 'Zukunft' in upcoming:
				start_end = "%s:%s" % (start_end, upcoming)	
		
		# Beiträge mit 'id":"auch-interessant', 'code":"BONUS"' - im Web:
		#	"Nächstes Video", "Auch interessant für Sie" - entfallen mit
		#	Api-Calls
		if ID == 'SINGLE_MORE':
			title	= u"[COLOR blue]Mehr: %s[/COLOR]" % title
		
		if mehrfach:
			tag = u"[B]Folgebeiträge[/B]"
			if page.find('"link":null') < 0:				# null: weiterer Cluster
				katurl = stringextract('"url":"', '"', item)
				PLog("katurl: " + title)
		else:
			tag = u"Dauer %s\n\n%s\n%s" % (dur, start_end, geo)
			
		title = transl_json(title); title = unescape(title);
		title = repl_json_chars(title); 					# franz. Akzent mögl.
		summ = repl_json_chars(summ)						# -"-
		tag_par = tag.replace('\n', '||')					# || Code für LF (\n scheitert in router)
		
		PLog('Satz1:')
		PLog(mehrfach); PLog(pid); PLog(title); PLog(url); PLog(katurl); 
		PLog(img); PLog(tag[:80]); PLog(summ[:80]);  PLog(geo);
		title=py2_encode(title); url=py2_encode(url);
		pid=py2_encode(pid); tag_par=py2_encode(tag_par);
		img=py2_encode(img); summ=py2_encode(summ);
		
		if mystrip(title) == '':							# Müll
			continue
			
		if mehrfach:
			if ID == 'KAT_START':							# mit Url zurück zu -> Kategorien (id vor Block "title")
				cat = stringextract(u'label":"%s"' % py2_decode(title), '}]}', page) # Sub-Kategorien-Liste ausschneiden
				tag = "Folgeseiten"
				summ = stringextract('description":"', '"', cat)

				fparams="&fparams={'title':'%s', 'path':'%s'}" % (quote(title), quote(url))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Kategorien", fanart=img, 
					thumb=img, tagline=tag, summary=summ, fparams=fparams)
			else:
				if katurl:									# mit Seitensteuerung
					katurl=py2_encode(katurl);
					fparams="&fparams={'katurl': '%s'}" % quote(katurl)
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteCluster", fanart=R(ICON_ARTE), 
						thumb=img, tagline=tag, summary=summ, fparams=fparams)
		
				else:										# ohne Seitensteuerung
					fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(url), quote(title))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", 
						fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)
				

			cnt=cnt+1					
		else:
			if mystrip(dur) == '' or pid == '':
				continue
			#if cnt > max_pre:								# ungenau
			#	tag = u"[COLOR blue]Auch interessant für Sie[/COLOR]\n\n%s" % tag
			if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
				mediatype='video'
			
			fparams="&fparams={'img':'%s','title':'%s','pid':'%s','tag':'%s','summ':'%s','dur':'%s','geo':'%s'}" %\
				(quote(img), quote(title), quote(pid), quote(tag_par), quote(summ), dur, geo)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.SingleVideo", 
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ,  mediatype=mediatype)		
			cnt=cnt+1

	return li, cnt
	
# -------------------------------
# holt Bild aus Datensatz
#
def get_img(item):
	PLog("get_img:")
	
	images = stringextract('resolutions":[', '}],', item)
	# PLog(images)
	images = blockextract('url":', images)
	PLog(len(images))
	
	img=''
	for image in images:
		if 'w":300' in image or 'w":720' in image or 'w":940' in image or 'w":1920' in image:
			img = stringextract('url":"', '",', image)
			break
			
	if img == '':
		img = R(ICON_DIR_FOLDER)
	
	return img
	
# ----------------------------------------------------------------------
# Folgebeiträge aus GetContent
#	-> GetContent -> SingleVideo
# 19.11.2021 ergänzt um weitere Auswertungsmerkmale, Hinw. auf Überschreitung
#	der Ebenentiefe entfernt, dto. 31.01.2022 (Subtitel, Dauer - Bilder 
#	können fehlen bzw. transparent.png)
# 17.02.2022 fehlende Bilder via api-Call ergänzt 
# 23.04.2022 Auswertung Webseite umgestellt auf enth. json-Anteil
# 28.04.2022 Auswertung next_url ergänzt (s. get_ArtePage), Ausleitung zu
#	ArteCluster bei Seiten mit collection_subcollection
#
def Beitrag_Liste(url, title, get_cluster='yes'):
	PLog("Beitrag_Liste: " + title)
	
	page = get_ArtePage('Beitrag_Liste', title, path=url)	
	if page == '':	
		msg1 = "Keine Videos oder Folgeseiten gefunden."
		msg2 = "Eventuell liegen nur redaktionelle Inhalte vor zu:"
		msg3 = "[B]%s[/B]" % title
		MyDialog(msg1, msg2, msg3)
		return
	
	li = xbmcgui.ListItem()
	
	items = blockextract('code":{',  page)
	PLog(len(items))
	if page.find('"collection_subcollection"') > 0 and get_cluster:	# Cluster vorh.?
		PLog("Ausleitung_Cluster")
		ArteCluster(katurl=url)
		
	else:
		li = home(li, ID='arte')									# Home-Button
		li,cnt = GetContent(li, page, ID='Beitrag_Liste') 			# eigenes ListItem
		
		next_url = stringextract('next_url":"', '"', page[-100:]) 	# next_url am Seitenende 
		PLog("next_url4: " + next_url)	
		if next_url:												# Mehr-Beiträge?
			ArteMehr(next_url, first=True)		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	return

# ----------------------------------------------------------------------
# holt die Videoquellen -> Sofortstart bzw. Liste der  Auflösungen 
# tag hier || behandelt (s. GetContent)
# 14.08.2020 Beschränkung auf deutsche + concert-Streams entfernt
#	(Videos möglich mit ausschl. franz. Streams), master.m3u8 wird
#	unverändert ausgewertet.
# 24.09.2020 Filterung master.m3u8 nach "DE" oder "FR"
# 02.04.2022 Nutzung build_Streamlists_buttons mit HLS_List, MP4_List,
#	Vorauswahl Deutsch bei Sofortstart (HLS + MP4)
# 20.04.2022 api (v1 -> v2) und Format geändert. Nur noch HLS-Quellen
# 21.04.2022 neuer api-Call (mit Authorization) aus Java-MServer von 
#	MediathekView
# 15.05.2022 Nutzung api_v2_Call (nur noch HLS-Quellen) plus api_opa_Call 
#	(kurze Teaser-Streams statt vollständ. Videos möglich, im Addon
#	werden MP4- und HBBTV-Quellen verwendet). 
#	Der Sofortstart findet hier statt (sonst build_Streamlists_buttons),
#		um Rekursion (ohne Homebuttons) zu vermeiden (ev. Ursache mit
#		Modulwechsel).
# 
def SingleVideo(img, title, pid, tag, summ, dur, geo):
	PLog("SingleVideo: " + pid)
	title_org = title

	path1 = 'https://api.arte.tv/api/player/v2/config/de/%s' % pid	# nur  HLS-Quellen, ev. Teaser (20.04.2022)
	path2 = "https://api.arte.tv/api/opa/v3/programs/de/%s"  % pid	# Nutzung HBBTV- + MP4-Quellen
	header = "{'Authorization': 'Bearer Nzc1Yjc1ZjJkYjk1NWFhN2I2MWEwMmRlMzAzNjI5NmU3NWU3ODg4ODJjOWMxNTMxYzEzZGRjYjg2ZGE4MmIwOA',\
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',\
		'Accept': 'application/json'}"

	page, msg = get_page(path1, JsonPage=True, do_safe=False)		# api_v2_Call
	if page == '':						
		msg1 = 'Fehler in SingleVideo: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
	page = page.replace('\\/', '/')
	page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
	#RSave('/tmp/x_artestreams_v2.json', py2_encode(page))	# Debug	

	if summ == '':	# ev. nicht besetzt in Beitrag_Liste. Fehlt in stream_* Dateien
		summ = stringextract('description":"',  '"', page)
		summ=transl_json(summ); summ=repl_json_chars(summ)			# -> HLS_List, HBBTV_List, MP4_List
	PLog("summ: " + summ)
	
	hls_add=""; mp4_add=""											# Titelzusatz für Trailer
	trailer_hls, HLS_List = get_streams_api_v2(page,title_org,summ)
	PLog("trailer_hls: " + str(trailer_hls))
	if trailer_hls:													# Trailer eher in MP4_List wahrsch.
		hls_add = ", HLS-Streams: [B]Trailer[/B]"
	
	#-------------------------------------------------------------	# HBBTV- + MP4-Quellen
	page, msg = get_page(path2, JsonPage=True, do_safe=False, header=header)	# api_opa_Call_1
	#RSave('/tmp/x_artestreams_opa1.json', py2_encode(page))	# Debug	
	if page == '':						
		PLog("error_api_opa_Call_1")
	# Abschnitt offlineAvailability enthält Links zu div. Quellen,
	#	z.Z. nur stream_hbbtv genutzt (ent. MP4-Quellen):
	streams = stringextract('"videoStreams":',  ']', page)		
	stream_hbbtv = stringextract('hbbtv":',  '}', streams)
	stream_hbbtv = stringextract('href": "',  '"', stream_hbbtv)
	#stream_web = stringextract('web":',  '}', streams)				# nicht genutzt - s. api_v2_Call
	#stream_web = stringextract('href": "',  '"', stream_web)
	#PLog("stream_web: " + stream_web); 
	PLog("stream_hbbtv: " + stream_hbbtv)

	page, msg = get_page(path=stream_hbbtv, JsonPage=True, do_safe=False, header=header)	# api_opa_Call_2
	if page == '':						
		PLog("error_api_opa_Call_1")
	#RSave('/tmp/x_artestreams_opa2.json', py2_encode(page))	# Debug	
	trailer_mp4, MP4_List = get_streams_api_opa(page, title_org, summ)
	if trailer_mp4:
		mp4_add = ", MP4-Streams: [B]Trailer[/B]"

	HBBTV_List=[]
	PLog("HLS_List: " + str(len(HLS_List)))
	PLog("MP4_List: " + str(len(MP4_List)))
	PLog("HBBTV_List: ohne (=MP4_list)")
			
	if not len(HLS_List) and not len(MP4_List):			
		msg1 = u'SingleVideo: [B]%s[/B]' % title
		msg2 = u'Streams leider (noch) nicht verfügbar.'
		MyDialog(msg1, msg2, '')
		return li
	
	if SETTINGS.getSetting('pref_video_direct') == 'true':			# Sofortstart hier (s.o.) + raus
		PLog('Sofortstart: SingleVideo')
		title_hls = "%s %s" % (title_org, hls_add)
		PlayVideo_Direct(HLS_List, MP4_List, title=title_hls, thumb=img, Plot=summ)
		return 
	#---------
	
	ID = 'arte'
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	Dict("store", '%s_MP4_List' % ID, MP4_List) 

	li = xbmcgui.ListItem()
	li = home(li, ID='arte')					# Home-Button
	
	if hls_add:									# Trailer-Zusatz	
		title = "%s %s" % (title, hls_add)
	if mp4_add:	
		title = "%s %s" % (title, mp4_add)
	tagline = "Titel: %s\n\n%s\n\n%s" % (title, tag, summ)	# s.a. ARD (Classic + Neu)
	tagline=repl_json_chars(tagline); tagline=tagline.replace( '||', '\n')
	Plot=tagline; 
	Plot=Plot.replace('\n', '||')
	sub_path=''
	HOME_ID = ID								# Default ZDF), 3sat
	PLog('Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
		
	ardundzdf.build_Streamlists_buttons(li,title_org,img,geo,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# Auslesen der Streamdetails api-v2-Call (nur HLS)
# Arte verwendet bei HBBTV MP4-Formate wie ZDF (HLS_List bleibt leer)
#
def get_streams_api_v2(page, title, summ):
	PLog("get_streams_api_v2:")
	title_org = title
	
	formitaeten = blockextract('"url":"https', page) # Bsp. "id":"HTTPS_MQ_1", "id":"HLS_XQ_1"
	PLog(len(formitaeten))
	
	HLS_List=[]; trailer=False
	for rec in formitaeten:	
		url = stringextract('"url":"',  '"', rec)
		if url.find("Trailer") > 0:
			trailer = True
		mediaType = stringextract('"protocol":"',  '"', rec)
		bitrate = ""
		
		mainQuality = stringextract('"mainQuality":',  '}', rec)
		quality = stringextract('"code":"',  '"', mainQuality)		# "XQ"
		width = stringextract('"label":"',  '"', mainQuality)		# "720p"
		height="?"
		size = "%sx%s" % (width, height)
		size = size.replace("p", "")
		
		versions = stringextract('"versions":',  '}', rec)
		lang = stringextract('"label":"',  '"', versions)			# z.B. Deutsch (Original)
		lang = transl_json(lang)
		
		PLog('Satz3:')
		PLog(url); PLog(size); PLog(lang);
		
		# versch. Streams möglich (franz, UT, ..) - in Konzert-Streams
		#	Einzelauflösungen alle erlauben (s.o.),
		#	für Sofortstart nur Deutsch auswählen (HLS + MP4)
		#	Downloads (MP4): get_bestdownload berücksichtigt Setting pref_arte_streams
		# skip Parseplaylist für master.m3u8 (arte liefert Auflösungen als master.m3u8)
		if SETTINGS.getSetting('pref_video_direct') == 'true':	
			if lang.strip() != "Deutsch":	# Sofortstart nur Deutsch
				PLog("skip_%s" % lang)
				continue
		if 'master.m3u8' in url:				# HLS master.m3u8 
			HLS_List.append('HLS, [B]%s[/B] ** %s ** AUTO ** %s#%s' % (lang, size, title, url))
		else:
			if ".m3u8" in url:									# HLS
				HLS_List.append('HLS, [B]%s[/B] ** %s ** %s ** %s#%s' % (lang, size, quality, title, url))

	return trailer,HLS_List

# ----------------------------------------------------------------------
# Auslesen der Streamdetails api-opa-Call 
# Arte verwendet bei HBBTV MP4-Formate wie ZDF (HLS_List bleibt leer)
#
def get_streams_api_opa(page, title,summ, mode="hls_mp4"):
	PLog("get_streams_api_opa: " + mode)
	title_org = title

	formitaeten = blockextract('"videoStreamId"', page) 
	PLog(len(formitaeten))
	
	MP4_List=[]; trailer=False
	for rec in formitaeten:	
		versions = stringextract('"versions":',  ']', rec)
		
		mediaType = stringextract('"mediaType": "',  '"', rec)
		bitrate = stringextract('"bitrate":',  ',', rec)
		quality = stringextract('"quality": "',  '"', rec)
		width = stringextract('"width": ',  ',', rec)
		height = stringextract('"height": ',  ',', rec)	
		if height == "": height = "?"
		size = "%sx%s" % (width, height)
		
		url = stringextract('"url": "',  '"', rec)
		if url.find("Trailer") > 0 or url.find("_EXTRAIT_") > 0:	# Trailer-Kennz. (Stand 22.05.2022)
			trailer = True

		lang = stringextract('"audioLabel": "',  '"', versions)	# z.B. Deutsch (Original)
		lang = transl_json(lang)
		shortLabel = stringextract('"audioShortLabel": "',  '"', versions) # Bsp..: "UT" oder "FR"
		
		PLog('Satz5:')
		PLog(url); PLog(size); PLog(lang);
		
		# versch. Streams möglich (franz, UT, ..) - in Konzert-Streams
		#	Einzelauflösungen alle erlauben (s.o.),
		#	für Sofortstart nur Deutsch auswählen (HLS + MP4)
		#	Downloads (MP4): get_bestdownload berücksichtigt Setting pref_arte_streams
		# skip Parseplaylist für master.m3u8 (arte liefert Auflösungen als master.m3u8)
		if ".mp4" in url:										# MP4
			title_url = u"%s#%s" % (title, url)
			mp4 = "MP4 [B]%s[/B]" % lang
			item = u"%s | %s ** Bitrate %s ** Auflösung %s ** %s" %\
				(mp4, quality, bitrate, size, title_url)
			MP4_List.append(item)

	return trailer,MP4_List
	
# ----------------------------------------------------------------------
# BASE_ARTE wird nur zum Auslesen der Kategorien verwendet
#	 -> GetContent (1. Stufe: Kategorienliste)
# 
# Hinw.: die Listen aller Subkats befinden sich sowohl in BASE_ARTE 
#	als auch in den einz. SubKats - alle ohne Bilder
# 13.10.2020 Auswertung Adds hinzugefügt (Aktuelle Highlights, 
#	Kollektionen, Sendungen) durch Laden der akt. SubKat
# 23.10.2020 Erfassung der Adds erweitert (s.u. Adds-Liste)
# 31.01.2021 Stufe 2 aufgrund der unsicheren Adds (dynamisch) geändert: 
#	keine Differenz. mehr für Titel + Pfadinhalte (z.B. Concert), Übergabe
#	der Katseite (path) für intrins. Inhalte + der verlinkten Webseite
#	(link_url). KatSub extrahiert den Seiten-Ausschnitt (-> GetContent).
#	Falls die Beitragszahl < 2 ist, lässt KatSub zusätzl. die verlinkte 
#	Webseite auswerten. Die Seitensteuerung folgt zum Schluss (nexturl).  
# 10.05.2021 Webseite geändert: Abschluss Kategorien nun ab
#	page.find('"pageNumber"', pos1+300). Auswertung der zusätzl. Beiträge
#	belassen.
# 26.04.2022 Abschluss Kategorien nach Auswertung "Wissenschaft",
#	Button Startseite hinzugefügt, Codebereinigung (gelöscht:  Kategorie_Dokus,
#	get_subkats, KatSub, neu: ArteCluster, ArteMehr, get_cluster, get_next_url)
# 15.05.2022 Kat-Liste + Kat-Icons nicht mehr auf den Webseiten enthalten, neue
#	Icons gefertigt + Kat-Liste hier mit Links vorgegeben 
#
def Kategorien():
	PLog("Kategorien:")

	li = xbmcgui.ListItem()
	li = home(li, ID='arte')				# Home-Button
	
	cat_list = ["Dokus und Reportagen|arte_dokus.png|/videos/dokumentationen-und-reportagen/", 
				"Kino|arte_kino.png|/videos/kino/",
				"Fernsehfilme und Serien|arte_filme.png|/videos/fernsehfilme-und-serien/", 
				"Aktuelles und Gesellschaft|arte_act.png|/videos/aktuelles-und-gesellschaft/",
				"Kultur und Pop|arte_kultur.png|/videos/kultur-und-pop/", 
				"ARTE Concert|arte_conc.png|/arte-concert/",
				"Wissenschaft|arte_science.png|/videos/wissenschaft/", 
				"Entdeckung der Welt|arte_entdeck.png|/videos/entdeckung-der-welt/", 
				"Geschichte|arte_his.png|/videos/geschichte/"
				]
	
	path = "https://www.arte.tv/de/"
	path=py2_encode(path)
	fparams="&fparams={'katurl': '%s'}" % quote(path)			# Button Startseite
	addDir(li=li, label="Startseite", action="dirList", dirID="resources.lib.arte.ArteCluster", fanart=R(ICON_ARTE), 
		thumb=R(ICON_ARTE_START), fparams=fparams)
	

	pre = "https://www.arte.tv/de"		
	for item in cat_list:											# Kategorien listen
		title, img, katurl = item.split("|")
		katurl = pre + katurl
		
		PLog('Satz4:')
		PLog(title); PLog(katurl);
		title=py2_encode(title); katurl=py2_encode(katurl)		# ohne title, katurl laden
		fparams="&fparams={'title': '', 'katurl': '%s'}" % quote(katurl)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteCluster", fanart=R(ICON_ARTE), 
				thumb=R(img), fparams=fparams)

	title = "Neueste Videos"									# Button Neueste Videos
	path = "https://www.arte.tv/de/videos/neueste-videos/"
	path=py2_encode(path)
	fparams="&fparams={'title': '%s', 'url': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", fanart=R(ICON_ARTE), 
		thumb=R(ICON_ARTE_NEW), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------------------------------------
# Webseite arte.tv ohne Kategorien
# Aufrufer: Kategorien / ArteCluster
# 2 Durchläufe: 1. Liste Cluster, 2. Cluster-Details
# Mehr-Seiten:  -> get_ArtePage mit katurl, ohne Dict_ID
#
def ArteCluster(title='', katurl=''):
	PLog("ArteCluster: " + title)
	PLog(katurl); 
	katurl_org=katurl

	page = get_ArtePage('ArteCluster', title, path=katurl)	
	next_url = stringextract('next_url":"', '"', page[-100:]) # next_url am Seitenende 
	PLog("next_url2: " + next_url)					# next_url1 s. get_ArtePage
	
	pos = page.find("footerProps")					# Footer kann skip_items enth.
	if pos > 0:
		page = page[:pos]
	items = blockextract('code":{',  page)			# ArteStart_1 + ArteStart_2
	PLog(len(items))
	img_def = R(ICON_DIR_FOLDER)

	li = xbmcgui.ListItem()
	
	# contentId: Login-relevante Beiträge, 	ohne Beiträge: 'data":[]'
	skip_item = [u'"Alle Kategorien', u'"contentId',  u'"Newsletter',
				u'"ARTE Magazin', u'"Meine Liste', u'Demnächst',
				 u'Zum selben Thema', u'Collection Articles', u'Collection Partners',
				 u'Collection Upcomings', u'"collection_content"',
				 u'data":[]']
					
	if title == '':								# 1. Durchlauf
		PLog('ArteStart_1:')
		PLog(page[:100])
		li = home(li, ID='arte')					# Home-Button
		for item in items:
			title = stringextract('title":"', '"', item)
			title = transl_json(title)
			label = title
							
			img = get_img(item)
			if img == '':
				img = img_def
			
			if item.find('"link":null') < 0:				# null: Beiträge, sonst weiterer Cluster
				katurl = stringextract('"url":"', '"', item)
				title=''
			else:
				katurl = katurl_org

			skip=False
			for s in skip_item:
				if item.find(s) > 0: PLog(s); skip=True
			if skip: 
				PLog("skip: " + title)
				continue
				
			PLog('Satz2:')
			PLog(title); PLog(katurl);
			
			title=py2_encode(title); katurl=py2_encode(katurl);
			if '"title":"Alle Videos"' in item:				# einz. Videos listen
				fparams="&fparams={'title': '%s','url': '%s','get_cluster': ''}" %\
					(quote(title), quote(katurl))
				addDir(li=li, label=label, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", 
					fanart=R(ICON_ARTE), thumb=img, fparams=fparams)
		
			else:
				fparams="&fparams={'title': '%s', 'katurl': '%s'}" % (quote(title), quote(katurl))
				addDir(li=li, label=label, action="dirList", dirID="resources.lib.arte.ArteCluster", 
					fanart=R(ICON_ARTE), thumb=img, fparams=fparams)

	else:												# 2. Durchlauf
		PLog('ArteStart_2:')
		PLog(page[:100])								# identisch mit ArteStart_1 ?
		name_org=name; title_org=title
		page = get_cluster(items, title_org)
		if page  == '':	
			return
			
		PLog(page[:80])
		if page.find('"link":null') < 0:				# null: Beiträge, sonst weiterer Cluster
			katurl = stringextract('"url":"', '"', page)
			page = get_ArtePage('ArteStart_2', title, path=katurl)
			ArteCluster(title=title_org, katurl=katurl)
			
		else:											# Beiträge zum Cluster-Titel zeigen
			PLog("next_url3: " + next_url)				# next_url1 s. get_ArtePage
			li = home(li, ID='arte')					# Home-Button
			li, cnt = GetContent(li, page, ID="ArteStart_2")
			PLog("cnt: " + str(cnt))
			if next_url:								# Mehr-Beiträge?
				ArteMehr(next_url, first=True)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ---------------------------------------------------------------------
# holt Cluster zu Cluster-titel title_org
def get_cluster(items, title_org):
	PLog("get_cluster: " + title_org)
	page=''
	for item in items:
		title = stringextract('title":"', '"', item)
		title = transl_json(title)
		PLog("title_org: %s, title: %s" % (title_org, title))
		if title_org in title:
			PLog("found_Cluster: " + title)
			page = item
			break
	if len(page) == 0:
		PLog("Cluster_failed: " + title_org)
	
	return page

# ---------------------------------------------------------------------
# holt Mehr-Beiträge 
# 1. Aufruf (Beitrag_Liste, ArteStart_2): nur Mehr Button
def ArteMehr(next_url, first=False):
	PLog("ArteMehr: " + next_url)
	PLog(first)
	jsonmark = '"props":'								# json-Bereich wie get_ArtePage
	li = xbmcgui.ListItem()

	if first:											# 1. Aufruf
		title = u"Weitere Beiträge"
		tag = u"weiter zu Seite %s (Gesamtzahl unbekannt)" % next_url[-1:]
		img = R(ICON_MEHR)

		query=py2_encode(next_url); 
		fparams="&fparams={'next_url': '%s'}" % quote(next_url)	
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteMehr", fanart=img, 
			thumb=img , fparams=fparams, tagline=tag)
		return
		
	#------------------------------------------------	# Folgeaufrufe
	
	li = home(li, ID='arte')							# Home-Button
	page, msg = get_page(next_url)
	if page == '':										# hier ohne Dialog
		PLog(msg)
		return

	pos = page.find(jsonmark)
	if pos > 0:		
		page = page[pos:]
		page = page.replace('\\u002F', '/')	
		page = page.replace('\\"', '*')	
	
	pos = page.find('"Alle Videos"')					# entf. bei neueste-videos
	if pos > 0:
		page = page[pos:]
	li, cnt = GetContent(li, page, ID="ArteMehr")
	
	try:
		nextpage = int(next_url[-1:]) + 1
		next_url = next_url[:-1] + str(nextpage)
		PLog("next_url_new: " + next_url)
	except:
		next_url=''
	
	if 	next_url:
		title = u"Weitere Beiträge"
		tag = u"weiter zu Seite %s (Gesamtzahl unbekannt)" % next_url[-1:]
		img = R(ICON_MEHR)

		query=py2_encode(next_url); 
		fparams="&fparams={'next_url': '%s'}" % quote(next_url)	
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteMehr", fanart=img, 
			thumb=img , fparams=fparams, tagline=tag)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ---------------------------------------------------------------------
# lädt Arte-Seite aus Cache / Web
# Rückgabe json-Teil der Webseite oder ''
# Cachezeit für Startseite + Kategorien identisch
# 26.07.2021 Anpassung an Webänderung (json-Auschnitt)
# 27.04.2022 Umstellung Dict_ID wg. rekursiver Aufrufe:
#	 Dict_ID = letzer Pfadanteil
#
def get_ArtePage(caller, title, path, header=''):
	PLog("get_ArtePage: " + path)
	PLog(caller); PLog(path)
	page=''
	
	if path == '':
		PLog("path_fehlt")
		return page

	Dict_ID = path.split("/")[-1]						# Dict_ID aus path erzeugen
	if path.endswith("arte.tv/de/"):
		Dict_ID = "startseite"
	if Dict_ID == '':
		Dict_ID = path.split("/")[-2]
	Dict_ID = Dict_ID.replace("?", "")					# Arte_?genres=oper, Arte_?page=1,..
	Dict_ID = "Arte_%s" % Dict_ID

										# Sicherung
	page = Dict("load", Dict_ID, CacheTime=ArteKatCacheTime)
	if page == False:
		page=''
	jsonmark = '"props":'								# json-Bereich	26.07.2021 angepasst

	if page == '':										# nicht vorhanden
		page, msg = get_page(path, header=header)	
		if page == '':						
			msg1 = 'Fehler in %s: %s' % (caller, title)
			msg2 = msg
			msg2 = u"Seite weder im Cache noch im Web verfügbar"
			MyDialog(msg1, msg2, '')
			return ''
		if 'id="no-content">' in page:					# no-content-Hinweis nur im html-Teil
			msg2 = stringextract('id="no-content">', '</', page)
			if msg2:
				msg1 = 'Arte meldet:'
				MyDialog(msg1, msg2, '')
				return ''
		else:
			# pos = page.find('__INITIAL_STATE__ ')		# json-Bereich vor 26.07.2021
			next_url = get_next_url(page, Dict_ID)		# ev. next_url wird unten angehängt
			if next_url:
				page = page + '{"next_url":"%s"}'  % next_url
			 	
			pos = page.find(jsonmark)					# json-Bereich abklemmen	
			if pos > 0:	
				page = page[pos:]
				page = page.replace('\\u002F', '/')	
				page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
				
				if path.endswith("neueste-videos/") == False:	# neueste-videos ohne Cache!
					Dict("store", Dict_ID, page) 				# Seite -> Cache, einschl. next_url
			else:
				PLog("json-Daten fehlen")
				page=''									# ohne json-Bereich: leere Seite

	#RSave('/tmp/x.json', py2_encode(page))	# Debug	
	PLog(len(page))
	# page = str(page)  # n. erf.
	PLog("page_start: " + page[:100])
	PLog("page_end: " + page[-100:])
	return page
	
# ---------------------------------------
# ermittelt next-Url
# unterschiedl. Tags: 'link rel="next"', '"_self">Next<'
# 	daher Ermittlung via '?page=2' - next_url wird verworfen,
#	falls Dict_ID (ohne arte_) nicht vorkommt  (z.B. next_url
#	für allgemeine neueste-videos
#	
def get_next_url(page, Dict_ID):
	PLog("get_next_url:")

	next_url=''; mark='?page='
	pos = page.find(mark)
	if pos > 0:
		PLog(page[pos-40:pos+40])
		pos2 = page[:pos].rfind("href=")
		next_url = stringextract('href="', '"', page[pos2:])
		d = Dict_ID.split("Arte_")[-1]
		if next_url.find(d) < 0:
			PLog("next_url_ohne: %s" % d)
			next_url=''
	PLog("next_url: " + next_url)
	return next_url
	
# ----------------------------------------------------------------------

