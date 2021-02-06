# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
#	Stand: 05.02.2021
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
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

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
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 

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
ARD_Archiv 		= 'https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-%s.html'	# 02.02.2021
ARD_Fakt		= 'https://www.tagesschau.de/investigativ/faktenfinder/'					# 02.02.2021
ARD_PolitikRadio= 'https://www.tagesschau.de/multimedia/politikimradio/index.html'
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
ICON_FAKT 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Faktenfinder.png?raw=true'
ICON_FAKT 		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Fakt.png?raw=true'
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
		
	mediatype='' 
	# --------------------------------- 						# Livestreams
	# Live: akt. PRG + vom Sender holen, json-Links in XL_Live
	# PRG gilt auch für die  intern. Seite			
	path = "http://www.tagesschau.de/multimedia/livestreams/index.html"
	page, msg = get_page(path=path)			
	if page == '':	
		msg1 = "Fehler in Main_XL:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
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

	# ---------------------------------							# in menu_hub Direktsprung zu XLGetSourcesHTML:
	tag = u"[B][COLOR red]Letzte Sendung[/COLOR][/B], zurückliegende Sendungen"		
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
	title = 'Faktenfinder'
	tag = u"häufig ohne Videos, dafür HTML-Auszüge. Für weitergehende Recherchen bitte  Quellen außerhalb des "
	tag = u"%sAddons verwenden" % tag
	fparams="&fparams={'title': '%s','path': '%s'}"  % (title, quote(ARD_Fakt)) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.Faktenfinder", fanart=ICON_MAINXL, 
		thumb=ICON_FAKT, tagline=tag, fparams=fparams)
	title = 'Politik im Radio'
	tag = u"Audiobeiträg"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_PolitikRadio), 'ARD_PolitikRadio', quote(ICON_RADIO))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_RADIO, tagline=tag, fparams=fparams)
	title = '#kurzerklärt'
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_kurz), 'ARD_kurz', quote(ICON_KURZ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_KURZ, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# 01.02.2021 Seitenlayout der Nachrichtenseiten durch ARD geändert, Videoquellen 
#	nun auf der Webseite als quoted json eingebettet, Direktsprung zu XLGetSourcesHTML 
#	entfällt - Auswertung nun über vorgeschaltete Funktion XLSinglePage ->
#	XLGetSourcesJSON
#
def menu_hub(title, path, ID, img):	
	PLog('menu_hub:')
	PLog(title); PLog(path); PLog(img)

	if ID=='ARD_Archiv':						# Vorschaltung Kalendertage (1 Monat)
		Archiv(path=path, ID=ID, img=img) 		# Archiv: Callback nach hier, dann weiter zu get_content
		return	

	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in menu_hub:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 		
	page = py2_decode(page)
	
	# Direktsprünge zu Url der Sendungseite - der Rest der Seiten enthält vorwiegend gleiche Inhalte 
	# aus dem Archiv
	if ID=='ARD_100' or ID=='ARD_Last' or ID=='ARD_20Uhr' or ID=='ARD_Gest' or ID=='ARD_tthemen' or ID=='ARD_Nacht':
		XLSinglePage(title,thumb=img,ID=ID,path='',page=page)
		return
		
	if ID == 'ARD_kurz':							# #kurzerklärt -> Search
		query = "kurzerklaert"
		XL_Search(query, pagenr='')
		return

	# Seiten mit unterschiedlichen Archiv-Inhalten - ARD_bab, ARD_Archiv, ARD_Blogs,
	#	ARD_PolitikRadio, ARD_Bilder, ARD_kurz, BASE_FAKT
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')			# Home-Button
	
	li = get_content(li, page, ID=ID, path=path)
	
	# Archiv 'Bericht aus Berlin': enthält weitere Beiträge eines Monats (java-script -
	#	hier nicht zugänglich, s. id="monthselect") 
	if ID == 'ARD_bab':							# 3 Buttons aus Sendungsarchiv anhängen
		ressort = stringextract('ressort">Sendungsarchiv', '</ul>', page)
		hreflist = blockextract('<a href', ressort)
		for link in hreflist:
			PLog("Archiv: " + link)
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
# menu_hub, ID's: ARD_100, ARD_Last, ARD_20Uhr, ARD_Gest, ARD_tthemen,ARD_Nacht
# Seitenaufbau identisch, die Videoquellen befinden sich im Abschnitt
#	data-ts_component='ts-mediaplayer' als quoted json
# letzte Sendung ist doppelt - von  der 1. Variante werden nur die Themen 
#	erfasst (-> summ)
# 
# ----------------------------------------------------------------------
def XLSinglePage(title,thumb, summ='', tag='', ID='',path='',page=''):
	PLog('XLSinglePage:'); PLog(ID);
	img = thumb
	
	if page == '':						# ID Search
		page, msg = get_page(path=path)	
		if page == '':	
			msg1 = "Fehler in XLSinglePage:"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return 		
	page = py2_decode(page)

	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')			# Home-Button

	items = blockextract('list-element__teaserinfo', page) 
	PLog(len(items))
	themen = stringextract('video__details">', '</div>', page)
	themen = repl_json_chars(themen)
	themen = cleanhtml(mystrip(themen)); 
	
	cnt=0;  
	for item in items:
		href = stringextract('href="', '"', item)
		title = stringextract('__headline">', '</h3', item)
		title = mystrip(title); title = cleanhtml(title); 
		datum = stringextract('_topline">', '</', item)
		if datum == '':
			datum = stringextract('__date">', '</', item)
		datum.strip()
		
		if cnt == 0:							# letzte Sendung
			title = "[B][COLOR red]%s[/COLOR][/B]: letzte Sendung" % title
			datum = "[B][COLOR red]%s[/COLOR][/B]" % datum
			summ = themen; summ_par = summ.replace('\n', '||')
		else:
			themen=''; summ=''									# entf. bei zurückl.  Sendungen
			if datum:											# fehlt bei TSchau100
				title = "%s: %s" % (title, datum)
		
		tag = datum
		
		PLog('Satz1:')
		PLog(title);PLog(summ[:80]);PLog(tag);PLog(href);
		title=py2_encode(title); href=py2_encode(href);  summ=py2_encode(summ)
		img=py2_encode(img); tag=py2_encode(tag); summ_par=py2_encode(summ_par)	
		fparams="&fparams={'title': '%s', 'path': '%s', 'summ': '%s', 'thumb': '%s', 'tag': '%s'}" %\
			(quote(title), quote(href), quote(summ_par), quote(img), quote(tag))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetSourcesJSON", 
			fanart=img, thumb=img, summary=summ, tagline=tag, fparams=fparams)				
		cnt=cnt+1
		
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
		
		ipath =  ARD_Archiv % SendDate
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
def XL_Search(query='', pagenr=''):
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
		MyDialog(msg1, msg2, '')	
		return 
	
	if u'leider erfolglos. Bitte überprüfen Sie Ihre Eingabe' in page:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
		msg1 = u'Keine Beiträge zu: %s' % query  
		MyDialog(msg1, '', '')
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
def get_content(li, page, ID, mark='', path=''):	
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
		content =  blockextract('class="teaser"', page, '</ul>')
		more = stringextract('>Weitere Audios<', 'googleon: index', page)
		more_list = blockextract('<a href=', more)
		content = content + more_list			# Weitere Audios anhängen
	

	PLog(len(page)); PLog(len(content));
	if len(content) == 0:										# kein Ergebnis oder allg. Fehler
		msg1 = 'Keine Inhalte gefunden.' 						# 
		msg2 = u'Bitte die Seite im Web überprüfen.'		
		msg3 = path
		if page.find('"title">' + msg2) >= 0:
			msg3 = u'Bitte versuchen Sie es später noch einmal.'					
		MyDialog(msg1, msg2, msg3)	
		return
		
	base_url = BASE_URL
	func = "XLGetSourcesHTML"									# Default Zielfunktion
	if ID=="ARD_Archiv_Day" or  ID=="Search":					
		func = "XLGetSourcesJSON"

	mediatype='' 												# 04.02.2021 entf. hier		
	#if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Kennz. Video für Sofortstart 
	#	mediatype='video'


	cnt = 0
	for rec in content:	
		cnt = cnt +1											# Satz-Zähler						
		teaser_img = ''												
		teaser_img = stringextract('src="', '"', rec) 	
		if teaser_img.find('http://') == -1:					# ohne http://	bei Wetter + gelöschten Seiten		
			teaser_img = base_url + teaser_img
		teaser_url = stringextract('href="', '"', rec)			# 1. Stelle <a href=
		if teaser_url.startswith('http') == False:
			teaser_url =  base_url + teaser_url				
		PLog(teaser_img); PLog(teaser_url)
		
		# keine Multimedia-Beiträe:	
		if 'twitter' in teaser_url or 'facebook' in teaser_url  or 'instagram' in teaser_url:	
			PLog('skip: url_skiplist')
			continue
		if teaser_url.endswith('.de') or  teaser_url.endswith('.de/'):
			PLog('Sender-/Studio-Link: skip')
			continue
			 
			
		# hier relevante ID-Liste. ID's mit Direktsprüngen (s. menu_hub) haben XLGetSourcesHTML als Callback:
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
			if headline == '':												# zusätzl. Liste "Weitere Audios"
				teasertext = "Weitere Audios"
				headline = stringextract('<a', '</li>', rec)				
				teaser_url = stringextract('<a href="', '"', rec)
				headline = headline.replace(teaser_url,'')
				headline = cleanhtml(headline); 
				headline = headline.replace('href="">','')
				teaser_url = BASE_URL + teaser_url
				teaser_img = R(ICON_MAIN_POD)
			
		if ID=='ARD_Archiv_Day':
			headlineclass = stringextract('headline">', '</h4>', rec)			# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			teasertext = stringextract('class="teasertext ">', '</p>', rec).strip()	# Teasertext mit url + Langtext, 
			teasertext = stringextract('html">', '</a>', teasertext)		# Text hinter url, nach | folgt typ
			if teasertext == '':											# leer: tagesschau vor 20 Jahren
				teasertext = headline		
			dachzeile = stringextract('dachzeile">', '</p>', rec)		
			tagline = dachzeile
			headline = "%s: %s" % (headline, dachzeile[-9:])	# Titel mit Uhrzeit
			
		PLog('pre_Satz3:')
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
			
		PLog('Satz3:')
		PLog(teaser_img);PLog(teaser_url);PLog(title);PLog(summary[:80]);PLog(tagline);
		PLog(ID); PLog(func)
		title=py2_encode(title); gallery_url=py2_encode(gallery_url)
		teaser_url=py2_encode(teaser_url);  summary=py2_encode(summary)
		teaser_img=py2_encode(teaser_img); tagline=py2_encode(tagline); summ_par=py2_encode(summ_par)				
		fparams="&fparams={'title': '%s', 'path': '%s', 'summ': '%s', 'thumb': '%s', 'tag': '%s', 'ID': '%s'}" %\
			(quote(title), quote(teaser_url), quote(summ_par), quote(teaser_img), quote(tagline), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.%s" % func, 
			fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams, mediatype=mediatype)				
	return li

