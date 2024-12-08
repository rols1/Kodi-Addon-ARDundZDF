# -*- coding: utf-8 -*-
################################################################################
#				my3Sat.py - Teil von Kodi-Addon-ARDundZDF
#							Start Juni 2019
#			Migriert von Plex-Plugin-3Sat_Mediathek, V0.5.9
#
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.3sat.de,
#	Seiten werden im html-Format, teils. json ausgeliefert
#
#	04.11.2019 Migration Python3  Python3 Modul future
#	18.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#	Nov./Dez. 2024 Umstellung Web-scraping -> api hbbtv.zdf.de
# 	
################################################################################
# 	<nr>23</nr>										# Numerierung für Einzelupdate
#	Stand: 07.12.2024

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

# Python
import string, re
import  json, ssl		
import datetime, time

# Addonmodule + Funktionsziele (util_imports.py)
# import ardundzdf reicht nicht für thread_getpic
from ardundzdf import *					# -> get_query, test_downloads, Parseplaylist, 
										# thread_getpic, ZDF_SlideShow, get_ZDFstreamlinks
from resources.lib.util import *


# Globals
ICON_TV3Sat 		= 'tv-3sat.png'
ICON_MAIN_ARD 		= 'ard-mediathek.png'			
ICON_MAIN_TVLIVE 	= 'tv-livestreams.png'		
			
ICON_SEARCH 		= 'ard-suche.png'						
ICON_DIR_FOLDER		= "Dir-folder.png"
ICON_SPEAKER 		= "icon-speaker.png"
ICON_MEHR 			= "icon-mehr.png"

DreiSat_BASE 		= 'https://www.3sat.de'
DreiSat_AZ 			= "https://www.3sat.de/sendungen-a-z"				# HBBTV -> HTML via sid			
DreiSat_Verpasst	= "http://hbbtv.zdf.de/3satm/dyn/get.php?id=special:time" 
DreiSat_Suche		= "https://hbbtv.zdf.de/3satm/dyn/search.php?t=%s&search=%s"
DreiSat_HBBTV 		= "http://hbbtv.zdf.de/3satm/dyn/get.php?id="
DreiSat_HBBTV_HTML  = "https://www.3sat.de/%s.html"						# HBBTV -> HTML via sid


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])
FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

my3satCacheTime =  600											# 10 Min.: 10*60	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):				# ADDON_DATA-Verzeichnis anpasen
	PLog('my3Sat_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")

days = int(SETTINGS.getSetting('pref_TEXTE_store_days'))
SophoraTeaser = os.path.join(TEXTSTORE, "SophoraTeaser")
ClearUp(SophoraTeaser, days*86400		)						# Cache SophoraTeaser bereinigen


DEBUG			= SETTINGS.getSetting('pref_info_debug')
NAME			= 'ARD und ZDF'

#----------------------------------------------------------------
# Aufrufer: Haupt-PRG, Menü Main
#
def Main_3Sat(name=''):
	PLog('Main_3Sat:'); 
	PLog(name)
				
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	PLog("li:" + str(li))						
			
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'gesucht wird in [B]3Sat[/B]'
		title=py2_encode(title);
		func = "resources.lib.my3Sat.Main_3Sat"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "3Sat", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R('3sat.png'), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
	
	title="Suche in 3sat-Mediathek"	
	tag = "Suchergebnisse begrenzt auf: 25"	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
		thumb=R('zdf-suche.png'), tagline=tag, fparams=fparams)
			
	title, tag, summ = get_epg()
	if title:
		tagline = tag
		summary = summ
	else:
		title = '3sat-Livestream'
	title=py2_encode(title); title=py2_encode(title);
	fparams="&fparams={'name': '%s', 'epg': '%s'}" % (quote(title), quote(title))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Live", 
		fanart=R('3sat.png'), thumb=R(ICON_MAIN_TVLIVE), tagline=tag, summary=summ, fparams=fparams)
	
	title = "Startseite"
	path = 	DreiSat_HBBTV + "3sat-startseite-100"					
	summ = "Startseite der 3sat-Mediathek"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Start", 
		fanart=R('3sat.png'), thumb=R('3sat.png'), summary=summ, fparams=fparams)

	title = 'Verpasst'
	summ = 'aktuelle Beiträge eines Monats - nach Datum geordnet'
	fparams="&fparams={'title': 'Sendung verpasst'}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Verpasst", 
		fanart=R('3sat.png'), thumb=R('zdf-sendung-verpasst.png'), summary=summ, fparams=fparams)
	
	title = "Sendungen A-Z | 0-9"	
	summ = "Sendereihen - alphabetisch geordnet"
	DreiSat_AZ 		= "https://www.3sat.de/sendungen-a-z"			# geht hier nach epg verloren	
	title=py2_encode(title); DreiSat_AZ=py2_encode(DreiSat_AZ);
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(DreiSat_AZ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZlist", 
		fanart=R('3sat.png'), thumb=R('zdf-sendungen-az.png'),  summary=summ, fparams=fparams)
												
	title = "Themen"
	path = 'http://hbbtv.zdf.de/3satm/dyn/get.php?id=themen-100'								
	summ = "Thementage, Themenwochen und 3sat-Themen"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.PageMenu_3sat", 
		fanart=R('3sat.png'), thumb=R('zdf-themen.png'), summary=summ, fparams=fparams)		

	title = "Rubriken"
	path = 'https://hbbtv.zdf.de/3satm/dyn/get.php?id=special:topic'		
	summ = "Dokumentation, Film, Gesellschaft, Kabarett, Kultur, Wissen"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.PageMenu_3sat", 
		fanart=R('3sat.png'), thumb=R('zdf-rubriken.png'), summary=summ, fparams=fparams)

	title = 'Bilderserien 3sat'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Bilder3sat",
		fanart=R('3sat.png'), thumb=R('zdf-bilderserien.png'), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		 		
