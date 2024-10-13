# -*- coding: utf-8 -*-
################################################################################
#				childs.py - Teil von Kodi-Addon-ARDundZDF
#		Rahmenmodul für Kinderprg div. Regionalsender von ARD und ZDF
#
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
################################################################################
#	
# 	<nr>31</nr>										# Numerierung für Einzelupdate
#	Stand: 12.10.2024

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

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('childs_python_3.x.x')
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

# ext. Icons zum Nachladen aus Platzgründen,externe Nutzung:						
#GIT_KIKA		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kika.png?raw=true"
KIKA_START		= "https://www.kika.de/bilder/startseite-104_v-tlarge169_w-1920_zc-a4147743.jpg"	# ab 07.12.2022
KIKA_VIDEOS		= "https://www.kika.de/videos/videos-110_v-tlarge169_zc-cc2f4e31.jpg"				# - " -
KIKA_AD			= "https://www.kika.de/audiodeskription/ad-110_v-tlarge169_zc-cc2f4e31.jpg?version=6313"
KIKA_DGS		= "https://www.kika.de/gebaerdensprache/dgs-110_v-tlarge169_zc-cc2f4e31.jpg?version=58142"
KIKA_SERIES		= "https://www.kika.de/videos/serie-100_v-tlarge169_zc-cc2f4e31.jpg?version=16437"
KIKA_FILME		= "https://www.kika.de/videos/film-108_v-tlarge169_zc-cc2f4e31.jpg?version=4412"
KIKA_WISSEN		= "https://www.kika.de/videos/wissen-108_v-tlarge169_zc-cc2f4e31.jpg?version=11506"
KIKA_SHOWS		= "https://www.kika.de/videos/show-100_v-tlarge169_zc-cc2f4e31.jpg?version=3229"
KIKA_LIVE		= "https://www.kika.de/live/bilder/live-102_v-tlarge169_zc-cc2f4e31.jpg?version=32751"
KIKA_GENALPHA	= "https://kommunikation.kika.de/ueber-kika/25-jahre/podcast/generation-alpha-100_v-tlarge169_zc-cc2f4e31.jpg?version=35225"	

GIT_AZ			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-AZ.png?raw=true"
				# Einzelbuchstaben zu A-Z siehe Tivi_AZ
GIT_CAL			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-calendar.png?raw=true"
GIT_VIDEO		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaVideo.png?raw=true"
GIT_RADIO		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/radio-kiraka.png?raw=true"
GIT_POPCORN		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaPopcorn.png?raw=true"
GIT_KANINCHEN	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchen.png?raw=true"
GIT_KANINVIDEOS	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenVideos.png?raw=true"
GIT_KRAMLIEDER	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenKramLieder.png?raw=true"
GIT_KRAMSCHNIPP	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchenKramSchnipsel.png?raw=true"
GIT_ZDFTIVI		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-zdftivi.png?raw=true"
GIT_TIVIHOME	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-home.png?raw=true"
GIT_TIVICAL		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-cal.png?raw=true"
GIT_KIR			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/kiraka.png?raw=true"
GIT_KIR_SHOWS	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/kiraka-shows.png?raw=true"
GIT_KIR_KLICK	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/klicker.png?raw=true"
GIT_DGS			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaDGS.png?raw=true"
GIT_AD			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaAD.png?raw=true"
GIT_ARD_KINDER	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-ard_kinder-familie.png?raw=true"

# 14.12.2022 1024x1024:
GIT_KIKASTART	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_KIKASTART.png?raw=true"
GIT_KIKALIVE	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_KIKALIVE.png?raw=true"
GIT_KIKAVIDEOS	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_KIKAVIDEOS.png?raw=true"
GIT_GENALPHA	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_GENALPHA.png?raw=true"
GIT_MAUSLIVE	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_MAUSLIVE.png?raw=true"


KikaCacheTime = 1*3600					# Addon-Cache für A-Z-Seiten: 1 Stunde
KIKA_HEADERS	="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}"


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

	# 07.09.2023 Geschichten für Kinder von 3 bis 6 nicht mehr vorh.
	title = u"Hörspaß für Kinder | ARD-Audiothek"						# neu ab 17.06.2023
	cluster_id = "entdecken-100:-601210988128917166"
	tag = u">Es war einmal ... Märchen\n>Hörspiele für Kinder ab 6\n>"
	tag = u"%s>Wer, wie, was - und warum?\n>Maus-Zoom\n>Familienkonzerte: Geschichten mit Musik" % tag
	summ = u"Mehr Hör-Geschichten für große und kleine Kinder findest du in der Audiothek in der Rubrik >Für Kinder<."
	fparams="&fparams={'cluster_id': '%s'}" % cluster_id
	addDir(li=li, label=title, action="dirList", dirID="Audio_get_homescreen", 
		fanart=R(ICON_CHILDS), thumb=R("ard-audiothek.png"), tagline=tag, summary=summ, fparams=fparams)

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
	
	title="Suche in KIKA"												# neu ab 07.12 2022
	summ = "Suche Sendungen in KiKA"
	fparams="&fparams={'query': '', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Search", 
		fanart=KIKA_START, thumb=R("kika-suche.png"), fparams=fparams)
			
	title='KiKA Live gucken'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Live", 
		fanart=KIKA_START, thumb=GIT_KIKALIVE, tagline='KIKA TV-Live', fparams=fparams)
		
	title='KiKA Programmvorschau'
	tag = u"Programmvorschau für eine Woche\n\nMit Klick zur laufenden Sendung"
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Vorschau", 
		fanart=KIKA_START, thumb=R(ICON_MAIN_TVLIVE), tagline=tag, fparams=fparams)

	title='KiKA Startseite' 											# neu ab 07.12 2022
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start",
		fanart=KIKA_START, thumb=GIT_KIKASTART, tagline=title, fparams=fparams)

	title='KiKA Videos'													# neu ab 07.12 2022
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos_Menu",
		fanart=KIKA_START, thumb=GIT_KIKAVIDEOS, tagline=title, fparams=fparams)
	
	title=u'MausLive'
	tag = u"%s\n\nDer Kinderradiokanal des WDR  (Nachfolgeseite für [B]KiRaKa[/B])" % title
	img = GIT_MAUSLIVE
	fparams="&fparams={}" 
	addDir(li=li, label=title , action="dirList", dirID="resources.lib.childs.MausLive",
		fanart=KIKA_START, thumb=img, tagline=tag, fparams=fparams)
		
	title=u'Kinderhörspiele der ARD-Audiothek'
	query = u"Kinderhörspiele"
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
	thumb = GIT_GENALPHA
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.gen_alpha", 
		fanart=KIKA_START, thumb=thumb, tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------
