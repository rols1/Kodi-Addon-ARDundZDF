# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
# 	<nr>9</nr>								# Numerierung für Einzelupdate
#	Stand: 20.08.2023
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
ARD_Fakt		= 'https://www.tagesschau.de/faktenfinder'					# 30.04.2023
Podcasts_Audios	= 'https://www.tagesschau.de/multimedia/audio'
ARD_Investigativ='https://www.tagesschau.de/investigativ'					# 10.06.2021
ARD_Bilder		= 'https://www.tagesschau.de/multimedia/bilder/index.html'	# 05.05.2023


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

	# ---------------------------------							# -> menu_hub -> XL_LastSendung -> get_content_json
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
		
	# ---------------------------------							
	title = 'Bericht aus Berlin'								# -> menu_hub -> ARDnew.get_json_content
	tag = u"In Berichten, Interviews und Analysen beleuchtet <Bericht aus Berlin> politische Sachthemen und die Persönlichkeiten, die damit verbunden sind."
	fparams="&fparams={'title': '%s','path': '%s', 'ID': '%s'}"  %\
		(quote(title), quote(ARD_bab), 'ARD_bab')
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.menu_hub", fanart=ICON_MAINXL, 
		thumb=ICON_BAB, tagline=tag, fparams=fparams)
		
	# ---------------------------------							# -> get_VideoAudio	-> get_content_json		
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

	title = 'Blickpunkte'
	tag = u"Bilder des Tages und Bildergalerien. Blickpunkte auf das aktuelle Geschehen in aller Welt. Nachrichten in Bildern auf tagesschau.de."
	fparams="&fparams={'title': '%s','path': '%s'}"  %\
		(quote(title), quote(ARD_Bilder))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_BilderCluster", fanart=ICON_MAINXL, 
		thumb=ICON_BILDER, tagline=tag, fparams=fparams) 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# 01.02.2021 Seitenlayout der Nachrichtenseiten durch ARD geändert, Videoquellen 
#	nun auf der Webseite als quoted json eingebettet, Direktsprung zu XLGetSourcesHTML 
#	entfällt - Auswertung nun über vorgeschaltete Funktion XL_LastSendung ->
#	XLGetSourcesJSON
# 15.04.2023 get_page_content -> get_content_json 
#
def menu_hub(title, path, ID, show=""):	
	PLog('menu_hub : + ID')
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
	
	# 
	if ID == 'ARD_bab':								# 14.02.2023 umgestellt auf api.ardmediathek.de
		mark=''; ID="XL_menu_hub"
		li = xbmcgui.ListItem()
		li = home(li, ID='TagesschauXL')			# Home-Button
		li = get_json_content(li, page, ID, mark)	# -> ARDnew
	
	
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
# Bildcluster der Webseite listen (Wetterbilder, Bilder des Tages..)
# 	Bilder entweder in json eingebettet  (data-v=..) oder in html-tags
#	Cluster -> XL_BilderClusterSingle
# 	
def XL_BilderCluster(title, path):
	PLog('XL_BilderCluster:')

	page, msg = get_page(path=path, GetOnlyRedirect=True)	
	path = page								
	page, msg = get_page(path)	
	if page == '':	
		msg1 = u"Fehler in XL_BilderCluster"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li

	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')									# Home-Button
		
	cluster =  blockextract('class="trenner trenner--default', page)
	PLog(len(cluster))
	img = R(ICON_DIR_FOLDER)
	for item in cluster:
		title = stringextract('<h2>', '</h2>', item)					# topline kann entfallen
		title=py2_encode(title); path=py2_encode(path)
		fparams="&fparams={'title': '%s','path': '%s'}"  %\
			(quote(title), quote(path))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_BilderClusterSingle", 
			fanart=ICON_BILDER, thumb=img, fparams=fparams)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		

# ----------------------------------------------------------------------

