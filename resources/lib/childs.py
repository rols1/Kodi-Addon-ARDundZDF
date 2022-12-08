# -*- coding: utf-8 -*-
################################################################################
#				childs.py - Teil von Kodi-Addon-ARDundZDF
#		Rahmenmodul für Kinderprg div. Regionalsender von ARD und ZDF
#
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
################################################################################
#	
# 	<nr>9</nr>										# Numerierung für Einzelupdate
#	Stand: 08.12.2022

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

import  json		
import os, sys
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke
import string

import ardundzdf					# -> SenderLiveResolution, transl_wtag, get_query, Audio_get_sendung..
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

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 				# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_ZDF		= 'https://www.zdf.de'
BASE_KIKA 		= 'https://www.kika.de'
BASE_TIVI 		= 'https://www.zdf.de/kinder'

# Icons
ICON 			= 'icon.png'		# ARD + ZDF
ICON_CHILDS		= 'childs.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MAIN_TVLIVE= 'tv-livestreams.png'
ICON_MEHR 		= "icon-mehr.png"
ICON_SEARCH 	= 'ard-suche.png'
ICON_ZDF_SEARCH = 'zdf-suche.png'
				
MAUSLIVE		= "https://www.wdrmaus.de//_teaserbilder/720913_512.jpg"
MAUSZOOM		= "https://www.wdrmaus.de//_teaserbilder/720893_512.jpg"
MAUSRELIVE		= "https://www.wdrmaus.de//_teaserbilder/721363_512.jpg"
MAUSHEAR		= "https://www1.wdr.de/mediathek/audio/sendereihen-bilder/maus_sendereihenbild_podcast-1-100~_v-original.jpg"

# ext. Icons zum Nachladen aus Platzgründen,externe Nutzung: ZDFRubriken  (GIT_ZDFTIVI)							
#GIT_KIKA		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kika.png?raw=true"
KIKA_START		= "https://www.kika.de/bilder/startseite-104_v-tlarge169_w-1920_zc-a4147743.jpg"	# ab 07.12.2022

GIT_AZ			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-AZ.png?raw=true"
				# Einzelbuchstaben zu A-Z siehe Tivi_AZ
GIT_CAL			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-calendar.png?raw=true"
GIT_VIDEO		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaVideo.png?raw=true"
GIT_RADIO		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/radio-kiraka.png?raw=true"
GIT_KANINCHEN	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchen.png?raw=true"
GIT_KANINVIDEOS	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenVideos.png?raw=true"
GIT_KRAMLIEDER	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenKramLieder.png?raw=true"
GIT_KRAMSCHNIPP	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenKramSchnipsel.png?raw=true"
GIT_ZDFTIVI		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-zdftivi.png?raw=true"
GIT_TIVIHOME	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-home.png?raw=true"
GIT_KIR			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/kiraka.png?raw=true"
GIT_KIR_SHOWS	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/kiraka-shows.png?raw=true"
GIT_KIR_KLICK	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/klicker.png?raw=true"
GIT_DGS			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaDGS.png?raw=true"
GIT_AD			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaAD.png?raw=true"
GIT_ARD_KINDER	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-ard_kinder-familie.png?raw=true"

KikaCacheTime = 1*86400					# Addon-Cache für A-Z-Seiten: 1 Tag


# ----------------------------------------------------------------------			
def Main_childs():
	PLog('Main_childs:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
		
	fparams="&fparams={'title': '%s'}" % "KiKA"
	addDir(li=li, label= "KiKA", action="dirList", dirID="resources.lib.childs.Main_KIKA", fanart=R(ICON_CHILDS), 
		thumb=KIKA_START, fparams=fparams)
		
	fparams="&fparams={'title': '%s'}" % "tivi"
	addDir(li=li, label= "ZDFtivi für Kinder", action="dirList", dirID="resources.lib.childs.Main_TIVI", 
		fanart=R(ICON_CHILDS), thumb=GIT_ZDFTIVI, fparams=fparams)

	title = "ARD - Kinder und Familie"
	tag = u"Märchen, Spielfilme, Serien, Wissen und Dokus - hier gibt's unterhaltsame und "
	tag = u"%s%s" % (tag, u"spannende Videos für Kinder und die ganze Familie!")
	img = GIT_ARD_KINDER
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/kinderfamilie?embedded=true"
	ID = "Main_childs"
	fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
		(quote(path), quote(title), ID)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
		tagline=tag, fparams=fparams)


	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------			
def Main_KIKA(title=''):
	PLog('Main_KIKA:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
		
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'gesucht wird in [B]KiKA[/B]'
		title=py2_encode(title);
		func = "resources.lib.childs.Main_KIKA"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "KiKA", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=KIKA_START, 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
	
	title="Suche in KIKA"
	summ = "Suche Sendungen in KiKA"
	fparams="&fparams={'query': '', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Search", 
		fanart=KIKA_START, thumb=R(ICON_SEARCH), fparams=fparams)
			
	title='KiKA Live gucken'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Live", 
		fanart=KIKA_START, thumb=R(ICON_MAIN_TVLIVE), tagline='KIKA TV-Live', fparams=fparams)
		
	title='KiKA Programmvorschau'
	tag = u"Programmvorschau für eine Woche\n\nMit Klick zur laufenden Sendung"
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Vorschau", 
		fanart=KIKA_START, thumb=R(ICON_MAIN_TVLIVE), tagline=tag, fparams=fparams)

	title='KiKA Startseite' 
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start",
		fanart=KIKA_START, thumb=KIKA_START, tagline=title, fparams=fparams)

	'''
	title='Videos und Bilder (A-Z)'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBuendelAZ",
		fanart=KIKA_START, thumb=GIT_VIDEO, tagline=title, fparams=fparams)

	title='Die beliebtesten Videos (meist geklickt)'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBeliebt", 
		fanart=KIKA_START, thumb=GIT_VIDEO, tagline=title, fparams=fparams)

	title=u'Videos mit Gebärdensprache'
	path = "https://www.kika.de/videos/videos-dgs-100.html"
	thumb = GIT_DGS
	path=py2_encode(path); title=py2_encode(title); thumb=py2_encode(thumb);
	fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}"  %\
		(quote(path), quote(title), quote(thumb))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Barrierearm", 
		fanart=KIKA_START, thumb=GIT_DGS, tagline=title, fparams=fparams)

	title=u'Videos als Hörfilme'
	path = "https://www.kika.de/videos/videos-ad-100.html"
	thumb = GIT_AD
	path=py2_encode(path); title=py2_encode(title); thumb=py2_encode(thumb);
	fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}"  %\
		(quote(path), quote(title), quote(thumb))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Barrierearm",
		fanart=KIKA_START, thumb=GIT_AD, tagline=title, fparams=fparams)
	'''
	
	title=u'MausLive'
	tag = u"%s\n\nDer Kinderradiokanal des WDR  (Nachfolgeseite für [B]KiRaKa[/B])" % title
	img = MAUSLIVE
	fparams="&fparams={}" 
	addDir(li=li, label=title , action="dirList", dirID="resources.lib.childs.MausLive",
		fanart=KIKA_START, thumb=img, tagline=tag, fparams=fparams)
		
	title=u'Kinderhörspiele der ARD-Audiothek'
	query = u"Kinderhoerspiele"
	tag = u"Kinderhörspiele aus verschiedenen Radio-Sendungen." 
	summ = u"Wir verlassen KIKA und wechseln zu den Kinderhörspielen in der ARD-Audiothek."
	title=py2_encode(title); query=py2_encode(query) 
	fparams="&fparams={'title': '%s', 'query': '%s'}" % (quote(title), quote(query))
	addDir(li=li, label=title , action="dirList", dirID="AudioSearch",
		fanart=KIKA_START, thumb=GIT_RADIO, tagline=tag, summary=summ, fparams=fparams)
			
	title='KiKANiNCHEN'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Menu", 
		fanart=KIKA_START, thumb=GIT_KANINCHEN, tagline='für Kinder 3-6 Jahre', fparams=fparams)

	title=u'[B]für Erwachsene:[/B] Generation Alpha – Der KiKA-Podcast'
	tag = u"[B]für Erwachsene:[/B]\nwie entwickelt sich die Lebenswelt der Kinder und welche Herausforderungen kommen auf "
	tag = u"%sMedienmacher*innen zu? Das sind die Leitfragen von [B]Generation Alpha – Der KiKA-Podcast[/B]" % tag
	thumb = "https://kommunikation.kika.de/ueber-kika/25-jahre/podcast/generation-alpha-100_v-tlarge169_zc-cc2f4e31.jpg?version=35225"	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.gen_alpha", 
		fanart=KIKA_START, thumb=thumb, tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------			
