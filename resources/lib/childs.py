# -*- coding: utf-8 -*-
################################################################################
#				childs.py - Teil von Kodi-Addon-ARDundZDF
#		Rahmenmodul für Kinderprg div. Regionalsender von ARD und ZDF
#
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
################################################################################
#	
#	Stand: 20.06.2021

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

import ardundzdf					# -> ParseMasterM3u, transl_wtag, get_query
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

BASE_ZDF		= 'http://www.zdf.de'
BASE_KIKA 		= 'http://www.kika.de'
BASE_TIVI 		= 'https://www.zdf.de/kinder'

# Icons
ICON 			= 'icon.png'		# ARD + ZDF
ICON_CHILDS		= 'childs.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MAIN_TVLIVE= 'tv-livestreams.png'
ICON_MEHR 		= "icon-mehr.png"
ICON_SEARCH 	= 'ard-suche.png'
ICON_ZDF_SEARCH = 'zdf-suche.png'				
# Github-Icons zum Nachladen aus Platzgründen
GIT_KIKA		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kika.png?raw=true"
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

KikaCacheTime = 1*86400					# Addon-Cache für A-Z-Seiten: 1 Tag


# ----------------------------------------------------------------------			
def Main_childs():
	PLog('Main_childs:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
		
	fparams="&fparams={'title': '%s'}" % "KIKA"
	addDir(li=li, label= "KIKA", action="dirList", dirID="resources.lib.childs.Main_KIKA", fanart=R(ICON_CHILDS), 
		thumb=GIT_KIKA, fparams=fparams)
		
	fparams="&fparams={'title': '%s'}" % "tivi"
	addDir(li=li, label= "tivi", action="dirList", dirID="resources.lib.childs.Main_TIVI", fanart=R(ICON_CHILDS), 
		thumb=GIT_ZDFTIVI, fparams=fparams)


	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------			
def Main_KIKA(title):
	PLog('Main_KIKA:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
		
	title="Suche in KIKA"
	summ = "Suche Sendungen in KIKA"
	fparams="&fparams={'query': '', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Search", fanart=GIT_KIKA, 
		thumb=R(ICON_SEARCH), fparams=fparams)
			
	title='KIKA Live gucken'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Live", fanart=GIT_KIKA,
		thumb=R(ICON_MAIN_TVLIVE), tagline='KIKA TV-Live', fparams=fparams)
	
	title=u'KiRaKa - Sendungen und Hörspiele'
	fparams="&fparams={}" 
	addDir(li=li, label=title , action="dirList", dirID="resources.lib.childs.Kiraka", fanart=GIT_KIKA,
		thumb=GIT_RADIO, tagline=title, fparams=fparams)
		
	title='Videos und Bilder (A-Z)'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBuendelAZ", fanart=GIT_KIKA,
		thumb=GIT_VIDEO, tagline=title, fparams=fparams)
		
	title='Die beliebtesten Videos (meist geklickt)'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBeliebt", fanart=GIT_KIKA,
		thumb=GIT_VIDEO, tagline=title, fparams=fparams)
		
	title='KiKANiNCHEN'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Menu", fanart=GIT_KIKA,
		thumb=GIT_KANINCHEN, tagline='für Kinder 3-6 Jahre', fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------			
