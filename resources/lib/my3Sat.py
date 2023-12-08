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
# 	
################################################################################
# 	<nr>14</nr>										# Numerierung für Einzelupdate
#	Stand: 08.12.2023

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
ICON_TV3Sat 			= 'tv-3sat.png'
ICON_MAIN_ARD 			= 'ard-mediathek.png'			
ICON_MAIN_TVLIVE 		= 'tv-livestreams.png'		
			
ICON_SEARCH 			= 'ard-suche.png'						
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_SPEAKER 			= "icon-speaker.png"
ICON_MEHR 				= "icon-mehr.png"

DreiSat_BASE 	= 'https://www.3sat.de'
DreiSat_AZ 		= "https://www.3sat.de/sendungen-a-z"
DreiSat_Verpasst= "https://www.3sat.de/programm?airtimeDate=%s"   		# Format %s: 2019-05-22 (Y-m-d) 
DreiSat_Suche	= "https://www.3sat.de/suche?q=%s&synth=true&attrs=&contentTypes=episode" 	# ganze Sendungen

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

ARDStartCacheTime = 300						# 5 Min.	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('my3Sat_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")

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
	fparams="&fparams={'first': 'True','path': ''}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
		thumb=R('zdf-suche.png'), fparams=fparams)
			
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
	path = DreiSat_BASE							
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
	path = 'https://www.3sat.de/themen'								
	summ = "Thementage, Themenwochen und 3sat-Themen"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'name': '%s', 'path': '%s', 'themen': 'ja'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubriken", 
		fanart=R('3sat.png'), thumb=R('zdf-themen.png'), summary=summ, fparams=fparams)
		

	title = "Rubriken"
	path = 'https://www.3sat.de/themen'								# auch Leitseite
	summ = "Dokumentation, Film, Gesellschaft, Kabarett, Kultur, Wissen"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubriken", 
		fanart=R('3sat.png'), thumb=R('zdf-rubriken.png'), summary=summ, fparams=fparams)

	title = 'Bildgalerien 3sat'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Bilder3sat",
		fanart=R('3sat.png'), thumb=R('zdf-bilderserien.png'), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		 		
####################################################################################################
# Hinweis: wir suchen in 3Sat_XML_FULL = alle Mediathekinhalte
#	Die Sucheingabe kann mehrere Wörter enthalten, getrennt durch Blanks (ODER-Suche) 
#	Gesucht wird in Titel + Beschreibung. Mediathek listet Suchergebnisse tageweise
# 
# 23.07.2022 nach Sofortstart: return ersetzt durch Aufruf Main_3Sat wie ARDSearchnew
#
def Search(first, path, query=''):
	PLog('Search:'); PLog(first);	
	if 	query == '':	
		query = get_query(channel='ZDF')
		
	query = py2_decode(query)
	name = 'Suchergebnis zu: ' + unquote(query)
	PLog("name: " + name)
	if  unquote(query) == None or unquote(query).strip() == '':
		Main_3Sat()									# statt return - s.o.
	
		
	if first == 'True':								# query nur 1. Aufruf injizieren,  Anpass. s. 'Mehr' 
		path =  DreiSat_Suche % quote(py2_encode(query))
		path = path + "&page=1"
	PLog(path); 										# Bsp. https://www.3sat.de/suche?q=brexit&synth=true&attrs=&page=2
	page, msg = get_page(path=path, do_safe=False)		# ohne quote in get_page, dto. in Sendereihe_Sendungen	
	if page == '':			
		msg1 = "Fehler in Search"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return
		
	rubriken =  blockextract('<picture class="">', page)	
	cnt = stringextract('class="search-number">', '<', page) # Anzahl Treffer
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button

	query_unqoute = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
	if len(rubriken) == 0 or cnt == '':						# kein Treffer
		msg1 = 'Leider kein Treffer (mehr) zu '  + unquote(query)
		PLog(msg1)
		MyDialog(msg1, '', '')
		return	
	
	new_title = "%s Treffer zu >%s<" % (cnt, query)
	li = Sendereihe_Sendungen(li, path=path, title=new_title)
	
	# auf mehr prüfen:
	if test_More(page=page):						# Test auf weitere Seiten (class="loader)
		li = xbmcgui.ListItem()						# Kontext-Doppel verhindern
		search_cnt = stringextract('class="search-number">', '<', page)
		page_max = 12
		
		plist = path.split('&page=')
		pagenr = int(plist[-1])
		new_path = plist[0] + '&page=' + str(pagenr + 1)
		title = "Mehr zu: %s" %  unquote(query)
		tag = "Suchergebnisse gesamt: %s | Anzeige pro Seite: %d" % (search_cnt, page_max)
		summ = 'Weiter zu Seite %s' % (pagenr + 1)
		PLog(new_path)
		
		new_path=py2_encode(new_path); query=py2_encode(query);
		fparams="&fparams={'first': 'False', 'path': '%s', 'query': '%s'}" % (quote(new_path), 
			quote(query))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
			thumb=R(ICON_MEHR), tagline=tag, summary=summ, fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#------------ 
# A-Z Liste der Buchstaben (mit Markierung 'ohne Beiträge')
def SendungenAZlist(name, path):				# 
	PLog('SendungenAZlist: ' + name)
	DreiSat_AZ 		= "https://www.3sat.de/sendungen-a-z"			# geht hier nach epg verloren	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button

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
	
	for rec in content:
		title	= stringextract('title="', '"', rec)
		href	= stringextract('href="', '"', rec)
		href	= DreiSat_BASE + href
		PLog(title)
		if 'link is-disabled' in rec:							# Button inaktiv
			letter = stringextract('true">', '<', rec)
			title = "[COLOR grey]Sendungen mit %s[/COLOR]" % letter
			fparams="&fparams={}"	 
			addDir(li=li, label=title, action="dirList", dirID="dummy", 
				fanart=R('3sat.png'), thumb=R('zdf-sendungen-az.png'), fparams=fparams)			
		else:
			title=py2_encode(title); href=py2_encode(href);
			fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(href))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZ", 
				fanart=R('3sat.png'), thumb=R('Dir-folder.png'), fparams=fparams)			
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------ 
# A-Z Liste der Beiträge
#	-> Sendereihe_Sendungen -> get_zdfplayer_content
# 04.08.2020 Anpassungen an Webänderungen (Rubrik, Titel)
# 16.02.2021 dto (Titel)
#
def SendungenAZ(name, path): 
	PLog('SendungenAZ: ' + name)

	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in SendungenAZ"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return li	
		
	content = blockextract('<picture class="">', page)
	PLog(len(content))
	
	for rec in content:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		rubrik 	= stringextract('a--preheadline level-4">', '<span class', rec)
		rubrik 	= stringextract('<span>', '</span>', rubrik)
		sub_rubrik = stringextract('ellipsis" >', '<', rec)
		tlink	= stringextract('teaser-title-link', "data-track=", rec)
		title	= stringextract('title="', '"', tlink)
		if "is-lowercase" in title:
			title	= stringextract('case">', '</span>', rec)
		href	= stringextract('href="', '"', tlink)
		href	= DreiSat_BASE + href
		descr	= stringextract('clickarea-link" >', '<', rec)
		tag 	= rubrik
		if sub_rubrik:
			tag = "%s | %s" % (tag, sub_rubrik)
		tag = cleanhtml(tag)

		title = repl_json_chars(title); descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
		
		PLog('Satz1:')
		PLog(img_src); PLog(rubrik); PLog(title);  PLog(href); PLog(descr);
			
		# Aufruf Sendereihe_Sendungen hier ohne Listitem					
		title=py2_encode(title); href=py2_encode(href);  img_src=py2_encode(img_src);
		fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
			 quote(href), quote(img_src))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
			fanart=R('3sat.png'), thumb=img_src, summary=descr, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------