# ----------------------------------------------------------------------
# 02.02.2021 Wegfall Bildergalerien:
# def XL_Bildgalerie(path, title):	
	
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
		MyDialog(msg1, msg2, msg3)
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
# Abweichende Struktur der HTML-Seite 
#	
#
def Faktenfinder(title, path):								# Faktenfinder
	PLog('Faktenfinder: ' + path)
	XLCacheTime = 3600										# 1 Std.	
	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
		
	page = Dict("load", 'XL_FAKT', CacheTime=XLCacheTime)					
	if page == False:										# nicht vorhanden oder zu alt
		page, msg = get_page(path)		
		if page == '':	
			msg1 = u"Fehler in Faktenfinder"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
		else:	
			Dict("store", 'XL_FAKT', page) 					# Seite -> Cache: aktualisieren		

	items=[]
	block  = blockextract('class="teaser__link"',  page, 'div class="columns')
	PLog(len(block))
	if len(block) > 0:
		items = items + block
	block  = blockextract('class="list-element__link"',  page, ">Alle Meldungen")
	PLog(len(block))
	if len(block) > 0:
		items = items + block
	block  = blockextract('class="list-element__teaserinfo',  page, '"class="footer"')
	PLog(len(block))
	if len(block) > 0:
		items = items + block
	PLog(len(items))
		
	old_href=[]; cnt=0
	for item in items:	
		href = stringextract('href="', '"', item)
		if href in old_href:
			continue
		old_href.append(href)
		if '__headline' not in item:						# skip Kurzform mit ts-picture__wrapper				
			continue
		if 'ts-image js-image' in item:
			img = stringextract('src="', '"', item)
		else:
			img = ICON_FAKT	
		page_local='' 										# Satz ohne Videodaten
		if "component='ts-mediaplayer" in item:				# mit Videodaten
			#player = stringextract('data-ts_component=', '</div>', item)
			Dict("store", 'XLFakt_%s' % cnt, item) 			# XLGetSourcesJSON lädt
			page_local = 'XLFakt_%s' % cnt
			
		title = stringextract('__headline">', '</', item)
		title = mystrip(title); title = cleanhtml(title); 
		title = unescape(title); title = repl_json_chars(title)
		tag = stringextract('__topline">', '</', item)
		summ = stringextract('_shorttext">', '</', item)
		summ = mystrip(summ); summ = repl_json_chars(summ)
		summ = cleanhtml(summ);
		summ_par = summ.replace('\n', '||')
						
		PLog('Satz4:')
		PLog(title);PLog(summ[:80]);PLog(tag);PLog(href);
		title=py2_encode(title); href=py2_encode(href);  summ=py2_encode(summ)
		img=py2_encode(img); tag=py2_encode(tag); summ_par=py2_encode(summ_par);
		page_local=py2_encode(page_local)				
		fparams="&fparams={'title': '%s', 'path': '%s', 'summ': '%s', 'thumb': '%s', 'tag': '%s', 'page_local': '%s'}" %\
			(quote(title), quote(href), quote(summ_par), quote(img), quote(tag), quote(page_local))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetSourcesJSON", 
			fanart=img, thumb=img, summary=summ, tagline=tag, fparams=fparams)				
		cnt=cnt+1
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# Aufrufer XLSinglePage - s. dort, Nutzung der Streamlisten-Funktionen
# 	in Haupt-PRG und ARD Neu
# page_local kann einen lokalen Seitenausschnitt enthalten (Dict) - 
#	z.B. Fakentfinder
#
def XLGetSourcesJSON(path, title, summ, tag, thumb, page_local='', ID=''):
	PLog('XLGetSourcesJSON: ' + title)
	title_org = title
	tagline = tag; summary =summ 
	
	if page_local:								# Seitenausschnitt 
		page = Dict("load", page_local)
	else:
		page, msg = get_page(path=path)				# Seite existiert nicht (mehr)?
	if page == '':	
		msg1 = "Fehler in XLGetSourcesJSON:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 
	PLog(len(page))			
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')					# Home-Button
	
	# -----------------------------------------			# Extrakt Videoquellen
	player = stringextract("component='ts-mediaplayer", 'class="player">', page)
	data = stringextract("data-config='", "'", player)	# quoted json
	PLog(data[:100])
	if data == '':
		if '__topline' in page and '__headline' in page:
			msg = get_content_text(page, title, summ, tag,)	# Textausgabe statt Video
			return
		else:
			msg1 = u"Keine Videoquellen gefunden für:"
			msg2 = "%s" % title
			MyDialog(msg1, msg2, '')	
			return 
		
	data = unescape(data)
	PLog(data[:100])
	PLog(data[-100:])
	#RSave('/tmp/XL_VideoSources.json', py2_encode(data))					

	page = data
	#link_img = stringextract('_previewImage":"', '",', page) # ev. nur Mediatheksymbol
	thumb = stringextract('xl":"', '"', page) 				# ev. nur Mediatheksymbol
	geoblock =  stringextract('geoblocked":', ',', page)	# Geoblock-Markierung ARD
	sub_path = stringextract('_subtitleUrl":"', '"', page)
	if geoblock == 'true':									# Geoblock-Anhang für title, summary
		geoblock = ' | Geoblock: JA'
		title = title + geoblock
	else:
		geoblock = ' | Geoblock: nein'
	dauer = stringextract('duration":"', '"', page)
	dauer = seconds_translate(dauer)
	
	tagline = "%s | Dauer: %s" % (tagline, dauer)
	if summary:	
		tagline = "%s\n\n%s" % (tagline, summary)
		
		
	tagline = "Titel: %s\n\n%s" % (title_org, tagline)	# Titel neu in Streamlists_buttons
	Plot = tagline.replace('\n', '||')
	
	PLog('Satz2:')
	PLog(title); PLog(dauer); PLog(geoblock);  PLog(tagline);

	PLog('import_ARDnew:');								# ARDStartVideoHLSget, ARDStartVideoMP4get
	import resources.lib.ARDnew as ARDnew
	VideoUrls = blockextract('_quality', page)
	PLog(len(VideoUrls))
	
	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	HBBTV_List=''										# nur ZDF
	HLS_List = ARDnew.ARDStartVideoHLSget(title, VideoUrls)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = ARDnew.ARDStartVideoMP4get(title, VideoUrls)	# Extrakt MP4
	Dict("store", 'TXL_HLS_List', HLS_List) 
	Dict("store", 'TXL_MP4_List', MP4_List) 
	PLog("download_list: " + str(MP4_List)[:80])
	PLog(str(MP4_List))
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_ready:');
	ID = ""; HOME_ID = 'TagesschauXL'; 
	ID = 'TXL'; 
	build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ------------------------			
