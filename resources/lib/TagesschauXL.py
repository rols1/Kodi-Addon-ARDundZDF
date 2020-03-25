# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
#	Stand: 15.02.2020
#
#	Anpassung Python3: Modul future
#	Anpassung Python3: Modul kodi_six + manuelle Anpassungen
#	

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

import json		
import os, sys
import ssl
import datetime, time
import re							# u.a. Reguläre Ausdrücke
import string

# import ardundzdf reicht nicht für thread_getpic
from ardundzdf import *					# transl_wtag, get_query, thread_getpic, 
										# ZDF_SlideShow, Parseplaylist, test_downloads
from resources.lib.util import *


# Globals
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
	ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

NAME			= 'ARD und ZDF'
BASE_URL 		= 'https://www.tagesschau.de'
ARD_m3u8 		= 'http://tagesschau-lh.akamaihd.net/i/tagesschau_1@119231/master.m3u8' # intern. Link
ARD_100 		= 'https://www.tagesschau.de/100sekunden/index.html'
ARD_Last 		= 'https://www.tagesschau.de/sendung/letzte-sendung/index.html'
ARD_20Uhr 		= 'https://www.tagesschau.de/sendung/tagesschau/index.html'
ARD_Gest 		= 'https://www.tagesschau.de/sendung/tagesschau_mit_gebaerdensprache/index.html'
ARD_tthemen 	= 'https://www.tagesschau.de/sendung/tagesthemen/index.html'
ARD_Nacht 		= 'https://www.tagesschau.de/sendung/nachtmagazin/index.html'
ARD_bab 		= 'https://www.tagesschau.de/bab/index.html'
ARD_Archiv 		= 'https://www.tagesschau.de/multimedia/sendung/index.html'
ARD_Blogs		= 'https://www.tagesschau.de/videoblog/startseite/index.html'
ARD_PolitikRadio= 'https://www.tagesschau.de/multimedia/politikimradio/index.html'
ARD_Bilder 		= 'https://www.tagesschau.de/multimedia/bilder/index.html'
ARD_kurz 		= 'https://www.tagesschau.de/faktenfinder/kurzerklaert/index.html'
BASE_FAKT		='https://faktenfinder.tagesschau.de'										# s. get_content


# Icons
ICON 			= 'icon.png'		# ARD + ZDF
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MAIN_TVLIVE= 'tv-livestreams.png'
ICON_MEHR 		= "icon-mehr.png"
ICON_SEARCH 	= 'ard-suche.png'
ICON_DELETE 			= "icon-delete.png"

# Github-Icons zum Nachladen aus Platzgründen
GIT_CAL			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-calendar.png?raw=true"
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'
ICON_LIVE 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Live.png?raw=true'
ICON_WICHTIG 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Wichtig.png?raw=true'
ICON_100sec 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau100sec.png?raw=true'
ICON_LAST 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-letzte-Sendung.png?raw=true'
ICON_20 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-20Uhr.png?raw=true'
ICON_20GEST 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-20Uhr-Gest.png?raw=true'
ICON_TTHEMEN 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesthemen.png?raw=true'
ICON_NACHT 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Nachtmagazin.png?raw=true'
ICON_BAB 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-BaB.png?raw=true'
ICON_ARCHIV 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Sendungsarchiv.png?raw=true'
ICON_POD 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Podcasts.png?raw=true'
ICON_BLOGS 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Videoblogs.png?raw=true'
ICON_RADIO 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Radio.png?raw=true'
ICON_BILDER		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Bilder.png?raw=true'
ICON_KURZ 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Kurz.png?raw=true'
ICON_24			= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau24.png?raw=true'