# 25.05.2019 more-Links nicht mehr verfügbar (javascript-generiert) -
#	more-Links müssem vom Aufrufer (z.B. Search) generiert werden.
def test_More(page):						# Test auf weitere Seiten
	PLog('test_More:')
	if page.find('class="loader"') > 0:		# 2. Seite (z.Z. Seite 1: 0-9, A-K, Seite 2: Rest)
		PLog('True')
		return True	
	else:
		PLog('False')
		return False	
	
	
#------------
def Verpasst(title):	# je 1 Tag - passend zum Webdesign
	PLog('Verpasst:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
		
	wlist = list(range(0,30))					# Abstand 1 Tage
	now = datetime.datetime.now()
	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")		# Formate s. man strftime (3)
		SendDate = rdate.strftime("%Y-%m-%d")	# 3Sat-Format 2019-05-22 (Y-m-d)  	
		iWeekday =  rdate.strftime("%A")
		punkte = '.'
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)
		iPath = DreiSat_Verpasst % SendDate

		# PLog(iPath); PLog(iDate); PLog(iWeekday);
		title =	"%s | %s" % (iDate, iWeekday)
		title =	iDate + ' | ' + iWeekday
		
		PLog('Satz2:')	
		PLog(SendDate); PLog(title); 
		title=py2_encode(title); 
		fparams="&fparams={'SendDate': '%s', 'title': '%s'}" % (SendDate, quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenDatum", 
			fanart=R('3sat.png'), thumb=R(ICON_DIR_FOLDER), fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------

# Liste Sendungen gewählter Tag
# 04.08.2020 Webänderung Sendung (label)
# 06.02.2022 dto
def SendungenDatum(SendDate, title):	
	PLog('SendungenDatum: ' + SendDate)
	
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
		
	path =  DreiSat_Verpasst % SendDate
	page, msg = get_page(path=path)	
	
	content = blockextract('<picture class="">', page)
	PLog(len(content))
			
	if len(content) == 0:			
		msg1 = u'leider kein Treffer im ausgewählten Zeitraum'
		PLog(msg1)
		MyDialog(msg1, '', '')
		return li	
		
	msg1 = "%s.%s.%s" % (SendDate[8:10], SendDate[5:7], SendDate[0:4])
	msg2 = "3sat"
	icon = R('zdf-sendung-verpasst.png')
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)

	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	for rec in content:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		href	= stringextract('href="', '"', rec)
		if href == '' or '#skiplinks' in href:
			continue
		href	= DreiSat_BASE + href
		sendung	= stringextract('-headline', 'class', rec)
		sendung = stringextract('>', '<', sendung)
		descr	= stringextract('teaser-epg-text">', '</p>', rec)		# mehrere Zeilen
		PLog(descr)
		descr	= cleanhtml(descr); 
		zeit	= stringextract('class="time">', '</', rec)
		dauer	= stringextract('class="label">', '</', rec)
		# enddate leer bei Verpasst, anders als üblich (s. get_teaserElement)
		#enddate	= stringextract('-end-date="', '"', rec)	
		#enddate = time_translate(enddate, add_hour=0, day_warn=True)
		#if dauer and enddate:
		#	dauer = "%s | [B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (dauer, enddate)			 
		
		sendung = u"[COLOR blue]%s[/COLOR] | %s" % (zeit, sendung)
		tagline = title_org +  ' | ' + zeit
		if dauer:
			tagline = tagline + ' | ' + dauer

		if SETTINGS.getSetting('pref_load_summary') == 'true':			# Inhaltstext im Voraus laden?
			pass														# o. Mehrwert zu descr												

		title = repl_json_chars(title);
		sendung = repl_json_chars(sendung)
		descr	= unescape(descr);  
		descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	

		PLog('Satz3:')
		PLog(img_src);  PLog(href); PLog(sendung); PLog(tagline); PLog(descr); PLog(dauer);
			 
		sendung=py2_encode(sendung); href=py2_encode(href);  img_src=py2_encode(img_src);
		descr_par=py2_encode(descr_par); dauer=py2_encode(dauer)
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
			(quote(sendung), quote(href), quote(img_src), quote(descr_par), quote(dauer))
		addDir(li=li, label=sendung, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, summary=descr, tagline=tagline, fparams=fparams, mediatype=mediatype)
			 					 	
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
# Aufrufer: Main_3Sat, Start
#	Startseite www.3sat.de (html + lazyload-Inhalte)
#	1. Durchlauf mit Stage und Rubriken der Starttseite
# 	2. Durchlauf: Rubrik-Ausschnitt erzeugen -> get_lazyload (die 
#			meisten oder -> Rubrik_Single (zdfplayer-Inhalte)
# 04.08.2020 Anpassungen an Webänderungen (Muster red is-uppercase)
# 16.02.2021 dto (headline)
#
def Start(name, path, rubrik=''):
	PLog('3satStart:')
	my3satCacheTime =  600					# 10 Min.: 10*60
	PLog("rubrik: " + rubrik)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')				# Home-Button
	
	page = Dict("load", '3satStart', CacheTime=my3satCacheTime)	
	if page == False:								# nicht vorhanden oder zu alt
		page, msg = get_page(path)
		if page == '':						
			msg1 = 'Fehler in Start: %s' % name
			msg2 = msg
			msg2 = u"Seite weder im Cache noch im Web verfügbar"
			MyDialog(msg1, msg2, '')
			return li
		else:
			Dict("store", '3satStart', page) # Seite -> Cache: aktualisieren				
	PLog(len(page))
	
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	if rubrik == '':								# 1. Durchlauf: Stage + Rubrik-Liste
		stage_home = stringextract('data-module="stage-home"', '</section', page)
		content =  blockextract('class="artdirect">', stage_home)
		PLog(len(content))
		i=1
		for rec in content:
			multi = False
			img_src = stringextract('data-srcset="', ' ', rec)	
			title 	= stringextract('title="', '"', rec)	
			title	= "Top %d: %s" % (i, title)
			title 	= unescape(title); title = repl_json_chars(title); 
			i=i+1
			href	= stringextract('href="', '"', rec)
			if href.startswith('http') == False:
				href	= DreiSat_BASE + href
				
			dauer 	= stringextract('class="label">', '</', rec)# 2 min
			endDate = stringextract('-end-date="', '"', rec)	# 2020-07-15T04:00:00.000Z
			endDate = time_translate(endDate, day_warn=True)
			
			tag = dauer
			if endDate:
				tag		= u"%s | [B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (dauer, endDate)
			PLog(tag)
			descr	= stringextract('paragraph-large ">', '</', rec)
			if descr == '':
				descr	= stringextract('text show-for-large">', '</', rec)
			descr = unescape(descr); descr = mystrip(descr); descr = repl_json_chars(descr)
			descr_par =	mystrip(descr); descr_par =	descr_par.replace('\n', '||')	
			
			if dauer == '':
				multi = True
				tag = "Folgeseiten"; # descr = ''		# vorh. descr beibehalten
				
			PLog('Satz1:')
			PLog(multi); PLog(title); PLog(href); PLog(tag); PLog(descr); PLog(descr_par);
			title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);
			descr_par=py2_encode(descr_par); 
			if multi:							
				fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
					 quote(href), quote(img_src))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
					fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, fparams=fparams)
			else:
				fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
					(quote(title), quote(href), quote(img_src), quote(descr_par), dauer)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
					fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, mediatype=mediatype,
					fparams=fparams)
				

		if 'class="m--teaser-topic-' in page:		# herausgestellte Themenseiten
			items =  blockextract('class="m--teaser-topic-', page, '</article>')
			PLog(len(items))
			for rec in items:
				img_src = stringextract('data-srcset="', ' ', rec)	
				title 	= stringextract('title="', '"', rec)
				href	= stringextract('href="', '"', rec)
				if href.startswith('http') == False:
					href	= DreiSat_BASE + href
				anz 	= stringextract('class="info">', '</', rec)	# Anzahl Beiträge
				tag		= u"[B]%s[/B] Beiträge" % anz
				
				subhead = stringextract('subheadline level-8', "<div", rec)
				descr	= stringextract('" >', '</', subhead)		# show-for-large" >
				title 	= unescape(title)
				descr 	= unescape(descr); descr = mystrip(descr); descr = repl_json_chars(descr)
				
				PLog('Satz2:')
				PLog(title); PLog(href); PLog(tag); PLog(descr);
				title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);
				fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
					 quote(href), quote(img_src))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
					fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, fparams=fparams)

		# todo: kurzzeitige neue Formate auswerten, z.B. <section class="o--cluster-brand"> (Top Sendungen)
		#	
													# restl. Rubriken der Leitseite listen													
		items = blockextract('--red is-uppercase', page)
		PLog(len(items))
		img_src = R('Dir-folder.png')				# alles lazyload-Beiträge ohne Bilder + hrefs
		for rec in items:
			title	= stringextract('">', '</h2', rec)
			title = cleanhtml(title)				# z.B.: 3sat</span>-Tipps
			if u'Das könnte Dich' in title:			# leer (java-script)
				continue
			if u'Alle löschen' in title:			# Merkliste 3sat
				continue
			if u'livestream &' in title:			# ausgelagert
				continue
			title = repl_json_chars(title)	
				
			# Bilder für 1. Rubrik-Beitrag laden (lazyload-, carousel- + andere Sätze möglich):	
			if SETTINGS.getSetting('pref_load_summary') == 'true': # hier nur Bild verwenden
				if 'is-medium lazyload' in rec:
					rec	= stringextract('class="b-cluster-teaser', '</div', rec)
					d1,d2,d3,d4,img_src,d5,d6,d7 = get_teaserElement(unescape(rec))
				if 'zdfplayer-teaser-image=' in rec:
					img_src = stringextract('&quot;http', '&quot;', rec)
					img_src = img_src.replace('\\/','/')
					img_src = "https" + img_src
				
			PLog('Satz15:')
			path = DreiSat_BASE
			PLog(title); PLog(path); PLog(img_src); 
			title=py2_encode(title); path=py2_encode(path); 
			fparams="&fparams={'name': '%s', 'path': '%s', 'rubrik': '%s'}" %\
				(quote(title), quote(path), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Start", 
				fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

	else:											# 2. Durchlauf: Rubrik-Ausschnitt auswerten
		items =  blockextract('--red is-uppercase', page)
		PLog(len(items))
		for rec in items:						
			title = stringextract('">', '</h2', rec)
			title = cleanhtml(title)				# z.B.: 3sat</span>-Tipps
			title 	= repl_json_chars(title);
			rubrik=py2_encode(rubrik); title=py2_encode(title);
			# PLog("title: %s, rubrik: %s" % (title, rubrik))
			if rubrik in title:						# geklickte Rubrik (json-bereinigt) suchen
				PLog("gefunden: rubrik")
				if 'ivestream' in title:			# Buttons Livestream + Verpasst
					epg = get_epg()
					if epg:
						epg = 'Jetzt in 3sat: ' + epg
					title = '3Sat-Livestream'
					title=py2_encode(title); epg=py2_encode(epg);
					fparams="&fparams={'name': '%s', 'epg': '%s'}" % (quote(title), quote(epg))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Live", 
						fanart=R('3sat.png'), thumb=R(ICON_MAIN_TVLIVE), tagline=epg, fparams=fparams)
						
					title = 'Verpasst'
					summ = 'aktuelle Beiträge eines Monats - nach Datum geordnet'
					fparams="&fparams={'title': 'Sendung verpasst'}"
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Verpasst", 
						fanart=R('3sat.png'), thumb=R('zdf-sendung-verpasst.png'), summary=summ, fparams=fparams)
					break	

				else:								# alle  übrigen Rubriken auswerten
					if 'is-medium lazyload' in rec:	# lazyload-Beiträge (die meisten)
						li, cnt = get_lazyload(li=li, page=rec, ref_path=path)
					elif 'video-carousel-item">' in rec:
						 get_video_carousel(li, rec)
					else: 							# -> Rubrik_Single als 2. Durchlauf mit thema, nochmal laden
						Rubrik_Single(name=title, path=path, thema=title, ID='Start')
					break
		
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------
# Aufrufer: Main_3Sat
#	Liste der 3sat-Rubriken (aus Dropdownmenü Webseite) 
#	Liste der 3sat-Themen (themen=ja) von https://www.3sat.de/themen	
# 	Liste der 3sat-Rubriken: 	1. Lauf: dropdown-link Themen-Seite, 	
#								2. Lauf: Auswertung wie Themen
# 	-> Rubrik_Single
# 27.10.2021 Blockbildung grid-container statt picture class 
#
def Rubriken(name, path, themen=''):
	PLog('Rubriken:')
	PLog(themen)
	path_org=path
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')							# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in Rubriken"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return li	
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Kennz. Video für Sofortstart 
		mediatype='video'
		
	if themen:											# Themen od. einz. Rubrik (name) 
		pos = page.find('class="o--footer">')
		if pos > 0:
			page = page[:pos]							# Fuß abschneiden
		
		items = get_container(page)						# Blöcke bilden
		PLog(len(items))
		skip_list=[]; dur=''
		PLog("Mark0")
		for  rec in items:	
			PLog(len(rec))
			PLog(rec[:100])
			title = stringextract('-headline', 'class=', rec) 
			title = get_title(title)				
			if title == '':
				continue
			title_org = title							# unbehandelt für Abgleich
			PLog("title_org: " + title_org)	
			title = cleanhtml(title); title = mystrip(title);  
			title = repl_json_chars(title) 			
			PLog("title: " + title)	
			if 'TV-Sendetermine' in title:
				continue
																									
			img_src =  stringextract('data-srcset="', ' ', rec)
			if img_src == '':
				img_src = R('Dir-folder.png')
			img_txt =  stringextract('alt="', '"', rec)
			img_txt = repl_json_chars(img_txt); img_txt = unescape(img_txt)
				
			descr =  stringextract('subheadline level-8 " >', '</', rec)
			if descr == '':
				descr =  stringextract('subheadline level-8 " >', '</p>', rec)
			descr = cleanhtml(descr); descr = unescape(descr)
			descr = repl_json_chars(descr) 
			
			 
			thema=''; single=False; dur=''
			if 'grid-container js-title"' in rec:			# lazyload-Beiträge ohne Bilder + hrefs
				PLog('grid-container js-title"')
				img_src = R('Dir-folder.png')
				href = path_org
				thema = title_org
			else:											# Einzelbeiträge filtern
				if 'data-module="zdfplayer"' in rec:		# zdfplayer in Carousel-Item u.a.
					videoinfos = stringextract("video-infos='{", '}', rec)
					videoinfos = unescape(videoinfos)
					img_src = stringextract('&quot;http', '&quot;', rec)
					img_src = img_src.replace('\\/','/')
					img_src = "http" + img_src				# s von http bereits enth.
					if img_src in skip_list:
						continue
					skip_list.append(img_src)
					
					href	= stringextract('embed_content": "', '"', rec) # zusätzl /zdf/ enth.
					href 	= DreiSat_BASE + href + ".html"
					skip_list.append(href)
					dur 	= stringextract('duration": "', '",', videoinfos)
				else:	
					try:										
						dur = re.search(u'>(.*?) min</span>', rec).group(1)		# 1 h 56 min
						dur = dur + " min"
					except Exception as exception:
						PLog(str(exception))

			href =  stringextract('href="', '"', rec)
			if  "#skip-cluster" in href:
				href = href.split("#skip-cluster")[0]
			PLog("href: " + href)
			if href == '':
				href = path_org
			else:
				if href.startswith('http') == False:
					href	= DreiSat_BASE + href
			#if href in skip_list:
			#	continue
			#skip_list.append(href)
				
			if dur:			
				PLog('Satz4:')
				tag = dur
				if img_txt:
					tag = "%s\nBild: %s" % (tag, img_txt)
					
				title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);
				path_org=py2_encode(path_org)							
				fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
					(quote(title), quote(href), quote(img_src), quote(descr), quote(dur))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
					fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)
				single=True
	
			#---------------------									
											
			tag = "Folgeseiten"	
			if img_txt:
				tag = "%s\nBild: %s" % (tag, img_txt)	
				
			PLog('Satz5:')
			PLog(title); PLog(href); PLog(img_src);  PLog(dur); PLog(single);
			title=py2_encode(title); thema=py2_encode(thema); href=py2_encode(href);  
			img_src=py2_encode(img_src);
			
			if single == False:
				if href == path_org:						
					fparams="&fparams={'name': '%s', 'path': '%s', 'thema': '%s'}" % (quote(title), 
						quote(href), quote(thema))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubrik_Single", 
						fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)
				else:														# Cluster auf neuer Seite suchen 
					fparams="&fparams={'name': '%s', 'path': '%s', 'themen': '%s'}" % (quote(title), 
						quote(href), quote(title))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubriken", 
						fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)
		
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# Ende Themen
		return
		
	else:													# Rubriken 
		rubriken =  blockextract('class="dropdown-link js-rb-click js-track-click"', page)
		PLog(len(rubriken))
		
		i=0; rubrik=[]; 							
		for rec in rubriken:								# Rubriken sammeln	
			title	= stringextract('title="', '"', rec)
			if 'A-Z' in title:
				continue
			href	= DreiSat_BASE + stringextract('href="', '"', rec)
			line 	= title + "|" + href	
			rubrik.append(line)
			i=i+1
	
	rubrik.sort()											# Rubriken sortieren
	img_src = R('Dir-folder.png')
	PLog('Satz13:')
	for rec in rubrik:
		title, href = rec.split('|')
		PLog(title); PLog(href); 
		title=py2_encode(title); href=py2_encode(href); 
		fparams="&fparams={'name': '%s', 'path': '%s', 'themen': '%s'}" % (quote(title), quote(href), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubriken", 
			fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------
# Aufrufer: Rubrik - Auswertung eines Rubrik-Clusters, z.B. von www.3sat.de/film
#			Themen - Auswertung eines Themen-Clusters von www.3sat.de/themen
# 04.08.2020 Anpassungen an Webänderungen (Rubrik, Titel)
# 27.10.2021 vereinheitlichte Auswertung Rubriken und Themen, Auswertung
#	mögliche Carousel-Serie + mögl. zdfplayer für gesamte Seite
# 
def Rubrik_Single(name, path, thema='', ID=''):	
	PLog('Rubrik_Single: '+ name)
	thema = thema.replace('*', '"')
	PLog("thema: " + thema)	
	path_org=path
	
	li = xbmcgui.ListItem()
	if ID != 'Start':
		li = home(li, ID='3Sat')								# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in Rubrik_Single"
		msg2 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, '')
		return li	
	pos = page.find('class="o--footer">')
	if pos > 0:
		page = page[:pos]										# Fuß abschneiden
		
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Kennz. Video für Sofortstart 
		mediatype='video'

	# Blöcke:
	items = get_container(page)	
	
	if thema:
		found=False
		PLog('Suche_Cluster: %s' % thema)						# Cluster thema auf Seite suche
		for item in items:
			#PLog(item[:100])
			head = stringextract('-headline', 'class', item)
			pos = item.find(u'">%s<' % thema)
			if pos > 0:
				PLog('Cluster gefunden: %s' % thema)
				PLog("pos: %d" % pos)

				if 'TV-SENDETERMINE' in name:
					msg1 = 'TV-SENDETERMINE'
					msg2 = u'Bitte das Menü Verpasst verwenden'
					MyDialog(msg1, msg2, '')
					xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
					return

				page = item[4:]						# hinter Blockstart
				# PLog(item[:600])
				pos2 = page.find('grid-container"')		# begrenzen (nächster Container)
				if pos2 > 0:
					page = page[:pos2]
				PLog("cluster_len: %d" % len(page))
					
				PLog("Clusterstart: " + page[:100]); PLog("Clusterend: " + page[-100:]);
				found=True
				break
		if found == False:
			PLog('Cluster nicht gefunden: %s' % thema)
			return
	else:
		PLog('ohne_Cluster: %s' % name)
		
	pos = page.find('class="o--footer">')
	if pos > 0:
		page = page[:pos]							# Fuß abschneiden
	title=name
	

	#--------------------------------------------			# Suche zdfplayer-/lazyload-Beiträge:			
	PLog("Mark0")
	skip_list=[]
	if 'data-module="zdfplayer"' in page:		
		PLog("zdfplayer")
		skip_list = get_zdfplayer_content(li, page)
			
	skip_lazyload=''										# -> Sendereihe_Sendungen		
	
	if 'is-medium lazyload' in page:						# 1 od. mehrere (grid-container) lazyload-Beiträge		
		PLog('lazyload_container: %s' % thema)				# Ausgabe hier
		pos = page.find("</article>")						# lazyload-Ende
		if pos > 0:
			page = page[:pos]
		get_lazyload(li, page, ref_path=path_org)

	#--------------------------------------------			# Suche weiterere Cluster:			
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Kennz. Video für Sofortstart 
		mediatype='video'

	items =  blockextract('<picture class="">', page)		# fehlt z.B. in Titelthema
	PLog(len(items))
	if len(items) == 0: 
		items =  items + blockextract('<img class=', page)
	PLog(len(items))
	for rec in items:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		title	= stringextract('clickarea-link">', '</p>', rec)
		if title == '':
			title	= stringextract("js-teaser-title",'</h3>', rec)
			title	= stringextract('data-module="headline">', '</p>', title)
		if title == '':
			title	= stringextract('headline">','</h3>', rec)
		href	= stringextract('href="', '"', rec)
		if href.startswith('http') == False:
			href	= DreiSat_BASE + href
		if '/einstellungen':
			continue
			
		descr	= stringextract('clickarea-link" >', '<', rec)
		if descr == '':
			descr	= stringextract('paragraph-large ">', '<', rec)
 		 
		try:
			dur = re.search(u'>(.*?) min</span>', rec).group(1)		# 1 h 56 min
			dur = dur + " min"
		except:
			dur=''
		
		title = repl_json_chars(title); descr = repl_json_chars(descr);	 					
		PLog('Satz6:')
		PLog(img_src); PLog(title);  PLog(href); PLog(descr); PLog(dur);
		title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);
		path_org=py2_encode(path_org)							
		thema=title; 
		
		# Rekursion bei Cluster möglich (ohne Dauer, href wird ignoriert) 
		#	nehmen wir hierin Kauf:
		if dur == '':								# Auswertung als Cluster auf Quellseite
			tag = "Folgeseiten"	
			fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
				 quote(href), quote(img_src))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
				fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, fparams=fparams)
		else:										# Einzelsendung -> SingleBeitrag
			tag = dur
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
				(quote(title), quote(href), quote(img_src), quote(dur))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", 
				fanart=R('3sat.png'), thumb=img_src, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)
		
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#------------
# Aufrufer: SendungenAZ mit path aber ohne Listitem, Rubrik_Single + 
#	Rubriken (Themen) mit page (Seitenausschnitt)
#	Search + Rubrik_Single jew. mit Listitem
#	rekursiv möglich - s. is-clickarea-action (keine Rubriken, aber
#		weiterführender Link.
#
# Achtung: hier wird (nochmal) auf video-carousel-item	+ o--stage-brand
#	geprüft - page ev. vorher begrenzen.
#																# Liste der Einzelsendungen zu Sendereihen
def Sendereihe_Sendungen(li, path, title, img='', page='', skip_lazyload='', skip_zdfplayer='', skip_list=[]):		
	PLog('Sendereihe_Sendungen: ' + path)
	PLog(title)
	PLog(skip_zdfplayer);
	PLog(len(page))
	title_org = title
	got_page = False
	if page:
		got_page = True
	
	ret = False									# Default Return  o. endOfDirectory
	if li:										# direkter Aufruf
		ret = True
	else:
		li = xbmcgui.ListItem()
		li = home(li, ID='3Sat')										# Home-Button
	
	if page == '':								# Seitenausschnitt vom Aufrufer?
		page, msg = get_page(path=path, do_safe=False)	
	if 'byte' in str(type(page)):				# Bsp.: https://w1.grimme-online-award.de/goa/voting/ext_voting.pl
		PLog("byte_page_detect: " + path)		#	-> str gegen codec-error (Bsp. Perl-Seite, s.o.)
		page=str(page)		
	pos = page.find('class="o--footer">')
	PLog("Mark1")		
	if pos > 0:
		page = page[:pos]							# Fuß abschneiden
	PLog(len(page))

	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
			
	skip_list=[]				
	# 1. Strukturen am Seitenanfang (1 Video doppelt möglich):	
	if 'data-module="zdfplayer"' in page:			# Bsp. www.3sat.de/kultur/kulturzeit
		PLog('data-module="zdfplayer"')
		if skip_zdfplayer == '':					# ausgewertet in Rubrik_Single?
			PLog(len(page))
			skip_list = get_zdfplayer_content(li, page)
			skip_zdfplayer=True
		
	if 'o--stage-brand' in page:		# Bsp. www.3sat.de/wissen/netz-natur (1 Beitrag)
		# "o--stage-brand-Beiträge auswerten, html-Format, Seitenkopf
		PLog('Struktur o--stage-brand')
		if skip_zdfplayer == '':					# ausgewertet in Rubrik_Single?
			content =   stringextract('o--stage-brand">', '</article>', page)	# ausschneiden
			PLog(len(content))
			skip_list = get_zdfplayer_content(li, page=content)

	
	# 2. Strukturen nach Seitenanfang (1 Video doppelt möglich)
	PLog('Sendereihe_Sendungen2:')	
	rubriken =  blockextract('<picture class="">', page)			# fehlt z.B. in Titelthema
	PLog(len(rubriken))
	if len(rubriken) == 0: 
		rubriken =  rubriken + blockextract('<img class=', page)
	PLog(len(rubriken))
	
	if len(rubriken) == 0:				# Einzelbeitrag mit Abspielbutton 
		# get_video_carousel od. get_zdfplayer_content nicht geeignet
		# Seite kürzen, da 2 x duration 
		if 'class="video-module-video b-ratiobox"' in page:
			summ = stringextract('paragraph-large ">', '<', page)
			summ = unescape(summ); summ = repl_json_chars(summ)
			descr_par =	summ.replace('\n', '||')
			content = stringextract('class="video-module-video b-ratiobox"', '</button>', page)
			img_src = stringextract('teaser-image="[', ',', content)
			duration = stringextract('duration": "', '"', content)
			# SingleBeitrag(title, path, img_src, summ, dauer=duration)	# direkt zugunsten Resume entfernt  

			PLog('Satz14:')
			title=py2_encode(title); href=py2_encode(path);	 img_src=py2_encode(img_src);
			descr_par=py2_encode(descr_par); duration=py2_encode(duration);						
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
				(quote(title), quote(href), quote(img_src), quote(descr_par), quote(duration))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
				thumb=img_src, summary=summ, fparams=fparams, mediatype=mediatype)
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
	PLog(len(rubriken))
	 
	# kein Einzelbeitrag, weiterführender Link?
	# Bsp.: Rubriken/Kabarett/35 JAHRE 3SAT - JUBILÄUMSPROGRAMM
	#	-> rekursiv
	if len(rubriken) == 0 and got_page == True:		
		if 'class="is-clickarea-action' in page:
			PLog('is-clickarea-action:')
			img_src = stringextract('data-srcset="', ' ', page)		#  vor is-clickarea-action
			if img_src == '':
				img_src = R('Dir-folder.png')
			try:
				dur = re.search(u'>(.*?) min</span>', page).group(1)		# 1 h 56 min
				dur = dur + " min"
			except:
				dur=''
			pos = page.find('class="is-clickarea-action')
			page = page [pos:]
			title 	= stringextract('title="', '"', page)	
			title	= unescape(title); title = repl_json_chars(title)
			href	= stringextract('href="', '"', page)
			if href.startswith('http') == False:
				href	= DreiSat_BASE + href
		pos = page.find('class="o--footer">')
		if pos > 0:
			page = page[:pos]							# Fuß abschneiden
			descr	= stringextract('paragraph-large ">', '</p>', page)
			
			if dur:
				descr = "Dauer: %s \n\n%s" % (dur, descr)
			
			if href in skip_list == False:							# bereits extern erfasst
				title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);							
				fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
					 quote(href), quote(img_src))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
					fanart=R('3sat.png'), thumb=img_src, summary=descr, fparams=fparams)
	
	PLog("Mark1")													# Einzelbeiträge
	cnt=0; 
	add_list = ['/gesellschaft/quer/quer-kontakt-100.html',			# Redakt. + SocialMedia ausblenden
				'twitter.com/BR_quer', 'facebook.com/quer',
				'youtube.com/quer', 'instagram.com/quer_vom_br/',
				]
	skip_list = skip_list + add_list		
	PLog(skip_list)
	
	for rec in rubriken:
		#if 'data-playlist-toggle' not in rec:
		#	continue
		img_src =  stringextract('data-srcset="', ' ', rec)	
		if img_src == '':
			img_src = R('Dir-folder.png')
		rubrik 	= stringextract('<span>', '</span>', rec)
		rubrik	= cleanhtml(rubrik); rubrik = mystrip(rubrik)
		sub_rubrik = stringextract('ellipsis" >', '<', rec)
		sub_rubrik = mystrip(sub_rubrik)
		title	= stringextract('clickarea-link">', '</p>', rec)
		if title == '':
			title = stringextract('title="', '"', rec)
		title = unescape(title); title = mystrip(title)
		
		href	= stringextract('href="', '"', rec)
		PLog("href: " + href)
		skip=False
		for h in skip_list:											# get_zdfplayer_content: skip_list o. BASE
			if h in href:
				PLog("skip: " + href)
				skip=True
				break
		if skip:	
			PLog("skip") 
			continue
		skip_list.append(href)									
		if href.startswith('http') == False:
			href	= DreiSat_BASE + href
			
		descr	= stringextract('clickarea-link" >', '<', rec)
		tagline = rubrik
		if sub_rubrik:
			tagline = tagline + ' | ' + sub_rubrik
		tagline = unescape(tagline)
			
		try:
			dur = re.search(u'>(.*?) min</span>', page).group(1)		# 1 h 56 min
			dur = dur + " min"
		except:
			dur=''
		if dur:
			tagline = tagline + ' | ' + dur
			
		enddate	= stringextract('-end-date="', '"', rec)				# s.a. get_teaserElement
		enddate = time_translate(enddate, add_hour=0, day_warn=True)
		if enddate:
			enddate = "[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % enddate			 
			tagline = "%s | %s" % (tagline, enddate)
		
			
		if href.endswith('zdf.de/') or '/einstellungen' in href or u'Suche öffnen' in title or title=='':
			continue
		if href == DreiSat_BASE:
			continue
			
		title = repl_json_chars(title); descr = unescape(descr);
		descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
				
		PLog('Satz7:')
		PLog(img_src); PLog(rubrik); PLog(title);  PLog(href); PLog(tagline); PLog(descr);
		PLog(dur); 
				
		title=py2_encode(title); href=py2_encode(href);	 img_src=py2_encode(img_src);
		descr_par=py2_encode(descr_par); dur=py2_encode(dur); 
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
			(quote(title), quote(href), quote(img_src), quote(descr_par), quote(dur))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, summary=descr, tagline=tagline, fparams=fparams, mediatype=mediatype)

	if 'is-medium lazyload' in page:							# Test auf Loader-Beiträge, escaped
		if skip_lazyload == '':
			li, cnt = get_lazyload(li=li, page=page, ref_path=path)
		
	if cnt == 0 and "Einige Folgen sind FSK 16" in page:		# FSK-Hinweis bei leerer Liste
		dialog_fsk(page)										# util			

	if ret == True:
		return li	
	else:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------
