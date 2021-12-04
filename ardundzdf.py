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
# 	<nr>6</nr>										# Numerierung für Einzelupdate
VERSION = '4.1.4'
VDATE = '04.12.2021'


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
FAVORITS_Pod 	= 'podcast-favorits.txt' 	# Lesezeichen für Podcast-Erweiterung 
FANART					= 'fanart.png'		# ARD + ZDF - breit
ART 					= 'art.png'			# ARD + ZDF
ICON 					= 'icon.png'		# ARD + ZDF
ICON_SEARCH 			= 'ard-suche.png'
ICON_ZDF_SEARCH 		= 'zdf-suche.png'				
ICON_FILTER				= 'icon-filter.png'	

ICON_MAIN_ARD 			= 'ard-mediathek.png'
ICON_MAIN_ZDF 			= 'zdf-mediathek.png'
ICON_MAIN_ZDFMOBILE		= 'zdf-mobile.png'
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
ICON_ZDF_MEIST 			= 'zdf-meist-gesehen.png'
ICON_ZDF_BARRIEREARM 	= 'zdf-barrierearm.png'
ICON_ZDF_BILDERSERIEN 	= 'zdf-bilderserien.png'

ICON_MAIN_POD			= 'radio-podcasts.png'
ICON_POD_AZ				= 'pod-az.png'
ICON_POD_FEATURE 		= 'pod-feature.png'
ICON_POD_TATORT 		= 'pod-tatort.png'
ICON_POD_RUBRIK	 		= 'pod-rubriken.png'
ICON_POD_NEU			= 'pod-neu.png'
ICON_POD_MEIST			= 'pod-meist.png'
ICON_POD_REFUGEE 		= 'pod-refugee.png'
ICON_POD_FAVORITEN		= 'pod-favoriten.png'

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

ICON_DIR_VIDEO 			= "Dir-video.png"
ICON_DIR_WORK 			= "Dir-work.png"
ICON_MOVEDIR_DIR 		= "Dir-moveDir.png"
ICON_DIR_FAVORITS		= "Dir-favorits.png"

ICON_DIR_WATCH			= "Dir-watch.png"
ICON_PHOENIX			= 'phoenix.png'			

# Github-Icons zum Nachladen aus Platzgründen
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'
GIT_CAL			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-calendar.png?raw=true"

# 01.12.2018 	Änderung der BASE_URL von www.ardmediathek.de zu classic.ardmediathek.de
# 06.12.2018 	Änderung der BETA_BASE_URL von  beta.ardmediathek.de zu www.ardmediathek.de
# 03.06.2021	Classic-Version im Web entfallen, Code bereinigt
ARD_BASE_URL	= 'https://www.ardmediathek.de'								# vorher beta.ardmediathek.de
ARD_VERPASST 	= '/tv/sendungVerpasst?tag='								# ergänzt mit 0, 1, 2 usw.
# ARD_AZ 			= 'https://www.ardmediathek.de/ard/shows'				# ARDneu, komplett (#, A-Z)
ARD_AZ 			= '/tv/sendungen-a-z?buchstabe='							# ARD-Classic ergänzt mit 0-9, A, B, usw.
ARD_Suche 		= '/tv/suche?searchText=%s&words=and&source=tv&sort=date'	# Vorgabe UND-Verknüpfung
ARD_Live 		= '/tv/live'


# ARD-Podcasts - 03.06.2021 alle Links der Classic-Version entfernt

# ARD Audiothek
ARD_AUDIO_BASE = 'https://api.ardaudiothek.de/'
AUDIO_HEADERS="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
	'Referer': '%s', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}"
AUDIOSENDER = ['br','dlf','hr','mdr','ndr','"radio-bremen"','rbb','sr','swr','wdr']

# Relaunch der Mediathek beim ZDF ab 28.10.2016: xml-Service abgeschaltet
ZDF_BASE				= 'https://www.zdf.de'
# ZDF_Search_PATH: ganze Sendungen, sortiert nach Datum, bei Bilderserien ohne ganze Sendungen (ZDF_Search)
#	s. ZDF_Search + SearchARDundZDF 
ZDF_SENDUNG_VERPASST 	= 'https://www.zdf.de/sendung-verpasst?airtimeDate=%s'  # Datumformat 2016-10-31
ZDF_SENDUNGEN_AZ		= 'https://www.zdf.de/sendungen-a-z?group=%s'			# group-Format: a,b, ... 0-9: group=0+-+9
ZDF_WISSEN				= 'https://www.zdf.de/doku-wissen'						# Basis für Ermittlung der Rubriken
ZDF_SENDUNGEN_MEIST		= 'https://www.zdf.de/meist-gesehen'
ZDF_BARRIEREARM			= 'https://www.zdf.de/barrierefreiheit-im-zdf'

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

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):					# ADDON_DATA-Verzeichnis anpasen
	PLog('Matrix-Version')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLog("ADDON_DATA: " + ADDON_DATA)


M3U8STORE 		= os.path.join(ADDON_DATA, "m3u8") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
JOBFILE			= os.path.join(ADDON_DATA, "jobliste.xml") 		# Jobliste für epgRecord
MONITOR_ALIVE 	= os.path.join(ADDON_DATA, "monitor_alive") 	# Lebendsignal für JobMonitor
DL_CHECK 		= os.path.join(ADDON_DATA, "dl_check_alive") 	# Anzeige Downloads (Lockdatei)
DL_CNT 			= os.path.join(ADDON_DATA, "dl_cnt") 			# Anzeige Downloads (Zähler)
PLog(SLIDESTORE); PLog(WATCHFILE); 
check 			= check_DataStores()					# Check /Initialisierung / Migration 
PLog('check: ' + str(check))


# die tvtoday-Seiten decken 12 Tage ab, trotzdem EPG-Lauf alle 12 Stunden
#	 (dto. Cachezeit für einz. EPG-Seite in EPG.EPG).
# 26.10.2020 Update der Datei livesenderTV.xml hinzugefügt - s. thread_getepg
if SETTINGS.getSetting('pref_epgpreload') == 'true':		# EPG im Hintergrund laden?
	EPGACTIVE = os.path.join(DICTSTORE, 'EPGActive') 		# Marker thread_getepg aktiv
	EPGCacheTime = 43200									# 12 STd.
	is_activ=False
	if os.path.exists(EPGACTIVE):							# gesetzt in thread_getepg 
		is_activ=True
		now = time.time()
		mtime = os.stat(EPGACTIVE).st_mtime
		diff = int(now) - mtime
		PLog(diff)
		if diff > EPGCacheTime:								# entf. wenn älter als 1 Tag	
			os.remove(EPGACTIVE)
			is_activ=False
	if is_activ == False:									# EPG-Daten veraltet, neu holen
		from threading import Thread
		bg_thread = Thread(target=EPG.thread_getepg, args=(EPGACTIVE, DICTSTORE, PLAYLIST))
		bg_thread.start()
													
if SETTINGS.getSetting('pref_dl_cnt') == 'true':			# laufende Downloads anzeigen
	if os.path.exists(DL_CHECK) == False:					# Lock beachten (Datei dl_check_alive)						
		PLog("Haupt_PRG: get_active_dls")
		from threading import Thread
		bg_thread = Thread(target=epgRecord.get_active_dls, args=())
		bg_thread.start()	
else:
		if os.path.exists(DL_CHECK):	
			os.remove(DL_CHECK)								# Setting Aus: Lock dl_check_alive entfernen
		if os.path.exists(DL_CNT):
			os.remove(DL_CNT)								# Zähler dl_cnt entfernen
				

MERKACTIVE 	= os.path.join(DICTSTORE, 'MerkActive') 		# Marker aktive Merkliste
if os.path.exists(MERKACTIVE):
	os.remove(MERKACTIVE)
MERKFILTER 	= os.path.join(DICTSTORE, 'Merkfilter') 
# Ort FILTER_SET wie filterfile (check_DataStores):
FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
AKT_FILTER	= ''
if os.path.exists(FILTER_SET):	
	AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()					# gesetzte Filter initialiseren 
STARTLIST	= os.path.join(ADDON_DATA, "startlist") 	# Videoliste mit Datum ("Zuletzt gesehen")

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
days = int(SETTINGS.getSetting('pref_TEXTE_store_days'))
ClearUp(TEXTSTORE, days*86400)		# TEXTSTORE bereinigen

if SETTINGS.getSetting('pref_epgRecord') == 'true':
	epgRecord.JobMain(action='init')						# EPG_Record starten

# Skin-Anpassung:
skindir = xbmc.getSkinDir()
PLog("skindir: %s" % skindir)
if 'confluence' in skindir:									# ermöglicht Plot-Infos in Medienansicht
	xbmcplugin.setContent(HANDLE, 'movies')	

ARDSender = ['ARD-Alle:ard::ard-mediathek.png:ARD-Alle']	# Rest in ARD_NEW, CurSenderZDF s. VerpasstWoche
CurSender = ARDSender[0]									# Default ARD-Alle
fname = os.path.join(DICTSTORE, 'CurSender')				# init CurSender (aktueller Sender)
if os.path.exists(fname):									# kann fehlen (Aufruf Merkliste)
	CurSender = Dict('load', "CurSender")					# Übergabe -> ARDnew in Main


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
	title="Suche in ARD und ZDF"
	tagline = 'gesucht wird in ARD  Mediathek Neu und in der ZDF Mediathek.'
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
		fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tagline, 
		fparams=fparams)
		

	title = "ARD Mediathek Neu"
	fparams="&fparams={'name': '%s', 'CurSender': '%s'}" % (title, CurSender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", fanart=R(FANART), 
		thumb=R(ICON_MAIN_ARD), fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_zdfmobile') == 'true':
		PLog('zdfmobile_set: ')
		tagline = 'in den Settings sind ZDF Mediathek und ZDFmobile austauschbar'
		fparams="&fparams={}"
		addDir(li=li, label="ZDFmobile", action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=R(FANART), thumb=R(ICON_MAIN_ZDFMOBILE), tagline=tagline, fparams=fparams)
	else:
		tagline = 'in den Settings sind ZDF Mediathek und ZDFmobile austauschbar'
		fparams="&fparams={'name': 'ZDF Mediathek'}"
		addDir(li=li, label="ZDF Mediathek", action="dirList", dirID="Main_ZDF", fanart=R(FANART), 
			thumb=R(ICON_MAIN_ZDF), tagline=tagline, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_3sat') == 'true':
		tagline = 'in den Settings kann das Modul 3Sat ein- und ausgeschaltet werden'
		fparams="&fparams={'name': '3Sat'}"									# 3Sat-Modul
		addDir(li=li, label="3Sat Mediathek", action="dirList", dirID="resources.lib.my3Sat.Main_3Sat", 
			fanart=R('3sat.png'), thumb=R('3sat.png'), tagline=tagline, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_funk') == 'true':
		tag = 'in den Settings kann das Modul FUNK ein- und ausgeschaltet werden'
		tag = u"%s\n\ndie Beiträge sind auch in der Startseite der ZDF Mediathek enthalten" % tag
		fparams="&fparams={}"													# funk-Modul
		addDir(li=li, label="FUNK", action="dirList", dirID="resources.lib.funk.Main_funk", 
			fanart=R('funk.png'), thumb=R('funk.png'), tagline=tag, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_childprg') == 'true':
		tagline = 'in den Settings kann das Modul Kinderprogramme ein- und ausgeschaltet werden'
		fparams="&fparams={}"													# Kinder-Modul
		addDir(li=li, label="Kinderprogramme", action="dirList", dirID="resources.lib.childs.Main_childs", 
			fanart=R('childs.png'), thumb=R('childs.png'), tagline=tagline, fparams=fparams)
			
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
		tagline = 'in den Settings kann das Modul Arte-Kategorien ein- und ausgeschaltet werden'
		summ = 'Ein komplettes Arte-Addon befindet sich im Kodinerds-Repo (ARTE.TV)'
		fparams="&fparams={}"													# arte-Modul
		addDir(li=li, label="Arte-Kategorien", action="dirList", dirID="resources.lib.arte.Main_arte", 
			fanart=R('icon-arte_kat.png'), thumb=R('icon-arte_kat.png'), tagline=tagline,
			summary=summ, fparams=fparams)
			
	label = 'TV-Livestreams'
	if SETTINGS.getSetting('pref_epgRecord') == 'true':		
		label = 'TV-Livestreams | Sendungen aufnehmen'; 
	tagline = 'TV-Livestreams stehen auch in ARD Mediathek Neu zur Verfügung'																																	
	fparams="&fparams={'title': 'TV-Livestreams'}"
	addDir(li=li, label=label, action="dirList", dirID="SenderLiveListePre", 
		fanart=R(FANART), thumb=R(ICON_MAIN_TVLIVE), tagline=tagline, fparams=fparams)
	
	# 29.09.2019 Umstellung Livestreams auf ARD Audiothek
	#	erneut ab 02.11.2020 nach Wegfall web.ard.de/radio/radionet
	# Button für Livestreams anhängen (eigenes ListItem)		# Radio-Livestreams
	tagline = 'die Radio-Livestreams stehen auch in der neuen ARD Audiothek zur Verfügung'
	title = 'Radio-Livestreams'	
	fparams="&fparams={'title': '%s', 'myhome': 'ARD'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=R(FANART), 
		thumb=R(ICON_MAIN_RADIOLIVE), fparams=fparams)
		
		
	if SETTINGS.getSetting('pref_use_podcast') ==  'true':		# Podcasts / Audiothek
			tagline	= 'ARD Audiothek | Die besten Podcasts der ARD und des Deutschlandradios'
			fparams="&fparams={'title': 'ARD Audiothek'}"
			label = 'ARD Audiothek - NEU'
			addDir(li=li, label=label, action="dirList", dirID="AudioStart", fanart=R(FANART), 
				thumb=R(ICON_MAIN_AUDIO), tagline=tagline, fparams=fparams)
						
																# Download-/Aufnahme-Tools. zeigen
	if SETTINGS.getSetting('pref_use_downloads')=='true' or SETTINGS.getSetting('pref_epgRecord')=='true':	
		tagline = 'Downloads und Aufnahmen: Verschieben, Löschen, Ansehen, Verzeichnisse bearbeiten'
		fparams="&fparams={}"
		addDir(li=li, label='Download- und Aufnahme-Tools', action="dirList", dirID="DownloadTools", 
			fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), tagline=tagline, fparams=fparams)	
				
	if SETTINGS.getSetting('pref_showFavs') ==  'true':			# Favoriten einblenden
		tagline = "Kodi's ARDundZDF-Favoriten zeigen und aufrufen"
		fparams="&fparams={'mode': 'Favs'}"
		addDir(li=li, label='Favoriten', action="dirList", dirID="ShowFavs", 
			fanart=R(FANART), thumb=R(ICON_DIR_FAVORITS), tagline=tagline, fparams=fparams)	
				
	if SETTINGS.getSetting('pref_watchlist') ==  'true':		# Merkliste einblenden
		tagline = 'interne Merkliste des Addons'
		fparams="&fparams={'mode': 'Merk'}"
		addDir(li=li, label='Merkliste', action="dirList", dirID="ShowFavs", 
			fanart=R(FANART), thumb=R(ICON_DIR_WATCH), tagline=tagline, fparams=fparams)		
								
	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if SETTINGS.getSetting('pref_info_update') == 'true': # Updatehinweis beim Start des Addons 
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
			
			if int_lv > int_lc:								# Update-Button "installieren" zeigen
				call_update = True
				title = 'neues Update vorhanden - jetzt installieren'
				summ = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
				# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
				url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
				fparams="&fparams={'url': '%s', 'ver': '%s'}" % (quote_plus(url), latest_version) 
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(FANART), 
					thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summ)
			
	if call_update == False:							# Update-Button "Suche" zeigen	
		title  = 'Addon-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summ='Suche nach neuen Updates starten'
		tag ='Bezugsquelle: ' + repo_url			
		fparams="&fparams={'title': 'Addon-Update'}"
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(FANART), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams, summary=summ, tagline=tagline)

	# Menü Einstellungen (obsolet) ersetzt durch Info-Button
	#	freischalten nach Posting im Kodi-Forum

	tag = 'Infos zu diesem Addon'					# Menü Info + Filter
	summ= u'Ausschluss-Filter (nur für Beiträge von ARD und ZDF)'
	if SETTINGS.getSetting('pref_playlist') == 'true':
		summ = "%s\n\n%s" % (summ, "PLAYLIST-Tools")
	summ = "%s\n\n%s" % (summ, u"Einzelupdate (Dateien und Module)")
	fparams="&fparams={}" 
	addDir(li=li, label='Info', action="dirList", dirID="InfoAndFilter", fanart=R(FANART), thumb=R(ICON_INFO), 
		fparams=fparams, summary=summ, tagline=tag)

	# Updatehinweis wird beim Caching nicht aktualisiert
	if SETTINGS.getSetting('pref_info_update') == 'true':
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	else:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#----------------------------------------------------------------
# Aufruf Main
# div. Addon-Infos + Filter (Titel) setzen/anlegen/löschen
# Filter-Button nur zeigen, wenn in Settings gewählt
def InfoAndFilter():
	PLog('InfoAndFilter:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)									# Home-Button

															# Button changelog.txt
	tag= u'Störungsmeldungen bitte via Kodinerds-Forum, Github-Issue oder rols1@gmx.de'
	summ = u'für weitere Infos zu bisherigen Änderungen [B](changelog.txt)[/B] klicken'
	path = os.path.join(ADDON_PATH, "changelog.txt") 
	title = "Änderungsliste [B](changelog.txt)[/B]"
	title=py2_encode(title)
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ShowText", fanart=R(FANART), 
		thumb=R(ICON_TOOLS), fparams=fparams, summary=summ, tagline=tag)		
							
	title = u"Addon-Infos"									# Button für Addon-Infos
	tag = "Infos zu Version, Cache und Dateipfaden." 
	summ = "Bei aktiviertem Debug-Log erfolgt die Ausgabe auch dort"
	summ = "%s (nützlich zum Kopieren der Pfade)." % summ
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="AddonInfos", fanart=R(FANART), 
		thumb=R(ICON_PREFS), tagline=tag, summary=summ, fparams=fparams)	
			
	if SETTINGS.getSetting('pref_startlist') == 'true':		# Button für LastSeen-Funktion
		maxvideos = SETTINGS.getSetting('pref_max_videos_startlist')
		title = u"Zuletzt gesehen"	
		tag = u"Liste der im Addon gestarteten Videos (max. %s Einträge)." % maxvideos
		tag = u"%s\n\nSortierung absteigende (zuletzt gestartete Videos zuerst)" % tag
		summ = u"Klick startet das Video (falls noch existent)"
		fparams="&fparams={}" 
		addDir(li=li, label=title, action="dirList", dirID="AddonStartlist", fanart=R(FANART), 
			thumb=R("icon-list.png"), tagline=tag, summary=summ, fparams=fparams)	
		
	if SETTINGS.getSetting('pref_usefilter') == 'true':											
		title = u"Filter bearbeiten "						# Button für Filter
		tag = "Ausschluss-Filter bearbeiten (nur für Beiträge von ARD und ZDF)" 
		fparams="&fparams={}" 
		addDir(li=li, label=title, action="dirList", dirID="FilterTools", fanart=R(FANART), 
			thumb=R(ICON_FILTER), tagline=tag, fparams=fparams)		

	# Problem beim Abspielen der Liste - s. PlayMonitor (Modul playlist)
	if SETTINGS.getSetting('pref_playlist') == 'true':
		MENU_STOP = os.path.join(ADDON_DATA, "menu_stop") 	# Stopsignal für Tools-Menü (Haupt-PRG)								
		if os.path.exists(MENU_STOP):						# verhindert Rekurs. in start_script 
			os.remove(MENU_STOP)							# Entfernung in playlist_tools
			
		title = u"PLAYLIST-Tools"							# Button für PLAYLIST-Tools
		myfunc="resources.lib.playlist.playlist_tools"
		fparams_add = quote('{"action": "playlist_add", "url": "", "menu_stop": "true"}') # hier json-kompat.
		
		tag = u"Abspielen und Verwaltung der addon-internen Playlist"
		tag = u"%s\n\nEinträge werden via Kontextmenü in den Einzelauflösungen eines Videos hinzugefügt." % tag
		tag = u"%s\n\n[COLOR blue]Am besten eigenen sich MP4-Url's[/COLOR]. HLS-Url's starten immer am Anfang, " % tag
		tag = u"%sunabhängig von der letzten Position. Livestreams werden abgewiesen." % tag			
		summ = u"die PLAYLIST-Tools stehen auch im Kontextmenü zur Verfügung, wenn ein Listeneintrag eine geeignete Stream-Url enthält" 
		fparams="&fparams={'myfunc': '%s', 'fparams_add': '%s'}"  %\
			(quote(myfunc), quote(fparams_add))
			
		addDir(li=li, label=title, action="dirList", dirID="start_script",\
			fanart=R(FANART), thumb=R("icon-playlist.png"), tagline=tag, summary=summ, fparams=fparams)	
			
	title = u"Einzelupdate (Dateien und Module)"		# Update von Einzeldateien
	tag = 'Update einzelner, neuer Bestandteile des Addons vom Github-Repo %s' % REPO_NAME
	tag = "%s\n\nNach Abgleich werden neue Dateien heruntergeladen und ersetzen lokale Dateien im Addon." % tag
	summ = "Anstehende Einzelupdates werden im Forum kodinerds im Startpost des Addons angezeigt."
	fparams="&fparams={'PluginAbsPath': '%s'}" % PluginAbsPath
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.EPG.update_single",\
		fanart=R(FANART), thumb=R("icon-update-einzeln.png"), tagline=tag, summary=summ, fparams=fparams)	
		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#---------------------------------------------------------------- 
# Wg.  Problemen mit der xbmc-Funktion executebuiltin(RunScript()) verwenden
#	wir importlib wie in router()
#	Bsp. myfunc: "resources.lib.playlist.items_add_rm" (relatv. Modulpfad + Zielfunktion)
#	fparams_add json-kompat., Bsp.: '{"action": "playlist_add", "url": ""}'
# Um die Rekursion der Web-Tools-Liste zu vermeiden wird MENU_STOP in playlist_tools
#	gesetzt und in InfoAndFilter wieder entfernt.
#  
def start_script(myfunc, fparams_add):
	PLog("start_script:")
	import importlib
	fparams_add = unquote(fparams_add)
	PLog(myfunc); PLog(fparams_add)
	
	l = myfunc.split('.')									# Bsp. resources.lib.updater.update
	PLog(l)
	newfunc =  l[-1:][0]									# Bsp. updater
	dest_modul = '.'.join(l[:-1])

	dest_modul = importlib.import_module(dest_modul )		# Modul laden
	PLog('loaded: ' + str(dest_modul))
	func = getattr(dest_modul, newfunc)	

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
#
def AddonStartlist(mode='', query=''):
	PLog('AddonStartlist:');
	PLog(mode); PLog(query)
	maxvideos = SETTINGS.getSetting('pref_max_videos_startlist')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)										# Home-Button
	img = R("icon-list.png")
	startlist=''

	if os.path.exists(STARTLIST):
		startlist= RLoad(STARTLIST, abs_path=True)				# Zuletzt gesehen-Liste ergänzen
	if startlist == '':
		msg1 = u'die "Zuletzt gesehen"-Liste ist leer'
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

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
			
	startlist=py2_encode(startlist)
	startlist= startlist.strip().splitlines()
	PLog(len(startlist))

	cnt=0
	for item in startlist:
		Plot=''
		ts, title, url, thumb, Plot = item.split('###')
		ts = datetime.datetime.fromtimestamp(float(ts))
		ts = ts.strftime("%d.%m.%Y %H:%M:%S")
		Plot_par = "gestartet: [COLOR darkgoldenrod]%s[/COLOR]\n\n%s" % (ts, Plot)
		Plot_par=py2_encode(Plot_par); 		
		Plot_par=Plot_par.replace('\n', '||')					# für router
		tag=Plot_par.replace('||', '\n')
		
		PLog("Satz16:"); PLog(title); PLog(ts); PLog(url); PLog(Plot_par)	
		show = True
		if 	query:												# Suchergebnis anwenden
			q = up_low(query, mode='low'); i = up_low(item, mode='low');
			PLog(q in i)
			show = q in i										# Abgleich 
		
		PLog(show)		
		if show == True:		
			url=py2_encode(url); title=py2_encode(title);  thumb=py2_encode(thumb);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
				(quote_plus(url), quote_plus(title), quote_plus(thumb), quote_plus(Plot_par))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=thumb, 
				fparams=fparams, mediatype='video', tagline=tag)
			cnt = cnt+1 	
	
	PLog(cnt);
	if query:
		if cnt == 0:
			msg1 = u"Suchwort >%s< leider nicht gefunden" % py2_decode(query)
			MyDialog(msg1, '', '')	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# Menüs für FilterToolsWork 
def FilterTools():
	PLog('FilterTools:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
		
	filterfile = os.path.join(ADDON_DATA, "filter.txt") 		# init: check_DataStores
	filter_page = RLoad(filterfile, abs_path=True)				# Filterliste laden

	if filter_page == '' or len(filter_page) <= 20:
		msg1 = "Problem Filterliste"
		msg2 = 'Liste kann nicht geladen werden'				# -> nur Button Hinzufügen
		PLog(msg2); PLog(filter_page)
		filter_page=''											# fehlerhaft=leer
		icon = R(ICON_FILTER)
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		
	akt_filter=''; 
	if os.path.isfile(FILTER_SET):
		page = RLoad(FILTER_SET, abs_path=True)
		page = page.strip()
		akt_filter = page.splitlines()
	PLog(akt_filter)
												
	summ = u"Ausschluss-Filter für Beiträge von ARD und ZDF."
	summ = u"%s\n\nWirkung: Einzelbeiträge, die einen gesetzten Filter in Titel, Subtitel oder Beschreibung enthalten, werden aussortiert." % summ 
	
	if filter_page:
		if akt_filter:
			title = u"aktuell gesetzte(n) Filter zeigen (%d)" %  len(akt_filter)
			fparams="&fparams={'action': 'show_set'}" 
			addDir(li=li, label=title, action="dirList", dirID="FilterToolsWork", fanart=R(FANART), 
				thumb=R(ICON_FILTER), summary=summ, fparams=fparams)		

		title = u"alle Filterwörter zeigen" 
		fparams="&fparams={'action': 'show_list'}" 
		addDir(li=li, label=title, action="dirList", dirID="FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), summary=summ, fparams=fparams)				
	
		title = u"Filter [COLOR blue]setzen (aktuell: %d)[/COLOR]" % len(akt_filter)
		tag = u"ein oder mehrere Filterworte [COLOR blue]setzen[/COLOR]" 
		fparams="&fparams={'action': 'set'}" 
		addDir(li=li, label=title, action="dirList", dirID="FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)
					
		title = u"Filterwort [COLOR red]löschen[/COLOR]"
		tag = u"ein Filterwort aus der Ausschluss-Liste [COLOR red]löschen[/COLOR]" 
		fparams="&fparams={'action': 'delete'}" 
		addDir(li=li, label=title, action="dirList", dirID="FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)		
		
	title = u"Filterwort [COLOR green]hinzufügen[/COLOR]"
	tag = u"ein Filterwort der Ausschluss-Liste [COLOR green]hinzufügen[/COLOR]" 
	fparams="&fparams={'action': 'add'}" 
	addDir(li=li, label=title, action="dirList", dirID="FilterToolsWork", fanart=R(FANART), 
		thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#----------------------------------------------------------------
# Aufruf FilterTools
# Ausschluss-Filter Anzeigen/Setzen/Hinzufügen/Löschen
# 13.05.2020 'Container.Refresh' muss für LibreElec + Android vor 
#	notification erfolgen und cacheToDisc=False - sonst wirkungslos.
#
def FilterToolsWork(action):
	PLog('FilterToolsWork: ' + action) 
	dialog = xbmcgui.Dialog()

	filter_pat = "<filter>\n%s\n</filter>\n" 					# Rahmen Filterliste
	filterfile = os.path.join(ADDON_DATA, "filter.txt")			# init: check_DataStores
	page = RLoad(filterfile, abs_path=True)						# Filterliste laden
	filter_list = stringextract('<filter>', '</filter>', page)
	filter_list = filter_list.splitlines()
	filter_list.remove('')										# aus ev. Leerz.
	filter_list=sorted(filter_list, key=str.lower)
	PLog(filter_list)
	
	page = RLoad(FILTER_SET, abs_path=True)						# akt. Filter laden
	akt_filter = page.splitlines()
	akt_filter=sorted(akt_filter, key=str.lower)
	PLog(akt_filter)	

	if action == 'show_set':									# gesetzte Filter zeigen
		title = u"aktuell gesetzte(r) Filter"
		akt_filter = "\n".join(akt_filter)
		dialog.textviewer(title, akt_filter,usemono=True)
			
	if action == 'set':
		index_list = get_list_indices(akt_filter, filter_list)	# akt. Filter-Indices ermitteln
		PLog(index_list); 
		title = u"Filter setzen (grün: gesetzt)"
		ret = dialog.multiselect(title, filter_list, preselect=index_list)
		PLog(ret)												# ret hier Liste
		if ret !=  None:										# None bei Abbruch
			if len(ret) > 0:
				items = get_items_from_list(ret, filter_list)	# Indices -> Filter-items
				items = "\n".join(items) 
			else:
				items = ''
			RSave(FILTER_SET, items)
			msg1 = u"Filter setzen"
			msg2 = u"gesetzte Filter: %d" % len(ret)
			icon = R(ICON_FILTER)
			xbmc.executebuiltin('Container.Refresh')
			xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		
	if action == 'add':
		title = u'Filterwort hinzufügen (Groß/klein egal)'
		ret = dialog.input(title, type=xbmcgui.INPUT_ALPHANUM)	# Eingabe Filterwort
		PLog(ret)
		if ret:
			ret = py2_encode(up_low(ret, mode='low'))
			if ret in filter_list:								# Check: vorhanden?
				msg1 = "Filterliste"
				msg2 = '%s existiert schon. Anzahl: %d' % (ret.strip(), len(filter_list))		
				icon = R(ICON_FILTER)
				xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
			else:	
				filter_list.append(ret.strip())					# Filterwort hinzufügen
				if '' in filter_list:
					filter_list.remove('')						# aus ev. Leerz.
				items = "\n".join(filter_list)
				items = py2_encode(items)
				filter_pat = filter_pat % items					# Filter -> xml-Rahmen
				PLog(filter_pat)
				err_msg = RSave(filterfile, filter_pat)			# speichern
				if err_msg:
					msg1 = "Fehler beim Speichern der Filterliste" 
					PLog(msg1)	
					MyDialog(msg1, '', '')
				else:
					msg1 = "Filterliste"
					msg2 = '%s hinzugefügt. Anzahl: %d' % (ret.strip(), len(filter_list))		
					icon = R(ICON_FILTER)
					xbmc.executebuiltin('Container.Refresh')					
					xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
	
	if action == 'delete':
		title = u"Filterwort löschen (ev. gesetzter Filter wird mitgelöscht)"
		ret = dialog.select(title, filter_list)					# Auswahl Filterliste
		PLog(ret)
		if ret >= 0:
			ret = filter_list[ret]								# Index -> item
			item = py2_encode(ret)
			PLog(item)
			is_filter=False;
			if item in akt_filter:								# auch gesetzter Filter?
				is_filter=True
			msg2 = "[COLOR red]%s[/COLOR] ist kein gesetzter Filter." % ret
			if is_filter:	
				msg2 = "gesetzter Filter [COLOR red]%s[/COLOR] wird mitgelöscht" % ret
			msg1 = "Filterwort [COLOR red]%s[/COLOR] wirklich löschen?" % ret 

			ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
			PLog(ret)
			if ret == 1:
				filter_list.remove(item)						# Filterwort entfernen
				filter_len = len(filter_list)
				items = "\n".join(filter_list)
				items = py2_encode(items)
				filter_pat = filter_pat % items					# Filter -> xml-Rahmen
				PLog(filter_pat)
				err_msg1 = RSave(filterfile, filter_pat)			# speichern
				if is_filter:
					akt_filter.remove(item)
					items = "\n".join(akt_filter)
					err_msg2 = RSave(FILTER_SET, items)	

				if err_msg1 or err_msg2:
					if err_msg1:
						msg1 = "Fehler beim Speichern der Filterliste" 
						PLog(msg1)	
						MyDialog(msg1, '', '')
					if err_msg2:
						msg1 = "Fehler beim Speichern der aktuell gesetzten Filter" 
						PLog(msg1)	
						MyDialog(msg1, '', '')
				else:
					msg1 = "Filterliste"
					msg2 = u'%s gelöscht. Anzahl: %d' % (item, filter_len)		
					icon = R(ICON_FILTER)
					xbmc.executebuiltin('Container.Refresh')					
					xbmcgui.Dialog().notification(msg1,msg2,icon,5000)		
			
	if action == 'show_list':									# Filterliste zeigen
		title = u"Liste verfügbarer Filter"
		filter_list = "\n".join(filter_list)
		dialog.textviewer(title, filter_list,usemono=True)
		
	if action == 'state_change':								# aus Kontextmenü
		if SETTINGS.getSetting('pref_usefilter') == 'true':
			SETTINGS.setSetting('pref_usefilter','false')
		else:											
			SETTINGS.setSetting('pref_usefilter','true')
		xbmc.executebuiltin('Container.Refresh')							

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
	a1 = u"%s %10s Dict (Variablen, Objekte)" %  (t, get_dir_size(DICTSTORE))
	a2 = u"%s %10s Inhaltstexte (im Voraus geladen)" %  (t, get_dir_size(TEXTSTORE))
	a3 = u"%s %10s m3u8 (Einzelauflösungen der Livestreams)" %  (t, get_dir_size(M3U8STORE))
	a4 = u"%s %10s Slides (Bilder)" %   (t, get_dir_size(SLIDESTORE))
	a5 = u"%s %10s subtitles (Untertitel)" %   (t, get_dir_size(SUBTITLESTORE))
	a6 = ''
	path = SETTINGS.getSetting('pref_download_path')
	PLog(path); PLog(os.path.isdir(path))
	if path and os.path.isdir(path):
		a6 = "%s %10s Downloads\n" %   (t, get_dir_size(path))
	p2 = u"%s\n%s\n%s\n%s\n%s\n%s\n%s" % (a,a1,a2,a3,a4,a5,a6)

	a = u"[COLOR red]Pfade:[/COLOR]"
	a1 = u"%s Addon-Home: %s" % (t, PluginAbsPath)
	a2 = u"%s Cache: %s" % (t,ADDON_DATA)
	fname = WATCHFILE
	a3 = u"%s Merkliste intern: %s" % (t, WATCHFILE)
	a4 = u"%s Merkliste extern: nicht aktiviert" % t
	if SETTINGS.getSetting('pref_merkextern') == 'true':	# externe Merkliste gewählt?
		fname = SETTINGS.getSetting('pref_MerkDest_path')
		a4 = u"%s Merkliste extern: %s" % (t,fname)
	a5 = u"%s Downloadverzeichnis: %s" % (t,SETTINGS.getSetting('pref_download_path'))
	a6 = u"%s Verschiebeverzeichnis: %s" % (t,SETTINGS.getSetting('pref_VideoDest_path'))
	filterfile = os.path.join(ADDON_DATA, "filter.txt")
	a7 = u"%s Filterliste: %s" %  (t,filterfile)
	fname =  SETTINGS.getSetting('pref_podcast_favorits')
	if os.path.isfile(fname) == False:
		fname = os.path.join(PluginAbsPath, "resources", "podcast-favorits.txt") 
	a8 = u"%s Podcast-Favoriten:\n%s%s" %  (t,t,fname)		# fname in 2. Zeile
	log = xbmc.translatePath("special://logpath")
	log = os.path.join(log, "kodi.log") 	
	a9 = u"%s Debug-Log: %s" %  (t, log)
	a10 = u"%s TV-und Event-Livestreams: %s/%s" % (t, PluginAbsPath, "resources/livesenderTV.xml")
	
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
	PLog(page)
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
def Main_ZDF(name):
	PLog('Main_ZDF:'); PLog(name)
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	title="Suche in ZDF-Mediathek"
	fparams="&fparams={'query': '', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
		thumb=R(ICON_ZDF_SEARCH), fparams=fparams)

	title = 'Startseite' 
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ZDFStart", fanart=R(ICON_MAIN_ZDF), thumb=R(ICON_MAIN_ZDF), 
		fparams=fparams)

	title = 'ZDF-funk' 
	fparams="&fparams={'title': '%s'}" % (quote(title))
	addDir(li=li, label=title, action="dirList", dirID="Main_ZDFfunk", fanart=R(ICON_MAIN_ZDF), thumb=R('zdf-funk.png'), 
		fparams=fparams)

	fparams="&fparams={'name': 'ZDF-Mediathek', 'title': 'Sendung verpasst'}" 
	addDir(li=li, label='Sendung verpasst', action="dirList", dirID="VerpasstWoche", fanart=R(ICON_ZDF_VERP), 
		thumb=R(ICON_ZDF_VERP), fparams=fparams)	

	fparams="&fparams={'name': 'Sendungen A-Z'}"
	addDir(li=li, label="Sendungen A-Z", action="dirList", dirID="ZDFSendungenAZ", fanart=R(ICON_ZDF_AZ), 
		thumb=R(ICON_ZDF_AZ), fparams=fparams)

	fparams="&fparams={'name': 'Rubriken'}"
	addDir(li=li, label="Rubriken", action="dirList", dirID="ZDFRubriken", fanart=R(ICON_ZDF_RUBRIKEN), 
		thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)

	fparams="&fparams={'name': 'Meist gesehen'}"
	addDir(li=li, label="Meist gesehen (1 Woche)", action="dirList", dirID="MeistGesehen", 
		fanart=R(ICON_ZDF_MEIST), thumb=R(ICON_ZDF_MEIST), fparams=fparams)

	title = "ZDF-sportstudio"
	path = "https://www.zdf.de/sport"
	tag = "	Aktuelle News, Livestreams, Liveticker, Ergebnisse, Hintergründe und Sportdokus. Sportstudio verpasst? Aktuelle Sendungen einfach online schauen!"
	fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ZDFRubrikSingle", fanart=R("zdf-sport.png"), 
		thumb=R("zdf-sport.png"), tagline=tag, fparams=fparams)
		
	fparams="&fparams={'title': 'Barrierearm'}"	
	addDir(li=li, label="Barrierearm", action="dirList", dirID="BarriereArm", fanart=R(ICON_ZDF_BARRIEREARM), 
		thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)

	fparams="&fparams={'title': 'ZDFinternational'}"
	tag = "This channel provides selected videos in English, Spanish or Arabic or with respective subtitles."
	summ = 'For Arabic, please set the font of your Skin to "Arial based".'
	addDir(li=li, label="ZDFinternational", action="dirList", dirID="International", fanart=R('ZDFinternational.png'), 
		thumb=R('ZDFinternational.png'), tagline=tag, summary=summ, fparams=fparams)

	fparams="&fparams={'s_type': 'Bilderserien', 'title': 'Bilderserien', 'query': 'Bilderserien'}"
	addDir(li=li, label="Bilderserien", action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_BILDERSERIEN), 
		thumb=R(ICON_ZDF_BILDERSERIEN), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
def Main_ZDFfunk(title):
	PLog('Main_ZDFfunk:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	title = 'ZDF-funk-Startseite' 
	path = "https://www.zdf.de/funk"
	fparams="&fparams={'title': '%s', 'path': '%s'}" % (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="ZDFStart", fanart=R('zdf-funk.png'), thumb=R('zdf-funk.png'), 
		fparams=fparams)

	fparams="&fparams={'name': 'ZDF-funk-A-Z', 'ID': 'ZDFfunk'}"
	addDir(li=li, label="ZDF-funk-A-Z", action="dirList", dirID="ZDFSendungenAZ", fanart=R('zdf-funk-AZ.png'), 
		thumb=R('zdf-funk-AZ.png'), fparams=fparams)

	fparams="&fparams={}"											# Button funk-Modul hinzufügen
	addDir(li=li, label="zum FUNK-Modul", action="dirList", dirID="resources.lib.funk.Main_funk", 
		fanart=R('zdf-funk.png'), thumb=R('funk.png'), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
##################################### Start Audiothek ###############################################
# Aufruf: Main
# 24.07.2021 Revision nach Renovierung der Audiothek durch die ARD
#	(umgestellt auf java-Script, Auswertung des html-Codes nicht 
#	nehr möglich). Nutzung des API durch das Addon (Inhalte im json-
#	Format)
#
def AudioStart(title):
	PLog('AudioStart:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)						# Home-Button

	path = ARD_AUDIO_BASE					
	page, msg = get_page(path=path)
	if page == '':	
		msg1 = "Fehler in AudioStart:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
					
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
	title_list = [u'Entdecken|ard-entdecken.png', u'Unsere Favoriten|ard-favoriten.png', 
			u'Themen|ard-themen.png', u'Meistgehörte Episoden|ard-meistgehoert.png',
			u'Ausgewählte Podcasts|ard-ausgewaehlt.png', u'Rubriken|ard-rubriken.png',
			u'Sport|ard-sport.png']								
	for item in title_list:
		title, img = item.split('|')
		tag=''
		if title == u"Entdecken":
			tag = "die Highlights  der Audiothek"
		if title == u"Sport":
			tag = "Achtung: Livestreams nicht aufnehmen. Stop im Addon nicht möglich!"
		fparams="&fparams={'title': '%s', 'ID': '%s'}" % (title, title)	
		addDir(li=li, label=title, action="dirList", dirID="AudioStartHome", fanart=R(ICON_MAIN_AUDIO), 
			thumb=R(img), tagline=tag, fparams=fparams)

	# Button für A-Z anhängen 									# A-Z alle Sender
	# 01.08.2021 nach Renovierung der Audiothek durch die ARD entfallen
	
	# Button für Sender anhängen 								# Sender/Sendungen (via AudioStartLive)
	title = 'Sender (Sendungen einzelner Radiosender)'
	fparams="&fparams={'title': '%s', 'programs': 'yes'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R("ard-sender.png"), fparams=fparams)
	
	# Button für funk anhängen 									# funk
	title = 'FUNK-Podcasts - Pop und Szene'
	fparams="&fparams={'url': ''}" 	
	addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik_funk", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R('funk.png'), fparams=fparams)
	
	# Button für Podcast-Favoriten anhängen 					# Podcast-Favoriten
	title="Podcast-Favoriten"; 
	tagline = u'konfigurierbar mit der Datei podcast-favorits.txt im Addon-Verzeichnis resources'
	summ = u'Suchergebnisse der Audiothek lassen sich hinzufügen\n'
	summ = u"%s\nMehrfach-Downloads (komplette Liste) möglich" % summ
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="PodFavoritenListe", fanart=R(ICON_MAIN_POD), 
		thumb=R(ICON_POD_FAVORITEN), tagline=tagline, summary=summ, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# 31.07.2021 Revision nach Renovierung der Audiothek durch die ARD
#
def AudioStartHome(title, ID, page='', path=''):	# Auswertung Homepage	
	PLog('AudioStartHome: ' + ID)
	li = xbmcgui.ListItem()
	
	ID = py2_decode(ID)
	if ID == 'Entdecken':							# Stage Web, Sonderbhdl., Beiträge nicht im api 		
		Audio_get_cluster_stage()					# direkt
		return
	if ID == 'Rubriken':							# Rubriken: eig. api-Call
		path = ARD_AUDIO_BASE + "editorialcategories"
	elif ID == 'Sport':								# Menü: Rubrik Sport 
		# path = 'https://www.ardaudiothek.de/suche/Sport' 			# Web-Suche
		path = 'https://www.ardaudiothek.de/rubrik/sport/42914734'	# 08.08.2021 (Rubrik umfangreicher)
	else:
		path = ARD_AUDIO_BASE + "homescreen"		# Kat's der Leitseite
		
	page=''									
	if 	ID == 'Sport':								# Permanent Redirect - s.a. Audio_get_cluster_rubrik
		page, msg = get_page(path=path, GetOnlyRedirect=True)	
		url = page								
		page, msg = get_page(path=url)			
	else:	
		page, msg = get_page(path=path)	
		if page == '':	
			msg1 = "Fehler in AudioStartHome:"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
	PLog(len(page))	
		
	li = home(li, ID='ARD Audiothek')				# Home-Button
		
	if ID == u'Meistgehörte Episoden':							
		Audio_get_json_single(li, page, ID)			# einz. Beiträge
	if ID == u'Unsere Favoriten' or ID == u'Themen' or ID == u'Ausgewählte Podcasts':
		Audio_get_json_multi(li, page, ID)			# mehrf. Beiträge
	if ID == u'Sport':
		Audio_get_cluster_rubrik(li, path, title, ID)
	if ID == u'Rubriken':							# Rubrik Sport direkt
		ID = "AudioStartHome"
		Audio_get_rubriken_web(li, title, path, ID, page)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# 1. Aufruf: (ID=AudioStartHome) -> Liste der Rubriken via api,
#	Ablage mit den passenden Webadressen im Dict 
# 2. Aufruf (Rubrik-Webseite in path) -> Audio_get_cluster_rubrik
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
		Obs = jsonObject["_embedded"]['mt:editorialCategories']
		PLog(len(Obs))
		base = "https://www.ardaudiothek.de/rubrik/%s"				# Name im Pfad ../wissen/..  nicht nötig
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
# 24.07.2021 Anpassung an renovierte Audiothek
# 	einschl.Event Streams
# Aufrufer: Main, AudioStart - Param. programs  steuert Unterscheidung
#	Livestreams / PRG-Sets
# 20.10.2021 zusätzl. Auswertung der Org. ohne Livesender (ARD, funk 
#	usw.)
#
def AudioStartLive(title, sender='', streamUrl='', myhome='', programs='', img='', Plot=''): # Sender / Livestreams 
	PLog('AudioStartLive: ' + sender)
	PLog(programs)
	CacheTime = 6000													# 1 Std.

	li = xbmcgui.ListItem()
	if myhome:
		li = home(li, ID=myhome)
	else:	
		li = home(li, ID='ARD Audiothek')								# Home-Button

	path = "https://api.ardaudiothek.de/organizations"			
	page = Dict("load", "AudioSender", CacheTime=CacheTime)
	if page == False or page == '':										# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path, JsonPage=True)
		Dict("store", "AudioSender", page)
	msg1 = "Fehler in AudioStartLive:"
	if page == '':	
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li

	#pubObjekts = blockextract('"brandingColor":"', page)				# Sender-Icon außerhalb
	pubObjekts = blockextract('"name":"publicationService"', page)		# Station: Livestreams + PRG
	PLog(len(pubObjekts))
	if sender == '':
		for pubObjekt in pubObjekts:
			orgname = stringextract('"organizationName":"', '"', pubObjekt)	# Sender, z.B BR
			LiveObj = stringextract('mt:liveStreams', 'mt:programSets', pubObjekt)
			live_cnt = stringextract('numberOfElements":', '},', LiveObj)	
			title = stringextract('"title":"', '"', pubObjekt)	
			PLog("orgname: %s, title: %s" % (orgname,title))
			img = stringextract('"mt:image"', 'ratio', pubObjekt)
			img = stringextract('"href":"', '{', img)					# ../46/555337067/{ratio}/{width}?
			img = img + "1x1/640?mandant=ard"
			Plot = stringextract('"synopsis":"', '"', pubObjekt)
			Plot = repl_json_chars(Plot)
			sender = title
			
			if programs == 'yes':										# Info-Text anpassen
				add = "zu den Programmen"
			else:
				add = "zum Livestream"
			tag = "Weiter %s von: [B]%s[/B]" % (add, title)
			
			if live_cnt != '0':											# Livestreams enthalten
				streamUrl = stringextract('"streamUrl":"', '"', pubObjekt)							
			else:
				streamUrl=''
				cnt_max = stringextract('"numberOfElements":', ',', pubObjekt)
				PLog("cnt_max: " + cnt_max)	
				if programs == '':										# Livestreams gefordert, nicht enth.
					continue			
				
			PLog('3Satz:');
			PLog(title); PLog(img); PLog(streamUrl); PLog(Plot);
			title=py2_encode(title); sender=py2_encode(sender);
			streamUrl=py2_encode(streamUrl); img=py2_encode(img)
			Plot=py2_encode(Plot)
			fparams="&fparams={'title': '%s', 'sender': '%s', 'streamUrl': '%s', 'myhome': '%s', 'programs': '%s', 'img': '%s', 'Plot': '%s'}" %\
				(quote(title), quote(sender), quote(streamUrl), myhome, programs,
				quote(img), quote(Plot))	
			addDir(li=li, label=sender, action="dirList", dirID="AudioStartLive", fanart=img, 
				thumb=img, tagline=tag, summary=Plot, fparams=fparams)


	#-------------------------		
		if programs == '':
			ARDAudioEventStreams(li)									# externe Zusätze listen

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	#-------------------------------------------------------------------
	
	else:																# 2. Durchlauf: einz. Sender
		if programs == '':
			if streamUrl:												# zum Livestream
				PlayAudio(streamUrl, title, img, Plot)  # direkt	
		else:															# Sendungen der Sender listen
			AudioSenderPrograms(li, page, sender, img)
	return		
#----------------------------------------------------------------
# Buttons ARD Audio Event Streams, Bundesliga ARD-Hörfunk,
#	 Sportschau Livestreams, Liste Netcast-Audiostreams
# Audio-Calls:
#	ARDSportAudioXML -> 	SenderLiveResolution		-> PlayAudio
#	ARDSportHoerfunk ->  	ARDSportAudioStreamsSingle 	-> PlayAudio
#	ARDSportAudioStreams ->	ARDSportAudioStreamsSingle 	-> PlayAudio
def ARDAudioEventStreams(li):
	PLog('ARDAudioEventStreams:')
	
	channel = u'ARD Audio Event Streams'								# aus livesenderTV.xml								
	title = u"[B]Audio:[/B] ARD Audio Event Streams"					# div. Events, z.Z. Fußball EM2020   
	img = R("radio-livestreams.png")
	tag = u'Reportagen von Events, z.B. Fußball EM2020' 
	img=py2_encode(img); channel=py2_encode(channel); title=py2_encode(title);
	fparams="&fparams={'channel': '%s'}"	% (quote(channel))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioXML", fanart=img, 
		thumb=img, tagline=tag, fparams=fparams)

	title = u"[B]Audio:[/B] Die Fussball-Bundesliga im ARD-Hörfunk"		# Button Bundesliga ARD-Hörfunk 
	href = 'https://www.sportschau.de/sportimradio/bundesligaimradio102.html'
	img = R("tv-ard-sportschau.png")							
	tag = u'An Spieltagen der Fußball-Bundesliga übertragen die Landesrundanstalten ' 
	tag = tag + u'im ARD-Hörfunk die Spiele live aus dem Stadion mit der berühmten ARD-Schlusskonferenz.'
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportHoerfunk", fanart=img, 
		thumb=img, tagline=tag, fparams=fparams)
							
	title = u"[B]Audio:[/B] aktuelle Livestreams (sportschau.de)"		# Button aktuelle LIVESTREAMS
	href = 'https://www.sportschau.de/audio/index.html'
	img = R("tv-ard-sportschau.png")								
	tag = u'aktuelle Livestreams der ARD Sportschau.' 
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s',  'ID': 'SportschauStreams'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioStreams", fanart=img, 
		thumb=img, tagline=tag, fparams=fparams)
							
	title = u"[B]Audio:[/B] alle Netcast-Audiostreams (sportschau.de)"	# Button Netcast-Audiostreams-Liste
	href = 'https://www.sportschau.de/sportimradio/audiostream-netcast-uebersicht-100.html'
	img = R("tv-ard-sportschau.png")								
	tag = u'Die Übersicht aller Netcast-Audiostreams für die Bundesliga-Übertragungen.' 
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s',  'ID': 'NetcastStreams'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioStreams", fanart=img, 
		thumb=img, tagline=tag, fparams=fparams)
		
	return
	
#----------------------------------------------------------------
# hier wird der Streamlink von der Website der Audiothek im json-Teil ermitelt.
# 	startet einzelnen Livestream für AudioStartLive
# AudioLiveSingle nach Renovierung Audiothek entfernt
# def AudioLiveSingle(url, title, thumb, Plot):		
	
#----------------------------------------------------------------
# listet Sendungen einzelner Radiosender
#	Sendungen sind bereits alph. sortiert
#	Auswertung Sendung -> Audio_get_sendung
# 28.07.2021 Anpassung an renovierte Audiothek
# 20.10.2021 zusätzl. Auswertung der Org. ohne Livesender (ARD, funk 
#	usw.) - Block organizationName statt sender 
# 
def AudioSenderPrograms(li, page, sender, img):
	PLog('AudioSenderPrograms:')
	sender = up_low(sender); 
	PLog(sender)
	base = "https://api.ardaudiothek.de/"			

	pubObjekts = blockextract('"brandingColor":"', page)				# Station: Livestreams + PRG
	PLog(len(pubObjekts))
	for pubObjekt in pubObjekts:
		orgname = stringextract('"organizationName":"', '"', pubObjekt)	# Sender, z.B BR
		PLog("orgname: " + orgname)

		titles = blockextract('"organizationName":"', pubObjekt, ",")	
		found=False
		for title in titles:
			title = stringextract('"organizationName":"', '"', pubObjekt)	
			title2 = stringextract('"title":"', '"', pubObjekt)	
			title = up_low(title); title2 = up_low(title2)
			PLog("sender: %s, title: %s" % (sender,title))			
			if title == sender or title2 == sender:
				found=True
				PLog("found_sender: %s bzw. %s" % (title, title2))
				break
		if found:
			break
		
	if found:			
		cnt_max = stringextract('"numberOfElements":', ',', pubObjekt)
		PLog("cnt_max: " + cnt_max)	
		pos = pubObjekt.find('mt:programSets')		
		SenderSets = pubObjekt[pos:]
		SenderSets = SenderSets.replace('\\"', '*')
		SenderSets = blockextract('"href":"./programsets/', SenderSets)	# 1. Link enth. PRG-ID
		PLog(len(SenderSets))
		cnt=0
		for prgSet in SenderSets:
			# PLog(prgSet[80:])
			cnt=cnt+1
			#if cnt==4:			# Debug
			#	PLog(prgSet)
			
			set_url = stringextract('"href":"', '"', prgSet)			# 1. link in _links
			set_img = stringextract('{"href":"', '{ratio}', prgSet)
			set_img = set_img + "1x1/640?mandant=ard"
			
			anzahl = stringextract('"numberOfElements":', ',', prgSet)
			prg_id = stringextract('/programsets/', '{?order', prgSet)
			href = base + "programsets/%s" % prg_id
			
			pos = prgSet.find('numberOfElements":')						# enthält Titel, Kategorie, ..
			cat = prgSet[pos:]
			title = stringextract('"title":"', '"', cat)
			
			#cat_url = stringextract('"href":"', '"', cat)				# -> Kategorie, nicht -> PRG
			
			cat_img = stringextract('"mt:image":', '"templated"', cat)	# Kategorie-Bild z.Z. nicht verwendet
			cat_img = stringextract('"href":"', '{ratio}', cat_img)
			cat_img = cat_img + "1x1/640?mandant=ard"
			pos = cat.find('"id":'); cat = cat[pos:]
			cat_title = stringextract('"title":"', '"', cat)
			
			tag = u"%s\n[B]Folgeseiten[/B] | Sendungen: %s"  % (cat_title, anzahl)
			
			PLog('14Satz:');
			PLog(title); PLog(tag); PLog(img); PLog(href); PLog(anzahl);
			title=py2_encode(title); href=py2_encode(href);
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (quote(href), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_sendung", fanart=img, thumb=set_img, fparams=fparams, 
				tagline=tag)
						
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#----------------------------------------------------------------
# Wrapper für Listing der Einzelbeiträge -> Audio_get_json
# Aufrufer: Audio_get_json_multi, Audio_get_sendung,
#	Audio_get_cluster_search, Audio_get_cluster_single
#
def Audio_get_rubrik(title, path, ID, page=''):							
	PLog('Audio_get_rubrik: ' + ID)
	PLog(path); PLog(len(page))
	path_org = path; ID_org=ID
	
	li = xbmcgui.ListItem()
	
	if page == '':								# Seite holen für Folgeaufrufe
		page, msg = get_page(path=path)	
		if page == '':	
			if 	"Error 404" in msg:
				msg1 = "HTTP Error 404 - %s nicht im API gefunden." % ID
				msg2 = u"Alternative: Webseite suchen für:"
				msg3 = "[B]%s[/B]" % title
				ret=MyDialog(msg1, msg2, msg3, ok=False, yes='JA')
				if ret:
					ID = "Error_404_Search"
					path = "https://www.ardaudiothek.de/suche/%s" % title
					Audio_get_cluster_search(li, path, title="Suche: %s" % title, ID=ID, query=title)
			else:
				msg1 = "Fehler in Audio_get_rubrik:" 
				msg2 = msg
				MyDialog(msg1, msg2, '')		
			return li
		PLog(len(page))
	else:										#1. Aufruf: AudioStartHome	
		Audio_get_json_multi(li, page, ID)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return									# zusätzl. nötig
		
	#------------------------------------------	# Folgeaufrufe
	li = home(li, ID='ARD Audiothek')			# Home-Button
	ID = "get_rubrik"							# neue ID für Audio_get_json_single
		
	cnt, downl_list = Audio_get_json_single(li, page=page, ID=ID)

	destfunc = "Audio_get_rubrik"
	Audio_get_nexturl(li, page, title, ID, destfunc)				# Mehr-Button anhängen
	path = ""
	
	#-------------------	# für Podfavs Button "Suchergebnis hinzufügen", nicht bei PodFavs selbst:
							
	if '/search/' in path and ID_org != "PodFavs":	
		query = stringextract('query=', '&', path)
		query = unquote_plus(query)								
		offset = stringextract('offset=', '&', path)
		if offset == "0" or  offset == "": 
			offset = "1"
		
		fav_path =  SETTINGS.getSetting('pref_podcast_favorits')
		if fav_path == 'podcast-favorits.txt' or fav_path == '':		# im Verz. resources
			fav_path = R(fav_path)
			fname = os.path.basename(fav_path)
		else:
			fav_path = os.path.abspath(fav_path)
			fname = "%s..%s" % (os.path.dirname(fav_path[:10]), os.path.basename(fav_path))
		PLog("fav_path: " + fav_path)
		PLog(os.path.isfile(fav_path)); 
		
		if os.path.isfile(fav_path):									# Button zum Anfügen in podcast-favorits.txt
			query	= "Suchergebnis: %s (ab Beitrag %s)" % (query, offset)
			title 	= u"Suchergebnis den Podcast-Favoriten hinzufügen"
			tag 	= query
			summ 	= "Ablage: %s" % fname
			mehrfach='0'
			fparams="&fparams={'title': '%s', 'path': '%s', 'fav_path': '%s', 'mehrfach': '%s'}" % \
				(quote(query), quote(path_org), quote(fav_path), mehrfach)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodAddFavs", 
				fanart=R(ICON_STAR), thumb=R(ICON_STAR), fparams=fparams, summary=summ, 
				tagline=tag)			
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# fertigt den Mehr-Button an Ende von Ergebnislisten 
#	via "next"-Key in json-Datei
def Audio_get_nexturl(li, page, title, ID, destfunc):							
	PLog('Audio_get_nexturl: ' + ID)
	
	next_url = stringextract('"next":', '}},', page)				# 1. next-Link gilt
	# anz = stringextract('"numberOfElements":', ',', page)			# anz fehlt bei einz. Rubriken
	if next_url:
		url = stringextract('"href":"', '"', next_url)
		url = ARD_AUDIO_BASE + url
		offset = stringextract('offset=', '&', url)
		img = R(ICON_MEHR)
		tag = u"Mehr (ab Beitrag %s)" % (offset)					# o. anz
		PLog('next:'); PLog(url); PLog(tag);
		url=py2_encode(url); title=py2_encode(title); ID=py2_encode(ID) 
		
		if 'get_rubrik' in destfunc:
			fparams="&fparams={'title': '%s', 'path': '%s', 'ID': '%s'}" % (quote(title), 
				quote(url), quote(ID))
			addDir(li=li, label=title, action="dirList", dirID=destfunc, \
				fanart=img, thumb=img, fparams=fparams, tagline=tag)

		if 'PodFavoriten' in destfunc:
			fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(url), 
				quote(title))
			addDir(li=li, label=title, action="dirList", dirID=destfunc, \
				fanart=img, thumb=img, fparams=fparams, tagline=tag)
					
	return

#----------------------------------------------------------------
# gibt entw. den  HTML- oder den json-Teil der Webseite zurück
#
def Audio_get_webslice(page, mode="web"):
	PLog('Audio_get_webslice:')
	
	if mode == "web":
		pos1 = page.find('</head><body>')
		pos2 = page.find('"props"')
		page = page[pos1:pos2]
	if mode == "json":
		pos1 = page.find('"props"')
		pos2 = page.find('<script nomodule=')
		page = page[pos1:pos2]
	
	PLog(len(page))
	return page
	
#----------------------------------------------------------------

# anstelle Homepage: Auswertung homescreen.json, nur Einzelbeiträge:
#	Entdecken, Meistgehört, Podcast-Favoriten, Suche
#
#	30.07.2021 Anpassung an renovierte Audiothek  (weitere ID's,
#		Rückgabe Zähler + Downloadliste), Aufrufer erl. li, Home + 
#		Mehr-Button
#
def Audio_get_json_single(li, page, ID, jsonObject=''):
	PLog('Audio_get_json_single: ' + ID)
	PLog(len(page))
	
	audObs=[];
	if jsonObject:
		audObs = jsonObject
	else:
		jsonObject = json.loads(page)
		if ID == u'Entdecken':				# Einzelbeiträge
			PLog("Mark3")
			audObs = jsonObject["_embedded"]['mt:stageItems']['_embedded']['mt:items']
		if ID == u'Meistgehörte Episoden':	# Einzelbeiträge
			audObs = jsonObject['_embedded']['mt:mostPlayed']['_embedded']['mt:items']
		if ID == u'get_rubrik':				# Einzelbeiträge vom Wrapper Audio_get_rubrik und
											#	Einzelbeiträge Podcast-Favoriten (podcast-favorits.txt)
			audObs = jsonObject['_embedded']['mt:items']
		if ID == u'AudioSearch':			# z.Z. Einzelbeiträge
			audObs = jsonObject['_embedded']['mt:itemSearchResults']['_embedded']['mt:items']
		if ID == u'Sport':					# wie Podcast-Favoriten
			audObs = jsonObject['_embedded']['mt:items']
					
	PLog(len(audObs))
		
	cnt=0; downl_list=[]; 
	for aO in audObs: 
		href=''
		try:
			try:
				mp3_url	= aO["_links"]['mt:downloadUrl']['href']
			except:	
				mp3_url	= aO["_links"]['mt:bestQualityPlaybackUrl']['href']
					
			href = aO["_links"]["self"]["href"]
			img = aO["_links"]["mt:image"]["href"]
			img = img.replace('{ratio}/{width}', '1x1/640')
			title = aO["title"]
			dauer = aO["duration"]
			dauer = seconds_translate(dauer)
			descr = aO["synopsis"]		
			stitle	= aO["tracking"]["play"]["show"]
			source	= aO["tracking"]["play"]["source"]
			pubDate	= aO["tracking"]["play"]["publicationDate"]
			pubDate = "%s.%s.%s" % (pubDate[6:8], pubDate[4:6], pubDate[0:4])
			
			descr	= "[B]Audiobeitrag[/B] | %s Std.| %s | %s\n\n%s" % (dauer, pubDate, source, descr)
			  
			descr	= unescape(descr); descr = repl_json_chars(descr)
			summ_par= descr.replace('\n', '||')
			title = repl_json_chars(title)
		
			PLog('15Satz:');
			PLog(title); PLog(stitle); PLog(img); PLog(href);  PLog(mp3_url); 
			title=py2_encode(title); mp3_url=py2_encode(mp3_url);
			img=py2_encode(img); summ_par=py2_encode(summ_par);	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, summary=descr)
				
			downl_list.append(title + '#' + mp3_url)
			cnt=cnt+1	
			
		except Exception as exception:
			PLog("json_Fehler: " + str(exception))
			#PLog(href)

	return cnt, downl_list
	
#----------------------------------------------------------------
#	30.07.2021 renovierte Audiothek: Ersatz für Audio_get_rubriken
#		Auswertung Mehrfach-Beiträge
#
def Audio_get_json_multi(li, page, ID, jsonObject=''):
	PLog('Audio_get_json_multi: ' + ID)

	audObs=[];
	if jsonObject:
		audObs = jsonObject
	else:
		jsonObject = json.loads(page)
		if ID == u'Unsere Favoriten':		
			audObs = jsonObject["_embedded"]['mt:editorialCollections']['_embedded']['mt:editorialCollections']
		if ID == u'Themen':			
			audObs = jsonObject["_embedded"]['mt:featuredPlaylists']['_embedded']['mt:editorialCollections']
		if ID == u'Ausgewählte Podcasts':				
			audObs = jsonObject["_embedded"]['mt:featuredProgramSets']['_embedded']['mt:programSets']
		if ID == u'Rubriken':				
			audObs = jsonObject["_embedded"]['mt:editorialCategories']
		if ID == u'funk':
			audObs = jsonObject["_embedded"]['mt:organizations'][11]['_embedded']["mt:publicationServices"]["_embedded"]["mt:programSets"]

		if ID == "Cluster_Sendungen":									# aus Audio_get_cluster_search 2. Aufruf
			audObs = jsonObject["_embedded"]['mt:programSets']	
			anz=jsonObject["numberOfElements"]
			PLog(anz)
			if anz==1:													# Klammer [ fehlt in json-Datei bei anz 1
				audObs=[]
				audObs.append(jsonObject['_embedded']['mt:programSets'])	
		if ID == "Cluster_Rubriken":									# aus Audio_get_cluster_search 2. Aufruf
			audObs = jsonObject["_embedded"]['mt:editorialCategories']	# kleines c in Audio_get_cluster_search!
			anz=jsonObject["numberOfElements"]
			PLog(anz)
			if anz==1:													# Klammer [ fehlt in json-Datei bei anz 1
				audObs=[]
				audObs.append(jsonObject['_embedded']['mt:editorialCategories'])	
		if ID == "Cluster_Sammlungen":											# aus Audio_get_cluster_search 2. Aufruf
			audObs = jsonObject["_embedded"]['mt:editorialCollections']	# 

	PLog(len(audObs))
		
	cnt=0;
	PLog(audObs)		
	for aO in audObs:
		try:	
			PLog("Mark0")
			href = aO["_links"]["self"]["href"]
			href = href.replace('order,', '')
			href = href.replace('{?offset,limit}', '?offset=0&limit=12')
			
			PLog("Mark1")			
			href = ARD_AUDIO_BASE + href
			img = aO["_links"]["mt:image"]["href"]
			img = img.replace('{ratio}/{width}', '1x1/640')
			sid = aO["id"]
			title = aO["title"]
			
			PLog("Mark2")			
			if ID == 'Rubriken' or ID == 'Cluster_Rubriken':			# Rubriken ohne Text, Anzahl
				descr=''
				anz=''
				tag = "Folgeseiten"
			elif ID == "funk":
				descr=''
				anz = aO["numberOfElements"]
				tag = "Folgeseiten"			
			else:
				descr = aO["synopsis"]	
				anz = aO["numberOfElements"]	
				tag	= "Folgeseiten | Anzahl %s" % (anz)
			PLog("Mark3")			
			  
			descr	= unescape(descr); descr = repl_json_chars(descr)
			summ_par= descr.replace('\n', '||')
			title = repl_json_chars(title)
		
			PLog('13Satz:');
			PLog(title); PLog(href); PLog(img); PLog(sid);  PLog(anz); 
			
			title=py2_encode(title); href=py2_encode(href); ID=py2_encode(ID);	
			fparams="&fparams={'title': '%s', 'path': '%s', 'ID': '%s', 'page': ''}" %\
				(quote(title), quote(href), quote(ID))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag)	
				
			cnt=cnt+1	
			
		except Exception as exception:
			PLog("json_Fehler: " + str(exception))

	return cnt

#----------------------------------------------------------------
# Auswertung Einzelrubrik /Sendung
# Aufrufer: AudioSenderPrograms
# 29.07.2021 Anpassung an renovierte Audiothek, Beiträge enthalten  
#	bereits Downloadlink
#	
def Audio_get_sendung(url, title):			# extrahiert Einzelbeiträge einer Sendung
	PLog('Audio_get_sendung: ' + title)
	title_org = title
	PLog(url);  
	base = "https://api.ardaudiothek.de/"
				
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')			# Home-Button
		
	path = url
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Audio_get_sendung:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li

	page = page.replace('\\"', '*')
	items = blockextract('mt:downloadUrl', page)
	if len(items) == 0:													# Bsp. ARD-Sendung Maischberger
		items = blockextract('mt:bestQualityPlaybackUrl', page)
	PLog(len(items))
	
	for item in items:
		mp3_url = stringextract('"href":"', '"', item)					#  1. Link

		img = stringextract('"mt:image":', '},', item)
		img = stringextract('"href":"', '"', img)
		img = img.replace('{ratio}', '1x1')
		img = img.replace('{width}', '640')

		pos = item.find('"duration"'); item=item[pos:]					# skip  title in links
		dur = stringextract('"duration":', ',', item)					# in Sek.
		dur = seconds_translate(dur)
		title = stringextract('"title":"', '"', item)
		title = repl_json_chars(title)
		summ = stringextract('"synopsis":"', '"', item)
		summ = repl_json_chars(summ)
		source = stringextract('"source":"', '"', item)
		pubDate = stringextract('"publicationDate":"', '"', item)
		pubDate = "%s.%s.%s" % (pubDate[6:8], pubDate[4:6], pubDate[0:4])
		
		tag = "Dauer %s | Datum %s | Sender %s" %  (dur, pubDate, source)
		summ_par = summ
		
		
		PLog('5Satz:');
		PLog(title); PLog(mp3_url); PLog(img); PLog(tag); PLog(summ[:80]);
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': ''}" % (quote(mp3_url), 
			quote(title), quote(img), quote_plus(summ_par))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)
				
	anz = stringextract('"numberOfElements":', ',', page)				# Mehr anzeigen
	next_url = stringextract('"next":', '}},', page)
	if next_url:
		url = stringextract('"href":"', '"', next_url)
		url = base + url
		offset = stringextract('offset=', '&', url)
		tag = u"Mehr (ab Beitrag %s von %s)" % (offset, anz)
		PLog(url); PLog(tag);
		title_org=py2_encode(title_org); url=py2_encode(url);
		fparams="&fparams={'title': '%s', 'path': '%s', 'ID': ''}" % (quote(title_org), quote(url))
		addDir(li=li, label=title_org, action="dirList", dirID="Audio_get_rubrik", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams, tagline=tag)		
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# 01.08.2021 Anpassung an renovierte Audiothek 	
# Alle Sendungen auf der organizations-Seite (Mehr anzeigen nicht erford.)
# Audio_get_json_multi verlinkt die einz. Sendungen mit Audio_get_rubrik
#
def Audio_get_rubrik_funk(url):							# Übersicht der funk-Podcasts
	PLog('Audio_get_rubrik_funk:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')					# Home-Button
		
	path = ARD_AUDIO_BASE + "organizations"
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in Audio_get_rubrik_funk:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	ID = "funk"
	Audio_get_json_multi(li, page, ID)					# Folgeaufrufe -> Audio_get_rubrik
			
	fparams="&fparams={}"								# Button funk-Modul hinzufügen
	addDir(li=li, label="zum FUNK-Modul", action="dirList", dirID="resources.lib.funk.Main_funk", 
		fanart=R('funk.png'), thumb=R('funk.png'), fparams=fparams)
			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#----------------------------------------------------------------
# AudioSingle gibt direkt das Thema-mp3 seiner Homepage wieder - die 
# 	Funktion ist Fallback für Beiträge (Bsp. Startseite), für die sonst
#	keine mp3-Quelle gefunden wurde.
# Die mp3-Quelle wird zusammen mit den Params zu AudioPlayMP3 durch-
#	gereicht	 
#
def AudioSingle(url, title, thumb, Plot):
	PLog('AudioSingle:')
	page, msg = get_page(path=url)	
	if page == '':	
		msg1 = "Fehler in AudioSingle:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))	
	
	pos1 = page.rfind('.mp3')			# Thema-mp3 an letzer Stelle im json-Teil
	page = page[:pos1]
	pos2 = page.rfind('https')
	PLog('pos1 %d, pos2 %d' % (pos1, pos2))
	l = page[pos2:] + '.mp3'

	url = l.replace('\\u002F', '/')
	PLog(url[:100])

	AudioPlayMP3(url, title, thumb, Plot)  # direkt	
	return

#----------------------------------------------------------------
# ermittelt img auf Webseite href (i.d.R. html/json gemischt) 
# 05.08.2021 benötigt in der alten Audiothek. Verbleibt vorerst..
#
def img_via_web(href):
	PLog('img_via_web:')
	
	img=''
	ID = href.split('/')[-1]
	fpath = os.path.join(SLIDESTORE, 'Audiothek')	# Bildverzeichnis
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
			PLog('erzeugt: %s' % fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = fpath
			PLog(msg1); PLog(msg2)
			MyDialog(msg1, msg2, '')
			return li	
	
	fpath = os.path.join(fpath, '%s.png' % ID)		# Pfad um Bildname erweitern
	fname =  '%s.png' % ID
	oldfpath = os.path.join(TEXTSTORE, ID)			# alte Webseite (vor Umstellung)
	PLog('fpath: ' + fpath)
	if os.path.exists(fpath) and os.stat(fpath).st_size == 0: # leer? = fehlerhaft -> entfernen 
		PLog('fpath_leer: %s' % fpath)
		os.remove(fpath)
	if os.path.exists(oldfpath):					# aufräumen
		os.remove(oldfpath)

	if os.path.exists(fpath):						# lokale Bildadresse existiert
		PLog('lade_img_lokal') 
		img = fpath	
	else:	
		from threading import Thread
		icon = R(ICON_MAIN_AUDIO) 
		bg_thread = Thread(target=thread_img_via_web, args=(href, fpath, fname, icon))
		bg_thread.start()											

	#if img == '':									# ohne Fallback bei thread
	#	img = R('icon-bild-fehlt.png')				
	return img

#----------------------------------------------------------------
# Hintergrundroutine für img_via_web
# Extrahiert img aus Webseite url und speichert in path
# 
def thread_img_via_web(url, path, fname, icon):
	PLog("thread_img_via_web:")
	
	try:
		page, msg = get_page(path=url)	
		if page:									# Bild holen
			img_web = stringextract('property="og:image" content="', '"', page) # Bildadresse 
			urlretrieve(img_web, path)
			msg1 = "Lade Bild"
			msg2 = fname
			xbmcgui.Dialog().notification(msg1,msg2,icon,1000, sound=False)	 
		else:
			PLog(msg)								# hier ohne Dialog
	except Exception as exception:
		PLog("thread_getsinglepic:" + str(exception))
	
	return
										
#----------------------------------------------------------------
# 30.07.2021 Anpassung an renovierte Audiothek (neuer api-Call +
#	Nutzung Audio_get_json_single) - bisher nur Einzelbeiträge ausgewertet
# 03.08.2021 für Auswertung der Cluster Rückkehr zum html-Code (Cluster-
#	Titel fehlen im api, Key-Probleme bei Objektanzahl 1) 
#
def AudioSearch(title, query='', path=''):
	PLog('AudioSearch:')
	CacheTime = 6000								# 1 Std.
	title_org = title
	ID="AudioSearch"

	base = "https://www.ardaudiothek.de/suche/%s/"
	# api-Bsp.: https://api.ardaudiothek.de/search?query=pandemie:
	
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
		path = base  % quote(query)
	path_org=path
	
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioSearch:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
		
	if '>Keine Treffer</' in page:	
		msg1 = "leider keine Treffer zu:"
		msg2 = query
		MyDialog(msg1, msg2, '')	
		return li
		
	Audio_get_cluster_search(li, path, title="Suche: %s" % query, ID=ID, query=query)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#----------------------------------------------------------------
# 1. Aufruf: lädt Webseite für Suche + ermittelt Cluster im Webteil,
#	erstellt die passenden api-Calls
# 2. Aufruf: führt api-Call aus und übergibt an Audio_get_json_multi
#
def Audio_get_cluster_search(li, url, title, page='', ID='', query=''):
	PLog('Audio_get_cluster_search: ' + ID)
	PLog(query)
	
	if li  == '':
		li = xbmcgui.ListItem()
		li = home(li,ID='ARD Audiothek')							# Home-Button		
		
	if page == '':							
		page, msg = get_page(path=url)	
		if page == '':	
			msg1 = "Fehler in Audio_get_cluster_search:" 
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
		PLog(len(page))
		
	#--------------------------------								# 2. Aufruf Sendungen, Sammlungen
	if ID=="Cluster_Sendungen" or ID=="Cluster_Rubriken" or ID=="Cluster_Sammlungen":		
		#PLog(page[:80])
		Audio_get_json_multi(li, page, ID)	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	#--------------------------------								# 1. Aufruf 

	if page.startswith('<!DOCTYPE html>'):
		page = Audio_get_webslice(page, mode="html")				# HTML ausschneiden
		
	href_add = "offset=0&limit=12"
	# Bsp. Cluster: <h2 class="H2-sc-1h18a06-3 hzOdMY">Sendungen <span..
	cluster = blockextract('<h2 class="H2', page)					
	PLog(len(cluster))	
	for clus in cluster:
		href = stringextract('href="', '"', clus)					# Web-href
		sid = href.split("/")[-1]									# z.B. 21679406

		ftitle = stringextract('<h3 class="H3', '<div>', clus)		# 1. Titel für tag
		ftitle = stringextract('">', '</h3>', ftitle)
		ftitle = unescape(ftitle); ftitle = repl_json_chars(ftitle)
		img = stringextract('img src="', '"', clus)					# 1. img vor srcSet
		if img == '':
			img = R(ICON_DIR_FOLDER)

		tag = "[B]Folgeseiten[/B]"
		if '/sendung/' in href:
			href = ARD_AUDIO_BASE  + "search/programsets?query=%s&%s" % (query, href_add) 
			dest_func = "Audio_get_cluster_search"
			title = "Sendungen"
			ID = "Cluster_Sendungen"
		if '/sammlung/' in href:
			href = ARD_AUDIO_BASE  + "search/editorialcollections?query=%s&%s" % (query, href_add) 
			dest_func = "Audio_get_cluster_search"
			title = "Sammlungen"
			ID = "Cluster_Sammlungen"
		if '/rubrik/' in href:
			href = ARD_AUDIO_BASE  + "search/editorialcategories?query=%s&%s" % (query, href_add) 
			dest_func = "Audio_get_cluster_search"
			title = "Rubriken"
			ID = "Cluster_Rubriken"
		if '/episode/' in href or ID == "Error_404_Search":			# optionale Websuche in Audio_get_rubrik
			dest_func = "Audio_get_rubrik"
			href = ARD_AUDIO_BASE  + "search/items?query=%s&%s" % (query, href_add) 
			title = "Episoden (einzelne Beiträge)"
		
		if ftitle:
			tag = "%s\n\n1. Beitrag: %s" % (tag, ftitle)
		
		PLog("1Satz:")
		PLog(href); PLog(title); PLog(img);
		
		href=py2_encode(href); title=py2_encode(title); ID=py2_encode(ID) 
		if dest_func == "Audio_get_rubrik":	
			fparams="&fparams={'title': '%s', 'path': '%s', 'ID': '%s'}" % (quote(title), 
				quote(href), quote(ID))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag)	
		if dest_func == "Audio_get_cluster_search":	
			fparams="&fparams={'li': '','url': '%s', 'title': '%s', 'ID': '%s'}" % (quote(href), 
				quote(title), quote(ID))
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_search", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag)	
			
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#----------------------------------------------------------------
# Aufrufer: Audio_get_rubriken_web (Liste Rubriken)
# anders als Audio_get_cluster_search wird für Rubriken der json-
#	Teil der Webseite ausgewertet - mit string-funktionen, da 
#	python's json.loads + json.load hier fehlschlagen.
#	Der Webteil eignet sich nicht wg. fehlender Bilder in den
#	Empfehlungen.
# Aufteilung Web-Beiträge: 1. Highligths, 2. veränderliche
#	Cluster, 3. Meistgehört, 4. Neueste Episoden, 5. Ausgewählte 
#	Sendungen, 6. Alle Sendungen aus dieser Rubrik  
def Audio_get_cluster_rubrik(li, url, title, ID=''):
	PLog('Audio_get_cluster_rubrik: ' + ID)
	PLog(title)
	title_org = title
	CacheTime = 6000												# 1 Std.
	
	if li  == '':
		li = xbmcgui.ListItem()
		li = home(li,ID='ARD Audiothek')							# Home-Button		
		
	
	rid = url.split('/')[-1]
	rubrik_id = "AudioRubrikWebJson_%s" % rid

	page = Dict("load", rubrik_id, CacheTime=CacheTime)				# json-Teil der Webseite schon vorhanden?
	if page == False or page == '':									# Cache miss od. leer - vom Sender holen
		# Name im Pfad fehlt hier noch, daher Redirect:
		page, msg = get_page(path=url, GetOnlyRedirect=True)		# Permanent-Redirect-Url
		url = page								
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
	sections = stringextract('"sections":', '"widgets":', page)	
	PLog(sections[:80])
	
	PLog('Mark0')
	block = ']},{"id":'	
		
	data=[]
	if '"type":"STAGE"' in page:									# Empfehlungen vor Blockmarke
		stage = stringextract('"STAGE"', '"GRID_LIST"', page)
		data.append(stage)
	cluster = blockextract(block, sections)
	data = data + cluster
	PLog(len(data))
	
	for item in data:												# einschl. Meistgehört, Neueste Episoden ..			
		tag = u"[B]Folgeseiten[/B]"
		title = stringextract('"title":"', '"', item)				# Cluster-Titel	
		pos = item.find('__typename'); item = item[pos:]			# 1. Beitrag
		ftitle = stringextract('"title":"', '"', item)
		img = stringextract('"url1X1":"', '"', item)
		img = img.replace('{width}', '640')
		tag = "%s\n\n1. Beitrag: %s" % (tag, ftitle)	

		PLog('2Satz:')
		PLog(title); PLog(rubrik_id); 
		title=py2_encode(title); rubrik_id=py2_encode(rubrik_id); 
		fparams="&fparams={'title': '%s', 'rubrik_id': '%s'}" % \
			(quote(title), quote(rubrik_id))
		addDir(li=li, label=title, action="dirList", dirID="Audio_get_cluster_single", \
			fanart=img, thumb=img, fparams=fparams, tagline=tag)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#----------------------------------------------------------------
# Aufrufer Audio_get_cluster_rubrik: listet einz. Cluster
#	Json-Ausschnitt der Rubrik-Webseite im Dict(rubrik_id)
#
def Audio_get_cluster_single(title, rubrik_id):
	PLog('Audio_get_cluster_single: ' + title)
	PLog(rubrik_id)

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')			# Home-Button

	page = Dict("load", rubrik_id)
	#PLog(page[:80])
	cluster = stringextract('"title":"%s' % title, '}]},', page)	# einz. section/Cluster
	#PLog(cluster[:80])
	if cluster == '':
		cluster = stringextract('"title":"%s' % title, '}]}],', page)# letzter Cluster (Alle Sendungen aus..)
	PLog(len(cluster))
	PLog(cluster[:80])
	
	pos = cluster.find('nodes'); cluster = cluster[pos:]

	nodes = blockextract('"__typename":', cluster)	
	PLog(len(nodes))
			
	downl_list=[]; 	href_add = "offset=0&limit=12"	
	for node in nodes:
		imgalt2=''
		node_id = stringextract('"id":"','"', node)				# ID der Sendung / des Beitrags / ..	
		typename = stringextract('__typename":"','"', node)		# Typ der Sendung / des Beitrags / ..	
		title = stringextract('"title":"','"', node)	
		dur = stringextract('"duration":',',', node)
		dauer = seconds_translate(dur)
		pubDate = stringextract('"publishDate":"','"', node)
		if pubDate:												# 2021-08-11T07:00:00+00:00
			pubDate = pubDate = "%s.%s.%s %s Uhr" % (pubDate[8:10], pubDate[5:7], pubDate[0:4], pubDate[11:16])
		descr = stringextract('"summary":"','"', node)	
		mp3_url = stringextract('"downloadUrl":"','"', node)
		if 	mp3_url == '':										# EventLivestream
			mp3_url = stringextract('"url":"','"', node)
		img = stringextract('"url1X1":"','"', node)	
		img = img.replace('{width}', '640')
		imgalt1 = stringextract('"description":"','"', node)	# Bildbeschr.	
		imgalt2 = stringextract('"attribution":"','"', node)	# Bild-Autor
		imgalt2 = repl_json_chars(imgalt2)
		org = stringextract('"organizationName":"','"', node)	
		anz = stringextract('"totalCount":','}', node)			# Anzahl bei Mehrfach-Beiträgen
		
		descr	= unescape(descr); descr = repl_json_chars(descr)
		summ_par= descr.replace('\n', '||')
		title = repl_json_chars(title)
		
		PLog('4Satz:');
		PLog(title); PLog(img); PLog(mp3_url); PLog(descr[:40]);
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	

		if typename=="Item" or typename=="EventLivestream":		# Einzelbeitrag
			tag = "[B]Audiobeitrag[/B] | %s Std. | %s | %s\nBild: %s" % (dauer,pubDate,org,imgalt2)
			if typename=="EventLivestream":		
				tag = "[B]EventLivestream[/B]  %s | %s\nBild: %s" % (pubDate,org,imgalt2)
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=descr)
				
						
	#--------------------------------							# Cluster mit Folgebeiträgen
		if typename=="EditorialCollection" or typename=="ProgramSet":
			if anz: anz = "(%s)" % anz
			if imgalt2: imgalt2 = "Bild: %s" % imgalt2
			tag = u"[B]Folgebeiträge[/B] %s\n%s" % (anz, imgalt2)
			if typename=="EditorialCollection":	
				ID="Cluster_Sammlungen"
				href = ARD_AUDIO_BASE  + "editorialcollections/%s?%s" % (node_id, href_add)
			if typename=="ProgramSet":
				ID=typename
				href = ARD_AUDIO_BASE  + "programsets/%s?%s" % (node_id, href_add)
				
			PLog(href);
			href=py2_encode(href)
			fparams="&fparams={'title': '%s', 'path': '%s', 'ID': '%s', 'page': ''}" %\
				(quote(title), quote(href), ID)
			addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik", \
				fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=descr)						
			
		if 	mp3_url:											# Downloadliste füllen
			downl_list.append(title + '#' + mp3_url)
			
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	
#----------------------------------------------------------------
# holt die Stage-Beiträge von der Web-Startseite (json-Teil), da
# nicht im api enthalten.
# Aufrufer: AudioStartHome
def Audio_get_cluster_stage():
	PLog('Audio_get_cluster_stage:')
	CacheTime = 6000											# 1 Std.
	
	path = "https://www.ardaudiothek.de/"
	ID = "AudioWebStage"
	page = Dict("load", ID, CacheTime=CacheTime)				# Startseite Web laden
	if page == False or page == '':								# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", ID, page)						
	if page == '':	
		msg1 = "Fehler in Audio_get_rubriken_web:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
			
	li = xbmcgui.ListItem()
	li = home(li,ID='ARD Audiothek')							# Home-Button		
	
	page = Audio_get_webslice(page, mode="json")				# json ausschneiden
	page = transl_json(page); page = page.replace('\\"', '*')
	
	pos1=page.find('"STAGE"'); pos2=page[pos1+10:].find('"nodes"')
	page = page[pos1:pos2]
	PLog(len(page))
	
	block = '}}},'; items=[]
	item1 = stringextract('"nodes"', '}}},', page)				# 1. Beitrag voranstellen
	items.append(item1)
	items = items + blockextract(block, page)
	PLog(len(items))
	
	for item in items:
		node_id = stringextract('"id":"','"', item)				# ID der Sendung / des Beitrags / ..	
		typename = stringextract('__typename":"','"', item)		# Typ der Sendung / des Beitrags / ..	
		title = stringextract('"title":"','"', item)	
		dur = stringextract('"duration":',',', item)
		dauer = seconds_translate(dur)	
		pubDate = stringextract('"publishDate":"','"', item)
		if pubDate:												# 2021-08-11T07:00:00+00:00
			pubDate = pubDate = "%s.%s.%s" % (pubDate[8:10], pubDate[5:7], pubDate[0:4])
		descr = stringextract('"description":"','"', item)	
		mp3_url = stringextract('"downloadUrl":"','"', item)
		if mp3_url == '':
			audios = stringextract('"audios":[',']', item)	
			mp3_url = stringextract('"url":"','"', audios)		# downloadUrl kann fehlen
		img = stringextract('"url1X1":"','"', item)	
		img = img.replace('{width}', '640')
		#imgalt1 = stringextract('"description":"','"', item)	# Bildbeschr.	
		imgalt2 = stringextract('"attribution":"','"', item)	# Bild-Autor
		org = stringextract('"organizationName":"','"', item)	
		
		descr	= unescape(descr); descr = repl_json_chars(descr)
		summ_par= descr.replace('\n', '||')
		title = repl_json_chars(title); imgalt2 = repl_json_chars(imgalt2); 
		
		PLog('6Satz:');
		PLog(title); PLog(img); PLog(mp3_url); PLog(descr[:40]); PLog(dauer)
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	

		if typename == "Item":									# Einzelbeitrag
			tag = "[B]Audiobeitrag[/B] | %s Std.| %s | %s\nBild: %s" % (dauer,pubDate,org,imgalt2)		
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
				quote(title), quote(img), quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=descr)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#----------------------------------------------------------------
# Ausgabe Audiobeitrag
# Falls pref_use_downloads eingeschaltet, werden 2 Buttons erstellt
#	(Abspielen + Download).
# Falls pref_use_downloads abgeschaltet, wird direkt an PlayAudio
#	übergeben.
# 01.07.2021 ID variabel für Austausch des Home-Buttons
#
def AudioPlayMP3(url, title, thumb, Plot, ID=''):
	PLog('AudioPlayMP3: ' + title)
	
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
	
		
	download_list = []					# 2-teilige Liste für Download: 'title # url'
	download_list.append("%s#%s" % (title, url))
	PLog(download_list)
	title_org=title; tagline_org=''; summary_org=Plot
	li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=-1)  # Downloadbutton
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
##################################### Ende Audiothek ###############################################

def ARDSport(title):
	PLog('ARDSport:'); 
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	SBASE = 'https://www.sportschau.de'
	path = 'https://www.sportschau.de/index.html'	 		# Leitseite		
	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))	
	
	title = "Live"								# Zusatz: Live (in tabpanel "Live&Ergebnisse")
	# href = 'https://www.sportschau.de/ticker/index.html'
	href = 'https://www.sportschau.de/streamindex100.html'
	img = R(ICON_DIR_FOLDER)
	# summ = "Livestreams nur hier im Menü [B]Live[/B] oder unten bei den Direktlinks unterhalb der Moderatoren"
	tagline = 'aktuelle Liveberichte und Vorschau'
	title=py2_encode(title); href=py2_encode(href); 
	href=py2_encode(href); img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)			

	# Dauerlinks am Fuß der Leitseite (Tab's am Kopf  können abweichen)
	# skip_title enthält manuell bearbeitete Buttons (Bsp. Olympia in Tokio), 
	#	die unten eingefügt werden-
	skip_title = ["Olympia in Tokio"]
	tabpanel = stringextract('<ul id="gseafooterlinks116-panel"', '</ul>', page) 
	tabpanel = blockextract('<li>', tabpanel)
	img = R(ICON_DIR_FOLDER)
	i=0	
	for tab in tabpanel:								# Panel Fußbereich
		tag=''
		if i == 0:										# Tab Startseite
			href = path
			title = 'Startseite'
		else:		
			href = stringextract('href="', '"', tab)
			title = stringextract('">', '</a>', tab)
			
		if title in skip_title:
			continue
		if "Ergebnisse" in title:
			title = "[COLOR grey]%s[/COLOR]" % title
			tag = "[B]Tabellen, Medaillienspiegel u.ä. sind im Addon leider nicht darstellbar[/B]"
				
		i=i+1
		if href.startswith('http') == False:
			href = SBASE + href
		href = href.replace('http://', 'https://')			# alte Links im Quelltext
		
		if "sportschau.de/weitere/index.html" in href:		# Korrektur (Fehler Webseite)
			href = "https://www.sportschau.de/mehr-sport/index.html"
		
		PLog("Satz17:"); 
		PLog(href); PLog(title);
		title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);	
		fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
			quote(href), quote(img))
		addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
			thumb=img, tagline=tag, fparams=fparams)			
	
	#-------------------------------------------------------# Zusätze
	# beim Ziel ARDSportPanel den Titel in theme_list für 2. Durchlauf 
	#	aufnehmen - entfernen, wenn Titel nicht in Panel vorh. (Auswer-
	#	tung läuft dann über die teaser-Blocks).
	#'''				
	title = "EURO 2020"									# (nicht in Fußlinks)
	href = 'https://www.sportschau.de/fussball/uefaeuro2020/index.html'
	img =  'https://www.sportschau.de/fussball/euro-zweitausendundzwanzig-logo-100~_v-gseagaleriexl.jpg'
	tagline = 'Alle Infos zur UEFA EURO 2021 - EURO 2020 - Fußball - sportschau.de'
	summ = u"Nachrichten, Berichte, Interviews und Ergebnisse zur UEFA EURO 2021 - Videos, Beiträge und Bilder zum Thema bei sportschau.de."
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
		thumb=img, tagline=tagline, summary=summ, fparams=fparams)
	#'''
	
	title = "Tour"										# (nicht in Fußlinks)
	label = "Tour de France"
	href = 'https://www.sportschau.de/radsport/tourdefrance/index.html'	# intern anderer Link s.u.
	#href = 'https://www.sportschau.de/tdf-navipunkt/index.html'		# 27.08.2021 wieder geändert
	img =  'https://www.sportschau.de/radsport/tourdefrance/gesamtkarte-tour-100~_v-gseagaleriexl.jpg'
	tagline = 'Tour de France 2021, Livestreams, Videos, Nachrichten, Rennberichte, Etappen, Ergebnisse und Wertungen - Tour de France - Radsport - sportschau.de'
	tagline = "Bildquelle: ard | Die Gesamtübersicht über die Strecke der Tour de France 2021\n\n%s" % tagline
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=label, action="dirList", dirID="ARDSportPanel", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)
	

	title = "Olympia in Tokio"										# manuell trotz Fußlinks 
	#href = 'https://tokio.sportschau.de/tokio2020/index.html'
	href = 'https://tokio.sportschau.de'
	img =  'https://www.ndr.de/sport/olympia3382_v-contentxl.jpg'
	tagline = 'Olympische Spiele 2021 in Tokio | 23.07.-08.08.2021 | Die wichtigsten Daten und Fakten'
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s',  'paneltabs': 'true'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)

	
	title = "Moderatoren"									# Moderatoren 
	href = 'https://www.sportschau.de/sendung/moderation/index.html'
	img =  'https://www1.wdr.de/unternehmen/der-wdr/unternehmen/bundesliga-sportschau-jessy-wellmer-100~_v-gseaclassicxl.jpg'
	tagline = 'Bilder von Moderatoren, Slideshow'
	title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
		quote(href), quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportBilder", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)			

	fparams="&fparams={}"
	label =u'ARD Event Streams (eingeschränkt verfügbar)'
	img = R("tv-ard-sportschau.png")	
	addDir(li=li, label=label, action="dirList", dirID="ARDSportEvents", fanart=img, 
		thumb=img, fparams=fparams)	
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#--------------------------------------------------------------------------------------------------
def ARDSportEvents():
	PLog('ARDSportEvents:');
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	 	
	# Quellen für Event-Livestreams (Chrome-Dev.-Tools):	
	# https://fifafrauenwm.sportschau.de/frankreich2019/live/eventlivestream3666-ardjson.json
	# https://lawm.sportschau.de/doha2019/live/livestreams170-extappjson.json

	# Livestreams WDR - s. Forum:
	# Livestream: MDR-Sachsen Fußball-Livestream Audio (nicht in livesenderTV.xml)
	#	Forum Weri 22.09.2020 - 04.04.2021 verlagert in livesenderTV.xml, SenderLiveResolution
	#		angepasst.
	#	Forum Weri 07.07.2021 - Integration ARD Audio Event Streams 
	#		wg. Übersichtlichkeit mit Buttons für TV + Audio -> ARDSportAudioXML
	channel = u'ARD Event Streams (eingeschränkt verfügbar)'									
	img = R("tv-ard-sportschau.png")			# dummy		
	# SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender='') # vormals direkt
	title = u'ARD TV Event Streams (eingeschränkt verfügbar)'  
	img = R("tv-ard-sportschau.png")
	tag = u'Reportagen von regionalen gesellschaftlichen und Sport-Events ' 
	img=py2_encode(img); channel=py2_encode(channel); title=py2_encode(title);
	fparams="&fparams={'channel': '%s'}"	% (quote(channel))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioXML", fanart=img, 
		thumb=img, tagline=tag, fparams=fparams)					

	ARDAudioEventStreams(li)					# zusätzl. Streams				
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#--------------------------------------------------------------------------------------------------
# gibt Video (fett) oder Audio (rot+fett) zurück 
# rec: Datensatz Sportschauseiten
# Bsp. Audio: class="media mediaA audio ">
def ARDSportgetMedia(rec):
	PLog('ARDSportgetMedia:');
	
	media=''
	audio_lst = ["media mediaA audio", "icon icon_audio"]
	video_lst = ["media mediaA video", "icon icon_video"]
	
	for m in audio_lst:
		if m in rec:
			return "[B][COLOR red]Audio[/COLOR][/B]"
			break
	for m in video_lst:
		if m in rec:
			return "[B]Video[/B]"
			break
	PLog("media: leer")
	return media

#--------------------------------------------------------------------------------------------------
# 28.04.2020 redirected Url 
#	(s. Modul util) verwendet für https://tokio.sportschau.de/tokio2020/ s.u.
# 2 Durchläufe bei Seiten mit Tabmenüs, 2. Lauf mit tab_path (Wintersport, 
#	Formel 1, Handball-WM), paneltabs triggert Auswertung eigener tablist in
#		ARDSportPanelTabs
def ARDSportPanel(title, path, img, tab_path='', paneltabs=''):
	PLog('ARDSportPanel:');
	PLog(title); PLog(path); PLog(tab_path);
	title_org = title; path_org=path

	if path.endswith('/paralympics/live/index.html'):		# Sonderbehandlung Livestreams Paralympics -> 
		ARDSportEventLive(path, page='', title=title)		# ARDSportVideo -> ARDSportTokioLive
		return
		
	if paneltabs:									# abweichende tablist-Auswertung
		ARDSportPanelTabs(title.strip(), path, img)		# -> ARDSportPanel
		return

	if title.strip() == "Podcast":
		ARDSportPodcast(path, title.strip())
		return
				
	SBASE = 'https://www.sportschau.de'
	if tab_path == '':
		parsed = urlparse(path)
		SBASE = 'https://' + parsed.netloc
		if SBASE.endswith('/'):
			SBASE = SBASE[:len(SBASE)-1]
	PLog("SBASE: " + SBASE)
	
	pre_sendungen = ''; tdm_seite=False
	# Seite "TOR DES MONATS" voranstellen, Folgeseite Retro-Inhalt
	if path.endswith('sendung/tdm/index.html'): 
		pre_path = SBASE + '/sendung/tdm/abstimmung/tordesmonatsvideos104.html'
		page, msg = get_page(path=pre_path)	
		pre_sendungen = blockextract('class="teaser ', page)
		PLog(len(pre_sendungen))
	
	table_list = ["/medaillenspiegel/", "/ergebnisse/", "/ergebnisse_tabellen/"]
	for t in table_list:
		if 	t in path:									# Abzweig ARDSportTable
			ARDSportTable(path, title)					# Home-Button dort
			return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	if tab_path:										# Path 2. Durchlauf
		path = tab_path
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))
	
	if path.endswith('/video/index.html'):			# Struktur abweichend
		sendungen = blockextract('<a href="', page)
	else:
		sendungen = blockextract('class="teaser', page)
		PLog(len(sendungen))
	if pre_sendungen:							# Seite "TOR DES MONATS"
		pre_sendungen.extend(sendungen)	
		sendungen = pre_sendungen
		tdm_seite=True
	PLog(len(sendungen))
	
	# manuelle Buttons in ARDSport - s. Zusätze dort
	# Wintersport: solange nicht in den Tabs präsent, aus theme_list
	#	entfernen. Die Auswertung läuft dann direkt über die teaser-Blocks
	#	(s. for s in sendungen).
	# Nicht präsente Tabs führen zu invalid handle in addDir!
	# Getrennte Auswertung für abweichende Tabs in ARDSportPanelTabs (s.o.) 
	# theme_list = ["EURO 2020", "Tour"] 					#['Wintersport', "Nordische Ski-WM"]
	# 27.11.2021 Liste geleert
	theme_list=[]
	PLog(title in theme_list)						
	if tab_path == '' and title in theme_list:			# 1. Durchlauf bei Tabmenüs
		tablist = blockextract('class="collapsed', page, '</li>')
		PLog(len(tablist))
		
		found=False
		if len(tablist) > 0:
			#path_end = "/%s/%s" % (path.split('/')[-2], path.split('/')[-1])
			for tab in tablist:							# Unterseiten für Fußball, Wintersport, TV
				tabpanel=''
				PLog(tab[:200]); # PLog(path_end); 
				#if path_end in tab:
				if title in tab:
					tabpanel = tab
					PLog('tab_found')
					found=True
					break
					
		PLog(found)
		PLog(tabpanel[:160])							# einschl. Teil-Link
				
		if tabpanel:	
			tabs = blockextract('<li>', tabpanel)
			img = R(ICON_DIR_FOLDER)
			i=0	
			for tab in tabs:								# Panel Kopfbereich
				pos = tab.find('</li>')						# begrenzen
				if pos > 0:
					tab = tab[:pos]
				title = stringextract('">', '</a>', tab)
				title = cleanhtml(tab); title = mystrip(title)
				title = repl_json_chars(title)
				
				if 'Spielplan' in title: 					# skip, Ergebnisse -> ARDSportTable - s.o.
					continue
				href = stringextract('href="', '"', tab)
				if href.startswith('http') == False:
					href = SBASE + href
				if href == "https://www.sportschau.de":
					continue
					
				PLog("Satz4:"); 
				PLog(href); PLog(title);
				title=py2_encode(title); href=py2_encode(href);	
				img=py2_encode(img); 
				fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s', 'tab_path': '%s'}"	%\
					(quote(title), quote(href), quote(img), quote(href))
				addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
					thumb=img, fparams=fparams)			
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	# -----------------------------------------------------	# Ende 1. Durchlauf bei Tabmenüs			

	PLog('Panel_sendungen:')
	PLog("sendungen: %d" % len(sendungen))					# 'class="teaser'	
	mediatype=''; item_cnt=0
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	# Müll-Liste für continue:
	garb_list = [u'Javascript-Fehler', u'Fragen und Antworten zu', u'class="tickerDate"'
				u'//programm.ard.de', u'class="first"', u'class="list">', 
				u'title="Darstellung der Seite', u'zu Startseite Sportschau'
		]
	path_list=[];											# Dopplercheck 
	for s in sendungen:										# 'class="teaser'		
		duration=''; tag=''; summ=''; title=''; path=''; skip=False	
		for garb in garb_list:								# Müllabfuhr
			if garb in s:
				skip=True
		if skip:
			continue
			
		if 'Mehr Beitr' in s:								# begrenzen
			pos = s.find('Mehr Beitr')
			s = s[:pos]
		if 'text="mehr"' in s:								# begrenzen
			pos = s.find('text="mehr"')
			s = s[:pos]
		if 'mehr</strong>' in s:							# begrenzen
			pos = s.find('mehr</strong>')
			s = s[:pos]
			
		# abweichende Struktur, Bsp. https://tokio.sportschau.de/tokio2020/:
		media = ARDSportgetMedia(s)							# Audio, Video
		if media:
			PLog('mit_Video_Audio:')
			tag = media
			summ = stringextract('alt="', '"', s)
		else:			
			PLog('ohne_Video_Audio:')									# ARDSportVideo -> ARDSportSingleTab 
			mediatype=''												# Sofortstart aus
			tag = u'Beitrag hier [COLOR red] ohne Video / Audio[/COLOR] - '
			tag = "%s%s" % (tag, u'eventuell auf der Folgeseite enthalten?')
			if 'programm.ard.de/Programm/Sender' in path:				# PRG-Hinweis ausblenden
				continue		
			if 'uration"' in s:
				duration = 	stringextract('duration">', '<', s)			# Video im Beitrag?
			summ = stringextract('teasertext">', '<strong>', s)

		title = stringextract('class="headline">', '</h', s)
		if title == '':
			title = stringextract('jmDescription">', '</', s)
		if title == '':
			title = stringextract('<span>', '</strong>', s)			# Videosseite: Kleinbeiträge unten
		if title == '':
			title = stringextract('title="', '"', s)				# ev. als Bildtitel

		path = stringextract('href="', '"', s)
		if path.startswith('//'):
			path = "https:" + path
		else:
			if path.startswith('http') == False:
				path = SBASE + path
		if '/Programm/Sender?sender=' in path:						# Programmhinweis
			continue
			
		img	= stringextract('srcset="', '"', s)
		if img == '':
			img = R("tv-ard-sportschau.png")						# Fallback
		img_txt = stringextract('title="', '"', s)
		if img.startswith('//'):									# z.B. //www1.wdr.de/..
			img	= "https:" + img
		if img.startswith('/'):										# z.B. /regional/rbb/..
			img	= SBASE + img
						
		summ		= unescape(summ); summ = mystrip(summ)
		summ		= cleanhtml(summ); summ=repl_json_chars(summ)
		title=title.strip(); summ=summ.strip();							# zusätzl. erf.
		
		if path in path_list:											# Dopplercheck
			continue
		path_list.append(path)
			
		mediaDate=''; mediaDuration=''
		if '"mediaDate"' in s:
			mediaDate = stringextract('mediaDate">', '<', s)		
		if '"mediaDuration"' in s:
			mediaDuration = stringextract('mediaDuration">', '<', s)
			if len(mediaDuration) >= 8:
				mediaDuration = mediaDuration + "Std."
			else:
				mediaDuration = mediaDuration + "Min."
		else:
			mediaDuration = duration
		if mediaDate:
			duration = mediaDate
			if mediaDuration:
				duration = "%s | %s" % (mediaDate, mediaDuration)

		if title == '' or path == '' or path.endswith('#'):
			continue	

		if duration:
			summ = "%s\n\n%s"	 % (duration, summ)
		if SETTINGS.getSetting('pref_load_summary') == 'true':		# Inhaltstext im Voraus laden?
			skip_verf=False; skip_pubDate=False						# beide Daten ermitteln
			summ_txt = get_summary_pre(path, 'ARDSport', skip_verf, skip_pubDate)
			PLog(len(summ)); PLog(len(summ_txt)); 
			if 	summ_txt and len(summ_txt) > len(summ):				# größer als vorher?
				summ = summ_txt
		summ_par = summ.replace('\n', '||')		
		
		title = mystrip(title); title = unescape(title); 
		title = cleanhtml(title); title = repl_json_chars(title)
		if "Video" in title:
			title = title.replace("Video", "[B]Video[/B]")
			
		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					break		
			if filtered:
				continue		
		
		PLog("Satz1:")
		PLog(path); PLog(img); PLog(title); PLog(tag); PLog(summ); 
		title=py2_encode(title)
		path=py2_encode(path); img=py2_encode(img); summ_par=py2_encode(summ_par);
		
		if 'data-more-text="bilder"' in s:
			tagline = "Bildgalerie"
			fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
				quote(path), quote(img))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportBilder", fanart=img, 
				thumb=img, tagline=tagline, fparams=fparams)				
		else:
			if path.endswith('/tokio2020/live/index.html'):	 	# Sonderbehandlung Livestreams Paralympics -> 
				mediatype=''									# ARDSportVideo -> ARDSportEventLive
				tag = "Folgeseite"
			fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'summ': '%s'}" %\
				(quote(path), quote(title), quote(img), quote(summ_par))				
			addDir(li=li, label=title, action="dirList", dirID="ARDSportVideo", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)			
		item_cnt = item_cnt +1	
		
	# Linkliste am Ende auswerten, z.b. ../wintersport/komplette-rennen/index.html,
	# 	im Bsp. 2 Blöcke mit Listen
	PLog('linklist_sendungen:')
	for s in sendungen:													# 'class="teaser"' - s.o.
		if 'class="linklist">' not in s:								# verwertbare Link-Liste
			continue
		img = R('tv-ard-sportschau.png')
		href_list = blockextract('<a href="', s, "</ul>") 				# Liste begrenzen
		for item in href_list:											
			path = SBASE + stringextract('href="', '"', item)
			title = stringextract('jmDescription">', '</span>', item)	# als Titel verwenden
			info1 = stringextract('title="', '"', item)					# Bsp.: "Sportschau, Das Erste"
			info2 = stringextract('<strong>', '</strong>', item)		# Bsp. video
			if title =='' or info2 != 'video':
				continue
			title = repl_json_chars(title)
			summ = "%s | %s | %s" % (info2, info1, title)	

			if SETTINGS.getSetting('pref_load_summary') == 'true':		# Inhaltstext im Voraus laden?
				skip_verf=False; skip_pubDate=False						# beide Daten ermitteln
				summ_txt = get_summary_pre(path, 'ARDSport', skip_verf, skip_pubDate)
				PLog(len(summ)); PLog(len(summ_txt)); 
				if 	summ_txt and len(summ_txt) > len(summ):				# größer als vorher?
					summ = summ_txt
			summ_par = summ.replace('\n', '||')		
			
			PLog("Satz5:")
			PLog(item_cnt)
			PLog(path);PLog(img); PLog(title); PLog(summ); 
			title=py2_encode(title)
			path=py2_encode(path); img=py2_encode(img); summ_par=py2_encode(summ_par);
			fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'summ': '%s'}" %\
				(quote(path), quote(title), quote(img), quote(summ_par))				
			addDir(li=li, label=title, action="dirList", dirID="ARDSportVideo", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, mediatype=mediatype)	
			item_cnt = item_cnt +1	 
										
	if 'tokio.sportschau.de/tokio2020/live/index.html' in  path_org:	# temp.
		channel = u'ARD Event Streams (eingeschränkt verfügbar)'
		ARDSportAudioXML(channel, img='')
		item_cnt=item_cnt+1
											
	PLog(item_cnt)
	if item_cnt == 0:
		msg1 = title_org
		msg2 = u'keine Beiträge gefunden'
		icon = R(ICON_DIR_FOLDER)
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#---------------------------------------------
# Aufrufer: ARDSportPanel mit manuellem Menübutton und Trigger paneltabs 
# Auswertung von Seiten, deren Tabstruktur nicht zu ARDSportPanel
#	passt 
# Bei mehr als 1 main_tabs erfolgt 2. Aufruf  zum Listen der subressorts
# Da im html-Code die href-Listen der Tabs nicht voneinander getrennt sind,
#	gleichen wir die href-Liste (Nutzung Dict) beim 2. Aufruf ab 
#
def ARDSportPanelTabs(title, path, img, tab_path=''):
	PLog('ARDSportPanelTabs: ' + title);
	 
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	if tab_path:
		path = tab_path
	page, msg = get_page(path)	
	if page == '':
		msg1 = 'ARDSportPanelTabs: Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))
	
	parsed = urlparse(path)
	base = 'https://' + parsed.netloc
	if base.endswith('/'):
		base = base[:len(base)-1]				# Bsp.: https://tokio.sportschau.de
	PLog("base: " + base)
	
	main_tabs =  blockextract('class="desktop">', page)
	if tab_path == '':							# 1. Aufruf
		href_list=[]							# Abgleich nächster Tab (2. Aufruf)
		for main_tab in main_tabs:
			line = stringextract('class="desktop">', '</span>', main_tab)
			href = stringextract('href="', '"', line)
			title = cleanhtml(line)
			if href.startswith('http') == False:
				href = base + href	
			href_list.append(href)		
		
			PLog("Satz10:")
			PLog(title); PLog(href); 
			title=py2_encode(title); path=py2_encode(path); img=py2_encode(img); 
			fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s', 'tab_path': '%s'}"	%\
				(quote(title), quote(path), quote(img), quote(href))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportPanelTabs", fanart=img, 
				thumb=img, fparams=fparams)	
		Dict("store", 'ARDSport_href_list', href_list)				
	else:										# 2. Aufruf
		found=False; tabpanel=''
		href_list = Dict("load", 'ARDSport_href_list')	
		PLog(href_list)			
		for main_tab in main_tabs:				# Tab via href suchen
			line = stringextract('class="desktop', '</span>', main_tab)
			href = stringextract('href="', '"', line)
			if href.startswith('http') == False:
				href = base + href
			PLog('href: ' + href)	
			if href in tab_path:
				PLog('tab_found')
				PLog(len(main_tab))
				found=True
				href_list.remove(href)			# akt. href aus Abgleich-Liste entfernen
				break
		
		# tabpanel enthält subressorts aller tabs. Nur der letzte enthält nur die eigenen -
		#	bei den übrigen Stop sobald der erste Link des nächsten tab erreicht ist (Abgleich
		#	href_list)
		# 	Doppler (bei Klapp-tabs) werden via path_list ausgefiltert. 
		#	z.B. paralympics in ../tokio.sportschau.de/tokio2020/paralympics/index.html
		if found:								# subressorts des Tab listen 	
			if '<!-- mnHolder -->' in main_tab:			# letzter Tab
				tabpanel = stringextract('class="desktop">', '<!-- mnHolder -->', main_tab)
			else:										# nächster Tab
				tabpanel = stringextract('class="desktop">', 'class="firstlevel">', main_tab)
			PLog(len(tabpanel))
			PLog(tabpanel[:80])
			link_list = blockextract('<li>', tabpanel, '</a>')
			PLog(len(tabpanel))
			
			path_list=[];							# Dopplercheck 
			for link in link_list:
				PLog(link[:200])
				href = base + stringextract('href="', '"', link)
				title=cleanhtml(link); title=mystrip(title); title=unescape(title)
				if href in href_list:				# Links des nächsten tab erreicht
					break
				
				if href in path_list:				# Dopplercheck
					continue
				path_list.append(href)
						
				PLog("Satz11:")
				PLog(title); PLog(href);
				title=py2_encode(title); href=py2_encode(href);	img=py2_encode(img);	
				fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (quote(title), 
					quote(href), quote(img))
				addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
					thumb=img, fparams=fparams)			
				 
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#--------------------------------------------------------------------------------------------------
# BUNDESLIGA IM ARD-HÖRFUNK
# img: radio-livestreams.png
# path: sportschau.de/sportimradio/bundesligaimradio102.html
#
def ARDSportHoerfunk(title, path, img):
	PLog('ARDSportHoerfunk:'); 
	fanimg = img
	base = "https://www.sportschau.de"

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'ARDSportHoerfunk: Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))
	
	content = blockextract('class="teaser"', page)	
	PLog(len(content))
	
	ID = "ARDSportHoerfunk"; tag = title
	for rec in content:
		if '"Javascript-Fehler"' in rec:				# Info Javascript-Fehler
			continue
		href = base + stringextract('href="', '"', rec)
		img = stringextract('srcset="', '"', rec)
		if img.startswith('http') == False:
			img = base + img
		title = stringextract('Audio:</span>', '</h4>', rec)
		title=cleanhtml(title); title=title.strip(); title=repl_json_chars(title); 
		summ = stringextract('teasertext">', '<strong>', rec)
		summ = summ.replace('&nbsp;|&nbsp;', ''); summ=mystrip(summ)
		summ=repl_json_chars(summ);  
			
		PLog("Satz18:");PLog(title);PLog(href);PLog(img);PLog(summ[0:40]);
		title=py2_encode(title); href=py2_encode(href);
		img=py2_encode(img); summ=py2_encode(summ); tag=py2_encode(tag);
		
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'tag': '%s', 'summ': '%s', 'ID': '%s'}" %\
			(quote(href), quote(title), quote(img), quote(tag), quote(summ), ID)				
		addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioStreamsSingle", fanart=fanimg, 
			thumb=img, fparams=fparams, tagline=tag, summary=summ)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
						
#--------------------------------------------------------------------------------------------------
# Liste der ARD Audio Event Streams in livesenderTV.xml
#	-> SenderLiveListe -> SenderLiveResolution (Aufruf
#	einz. Sender)
#
def ARDSportAudioXML(channel, img=''):
	PLog('ARDSportAudioXML:') 
	PLog(channel)

	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender='')
	return
#--------------------------------------------------------------------------------------------------
# Bilder für ARD Sportschau, z.B. Moderatoren
# Einzelnes Listitem in Video-Addon nicht möglich - s.u.
# Slideshow: ZDF_SlideShow
def ARDSportBilder(title, path, img):
	PLog('ARDSportBilder:'); 
	PLog(title); PLog(path)
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))
	
#	content = blockextract('class="teaser"', page)	
	content = blockextract('class="teaser', page)	
	PLog(len(content))
	if len(content) == 0:										
		msg1 = 'Keine Bilder gefunden.'
		PLog(msg1)
		msg2 = 'Seite:'
		msg3 = path
		MyDialog(msg1, msg2, msg3)
		return li
		
	fname = make_filenames(title)			# Ablage: Titel + Bildnr
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
				
	SBASE = 'https://www.sportschau.de'
	image = 0; background=False; path_url_list=[]; text_list=[]
	for rec in content:
		pos = rec.find('<!-- googleon: all -->')	# "Javascript-Fehler" entfernen
		if pos > 0:
			rec = rec[pos:]
			
		# größere Bilder erst auf der verlinkten Seite für einz. Moderator		
		img_src		= stringextract('srcset="', '"', rec)				# erste = größtes Bild
		if img_src.startswith('//'):									# //www1.wdr.de/..
			img_src	= 'https:' + img_src
		else:															# /sendung/moderatoren/
			img_src	= SBASE + img_src
		if img_src == 'https://www.sportschau.de':
			continue
			
		headline	= stringextract('Fotostrecke:</span>', '</', rec)	# z.B. Name
		headline	= mystrip(headline); headline = unescape(headline)
		summ		= stringextract('teasertext">', '<strong>', rec)
		summ		= mystrip(summ); summ = unescape(summ); summ = cleanhtml(summ)
		summ		= repl_json_chars(summ)
		title=summ.strip()
		
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
			summ = unescape(summ)
			
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
		
		lable = u"Alle Bilder löschen"						# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#--------------------------------------------------------------------------------------------------
# Die Videoquellen des WDR sind in SingleSendung nicht erreichbar. Wir laden
#	die Quelle (2 vorh.) über die Datei ..deviceids-medp-id1.wdr.de..js und
#	übergeben an PlayVideo.
# 26.11.2021 neu nach Änderungen der ARD: Videoquellen: Dekodierung hier - nicht in get_page. 
#	Video-/Audioquellen: Webseite (json embedded, wdr-Link, iframe-Link), Videolink 
#	(Endung .js) -> json-Datei mit Quellen, Videolink (Endung .html, enthalten: 
#	'-ardplayer_image) -> zusammengesetzt zu json-Link).
#	Die Quellen enthalten jeweils unterschiedl. Sets an m3u8-, mp4, -mp3-Quellen, häufig nur
#		1 Quelle.
# Fallback ohne Quellen: Webseiten mit 'media mediaA video' -> ARDSportSingleTab
# Besonderheit: bei einigen Seiten scheitert utf-8-Dekodierung in util. Daher Dekodierung 
#	hier mit py2_decode
#	
def ARDSportVideo(path, title, img, summ, Merk='false'):
	PLog('ARDSportVideo:'); 
	PLog(summ)
	summ = summ.replace('||||', ' | ')

	title_org = title
	# Header erforder.?: /wintersport/alle-videos-komplett-uebersicht-100.html
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}"
	page, msg = get_page(path=path, header='', decode=True)		# decode hier i.V.m. py2_decode 						
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return 
	PLog(len(page))
	page=py2_decode(page)					

	'''
	# Livestream-Problematik 
	# todo: für nächstes Großereignis anpassen
	#	s. Forum https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF Post 472ff
	# Button ist Behelfslösung für Frauen-Fußball-WM - url via chrome-developer-tools ermittelt
	# Button ist zusätzl. dauerhaft im Menü ARD Sportschau (Livestream 3) platziert.
	if "/frankreich2019/live" in path:
		url = "https://ndrspezial-lh.akamaihd.net/i/spezial_3@430237/master.m3u8"
		summ = 'bitte die FRAUEN WM 2019 Livestreams testen, falls dieser nicht funktioniert'
		mediatype = 'video'
		url=py2_encode(url); title=py2_encode(title); img=py2_encode(img); summ=py2_encode(summ);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	'''

	if path.endswith('/tokio2020/live/index.html'):					# Sonderbehandlung Livestreams Paralympics
		ARDSportEventLive(path, page, title)						# für künft. Events prüfen (aktuell OK)
		return
		
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
		if page.find('class="media mediaA videoLink') < 0:
			if 'class="media mediaA video' in page:					# ohne Quellen, aber Videos gefunden
				ARDSportSingleTab(title, path, img, page)			# -> ARDSportSingleTab
				return
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
		else:
			if '"videoURL" : "' in page:						# Quellen in Seite eingebettet					
				PLog('detect_videoURL:')
				# Je ein HLS + MP4-Link direkt auf der Seite im json-Format
				# Bsp.: www.sportschau.de/tor-des-monats/archiv/april2017tdm100.html
				page = stringextract('"mediaResource"', '</script>', page)	# json-Inhalt ausschneiden
				PLog("page_web: " + page[:100])
				video_src=''									# skip 	'-ardplayer_image-' in video_src
			else:
				msg1 = u'Leider kein Video gefunden: %s' % title # keine Chance auf Videoquellen
				msg2 = path
				MyDialog(msg1, msg2, '')
				return
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	if video_src.endswith('.js'):									# //deviceids-medp-id1.wdr.de/../2581397.js
		page, msg = get_page(video_src)								# json mit (nur) Videoquellen laden
		
	if '"videoURL' in page or '"audioURL' in page:
		page = page.replace('":"', '" : "')						# Anpassung an Web-embedded json
		video_src=''
		
	m3u8_url=''; mp_url=''; title_m3u8=''; title_mp=''					# mp_url: mp4 oder mp3
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
		
		mp 	= stringextract('quality": 3', 'cdn"', page)		# mp4-HD-Quality od. mp3
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
			if url.endswith('master.m3u8'):
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
		PlayVideo(url=m3u8_url, title=title_m3u8, thumb=img, Plot=summ, sub_path="")
		return
	
	PLog("Satz27:")
	PLog("m3u8_url: " + m3u8_url); PLog(title_m3u8);
	PLog(title_mp); PLog("mp_url: " + mp_url)
	
	m3u8_url=py2_encode(m3u8_url); title_m3u8=py2_encode(title_m3u8); 
	title_mp=py2_encode(title_mp); 
	img=py2_encode(img); summ=py2_encode(summ);
	if m3u8_url:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': ''}" %\
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

#------------------------------------
# 24.11.2021 bisher nur Fallback für ARDSportVideo (direkt): ohne  Quellen, 
#	aber Videos vorhanden
#
def ARDSportSingleTab(title, path, img, page=''):
	PLog('ARDSportSingleTab:')
	
	SBASE = 'https://www.sportschau.de'
	sendungen = blockextract('class="teaser">', page)	# <strong>video
	PLog(len(sendungen))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	for s in sendungen:
		if '"Javascript-Fehler"' in s:								# Info Javascript-Fehler
			continue
		media = ARDSportgetMedia(s)									# Audio, Video - markiert
		if media == '':
			PLog('ohne_Video_Audio:')
			continue
		
		styp = media			
		path = stringextract('href="', '"', s)	
		if 'avascript:void(0)' in path:
			continue			
		if path.startswith('http') == False:
			path = SBASE + path
		title = stringextract('data-pre-headline="', '"', s)
		if title == '':
			title = stringextract('title="', '"', s)				# Altern. in href
		title=repl_json_chars(title);
		
		img	= stringextract('srcset="', '"', s)
		img_txt = stringextract('title="', '"', s)
		img_txt=unescape(img_txt);
		
		if img.startswith('//'):									# z.B. //www1.wdr.de/..
			img	= "https:" + img
		if img.startswith('/'):										# z.B. /regional/rbb/..
			img	= SBASE + img
		mediaDate = stringextract('mediaDate">', '<', s)	
		mediaDuration = stringextract('mediaDuration">', '<', s)
		tag = img_txt
		tag=styp
		if mediaDate and mediaDuration:
			tag = "%s | [B]%s | %s[/B]" % (tag,mediaDate, mediaDuration)
		if img_txt:
			tag = "%s\n\nBild: %s" % (tag, img_txt)
		
		summ = stringextract('teasertext">', '<strong>', s)
		summ=mystrip(summ); summ=cleanhtml(summ); 
		summ = summ.replace('&nbsp;|&nbsp;', ''); summ=repl_json_chars(summ);  
		summ_par = summ.replace('\n', '||')		
		
		PLog("Satz26:")
		PLog(path); PLog(img); PLog(title); PLog(summ); 
		title=py2_encode(title)
		path=py2_encode(path); img=py2_encode(img); summ_par=py2_encode(summ_par);
		
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'summ': '%s'}" %\
			(quote(path), quote(title), quote(img), quote(summ_par))				
		addDir(li=li, label=title, action="dirList", dirID="ARDSportVideo", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
	
#------------------------------------
# Sonderbehandlung Livestreams Paralympics
# page (aktuell): https://tokio.sportschau.de/tokio2020/live/index.html - kein
#	verwertbarer Inhalt (Streambezüge komplett js-generiert)
# pgm_id osslive100: Sportschau
# pgm_id osslive102: Einzelsendung
# 2. Durchlauf mit oss_url -> PlayVideo
# anpassen: path in ARDSportVideo
def ARDSportEventLive(path, page, title, oss_url='', url='', thumb='', Plot=''):		
	PLog('ARDSportEventLive:')
	PLog(path); PLog(oss_url);
	title_org=title
		
	if oss_url:															# 2. Durchlauf
		page, msg = get_page(path=oss_url)
		if page == '':
			msg1 = "Fehler in ARDSportEventLive" 
			msg2 = "%s nicht gefunden"	% oss_url.split('/')[-1]
			msg3 = msg
			PLog(msg2)	
			MyDialog(msg1, msg2, msg3)
			return 
		
		url = stringextract('"_stream": "', '"', page)
		tag, descr = Plot.split('||||')
		PLog(url); PLog(tag); PLog(descr[:80]) 
		
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD')						# Home-Button
		
		img=py2_encode(thumb); Plot=py2_encode(Plot); 
		title=py2_encode(title); url=py2_encode(url);		
		
		if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true': 	# Sofortstart
			PLog('Sofortstart: ARDSportEventLive')
			PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
			PlayVideo(url=url, title=title, thumb=img, Plot=Plot)
			#xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			return

		if url.endswith('master.m3u8'):
			li = Parseplaylist(li=li, url_m3u8=url, thumb=thumb, geoblock='', descr=Plot)
		else:		
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
				(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(Plot))
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
				tagline=tag, summary=descr) 
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return
		
	#------------------------------------------------------------------	# 1. Durchlauf	
	#img = "https://tokio.sportschau.de/tokio2020/olympiastadiontokio100_v-original.jpg"
	# Bsp. 	path: "https://tokio.sportschau.de/tokio2020/live/index.html",
	#		path: "https://tokio.sportschau.de/tokio2020/paralympics/live/livestreams180.html"
	# json-Inhalt für beide Beisp. identisch	
	base = "%s/live" % path.split('/live/')[0]
	page, msg = get_page(path=base + "/lcconfig110-extappjson.json")	# Liste zusätzl. json-Dateien
	if page == '':
		msg1 = "Fehler in ARDSportEventLive" 
		msg2 = "lcconfig110-extappjson.json nicht gefunden"
		PLog(msg2)	
		MyDialog(msg1, msg2, '')
		return 
	
	url = stringextract('"additionalTitleClass":"","url":"', '"', page)	# livestreams184-extappjson.json (channels)	
	url = base + url
	page, msg = get_page(path=url)
	if page == '':
		msg1 = "Fehler in ARDSportEventLive" 
		msg2 = "%s nicht gefunden" % url.split('/')[-1]
		PLog(msg2)	
		MyDialog(msg1, msg2, '')
		return	
				
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	

	channels  = blockextract('"starttime":', page)						# Beiträge
	PLog(len(channels))
	# Bsp: "/paralympics/live/osslive102-ardjson_image-36c61add-66fc-4fd8-8050-126ef2095659.json":
	oss_url_templ = base + "/paralympics/live/%s-ardjson_image-%s.json"
	now = EPG.get_unixtime(onlynow=True)								# akt. Zeit für Abgleich
	now = int(now)
	now_human = epgRecord.date_human("%Y.%m.%d_%H:%M:%S", now='')		# Debug	
	PLog("now_human: " + now_human)
	live_flag=False
	for rec in channels:
		start = stringextract('"starttime": ', ',', rec)				# Unix-Time
		end = stringextract('"endtime": ', ',', rec)					# 	-"-
		PLog("start, end: %s, %s" % (epgRecord.date_human("%Y.%m.%d_%H:%M:%S", now=start), 
			epgRecord.date_human("%Y.%m.%d_%H:%M:%S", now=end)))
		start=int(start); end=int(end); 
		if end < now:													# abgelaufen
			continue
		
		datum = stringextract('"displaystartdate": "', '"', rec)	 
		zeitstart = stringextract('"displaystarttime": "', '"', rec)	 
		zeitende = stringextract('"displayendtime": "', '"', rec)
		headline = stringextract('"headline": "', '"', rec)	 
		sender = stringextract('"channel": "', '"', rec)	 
		pgm_id = stringextract('"pgm_id": "', '"', rec)	 
		descr = stringextract('"description": "', '"', rec)	 
		img = base + stringextract('"displayimage": "', '"', rec)	 
		image_uuid = stringextract('"displayimage_uuid": "', '"', rec)	 
		mod = stringextract('"moderation": "', '"', rec)
		if mod == '':
			mod = stringextract('"reporter": "', '"', rec) 
		mod = mod.replace('\\t', '')									# italic entf.
	
		title = repl_json_chars(headline); descr= repl_json_chars(descr)
		if now >= start and now <= end:									# Zeitabgleich für Titel
			title = '[COLOR red][B]  LIVE [/B][/COLOR] | %s' % (title)
			live_flag=True
		else:
			title = '[B]%s[/B] | %s' % (datum, title)
			
		tag = '[B]Start: %s, %s[/B] | Ende: %s | %s' % (datum, zeitstart, zeitende, mod)
		Plot = "%s||||%s" %  (tag, descr)
		oss_url = oss_url_templ % (pgm_id, image_uuid)
		
		PLog("Satz2:")
		PLog(title); PLog(pgm_id); PLog(image_uuid); PLog(oss_url); PLog(Plot[:80]);
		
		img=py2_encode(img); Plot=py2_encode(Plot); 
		title=py2_encode(title); oss_url=py2_encode(oss_url);
		
		fparams="&fparams={'path': '', 'page': '', 'oss_url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
			(quote(oss_url), quote(title), quote(img), quote(Plot))
		addDir(li=li, label=title, action="dirList", dirID="ARDSportEventLive", fanart=img, thumb=img, fparams=fparams, 
			tagline=tag, summary=descr) 
			
	if live_flag == False:
		icon = R("icon-info.png")
		msg1 = "Derzeit keine Livestreams"
		xbmcgui.Dialog().notification(msg1,'',icon,2000)	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#--------------------------------------------------------------------------------------------------
# spez. Pocastseiten, z.B. www.sportschau.de/tourfunk/index.html bei Tour de France
#	Inhalte collapsed, mp3-Link als Download-Button eingebettet
# Aufrufer: ARDSportPanel
def ARDSportPodcast(path, title):
	PLog('ARDSportPodcast:'); PLog(path)
	
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(len(page))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	img = R(ICON_SPEAKER)
	items = blockextract('class="infotext">', page)				# Verzicht auf Mini-Icons (außerhalb)
	for item in items:
		dl_button = stringextract('class="button download', 'Download">', item)
		mp3_url = stringextract('href="', '"', dl_button)
		if ".mp3" in mp3_url == False:
			continue
		if mp3_url.startswith("//"):
			mp3_url = "https:" + mp3_url
			
		mediaTitle = stringextract('mediaTitle">', '</span>', item)
		mediaSerial = stringextract('mediaSerial">', '</span>', item)
		mediaDate = stringextract('mediaDate">', '</span>', item)
		dur = stringextract('mediaDuration">', '</span>', item)
		exp = stringextract('mediaExpiry">', '</span>', item)
		sender = stringextract('mediaStation">', '</span>', item)
		summ = stringextract('class="text">', '</p>', item)
		summ_par= summ.replace('\n', '||')
		
		mediaTitle=cleanhtml(mediaTitle); mediaSerial=cleanhtml(mediaSerial)
		mediaDate=cleanhtml(mediaDate); dur=cleanhtml(dur)
		exp=cleanhtml(exp); sender=cleanhtml(sender)
		
		title=repl_json_chars(mediaTitle); 
		tag="%s: %s, %s | [COLOR darkgoldenrod]%s[/COLOR]" % (mediaSerial, mediaDate, dur, exp)
		
		
		PLog("Satz9")
		PLog(title); PLog(mp3_url); PLog(summ[:80]); PLog(tag[:80]);
		
		title=py2_encode(title); mp3_url=py2_encode(mp3_url);
		img=py2_encode(img); summ_par=py2_encode(summ_par);	
		ID="ARD"													# ID Home-Button
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'ID': '%s'}" % (quote(mp3_url), 
			quote(title), quote(img), quote_plus(summ_par), ID)
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#--------------------------------------------------------------------------------------------------
# erste Menüebene für umfangr. Tabellen in ARDSportTable - bisher "/ergebnisse/", 
#	"/ergebnisse_tabellen/"
# page: 'class="conHeadline">' .. 'sectionArticle'
# 1. Durchlauf (ohne clap_title): Liste der Klappentitel
# 2. Durchlauf: Eventtitel mit Unterevents (s. Radsport)
#
#
def ARDSportTablePre(base, img, clap_title=''):
	PLog('ARDSportTablePre:'); 
	PLog(clap_title)
	
	page = Dict("load", 'ARDSportTable')
	clap_list =  blockextract("data-ctrl-klappe-entry", page)	# Klappen: BIATHLON, SKI ALPIN..
	PLog("clap_list %d" % len(clap_list))
	
	if clap_title == '':										# 1. Durchlauf: Klappentitel
		li = xbmcgui.ListItem()
		li = home(li, ID='ARD')					# Home-Button
		for clap in clap_list:
			clap_title = stringextract('title="', '"', clap)
			clap_title = unescape(clap_title)
			
			PLog("Satz6_1:")
			PLog(clap_title); 
			clap_title=py2_encode(clap_title);
			fparams="&fparams={'base': '%s', 'img': '%s', 'clap_title': '%s'}"	%\
				(quote(base), quote(img), quote(clap_title))
			addDir(li=li, label=clap_title, action="dirList", dirID="ARDSportTablePre", fanart=img, 
				thumb=img, fparams=fparams)
		
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
		return 
						
	# -----------------------------------------					# 2. Durchlauf: Eventtitel 
	PLog("clap_title: " + clap_title)
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	clap_title_org=clap_title; found=False
	clap=''
	for clap in clap_list:
		clap_title = stringextract('title="', '"', clap)
		clap_title = unescape(clap_title)
		if clap_title_org in clap_title:
			PLog("gefunden: %s" % clap_title)
			found = True
			break
			
	if found == False:
		msg1 = "Tabelle nicht gefunden: %s"	% clap_title_org
		MyDialog(msg1, '', '')	
		return li			
	
	h3_cnt=0
	h3_list =  blockextract("<h3>", clap, "</ul>")		# Groß-Events: WELTCUP, OLYMPIA..
	if len(h3_list) == 0:								# ohne Groß-Events
		h3_list =  blockextract("<h2>", clap, "</ul>")
	PLog("h3_list %d" % len(h3_list))
	for h3 in h3_list:
		h3_cnt=h3_cnt+1
		h3_title = stringextract('<h3>', '</h3>', h3)
		if h3_title == '':								# ohne Groß-Events
			h3_title = stringextract('<h2>', '</h2>', h3)
		if h3_cnt % 2 == 0:								# Farbwechsel h3_title
			h3_col = "red"
		else:
			h3_col = "blue"
		
		li_list = blockextract("<li>", h3, "</li>")
		PLog("li_list %d" % len(li_list))
		for item in li_list:
			table_path = base + stringextract('href="', '"', item)
			li_title=cleanhtml(item); li_title=li_title.strip()# Wettkampf
			title = u"%s | [COLOR %s]%s[/COLOR] | %s" %\
				(clap_title, h3_col, h3_title, li_title)
			title = unescape(title)
			tag = title	
			inf = u"aktuelle Saison, letzter Spieltag.\nÄltere Ergebnisse s. sportschau.de, Tab Ergebnisse"
			tag = u"%s\n\n%s" % (tag, inf)
			
			PLog("Satz6_2:")
			PLog(clap_title); PLog(h3_title); PLog(li_title);
			title=py2_encode(title); table_path=py2_encode(table_path)
			fparams="&fparams={'path': '', 'title': '%s', 'table_path': '%s'}"	%\
				(quote(title), quote(table_path))
			addDir(li=li, label=title, action="dirList", dirID="ARDSportTable", fanart=img, 
				thumb=img, tagline=tag, fparams=fparams)
					
						
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#--------------------------------------------------------------------------------------------------
# extrahiert Medaillenspiegel auf sportschau.de (einheitl. Aufbau)
#	Bsp.: https://www.sportschau.de/biathlon-wm/medaillenspiegel/index.html (Options-Feld),
#		https://www.sportschau.de/wintersport/ergebnisse/index.html (Klapp-Listen)
#	Home in ARDSportPanel
# 1. Durchlauf (ohne table_path): Param. für die einz. Tabellen ermitteln
#	Übersicht abweichend: Klapp-Listen, Options-Feld
# 2.  Durchlauf (mit table_path): Seite laden + Tabelle im Textviewer darstellen
# 
def ARDSportTable(path, title, table_path=''):
	PLog('ARDSportTable:'); 
	
	if table_path:
		path = table_path
	page, msg = get_page(path)
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
	PLog(len(page))
	
	img = R(ICON_DIR_FOLDER)
	base = "https://www.sportschau.de"
	
	# ----------------------------------------------------------			# 1. Durchlauf
	if table_path == '':
		# "ergebnisse" deckt ab: "/ergebnisse/", "/ergebnisse_tabellen/"
		if "ergebnisse" in path:										# 1.1 abweichende Übersicht (Klapp-Listen)
			PLog('pass1_lists:')
			page = stringextract('class="conHeadline">', 'sectionArticle', page)		
			Dict("store", 'ARDSportTable', page) 
			ARDSportTablePre(base, img)									# erste Menüebene außerhalb
			return
		
		PLog('pass1_optionfields:')													# 1.2 Übersicht in Options-Feld
		# Tabellen-Übersicht auf jeder Seite vorh. (selected="selected") :
		page = stringextract('class="siteHeadline', '<thead', page) # Tab-Übersicht ausschneiden
		form_url = stringextract('form action="', '"', page)					# .jsp-Url
		id_name =  stringextract('onchangesubmit', '<optgroup', page)	# -> table_path
		id_name =  stringextract('name="', '"', id_name) 
		eap = stringextract('"eap" ', '/>', page)						# -> table_path
		eap = stringextract('value="', '"', eap)

		optgroups = blockextract("<optgroup", page, "</optgroup>")
		for item in optgroups:
			label  = stringextract('label="', '"', item)			# Haupt-Titel
			options = blockextract("<option ", item, "</option>")	# Unter-Titel
			option_list=[]
			for option in options:
				op = stringextract('value="', '"', option) 			# Bsp. value="bi|wc|Einzelrennen"
				s = cleanhtml(option)
				title = "%s: %s" % (label, s)
				tag = "Tabelle %s" % s
				
				# <input name="_sportart" value="ws",   <input name="eap" 
				liga = '?%s=%s&_sportart=ws&eap=%s' % (id_name, op, eap) # Bez. ws + eap bei Bedarf auslesen
				liga = (liga.replace('|', '%7C').replace('/', '%2F'))# Quoting: | und /
				table_path = base + form_url + liga
				
	
				PLog("Satz6_3:")
				PLog(title);PLog(label); PLog(table_path);
				title=py2_encode(title); table_path=py2_encode(table_path)
				fparams="&fparams={'li': '%s', 'path': '', 'title': '%s', 'table_path': '%s'}"	% (li,
					quote(title), quote(table_path))
				addDir(li=li, label=title, action="dirList", dirID="ARDSportTable", fanart=img, 
					thumb=img, tagline=tag, fparams=fparams)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return li
		
	# ----------------------------------------------------------			# 2. Durchlauf: einz. Tabelle
	PLog('pass2:')
	table = stringextract("<table", "</table>", page)
	if table == '':
		msg1 = 'keine Tabelle gefunden.'
		msg2 = title
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(table))
	
	# die unterschiedl. Zeichensätze in Header + Zeilen verhindern im Texviewer
	#	die Überstimmung. Die hier verwend. Werte sind Näherungswerte.
	# Bei der großen Ergebnisseite (außerhalb Wintersport) müssen Spaltengrenzen entfallen,
	#	um Infos zu erhalten. Das betrifft auch verdeckte Bezeichner (Bsp. Halbzeitstand) -
	#	Folge: Zeilenumbruch
	width_def = "Default|%10s#Default|%20s"								# Defaults
	PLog("width_def: " + width_def)
	width_list = [u"Rang|%8s#Rang|%10s", u"Name|%26s#Name|%20s", 		# "Header#Zeile"
				u"Land|%22s#Land|%14s", u"Team|%22s#Team|%14s", 
				u"Punkte|%20s#Punkte|%10s", u"Lauf|%20s#Lauf|%7s",
				u"Minuten|%10s#Minuten|%7s", u"Pkt|%20s#Pkt|%10s",
				u"Informationen|%20s#Informationen|%10s",				# ab hier Tabs != Wintersport
				u"Tag|%10s#Tag|%10s", u"Ergebnis|%20s#Ergebnis|%40s",	# Ergebnis: einschl. Halbzeitstand
				u"Begegnung|%20s#Begegnung|%40s"]
	table = re.sub(r"\s+", " ", table)
	hzeile  = stringextract('class="headlines"' , '</tr>', table)		# Tabelle-Header-Zeile
	hzeile  = blockextract('<th', hzeile, '</th>')
	PLog(len(hzeile)); PLog(str(hzeile))
	headline = stringextract('"conHeadline">' , '</', page)				# Event-Titel
	headline = unescape(headline)
	stand = stringextract('</table>' , '</div>', page)					# Schlusszeile
	stand = cleanhtml(stand)
	
	htitle=''
	cnt=0; width_list2=[]												# width_list2: Tabbreite in Zeilen
	for d in hzeile:
		PLog(d)
		td = stringextract('scope="col">', '</th>', d)
		if 'title="' in td:
			td = stringextract('title="' , '"', td)
		else:
			td = cleanhtml(d)
		td = cleanhtml(d)
		td = td.strip()
		for w in width_list:
			s=td
			PLog(">%s<" % td)
			default=True							
			if td in w:
				tab_h, tab_z = w.split("#") 								# "Rang|%10s#Rang|%10s"	
				bez, svar = tab_h.split("|")								# "Rang|%5s"
				td_width = re.search('\d+', svar).group(0)
				td_width = int(td_width)
				width_list2.append(w)
				default=False
				break
		if default:	
			if 'nolimit' in width_def:									# s ohne Begrenzung
				 svar = "%s    "										# + 4 Blanks Abstand
				 td_width = len(s)
			else:
				tab_h, tab_z = width_def.split("#") 						# "Default|%15s#Default|%15s"	
				bez, svar = tab_h.split("|")								# "Default|%15s"
				td_width = re.search('\d+', svar).group(0)
				td_width = int(td_width)
				width_list2.append(width_def)
		s = svar % td[:td_width]		
		htitle = htitle +s
		cnt=cnt+1
			
	htitle = "%s\n[COLOR red] %s [/COLOR]" % (headline, htitle)			# max. 2 Zeilen
	htitle = htitle.replace('<span class="hi ', '')
	PLog("htitle: " + htitle)

	zeilen = blockextract('<tr', table, '</tr>')
	PLog(len(zeilen))
	zeilen = hzeile + zeilen

	line=''; 
	for z in zeilen:													# Zeilen
		#print z[:80]
		if '<td' in z and  '</td>' in z:
			spalten = blockextract('<td', z, '</td>') 
			s_anz = len(spalten)
			cnt=0;
			for s in spalten:				# Spalten-Data
				s_bak = s
				s=cleanhtml(s); s=unescape(s); s=mystrip(s)
				if s.strip() == '' and 'title="' in s_bak:				# Länder-Bez.
					s = stringextract('title="' , '"', s_bak)
					s=unescape(s);
				
				PLog("width_def: "+ width_def)
				if 'nolimit' in width_def:								# s ohne Begrenzung
					# pass
					s = "%s    " %s										# + 4 Blanks Abstand
				else:
					if width_list2:
						w = width_list2[cnt]
					else:
						w = width_def
					tab_h, tab_z = w.split("#") 							# "Rang|%10s#Rang|%10s"	
					bez, svar = tab_z.split("|")							# "Rang|%5s"
					td_width = re.search('\d+', svar).group(0)
					td_width = int(td_width)
					s = svar % s[:td_width]
				
				line = line + s
				cnt=cnt+1
			line = (line.replace('Statistik', '').replace(' gegen : ', ' : ')
				.replace('Endstand', '').replace('Halbzeitstand', '')
				.replace(': zu', ':'))
					
			line = line + "\n"
				
	new_table = "%s\n\n%s" % (htitle, line)
	ShowText(path='', title=htitle, page=line)

	return	# GetDirectory-Error, dafür Verbleib in Liste				
	#xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#----------------------------------------------------------------
# aktuelle LIVESTREAMS + Netcast-Audiostreams-Liste von sportschau.de
# Aufrufer: ARDAudioEventStreams
#
def ARDSportAudioStreams(title, path, img, ID):
	PLog('ARDSportAudioStreams:')
	CacheTime = 60 * 60								# 1 Std.
	base = "https://www.sportschau.de"
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	
	page = Dict("load", ID, CacheTime=CacheTime)
	if page == False or page == '':								# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", ID, page) 								# Seite -> Cache: aktualisieren	
	if page == '':
		msg1 = "Fehler in ARDSportAudioStreams"
		msg2 = 'Seite kann nicht geladen werden.'
		msg3 = msg
		MyDialog(msg1, msg2, msg3)
		return li 						
	
	if "aktuelle Livestreams" in title:							# aktuelle LIVESTREAMS				
		page = stringextract('Livestreams',  'class="conHeadline">', page)
		items = blockextract('class="teaser">', page)
		imgbase = "https://www.sportschau.de"
	else:														# Netcast-Audiostreams-Liste 
		items = blockextract('class="teaser hideTeasertext">', page)
		imgbase = "https:"
		
	PLog(len(items))
	for item in items:
		href = base + stringextract('href="', '"', item)
		title = stringextract('title="', '"', item)			# in href-tag
		img	= imgbase + stringextract('srcset="', '"', item)
		summ = stringextract('teasertext">', '&nbsp', item)
		summ = mystrip(summ); summ = repl_json_chars(summ)
		'''
		if SETTINGS.getSetting('pref_load_summary') == 'true':		# Inhaltstext im Voraus laden?
			pattern ='Description" content="|"' 
			summ_txt = get_summary_pre(href, 'ARDSportSingle', pattern=pattern)
			if summ_txt:
				summ = "%s\n%s" % (summ, summ_txt)
		'''
		
		summ_par = summ.replace('\n', '||')
		
		mediaSerial = stringextract('mediaSerial">', '<', item)		
		mediaDate = stringextract('mediaDate">', '<', item)		
		mediaDuration = stringextract('mediaDuration">', '<', item)
		if mediaDuration == '':
			mediaDuration = "Dauer unbekannt"
		mediaStation = stringextract('mediaStation">', '<', item)
		tag = "%s | [B]%s[/B] | %s | %s" % (mediaSerial, mediaDate, mediaDuration, mediaStation)
		
		PLog("Satz12:")
		PLog(path);PLog(img); PLog(title); PLog(summ); 
		title=py2_encode(title); href=py2_encode(href); img=py2_encode(img);
		tag=py2_encode(tag); summ_par=py2_encode(summ_par);
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'tag': '%s', 'summ': '%s', 'ID': '%s'}" %\
			(quote(href), quote(title), quote(img), quote(tag), quote(summ_par), ID)				
		addDir(li=li, label=title, action="dirList", dirID="ARDSportAudioStreamsSingle", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)	
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#----------------------------------------------------------------
# Audioquelle in Javascript ermitteln
# Aufrufer: ARDSportAudioStreams (Netcast-Audiostreams-Liste,
#	aktuelle LIVESTREAMS)
#
def ARDSportAudioStreamsSingle(title, path, img, tag, summ, ID):
	PLog('ARDSportAudioStreamsSingle: ' + path)
	
	li = xbmcgui.ListItem()

	page, msg = get_page(path=path)
	if page == '':
		msg1 = "Fehler in ARDSportAudioStreamsSingle"
		msg2 = 'Seite kann nicht geladen werden.'
		msg3 = msg
		MyDialog(msg1, msg2, msg3)
		return li 						
	
	script = stringextract('data-extension-ard=', 'title=', page)
	script = stringextract('url":"', '"', script)
	PLog("script: " + script)											# Bsp.: ../ondemand/238/2380586.js
	
	page, msg = get_page(path=script)
	mp3_url = stringextract('"audioURL":"','"', page)	
	PLog("mp3_url: " + mp3_url)	
	
	summ_par = "%s||||%s" % (tag, summ)
	# AudioPlayMP3(mp3_url, title, img, summ_par,"ARD")					# mit Download, Rekursion
	PlayAudio(mp3_url, title, img, summ_par)  							# Alternative o. Download
	
	#xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	return																# Inkaufnahme GetDirectory-Error 
	
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
####################################################################################################
# Liste der Wochentage ARD + ZDF
	# Ablauf (ARD):  entfällt seit Einstellung der alten Mediathek	
	#		2. PageControl: Liste der Rubriken des gewählten Tages
	#		3. SinglePage: Sendungen der ausgewählten Rubrik mit Bildern (mehrere Sendungen pro Rubrik möglich)
	#		4. Parseplaylist: Auswertung m3u8-Datei (verschiedene Auflösungen)
	#		5. in Plex CreateVideoClipObject, in Kodi PlayVideo
	# Funktion VerpasstWoche bisher in www.ardmediathek nicht vorhanden. 
	#
	# ZDF:
	#	Wochentag-Buttons -> ZDF_Verpasst
	# 22.10.2021 sfilter dauerhaft  (Dict("CurSenderZDF")), Ablage
	#	in ZDF_Verpasst_Filter
	#
def VerpasstWoche(name, title):					# Wochenliste zeigen, name: ARD, ZDF Mediathek
	PLog('VerpasstWoche:')
	PLog(name);PLog(title); 
	title_org = title
	 
	sfilter=''
	fname = os.path.join(DICTSTORE, 'CurSenderZDF')				# init CurSenderZDF (aktueller Sender)
	if os.path.exists(fname):									# kann fehlen (Aufruf Merkliste)
		sfilter = Dict('load', 'CurSenderZDF')			
		
	if sfilter == '' or sfilter == False or sfilter == 'false':	# Ladefehler?
		sfilter = 'Alle ZDF-Sender'								# Default Alle ZDF-Sender (nur VERPASST)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
		
	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")		# Formate s. man strftime (3)
		zdfDate = rdate.strftime("%Y-%m-%d")		
		iWeekday =  rdate.strftime("%A")
		punkte = '.'
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)
		PLog(iDate); PLog(iWeekday);
		#title = ("%10s ..... %10s"% (iWeekday, iDate))	 # Formatierung in Plex ohne Wirkung		
		title =	"%s | %s" % (iDate, iWeekday)
		
		title=py2_encode(title); zdfDate=py2_encode(zdfDate);
		fparams="&fparams={'title': '%s', 'zdfDate': '%s', 'sfilter': '%s'}" % (quote(title), quote(zdfDate), sfilter)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Verpasst", fanart=R(ICON_ZDF_VERP), 
			thumb=R(ICON_ZDF_VERP), fparams=fparams)
	
	label = "Datum eingeben"							# Button für Datumeingabe anhängen
	tag = u"teilweise sind bis zu 4 Jahre alte Beiträge abrufbar"
	fparams="&fparams={'title': '%s', 'zdfDate': '%s', 'sfilter': '%s'}" % (quote(title), quote(zdfDate), sfilter)
	addDir(li=li, label=label, action="dirList", dirID="ZDF_Verpasst_Datum", fanart=R(ICON_ZDF_VERP), 
		thumb=GIT_CAL, fparams=fparams, tagline=tag)

														# Button für Stationsfilter
	label = u"Wählen Sie Ihren ZDF-Sender - aktuell: [COLOR red]%s[/COLOR]" % sfilter
	tag = "Auswahl: Alle ZDF-Sender, zdf, zdfneo oder zdfinfo" 
	fparams="&fparams={'name': '%s', 'title': 'ZDF-Mediathek', 'sfilter': '%s'}" % (quote(name), sfilter)
	addDir(li=li, label=label, action="dirList", dirID="ZDF_Verpasst_Filter", fanart=R(ICON_ZDF_VERP), 
		thumb=R(ICON_FILTER), tagline=tag, fparams=fparams)
		
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# True, sonst Rückspr. nach ZDF_Verpasst_Filter
	
#-------------------------
#  03.06.2021 ARD_Verpasst_Filter (Classic) entfernt							
#-------------------------
# Auswahl der ZDF-Sender für VerpasstWoche
# bei Abbruch bleibt sfilter unverändert								
def ZDF_Verpasst_Filter(name, title, sfilter):
	PLog('ZDF_Verpasst_Filter:'); PLog(sfilter); 
	
	stations = ['Alle ZDF-Sender', 'zdf', 'zdfneo', 'zdfinfo']
	i = stations.index(sfilter)
	dialog = xbmcgui.Dialog()
	d = dialog.select('ZDF-Sendestation wählen', stations, preselect=i)
	if d == -1:						# Fallback Alle
		d = 0
	sfilter = stations[d]
	PLog("Auswahl: %d. %s" % (d, sfilter))
	Dict('store', "CurSenderZDF", sfilter)
	
	return VerpasstWoche(name, title)

####################################################################################################
# 03.06.2021 entfernt (Classic-Version eingestellt): PODMore							
####################################################################################################
def PodFavoritenListe(title, offset=0):
	PLog('PodFavoritenListe:'); 
	
	title_org = title
	# Default fname: podcast-favorits.txt im Ressourcenverz.
	#	Alternative: Pfad zur persönlichen Datei 
	fname =  SETTINGS.getSetting('pref_podcast_favorits')
	PLog(fname)
	if os.path.isfile(fname) == False:
		PLog('persoenliche Datei %s nicht gefunden' % fname)					
		Inhalt = RLoad(FAVORITS_Pod)		# Default-Datei
	else:										
		try:
			Inhalt = RLoad(fname,abs_path=True)	# pers. Datei verwenden (Name ebenfalls podcast-favorits.txt)	
		except:
			Inhalt = ''
		
	if  Inhalt is None or Inhalt == '' or 'podcast-favorits.txt' not in Inhalt:				
		msg1='Datei podcast-favorits.txt nicht gefunden, nicht lesbar oder falsche Datei.'
		msg2='Bitte Einstellungen prüfen.'
		MyDialog(msg1, msg2, '')
		return
							
	# PLog(Inhalt) 
	bookmarks = []
	lines = Inhalt.splitlines()
	for line in lines:								# skip Kommentarzeilen + Leerzeilen 
		if line.startswith('#'):			
			continue
		if line.strip() == '':		
			continue
		bookmarks.append(line)
		
	rec_per_page = 20								# Anzahl pro Seite
	max_len = len(bookmarks)						# Anzahl Sätze gesamt
	start_cnt = int(offset) 						# Startzahl diese Seite
	end_cnt = int(start_cnt) + int(rec_per_page)	# Endzahl diese Seite
				
	title2 = 'Favoriten %s - %s (%s)' % (start_cnt+1, min(end_cnt,max_len) , max_len)
	li = xbmcgui.ListItem()
	li = home(li,ID='ARD Audiothek')				# Home-Button

	for i in range(len(bookmarks)):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:				# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:				# Anzahl pro Seite überschritten?
			break
		line = bookmarks[cnt]
		try:		
			title = line.split('|')[0]	
			path = line.split('|')[1]
			title = title.strip(); 
			path = path.strip() 
		except:
			title=''; path=''
		PLog(title); PLog(path)
		if path == '':						# ohne Link kein verwertbarer Favorit
			continue
			
		
		title=title.replace('\'', '')		# z.B. "Stimmt's? - NDR2"
		title=title.replace('&', 'plus')	# &=Trenner für Parameter in router
		PLog(title); PLog(path)
		title=py2_encode(title); path=py2_encode(path);
		
		if path.startswith('http'):			# Server-Url
			summary='Favoriten: ' + title
			fparams="&fparams={'title': '%s', 'path': '%s'}" % \
				(quote(title), quote(path))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFavoriten", 
				fanart=R(ICON_STAR), thumb=R(ICON_STAR), fparams=fparams, summary=path, 
				tagline=summary)
		else:								# lokales Verz./Share?
			fparams="&fparams={'title': '%s', 'path': '%s'}" % \
				(quote(title), quote(path))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFolder", 
				fanart=R(ICON_NOTE), thumb=R(ICON_DIR_FOLDER), fparams=fparams, summary=path, 
				tagline=title)		
			
					
	# Mehr Seiten anzeigen:
	PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt + int(offset)
		PLog(new_offset)
		summ = 'Mehr (insgesamt ' + str(max_len) + ' Favoriten)'
		title_org=py2_encode(title_org);
		fparams="&fparams={'title': '%s', 'offset': '%s'}" % (quote(title_org), new_offset)
		addDir(li=li, label=summ, action="dirList", dirID="PodFavoritenListe", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams, summary=title_org, tagline='Favoriten')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
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

	PLog(SETTINGS.getSetting('pref_use_downloads')) 	# Voreinstellung: False 
	if check_Setting('pref_use_downloads') == False:	# einschl. Test Downloadverzeichnis
		return
			
	if SETTINGS.getSetting('pref_show_qualities') == 'false':	# nur 1 (höchste) Qualität verwenden
		download_items = []
		download_items.append(download_list.pop(high))									 
	else:	
		download_items = download_list						# ganze Liste verwenden
	# PLog(download_items)
		
	i=0
	for item in download_items:
		PLog(item)
		item = item.replace('**', '|')						# 04.01.2021 Korrek. Trennz. Stream_List
		quality,url = item.split('#')
		PLog(url); PLog(quality); PLog(title_org)
		if url.find('.m3u8') == -1 and url.find('rtmp://') == -1:
			# detailtxt =  Begleitdatei mit Textinfos zum Video / Podcast:				
			detailtxt = MakeDetailText(title=title_org,thumb=thumb,quality=quality,
				summary=summary_org,tagline=tagline_org,url=url)
			v = 'detailtxt'+str(i)
			Dict('store', v, detailtxt)		# detailtxt speichern 
			if url.endswith('.mp3'):		
				Format = 'Podcast ' 			
			else:	
				Format = 'Video '			# .mp4, .webm, .. 
			#lable = 'Download ' + Format + ' | ' + quality
			lable = 'Download' + ' | ' + quality	# 09.01.2021 Wegfall Format aus Platzgründen 
			dest_path = SETTINGS.getSetting('pref_download_path')
			tagline = Format + 'wird in ' + dest_path + ' gespeichert' 									
			summary = 'Sendung: ' + title_org
			key_detailtxt='detailtxt'+str(i)
			url=py2_encode(url); title_org=py2_encode(title_org); sub_path=py2_encode(sub_path);
			fparams="&fparams={'url': '%s', 'title': '%s', 'dest_path': '%s', 'key_detailtxt': '%s', 'sub_path': '%s'}" % \
				(quote(url), quote(title_org), dest_path, key_detailtxt, quote(sub_path))
			addDir(li=li, label=lable, action="dirList", dirID="DownloadExtern", fanart=R(ICON_DOWNL), 
				thumb=R(ICON_DOWNL), fparams=fparams, summary=summary, tagline=tagline, mediatype='')
			i=i+1					# Dict-key-Zähler
	
	return li
	
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
		dfname = make_filenames(title.strip()) 
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
	if url.endswith('.mp3'):
		suffix = '.mp3'		
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
	
	dfname = dfname + suffix							# suffix: '.mp4', '.webm', oder '.mp3'
	
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
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
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

			for item in path_url_list:
				PLog(item)
				path, url = item.split('|')
				urlretrieve(url, path)
				#xbmc.sleep(1000*3)							# Debug
			
			msg1 = 'Download erledigt'
			msg2 = 'gestartet: %s' % timemark				# Zeitstempel 
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

			if notice:
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
						f.seek(0)								# seek + trancate: alten Inhalt löschen
						line = "%s|%s" % (str(cnt), str(new_len))
						f.write(line)
						f.truncate()
						PLog("line_start_dl: %s" % line)
				else:
					with open(DL_CNT,'w') as f:
						f.write("1|%s" % str(clen))					
				urlretrieve(url, fulldestpath)				
				#xbmc.sleep(1000*30)	# Debug
			if subget:											# Untertitel holen 
				get_subtitles(fulldestpath, sub_path)
			
			# sleep(20)											# Debug
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
						f.seek(0)								# seek + trancate: alten Inhalt löschen
						f.write(line)
						f.truncate()
						PLog("line_end_dl: %s" % line)
			
				
	except Exception as exception:
		PLog("thread_getfile:" + str(exception))
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
	sub_path = sub_path_conv(sub_path)		# ARD-Untertitel holen + konvertieren
	if sub_path.startswith('http'):			# ZDF-Untertitel holen
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
				PLog(myfont)
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
				
				w,h = draw.textsize(mytxt, font=font)
				W,H = base.size
				# x,y = 0.5*(W-w),0.90*H-h		# zentriert
				# x,y = W-w,0.90*H-h			# rechts
				x,y = 0.05*(W-w),0.96*(H-h)		# u. links
				PLog("x,y: %d, %d" % (x,y))

				# outlined Text - für helle Flächen erforderlich, aus stackoverflow.com/
				# /questions/41556771/is-there-a-way-to-outline-text-with-a-dark-line-in-pil 
				# try-Block für Draw 
				try:
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
def DownloadTools():
	PLog('DownloadTools:');

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
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0:
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

	PLog(SETTINGS.getSetting('pref_podcast_favorits'))					# Pfad zur persoenlichen Podcast-Favoritenliste
	path =  SETTINGS.getSetting('pref_podcast_favorits')							
	title = u'Persoenliche Podcast-Favoritenliste festlegen/ändern (%s)' % path			
	tagline = 'Format siehe podcast-favorits.txt (Ressourcenverzeichnis)'
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_podcast_favorits', 'mytype': '1', 'heading': '%s', 'path': '%s'}" % (title, path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_FAVORITS), fparams=fparams, tagline=tagline)
		
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
	if path == None or path == '':									# Existenz Verz. prüfen, falls vorbelegt
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
			dirlist = os.listdir(path)						# Größe Inhalt? 		
	dlpath = path

	PLog(len(dirlist))
	mpcnt=0; vidsize=0
	for entry in dirlist:
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0:
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
	
	# Downloads listen:
	for entry in dirlist:							# Download + Beschreibung -> DirectoryObject
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0:
			localpath = entry
			title=''; tagline=''; summary=''; quality=''; thumb=''; httpurl=''
			fname =  entry							# Dateiname 
			basename = os.path.splitext(fname)[0]	# ohne Extension
			ext =     os.path.splitext(fname)[1]	# Extension
			PLog(fname); PLog(basename); PLog(ext)
			txtfile = basename + '.txt'
			txtpath = os.path.join(path, txtfile)   # kompl. Pfad
			PLog('entry: ' + entry)
			PLog('txtpath: ' + txtpath)
			if os.path.exists(txtpath):
				txt = RLoad(txtpath, abs_path=True)		# Beschreibung laden - fehlt bei Sammeldownload
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
				#tagline = 'Beschreibung fehlt - Beschreibung gelöscht, Sammeldownload oder TVLive-Video'
				
			tag_par= tagline.replace('\n', '||')	
			PLog("Satz20:")
			PLog(httpurl); PLog(summary); PLog(tagline); PLog(quality); # PLog(txt); 			
			if httpurl.endswith('mp3'):
				oc_title = u'Anhören, Bearbeiten: Podcast | %s' % py2_decode(title)
				thumb = R(ICON_NOTE)
			else:
				oc_title=u'Ansehen, Bearbeiten: %s' % py2_decode(title)
				if thumb == '':							# nicht in Beschreibung
					thumb = R(ICON_DIR_VIDEO)

			httpurl=py2_encode(httpurl); localpath=py2_encode(localpath); dlpath=py2_encode(dlpath); 
			title=py2_encode(title); summary=py2_encode(summary); thumb=py2_encode(thumb); 
			tag_par=py2_encode(tag_par); txtpath=py2_encode(txtpath);
			fparams="&fparams={'httpurl': '%s', 'path': '%s', 'dlpath': '%s', 'txtpath': '%s', 'title': '%s','summary': '%s', \
				'thumb': '%s', 'tagline': '%s'}" % (quote(httpurl), quote(localpath), quote(dlpath), 
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
		
	else:										# 'mp3' = Podcast
		if fulldest_path.endswith('mp3'):		# Dateiname bei fehl. Beschreibung, z.B. Sammeldownloads
			title = title_org 											# 1. Anhören
			lable = "Anhören | %s" % (title_org)
			fulldest_path=py2_encode(fulldest_path); title=py2_encode(title); thumb=py2_encode(thumb); 
			summary=py2_encode(summary);	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(fulldest_path), 
				quote(title), quote(thumb), quote_plus(summary))
			addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, 
				fparams=fparams, mediatype='music') 
	
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
		
####################################################################################################
# Aufruf Main, Favoriten oder Merkliste anzeigen + auswählen
#	Hinzufügen / Löschen in Watch (Script merkliste.py)
# mode = 'Favs' für Favoriten  oder 'Merk' für Merkliste
# 	Datenbasen (Einlesen in ReadFavourites (Modul util) :
#		Favoriten: special://profile/favourites.xml 
#		Merkliste: ADDON_DATA/merkliste.xml (WATCHFILE)
# 	Verarbeitung:
#		Favoriten: Kodi's Favoriten-Menü, im Addon_Listing
#		Merkliste: zusätzl. Kontextmenmü (s. addDir Modul util) -> Script merkliste.py
#	
#	Probleme:  	Kodi's Fav-Funktion übernimmt nicht summary, tagline, mediatype aus addDir-Call
#				Keine Begleitinfos, falls  summary, tagline od. Plot im addDir-Call fehlen.
#				gelöst mit Base64-kodierter Plugin-Url: 
#					Sonderzeichen nach doppelter utf-8-Kodierung
#				07.01.2020 Base64 in addDir wieder entfernt - hier Verbleib zum Dekodieren
#					alter Einträge
# 				Sofortstart/Resumefunktion: funktioniert nicht immer - Bsp. KIKA-Videos.
#					Die Kennzeichnung mit mediatype='video' erfolgt nach Abgleich mit
#					CallFunctions.
#					Kodi verwaltet die Resumedaten getrennt (Merkliste/Originalplatz). 
#
# Ordnerverwaltung + Filter s. Wicki
#	Filter-Deadlock-Sicherungen: 
#		1. ShowFavs bei leerer Liste	2. Kontextmenü -> watch_filter
#		3. Settings (Ordner abschalten)
# 14.11.2021 Home-Button + Sortierung getrennt von globalen Settings
#
def ShowFavs(mode, myfilter=''):			# Favoriten / Merkliste einblenden
	PLog('ShowFavs: ' + mode)				# 'Favs', 'Merk'
	
	myfilter=''
	if mode == 'Merk':
		if SETTINGS.getSetting('pref_merkordner') == 'true':
			with open(MERKACTIVE, 'w'):			# Marker aktivieren (Refresh in merkliste)
				pass
			if os.path.isfile(MERKFILTER):	
				myfilter = RLoad(MERKFILTER,abs_path=True)
		else:									# Filter entfernen, falls Ordner abgewählt
			if os.path.isfile(MERKFILTER):		# Altern.: siehe Kontextmenü -> watch_filter
				os.remove(MERKFILTER)
				
	PLog('myfilter: ' + myfilter)
	li = xbmcgui.ListItem()						
	li = home(li, ID=NAME)								# Home-Button

	my_items, my_ordner= ReadFavourites(mode)			# Addon-Favs / Merkliste einlesen
	PLog(len(my_items))
	# Dir-Items für diese Funktionen erhalten mediatype=video:
	# 05.12.2020 zdfmobile.ShowVideo entfernt (enthält auch Mehrfachbeiträge)
	# 13.11.2021 ARDStartSingle hinzugefügt
	CallFunctions = ["PlayVideo", "ZDF_getVideoSources",
						"zdfmobile.PlayVideo", "SingleSendung", "ARDStartVideoStreams", 
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
		s3		= u"Ordner für Einträge lassen sich in den Settings ein-/ausschalten"
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
	
	item_cnt = 0
	for fav in my_items:
		fav = unquote_plus(fav)						# urllib2.unquote erzeugt + aus Blanks!		
		fav_org = fav										# für ShowFavsExec
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
			
		if myfilter:
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
		
		modul = "ardundzdf"
		dirPars = unescape(dirPars); 
		if 'resources.lib.' in dirPars:
			modul = stringextract('resources.lib.', ".", dirPars) 
		
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
		Plot = Plot.replace('||', '\n')			# s. PlayVideo
		Plot = Plot.replace('+|+', '')	
		if Plot.strip().startswith('stage|'):	# zdfMobile: nichtssagenden json-Pfad löschen
			Plot = 'Beitrag aus zdfMobile' 
		PLog('summary: ' + summary); PLog('tagline: ' + tagline); PLog('Plot: ' + Plot)
		
		if SETTINGS.getSetting('pref_FavsInfo') ==  'false':	# keine Begleitinfos 
			summary='';  tagline=''
			
		PLog('fanart: ' + fanart); PLog('thumb: ' + thumb);
		fparams = fparams.replace('\n', '||')				# json-komp. für func_pars in router()
		fparams = unquote_plus(fparams)
		fparams ="&fparams={%s}" % quote_plus(fparams)		# router-kompatibel			
		PLog('fparams3: ' + fparams)
		fanart = R(ICON_DIR_WATCH)
		if mode == 'Favs':
			fanart = R(ICON_DIR_FAVORITS)
		
		summary = summary.replace('||', '\n')		# wie Plot	
		tagline = tagline.replace('||', '\n')
		
		if modul != "ardundzdf":					# Hinweis Modul
			tagline = "[B][COLOR red]Modul: %s[/COLOR][/B]%s" % (modul, tagline)
		if SETTINGS.getSetting('pref_merkordner') == 'true':	
			merkname = name								# für Kontextmenü Ordner in addDir
			if ordner:									# Hinweis Ordner
				if 'COLOR red' in tagline:				# bei Modul plus LF
					tagline = "[B][COLOR blue]Ordner: %s[/COLOR][/B]\n%s" % (ordner, tagline)
				else:
					tagline = "[B][COLOR blue]Ordner: %s[/COLOR][/B]%s" % (ordner, tagline)
				
			if SETTINGS.getSetting('pref_WatchFolderInTitle') ==  'true':	# Kennz. Ordner
				if ordner: 
					name = "[COLOR blue]%s[/COLOR] | %s" % (ordner, name)

		sortlabel = "ShowFavs"						# 16.11.2021 z.Z. nicht genutzt
		addDir(li=li, label=name, action=action, dirID=dirID, fanart=fanart, thumb=my_thumb,
			summary=summary, tagline=tagline, fparams=fparams, mediatype=mediatype, 
			sortlabel=sortlabel, merkname=merkname)
		item_cnt = item_cnt + 1
		
	if item_cnt == 0:								# Ordnerliste leer?
		if myfilter:								# Deadlock
			heading = u'Leere Merkliste mit dem Filter: %s' % myfilter
			msg1 = u'Der Filter wird nun gelöscht; die Merkliste wird ohne Filter geladen.'
			msg2 = u'Wählen Sie dann im Kontextmenü einen anderen Filter.'
			MyDialog(msg1,msg2,heading=heading)
			if os.path.exists(MERKFILTER):
				os.remove(MERKFILTER)
			# ShowFavs('Merk')						# verdoppelt Home- + Infobutton
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
		name = stringextract('<name>', '</name>', element)
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
			thumb=img, fparams=fparams)

	laenge = SETTINGS.getSetting('pref_LiveRecord_duration')
	if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
		laenge = "wird manuell eingegeben"

	title = 'EPG Alle JETZT | Recording TV-Live'; 
	summary =u'elektronischer Programmführer\n\nAufnehmen via Kontexmenü, Dauer: %s (siehe Settings)' % laenge
	tagline = 'zeigt die laufende Sendung für jeden Sender'
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
		thumb=R('tv-EPG-all.png'), fparams=fparams, summary=summary, tagline=tagline)
							
	title = 'EPG Sender einzeln'; 
	if SETTINGS.getSetting('pref_epgRecord') == 'true':		
		title = 'EPG Sender einzeln | Sendungen mit EPG aufnehmen'; 
	tagline = u'zeigt für den ausgewählten Sender ein 12-Tage-EPG'		# EPG-Button Einzeln anhängen
	summary='je Seite: 24 Stunden (zwischen 05.00 und 05.00 Uhr des Folgetages)'
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="EPG_Sender", fanart=R(ICON_MAIN_TVLIVE), 
		thumb=R('tv-EPG-single.png'), fparams=fparams, summary=summary, tagline=tagline)	
		
	PLog(str(SETTINGS.getSetting('pref_LiveRecord'))) 
	if SETTINGS.getSetting('pref_LiveRecord') == 'true':		
		title = 'Recording TV-Live'										# TVLiveRecord-Button anhängen
		summary = u'Sender wählen und direkt aufnehmen.\nDauer: %s (siehe Settings)' % laenge
		tagline = 'Downloadpfad: %s' 	 % SETTINGS.getSetting('pref_download_path') 				
		fparams="&fparams={'title': '%s'}" % title
		addDir(li=li, label=title, action="dirList", dirID="TVLiveRecordSender", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=R('icon-record.png'), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

	
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
	
	sort_playlist = get_sort_playlist()	# einschl. get_ZDFstreamlinks
	# PLog(sort_playlist)
	
	summ = u"für die Merkliste (Kontextmenü) sind die Einträge dieser Liste wegen des EPG besser geeignet"
	summ = u"%s als die Menüs Überregional, Regional und Privat" % summ
	
	for rec in sort_playlist:
		title = rec[0]
		img = rec[2]
		if u'://' not in img:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		link = rec[3]
		ID = rec[1]
		
		PLog("Satz13:")
		PLog('title: %s, ID: %s' % (title, ID))
		PLog(img)
		if ID == '':				# ohne EPG_ID
			title = title + ': ohne EPG' 
			title=py2_encode(title); link=py2_encode(link); img=py2_encode(img); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '', 'Merk': '%s'}" %\
				(quote(link), quote(title), quote(img), Merk)
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
				thumb=img, fparams=fparams, tagline='weiter zum Livestream', summary=summ)
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
#-----------------------------
#	Liste aller TV-Sender wie EPG_Sender, hier mit Aufnahme-Button
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

	sort_playlist = get_sort_playlist()		# Senderliste, einschl. get_ZDFstreamlinks, get_ARDstreamlinks
	PLog('Sender: ' + str(len(sort_playlist)))
	for rec in sort_playlist:
		title 	= rec[0]
		ID 		= rec[1]
		img 	= rec[2]
		if u'://' not in img:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		link 	= rec[3]
		if ID == '':				# ohne EPG_ID
			title = "%s | ohne EPG" % title 
		if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
			laenge = "wird manuell eingegeben"
		summ 	= 'Aufnahmedauer: %s' 	% laenge
		summ	= u"%s\n\nStart ohne Rückfrage!" % summ
		tag		= 'Zielverzeichnis: %s' % SETTINGS.getSetting('pref_download_path')
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
# Aufruf: EPG_Sender, TVLiveRecordSender
# get_sort_playlist: Einbettung get_ZDFstreamlinks 
#	für ZDF-Sender
#
def get_sort_playlist():						# sortierte Playliste der TV-Livesender
	PLog('get_sort_playlist:')
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	sort_playlist =  []
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)				# skip_log: Log-Begrenzung
	ard_streamlinks = get_ARDstreamlinks(skip_log=True)
	
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
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)	
						
		if 'ARDSource' in link:							# Streamlink für ARD-Sender holen,
			title_sender = stringextract('<hrefsender>', '</hrefsender>', item)	
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
			for line in ard_streamlinks:
				PLog("ardline: " + line)
				items = line.split('|')
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
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
		
	today_human = 'ab ' + EPG_rec[0][7]
			
	for rec in EPG_rec:
		href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];
		starttime=rec[0]; endtime=rec[8]; 
		start_end = ''										# Trigger K-Menü
		if SETTINGS.getSetting('pref_epgRecord') == 'true':	
			start_end = "%s|%s" % (starttime, endtime)		# Unix-Format -> ProgramRecord

		if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
			img = R('icon-bild-fehlt.png')
		sname = unescape(sname)
		title = sname
		summ = unescape(summ)
		if 'JETZT' in title:			# JETZT-Markierung unter icon platzieren
			# Markierung für title bereits in EPG
			summ = "[COLOR red][B]LAUFENDE SENDUNG![/B][/COLOR]\n\n%s" % summ
			title = sname
		PLog("title: " + title)
		tagline = 'Zeit: ' + vonbis
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
		summ = u'nächster Tag'
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

def EPG_ShowAll(title, offset=0, Merk='false'):
	PLog('EPG_ShowAll:'); PLog(offset) 
	title = unquote(title)
	title_org = title
	title2='Aktuelle Sendungen'
	
	import resources.lib.EPG as EPG
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = get_sort_playlist()	
	PLog(len(sort_playlist))
	# PLog(sort_playlist)
	
	rec_per_page = 25								# Anzahl pro Seite (Plex: Timeout ab 15 beobachtet)
	max_len = len(sort_playlist)					# Anzahl Sätze gesamt
	start_cnt = int(offset) 						# Startzahl diese Seite
	end_cnt = int(start_cnt) + int(rec_per_page)	# Endzahl diese Seite
	
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
		img_playlist = rec[2]	
		if u'://' not in img_playlist:		# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img_playlist = R(img_playlist)
		ID = rec[1]
		summ = ''
		
		tagline = 'weiter zum Livestream'
		if ID == '':									# ohne EPG_ID
			title = title_playlist + ': ohne EPG' 
			img = img_playlist
			PLog("img: " + img)
		else:
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis: 
			rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
			# PLog(rec)	# bei Bedarf
			if len(rec) == 0:							# EPG-Satz leer?
				title = title_playlist + '| ohne EPG'
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
# onlySender: Button nur für diesen Sender (z.B. ZDFSportschau Livestream für Menü
#	ZDFSportLive)
# 23.06.2020 lokale m3u8-Dateien in livesenderTV.xml sind entfallen
#			Ermittlung ZDF-Streamlinks im Web (link=ZDFsource)
#
def SenderLiveListe(title, listname, fanart, offset=0, onlySender=''):			
	# SenderLiveListe -> SenderLiveResolution (reicht nur durch) -> Parseplaylist (Ausw. m3u8)
	#	-> CreateVideoStreamObject 
	PLog('SenderLiveListe:')
	PLog(title); PLog(listname)
				
	title2 = 'Live-Sender ' + title
	title2 = title2
	li = xbmcgui.ListItem()
			
	# Besonderheit: die Senderliste wird lokal geladen (s.o.). Über den link wird die URL zur  
	#	*.m3u8 geholt. Nach Anwahl eines Live-Senders werden in SenderLiveResolution die 
	#	einzelnen Auflösungsstufen ermittelt.
	#
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
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
			
	zdf_streamlinks=''
	lname = py2_decode(listname)
	if lname == u'Überregional':			# Streamlinks für ZDF-Sender holen
		zdf_streamlinks = get_ZDFstreamlinks()			# Modul util
	if lname == u'Überregional' or lname == u'Regional':
		ard_streamlinks = get_ARDstreamlinks()			# ard_streamlinks oder ard_streamlinks_UT	
		
	mediatype='' 						# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	liste = blockextract('<item>', mylist)				# Details eines Senders
	PLog(len(liste));
	EPG_ID_old = ''											# Doppler-Erkennung
	sname_old=''; stime_old=''; summ_old=''; vonbis_old=''	# dto.
	summary_old=''; tagline_old=''
	for element in liste:									# EPG-Daten für einzelnen Sender holen 	
		element = py2_decode(element)	
		link = stringextract('<link>', '</link>', element) 
		link = unescape(link)	
		title_sender = stringextract('<hrefsender>', '</hrefsender>', element) # mit folgendem Blank!
		PLog(u'Sender: %s, link: %s' % (title_sender, link));

		if 'ZDFsource' in link:							# Streamlink für ZDF-Sender holen,
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
			for line in zdf_streamlinks:
				PLog("zdfline: " + line)
				items = line.split('|')
				# Bsp.: "ZDFneo " in "ZDFneo Livestream":
				if up_low(title_sender) == up_low(items[0]): 
					link = items[1]
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
				
		if 'ARDSource' in link:							# Streamlink für ARD-Sender holen,
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
			for line in ard_streamlinks:
				PLog("ardline: " + line)
				items = line.split('|')
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)
		
		PLog('Mark2')
		# Spezialbehandlung für N24 in SenderLiveResolution - Test auf Verfügbarkeit der Lastserver (1-4)
		# EPG: ab 10.03.2017 einheitlich über Modul EPG.py (vorher direkt bei den Sendern, mehrere Schemata)
		# 								
		title = stringextract('<title>', '</title>', element)
		if onlySender:									# Button nur für diesen Sender
			title=py2_encode(title); onlySender=py2_encode(onlySender) 
			if title != onlySender:
				continue
			
		epg_date=''; epg_title=''; epg_text=''; summary=''; tagline='' 
		# PLog(SETTINGS.getSetting('pref_use_epg')) 	# Voreinstellung: EPG nutzen? - nur mit Schema nutzbar
		PLog('setting: ' + str(SETTINGS.getSetting('pref_use_epg')))
		if SETTINGS.getSetting('pref_use_epg') == 'true':
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis:
			EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', element)
			PLog(EPG_ID); PLog(EPG_ID_old);

			try:
				rec = EPG.EPG(ID=EPG_ID, mode='OnlyNow')	# Daten holen - nur aktuelle Sendung
				if rec == '':								# Fehler, ev. Sender EPG_ID nicht bekannt
					sname=''; stime=''; summ=''; vonbis=''
				else:
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
				tagline = u'Sendung: %s Uhr' % vonbis
			else:
				tagline = ''

		title = unescape(title)	
		title = title.replace('JETZT:', '')					# 'JETZT:' hier überflüssig
		if link == '':										# fehlenden Link im Titel kennz.
			title = "%s | Streamlink fehlt!" %  title	
		summary = unescape(summary)	
						
		img = stringextract('<thumbnail>', '</thumbnail>', element) 
		if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
			
		geo = stringextract('<geoblock>', '</geoblock>', element)
		PLog('geo: ' + geo)
		if geo:
			tagline = 'Livestream nur in Deutschland zu empfangen!'
			
		PLog("Satz8:")
		PLog(title); PLog(link); PLog(img); PLog(summary); PLog(tagline[0:80]);
		Resolution = ""; Codecs = ""; duration = ""
	
		# if link.find('rtmp') == 0:				# rtmp-Streaming s. CreateVideoStreamObject
		# Link zu master.m3u8 erst auf Folgeseite? - SenderLiveResolution reicht an  Parseplaylist durch
		descr = summary.replace('\n', '||')
		if tagline:
			descr = "%s %s" % (tagline, descr)		# -> Plot (PlayVideo) 
		title=py2_encode(title); link=py2_encode(link);
		img=py2_encode(img); descr=py2_encode(descr);	
		fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': '%s'}" % (quote(link), 
			quote(img), quote(title), quote(descr))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=fanart, thumb=img, 
			fparams=fparams, summary=summary, tagline=tagline, mediatype=mediatype)		
	
	if onlySender== '':		
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
#
def SenderLiveResolution(path, title, thumb, descr, Merk='false', Sender='', start_end=''):
	PLog('SenderLiveResolution:')
	PLog(title); PLog(descr); PLog(Sender);
	path_org = path

	# Radiosender in livesenderTV.xml ermöglichen (ARD Audio Event Streams)
	link_ext = ["mp3", '.m3u', 'low']				# auch ../stream/mp3
	switch_audio = False
	for ext in link_ext:
		if path_org.endswith(ext):
			switch_audio = True
	if switch_audio or 'sportradio' in path_org:	# sportradio-deutschland o. passende Ext.
		PLog("Audiolink: %s" % path_org) 			
		PlayAudio(path_org, title, thumb, Plot=title)  # direkt	
		return

	page, msg = get_page(path=path)					# Verfügbarkeit des Streams testen
	if page == '':									# Fallback zum Classic-Sendername in Startsender
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
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: SenderLiveResolution')
		PlayVideo(url=path, title=title, thumb=thumb, Plot=descr, Merk=Merk)
		return
	
	url_m3u8 = path
	PLog(title); PLog(url_m3u8);

	li = xbmcgui.ListItem()
	if "kikade-" in path:
		li = home(li, ID='Kinderprogramme')			# Home-Button
	else:
		li = home(li, ID=NAME)				# Home-Button
										
	# Spezialbehandlung für N24 - Test auf Verfügbarkeit der Lastserver (1-4),
	#	  m3u8-Datei für Parseplaylist inkompatibel, nur 1 Videoobjekt
	if title.find('N24') >= 0:
		url_m3u8 = N24LastServer(url_m3u8) 
		PLog(url_m3u8)
		if '?sd=' in url_m3u8:				# "Parameter" sd kappen: @444563/index_3_av-b.m3u8?sd=10
			url_m3u8 = url_m3u8.split('?sd=')[0]	
		PLog(url_m3u8)
		summary = 'Bandbreite unbekannt'
		title=py2_encode(title); url_m3u8=py2_encode(url_m3u8);
		thumb=py2_encode(thumb); descr=py2_encode(descr);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote_plus(url_m3u8), 
			quote_plus(title), quote_plus(thumb), quote_plus(descr))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title, mediatype='video')	
		
	if url_m3u8.find('rtmp') == 0:		# rtmp, nur 1 Videoobjekt
		summary = 'rtmp-Stream'
		title=py2_encode(title); url_m3u8=py2_encode(url_m3u8);
		thumb=py2_encode(thumb); descr=py2_encode(descr);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote_plus(url_m3u8), 
			quote_plus(title), quote_plus(thumb), quote_plus(descr))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title, mediatype='video')	
		
	# alle übrigen (i.d.R. http-Links), Videoobjekte für einzelne Auflösungen erzeugen
	# Für Kodi: m3u8-Links abrufen, speichern und die Datei dann übergeben - direkte
	#	Übergabe der Url nicht abspielbar
	# is_playable ist verzichtbar
	if url_m3u8.find('.m3u8') >= 0: # häufigstes Format
		PLog(url_m3u8)
		if url_m3u8.startswith('http'):			# URL extern? (lokal entfällt Eintrag "autom.")
												# Einzelauflösungen + Ablage master.m3u8:
			li = ParseMasterM3u(li, url_m3u8, thumb, title, tagline=title, descr=descr)	
							
		# Auswertung *.m3u8-Datei  (lokal oder extern), Auffüllung Container mit Auflösungen. 
		# jeweils 1 item mit http-Link für jede Auflösung.
		
		# Parseplaylist -> CreateVideoStreamObject pro Auflösungstufe
		PLog("title: " + title)
		descr = "%s\n\n%s" % (title, descr)
		PLog("descr: " + descr)
		li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=descr)	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
							
	else:	# keine oder unbekannte Extension - Format unbekannt,
			# # Radiosender s.o.
		msg1 = 'SenderLiveResolution: unbekanntes Format. Url:'
		msg2 = url_m3u8
		PLog(msg1)
		MyDialog(msg1, msg2, '')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
		
#--------------------------------------------------------------------------------------------------
# Button für Einzelauflösungen für Streamlink url_m3u8
#	ID: Kennung für home
def show_single_bandwith(url_m3u8, thumb, title, descr, ID):
	PLog('show_single_bandwith:'); 
	
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)						# Home-Button
	
	descr = title + "\n\n" + descr
	li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=descr)	
	
	xbmcplugin.endOfDirectory(HANDLE)

#-----------------------------
# Ablage master.m3u8, einschl. Behandlung relativer Links
#	Button für "Bandbreite und Aufloesung automatisch" (master.m3u8)
#	Die Dateiablage dient zur Ablage der Einzelauflösungen, kann aber 
#		bei Kodi auch zum Videostart verwendet werden. 
#	Buttons für die Einzelauflösungen werden in Parseplaylist
#		gefertigt.
#   descr = Plot, wird zu PlayVideo durchgereicht.
#	19.12.2020 Sendungs-Titel ergänzt (optional: stitle)
#
def ParseMasterM3u(li, url_m3u8, thumb, title, descr, tagline='', sub_path='', stitle=''):	
	PLog('ParseMasterM3u:'); 
	PLog(title); PLog(url_m3u8); PLog(thumb); PLog(tagline);
	 
	PLog(type(title)); 	PLog(type(url_m3u8))
	title=unescape(title); title=repl_json_chars(title)
	
	sname = url_m3u8.split('/')[2]				# Filename: Servername.m3u8
	msg1 = "Datei konnte nicht "				# Vorgaben xbmcgui.Dialog
	msg2 = sname + ".m3u8"
	msg3 = "Details siehe Logdatei"
			
	page, msg = get_page(path=url_m3u8)			# 1. Inhalt m3u8 laden	
	PLog(len(page))
	if page == '':								# Fehlschlag
		msg1 = msg1 + "geladen werden." 
		MyDialog(msg1, msg2, msg3)
		return
		
	lines = page.splitlines()					# 2. rel. Links korrigieren 
	lines_new = []
	i = 0
	for line in lines:	
		# PLog(line)
		line = line.strip()
		if line == '' or line.startswith('#'):		# skip Metadaten
			lines_new.append(line)
			continue
		if line.startswith('http') == False:   		# relativer Pfad? 
			# PLog('line: ' + line)
			path = url_m3u8.split('/')[:-1]			# m3u8-Dateinamen abschneiden
			path = "/".join(path)
			url = "%s/%s" % (path, line) 			# Basispfad + relativer Pfad
			line = url
			# PLog('url: ' + url)
		# PLog('line: ' + line)
		lines_new.append(line)
		i = i + 1
		
	page = '\n'.join(lines_new)
	PLog('page: ' + page[:100])

	fname = sname + ".m3u8"
	fpath = os.path.join(M3U8STORE, fname)
	PLog('fpath: ' + fpath)
	msg = RSave(fpath, page)			# 3.  Inhalt speichern -> resources/m3u/
	if 'Errno' in msg:
		msg1 = msg1 + " gespeichert werden." # msg1 s.o.
		PLog(msg1); PLog(msg2)
		MyDialog(msg1, msg2, msg3)
		return
	else:				
		# Alternative: m3u8-lokal starten:
		# 	fparams="&fparams=url=%s, title=%s, is_playable=%s" % (sname + ".m3u8", title, True)
		# descr -> Plot	
		tagline	 = tagline.replace('||','\n')				# s. tagline in ZDF_get_content
		descr_par= descr
		descr	 = descr.replace('||','\n')					# s. descr in ZDF_get_content
		title = "autom. | " + title

		title=py2_encode(title); url_m3u8=py2_encode(url_m3u8);
		thumb=py2_encode(thumb); descr_par=py2_encode(descr_par); sub_path=py2_encode(sub_path);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
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
		img_src = img_src.replace('v-varxs', 'v-varxl')			# ev. attributeswap auswerten 
		
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
		#pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
		pic_name 	= img_src.split('/')[-1]			# Bildname aus Quelle
		local_path 	= "%s/%s" % (fpath, pic_name)
		PLog("local_path: " + local_path)
		title = "Bild %03d: %s" % (image+1, pic_name)	# Numerierung
		if len(title) > 70:
			title = "%s.." % title[:70]					# Titel begrenzen
		
		PLog("Bildtitel: " + title)
		
		local_path 	= os.path.abspath(local_path)
		thumb = local_path
		if os.path.isfile(local_path) == False:			# schon vorhanden?
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
				
		lable = u"Alle Bilder löschen"						# 2. Löschen
		tag = 'Bildverzeichnis: ' + fname 
		summ= u'Bei Problemen: Bilder löschen, Wasserzeichen ausschalten,  Bilder neu einlesen'
		fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % quote(fpath)
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
			thumb=R(ICON_DELETE), fparams=fparams, summary=summ, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern
		
	
				  
####################################################################################################
# 29.09.2019 Umstellung Radio-Livestreams auf ARD Audiothek
#	Codebereinigung - gelöscht: 
#		RadioLiveListe, RadioAnstalten, livesenderRadio.xml, 77 Radio-Icons (Autor: Arauco)
#

###################################################################################################
#									ZDF-Funktionen
###################################################################################################
# Startseite der ZDF-Mediathek 
#	show_cluster (rekursiv): falls true, wird der Stage-Bereich mit den Highlights gelistet
#	Die Cluster haben dieselbe Struktur wie ZDF-Rubriken mit Besonderheit class="loader"
#		(Nachlade-Beiträge, escaped) - daher jeweils Buttons für ZDFRubrikSingle.
#	Rubriken enthalten zusätzl. Clusterung - Bearbeitung in Funktion ZDFRubriken.
# cut Stage, geändert 27.09.2019
#	21.11.2019 Webseite geändert - Beiträge der Cluster werden beim 2. Durchlauf 
#		ausgeschnitten + via ZDF_get_content geladen (wie Highlights, Ausnahmen siehe
#		Getrennt behandeln).
# 21.11.2020 funk-Cluster "funk - Wissen, Liebe, Gaming" -> statt des 2. Durchlaufs mit 
#	den einzelnen Beiträgen zeigen wir die funk-Startseite verlinkt im letzten Einzel-
#	beitrag und verfahren wie beim 1. Durchlauf (Quell-Struktur mit ZDF-Startseite identisch).
# 07.07.2021 ZDF-funk-Beiträge aufgrund der Webänderungen mit eigenem Menü ZDF-funk in Main_ZDF,
#	Nutzung ZDFStart für die funk-Startseite wie bisher.
#
def ZDFStart(title, show_cluster='', path=''): 
	PLog('ZDFStart: ' + show_cluster); 
	PLog(title)
		
	title_org = title
	li = xbmcgui.ListItem()

	if 'www.zdf.de/funk' in path:
		BASE = ZDF_BASE + '/funk/'
		ID = 'ZDFfunkStart'
	else:
		BASE = ZDF_BASE
		ID = 'ZDFStart'
	Logo = 'ZDF'; 
	if "www.zdf.de/kinder" in path:
		BASE 	= "https://www.zdf.de/kinder"							# BASE_TIVI
		Logo	= 'ZDFtivi'
		ID 		= 'Kinderprogramme'								
		
	#headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
	#'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}"
	headers=''
	page, msg = get_page(path=BASE, header=headers)
	if page == '':
		msg1 = "%s-Startseite nicht im Web verfügbar." % Logo
		msg2 = msg
		PLog(msg1); PLog(msg2);
		MyDialog(msg1, msg2, '')	
		
	# ------------------------------------------------------------------
	# 2. Durchlauf: 
	if show_cluster:											
		PLog("ZDFStart_2:")
		if  title == "[B]Highlights[/B]":								# Liste Highlights 
			li = home(li, ID=ID)										# Home-Button
			stage = stringextract('class="sb-page">', 'class="cluster-title-wrap">', page) 
			# ID='DEFAULT': ermöglicht Auswertung Mehrfachseiten in ZDF_get_content
			li, page_cnt = ZDF_get_content(li=li, page=stage, ref_path=path, ID='STAGE')
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		else:													#Home-Button in ZDFRubrikSingle
			# Cluster ermitteln:
			content =  blockextract('class="cluster-title-wrap">', page)
			promo=[]
			if 'class="b-promo-teaser' in page:						# o. cluster-title-wrap
				promo = blockextract('class="b-promo-teaser', page, '</article>')
				PLog('content_promo2: ' + str(len(promo)))
			content = promo + content
			PLog('content2: ' + str(len(content)))
				
			for rec in content:
				pos=-1
				if rec.startswith('class="b-promo-teaser') == False:	# normale Cluster begrenzen
					if 'class="b-promo-teaser' in rec:					# PromoTeaser am Ende abschneiden
						pos = rec.find('class="b-promo-teaser')
					if "title='Weitere laden" in rec:					#
						pos = rec.find("title='Weitere laden")
				if pos > 0:
					rec = rec[:pos]	

				href	= stringextract('href="', '"', rec)
				if href.startswith('http') == False:
					href = BASE + href
				title = ZDF_get_clustertitle(rec)						# Cluster-Titel ermitteln
				title = py2_decode(title)
				# PLog('Mark0'); PLog(title); PLog(title_org)
				if title_org in title:
					PLog('Cluster_gefunden: %s' % title_org)
					break  
					
			ZDFRubrikSingle(title, path, clus_title=title, page=rec)	# einschl. Loader-Beiträge
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

	# ------------------------------------------------------------------
	# 1. Durchlauf: Buttons Stage + Cluster 
	PLog("ZDFStart_1:")
	PLog("ID: " + ID)
	li = home(li, ID=ID)						# Home-Button
	
	title = '[B]Highlights[/B]'									# Highlights voranstellen
	# thumb = R(ICON_DIR_FOLDER)
	thumb = ZDF_get_img(page)									#  1. img der Highlights
	tag = "Folgeseiten"
	fparams="&fparams={'title': '%s', 'show_cluster': 'true','path': '%s'}" % (quote(title), quote(BASE))
	addDir(li=li, label=title, action="dirList", dirID="ZDFStart", fanart=thumb, 
		thumb=thumb, tagline=tag, fparams=fparams)
	
	content =  blockextract('cluster-title"', page)				# 2.Cluster
	promo=[]
	if 'class="b-promo-teaser' in page:							# o. cluster-title-wrap
		promo = blockextract('class="b-promo-teaser', page, '</article>')
		promo_cnt = len(promo)
		PLog('content_promo1: ' + str(promo_cnt))
	content = promo + content
	PLog('content1: ' + str(len(content)))

	tlist=[]; cnt=0												# Titel-Liste für Dopplererkenn.
	for rec in content:
		title = ZDF_get_clustertitle(rec)						# Cluster-Titel ermitteln
		title = py2_decode(title)		

		# "Inhaltstext im Voraus laden" in ZDF_get_content (via ZDFRubrikSingle ->
		#	ZDF_Sendungen) 
		# Getrennt behandeln:
		if title == 'Rubriken':									# doppelt: hier + Hauptmenü
			fparams="&fparams={'name': 'Rubriken'}"
			addDir(li=li, label="Rubriken", action="dirList", dirID="ZDFRubriken", fanart=R(ICON_ZDF_RUBRIKEN), 
				thumb=R(ICON_ZDF_RUBRIKEN), tagline=tag, fparams=fparams)
		
		elif title == 'Livestreams':							# Livestreams, geändert 27.09.2019 
			thumb = ZDF_get_img(rec)
			fparams="&fparams={'title': '%s'}"	% title 
			addDir(li=li, label=title, action="dirList", dirID="ZDFStartLive", fanart=thumb, 
				thumb=thumb, tagline=tag, fparams=fparams)
				
		# skip: enthaltene Cluster A-Z, Barrierefrei, Verpasst getrennt im Hauptmenü:			
		elif title == 'Alles auf einen Blick':					
			continue
		elif title.startswith('Direkt zu ...'):					
			continue
		elif title.startswith(u'Das könnte dich'):				# .. interessieren 					
			continue
		elif 'Mein Programm' in title:				
			continue
		elif 'Neue Videos aus deinen Lieblingssendungen' in title:	# tivi-Start			
			continue
		elif title == '':				
			continue

		# skip: javascript-erzeugte Inhalte, SCMS-ID's bisher nicht erreichbar,
		#	Call data-clusterrecommendation-template="/broker/relay?plays=..,
		# Bsp: 'Empfehlungen für Sie', 'Direkt zu ..', 'weiterschauen..', 'Vorab in..',
		# dto. ZDF_Sendungen:	
		elif 'data-tracking-title=' in rec:
			continue
		else:													# restl. Cluster -> 2. Durchlauf	
			label = title
			tag = "Folgeseiten"
			href = BASE
			show_cluster = "true"
			thumb = ZDF_get_img(rec)
			
			if 'class="b-promo-teaser' in rec:					# Text für Teaserboxen erweitern
				if cnt < promo_cnt:
					label,path,img_src,descr,dauer,enddate,isvideo = ZDF_get_teaserDetails(page=rec)
					label = "[B]Teaserbox:[/B] %s" % label
					tag = "%s\n\n%s" % (tag, descr)
					cnt = cnt + 1
			
			PLog("Satz3:")
			PLog(title); PLog(href); PLog(thumb); PLog(tag); 
			title=py2_encode(title);
			fparams="&fparams={'title': '%s', 'show_cluster': '%s','path': '%s'}" %\
				(quote(title), show_cluster, quote(href))
			addDir(li=li, label=label, action="dirList", dirID="ZDFStart", fanart=thumb, 
				thumb=thumb, tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
#---------------------------------------------------------------------------------------------------
# Aufrufer: ZDFStart (2x), ZDFRubrikSingle, ZDF_Sendungen
def ZDF_get_clustertitle(rec): 							# Cluster-Titel der Startseite ermitteln
	PLog('ZDF_get_clustertitle:');
	#PLog(rec[:200])
	
	title=''
	if 'tabindex="0"' in rec:
		title = stringextract(u'tabindex="0"', '</h2>', rec)
		if title:
			title=mystrip(title); title=title.replace('>', '')	# >Film-Highlights</h2>
			title=unescape(title); title=title.strip() 			# zum Vergleich im 2. Durchlauf
			PLog("tabindex_title: " + title)

	title = py2_encode(title)									# Aufrufer muss dekodieren
	PLog("clustertitle: " + title)
	return title 

#---------------------------------------------------------------------------------------------------
# Aufruf: ZDFStart
# 24.06.2020 gemeinsame Nutzung von get_ZDFstreamlinks (wie SenderLiveListe für ZDF-Sender
#	aus livesenderTV.xml für Menü TV-Livestreams/Überregional)
def ZDFStartLive(title): 										# ZDF-Livestreams von ZDFStart
	PLog('ZDFStartLive:'); 
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	mediatype='' 						# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	# Zeile: "webtitle|href|thumb|tagline"
	zdf_streamlinks = get_ZDFstreamlinks()
	for line in zdf_streamlinks:
		title, href, thumb, tagline = line.split('|')
		PLog(title); PLog(href);
	
		title=py2_encode(title); href=py2_encode(href);
		thumb=py2_encode(thumb); descr=py2_encode(tagline);	
		fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': '%s'}" % (quote(href), 
			quote(thumb), quote(title), quote(tagline))
		addDir(li=li, label=title, action="dirList", dirID="ZDFStartLiveSingle", fanart=thumb, thumb=thumb, 
			fparams=fparams, tagline=tagline, mediatype=mediatype)		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
#-------------------------------------------------------
# Aufruf: ZDFStartLive - Sofortstart Livestream bzw. 
#	Liste Einzelauflösungen
#	
def ZDFStartLiveSingle(path, thumb, title, descr):
	PLog('ZDFStartLiveSingle:'); 
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: ZDFStartLiveSingle')
		PlayVideo(url=path, title=title, thumb=thumb, Plot=descr)
		return

	title=py2_encode(title); url_m3u8=py2_encode(path);
	thumb=py2_encode(thumb); descr=py2_encode(descr);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote_plus(url_m3u8), 
		quote_plus(title), quote_plus(thumb), quote_plus(descr))	
	addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
		tagline=title, mediatype='video')	
		
	li = Parseplaylist(li, url_m3u8, thumb, geoblock='', descr=descr)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
		
####################################################################################################
# ZDF-Suche:
# 	Voreinstellungen: alle ZDF-Sender, ganze Sendungen, sortiert nach Datum
#	Anzahl Suchergebnisse: 25 - nicht beeinflussbar
#	Format Datum (bisher nicht verwendet)
#		..&from=2012-12-01T00:00:00.000Z&to=2019-01-19T00:00:00.000Z&..
#	ZDF_Search_PATH steht bei Rekursion nicht als glob. Variable zur Verfügung
# 	02.06.2021 Umstellung auf alle Beiträge (statt ganzen Sendungen)
#
def ZDF_Search(query=None, title='Search', s_type=None, pagenr=''):
	PLog("ZDF_Search:")
	if 	query == '':	
		query = get_query(channel='ZDF')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
	
	query = query.replace(u'–', '-')# verhindert 'ascii'-codec-Error
	query = query.replace(' ', '+')	# Aufruf aus Merkliste unbehandelt	
			
	query_org = query	
	query=py2_decode(query)			# decode, falls erf. (1. Aufruf)

	PLog(query); PLog(pagenr); PLog(s_type)

	ID='Search'
	# umgestellt von ganze Sendungen auf alle Beiträge (&abName=ab-2021-06-07 kann entfallen)
	# ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&synth=true&sender=Gesamtes+Angebot&from=&to=&attrs=&abGroup=gruppe-a&page=%s'
	if s_type == 'MEHR_Suche':		# ZDF_Sendungen: Suche alle Beiträge (auch Minutenbeiträge)
		ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&sortBy=date&page=%s'

	if s_type == 'Bilderserien':	# 'ganze Sendungen' aus Suchpfad entfernt:
		ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=&sortBy=date&page=%s'
		ID=s_type
	
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path = ZDF_Search_PATH % (query, pagenr) 
	PLog(path)
	path = transl_umlaute(path)
	
	page, msg = get_page(path=path, do_safe=False)	# +-Zeichen für Blank nicht quoten	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog("searchResult: "  + searchResult);
	
	# PLog(page)	# bei Bedarf		
	NAME = 'ZDF Mediathek'
	name = 'Suchergebnisse zu: %s (Gesamt: %s), Seite %s'  % (quote(py2_encode(query)), searchResult, pagenr)

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	# Der Loader in ZDF-Suche liefert weitere hrefs, auch wenn weitere Ergebnisse fehlen
	# 22.01.2020 Webänderung 'class="artdirect " >' -> 'class="artdirect"'
	if searchResult == '0' or 'class="artdirect"' not in page:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen
		msg2 = msg 
		msg1 = 'Keine Ergebnisse (mehr) zu: %s' % query  
		MyDialog(msg1, msg2, '')
		return li	
				
	# anders als bei den übrigen ZDF-'Mehr'-Optionen gibt der Sender Suchergebnisse bereits
	#	seitenweise aus, hier umgesetzt mit pagenr - offset entfällt
	#	entf. bei Bilderserien	
	if s_type == 'Bilderserien':	# 'ganze Sendungen' aus Suchpfad entfernt:
		li, page_cnt = ZDF_Bildgalerien(li, page)
	else:
		li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID=ID)
	PLog('li, page_cnt: %s, %s' % (li, page_cnt))
	
	if page_cnt == 'next':							# mehr Seiten (Loader erreicht)
		pagenr = int(pagenr) + 1
		query = query_org.replace('+', ' ')
		path = ZDF_Search_PATH % (query, pagenr)	# Debug
		PLog(pagenr); PLog(path)
		title = "Mehr Ergebnisse im ZDF suchen zu: >%s<"  % query
		tagline = u"zusätzliche Suche starten (Seite %d)" % pagenr
		query_org=py2_encode(query_org); 
		fparams="&fparams={'query': '%s', 's_type': '%s', 'pagenr': '%s'}" %\
			(quote(query_org), s_type, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), tagline=tagline, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE)
	
#-------------------------
# Aufruf VerpasstWoche (Button "Datum eingeben")
# xbmcgui.INPUT_DATE gibt akt. Datum vor
# 11.01.2020: Ausgabe noch für 1.1.2016, nicht mehr für 1.1.2015
# sfilter wieder zurück an VerpasstWoche
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
	
	# zurück zu VerpasstWoche:
	ZDF_Verpasst(title='Datum manuell eingegeben', zdfDate=zdfDate, sfilter=sfilter)
	return
#-------------------------
# Aufruf: VerpasstWoche, ZDF_Verpasst_Datum
# Abruf Webseite, Auswertung -> ZDF_get_content
def ZDF_Verpasst(title, zdfDate, sfilter='Alle ZDF-Sender'):
	PLog('ZDF_Verpasst:'); PLog(title); PLog(zdfDate);

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	path = ZDF_SENDUNG_VERPASST % zdfDate
	page, msg = get_page(path)
	if page == '':
		msg1 = "Abruf fehlgeschlagen | %s" % title
		MyDialog(msg1, msg, '')
		return li 
	PLog(path);	PLog(len(page))

	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='VERPASST', sfilter=sfilter)
	PLog("page_cnt: " + str(page_cnt))
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# 19.11.2020 Integration funk A-Z - Ausleitung aus ZDFRubrikSingle
#
def ZDFSendungenAZ(name, ID=''):				# name = "Sendungen A-Z"
	PLog('ZDFSendungenAZ:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	azlist = list(string.ascii_uppercase)
	azlist.append('0-9')

	# Menü A to Z
	for element in azlist:
		title='Sendungen mit ' + element
		fparams="&fparams={'title': '%s', 'element': '%s', 'ID': '%s'}" % (title, element, ID)
		addDir(li=li, label=title, action="dirList", dirID="ZDFSendungenAZList", fanart=R(ICON_ZDF_AZ), 
			thumb=R(ICON_ZDF_AZ), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
# Laden der Buchstaben-Seite, Auflistung der Sendereihen in 
#	ZDF_get_content -> ZDF_Sendungen (Cluster-Abzweig) -> ZDFRubrikSingle 
#		-> ZDF_Sendungen (isvideo=False) / ZDF_BildgalerieSingle
#		-> ZDF_getVideoSources (isvideo=True)
# Buchstaben-Seiten enthalten nur Sendereihen, keine Einzelbeiträge
# 19.11.2020 Integration funk A-Z (ID=funk)
#
def ZDFSendungenAZList(title, element, ID=''):			# ZDF-Sendereihen zum gewählten Buchstaben
	PLog('ZDFSendungenAZList:')
	PLog(title)
	title_org = title
	li = xbmcgui.ListItem()	
	li = home(li, ID='ZDF')						# Home-Button

	group = element	
	if element == '0-9':
		group = '0 - 9'		# ZDF-Vorgabe (vormals '0+-+9')
	azPath = ZDF_SENDUNGEN_AZ % group
	add = "ZDF: "
	if ID == 'ZDFfunk':
		add = "funk: "
		group = "group=%s" % element
		azPath = "https://www.zdf.de/funk/funk-alle-sendungen-von-a-z-100.html?%s" % group
	PLog(azPath);
	
	page, msg = get_page(path=azPath)	
	if page == '':
		msg1 = u'AZ-Beiträge können nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
		
	content = blockextract(u'<picture class="artdirect"', page)
	if len(content) == 0:
		msg1 = u'%skeine AZ-Beiträge für die Gruppe >%s< gefunden' % (add, element)
		MyDialog(msg1, '', '')
		return li

	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=azPath, ID='A-Z')
	PLog(page_cnt)  
	if page_cnt == 0:	# Fehlerbutton bereits in ZDF_get_content
		return li		
		
	# if offset: 	Code entfernt, in Kodi nicht nutzbar
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# 	wrapper für Mehrfachseiten aus ZDF_get_content (multi=True). Dort ist kein rekursiver Aufruf
#	möglich (Übergabe Objectcontainer in Callback nicht möglich - kommt als String an)
#	Hinw.: Drei-Stufen-Test - Genehmigungsverfahren für öffentlich-rechtliche Telemedienangebote
#		s.  https://www.zdf.de/zdfunternehmen/drei-stufen-test-100.html (1. gesellsch. Bedarf,
#		2. Umfang am publiz. Wettbewerb, 3. finanzieller Aufwand)
# 	06.05.2019 Anpassung an ZDFRubrikSingle (neue ZDF-Struktur): Vorprüfung auf einz. Videobeitrag,
#		Durchreichen von tagline + thumb an ZDF_getVideoSources
#	27.09.2019 Vorprüfung wieder verlagert nach ZDFRubrikSingle (erleichtert Debugging).
#	02.09.2020 Abzweig zu ZDFRubrikSingle bei Cluster-Titeln (Bsp. Dinner Date,
#		Die Küchenschlacht)
#	19.11.2020 Ausleitung funk A-Z (aus ZDFRubrikSingle) -> ZDFSendungenAZ (Übersichtsseite)
#	20.05.2021 Cluster + Playerbox detektieren, Ausleitung -> ZDFRubrikSingle
#
def ZDF_Sendungen(url, title,ID,page_cnt=0,tagline='',thumb='',page='',skip_playerbox=False):
	PLog('ZDF_Sendungen:')
	PLog(title); PLog("ID: " + ID); 
	title_org 	= title
	page_cnt_org= int(page_cnt)
	
	li = xbmcgui.ListItem()			
	if "funk/funk-alle-sendungen-von-a-z-100.html" in url:
		ZDFSendungenAZ(title, ID='funk')
		return li 
	
	if page == '':
		page, msg = get_page(path=url)	
		if page == '':
			msg1 = u'Beitrag kann nicht geladen werden: %s' % title
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return li 
						
	if "www.zdf.de/kinder" in url:
		li = home(li, ID='Kinderprogramme')			# Home-Button
	else:
		li = home(li, ID='ZDF')						# Home-Button			


#----------------------------------------------		# Abzweig funk "Alle Folgen" -> ZDF_get_content
#	if 'www.zdf.de/funk/' in url and '>Alle Folgen</h2>' in page:
#		li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=url, ID='ZDF_Sendungen')
#		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#	08.07.2021 Abzweig >Alle Folgen< kann entfallen - keine weitere Clusterung gesichtet
#----------------------------------------------		# Abzweig Cluster -> ZDFRubrikSingle

	if 'class="b-cluster' in page:				# Cluster ermitteln, pro Cluster -> ZDFRubrikSingle
		# if ID == 'A-Z':							
		PLog('Abzweig_b_cluster')
		path = url
		# Cluster-Blöcke, dto. ZDF_Sendungen, ZDFRubrikSingle, ZDFStart:
		cluster =  blockextract('class="cluster-title-wrap">', page)
		cluster2 =  blockextract('<h2 class="title"  tabindex="0"', page)
		PLog(len(cluster)); PLog(len(cluster2))
		if len(cluster2) > 0:
			cluster = cluster + cluster2

		# Playerbox-Beiträge (Seitenanfang) voranstellen. Bei skip_playerbox
		#	liegt die Auswertung bereits vor (ZDFRubrikSingle mit Clusterliste)
		if 'data-module="zdfplayer"' in page or 'class="stage-wrapper">' in page:
			if skip_playerbox == False:
				ZDF_get_playerbox(li, page)

		if 'big-headline" tabindex="0"' in page:						# Suche nach Beiträgen vor 1. Cluster
			pos = page.find('big-headline" tabindex="0"')				# Überschriften
		else:
			pos = page.find('class="cluster-title-wrap">')				# Cluster
		page_cut = page[:pos]
		content = blockextract('<picture class="artdirect"', page_cut) # zdfplayer-Modul in artdirect möglich
		PLog("content_page_cut: %d" % len(content))	
		if len(content) > 0:									# 
			li, page_cnt = ZDF_get_content(li=li, page=page_cut, ref_path=url, ID='ZDF_Sendungen')	

		tag = 'Folgeseiten'	
		PLog('click">Altersverifikation</a>' in page)
		if 'click">Altersverifikation</a>' in page:							# FSK-Hinweis (bisher ohne Blockade)
			fsk = stringextract('-headline">Hinweis</h3>', 'click">Altersverifikation</a>', page)
			if fsk:
				fsk = stringextract('nur in der Zeit zwischen ', ' oder mit', fsk)
				fsk = "[B]FSK-Hinweis:[/B] Folgen nur zwischen %s abrufbar" % fsk
				tag = "%s\n\n%s" % (tag, fsk)			

		for clus in cluster:
			clustertitle = ZDF_get_clustertitle(clus) # Entf. html-Tags dort
			clustertitle = py2_decode(clustertitle)
			# skip: javascript-erzeugte Inhalte - s. ZDFStart,
			#	Bsp. Trending
			if 'data-tracking-title=' in clus or "Direkt zu ..." in clus:
				continue

			ctitle_org = clustertitle									# für Abgleich
			ctitle_org = ctitle_org.replace('"', '&quot;')				# Hochkommata-Behandl.
			img_src = ZDF_get_img(clus)	
			clustertitle = unescape(clustertitle); clustertitle = repl_json_chars(clustertitle) 
			PLog('11Satz:')
			
			clustertitle=py2_encode(clustertitle); path=py2_encode(path); 
			ctitle_org=py2_encode(ctitle_org)	
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s', 'ID': '%s'}"	%\
				(quote(clustertitle), quote(path), quote_plus(ctitle_org), ID)						
			addDir(li=li, label=clustertitle, action="dirList", dirID="ZDFRubrikSingle", fanart=R(ICON_DIR_FOLDER), 
				thumb=img_src, tagline=tag, fparams=fparams)

		ZDF_search_button(li, query=title_org)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------
	
	# 29.03.2020 Kurzvideos, in artdirect-Blöcken in ZDF_get_content
	#	nicht als Video erkennbar. Mehrere Videos möglich, Verarbeitung
	#	durch ZDF_getVideoSources fehlerhaft - Anpassung bzw. neue Funktion,
	#	apiToken + Link zu json-Quellen in zdfplayer-Block vorhanden.
	#	Aufruf: ZDFRubrikSingle, Ausleitung einz. Videobeiträge in
	#	ZDF_get_content (Merkmal 'class="b-playerbox')
	#	
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=url, ID='ZDF_Sendungen')
	
	PLog(page_cnt)
	if page_cnt == 0:	# Fehlerbutton bereits in ZDF_get_content
		return li
				
	if ID == 'ZDFSportLive':					# ohne zusätzliche Suche 
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
	ZDF_search_button(li, query=title_org)			# Abschluss: MEHR_Suche ZDF
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#----------------------------------------------
# MEHR_Suche ZDF nach query (title)
# Aufrufer: ZDF_Sendungen
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
  
####################################################################################################
# ZDF-Bereich, Liste der Rubriken (Filme, Serien,  Comedy & Satire,  Politik & Gesellschaft, ..)
#	Auswertung der Einzelbeiträge (nur solche) in ZDFRubrikSingle 
# 19.05.2021 Anpassung an Änderung Webseite, Cache-Nutzung für 
#	www.zdf.de/doku-wissen
# 21.11.2021 Quellen-Wechsel: Rubrik-Liste von www.zdf.de (Cache hier 5 min) 

def ZDFRubriken(name):								
	PLog('ZDFRubriken:')
	CacheTime = 60*5							# 5 min.
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	path = ZDF_BASE
	page = Dict("load", "ZDF_Start", CacheTime=CacheTime)
	if page == False or page == '':								# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", "ZDF_Start", page) 						# Seite -> Cache: aktualisieren	
	if page == '':
		msg1 = 'ZDF_Start kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 						

	pos1 = page.find(">Rubriken</h2>")
	pos2 = page.find('class="b-footer"')
	page = page[pos1:pos2]
	dirID="ZDFRubrikSingle"

	cluster = blockextract('class="b-cluster-teaser b-vertical-teaser', page, '</article')
	lazy = blockextract('class="b-cluster-teaser m-placeholder lazyload', page, '</article')
	rubriken = cluster + lazy
	PLog(len(rubriken))
	
	for rec in rubriken:
		if 'class="loader"' in rec:									# Nachlade-Beiträge, escaped, s. ZDFRubrikSingle
			pos  = rec.find('class="loader"')						# Satz begrenzen (Kennz. steht
			rec = rec[:pos]											#	am Ende
			rec = unescape(rec)
			rec = rec.replace('": "', '":"')						# 10.12.2019 wieder mal Blank nach Trenner
			PLog('loader_Beitrag')
			sophId,NodePath,path,title,descr,img_src,dauer,isvideo,teaser_typ,teaser_nr,\
				teaser_brand,teaser_count = get_teaserElement(rec)
			#PLog('title: %s, path: %s, img_src: %s, descr: %s, dauer: %s' %\
			#	(title,path,img_src,descr,dauer))
			
		else:
			title = stringextract('"teaser-title"', 'class', rec)
			path = ZDF_BASE + stringextract('href="', '"', title)	# z.B. href="/Filme"
			title = stringextract('title="', '"', title)
			img_src = ZDF_get_img(rec)
			descr = stringextract('extended-text">', '<', rec)
		
		label = unescape(title)
		tag = descr; 
		PLog("Satz23:")
		PLog(title); PLog(img_src); PLog(path); PLog(tag[:80]) 		
			
		title=py2_encode(title); path=py2_encode(path); 
	
		if title.startswith('ZDFtivi'):								# Kinder: Umlenkung -> tivi Modul childs
			GIT_ZDFTIVI	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-zdftivi.png?raw=true"
			ICON_CHILDS	= 'childs.png'	
			tag = "Kinder- und Jugendprogramm des ZDF"		
			fparams="&fparams={'title': '%s'}" % "tivi"
			addDir(li=li, label= "ZDFtivi für Kinder", action="dirList", dirID="resources.lib.childs.Main_TIVI", 
				fanart=R(ICON_CHILDS), thumb=GIT_ZDFTIVI, tagline=tag, fparams=fparams)		
		else:
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s'}"	%\
				(quote(title), quote(path), "")						
			addDir(li=li, label=label, action="dirList", dirID="ZDFRubrikSingle", fanart=R(ICON_MAIN_ZDF), 
				thumb=img_src, tagline=tag, fparams=fparams)			
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-------------------------
# ZDF-Bereich, Sendungen einer Rubrik (unbegrenzt, anders als A-Z Beiträge)
#	Besonderheit: die Zielseiten enthalten class="loader" (Nachlade-Beiträge, 
#	escaped).
#	Aufruf auch aus ZDFStart (Struktur wie ZDF-Rubriken),
#		ab 03.09.2020 auch aus ZDF_Sendungen (ID=A-Z).
#	2-facher Aufruf - Unterscheidung nach Cluster-Titeln (clus_title):
#		1. Übersichtseite (Cluster)			- Rücksprung hierher
#		2. Zielseite (z.B. einzelne Serie) 	- Sprung -> ZDF_Sendungen
# 	ZDF_Sendungen macht eine Vorprüfung auf Einzelvideos vor Aufruf von
#		ZDF_get_content. Einzelvideos -> ZDF_getVideoSources
#
#	Hinw.: "Verfügbar bis" bisher nicht in Rubrikseiten gefunden (wie
#		teaserElement, s. get_teaserElement)
#
# 27.09.2019 ZDF-Änderungen bei den Abgrenzungen der Cluster (s.u. Blockbildung)
# 22.11.2019 Nutzung bereits geladener Seite / Seitenausschnitt (page)
# 10.12.2019 ZDFRubriken: Abgleich Cluster-Titel wird mittels spez. clus_title 
#	übersprungen )
# 03.09.2020 Nutzung für A-Z-Seiten mit Cluster-Titeln (Abzweig in ZDF_Sendungen)
#	Auswertung für loader- und Normal-Seiten vereinheitlicht (get_teaserElement,
#	ZDF_get_teaserDetails, ZDF_get_teaserbox)
# 05.09.2020 promo-teaser in ZDFStart + hier ergänzt (bisher nur 1 x je Seite gesichtet)
# 22.01.2021 custom_cluster: vom Aufrufer def. Anfangs- und Endbedingung, 
#	z.B. '>Spielberichte<|</section>'
# 
def ZDFRubrikSingle(title, path, clus_title='', page='', ID='', custom_cluster='', nav_title=''):							
	PLog('ZDFRubrikSingle:'); PLog(title);
	CacheTime = 60*5								# 5 min.
	PLog(clus_title); PLog(ID); PLog(custom_cluster); PLog(nav_title)
	clus_title = clus_title.replace('&quot;', '"')				# Hochkommata-Behandl. (s. ZDF_Sendungen)
 
	path_org = path
	
	title_org = title
	li = xbmcgui.ListItem()
	if "www.zdf.de/kinder" in path:
		li = home(li, ID='Kinderprogramme')			# Home-Button 
	else:
		li = home(li, ID='ZDF')						# Home-Button

	dictid = path.split('/')[-1]
	if page == '':
		page = Dict("load", dictid, CacheTime=CacheTime)
		if page == False or page == '':				# Cache miss od. leer - vom Sender holen
			page, msg = get_page(path=path)	
			Dict("store", dictid, page) 			# Seite -> Cache: aktualisieren	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
		
	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'	

	if custom_cluster == '':										# Abgleich mit clus_title
		# Cluster-Blöcke, dto. ZDF_Sendungen, ZDFRubrikSingle, ZDFStart:
		cluster =  blockextract('class="cluster-title-wrap">', page)# Cluster-Blöcke
		PLog(len(cluster))
		cluster = cluster + blockextract('"section-header-title', page, "</section>")
		if len(cluster) == 0:										# aus promo-teaser
			cluster =  cluster + blockextract('class="big-headline"', page, '')
		if len(cluster) == 0:										
			cluster =  cluster + blockextract('headline-with-btn', page, '')
		if len(cluster) == 0:										
			cluster =  blockextract('class="top5-headline"', page, '')
		cluster =  cluster + blockextract('<h2 class="title"  tabindex="0"', page)
		PLog(len(cluster))
		
		if clus_title and len(cluster) > 0:							# Beiträge zu gesuchtem Cluster auswerten - s.o.
			clus_title = py2_encode(clus_title)
			if clus_title.startswith('>'):
				clus_title = clus_title[1:]
			for clus in cluster:
				clustertitle = ZDF_get_clustertitle(rec=clus)		# Cluster-Titel ermitteln
				clustertitle = py2_decode(clustertitle)
				clus_title = py2_decode(clus_title)
				PLog(clus_title); PLog(clustertitle);	 # Debug
				PLog(clus_title in clustertitle)
				if clus_title in clustertitle:		# Cluster gefunden
					PLog('gefunden: clus_title=%s, clustertitle=%s' % (clus_title, clustertitle))
					break
					
	else:															# freie Anfangs- und Endbedingung
		#custom_cluster=py2_encode(custom_cluster)
		PLog(custom_cluster)
		blockstart, blockend = custom_cluster.split("|")
		cluster =  blockextract(blockstart, page, blockend)
		PLog(len(cluster))
		if clus_title and len(cluster) > 0:							# Beiträge zu gesuchtem Cluster auswerten - s.o.
			for clus in cluster:
				if  clus_title in clus:
					PLog('gefunden: clus_title=%s' % clus_title)
					break
		
	if clus_title and len(cluster) > 0:	
		# script-gesteuerte Beiträge ("clusterrecommendation") z.Z. nicht genutzt.
			
		# 27.09.2019 Blockbildung geändert (nach ZDF-Änderungen)
		# class="artdirect"> und class="artdirect " nicht eindeutig genug,
		# b-cluster-teaser umfassen die article-Blöcke und lazyload-Blöcke
		# lazyload-Blöcke können Einzelbeiträge enthalten (teaserElement: icon-502_play)
		# 28.03.2020 'class="artdirect' als Fallback (u.a. für 'class="artdirect cell">')
		# 08.07.2021 skip_list hinzugefügt (z.B. für funk-SendungenA-Z), verlässlichere
		#	Blockbildung via "article class".
		# 13.07.2021 Blockbegrenzung </article> erst im rec -  loader-Beiträge werden sonst
		#	ausgeschlossen

		skip_list = [u"https://www.zdf.de/funk/funk-alle-sendungen-von-a-z-100.html"]	# Abgleich 
		if '"PromoTeaser"' in clus:							# Promo-Teasern fehlt "article class"
			article = "PromoTeaser"
			content = [clus]								# je Promo-Teaser nur 1 Block
			PLog(clus[:80])
		else:
			article = stringextract('<article class="', ' ', clus)	# class für Block bestimmen
			if article.startswith('class="b-cluster"'):		# ohne Blank hinter class-Marke
					article = 'class=b-cluster'
			content =  blockextract('class="%s' % article, clus) # Begrenzung </article> erst in rec
		PLog("article: " + article)
		PLog('content1: ' + str(len(content)))

		for rec in content:				
			title='';  clustertitle=''; lable=''; isvideo=False; isgallery=False
			teaser_nr=''; summ_txt=''; descr='';teaserDetails=''
			pos = rec.find('</article>')						# Satz begrenzen (im Block n.m., s.o.)
			if pos > 0:
				rec = rec[:pos]
			
			
			# --------------------------------------------------	
			if 'class="loader"' in rec:							# Nachlade-Beiträge, escaped
				pos  = rec.find('class="loader"')				# Satz begrenzen (Kennz. steht
				rec = rec[:pos]									#	am Ende
				rec = unescape(rec)
				rec = rec.replace('": "', '":"')				# 10.12.2019 wieder mal Blank nach Trenner
				PLog('loader_Beitrag')
				# PLog(rec); 	# bei Bedarf
				#	Auswertung Loader-Beitrag einschl. teaserbox
				sophId,NodePath,path,title,descr,img_src,dauer,isvideo,teaser_typ,teaser_nr,\
					teaser_brand,teaser_count = get_teaserElement(rec)
			# --------------------------------------------------	
			else:												# Seite normal auswerten	
			# --------------------------------------------------
				title,path,img_src,descr,dauer,enddate,isvideo = ZDF_get_teaserDetails(rec)
				teaserDetails='done'							# Flag für get_summary_pre
				# multi z.Z. nicht verwendet, isvideo reicht aus
				teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count,multi = ZDF_get_teaserbox(rec)
			
			PLog("isvideo: %s, dauer: %s" % (isvideo, dauer))
			PLog(enddate);
			#if isvideo == True and dauer == '':						# filtert 'Demnächst'-Beiträge aus
			#	continue

			tag='';
			if path == '' or 'skiplinks' in path:
				PLog('skip_path: ' + path)
				continue
			if path in skip_list:										# z.B. funk-SendungenA-Z
				PLog('skip_list: ' + path)
				continue
				
			if teaser_label:
				tag = teaser_label
			if teaser_brand:
				teaser_brand = teaser_brand.replace(' - ', '')
				teaser_brand = "[COLOR red]%s[/COLOR]" % teaser_brand
				tag = teaser_brand
				
			if teaser_typ:
				tag = "%s | %s" % (tag, teaser_typ)
			if teaser_nr:
				tag = "Episode %s | %s" % (teaser_nr, tag)
				title = "[%s] %s" % (teaser_nr, title)
			if tag.startswith(' | '):									# tag-Korr. leer Brand								
				tag = tag.replace(' | ', '')
			tag = tag.replace('  ,', ', ')
								
			if teaser_label == 'Bilderserie':
				PLog('Bilderserie')
				isgallery = True
			
																		# Formatierung
			if 'Folgen' in tag or 'Staffeln' in tag or 'Teile' in tag:		
				title = teaser_label.ljust(11) + "| %s" % title
				# Einzelvideo bei Folgen ausgeblenden, um Folge auszuwerten 				
										
			if descr and dauer:
				descr = "%s\n\n%s" % (dauer, descr)
			if clustertitle:
					descr = "%s | %s" % (clustertitle, descr.strip())
			title = repl_json_chars(py2_decode(title));
			descr = repl_json_chars(descr)
			if tag:
				descr = "%s\n\n%s" % (tag, descr)
			descr_par = descr.replace('\n', '||')
			
			if '>Jetzt live</h2>' in rec:								# Livestream-Satz?
				PLog('>Jetzt live</h2>')
				title = '[COLOR red][B]%s[/B][/COLOR]' % title
			lable = title
			
						
			if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
				filtered=False
				for item in AKT_FILTER: 
					item = up_low(item)
					# rec ist hier lazyload-Element, Inhalte fehlen für Abgleich!
					if up_low(item) in up_low(title) or up_low(item) in up_low(descr):
						filtered = True
						break		
				if filtered:
					PLog('filtered: ' + title)
					continue	
			
			PLog('12Satz:')
			PLog(title);PLog(path);PLog(img_src);PLog(tag);PLog(descr); 
			PLog(isvideo);PLog(multi);PLog(isgallery);
			descr=py2_encode(descr)
			
			if isvideo == False:			# Mehrfachbeiträge
				ID='ZDFRubrikSingle'
				title=py2_encode(title); path=py2_encode(path); ID=py2_encode(ID);
				descr_par=py2_encode(descr_par); img_src=py2_encode(img_src);
				
				 
				if isgallery == False:		# keine Bildgalerie
					fparams="&fparams={'title': '%s', 'url': '%s', 'ID': '%s', 'tagline': '%s', 'thumb': '%s'}"	%\
						(quote(title),  quote(path), quote(ID), quote(descr_par), quote(img_src))
					addDir(li=li, label=lable, action="dirList", dirID="ZDF_Sendungen", fanart=img_src, 
						thumb=img_src, summary=descr, fparams=fparams)
				else:						# Bildgalerie
					fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))	
					addDir(li=li, label=lable, action="dirList", dirID="ZDF_BildgalerieSingle", fanart=img_src, 
						thumb=img_src, fparams=fparams, summary='Bilderserie', tagline=descr)
					
					
			else:							# Einzelbeitrag direkt - anders als A-Z (ZDF_get_content)		
				if SETTINGS.getSetting('pref_load_summary') == 'true':		# Inhaltstext im Voraus laden?
					# get_summary_pre in ZDF_get_teaserDetails bereits erledigt
					if teaserDetails == '':									
						skip_verf=False; skip_pubDate=False					# beide Daten ermitteln
						summ_txt = get_summary_pre(path, 'ZDF', skip_verf, skip_pubDate)
						PLog(len(summ_txt)); PLog(len(descr));
						if 	summ_txt and len(summ_txt) > len(descr):
							descr= summ_txt
							descr_par = descr.replace('\n', '||')
							
				title=py2_encode(title); path=py2_encode(path); 
				descr_par=py2_encode(descr_par); img_src=py2_encode(img_src); 	
				fparams="&fparams={'title': '%s', 'url': '%s', 'tagline': '%s', 'thumb': '%s'}"	%\
					(quote(title),  quote(path), quote(descr_par), quote(img_src))
				addDir(li=li, label=lable, action="dirList", dirID="ZDF_getVideoSources", fanart=img_src, 
					thumb=img_src, summary=descr, mediatype=mediatype, fparams=fparams)
							
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
	else:												# nur Cluster listen, ohne Bilder, 
														#	Blockbegrenzung s.o.
		#page_title = stringextract('<title>', '</title>', page)			# z.Z.  nicht genutzt
		#page_descr = stringextract('description" content="', '"', page)
		#page_title=mystrip(page_title); page_title=unescape(page_title)
		#page_descr=mystrip(page_descr); page_descr=unescape(page_descr)
		
		PLog("nav_list_Check")			
		if 'class="second-nav-list">' in page:			# ev. Navigationsleiste berücksichtigen, Bsp. zdf.de/sport
			if nav_title == '':							# 1. Aufruf (ohne Wahl in Navigationsleiste)
				nav_list = stringextract('class="second-nav-list">', '</ul>', page)	
				nav_list = blockextract('<a href', nav_list)
				for item in nav_list:
					path =  ZDF_BASE + stringextract('href="', '"', item)
					title = stringextract('title="', '"', item)
					title = unescape(title)
					tag = u"Navigation: %s -> %s" % (title_org, title)
					img_src = R(ICON_DIR_FOLDER)
					
					title=py2_encode(title); path=py2_encode(path); 
					fparams="&fparams={'title': '%s', 'path': '%s', 'nav_title': '%s'}" % (quote(title),
						quote(path), quote(title))
					addDir(li=li, label=title, action="dirList", dirID="ZDFRubrikSingle", fanart=img_src, 
						thumb=img_src, tagline=tag, fparams=fparams)
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
			
			
		# Auswertung "zdfplayer" Seitenanfang (Highlights, Empfehlungen):
		PLog("zdfplayer_Check")
		skip_list=[]			
		if 'data-module="zdfplayer"' in page or 'class="stage-wrapper">' in page:
			skip_list = ZDF_get_playerbox(li, page, skip_list)			#  o. skip_list

		PLog("no_title_Check")											# Beiträge ohne Clustertitel ausgeben
		pos1 = page.find('class="b-content-teaser-list no-title"')
		if pos1 > 0:
			pos2 = page.find('"b-content-teaser-list"')					# ev. Varianten prüfen
			PLog("%d, %d" % (pos1, pos2))
			if pos2 > 0 and pos2 > pos1:								# Blockende < Blockanfang mögl.
				page_cut = page[pos1:pos2]
				# ID="ZDF_Sendungen" unterdrückt zdfplayer-Block in ZDF_get_content:
				ZDF_get_content(li, page=page_cut, ref_path=path_org, ID="ZDF_Sendungen", skip_list=skip_list)
				# xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# Debug
		
		i=0
		for clus in cluster:							# Cluster: cluster-title + section-header-title	- s.o.
			clustertitle=''
			i=i+1
			PLog("cluster_%d" % i)
			PLog(clus[:80])
			clustertitle = ZDF_get_clustertitle(clus)
			clustertitle = py2_decode(clustertitle)
				
			label =	unescape(clustertitle); 
			label = repl_json_chars(label)
			clustertitle = repl_json_chars(clustertitle)
			if '>' in label:							# Bsp.: data-tracking-title="Beliebte_Serien">Bel..
				label = label.split('>')[1]
				
			PLog("clustertitle: " + clustertitle);	
			if 'data-module="zdfplayer"' in clus:		# bereits erfasst
				continue		
			if 'Direkt zu ...' in clustertitle: 		# in zdf.de/kinder, hier nicht erreichbar
				continue
			if clustertitle.endswith('weiterschauen'): 	# in zdf.de/kinder, .. weiterschauen
				continue
			if 'In eigener Sache' in clustertitle: 		# dto. (vorwiegend redakt. Seiten)
				continue
			if clustertitle.strip() == '': 
				continue
			if 'eliebte Filme' in clustertitle or 'eliebte Serien' in clustertitle or 'Dich interessieren' in clustertitle:
				continue
				
				
			#img_src = R(ICON_DIR_FOLDER)
			img_src = ZDF_get_img(clus)
			clustertitle=py2_encode(clustertitle); path=py2_encode(path); 
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s'}" % (quote(clustertitle),
				quote(path), quote(clustertitle))
			addDir(li=li, label=label, action="dirList", dirID="ZDFRubrikSingle", fanart=img_src, 
				thumb=img_src, fparams=fparams)
				
		if path_org.endswith('sport-im-zdf-livestream-live-100.html'):	# ZDF Event Streams einblenden
			fparams="&fparams={}"
			label =u'ZDF Event Streams (eingeschränkt verfügbar)'
			img = R("zdf-sportlive.png")	
			addDir(li=li, label=label, action="dirList", dirID="ZDFSportEvents", fanart=img, 
				thumb=img, fparams=fparams)	
	
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-------------------------
# Ersatz für javascript: Ermittlung Icon + Sendedauer (Nachlade-Beiträge, 
#	escaped' - class="loader")
#	die html-Seite des get_teaserElements wird aus TEXTSTORE 
#	geladen bzw. bei www.zdf.de/teaserElement abgerufen und
#	dann in TEXTSTORE gespeichert.
#	Hinw.1: "Verfügbar bis" nicht immer im teaserElement enthalten
#   Hinw.2: Änderungen ev. auch in my3Sat erforderlich.
# 03.09.2020 ergänzt um Auswertung teaserbox
#
def get_teaserElement(rec):
	PLog('get_teaserElement:')
	# Reihenfolge Ersetzung: sophoraId, teaserHeadline, teasertext, filterReferenceId, 
	#		contextStructureNodePath
	#	vorbelegt (nicht ausgewertet):
	#		style, mostwatched, recommended, newest, reloadTeaser, mainContent, 
	#		sourceModuleType, highlight
	# PLog(rec)	
	sophoraId = stringextract('"sophoraId":"', '",', rec)
												
	teaserHeadline = stringextract('teaserHeadline":"', '",', rec)
	teaserHeadline = teaserHeadline.replace('"', '')
	teasertext = stringextract('"teasertext":"', '",', rec)
	filterReferenceId = stringextract('filterReferenceId":"', '",', rec)
	contextStructureNodePath = stringextract('contextStructureNodePath":"', '",', rec)
	
	mostwatched = stringextract('"mostwatched":"', '",', rec)
	recommended = stringextract('"recommended":"', '",', rec)
	newest = stringextract('"newest":"', '",', rec)
	
	teaserHeadline = transl_json(teaserHeadline); teasertext = transl_json(teasertext); 
	sophId = sophoraId; title = teaserHeadline; descr = teasertext;  	# Fallback-Rückgaben
	NodePath = contextStructureNodePath; 
	
	# urllib.quote_plus für Pfadslash / erf. in contextStructureNodePath
	sophoraId = quote_plus(py2_encode(sophoraId)); 
	contextStructureNodePath = quote_plus(py2_encode(contextStructureNodePath));
		
	# ähnl. 3sat - nicht erforderlich: teaserHeadline, teasertext
	path = "https://www.zdf.de/teaserElement?sophoraId=%s&style=m2&reloadTeaser=true&filterReferenceId=%s&mainContent=false&sourceModuleType=cluster-s&highlight=false&contextStructureNodePath=%s" \
		% (sophoraId, filterReferenceId, contextStructureNodePath)


	fpath = os.path.join(TEXTSTORE, sophoraId)		# 1. Cache für teaserElement
	PLog('fpath: ' + fpath)
	if os.path.exists(fpath) and os.stat(fpath).st_size == 0: # leer? = fehlerhaft -> entfernen 
		PLog('fpath_leer: %s' % fpath)
		os.remove(fpath)
	if os.path.exists(fpath):						# Element lokal laden
		PLog('lade_lokal:') 
		page =  RLoad(fpath, abs_path=True)	
	else:											# von www.zdf.de/teaserElement laden
		page, msg = get_page(path=path)			
		if page:									# und in TEXTSTORE speichern - bei Bedarf
			msg = RSave(fpath, py2_encode(page))	#	withcodec verwenden (s. my3Sat)
		
	PLog(page[:100])
	page = py2_decode(page)
	isvideo = False
	if page:										# 2. teaserElement einschl. teaserbox auswerten
		title,path,img_src,descr,dauer,enddate,isvideo = ZDF_get_teaserDetails(page, NodePath, sophId)
		# multi z.Z. nicht verwendet, isvideo reicht aus
		teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count,multi = ZDF_get_teaserbox(page)		
		# sophId s.o.
		return sophId,NodePath, path,title,descr,img_src,dauer,isvideo,teaser_typ,teaser_nr,teaser_brand,teaser_count	
	else:									#  Fallback-Rückgaben, Bild + Dauer leer
		img_src=''; dauer=''; NodePath=''
		return sophId,NodePath,path,title,descr,img_src,dauer,isvideo,teaser_typ,teaser_nr,teaser_brand,teaser_count

#-------------------------
# Auswertung ZDF-Seite für ZDFRubrikSingle
# page hier Einzelblock (rec)
#	
def ZDF_get_teaserDetails(page, NodePath='', sophId=''):
	PLog('ZDF_get_teaserDetails:')
	title='';path='';img_src='';descr='';dauer='';enddate='';isvideo=False
	img_src = ZDF_get_img(page)
		
	title	= stringextract('plusbar-title="', '"', page)
	if title == '':
		if '<span class="normal-space">' in page:
			title= stringextract('<span class="normal-space">', '<span class=', page)
			title = title.strip()
	if title == '':
		title	= stringextract('title="', '"', page)					# href-Titel			
		
	title = unescape(title);
	title = repl_json_chars(py2_decode(title));
	enddate	= stringextract('-end-date="', '"', page)					# kann leer sein, wie get_teaserElement
	enddate = time_translate(enddate, add_hour=0)

	path	= stringextract('plusbar-url="', '"', page)
	if path == '':
		path	= stringextract('href="', '"', page)					# Fallback 1
	if path == '':
		path	= stringextract('href = "', '"', page)					# Fallback 2
	if path == '':
		if 	NodePath and sophId:											
			path	= "https://www.zdf.de%s/%s.html" % (NodePath, sophId)# Fallback 3
	if path and path.startswith('http') == False:
		path = ZDF_BASE + path
		
	PLog("Videolänge2:")
	icon502 = stringextract('"icon-502_play', '</dl>', page) 			# Länge - 1. Variante
	# PLog(icon502)	
	try:
		dauer = re.search(u'aria-label="(\d+) min"', icon502).group(1)
	except:
		dauer=''
	if dauer == '':	
		try:															# Länge - 2. Variante
			dauer = re.search(u'label="Videolänge (\d+) min', icon502).group(1)
		except Exception as exception:
			dauer=''
	if dauer == '':
		dauer = stringextract(u'Videolänge', 'min', icon502) 				# Länge - 2. Variante bzw. fehlend
	if dauer:
		dauer = "%s min" % cleanhtml(dauer) 
		dauer = mystrip(dauer.strip())
	if '<dd class="teaser-info" aria-label="' in dauer:
		dauer =  dauer.replace('<dd class="teaser-info" aria-label="', '')	
	
	descr	= stringextract('teaser-text"', '<', page)					# > mit/ohne Blank möglich
	descr	= descr.replace('>', '')
	if descr == '':
		descr	= stringextract('teaser-info" aria-label="', '"', page)	
	if descr == '':
		descr	= stringextract('extended-text">', '<', page)	
	if descr == '':
		descr = stringextract('alt="', '"', page)						# Fallback Bildbeschr.
		
	descr = unescape(descr); descr = descr.strip()
	if u'Videolänge' in descr:
		dauer=''
		isvideo = True
	PLog(descr)
	
	enddate=py2_decode(enddate); descr=py2_decode(descr)
	if enddate:
		descr = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s\n" % (enddate, descr)
	if 'class="icon-502_play' in page:
		isvideo = True
	
		
	if SETTINGS.getSetting('pref_load_summary') == 'true':				# Inhaltstext im Voraus laden?
		skip_verf=False; skip_pubDate=False								# Teaser enth. beide Daten
		summ_txt = get_summary_pre(path, 'ZDF', skip_verf, skip_pubDate)
		PLog(len(summ_txt)); 
		if 	summ_txt and len(summ_txt) > len(descr):
			descr= summ_txt
			
	PLog('title: %s, path: %s, img_src: %s, descr: %s, dauer: %s, enddate: %s, isvideo: %s' %\
		(title,path,img_src,descr,dauer,enddate,isvideo))
		
	return title,path,img_src,descr,dauer,enddate,isvideo
			
#-------------------------
def ZDF_get_img(page):
	PLog('ZDF_get_img:')
	#PLog(page)			# Debug
	
	page = page.replace('data-srcset=""',  '')		# möglich: data-srcset=""
	
	img =  stringextract('data-srcset="', ' ', page)
	if img == '':
		img = stringextract('-srcset="', ' ', page)
	if img == '':
		img =  stringextract('data-src="', ' ', page)
		
	if img.startswith('data:image'):				# gif-Pixelreihe
		img = stringextract('srcset="https://www.zdf.de', ' ', page) 
		
	if img== '':									# Fallback, Altern.: icon-bild-fehlt.png
		img= R('Dir-folder.png')
		return img
	img = img.replace('"', '')						# solte nicht vorkommen
	
	if img.startswith('http') == False:
		img = ZDF_BASE + img
	PLog(img)
	return img
#-------------------------
# wertet die (teilw. unterschiedlichen) Parameter von
#	class="bottom-teaser-box"> aus.
# Aufrufer: ZDFRubrikSingle, get_teaserElement (loader-
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
			teaser_typ = re.search(u'>(\d+) Teile', teaser_label).group(0)
		except:
			teaser_typ=''
	teaser_label = mystrip(teaser_label) 
	teaser_label = teaser_label.replace('<div class="ellipsis">', ' ')
	teaser_label = (teaser_label.replace('<strong>', '').replace('</strong>', ''))

	PLog('teaser_label: %s,teaser_typ: %s, teaser_nr: %s, teaser_brand: %s, teaser_count: %s, multi: %s' %\
		(teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count, multi))
		
	return teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count,multi
	
#-------------------------
# ermittelt html-Pfad in json-Listen für ZDFRubrikSingle
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
####################################################################################################
def MeistGesehen(name):							# ZDF-Bereich, Beiträge unbegrenzt
	PLog('MeistGesehen'); 
	title_org = name
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	path = ZDF_SENDUNGEN_MEIST
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
		
	# unbegrenzt (anders als A-Z Beiträge):
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='MeistGesehen')
	
	PLog(page_cnt)
	# if offset:	Code entfernt, in Kodi nicht nutzbar
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
####################################################################################################
# ZDF Barrierefreie Angebote - Vorauswahl
#	ARD siehe BarriereArmARD (Classic)
# 06.04.2020 aktualisiert: Webseite geändert, nur kleine Übersicht, die 3
#	Folgeseiten enthalten jeweils die neuestens Videos 
# 13.12.2020 Anpassungen an Webseitenänderungen
#
def BarriereArm(title):				
	PLog('BarriereArm:')
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')							# Home-Button
	
	# kleine Übersicht, Cache n.  erf.
	path = ZDF_BARRIEREARM							# www.zdf.de/barrierefreiheit-im-zdf/
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
	PLog(len(page))
	
	# z.Z. 	>Gebärdensprache<
	#		>Untertitel<
	#		>Hörfilme<
	content = blockextract('<section class="b-content-teaser-list"', page)
	PLog(len(content))
	content = blockextract('class="artdirect"', content[0])	# 2. Block: Service (nicht verw.)
	PLog(len(content))
	
	if SETTINGS.getSetting('pref_usefilter') == 'true':
		if 'Audiodeskription' or 'Hörfassung' in AKT_FILTER:
			msg1 = 'Hinweis:'
			msg2 = 'Filter für Hörfassungen und/oder Audiodeskription ist eingeschaltet!'
			MyDialog(msg1, msg2, '')	
	
	i=0
	for rec in content:	
		i=i+1
		ID = "ID_%d" % i						# Titel n. als iD geeignet
		title = stringextract('class="teaser-text">', '</p>', rec)
		title = title.replace('\n', ''); 
		title = (title.replace('>', '').replace('<', '')); title = title.strip()
				
		path = stringextract('href="', '"', rec)
		if path.startswith('http') == False:
			path = ZDF_BASE + path
			
		img_src = ZDF_get_img(rec)	
		
		tag = u"Übersicht der neuesten Videos"
		PLog(title); PLog(path); PLog(img_src); 
		if u'Livestreams' in title:				# nur EPG, kein Video
			PLog('skip: '  + title)
			continue
		
		PLog("Satz7:")
		PLog(title);	PLog(path)	
		ID = 'BarriereArm_%s' % str(i)		
		path=py2_encode(path); title=py2_encode(title);	
		fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" % (quote(path), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="BarriereArmSingle", fanart=R(ICON_ZDF_BARRIEREARM),
			thumb=img_src, fparams=fparams, tagline=tag)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------------------
# Aufrufer: BarriereArm (ZDF Barrierefreie Angebote)
#	ARD s. BarriereArmARD (Classic)
#	2-facher Aufruf - Unterscheidung nach Titeln (class="title"):
#		1. Übersichtseite (Titel)			- Rücksprung hierher
#		2. Zielseite (z.B. einzelne Serie) 	- Sprung -> ZDFRubrikSingle
# 01.08.2020 Anpassungen an  Webänderungen, einschl. lazyload-Beiträge
# 21.05.2021 eneute Anpassung an Webänderung, zusätzl. Clusterung wie in 
#	ZDF_Sendungen
#	 
def BarriereArmSingle(path, title, clus_title='', ID=''):
	PLog('BarriereArmSingle: ' + title)
	PLog(clus_title); PLog(path)
	CacheTime = 6000								# 1 Std.
			
	li = xbmcgui.ListItem()	

	msg=''
	page = Dict("load", ID, CacheTime=CacheTime)
	if page == False:								# Cache miss - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", ID, page) 					# Seite -> Cache: aktualisieren	
	if page == '':							
		msg1 = '%s: Seite kann nicht geladen werden.' % "BarriereArmSingle"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 
		
	PLog(len(page))
	
	# Cluster-Blöcke, dto. ZDF_Sendungen, ZDFRubrikSingle, ZDFStart:
	cluster =  blockextract('class="cluster-title-wrap">', page)
	PLog(len(cluster))
	
	if clus_title:								# 2. Aufruf: Beiträge zu Cluster-Titel auswerten
		for clus in cluster:					# wie Abzweig_b_cluster in ZDF_Sendungen
			clustertitle = ZDF_get_clustertitle(clus) # Entf. html-Tags dort
			clustertitle = py2_decode(clustertitle)
			# skip: javascript-erzeugte Inhalte - s. ZDFStart,
			#	Bsp. Trending
			if 'data-tracking-title=' in clus:
				continue

			ctitle_org = clustertitle			# für Abgleich
			img_src = ZDF_get_img(clus)	
			clustertitle = unescape(clustertitle); clustertitle = repl_json_chars(clustertitle) 
			
			clustertitle=py2_encode(clustertitle); path=py2_encode(path); 
			ctitle_org=py2_encode(ctitle_org)	
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s', 'ID': '%s'}"	%\
				(quote(clustertitle), quote(path), quote(ctitle_org), ID)						
			addDir(li=li, label=clustertitle, action="dirList", dirID="ZDFRubrikSingle", fanart=R(ICON_DIR_FOLDER), 
				thumb=img_src, tagline="Folgeseiten", fparams=fparams)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
							
	else:										# 1. Aufruf: nur Cluster-Titel + Bild listen 
		li = home(li, ID='ZDF')							# Home-Button
		for clus in cluster:
			if u'könnten Dich interessieren' in clus: 	# Wiederholung der Cluster
				continue
			clustertitle = ZDF_get_clustertitle(clus)
			clustertitle = py2_decode(clustertitle)
			if 'Livestream' in clustertitle:
				continue
			img = R(ICON_DIR_FOLDER)					# Fallback
			img_src =  stringextract('class="m-16-9"', '</picture>', clus)
			img_src =  blockextract('https://', img_src, ' ')
			for img in img_src:
				if '720' in img or '1080' in img:
					break
			
			content = blockextract('class="b-cluster-teaser', clus)	# Beiträge/Cluster einschl. lazyload
			tag = u"%d Beiträge" % len(content)
			PLog("Satz15:")
			PLog(clustertitle); PLog(img); PLog(tag)
		 
			clustertitle=py2_encode(clustertitle); path=py2_encode(path); 
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s', 'ID': '%s'}" %\
				(quote(clustertitle), quote(path), quote(clustertitle), ID)
			addDir(li=li, label=clustertitle, action="dirList", dirID="BarriereArmSingle", fanart=img, 
				thumb=img, fparams=fparams, tagline=tag)	
								
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
####################################################################################################
# Leitseite zdf-sportreportage - enthält Vorschau mit Links zu den Reportageseiten - Auswertung in
#	ZDFSportLiveSingle. 
#	Angefügt: Button für zurückliegende Sendungen der ZDF-Sportreportage.
#	Angefügt: Button für Sprung zum Livestream (unabhängig vom Inhalt)
#	Angefügt: Button für Sprung zu Ganze Wettbewerbe	05.12.2020
# Bei aktivem Livestream wird der Link vorangestellt (Titel: rot/bold),
# Stream am 27.04.2019: 
#	http://zdf0304-lh.akamaihd.net/i/de03_v1@392855/master.m3u8
#		ohne Zusatz (Web-Url) ?b=0-776&set-segment-duration=quality
# 29.04.2019 Button für Livestream wieder entfernt (Streams wechseln), dto. Eintrag livesenderTV.xml
# 20.12.2020 Eventstreams aufgenommen (analog ARDSport)
# 12.11.2021 Einfügung zeitl. begrenzter Events (Wintersport, Handball-WM) - ähnl. ARDSportPanel
# 27.05.2021 Live-Videolink nicht mehr in Webseite - Ermittlung via apiToken in ZDF_getVideoSources
# 21.08.2021 ZDFSportLive + ZDFSportLiveSingle entfernt - abgedeckt durch Rubrik Sport 
#	(mit Auswertung der Navi.-Leiste). ZDFSportEvents weiter genutzt (ZDFRubrikSingle).
#	Ebenfalls entfernt: ZDFRubrikSingleCall (Nutzung ZDFSportLive zur Vermeidung 'setLabel'-error).
####################################################################################################

def ZDFSportEvents():
	PLog('ZDFSportEvents:');
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	

	channel = u'ZDF Event Streams (eingeschränkt verfügbar)'									
	img = R("zdf-sportlive.png")				# dummy	
	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender='')
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	 			
####################################################################################################
def International(title):
	PLog('International:'); 
	title_org = title
	CacheTime = 6000								# 1 Std.
			
	#path = 'https://www.zdf.de/international/zdfenglish'		# engl. Seite
	#path = 'https://www.zdf.de/international/zdfarabic'		# arab. Seite
	path = 'https://www.zdf.de/international'					# Cluster-Auswertung
	ID="ZDFInternational"
	
	page = Dict("load", ID, CacheTime=CacheTime)
	if page == False or page == '':								# Cache miss od. leer - vom Sender holen
		page, msg = get_page(path=path)
		Dict("store", ID, page) 								# Seite -> Cache: aktualisieren	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return					
	
	ZDF_Sendungen(path, title, ID, page=page)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# Auswertung von ZDF-Seiten ohne Cluster (bzw. page auf Inhalt eines Clusters reduziert)
#	Cluster-Auswertung in ZDF_Sendungen -> ZDFRubrikSingle
# 	ID='Search' od. 'VERPASST' - Abweichungen zu Rubriken + A-Z
#	Seiten mit Einzelvideos werden hier nicht erfasst - ev. vor
#		Aufruf Vorprüfung 'class="artdirect"' durchführen
#	enthält "Inhaltstext im Voraus laden"
#	Änderungen Webseite nachziehen: SearchARDundZDF, SearchARDundZDFnew,
#		ZDF_Search, ZDFSportLive, Tivi_Search (Modul childs).
#	Blockbereich für VERPASST erweitert (umfasst data-station)
#	08.01.2021 Anpassung an geänderte Formate bei Hochkant-Videos.
#
def ZDF_get_content(li, page, ref_path, ID=None, sfilter='Alle ZDF-Sender', skip_list=''):	
	PLog('ZDF_get_content:'); PLog(ref_path); PLog(ID); PLog(sfilter)
	PLog(len(page));

	max_count = 0; content=[]
	PLog(max_count)
	
	if page == '':											# Aufruf via Button
		page, msg = get_page(ref_path)
		if page == '':
			msg1 = 'Seite kann nicht geladen werden.'
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return	
		
	img_alt = teilstring(page, 'class=\"m-desktop', '</picture>') # Bildsätze für b-playerbox
		
	page_title = stringextract('<title>', '</title>', page)  # Seitentitel
	page_title = page_title.strip()
	msg_notfound = ''
	if 'Leider kein Video verf' in page:					# Verfügbarkeit vor class="artdirect"
		msg_notfound = u'Leider kein Video verfügbar'		# z.B. Ausblick auf Sendung
		if page_title:
			msg_notfound = u'Leider kein Video verfügbar zu: ' + page_title
	
	if  ID == 'STAGE':										# Highlights (dto. funk + tivi)
		content = blockextract('class="stage-wrap ', page, "</article>")  # mit Blank + Begrenzung
		stage_url_list=[]
				
	if ID == 'VERPASST' or ID == 'Search':
		content = blockextract('class="b-content-teaser-item', page) 
		
	if len(content) == 0:									# Fallback artdirect
		content = blockextract('<picture class="artdirect"', page) # tivi: doppelt  (is-tivi,is-not-tivi)
																																
	# 27.03.2020 Hochkant-Videos (neues ZDF-Format bei Nachrichten)
	#	Auswirkung: thumb + brand (s.u.)
	# 08.01.2020 Blocks entfernt - Format geändert, s.u. ("PlakatTeaser")	

	if 'data-module="zdfplayer"' in page:					# Playerbox-Videos
		if "www.zdf.de/kinder" not in ref_path:				# tivi: doppel vermeiden
			if ID != 'ZDF_Sendungen':						# Playerbox-Videos schon ausgewertet	
				zdfplayer = blockextract('data-module="zdfplayer"', page, '</article>')
				PLog('zdfplayer: ' + str(len(zdfplayer)))
				content = zdfplayer	+ content				# Blöcke content voranstellen
				
#---------------------------		
	if len(content) == 0:
		msg_notfound = 'Video ist leider nicht mehr oder noch nicht verfügbar'
		
	if len(content) == 0:									# Ausleitung Einzelbeiträge ohne icon-502
		rec = ZDF_get_playerbox(li, page)					# Format: Titel##Thumb###tagline
		if rec:
			PLog('AusleitungEinzelbeitrag1')
			title, thumb, tag = rec.split('###')
			ZDF_getVideoSources(url=ref_path, title=title, thumb=thumb, tagline=tag)
			return li, 0

	if len(content) == 0:									# Ausleitung ZDF_Bildgalerien
		if "gallery-slider-box" in page:
			PLog('AusleitungBildgalerie')
			ZDF_BildgalerieSingle(ref_path, page_title)		
			return li, 0			
	
	page_cnt = len(content)
	PLog('content_Blocks: ' + str(page_cnt));			
	
	if page_cnt == 0:											# kein Ergebnis oder allg. Fehler
		if 'class="b-playerbox' not in page and 'class="item-caption' not in page: # Einzelvideo?
			s = 'Es ist leider ein Fehler aufgetreten.'				# ZDF-Meldung Server-Problem
			if page.find('\"title\">' + s) >= 0:
				msg_notfound = s + ' Bitte versuchen Sie es später noch einmal.'
			else:
				msg_notfound = 'Leider keine Inhalte gefunden.' 	# z.B. bei A-Z für best. Buchstaben 
				if page_title:
					msg_notfound = 'Leider keine Inhalte gefunden zu: ' + page_title
				
			PLog('msg_notfound: ' + str(page_cnt))
	
	if msg_notfound:											# gesamte Seite nicht brauchbar		
		msg1 = msg_notfound
		MyDialog(msg1, '', '')
		return li, 0
						
	# Block '<picture class="artdirect"' kann 'class="b-playerbox' enthalten, z.B. als Trailer
	#	wird hier getrennt erfasst und in der Schleife verworfen (s.u.)
	if page.find('class="b-playerbox') > 0 and page.find('class="item-caption') > 0:  # mehrspaltig: Video gesamte Sendung?
		first_rec = img_alt +  stringextract('class="item-caption', 'data-tracking=', page) # mit img_alt
		content.insert(0, first_rec)							# an den Anfang der Liste
		# PLog(content[0]) # bei Bedarf

	PLog(len(content))

	mediatype=''												# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
			
	#---------------------------		
	items_cnt=0													# Zähler listitems
	href_list=[]
	for rec in content:	
		PLog("items_cnt: %d" % items_cnt)
		teaser_nr=''; teaser_brand=''; poster=False			
		if rec.startswith('data-module="zdfplayer"'): 			# Playerbox(en) auswerten 
			PLog("data-module=zdfplayer")
			PLog(rec[:80])				
			if SETTINGS.getSetting('pref_usefilter') == 'true':	# Filter - s.a. neuer_Satz
				filtered=False
				for item in AKT_FILTER: 
					if up_low(item) in py2_encode(up_low(rec)):
						filtered = True
						break		
				if filtered:
					PLog('filtered: ' + 'data-module="zdfplayer"')
					continue

			p_cnt = ZDF_get_playerbox(li, page=rec, skip_list=skip_list)	
			items_cnt = items_cnt + p_cnt		
			continue
			
		# loader:  enthält bei Suche Links auch wenn weiterer Inhalt fehlt. 
		#			Bei Verpasst u.a. enthält er keinen Link
		if 'class="loader"></span>Weitere laden' in rec:	# Loader erreicht=Ende 
			href = stringextract('load-more-container">', 'class="loader">', rec)
			href = stringextract('href="', '"', href)
			PLog('href_loader:' + href)
			if href:
				PLog('exit_next')
				return li, 'next'
		
		if 'class="b-playerbox' in rec:				# vor Schleifenstart bereits getrennt behandelt,
			pos = rec.find('class="b-playerbox')	#	kann Trailer-Url in plusbar enthalten
			rec = rec[:pos]
		
		if 'data-module="plusbar"' not in rec:	
			pos = rec.find('</article>')		   	# Satz begrenzen - bis nächsten Satz nicht verwertbare 
			if pos > 0:								# 	Inhalte möglich
				rec = rec[0:pos]
				# PLog(rec)  # bei Bedarf
		
		if ID != 'DEFAULT':								# DEFAULT: Übersichtsseite ohne Videos, Bsp. Sendungen A-Z
			if ID != 'A-Z' and ID != 'STAGE':	
				if 'icon-502_play' not in rec :  		# Videobeitrag? auch ohne Icon möglich
					if u'>Videolänge' not in rec: 
						if '>Trailer<' not in rec: 		# Trailer o. Video-icon-502
							PLog('Beitrag_fehlt')
							continue
		
		multi = False			# steuert Mehrfachergebnisse 
		thumb = ZDF_get_img(rec)
						
		teaser_label = stringextract('class="teaser-label"', '</div>', rec) # auch möglich: noch 7 Stunden
		teaser_typ =  stringextract('<strong>', '</strong>', teaser_label)
		if u"teaser-episode-number" in rec:
			teaser_nr = stringextract('teaser-episode-number">', '</', rec)
		if teaser_typ == u'Beiträge':		# Mehrfachergebnisse ohne Datum + Uhrzeit
			multi = True
			summary = dt1 + teaser_typ 		# Anzahl Beiträge
			
		# teaser_brand bei Staffeln (vor Titel s.u.):
		teaser_brand = stringextract('class="teaser-cat-brand-ellipsis">', '</span>', rec) # "<a href" n. eindeutig
		teaser_brand = cleanhtml(teaser_brand); teaser_brand = mystrip(teaser_brand)
		PLog('teaser_brand: ' + teaser_brand)
		
		# 20.02.2021 neue Staffel-Info in teaser_info, angehängt in tag
		teaser_info = stringextract('"teaser-info"', '>', rec)
		if "Staffel" in teaser_info:
			teaser_info = stringextract('aria-label="', '"', teaser_info)
		else:
			teaser_info=''
		PLog('teaser_info: ' + teaser_info)						# ev. Doppel mit duration, s.u.
			
		subscription = stringextract('is-subscription="', '"', rec)	# aus plusbar-Block	
		PLog(subscription)
		if subscription == 'true':						
			multi = True
			teaser_count = stringextract('</span>', '<strong>', teaser_label)	# bei Beiträgen
			stage_title = stringextract('class="stage-title"', '</h1>', rec)  
			summary = teaser_count + ' ' + teaser_typ 

		# Titel	
		href_title = stringextract('<a href="', '>', rec)		# href-link hinter teaser-cat kann Titel enthalten
		href_title = stringextract('title="', '"', href_title)
		if teaser_brand and href_title:							# bei Staffeln, Bsp. Der Pass , St. 01 - Finsternis
			if teaser_brand != href_title:
				if ID != 'A-Z':
					href_title = "%s: %s" % (teaser_brand, href_title)
			
		href_title = unescape(href_title)
		PLog('href_title: ' + href_title)
		if 	href_title == '' and ID == "A-Z":
			continue
		if 	href_title == 'ZDF Livestream' or href_title == 'Sendung verpasst':
			continue
		if 	'<strong>Livestream</strong>' in rec:				# Livestreammarkierung, z.B. Send. m. Gebärdenspr.
			continue
			
		# Pfad, Enddatum. 01.12.2020 plusbar_path kann fehlen, z.B. bei ZDF_Search			
		plusbar_title = stringextract('plusbar-title="', '"', rec)	# Bereichs-, nicht Einzeltitel, nachrangig
		plusbar_path  =  stringextract('plusbar-url="', '"', rec)	# plusbar nicht vorh.? - sollte nicht vorkommen
		enddate	= stringextract('plusbar-end-date="', '"', rec)		# kann leer sein
		enddate = time_translate(enddate, add_hour=False)			# ohne Abgleich summer_time
		
		PLog('plusbar_path: ' + plusbar_path); PLog('ref_path: %s' % ref_path); PLog('enddate: ' + enddate);
		if plusbar_path == '':
			plusbar_path = stringextract('<a href="', '"', rec)
			if plusbar_path.startswith('http') == False:
				plusbar_path = ZDF_BASE + plusbar_path
		if plusbar_path == ref_path:								# Selbstreferenz
			continue
		
		# Datum, Uhrzeit Länge	
		if 'icon-301_clock icon' in rec:					# Uhrsymbol  am Kopf mit Datum/Uhrzeit
			teaser_label = stringextract('class="teaser-label"', '</div>', rec)	
			PLog('teaser_label: ' + teaser_label)
			video_datum =  stringextract('</span>', '<strong>', teaser_label)   
			video_time =  stringextract('<strong>', '</strong>', teaser_label)
		else:
			if '<time datetime="' in rec:						# Datum / Zeit können fehlen
				datum_line =  stringextract('<time datetime="', '/time>', rec) # datetime="2017-11-15T20:15:00.000+01:00">15.11.2017</time>
				video_datum =  stringextract('">', '<', datum_line)
				video_time = datum_line.split('T')[1]
				video_time = video_time[:5] 
			else:
				video_datum=''; video_time=''			
		PLog(video_datum); PLog(video_time);
							
		PLog("Videolänge1:");
		duration = ZDF_getDuration(rec)								# ev. Doppel mit teaser_info
		if teaser_info == duration:
			teaser_info=''
			
		if 	'<strong>Livestream</strong>' in rec:
			duration = u'[COLOR red]Livestream[/COLOR]'	
		duration = duration.strip()
		PLog('duration: ' + duration);
		if duration == '':											# Search: icon-502_play vorh., duration nicht
			multi = True
					
		title = href_title 
		if title == '':
			title = plusbar_title
		if title.startswith(' |'):
			title = title[2:]				# Korrektur
			
		station=''
		if ID == 'VERPASST':
			if 'class="special-info">' in rec:						
				sendtime = stringextract('class="special-info">', '</', rec)
				title = "[COLOR blue]%s[/COLOR] | %s" % (sendtime, title)	# Sendezeit | Titel
			station = stringextract('data-station="', '"', rec)
			station = station.strip()
			PLog("sfilter: " + sfilter); PLog(station); 
			if sfilter == "Alle ZDF-Sender":						# Filterung
				if station == "undefined":
					station = "nicht eindeutig"
			else:
				if sfilter != station or station == "undefined":	# undefined nur für "Alle ZDF-Sender"
					continue
			
		category = stringextract('teaser-cat-category">', '</span>', rec)
		PLog(category)
		category = mystrip(category)
		brand = stringextract('teaser-cat-brand">', '</span>', rec)
		brand = mystrip(brand)
		# z.Z.nicht genutzt:
		# teaser_label,teaser_typ,teaser_nr,teaser_brand,teaser_count,multi = ZDF_get_teaserbox(rec)
			
		tagline = video_datum
		video_time = video_time.replace('00:00', '')				# ohne Uhrzeit
		if video_time:
			tagline = tagline + ' | ' + video_time
		if duration:
			tagline = tagline + ' | ' + duration
		if category:
			tagline = tagline + ' | ' + category
		if brand:
			tagline = tagline + ' | ' + brand
		if teaser_info:
			tagline = tagline + ' | ' + teaser_info
		if tagline.startswith(' |'):
			tagline = tagline[2:]			# Korrektur
		if station:
			tagline = "%s | Sender: [COLOR red]%s[/COLOR]" % (tagline, station)
		if enddate:
			tagline = u"%s\n\n[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % (tagline, enddate)
			
		descr = stringextract('description">', '<', rec)
		if descr == '':
			descr = stringextract('teaser-text">', '<', rec) # mehrere Varianten möglich
		if descr == '':
			descr = stringextract('class="teaser-text" >', '<', rec)
		descr = mystrip(descr)
		PLog('descr:' + descr)		# UnicodeDecodeError möglich
		if descr:
			summary = descr
			if teaser_nr:
				summary = "Episode %s | %s" % (teaser_nr, summary)
				title = "[%2s] %s" % (teaser_nr, title)
		else:
			summary = href_title
			
		# Kurzform icon-502_play in https://www.zdf.de/sport/zdf-sportreportage
		if 	'icon-502_play' not in rec and 'icon-301_clock' not in rec or ID == "A-Z":
			PLog('icon-502_play und icon-301_clock nicht gefunden')
			if plusbar_title.find(' in Zahlen') > 0:	# Statistik-Seite, voraus. ohne Galeriebilder 
				continue
			if plusbar_title.find('Liveticker') > 0:	#   Liveticker und Ergebnisse
				continue
			if plusbar_path.find('-livestream-') > 0:	#   Verweis Livestreamseite
				continue
			multi = True			# weitere Folgeseiten mit unbekanntem Inhalt, ev. auch Videos
			tagline = 'Folgeseiten'
		
		if multi == True:			
			tagline = 'Folgeseiten'
		
		title = mystrip(title)
		title = unescape(title)	
		summary = unescape(summary)
		summary = cleanhtml(summary)		
		tagline = unescape(tagline); tagline = tagline.strip()
		tagline = cleanhtml(tagline)
		
		title=repl_json_chars(title)						# json-komp. für func_pars in router()
		summary=repl_json_chars(summary)					# dto.
		tagline=repl_json_chars(tagline)					# dto.
		
							
		PLog("check_full_shows")							# full_show in summary: ganze Sendungen rot+fett
		if ID != 'EPG' and duration != '':
			title_samml = "%s|%s|%s" % (title, category, brand)
			title = full_shows(title, title_samml, summary, duration, "full_shows_ZDF")
		
		# ab 08.01.2021 in Sätzen mit class="b-cluster-poster-teaser:
		if '"element": "PlakatTeaser"' in rec:
			track = stringextract("data-track='{", '<div', rec)
			form =  stringextract('format": "', '"', track)
			title =  stringextract('Teaser:', '|', track)
			plusbar_path =  stringextract('Linkziel:', '"', track)
			if plusbar_path.startswith('http') == False:
				plusbar_path = ZDF_BASE + plusbar_path
			tagline = "Format: %s | %s" % (form, tagline)
			
		if title.strip() in u"Über ZDFtivi : Kontakt ZDFtivi":	# skip tivi 
			continue
					
		if ID == 'STAGE':										# einige Stage-Beiträge im Web doppelt vorh.
			if plusbar_path in stage_url_list:
				continue
			else:
				stage_url_list.append(plusbar_path)
		
		#if plusbar_path != '':									# bisher nicht benötigt
		#	if check_urlend(plusbar_path,skip_list):			# Url-Enden vergleichen 
		#		PLog("skip: " + plusbar_path)
		#		continue
		
		if SETTINGS.getSetting('pref_usefilter') == 'true':		# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(rec)):
					filtered = True
					break		
			if filtered:
				continue
				
							
		PLog('neuer_Satz:')
		PLog(thumb);PLog(plusbar_path);PLog(title);PLog(summary);PLog(tagline); PLog(multi);
		 
		if multi == True:
			plusbar_path=py2_encode(plusbar_path); title=py2_encode(title);
			fparams="&fparams={'url': '%s', 'title': '%s', 'ID': '%s'}" % (quote(plusbar_path), 
				quote(title), ID)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Sendungen", fanart=thumb, 
				thumb=thumb, fparams=fparams, summary=summary, tagline=tagline)
		else:											# Einzelseite	
														# summary (Inhaltstext) im Voraus laden falls 
														#	 leer oder identisch mit title:										
			tag_par = tagline					
			tag_par = "%s||||%s" % (tag_par, summary)	
			if SETTINGS.getSetting('pref_load_summary') == 'true':	# Voraustext gefragt?
				skip_verf=False; skip_pubDate=False
				if u'Verfügbar' in tagline:
					skip_verf = True
				summ_txt = get_summary_pre(plusbar_path, 'ZDF', skip_verf, skip_pubDate)
				PLog(len(summary));PLog(len(summ_txt)); 
				if 	summ_txt and len(summ_txt) > len(summary):
					tag_par= "%s\n\n%s" % (tagline, summ_txt)
					tag_par = tag_par.replace('\n', '||')
					summary = summ_txt	
						
			tag = tag_par.replace('||', '\n')		# Tag-Label
			tag_par = tag_par.replace('\n', '||')	# json-komp. für func_pars in router()					
			tagline=repl_json_chars(tagline)		# json-komp. für func_pars in router()	
			plusbar_path=py2_encode(plusbar_path); title=py2_encode(title);
			thumb=py2_encode(thumb); tag_par=py2_encode(tag_par);			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s'}" %\
				(quote(plusbar_path), quote(title), quote(thumb), quote(tag_par))	
			addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", 
				fanart=thumb, thumb=thumb, fparams=fparams, tagline=tag, mediatype=mediatype)
				
		items_cnt = items_cnt+1
		
	if items_cnt == 0:								# Ausleitung Einzelbeiträge ohne icon-502 
		if 'data-module="zdfplayer"' in page or 'class="stage-wrapper">' in page:			
			PLog('AusleitungEinzelbeitrag2')
			ZDF_get_playerbox(li, page)
			return li, 0

	return li, page_cnt 
	
#-----------------------------------------------------------------------
# vergleicht Titel + Länge eines Beitrags mit den Listen full_shows_ZDF,
#	full_shows_ARD
# title_samml: Titel|Subtitel oder (Long-|Medium-|Short-Titel)
# duration: Minuten-Wert (ARD-sec umrechnen)
# fname: Dateinamen der Liste (full_shows_ZDF, full_shows_ARD)
# Rückgabe: fett/rot-markierter Titel bei entspr. Beitrag, sonst unbeh.
#	Titel
# Aufrufer: ZDF_get_content, get_page_content (ARDnew)
#
def full_shows(title, title_samml, summary, duration,  fname):
	PLog('full_shows:')
	PLog(title_samml); PLog(summary[:60]); PLog(duration); PLog(fname);
	
	if duration == '':									# Sicherung gg. int()-error
		return title
	
	#if "Ende der Feier" in title_samml:	# Debug
	#	PLog("Mark0")
		
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
				duration = re.search(u'(\d+) min', duration).group(1)
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
						title = "[B][COLOR red]%s[/COLOR][/B]" % title
				break		
	PLog("return: " + title)
	return title
#-----------------------------------------------------------------------
# class="b-playerbox in page auswerten (1 od. mehrere)
# Aufrufer: ZDFRubrikSingle, ZDF_get_content, ZDF_Sendungen
# 20.08.2021 erweitert um Stage-Content - horiz. Scrollrahmen ähnlich 
#	zdfplayer, Bsp.: zdf.de/kultur - Bezeichn. im Addon: Stagebox
#	"zdfplayer"' in Stage-Content möglich (s.u. continue), Bsp. zdf.de/kinder
# 22.11.2021 skip_list für Abgleich
#
def ZDF_get_playerbox(li, page, skip_list=[]):									
	PLog('ZDF_get_playerbox:')

	p_cnt=0; 
	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
													# Playerbox
	boxes = blockextract('data-module="zdfplayer"', page, '</article>')
	PLog(len(boxes))
	for box in boxes:	
		PLog(box[:80])
		url,apiToken,sid,descr_display,descr,title,img = ZDF_getKurzVideoDetails(box)
		tag = "[B]Playerbox-Video[/B]\n\n%s" % descr_display
		if '"isLivestream": true' in box:
			tag = "[COLOR red]Jetzt live[/COLOR] | %s" % tag
		if 'Laufzeit Livestream' in box:
			dauer = stringextract('aria-label="Laufzeit Livestream', '"', box)
			dauer = 'Laufzeit Livestream ' + dauer
			tag = "%s\n%s" % (tag, dauer)
		summ = descr
		if summ and descr_display:
			summ = "%s\n%s" % (summ, descr_display)
			
		if url != '':
			if check_urlend(url,skip_list):			# Url-Enden vergleichen 
				PLog("skip: " + url)
				continue
			else:
				skip_list.append(url)	

		PLog("Satz24:")
		PLog(url); PLog(title); PLog(img); PLog(sid); PLog(apiToken[:80]);
		title=py2_encode(title); descr=py2_encode(descr);
		# sid="": ZDF_getVideoSources soll url neu laden
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s', 'apiToken': '%s', 'sid': '%s'}" %\
			(quote(url),quote(title), quote(img), quote(descr), quote(apiToken), "")
		addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)
		p_cnt=p_cnt+1	
			
	#-------------									# Stagebox (Stage-Content)
	PLog("Stagebox_Check")				
	if 'class="stage-wrapper">' in page and 'stageitemscroller' in page:
		# stage-wrap m-small od. ..-large. Blockende. z.Z nur  'stageitemscroller' genutzt:
		boxes = blockextract('class="stage-wrap m-', page, 'stageitemscroller')
		PLog(len(boxes))
		for box in boxes:
			if 'data-module="zdfplayer"' in box:	# Vorkommen möglich, bereits erfasst
				continue
			PLog(box[:80])
			title,path,img,descr,dauer,enddate,isvideo = ZDF_get_teaserDetails(box)		

			tag = "[B]Stagebox-Video[/B]"
			if isvideo == False:
				tag = "%s | Folgeseiten" % tag
			tag = "%s\n\n%s" % (tag, descr)
			tag_par = tag.replace('\n', '||')

			if path != '':
				if check_urlend(path,skip_list):			# Url-Enden vergleichen 
					PLog("skip: " + path)
					continue
				else:
					skip_list.append(path)	
				
			PLog("Satz25:")
			PLog(path); PLog(title); PLog(img);
			title=py2_encode(title); descr=py2_encode(descr);
			path=py2_encode(path); tag_par=py2_encode(tag_par);
			# sid="": ZDF_getVideoSources soll url neu laden
			
			if isvideo == False:					# Mehrfachbeiträge
				ID = "ZDF_get_playerbox"
				fparams="&fparams={'title': '%s', 'url': '%s', 'ID': '%s', 'tagline': '%s', 'thumb': '%s'}"	%\
					(quote(title),  quote(path), quote(ID), quote(tag_par), quote(img))
				addDir(li=li, label=title, action="dirList", dirID="ZDF_Sendungen", fanart=img, 
					thumb=img, tagline=tag, fparams=fparams)
				
			else:
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s', 'apiToken': '%s', 'sid': '%s'}" %\
					(quote(path),quote(title), quote(img), quote(tag_par), "", "")
				addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=img, thumb=img, 
					fparams=fparams, tagline=tag, mediatype=mediatype)
			p_cnt=p_cnt+1	
			
	#-------------									# Carousel-Box (Stage-Content) ohne zdfplayer - ungetestet
	PLog("carousel_Check")				
	if 'video-carousel-item' in page:
		# stage-wrap m-small od. ..-large. Blockende. z.Z nur  'stageitemscroller' genutzt:
		boxes = blockextract('video-carousel-item', page)
		PLog(len(boxes))
		for box in boxes:
			if 'data-module="zdfplayer"' in box:	# Vorkommen möglich, bereits erfasst
				continue
			PLog(box[:80])
			title,path,img,descr,dauer,enddate,isvideo = ZDF_get_teaserDetails(box)	
			url=path	
			tag = "[B]Stagebox-Video[/B]"
			
			if url != '':
				if check_urlend(url,skip_list):			# Url-Enden vergleichen 
					PLog("skip: " + url)
					continue
				else:
					skip_list.append(url)	

			PLog(url); PLog(title); PLog(img); PLog(sid); PLog(apiToken[:80]);
			title=py2_encode(title); descr=py2_encode(descr);
			# sid="": ZDF_getVideoSources soll url neu laden
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s', 'apiToken': '%s', 'sid': '%s'}" %\
				(quote(url),quote(title), quote(img), quote(descr), quote(apiToken), "")
			addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, mediatype=mediatype)
			p_cnt=p_cnt+1	

	return p_cnt

####################################################################################################
# Subtitles: im Kopf der videodat-Datei enthalten (Endung .vtt). Leider z.Z. keine Möglichkeit
#	bekannt, diese in Plex-Plugins einzubinden. Umsetzung in Kodi-Version OK (s. get_formitaeten).
# Ladekette für Videoquellen s. get_formitaeten
# tagline enthält hier tagline + summary (tag_par von ZDF_get_content)
# Auswertung Kurzvideos (Block 'data-module="zdfplayer" ') in ZDF_get_playerbox/
#	ZDF_getKurzVideoDetails
#	Aufrufer ZDF_get_content + ZDFSportLiveSingle
# 
def ZDF_getVideoSources(url,title,thumb,tagline,Merk='false',apiToken='',sid='',nohome=''):
	PLog('ZDF_getVideoSources:'); PLog(url); PLog(tagline); 
	PLog(title); 
	title=unescape(title); title_org=title; url_org=url
	urlSource = url			
	li = xbmcgui.ListItem()
		
	page, msg = get_page(url)									# Test auf zdfplayer-Modul
	PLog('data-module="zdfplayer"' in page)
	if page.find('data-module="zdfplayer"') == -1 :
		PLog("zdfplayer_Modul_Test")
		msg1 = 'ZDF_getVideoSources: (noch) keine Videoquelle gefunden zu'
		msg2 = "[B]>%s<[/B]" % title
		msg3 = "oder Beitrag existiert nicht mehr"
		MyDialog(msg1, msg2, msg3)
		return li
		
			
	# ab hier normale Auswertung (Einzelbeitrag)
	# ab 08.10.2017 dyn. ermitteln (wieder mal vom ZDF geändert)
	# 12.01.2018: ZDF verwendet nun 2 verschiedene Token - s. get_formitaeten: 1 x profile_url, 1 x videodat_url
	# 29.03.2020: bei Kurzvideos nur 1 apiToken - ermittelt in ZDF_get_content
	scms_id=sid													# Vorbelegung für Sport Live
	if apiToken and sid:
		apiToken1 = apiToken; apiToken2=apiToken1
		page=''
	else:
		if page == '':
			msg1 = 'ZDF_getVideoSources: Problem beim Abruf der Videoquellen.'
			msg2 = msg
			MyDialog(msg1, msg2, '')
			return li

		apiToken1 = stringextract('apiToken: \'', '\'', page) 	# Bereich window.zdfsite
		apiToken2 = stringextract('"apiToken": "', '"', page)
		sid = stringextract("docId: \'", "\'", page)				
		scms_id = stringextract("externalId: \'", "\'", page)	# für hbbtv-Quellen	
			
	PLog('apiToken1: %s, apiToken2: %s, sid: %s' % (apiToken1[:80], apiToken2[:80], sid))
					
	# -- Ende Vorauswertungen
	if nohome != '':									# z.B. nach ZDF_get_playerbox
		if "www.zdf.de/kinder" in urlSource:
			li = home(li, ID='Kinderprogramme')			# Home-Button
		else:
			li = home(li, ID='ZDF')						# Home-Button

	formitaeten,duration,geoblock, sub_path = get_formitaeten(sid, apiToken1, apiToken2)	# Video-URL's ermitteln
	PLog("formitaeten: %d" % len(formitaeten))

	#------------ 										# Nachprüfung auf Videos
	# 06.02.2021 Kennz. "nicht mehr verfügbar" z.B. bei Mehr-Suche (redak. Inhalte zu
	#	vergangenen Videos, formitaeten liefern dann falsche Quellen bei ptmd-template)
	if len(formitaeten) == 0:							# letzte Chance für Inhalte
		if 'picture class="artdirect"' in page and '"icon-502_play' in page:
			ID="ZDF_getVideoSources"
			ZDF_Sendungen(urlSource, title, ID)
			return

		if u"Video leider nicht mehr verfügbar" in page:			
			msg1 = u'Video nicht (mehr) vorhanden / verfügbar.'
			msg2 = u'Titel: %s' % unquote(title)
			MyDialog(msg1, msg2, '')
			return li	
	#------------		
		
				
	if tagline:
		if 'min' in tagline == False:	# schon enthalten (aus ZDF_get_content)?
			tagline = tagline + " | " + duration
	else:
		tagline = duration
	

	HLS_List,MP4_List,HBBTV_List = build_Streamlists(li,title,thumb,geoblock,tagline,\
		sub_path,formitaeten,scms_id,ID="ZDF")
	#----------------------------------------------- 	

	# MEHR_Suche (wie ZDF_Sendungen) - bei Verpasst-Beiträge Uhrzeit abschneiden:
	if '|' in title_org:						# Bsp. Verpasst:  "04:20 Uhr | Abenteuer Winter.."
		title_org = title_org.split('|')[1].strip()
	label = u"Alle Beiträge im ZDF zu >%s< suchen"  % title_org
	query = title_org.replace(' ', '+')	
	tagline = u"zusätzliche Suche starten"
	summ 	= u"suche alle Beiträge im ZDF, die sich auf >%s< beziehen" % title_org
	s_type	= 'MEHR_Suche'						# Suche alle Beiträge (auch Minutenbeiträge)
	query=py2_encode(query); 
	fparams="&fparams={'query': '%s', 's_type': '%s'}" % (quote(query), s_type)
	addDir(li=li, label=label, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams, tagline=tagline, summary=summ)
		
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------------------
# Bau HLS_List, MP4_List, HBBTV_List (nur ZDF)
# Formate siehe StreamsShow						
#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
#	fehlende Bandbreiten + Auflösungen werden ergänzt
# Aufrufer: ZDF_getVideoSources, SingleBeitrag (my3Sat)
#
def build_Streamlists(li,title,thumb,geoblock,tagline,sub_path,formitaeten,scms_id='',ID="ZDF"):
	PLog('build_Streamlists:'); PLog(ID)
	title_org = title
	
	HLS_List=[]; MP4_List=[]; HBBTV_List=[];			# MP4_List = download_list
	only_list = ["h264_aac_mp4_http_na_na", "h264_aac_ts_http_m3u8_http",	# erlaubte Formate
				"vp9_opus_webm_http_na_na", "vp8_vorbis_webm_http_na_na"]
	for rec in formitaeten:									# Datensätze gesamt, Achtung unicode!
		typ = stringextract('"type":"', '"', rec)
		typ = typ.replace('[]', '').strip()
		facets = stringextract('"facets": ', ',', rec)	# Bsp.: "facets": ["progressive"]
		facets = facets.replace('"', '').replace('\n', '').replace(' ', '') 
		PLog("typ %s, facets %s" % (typ, facets))
		if typ not in only_list:
			continue 
			
		audio = blockextract('"audio":', rec)			# Datensätze je Typ
		PLog("audio_Blocks: " + str(len(audio)))
		# PLog(audio)	# bei Bedarf
		for audiorec in audio:					
			url = stringextract('"uri":"',  '"', audiorec)			# URL
			# Zusatz audiotrack ff. abschneiden, lädt falsche Playlist ('#EXT-X-MEDIA')
			if '?audiotrack=1' in url:
				url = url.split('?audiotrack=1')[0]					
			quality = stringextract('"quality":"',  '"', audiorec)
			quality = up_low(quality)
			mimeCodec = stringextract('"mimeCodec":"',  '"', audiorec)

			PLog(url); PLog(quality)
			if facets.startswith('['):
				quality = "%s [%s..]" % (quality, up_low(facets[1:6], mode='low'))
			if url:	
				if up_low(quality) == 'AUTO' and 'master.m3u8' not in url:	# funk: m3u8-Urls nicht verwertbar
					continue	
				if url.find('master.m3u8') > 0:			# m3u8 enthält alle Auflösungen
					quality = u'automatisch'
					HLS_List.append('HLS, automatische Anpassung ** auto ** auto ** %s#%s' % (title,url))
					Stream_List = Parseplaylist(li, url, thumb, geoblock, tagline,\
						stitle=title,buttons=False)
					HLS_List = HLS_List + Stream_List
					break
				else:	
					res='0x0'; bitrate='0'						# Default funk ohne AzureStructure						
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
					
					if '://funk' in url:						# funk: anderes Format (nur AzureStructure)
						# Bsp.: ../1646936_src_1024x576_1500.mp4?fv=1
						if '_' in url:
							res = url.split('_')[2]
							bitrate = url.split('_')[3]				# 6000.mp4?fv=2
							bitrate = bitrate.split('.')[0]
							bitrate = bitrate + "000"				# K-Angabe anpassen 
					else:
						if '_' in url:
							try:								# Fehlschlag bei arte-Links
								bitrate = re.search(u'_(\d+)k_', url).group(1)
							except:
								bitrate = "unbekannt"
						res = "%sx%s" % (w,h)
					
					PLog(res)
					title_url = u"%s#%s" % (title, url)
					item = u"MP4, Qualität: %s ** Bitrate %s ** Auflösung %s ** %s" %\
						(quality, bitrate, res, title_url)
					MP4_List.append(item)
	
	PLog("HLS_List: " + str(len(HLS_List)))
	#PLog(HLS_List)
	PLog("MP4_List: " + str(len(MP4_List)))
	Dict("store", '%s_HLS_List' % ID, HLS_List) 
	Dict("store", '%s_MP4_List' % ID, MP4_List) 
		
	if not len(HLS_List) and not len(MP4_List):			
		msg = 'keine Streamingquelle gefunden - Abbruch' 
		PLog(msg)
		msg1 = u"keine Streamingquelle gefunden: %s"	% title
		MyDialog(msg1, '', '')	
		return HLS_List, MP4_List, HBBTV_List
		
	if ID == "ZDF":										# o. Abbruch-Dialog
		HBBTV_List = ZDFSourcesHBBTV(title, scms_id)				
		PLog("HBBTV_List: " + str(len(HBBTV_List)))
		Dict("store", '%s_HBBTV_List' % ID, HBBTV_List) 
		
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
# Sofortstart + Buttons für die einz. Streamlisten
# Aufrufer: build_Streamlists (ZDF, 3sat), ARDStartSingle (ARD Neu),
#	SingleSendung (ARD Classic), XLGetSourcesPlayer
# Plot = tagline (zusammengefasst: Titel (abgesetzt), tagline, summary)
# Kennzeichung mit mediatype='video' vor aufrufenden Funktionenen, z.B.
#	StreamsShow, XLGetSourcesPlayer, 
#
def build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID="ZDF",HOME_ID="ZDF"):
	PLog('build_Streamlists_buttons:'); PLog(ID)
	
	if geoblock and geoblock not in Plot:
		Plot = "%s||%s" % (Plot, geoblock) 
	
	tagline = Plot.replace('||', '\n')
	Plot = Plot.replace('\n', '||')
	
	# Sofortstart HLS / MP4 - abhängig von Settings	 	# Sofortstart
	played_direct=False
	if SETTINGS.getSetting('pref_video_direct') == 'true':	
		played_direct=True
		img = thumb
		PlayVideo_Direct(HLS_List, MP4_List, title_org, img, Plot, sub_path, HBBTV_List)
		return played_direct

	# -----------------------------------------			# Buttons Einzelauflösungen
	PLog("Satz3:")
	title_list=[]
	img=thumb; 
	PLog(title_org); PLog(tagline[:60]); PLog(img); PLog(sub_path);
	title_hls 	= u"[COLOR blue]Streaming-Formate[/COLOR]"
	title_hb = "[COLOR blue]HBBTV-Formate[/COLOR]"
	title_mp4 = "[COLOR red]MP4-Formate und Downloads[/COLOR]"
	title_hls=repl_json_chars(title_hls); title_hb=repl_json_chars(title_hb);
	title_mp4=repl_json_chars(title_mp4); 
	
	# title_list: Titel + Dict-ID + Anzahl Streams
	title_list.append("%s###%s###%s" % (title_hls, '%s_HLS_List' % ID, len(HLS_List)))
	if ID == "ZDF":										# HBBTV nur bei ZDF verwenden
		title_list.append("%s###%s###%s" % (title_hb, 'ZDF_HBBTV_List', len(HBBTV_List)))	
	title_list.append("%s###%s###%s" % (title_mp4, '%s_MP4_List' % ID, len(MP4_List)))	


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
# HBBTV Videoquellen (nur ZDF)		
def ZDFSourcesHBBTV(title, scms_id):
	PLog('ZDFSourcesHBBTV:'); 
	PLog("scms_id: " + scms_id) 
	HBBTV_List=[]
	url = "https://hbbtv.zdf.de/zdfm3/dyn/get.php?id=%s" % scms_id
		
	# Call funktioniert auch ohne Header:
	header = "{'Host': 'hbbtv.zdf.de', 'content-type': 'application/vnd.hbbtv.xhtml+xml'}"
	page, msg = get_page(path=url, header=header, JsonPage=True)	
	if page == '':						
		msg1 = u'HBBTV-Quellen nicht vorhanden / verfügbar'
		msg2 = u'Video: %s' % title
		MyDialog(msg1, msg2, '')
		return 
		
	page = page.replace('": "', '":"')				# für funk-Beiträge erforderlich
	PLog('page_hbbtv: ' + page[:100])
				
	streams = stringextract('"streams":', '"head":', page)	# Video-URL's ermitteln
	ptmdUrl_list = blockextract('"ptmdUrl":', streams)		# mehrere mögl., z.B. Normal + DGS
	#PLog(ptmdUrl_list)
	PLog(len(ptmdUrl_list))

	for ptmdUrl in ptmdUrl_list:							# 1-2
		PLog(ptmdUrl[:200])
		label = stringextract('"label":"', '"', ptmdUrl)
		main_list = blockextract('"main":', ptmdUrl)		#  mehrere mögl., z.B. MP4, m3u8
		stream_list=[]
		for qual in main_list:								# bisher nur q1 + q3 gesehen
			PLog(qual[:80])
			if '"q1"' in qual:								# Bsp.: "q1": "http://tvdlzdf..
				q="q1"
				url = stringextract('"q1":"',  '"', qual)
				stream_list.append("%s|%s" % (q, url)) 
			if '"q2"' in qual:							
				q="q2"
				url = stringextract('"q2":"',  '"', qual)
				stream_list.append("%s|%s" % (q, url)) 
			if '"q3"' in qual:
				q="q3"
				url = stringextract('"q3":"',  '"', qual)
				stream_list.append("%s|%s" % (q, url))
		
		PLog(len(stream_list))
		for stream in stream_list:
			q, url = stream.split("|")
			if q == 'q1':
				quality = u'HOHE'
				w = "960"; h = "540"					# Probeentnahme	
				bitrate = u"1812067"
				if u'm3u8' in stream:
					bitrate = u"16 MB/Min."
			if q == 'q2':
				quality = u'SEHR HOHE'
				w = "1024"; h = "576"					# Probeentnahme							
				bitrate = u"3621101"
				if u'm3u8' in stream:
					bitrate = u"19 MB/Min."
			if q == 'q3':
				quality = u'HD'
				w = "1280"; h = "720"					# Probeentnahme, bisher fehlend: w = "1920"; h = "1080"						
				bitrate = u"6501324"
				if u'm3u8' in stream:
					bitrate = u"23 MB/Min."
			
			res = "%sx%s" % (w,h)
			
			if u'm3u8' in stream:
				stream_title = u'HLS, Qualität: %s | %s' % (quality, label) # label: Normal, DGS, .
			else:
				stream_title = u'MP4, Qualität: %s | %s' % (quality, label)
				try:
					bitrate = re.search(u'_(\d+)k_', url).group(1)	# bitrate überschreiben	
					bitrate = bitrate + "000"			# k ergänzen 
				except Exception as exception:			# ts möglich: http://cdn.hbbtvlive.de/zdf/106-de.ts
					PLog(str(exception))
					PLog(url)	

			title_url = u"%s#%s" % (title, url)
			item = u"%s ** Bitrate %s ** Auflösung %s ** %s" %\
				(stream_title, bitrate, res, title_url)
			HBBTV_List.append(item)
		
	PLog(len(HBBTV_List))
	return HBBTV_List
	 
#-------------------------
# Aufrufer: ZDF_get_playerbox
# Blockmerkmal 'data-module="zdfplayer"'
def ZDF_getKurzVideoDetails(rec):
	PLog('ZDF_getKurzVideoDetails:')
	
	pos = rec.find('data-module="zdfplayer"')			# Vorspann abschneiden 
	rec = rec[pos:]
	
	descr_display=''; video_datum=''; video_time=''
	apiToken = stringextract('apiToken": "', '"', rec)  # hier nur 1 apiToken
	sid = stringextract('data-zdfplayer-id="', '"', rec)

	descr = stringextract('item-description"', '</p>', rec) 
	descr = cleanhtml(descr); descr = mystrip(descr); 
	descr = unescape(descr); descr = repl_json_chars(descr);
	descr = descr.replace('>','');

	# Bsp.: datetime="2017-11-15T20:15:00.000+01:00">15.11.2017</time>
	datum_line =  stringextract('<time datetime="', '/time>', rec) 
	if datum_line:
		video_datum =  stringextract('">', '<', datum_line)
		video_time = datum_line.split('T')[1]
		video_time = video_time[:5]
	if video_datum and video_time:
		descr_display 	= "%s, %s Uhr \n\n%s" % (video_datum, video_time, descr)		
		descr 			= "%s, %s Uhr||||%s" % (video_datum, video_time, descr)	
		
	duration = ZDF_getDuration(rec)
	#if duration:									# -> Titel s.u.
	#	descr = "%s | %s" % (descr, duration)

	title=''
	if '"title-inner">' in rec:
		title = stringextract('class="title-inner">', '</span>', rec)
		title = mystrip(title); title = cleanhtml(title)
		title = unescape(title.strip())
	if title =='':
		title = stringextract('medium-headline">', '</', rec)
	if title =='':
		title = stringextract('class="shorter">', '</', rec)
	if title =='' and 'plusbar-title=' in rec:
		title = stringextract('plusbar-title="', '"', rec)
	if title =='':
		href = stringextract('<a href="', '">', rec)
		title = stringextract('title="', '"', href)
	if 'nach oben scrollen' in  title:
		title=''
	if title =='':
		title = sid									# Bsp. "37-nur-haut-und-knochen-100"
	if duration:									# -> Titel s.u.
		title = "%s | %s" % (title, duration)
	title = unescape(title); title = repl_json_chars(title)	
	
	img = stringextract('teaser-image="', '</', rec)	
	img = unescape(img); img = img.replace('\\/','/')
	if '":"https' in img:							# 24.08.2021 json, alle Größen abschn.
			img =  stringextract('":"', '"', img)
		
	url = stringextract('"embed_content": "', '"', rec) # im json-Block data-zdfplayer-jsb 
	url = "https://www.zdf.de%s.html" % url				# 		
	
	PLog('url: %s, apiToken: %s, sid: %s, descr_display: %s, descr: %s, title: %s, img: %s' %\
		(url,apiToken,sid,descr_display,descr,title,img[:80]))
	return(url,apiToken,sid,descr_display,descr,title,img)				
	
#-------------------------
# Videolänge holen
def ZDF_getDuration(rec):
	PLog('ZDF_getDuration:')
	
	duration=''
	if u'>Videolänge<' in rec:											# Ausn. Trailer
		PLog("Var0:")
		duration = stringextract(u'>Videolänge<', '</dd>', rec) 
		duration = stringextract('aria-label="', '"', duration) 
		if duration:
			return duration
			
	PLog("Var1:")
	if ' min</dd>' in rec:
		try:															# 1. Variante
			duration = re.search(u' (\d+) min</dd>', rec).group(1)
			return duration + " min"
		except Exception as exception:
			duration=''		
	PLog("Var2:")
	if u'"Videolänge ' in rec:
		try:															# 2. Variante
			duration = re.search(u'"Videolänge (\d+) min ', rec).group(1)
			return duration + " min"
		except Exception as exception:
			duration=''
	PLog("Var3:")
	if ' min ' in rec:
		try:															# Fallback-Variante
			duration = re.search(u'(\d+) min ', rec).group(1)
			return duration + " min"
		except Exception as exception:
			duration=''

	return duration
#-------------------------

# 08.01.2021 ZDFotherSources + show_formitaeten entfallen	
#	def ZDFotherSources(title, tagline, thumb, sid, apiToken1, apiToken2, ref_path=''):
#	def show_formitaeten(li, title_call, formitaeten, tagline, thumb, only_list, geoblock, sub_path, Merk='false'):	

#-------------------------
#	Ladekette für Videoquellen ab 30.05.2017:
#		1. Ermittlung der apiToken (in configuration.json), nur anfangs 2016 unverändert, Verwendung in header
#		2. Sender-ID sid ermitteln für profile_url (durch Aufrufer ZDF_getVideoSources, ZDFotherSources)
#		3. Playerdaten ermitteln via profile_url (Basis bisher unverändert, hier injiziert: sid)
#		4. Videodaten ermitteln via videodat_url )
#	Bei Änderungen durch das ZDF Ladekette mittels chrome neu ermitteln (network / HAR-Auswertung)
#
def get_formitaeten(sid, apiToken1, apiToken2, ID=''):
	PLog('get_formitaeten:')
	PLog(apiToken1)
	PLog('sid/docId: ' + sid)
	PLog('Client: '); PLog(OS_DETECT);						# s. Startbereich
	PLog(apiToken1[:80]); PLog(apiToken2[:80]);
	if apiToken2 =='':										# ZDFSportLive
		apiToken2 = apiToken1
	
	# bei Änderung profile_url neu ermitteln - ZDF: zdfplayer-Bereich, NEO: data-sophoraid
	profile_url = 'https://api.zdf.de/content/documents/%s.json?profile=player'	% sid

	PLog("profile_url: " + profile_url)
	if sid == '':											# Nachprüfung auf Videos
		return '','',''
	
	# apiToken (Api-Auth) : bei Änderungen des  in configuration.json neu ermitteln (für NEO: HAR-Analyse 
	#	mittels chrome)	ab 08.10.2017 für ZDF in ZDF_getVideoSources ermittelt + als Dict gespeichert + 
	#	hier injiziert (s.u.)
	# Header Api-Auth + Host reichen manchmal, aber nicht immer - gesetzt in get_page.
	# 15.10.2018 Abrufe ausgelagert nach get_page. 
	# Kodi-Version: Wegen Problemen mit dem Parameterhandling von Listen und Dicts wird hier
	#	 nur der Api-Auth Key übergeben (Rest in get_page). 
	#	
	if ID == 'NEO':
		# header = {'Api-Auth': "Bearer d90ed9b6540ef5282ba3ca540ada57a1a81d670a",'Host':"api.zdf.de", 'Accept-Encoding':"gzip, deflate, sdch, br", \
		#	'Accept':"application/vnd.de.zdf.v1.0+json"}
		header = "{'Api-Auth': 'Bearer d90ed9b6540ef5282ba3ca540ada57a1a81d670a','Host': 'api.zdf.de'}"
	else:
		PLog(apiToken1)									# s. ZDF_getVideoSources
		# kompl. Header für Modul requests, für urllib2.urlopen reichen Api-Auth + Host
		# header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de', 'Accept-Encoding': 'gzip, deflate, sdch, br', \
		#	'Accept':'application/vnd.de.zdf.v1.0+json'}" % apiToken1
		header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken1
	
	page, msg	= get_page(path=profile_url, header=header, JsonPage=True)	
	if page == '':										# Abbruch
		PLog('profile_url: Laden fehlgeschlagen')
		return '', '', '', ''
	PLog("page_json: " + page[:40])
	page = page.replace('": "', '":"')					# für funk-Beiträge erforderlich
	#RSave('/tmp/profile_url.json', py2_encode(page))	# Debug	
	
														# Videodaten ermitteln:
	pos = page.rfind('mainVideoContent')				# 'mainVideoContent' am Ende suchen
	page_part = page[pos:]
	PLog("page_part: " + page_part[:40])			# bei Bedarf
	# neu ab 20.1.2016: uurl-Pfad statt ptmd-Pfad ( ptmd-Pfad fehlt bei Teilvideos)
	# neu ab 19.04.2018: Videos ab heute auch ohne uurl-Pfad möglich, Code einschl. Abbruch entfernt - s.a. KIKA_und_tivi.
	# 18.10.2018: Code für old_videodat_url entfernt (../streams/ptmd":).
	# 23.11.2019: extract videodat_url ohne Blank hinter separator : (s. json.loads in get_page)
	# 02.08.2020: extract DGS-Url (Gebärdensprache) abhängig vom Setting
	
	# ptmd_player = 'ngplayer_2_3'						# ohne webm
	ptmd_player = 'ngplayer_2_4'						# ab 22.12.2020
	videodat_url = ''
	if SETTINGS.getSetting('pref_DGS_ON') == 'true':								# Link Gebärdensprache?
		dgs_part = stringextract('label":"DGS"', '}}', page_part)
		PLog("dgs_part: " + dgs_part)
		videodat_url = stringextract('ptmd-template":"', '"', dgs_part)
	if videodat_url == '':
		videodat_url = stringextract('ptmd-template":"', '"', page_part)			# Ende funk-Beiträge: ..profile=tmd"}}}
		# videodat_url = 'https://api.zdf.de/tmd/2/portal/vod/ptmd/mediathek/'  	# unzuverlässig
	videodat_url = videodat_url.replace('{playerId}', ptmd_player) 					# ptmd_player injiziert 
	if videodat_url:
		videodat_url = 'https://api.zdf.de' + videodat_url		
	PLog('videodat_url: ' + videodat_url)	
	
	# apiToken2 aus ZDF_getVideoSources. header ohne quotes in get_page leer 
	# kompl. Header für Modul requests, für urllib2.urlopen reichen Api-Auth + Host
	#header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de', 'Accept-Encoding': 'gzip, deflate, sdch, br', \
	#	'Accept':'application/vnd.de.zdf.v1.0+json'}" % apiToken2
	header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken2
	page, msg	= get_page(path=videodat_url, header=header, JsonPage=True)
	PLog("request_json: " + page[:40])
	#RSave('/tmp/videodat_url.json', py2_encode(page))	# Debug	

	if page == '':	# Abbruch 
		PLog('videodat_url: Laden fehlgeschlagen')
		return '', '', '', ''
	PLog(page[:100])	# "{..attributes" ...
	# PLog(page)		# bei Bedarf
		
	# Kodi: https://kodi.wiki/view/Features_and_supported_formats#Audio_playback_in_detail 
	#	AQTitle, ASS/SSA, CC, JACOsub, MicroDVD, MPsub, OGM, PJS, RT, SMI, SRT, SUB, VOBsub, VPlayer
	#	Für Kodi eignen sich beide ZDF-Formate xml + vtt, umbenannt in *.sub oder *.srt
	#	VTT entspricht SubRip: https://en.wikipedia.org/wiki/SubRip
	subtitles = stringextract('\"captions\"', '\"documentVersion\"', page)	# Untertitel ermitteln, bisher in Plex-
	subtitles = blockextract('\"class\"', subtitles)						# Channels nicht verwendbar
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
	PLog('page_formitaeten: ' + page[:100])		
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

	PLog('Ende get_formitaeten:')
	return formitaeten, duration, geoblock, sub_path  

#-------------------------
# Aufrufer: ZDF_Search (weitere Seiten via page_cnt)
#	Einzelseite -> ZDF_BildgalerieSingle
def ZDF_Bildgalerien(li, page):	
	PLog('ZDF_Bildgalerien:'); 
	
	page_cnt=0;
	content =  blockextract('class="artdirect"', page)
	for rec in content:	
		infoline = stringextract('infoline-text="', '"', rec)
		if " Bilder " in infoline == False:
			continue
			
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
		
		tag = stringextract('aria-label="', '</dd', rec)		# Anzahl Bilder
		tag=mystrip(tag); tag=cleanhtml(tag); tag=tag.replace('">', "")
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
		PLog('neuer Satz')
		PLog(thumb);PLog(path);PLog(title);PLog(summ);PLog(tag);
		
		path=py2_encode(path); title=py2_encode(title);
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))	
		addDir(li=li, label=title, action="dirList", dirID="ZDF_BildgalerieSingle", fanart=thumb, thumb=thumb, 
			fparams=fparams, summary=summ,  tagline=tag)
		page_cnt = page_cnt + 1
	
	return li, page_cnt 

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
#
def ZDF_BildgalerieSingle(path, title):	
	PLog('ZDF_BildgalerieSingle:'); PLog(path); PLog(title)
	title_org = title
	
	li = xbmcgui.ListItem()
	
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li 

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
		
		lable = u"Alle Bilder löschen"						# 2. Löschen
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
def Parseplaylist(li, url_m3u8, thumb, geoblock, descr, sub_path='', stitle='', buttons=True):	
#	# master.m3u8 auswerten, Url muss komplett sein. 
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
#
	PLog ('Parseplaylist: ' + url_m3u8)
	Stream_List=[]

	if SETTINGS.getSetting('pref_video_direct') == 'true' and buttons:		# nicht für Stream_List
		return li

	playlist = ''
	# seit ZDF-Relaunch 28.10.2016 dort nur noch https
	if url_m3u8.startswith('http') == True :								# URL oder lokale Datei?			
		playlist, msg = get_page(path=url_m3u8)								# URL
		if playlist == '':
			icon = R(ICON_WARNING)
			# msg1 = "master.m3u8 nicht abrufbar"
			msg1 = "Streaming-Quelle fehlt."
			msg2 = 'Fehler: %s'	% (msg)
			xbmcgui.Dialog().notification(msg1, msg2,icon,5000)
			return li				
	else:																	# lokale Datei	
		fname =  os.path.join(M3U8STORE, url_m3u8) 
		playlist = RLoad(fname, abs_path=True)					
	 
	PLog('playlist: ' + playlist[:100])		# bei Bedarf
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
		PLog("line: " + line)		# bei Bedarf
		if '#EXT-X-MEDIA' in playlist:				# getrennte ZDF-Audiostreams, 1-zeilig
			if line.startswith('#EXT-X-MEDIA'):			# 
				NAME = stringextract('NAME="', '"', line)
				LANGUAGE = stringextract('LANGUAGE="', '"', line)
				url = stringextract('URI="', '"', line)
				title='Audio:  %s | Sprache %s' % (NAME, LANGUAGE)
				PLog(NAME); PLog(NameOld); 
				if NAME in NameOld:
					title='Audio:  %s | Sprache %s %s' % (NAME, LANGUAGE, '(2. Alternative)')
				NameOld.append(NAME)
			else:										# skip Videostreams ohne Ton	
				continue	
			
		else:											# konventionelle Audio-/Videostreams
			if line.startswith('#EXT-X-STREAM-INF'):# tatsächlich m3u8-Datei?
				url = lines[i + 1]						# URL in nächster Zeile
				PLog("url: " + url)
				Bandwith = GetAttribute(line, 'BANDWIDTH')
				Resolution = GetAttribute(line, 'RESOLUTION')
				Resolution_org = Resolution				# -> Stream_List
				try:
					BandwithInt	= int(Bandwith)
				except:
					BandwithInt = 0
				if Resolution:	# fehlt manchmal (bei kleinsten Bandbreiten)
					Resolution = u'Auflösung ' + Resolution
				else:
					Resolution = u'Auflösung unbekannt'	# verm. nur Ton? CODECS="mp4a.40.2"
					thumb=R(ICON_SPEAKER)
				Codecs = GetAttribute(line, 'CODECS')
				# als Titel wird die  < angezeigt (Sender ist als thumb erkennbar)
				title='Bandbreite ' + Bandwith
				if url.find('#') >= 0:	# Bsp. SR = Saarl. Rundf.: Kennzeichnung für abgeschalteten Link
					Resolution = u'zur Zeit nicht verfügbar!'
				if url.startswith('http') == False:   		# relativer Pfad? 
					pos = url_m3u8.rfind('/')				# m3u8-Dateinamen abschneiden
					url = url_m3u8[0:pos+1] + url 			# Basispfad + relativer Pfad
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
	
		if descr.strip() == '|':			# ohne EPG: EPG-Verbinder entfernen
			descr=''
			
		if url.startswith('http') == False: # kompl. Pfad fehlt - Bsp.: one, kika
			continue
		
		summ=''
		if stitle:
			summ = u"Sendung: %s" % py2_decode(stitle)
		
		PLog("SatzParse:")
		PLog(title); PLog(label); PLog(url[:80]); PLog(thumb); PLog(Plot); PLog(descr); 
		
		if buttons:															# Buttons, keine Stream_List
			title=py2_encode(title); url=py2_encode(url);
			thumb=py2_encode(thumb); Plot=py2_encode(Plot); 
			sub_path=py2_encode(sub_path);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
				(quote_plus(url), quote_plus(title), quote_plus(thumb), quote_plus(Plot), 
				quote_plus(sub_path))
			addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
				mediatype='video', tagline=descr, summary=summ) 
		else:																# nur Stream_List füllen
			# Format: "HLS Einzelstream | Bandbreite | Auflösung | Titel#Url"
			PLog("append: %s, %s.." % (str(BandwithInt), Resolution_org))
			if Resolution_org == '':										# für sorted in StreamsShow erford.
				Resolution_org = '0x0 (vermutl. Audio)'
			Stream_List.append(u'HLS, Einzelstream ** Bitrate %s ** Auflösung %s ** %s#%s' %\
				(str(BandwithInt), Resolution_org, stitle, url)) # wie Downloadliste
		
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
# 	"HLS Einzelstream ** Bandbreite ** Auflösung ** Titel#Url" (wie Downloadliste)"
#
#	"MP4 Qualität: niedrige ** leer **leer ** Titel#Url"	
#	"MP4 Qualität: Full HD ** Bandbreite ** Auflösung ** Titel#Url"
# Anzeige: aufsteigend (beide Listen)
# Aufrufer: build_Streamlists_buttons (Aufrufer: ARDStartSingle (ARD Neu), 
#	build_Streamlists (ZDF,  my3Sat), SingleSendung (ARD Classic)
# 
# Plot = tagline (zusammengefasst: Titel, tagline, summary)
# 10.11.2021 Sortierung der MP4-Liste von Auflösung nach Bitrate geändert
#
def StreamsShow(title, Plot, img, geoblock, ID, sub_path='', HOME_ID="ZDF"):	
	PLog('StreamsShow:'); PLog(ID)
	title_org = title; 
	
	li = xbmcgui.ListItem()
	li = home(li, ID=HOME_ID)						# Home-Button

	Stream_List = Dict("load", ID)
	#PLog(Stream_List)

	if 'MP4_List' in ID:
		Stream_List = sorted(Stream_List,key=lambda x: int(re.search(u'Bitrate (\d+)', x).group(1)))

	title_org=py2_encode(title_org);  img=py2_encode(img);
	sub_path=py2_encode(sub_path); 	Plot=py2_encode(Plot); 
	
	tagline_org = Plot.replace('||', '\n')

	cnt=1
	for item in Stream_List:
		item = py2_encode(item)
		PLog("item: " + item[:80])
		label, bitrate, res, title_href = item.split('**')
		bitrate = bitrate.replace('Bitrate 0', 'Bitrate unbekannt')	# Anpassung für funk ohne AzureStructure
		res = res.replace('0x0', 'unbekannt')						# dto.
		PLog(title_href)
		title, href = title_href.split('#')
		
		PLog(title); PLog(tagline_org[:80]); PLog(sub_path)
		tagline = tagline_org
	
		label = "%d. %s | %s| %s" % (cnt, label, bitrate, res)
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
		if SETTINGS.getSetting('pref_show_qualities') == 'false':
			del Stream_List[:-1]													# nur letztes Element verwenden
		summ=''
		li = test_downloads(li,Stream_List,title,summ,tagline,img,high=-1, sub_path=sub_path) # Downloadbutton(s)
	
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
	PLog(' router_params1: ' + paramstring)
	PLog(type(paramstring));
		
	if paramstring:	
		params = dict(parse_qs(paramstring[1:]))
		PLog(' router_params_dict: ' + str(params))
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
				
				dest_modul = importlib.import_module(dest_modul )		# Modul laden
				PLog('loaded: ' + str(dest_modul))
				
				try:
					# func = getattr(sys.modules[dest_modul], newfunc)  # falls beim Start geladen
					func = getattr(dest_modul, newfunc)					# geladen via importlib
				except Exception as exception:
					PLog(str(exception))
					func = ''
				if func == '':						# Modul nicht geladen - sollte nicht
					li = xbmcgui.ListItem()			# 	vorkommen - s. Addon-Start
					msg1 = "Modul %s ist nicht geladen" % dest_modul
					msg2 = "oder Funktion %s wurde nicht gefunden." % newfunc
					msg3 = "Ursache unbekannt."
					PLog(msg1)
					MyDialog(msg1, msg2, msg3)
					xbmcplugin.endOfDirectory(HANDLE)

			else:
				func = getattr(sys.modules[__name__], newfunc)	# Funktion im Haupt-PRG OK		
			
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
	except Exception as e: 
		msg = str(e)
		PLog('network_error: ' + msg)

