# 23.07.2024 tivi_Verpasst abgeschaltet wg. Ausfall cdn-api
#			
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
			
	title='tivi_Startseite'
	fparams="&fparams={'ID': '%s'}" % (title)
	addDir(li=li, label=title , action="dirList", dirID="ardundzdf.ZDF_Start", fanart=GIT_ZDFTIVI, 
		thumb=GIT_TIVIHOME, tagline=title, fparams=fparams)
		
	title = 'tivi_Verpasst' 	# ZDF_VerpasstWoche -> tivi_Verpasst
	fparams="&fparams={'name': 'ZDF-tivi_Verpasst', 'title': '%s', 'homeID': 'Kinderprogramme'}" % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_VerpasstWoche", fanart=GIT_ZDFTIVI, 
		thumb=GIT_TIVICAL, tagline=title, fparams=fparams)				

	title='tivi_Sendungen A-Z | 0-9'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ", fanart=GIT_ZDFTIVI, 
		thumb=GIT_AZ, tagline=title, fparams=fparams)

	title='tivi_ZDFchen'
	tag = "Für Kinder bis 6 Jahre"
	thumb = "https://www.zdf.de/assets/zdfchen-buehne-m-song-100~936x520?cb=1658852787035"
	url = "https://zdf-prod-futura.zdf.de/mediathekV2/document/zdfchen-100"
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
	addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=GIT_ZDFTIVI, 
		thumb=thumb, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 13.12.2022 neu: 'Kikaninchen Videos A-Z' und 'Kikaninchen Filme'			
def Kikaninchen_Menu():
	PLog('Kikaninchen_Menu')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	title='Kikaninchen Videos A-Z'				# 15.08.2023 allevideos864.html -> api/v1/
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KikaninchenVideosAZ", fanart=GIT_KANINCHEN, 
		thumb=GIT_KANINVIDEOS, tagline='für Kinder 3-6 Jahre', fparams=fparams)
	title='Kikaninchen Filme'					# www.kikaninchen.de/filme/filme-122.html ausgelagert von					
	fparams="&fparams={}"						#	Kikaninchen Videos ("Alle Filme")
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KikaninchenFilme", fanart=GIT_KANINCHEN, 
		thumb=GIT_POPCORN, tagline='für Kinder 3-6 Jahre', fparams=fparams)
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
# 07.12.2022 Neu nach Webänderungen	
def Kika_Videos_Menu():
	PLog('Kika_Videos_Menu')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button

	title='Videos: Start'
	fparams="&fparams={'title': '%s'}" % title
	tag = "KiKA bietet dir in dieser Kinder-Mediathek die Videos deiner liebsten Kinderfilme, Kinderserien, Kindershows und Wissenssendungen für Kinder. Schau rein!"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_VIDEOS, tagline=tag, fparams=fparams)
	title='Videos: Serien'
	tag = "Bei KiKA findest du alte und neue Folgen deiner Lieblingsserien: Schloss Einstein, Wissen macht Ah!, KiKA LIVE und viele mehr. Schau rein!"
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_SERIES, tagline=tag, fparams=fparams)
	title='Videos: Filme'
	tag = "Schau dir an, welche Filme bei KiKA laufen. Entdecke spannende, rätselhafte und lustige Kinderfilme und Märchen für Kinder in der KiKA Mediathek."
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_FILME, tagline=tag, fparams=fparams)
	title='Videos: Wissen'
	tag = "Experimente für Kinder, Physik einfach erklärt und Antworten auf Fragen, die du dir immer gestellt hast. Das findest du bei den Wissenssendungen von KiKA."
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_WISSEN, tagline=tag, fparams=fparams)
	title='Videos: Shows'
	tag = "Bei KiKA findest aufregende Shows, die großen Spaß machen. Verpasse keine Folge deiner Lieblingssendung: Von *Dein Song* bis *Die beste Klasse Deutschlands*"
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_SHOWS, tagline=tag, fparams=fparams)
	title='Videos: A-Z'
	tag = "Sendungen von A bis Z"
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=GIT_AZ, tagline=tag, fparams=fparams)
	title=u'Videos: mit Hörfassung'
	tag = "Welche Hörfilme gibt es bei KiKA? Hier findest du Filme und Folgen von KiKA-Sendungen mit Audiodeskription."
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_AD, tagline=tag, fparams=fparams)
	title=u'Videos: mit Gebärdensprache'
	tag = "Hier findest du Folgen und Videos von KiKA-Sendungen mit Deutscher Gebärdensprache. Schau dir die *Sesamstraße* oder *Die Sendung mit der Maus* an."
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Videos", fanart=KIKA_VIDEOS, 
		thumb=KIKA_DGS, tagline=tag, fparams=fparams)
	
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
# 19.11.2022 Verwendung der Websuche (../suche/suche104.html?q=..) - früher nicht
#	 nutzbar, da script-generiert. Vorherigen Code der Suche über alle Bündelgruppen 
#	(Kika_VideosBuendelAZ) gelöscht.
# 06.12.2022 Neu nach Webseitenänderungen
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
# 06.12.2022 Neu nach Webseitenänderungen
# 1. Durchlauf Buttons Highlights + Cluster
# 2. Durchlauf Cluster -> Kika_Rubriken
#
def Kika_Start(show_cluster='', path=''):
	PLog("Kika_Start: " + show_cluster)
	PLog(path)
	path_org=path

	if path == "":
		path=BASE_KIKA
	page, msg = get_page(path)
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
			cnt=0
			for item in items:
				cnt=cnt+1												# Folge-Index zum verketten
				title = stringextract('"title":"', '"', item)
				title=repl_json_chars(title)
				PLog("title: %s, show_cluster: %s" % (title, show_cluster))
				summ = "Folgeseiten"
				ID = "Start_2"
				if title and title in show_cluster:
					img, img_alt = Kika_get_img(item)					# 1. Bild
					PLog("found_cluster: " + show_cluster)
					pos2 = item.find("viewVariant")						# boxType begrenzen
					PLog(pos2); PLog(item[-60:])						# Check viewVariant
					item = item[:pos2]
					
					# Bsp. für Verketten www.kika.de/videos/filme/kinderfilme-100:
					if cnt < len(items):
						PLog("check_Subchannel:")						# Doku: x_channel_chained.json
						if '"docType":"videoSubchannel"' in items[cnt]:	# check Subchannel -> verketten
							PLog("chain_Subchannel:")
							item = str(item + items[cnt])
						else:
							pos = item.find('"structureBrand":')		# Alternative
							if pos > 0:
								item_id = stringextract('"id":"', '"', item[pos:])
								if item_id in items[cnt]:							
									PLog("chain_id:")
									item = str(item + items[cnt])
					
					Kika_Rubriken(page=item, title=title, thumb=img, ID='Start_2',li=li)	# Seitensteuerung Kika_Rubriken	
					break
	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
	# ------------------------------------------------------------------
	# 1. Durchlauf: Buttons Stage + Cluster 
	PLog("Start_1:")
	path_org=py2_encode(path_org)
	if '"stageContent":null' not in page:									# fehlt in DGS- und AD-Videos
		title = '[B]Highlights[/B]'											# Highlights voranstellen
		tag = "Folgeseiten"
		show_cluster = "Highlights"
		
		fparams="&fparams={'show_cluster': 'Highlights', 'path': '%s'}" % quote(path_org)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start", 
			fanart=KIKA_START, thumb=KIKA_START, fparams=fparams, tagline=tag)
	
	items = blockextract('"boxType":', page)
	PLog("items1: %d" % len(items))
	for item in items:
		title = stringextract('"title":"', '"', item)
		title=repl_json_chars(title)
		PLog("title: " + title)
		if "Jetzt live" in title or title == "":						# skip Live + Game
			continue
			
		title=py2_encode(title)
		img, img_alt = Kika_get_img(item)								# 1. Bild
		tag = "Folgeseiten"
		fparams="&fparams={'show_cluster': '%s', 'path': '%s'}" % (quote(title), quote(path_org))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Start", 
			fanart=KIKA_START, thumb=img, fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen	