# Blöcke für Rubrik, Rubrik_Single,  skip Systemhinw. usw. 
def get_container(page):
	PLog("get_container:")
			
	block_list = [
				u'class="o--horizontal-scroller js-cluster"|</article>',	# lazyload-Container
				u'grid-container has-title"|</article>',					# 
				u'"m--content-module grid-x large-up-2 small-margin-collapse is-white"|grid-container',
				u'<article class="m--teaser-topic-primary align-center-middle is-clickarea"|</article>',
				u'<article class="m--teaser-topic-secondary is-clickarea"|</article>',		
				u'<article class="m--teaser-small js-teaser js-rb-live  is-responsive"|</article>',
				u'<article class="video-carousel-item|</article>',				# Carousel-Item einzeln
				]
	
	container=[]; 
	for item in block_list:
		start, end = item.split('|')
		blocks = blockextract(start, page, end)
		if len(blocks) > 0:
			for block in blocks:
				container.append(block)
									
	PLog("container: %d" % len(container))
	return container			

#-------------
# Titel zum Block ermittlen
def get_title(rec):
	PLog("get_title:")
	PLog(rec)
	try:
		title = re.search(u'">(.*?)</h', rec).group(1)
	except:
		title=''
		PLog("skip_empty_title")
	
	return title

#-------------
# Loader-Beitrag auswerten, json-Format, 
# keys: style, sourceModuleType, teaserImageId, clusterType, clusterTitle,
#	teasertext, sophoraId, moduleId
# Die Pfade zu den Loader-Beiträgen  werden in einer Json-Beitragsliste außerhalb
#	der Loader-Beiträge ermittelt (mittels sophId).
#
def get_lazyload(li, page, ref_path):
	PLog('get_lazyload:')
	content =  blockextract('is-medium lazyload', page)		# Test auf Loader-Beiträge, escaped
	PLog(len(content))
	dauer	= stringextract('duration": "', '"', page)		# gilt für folgende loader-Beiträge
	img_pre = stringextract('data-srcset="', ' ', page)		# dto.
	PLog("dauer %s, img_pre: %s " % (dauer, img_pre))	
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	cnt=0
	for rec in content:	
		rec = unescape(rec)
		PLog('loader_Beitrag')
		PLog(rec[:60]); 
	
		# Ersatz für javascript: Auswertung + Rückgabe aller  
		#	Bestandteile:
		sophId,path,title,descr,img_src,dauer,tag,isvideo = get_teaserElement(rec)
		PLog(descr)
		if img_src == '':										
			if img_pre:
				img_src = img_pre								# Fallback 1: Rubrikbild
			else:
				img_src = R('icon-bild-fehlt.png')				# Fallback 2: Leer-Bild 
		if path == '':
			path	= "%s/%s.html" % (DreiSat_BASE, sophId)		# Zielpfad bauen
			
		tag = tag.strip()
		descr=py2_decode(descr); tag=py2_decode(tag) 
		if tag:
			descr = "%s\n\n%s"   % (tag, descr)
				
		title = repl_json_chars(title); 
		descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
		
		cnt = cnt+1	
		PLog('Satz8: %d' % cnt)
		PLog(sophId); PLog(path); PLog(title);PLog(descr); PLog(img_src); PLog(dauer); PLog(tag); 
		
		if isvideo == 'true':											#  page enthält data-playlist
			title=py2_encode(title); path=py2_encode(path);	img_src=py2_encode(img_src);
			descr_par=py2_encode(descr_par); dauer=py2_encode(dauer);					
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s'}" %\
				(quote(title), quote(path), quote(img_src), quote(descr_par), quote(dauer))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
				thumb=img_src, summary=descr, tagline=dauer, fparams=fparams, mediatype=mediatype)
		else:
			title=py2_encode(title); path=py2_encode(path);	img_src=py2_encode(img_src);
			fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
				 quote(path), quote(img_src))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
				fanart=R('3sat.png'), thumb=img_src, summary=descr, fparams=fparams)

	return li, cnt
	