def XL_BilderClusterSingle(title, path):
	PLog('XL_BilderClusterSingle: ' + title)
	title_org=title

	page, msg = get_page(path=path, GetOnlyRedirect=True)	
	path = page								
	page, msg = get_page(path)	
	if page == '':	
		msg1 = u"Fehler in XL_BilderClusterSingle"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	cluster =  blockextract('class="trenner trenner--default', page)	# Cluster suchen
	mycluster=""
	for item in cluster:
		title = stringextract('<h2>', '</h2>', item)
		if title in title_org:
			mycluster = item
			PLog("cluster_found: " + title)
			break
	
	# Format img_list: "Titel || img_url || img_alt || summ"	
	img_list=[]; cnt=0
	if '<div data-v="' in mycluster:										# json
		PLog("content_json:")
		cnt=cnt+1
		conf = stringextract('data-v="', '"', mycluster)	
		conf = conf.replace('\\"', '"')
		conf = conf.replace('&quot;', '"')
		conf = unquote(conf)
		obj = json.loads(conf)
		PLog(str(obj)[:60]);
	
		name = obj["name"]
		imgObjects = obj["images"]
		PLog("imgs_in_Block_%d: %d" % (cnt, len(imgObjects)))
		for img in imgObjects:
			summ=""
			img_url = img["imageUrls"]["l"]
			img_alt = img["alttext"]
			summ = img["description"]
			summ=summ.replace(u'&lt;strong&gt;', '')					# html-Rest in json
			summ=summ.replace(u'&lt;/strong&gt;', '')				# html-Rest in json
			title = img["title"]
			line = "%s||%s||%s||%s" % (title, img_url, img_alt, summ)
			img_list.append(line)
	else:
		PLog("content_html:")		
		items = blockextract('ts-picture__wrapper', mycluster, "</noscript>")
		cnt=0
		for item in items:
			summ=""
			cnt=cnt+1
			title = "%s: Bild %d" % (title_org, cnt)
			img_alt = stringextract('alt="', '"', item)
			img_last  = blockextract('data-srcset=', item)[-1] 			# größtes Bild
			img_url = stringextract('data-srcset="', '"', img_last)
			line = "%s||%s||%s||%s" % (title, img_url, img_alt, summ)
			img_list.append(line)
			PLog(line)
			
	PLog("img_list: %d" % len(img_list))
	if len(img_list) > 0:
		XL_BilderShow(title, img_list)
	
	return
# ----------------------------------------------------------------------	 
def XL_BilderShow(title, img_list):
	PLog("XL_BilderShow:")
	title_org=title
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')									# Home-Button

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
			
	cnt=0; background=False; path_url_list=[]; text_list=[]
	for line in img_list:
		cnt=cnt+1
		title, img_url, img_alt, summ = line.split("||")
		title = make_filenames(title) 					# Umlaute möglich
		local_path 	= "%s/%s.jpg" % (fpath, title)		# Kodi braucht Endung (ohne Prüfung) 
		if len(title) > 70:
			title = "%s.." % title[:70]					# Titel begrenzen
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		PLog(local_path)
		if os.path.isfile(local_path) == False:			# schon vorhanden?
			# path_url_list (int. Download): 
			#	Zieldatei_kompletter_Pfad|Bild-Url ..
			PLog(local_path); PLog(img_url)
			PLog(type(local_path)); PLog(type(img_url))
			path_url_list.append('%s|%s' % (local_path, img_url))

			if SETTINGS.getSetting('pref_watermarks') == 'true':
				txt = "%s\n%s\n%s\n%s\n%s" % (fname,title_org,title,img_alt,summ)
				PLog("Mark6")
				text_list.append(txt)	
			background	= True											

		title=repl_json_chars(title); summ=repl_json_chars(summ)
		PLog('new_img:');PLog(title);PLog(img_url);PLog(thumb);PLog(summ[0:40]);
		if thumb:	
			local_path=py2_encode(local_path);
			fparams="&fparams={'path': '%s', 'single': 'True'}" % quote(local_path)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_SlideShow", 
				fanart=thumb, thumb=local_path, fparams=fparams, tagline=img_alt, summary=summ)

	if background and len(path_url_list) > 0:				# Übergabe Url-Liste an Thread
		from threading import Thread	# thread_getfile
		textfile=''; pathtextfile=''; storetxt=''; url=img_url; 
		fulldestpath=local_path; notice=True; destdir="Slide-Show-Cache"
		now = datetime.datetime.now()
		timemark = now.strftime("%Y-%m-%d_%H-%M-%S")
		folder = fname 
		background_thread = Thread(target=thread_getpic,
			args=(path_url_list,text_list,folder))
		background_thread.start()
			
	if cnt > 0:		
		fpath=py2_encode(fpath);
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
		
		lable = u"Alle Bilder löschen"						# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, tagline=img_alt, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)	