def Main_TIVI(title=''):
	PLog('Main_TIVI:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'gesucht wird in [B]ZDF-tivi[/B]'
		title=py2_encode(title);
		func = "resources.lib.childs.Main_TIVI"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ZDF-tivi", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=GIT_ZDFTIVI, 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
	
	title="Suche in ZDFtivi"
	summ = "Suche Videos in KIKA"
	fparams="&fparams={'query': '', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_Search", fanart=GIT_ZDFTIVI, 
		thumb=R(ICON_ZDF_SEARCH), fparams=fparams)
			
	title='Startseite'
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(BASE_TIVI), title)
	addDir(li=li, label=title , action="dirList", dirID="ardundzdf.ZDFStart", fanart=GIT_ZDFTIVI, 
		thumb=GIT_TIVIHOME, tagline=title, fparams=fparams)
		
	title='Sendungen der letzten 7 Tage'
	fparams="&fparams={}" 
	addDir(li=li, label=title , action="dirList", dirID="resources.lib.childs.Tivi_Woche", fanart=GIT_ZDFTIVI, 
		thumb=GIT_CAL, tagline=title, fparams=fparams)
		
	title='Sendungen A-Z | 0-9'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ", fanart=GIT_ZDFTIVI, 
		thumb=GIT_AZ, tagline=title, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
def Kikaninchen_Menu():
	PLog('Kikaninchen_Menu')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	title='Kikaninchen Videos'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Videoseite", fanart=GIT_KANINCHEN, 
		thumb=GIT_KANINVIDEOS, tagline='für Kinder 3-6 Jahre', fparams=fparams)
	title='Kikaninchen Singen und Tanzen'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KikaninchenLieder", fanart=GIT_KANINCHEN, 
		thumb=GIT_KRAMLIEDER, tagline='für Kinder 3-6 Jahre', fparams=fparams)
	title='Kikaninchen Tonschnipsel'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tonschnipsel", fanart=GIT_KANINCHEN, 
		thumb=GIT_KRAMSCHNIPP, tagline='für Kinder 3-6 Jahre', fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 19.11.2022 Verwendung der Websuche (../suche/suche104.html?q=..) - früher nicht
#	 nutzbar, da script-generiert. Vorherigen Code der Suche über alle Bündelgruppen 
#	(Kika_VideosBuendelAZ) gelöscht.
# 06.12.2022 Anpassung an Webseitenänderungen
#
def Kika_Search(query=None, title='Search', pagenr=''):
	PLog("Kika_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='ARD')
	PLog(query)
	query_org = unquote(query)
	query_org = query_org.replace('+', ' ')								# für Vergleich entfernen
	if  query == None or query.strip() == '':
		return ""

	path = "https://www.kika.de/suche/suche104?q=%s" % query_org
	page, msg = get_page(path)
	if page == '':
		msg1 = "Fehler in Kika_Search:"
		msg2 = msg
		
	if u'</strong> keine Ergebnisse' in page:
		msg1 = "Na sowas. Nichts gefunden, was deinem Suchbegriff entspricht."
		msg2 = "Versuche es mit einem anderen Wort."
		page = ""
	if page == "":
		MyDialog(msg1, msg2, '')	
		return
	
	title = "Suche nach [B]%s[/B]"	% query_org
	Kika_Rubriken(page, title='', thumb=R(ICON_SEARCH), ID='Search')
	return
	
# ----------------------------------------------------------------------
# 06.12.2022 Neu an Webseitenänderungen
# 1. Durchlauf Buttons Highlights + Cluster
# 2. Durchlauf Cluster -> 
def Kika_Start(show_cluster=''):
	PLog("Kika_Start: " + show_cluster)

	page, msg = get_page(path=BASE_KIKA)
	if page == '':
		msg1 = "Fehler in Kika_Start:"
		msg2 = msg

	page = Kika_get_props(page)										# Web-json ausschneiden
	page = page.replace('\\"', '*')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')				# Home-Button
	# ------------------------------------------------------------------
	# 2. Durchlauf: Buttons Stage + Cluster 
	if show_cluster:
		PLog("Start_2:")
		if "Highlights" in show_cluster:								# Highlights
			pos1 = page.find('"stageContent"')
			pos2 = page.find('"mainNavigationResponse"')
			page = page[pos1:pos2]
			title = "Highlights"; fanimg = KIKA_START
			Kika_Rubriken(page, title, fanimg, ID='Start_2',li=li)	
		else:															# restl. Cluster
			items = blockextract('"boxType":', page)
			PLog("items2: %d" % len(items))
			for item in items:
				title = stringextract('"title":"', '"', item)
				PLog("title: %s, show_cluster: %s" % (title, show_cluster))
				summ = "Folgeseiten"
				ID = "Start_2"
				if title in show_cluster:
					img, img_alt = Kika_get_img(item)						# 1. Bild
					PLog("found_cluster: " + show_cluster)
					Kika_Rubriken(item, title, img, ID='Start_2',li=li)	# Seitensteuerung Kika_Rubriken					
	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
	# ------------------------------------------------------------------
	# 1. Durchlauf: Buttons Stage + Cluster 
	PLog("Start_1:")
	title = '[B]Highlights[/B]'											# Highlights voranstellen
	tag = "Folgeseiten"
	show_cluster = "Highlights"
	fparams="&fparams={'show_cluster': 'Highlights'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start", 
		fanart=KIKA_START, thumb=KIKA_START, fparams=fparams, tagline=tag)
	
	items = blockextract('"boxType":', page)
	PLog("items1: %d" % len(items))
	for item in items:
		title = stringextract('"title":"', '"', item)
		PLog("title: " + title)
		if "Jetzt live" in title or title == "":						# skip Live + Game
			continue
			
		img, img_alt = Kika_get_img(item)								# 1. Bild
		tag = "Folgeseiten"
		fparams="&fparams={'show_cluster': '%s'}" % title
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start", 
			fanart=KIKA_START, thumb=img, fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - json-Inhalt ausschneiden (nicht
#	json.loads-geeignet)
def Kika_get_props(page):
	PLog('Kika_get_props:')
	
	m1 = page.find('"props":')
	m2 = page.find(',"__N_SSP"')
	if m1 > 0 and m2 > 0:
		page = page[m1:m2]
	PLog(page[:60])
	return page
				
# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - img + img_alt ermitteln
#	
def Kika_get_img(item):
	PLog('Kika_get_img:')
	
	#img_types = blockextract("imageType", item)					# bei Bedarf weitere Typen/Größen suchen
	#for img_type in img_types:
	
	img = stringextract('urlScheme":"', '"', item)
	#img = img.replace("**imageVariant**", "miniKika")				# miniKika häufig nicht vorh.
	img = img.replace("**imageVariant**", "original")				# Varianten s. "variants":[
	img = img.replace("**width**", "1920")							# s.o.
	if img.startswith('http') == False:
		img = BASE_KIKA + img
	img_alt = stringextract('alt":"', '"', item)		
	
	return img, img_alt
				
# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - einz. Datensatz auswerten (docType
#	videoSubchannel, externalVideo, ..)
# s=Blockitem (z.B. docType)
# 
def Kika_get_singleItem(s):
	PLog('Kika_get_singleItem:')

	date=""; endDate=""; summ=""; mehrf=False; func=""
	typ = stringextract('docType":"', '"', s)
	PLog("docType: " + typ)
	
	s = s.replace('\\"', '*')
	ext_id = stringextract('externalId":"', '"', s)					# Bsp. zdf-SCMS_tivi_vcms_video_1914206-default
	api_url = stringextract('url":"', '"', s)						# "api":{	
	stitle = stringextract('title":"', '"', s)		
	
	# Einzelvideos: docType":"externalVideo", docType":"video"
	if "channel" in typ or typ=="broadcastSeries":
		mehrf = True												# Folgeseiten
						
	date = stringextract('date":"', '"', s)	
	endDate = stringextract('endDate":"', '"', s)
	if date:
		date = time_translate(date, add_hour=0)
		date = "Sendedatum: [B][COLOR blue]%s[/COLOR][/B]" % date
	if endDate:
		endDate = time_translate(endDate, add_hour=0)
		endDate = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % endDate
	
	descr = stringextract('teaserText":"', '"', s)
	img, img_alt = Kika_get_img(s)		
	cr = stringextract('copyrights":"', '"', s)
	dur = stringextract('duration":"', '"', s)
	
	if mehrf == False:
		summ = descr
		tag = "Dauer: %s | [B]Bild: [/B] %s | %s" % (dur, cr, img_alt) 
		tag = "%s\n\n%s\n%s" % (tag,  endDate, date)
	else:
		tag = "[B]Bild: [/B] %s | Folgeseiten" % cr
	summ = descr			

	stitle = unescape(stitle); stitle = repl_json_chars(stitle); 
	tag = unescape(tag); tag = repl_json_chars(tag); 
	summ = unescape(summ); summ = repl_json_chars(summ); 
	Plot = "%s\n\n[B]Inhalt: [/B] %s" % (tag, summ)
	Plot = Plot.replace('\n', '||')
		
	api_url=py2_encode(api_url); stitle=py2_encode(stitle); img=py2_encode(img);
	path=api_url; thumb=img; Plot=Plot	
	PLog('mehrf: %s, typ: %s, api_url: %s, stitle: %s, thumb: %s, Plot: %s' % (mehrf, typ, path, stitle, thumb, Plot))	
	return mehrf,typ,path,stitle,thumb,Plot			
# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - Cluster ermitteln in  
#	Folgeseiten (path=api_url -> json), docType: videoSubchannel
#
def Kika_Subchannel(path, title, thumb, Plot, li=''):
	PLog('Kika_Subchannel: ' + title)
	title_org=title
	
	page, msg = get_page(path)
	if page == '':
		msg1 = "Fehler in Kika_Rubriken:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	if li == "":			
		li = xbmcgui.ListItem()
		li = home(li, ID='Kinderprogramme')				# Home-Button
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	
	Plot_par = Plot
	summ_org = Plot.replace("||", "\n")										# Plot hier: tagline + summary
	
	featuredVideo = stringextract('"featuredVideo"',  '"videosPageUrl"', page)
	fanimg=""
	if featuredVideo:													# kann fehlen
		teaserImage = stringextract('"teaserImage"',  '"structure"', page)
		if teaserImage:
			fanimg, img_alt = Kika_get_img(teaserImage)
			
		mehrf,typ,path,stitle,thumb,Plot = Kika_get_singleItem(featuredVideo)
		summ = Plot.replace("||", "\n")	
	
		stitle = "[B]Empfehlung: [/B] %s" % stitle							# herausgestelltes Video im Web
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
			(quote(path), quote(stitle), quote(thumb), quote(Plot))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", 
			fanart=fanimg, thumb=thumb, fparams=fparams, summary=summ, mediatype=mediatype)
	
	if '"videosPageUrl":"' in page:										# Videos nachladen
		PLog("get_allvideos:")
		allvideos = stringextract('"videosPageUrl":"',  '"', page)		# Folgenübersicht (json)
		page, msg = get_page(path=allvideos)
		if page == '':
			msg1 = "Fehler in Kika_Subchannel:"
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
	else:																# Channelinhalt
		fanimg=thumb
	
	Kika_Rubriken(page, title_org, fanimg, ID='Subchannel',li=li)		# Seitensteuerung Kika_Rubriken
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)				
				
# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - Folgeseiten ermitteln in  
#	 (path=api_url -> json), docType: broadcastSeries
#
def Kika_Series(path, title, thumb, Plot):
	PLog('Kika_Series: ' + title)
	title_org=title
	
	page, msg = get_page(path)
	if page == '':
		msg1 = "Fehler in Kika_Series:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	
	Subchannel = stringextract('"videoSubchannel"',  '},', page)
	api_url = stringextract('url":"', '"', Subchannel)
	Kika_Subchannel(api_url, title, thumb, Plot)						# -> Seitensteuerung Kika_Rubriken
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)				
	
# ----------------------------------------------------------------------
# 07.12.2022 nach Webänderungen - einz. Cluster/Channel/Folgen auswerten 
#	li + page durch Aufrufer möglich
def Kika_Rubriken(page, title, thumb, ID='', li='', path=''):
	PLog('Kika_Rubriken: ' + ID)
	thumb_org=thumb; title_org=title; li_org=li
	
	if li == '':				
		li = xbmcgui.ListItem()
		li = home(li, ID='Kinderprogramme')				# Home-Button

	if ID == "Search":
		page = Kika_get_props(page)										# Web-json ausschneiden
		pos = page.find("searchResponse")								# Ergebn. ab searchResponse
		page = page[pos:]
	else:
		if path:														# Bsp.: nächste Seite, s.u.
			page, msg = get_page(path)
			if page == '':
				msg1 = "Fehler in Kika_Rubriken:"
				msg2 = msg
				MyDialog(msg1, msg2, '')
				return
	
	items = blockextract('"docType":', page)
	PLog(len(items))
	for s in items:
		mediatype='' 
		# path: api_url 
		mehrf,typ,path,stitle,thumb,Plot = Kika_get_singleItem(s)		# -> Kika_get_singleItem
		tag = Plot.replace('||', '\n')

		if mehrf:														# Folgeseiten
			if "channel" in typ:
				func = "Kika_Subchannel"
			if typ == "broadcastSeries":
				func = "Kika_Series"
		else:
			func = "Kika_SingleBeitrag"									# einz. Video
			if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Kennz. Video für Sofortstart 
				mediatype='video'
		PLog("func:" + func)	
		if func:		
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
				(quote(path), quote(stitle), quote(thumb), quote(Plot))
			addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.%s" % func, 
				fanart=thumb_org, thumb=thumb, fparams=fparams, tagline=tag, mediatype=mediatype)

	# Mehr Seiten anzeigen:
	next_path = stringextract('next":"', '"', page)						# Ende: "next":null
	next_path = next_path.replace(u'\\u0026', u'&')						# in Web-json nötig
	PLog("next_path: " + next_path)
	if next_path:
		next_page=0
		try:
			next_page =  re.search(u'page=(\d+)', next_path).group(1)
			next_page = int(next_page)
		except Exception as exception:
			PLog(str(exception))
			
		totalPages = stringextract('totalPages":', ',', page)
		summ=""
		if totalPages != "null":										# null möglich
			summ = u"insgesamt: %s Seite(n)" % totalPages
		tag = "weiter zu Seite %s" % str(next_page)
		title_org=py2_encode(title_org); next_path=py2_encode(next_path); 
		thumb_org=py2_encode(thumb_org);
		fparams="&fparams={'page':'', 'title':'%s', 'thumb':'%s', 'ID':'%s', 'li':'', 'path':'%s'}" %\
			(quote(title_org), quote(thumb_org), "NextPage", quote(next_path))
		addDir(li=li, label=tag, action="dirList", dirID="resources.lib.childs.Kika_Rubriken", 
			fanart=thumb_org, thumb=R(ICON_MEHR), fparams=fparams, tagline=tag,summary=summ)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------			
# 25.06.2020 Nutzung neue Funktion get_ZDFstreamlinks
def Kika_Live():
	PLog('Kika_Live:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	import resources.lib.EPG as EPG
	zdf_streamlinks = get_ZDFstreamlinks()
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	m3u8link=''
	for line in zdf_streamlinks:
		PLog(line)
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('KiKA') in up_low(webtitle): 	# Sender mit Blank!
			m3u8link = href
			break
	if m3u8link == '':
		PLog('%s: Streamlink fehlt' % 'KiKA ')
	
	ID = 'KIKA'
	title = 'KIKA TV-Live'
	Merk = ''
	
	rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
	PLog(rec)	# bei Bedarf
	if len(rec) == 0:							# EPG-Satz leer?
		title = 'EPG nicht gefunden'
		summ = ''
		tagline = ''
	else:	
		href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]
		if img.find('http') == -1:	# Werbebilder today.de hier ohne http://
			img = R('tv-kika.png')
		title 	= sname.replace('JETZT', ID)		# JETZT durch Sender ersetzen
		# sctime 	= "[COLOR red] %s [/COLOR]" % stime			# Darstellung verschlechtert
		# sname 	= sname.replace(stime, sctime)
		tagline = 'Zeit: ' + vonbis
				
	title = unescape(title); title = repl_json_chars(title)
	summ = unescape(summ); summ = repl_json_chars(summ)
	PLog("title: " + title); PLog(summ)
	title=py2_encode(title); m3u8link=py2_encode(m3u8link);
	img=py2_encode(img); summ=py2_encode(summ);			
	fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'Merk': '%s'}" %\
		(quote(m3u8link), quote(title), quote(img), quote_plus(summ), Merk)
	addDir(li=li, label=title, action="dirList", dirID="ardundzdf.SenderLiveResolution", fanart=R('tv-EPG-all.png'), 
		thumb=img, fparams=fparams, summary=summ, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------			
# 
def Kika_Vorschau():
	PLog('Kika_Vorschau:')

	zdf_streamlinks = get_ZDFstreamlinks()
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	stream_url=''
	for line in zdf_streamlinks:
		PLog(line)
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('KiKA') in up_low(webtitle): 	# Sender mit Blank!
			stream_url = href
			break
	if stream_url == '':
		PLog('%s: Streamlink fehlt' % 'KiKA ')
		
	ID="KIKA"; name="KIKA"
	
	ardundzdf.EPG_ShowSingle(ID, name, stream_url, pagenr=0)
	return
	
# ----------------------------------------------------------------------
# 04.07.2021 Aus WDR5 KiRaKa wird MausLive - Infoseite:
#	kinder.wdr.de/radio/kiraka/mauslive-160.html 
# Aufruf: Main_KIKA	
def MausLive():
	PLog('MausLive:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	#---------------------						# Live Start: akt. Audiostream + PRG-Hinweis
	path = "https://kinder.wdr.de/radio/player/radioplayer-die-maus-100~_layout-popupVersion.html"
	page1, msg = get_page(path)	
	pos = page1.find('wdrrCurrentShowTitleTitle')
	mp3_img = MAUSHEAR
	if pos < 0:
		sendung = "Maus-Stream abspielen"
	else:
		sendung = stringextract('wdrrCurrentShowTitleTitle">', '</', page1[pos:])
		
	
	mediaObj = stringextract('mediaObj":{"url":"', '"', page1) # -> deviceids-medp.wdr.de (json)
	PLog("mediaObj: " + mediaObj)
	page2, msg = get_page(mediaObj)							
	if page2 == '':	
		msg1 = "Fehler in MausLive"
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page2))	
	
	mp3_url = stringextract('audioURL":"', '"', page2)	# .m3u8
	if mp3_url.startswith("http") == False:
		mp3_url = "https:" + mp3_url
	PLog("mp3_url: " + mp3_url)
	
	title = u'MausLive hören: [B]%s[/B]' % sendung
	tag = u"aktuelle Sendung: [B]%s[/B]" % sendung
	summ = u'MausLive ab 19:04 Uhr live hören - Montag bis Freitag und Sonntag'
	Plot = "%s||||%s" % (tag, summ)
	mp3_url=py2_encode(mp3_url); title=py2_encode(title);
	mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
		quote(title), quote(mp3_img), quote_plus(Plot))
	addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSLIVE, thumb=mp3_img, fparams=fparams, 
		tagline=tag, mediatype='music')	
	
	#---------------------						#  Live Ende
	title = u'MausZoom - Kindernachrichten'
	tag = u"Nachrichten gehen schnell ins Ohr und sind oft schnell wieder weg. Um sie richtig zu verstehen braucht man"
	tag = "%s Zeit. Die Maus nimmt sich diese und schaut im MausZoom auf ein Thema wie eine Kamera, die sich" % tag
	tag = "%s langsam reinzoomt und immer mehr Details entdeckt." % tag
	url = "https://kinder.wdr.de/radio/diemaus/audio/maus-zoom/maus-zoom-106.podcast"
	title=py2_encode(title); url=py2_encode(url);
	fparams="&fparams={'title': '%s', 'url': '%s'}" % (quote(title), quote(url))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Maus_Audiobooks", fanart=MAUSLIVE, 
		thumb=MAUSZOOM, fparams=fparams, tagline=tag)
		
	title = u'MausLive zum Nachhören'
	tag = u"Hier kannst du die Sendungen noch mal anhören."
	url = "https://www.wdrmaus.de/hoeren/MausLive/nachhoeren.php5"
	title=py2_encode(title); url=py2_encode(url);
	fparams="&fparams={'title': '%s', 'url': '%s'}" % (quote(title), quote(url))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Maus_MediaObjects", fanart=MAUSLIVE, 
		thumb=MAUSRELIVE, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 05.07.2021 - Auswertung podcast-Seite (url)
