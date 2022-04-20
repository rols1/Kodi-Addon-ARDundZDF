# -*- coding: utf-8 -*-
################################################################################
#				arte.py - Teil von Kodi-Addon-ARDundZDF
#		Kategorien der ArteMediathek auf https://www.arte.tv/de/
#
#	Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	Auswertung via Strings statt json (Performance)
#
################################################################################
# 	<nr>6</nr>										# Numerierung für Einzelupdate
#	Stand: 20.04.2022

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
ICON_ARTE		= 'icon-arte_kat.png'			
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
			
	tag='[B][COLOR red]Arte Livestream[/COLOR][/B]'
	title, summ, descr, vonbis, img, href = get_live_data('ARTE')
	title = repl_json_chars(title)
	
	if img == '':
		img = R(ICON_TVLIVE)
	summ_par = summ.replace('\n', '||')	
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
		summ = unescape(summ)
		PLog("title: " + title); 
		summ = "[B]LAUFENDE SENDUNG [COLOR red](%s Uhr)[/COLOR][/B]\n\n%s" % (vonbis, summ)
		title= sname
		try:										# 'list' object in summ möglich - Urs. n.b.
			descr = summ.replace('\n', '||')		# \n aus summ -> ||
		except Exception as exception:	
			PLog(str(exception))
			descr = ''
		PLog(title); PLog(img); PLog(sname); PLog(stime); PLog(vonbis); 

	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('Arte ') in up_low(webtitle): 	# Arte mit Blank!
			href = href
			break
					
	if href == '':
		PLog('%s: Streamlink fehlt' % 'Arte ')
	if img == '':
		img = thumb									# Fallback Senderlogo (+ in Main_arte)				
	
	return title, summ, descr, vonbis, img, href

