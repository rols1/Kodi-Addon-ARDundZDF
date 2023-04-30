# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
# 	<nr>7</nr>								# Numerierung für Einzelupdate
#	Stand: 30.04.2023
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
from resources.lib.ARDnew import get_json_content	# ARD_bab										
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
ARD_Last 		= 'https://www.tagesschau.de/multimedia'	# ARD_100,ARD_Last,ARD_20Uhr,ARD_Gest,ARD_tthemen,ARD_Nacht
ARD_bab 		= 'https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL2Rhc2Vyc3RlLmRlL2JlcmljaHQgYXVzIGJlcmxpbg?pageNumber=0&pageSize=12'
ARD_Fakt		= 'https://www.tagesschau.de/faktenfinder/'				# 30.04.2023
Podcasts_Audios	= 'https://www.tagesschau.de/multimedia/audio'
ARD_Investigativ='https://www.tagesschau.de/investigativ/'				# 10.06.2021


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
	'''
	title="Suche auf www.tagesschau.de"
	summ = "Suche Sendungen und Videos auf www.tagesschau.de"
	fparams="&fparams={'query': ''}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Search", fanart=ICON_MAINXL, 
		thumb=R(ICON_SEARCH), fparams=fparams)
	'''	
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
	tag = stringextract('<meta name="description" content="', '"', page)
		
	title = 'Livestream'
	tag = stringextract('<meta name="description" content="', '"', page)
	summ = u"[B][COLOR green]Livestream mit Sport (nur für Deutschland)[/COLOR][/B]"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Live", fanart=ICON_MAINXL, 
		thumb=ICON_LIVE, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)
		
	title = 'Livestream (diesen im Ausland verwenden)'
	tag = "[B]%s[/B]" % "Ohne Geoblocking"
	summ = "[B][COLOR green]Internationaler Livestream[/COLOR][/B]"
	fparams="&fparams={'ID': 'international'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Live", fanart=ICON_MAINXL, 
		thumb=ICON_LIVE, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)

	# ---------------------------------							# menu_hub -> XL_LastSendung
	tag = u"[B][COLOR red]Letzte Sendung[/COLOR][/B], zurückliegende Sendungen"	
	summ = u"Tagesschau und Tagesschau:\n..in 100 Sekunden\n..17:50 Uhr\n..20 Uhr\n..vor 20 Jahren.."	
	title = 'Tagesschau'
	show = "tagesschau"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s','show': '%s'}"  %\
		(quote(title), quote(ARD_Last), 'ARD_Last', show)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_LAST, fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)

	title = 'Tagesschau 20 Uhr (Gebärdensprache)'
	tag=""
	path = "https://www.tagesschau.de/multimedia/sendung/tagesschau_mit_gebaerdensprache"
	show = u"tagesschau mit Gebärdensprache"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s', 'show': '%s'}"  %\
		(quote(title), quote(path), "ARD_Gest", show)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_20GEST, fparams=fparams, tagline=tag, mediatype=mediatype)
		
	title = 'Tagesthemen'
	tag = "mit Videos zu einzelnen Themen"
	show = "tagesthemen"
	path = "https://www.tagesschau.de/multimedia/sendung/tagesthemen"
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s', 'show': '%s'}"  %\
		(quote(title), quote(path), "ARD_tthemen", show)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_TTHEMEN, fparams=fparams, tagline=tag, mediatype=mediatype)
		
	# ---------------------------------							# in menu_hub Direktsprung zu get_content:	
	title = 'Bericht aus Berlin'
	tag = u"In Berichten, Interviews und Analysen beleuchtet <Bericht aus Berlin> politische Sachthemen und die Persönlichkeiten, die damit verbunden sind."
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s'}"  %\
		(quote(title), quote(ARD_bab), 'ARD_bab')
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_BAB, tagline=tag, fparams=fparams)
		
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
	fparams="&fparams={'title': '%s','path': '%s'}"  %\
		(quote(title), quote(Podcasts_Audios))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", fanart=ICON_MAINXL, 
		thumb=ICON_RADIO, tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# 01.02.2021 Seitenlayout der Nachrichtenseiten durch ARD geändert, Videoquellen 
#	nun auf der Webseite als quoted json eingebettet, Direktsprung zu XLGetSourcesHTML 
#	entfällt - Auswertung nun über vorgeschaltete Funktion XL_LastSendung ->
#	XLGetSourcesJSON
# 15.04.2023 get_page_content -> get_json_content 
#
def menu_hub(title, path, ID, show=""):	
	PLog('menu_hub:')
	PLog(title); PLog(path); 

	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in menu_hub:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 		
	page = py2_decode(page)
	
	# Direktsprünge zu Url der Live-Sendungseiten  -> XL_LastSendung
	if ID=='ARD_100' or ID=='ARD_Last' or ID=='ARD_20Uhr' or ID=='ARD_Gest' or ID=='ARD_tthemen':
		XL_LastSendung(title, page, show=show)
		return

	# Seiten mit unterschiedlichen Archiv-Inhalten - ARD_bab, ARD_Archiv, ARD_Blogs,
	#	Podcasts_Audios, ARD_Bilder, ARD_kurz, BASE_FAKT
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')				# Home-Button
	
	# 
	if ID == 'ARD_bab':								# 14.02.2023 umgestellt auf api.ardmediathek.de
		mark=''; ID="XL_menu_hub"
		li = get_json_content(li, page, ID, mark)	# -> ARDnew
	else:
		li = get_content(li, page, ID=ID, path=path)
	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