# ----------------------------------------------------------------------	 
def XL_Search(query='', pagenr=''):
	PLog("XL_Search: " + pagenr)
	
	if 	query == '':	
		query = get_query(channel='ARD')
	PLog(query)
	if  query == None or query.strip() == '':
		return Main_XL()		# sonst Wiedereintritt XL_Search bei Sofortstart, dann Absturz Addon
	query_org = query	
	query=py2_decode(query)		# decode, falls erf. (1. Aufruf)

	ID='Search'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	else:
		pagenr = int(pagenr)
	
	path1 =  "https://www.tagesschau.de/json/search?searchText=%s&documentType=video&pageIndex=%d" % (query, pagenr)
	path2 =  "https://www.tagesschau.de/json/search?searchText=%s&documentType=audio&pageIndex=%d" % (query, pagenr)
	page1, msg = get_page(path=path1)	 
	page2, msg = get_page(path=path2)	 
	if not page1 and not page2:	
		msg1 = "Fehler in XL_Search:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 	

	jsonObject1 = json.loads(page1)
	jsonObject2 = json.loads(page2)
	PLog(str(jsonObject1)[:80])
	if len(jsonObject1["documentTypes"][0]["items"]) == 0 and len(jsonObject2["documentTypes"][0]["items"]) == 0:
		msg1 = u'nichts gefunden'
		msg2 = query
		icon = R(ICON_MAINXL)		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("%s: %s" % (msg1, msg2))
		return
		
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
	
	docObject1 = jsonObject1["documentTypes"][0]
	docObject2 = jsonObject2["documentTypes"][0]
	cnt1 = docObject1["count"]
	cnt2 = docObject2["count"]
	PLog("cnt1: %d, cnt2: %d" % (cnt1, cnt2))
	items1 = docObject1["items"]
	items2 = docObject2["items"]
	PLog("items1: %d, items2: %d" % (len(items1), len(items2)))
	
	try:
		item1 = docObject1["items"][0]
		PLog(str(item1)[:80])
	except:
		cnt1=0
	try:
		item2 = docObject2["items"][0]
	except:
		cnt2=0
	
	if len(items1):
		title = "[B]Videos: Seite %d[/B]" % pagenr
		img = get_img(item1)		# Bild 1. Beitrag
		url = BASE_URL + item1["url"]
		tag = "Folgeseiten | zu den Videos" 
	
		query=py2_encode(query); url=py2_encode(url)
		fparams="&fparams={'url': '%s', 'query': '%s', 'typ': 'VIDEO'}" %\
			(quote(path1), quote(query))					# hier Such-Url11 -> XL_SearchContent
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_SearchContent", 
			fanart=img, thumb=img, tagline=tag, fparams=fparams)
			
	if len(items2):
		title = "[B]Audios: Seite %d[/B]" % pagenr
		img = get_img(item2)		# Bild 1. Beitrag
		url = BASE_URL + item2["url"]
		tag = "Folgeseiten | zu den Audios"
	
		query=py2_encode(query); url=py2_encode(url)
		fparams="&fparams={'url': '%s', 'query': '%s', 'typ': 'AUDIO'}" %\
			(quote(path2), quote(query))					# hier Such-Url2 -> XL_SearchContent
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_SearchContent", 
			fanart=img, thumb=img, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)			
	
# ----------------------------------------------------------------------	 
def XL_SearchContent(url, query, typ):
	PLog("XL_SearchContent: " + url)

	page, msg = get_page(path=url)	 
	if not page:	
		msg1 = "Fehler in XL_SearchContent:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 	
	pagenr = url.split("pageIndex=")[-1]
	PLog("pagenr: " + pagenr)

	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
	
	jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
	items = jsonObject["documentTypes"][0]["items"]
	
	for item in items:
		tag=""; summ=""
		title = item["headline"]
		#img = get_img(item)								# bei Videos sehr häufig fehlend
		img = ICON_MAINXL
		if "datetime" in item:
			tag = "Sendedatum: " + item["datetime"]
		tag = "%s | weiter zum [B]%s[/B]" % (tag, typ)
		if "description" in item:
			summ = item["description"] 
		url = BASE_URL + item["url"]
		
		title = repl_json_chars(title); summ = repl_json_chars(summ);
		url=py2_encode(url); title=py2_encode(title); 		
		fparams="&fparams={'title': '%s','path': '%s'}"  %\
			(quote(title), quote(url))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
			fanart=img, thumb=img, tagline=tag, summary=summ, fparams=fparams)
	
	# Mehr-Seiten - ohne Berechnung
	tag = u"nächste Seite, aktuell: %s" % pagenr
	nextpage = str(int(pagenr) + 1)
	PLog("nextpage: %s" % nextpage) 
	title = "Mehr: [B]%s[/B]" % query
	query=py2_encode(query);
	fparams="&fparams={'query': '%s', 'pagenr': '%s'}" % (quote(query), nextpage)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Search", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)			
	
# ----------------------------------------------------------------------
def get_img(item):	
	PLog('get_img:')
	PLog(str(item)[:60])
	try:
		img = item["teaserImage"]["urlM"]	
	except:
		img = R(ICON_DIR_FOLDER)
	return img
	
# ----------------------------------------------------------------------

# todo: intern. Livesteream separieren 

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
		player = players[0]								# Default: nation. Stream
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
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Sofortstart
		PLog('Sofortstart: ' + title)
		PlayVideo(url=url_m3u8, title=title, thumb=thumb, Plot=title, live="true")
		return
	
	li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=title,  live='true')	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# json-Daten im data-v-Block
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
	
	content =  blockextract('class="v-instance" data-v="', page, '</div>')
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
# 
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
		if len(img.split(".")) < 4:						# Endung fehlt
			img = img + ".webp"
	except Exception as exception:
		PLog("get_img_error: " + str(exception))
		img = R(ICON_DIR_FOLDER)		

	title=obj["mediadescription"]						# leer möglich
	if title.strip() == "":								# Altern.
		title = stringextract('av_content":"', '"', conf)
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
# Bau HBBTV_List (leer), HLS_List, MP4_List via Modul ARDnew
# page -> json 
# 01.05.2023 z.Z. nicht genutzt - häufige Beiträge mit nur 1 Stream
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