# Verteiler für Kika_Videos_Menu	
def Kika_Videos(title):
	PLog('Kika_Videos: ' + title)

	if title.endswith("Start"):
		path = "https://www.kika.de/videos/kindervideos-videos-fuer-kinder-100"
		Kika_Start(path=path)
	if title.endswith("Serien"):
		path = "https://www.kika.de/videos/serien/kinderserien-100"
		Kika_Start(path=path)
	if title.endswith("Filme"):
		path = "https://www.kika.de/videos/filme/kinderfilme-100"
		Kika_Start(path=path)
	if title.endswith("Wissen"):
		path = "https://www.kika.de/videos/wissen/wissenssendung-kinder-100"
		Kika_Start(path=path)
	if title.endswith("Shows"):
		path = "https://www.kika.de/videos/shows/kindershows-100"
		Kika_Start(path=path)
	if title.endswith("fassung"):
		path = "https://www.kika.de/audiodeskription/videos-mit-hoerfassung-102"
		Kika_Start(path=path)
	if title.endswith("sprache"):
		path = "https://www.kika.de/gebaerdensprache/videos-mit-gebaerdensprache-102"
		Kika_Start(path=path)
		
	if title.endswith("A-Z"):
		Kika_AZ()
		
	return
	
# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen
#	
def Kika_AZ(title='', path=''):
	PLog('Kika_AZ: ' + path)
		
	# ---------------------------------------							# 1. Durchlauf: Liste Buchstaben
	if path == "":
		PLog("AZ_1:")
		li = xbmcgui.ListItem()
		li = home(li, ID='Kinderprogramme')				# Home-Button
		
		azlist = list(string.ascii_uppercase)
		azlist.append('...')

		# Menü A to Z
		for element in azlist:
			title='Sendungen mit ' + element
			button = element
			if element == "...":
				button = "0-9"
			img = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
			path = "https://www.kika.de/suche/suche104?broadcast=%s" % element
			fparams="&fparams={'title': '%s', 'path': '%s'}" % (button, quote(path))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_AZ", fanart=GIT_AZ, 
				thumb=img, fparams=fparams)

	# ---------------------------------------							# 2. Durchlauf
	else:			
		PLog("AZ_2:")
		page, msg = get_page(path)
		if page == '':
			msg1 = "Fehler in Kika_AZ:"
			msg2 = msg

		page = Kika_get_props(page)										# Web-json ausschneiden
		page = page.replace('\\"', '*')
		
		# Hinw.: firstBroadcastResponse zeigt Inhalte zu A
		pos1 = page.find('"broadcastResponse"')	
		page = page[pos1:]
			
		Kika_Rubriken(page, title='', thumb=GIT_AZ, ID='AZ')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
					
# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen - json-Inhalt ausschneiden,
# 22.03.2023 geeignet für json.loads
def Kika_get_props(page):
	PLog('Kika_get_props:')
	
	m1 = page.find('{"pageProps')
	m2 = page.find(',"__N_SSP"')
	if m1 > 0 and m2 > 0:
		page = page[m1:m2] + '}'
	PLog(page[:60])
	return page
				
# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen - img + img_alt ermitteln
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
# 07.12.2022 Neu nach Webänderungen - einz. Datensatz auswerten 
#	(docType: videoSubchannel, externalVideo, ..)
# s=Blockitem (z.B. docType)
# 
def Kika_get_singleItem(s):
	PLog('Kika_get_singleItem:')

	mehrf='';typ='';path='';stitle='';thumb='';Plot=''
	if '"mainNavigation":' in s:
		typ="skip_mainNavigation"
		return mehrf,typ,path,stitle,thumb,Plot

	date=""; endDate=""; summ=""; mehrf=False; func=""
	typ = stringextract('docType":"', '"', s)
	PLog("docType: " + typ)
	
	s = s.replace('\\"', '*'); s = s.replace(u'\\u0026', u'&')
	ext_id = stringextract('externalId":"', '"', s)					# Bsp. zdf-SCMS_tivi_vcms_video_1914206-default
	if '"api":null' in s:											# z.B. ext. Link zu Junior ESC-Abstimmung
		api_url=""
		typ = "skip_api_null"
		return mehrf,typ,path,stitle,thumb,Plot
	else:
		api_url = stringextract('url":"', '"', s)					# "api":{	
	stitle = stringextract('title":"', '"', s)		
	
	mehrf = True													# default 
	# Einzelvideos: docType":"externalVideo", docType":"video"
	if typ.endswith("ideo"):
		mehrf = False												# Folgeseiten
						
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
	ctitle = stringextract('contentCategoryTitle":"', '"', s)		# Kategorie-Title
	
	if mehrf == False:
		summ = descr
		tag = "Dauer: %s | [B]Bild: [/B] %s | %s" % (dur, cr, img_alt) 
		tag = "%s\n\n%s\n%s" % (tag,  endDate, date)
	else:
		tag = "[B]Bild: [/B] %s | Folgeseiten" % cr
		if ctitle:
			tag = "%s[B] | %s[/B]" % (tag, ctitle)
	summ = descr			

	stitle = unescape(stitle); stitle = repl_json_chars(stitle); 
	tag = unescape(tag); tag = repl_json_chars(tag); 
	summ = unescape(summ); summ = repl_json_chars(summ); 
	if summ:														# kann fehlen
		summ = '[B]Inhalt: [/B] %s' % summ 
	
	Plot = "%s\n\n%s" % (tag, summ)
	Plot = Plot.replace('\n', '||')
		
	path=api_url; thumb=img; Plot=Plot	
	path=py2_encode(path); typ=py2_encode(typ); stitle=py2_encode(stitle); 
	thumb=py2_encode(thumb); Plot=py2_encode(Plot)
	PLog('mehrf: %s, typ: %s, api_url: %s, stitle: %s, thumb: %s, Plot: %s' % (mehrf, typ, path, stitle, thumb, Plot))	
	return mehrf,typ,path,stitle,thumb,Plot			
# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen - Cluster ermitteln in  
#	Folgeseiten (path=api_url -> json), docType: videoSubchannel
# Sonderbehdl. Kikaninchen_Videos: extract api_url in html-Seite,
#	erneut -> Kika_Subchannel
def Kika_Subchannel(path, title, thumb, Plot, li=''):
	PLog('Kika_Subchannel: ' + title)
	title_org=title	
	
	page, msg = get_page(path)
	if page == '':
		msg1 = "Fehler in Kika_Subchannel:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return

	# ------------------------
	if path.endswith("html"):											# von Kikaninchen_Videos, s.o.
		PLog("html_site")
		pos1 = page.find('"videoSubchannel"')
		PLog(pos1)
		if pos1 > 0:
			page = page[pos1:]
		allvideos = stringextract('"url":"',  '"', page)				# wie videosPageUrl in json-Seite
		Kika_Subchannel(allvideos, title, thumb, Plot="")
		return
	# ------------------------		
		
	if li == "":			
		li = xbmcgui.ListItem()
		li = home(li, ID='Kinderprogramme')				# Home-Button
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	
	Plot_par = Plot
	summ_org = Plot.replace("||", "\n")									# Plot hier: tagline + summary
		
	featuredVideo = stringextract('"featuredVideo"',  '"videosPageUrl"', page)
	fanimg=""
	if featuredVideo:													# Empfehlung od. 1. Folge | kann fehlen 
		teaserImage = stringextract('"teaserImage"',  '"structure"', page)
		if teaserImage:
			fanimg, img_alt = Kika_get_img(teaserImage)
			
		mehrf,typ,path,stitle,thumb,Plot = Kika_get_singleItem(featuredVideo)
		summ = Plot.replace("||", "\n")	
		if path == '':													# Sicherung
			PLog("skip_empty_path") 
		else:
			stitle = "[B]Empfehlung: [/B] %s" % stitle					# herausgestelltes Video im Web
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
# 07.12.2022 Neu nach Webänderungen - Folgeseiten ermitteln in  
#	 (path=api_url -> json), docType: broadcastSeries
# Aufrufer: Kika_Rubriken
def Kika_Series(path, title, thumb, Plot):
	PLog('Kika_Series: ' + title)
	title_org=title

	page, msg = get_page(path)
	if page == '':
		msg1 = "Fehler in Kika_Series:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
			
	Subchannel = stringextract('"videoSubchannel":',  '},', page)		# fehlt für Serien-Button
	PLog("videoSubchannel: " + Subchannel)
	if Subchannel.startswith("null") == False:							# broadcastSeries mit/ohne Subchannel		
		api_url = stringextract('url":"', '"', Subchannel)
		Kika_Subchannel(api_url, title, thumb, Plot)					# -> Seitensteuerung Kika_Rubriken
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
	if page.startswith('{"docType":"broadcastSeries'):
		Kika_Rubriken(page, title, thumb, ID='Kika_Series')
		return