def Main_TIVI(title):
	PLog('Main_TIVI:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
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
# Die Kika-Suche über www.kika.de/suche/suche104.html?q= ist hier nicht nutzbar, da 
#	script-generiert und außer den Bildern keine Inhalte als Text erscheinen.
# Lösung: Suche über alle Bündelgruppen (Kika_VideosBuendelAZ) und Abgleich
#	mit Sendungstitel. Damit nicht jedesmal sämtliche A-Z-Seiten neu geladen
#	werden müssen, lagern wir sie 1 Tag im Cache. Diese Cacheseiten werden von
#	Kika_VideosBuendelAZ mitgenutzt.	
#	 
def Kika_Search(query=None, title='Search', pagenr=''):
	PLog("Kika_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='ARD')
	PLog(query)
	query_org = unquote(query)
	query_org = query_org.replace('+', ' ')					# für Vergleich entfernen
	if  query == None or query.strip() == '':
		return ""

	# Home-Button in Kika_VideosBuendelAZ

	li, HrefList = Kika_VideosBuendelAZ(getHrefList=True)
	PLog("HrefList: " + str(len(HrefList)))
	found_hrefs=[]
	for path in HrefList: 
		fname = stringextract('allevideos-buendelgruppen100_', '.htm', path)
		page = Dict("load", fname, CacheTime=KikaCacheTime)
		if page == False:
			page, msg = get_page(path=path)	
		if page == '':								# hier kein Dialog
			PLog("Fehler in Kika_Search: " + msg)
		else:
			Dict("store", fname, page)				# im Addon-Cache speichern
		pos = page.find("The bottom navigation")		# begrenzen, es folgen A-Z + meist geklickt
		page = page[:pos]
		pageItems = blockextract('class="media mediaA">', page)	
		PLog(len(pageItems))

		for s in pageItems:			
			stitle = stringextract('class="linkAll" title="', '"', s)		
			stitle = cleanhtml(stitle); stitle = unescape(stitle);
			if up_low(query_org) in up_low(stitle):	
				href =  BASE_KIKA + stringextract('href="', '\"', s)
				if href in found_hrefs:				# Doppler vermeiden
					continue
				found_hrefs.append(href)
				img = stringextract('<noscript>', '</noscript>', s).strip()		# Bildinfo separieren
				img_alt = stringextract('alt="', '"', img)	
				img_src = stringextract('src="', '"', img)
				if img_src.startswith('http') == False:
					img_src = BASE_KIKA + img_src

				stitle = repl_json_chars(stitle)	
				img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt) 	
				
				PLog('Satz4:')
				PLog(query);PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src)
				href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src);
				
				fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" %\
					(quote(href), quote(stitle), quote(img_src))
				addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=img_src, 
					thumb=img_src, fparams=fparams, tagline=img_alt)

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
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('KiKA ') in up_low(webtitle): 	# Sender mit Blank!
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
def Kiraka():
	PLog('Kiraka:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	thumb 	= GIT_KIR
	title = u'KiRaKa - Sendungen zum Nachhören'
	tagline = u'Die Live-Sendung WDR 5 KiRaKa sieben Tage lang nachhören. Mit allem drum und dran.'
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kiraka_shows", fanart=GIT_RADIO, 
		thumb=thumb, fparams=fparams, tagline=tagline)
	
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
#			
def Kiraka_pods(title):
	PLog('Kiraka_pods:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	base = "https://kinder.wdr.de"
	path = base + "/radio/kiraka/hoeren/hoerspiele/kinderhoerspiel-podcast-102.html"
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kiraka_pods"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract('podcast-102-entry=', page)	
	for s in items:
		img = stringextract('srcset="', '"', s)
		if img.startswith('//'):				# //www1.wdr.de/..
			img = 'https:' + img
		else:									# /radio/kiraka/..
			img = base + img
		stitle = stringextract('mediaTitle">', '</', s)
		webid = stringextract("'id':'", "'", s) # podcast-102-entry="{'id':'audio-wie-viele..
			
		day = stringextract('mediaDate">', '</', s)	
		dur = stringextract('mediaDuration">', '</', s)	
		dur = cleanhtml(dur)
		descr = stringextract('"text">', '</p', s)
		descr = mystrip(descr); descr = unescape(descr)										
		
		tag = "%s | %s | %s | %s\n\n%s" % (title, stitle, day, dur, descr)
		Plot = tag.replace('\n', '||'); 
		
		PLog('Satz6:')
		PLog(img); PLog(stitle); PLog(webid); PLog(Plot);
		stitle=py2_encode(stitle); webid=py2_encode(webid);
		thumb=py2_encode(img); Plot=py2_encode(Plot); 
		fparams="&fparams={'webid': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(webid), 
			quote(stitle), quote(thumb), quote_plus(Plot))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kiraka_get_mp3", \
			fanart=GIT_KIR_SHOWS, thumb=thumb, fparams=fparams, tagline=tag, mediatype='music')
		
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
#	
def Kika_VideosBuendelAZ(path='', getHrefList=False, button=''): 
	PLog('Kika_VideosBuendelAZ: ' + path); PLog(button)
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	first=False; fname=''
	if button == '':								# A-Z-Liste laden
		path = 'https://www.kika.de/videos/allevideos/allevideos-buendelgruppen100.html'
		first=True
	else:
		fname = stringextract('allevideos-buendelgruppen100_', '.htm', path)

	page = Dict("load", fname, CacheTime=KikaCacheTime)
	if page == False:
		page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_VideosBuendelAZ:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
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
					break
				img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
				PLog("button: " + button); PLog("href: " + href)
				title = "Sendungen mit " + button
				fparams="&fparams={'path': '%s', 'button': '%s'}" % (quote(href), button)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_VideosBuendelAZ", fanart=GIT_KIKA,
					thumb=img_src, tagline=title, fparams=fparams)
				
		if getHrefList:							# nur hrefs return
			return li, HrefList	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True); 
		return
			
	# 2. Aufruf: Liste einer Gruppe 
	PLog("button: " + button);  PLog(first)
	pos = page.find("The bottom navigation")		# begrenzen, es folgen A-Z + meist geklickt
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
def Kika_VideosBeliebt(): 
	PLog('Kika_VideosBeliebt:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kika.de/videos/allevideos/allevideos-buendelgruppen100.html'
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
		tagline = duration + ' Minuten'	
		
		stitle = unescape(stitle); stitle = repl_json_chars(stitle)	
		img_alt = unescape(img_alt); img_alt = repl_json_chars(img_alt);	
			
		PLog('Satz3:')		
		PLog(href);PLog(stitle);PLog(img_alt);PLog(img_src);
		PLog(tagline); 
		href=py2_encode(href); stitle=py2_encode(stitle); img_src=py2_encode(img_src); img_alt=py2_encode(img_alt);
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'summ': '%s', 'duration': '%s'}" %\
			(quote(href), quote(stitle), quote(img_src), quote(img_alt), quote(duration))
		addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.Kika_SingleBeitrag", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=img_alt, mediatype=mediatype)
			
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
			tag = "weiter zu Seite %s" % str(next_pagenr) 
			href=py2_encode(href); title_org=py2_encode(title_org); 
			thumb_org=py2_encode(thumb_org); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'pagenr': '%d'}" %\
				(quote(href), quote(title_org), quote(thumb_org), next_pagenr)
			addDir(li=li, label="Mehr..", action="dirList", dirID="resources.lib.childs.Kika_Videos", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
					
# ----------------------------------------------------------------------
# Kikaninchen - Seitenliste Sendungsvideos  			
def Kikaninchen_Videoseite():
	PLog('Kikaninchen_Videoseite')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kika.de/kikaninchen/sendungen/videos-kikaninchen-100.html'
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kikaninchen_Videoseite:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
														# Buchstabenblock (2 x vorh.):
	items = stringextract('class="bundleNaviWrapper"', '"">...</a>', page)
	items = blockextract('bundleNaviItem', items)		# nur aktive Buchstaben
	PLog(len(items))
	
	for s in items:	
		# PLog(s)
		seite =  stringextract('title="">', '</a>', s).strip()
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
# einzelnes Video - xml-Seite
def Kika_SingleBeitrag(path, title, thumb, summ, duration):
	PLog('Kika_SingleBeitrag: ' + path)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Kika_SingleBeitrag:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	summ1 = stringextract('<broadcastDescription>', '</', page)
	summ2 = stringextract('<topline>', '</', page)
	summ = summ1 + ' ' + summ2
	summ = repl_json_chars(summ)
	Plot_par = summ

	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	assets = blockextract('<asset>', page)
	url_m3u8 = stringextract('<adaptiveHttpStreamingRedirectorUrl>', '</', page) # x-mal identisch
	sub_path = ''

	HBBTV_List=''										# nur ZDF
	HLS_List=[]; Stream_List=[];
	quality = u'automatisch'
	HLS_List.append('HLS automatische Anpassung ** auto ** auto ** %s#%s' % (title,url_m3u8))
			
	href=url_m3u8;  geoblock=''; descr='';					# für Stream_List n.b.
	img = thumb
	if href:
		Stream_List = ardundzdf.Parseplaylist(li, href, img, geoblock, descr, stitle=title, buttons=False)
		if type(Stream_List) == list:						# Fehler Parseplaylist = string
			HLS_List = HLS_List + Stream_List
		else:
			HLS_List=[]
	PLog("HLS_List: " + str(HLS_List)[:80])
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
		frameWidth = stringextract('<frameWidth>', '</frameWidth>', s)	
		frameHeight = stringextract('<frameHeight>', '</frameHeight>', s)
		href = stringextract('<progressiveDownloadUrl>', '</', s)
		bitrate =  stringextract('<bitrateVideo>', '</', s)
		if bitrate == '':
			if '_' in href:
				try:
					bitrate = re.search(u'_(\d+)k_', href).group(1)
				except Exception as exception:
					PLog(str(exception))
					bitrate = '0'
		profil =  stringextract('<profileName>', '</', s)	
		res = frameWidth + 'x' + frameHeight
				
		# Bsp. Profil: Video 2018 | MP4 720p25 | Web XL| 16:9 | 1280x72
		# einige Profile enthalten nur die Auflösung, Bsp. 640x360
		if 	"MP4 Web S" in profil or "480" in frameWidth:			# skip niedrige 320x180
			continue			
		if "MP4 Web M Mobil" in profil or "640" in frameWidth:
			quality = u'mittlere'
		if "MP4 Web L mobil" in profil or "960" in frameWidth:
			quality = u'hohe'
		if "MP4 Web L |" in profil or "1024" in frameWidth:
			quality = u'sehr hohe'
		if "MP4 Web XL" in profil or "1280" in frameWidth:
			quality = u'Full HD'
			
		PLog("res: %s, bitrate: %s" % (res, bitrate)); 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4 Qualität: %s ** Bitrate %s ** Auflösung %s ** %s" % (quality, bitrate, res, title_url)
		download_list.append(item)

	return download_list
			
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
	PLog('Tivi_Woche')
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
		
	# Home-Button in ZDFRubrikSingle
	ardundzdf.ZDFRubrikSingle(title, path, clus_title=day, page=page)				
	return

# ----------------------------------------------------------------------
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 			
def Tivi_AZ():
	PLog('Tivi_AZ')
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
	PLog('Tivi_AZ_Sendungen'); PLog(char)
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