#------------
# Ersatz für javascript: Ermittlung Icon + Sendedauer
#	rec hier bereits unescaped durch get_lazyload
# Aus Performancegründen (Anzahl der Elemente manchmal 
#	> 30) werden die Elemente in STORE (TEXTSTORE/SophoraTeaser)
# gecached, unabhängig von SETTINGS('pref_load_summary').
# 20.11.2019 Einsetzungselement sophoraId ausreichend für path 
#	(teaserHeadline,teasertext,clusterTitle entfallen)
# Hinweis: Änderungen ev. auch in ardundzdf erforderlich.
#
# 20.09.2021 Einsetzungselemente style, moduleId, clusterType
#	fallen ebenfalls (sophoraId + sourceModuleType ausreichend)
# 28.03.2023 Unterverz. SophoraTeaser in TEXTSTORE (Performance)
#
def get_teaserElement(rec):
	PLog('get_teaserElement:')
	# Reihenfolge Ersetzung: sophoraId, teaserHeadline, teasertext, clusterTitle
	
	sophoraId = stringextract('"sophoraId": "', '"', rec)
	teaserHeadline = stringextract('teaserHeadline": "', ',', rec)
	teasertext = stringextract('"teasertext": "', '",', rec)
	clusterTitle = stringextract('clusterTitle": "', ',', rec)
	
	sophoraId = transl_json(sophoraId); #teaserHeadline = transl_json(teaserHeadline);
	teasertext = transl_json(teasertext); clusterTitle = transl_json(clusterTitle);
	PLog(teaserHeadline)	
	
	sophId = sophoraId; title = teaserHeadline; ctitle = clusterTitle;  # Fallback-Rückgaben
	descr = teasertext; 
	isvideo=''	
		
	sophoraId=quote(py2_encode(sophoraId)); 
	teasertext = quote(py2_encode(teasertext)); clusterTitle = quote(py2_encode(clusterTitle));
	
	#path = "https://www.3sat.de/teaserElement?sophoraId=%s&style=m2&moduleId=mod-2&clusterType=Cluster_S&sourceModuleType=cluster-s" % (sophoraId)
	path = "https://www.3sat.de/teaserElement?sophoraId=%s&sourceModuleType=cluster-s" % (sophoraId)
	PLog(path)
	
	STORE = os.path.join(TEXTSTORE, 'SophoraTeaser') 
	if os.path.exists(STORE) == False:
		try:  
			os.mkdir(STORE)
		except OSError:  
			msg1 = 'Verzeichnis SophoraTeaser konnte nicht erzeugt werden.'
			msg2 = "Funktion: get_teaserElement my3Sat.py"
			PLog(msg1); PLog(msg2); 
			MyDialog(msg1, msg2, '')
			return	
	
	fpath = os.path.join(STORE, sophoraId)
	PLog('fpath: ' + fpath)
	if os.path.exists(fpath) and os.stat(fpath).st_size == 0: # leer? = fehlerhaft -> entfernen 
		PLog('fpath_leer: %s' % fpath)
		os.remove(fpath)
	if os.path.exists(fpath):				# teaserElement lokal laden
		PLog('lade_lokal:') 
		page =  RLoad(fpath, abs_path=True)
	else:
		page, msg = get_page(path)			# teaserElement holen
		if page:							# 	und in STORE speichern
			msg = RSave(fpath, page, withcodec=True)
	PLog(page[:100])
	
	if page:								# 2. teaserElement auswerten
		img_src =  stringextract('data-srcset="', ' ', page)	
		title	= stringextract('clickarea-link">', '</p>', page)
		if title == '':
			title = stringextract('title="', '"', page)			# Ersatz: Titel hinter href-Url
		title	= unescape(title); 
		title	= transl_json(title); 
		ctitle = stringextract('ellipsis" >', '<', page)  		# -> tag (subheadline)
		tag 	= stringextract('<span>', '</span>', page)
		dauer	= stringextract('icon-opaque is-not-selected', '/span>', page)
		dauer	= stringextract('class="label">', '<', dauer)	# label allein unsicher (Bsp. Vorab)
		
		enddate	= stringextract('-end-date="', '"', page)		# kann leer sein
		enddate = time_translate(enddate, add_hour=0, day_warn=True)
		if dauer and enddate:
			dauer = u"%s | [B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (dauer, enddate)			 
		
		
		path	= stringextract('href="', '"', page)
		if path.startswith('http') == False:
			path = DreiSat_BASE + path
		descr	= stringextract('clickarea-link" >', '<', page)
		if descr == '':											# 1. Ersatz: 
			descr	= stringextract('teaser-text" >', '<', page)# wie ardundzdf
		if descr == '':											# 2. Ersatz (Bild-Beschr.): 
			descr	= stringextract('alt="', '"', page)
		if ctitle:
			tag = tag + " | " + ctitle
			
		tag = cleanhtml(tag); descr = unescape(descr)
		if "data-playlist" in page:			# Videobeitrag? - Folgeseiten möglich
			isvideo = 'true'
		
		# sophId s.o.
		return sophId, path, title, descr, img_src, dauer, tag, isvideo	
	else:									#  Fallback-Rückgaben, Bild + Dauer leer
		img_src=''; dauer=''; tag=''; isvideo=''
		return sophId, path, title, descr, img_src, dauer, tag, isvideo
	