# ----------------------------------------------------------------------
# Seiten mit unterschiedlichen Archiv-Inhalten - ARD_bab, ARD_Archiv, ARD_Blogs,
#	ARD_PolitikRadio, ARD_Bilder, ARD_kurz, BASE_FAKT
# 
# 			
def Main_XL():
	PLog('Main_XL:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
				
	title="Suche auf www.tagesschau.de"
	summ = "Suche Sendungen und Videos auf www.tagesschau.de"
	fparams="&fparams={'query': ''}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Search", fanart=ICON_MAINXL, 
		thumb=R(ICON_SEARCH), fparams=fparams)
		
	# Seiten mit Direktsprung in menu_hub zu XLGetVideoSources (-> PlayVideo) benötigen 
	#	für die Resumefunktion beim Sofortstart hier bereits die Kennz. als Video
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	# --------------------------------- 						# Livestreams
	# Live: akt. PRG + vom Sender holen, json-Links in XL_Live
	# PRG gilt auch für die  intern. Seite			
	path = "http://www.tagesschau.de/multimedia/livestreams/index.html"
	page, msg = get_page(path=path)			
	if page == '':	
		msg1 = "Fehler in Main_XL:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
	PLog(len(page))			
	teasertext = stringextract('class="teasertext">', '</p>', page)
	teasertext =  stringextract('<strong>', '</strong>', teasertext)
		
	title = 'Livestream'
	tag = teasertext
	summ = u"[B][COLOR green]Livestream mit Sport (nur für Deutschland)[/COLOR][/B]"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Live", fanart=ICON_MAINXL, 
		thumb=ICON_LIVE, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)
	title = 'Livestream (diesen im Ausland verwenden)'
	summ = "[B][COLOR green]internationaler Livestream[/COLOR][/B]"
	fparams="&fparams={'ID': 'international'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Live", fanart=ICON_MAINXL, 
		thumb=ICON_LIVE, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)

	# ---------------------------------							# in menu_hub Direktsprung zu XLGetVideoSources:
	tag = "[B][COLOR red]Letzte Sendung[/COLOR][/B]"		
	title = 'Tagesschau'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_Last), 'ARD_Last', quote(ICON_LAST))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_LAST, fparams=fparams, tagline=tag, mediatype=mediatype)
	title = 'Tagesschau in 100 Sekunden' 
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_100), 'ARD_100', quote(ICON_100sec))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_100sec, fparams=fparams, tagline=tag, mediatype=mediatype)
	title = 'Tagesschau 20 Uhr'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_20Uhr), 'ARD_20Uhr', quote(ICON_20))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_20, fparams=fparams, tagline=tag, mediatype=mediatype)
	title = 'Tagesschau 20 Uhr (Gebärdensprache)'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), ARD_Gest, 'ARD_Gest', quote(ICON_100sec))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_20GEST, fparams=fparams, tagline=tag, mediatype=mediatype)
	title = 'Tagesthemen'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_tthemen), 'ARD_tthemen', quote(ICON_TTHEMEN))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_TTHEMEN, fparams=fparams, tagline=tag, mediatype=mediatype)
	title = 'Nachtmagazin'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_Nacht), 'ARD_Nacht', quote(ICON_NACHT))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_NACHT, fparams=fparams, tagline=tag, mediatype=mediatype)
		
	# ---------------------------------							# in menu_hub Direktsprung zu get_content:	
	title = 'Bericht aus Berlin'
	tag = u"aktuelle Beiträge - mehr im Sendungsarchiv (jeweils sonntags)"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_bab), 'ARD_bab', quote(ICON_BAB))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_BAB, tagline=tag, fparams=fparams)
	title = 'Sendungsarchiv: Tagesschau-Sendungen eines Monats'
	tag = u"enthält auch: tagesschau vor 20 Jahren und tagesthemen."
	summ = u'sonntags enthält das Archiv in der Regel auch den Bericht aus Berlin'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_Archiv), 'ARD_Archiv', quote(ICON_ARCHIV))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_ARCHIV, fparams=fparams, tagline=tag, summary=summ)
	title = 'Videoblogs'
	fparams="&fparams={'title': '%s','path': '%s'}"  % (title, quote(ARD_Blogs)) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.Videoblogs", fanart=ICON_MAINXL, 
		thumb=ICON_BLOGS, fparams=fparams)
	title = 'Politik im Radio'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_PolitikRadio), 'ARD_PolitikRadio', quote(ICON_RADIO))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_RADIO, fparams=fparams)
	title = 'Bildergalerien'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_Bilder), 'ARD_Bilder', quote(ICON_BILDER))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_BILDER, fparams=fparams)
	title = '#kurzerklärt'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_kurz), 'ARD_kurz', quote(ICON_KURZ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_KURZ, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE)
		
