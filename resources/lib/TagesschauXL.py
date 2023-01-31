# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
# 	<nr>5</nr>								# Numerierung für Einzelupdate
#	Stand: 28.01.2023
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

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('TagesschauXL_python_3.x.x')
	ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

NAME			= 'ARD und ZDF'
BASE_URL 		= 'https://www.tagesschau.de'
ARD_m3u8 		= 'https://tagesschau-lh.akamaihd.net/i/tagesschau_1@119231/master.m3u8' # intern. Link
ARD_100 		= 'https://www.tagesschau.de/100sekunden/index.html'
ARD_Last 		= 'https://www.tagesschau.de/sendung/letzte-sendung/index.html'
ARD_20Uhr 		= 'https://www.tagesschau.de/sendung/tagesschau/index.html'
ARD_Gest 		= 'https://www.tagesschau.de/sendung/tagesschau_mit_gebaerdensprache/index.html'
ARD_tthemen 	= 'https://www.tagesschau.de/sendung/tagesthemen/index.html'
ARD_Nacht 		= 'https://www.tagesschau.de/sendung/nachtmagazin/index.html'
ARD_bab 		= 'https://www.tagesschau.de/bab/index.html'
ARD_Archiv 		= 'https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-%s.html'	# 02.02.2021
ARD_Fakt		= 'https://www.tagesschau.de/investigativ/faktenfinder/'					# 02.02.2021
Podcasts_Audios	= 'https://www.tagesschau.de/multimedia/audio'
ARD_kurz 		= 'https://www.tagesschau.de/faktenfinder/kurzerklaert/index.html'
BASE_FAKT		='https://faktenfinder.tagesschau.de'										
ARD_Investigativ='https://www.tagesschau.de/investigativ/'									# 10.06.2021


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
ICON_Investig	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Investigativ.png?raw=true'
ICON_Themen		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau-Themen.png?raw=true'
# ---------------------------------------------------------------------- 
# 			
def Main_XL():
	PLog('Main_XL:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
				
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'gesucht wird in [B]ARD[/B] (nicht in tagesschau.de allein)'
		title=py2_encode(title);
		func = "resources.lib.TagesschauXL.Main_XL"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARD", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=ICON_MAINXL, 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)

	title="Suche auf www.tagesschau.de"
	summ = "Suche Sendungen und Videos auf www.tagesschau.de"
	fparams="&fparams={'query': ''}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Search", fanart=ICON_MAINXL, 
		thumb=R(ICON_SEARCH), fparams=fparams)
		
	mediatype='' 
	# --------------------------------- 						# Livestreams
	# Live: akt. PRG + vom Sender holen, json-Links in XL_Live
	# PRG gilt auch für die  intern. Seite			
	path = "https://www.tagesschau.de/multimedia/livestreams/index.html"
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in Main_XL:"
		msg2 = msg
		msg3 = u"Livestreams nicht verfügbar"
		MyDialog(msg1, msg2, msg3)	
		#return 												# ohne Livestreams weiter
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
		
	title = 'Investigativ'
	tag = u"Investigative Inhalte der ARD - aufwändig recherchierte Beiträge und Exclusivgeschichten der "
	tag = u"%sPolitik-Magazine Monitor, Panorama, Report und Kontraste. " % tag
	fparams="&fparams={'title': '%s','path': '%s'}"  % (quote(title), quote(ARD_Investigativ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
		fanart=ICON_MAINXL, thumb=ICON_Investig, tagline=tag, fparams=fparams)
	
	title = 'Faktenfinder'
	tag = u"Die faktenfinder - das Verifikationsteam der ARD - untersuchen Gerüchte, stellen Falschmeldungen "
	tag = u"%srichtig und liefern Hintergründe zu aktuellen Themen." % tag
	fparams="&fparams={'title': '%s','path': '%s'}"  % (title, quote(ARD_Fakt)) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
		fanart=ICON_MAINXL, thumb=ICON_FAKT, tagline=tag, fparams=fparams)
		
	title = 'Podcasts und Audios'
	tag = u"Audiobeiträge"
	ID = "Audios"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(Podcasts_Audios), ID, quote(ICON_RADIO))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Audios", fanart=ICON_MAINXL, 
		thumb=ICON_RADIO, tagline=tag, fparams=fparams)
		
	title = '#kurzerklärt'
	tag = u"kompakte Hintergrundinfos zu Nachrichtenthemen"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
		(quote(title), quote(ARD_kurz), 'ARD_kurz', quote(ICON_KURZ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_KURZ, tagline=tag, fparams=fparams)
		
	title = 'Weitere Themen'									# weitere Themen der Startseite
	tag = u"Startseiten: Inland, Ausland, Wirtschaft"
	fparams="&fparams={'title': '%s','path': '', 'menu': ''}"  % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Themen", fanart=ICON_MAINXL, 
		thumb=ICON_Themen, tagline=tag, fparams=fparams)

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
	#	Podcasts_Audios, ARD_Bilder, ARD_kurz, BASE_FAKT
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
def XLSinglePage(title, thumb, summ='', tag='', ID='', path='', page=''):
	PLog('XLSinglePage:'); PLog(ID);
	img = thumb; title_org = title
	
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

	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	# 2 Varianten: "ts-mediaplayer" (häufig Audio), 'ts-mediaplayer' (häufig Video):
	items =  blockextract('ts_component="ts-mediaplayer"', page)
	PLog(len(items))
	items =  items + blockextract("ts_component='ts-mediaplayer'", page)
	PLog(len(items))
	base_url = BASE_URL
	
	themen = stringextract('video__details">', '</div>', page)	# Themen 1. Sendung -> summ
	themen = repl_json_chars(themen)
	themen = cleanhtml(mystrip(themen)); 
	
	cnt=0;  
	for item in items:
		conf = stringextract("data-config='", "'", item)				# json-Daten mit mp3-Link
		conf = conf.replace('\\"', '"')
		conf = conf.replace('&quot;', '"')
		
		teaser_img = stringextract('"xs":"', '"', conf)					# häufig gleich				
		if teaser_img == '':
			teaser_img = stringextract('"m":"', '"', conf)
		if teaser_img.startswith('http') == False:
			teaser_img = base_url + teaser_img

		href = stringextract('href="', '"', item)
		if href == '':							# Link fehlt im 1. item, aus 2. item entnommen
			href = stringextract('href="', '"', items[1])
		title = stringextract('__headline">', '</', item)
		title = mystrip(title); title = cleanhtml(title); 
		datum = stringextract('_topline">', '</', item)
		if datum == '':
			datum = stringextract('__date">', '</', item)
		datum = mystrip(datum)
		
		if cnt == 0:							# letzte Sendung
			title = "[B][COLOR red]%s[/COLOR][/B]" % title_org + ": letzte Sendung"
			datum = "[B][COLOR red]%s[/COLOR][/B]" % datum
			summ = themen; summ_par = summ.replace('\n', '||')
		else:
			themen=''; summ=''									# entf. bei zurückl.  Sendungen
			if datum:											# fehlt bei TSchau100
				title = "%s: %s" % (title, datum)
		
		tag = datum; img = thumb
		tag = mystrip(tag)
		
		PLog('Satz1:')
		PLog(title);PLog(summ[:80]);PLog(tag);PLog(href);
			
		Dict_ID = 'XLSinglePage_%d' % cnt						# Dict hier vertretbar (kleine Listen) -
		Dict("store", Dict_ID, conf) 							#	anders: get_VideoAudio
		title=py2_encode(title); href=py2_encode(href);  summ=py2_encode(summ)
		teaser_img=py2_encode(teaser_img); tag=py2_encode(tag); summ_par=py2_encode(summ_par)
		
		fparams="&fparams={'title': '%s', 'Dict_ID': '%s', 'Plot': '%s', 'img': '%s'}" %\
			(quote(title), Dict_ID, quote(summ_par), quote(teaser_img))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetSourcesPlayer", 
			fanart=teaser_img, thumb=teaser_img, tagline=tag, fparams=fparams, mediatype=mediatype, 
			summary=summ)
			
						
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
		return Main_XL()		# sonst Wiedereintritt XL_Search bei Sofortstart, dann Absturz Addon
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
		li = xbmcgui.ListItem()									# Kontext-Doppel verhindern
		PLog("pagenr: " + str(pagenr))
		title 	= u"Weitere Beiträge zu [B][COLOR red]%s[/COLOR][/B]" % query_org
		summ 	= "Insgesamt: %s Treffer, Seiten: %d," % (searchResult, MaxPages) 
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
	if ID=='ARD_bab' or ID=='ARD_Bilder':
		content =  blockextract('class="teaser">', page)
	if ID=='ARD_Blogs' or ID=='ARD_kurz'  or ID=='ARD_Archiv_Day':
		content =  blockextract('class="teaser" >', page)
		base_url = BASE_FAKT
	

	PLog(len(page)); PLog(len(content));
	if len(content) == 0:										# kein Ergebnis oder allg. Fehler
		msg1 = 'Keine Inhalte gefunden.' 						# 
		msg2 = u'Bitte die Seite im Web überprüfen.'		
		msg3 = path
		MyDialog(msg1, msg2, msg3)	
		return
		
	base_url = BASE_URL
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
		# Search, ARD_bab, ARD_Archiv, Podcasts_Audios, ARD_Bilder, ARD_kurz 
		teasertext='';	headline=''; dachzeile=''; teaser_typ=''; teaser_date=''
		gallery_url='';	tagline=''; mp3_url=''; onlyGallery=False							
		if ID=='Search':
			teasertext = stringextract('class="teasertext ">', '</p>', rec).strip()	# Teasertext mit url + Langtext, 
			teasertext = teasertext.replace('|&nbsp;', '')
			teasertext = cleanhtml(teasertext)	
			
			dachzeile = stringextract('dachzeile">', '</p>', rec).strip()		# Dachzeile mit url + Typ + Datum
			dachzeile = cleanhtml(dachzeile)							
			teaser_typ =  stringextract('<strong>', '</strong>', dachzeile)
			teaser_date =  stringextract('</strong>', '</a>', dachzeile)
			tagline = teaser_typ + teaser_date
			headlineclass = stringextract('headline">', '</h3>', rec).strip()	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			
			teasertext = "%s | %s" % (dachzeile, teasertext.strip())
			PLog(teasertext[:80])
				
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
			onlyGallery=True											# kein Hybrid-Satz
			gallery_url =  base_url + stringextract('href="', '"', rec)	# 1. Stelle <a href=
			headlineclass = stringextract('headline">', '</h4>', rec).strip()	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			teasertext = stringextract('title="', '"', rec)				# Bildtitel als teasertext
			teaserdate = stringextract('class="teasertext">', '|&nbsp', rec)  # nur Datum
			tagline = teaserdate
			
		if ID=='ARD_Archiv_Day':
			headlineclass = stringextract('headline">', '</h4>', rec)	# Headline mit url + Kurztext
			headline = stringextract('html">', '</a>', headlineclass)
			teasertext = stringextract('class="teasertext ">', '</p>', rec).strip()	# Teasertext mit url + Langtext, 
			teasertext = stringextract('html">', '</a>', teasertext)	# Text hinter url, nach | folgt typ
			if teasertext == '':										# leer: tagesschau vor 20 Jahren
				teasertext = headline		
			dachzeile = stringextract('dachzeile">', '</p>', rec)		
			tagline = dachzeile
			headline = "%s: %s" % (headline, dachzeile[-9:])			# Titel mit Uhrzeit
			
		PLog('pre_Satz3:')
		PLog(teaser_url); PLog(headline); PLog(teasertext[:80]);  		
		PLog(dachzeile);	PLog(teaser_typ); PLog(teaser_date);		
			
		title = headline; title = repl_json_chars(title)
		title = mystrip(title); title = unescape(title)	
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
		PLog(ID); PLog(mp3_url); 
		title=py2_encode(title); gallery_url=py2_encode(gallery_url)
		teaser_url=py2_encode(teaser_url);  summary=py2_encode(summary)
		teaser_img=py2_encode(teaser_img); tagline=py2_encode(tagline); summ_par=py2_encode(summ_par)	
		
		if mp3_url:														# mp3-Quelle bereits bekannt
			ID='TagesschauXL'
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(mp3_url), 
				quote(title), quote(teaser_img), quote_plus(summ_par), ID)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.AudioPlayMP3", fanart=teaser_img, thumb=teaser_img, 
				fparams=fparams, summary=summary)
			
		else:															# -> XLGetSourcesHTML / XLGetSourcesJSON
			mediatype=''												# (direkt -> PlayVideo)
			if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Kennz. Video für Sofortstart 
				mediatype='video'	
				
			if ID=="ARD_Archiv_Day" or  ID=="Search":					# ohne ts-mediaplayer in Webseite				
				func = "XLGetSourcesPlayer"
				Dict_ID=teaser_url										# XLGetSourcesPlayer lädt conf von Zielseite
				fparams="&fparams={'title': '%s', 'Dict_ID': '%s', 'Plot': '%s', 'img': '%s'}" %\
					(quote(title), Dict_ID, quote(summ_par), quote(teaser_img))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.%s" % func, 
					fanart=teaser_img, thumb=teaser_img, fparams=fparams, mediatype=mediatype, summary=summary)
			else:									
				func = "XLGetSourcesHTML"								# Default Zielfunktion
				fparams="&fparams={'title': '%s', 'path': '%s', 'summ': '%s', 'thumb': '%s', 'tag': '%s', 'ID': '%s'}" %\
					(quote(title), quote(teaser_url), quote(summ_par), quote(teaser_img), quote(tagline), ID)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.%s" % func, 
					fanart=teaser_img, thumb=teaser_img, summary=summary, tagline=tagline, fparams=fparams, 
					mediatype=mediatype)				
	return li