# Umsetzung java-Code loadAudiobooks, z.B. in wdrmaus.de/hoeren/mauszoom.php5	
# Aufruf: MausLive	
def Maus_Audiobooks(title, url):
	PLog('Maus_Audiobooks:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(url)	
	if page == '':	
		msg1 = "Fehler in Maus_Audiobooks"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract("<item>", page)
	PLog(len(items))	
	
	for item in items:
		title = stringextract("<title>", "</title>", item)
		mp3_url = stringextract('<enclosure url="', '"', item)
		mp3_img = stringextract('href="', '"', item)			# itunes:image href="..
		if mp3_img == '':										# kann fehlen
			mp3_img = MAUSZOOM
		dur = stringextract("<duration>", "</itunes:duration>", item)
		descr = stringextract("summary>", "</itunes:summary>", item)
		pubDate = stringextract("<pubDate>", "</pubDate>", item)
		author = stringextract("author>", "</itunes:author>", item)
		
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)
		tag = "Dauer: %s | Sendung vom %s | Autor: %s" % (dur, pubDate, author)
		Plot= "%s||||%s" % (tag, descr)
	
		PLog('Satz11:')		
		PLog(title);PLog(mp3_url);PLog(mp3_img);
		PLog(tag);PLog(descr[:60]);
		
		mp3_url=py2_encode(mp3_url); title=py2_encode(title);
		mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(mp3_img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSZOOM, thumb=mp3_img, fparams=fparams, 
			tagline=tag, summary=descr, mediatype='music')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 05.07.2021 - Auswertung Seite (url) mit mehreren 'mediaObj'	
# Aufruf: MausLive	
#
def Maus_MediaObjects(title, url):
	PLog('Maus_MediaObjects:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(url)	
	if page == '':	
		msg1 = "Fehler in Maus_MediaObjects"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract('class="audioButton"', page)
	PLog(len(items))
	
	for item in items:
#		PLog(item)
		mediaObj = stringextract("'url': '", "'", item) # -> ..-hoeren-104.assetjsonp (MausLive abwei.)
		PLog("mediaObj: " + mediaObj)

		page, msg = get_page(mediaObj)
		if page == '':
			continue
		mp3_url = stringextract('audioURL" : "', '"', page)	# .mp3
		PLog("mp3_url1: " + mp3_url)
		if mp3_url.startswith("http") == False:
			mp3_url = "https:" + mp3_url
		PLog("mp3_url2: " + mp3_url)

		title = stringextract('ClipTitle" : "', '"', page)
		pubDate = stringextract('AirTime" : "', '"', page)
		Plot  = "%s||||gesendet: %s" % (title, pubDate)
		tag = Plot.replace("||", "\n")
		mp3_img = MAUSRELIVE							# json- und html-Seite ohne Kontext-Bild
		
		mp3_url=py2_encode(mp3_url); title=py2_encode(title);
		mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(mp3_img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSLIVE, thumb=MAUSRELIVE, 
			fparams=fparams, tagline=tag, mediatype='music')	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
	
# ----------------------------------------------------------------------
# 04.07.2021 Aus WDR5 KiRaKa wird MausLive - s. Funktion MausLive.
#	Hörspiele + Nachrichten noch vorhanden 'KiRaKa - Sendungen 
#	zum Nachhören'	inzwischen entfallen
#		
def Kiraka():
	PLog('Kiraka:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	thumb 	= GIT_KIR_SHOWS
	title = u'KiRaKa - Hörspiele'
	tagline = u'Alle KiRaKa - Kinderhörspiele'
	title=py2_encode(title); 
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kiraka_pods", fanart=GIT_RADIO, 
		thumb=thumb, fparams=fparams, tagline=tagline)
	
	thumb 	= GIT_KIR_KLICK
	title = u'KiRaKa-Klicker - Nachrichten für Kinder'
	tagline = u'aktuelle und speziell für Kinder aufbereitete Nachrichten von der Kiraka-Redaktion'
	title=py2_encode(title); 
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kiraka_klick", fanart=GIT_RADIO, 
		thumb=thumb, fparams=fparams, tagline=tagline)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------			
def Kiraka_shows(title):
	PLog('Kiraka_shows:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = "https://kinder.wdr.de/radio/kiraka/kiraka-on-demand-100.html"
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kiraka_shows"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract('"AudioObject",', page)	
	for s in items:
		img = stringextract('url" : "', '"', s)
		stitle = stringextract('headline" : "', '"', s)
		webid = stringextract('"@id" : "', '"', s) # url" : "https://www1.wdr.de/mediathek/..
		
		dur = stringextract('duration" : "', '"', s)		# Bsp. PT55M38S
		dur = dur[2:5]										# min ausschneiden
		dur = dur.replace('M', ' min')
		
		stitle = py2_encode(stitle); dur = py2_encode(dur)
		tag = "%s | %s | %s" % (title, stitle, dur)
		Plot = tag
		
		PLog('Satz5:')
		PLog(img); PLog(stitle); PLog(webid); PLog(Plot);
		stitle=py2_encode(stitle); webid=py2_encode(webid);
		thumb=py2_encode(img); Plot=py2_encode(Plot); 
			
		fparams="&fparams={'webid': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(webid), 
			quote(stitle), quote(thumb), quote_plus(Plot))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kiraka_get_mp3", \
			fanart=GIT_KIR, thumb=thumb, fparams=fparams, tagline=tag, mediatype='music')
			
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Kinderhörspiele
# die ermittelte webid wird in Kiraka_get_mp3 zur Web-Url. Auf der
#	Webseite wird dann die mp3-Quelle ermittelt.
# 20.02.2022 WDR-Seite kinderhoerspiel-podcast-102 nicht mehr vorh. -
#	Umstellung auf Inhalte der Audiothek
#			
def Kiraka_pods(title):
	PLog('Kiraka_pods:')
	
	title = u'KiRaKa - Hörspiele'
	ARD_AUDIO_BASE = 'https://api.ardaudiothek.de/'
	web_url = "https://www.ardaudiothek.de/kinderhoerspiel-im-wdr/36244846"
	node_id = "36244846"
	url = "https://api.ardaudiothek.de/programsets/36244846/?offset=0&limit=20"
	
	ardundzdf.Audio_get_sendung_api(url, title, home_id='Kinderprogramme')
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# mp3-Quelle ermitteln + direkt zu PlayAudio
# Aufrufer Kiraka_pods, Kiraka_klick (2. Durchlauf)
def Kiraka_get_mp3(webid, title, thumb, Plot):
	PLog('Kiraka_get_mp3: ' + webid)

	if webid.startswith('http') == False:					# kompl. Url bei Klicker-Nachrichten, nicht bei Pods
		base = "https://kinder.wdr.de/radio/kiraka/hoeren/hoerspiele/"
		path = base + webid + ".html"
	else:
		path = webid
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kiraka_klick"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	

	mp3url=''
	if '"mediaObj":' in page:								# mit + ohne Download-Button
		PLog("Lade mediaObj:")
		dl_js = stringextract('"mediaObj":', 'title="Audio starten"', page)
		dl_js = stringextract('url":"', '"', dl_js)		# java -> json-Seite mit mp3
		page, msg = get_page(dl_js)
		mp3url = stringextract('audioURL":"', '"', page)			
	else:
		msg1 = u"Kiraka_get_mp3: MediaObjekt nicht gefunden für"
		msg2 = ">%s<" % title
		MyDialog(msg1, msg2, '')	
		return li

	if mp3url.startswith('//'):
		mp3url = "https:" + mp3url
	else:
		if mp3url:
			mp3url = base + mp3url
		else:
			stitle = stitle + " | keine mp3-Quelle gefunden!"
	
	PLog('Satz7:')
	PLog(title); PLog(mp3url); PLog(Plot);
	PlayAudio(mp3url, title, thumb, Plot)
	return