#------------
# video-carousel-item-Beiträge auswerten, html-Format, Seitenkopf
def get_video_carousel(li, page):
	PLog('get_video_carousel:')
	content =  blockextract('video-carousel-item">', page)
	if len(content) == 0:
		content =  blockextract('class="video-module-video b-ratiobox"', page)
	PLog(len(content))
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	cnt=0

	for rec in content:	
		if 'data-module="zdfplayer"' not in rec:		# redakt. Beitrag o. Video
			continue
		videoinfos = stringextract("video-infos='{", '}', rec)
		videoinfos = unescape(videoinfos)
		title 	= stringextract('title":', '",', videoinfos)
		title 	= (title.replace('\\"', '').replace('"', ''))
		dauer 	= stringextract('duration": "', '"', videoinfos)	# 2 min
		path	= stringextract('embed_content": "', '"', rec)
		path 	= "%s%s.html" % (DreiSat_BASE, path)
		img_src	= stringextract('image="{', '}', rec)	# data-zdfplayer-teaser-image=
		img_src	= stringextract('768xauto&quot;:&quot;', '&quot', rec)	# 768xauto	
		img_src	= unescape(img_src); img_src = img_src.replace('\\', '')
		if img_src == '':
			img_src = R('Dir-folder.png')
	
		tagline = dauer
		subtitle	= stringextract('brand-subtitle">', '<', rec)
		if not subtitle:
			subtitle	= stringextract('subheadline level-7 " >', '<', rec)
		if subtitle:
			tagline = "%s | %s" % (dauer, subtitle)
		descr 	= stringextract('paragraph-large ">', '<', rec)
		descr 	= unescape(descr)
		descr = transl_json(descr); 

		descr = transl_json(descr); 
		PLog('Satz9:')
		PLog(img_src); PLog(title); PLog(dauer); PLog(path); 
		title=py2_encode(title); path=py2_encode(path);	 img_src=py2_encode(img_src);
		dauer=py2_encode(dauer);
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
			(quote(title), quote(path), quote(img_src), quote(dauer))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, tagline=tagline, fparams=fparams, mediatype=mediatype)			 
			 
		cnt=cnt+1
	return li, cnt