# ----------------------------------------------------------------------
# 02.02.2021 Wegfall Bildergalerien:
# def XL_Bildgalerie(path, title):	
	
# ----------------------------------------------------------------------
# Übersicht Podcasts + einz. Audios auf www.tagesschau.de/multimedia/audio/
#	(1. Aufruf mit ID="Audios"
# path: einz. Podcastseiten, z.B. podcasts/faktenfinder-feed-101.html 
#	(2. Aufruf mit ID=Podcasts und path)
# 05.11.2021 Link-Button zu Audiothek-Tagesschau-Podcasts
#
def XL_Audios(title, ID, img,  path=''):	
	PLog('XL_Audios:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')									# Home-Button
	
	if path == '':														# ID = "Audios"
		path = Podcasts_Audios
		
	page, msg = get_page(path=path, GetOnlyRedirect=True)	
	path = page								
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in XL_Audios:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 
	PLog(len(page));
	
	items=[]
	items =  blockextract('class="teaser__link"', page)				# Podcasts-Übersichten
	items =  items + blockextract('component="ts-mediaplayer"', page)
	PLog(len(page));
	
	
	dest_func = "ardundzdf.AudioSenderPrograms"						# -> Audiothek-Tagesschau-Podcasts
	path = "https://api.ardaudiothek.de/organizations"
	tag = "weiter zu den Podcasts der ARD-Audiothek"
	path=py2_encode(path);
	fparams="&fparams={'dest_func': '%s', 'path': '%s'}" % (dest_func, quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Link", 
		fanart=ICON_MAINXL, thumb=R(ICON_DIR_FOLDER), fparams=fparams, tagline=tag)
		

	base_url = BASE_URL
	for item in items:
		if '>Unser Podcast-Angebot<' in item:						# Feeds html/itunes
			continue
			
		if 'class="teaser__link"' in item:							# Podcasts
			mp3_url=''
			href = stringextract('href="', '"', item)	
			teaser_img = stringextract('data-srcset="', '"', item)	# 1. (kleines Bild)
			if teaser_img.startswith('http') == False:
				teaser_img = base_url + teaser_img
			
			# topline = stringextract('teaser__topline">', '<', rec)# mal Rubrik, mal Podcast	
			headline = stringextract('__headline">', '<', item)
			headline = unescape(headline)
			headline = "%s: %s" % ("Podcast", headline)	
			
			teasertext = stringextract('teaser__shorttext">', '</p>', item)
			teasertext = cleanhtml(teasertext); teasertext = mystrip(teasertext)
			
		if 'component="ts-mediaplayer"' in item:						# Audios
			conf = stringextract("data-config='", "'", item)			# json-Daten mit mp3-Link
			conf = unescape(conf); conf = conf.replace('\\"', '"')
			conf = conf.replace(':""', ':"')						# Titelstart mit "
			teaser_img = stringextract('"xs":"', '"', conf)			# immer gleich				
			if teaser_img == '':
				teaser_img = stringextract('"m":"', '"', conf)
			if teaser_img.startswith('http') == False:
				teaser_img = base_url + teaser_img
			headline =  stringextract('"title":"', '",', conf)
			mp3_url =  stringextract('"url":"', '"', conf)			# Audios (download-Url)
			dur =  stringextract('"duration":"', '"', conf)			# sec, Kurzbeiträge
			dur = "%s sec" % dur									# 	Alt.: seconds_translate
			teasertext = "%s | Dauer %s" % (headline, dur)
	
		title = unescape(headline); title = repl_json_chars(title)
		summary = unescape(teasertext.strip())
		summary = cleanhtml(summary); summary = repl_json_chars(summary)
		summ_par = summary.replace('\n','||')
		
		PLog('Satz4:')
		PLog(teaser_img);PLog(mp3_url);PLog(title);PLog(summary[:80]);
		PLog(ID);

		title=py2_encode(title); summary=py2_encode(summary);
		teaser_img=py2_encode(teaser_img); summ_par=py2_encode(summ_par)			
		
		if mp3_url:													# Podcasts -> XL_Audios, 2. Aufruf
			tag = "[COLOR red]%s[/COLOR]" % "Audio"
			mp3_url=py2_encode(mp3_url);
			ID='TagesschauXL'										# ID Homebutton
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(mp3_url), 
				quote(title), quote(teaser_img), quote_plus(summ_par), ID)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.AudioPlayMP3", fanart=teaser_img, thumb=teaser_img, 
				fparams=fparams, tagline=tag, summary=summary)
				
		else:														# Audios -> AudioPlayMP3 (play + download)
			fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','img': '%s'}"  %\
				(quote(title), quote(href), ID, quote(teaser_img))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Audios", fanart=teaser_img, 
				thumb=teaser_img, fparams=fparams, tagline="Folgeseiten",  summary=summary)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
