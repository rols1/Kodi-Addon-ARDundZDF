# -*- coding: utf-8 -*-
################################################################################
#				arte.py - Teil von Kodi-Addon-ARDundZDF
#		Inhalte der ArteMediathek auf https://www.arte.tv/de/
#
#	Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	Auswertung via Strings statt json (Performance)
#
################################################################################
# 	<nr>63</nr>								# Numerierung für Einzelupdate
#	Stand: 28.03.2025

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
import resources.lib.EPG as EPG
from resources.lib.util import *

# Globals
ArteKatCacheTime	= 3600									# 1 Std.: 60*60

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')				# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]								# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):			# ADDON_DATA-Verzeichnis anpasen
	PLog('arte_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 			# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_ARTE		= 'https://www.arte.tv'						# + /de/ nach Bedarf
HBBTV_BASE		= "https://arte.tv/hbbtv-mw"

PLAYLIST 		= 'livesenderTV.xml'	  					# enth. Link für arte-Live											

# Icons
ICON 			= 'icon.png'								# ARD + ZDF
ICON_ARTE		= 'arte_Mediathek.png'						# Bitstream Charter Bold, 60p			
ICON_ARTE_NEW	= 'icon-arte-new.png'						# Bitstream Charter Bold, 60p			
ICON_ARTE_START	= 'icon-arte-start.png'						# Bitstream Charter Bold, 60p				
ICON_DIR_FOLDER	= 'Dir-folder.png'
ICON_MEHR 		= 'icon-mehr.png'
ICON_SEARCH 	= 'arte-suche.png'				
ICON_TVLIVE		= 'tv-arte.png'						
ICON_TV			= 'tv-arteTV.png'						
ICON_DIR_FOLDER	= "Dir-folder.png"

LANG  = [u"Français | fr",  u"Deutsch | de", u"English | en",
		u"Español | es", u"Polski | pl", u"Italiano | it",
	]
fname = os.path.join("%s/Dict/arte_lang") % ADDON_DATA
if os.path.exists(fname) == False:							# Sprache vorbelegen / laden
	arte_lang = LANG[1]
	Dict('store', "arte_lang", arte_lang)
else:
	arte_lang = Dict('load', "arte_lang")

# ----------------------------------------------------------------------			
def Main_arte(title='', summ='', descr='',href=''):
	PLog('Main_arte:')
	arte_lang = Dict('load', "arte_lang")
	
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, NAME)							# Startblank s. home
	li = home(li, ID=NAME, ltitle=ltitle)					# Home-Button
	

	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		l = L(u"Suche in")
		title = u'%s MediathekViewWeb.de' % l
		tag = "Extrem schnelle Suche im [B]ARTE.DE[/B]-Datenbestand von MediathekView."
		title=py2_encode(title);
		func = "resources.lib.arte.Main_arte"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARTE.DE", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_ARTE), 
			thumb=R("suche_mv.png"), tagline=tag, fparams=fparams)

	title=u"%s Arte-Mediathek" % L(u"Suche in")
	tag = u"[B]%s[/B]" % arte_lang
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Arte_Search", fanart=R(ICON_ARTE), 
		thumb=R(ICON_SEARCH), tagline=tag, fparams=fparams)
	# ------------------------------------------------------

	title = u"%s" % L("Arte TV-Programm heute")
	tag = "[B]%s[/B]" % arte_lang
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.EPG_Today", fanart=R(ICON_ARTE), 
		thumb=R(ICON_TV), tagline=tag, fparams=fparams)

	tag=u'[B]%s[/B]' % L("Arte Livestream")					# Livestream-Daten
	try:
		title, tag, summ, img, href = get_live_data('ARTE')
		title = repl_json_chars(title)
	except Exception as exception:
		PLog("json_error5: " + str(exception))
		title="LIVE"; tag="LIVE"; summ=""; img=R(ICON_TV)	# Defaults	
	
	summ_par = summ.replace('\n', '||')
	summ_par = repl_json_chars(summ_par)
	title=py2_encode(title); href=py2_encode(href); summ_par=py2_encode(summ_par);
	img=py2_encode(img)
	fparams="&fparams={'href': '%s', 'title': '%s', 'Plot': '%s', 'img': '%s'}" %\
		(quote(href), quote(title), quote(summ_par), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Arte_Live", fanart=R(ICON_ARTE),
		thumb=img, fparams=fparams, tagline=tag, summary=summ)

	# ------------------------------------------------------
	title = u"%s" % L(u"Kategorien")
	tag = u"%s wwww.arte.tv" % L(u"einschließlich Startseite")
	summ = u"[B]%s[/B]" % arte_lang
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Kategorien", fanart=R(ICON_ARTE), 
		thumb=R(ICON_ARTE), tagline=tag, summary=summ, fparams=fparams)
		
	# ------------------------------------------------------
	# 27.03.2025 Bisher keine PRG für Gebärdensprache gefunden (Icon arte_Gebaerden.png)
	title = u"%s" % L(u"Barrierefreie Inhalte")
	tag = "[B]%s[/B]" % arte_lang							# aktuell
	lang = arte_lang.split("|")[1].strip()					# fr, de, ..
	path = "https://www.arte.tv/hbbtv-mw/api/1/skeletons/pages/ACCESSIBLE_PROGRAMS?lang=%s" % lang
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))							
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteStart", 	# -> Step2
		thumb=R("arte_barrierefrei.png"), fanart=R(ICON_ARTE), tagline=tag, fparams=fparams)
	
	# ------------------------------------------------------
	title 	= u'Sprache / Language'							# Auswahl Sprache
	tag = "[B]%s[/B]" % arte_lang							# aktuell
	title=py2_encode(title); 
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.set_lang", fanart=R(ICON_ARTE), 
		thumb=R('arte_lang.png'), tagline=tag, fparams=fparams) 
		
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)	
	
####################################################################################################
# Auswahl Sprache
# Aufruf main_arte ohne new_set
# 
def set_lang(title, new_set=""):	
	PLog('set_lang: ' + new_set)
	
	if new_set:												# 2. Aufruf -> Auswahl speichern
		Dict('store', "arte_lang", new_set)
		arte_lang = new_set
		icon = R('arte_lang.png')
		msg1 = u"[B]%s[/B]" % arte_lang
		xbmcgui.Dialog().notification(msg1,"",icon,2000,sound=False)
		
		return
		
	#----------------------									# 1. Aufruf -> Auswahl
	arte_lang = Dict('load', "arte_lang")
	if arte_lang == False or arte_lang == "":
		arte_lang = LANG[1]
		
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")						# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)					# Home-Button
	
	tag = u"[B]%s[/B]" % arte_lang							# aktuell
	for item in LANG:
		title = u"%s --> [B]%s[/B]" % (arte_lang, item)
		PLog('Satz6: ' + title)
		title=py2_encode(title); item=py2_encode(item);
		fparams="&fparams={'title': '%s', 'new_set': '%s'}" % (quote(title), quote(item))							
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.set_lang", 
			fanart=R(ICON_ARTE), thumb=R('arte_lang.png'), tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Nutzung EPG-Modul, Daten von tvtoday		