#------------
# ideo-carousel-item- und o--stage-brand-Beiträge auswerten,
#	html-Format, Seitenkopf - Doppel zu Folgebeiträgen möglich
# 28.10.2021 Rückgabe skip_list (path) für externen Abgleich
#
def get_zdfplayer_content(li, page):
	PLog('get_zdfplayer_content:')
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 			# Kennz. Video für Sofortstart 
		mediatype='video'

	content = blockextract('data-module="zdfplayer"', page)
	PLog(len(content))
	cnt=0; skip_list=[]
	for rec in content:	
		tag=''; 
		if 'data-module="zdfplayer"' in rec == False:				# redakt. Beitrag ohne Video
			continue
		videoinfos = stringextract("video-infos='{", '}', rec)
		videoinfos = unescape(videoinfos)
		title 	= stringextract('title":', '",', videoinfos)
		title 	= (title.replace('\\"', '').replace('"', ''))

		dauer 	= stringextract('duration": "', '",', videoinfos)	# Bsp. 2 min
		enddate	= stringextract('-end-date="', '"', page)			# get_teaserElement
		enddate = time_translate(enddate, add_hour=0, day_warn=True)
		if dauer and enddate:
			dauer = "%s | [B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (dauer, enddate)			 
		
		play_id	= stringextract('zdfplayer-id="', '"', rec)			# z.B. die-anstalt-vom-5-oktober-2021-100
		
		path	= stringextract('embed_content": "', '"', rec)
		p = path.replace('/zdf/', '/') 								# z.B. /zdf/kultur/kulturzeit/..
		skip_list.append(p + ".html" )								# skip_list für ext. Abgleich o. Base
		path 	= DreiSat_BASE + path + ".html"
		
		img_src	= stringextract('data-srcset="', '"', rec)			
		img_src	= img_src.split(' ')[0]								# kann mit Blank enden
		if img_src == '':
			img_src = stringextract('teaser-image-overwrite', 'quot;}', rec)	# Bsp. Wissen/#Erklärt
			PLog(img_src[:100])
			img_src =stringextract('https:', '&', img_src)
			PLog(img_src)
			img_src = 'https:' + img_src.replace('\\/', '/')	 
		
		tag = dauer
		subtitle	= stringextract('brand-subtitle">', '<', rec)
		if subtitle:
			tag = "Dauer %s min" % (dauer, subtitle)
		tag = "%s\n%s" % (tag, play_id)

		descr 	= stringextract('paragraph-large ">', '<', rec)
		descr 	= unescape(descr)
		descr = transl_json(descr); 
		title = transl_json(title); title = repl_json_chars(title);
	
		PLog('Satz10:')
		PLog(img_src); PLog(title); PLog(path); 
		PLog(skip_list); PLog(play_id);
		title=py2_encode(title); path=py2_encode(path);	img_src=py2_encode(img_src);
		dauer=py2_encode(dauer);
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s'}" %\
			(quote(title), quote(path), quote(img_src), quote(dauer))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)
			 	
		cnt=cnt+1

	PLog(u"Anzahl Beiträge: %s" % cnt)
	PLog(len(skip_list)); 
	return skip_list