####################################################################################################
# neu: api hbbtv.zdf.de
# Offsets search=1, search=2 usw. funktionieren im api (noch) nicht, 
#	vorerst deaktiviert - Ergebnisse begrenzt auf 25
#
def Search(offset="1", query=''):
	PLog('Search:'); 
	if 	query == '':	
		query = get_query(channel='ZDF')
		
	query = py2_decode(query)
	name = 'Suchergebnis zu: ' + unquote(query)
	PLog("name: " + name)
	if  unquote(query) == None or unquote(query).strip() == '':
		Main_3Sat()									# statt return - s.o.	
		
	path = DreiSat_Suche % (query, offset)
	page, msg = get_page(path=path, do_safe=False)		# ohne quote in get_page, dto. in Sendereihe_Sendungen	
	if page == '':			
		msg1 = "Fehler in Search"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return
		
	query_unqoute = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
	if '"titletxt":"Keine passende' in page:						# kein Treffer
		msg1 = 'Leider kein Treffer (mehr) zu: '  + query_unqoute
		PLog(msg1)
		MyDialog(msg1, '', '')
		return	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')								# Home-Button

	try:
		result = json.loads(page)["result"]
		PLog("result: " + str(result)[:100])				# i.d.R. zwei elems-Level
		PLog(len(result))
	except Exception as exception:
		PLog("result_error " + str(exception))		

	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Kennz. Video für Sofortstart 
		mediatype='video'
	fanart=R('3sat.png')
	DreiSat_HBBTV_HTML = "https://www.3sat.de/%s.html"				# SingleBeitrag mit sid via html

	for item in result:										# i.G.z. Rubriken nur 1 Ebene
		PLog(str(item)[:60])
		linktyp,title,dauer,tag,descr,img,sid = my3sat_content(item, mark=query_unqoute)
		if linktyp == "":						# exception
			continue
		
		PLog('Satz4:')
		PLog(linktyp); PLog(title); PLog(img); PLog(sid);PLog(fanart);
		title=py2_encode(title); 
		
		if linktyp == "video":
			path = DreiSat_HBBTV_HTML % sid
			tag = "Dauer [B]%s[/B]\n%s" % (dauer, tag)
			if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Hinw. Inhaltstext bei Sofortstart 
				tag = u"%s\n\n%s" % (tag, u"[B]Inhaltstext[/B] zum Video via Kontextmenü aufrufen.")							 		
			title=py2_encode(title); path=py2_encode(path);	img=py2_encode(img);
			dauer=py2_encode(dauer);
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
				(quote(title), quote(path), quote(img), quote(dauer))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
				fanart=fanart, thumb=img, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)
		
	'''	
	#---------------------------------						# More-Button, deaktiviert - s.o.	
	# Mehr-Url fehlt in hbbtv-Ergebnis
	PLog("More_Button: " + offset)
	li = xbmcgui.ListItem()									# Kontext-Doppel verhindern
	
	offset = int(offset) + 1
	PLog("offset: " + str(offset))
	
	title = "Weiter suchen: %s" %  unquote(query)
	tag = "Weiter zu Seite: %d" % offset
	
	query=py2_encode(query);
	fparams="&fparams={'offset': '%d', 'query': '%s'}" % (offset, quote(query))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
		thumb=R(ICON_MEHR), tagline=tag, fparams=fparams)
	'''
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#------------ 
# A-Z Liste der Buchstaben (mit Markierung 'ohne Beiträge')
# Hier noch Web statt api - Seite nur ca. 115 KByte. Nur die 
#	Buchstabenliste der Webseite enthält gesperrte Buchstaben 
#	(Addon: icon-error.png) - api enthält Buchstabengruppen.
#
def SendungenAZlist(name, path):
	PLog('SendungenAZlist: ' + name)
	DreiSat_AZ 		= "https://www.3sat.de/sendungen-a-z"		# geht hier nach epg verloren	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')									# Home-Button

	page, msg = get_page(path)
	if page == '':			
		msg1 = "Fehler in SendungenAZlist"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return li	
	
	liste = blockextract('<ul class="letter-list"', page)  # 1 x
	content = blockextract('class="item', liste[0])
	PLog(len(content))
	fanart=R('3sat.png')
	
	for rec in content:
		title	= stringextract('title="', '"', rec)
		href	= stringextract('href="', '"', rec)				# ../sendungen-a-z?group=b
		href	= DreiSat_BASE + href
		PLog(title)
		if 'link is-disabled' in rec:							# Button inaktiv
			thumb = R('icon-error.png')
			letter = stringextract('true">', '<', rec)
			title = "[COLOR grey]Sendungen mit %s[/COLOR]" % letter
			fparams="&fparams={}"	 
			addDir(li=li, label=title, action="dirList", dirID="dummy", 
				fanart=fanart, thumb=thumb, fparams=fparams)			
		else:
			thumb = R('Dir-folder.png')
			title=py2_encode(title); href=py2_encode(href);
			fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(href))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZ", 
				fanart=fanart, thumb=thumb, fparams=fparams)			
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------ 
# A-Z Liste der Beiträge
#	-> Sendereihe_Sendungen -> get_zdfplayer_content
# 04.08.2020 Anpassungen an Webänderungen (Rubrik, Titel)
# 16.02.2021 dto (Titel)
# neu: Umsetzung html-Links -> api hbbtv.zdf.de, api-
#	Auswertung der Sendereihen. Damit entfallen api-Calls mit
#	id=special:atoz:8387 u.ä. 
#
def SendungenAZ(name, path): 
	PLog('SendungenAZ: ' + name)

	path = DreiSat_AZ
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in SendungenAZ"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return
		
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')							# Home-Button		

	content = blockextract('<picture class="">', page)
	PLog(len(content))
	
	for rec in content:
		sid=  stringextract('Linkziel:', '"', rec)
		href = DreiSat_HBBTV + sid

		img_src =  stringextract('data-srcset="', ' ', rec)	
		rubrik 	= stringextract('a--preheadline level-4">', '<span class', rec)
		rubrik 	= stringextract('<span>', '</span>', rubrik)
		sub_rubrik = stringextract('ellipsis" >', '<', rec)
		tlink	= stringextract('teaser-title-link', "data-track=", rec)
		title	= stringextract('title="', '"', tlink)
		if "is-lowercase" in title:
			title	= stringextract('case">', '</span>', rec)
		descr	= stringextract('clickarea-link" >', '<', rec)
		tag 	= unescape(rubrik)
		if sub_rubrik:
			tag = "%s | %s" % (tag, sub_rubrik)
		tag = cleanhtml(tag)

		title=unescape(title)
		title = repl_json_chars(title); descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	

		PLog('Satz1:')
		PLog(href); PLog(img_src); PLog(rubrik); PLog(title);  PLog(sid); PLog(descr);
			
		title=py2_encode(title); href=py2_encode(href);  img_src=py2_encode(img_src);	
		fparams="&fparams={'title': '%s', 'path': '%s', 'allcover': 'true'}"	% (quote(title), quote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.CoverSingle", 	# oder PageMenu_3sat
			fanart=R('3sat.png'), thumb=img_src, summary=descr, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
	
#------------
# 12.2024 Umstellung auf HBBTV-Api
# DreiSat_Verpasst liefert 2 Wochen, je 1 Woche vor und nach akt. Datum
#
def Verpasst(title):	
	PLog('Verpasst:')
	
	path = DreiSat_Verpasst										# 14 Tage
	page = Dict("load", '3satPRG', CacheTime=my3satCacheTime)	# 10min	
	if page == False:											# nicht vorhanden oder zu alt
		page, msg = get_page(path)
		if page == '':						
			msg1 = 'Fehler in Verpasst:' 
			msg2 = msg
			msg2 = u"Seite weder im Cache noch bei 3sat abrufbar"
			MyDialog(msg1, msg2, '')
			return
		else:
			Dict("store", '3satPRG', page) 	# Cache aktualisieren				
	PLog(len(page))
	
	try:
		elems = json.loads(page)["elems"]
		prg_elems = elems[0]["data"]							# PRG-Beiträge
		wlist = elems[0]["days"]		
		tkey_now = elems[0]["nowKey"]							# tkey_now, tkey_first, tkey_last z.Z.
		tkey_first = prg_elems[0]["tkey"]						#	nicht verwendet
		tkey_last = prg_elems[-1]["tkey"]
		PLog("prg_elems: " + str(prg_elems)[:60])
		PLog("tkey_first: %s, tkey_last: %s, wlist: %d" % (tkey_first, tkey_last, len(wlist)))	
	except Exception as exception:
		PLog("elems_error " + str(exception))
		MyDialog("Verpasst: Problem mit Datenformat", str(exception), "")
		return
				
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')									# Home-Button
		
	for day in wlist:
		title = day["longname"]
		if "Heute" in title:
			title = "[B]%s[/B]" % title
		dayID = day["id"]
		
		PLog('Satz2:')	
		PLog(title); PLog(dayID); 
		title=py2_encode(title); 
		fparams="&fparams={'title': '%s', 'dayID': '%s'}" % (quote(title), dayID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenDatum", 
			fanart=R('3sat.png'), thumb=R(ICON_DIR_FOLDER), fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------
# 12.2024 Umstellung auf HBBTV-Api
#
def SendungenDatum(title, dayID):	
	PLog('SendungenDatum: %s, %s' % (title, dayID))
	
	try:
		if "Heute" in title:								# akt. Tag immer aktualisieren (für lfd. Sendung)
			page, msg = get_page(path=DreiSat_Verpasst)
		else:	
			page = Dict("load", '3satPRG')					# Cache: Verpasst
		elems = json.loads(page)["elems"]
		prg_elems = elems[0]["data"]						# PRG-Beiträge
		PLog("prg_elems: " + str(prg_elems)[:60])
	except Exception as exception:
		PLog("elems_error " + str(exception))
		MyDialog("SendungenDatum: Problem mit Datenformat", str(exception), "")
		return
	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')								# Home-Button
		
	msg1 = title
	msg2 = "3sat"
	icon = R('zdf-sendung-verpasst.png')
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)

	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	for item in prg_elems:
		dur=""; perc=""; descr="";							# descr im api für Programm nicht verfügbar
		foot=""; end=""; vid=""; summ=""; vid=""
		try:
			tkey = item["tkey"]
			# PLog("%s | %s" % (dayID, tkey))
			if tkey.startswith(dayID) == False:
				continue
				
			prgID = item["id"]		
			head = item["head"]								# "Dokumentation | Natur"
			title = item["title"]
			img = item["img"]
			tim = item["tim"]								# "09:45"
			if "foot" in item:								#"03.12.2024", fehlt in lauf. Sendung
				foot = item["foot"]	
			
			if "vid" in item:								# fehlen dann auch im Web (Senderechte?)
				vid = item["vid"]							# "ein-winter-im-schwarzwald-102"
				href = DreiSat_HBBTV_HTML % vid
			else:
				href=""
				PLog("missing_vid: " + title)
			
			if "dur" in item:
				dur = item["dur"]							# "89 min"		
			if "perc" in item:
				perc = item["perc"]							# 12 (int, noch 12 % verfügbar)
				end = item["end"]							# 09:45"
				
			tag = head
			if foot:
				tag = "%s\n%s" %  (tag, foot)
			if dur:	
				tag = "Dauer [B]%s[/B]\n%s" % (dur, tag)
			if perc:										# laufende Sendung
				tag = "%s\nbis %s | noch %d Prozent"	% (tag, end, perc)
				title = "[B]%s[/B]" % title
			
			sendung = "[COLOR blue]%s[/COLOR] | %s" % (tim, title)	# Sendezeit | Titel
			if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Hinw. Inhaltstext bei Sofortstart 
				summ = u"[B]Inhaltstext[/B] zum Video via Kontextmenü aufrufen."							 		
			
		except Exception as exception:
			prgID=""
			PLog("prg_elems_error: " + str(exception))
			
		PLog('Satz3:')
		PLog(sendung); PLog(href); PLog(tag);
				 
		if prgID and href:									# skip exception, skip missing vid->href
			sendung=py2_encode(sendung); href=py2_encode(href); 
			img_src=py2_encode(img); 
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
				(quote(sendung), quote(href), quote(img), descr, dur)
			addDir(li=li, label=sendung, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
				thumb=img_src, tagline=tag, summary=summ, fparams=fparams, mediatype=mediatype)
			 					 	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------
def transl_month(shortmonth):	# Monatsbez. (3-stellig) -> Zahl 
	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	val = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
	
	mval = shortmonth
	for i in range (len(month)):
		m = month[i]
		if m == shortmonth:
			mval = val[i]
			break
	return mval

#------------
# Aufrufer: Main_3Sat, Listing Stage, Rest -> PageMenu_3sat
# neu: api hbbtv.zdf.de
#
def Start(name, path, rubrik=''):
	PLog('3satStart:')
	PLog("rubrik: " + rubrik)
	name_org=name; path_org=path
	
	page = Dict("load", '3satStart', CacheTime=my3satCacheTime)	# 10 min
	if page == False:											# nicht vorhanden oder zu alt
		page, msg = get_page(path)
		if page == '':						
			msg1 = 'Fehler in Start:' 
			msg2 = msg
			msg2 = u"Seite weder im Cache noch im Web verfügbar"
			MyDialog(msg1, msg2, '')
			return
		else:
			Dict("store", '3satStart', page) 					# Seite -> Cache: aktualisieren				
	PLog(len(page))
	
	try:
		elems = json.loads(page)["elems"]
		stage_elems = elems[1]["elems"]							# Stage-Beiträge
		PLog("stage_elems: " + str(stage_elems)[:100])	
		PLog(len(stage_elems))
	except Exception as exception:
		PLog("elems_error " + str(exception))
		MyDialog("Fehler in Start:", "Problem mit Datenformat", str(exception))
		return
				
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')									# Home-Button
	
	mediatype=''; fanart=R('3sat.png'); cnt=0
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	CoverElems(li, stage_elems, top="true")						# Ausgabe Stage
	PageMenu_3sat(name_org, path_org, page=page, li=li)			# restl. Beiträge			
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------
# 11.2024 neu
# Umstellung Web-scraping -> api hbbtv.zdf.de, Mitnutzung vorh. 
#	Ladekette ab SingleBeitrag via HTML-Seite (DreiSat_HBBTV_HTML + sid)
# Aufrufer: Main_3Sat (Themen, Rubriken), Start (hier mit page,
#	stage-Listing dort.
# Quelle: json-Datei type=page. Doppel in stage- und wide-Beiträgen
#	werden akzeptiert (wie im Web)
#
def PageMenu_3sat(name, path, sid='', page="", li=""):
	PLog('PageMenu_3sat: ' + name)
	PLog(sid); 
		
	if sid:
		path = DreiSat_HBBTV + sid							# ../3satm/dyn/get.php?id=kabarett-100
	path_org=path
	if page == "":
		page, msg = get_page(path)	
		if page == '':			
			msg1 = "Fehler in Rubriken:"
			msg2 = msg
			PLog(msg1)
			MyDialog(msg1, msg2, '')
			return 

	try:
		elems = json.loads(page)["elems"]
		PLog("page_elems: " + str(elems)[:100])				# i.d.R. zwei elems-Level
		PLog(len(elems))
	except Exception as exception:
		PLog("elems_error " + str(exception))		
		MyDialog("Fehler in Start:", "Problem m Datenformat", '')
		return
	
	li2 = xbmcgui.ListItem()								# eigenes Listitem für Kontextmenüs
	if li == "":											# Home-Button extern?
		li2 = home(li2, ID='3Sat')							# Home-Button
			
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Kennz. Video für Sofortstart 
		mediatype='video'
	
	fanart=R('3sat.png')
	for entry in elems:
		PLog(str(entry)[:60])								# erste Ebene
		typ = entry["type"]
		variant=""; title=""
		if "variant" in entry:
			variant = entry["variant"]
		if "title" in entry:
			title = entry["title"]
		if typ == "covers":									# Verzweigung -> CoverSingle
			if "stage" in variant == False:					# variant=stage bereits in Start ausgegeben
				PLog("skip_variant_stage")
				continue
			if title:										# title -> CoverSingle
				PLog("covers_with_title: " + title)
				titletxt = entry["elems"][0]["titletxt"]
				tag = unescape(titletxt)
				tag = repl_json_chars(tag)
				label = unescape(title)						# entry["title"]		
				label = repl_json_chars(label)
				PLog("ToCoverSingle: %s, %s" % (label, path_org))
				img = entry["elems"][0]["img"]["hi"]
				tag = "Folgeseiten | 1. Beitrag:\n%s" % tag
				title=py2_encode(title); path=py2_encode(path);	
				img=py2_encode(img);			
				fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title), quote(path_org))
				addDir(li=li2, label=label, action="dirList", dirID="resources.lib.my3Sat.CoverSingle", 
					fanart=fanart, thumb=img, tagline=tag, fparams=fparams)

			else:
				PLog("covers_without_title")
				if "wide" in variant or "std" in variant or "three" in variant:	# bei Bedarf erweitern
					wide_elems = entry["elems"]
					top=""
					if "wide" in variant or "three" in variant:
						top='true'
					CoverElems(li2, wide_elems, top)		# Ausgabe Wide-Beiträge

		elif typ == "list":									# Ausgabe Liste Rubriken
			items = elems[0]["elems"]
			CoverElems(li2, items)	 
			
		else:
			PLog("unknown_entry_type: " + typ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#------------
# Ausgabe elems eines covers
# top steuert TOP-Markierung in stage- und wide-Beiträgen (ohne
#	Numerierung - überlappt bei mehreren wide's)
#
def CoverElems(li, cover, top=""):
	PLog('CoverElems: ')

	fanart=R('3sat.png')
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	
	for entry in cover:	
		linktyp,title,dauer,tag,descr,img,sid = my3sat_content(entry)
		if linktyp == "":									# exception
			continue
		
		PLog('Satz6:')
		PLog(linktyp); PLog(title); PLog(img); PLog(sid);
		if top:												# z.B. stage-Beiträge 
			title = "[B]Top: %s[/B]" % title

		if linktyp == "video":
			path = DreiSat_HBBTV_HTML % sid
			PLog("path: " + path)
			tag = "Dauer [B]%s[/B]\n%s" % (dauer, tag)
			if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Hinw. Inhaltstext bei Sofortstart 
				tag = u"%s\n\n%s" % (tag, u"[B]Inhaltstext[/B] zum Video via Kontextmenü aufrufen.")							 		
			title=py2_encode(title); path=py2_encode(path);	img=py2_encode(img);
			dauer=py2_encode(dauer);
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
				(quote(title), quote(path), quote(img), quote(dauer))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
				fanart=fanart, thumb=img, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)

		elif linktyp == "page":
			if img == "":
				img= R('Dir-folder.png')
			tag = "Folgeseiten\n%s" % tag
			title=py2_encode(title); sid=py2_encode(sid);
			fparams="&fparams={'name': '%s', 'path': '', 'sid': '%s'}" % (quote(title), quote(sid))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.PageMenu_3sat", 
				fanart=fanart, thumb=img, tagline=tag, summary=descr, fparams=fparams)

		else:
			PLog("skip_linktyp: " + linktyp)
			
	return
	