# 14.03.2023 Umstellung auf Daten von https://www.arte.tv/%s/live
# 14.03.2025 Umstellung auf Daten aus EPG_Today (json-Daten in
#	vorheriger Variante können fehlen), in arte für de und fr
#
def get_live_data(name):
	PLog('get_live_data:')

	#------------------											# Livestream aus Cache holen
	ard_streamlinks = get_ARDstreamlinks(skip_log=True)
	# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
	for line in ard_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('Arte') in up_low(webtitle): 
			href = href
			break		
	thumb = R('arte_live.png')									# Cache-thumb ist landscape
	if href == '':
		PLog('%s: Streamlink fehlt' % 'Arte ')
	#------------------

	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()						# fr, de, ..

	err_par = [u"[B]LIVE[/B]", "", "", thumb, href]				# Stream ohne Daten
	page = EPG_Today(mode="onlyPage")							# nur Seite für Heute holen, kein Check ob Sprache verfügbar
	player = "https://api.arte.tv/api/player/v2/config/%s/LIVE" % lang	# aus ../pages/TV_GUIDE/?day=..
	if page:
		li=""
		try:
			title, tag, summ, thumb, url = GetContent(li, page, ID="EPG_Today", OnlyNow=True)
		except Exception as exception:
			PLog("json_error6: " + str(exception))
			PLog("use_ard_streamlinks")
			title=""; tag=""; summ=""; thumb=""; url=href	
		
		if title == "":											# EPG-Abruf fehlgeschlagen
			title = "unbekannt"
		title = u"[B]LIVE[/B] | %s" % title
		tag = u"%s\n%s" % (title, tag)
		if thumb == "":
			thumb = R('arte_live.png')

		page = get_page(path=player)							# Playerdaten mit Stream-Url
		page = py2_encode(page)
		try:
			streams = stringextract('"streams":', '"stat"', str(page))
			PLog("streams: " + streams[:80])
			streams = streams.replace('\\\\/','/')				# https:\\/\\/artesimulcast.akamaized.net/..
			PLog("streams: " + streams[:80])
			urls = blockextract('url":', streams)				# Live-Streams nur für fr, de vorhanden
			PLog(len(urls))
			if "fr" in lang:
				stream_url = stringextract('url":"', '"', urls[0])
			else:												# [1] Direct Allemand"
				stream_url = stringextract('url":"', '"', urls[1])
			
			href = stream_url			
		except Exception as exception:
			PLog("player_error: " + str(exception))							
			PLog("stream_url=href")								# Fallback: href aus ard_streamlinks
		
		PLog("lang: %s, href: %s" % (lang, href))
		title=py2_decode(title); summ=py2_decode(summ);			# PY2
		return title, tag, summ, thumb, href		
	else:
		PLog("empty_epg")
		return err_par

# ----------------------------------------------------------------------
# TV-Programm Heute von arte.tv/de/guide/
# 14.03.2025 mode="onlyPage" -> nur Seite für get_live_data	
#
def EPG_Today(mode=""):
	PLog('EPG_Today:')
	PLog("mode: " + mode)

	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()			# fr, de, ..	

	now = datetime.datetime.now()
	today = now.strftime("%Y-%m-%d")				# 2023-01-16 
	EPG_path = "https://www.arte.tv/api/rproxy/emac/v4/%s/web/pages/TV_GUIDE/?day=%s"
	path = EPG_path % (lang, today)
	PLog(path)
	if url_check(path, dialog=False) == False:		# nicht für alle Sprachen verfügbar
		icon = R('arte_lang.png')
		msg1 = u"EPG fehlt: " + arte_lang
		msg2 = u"lade: " + u"Deutsch | de"			# Fallback Deutsch
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		PLog(msg1); PLog(msg2)
		path = EPG_path % ("de", today)
	
	page = get_ArtePage('EPG_Today', "EPG_Today", path)	
	if page == '':
		msg1 = L(u"Programmabruf fehlgeschlagen") 
		MyDialog(msg1, "", '')
		return
		
	if mode == "onlyPage":							# nur Inhalt, keine Liste
		PLog("return_page")
		return page
		
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")				# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)			# Home-Button	
	
	li, cnt = GetContent(li, page, ID="EPG_Today")
	PLog("cnt: " + str(cnt))
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


####################################################################################################
# arte - TV-Livestream mit akt. PRG
#
def Arte_Live(href, title, Plot, img):	
	PLog('Arte_Live:')

	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")					# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)				# Home-Button

	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true'	# Sofortstart
		PLog('Sofortstart: Arte_Live')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot, live="true")
		return	
							
	Plot_par = Plot.replace('\n', '||')
	
	title=py2_encode(title); href=py2_encode(href); img=py2_encode(img);
	Plot_par=py2_encode(Plot_par);
	label = u"%s (HLS)" % L(u"Bandbreite und Auflösung automatisch")
	tag = Plot.replace('||', '\n')
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'live': 'true'}" %\
		(quote_plus(href), quote_plus(title), quote_plus(img), quote_plus(Plot_par))
	addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
		fparams=fparams, mediatype='video', tagline=tag) 		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# 15.01.2023 umgestellt: api-path (path für Seite 1 war abweichend)
# 12.09.2023 neue Api-Version (emac/v3 -> emac/v4)
#
def Arte_Search(query='', next_url=''):
	PLog("Arte_Search:")
	PLog(query); PLog(next_url);
	if 	query == '':	
		query = ardundzdf.get_query(channel='phoenix')	# unbehandelt
	query = py2_decode(query)
	if  query == None or query == '':
		return ""
				
	query=py2_encode(query);
						
	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()				# fr, de, ..	
	path = next_url										# Pagination-Link (api-internal ersetzt)
	if path == "":										# Seite 1 
		path = "https://www.arte.tv/api/rproxy/emac/v4/%s/web/pages/SEARCH?query=%s&mainZonePage=1&page=1&limit=20" %\
		(quote(lang), quote(query))		
	aktpage = stringextract('page=', '&', path)

	page, msg = get_page(path=path, do_safe=False)		# ohne quote in get_page (api-Call)
	if page == '':						
		msg1 = L(u'Fehler in Suche') + ": %s" % query
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(len(page))
				
		
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")					# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)				# Home-Button

	PLog(len(page))
	page = page.replace('\\"', '*')						# Bsp. "\"Brisant\""

	page = json.loads(page)
	ID='SEARCH'
	if next_url:										# Folgeseiten: Struktur wie MOST_RECENT
		ID='SEARCH_NEXT'
	li,cnt = GetContent(li, page, ID)
	if 	cnt == 0:
		icon = R(ICON_SEARCH)
		msg1 = L(u"leider keine Treffer zu")
		msg2 = query
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=False)
		return
		
	#													# Mehr-Beiträge? ArteMehr nicht geeignet
	next_url,page_akt,page_anz,anz,next_page = get_next_url(str(page))
	if next_url:
		next_url = next_url.replace("api-internal.arte.tv/api", "www.arte.tv/api/rproxy")
		li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
		img = R(ICON_MEHR)
		title = L(u"Weitere Beiträge")
		l = L(u"weiter zu Seite")
		tag = u"weiter zu [B]Seite %s[/B] (Seiten: %s, Beiträge: %s)" % (next_page, page_anz, anz)

		query=py2_encode(query); next_url=py2_encode(next_url)
		fparams="&fparams={'query': '%s', 'next_url': '%s'}" % (quote(query), quote(next_url))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Arte_Search", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Einzel- und Folgebeiträge auch bei Suche möglich. Viele Einzelbeiträge
