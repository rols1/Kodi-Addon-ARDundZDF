# -*- coding: utf-8 -*-
################################################################################
#				phoenix.py - Teil von Kodi-Addon-ARDundZDF
#				benötigt Modul yt.py (Youtube-Videos, MVW-Suche)
#		Videos der Phoenix_Mediathek auf https://www.phoenix.de/ 
#		Juni 2023: da Youtube-Videos nicht mehr verfügbar, Umstellung 
#					auf ARD-Mediathek (ardmediathek.de/phoenix)
#
#	30.12.2019 Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	
################################################################################
# 	<nr>13</nr>										# Numerierung für Einzelupdate
#	Stand: 12.09.2023

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
import re				# u.a. Reguläre Ausdrücke
import string

import ardundzdf					# -> get_query,test_downloads,get_zdf_search 
from resources.lib.ARDnew import *	# ab Juni 2023 (s.o.)
from resources.lib.util import *
import resources.lib.yt	as yt		# Rahmen für pytube, mögl. Dev.-Problem s. dort

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

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('phoenix_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 				# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_PHOENIX	= 'https://www.phoenix.de'
PLAYLIST 		= 'livesenderTV.xml'	  	# enth. Link für phoenix-Live											

# Icons
ICON 			= 'icon.png'				# ARD + ZDF
ICON_PHOENIX	= 'phoenix.png'	
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MEHR 		= "icon-mehr.png"
ICON_ZDF_SEARCH = 'zdf-suche.png'
ICON_ARD_SEARCH = 'ard-suche.png'						
							
# Github-Icons zum Nachladen aus Platzgründen
ICON_TVLIVE		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/tv-livestreams.png?raw=true'			
ICON_SEARCH		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/icon-search.png?raw=true'			
ICON_VERPASST	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Verpasst.png?raw=true'
	
CurSender = 'phoenix:phoenix::tv-phoenix.png:phoenix'	
# ----------------------------------------------------------------------			
def Main_phoenix():
	PLog('Main_phoenix:')
	
	li = xbmcgui.ListItem()
	liICON_TVLIVE = home(li, ID=NAME)			# Home-Button

	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'Sender: [B]alle Sender des ARD[/B] (nicht in phoenix allein)' 
		title=py2_encode(title); 
		func = "resources.lib.phoenix.Main_phoenix"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARD", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_PHOENIX), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)

	title="Suche auf phoenix"
	tag = "Suche Themen, Sendungen und Videos in phoenix"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Search", fanart=R(ICON_PHOENIX), 
		thumb=ICON_SEARCH, fparams=fparams, tagline=tag)
	# ------------------------------------------------------
			
	tag='[B]Phoenix Livestream[/B]'
	title,subtitle,vorspann,descr,href,sender,icon = get_live_data()
	title = '[B]LIVE: %s[/B]' % title
	
	if sender:
		tag = "%s | Herkunft: %s" % (tag, sender)
	summ = descr
	if subtitle:
		summ = '%s\n%s' % (subtitle, summ)
	if vorspann:
		summ = '%s\n%s' % (vorspann, summ)
	thumb = icon
	if icon == '':	
		thumb = ICON_TVLIVE
	Plot = "%s\n\n%s" % (tag, summ)
	Plot = Plot.replace("\n", "||")
		
	title=py2_encode(title); href=py2_encode(href); Plot=py2_encode(Plot);
	fparams="&fparams={'href': '%s', 'title': '%s', 'Plot': '%s'}" % (quote(href), quote(title), quote(Plot))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Live", fanart=R(ICON_PHOENIX),
		thumb=thumb, fparams=fparams, tagline=tag, summary=summ)
	# ------------------------------------------------------
	
	title = 'Startseite'
	tag = 'Startseite der phoenix-Mediathek' 
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Start", 
		fanart=R(ICON_PHOENIX), thumb=R("phoenix_Startseite.png"), tagline=tag, fparams=fparams)
	
	title = 'Sendung verpasst'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Verpasst", 
		fanart=R(ICON_PHOENIX), thumb=ICON_VERPASST, fparams=fparams)

	title = 'Sendungen A-Z'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_AZ", 
		fanart=R(ICON_PHOENIX), thumb=R("phoenix_az.png"), fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
			