def get_content_text(page, title, summ, tag,):					# Textausgabe statt Video
	PLog('get_content_text: ' + title)

	show_text=[]; 
	show_text_title = "ohne Video | %s" % title
	
	pos = page.find("<!-- Boxen unten -->")						# Rest abschneiden
	page = page[:pos]
	page = mystrip(page)
	
	item_list=[]							
	meldungskopf = stringextract('class="meldungskopf', 'list-element__date', page)
	item_list.append(meldungskopf)										# Hauptmeldung	
	
	meldungen = blockextract('"list-element__date">', page, "picture class")		
	PLog(len(meldungen))											# weitere Meldungen
	item_list= item_list + meldungen
	PLog(len(item_list))									

	for item in item_list:
		PLog(item[:200])
		PLog('Mark0')
		datum = stringextract('_date">', '</', item)				# 1. Kopfdaten
		if datum ==  '':
			datum = stringextract('datetime">', '</', item)			# Meldungskopf
		topline = stringextract('_topline">', '</', item)
		headline = stringextract('_headline">', '</', item)
		if "meldungskopf_" in item:									# Meldungskopf
			headline = stringextract('_headline--text">', '</', item)
			
		headline = cleanhtml(headline); headline = py2_decode(headline)
		headline = unescape(headline)
		datum=mystrip(datum);topline=mystrip(topline);
		headline=mystrip(headline); 
		
		absatztitle = u"%s | %s | %s\n" % (datum, topline, headline)
		if datum == '':
			PLog(topline); PLog(headline);
			absatztitle = u"%s | %s | %s\n" % (title, tag, summ)
		show_text.append(absatztitle)
		PLog('Satz5:')
		PLog(datum); PLog(topline);PLog(headline);PLog(title); PLog(absatztitle)
		
		#------------------
		absatz=''; 
		absatz_list = blockextract('class="m-ten', item, "</p>")	# 2. Absätze
		PLog(len(absatz_list))
		for line in absatz_list:
			line = stringextract('twelve">', '</', line)
			line = mystrip(line)
			PLog(line[:80])
			absatz = "%s\n%s\n" % (absatz, line)
		
		show_text.append(absatz)
		
	PLog('Mark1')
	PLog(len(show_text))	
	PLog(str(show_text))

	show_text = "\n".join(show_text)
	show_text = cleanhtml(show_text)
	ShowText(path='', title=show_text_title, page=show_text)
	return