#	liegen in der Zukunft, bieten aber kleinen Teaser 
# Seiten mit collection_subcollection: Auswertung ab dort (Serien)
# 15.01.2023 umgestellt: page=json
# 14.03.2025 OnlyNow triggert EPG-Rückgabe -> get_live_data
# 23.03.2025 ergänzt für hbbtv
#
def GetContent(li, page, ID, ignore_pid="", OnlyNow="", lang=""):
	PLog("GetContent: " + ID)
	PLog(ignore_pid); PLog(OnlyNow)
	
	PLog(str(page)[:80])
	img_def = R(ICON_DIR_FOLDER)
	skip_list=[]
		
	if ID == "SEARCH":									# web-api-Call
		values = page["value"]["zones"][0]["content"]["data"]
	elif ID == "SEARCH_NEXT":							# Folgeseiten wie MOST_RECENT
		values = page["value"]["data"]
	elif ID == "EPG_Today":								# web-api-Call
		values = page["value"]["zones"][1]["content"]["data"]	# 0=TVGuide Highlights, 1=Listing
	elif ID == "Beitrag_Liste":	
		if 	"pageProps" in page:						# 24.03.2024: vermutl. entfallen nach arte-Änderung
			values = page["pageProps"]["initialPage"]["value"]["zones"][0]["content"]["data"]
		else:
			values = page["value"]["data"]
		PLog(len(values))
		PLog(str(values)[:100])
	elif ID == "MOST_RECENT":			
		values = page["value"]["data"]
		PLog(len(values))
		PLog(str(values)[:100])
	elif ID == "HBBTV":									# Neu HBBTV
		if "cards" in page:
			values = page["cards"]
		elif "collections" in page:						# hbbtv
			values = page["collections"]
		else:
			values=[]
		if "images" in page:							# Default-Image statt ICON_DIR_FOLDER
			img_def=""
			if "highlight" in page["images"]:
				img_def = page["images"]["highlight"]
			else:
				img_def = page["images"]["landscape"]
		
	else:
		values = page["pageProps"]["initialPage"]		# web-embedded, ganze Seite
		try:											# s.a. ArteCluster
			if "value" in page:							# nach 13.01.2021
				values = values["value"]["zones"]
			else:										# vor 13.01.2021
				values = values["zones"]
		except Exception as exception:
			PLog("json_error8: " + str(exception))
			values=[]
	
	PLog("img_def: " + img_def)	
	PLog(len(values))
	if len(values) == 0:
		PLog("no_values")
		return li, 0
	
	PLog(str(values)[:100])
	mediatype=''; cnt=0
	
	for item in values:
		PLog(str(item)[:60])
		mehrfach=False; summ=''; dur=""; geo=""	
		start=''; end=''; upcoming=""; teaserText=""; coll=""
		
		title = item["title"]							# für Abgleich in Kategorien	
		if "subtitle" in item:
			subtitle = item["subtitle"]	
			if subtitle:								# arte verbindet mit -
				title  = "%s - %s" % (title, subtitle)
		title = valid_title_chars(title)				# Steuerz. möglich: \t\n
		
		if "Description" in item:
			summ = item["Description"]					
		if "description" in item:						# hbbtv
			summ = item["description"]					
		if "shortDescription" in item:					# Vorrang, altern.: teaserText
			summ = item["shortDescription"]
		if summ == None:
			summ = ""					
		pid = item["id"]
		if ID == "HBBTV":								# hbbtv
			program_id=""
			if "program_id" in item:					# null möglich
				pid = item["program_id"]
			else:
				if "program_id" in page:				# übergeordnet, ungeprüft!
					pid = page["program_id"]			

		PLog("Mark1")
		PLog(pid); PLog(ignore_pid); 
		
		kind = ""; typ=""
		if "kind" in item:
			kind = item["kind"]["code"]					# z.B. TOPIC
			if "type" in item["kind"]:					# fehlt in EPG
				typ = item["kind"]["type"]				# z.B. Kollektion
			coll = item["kind"]["isCollection"]			# true/false
		else:											# hbbtv
			typ = item["type"]
			if "isCollection" in item:
				coll = item["isCollection"]			
		if coll:										# nicht verlässlich, s. dur					
			mehrfach = True	
		
		if "url" in item:
			url = item["url"]
		if "link" in item:
			url = "%s%s?lang=%s" % (HBBTV_BASE, item["link"], lang)	# hbbtv	
			if not item["link"]:						# null für Kats wie DOR
				if item["deeplink"]:
					kat = item["deeplink"]
					kat = kat.split("/")[-1]
					url = "%s/api/1/skeletons/pages/%s?lang=%s" % (HBBTV_BASE, kat, lang)	
		
		img = get_img(item, ID)
		if "ACCESSIBLE_PROGRAMS/2" in url:
			img = R("arte_barrierefrei.png")
		if "ACCESSIBLE_PROGRAMS/3" in url:
			img = R("arte_Untertitel.png")
		if img == "" and ID == "HBBTV":
			img = get_img_pre(url, title)				# Bild 1. Beitrag Zielseite
		if img == "":
			img = img_def								# übergeordnetes Bild oder Folder
		PLog("img: %s, img_def: %s" % (img, img_def))
	
			
		if "teaserText" in item:										
			teaserText = item["teaserText"]
		if "duration" in item:										
			dur = item["duration"]
		if dur == None:
			dur = ""					
		PLog('dur: ' + str(dur))
		if "int" in str(type(dur)):						# hbbtv: "3 Min.", sonst: 180
			dur = seconds_translate(dur)
		if dur == "":
			mehrfach = True
		else:
			mehrfach = False
		
		try:
			geo = item["geoblocking"]					# hbbtv
			if "code" in geo:
				geo = geo["code"]						# Bsp. "DE_FR", "ALL"
		except:
			geo=""
		if geo:
			geo = "Geoblock-Info: %s" % str(geo)	
		else:
			"Geoblock-Info: ALL"
		
		try:
			start = item["availability"]["start"]
			end = item["availability"]["end"]
		except:
			start=""; end=""; start_end=""
		PLog(str(start)); PLog(str(end))
		if start and end:
			start = time_translate(start)
			end = time_translate(end)
			rlang = L(u"Verfügbar")
			start_end = u'[B]%s: [COLOR green]%s[/COLOR] - [COLOR darkgoldenrod]%s[/COLOR][/B]' % (rlang, start, end)	

			if "upcomingDate" in item:
				upcoming = item["upcomingDate"]	
				if upcoming:
					upcoming = getOnline(upcoming, onlycheck=True)	# check Zukunft
				if 'Zukunft' in upcoming:
					start_end = "%s:%s" % (start_end, upcoming)	
		
		
		if mehrfach:										# s. coll
			tag = u"[B]%s[/B]" % L(u"Folgebeiträge")
		else:
			l = L("Dauer")
			if start_end:
				tag = u"%s %s\n\n%s\n%s" % (l, dur, start_end, geo)
			else:
				if dur:
					tag = u"%s %s\n%s" % (l, dur, geo)
				else:
					tag = u"%s" % (geo)
					
		title = transl_json(title); title = unescape(title);
		title = repl_json_chars(title); 					# franz. Akzent mögl.
		summ = repl_json_chars(summ)						# -"-
		summ  = valid_title_chars(summ)						# s. changelog V4.7.4
		
		tag_par = tag.replace('\n', '||')					# || Code für LF (\n scheitert in router)
		summ_par = summ.replace('\n', '||')					# || Code für LF (\n scheitert in router)
		
		
		PLog('Satz1:')
		PLog(mehrfach); PLog(typ); PLog(pid); PLog(title); 
		PLog(url); PLog(img); PLog(tag[:80]); PLog(summ[:80]); 
		PLog(geo);
		pid_org=pid
		title=py2_encode(title); url=py2_encode(url);
		pid=py2_encode(pid); tag_par=py2_encode(tag_par);
		img=py2_encode(img); summ=py2_encode(summ);
		summ_par=py2_encode(summ_par);
		
		if mehrfach:
			if not OnlyNow:
				if "hbbtv-mw" in url:						# hbbtv
					fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(url), quote(title))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteStart", 
					fanart=R(ICON_ARTE), thumb=img, tagline=tag, summary=summ, fparams=fparams)
				else:
					fparams="&fparams={'katurl': '%s'}" % quote(url)
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteCluster",
						fanart=R(ICON_ARTE), thumb=img, tagline=tag, summary=summ, fparams=fparams)											
				cnt=cnt+1					
		else:
			if dur == '' and pid == '':
				PLog("dur_and_pid_empty")
				continue
			if "hbbtv-mw" in url == False:					# hbbtv:Player-Url, nicht genutzt, pid->SingleVideo (Streamlisten)
				if url.count("/") > 2:						# Bsp. /de/ (kein video)
					pid = url.split("/")[3]					# /de/videos/100814-000-A/.., id nicht verwendbar
				if url.endswith("/live/"):					# läuft gerade
					pid=pid_org			
			PLog("pid: " + pid)
				
			if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
				mediatype='video'
				
			label = title
			if ID == "EPG_Today":							# EPG: Uhrzeit -> Label
				lvon = L("von"); lbis = L("bis")
				ldauer = L("Dauer")
				start = start[-5:]; end = end[-5:];
				title = py2_decode(title)
				label = u"[COLOR blue]%s[/COLOR] | %s" % (start, title)	# Sendezeit | Titel
				tag = u"[B]%s %s %s %s Uhr | %s: %s [/B]" % (lvon, start, lbis, end, ldauer, dur)
				if "stickers" in item:
					PLog("found_stickers")
					live=True
					try:			 
						if item["stickers"]:				# [] möglich
							if item["stickers"][0]["code"] == "LIVE":
								label = "[B]%s[/B]" % label
								if OnlyNow:					# nur Live-EGP, keine Liste
									PLog("return_liveEPG")
									return label, tag, summ, img, url
					except Exception as exception:
						# PLog(item)
						PLog("stickers_error: " + str(exception))# ohne Rückgabe try in get_live_data)
																

			if not OnlyNow:							
				pid=py2_encode(pid); 
				title=py2_encode(title);	
				fparams="&fparams={'img':'%s','title':'%s','pid':'%s','tag':'%s','summ':'%s','dur':'%s','geo':'%s'}" %\
					(quote(img), quote(title), quote(pid), quote(tag_par), quote(summ_par), dur, geo)
				addDir(li=li, label=label, action="dirList", dirID="resources.lib.arte.SingleVideo", 
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ,  mediatype=mediatype)		
				cnt=cnt+1

	PLog("count: %d" % cnt)
	return li, cnt
	