# ----------------------------------------------------------------------
# Nachrichten für Kinder
# 2 Durchgänge:
#	1. Übersicht der Beiträge
#	2. Weburl: Zielseite mit mp3url
#			
def Kiraka_klick(title, weburl=''):
	PLog('Kiraka_klick:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	base = "https://kinder.wdr.de"
	if weburl == '':							# 1. Durchlauf: Übersicht
		path = base + "/radio/kiraka/nachrichten/klicker/index.html"
	else:
		path = weburl
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kiraka_klick"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	if weburl == '':							# 1. Durchlauf: Übersicht
		items = blockextract('class="teaser">', page)	
		for s in items:
			if '"Javascript-Fehler"' in s or 'class="media mediaA audio' not in s:
				continue
			weburl = base + stringextract('href="', '"', s)	# abweichend von Kiraka_pods
			img = stringextract('srcset="', '"', s)
			if img.startswith('//'):
				img = "https:" + img
			else:
				img = base + img
			stitle = stringextract('title="', '"', s)		# href-title
			stitle = unescape(stitle)
			descr = stringextract('teasertext">', '&nbsp', s)
			descr = mystrip(descr)										
			
			tag = "%s\n\n%s" % (stitle, descr)
			Plot = tag.replace('\n', '||')
			
			PLog('Satz6:')		
			PLog(img); PLog(stitle); PLog(weburl); PLog(Plot);
			stitle=py2_encode(stitle); weburl=py2_encode(weburl);
			thumb=py2_encode(img); Plot=py2_encode(Plot); 
			fparams="&fparams={'webid': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(weburl), 
				quote(stitle), quote(thumb), quote_plus(Plot))
			addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kiraka_get_mp3", \
				fanart=GIT_KIR_KLICK, thumb=thumb, fparams=fparams, tagline=tag, mediatype='music')
				
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		

# ----------------------------------------------------------------------
# alle Videos - erster Aufruf A-Z-Liste ../allevideos-buendelgruppen100.html, 
#	zweiter Aufruf: Liste einer Gruppe 
# Info: die Blöcke 'teaser teaserIdent' enthaltenen die Meist geklickten,
#	Auswertung in Kika_VideosBeliebt
# getHrefList: nur hrefs der Bündelgruppen sammeln für Kika_Search - dort
#	-> Dict-Cache 
# 30.12.2021 Cache ergänzt (Leit- und Einzelseiten) 
# 29.07.2022 Link geändert ../allevideos-buendelgruppen100.html ->
#	../uebersicht-alle-videos-100.html			
# 06.12.2022 Link-Änderung: https://www.kika.de/videos		
#	
def Kika_VideosBuendelAZ(path='', getHrefList=False, button=''): 
	PLog('Kika_VideosBuendelAZ: ' + path); PLog(button)
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	first=False; fname=''; page=''
	if button == '':								# A-Z-Liste laden
		path = 'https://www.kika.de/videos'
		first=True
		fname = "page-A_zc-05fb1331"
	else:
		fname = stringextract('allevideos-buendelgruppen100_', '.htm', path)
		page = Dict("load", fname, CacheTime=KikaCacheTime)
	
	if page == False or page == '':
		page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_VideosBuendelAZ:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	else:
		Dict("store", fname, page)
	PLog(len(page)); PLog(first)
	
	if first:							# 1. Aufruf: A-Z-Liste
		# begrenzen - Wiederholung A-Z-Liste am Fuß:
		page = stringextract('top navigation -->', 'class="media mediaA"', page)
		HrefList = []
		pageItems = blockextract('class="bundleNaviItem ">', page)
		blockA = stringextract('bundleNaviWrapper"', '</div>', page) # A fehlt in pageItems
		pageItems.insert(0, blockA)
		PLog(len(pageItems))
		for item in pageItems:
			href = BASE_KIKA + stringextract('href="', '"', item)
			href=py2_encode(href)
			if getHrefList:							# nur hrefs sammeln 
				HrefList.append(href)
			else:
				button = stringextract('title="">', '<', item)
				if '...' in button:					# Ende Liste
					button = "0-9"
				img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
				PLog("button: " + button); PLog("href: " + href)
				title = "Sendungen mit " + button
				fparams="&fparams={'path': '%s', 'button': '%s'}" % (quote(href), button)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBuendelAZ", fanart=KIKA_START,
					thumb=img_src, tagline=title, fparams=fparams)
				
		if getHrefList:							# nur hrefs return
			return li, HrefList	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True); 
		return
			
	# 2. Aufruf: Liste einer Gruppe 
	PLog("button: " + button);  PLog(first)
	pos = page.find("The bottom navigation")		# begrenzen, es folgen A-Z + meist geklickt
	PLog(pos)
	if pos > 0:
		page = page[:pos]
	PLog(len(page))
	pageItems = blockextract('class="media mediaA">', page)	
	PLog(len(pageItems))
	
	for s in pageItems:			
		# PLog(s[0:40])		# bei Bedarf
		href =  BASE_KIKA + stringextract('href="', '"', s)
		img = stringextract('<noscript>', '</noscript>', s).strip()		# Bildinfo separieren
		img_alt = stringextract('alt="', '"', img)						# hier Infotext
		img_src = stringextract('src="', '"', img)
		if img_src.startswith('http') == False:
			img_src = BASE_KIKA + img_src
		
		stitle = stringextract('class="linkAll" title="', '"', s)		
		stitle = cleanhtml(stitle)
		
		stitle = unescape(stitle); stitle = repl_json_chars(stitle)	
		img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt)		
		
		PLog('Satz1:')
		PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src)
		href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src);
		
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" %\
			(quote(href), quote(stitle), quote(img_src))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=img_alt)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# alle Videos - beliebteste Bündelgruppen, Einzelvideos in Kika_Videos  		
# 29.07.2022 Link geändert ../allevideos-buendelgruppen100.html ->
#	../uebersicht-alle-videos-100.html
# 06.12.2022 Link-Änderung: https://www.kika.de/videos		
def Kika_VideosBeliebt(): 
	PLog('Kika_VideosBeliebt:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kika.de/videos'
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_VideosBeliebt:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	buendel = blockextract('teaser teaserIdent', page)	
	PLog(len(buendel))
	
	for s in 	buendel:			
		# PLog(s[0:40])		# bei Bedarf
		href =  BASE_KIKA + stringextract('href=\"', '\"', s)
		img = stringextract('<noscript>', '</noscript>', s).strip()		# Bildinfo separieren
		img_alt = stringextract('alt=\"', '\"', img)	
		img_src = stringextract('src="', '"', img)
		if img_src.startswith('http') == False:
			img_src = BASE_KIKA + img_src
		
		dachzeile = stringextract('<h4 class=\"headline\">', '</h4>', s)		
		headline = stringextract('page=artikel\">', '</a>', dachzeile).strip()	
		stitle = headline
		img_title = stringextract('img title="', '"', s)
		if stitle == '':
			stitle = img_title
		
		stitle = unescape(stitle); stitle = repl_json_chars(stitle)	
		img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt)		
		
		PLog('Satz2:')
		PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src)
		href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src);
		
		if 'KiKA LIVE' in stitle:										# s. Main_KIKA
			continue
		else:				
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" %\
				(quote(href), quote(stitle), quote(img_src))
			addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=img_src, 
				thumb=img_src, fparams=fparams, tagline=img_alt)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Kika-Videos eines Bündels aus Kika_VideosBuendelAZ oder Kika_VideosBeliebt 
