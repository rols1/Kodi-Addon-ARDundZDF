# -*- coding: utf-8 -*-
################################################################################
#				TagesschauXL.py - Teil von Kodi-Addon-ARDundZDF
#				  Modul für für die Inhalte von tagesschau.de
################################################################################
# 	<nr>16</nr>								# Numerierung für Einzelupdate
#	Stand: 03.08.2024
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
ICON_DELETE 	= "icon-delete.png"

ICON_EINFACH	= "tagesschau_einfach.png"
ICON_REGIONAL	= "tagesschau_regional.png"

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

CurSender = 'tagesschau24:tagesschau24::tv-tagesschau24.png:tagesschau24'
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

	# ---------------------------------						# -> ARDnew -> get_json_content
	T_List = 	[u"tagesschau|%s|%s" % (ICON_LAST, "Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXU"),
				u"tagesschau Gebärdensprache|%s|%s" % (ICON_20GEST, "Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXUgbWl0IEdlYsOkcmRlbnNwcmFjaGU"),
				u"tagesschau in Einfacher Sprache|%s|%s" %  (R(ICON_EINFACH), "Y3JpZDovL3RhZ2Vzc2NoYXUyNC90YWdlc3NjaGF1LWluLWVpbmZhY2hlci1zcHJhY2hl"),
				u"tagesschau24|%s|%s" % (ICON_24, "Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2Vzc2NoYXUyNA"),
				u"tagesschau in 100 SEKUNDEN|%s|%s" % (ICON_100sec, "Y3JpZDovL2Rhc2Vyc3RlLmRlL3RzMTAwcw"),
				u"tagesthemen|%s|%s" % (ICON_TTHEMEN, "Y3JpZDovL2Rhc2Vyc3RlLmRlL3RhZ2VzdGhlbWVu"),
				u"Regionale Nachrichten|%s|%s" % (R(ICON_REGIONAL), "3mJgQ9gapwqrKZrrF9hTWo:-3801511732729640100"),
				u"Bericht aus Berlin|%s|%s" % (ICON_BAB, "Y3JpZDovL2Rhc2Vyc3RlLmRlL2JlcmljaHQgYXVzIGJlcmxpbg"),
				]
	for t in T_List:
		title, thumb, pid = t.split("|")
		PLog(title); PLog(thumb); PLog(pid)
		title = "[B]%s[/B]" % title
		tag = u"mit allen von der ARD angebotenen Stream-Qualitäten"
		title=py2_encode(title); pid=py2_encode(pid);
		fparams="&fparams={'title': '%s', 'pid': '%s'}"  % (quote(title), quote(pid))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_Tagesschau", 
		fanart=ICON_MAINXL, thumb=thumb, tagline=tag, fparams=fparams, mediatype="")
		
	# ---------------------------------							# -> get_VideoAudio	-> get_content_json		
	title = 'Investigativ'
	tag = u"Investigative Inhalte der ARD - aufwändig recherchierte Beiträge und Exclusivgeschichten der "
	summ = u"Hinweis: Videos nur in geringer Auflösung (480x270) vorhanden."
	tag = u"%sPolitik-Magazine Monitor, Panorama, Report und Kontraste. " % tag
	fparams="&fparams={'title': '%s','path': '%s'}"  % (quote(title), quote(ARD_Investigativ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
		fanart=ICON_MAINXL, thumb=ICON_Investig, tagline=tag, summary=summ, fparams=fparams)
	
	title = 'Faktenfinder'
	tag = u"Die faktenfinder - das Verifikationsteam der ARD - untersuchen Gerüchte, stellen Falschmeldungen "
	tag = u"%srichtig und liefern Hintergründe zu aktuellen Themen." % tag
	summ = u"Hinweis: Videos nur in geringer Auflösung (480x270) vorhanden."
	fparams="&fparams={'title': '%s','path': '%s'}"  % (title, quote(ARD_Fakt)) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
		fanart=ICON_MAINXL, thumb=ICON_FAKT, tagline=tag, summary=summ, fparams=fparams)
		
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
# 20.01.2024 umgestellt auf api.ardmediathek.de
# Aufruf Main_XL
def XL_Tagesschau(title, pid):	
	PLog("XL_Tagesschau:")
	PLog(title); PLog(pid); 
	base="https://api.ardmediathek.de/page-gateway/pages/tagesschau24/grouping/"
	if "Regionale Nachrichten" in title:		# abweichender Call
		base = "https://api.ardmediathek.de/page-gateway/widgets/ard/editorials/"	# alt.: tagesschau24 statt ard
	path = "%s%s?embedded=true" % (base, unquote(pid))	# unquote: %3A -> :
	
	page, msg = get_page(path)		
	if page == '':	
		msg1 = u"Fehler in XL_Tagesschau: %s" % title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))
	page = page.replace('\\"', '*')				# quotierte Marks entf., Bsp. \"query\"
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')			# Home-Button
	ID = 'A-Z'
	li = get_json_content(li, page, ID, mark="", homeID='TagesschauXL')
																
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
# 
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
		return
	
	cluster =  blockextract('class="trenner trenner--default', page)	# Cluster suchen
	mycluster=""
	if len(cluster) > 0:												# Einzelbilder mit Link auf Seite mit Slider
		for item in cluster:
			title = stringextract('<h2>', '</h2>', item)
			if title in title_org:
				mycluster = item
				PLog("cluster_found: " + title)
				break
	else:
		mycluster = page												# Slider-Bilder
	
	if 	'<div data-v=' in mycluster:									# 1 x Bilder in quoted json
		PLog("content_json:")
		items = blockextract('<div data-v=', mycluster, "</div>")
		conf = stringextract('data-v="', '"', items[0])					# nur 1 Bilderblock
		PLog(str(conf)[:80])
		conf = conf.replace('\\"', '"')
		conf = conf.replace('&quot;', '"')
		conf = unquote(conf)
		obj = json.loads(conf)
		PLog(str(obj)[:80]);
	
		name = obj["name"]
		imgObjects = obj["images"]
		PLog("imgs: %d, name: %s" % (len(imgObjects), name))
		img_list=[]; img_cnt=0
		for img in imgObjects:
			summ=""; img_cnt=img_cnt+1
			img_url = img["imageUrls"]["l"]
			img_alt = img["alttext"]
			summ=""														# i.d.R. img_alt mit  html-tags													
		
			title = img["title"]
			# Format img_list: "Titel || img_url || img_alt || summ"# img_list -> XL_BilderShow
			line = "%s||%s||%s||%s" % (title, img_url, img_alt, summ)
			img_list.append(line)

		if len(img_list) > 0:
			XL_BilderShow(name, img_list)
		return
		
	else:																# Bilder auf Folgeseiten
		PLog("content_html:")	
		li = xbmcgui.ListItem()
		li = home(li, ID='TagesschauXL')									# Home-Button
			
		items = blockextract('class="teaser-xs__link"', mycluster)
		cnt=0; path=""
		for item in items:
			summ=""
			cnt=cnt+1
			headline = stringextract('teaser-xs__headline">', '</span>', item)
			headline = cleanhtml(headline.strip())
			headline  = headline.replace('"', '*')

			
			PLog(headline)
			topline = stringextract('teaser-xs__topline">', '</span>', item)	# Subtitel
			img_alt = stringextract('alt="', '"', item)
			img_alt = img_alt.replace('&quot;', '"')
			title = headline
			title  = unescape(title)
			tag = "Folgeseiten\n\nBild: %s" % img_alt
			summ = "[B]%s[/B]" % topline
			img_url = stringextract('js-image" src="', '"', item)
			link = stringextract('teaser-xs__link" href="', '"', item)
			path = BASE_URL + link
			
			PLog("Satz1_2:")
			PLog(headline); PLog(topline); PLog(path); PLog(tag); PLog(summ); 
			title=py2_encode(title); path=py2_encode(path);
			fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(headline), quote(path))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_BilderClusterSingle", 
				fanart=ICON_BILDER, thumb=img_url, fparams=fparams, tagline=tag, summary=summ)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# ----------------------------------------------------------------------
