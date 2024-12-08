# -*- coding: utf-8 -*-

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
	try:									
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

# Kodi-API-Änderungen:
#	18.08.2021 xbmc.translatePath -> xbmc.translatePath (nur PYTHON3)
#		https://github.com/xbmc/xbmc/pull/18345
#		https://forum.kodi.tv/showthread.php?tid=344263&pid=2975581#pid2975581
#	13.09.2020 	LOG_MSG = xbmc.LOGNOTICE (nur PYTHON2) 	Modul util
#				LOG_MSG = xbmc.LOGINFO (nur PYTHON3) 	Modul util
#		https://forum.kodi.tv/showthread.php?tid=344263&pid=2943703#pid2943703


# Python
import base64 			# url-Kodierung für Kontextmenüs
import sys				# Plattformerkennung
import shutil			# Dateioperationen
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import datetime, time
from datetime import timedelta
import json				# json -> Textstrings
import string
import importlib		# dyn. Laden zur Laufzeit, s. router


# ständige Addonmodule - Rest dyn. in router
import resources.lib.updater as updater	
from resources.lib.util import *
import resources.lib.EPG as EPG
import resources.lib.epgRecord as epgRecord
	
																		
# +++++ ARDundZDF - Addon Kodi-Version, migriert von der Plexmediaserver-Version +++++

# VERSION -> addon.xml aktualisieren
# 	<nr>224</nr>										# Numerierung für Einzelupdate
VERSION = '5.1.5'
VDATE = '08.12.2024'


# (c) 2019 by Roland Scholz, rols1@gmx.de
# 
#     Functions -> README.md
# 
# 	Licensed under MIT License (MIT)
# 	(previously licensed under GPL 3.0)
# 	A copy of the License you find here:
#		https://github.com/rols1/Kodi-Addon-ARDundZDF/blob/master/LICENSE.txt

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.


####################################################################################################
NAME			= 'ARD und ZDF'
PREFIX 			= '/video/ardundzdf'		#	
												
PLAYLIST 		= 'livesenderTV.xml'		# TV-Sender-Logos erstellt von: Arauco (Plex-Forum). 											
FANART					= 'fanart.png'		# ARD + ZDF - breit
ART 					= 'art.png'			# ARD + ZDF
ICON 					= 'icon.png'		# ARD + ZDF
ICON_SEARCH 			= 'ard-suche.png'
ICON_ZDF_SEARCH 		= 'zdf-suche.png'				
ICON_FILTER				= 'icon-filter.png'	

ICON_MAIN_ARD 			= 'ard-mediathek.png'
ICON_MAIN_ZDF 			= 'zdf-mediathek.png'
ICON_MAIN_TVLIVE 		= 'tv-livestreams.png'
ICON_MAIN_RADIOLIVE 	= 'radio-livestreams.png'
ICON_MAIN_UPDATER 		= 'plugin-update.png'
ICON_UPDATER_NEW 		= 'plugin-update-new.png'

ICON_ARD_AZ 			= 'ard-sendungen-az.png'
ICON_ARD_VERP 			= 'ard-sendung-verpasst.png'
ICON_ARD_RUBRIKEN 		= 'ard-rubriken.png'
ICON_ARD_BARRIEREARM 	= 'ard-barrierearm.png'
ICON_ARD_HOERFASSUNGEN	= 'ard-hoerfassungen.png'
ICON_ARD_BILDERSERIEN 	= 'ard-bilderserien.png'

ICON_ZDF_AZ 			= 'zdf-sendungen-az.png'
ICON_ZDF_VERP 			= 'zdf-sendung-verpasst.png'
ICON_ZDF_RUBRIKEN 		= 'zdf-rubriken.png'
ICON_ZDF_BARRIEREARM 	= 'zdf-barrierearm.png'
ICON_ZDF_BILDERSERIEN 	= 'zdf-bilderserien.png'

ICON_MAIN_POD			= 'radio-podcasts.png'			# childs: Tonschnipsel
ICON_MAIN_AUDIO			= 'ard-audiothek.png'
ICON_AUDIO_LIVE			= 'ard-audio-live.png'
ICON_AUDIO_AZ			= 'ard-audio-az.png'

ICON_OK 				= "icon-ok.png"
ICON_INFO 				= "icon-info.png"
ICON_WARNING 			= "icon-warning.png"
ICON_NEXT 				= "icon-next.png"
ICON_CANCEL 			= "icon-error.png"
ICON_MEHR 				= "icon-mehr.png"
ICON_DOWNL 				= "icon-downl.png"
ICON_DOWNL_DIR			= "icon-downl-dir.png"
ICON_DELETE 			= "icon-delete.png"
ICON_STAR 				= "icon-star.png"
ICON_NOTE 				= "icon-note.png"
ICON_SPEAKER 			= "icon-speaker.png"
ICON_TOOLS 				= "icon-tools.png"
ICON_PREFS 				= "icon-preferences.png"

# Basis DIR-Icons: Tango/folder.png s. Wikipedia Tango_Desktop_Project
ICON_DIR_CURLWGET 		= "Dir-curl-wget.png"
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_DIR_PRG 			= "Dir-prg.png"
ICON_DIR_IMG 			= "Dir-img.png"
ICON_DIR_TXT 			= "Dir-text.png"
ICON_DIR_MOVE 			= "Dir-move.png"
ICON_DIR_MOVE_SINGLE	= "Dir-move-single.png"
ICON_DIR_MOVE_ALL 		= "Dir-move-all.png"
ICON_DIR_BACK	 		= "Dir-back.png"
ICON_DIR_SAVE 			= "Dir-save.png"
ICON_DIR_STRM			= "Dir-strm.png"

ICON_DIR_VIDEO 			= "Dir-video.png"
ICON_DIR_WORK 			= "Dir-work.png"
ICON_MOVEDIR_DIR 		= "Dir-moveDir.png"
ICON_DIR_FAVORITS		= "Dir-favorits.png"

ICON_DIR_WATCH			= "Dir-watch.png"
ICON_PHOENIX			= 'phoenix.png'			

# Github-Icons zum Nachladen aus Platzgründen
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'
GIT_CAL			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-calendar.png?raw=true"
GIT_TIVIHOME	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-home.png?raw=true"
GIT_ZDFTIVI		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-zdftivi.png?raw=true"
GIT_TIVICAL		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-cal.png?raw=true"


# 01.12.2018 	Änderung der BASE_URL von www.ardmediathek.de zu classic.ardmediathek.de
# 06.12.2018 	Änderung der BETA_BASE_URL von  beta.ardmediathek.de zu www.ardmediathek.de
# 03.06.2021	Classic-Version im Web entfallen, Code bereinigt
ARD_BASE_URL	= 'https://www.ardmediathek.de'								# vorher beta.ardmediathek.de
ARD_VERPASST 	= '/tv/sendungVerpasst?tag='								# ergänzt mit 0, 1, 2 usw.
# ARD_AZ 			= 'https://www.ardmediathek.de/ard/shows'				# ARDneu, komplett (#, A-Z)
ARD_AZ 			= '/tv/sendungen-a-z?buchstabe='							# ARD-Classic ergänzt mit 0-9, A, B, usw.
ARD_Suche 		= '/tv/suche?searchText=%s&words=and&source=tv&sort=date'	# Vorgabe UND-Verknüpfung
ARD_Live 		= '/tv/live'


# ARD-Podcasts - 03.06.2021 alle Links der Classic-https://api.ardaudiothek.de/Version entfernt

# ARD Audiothek
ARD_AUDIO_BASE = 'https://api.ardaudiothek.de/'
HEADERS="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
	'Referer': '%s', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}"

# Relaunch der Mediathek beim ZDF ab 28.10.2016: xml-Service abgeschaltet
ZDF_BASE				= 'https://www.zdf.de'
ZDF_CacheTime_Start = 300			# 5 Min.
ZDF_CacheTime_AZ 	= 1800			# 30 Min.
# Aktualisierung via window.zdfsite www.zdf.de
zdfToken = "5bb200097db507149612d7d983131d06c79706d5"	# 21.07.2024


REPO_NAME		 	= 'Kodi-Addon-ARDundZDF'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME

PLog('Addon: lade Code')
PluginAbsPath = os.path.dirname(os.path.abspath(__file__))				# abs. Pfad für Dateioperationen
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]
HANDLE			= int(sys.argv[1])

ICON = R(ICON)
PLog("ICON: " + ICON)
TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):				# ADDON_DATA-Verzeichnis anpasen
	PLog('python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLog("ADDON_DATA: " + ADDON_DATA)


THUMBNAILS 		= os.path.join(USERDATA, "Thumbnails")
M3U8STORE 		= os.path.join(ADDON_DATA, "m3u8") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides")
PODIMGSTORE		= os.path.join(SLIDESTORE, "PodcastImg")
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
JOBFILE			= os.path.join(ADDON_DATA, "jobliste.xml") 		# Jobliste für epgRecord
MONITOR_ALIVE 	= os.path.join(ADDON_DATA, "monitor_alive") 	# Lebendsignal für JobMonitor
DL_CHECK 		= os.path.join(ADDON_DATA, "dl_check_alive") 	# Anzeige Downloads (Lockdatei)
DL_CNT 			= os.path.join(ADDON_DATA, "dl_cnt") 			# Anzeige Downloads (Zähler)
STRM_SYNCLIST	= os.path.join(ADDON_DATA, "strmsynclist")		# strm-Liste für Synchronisierung	
STRM_CHECK 		= os.path.join(ADDON_DATA, "strm_check_alive") 	# strm-Synchronisierung (Lockdatei)
FLAG_OnlyUrl	= os.path.join(ADDON_DATA, "onlyurl")			# Flag PlayVideo_Direct	-> strm-Modul
PLog(SLIDESTORE); PLog(WATCHFILE); 
check 			= check_DataStores()							# Check /Initialisierung / Migration 
PLog('check: ' + str(check))


now = time.time()											# Abgleich Flags
# die tvtoday-Seiten decken 12 Tage ab, trotzdem EPG-Lauf alle 12 Stunden
#	 	(dto. Cachezeit für einz. EPG-Seite in EPG.EPG).
#		26.11.2023 Intervall optional statt 12 Std. - s.a. EPG-Modul
# 26.10.2020 Update der Datei livesenderTV.xml hinzugefügt - s. thread_getepg
if SETTINGS.getSetting('pref_epgpreload') == 'true':		# EPG im Hintergrund laden?
	eci = SETTINGS.getSetting('pref_epg_intervall')
	eci = re.search(r'(\d+) ', eci).group(1)  				# "12 Std.|1 Tag|5 Tage|10 Tage"
	eci = int(eci)
	PLog("epg_check: eci %d" % eci)	
	if eci == 12:											# 12 Std.
		EPGCacheTime = 43200
	else:
		EPGCacheTime = eci * 86400 							# 1-10 Tage
		
	EPGACTIVE = os.path.join(DICTSTORE, 'EPGActive') 		# Marker thread_getepg aktiv
	is_activ=False
	if os.path.exists(EPGACTIVE):							# gesetzt in thread_getepg 
		is_activ=True
		mtime = os.stat(EPGACTIVE).st_mtime
		diff = int(now) - mtime
		PLog("epg_active: %d diff, %d EPGCacheTime" % (diff, EPGCacheTime))			
		if diff > EPGCacheTime:								# Flag entf. wenn älter als Option	
			os.remove(EPGACTIVE)
			is_activ=False
	if is_activ == False:									# EPG-Daten veraltet, neu holen
		from threading import Thread
		bg_thread = Thread(target=EPG.thread_getepg, args=(EPGACTIVE, DICTSTORE, PLAYLIST))
		bg_thread.start()				

tci = int(SETTINGS.getSetting('pref_tv_store_days'))		# TV-Livestream-Quellen aktualisieren
if tci >= 5:												# Thread nicht bei 0 od. 1 aktivieren
	ID = "ard_streamlinks"									# stellvertretend auch für zdf + iptv
	dictfile = os.path.join(DICTSTORE, ID)
	if os.path.exists(dictfile):
		mtime = os.path.getmtime(dictfile)
		now	= int(time.time())	
		CacheLimit = tci * 86400
		cache_diff = CacheLimit - int(now - mtime)				# Sec-Abstand zum nächsten Ablaufdatum
		
		PLog("streamcache_check: tci %d" % tci)	
		PLog("cache_diff: %d sec, %d days" % (cache_diff, int(cache_diff/86400)))
		
		if cache_diff <= 43200:									# Refresh bereits 12 Std. vor Ablauf möglich
			PLog("CacheLimit_reached: %d" % int(now-CacheLimit))			
			bg_thread = Thread(target=EPG.thread_getstreamlinks, args=())
			bg_thread.start()				
								
if SETTINGS.getSetting('pref_dl_cnt') == 'true':			# laufende Downloads anzeigen
	if os.path.exists(DL_CHECK) == False:					# Lock beachten (Datei dl_check_alive)						
		PLog("Haupt_PRG: get_active_dls")
		from threading import Thread
		bg_thread = Thread(target=epgRecord.get_active_dls, args=())
		bg_thread.start()
	else:													# Check Dateileiche
		mtime = os.stat(DL_CHECK).st_mtime
		diff = int(now) - mtime
		if diff > 43200:                        			# nach 12 Std. entfernen
				PLog("remove_dead_file: " + DL_CHECK)
				os.remove(DL_CHECK)
				if os.path.exists(DL_CNT):					# einschl. alten Zähler
						os.remove(DL_CNT)		
else:
		if os.path.exists(DL_CHECK):	
			os.remove(DL_CHECK)								# Setting Aus: Lock dl_check_alive entfernen
		if os.path.exists(DL_CNT):
			os.remove(DL_CNT)								# Zähler dl_cnt entfernen

if os.path.exists(FLAG_OnlyUrl):							# Lockdatei für Synchronisierung strm-Liste				
	mtime = os.stat(FLAG_OnlyUrl).st_mtime
	diff = int(now) - mtime
	if diff > 60:											# entf. wenn älter als 60 sec	
		os.remove(FLAG_OnlyUrl)
		PLog("onlyurl_removed, age: %d sec" % diff)
	
if os.path.exists(STRM_SYNCLIST):							# strm-Liste für Synchronisierung					
	if os.path.exists(STRM_CHECK):							# Leiche? 2-sec-Aktualisierung durch strm_sync
		mtime = os.stat(STRM_CHECK).st_mtime
		diff = int(now) - mtime
		if diff > 10:										# entf. wenn älter als 10 sec	
			os.remove(STRM_CHECK)
			PLog("strm_check_alive_removed, age: %d sec" % diff)
		else:
			PLog("Haupt_PRG: strm_sync_is_running")

	if os.path.exists(STRM_CHECK) == False:					# Lock beachten (Datei strm_check_alive)
		open(STRM_CHECK, 'w').close()						# Lock strm_check_alive anlegen
		PLog("Haupt_PRG: start_strm_sync")
		import resources.lib.strm as strm
		from threading import Thread
		bg_thread = Thread(target=strm.strm_sync, args=())
		bg_thread.start()	
else:
		if os.path.exists(STRM_CHECK):
			PLog("Haupt_PRG: clear_strm_check_alive")	
			os.remove(STRM_CHECK)							# Liste fehlt: Lock strm_check_alive entfernen
		

MERKACTIVE 	= os.path.join(DICTSTORE, 'MerkActive') 		# Marker aktive Merkliste
if os.path.exists(MERKACTIVE):
	os.remove(MERKACTIVE)
MERKFILTER 	= os.path.join(DICTSTORE, 'Merkfilter') 
# Ort FILTER_SET wie filterfile (check_DataStores):
FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
AKT_FILTER	= ''
if os.path.exists(FILTER_SET):	
	AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()						# gesetzte Filter initialiseren 
STARTLIST	= os.path.join(ADDON_DATA, "startlist") 		# Videoliste ("Zuletzt gesehen")

try:	# 28.11.2019 exceptions.IOError möglich, Bsp. iOS ARM (Thumb) 32-bit
	from platform import system, architecture, machine, release, version	# Debug
	OS_SYSTEM = system()
	OS_ARCH_BIT = architecture()[0]
	OS_ARCH_LINK = architecture()[1]
	OS_MACHINE = machine()
	OS_RELEASE = release()
	OS_VERSION = version()
	OS_DETECT = OS_SYSTEM + '-' + OS_ARCH_BIT + '-' + OS_ARCH_LINK
	OS_DETECT += ' | host: [%s][%s][%s]' %(OS_MACHINE, OS_RELEASE, OS_VERSION)
except:
	OS_DETECT =''
	
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

PLog('Addon: ClearUp')
# Dict: Simpler Ersatz für Dict-Modul aus Plex-Framework
ARDStartCacheTime = 300						# 5 Min.	
 
days = int(SETTINGS.getSetting('pref_DICT_store_days'))
Dict('ClearUp', days)				# Dict bereinigen 
ClearUp(M3U8STORE, days*86400)		# M3U8STORE bereinigen	
days = int(SETTINGS.getSetting('pref_UT_store_days'))
ClearUp(SUBTITLESTORE, days*86400)	# SUBTITLESTORE bereinigen	

days = int(SETTINGS.getSetting('pref_SLIDES_store_days'))
ClearUp(SLIDESTORE, days*86400)		# SLIDEESTORE bereinigen
ARDNeu_Startpage = os.path.join(SLIDESTORE, "ARDNeu_Startpage")
ClearUp(ARDNeu_Startpage, days*86400)# Thumbscache ARDneu bereinigen
ClearUp(PODIMGSTORE, days*86400)	# PodcastImg-Cache bereinigen


days = int(SETTINGS.getSetting('pref_TEXTE_store_days'))
ClearUp(TEXTSTORE, days*86400)		# TEXTSTORE bereinigen

if SETTINGS.getSetting('pref_epgRecord') == 'true':
	epgRecord.JobMain(action='init')						# EPG_Record starten

# Skin-Anpassung:
skindir = xbmc.getSkinDir()
PLog("skindir: %s" % skindir)
sel = SETTINGS.getSetting('pref_content_type')				# 31.03.2023 erweitert: pull request #12 from Trekky12
try:
	sel = re.search(r'\((.*?)\)', sel).group(1)				# Default: "" -> except 
except:
	sel=""
PLog("content_type: %s" % sel)				
xbmcplugin.setContent(HANDLE, sel)

ARDSender = 'ARD-Alle:ard::ard-mediathek.png:ARD-Alle'		# Rest in ARD_NEW, CurSenderZDF s. ZDF_VerpasstWoche
CurSender = ARDSender										# Default ARD-Alle
fname = os.path.join(DICTSTORE, 'CurSender')				# init CurSender (aktueller Sender)
if os.path.exists(fname):									# kann fehlen (Aufruf Merkliste)
	CurSender = Dict('load', "CurSender")					# Übergabe -> Main_NEW (ARDnew)
else:
	Dict('store', "CurSender", CurSender)
PLog(fname); PLog(CurSender)

#----------------------------------------------------------------  
																	
def Main():
	PLog('Main:'); 
	PLog('Addon-Version: ' + VERSION); PLog('Addon-Datum: ' + VDATE)	
	PLog(OS_DETECT)	
	PLog('Addon-Python-Version: %s'  % sys.version)
	PLog('Kodi-Version: %s'  % KODI_VERSION)
			
	PLog(PluginAbsPath)	

	icon = R(ICON_MAIN_ARD)
	label 		= NAME
	li = xbmcgui.ListItem("ARD und ZDF")
	
	
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'Gesucht wird in [B]allen von MediathekView unterstützen Sendern[/B].'
		summ = "%s\n\nBilder sind in den Ergebnislisten nicht enthalten. " % summ
		title=py2_encode(title);
		func = "ardundzdf.Main"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARD|ZDF", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R('suche_ardundzdf.png'), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
	
	title="Suche in ARD und ZDF"
	tagline = 'gesucht wird in [B]ARD  Mediathek, ZDF Mediathek[/B] und [B]Merkliste[/B].'
	summ = u"Tools für die Suchwortliste: Menü [B]Suchwörter bearbeiten[/B] (siehe Infos + Tools)."
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
		fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tagline, 
		summary=summ, fparams=fparams)

	title = "ARD Mediathek"
	tagline = u'einschließlich Teletext und sportschau.de (WDR) '
	CurSender = Dict('load', "CurSender")
	if ":" in str(CurSender):
		tagline = "%s\n\nSender: [B]%s[/B]" % (tagline, CurSender.split(":")[0])
	fparams="&fparams={'name': '%s'}" % (title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", fanart=R(FANART), 
		thumb=R(ICON_MAIN_ARD), tagline=tagline, fparams=fparams)
			
	tagline = u"einschließlich Teletext und ZDF-funk"
	summ = "funk-Podcasts befinden sich in der Audiothek"
	fparams="&fparams={'name': 'ZDF Mediathek'}"
	addDir(li=li, label="ZDF Mediathek", action="dirList", dirID="Main_ZDF", fanart=R(FANART), 
		thumb=R(ICON_MAIN_ZDF), tagline=tagline, summary=summ, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_3sat') == 'true':
		tagline = 'in den Settings kann das Modul 3Sat ein- und ausgeschaltet werden'
		fparams="&fparams={'name': '3Sat'}"									# 3Sat-Modul
		addDir(li=li, label="3Sat Mediathek", action="dirList", dirID="resources.lib.my3Sat.Main_3Sat", 
			fanart=R('3sat.png'), thumb=R('3sat.png'), tagline=tagline, fparams=fparams)
	
	if SETTINGS.getSetting('pref_use_childprg') == 'true':
		tagline = 'in den Settings kann das Modul Kinderprogramme ein- und ausgeschaltet werden'
		summ = u"KiKA, ZDFtivi, MausLive u.a."
		fparams="&fparams={}"													# Kinder-Modul
		addDir(li=li, label="Kinderprogramme", action="dirList", dirID="resources.lib.childs.Main_childs", 
			fanart=R('childs.png'), thumb=R('childs.png'), tagline=tagline, summary=summ, fparams=fparams)

	#	26.04.2023 erneuert		
	if SETTINGS.getSetting('pref_use_XL') == 'true':
		tagline = 'in den Settings kann das Modul TagesschauXL ein- und ausgeschaltet werden'
		fparams="&fparams={}"													# TagesschauXL-Modul
		addDir(li=li, label="TagesschauXL", action="dirList", dirID="resources.lib.TagesschauXL.Main_XL", 
			fanart=ICON_MAINXL, thumb=ICON_MAINXL, tagline=tagline, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_phoenix') == 'true':
		tagline = 'in den Settings kann das Modul phoenix ein- und ausgeschaltet werden'
		fparams="&fparams={}"													# Phoenix-Modul
		addDir(li=li, label="phoenix", action="dirList", dirID="resources.lib.phoenix.Main_phoenix", 
			fanart=R(ICON_PHOENIX), thumb=R(ICON_PHOENIX), tagline=tagline, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_arte') == 'true':
		tagline = 'in den Settings kann das Modul Arte-Mediathek ein- und ausgeschaltet werden'
		fparams="&fparams={}"													# arte-Modul
		addDir(li=li, label="Arte-Mediathek", action="dirList", dirID="resources.lib.arte.Main_arte", 
			fanart=R('arte_Mediathek.png'), thumb=R('arte_Mediathek.png'), tagline=tagline,
			fparams=fparams)
			
	label = 'TV-Livestreams'
	if SETTINGS.getSetting('pref_epgRecord') == 'true':		
		label = u'TV-Livestreams | Sendungen aufnehmen'; 
	tagline = u'Livestreams von ARD, ZDF und einigen Privaten. Zusätzlich Event Streams von ARD und ZDF.'
	summ = u"Die Haltezeit im Cache für die Livestreamquellen kann zwischen 0 bis 60 Tage eingestellt werden."																																	
	fparams="&fparams={'title': 'TV-Livestreams'}"
	addDir(li=li, label=label, action="dirList", dirID="SenderLiveListePre", 
		fanart=R(FANART), thumb=R(ICON_MAIN_TVLIVE), tagline=tagline, summary=summ, fparams=fparams)
	
	# 29.09.2019 Umstellung Livestreams auf ARD Audiothek
	#	erneut ab 02.11.2020 nach Wegfall web.ard.de/radio/radionet
	# Button für Livestreams anhängen (eigenes ListItem)		# Radio-Livestreams
	tagline = u'die Radio-Livestreams stehen auch in der neuen ARD Audiothek zur Verfügung'
	title = u'Radio-Livestreams'	
	fparams="&fparams={'title': '%s', 'myhome': 'ARD'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=R(FANART), 
		thumb=R(ICON_MAIN_RADIOLIVE), tagline=tagline, fparams=fparams)
		
		
	if SETTINGS.getSetting('pref_use_podcast') ==  'true':		# Podcasts / Audiothek
			tagline	= 'ARD Audiothek | Die besten Podcasts der ARD und weitere Podcasts'
			fparams="&fparams={'title': 'ARD Audiothek'}"
			label = 'ARD Audiothek'
			addDir(li=li, label=label, action="dirList", dirID="AudioStart", fanart=R(FANART), 
				thumb=R(ICON_MAIN_AUDIO), tagline=tagline, fparams=fparams)
						
	# Download-/Aufnahme-Tools. im Hauptmenü  entfernt | bis Ende 2023 im Hauptmenü, seit 
	#	2022 zusätzlich in Infos+Tools
				
	if SETTINGS.getSetting('pref_showFavs') ==  'true':			# Favoriten einblenden
		tagline = "Kodis ARDundZDF-Favoriten zeigen und aufrufen"
		fparams="&fparams={'mode': 'Favs'}"
		addDir(li=li, label='Favoriten', action="dirList", dirID="ShowFavs", 
			fanart=R(FANART), thumb=R(ICON_DIR_FAVORITS), tagline=tagline, fparams=fparams)	
				
	if SETTINGS.getSetting('pref_watchlist') ==  'true':		# Merkliste einblenden
		tagline = 'Merkliste des Addons'
		if SETTINGS.getSetting('pref_merkextern') ==  'true': 
			add1 = u"[B]Setting:[/B] externe Merkliste eingeschaltet"
			add2 = u"externer Dateipfad fehlt"
			if SETTINGS.getSetting('pref_MerkDest_path'):
				add2 = u"externer Dateipfad ausgewählt"
			tagline = "%s\n\n%s | %s" % (tagline, add1, add2)
		fparams="&fparams={'mode': 'Merk'}"
		addDir(li=li, label='Merkliste', action="dirList", dirID="ShowFavs", 
			fanart=R(FANART), thumb=R(ICON_DIR_WATCH), tagline=tagline, fparams=fparams)		
								
	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if SETTINGS.getSetting('pref_info_update') == 'true': 		# Updatehinweis beim Start des Addons 
		ret = updater.update_available(VERSION)
		if ret[0] == False:		
			msg1 = "Github ist nicht erreichbar"
			msg2 = 'update_available: False'
			PLog("%s | %s" % (msg1, msg2))
			MyDialog(msg1, msg2, '')
		else:	
			int_lv = ret[0]			# Version Github
			int_lc = ret[1]			# Version aktuell
			latest_version = ret[2]	# Version Github, Format 1.4.1
			
			if int_lv > int_lc:									# Update-Button "installieren" zeigen
				call_update = True
				title = 'neues Update vorhanden - jetzt installieren'
				summ = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
				# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
				url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
				fparams="&fparams={'url': '%s', 'ver': '%s'}" % (quote_plus(url), latest_version) 
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(FANART), 
					thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summ)
			
	if call_update == False:									# Update-Button "Suche" zeigen	
		title  = 'Addon-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summ = u'Quelle: github.com/rols1\n\n'
		summ = u"%sHinweis: zwischen den Updates sind Einzelupdates in Infos + Tools möglich"	% summ		
		tag = u'Suche nach neuen Updates starten'
		fparams="&fparams={'title': 'Addon-Update'}"
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(FANART), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams, tagline=tag, summary=summ)

	summ = '[B]Infos und Tools zu diesem Addon[/B]'				# Menü Infos + Tools
	summ= u'%s\n- Zuletzt-gesehen-Liste' % summ
	summ= u'%s\n- Ausschluss-Filter bearbeiten' % summ
	summ= u"%s\n- Merkliste bereinigen" % summ
	summ= u"%s\n- Merklisten-Ordner bearbeiten" % summ
	summ= u'%s\n- Suchwörter bearbeiten' % summ
	summ= u'%s\n- Refresh TV-Livestream-Quellen' % summ
	summ = "%s\n-%s" % (summ, "Download- und Aufnahme-Tools")
	if SETTINGS.getSetting('pref_strm') == 'true':
		summ = "%s\n-%s" % (summ, "strm-Tools")
	if SETTINGS.getSetting('pref_playlist') == 'true':
		summ = "%s\n-%s\n-%s" % (summ, "PLAYLIST-Tools", "Settings inputstream.adaptive")
	summ = "%s\n-%s" % (summ, "Kodis Thumbnails-Ordner bereinigen")
	summ = "%s\n\n%s" % (summ, u"[B]Einzelupdate[/B] (für einzelne Dateien des Addons)")
	fparams="&fparams={}" 
	addDir(li=li, label='Infos + Tools', action="dirList", dirID="InfoAndFilter", fanart=R(FANART), thumb=R(ICON_INFO), 
		fparams=fparams, summary=summ)

	# Updatehinweis wird beim Caching nicht aktualisiert
	if SETTINGS.getSetting('pref_info_update') == 'true':
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	else:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#----------------------------------------------------------------
# Aufruf Main
# div. Addon-Infos + Filter (Titel) setzen/anlegen/löschen
# Filter-Button nur zeigen, wenn in Settings gewählt
# Juni 2022 verlagert zum neuen tools-Modul: ShowText, AddonInfos, 
#	AddonStartlist, SearchWordTools, FilterTools.
#
def InfoAndFilter():
	PLog('InfoAndFilter:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)									# Home-Button
	
	try:
		import resources.lib.tools
	except:
		pass	

	# AddonStartlist()	# Debug
#---------------------------------------------------			
															# Button changelog.txt
	tag= u'Störungsmeldungen bitte via Kodinerds-Forum, Github-Issue oder rols1@gmx.de'
	summ = u'für weitere Infos zu bisherigen Änderungen [B](changelog.txt)[/B] klicken'
	path = os.path.join(ADDON_PATH, "changelog.txt") 
	title = u"Änderungsliste [B](changelog.txt)[/B]"
	title=py2_encode(title)
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ShowText", fanart=R(FANART), 
		thumb=R(ICON_TOOLS), fparams=fparams, summary=summ, tagline=tag)		
							
	title = u"Addon-Infos"									# Button für Addon-Infos
	tag = u"[B]Infos zu Version, Cache und Dateipfaden.[/B]" 
	summ = u"Bei aktiviertem Debug-Log erfolgt die Ausgabe auch dort"
	summ = u"%s (nützlich zum Kopieren der Pfade)." % summ
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="AddonInfos", fanart=R(FANART), 
		thumb=R(ICON_PREFS), tagline=tag, summary=summ, fparams=fparams)	
			
	if SETTINGS.getSetting('pref_startlist') == 'true':		# Button für LastSeen-Funktion
		maxvideos = SETTINGS.getSetting('pref_max_videos_startlist')
		title = u"Zuletzt gesehen"	
		tag = u"[B]Liste der im Addon gestarteten Videos (max. %s Einträge, keine Livestreams).[/B]" % maxvideos
		tag = u"%s\n\nSortierung absteigend (zuletzt gestartete Videos zuerst)." % tag
		summ = u"Klick startet das Video (falls noch existent)."
		fparams="&fparams={}" 
		addDir(li=li, label=title, action="dirList", dirID="AddonStartlist", fanart=R(FANART), 
			thumb=R("icon-list.png"), tagline=tag, summary=summ, fparams=fparams)	
		
	if SETTINGS.getSetting('pref_usefilter') == 'true':											
		title = u"Filter bearbeiten"						# Button für Filter
		tag = u"[B]Ausschluss-Filter bearbeiten[/B]\n\nnur für Beiträge von ARD und ZDF" 								
		fparams="&fparams={}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterTools", 
			fanart=R(FANART), thumb=R(ICON_FILTER), tagline=tag, fparams=fparams)
			
	title = u"Merkliste bereinigen"							# Button für Bereinigung der Merkliste 
	tag = u"Nicht mehr erreichbare Beiträge listen und nach Abfrage löschen." 
	tag = u"%s\n\n[B]Ablauf[/B]: enthaltene Url's (Webseiten, Bildverweise) werden angepingt und der Status bewertet." % tag
	tag = u"%s\nEin [B]HTTP Timeout[/B] schließt eine spätere Erreichbarkeit nicht aus." % tag
	tag = u"%s\nSucheinträge werden durchgewinkt." % tag
	summ = u"Die Dauer ist von vielen Faktoren abhängig und nicht kalkulierbar (Testläufe mit 90 Einträgen: ca. 30 sec)"	
	summ = u"%s\n\nEin [B]Backup[/B] der Datei merkliste.xml im userdata-Verzeichnis wird empfohlen" % summ					
	summ = u"%s (insbesondere bei externer Merkliste)." % summ					
	myfunc="resources.lib.merkliste.clear_merkliste"

	fparams="&fparams={'myfunc': '%s', 'fparams_add': 'clear'}"  % quote(myfunc)		
	addDir(li=li, label=title, action="dirList", dirID="start_script",\
		fanart=R(FANART), thumb=R(ICON_DIR_WATCH), tagline=tag, summary=summ, fparams=fparams)	
				
	title = u"Merklisten-Ordner bearbeiten"					# Button für Bearbeitung der Merklisten-Ordner 
	tag = u"Ordner der Merklisten hinzufügen oder entfernen." 
	tag = u"%s\nBasis-Ordnerliste wiederherstellen (Reset der Ordnerliste)." % tag
	fparams="&fparams={'fparams_add': 'do_folder'}" 		# Variante ohne start_script, in Merkliste identische
															# Verarbeitung sys.argv	(Funktionscall erst dort)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.merkliste.do_folder",\
		fanart=R(FANART), thumb=R(ICON_DIR_WATCH), tagline=tag, fparams=fparams)	
				
			
	title = u"Suchwörter bearbeiten"						# Button für Suchwörter
	tag = u"[B]Suchwörter bearbeiten (max. 24)[/B]\n\n"
	tag = u"(nur für die gemeinsame Suche in ARD-/ZDF Mediathek und der Merkliste.)" 								
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.SearchWordTools", 
		fanart=R(FANART), thumb=R('icon_searchwords.png'), tagline=tag, fparams=fparams)	
			
	title = u"Refresh: Addon-Cache für TV-Livestream-Quellen" 
	ays = int(SETTINGS.getSetting('pref_tv_store_days'))
	tag = u"ARD- und ZDF-TV-Livestream-Quellen aktualisieren.\n"
	tag = u"%sDas eingestellte Setting ([B]%s Tage[/B]) bleibt unverändert" % (tag, days)
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="refresh_streamlinks",
		fanart=R(FANART), thumb=R('tv-livestreams_grey.png'), tagline=tag, fparams=fparams)	
			
	# hier ohne Abhängigkeit vom Setting pref_use_downloads:
	tagline = u'[B]Downloads und Aufnahmen[/B]\n\nVerschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
	fparams="&fparams={}"
	addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
		fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	
	
				
	if SETTINGS.getSetting('pref_strm') == 'true':											
		title = u"strm-Tools"								# Button für strm-Tools
		tag = u"[B]strm-Tools - Details siehe Addon-Wicki auf Github[/B]"
		tag = u"%s\n\nAbgleichintervall in Stunden\nListen anzeigen\nListeneinträge löschen\n" % tag
		tag = u"%sMonitorreset\nstrm-Log anzeigen\nAbgleich einer Liste erzwingen\n" % tag
		tag = u"%sunterstützte Sender/Beiträge\nzu einem strm-Verzeichnis wechseln" % tag
		myfunc="resources.lib.strm.strm_tools"
		fparams_add = quote('{}')

		fparams="&fparams={'myfunc': '%s', 'fparams_add': '%s'}"  %\
			(quote(myfunc), quote(fparams_add))			
		addDir(li=li, label=title, action="dirList", dirID="start_script",\
			fanart=R(FANART), thumb=R("icon-strmtools.png"), tagline=tag, fparams=fparams)	

	
	# Problem beim Abspielen der Liste - s. PlayMonitor (Modul playlist)
	if SETTINGS.getSetting('pref_playlist') == 'true':
		MENU_STOP = os.path.join(ADDON_DATA, "menu_stop") 	# Stopsignal für Tools-Menü (Haupt-PRG)								
		if os.path.exists(MENU_STOP):						# verhindert Rekurs. in start_script 
			os.remove(MENU_STOP)							# gesetzt in playlist_tools
			
		title = u"PLAYLIST-Tools"							# Button für PLAYLIST-Tools
		myfunc="resources.lib.playlist.playlist_tools"
		fparams_add = quote('{"action": "playlist_add", "add_url": "", "menu_stop": "true"}') # hier json-kompat.
		
		tag = u"[B]Abspielen und Verwaltung der addon-internen Playlist[/B]"
		tag = u"%s\n\nEinträge werden via Kontextmenü von abspielbaren Videos hinzugefügt." % tag
		tag = u"%s\n\nLivestreams werden abgewiesen." % tag			
		summ = u"Die PLAYLIST-Tools stehen auch im Kontextmenü zur Verfügung." 

		fparams="&fparams={'myfunc': '%s', 'fparams_add': '%s'}"  %\
			(quote(myfunc), quote(fparams_add))			
		addDir(li=li, label=title, action="dirList", dirID="start_script",\
			fanart=R(FANART), thumb=R("icon-playlist.png"), tagline=tag, summary=summ, fparams=fparams)	
			
	dz = get_dir_size(THUMBNAILS)							# Thumbnails-Ordner bereinigen
	dz = "[B](%s)[/B]" % dz
	title = u"Kodis Thumbnails-Ordner bereinigen %s" % dz	
	tag = u'[B]Kodis Thumbnails-Ordner bereinigen[/B]'
	summ = u"Das Bereinigen schafft Platz, indem es ältere Bilder entfernt (Auswahl: Dateien älter als 1-100 Tage)."
	summ = u"%s\nDadurch kann sich die Anzeige älterer Beiträge anfangs verzögern." % summ
	summ = u"%s\n\nDer aktuelle Füllstand %s kann auch im Menü Addon-Infos eingesehen werden." % (summ, dz)
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.ClearUpThumbnails",\
		fanart=R(FANART), thumb=R("icon-clear.png"), tagline=tag, summary=summ, fparams=fparams)	

	
	addon_id='inputstream.adaptive'; cmd="openSettings"		# Settings inputstream-Addon öffnen
	try:													# Check inputstream-Addon
		inp_vers = xbmcaddon.Addon(addon_id).getAddonInfo('version')
	except:
		inp_vers=""
	PLog("inp_vers: " + inp_vers)			
	if inp_vers and SETTINGS.getSetting('pref_inputstream') == 'true':
		title = u"Settings inputstream.adaptive-Addon (v%s) öffnen" % inp_vers
		akt="EIN"
		if SETTINGS.getSetting('pref_UT_ON') == "false":
			akt="AUS"
		tag = u"Bandbreite, Auflösung und weitere Einstellungen."
		tag = u"%s\nDie Nutzung ist [B]%s-[/B]geschaltet (siehe Modul-Einstellungen von ARDundZDF)" % (tag, akt)
		fparams="&fparams={'addon_id': '%s', 'cmd': '%s'}" % (addon_id, cmd)
		addDir(li=li, label=title, action="dirList", dirID="open_addon",\
			fanart=R(FANART), thumb=R("icon-inp.png"), tagline=tag, fparams=fparams)	
			
	
	dt, lt = resources.lib.tools.get_foruminfo()					# Datum, letzter Eintrag
	# dt=""; lt="" # Debug
	item = "zuletzt: [B]%s[/B] | %s" % (dt, lt)		
	title = u"Einzelupdate (einzelne Dateien und Module), %s" % dt	# Update von Einzeldateien
	tag = u'[B]Update einzelner Dateien aus dem Github-Repo des Addons'
	tag = u"%s\n\nEinzelupdates ermöglichen kurzfristige Fixes und neue Funktionen zwischen den regulären Updates." % tag
	summ = u"Anstehende Einzelupdates werden im Forum kodinerds im Startpost des Addons angezeigt"
	summ = u"%s - %s" % (summ, item)								# Forum-Info
	fparams="&fparams={'PluginAbsPath': '%s'}" % PluginAbsPath
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.EPG.update_single",\
		fanart=R(FANART), thumb=R("icon-update-einzeln.png"), tagline=tag, summary=summ, fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#---------------------------------------------------------------- 
# Aufruf: InfoAndFilter (-> Module strm, merkliste, playlist)
# Bei der Merkliste erfolgt der Funktionscall bis auf Weiteres  nicht hier 
#	sondern am Modulende durch Auswertung von sys.argv (ähnlich beim Context-Call,
#	aber getrennte return-Behandlung, s. ignore_this_network_error bzw. exit()
# 	in merkliste).
#	
# Wg.  Problemen mit der xbmc-Funktion executebuiltin(RunScript()) verwenden
#	wir importlib wie in router()
#	Bsp. myfunc: "resources.lib.playlist.items_add_rm" (relatv. Modulpfad + Zielfunktion)
#	fparams_add json-kompat., Bsp.: '{"action": "playlist_add", "url": ""}'
# Um die Rekursion der Web-Tools-Liste zu vermeiden wird MENU_STOP in playlist_tools
#	gesetzt und in InfoAndFilter wieder entfernt.
# Beispiel fparams bei Direktaufruf (is_dict=False):   
#					fparams="{'strmpath': '%s'}" % strmpath	 
#					fparams = quote(fparams)
#					start_script(myfunc, fparams)
#
def start_script(myfunc, fparams_add, is_dict=True):
	PLog("start_script:")
	import importlib
	PLog(type(fparams_add))
	fparams_add = unquote(fparams_add)
	PLog(myfunc); PLog(fparams_add)
	
	l = myfunc.split('.')									# Bsp. resources.lib.updater.update
	PLog(l)
	newfunc =  l[-1:][0]									# Bsp. updater
	dest_modul = '.'.join(l[:-1])

	dest_modul = importlib.import_module(dest_modul )		# Modul laden
	PLog('loaded: ' + str(dest_modul))
	func = getattr(dest_modul, newfunc)	

	if is_dict == False:									# Direktaufruf
		try:
			fparams_add = fparams_add.replace("'", "\"")
			fparams_add = fparams_add.replace('\\', '\\\\')	
		except Exception as exception:
			PLog('router_exception: {0}'.format(str(exception)))	
		PLog(fparams_add)
		
	if fparams_add != '""':									# leer, ohne Parameter?	
		mydict = json.loads(fparams_add)
		PLog("mydict: " + str(mydict));
		func(**mydict)
	else:
		func()

	#xbmc.sleep(500)
	# ohne endOfDirectory wird das Fenster des Videoplayers blockiert (Ladekreis):
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True) 	 
	
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# 18.01.2021 Abgleich mit STARTLIST in items_add_rm (Modul Playlist)
# Problem: Videos aus Startlist speichert Kodi in MyVideos, table files, 
#	nicht mit Plugin-Pfad, sondern mit http-Url-Extension (z.B. master.m3u8). 
#	Damit sind folgende Abgleiche über die DB MyVideos nicht mehr möglich 
#	(s. lokale Doku 00_sqlite).
# Lösung 14.01.2024: Scan Player.getTime (monitor_resume in util). Der
#	Resume-Abgleich mit Dialog erfolgt in check_Resume über seekPos in 
#	STARTLIST. Überschneidungen mit Kodi-Resume möglich.
# mediatype="video" erforderlich - ohne sind Total-Blockaden in 
#	monitor_resume möglich.
#
def AddonStartlist(mode='', query=''):
	PLog('AddonStartlist:');
	PLog(mode); PLog(query)
	maxvideos = SETTINGS.getSetting('pref_max_videos_startlist')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)										# Home-Button
	img = R("icon-list.png")
	startlist=''; mylist=""

	PLog("STARTLIST: " + STARTLIST)
	if os.path.exists(STARTLIST):
		mylist= RLoad(STARTLIST, abs_path=True)				# Zuletzt gesehen-Liste laden
	if mylist == '':
		msg1 = u'"Zuletzt gesehen"-Liste nicht gefunden.'
		MyDialog(msg1, '', '')
		return
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
	mylist=py2_encode(mylist)
	mylist= mylist.strip().splitlines()
	PLog(len(mylist))
	try:														# Sortierung unixtime-stamp 1704966112[.0###..]
		startlist = sorted(mylist, key=lambda x: re.search(r'(\d+).', x).group(1), reverse=True)
	except Exception as exception:
		PLog("sorted_error: " + str(exception))
		startlist = mylist										# unsortiert

	if mode == 'search':										# Suche
		query = get_keyboard_input() 
		if query == None or query.strip() == '': 				# None bei Abbruch
			pass
		else:
			query = query.strip()	
			query = py2_encode(query)							# decode in up_low	

		
	title = u'Suche in der "Zuletzt gesehen"-Liste"'			# Suchbutton
	tag = u"Suche der im Addon gestarteten Videos (max %s)."  % maxvideos
	tag = u"%s\n\nGesucht wird in Titel und Infotext." % tag
	fparams="&fparams={'mode': 'search'}" 
	addDir(li=li, label=title, action="dirList", dirID="AddonStartlist", fanart=img, 
		thumb=R(ICON_SEARCH), tagline=tag, fparams=fparams)	
			
	cnt=0; 
	for item in startlist:
		#PLog(item)
		Plot=''; sub_path=''; seekPos=""; video_dur=""; resume=""
		ts, title, url, thumb, Plot = item.split('###')[0:5]	# altes Format ohne sub_path, seekPos
		if "sub_path" in item:
			sub_path = stringextract("###sub_path:", "###", item)
		if "seekPos" in item:									# ..###seekPos:75.197###
			seekPos = stringextract("###seekPos:", "###", item)
			PLog("seekPos: " + seekPos)
			if seekPos:
				seekPos = float(seekPos)
		if "video_dur" in item:									# ..###video_dur:460.0###
			video_dur = stringextract("###video_dur:", "###", item)
		
		dt = datetime.datetime.fromtimestamp(float(ts))			# Date-Objekt
		my_date = dt.strftime("%d.%m.%Y %H:%M:%S")
		my_date = "[COLOR darkgoldenrod]%s[/COLOR]" % my_date
		if seekPos:
			if seekPos >= 40:						   			# Min. 40  Sek. (mögl. bei Trailern)
				resume = seconds_translate(seekPos)
			if resume:
				my_date = "%s | gesehen bis: %s" % (my_date, resume)
			
		Plot_par = "gestartet: %s\n\n%s" % (my_date, Plot)
		Plot_par=py2_encode(Plot_par); 		
		Plot_par=Plot_par.replace('\n', '||')					# für router
		tag=Plot_par.replace('||', '\n')
		
		PLog("Satz16:"); 
		PLog(title); PLog(ts); PLog(url); PLog(Plot_par); 
		PLog(sub_path); PLog(video_dur)
		show = True
		if 	query:												# Suchergebnis anwenden
			q = up_low(query, mode='low'); i = up_low(item, mode='low');
			PLog(q in i)
			show = q in i										# Abgleich 		
		PLog(show)
		
		if show == True:		
			url=py2_encode(url); title=py2_encode(title);  
			thumb=py2_encode(thumb); thumb=py2_encode(thumb);
			fparams="&fparams={'url':'%s','title':'%s','thumb':'%s','Plot':'%s','sub_path':'%s','seek':'%s','dur':'%s'}" %\
				(quote_plus(url), quote_plus(title), quote_plus(thumb), quote_plus(Plot_par), 
				quote_plus(sub_path), seekPos, video_dur)
			addDir(li=li, label=title, action="dirList", dirID="check_Resume", fanart=img, thumb=thumb, 
				fparams=fparams, tagline=tag, mediatype="video")
			cnt = cnt+1 	

	PLog(cnt);
	if query:
		if cnt == 0:
			msg1 = u"Suchwort >%s< leider nicht gefunden" % py2_decode(query)
			MyDialog(msg1, '', '')	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
							
#----------------------------------------------------------------
# Resume-Zeit ermitteln, Dialog-Abfrage, -> PlayVideo
# s.a. Kopfdoku AddonStartlist. Früherer sqlite-Code
# in sqlite_check_Resume.py (lokale Doku)
#
def check_Resume(url, title, thumb, Plot, sub_path, seek, dur):	
	PLog('check_Resume: ' + str(seek))
	if seek == "":
		seek = "0"
	if float(str(seek)) >= 40:						   		# Min. 40  Sek. wie  AddonStartlist
		resume = seconds_translate(seek); 
		total = seconds_translate(dur)
		PLog("resume: %s, total: %s" % (resume,total))
		
		msg1 = "Fortsetzen bei [B]%s[/B]?" % resume
		msg2 = "Gesamtdauer: [B]%s[/B]" % total
		msg3 = "Abbruch für neuen Start ab Beginn."
		ret=MyDialog(msg1, msg2, msg3, ok=False, yes='JA')
		PLog(ret)
		if ret != 1:
			seek=""

	PlayVideo(url, title, thumb, Plot, sub_path, seekTime=seek)
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True) 	# Rebuild Liste

#----------------------------------------------------------------
# Aufruf InfoAndFilter
# Addon-Infos (Pfade, Cache, ..)
# einschl. Log-Ausgabe 
def AddonInfos():
	PLog('AddonInfos:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	dialog = xbmcgui.Dialog()
	t = "     "		# Tab (5)

	a = u"[COLOR red]Addon, System:[/COLOR]"
	a1 = u"%s%s, Version %s vom %s" % (t, ADDON_ID, VERSION, VDATE)
	a2 = u"%sGithub-Releases https://github.com/%s/releases" % (t, GITHUB_REPOSITORY)
	a3 = u"%sOS: %s" % (t, OS_DETECT)
	a4 = u"%sKodi-Version: %s" % (t, KODI_VERSION)
	p1 = u"%s\n%s\n%s\n%s\n%s\n" % (a,a1,a2,a3,a4)
	
	a = u"[COLOR red]Cache:[/COLOR]"
	a1 = u"%s %10s Thumbnails (Kodi gesamt)" %  (t, get_dir_size(THUMBNAILS))
	a2 = u"%s %10s Dict (Variablen, Objekte)" %  (t, get_dir_size(DICTSTORE))
	a3 = u"%s %10s Inhaltstexte (im Voraus geladen)" %  (t, get_dir_size(TEXTSTORE))
	a4 = u"%s %10s Slides (Bilder)" %   (t, get_dir_size(SLIDESTORE))
	a5 = u"%s %10s subtitles (Untertitel)" %   (t, get_dir_size(SUBTITLESTORE))
	a6 = ''
	path = SETTINGS.getSetting('pref_download_path')
	PLog(path); PLog(os.path.isdir(path))
	if path and os.path.isdir(path):
		a6 = "%s %10s Downloads\n" %   (t, get_dir_size(path))
	p2 = u"%s\n%s\n%s\n%s\n%s\n%s\n%s" % (a,a1,a2,a3,a4,a5,a6)

	a = u"[COLOR red]Pfade:[/COLOR]"
	a1 = u"%s [B]Addon-Home:[/B] %s" % (t, PluginAbsPath)
	a2 = u"%s [B]Cache:[/B] %s" % (t,ADDON_DATA)
	fname = WATCHFILE
	a3 = u"%s [B]Merkliste intern:[/B]\n%s %s" % (t, t, WATCHFILE)
	a4 = u"%s [B]Merkliste extern:[/B] nicht aktiviert" % t
	if SETTINGS.getSetting('pref_merkextern') == 'true':	# externe Merkliste gewählt?
		fname = SETTINGS.getSetting('pref_MerkDest_path')
		a4 = u"%s [B]Merkliste extern:[/B]\n%s %s" % (t,t,fname)
	a5 = u"%s [B]Downloadverzeichnis:[/B] %s" % (t,SETTINGS.getSetting('pref_download_path'))
	a6 = u"%s V[B]erschiebeverzeichnis:[/B] %s" % (t,SETTINGS.getSetting('pref_VideoDest_path'))
	filterfile = os.path.join(ADDON_DATA, "filter.txt")
	a7 = u"%s [B]Filterliste:[/B] %s" %  (t,filterfile)
	searchwords = os.path.join(ADDON_DATA, "search_ardundzdf")
	a8 = u"%s [B]Suchwortliste:[/B] %s" %  (t,searchwords)
	log = xbmc.translatePath("special://logpath")
	log = os.path.join(log, "kodi.log")
	size = humanbytes(os.path.getsize(log)) 
	size = "[B]%s[/B]" %  size	
	if "GB" in size or "TB" in size:
		size = "[COLOR red]%s !!![/COLOR]" %  size	
	a9 = u"%s [B]Debug-Log:[/B] %s | %s" %  (t, log, size)
	a10 = u"%s [B]TV-und Event-Livestreams:[/B] %s/%s" % (t, PluginAbsPath, "resources/livesenderTV.xml")
	
	p3 = u"%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % (a,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10)
	page = u"%s\n%s\n%s" % (p1,p2,p3)
	
	#--------------------------------------------------					# Module
	mpage = u"\n[COLOR red]Module:[/COLOR]"
	globFiles = "%s/%s/*py" % (PluginAbsPath, "resources/lib")
	files = glob.glob(globFiles) 
	files = sorted(files,key=lambda x: x.upper())
	# PLog(files)			# Debug
	for f in files:
		if "__init__.py" in f:
			continue
		modul = f.split('/')[-1]
		modul = modul.replace('.py', '')
		fcont = RLoad(f, abs_path=True)
		datum = stringextract('Stand:', '#', fcont)
		datum = datum.strip()
		
		datum = "%s %16s (Stand: %s)" % (t, modul, datum)		
		mpage = "%s\n%s" % (mpage, datum) 
	
	page = page + mpage
	PLog(cleanmark(page))
	dialog.textviewer(u"Addon-Infos (Ausgabe auch im Debug-Log bei aktiviertem Plugin-Logging)", page,usemono=True)
	
#	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#----------------------------------------------------------------
# Aufruf Info_Filter
# 20.01.2020 usemono für textviewer (ab Kodi v18)
# dialog.select ungeeignet (Font zu groß, Zeilen zu schmal)
# 02.02.2021 erweitert mit direkter page-Übergabe
# Hinw.: usemono wirkt nicht, falls im Skin der Font Arial
#	gewählt ist (notwend. für arabische Schrift (ZDFarabic) 
#
def ShowText(path, title, page=''):
	PLog('ShowText:'); 
	
	if page == '':
		page = RLoad(path, abs_path=True)
		page = page.replace('\t', ' ')		# ersetze Tab's durch Blanks
	
	dialog = xbmcgui.Dialog()
	dialog.textviewer(title, page,usemono=True)
	
	return
	
#----------------------------------------------------------------
#  03.06.2021 Main_ARD (Classic) entfernt
# def Main_ARD(name, sender=''):		 		
#---------------------------------------------------------------- 
def Main_ZDF(name=''):
	PLog('Main_ZDF:'); PLog(name)
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'Sender: [B]alle Sender des ZDF[/B]' 
		title=py2_encode(title);
		func = "ardundzdf.Main_ZDF"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ZDF", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_MAIN_ARD), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
		
	title="Suche in ZDF-Mediathek"
	fparams="&fparams={'title': '%s', 'homeID': 'ZDF'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
		fanart=R(ICON_ZDF_SEARCH), thumb=R(ICON_ZDF_SEARCH), fparams=fparams)
		
	title = 'Startseite' 
	fparams="&fparams={'ID': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Start", fanart=R(ICON_MAIN_ZDF), thumb=R(ICON_MAIN_ZDF), 
		fparams=fparams)

	title = 'ZDF-funk' 
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="Main_ZDFfunk", fanart=R(ICON_MAIN_ZDF), thumb=R('zdf-funk.png'), 
		fparams=fparams)

	title = 'Sendung verpasst' 
	fparams="&fparams={'name': 'ZDF-Mediathek', 'title': '%s'}" % title 
	addDir(li=li, label=title, action="dirList", dirID="ZDF_VerpasstWoche", fanart=R(ICON_ZDF_VERP), 
		thumb=R(ICON_ZDF_VERP), fparams=fparams)	

	title = 'Sendungen A-Z' 
	fparams="&fparams={'name': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_AZ", fanart=R(ICON_ZDF_AZ), 
		thumb=R(ICON_ZDF_AZ), fparams=fparams)

	# -------------------
	# 05.03.2024 Rubriken, Sportstudio, Barrierearm, ZDFinternational -> ZDF_RubrikSingle
	base = "https://zdf-prod-futura.zdf.de/mediathekV2/"

	title = 'Rubriken' 
	url = base + "categories-overview"
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
	addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=R(ICON_ZDF_RUBRIKEN), 
		thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)

	title = "ZDF-Sportstudio"
	url = base + "document/sport-106"
	tag = u"Aktuelle News, Livestreams, Liveticker, Ergebnisse, Hintergründe und Sportdokus. Sportstudio verpasst? Aktuelle Sendungen einfach online schauen!"
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
	addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=R("zdf-sport.png"), 
		thumb=R("zdf-sport.png"), tagline=tag, fparams=fparams)
		
	title = "Barrierearm"
	url = base + "document/barrierefrei-im-zdf-100"
	tag = u"Alles an einem Ort: das gesamte Angebot an Videos mit Untertiteln, Gebärdensprache und Audiodeskription sowie hilfreiche Informationen zum Thema gebündelt."
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
	addDir(li=li, label="Barrierearm", action="dirList", dirID="ZDF_RubrikSingle", fanart=R(ICON_ZDF_BARRIEREARM), 
		thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)

	title = "ZDFinternational"
	url = base + "document/international-108"
	tag = "This channel provides selected videos in English, Spanish or Arabic or with respective subtitles."
	summ = 'Kodi Leia and older: for Arabic, please set the font of your Skin to "Arial based".'
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
	addDir(li=li, label="ZDFinternational", action="dirList", dirID="ZDF_RubrikSingle", fanart=R('ZDFinternational.png'), 
		thumb=R('ZDFinternational.png'), tagline=tag, summary=summ, fparams=fparams)
	# -------------------

	fparams="&fparams={}"
	addDir(li=li, label="Bilderserien", action="dirList", dirID="ZDF_Bildgalerien", fanart=R(ICON_ZDF_BILDERSERIEN), 
		thumb=R(ICON_ZDF_BILDERSERIEN), fparams=fparams)

	fparams="&fparams={}"												# ab V 4.8.1
	addDir(li=li, label="Teletext ZDF", action="dirList", dirID="ZDF_Teletext", fanart=R("teletext_zdf.png"), 
		thumb=R("teletext_zdf.png"), fparams=fparams)
	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
def Main_ZDFfunk(title):
	PLog('Main_ZDFfunk:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	title = 'funk-Startseite' 
	fparams="&fparams={'ID': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Start", fanart=R('zdf-funk.png'), thumb=R('zdf-funk.png'), 
		fparams=fparams)

	fparams="&fparams={'name': 'ZDF-funk-A-Z', 'ID': 'ZDFfunk'}"
	addDir(li=li, label="ZDF-funk-A-Z", action="dirList", dirID="ZDF_AZ", fanart=R('zdf-funk-AZ.png'), 
		thumb=R('zdf-funk-AZ.png'), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
##################################### Start Teletext ###############################################
# Die Mobilversion /teletext/zdf/mobil.html basiert auf /teletext/zdf/seiten/100.html
# Für Seite 666 ist Umschaltung auf zdfinfo notwendig (beim zdf fehlt die Aktien-Tabelle)
#
def ZDF_Teletext(path=""):
	PLog('ZDF_Teletext:')
	
	if path == "":
		path = "https://teletext.zdf.de/teletext/zdf/seiten/100.html"
	if path.endswith("666.html"):										# -> zdfinfo, s.o.
		path = "https://teletext.zdf.de/teletext/zdfinfo/seiten/666.html"
	base = "https://teletext.zdf.de/teletext/zdf/seiten/"
	img = R(ICON_MAIN_ZDF)
	thumb = R("teletext_zdf.png")
		
	Seiten = ["Startseite|100", "Rubriken|101", "Inhalt A-Z (bis ca. 108)|102", 
		"Nachrichten|112", "Politbarometer|165", "Wetter|170", "Sport|200",
		"Programm|300", "Flughafen|575", "Börse|600", 
		]
		
	#  ZDF korrigiert nicht selbst 
	if url_check(path, caller='ZDF_Teletext', dialog=False) == False:   # falsche Seite manuell?
		aktpg = re.search(r'seiten/(.*?).html', path).group(1)
		msg1 = u'Seite %s' % aktpg
		msg2 = u'nicht verfügbar'
		icon = thumb		
		xbmcgui.Dialog().notification(msg1,msg2,img,3000)
		PLog("coreccted: %s -> %s" % (aktpg, "100"))
		path = "https://teletext.zdf.de/teletext/zdf/seiten/100.html"
		
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in ZDF_Teletext:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))		
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')			# Home-Button

	body =  stringextract('<body',  'footer_container', page)
	footer =  page.split('footer_container')[-1]
	PLog(body[:60]);  PLog(footer[:60])

	prevpg = re.search(r'prevpg="(.*?)"', body).group(1)				# body-Start
	if prevpg == "0":													# 0 -> Startseite
		prevpg = "100"
	nextpg = re.search(r'nextpg="(.*?)"', body).group(1)
	aktpg =  re.search(r'page="(.*?)"', body).group(1)
	PLog("prevpg: %s, nextpg: %s, aktpg: %s, lines: %d" % (prevpg, nextpg, aktpg, len(body.splitlines())))

	if len(body.splitlines()) <= 6:										# body-, footer-, copy- plus 3 Leerzeilen, 
		msg1 = "Seite [B]%s[/B]: leider keine" % aktpg					#	Bsp. 777 (Untertitel)
		msg2 = "Inhalte gefunden."
		MyDialog(msg1, msg2, '')	
		return
		
	#------------------------------------------------					# Body
	PLog("get_tables:")
	hrefs = ZDF_Teletext_Table(li, body, aktpg)							# <a href= .. </a>##<a href= .. </a> 
	
	# ---------------------------------------							# Footer
	prevpg = int(aktpg) - 1												# vorwärts/rückwärts
	nextpg = int(aktpg) + 1
	if prevpg < 100:
		prevpg = 899
	if nextpg > 899:
		nextpg = 100
	
	title = u"rückwärts zu [B]%s[/B]"	% prevpg
	thumb = R("icon-previos.png")
	href = "%s%s.html" % (base, prevpg)
	fparams="&fparams={'path': '%s'}" % quote(href)
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Teletext", fanart=img, thumb=thumb, 
		fparams=fparams)			
			
	title = u"vorwärts zu [B]%s[/B]"	% nextpg
	thumb = R("icon-next.png")
	href = "%s%s.html" % (base, nextpg)
	fparams="&fparams={'path': '%s'}" % quote(href) 
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Teletext", fanart=img, thumb=thumb, 
		fparams=fparams)				
		
	thumb = R("teletext_zdf.png")
	#------------------------------------------------------		# prominente Seiten
	tag=""
	PLog("proms:")
	for item in Seiten:
		title, pgnr = item.split("|")
		title = "[B]%s[/B]: %s" % (pgnr, title)	
		if "A-Z" in title:
			tag = title
		href = "%s%s.html" % (base, pgnr)
		fparams="&fparams={'path': '%s'}" % quote(href) 
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Teletext", 
			fanart=img, thumb=thumb, fparams=fparams, tagline=tag)

	#------------------------------------------------------		# manuelle Eingabe
	title = u"Seitenzahl manuell eingeben"
	thumb = R("teletext_zdf.png")
	basepath = base + "%s.html"
	func = "ZDF_Teletext" 
	fparams="&fparams={'func': '%s', 'basepath': '%s'}" % (quote(func), quote(basepath))
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Teletext_setPage", 
		fanart=img, thumb=thumb, fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#---------------------------------------------------------------- 
# Hinw.: in textviewer für monospaced Font die Kodi-Einstellung
#	"Standardwert des Skins" wählen
# Wetterkarten: liefert das ZDF anders als die ARD als bae64-kodierte
#	Gifs aus - Darstellung hier nach Schließen des Textviewers.
# 
def ZDF_Teletext_Table(li, body, aktpg):
	PLog('ZDF_Teletext_Table: ' + aktpg)
	base = "https://teletext.zdf.de/teletext/zdf/seiten/"
	thumb = R("teletext_zdf.png")
	img = R(ICON_MAIN_ZDF)
	colors = [ u"#0000FF|dunkelblau", u"#80FFFF|hellblau", 				# s. encycolorpedia.de
		u"#00FF00|grün", u"#FFFF00|gelb"]
	lines=[]; img_data=""; 
	
	html_lines = body.splitlines()
	PLog(len(html_lines))
	for i, hl in enumerate(html_lines[2:]):								# ab Zeile 2
		line=""; h1=""; left=""; leftp=""; center=""; right=""
		hl = hl.strip()
		PLog("%d. %s" %(i, hl[:80]))
		if hl.startswith('<h1>'):
			line = stringextract('<h1>',  '</', hl)
			lines.append(cleanhtml(line))
			continue
		if hl.startswith('<div class="table">'):						# Einzelzeile
			line = stringextract('table">',  '</', hl)
			lines.append(cleanhtml(line))
			continue
		if hl.startswith('<h2 class="headline_normal">'):				# Einzelzeile
			h2 = stringextract('headline_normal">',  '</h2>', hl)
			lines.append(cleanhtml(h2))
			continue
		if hl.startswith('<p class="copy" >'):							# Tochterzeile o. Link
			pre_line = lines[len(lines)-1]
			PLog("pre_line: " + pre_line); 
			new_line = cleanhtml(hl).rjust(len(pre_line)-5, ' ')
			PLog("pre_line: %s" % pre_line)
			PLog("new_line: %s" % new_line)
			lines.append(new_line)	
			continue
			
		if 	hl.startswith("<a href="):
			PLog("<a href=:")
			part_list = html_lines[i+2:]
			PLog(part_list[0])
			for i2, p in enumerate(part_list):
				if "</a>" in p:
					break
			new_ind = i + 2 + i2
			part_list = part_list[:i2]
			txt = "\n".join(part_list[:new_ind])						# String "<a href=" .. </a>"
			PLog("new_ind: %d, txt: %s" % (new_ind, txt[:60]))
			href = re.search(r'href="(.*?)"', txt).group(1)
			pagenr = href.split(".html")[0]
			if 'left">' in txt:											# News-Text
				left = stringextract('left">',  '</th>', txt)
			if "left_programm" in txt:									# EPG-Titel
				leftp = stringextract('left_programm">',  '</th>', txt)
			if 'class="center">' in txt:								# class="center">
				center = stringextract('class="center">',  '</th>', txt)
			if 'class="right">' in txt:									# class="right">
				right = stringextract('class="right">',  '</th>', txt)
				if pagenr in right:										# doppelt
					right=""
			left=cleanhtml(left.strip()); leftp=cleanhtml(leftp); 
			center=cleanhtml(center); right=cleanhtml(right);
			PLog("left: %s, center: %s, right: %s" % (left, center, right))
			if pagenr:
				line = "%s" % pagenr
			if left:
				line = "%s | %s" % (line, left)
			if leftp:
				line = "%s | %s" % (line, leftp)
			if center:
				line = "%s | %s" % (line, center)
			if right:
				line = "%s | %s" % (line, right)
			line = unescape(line)
			PLog(line)
			lines.append(line)	
			i=new_ind+1													# neuer Index
			continue			
			 
		if 	hl.startswith('<div class="link_button_a"'):				# ohne Link, z.B. Trennzeile bei A-Z
			PLog("link_button_a:")
			part_list = html_lines[i+2:]
			PLog(part_list[0])
			for i2, p in enumerate(part_list):
				if "</div>" in p:
					break
			new_ind = i + 2 + i2
			part_list = part_list[:i2]
			txt = "\n".join(part_list[:new_ind])						# String "<a href=" .. </a>"
			PLog("new_ind: %d, txt: %s" % (new_ind, txt[:60]))			
			if 'left">' in txt:											# News-Text
				left = stringextract('left">',  '</th>', txt)
			if "left_programm" in txt:									# EPG-Titel
				leftp = stringextract('left_programm">',  '</th>', txt)
			if 'class="center">' in txt:								# class="center">
				center = stringextract('class="center">',  '</th>', txt)
			left=cleanhtml(left); leftp=cleanhtml(leftp); 
			center=cleanhtml(center); right=cleanhtml(right);
			if left == "":
				left = "%3s" % " "										# padding fehlende pagenr
			PLog("left: %s, center: %s, right: %s" % (left, center, right))
			if left:
				line = left
			if leftp:
				line = "%s | %s" % (line, leftp)
			if center:
				line = "%s | %s" % (line, center)
			if right:
				line = "%s | %s" % (line, right)
			line = unescape(line)
			PLog(line)
			lines.append(line)	
			i=new_ind+1													# neuer Index
			continue
		
	#----------------------------------------------						# Wetter, 171.html
	
	if '<img src=' in body:
		PLog('<img src=')
		col=""
		tables = blockextract('<div class="table"', body)
		img_data = stringextract('base64,',  '"', body)
		line=""
		for table in tables:
			col=""
			line = stringextract('z-index:10">',  '</', table)
			if 'left:-10px;' in table:
				line =  stringextract('></div>',  '</', table)
			if 'background' in table:
				col = stringextract('background:',  ';', table)
			if col:
				this_col=""
				for item in colors:
					if col in item:
						this_col = item.split("|")[-1]
				if this_col:		
					line = "Farbe %s: %s" % (this_col, line)	
			PLog(line)
			if line:
				lines.append(line)	
		
	#----------------------------------------------						# Ausgabe
	
	PLog("anz_lines: %d" % len(lines))
	if len(lines) > 0:
		if aktpg == "100":
			h1 = "Startseite"
		if h1:
			title = "%s | %s" % (aktpg, h1)
		else:
			title = "Seite %s" % aktpg
		if title == "":
			title =  u'Seite %s' % aktpg
		if img_data:
			title = u'Seite %s | Bild kommt anschließend' % aktpg	# Titel fehlt hier
			
		lines = list(dict.fromkeys(lines))							# Duplikate entf.
		
		txt =  "\n".join(lines)
		txt = txt.strip()											# LF's vor + hinter txt entf.
		xbmcgui.Dialog().textviewer(title, txt,usemono=True)		# todo: Verzicht auf Bottom-Buttons	
			
		if img_data:												# Wetterkarten
			import base64
			img_data = py2_encode(img_data)
			fname = os.path.join("%s/teletext.png") % DICTSTORE	
			PLog(fname)
			with open(fname, "wb") as f:
				f.write(base64.urlsafe_b64decode(img_data))	
			ZDF_SlideShow(fname, single="True")	
		return
		
	msg1 = u'Seite %s' % aktpg
	msg2 = u'Inhalt nicht darstellbar'
	icon = thumb		
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
	PLog("%s: %s" % (msg1, msg2))			
	
	return
#---------------------------------------------------------------- 
# ohne Plausib.-Prüfung (Fehler: ARD -> 100, ZDF -> )
def ZDF_Teletext_setPage(func, basepath):
	PLog('ZDF_Teletext_setPage: ' + func)
	
	dialog = xbmcgui.Dialog()
	inp = dialog.input("Teletextseite (3-stellig):", type=xbmcgui.INPUT_NUMERIC)
	PLog(inp)
	if inp == '':
		return						# Listitem-Error, aber Verbleib im Listing
	
	path = basepath % inp
	PLog("path: " + path)
	fparams_add = "{'path': '%s'}" % path	
	
	if func.startswith("resources.lib"):
		start_script(func, fparams_add, is_dict=False)
	else:
		ZDF_Teletext(path)
	
	return

##################################### Start Audiothek ###############################################
# Aufruf: Main
# 24.07.2021 Revision nach Renovierung der Audiothek durch die ARD
# 19.02.2022 Neubau nach Strukturänderungen Web, api-json und
#	Web-json - lokale Doku: Ordner Audiothek
#
def AudioStart(title):
	PLog('AudioStart:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)						# Home-Button
					
	title="Suche in ARD Audiothek"				# Button Suche voranstellen
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="AudioSearch", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R(ICON_SEARCH), fparams=fparams)

	# Button für Livestreams anhängen (eigenes ListItem)		# Livestreams
	title = 'Livestreams'	
	fparams="&fparams={'title': '%s'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R(ICON_AUDIO_LIVE), fparams=fparams)

	img = R(ICON_MAIN_AUDIO)
	title_list = [u'Entdecken|ard-entdecken.png', u'Rubriken|ard-rubriken.png',
			u'Sportschau|ard-sport.png']								
	for item in title_list:
		title, img = item.split('|')
		tag=''
		if title == u"Entdecken":
			tag = "die Startseite  der Audiothek"
		fparams="&fparams={'title': '%s', 'ID': '%s'}" % (title, title)	
		addDir(li=li, label=title, action="dirList", dirID="AudioStartHome", fanart=R(ICON_MAIN_AUDIO), 
			thumb=R(img), tagline=tag, fparams=fparams)

	# Button für A-Z anhängen 									# A-Z alle Sender
	# 01.08.2021 nach Renovierung der Audiothek durch die ARD entfallen
	
	# Button für Sender anhängen 								# Sender/Sendungen (via AudioStartLive)
	title = 'Sender (Sendungen einzelner Radiosender)'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="AudioSenderPrograms", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R("ard-sender.png"), fparams=fparams)
	
	# Button für funk anhängen 									# funk
	title = 'funk'												# Watchdog: ../organizations
	tagline = "Podcasts des Senders funk"
	fparams="&fparams={'org': '%s'}" %  title
	addDir(li=li, label=title, action="dirList", dirID="AudioSenderPrograms", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R('funk.png'), tagline=tagline, fparams=fparams)
		
	# Button für podcast.de anhängen 							# podcast.de
	title = 'podcast.de'										#  Watchdog: 
	tagline = "Podcasts der Plattform www.podcast.de"
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDe", fanart=R('podcast-de.png'), 
		thumb=R('podcast-de.png'), tagline=tagline, fparams=fparams)		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# 31.07.2021 Revision nach Renovierung der Audiothek durch die ARD
# 19.02.2022 dto
# 02.11.2024 Aktualisierung path Sportschau (neues ARD-Schema 
#	../urn:ard:page:../
#
def AudioStartHome(title, ID, page='', path=''):	# Auswertung Homepage	
	PLog('AudioStartHome: ' + ID)
	li = xbmcgui.ListItem()
	
	ID = py2_decode(ID)
	if ID == 'Sportschau':								# Menü: Rubrik Sportschau herausgehoben
		path = 'https://www.ardaudiothek.de/rubrik/sportschau/urn:ard:page:cebf0dfe68c7f771/'
		ID = "AudioRubrikWebJson_%s" % "42914734"
		Audio_get_cluster_rubrik(li='', url=path, title='Sport', ID=ID)
		return
	if ID == 'Rubriken':							# Rubriken-Liste: eig. api-Call
		path = ARD_AUDIO_BASE + "editorialcategories"
	if ID == 'Entdecken':
		#path = ARD_AUDIO_BASE + "homescreen"		# Leitseite api
		path = "https://www.ardaudiothek.de/"		# Web: nur teilw. vollständig, Nachladen
							
	page, msg = get_page(path=path, header=HEADERS)
	if page == '':	
		msg1 = "Fehler in AudioStartHome:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))	
		
	li = home(li, ID='ARD Audiothek')				# Home-Button
		
	if ID == 'Entdecken':							# Stage Web, Sonderbhdl., Beiträge nicht im api 		
		Audio_get_homescreen(page)					# direkt o. li
	if ID == u'Rubriken':							# Rubrik Sport direkt s.o.
		ID = "AudioStartHome"
		Audio_get_rubriken_web(li, title, path, ID, page)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# 1. Aufruf: (ID=AudioStartHome) -> Liste der Rubriken via api-Call,
# 2. Aufruf (Rubrik-Webseite in path) -> Audio_get_cluster_rubrik 
#		(Cluster -> Dict) -> Audio_get_cluster_single 
# 02.11.2024 den api-Daten fehlt coreId mit neuem ARD-Pfad  (Schema
#	../urn:ard:page:../.. In den Web-json-Daten ist coreId vorh.
#
def Audio_get_rubriken_web(li, title, path, ID, page):
	PLog('Audio_get_rubriken_web: ' + ID)
	CacheTime = 86400												# 24 Std.

	if li  == '':
		li = xbmcgui.ListItem()
		li = home(li,ID='ARD Audiothek')							# Home-Button		

	page = Dict("load", "AudioRubriken", CacheTime=CacheTime)		# editorialCategories laden
	if page == False or page == '':									# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", "AudioRubriken", page)						
	if page == '':	
		msg1 = "Fehler in Audio_get_rubriken_web:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	if ID == "AudioStartHome":										# 1. Liste der Rubriken
		jsonObject = json.loads(page)
		if "graphql" in page:										# 18.02.2022 auch möglich (alte Form)
			Obs = jsonObject["_embedded"]['mt:editorialCategories']
		else:
			Obs = jsonObject["data"]['editorialCategories']["nodes"]# coreId mit neuem Pfad fehlt, s.o.
		PLog(len(Obs))
		base = "https://www.ardaudiothek.de/rubrik/%s/"				# Name im Pfad (z.B. ../wissen/..)  nicht nötig
		# base = "https://www.ardaudiothek.de/redirect/%s"			# HTTP-error 301 vermeiden - s. get_page
		img = R("ard-rubriken.png"); thumb = R(ICON_DIR_FOLDER)
		for ob in Obs:
			oid = ob["id"]
			title = ob["title"]
			href = base % oid			
			
			PLog('10Satz:');
			PLog(title); PLog(oid); PLog(href);
			
			title=py2_encode(title); href=py2_encode(href);	
			fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'ID': 'Audio_get_rubriken_web'}" % (quote(href), 
				quote(title))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_rubrik", \
				fanart=img, thumb=thumb, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# 21.02.2022 Anpassung an renovierte Audiothek
# 	einschl.Event Streams, Ausgliederung AudioSenderPrograms
# 2. Durchlauf mit sender -> PlayAudio
# Auswertung Sender-Programme s. AudioSenderPrograms
# 06.05.2024 Erweiterung Download Senderlinks als einzelne Playlist
#
def AudioStartLive(title, sender='', streamUrl='', myhome='', img='', Plot=''): # Sender / Livestreams 
	PLog('AudioStartLive: ' + sender)
	CacheTime = 3600													# 1 Std.

	li = xbmcgui.ListItem()
	if myhome:
		li = home(li, ID=myhome)
	else:	
		li = home(li, ID='ARD Audiothek')								# Home-Button

	path = "https://api.ardaudiothek.de/organizations"					# api=Webjson				
	page = Dict("load", "AudioSender", CacheTime=CacheTime)
	if page == False or page == '':										# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", "AudioSender", page)
	msg1 = "Fehler in AudioStartLive:"
	if page == '':	
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li

	LiveObjekts = blockextract('"organizationName"', page)				# Station: Livestreams + programSets
	PLog(len(LiveObjekts))
	streamList=[]
	now = datetime.datetime.now()										# für streamList
	timemark = now.strftime("%d.%m.%Y")
	
	# RadioPlaylist mit play_lines, play_line: m3u-Template
	PlayList = ["#EXTM3U"]											
	play_line = '#EXTINF:-1 logo="%s" group-title="ARD_Radio", %s\n%s'													
	
	if sender == '':
		for LiveObj in LiveObjekts:
			liveStreams = stringextract('liveStreams":', 'programSets', LiveObj)
			live_cnt = stringextract('numberOfElements":', ',', liveStreams)
			streamUrl = stringextract('"streamUrl":"', '"', liveStreams)
			if live_cnt == '0':		
				continue
				
			img = stringextract('"image"', '"url1X1"', LiveObj)			# 18.02.2022 neues Format:
			img = stringextract('"url":"', '"', img)	
			img = img.replace('{width}', '640')							# fehlt manchmal
			Plot = stringextract('"synopsis":"', '"', LiveObj)
			Plot = repl_json_chars(py2_decode(Plot))
					
			title = stringextract('"sender":"', '"', liveStreams)		# Sender, z.B BAYERN 1	
			sender = title
			
			add = "zum Livestream"
			tag = "Weiter %s von: [B]%s[/B]" % (add, title)		
															
			PLog('3Satz:');
			PLog(title); PLog(img); PLog(streamUrl); PLog(Plot);
			title=py2_encode(title); sender=py2_encode(sender);
			streamUrl=py2_encode(streamUrl); img=py2_encode(img)
			Plot=py2_encode(Plot)
			fparams="&fparams={'title': '%s', 'sender': '%s', 'streamUrl': '%s', 'myhome': '%s', 'img': '%s', 'Plot': '%s'}" %\
				(quote(title), quote(sender), quote(streamUrl), myhome, quote(img), quote(Plot))	
			addDir(li=li, label=sender, action="dirList", dirID="AudioStartLive", fanart=img, 
				thumb=img, tagline=tag, summary=Plot, fparams=fparams)
			
			# Streamlinks: "Dateiname ** Titel Zeitmarke ** Streamlink" -> DownloadText
			fname = make_filenames(title)
			fname = py2_encode(fname)
			streamList.append("%s.m3u**# %s | ARDundZDF %s**%s" % (fname,title, timemark, streamUrl))
			
			# play_line = '#EXTINF:-1 logo="%s" group-title="ARD_Radio", %s\n%s'													
			extinf = play_line % (img, title, streamUrl)
			PlayList.append(extinf)

		streamList = py2_encode(streamList)								# Streamlist-Button
		textKey  = "RadioStreamLinks"
		Dict("store", textKey, streamList)				
		lable = u"[B]Download 1: Streamlinks (Anzahl: %d)[/B] als m3u-Dateien" % len(streamList)
		tag = u"Ablage als einzelne m3u-Datei je Streamlink im Downloadverzeichnis"
		summ = u"die nachfolgenden Audio-Buttons bleiben beim Download unberücksichtigt."
		fparams="&fparams={'textKey': '%s'}" % textKey
		addDir(li=li, label=lable, action="dirList", dirID="DownloadText", fanart=R(ICON_DOWNL), 
			thumb=R(ICON_DOWNL), fparams=fparams, tagline=tag, summary=summ)

		PlayList = py2_encode(PlayList)									# RadioPlaylist-Button
		textKey  = "RadioPlaylist"
		Dict("store", textKey, PlayList)				
		lable = u"[B]Download 2: Streamlinks (Anzahl: %d)[/B] als Playlist" % len(PlayList)
		tag = u"Ablage als <Playlist.m3u> im Downloadverzeichnis.\nDie Verwendung als [B]Kodi-Playlist[/B]"
		tag = u"%s im Verzeichnis ../.kodi/userdata/playlists ist möglich." % tag
		summ = u"die nachfolgenden Audio-Buttons bleiben beim Download unberücksichtigt."
		fparams="&fparams={'textKey': '%s'}" % textKey
		addDir(li=li, label=lable, action="dirList", dirID="DownloadText", fanart=R(ICON_DOWNL), 
			thumb=R(ICON_DOWNL), fparams=fparams, tagline=tag, summary=summ)
		
		ARDAudioEventStreams(li)										# externe Zusätze listen

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	#-------------------------------------------------------------------
	
	else:																# 2. Durchlauf: einz. Sender
		if streamUrl:													# zum Livestream
			PlayAudio(streamUrl, title, img, Plot)  # direkt	
	return
			
#----------------------------------------------------------------
# 21.02.2022 Anpassung an renovierte Audiothek
# 14.07.2022 
# 1. Lauf Einzelsender, 2. Lauf Sendungen
# Auswertung Livestreams der Sender s. AudioStartLive
#
def AudioSenderPrograms(org=''): 
	PLog('AudioSenderPrograms:')
	PLog(org); 
	CacheTime = 60*5													# 5 min.				

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')									# Home-Button

	path = "https://api.ardaudiothek.de/organizations"					# api=Webjson		
	page = Dict("load", "AudioSender", CacheTime=CacheTime)
	if page == False or page == '':										# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", "AudioSender", page)
	msg1 = "Fehler in AudioStartLive:"
	if page == '':	
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	LiveObjekts = blockextract('"brandingColor"', page)				# Station: Livestreams + programSets
	PLog(len(LiveObjekts))

	#---------------------------------
	if org == '':														# 1. Durchlauf: alle Einzelsender listen
		PLog("stage1:")
		for LiveObj in LiveObjekts:
			PLog(LiveObj[:80])
			liveStreams = stringextract('liveStreams":', 'programSets', LiveObj)
				
			live_cnt = stringextract('numberOfElements":', ',', liveStreams)
			title = stringextract('"sender":"', '"', liveStreams)		# Sender, z.B BAYERN 1
			if live_cnt == '0':											# ARD, funk
				title = stringextract('"organizationName":"', '"', LiveObj)
				synop = stringextract('"synopsis":"', '"', LiveObj)
				synop = synop.replace("\\n", "")
				if synop:
					title = "%s: %s" % (title, synop[:70])
				
			img = stringextract('"image"', '"url1X1"', LiveObj)			# 18.02.2022 neues Format:
			img = stringextract('"url":"', '"', img)	
			img = img.replace('{width}', '640')							# fehlt manchmal
			tag = "Weiter zu den Sendungen  von %s" % title 
				
			PLog("Sendername: " + org)									# org z.B. BAYERN 1 Franken
			title=py2_encode(title)
			fparams="&fparams={'org': '%s'}" % (quote(title))	
			addDir(li=li, label=title, action="dirList", dirID="AudioSenderPrograms", fanart=img, 
				thumb=img, tagline=tag, fparams=fparams)
				
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

	#---------------------------------
	
	if org:															# 2. Durchlauf: programSets listen	
		PLog("stage2: " + org)
		for LiveObj in LiveObjekts:			
			PLog(LiveObj[:80])
			liveStreams = stringextract('liveStreams":', 'programSets', LiveObj)
				
			live_cnt = stringextract('numberOfElements":', ',', liveStreams)
			title = stringextract('"sender":"', '"', liveStreams)		# Sender, z.B BAYERN 1
			if live_cnt == '0':											# ARD, funk
				title = stringextract('"organizationName":"', '"', LiveObj)
				synop = stringextract('"synopsis":"', '"', LiveObj)
				if synop:
					title = "%s: %s" % (title, synop[:70])
			PLog(org); PLog(title);	
			PLog(title.find(org))
			if title.startswith(org):
				PLog("found_org: %s, title: %s" % (org, title))
				break			

		pos = LiveObj.find('"programSets"')
		page = LiveObj[pos:]
		page= page.replace('\\"', '*')	
		PLog(page[:80])	
		items = blockextract('"id":', page)								# 2. Block enthält editorialCategories 		
		PLog(len(items))
		cnt=0
		for item in items:
			cat =  stringextract('"title":"', '"', item)				# 19.01.2023 Kategorie wieder im 1. Block
			cnt=cnt+1													#	statt im früheren 2. (fehlt jetzt)
			
			web_url =  stringextract('"sharingUrl":"', '"', item)		
			PLog("web_url: " + web_url)
			href_add = "?offset=0&limit=20"								# Liste der Sendungen aufsteigend sortiert
			if web_url.endswith("/"):
				url_id 	= web_url.split('/')[-2]
			else:
				url_id 	= web_url.split('/')[-1]
			api_url = ARD_AUDIO_BASE + "programsets/%s/%s" % (url_id, href_add)
			
			title = stringextract('"title":"', '"', item)				# PRG, z.B. Blaue Couch
			anz =  stringextract('"numberOfElements":', ',', item)
			if anz == '':
				continue

			img = stringextract('"image"', '"url1X1"', item)			# 18.02.2022 neues Format
			img = stringextract('"url":"', '"', item)	
			img = img.replace('{width}', '640')
			
			
			PLog("prg: %s, url_id: %s" % (title, url_id))
			tag = u"Folgeseiten | Anzahl: %s\nKategorie [B]%s[/B]" % (anz, cat) 
			summ = u"zu den einzelnen Beiträgen:\n%s" % title 
			
			api_url=py2_encode(api_url); title=py2_encode(title)
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(api_url), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung_api", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)						
	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	


#----------------------------------------------------------------
# neu ab 26.08.2023
# Button ARD Audio Event Streams -> ARDSportAudioXML -> SenderLiveListe
#	(Audio-channels in livesenderTV.xml
# Button Sport in der Audiothek -> Audio_get_cluster_rubrik
#	(Audiothek, Rubrik LIVE: 1. und 2. Bundesliga)
# restl. Buttons -> ARDSportNetcastAudios (Audio-Livestreams auf
#	sportschau.de, WDR -> ARDSportMediaPlayer extrahiert die eingebetteten
#	Mediaplayerdaten)
#
def ARDAudioEventStreams(li=''):
	PLog('ARDAudioEventStreams:')
	endof=False
	if li == '':														# Aufruf ARDSportWDR (ARDnew)
		endof = True
		li = xbmcgui.ListItem()
		
	channel = u'ARD Audio Event Streams'								# aus livesenderTV.xml								
	title = u"[B]Audio:[/B] ARD Radio Event Streams"					# div. Events, z.Z. Fußball EM2020   
	img = R("radio-livestreams.png")
	tag = u'Reportagen von regionalen und überregionalen Events' 
	summ = u"Quelle: Channel >ARD Audio Event Streams< in livesenderTV.xml"
	img=py2_encode(img); channel=py2_encode(channel); title=py2_encode(title);
	fparams="&fparams={'channel': '%s'}"	% (quote(channel))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioXML", fanart=img, 
		thumb=img, tagline=tag, summary=summ, fparams=fparams)
		
	label = "[B]Audio:[/B] Sport in der Audiothek"					# Querverweis Audiothek Rubrik Sport
	li = xbmcgui.ListItem()
	tag = u"LIVE: 1. und 2. Bundesliga, einschl. Bundesliga-Konferenz, Aktuell informiert und weitere Themen"
	summ = u"Quelle: Rubrik sport/42914734 in der ARD Audiothek"
	thumb = R("ard-sport.png")
	img = R(ICON_MAIN_AUDIO)
	href = 'https://www.ardaudiothek.de/rubrik/sport/42914734'
	href=py2_encode(href);
	fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'ID': 'Audio_get_rubriken_web'}" % (quote(href), 
		quote("Sport"))
	addDir(li=li, label=label, action="dirList", dirID="Audio_get_cluster_rubrik", \
		fanart=img, thumb=thumb, tagline=tag, summary=summ, fparams=fparams)	
	 	
	# Startseite für Audiostreams: https://www.sportschau.de/fussball/how-to-audio-netcast-100.html				
	title = u"[B]Audio:[/B] Alle Audiostreams der Fußball-Bundesliga"	# Button Audiostreams sportschau.de
	href = 'https://www.sportschau.de/fussball/bundesliga/audiostreams-bundesliga-uebersicht-100.html'
	img = R("tv-ard-sportschau.png")
	thumb =	"https://images.sportschau.de/image/14367dff-c9b4-4237-8421-6a9c0e01d61e/AAABiYhYFh4/AAABibBxqrQ/16x9-1280/buli-audio-netcast-teaser-100.jpg"						
	tag = u'Fußball-Bundesliga live hören.\nQuelle: ARD sportschau.de (WDR)' 
	summ = u"Quelle: sportschau.de (WDR)"
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s', 'cacheID': 'ARDSport_Audios_BL1'}" %\
		(quote(title), quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportNetcastAudios", fanart=img, 
		thumb=thumb, tagline=tag, summary=summ, fparams=fparams)

	title = u"[B]Audio:[/B] Alle Audiostreams der 2. Fußball-Bundesliga"# Button Audiostreams sportschau.de
	href = 'https://www.sportschau.de/fussball/bundesliga2/audiostreams-zweite-bundesliga-uebersicht-100.html'
	img = R("tv-ard-sportschau.png")
	thumb =	"https://images.sportschau.de/image/14367dff-c9b4-4237-8421-6a9c0e01d61e/AAABiYhYFh4/AAABibBxqrQ/16x9-1280/buli-audio-netcast-teaser-100.jpg"						
	tag = u'2. Bundesliga live hören.\nQuelle: ARD sportschau.de (WDR)' 
	summ = u"Quelle: sportschau.de (WDR)"
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s', 'cacheID': 'ARDSport_Audios_BL2'}" %\
		(quote(title), quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportNetcastAudios", fanart=img, 
		thumb=thumb, tagline=tag, summary=summ, fparams=fparams)
	
	title = u"[B]Audio:[/B] Live hören: Alle Spiele im DFB Pokal"		# Button Audiostreams sportschau.de
	href = 'https://www.sportschau.de/fussball/dfbpokal/audiostreams-dfb-pokal-uebersicht-100.html'
	img = R("tv-ard-sportschau.png")
	thumb =	"https://images.sportschau.de/image/5b48b637-8cc1-4228-8504-861eeb0358af/AAABiqiJb4U/AAABibBxqrQ/16x9-1280/dfb-pokal-audio-netcast-teaser-100.jpg"						
	tag = u'DFB-Pokal live aus den Stadien: Bei der Sportschau hören Sie jedes Einzelspiel in voller Länge.' 
	summ = u"Quelle: sportschau.de (WDR)"
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s', 'cacheID': 'ARDSport_DFBPokal'}" %\
		(quote(title), quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportNetcastAudios", fanart=img, 
		thumb=thumb, tagline=tag, summary=summ, fparams=fparams)
	
	title = u"[B]Audio:[/B] Alle Audiostreams aus der Champions League"# Button Audiostreams sportschau.de
	href = 'https://www.sportschau.de/fussball/championsleague/audiostreams-champions-league-uebersicht-100.html'
	img = R("tv-ard-sportschau.png")
	thumb =	"https://images.sportschau.de/image/c99df197-9b30-4af0-9a84-3cc3e1ec991a/AAABiqiMH6k/AAABibBxqrQ/16x9-1280/cl-audio-netcast-teaser-100.jpg"						
	tag = u'Champions League live hören.\nQuelle: ARD sportschau.de (WDR)' 
	summ = u"Quelle: sportschau.de (WDR)"
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s', 'cacheID': 'ARDSport_Audios_CLeague'}" %\
		(quote(title), quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportNetcastAudios", fanart=img, 
		thumb=thumb, tagline=tag, summary=summ, fparams=fparams)
		
	title = u"[B]Audio-Livestreams auf sportschau.de[/B]"				# ARDSportLive filtert Videos heraus
	tag = u"kommende Events: Ankündigungen mit Direktlinks"
	summ = u"Quelle: www.sportschau.de/streams"
	img = R("tv-ard-sportschau.png")
	title=py2_encode(title)
	fparams="&fparams={'title': '%s', 'skip_video': 'True'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="ARDSportLive", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	


	if endof:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:	
		return

#----------------------------------------------------------------
# gibt entw. den  HTML- oder den json-Teil der Webseite zurück
# HTML-Inhalt genutzt für Cluster-Liste.
# json-Inhalt weicht für einige Objekte von api-json-Inhalt ab
# 16.01.2023 json-Extraktion wie get_ArtePage
def Audio_get_webslice(page, mode="web"):
	PLog('Audio_get_webslice:')
	
	if mode == "web":
		pos1 = page.find('</head><body')
		pos2 = page.find('{"props"')
		page = page[pos1:pos2]
	if mode == "json":							# wie get_ArtePage
		mark1 = '{"pageProps'; mark2 = '__N_SSP":true}'		
		pos1 = page.find(mark1)
		pos2 = page.find(mark2)
		PLog(pos1); PLog(pos2)
		if pos1 < 0 and pos2 < 0:
			PLog("json-Daten fehlen")
			page=''								# ohne json-Bereich: leere Seite
		page = page[pos1:pos2+len(mark2)]	
	
	PLog(page[:80])
	PLog(len(page))
	return page
				
#----------------------------------------------------------------
# 28.10.2024 Podcasts podcast.de
# Doku: ../Audiothek/Podcast.de
#
def AudioPodcastDe(title="", Dict_ID=''):
	PLog('AudioPodcastDe: ' + Dict_ID)
	path = "https://www.podcast.de/"
	CacheTime = 3600		# 1 Std.
	WebID = "AudioPodcastDe"
	
	page = Dict("load", WebID, CacheTime=CacheTime)	
	if page == False or page == '':									# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		icon = R('podcast-de.png')
		xbmcgui.Dialog().notification("Cache podcast.de:","Haltedauer 1 Stunde",icon,3000,sound=False)
		Dict("store", "AudioPodcastDe", page)						
	if page == '':	
		msg1 = "Fehler in AudioPodcastDe:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	PLog(len(page))
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')

	# umfangreichere json-Daten (Autor, Mail, CR,..) nur bei lchannels=" 
	#	und lshows=" - hier nicht benötigt:
	json_blocks = stringextract("Scripts -->", "</script>", page)
	PLog("json_blocks: " + json_blocks[:80])
	
	rubrics = [u"editors_choice|Tipps der Redaktion", u"dashboard_charts|Podcast-Charts",
				u"latest_shows|Neue Episoden", u"latest_channels|Neue Podcasts" 
			]
	editors_choice 	= stringextract("editors_choice = [", "]", json_blocks)
	dashboard_charts= stringextract("dashboard_charts = [", "]", json_blocks)
	latest_shows 	= stringextract("latest_shows = [", "]", json_blocks)
	latest_channels = stringextract("latest_channels = [", "]", json_blocks)
	
	#----------------------------------------------------------------	# 1. json-Blöcke aus Webseite laden  
	if Dict_ID == '':
		PLog("Step1:")
		title="Suche auf podcast.de"
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSearch", 
			fanart=R('podcast-de.png'), thumb=R('ard-suche.png'), fparams=fparams)	
		
		for rubric in rubrics:
			Dict_ID, label = rubric.split("|")
			mark1="%s = [" % Dict_ID
			mark2="]"
			pos1 = json_blocks.find(mark1)
			if mark1 in json_blocks:
				block = stringextract(mark1, mark2, json_blocks[pos1:])
				block = block.strip()
				Dict("store", Dict_ID, block)				
				anz = block.count('"url":')
				tag = "Podcasts: [B]%d[/B]" % anz
				PLog("Dict_ID: %s, anz: %d, %s" % (Dict_ID, anz, block[:80]))
				
				fparams="&fparams={'title': '%s', 'Dict_ID': '%s'}" % (title, Dict_ID)
				addDir(li=li, label=label, action="dirList", dirID="AudioPodcastDe", fanart=R('podcast-de.png'), 
					thumb=R(ICON_DIR_FOLDER), fparams=fparams, tagline=tag)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:		
	#----------------------------------------------------------------	# 2. mp3's
		PLog("Step2:")
		block = Dict("load", Dict_ID)
		block = transl_json(block)									# Format ungeeignet für json.loads 
		PLog(block[:100])
		block = (block.replace(u"&quot;", '').replace(u"\\", '').replace(u"u0027", '')\
				.replace(u"&amp;", '&'))
		
		items = blockextract('"name":', block)
		for item in items:
			title = stringextract('"name": "', '",', item)
			title=title.replace("#", "*")							# z.B.: #544 Für wen..
			artist = stringextract('"artist": "', '",', item)		# Podcast-Reihe
			Plot = "Podcast-Reihe: [B]%s[/B]" % artist
			url = stringextract('"url": "', '",', item)
			url = decode_url(url)									# AudioPlayMP3 -> entf. Url-Suffix ?source=feed
			
			anz = stringextract('"subscribers": "', '",', item)
			img = stringextract('"cover_art_url": "', '"', item)
			img=img.replace("/33/", "/600/"); img=img.replace("/55/", "/600/")
			img=img.replace("/66/", "/600/"); img=img.replace("/100/", "/600/"); 
			summ = "Weiter zu dieser Folge und zur Podcast-Reihe."
		  
			PLog("Step2_title: %s, artist: %s, url: %s, anz: %s, img: %s," % (title, Plot, url, anz, img))		  
			title=py2_encode(title); url=py2_encode(url);
			img=py2_encode(img); Plot=py2_encode(Plot);	
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'artist': '%s'}" %\
				(quote(url), quote(title), quote(img), quote(Plot), quote(artist))
			addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSingle", fanart=img, thumb=img, 
				fparams=fparams, tagline=Plot, summary=summ)			
	  
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# Suche auf podcast.de
# Step 1: Suche, Step 2: mit dest_url zur neuesten Episode
# query: Nutzung durch AudioPodcastDeSingle für Suche nach Podcast-Reihe
# 15.11.2024 next_url: nächste Web-Seite Suchergebnisse
#
def AudioPodcastDeSearch(dest_url="", query="", next_url=""):
	PLog('AudioPodcastDeSearch: ')
	PLog(dest_url); PLog(query); PLog(next_url); 

	if dest_url == "":												# Step 1: Suche
		PLog("Step1")
		base = "https://www.podcast.de/suche?query=%s"
		if next_url:												# nächste Web-Seite Suchergebnisse
			path = next_url
		else:
			if query == "":
				query = get_query(channel='ARD Audiothek')
				if  query == None or query.strip() == '':
					return ""
				query = py2_encode(query)							# encode für quote
				path = base % quote(query)
		
		page, msg = get_page(path, do_safe=False)					# nach quote ohne do_safe 	
		if page == '' or page.find("<title>Server Error</title>") > 0 or page.find("<h5>") < 0:	
			PLog("msg: " + msg)
			msg1 = "AudioPodcastDeSearch:"
			msg2 = "Suche leider fehlgeschlagen."
			MyDialog(msg1, msg2, '')	
			return
		WebID = "AudioPodcastDeSearch"
		Dict("store", WebID, page)
			
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD Audiothek')						# Home-Button

		items = blockextract("<h5>", page)
		for item in items:
			artist = stringextract('<h5>', '</h5>', item)		# Podcast-Reihe
			artist = cleanhtml(artist); artist = artist.strip()
			img = stringextract('img src="', '"', item)
			img=img.replace("/33/", "/600/"); img=img.replace("/55/", "/600/")
			img=img.replace("/66/", "/600/"); img=img.replace("/100/", "/600/"); 
			alt = stringextract('alt="', '"', item)
			alt = unescape(alt)									# alt="LANZ &amp; PRECHT"
			Plot = stringextract('text-muted small">', '<br>', item)
			Plot = unescape(Plot); Plot = cleanhtml(Plot); 
			Plot = mystrip(Plot)
			
			href = stringextract('Neueste Episode:', '</span>', item)
			title = cleanhtml(href); title = mystrip(title); 
			title = unescape(title); title=title.replace("#", "*")
			title = "%s: [B]%s[/B]" % (alt, title)
			dest_url = stringextract('href="', '"', href)		# podcast.de/episode/644335688/ausgabe-..
			if dest_url == "":									# Abschnitte Service, Dienst, ..
				continue

			PLog("dest_url: %s, img: %s, title: %s, Plot: %s" % (dest_url, img, title, Plot[:80]))
			title=py2_encode(title); dest_url=py2_encode(dest_url);
			img=py2_encode(img); Plot=py2_encode(Plot);	
			
			fparams="&fparams={'dest_url': '%s'}" % quote(dest_url) 
			addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSearch", fanart=img, thumb=img, 
				fparams=fparams, tagline=Plot)
		
		pages  = blockextract('<li class="page-item">', page, "</li>")	# Pagination? (ungleich AudioPodcastDeArchiv)	
		for p in pages:
			if "pagination.next" in p:									# keine Liste, nur nächste Seite
				next_url = stringextract('href="', '"', p)
				next_url = decode_url(next_url)
				nr = re.search(r'page=(\d+)', next_url).group(1)
				query = re.search(r'query=(.*?)&page', next_url).group(1)
				PLog("next_url: %s, query: %s" % (next_url, query))
				title = "Weiter zu Seite %s" % nr
				tag = "Mehr zur Suche nach: [B]%s[/B]" % query
				
				next_url=py2_encode(next_url)
				fparams="&fparams={'next_url': '%s'}" % quote(next_url)
				addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSearch", \
					fanart=R('podcast-de.png'), thumb=R(ICON_MEHR), tagline=tag, fparams=fparams)			
				break

	else:
	#----------------------------------------------------------------	# Step 2: -> neueste Episode -> Archiv
		PLog("Step2")
		page, msg = get_page(path=dest_url)	
		if page == '' or page.find(">Server Error</") > 0 or page.find(">Nichts gefunden.</") > 0:		
			msg1 = "AudioPodcastDeSearch: Seite nicht gefunden."
			MyDialog(msg1, msg, '')	
			return

		li = xbmcgui.ListItem()
		li = home(li, ID='ARD Audiothek')						# Home-Button
			
		script = stringextract('application/ld+json">', '</script>', page)
		script = script.replace("\n"," ")								# sonst JSONDecodeError
		try:
			items = json.loads(script)
			PLog(str(items)[:80])
			title = items["name"]
			title = title.replace("#", "*")
			Plot = items["description"]
			Plot_org=Plot
			Plot = Plot.replace("\n", "")
			img = items["thumbnailUrl"]
			img=img.replace("/33/", "/600/"); img=img.replace("/55/", "/600/")
			img=img.replace("/66/", "/600/"); img=img.replace("/100/", "/600/"); 
			
			mp3_url = items["associatedMedia"]["contentUrl"]
			ser_url = items["partOfSeries"]["url"]						# Serien-Url
			serie = ser_url.split("/")[-1]								# z.B. lanz-precht
			archiv_url = ser_url.replace(serie, "archiv?page=1")
			PLog("archiv_url: " + archiv_url)
		except Exception as exception:
			msg = "items_error: " + str(exception)
			PLog(msg)
			msg1 = "Fehler in AudioPodcastDeSearch:"
			MyDialog(msg1, msg, '')	
			return
				
		summ = "Weiter zu diesem Podcast"
		if SETTINGS.getSetting('pref_video_direct') == 'false': 
			summ = "%s und zum Download" % summ
																	# 1. Button Neueste Episode
		PLog("title_Step2: %s, artist: %s, url: %s, img: %s," % (title, Plot, mp3_url, img))		  
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); Plot=py2_encode(Plot);	
		
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
			fparams=fparams, tagline=Plot, summary=summ)			
		
		AudioPodcastDeArchiv(archiv_url, li)							# Buttons Archiv-Beiträge

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# Buttons Archiv-Podcasts für AudioPodcastDeSearch
#
def AudioPodcastDeArchiv(url, li=""):	
	PLog('AudioPodcastDeArchiv: ' + url)
	url_org=url
	
	page, msg = get_page(path=url)	
	if page == '':	
		msg1 = "Fehler in AudioPodcastDeArchiv:"
		MyDialog(msg1, msg, '')	
		return

	if li == "":												# Mehr-Seiten
		li = xbmcgui.ListItem()	
		li = home(li, ID='ARD Audiothek')						# Home-Button
	
	folgen = page.split('episode-list">')[-1]					# <div class="episode-list">
	folgen = folgen.split('<div class="row">')[0]
	pages  = page.split('pagination">')[-1]
	
	items = blockextract('position-relative">', folgen)
	del items[0]											# Neueste Episode löschen
	for item in items:
		href = stringextract('href="', '"', item)			# Web-Ziel
		img = stringextract('img src="', '"', item)
		img=img.replace("/33/", "/600/"); img=img.replace("/55/", "/600/")
		img=img.replace("/66/", "/600/"); img=img.replace("/100/", "/600/"); 
		
		title = stringextract('<h3>', '</h3>', item)
		title=title.strip(); title=unescape(title)
		title=repl_json_chars(title)
		
		Plot = stringextract('text-muted">', '</small>', item)
		Plot = Plot.strip()
		summ = "Weiter zu diesem Podcast"
		if SETTINGS.getSetting('pref_video_direct') == 'false': 
			summ = "%s und zum Download" % summ
		
		PLog("archiv_title: %s, mp3_url: %s, img: %s, Plot: %s" % (title, href, img, Plot))		  
		title=py2_encode(title); href=py2_encode(href);
		img=py2_encode(img); Plot=py2_encode(Plot);	
		
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
			(quote(href), quote(title), quote(img), quote_plus(Plot), )
		addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSingle", fanart=img, thumb=img, 
			fparams=fparams, tagline=Plot, summary=summ)			

	if pages:												# Pagination
		p = url_org.split("/")[-1]		# ?page=1
		nr = re.search(r'page=(\d+)', p).group(1)
		new_nr = int(nr)+1
		next_page = "archiv?page=%d" % new_nr
		nexturl = url_org.replace(p, next_page)
		PLog("url_org: %s, nexturl: %s" % (url_org, nexturl))
		title = "Weiter zu Seite %d" % new_nr
		PLog(pages.find(nexturl))
		if pages.find(nexturl) > 0:
			nexturl=py2_encode(nexturl)
			fparams="&fparams={'url': '%s'}" % quote(nexturl)
			addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeArchiv", \
				fanart=R('podcast-de.png'), thumb=R(ICON_MEHR), fparams=fparams)			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# Aufrufer: 1. AudioPodcastDeArchiv -> Webseite mit Einzelbeitrag
#			2. AudioPodcastDe -> einz. mp3-Url plus Podcast-Reihe (artist)
#
def AudioPodcastDeSingle(url, title, thumb, Plot, artist=""):	
	PLog('AudioPodcastDeSingle: ' + url)
	PLog("artist: " + artist)
	PLog("title: " + title)

	if artist:														# einz. mp3-Url plus Podcast-Reihe
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD Audiothek')	# Home-Button
		
		tag = "Weiter zum Podcast"									# Button -> Podcast
		clen = get_content_length(url)								# Größe aus Header ermitteln
		if clen:
			vsize = u"(Größe [B]%s[/B])." % humanbytes(clen)
		else:
			vsize = u"(Größe unbekannt)"
		tag = "%s %s" % (tag, vsize)
		summ = Plot
		mp3_url = url; img = thumb
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); Plot=py2_encode(Plot);	
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(img), quote(Plot))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)
		
		title = "Zur Podcast-Reihe [B]%s[/B]" % artist				# Button -> Podcast-Reihe
		tag = "%s und verwandten Themen" % title
		fparams="&fparams={'query': '%s'}" % artist
		addDir(li=li, label=title, action="dirList", dirID="AudioPodcastDeSearch", 
			fanart=R('podcast-de.png'), thumb=R('ard-suche.png'), tagline=tag, fparams=fparams)
	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return
				
	# -----------------------------									# Webseite mit Einzelbeitrag 
	page, msg = get_page(path=url)	
	if page == '' or page.find(">Server Error</") > 0 or page.find(">Nichts gefunden.</") > 0:		
		msg1 = "AudioPodcastDeSingle: Seite nicht gefunden."
		MyDialog(msg1, msg, '')	
		return
		
	script = stringextract('application/ld+json">', '</script>', page)
	script = script.replace("\n"," ")								# JSONDecodeError
	try:
		items = json.loads(script)
		title = items["name"]
		title = repl_json_chars(title)
		Plot = items["description"]
		Plot = Plot.replace("\n", "")
		Plot = repl_json_chars(Plot)
		img = items["thumbnailUrl"]
		img=img.replace("/33/", "/600/"); img=img.replace("/55/", "/600/")
		img=img.replace("/66/", "/600/"); img=img.replace("/100/", "/600/"); 
		mp3_url = items["associatedMedia"]["contentUrl"]
		ser_url = items["partOfSeries"]["url"]						# Serien-Url
		serie = ser_url.split("/")[-1]								# z.B. lanz-precht
		archiv_url = ser_url.replace(serie, "archiv?page=1")
		PLog("archiv_url: " + archiv_url)
	except Exception as exception:
		msg = "items_error: " + str(exception)
		PLog(msg)
		msg1 = "Fehler in AudioPodcastDeSingle:"
		MyDialog(msg1, msg, '')	
		return
	
	li = xbmcgui.ListItem()
	if SETTINGS.getSetting('pref_video_direct') == 'true':  		# Sofortstart
		PLog('Sofortstart: AudioPodcastDeSingle')
		AudioPlayMP3(mp3_url, title, thumb, Plot)
		return
	else:
		clen = get_content_length(url)								# Größe aus Header ermitteln
		if clen:
			vsize = u"(Größe [B]%s[/B])." % humanbytes(clen)
		else:
			vsize = u"(Größe unbekannt)"
		tag = "[B]Weiter zum Podcast und Download[/B] %s" % vsize
		li = home(li, ID='ARD Audiothek')				# Home-Button
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); Plot=py2_encode(Plot);	
	
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(img), quote(Plot))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=Plot)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)			

#----------------------------------------------------------------
# extrahiert Einzelbeiträge einer Sendung
# Aufrufer: AudioSenderPrograms + Audio_get_sendung_api (Fallback
#	bei page mit fehlenden durations), Audio_get_cluster_single,
#	Audio_get_homescreen
# 18.02.2022 Anpassung an ARD-Änderungen
#	Web-Url -> AudioWebMP3, next-Url nicht mehr enthalten
# Nutzung Audio_get_items_single  + Audio_get_nexturl wie 
#	Audio_get_sendung_api
# Sammel-Downloads: Liste enthält je nach Quelle mp3_url oder web_url
#	(Auswertung web_url via DownloadMultiple -> AudioWebMP3)
#
def Audio_get_sendung(url, title, page=''):	
	PLog('Audio_get_sendung: ' + title)
	url_org=url; title_org=title

	title_org = title; url_org = url
	PLog(url);  
	base = "https://api.ardaudiothek.de/"
				
	li = xbmcgui.ListItem()
	ID = 'ARD Audiothek'
	li = home(li, ID)				# Home-Button
		
	if page == '':					# Fallback Audio_get_sendung_api?
		page, msg = get_page(path=url, GetOnlyRedirect=True)
		path = page								
		if "//api" in path:
			path = path + "&order=descending"
		page, msg = get_page(path)	
		if page == '':
			msg1 = "Fehler in Audio_get_sendung:"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
	
	if page.startswith('<!DOCTYPE html>'):
		page = Audio_get_webslice(page, mode="json")				# json ausschneiden
	elements = stringextract('"numberOfElements":', ',', page)		# für Mehr anzeigen 
	PLog("elements: %s" % elements)
		
	pos = page.find("nodes")
	PLog(pos)
	if pos > 0:
		page = page[pos:]
		
	page = page.replace('\\"', '*')
	items = blockextract('"id":', page, '}]},{')					# bis nächste "id" (nicht trennsicher)
	PLog(len(items))
	
	PLog("Mark0")
	cnt=0; dl_cnt=0; downl_list=[]; skip_list=[]
	for item in items:		
		mp3_url=''; web_url=''
		if item.find("publishDate") < 0 and  item.find("publicationStart") < 0:
			continue
		mp3_url, web_url, attr, img, dur, title, summ, source, sender, pubDate = Audio_get_items_single(item)		
		if title in skip_list:										# mögl. bei programsets mit Einzelbeiträgen
			continue
		skip_list.append(title)
		
		tag = "Dauer %s" % dur
		if pubDate:
			tag = "%s | Datum %s" %  (tag, pubDate)
		if sender:
			tag = "%s | Sender %s\n[B]%s[/B]" % (tag, sender, attr)
		summ_par = summ
		
		PLog('5Satz:');
		PLog(title); PLog(tag); PLog(summ[:80]); PLog(mp3_url); PLog(web_url);
		title=py2_encode(title); web_url=py2_encode(web_url); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	
		
		if mp3_url:
			downl_list.append("%s#%s" % (title, mp3_url))
			summ_par = "%s\n\n%s" % (tag, summ)
			summ_par = summ_par.replace('\n', '||')
			summ_par=py2_encode(summ_par)
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)			
		else:
			downl_list.append("%s#%s" % (title, web_url))
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': ''}" % (quote(web_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioWebMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)	
		cnt=cnt+1

	PLog("cnt: %d" % cnt)
	if cnt  == 0:
		msg1 = u'nichts gefunden'
		msg2 = title_org
		icon = R(ICON_MAIN_AUDIO)		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("%s: %s" % (msg1, msg2))
		return
		
	if elements and url_org:
		myfunc = "Audio_get_sendung"	
		Audio_get_nexturl(li, url_org, title_org, elements, cnt, myfunc)# Mehr anzeigen
	
	if len(downl_list) > 1:												# Button Sammel-Downloads
		title=u'[B]Download! Alle angezeigten %d Podcasts speichern?[/B]' % cnt
		summ = u'[B]Download[/B] von insgesamt %s Podcasts' % len(downl_list)	
		Dict("store", 'dl_podlist', downl_list) 

		fparams="&fparams={'key': 'dl_podlist'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.DownloadMultiple", 
			fanart=R(ICON_DOWNL), thumb=R(ICON_DOWNL), fparams=fparams, summary=summ)
		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# Aufrufer: AudioSenderPrograms, Audio_get_search_cluster,
#	Audio_get_homescreen (Step 2), Audio_get_cluster_single
# json -> strings (Performance)
# Nutzung Audio_get_items_single + Audio_get_nexturl wie Audio_get_sendung
# Sammel-Downloads: Liste enthält je nach Quelle mp3_url oder web_url
#	(Auswertung web_url via DownloadMultiple -> AudioWebMP3)
#
def Audio_get_sendung_api(url, title, page='', home_id='', ID=''):
	PLog('Audio_get_sendung_api: ' + url)
	PLog(ID)
	url_org=url; title_org=title

	li = xbmcgui.ListItem()

	if page == '':
		page, msg = get_page(path=url+"&order=descending")
	if page == '':	
		msg1 = "Fehler in Audio_get_sendung_api:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	
	if page.find('"duration"') < 0:									# Fallback -> Audio_get_sendung
		PLog("Fallback_Audio_get_sendung")
		Audio_get_sendung(url, title, page)
		return
		
	if home_id:
		li = home(li, home_id)				# Home-Button
	else:
		li = home(li, 'ARD Audiothek')		# Home-Button
	
	page = page.replace('\\"', '*')	
	elements = stringextract('"numberOfElements":', ',', page)		# für Mehr anzeigen
	PLog("elements: %s" % elements)
	items = blockextract('"duration"', page)
	PLog(len(items))
	
	PLog("Mark1")
	cnt=0; dl_cnt=0; downl_list=[]
	for item in items:
		mp3_url, web_url, attr, img, dur, title, summ, source, sender, pubDate = Audio_get_items_single(item, ID)		
			
		tag = "Dauer %s" % dur
		if pubDate:
			tag = "%s | Datum %s" %  (tag, pubDate)
		if sender:
			tag = "%s | Sender %s\n[B]%s[/B]" % (tag, sender, attr)
		summ_par = summ
		
		PLog('7Satz:');
		PLog(tag); PLog(summ[:80]); PLog("icecastssl_url: %d" % mp3_url.find(".icecastssl."))
		title=py2_encode(title); web_url=py2_encode(web_url); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	
			
		if mp3_url:
			if  mp3_url.find(".icecastssl.") < 0:					# Livestreams von Downloads ausschließen
				downl_list.append("%s#%s" % (title, mp3_url))	

			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)			
		else:
			downl_list.append("%s#%s" % (title, web_url))
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': ''}" % (quote(web_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioWebMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)
				
		cnt=cnt+1	

	if cnt  == 0:
		msg1 = u'nichts gefunden'
		msg2 = title_org
		icon = R(ICON_MAIN_AUDIO)		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("" % (msg1, msg2))
		return
	
	if elements and url_org and cnt > 1:
		myfunc = "Audio_get_sendung_api"	
		Audio_get_nexturl(li, url_org, title_org, elements, cnt, myfunc)# Mehr anzeigen (Beiträge > 1)
	
	if len(downl_list) > 1:												# Button Sammel-Downloads
		title=u'[B]Download! Alle angezeigten %d Podcasts speichern[/B]' % cnt
		summ = u'[B]Download[/B] von insgesamt %s Podcasts' % len(downl_list)	
		Dict("store", 'dl_podlist', downl_list) 

		fparams="&fparams={'key': 'dl_podlist'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.DownloadMultiple", 
			fanart=R(ICON_DOWNL), thumb=R(ICON_DOWNL), fparams=fparams, summary=summ)
	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-------------------------
# Mehr-Button für myfunc (Audio_get_sendung, Audio_get_sendung_api) 
# Bsp.: Top-Podcasts ff.
# 
def Audio_get_nexturl(li, url_org, title_org, elements, cnt, myfunc):
	PLog('Audio_get_nexturl:')
	PLog(url_org)
	url=url_org
	
	if elements:														# numberOfElements
		limit=20; offset=0; url_part="";
		if "offset=" in url:
			offset = re.search(r'offset=(\d+)', url).group(1)
			url_part = "offset=%s" % offset
		if "limit=" in url_org:
			re.search(r'limit=(\d+)', url).group(1)
		new_offset = int(offset) + cnt 
		if url_part:													# aktualisiere offset
			new_url_part = "offset=%s" % str(new_offset)
			url = url.replace(url_part, new_url_part)
		PLog("url: " + url)	
		PLog("elements: %s, offset: %s, new_offset: %d, limit: %d" % (elements, offset, new_offset, limit))

		if new_offset < int(elements):
			tag = u"Mehr (ab Beitrag %d von %s)" % (new_offset+1, elements)
			PLog(tag);
			title_org=py2_encode(title_org); url=py2_encode(url);
			fparams="&fparams={'title': '%s', 'url': '%s'}" % (quote(title_org), quote(url))
			addDir(li=li, label=title_org, action="dirList", dirID=myfunc, fanart=R(ICON_MEHR), 
				thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)		
		return
	
#-------------------------
# extrakt json-Rekord für Audio_get_sendung + 
#	Audio_get_sendung_api
# 
def Audio_get_items_single(item, ID=''):
	PLog('Audio_get_items_single:')
	PLog(ID)
	base = "https://www.ardaudiothek.de"
	item = py2_encode(item); base = py2_encode(base)				# PY2
	
	item = item.replace('\\"', '*')
	mp3_url=''; web_url=''; attr=''; img=''; dur=''; title=''; 
	summ=''; source=''; sender=''; pubDate='';
	
	mp3_url = stringextract('"downloadUrl":"', '"', item)			# api-Seiten ev. ohne mp3_url
	if 	mp3_url == '':
		audios = stringextract('"audios":', '}', item)				# Altern.
		mp3_url = stringextract('"url":"', '"', audios)
	if 	mp3_url == '':	
		web_url = stringextract('"sharingUrl":"', '"', item)		# Weblink
	if 	mp3_url == '' and web_url == "":							# neu ab 25.03.2023 (Web-json)
		if '"path":"' in item:
			web_url = base + stringextract('"path":"', '"', item)
		else:
			links = stringextract('"_links":', '},', item)
			href = stringextract('"href":"', '"', links)			#  ./editorialcollections/56087830{?offset,limit}"
			href = href.replace("{?offset,limit}", "")				# hier ohne href_add
			href = href.replace("./", ARD_AUDIO_BASE)
			web_url = href
		if web_url == base:											# falls path leer
			web_url=""	

	attr = stringextract('"attribution":"', '"', item)				# Sender, CR usw.
	if attr:
		attr = "Bild: %s" % repl_json_chars(py2_decode(attr))					# ' möglich

	img = stringextract('"image":', ',', item)
	img = stringextract('"url":"', '"', img)
	img = img.replace('{width}', '640')
	img = img.replace('16x9', '1x1')								# 16x9 kann fehlen, z,B. bei Suche
	img = img.replace(u'\\u0026', '&')								# 13.03.2022: escape-Zeichen mögl.
	if img == "":
		img = R(ICON_DIR_FOLDER)
	

	dur = stringextract('"duration":', ',', item)					# in Sek.
	dur = dur.replace("}", '')										# 3592} statt 3592,
	dur = seconds_translate(dur)
	if "clipTitle" in item:											# Abschnitt "tracking"
		title = stringextract('"clipTitle":"', '"', item)
	else:
		title = stringextract('"title":"', '"', item)
	title = repl_json_chars(py2_decode(title))						# PY2
	summ = stringextract('"synopsis":"', '"', item)
	summ = repl_json_chars(py2_decode(summ))						# PY2
	source = stringextract('"source":"', '"', item)
	sender = stringextract('zationName":"', '"', item)

	pubDate = stringextract('DateAndTime":"', '"', item)			# 2021-11-16T16:12:43+01:00
	if pubDate == '':
		pubDate = stringextract('"publicationDate":"', '"', item)	# 20220120
	if pubDate == '':
		pubDate = stringextract('"publishDate":"', '"', item)		# 2021-05-26T09:26:44+02:00
	if pubDate:
		if len(pubDate) == 25:
			pubDate = "[B]%s.%s.%s, %s:%s[/B]" % (pubDate[8:10],pubDate[5:7],pubDate[0:4],pubDate[11:13],pubDate[14:16])
		if len(pubDate) == 8:			
			pubDate = "[B]%s.%s.%s[/B]" % (pubDate[6:8], pubDate[4:6], pubDate[0:4])
	
	PLog("mp3_url: %s, web_url: %s, attr: %s, img: %s, dur: %s" % (mp3_url, web_url, attr, img, dur))
	PLog("title: %s, summ: %s, source: %s, sender: %s, pubDate: %s" % (title, summ, source, sender, pubDate))
	return mp3_url, web_url, attr, img, dur, title, summ, source, sender, pubDate
							
#----------------------------------------------------------------
# 22.02.2022 Anpassung an ARD-Änderung
# Ausführung: AudioSearch_cluster 
# 26.03.2023 Umstellung Web.json -> api.json
# 14.04.2024 Rückkehr zur Websuche, s.u.
#
def AudioSearch(title, query='', path=''):
	PLog('AudioSearch:')
	CacheTime = 3600							# 1 Std.
	title_org = title

	# https://api.ardaudiothek.de/search?query=%s - Abweichung der Ergebnisse
	#	vom Web
	# next-Link: www.ardaudiothek.de//_next/data/utkFcitMgXTWZyB2T6HPH/suche/%s.json 
	#	unbrauchbar wg. Session-Token
	# Versuch graphql-Umsetzung: Formatprobleme mit Quotierung, Doku graphql: 
	#	https://api.ardaudiothek.de/graphql -> DOCS
	# 14.04.2024 Rückkehr zur Websuche "https://www.ardaudiothek.de/suche/%s/",
	#	Extraktion der Web-json-Daten, starten mit {"pageProps":{"initialData": 
	#	vor {"data", _links fehlen, im Gegensatz sind die nodes für Podcasts + 
	#	Themen wie im Web vorhanden (in der norm. api-Quelle nur bis zu 23).
	#	
	base = "https://www.ardaudiothek.de/suche/%s/"
	
	if 	query == '':	
		query = get_query(channel='ARD Audiothek')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
		
	query = py2_encode(query)										# encode für quote
	query = query.strip()
	query_org = query	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')								# Home-Button
	
	if path == '':													# Folgeseiten
		path = base % quote(query)
	path_org=path
	
	page, msg = get_page(path=path, do_safe=False)					# nach quote ohne do_safe 	
	if page == '':	
		msg1 = "Fehler in AudioSearch:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	if page.find('>Keine Treffer<') > 0:	
		msg1 = "leider keine Treffer zu:"
		msg2 = query
		MyDialog(msg1, msg2, '')	
		return
		
	page =  Audio_get_webslice(page, mode="json")
	AudioSearch_cluster(li, path, title="Suche: %s" % query, page=page, key="", query=query)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#----------------------------------------------------------------
# 1. Aufruf: lädt Webseite für Suche + ermittelt Cluster im Webteil,
#	erstellt die passenden api-Calls
# 2. Aufruf: führt api-Call aus und übergibt an Audio_get_search_cluster
# entfallen: Suchergebnisse -> PodFavoriten
# 25.03.2023 Umstellung Web -> json nach ARD-Änderungen
# 15.04.2024 Webaufrufe integriert (editorialCollections) -> Audio_get_webslice
#
def AudioSearch_cluster(li, url, title, page='', key='', query=''):
	PLog('AudioSearch_cluster: ' + key)
	PLog(query); PLog(li)
		
	if page == '':													# Permanent-Redirect-Url				
		page, msg = get_page(path=url, do_safe=False, GetOnlyRedirect=True)	
		url = page								
		page, msg = get_page(path=url, do_safe=False)	
		if page == '':	
			msg1 = "Fehler in AudioSearch_cluster:" 
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return
	PLog(len(page))
	if page.startswith('<!DOCTYPE html>'):
		PLog("webpage_found")
		page = Audio_get_webslice(page, mode="json")				# json ausschneiden
	
	page = json.loads(page)
	PLog(str(page)[:100])
	
	search_url = url												# für erneuten Aufruf Step2
	try:
		if "pageProps" in page:										# Web-api?
			PLog("pageProps_found")
			page  = page["pageProps"]["initialData"]
			searchText  = page["searchText"]
		objs = page["data"]["search"]								# Ergebnis-Ebenen
	except Exception as exception:
		PLog("search_error: " + str(exception))
	PLog(str(page)[:100])
	PLog(len(objs))

	#--------------------------------								# 2. Aufruf Sendungen, Sammlungen
	if key:
		PLog("Step2:")
		Audio_get_search_cluster(objs, key)							#  -> Verteilung
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
		return
	#--------------------------------	
	
	PLog("Step1:")													# 1. Aufruf 
	if li  == '':
		li = xbmcgui.ListItem()
		li = home(li,ID='ARD Audiothek')							# Home-Button
				
	# Der zusätzl. Abschnitt "deviceType": "responsive" mit 
	# 	allen Rubriken wird nicht gelistet
	cluster = [
			u"programSets|Sendungen (Podcasts)|Sendung",
			u"editorialCollections|Sammlungen/Themen|Thema", 
			u"editorialCategories|Rubriken|Rubrik", 
			u"items|Episoden (alle Einzelbeiträge)|Episode"]
	
	tag = "Folgeseiten"
	for clus in cluster:
		key, tag1, tag2 = clus.split("|")								# tag1, tag2 -> Infotext 1. + 2.Zeile
		PLog("%s | %s | %s" % (key, tag1, tag2))
		if "numberOfElements" in objs[key]:
			anz = objs[key]["numberOfElements"]
		else:
			anz = objs[key]["totalCount"]
		PLog("anz: %d" % anz)
		
		if anz > 0:
			if key != "items":											# nur Beiträge aus 1. Suchseite verfügbar,
				anz_api = anz											# 	"_links" nicht verwendbar (s.u.)
				anz = len(objs[key]["nodes"])	
				if anz != anz_api:										# tatsächliche Anzahl in api-Quelle abweichend!
					PLog("anz_correct: %d statt %d" % (anz, anz_api))		
			item =  objs[key]["nodes"][0]								# 1. Beitrag
			tag = u"Folgeseiten | [B]%s | Anzahl: %d[/B]" % (tag1, anz) # 1. tagline
			tag = u"%s\nTitel + Bild: 1. %s" % (tag, tag2)				# 2. tagline
	
			# Anpassung für string-Auswertung, einschl. utf-8-Kodierung für Python <= 2.7 -> Audio_get_items_single:
			s=my_jsondump(item)
			mp3_url, web_url, attr, img, dur, title, summ, source, sender, pubDate = Audio_get_items_single(s, key)
			if mp3_url == "" and web_url == "":
				PLog("skip_empty_mp3_and_web_url") 
				continue

			PLog("1Satz_a:")
			label = title
			PLog(key); PLog(title); PLog(search_url); PLog(attr);
			
			# nur die Links der items funktionieren. Für die übrigen 
			#	Cluster stehen nur die Beiträge der 1. Suchseite zur
			#	Verfügung, trotz kompl. Linksätze (first, next,..) - 
			#	Ursache nicht bekannt.  
			# Web-api ohne _links
			if key == "items":											# Episoden (Einzelbeiträge)
				if "_links" in objs[key]:
					url_first = objs[key]["_links"]["first"]["href"]
					PLog("url_first: " + url_first)
					search_url = url_first.replace("./", ARD_AUDIO_BASE)
					PLog("search_url: " + search_url)
				else:													# Web-api: build search_url
					api_url = "search/items?query=%s&offset=0&limit=24"	% quote(py2_encode(searchText)) # searchText s.o.
					search_url = ARD_AUDIO_BASE + api_url
					
				
			search_url=py2_encode(search_url); title=py2_encode(title); # -> 2. Aufruf 
			fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'key': '%s'}" % (quote(search_url), 
				quote(title), key)
			addDir(li=li, label=label, action="dirList", dirID="AudioSearch_cluster", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)	
				
				
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


#----------------------------------------------------------------
#	20.02.2022 Erneuerung Audiothek
#	Auswertung Mehrfach-Beiträge für AudioSearch_cluster
#	keys: 	editorialCategories 	= Rubriken
#			editorialCollections = Sammlungen -> Audio_get_sendung_api
#			programSets = Sendungen	-> Audio_get_sendung)
#			items = Einzelsendungen (Episoden)
# 	25.03.2023 Anpassungen an ARD-Änderungen
#	27.03.2023 Anbindung Rubriken an Auswertung der Cluster via 
#		Audio_get_cluster_rubrik über Web-Link
#
def Audio_get_search_cluster(objs, key):
	PLog('Audio_get_search_cluster: ' + key)
	PLog(str(objs)[:80])
	
	li = xbmcgui.ListItem()
	li = home(li,ID='ARD Audiothek')		# Home-Button

	items =  objs[key]["nodes"]
	PLog(len(items))
	
	try:									# nexturl?			
		href = objs[key]["_links"]["next"]["href"]
		nexturl = href.replace("./", ARD_AUDIO_BASE)
		total = stringextract("numberOfElements': ", ",", str(objs))
	except Exception as exception:
		PLog("nexturl_error: " + str(exception))
		nexturl=""; total=""
	PLog('nexturl: %s, total: %s ' % (nexturl, total))	
	PLog(str(objs)[:80])
	PLog(len(items))
	
	cnt=0
	for item in items:
		node_id = item["id"]								# -> api-Path				
		# Anpassung für string-Auswertung, einschl. utf-8-Kodierung für Python <= 2.7 -> Audio_get_items_single:
		s=my_jsondump(item)
		mp3_url, web_url, attr, img, dur, title, summ, source, sender, pubDate = Audio_get_items_single(s, key)
		tag = "Folgeseiten"
		if "programSets" in key:							# Sendungen der Sender
			tag = "%s\nSender: %s" % (tag, sender)
		href = ARD_AUDIO_BASE  + "%s/%s/?offset=0&limit=20" % (key, node_id) 
		
		PLog('13Satz_a:');
		PLog(title); PLog(href); PLog(img);
		title=py2_encode(title); href=py2_encode(href);	
		
		if key=="editorialCollections" or key=="programSets":# Kollektionen, ProgrammSets
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)
		elif  key=="editorialCategories":					# editorialCategories / Kategorien
			PLog('13Satz_b: ' + href);
			href = "https://www.ardaudiothek.de/rubrik/%s" % node_id
			fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'ID': 'Audio_get_search_cluster'}" %\
				(quote(href), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_rubrik", \
				fanart=img, thumb=img, tagline=tag, fparams=fparams)	
		else:												# items: Episoden (Einzelbeiträge)
			PLog('13Satz_c: ' + mp3_url);
			tag = "Dauer %s" % dur
			if pubDate:
				tag = "%s | Datum %s" %  (tag, pubDate)
			if sender:
				tag = "%s | Sender %s\n[B]%s[/B]" % (tag, sender, attr)
			summ_par = summ
			
			mp3_url=py2_encode(mp3_url); img=py2_encode(img); summ_par=py2_encode(summ_par);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)
								
		cnt=cnt+1
			
	if 	key == "items" and nexturl:						# nexturl aus json-Quelle, Audio_get_nexturl entfällt
		img=R(ICON_MEHR)
		offset = re.search(r'offset=(\d+)', nexturl).group(1)
		offset = int(offset) +1							# Basis 0
		title = "Mehr: [B]%s[/B]" %  stringextract("searchText': '", "'", str(objs))
		tag = u"Mehr (ab Beitrag %d von %s)" % (offset, total)
		nexturl=py2_encode(nexturl); title=py2_encode(title); 	# -> 2. Aufruf 
		fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'key': '%s'}" % (quote(nexturl), 
			quote(title), key)
		addDir(li=li, label=title, action="dirList", dirID="AudioSearch_cluster", \
			fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)	
				
					
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

			
#----------------------------------------------------------------
# Aufrufer: Audio_get_rubriken_web (Liste Rubriken),
#	Audio_get_homescreen
# anders als AudioSearch_cluster wird für Rubriken der json-
#	Teil der Webseite ausgewertet - mit string-funktionen
#	Der Webteil eignet sich nicht wg. fehlender Bilder in den
#	Empfehlungen.
# Aufteilung Web-Beiträge: 1. Highligths, 2. veränderliche
#	Cluster, 3. Meistgehört, 4. Neueste Episoden, 5. Ausgewählte 
#	Sendungen, 6. Alle Sendungen aus dieser Rubrik
# 
def Audio_get_cluster_rubrik(li, url, title, ID=''):
	PLog('Audio_get_cluster_rubrik: ' + ID)
	PLog(title); PLog(url)
	title_org = title
	CacheTime = 3600												# 1 Std.
	
	if li  == '':
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD Audiothek')							# Home-Button		
		
	if "AudioHomescreen" in ID:										# Stage-Beiträge Startseite
		rubrik_id = ID
	else:															# rubrik_id aus Url-Ende
		id_url = url.split("//")[-1]
		if id_url.endswith("/"):									# i.d.R. alle
			id_url = id_url[0:len(id_url)-1]
		PLog("id_url: " + id_url)
		
		if "/" in id_url:											# alt, z.B. ../rubrik/42914694/
			rid = id_url.split('/')[-1]
		if ":" in id_url:											# neu, z.B. ../urn:ard:page:cebf0dfe68c7f771/
			rid = id_url.split(':')[-1]
		PLog("rid: " + rid)
		rubrik_id = "AudioRubrikWebJson_%s" % rid

	page = Dict("load", rubrik_id, CacheTime=CacheTime)				# json-Teil der Webseite schon vorhanden?
	if page == False or page == '':									# Cache miss od. leer - vom Sender holen
		# Name im Pfad fehlt hier noch, daher Redirect:
		url, msg = get_page(path=url, GetOnlyRedirect=True)			# Permanent-Redirect-Url
		page, msg = get_page(path=url)	
	if page == '':	
		msg1 = "Fehler in Audio_get_cluster_rubrik:" 
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
			
	if page.startswith('<!DOCTYPE html>'):							# Webseite musste neu geladen werden
		page = Audio_get_webslice(page, mode="json")				# webslice: json ausschneiden
		page = transl_json(page); page = page.replace('\\"', '*')
		Dict("store", rubrik_id, page)

	#--------------------------------								# Empfehlungen + veränderliche Cluster
	sections = stringextract('"sections":', '"rubricsData":', page)	
	PLog(sections[:80])
	
	PLog('Mark0')
	data=[]; stage=False; cnt=0										# wie Audio_get_cluster_single
	if "AudioHomescreen" in ID:										# AudioHomescreen hier nicht Stage
		data = blockextract('__typename"', stage)
	else:
		if '"type":"STAGE"' in page:								# Stage-Sätze
			data.append(stringextract('"STAGE"', '}}}]},', page))
			stage=True
		data = data + blockextract(']},{"id":', page)				# und restl. Cluster
	PLog(len(data))
	
	for item in data:	
		section_id = stringextract('"id":"', '"', item)				# id":"comedy_satire-100:-8132981499462389106",
		if cnt == 0 and stage:
			section_id = "STAGE"									# nur STAGE auswerten

		tag = u"[B]Folgeseiten[/B]"
		title = stringextract('"title":"', '"', item)				# Cluster-Titel	
		title = repl_json_chars(title)
		pos = item.find('__typename'); item = item[pos:]			# 1. Beitrag
		ftitle = stringextract('"title":"', '"', item)
		img = stringextract('"url1X1":"', '"', item)
		#img = img.replace('{width}', '640')						# fehlt manchmal
		img = img.replace('{width}', '320')
		if img == '':												# fehlt bei nicht verfügb. Livestreams, s.
			continue												#	Audio_get_homescreen (GRID_LIST_COLLAPSIBLE)
			
		tag = "%s\n\n1. Beitrag: %s" % (tag, ftitle)	

		PLog('2Satz:')
		PLog(title); PLog(img); PLog(rubrik_id); PLog(section_id);
		title=py2_encode(title); rubrik_id=py2_encode(rubrik_id); 
		section_id=py2_encode(section_id);url=py2_encode(url)
		fparams="&fparams={'title': '%s', 'rubrik_id': '%s', 'section_id': '%s', 'url': '%s'}" % \
			(quote(title), quote(rubrik_id), quote(section_id), quote(url))
		addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_single", \
			fanart=img, thumb=img, fparams=fparams, tagline=tag)	
		cnt=cnt+1
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# Aufrufer Audio_get_cluster_rubrik, Audio_get_homescreen (Stage) 
#	listet einz. Cluster oder Stage (ohne section_id)
#	Json-Ausschnitt der Rubrik-Webseite im Dict(rubrik_id)
# 17.12.2023 zusätzl. Param url (Absicherung gegen Dict-Löschung)
# 13.05.2024 Playlist-Erweiterung für Livestreams wie AudioStartLive
#
def Audio_get_cluster_single(title, rubrik_id, section_id, page='', url=""):
	PLog('Audio_get_cluster_single: ' + title)
	PLog(rubrik_id); PLog(section_id)
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')			# Home-Button

	if page == '':								# page nicht genutzt
		page = Dict("load", rubrik_id)
		if not page:							# Dict schon gelöscht?
			page, msg = get_page(url)
			if page == "":
				msg1 = 'Fehler in Audio_get_cluster_single:'
				msg2 = msg
				MyDialog(msg1, msg2, '')
				return
			page = transl_json(page); page = page.replace('\\"', '*')

	data=[]; cluster=""							# wie Audio_get_cluster_rubrik
	if section_id == "STAGE":					# nur Stage auswerten, Homescreen od. Rubriken
		cluster = stringextract('"sections"', '}}}]},', page)
	else:
		data = data + blockextract(']},{"id":', page)	
		for item in data:						# Cluster section_id suchen 
			if section_id in item:
				PLog("found: " + section_id)
				cluster = item
				break
	PLog(cluster[:300])
	pos = cluster.find('nodes'); cluster = cluster[pos:]
	nodes = blockextract('"__typename":', cluster)	
	PLog(len(nodes))
			
	# RadioPlaylist mit play_lines, play_line: m3u-Template
	PlayList = ["#EXTM3U"]											
	play_line = '#EXTINF:-1 logo="%s" group-title="ARD_Radio", %s\n%s'													
	
	downl_list=[]; 	href_add = "offset=0&limit=12&order=descending"	
	for node in nodes:		
		imgalt2=''; web_url=''; mp3_url=''
		mp3_url = stringextract('"downloadUrl":"', '"', node)			# api-Seiten ev. ohne mp3_url
		if 	mp3_url == '':
			audios = stringextract('"audios":', '}', node)				# Altern.
			mp3_url = stringextract('"url":"', '"', audios)
		if 	mp3_url == '':	
			web_url = stringextract('"sharingUrl":"', '"', node)		# Weblink
		
		node_id = stringextract('"id":"','"', node)				# ID der Sendung / des Beitrags / ..	
		typename = stringextract('__typename":"','"', node)		# Typ der Sendung / des Beitrags / ..	
		title = stringextract('"title":"','"', node)	
		dur = stringextract('"duration":',',', node)
		dauer = seconds_translate(dur)
		pubDate = stringextract('"publishDate":"','"', node)
		if pubDate:												# 2021-08-11T07:00:00+00:00
			pubDate = pubDate = "%s.%s.%s %s Uhr" % (pubDate[8:10], pubDate[5:7], pubDate[0:4], pubDate[11:16])
		descr = stringextract('"summary":"','"', node)
		if 	descr == '':
			descr = stringextract('"synopsis":"','"', node)
		if 	descr == '':
			descr = stringextract('"description":"','"', node)
		img = stringextract('"url1X1":"','"', node)				# möglich: "image": null 	
		#img = img.replace('{width}', '640')
		img = img.replace('{width}', '320')
		if img == '':
			img = R(ICON_DIR_FOLDER)
		imgalt1 = stringextract('"description":"','"', node)	# Bildbeschr.	
		imgalt2 = stringextract('"attribution":"','"', node)	# Bild-Autor
		imgalt2 = repl_json_chars(imgalt2)
		org = stringextract('"organizationName":"','"', node)	
		anz = stringextract('"totalCount":','}', node)			# Anzahl bei Mehrfach-Beiträgen
		
		PLog(descr)
		descr 	= descr.replace('\\n', '')
		descr	= unescape(descr); descr = repl_json_chars(descr)
		summ_par= descr
		title = repl_json_chars(title)
		
		PLog('4Satz:');
		PLog("typename: " + typename)
		PLog(title); PLog(img); PLog(web_url); PLog(descr[:40]);
		
		title=py2_encode(title); web_url=py2_encode(web_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	

		if typename=="Item" or typename=="EventLivestream":		# Einzelbeitrag
			tag = "[B]Audiobeitrag[/B] | %s Std. | %s | %s\nBild: %s" % (dauer,pubDate,org,imgalt2)
			if typename=="EventLivestream":		
				tag = "[B]EventLivestream[/B]  %s | %s\nBild: %s" % (pubDate,org,imgalt2)
				
			if mp3_url:
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
					quote(title), quote(img), quote_plus(summ_par))
				addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, summary=descr)			
				
				if mp3_url.endswith(".mp3") == False:				# mp3-Beiträge vom Typ items von PlayList ausschließen 
					# play_line = '#EXTINF:-1 logo="%s" group-title="ARD_Radio", %s\n%s'													
					extinf = play_line % (img, title, mp3_url)
					PlayList.append(extinf)							# -> RadioPlaylist-Button

			else:	
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(web_url), 
					quote(title), quote(img), quote_plus(summ_par))
				addDir(li=li, label=title, action="dirList", dirID="AudioWebMP3", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, summary=descr)
				
						
	#--------------------------------							# Cluster mit Folgeseiten
		if typename=="EditorialCollection" or typename=="ProgramSets" or typename=="ProgramSet":
			if anz: anz = "(%s)" % anz
			if imgalt2: imgalt2 = "Bild: %s" % imgalt2
			tag = u"[B]Folgeseiten[/B] %s\n%s" % (anz, imgalt2)
			if typename=="EditorialCollection":					# api-Call -> web-Url in Audio_get_sendung
				ID="Cluster_Sammlungen"
				href = ARD_AUDIO_BASE  + "editorialcollections/%s/?offset=0&limit=20" % (node_id)
			if typename=="ProgramSets" or typename=="ProgramSet": 	# api-Call -> web-Url in Audio_get_sendung
				ID=typename
				href = ARD_AUDIO_BASE  + "programsets/%s/?offset=0&limit=20" % (node_id)
			
			PLog('4Satz_2:');
			PLog(href)
			if typename=="ProgramSet":							# ProgramSet -> Einzelsendungen
				PLog("->Audio_get_sendung_api")
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung_api", \
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=descr)						
			else:
				PLog("->Audio_get_sendung")
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung", \
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=descr)						

	if len(PlayList) > 1:										# RadioPlaylist-Button wie AudioStartLive
		PLog("PlayList_Button: %s" % title_org)
		PlayList = py2_encode(PlayList)
		fname = make_filenames(title_org.strip())				# Titel -> Playlist-Titel	
		textKey  = "RadioPlaylist_%s" % fname
		Dict("store", textKey, PlayList)

		lable = u"[B]Download: Streamlinks (Anzahl: %d)[/B] als Playlist" % len(PlayList)
		tag = u"Ablage als <%s.m3u> im Downloadverzeichnis.\nDie Verwendung als [B]Kodi-Playlist[/B]" % textKey
		tag = "%s im Verzeichnis ../.kodi/userdata/playlists ist möglich." % tag
		summ = u""
		fparams="&fparams={'textKey': '%s'}" % textKey
		addDir(li=li, label=lable, action="dirList", dirID="DownloadText", fanart=R(ICON_DOWNL), 
			thumb=R(ICON_DOWNL), fparams=fparams, tagline=tag, summary=summ)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#----------------------------------------------------------------
# Startseite https://www.ardaudiothek.de/
# Aufrufer: AudioStartHome
# Besonderheit: Nachladebeiträge in Step 2 ("nodes":[]) - hier Pfad-
#	Nachbildung der java-Funktion (Kennz. graphql im api-Call)
#	Die ermittelten Webadressen werden hier für die weitere Nutzung im
#	Addon zu api-Calls konvertiert.
# 
def Audio_get_homescreen(page='', cluster_id=''):
	PLog('Audio_get_homescreen:')
	CacheTime = 3600												# 1 Std.
	
	path = "https://www.ardaudiothek.de/"
	ID = "AudioHomescreen"
	page = Dict("load", ID, CacheTime=CacheTime)					# Startseite Web laden 
	if page == False or page == '':									# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		page = Audio_get_webslice(page, mode="json")				# webslice: json ausschneiden
		page = transl_json(page); page = page.replace('\\"', '*')
		Dict("store", ID, page)										# Audio_get_cluster_rubrik lädt für Stage				
	if page == '':	
		msg1 = "Fehler in Audio_get_homescreen:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))
	
	skip_title = [u'für dich', u'Weiterhören', u'Meine Sender',
				u"Login-Banner", u"Bundesliga"]
	li = xbmcgui.ListItem()

	#----------------------------------------							# Step 1
	if cluster_id == '':
		PLog("Audio_step1")
		title = ID														# Stage auswerten
		tag = "Folgeseiten"
		img = R(ICON_DIR_FOLDER)
		
		objs = json.loads(page)
		items = objs["pageProps"]["initialData"]["data"]["homescreen"]["sections"]
		PLog("items: %d" % len(items))
		
		for item in items:
			PLog(str(item)[:80])
			cluster_id = item["id"]
			title = item["title"]
			if title == None:
				title=""
			typ = item["type"]											# z.B. Stage (title null)

			PLog(title); skip=False
			for s in skip_title:										# skip personenbezogene Beiträge 
				if s in title:
					skip=True; 
					break
			if skip:
				continue
				
			nodes = item["nodes"]
			PLog(len(nodes))
			if nodes:
				img = nodes[0]["image"]["url"]
				img = img.replace('{width}', '320')
				img = img.replace('16x9', '1x1')						# 16x9 kann fehlen (ähnlich Suche)
			else:
				img = R(ICON_DIR_FOLDER)
				
						
			PLog('6Satz:');
			PLog(title); PLog(typ); PLog(cluster_id); 
			cluster_id=py2_encode(cluster_id);
			label=title
			if typ == "STAGE":											# Button Highlights -> Audio_get_cluster_single
				cluster_id = "Highlights"
				label = "[B]%s[/B]" % cluster_id
			if typ == "NAVIGATION":										# neu ab 29.03.2024 -> node_load
				label = "[B]%s[/B]" % typ
	
			fparams="&fparams={'cluster_id': '%s'}" % cluster_id				
			addDir(li=li, label=label, action="dirList", dirID="Audio_get_homescreen",
				fanart=R(ICON_MAIN_AUDIO), thumb=img, tagline=tag, fparams=fparams)				
				
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

	else:	
	#----------------------------------------							# Step 2
		PLog("Audio_step2")
		PLog("cluster_id: " + cluster_id)								# ID für Nachladebeiträge (Web: "nodes":[])
		base = "https://www.ardaudiothek.de"

		if cluster_id == "Highlights":									# Stage getrennt auswerten	
			ID = "AudioHomescreen"
			title = cluster_id				
			Audio_get_cluster_single(title, rubrik_id=ID, section_id='STAGE') # lädt Dict "AudioHomescreen"
			return	
		
		li = home(li, 'ARD Audiothek')		# Home-Button
		
		# node_load: im Web java-generiert (api-Call graphql), hier mit eingestanzter cluster_id
		node_load='https://api.ardaudiothek.de/graphql?query=query%20WidgetQuery(%24id%3AID!)%7Bsection(id%3A%24id)%7Bid%20title%20type%20nodes%7Bid%20title%20image%7Burl%20url1X1%20description%20attribution%7Dpath%20...%20on%20ProgramSet%7Bid%20synopsis%20publicationService%7Bgenre%20organizationName%7D%7D...%20on%20Item%7BcoreType%20publishDate%20programSet%7Bid%20title%20publicationService%7Btitle%20genre%20path%20organizationName%7D%7Daudios%7Burl%20downloadUrl%20allowDownload%7Dduration%7D...%20on%20EditorialCollection%7Bsummary%20items%7BtotalCount%7D%7D%7D%7D%7D&variables=%7B%22id%22%3A%22entdecken-'
		node_path = node_load + cluster_id.split("entdecken-")[-1] + "%22%7D"
		
		page, msg = get_page(node_path, do_safe=False)					# node_path bereits quotiert
		page = page.replace('\\"', '*')
		ctitle = stringextract('"title":"', '"', page)					# Cluster-Titel
		
		objs = json.loads(page)
		items = objs["data"]["section"]["nodes"]
		PLog("items: %d" % len(items))
		href_add = "?offset=0&limit=20&order=descending"

		for item in items:	
			summ=""; dur=""; pubService=""; org=""; 

			node_id = item["id"]										# ID der Sendung / des Beitrags / ..	
			title = item["title"]

			img =  item["image"]["url"]
			attr =  item["image"]["attribution"]						# img-Text
			img = img.replace('{width}', '320')
			img = img.replace('16x9', '1x1')							# 16x9 kann fehlen (ähnlich Suche)
			web_url = item["path"]
			PLog("web_url: " + web_url) 
			 
			if "synopsis" in item:
				summ =  item["synopsis"]
			
			if "duration" in item:
				dur = item["duration"]
			
			if "programSet" in item:
				pubService = item["programSet"]["publicationService"]
				genre = pubService["genre"]
				org = pubService["organizationName"]
			if org == "":
				org = attr												# Fallback img-Text
			
			summ = repl_json_chars(summ); title = repl_json_chars(title)
			tag = "Cluster: %s | %s | %s | %s" % (ctitle, attr, org, dur)
			
			# Url-Konvertierung Web->Api ähnlich AudioSearch_cluster (o. query), 
			# items-Formate abweichend, Ziel-Verteilung via ID in AudioSearch_cluster:
			# Fallback für fehlende Kennz. in web_url, z.B. Sendungs-Vorschau 
			tag = "[B]Folgeseiten[/B]"
			if dur:
				tag = "[B]zum Audio[/B] (%s)" % seconds_translate(dur)
			href = ARD_AUDIO_BASE  + "items/%s%s" % (node_id, href_add)	# Fallback vorangestellt	
						
			vert="sendung"												# default -> Audio_get_sendung
			if '/sendung/' in web_url:									# "Sendungen"
				href = ARD_AUDIO_BASE  + "programsets/%s/%s" % (node_id, href_add)
			if '/sammlung/' in web_url:									# "Sammlungen"		
				href = ARD_AUDIO_BASE  + "editorialcollections/%s/%s" % (node_id, href_add)  
			if '/rubrik/' in web_url:									# "Rubriken"		
				href = "https://www.ardaudiothek.de/rubrik/%s/" % node_id
				vert="web"  
			if '/episode/' in web_url:									# "Episoden (einzelne Beiträge)"										
				href = ARD_AUDIO_BASE  + "items/%s%s" % (node_id, href_add) 
				vert='api'				
			
			PLog("8Satz:")
			PLog(title); PLog(href); PLog(img); PLog(summ[:80]); 
			PLog("vert: " + vert)
			
			href=py2_encode(href); title=py2_encode(title); 
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
			if vert == "sendung":
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung", \
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)		
			
			if vert == "api":
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung_api", \
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)							

			if vert == "web":
				fparams="&fparams={'li': '', 'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_rubrik", \
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)							

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#----------------------------------------------------------------
# MP3 in Webpage (json-Bereich) ermitteln - Vorstufe für AudioPlayMP3
# Aufruf Audio_get_sendung (Webseite Feb. 2022 ohne mp3-Quellen)
# Audio_get_webslice nicht benötigt (url eindeutig ermittelbar)
# no_gui: nur Rückgabe (-> DownloadMultiple)
#
def AudioWebMP3(url, title, thumb, Plot, ID='', no_gui=''):
	PLog('AudioWebMP3: ' + title)
	
	page, msg = get_page(path=url, GetOnlyRedirect=True)	
	url = page								
	page, msg = get_page(path=url)			
	if page == '' and no_gui == '':	
		msg1 = "Fehler in AudioWebMP3:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return 
	PLog(len(page))
	
	url = stringextract('"downloadUrl":"','"', page)
	if 	url == '':
		pos = page.find('"audios":')
		if pos >= 0:
			url = stringextract('"url":"','"', page)			# vor downloadUrl
	 
	if url == '' and no_gui == '':	
		msg1 = "AudioWebMP3:"
		msg2 = "leider keine Audioquelle gefunden zu:"
		msg3 = "[B]%s[/B]" % title
		MyDialog(msg1, msg2, msg3)	
	else:
		if no_gui:
			PLog("url: " + url)
			return url
		else:
			AudioPlayMP3(url, title, thumb, Plot, ID='')
		
	return
	
#----------------------------------------------------------------
# Ausgabe Audiobeitrag
# Falls pref_use_downloads eingeschaltet, werden 2 Buttons erstellt
#	(Abspielen + Download).
# Falls pref_use_downloads abgeschaltet, wird direkt an PlayAudio
#	übergeben.
# 01.07.2021 ID variabel für Austausch des Home-Buttons
# 13.05.2024 Erweiterung für Livestreams: Download als
#	m3u-Datei (wie AudioStartLive)
# 28.10.2024 Url-Behandlung für Audios von podcast.de (AudioPodcastDe,
#	AudioPodcastDeSearch)
#
def AudioPlayMP3(url, title, thumb, Plot, ID=''):
	PLog('AudioPlayMP3: ' + url)
	PLog(title)
	
	if ".mp3?" in url or ".m4a?" in url:					# AudioPodcastDe, AudioPodcastDeSearch
		if ".mp3?" in url:									# ..644e320a4561.mp3?source=feed
			pos=url.find(".mp3?")
			url = url[:pos+4]
		if ".m4a?" in url:
			pos=url.find(".m4a?")
			url = url[:pos+4]
	
	if SETTINGS.getSetting('pref_use_downloads') == 'false':
		PLog('starte PlayAudio direkt')
		PlayAudio(url, title, thumb, Plot)  # PlayAudio	direkt
		return
	
	li = xbmcgui.ListItem()
	if ID == '':
		ID='ARD Audiothek'
	li = home(li, ID=ID)						# Home-Button
		
	summary = Plot.replace('||', '\n')			# Display
	 
	PLog(title); PLog(url); PLog(Plot);
	title=py2_encode(title); url=py2_encode(url);
	thumb=py2_encode(thumb); Plot=py2_encode(Plot);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(url), 
		quote(title), quote(thumb), quote_plus(Plot))
	addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams, 
		summary=summary, mediatype='music')
	
	if ".icecastssl." not in url:				# Livestreams ausschließen
		download_list = []						# 2-teilige Liste für Download: 'title # url'
		download_list.append("%s#%s" % (title, url))
		PLog(download_list)
		title_org=title; tagline_org=''; summary_org=Plot
		li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=-1)  # Downloadbutton
	else:
		# Streamlinks: "Dateiname ** Titel Zeitmarke ** Streamlink" -> DownloadText
		textKey  = "RadioStreamSingle"
		streamList=[]							# Button m3u-Datei wie AudioStartLive
		now = datetime.datetime.now()
		timemark = now.strftime("%d.%m.%Y")
		fname = make_filenames(title)
		fname = py2_encode(fname)
		streamList.append("%s.m3u**# %s | ARDundZDF %s**%s" % (fname, title, timemark, url))
		streamList = py2_encode(streamList)	
		Dict("store", textKey, streamList)
						
		lable = u"[B]Download[/B]: %s.m3u" % fname
		tag = u"Die Ablage der m3u-Datei erfolgt im Downloadverzeichnis." 
		summ = u"Sie kann in eine Playlist eingefügt oder direkt im Player abgespielt werden."
		fparams="&fparams={'textKey': '%s'}" % textKey
		addDir(li=li, label=lable, action="dirList", dirID="DownloadText", fanart=R(ICON_DOWNL), 
			thumb=R(ICON_DOWNL), fparams=fparams, tagline=tag, summary=summ)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
##################################### Ende Audiothek ###############################################
# ---------------------------------------- Start ARD Sportschau.de ---------------------------------
# 12.06.2022 nach erneutem Umbau der Seite www.sportschau.de abgeschaltet - s. Post 2606 zu
#	Update 4.4.0
#def ARDSport(title):
#def ARDSportEvents():
#def ARDSportPanel(title, path, img, tab_path='', paneltabs=''):
#def ARDSportPanelTabs(title, path, img, tab_path=''):
#def ARDSportHoerfunk(title, path, img):
#def ARDSportTablePre(base, img, clap_title=''):
#def ARDSportTable(path, title, table_path=''):
#def ARDSportAudioStreamsSingle(title, path, img, tag, summ, ID):
#def ARDSportPodcast(path, title):
#def ARDSportEventLive(path, page, title, oss_url='', url='', thumb='', Plot=''):		
#def ARDSportSliderSingleTab(title, path, img, page=''):
					
#--------------------------------------------------------------------------------------------------
# Liste der ARD Audio Event Streams in livesenderTV.xml
#	-> SenderLiveListe -> SenderLiveResolution (Aufruf
#	einz. Sender)
# 24.08.2023 vorerst deaktivert, channel in livesenderTV.xml
#	entfernt - 26.08.2023 wiederhergestellt
def ARDSportAudioXML(channel, img=''):
	PLog('ARDSportAudioXML:') 
	PLog(channel)

	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender='')
	return
#--------------------------------------------------------------------------------------------------
# Bilder für ARD Sportschau, z.B. Moderatoren
# Einzelnes Listitem in Video-Addon nicht möglich - s.u.
# Slideshow: ZDF_SlideShow
# 17.06.2022 angepasst an Webänderungen
#
def ARDSportBilder(title, path, img):
	PLog('ARDSportBilder:'); 
	PLog(title); PLog(path)
	title_org = title
	icon = R("ard-sportschau.png")

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	page = ARDSportLoadPage(title, path, "ARDSportBilder") 	# path: cacheID
	if page == '':
		return
	PLog(len(page))
	
	pos = page.find('_topline">Bilderstrecke<')
	if pos < 0:
		pos = page.find('>Bilder<')							# Altern.
		if pos < 0:
			msg1 = u"%s:" % title
			msg2 = u'keine Bilder gefunden'
			xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
			return  
		
		
	page = page[pos:]
	cont = stringextract('data-v="', '"', page)				# json-Inhalt (Bildstrecke.json)
	cont = decode_url(cont)									# abweichend von Playerdaten
	cont = unescape(cont)
	cont = (cont.replace('\\"','*').replace('<strong>','[B]').replace('</strong>','[/B]'))
	PLog(cont[:60])
	
	content = blockextract('"description"', cont)	
	PLog(len(content))
	if len(content) == 0:
		msg1 = u"%s:" % title
		msg2 = u'keine Bilder gefunden'
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
		return  
		
	DelEmptyDirs(SLIDESTORE)								# leere Verz. löschen									
	fname = make_filenames(title)							# Ablage: Titel + Bildnr
	fpath = os.path.join(SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2); 
			MyDialog(msg1, msg2, '')
			return li	
				
	image = 0; background=False; path_url_list=[]; text_list=[]
	for rec in content:			
		# größere Bilder erst auf der verlinkten Seite für einz. Moderator		
		img_src	= stringextract('"l":"', '"', rec)				
		if img_src == "":
			img_src	= stringextract('"m":"', '"', rec)
			
		headline	= stringextract('"title":"', '"', rec)
		headline	= unescape(headline); headline=repl_json_chars(headline)
		summ		= stringextract('"description":"', '"', rec)
		PLog("summ: " + summ[:80]) 	
		
		if img_src:
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
			local_path 	= "%s/%s" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d" % (image+1)
			PLog("Bildtitel: " + title)
			title = unescape(title)
			lable = "%s: %s" % (title, headline)			# Listing-Titel
			
			thumb = ''
			local_path = os.path.abspath(local_path)
			thumb = local_path
			if os.path.isfile(local_path) == False:			# schon vorhanden?
				# urlretrieve(img_src, local_path)			# umgestellt auf Thread	s.u.		
				# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Podcast, 
				#	Zieldatei_kompletter_Pfad|Podcast ..
				path_url_list.append('%s|%s' % (local_path, img_src))
					
				if SETTINGS.getSetting('pref_watermarks') == 'true':
					txt = "%s\n%s\n%s\n%s\n" % (fname,lable,'',summ)
					text_list.append(txt)	
				background	= True						
				
			PLog("Satz19:");PLog(title);PLog(img_src);PLog(thumb);PLog(summ[0:40]);
			# Lösung mit einzelnem Listitem wie in ShowPhotoObject (FlickrExplorer) hier
			#	nicht möglich (Playlist Player: ListItem type must be audio or video) -
			#	Die li-Eigenschaft type='image' wird von Kodi nicht akzeptiert, wenn
			#	addon.xml im provides-Feld video enthält
			if thumb:										
				local_path=py2_encode(local_path);
				fparams="&fparams={'path': '%s', 'single': 'True'}" % quote(local_path)
				addDir(li=li, label=lable, action="dirList", dirID="ZDF_SlideShow", 
					fanart=thumb, thumb=thumb, fparams=fparams, summary=summ)
				image += 1
			
	if background and len(path_url_list) > 0:				# Übergabe Url-Liste an Thread
		from threading import Thread	# thread_getfile
		textfile=''; pathtextfile=''; storetxt=''; url=img_src; 
		fulldestpath=local_path; notice=True; destdir="Slide-Show-Cache"
		now = datetime.datetime.now()
		timemark = now.strftime("%Y-%m-%d_%H-%M-%S")
		folder = fname 
		background_thread = Thread(target=thread_getpic,
			args=(path_url_list,text_list,folder))
		background_thread.start()
			
	if image > 0:		
		fpath=py2_encode(fpath);
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
		
		lable = u"Alle Bilder in diesem Bildverzeichnis löschen"		# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------------------------------------------------------------------------------------------- 
# 04.06.2023 nur noch von WDRstream (WRD-Lokalzeit) verwendet (live=true) - 
#	baldmöglichst auf neue ARD-Quellen umstellen 
# 14.07.2023 nicht für ShowSeekPos geeignet - alle Streams starten verzögert am
#	Pufferanfang, zeigen "large audio sync error" - s.a. WDRstream
# 
def ARDSportVideo(path, title, img, summ, Merk='false', page=''):
	PLog('ARDSportVideo:');
	img_org=img
	PLog(path); PLog(summ); PLog(len(page))
	summ = summ.replace('||||', ' | ')

	title_org = title
	# Header erforder.?: /wintersport/alle-videos-komplett-uebersicht-100.html
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}"
	msg=''
	if page == '':
		page, msg = get_page(path=path, header='', decode=True)		# decode hier i.V.m. py2_decode 						
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return 
	PLog(len(page))
	page=py2_decode(page)					

		
	# Bsp. video_src: "url":"http://deviceids-medp.wdr.de/ondemand/167/1673848.js"}
	#	-> 	//ardevent2.akamaized.net/hls/live/681512/ardevent2_geo/master.m3u8
	#	derselbe Streamlink wie Direktlink + Hauptmenü
	# 16.06.2019 nicht für die Livestreams geeignet.
	if 'deviceids-medp.wdr.de' in page:								# häufige Quelle
		video_src = stringextract('deviceids-medp.wdr.de', '"', page)
		video_src = 'http://deviceids-medp.wdr.de' + video_src
	else:
		PLog('hole_video_src_iframe:')
		video_src=''
		playerurl = stringextract('webkitAllowFullScreen', '</iframe>', page)
		playerurl = stringextract('src="', '"', playerurl)
		if playerurl:
			base = 'https://' + path.split('/')[2]					# Bsp. fifafrauenwm.sportschau.de
			video_src = base + playerurl
	PLog("video_src: " + video_src)
	
	if video_src == '':
		if 'class="media mediaA video' in page:					# ohne Quellen, aber Videos gefunden
			ARDSportSliderSingleTab(title, path, img, page)			# -> ARDSportSliderSingleTab - obsolet, s.o.
			return
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
				
		else:
			if '"videoURL" : "' in page or '"config"' in page:	# Quellen in Seite eingebettet					
				PLog('detect_videoURL:')
				# Je ein HLS + MP4-Link direkt auf der Seite im json-Format
				# Bsp.: www.sportschau.de/tor-des-monats/archiv/april2017tdm100.html
				web = stringextract('"mediaResource"', '</script>', page)	# json-Inhalt ausschneiden
				if web == '':							
					web = stringextract('"streamUrl":"', '"', page)	# z.B. .m3u8-Link auf hessenschau.de/sport
					web = '"videoURL":"' + web + '"'				# komp. für weit. Auswertung
				PLog("web-media oder -config: " + web[:100])
				page = web
				video_src=''										# skip 	'-ardplayer_image-' in video_src
			else:
				msg1 = u'Leider kein Video gefunden: %s' % title 	# keine Chance auf Videoquellen
				msg2 = path
				MyDialog(msg1, msg2, '')
				return
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

		
	li = xbmcgui.ListItem()
	#li = home(li, ID='ARD')						# Home-Button (in WDRstream gesetzt)

	if video_src.endswith('.js'):									# //deviceids-medp-id1.wdr.de/../2581397.js
		page, msg = get_page(video_src)								# json mit (nur) Videoquellen laden
		
	if '"videoURL' in page or '"audioURL' in page:
		page = page.replace('":"', '" : "')							# Anpassung an Web-embedded json
		video_src=''
		
	m3u8_url=''; mp_url=''; title_m3u8=''; title_mp=''				# mp_url: mp4 oder mp3
	if '-ardplayer_image-' in video_src:							# Bsp. Frauen-Fußball-WM
		PLog('-ardplayer_image- in video_src:')
		# Debug-Url's:
		#https://fifafrauenwm.sportschau.de/frankreich2019/nachrichten/fifafrauenwm2102-ardplayer_image-dd204edd-de3d-4f55-8ae1-73dab0ab4734_theme-sportevents.html		
		#->:
		#https://fifafrauenwm.sportschau.de/frankreich2019/nachrichten/fifafrauenwm2102-ardjson_image-dd204edd-de3d-4f55-8ae1-73dab0ab4734.json	
					
		image = stringextract('image-', '_', video_src) 			# json-Pfad neu bauen
		PLog(image)
		path = video_src.split('-ardplayer_image-')[0]
		PLog(path)
		path = path + '-ardjson_image-' + image + '.json'
		PLog(path)
		page, msg = get_page(path)									# json mit videoquellen laden
		
		plugin 	= stringextract('plugin": 0', '_duration"', page) 
		auto 	= stringextract('"auto"', 'cdn"', plugin) 			# master.m3u8 an 1. Stelle		
		m3u8_url= stringextract('stream": "', '"', auto)
		PLog("m3u8_url: " + m3u8_url)
		title_m3u8 = "HLS auto | %s" % title_org
		
		mp 	= stringextract('quality": 3', 'cdn"', page)			# mp4-HD-Quality od. mp3
		mp_url= stringextract('stream": "', '"', mp)
		PLog("mp_url: " + mp_url)
		if mp_url:
			title_mp = "MP4 HD | %s" % title_org
			if mp_url.endswith('.mp3'):
				title_mp = "Audio MP3 | %s" % title_org
	
	else:															# Videoquellen in Webseite?
		videos = blockextract('"videoURL" : "', page, '}')
		videos = videos + blockextract('"audioURL" : "', page, '}')
		PLog(len(videos))
		
		if len(videos) == 0:
			msg1 = u'Leider kein Video gefunden: %s' % title # keine weitere Chance auf Videoquellen
			msg2 = path
			MyDialog(msg1, msg2, '')
			return
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
		
		for video in videos:
			if "videoURL" in video:
				url= stringextract('"videoURL" : "', '"', video)
			else:
				url= stringextract('"audioURL" : "', '"', video)
			if 'manifest.f4m' in url:					#  manifest.f4m überspringen
				continue
			if url.endswith('.m3u8'):
				m3u8_url = url
				title_m3u8 = "HLS auto | %s" % title_org
			if url.endswith('.mp4'):
				mp_url = url
				title_mp = "MP4 HD | %s" % title_org
			if url.endswith('.mp3'):
				mp_url = url
				title_mp = "MP3 Audio | %s" % title_org		
		
		if m3u8_url == '' and mp_url == '':				# ev. nur Audio verfügbar
			mp_url = stringextract('"audioURL":"', '"', page)
			
		if m3u8_url and m3u8_url.startswith('http') == False:		
			m3u8_url = 'https:' + m3u8_url				# //wdradaptiv-vh.akamaihd.net/..	
		if mp_url and mp_url.startswith('http') == False:		
			mp_url = 'https:' + mp_url				
		
		
	mediatype = 'video'
		
	# Sofortstart - direkt, falls Listing nicht Playable:
	# 04.08.2019 Sofortstart nur noch abhängig von Settings und nicht zusätzlich von  
	#	Param. Merk.
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true': 	# Sofortstart
		PLog('Sofortstart: ARDSportPanel')
		PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
		PlayVideo(url=m3u8_url, title=title_m3u8, thumb=img, Plot=summ, sub_path="", live="")
		return
	
	if img  == "":
		img = img_org
	PLog("Satz27:")
	PLog("m3u8_url: " + m3u8_url); PLog(title_m3u8);
	PLog(title_mp); PLog("mp_url: " + mp_url)
	PLog(img)
	
	m3u8_url=py2_encode(m3u8_url); title_m3u8=py2_encode(title_m3u8); 
	title_mp=py2_encode(title_mp); 
	img=py2_encode(img); summ=py2_encode(summ);
	if m3u8_url:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': ''}" %\
			(quote_plus(m3u8_url), quote_plus(title_m3u8), quote_plus(img), quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, tagline=title_m3u8, summary=summ) 
	if mp_url:	
		if mp_url.endswith('.mp3'):
			mediatype = 'audio'
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': ''}" %\
			(quote_plus(mp_url), quote_plus(title_mp), quote_plus(img), quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, tagline=title_mp, summary=summ) 	
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#---------------------------------------------------------------------------------------------------
# Neues  Menü sportschau.de (WDR)
# Ersatz für weggefallene Funktionen. Siehe Start ARD Sportschau.de
# 
def ARDSportWDR(): 
	PLog('ARDSportWDR:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	base = "https://images.sportschau.de"
	logo = base + "/image/3fbb1eaf-fb0a-4f1b-a5a9-44a643839cd5/AAABgTjL3GM/AAABgPp7Db4/16x9-1280/sportschau-logo-sendung-100.jpg"
	
	title = u"Startseite"									# Startseite	
	tag = u"Für Groß-Events bitte die vorhandenen Menü-Buttons verwenden."
	cacheID = "Sport_Startseite"
	img = logo
	path = "https://www.sportschau.de"
	fparams="&fparams={'logo': '%s'}" % quote(img)
	addDir(li=li, label=title, action="dirList", dirID="ARDSportStart", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Livestreams der Sportschau"
	tag = u"kommende Events: Ankündigungen mit Direktlinks"
	img = logo
	title=py2_encode(title)
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="ARDSportLive", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	
	#---------------------------------------------------------	Großevents Start
	'''
	title = u"Event: [B]Tour de France Femmes 2024[/B]"					# Großevent	Template
	tag = u"Tour de France Femmes 2024, Rennberichte, Analysen, Bilder, Ergebnisse und Wertungen zu allen Etappen"
	cacheID = "Sport_TourdeFemmes_2024"
	img = "https://images.sportschau.de/image/5e488d45-7e8c-4ec6-9d90-b10cb3a43233/AAABiaIsZUA/AAABkUqnCZ0/16x9-1280/tdff-peloton-etappe-7-100.jpg"
	path = "https://www.sportschau.de/radsport/tourdefrance-femmes"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	'''

	#---------------------------------------------------------	Großevents Ende

	title = u"Event-Archiv"									# Buttons für ältere Events	
	tag = u"Archiv für zurückliegende Groß-Events."
	img = logo
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="ARDSportWDRArchiv", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Tabelle 1. Bundesliga"						# Tabelle 1					
	tag = u"Quelle: www.sportschau.de"
	summ = u"aktuelle Tabelle plus Zugang zum Archiv bis 1964"
	path = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/tabelle/"
	logo=py2_encode(logo); path=py2_encode(path) 
	fparams="&fparams={'title': '%s', 'logo': '%s', 'path': '%s'}" % (title, logo, quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportTabellen", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	

	title = u"Tabelle 2. Bundesliga"						# Tabelle 2							
	path = "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-2-bundesliga/tabelle/"
	fparams="&fparams={'title': '%s', 'logo': '%s', 'path': '%s'}" % (title, logo, quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportTabellen", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	

	title = u"Tor des Monats"									# Tor des Monats
	tag = u"Tor des Monats: Hier gibt's Highlights, Clips und ausgewählte Höhepunkte aus der langen Geschichte dieser Rubrik."
	img = "https://images.sportschau.de/image/02d77451-37d2-4f6c-a9e3-13747421eb85/AAABgQuiu3s/AAABgPp7Db4/16x9-1280/tordesmonats-sp-836.jpg" 
	path = "https://www.sportschau.de/tor-des-monats"
	title=py2_encode(title); path=py2_encode(path); 
	img=py2_encode(img); 
	fparams="&fparams={'title': '%s', 'path': '%s','img': '%s'}" %\
		(quote(title), quote(path), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMonatstor", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Moderation der Sportschau"						# Moderation
	tag = u"Bildgalerie"
	img = "https://images.sportschau.de/image/43770bba-0b81-4d0e-8dd2-b282f90859d5/AAABgUeQFuU/AAABg8tMQ7w/1x1-840/sportschaumoderator-sp-126.jpg"
	path = "https://www.sportschau.de/sendung/moderation"
	title=py2_encode(title); path=py2_encode(path); 
	img=py2_encode(img); 
	fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" %\
		(quote(title), quote(path), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportHub", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	
	title = u"ARD Event Streams (eingeschränkt verfügbar)"		# ARD Event Streams im Haupt-PRG	
	tag = u"Event Streams von BR, MDR, NDR, WDR | eingeschränkt verfügbar"
	img = R("tv-livestreams.png")
	title=py2_encode(title)
	fparams="&fparams={'title': '%s', 'listname': '%s', 'fanart': '%s'}" % (quote(title), quote(title), img)
	addDir(li=li, label=title, action="dirList", dirID="SenderLiveListe", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	
	title = u"ARD Audio Event Streams"							# Audio Event Streams im Haupt-PRG	
	tag = u"Event- und Netcast-Streams, Sport in der Audiothek, Audiostreams auf sportschau.de"
	img = R("radio-livestreams.png")
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="ARDAudioEventStreams", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#---------------------------------------------------------------------------------------------------
# Event-Archiv
#	Buttons für ältere Events
# 
def ARDSportWDRArchiv(): 
	PLog("ARDSportWDRArchiv:")
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	title = u"Event: [B]Tour de France Femmes 2024[/B]"					# Großevent	
	tag = u"Tour de France Femmes 2024, Rennberichte, Analysen, Bilder, Ergebnisse und Wertungen zu allen Etappen"
	cacheID = "Sport_TourdeFemmes_2024"
	img = "https://images.sportschau.de/image/5e488d45-7e8c-4ec6-9d90-b10cb3a43233/AAABiaIsZUA/AAABkUqnCZ0/16x9-1280/tdff-peloton-etappe-7-100.jpg"
	path = "https://www.sportschau.de/radsport/tourdefrance-femmes"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)

	title = u"Event: [B]OLYMPIA 2024[/B]"							# Großevent	
	tag = u"Alles zu den Olympischen Spielen 2024 Paris - News, Ergebnisse, Livestreams"
	cacheID = "Sport_OLYMPIA_2024"
	img = "https://images.sportschau.de/image/8256571a-83dd-474d-9f81-982a02eea327/AAABi9KI1Ww/AAABjwnlFvA/16x9-1280/logo-olympia-paris-2024-100.jpg"
	path = "https://www.sportschau.de/olympia/index.html"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Tour de France 2024[/B]"					# Großevent	
	tag = u"Tour de France 2024, Livestreams, Videos, Nachrichten, Rennberichte, Etappen, Ergebnisse und Wertungen"
	cacheID = "Sport_TourdeFrance_2024"
	img = "https://images.sportschau.de/image/b0709b8b-c4de-4632-af95-5594f03eeea3/AAABkAOw8zc/AAABjwnlFvA/16x9-1280/nizza-256.jpg"
	path = "https://www.sportschau.de/radsport/tourdefrance/index.html"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]UEFA EURO 2024[/B]"							# Großevent	
	tag = u"Alle Infos zur UEFA EURO 2024 | sportschau.de"
	cacheID = "UEFA_EURO"
	img = "https://images.sportschau.de/image/8f60e4b7-dd53-4cee-bbc2-5ace93112d8b/AAABiz2LtlE/AAABjwnlFvA/16x9-1280/em-pokal-122.jpg"
	path = "https://www.sportschau.de/fussball/uefa-euro-2024"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Basketball-WM 2023[/B]"							# Großevent	
	tag = u"Aktuelle News zur Basketball-WM 2023 | sportschau.de"
	cacheID = "BasketballWM"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/basketball/wm-maenner"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Radsport: Deutschland Tour 2023[/B]"			# Großevent	
	tag = u"Livestreams, Rennberichte, Analysen, Videos, Ergebnisse zur Deutschland Tour."
	cacheID = "DTOUR"
	img = "https://images.sportschau.de/image/c5f18e62-94e0-471f-96fc-1ca5b9d462a1/AAABiU-tGd0/AAABibBx2rU/20x9-1280/deutschland-tour-erste-etappe-108.webp"
	path = "https://www.sportschau.de/radsport/deutschland-tour/"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Hockey-EM 2023 der Männer und Frauen[/B]"		# Großevent	
	tag = u"Aktuelle News zur Hockey-EM 2023 in Mönchengladbach | sportschau.de."
	cacheID = "HockeyEM"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/hockey/feldhockey-em-index-100.html"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]FIFA Frauen WM 2023[/B]"						# Großevent	
	tag = u"32 Mannschaften spielen im Juli und August in Australien und Neuseeland um den Fußball-WM-Titel der Frauen."
	cacheID = "Sport_WMFrauen"
	img = "https://images.sportschau.de/image/b64c79b7-767b-4a7f-acda-841a07ef03d4/AAABiUo9W2s/AAABg8tME_8/16x9-1280/ffwm-pokal-laenderflaggen-100.jpg"
	path = "https://www.sportschau.de/fussball/fifa-frauen-wm"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Tour de France 2024[/B]"					# Großevent	
	tag = u"Tour de France 2024, Livestreams, Videos, Nachrichten, Rennberichte, Etappen, Ergebnisse und Wertungen"
	cacheID = "Sport_TourdeFrance_2024"
	img = "https://images.sportschau.de/image/b0709b8b-c4de-4632-af95-5594f03eeea3/AAABkAOw8zc/AAABjwnlFvA/16x9-1280/nizza-256.jpg"
	path = "https://www.sportschau.de/radsport/tourdefrance/index.html"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Handball-WM 2023 in Polen und Schweden[/B]"		# Großevent	
	tag = u"Nachrichten, Berichte, Interviews und Ergebnisse zur Handball-WM 2023 in Polen und Schweden mit dem DHB-Team."
	cacheID = "Sport_WMHandball"
	img = "https://images.sportschau.de/image/9741356a-13b2-40ed-93d0-bb70c90ebbd1/AAABhSXiawI/AAABg8tME_8/16x9-1280/handball-wm-bild-100.jpg"
	path = "https://www.sportschau.de/handball/wm"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Die Finals 2023[/B]"							# Großevent	
	tag = u"14 Sportarten, 190 deutsche Meistertitel - vom 23. bis 26. Juni finden in Berlin die Finals statt."
	cacheID = "Finals"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/die-finals"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]TOUR DE FRANCE FEMMES 2023[/B]"					# Großevent	
	tag = u"Rennberichte, Analysen, Bilder, Ergebnisse und Wertungen zu allen Etappen der Tour de France Femmes 2022."
	cacheID = "Sport_FRANCEFEMMES"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/radsport/tour-de-femmes-100.html"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]NORDISCHE SKI-WM 2023[/B]"						# Großevent	
	tag = u"Alles zur Nordischen Ski-WM in Planica."
	cacheID = "Sport_SkiWM"
	img = "https://images.sportschau.de/image/237354e3-b9b2-46bf-993a-8ecc48947e7f/AAABhol6U80/AAABg8tMRzY/20x9-1280/constantin-schmid-150.webp"
	path = "https://www.sportschau.de/wintersport/nordische-ski-wm"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Leichtathletik-WM 2022 in Eugene[/B]"			# Großevent	
	tag = u"Erstmals findet eine Leichtathletik-WM in den USA statt. News, TV-Zeiten, Livestreams, Ergebnisse zur Weltmeisterschaft in Oregon."
	cacheID = "Sport_WMEugene"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/leichtathletik/wm"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]European Championships 2022[/B]"				# Großevent	
	tag = u"Neun Europameisterschaften unter einem Dach - vom 11. bis zum 21. August finden die European Championships in München statt."
	cacheID = "ECS"
	img = "https://images.sportschau.de/image/80041de3-f096-423f-9884-a227122f0ddf/AAABgUiU4GI/AAABkZLhkrw/16x9-1280/logo-sportschau-100.jpg"
	path = "https://www.sportschau.de/european-championships"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	

	title = u"Event: [B]Fußball WM 2022 in Katar[/B]"					# Großevent	
	tag = u"Hier finden Sie alle Nachrichten, Berichte, Interviews und Ergebnisse zur FIFA WM 2022 in Katar."
	cacheID = "Sport_WMKatar"
	img = "https://images.sportschau.de/image/1e5f994d-d7c8-4c5b-a98b-23a8c5b3a71c/AAABhFJhnRw/AAABg8tME_8/16x9-1280/wm-katar-logo-news-100.jpg"
	path = "https://www.sportschau.de/fussball/fifa-wm-2022"
	title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
	fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
		(quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#---------------------------------------------------------------------------------------------------
# Live-Spiele Liga3 - Spiele-Liste von liga3-online.de/live-spiele/,
#	verknüpft wahlweise mit individueller EventStreamliste (vorerst 
#	livesenderTV.xml) oder regionalen Livestreams
# ext. Aufrufer: SenderLiveListe
# Aufruf: 	ohne sender -> List Spielepaarungen, mit sender -> Streamauswahl, play
#			mit source -> Umschalter Streamquellen (Eventstreams, Livestreams)
# Hinw.: inputstream.adaptive nicht mit Kodi < 19.* verwenden
#	Quelle liga3-online.de in utf-8 (Umlaute-Problem mit Kodi < 19.*)
# 17.12.2023 Problem: Datumsangaben ohne Jahr. Daher 6-Monatsvergleich + 
#	ggfls. Jahreskorrektur
# 08.02.2024 Berücksichtigung von 1-3 Sendern statt 1-2
#
def ARDSportLiga3(title, img, sender="", source=""): 
	PLog("ARDSportLiga3: " + sender)
	PLog(source)
	title_org=title
	
	# -----------------------------------------							# mit source -> Umschalter	
	if source:
		if source == "Live":
			Dict("store", "ARD_streamsource", "Event")
		else:
			Dict("store", "ARD_streamsource", "Live")
		ARDSportLiga3(title, img, sender="", source="")
		return
		
	# -----------------------------------------								
		
	if sender == "":													# ohne sender -> Liste Spielepaarungen
		path = "https://www.liga3-online.de/live-spiele/"
		page, msg = get_page(path)
		if page == '':	
			msg1 = "Fehler in ARDSportLiga3:" 
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return
			
		li = xbmcgui.ListItem()
		#li = home(li, ID='ARD Neu')									# entfällt (SenderLiveListe <-)
		
		month = {"Januar":1, "Februar":2, u"März":3, "April":4, "Mai":5,	# Monat numerisch (strftime)
           "Juni":6, "Juli":7, "August":8, "September":9, "Oktober":10, 
           "November":11, "Dezember":12}
	
		page = stringextract("tbody>", "</tbody>", page)# 1. Tabelle (1.: Mobilversion)
		PLog(page[:80])
		rows = blockextract("<tr", page, "</tr>")
		PLog("rows: %d" % len(rows))
		col0_pre=""; col1_pre=""; col2_pre=""
		now = EPG.get_unixtime(onlynow=True)							# unix-sec passend zu TotalTime, LastSeek
		now = int(now)
		now_dt = datetime.datetime.fromtimestamp(now)
		my_year = now_dt.strftime("%Y")
		date_format = "%Y-%m-%dT%H:%M:%SZ"
		sixmonth = 2629743 * 6	
		cnt=0										# unix-sec 6 Monate (Abgleich past/future)
		for row in rows:
			row = str(blockextract("<td", row, "</td>"))
			PLog(row)
			col0=stringextract('column-1">', '<', row)
			col1=stringextract('column-2">', '<', row)
			col2=stringextract('column-3">', '<', row)
			col3=stringextract('column-4">', '<', row)
			col4=stringextract('column-5">', '<', row)
				
			if col0 == "": col0=col0_pre 								# Leerspalten ergänzen
			if col1 == "": col1=col1_pre
			if col2 == "": col2=col2_pre
			col0_pre = col0; col1_pre = col1; col2_pre = col2;			# Backup Spalten 1-3

			nr = unescape(col0)											# &nbsp möglich
			date=""
			date = "Spiel: %s, %s" % (col1, col2)						# Datum, Zeit
			meet = col3
			sender = col4
			title = meet
			tag = "Bild: MDR.de\n" 
			tag = "%s%s" % (tag,  date)
			summ = "Spieltag: %s | Livestream bei %s" % (nr, sender)
			if sender == "":											# Leerzeilen
				PLog("skip_missing_sender")
				continue
				
			try:
				live=False; past=False
				monat = col1.split(",")[1]; monat = monat.split(".")[1]	# Samstag, 04. November, 14:00 Uhr
				my_month = month[monat.strip()]							# Juli -> 7
				my_day = re.search(r'(\d+)', date.split(",")[1]).group(1)
				my_time = col2.split(" ")[0]							# 14:00 Uhr
				my_date = "%s-%s-%sT%s:00Z" % (my_year, my_month, my_day, my_time)

				#if "Rot-Weiss" in meet:					# Debug
				#	my_date = "2023-10-21T21:10:00Z"

				my_start = datetime.datetime.fromtimestamp(time.mktime(time.strptime(my_date, date_format)))
				verf = time_translate(my_date, add_hour=False, day_warn=True)
				title_date = "%2s.%s.%s" % (my_day, my_month, my_year)
				
				my_end = my_start + timedelta(hours=2)
				my_start = time.mktime(my_start.timetuple())
				my_start = int(my_start)
				my_end = time.mktime(my_end.timetuple())
				my_end = int(my_end)
				PLog("now: %d, my_start: %d my_end: %d" % (now, my_start, my_end))
				diff = now - my_start
				if diff >= sixmonth:									# 6 Monate Abstand: wohl Zukunft
					PLog("diff_greater_sixmonth")
					my_start = now + (now-my_start)
					my_end = now + (now-my_end)
					next_year = int(my_year) +1							# Jahreskorrketur
					title_date = title_date.replace(my_year, str(next_year))
				 
				if now >= my_start and now <= my_end:
					live=True				
				if my_end < now:										# Vergangenheit
					past=True				
			except Exception as exception:
				my_date=""; title_date=""; verf=""; live=False
				PLog("my_date_error: " + str(exception))
				
			if title_date:											
				title = "%s: %s" % (title_date, title)
			if past:													# Vergangenheit: grau
				title = "[COLOR grey]%s: %s[/COLOR]" % (title_date, title)
				tag = "%s\nSpiel ist vorbei." % tag 
				summ = "%s" % summ
			else:														# Zukunft + Live
				if "| NOCH" in verf:
					only = verf.split("|")[1]
					tag = "%s | %s" % (tag, only)
				if live:												# LIVE: fett
					title = "[B]%s: %s[/B]" % (title_date, title)
					tag = "!!! LIVE !!!\n%s" % tag 
	
				tag = "[B]%s[/B]" % tag									# tag + summ Zukunft: fett
				summ = "[B]%s[/B]" % summ
				
			PLog("Satz15:"); PLog(meet);  PLog(my_date)
			fparams="&fparams={'title': '%s', 'img': '%s', 'sender': '%s'}" % (quote(title), quote(img), sender)
			addDir(li=li, label=title, action="dirList", dirID="ARDSportLiga3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)
			cnt=cnt+1
			
		if cnt == 0:
			msg1 = "ARDSportLiga3:"
			msg2 = "keine Live-Spiele gefunden" 
			xbmcgui.Dialog().notification(msg1,msg2,img,3000,sound=True)
			return

		stream_source = Dict("load", "ARD_streamsource")	# Streamquellen einstellen
		if stream_source == False or stream_source == "":
			stream_source = "Live"							# Default: Livestream
		title = u"Wechsel der [B]Streamquellen[/B] | aktuell: [B]%s-Streams[/B]" % stream_source
		tag = "Der Umschalter wechselt zwischen den [B]Livestreams der regionalen Sender[/B] und den"
		tag = "%s [B]ARD-Event-Streams in livesenderTV.xml[/B]." % tag
		
		fparams="&fparams={'title': '%s', 'img': '%s', 'source': '%s'}" % (quote(title_org), quote(img), stream_source)
		addDir(li=li, label=title, action="dirList", dirID="ARDSportLiga3", fanart=img, thumb=R("icon-list.png"), 
			fparams=fparams, tagline=tag)
			
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	# -----------------------------------------						# mit Sender -> Streamauswahl	
	else:
		source = Dict("load", "ARD_streamsource")
		PLog("source: " + str(source))
		if source == False or source == "":
			source = "Live"
		
		senderlist = ["%s" % sender]								# 3 Sender möglich, Default: 1
		if sender.count("/") > 0:
			senderlist = sender.split("/")
		PLog("sender1: %s, Anz. Sender: %s" % (senderlist[0], len(senderlist)))
		
		if source == "Event":										# Eventstreams	
			streamlist, title_list = ARDSportgetEventlist(senderlist)	
		else:														# Livestreams			
			streamlist=[]; title_list=[]							# gewählte(n) Sender filtern
			ard_streamlinks = Dict("load", "ard_streamlinks")
			# Format ard_streamlinks s. get_ARDstreamlinks,
			# Ard-Sender s. Debuglog (ardline:)
			ard_streamlinks=py2_encode(ard_streamlinks)
			
			for link in ard_streamlinks.split("\n"):			# Abgleich ARD-Url, Zuordnung linkid
				title = link.split("|")[0]						# up_low, da sender1 + 2 uppercase
				for sender in senderlist:
					if up_low(title).startswith(sender.strip()):
						PLog("title: %s, sender: %s" % (title, sender.strip()))
						url = link.split("|")[1]
						img = link.split("|")[2]
						streamlist.append("%s##%s##%s" % (title, url, img)) 
						title_list.append(title)					

		if len(streamlist) == 0:
			msg1 = "ARDSportLiga3: %s" % sender
			msg2 = "keine Streams zu %s gefunden" % sender
			xbmcgui.Dialog().notification(msg1,msg2,img,2000,sound=True)

		if  len(streamlist) == 1:								# Auswahl entfällt
			stream = streamlist[0]
		else:
			header = u"Stream auswählen | Quelle: %s-Streams" % source
			ret = xbmcgui.Dialog().select(header, title_list, preselect=0) # Dialog
			if ret >= 0:											# Auswahl?
				stream = streamlist[ret]
			else:
				return

		# hier direkter Start, um bei Fehlschlag die Streamliste sofort wieder
		#	aufrufen zu können
		PLog(stream)
		title, url, img = stream.split("##")				# Liste -> Kodi
		Plot=""
		if len(streamlist) > 1:
			Plot = "Falls der Stream nicht funktioniert, bitte die Streamliste durchprobieren."

		# live= False verhindert Streamuhrzeit (Klemmer bei einigen Streams) 
		PlayVideo(url=url, title=title, thumb=img, Plot=Plot, live="false")
		xbmc.sleep(500)									# Klemmerschutz
		return
	
#---------------------------------------------------------------------------------------------------
# 21.10.2023 Url-Check hinzugefügt
#
def ARDSportgetEventlist(senderlist): 
	PLog("ARDSportgetEventlist:")
	PLog(senderlist)

	playlist = RLoad(PLAYLIST)							# lokale XML-Datei (Pluginverz./Resources)
	playlist = blockextract('<channel>', playlist)
	listname = "ARD Event Streams"
	mylist=""; 
	for i in range(len(playlist)):						# gewählte Channel extrahieren
		item = playlist[i] 
		name =  stringextract('<name>', '</name>', item)
		PLog(name)
		if name.startswith(listname):	
			mylist =  playlist[i]
			break
	PLog("mylist: " + mylist[:60])
	
	streamlist=[]; title_list=[]						# gewählte(n) Sender filtern
	itemlist = blockextract('<item>', mylist)
	for item in itemlist:
		title = stringextract('<title>', '</title>', item)
		# PLog(title)
		for sender in senderlist:
			if title.startswith(sender.strip()):
				PLog("title: %s, sender: %s" % (title, sender.strip()))
				url = stringextract('<link>', '</link>', item)
				img = stringextract('<thumbnail>', '</thumbnail>', item)
				if img.startswith("http") == False:			# extern od. lokal?
					img = R(img)
				streamlist.append("%s##%s##%s" % (title, url, img))
				 
				msg1 = "Stream-Check gestartet" 
				msg2 = "Sender: %s" % sender
				xbmcgui.Dialog().notification(msg1,msg2,img,2000,sound=False)

				if url_check(url, caller='ARDSportgetEventlist', dialog=False):
					title_list.append(title + " | Check: OK")
				else:
					title_list.append(title + " | Check: Error")
	PLog("title_list: " + str(title_list))	

	return streamlist, title_list

#---------------------------------------------------------------------------------------------------
# Untermenüs Tor des Monats
#	Buttons für weitere Untermenüs, Beiträge der Startseite
# 
def ARDSportMonatstor(title, path, img): 
	PLog("ARDSportMonatstor:")
	path_org=path
	img_org=img
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	title = u"Tor des Monats: [B]%s[/B]" % "Abstimmung"					# Menü Abstimmung
	tag = u"Tor des Monats: Hier gibt's Highlights, Clips und ausgewählte Höhepunkte aus der langen Geschichte dieser Rubrik."
	summ = "Folgebeiträge"
	path = "https://www.sportschau.de/tor-des-monats/abstimmung"
	title=py2_encode(title); path=py2_encode(path); 
	img=py2_encode(img); img_org=py2_encode(img_org); 
	fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" %\
		(quote(title), quote(path), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMonatstorSingle", fanart=img_org, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	
	
	title = u"Tor des Monats: [B]%s[/B]" % "Archiv"						# Menü Archiv
	tag = u"Seit über 40 Jahren wählen die Zuschauer der Sportschau ihr Tor des Monats. Über 500 Treffer sind bereits ausgezeichnet worden. Lassen Sie sich zurückversetzen in die Zeit von Netzer, Beckenbauer und Co. und schauen Sie sich die besten Tore seit 1971 nochmal an - mit vielen Videos."
	summ = "Folgebeiträge"
	path = "https://www.sportschau.de/tor-des-monats/archiv"
	title=py2_encode(title); path=py2_encode(path); 
	img = "https://images.sportschau.de/image/f0d59127-0aa3-4ac0-bf76-2c47cb5ff332/AAABgP4SFF4/AAABgPp7Db4/16x9-1280/tdm70er-sp-104.jpg"
	img=py2_encode(img); img_org=py2_encode(img_org); 
	fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" %\
		(quote(title), quote(path), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMonatstorSingle", fanart=img_org, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	
	
	title = u"Tor des Monats: [B]%s[/B]" % u"DIE BESTEN TORSCHÜTZEN"		# Menü DIE BESTEN TORSCHÜTZEN
	tag = u"In den 70ern war es Gerd Müller, in den 80ern Karl-Heinz-Rummenigge und in den 90ern Jürgen Klinsmann. Sie alle vereint eine besondere Auszeichung: In Ihrer Zeit führten sie die TdM-Rangliste an. 2005 betrat Lukas Podolski die Fußball-Bühne und überholte sie alle."
	summ = "Folgebeiträge"
	path = "https://www.sportschau.de/tor-des-monats/statistikspieler-sp-102.html"
	title=py2_encode(title); path=py2_encode(path); 
	img = "https://images.sportschau.de/image/cab85e31-6758-422c-8848-86684d5de288/AAABgP63Crc/AAABgPp7Db4/16x9-1280/statistikspieler-sp-100.jpg"
	img=py2_encode(img); img_org=py2_encode(img_org); 
	fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" %\
		(quote(title), quote(path), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportMonatstorSingle", fanart=img_org, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)	


	#-----------------------------------------							# Beiträge der Startseite
	page = ARDSportLoadPage(title, path_org, "ARDSportMonatstor")
	if page == '':
		return
	
	cnt = ARDSportMedia(li, title, page)
	if cnt == 0:								# Verbleib in Liste
		return		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#---------------------------------------------------------------------------------------------------
# Einzelnes Untermenü zu Tor des Monats
# 
def ARDSportMonatstorSingle(title, path, img): 
	PLog("ARDSportMonatstorSingle:")
	
	li = xbmcgui.ListItem()
	
	page = ARDSportLoadPage(title, path, "")
	if page == '':
		return
	
	base = "https://www.sportschau.de"
	if path.endswith("/abstimmung"):
		li = home(li, ID='ARD')						# Home-Button
		cnt = ARDSportMedia(li, title, page)
	if path.endswith("/archiv"):	
		items = blockextract('data-v="', page)		# Sliderboxen je Jahrzehnt	
		PLog("archiv_or_statistikspieler")
		PLog(len(items))
		for item in items:
			ARDSportSlider(li, item, skip_list=[], img='')		# -> json-extract
	if path.endswith("/statistikspieler-sp-102.html"):
		items = blockextract('class="teaser-xs__link"', page)			
		PLog(len(items))
		for item in items:
			url = base + stringextract('href="', '"', item)
			topline = stringextract('__topline">', '</', item)
			title = stringextract('__headline">', '</', item)	
			summ = stringextract('__shorttext">', '</', item)	
			title=repl_json_chars(title); summ=repl_json_chars(summ);
			title=cleanhtml(title)
			title=title.strip(); summ=summ.strip() 
			title_org=title
			title = "%s: [B]%s[/B]" % (topline, title)		
			img = stringextract('src="', '"', item)
			tag = u"Statistik: %s\n ohne Video, ohne Audio" % title_org
		
			PLog("Satz13_pic:")
			PLog(title); PLog(url); PLog(img); PLog(summ[:80]);
			tag = "weiter zum Beitrag %s" % title
			Plot = summ
			title=py2_encode(title); url=py2_encode(url);
			img=py2_encode(img); Plot=py2_encode(Plot);
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(url), 
				quote(title), quote(img), quote_plus(Plot))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportSliderSingle", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag)			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#---------------------------------------------------------------------------------------------------
# Tabellen
# frühere Jahre <- ARDSportTabellenArchiv
# 
def ARDSportTabellen(title, logo, path, year=""): 
	PLog("ARDSportTabellen: " + path)
	PLog(title); PLog(year)
	title_org=title; path_org=path
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	if "1. Bund" in title:
		cacheID="TabBund1"
	else:
		cacheID="TabBund2"	
			
	page = ARDSportLoadPage("Tabelle", path, func="ARDSportTabellen", cacheID=cacheID)
	if page == '':
		return
	try:	
		summ = re.search(r'<title>(.*?)</title>', page).group(1)
	except:
		summ=""
	summ = "[B]%s[/B]\n\nSpalten-Info: Rang [Punkte | Tore (Tor-Diff.) | Spiele] Mannschaft" % summ
	
	# Tab-Format (11): Tendenz | Rang | Icon| Team	| Sp.|S|U|N	| Tore | Diff. | Punkte
	# Verwendung: Icon | Rang | Punkte |Tore | Diff. | Spiele
	
	base = "https://www.sportschau.de"
	page = stringextract("<!--start module standing", "<!--end module standing", page)
	tr_blk = blockextract("<tr ", page)				# Zeilen
	PLog("lines: %d" % len(tr_blk))
	try:
		for tr in tr_blk:
			#PLog(tr)
			td_blk = blockextract("<td ", tr)			# Spalten
			PLog("columns: %d" % len(td_blk))
			PLog("column_1: " + td_blk[0])
			path		= re.search(r'href="(.*?)"><img', tr).group(1)	# Pfad -> Team
			path		= base + path
			td_img		= re.search(r'src="(.*?)"', tr).group(1)	# Icon-Url
			td_team		= re.search(r'title="(.*?)"', tr).group(1)	# Mannschaft
			td_rank 	= re.search(r'rank">(.*?)<', tr).group(1)	# Rang
			td_pts 		= re.search(r'points">(.*?)<', tr).group(1)	# Punkte
			
			td_goals 		= re.search(r'goaldiff">(.*?)<', tr).group(1)	# Tore
			td_diff 		= re.search(r'difference">(.*?)<', tr).group(1)	# Tor-Differenz
			td_match 		= re.search(r'played">(.*?)<', tr).group(1)	# Spiele
			
			points = "[%s | %s (%s) | %s]" % (td_pts, td_goals, td_diff, td_match)
			title = u"[B]%4s[/B] %24s %4s[B]%s[/B]" % (td_rank, points, " ", td_team)
			tag = u"[B]Platz %s: %s[/B]" % (td_rank, td_team)
			summ=""
			if year:
				summ = "diese Tabelle: [B]%s[/B]" % (year)
				
			PLog("Satz12_title: %s" % title); PLog(td_img)
			tag = u"Klick für die aktuelle Teamübersicht von  %s" % td_team			
			logo=py2_encode(logo); path=py2_encode(path)
			fparams="&fparams={'title': '%s', 'path': '%s', 'logo': '%s'}" % (title_org, quote(path), td_img)
			addDir(li=li, label=title, action="dirList", dirID="ARDSportTabellenTeam", fanart=logo, thumb=td_img, 
				fparams=fparams, tagline=tag,  summary=summ)	
				
	except Exception as exception:
		PLog("table_error: " + str(exception))
	
	now = datetime.datetime.now()
	thisyear = now.strftime("%Y")
		
	title = u"[B]Archiv[/B]: Tabellen seit 1964" 					# Archiv
	if "2. Bund" in title_org:
		title = u"[B]Archiv[/B]: Tabellen seit 2017"	
	tag = u"zurückliegende Tabellen %s" % title_org	
	summ = "Bildquelle: sportschau.de"
	if year:
		summ = "%s\n\ndiese Tabelle: [B]%s[/B]" % (summ, year)
					
	logo=py2_encode(logo); path_org=py2_encode(path_org)
	fparams="&fparams={'title': '%s', 'path': '%s', 'logo': '%s'}" % (title_org, quote(path_org), logo)
	addDir(li=li, label=title, action="dirList", dirID="ARDSportTabellenArchiv", fanart=logo, thumb=logo, 
		fparams=fparams, tagline=tag, summary=summ)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#---------------------------------------------------------------------------------------------------
# Archiv: Bundeslliga-Tabellen ab 1964
#  
def ARDSportTabellenArchiv(title, path, logo): 
	PLog('ARDSportTabellenArchiv: ' + path)
	title_org=title
	
	page, msg = get_page(path=path)					# ohne Cache
	page = stringextract("start module select--><", "<!--end module select-->", page)
	if page == '':
		return	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	base = "https://www.sportschau.de"
	tab_list = blockextract("<option value", page)
	PLog(tab_list[0])							# ../tabelle/">1963/1964</option>
	try:
		sort_list = sorted(tab_list,key=lambda x: int(re.search(r'/">(\d+)/', x).group(1)), reverse=True)	
	except Exception as exception:
		PLog("tab_list_error: " + str(exception))
		sort_list = tab_list
	
	for tab in sort_list:
		PLog(tab)
		href =  base + re.search(r'value="(.*?)"', tab).group(1)
		year = href.split("/")[-3]					# ../se2588/1966-1967/tabelle/
		title = "%s: [B]%s[/B]" % (title_org, year)
		PLog("href: " + href)
		
		title_org=py2_encode(title_org); logo=py2_encode(logo); href=py2_encode(href)
		fparams="&fparams={'title': '%s', 'logo': '%s', 'path': '%s', 'year': '%s'}" %\
			(title_org, quote(logo), quote(href), year)
		addDir(li=li, label=title, action="dirList", dirID="ARDSportTabellen", fanart=logo, thumb=logo, 
			fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#---------------------------------------------------------------------------------------------------
# Teamübersicht
#  
def ARDSportTabellenTeam(title, path, logo): 
	PLog('ARDSportTabellenTeam: ' + path)
	title_org=title
	
	page, msg = get_page(path=path)					# ohne Cache
	page = stringextract("start module person--><", "<!--end module person-->", page)
	if page == '':
		return	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	base = "https://www.sportschau.de"
	role_blk = blockextract('role">', page)	# Rollen
	try:
		for item in role_blk:
			tr_blk = blockextract("<tr ", item)
			PLog("lines: %d" % len(tr_blk))
			role = re.search(r'role">(.*?)<', item).group(1)		# z.B. Torwart
			for tr in tr_blk:
				#PLog(tr)
				td_blk = blockextract("<td ", tr)			# Spalten
				PLog("columns: %d" % len(td_blk))
				PLog("column_1: " + td_blk[0])
				# path		= re.search(r'href="(.*?)"><img', tr).group(1)		# Pfad -> Profil Person - nicht genutzt
				td_img		= re.search(r'src="(.*?)" alt', tr).group(1)		# Bild-Url
				td_name		= re.search(r'title="(.*?)"', tr).group(1)			# Name
				td_nr 		= re.search(r'shirtnumber-">(.*?)<', tr).group(1)	# Spieler-Nr.
				td_nation 	= re.search(r'country-name-">(.*?)<', tr).group(1)	# Nationalität
				td_birth 	= re.search(r'birthday">(.*?)<', tr).group(1)		# Geburtstag
				
				title = u"[B]%2s[/B] [B]%s[/B] (geb. %s)" % (td_nr, td_name, td_birth)
				tag = u"[B]%s[/B] | Herkunft: %s | Rolle: [B]%s[/B]" % (td_name, td_nation, role)
				summ = "Bildquelle: sportschau.de"
					
				PLog("Satz12_team: %s" % title); PLog(td_img)
				fparams="&fparams={}" 
				addDir(li=li, label=title, action="dirList", dirID="dummy", fanart=logo, thumb=td_img, 
					fparams=fparams, tagline=tag, summary=summ)				
				
	except Exception as exception:
		PLog("team_error: " + str(exception))

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#---------------------------------------------------------------------------------------------------
# Laden + Verteilen 
#
def ARDSportHub(title, path, img, Dict_ID=''): 
	PLog('ARDSportHub: ' + title)
	
	base = "https://www.sportschau.de"
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	if "Moderation" in title:
		page = ARDSportLoadPage(title, path, "ARDSportHub")
		if page == '':
			return
		items = blockextract('class="teaser__link"', page)			
		PLog(len(items))
		for item in items:
			url = stringextract('href="', '"', item)					
			if url.startswith("http") == False:
				url = base + url
				
			topline = stringextract('__topline">', '</', item)	# html-Bereich
			title = stringextract('__headline">', '</', item)	
			summ = stringextract('__shorttext">', '</', item)	
			title=repl_json_chars(title); summ=repl_json_chars(summ);
			title=title.strip(); summ=summ.strip() 
			summ = cleanhtml(summ)
			title = "%s: [B]%s[/B]" % (topline, title)		
				
			tag = "[B]Bilderstrecke[/B]" 
			func = "ARDSportBilder"
			if  item.find(">Bilder<") < 0:
				tag = "[B]ohne weitere Bilder[/B]" 
				func = "dummy"
			img = stringextract('src="', '"', item)
			if img == '':
				img = R(ICON_DIR_FOLDER)
			PLog("Satz12_pic:")
			PLog(title); PLog(url); PLog(img); PLog(summ[:80]);
			fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title), 
				quote(url), quote(img))
			addDir(li=li, label=title, action="dirList", dirID=func, fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)
				
	if "[B]Sliderbox" in title:									# einzelner Sliderbeitrag
		page = ARDSportLoadPage(title, path, "ARDSportHub")
		if page == '':
			return
		PLog("slider_from_Dict")
		teaser = Dict("load", Dict_ID)
		skip_list = []; cnt=0
		skip_list = ARDSportSlider(li, teaser, skip_list, img)		# -> addDir			
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#---------------------------------------------------------------------------------------------------
# Notification: keine Aktion
# verhindert nicht GetDirectory-Error 
def dummy(title="",path="",img=""):
	PLog("dummy:")
	icon = R(ICON_INFO)
	msg1 = "Hinweis:"
	msg2 = 'Button ohne Funktion'		
	if title:
		msg2 = title
	xbmcgui.Dialog().notification(msg1,msg2,icon,2000, sound=False)
	return

#---------------------------------------------------------------------------------------------------
# Webseite für Funktion func laden 
# falls cacheID leer, wird sie letztes path-Element (eindeutig!)
#
def ARDSportLoadPage(title, path, func, cacheID=""): 
	PLog('ARDSportLoadPage:')
	PLog('func: ' + func)
	CacheTime = 60*5							# 5 min.
	
	if cacheID == "":
		p = path.split("/")[-1]
		cacheID = "ARDSport_%s" % p
	
	page = Dict("load", cacheID, CacheTime=CacheTime)
	page=''
	if page == False or page == '':								# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		if page:
			Dict("store", cacheID, page) 						# Seite -> Cache: aktualisieren	
	if page == '':
		msg1 = "Fehler in %s" % func
		msg2 = 'Seite kann nicht geladen werden.'
		msg3 = msg
		MyDialog(msg1, msg2, msg3)
	
	return page	
	
#---------------------------------------------------------------------------------------------------
# 16.11.2024 Anpassung an Änderungen des WDR, Aufteilung der Startseite 
#	in Navigation und Liste der Videos/Audios.
#
def ARDSportStart(logo, burger=""): 
	PLog('ARDSportStart:')
	
	base = "https://www.sportschau.de"	
	page = ARDSportLoadPage("Startseite", base, "ARDSportStart")
	if page == '':
		return

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')										# Home-Button
	img = R(ICON_DIR_FOLDER)										# Burger-img's grauslich

	#---------------------------------------------------------------# Step 1: Button Hamburger-Menü, Videos+Audios
	# rechte Seite bis Subnavigationen 2. Ebene					
	if burger == "":
		title="Navigation"
		tag = u"Zum Hamburger-Menü der Startseite (1. Ebene)"
		fparams="&fparams={'logo': '%s', 'burger': 'true'}" % quote(logo)
		addDir(li=li, label=title, action="dirList", dirID="ARDSportStart", fanart=logo, thumb=img, 
			fparams=fparams, tagline=tag)

		ARDSportMedia(li, title, page)								# Videos + Audios der Startseite
	else:
	#---------------------------------------------------------------# Step 2: Hamburger-Menü aufklappen
		burger = stringextract('class="burger-navi-nav', 'burger-navi-nav__sublevel', page)
		items = blockextract("<a href=", burger, "</span>")
		skip_list = [u"Live & Ergebnisse", "Tor des Monats", "Livestreams",
					"Einstellungen"]
		
		PLog(len(items))
		for item in items:
			if "_submenulink" in item:									# Links zu Submenüs ausblenden
				continue

			path = base + stringextract('href="', '"', item)			# Folgeseiten hier ohne http				
			title = stringextract('title="', '"', item)
			title = title.replace(" aufrufen", "")
			title = unescape(title)
			title = "[B]%s[/B]" % title									# Bsp. Menüpunkt Paralympics

			skip=False
			for s in skip_list:
				if title.find(s) > 0:
					PLog("skip_title: " + title)
					skip=True
					break
			if skip:
				continue

			PLog("Satz9:")
			PLog(title); PLog(path); PLog(img);
			tag = "Folgeseiten"
			title=py2_encode(title); path=py2_encode(path); img=py2_encode(img);
			fparams="&fparams={'li': '', 'title': '%s', 'page': '', 'path': '%s'}" %\
				(quote(title), quote(path))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportMedia", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag)	
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------------------------------------------
# Livestreams der Sportschau
# Aufruf: ARDSportWDR
# 14.06.2024 Ausfilterung Videos für "Audiolivestreams der Sportschau"
#	in ARDAudioEventStreams
#
def ARDSportLive(title, skip_video=""): 
	PLog('ARDSportLive:')

	path = "https://www.sportschau.de/streams"
	page = ARDSportLoadPage(title, path, "ARDSportLive")
	if page == '':
		return

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
		
	items = blockextract('<picture class=', page)
	PLog(len(items))
	for item in items:
		data  = ARDSportgetPlayer(item)
		if data:
			player,live,title,mp3_url,stream_url,img,tag,summ,Plot = ARDSportMediaPlayer(li, data)
			title=repl_json_chars(title)
			PLog("player_typ: " + player)
			
			title=py2_encode(title); Plot=py2_encode(Plot)
			if player == "video" and not skip_video:
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(stream_url), 
					quote(title), quote(img), quote_plus(Plot))
				addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
					tagline=tag, summary=summ, mediatype='video')	
			if player == "audio":
				if live:
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
						quote(title), quote(img), quote_plus(Plot))
					addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=img, thumb=img, fparams=fparams, 
						tagline=tag, mediatype='music')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# holt Playerdaten bei data-v="..
def ARDSportgetPlayer(item):
	PLog("ARDSportgetPlayer:")

	pos1=item.find('{'); pos2=item.rfind('}')
	PLog(pos1); PLog(pos2)
	data = item[pos1:pos2+1]
	
	if data:
		data = unescape(data)
		data = (data.replace('\\"','*').replace('<strong>','[B]').replace('</strong>','[/B]'))

	PLog(py2_decode(data)[:80])
	return data	
	
#----------------------------------------------------------------
# aktuelle LIVESTREAMS + Netcast-Audiostreams-Liste von sportschau.de
# Aufrufer: ARDAudioEventStreams
# aktuelle Livestreams: ../audio/index.html
# Alle Netcast-Streams: ../sportimradio/audiostream-netcast-uebersicht-100.html
# ab Juni 2022 beide Webseiten ähnlich
def ARDSportAudioStreams(title, path, img, cacheID):
	PLog('ARDSportAudioStreams:')
	
	page = ARDSportLoadPage(title, path, "ARDSportAudioStreams", cacheID)
	if page == '':
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	cnt = ARDSportMedia(li, title, page)
	if cnt == 0:												# Verbleib in Liste
		return		
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------------------------------------------
# Auswertung mediaplayer-Klassen (quoted:data-v=..)
# Aufrufer ARDSportWDR, ARDSportAudioStreams
# 05.08.2024 Nutzung TagesschauXL.get_content_json
#
def ARDSportMedia(li, title, page, path=""): 
	PLog('ARDSportMedia: ' + title)
	title_org=title
	base = "https://www.sportschau.de"
	import resources.lib.TagesschauXL as TagesschauXL	
	
	if path:												# Bsp. sportschau.de/olympia
		page = ARDSportLoadPage(title, path, "ARDSportMedia")
		if page == '':
			return
	eof=False
	if li == "":
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD')						# Home-Button
		eof=True
		
	content =  blockextract('data-v=', page, '</div>')	
	PLog("content: %d" % len(content))

	if len(content) == 0:
		icon = R("ard-sportschau.png")
		msg1 = u"%s:" % title
		msg2 = u'keine Videos/Audios/Bilder gefunden'
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
		return 0 
				
	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
		
	cnt = 0; url_list=[]
	for item in content:
		PLog(item[:80])

		typ,av_typ,title,tag,summ,img,stream = TagesschauXL.get_content_json(item)
		if typ == False:											# jsonloads_error
			continue
		if stream in url_list:										# Doppel möglich (Tour de France Femmes)
			continue
		url_list.append(stream)
				
		title=py2_encode(title); stream=py2_encode(stream); 
		summ=py2_encode(summ); img=py2_encode(img); 
			
		if typ == "audio":											# Audio
			ID='ARD'
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote_plus(summ), ID)
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
		
		live=""
		if SETTINGS.getSetting('pref_startlist') == 'true':			# Blockade verhindern, s. Kopf
			live="true"		
		if typ == "video":											# Video	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': '%s'}" %\
				(quote(stream), quote(title), quote(img), quote_plus(summ), live)
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)			
		cnt = cnt + 1
		
	if cnt == 0: 
		msg1 = u'weder Videos noch Audios:'
		msg2 = title_org
		icon = ICON_MAINXL		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("%s: %s" % (msg1, msg2))
		return
	
	if eof:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	return cnt

#----------------------------------------------------------------
# Auswertung Mediaplayerdaten
# 24.07.2022 Anpassung für Tor des Monats ("video/mp4" in url)
#
def ARDSportMediaPlayer(li, item_data): 
	PLog('ARDSportMediaPlayer:')
	
	player=''; live=False; title='';  mp3_url=''; stream_url=''; 
	img=''; verf=''; tag=''; summ=''; Plot=''; 

	player = stringextract('playerType":"', '"', item_data)		# audio, video
	media = stringextract('streams":', '"meta"', item_data)		# für video dash.mpd, m3u8 + ts
	PLog("media: " + media[:80]); 
	if player == "audio":
		mp3_url = stringextract('url":"', '"', media)			# 1 x mp3
	else:
		urls = blockextract('url":', media)
		for url in urls:										# erste: höchste Auflösung
			if "index.m3u8" in url or "master.m3u8" in url or "video/mp4" in url:
				stream_url = stringextract('url":"', '"', url)
				break
	
	title = stringextract('],"title":"', ',"', item_data)		# 29.05.2024 nach Bildtitel
	title=decode_url(title); title=repl_json_chars(title);
	title=title.replace('}', '') 
	
	duration = stringextract('durationSeconds":"', '"', item_data)
	if duration == '':
		dur = stringextract('content_duration":', ',', item_data) # Altern. außerhalb media (int, milli-secs)
		PLog("dur_raw: " + dur)
		try:
			dur = int(dur)
			duration = str(int(dur / 1000))
		except:
			duration=""
	PLog("duration: " + duration); 
	duration = seconds_translate(duration)
		
	imgs = blockextract('"minWidth":', item_data, "}")
	if len(imgs) > 0:
		img = stringextract('value":"', '"', imgs[-1])			# letztes=größtes
		if "." not in img.split("/")[-1]:						# Kodi braucht Extension
			img = img + ".png"
	mode = stringextract('_broadcasting_type":"', '"', item_data)
	if mode == "live":
		live=True
	
	TimeDate=''; tag='';

	if duration:
		if duration == "0 sec":
			duration = "unbekannt"
		
	avail = stringextract('av_original_air_time":"', '"', item_data)
	if avail:
		verf = time_translate(avail, add_hour=False, day_warn=True)
	
	chapter = stringextract('chapter1":"', '"', item_data)
	creator = stringextract('creator":"', '"', item_data)
	genre = stringextract('_genre":"', '"', item_data)
	geo = stringextract('languageCode":"', '"', item_data)
	if geo:
		geo = "Geoblock: %s" % up_low(geo)
	else:
		geo = "Geoblock: NEIN"
	
	if player == "audio":
		tag = "Audio"
	else:
		tag = "Video"
	if live:
		tag = "%s-Livestream" % tag
	tag = "[B]%s[/B]" % tag
	PLog("duration: " + duration)
	if live == False and duration:
		tag = "%s | Dauer %s" % (tag, duration)
	if verf:
		tag = u"%s | Verfügbar ab [B]%s[/B]" % (tag, verf)	
		
	tag = "%s\n%s | %s | %s | %s" % (tag, chapter, creator, genre, geo)

	if summ:
		tag = "%s\n\n%s" % (tag, summ)
	Plot = tag.replace("\n", "||")
	
	PLog("Satz31:")
	PLog(player); PLog(live); PLog(title); PLog(mp3_url); PLog(stream_url); PLog(avail);
		
	return player, live, title, mp3_url, stream_url, img, tag, summ, Plot  

#---------------------------------------------------------------------------------------------------
# Für Seiten mit nur einheitlichen Blöcken
# Aufrufer: ARDAudioEventStreams (Audiostreams, Netcast-Audiostreams) 
# 
def ARDSportNetcastAudios(title, path, img, cacheID):
	PLog('ARDSportNetcastAudios:')
	
	page = ARDSportLoadPage(title, path, "ARDSportNetcastAudios", cacheID)
	if page == '':
		return
	
	items = blockextract('<picture class=', page)							# Kombi?: ARDSportLive (Videos + Audios)
	PLog(len(items))
	if  len(items) == 0:
		icon = img
		msg1 = u"z.Z. keine Beiträge"
		msg2 = title		
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000, sound=False)
		return
	
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	for item in items:
		data  = ARDSportgetPlayer(item)
		PLog(data[:60])
		if data:
			player,live,title,mp3_url,stream_url,img,tag,summ,Plot = ARDSportMediaPlayer(li, data)
			PLog("Satz12_single:")
			PLog(player); PLog(live); PLog(title); PLog(mp3_url); PLog(stream_url);   
			PLog(img); PLog(summ[:80]);
			title=py2_encode(title); mp3_url=py2_encode(mp3_url); img=py2_encode(img);
			tag=py2_encode(tag); Plot=py2_encode(Plot);
			
			if player == "audio":												# bei Bedarf für Video ergänzen
				if live:														# netcast Livestream
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
						quote(title), quote(img), quote_plus(Plot))
					addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=img, thumb=img, fparams=fparams, 
						tagline=tag, mediatype='music')	
				else:															# Konserve
					ID="ARD"													# ID Home-Button
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(mp3_url), 
						quote(title), quote(img), quote_plus(Plot), ID)
					addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
						fparams=fparams, tagline=tag)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# Auswertung Slider-Beiträge mit json-Bereich
#
def ARDSportSlider(li, item, skip_list, img=''): 
	PLog('ARDSportSlider:')
	PLog(item[:80])
	base = "https://www.sportschau.de"
	player=''; live=False; title='';  mp3_url=''; stream_url=''; 
	img=''; tag=''; summ=''; Plot='';
	
	cont  = ARDSportgetPlayer(item)						# json-Inhalt zum Player
	content = blockextract('"teaserUrl"', cont)
	PLog(len(content))
	#PLog(content)	# Debug
	
	allow_list = ["AUDIO", "VIDEO", "PODCAST",			# Web: groß-/klein-Mix
				"LIVESTREAM"]
	for rec in 	content:
		label = stringextract('label":"', '"', rec)		# audio, video, podcast

		url = stringextract('teaserUrl":"', '"', rec)
		if url.startswith('http') == False:
			url = base + url
		topline = stringextract('topline":"', '"', rec)
		title = stringextract('headline":"', '"', rec)
		if title in skip_list:
			PLog("skip_title: " + title)
			continue
		skip_list.append(title)
		
		img = stringextract('imageUrl":"', '"', rec)
		if img == '':
			pos = rec.find('minWidth":640')				# Altern. minWidth 256 - 960
			if pos > 0:
				img = stringextract('value":"', '"', rec[pos:])
		alt = stringextract('alttext":"', '"', rec)
		cr = stringextract('copyright":"', '"', rec)
		
		summ = "[B]%s[/B] | %s | %s "  % (topline, alt, cr)
	
		allow=False; live=False
		for item in allow_list:							# Abgleich label-Typen
			if item in up_low(label) or '"Tor des Monats' in rec: # Tor des Monats Sätze ohne label
				if "LIVESTREAM" in item:
					live=True
				allow=True; break				
				
		PLog("Satz12_slider:")
		PLog(title); PLog(label); PLog(allow); PLog(topline);
		PLog(url); PLog(img);PLog(alt);PLog(cr);
		title=py2_encode(title); url=py2_encode(url);
		img=py2_encode(img); Plot=py2_encode(Plot);
		
		if allow:
			tag = "weiter zum [B]%s[/B]-Beitrag" % label
			if live:
				tag = tag.replace("-Beitrag", "")
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(url), 
				quote(title), quote(img), quote_plus(Plot))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportSliderSingle", fanart=img, thumb=img, fparams=fparams, 
				tagline=tag)			
		else:											# nur Textinhalte
			tag = "[B]ohne Videos, Audios, Bilder[/B]\nMehr auf sportschau.de.."
			title = "[COLOR grey]%s[/COLOR]" % title
			PLog("Satz12_slider_text: %s" % title)
			fparams="&fparams={}" 
			addDir(li=li, label=title, action="dirList", dirID="dummy", fanart=img, thumb=img, fparams=fparams, 
				tagline=tag, summary=summ)				
		
	return skip_list

#----------------------------------------------------------------
# einzelner Slider für ARDSportSlider
# 24.07.2022 Anpassung für Tor des Monats (mehrere mediaplayer-Sätze)
#	
def ARDSportSliderSingle(url, title, thumb, Plot, firstblock=False): 
	PLog('ARDSportSliderSingle: ' + title)
	PLog(url); PLog(firstblock);
	cacheID=url.split("/")[-1]

	page = ARDSportLoadPage(title, url, "ARDSportSliderSingle", cacheID)
	if page == '':
		return

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	base = "https://www.sportschau.de"
	mediatype=""
	items=[]
	if "/tor-des-monats/" in url:				# mehrere Beiträge "Tore des Monats"
		items = blockextract('class="mediaplayer', page, '"MediaPlayer"')
		PLog("mediaplayer_items: %d" % len(items))
		if len(items) == 0:						# Beiträge erst auf Folgeseiten
			items = blockextract('<div class="teaser__media">', page)
			PLog("teaserlink_items: %d" % len(items))
			base = "https://www.sportschau.de"
			for item in items:
				if item.find('"teaser__link"') < 0:
					continue

				url = base + stringextract('href="', '"', item)
				img = stringextract('src="', '"', item)
				if img == '':
					img = thumb
				topline = stringextract('__topline">', '</', item)
				title = stringextract('__headline">', '</', item)
				if title == '':
					continue
					
				summ = stringextract('__shorttext">', '</', item)	
				title=repl_json_chars(title); summ=repl_json_chars(summ);
				title=cleanhtml(title)
				title=title.strip(); summ=summ.strip() 
				summ = cleanhtml(summ)
				tag = "[B]%s[/B]" % topline
					
				PLog("Satz32:")
				PLog(title); PLog(url);
				url=py2_encode(url); title=py2_encode(title); 
				thumb=py2_encode(thumb); Plot=py2_encode(Plot);
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'firstblock': 'True'}" %\
					(quote(url), quote(title), quote(thumb), quote_plus(Plot), )
				addDir(li=li, label=title, action="dirList", dirID="ARDSportSliderSingle", fanart=thumb, thumb=img, 
					fparams=fparams, tagline=tag, summary=summ)		
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			return									# erford. für Abschluss
		else:										# Einzelbeitrag "Tore des Monats"					
			if firstblock:
				if 'leider nicht im Internet' in page:
					icon = R(ICON_INFO)
					msg1 = u"Beitrag gesperrt"
					msg2 = u"im Internet nicht verfügbar"
					xbmcgui.Dialog().notification(msg1,msg2,icon,2000, sound=False)
					PLog(msg2)
					return
				PLog("firstblock: " + str(items[:1])[:60] )
			if 'class="v-instance" data-v="' in page:
				items = blockextract('class="v-instance" data-v="', page, '"MediaPlayer"')	# erster json-Bereich
				PLog(len(items))
				item = items[0]
				data  = ARDSportgetPlayer(item)			# json-Inhalt
				player,live,title,mp3_url,stream_url,img,tag,summ,Plot = ARDSportMediaPlayer(li, data)
				PLog("Satz32_2:")
				title=py2_encode(title); mp3_url=py2_encode(mp3_url); img=py2_encode(img);
				tag=py2_encode(tag); Plot=py2_encode(Plot);
				if player == "video":
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(stream_url), 
						quote(title), quote(img), quote_plus(Plot))
					addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
						tagline=tag, summary=summ, mediatype='mediatype')
	
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			return										# erford. für Abschluss		
			
	else:	
		item = stringextract('class="v-instance" data-v="', '"MediaPlayer"', page)	# erster json-Bereich
		items.append(item) 
		
	if len(items) == 0:									# z.B. Verweis auf https://www.zdf.de/live-tv
		icon = R("ard-sportschau.png")
		msg1 = u"%s:" % title
		msg2 = u'Quelle nicht gefunden/verfügbar'
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
		return 0 
	
	PLog("Slideritems: %d" % len(items))
	for item in items:
		PLog(item[:80])
		if item.find('data-v="') < 0:					# Playerdaten auf Folgeseite?
			PLog("follow_up:")
			path = base + stringextract('href="', '"', item)
			page, msg = get_page(path)
			item = stringextract('class="mediaplayer', '"MediaPlayer"', page)
			PLog(item[:60])	
		if item.find('data-v="') > 0:
			data  = ARDSportgetPlayer(item)				# json-Inhalt zum Player	
			player,live,title,mp3_url,stream_url,img,tag,summ,Plot = ARDSportMediaPlayer(li, data)
		else:
			PLog('no_data-v')
			continue
		
		if player == "audio":
			ID="ARD"													# ID Home-Button
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(Plot), ID)
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag)
		if player == "video":
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(stream_url), 
				quote(title), quote(img), quote_plus(Plot))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
				tagline=tag, mediatype='mediatype')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ---------------------------------------- Ende ARD Sportschau.de ---------------------------------
####################################################################################################
# Aufrufer: Main
def SearchUpdate(title):		
	PLog('SearchUpdate:')
	li = xbmcgui.ListItem()

	ret = updater.update_available(VERSION)	
	#PLog(ret)
	if ret[0] == False:		
		msg1 = 'Updater: Github-Problem'
		msg2 = 'update_available: False'
		PLog("%s | %s" % (msg1, msg2))
		MyDialog(msg1, msg2, '')
		return li			

	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1
	
	summ = ret[3]			# Changes, cleanSummary: "\n" -> "|"  
	tag = ret[4]			# tag, Bsp. 029
	
	# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
	url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
	PLog(int_lv); PLog(int_lc); PLog(latest_version); PLog(summ);  PLog(url);
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Addon vorher sichern!)			
		title = 'Update vorhanden - jetzt installieren'
		summary = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
		PLog(type(summary));PLog(type(latest_version));

		tagline = cleanhtml(summ)
		thumb = R(ICON_UPDATER_NEW)
		url=py2_encode(url);
		fparams="&fparams={'url': '%s', 'ver': '%s'}" % (quote_plus(url), latest_version) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary, 
			tagline=summ)
			
		title = 'Update abbrechen'
		summary = 'weiter im aktuellen Addon'
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_UPDATER_NEW), 
			thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
	else:	
		title = 'Addon ist aktuell | weiter zum aktuellen Addon'
		summary = 'Addon Version ' + VERSION + ' ist aktuell (kein Update vorhanden)'
		summ = summ[:200]				# begrenzen
		tagline = "%s.. | Mehr in changelog.txt" % summ
		thumb = R(ICON_OK)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_OK), 
			thumb=R(ICON_OK), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
#							beta.ardmediathek.de / www.ardmediathek.de
#
#					zusätzliche Funktionen für die Betaphase ab Sept. 2018
#					ab Jan 2019 wg. Scrollfunktion haupts. Nutzung der Classic-Version
#					ab April 2019 hier allein Classic-Version - Neu-Version als Modul
#					ab Juni 2021 nach Wegfall Classic hier entfernt: ARDStart, ARDStartRubrik,
#						SendungenAZ, SearchARDundZDF, Search (ARD Classic + Podcast Classic), -
#						gesamt s. changelog.txt.
#						
####################################################################################################

#----------------------------------------------------------------  
# Vorstufe von Search - nur in Kodi-Version.
#	blendet Tastatur ein und fragt Suchwort(e) ab.
#	
def get_query(channel='ARD'):
	PLog('get_query:'); PLog(channel)
	query = get_keyboard_input()			# Modul util
	if  query == None or query.strip() == '':
		return ""
	
	if channel == 'ARD' or channel == 'ARDundZDF':				
		if '|' in query:		# wir brauchen | als Parameter-Trenner in SinglePage
			msg1 = 'unerlaubtes Zeichen in Suchwort: |'
			MyDialog(msg1, '', '')
			return ""
				
		query_ard = query.strip()
		query_ard = query_ard.replace(' ', '+')	# Leer-Trennung = UND-Verknüpfung bei Podcast-Suche 
		
	if channel == 'ZDF' or channel == 'ARDundZDF':				
		query_zdf =query.strip()					# ZDF-Suche
		query_zdf = query_zdf.replace(' ', '+')		# Leer-Trennung bei ZDF-Suche mit +
		
	if channel == 'ARD':	
		return 	query_ard
	if channel == 'ZDF':	
		return 	query_zdf
	if channel == 'ARDundZDF':						# beide queries zusammengesetzt				
		query = "%s|%s" % (query_ard, query_zdf)							
		PLog('query_ARDundZDF: %s' % query);
		return	query
	if channel=='ARD Audiothek' or channel=='phoenix':	# nur strip, quoting durch Aufrufer
		return 	query.strip()
			
#---------------------------------------------------------------- 
#  Search_refugee - erforderlich für Refugee Radio (WDR) - nur
#		Podcasts Classics - 03.06.2021  entfernt
#---------------------------------------------------------------- 

####################################################################################################
# 03.06.2021 entfernt (Classic-Version eingestellt): PODMore							
####################################################################################################
####################################################################################################
# 14.11.2023 entfernt (obsolet durch Merkliste): PodFavoritenListe							
####################################################################################################
####################################################################################################
# 03.06.2021 Classic-Funktionen entfernt: BarriereArmARD, PageControl, SinglePage,
#	SingleSendung
####################################################################################################

#-----------------------
# test_downloads: prüft ob curl/wget-Downloads freigeschaltet sind + erstellt den Downloadbutton
# high (int): Index für einzelne + höchste Video-Qualität in download_list
# 04.01.2021 Anpassung Trennz. Stream_List (Bsp. Parseplaylist, StreamsShow)
# 23.04.2021 Durchreichen von sub_path (Untertitel), leer für mp3-files
def test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high, sub_path=''):  
	PLog('test_downloads:')
	PLog('summary_org: ' + summary_org)
	PLog('title_org: ' + title_org)
	PLog('tagline_org: ' + tagline_org)

	PLog(SETTINGS.getSetting('pref_use_downloads')) 			# Voreinstellung: False 
	if check_Setting('pref_use_downloads') == False:			# einschl. Test Downloadverzeichnis
		return

	if SETTINGS.getSetting('pref_show_qualities') == 'false':	# nur 1 (höchste) Qualität verwenden
		download_items = get_bestdownload(download_list)
	else:	
		download_items = download_list							# ganze Liste verwenden
	# PLog(download_items)
		
	i=0
	for item in download_items:
		PLog(item)
		item = item.replace('**', '|')							# 04.01.2021 Korrek. Trennz. Stream_List
		quality,url = item.split('#')
		PLog(url); PLog(quality); PLog(title_org)
		if url.find('.m3u8') == -1 and url.find('rtmp://') == -1:
			# detailtxt =  Begleitdatei mit Textinfos zum Video / Podcast:				
			detailtxt = MakeDetailText(title=title_org,thumb=thumb,quality=quality,
				summary=summary_org,tagline=tagline_org,url=url)
			v = 'detailtxt'+str(i)
			Dict('store', v, detailtxt)							# detailtxt speichern 
			if url.endswith('.mp3'):		
				Format = 'Podcast ' 			
			else:	
				Format = 'Video '								# .mp4, .webm, .. 
			if url.endswith('.aac') and "/event" in url:		# z.B. liveradio.swr.de
				msg1 = u"vermutlich Livestream - Download nicht möglich!" 
				msg2 = title_org
				MyDialog(msg1, msg2, "")
				return
			
			#lable = 'Download ' + Format + ' | ' + quality
			lable = 'Download' + ' | ' + quality				# 09.01.2021 Wegfall Format aus Platzgründen 
			dest_path = SETTINGS.getSetting('pref_download_path')
			tagline = Format + 'wird in ' + dest_path + ' gespeichert' 									
			summary = 'Sendung: ' + title_org
			key_detailtxt='detailtxt'+str(i)
			title_par = title_org.replace("\n", "||")			# Bsp. \n s. yt_get
			
			url=py2_encode(url); title_par=py2_encode(title_par); sub_path=py2_encode(sub_path);
			fparams="&fparams={'url': '%s', 'title': '%s', 'dest_path': '%s', 'key_detailtxt': '%s', 'sub_path': '%s'}" % \
				(quote(url), quote(title_par), dest_path, key_detailtxt, quote(sub_path))
			addDir(li=li, label=lable, action="dirList", dirID="DownloadExtern", fanart=R(ICON_DOWNL), 
				thumb=R(ICON_DOWNL), fparams=fparams, summary=summary, tagline=tagline, mediatype='')
			i=i+1					# Dict-key-Zähler
	
	return li
	
#---------------------------
# Aufruf test_downloads (Setting pref_show_qualities=false)
# ermittelt Stream mit höchster Auflösung
#
def get_bestdownload(download_list):
	PLog('get_bestdownload:')
	PLog("download_list:" + str(download_list))
	download_items=[]

	# Filterung Arte-Streams (Sprachen, UT, ..). Bei leerer Liste
	#	erfolgt Abgleich mit download_list unabhängig von Sprachen
	my_list=[]
	pref = SETTINGS.getSetting('pref_arte_streams')
	pref = py2_decode(pref)
	PLog(u"pref: " + pref)
	
	for item in download_list:
		item = py2_decode(item)
		lang = stringextract('[B]', '[/B]', item)
		if item.find(u"//arteptweb") >= 0 and item.find(pref) >= 0:
			if lang == pref: 		# Zusätze berücks. z.B. UT Deutsch	
				my_list.append(item)				
	PLog(len(my_list))
	
	if len(my_list)== 0:							# Arte Fallback Deutsch
		for item in download_list:
			item = py2_decode(item)
			lang = stringextract('[B]', '[/B]', item)
			if u"//arteptweb" in item and lang == u"Deutsch":
				my_list.append(item)				
	PLog(len(my_list))
				
	if len(my_list) > 0:
		download_list = my_list	

	# Full HD (ARD, ZDF): 1920x1080 (funk)
	# high_list: absteigende Qualitäten in diversen Erscheinungen
	high_list =  ["3840x2160", "Full HD", "1920x1080", "1280x1080", "5000kbit",
					"1280x", "veryhigh", "960x720", "960x", "640x540", "640x360"]
	for hl in high_list:					# Abgleich mit Auslösungen
		for item in download_list:
			#PLog("hl: %s | %s" % (hl, item))
			if hl in item:
				download_items.append(item)
				PLog("found1: " + item)
				return download_items

	download_items.append(download_list[0])		# Fallback 1. Stream (ARD, ZDF OK)
	return download_items
	
#-----------------------
# Textdatei für Download-Video / -Podcast -
# 05.07.2020 verlagert nach util:
#def MakeDetailText(title, summary,tagline,quality,thumb,url):	
	
####################################################################################################
# Verwendung von curl/wget mittels Phytons subprocess-Funktionen
# 30.08.2018:
# Zum Problemen "autom. Wiedereintritt" - auch bei PHT siehe Doku in LiveRecord.
# 20.12.2018 Problem "autom. Wiedereintritt" in Kodi nicht relevant.
# 20.01.2020 der Thread zum internen Download wird hier ebenfalls aufgerufen 
# 27.02.2020 Code für curl/wget-Download entfernt
# 30.06.2020 Angleichung Dateiname (Datum) an epgRecord (Bindestriche entf.)
# 23.03.2021 erweitert um Download der Untertitel (sub_path), leer für mp3-files 
# 02.04.2021 Var PIDcurl entfernt (für Kodi obsolet)
# 25.09.2021 Fix Security-Issue Incomplete URL substring sanitization (CodeQL-
#				Check)
#
def DownloadExtern(url, title, dest_path, key_detailtxt, sub_path=''):  
	PLog('DownloadExtern: ' + title)
	PLog(url); PLog(dest_path); PLog(key_detailtxt)
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	
	if 	SETTINGS.getSetting('pref_generate_filenames') == 'true':	# Dateiname aus Titel generieren
		max_length = 255 - len(dest_path)
		dfname = make_filenames(title.strip(), max_length) 
	else:												# Bsp.: Download_20161218_091500.mp4  oder ...mp3
		now = datetime.datetime.now()
		mydate = now.strftime("%Y%m%d_%H%M%S")	
		dfname = 'Download_' + mydate 
	
	if '?file=.mp3' in url:								# Livestream aus Audiothek?
		msg1 = "Achtung: das ist vermutlich ein Livestream!"
		msg2 = "Download trotzdem durchführen?"
		msg3 = "Ein Abbruch des Downloads ist im Addon nicht möglich!"
		ret=MyDialog(msg1, msg2, msg3, ok=False, yes='JA')
		if ret  == False:
			return		
	
	suffix=''
	if url.endswith('.mp3') or url.endswith('.m4a'):	# 25.10.2024 Podcasts .m4a 
		suffix = url[-4:]		
		dtyp = 'Podcast '
	else:												# .mp4 oder .webm	
		dtyp = 'Video '
		if 'googlevideo.com/' in url:					# Youtube-Url ist ohne Endung (pytube-Ausgabe)
			suffix = '.mp4'	
		if url.endswith('.mp4') or '.mp4' in url:		# funk: ..920x1080_6000.mp4?hdnts=				
			suffix = '.mp4'		
		if url.endswith('.webm'):				
			suffix = '.webm'		
		
	if suffix == '':
		msg1='DownloadExtern: Problem mit Dateiname. Video: %s' % title
		PLog(msg1)
		MyDialog(msg1, '', '')
		return li

	title = dtyp + 'curl/wget-Download: ' + title
	textfile = dfname + '.txt'
	
	dfname = dfname + suffix							# suffix: '.mp4', '.webm', oder '.mp3', 'm4a'
	
	pathtextfile = os.path.join(dest_path, textfile)	# kompl. Speicherpfad für Textfile
	PLog(pathtextfile)
	detailtxt = Dict("load", key_detailtxt)				# detailtxt0, detailtxt1, ..
	PLog(detailtxt[:60])
	
	PLog('convert_storetxt:')
	dtyp=py2_decode(dtyp); dfname=py2_decode(dfname); detailtxt=py2_decode(detailtxt)
	storetxt = 'Details zum ' + dtyp +  dfname + ':\r\n\r\n' + detailtxt
	
	PLog(sys.platform)
	fulldestpath = os.path.join(dest_path, dfname)	# wie curl_fullpath s.u.
									# Untertiteldatei hinzufügen:
	PLog(dtyp); PLog(SETTINGS.getSetting('pref_load_subtitles'))
	
	from threading import Thread	# thread_getfile
	path_url_list=''; timemark=''; notice=True
	background_thread = Thread(target=thread_getfile, args=(textfile,pathtextfile,storetxt,url,fulldestpath,path_url_list,timemark,notice,sub_path,dtyp))
	background_thread.start()		
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# return blockt hier bis Thread-Ende									
	return
#---------------------------
# interne Download-Routine für MP4, MP3 u.a. mittels urlretrieve 
#	Download-Routine für Bilder: thread_getpic
#	bei Bedarf ssl.SSLContext verwenden - s.
#		https://docs.python.org/2/library/urllib.html
# vorh. Dateien werden überschrieben (wie früher mit curl/wget).
# Aufrufer: DownloadExtern, DownloadMultiple (mit 
#	path_url_list + timemark)
# 	notice triggert die Dialog-Ausgabe.
# Alternativen für urlretrieve (legacy): wget-Modul oder 
#	Request (stackoverflow: alternative-of-urllib-urlretrieve-in-python-3-5)
# 25.01.2022 hinzugefügt nach Ende Einzeldownload: Entfernung Lock DL_CHECK, 
#	Entf. in Monitor epgRecord.get_active_dls nicht sicher
# 19.02.2022 Nachrüstung GetOnlyRedirect vor urlretrieve für Audiothek
#
def thread_getfile(textfile,pathtextfile,storetxt,url,fulldestpath,path_url_list='',timemark='',notice=True,sub_path="",dtyp=""):
	PLog("thread_getfile:")
	PLog(url); PLog(fulldestpath); PLog(len(path_url_list)); PLog(timemark); PLog(notice); 

	icon = R('icon-downl-dir.png')
	try:
		if path_url_list:									# Sammeldownloads (Podcast)
			msg1 = 'Starte Download im Hintergrund'		
			msg2 = 'Anzahl der Dateien: %s' % len(path_url_list)
			msg3 = 'Ablage: ' + SETTINGS.getSetting('pref_download_path')
			ret=MyDialog(msg1, msg2, msg3, ok=False, yes='OK')
			if ret  == False:
				return

			cnt=0
			for item in path_url_list:
				cnt=cnt+1
				msg1 = "Sammeldownloads"
				msg2 = "Podcast: %d von %d" % (cnt, len(path_url_list))
				xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=False)
				PLog(item)
				path, url = item.split('|')	
				new_url, msg = get_page(path=url, GetOnlyRedirect=True) # für Audiothek erforderlich
				if new_url == '':							# 30.03.2022 weiter ohne Exception
					msg1 = "Fehler"
					msg2 = "Quelle nicht gefunden: %s" % url.split("/")[-1]
					wicon = R(ICON_WARNING)
					#raise Exception("Quelle nicht gefunden: %s" % url.split("/")[-1])
					xbmcgui.Dialog().notification(msg1,msg2,wicon,2000)
				else:
					urlretrieve(new_url, path)
				#xbmc.sleep(1000*2)							# Debug
			
			msg1 = u'%d Downloads erledigt' % cnt 
			msg2 = u'gestartet: %s' % timemark				# Zeitstempel 
			if notice:
				xbmcgui.Dialog().notification(msg1,msg2,icon,4000)	# Fertig-Info
				xbmc.executebuiltin('Container.NextSortMethod') # OK s.o.

		else:												# Einzeldownload
			vsize=''
			clen = get_content_length(url)
			if clen:
				vsize = " (%s):" % humanbytes(clen)
			else:
				vsize = u" (Größe unbekannt)"
			msg1 = 'Starte Download im Hintergrund'	+ vsize	
			msg2 = fulldestpath	
			msg3 = 'Begleit-Infos in: %s' % textfile
			subget = False
			if SETTINGS.getSetting('pref_load_subtitles') == 'true':		
				if sub_path and 'Video' in dtyp:				# Untertitel verfügbar?
					subget = True
					subname = os.path.split(sub_path)[1]
					msg3 = u"%s\nUntertitel werden zusätzlich geladen" % (msg3)					  

			if notice and SETTINGS.getSetting('pref_dl_showinfo') == 'true':
				ret=MyDialog(msg1, msg2, msg3, ok=False, yes='OK')
				if ret  == False:
					return
			if pathtextfile:
				RSave(pathtextfile, storetxt, withcodec=True)	# Text speichern
				
			# Fortschrittsbalken nur mit ermittelter Länge möglich:
			if clen and SETTINGS.getSetting('pref_use_pgbar') == 'true':	# mit Fortschrittsbalken 
				msg = get_chunks(url, clen, fulldestpath)
				if msg:
					raise Exception(msg)
			else:
				if os.path.exists(DL_CNT):						# Datei dl_cnt
					with open(DL_CNT,'r+') as f:				# Anz. Downloads schreiben -> get_active_dls
						line = f.read()
						new_len=clen
						if line == '' or line.startswith('0|'):	# leer / 0
							cnt=0; old_len=0; new_len=clen
							if new_len == '' :					# mögl. Problem in get_content_length
								new_len=0
						else:
							cnt, old_len = line.split("|")
						cnt = int(cnt) + 1; new_len = int(old_len) + int(new_len)
						f.seek(0)								# seek + truncate: alten Inhalt löschen
						line = "%s|%s" % (str(cnt), str(new_len))
						f.write(line)
						f.truncate()
						PLog("line_start_dl: %s" % line)
				else:
					with open(DL_CNT,'w') as f:
						f.write("1|%s" % str(clen))					
				new_url, msg = get_page(path=url, GetOnlyRedirect=True) # für Audiothek erforderlich
				if new_url == '':
					raise Exception("Quelle nicht gefunden")
				urlretrieve(new_url, fulldestpath)				
				#xbmc.sleep(1000*30)	# Debug
			if subget:											# Untertitel holen 
				get_subtitles(fulldestpath, sub_path)
			
			# time.sleep(10)											# Debug
			line=''
			msg1 = 'Download abgeschlossen:'
			msg2 = os.path.basename(fulldestpath) 				# Bsp. heute_Xpress.mp4
			if notice:
				xbmcgui.Dialog().notification(msg1,msg2,icon,4000)	# Fertig-Info
				if os.path.exists(DL_CNT):						# Datei dl_cnt
					with open(DL_CNT,'r+') as f:				# Anz. Downloads verringern -> get_active_dls
						line = f.read()
						new_len=clen
						cnt, old_len = line.split("|")
						if line != '' and line.startswith('0|') == False:
							cnt = int(cnt) - 1; 
							try:
								new_len = int(old_len) - int(new_len)
								if new_len < 0:
									new_len=0
							except:
								new_len = 0
							line = "%s|%s" % (str(cnt), str(new_len))
						f.seek(0)								# seek + truncate: alten Inhalt löschen
						f.write(line)
						f.truncate()
		
						PLog("line_end_dl: %s" % line)
						if "0|0" in line:						# Lock dl_check_alive entfernen
							PLog("Lock_entfernt")
							if os.path.exists(DL_CHECK):		
								os.remove(DL_CHECK)						
			
				
	except Exception as exception:
		PLog("thread_getfile:" + str(exception))
		if os.path.exists(DL_CHECK):							# Abbruchsignal -> 	epgRecord.get_active_dls
			os.remove(DL_CHECK)						
		msg1 = 'Download fehlgeschlagen'
		msg2 = 'Fehler: %s' % str(exception)		
		if notice:
			MyDialog(msg1, msg2, '')

	return

#---------------------------
# ermittelt Dateilänge für Downloads (leer bei Problem mit HTTPMessage-Objekt)
# Aufrufer: thread_getfile
#
def get_content_length(url):
	PLog('get_content_length:')
	UrlopenTimeout = 3
	try:
		req = Request(url)	
		r = urlopen(req)
		if PYTHON2:					
			h = r.headers.dict
			clen = h['content-length']
		else:
			h = r.getheader('Content-Length')
			clen = h
		# PLog(h)
		
	except Exception as exception:
		err = str(exception)
		PLog(err)
		clen = ''
	
	PLog(clen)
	return clen
	
#---------------------------
# Download stückweise mit Fortschrittsbalken
# Aufrufer: thread_getfile
# Upgrade: xbmcgui.DialogProgressBG (nach Supportende Leia)
#
def get_chunks(url, DL_len, fulldestpath):
	PLog('get_chunks:')
	
	msg=''; DL_len = int(DL_len); get_len = 0	
	
	dp = xbmcgui.DialogProgress()
	fname = fulldestpath.split('/')[-1]				# Dateiname
	dp.create('%s: %s' % (humanbytes(DL_len), fname))
	r = urlopen(url)
	blowup = 1024									# Default 1 MByte	
	CHUNK_len = 1024 * blowup
	if CHUNK_len > DL_len:
		CHUNK_len = DL_len
	PLog("DL_len %s, CHUNK_len %s, fname %s" % (str(DL_len), str(CHUNK_len), fname))


	with open(fulldestpath, 'wb') as f:
		remain = DL_len
		while remain > 0:	
			chunk = r.read(CHUNK_len)
			if not chunk:
				break
			f.write(chunk)
			
			chunk_len = len(chunk)
			get_len = get_len + chunk_len
			remain = DL_len - get_len
			up = 100 * float(get_len) / float(DL_len)	# Prozentsatz
			upround = int(round(up))					# int für DialogProgress erford.
			PLog("up: %s, upround %s" % (str(up), str(upround)))
			line = 'Länge chunk: %s, ausstehend %s von %s' % (str(chunk_len), remain, str(DL_len))
			PLog(line)
			dp.update(upround)
			#xbmc.sleep(1000)	# Debug
			up=up+up
			if (dp.iscanceled()): 
				msg="abgebrochen"
				break
			
	r.close()
	dp.close()
	return msg


#---------------------------
# Untertitel für Download holen
# Aufrufer: thread_getfile
def get_subtitles(fulldestpath, sub_path):
	PLog('get_subtitles:')
	
	PLog("fulldestpath: " + fulldestpath)
	PLog("sub_path: " + sub_path)
	if "|" in sub_path:						# ZDF 2 Links: .sub, .vtt
		 sub_path = sub_path.split('|')[0]
	local_path=''
	sub_path = sub_path_conv(sub_path)		# Untertitel holen + konvertieren
	if isinstance(sub_path, list):			# Liste für PY3 in sub_path_conv
		sub_path = sub_path[0]
	PLog("sub_path2: " + str(sub_path))

	if sub_path.startswith('http'):	# ZDF-Untertitel holen
		local_path = "%s/%s" % (SUBTITLESTORE, sub_path.split('/')[-1])
		local_path = os.path.abspath(local_path)
		try:
			urlretrieve(sub_path, local_path)
		except Exception as exception:
			PLog(str(exception))
			local_path=''
	else:
		local_path = sub_path
			
	if 	local_path:						# Name der UT-Datei an Videotitel anpassen
		suffix=''; ext=''
		if "." in fulldestpath:
			suffix =  "." + fulldestpath.split('.')[-1]
		if "." in local_path:
			ext =  "." + local_path.split('.')[-1]
		PLog("local_path: %s, suffix: %s, ext: %s" % (local_path, suffix, ext))
		
		utsrc = local_path
		if suffix and ext:
			utdest = fulldestpath.replace(suffix, ext)  # Bsp.: .mp4 -> .srt
		else:
			utdest = fulldestpath + ext
		PLog("utdest: " + utdest)
		if '//' not in utdest:		# keine Share
			shutil.copy(utsrc, utdest)					
			os.remove(utsrc)
		else:
			xbmcvfs.copy(utsrc, utdest)	
	return					

#---------------------------
# Download-Routine mittels urlretrieve ähnlich thread_getfile
#	hier für Bilder + Erzeugung von Wasserzeichen (text_list: Titel, tagline,
#	summary)
# Aufrufer: ZDF_BildgalerieSingle + ARDSportBilder 
#	dort Test auf SETTINGS.getSetting('pref_watermarks')
# Container.NextSortMethod sorgt für Listing-Refresh (ohne Sort.-Wirkung) - 
#	dagegen bleiben Container.Refresh und ActivateWindow wirkungslos.
# Testscript: watermark2.py
# Fehler: cannot write mode RGBA as JPEG (LibreElec) - siehe:
#	https://github.com/python-pillow/Pillow/issues/2609
#	Lösung new_image.convert("RGB") OK
# 5 try-Blöcke - 1 Block für Debugzwecke nicht ausreichend
# Problem Windows7: die meisten draw.text-Operationen schlagen fehl -
#	Ursache ev. Kodi 18.5/python3 auf dem Entw.PC (nicht mit
#	python2 getestet).
# 08.02.2024 
#
def thread_getpic(path_url_list,text_list,folder=''):
	PLog("thread_getpic:")
	PLog(len(path_url_list)); PLog(len(text_list)); PLog(folder);
	li = xbmcgui.ListItem()

	watermark=False; ok="nein"
	if text_list:										# 
		xbmc_base = xbmc.translatePath("special://xbmc")
		myfont = os.path.join(xbmc_base, "media", "Fonts", "arial.ttf") 
		if os.path.exists(myfont) == False:				# Font vorhanden?
			msg1 = 'Kodi Font Arial nicht gefunden.'
			msg2 = 'Bitte den Font Arial installieren oder die Option Wasserzeichen in den Settings abschalten.'
			MyDialog(msg1, msg2, '')
		else:	
			try:										# PIL auf Android nicht verfügbar
				from PIL import Image, ImageDraw, ImageFont
				watermark=True; ok="ja"
				PLog("Font: " + myfont)
				font = ImageFont.truetype(myfont)
				img_fraction=0.50; fontsize=1		# Text -> Bildhälfte: 
			except Exception as exception:
				PLog("Importerror: " + str(exception))
				watermark=False

	icon = R('icon-downl-dir.png')
	msg1 = 'Starte Download im Hintergrund'		
	msg2 = 'Anzahl der Bilder: %s, Wasserzeichen: %s' % (len(path_url_list), ok)
	msg3 = 'Ordner (Bildersammlungen): ' + folder
	ret=MyDialog(msg1, msg2, msg3, ok=False, yes='OK')
	if ret  == False:
		return
		
		
	i=0; err_url=0; err_PIL=0
	for item in path_url_list:
		PLog(item)
		path, url = item.split('|')					# path: Bilddatei, url: Quelle
		try:										# Server-Probleme abfangen, skip Bild
			urlretrieve(url, path)
			# xbmc.sleep(2000)						# Debug
		except Exception as exception:
			PLog("thread_getpic1: " + str(exception))
			err_url=err_url+1
			watermark = False						# skip Watermark
			
		if watermark:
			try:
				base = Image.open(path).convert('RGBA')
				skip_watermark=False
			except Exception as exception:
				PLog("thread_getpic2: " + str(exception))
				err_PIL=err_PIL+1
				skip_watermark=True
			
			if skip_watermark == False:	
				width, height = base.size
				PLog("Bildbreite, -höhe: %d, %d" % (width, height))
				# 0 = 100% Deckung für helle Flächen
				txtimg = Image.new('RGBA', base.size, (255,255,255,0))
				fz = SETTINGS.getSetting('pref_fontsize')
				if fz == 'auto':
					mytxt_col = 80						# Zeilenbreite 
				else:
					mytxt_col = 100 - int(fz)			# Bsp. 100-20				
				
				mytxt = text_list[i]
				mytxt = wrap(mytxt,mytxt_col)			# Zeilenumbruch
				PLog(mytxt)
				
				try:	
					# für Windows7 Multi- -> Single-Line:	
					import platform						# IOError möglich
					PLog('Plattform: ' + platform.release())
					if platform.release() == "7":
						PLog("Windows7: entferne LFs")	
						mytxt = mytxt.replace('\n', ' | ')
						mytxt = textwrap.fill(mytxt, mytxt_col)
				except Exception as exception:
					PLog("Plattform_Error: " + str(exception))				
								
				try:
					if SETTINGS.getSetting('pref_fontsize') == 'auto':
						# fontsize abhängig von Bildgröße:
						while font.getsize(mytxt)[0] < img_fraction*base.size[0]:		
							fontsize += 2
							font = ImageFont.truetype(myfont, fontsize)
							
						fontsize = max(10, fontsize)			# fontsize Minimum 10
					else:
						fontsize = int(SETTINGS.getSetting('pref_fontsize'))
					PLog("Fontsize: %d" % fontsize)
					font = ImageFont.truetype(myfont, fontsize)
					draw = ImageDraw.Draw(txtimg)
					# txtsz = draw.multiline_textsize(mytxt, font)	# exeption Windows7
					# PLog("Größe Bildtext: " + str(txtsz))
					
					#  w,h = draw.textsize(mytxt, font=font)	# textsize() nicht mehr verfügbar
					x=1; y=1									# Start links oben
					# outlined Text - für helle Flächen erforderlich, aus stackoverflow.com/
					# /questions/41556771/is-there-a-way-to-outline-text-with-a-dark-line-in-pil 
					# try-Block für Draw 
					outlineAmount = 2
					shadowColor = 'black'
					for adj in range(outlineAmount):					
						draw.text((x-adj, y), mytxt, font=font, fill=shadowColor)	#move right						
						draw.text((x+adj, y), mytxt, font=font, fill=shadowColor)	#move left					
						draw.text((x, y+adj), mytxt, font=font, fill=shadowColor)	#move up					
						draw.text((x, y-adj), mytxt, font=font, fill=shadowColor)	#move down						
						draw.text((x-adj, y+adj), mytxt, font=font, fill=shadowColor)#diagonal left up
						draw.text((x+adj, y+adj), mytxt, font=font, fill=shadowColor)#diagonal right up
						draw.text((x-adj, y-adj), mytxt, font=font, fill=shadowColor)#diagonal left down
						draw.text((x+adj, y-adj), mytxt, font=font, fill=shadowColor)#diagonal right down

					# fill: color, letz. Param: Deckung:
					draw.text((x,y), mytxt, font=font, fill=(255,255,255,255))
				except Exception as exception:
					PLog("thread_getpic3: " + str(exception))
					PLog('draw.text fehlgeschlagen')
					err_PIL=err_PIL+1
					
				new_image = Image.alpha_composite(base, txtimg)
				try:
					new_image.save(path)					# Orig. überschreiben
				except Exception as exception:
					PLog("thread_getpic4: " + str(exception))
					if 'cannot write mode RGBA' in str(exception):
						new_image = new_image.convert("RGB")
						try:
							new_image.save(path)
						except Exception as exception:
							PLog("thread_getpic5: " + str(exception))
							err_PIL=err_PIL+1	
		i=i+1	
	
	msg1 = 'Download erledigt'
	msg2 = 'Ordner: %s' % folder					# Ordnername 
	if err_url or err_PIL:							# Dialog statt Notif. bei Fehlern
		if 	err_url:
			msg3 = u'Fehler: %s Bild(er) nicht verfügbar' % err_url
		else:
			msg3 = u'Fehler: %s Wasserzeichen fehlgeschlagen' % err_PIL
		MyDialog(msg1, msg2, msg3)
	else:	
		xbmcgui.Dialog().notification(msg1,msg2,icon,4000)	# Fertig-Info
	xbmc.executebuiltin('Container.NextSortMethod') # OK (s.o.)
	return li	# ohne ListItem Rekursion möglich
#---------------------------
# Tools: Einstellungen,  Bearbeiten, Verschieben, Löschen
# 11.06.2022 Notif. für Zugang aus Menü Infos+Tools ergänzt
def DownloadTools():
	PLog('DownloadTools:');

	if SETTINGS.getSetting('pref_use_downloads') == 'false':
		msg1 = "Hinweis:"
		msg2 = 'Downloads sind ausgeschaltet'	
		icon = R(ICON_DOWNL_DIR)
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)

	path = SETTINGS.getSetting('pref_download_path')
	PLog(path)
	dirlist = []
	if os.path.isdir(path) == False:
		msg1='Hinweis:'
		if path == '':		
			msg2='Downloadverzeichnis noch nicht festgelegt.'
		else:
			msg2='Downloadverzeichnis nicht gefunden: '
		msg3=path
		MyDialog(msg1, msg2, msg3)
	else:
		dirlist = os.listdir(path)						# Größe Inhalt? 		
			
	PLog(len(dirlist))
	mpcnt=0; vidsize=0
	for entry in dirlist:
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0 or entry.find('.m3u') > 0:
			mpcnt = mpcnt + 1	
			fname = os.path.join(path, entry)					
			vidsize = vidsize + os.path.getsize(fname) 
	vidsize	= humanbytes(vidsize)
	PLog('Downloadverzeichnis: %s Download(s), %s' % (str(mpcnt), vidsize))
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)								# Home-Button
	
	dlpath =  SETTINGS.getSetting('pref_download_path')# Einstellungen: Pfad Downloadverz.
	title = u'Downloadverzeichnis festlegen/ändern: (%s)' % dlpath			
	tagline = 'Das Downloadverzeichnis muss für den Addon-Nutzer beschreibbar sein.'
	summ = ''; 
		
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_download_path', 'mytype': '0', 'heading': '%s', 'path': '%s'}" % (title, dlpath)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DOWNL_DIR), fparams=fparams, tagline=tagline)

	PLog(SETTINGS.getSetting('pref_VideoDest_path'))
	movie_path = SETTINGS.getSetting('pref_VideoDest_path')
	if SETTINGS.getSetting('pref_VideoDest_path') == '':# Vorgabe Medienverzeichnis (Movieverz), falls leer	
		pass
		# movie_path = xbmc.translatePath('library://video/')
		# PLog(movie_path)
				
	#if os.path.isdir(movie_path)	== False:			# Sicherung gegen Fehleinträge - in Kodi nicht benötigt
	#	movie_path = ''									# wird ROOT_DIRECTORY in DirectoryNavigator
	PLog(movie_path)	
	title = u'Zielverzeichnis zum Verschieben festlegen/ändern (%s)' % (movie_path)	
	tagline = 'Zum Beispiel das Medienverzeichnis.'
	summ = u'Hier kann auch ein Netzwerkverzeichnis, z.B. eine SMB-Share, ausgewählt werden.'
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_VideoDest_path', 'mytype': '0', 'heading': '%s', 'shares': '%s', 'path': '%s'}" %\
		(title, '', movie_path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_MOVE), fparams=fparams, tagline=tagline, summary=summ)
		
	if mpcnt > 0:																# Videos / Podcasts?
		dirsize=''
		dirsize = get_dir_size(SETTINGS.getSetting('pref_download_path'))
		summ = u"Größe Downloadverzeichnis: %s | Anzahl Downloads: %s | Größe Video-/Audiodateien: %s" %\
			(dirsize, str(mpcnt), vidsize)		
		title = 'Downloads und Aufnahmen bearbeiten: %s Download(s)' % (mpcnt)	# Button Bearbeiten
		tag = 'Downloads im Downloadverzeichnis ansehen, loeschen, verschieben'
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="DownloadsList", fanart=R(ICON_DOWNL_DIR), 
			thumb=R(ICON_DIR_WORK), fparams=fparams, summary=summ, tagline=tag)

		if dirlist:
			dest_path = SETTINGS.getSetting('pref_download_path') 
			if path and movie_path:												# Button Verschieben (alle)
				title = 'ohne Rückfrage! alle (%s) Downloads verschieben' % (mpcnt)	
				tagline = 'Verschieben erfolgt ohne Rueckfrage!' 
				summary = 'alle Downloads verschieben nach: %s'  % (movie_path)
				fparams="&fparams={'dfname': '', 'textname': '', 'dlpath': '%s', 'destpath': '%s', 'single': 'False'}" \
					% (dest_path, movie_path)
				addDir(li=li, label=title, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DOWNL_DIR), 
					thumb=R(ICON_DIR_MOVE_ALL), fparams=fparams, summary=summary, tagline=tagline)
			
			title = 'alle (%s) Downloads löschen' % (mpcnt)						# Button Leeren (alle)
			summary = 'alle Dateien aus dem Downloadverzeichnis entfernen'
			fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % dlpath
			addDir(li=li, label=title, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DOWNL_DIR), 
				thumb=R(ICON_DELETE), fparams=fparams, summary=summary)
	
	# ------------------------------------------------------------------	
	# Aufnahme-Tools			
	if os.path.exists(JOBFILE):													# Jobliste vorhanden?
		title = 'Aufnahme-Jobs verwalten'					
		tag = u'Jobliste EPG-Menü-Aufnahmen: Liste, Job-Status, Jobs löschen'
		fparams="&fparams={'action': 'listJobs'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.epgRecord.JobMain", fanart=R(ICON_DOWNL_DIR),  
			thumb=R("icon-record.png"), fparams=fparams, tagline=tag)

	if os.path.exists(MONITOR_ALIVE):											# JobMonitor?
		title = 'Aufnahme-Monitor stoppen'					
		tag = u'stoppt das Monitoring für EPG-Aufnahmen (aber keine laufenden Aufnahmen)'
		summ = 'das Setting "Aufnehmen Menü: EPG Sender einzeln" wird ausgeschaltet'
		summ = '%s\n\nZum Restart dieses Menü erneut aufrufen oder das Aufnehmen im Setting wieder einschalten' % summ
		fparams="&fparams={'action': 'stop', 'setSetting': 'true'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.epgRecord.JobMain", fanart=R(ICON_DOWNL_DIR), 
			thumb=R("icon-stop.png"), fparams=fparams, tagline=tag, summary=summ)
	else:
		title = 'Aufnahme-Monitor starten'					
		tag = u'startet das Monitoring für EPG-Aufnahmen'
		summ = 'das Setting "Aufnehmen Menü: EPG Sender einzeln" wird eingeschaltet'
		fparams="&fparams={'action': 'init', 'setSetting': 'true'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.epgRecord.JobMain", fanart=R(ICON_DOWNL_DIR), 
			thumb=R("icon-record.png"), fparams=fparams, tagline=tag, summary=summ)

		'''
		title = 'Testjobs starten'												# nur Debug 				
		fparams="&fparams={'action': 'test_jobs'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.epgRecord.JobMain", fanart=R("icon-record.png"), 
			thumb=R("icon-record.png"), fparams=fparams)
		'''	
		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#---------------------------
# Downloads im Downloadverzeichnis zur Bearbeitung listen	 	
def DownloadsList():			
	PLog('DownloadsList:')	
	path = SETTINGS.getSetting('pref_download_path')
	
	dirlist = []
	if path == None or path == '':										# Existenz Verz. prüfen, falls vorbelegt
		msg1 = 'Downloadverzeichnis noch nicht festgelegt'
		MyDialog(msg1, '', '')
		return
	else:
		if os.path.isdir(path)	== False:			
			msg1 =  'Downloadverzeichnis nicht gefunden: ' 
			msg2 =  path
			MyDialog(msg1, msg2, '')
			return
		else:
			dirlist = os.listdir(path)
			dirlist = [os.path.join(path, f) for f in dirlist]			# plus path
			dirlist.sort(key=lambda x: os.path.getmtime(x))				# sortieren
	dlpath = path

	PLog(len(dirlist))
	mpcnt=0; vidsize=0
	for entry in dirlist:
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0 or entry.find('.m3u') > 0:
			mpcnt = mpcnt + 1	
			fname = os.path.join(path, entry)					
			vidsize = vidsize + os.path.getsize(fname) 
	vidsize	= vidsize/1000000
	PLog('Inhalt: %s Download(s), %s MBytes' % (mpcnt, str(vidsize)))
	
	if mpcnt == 0:
		msg1 = 'Kein Download vorhanden | Pfad:' 
		msg2 = dlpath
		MyDialog(msg1, msg2, '')
		return		
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	ext_list = ['.mp4', '.webm', '.mp3', '.m4a', '.m3u']
	
	# Downloads listen:
	for entry in dirlist:							# Download + Beschreibung -> DirectoryObject
		for ext in ext_list:
			if entry.find(ext) > 0:
				localpath = entry
				title=''; tagline=''; summary=''; quality=''; thumb=''; httpurl=''
				fname =  entry							# Dateiname 
				basename = os.path.splitext(fname)[0]	# ohne Extension
				ext =     os.path.splitext(fname)[1]	# Extension
				fdate = os.stat(entry).st_mtime
				fdate = datetime.datetime.fromtimestamp(int(fdate))
				fdate = "Ablage: %s" % fdate.strftime("%d.%m.%Y, %H:%M Uhr")
				PLog(fname); PLog(basename); PLog(ext); PLog(fdate)
				txtfile = basename + '.txt'
				txtpath = os.path.join(path, txtfile)   # kompl. Pfad
				PLog('entry: ' + entry); PLog('txtpath: ' + txtpath)
				if os.path.exists(txtpath):
					txt = RLoad(txtpath, abs_path=True)	# Beschreibung laden - fehlt bei Sammeldownload
				else:
					txt = None
					title = entry						# Titel = Dateiname, falls Beschreibung fehlt
				if txt != None:			
					title = stringextract("Titel: '", "'", txt)
					tagline = stringextract("ung1: '", "'", txt)
					summary = stringextract("ung2: '", "'", txt)
					quality = stringextract("taet: '", "'", txt)
					thumb = stringextract("Bildquelle: '", "'", txt)
					httpurl = stringextract("Adresse: '", "'", txt)
					
					if tagline and quality:
						tagline = "%s | %s" % (tagline, quality)
						
					# Falsche Formate korrigieren:
					summary=py2_decode(summary); tagline=py2_decode(tagline);
					summary=repl_json_chars(summary); tagline=repl_json_chars(tagline); 
					summary=summary.replace('\n', ' | '); tagline=tagline.replace('\n', ' | ')
					summary=summary.replace('|  |', ' | '); tagline=tagline.replace('|  |', ' | ')

				else:										# ohne Beschreibung
					# pass									# Plex brauchte hier die Web-Url	aus der Beschreibung
					title = fname
					httpurl = fname							# Berücksichtigung in VideoTools - nicht abspielbar
					summary = 'ohne Beschreibung'
				tagline = "[COLOR blue]%s[/COLOR]\n%s" % (fdate, tagline)
					
				tag_par= tagline.replace('\n', '||')	
				PLog("Satz20:")
				PLog(httpurl); PLog(summary); PLog(tagline); PLog(quality); # PLog(txt); 			
				if httpurl.endswith('mp3') or httpurl.endswith('m3u'):
					oc_title = u'Anhören, Bearbeiten: Podcast | %s' % py2_decode(title)
					thumb = R(ICON_NOTE)
				else:
					oc_title=u'Ansehen, Bearbeiten: %s' % py2_decode(title)
					if thumb == '':							# nicht in Beschreibung
						thumb = R(ICON_DIR_VIDEO)

				httpurl=py2_encode(httpurl); localpath=py2_encode(localpath); dlpath=py2_encode(dlpath); 
				title=py2_encode(title); summary=py2_encode(summary); thumb=py2_encode(thumb); 
				tag_par=py2_encode(tag_par); txtpath=py2_encode(txtpath);
				fparams="&fparams={'httpurl': '%s', 'path': '%s', 'dlpath': '%s', 'txtpath': '%s', 'title': '%s',\
					'summary': '%s', 'thumb': '%s', 'tagline': '%s'}" % (quote(httpurl), quote(localpath), quote(dlpath), 
					quote(txtpath), quote(title), quote(summary), quote(thumb), quote(tag_par))
				addDir(li=li, label=oc_title, action="dirList", dirID="VideoTools", fanart=thumb, 
					thumb=thumb, fparams=fparams, summary=summary, tagline=tagline)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#---------------------------
# Downloads im Downloadverzeichnis ansehen, löschen, verschieben
#	zum  Ansehen muss das Video  erneut angefordert werden - CreateVideoClipObject verweigert die Wiedergabe
#		lokaler Videos: networking.py line 224, in load ... 'file' object has no attribute '_sock'
#	entf. unter Kodi (Wiedergabe lokaler Quellen möglich).
#	httpurl=HTTP-Videoquelle, path=Videodatei (Name), dlpath=Downloadverz., txtpath=Textfile (kompl. Pfad)
#	
def VideoTools(httpurl,path,dlpath,txtpath,title,summary,thumb,tagline):
	PLog('VideoTools: ' + path)

	title_org = py2_encode(title)
	
	sub_path=''							# s. 1. Ansehen
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	dest_path = SETTINGS.getSetting('pref_download_path')
	fulldest_path = os.path.join(dest_path, path)
	if  os.access(dest_path, os.R_OK) == False:
		msg1 = 'Downloadverzeichnis oder Leserecht  fehlt'
		msg2 = dest_path
		PLog(msg1); PLog(msg2)
		MyDialog(msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	
	fsize=''
	if os.path.exists(fulldest_path) == False:	# inzw. gelöscht?
		msg1 = 'Datei nicht vorhanden:'
		msg2 = fulldest_path
		PLog(msg1); PLog(msg2)
		MyDialog(msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	else:
		fsize = os.path.getsize(fulldest_path)  # nur Video bzw. mp3
			
	fulldest_path=py2_encode(fulldest_path); 
	PLog("fulldest_path: " + fulldest_path)
	tagline = u'Größe: %s' % humanbytes(fsize)
	if fulldest_path.endswith('mp4') or fulldest_path.endswith('webm'): # 1. Ansehen
		title = title_org 
		globFiles = "%s*" % fulldest_path.split('.')[0] # Maske o. Endung: Video-, Text-, Sub-Datei
		files = glob.glob(globFiles)
		PLog(files) 
		for src_file in files:
			if src_file.endswith(".srt") or src_file.endswith(".sub"):
				sub_path = src_file
		PLog("sub_path: " + sub_path)
		lable = "Ansehen | %s" % (title_org)
		fulldest_path=py2_encode(fulldest_path); title=py2_encode(title); thumb=py2_encode(thumb);	
		summary=py2_encode(summary); sub_path=py2_encode(sub_path);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(quote_plus(fulldest_path), quote_plus(title), quote_plus(thumb), 
			quote_plus(summary), quote_plus(sub_path))
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, tagline=tagline,
			thumb=thumb, fparams=fparams, mediatype='video')
	else:																# 'mp3', 'm4a' = Podcast
		# Dateiname bei fehl. Beschreibung, z.B. Sammeldownloads: 		# 1. Anhören
		is_playlist=False
		if fulldest_path.endswith('mp3') or fulldest_path.endswith('m3u') or fulldest_path.endswith('m4a'):
			if fulldest_path.endswith('m3u'):							# Link auspacken
				is_playlist=False
				data = RLoad(fulldest_path, abs_path=True)
				if "#EXTM3U" in data:
					is_playlist=True
				else:
					data = data.splitlines()
					for line in data:
						if line.startswith("http"):
							fulldest_path = line
							break
			if 	is_playlist == False:
				title = title_org 							
				lable = "Anhören | %s" % (title_org)
				fulldest_path=py2_encode(fulldest_path); title=py2_encode(title); thumb=py2_encode(thumb); 
				summary=py2_encode(summary);	
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(fulldest_path), 
					quote(title), quote(thumb), quote_plus(summary))
				addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, 
					fparams=fparams, mediatype='music') 
			else:														#  Playlist hier nicht abspielbar
				msg1 = u'Eine Playlist ist hier nicht abspielbar.'
				msg2 = u"Bitte die Playlist: 1. im Kodi-Hauptmenü unter Musik/Dateien hinzufügen oder"
				msg3 = u"2. in den Kodi-Ordner ../userdata/playlists verschieben."
				MyDialog(msg1, msg2, msg3)				
	
	lable = "Löschen: %s" % title_org 									# 2. Löschen
	tagline = 'Datei: %s..' % path[:28] 
	fulldest_path=py2_encode(fulldest_path);	
	fparams="&fparams={'dlpath': '%s', 'single': 'True'}" % quote(fulldest_path)
	addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
		thumb=R(ICON_DELETE), fparams=fparams, summary=summary, tagline=tagline)
	
	if SETTINGS.getSetting('pref_VideoDest_path'):	# 3. Verschieben nur mit Zielpfad, einzeln
		VideoDest_path = SETTINGS.getSetting('pref_VideoDest_path')
		textname = os.path.basename(txtpath)
		lable = "Verschieben | %s" % title_org									
		summary = "Ziel: %s" % VideoDest_path
		tagline = u'Das Zielverzeichnis kann im Menü Download-Tools oder in den Addon-Settings geändert werden'
		path=py2_encode(path); textname=py2_encode(textname);
		dlpath=py2_encode(dlpath); VideoDest_path=py2_encode(VideoDest_path);
		fparams="&fparams={'dfname': '%s', 'textname': '%s', 'dlpath': '%s', 'destpath': '%s', 'single': 'True'}" \
			% (quote(path), quote(textname), quote(dlpath), quote(VideoDest_path))
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DIR_MOVE_SINGLE), 
			thumb=R(ICON_DIR_MOVE_SINGLE), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#---------------------------
# Downloadverzeichnis leeren (einzeln/komplett)
# Mitnutzung: Bildershows
def DownloadsDelete(dlpath, single):
	PLog('DownloadsDelete: ' + dlpath)
	PLog('single=' + single)
	
	msg1 = u'Rückgängig nicht möglich!'
	msg2 = u'Wirklich löschen?'		
	ret=MyDialog(msg1, msg2, msg3='', ok=False, yes='Löschen')
	if ret  == False:
		return
	
	try:
		if single == 'False':
			if ClearUp(os.path.abspath(dlpath), 1) == True:
				error_txt = 'Verzeichnis geleert'
			else:
				raise NameError('Ursache siehe Logdatei')
		else:
			txturl = os.path.splitext(dlpath)[0]  + '.txt' 
			if os.path.isfile(dlpath) == True:							
				os.remove(dlpath)				# Video löschen
			if os.path.isfile(txturl) == True:							
				os.remove(txturl)				# Textdatei löschen
			error_txt = u'Datei gelöscht: ' + dlpath
		PLog(error_txt)			 			 	 
		msg1 = u'Löschen erfolgreich'
		msg2 = error_txt
		xbmcgui.Dialog().notification(msg1,msg2,R(ICON_DELETE),5000)
	except Exception as exception:
		PLog(str(exception))
		msg1 = u'Fehler | Löschen fehlgeschlagen'
		msg2 = str(exception)
		MyDialog(msg1, msg2, '')
	
	return
#---------------------------
# dfname=Videodatei, textname=Textfile,  dlpath=Downloadverz., destpath=Zielverz.
#
def DownloadsMove(dfname, textname, dlpath, destpath, single):
	PLog('DownloadsMove: ');PLog(dfname);PLog(textname);PLog(dlpath);PLog(destpath);
	PLog('single=' + single)

	li = xbmcgui.ListItem()

	if  os.access(destpath, os.W_OK) == False:
		if '//' not in destpath:					# Test entfällt bei Shares
			msg1 = 'Download fehlgeschlagen'
			msg2 = 'Kein Schreibrecht im Zielverzeichnis'
			MyDialog(msg1, msg2, '')
			return li	

	try:
		cnt=0; err_cnt=0
		if single == 'False':						# Verzeichnisinhalt verschieben
			dlpath_list = next(os.walk(dlpath))[2]	# skip .. + dirs		
			ges_cnt = len(dlpath_list)				# Anzahl Dateien
			for fname in dlpath_list:
				src = os.path.join(dlpath, fname)
				if '//' not in destpath:
					dest = os.path.join(destpath, fname)
				else:
					dest = destpath + fname			#  smb://myShare/myVideos/video1.mp4							
				PLog(src); PLog(dest); 
				
				if os.path.isfile(src) == True:	   	# Quelle testen
					if '//' not in destpath:						
						shutil.copy(src, dest)		# konv. kopieren	
					else:
						xbmcvfs.copy(src, dest)		# zu Share kopieren
						
					if xbmcvfs.exists(dest):
						xbmcvfs.delete(src)
						cnt = cnt + 1

			if cnt == ges_cnt:
				msg1 = 'Verschieben erfolgreich'
				msg2 = '%s von %s Dateien verschoben nach: %s' % (cnt, ges_cnt, destpath)
				msg3 = ''
			else:
				msg1 = 'Problem beim Verschieben - Ursache nicht bekannt'
				msg2 = 'verschobene Dateien: %s von %s.' % (cnt, ges_cnt)
				msg3 = 'Vielleicht hilft es, Dateien einzeln zu verschieben (Menü >Downloads bearbeiten<)'
			PLog(msg2)	
			MyDialog(msg1, msg2, msg3)
			return li
				 			 	 
		else:								# Einzeldatei verschieben
			videosrc = os.path.join(dlpath, dfname)	
			globFiles = "%s*" % videosrc.split('.')[0] # Maske o. Endung: Video-, Text-, Sub-Datei
			files = glob.glob(globFiles) 
			PLog(files)
					
			if '//' not in destpath:
				for src_file in files:
					srcname = os.path.split(src_file)[1]
					dest_file = os.path.join(destpath, srcname)
					PLog("srcname %s, dest_file %s" % (srcname, dest_file))	 						
					if os.path.isfile(src_file) == True:	# Quelldatei testen						
						shutil.copy(src_file, dest_file)		
						os.remove(src_file)					# Quelldatei löschen
			else:											# Share
				for src_file in files:
					srcname = os.path.split(src_file)[1]
					dest_file = destpath + srcname
					PLog("srcname %s, dest_file %s" % (srcname, dest_file))	 						
					ret = xbmcvfs.copy(src_file, dest_file)
					PLog(ret)

					if xbmcvfs.exists(dest_file):
						xbmcvfs.delete(src_file)
					else:
						msg = 'Kopieren auf Share %s fehlgeschlagen' % dest_file
						PLog(msg)
						raise Exception(msg)
						break
				
		msg1 = 'Verschieben erfolgreich'
		msg2 = 'Video verschoben: ' + 	dfname
		PLog(msg2)	
		MyDialog(msg1, msg2, '')
		return li

	except Exception as exception:
		PLog(str(exception))
		msg1 = 'Verschieben fehlgeschlagen'
		msg2 = str(exception)
		MyDialog(msg1, msg2, '')
		return li
		
#---------------------------
# Ablage von Texten im Downloadverzeichnis
# Aufruf: AudioStartLive (Liste RadioStreamLinks)
#	textKey -> Dict-Datei 
# data = Liste oder string, je Zeile wird eine Datei erzeugt,
#	"**" splittet Zeile in mehrere Zeilen, 1. Zeile = Dateiname
# 06.05.2024 textKey=RadioPlaylist -> einzelne Playlist
# 
def DownloadText(textKey):
	PLog('DownloadText: ' + textKey)
	
	data = Dict("load", textKey)
	PLog(type(data))
	if isinstance(data, list) == False:
		data = data.splitlines() 
	textlen = len(data)
	PLog(textlen)
	
	path = SETTINGS.getSetting('pref_download_path')
	PLog(path)
	if path == None or path == '':							# Existenz Verz. prüfen, falls vorbelegt
		msg1 = 'Downloadverzeichnis noch nicht festgelegt'
		MyDialog(msg1, '', '')
		return
	else:
		if os.path.isdir(path)	== False:			
			msg1 =  'Downloadverzeichnis nicht gefunden: ' 
			msg2 =  path
			MyDialog(msg1, msg2, '')
			return
	
	if "Playlist" in textKey:									
		fname = "%s.m3u" % textKey
		msg1 = "[B]%s[/B] mit %d Radiosendern speichern?"	 % (fname, textlen)
	else:	 
		msg1 = "[B]%d Streamlinks[/B] in einzelnen m3u-Dateien speichern?"	 % textlen
		if textlen == 1:
			msg1 = "[B]Einzel-Streamlink[/B] in m3u-Datei speichern?"	
	msg2 = 'Die Ablage erfolgt im Downloadverzeichnis.'
	ret=MyDialog(msg1, msg2, msg3="", ok=False, yes='OK')
	if ret  == False:
		return			

	msg1 = textKey
	icon = R('icon-downl-dir.png')
		
	if "Playlist" in textKey:								# -> RadioPlaylist
		playlist = "\n".join(data)
		fpath = os.path.join(path, fname)
		RSave(fpath, playlist, withcodec=True)	
		msg2 = "%s gespeichert" % fname

	else:													# -> einzelne m3u-Dateien
		for inline in data:
			lines=[] ; outlines=[]
			lines = inline.split("**")
			f = lines[0]									# Dateiname
			fname = os.path.join(path, f)	 
			del lines[0]
			
			for line in lines:
				outlines.append(line)
			page  = "\n".join(outlines)
			#PLog(page) 	# Debug
			msg = RSave(fname, py2_encode(page), withcodec=False)
			if msg:									# RSave_Exception
				msg2 = msg
				break	 
		msg2 = "%d Dateien gespeichert" % textlen

	xbmcgui.Dialog().notification(msg1,msg2,icon,2000)	
	return			
		
####################################################################################################
# Aufruf Main, Favoriten oder Merkliste anzeigen + auswählen
#	Hinzufügen / Löschen in Watch (Script merkliste.py)
# mode = 'Favs' für Favoriten  oder 'Merk' für Merkliste
# Datenbasen (Einlesen in ReadFavourites (Modul util) :
#	Favoriten: special://profile/favourites.xml 
#	Merkliste: ADDON_DATA/merkliste.xml (WATCHFILE)
# Verarbeitung:
#	Favoriten: Kodi's Favoriten-Menü, im Addon_Listing
#	Merkliste: zusätzl. Kontextmenmü (s. addDir Modul util) -> Script merkliste.py
#	
# Probleme: Kodi's Fav-Funktion übernimmt nicht summary, tagline, mediatype aus addDir-Call
#			Keine Begleitinfos, falls  summary, tagline od. Plot im addDir-Call fehlen.
#			gelöst mit Base64-kodierter Plugin-Url: 
#				Sonderzeichen nach doppelter utf-8-Kodierung
#			07.01.2020 Base64 in addDir wieder entfernt - hier Verbleib zum Dekodieren
#				alter Einträge
# 			Sofortstart/Resumefunktion: funktioniert nicht immer - Bsp. KIKA-Videos.
#				Die Kennzeichnung mit mediatype='video' erfolgt nach Abgleich mit
#				CallFunctions.
#				Kodi verwaltet die Resumedaten getrennt (Merkliste/Originalplatz). 
#
# Ordnerverwaltung + Filter s. Wicki
#	Filter-Deadlock-Sicherungen: 
#		1. ShowFavs bei leerer Liste	2. Kontextmenü -> watch_filter
#		3. Settings (Ordner abschalten)
# 14.11.2021 Home-Button + Sortierung getrennt von globalen Settings
# 16.11.2022 Berücksichtigung ausgewählter Sätze in selected (zunächst für
#	SearchARDundZDFnew)
#  10.09.2023 Sortierung der Verzeichnisliste mittels addDir-Array
# 
def ShowFavs(mode, selected=""):					# Favoriten / Merkliste einblenden
	PLog('ShowFavs: ' + mode)						# 'Favs', 'Merk'
	if selected:
		selected = selected.split()
		selected = [int(x) for a,x in enumerate(selected)]
	PLog(selected)
	
	myfilter=''
	if mode == 'Merk':
		with open(MERKACTIVE, 'w'):					# Marker aktivieren (Refresh in merkliste)
			pass
		if SETTINGS.getSetting('pref_merkordner') == 'true':
			if os.path.isfile(MERKFILTER):	
				myfilter = RLoad(MERKFILTER,abs_path=True)
			else:									# Filter entfernen, falls Ordner abgewählt
				if os.path.isfile(MERKFILTER):		# Altern.: siehe Kontextmenü -> watch_filter
					os.remove(MERKFILTER)
				
	PLog('myfilter: ' + myfilter)
	li = xbmcgui.ListItem()						
	li = home(li, ID=NAME)							# Home-Button

	my_items, my_ordner= ReadFavourites(mode)		# Addon-Favs / Merkliste einlesen
	PLog(len(my_items))
	if len(my_items) == 0:
		icon = R(ICON_DIR_WATCH)
		msg1 = "Merkliste"
		if mode == 'Favs':
			msg1 = "Favoriten"
			icon = R(ICON_DIR_FAVORITS)
		msg2 = u"keine Inhalte gefunden"
		xbmcgui.Dialog().notification(msg1,msg2,icon,2000)
		return	
	
	# Dir-Items für diese Funktionen erhalten mediatype=video:
	# 13.11.2021 ARDStartSingle hinzugefügt
	# 27.05.2023 zdfmobile-Verweise entfernt
	CallFunctions = ["PlayVideo", "ZDF_getVideoSources",
						"SingleSendung", "ARDStartVideoStreams", 
						"ARDStartVideoMP4", "ARDStartSingle", "PlayVideo", "my3Sat.SingleBeitrag",
						"SenderLiveResolution", "phoenix.get_formitaeten",
						"phoenix.SingleBeitrag", "phoenix.yt.yt_get",
						"arte.SingleVideo", "arte.GetContent"]	

	if mode == 'Favs':														
		tagline = u"Anzahl Addon-Favoriten: %s" % str(len(my_items)) 	# Info-Button
		s1 		= u"Hier werden die ARDundZDF-Favoriten aus Kodi's Favoriten-Menü eingeblendet."
		s2		= u"Favoriten entfernen: im Kodi's Favoriten-Menü oder am Ursprungsort im Addon (nicht hier!)."
		summary	= u"%s\n\n%s"		% (s1, s2)
		label	= u'Infos zum Menü Favoriten'
	else:
		mf = myfilter
		if mf == '':
			mf = "kein Filter gesetzt"
		tagline = u"Anzahl Merklisteneinträge: %s" % str(len(my_items)) 	# Info-Button
		s1		= u"Einträge entfernen: via Kontextmenü hier oder am am Ursprungsort im Addon."
		s2		= u"Merkliste filtern: via Kontextmenü hier.\nAktueller Filter: [COLOR blue]%s[/COLOR]" % mf
		s3		= u"Ordner im Titel der Einträge lassen sich in den Settings ein-/ausschalten"
		if SETTINGS.getSetting('pref_merkordner') == 'true':
			s3 = s3 + u"[COLOR blue] (eingeschaltet)[/COLOR]"
		else:
			s3 = s3 + " (ausgeschaltet)"
		summary	= u"%s\n\n%s\n\n%s"		% (s1, s2, s3)
		label	= u'Infos zum Menü Merkliste'
	

	# Info-Button ausblenden falls Setting true
	if SETTINGS.getSetting('pref_FavsInfoMenueButton') == 'false':		
		fparams="&fparams={'mode': '%s'}"	% mode						# Info-Menü
		addDir(li=li, label=label, action="dirList", dirID="ShowFavs",
			fanart=R(ICON_DIR_FAVORITS), thumb=R(ICON_INFO), fparams=fparams,
			summary=summary, tagline=tagline, cmenu=False) 	# ohne Kontextmenü)	
	
	Dir_Arr=[[] for _ in range(len(my_items))]			# addDir-Array Für Sortierung
	item_cnt=0; cnt=-1
	for fav in my_items:
		if selected:									# Auswahl (Suchergebnisse) beachten
			cnt = cnt + 1
			if cnt not in selected:	
				continue
		
		#fav = unquote_plus(fav)						# urllib2.unquote erzeugt + aus Blanks!		
		fav = unquote(fav)								# kleineres Übel (unquote_plus entfernt + im Eintrag)
		fav_org = fav		
		
		# PLog('fav_org: ' + fav_org)
		name=''; merkname=''; thumb=''; dirPars=''; fparams='';	ordner=''		
		name 	= re.search(' name="(.*?)"', fav) 			# name, thumb,Plot zuerst
		ordner 	= stringextract(' ordner="', '"',fav) 
		thumb 	= stringextract(' thumb="', '"',fav) 
		Plot_org = stringextract(' Plot="', '"',fav) 		# ilabels['Plot']
		Plot_org = Plot_org.replace(' Plot="', ' Plot=""')  # leer
		if name: 	
			name 	= name.group(1)
			name 	= unescape(name)

		# thumb-Pfad an lokales Addon anpassen (externe Merkliste) -
		# kein Test pref_merkextern (andere Gründe möglich, z.B. manuell
		# kopiert):
		my_thumb = thumb
		if thumb and mode == 'Merk':  # and SETTINGS.getSetting('pref_merkextern') == 'true':
			if thumb.startswith('http') == False:	
				if '/addons/' in thumb:
					home_thumb, icon = thumb.split('/addons/')
					myhome = xbmc.translatePath("special://home")
					my_thumb = "%saddons/%s" % (myhome, icon)
					PLog("home_thumb: %s, my_thumb: %s" % (home_thumb, my_thumb))
		
		if myfilter and len(selected) ==  0:				# Filterabgleich - nicht bei Auswahlliste 
			if 'ohne Zuordnung' in myfilter:				# merkliste.xml: ordner=""
				if ordner:
					continue
			else:
				if ordner != myfilter: 						# ausfiltern
						continue
			
		if mode == 'Merk' and 'plugin://plugin' not in fav:	# Base64-kodierte Plugin-Url
			PLog('base64_fav')
			fav = fav.replace('10025,&quot;', '10025,"')	# Quotierung Anfang entfernen
			fav = fav.replace('&quot;,return', '",return')	# Quotierung Ende entfernen					
			p1, p2 	= fav.split('",return)</merk>')	# Endstück p2: &quot;,return)</merk>
			p3, b64	=  p1.split('10025,"')					# p1=Startstück, b64=kodierter string
			b64_clean = convBase64(b64)						# Dekodierung mit oder ohne padding am Ende
			if b64_clean == False:							# Fehler mögl. bei unkodierter Url
				msg1 = "Problem bei Base64-Dekodierung: %s" % name
				PLog(msg1)
				#MyDialog(msg1, '', '')					# 30.06.2020: nicht mehr verwerfen			
				#continue
			else:	
				b64_clean=unquote_plus(b64_clean)		# unquote aus addDir-Call
				b64_clean=unquote_plus(b64_clean)		# unquote aus Kontextmenü
				#PLog(b64_clean)
				fav		= p3 + '10025,"' + b64_clean + p2 

		fav = fav.replace('&quot;', '"')					# " am Ende fparams
		fav = fav.replace('&amp;', '&')						# Verbinder &
		PLog('fav_b64_clean: ' + fav)
		dirPars	= re.search('action=(.*?)&fparams',fav)		# dirList&dirID=PlayAudio&fanart..
		fparams = stringextract('&fparams={', '}',fav)
		fparams = unquote_plus(fparams)				# Parameter sind zusätzl. quotiert
		PLog('fparams1: ' + fparams);
		
		try:
			dirPars = dirPars.group(1)
		except:
			dirPars = ''
		PLog('dirPars: ' + dirPars);
		mediatype=''										# Kennz. Videos im Listing
		CallFunction = stringextract("&dirID=", "&", dirPars) 
		PLog('CallFunction: ' + CallFunction)
		for f in CallFunctions:								# Parameter Merk='true' anhängen
			if f in CallFunction:			
				if SETTINGS.getSetting('pref_video_direct') == 'true':
					mediatype='video'
					break		
		PLog('mediatype: ' + mediatype)
		
		modul = "Haupt-PRG"
		dirPars = unescape(dirPars); 
		if 'resources.lib.' in dirPars:
			modul = stringextract('resources.lib.', ".", dirPars) 
		
		name = cleanmark(name)						# Pos.-Verschieb. durch Fett + Farbe vermeiden,
		name = name.strip()							# 	s.a. cleanmark in merkliste (action == 'del')
		
		PLog(name); PLog(thumb); PLog(Plot_org); PLog(dirPars); PLog(modul); PLog(mediatype);
		PLog('fparams2: ' + fparams);
			
		# Begleitinfos aus fparams holen - Achtung Quotes!		# 2. fparams auswerten
		fpar_tag = stringextract("tagline': '", "'", fparams) 
		fpar_summ = stringextract("summ': '", "'", fparams)
		if fpar_summ == '':
			fpar_summ = stringextract("summary': '", "'", fparams)
		fpar_plot= stringextract("Plot': '", "'", fparams) 
		fpar_path= stringextract("path': '", "'", fparams) # PodFavoriten
		
		action=''; dirID=''; fanart=''; summary=''; tagline=''; Plot=''
		if dirPars:
			dirPars = dirPars.split('&')					# 3. addDir-Parameter auswerten
			action	= dirPars[0] # = dirList 				#	ohne fparams, name + thumb s.o.
			del dirPars[0]
			for dirPar in dirPars:
				if 	dirPar.startswith('dirID'):		# dirID=PlayAudio
					dirID = dirPar.split('=')[1]
				if 	dirPar.startswith('fanart'):		
					fanart = dirPar[7:]				# '=' ev. in Link enthalten 
				if 	dirPar.startswith('thumb'):		# s.o. - hier aktualisieren
					thumb = dirPar[6:]				# '=' ev. in Link enthalten 
				if 	dirPar.startswith('summary'):		
					summary = dirPar.split('=')[1]
				if 	dirPar.startswith('tagline'):		
					tagline = dirPar.split('=')[1]
				if 	dirPar.startswith('Plot'):		# zusätzl. Plot in fparams möglich
					Plot = dirPar.split('=')[1]
				#if 	dirPar.startswith('mediatype'):		# fehlt in Kodi's Fav-Funktion 	
				#	mediatype = dirPar.split('=')[1]
		
			
		PLog('dirPars:'); PLog(action); PLog(dirID); PLog(fanart); PLog(thumb);
		PLog(Plot_org); PLog(fpar_plot); PLog(Plot);
		if SETTINGS.getSetting('pref_nohome') == 'true':	# skip Homebutton
			if 'Main' in dirID or  u'Zurück im' in dirID:
				continue	

		
		if summary == '':							# Begleitinfos aus fparams verwenden
			summary = fpar_summ
		if tagline == '':	
			tagline = fpar_tag
		if Plot_org == '':
			Plot = fpar_plot		# fparams-Plot
		else:
			Plot = Plot_org

		if Plot:									# Merkliste: Plot im Kontextmenü (addDir)
			if mode == 'Favs':						# Fav's: Plot ev. in fparams enthalten (s.o.)
				if tagline in Plot:
					tagline = ''
				if summary == '' or summary == None:# Plot -> summary					
					summary = Plot
			else:
				tagline = '' 						# falls Verwendung von tagline+summary aus fparams:
				summary = Plot						#	non-ascii-chars entfernen!
						
		summary = unquote_plus(summary); tagline = unquote_plus(tagline); 
		Plot = unquote_plus(Plot)
		summary = summary.replace('+', ' ')
		summary = summary.replace('&quot;', '"')
			
		Plot=unescape(Plot)
		Plot = Plot.replace('||', '\n')							# s. PlayVideo
		Plot = Plot.replace('+|+', '')	
		PLog('summary: ' + summary); PLog('tagline: ' + tagline); PLog('Plot: ' + Plot)
		
		if SETTINGS.getSetting('pref_FavsInfo') ==  'false':	# keine Begleitinfos 
			summary='';  tagline=''
			
		PLog('fanart: ' + fanart); PLog('thumb: ' + thumb);
		fparams = fparams.replace('\n', '||')					# json-komp. für func_pars in router()
		fparams = unquote_plus(fparams)
		fparams ="&fparams={%s}" % quote_plus(fparams)			# router-kompatibel			
		PLog('fparams3: ' + fparams)
		fanart = R(ICON_DIR_WATCH)
		if mode == 'Favs':
			fanart = R(ICON_DIR_FAVORITS)
		
		summary = summary.replace('||', '\n')					# wie Plot	
		tagline = tagline.replace('||', '\n')
		
		if modul != "ardundzdf":								# Hinweis Modul
			tagline = "[B]Modul: %s[/B]%s" % (modul, tagline)
		if SETTINGS.getSetting('pref_merkordner') == 'true':	
			merkname = name										# für Aufnahme/Abgleich im Kontextmenü addDir
			if ordner:											# Hinweis Ordner
				if 'COLOR red' in tagline:						# bei Modul plus LF
					tagline = "[B][COLOR blue]Ordner: %s[/COLOR][/B]\n%s" % (ordner, tagline)
				else:
					tagline = "[B][COLOR blue]Ordner: %s[/COLOR][/B] | %s" % (ordner, tagline)
				
			if SETTINGS.getSetting('pref_WatchFolderInTitle') ==  'true':	# Kennz. Ordner
				if ordner: 
					name = "[COLOR blue]%s[/COLOR] | %s" % (ordner, name)
		
		# Sätze -> Array für Sortierung
		Dir_Arr[item_cnt].append(name); Dir_Arr[item_cnt].append(action); Dir_Arr[item_cnt].append(dirID);
		Dir_Arr[item_cnt].append(fanart); Dir_Arr[item_cnt].append(my_thumb); Dir_Arr[item_cnt].append(summary);
		Dir_Arr[item_cnt].append(tagline); Dir_Arr[item_cnt].append(fparams); Dir_Arr[item_cnt].append(mediatype);
		Dir_Arr[item_cnt].append(merkname)
		item_cnt = item_cnt + 1
		
	#---------------------------------							# Sortierung
	PLog("Dir_Arr: %d" % len(Dir_Arr))	
	PLog(Dir_Arr[0])											# erster Satz vor Sortierung
	try:														# fängt leere Liste ab (Filter o. Element)
		PLog(Dir_Arr[0][-1])										# letztes Element im ersten Satz
		Dir_Arr = list(filter(lambda a: a != [], Dir_Arr))			# Leere Sätze entfernen
		PLog("Dir_Arr_clean: %d" % len(Dir_Arr))
		sortoption = SETTINGS.getSetting('pref_merksort')
		PLog("sortoption: %s" % sortoption)
		if sortoption != "keine":
			if 	myfilter:											# Filter gesetzt? Sortierung nach merkname 
				if sortoption == "aufsteigend":						#	(letztes Element, o. Attribute)
					Dir_Arr = sorted(Dir_Arr,key=lambda x: x[-1].lower())
				else:
					Dir_Arr = sorted(Dir_Arr,key=lambda x: x[-1].lower(), reverse=True)
			else:													# Sortierung nach name (erstes Element plus ev. 										
				if sortoption == "aufsteigend":						# 	Ordner-Kennzeichnung im Titel, Bsp. Audio | ..)
					Dir_Arr = sorted(Dir_Arr,key=lambda x: x[0].lower())
				else:	
					Dir_Arr = sorted(Dir_Arr,key=lambda x: x[0].lower(), reverse=True)													
		PLog(Dir_Arr[0])											# erster Satz nach Sortierung
		
		for rec in Dir_Arr:
			name=rec[0]; action=rec[1]; dirID=rec[2]; fanart=rec[3]; my_thumb=rec[4];
			summary=rec[5]; tagline=rec[6]; fparams=rec[7]; mediatype=rec[8]; merkname=rec[9];

			addDir(li=li, label=name, action=action, dirID=dirID, fanart=fanart, thumb=my_thumb,
				summary=summary, tagline=tagline, fparams=fparams, mediatype=mediatype, 
				merkname=merkname, ShowFavs="true")					# ShowFavs verhindert "Hinzufügen" im Kontextmenü
	except Exception as exception:
		PLog("ShowFavs_error: " + str(exception))
	
	#---------------------------------

	if item_cnt == 0:											# Ordnerliste leer?
		if myfilter:											# Deadlock
			heading = u'Leere Merkliste mit dem Filter: %s' % myfilter
			msg1 = u'Der Filter wird nun gelöscht; die Merkliste wird ohne Filter geladen.'
			msg2 = u'Wählen Sie dann im Kontextmenü einen anderen Filter.'
			MyDialog(msg1,msg2,heading=heading)
			if os.path.exists(MERKFILTER):
				os.remove(MERKFILTER)
			# ShowFavs('Merk')									# verdoppelt Home- + Infobutton
			xbmc.executebuiltin('Container.Refresh')
		else:
			heading = u'Leere Merkliste'
			msg1 = 'Diese Merkliste ist noch leer.'
			msg2 = u'Einträge werden über das Kontextmenü hinzugefügt'
			MyDialog(msg1,msg2,heading=heading)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-------------------------------------------------------
# convBase64 dekodiert base64-String für ShowFavs bzw. gibt False zurück
#	Base64 füllt den String mittels padding am Ende (=) auf ein Mehrfaches von 4 auf.
# aus https://stackoverflow.com/questions/12315398/verify-is-a-string-is-encoded-in-base64-python	
# 17.11.2019 mit Modul six zusätzl. unquote_plus erforderlich 
#
def convBase64(s):
	PLog('convBase64:')
	PLog(s[:80])
	try:
		if len(s.strip()) % 4 == 0:
			if PYTHON2:					
				s = base64.decodestring(s)
			else:
				s =  base64.b64decode(s)
				s = s.decode("utf-8") 
			return unquote_plus(s)		
	except Exception as exception:
		PLog(str(exception))
	return False
			
####################################################################################################
# Addon-interne Merkliste : Hinzufügen / Löschen
#	verlagert nach resources/lib/merkliste.py - Grund: bei Verarbeitung hier war kein
#	ein Verbleib im akt. Addon-Listing möglich.
#def Watch(action, name, thumb='', Plot='', url=''):
# 23.01.2021 Wegfall parseLinks_Mp4_Rtmp nach Umstellung auf Sofortstart-Erweiterungen:  				
#def parseLinks_Mp4_Rtmp(page, ID=''):	
#	
####################################################################################################
# 03.06.2021 get_sendungen (Classic) entfernt
####################################################################################################
# LiveListe Vorauswahl - verwendet lokale Playlist
# 
def SenderLiveListePre(title, offset=0):	# Vorauswahl: Überregional, Regional, Privat
	title = unquote(title)
	PLog('SenderLiveListePre:')
	PLog('title: ' + title)
	playlist = RLoad(PLAYLIST)	# lokale XML-Datei (Pluginverz./Resources)
	# PLog(playlist)		# nur bei Bedarf

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
		
	liste = blockextract('<channel>', playlist)
	PLog(len(liste))
	
	for element in liste:
		name = stringextract('<name>', '</name>', element)				# Titel
		tag = stringextract('<tag>', '</tag>', element)					# Zusatzinfos
		summ = stringextract('<summ>', '</summ>', element)
		if 'ARD Audio Event Streams' in name:							# -> Radio-Livestreams			
			continue
		img = stringextract('<thumbnail>', '</thumbnail>', element) # channel-thumbnail in playlist
		if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		else:
			img = img
		PLog(name); PLog(img); # PLog(element);  # nur bei Bedarf
		
		name=py2_encode(name); 
		fparams="&fparams={'title': '%s', 'listname': '%s', 'fanart': '%s'}" % (quote(name), quote(name), img)
		addDir(li=li, label=name, action="dirList", dirID="SenderLiveListe", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=img, fparams=fparams, tagline=tag, summary=summ)

	laenge = SETTINGS.getSetting('pref_LiveRecord_duration')
	if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
		laenge = "wird manuell eingegeben"

	title = 'EPG Alle JETZT | Recording TV-Live'; 						# EPG-Button Alle 
	summary =u'elektronischer Programmführer\n\nAufnehmen via Kontexmenü, Dauer: %s (siehe Settings)' % laenge
	tagline = 'zeigt die laufende Sendung für jeden Sender | Quelle: tvtoday.de'
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
		thumb=R('tv-EPG-all.png'), fparams=fparams, summary=summary, tagline=tagline)
							
	title = 'EPG Sender einzeln'; 										# EPG-Button Einzeln 
	if SETTINGS.getSetting('pref_epgRecord') == 'true':		
		title = u"%s | [B]Sendungen via Kontexmenü aufnehmen[/B]" % title
	tagline = u'zeigt für den ausgewählten Sender ein 12-Tage-EPG | Quelle: tvtoday.de'
	summary='je Seite: 24 Stunden (zwischen 05.00 und 05.00 Uhr des Folgetages)'
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="EPG_Sender", fanart=R(ICON_MAIN_TVLIVE), 
		thumb=R('tv-EPG-single.png'), fparams=fparams, summary=summary, tagline=tagline)	

	title = 'Suche im EPG'; 											# EPG-Button Suche 
	if SETTINGS.getSetting('pref_epgRecord') == 'true':
		title = u"%s | [B]Sendungen via Kontexmenü aufnehmen[/B]" % title
	tagline = 'Suche im 12-Tage-EPG | Quelle: tvtoday.de'
	summary='Aktualisierungsintervall (Setting): [B]%s[/B]' % SETTINGS.getSetting('pref_epg_intervall')
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="EPG_Search", fanart=R('tv-EPG-suche.png'), 
		thumb=R('tv-EPG-suche.png'), fparams=fparams, summary=summary, tagline=tagline)

	PLog(str(SETTINGS.getSetting('pref_LiveRecord'))) 
	if SETTINGS.getSetting('pref_LiveRecord') == 'true':		
		title = 'Recording TV-Live'										# TVLiveRecord-Button anhängen
		tagline = 'Downloadpfad: %s' 	 % SETTINGS.getSetting('pref_download_path') 				
		summary = u'Sender wählen und direkt aufnehmen.\nDauer: %s (siehe Settings)' % laenge
		fparams="&fparams={'title': '%s'}" % title
		addDir(li=li, label=title, action="dirList", dirID="TVLiveRecordSender", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=R('icon-record.png'), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

	
#-----------------------------------------------------------------------------------------------------
# EPG SenderListe - Liste aus livesenderTV.xml sortiert
# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
# 	EPG-Daten:  -> EPG_ShowSingle ("EPG Sender einzeln")
#	ohne EPG:	-> SenderLiveResolution
# Aufrufer SenderLiveListePre
# 
#
def EPG_Sender(title, Merk='false'):
	PLog('EPG_Sender:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	sort_playlist = get_sort_playlist()	# Senderliste + Cache
	#PLog(sort_playlist)
	
	# summ nur bei ID:
	summ = u"für die Merkliste (Kontextmenü) sind die Einträge dieser Liste wegen des EPG besser geeignet"
	summ = u"%s als die Menüs Überregional, Regional und Privat" % summ
	
	for rec in sort_playlist:
		title = rec[0]
		img = rec[2]
		if u'://' not in img:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		link = rec[3]
		ID = rec[1]
		if link == "":			# spez. Sender in livesenderTV.xml z.B. liga3
			continue
		
		PLog("Satz13:")
		PLog('title: %s, ID: %s' % (title, ID))
		PLog(img)
		if ID == '':				# ohne EPG_ID
			title = title + ': [B]ohne EPG[/B]' 
			title=py2_encode(title); link=py2_encode(link); img=py2_encode(img); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '', 'Merk': '%s'}" %\
				(quote(link), quote(title), quote(img), Merk)
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
				thumb=img, fparams=fparams, tagline='weiter zum Livestream')
		else:
			add = ''
			if SETTINGS.getSetting('pref_epgRecord') == 'true':
				add = u" und zum Aufnehmen via Kontextmenü"
			title=py2_encode(title); link=py2_encode(link);
			fparams="&fparams={'ID': '%s', 'name': '%s', 'stream_url': '%s', 'pagenr': %s}" % (ID, quote(title), 
				quote(link), '0')
			addDir(li=li, label=title, action="dirList", dirID="EPG_ShowSingle", fanart=R('tv-EPG-single.png'), thumb=img, 
				fparams=fparams, tagline='weiter zum EPG' + add, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-----------------------------------------------------------------------------------------------------
# Aufrufer SenderLiveListePre
# Setting "EPG im Hintergrund laden" wird geprüft
# Wegen des Kodi-Problems (Vermeidung Absturzproblem nach Abbruch, s.
#	SearchARDundZDFnew) wird Ergebnisliste erst in EPG_Search2 gebaut.
# EPG_Search2 übernimmt EPG_Search_Array (Sätze ab akt. Tag)  und 
#	sortiert nach starttime. Den gefundenen Sätzen wird hier die 
#	Sender-ID angehängt (sonst keine Zuordnung in EPG_Search2 möglich).
#
def EPG_Search(title, query=""):
	PLog('EPG_Search:')
	from resources.lib.ARDnew import ARDHandleRecents
	
	img = R("tv-EPG-suche.png")
	title_org=title;

	if SETTINGS.getSetting('pref_epgpreload') == 'false':
		xbmcgui.Dialog().notification(title_org, "EPG laden ist ausgeschaltet",img,3000)
		return
			
	query = ARDHandleRecents(title, mode="load", query="")
	if  query == None or query.strip() == '':
		return
	query = query.split('|')[0]											# Suchwortliste: doppelt für ARD|ZDF
	if len(query) <3:
		msg1 = u"Suchworte müssen  mindestens 3 Buchstaben  enthalten."
		MyDialog(msg1, '', '')	
		return
	PLog("query: %s" % query)

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	sort_playlist = get_sort_playlist()									# Senderliste wie EPG.thread_getepg
	plen = len(sort_playlist)
	PLog("SearchSender: %d" % plen)
	
	now,today,today_5Uhr,nextday,nextday_5Uhr = EPG.get_unixtime()		# lokale Unix-Zeitstempel holen + Offsets
	
	EPG_SearchHits=[]													# nimmt Treffer ab akt. Tag auf
	tag_negativ =u'neue EPG-Suche starten'								# ohne Treffer
	tag_positiv =u'gefundene Beiträge zeigen'							# mit Treffer
	cnt=0; up_query=up_low(query);
	up_query = up_query.replace("+", " ")								# Markus+Lanz -> Markus Lanz
	PLog("up_query: %s" % up_query)
	
	for i in range(len(sort_playlist)):
		rec = sort_playlist[i]
		sender=rec[0]; ID=rec[1]; sender_img=rec[2]; link = rec[3]		# Senderdaten 

		fname = os.path.join(DICTSTORE, "EPG_%s" % ID)
		if os.path.exists(fname):										# Dict-Datei (tvtoday-ID) vorhanden?
			EPG_dict = Dict("load", fname)								# Array-Format s. EPG.EPG, 12-Tage-EPG je Sender
			
			if EPG_dict == False or len(EPG_dict) == 0 or '<!DOCTYPE html>' in EPG_dict:	# Array-Format korrekt?
				continue
			if up_query not in up_low(str(EPG_dict)):					# Suchbegriff irgendwo im 12-Tage-Array?
				continue
			for r in EPG_dict:											# Fundstellen, Button in EPG_Search2
				starttime=r[0]
				if starttime < today:									# älter als heute -> verwerfern
					continue
				if up_query in up_low(r[3]) or up_query in up_low(r[5]):# Fund? 3=sname, 5=summ
					r.append(ID)										# Sender-ID anhängen für Zuordnung EPG_Search2
					if r in EPG_SearchHits:								# Doppel üblich bei Regionalsendern
						PLog("skip_double: %s | %s" % (ID, starttime))
						continue
					EPG_SearchHits.append(r)							# Treffer-Sender-EPG speichern
					PLog("query_found: %s | %s" % (query, r[3]))
					cnt=cnt+1
	
	#-----------------------------------
	PLog("cnt: %d" % cnt)
	store_recents=False
	if cnt == 0:
		img = R('tv-EPG-suche.png')
		label = "[B]EPG-Suche[/B] | nichts gefunden zu: [B]%s[/B] | neue Suche" % query.replace("+", " ")
		fparams="&fparams={'title': '%s', 'query': ''}" % quote(title)
		addDir(li=li, label=label, action="dirList", dirID="EPG_Search", 
			fanart=img, thumb=img, tagline=tag_negativ, fparams=fparams)
	else:	
		store_recents = True
		Dict("store", "EPG_SearchHits", EPG_SearchHits)					# -> EPG_Search2		
	
	#-----------------------------------
	if store_recents:										
		ARDHandleRecents(title, mode="store", query=query)				# query -> Suchwortliste
		
		if SETTINGS.getSetting('pref_epgRecord') == 'true':	
			tag_positiv = u"%s und via Kontextmenü aufnehmen" % tag_positiv
		title = "[B]EPG-Suche[/B]: %s Video(s)  | %s" % (cnt, query)	# Button -> EPG_Search2
		fparams="&fparams={'title': '%s', 'query': '%s'}" % (quote_plus(title), quote_plus(query))
		addDir(li=li, label=title, action="dirList", dirID="EPG_Search2", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag_positiv)
												

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------
# Aufruf EPG_Search
# Suchergebnis im Dict (EPG_SearchHits) 
# Schema: Senderliste sortieren (playlist), EPG_SearchHits laden + 
#		nach starttime sortieren, Je Satz Abgleich mit Titel (sname)
#		 und Beschreibung (summ), Play-Button bei Treffer.
#		Aufbau Liste ähnlich EPG_ShowSingle.
#		Setting 'pref_epgRecord' triggert Kontexmenü "Sendung aufnehmen" 
# img-Format von tvtoday auffällig im Log: Could not find suitable 
#	input format: x-directory/normal
#
def EPG_Search2(title, query=""):
	PLog('EPG_Search2: ' + query)
	
	from resources.lib.ARDnew import ARDHandleRecents
	icon = R("tv-EPG-suche.png")
	title_org=title

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	EPG_SearchHits = Dict("load", "EPG_SearchHits")
	if EPG_SearchHits == False or EPG_SearchHits == '':					# Ladeproblem?	
		EPG_SearchHits=[]
	PLog("EPG_SearchHits: %d" % len(EPG_SearchHits))
	EPG_SearchHits = sorted(EPG_SearchHits)								# nach starttime r[0] sortieren 
	
	sort_playlist = get_sort_playlist()									# Senderliste wie EPG.thread_getepg
	plen = len(sort_playlist)
	PLog("SearchSender2: %d" % plen)

	now,today,today_5Uhr,nextday,nextday_5Uhr = EPG.get_unixtime()		# lokale Unix-Zeitstempel holen + Offsets

	cnt=0; up_query=up_low(query); store_recents=False
	up_query = up_query.replace("+", " ")								# wie in EPG_Search
	
	img_base = "https://images.tvtoday.de/"
	for i in range(len(EPG_SearchHits)):
		r = EPG_SearchHits[i]
		ID = r[-1]; sender=""; sender_img=""; link=""					# Sender-ID
				
		if up_query in up_low(r[3]) or up_query in up_low(r[5]):		# Fund? 3=sname, 5=summ
			PLog("query_found2: %s | %s" % (query, r[3]))
			PLog(str(r))
			
			for rec in sort_playlist:									# Sender-Datensatz suchen
				if ID == rec[1]:
					sender=rec[0]; ID=rec[1]; sender_img=rec[2]; link = rec[3]	# Senderdaten
					sender_img = R(sender_img)
					PLog("Sender: %s, ID: %s" % (sender, ID))
					break
			if sender == "":											# sollte nicht vorkommen
				PLog("SenderID_missing: %s" % ID)
				continue
			
			starttime=r[0]; img=r[2]; sname=r[3]; summ=r[5];			# EPG-Datensatz
			vonbis=r[6]; today_human=r[7]; endtime=r[8]
			
			s_start = datetime.datetime.fromtimestamp(int(starttime))	# Unixtime -> human wie EPG.EPG
			day_human =  s_start.strftime("%d.%m.%Y")
			PLog("day_human: " + day_human)
			
			wday =  s_start.strftime("%A")					
			wday = transl_wtag(wday)									# engl. -> deutsch
			img = img.replace(".webp", ".jpg")
			if img.startswith("/"):										# /bundles/frontend/images/..
				img = img_base + img
			if img == "":												# kann fehlen
				img = sender_img
			PLog("wday: %s, img: %s" % (wday, img))
			 
			
			today_human = u"%s, %s" % (day_human, up_low(wday[:2]))		# Datum + Wochentag -> tagline, Titel						
			tag = u"[COLOR blue]%s[/COLOR] | [B]%s[/B] | zur Livesendung klicken." % (today_human, vonbis)
			start_end=""
			if SETTINGS.getSetting('pref_epgRecord') == 'true':	
				tag = u"%s\n[B]Zur Aufnahme:[/B] Kontextmenü" % tag
				start_end = "%s|%s" % (starttime, endtime)				# Kontexmenü "Sendung aufnehmen" 

			sender = py2_decode(sender)
			summ = "[B]%s[/B] | %s" % (sender, summ)
			Plot = summ.replace("\n", "||")
			if starttime < now:
				title = "[COLOR grey]%s | %s[/COLOR]" % (day_human, sname)	# grau - Vergangenheit
			else:
				title = "[COLOR blue]%s[/COLOR] | %s" % (day_human, sname)	# Datum + Wochentag | Titel
			
			PLog("Satz7:")
			PLog(today_human);PLog(title);PLog(vonbis);PLog(summ[:40]);
			
			title=py2_encode(title); link=py2_encode(link); img=py2_encode(img)
			Plot=py2_encode(Plot); 						
			fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','descr': '%s','Sender': '%s'}" %\
				(quote(link), quote(title), quote(img), quote(Plot), sender)
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
				thumb=img, fparams=fparams, summary=summ, tagline=tag, start_end=start_end)
			
			cnt=cnt+1				

	#-----------------------------------
	PLog("cnt: %d" % cnt)
	# Suchergebnis 0 möglich, falls Call von EPG_Search2 mit großer Zeitdiff. - unwahrscheinlich
	if cnt == 0:														
		xbmcgui.Dialog().notification(title_org, "leider nichts gefunden",icon,3000)
		return
	else:	
		store_recents = True		
																		# Wechsel-Button zu den DownloadTools:	
		if SETTINGS.getSetting('pref_epgRecord') == 'true':	
			tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
			fparams="&fparams={}"
			addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
				fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	
	
	#-----------------------------------
	if 	store_recents:													# Sucheingabe speichern
		ARDHandleRecents(title_org, mode="store", query=query)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#-----------------------------
# Liste aller TV-Sender wie EPG_Sender, hier mit Aufnahme-Button
# 17.04.2024 Ausfilterung spezieller Sender aus livesenderTV.xml
#
def TVLiveRecordSender(title):
	PLog('TVLiveRecordSender:')
	title = unquote(title)
	
	if check_Setting('pref_LiveRecord_ffmpegCall') == False:	
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)					# Home-Button
	
	duration = SETTINGS.getSetting('pref_LiveRecord_duration')
	duration, laenge = duration.split('=')
	duration = duration.strip()

	sort_playlist = get_sort_playlist()		# Senderliste + Cache
	PLog('Sender: ' + str(len(sort_playlist)))
	for rec in sort_playlist:
		title 	= rec[0]
		ID 		= rec[1]
		img 	= rec[2]
		if u'://' not in img:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		link 	= rec[3]
		if title == "":				# Spezialfälle, s. livesenderTV.xml (Bsp.: 3. Bundesliga)
			continue
		if link.endswith(".mp3") or link.endswith(".m3u") or "/mp3" in link:
			continue				# Spezialfälle ARD Audio Event Streams, s. livesenderTV.xml
		if ID == '':				# ohne EPG_ID
			title = title + ': [B]ohne EPG[/B]' 
		if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
			laenge = "wird manuell eingegeben"
		summ 	= 'Aufnahmedauer: %s' 	% laenge
		summ	= u"%s\n\nStart ohne Rückfrage!" % summ
		tag		= 'Zielverzeichnis: %s' % SETTINGS.getSetting('pref_download_path')
		
		PLog("RecordSender: %s, %s" % (title, link))
		PLog(str(rec))
		title=py2_encode(title); link=py2_encode(link);
		fparams="&fparams={'url': '%s', 'title': '%s', 'duration': '%s', 'laenge': '%s'}" \
			% (quote(link), quote(title), duration, laenge)
		addDir(li=li, label=title, action="dirList", dirID="LiveRecord", fanart=R(rec[2]), thumb=img, 
			fparams=fparams, summary=summ, tagline=tag)
		
	# Wechsel-Button zu den DownloadTools:	
	tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
	fparams="&fparams={}"
	addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
		fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	
			
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------
# 30.08.2018 Start Recording TV-Live
# Doku z. PHT-Problemen s. ältere Versionen
#
# 29.04.0219 Erweiterung manuelle Eingabe der Aufnahmedauer
# Check auf ffmpeg-Settings bereits in TVLiveRecordSender, Check auf LiveRecord-Setting
# 	bereits in SenderLiveListePre
# 04.07.2020 angepasst für epgRecord (Eingabe Dauer entf., Dateiname mit Datumformat 
#		geändert, Notification statt Dialog. epgJob enthält Aufnahmestart (Unixformat)
# 		LiveRecord verlagert nach util (import aus  ardundzdf klappt nicht in epgRecord,
#		dto. MakeDetailText).
#		
# 29.06.0219 Erweiterung "Sendung aufnehmen", Call K-Menü <- EPG_ShowSingle
# Check auf Setting pref_epgRecord in EPG_ShowSingle
# 30.08.2020 Wegfall m3u8-Verfahren: Mehrkanal-Check entf. (dto. in LiveRecord)
#
def ProgramRecord(url, sender, title, descr, start_end):
	PLog('ProgramRecord:')
	PLog(url); PLog(sender); PLog(title); 
	PLog(start_end);
			
	now = EPG.get_unixtime(onlynow=True)
	
	start, end = start_end.split('|')				# 1593627300|1593633300
	s = datetime.datetime.fromtimestamp(int(start))
	von = s.strftime("%d.%m.%Y, %H:%M")	
	s = datetime.datetime.fromtimestamp(int(end))
	bis = s.strftime("%d.%m.%Y, %H:%M")	
	PLog("now %s, von %s, bis %s"% (now, von, bis))
	
	#----------------------------------------------				# Voraussetzungen prüfen
	if check_Setting('pref_LiveRecord_ffmpegCall') == False:	# Dialog dort
		return			
	if check_Setting('pref_download_path') == False:			# Dialog dort
		return			
	
	if start == '' or end == '':					# sollte nicht vorkommen
		msg1 = "%s: %s" % (sender, title)
		msg2 = "Sendezeit fehlt - Abbruch"
		MyDialog(msg1, msg2, '')
		return
	if end < now:
		msg1 = "%s: %s\nSendungsende: %s" % (sender, title, bis)
		msg2 = "diese Sendung ist bereits vorbei - Abbruch"
		MyDialog(msg1, msg2, '')
		return

	#----------------------------------------------				# Aufnehmen
	msg2 = "von [B]%s[/B] bis [I][B]%s[/B][/I]" % (von, bis) 	# Stil- statt Farbmarkierung 
	msg3 = "Sendung aufnehmen?" 
	if start < now and end > now:					# laufende Sendung
		msg1 = u"läuft bereits: %s" % title
	else:											# künftige Sendung
		msg1 = u"Aufnehmen: %s" % title 		
	ret = MyDialog(msg1=msg1, msg2=msg2, msg3=msg3, ok=False, cancel='Abbruch', yes='JA', heading='Sendung aufnehmen')
	if ret == False:
		return			
		
	action="setjob"
	# action="test_jobs"	# Debug
	epgRecord.JobMain(action, start_end, title, descr, sender, url)
	return
	
#---------------------------------------------
# Aufruf: EPG_Sender, EPG_ShowAll, TVLiveRecordSender
# get_sort_playlist: Senderliste + Cache 
# erstellt sortierte Playlist für TV-Sender in livesenderTV.xml
#	im Abgleich mit TV-Livestream-Cache
#
def get_sort_playlist():						# Senderliste für EPG + Recording
	PLog('get_sort_playlist:')
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	sort_playlist =  []
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)				# skip_log: Log-Begrenzung
	ard_streamlinks = get_ARDstreamlinks(skip_log=True)
	iptv_streamlinks = get_IPTVstreamlinks(skip_log=True)
	
	for item in playlist:   
		rec = []
		title = stringextract('<title>', '</title>', item)
		# PLog(title)
		title = up_low(title)										# lower-/upper-case für sort() relevant
		EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', item)
		img = 	stringextract('<thumbnail>', '</thumbnail>', item)
		link =  stringextract('<link>', '</link>', item)			# url für Livestreaming
		if "<reclink>" in item:
			link =  stringextract('<reclink>', '</reclink>', item)	# abw. Link, zum Aufnehmen geeignet
		
		if 'ZDFsource' in link:
			title_sender = stringextract('<hrefsender>', '</hrefsender>', item)	
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
			for line in zdf_streamlinks:
				items = line.split('|')
				# Bsp.: "ZDFneo " in "ZDFneo Livestream":
				#PLog("ZDFsource: %s || %s" % (title_sender, str(items)))
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
					PLog("found: %s || %s" % (title_sender, str(items)))
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)	
						
		if 'ARDSource' in link:							# Streamlink für ARD-Sender holen,
			title_sender = stringextract('<hrefsender>', '</hrefsender>', item)	
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile ard_streamlinks: "webtitle|href|thumb|linkid"
			for line in ard_streamlinks:
				#PLog("ARDSource: %s || %s" % (title_sender, str(items)))
				items = line.split('|')
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
		
		if 'IPTVSource' in link:						# Streamlink für private Sender holen
			title_sender = stringextract('<title>', '</title>', item)	
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile iptv_streamlinks: "Sender|href|thumb|''"
			for line in iptv_streamlinks:
				#PLog("IPTVSource: %s || %s" % (title_sender, str(items)))
				items = line.split('|')
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
					if items[2]:						# Icon aus IPTVSource?
						img = items[2]
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
		
		rec.append(title); rec.append(EPG_ID);						# Listen-Element
		rec.append(img); rec.append(link);
		sort_playlist.append(rec)									# Liste Gesamt
	
	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = sorted(sort_playlist,key=lambda x: x[0])		# Array-sort statt sort()
	return sort_playlist
	
#-----------------------------------------------------------------------------------------------------
# Aufrufer EPG_Sender (falls EPG verfügbar)
# 	EPG-Daten holen in Modul EPG  (1 Woche), Listing hier jew. 1 Tag, 
#	JETZT-Markierung für laufende Sendung
# Klick zum Livestream -> SenderLiveResolution 
# 29.06.2020 Erweiterung Kontextmenü "Sendung aufnehmen" (s. addDir), 
#	Trigger start_end (EPG-Rekord mit endtime erweitert) -> ProgramRecord
#
def EPG_ShowSingle(ID, name, stream_url, pagenr=0):
	PLog('EPG_ShowSingle:'); 
	Sender = name
	PLog(Sender)

	EPG_rec = EPG.EPG(ID=ID, day_offset=pagenr)		# Daten holen
	PLog(len(EPG_rec))
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	if len(EPG_rec) == 0:			# kann vorkommen, Bsp. SR
		msg1 = 'Sender %s:' % name 
		msg2 = 'keine EPG-Daten gefunden'
		MyDialog(msg1, msg2, '')
		return li
		
	for rec in EPG_rec:
		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis, 
		#			7=today_human, 8=endtime:  
		href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];
		starttime=rec[0]; today_human=rec[7]; endtime=rec[8]; 
		start_end = ''										# Trigger K-Menü
		if SETTINGS.getSetting('pref_epgRecord') == 'true':	
			start_end = "%s|%s" % (starttime, endtime)		# Unix-Format -> ProgramRecord

		if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
			img = R('icon-bild-fehlt.png')
		PLog("sname2: " + sname)
			
		sname = unescape(sname)
		title = sname
		summ = unescape(summ)
		if 'JETZT' in title:			# JETZT-Markierung unter icon platzieren
			# Markierung für title bereits in EPG
			summ = "[B]LAUFENDE SENDUNG![/B]\n\n%s" % summ
			title = sname
		PLog("title: " + title)
		tagline = 'Datum: %s\nZeit: %s' % (today_human, vonbis)
		descr = summ.replace('\n', '||')		# \n aus summ -> ||
		
		title=py2_encode(title); stream_url=py2_encode(stream_url);
		img=py2_encode(img); descr=py2_encode(descr);
		Sender=py2_encode(Sender);
		fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','descr': '%s','Sender': '%s'}" %\
			(quote(stream_url), quote(title), quote(img), quote(descr), quote(Sender))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
			thumb=img, fparams=fparams, summary=summ, tagline=tagline, start_end=start_end)
			
	# Mehr Seiten anzeigen:
	max = 12
	pagenr = int(pagenr) + 1
	if pagenr < max: 
		summ = u'nächster Tag (%d von %d)' % (pagenr+1, max) 
		name=py2_encode(name); stream_url=py2_encode(stream_url);
		fparams="&fparams={'ID': '%s', 'name': '%s', 'stream_url': '%s', 'pagenr': %s}" % (ID, quote(name),
			quote(stream_url), pagenr)
		addDir(li=li, label=summ, action="dirList", dirID="EPG_ShowSingle", fanart=R('tv-EPG-single.png'), 
		thumb=R(ICON_MEHR), fparams=fparams, summary=summ)
		
	# Wechsel-Button zu den DownloadTools:	
	tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
	fparams="&fparams={}"
	addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
		fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	
		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#-----------------------------------------------------------------------------------------------------
# EPG: aktuelle Sendungen aller Sender mode='allnow'
# Aufrufer SenderLiveListePre (Button 'EPG Alle JETZT')
#	26.04.2019 Anzahl pro Seite auf 20 erhöht (Timeout bei Kodi kein Problem wie bei Plex)  
# sort_playlist: Senderabgleich in livesenderTV.xml mit direkten Quellen + Cachenutzung
#
def EPG_ShowAll(title, offset=0, Merk='false'):
	PLog('EPG_ShowAll:'); PLog(offset) 
	title = unquote(title)
	title_org = title
	title2='Aktuelle Sendungen'
	
	import resources.lib.EPG as EPG
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = get_sort_playlist()				# Senderliste + Cache
	PLog(len(sort_playlist))
	# PLog(sort_playlist)
	
	rec_per_page = 25								# Anzahl pro Seite (Plex: Timeout ab 15 beobachtet)
	max_len = len(sort_playlist)					# Anzahl Sätze gesamt
	start_cnt = int(offset) 						# Startzahl diese Seite
	end_cnt = int(start_cnt) + int(rec_per_page)	# Endzahl diese Seite
	
	#icon = R('tv-EPG-all.png')						# interferiert mit thread_getepg
	#xbmcgui.Dialog().notification("lade EPG-Daten",u"max. Anzahl: %d" % rec_per_page,icon,5000)
	
	PLog("walk_playlist")
	for i in range(len(sort_playlist)):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:				# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:				# Anzahl pro Seite überschritten?
			break
		rec = sort_playlist[cnt]
		# PLog(rec)							# Satz ['ARTE', 'ARTE', 'tv-arte.png', ..

		title_playlist = rec[0]
		m3u8link = rec[3]
		if m3u8link == "":					# spez. Sender in livesenderTV.xml z.B. liga3
			continue

		img_playlist = rec[2]	
		if u'://' not in img_playlist:		# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img_playlist = R(img_playlist)
		ID = rec[1]
		summ = ''
		
		tagline = 'weiter zum Livestream'
		if ID == '':									# ohne EPG_ID
			title = "[COLOR grey]%s[/COLOR]" % title_playlist + ' | [B]ohne EPG[/B]'
			img = img_playlist
			PLog("img: " + img)
		else:
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis: 
			rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
			# PLog(rec)	# bei Bedarf
			if len(rec) == 0:							# EPG-Satz leer?
				title = "[COLOR grey]%s[/COLOR]" % title_playlist + ' | ohne EPG'
				img = img_playlist			
			else:	
				href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]
				PLog("img: " + img)
				if type(img) != list:			# Ursache Listobjekt n.b.
					if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
						img = R('icon-bild-fehlt.png')
				title=py2_decode(title); sname=py2_decode(sname); title_playlist=py2_decode(title_playlist);
				title 	= sname.replace('JETZT', title_playlist)		# JETZT durch Sender ersetzen
				# sctime 	= "[COLOR red] %s [/COLOR]" % stime			# Darstellung verschlechtert
				# sname 	= sname.replace(stime, sctime)
				tagline = '%s | Zeit: %s' % (tagline, vonbis)
				
		descr = summ.replace('\n', '||')
		duration = SETTINGS.getSetting('pref_LiveRecord_duration')
		duration, laenge = duration.split('=')
		laenge = laenge.strip()
		summ 	= "%s\n\n%s" % (summ, u"Kontextmenü: Recording TV-Live (Aufnahmedauer: %s)" % laenge)	
		title = unescape(title)
		
		PLog("Satz14:")
		PLog("title: " + title); PLog(m3u8link); PLog(summ)
		
		title=py2_encode(title); m3u8link=py2_encode(m3u8link);
		img=py2_encode(img); descr=py2_encode(descr); summ=py2_encode(summ);		
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'Merk': '%s'}" %\
			(quote(m3u8link), quote(title), quote(img), quote_plus(descr), Merk)
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-all.png'), 
			thumb=img, fparams=fparams, summary=summ, tagline=tagline, start_end="Recording TV-Live")

	#icon = R('tv-EPG-all.png')											# interferiert mit thread_getepg
	#xbmcgui.Dialog().notification("EPG-Daten geladen", "",icon,2000)
	
	# Mehr Seiten anzeigen:
	# PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt 
		PLog(new_offset)
		summ = 'Mehr %s (insgesamt %s)' % (title2, str(max_len))
		title_org=py2_encode(title_org);
		fparams="&fparams={'title': '%s', 'offset': '%s'}"	% (quote(title_org), new_offset)
		addDir(li=li, label=summ, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
			thumb=R(ICON_MEHR), fparams=fparams, summary=summ, tagline=title2)

	# Wechsel-Button zu den DownloadTools:	
	tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
	fparams="&fparams={}"
	addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
		fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#-----------------------------------------------------------------------------------------------------
# TV LiveListe - verwendet lokale Playlist livesenderTV.xml
# Aufrufer: SenderLiveListePre
# onlySender: Button nur für diesen Sender (z.B. ZDFSportschau Livestream für Menü
#	ZDFSportLive)
# 23.06.2020 lokale m3u8-Dateien in livesenderTV.xml sind entfallen
#	Ermittlung Streamlinks im Web (link: ARDSource, ZDFsource)
# 26.05.2022 ergänzt um Nutzung iptv_streamlinks für private Sender
#	(link: IPTVSource)
# 05.02.2023 addDir ergänzt mit EPG_ID für Kontextmenü
# 08.10.2023 ard_streamlinks mit linkid ergänzt (Verwendung
#	für programm-api.ard)
#
def SenderLiveListe(title, listname, fanart, offset=0, onlySender=''):			
	# SenderLiveListe -> SenderLiveResolution (reicht nur durch) -> Parseplaylist (Ausw. m3u8)
	#	-> CreateVideoStreamObject 
	PLog('SenderLiveListe:')
	PLog(title); PLog(listname)
				
	title2 = 'Live-Sender ' + title
	title2 = title2
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
			
	playlist = RLoad(PLAYLIST)							# lokale XML-Datei (Pluginverz./Resources)
	playlist = blockextract('<channel>', playlist)
	PLog(len(playlist)); PLog(listname)
	mylist=''
	for i in range(len(playlist)):						# gewählte Channel extrahieren
		item = playlist[i] 
		name =  stringextract('<name>', '</name>', item)
		# PLog(name)
		if py2_decode(name) == py2_decode(listname):	# Bsp. Überregional, Regional, Privat
			mylist =  playlist[i] 
			break
			
	lname = py2_decode(listname)
	# Streamlinks aus Caches laden (Modul util), ab 01.06.2022 für Überregional,
	#	Regional + Privat. get_sort_playlist entfällt hier:
	zdf_streamlinks = get_ZDFstreamlinks()			# Streamlinks für ZDF-Sender 
	ard_streamlinks = get_ARDstreamlinks()			# ard_streamlinks oder ard_streamlinks_UT
	iptv_streamlinks = get_IPTVstreamlinks()		# private + einige regionale

	PLog(OS_DETECT)									# 07.08.2022 kleine Verbesserung mit Delay:
	if "armv7" in OS_DETECT:						# host: [armv7l]
		xbmc.sleep(1000)							# Test: für Raspi (verhind. Klemmer)

	mediatype='' 						# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		if "Audio Event" in title:		# ARD Audio Event Streams (ARDSportAudioXML:)
			mediatype='music'
		else:
			mediatype='video'

	# abweichend - externe Funktion:					# channel in livesenderTV.xml
	if u'Regional: WDR' in lname:						# Auswertung + Liste WDR Lokalzeit
		url = "https://www1.wdr.de/fernsehen/livestream/lokalzeit-livestream/index.html" 
		wdr_streamlinks = list_WDRstreamlinks(url)		# Webseite
		return
		
	# abweichend - externe Funktion:					# channel in livesenderTV.xml
	if u'3. Bundesliga' in lname:						# 3. Liga Livestream
		title = u"ARD Livestreams 3. Bundesliga"
		img = R("tv-liga3.png")			
		ARDSportLiga3(title, img)
		return
		
	# Zusatzbutton:
	if u'Privat' in listname:							# Suchfunktion IPTV-Private
		title = u"Suche lokale private IPTV-Sender"
		img = R("suche_iptv.png")
		tag = "Quelle: [B]kodi_tv_local.m3u[/B] im jnk22-Repo auf Github"
		summ = "der zuletzt gefundene IPTV-Sender wird unter diesem Suchbutton eingeblendet."
		title=py2_encode(title)	
		fparams="&fparams={'title': '%s'}" % (quote(title))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveSearch", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)
			
		iptv_search = Dict("load", "iptv_search")	# letztes Suchergebnis -> Senderbutton
		if iptv_search:
			tvgname,tvgid,thumb,link = iptv_search.splitlines()
			title=py2_encode(tvgname); link=py2_encode(link);
			thumb=py2_encode(thumb); 
			title = "Suchergebnis: [B]%s[/B]" % tvgname
			summ = "zuletzt gefundener IPTV-Sender: [B]%s[/B]" % tvgname
			fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': ''}" % (quote(link), 
				quote(thumb), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R("suche_iptv.png"), 
				thumb=thumb, fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)		
				
				
	if SETTINGS.getSetting('pref_use_epg') == 'true':		# Vorab-Info: EPG-Nutzung
		if "Audio" in listname == False:					# nicht bei ARD Audio Event Streams 
			icon = R('tv-EPG-all.png')
			msg1 = ""
			msg2 = "wird aktualisiert"
			xbmcgui.Dialog().notification(msg1,msg2,icon,4000)

	liste = blockextract('<item>', mylist)					# Details eines Senders
	PLog(len(liste));
	EPG_ID_old = ''											# Doppler-Erkennung
	sname_old=''; stime_old=''; summ_old=''; vonbis_old=''	# dto.
	summary_old=''; tagline_old=''
	for element in liste:									# Senderliste mit Links, ev. EPG (Setting) 
		img_streamlink=''; 									# Austausch Icon
		linkid=""											# ARD-Sender
		element = py2_decode(element)	
		link = stringextract('<link>', '</link>', element) 
		link = unescape(link)	
		title_sender = stringextract('<hrefsender>', '</hrefsender>', element) 
		if "<tvg-name>" in element:
			title_sender = stringextract('<title>', '</title>', element) # IPTVSource-Sender
		PLog(u'Sender: %s, link: %s' % (title_sender, link));

		# --												# Cache 
		if 'ZDFsource' in link:								# Streamlink für ZDF-Sender holen,
			link=''	
			# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
			for line in zdf_streamlinks:
				PLog("zdfline: " + line[:40])
				items = line.split('|')
				# Bsp.: "ZDFneo " in "ZDFneo Livestream":
				if up_low(title_sender) == up_low(items[0]): 
					link = items[1]
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
				
		if 'ARDSource' in link:								# Streamlink für ARD-Sender holen, Ermittlung
			link=''											#	Untertitel ab Okt 2022 in PlayVideo
			# Zeile ard_streamlinks: "webtitle|href|thumb|tagline|linkid"
			for line in ard_streamlinks:
				PLog("ardline: " + line[:40])
				items = line.split('|')
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]							# master.m3u8
					linkid = items[-1]						# linkid für programm-api.ard
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
				
		if 'IPTVSource' in link:							# Streamlink für private Sender holen
			link=''	
			# Zeile iptv_streamlinks: "Sender|href|thumb|tagline"
			for line in iptv_streamlinks:
				PLog("iptvline: " + line[:40])
				items = line.split('|')
				if up_low(title_sender) == up_low(items[0]):# title_sender hier tvg-name
					link = items[1]
					if items[2]:							# Icon aus IPTVSource?
						img_streamlink = items[2]
					break
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
		# --												# Cache 			
		
		PLog('Mark2:')
		PLog("found: %s, linkid: %s" % (title_sender, linkid))
		# Spezialbehandlung für N24 in SenderLiveResolution - Test auf Verfügbarkeit der Lastserver (1-4)
		# EPG: ab 10.03.2017 einheitlich über Modul EPG.py (vorher direkt bei den Sendern, mehrere Schemata)
		# 								
		title = stringextract('<title>', '</title>', element)
		if onlySender:										# Button nur für diesen Sender
			title=py2_encode(title); onlySender=py2_encode(onlySender) 
			if title != onlySender:
				continue
			
		epg_date=''; epg_title=''; epg_text=''; summary=''; tagline='' 
		EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', element)	# -> EPG.EPG und Kontextmenü
		if EPG_ID.strip() == "":
			EPG_ID="dummy"								# Kodi-Problem: ohne Wert verwendet addDir vorige EPG_ID
			PLog("set_dummmy_EPG_ID: " + title)
		PLog('setting: ' + str(SETTINGS.getSetting('pref_use_epg')))# EPG nutzen? 
		if SETTINGS.getSetting('pref_use_epg') == 'true':	# hier nur aktuelle Sendung
			if EPG_ID and EPG_ID != "dummy":
				# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis:
				try:
					rec = EPG.EPG(ID=EPG_ID, mode='OnlyNow')	# Daten holen - nur aktuelle Sendung
					sname=''; stime=''; summ=''; vonbis=''		# Fehler, ev. Sender EPG_ID nicht bekannt
					if rec:								
						sname=py2_encode(rec[3]); stime=py2_encode(rec[4]); 
						summ=py2_encode(rec[5]); vonbis=py2_encode(rec[6])	
				except:
					sname=''; stime=''; summ=''; vonbis=''	
										
				if sname:
					title=py2_encode(title); 
					title = "%s: %s"  % (title, sname)
				if summ:
					summary = py2_encode(summ)
				else:
					summary = ''
				if vonbis:
					tagline = u'[B]Sendung: %s Uhr[/B]' % vonbis
				else:
					tagline = ''
				tagline = u"%s\n[B]Tages-EPG[/B] via Kontext-Menü aufrufen." % tagline

		title = unescape(title)	
		title = title.replace('JETZT:', '')					# 'JETZT:' hier überflüssig
		if link == '':										# fehlenden Link im Titel kennz.
			title = "%s | Streamlink fehlt!" %  title	
		summary = unescape(summary)	
				
		if img_streamlink:									# Vorrang Icon aus direkten Quellen	
			img = img_streamlink 
		else:
			img = stringextract('<thumbnail>', '</thumbnail>', element) 
			if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
				if img:										# kann fehlen, z.B. bei Privaten
					img = R(img)
				else:				
					img = R(ICON_MAIN_TVLIVE)
			
		geo = stringextract('<geoblock>', '</geoblock>', element)
		PLog('geo: ' + geo)
		if geo:
			tagline = '%s\nLivestream nur in Deutschland zu empfangen!' % tagline
			
		PLog("Satz8:")
		PLog(title); PLog(link); PLog(img); PLog(summary); PLog(tagline[0:80]);
	
		descr = summary.replace('\n', '||')
		if tagline:
			descr = "%s %s" % (tagline, descr)				# -> Plot (PlayVideo)
			descr = descr.replace("\n", "||") 
		title=py2_encode(title); link=py2_encode(link);
		img=py2_encode(img); descr=py2_encode(descr);	
		fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': '%s'}" % (quote(link), 
			quote(img), quote(title), quote(descr))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=fanart, thumb=img, 
			fparams=fparams, summary=summary, tagline=tagline, mediatype=mediatype, EPG_ID=EPG_ID)		
	
	#  if onlySender== '':		# obsolet seit V4.4.2 
	# RP3b+: Abstürze möglich beim Öffen der Regional-Liste, Log: clean up-Problem mit Verweis auf classes:
	#	N9XBMCAddon9xbmcaddon5AddonE,N9XBMCAddon9xbmcaddon5AddonE.  Ähnlich issue
	#	https://github.com/asciidisco/plugin.video.netflix/issues/576 aber Fix hier nicht anwendbar.
	# s.a. https://forum.kodi.tv/showthread.php?tid=359608
	# Delay nach Laden der Streamlinks ohne Wirkung (s.o. OS_DETECT)
	# Memory-Bereinig. nach router-Ende unwirksam s. Script-Ende)
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
#-----------------------------------------------
# Suche nach IPTV-Livesendern - bisher nur lokale private Sender
#	 aus jnk22-Repo - s. Zusatzbutton SenderLiveListe
def SenderLiveSearch(title):
	PLog('SenderLiveSearch:')

	query = get_keyboard_input() 
	if query == None or query.strip() == '': 	# None bei Abbruch
		return SenderLiveListe("", "","")		# dummy, sonst Absturz nach Sofortstart/Suche
	query = query.strip()
	PLog(query)
	
	url1 = "https://raw.githubusercontent.com/jnk22/kodinerds-iptv/master/iptv/kodi/kodi_tv_local.m3u"
	url2 = "https://github.com/jnk22/kodinerds-iptv/blob/e297851866d6af270e69da6d1d60f2e938f72860/iptv/kodi/kodi_tv_main.m3u"
	page1, msg = get_page(url1)					
	page2, msg = get_page(url2)					
	if page1 == '' and  page2 == '':	
		msg1 = "Fehler in SenderLiveSearch:"
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return
	page = page1 + page2
	PLog(page[:60])
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	mediatype='' 						# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	items = blockextract('#EXTINF:', page)
	for item in items:
		if up_low(query) in up_low(item):
			item = item.replace('\\"', '"')						# Ergebnis url2: tvg-name=\"ServusTV HD\"..
			PLog("item: %s" % item)
			tag=""
			tvgname = stringextract('tvg-name="', '"', item)
			tvgid = stringextract('tvg-id="', '"', item)
			thumb = stringextract('tvg-logo="', '"', item)
			links = blockextract('https', item)					# 1. logo, 2. streamlink
			link = links[-1]
			link = link.replace('",', '')
			tvgname = py2_decode(tvgname); tvgid = py2_decode(tvgid)
			PLog(tvgid)
			if tvgid:
				tag = "tvg-id: [B]%s[/B]" % tvgid
			PLog(tvgname); PLog(tvgid); PLog(thumb); PLog(link);
			iptv_search = "%s\n%s\n%s\n%s" % (tvgname,tvgid,thumb,link)
			Dict("store", "iptv_search", iptv_search)
			
			title=py2_encode(tvgname); link=py2_encode(link);
			thumb=py2_encode(thumb); 
			fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': ''}" % (quote(link), 
				quote(thumb), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R("suche_iptv.png"), 
				thumb=thumb, fparams=fparams, tagline=tag, mediatype=mediatype)		
		
			break
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#-----------------------------------------------
# WRD-Links 
# Aufruf SenderLiveListe für WDR Lokalzeit
#
def list_WDRstreamlinks(url):
	PLog('list_WDRstreamlinks:')
	wdr_base = "https://www1.wdr.de"
	
	page, msg = get_page(url)					
	if page == '':	
		msg1 = "Fehler in get_WRDstreamlinks:"
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	
	stations = stringextract('broadcastingStations">', '</script>', page)
	items = blockextract('class="headline', stations)
	PLog(len(items))	

	li = xbmcgui.ListItem()
	
	tag = u"zur aktuellen Sendung des WDR"
	img = "https://www1.wdr.de/lokalzeit/fernsehen/tv-ubersicht-bild-100~_v-TeaserAufmacher.jpg"
	for item in items:
		path = stringextract('live"><a href="', '"', item)		
		title = stringextract('programme-uuid="', '"', item)
		title = title.replace("_", " ")
		title = title.replace("WDR", "")
		summ = u"[B]Sendezeit 19.30 - 20.00 Uhr[/B]" 
		
		PLog("Satz28:")
		
		PLog(path);PLog(img); PLog(title); PLog(summ); 
		title=py2_encode(title); 
		path=py2_encode(path); img=py2_encode(img);
		
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'summ': '%s'}" %\
			(quote(path), quote(title), quote(img), quote(summ))				
		addDir(li=li, label=title, action="dirList", dirID="WDRstream", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------------------------
# Livesender WRD-Lokalzeit-Link 
# Aufruf list_WDRstreamlinks
# Nach Sendungsende bleibt der Link unter deviceids-medp.wdr.de noch
#	einige Minuten erhalten, führt jedoch ins Leere. Ohne Link: Notific.
# 04.03.2022 einige Seiten enthalten bereits eine .m3u8-Quelle während 
#	der Lokalzeit - außerhalb Verzweigung via deviceids-medp.wdr.de mit
#	js-Dateilink zum Livestream WDR od. Störungsbild.
# 14.07.2023 nicht für ShowSeekPos geeignet - alle Streams starten verzögert am
#	Pufferanfang, zeigen "large audio sync error" - s.a. ARDSportVideo
#	
def WDRstream(path, title, img, summ):
	PLog('WDRstream:')
	summ = summ.replace( '||', '\n')
	img_org=img
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in WDRstream:"
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	page=py2_decode(page)					
	
	vonbis = stringextract('>Hier sehen Sie ', ' die Lokalzeit ', page)	# 19.30 - 20.00 Uhr
	m3u8_url = stringextract('"videoURL" : "', '"', page)			# .m3u8-Quelle vorh.?
	pos = page.find('videoLink live">')
	img = stringextract('"contentUrl" : "', '"', page[pos:])
	if img == "" or "json_logo_amp" in img:			# http-Error 404
		img = img_org
	PLog(m3u8_url)
	PLog(img)
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	if m3u8_url:
		PLog("detect_videoURL")
		if m3u8_url.startswith('http') == False:		
			m3u8_url = 'https:' + m3u8_url						# //wdrlokalzeit.akamaized.net/..
		
		if SETTINGS.getSetting('pref_video_direct') == 'true': 	# Sofortstart
			PLog('Sofortstart: WDRstream')
			PlayVideo(url=m3u8_url, title=title, thumb=img, Plot=summ, live="")
			return	
		else:
			summ_par = summ.replace('\n', '||')
			title=py2_encode(title); summ_par=py2_encode(summ_par)
			img=py2_encode(img); m3u8_url=py2_encode(m3u8_url)
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': ''}" %\
				(quote_plus(m3u8_url), quote_plus(title), quote_plus(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
				mediatype=mediatype, tagline=title, summary=summ)
				 				 
	else:														# keine m3u8-Quelle vorh.
		PLog("no_videoURL")	
		summ = "%s | außerhalb dieser Zeiten zeigen einige Sender den Livestream des WDR" % vonbis
		if 'deviceids-medp.wdr.de' in page:
			PLog("detect_deviceids")
			ARDSportVideo(path, title, img, summ, page=page)
		else:
			icon=img_org
			msg1 = u"Sendungszeiten"
			msg2 = vonbis									
			xbmcgui.Dialog().notification(msg1,msg2,icon,3000, sound=True)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------------------------------------------------------------------------------
#	17.02.2018 Video-Sofort-Format wieder entfernt (V3.1.6 - V3.5.0)
#		Forum:  https://forums.plex.tv/discussion/comment/1606010/#Comment_1606010
#		Funktionen: remoteVideo, Parseplaylist, SenderLiveListe, TestOpenPort
#	14.12.2018 für Kodi wieder eingeführt (Kodi erlaubt direkten Playerstart).
#-----------------------------------------------------------------------------------------------------

###################################################################################################
# Auswahl der Auflösungstufen des Livesenders - Aufruf: SenderLiveListe + ARDStartRubrik
#	Herkunft Links: livesenderTV.xml (dto. bei Aufruf durch ARDStartRubrik).
#	descr: tagline | summary
#	Startsender ('' oder true): Aufrufer ARDStartRubrik, ARDStartSingle (ARD-Neu)
# 16.05.2019 Fallback hinzugefügt: Link zum Classic-Sender auf Webseite
#	mögl. Alternative: Senderlinks aus ARD-Neu (s. Watchdog_TV-Live.py).	
# 25.06.2020 Fallback-Code (Stream auf classic.ardmediathek.de/tv/live ermitteln)
#	wieder entfernt - nur für ARD-Sender + selten gebraucht.
# 26.06.2020 Aktualisierung der EPG-Daten (abhängig von EPG-Setting, außer bei 
#	EPG_ShowSingle) - relevant für Aufrufe aus Merkliste.
#	Sender: Sendername bei Aufrufen durch EPG_ShowSingle (title mit EPG-Daten
#			belegt)
#	start_end: EPG-Start-/Endzeit Unix-Format für Kontextmenü (EPG_ShowSingle <-)
# 04.04.2021 Anpassung für Radiosender (z.B. MDR Fußball-Radio Livestream)
# 08.06.2021 Anpassung für Radiosender (Endung /mp3, Code an Funktionsstart)
# 17.08.2023 Anpassung für mp4-Livestreams von //sportschau-dd (Sofortstart AUS)
#
def SenderLiveResolution(path, title, thumb, descr, Merk='false', Sender='', start_end='', homeID=''):
	PLog('SenderLiveResolution:')
	PLog(title); PLog(path); PLog(thumb); PLog(descr); PLog(Sender);
	path_org = path

	# Radiosender in livesenderTV.xml ermöglichen (ARD Audio Event Streams)
	link_ext = ["mp3", '.m3u', 'low', '=ard-at']	# auch ../stream/mp3
	switch_audio = False
	for ext in link_ext:
		if path_org.endswith(ext):
			switch_audio = True
	if switch_audio or 'sportradio' in path_org:	# sportradio-deutschland o. passende Ext.
		PLog("Audiolink: %s" % path_org) 
		li = xbmcgui.ListItem()
		li.setProperty('IsPlayable', 'false')			
		PlayAudio(path_org, title, thumb, Plot=title)  # direkt	
		return

	page, msg = get_page(path=path)					# Verfügbarkeit des Streams testen
	if page == '':
		msg1 = u'SenderLiveResolution: Stream nicht verfügbar'
		msg2 = path[:50] + ".."
		msg3 = msg
		PLog(msg1)
		MyDialog(msg1, msg2, msg3)
		# xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False) # Fehlschlag - raus
		return										# endOfDirectory reicht hier nicht
		
	# EPG aktualisieren? Der Titel mit ev. alten EPG-Daten wird durch Sendungstitel
	#	ersetzt. Setting unbeachtet, falls Aufruf mit Sender erfolgt (EPG_ShowSingle):
	if Sender or SETTINGS.getSetting('pref_use_epg') == 'true':
		if Sender:									# EPG_ShowSingle: title=EPG-Daten
			title = Sender
		playlist_img, link, EPG_ID= get_playlist_img(title)
		if EPG_ID:
			rec = EPG.EPG(ID=EPG_ID, mode='OnlyNow')
			if rec:
				sname=py2_encode(rec[3]); stime=py2_encode(rec[4]); 
				summ=py2_encode(rec[5]); vonbis=py2_encode(rec[6])	
				PLog(summ); PLog(stime); PLog(vonbis)
				if sname:								# Sendung ersetzt Titel
					title = sname
				if summ:
					descr = summ
				if vonbis:
					descr = "%s | %s" % (summ, vonbis)
		else:
			descr = "EPG-Daten fehlen"					


	# direkter Sprung hier erforderlich, da sonst der Player mit dem Verz. SenderLiveResolution
	#	startet + fehlschlägt.
	# 04.08.2019 Sofortstart nur noch abhängig von Settings und nicht zusätzlich von  
	#	Param. Merk.
	PLog(SETTINGS.getSetting('pref_video_direct'))
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Sofortstart
		PLog('Sofortstart: SenderLiveResolution')
		PlayVideo(url=path, title=title, thumb=thumb, Plot=descr, live="true")
		return
	
	url_m3u8 = path
	PLog(title); PLog(url_m3u8);

	li = xbmcgui.ListItem()
	if "kikade-" in path or path.startswith("https://kika"):
		li = home(li, ID='Kinderprogramme')		# Home-Button
	else:
		if homeID:
			li = home(li, ID=homeID)
		else:	
			li = home(li, ID=NAME)				# Home-Button
										
	# Spezialbehandlung für N24 - Test auf Verfügbarkeit der Lastserver (1-4),
	# entf. mit Umstellung auf IPTV-Links in V4.3.8
		
	# alle übrigen (i.d.R. http-Links), Videoobjekte für einzelne Auflösungen erzeugen,
	# 	Mehrkanalstreams -> PlayButtonM3u8
	if url_m3u8.endswith('master.m3u8') or url_m3u8.endswith('index.m3u8'): # Vorrang vor .m3u8
		# Parseplaylist -> CreateVideoStreamObject pro Auflösungstufe
		PLog("title: " + title)
		descr = "%s\n\n%s" % (title, descr)
		PLog("descr: " + descr)
		li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=descr, live=True) # mit url_check
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
							
	elif url_m3u8.find('.m3u8') >= 0: 
		# 1 Button für autom. Auflösung (z.B. IPTV-Links) 
		# 
		PLog(url_m3u8)
		if url_m3u8.startswith('http'):			# URL extern? (lokal entfällt Eintrag "autom.")
												# Einzelauflösungen + Ablage master.m3u8:
			li = PlayButtonM3u8(li, url_m3u8, thumb, title, tagline=title, descr=descr)	
									
	else:	# keine oder unbekannte Extension - Format unbekannt,
			# Radiosender s.o.
			# 17.08.2023 Ausnahme mp4-Streams von sportschau-dd nach ARD-Änderung des 
			#	api-Calls für Startseite
		if "//sportschau-dd" in url_m3u8:
			title=py2_encode(title); url_m3u8=py2_encode(url_m3u8);
			thumb=py2_encode(thumb); descr=py2_encode(descr)
			fparams="&fparams={'url': '%s','title': '%s','thumb': '%s','Plot': '%s', 'live': 'true'}" %\
				(quote_plus(url_m3u8), quote_plus(title), quote_plus(thumb), 
				quote_plus(descr))	
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
				mediatype='video', summary=descr) 		
		else:
			msg1 = 'SenderLiveResolution: unbekanntes Format. Url:'
			msg2 = url_m3u8
			PLog(msg1)
			MyDialog(msg1, msg2, '')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------
# Aufruf: Parseplaylist (bei Mehrkanalstreams), SenderLiveResolution
# Einzelbutton für ausgewählte Livestreams
# 31.05.2022 umbenannt (vorm. ParseMasterM3u), Code für relative Pfade 
#	entfernt, ausschl. Behandl. .m3u8 (.master.m3u8 in Parseplaylist),
#	Verzicht auf lokale Dateiablage
#
def PlayButtonM3u8(li, url_m3u8, thumb, title, descr, tagline='', sub_path='', stitle=''):	
	PLog('PlayButtonM3u8:'); 
	PLog(title); PLog(url_m3u8); PLog(thumb); PLog(tagline);
	
	li = xbmcgui.ListItem()								# li kommt hier als String an
	title=unescape(title); title=repl_json_chars(title)
	
	tagline	= tagline.replace('||','\n')				# s. tagline in ZDF_get_content
	descr_par= descr; descr_par	 = descr_par.replace('\n', '||')
	descr	 = descr.replace('||','\n')					# s. descr in ZDF_get_content
	title = "autom. | " + title

	title=py2_encode(title); url_m3u8=py2_encode(url_m3u8);
	thumb=py2_encode(thumb); descr_par=py2_encode(descr_par); sub_path=py2_encode(sub_path);
	fparams="&fparams={'url': '%s','title': '%s','thumb': '%s','Plot': '%s','sub_path': '%s','live': 'true'}" %\
		(quote_plus(url_m3u8), quote_plus(title), quote_plus(thumb), 
		quote_plus(descr_par), quote_plus(sub_path))	
	addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
		mediatype='video', tagline=tagline, summary=descr) 

	return li
#-----------------------------
# Spezialbehandlung für N24 - Test auf Verfügbarkeit der Lastserver (1-4): wir prüfen
# 	die Lastservers durch, bis einer Daten liefert
def N24LastServer(url_m3u8):	
	PLog('N24LastServer: ' + url_m3u8)
	url = url_m3u8
	
	pos = url.find('index_')	# Bsp. index_1_av-p.m3u8
	nr_org = url[pos+6:pos+7]
	PLog(nr_org) 
	for nr in [1,2,3,4]:
		# PLog(nr)
		url_list = list(url)
		url_list[pos+6:pos+7] = str(nr)
		url_new = "".join(url_list)
		# PLog(url_new)
		try:
			req = Request(url_new)
			r = urlopen(req)
			playlist = r.read()			
		except:
			playlist = ''
			
		PLog(playlist[:20])
		if 	playlist:	# playlist gefunden - diese url verwenden
			return url_new	
	
	return url_m3u8		# keine playlist gefunden, weiter mit Original-url
	
###################################################################################################
def BilderDasErste(path=''):
	PLog("BilderDasErste:")
	PLog(path)
	searchbase = 'https://www.daserste.de/search/searchresult-100.js'
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	if path == '':										# Gesamt-Seitenübersicht laden
		path = 'https://www.daserste.de/search/searchresult-100.jsp?searchText=bildergalerie'
		page, msg = get_page(path)	
		if page == '':
			msg1 = ' Übersicht kann nicht geladen werden.'
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
	
		pages = blockextract('class="entry page', page)
		for rec in pages:
			href 	= stringextract('href="', '"', rec)
			href	= searchbase + href
			nr 		= stringextract('">', '</a>', rec)	# ..&start=40">5</a
			title 	= "Bildgalerien Seite %s" % nr
			fparams="&fparams={'path': '%s'}" % (quote(href))
			addDir(li=li, label=title, action="dirList", dirID="BilderDasErste", fanart=R(ICON_MAIN_ARD),
				thumb=R('ard-bilderserien.png'), fparams=fparams)
		
	else:	# -----------------------					# 10er-Seitenübersicht laden		
		page, msg = get_page(path)	
		if page == '':
			msg1 = ' %s kann nicht geladen werden.' % title
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
		
		entries = blockextract('class="teaser">', page)
		for rec in entries:
			headline =  stringextract('class="headline">', '</h3>', rec)
			href =  stringextract('href="', '"', headline)
			title =  cleanhtml(headline); title=mystrip(title)
			title =  title.strip()
			title = unescape(title); title = repl_json_chars(title)		# \n

			dach =  stringextract('class="dachzeile">', '</p>', rec)	# \n
			tag = cleanhtml(dach); tag = unescape(tag); 
			tag = mystrip(tag);	
	
			teasertext =  stringextract('class="teasertext">', '</a>', rec)
			teasertext = cleanhtml(teasertext); teasertext = mystrip(teasertext)
			summ = unescape(teasertext.strip())
			
			
			PLog("Satz21:")
			PLog(href); PLog(title); PLog(summ); PLog(tag);		
			
			href=py2_encode(href); title=py2_encode(title);	
			fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title), quote(href))
			addDir(li=li, label=title, action="dirList", dirID="BilderDasErsteSingle", fanart=R(ICON_MAIN_ARD),
				thumb=R('ard-bilderserien.png'), tagline=tag, summary=summ, fparams=fparams)
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#--------------------------------------------------------------------------------------------------	
# 23.09.2021 Umstellung Bildname aus Quelle statt "Bild_01" (eindeutiger beim
#	Nachladen) - wie ZDF_BildgalerieSingle.
#
def BilderDasErsteSingle(title, path):					  
	PLog("BilderDasErsteSingle:")
	PLog(title)
	
	li = xbmcgui.ListItem()
	
	page, msg = get_page(path)	
	if page == '':
		msg1 = ' %s kann nicht geladen werden.' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
		
	li = home(li, ID=NAME)				# Home-Button
	content = blockextract('class="teaser">', page)
	PLog("content: " + str(len(content)))
	if len(content) == 0:										
		msg1 = 'BilderDasErsteSingle: keine Bilder gefunden.'
		msg2 = title
		MyDialog(msg1, msg2, '')
		return li
	
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
	
	image=0; background=False; path_url_list=[]; text_list=[]
	base = 'https://' + urlparse(path).hostname
	for rec in content:
		# headline, title, dach fehlen
		#	xl ohne v-vars									# json-Bilddaten
		imgs = stringextract('data-ctrl-attributeswap=', 'class="img"', rec)		
		img_src = stringextract("l': {'src':'", "'", imgs)	# Blank vor {	
		if img_src == '':
			img_src = stringextract("m':{'src':'", "'", imgs)		
		if img_src == '':
			continue
		
		img_src = base + img_src	
		img_src = img_src.replace('v-varxs', 'v-varxl')		# ev. attributeswap auswerten 
		
		alt = stringextract('alt="', '"', rec)	
		alt=unescape(alt); 
		title = stringextract('title="', '"', rec)	
		# tag = "%s | %s" % (alt, title)
		tag = alt
		lable = title
		
		teasertext =  stringextract('class="teasertext">', '</a>', rec)
		teasertext = cleanhtml(teasertext); teasertext = mystrip(teasertext)
		summ = unescape(teasertext)
		tag=repl_json_chars(tag) 
		title=repl_json_chars(title); summ=repl_json_chars(summ); 
		PLog("Satz22:")
		PLog(img_src); PLog(title); PLog(tag[:60]); PLog(summ[:60]); 		
			
		#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
		#	nicht zum Imageformat passen
		#pic_name 	= 'Bild_%04d.jpg' % (image+1)			# Bildname
		pic_name 	= img_src.split('/')[-1]				# Bildname aus Quelle
		local_path 	= "%s/%s" % (fpath, pic_name)
		PLog("local_path: " + local_path)
		title = "Bild %03d: %s" % (image+1, pic_name)		# Numerierung
		if len(title) > 70:
			title = "%s.." % title[:70]						# Titel begrenzen
		
		PLog("Bildtitel: " + title)
		
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		if os.path.isfile(local_path) == False:				# schon vorhanden?
			# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Bild-Url, 
			#	Zieldatei_kompletter_Pfad|Bild-Url ..
			path_url_list.append('%s|%s' % (local_path, img_src))

			if SETTINGS.getSetting('pref_watermarks') == 'true':
				txt = "%s\n%s\n%s\n%s\n%s" % (fname,title,lable,tag,summ)
				text_list.append(txt)	
			background	= True											
								
		title=repl_json_chars(title); summ=repl_json_chars(summ)
		PLog('neu:');PLog(title);PLog(img_src);PLog(thumb);PLog(summ[0:40]);
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
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
				
		lable = u"Alle Bilder in diesem Bildverzeichnis löschen"		# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  	# ohne Cache, um Neuladen zu verhindern
		
	
				  
####################################################################################################
# 29.09.2019 Umstellung Radio-Livestreams auf ARD Audiothek
#	Codebereinigung - gelöscht: 
#		RadioLiveListe, RadioAnstalten, livesenderRadio.xml, 77 Radio-Icons (Autor: Arauco)
#

###################################################################################################
#									ZDF-Funktionen
###################################################################################################
# Startseite der ZDF-Mediathek 
# Neu: April 2023	
#
def ZDF_Start(ID, homeID=""): 
	PLog('ZDF_Start: ' + ID);
	 
	base = "https://zdf-prod-futura.zdf.de/mediathekV2/"					
	if ID=='Startseite':
		path = base + "start-page"
	elif ID=="tivi_Startseite":
		path = base + "document/zdftivi-fuer-kinder-100"
	elif ID=="funk-Startseite":
		path = base + "document/funk-126"	
		
	DictID =  "ZDF_%s" % ID
	page = Dict("load", DictID, CacheTime=ZDF_CacheTime_Start)	# 5 min				
	if not page:												# nicht vorhanden oder zu alt						
		icon = R(ICON_MAIN_ZDF)
		if ID.startswith("tivi"):
			icon = GIT_TIVIHOME
		xbmcgui.Dialog().notification("Cache %s:" % ID,"Haltedauer 5 Min",icon,3000,sound=False)

		page, msg = get_page(path)								# vom Sender holen		
		if page == "":
			msg1 = 'Fehler in ZDF_Start:'
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
		else:
			jsonObject = json.loads(page)
			Dict('store', DictID, jsonObject)		# jsonObject -> Dict, ca. 10 MByte, tivi 8.5 MByte
	else:
		jsonObject = page
		
	PLog("jsonObject1: " + str(jsonObject)[:80])
	ZDF_PageMenu(DictID,jsonObject=jsonObject,url=path)
	
	# 05.03.2024 frühere Calls direkt verlinkt in Main_ZDF -> ZDF_RubrikSingle:
	#	Rubriken, Sportstudio, Barrierearm, ZDFinternational
	return
	
#---------------------------------------------------------------------------------------------------
# Aufruf ZDF_Start mit jsonObject direkt,
#		ZDF_RubrikSingle mit DictID (-> gespeichertes jsonObject)
# mark: Titelmarkierung, z.B. für ZDF_Search
# 13.05.2023 zusätzl. urlkey (Kompensation falls jsonObject fehlt),
#	Format urlkey: "%s#cluster#%d" % (url, obj_id, obj_nr)
# 02.10.2023 recommendation-Inhalte (ZDF, ARD-Links): DictID auf urlkey-
#	Basis ("ZDF_reco_%s" % scmsid)
# 21.03.2024 CacheTime für DictID (30 min), um Aktualisierung bei Favoriten
#	 und Merkliste sicherzustellen, ergänzt mit url ohne key zum Nachladen 
#	von Startseiten (s. ZDF_Start)
# 
#	
def ZDF_PageMenu(DictID,  jsonObject="", urlkey="", mark="", li="", homeID="", url=""):								
	PLog('ZDF_PageMenu:')
	PLog('DictID: ' + DictID)
	PLog(mark); PLog(homeID);  
	url_org = url; PLog("url_org: " + url_org)
	li_org=li 

	if not jsonObject and DictID:
		jsonObject = Dict("load", DictID, CacheTime=ZDF_CacheTime_AZ)	# 30 min		
	if not jsonObject:								# aus Url wiederherstellen (z.B. für Merkliste)
		if url:										# url ohne key (Seiten ZDF_Start)
			PLog("get_from_url:")
			page, msg = get_page(path=url, header=HEADERS)
			jsonObject = json.loads(page)
		if urlkey:									# ZDF_RubrikSingle: "%s#cluster#%s" % (url, cnt)
			PLog("get_from_urlkey:")
			if "/recommendation/" in urlkey:		# recommendation-Inhalte (wie Web "clusterrecommendation"),
				page, msg = get_page(path=urlkey, header=HEADERS)   # z.B. Empf. der Redaktion
			else:
				url, obj_id, obj_nr = urlkey.split("#")
				PLog("obj_id: %s, obj_nr: %s" % (obj_id, obj_nr))
				page, msg = get_page(path=url)

			try:
				jsonObject = json.loads(page)
				if "/recommendation/" not in urlkey:
					jsonObject = jsonObject[obj_id][int(obj_nr)]
				else:								# recommendation: teaser bei ZDF, Cluster bei ARD
					scmsid = stringextract("configuration=", "&", urlkey) # zdfinfo-trending, ARD: automated_seasons
					DictID = "ZDF_reco_%s" % scmsid	# eigene DictID
					Dict('store', DictID, jsonObject)
					
			except Exception as exception:
				PLog(str(exception))
				jsonObject=""

	if not jsonObject:
		msg1 = u'ZDF_PageMenu: Beiträge können leider nicht geladen werden.'
		MyDialog(msg1, '', '')
		return	
	PLog(str(jsonObject)[:80])
	
	validchars=True										# -> valid_title_chars in ZDF_get_content
	if DictID.startswith("ZDF_international"):
		validchars=False	
		
	if not li:	
		li = xbmcgui.ListItem()
	if "ZDF_tivi" in DictID or "Kinder" in homeID:
		homeID = "Kinderprogramme"
		li = home(li, ID=homeID)
	else:
		li = home(li, ID="ZDF")				# Home-Button
	li2 = xbmcgui.ListItem()										# mediatype='video': eigene Kontextmenüs in addDir							
		
	mediatype=''													# Kennz. Videos im Listing
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	PLog('mediatype: ' + mediatype); 
	
	PLog("stage" in jsonObject); PLog("teaser" in jsonObject); PLog("results" in jsonObject);		
	if "stage" in jsonObject or "teaser" in jsonObject or "results" in jsonObject:
		PLog('ZDF_PageMenu_stage_teaser')
		stage=False
		
		if DictID == "ZDF_Startseite" or "tivi_" in DictID or "funk-" in DictID:
			if "stage" in jsonObject:								# <- ZDF-Start, tivi-Start
				entryObject = jsonObject["stage"]
				PLog("stage_len: %d" % len(entryObject))
				stage=True
		if "teaser" in jsonObject:									# ZDF_RubrikSingle
			entryObject = jsonObject["teaser"]
			PLog("teaser: %d" % len(entryObject))
		if  "results" in jsonObject:								# ZDF_Search
			entryObject = jsonObject["results"]
			PLog("results: %d" % len(entryObject))
			
		for entry in entryObject:
			typ,title,tag,descr,img,url,stream,scms_id = ZDF_get_content(entry,mark=mark,validchars=validchars)
			label=""
			if stage:
				label = "[B]TOP:[/B]"
			label = "%s %s" % (label, title)
			
			PLog("Satz1_1:")
			PLog(stage); PLog(typ); PLog(title);
			title = repl_json_chars(title)
			tag = repl_json_chars(tag)
			if typ=="video":								# Videos
				if SETTINGS.getSetting('pref_usefilter') == 'true':	# Ausschluss-Filter
					filtered=False
					for item in AKT_FILTER: 
						if up_low(item) in py2_encode(up_low(str(entry))):
							filtered = True
							break		
					if filtered:
						PLog('filtered_1: <%s> in %s ' % (item, title))
						continue								
				if "channel" in entry:								# Zusatz Sender
					sender = entry["channel"]
					tag = "%s | %s" % (tag, sender)
				if stream == "":									# Bsp.: ZDFtivi -> KiKA live
					stream = url
				fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','tag': '%s','summ': '%s','scms_id': '%s'}" %\
					(stream, title, img, tag, descr, scms_id)
				PLog("fparams: " + fparams)	
				addDir(li=li2, label=label, action="dirList", dirID="ZDF_getApiStreams", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, summary=descr, mediatype=mediatype)
			elif typ=="livevideo":
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
				PLog("fparams: " + fparams)	
				addDir(li=li2, label=title, action="dirList", dirID="ZDF_Live", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag, mediatype=mediatype)   
			elif typ=="externalUrl":						# Links zu anderen Sendern
				if "KiKANiNCHEN" in title:
					PLog("ZDF_PageMenu_Link_KiKANiNCHEN")
					KIKA_START="https://www.kika.de/bilder/startseite-104_v-tlarge169_w-1920_zc-a4147743.jpg"	# ab 07.12.2022
					GIT_KANINCHEN="https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchen.png?raw=true"					
					fparams="&fparams={}" 
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Menu", 
						fanart=KIKA_START, thumb=GIT_KANINCHEN, tagline='für Kinder 3-6 Jahre', fparams=fparams)
				if "Zahlen zur" in title:							# Wahlbeiträge, Statistiken
					PLog("skip_externalUrl: " + title)
				
			else:
				fparams="&fparams={'url': '%s', 'title': '%s', 'homeID': '%s'}" % (url, title, homeID)
				PLog("fparams: " + fparams)	
				addDir(li=li, label=label, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag)
							
						
	if("cluster" in jsonObject):		# Bsp- A-Z Leitseite -> SingleRubrik
		PLog('ZDF_PageMenu_cluster')
		for counter, clusterObject in enumerate(jsonObject["cluster"]):	# Bsp. "name":"Neu in der Mediathek"
			title=""; url=""
			try:													# detect PromoTeaser (Web: ganze Breite)
				typ = clusterObject["type"]
				url = clusterObject["promoTeaser"]["url"]
			except:
				typ=""	

			if "name" in clusterObject:
				title = clusterObject["name"]
			if title == '':											# "teaser": [.. - kann leer sein
				PLog(str(clusterObject["teaser"])[:60])
				if clusterObject["teaser"]:
					title = clusterObject["teaser"][0]['titel']
			if clusterObject["teaser"]:
				img = ZDF_get_img(clusterObject["teaser"][0])
			if "promoTeaser" in clusterObject:						#  PromoTeaser
				img = ZDF_get_img(clusterObject["promoTeaser"])
				
			tag = "Folgeseiten"
			descr=""
			if  "beschreibung" in clusterObject:
				descr = clusterObject["beschreibung"]
			
			# skip: personalisierten Inhalte, Addon-Menüs:
			skip_list = ['Alles auf einen Blick', u'Das könnte Dich', 'Direkt zu',
						'Mein Programm', 'Deine', 'KiKA live sehen', 'Weiterschauen',
						'Mehr zu funk', 'Trending'
						 ]
			skip=False						
			if title == '':
				PLog('ohne_Titel: %s' % str(clusterObject)[:80])	# ?
				skip = True 
			for t in skip_list:
				# PLog("t: %s, title: %s" % (t, title))
				if title.startswith(t) or title.endswith(t):
					PLog("skip: %s" % title)
					skip = True 
			if skip:
				continue 
				
			jsonpath = "cluster|%d|teaser" % counter
			title = repl_json_chars(title)
			descr = repl_json_chars(descr)
			PLog("Satz1_2:")
			PLog(DictID); PLog(title); PLog(jsonpath); PLog(typ);
						
			if typ != "teaserPromo": 
				fparams="&fparams={'jsonpath':'%s','title':'%s','DictID':'%s','homeID':'%s','url':'%s'}"  %\
					(jsonpath, title, DictID, homeID, url_org)		# url_org i.V.m. jsonpath=Fallback
				PLog("fparams: " + fparams)	
				addDir(li=li, label=title, action="dirList", dirID="ZDF_Rubriken", 				
					fanart=img, thumb=img, tagline=tag, summary=descr, fparams=fparams)
			else:													# teaserPromo - s.o.		
				tag = "[B]Promo-Teaser[/B] | %s" % tag
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
				PLog("fparams: " + fparams)	
				addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag)
				
			if title == "Das ZDF im Livestream":					# Ausland-Livestreams ergänzt,
				title = "Livestreams im Ausland"					# 	skipped: Alles auf einen Blick
				url = "https://zdf-prod-futura.zdf.de/mediathekV2/document/einzel-livestreams-100"
				img = "https://www.zdf.de/assets/rubrik-livestreams-im-ausland-100~1280x720?cb=1660040584240"
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
				PLog("fparams: " + fparams)	
				addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag)

		title = "Terra X plus Schule"					# 	skipped: Alles auf einen Blick
		url = "https://zdf-prod-futura.zdf.de/mediathekV2/document/terra-x-plus-schule-100"
		img = "https://www.zdf.de/assets/terrax-plusschule-buehnes-100~1140x240?cb=1698932648730"
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
		PLog("fparams: " + fparams)	
		addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
			thumb=img, fparams=fparams, summary=descr, tagline=tag)


	if li_org:
		return li
	else:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

###################################################################################################
# Aufruf: ZDF_PageMenu
# ZDF-Rubriken (Film, Serie,  Comedy & Satire,  Politik & Gesellschaft, ZDF im Livestream, ..)
# path: json-key-Pfad (Bsp. cluster|2|teaser) 
# 02.10.2023 für ARD-Inhalte des ZDF stream=url (abweichendes json-Format)
# 18.03.2024 url i.V.m. jsonpath=Fallback bei Ausfall Dict (DictID)
#
def ZDF_Rubriken(jsonpath, title, DictID, homeID="", url=""):								
	PLog('ZDF_Rubriken: ' + DictID)
	PLog("jsonpath: " + jsonpath)
	jsonpath_org = jsonpath

	if DictID:
		jsonObject = Dict("load", DictID, CacheTime=ZDF_CacheTime_AZ)
	if not jsonObject:								# aus Url + wiederherstellen 
		PLog("get_from_url:")
		page, msg = get_page(path=url, header=HEADERS)
		jsonObject = json.loads(page)
	
	jsonObject, msg = GetJsonByPath(jsonpath, jsonObject)
	if jsonObject == '':					# index error
		msg1 = 'Cluster [B]%s[/B] kann nicht geladen werden.' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(str(jsonObject)[:80])
					
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
	else:
		li = home(li, ID='ZDF')						# Home-Button
	li2 = xbmcgui.ListItem()						# mediatype='video': eigene Kontextmenüs in addDir							
		
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
		
	i=0
	PLog("walk_entries: %d" % len(jsonObject))					
	for entry in jsonObject:
		jsonpath = jsonpath_org + '|%d' % i
		PLog("entry_type1: " + entry["type"])
				
		typ,title,tag,descr,img,url,stream,scms_id = ZDF_get_content(entry)
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)
		tag = repl_json_chars(tag)
		if stream == "":												# ARD-Inhalte: o. length
			stream = url
			tag = tag.replace("Folgeseiten", "Video")
		if typ == "video":	
			if SETTINGS.getSetting('pref_usefilter') == 'true':			# Ausschluss-Filter
				filtered=False
				for item in AKT_FILTER: 
					if up_low(item) in py2_encode(up_low(str(entry))):
						filtered = True
						break		
				if filtered:
					PLog('filtered_2: <%s> in %s ' % (item, title))
					continue								
			if "channel" in entry:										# Zusatz Sender
				sender = entry["channel"]
				tag = "%s | %s" % (tag, sender)
			fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','tag': '%s','summ': '%s','scms_id': '%s'}" %\
				(stream, title, img, tag, descr, scms_id)	
			addDir(li=li2, label=title, action="dirList", dirID="ZDF_getApiStreams", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=descr, mediatype=mediatype)	
		elif typ == "livevideo":
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
			PLog("fparams: " + fparams)	
			addDir(li=li2, label=title, action="dirList", dirID="ZDF_Live", fanart=img, 
				thumb=img, fparams=fparams, summary=descr, tagline=tag, mediatype=mediatype)
		elif typ == "externalUrl": 
			PLog("externalUrl_not_used")
					
		else:
			tag = "Folgeseiten"
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
			PLog("fparams: " + fparams)	
			addDir(li=li, label=title, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
				thumb=img, fparams=fparams, summary=descr, tagline=tag)
													
		i=i+1
		# break		# Test Einzelsatz		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

###################################################################################################
# einzelne ZDF-Rubrik (Film, Serie,  Comedy & Satire,  Politik & Gesellschaft, ..)
# Cluster-Objekte > 1: Dict-Ablage mit DictID je Cluster -> PageMenu. Die Dicts 
#	werden bei jedem Durchlauf überschrieben (max. Cachezeit=Cachezeit der entspr. Leitseite,
#	s. ZDF_Start).
# einz. Cluster-Objekt: Auswertung Teaser -> wieder hierher, ohne Dict
# 01.10.2023 Auswertung recommendation-Inhalte (ohne Cache, DictID leer), dabei 
#	Verzicht auf {bookmarks}-Urls ("Das könnte Dich interessieren", kodinerds Post 3.134)
# 02.12.2023 Auswertung Navigationsmenü (ZDF-Sportstudio, ZDFtivi)
#
def ZDF_RubrikSingle(url, title, homeID=""):								
	PLog('ZDF_RubrikSingle: ' + title)
	PLog("url: " + url)
	title_org = title
	noicon = R(ICON_MAIN_ZDF)									# notific.

	page=""; AZ=False
	if url.endswith("sendungen-100"):							# AZ Gesamt ca. 12 MByte -> Dict
		page = Dict("load", "ZDF_sendungen-100", CacheTime=ZDF_CacheTime_AZ)
		AZ=True
	if not page:	
		page, msg = get_page(path=url)
		if not page:											# nicht vorhanden?
			msg1 = 'ZDF_RubrikSingle: [B]%s[/B] kann nicht geladen werden.' % title
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
		if AZ:
			page = json.loads(page)
			Dict("store", "ZDF_sendungen-100", page)
	
	if "dict" in str(type(page)):								# AZ: json
		jsonObject = page
	else: 
		jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
		
	navi=False
	if "navigation"	in jsonObject:								# Navigations-Menü?, Bsp. Sportstudio
		navi=True		
		
	clusterObject, msg = GetJsonByPath("cluster", jsonObject)
	if clusterObject == '':					# index error
		msg1 = 'Rubrik [B]%s[/B] kann nicht geladen werden.' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(str(clusterObject)[:80])
	PLog("Cluster: %d " % len(clusterObject))
	
	if len(clusterObject) == 0:									# z.B. Wahltool, ohne Videos
		msg1 = u"%s" % title
		msg2 = u'keine Videos gefunden'
		xbmcgui.Dialog().notification(msg1,msg2,noicon,2000,sound=True)
		return
	
	#--------------------------------
			
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
	else:	
		li = home(li, ID='ZDF')				# Home-Button
	li2 = xbmcgui.ListItem()									# mediatype='video': eigene Kontextmenüs in addDir							
	
	mediatype=''												# Kennz. Videos im Listing
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	PLog('mediatype: ' + mediatype); 
						
	if navi:													# Navigations-Menü voranstellen
		PLog("add_navi_menu:")									# Ausw. livestreamsTeaser s.u.
		obj = jsonObject["navigation"]
		PLog(str(obj)[:80])
		DictID = "ZDF_navigation"
		Dict("store", DictID, obj)
		label = jsonObject["navigation"]["name"]
		fparams="&fparams={'DictID': '%s', 'title': '%s', 'homeID': '%s'}" % (DictID, title, homeID)
		addDir(li=li, label=label, action="dirList", dirID="ZDF_get_navi", fanart=R(ICON_DIR_FOLDER), 
			thumb=R(ICON_DIR_FOLDER), fparams=fparams, tagline=u"Navigations-Menü")
		
						
	PLog("Seriencheck:")										# Abzweig Serienliste ZDF_FlatListEpisodes
	try:
		docObject = jsonObject["document"]
	except:
		docObject=""
	if docObject:
		if "structureNodePath" in docObject:
			if "/zdf/serien/" in docObject["structureNodePath"]:
				sid = docObject["id"]							# z.B. trigger-point-102
				PLog("Serie: " + sid)
				label = "komplette Liste: %s" % title
				tag = u"Liste aller verfügbaren Folgen | strm-Tools"
				fparams="&fparams={'sid': '%s'}"	% (sid)						
				addDir(li=li, label=label, action="dirList", dirID="ZDF_FlatListEpisodes", fanart=R(ICON_DIR_FOLDER), 
					thumb=R(ICON_DIR_FOLDER), tagline=tag, fparams=fparams)

	cnt=0
	if len(clusterObject) > 1:									# mehrere Cluster
		PLog("walk_cluster: %d" % len(clusterObject))					
		for jsonObject in clusterObject:
			typ = jsonObject["type"]
			title=""; name=""
			if "name" in jsonObject:							# kann fehlen oder leer sein
				title = jsonObject["name"]
			if not title:										# z.B. type=teaserContent						
				title = title_org
			title = repl_json_chars(title)
			
			if typ == "videoCarousel":
				title = "[B]Highlights[/B]: %s" % title
			if typ == "teaserContent":							# Teaser
				if name == "":
					try:
						name = jsonObject["teaser"][0]["titel"] # Titel 1. Teaser
					except Exception as exception:
						PLog("teaserContent_error: " + str(exception))
						name = title
				title = "[B]Teaser[/B]: %s" % name
	
			urlid = url.split("/")[-1]
			urlkey = "%s#cluster#%d" % (url, cnt)				# dto			
			tag = "Folgeseiten"
			descr = ""
		
			try:
				img = ZDF_get_img(jsonObject["teaser"][0])		# fehlt/leer bei recommendation-Inhalten
				DictID = "ZDF_%s_%d" % (urlid, cnt)				# DictID: url-Ende + cluster-nr
				Dict('store', DictID, jsonObject)				# für ZDF_PageMenu	
			except Exception as exception:
				PLog("teaser_error: " + str(exception))				
				img = R(ICON_DIR_FOLDER)
				if "reference" in jsonObject:
					ref_url = jsonObject["reference"]["url"]
					if '{bookmarks}' in ref_url:				# skip personenbezogene Inhalte, s.o.
						PLog("skip_bookmarks_url:" + title)
						continue
					DictID=""
					ref_url = ref_url.replace("%2F", "/")
					urlkey = ref_url.replace('{&appId,abGroup}', '&appId=exozet-zdf-pd-0.99.2145&abGroup=gruppe-a')
					descr = u"[B]Vorschläge der Redaktion[/B]"
					PLog("new_urlkey: " + urlkey)
				else:											# o. teaser, o. reference-Url, Bsp. Weiterschauen
					PLog("reference_missing: " + title)
					continue										
			
			PLog("Satz6_1:")
			urlkey=py2_encode(urlkey)
			fparams="&fparams={'DictID': '%s', 'homeID': '%s', 'urlkey': '%s'}" % (DictID, homeID, quote(urlkey))
			PLog("fparams: " + fparams)	
			addDir(li=li, label=title, action="dirList", dirID="ZDF_PageMenu", fanart=img, 
			thumb=img, fparams=fparams, summary=descr, tagline=tag)
			cnt=cnt+1
	else:														# einzelner Cluster -> teaser-Auswertung
		teaserObject, msg = GetJsonByPath("0|teaser", clusterObject)
		if len(teaserObject) == 0:								# Bsp. Sportstudio: statt key teaser
			teaserObject, msg = GetJsonByPath("0|livestreamsTeaser", clusterObject)
			teaserObject2, msg = GetJsonByPath("0|scheduledLivestreamsTeaser", clusterObject)
			if len(teaserObject2) > 0:							# z.B. "Demnächst live"
				teaserObject = teaserObject + teaserObject2
		PLog("walk_teaser: %d" % len(teaserObject))
		PLog("Teaser: %d " % len(teaserObject))
		
		if len(teaserObject) == 0:								# z.B. Link zu ARD-Inhalten 
			ref_url=""
			obj = clusterObject[0]
			PLog(str(obj)[:80])
			# 2-facher Aufruf bei ARD-Inhalten: hier  -> ZDF_PageMenu -> hier
			#	ev. auslagern
			if "reference" in obj:								# Test auf recommendation-Verweis, Bsp.
				if "url" in obj["reference"]:					# 	https://www.zdf.de/hr/ard-crime-time
					ref_url = obj["reference"]["url"]			# ähnlich ref_url bei mehreren Clustern (s.o.)
					ref_url = ref_url.replace("%2F", "/")
					PLog(ref_url)
					ref_url = ref_url.replace('{appId}', 'exozet-zdf-pd-0.99.2145')
					urlkey = ref_url.replace('{abGroup}', 'abGroup=gruppe-a')
					PLog("new_urlkey: " + urlkey)
					img = R(ICON_DIR_FOLDER); tag=""; descr=""	
					fparams="&fparams={'DictID': '', 'homeID': '%s', 'urlkey': '%s'}" %\
						(homeID, quote(urlkey))					# o. DictID wie recommendation-Inhalte oben
					PLog("fparams: " + fparams)	
					addDir(li=li, label=title, action="dirList", dirID="ZDF_PageMenu", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag)
				
			if 	ref_url == "":									# Fehlschlag
				msg1 = u"%s" % title
				msg2 = u'keine Videos gefunden'
				xbmcgui.Dialog().notification(msg1,msg2,noicon,2000,sound=True)
				return						
				
		for entry in teaserObject:
			typ,title,tag,descr,img,url,stream,scms_id = ZDF_get_content(entry)
			title = repl_json_chars(title)
			label = title
			descr = repl_json_chars(descr)
			tag = repl_json_chars(tag)
			PLog("Satz6_2:")
			if(entry["type"]=="video"):							# Videos am Seitenkopf
				# path = 'stage|%d' % i	# entf. hier
				PLog("stream: " + stream)
				if SETTINGS.getSetting('pref_usefilter') == 'true':	# Ausschluss-Filter
					filtered=False
					for item in AKT_FILTER: 
						if up_low(item) in py2_encode(up_low(str(entry))):
							filtered = True
							break		
					if filtered:
						PLog('filtered_3: <%s> in %s ' % (item, title))
						continue								
				if "channel" in entry:							# Zusatz Sender
					sender = entry["channel"]
					tag = "%s | %s" % (tag, sender)
				fparams="&fparams={'path': '%s','title': '%s','thumb': '%s','tag': '%s','summ': '%s','scms_id': '%s'}" %\
					(stream, title, img, tag, descr, scms_id)	
				addDir(li=li2, label=label, action="dirList", dirID="ZDF_getApiStreams", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, summary=descr, mediatype=mediatype)
			else:
				fparams="&fparams={'url': '%s', 'title': '%s', 'homeID': '%s'}" % (url, title, homeID)
				addDir(li=li, label=label, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
					thumb=img, fparams=fparams, summary=descr, tagline=tag)
					
	ZDF_search_button(li, query=title_org)	
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------------------------------------------
# Aufruf: ZDF_Rubriken
# Seite enthält alle ZDF-Sender, einschl. EPG für akt. Tag
# 23.07.2023 Event-Livestreams hinzugefügt (Trigger: obj["label"] =
#	 "Livestream" oder "Jetzt live" in ZDF_get_content) 
#
def ZDF_Live(url, title): 											# ZDF-Livestreams von ZDFStart
	PLog('ZDF_Live: '  + url); 
	PLog(title)
	if "[/B]" in title:												# entfernen: [B]LIVE: [/B]
		pos = title.find("[/B]")
		title_org = title[pos+5:]
	PLog(title_org)
		
	page, msg = get_page(path=url)
	if not page:
		msg1 = u'ZDF_Live: der Stream von [B]%s[/B] kann leider nicht geladen werden.' % title
		MyDialog(msg1, "", '')
		return
	jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
	
	if '"formitaeten"' in page and '"epgCluster"' not in page:	# abweichendes Format (Events-JustInTime)
		PLog("formitaetenInPage")
		streamsObject = jsonObject["document"]["formitaeten"]
		m3u8_url = streamsObject[0]["url"]						# 1. form. = auto
		PLog("m3u8_url: " + m3u8_url)
		img = ZDF_get_img(jsonObject["document"])
	else:														# Regel-Livestreams + Events-OutOfTime		
		try:												
			for clusterObject in jsonObject["epgCluster"]:		# epgCluster bei Regel-Livestreams	
				clusterLive = clusterObject["liveStream"]
				if clusterLive["titel"] == title_org:
					break
		except Exception as exception:
			PLog("clusterLive_error: " + str(exception))
			msg1 = u'%s:' % title
			msg2 = u"leider (noch) kein Stream verfügbar."
			MyDialog(msg1, msg2, '')
			return
		streamsObject = clusterLive["formitaeten"]
		m3u8_url = streamsObject[0]["url"]						# 1. form. = auto
		img = ZDF_get_img(clusterLive)
		
	if SETTINGS.getSetting('pref_video_direct') == 'true':		# Sofortstart
		PLog("Sofortstart_ZDF_Live")
		PlayVideo(url=m3u8_url, title=title, thumb=img, Plot=title, live="true")
		return
	#----------------------
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	cnt=1; 
	for entry in streamsObject:
		url = entry["url"]
		quality = entry["quality"]
		typ = entry["type"]
		lang = entry["language"]
		label = u"%d. %s | [B]HLS %s[/B]" % (cnt, title_org, quality)
		Plot = u"Typ: %s | %s" % (typ, lang)
		
		PLog("Satz5:")
		PLog(url);PLog(quality);PLog(typ);
		title=py2_encode(title); Plot=py2_encode(Plot)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'live': 'true'}" %\
			(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(Plot)) 
		addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
			fparams=fparams, tagline=Plot, mediatype='video') 
		cnt=cnt+1		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#-------------------------
def ZDF_get_img(obj, landscape=False):
	PLog('ZDF_get_img:')
	PLog(str(obj)[:60])	
	
	minWidth=1280					# 1280x720
	if landscape:
		minWidth=1140				# 1140x240
	img=""
	try:
		if("teaserBild" in obj):
			cnt=0
			for width,imageObject in list(obj["teaserBild"].items()):
				if cnt == 0:
					img_first = imageObject["url"]		# Backup
				cnt=cnt+1
				if int(width) >= minWidth:
					img=imageObject["url"]
		if not img:
			if("image" in obj):
				cnt=0
				for width,imageObject in list(obj["image"].items()):
					if cnt == 0:
						img_first = imageObject["url"]	# Backup
					cnt=cnt+1
					if int(width) >= minWidth:
						img=imageObject["url"];
		if not img:										# Backup -> img
			img = img_first
		
	except Exception as exception:
		PLog("get_img_error: " + str(exception))

	if not img:
		img = R(ICON_DIR_FOLDER)
	PLog(img)	
	return img

#---------------------------------------------------------------------------------------------------
# mark: Titelmarkierung, z.B. für ZDF_Search
# 
def ZDF_get_content(obj, maxWidth="", mark="", validchars=True):
	PLog('ZDF_get_content:')
	PLog(str(obj)[:60])
	PLog(mark); PLog(validchars)
	
	if not maxWidth:				# Teaserbild, Altern. 1280 für Video
		maxWidth=840
	multi=True; verf=""; url=""; stream=""; scms_id=""; now_live=""
	headline=""; avail=""
	season=""; episode=""			# episodeNumber, seasonNumber
	
	if "url" in obj:
		url=obj["url"]
	if "headline" in obj:
		headline=obj["headline"]
	title=obj["titel"]
	if title.strip() == "":
		title = headline
	if title.strip() == "":			# mögl.: title/headline mit 1 Blank
		title = obj["id"]

	if mark:
		title = make_mark(mark, title, "", bold=True)	# Titel-Markierung
	
	teaser_nr=''			# wie Serien in ZDF_get_content
	if ("seasonNumber" in obj and "episodeNumber" in obj):
		season = obj["seasonNumber"]
		episode = obj["episodeNumber"]
		teaser_nr = "Staffel %s | Folge %s | " % (season, episode)
		title_pre = "S%02dE%02d" % (int(season), int(episode))
		title = "%s | %s" % (title_pre, title)
	descr=''	
	if("beschreibung" in obj):
		descr = teaser_nr + obj["beschreibung"]	
			
	typ=''	
	if("type" in obj):
		typ = obj["type"]
		if ("label" in obj):
			PLog("label: " + obj["label"])
			if obj["label"] == "Livestream":
				typ = "livevideo"								# z.B. Events, s.u. screentxt
			if obj["label"] == "Jetzt live":					# kann verzögert erscheinen 
				typ = "livevideo"					
				now_live=True									# s.u. screentxt
				
		
	img="";
	if("teaserBild" in obj):
		for width,imageObject in list(obj["teaserBild"].items()):
			if int(width) <= maxWidth:
				img=imageObject["url"];
	
	dur=''
	if("length" in obj) or typ == "video" or typ == "livevideo": # ein. Video / Livestream
		multi = False
		sec=""; fsk="none"; geo="none"; 
		if "length" in obj:
			sec = obj["length"]
		if sec:
			dur = time.strftime('%H:%M Std.', time.gmtime(sec))	
		if sec == "" and "infoline" in obj:						# z.B "45 min · Doku" in letzte chance
			if "title" in obj["infoline"]:
				PLog(str(obj["infoline"]))
				dur = obj["infoline"]["title"]
				PLog("dur: " + dur)

		avail=''; pubDate=''	
		if("offlineAvailability" in obj):
			avail = obj["offlineAvailability"]
			avail =time_translate(avail, day_warn=True)			# day_warn: noch x Tage!
			avail = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % avail
		if avail == "":			
			if "label" in obj:									# z.B. "Noch 3 Stunden" in letzte chance
				avail = obj["label"]
				avail = u"[B][COLOR darkgoldenrod]%s[/COLOR][/B]" % avail
		if("visibleFrom" in obj):
			pubDate = obj["visibleFrom"]						# 23.10.2023 00:00
			pubDate = "[B]ab: %s[/B]" % pubDate.split(" ")[0]	# o. Uhrzeit
		
		if "fsk" in obj:	
			fsk = obj["fsk"]
		if fsk == "none":
			fsk = "ohne"
		if "geo" in obj:	
			geo = obj["geoLocation"]
		if geo == "none":
			geo = "ohne"
		#if "streamApiUrlVoice" in obj:						
		#	stream = obj["streamApiUrlVoice"] # needs api-token
		if "url" in obj:
			stream = obj["url"]
		# stream = obj["cockpitPrimaryTarget"]["url"] 			# Altern. (mit url identisch)
		if "externalId" in obj:
			scms_id = obj["externalId"]
			
		# 01.10.2024 Keine api-Quelle mit umfangr. Inhaltstext wie Web gefunden:
		if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
			if "sharingUrl" in obj:								# Web-Referenz
				path=obj["sharingUrl"]
				descr_new = get_summary_pre(path, ID='ZDF',skip_verf=True,skip_pubDate=True)  # Modul util
				if 	len(descr_new) > len(descr):
					PLog("descr_new: " + descr_new[:60] )
					descr = descr_new
					
	if validchars:												# unterdrückt bei Arabic
		summ = valid_title_chars(descr)
	else:
		summ = repl_json_chars(descr)							# router-komp.

	if multi:
		tag = "Folgeseiten"
	else:
		tag = "Dauer: %s | FSK: %s | GEO: %s" % (dur, fsk, geo)
		if avail:												# kann fehlen
			tag = "%s | %s" % (tag, avail)
		if pubDate:	
			tag = "%s | %s" % (tag, pubDate)
		if typ == "livevideo":									# z.B. Events
			try:
				screentxt = obj["infoline"]["screenReaderTexts"]
				PLog("screentxt: " + str(screentxt))
				t1 = screentxt[0]["text"]						# Bsp. Livestream verfügbar
				t2 = screentxt[0]["title"]						# Bsp. Mo., 12:45 - 15:35 Uhr
				tag = "[B]%s | %s[/B]" % (t1,  t2)
				title = "[B]LIVE: [/B] %s" % title
				if now_live:
					title = "[B]JETZT[/B] %s" % title
			except Exception as exception:
				PLog("screentxt_error: " + str(exception))
				tag=""
	if headline:
		tag = "%s | [B]%s[/B]" % (tag, headline)
	
	PLog('Get_content typ: %s | title: %s | tag: %s | descr: %s |img:  %s | url: %s | stream: %s | scms_id: %s' %\
		(typ,title,tag,summ,img,url,stream,  scms_id) )		
	return typ,title,tag,summ,img,url,stream,scms_id

#---------------------------------------------------------------------------------------------------
# Navigations-Menü, z.B. Sportstudio
# Aufruf ZDF_RubrikSingle
def ZDF_get_navi(DictID, title, homeID=""):
	PLog('ZDF_get_navi: ' + DictID)
	
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
	else:	
		li = home(li, ID='ZDF')				# Home-Button
		
	jsonObject = Dict("load", DictID)
	PLog(str(jsonObject)[:80])
	name = jsonObject["name"]
	jsonObject = jsonObject["teaser"]
	PLog(str(jsonObject)[:80])
	PLog(len(jsonObject))
	for obj in jsonObject:
		url = obj["url"]
		title = obj["titel"]
		summ = obj["beschreibung"]
		
		label = "%s | [B]%s[/B]" % (name, title)
		tag = "Inhalt [B]%s[/B] | Folgeseiten" % title
		title=py2_encode(title)
	
		fparams="&fparams={'url': '%s', 'title': '%s', 'homeID': '%s'}" % (url, quote(title), homeID)
		addDir(li=li, label=label, action="dirList", dirID="ZDF_RubrikSingle", fanart=R(ICON_DIR_FOLDER), 
			thumb=R(ICON_DIR_FOLDER), fparams=fparams, summary=summ, tagline=tag)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
###################################################################################################
# ZDF-Suche:
# 
def ZDF_Search(query=None, title='Search', s_type=None, pagenr=''):
	PLog("ZDF_Search:")
	if 	query == '':	
		query = get_query(channel='ZDF')
	PLog(query)
	if  query == None or query.strip() == '':
		#return ""
		Main_ZDF(name='')			# Absturz nach Sofortstart-Abbruch
	
	query = query.replace(u'–', '-')# verhindert 'ascii'-codec-Error
	query = query.replace(' ', '+')	# Aufruf aus Merkliste unbehandelt	
			
	query_org = query	
	query=py2_decode(query)			# decode, falls erf. (1. Aufruf)

	PLog(query); PLog(pagenr); PLog(s_type)
	ID='Search'
	ZDF_Search_PATH	 = "https://zdf-prod-futura.zdf.de/mediathekV2/search?profile=cellular-5&q=%s&page=%s"
	
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path = ZDF_Search_PATH % (quote(py2_encode(query)), str(pagenr)) 
	PLog(path)
	
	page, msg = get_page(path=path, do_safe=False)	# +-Zeichen für Blank nicht quoten	
	try:
		jsonObject = json.loads(page)
		searchResult = str(jsonObject["totalResultsCount"])
		nextUrl = str(jsonObject["nextPageUrl"])
		nextPage = str(jsonObject["nextPage"])
	except:
		searchResult=""; nextUrl=""; nextPage=""
	PLog("searchResult: "  + searchResult);
	PLog("nextPage: "  + nextPage);
	
	NAME = 'ZDF Mediathek'
	name = 'Suchergebnisse zu: %s (Gesamt: %s), Seite %s'  % (quote(py2_encode(query)), searchResult, pagenr)

	li = xbmcgui.ListItem()

	# Der Loader in ZDF-Suche liefert weitere hrefs, auch wenn weitere Ergebnisse fehlen
	# 22.01.2020 Webänderung 'class="artdirect " >' -> 'class="artdirect"'
	if not searchResult:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen
		msg2 = msg 
		msg1 = 'Keine Ergebnisse (mehr) zu: %s' % query  
		MyDialog(msg1, msg2, '')
		return li	
				
	query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen
		
	DictID="ZDF_Search"											# hier dummy
	li=ZDF_PageMenu(DictID, jsonObject=jsonObject, mark=query, li=li)
	
	li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
	PLog("nextUrl: " + nextUrl)
	if nextPage and nextUrl:
		query = query_org.replace('+', ' ')
		pagenr = re.search(r'&page=(\d+)', nextUrl).group(1)
		PLog(pagenr); 
		title = "Mehr Ergebnisse im ZDF zeigen zu: >%s<"  % query
		tagline = u"nächste Seite [B]%s[/B]" % pagenr
		query_org=py2_encode(query_org); 
		fparams="&fparams={'query': '%s', 's_type': '%s', 'pagenr': '%s'}" %\
			(quote(query_org), s_type, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), tagline=tagline, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
###################################################################################################

# Liste der Wochentage ZDF
# ARD s. ARDnew.SendungenAZ (früherer Classic-Code entfernt)
# 
def ZDF_VerpasstWoche(name, title, homeID=""):									# Wochenliste ZDF Mediathek
	PLog('ZDF_VerpasstWoche:')
	PLog(name); 
	 
	sfilter=''
	fname = os.path.join(DICTSTORE, 'CurSenderZDF')				# init CurSenderZDF (aktueller Sender)
	if os.path.exists(fname):									# kann fehlen (Aufruf Merkliste)
		sfilter = Dict('load', 'CurSenderZDF')
		
	if sfilter == '' or sfilter == False:						# 'Alle ZDF-Sender' nur bei zdf-cdn-api
		sfilter = 'ZDF'											# Default Alle ZDF-Sender (nur VERPASST)
	
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)				# Home-Button extern
	else:
		li = home(li, ID='ZDF')					# Home-Button
		
	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")		# Formate s. man strftime (3)
		zdfDate = rdate.strftime("%Y-%m-%d")		
		iWeekday =  rdate.strftime("%A")
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)
		PLog(iDate); PLog(iWeekday);
		#title = ("%10s ..... %10s"% (iWeekday, iDate))	 # Formatierung in Plex ohne Wirkung		
		title =	"%s | %s" % (iDate, iWeekday)
		
		func = "ZDF_Verpasst"					# Call intern
		fanart=R(ICON_ZDF_VERP); thumb=R(ICON_ZDF_VERP)
		if homeID == "Kinderprogramme":
			func = "resources.lib.childs.tivi_Verpasst"	# Call extern
			fanart=GIT_ZDFTIVI; thumb=GIT_TIVICAL
			sfilter='Alle ZDF-Sender'

		PLog("Satz1: ")
		PLog(title); PLog(zdfDate)
		fanart=R(ICON_ZDF_VERP); thumb=R(ICON_ZDF_VERP)
		title=py2_encode(title); zdfDate=py2_encode(zdfDate);
		fparams="&fparams={'title': '%s', 'zdfDate': '%s', 'sfilter': '%s'}" %\
			(quote(title), quote(zdfDate), sfilter)
		addDir(li=li, label=title, action="dirList", dirID=func, fanart=fanart, 
			thumb=thumb, fparams=fparams)
	
	if homeID == "":									# Folgebuttons nicht für ext. Nutzung
		label = "Datum eingeben"						# Button für Datumeingabe anhängen
		tag = u"teilweise sind bis zu 4 Jahre alte Beiträge abrufbar"
		fparams="&fparams={'title': '%s', 'zdfDate': '%s', 'sfilter': '%s'}" % (quote(title), quote(zdfDate), sfilter)
		addDir(li=li, label=label, action="dirList", dirID="ZDF_Verpasst_Datum", fanart=R(ICON_ZDF_VERP), 
			thumb=GIT_CAL, fparams=fparams, tagline=tag)

														# Button für Stationsfilter
		label = u"Wählen Sie Ihren ZDF-Sender - aktuell: [B]%s[/B]" % sfilter
		tag = "Auswahl: Alle ZDF-Sender, ZDF, ZDFneo oder ZDFinfo" 
		fparams="&fparams={'name': '%s', 'title': 'ZDF-Mediathek', 'sfilter': '%s'}" % (quote(name), sfilter)
		addDir(li=li, label=label, action="dirList", dirID="ZDF_Verpasst_Filter", fanart=R(ICON_ZDF_VERP), 
			thumb=R(ICON_FILTER), tagline=tag, fparams=fparams)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# True, sonst Rückspr. nach ZDF_Verpasst_Filter
	
#-------------------------
#  03.06.2021 ARD_Verpasst_Filter (Classic) entfernt							
#-------------------------
# Auswahl der ZDF-Sender für ZDF_VerpasstWoche
# bei Abbruch bleibt sfilter unverändert
								
def ZDF_Verpasst_Filter(name, title, sfilter):
	PLog('ZDF_Verpasst_Filter:'); PLog(sfilter); 
	
	stations = ['Alle ZDF-Sender', 'ZDF', 'ZDFneo', 'ZDFinfo']
	if sfilter not in stations:		# Fallback für Version < 4.7.0
		i=0
	else:
		i = stations.index(sfilter)

	dialog = xbmcgui.Dialog()
	d = dialog.select('ZDF-Sendestation wählen', stations, preselect=i)
	if d == -1:						# Fallback Alle
		d = 0
	sfilter = stations[d]
	PLog("Auswahl: %d | %s" % (d, sfilter))
	Dict('store', "CurSenderZDF", sfilter)
	
	return ZDF_VerpasstWoche(name, title)

#-------------------------
# Aufruf ZDF_VerpasstWoche (Button "Datum eingeben")
# xbmcgui.INPUT_DATE gibt akt. Datum vor
# 11.01.2020: Ausgabe noch für 1.1.2016, nicht mehr für 1.1.2015
# sfilter wieder zurück an ZDF_VerpasstWoche
#
def ZDF_Verpasst_Datum(title, zdfDate, sfilter):
	PLog('ZDF_Verpasst_Datum:')
	
	dialog = xbmcgui.Dialog()
	inp = dialog.input("Eingabeformat: Tag/Monat/Jahr (4-stellig)", type=xbmcgui.INPUT_DATE)
	PLog(inp)
	if inp == '':
		return						# Listitem-Error, aber Verbleib im Listing
	d,m,y = inp.split('/')
	d=d.strip(); m=m.strip(); y=y.strip();
	if len(d) == 1: d="0%s" % d	
	if len(m) == 1: m="0%s" % m	
	if len(y) != 4:
		msg1 = 'Jahr bitte 4-stellig eingeben'
		MyDialog(msg1, '', '')
		return
	
	zdfDate = "%s-%s-%s" % (y,m,d)	# "%Y-%m-%d"
	PLog(zdfDate)
	
	# zurück zu ZDF_VerpasstWoche:
	ZDF_Verpasst(title='Datum manuell eingegeben', zdfDate=zdfDate, sfilter=sfilter)
	return
	
#-------------------------
# Aufruf: ZDF_VerpasstWoche, 2 Durchläufe
# 1. Buttons Morgens. Mittags, Abends, Nachts
# 2. Cluster-Ermittl. via DictID, Teaser-Auswertung 
# 04.03.2024 ZDFtivi integriert
# 
def ZDF_Verpasst(title, zdfDate, sfilter='Alle ZDF-Sender', DictID=""):
	PLog('ZDF_Verpasst:'); PLog(title); PLog(zdfDate); PLog(sfilter);
	PLog("DictID: " + DictID);
	title_org = title

	mediatype=''													# Kennz. Videos im Listing
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	PLog('mediatype: ' + mediatype); 

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	li2 = xbmcgui.ListItem()										# mediatype='video': eigene Kontextmenüs in addDir							

	# -----------------------------------------						# 2. Durchlauf
	
	if DictID:	
		jsonObject = Dict("load", DictID)
		teaserObject = jsonObject["teaser"]
		PLog(len(teaserObject))
		PLog(str(teaserObject)[:80])
		for entry in teaserObject:
			try:
				typ,title,tag,descr,img,url,stream,scms_id = ZDF_get_content(entry)
				airtime = entry["airtime"]
				t = airtime[-5:]
				title = "[COLOR blue]%s[/COLOR] | %s" % (t, title)	# Sendezeit | Titel
				channel = entry["channel"]
				if sfilter.startswith("Alle") == False:
					PLog("Mark0"); PLog(sfilter); PLog(channel)
					if up_low(sfilter) != up_low(channel):							# filtern
						continue
				tag = "%s | Sender: [B]%s[/B]" % (tag,channel) 
				if SETTINGS.getSetting('pref_usefilter') == 'true':	# Ausschluss-Filter
					filtered=False
					for item in AKT_FILTER: 
						if up_low(item) in py2_encode(up_low(str(entry))):
							filtered = True
							break		
					if filtered:
						PLog('filtered_4: <%s> in %s ' % (item, title))
						continue								
					
				PLog("Satz4:")
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
		return
	
	# -----------------------------------------							# 1. Durchlauf
	
	path = "https://zdf-prod-futura.zdf.de/mediathekV2/broadcast-missed/" + zdfDate
	page, msg = get_page(path)
	if page == '':
		msg1 = "Abruf fehlgeschlagen | %s" % title
		MyDialog(msg1, msg, '')
		return li 

	jsonObject = json.loads(page)
	clusterObject = jsonObject["broadcastCluster"]
	PLog(str(clusterObject)[:80])
	PLog("Cluster: %d " % len(clusterObject))

	msg1 = title								# Notification Datum + Sender
	if "manuell" in title:
		msg1 = "%s.%s.%s" % (zdfDate[8:10], zdfDate[5:7], zdfDate[0:4])
	msg2 = sfilter
	icon = R(ICON_ZDF_VERP)
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)
	cnt=0
			
	for jsonObject in clusterObject:
		title = jsonObject["name"]
		img = ZDF_get_img(jsonObject["teaser"][0])
		tag = "Folgeseiten"
		DictID = "ZDF_Verpasst_%d" % cnt	 				# DictID: cluster-nr
		Dict('store', DictID, jsonObject)					# -> ZDF_Verpasst
	
		fparams="&fparams={'title': '%s', 'zdfDate': '%s', 'sfilter': '%s', 'DictID': '%s'}" %\
			(title_org, zdfDate, sfilter, DictID)
		PLog("fparams: " + fparams)	
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Verpasst", fanart=img, 
		thumb=img, fparams=fparams, tagline=tag)
		cnt=cnt+1
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# ZDF-eigener Zugang via ZDF_Rubriken
# hier: Buchstaben-Icons vorgeschaltet ->  ZDF_AZList
#	einschl. Cache-Nutzung (AZ > 12 MByte)
#	ID=ZDFfunk <- Main_ZDFfunk
#
def ZDF_AZ(name, ID=""):						# name = "Sendungen A-Z"
	PLog('ZDF_AZ: ' + name);
	PLog(ID) 
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	azlist = list(string.ascii_uppercase)
	azlist.append('0 - 9')

	# Menü A to Z
	for element in azlist:
		title='Sendungen mit ' + element
		fparams="&fparams={'title': '%s', 'element': '%s', 'ID': '%s'}" % (title, element, ID)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_AZList", fanart=R(ICON_ZDF_AZ), 
			thumb=R(ICON_ZDF_AZ), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
# Laden der Buchstaben-Seite, Auflistung der Sendereihen in 
#	ZDF_RubrikSingle
# Buchstaben-Seiten enthalten nur Sendereihen, keine Einzelbeiträge
# 19.11.2020 Integration funk A-Z (ID=ZDFfunk)
#
def ZDF_AZList(title, element, ID=""):					# ZDF-Sendereihen zum gewählten Buchstaben
	PLog('ZDF_AZList: ' + element)
	PLog(title); PLog(ID);
	title_org = title
	
	DictID = "ZDF_sendungen-100"
	path = "https://zdf-prod-futura.zdf.de/mediathekV2/document/sendungen-100"
	msg1 = "Cache ZDF A-Z:"
	if "funk" in ID:
		DictID = "funk-alle-sendungen-von-a-z-100"
		path = "https://zdf-prod-futura.zdf.de/mediathekV2/document/%s" % DictID
		if element == "0 - 9":							# für funk o. Blanks
			element="0-9"
		msg1 = "Cache funk A-Z:"
	jsonObject = Dict("load", DictID, CacheTime=ZDF_CacheTime_AZ)
	if not jsonObject:
		icon = R(ICON_ZDF_AZ)
		xbmcgui.Dialog().notification(msg1,"Haltedauer 30 Min",icon,3000,sound=False)
		page, msg = get_page(path)
		if not page:												# nicht vorhanden?
			msg1 = 'ZDF_AZList: Beiträge können leider nicht geladen werden.' 
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return
		jsonObject = json.loads(page)
		Dict("store", DictID, jsonObject)
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	PLog(str(jsonObject)[:80])
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
			typ,title,tag,descr,img,url,stream,scms_id = ZDF_get_content(entry)
			title = repl_json_chars(title)
			label = title
			descr = repl_json_chars(descr)
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (url, title)
			PLog("fparams: " + fparams)	
			addDir(li=li, label=label, action="dirList", dirID="ZDF_RubrikSingle", fanart=img, 
				thumb=img, fparams=fparams, summary=descr, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------
# MEHR_Suche ZDF nach query (title)
# Aufrufer: ZDF_RubrikSingle
def ZDF_search_button(li, query):
	PLog('ZDF_search_button:')

	query = (query.replace('|', '').replace('>', '')) # Trenner + Staffelkennz. entfernen
	query_org = query

	query = query.replace(u"Das ZDF ist für den verlinkten Inhalt nicht verantwortlich!", '')
	label = u"Alle Beiträge im ZDF zu >%s< suchen"  % query_org
	query = query.replace(' ', '+')	
	tagline = u"zusätzliche Suche starten"
	summ 	= u"mehr Ergebnisse im ZDF suchen zu >%s<" % query_org
	s_type	= 'MEHR_Suche'						# Suche alle Beiträge (auch Minutenbeiträge)
	query=py2_encode(query); 
	fparams="&fparams={'query': '%s', 's_type': '%s'}" % (quote(query), s_type)
	addDir(li=li, label=label, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams, tagline=tagline, summary=summ)
	return
  
#----------------------------------------------
# Ähnlich ARD_FlatListEpisodes (dort entfällt die
#	Liste aller Serien)
# Aufruf ZDF_RubrikSingle (Abzweig), Button flache Serienliste,
#	zusätzl. Button für ZDF_getStrmList + strm-Tools
#	sid=Serien-ID (Url-Ende)
#	Ablauf: Liste holen via api-Call, Abgleich mit sid,
#		Serieninhalt holen via api-Call
# 	Cache: von der Gesamt-Liste (> 3 MB) werden im Dict nur
#		sid und url gespeichert
# 01.05.2023 Folge direkt holen mit sid statt serien-100
#
def ZDF_FlatListEpisodes(sid):
	PLog('ZDF_FlatListEpisodes: ' + sid)
	CacheTime = 43200											# 12 Std.
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button			
	li2 = xbmcgui.ListItem()									# mediatype='video': eigene Kontextmenüs in addDir							
	
	#															# headers wg. häufiger timeouts
	path = "https://zdf-prod-futura.zdf.de/mediathekV2/document/%s" % sid 
	page, msg = get_page(path=path, header=HEADERS)
	if page == "":	
		msg1 = "Abbruch  in ZDF_FlatListEpisodes:"
		msg2 = "Die Serien-ID [B]%s[/B] ist nicht (mehr)" % sid
		msg3 = " in der Serienübersicht des ZDF enthalten."
		MyDialog(msg1, msg2, msg3)	
		return
		
	jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
		
	#-----------------------------								# strm-Buttons

	mediatype=''												# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
		
	#															# Button strm-Dateien gesamte Liste
	if SETTINGS.getSetting('pref_strm') == 'true':
		img = R(ICON_DIR_STRM)
		title = u"strm-Dateien für die komplette Liste erzeugen / aktualisieren"
		tag = u"Verwenden Sie das Kontextmenü, um strm-Dateien für [B]einzelne Videos[/B] zu erzeugen"
		summ = u"[B]strm-Dateien (strm-Bündel)[/B] sparen Platz und lassen sich auch in die Kodi-Bibliothek integrieren."
		summ = u"%s\n\nEin strm-Bündel in diesem Addon besteht aus der strm-Datei mit der Streamurl, einer jpeg-Datei" % summ
		summ = u"%s\nmit dem Bild zum Video und einer nfo-Datei mit dem Begleittext." % summ
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s'}" %\
			(quote(path), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="ZDF_getStrmList", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)
			
		title = u"strm-Tools"									# Button für strm-Tools
		tag = "Abgleichintervall in Stunden\nListen anzeigen\nListeneinträge löschen\n"
		tag = "%sMonitorreset\nstrm-Log anzeigen\nAbgleich einer Liste erzwingen\n" % tag
		tag = "%sunterstützte Sender/Beiträge\nzu einem strm-Verzeichnis wechseln" % tag
		myfunc="resources.lib.strm.strm_tools"
		fparams_add = quote('{}')

		fparams="&fparams={'myfunc': '%s', 'fparams_add': '%s'}"  %\
			(quote(myfunc), quote(fparams_add))			
		addDir(li=li, label=title, action="dirList", dirID="start_script",\
			fanart=R(FANART), thumb=R("icon-strmtools.png"), tagline=tag, fparams=fparams)	
		
	
	#-----------------------------								# Auswertung Serie

	# Blockmerkmal für Folgen unterschiedlich:					# Blockmerkmale wie ZDF_getStrmList	
	season_title = jsonObject["document"]["titel"]
	season_id 	= jsonObject["document"]["id"]
	staffel_list = jsonObject["cluster"]
	PLog("season_title: %s" % season_title)
	PLog("staffel_list: %d" % len(staffel_list))

	for staffel in 	staffel_list:
		if 	staffel["name"] == "":								# Teaser u.ä.
			continue							
		folgen = staffel["teaser"]								# Folgen-Blöcke	
		PLog("Folgen: %d" % len(folgen))
		for folge in folgen:
			# Abgleich headline/season_title entfällt wg. möglicher Abweichungen
			#	Bsp.: FETT UND FETT/FETT & FETT, daher Abgleich mit brandId
			scms_id = folge["id"]
			try:
				brandId = folge["brandId"]
			except:
				brandId=""
			if season_id != brandId:
				PLog("skip_no_brandId: " + str(folge)[:60])
				continue
			title, url, img, tag, summ, season, weburl = ZDF_FlatListRec(folge)
			if season == '':
				PLog("skip_no_season: " + str(folge)[:60])
				continue
			if SETTINGS.getSetting('pref_usefilter') == 'true':	# Ausschluss-Filter
				filtered=False
				for item in AKT_FILTER:
					if up_low(item) in py2_encode(up_low(str(folge))):
						filtered = True
						break		
				if filtered:
					PLog('filtered_5: <%s> in %s ' % (item, title))
					continue								
				
			summ_par= summ.replace('\n', '||')
			tag_par= tag.replace('\n', '||')
			PLog("Satz29:")
			PLog(url);PLog(img);PLog(title);PLog(tag);PLog(summ[:80]); 
			url=py2_encode(url); title=py2_encode(title); img=py2_encode(img); 
			tag_par=py2_encode(tag_par);summ_par=py2_encode(summ_par);
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'tag': '%s', 'summ': '%s', 'scms_id': '%s'}" %\
				(quote(url), quote(title), quote(img), quote(tag_par), quote(summ_par), scms_id)
			addDir(li=li2, label=title, action="dirList", dirID="ZDF_getApiStreams", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------
# Ermittlung Streamquellen für api-call, ähnlich build_Streamlists 
#	aber abweichendes Quellformat
# Aufrufer: ZDF_FlatListEpisodes, ab V4.7.0 auch ZDF_PageMenu,
#	ZDF_Rubriken, ZDF_RubrikSingle, ZDF_Verpasst.
# Mitnutzung get_form_streams sowie build_Streamlists_buttons
# gui=False: ohne Gui, z.B. für ZDF_getStrmList
# 16.05.2024 Auswertung Bitraten entfernt (unsicher)
# 21.07.2024 zdf-cdn-api bei vielen Url's nicht mehr akzeptiert,
#	Alternative profile_url mit api.zdf.de + scms_id hinzugefügt.
# 25.07.2024 Austausch zdf-cdn.live.cellular.de -> zdf-prod-futura.zdf.de
#	Alternative profile_url ev. entbehrlich, aber vorerst belassen.
#
def ZDF_getApiStreams(path, title, thumb, tag,  summ, scms_id="", gui=True):
	PLog("ZDF_getApiStreams: " + scms_id)

	cdn_api=True
	header=""
	if "ngplayer" in path:
		header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % zdfToken
		cdn_api=False
	page, msg = get_page(path, header=header)
	if page == '':	
		msg1 = "Fehler in ZDF_getStreamSources:"
		msg2 = msg
		if "Error 503" in msg:								# cdn-api nicht akzeptiert? -> api.zdf.de
			try:
				profile_url="https://api.zdf.de/content/documents/%s.json?profile=player" % scms_id
				PLog("profile_url: " + profile_url)
				header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % zdfToken
				page, msg = get_page(path=profile_url, header=header, JsonPage=True)
				pos = page.rfind('mainVideoContent')					# 'mainVideoContent' am Ende suchen
				page_part = page[pos:]
				PLog("page_part: " + page_part[:40])
				ptmd_player = 'ngplayer_2_4'							# ab 22.12.2020
				videodat_url = stringextract('ptmd-template":"', '"', page_part)
				videodat_url = videodat_url.replace('{playerId}', ptmd_player) 	# ptmd_player injiziert 
				videodat_url = 'https://api.zdf.de' + videodat_url	
				videodat_url = videodat_url.replace('\\/','/')	
				PLog('videodat_url: ' + videodat_url)	
				page, msg	= get_page(path=videodat_url, header=header, JsonPage=True)
				PLog("videodat_page: " + page[:80])					
				cdn_api=False
			except Exception as exception:
				PLog("profile_url_error: " + str(exception))
				page=""
		if page == "":	
			MyDialog(msg1, msg2, '')
			return
	page = page.replace('\\/','/')
	page=page.replace('" :', '":'); page=page.replace('": "', '":"')  # Formatanpassung für get_form_streams

	li = xbmcgui.ListItem()
	if gui:
		li = home(li, ID='ZDF')								# Home-Button	
	
	availInfo = stringextract('"availabilityInfo":"',  '"', page) # FSK-Info? -> s.u. Dialog
	availInfo = transl_json(availInfo)
	channel = stringextract('"channel":"',  '"', page)
	
	HLS_List=[]; MP4_List=[]; HBBTV_List=[];				# MP4_List = download_list
	# erlaubte Formate wie build_Streamlists:
	only_list = ["h264_aac_mp4_http_na_na", "h264_aac_ts_http_m3u8_http",	
				"vp9_opus_webm_http_na_na", "vp8_vorbis_webm_http_na_na"
				]	
		
	# Format formitaeten von Webversion abweichend, build_Streamlists
	#	nicht verwendbar
	PLog("cdn_api: " + str(cdn_api))
	formitaeten, duration, geoblock, sub_path = get_form_streams(page)
	forms=[]
	if len(formitaeten) > 0:								# Videoquellen fehlen?
		PLog("formitaeten_0: " + str(formitaeten[0])[:100])
		if cdn_api:
			formsblock = stringextract('formitaeten":', ']', formitaeten[0])
			forms = blockextract('"type":', formsblock)
		else:
			forms = blockextract('"type":', str(formitaeten))
			
	PLog("forms: %d" % len(forms))
	
#	Plot  = "%s||||%s" % (tag, summ)
	line=''; skip_list=[]
	for form in forms:
		#PLog("form: " + form)
		track_add=''; class_add=''; lang_add=''				# class-und Sprach-Zusätze
		typ = stringextract('"type":"', '"', form)
		class_add = stringextract('"class":"',  '"', form)	
		lang_add = stringextract('"language":"',  '"', form)
		if class_add == "main": class_add = "TV-Ton"
		if class_add == "ot": class_add = "Originalton"
		if class_add == "ad": class_add = "Audiodeskription"
		if class_add or lang_add:
			track_add = "[B]%s %s[/B]" % (class_add, lang_add)
			track_add = "%23s" % track_add 				# formatiert
					
		url = stringextract('"url":"',  '"', form)		# Stream-URL
		if url == "":
			url = stringextract('"uri":"',  '"', form)	# api.zdf.de
		PLog("url: " + url); PLog("typ: " + typ);
		server = stringextract('//',  '/', url)			# 2 Server pro Bitrate möglich
		if typ not in only_list or url in skip_list or url == "":
			continue
		
		skip_list.append(url)
			
		quality = stringextract('"quality":"',  '"', form)
		mimeType = stringextract('mimeType":"', '"', form)
		PLog("quality: " + quality); PLog("mimeType: " + mimeType);
		
		# bei HLS entfällt Parseplaylist - verschiedene HLS-Streams verfügbar 
		if url.find('master.m3u8') > 0:					# HLS-Stream 
			HLS_List.append('HLS, %s ** AUTO ** %s ** %s#%s' % (track_add, quality,title,url))
		else:
			res='0x0'; w=''; h=''						# Default					
			if 'hd":true' in form:	
				w = "1920"; h = "1080"					# Probeentnahme													
			if 'veryhigh' in quality:
				w = "1280"; h = "720"					# Probeentnahme							
			if 'high' in quality:
				w = "960"; h = "540"					# Probeentnahme							
			if 'med' in quality:
				w = "640"; h = "360"					# Probeentnahme							
			if 'low' in quality:
				w = "480"; h = "270"					# Probeentnahme							
			
			res = "%sx%s" % (w,h)
			title_url = u"%s#%s" % (title, url)
			item = u"MP4, %s | %s ** Auflösung %s ** %s" %\
				(track_add, quality, res, title_url)
			PLog("title_url: " + title_url); PLog("item: " + item)
			PLog("server: " + server)					# nur hier, kein Platz im Titel			
			MP4_List.append(item)
			
			
	ID="ZDF"; HOME_ID = ID
	title_org = title
	
	PLog("HLS_List: " + str(len(HLS_List)))
	#PLog(HLS_List)
	PLog("MP4_List: " + str(len(MP4_List)))
	
	UHD_DL_list=[]
	if scms_id:
		HBBTV_List = ZDFSourcesHBBTV(title, scms_id)	# bisher nur MP4-Quellen				
		HBBTV_List, UHD_DL_list = add_UHD_Streams(HBBTV_List) # UHD-Streams -> Download_Liste
		Dict("store", '%s_HBBTV_List' % ID, HBBTV_List) 
	PLog("HBBTV_List: " + str(len(HBBTV_List)))
	PLog("UHD_DL_list: " + str(len(UHD_DL_list)))
		
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	if len(UHD_DL_list) > 0:							# UHD_Liste in Downloads voranstellen
		MP4_List = UHD_DL_list + MP4_List
	Dict("store", '%s_MP4_List' % ID, MP4_List) 
		
	if not len(HLS_List) and not len(MP4_List) and not len(HBBTV_List):			
		if gui:										# ohne Gui
			msg = 'keine Streamquellen gefunden - Abbruch' 
			PLog(msg); PLog(availInfo)
			msg1 = u"keine Streamquellen gefunden: >%s<"	% title
			msg2=""
			if availInfo:
				msg2 = availInfo
			MyDialog(msg1, msg2, '')

		return HLS_List, MP4_List, HBBTV_List
	
	Plot  = "%s||||%s" % (tag, summ)
	build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)

	if gui:											# ohne Gui
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:
		return

#----------------------------------------------
# erzeugt / aktualsiert strm-Dateien für die komplette Liste 
# Ermittlung Streamquellen für api-call
# Ablauf: Seite path laden, Blöcke wie ZDF_FlatListEpisodes
#	iterieren -> ZDF_FlatListRec -> ZDF_getApiStreams (Streamquelle 
#	ermitteln -> 
# Nutzung strm-Modul: get_strm_path, xbmcvfs_store
# Cache-Verzicht, um neue Folgen nicht zu verpassen.
#
def ZDF_getStrmList(path, title, ID="ZDF"):
	PLog("ZDF_getStrmList:")
	title_org = title
	list_path = path
	icon = R(ICON_DIR_STRM)
	FLAG_OnlyUrl = os.path.join(ADDON_DATA, "onlyurl")
	import resources.lib.strm as strm
	
	page, msg = get_page(path=path)
	if page == '':
		msg1 = "Fehler in ZDF_getStrmList:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
		
	if page.find('"seasonNumber"') < 0:
		msg1 = "[B]seasonNumber[/B] fehlt in den Beiträgen."
		msg2 = "strm-Liste für diese Serie kann nicht erstellt werden."
		MyDialog(msg1, msg2, '')
		return
		
	jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
				
	list_title = jsonObject["document"]["titel"]
	list_title = transl_json(list_title)
	PLog("list_title:" + list_title)
	
	strm_type = strm.get_strm_genre()					# Genre-Auswahl
	if strm_type == '':
		return
	strmpath = strm.get_strm_path(strm_type)			# Abfrage Zielverz. != Filme
	if os.path.isdir(strmpath) == False:
		msg1 = "Zielverzeichnis existiert nicht."
		msg2 = u"Bitte Settings überprüfen."
		MyDialog(msg1, msg2, '')
		return
	
	fname = make_filenames(list_title)					# Abfrage Unterverzeichnis Serie
	strmpath = os.path.join(strmpath, fname)
	PLog("list_strmpath: " + strmpath)		
	head = u"Unterverzeichnis für die Serie"
	msg1 = u"Das Addon legt für die Serie folgendes Unterverzeichnis an:"
	if os.path.isdir(strmpath):		
		msg1 = u"Das Addon verwendet für die Serie folgendes Unterverzeichnis:"
	msg2 = u"[B]%s[/B]" % fname
	msg3 = u"Ein vorhandenes Verzeichnis wird überschrieben."
	ret = MyDialog(msg1, msg2, msg3, ok=False, cancel='Abbruch', yes='OK', heading=head)
	if ret != 1:
		return
	if os.path.exists(strmpath) == False:
		try:
			os.mkdir(strmpath)											# Verz. erzeugen, falls noch nicht vorh.
			list_exist=False
		except Exception as exception:
			PLog(str(exception))
			msg1 = u'strm-Verzeichnis konnte nicht angelegt werden:'
			msg2 = str(exception)
			MyDialog(msg1, msg2, '')
			return	
	else:
		list_exist=True

	#---------------------
	# Blockmerkmale s. ZDF_FlatListEpisodes:						# Blockmerkmale wie ZDF_FlatListEpisodes
	staffel_list = jsonObject["cluster"]							# Staffel-Blöcke
	if len(staffel_list) == 0:										# ohne Staffel-Blöcke
		staffel_list = blockextract('"headline":"', page)
	season_title = jsonObject["document"]["titel"]
	season_id 	= jsonObject["document"]["id"]
	PLog("season_title: %s" % season_title)
	PLog("staffel_list: %d" % len(staffel_list))
	
	cnt=0; skip_cnt=0; do_break=False
	for staffel in 	staffel_list:
		folgen = staffel["teaser"]								# Folgen-Blöcke	
		PLog("Folgen: %d" % len(folgen))
		for folge in folgen:
			scms_id = folge["id"]								# wie ZDF_FlatListEpisodes
			try:
				brandId = folge["brandId"]
			except:
				brandId=""
			if season_id != brandId:
				PLog("skip_no_brandId: " + str(folge)[:60])
				continue
			title, url, img, tag, summ, season, weburl = ZDF_FlatListRec(folge) # Datensatz
			if season == '':
				PLog("skip_no_season: " + str(folge)[:60])
				continue
			
			fname = make_filenames(title)							# Zieldatei hier ohne Dialog
			PLog("fname: " + fname)
			if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
				f = os.path.join(strmpath, fname, "%s.nfo" % fname)
			else:
				f = os.path.join(strmpath, "%s.nfo" % fname)
			PLog("f: " + f)
			if os.path.isfile(f):									# skip vorh. strm-Bundle
				msg1 = u'schon vorhanden:'
				msg2 = title
				xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
				PLog("skip_bundle: " + f)
				skip_cnt=skip_cnt+1
				continue
			else:
				msg1 = u'neues strm-Bündel:'
				msg2 = title
				xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
				
			PLog("Satz30:")
			PLog(url);PLog(img);PLog(title);PLog(tag);PLog(summ[:80]); 
			
			msg1 = u'Suche Streamquellen'
			msg2 = title
			xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
			open(FLAG_OnlyUrl, 'w').close()							# Flag PlayVideo_Direct: kein Videostart
			ZDF_getApiStreams(url, title, img, tag,  summ, gui=False) # Streamlisten bauen, Ablage Url
			url = RLoad(STRM_URL, abs_path=True)					# abgelegt von PlayVideo_Direct
			PLog("strm_Url: " + str(url))
			
			Plot = "%s\n\n%s" % (tag, summ)
			ret = strm.xbmcvfs_store(strmpath, url, img, fname, title, Plot, weburl, strm_type)
			if ret:
				cnt=cnt+1

	#------------------
	PLog("strm_cnt: %d" % cnt)		
	msg1 = u'%d neue STRM-Datei(en)' % cnt
	if cnt == 0:
		msg1 = u'STRM-Liste fehlgeschlagen'
		if list_exist == True:
			msg1 = u'STRM-Liste unverändert'
	msg2 = list_title
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		
	#------------------												# Liste synchronisieren?
	# Format: Listen-Titel ## lokale strm-Ablage ##  ext.Url ## strm_type
	item = "%s##%s##%s##%s"	% (list_title, strmpath, list_path, strm_type)
	PLog("item: " + item)
	synclist = strm.strm_synclist(mode="load")						# "strm_synclist"
	if exist_in_list(item, synclist) == True:	
		msg1 = "Synchronsisation läuft"
		msg2 = list_title
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		PLog(msg1)
	else:
		sync_hour = strm.strm_tool_set(mode="load")	# Setting laden
		head = u"Liste synchronisieren"
		msg1 = u"Soll das Addon diese Liste regelmäßig abgleichen?"
		msg2 = u"Intervall: %s Stunden" % sync_hour	
		ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Nein', yes='OK', heading=head)
		if ret == 1:											# Liste neu aufnehmen
			strm.strm_synclist(mode="save", item=item)
			line = "%6s | %15s | %s..." % ("NEU", list_title[:15], "Liste neu aufgenommen")
			strm.log_update(line)

	return

#----------------------------------------------
# holt Details für item
# Aufrufer: ZDF_FlatListEpisodes, ZDF_getStrmList
def ZDF_FlatListRec(item):
	PLog('ZDF_FlatListRec:')
	PLog(str(item)[:80])

	title='';url='';img='';tag='';summ='';season='';
	descr='';weburl=''
	
	if "seasonNumber" in item:
		season =  item["seasonNumber"]						# string
	if season == '':										# Satz verwerfen	
		return title, url, img, tag, summ, season, weburl
		
	episode =  item["episodeNumber"]						# string
	PLog(season); PLog(episode)
	title_pre = "S%02dE%02d" % (int(season), int(episode))	# 31.01.2022 S13_F10 -> S13E10
	
	brand =  item["headline"]
	title =	 item["titel"]
	title =  repl_json_chars(title)			
	descr =  item["beschreibung"]
	weburl =  item["sharingUrl"] 							# für Abgleich vor./nicht mehr vorh. 
	fsk =  item["fsk"]
	if fsk == "none":
		fsk = "ohne"
	end =  item["timetolive"]								# Altern.: offlineAvailability
	end = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % end
	geo =  item["geoLocation"]
	if geo == "none":
		geo = "ohne"
	dauer = item["length"]
	dauer = seconds_translate(dauer)
	title = "%s | %s" % (title_pre, title)
	
	img = ZDF_get_img(item)
	url =  item["cockpitPrimaryTarget"]["url"]				# Ziel-Url mit Streamquellen
	
	tag = u"%s | Staffel: %s | Folge: %s\nDauer: %s | FSK: %s | Geo: %s | %s" %\
		(brand, season, episode, dauer, fsk, geo, end)
	
	title = repl_json_chars(title); title = unescape(title); 
	summ = repl_json_chars(descr)

	return title, url, img, tag, summ, season, weburl

#-------------------------
# wertet die (teilw. unterschiedlichen) Parameter von
#	class="bottom-teaser-box"> aus.
# Aufrufer: ZDF_Rubriken, get_teaserElement (loader-
#	Beiträge), 
#
def ZDF_get_teaserbox(page):
	PLog('ZDF_get_teaserbox:')
	teaser_label='';teaser_typ='';teaser_nr='';teaser_brand='';teaser_count='';multi=False
	
	if 'class="bottom-teaser-box">' in page:
		if 'class="teaser-cat-category">' in page:
			if 'cat-category-ellipsis">' in page:
				# teaser_brand =  stringextract('cat-category-ellipsis">', '</', page)	   
				teaser_brand =  stringextract('cat-category-ellipsis">', '<a href=', page)	 
			else:		
				teaser_typ = stringextract('class="teaser-cat-category">', '</', page)   # teaser_brand s.u.
			
		else:
			teaser_label = stringextract('class="teaser-label"', '</div>', page) 
			teaser_typ =  stringextract('<strong>', '</strong>', teaser_label)
				
		PLog('teaser_typ: ' + teaser_typ)
		teaser_label = cleanhtml(teaser_label.strip())					# wird ev. -> title	
		teaser_label = unescape(teaser_label);
		teaser_typ = mystrip(teaser_typ.strip())
		
		if u"teaser-episode-number" in page:
			teaser_nr = stringextract('teaser-episode-number">', '</', page)
		if teaser_typ == u'Beiträge':		# Mehrfachergebnisse ohne Datum + Uhrzeit
			multi = True
			
		# teaser_brand bei Staffeln (vor Titel s.u.)
		if teaser_brand == '':
			# teaser_brand = stringextract('cat-brand-ellipsis">', '</', page)  
			teaser_brand =  stringextract('cat-brand-ellipsis">', '<a href=', page)	 # Bsp. Wilsberg, St. 07 -
		
		teaser_brand = cleanhtml(teaser_brand);
		teaser_brand = mystrip(teaser_brand)
		teaser_brand = (teaser_brand.replace(" - ", "").replace(" , ", ", "))
	
	if teaser_nr == '' and teaser_count == '':							# mögl. Serienkennz. bei loader-Beiträgen,
		ts = stringextract('502_play icon ">', '</div>', page)			# Bsp. der STA
		ts=mystrip(ts); ts=cleanhtml(ts)
		if teaser_typ == '':
			teaser_typ=ts
			
	# Bsp. teaser_label class="teaser-label">4 Teile</div> oder 
	#	class="teaser-label"><div class="ellipsis">3 Teile</div></div>
	if teaser_label == '' and teaser_typ == '':							# z.B. >3 Teile< bei Doku-Titel
		teaser_label = stringextract('class="teaser-label"', '</div>', page)
		try: 
			teaser_typ = re.search(r'>(\d+) Teile', teaser_label).group(0)
		except:
			teaser_typ=''
	teaser_label = mystrip(teaser_label) 
	teaser_label = teaser_label.replace('<div class="ellipsis">', ' ')
	teaser_label = (teaser_label.replace('<strong>', '').replace('</strong>', ''))
	PLog(teaser_label); PLog(teaser_typ);

	PLog('teaser_label: %s,teaser_typ: %s, teaser_nr: %s, teaser_brand: %s, teaser_count: %s, multi: %s' %\
		(teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count, multi))
		
	return teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count,multi
	
#-------------------------
# ermittelt html-Pfad in json-Listen für ZDF_Rubriken
#	 z.Z. nicht benötigt s.o. (ZDF_BASE+NodePath+sophId)
def ZDF_get_rubrikpath(page, sophId):
	PLog('ZDF_get_rubrikpath: ' + sophId)
	path=''
	if sophId == '':	# Sicherung
		return path
	content =  blockextract('"@type":"ListItem"', page) # Beiträge des Clusters
	PLog(len(content))
	for rec in content:
		path =  stringextract('"url":"', '"', rec)
		if sophId in path:
			PLog("path: " + path)
			return path	
	return	'' 
	
#-----------------------------------------------------------------------
# vergleicht Titel + Länge eines Beitrags mit den Listen full_shows_ZDF,
#	full_shows_ARD
# title_samml: Titel|Subtitel oder (Long-|Medium-|Short-Titel)
# duration: Minuten-Wert (ARD-sec umrechnen)
# fname: Dateinamen der Liste (full_shows_ZDF, full_shows_ARD)
# Rückgabe: fett-markierter Titel bei entspr. Beitrag, sonst unbeh.
#	Titel
# Aufrufer: ZDF_get_content, get_json_content (ARDnew)
#
def full_shows(title, title_samml, summary, duration,  fname):
	PLog('full_shows:')
	PLog(title_samml); PLog(summary[:60]); PLog(duration); PLog(fname);
	
	if duration == '':									# Sicherung gg. int()-error
		return title
	
	ret = "nofill"										# Return-Flag
	if SETTINGS.getSetting('pref_mark_full_shows') == 'true':
		path = SETTINGS.getSetting('pref_fullshows_path')
		if path == '':
			path = '%s/resources/%s' % (ADDON_PATH, fname)
		else:
			path = "%s/%s" % (SETTINGS.getSetting('pref_mark_full_shows'), fname)
		shows = ReadTextFile(path)
		PLog("path: " + path)
		PLog('full_shows_lines: %d' % len(shows))

		duration=py2_decode(duration)
		if " min" in duration:							# Bsp. "Videolänge 1 min", "33 min · Comedy"
			try:
				duration = re.search(r'(\d+) min', duration).group(1)
			except:
				duration=''
			
		if duration.startswith("Dauer "):				# Bsp. Dauer 0:01 od. Dauer 59 sec
			duration = duration.split("Dauer ")[1]
		if duration.endswith(" sec"):					# Bsp. 59 sec 
			duration = duration.split(" sec")[0]
		if ':' in duration:
			duration = time_to_minutes(duration)
		PLog("duration: " + duration)
		title = title.strip()

		ret = "nofill"									# Return-Flag
		for show in shows:
			st, sdur = show.split("|")					# Bsp. Querbeet|40
			#PLog(duration); PLog(st); PLog(sdur); # PLog(up_low(st) in up_low(title));
			# Show in Datensatz?:
			if up_low(st) in up_low(title_samml) or up_low(st) in up_low(summary): 
				if sdur:
					if ':' in sdur:
						sdur = time_to_minutes(duration)
					PLog("sdur: " + sdur)
					if int(duration) >= int(sdur):
						title = "[B]%s[/B]" % title
						ret = "fill"
				break		
	PLog("%s_return: %s" % (ret, title))
	return title
	
#-------------------------
# Bau HLS_List, MP4_List, HBBTV_List (nur ZDF + Arte)
# Formate siehe StreamsShow						
#	generisch: "Label |  Auflösung | Bitrate | Titel#Url"
#	fehlende Bandbreiten + Auflösungen werden ergänzt
# Aufrufer: ZDF_getVideoSources, SingleBeitrag (my3Sat)
# formitaeten: Blöcke 'formitaeten' (get_form_streams)
# 08.03.2022 Anpassung für Originalton + Audiodeskription (class_add)
# 21.01.2023 UHD-Streams für Testbetrieb ergänzt (add_UHD_Streams)
# ab V4.7.0 nur noch von SingleBeitrag (my3Sat) genutzt, ZDF s. 
#	ZDF_getApiStreams. page: json-Quelle (api.3sat.de), neu
#	kodiert ohne funk-Beiträge 
# 16.05.2024 Auswertung Bitraten entfernt (unsicher)
#
def build_Streamlists(li,title,thumb,geoblock,tagline,sub_path,page,scms_id='',ID="ZDF",weburl=''):
	PLog('build_Streamlists:'); PLog(ID)
	title_org = title	
	
	HLS_List=[]; MP4_List=[]; HBBTV_List=[];			# MP4_List = download_list
	skip_list=[]
	# erlaubte Formate wie ZDF_getApiStreams 
	form_list = ["h264_aac_mp4_http_na_na", "h264_aac_ts_http_m3u8_http",	# erlaubte Formate
				"vp9_opus_webm_http_na_na", "vp8_vorbis_webm_http_na_na"]
	try:			
		jsonObject = json.loads(page)
		prioList = jsonObject["priorityList"]
		PLog("prioList: %d" % len(prioList))
		for prio in prioList:
			formitaeten = prio["formitaeten"]
			PLog("formitaeten: %d" % len(formitaeten))
			for form in formitaeten:
				PLog(form["type"]); 
				if form["type"] in form_list:
					PLog(form["facets"])
					PLog("found_form: " + form["type"])
					facets = form["facets"]
					if "restriction_useragent" in facets:	# Server rodlzdf statt nrodlzdf sonst identisch
						continue 
					
					qualities = form["qualities"]
					PLog("qualities: %d" % len(qualities))
					for qual in qualities:
						track_add=''; class_add=''; lang_add=''; mimeCodec=""
						if "mimeCodec" in qual:				# fehlt bei HLS
							mimeCodec = qual["mimeCodec"]
						quality = up_low(qual["quality"])
						tracks = qual["audio"]["tracks"][0]	# nir 1 track bisher, adds + url
						PLog("tracks: %d" % len(tracks))
						class_add = tracks["class"]
						lang_add = tracks["language"]
						if class_add == "main": class_add = "TV-Ton"
						if class_add == "ot": class_add = "Originalton"
						if class_add == "ad": class_add = "Audiodeskription"
						if class_add or lang_add:
							track_add = "[B]%s %s[/B]" % (class_add, lang_add)
							track_add = "%23s" % track_add
						url = tracks["uri"]	
						if '?audiotrack=1' in url:
							url = url.split('?audiotrack=1')[0]					
						
						PLog("Satz_track:")
						PLog(class_add); PLog(lang_add); PLog(url); PLog(quality);
						url_combi = "%s|%s" % (class_add, url)
						if url_combi in skip_list:
							PLog("skip_url_combi: " + url_combi)
							continue
						skip_list.append(url)	
						
						if url.find('master.m3u8') > 0:					# m3u8 high (=auto) enthält alle Auflösungen
							if 'AUTO' in up_low(quality):				# skip high, med + low
								if track_add:
									HLS_List.append('HLS, %s ** AUTO ** %s ** %s#%s' % (track_add, quality,title,url))
								else:
									HLS_List.append('HLS, automatische Anpassung ** AUTO ** AUTO ** %s#%s' % (title,url))
								Stream_List = Parseplaylist(li, url, thumb, geoblock, tagline,\
									stitle=title,buttons=False, track_add=track_add)
								HLS_List = HLS_List + Stream_List
						else:
							res='0x0'; w='0'; h='0'											
							if 'HD' in quality:							# up_low(quality s.o.
								w = "1920"; h = "1080"					# Probeentnahme													
							if 'VERYHIGH' in quality:
								w = "1280"; h = "720"					# Probeentnahme							
							if 'HIGH' in quality:
								w = "960"; h = "540"					# Probeentnahme							
							if 'MED' in quality:
								w = "640"; h = "360"					# Probeentnahme							
							if 'LOW' in quality:
								w = "480"; h = "270"					# Probeentnahme							
							
							res = "%sx%s" % (w,h)
							PLog(res)
							title_url = u"%s#%s" % (title, url)
							mp4 = "%s" % "MP4"
							if ".webm" in url:
								mp4 = "%s" % "WEBM"
							item = u" %s, %s | %s ** Auflösung %s ** %s" %\
								(mp4, track_add, quality, res, title_url)
							MP4_List.append(item)
							
	except Exception as exception:
		PLog("formitaeten_error: " + str(exception))
		HLS_List=[]; MP4_List=[]
		
	PLog("HLS_List: " + str(len(HLS_List)))
	PLog("MP4_List: " + str(len(MP4_List)))
	

	# ------------										# HBBTV + UHD-Streams von ZDF + 3sat:
	UHD_DL_list=[]
	if ID == "3sat":									# 3sat 
		HBBTV_List = m3satSourcesHBBTV(weburl, title_org)	 				
		PLog("HBBTV_List: " + str(len(HBBTV_List)))
		# UHD-Streams erzeugen+testen:					# UHD-Streams -> HBBTV_List
		HBBTV_List, UHD_DL_list = add_UHD_Streams(HBBTV_List)
		Dict("store", '%s_HBBTV_List' % ID, HBBTV_List) 
		
	PLog("UHD_DL_list: " + str(len(UHD_DL_list)))
		
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	# MP4_List = add_UHD_Streams(MP4_List)				# entf., nur in HBBTV-Quellen (?)
	if len(UHD_DL_list) > 0:							# UHD_Liste für Downloads anhängen
		MP4_List = UHD_DL_list + MP4_List
	Dict("store", '%s_MP4_List' % ID, MP4_List) 
		
	tagline = "Titel: %s\n\n%s" % (title_org, tagline)	# s.a. ARD (Classic + Neu)
	tagline=repl_json_chars(tagline); tagline=tagline.replace( '||', '\n')
	Plot=tagline; 
	Plot=Plot.replace('\n', '||')
	
	HOME_ID = ID										# ZDF (Default), 3sat
	PLog('Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
		
	build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)
	
	PLog("build_Streamlists_end")		
	return HLS_List, MP4_List, HBBTV_List
	
#-------------------------
# Aufruf: build_Streamlists
# ZDF-UHD-Streams kennzeichnen
# verfügbare UHD-Streams werden oben in
#	MP4_List (->Downloadliste) eingefügt.
# 24.02.2023 replace("3360k_p36v15", "4692k_p72v16") entfällt
#	mit Auswertung "q5" in ZDFSourcesHBBTV "h265_*", Verfügbarkeits-
#	Ping ebenfalls entbehrlich.
# 
def add_UHD_Streams(Stream_List):
	PLog('add_UHD_Streams:')

	UHD_DL_list=[]; 
	cnt_find=0; cnt_ready=0
	mark="_4692k_"											# bei Bedarf ergänzen
	
	cnt=0
	for item in Stream_List:
		PLog(item)
		url = item.split("#")[-1]
		PLog(url)
		if url.find(mark) > 0:	 
			item = item.replace("MP4,", "[B]UHD_MP4[/B],")	# Label ändern
			item = item.replace("WEBM,", "[B]UHD_WEBM[/B],")
			Stream_List[cnt] = item							# Stream_List aktualisieren
			UHD_DL_list.append(item)						# add UHD-Download-Streams
			cnt_ready=cnt_ready+1

		cnt=cnt+1

	PLog(u"found_UDH_Template: %d" % cnt_find)
	return Stream_List, UHD_DL_list
	
#-------------------------
# Aufruf: build_Streamlists
# 3sat-HBBTV-MP4-Streams ermitteln, ähnlich
# 	ZDFSourcesHBBTV (["streams"] statt ["vidurls"])
def m3satSourcesHBBTV(weburl, title):
	PLog('m3satSourcesHBBTV: ' + weburl)

	stream_list=[]; HBBTV_List=[]
	base= "http://hbbtv.zdf.de/3satm/dyn/get.php?id="
	 
	try:
		url = weburl.split("/")[-1]				# ../kultur/kulturdoku/kuenstlerduelle-vangogh-gaugin-100.html
		url = url.split(".html")[0]
	except Exception as exception:
		PLog(str(exception))			
		return HBBTV_List

	header = "{'Host': 'hbbtv.zdf.de', 'content-type': 'application/vnd.hbbtv.xhtml+xml'}"
	path = base + url
	page, msg = get_page(path, header=header)	
	if page == '':		
		msg1 =  u'HBBTV-Quellen fehlen'
		msg2 = title
		icon = R('3sat.png')
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000, sound=False)

		return HBBTV_List
		
	jsonObject = json.loads(page)
	PLog('page_hbbtv_3sat: ' + str(jsonObject)[:100])
	
	form_list=["h265_aac_mp4_http_na_na", "h264_aac_mp4_http_na_na"] # bei hbbtv Verzicht auf m3u8
	q_list=["q5", "q4", "q3", "q2", "q1"]
	stream_list=[]
	try:
		streams = jsonObject["vidurls"]
		for stream in streams:
			for form in form_list:
				if form in stream:
					PLog("found_form: " + form)
					streamObject = streams[form]["main"]["deu"]	
					for q in q_list:
						if q in streamObject:
							add = "%s_%s_%s_%s" % (form[:4], "main", "deu", q)
							url = streamObject[q]
							line = "%s##%s##%s" % (title, add, url)
							stream_list.append(line)
	except Exception as exception:
		PLog(str(exception))
		stream_list=[]
				
	PLog(len(stream_list))
	PLog(str(stream_list))										
	HBBTV_List = form_HBBTV_Streams(stream_list, title)	# Formatierung wie ZDF-Streams	
	PLog(str(HBBTV_List))
	
	return HBBTV_List
	
#-------------------------
# Sofortstart + Buttons für die einz. Streamlisten
# Aufrufer: build_Streamlists (ZDF, 3sat), ARDStartSingle (ARD Neu),
#	SingleSendung (ARD Classic), XLGetSourcesPlayer
# Plot = tagline (zusammengefasst: Titel (abgesetzt), tagline, summary)
# Kennzeichung mit mediatype='video' vor aufrufenden Funktionenen, z.B.
#	StreamsShow, XLGetSourcesPlayer, ZDF_getApiStreams
#
def build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID="ZDF",HOME_ID="ZDF"):
	PLog('build_Streamlists_buttons:'); PLog(ID);  PLog(title_org)
	
	if geoblock and geoblock not in Plot:
		Plot = "%s||%s" % (Plot, geoblock) 
	
	title_org=repl_json_chars(title_org)
	tagline = Plot.replace('||', '\n')
	Plot = Plot.replace('\n', '||')
	
	# Sofortstart HLS / MP4 - abhängig von Settings	 	# Sofortstart
	played_direct=False
	if SETTINGS.getSetting('pref_video_direct') == 'true':	
		PLog('Sofortstart: build_Streamlists_buttons, ID: %s' % ID)
		played_direct=True
		img = thumb
		PlayVideo_Direct(HLS_List, MP4_List, title_org, img, Plot, sub_path, HBBTV_List=HBBTV_List,ID=ID)
		return played_direct							# direct-Flag z.B. für ARDStartSingle
		

	# -----------------------------------------			# Buttons Einzelauflösungen
	PLog("Satz3_items:")
	title_list=[]
	img=thumb; 
	PLog(title_org); PLog(tagline[:60]); PLog(img); PLog(sub_path);
	PLog(str(HBBTV_List))
	
	uhd_cnt_hb = str(HBBTV_List).count("UHD")				# UHD-Kennz. -> Titel ZDF+3sat
	uhd_cnt_hls = str(HLS_List).count("UHD")				# Arte
	uhd_cnt_mp4 = str(MP4_List).count("UHD")
	PLog("uhd_cnt: %d, %d, %d" % (uhd_cnt_hb, uhd_cnt_hls, uhd_cnt_mp4))
	
	title_hb = "[B]HBBTV[/B]-Formate"
	if uhd_cnt_hb:
		title_hb = title_hb + ", einschl. [B]UHD-Streams[/B]"
	title_hls 	= u"[B]Streaming[/B]-Formate"
	if uhd_cnt_hls:
		title_hls = title_hls + ", einschl. [B]UHD-Streams[/B]"
	title_mp4 = "[B]MP4[/B]-Formate und [B]Downloads[/B]"
	if uhd_cnt_mp4:
		title_mp4 = title_mp4 + ", einschl. [B]UHD-Streams[/B]"
	title_hls=repl_json_chars(title_hls); title_hb=repl_json_chars(title_hb);
	title_mp4=repl_json_chars(title_mp4); 
	
	# title_list: Titel + Dict-ID + Anzahl Streams
	title_list.append("%s###%s###%s" % (title_hls, '%s_HLS_List' % ID, len(HLS_List)))
	if ID == "ARDNEU" or ID == "ZDF" or ID == "arte" or ID == "3sat":			# HBBTV: ZDF, arte, 3sat
		listtyp = "%s_HBBTV_List" % ID
		title_list.append("%s###%s###%s" % (title_hb, listtyp, len(HBBTV_List)))	
	title_list.append("%s###%s###%s" % (title_mp4, '%s_MP4_List' % ID, len(MP4_List)))	
	PLog(len(title_list))
	PLog("title_list: " + str(title_list))	

	Plot=py2_encode(Plot); img=py2_encode(img);
	geoblock=py2_encode(geoblock); sub_path=py2_encode(sub_path); 
	
	for item in title_list:
		title, Dict_ID, anz = item.split('###')
		if anz == '0':									# skip leere Liste
			continue
		title=py2_encode(title); title_org=py2_encode(title_org);
		fparams="&fparams={'title': '%s', 'Plot': '%s', 'img': '%s', 'geoblock': '%s', 'sub_path': '%s', 'ID': '%s', 'HOME_ID': '%s'}" \
			% (quote(title_org), quote(Plot), quote(img), quote(geoblock), quote(sub_path), Dict_ID, HOME_ID)
		addDir(li=li, label=title, action="dirList", dirID="StreamsShow", fanart=img, thumb=img, 
			fparams=fparams, tagline=tagline, mediatype='')	
	
	return played_direct
	
#-------------------------
# HBBTV-MP4 Videoquellen (nur ZDF)	
# 17.05.2023 Auswertung vorerst	nur "main"|"deu" und "ad"|"deu"
#	mit MP4-Links (s. form_list)
# ähnlich in m3satSourcesHBBTV (["vidurls"] statt ["streams"])
# 23.10.2023 Ausfilterung DGS bei Sofortstart (ungeeignet für
#	Sortierung in PlayVideo_Direct).
#
def ZDFSourcesHBBTV(title, scms_id):
	PLog('ZDFSourcesHBBTV:'); 
	PLog("scms_id: " + scms_id) 
	HBBTV_List=[]
	url = "https://hbbtv.zdf.de/zdfm3/dyn/get.php?id=%s" % scms_id
		
	# Call funktioniert auch ohne Header:
	header = "{'Host': 'hbbtv.zdf.de', 'content-type': 'application/vnd.hbbtv.xhtml+xml'}"
	page, msg = get_page(path=url, header=header)	
	if page == '':						
		msg1 = u'HBBTV-Quellen nicht vorhanden / verfügbar'
		msg2 = u'Video: %s' % title
		MyDialog(msg1, msg2, '')
		return HBBTV_List
	
	jsonObject = json.loads(page)
	PLog('page_hbbtv: ' + str(jsonObject)[:100])
	if len(jsonObject["streams"]) == 0:
		return HBBTV_List
		
	label = jsonObject["streams"][0]["label"]				# i.d.R. "Normal", z.Z. nicht genutzt
	
	form_list=["h265_aac_mp4_http_na_na", "h264_aac_mp4_http_na_na"]
	q_list=["q5", "q4", "q3", "q2", "q1"]
	stream_list=[]
	# Audiodescription bei Bedarf nachrüsten (streamObject["ad"])
	
	try:
		streams = jsonObject["streams"]
		for stream in streams:
			for form in form_list:
				if form in stream:
					PLog("found_form: " + form)
					streamObject = stream[form]["main"]["deu"]	
					PLog(str(streamObject)[:80])
					for q in q_list:
						if q in streamObject:
							add = "%s_%s_%s_%s" % (form[:4], "main", "deu", q)
							url = streamObject[q]["url"]
							if "_dgs_" in url:				# DGS nicht bei Sofortstart
								if SETTINGS.getSetting('pref_video_direct') == 'true':
									continue
								add = "%s_%s_%s_%s_%s" % (form[:4], "main", "deu", "DGS", q)
							line = "%s##%s##%s" % (title, add, url)
							stream_list.append(line)
	except Exception as exception:
		PLog("streams_error: " + str(exception))
		stream_list=[]
			
	PLog(len(stream_list))
	HBBTV_List = form_HBBTV_Streams(stream_list, title)		# Formatierung
		
	PLog(len(HBBTV_List))
	PLog(str(HBBTV_List))
	return HBBTV_List
	
#-------------------------
# Aufruf: ZDFSourcesHBBTV, m3satSourcesHBBTV
# Formatierung der Streamlinks ("Qual.|Link")
# 17.05.2023 Anpassungen an Änderungen in ZDFSourcesHBBTV,
#	neue Reihenfolge im Streamtitel:  Auflösung | Bitrate 
# 16.05.2024 Auswertung Bitraten entfernt (unsicher)
#
def form_HBBTV_Streams(stream_list, title):
	PLog('form_HBBTV_Streams:')
	HBBTV_List=[]
	
	# line-format: 	"title ## add ## url"			# s. ZDFSourcesHBBTV
	# add-format: 	"form[:4]_main/ad_deu_q"	# - "-

	for line in stream_list:
		title, add, url = line.split("##")
		q = add.split("_")[-1]
		PLog("q: " + q)
		
		if q == 'q0':
			quality = u'GERINGE'
			w = "640"; h = "360"					# Probeentnahme	
			if u'm3u8' in url:
				bitrate = u"16 MB/Min."
		if q == 'q1':
			quality = u'HOHE'
			w = "960"; h = "540"					# Probeentnahme	
			if u'm3u8' in url:
				bitrate = u"16 MB/Min."
		if q == 'q2':
			quality = u'SEHR HOHE'
			w = "1024"; h = "576"					# Probeentnahme							
			if u'm3u8' in url:
				bitrate = u"19 MB/Min."
		if q == 'q3':
			quality = u'HD'
			w = "1280"; h = "720"					# Probeentnahme					
			if u'm3u8' in url:
				bitrate = u"23 MB/Min."
		if q == 'q4':
			quality = u'Full-HD'
			w = "1920"; h = "1080"					# Probeentnahme,					
			if u'm3u8' in url:
				bitrate = u"?"			
		if q == 'q5':
			quality = u'UHD'
			w = "3840"; h = "2160"					# Probeentnahme						
		
		res = "%sx%s" % (w,h)
		
		if u'm3u8' in url:
			stream_title = u'HLS, Qualität: [B]%s | %s[/B]' % (quality, add) # label: Normal, DGS, .
		else:
			stream_title = u'MP4, Qualität: [B]%s | %s[/B]' % (quality, add)

		title_url = u"%s#%s" % (title, url)
		item = u"%s ** Auflösung %s ** %s" %\
			(stream_title, res, title_url)
		PLog("item: " + item)
		HBBTV_List.append(item)	
		
	return HBBTV_List

#-------------------------
# ermittelt streamurls, duration, geoblock, sub_path
#
def get_form_streams(page):
	PLog('get_form_streams:')
	# Kodi: https://kodi.wiki/view/Features_and_supported_formats#Audio_playback_in_detail 
	#	AQTitle, ASS/SSA, CC, JACOsub, MicroDVD, MPsub, OGM, PJS, RT, SMI, SRT, SUB, VOBsub, VPlayer
	#	Für Kodi eignen sich beide ZDF-Formate xml + vtt, umbenannt in *.sub oder *.srt
	#	VTT entspricht SubRip: https://en.wikipedia.org/wiki/SubRip
	subtitles = stringextract('"captions"', ']', page)	# Untertitel ermitteln, bisher in Plex-
	subtitles = blockextract('"class"', subtitles)					# Channels nicht verwendbar
	PLog('subtitles: ' + str(len(subtitles)))
	sub_path = ''													# Format: "local_path|url", Liste 
	if len(subtitles) == 2:											#			scheitert in router
		# sub_xml = subtitles[0]									# xml-Format für Kodi ungeeignet
		sub_vtt = subtitles[1]	
		# PLog(sub_vtt)
		#sub_xml_path = stringextract('"uri": "', '"', sub_xml)# xml-Format
		sub_vtt_path = stringextract('"uri":"', '"', sub_vtt)	
		# PLog('Untertitel xml:'); PLog(sub_xml_path)
		PLog('Untertitel vtt:'); PLog(sub_vtt_path)
		
		# 20.01.2019 Pfad + Url in PlayVideo via listitem.setInfo direkt übergeben
		local_path = "%s/%s" % (SUBTITLESTORE, sub_vtt_path.split('/')[-1])
		local_path = local_path.replace('.vtt', '.sub')				# Endung für Kodi anpassen
		local_path = os.path.abspath(local_path)
		try:
			if os.path.isfile(local_path) == False:					# schon vorhanden?
				urlretrieve(sub_vtt_path, local_path)
		except Exception as exception:
			local_path = ''
			PLog(str(exception))
		sub_path = '%s|%s' % (local_path, sub_vtt_path)						
		PLog(sub_path)
				
	duration = stringextract('duration',  'fsk', page)	# Angabe im Kopf, sec/1000
	duration = stringextract('"value":',  '}', duration).strip()
	PLog(duration)	
	if duration:
		duration = int((int(duration) / 1000) / 60)		# Rundung auf volle Minuten reicht hier 
		duration = max(1, duration)						# 1 zeigen bei Werten < 1
		duration = str(duration) + " min"	
	PLog('duration: ' + duration)
	formitaeten = blockextract('formitaeten', page)		# Video-URL's ermitteln
	PLog('formitaeten: ' + str(len(formitaeten)))
	# PLog(formitaeten[0])								# bei Bedarf
				
	geoblock =  stringextract('geoLocation',  '}', page) 
	geoblock =  stringextract('"value": "',  '"', geoblock).strip()
	PLog('geoblock: ' + geoblock);
	if 	geoblock == 'none':								# i.d.R. "none", sonst "de" - wie bei ARD verwenden
		geoblock = ' | ohne Geoblock'
	else:
		if geoblock == 'de':			# Info-Anhang für summary 
			geoblock = ' | Geoblock DE!'
		if geoblock == 'dach':			# Info-Anhang für summary 
			geoblock = ' | Geoblock DACH!'
		
	return formitaeten, duration, geoblock, sub_path
	
#-------------------------
#	Einzelseite -> ZDF_BildgalerieSingle
def ZDF_Bildgalerien(pagenr=""):	
	PLog('ZDF_Bildgalerien: ' + str(pagenr)); 

	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	
	pic_path = "https://www.zdf.de/suche?q=%s&synth=true&usePartnerContent=true&syntheticProfile=large&sender=Gesamtes+Angebot&from=&to=&attrs=&abName=ab-2024-07-29&abGroup=gruppe-e&page=%s"
	pic_path = pic_path % ("Bilderserie", str(pagenr)) 
	PLog(pic_path)
	page, msg = get_page(path=pic_path, do_safe=False)	
	
	if page == '':
		msg1 = 'Keine (weiteren) Bilderserien gefunden' 
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID="ZDF")						# Home-Button
			
				
	page_cnt=0;
	content =  blockextract('class="artdirect"', page)
	for rec in content:	
		infoline = stringextract('infoline-text="', '"', rec)
		if " Bilder " in infoline == False:
			continue
		tag = unescape(infoline); tag=cleanhtml(tag)		# einschl. Anzahl Bilder
			
		category = stringextract('teaser-cat-category">', '</span>', rec)
		category = mystrip(category)
		PLog(category)
		brand = stringextract('brand-ellipsis">', '</span>', rec)
		brand = mystrip(brand)	
		PLog(brand)

		thumb =  stringextract('data-srcset="', ' ', rec)	
		href = stringextract('a href', '</a>', rec)
		path  = stringextract('="', '"', href)
		if path == '':										# Sicherung
			path = 	stringextract('plusbar-url="', '"', rec)
		if path.startswith("http") == False:
			path = "https://www.zdf.de" + path
		if path == "https://www.zdf.de":					# ohne Link zur Bilderserie
			continue

		title = stringextract('title="', '"', href)			# falls leer -> descr, s.u.
			
		descr = stringextract('description">', '<', rec)
		if descr == '':
			descr = stringextract('teaser-text">', '<', rec) # mehrere Varianten möglich
		if descr == '':
			descr = stringextract('class="teaser-text" >', '<', rec)
		descr = mystrip(descr.strip())
		PLog('descr:' + descr)		# UnicodeDecodeError möglich
		
		if title == '':
			title =  descr		
		
		airtime = stringextract('class="air-time" ', '</time>', rec)
		airtime = stringextract('">', '</time>', airtime)
		if airtime:
			tag = "%s | %s" % (tag, airtime)
		if category:
			tag = "%s | %s" % (tag, category)
		if brand:
			tag = "%s | %s" % (tag, brand)
						
		title = unescape(title); summ = unescape(descr)
		title=repl_json_chars(title); summ=repl_json_chars(summ)	
		PLog('neuer_Satz')
		PLog(thumb);PLog(path);PLog(title);PLog(summ);PLog(tag);
		
		path=py2_encode(path); title=py2_encode(title);
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))	
		addDir(li=li, label=title, action="dirList", dirID="ZDF_BildgalerieSingle", fanart=thumb, thumb=thumb, 
			fparams=fparams, summary=summ,  tagline=tag)
		page_cnt = page_cnt + 1
	
	PLog("Serien: %s" % str(page_cnt))
	
	#--------------------------------------------------------			# nächste Seite
	if page_cnt >= 20:
		img = R(ICON_ZDF_BILDERSERIEN)
		pagenr =  int(pagenr)+1
		tag = "zu Seite %d" % pagenr
		fparams="&fparams={'pagenr': '%s'}" % str(pagenr)
		addDir(li=li, label="Mehr: Bilderserien", action="dirList", dirID="ZDF_Bildgalerien", \
			fanart=img, thumb=img, fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-------------------------
# Lösung mit einzelnem Listitem wie in ShowPhotoObject (FlickrExplorer) hier
#	nicht möglich (Playlist Player: ListItem type must be audio or video) -
#	Die li-Eigenschaft type='image' wird von Kodi nicht akzeptiert, wenn
#	addon.xml im provides-Feld video enthält. Daher müssen die Bilder hier
#	im Voraus geladen werden.
# Ablage im SLIDESTORE, Bildverz. wird aus Titel erzeugt. Falls ein Bild
#	nicht existiert, wird es via urlretrieve geladen.
# 04.02.2020 Umstellung Bildladen auf Thread (thread_getfile).
# 07.02.2020 wegen Rekursion (Rücksprung zu ZDF_getVideoSources) Umstellung:
#	Auswertung des Suchergebnisses (s. ZDF_Search) in ZDF_Bildgalerien,
#	Auswertung Einzelgalerie hier.
# 23.09.2021 Umstellung Bildname aus Quelle statt "Bild_01" (eindeutiger beim
#	Nachladen).
# 19.05.2022 Param. li: Vermeid. Home-Doppel (Aufruf ZDF_get_content)
#
def ZDF_BildgalerieSingle(path, title, li=''):	
	PLog('ZDF_BildgalerieSingle:'); PLog(path); PLog(title)
	title_org = title
	
	
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden: [B]%s[/B]' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	
	if li == '':
		li = xbmcgui.ListItem()
		li = home(li, ID="ZDF")						# Home-Button
	
	# gallery-slider-box: echte Bildgalerien, andere spielen kaum eine Rolle
	#	bei Fehlen auf Weiterleitung prüfen (z.B. in lazyload-container):
	if page.find(u'class="content-box gallery-slider-box') < 0:
		PLog('check_extern_link:')
		href=''
		href_list = blockextract('a href=', page, '</a>')
		for h in href_list:
			PLog(h[:80])
			if u'#gallerySlide=0' in h:
				href = stringextract('href="', '"', h)
				break
		if href:
			PLog('get_extern_link')
			page, msg = get_page(path=href)	
		
	content =  stringextract(u'class="content-box gallery-slider-box', u'title="Bilderserie schließen"', page)
	content = blockextract('class="img-container', content)	
	PLog("content: " + str(len(content)))
	
	if len(content) == 0:										
		msg1 = 'ZDF_BildgalerieSingle: keine Bilder gefunden.'
		msg2 = title
		MyDialog(msg1, msg2, '')
		return li
	
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

	image=0; background=False; path_url_list=[]; text_list=[]
	for rec in content:				
		category = stringextract('teaser-cat-category">', '</span>', rec)
		category = mystrip(category)
		PLog(category)
		brand = stringextract('brand-ellipsis">', '</span>', rec)
		brand = mystrip(brand)	
		PLog(brand)

		img_links =  stringextract('data-srcset="', '"', rec)	# mehrere Links, aufsteig. Bildgrößen
		img_links = blockextract('http', img_links)
		w_old=0
		for img_link in img_links:
			img_link = img_link.split(' ')[0]					# Link bis 1. Blank: ..?cb=1462007560755 384w 216h
			w=''
			w_h = stringextract('~', '?cb', img_link)			# Bsp.: ..-2014-100~384x216?cb=1462007562325
			PLog(img_link); PLog(w_h)
			if "x" in w_h:
				w  = w_h.split('x')[0]							# Bsp.: 384
				if int(w) > w_old and int(w) <= 1280:			# Begrenz.: 1280 (gesehen: 3840)
					w_old = int(w)
					
		img_src  = img_link
		PLog("img_src: %s, w: %d" % (img_link, w_old))			
					
		href = stringextract('a href', '</a>', rec)
		path  = stringextract('="', '"', href)
		if path == '':										# Sicherung
			path = 	stringextract('plusbar-url="', '"', rec)
		if path.startswith("http") == False:
			path = "https://www.zdf.de" + path
		title = stringextract('title="', '"', href)			# falls leer -> descr, s.u.
			
		descr = stringextract('description">', '<', rec)
		if descr == '':
			descr = stringextract('teaser-text">', '<', rec) # mehrere Varianten möglich
		if descr == '':
			descr = stringextract('class="teaser-text" >', '<', rec)
		descr = mystrip(descr.strip())
		PLog('descr:' + descr)		# UnicodeDecodeError möglich
		
		if title == '':
			title =  descr
		lable = title				# Titel in Textdatei	
				
		
		tag = stringextract('"teaser-info">', '</dd>', rec)		# Quelle
		tag = cleanhtml(tag); tag = mystrip(tag)
		airtime = stringextract('class="air-time" ', '</time>', rec)
		airtime = stringextract('">', '</time>', airtime)
		if airtime:
			tag = "%s | %s" % (tag, airtime)
		if category:
			tag = "%s | %s" % (tag, category)
		if brand:
			tag = "%s | %s" % (tag, brand)
		
				
		if img_src == '':									# Sicherung			
			PLog('Problem in Bildgalerie: Bild nicht gefunden')
		else:		
			if tag:
				tag = "%s | %s" % (tag, title_org)
			
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			# pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
			pic_name 	= img_src.split('/')[-1]			# Bildname aus Quelle
			if '?' in pic_name:								# Bsp.: ~2400x1350?cb=1631630217812
				pic_name = pic_name.split('?')[0]
			local_path 	= "%s/%s.jpg" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d: %s" % (image+1, pic_name)	# Numerierung
			PLog("Bildtitel: " + title)
			summ = unescape(descr)			
			
			thumb = ''
			local_path 	= os.path.abspath(local_path)
			thumb = local_path
			if os.path.isfile(local_path) == False:			# schon vorhanden?
				# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Bild-Url, 
				#								 Zieldatei_kompletter_Pfad|Bild-Url, ..
				path_url_list.append('%s|%s' % (local_path, img_src))

				if SETTINGS.getSetting('pref_watermarks') == 'true':
					txt = "%s\n%s\n%s\n%s\n" % (fname,title,tag,summ)
					text_list.append(txt)	
				background	= True											
									
			title=repl_json_chars(title); summ=repl_json_chars(summ)
			PLog('neu:');PLog(title);PLog(img_src);PLog(thumb);PLog(summ[0:40]);
			if thumb:	
				local_path=py2_encode(local_path);
				fparams="&fparams={'path': '%s', 'single': 'True'}" % quote(local_path)
				addDir(li=li, label=title, action="dirList", dirID="ZDF_SlideShow", 
					fanart=thumb, thumb=thumb, fparams=fparams, summary=summ, tagline=tag)

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
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDF_SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
		
		lable = u"Alle Bilder in diesem Bildverzeichnis löschen"		# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)
		
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern

#-----------------------
# PhotoObject fehlt in kodi - wir speichern die Bilder in SLIDESTORE und
#	übergeben an xbmc.executebuiltin('SlideShow..
# ClearUp in SLIDESTORE s. Modulkopf
# Aufrufer: ZDF_BildgalerieSingle, ARDSportBilder, XL_Bildgalerie,
#	BilderDasErsteSingle
# Um die Wasserzeichen (unten links) zu sehen, sind in Kodi's Player
#	die Schwenkeffekte abzuschalten.  
def ZDF_SlideShow(path, single=None):
	PLog('ZDF_SlideShow: ' + path)
	local_path = os.path.abspath(path)
	PLog(local_path)
	if single:							# Einzelbild
		return xbmc.executebuiltin('ShowPicture(%s)' % local_path)
	else:
		return xbmc.executebuiltin('SlideShow(%s, %s)' % (local_path, 'notrandom'))

	 
####################################################################################################
def Parseplaylist(li, url_m3u8, thumb, geoblock, descr, sub_path='', stitle='', buttons=True, track_add='', live=''):	
#	# master.m3u8 bzw. index.m3u8 auswerten, Url muss komplett sein. 
#  	1. Besonderheit: in manchen *.m3u8-Dateien sind die Pfade nicht vollständig,
#	sondern nur als Ergänzung zum Pfadrumpf (ohne Namen + Extension) angegeben, Bsp. (Arte):
#	delive/delive_925.m3u8, url_m3u8 = http://delive.artestras.cshls.lldns.net/artestras/contrib/delive.m3u8
#	Ein Zusammensetzen verbietet sich aber, da auch in der ts-Datei (z.B. delive_64.m3u8) nur relative 
#	Pfade angegeben werden. Beim Redirect des Videoplays zeigt dann der Pfad auf das Plugin und Plex
#	versucht die ts-Stücke in Dauerschleife zu laden.
#	Wir prüfen daher besser auf Pfadbeginne mit http:// und verwerfen Nichtpassendes - auch wenn dabei ein
#	Sender komplett ausfällt.
#	Lösung ab April 2016:  Sonderbehandlung Arte in Arteplaylists.						
#	ARTE ab 10.03.2017:	 die m3u8-Links	enthalten nun komplette Pfade. Allerdings ist SSL-Handshake erforderlich zum
#		Laden der master.m3u8 erforderlich (s.u.). Zusätzlich werden in	CreateVideoStreamObject die https-Links durch 
#		http ersetzt (die Streaming-Links funktionieren auch mit http).	
#		SSL-Handshake für ARTE ist außerhalb von Plex nicht notwendig!
#  	2. Besonderheit: fast identische URL's zu einer Auflösung (...av-p.m3u8, ...av-b.m3u8) Unterschied n.b.
#  	3. Besonderheit: für manche Sendungen nur 1 Qual.-Stufe verfügbar (Bsp. Abendschau RBB)
#  	4. Besonderheit: manche Playlists enthalten zusätzlich abgeschaltete Links, gekennzeichnet mit #. Fehler Webplayer:
#		 crossdomain access denied. Keine Probleme mit OpenPHT und VLC - betr. nur Plex.
#  	10.08.2017 Filter für Video-Sofort-Format - wieder entfernt 17.02.2018
#	23.02.2020 getrennte Video- und Audiostreams bei den ZDF-Sendern (ZDF, ZDFneo, ZDFinfo - nicht bei 3sat +phoenix)
#		 - hier nur Auflistung der Audiostreams 
#	19.12.2020 Sendungs-Titel ergänzt (optional: stitle)
#	03.03.2020 Erweiterung buttons: falls False keine Buttons sondern Rückgabe als Liste
#		Stream_List (Format s.u.)
#	23.04.2022 Mehrkanalstreams mit Kennung GROUP-ID entfernen (in Kodi nicht verwertbar) - nicht mehr relevant
#		mit Sender-Liste für Einzelauflösungen
#	29.10.2022 Bereinigung Sender-Liste mit mögl. Einzelauflösungen (entfernt: HR, NDR, WDR)
#
	PLog ('Parseplaylist: ' + url_m3u8)
	Stream_List=[]

	if SETTINGS.getSetting('pref_video_direct') == 'true' and buttons:	# nicht für Stream_List
		return li

	playlist = ''
	# seit ZDF-Relaunch 28.10.2016 dort nur noch https
	if url_m3u8.startswith('http') == True :							# URL oder lokale Datei?
		url_check(url_m3u8, caller='Parseplaylist', dialog=False)		# o. Dialog (wg. Nutzung strm-Thread)				
		playlist, msg = get_page(path=url_m3u8)				
		if playlist == '':
			icon = R(ICON_WARNING)
			msg1 = "Streamquelle kann nicht geladen werden."
			msg2 = 'Fehler: %s'	% (msg)
			xbmcgui.Dialog().notification(msg1, msg2,icon,5000)
			if buttons:
				return li
			else:
				return []										# leere Liste für build_Streamlists				
	else:														# lokale Datei	
		fname =  os.path.join(M3U8STORE, url_m3u8) 
		playlist = RLoad(fname, abs_path=True)					
	 
	PLog('playlist: ' + playlist[:100])
	PLog('live: ' + str(live))
	skip_list = ["/srfsgeo/",									# keine Mehrkanalstreams: Einzelauflösungen mögl.,
				"/dwstream",									#	letzter Test: 04.12.2024
				"/arteliveext.akamaized", 
				"/tagesschau.akamaized"
				]
	PLog('#EXT-X-MEDIA' in playlist)
	# live=True: skip 1 Button, Altern.: Merkmal "_sendung_" in url_m3u8
	if '#EXT-X-MEDIA' in playlist:								# Mehrkanalstreams: 1 Button
		skip=False
		for item in skip_list:
			if item in url_m3u8:
				skip=True										# i.d.R. ARD-Streams (nicht alle)
				break
	
		PLog('skip: ' + str(skip))
		if skip == False and live:								# Mehrkanalstreams: nur 1 Button
			stitle = "HLS-Stream"
			PLog("jump_PlayButtonM3u8")
			PlayButtonM3u8(li, url_m3u8, thumb, stitle, tagline=track_add, descr=descr)	# -> live=true
			return
	
	
	li = xbmcgui.ListItem()	
	lines = playlist.splitlines()
	# PLog(lines)
	BandwithOld 	= ''			# für Zwilling -Test (manchmal 2 URL für 1 Bandbreite + Auflösung) 
	NameOld 		= []			# für Zwilling -Test bei ZDF-Streams (nicht hintereinander)
	thumb_org=thumb; descr_org=descr 	# sichern
	
	i = 0; li_cnt = 1; url=''
	for i, line in enumerate(lines):
		thumb=thumb_org
		res_geo=''; label=''; BandwithInt=0; Resolution_org=''
		# Abgrenzung zu ts-Dateien (Bsp. Welt24): #EXT-X-MEDIA-SEQUENCE: 9773324
		# Playlist Tags s. https://datatracker.ietf.org/doc/html/rfc8216
		if line.startswith('#EXT-X-MEDIA:') == False and line.startswith('#EXT-X-STREAM-INF') == False:
			continue
		if ',GROUP-ID' in line:									# zusätzl. Mehrkanalstreams (Audio)
			continue
		PLog("line: " + line)
			
		if line.startswith('#EXT-X-STREAM-INF'):				# tatsächlich m3u8-Datei?
			url = lines[i + 1]									# URL in nächster Zeile
			PLog("url: " + url)
			Bandwith = GetAttribute(line, 'BANDWIDTH')
			Resolution = GetAttribute(line, 'RESOLUTION')
			Resolution_org = Resolution							# -> Stream_List

			try:
				BandwithInt	= int(Bandwith)
			except:
				BandwithInt = 0
			if Resolution:	# fehlt manchmal (bei kleinsten Bandbreiten)
				Resolution = u'Auflösung ' + Resolution
			else:
				Resolution = u'Auflösung unbekannt'				# verm. nur Ton? CODECS="mp4a.40.2"
				thumb=R(ICON_SPEAKER)
			Codecs = GetAttribute(line, 'CODECS')
			# als Titel wird die  < angezeigt (Sender ist als thumb erkennbar)
			title='Bandbreite ' + Bandwith
			if url.find('#') >= 0:	# Bsp. SR = Saarl. Rundf.: Kennzeichnung für abgeschalteten Link
				Resolution = u'zur Zeit nicht verfügbar!'
			if url.startswith('http') == False:   				# relativer Pfad? 
				pos = url_m3u8.rfind('/')						# m3u8-Dateinamen abschneiden
				url = url_m3u8[0:pos+1] + url 					# Basispfad + relativer Pfad
			if Bandwith == BandwithOld:	# Zwilling -Test
				title = 'Bandbreite ' + Bandwith + ' (2. Alternative)'
			
			PLog(Resolution); PLog(BandwithInt); 
			# nur Audio (Bsp. ntv 48000, ZDF 96000), 
			if BandwithInt and BandwithInt <=  100000:
				Resolution = Resolution + ' (nur Audio)'
				thumb=R(ICON_SPEAKER)
			res_geo = Resolution+geoblock
			BandwithOld = Bandwith
		else:
			continue

		label = "%s" % li_cnt + ". " + title
		if res_geo:
			label = "%s | %s" % (label, res_geo)
						
		# quote für url erforderlich wg. url-Inhalt "..sd=10&rebase=on.." - das & erzeugt in router
		#	neuen Parameter bei dict(parse_qs(paramstring)
		Plot = descr_org
		if "\n" in Plot:
			Plot = repl_dop(Plot.splitlines())
			Plot = "\n".join(Plot)
		Plot = Plot.replace('\n', '||')	
		descr = Plot.replace('||', '\n')		
	
		if descr.strip() == '|':								# ohne EPG: EPG-Verbinder entfernen
			descr=''
			
		if url.startswith('http') == False: 					# kompl. Pfad fehlt - Bsp.: one, kika
			continue
		
		summ=''
		if stitle:
			summ = u"Sendung: %s" % py2_decode(stitle)
		
		PLog("SatzParse:")
		PLog(title); PLog(label); PLog(url[:80]); PLog(thumb); PLog(Plot[:80]); PLog(descr[:80]); 
		
		if buttons:												# Buttons, keine Stream_List
			title=py2_encode(title); url=py2_encode(url);
			thumb=py2_encode(thumb); Plot=py2_encode(Plot); 
			sub_path=py2_encode(sub_path);
			fparams="&fparams={'url': '%s','title': '%s','thumb': '%s','Plot': '%s','sub_path': '%s','live': '%s'}" %\
				(quote_plus(url), quote_plus(title), quote_plus(thumb), quote_plus(Plot), 
				quote_plus(sub_path), live)
			addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
				mediatype='video', tagline=descr, summary=summ) 
		else:													# nur Stream_List füllen
			# Format: "HLS Einzelstream | Auflösung | Bitrate | Titel#Url"
			if Resolution_org=='':
				Resolution_org = "0x0 Audiostream"				# 0x0 -> sorted in PlayVideo_Direct
			PLog("append: %s, %s.." % (Resolution_org, str(BandwithInt)))
			Stream_List.append(u'HLS-Stream ** Auflösung %s ** Bitrate %s ** %s#%s' %\
				(Resolution_org, str(BandwithInt), stitle, url)) # wie Downloadliste
			if track_add:										# TV-Ton deu, Originalton eng usw.
				Stream_List[-1] = Stream_List[-1].replace("HLS-Stream", "HLS, %s" % track_add)
		
		li_cnt = li_cnt + 1  	# Listitemzähler												
  	
	if i == 0:	# Fehler
		line1 = 'Kennung #EXT-X-STREAM-INF / #EXT-X-MEDIA fehlt'
		line2 = 'oder den Streamlinks fehlt http / https'
		MyDialog(line1, line2, '')
	
	if buttons:
		return li
	else:
		return Stream_List
		
####################################################################################################
# Ausführung nur ohne Sofortstart - bei Sofortstart ruft build_Streamlists_buttons
#	PlayVideo_Direct auf (Auswahl Format/Qualität -> PlayVideo).
# Streambuttons HLS / MP4 (ID-abh.), einschl. Downloadbuttons bei MP4-Liste
# Streamliste wird aus Dict geladen (Datei: ID)
#	Bandbreite + Auflösung können fehlen (Qual. < hohe, Audiostreams)
# Formate:
#	"HLS automatische Anpassung ** auto ** auto ** Titel#Url"  	# master.m3u8
# 	"HLS Einzelstream ** Auflösung ** Bandbreite ** Titel#Url" (wie Downloadliste)"
#
#	"MP4 Qualität: niedrige ** leer **leer ** Titel#Url"	
#	"MP4 Qualität: Full HD ** Auflösung ** Bandbreite ** Titel#Url"
# Anzeige: aufsteigend (beide Listen)
# Aufrufer: build_Streamlists_buttons (Aufrufer: ARDStartSingle (ARD Neu), 
#	build_Streamlists (ZDF,  my3Sat), SingleSendung (ARD Classic)
# 
# Plot = tagline (zusammengefasst: Titel, tagline, summary)
# 10.11.2021 Sortierung der MP4-Liste von Auflösung nach Bitrate geändert
# 05.05.2022 Wechsel-Button zu den DownloadTools hinzugefügt 
# 20.05.2023 Sortierung MP4-Liste wieder nach Auflösung (verlässlicher),
#	dto. in PlayVideo_Direct
#
def StreamsShow(title, Plot, img, geoblock, ID, sub_path='', HOME_ID="ZDF"):	
	PLog('StreamsShow:'); PLog(ID)
	title_org = title; 
	
	li = xbmcgui.ListItem()
	li = home(li, ID=HOME_ID)						# Home-Button

	Stream_List = Dict("load", ID)
	PLog(str(Stream_List)[:80])
	PLog(len(Stream_List))

	try:
		if u"Auflösung" in str(Stream_List):
			Stream_List = sorted(Stream_List,key=lambda x: int(re.search(r'sung (\d+)x', x).group(1)))		
	except Exception as exception:					# bei HLS/"auto", problemlos da vorsortiert durch Sender 
		PLog("sort_error:  " + str(exception))

	title_org=py2_encode(title_org);  img=py2_encode(img);
	sub_path=py2_encode(sub_path); 	Plot=py2_encode(Plot); 
	
	tagline_org = Plot.replace('||', '\n')

	cnt=1
	for item in Stream_List:
		item = py2_encode(item)
		PLog("item: " + item[:80])
		bitrate=""
		if item.count("**") == 3:										# mit bitrate
			label_item, bitrate, res, title_href = item.split('**')
			bitrate = bitrate.replace('Bitrate 0', 'Bitrate ?')			# Anpassung für funk ohne AzureStructure
			res = res.replace('0x0', '?')								# dto.
		else:															# ohne bitrate
			label_item, res, title_href = item.split('**')
		PLog("title_href: " + title_href)
		title, href = title_href.split('#')
		
		PLog(title); PLog(label_item); PLog(tagline_org[:80]); PLog(sub_path)
		tagline = tagline_org
		
		label = "%d. %s | %s" % (cnt, label_item, res)
		if bitrate:														# HLS: numeriert, mit bitrate
			label = "%s | %s | %s" % (label_item, bitrate, res)

		cnt = cnt+1
		href=py2_encode(href); title=py2_encode(title);
		
		# 17.06.2021 Absturz mit 'video' nach Sofortstart aus Kontextmenü nicht
		#	mehr relevant
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(quote_plus(href), quote_plus(title_org), quote_plus(img), 
			quote_plus(Plot), quote_plus(sub_path))
		addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			tagline=tagline, mediatype='video')
	
	if 'MP4_List' in ID:
		# ohne check Error mögl. (LibreElec 10.0) - setLabel=None in addDir
		if check_Setting('pref_use_downloads'):						
			summ=''
			li = test_downloads(li,Stream_List,title,summ,tagline,img,high=-1, sub_path=sub_path) # Downloadbutton(s)
			
			# Wechsel-Button zu den DownloadTools:	
			tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
			fparams="&fparams={}"
			addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
				fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
			    
####################################################################################################
#						Hilfsfunktionen - für Kodiversion augelagert in Modul util.py
####################################################################################################
# Bsp. paramstring (ab /?action):
#	url: plugin://plugin.video.ardundzdf/?action=dirList&dirID=Main_ARD&
#	fanart=/resources/images/ard-mediathek.png&thumb=/resources/images/ard-mediathek.png&
#	params={&name=ARD Mediathek&sender=ARD-Alle:ard::ard-mediathek.png}
# 17.11.2019 mit Modul six + parse_qs erscheinen die Werte als Liste,
#	Bsp: {'action': ['dirList']}, vorher als String: {'action': 'dirList'}.
#	fparams wird hier in unicode erwartet, s. py2_decode(fparams) in addDir
#---------------------------------------------------------------- 
def router(paramstring):
	# paramstring: Dictionary mit
	# {<parameter>: <value>} Elementen
	paramstring = unquote_plus(paramstring)
	# PLog(' router_params1: ' + paramstring)
	PLog(type(paramstring));
		
	if paramstring:	
		params = dict(parse_qs(paramstring[1:]))
		# PLog(' router_params_dict: ' + str(params))
		try:
			if 'content_type' in params:
				if params['content_type'] == 'video':	# Auswahl im Addon-Menü
					Main()
			PLog('router action: ' + params['action'][0]) # hier immer action="dirList"
			PLog('router dirID: ' + params['dirID'][0])
			PLog('router fparams: ' + params['fparams'][0])
		except Exception as exception:
			PLog(str(exception))

		if params['action'][0] == 'dirList':			# Aufruf Directory-Listing
			newfunc = params['dirID'][0]
			func_pars = params['fparams'][0]

			# Modul laden, Funktionsaufrufe + Parameterübergabe via Var's 
			#	s. 00_Migration_ardundzdf.txt
			# Modulpfad immer ab resources - nicht verkürzen.
			# Direktsprünge: Modul wird vor Sprung in Funktion geladen.
			if '.' in newfunc:						# Funktion im Modul, Bsp.:				
				l = newfunc.split('.')				# Bsp. resources.lib.updater.update
				PLog(l)
				newfunc =  l[-1:][0]				# Bsp. updater
				dest_modul = '.'.join(l[:-1])
				
				PLog(' router dest_modul: ' + str(dest_modul))
				PLog(' router newfunc: ' + str(newfunc))
				# Codeausführung außerhalb der Funktionen vor func()!
				try:
					dest_modul = importlib.import_module(dest_modul )	# Modul laden, Params -> sys.argv
				except Exception as exception:
					PLog("func_error_modul: " + str(exception))

				PLog('loaded: ' + str(dest_modul))
				#PLog(' router_params_dict: ' + str(params))			# Debug Modul-params
				
				try:
					# func = getattr(sys.modules[dest_modul], newfunc)  # falls beim Start geladen
					func = getattr(dest_modul, newfunc)					# geladen via importlib
				except Exception as exception:
					PLog("func_error_lib: " + str(exception))
					func = ''
				if func == '':						# Modul nicht geladen - sollte nicht
					li = xbmcgui.ListItem()			# 	vorkommen - s. Addon-Start
					msg1 = "Modul %s fehlt / ist nicht geladen" % dest_modul
					msg2 = "oder Funktion %s wurde nicht gefunden." % newfunc
					msg3 = "Alter Eintrag in Merkliste oder Favoriten?"
					PLog(msg1)
					MyDialog(msg1, msg2, msg3)
					xbmcplugin.endOfDirectory(HANDLE)

			else:
				try:
					func = getattr(sys.modules[__name__], newfunc)	# Funktion im Haupt-PRG OK
				except Exception as exception:
					PLog("func_error: " + str(exception))
					msg1 = "Funktion %s wurde nicht gefunden." % newfunc
					msg2 = "Alter Eintrag in Merkliste oder Favoriten?"
					MyDialog(msg1, msg2)
					xbmcplugin.endOfDirectory(HANDLE)
						
			
			PLog(' router func_getattr: ' + str(func))		
			if func_pars != '""':		# leer, ohne Parameter?	
				# func_pars = unquote_plus(func_pars)		# quotierte url auspacken - entf.
				PLog(' router func_pars unquote_plus: ' + str(func_pars))
				try:
					# Problem (spez. Windows): Parameter mit Escapezeichen (Windows-Pfade) müssen mit \\
					#	behandelt werden und werden dadurch zu unicode-Strings. Diese benötigen in den
					#	Funktionen eine UtfToStr-Behandlung.
					# Keine /n verwenden (json.loads: need more than 1 value to unpack)
					func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
					func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
					
					PLog("json.loads func_pars: " + func_pars)
					PLog('json.loads func_pars type: ' + str(type(func_pars)))
					mydict = json.loads(func_pars)
					PLog("mydict: " + str(mydict)); PLog(type(mydict))
				except Exception as exception:
					PLog('router_exception: {0}'.format(str(exception)))
					mydict = ''
				
				# PLog(' router func_pars: ' + str(type(mydict)))
				if 'dict' in str(type(mydict)):				# Url-Parameter liegen bereits als dict vor
					mydict = mydict
				else:
					mydict = dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in func_pars.split(',')))			
				PLog(' router func_pars: mydict: %s' % str(mydict))
				func(**mydict)
			else:
				func()
		else:
			PLog('router action-params: ?')
	else:
		# Plugin-Aufruf ohne Parameter
		Main()

#---------------------------------------------------------------- 

PLog('Addon_URL: ' + PLUGIN_URL)		# sys.argv[0], plugin://plugin.video.ardundzdf/
PLog('ADDON_ID: ' + ADDON_ID); PLog(SETTINGS); PLog(ADDON_NAME);PLog(SETTINGS_LOC);
PLog(ADDON_PATH);PLog(ADDON_VERSION);
PLog('HANDLE: ' + str(HANDLE))
PLog('PluginAbsPath: ' + PluginAbsPath)

PLog('Addon: Start')
if __name__ == '__main__':
	try:
		router(sys.argv[2])
		# Memory-Bereinig. unwirksam gegen Raspi-Klemmer (s. SenderLiveListe)
		#del get_ZDFstreamlinks, get_ARDstreamlinks, get_IPTVstreamlinks
	except Exception as e: 
		msg = str(e)
		PLog('network_error_main: ' + msg)

