# 30.08.2020 Folgeseiten-Auswertung hinzugefügt
#	
def Kika_Videos(path, title, thumb, pagenr=''):
	PLog('Kika_Videos:')
	if pagenr == '':
		pagenr  =  1
	pagenr = int(pagenr)
	PLog(pagenr)
	title_org = title; thumb_org = thumb
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_VideosAZ:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	if page.find('dataURL:') < 0:		  # ohne 'dataURL:' - ohne kein Link zu xml-Seite, also keine Videos.
		msg1 = "Leider kein Video gefunden zu:"
		msg2 = title
		MyDialog(msg1, msg2, '')	
		return li
		
	videos = blockextract('class="av-playerContainer"', page)
	PLog(len(videos))
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	for s in videos:					
		href = ref = stringextract('dataURL:\'', '\'}', s)				# Link Videodetails  (..avCustom.xml)
		# PLog(href);   # PLog(s);   # Bei Bedarf
		img = stringextract('<noscript>', '</noscript>', s).strip()		# Bildinfo separieren
		img_alt = stringextract('alt=\"', '\"', img)	
		img_alt = unescape(img_alt)	
		img_src = stringextract('src="', '"', img)
		if img_src.startswith('http') == False:
			img_src = BASE_KIKA + img_src

		stitle = stringextract('title="', '"', s)
		duration = stringextract('icon-duration">', '</span>', s)	
		tag = duration + ' Minuten'	
		
		stitle = unescape(stitle); stitle = repl_json_chars(stitle)	
		img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt);	
			
		PLog('Satz3:')		
		PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src);
		PLog(tag); 
		href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src); img_alt=py2_encode(img_alt);
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'summ': '%s', 'duration': '%s'}" %\
			(quote(href), quote(stitle), quote(img_src), quote(img_alt), quote(duration))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=tag, summary=img_alt, mediatype=mediatype)
			
	pos = page.find('<!--The bottom navigation')						# Seite auf Folgeseiten prüfen			
	page = page[pos:]
	if 'class="bundleNavi' in page:
		pagelist = blockextract('class="bundleNaviItem', page)
		next_pagenr = int(pagenr + 1)		
		PLog('pagelist: %d, next_pagenr: %d' % (len(pagelist), next_pagenr))
		href=''
		if next_pagenr-1 < len(pagelist):								# Basis 0
			for item in pagelist:
				title = stringextract('title="">', '</a>', item)
				PLog(title)
				if title == str(next_pagenr):							# Basis 0
					href = BASE_KIKA + stringextract('href="', '"', item)
					break
		if href:
			li = xbmcgui.ListItem()										# Kontext-Doppel verhindern
			tag = "weiter zu Seite %s" % str(next_pagenr) 
			href=py2_encode(href); title_org=py2_encode(title_org); 
			thumb_org=py2_encode(thumb_org); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'pagenr': '%d'}" %\
				(quote(href), quote(title_org), quote(thumb_org), next_pagenr)
			addDir(li=li, label="Mehr..", action="dirList", dirID="resources.lib.childs.Kika_Videos", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
					
# ----------------------------------------------------------------------
# Kika_Barrierearm: Videos mit Gebärdensprache + als Hörfilme
# 1. Durchgang Navigation	
# 2. Durchgang: einz. Videos (rubrik)
#
def Kika_Barrierearm(path, title, thumb, rubrik=''):
	PLog('Kika_Barrierearm:')
	PLog(rubrik)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_Barrierearm:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
		
	#------------------------------------------
	if rubrik == '':							# 1. Durchgang Navigation
		PLog('Stufe1:')	
		pos = page.find("bottom navigation -->")
		page = page[pos:]
		nav_items =  blockextract('"bundleNaviItem', page)
		PLog(len(nav_items))
		
		thumb = R(ICON_DIR_FOLDER)
		if u'Hörfilme' in title:
			fanart = GIT_AD
		else:
			fanart = GIT_DGS
		thumb = R(ICON_DIR_FOLDER)	
			
		for item in nav_items:
			path = BASE_KIKA + stringextract('href="', '"', item)
			title = stringextract('title="">', '<', item)
			
			path=py2_encode(path); title=py2_encode(title); thumb=py2_encode(thumb);
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'rubrik': '%s'}"  %\
				(quote(path), quote(title), quote(thumb), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Barrierearm", 
				fanart=fanart, thumb=thumb, tagline=title, fparams=fparams)
	
	else:	
	#------------------------------------------	# 2. Durchgang: einz. Videos (rubrik)
		PLog('Stufe2:')	
		PLog(len(page))
		videos = blockextract('class="av-playerContainer"', page)	# wie Kika_Videos, ohne 
		PLog(len(videos))											#	bottom navigation
		
		mediatype='' 		
		if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
			mediatype='video'
		for s in videos:					
			href = ref = stringextract('dataURL:\'', '\'}', s)		# Link Videodetails  (..avCustom.xml)
			# PLog(href);   # PLog(s);   # Bei Bedarf
			img = stringextract('<noscript>', '</noscript>', s).strip()	# Bildinfo separieren
			img_alt = stringextract('alt=\"', '\"', img)	
			img_alt = unescape(img_alt)	
			img_src = stringextract('src="', '"', img)
			if img_src.startswith('http') == False:
				img_src = BASE_KIKA + img_src

			stitle = stringextract('title="', '"', s)
			duration = stringextract('icon-duration">', '</span>', s)	
			tagline = duration + ' Minuten'	
			
			stitle = unescape(stitle); stitle = repl_json_chars(stitle)	
			img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt);	
				
			PLog('Satz8:')		
			PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src);
			PLog(tagline); 
			href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src); img_alt=py2_encode(img_alt);
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'summ': '%s', 'duration': '%s'}" %\
				(quote(href), quote(stitle), quote(img_src), quote(img_alt), quote(duration))
			addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", fanart=img_src, 
				thumb=img_src, fparams=fparams, tagline=img_alt, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Kikaninchen - Seitenliste Sendungsvideos 
# 30.12.2021 Cache ergänzt (hier nur Leitseite) 			
def Kikaninchen_Videoseite():
	PLog('Kikaninchen_Videoseite')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kika.de/kikaninchen/sendungen/videos-kikaninchen-100.html'
	page = Dict("load", "KikaninchenAZ", CacheTime=KikaCacheTime)
	if page == False or page == '':
		page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kikaninchen_Videoseite:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	else:
		Dict("store", "KikaninchenAZ", page)
														# Buchstabenblock (2 x vorh.):
	items = stringextract('class="bundleNaviWrapper"', '"modCon"', page)
	items = blockextract('bundleNaviItem', items)		# nur aktive Buchstaben
	PLog(len(items))
	
	for s in items:	
		# PLog(s)
		seite =  stringextract('title="">', '</a>', s).strip()
		if '...' in seite:					# Ende Liste
			seite = "0-9"
		if "disabled" in s or seite == '':
			continue 
		PLog(seite)
		title = 'Kikaninchen Videos: Seite ' + seite
		tag = 'Sendungen mit ' + seite
		# img_src = R(ICON_DIR_FOLDER)
		img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % seite
		
		href = BASE_KIKA + stringextract('href="', '"', s)
		
		PLog(href); PLog(title); PLog(img_src)
		href=py2_encode(href); 		
		fparams="&fparams={'path': '%s'}" % (quote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Videos", fanart=GIT_KANINCHEN, 
			thumb=img_src, fparams=fparams, tagline=tag)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Kikaninchen - Sendungsvideos, mehrere Seiten - ermittelt die Videos
#	zu einer einzelnen (Buchstaben-)Seite
#	zusammengelegt mit 	playerContainer() der Plexversion	
def Kikaninchen_Videos(path):
	PLog('Kikaninchen_Videos')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kikaninchen_Videos:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	videos =  blockextract('class="av-playerContainer"', page)	# 16 pro Seite
	PLog(len(videos))
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	
	for s in videos:					 # stringextract('', '', s)
		href = ref = stringextract('dataURL:\'', '\'}', s)					# Link Videodetails  (..avCustom.xml)
		PLog(href);   # PLog(s);   # Bei Bedarf
		img = stringextract('<noscript>', '</noscript>', s).strip()			# Bildinfo separieren
		img_alt = stringextract('alt="', '"', img)	
		img_alt = unescape(img_alt)	
		img_src = stringextract('src="', '"', img)
		if img_src.startswith('http') == False:
			img_src = BASE_KIKA + img_src
		stitle = stringextract('title="', '"', s)
		stitle = unescape(stitle)	
		duration = stringextract('icon-duration">', '</span>', s)	
		tagline = duration + ' Minuten'	
		
		stitle = repl_json_chars(stitle)
		img_alt = repl_json_chars(img_alt);
		
		PLog(href); PLog(stitle); PLog(img_src); PLog(img_alt)
		href=py2_encode(href); 		
		href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src); img_alt=py2_encode(img_alt);
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'summ': '%s', 'duration': '%s'}" %\
			(quote(href), quote(stitle), quote(img_src), quote(img_alt), quote(duration))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=tagline, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