# 23.01.2024 Bereinigung leerer Verz. in SLIDESTORE hinzugefügt (bei
#	Abbruch vor Slideshow, bleibt das angelegte Verz. leer).
#  12.03.2024 Übergabe img_list	via Dict (Dict_id), 
def XL_BilderShow(title, img_list, Dict_id=""):
	PLog("XL_BilderShow:")
	title_org=title
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button

	DelEmptyDirs(SLIDESTORE)								# leere Verz. löschen							
	fname = make_filenames(title)							# Ordnername: Titel 
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
	if Dict_id:												# Bildliste nachladen
		img_list = Dict("load", Dict_id)
	for line in img_list:
		cnt=cnt+1
		title, img_url, img_alt, summ = line.split("||")
		title = make_filenames(title) 						# Umlaute möglich
		local_path 	= "%s/%s.jpg" % (fpath, title)			# Kodi braucht Endung (ohne Prüfung) 
		if len(title) > 70:
			title = "%s.." % title[:70]						# Titel begrenzen
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		PLog(local_path)
		if os.path.isfile(local_path) == False:				# schon vorhanden?
			# path_url_list (int. Download): 
			#	Zieldatei_kompletter_Pfad|Bild-Url ..
			PLog(local_path); PLog(img_url)
			PLog(type(local_path)); PLog(type(img_url))
			path_url_list.append('%s|%s' % (local_path, img_url))

			if SETTINGS.getSetting('pref_watermarks') == 'true':
				# txt = "%s\n%s\n%s\n%s\n%s" % (fname,title_org,title,img_alt,summ)
				txt = "%s" % summ							# zu viele Wiederholung in übrigen Params
				if txt == "":
					txt = "%s" % img_alt	
				if txt == "":
					txt = "%s" % title	
				
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
# 18.11.2023 Anpassung an ARD-Änderungen
# 1. Call für Übersicht (nur jweils 3 items), Folgecalls in
#	XL_SearchContent
# Unterschiedliche Videoqualitäten
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
	
	path =  "https://www.tagesschau.de/json/search?searchText=%s" % (query) # ohne documentType nur jweils 3 items
	page, msg = get_page(path)	 
	if not page:	
		msg1 = "Fehler in XL_Search:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 	

	jsonObject = json.loads(page)
	PLog(str(jsonObject["documentTypes"])[:80])
	cnt_video=0; cnt_audio=0
	for typ in jsonObject["types"]:
		if typ["type"] == "video":
			cnt_video = typ["count"]
		if typ["type"] == "audio":
			cnt_audio = typ["count"]
	PLog("cnt_video: %d, cnt_audio: %d" % (cnt_video, cnt_audio))
			
	if cnt_video == 0 and cnt_audio == 0: 
		msg1 = u'keine Videos und Audios gefunden'
		msg2 = query
		icon = ICON_MAINXL		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("%s: %s" % (msg1, msg2))
		return
		
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')						# Home-Button
	
	if cnt_video:
		title = "[B]Videos: Anzahl %d[/B]" % cnt_video
		img = R(ICON_DIR_FOLDER)
		tag = "Folgeseiten | zu den Videos" 
		query=py2_encode(query);
		fparams="&fparams={'typ': 'video', 'query': '%s'}" % quote(query)		
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_SearchContent", 
			fanart=img, thumb=img, tagline=tag, fparams=fparams)
			
	if cnt_audio:
		title = "[B]Audios: Anzahl %d[/B]" % cnt_audio
		tag = "Folgeseiten | zu den Audios"
		fparams="&fparams={'typ': 'audio', 'query': '%s'}" % quote(query)			
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_SearchContent", 
			fanart=img, thumb=img, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)			
	