# ----------------------------------------------------------------------
# 07.12.2022 Neu nach Webänderungen - einz. Cluster/Channel/Folgen
#	 auswerten
# page: Seite / Ausschnitt 
# einz. Datensätze -> Kika_get_singleItem
# li + page durch Aufrufer möglich
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
	PLog(page[:100])

	items = blockextract('"docType":', page)
	PLog(len(items))
	skip_list=[]; cnt=0
	for s in items:
		mediatype='' 
		# path: api_url, neue typ-Varianten in Kika_get_singleItem
		#	ergänzen: 
		mehrf,typ,path,stitle,thumb,Plot = Kika_get_singleItem(s)		# -> Kika_get_singleItem
		tag = Plot.replace('||', '\n')
		if path in skip_list:											# Doppler vermeiden
			continue
		skip_list.append(path)	
		
		if typ == "" or typ.startswith("skip_"):						#Satz leer, mainNavigation, ..
			PLog(typ) 
			continue
		if typ == "interactiveContent":									# Spiele ausblenden
			PLog(typ)
			continue
		if stitle.endswith("Start") or path.endswith("suche104"):		# Ende Rubrik
			break

		if mehrf:														# Folgeseiten
			if "channel" in typ:
				func = "Kika_Subchannel"
			elif typ == "broadcastSeries" or typ == "link":
				func = "Kika_Series"
			else:
				func = "Kika_Subchannel"
		else:
			func = "Kika_SingleBeitrag"									# einz. Video
			if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Kennz. Video für Sofortstart 
				mediatype='video'
		PLog("func:" + func)	
		if func:		
			stitle=py2_encode(stitle); path=py2_encode(path); 
			thumb=py2_encode(thumb); Plot=py2_encode(Plot)
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
				(quote(path), quote(stitle), quote(thumb), quote(Plot))
			addDir(li=li, label=stitle, action="dirList", dirID="resources.lib.childs.%s" % func, 
				fanart=thumb_org, thumb=thumb, fparams=fparams, tagline=tag, mediatype=mediatype)
			cnt=cnt+1


	# Mehr Seiten anzeigen:
	next_path = stringextract('next":"', '"', page)						# Ende: "next":null
	next_path = next_path.replace(u'\\u0026', u'&')						# in Web-json nötig
	PLog("next_path: " + next_path)
	if next_path:
		next_page=0
		try:
			next_page =  re.search(r'page=(\d+)', next_path).group(1)
			next_page = int(next_page) +1
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
	
	PLog("Mark0")
	PLog(li_org)
	if li_org:
		if cnt == 0:
			msg1 = "leider kein Video:"									# notification (nur ext. Hauptmenü)
			msg2 = title_org
			icon = KIKA_VIDEOS
			xbmcgui.Dialog().notification(msg1,msg2,icon,3000, sound=False)			
		return
	else:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		


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
		sendung = unescape(sendung)
	
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
	if len(items) == 0:
		msg1 = title
		msg2 = "leider keine Sendung gefunden"							
		icon = MAUSZOOM
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=True)			
		return
		
	
	for item in items:
		title = stringextract("<title>", "</title>", item)
		mp3_url = stringextract('<enclosure url="', '"', item)
		mp3_img = stringextract('href="', '"', item)			# itunes:image href="..
		if mp3_img == '':										# kann fehlen
			mp3_img = MAUSZOOM
		dur = stringextract("duration>", "</", item)
		descr = stringextract("summary>", "</", item)
		
		start = stringextract("visibleFrom>", "</", item)
		start = time_translate(start)
		start =  u"Sendedatum: [COLOR blue]%s Uhr[/COLOR]" % start
		end = stringextract("visibleUntil>", "</", item)
		end = time_translate(end)
		end = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % end
		
		author = stringextract("author>", "</itunes:author>", item)
		
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)
		tag = "Dauer: %s | Autor: %s | %s | %s" % (dur, author, start, end)
		
		Plot= "%s||||%s" % (tag, descr)
	
		PLog('Satz11:')		
		PLog(title);PLog(mp3_url);PLog(mp3_img);
		PLog(dur); PLog(tag);PLog(descr[:60]);
		
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
		return
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
		return

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
# Kikaninchen: alle Videos von A-Z
#	A-Z-Liste der Sendereihen (Web: Videos)
# 12.12.2022 Neu nach Webseitenänderungen
# 15.08.2023 allevideos864.html -> api/v1/
#		
def KikaninchenVideosAZ():
	PLog('KikaninchenVideosAZ:')
	
	path = "https://www.kika.de/api/v1/kikaplayer/kikaapp/api/brands/ebb32e6f-511f-450d-9519-5cbf50d4b546/videos"
	path_add = "?limit=400&orderBy=date&orderDirection=DESC"	
	page = Dict("load", "KikaninchenVideos", CacheTime=KikaCacheTime)
	if page == False:
		page, msg = get_page(path + path_add, header=KIKA_HEADERS)
		if page:
			Dict("store", "KikaninchenVideos", page)
	
	if page == '':							
		msg1 = "Fehler in KikaninchenVideosAZ:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return

	try:
		objs = json.loads(page)
		items = objs["_embedded"]["items"]
	except Exception as exception:
		PLog("items_error: " + str(exception))
	PLog("Videos: %s" % len(items))
	if len(items) == 0:
		return

	AZ_lines=[]														# Zeile: Titel|Link
	AZ_chars=[]														# vorkommende Buchst.
	for s in items:
		#PLog(s)
		title= s["title"]
		vid = s["id"]
		AZ_lines.append("%s|%s" % (title, vid))
		fchar = up_low(title[0])
		PLog("fchar: %s, title: %s" % (fchar, title))
		if fchar not in AZ_chars:
			AZ_chars.append(fchar)

	if 	len(AZ_lines) == 0:
		msg1 = "Leider finde ich keine Videos bei Kikaninchen."
		msg2 = "Jemand hat sie wohl versteckt."
		MyDialog(msg1, msg2, '')	
		return
	
	#-----------------------------------------------------------	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
	PLog(AZ_lines[0])	
	AZ_lines.sort(); AZ_chars.sort()
	Dict("store", "KikaninchenAZ", AZ_lines)						# sortierte Titel|Link - Liste speichern
	PLog(len(AZ_lines));
	PLog(str(AZ_chars))
	
	for fchar in AZ_chars:											# A-Z-Liste  für die Sendereihen
		showChar = fchar
		PLog(ord(fchar))
		if ord(fchar) < 65 or ord(fchar) > 90: 	# außerhalb A - Z
			showChar = "0-9"
			
		title = 'Kikaninchen Videos: Seite ' + showChar
		tag = 'Weiter zu den Videos mit [B]%s[/B]' % showChar
		img = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % showChar
		
		fparams="&fparams={'showChar': '%s'}" % showChar
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Videos", fanart=GIT_KANINCHEN, 
			thumb=img, fparams=fparams, tagline=tag)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Kikaninchen - Videos zum Buchstaben showChar zeigen