#------------
# 11.2024 neu
# Auswertung eines Covers (analog ZDF-Cluster)
# Aufrufer: PageMenu_3sat (title -> gesuchter cover)
# allcover=true wertet sämtl. cover aus, z.B. SendungenAZ
#
def CoverSingle(title, path, allcover=""):
	PLog('CoverSingle: ' + title)
	PLog(path)
	path_org=path
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in CoverSingle:"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return
	
	try:
		elems = json.loads(page)["elems"]
		PLog("page_elems: " + str(elems)[:100])					# i.d.R. zwei elems-Level
		PLog(len(elems))
	except Exception as exception:
		PLog("elems_error " + str(exception))
		MyDialog("Fehler in CoverSingle:", "Problem m Datenformat", '')
		return		
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')									# Home-Button		

	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Kennz. Video für Sofortstart 
		mediatype='video'
	
	fanart=R('3sat.png'); items=[]

	covers=[]
	for entry in elems:											# Cover (Cluster) suchen
		if entry["type"] == "header":							# header ohne elems
			continue
		variant=""
		if "variant" in entry:
			variant = entry["variant"]
						
		etitle = entry["title"]
		PLog("%s | %s" % (title, etitle))
		if allcover:											# alle cover (Cluster)
			if variant == "std" or variant == "wide":			# wide: breite Beiträge	
				PLog("append_cover: " + etitle)
				items = entry["elems"]					
				covers.append(items)							# cover -> Liste
		else:													# nur title-cover (Cluster)
			if title in etitle:
				if variant == "std" or variant == "wide":		# wide: breite Beiträge							
					PLog("found_cover: " + etitle)
					PLog(str(entry)[:200])
					items = entry["elems"]
					covers.append(items)
					break										# nur 1 cover -> Liste
					
	PLog("covers: %d" % len(covers))
	skip_list=[]
	for cover in covers:		
		for item in cover:
			linktyp,title,dauer,tag,descr,img,sid = my3sat_content(item)
			if linktyp == "":									# exception
				continue

			PLog('Satz5:')
			PLog(linktyp); PLog(title); PLog(img); PLog(sid);
			if sid in skip_list:								# Doppel zu wide-cover verhindern
				continue
			skip_list.append(sid)
			
			if linktyp == "video":
				path = DreiSat_HBBTV_HTML % sid
				tag = "Dauer [B]%s[/B]\n%s" % (dauer, tag)
				if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Hinw. Inhaltstext bei Sofortstart 
					tag = u"%s\n\n%s" % (tag, u"[B]Inhaltstext[/B] zum Video via Kontextmenü aufrufen.")							 		
				title=py2_encode(title); path=py2_encode(path);	img=py2_encode(img);
				dauer=py2_encode(dauer);
				fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
					(quote(title), quote(path), quote(img), quote(dauer))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
					fanart=fanart, thumb=img, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)
	
			elif linktyp == "page":
				if img == "":
					img= R('Dir-folder.png')
				tag = "Folgeseiten\n%s" % tag	
				title=py2_encode(title); sid=py2_encode(sid);
				fparams="&fparams={'name': '%s', 'path': '', 'sid': '%s'}" % (quote(title), quote(sid))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.PageMenu_3sat", 
					fanart=fanart, thumb=img, tagline=tag, summary=descr, fparams=fparams)

			else:
				PLog("skip_linktyp: " + linktyp)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------