# -------------------------------
#  wie ARDnew.img_preload, angepasste json- und img-path-
#	Behandlung. Eindeutiger Dateiname wird aus Kombi collection-
#	Name, collection-Nr. und lang erzeugt, z.B. home_24de (Beiträge
#	+ Bilder unterscheiden sich für die de,fr,en,es,pl,it).
#	
def get_img_pre(path, title):
	PLog("get_img_pre:")
	PLog("title: %s, path: %s" % (title, path))
	leer_img=""	
	
	oname = os.path.join(SLIDESTORE, "ARTE_Startpage")
	p = path.replace("?lang=", "")						# entferne lang=, behalte Kennung
	p = p.split("/")									# details/home/24?lang=de ->
	PLog(p)
	fname = "_".join(p[-2:])							# home_24de
	fname = os.path.join(oname, fname)
	PLog("oname: %s, fname: %s" % (oname, fname))
	
	if os.path.isdir(oname) == False:
		try:  
			PLog("mkdir: " + oname)
			os.mkdir(oname)								# UZ-Verz. ARTE_Startpage erzeugen
		except OSError as exception:
			PLog("mkdir_error " + str(exception))
			return leer_img	
			
	if os.path.exists(fname):							# img aus Cache laden
		PLog('img_cache_load: ' + fname)	
		return fname
	#-------------------------------------------------- # Beitrag path von Sender laden	
		
	try:
		page, msg = get_page(path)
		PLog(str(page)[:80])
		page = json.loads(page)
		if "cards" in page:
			item = page["cards"][0]
		elif "collections" in page:						# hbbtv
			item = page["collections"][0]
		else:
			item=[]
	except Exception as exception:
		PLog("json_error7: " + str(exception))
		return 	leer_img
	PLog(str(item)[:80])
	
	img = get_img(item, ID="HBBTV")
	if img == "":
		return 	leer_img

	PLog('img_cache_leer')
	PLog("urlretrieve %s to %s" % (img, fname))	
	msg1 = L("Lade Bild")
	msg2 = title
	xbmcgui.Dialog().notification(msg1,msg2,R(ICON_ARTE),2000, sound=False)	 
	urlretrieve(img, fname)								# img -> Cache
	icon = R(ICON_ARTE)
	return fname
	
# -------------------------------
# holt Bild aus Datensatz
# 15.01.2023 angepasst für json-Inhalte
# 25.03.2025  für hbbtv erweitert mit Cache
#
def get_img(item, ID=""):
	PLog("get_img: " + ID)
	PLog(str(type(item)))
	PLog(str(item)[:80])	
	img=""
	
	if ID == "HBBTV":
		if "images" in item:
			if "highlight" in item["images"]:
				img = item["images"]["highlight"]
			else:
				img = item["images"]["landscape"]
		else:		 
			img=""
		PLog("img: " + img)
		return img
		
	# -------------------------------------------------	# Bilder api/rproxy/emac/v4
	if type(item) == dict:
		if "mainImage" in item:
			img = item["mainImage"]["url"]
			img = img.replace('__SIZE__', '400x225')
		if "images" in item:
			imgs = item["images"]["landscape"]["resolutions"]
			PLog(str(imgs)[:40])
			imgs = str(imgs)
			imgs = blockextract("'url'", imgs)
			for img in imgs:
				if "400x225" in img:					# 200,400,720,940,1920 
					img = stringextract("url': '", "'", img)
					break	
		return img
	
	if "resolutions" in item:
		images = stringextract('resolutions":[', '}],', item)
		# PLog(images)
		images = blockextract('url":', images)
		PLog(len(images))
		
		img=''
		for image in images:
			if 'w":300' in image or 'w":720' in image or 'w":940' in image or 'w":1920' in image:
				img = stringextract('url":"', '",', image)			
				break
	else: 
		image = stringextract('mainImage":', '}', item)
		#PLog(image)
		img = stringextract('url":"', '"', image)
		img = img.replace('__SIZE__', '400x225')		# nur 400x225 akzeptiert
		
			
	if img == '':
		img = R(ICON_DIR_FOLDER)
	
	return img
	
# -------------------------------
# 15.01.2023
# def get_trailer() entfernt
	