# ----------------------------------------------------------------------
# Wrapper für Funktionsaufrufe
def XL_Link(dest_func, path):	
	PLog('XL_Link:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')							# Home-Button
	
	if "AudioSenderPrograms" in dest_func:
		page, msg = get_page(path=path)	
		if page == '':	
			msg1 = "Fehler in XL_Audios:"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return 
		PLog(len(page));
		
		sender = "Tagesschau"
		img = ICON_MAINXL		# github
		AudioSenderPrograms(li, page, sender, img)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# weitere Themen der Startseite
# 1. step: Menüs der Startseite listen
# 2. step (path, menu): Untermenüs listen 
def XL_Themen(title, path, menu=''):	
	PLog('XL_Themen:')
	PLog(menu)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')							# Home-Button
	
	menu_list = [
					u'/inland/|Startseite Inland', u'/ausland/|Startseite Ausland',
					u'/wirtschaft/|Startseite Wirtschaft',
				]
	PLog(len(menu_list))
	skip_list = [u'Podcast', u'Investigativ', u'Wetter', 'Wahlergebnisse', 
				u'Audios',]
	
	if menu == '':												# Step 1 Menüs der Startseite listen
		for item in menu_list:
			href, title = item.split('|')
			href = BASE_URL + href
			PLog('Satz7:')
			PLog(title);PLog(href);
			title=py2_encode(title); href=py2_encode(href); 
			fparams="&fparams={'title': '%s','path': '%s', 'menu': '%s'}"  %\
				(quote(title), quote(href), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Themen", 
				fanart=ICON_MAINXL, thumb=ICON_Themen, fparams=fparams)
					
	# -----------------											# Step 2 Untermenüs listen 
	
	else:
		page, msg = get_page(path=path)
		if page == '':	
			msg1 = "Fehler in XL_Themen:"
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return 	
			
		menu_list = blockextract('class="header__navigation__list">', page,  '</ul>') # Hamb.-Menü Web
		block=[]; img_src=R(ICON_DIR_FOLDER)
		for block in menu_list:
			found=False
			if '/">%s<' % menu in block:
				PLog('gefunden: >%s<' % menu)
				found=True
				break
		
		items = blockextract('list__item">', block, '</li>')
		PLog(len(items))
		for item in items:
			href =  stringextract('href="', '"', item)
			title = stringextract('/">', '</a', item)
			title = unescape(title)
			
			PLog('Satz8:')
			PLog(title);PLog(href);
			title=py2_encode(title); href=py2_encode(href); 
			fparams="&fparams={'title': '%s','path': '%s'}"  % (title, quote(href)) 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
				fanart=ICON_MAINXL, thumb=img_src, tagline='Folgeseiten', fparams=fparams)						
		
		
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
	path = "https://www.tagesschau.de/multimedia/livestreams/livestream-3-105~mediajson.json"
	if ID == "international":
		path = "https://www.tagesschau.de/multimedia/livestreams/livestream-1-101~mediajson.json"
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
# Abweichende Struktur der HTML-Seite (Daten im ts-mediaplayer-Block)
#
def get_VideoAudio(title, path):								# Faktenfinder
	PLog('get_VideoAudio: ' + path)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
		
	page, msg = get_page(path)		
	if page == '':	
		msg1 = u"Fehler in get_VideoAudio"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
				
	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	# 2 Varianten: "ts-mediaplayer" (häufig Audio), 'ts-mediaplayer' (häufi Video):
	content =  blockextract('"ts-mediaplayer"', page)
	PLog(len(content))
	content =  content + blockextract("'ts-mediaplayer'", page)
	PLog(len(content))
	base_url = BASE_URL
		
	cnt = 0; url_list=[]
	for rec in content:
		cnt = cnt +1													# Satz-Zähler						
		path =  stringextract('href="', '"', rec)						# Zielseite
			
		conf = stringextract("data-config='", "'", rec)					# json-Daten mit media-Links
		conf = conf.replace('\\"', '"')
		conf = conf.replace('&quot;', '"')
		conf = unescape(conf)
		teaser_img = stringextract('"xs":"', '"', conf)					# immer gleich				
		if teaser_img == '':
			teaser_img = stringextract('"m":"', '"', conf)
		if teaser_img.startswith('http') == False:
			teaser_img = base_url + teaser_img
			
		#title =  stringextract('"title":"', '"', conf)					# Clip-Titel (stimmt nicht mit Web überein)
		img_title =  stringextract('"_title":"', '"', conf)				# Bildtitel -> tag
		h3_teaser = stringextract('<h3 class="teaser', '</h3>', rec)    # Titelvarianten
		h3_teaser = unescape(h3_teaser)
		teaser1 = stringextract('topline">', '</span>', h3_teaser)
		teaser2 = stringextract('headline">', '</span>', h3_teaser)		# kann </span> im Titel enthalten
		title = "%s: [B]%s[/B]" % (teaser1, teaser2)
		title = cleanhtml(title)
		title = mystrip(title); 	 
		title = unescape(title); title = repl_json_chars(title)
		
		typ =  stringextract('"_type":"', '"', conf)
		typ_org = typ
		typ = "[COLOR red]%s[/COLOR]" % up_low(typ)
		url =  stringextract('"url":"', '"', conf)						# Videos, Audios
		if url in url_list:
			continue
		else:
			url_list.append(url)
		
		dur =  stringextract('"duration":"', '"', conf)					# sec
		dur = "%s sec" % dur
		
		sub_path	= stringextract('_subtitleUrl":"', '"', conf)
		geoblock 	= stringextract('geoblocked":', ',', conf)
		if geoblock == 'true':										# Geoblock-Anhang für title, summary
			geoblock = 'Geoblock: JA'
		else:
			geoblock = 'Geoblock: nein'
		
		tag = "%s | Bild: %s" % (typ, img_title)
		teasertext = "Dauer %s | %s" % (dur, geoblock)
		
		PLog(conf[:80])
		
		teasertext = repl_json_chars(teasertext); teasertext = unescape(teasertext);
		summ = "%s\n\n%s" % (tag, teasertext)	
		summ_par=summ.replace('\n', '||'); 
		
		PLog('Satz6:')
		PLog(title);PLog(path);PLog(teaser_img);PLog(typ);PLog(title);
		PLog(summ[:80]); 
		
		title=py2_encode(title); url=py2_encode(url); 
		summ_par=py2_encode(summ_par); teaser_img=py2_encode(teaser_img); 
			
		if typ_org == "audio":											# Audio
			ID='TagesschauXL'
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(url), 
				quote(title), quote(teaser_img), quote_plus(summ_par), ID)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.AudioPlayMP3", fanart=teaser_img, thumb=teaser_img, 
				fparams=fparams, summary=summ)
				
		if typ_org == "video":											# Video	
			#Dict_ID = 'get_VideoAudio_%d' % cnt						# bremst bei großen Listen (Dateisystem-abh.)
			#Dict("store", Dict_ID, conf) 
			Dict_ID = path												# XLGetSourcesPlayer holt conf neu
			fparams="&fparams={'title': '%s', 'Dict_ID': '%s', 'Plot': '%s', 'img': '%s'}" %\
				(quote(title), Dict_ID, quote(summ_par), quote(teaser_img))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XLGetSourcesPlayer", 
				fanart=teaser_img, thumb=teaser_img, fparams=fparams, mediatype=mediatype, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# holt Videoquellen aus data-config-Bereich des eingebetteten 