#------------

# SingleBeitrag für Verpasst + A-Z
#	hier auch m3u8-Videos verfügbar. 
#
# 16.05.2017: Design neu, Videoquellen nicht mehr auf der Webseite vorhanden - (Ladekette ähnlich ZDF-Mediathek)
# 22.05.2019: Design neu, Ladekette noch ähnlich ZDF-Mediathek, andere Parameter, Links + zusätzl. apiToken
# 21.01.2021 Nutzung build_Streamlists + build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
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
	li = home(li, ID='3Sat')							# Home-Button
			
	page, msg = get_page(path=path)						# 1. Basisdaten von Webpage holen
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
	profile_url= stringextract('content": "', '"', content)		# profile_url
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
	
	page = (page.replace('\\', '').replace('": "', '":"'))
	PLog(page[:100])

	player = "ngplayer_2_4"
	pos = page.find('"programmeItem"')
	page = page[max(0, pos):]
	streams = stringextract('streams":', '}}', page)	# in "mainVideoContent":..
	videodat_url= stringextract('ptmd-template":"', '"', streams)
	videodat_url = "https://api.3sat.de" + videodat_url
	videodat_url = videodat_url.replace('{playerId}', player)
	PLog("videodat_url: " + videodat_url)
	page,msg = get_page(path=videodat_url, header=headers)
	
	if page == '':			
		msg1 = "SingleBeitrag3: Abruf fehlgeschlagen"
		PLog(msg1); PLog(msg)
		msg2 = msg
	
	if page == '':											# Alternative mediathek statt 3sat in Url
		videodat_url = 'https://api.3sat.de/tmd/2/ngplayer_2_3/vod/ptmd/mediathek/' + video_ID
		page,msg = get_page(path=videodat_url, header=headers)
		page = str(page)									# <type 'tuple'> möglich
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
		formitaeten = blockextract('formitaeten', page)		# 4. einzelne Video-URL's ermitteln 
		geoblock =  stringextract('geoLocation',  '}', page) 
		geoblock =  stringextract('"value":"',  '"', geoblock).strip()
		PLog('geoblock: ' + geoblock);
		if 	geoblock == 'none':								# i.d.R. "none", sonst "de" - wie bei ARD verwenden
			geoblock = ' | ohne Geoblock'
		else:
			if geoblock == 'de':			# Info-Anhang für summary 
				geoblock = ' | Geoblock DE!'
			if geoblock == 'dach':			# Info-Anhang für summary 
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
	li = home(li, ID='3Sat')						# Home-Button
	
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('3sat') in up_low(webtitle): 	# Sender mit Blank!
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
	my3satCacheTime =  600							# 10 Min.: 10*60	
	
	# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime,  
	#			5=summ, 6=vonbis, 7=today_human, 8=endtime:  
	rec = EPG.EPG(ID="3SAT", mode='OnlyNow')	# Daten holen - nur aktuelle Sendung
	sname=''; stime=''; summ=''; vonbis=''		# Fehler, ev. Sender EPG_ID nicht bekannt
	title=''; tag=''

	if rec:								
		sname=py2_encode(rec[3]); stime=py2_encode(rec[4]); 
		summ=py2_encode(rec[5]); vonbis=py2_encode(rec[6])
	else:
		return "", "", ""						# title, tag, summ	

	PLog("get_epg_Debug:")
	typ=str(type(sname))	# Debug, Forum Post 3.301
	PLog(typ)	
	PLog(str(rec))
	if "list" in typ:
		msg1 = "Fehler im Datensatz."
		msg2 = "Bitte Debuglog hochladen"
		MyDialog(msg1, msg2, '')	
		sname=""
			

	if sname:									# Sendungstitel
		title = str(sname).replace('JETZT:', 'LIVE')
		tag = u'Sendung: %s Uhr' % vonbis
	
	return title, tag, summ
	
####################################################################################################
# 3Sat - Bild-Galerien/-Serien
#	Übersichtsseiten - 3sat zeigt 12 Beiträge pro Seite
#		path für weitere Seiten: class="load-more-container"
# 04.08.2020 Webänderungen Titel, Subtitel
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