# ----------------------------------------------------------------------
# 15.01.2023 spez. ID für GetContent
# 25.03.2025 nach Umstellung auf hbbtv nur noch genutzt für Neueste Videos
#	(api rproxy/emac/v4). Mit Pagination ArteMehr
#
def Beitrag_Liste(url, title):
	PLog("Beitrag_Liste: " + title)
	PLog(url); 
	if url.startswith("/de/"):
		url = "https://www.arte.tv" + url
	PLog(url) 
	
	page = get_ArtePage('Beitrag_Liste', title, path=url)	
	if page == '':	
		msg1 = "Keine Videos oder Folgeseiten gefunden."
		msg2 = "Eventuell liegen nur redaktionelle Inhalte vor zu:"
		msg3 = "[B]%s[/B]" % title
		MyDialog(msg1, msg2, msg3)
		return
	
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")							# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)						# Home-Button

	ID='Beitrag_Liste'
	if url.find('pageId=MOST_RECENT') > 0:						# Neueste Videos
		ID='MOST_RECENT'
	li,cnt = GetContent(li, page, ID=ID) 						# eigenes ListItem
	
	page = str(page)
	if page.find("pagination"):									# Mehr-Beiträge?
		ArteMehr(page, li)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# holt die Videoquellen -> Sofortstart bzw. Liste der  Auflösungen 