# ----------------------------------------------------------------------
def menu_hub(title, path, ID, img):	
	PLog('menu_hub:'); PLog(title); PLog(ID);

	if ID=='ARD_Archiv':						# Vorschaltung Kalendertage (1 Monat)
		Archiv(path=path, ID=ID, img=img) 	# Archiv: Callback nach hier, dann weiter zu oc=get_content
		return	

	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in menu_hub:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 		
	
	# Direktsprünge zu Url der Sendungseite - der Rest der Seiten enthält vorwiegend gleiche Inhalte 
	# aus dem Archiv
	# home in GetVideoSources
	if ID=='ARD_100' or ID=='ARD_Last' or ID=='ARD_20Uhr' or ID=='ARD_Gest' or ID=='ARD_tthemen' or ID=='ARD_Nacht':
		url = path
		PLog('Satz:')
		PLog(title); PLog(url); PLog(img)
		XLGetVideoSources(path=url,title=title,summary='',tagline='',thumb=img)
		return

	# Seiten mit unterschiedlichen Archiv-Inhalten - ARD_bab, ARD_Archiv, ARD_Blogs,
	#	ARD_PolitikRadio, ARD_Bilder, ARD_kurz, BASE_FAKT
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')			# Home-Button
	
	li = get_content(li, page, ID=ID)
	
	# Archiv 'Bericht aus Berlin': enthält weitere Beiträge eines Monats (java-script -
	#	hier nicht zugänglich, s. id="monthselect") 
	if ID == 'ARD_bab':							# 2 Buttons aus Sendungsarchiv anhängen
		ressort = stringextract('ressort">Sendungsarchiv', '</ul>', page)
		hreflist = blockextract('<a href', ressort)
		for link in hreflist:
			PLog(link)
			href =  stringextract('href="', '"', link)
			href = BASE_URL + href
			title= stringextract('.html">', '</a>', link) 
			title= "[COLOR red]Archiv: [/COLOR]" + title
			tag = u"Auszug aus dem Sendungsarchiv - mehr im Menü Sendungsarchiv"
			fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
				(quote(title), quote(href), 'ARD_bab', quote(ICON_BAB))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_BAB, 
				thumb=ICON_BAB, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
		 
# ----------------------------------------------------------------------
def Archiv(path, ID, img):	# 30 Tage - ähnlich Verpasst 
	PLog('Archiv:'); PLog(ID);

	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')										# Home-Button
		
	wlist = range(0,30)			# Abstand 1 Tage
	now = datetime.datetime.now()
	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")		# Formate s. man strftime (3)
		SendDate = rdate.strftime("%Y%m%d")		# ARD-Archiv-Format		
		iWeekday =  rdate.strftime("%A")
		punkte = '.'
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)
		
		ipath =  BASE_URL + '/multimedia/video/videoarchiv2~_date-%s.htm' % (SendDate)
		PLog(ipath); PLog(iDate); PLog(iWeekday);
		title =	"%s | %s" % (iDate, iWeekday)
		PLog(title)	

		ID = 'ARD_Archiv_Day'
		title=py2_encode(title); ipath=py2_encode(ipath); img=py2_encode(img);
		fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
			(quote(title), quote(ipath), ID, quote(img))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
			thumb=GIT_CAL, fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
			
	 
# ----------------------------------------------------------------------	 
def XL_Search(query='', search=None, pagenr=''):
	PLog("XL_Search:")
	if 	query == '':	
		query = get_query(channel='ARD')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
	query_org = query	
	query=py2_decode(query)		# decode, falls erf. (1. Aufruf)

	items_per_page = 10			# höhere Werte sind wirkungslos (Vorgabe ARD)
	PLog('XL_Search:'); PLog(query); PLog(pagenr); 

	ID='Search'
	path =  BASE_URL + '/suche2.html?page_number=%s&results_per_page=%s&query=%s&dnav_type=video&sort_by=date' %\
		(pagenr,items_per_page,query)
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in XL_Search:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
	
	if u'leider erfolglos. Bitte überprüfen Sie Ihre Eingabe' in page:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
		msg1 = u'Keine Beiträge zu: %s' % query  
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return 	

	searchBox 	= stringextract('Suchergebnis</h2>', '</p>', page)	
	searchResult = stringextract('<strong>', '</strong>', searchBox)
	searchView	= stringextract('</strong> Treffer.', '.', searchBox)
	MaxPages	= (int(searchResult) / items_per_page)			# -> float (__future__)
	if '.' in str(MaxPages):									# 1 Seite mehr
		MaxPages = MaxPages + 1
	PLog("searchResult: %s, MaxPages %d, searchView: %s" % (searchResult, MaxPages, searchView))
				
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')										# Home-Button
	
	# der Sender gibt Suchergebnisse bereits seitenweise aus, hier
	#	 umgesetzt mit pagenr - offset entfällt	
	li = get_content(li, page, ID='Search', mark=query)

	pagenr = int(pagenr) + 1
	if pagenr <= MaxPages:
		PLog("pagenr: " + str(pagenr))
		title 	= u"Weitere Beiträge zu [B][COLOR red]%s[/COLOR][/B]" % query_org
		summ 	= "Insgesamt: %s Treffer, Seite(n): %d," % (searchResult, MaxPages) 
		summ	= "%s %s" % (summ, searchView)  
		tag 	= "Aktuelle Seite: %d" % (pagenr-1)
		query_org=py2_encode(query_org); 
		fparams="&fparams={'query': '%s', 'pagenr': '%s'}" %\
			(quote(query_org), str(pagenr))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), tagline=tag, summary=summ, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# mark dient der Farbmarkierung bei ID='Search' 