# ----------------------------------------------------------------------
# die json-Seite enthält ca. 4 Tage EPG - 1. Beitrag=aktuell
# 15.08.2020 Verwendung ZDFstreamlinks (util) für href (master.m3u8)
#
def get_live_data():
	PLog('get_live_data:')
	path = "https://www.phoenix.de/response/template/livestream_json"
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "get_live_data:"
		msg2 = msg
		# MyDialog(msg1, msg2, '')
		PLog("%s | %s" % (msg1, msg2))	
	PLog(len(page))			
	
	title='';subtitle='';vorspann='';descr='';href='';sender='';
	thumb=''; icon=''
	if page:
		# Kurzf. möglich: {"title":"tagesschau","subtitel":"mit Geb\u00e4rdensprache",
		#	"typ":"","vorspann":""}
		if '":"' in page:					# möglich: '":"', '": "'
			page = page.replace('":"', '": "')
		page = page.replace('\\"', '*')	
		page = 	transl_json(page)					
		PLog(page[:80])
		title 	= stringextract('"titel": "', '"', page)		# titel!
		subtitle= stringextract('"subtitel": "', '"', page)
		vorspann= stringextract('"vorspann": "', '"', page)
		descr	= stringextract('"text": "', '"', page)			# html als Text
		sender	= stringextract('sender": "', '"', page)
		icon	= stringextract('bild_l": "', '"', page)		# bild_s winzig
		if icon == '':
			icon = stringextract('bild_m": "', '"', page)
		PLog("icon: " + icon)
		if icon != '' and icon.startswith('http') == False:
			icon = BASE_PHOENIX + icon

		title=transl_json(title); subtitle=transl_json(subtitle); 
		vorspann=transl_json(vorspann); 
		descr=cleanhtml(descr); descr=transl_json(descr)
		descr=unescape(descr); descr=descr.replace("\\r\\n", "\n")
		
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	href=''
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		if up_low('phoenix') in up_low(webtitle): 
			href = href
			break
	
	PLog("Satz6:")
	PLog(title); PLog(subtitle); PLog(vorspann); PLog(descr); PLog(href);
	PLog(sender); PLog(icon);					
	return title,subtitle,vorspann,descr,href,sender,icon
# ----------------------------------------------------------------------
# path via chrome-tools ermittelt. Ergebnisse im json-Format
# 25.05.2021 Suchlink an phoenix-Änderung angepasst
# 28.06.2021 erneut angepasst
# 09.11.2021 wegen key-Problem ("0", "1"..) Wechsel json -> string-Auwertung,
#	s. GetContent + ThemenListe
def phoenix_Search(query='', nexturl=''):
	PLog("phoenix_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='phoenix')
	PLog(query)
	if  query == None or query == '':
		#return ""
		Main_phoenix()					# Absturz nach Sofortstart-Abbruch
		
	title="Suche auf phoenix"
	ARDSearchnew(title, sender="phoenix", offset=0, query=query, homeID="phoenix")

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# Phoenix - TV-Livestream mit EPG
# 23.04.2022 Parseplaylist entfernt (ungeeignet für Mehrkanal-Streams)
# 
def phoenix_Live(href, title, Plot):	
	PLog('phoenix_Live:')

	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button

	img = ICON_TVLIVE
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true'	# Sofortstart
		PLog('Sofortstart: phoenix_Live')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot, live="true")
		return	
							
	tag = Plot.replace("||", "\n")
	
	title=py2_encode(title); href=py2_encode(href); img=py2_encode(img);
	Plot=py2_encode(Plot);
	label = title.replace('Live', 'auto')
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'live': 'true'}" %\
		(quote_plus(href), quote_plus(title), quote_plus(img), quote_plus(Plot))
	addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
		fparams=fparams, mediatype='video', tagline=tag) 		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
def phoenix_Start():	
	PLog('phoenix_Start:')

	title = 'Sendung verpasst'
	ARDStart(title, sender=CurSender, homeID="phoenix")

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
# ----------------------------------------------------------------------
# Nutzung api.ardmediathek.de in ARDnew. Die phoenix-eigene Webseite
#	listet zwar mehr Sendungen, die aber häufig keine Videos enthalten.
def Verpasst():	
	PLog('Verpasst:')

	title = 'Sendung verpasst'
	ARDVerpasst(title, CurSender=CurSender, homeID="phoenix")

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
def phoenix_AZ():	
	PLog('phoenix_AZ:')

	title = 'Sendungen A-Z'
	SendungenAZ(title, CurSender=CurSender, homeID="phoenix")

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------