# tag hier || behandelt (s. GetContent)
# externe Trailer-Erkennung nicht eindeutig, s. GetContent
#
# 14.01.2023 Korrektur "_de"-Endung in pid (falls pid=url)
# 11.03.2023 bei Bedarf alternative HBBTV-Quellen nutzen, siehe
#	 lokale Doku 00_Arte_HBBTV_Links
# 24.11.2023 Check api_opa und api_V2: wie bisher nur HLS-UHD-Quellen in
#	api_V2
# 29.09.2024 Ausfall api/opa/v3/, neu: www.arte.tv/hbbtvv2/.. (s. path2),
#	ohne früheren Link zu den getrennten HBBTV-Quellen, s.a. fix arte 
#	crawler #1010 zu mediathekview/MServer
# 16.12.2024 Für Call von get_streams_from_link fehlende Parameter aus
#	api_v2-Daten ergänzt
#
def SingleVideo(img, title, pid, tag, summ, dur, geo, trailer=''):
	PLog("SingleVideo: " + pid) 
	title_org = title

	if pid.endswith("_de"):			# Bsp. ../de/109228-000-A_de
		pid = pid[:-3]
	PLog(pid)

	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()			 				# wirkt nur auf Label, nicht auf Streamauswahl
	if trailer:														# eindeutige Trailer? s.o.
		path1 = 'https://api.arte.tv/api/player/v2/trailer/%s/%s' % (lang,pid)	 
		
	path1 = 'https://api.arte.tv/api/player/v2/config/%s/%s' % (lang,pid)	# nur  HLS-Quellen, ev. Teaser (20.04.2022)
	# neu ab 29.09.2024 nur MP4-Quellen
	path2 = "https://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/streams/%s/SHOW/%s"  % (pid, lang)	
	header = "{'Authorization': 'Bearer Nzc1Yjc1ZjJkYjk1NWFhN2I2MWEwMmRlMzAzNjI5NmU3NWU3ODg4ODJjOWMxNTMxYzEzZGRjYjg2ZGE4MmIwOA',\
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',\
		'Accept': 'application/json'}"

	page, msg = get_page(path1, do_safe=False)						# api_v2_Call
	if page == '':						
		msg1 = L(u'Fehler in SingleVideo') + ": %s" % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(len(page))
	page = page.replace('\\/', '/')
	page = page.replace('\\"', '*')			# Bsp. "\"Brisant\""
	#RSave('/tmp2/x_artestreams_v2.json', py2_encode(page))	# Debug		

	try: 															# fehlende Daten für get_streams_from_link
		objs = json.loads(page)["data"]["attributes"]
		obj = objs["metadata"]
		title_new = obj["title"]
		summ_new = obj["description"]
		dur_new = obj["duration"]["seconds"]
		if dur_new == None:
			dur_new = ""					
		PLog('dur_new: ' + str(dur_new))
		if dur_new:
			dur_new = seconds_translate(dur_new)
		img_new = obj["images"][0]["url"]
			
		obj = objs["restriction"]
		geo_new  = obj["geoblocking"]["code"]

		tag_new = "Dauer: %s\nGeoblock-Info: %s" % (dur_new, geo_new)	# hier ohne Verfügbar von/bis
		PLog("title_new: %s, dur_new: %s, tag_new: %s, summ_new: %s, img_new: %s" % (title_new,dur_new,tag_new,summ_new[:80],img_new)) 
	except Exception as exception:
		title_new="";dur_new="";tag_new="";summ_new="";img_new=""
		PLog("page_error " + str(exception))		

	if summ == '':													# ev. nicht besetzt in Beitrag_Liste. Fehlt in stream_* Dateien
		summ = summ_new
	if title == '':													# get_streams_from_link (leere Param außer pid)
		title = title_new
		title_org = title_new
		dur = dur_new; geo = geo_new; tag = tag_new; img = img_new

	summ=transl_json(summ); summ=repl_json_chars(summ)				# -> HLS_List, HBBTV_List, MP4_List
	
	
	hls_add=""; mp4_add=""											# HLS_List + Titelzusatz für Trailer
	trailer_hls, HLS_List = get_streams_api_v2(page,title_org,summ)
	PLog("trailer_hls: " + str(trailer_hls))
	if trailer_hls:													# Trailer eher in MP4_List wahrsch.
		hls_add = ", HLS-Streams: [B]Trailer[/B]"
	
	#-------------------------------------------------------------	# HBBTV-MP4-Quellen
	page, msg = get_page(path2, do_safe=False)						# Bearer entbehrlich 
	#RSave('/tmp2/x_artestreams_hbbtvv2.json', py2_encode(page))	# Debug	
	MP4_List=[]
	try:
		page = json.loads(page)
		formitaeten = page["videoStreams"]
	except Exception as exception:
		formitaeten=""; MP4_List=[]
		PLog("json_error_path2: " + str(exception))	

	if formitaeten:
		trailer_mp4, MP4_List = get_streams_hbbtvv2(formitaeten, title_org, summ)
		if trailer_mp4:
			mp4_add = ", MP4-Streams: [B]Trailer[/B]"

	HBBTV_List=[]
	PLog("HLS_List: " + str(len(HLS_List)))
	PLog("MP4_List: " + str(len(MP4_List)))
	PLog("HBBTV_List: in MP4_List")
			
	if not len(HLS_List) and not len(MP4_List):			
		msg1 = u'SingleVideo: [B]%s[/B]' % title
		msg2 = L(u'Streams leider (noch) nicht verfügbar.')
		msg3=""
		if SETTINGS.getSetting('pref_video_direct') == 'true':	
			msg3 = L(u"Mehr Streamauswahl ohne Sofortstart!")
		MyDialog(msg1, msg2, msg3)
		return
	
	if SETTINGS.getSetting('pref_video_direct') == 'true':			# Sofortstart hier (s.o.) + raus
		PLog('Sofortstart: SingleVideo')
		title_hls = "%s %s" % (title_org, hls_add)
		PlayVideo_Direct(HLS_List, MP4_List, title=title_hls, thumb=img, Plot=summ, ID="Arte")
		return 
	#---------
	
	ID = 'arte'
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	Dict("store", '%s_MP4_List' % ID, MP4_List) 

	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")								# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)							# Home-Button
	
	if hls_add:														# Trailer-Zusatz	
		title = "%s %s" % (title, hls_add)
	if mp4_add:	
		title = "%s %s" % (title, mp4_add)
	tagline = "Titel: %s\n\n%s\n\n%s" % (title, tag, summ)			# s.a. ARD (Classic + Neu)
	tagline=repl_json_chars(tagline); tagline=tagline.replace( '||', '\n')
	Plot=tagline; 
	Plot=Plot.replace('\n', '||')
	sub_path=''
	HOME_ID = ID													# Default ZDF), 3sat
	PLog('Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
		
	ardundzdf.build_Streamlists_buttons(li,title_org,img,geo,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# Auslesen der Streamdetails api-v2-Call (nur HLS)
# Arte verwendet bei HBBTV MP4-Formate wie ZDF (HLS_List bleibt hier
#	aber offenbar leer)
#
def get_streams_api_v2(page, title, summ):
	PLog("get_streams_api_v2:")
	title_org = title
	
	formitaeten = blockextract('"url":"https', page) 				# Bsp. "id":"HTTPS_MQ_1", "id":"HLS_XQ_1"
	PLog(len(formitaeten))
	
	HLS_List=[]; trailer=False; uhd_m3u8=""
	for rec in formitaeten:	
		url = stringextract('"url":"',  '"', rec)
		if url.find("Trailer") > 0:
			trailer = True
		mediaType = stringextract('"protocol":"',  '"', rec)
		bitrate = ""
		
		mainQuality = stringextract('"mainQuality":',  '}', rec)
		quality = stringextract('"code":"',  '"', mainQuality)		# Bsp.: "XQ"
		width = stringextract('"label":"',  '"', mainQuality)		# "720p"
		height="?"
		size = "%sx%s" % (width, height)
		size = size.replace("p", "")
		
		versions = stringextract('"versions":',  '}', rec)
		lang = stringextract('"label":"',  '"', versions)			# z.B. Deutsch (Original)
		lang = transl_json(lang)
		
		if quality == "XQ" and lang == "Deutsch":					# Link für UHD-Extrakt 					
			uhd_m3u8 = url
			uhd_details = "%s##%s" % (lang, title)
		
		PLog('Satz3:')
		PLog(url); PLog(uhd_m3u8); PLog(quality); PLog(size); PLog(lang);
		
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
			HLS_List.append(u'HLS, [B]%s[/B] ** Auflösung %s ** AUTO ** %s#%s' % (lang, size, title, url))
		else:
			if ".m3u8" in url:										# HLS
				HLS_List.append(u'HLS, [B]%s[/B] ** Auflösung %s ** %s ** %s#%s' % (lang, size, quality, title, url))
	
	PLog("uhd_check:")			
	if uhd_m3u8:
		page, msg = get_page(uhd_m3u8)
		ext_list = blockextract("STREAM-INF", page)
		PLog(len(ext_list))
		uhd=""
		for item in ext_list:
			res = stringextract('RESOLUTION=',  ',', item)
			PLog(res)
			if "3840x" in item:
				PLog(item)
				uhd = item.splitlines()[-2]							# Bsp.: videos/106654-000-G_v2160.m3u8
				PLog("uhd: " + uhd)
				break
		
		if uhd:
			try:
				# s = uhd_m3u8.split("/")[:-2]						# Basis: Url
				base = uhd_m3u8.split("/")[:-1]
				base = "/".join(base)
				uhd_stream = "%s/%s" % (base, uhd)					# plus uhd-Anhängsel
			except Exception as exception:
				PLog(str(exception))
				uhd_stream=""				
			PLog("uhd_stream: " + uhd_stream)
			if uhd_stream:											# HLS-Liste ergänzen
				if url_check(uhd_stream, caller='get_streams_api_v2', dialog=False):	# Url-Check
					lang, title = uhd_details.split("##")
					line = u'[B]UHD_HLS[/B], [B]%s[/B] ** Auflösung %s ** %s ** %s#%s' % (lang, "3840x2160", "XQ", title, uhd_stream)
				
			HLS_List.insert(0, line)								# -> 1. Position wie ZDF-HLS-UHD 
		
	return trailer,HLS_List

# ----------------------------------------------------------------------
# 29.09.2024 Streamdetails via hbbtvv2-Link, formitaeten=json 
# Arte verwendet bei HBBTV MP4-Formate wie ZDF, HLS_List s. get_streams_api_v2
# audioLabel: Abgleich setting pref_arte_streams in get_bestdownload
# 
def get_streams_hbbtvv2(formitaeten, title, summ):
	PLog("get_streams_hbbtvv2:")
	title_org = title
	PLog(len(formitaeten))
	
	MP4_List=[]; trailer=False
	for rec in formitaeten:	
		quality = rec["quality"]
		width = rec["width"]
		height = rec["height"]
		if height == "": height = "?"
		size = "%sx%s" % (width, height)

		url = rec["url"]
		if url.find("Trailer") > 0 or url.find("_EXTRAIT_") > 0:	# Trailer-Kennz. (Stand 22.05.2022)
			trailer = True
		try:
			bitrate = re.search(r'_MP4-(\d+)_', url).group(1)
		except Exception as exception:					
			PLog("bitrate_error:  " + str(exception))
			bitrate = width											# dummy-Marker

		lang = rec["audioLabel"]
		shortLabel = rec["audioShortLabel"]
		
		PLog('Satz5:')
		PLog(url); PLog(size); PLog(bitrate); PLog(lang);
		
		#	für Sofortstart nur Deutsch auswählen (HLS + MP4)
		if SETTINGS.getSetting('pref_video_direct') == 'true':	
			if lang.strip() != "Deutsch":	# Sofortstart nur Deutsch
				PLog("skip_%s" % lang)
				continue
		
		# versch. Streams möglich (franz, UT, ..) - in Konzert-Streams
		#	Einzelauflösungen alle erlauben (s.o.),
		#	für Sofortstart nur Deutsch auswählen (HLS + MP4)
		#	Downloads (MP4): get_bestdownload berücksichtigt Setting pref_arte_streams
		# skip Parseplaylist für master.m3u8 (arte liefert Auflösungen als master.m3u8)
		if ".mp4" in url:										# MP4
			title_url = u"%s#%s" % (title, url)
			mp4 = "MP4 [B]%s[/B]" % (lang)
			item = u"%s | %s ** Bitrate %s ** Auflösung %s ** %s" %\
				(mp4, quality, bitrate, size, title_url)
			MP4_List.append(item)

	return trailer,MP4_List
	
# ----------------------------------------------------------------------
# Buttons für Startseite, Kategorien und Neueste Videos
#
# 15.01.2023 Auswertung wg. mehrmaliger Arte-Änderungen des eingebetteten json-
#	Codes auf json (statt strings) umgestellt, api-Path für Neueste Videos
# 14.03.2023 Unterstützung aller Arte-Sprachen 
# 21.11.2024 Kat_ID's nicht mehr genutzt, dafür katlinks aus arte_lang.json
# 25.03.2025 Umstellung auf hbbtv, BASE_ARTE entfällt
# 
def Kategorien():
	PLog("Kategorien:")

	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")				# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)			# Home-Button

	# Format: Titel-deutsch | Icon | Kat_ID | verfügbar für Sprache
	l1=L("Dokus und Reportagen"); l2=L("Kino"); l3=L("Fernsehfilme und Serien");
	l4=L("Aktuelles und Gesellschaft"); l5=L("Kultur und Pop"); l6=L("ARTE Concert");
	l7=L("Wissenschaft"); l8=L("Entdeckung der Welt"); l9=L("Geschichte");
	cat_list = [u"%s|arte_dokus.png|DOR" % l1, 
				u"%s|arte_kino.png|CIN" % l2,
				u"%s|arte_filme.png|SER" % l3, 
				u"%s|arte_act.png|ACT" % l4,
				u"%s|arte_kultur.png|CPO" % l5, 
				u"%s|arte_conc.png|arte_concert" % l6,
				u"%s|arte_science.png|SCI" % l7, 
				u"%s|arte_entdeck.png|DIS" % l8, 		
				u"%s|arte_his.png|HIS" % l9
				]
	
	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()			# fr, de, ..	
	summ  = "[B]%s[/B]" % arte_lang 
	
	# Kategorienpfade laden
	fname = os.path.join("%s/resources/arte_lang.json") % ADDON_PATH
	if os.path.exists(fname) == False:
		PLog("fehlt: %s, default: de" % fname)	
		katlinks = "dokumentationen-und-reportagen/|kino/|fernsehfilme-und-serien/|aktuelles-und-gesellschaft/|kultur-und-pop/|arte-concert/|wissenschaft/entdeckung-der-welt/|geschichte/"
	else:
		items = RLoad(fname, abs_path=True)
		obj = json.loads(items)
		katlinks = obj["katlinks"][lang]
		PLog("katlinks: " + str(katlinks))
		katlinks = katlinks.split("|")
	PLog("katlinks: " + str(katlinks))
	PLog(len(katlinks))
	
	path = "https://www.arte.tv/hbbtv-mw/api/1/skeletons/pages/" 
	path=py2_encode(path)
	
	fparams="&fparams={}" 										# Button Startseite
	l = L("Startseite")
	addDir(li=li, label=u"%s [B]www.arte.tv/%s[/B]" % (l, lang), action="dirList", dirID="resources.lib.arte.ArteStart", 
		fanart=R(ICON_ARTE), thumb=R(ICON_ARTE_START), summary=summ, fparams=fparams)

	for i, item in enumerate(cat_list):							# Buttons Kategorien
		katurl=""
		title, img, Kat_ID = item.split("|")

		if katlinks[i] == "dummy":								# aktuelles-und-gesellschaft=dummy für en,es,
			PLog("empty_katlinks: %d" %i)
			continue
		katurl = "%s%s?lang=%s" % (path, Kat_ID, lang)
					
		l = L("Kategorie")
		tag = u"%s: [B]%s[/B]" % (l, title)
	
		PLog('Satz4:')
		PLog(title); PLog(arte_lang); PLog(katurl);
		title=py2_encode(title); katurl=py2_encode(katurl)
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(katurl), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteStart", fanart=R(ICON_ARTE), 
				thumb=R(img), tagline=tag, summary=summ, fparams=fparams)

	title = L("Neueste Videos")									# Button Neueste Videos
	path = "https://www.arte.tv/api/rproxy/emac/v4/%s/web/zones/daeadc71-4306-411a-8590-1c1f484ef5aa/content?abv=A&page=1&pageId=MOST_RECENT&zoneIndexInPage=0" % lang
	title=py2_encode(title); path=py2_encode(path); 
	fparams="&fparams={'title': '%s', 'url': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", fanart=R(ICON_ARTE), 
		thumb=R(ICON_ARTE_NEW), summary=summ, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------------------------------------
# 24.03.2025 neu mit hbbtv
# Startseite arte - Step1 Übersicht, Step2 Folgeseiten (path, title)
#	Step2 zusätzl. Verteiler Folgebeiträge aus hbbtv-Ergebnissen
#
def ArteStart(path="", title=""):
	PLog("ArteStart: " + path)

	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()				# fr, de, ..

	step1=True	
	if path == "":
		path = "https://arte.tv/hbbtv-mw/api/1/skeletons/pages/home?lang=%s" % lang	
	else:
		step1=False

	page = get_ArtePage('ArteStart', "ArteStart", path)	
	if page == "":
		return
	
	li = xbmcgui.ListItem()
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")					# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)				# Home-Button

	if step1:
		# -------------------------------------------------------------- # Step1 Übersicht
		PLog("ArteStart_Step1:")
		thumb = R(ICON_DIR_FOLDER)
		fanart = R(ICON_ARTE)
		tag=""
		
		title = L(u"Programme in UHD-Qualität")							# UHD-Button vor Startseite
		href = "https://www.arte.tv/hbbtv-mw/api/1/skeletons/collections/RC-022710?lang=%s" % lang
		title=py2_encode(title); href=py2_encode(href);
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))							
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteStart", 
			fanart=fanart, thumb=thumb, tagline=tag, fparams=fparams)
			
		try:
			items = page["collections"]
			PLog(str(items)[:80])
		except Exception as exception:
			items=[]
			PLog("json_error1: " + str(exception))

		skip_list=["Ihre Woche auf arte.tv", "Meine Liste",	
				"Meine Videos weiterschauen"]
		try:
			for item in items:											# Liste Startseite
				PLog(str(item)[:80])
				title = item["title"]
				if title in skip_list:
					continue
				link = item["link"]
				href = "%s%s?lang=%s" % (HBBTV_BASE, link, lang)
				img = get_img_pre(href, title)							# Bild 1. Beitrag Zielseite
				if img:
					thumb = img
				
				PLog('Satz7:')
				PLog(title); PLog(href)
				title=py2_encode(title); href=py2_encode(href);
				fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))							
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.ArteStart", 
					fanart=fanart, thumb=thumb, tagline=tag, fparams=fparams)
				
		except Exception as exception:
			PLog("json_error2: " + str(exception))
	else:
		# -------------------------------------------------------------- # Step2 Folgeseiten
		# leere Seiten möglich, Bsp. Event-Teaser, in Liste ohne Bild
		PLog("ArteStart_Step2:")	
		ID = "HBBTV"
		GetContent(li, page, ID, ignore_pid="", OnlyNow="", lang=lang)
			
						
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------------------------------------
# 27.03.2025 Folgebeiträge aus Suche + Neueste Videos werden hier auf 
#	hbbtv umgesetzt (collections/RC-..), damit entfallen ArteCluster_2
#	und get_cluster
#
def ArteCluster(pid='', title='', katurl=''):
	PLog("ArteCluster: " + pid)
	PLog(title); PLog(katurl); 
	title_org = title
	pid_org=pid
	ping_uhd = False
	
	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()			# fr, de, ..
	
	if katurl.startswith("http") == False:			# Folgebeiträge aus Suche + Neueste Videos
		rc = stringextract("/RC-", "/", katurl)
		PLog("set_katurl_RC: %s" % rc)
		katurl = "%s/api/1/skeletons/collections/RC-%s?lang=%s" % (HBBTV_BASE, rc, lang)		
	PLog(katurl); 
	katurl_org=katurl

	page = get_ArtePage('ArteCluster', title, path=katurl)
	
	coll_img=""											# Collection-Bild bei hbbtv
	try:												# s.a. GetContent
		PLog(str(page)[:100])	
		if "pageProps" in page:							# Web-json
			page = page["pageProps"]["props"]["page"]["value"]
			values = page["zones"]
		elif "hbbtv-mw" in katurl:
			values = page
		else:
			values=[]
		PLog(len(page))
	except Exception as exception:
		PLog("json_error: " + str(exception))
		values=[]
	
	PLog("values: %d" % len(values))
	if len(values) == 0:
		PLog("values_0")
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return

	PLog(str(values)[:100])	
	img_def = R(ICON_DIR_FOLDER)
	li = xbmcgui.ListItem()
						
	PLog('ArteCluster_1:')
	PLog(str(values)[:100])
	l = L(u'Zurück zum Hauptmenü')
	ltitle = u" %s %s" % (l, "arte")					# Startblank s. home
	li = home(li, ID='arte', ltitle=ltitle)				# Home-Button
		
	if "hbbtv-mw" in katurl:							# hbbtv direkt -> GetContent
		ID = "HBBTV"
		GetContent(li, page, ID, ignore_pid="", OnlyNow="", lang=lang)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
		return
	
	for item in values:
		PLog(str(page)[:60])
		tag=""; anz=""
		
		pid = item["id"]
		title = item["title"]
		title = transl_json(title)
		
		PLog("Mark0")
		skip=False
		for s in skip_item:
			if title.find(s) >= 0: 
				if title != "Alle Videos":				# trotz data":[] möglich
					PLog("skip_item: " + s); 
					skip=True
		if skip: 
			PLog("skip_title: " + title)
			continue	
		try:
			anz = len(item["content"]["data"])
			descr=""
			tag = L(u"Folgebeiträge") + ": %d" % anz			
			img = item["content"]["data"][0]["mainImage"]["url"]
			img = img.replace('__SIZE__', '400x225')	# nur 400x225 akzeptiert
		except Exception as exception:
			PLog("json_error4: " + str(exception))
			img = img_def
		if anz == 0:
			PLog("skip_no_anz: " + title)
			continue
			
		PLog('Satz2:')
		PLog(title); PLog(pid); PLog(katurl); PLog(img); PLog(anz);
		title_org = title								# unverändert für Abgleich
		title = repl_json_chars(title) 
		label = title
		summ  = "[B]%s[/B]" % arte_lang 
		if descr:
			summ = "%s\n%s" % (summ, descr)
		
		title=py2_encode(title); katurl=py2_encode(katurl);
		title_org=title
		fparams="&fparams={'pid': '%s', 'title': '%s', 'katurl': '%s'}" %\
			(pid, quote(title_org), quote(katurl))
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.arte.ArteCluster", 
			fanart=R(ICON_ARTE), thumb=img, tagline=tag, summary=summ, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------------------------------------