#	ts-mediaplayers, hier erneut geladen via Dict_ID
# Ev. vorh. Audioquelle wird sofort gestartet 
#  Sofortstart: Direktaufruf in build_Streamlists_buttons
# Dict_ID enthält path bei Aufruf aus get_content (ID's: ARD_Archiv_Day, 
#	Search - Webseiten ohne ts-mediaplayer)
#
def XLGetSourcesPlayer(title, Dict_ID, Plot, img):
	PLog('XLGetSourcesPlayer: ' + title)
	PLog(Dict_ID)
	
	if Dict_ID.startswith('http'):
		page, msg = get_page(path=Dict_ID)
		conf = stringextract("data-config='", "'", page)			# json-Daten mit Video-/Audio-Link
		conf = unescape(conf); conf = conf.replace('\\"', '"')
		if page == '' or conf == '':
			conf=False	
	else:	
		conf = Dict("load", Dict_ID)								# unescape durch Aufrufer
	PLog(conf[:80])
		
	if conf == False:
		msg1 = u"XLGetSourcesPlayer: Playerdaten nicht gefunden für"
		msg2 = title
		MyDialog(msg1, msg2, '')	
		return 
		
	typ =  stringextract('"_type":"', '"', conf)					# Ausleitung Audio
	if typ == "audio":
		Plot = Plot.replace("VIDEO", "AUDIO")
		url =  stringextract('"url":"', '"', conf)
		ID='TagesschauXL'
		AudioPlayMP3(url, title, img, Plot, ID)
		return
		
	base_url = BASE_URL
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button

	title =  stringextract('"title":"', '"', conf)
	title = title.replace('#', '*')							# # ist Trenner in title_href in StreamsShow
	PLog("title: " + title)
	typ =  stringextract('"_type":"', '"', conf)
	
	sub_path	= stringextract('_subtitleUrl":"', '"', conf)
	geoblock 	= stringextract('geoblocked":', ',', conf)
	if geoblock == 'true':										# Geoblock-Anhang für title, summary
		geoblock = ' | Geoblock: JA'
	else:
		geoblock = ' | Geoblock: nein'
	
	VideoUrls = blockextract('_quality', conf)
	PLog(len(VideoUrls))
	HLS_List,MP4_List,HBBTV_List = XLGetVideoLists(li, title, VideoUrls)

	if not len(HLS_List) and not len(MP4_List):
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li
							
	#----------------------------------------------- Abschluss wie XLGetSourcesJSON
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_Investigativ_ready:');
	ID = ""; HOME_ID = 'TagesschauXL'; 
	ID = 'TXL'; thumb=img; 
	Plot=Plot.replace('||', '\n')
	build_Streamlists_buttons(li,title,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# Bau HBBTV_List (leer), HLS_List, MP4_List via Modul ARDnew
#
def XLGetVideoLists(li, title, VideoUrls):					
	PLog('XLGetVideoLists:')
	PLog('import_ARDnew:');								# ARDStartVideoHLSget, ARDStartVideoMP4get
	import resources.lib.ARDnew as ARDnew

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

	return HLS_List,MP4_List,HBBTV_List
# ----------------------------------------------------------------------
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
		
		absatztitle = u"[COLOR red]%s | %s | %s[/COLOR]\n" % (datum, topline, headline)
		if datum == '':												# statt Datum tag + summ
			PLog(topline); PLog(headline);
			absatztitle = u"[COLOR red]%s | %s[/COLOR]\n\n%s\n" % (title, tag, summ)
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
	PLog(str(show_text)[:80])

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
	if '/multimedia/video/video-' in page:
		player_id = stringextract('/multimedia/video/video-', '.html', page)
		videolink = BASE_URL + '/multimedia/video/video-' + player_id + ".html"
		videolink = videolink.replace('~ardplayer', '')
		PLog("player_id: %s, videolink: %s" % (player_id, videolink))
		page, msg = get_page(path=videolink)	
	 	
	player = stringextract('player:stream"', '/>', page)
	player_url = stringextract('content="', '"', player)	# i.d.R. mp3-url
	Plot = "%s\n\n%s" % (tag, summ)
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true': # Sofortstart
		PLog('Sofortstart: XLGetSourcesHTML')
		PlayVideo(player_url, title, thumb, Plot)
		return

	if ID =="Podcasts_Audios":
		url = stringextract('title="MP3-Format', '>mp3<', page)
		url = stringextract('href="', '"', url)
		if url == '':										# Altermative
			url = stringextract('player:stream', '/>', page)
			url = stringextract('content="', '"', url)
		PLog('audio_url' + url)
		
		if url:
			ID='TagesschauXL'
			AudioPlayMP3(url, title, thumb, Plot=title, ID=ID)  	# direkt (ardundzdf.py)	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return

	media_base = "https://www.tagesschau.de/multimedia/video/video-%s~mediajson.json"
	player_id = player_id.replace('~ardplayer', '')
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
	 	
# ----------------------------------------------------------------------