# 12.12.2022 Neu nach Webseitenänderungen
# 1. Durchlauf: Sendereihen zu showChar
# 2. Durchlauf: Videoliste zu path
# 26.07.2023 zusätzlicher Durchlauf für einige Links erforderlich
#	Ziel Kikaninchen_VideoSingle ersetzt durch  Kikaninchen_Videos
#
def Kikaninchen_Videos(showChar,vid='',title="",assets="",thumb="",Plot="" ):
	PLog('Kikaninchen_Videos: %s | %s' % (showChar, vid))
	base = "https://www.kika.de/api/v1/kikaplayer/kikaapp"
	
	#-------------------------------------------------					# 2. Video-Quellen zu vid
	if vid:
		PLog("Step2:")
		PLog(title)
		page, msg = get_page(assets, header=KIKA_HEADERS)				# json-Quelle kikaplayer abweichend
		assetid = stringextract('"assetid":"', '"', page) 				# -> _next-api/proxy..
		proxy_path = "https://www.kika.de/_next-api/proxy/v1/videos/%s/assets" % assetid
		PLog("proxy_path: " + proxy_path)
		page, msg = get_page(proxy_path, header=KIKA_HEADERS)
		Kika_SingleBeitrag(assets, title, thumb, Plot, page)			# Home-Button dort
		
		return
		
	#-------------------------------------------------
	PLog("Step1:")
	AZ_lines = Dict("load", "KikaninchenAZ")							# Buchstabenliste
	page =  Dict("load", "KikaninchenVideos")							# gesamte Videoliste (Einzelvideos)
	try:
		objs = json.loads(page)
		items = objs["_embedded"]["items"]
	except Exception as exception:
		PLog("items_error: " + str(exception))
		items=[]
	if AZ_lines == False or len(items) == 0:	
		msg1 = "Leider finde ich keine Videos bei Kikaninchen."
		msg2 = "Jemand hat sie wohl versteckt."
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(AZ_lines))	
	PLog("Videos: %s" % len(items))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
	img = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % showChar
	for item in items:
		title = item["title"]
		fchar = up_low(title[0])
		if fchar in showChar:
			vid = item["id"]
			descr = item["description"]
			thumb = item["teaserImageUrl"]
			dur = item["duration"] 
			dur = seconds_translate(str(dur))
			date = item["appearDate"] 
			if date:
				date = time_translate(date, add_hour=0)
				date = "Sendedatum: [B][COLOR blue]%s[/COLOR][/B]" % date
			endDate = item["expirationDate"] 
			if endDate:
				endDate = time_translate(endDate, add_hour=0)
				endDate = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % endDate
			assets = item["_links"]["player-assets"]["href"]
			href = base + assets
			tag = "Dauer: %s" %dur
			if date and endDate:
				tag = "%s\n%s\n%s" % (tag, endDate, date)
			Plot = "%s\n\n%s" % (tag, descr)
			Plot = repl_json_chars(Plot)
			Plot =  Plot.replace("\n", "||")

			PLog(title); PLog(href); 
			href=py2_encode(href); title=py2_encode(title);
			thumb=py2_encode(thumb); Plot=py2_encode(Plot);
			fparams="&fparams={'showChar':'%s','vid':'%s','title':'%s','assets':'%s','thumb':'%s','Plot':'%s'}" %\
				(showChar, vid, quote(title), quote(href), quote(thumb), quote(Plot))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Videos", 
				fanart=img, thumb=thumb, fparams=fparams, tagline=tag, summary=descr)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 13.12.2022 Neu nach Webseitenänderungen
# ausgelagert von Kikaninchen Videos ("Alle Filme")
# 21.03.2023 Quelle geändert ../filme-122.html -> ../filme-122.json
#	(mit html nur noch 1 film erreichbar). href -> xml-Quelle ->
#	 Kikaninchen_VideoSingle
def KikaninchenFilme():	
	PLog("KikaninchenFilme:")
	
	path = 'https://www.kikaninchen.de/filme/filme-122.json'
	page, msg = get_page(path, header=KIKA_HEADERS)			# ohne Dict, kleine Seite
	if page == '':							
		msg1 = "Fehler in KikaninchenFilme:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return

	try:
		objs = json.loads(page)
		films = objs["document"]["teaserBoxes"][0]["teasers"]
	except Exception as exception:
		PLog("L_error: " + str(exception))
		films = []
	PLog("Filme: %s" % len(films))
	if len(films) == 0:
		return

	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
	#thumb = R("Dir-video.png")   				# Fallback
	for film in films:							# Bereiche standard/special
		standard = film["standard"]
		special = film["special"]
		PLog(str(standard)[:80])
		PLog(str(special)[:80])
		
		title = standard["title"]
		title = repl_json_chars(title)
		tline = standard["topline"]
		descr = standard["teaserText"]

		img = standard["teaserImage"]["urlScheme"]
		img = img.replace("**imageVariant**", "original")	# Varianten s. "variants":[
		thumb = img.replace("**width**", "1920")							# s.o.
		img_alt = standard["teaserImage"]["altText"]
		cr = standard["teaserImage"]["rights"]
		bild = "Bild: %s | %s" % (img_alt, cr)
		bild = unescape(bild)

		
		href = special["avCustomUrl"]
		dur = special["duration"]
		
		dauer = "Dauer: " + dur
		tag = "%s\n%s" % (dauer, bild)
		summ = "[B]%s[/B]\n%s" % (tline, descr)
		summ = unescape(summ)
		
		PLog('Satz2:')		
		PLog(title);PLog(href);PLog(img);PLog(bild);
		
		href=py2_encode(href); title=py2_encode(title)
		fparams="&fparams={'path': '', 'title': '%s', 'assets_url': '%s'}" % (quote(title), quote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_VideoSingle", fanart=GIT_KANINCHEN, 
			thumb=thumb, fparams=fparams, tagline=tag, summary=summ)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# 10.12.2022 Neu nach Webseitenänderungen