# 11.2024 neu
# json-Auswertung für alle Linktypen (video, page in Themen/Rubriken). 
# mark steuert Suchmarkierung (hier auch mehrteilige)
#
def my3sat_content(item, img_qual="hi", mark=""):
	PLog('my3sat_content: ' + str(item)[:60])
	PLog(mark);

	try:
		descr=""; dauer=""; headtxt=""; titletxt="";
		vidlentxt=""; isgroup=""; 
		if "headtxt" in item:
			headtxt = item["headtxt"]
		if "titletxt" in item:
			titletxt = item["titletxt"]
		if "title" in item:
			titletxt = item["title"]
		if "vidlentxt" in item:				# "87 min"
			dauer = item["vidlentxt"]
			
		if "isgroup" in item:
			isgroup = item["isgroup"]
			
		foottxt = item["foottxt"]			# "36 Beiträge"
		
		if "text" in item:
			descr = item["text"] 

		img = item["img"][img_qual]			# std,sq,hi,tea
		link = item["link"]		
		sid = link["id"]					# "tatort-von-affen-und-menschen-104"
		linktyp = link["type"]
		ctyp = link["ctype"]		
		
		# HBBTV-api-Quelle i.d.R. kleine Inhaltstexte, für 3sat ohne Verfügbar und pubDate:
		if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
			path = DreiSat_HBBTV_HTML % sid						# Web-Referenz
			descr_new = get_summary_pre(path, ID='3sat',skip_verf=True,skip_pubDate=True)  # Modul util
			if 	len(descr_new) > len(descr):
				PLog("descr_new: " + descr_new[:60] )
				descr = descr_new
			
		tag = headtxt						# kann fehlen
		if foottxt:
			tag = "%s\n%s" %  (tag, foottxt)		
		
		sidtitle = sid_to_title(sid)		# ergänzender Titel aus Sendungs-ID für tag
		title = titletxt				
		if headtxt in foottxt == False:
			tag = "%s\n%s" % (titletxt, headtxt)
		tag = "%s | [B]%s[/B]" % (tag, sidtitle.strip())

		if mark:
			mlist = mark.split(" ")			# Aufrufer replaceing -> " " (z.B. Search)
			for m in mlist:
				title = make_mark(m, title, "", bold=True)	# Titel-Markierung
		title=unescape(title); title=repl_json_chars(title)
		tag=unescape(tag); descr=unescape(descr); 
			
	except Exception as exception:
		PLog("content_error: " + str(exception))
		linktyp="";title="";dauer="";tag="";descr="";img="";sid=""

	PLog('linktyp: %s | title: %s | dauer: %s | tag: %s | descr: %s |img:  %s | sid: %s' %\
		(linktyp,title,dauer,tag,descr,img,sid) )		
	return linktyp,title,dauer,tag,descr,img,sid