# ----------------------------------------------------------------------
# Problem Texte (tagline, summary): hier umfangreicher, aber Verzicht, da mindestens 3 Seitenkonzepte.
# 	Wir übernehmen daher die Texte vom Aufrufer.
#  Seiten können sowohl Video- als auch Audio-Beiträge enthalten - für Kodi-Player keine getrennte
#	Behandlung erforderlich. 
# 03.02.2021 neu: Videoquellen erreichbar als json-Datei via player_id (Kopfbereich html-Seite) 
# 
def XLGetSourcesHTML(path, title, summ, tag, thumb, ID=''):
	PLog('XLGetSourcesHTML: ' + path)
	PLog(title); PLog(summ); PLog(tag); PLog(ID);
	title_org = title
	tagline = tag; summary =summ 
	thumb_org = thumb

	page, msg = get_page(path=path)
	# Bsp. ../multimedia/video/video-813379~ardplayer.html:
	player_id = stringextract('/multimedia/video/video-', '~ardplayer.html', page)
	PLog("player_id: " + player_id)
	
	if player_id == '':										# o. Video, nach Audio suchen
		player = stringextract('player:stream"', '/>', page)
		url = stringextract('content="', '"', player)
		Plot = "%s\n\n%s" % (tag, summ)
		PlayVideo(url, title, thumb, Plot)
		return

	media_base = "https://www.tagesschau.de/multimedia/video/video-%s~mediajson.json"
	path = media_base % player_id
	page, msg = get_page(path=path, JsonPage=True)

	if page == '':	
		msg1 = u"Keine Videoquellen gefunden für:"
		msg2 = "%s" % title
		msg3 = msg
		MyDialog(msg1, msg2, msg3)	
		return 
	PLog(len(page))
	
	# wir verwenden nur _plugin":1 (skip .f4m-Formate in _plugin":0, s. 
	#	ARDStartSingle:
	page = page.replace('\n', '')							# anpassen an übl. Format	
	page = page.replace('": ', '":')				
	Plugin1 = page.split('_plugin":1')[1]
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
	