# ----------------------------------------------------------------------
# komplettes Suchergebnis mit documentType laden
# 	 
def XL_SearchContent(typ, query, pagenr=''):
	PLog("XL_SearchContent: " + typ)							# Bsp. TXL_Search_video

	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 0
	else:
		pagenr = int(pagenr)	
	
	path =  "https://www.tagesschau.de/json/search?searchText=%s&documentType=%s&pageIndex=%d" % (query, typ, pagenr) 
	page, msg = get_page(path)	 
	if not page:	
		msg1 = "Fehler in XL_SearchContent:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 
	jsonObject = json.loads(page)		
	PLog(str(jsonObject)[:80])
	items = jsonObject["documentTypes"][0]["items"]
	PLog(len(items))
	PLog(str(items)[:80])
	
	li = xbmcgui.ListItem()
	li = home(li, ID='TagesschauXL')							# Home-Button
	
	for item in items:
		tag=""; summ=""
		title = item["headline"]
		img = get_img(item)								
		if "datetime" in item:
			tag = "Sendedatum: " + item["datetime"]
		tag = "%s | weiter zum [B]%s[/B]" % (tag, up_low(typ))
		if "description" in item:
			summ = item["description"] 
		url = BASE_URL + item["url"]
		
		if title == "Video":									# nichtsagenden Titel erweitern
			title = "%s ..." % summ[:50]
		if len(title) > 65:
			title = "%s ..." % title[:65]
		mark = unquote(query).replace("+", "")
		title = make_mark(mark, title, "", bold=True)	# Suchbegriff fett -> util		
		
		title = repl_json_chars(title); summ = repl_json_chars(summ);
		url=py2_encode(url); title=py2_encode(title); 		
		fparams="&fparams={'title': '%s','path': '%s'}"  %\
			(quote(title), quote(url))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.get_VideoAudio", 
			fanart=img, thumb=img, tagline=tag, summary=summ, fparams=fparams)
			
	# Mehr-Seiten - ohne Berechnung
	nextpage = str(int(pagenr) + 1)
	tag = u"nächste Seite, aktuell: %s" % nextpage				# Basis 0
	PLog("nextpage: %s" % nextpage) 
	title = "Mehr: [B]%s[/B]" % query
	query=py2_encode(query);
	fparams="&fparams={'typ': '%s', 'query': '%s', 'pagenr': '%s'}" % (typ, quote(query), nextpage)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.XL_SearchContent", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------