# holt Mehr-Beiträge -> get_next_url (ab "pagination") für
#	Neueste Videos Beitrag_Liste
# page = string
def ArteMehr(page, li=''):
	PLog("ArteMehr:")
	
	next_url,page_akt,page_anz,anz,next_page = get_next_url(page)
	if next_url:
		title = L(u"Weitere Beiträge")
		tag = u"weiter zu [B]Seite %s[/B] (Seiten: %s, Beiträge: %s)" % (next_page, page_anz, anz)
		img = R(ICON_MEHR)

		next_url=py2_encode(next_url);# title=py2_encode(title);
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(next_url), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Beitrag_Liste", fanart=img, 
			thumb=img , fparams=fparams, tagline=tag)
	return
	
# ---------------------------------------------------------------------
# 14.01.2023 json.loads - soweit möglich
#
def get_ArtePage(caller, title, path, header=''):
	PLog("get_ArtePage: " + path)
	PLog(caller); PLog(path)
	
	if path == '':
		PLog("path_fehlt")
		return page

	page, msg = get_page(path, header=header)
	if page == '':						
		msg1 = u"%s: " % caller + L("nicht verfügbar") + ":"
		msg2 = title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return ''

	PLog("extract:"); 
	page = py2_encode(page)
	if '"Not found' in str(page)[:44]:						# {"error": "Not found /de/hbbtv/pages/..
		msg2 = stringextract('error": "', '"}', str(page))
		if msg2:
			msg1 = 'Arte meldet:'
			MyDialog(msg1, msg2, '')
			return ''
	else:
		try:
			page = json.loads(page)
		except Exception as exception:
			page=""
			PLog("page_json_error: " + str(exception))

	#RSave('/tmp2/x_artePage.json', py2_encode(str(page)))	# Debug	
	PLog(len(page))
	PLog("page_start: %s" % str(page)[0:60])
	PLog("page_end: %s" % str(page)[-60:])
	return page
	