####################################################################################################
# arte - TV-Livestream mit akt. PRG
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
	
	li =  ardundzdf.Parseplaylist(li, href, img, geoblock='', descr=Plot)	
	
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
		items = blockextract('"programId"',  page)						# Fallback		 
	PLog("pre_items: %d, items: %d" % (len(pre_items), len(items)))
	if max_pre > 0:														# Blöcke zusammenlegen
		items = pre_items + items
	
	
	mediatype=''; cnt=0													# Default für mehrfach
	
	for item in items:
		mehrfach = False			
			
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
		else:
			tag = u"Dauer %s\n\n%s\n%s" % (dur, start_end, geo)
			
		title = transl_json(title); title = unescape(title);
		title = repl_json_chars(title); 					# franz. Akzent mögl.
		summ = repl_json_chars(summ)						# -"-
		tag_par = tag.replace('\n', '||')					# || Code für LF (\n scheitert in router)
		
		PLog('Satz1:')
		PLog(mehrfach); PLog(pid); PLog(title); PLog(url); PLog(tag[:80]); PLog(summ[:80]); 
		PLog(img); PLog(geo);
		title=py2_encode(title); url=py2_encode(url);
		pid=py2_encode(pid); tag_par=py2_encode(tag_par);
		img=py2_encode(img); summ=py2_encode(summ);
		
		if mystrip(title) == '':							# Müll
			continue
			
		if mehrfach:
			if ID == 'KAT_START':							# mit Url zurück zu -> Kategorien (id vor Block "title")
				cat = stringextract(u'label":"%s"' % py2_decode(title), '}]}', page) # Sub-Kategorien-Liste ausschneiden
				tag = stringextract('description":"', '"', cat)

				fparams="&fparams={'title':'%s', 'path':'%s'}" % (quote(title), quote(url))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Kategorien", fanart=img, 
					thumb=img, tagline=tag, fparams=fparams)
			else:
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(url), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", 
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)
			cnt=cnt+1					
		else:
			if mystrip(dur) == '':
				continue
			#if cnt > max_pre:								# ungenau
			#	tag = u"[COLOR blue]Auch interessant für Sie[/COLOR]\n\n%s" % tag
			
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
def Beitrag_Liste(url, title):
	PLog("Beitrag_Liste:")				

	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in Beitrag_Liste: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='arte')				# Home-Button

	mediatype=''; cnt=0													# Default für mehrfach
	
	cnt=0;
	if '__INITIAL_STATE__ ' in page:			# json-Format
		page = page.replace('\\u002F', '/')	
		page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
		li,cnt = GetContent(li, page, ID='Beitrag_Liste')		
	else:	
		pos1 = page.find('labelledby')
		pos2 = page.find('>Websites<')
		page = page[pos1:pos2]
		PLog(len(page))
		items = blockextract('labelledby', page)	
		PLog(len(items))
		img_api = "https://api-cdn.arte.tv/api/mami/v1/program/de/%s/1920x1080"
		
		for item in items:
			summ=''; geo='';											# nicht vorh.
			tag=''; tag_par=''									
			url = stringextract('href="', '"', item)
			pid = stringextract('/videos/', '/', url)
			img = stringextract('src="', '"', item)
			if img == '' or img.endswith("transparent.png"):
				img = img_api % pid										# Bild via api
				
			title = stringextract('_title">', '</h3>', item)
			title = unescape(title); title = repl_json_chars(title);
			title = unescape(title); title = repl_json_chars(title);
			subtitle = stringextract('_subtitle">', '</p>', item)
			subtitle = unescape(subtitle); subtitle = repl_json_chars(subtitle);
			dur = stringextract('css-18884f0">', '</p>', item)
			if dur == '':
				dur = stringextract('css-rmfqry">', '</p>', item)
			
			if dur:
				tag = "Dauer %s" % dur
				if subtitle:
					tag = "%s | %s" % (tag, subtitle)
				tag_par = tag; 
			
			
			PLog('Satz2:')
			PLog(pid); PLog(title); PLog(url); PLog(tag[:80]); PLog(summ[:80]); 
			PLog(img); PLog(geo);
			title=py2_encode(title); url=py2_encode(url);
			pid=py2_encode(pid); tag_par=py2_encode(tag_par);
			img=py2_encode(img); summ=py2_encode(summ);

			fparams="&fparams={'img':'%s','title':'%s','pid':'%s','tag':'%s','summ':'%s','dur':'%s','geo':'%s'}" %\
				(quote(img), quote(title), quote(pid), quote(tag_par), quote(summ), dur, geo)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.SingleVideo", 
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ,  mediatype=mediatype)		
			cnt=cnt+1
	
	if cnt == 0:					
		msg1 = u"%s:" % py2_decode(title)
		msg2 = u'Leider keine Videos gefunden.' 
		msg3 = u'Bitte bei Bedarf im Web nachschlagen' 
		MyDialog(msg1, msg2, msg3)
		PLog(msg1)
		return li
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

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
#
def SingleVideo(img, title, pid, tag, summ, dur, geo):
	PLog("SingleVideo: " + pid)
	title_org = title

	path = 'https://api.arte.tv/api/player/v2/config/de/%s' % pid
	page, msg = get_page(path, JsonPage=True)	
	if page == '':						
		msg1 = 'Fehler in SingleVideo: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
	page = page.replace('\\/', '/')
	page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
	
	li = xbmcgui.ListItem()
	li = home(li, ID='arte')				# Home-Button
	
	pos1 = page.find('"streams":')
	pos2 = page.find('"stat":')
	if pos1 >= 0 and pos2 > pos1:
		page = page[pos1:pos2]
	
	formitaeten = blockextract('"url":', page) 
	PLog(len(formitaeten))
	if summ == '':							# ev. nicht besetzt in Beitrag_Liste
		summ = stringextract('description":"',  '"', page)
		summ=transl_json(summ); summ=repl_json_chars(summ)
	PLog("summ: " + summ)
	
	form_arr = []; rec_list=[]	
	HLS_List=[]; MP4_List=[]; HBBTV_List=[];			# MP4_List = download_list
	skip_list=[]
	for rec in formitaeten:	
		r = []
		versions = stringextract('"versions":',  ']', rec)
		mainQuality = stringextract('"mainQuality":',  '}', rec)
		
		mediaType = stringextract('"protocol":"',  '"', rec)
		bitrate = stringextract('"bitrate":',  ',', rec)	# ? fehlt
		quality = stringextract('"code":"',  '"', mainQuality)
		width = stringextract('"label":"',  '"', mainQuality)
		height = stringextract('"height":"',  '"', rec)		# ? fehlt
		if height == "": height = "?"
		size = "%sx%s" % (width, height)
		size = size.replace("p", "")
		
		url = stringextract('"url":"',  '"', rec)
		lang = stringextract('"label":"',  '"', versions)	# z.B. Deutsch (Original)
		lang = transl_json(lang)
		shortLabel = stringextract('"shortLabel":"',  '"', versions) # Bsp..: "UT" oder "FR"
		
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
		if '.m3u8' in url:						# master.m3u8 
			HLS_List.append('HLS, [B]%s[/B] ** %s ** AUTO ** %s#%s' % (lang, size, title,url))
		else:									# MP4
			title_url = u"%s#%s" % (title, url)
			mp4 = "MP4 [B]%s[/B]" % lang
			item = u"%s | %s ** Bitrate %s ** Auflösung %s ** %s" %\
				(mp4, quality, bitrate, size, title_url)
			MP4_List.append(item)
		
			
	PLog("MP4_List: " + str(len(MP4_List)))
	ID = 'arte'
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	Dict("store", '%s_MP4_List' % ID, MP4_List) 
							
	if not len(HLS_List) and not len(MP4_List):			
		msg1 = u'SingleVideo: [B]%s[/B]' % title
		msg2 = u'Streams leider (noch) nicht verfügbar.'
		MyDialog(msg1, msg2, '')
		return li		
			

	tagline = "Titel: %s\n\n%s\n\n%s" % (title_org, tag, summ)	# s.a. ARD (Classic + Neu)
	tagline=repl_json_chars(tagline); tagline=tagline.replace( '||', '\n')
	Plot=tagline; 
	Plot=Plot.replace('\n', '||')
	sub_path=''
	HOME_ID = ID									# Default ZDF), 3sat
	PLog('Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
		
	ardundzdf.build_Streamlists_buttons(li,title_org,img,geo,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
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
#
def Kategorien(title='', path=''):
	PLog("Kategorien: " + title)

	li = xbmcgui.ListItem()
	li = home(li, ID='arte')				# Home-Button
	
	
	if title == '':											# 1. Stufe: Kategorien listen
		PLog('Stufe1:')	
		path = BASE_ARTE+'/de/'
		page = get_ArtePage('Kategorien_1', title, Dict_ID='ArteStart', path=path)	
		if page == '':	
			return li
		
		pos1 = page.find(':"Alle Kategorien')				# ausschneiden
		pos2 = page.find(':"Alle Sendungen', pos1+1)		# 10.05.2021 geändert. s.o.
		PLog("pos1: %d, pos2: %d" % (pos1, pos2))
		if pos2 == -1:										# Fallback  
			pos2 = len(page)
		page = page[pos1:pos2]
		PLog(page[:100])
		
		# Kategorien listen
		# GetContent: eigenes ListItem mit Titel (raw) -> KatSub 
		li,cnt = GetContent(li, page, ID='KAT_START') 		# eigenes ListItem
		
	else:													# 2. Stufe: Subkats von path
		PLog('Stufe2:')
		if 'Concert' in title:
			path = 'https://www.arte.tv/de/arte-concert/'
		page = get_ArtePage('Kategorien_1', title, Dict_ID='ArteStart_%s' % title[:10], path=path)	
		if page == '':	
			return li
			
		if "/dokumentationen-und-reportagen/" in path:		# nicht im Abschnitt categories + abweichend
			Kategorie_Dokus(li, title, page, path)
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

		PLog('Mark0')										# Liste SubKats einschl. Add's	
		Kat_pid =  stringextract('page":"', '"', page)		# z.B. HIS
		items = blockextract('code":{', page)	# Altern.:'{"id":"'
		PLog(len(items))
		get_subkats(li, items, path)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# Dokumentationen und Reportagen: nicht im Abschnitt categories + abweichend
# Aufrufer: Kategorien (Stufe 2),  Hauptmenü dort 
def Kategorie_Dokus(li, title, page, path):
	PLog("Kategorie_Dokus:")
	
	pos = page.find('"title":"Dokus und Reportagen"')
	pos2 = page.find('"title":"Alle Kategorien"')
	PLog("titel: %s, pos: %d, pos2: %d" % (title, pos, pos2))

	if pos == -1:						
		msg1 = 'Kategorie nicht gefunden: %s' % title
		MyDialog(msg1, '', '')
		return 

	page = page[pos:pos2]
	PLog(page[:100])
	
	items = blockextract('"code":{', page)			# entspr. bei Dokus den Subkats
	PLog(len(items))
	get_subkats(li, items, path)

	return

# ----------------------------------------------------------------------
# Liste der Subkategorien
# Aufrufer: Kategorien (Stufe 2) und Kategorie_Dokus (via Kategorien)
# 
def get_subkats(li, items, path):
	PLog("get_subkats:")

	for item in items:
		title = stringextract('title":"', '"', item)			
		label = title
		if title == '':								# vemutl. Restblock "Alle Kategorien"
			continue
		if "Category Banner" in title:
			label = title.replace("Category Banner", "arte Empfehlung")
		if 'data":[]' in item:						# skip, ohne Beiträge, Bsp. Playlists
			continue
		summ = stringextract('escription":"', '"', item)
		link_url = stringextract('url":"', '"', item)	# Webseite, abweichend von url in data
		data = stringextract('data":[', '],', item)
		
		# 1. Bild der Subkat laden 
		#	(Bild nur stellvertretend für gesamte Subkat)
		#	bei Cache-miss ICON_DIR_FOLDER . Subkats-Listen ohne img.
		#	Sonderfall arte-concert (mehrere Seiten möglich).
		img = R(ICON_DIR_FOLDER)						# Default 
		pos = item.find('title":"%s"' % title)
		PLog('pos: ' + str(pos))
		if pos > 0:
			img = get_img(item)
			
		pid = stringextract('id":"', '"', item)			# pid für SubKat
		label = transl_json(label)				
		title = transl_json(title); title = repl_json_chars(title)
		url = path
					
		PLog('Satz_Subs_Dokus:');  PLog(title);  PLog(pid); PLog(url); PLog(link_url); PLog(img);
		title=py2_encode(title); url=py2_encode(url); link_url=py2_encode(link_url);	
		fparams="&fparams={'path': '%s','title':'%s','pid':'%s','link_url':'%s'}" %\
			(quote(url), quote(title), pid, quote(link_url))
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.arte.KatSub", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)	
	return
# ----------------------------------------------------------------------
# listet einzelne Beiträge der Sub-Kategorie title in Datei path
# Hinw.: jede Datei der SubKats enthält die Subkats aller Kategorien
# Sonderfall: Arte Concert - die Url's (nextPage) der folgenden Seiten 
#		ergeben 401-errors. Daher leiten wir SubKats mit /arte-concert/
#		hier aus + verwenden einen Api-Call ähnlich in arte_Search
#		(ermit. in chrome-tools) -> KatSubConcert
# add: Trigger für Zusätze (Aktuelle Highlights, Kollektionen, Sendungen)
#
def KatSub(path, title, pid, link_url=''):
	PLog("KatSub: " + title)
	PLog(pid); PLog(path); PLog(link_url);

	li = xbmcgui.ListItem()
	li = home(li, ID='arte')						# Home-Button
	
	pagenr = stringextract('&page=', '&', path)	
	page = get_ArtePage('KatSub', title, Dict_ID='ArteSubKat_%s' % pid, path=path)	
	# RSave('/tmp/x.json', py2_encode(page))	# Debug	
	if page == '':	
		return li
		
	PLog('Mark2')								
	# alle Beiträge auf der 1. SubKat-Seite - zum Blättern wie im Web 
	# schneiden wir aus. Die Folgeseiten (json) enthalten nur die Beiträge
	# der angeforderten Seite. 
	PLog("title: %s" % title)
	pos1 = page.find('"title":"%s"' % title) 		# Anfang 
	pos2 = page.find('{"id":"', pos1+1)	# Ende
	PLog("pos1 %s, pos2 %s, len %s" % (pos1, pos2, len(page)))
	page = page[pos1:pos2]							# Ausschnitt
	PLog(page[:80])
	PLog(page[len(page)-80:])	

	li,cnt = GetContent(li, page, ID='KAT_SUB') 	# eigenes ListItem
	PLog("cnt: %d" % cnt)
	if cnt == 0:									# von Webseite ergänzen
	#if cnt < 2:									# von Webseite ergänzen (skip ev. Teaser)
		page = get_ArtePage('KatSub', title, Dict_ID='ArteWeb_%s' % pid, path=link_url)	
		if page:
			pos = page.find('"Die meistgesehenen Videos')	# ausschließen (auf jeder Seite wieder)
			page = page[:pos]
			li,cnt = GetContent(li, page, ID='KAT_SUB')
	

	nexturl = stringextract('nextPage":', ',', page)		# letzte Seite: "", auch "null," möglich
	if nexturl == 'null':
		nexturl = ''	
	try:
		nextpage = re.search('&page=(.d?)', nexturl).group(1)
	except:
		nextpage=""
	PLog("nextpage: " + nextpage)	

	PLog('Mark3')								
	if nexturl:										# Mehr-Button
		li = xbmcgui.ListItem()						# Kontext-Doppel verhindern
		# der api-internal Link in nextPage erzeugt http-403-Error - 
		# 	nach ersetzen durch www.arte.tv/guide OK: 
		nexturl = nexturl.replace('"', '')										# s.o. null
		nexturl = nexturl.replace('api-cdn.arte.tv', 'www.arte.tv/guide')		# Adds-Url
		nexturl = nexturl.replace('api-internal.arte.tv', 'www.arte.tv/guide')	# SubKats-Url
		nexturl = nexturl.replace('&limit=6', '&limit=100')
			
		nexturl = unquote(nexturl)						# DE_FR%252CEUR_DE_FR%252CSAT%252CALL
		PLog("nexturl: " + nexturl);
		PLog('Satz_KatSubs:'); PLog(nextpage); PLog(nexturl);
		tag = "weiter zu Seite %s" % nextpage
		
		title=py2_encode(title); nexturl=py2_encode(nexturl)
		fparams="&fparams={'title': '%s', 'path': '%s', 'pid': '%s', 'link_url': '%s'}" %\
			(quote(title), quote(nexturl), pid, quote(link_url))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.KatSub", 
			fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), tagline=tag, fparams=fparams)		
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------------------------------------
# lädt Arte-Seite aus Cache / Web
# Rückgabe json-Teil der Webseite oder ''
# Cachezeit für Startseite + Kategorien identisch
# 26.07.2021 Anpassung an Webänderung (json-Auschnitt)
#
def get_ArtePage(caller, title, Dict_ID, path, header=''):
	PLog("get_ArtePage: " + Dict_ID)
	PLog(caller); PLog(path)
	
	page = Dict("load", Dict_ID, CacheTime=ArteKatCacheTime)
	# page=False	# Debug
		
	if page == False:								# nicht vorhanden oder zu alt
		page, msg = get_page(path, header=header)	
		if page == '':						
			msg1 = 'Fehler in %s: %s' % (caller, title)
			msg2 = msg
			msg2 = u"Seite weder im Cache noch im Web verfügbar"
			MyDialog(msg1, msg2, '')
			return ''
		if 'id="no-content">' in page:				# no-content-Hinweis nur im html-Teil
			msg2 = stringextract('id="no-content">', '</', page)
			if msg2:
				msg1 = 'Arte meldet:'
				MyDialog(msg1, msg2, '')
				return ''
		else:
			# pos = page.find('__INITIAL_STATE__ ')	# json-Bereich
			pos = page.find('{"props":')	# json-Bereich			# 26.07.2021 angepasst
			if pos > 0:
				page = page[pos:]
			page = page.replace('\\u002F', '/')	
			page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
			Dict("store", Dict_ID, page) # Seite -> Cache: aktualisieren				

	# RSave('/tmp/x.json', py2_encode(page))	# Debug	
	PLog(len(page))
	# page = str(page)  # n. erf.
	PLog(page[:100])
	return page
# ----------------------------------------------------------------------