def get_img(item):	
	PLog('get_img:')
	PLog(str(item)[:60])
	PLog(str(item))
	try:
		img = item["teaserImage"]["urlS"]	# urlM sehr häufig fehlend
	except:
		img = R(ICON_DIR_FOLDER)
	PLog("img: " + img)
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
	PLog(conf)
	
	
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
# 20.01.2024 live=true verhindert Stream-Blockade der 480p-Webplayer-Streams
#	bei eingeschalteter Zuletzt-gesehen-Liste
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
	
	content =  blockextract('data-v=', page, '</div>')
	PLog(len(content))
		
	cnt = 0; url_list=[]
	for item in content:
		PLog(item[:80])

		cnt = cnt +1												# Satz-Zähler						
		typ,av_typ,title,tag,summ,img,stream = get_content_json(item)
		if typ == False:											# jsonloads_error
			continue
				
		title=py2_encode(title); stream=py2_encode(stream); 
		summ=py2_encode(summ); img=py2_encode(img); 
			
		if typ == "audio":											# Audio
			ID='TagesschauXL'
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote_plus(summ), ID)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
		
		live=""
		if SETTINGS.getSetting('pref_startlist') == 'true':			# Blockade verhindern, s. Kopf
			live="true"		
		if typ == "video":											# Video	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote_plus(summ), live)
			addDir(li=li, label=title, action="dirList", dirID="ardundzdf.PlayVideo", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		

# ----------------------------------------------------------------------
# Aufruf: get_VideoAudio
# Auswertung Blöcke 'data-v=' - können Navi-Elemente o.a. enthalten.
#	Berücksichtigt werden nur Blöcke mit Playerdaten "playerType"
def get_content_json(item):	
	PLog('get_content_json:')
			
	minWidth=700					# .., 768x, 944x

	conf = stringextract('data-v="', '"', item)	
	conf = conf.replace('\\"', '"')
	conf = conf.replace('&quot;', '"')
	conf = unquote(conf)
	try:
		obj = json.loads(conf)
	except Exception as exception:
		PLog("jsonloads_error: " + str(exception))
		return False,"","","","","",""						# 7 Params

	PLog(str(obj)[:60]); 
	verf=""; url=""; stream=""; 
	tag=""; img=""

	if "playerType" not  in obj:							# falsches Format
		PLog("missing_playerType")
		return False,"","","","","",""		
		
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