# ----------------------------------------------------------------------			
# 18.06.2017: KikaninchenLieder ersetzt die Kikaninchen Kramkiste (xml-Seite mit mp3-Audioschnipsel, abgeschaltet)
# 	Unterseite 'Singen + Tanzen' von http://www.kikaninchen.de/index.html?page=0
def KikaninchenLieder():	
	PLog('KikaninchenLieder')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kikaninchen.de/kikaninchen/lieder/liederkikaninchen100.json'	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kikaninchen_Videos:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
			
	records = page.split('documentCanvasId')
	PLog(len(records))						
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	for rec in records:
		href = stringextract('avCustomUrl":"', '"', rec)
		if href == '':
			continue					
		img_src = stringextract('urlScheme":"', '**imageVariant**', rec)
		PLog(img_src)
		if img_src.startswith('http') == False:
			img_src = 'http://www.kikaninchen.de' + img_src
		img_src = img_src + 'ident.jpg'						# ident = 800x800
		title = stringextract('title":"', '"', rec)
		altText =  stringextract('altText":"', '"', rec)
		titleText =  stringextract('titleText":"', '"', rec)
		
		title = repl_json_chars(title)	
		altText = repl_json_chars(altText)	
		titleText = repl_json_chars(titleText)	
		
		summ = ''
		if altText:
			summ = altText
		if summ == '':
			summ = titleText
										
		PLog(href); PLog(title); PLog(img_src); PLog(summ)
		href=py2_encode(href); title=py2_encode(title); img_src=py2_encode(img_src); summ=py2_encode(summ);
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'summ': '%s', 'duration': ''}" %\
			(quote(href), quote(title), quote(img_src), quote(summ))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=summ, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# Tonschnipsel aus verschiedenen Seiten
def Tonschnipsel():	
	PLog('Tonschnipsel')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button

	mp3_links =  [
		'kikaninchen = http://www.kikaninchen.de/kikaninchen/teaseraudio320-play.mp3',
		'Gitarre = http://www.kikaninchen.de/static_kkn/global/clickons/sounds/Gitarre_1.mp3',
		'Trompetenaffe =  http://www.kikaninchen.de/static_kkn/global/clickons/sounds/Trompetenaffe.mp3',
		'Frosch winkt = http://www.kikaninchen.de/static_kkn/global/clickons/sounds/Froschwinkt2_01.mp3?1493048916578',
		# 'Malfrosch =  http://www.kikaninchen.de/static_kkn/global/clickons/sounds/malfrosch1.mp3?1493048916578',
		'Grunz =  http://www.kikaninchen.de/static_kkn/global/clickons/sounds/grunz.mp3?1492871718285',
		'Huhu = http://www.kikaninchen.de/static_kkn/global/clickons/sounds/huhu.mp3?1493022362691',
		'Schnippel = http://www.kikaninchen.de/static_kkn/global/clickons/sounds/schnippel.mp3?1493022362691',
		'Klacker = http://www.kikaninchen.de/static_kkn/global/clickons/sounds/dices.mp3?1492868784119', 
			#Kurzlieder von http://www.kikaninchen.de/kikaninchen/lieder/liederkikaninchen100.json:
		'Lieder	= http://www.kikaninchen.de/kikaninchen/lieder/teaseraudio288-play.mp3',
		'La, la, la = http://www.kikaninchen.de/kikaninchen/lieder/hilfeaudio104-play.mp3',
		'Haha, toll - so viele lustige Lieder = http://www.kikaninchen.de/kikaninchen/lieder/hilfeaudio106-play.mp3',
		'Höre dir Lieder an und singe mit! = http://www.kikaninchen.de/kikaninchen/lieder/hilfeaudio102-play.mp3',
		'Ja, lass uns singen und dazu tanzen! = http://www.kikaninchen.de/kikaninchen/lieder/hilfeaudio100-play.mp3',		
		]
	PLog(len(mp3_links))
	
	for link in mp3_links:
		title = link.split('=')[0].strip()
		url = link.split('=')[1].strip()

		PLog(url);PLog(title);
		thumb=R('radio-podcasts.png')
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': ''}" % (quote(url), 
			quote(title), quote(thumb))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=title, mediatype='music')
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ######################################################################
# einzelnes Video
# 07.12.2022 Umbau nach Webänderungen (vormals xml-Seite)			
# path enthält die api-Seite mit Details. Hier direkt
#	weiter mit der assets-Url zu den Videoquellen
#
def Kika_SingleBeitrag(path, title, thumb, Plot):
	PLog('Kika_SingleBeitrag: ' + path)
	title_org = title
		
	path = path + "/assets"
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_SingleBeitrag:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button

	Plot_par = Plot
	summ = Plot.replace("||", "\n")

	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	url_m3u8 = stringextract('"auto","url":"', '"', page) 
	sub_path = stringextract('"webvttUrl":"', '"', page)	# Altern.: subtitle-Url tt:style 
	
	HBBTV_List=''										# nur ZDF
	HLS_List=[]; Stream_List=[];
	
	href=url_m3u8;  geoblock=''; descr='';	
	geoblock=''; descr=summ;				
	img = thumb

	quality = u'automatisch'
	HLS_List.append('HLS automatische Anpassung ** auto ** auto ** %s#%s' % (title,url_m3u8))
	Stream_List = ardundzdf.Parseplaylist(li, href, img, geoblock, descr, stitle=title, buttons=False)
	if type(Stream_List) == list:					# Fehler Parseplaylist = string
		HLS_List = HLS_List + Stream_List
	else:
		HLS_List=[]
	PLog("HLS_List: " + str(HLS_List)[:80])
	
	assets = blockextract('"profileName"', page)
	MP4_List = Kika_VideoMP4get(title, assets)
	PLog("download_list: " + str(MP4_List)[:80])
	Dict("store", 'KIKA_HLS_List', HLS_List) 
	Dict("store", 'KIKA_MP4_List', MP4_List) 
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_ready:');
	Plot = "Titel: %s\n\n%s" % (title_org, summ)				# -> build_Streamlists_buttons
	PLog('Plot:' + Plot)
	thumb = img; ID = 'KIKA'; HOME_ID = "Kinderprogramme"
	ardundzdf.build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ------------------------------
def Kika_VideoMP4get(title, assets):	
	PLog('Kika_VideoMP4get:')
	
	href=''; quality=''
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	for s in assets:
		PLog(s[:100])		
		frameWidth = stringextract('frameWidth":', ',', s)	
		frameHeight = stringextract('frameHeight":', ',', s)
		href = stringextract('"url":"', '"', s)
		href = href.replace("http:", "https:")							# Redakt.-Fehler? (bisher nur bei mp4-Quellen)
		bitrate =  stringextract('<bitrateVideo>', '</', s)
		if bitrate == '':
			if '_' in href:
				try:
					bitrate = re.search(u'_(\d+)k_', href).group(1)
				except Exception as exception:
					PLog(str(exception))
					bitrate = '0'
		profil =  stringextract('"profileName":"', '"', s)	
		res = frameWidth + 'x' + frameHeight
				
		# Bsp. Profil: Video 2018 | MP4 720p25 | Web XL| 16:9 | 1280x72
		# einige Profile enthalten nur die Auflösung, Bsp. 640x360
		#if 	"MP4 Web S" in profil or "320" in frameWidth:			# skip niedrige 320x180
		#	continue
		try:
			width = int(frameWidth)
		except Exception as exception:									# letzter Block
			PLog(str(exception))
			continue
				
		if "MP4 Web M Mobil" in profil or width <= 640:
			quality = u'mittlere'
		if "MP4 Web L mobil" in profil or width <= 960:
			quality = u'hohe'
		if "MP4 Web L |" in profil or width <= 1024:
			quality = u'sehr hohe'
		if "Web XL" in profil or width <= 1280:
			quality = u'Full HD'
			
		PLog("res: %s, bitrate: %s" % (res, bitrate)); 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4 Qualität: %s ** Bitrate %s ** Auflösung %s ** %s" % (quality, bitrate, res, title_url)
		download_list.append(item)

	return download_list
			