# ---------------------------------------
# ermittelt next-Url in pagination 
#	(json -> strings)
# Anpassung api-Call (Variante ohne Auth-Header)
#	
def get_next_url(page):
	PLog("get_next_url:")
	page = str(page)
	pos = page.find("pagination")
	p = page[pos:]
	if "':" in p:
		p = p.replace("'", "\"")
	PLog(p[:200])

	page_akt =stringextract('"page": ', ',', p)
	page_anz =stringextract('"pages": ', ',', p)
	try:
		anz = re.search(r'totalCount": (\d+)', p).group(1)
	except Exception as exception:
		anz=""
		PLog("anz_error: " + str(exception))
	
	
	next_url = stringextract('"next": "', '"', p)
	next_page = stringextract('page=', '&', next_url)
	
	if next_url:
		PLog("next_url_found: " + next_url)
		# api-internal-Call endet mit HTTP Error 401: Unauthorized
		# next_url = next_url.replace("api-internal.arte.tv/api", "www.arte.tv/api/rproxy")
		# 17.01.2025 neuer Serverlink: api-internal.infra-priv.arte.tv funktioniert nicht
		# next_url = next_url.replace("api-internal.infra-priv.arte.tv/api", "www.arte.tv/api/rproxy")
		# 01.02.2025 api-internal-Call nicht mehr verwendet:
		next_url = next_url.replace("/api/emac/", "www.arte.tv/api/rproxy/emac/")
		# 12.02.2025 api-cdn.arte.tv am Url-Start beobachtet
		next_url = next_url.replace("api-cdn.arte.tv", "")
		if next_url.startswith("http") == False:
			next_url = "https://" + next_url 
		PLog("next_url_correct: " + next_url)
	
	PLog("next_url: %s, page_akt: %s, page_anz: %s, anz: %s, next_page: %s" % (next_url, page_akt, page_anz, anz, next_page))
	return next_url,page_akt,page_anz,anz,next_page
	
# ----------------------------------------------------------------------
# einfache Übersetzungsfunktion (deutsch -> gewählte Sprache)
# Format s. arte_lang.json
#
def L(string):	
	PLog('L_func: ' + string)
	
	arte_lang = Dict('load', "arte_lang")
	lang = arte_lang.split("|")[1].strip()			# fr, de, ..
	PLog("lang: " + arte_lang)
		
	# erstes / für Leia erforderlich:
	fname = os.path.join("%s/resources/arte_lang.json") % ADDON_PATH
	if os.path.exists(fname) == False:
		PLog("fehlt: %s" % fname)	
		return 	string
	
	items = RLoad(fname, abs_path=True)
	lstring=""
	try:
		obj = json.loads(items)
		msgs = obj["strings"]["msgstr"]
		PLog("strings: %d" % len(msgs))
		for msg in msgs:
			# PLog("string: %s, msg_de: %s" % (string, msg["de"])) # Debug
			if string in msg["de"]:					# Bsp. es: Folgebeiträge -> 
				lstring = msg["%s" % lang]			#	Artículos complementarios
				break
	except Exception as exception:
		PLog("L_error: " + str(exception))
			
	if lstring:
		PLog("lstring_found: %s" % lstring)
		return lstring
	else:
		PLog("lstring_not_found: %s" % string)
		return string								# Rückgabe Basis-String, falls kein Paar gefunden