#------------
# 11.2024 neu
# simple Konvertierung (z.B. Datum unbehandelt)
# 	"mitternachtsspitzen-november-kabarett-100" ->
#	"Mitternachtsspitzen November Kabarett"
# Verwendung als zusätzl. Tag
def sid_to_title(sid):
	PLog('sid_to_title: ' + sid)

	title=""
	sid = (sid.replace("---","-").replace("--","-"))
	items = sid.split("-")
	items.pop()							# entf.  Url-Marke 100
	for item in items:
		s = item[0].upper() + item[1:]
		title = "%s %s" % (title, s)

	PLog(title)
	return title 

#------------
# Einzelvideo - Auswertung der Streams
# 16.05.2017: Design neu, Videoquellen nicht mehr auf der Webseite vorhanden - (Ladekette ähnlich ZDF-Mediathek)
# 22.05.2019: Design neu, Ladekette noch ähnlich ZDF-Mediathek, andere Parameter, Links + zusätzl. apiToken
# 21.01.2021 Nutzung build_Streamlists + build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
# 11.2024 Mitnutzung der Ladekette durch neue api-hbbtv-Funktionen
#
def SingleBeitrag(title, path, img_src, summ, dauer):
	PLog('SingleBeitrag: ' + title)
	PLog(dauer);PLog(summ);PLog(path)
	path_org = path
	
	Plot	 = title
	Plot_par = summ										# -> PlayVideo
	if Plot_par == '':			
		Plot_par = title
	tag_org = dauer
	thumb	= img_src; title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
			
	page, msg = get_page(path=path)									# 1. Basisdaten von Webpage holen
	if page == '':			
		msg1 = "SingleBeitrag1: Abruf fehlgeschlagen"
		msg2 = msg
		msg3=path
		PLog(msg1)
		MyDialog(msg1, msg2, msg3)
		return li	
	
	endDate = stringextract('list-desc">bis ', '</', page)			# Bsp. 12.09.2020
	pubDate = stringextract('publicationDate" content="', '"', page)# Bsp. 2020-06-19T08:21:30.448Z
	pubDate = time_translate(pubDate)
	if pubDate:
		pubDate = "Sendedatum: %s | " % pubDate
	PLog(pubDate)
	

	content = stringextract('window.zdfsite', 'tracking', page)  			
	content = stringextract('data-module="zdfplayer"', 'teaser-image=', page)  			
	appId	= stringextract('zdfplayer-id="', '"', content)
	apiToken= stringextract('apiToken": "', '"', content)
	profile_url= stringextract('content": "', '"', content)			# profile_url
	PLog(appId); PLog(profile_url); PLog("apiToken: " + apiToken); 
	
	if 	apiToken == '' or profile_url == '':
		if '<time datetime="' in page:
			termin = stringextract('<time datetime="', '"', page)
			termin = time_translate(termin)
			msg1 = "(noch) kein Video gefunden, Sendetermin: " + termin
		else:
			msg1 = "keine Videoquelle gefunden. Seite:\n" + path
			PLog(msg1)
			PLog(apiToken)		# zur Kontrolle
		MyDialog(msg1, '', '')
		return li	
	
	# 11.01.2021 Host nicht mehr akzeptiert - Austausch gegen Referer und
	#	Nutzung get_page (Modul util)
	headers = "{'Api-Auth': 'Bearer %s','Referer': 'https://www.3sat.de/'}" % apiToken 
	page,msg = get_page(path=profile_url, header=headers)
	
	if page == '':			
		msg1 = "SingleBeitrag2: Abruf fehlgeschlagen"
		msg2 = msg
		msg3=path
		PLog(msg1)
		MyDialog(msg1, msg2, msg3)
		return li	
	
	try:															# mainVideoContent mehrfach in page möglich
		objs = json.loads(page)["mainVideoContent"]
		PLog("mainVideoContent: " + str(objs)[:100])
		streams = objs["http://zdf.de/rels/target"]["streams"]["default"]
		PLog("streams: " + str(streams)[:100])
		videodat_url = streams["http://zdf.de/rels/streams/ptmd-template"]
			
	except Exception as exception:
		PLog("objs_error " + str(exception))

	player = "ngplayer_2_4"
	videodat_url = "https://api.3sat.de" + videodat_url
	videodat_url = videodat_url.replace('{playerId}', player)
	PLog("videodat_url: " + videodat_url)
	page,msg = get_page(path=videodat_url, header=headers)
	
	if page == '':			
		msg1 = "SingleBeitrag3: Abruf fehlgeschlagen"
		PLog(msg1); PLog(msg)
		msg2 = msg
	
	if page == '':													# Alternative mediathek statt 3sat in Url
		videodat_url = 'https://api.3sat.de/tmd/2/ngplayer_2_3/vod/ptmd/mediathek/' + video_ID
		page,msg = get_page(path=videodat_url, header=headers)
		page = str(page)											# <type 'tuple'> möglich
		PLog(page[:100])

	PLog(type(page)); 
	if 	"formitaeten" not in page:
		msg1 = "keine Videoquelle gefunden. Seite:\n" + path
		PLog(msg1)
		PLog(videodat_url)		# zur Kontrolle
		MyDialog(msg1, '', '')
		return li	
	PLog(page[:100])
	

	if page:
		formitaeten = blockextract('formitaeten', page)				# 4. einzelne Video-URL's ermitteln 
		geoblock =  stringextract('geoLocation',  '}', page) 
		geoblock =  stringextract('"value":"',  '"', geoblock).strip()
		PLog('geoblock: ' + geoblock);
		if 	geoblock == 'none':										# i.d.R. "none", sonst "de" - wie bei ARD verwenden
			geoblock = ' | ohne Geoblock'
		else:
			if geoblock == 'de':									# Info-Anhang für summary 
				geoblock = ' | Geoblock DE!'
			if geoblock == 'dach':									# Info-Anhang für summary 
				geoblock = ' | Geoblock DACH!'
			
	download_list = []
	if endDate:
		dauer = u"%s | %s [B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (dauer, pubDate, endDate)
	tagline = dauer + " " + geoblock
	Plot_par = tagline + "||||" + Plot_par	
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists + build_Streamlists_buttons (Haupt-PRG),
	#	einschl. Sofortstart
	#
	thumb=img_src; sub_path=''; scms_id=''
	HLS_List,MP4_List,HBBTV_List = build_Streamlists(li,title,thumb,geoblock,tagline,\
		sub_path,page,scms_id,ID="3sat",weburl=path_org)
					
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
# 3Sat - TV-Livestream mit EPG
#
def Live(name, epg=''):	
	PLog('Live: ' + name)
	title2 = name
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
	
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('3sat') in up_low(webtitle): 						# Sender mit Blank!
			m3u8link = href
			break
	if m3u8link == '':
		PLog('%s: Streamlink fehlt' % '3sat ')

	summary = u'automatische Auflösung';				
	title = 'Bandbreite und Auflösung automatisch'
	img	= R(ICON_TV3Sat)
	

	Plot	 = 'Live: ' + epg + '\n\n' + summary
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		PLog('Sofortstart: Live')
		PlayVideo(url=m3u8link, title='3Sat Live TV', thumb=img, Plot=Plot, live="true")
		return	
							
	Plot_par = Plot.replace('\n', '||')
	title=py2_encode(title); m3u8link=py2_encode(m3u8link); img=py2_encode(img);
	Plot_par=py2_encode(Plot_par);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': 'true'}" %\
		(quote_plus(m3u8link), quote_plus(title), quote_plus(img), quote_plus(Plot_par))
	addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
		mediatype='video', tagline=Plot) 		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-----------------------------