# ----------------------------------------------------------------------
# menu_hub, ID's: ARD_100, ARD_Last, ARD_20Uhr, ARD_Gest, ARD_tthemen,ARD_Nacht
# Seitenaufbau identisch, die Videoquellen befinden sich im Abschnitt
#	data-ts_component='ts-mediaplayer' als quoted json
# letzte Sendung ist doppelt - von  der 1. Variante werden nur die Themen 
#	erfasst (-> summ)
# 
# ----------------------------------------------------------------------
def XL_LastSendung(title, page, show=""):
	PLog('XL_LastSendung:'); PLog(show);
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')			# Home-Button

	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'		

	items =  blockextract('class="v-instance" data-v="', page)
	PLog(len(items))
	
	for item in items:
		typ,av_typ,title,tag,summ,img,stream = get_content_json(item)
		if title.startswith(show):
			title=py2_encode(title); stream=py2_encode(stream); 
			summ=py2_encode(summ); img=py2_encode(img); 
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote(summ))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", 
				fanart=img, thumb=img, tagline=summ, fparams=fparams, mediatype=mediatype)
								
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
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	
	path =  "https://www.tagesschau.de/json/search?searchText=%s" % query 	# 30.04.2023
	page, msg = get_page(path=path, JsonPage=True)			# -> dump 
	if page == '':	
		msg1 = "Fehler in XL_Search:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 
	
	jsonObject = json.loads(page)
	PLog(len(jsonObject))
	cnt = jsonObject["totalEntriesCount"]
	PLog("cnt: %d" % cnt)
	if cnt == 0:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
		msg1 = u'Leider keine Beiträge zu: [B]%s[/B] gefunden' % query  
		MyDialog(msg1, '', '')
		return 	
	
	XL_SearchCluster(jsonObject, query)
	return

# ----------------------------------------------------------------------
def XL_SearchCluster(jsonObject, query):
	PLog("XL_SearchCluster:")
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
	
	# todo: "imageGallery" ergänzen:
	typ_list = ["video", "audio"]							# nicht: "all", "article"

	for objs in jsonObject["documentTypes"]:
		PLog(str(objs)[:60])
		
		summ=""
		typ = objs ["type"]
		cnt = objs["count"]
		PLog("cnt: %d" % cnt)
		if typ not in typ_list:
			continue

		for item in objs["items"]:
			PLog(str(item)[:60])
			headline = item["headline"]
			title = "[B]%s: [/B] %s" % (up_low(typ), headline)
			tag = "weiter zum Beitrag | Suche: %s" % query
			
			if "teaserImage" in item:						# kann fehlen
				img = item["teaserImage"]["urlM"]	
				img_alt = item["teaserImage"]["altText"]
				img_cr = item["teaserImage"]["imageRights"]
				summ = "Bild: %s | %s" % (img_alt, img_cr)
			else:
				img = R(ICON_DIR_FOLDER)	

			url = BASE_URL + item["url"]
		
			query=py2_encode(query); url=py2_encode(url)
			fparams="&fparams={'title': '%s', 'path': '%s'}" %\
				(quote(query), quote(url))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
				fanart=img, thumb=img, tagline=tag, summary=summ, fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
	