# ----------------------------------------------------------------------
	# Rest bei Gelegenheit mit XLGetSourcesJSON zusammenführen:
	#link_img = stringextract('_previewImage":"', '",', page) # ev. nur Mediatheksymbol
	thumb = stringextract('xl":"', '"', page) 				# ev. nur Mediatheksymbol
	if thumb == '':
		thumb = stringextract('xs":"', '"', page) 
	if thumb.startswith('http') == False:
		thumb = BASE_URL + thumb
	geoblock =  stringextract('geoblocked":', ',', page)	# Geoblock-Markierung ARD
	sub_path = stringextract('_subtitleUrl":"', '"', page)
	if geoblock == 'true':									# Geoblock-Anhang für title, summary
		geoblock = ' | Geoblock: JA'
		title = title + geoblock
	else:
		geoblock = ' | Geoblock: nein'
	dauer = stringextract('duration":"', '"', page)
	dauer = seconds_translate(dauer)
	
	tagline = "%s | Dauer: %s" % (tagline, dauer)
	if summary:	
		tagline = "%s\n\n%s" % (tagline, summary)
		
		
	tagline = "Titel: %s\n\n%s" % (title_org, tagline)	# Titel neu in Streamlists_buttons
	Plot = tagline.replace('\n', '||')
	
	PLog('Satz2:')
	PLog(title); PLog(dauer); PLog(geoblock);  PLog(tagline);

	PLog('import_ARDnew:');								# ARDStartVideoHLSget, ARDStartVideoMP4get
	import resources.lib.ARDnew as ARDnew
	VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))
	
	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	HBBTV_List=''										# nur ZDF
	HLS_List = ARDnew.ARDStartVideoHLSget(title, VideoUrls)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = ARDnew.ARDStartVideoMP4get(title, VideoUrls)	# Extrakt MP4
	Dict("store", 'TXL_HLS_List', HLS_List) 
	Dict("store", 'TXL_MP4_List', MP4_List) 
	PLog("download_list: " + str(MP4_List)[:80])
	PLog(str(MP4_List))
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_ready:');
	ID = ""; HOME_ID = 'TagesschauXL'; 
	ID = 'TXL'; 
	build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	 	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------