# ----------------------------------------------------------------------
# Jubiläumspodcast (25 Jahre Kika), 14-tätig
# aktuell (16.02.2022): 4 Folgen, geplant: 25
# 2 Durchläufe, xml_path: 1 Podcast mit Details + mp4-Quelle
def gen_alpha(xml_path='', thumb=''):
	PLog('gen_alpha:')

	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	base = "https://kommunikation.kika.de"
	
	if xml_path == '':							# 1. html-, 2. xml-Seite 
		path = "https://kommunikation.kika.de/ueber-kika/25-jahre/podcast/generation-alpha-podcast-100.html"
	else:
		path = xml_path
		
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_SingleBeitrag:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
			
	if xml_path == '':							# 1. Durchlauf: Liste Podcasts
		items = blockextract('class="av-playerContainer', page)
		PLog(len(items))
		for s in items:			
			img = stringextract('<noscript>', '</noscript>', s)
			if '|' in img:
				title = stringextract('alt="', '|', img)
				img_alt = stringextract('title="', '"', img)
			else:
				title = stringextract('alt="', '"', img)
			img_alt = stringextract('title="', '"', img)
			img_src = base + stringextract('src="', '"', img)
			
			xml_path = stringextract("dataURL:'", "'", s)
			dur = stringextract('duration">', '</', s)
			
			tag = "Dauer: %s" % dur
			summ = img_alt
			title = unescape(title)
			summ = unescape(summ)

			PLog('Satz9:')		
			PLog(xml_path);PLog(title);PLog(img_alt);PLog(img_src);
			xml_path=py2_encode(xml_path); img_src=py2_encode(img_src)
			fparams="&fparams={'xml_path': '%s', 'thumb': '%s'}" % (quote(xml_path), quote(img_src))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.gen_alpha", fanart=KIKA_START, 
				thumb=img_src, fparams=fparams, tagline=tag, summary=summ)
	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:	# ---------------------------		# 2. Durchlauf: einz. Podcast
			
			title = stringextract("<headline>", "</headline>", page)
			top = stringextract("<topline>", "</topline>", page)
			summ1 = stringextract("<title>", "</title>", page)
			summ2 = stringextract("<teaserText>", "</teaserText>", page)
			sday = stringextract("<webTime>", "</webTime>", page)	# gesendet
			dur = stringextract("<duration>", "</duration>", page)
			
			tag = "Dauer: %s | %s" % (dur, top)
			summ = "%s\n%s" % (summ1, summ2)
			Plot = "%s\n\n%s" % (tag, summ)
			
			assets = blockextract('<asset>', page)
			PLog(len(assets))
			url=''
			for a in assets:
				profil = stringextract("<profileName>", "</profileName>", a) # Codec
				if "MP3" in profil:
					url = stringextract("Url>", "</", a)
					size = stringextract("<fileSize>", "</fileSize>", a)
					break	
		
			PLog('Satz10:')		
			PLog(url);PLog(title);PLog(thumb);
			if url:				
				PlayAudio(url, title, thumb, Plot)
	return

# ----------------------------------------------------------------------			
#								tivi
# ----------------------------------------------------------------------			
def Tivi_Search(query=None, title='Search', pagenr=''):
	PLog("Tivi_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='ZDF')
	PLog(query)
	if  query == None or query.strip() == '':
		# return ""
		return Main_TIVI("tivi") # sonst Wiedereintritt Tivi_Search bei Sofortstart, dann Absturz Addon
	query_org = query	
	query=py2_decode(query)		# decode, falls erf. (1. Aufruf)

	PLog('Tivi_Search:'); PLog(query); PLog(pagenr); 

	ID='Search'
	Tivi_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=ZDFtivi&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1

	path = Tivi_Search_PATH % (query, pagenr) 
	PLog(path)	
	page, msg = get_page(path=path)	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog("searchResult: " + searchResult)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')										# Home-Button

	# Der Loader in ZDF-Suche liefert weitere hrefs, auch wenn weitere Ergebnisse fehlen -
	#	dto ZDFtivi
	if searchResult == '0' or 'class="artdirect"' not in page:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
		msg1 = 'Keine Ergebnisse (mehr) zu: %s' % query  
		MyDialog(msg1, '', '')
		return li	
				
	
	# anders als bei den übrigen ZDF-'Mehr'-Optionen gibt der Sender Suchergebnisse bereits
	#	seitenweise aus, hier umgesetzt mit pagenr - offset entfällt	
	li, page_cnt = ardundzdf.ZDF_get_content(li=li, page=page, ref_path=path, ID=ID)
	PLog('li, page_cnt: %s, %s' % (li, page_cnt))
	
	if page_cnt == 'next':							# mehr Seiten (Loader erreicht)
		li = xbmcgui.ListItem()						# Kontext-Doppel verhindern
		pagenr = int(pagenr) + 1
		query = query_org.replace('+', ' ')
		path = Tivi_Search_PATH % (query, pagenr)	# Debug
		PLog(pagenr); PLog(path)
		title = "Mehr Ergebnisse in ZDFtivi suchen zu: >%s<"  % query
		query_org=py2_encode(query_org); 
		fparams="&fparams={'query': '%s', 'pagenr': '%s'}" %\
			(quote(query_org), pagenr)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)	# Absturz Addon bei Sofortstart - s.o.

# ----------------------------------------------------------------------			
def Tivi_Woche():
	PLog('Tivi_Woche:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	wlist = range(0,8)							# tivi zeigt Sendungen für 8 Tage
	now = datetime.datetime.now()
	img_src = R(ICON_DIR_FOLDER)

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")			# Formate s. man strftime (3)
		punkte = '.'
		iWeekday = ardundzdf.transl_wtag(rdate.strftime("%A"))
		tiviDate = "%s, %s" % (iWeekday, iDate) 	# Bsp. Freitag, 08.09.2017 	
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		
		# Log(iDate); Log(iWeekday); Log(tiviDate)
		#title = ("%10s ..... %10s"% (iWeekday, iDate))	 # Formatierung in Plex ohne Wirkung
		title = iDate + ' | ' + iWeekday	 # Bsp.: 07.07.2016 | Freitag 
		PLog(tiviDate); PLog(title); 
		tiviDate=py2_encode(tiviDate); title=py2_encode(title);		
		fparams="&fparams={'day': '%s', 'title': '%s'}" % (quote(tiviDate), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_Woche_Sendungen", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=title)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# tivi VERPASST
# im Web fehlend: Uhrzeiten. Die Sendungen finden sich auch auf www.zdf.de/sendung-verpasst,
#	dort auch mit Uhrzeiten, allerdings fehlt die Senderangabe ZDFtivi in data-station 
#	sondern in teaser-cat-category.
#			
def Tivi_Woche_Sendungen(day, title):
	PLog('Tivi_Woche_Sendungen: ' + day)
		
	path = 'https://www.zdf.de/kinder/sendung-verpasst' 	# kompl. Woche						
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Tivi_Woche_Sendungen:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	msg1 = title											# notification
	msg2 = "ZDF-tivi"
	icon = GIT_CAL
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)
	
	# Home-Button in ZDFRubrikSingle
	ardundzdf.ZDFRubrikSingle(title, path, clus_title=day, page=page)					
	return

# ----------------------------------------------------------------------
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 			
def Tivi_AZ():
	PLog('Tivi_AZ:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	azlist = list(string.ascii_uppercase)
	# azlist.insert(0, '0-9')
	azlist.append('0 - 9')						# ZDF-Vorgabe (vormals '0+-+9')

	for element in azlist:	
		# PLog(element)
		button = element
		if button == '0 - 9':
			button = '0-9'						# für Icon anpassen
		title = "Sendungen mit " + button
		#img_src = R(ICON_DIR_FOLDER)
		#img_src = "Buchstabe_%s.png"  % button
		img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
		
		PLog(img_src)
		button=py2_encode(button); title=py2_encode(title);		
		fparams="&fparams={'name': '%s', 'char': '%s'}" % (quote(title), quote(button))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ_Sendungen", fanart=R(ICON_DIR_FOLDER), 
			thumb=img_src, fparams=fparams, tagline=title)
 
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# Alle Sendungen, char steuert Auswahl 0-9, A-Z
# 12.12.2019 Nutzung ZDF_get_content statt get_tivi_details
def Tivi_AZ_Sendungen(name, char=None):	
	PLog('Tivi_AZ_Sendungen:'); PLog(char)
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	char_tmp = char
	if char_tmp == '0-9':
		char_tmp = '0 - 9'						# ZDF-Vorgabe (vormals '0+-+9')
	path = 'https://www.zdf.de/kinder/sendungen-a-z?group=%s'	% char_tmp
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Tivi_AZ_Sendungen:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	page = stringextract('class="b-content-teaser-list"', '>Direkt zu ...</h2>', page)
	PLog(len(page))
	sendungen = blockextract('class="artdirect', page)
	PLog(len(sendungen))
	if len(sendungen) == 0:	
		msg1 = "Leider kein Video gefunden zu:"
		msg2 = name
		msg3 = path
		MyDialog(msg1, msg2, msg3)	
		return li
	
	# Sendungsdetails holen, ID: Einzelvideos auswerten
	li = ardundzdf.ZDF_get_content(li, page, ref_path=path, ID='A-Z')				
							
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 12.12.2019 get_tivi_details entfernt  (Nutzung in Plex-Version:
#	Tivi_AZ_Sendungen, Tivi_Woche_Sendungen, TiviTip, 
#	Tivi_SinglePage)
# def get_tivi_details(li, sendungen, path):			
# ----------------------------------------------------------------------
# 12.12.2019 Tivi_SinglePage entfernt - Auswertung durch ZDFRubrikSingle
#	in Tivi_Woche_Sendungen
# def Tivi_SinglePage(title, path, ID=None, key=None):
# ----------------------------------------------------------------------
# 12.12.2019 SingleBeitragTivi entfernt - Auswertung durch durch
#	ZDF_getVideoSources im Verlauf von ZDF_get_content,  ZDFStart,
#	ZDFRubrikSingle.
# def SingleBeitragTivi(path, title):
# ----------------------------------------------------------------------