# 02.11.2023 akt. PRG-Hinweis aus EPG-Cache laden, sonst leer
#
def get_epg():									
	PLog('get_epg:')
	
	# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime,  
	#			5=summ, 6=vonbis, 7=today_human, 8=endtime:  
	rec = EPG.EPG(ID="3SAT", mode='OnlyNow')						# Daten holen - nur aktuelle Sendung
	sname=''; stime=''; summ=''; vonbis=''							# Fehler, ev. Sender EPG_ID nicht bekannt
	title=''; tag=''

	if rec:								
		sname=py2_encode(rec[3]); stime=py2_encode(rec[4]); 
		summ=py2_encode(rec[5]); vonbis=py2_encode(rec[6])
	else:
		return "", "", ""											# title, tag, summ	

	if sname:									# Sendungstitel
		title = str(sname).replace('JETZT:', 'LIVE')
		tag = u'Sendung: %s Uhr' % vonbis
	
	return title, tag, summ
	
####################################################################################################
# 3Sat - Bild-Galerien/-Serien
#	Übersichtsseiten - 3sat zeigt 12 Beiträge pro Seite
#		path für weitere Seiten: class="load-more-container"
# 04.08.2020 Webänderungen Titel, Subtitel
# 12/2024 search.php von hbbtv-api liefert keine Bilder - weiter
#	mit Webscraping.
#
def Bilder3sat(path=''):
	PLog('Bilder3sat:')
	if path == '':
		path="https://www.3sat.de/suche?q=bilderserie&synth=true&attrs=&page=1"
	
	page, msg = get_page(path)	
	if page == '':
		msg1 = 'Bilder3sat: Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')						# Home-Button

	content = blockextract('class="is-clickarea panel">', page)
	PLog("content: " + str(len(content)))
	if len(content) == 0:										
		msg1 = 'Bilder3sat: keine Bilder (mehr) gefunden.'
		MyDialog(msg1, '', '')
		return li
		
	for rec in content:
		if 'class="icon-gallery"' not in rec:					# Bildsymbol 
			continue
		
		img_set = stringextract('data-srcset="', '"', rec) # Format 16-9
		img_list= img_set.split(',')
		img = img_list[-1]										# 384x216
		PLog(img)
		img_src = 'https:' + stringextract('https:', ' ', img)
		if img == '':
			continue
		
		href = 'https://www.3sat.de' + stringextract('href="', '"', rec)
		
		
		headline = stringextract('clickarea-link js-teaser-title', 'class', rec)	# Klick-Titel
		headline = stringextract('">', '<', headline)
		PLog("headline; " + headline)
		if headline == '':
			 headline = stringextract('title="', '"', rec)
			
		pre_head = stringextract('class="a--preheadline level-4">', '</span>', rec)	# SubTitel oben, Bsp. Kultur
		pre_head = pre_head.replace('<span>', '').strip()	
		sub_head = stringextract('class="a--subheadline', 'class', rec)				# SubTitel unten, Bsp. Musik
		sub_head = stringextract('>', '<', sub_head)		
		
		title = repl_json_chars(headline)
		if pre_head and sub_head:
			tag = "%s | %s" % (pre_head, sub_head)		
		summ = stringextract('class="label">', '</', rec)				# Bsp. 5 Bilder
		
		PLog('Satz11:')
		PLog(img_src); PLog(title); PLog(tag);  		
			
		href=py2_encode(href); title=py2_encode(title);
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Bilder3satSingle", 
			fanart=img_src, thumb=img_src, fparams=fparams, tagline=tag, summary=summ)
			
	if 'class="load-more-container">' in page:
		href = stringextract('class="load-more-container">', '</div>', page)
		href = stringextract('href="', '"', href)
		if href:
			title = u'weitere Bilderserien laden'
			href = 'https://www.3sat.de' + href
			PLog('more_url: ' + href)
			href = decode_url(href); href=py2_encode(href); 	# ..&amp;attrs=&amp;page=2
			fparams="&fparams={'path': '%s'}" % (quote(href))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Bilder3sat", 
				fanart=R('zdf-bilderserien.png'), thumb=R(ICON_MEHR), tagline='Mehr...', fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern
		