#
def get_content(li, page, ID, mark=''):	
	PLog('get_content:')
	PLog(len(page)); PLog(ID);
	
	if  ID=='Search':
		content =  blockextract('class="teaser">', page)
	if ID=='ARD_bab' or ID=='ARD_Bilder' or ID=='ARD_PolitikRadio':
		content =  blockextract('class="teaser">', page)
	if ID=='ARD_Blogs' or ID=='ARD_kurz'  or ID=='ARD_Archiv_Day':
		content =  blockextract('class="teaser" >', page)
		base_url = BASE_FAKT
	if ID=='ARD_PolitikRadio':
		content =  blockextract('class="teaser"', page)
		
	base_url = BASE_URL						
	PLog(len(page)); PLog(len(content));
	
	if len(content) == 0:										# kein Ergebnis oder allg. Fehler
		msg1 = 'Leider keine Inhalte' 							# z.B. bei A-Z für best. Buchstaben 
		s = 'Es ist leider ein Fehler aufgetreten.'				# ZDF-Meldung Server-Problem
		if page.find('"title">' + s) >= 0:
			msg = s + u' Bitte versuchen Sie es später noch einmal.'					
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		return
		
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	cnt = 0
	for rec in content:	
		cnt = cnt +1												# Satz-Zähler						
		teaser_img = ''												
		teaser_img = stringextract('src="', '"', rec) 	
		if teaser_img.find('http://') == -1:						# ohne http://	bei Wetter + gelöschten Seiten		
			teaser_img = base_url + teaser_img
		teaser_url = stringextract('href="', '"', rec)				# 1. Stelle <a href=
		if teaser_url.startswith('http') == False:
			teaser_url =  base_url + teaser_url				
		PLog(teaser_img); PLog(teaser_url)
		
		if 'twitter' in teaser_url or 'facebook' in teaser_url :	# kein Multimedia-Beitrag?	
			PLog('twitter, facebook: skip')
			continue
		if teaser_url.endswith('.de') or  teaser_url.endswith('.de/'):
			PLog('Sender-/Studio-Link: skip')
			continue
			 
			
		# hier relevante ID-Liste. ID's mit Direktsprüngen (s. menu_hub) haben XLGetVideoSources als Callback:
		# Search, ARD_bab, ARD_Archiv, ARD_PolitikRadio, ARD_Bilder, ARD_kurz 
		teasertext='';	headline=''; dachzeile=''; teaser_typ=''; teaser_date=''
		gallery_url='';	tagline=''; onlyGallery=False							
		if ID=='Search':
			teasertext = stringextract('class="teasertext ">', '</p>', rec).strip()	# Teasertext mit url + Langtext, 
			teasertext = stringextract('html">', '<strong>', teasertext)		# Text hinter url, nach | folgt typ
			teasertext = teasertext.replace('|', '')			
			dachzeile = stringextract('dachzeile">', '</p>', rec).strip()		# Dachzeile mit url + Typ + Datum							
			teaser_typ =  stringextract('<strong>', '</strong>', dachzeile)
			teaser_date =  stringextract('</strong>', '</a>', dachzeile)
			tagline = teaser_typ + teaser_date
			headlineclass = stringextract('headline">', '</h3>', rec).strip()	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
		if ID=='ARD_bab':
			headline = stringextract('class="headline">', '</h', rec)
			dachzeile = stringextract('dachzeile">', '</p>', rec)				# fehlt im 1. Satz
			if cnt == 1:
				teasertext = stringextract('class="teasertext">', '|&nbsp', rec)	# 1. Satz mit Leerz. vor ", mit url + Typ
				pos = rec.find('Ganze Sendung:')			# dachzeile im 1. Satz hier mit Datum
				if pos:
					headline = stringextract('>', '|&nbsp', rec[pos-1:])
			else:
				teasertext = stringextract('class="teasertext ">', '|&nbsp', rec)
			if dachzeile:
				tagline = dachzeile
			else:
				tagline = headline
		if ID=='ARD_Blogs' or ID=='ARD_kurz':
			if cnt == 1 and ID=='ARD_Blogs':		# allg. Beschreibung in ARD_Blogs, 1. Satz
				continue
			headline = stringextract('class="headline">', '</h4', rec)
			dachzeile = stringextract('dachzeile">', '</p>', rec)				# fehlt im 1. Satz
			teasertext = stringextract('class="teasertext">', '|&nbsp', rec)	# 1. Satz mit Leerz. vor ", mit url + Typ
			tagline = dachzeile	
			pos = rec.find('class="gallerie">')								# Satz mit zusätzl. Bilderserie?
			if pos > 0:															# wir erzeugen 2. Button, s.u.
				leftpos, leftstring = my_rfind('<a href=', 'class="icon galerie">', rec)		
				gallery_url = base_url + stringextract('href="', '"', leftstring) 
		if ID=='ARD_Bilder': 
			onlyGallery=True													# kein Hybrid-Satz
			gallery_url =  base_url + stringextract('href="', '"', rec)		# 1. Stelle <a href=
			headlineclass = stringextract('headline">', '</h4>', rec).strip()	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			teasertext = stringextract('title="', '"', rec)					# Bildtitel als teasertext
			teaserdate = stringextract('class="teasertext">', '|&nbsp', rec)  # nur Datum
			tagline = teaserdate			
		if ID=='ARD_PolitikRadio': 													# Podcasts
			headlineclass = stringextract('headline">', '</h4>', rec).strip()	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			if cnt == 1:									# url für 1. Satz hier - fieldset hier eingebettet	
				teaser_url = ARD_PolitikRadio	
				headline = stringextract('<h2 class="headline">', '</h2>', page) # außerhalb akt. Satz! 
			teasertext = stringextract('class="teasertext">', '</p>', rec)	# Autor + Sendeanstalt					
			tagline = teasertext.strip()
		if ID=='ARD_Archiv_Day':
			headlineclass = stringextract('headline">', '</h4>', rec)			# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			teasertext = stringextract('class="teasertext ">', '</p>', rec).strip()	# Teasertext mit url + Langtext, 
			teasertext = stringextract('html">', '</a>', teasertext)		# Text hinter url, nach | folgt typ
			if teasertext == '':											# leer: tagesschau vor 20 Jahren
				teasertext = headline		
			dachzeile = stringextract('dachzeile">', '</p>', rec)		
			tagline = dachzeile	
		PLog('content-extracts:')
		teasertext = teasertext	 # Decod. manchmal für Logausgabe erforderlich 	
		PLog(teaser_url); PLog(headline); PLog(teasertext[:81]);  		
		PLog(dachzeile);	PLog(teaser_typ); PLog(teaser_date);		
			
		title = unescape(headline); title = repl_json_chars(title)
		if ID=='Search':
			title = make_mark(mark, title, "red")	# farbige Markierung
		tagline = cleanhtml(tagline); tagline = repl_json_chars(tagline)
		summary = unescape(teasertext.strip())
		summary = cleanhtml(summary); summary = repl_json_chars(summary)
		summ_par = summary.replace('\n','||')
		if tagline  == summary:
			tagline = ''
				
		if title=='':	
			PLog('title leer: skip')
			continue
			
		PLog('neuer_Satz:')
		PLog(teaser_img);PLog(teaser_url);PLog(title);PLog(summary[:80]);PLog(tagline);
		title=py2_encode(title); gallery_url=py2_encode(gallery_url)
		if onlyGallery == True:					# reine Bildgalerie
			fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title),
				 quote(gallery_url))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Bildgalerie", 
				fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams)				
		else:									# Hybrid-Sätze Video/Bilder 
			title=py2_encode(title); teaser_url=py2_encode(teaser_url);  summary=py2_encode(summary)
			teaser_img=py2_encode(teaser_img); tagline=py2_encode(tagline); summ_par=py2_encode(summ_par)				
			fparams="&fparams={'title': '%s', 'path': '%s', 'summary': '%s', 'thumb': '%s', 'tagline': '%s'}" %\
				(quote(title), quote(teaser_url), quote(summ_par),
				quote(teaser_img), quote(tagline))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetVideoSources", 
				fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams, mediatype=mediatype)				
			if gallery_url:
				title = 'Bilder: ' + title
				fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title),
					 quote(gallery_url))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Bildgalerie", 
					fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams)	
	return li