# Videodetails via Assets-Url ermitteln. path = Videoseite mit embedded
#	Player, für Videodetails 
# Aufrufer: Kikaninchen_Videos
# Aufrufer mit assets_url: KikaninchenLieder
# 21.03.2023 url_m3u8 <adaptiveHttpStreamingRedirectorUrl> ergänzt
#
def Kikaninchen_VideoSingle(path, title, assets_url=''):	
	PLog('Kikaninchen_VideoSingle: ' + path)
	PLog(title)
	title_org=title

	#-------------------------------------------------		# 1. Assets-Url ermittlen -> xml-Datei
	if assets_url == "":
		if "_zc-" in path:									# Format vor 01.06.2023
			try:
				path = path.split("_zc-")[0]					# Bsp.: ../video52242_zc-b799b903_zs-8eedf79c.html
				assets_url = path + "-avCustom.xml"				# Bsp.: ../videos/video52242-avCustom.xml		
			except Exception as exception:
				PLog(str(exception))
				assets_url=""
		else:
			assets_url = path.replace(".html", "-avCustom.xml")		# ab 01.06.2023

	#-------------------------------------------------		# 2. Videodetails aus xml-Datei holen
	page=""
	if assets_url:
		page, msg = get_page(path=assets_url)
	if page == '':	
		msg1 = "Leider finde ich den Weg zum Video nicht."
		msg2 = "Fehler in Kikaninchen_VideoSingle."
		MyDialog(msg1, msg2, '')	
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	title = stringextract("<headline>", "</headline>", page)
	top = stringextract("<topline>", "</topline>", page)
	summ1 = stringextract("<title>", "</title>", page)
	summ2 = stringextract("<teaserText>", "</teaserText>", page)
	dur = stringextract("<duration>", "</duration>", page)
	
	img_src = stringextract("<teaserimage>", "</teaserimage>", page)
	img = stringextract("<url>", "</url>", img_src)
	variant = stringextract("<large>", "</large>", img_src)
	if variant == "":
		variant = stringextract("<small>", "</small>", img_src)
	img = img.replace("**aspectRatio**", variant)
	img = img.replace("**width**", "1024")
	
	tag = "Dauer: %s | %s" % (dur, top)
	summ = "%s\n%s" % (summ1, summ2)
	Plot = "%s\n\n%s" % (tag, summ)
	assets = blockextract('<asset>', page)
	
	title = valid_title_chars(title)
	summ = valid_title_chars(summ)
	
	PLog("Satz1:")
	PLog(len(assets)); PLog(title); PLog(summ); PLog(img); 
	
	#-------------------------------------------------		# 3. Bau HLS_List + Stream_List, ähnl. Kika_SingleBeitrag
	# Formate siehe StreamsShow								# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	asset=""
	for asset in assets:
		if "Web XL|" in asset:								# größte HLS-Quelle verwenden, Altern.: "MP4 Web L"
			break
		
	url_m3u8 = stringextract('<csmilHlsStreamingRedirectorUrl>', '</', asset)
	if url_m3u8 == "":
		url_m3u8 = stringextract('<adaptiveHttpStreamingRedirectorUrl>', '</', asset)
	PLog("url_m3u8: " + url_m3u8)
	# sub_path = stringextract('"webvttUrl":"', '"', page)	# Altern.: subtitle-Url tt:style, fehlen hier
	sub_path=""; geoblock=''; descr='';	
	href = url_m3u8
	HBBTV_List=''											# nur ZDF
	HLS_List=[]; Stream_List=[];
	
	#'''
	quality = u'automatisch'
	HLS_List.append('HLS automatische Anpassung ** auto ** auto ** %s#%s' % (title,url_m3u8))
	Stream_List = ardundzdf.Parseplaylist(li, href, img, geoblock, descr, stitle=title, buttons=False)
	if type(Stream_List) == list:					# Fehler Parseplaylist = string
		HLS_List = HLS_List + Stream_List
	else:
		HLS_List=[]
	#'''
		
	PLog("HLS_List: inputstream.adaptive returned bad status Permanent failure..")
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = Kika_VideoMP4getXML(title, assets)
	PLog("download_list: " + str(MP4_List)[:80])
	Dict("store", 'KIKA_HLS_List', HLS_List) 
	Dict("store", 'KIKA_MP4_List', MP4_List) 
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "Leider finde ich keine Videodaten."
		msg2 = "Fehler in Kikaninchen_VideoSingle."
		MyDialog(msg1, msg2, '')	
		return li

	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	thumb = img; ID = 'KIKA'; HOME_ID = "Kinderprogramme"
	PLog('childs_Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
	Plot = "Titel: %s\n\n%s" % (title_org, summ)				# -> build_Streamlists_buttons
	Plot = Plot.replace("\n", "||")
	PLog('Plot: ' + Plot)
	ardundzdf.build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Verbleib in Liste	
		return	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------			
# 18.06.2017: KikaninchenLieder ersetzt die Kikaninchen Kramkiste (xml-Seite mit mp3-Audioschnipsel, abgeschaltet)
# 18.06.2017: KikaninchenLieder ersetzt die Kikaninchen Kramkiste (xml-Seite mit mp3-Audioschnipsel, abgeschaltet)
# 	Unterseite 'Singen + Tanzen' von http://www.kikaninchen.de/index.html?page=0
# 13.12.2022 avCustomUrl als assets_url -> Kikaninchen_VideoSingle (früher Kika_SingleBeitrag)
def KikaninchenLieder():	
	PLog('KikaninchenLieder:')
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
		href=py2_encode(href); title=py2_encode(title)
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_VideoSingle", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=summ, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# Tonschnipsel aus verschiedenen Seiten
def Tonschnipsel():	
	PLog('Tonschnipsel:')
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
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", 
			fanart=thumb, thumb=thumb, fparams=fparams, summary=title, mediatype='music')
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ######################################################################
# einzelnes Video
# 07.12.2022 Neu nach Webänderungen (vormals xml-Seite)			
# path enthält die api-Seite mit Details (json). Hier direkt
#	weiter mit der assets-Url zu den Videoquellen (einfaches Anhängen
#	von /assets klappt nicht bei typ=relatedVideo
# Aufrufer: Kika_Subchannel, Kika_Rubriken
# 16.08.2023 Kikaninchen_Videos lädt Quellen bereits vor (page)
#
def Kika_SingleBeitrag(path, title, thumb, Plot, page=""):
	PLog('Kika_SingleBeitrag: ' + path)
	title_org = title
		
	if page == "":
		page, msg = get_page(path)					# Details mit asset_url
		pos = page.find('"assets":{')
		page = page[pos:]
		PLog("pos: %d" % pos)
		asset_url = stringextract('"url":"', '"', page)
		PLog("asset_url: " + asset_url)
		page, msg = get_page(path=asset_url)		# Videoquellen
		PLog(msg)
		
	if page == '':								# bei Spielen können Videos fehlen
		msg1 = "Kika_SingleBeitrag:"
		msg2 = "leider finde ich dazu kein Video."
		msg3 = "Spiele oder Abstimmungen kann ich leider auch nicht."
		MyDialog(msg1, msg2, msg3)	
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

	PLog("Mark0")
	PLog(page)
	PLog(url_m3u8); PLog(sub_path)
	
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
# 07.12.2022 angepasst nach Webänderungen
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
			
		PLog("res: %s" % res); 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4 Qualität: %s ** Auflösung %s ** %s" % (quality, res, title_url)
		download_list.append(item)

	return download_list
			