####################################################################################################
# 23.09.2021 Umstellung Bildname aus Quelle statt "Bild_01" (eindeutiger beim
#	Nachladen) - wie ZDF_BildgalerieSingle.
#
def Bilder3satSingle(title, path):
	PLog('Bilder3satSingle:')
	
	page, msg = get_page(path)	
	if page == '':
		msg1 = 'Bilder3satSingle: Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')						# Home-Button

	content = blockextract('class="img-container">', page)
	PLog("content: " + str(len(content)))
	if len(content) == 0:										
		msg1 = 'Bilder3satSingle: keine Bilder gefunden.'
		msg2 = title
		MyDialog(msg1, msg2, '')
		return li
	
	DelEmptyDirs(SLIDESTORE)								# leere Verz. löschen							
	fname = make_filenames(title)			# Ordnername: Titel 
	fpath = os.path.join(SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2)
			MyDialog(msg1, msg2, '')
			return li	
	
	image=0; background=False; path_url_list=[]; text_list=[]
	for rec in content:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		img_src = img_src.replace('384x216', '1280x720')			
		title 	= stringextract('level-3   ">', '</h2>', rec) 
		stitle 	= stringextract('level-2">', '</span>', rec)
		title=cleanhtml(title); title=mystrip(title);  
		stitle=cleanhtml(stitle); stitle=mystrip(stitle.strip()); 
		
		descr 	= stringextract('paragraph-large ">', '</p', rec) 	# Bildtext
		urh	= stringextract('teaser-info is-small">', '</dd', rec)	# Urheber
		urh=mystrip(urh.strip()); 
		urh	= urh.replace("amp;", "")
		
		tag = "%s | %s" % (stitle, title)
		summ = "%s\n%s" % (descr, urh)
		
		PLog('Satz12:')
		PLog(img_src); PLog(tag[:60]); PLog(summ[:60]);	
		tag=repl_json_chars(tag) 
		title=repl_json_chars(title); summ=repl_json_chars(summ); 		
			
		#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
		#	nicht zum Imageformat passen
		#pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
		pic_name 	= img_src.split('/')[-1]			# Bildname aus Quelle
		if '?' in pic_name:								# Bsp.: ~2400x1350?cb=1631630217812
			pic_name = pic_name.split('?')[0]
		local_path 	= "%s/%s.jpg" % (fpath, pic_name)
		title = "Bild %03d: %s" % (image+1, pic_name)	# Numerierung
		PLog("Bildtitel: " + title)
		
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		if os.path.isfile(local_path) == False:			# schon vorhanden?
			# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Bild-Url, 
			#	Zieldatei_kompletter_Pfad|Bild-Url ..
			path_url_list.append('%s|%s' % (local_path, img_src))

			if SETTINGS.getSetting('pref_watermarks') == 'true':
				lable=''
				txt = "%s\n%s\n%s\n%s\n%s\n" % (fname,title,lable,tag,summ)
				text_list.append(txt)	
			background	= True											
								
		title=repl_json_chars(title); summ=repl_json_chars(summ)
		PLog('neu:');PLog(title);PLog(img_src);PLog(thumb);PLog(summ[0:40]);
		if thumb:	
			local_path=py2_encode(local_path);
			fparams="&fparams={'path': '%s', 'single': 'True'}" % quote(local_path)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_SlideShow", 
				fanart=thumb, thumb=local_path, fparams=fparams, summary=summ, tagline=tag)

		image += 1
			
	if background and len(path_url_list) > 0:				# Thread-Call mit Url- und Textliste
		PLog("background: " + str(background))
		from threading import Thread						# thread_getpic
		folder = fname 
		background_thread = Thread(target=thread_getpic,
			args=(path_url_list, text_list, folder))
		background_thread.start()

	PLog("image: " + str(image))
	if image > 0:	
		fpath=py2_encode(fpath);	
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
				
		lable = u"Alle Bilder löschen"						# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern

####################################################################################################
#	Hilfsfunktionen
#----------------------------------------------------------------  
# 1. Format timecode '01:30' oder '00:30', Rest (Min, min o.ä.) wird abgeschnitten
# 2. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
def HourToMinutes(timecode):	
	if timecode.find('P0Y0M0D') >= 0:			# 1. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
		d = re.search('T([0-9]{1,2})H([0-9]{1,2})M([0-9]{1,2}).([0-9]{1,3})S', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
	else:
		timecode =  timecode[0:5]
		if timecode.find(':') < 0:
			return timecode
		t =  timecode.split(':')
		hours = int(t[0])
		minutes = int(t[1])
	
	if hours > 0:
		minutes = (hours * 60) + minutes
	
	return str(minutes)

#----------------------------------------------------------------  
# 11.01.2021 Nutzung get_page (Modul util)
# nur für Anford. Videodaten mittels apiToken 
# def get_page3sat(path, apiToken):
#----------------------------------------------------------------  