# ----------------------------------------------------------------------
def XL_Bildgalerie(path, title):	
	PLog('XL_Bildgalerie'); PLog(title); PLog(path)
	title_org = title
	
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in XL_Bildgalerie:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
		
	segment =  stringextract('class="mod modA modGallery">', 'class=\"section sectionA">', page)	
	img_big = False		
	if segment.find('-videowebl.jpg') > 0:		# XL-Format vorhanden?  
		img_big = True		
	content =  blockextract('class="mediaLink" href=\"#">', segment)   					# Bild-Datensätze		
	PLog(len(content))
	title = 'Bildgalerie: %s' % title
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')										# Home-Button
	
	fname = make_filenames(title)			# Ablage: Titel + Bildnr
	fpath = '%s/%s' % (SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li	

	image=0; background=False; path_url_list=[]; text_list=[]
	for rec in content:
		# Hinw.: letzter Satz ist durch section sectionA begrenzt
		# PLog(rec)  # bei Bedarf
		thumb = BASE_URL + stringextract('class="img" src="', '"', rec)		
		if 	img_big == True:
			img_src = thumb[0:len(thumb)-5] + 'l.jpg'  # klein -> groß
		else:
			img_src = thumb
		
		if img_src == '':									# Sicherung			
			msg1 = 'Problem in Bildgalerie: Bild nicht gefunden'
			PLog(msg1)
		else:							
			title = stringextract('<img alt="', '"', rec)
			summ = stringextract('teasertext colCnt\">', '</p>', rec)
			tag=''
							
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
			local_path 	= "%s/%s" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d" % (image+1)
			label = title
			PLog("Bildtitel: " + title)
			title = unescape(title)
			
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		if os.path.isfile(local_path) == False:			# schon vorhanden?
			# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Bild-Url, 
			#	Zieldatei_kompletter_Pfad|Bild-Url ..
			path_url_list.append('%s|%s' % (local_path, img_src))

			if SETTINGS.getSetting('pref_watermarks') == 'true':
				txt = "%s\n%s\n%s\n%s\n" % (fname,title,tag,summ)
				text_list.append(txt)	
			background	= True											
								
		title=repl_json_chars(title); summ=repl_json_chars(summ)
		PLog('neu:');PLog(title);PLog(thumb);PLog(summ[0:40]);
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
		label = "SlideShow"	
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label=label, action="dirList", dirID="ardundzdf.ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
	
		lable = u"Alle Bilder löschen"									# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
# ----------------------------------------------------------------------
def XL_Live(ID=''):	
	PLog('XL_Live:')
	title = 'TagesschauXL Live'
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')									# Home-Button
		
	# json-Seiten ermittelt mit chrome-dev-tools von 
	# 	tagesschau.de/multimedia/livestreams/index.htm,
	#	tagesschau.de/multimedia/livestreams/livestream1/index.html (int.)
	path = "http://www.tagesschau.de/multimedia/livestreams/livestream-3-105~mediajson.json"
	if ID == "international":
		path = "http://www.tagesschau.de/multimedia/livestreams/livestream-1-101~mediajson.json"
	page, msg = get_page(path=path)
	PLog(page[:100])	

	if page == '':	
		msg1 = "Fehler in XL_Live:"
		msg2 = msg
		msg3 = "Fallback zu ARD_m3u8 (s. Log)" 
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		PLog(msg3)
		url_m3u8=''
	else:
		streams = blockextract('_stream":', page)
		for stream in streams:
			url_m3u8 = stringextract('_stream": "', '"', stream)
			if "master.m3u8" in url_m3u8:
				break

	if url_m3u8 == '':
		url_m3u8 = ARD_m3u8	
	
	thumb = stringextract('xl": "', '"', page)
	if thumb == '':
		thumb = ICON_LIVE
	if thumb.startswith('http') == False:
		thumb = BASE_URL + thumb
			
	PLog('url_m3u8: '+ url_m3u8); PLog('thumb: ' + thumb)	
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: ' + title)
		PlayVideo(url=url_m3u8, title=title, thumb=thumb, Plot=title)
		return
	
	li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=title,  sub_path='')	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