# ------------------------------
# 13.12.2022 Neu nach Webänderungen
def Kika_VideoMP4getXML(title, assets):	
	PLog('Kika_VideoMP4getXML:')
	
	href=''; quality=''
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	for s in assets:
		PLog(s[:100])		
		frameWidth = stringextract('<frameWidth>', '</frameWidth>', s)	
		frameHeight = stringextract('<frameHeight>', '</frameHeight>', s)
		href = stringextract('<progressiveDownloadUrl>', '</', s)
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
			
		PLog("res: %s, href: %s" % (res, href)); 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4 Qualität: %s ** Auflösung %s ** %s" % (quality, res, title_url)
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
			img_alt = stringextract('title="', '"', img)
			title = img_alt
			pos = title.find("|")
			if pos > 0:							# cut Copyright
				title = title[:pos-1]
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
# Aufrufer: ZDF_VerpasstWoche (teilw. adaptiert)
# Nutzung ZDF_get_content
# Kennung ZDFtivi in key infoline, nicht in channel wie z.B. ZDFinfo -
#	Auswertung in ZDF_Verpasst zu aufwändig
# Wegen der geringen Anzahl hier ohne Unterteilung in Tageszeiten
#
def tivi_Verpasst(title, zdfDate, sfilter=""):
	PLog('tivi_Verpasst:'); PLog(title); PLog(zdfDate);
	
	path = "https://zdf-prod-futura.zdf.de/mediathekV2/broadcast-missed/" + zdfDate
	page = Dict("load", "ZDFtivi_%s" % zdfDate, CacheTime=KikaCacheTime)# 1 Std.
	if page == False:
		page, msg = get_page(path)
		if page:
			Dict("store", "ZDFtivi_%s" % zdfDate, page)	

	if page == '':
		msg1 = "Fehler in tivi_Verpasst | %s" % title
		MyDialog(msg1, msg, '')
		return
	
	mediatype=''														# Kennz. Videos im Listing
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	PLog('mediatype: ' + mediatype); 

	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	li2 = xbmcgui.ListItem()											# mediatype='video': eigene Kontextmenüs in addDir							
	
	jsonObject = json.loads(page)
	clusterObject = jsonObject["broadcastCluster"]						# Morgens, Mittags, Abends, Nachts
	PLog(str(clusterObject)[:80])
	for cluster in clusterObject:
		teaser = cluster["teaser"]
		PLog(len(teaser))
		PLog(str(teaser)[:80])
		for entry in teaser:
			try:
				infoline = str(entry["infoline"])
				if not "ZDFtivi" in infoline:							# hier nur ZDFtivi-Inhalte
					continue

				PLog("infoline: " + infoline[:60])
				typ,title,tag,descr,img,url,stream,scms_id = ardundzdf.ZDF_get_content(entry)
				airtime = entry["airtime"]
				t = airtime[-5:]
				title = "[COLOR blue]%s[/COLOR] | %s" % (t, title)			# Sendezeit | Titel
				channel = entry["channel"]
				tag = "%s | Sender: [B]%s[/B]" % (tag, "ZDFtivi") 
					
				PLog("Satz3:")
				PLog(tag); PLog(title); PLog(stream);
				title = repl_json_chars(title)
				descr = repl_json_chars(descr)
				tag = repl_json_chars(tag)
				fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','tag': '%s','summ': '%s','scms_id': '%s'}" %\
					(stream, title, img, tag, descr, scms_id)	
				addDir(li=li2, label=title, action="dirList", dirID="ZDF_getApiStreams", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, summary=descr, mediatype=mediatype)
			except Exception as exception:
				PLog("verpasst_error: " + str(exception))
							
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

# ----------------------------------------------------------------------
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 			
def Tivi_AZ():
	PLog('Tivi_AZ:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	azlist = list(string.ascii_uppercase)
	azlist.append('0 - 9')						# ZDF-Vorgabe (vormals '0+-+9')

	for element in azlist:	
		button = element
		if button == "0 - 9":
			button = "0-9"						# Anpas. img-Name
		title = "Sendungen mit " + element
		img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
		
		PLog(button); PLog(img_src)
		button=py2_encode(button); title=py2_encode(title);		
		fparams="&fparams={'name': '%s', 'element': '%s'}" % (quote(title), button)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ_Sendungen", fanart=R(ICON_DIR_FOLDER), 
			thumb=img_src, fparams=fparams, tagline=title)
 
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# Alle Sendungen, char steuert Auswahl 0-9, A-Z
# 12.12.2019 Nutzung ZDF_get_content statt get_tivi_details
# 26.04.2023 Umstellung www.zdf.de -> zdf-cdn
#
def Tivi_AZ_Sendungen(name, element=None):	
	PLog('Tivi_AZ_Sendungen:'); PLog(element)
		
	jsonObject = Dict("load", "ZDF_tiviAZ", CacheTime=KikaCacheTime)	# 1 Std., ca. 3 MByte
	if not jsonObject:
		icon = GIT_AZ
		xbmcgui.Dialog().notification("Cache tivi A-Z:","Haltedauer 60 Min",icon,3000)
		path = "https://zdf-prod-futura.zdf.de/mediathekV2/document/kindersendungen-a-z-100"
		page, msg = get_page(path)
		if not page:												# nicht vorhanden?
			msg1 = 'Tivi_AZ_Sendungen: Beiträge können leider nicht geladen werden.' 
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
		jsonObject = json.loads(page)
		Dict("store", "ZDF_tiviAZ", jsonObject)		
		
	li = xbmcgui.ListItem()
	homeID = 'Kinderprogramme'
	li = home(li, ID=homeID)			# Home-Button
		
	jsonObject = jsonObject["cluster"]
	PLog(len(jsonObject))
	PLog(str(jsonObject)[:80])
	AZObject=[]	
	for clusterObject in jsonObject:
		PLog(str(clusterObject)[:12])
		if element in clusterObject["name"]:
			title = clusterObject["name"]
			PLog("found_title: " + title)
			AZObject = clusterObject
			break
	
	if AZObject:
		teaserObject = AZObject["teaser"]
		for entry in teaserObject:
			typ,title,tag,descr,img,url,stream,scms_id = ardundzdf.ZDF_get_content(entry)
			title = repl_json_chars(title)
			label = title
			descr = repl_json_chars(descr)
			fparams="&fparams={'url': '%s', 'title': '%s', 'homeID': '%s'}" % (url, title, homeID)
			PLog("fparams: " + fparams)	
			addDir(li=li, label=label, action="dirList", dirID="ardundzdf.ZDF_RubrikSingle", fanart=img, 
				thumb=img, fparams=fparams, summary=descr, tagline=tag)	
	else:
		msg1 = name
		msg2 = "leider nichts gefunden"
		icon = GIT_AZ
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000, sound=True)
		return					

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			