# ----------------------------------------------------------------------
# mark dient der Farbmarkierung bei ID='Search' 
# 14.02.2023 ARD_bab hier entfernt (umgestellt auf api, s. menu_hub)
#
def get_content(li, page, ID, mark='', path=''):	
	PLog('get_content:')
	PLog(len(page)); PLog(ID);
	
	if  ID=='Search' or ID=='ARD_Bilder':
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
		# Search, ARD_Archiv, Podcasts_Audios, ARD_Bilder, ARD_kurz 
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
def XL_Live(ID=''):	
	PLog('XL_Live:')
	title = 'TagesschauXL Live'
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')									# Home-Button
		
	path = "https://www.tagesschau.de/multimedia/livestreams/index.html"
	page, msg = get_page(path=path)

	if page == '' or "(Fehlernummer 404)" in page:	
		msg1 = "Fehler in XL_Live:"
		msg2 = msg
		msg3 = "Fallback zum Livestreamcache" 
		MyDialog(msg1, msg2, msg3)
		PLog(msg3)
		url_m3u8=''
	else:
		players = blockextract('class="v-instance" data-v="', page)
		PLog("players: %d" % len(players))
		player = players[0]
		if ID == "international":
			player = players[1]
		PLog(str(player[:80]))	

	conf = stringextract('data-v="', '"', player)		# json-Daten mit Streamlink
	conf = conf.replace('\\"', '"')
	conf = conf.replace('&quot;', '"')
	conf = unquote(conf)
	PLog(conf[:80])
	
	streams = stringextract('streams":[', ']', conf)
	url_m3u8 = stringextract('url":"', '"', streams)

	if url_m3u8 == '':
		ard_streamlinks = get_ARDstreamlinks()	# util
		for rec in ard_streamlinks:
			PLog(rec)
			if "tagesschau24" in rec:
				line = rec.split("|")
				ARD_m3u8 = line[1]
				break
				PLog ("ARD_m3u8:" + ARD_m3u8)
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
	
	page, msg = get_page(path=path, GetOnlyRedirect=True)	
	path = page								
	page, msg = get_page(path)	
	if page == '':	
		msg1 = u"Fehler in get_VideoAudio"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button

	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	content =  blockextract('class="v-instance" data-v="', page)
	PLog(len(content))
		
	cnt = 0; url_list=[]
	for item in content:
		cnt = cnt +1													# Satz-Zähler						
		typ,av_typ,title,tag,summ,img,stream = get_content_json(item)
				
		title=py2_encode(title); stream=py2_encode(stream); 
		summ=py2_encode(summ); img=py2_encode(img); 
			
		if typ == "audio":											# Audio
			ID='TagesschauXL'
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote_plus(summ), ID)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
				
		if typ == "video":											# Video	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(stream), 
				quote(title), quote(img), quote_plus(summ))
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.PlayVideo", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		

# ----------------------------------------------------------------------
def get_content_json(item):	
	PLog('get_content_json:')		
			
	minWidth=700					# .., 768x, 944x

	conf = stringextract('data-v="', '"', item)	
	conf = conf.replace('\\"', '"')
	conf = conf.replace('&quot;', '"')
	conf = unquote(conf)
	obj = json.loads(conf)
	PLog(str(obj)[:60]); 
	
	verf=""; url=""; stream=""; 
	tag=""; img=""

	typ = obj["playerType"]
	try:
		items = obj["pc"]["generic"]["imageTemplateConfig"]["size"]
		for item in items:
			width = item["minWidth"]; url = item["value"]	
			PLog(width);PLog(url)
			if int(width) >= minWidth:
				img=url
				break
			if img == "":
				img=url		# Fallback: letzte url
	except Exception as exception:
		PLog("get_img_error: " + str(exception))
		img = R(ICON_DIR_FOLDER)		

	title=obj["mediadescription"]
	title = repl_json_chars(title)
	
	# Streams: zu geringe Auswahl für Listen
	stream = obj["mc"]["streams"][0]["media"][0]["url"]		# 1. Url, m3u8 od. mp4, 
	
	tag = "[B]%s[/B]" % up_low(typ)
	summ = obj["mc"]["meta"]["title"]			
	summ = repl_json_chars(summ)
	av_typ = stringextract('av_content_type":"', '"', conf)
	
	PLog('Get_content typ: %s | av_typ: %s | title: %s | tag: %s | descr: %s |img:  %s | stream: %s' %\
		(typ,av_typ,title,tag,summ,img,stream) )		
	return typ,av_typ,title,tag,summ,img,stream		
	
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
		page, msg = get_page(path=Dict_ID)							# json-Daten mit Video-/Audio-Link
		conf = stringextract("data-config='", ',&quot;_sharing', page)	# quoted ohne Abschnitt services	
		conf = unescape(conf); conf = conf.replace('\\"', '"')
		conf = conf + '}}'											# json-komp.
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
		
	try:
		VideoObj = json.loads(conf)
		mediaArray = VideoObj["mc"]["_mediaArray"][0]
		StreamArray = mediaArray["_mediaStreamArray"]
		PLog("VideoObj: %d, mediaArray: %d, StreamArray: %d" % (len(VideoObj),len(mediaArray), len(StreamArray)))		
	except Exception as exception:
		PLog(str(exception))
		msg1 = u'keine Videoquellen gefunden'
		PLog(msg1)
		MyDialog(msg1, '', '')
		return
	
	HLS_List,MP4_List,HBBTV_List = XLGetVideoLists(li, title, StreamArray)

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
# page -> json 
def XLGetVideoLists(li, title, StreamArray):					
	PLog('XLGetVideoLists:')
	PLog('import_ARDnew:');								# ARDStartVideoHLSget, ARDStartVideoMP4get
	import resources.lib.ARDnew as ARDnew
	
	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	HBBTV_List=''										# nur ZDF
	HLS_List = ARDnew.ARDStartVideoHLSget(title, StreamArray)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = ARDnew.ARDStartVideoMP4get(title, StreamArray)	# Extrakt MP4
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