def Videoblogs(title, path):					# Videoblogs
	PLog('Videoblogs: ' + path)
	title2 = 'Videoblogs'
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')										# Home-Button
		
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in Videoblogs:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
	
	content =  blockextract('class="teaser" >',  page)
	PLog(len(content))
	if len(content) == 0:										# kein Ergebnis oder allg. Fehler
		msg1 = 'Videoblog-Seite leer. URL:'
		msg2 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
		
	for rec in content:	
		teaser_img = stringextract('src="', '"', rec) 	
		if teaser_img.startswith('http') == False:						
			teaser_img = BASE_URL + teaser_img
			
		mediabutton =  stringextract('class="multimediaButtons', '</div>', rec)	
		if mediabutton == '':									# keine direkten Videolinks?
			continue
		teaser_url = stringextract('href="', '"', mediabutton)		
		if teaser_url.startswith('http') == False:
			teaser_url =  BASE_URL + teaser_url	
			
		dachzeile 	= stringextract('dachzeile">', '<', rec) 	
		dachzeile 	= dachzeile.replace('"', '')
		headline 	= stringextract('headline">', '<', rec) 
		title		= "%s | %s" % (dachzeile, headline)
		
		teasertext 	= stringextract('teasertext">', '</strong>', rec) 
		teasertext	= cleanhtml(teasertext); teasertext = unescape(teasertext)
		summary 	= teasertext
		datum 	= stringextract('dachzeile datum">', '<', rec) 
		
		title = repl_json_chars(title)
		summary = repl_json_chars(summary)
		summ_par = summary.replace('\n','||')
		
		tagline = datum
		PLog('Satz:')
		PLog(title);PLog(summary[:80]);PLog(tagline);PLog(teaser_url);
		title=py2_encode(title); teaser_url=py2_encode(teaser_url);  summary=py2_encode(summary)
		teaser_img=py2_encode(teaser_img); tagline=py2_encode(tagline); summ_par=py2_encode(summ_par)				
		fparams="&fparams={'title': '%s', 'path': '%s', 'summary': '%s', 'thumb': '%s', 'tagline': '%s'}" %\
			(quote(title), quote(teaser_url), quote(summ_par),
			quote(teaser_img), quote(tagline))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetVideoSources", 
			fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams)				
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# Problem Texte (tagline, summary): hier umfangreicher, aber Verzicht, da mindestens 3 Seitenkonzepte.
# 	Wir übernehmen daher die Texte vom Aufrufer.
#  Seiten können sowohl Video- als auch Audio-Beiträge enthalten - für Kodi-Player keine getrennte
#	Behandlung erforderlich.  
def XLGetVideoSources(path, title, summary, tagline, thumb):
	PLog('XLGetVideoSources: ' + path)
	PLog(title); PLog(summary); PLog(tagline); 
	title_org = title
	summary_org = summary
	tagline_org = tagline
	summary = summary.replace('||', '\n')

	page, msg = get_page(path=path)				# Seite existiert nicht (mehr)?
	if page == '':	
		msg1 = "Fehler in XLGetVideoSources:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return 
	PLog(len(page))			
	
	if path.find('/multimedia/bilder/') > 0:					# kann nur Bildstrecke sein, kommt z.B. aus Suche
		li = Bildgalerie(path=path, title=title)
		return 
	if '/faktenfinder/kurzerklaert/' in  path:					# 1 Beitrag in class="infokasten small"
		href = stringextract('href="/multimedia/video/video-', '"', page)
		PLog(href)
		path = BASE_URL + "/multimedia/video/video-" + href
		PLog(path)
		XLGetVideoSources(path, title, summary, tagline, thumb) # nochmal
		return
	
	PLog('<fieldset>' in page)								# Download-Formate
	if '<fieldset>' not in page:							# Test auf Videos
		if page.find('magnifier_pos-0.html">') > 0 :	     # Einzelbild(er) vorhanden
			leftpos, leftstring = my_rfind('href=', 'magnifier_pos-0.html">', page)	
			PLog(leftstring)	
			gallery_url = BASE_URL + stringextract('href="', '"', leftstring) 
			li = Bildgalerie(path=gallery_url, title=title)
			return
		else:												
			msg1 = u'Das Video steht nicht (mehr) zur Verfügung.'	# weder Videos noch Einzelbilder - Abbruch	 			 	 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return	
		
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')										# Home-Button

	videoarea = stringextract('<fieldset>', '</fieldset>', page)		# div. Formate: mp3, ogg 
	# PLog(videoarea)
	videos = blockextract('<div class="button"', videoarea)		# auch Audio-Beiträge, Bsp. Politik im Radio
	PLog('videos %d' % len(videos))
	if len(videos) == 0:										# Seite mit fieldset aber ohne Videobuttons
		if page.find('class="icon video"') > 0 :	      		# möglich: Verweise auf ältere Beiträge
			leftpos, leftstring = my_rfind('href=', 'class="icon video"', page)	
			PLog("leftstring: " + leftstring)
			video_url = BASE_URL + stringextract('href="', '"', leftstring) # damit hierhin zurück
			XLGetVideoSources(path=video_url,title=title,summary=summary,tagline=tagline, thumb=thumb)
			return			

	# Sofortstart hier mit der letzten (größten) Qualität. master.m3u8 fehlt hier.
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: XLGetVideoSources')
		url = stringextract('href="', '"', videos[-1])
		if url.startswith('http') == False:
			if url.startswith('//'):			# href="//download.media.tagesschau.de/..
				url =  "https:" + url
			else:	
				url =  BASE_URL + url	
		Plot = "%s\n\n%s" % (tagline, summary)
		PlayVideo(url=url, title=title, thumb=thumb, Plot=Plot)
		return	
		
	mediatype=''	
	if SETTINGS.getSetting('pref_video_direct') == 'true': 
		mediatype='video'
		
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	for video in videos:
		PLog(video)
		video = stringextract('<div', '</div>', video)		# begrenzen
		title = stringextract('title="', '">', video)
		url = stringextract('href="', '"', video)
		if url.startswith('http') == False:
			if url.startswith('//'):			# href="//download.media.tagesschau.de/..
				url =  "https:" + url
			else:	
				url =  BASE_URL + url
		if '.mp3' in url or '.ogg' in url:			# Audio, Bsp. Politik im Radio
			title = stringextract('title="', '"', video) # Audio ohne /N im Titel
			title = 'Audio: ' + title
			summ = "%s\n%s\n%s" % (title_org, tagline, summary)
		else:		
			title = unescape(title)			# enthält /n
			PLog(title)
			typ=''; res=''; bw_video=''; bw_audio=''; mb=''
			title = title.split('\n')
			PLog(len(title))
			if len(title) == 5:
				video=title[0]; 
				res=title[1]; bw_video=title[2]; 
				bw_audio=title[3]; mb=title[4];
				# Bsp. Titel: Video: H.264/MPEG4 , 1280x720px, 3584kbps
				# Bsp. bw_audio + mb in summ: Audio: 192kbps, Stereo|Größe: 37 MB
				title = u"%s, %s, %s, %s" % (video, res, bw_video, bw_audio)	
				summ = "%s\n%s\n\n%s\n\n%s" % (title_org, tagline, summary, mb)
		summ_par = summ.replace('\n', '||')
		PLog('Satz:')
		PLog(title); PLog(url)
		if url:					
			download_list.append(title + '#' + url)			# Download-Liste füllen	
			title=py2_encode(title); url=py2_encode(url); img=py2_encode(thumb); summ_par=py2_encode(summ_par);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': ''}" %\
				(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
				mediatype=mediatype, summary=summ)
				
	if 	download_list:	# Downloadbutton(s), high=0: 1. Video = höchste Qualität	
		# Qualitäts-Index high: hier Basis Bitrate (s.o.)
		summary_org = repl_json_chars(summary_org)
		tagline_org = repl_json_chars(tagline_org)
		thumb = img
		# PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=0)  
	 	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------






