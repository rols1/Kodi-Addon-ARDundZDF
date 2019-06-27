# -*- coding: utf-8 -*-
# XBM
import xbmc	
import xbmcaddon
import xbmcplugin		
import xbmcgui

# Python
import string
import urllib			# urllib.quote()
from urlparse import parse_qsl
from urllib import urlencode
import base64 			# url-Kodierung für Kontextmenüs 
import urllib2			# urllib2.Request
import os, subprocess 	# u.a. Behandlung von Pfadnamen
import shlex			# Parameter-Expansion für subprocess.Popen (os != windows)
import sys				# Plattformerkennung
import shutil			# Dateioperationen
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import datetime, time
import json				# json -> Textstrings

# Addonmodule + Funktionsziele (util_imports.py)
import resources.lib.util as util
PLog=util.PLog; home=util.home; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
getDirZipped=util.getDirZipped; Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
UtfToStr=util.UtfToStr; addDir=util.addDir; get_page=util.get_page; img_urlScheme=util.img_urlScheme; 
R=util.R; RLoad=util.RLoad; RSave=util.RSave; GetAttribute=util.GetAttribute; repl_dop=util.repl_dop; 
repl_char=util.repl_char; repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract; blockextract=util.blockextract; 
teilstring=util.teilstring; cleanhtml=util.cleanhtml; decode_url=util.decode_url; 
unescape=util.unescape; transl_doubleUTF8=util.transl_doubleUTF8; make_filenames=util.make_filenames; 
transl_umlaute=util.transl_umlaute; transl_json=util.transl_json; humanbytes=util.humanbytes; 
CalculateDuration=util.CalculateDuration; time_translate=util.time_translate; seconds_translate=util.seconds_translate; 
get_keyboard_input=util.get_keyboard_input; transl_wtag=util.transl_wtag; xml2srt=util.xml2srt; 
ReadFavourites=util.ReadFavourites; get_summary_pre=util.get_summary_pre; get_playlist_img=util.get_playlist_img; 
get_startsender=util.get_startsender; PlayVideo=util.PlayVideo; PlayAudio=util.PlayAudio;
transl_pubDate=util.transl_pubDate; 

import resources.lib.updater 			as updater		
import resources.lib.EPG				as EPG		

# import resources.lib.ARD_Bildgalerie 	as ARD_Bildgalerie	# 10.12.2018 ARD-Link nicht mehr verfügbar

# +++++ ARDundZDF - Addon Kodi-Version, migriert von der Plexmediaserver-Version +++++

VERSION =  '1.7.7'		 
VDATE = '27.06.2019'

# 
#	

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
PREFIX 			= '/video/ardundzdf'			
												
PLAYLIST 		= 'livesenderTV.xml'		# TV-Sender-Logos erstellt von: Arauco (Plex-Forum). 											
PLAYLIST_Radio  = 'livesenderRadio.xml'		# Liste der RadioAnstalten. Einzelne Sender und Links werden 
											# 	vom Addon ermittelt
											# Radio-Sender-Logos erstellt von: Arauco (Plex-Forum). 
FAVORITS_Pod 	= 'podcast-favorits.txt' 	# Lesezeichen für Podcast-Erweiterung 
FANART					= 'fanart.png'		# ARD + ZDF - breit
ART 					= 'art.png'			# ARD + ZDF
ICON 					= 'icon.png'		# ARD + ZDF
ICON_SEARCH 			= 'ard-suche.png'						
ICON_ZDF_SEARCH 		= 'zdf-suche.png'						

ICON_MAIN_ARD 			= 'ard-mediathek.png'			
ICON_MAIN_ARD_Classic	= 'ard-mediathek-classic.png'			
ICON_MAIN_ZDF 			= 'zdf-mediathek.png'
ICON_MAIN_ZDFMOBILE		= 'zdf-mobile.png'			
ICON_MAIN_TVLIVE 		= 'tv-livestreams.png'		
ICON_MAIN_RADIOLIVE 	= 'radio-livestreams.png' 	
ICON_MAIN_UPDATER 		= 'plugin-update.png'		
ICON_UPDATER_NEW 		= 'plugin-update-new.png'

ICON_ARD_AZ 			= 'ard-sendungen-az.png'
ICON_ARD_VERP 			= 'ard-sendung-verpasst.png'			
ICON_ARD_RUBRIKEN 		= 'ard-rubriken.png' 			
ICON_ARD_Themen 		= 'ard-themen.png'	 			
ICON_ARD_Filme 			= 'ard-ausgewaehlte-filme.png' 	
ICON_ARD_FilmeAll 		= 'ard-alle-filme.png' 		
ICON_ARD_Dokus 			= 'ard-ausgewaehlte-dokus.png'			
ICON_ARD_DokusAll 		= 'ard-alle-dokus.png'		
ICON_ARD_Serien 		= 'ard-serien.png'				
ICON_ARD_MEIST 			= 'ard-meist-gesehen.png' 	
ICON_ARD_BARRIEREARM 	= 'ard-barrierearm.png' 
ICON_ARD_HOERFASSUNGEN	= 'ard-hoerfassungen.png' 
ICON_ARD_NEUESTE 		= 'ard-neueste-videos.png' 	
ICON_ARD_BEST 			= 'ard-am-besten-bewertet.png' 	
ICON_ARD_BILDERSERIEN 	= 'ard-bilderserien.png'

ICON_ZDF_AZ 			= 'zdf-sendungen-az.png' 		
ICON_ZDF_VERP 			= 'zdf-sendung-verpasst.png'	
ICON_ZDF_RUBRIKEN 		= 'zdf-rubriken.png' 		
ICON_ZDF_Themen 		= 'zdf-themen.png'			
ICON_ZDF_MEIST 			= 'zdf-meist-gesehen.png' 	
ICON_ZDF_BARRIEREARM 	= 'zdf-barrierearm.png' 
ICON_ZDF_HOERFASSUNGEN	= 'zdf-hoerfassungen.png' 
ICON_ZDF_UNTERTITEL 	= 'zdf-untertitel.png'
ICON_ZDF_INFOS 			= 'zdf-infos.png'
ICON_ZDF_BILDERSERIEN 	= 'zdf-bilderserien.png'
ICON_ZDF_NEWCONTENT 	= 'zdf-newcontent.png'

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
ICON_SPEAKER 			= "icon-speaker.png"								# Breit-Format

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

# 01.12.2018 	Änderung der BASE_URL von www.ardmediathek.de zu classic.ardmediathek.de
# 06.12.2018 	Änderung der BETA_BASE_URL von  beta.ardmediathek.de zu www.ardmediathek.de
BASE_URL 		= 'https://classic.ardmediathek.de'
BETA_BASE_URL	= 'https://www.ardmediathek.de'								# vorher beta.ardmediathek.de
ARD_VERPASST 	= '/tv/sendungVerpasst?tag='								# ergänzt mit 0, 1, 2 usw.
# ARD_AZ 			= 'https://www.ardmediathek.de/ard/shows'				# ARDneu, komplett (#, A-Z)
ARD_AZ 			= '/tv/sendungen-a-z?buchstabe='							# ARD-Classic ergänzt mit 0-9, A, B, usw.
ARD_Suche 		= '/tv/suche?searchText=%s&words=and&source=tv&sort=date'	# Vorgabe UND-Verknüpfung
ARD_Live 		= '/tv/live'

# Aktualisierung der ARD-ID's in Update_ARD_Path
ARD_RadioAll 	= 'https://classic.ardmediathek.de/radio/live?genre=Alle+Genres&kanal=Alle'

# ARD-Podcasts
POD_SEARCH  = '/suche?source=radio&sort=date&searchText=%s&pod=on&playtime=all&words=and&to=all='
POD_AZ 		= 'https://classic.ardmediathek.de/radio/sendungen-a-z?sendungsTyp=podcast&buchstabe=' 
POD_RUBRIK 	= 'https://classic.ardmediathek.de/radio/Rubriken/mehr?documentId=37981136'
POD_FEATURE = 'https://classic.ardmediathek.de/radio/das-ARD-radiofeature/Sendung?documentId=3743362&bcastId=3743362'
POD_TATORT 	= 'https://classic.ardmediathek.de/radio/ARD-Radio-Tatort/Sendung?documentId=1998988&bcastId=1998988'
POD_NEU 	= 'https://classic.ardmediathek.de/radio/Neueste-Audios/mehr?documentId=23644358'
POD_MEIST 	= 'https://classic.ardmediathek.de/radio/Meistabgerufene-Audios/mehr?documentId=23644364'
POD_REFUGEE = 'https://www1.wdr.de/radio/cosmo/programm/refugee-radio/refugee-radio-112.html'	# z.Z. Refugee Radio via Suche

# ARD Audiothek
ARD_AUDIO_BASE = 'https://www.ardaudiothek.de'

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
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]
HANDLE			= int(sys.argv[1])
																		# Modul-Importe je nach Setting,
																		#	EPG + updater s.o.
if SETTINGS.getSetting('pref_use_podcast') ==  'true':					# ARD-Radio-Podcasts
	import resources.lib.Podcontent 		as Podcontent
if SETTINGS.getSetting('pref_use_zdfmobile') == 'true':					# ZDFmobile					
	import resources.lib.zdfmobile
if SETTINGS.getSetting('pref_use_classic') == 'false':					# ARD Neu
	import resources.lib.ARDnew
if SETTINGS.getSetting('pref_use_3sat') == 'true':						# 3Sat
	import resources.lib.my3Sat
																		

ICON = R(ICON)
PLog("ICON: " + ICON)
TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
PLog(ADDON_DATA)

M3U8STORE 		= os.path.join("%s/m3u8") % ADDON_DATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA
WATCHFILE		= os.path.join("%s/merkliste.xml") % ADDON_DATA
PLog(SLIDESTORE); PLog(WATCHFILE); 
check 			= check_DataStores()	# Check /Initialisierung / Migration 
PLog('check: ' + str(check))

from platform import system, architecture, machine, release, version	# Debug
OS_SYSTEM = system()
OS_ARCH_BIT = architecture()[0]
OS_ARCH_LINK = architecture()[1]
OS_MACHINE = machine()
OS_RELEASE = release()
OS_VERSION = version()
OS_DETECT = OS_SYSTEM + '-' + OS_ARCH_BIT + '-' + OS_ARCH_LINK
OS_DETECT += ' | host: [%s][%s][%s]' %(OS_MACHINE, OS_RELEASE, OS_VERSION)
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

PLog('Addon: ClearUp')
# Dict: Simpler Ersatz für Dict-Modul aus Plex-Framework
ARDStartCacheTime = 300						# 5 Min.	
 
days = int(SETTINGS.getSetting('pref_DICT_store_days'))
Dict('ClearUp', days)				# Dict bereinigen 

days = int(SETTINGS.getSetting('pref_UT_store_days'))
ClearUp(SUBTITLESTORE, days*86400)	# SUBTITLESTORE bereinigen	
days = int(SETTINGS.getSetting('pref_SLIDES_store_days'))
ClearUp(SLIDESTORE, days*86400)		# SLIDEESTORE bereinigen
days = int(SETTINGS.getSetting('pref_TEXTE_store_days'))
ClearUp(TEXTSTORE, days*86400)		# TEXTSTORE bereinigen

ARDSender = ['ARD-Alle:ard::ard-mediathek.png:ARD-Alle']	# Rest in ARD_NEW

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
	tagline = 'bei der ARD-Suche wird zur Zeit noch die Classic-Version genutzt. '
	fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
	addDir(li=li, label=title, action="dirList", dirID="SearchARDundZDF", fanart=R('suche_ardundzdf.png'), 
		thumb=R('suche_ardundzdf.png'), tagline=tagline, fparams=fparams)
		

	if SETTINGS.getSetting('pref_use_classic') == 'true':	# Classic-Version der ARD-Mediathek
		PLog('classic_set: ')
		title = "ARD Mediathek Classic"
		fparams="&fparams={'name': '%s', 'sender': '%s'}" % (title, '')
		PLog(fparams)	
		addDir(li=li, label=title, action="dirList", dirID="Main_ARD", fanart=R(FANART), 
			thumb=R(ICON_MAIN_ARD_Classic), tagline=tagline, fparams=fparams)
	else:
		title = "ARD Mediathek Neu"
		tagline = 'in den Settings sind ARD Mediathek Neu und ARD Mediathek Classic austauschbar'
		fparams="&fparams={'name': '%s', 'CurSender': '%s'}" % (title, '')
		PLog(fparams)	
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", fanart=R(FANART), 
			thumb=R(ICON_MAIN_ARD), tagline=tagline, fparams=fparams)
			
	if SETTINGS.getSetting('pref_use_zdfmobile') == 'true':
		PLog('zdfmobile_set: ')
		tagline = 'in den Settings sind ZDF Mediathek und ZDFmobileaustauschbar'
		fparams="&fparams={}"
		addDir(li=li, label="ZDFmobile", action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=R(FANART), thumb=R(ICON_MAIN_ZDFMOBILE), fparams=fparams)
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
			
	tagline = 'TV-Livestreams stehen auch in ARD Mediathek Neu zur Verfügung'																																	
	fparams="&fparams={'title': 'TV-Livestreams'}"
	addDir(li=li, label='TV-Livestreams', action="dirList", dirID="SenderLiveListePre", 
		fanart=R(FANART), thumb=R(ICON_MAIN_TVLIVE), tagline=tagline, fparams=fparams)
	
	tagline = 'Radio-Livestreams stehen auch in der neuen ARD Audiothek zur Verfügung'
	fparams="&fparams={'path': 'ARD_RadioAll', 'title': 'Radio-Livestreams'}"
	addDir(li=li, label='Radio-Livestreams', action="dirList", dirID="RadioLiveListe", 
		fanart=R(FANART), thumb=R(ICON_MAIN_RADIOLIVE), tagline=tagline, fparams=fparams)
		
	if SETTINGS.getSetting('pref_use_podcast') ==  'true':		# Podcasts / Audiothek
		if SETTINGS.getSetting('pref_use_audio') ==  'true':	# Audiothek
			tagline	= 'ARD Audiothek - Entdecken, Themen, Livestreams'
			summary = 'in den Settings sind Audiothek und Podcasts Classic austauschbar'
			fparams="&fparams={'title': 'ARD Audiothek'}"
			label = 'ARD Audiothek - NEU'
			addDir(li=li, label=label, action="dirList", dirID="AudioStart", fanart=R(FANART), 
				thumb=R(ICON_MAIN_AUDIO), summary=summary, tagline=tagline, fparams=fparams)
		else:													# Podcasts
			tagline	= 'ARD-Radio-Podcasts suchen, hören und herunterladen'
			summary = 'in den Settings sind Audiothek und Podcasts Classic austauschbar'
			fparams="&fparams={'name': 'PODCAST'}"
			label = 'Radio-Podcasts Classic'
			addDir(li=li, label=label, action="dirList", dirID="Main_POD", fanart=R(FANART), 
				thumb=R(ICON_MAIN_POD), summary=summary, tagline=tagline, fparams=fparams)
						
	if SETTINGS.getSetting('pref_use_downloads') ==  'true':	# Download-Tools. zeigen
		tagline = 'Download-Tools: Verschieben, Loeschen, Ansehen, Verzeichnisse bearbeiten'
		fparams="&fparams={}"
		addDir(li=li, label='Download-Tools', action="dirList", dirID="DownloadsTools", 
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
		int_lv = ret[0]			# Version Github
		int_lc = ret[1]			# Version aktuell
		latest_version = ret[2]	# Version Github, Format 1.4.1
		
		if int_lv > int_lc:								# Update-Button "installieren" zeigen
			call_update = True
			title = 'neues Update vorhanden - jetzt installieren'
			summary = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
			# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
			url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
			fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(FANART), 
				thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
			
	if call_update == False:							# Update-Button "Suche" zeigen	
		title = 'Addon-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summary='Suche nach neuen Updates starten'
		tagline='Bezugsquelle: ' + repo_url			
		fparams="&fparams={'title': 'Addon-Update'}"
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(FANART), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams, summary=summary, tagline=tagline)

	# Menü Einstellungen (obsolet) ersetzt durch Info-Button
	#	freischalten nach Posting im Kodi-Forum
	summary = 'Störungsmeldungen an Forum oder rols1@gmx.de'
	tagline = 'für weitere Infos (changelog.txt) klicken'
	path = os.path.join(ADDON_PATH, "changelog.txt") 
	title = "Änderungsliste (changelog.txt)"
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (urllib2.quote(path), urllib2.quote(title))
	addDir(li=li, label='Info', action="dirList", dirID="ShowText", fanart=R(FANART), thumb=R(ICON_INFO), 
		fparams=fparams, summary=summary, tagline=tagline)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#----------------------------------------------------------------
def ShowText(path, title):
	PLog('ShowText:'); 
	page = RLoad(path, abs_path=True)
	page = page.replace('\t', ' ')		# ersetze Tab's durch Blanks
	dialog = xbmcgui.Dialog()
	dialog.textviewer(title, page)
	return
#----------------------------------------------------------------
# sender neu belegt in Senderwahl (Classic: deaktiviert) 
def Main_ARD(name, sender=''):
	PLog('Main_ARD:'); 
	PLog(name); PLog(sender)
	
	# Senderwahl in Classic-Version deaktivert
	# sender 	= ARDSender[0]			# Default 1. Element ARD-Alle
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	PLog("li:" + str(li))						
			
	title="Suche in ARD-Mediathek"		# ARD-New verwendet die Classic-Suche
	fparams="&fparams={'title': '%s', 'query': '', 'channel': 'ARD'}" % urllib2.quote(title)
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_ARD), 
		thumb=R(ICON_SEARCH), fparams=fparams)
		
	img = R(ICON_MAIN_ARD_Classic)
	title = 'Start | Sender: alle Sender' 
	fparams="&fparams={'title': '%s'}" % (urllib2.quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ARDStart", fanart=img, thumb=img, 
		fparams=fparams)

	# title = 'Sendung verpasst | Sender: %s' % sendername
	title = 'Sendung verpasst (alle Sender)'
	fparams="&fparams={'name': 'ARD', 'title': 'Sendung verpasst'}"
	addDir(li=li, label=title, action="dirList", dirID="VerpasstWoche", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_VERP), fparams=fparams)
	
	title = 'Sendungen A-Z (alle Sender)'
	fparams="&fparams={'name': 'Sendungen A-Z', 'ID': 'ARD'}"
	addDir(li=li, label=title, action="dirList", dirID="SendungenAZ", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_AZ), fparams=fparams)
					
	title = 'Rubriken'
	next_cbKey = 'SinglePage'	
	url = BASE_URL + '/tv/Rubriken/mehr?documentId=21282550'
	fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
		% (urllib2.quote(title), urllib2.quote(url), next_cbKey)
	addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_RUBRIKEN) , 
		thumb=R(ICON_ARD_RUBRIKEN) , fparams=fparams)
				
	title = 'ARD Sportschau'
	fparams="&fparams={'title': '%s'}"	% title
	addDir(li=li, label=title, action="dirList", dirID="ARDSport", 
		fanart=R("tv-ard-sportschau.png"), thumb=R("tv-ard-sportschau.png"), fparams=fparams)
						
	fparams="&fparams={'name': 'Barrierearm'}"
	addDir(li=li, label="Barrierearm", action="dirList", dirID="BarriereArmARD", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_BARRIEREARM), fparams=fparams)

	# 10.12.2018 nicht mehr verfügbar, 02.01.2018 Code in Search entfernt:
	#	www.ard.de/home/ard/23116/index.html?q=Bildergalerie
	#title = 'Bilderserien'	
	#fparams='&fparams=query=%s, channel=ARD, s_type=%s, title=%s' % (title,title,title)
	#addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_ARD),
	#	thumb=R('ard-bilderserien.png'), fparams=fparams)

	# 25.01.2019 Senderwahl hier deaktivert - s. Modul ARDnew

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		 		
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
	fparams="&fparams={'title': '%s'}" % (urllib2.quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ZDFStart", fanart=R(ICON_MAIN_ZDF), thumb=R(ICON_MAIN_ZDF), 
		fparams=fparams)

	fparams="&fparams={'name': '%s', 'title': 'Sendung verpasst'}" % name
	addDir(li=li, label='Sendung verpasst', action="dirList", dirID="VerpasstWoche", fanart=R(ICON_ZDF_VERP), 
		thumb=R(ICON_ZDF_VERP), fparams=fparams)	

	fparams="&fparams={'name': 'Sendungen A-Z'}"						# Startseite: Alles auf einen Blick
	addDir(li=li, label="Sendungen A-Z", action="dirList", dirID="ZDFSendungenAZ", fanart=R(ICON_ZDF_AZ), 
		thumb=R(ICON_ZDF_AZ), fparams=fparams)

	fparams="&fparams={'name': 'Rubriken'}"
	addDir(li=li, label="Rubriken", action="dirList", dirID="ZDFRubriken", fanart=R(ICON_ZDF_RUBRIKEN), 
		thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)

	fparams="&fparams={'name': 'Meist gesehen'}"						# Startseite: Alles auf einen Blick
	addDir(li=li, label="Meist gesehen (1 Woche)", action="dirList", dirID="MeistGesehen", 
		fanart=R(ICON_ZDF_MEIST), thumb=R(ICON_ZDF_MEIST), fparams=fparams)
		
	fparams="&fparams={'title': 'Sport Live im ZDF'}"
	addDir(li=li, label="Sport Live im ZDF", action="dirList", dirID="ZDFSportLive", 
		fanart=R("zdf-sportlive.png"), thumb=R("zdf-sportlive.png"), fparams=fparams)
		
	fparams="&fparams={'title': 'Barrierearm'}"							# Startseite: Alles auf einen Blick
	addDir(li=li, label="Barrierearm", action="dirList", dirID="BarriereArm", fanart=R(ICON_ZDF_BARRIEREARM), 
		thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)

	fparams="&fparams={'title': 'ZDFenglish'}"
	addDir(li=li, label="ZDFenglish", action="dirList", dirID="International", fanart=R('ZDFenglish.png'), 
		thumb=R('ZDFenglish.png'), fparams=fparams)

	fparams="&fparams={'title': 'ZDFarabic'}"
	addDir(li=li, label="ZDFarabic", action="dirList", dirID="International", fanart=R('ZDFarabic.png'), 
		thumb=R('ZDFarabic.png'), fparams=fparams)

	fparams="&fparams={'s_type': 'Bilderserien', 'title': 'Bilderserien', 'query': 'Bilderserien'}"
	addDir(li=li, label="Bilderserien", action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_BILDERSERIEN), 
		thumb=R(ICON_ZDF_BILDERSERIEN), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#----------------------------------------------------------------
def Main_POD(name):
	PLog('Main_POD:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

		
	title="Suche Podcasts in ARD-Mediathek"
	fparams="&fparams={'channel': 'PODCAST', 'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_ARD), 
		thumb=R(ICON_SEARCH), fparams=fparams)

	title = 'Sendungen A-Z'
	fparams="&fparams={'name': '%s', 'ID': 'PODCAST'}"	% title
	addDir(li=li, label=title, action="dirList", dirID="SendungenAZ", fanart=R(ICON_MAIN_POD), thumb=R(ICON_ARD_AZ), 
		fparams=fparams)

	title = 'Rubriken'	
	fparams="&fparams={'title': '%s', 'morepath': '%s', 'next_cbKey': 'SinglePage', 'ID': 'PODCAST', 'mode': 'Sendereihen'}" \
		% (title,urllib2.quote(POD_RUBRIK))
	addDir(li=li, label=title, action="dirList", dirID="PODMore", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_RUBRIK), 
		fparams=fparams)

	title="Radio-Feature"	 
	fparams="&fparams={'title': '%s', 'morepath': '%s', 'next_cbKey': 'SingleSendung', 'ID': 'PODCAST', 'mode': 'Sendereihen'}" \
		% (title,urllib2.quote(POD_FEATURE))
	addDir(li=li, label=title, action="dirList", dirID="PODMore", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_FEATURE), 
		fparams=fparams)

	title="Radio-Tatort"
	fparams="&fparams={'title': '%s', 'morepath': '%s', 'next_cbKey': 'SingleSendung', 'ID': 'PODCAST', 'mode': 'Sendereihen'}" \
		% (title,urllib2.quote(POD_TATORT))
	addDir(li=li, label=title, action="dirList", dirID="PODMore", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_TATORT), 
	fparams=fparams)
		 
	title="Neueste Audios"	 
	fparams="&fparams={'title': '%s', 'morepath': '%s', 'next_cbKey': 'SingleSendung', 'ID': 'PODCAST', 'mode': 'Sendereihen'}" \
		% (title,urllib2.quote(POD_NEU))
	addDir(li=li, label=title, action="dirList", dirID="PODMore", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_NEU), 
		fparams=fparams)

	title="Meist abgerufen"	 
	fparams="&fparams={'title': '%s', 'morepath': '%s', 'next_cbKey': 'SingleSendung', 'ID': 'PODCAST', 'mode': 'Sendereihen'}" \
		% (title,urllib2.quote(POD_MEIST))
	addDir(li=li, label=title, action="dirList", dirID="PODMore", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_MEIST), 
		fparams=fparams)

	title="Refugee-Radio"; query='Refugee Radio'	# z.Z. Refugee Radio via Suche
	fparams="&fparams={'title': '%s', 'query': '%s', 'channel': 'PODCAST'}" % (query, query)
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_REFUGEE), 
		fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#----------------------------------------------------------------
# Liste der Rubriken - Hub: AudioStartRubrik -> Audio_get_rubrik
# Buttons für Highlights, Unsere Favoriten, Sammlungen, Ausgewählte 
#	Sendungen, Meistgehört - zusätzlich Themen + LIVESTREAMS.
def AudioStart(title):
	PLog('AudioStart:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)						# Home-Button

	path = ARD_AUDIO_BASE					
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioStart:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
					
	title="Suche in ARD Audiothek"				# Button Suche voranstellen
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="AudioSearch", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R(ICON_SEARCH), fparams=fparams)

	# Liste der Rubriken: Themen + Livestreams fest (am Ende), der Rest 
	#	wird im Web geprüft:
	title_list = ['Highlights']
	if "Sendungsauswahl Unsere Favoriten" in page:
		title_list.append('Unsere Favoriten')
	if "Sendungsauswahl Sammlungen" in page:
		title_list.append('Sammlungen')
	if 'aria-label="Meistgehört"' in page:
		title_list.append('Meistgehört')
	if "Sendungsauswahl Ausgewählte Sendungen" in page:
		title_list.append('Ausgewählte Sendungen')
	title_list.append('Themen');
	
	for title in title_list:
		fparams="&fparams={'title': '%s', 'ID': '%s'}" % (title, title)	
		addDir(li=li, label=title, action="dirList", dirID="AudioStartRubrik", fanart=R(ICON_MAIN_AUDIO), 
			thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	# Button für A-Z anhängen (eigenes ListItem)				# A-Z
	title = 'Sendungen A-Z (alle Radiosender)'
	fparams="&fparams={'title': '%s'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStart_AZ", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R(ICON_AUDIO_AZ), fparams=fparams)
	
	# Button für Podcast-Favoriten anhängen 						# Podcast-Favoriten
	title="Podcast-Favoriten"; 
	tagline = 'konfigurierbar mit der Datei podcast-favorits.txt im Addon-Verzeichnis resources'
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="PodFavoritenListe", fanart=R(ICON_MAIN_POD), 
		thumb=R(ICON_POD_FAVORITEN), tagline=tagline, fparams=fparams)

	# Button für Livestreams anhängen (eigenes ListItem)		# Livestreams
	title = 'Livestreams'	
	fparams="&fparams={'title': '%s'}" % (title)	
	addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=R(ICON_MAIN_AUDIO), 
		thumb=R(ICON_AUDIO_LIVE), fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#----------------------------------------------------------------
# Die Startseite liefert html/json gemischt. mp3-Url wird im html-Bereich
#	ermittelt, bei Fehlen wird die Homepage des Beitrags weitergegeben.
#	img wird im json-Bereich ermittelt - bei Fehlen "kein-Bild".
# Hier wird zur ID der passende page-Ausschnitt ermittelt - Auswertung in 
#	Audio_get_rubrik
# Bei Aufruf von AudioStartThemen wird path statt Startseite geladen.
#
def AudioStartRubrik(title, ID, path=''):
	PLog('AudioStartRubrik: ' + ID)
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')				# Home-Button
	
	if not path:
		path = ARD_AUDIO_BASE					# Default				
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioStartRubrik:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	ID = UtfToStr(ID)
	if ID == 'Highlights':			# Einzelbeiträge
		stage = stringextract('loading-spinner spinner-homepage', 'aria-label="Sendungsauswahl', page)
		gridlist = blockextract('class="episode-teaser-big-wrapper"', stage)
		li = Audio_get_sendungen(li, gridlist, page, ID)
	if ID == 'Unsere Favoriten':
		stage = stringextract('Sendungsauswahl Unsere Favoriten', 'aria-label="Sendungsauswahl', page)
		gridlist = blockextract('class="swiper-slide"', stage)
		li = Audio_get_rubriken(li, gridlist, page, ID)
	if ID == 'Sammlungen':
		stage = stringextract('Sendungsauswahl Sammlungen', 'class="center-text title', page)
		gridlist = blockextract('class="swiper-slide"', stage)
		li = Audio_get_rubriken(li, gridlist, page, ID)
	if ID == 'Meistgehört':			# Einzelbeiträge
		stage = stringextract('aria-label="Meistgehört"', 'Sendungsauswahl Ausgewählte Sendungen', page)
		gridlist = blockextract('label="Episode abspielen"', stage)  # skip 1. Label
		li = Audio_get_sendungen(li, gridlist, page, ID)
	if ID == 'Ausgewählte Sendungen':
		stage = stringextract('Sendungsauswahl Ausgewählte Sendungen', 'id="footer"', page)
		gridlist = blockextract('class="swiper-slide"', stage)
		li = Audio_get_rubriken(li, gridlist, page, ID)
		
	if ID == 'Themen':				# Themen der Seite www.ardaudiothek.de/kategorie
		li = AudioStartThemen(li)
	if ID == 'Themen-Single':		# Einzelthema - Auswertung wie Ausgewählte Sendungen
		gridlist = blockextract('label="Episode abspielen"', page)  # wie Meistgehört
		li = Audio_get_sendungen(li, gridlist, page, ID)  # page s.o.

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#----------------------------------------------------------------
def AudioStart_AZ(title):		
	PLog('AudioStart_AZ:')
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')					# Home-Button

	path = ARD_AUDIO_BASE + '/alphabetisch?al=a'	# A-Z-Seite laden für Prüfung auf inaktive Buchstaben
	page, msg = get_page(path)		
	if page == '':
		msg1 = "Fehler in AudioStart_AZ"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			
	PLog(len(page))
	
	page = stringextract('Alle Sendungen von A bis Z durchsuchen', '<!---->', page)
	gridlist = blockextract('aria-label=', page) 
	del gridlist[0] 						# skip 1. Eintrag
	PLog(len(gridlist))
	
	img = R(ICON_DIR_FOLDER)
	for grid in gridlist:	
		if "isDisabled" in grid:
			continue
		button 	= stringextract('label="', '"', grid)
		title = "Sendungen mit " + button.upper()
		if button == '#':
			title = "Sendungen mit #, 0-9" 
		href	= ARD_AUDIO_BASE + stringextract('href="', '"', grid)
		
		PLog('Satz:');
		PLog(button); PLog(href); 
		 
		fparams="&fparams={'button': '%s'}" % button
		addDir(li=li, label=title, action="dirList", dirID="AudioStart_AZ_content", fanart=R(ICON_MAIN_AUDIO), 
			thumb=img, fparams=fparams)													
		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#----------------------------------------------------------------
# Auswertung A-Z
# Besonderheit: der Quelltext der Leiteite enthält sämtliche Beiträge.  
#	Im Web sorgen java-scripts für die Auswahl zum gewählten Buchstaben.
# Der Quelltext enthält im html-Teil die Beiträge zum Buchstaben plus,
#	im json-Teil den Rest.
# Die Sätze im json-Teil sind inkompatibel  mit  den Sätzen in AudioContentJSON.
#	Nachladebutton (java-script, ohne api-Call).
# Auswahl der Sätze: Vergleich des 1. Buchstaben des Ttitels mit dem Button, 
#	Sonderbehandlung für Button # (Ascii-Wert 35 (#), 34 (") oder 48-57 (0-9).
#		 Außerdem werden führende " durch # ersetzt (Match mit Ascii 35).
#
def AudioStart_AZ_content(button):		
	PLog('AudioStart_AZ_content: ' + button)
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')					# Home-Button

	path = ARD_AUDIO_BASE + '/alphabetisch?al=a'	# A-Z-Seite laden für Prüfung auf inaktive Buchstaben
	page, msg = get_page(path)		
	if page == '':
		msg1 = "Fehler in AudioStart_AZ_content"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			
	PLog(len(page))
	
	pos = page.find(',podcasts:{allPodcasts:')		# Start Podcasts im json-Teil
	page = page[pos:]
	page= page.replace('\u002F', '/')				# Pfadbehandlung gesamte Seite
	gridlist = blockextract(',feed_url:', page) 
	PLog(len(gridlist))
	
	button = button.upper()
	button = UtfToStr(button)
	for grid in gridlist:			
		title 	= stringextract(',title:"', '",', grid) # kann \" enthalten	
		title = title.replace('\\"', '#')				# "  soll mit # matchen
		if 'Roman von Lucy Fricke' in title:
			PLog(title)
			b = title[0].upper()
			PLog(b); PLog(ord(b)); 
					
		# title = title.replace('\\', '')			# " ist Stilmittel
		label = title.replace('\\', '')
		label = title
		if not title:								# kann leer sein
			continue
		if title.startswith('ARD Audiothek\u002F'): # ?
			continue
		b = title[0].upper()
		if button == '#':							# Abgleich: #, 0-9 
			b_val = ord(b)							# Werte / Zeichen s.o.
			if (b_val < 48 or b_val > 57) and b_val != 35:
				continue
		else:
			if b != button:
				continue
		
		img 	=  stringextract('image_16x9:"', '"', grid)
		img		= img.replace('{width}', '640')
		url		= stringextract('sharing_url:"', '"', grid) 
		feed_url= stringextract('feed_url:"', '"', grid) 
		
		PLog('Satz:');
		PLog(title); PLog(img); PLog(url); PLog(feed_url); 
		 
		fparams="&fparams={'path': '%s', 'title': '%s'}" %\
			(urllib2.quote(feed_url), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="AudioContentXML", 
			fanart=R(ICON_MAIN_AUDIO), thumb=img, fparams=fparams)													
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#----------------------------------------------------------------
# Website: http://web.ard.de/radio/radionet/liste.php?ressort=alle&channel=
# HTML-Seite, PHP-Steuerung - lt. Impressum Südwestrundfunk Mainz
# Gesamtliste wie Website - Trennung nach Sendeanstalten nicht 
# 	möglich, da url-Basis nicht immer gleich.
# Die mp3_url kann nicht direkt verwendet werden - sie zeigt auf
#	die Playerseite von web.ard.de. Der enthaltene Streamlink 
#	wird von AudioLiveSingle ermittelt und an PlayAudio durch-
#	gereicht.
#   
# 15.05.2019 Wechsel zur Website https://www.ardaudiothek.de/sender	-  Grund
#	keine sinnvolle Gliederung der 128 Sender möglich, Liste unübersichtlich.
# 1. Durchlauf: Senderliste		2. Durchlauf: einzelne Streams
# Problem: der Streamlink muss von einer zusätzl. Seite der Audiothek ge-
#	holt werden. Der Link zu dieser Seite ist script-generiert  und muss
#	hier nachgebildet werden (Blanks -> -).
def AudioStartLive(title, sender=''):			# Sender / Livestreams 
	PLog('AudioStartLive: ' + sender)
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')				# Home-Button
	sender = UtfToStr(sender)

	path = ARD_AUDIO_BASE + '/sender'
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioStartThemen:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	pos = page.find('{podcastOrganizations:')	# json-Teil
	page= page[pos:]							# 
	page= page.replace('\u002F', '/')			# Pfadbehandlung gesamte Seite

	# Senderliste = Blockersatz
	senderliste = ['br','dlf','hr','mdr','ndr','"radio-bremen"','rbb','sr','swr','wdr']
	if sender == '':							# . Durchlauf: Senderliste
		for sender in senderliste:
			# Bsp. title: data-v-f66b06a0>Theater, Film
			pos1 = page.find('%s:' % sender)	# keine Blockbildung für sender möglich
			pos2 = page.find('}},', pos1)
			grid = page[pos1:pos2]
			# PLog(grid)			# bei Bedarf
			title 	= sender.upper()		
			img 	= stringextract('image_16x9:"', '"', grid)		# Bild 1. Sender
			img		= img.replace('{width}', '640')				
			title = repl_json_chars(title)							# für "bremen" erf.
			sender = repl_json_chars(sender)						# für "bremen" erf.
			
			PLog('Satz:');
			PLog(title); PLog(img);
			fparams="&fparams={'title': '%s', 'sender': '%s'}" % (title, sender)	
			addDir(li=li, label=title, action="dirList", dirID="AudioStartLive", fanart=img, 
				thumb=img, fparams=fparams)
	
		xbmcplugin.endOfDirectory(HANDLE)
	else:										# 2. Durchlauf: einzelne Streams
		my_sender = sender
		sender = sender.replace('radio-bremen', '"radio-bremen"')	# Quotes für Bremen
		# Bsp. title: data-v-f66b06a0>Theater, Film
		pos1 = page.find('%s:' % sender)	# keine Blockbildung für sender möglich
		pos2 = page.find('}},', pos1)
		grid = page[pos1:pos2]
		gridlist = blockextract('image_16x9:"https', grid)	
		PLog(len(gridlist))
		for rec in gridlist:
			title 	= stringextract('title:"', '"', rec)	# Anfang Satz	
			img 	= stringextract('image_16x9:"', '"', rec)		
			img		= img.replace('{width}', '640')	
			descr 	= stringextract('synopsis:"', '",', rec)	
			url 	= "%s/%s/%s" % (path, my_sender, title)	# nicht website_url verwenden
			url		= url.lower()
			url= url.replace(' ', '-')			# Webseiten-URL: Blanks -> -
			url= url.replace(',', '-')			# dto Komma -> -
			
			title = repl_json_chars(title)
			descr = repl_json_chars(descr)	
			summ_par = descr	
						
			PLog('Satz:');
			PLog(title); PLog(img); PLog(url); PLog(descr);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(url), 
				urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioLiveSingle", fanart=img, thumb=img, 
				fparams=fparams, summary=descr, mediatype='music')	
					
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
						
#----------------------------------------------------------------
# hier wird der Streamlink von der Website der Audiothek im json-Teil
#	ermitelt.
# Wie bei den Radiostreams des Hauptmenüs ist hier die Nutzung der Templates
#	erforderlich - s. PlayAudio. Alternative: Streamlinks von der Seite
#	web.ard.de/radio/radionet/liste.php?ressort=alle&channel= holen
#
def AudioLiveSingle(url, title, thumb, Plot):		# startet einzelnen Livestream für AudioStartLive
	PLog('AudioLiveSingle:')

	page, msg = get_page(path=url)	
	if page == '':	
		msg1 = "Fehler in AudioLiveSingle:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	url = stringextract('playback_url:"', '"', page)
	url= url.replace('\u002F', '/')
	PLog(url)
	PlayAudio(url, title, thumb, Plot, url_template='1')  # direkt, template s. PlayAudio	
	
	return	
	
#----------------------------------------------------------------
# html/json gemischt - andere Struktur  als Startseite
# 	Zielfunktion: AudioStartRubrik - ID=Themen-Single + path
#	 steuern Auswertung 
def AudioStartThemen(li):							# Themen der Startseite (/kategorie)
	PLog('AudioStartThemen:')
	
	path = ARD_AUDIO_BASE + '/kategorie'
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioStartThemen:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	pos = page.find('itemprop="item" class="breadcrumb-item-current"')
	page= page[pos:]							# skip Tabliste
	gridlist = blockextract('<li class="category-title"', page)
	PLog(len(gridlist))	
	
	for grid in gridlist:
		# Bsp. title: data-v-f66b06a0>Theater, Film
		title 	= stringextract('<h2', '</h2>', grid) 
		title	= title.split('>')[-1]
		
		href	= ARD_AUDIO_BASE + stringextract('href="', '"', grid)
		img 	= stringextract('src="', '"', grid)
		img_alt = stringextract('title="', '"', grid)
		descr	= img_alt
		
	
		descr	= unescape(descr); descr = repl_json_chars(descr)
		summ_par= descr.replace('\n', '||')
		title	= unescape(title); title = repl_json_chars(title)
			
		PLog('Satz:');
		PLog(title); PLog(img); PLog(href);  PLog(descr);
		fparams="&fparams={'title': '%s', 'ID': '%s', 'path': '%s'}" %\
			(title, 'Themen-Single', urllib2.quote(href))	
		addDir(li=li, label=title, action="dirList", dirID="AudioStartRubrik", fanart=img, 
			thumb=img, summary=descr, fparams=fparams)
	
	return li
#----------------------------------------------------------------
# gridlist: 	Blöcke aus page-Ausschnitt (z.B. Highlights der Startseite)
# page:			kompl. Seite für die img-Suche
#
def Audio_get_rubriken(li, gridlist, page, ID):		# extrahiert Rubriken 
	PLog('Audio_get_rubriken: ' + ID)
	PLog(len(gridlist))	
	cnt=0		
	for grid in gridlist:												
		title 	= stringextract('aria-label="', '"', grid)
		title 	= title.replace('Sendung: ', '')				# Zusatz entfernen
		href		= ARD_AUDIO_BASE + stringextract('href="', '"', grid)  # Homepage Beiträge
		
		img= img_via_audio_href(href=href, page=page)	# img im json-Teil holen

		anzahl 	= stringextract('class="station"', '</span>', grid)
		anzahl	= cleanhtml(anzahl); anzahl = mystrip(anzahl)
		pos		= anzahl.find('>'); anzahl = anzahl[pos+1:]		# entfernen: data-v-7c906280>
		descr	= "[B]Folgeseiten[/B] | %s" % (anzahl) 
		descr = repl_json_chars(descr)
		summ_par= descr
		title = repl_json_chars(title)
				
		PLog('Satz:');
		PLog(title); PLog(img); PLog(href);  PLog(descr);
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(href), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik", fanart=img, thumb=img, fparams=fparams, 
			summary=descr)	
		cnt=cnt+1
		
	return li	
#----------------------------------------------------------------
# api-Call für "WEITERE LADEN" benötigt die an url angehängte id
#	Auswertung in AudioContentJSON (li-Behandl. + Mehr-Button dort)
def Audio_get_rubrik(url, title, pagenr='1'):			# extrahiert Einzelbeiträge einer Rubrik 
	PLog('Audio_get_rubrik: ' + title)
	
	# Header für api-Call:
	ref = url + "/alle"
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Referer': '%s', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}" % ref
	url_id = url.split('/')[-1]
	pagenr = int(pagenr)
	path = ARD_AUDIO_BASE + "/api/podcasts/%s/episodes?items_per_page=24&page=%d" % (url_id, pagenr)				
	page, msg = get_page(path, header=headers)	
	if page == '':	
		msg1 = "Fehler in Audio_get_rubrik:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	ID = 'Audio_get_rubrik'
	# li = Audio_get_sendungen(li, gridlist, page, ID) # Beiträge holen
	title = (title.replace('WEITERE LADEN zu ', '').replace('<', '').replace('>', ''))  # Korrek. title
	AudioContentJSON(title, page, pagenr)				# kehrt nicht zurück
	
	return	
#----------------------------------------------------------------
# gridlist: 	Blöcke aus page-Ausschnitt (z.B. Highlights der Startseite)
# page:			kompl. Seite für die img-Suche (html/json gemischt)
#
def Audio_get_sendungen(li, gridlist, page, ID):	# extrahiert Einzelbeiträge
	PLog('Audio_get_sendungen: ' + ID)
	PLog(len(gridlist))	
	cnt=0		
	for grid in gridlist:
		descr2	= ''											
		title 	= stringextract('aria-label="', '"', grid)
		if ' | ' in title:
			descr2, title = title.split(' | ')
		mp3_url	= stringextract('share-menu-button', 'aria-label', grid)	# teilw. ohne mp3-url
		mp3_url	= stringextract('href="', '"', mp3_url)    		# mp3-File
		href 	= stringextract('podcast-title"', 'aria-label', grid)				# Default
		if ID=="Meistgehört":
			href 	= stringextract('class="podcast-title"', 'aria-label', grid)	# Homepage Beitrag
		href 	= stringextract('href="', '"', href)
		href	= ARD_AUDIO_BASE + href
		
		img= img_via_audio_href(href=href, page=page)	# img im json-Teil holen

		descr 	= stringextract('href"', '"', grid)
		if not descr:
			descr = descr2
		dauer	= stringextract('duration"', '</div>', grid)
		dauer	= cleanhtml(dauer); dauer = mystrip(dauer)
		pos		= dauer.find('>'); dauer = dauer[pos+1:]		# entfernen: data-v-7c906280>
			
		
		if dauer:
			descr	= "[B]Audiobeitrag[/B] | %s\n\n%s" % (dauer, descr)
		else:
			descr	= "[B]Audiobeitrag[/B]\n\n%s" % (descr)  
		descr	= unescape(descr); descr = repl_json_chars(descr)
		summ_par= descr.replace('\n', '||')
		title = repl_json_chars(title)
			
		PLog('Satz:');
		PLog(title); PLog(img); PLog(href);  PLog(mp3_url);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(mp3_url), 
			urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ_par))
		if mp3_url:
			addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, fparams=fparams, 
				summary=descr)
		else:
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(href), 
				urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ_par))
			addDir(li=li, label=title, action="dirList", dirID="AudioSingle", fanart=img, thumb=img, fparams=fparams, 
				summary=descr, mediatype='music')
			
		cnt=cnt+1
		
	return li	
#----------------------------------------------------------------
# AudioSingle gibt direkt das Thema-mp3 seiner Homepage wieder - die 
# 	Funktion ist Fallback für Beiträge (Bsp. Startseite), für die
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
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return
	PLog(len(page))	
	
	pos1 = page.rfind('.mp3')			# Thema-mp3 an letzer Stelle im json-Teil
	page = page[:pos1]
	pos2 = page.rfind('https')
	PLog('pos1 %d, pos2 %d' % (pos1, pos2))
	l = page[pos2:] + '.mp3'

	url = l.replace('\u002F', '/')
	PLog(url[:100])

	AudioPlayMP3(url, title, thumb, Plot)  # direkt	
	return
	
#-----------------------------
# img_via_id: ermittelt im json-Teil (ARD Audiothek) img mittels
#	 letztem href-url-Teil, z.B. ../-diversen-peinlichkeiten/63782268
# Wegen der url-Quotierung (u002F) kann nicht die gesamte url
#	verwendet werden.
# Die img-url befindet sich vor der Fundstelle - daher anschl. Suche
#	nach img.ardmediathek mittels rfind.
def img_via_audio_href(href, page):
	PLog("img_via_audio_href: " + href)

	url_part = href.split('/')[-1]		# letzten url-Teil abschneiden
	url_part = "u002F%s" % url_part		# eindeutiger machen
	PLog(url_part)
	pos1 = page.find(url_part)
	page = page[:pos1]
	pos2 = page.rfind('img.ardmediathek.de')
	PLog('pos1 %d, pos2 %d' % (pos1, pos2))
	l = page[pos2:]

	l = l.replace('\u002F', '/')
	PLog(l[:100])
	
	img=''
	if 'img.ardmediathek.de' in l:		# image_16x9 fehlt manchmal
		img = stringextract('img.ardmediathek.de', '"', l)
		if img:
			img = 'https://img.ardmediathek.de' + img
	img = img.replace('{width}', '640')
	img = img.replace('\u002F', '/')
			
	if img == '':
		img = R('icon-bild-fehlt.png')		# Fallback bei fehlendem Bild

	return img									
	
#----------------------------------------------------------------
# AudioSearch verwendet api-Call -> Seiten im json-Format.
# Auswertung in AudioContentJSON (li-Behandl. + Mehr-Button dort).
# Achtung: cacheToDisc in endOfDirectory nicht verwenden, 
#	cacheToDisc=False springt bei Rückkehr in get_query
# 
def AudioSearch(title, query=''):
	PLog('AudioSearch:')
	# Default items_per_page: 8, hier 24
	base = 'https://www.ardaudiothek.de/api/search/%s?items_per_page=24&page=1'  

	if 	query == '':	
		query = get_query(channel='ARDaudio')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
	
	query = UtfToStr(query)	
	path = base  % urllib2.quote(query)
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioSearch:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))				
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	
	name = 'Suchergebnis zu: ' + urllib2.unquote(query)
	AudioContentJSON(query, page, pagenr='1')				# kehrt nicht zurück
		
	return		
	
#----------------------------------------------------------------
# listet Sendungen  und / oder Einzelbeiträge im json-Format.
# die Ergebnisseiten enthalten gemischt Einzelbeiräge und Links zu Folgeseiten.
# Aufrufer sorgt  für page im json-format (Bsp. api-call in AudioSearch).
#
def AudioContentJSON(title, page, pagenr=''):				
	PLog('AudioContentJSON: ' + title)
	title_org = title
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')		# Home-Button

	cnt=0
	gridlist = blockextract('podcast":{"category', page)		# Sendungen / Rubriken
	PLog(len(gridlist))
	href_pre=''
	for rec in gridlist:
		rec		= rec.replace('\\"', '')
		rubrik 	= stringextract('category":"', '"', rec) 
		descr 	= stringextract('description":"', '"', rec)
		href	= stringextract('link":"', '"', rec) 
		if href == href_pre:									# Dublette?
			continue
		href_pre = href	
		anzahl	= stringextract('_elements":', ',', rec) 		# int
		sender	= stringextract('station":"', '"', rec) 
		title	= stringextract('title":"', '"', rec) 
		url_xml	= stringextract('url":"', '"', rec) 			
		img 	=  stringextract('image_16x9":"', '"', rec)
		img		= img.replace('{width}', '640')
		
		title	= "%s  | %s" % (rubrik, title)
		descr	= "[B]Folgeseiten[/B] | %s Episoden\n\n%s" % (anzahl, descr) 		
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)
	
		PLog('Satz:');
		title=UtfToStr(title); descr=UtfToStr(descr); rubrik=UtfToStr(rubrik); 
		PLog(rubrik); PLog(title); PLog(img); PLog(href)
		fparams="&fparams={'path': '%s', 'title': '%s'}" %\
			(urllib2.quote(url_xml), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="AudioContentXML", fanart=img, thumb=img, 
			fparams=fparams, summary=descr)													
		cnt=cnt+1
		
	
	gridlist = blockextract('"episode":{', page)			# Einzelbeiträge
	if len(gridlist) == 0:
		gridlist = blockextract('"podcast_id":', page)		# Fallback
	PLog(len(gridlist))
	for rec in gridlist:
		rec		= rec.replace('\\"', '')
		rubrik 	= stringextract('category":"', '"', rec) 
		dauer 	= stringextract('duration":"', '"', rec)
		if dauer == '':										# mp3 fehlt
			continue
		descr 	= stringextract('description":"', '"', rec)
		url	= stringextract('playback_url":"', '"', rec) 
		count	= stringextract('_elements":', ',', rec) 	# int
		sender	= stringextract('station":"', '"', rec) 
		title	= stringextract('title":"', '"', rec) 
		href	= stringextract('link":"', '"', rec) 		# Link zur Website
		img 	=  stringextract('image_16x9":"', '"', rec)
		img		= img.replace('{width}', '640')
		
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)		
		
		title	= "%s  | %s" % (rubrik, title)
		descr	= "[B]Audiobeitrag[/B] | Dauer %s\n\n%s" % (dauer, descr) 
		summ_par= descr.replace('\n', '||')
	
		PLog('Satz:');
		title=UtfToStr(title); descr=UtfToStr(descr); rubrik=UtfToStr(rubrik); 
		PLog(dauer); PLog(rubrik); PLog(title); PLog(img); PLog(url)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(url), 
			urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ_par))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, fparams=fparams, 
			summary=descr)
		cnt=cnt+1

	PLog(cnt)	
	if cnt == 0:
		msg1 = 'nichts gefunden zu >%s<' % title_org
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)
		
	try:  																		# Mehr-Button?
		items_per_page =  int(stringextract('items_per_page":', ',', page))
		total 			= int(stringextract('total":', '}', page)) 
		now_max			= int(pagenr) * items_per_page
		PLog("items_per_page %d, total %d, now_max %d " % (items_per_page, total, now_max))
	except Exception as exception:
		PLog(str(exception))
		now_max=1; total=1		# Fallback: kein Mehr-Button
	
	if now_max < total:	
		title = "WEITERE LADEN zu >%s<" % title_org				
		page_next = int(pagenr) +1	
		img = R(ICON_MEHR) 
		tag = "weiter zu Seite %d" % page_next
		PLog(tag)
		title = UtfToStr(title)
		fparams="&fparams={'url': '%s', 'title': '%s', 'pagenr': '%d'}" % (urllib2.quote(href), 
			urllib2.quote(title), page_next)
		PLog('Merk0')
		addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubrik", fanart=img, thumb=img, fparams=fparams, 
			tagline=tag)	
									
	xbmcplugin.endOfDirectory(HANDLE)
	
#----------------------------------------------------------------
# listet Sendungen  und / oder Einzelbeiträge im xml-format
# die Ergebnisseiten enthalten gemischt Einzelbeiräge und Links zu Folgeseiten.
# Aufrufer übergibt path, nicht page wie AudioSearch zu AudioContentJSON
# Problem Datumkonvert. s. transl_pubDate - GMT-Datum bleibt hier unverändert.
# Im xml-Format fehlt die Dauer der Beiträge.
#
def AudioContentXML(title, path):				
	PLog('AudioContentXML: ' + title)
	title_org = title
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')		# Home-Button
	
	page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in AudioContentXML:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))				
	
	img_list = blockextract('<image>', page)						# img Dachsatz
	if len(img_list) == 1:	
		img	= stringextract('<image>', '</width>', page)
		img	= stringextract('<url>', '</url>', img)
	
	cnt=0
	gridlist = blockextract('<item>', page)	
	PLog(len(gridlist))
	for rec in gridlist:
		title	= stringextract('<title>', '</title>', rec) 
		url	= stringextract('url="', '"', rec) 						# mp3
		link	= stringextract('<link>', '</link>', rec) 				# Website
		descr	= stringextract('<description>', '</description>', rec) 
		datum	= stringextract('<pubDate>', '</pubDate>', rec) 
		# datum	= transl_pubDate(datum)								# s. transl_pubDate
		sender	= stringextract('<dc:creator>', '</dc:creator>', rec) 	
		
		title = unescape(title); title = repl_json_chars(title); 
		descr = unescape(descr); descr = repl_json_chars(descr); 
		descr	= "Sender: %s | gesendet: %s\n\n%s" % (sender, datum, descr)	
		summ_par= descr.replace('\n', '||')
	
		PLog('Satz:');
		title=UtfToStr(title); descr=UtfToStr(descr);  
		PLog(title); PLog(url); PLog(link); PLog(datum);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(url), 
			urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ_par))
		addDir(li=li, label=title, action="dirList", dirID="AudioPlayMP3", fanart=img, thumb=img, fparams=fparams, 
			summary=descr)
		cnt=cnt+1
		
	PLog(cnt)	
	if cnt == 0:
		msg1 = 'keine Audios gefunden zu >%s<' % title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
	xbmcplugin.endOfDirectory(HANDLE)
	
#----------------------------------------------------------------
# Ausgabe Audiobeitrag
# Falls pref_use_downloads eingeschaltet, werden 2 Buttons erstellt
#	(Abspielen + Download).
# Falls pref_use_downloads abgeschaltet, wird direkt an PlayAudio
#	übergeben.
#
def AudioPlayMP3(url, title, thumb, Plot):
	PLog('AudioPlayMP3: ' + title)
	
	if SETTINGS.getSetting('pref_use_downloads') == 'false':
		PLog('starte PlayAudio direkt')
		PlayAudio(url, title, thumb, Plot)  # PlayAudio	direkt
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')		# Home-Button
		
	title=UtfToStr(title); Plot=UtfToStr(Plot); 
	summary = Plot.replace('||', '\n')			# Display
	 
	PLog(title); PLog(url); PLog(Plot);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(url), 
		urllib2.quote(title), urllib2.quote(thumb), urllib.quote_plus(Plot))
	addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams, 
		summary=summary, mediatype='music')
	
	download_list = []					# 2-teilige Liste für Download: 'title # url'
	url=UtfToStr(url)
	download_list.append("%s#%s" % (title, url))
	PLog(download_list)
	title_org=title; tagline_org=''; summary_org=Plot
	li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=-1)  # Downloadbutton
		
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################

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
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	title = "Live"								# Zusatz: Live (fehlt in tabpanel)
	href = 'https://www.sportschau.de/ticker/index.html'
	img = R(ICON_DIR_FOLDER)
	# summ = "Livestreams nur hier im Menü [B]Live[/B] oder unten bei den Direktlinks unterhalb der Moderatoren"
	tagline = 'aktuelle Liveberichte (Video, Audio)'
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (urllib2.quote(title), 
		urllib2.quote(href), urllib2.quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)			

	tabpanel = stringextract('<ul id="gseafooterlinks116-panel"', '</ul>', page) 
	tabpanel = blockextract('<li>', tabpanel)
	img = R(ICON_DIR_FOLDER)
	i=0	
	for tab in tabpanel:								# Panel Kopfbereich
		if i == 0:										# Tab Startseite
			href = path
			title = 'Startseite'
		else:		
			href = stringextract('href="', '"', tab)
			title = stringextract('">', '</a>', tab)
		i=i+1
		if 'Ergebnisse' in title:							# Switch zu Hintergrund, 
			href = SBASE + '/hintergrund/index.html'		# Ergebnisse ohne Videos
			title = 'Hintergrund'
		
		PLog('Satz:'); PLog(href); PLog(title); 
		fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (urllib2.quote(title), 
			urllib2.quote(href), urllib2.quote(img))
		addDir(li=li, label=title, action="dirList", dirID="ARDSportPanel", fanart=img, 
			thumb=img, fparams=fparams)			
	 	
	title = "Moderatoren"									# Zusatz: Moderatoren 
	href = 'https://www.sportschau.de/sendung/index.html'
	img =  'https://www1.wdr.de/unternehmen/der-wdr/unternehmen/bundesliga-sportschau-jessy-wellmer-100~_v-gseaclassicxl.jpg'
	tagline = 'Bilder von Moderatoren, Slideshow'
	fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (urllib2.quote(title), 
		urllib2.quote(href), urllib2.quote(img))
	addDir(li=li, label=title, action="dirList", dirID="ARDSportBilder", fanart=img, 
		thumb=img, tagline=tagline, fparams=fparams)			


	channel = 'Überregional'								# zum Livestream: ARDSportschau
	onlySender = 'ARDSportschau Livestream'	
	img = R("tv-ard-sportschau.png")	
	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender=onlySender)
	PLog(onlySender)
		
	mediatype=''	
	if SETTINGS.getSetting('pref_video_direct') == 'true': 
		mediatype='video'
			
	# https://fifafrauenwm.sportschau.de/frankreich2019/live/eventlivestream3666-ardjson.json		
	title = "ARDSportschau FIFA FRAUEN WM 2019 Livestream 1"
	url = "https://ndrspezial-lh.akamaihd.net/i/spezial_1@430235/master.m3u8"
	img = "https://img.ardmediathek.de/standard/00/63/58/44/30/-295433861/16x9/1920?mandant=ard"
	Merk = 'false'
	summ = 'bitte die anderen FRAUEN WM 2019 Livestreams testen, falls dieser nicht funktioniert'
	if not mediatype:										# Einzelauflösungen
		fparams="&fparams={'url_m3u8': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'ID': 'ARD'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="show_single_bandwith", fanart=img, thumb=img, fparams=fparams, 
			summary=summ) 		
	else:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 		

	# https://fifafrauenwm.sportschau.de/frankreich2019/live/eventlivestream3670-ardjson.json
	title = "ARDSportschau FIFA FRAUEN WM 2019 Livestream 2"
	url = "https://ndrspezial-lh.akamaihd.net/i/spezial_2@430236/master.m3u8"   
	img = "https://img.ardmediathek.de/standard/00/63/58/44/30/-295433861/16x9/1920?mandant=ard"
	Merk = 'false'
	summ = 'bitte die anderen FRAUEN WM 2019 Livestreams testen, falls dieser nicht funktioniert'
	if not mediatype:										# Einzelauflösungen
		fparams="&fparams={'url_m3u8': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'ID': 'ARD'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="show_single_bandwith", fanart=img, thumb=img, fparams=fparams, 
			summary=summ) 		
	else:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 		

	#
	title = "ARDSportschau FIFA FRAUEN WM 2019 Livestream 3"
	url = "https://ndrspezial-lh.akamaihd.net/i/spezial_3@430237/master.m3u8"
	img = "https://img.ardmediathek.de/standard/00/63/58/44/30/-295433861/16x9/1920?mandant=ard"
	Merk = 'false'
	summ = 'bitte die anderen FRAUEN WM 2019 Livestreams testen, falls dieser nicht funktioniert'
	if not mediatype:										# Einzelauflösungen
		fparams="&fparams={'url_m3u8': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'ID': 'ARD'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="show_single_bandwith", fanart=img, thumb=img, fparams=fparams, 
			summary=summ) 		
	else:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 	
			
	channel = 'Regional'									# zum Livestream: MDR+ Eventlivestreams
	onlySender = 'MDR+ Eventlivestreams & SocialTV'	
	img = R("tv-mdr-sachsen.png")	
	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender=onlySender)
	PLog(onlySender)	
		
	channel = 'Regional'									# zum Livestream: WDR/ARD Event Sportschau
	onlySender = 'WDR/ARD Event Sportschau'	
	img = "https://www.sportschau.de/resources/img/sportschau/banner/logo_base.png"
	SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender=onlySender)
	PLog(onlySender)
			
	xbmcplugin.endOfDirectory(HANDLE)
	
#--------------------------------------------------------------------------------------------------
def ARDSportPanel(title, path, img):
	PLog('ARDSportPanel:'); 
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	sendungen = blockextract('class="teaser"', page)	
	PLog(len(sendungen))
	
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
			
	SBASE = 'https://www.sportschau.de'
	for s in sendungen:
		pos = s.find('<!-- googleon: all -->')	# "Javascript-Fehler" entfernen
		if pos > 0:
			s = s[pos:]
		if 'media mediaA video' not in s and 'media mediaA audio  video' not in s  and 'media mediaA audio' not in s:			
			continue												# Video im Beitrag?
		path 		= stringextract('href="', '"', s)	
		if path.startswith('http')	== False:
			path 	= SBASE + stringextract('href="', '"', s)		
		img			= stringextract('srcset="', '"', s)				# erste = größtes Bild
		if img.startswith('//'):									# //www1.wdr.de/..
			img	= 'https:' + img
		else:
			if img.startswith('http') == False:						# /sendung/moderatoren/
				img	= SBASE + img
		title		= stringextract('class="headline">', '</h', s)
		summ		= stringextract('teasertext">', '<strong>', s)
		title		= mystrip(title); title = cleanhtml(title)
		title		= repl_json_chars(title)
		summ		= unescape(summ); summ = mystrip(summ)
		summ		= cleanhtml(summ); summ=repl_json_chars(summ)
		title=title.strip(); summ=summ.strip();						# zusätzl. erf.
		if title == '':
			continue
		
		if 'Hörfassung' in title or 'Audiodeskription' in title:				# Filter
			if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true':
				continue		
			if SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
				continue		
		
		PLog('Satz:')
		path=UtfToStr(path); img=UtfToStr(img); title=UtfToStr(title); summ=UtfToStr(summ);  
		PLog(path); PLog(img); PLog(title); PLog(summ); 

		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'summ': '%s'}" %\
			(urllib2.quote(path), urllib2.quote(title), urllib2.quote(img), urllib2.quote(summ))				
		addDir(li=li, label=title, action="dirList", dirID="ARDSportVideo", fanart=img, thumb=img, 
			fparams=fparams, summary=summ, mediatype=mediatype)		 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#--------------------------------------------------------------------------------------------------
# Bilder für ARD Sportschau, z.B. Moderatoren
# Slideshow: ZDFSlideShow
def ARDSportBilder(title, path, img):
	PLog('ARDSportBilder:'); 
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button

	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	content = blockextract('class="teaser"', page)	
	PLog(len(content))
	if len(content) == 0:										
		msg1 = 'Keine Bilder gefunden.'
		PLog(msg1)
		msg2 = 'Seite:'
		msg3 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
				
	fname = make_filenames(title)			# Ablage: Titel + Bildnr
	fpath = '%s/%s' % (SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2); 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li	
				
	SBASE = 'https://www.sportschau.de'
	image = 0
	for rec in content:
		pos = rec.find('<!-- googleon: all -->')	# "Javascript-Fehler" entfernen
		if pos > 0:
			rec = rec[pos:]
		if 'media mediaA gallery gallery' not in rec:					# Gallery im Beitrag?
			continue												
		path 		= SBASE + stringextract('href="', '"', rec)			# nicht genutzt		
		img_src		= stringextract('srcset="', '"', rec)				# erste = größtes Bild
		if img_src.startswith('//'):									# //www1.wdr.de/..
			img_src	= 'https:' + img_src
		else:															# /sendung/moderatoren/
			img_src	= SBASE + img_src
			
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
			title = UtfToStr(title)
			title = unescape(title)
			lable = "%s: %s" % (title, headline)			# Listing-Titel
			
			thumb = ''
			local_path = os.path.abspath(local_path)
			if os.path.isfile(local_path) == False:			# schon vorhanden?
				try:
					urllib.urlretrieve(img_src, local_path)
					thumb = local_path
				except Exception as exception:
					PLog(str(exception))	
			else:		
				thumb = local_path
				
			tagline = headline
			summ = unescape(summ)
			PLog('Satz:');PLog(title);PLog(img_src);PLog(thumb);PLog(summ[0:40]);
			if thumb:
				fparams="&fparams={'path': '%s', 'single': 'True'}" % urllib2.quote(local_path)
				addDir(li=li, label=lable, action="dirList", dirID="ZDFSlideShow", 
					fanart=thumb, thumb=thumb, fparams=fparams, summary=summ)

			image += 1
			
	if image > 0:		
		fparams="&fparams={'path': '%s'}" % urllib2.quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDFSlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
		

	xbmcplugin.endOfDirectory(HANDLE)
	
#--------------------------------------------------------------------------------------------------
# Die Videoquellen des WDR sind in SingleSendung nicht erreichbar. Wir laden
#	die Quelle (2 vorh.) über die Datei ..deviceids-medp-id1.wdr.de..js und
#	übergeben an PlayVideo.
def ARDSportVideo(path, title, img, summ, Merk='false'):
	PLog('ARDSportVideo:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')						# Home-Button
	title = UtfToStr(title); img = UtfToStr(img); summ = UtfToStr(summ);
	Merk = UtfToStr(Merk);
	title_org = title
		
	page, msg = get_page(path=path)		
	page = UtfToStr(page)

	# Livestream-Problematik 
	# todo: nach WM entfernen
	#	s. Forum https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF Post 472ff
	# Button ist Behelfslösung für Frauen-Fußball-WM - url via chrome-developer-tools ermittelt
	# Button ist zusätzl. dauerhaft im Menü ARD Sportschau (Livestream 3) platziert.
	if "/frankreich2019/live" in path:
		url = "https://ndrspezial-lh.akamaihd.net/i/spezial_3@430237/master.m3u8"
		summ = 'bitte die FRAUEN WM 2019 Livestreams testen, falls dieser nicht funktioniert'
		mediatype = 'video'
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)	

	# Bsp. video_src: "url":"http://deviceids-medp.wdr.de/ondemand/167/1673848.js"}
	#	-> 	//ardevent2.akamaized.net/hls/live/681512/ardevent2_geo/master.m3u8
	#	derselbe Streamlink wie Direktlink + Hauptmenü
	# 16.06.2019 nicht für die Livestreams geeignet.
	if 'deviceids-medp.wdr.de' in page:								# häufigste Quelle
		video_src = stringextract('deviceids-medp.wdr.de', '"', page)
		video_src = 'http://deviceids-medp.wdr.de' + video_src
	else:
		PLog('hole playerurl:')
		playerurl = stringextract('webkitAllowFullScreen', '</iframe>', page)
		playerurl = stringextract('src="', '"', playerurl)
		base = 'https://' + path.split('/')[2]						# Bsp. fifafrauenwm.sportschau.de
		video_src = base + playerurl
		PLog(video_src)

	if '-ardplayer_image-' in video_src:							# Bsp. Frauen-Fußball-WM
		# Debug-Url's:
		#https://fifafrauenwm.sportschau.de/frankreich2019/nachrichten/fifafrauenwm2102-ardplayer_image-dd204edd-de3d-4f55-8ae1-73dab0ab4734_theme-sportevents.html		
		#https://fifafrauenwm.sportschau.de/frankreich2019/nachrichten/fifafrauenwm2102-ardjson_image-dd204edd-de3d-4f55-8ae1-73dab0ab4734.json	

		page, msg = get_page(video_src)									# Player-Seite laden, enthält image-ID
		image = stringextract('image = "', '"', page) 
		PLog(image)
		path = video_src.split('-ardplayer_image-')[0]
		PLog(path)
		path = path + '-ardjson_image-' + image + '.json'
		PLog(path)
		page, msg = get_page(path)							# json mit videoquellen laden
		
		plugin 	= stringextract('plugin": 1', '_duration"', page) 
		auto 	= stringextract('"auto"', 'cdn"', plugin) 	# master.m3u8 an 1. Stelle		
		m3u8_url= stringextract('stream": "', '"', auto)
		PLog(m3u8_url)
		title = "m3u8 auto | %s" % title_org
		title=UtfToStr(title); m3u8_url=UtfToStr(m3u8_url); img=UtfToStr(img);
		title_org=UtfToStr(title_org); summ=UtfToStr(summ);Merk=UtfToStr(Merk);
		
		# Sofortstart - direkt, falls Listing nicht Playable
		if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true': 
			PLog('Sofortstart: ARDSportVideo')
			PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
			PlayVideo(url=m3u8_url, title=title, thumb=img, Plot=summ, sub_path="")
			return
		
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(m3u8_url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			summary=summ) 
			
		mp4 	= stringextract('quality": 3', 'cdn"', page)	# mp4-HD-Quality od. mp3
		mp4_url= stringextract('stream": "', '"', mp4)
		PLog(mp4_url)
		if mp4_url:
			title = "MP4 HD | %s" % title_org
			if mp4_url.endswith('.mp3'):
				title = "Audio MP3 | %s" % title_org
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
				(urllib.quote_plus(m3u8_url), urllib.quote_plus(title), urllib.quote_plus(img), 
				urllib.quote_plus(summ), Merk)
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
				summary=summ) 
			
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
	# Website enthält Button: Ich bin damit einverstanden, dass mir Bilder/Videos von Twitter 
	#	angezeigt werden. Nach Bestätigung (syndication.twitter.com/settings) wird das Twitter-
	#	Video in einem Frame  eingeblendet (Bsp. widget_iframe.d753e00c3e838c1b2558149bd3f6ecb8.html).
	# Umsetzung lohnt sich m.E. nicht.
	page, msg = get_page(path=video_src)		
	if page == '':
		msg1 = 'Videoquellen können nicht geladen werden.'
		msg2 = "Eventuell eingebettetes Twitter-Video?. Seite:"
		msg3 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
			
	
	content = blockextract('"videoURL":"', page)
	url=''
	for rec in content:
		url = stringextract('"videoURL":"', '"', rec)	# bei Bedarf zweite altern. Url laden
		PLog(url)
		if 'manifest.f4m' in url:					#  manifest.f4m überspringen
			continue
	if url == '':									# ev. nur Audio verfügbar
		url = stringextract('"audioURL":"', '"', page)
	if url.startswith('http') == False:		
		url = 'http:' + url							# //wdradaptiv-vh.akamaihd.net/..
	PLog ("url: " + url) 	 										
	
	mediatype = 'video'
	if url.endswith('.mp3'):
		mediatype = 'audio'
		title = "Audio: %s"  % title
		
	# Sofortstart - direkt, falls Listing nicht Playable:
	if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true': 
		PLog('Sofortstart: ARDSportPanel')
		PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
		PlayVideo(url=url, title=title, thumb=img, Plot=summ, sub_path="")
		return
	
	summ=UtfToStr(summ); summ=UtfToStr(summ); title=UtfToStr(title); 
	if url.endswith('master.m3u8'):
		li = Parseplaylist(li=li, url_m3u8=url, thumb=img, geoblock='', descr=summ, summary=summ)
	else:
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(img), 
			urllib.quote_plus(summ), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype=mediatype, summary=summ) 
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

####################################################################################################
def SearchUpdate(title):		
	PLog('SearchUpdate:')
	li = xbmcgui.ListItem()

	ret = updater.update_available(VERSION)	
	#PLog(ret)
	if ret[0] == False:		
		msg1 = 'Updater: Github-Problem'
		msg2 = 'update_available: False'
		PLog("%s | %s" % (msg1, msg2))
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			

	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1
	summ = ret[3]			# Changes
	tag = ret[4]			# tag, Bsp. 029
	
	# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
	url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)

	PLog(int_lv); PLog(int_lc); PLog(latest_version); PLog(summ);  PLog(url);
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Addon vorher sichern!)			
		title = 'Update vorhanden - jetzt installieren'
		summary = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
		tagline = cleanhtml(summ)
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary, 
			tagline=cleanhtml(summ))
			
		title = 'Update abbrechen'
		summary = 'weiter im aktuellen Addon'
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_UPDATER_NEW), 
			thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
	else:	
		title = 'Addon ist aktuell | weiter zum aktuellen Addon'
		summary = 'Addon Version ' + VERSION + ' ist aktuell (kein Update vorhanden)'
		summ = summ.splitlines()[0]		# nur 1. Zeile changelog
		tagline = "%s | Mehr in changelog.txt" % summ
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
#
#  	Funktion VerpasstWoche weiter als Classic-Version (fehlt in Neu-Version). 
#	
####################################################################################################

# Startseite der Mediathek - passend zum ausgewählten Sender.
# 	Bilder werden über die sid im player-Pfad ermittelt. Dieser fehlt bei Staffeln + Serien -
#		img_via_id gibt dann ein Info-Bild zurück.
#	Die Startseite wird im Cache für ARDStartRubrik abgelegt und dient gleichzeitig als Fallback 
#	23.01.2019  neue Seite wird unvollständig geladen (wie SendungenAZ) - java-script-gesteuerter
#		Scroll-Mechanismus.
#		Rückbau auf Classic-Version.
#		Da die meisten Beiträge in der Neu-Version verfügbar sind, erfolgt beim Abruf häufig der
#		Fehler 301 Moved Permanently.
#
def ARDStart(title): 
	PLog('ARDStart:'); 
	
	sendername = "ARD-Alle"
	title2 = "Sender: ARD-Alle"
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')										# Home-Button

	path = BASE_URL + "/tv" 
	# Seite aus Cache laden
	page = Dict("load", 'ARDStart_%s' % sendername, CacheTime=ARDStartCacheTime)					
	if page == False:											# nicht vorhanden oder zu alt
		page, msg = get_page(path=path)							# vom Sender holen
	
		if 'class="section onlyWithJs sectionA">' not in page:	# Fallback: Cache ohne CacheTime
			page = Dict("load", 'ARDStart_%s' % sendername)					
			msg1 = "Startseite nicht im Web verfuegbar."
			PLog(msg1)
			msg3=''
			if page:
				msg2 = "Seite wurde aus dem Addon-Cache geladen."
				msg3 = "Seite ist älter als %s Minuten (CacheTime)" % str(CacheTime/60)
			else:
				msg2='Startseite nicht im Cache verfuegbar.'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)	
		else:	
			Dict("store", 'ARDStart_%s' % sendername, page) 	# Seite -> Cache: aktualisieren	
		
	PLog(len(page))		
	
	# Rubriken: 
	gridlist = blockextract('class="section onlyWithJs sectionA">', page)		# Rubriken
	PLog(len(gridlist))
	for grid in gridlist:
		href = BASE_URL + "/tv" 						# Rest-Url in ARDStartRubrik

		if 'Stage' in grid:								# Highlights im Wischermodus
			ID = 'Swiper'								# Abgleich in ARDStartRubrik
			title 	= 'Highlights'
			img, img_alt = img_urlScheme(grid, 320, 'Sendereihen')

		elif 'Livestreams' in grid and 'Das-Erste/live?kanal=208' in grid:			
			ID = 'Livestreams'
			title 	= 'Livestreams'
			img = R(ICON_MAIN_TVLIVE)					# eigenes Icon für Livestreams
														# alle Live-Sender neu laden (PRG-Info):
			href = 'https://classic.ardmediathek.de/tv/live' 		

		else:
			ID = 'ARDStart'	
			title 	= stringextract('modHeadline">', '<span', grid)		# Zeile unter modHeadline
			title 	= title.strip()						# title ist Referenz für ARDStartRubrik
			img, img_alt = img_urlScheme(grid, 320) 
		
		if title == '':									# s.u.  Neueste Videos, Am besten bewertet
			continue
											
		PLog(title); PLog(ID);  PLog(img); PLog(href); 
		title = UtfToStr(title);  

		# Rubriken -> PageControl (Konflikt mit "Alle zeigen"). In PageControl wird cbKey 
		#	bei 2. Durchlauf (Weiter zu) von SingleSendung in PageControl getauscht.
		if title == 'Rubriken':							# Rubriken
			href = 'https://classic.ardmediathek.de/tv/Rubriken/mehr?documentId=21282550'
			img = R(ICON_ARD_RUBRIKEN)
			fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': 'SinglePage', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
				% (urllib2.quote(title),  urllib2.quote(href))
			addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=img, 
				thumb=img, fparams=fparams)
		else:	
			fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'sendername': '%s', 'ID': '%s'}" % (urllib2.quote(href), 
				urllib2.quote(title), urllib2.quote(img), sendername, ID)
			addDir(li=li, label=title, action="dirList", dirID="ARDStartRubrik", fanart=img, thumb=img, 
				fparams=fparams)
		
	# anfügen + nach PageControl verteilen:	
	#	s.a. Verzweigung in ARDStartSingle (Vorprüfung 1)	
	if '>Neueste Videos<' in page:						# Neueste Videos
		title 	= 'Neueste Videos'
		href =  BASE_URL + "/tv/Neueste-Videos/mehr?documentId=21282466"
		img = R(ICON_ARD_NEUESTE)			
		fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': 'SinglePage', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
			% (urllib2.quote(title),  urllib2.quote(href))
		addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=img, 
			thumb=img, fparams=fparams)
			
	if '>Am besten bewertet<' in page:					# Am besten bewertet
		title 	= 'Am besten bewertet'
		href =  BASE_URL + "/tv/Am-besten-bewertet/mehr?documentId=21282468"
		img = R(ICON_ARD_BEST)
		fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': 'SinglePage', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
			% (urllib2.quote(title),  urllib2.quote(href))
		addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=img, 
			thumb=img, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE)
#---------------------------------------------------------------------------------------------------
	
# Auflistung einer Rubrik aus ARDStart - title (ohne unescape) ist eindeutige Referenz 
# path=Seite aus ARDStart - wir laden aus dem Cache, speichern nicht
def ARDStartRubrik(path, title, img, sendername='', ID=''): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title); PLog(path); 
	title = UtfToStr(title)
	title_org 	= title 								# title ist Referenz zur Rubrik
		
	li = xbmcgui.ListItem()
	if 'Livestream' in title == False:					# Livestreams ohne Home-Button
		li = home(li, ID='ARD')							# Home-Button
		
	if sendername == '':
		sendername = "ARD-Alle"	
		
	page = False
	if 	ID == 'ARDStart':								# Startseite laden	
		page = Dict("load", 'ARDStart_%s', CacheTime=ARDStartCacheTime)	# Seite aus Cache laden		

	if page == False:									# keine Startseite od. Cache miss								
		page, msg = get_page(path=path, GetOnlyRedirect=True)
		path = page
		page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	found = False; grid = ''; 
	# mediatype: für Highlights (Einzelbeiträge) mit video vorbelegen 
	if ID == 'Swiper':												# vorangestellte Highlights
		gridlist = stringextract('<h2 class="modHeadline hidden', '<h2 class="modHeadline">', page)
		found = True
	else:
		if ID =='ARDStartSingle':									# Rücksprung aus ARDStartSingle	
			gridlist = blockextract('class="_focusable', page)
			found = True
		else:
			gridlist = blockextract('<h2 class="modHeadline">', page)	# Rubriken
			PLog('gridlist: ' + str(len(gridlist)))
			for grid in gridlist:
				title 	= stringextract('modHeadline">', '<span', grid)	# Zeile unter modHeadline
				title 	= title.strip()		
				PLog(title); PLog(title_org); 
				if title == title_org or ID == 'Livestreams':			# Referenz-Rubrik gefunden,
					gridlist = grid										#	bei Livestreams immer
					found = True
					break
	PLog('gridlist: ' + str(len(gridlist)))
	if found == False:	
		msg1 = "Rubrik >%s< nicht gefunden" % title_org
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		return li
	
	multi = False											# steuert Einzel-/Mehrfachbeiträge	
	sendungen = blockextract('class="teaser"', gridlist)
	PLog(len(sendungen))
	for s in sendungen:
		# PLog(s)		# Debug
		tagline=''; summ=''; mediatype=''
		# Achtung: gleichz. Vorkommen von 'bcastId=' + 'documentId=' kein Indiz für einz. Sendung.
		href 	= BASE_URL + stringextract('href="', '"', s) # OK häufig auch bei Classic-Version
		href 	= 	path = decode_url(href)
		title 	= stringextract('class="headline">', '<', s)
		subline =  stringextract('class="subtitle">', '<', s)
		img, img_alt = img_urlScheme(s, 320, 'Sendereihen') 										
													
		more_path = ''
		more	= stringextract('class="more', '<span', s)		# Link zu "ALLE ZEIGEN"
		if 'mehr?documentId=' in more:							# außer Livestreams (Alle bereits in path)
			more_path = BASE_URL + stringextract('href="', '"', more)
					
		if summ == '':											# summary (Inhaltstext) im Voraus holen,
			if ID != 'Livestreams':								#	Seite Livestreams enthält bereits EPG
				if SETTINGS.getSetting('pref_load_summary') == 'true':
					summ_txt = get_summary_pre(href, 'ARDClassic')
					if 	summ_txt:
						summ = summ_txt	
					
		if	ID == 'Livestreams':						
			if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
				mediatype='video'
			subline =  stringextract('class="subtitle">', '</p>', s) # Uhrzeit + Sendung
			subline = cleanhtml(subline); subline = unescape(subline);
			subline=subline.replace('&', '+') 
			sender = (title.replace('Livestream', '').replace('im', '')).strip()
			playlist_img, href = get_playlist_img(hrefsender=sender) # Icon, link aus livesenderTV.xml holen			
			
		tagline = stringextract('class="dachzeile">', '<', s)	
		duration= stringextract('duration">', '</div>', s)
		if duration:
			tagline = "%s | %s"	% (duration, subline)
		else:
			tagline = subline
		if tagline.endswith('| '):
			tagline = tagline.replace('| ', '')
			
		if 	title == '':
			continue
		title=UtfToStr(title); tagline=UtfToStr(tagline); subline=UtfToStr(subline);
		title=unescape(title); 	
		title=repl_json_chars(title) 		# dto.
		tagline=repl_json_chars(tagline) 	# dto.
		summ=repl_json_chars(summ) 			# dto.
		subline=subline.replace('"', '') 	# dto.
		subline=repl_json_chars(subline) 	# dto.
		
		PLog("title: " + title);  PLog(tagline); PLog(href); PLog(multi);		
		
		# -> SenderLiveResolution wie SenderLiveListe aus Hauptmenü, Fallback zum Classic-Senderlink
		#		bei Fehlschlag	
		if	ID == 'Livestreams':	
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'Startsender': 'true'}" %\
				(href, title, img, subline)
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
				thumb=img, fparams=fparams, summary=subline, mediatype=mediatype)					
		else:	
			if ID == 'Swiper':				# nur Einzelbeiräge zeigen (weitere Beiträge via PageControl möglich)
				Plot=summ					# für Einzelauflösungen/summary in SingleSendung
				sid = href.split('documentId=')[1]
				path = BASE_URL + '/play/media/' + sid			# -> *.mp4 (Quali.-Stufen) + master.m3u8-Datei (Textform)
				PLog('Medien-Url: ' + path)	
						
				if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
					mediatype='video'
					Plot = "%s||||%s" % (subline, summ)				# für Sofortstart/Plot in SingleSendung
						
				if 'Hörfassung' in title or 'Audiodeskription' in title:				# Filter
					if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true':
						continue		
					if SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
						continue		
						
				fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'duration': '%s', 'summary': '%s', 'tagline': '%s', 'ID': '%s', 'offset': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(title), urllib2.quote(img), 
					duration, urllib2.quote(Plot),  urllib2.quote(subline), 'ARD', '0')				
				addDir(li=li, label=title, action="dirList", dirID="SingleSendung", fanart=img, thumb=img, 
					fparams=fparams, summary=summ, tagline=subline, mediatype=mediatype)			
			else:
			
				next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl  SinglePage
				fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
					% (urllib2.quote(title), urllib2.quote(href), next_cbKey)
				addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=img, 
					thumb=img, fparams=fparams, tagline=tagline)
				
		if more_path:				# Button "ALLE ZEIGEN"	
			PLog("more_path more: " + more_path)	
			img 	= R(ICON_MEHR)
			title 	= "ALLE ZEIGEN"
			tagline	= "%s zu >%s<" % (title, title_org)
			next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl  SinglePage
			fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
				% (urllib2.quote(title), urllib2.quote(more_path), next_cbKey)
			addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=img, 
				thumb=img, fparams=fparams, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE)
			
####################################################################################################
# 	Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
#	ID = PODCAST, ARD
#	
def SendungenAZ(name, ID):		
	PLog('SendungenAZ: ' + name)
	PLog(ID)
	
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)								# Home-Button
		
	azlist = list(string.ascii_uppercase)					# A - Z, 0-9
	azlist.append('0-9')
	
	next_cbKey = 'PageControl'	# SinglePage zeigt die Sendereihen, PageControl dann die weiteren Seiten
	azPath = BASE_URL + ARD_AZ + 'A'		# A-Seite laden für Prüfung auf inaktive Buchstaben
	PLog(azPath)
	page, msg = get_page(azPath)		
	if page == '':
		msg1 = "Fehler in SendungenAZ"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	PLog(len(page))
	
	inactive_list = ""							# inaktive Buchstaben?
	inactive_range = stringextract('Aktuelle TV Auswahl:', 'subressort collapsed', page)
	inactive_list = blockextract('class=\"inactive\"', inactive_range)
	PLog('Inaktive: ' + str(len(inactive_list)))		

	inactive_char = ""
	if inactive_list:							# inaktive Buchstaben -> 1 String
		for element in inactive_list:
			char = stringextract('<a>', '</a>', element)
			char = char.strip()
			inactive_char =  inactive_char + char
	PLog('inactive_char: ' + inactive_char)							# z.B. XY
	
	for element in azlist:	
		# Log(element)
		if ID == 'ARD':
			azPath = BASE_URL + ARD_AZ + element
		if ID == 'PODCAST':
			azPath = POD_AZ + element
		button = element
		title = "Sendungen mit " + button
		PLog(title)
		PLog(button in inactive_char)
		if button in inactive_char:					# inaktiver Buchstabe?
			title = "Sendungen mit " + button + ': keine gefunden'
			fparams="&fparams={'name': 'Sendungen A-Z', 'ID': 'ARD'}"
			addDir(li=li, label=title, action="dirList", dirID="SendungenAZ", 
				fanart=R(ICON_ARD_AZ), thumb=R(ICON_ARD_AZ), fparams=fparams)
		else:
			mode = 'Sendereihen'
			fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': '%s', 'mode': '%s', 'ID': '%s'}" \
				% (urllib2.quote(title), urllib2.quote(azPath), next_cbKey, mode, ID)
			addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_ARD_AZ), 
				thumb=R(ICON_ARD_AZ), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
# Suche in beiden Mediatheken
#	Abruf jeweils der 1. Ergebnisseite
#	Ohne Ergebnis -> Button mit Rücksprung hierher
#	Ergebnis ZDF: -> ZDF_Search (erneuter Aufruf Seite 1, weitere Seiten dort rekursiv)
#		Ablage in Dict nicht erf., Kodi-Cache ausreichend.
#	Umlaute in Suche erzeugen unicode-Strings - UtfToStr-Behandl. jeweils in den Funktions-
#		ketten.
#
def SearchARDundZDF(title, query='', pagenr=''):
	PLog('SearchARDundZDF:');
	
	if query == '':
		query = get_query(channel='ARDundZDF') 
	if  query == None or query.strip() == '':
		return ""
		
	PLog(query)
	query_ard = query.split('|')[0]
	query_zdf = query.split('|')[1]
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)												# Home-Button
	tag_negativ ='neue Suche in ARD und ZDF starten'					# ohne Treffer
	tag_positiv ='gefundene Beiträge zeigen'							# mit Treffer
	
	
	#------------------------------------------------------------------	# Suche ARD
	path =  BASE_URL +  ARD_Suche 
	path_ard = path % urllib2.quote(query_ard)
	page, msg = get_page(path=path_ard)	
	channel='ARD'

	query_lable = query_ard.replace('+', ' ')
	
	if '<strong>keine Treffer</strong' in page:
		title="Suche in ARD und ZDF"
		label = "ARD | nichts gefunden zu: %s | neue Suche" % query_lable
		fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
		addDir(li=li, label=label, action="dirList", dirID="SearchARDundZDF", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		hits = re.findall("mresults=page", page)	# ['mresults=page', ..
		PLog(len(hits))								# '' bei 1 Seite
		cnt = len(hits)
		if cnt == 0:
			cnt = 1
			
		title = "ARD: %s Seite(n) | %s" % (str(cnt), query_lable)
		PLog(query_ard)
		fparams="&fparams={'title': '%s', 'query': '%s', 'channel': '%s'}" %\
			(title, urllib.quote_plus(query_ard), channel)
		addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
		
	#------------------------------------------------------------------	# Suche ZDF
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path_zdf = ZDF_Search_PATH % (urllib2.quote(query_zdf), pagenr) 
	page, msg = get_page(path=path_zdf)	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog(searchResult);
	
	query_lable = (query_zdf.replace('%252B', ' ').replace('+', ' ')) 	# quotiertes ersetzen 
	query_lable = urllib2.unquote(query_lable)
	if searchResult == '0' or 'class="artdirect " >' not in page:		# Sprung hierher
		label = "ZDF | nichts gefunden zu: %s | neue Suche" % query_lable
		title="Suche in ARD und ZDF"
		fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
		addDir(li=li, label=label, action="dirList", dirID="SearchARDundZDF", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		title = "ZDF: %s Video(s)  | %s" % (searchResult, query_lable)
		fparams="&fparams={'query': '%s', 'title': '%s', 'pagenr': '%s'}" % (urllib.quote_plus(query_zdf), 
			title, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
				
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
	# Suche - Verarbeitung der Eingabe
	# Vorgabe UND-Verknüpfung (auch Podcast)
	# Kodi-Problem ..-Button s.u.
	#
def Search(title, query='', channel='ARD'):
	PLog('Search:'); PLog(query); PLog(channel); 
			
	if 	query == '':	
		query = get_query(channel='ARD')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
	
	query = UtfToStr(query)	
	name = 'Suchergebnis zu: ' + urllib2.unquote(query)
		
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
			
	if channel == 'ARD':
		path =  BASE_URL +  ARD_Suche 
		path = path % urllib2.quote(query)
		ID='ARD'
	if channel == 'PODCAST':	
		path =  BASE_URL  + POD_SEARCH
		path = path % urllib2.quote(query)
		ID=channel
		
	li = xbmcgui.ListItem()		
	PLog(path)
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}"
	headers=urllib2.quote(headers)					# headers ohne quotes in get_page leer 
	page, msg = get_page(path=path, header=headers)	
	if page == '':						
		msg1 = 'Fehler in Suche: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
			
	if page.find('<strong>keine Treffer</strong') >= 0:
		msg1 = 'Leider kein Treffer.'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li

	# Kodi-Problem: Direktsprung n.m., da der ..-Button von xbmcgui.ListItem  zurück 
	#	zu get_query führt statt zur Liste der Ergebnisseiten. Leider muss der entspr. Code 
	#	aus PageControl hier nochmal verwemdet werden. Dafür verzichten wir hier auf den
	#	Offset und geben die Übersicht komplett aus.
	#	Mit mode='Suche|Query|Channel' stellt SinglePage einen Button voran, der Search mit den
	#   akt. Parametern ansteuert und damit die Übersicht erneut ausgibt.
	
	pagenr_suche = re.findall("mresults=page", page)
	pagenr_path =  re.findall("=page.(\d+)", page) # 
	# PLog(pagenr_path)
	if pagenr_path:
		# pagenr_path = repl_dop(pagenr_path) 	# Doppel entfernen (ohne offset immer 2)
		del pagenr_path[-1]						# letzten Eintrag entfernen - OK
	pagenr_path.insert(0, '1')					# Seite 1 einfügen
	PLog(pagenr_path)
	
	if 	pagenr_suche:							# Ergebnisse mit mehreren Seiten -> Seitenübersicht
		li = home(li, ID=ID)					# Home-Button nur für mehrere Seiten
		next_cbKey = 'SingleSendung'
		query=UtfToStr(query); channel=UtfToStr(channel);
		for pagenr in pagenr_path:
			mode = 'Suche|%s|%s'	% (query, channel) # abgefangen in get_query: |
			href = path + '&mresults=page.%s' %  pagenr
			# PLog(href)
			title = 'Weiter zu Seite %s' %  pagenr
			href=UtfToStr(href); mode=UtfToStr(mode);
			fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': '%s', 'mode': '%s', 'ID': '%s'}" \
				% (urllib2.quote(name), urllib2.quote(href), next_cbKey,  mode, ID)	
			addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_NEXT), 				
				thumb=R(ICON_MAIN_ARD), fparams=fparams)

 	else:										# Ergebnisse mit 1 Seite, wir springen direkt:
		SinglePage(title=title, path=path, next_cbKey='SingleSendung', mode='Suche', ID=ID)

	xbmcplugin.endOfDirectory(HANDLE)			# cacheToDisc nicht verwenden - so.o.AudioSearch

#----------------------------------------------------------------  
# Vorstufe von Search - nur in Kodi-Version.
#	blendet Tastatur ein und fragt Suchwort(e) ab.
#	
def get_query(channel='ARD'):
	PLog('get_query:')
	query = get_keyboard_input()			# Modul util
	if  query == None or query.strip() == '':
		return ""
	
	if channel == 'ARD' or channel == 'ARDundZDF':				
		if '|' in query:		# wir brauchen | als Parameter-Trenner in SinglePage
			msg1 = 'unerlaubtes Zeichen in Suchwort: |'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
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
	if channel == 'ARDundZDF':				# beide queries zusammengesetzt				
		query = "%s|%s" % (query_ard, query_zdf)							
		PLog('query_ARDundZDF: %s' % query);
		return	query
	if channel == 'ARDaudio':				# nur strip, quoting durch Aufrufer
		return 	query.strip()
			

####################################################################################################
# Liste der Wochentage
	# Ablauf (ARD): 	
	#		2. PageControl: Liste der Rubriken des gewählten Tages
	#		3. SinglePage: Sendungen der ausgewählten Rubrik mit Bildern (mehrere Sendungen pro Rubrik möglich)
	#		4. Parseplaylist: Auswertung m3u8-Datei (verschiedene Auflösungen)
	#		5. in Plex CreateVideoClipObject, in Kodi PlayVideo
	# Funktion VerpasstWoche bisher in www.ardmediathek nicht vorhanden. 
	#
	# ZDF:
	#	Wochentag-Buttons -> ZDF_Verpasst
	#
def VerpasstWoche(name, title):		# Wochenliste zeigen, name: ARD, ZDF Mediathek
	PLog('VerpasstWoche:')
	PLog(name);PLog(title); 
	 
	# Senderwahl deaktivert		
	CurSender 	= ARDSender[0]	# Default 1. Element ARD-Alle
	sendername, sender, kanal, img, az_sender = CurSender.split(':')	
	sendername = UtfToStr(sendername)
	title_org = '%s | aktuell: %s'	% (title, sendername)
	PLog("title_org: " + title_org)
	
	li = xbmcgui.ListItem()
	if name == 'ZDF Mediathek':
		li = home(li, ID='ZDF')						# Home-Button
	else:	
		li = home(li, ID='ARD')						# Home-Button
		
	wlist = range(0,7)
	now = datetime.datetime.now()

	for nr in wlist:
		iPath = BASE_URL + ARD_VERPASST + str(nr)	# classic.ardmediathek.de'
		if kanal:
			iPath = '%s&kanal=%s' % (iPath, kanal)
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
		PLog(iPath); PLog(iDate); PLog(iWeekday);
		#title = ("%10s ..... %10s"% (iWeekday, iDate))	 # Formatierung in Plex ohne Wirkung		
		title =	"%s | %s" % (iDate, iWeekday)
		cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
		if name == 'ARD':
			summ = 'Gezeigt wird der Inhalt für %s' % sendername
			if kanal == '' and sendername != 'ARD-Alle': # Sender noch ohne Kanalnummer? 
				summ = 'Gezeigt wird der Inhalt für %s - Seite für %s fehlt!' % ('ARD-Alle', sendername)
			fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': 'SinglePage', 'mode': 'Verpasst', 'ID': 'ARD'}" \
				% (urllib2.quote(title),  urllib2.quote(iPath))
			addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_VERP), 
				thumb=R(ICON_ARD_VERP), fparams=fparams, tagline=summ)

		else:
			fparams="&fparams={'title': '%s', 'zdfDate': '%s'}" % (title, urllib2.quote(zdfDate))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Verpasst", fanart=R(ICON_ZDF_VERP), 
				thumb=R(ICON_ZDF_VERP), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)		
	
####################################################################################################
# Dachfunktion für Podcasts: 'Rubriken' .. 'Refugee-Radio'
#
# next_cbKey: Vorgabe für nächsten Callback in SinglePage
# mode: 'Sendereihen', 'Suche' 	- steuert Ausschnitt in SinglePage + bei Podcast Kopfauswertung 1.Satz
#									
def PODMore(title, morepath, next_cbKey, ID, mode):
	PLog('PODMore:'); PLog(morepath); PLog(ID)
	title2=title
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)					# Home-Button
					 
	path = morepath			
	page, msg = get_page(path=path)	
	if page == '':							# ARD-spezif. Error-Test: 'Leider liegt eine..'
		msg1 = 'Fehler: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
					
	PLog(len(page))					
	pagenr_path =  re.findall("=page.(\d+)", page) # Mehrfachseiten?
	PLog("pagenr_path: " + str(pagenr_path))
	if pagenr_path:
		del pagenr_path[-1]						# letzten Eintrag entfernen (Doppel) - OK
	PLog(pagenr_path)
	PLog(path)	
	
	if page.find('mcontents=page.') >= 0: 		# Podcast
		prefix = 'mcontents=page.'
	if page.find('mcontent=page') >= 0: 		# Default
		prefix = 'mcontent=page.'
	if page.find('mresults=page') >= 0: 		# Suche (hier i.d.R. nicht relevant, Direktsprung zu PageControl)
		prefix = 'mresults=page.'

	if pagenr_path:	 							# bei Mehrfachseiten Liste Weiter bauen, beginnend mit 1. Seite
		title = 'Weiter zu Seite 1'
		path = morepath + '&' + prefix + '1' # 1. Seite, morepath würde auch reichen
		PLog(path)
		fparams="&fparams={'path': '%s', 'title': '%s', 'next_cbKey':'%s', 'mode': '%s', 'ID': '%s'}"  \
			% (urllib.quote_plus(path), title, next_cbKey, mode, ID)
		addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_NEXT), thumb=R(ICON_NEXT), 
			fparams=fparams)
		
		for page_nr in pagenr_path:
			path = morepath + '&' + prefix + page_nr
			title = 'Weiter zu Seite ' + page_nr
			PLog(path)
			fparams="&fparams={'path': '%s', 'title': '%s', 'next_cbKey': '%s', 'mode': '%s', 'ID': '%s'}"  \
				% (urllib.quote_plus(path),title, next_cbKey, mode, ID)
			addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_NEXT), thumb=R(ICON_NEXT), 
				fparams=fparams)
	else:										# bei nur 1 Seite springen wir direkt, z.Z. bei Rubriken
		li = SinglePage(path=path, title=title, next_cbKey=next_cbKey, mode='Sendereihen', ID=ID)
		return li
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

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
		
	if  Inhalt is None or Inhalt == '':				
		msg1='Datei podcast-favorits.txt nicht gefunden oder nicht lesbar.'
		msg2='Bitte Einstellungen prüfen.'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return
							
	# PLog(Inhalt) 
	bookmarks = []
	lines = Inhalt.splitlines()
	for line in lines:						# Kommentarzeilen + Leerzeilen löschen
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
	li = home(li,ID='ARDaudio')				# Home-Button

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
		title = UtfToStr(title)
		summary='Favoriten: ' + title
		fparams="&fparams={'title': '%s', 'path': '%s'}" % \
			(urllib2.quote(title), urllib2.quote(path))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFavoriten", 
			fanart=R(ICON_STAR), thumb=R(ICON_STAR), fparams=fparams, summary=path, 
			tagline=summary)
					
	# Mehr Seiten anzeigen:
	PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt + int(offset)
		PLog(new_offset)
		summ = 'Mehr (insgesamt ' + str(max_len) + ' Favoriten)'
		fparams="&fparams={'title': '%s', 'offset': '%s'}" % (urllib2.quote(title_org), new_offset)
		addDir(li=li, label=summ, action="dirList", dirID="PodFavoritenListe", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams, summary=title_org, tagline='Favoriten')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
# z.Z. nur Hörfassungen - siehe ZDF (BarriereArm)	
# ausbauen, falls PMS mehr erlaubt (Untertitle)
# ohne offset - ARD-Ergebnisse werden vom Sender seitenweise ausgegeben 
def BarriereArmARD(name):		# 
	PLog('BarriereArmARD:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')										# Home-Button

	title = 'Hörfassungen (ARD-Suche)'							# ARD-Suche nach Hörfassungen
	title = UtfToStr(title)										#	mode=Suche
	query = urllib2.quote(title, "utf-8")
	path = BASE_URL + ARD_Suche	%   urllib2.quote('Hörfassungen', "utf-8")
	
	if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true' or \
		SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
		msg1 = 'Hinweis:'
		msg2 = 'Filter für Hörfassungen oder  Audiodeskription ist eingeschaltet!'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, "")		
	
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
	fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Suche', 'ID': 'ARD'}" \
		% (urllib2.quote(title), urllib2.quote(path), next_cbKey)
	addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_BARRIEREARM), 
		thumb=R(ICON_ARD_HOERFASSUNGEN), fparams=fparams)

	title = 'Tagesschau mit Gebärdensprache'					# Tagesschau-mit-Gebärdensprache
	title = UtfToStr(title)										#	mode=Sendereihen
	query = urllib2.quote(title, "utf-8")
	path =  BASE_URL + '/tv/Tagesschau-mit-Geb%C3%A4rdensprache/Sendung?documentId=12722002&bcastId=12722002'
	
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
	fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Sendereihen', 'ID': 'ARD'}" \
		% (urllib2.quote(title), urllib2.quote(path), next_cbKey)
	addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_BARRIEREARM), 
		thumb=R(ICON_ARD_BARRIEREARM), fparams=fparams)

	title = 'Untertitel (ARD-Suche)'							# ARD-Suche nach Untertiteln
	title = UtfToStr(title)										#	mode=Suche
	query = urllib2.quote(title, "utf-8")
	path = BASE_URL + ARD_Suche	%  'Untertitel'
	
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
	fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Suche', 'ID': 'ARD'}" \
		% (urllib2.quote(title), urllib2.quote(path), next_cbKey)
	addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_BARRIEREARM), 
		thumb=R(ICON_ARD_BARRIEREARM), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
	# kontrolliert auf Folgeseiten. Mehrfache Verwendung.
	# Wir laden beim 1. Zugriff alle Seitenverweise in eine Liste. Bei den Folgezugriffen können die Seiten-
	# verweise entfallen - der Rückschritt zur Liste ist dem Anwender nach jedem Listenelement  möglich.
	# Dagegen wird in der Mediathek geblättert.
	# PODMore stellt die Seitenverweise selbst zusammen.	
	# 
def PageControl(cbKey, title, path, mode, ID, offset=0):  # ID='ARD', 'POD', mode='Suche', 'VERPASST', 'Sendereihen'
	PLog('PageControl:'); PLog('cbKey: ' + cbKey); PLog(path)
	PLog('mode: ' + mode); PLog('ID: ' + str(ID))
	title1='Folgeseiten: ' + title
	
	li = xbmcgui.ListItem()		
	
	#headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
	#	'Accept': '*/*', 'Host': 'classic.ardmediathek.de'}"
	#headers=urllib2.quote(headers)					# headers ohne quotes in get_page leer 
	page, msg = get_page(path=path, header='')		# z.Z. nicht erf.
	if page == '':
		msg1 = 'PageControl: Beiträge können nicht geladen werden.'
		msg2 = 'Fehler: %s'	% msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			
	PLog(len(page))
	path_page1 = path							# Pfad der ersten Seite sichern, sonst gehts mit Seite 2 weiter	

	pagenr_suche = re.findall("mresults=page", page)   
	pagenr_andere = re.findall("mcontents=page", page)  
	pagenr_einslike = re.findall("mcontent=page", page)  	# auch in ARDThemen
	PLog(pagenr_suche); PLog(pagenr_andere); PLog(pagenr_einslike)
	if (pagenr_suche) or (pagenr_andere) or (pagenr_einslike):
		PLog('PageControl: Mehrfach-Seite mit Folgeseiten')
	else:												# keine Folgeseiten -> SinglePage
		PLog('PageControl: Einzelseite, keine Folgeseiten'); PLog(cbKey); PLog(path); PLog(title)
		li = SinglePage(title=title, path=path, next_cbKey='SingleSendung', mode=mode, ID=ID) # wir springen direkt 
		#if len(li) == 1:								# 1 = Home, len(li) bei Kodi n.v.
		#	msg1 = 'Keine Inhalte gefunden.'		
		#	xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li																				

	# pagenr_path =  re.findall("&mresults{0,1}=page.(\d+)", page) # lange Form funktioniert nicht
	pagenr_path =  re.findall("=page.(\d+)", page) # 
	PLog(pagenr_path)
	if pagenr_path:
		# pagenr_path = repl_dop(pagenr_path) 	# Doppel entfernen (z.B. Zif. 2) - Plex verweigert, warum?
		del pagenr_path[-1]						# letzten Eintrag entfernen - OK
	PLog(pagenr_path)
	pagenr_path = pagenr_path[0]	# 1. Seitennummer in der Seite - brauchen wir nicht , wir beginnen bei 1 s.u.
	PLog(pagenr_path)		
	
	# ab hier Liste der Folgeseiten. Letzten Eintrag entfernen (Mediathek: Rückverweis auf vorige Seite)
	# Hinw.: die Endmontage muss mit dem Pfad der 1. Seite erfolgen, da ev. Umlaute in den Page-Links 
	#	nicht erfolgreich gequotet werden können (Bsp. Suche nach 'Hörfassung) - das ZDF gibt die
	#	Page-Links unqoted aus, die beim HTTP.Request zum error führen.
	list = blockextract('class=\"entry\"', page)  # sowohl in A-Z, als auch in Verpasst, 1. Element
	del list[-1]				# letzten Eintrag entfernen - wie in pagenr_path
	PLog(len(list))

	first_site = True								# falls 1. Aufruf ohne Seitennr.: im Pfad ergänzen für Liste		
	if (pagenr_suche) or (pagenr_andere) or (pagenr_einslike) :		# re.findall s.o.  
		if 	'=page'	not in path:
			if pagenr_andere: 
				path_page1 = path_page1 + 'mcontents=page.1'
				path_end =  '&mcontents=page.'				# path_end für die Endmontage
			if pagenr_suche:
				path_page1 = path_page1 + '&mresults=page.1'# Suche
				path_end = '&mresults=page.' 
			if pagenr_einslike:								#  einslike oder Themen
				path_page1 = path_page1 + 'mcontent=page.1'
				path_end = '&mcontent=page.'
		PLog('path_end: ' + path_end)
	else:
		first_site = False
		
	PLog(first_site)
	if  first_site == True:										
		path_page1 = path
		title = 'Weiter zu Seite 1'
		next_cbKey = 'SingleSendung'
			
		PLog(first_site); PLog(path_page1); PLog(next_cbKey)
		path_page1 = UtfToStr(path_page1)
		fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': 'SingleSendung', 'mode': '%s', 'ID': '%s'}" \
			% (urllib2.quote(title), urllib2.quote(path_page1), mode, ID)	
		addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=ICON, thumb=ICON, fparams=fparams)
	
	else:	# Folgeseite einer Mehrfachseite - keine Liste mehr notwendig
		PLog(first_site)										# wir springen wieder direkt:
		SinglePage(title=title, path=path, next_cbKey='SingleSendung', mode=mode, ID=ID)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)	# und  springen wieder zurück	
		
	for element in list:	# [@class='entry'] 
		pagenr_suche = ''; pagenr_andere = ''; title = ''; href = ''
		href = stringextract(' href=\"', '\"', element)
		href = unescape(href)
		if href == '': 
			continue							# Satz verwerfen
			
		# PLog(element); 	# PLog(s)  # class="entry" - nur bei Bedarf
		pagenr =  re.findall("=page.(\d+)", element) 	# einzelne Nummer aus dem Pfad s ziehen	
		PLog(pagenr); 
					
		if (pagenr):							# fehlt manchmal, z.B. bei Suche
			if href.find('=page.') >=0:			# Endmontage
				title = 'Weiter zu Seite ' + pagenr[0]
				href =  path_page1 + path_end + pagenr[0]
			else:				
				continue						# Satz verwerfen
		else:
			continue							# Satz verwerfen
			
		PLog('href: ' + href); PLog('title: ' + title)
		next_cbKey = 'SingleSendung'
		fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': '%s', 'mode': '%s', 'ID': '%s'}" \
			% (urllib2.quote(title), urllib2.quote(href), next_cbKey, mode, ID)	
		addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_NEXT), 
			thumb=R(ICON_NEXT), fparams=fparams)
 
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
  
####################################################################################################
# Liste der Sendungen eines Tages / einer Suche 
# durchgehend angezeigt (im Original collapsed)
def SinglePage(title, path, next_cbKey, mode, ID, offset=0):	# path komplett
	PLog('SinglePage: ' + path)
	PLog('mode: ' + mode); PLog('next_cbKey: ' + next_cbKey); PLog('ID: ' + str(ID))
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)							# Home-Button
	
	func_path = path								# für Vergleich sichern					
	page, msg = get_page(path=path)
	if page == '':
		msg1 = 'Fehler:'
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	
	sendungen = ''
	
	if mode == 'Suche':									# relevanten Inhalt ausschneiden, Blöcke bilden
		page = stringextract('data-ctrl-scorefilterloadableLoader-source', '<!-- **** END **** -->', page)	
	if mode == 'Verpasst':								
		page = stringextract('"boxCon isCollapsible', '<!-- **** END **** -->', page)	
	if mode == 'Sendereihen':	
		if ID == 'PODCAST':						       # auch A-Z 
			# Filter nach next_cbKey (PageControl, 	SinglePage, SingleSendung) hier nicht erforderlich	
			page = stringextract('class=\"section onlyWithJs sectionA\">', '<!-- content -->', page)
		else:
			page = stringextract('data-ctrl-layoutable', '<!-- **** END **** -->', page)	
	sendungen = blockextract('class="teaser"', page)	# Sendungsblöcke in PODCAST: 1. teaser=Sendungskopf, 
	PLog('sendungen: ' + str(len(sendungen)))			#   Rest Beiträge - Auswertung in get_sendungen	
	PLog(len(page));													
	if len(sendungen) == 0:								# Fallback 	
		sendungen = blockextract('class="entry"', page) 				
		PLog('sendungen, Fallback: ' + str(len(sendungen)))

	# mode = 'Suche|Query|Channel': mit Suchbegriff Button für Seitenübersicht 
	if '|' in mode:					# voranstellen - s. Search	
		mode=UtfToStr(mode);
		dummy, query, channel = mode.split('|')
		PLog(dummy); PLog(query); PLog(channel); 
		title = 'Suchergebnis zu: %s'  % query
		label = 'Zurück zur Seitenübersicht'
		fparams="&fparams={'title': '%s', 'query': '%s',  'channel': '%s'}" % (urllib2.quote(title), \
			urllib2.quote(query), channel)
		addDir(li=li, label=label, action="dirList", dirID="Search", fanart=R('icon-pages.png'), 
			thumb=R('icon-pages.png'), fparams=fparams)			
	
	mediatype=''							# Kennz. Video für Sofortstart, hier für dirID="SingleSendung"
	if ID != 'PODCAST':						# nicht bei Podcasts
		if SETTINGS.getSetting('pref_video_direct') == 'true':
			mediatype='video'
	
	send_arr = get_sendungen(li, sendungen, ID, mode)	# send_arr enthält pro Satz 9 Listen 
	# Rückgabe send_arr = (send_path, send_headline, send_img_src, send_millsec_duration)
	#PLog(send_arr); PLog('Länge send_arr: ' + str(len(send_arr)))
	send_path = send_arr[0]; send_headline = send_arr[1]; send_subtitle = send_arr[2];
	send_img_src = send_arr[3]; send_img_alt = send_arr[4]; send_millsec_duration = send_arr[5]
	send_dachzeile = send_arr[6]; send_sid = send_arr[7]; send_teasertext = send_arr[8]

	#PLog(send_path); #PLog(send_arr)
	PLog('Sätze: ' + str(len(send_path)));
	for i in range(len(send_path)):					# Anzahl in allen send_... gleich
		PLog(send_headline[i]); PLog(send_subtitle[i]); PLog(send_img_alt[i]); PLog(send_dachzeile[i]); 
		PLog(send_teasertext[i]);
		path = send_path[i]
		headline = send_headline[i]					# UtfToStr, unescape, "-Ersatz in get_sendungen
		subtitle = send_subtitle[i]
		subtitle = UtfToStr(subtitle)
		
		if 'Hörfassung' in headline or 'Hörfassung' in subtitle:			# Filter
			if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true':
				continue
		if 'Audiodeskription' in headline or 'Audiodeskription' in subtitle:# Filter
			if SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
				continue
			
		if next_cbKey == 'PageControl' and subtitle:	# A-Z: subtitle enthält Sender
			headline = "%s | %s" % (headline, subtitle)
		img_src = send_img_src[i]
		img_alt = send_img_alt[i]
		img_alt = UtfToStr(img_alt)
		img_alt = unescape(img_alt)
		millsec_duration = send_millsec_duration[i]
		if not millsec_duration:
			millsec_duration = "leer"
		dachzeile = send_dachzeile[i]
		dachzeile = UtfToStr(dachzeile)
		PLog(dachzeile)
		sid = send_sid[i]
		teasertext = send_teasertext[i]

		summary = ''	
		if teasertext != "":				# teasertext z.B. bei Podcast
			summary = teasertext
		else:  
			if dachzeile != "":
				summary = dachzeile 
			if  subtitle != "":
				summary = subtitle
				if  dachzeile != "":
					summary = dachzeile + ' | ' + subtitle
					
		summary = UtfToStr(summary)
		summary = unescape(summary)
		summary = cleanhtml(summary)
		subtitle = cleanhtml(subtitle)
		subtitle = UtfToStr(subtitle)
		dachzeile = UtfToStr(dachzeile)
		PLog(headline); PLog(subtitle); PLog(dachzeile)
				
		path = UtfToStr(path)				# Pfade können Umlaute enthalten
		img_src = UtfToStr(img_src)
		func_path = UtfToStr(func_path)
														# teasertext (Inhaltstext) im Voraus holen falls 
														#	 leer:	
		if teasertext == '':	
			if SETTINGS.getSetting('pref_load_summary') == 'true':
				txt = get_summary_pre(BASE_URL + path, 'ARDClassic')
				if 	txt:
					summary = "%s\n\n%s" % (subtitle, txt)
					if dachzeile:
						summary = "%s | %s\n\n%s" % (dachzeile, subtitle, txt)
		
		if subtitle in summary:				# Doppler subtitle durch Bildtext ersetzen
			subtitle = img_alt			
			
		headline=repl_json_chars(headline)			# json-komp.
		subtitle=repl_json_chars(subtitle)			# dto.
		summary=repl_json_chars(summary)			# dto.
		
		PLog('neuer Satz'); PLog('path: ' + path); PLog(title); PLog(img_src); PLog(millsec_duration);
		PLog('next_cbKey: ' + next_cbKey); PLog('summary: ' + summary);
		if '/tv/Rubriken/mehr' in func_path:		# Sonderfall: Austausch next_cbKey für Rubriken, da
			next_cbKey = 'PageControl'				#	nochmal Seiten mit Seitenkontrolle folgen - s. ARDStart
		if next_cbKey == 'SingleSendung':		# Callback verweigert den Funktionsnamen als Variable
			PLog('path: ' + path); PLog('func_path: ' + func_path); PLog('subtitle: ' + subtitle); PLog(sid)
			PLog(ID)
			if ID == 'PODCAST' and img_src == '':	# Icon für Podcast
				img_src = R(ICON_NOTE)					     
			if func_path == BASE_URL + path: 	# überspringen - in ThemenARD erscheint der Dachdatensatz nochmal
				PLog('BASE_URL + path == func_path | Satz überspringen');
				continue
			if sid == '':
				continue
			#if subtitle == '':	# ohne subtitle verm. keine EinzelSendung, sondern Verweis auf Serie o.ä.
			#	continue		#   11.10.2017: Rubrik "must see" ohne subtitle
			if subtitle == summary or subtitle == '':
				subtitle = UtfToStr(img_alt)
			# 27.12.2017 Sendungslisten (mode: Sendereihen) können (angehängte) Verweise auf Sendereihen enthalten,
			#	Bsp. https://classic.ardmediathek.de/tv/filme. Erkennung: die sid enthält die bcastId, Bsp. 1933898&bcastId=1933898
			if '&bcastId=' in path:				#  keine EinzelSendung -> Sendereihe
				PLog('&bcastId= in path: ' + path)
				if path.startswith('http') == False:	# Bsp. /tv/Film-im-rbb/Sendung?documentId=10009780&bcastId=10009780
					path = BASE_URL + path
				fparams="&fparams={'path': '%s', 'title': '%s', 'cbKey': 'SinglePage', 'mode': 'Sendereihen', 'ID': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(headline), ID)	
				addDir(li=li, label=headline, action="dirList", dirID="PageControl", fanart=img_src, thumb=img_src, 
					fparams=fparams, summary='Folgeseiten', tagline=subtitle)
			else:								# normale Einzelsendung, Bsp. für sid: 48545158
				path = BASE_URL + '/play/media/' + sid			# -> *.mp4 (Quali.-Stufen) + master.m3u8-Datei (Textform)
				PLog('Medien-Url: ' + path)			
				PLog(img_src)
				summ_par=summary.replace('\n', '||')		# || Code für LF (\n scheitert in router)
				fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'duration': '%s', 'summary': '%s', 'tagline': '%s', 'ID': '%s', 'offset': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(headline), urllib2.quote(img_src), 
					millsec_duration, urllib2.quote(summ_par),  urllib2.quote(subtitle), ID, offset)				
				addDir(li=li, label=headline, action="dirList", dirID="SingleSendung", fanart=img_src, thumb=img_src, 
					fparams=fparams, summary=summary, tagline=subtitle, mediatype=mediatype)
		if next_cbKey == 'SinglePage':						# mit neuem path nochmal durchlaufen
			PLog('next_cbKey: SinglePage in SinglePage')
			path = BASE_URL + path
			PLog('path: ' + path);
			if mode == 'Sendereihen':			# Seitenkontrolle erforderlich, dto. Rubriken in Podcasts
				fparams="&fparams={'path': '%s', 'title': '%s', 'cbKey': 'SinglePage', 'mode': 'Sendereihen', 'ID': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(headline), ID)	
				addDir(li=li, label=headline, action="dirList", dirID="PageControl", fanart=img_src, thumb=img_src, 
					fparams=fparams, summary='Folgeseiten', tagline=subtitle)
			else:
				fparams="&fparams={'path': '%s', 'title': '%s', 'next_cbKey': 'SingleSendung', 'mode': '%s', 'ID': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(headline), mode, ID)	
				addDir(li=li, label=headline, action="dirList", dirID="SinglePage", fanart=img_src, thumb=img_src, 
					fparams=fparams, summary=summary, tagline=subtitle)
		if next_cbKey == 'PageControl':		
			path = BASE_URL + path
			PLog('path: ' + path);
			PLog('next_cbKey: PageControl in SinglePage')
			
			fparams="&fparams={'path': '%s', 'title': '%s', 'cbKey': 'SingleSendung', 'mode': 'Sendereihen', 'ID': '%s'}" \
				% (urllib2.quote(path), urllib2.quote(headline), ID)	
			addDir(li=li, label=headline, action="dirList", dirID="PageControl", fanart=img_src, thumb=img_src, 
				fparams=fparams, summary=summary, tagline=subtitle)						
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
####################################################################################################
# ARD - einzelne Sendung, path in neuer Mediathekführt zur 
# Quellenseite (verschiedene Formate -> 
#	1. Text-Seite mit Verweis auf .m3u8-Datei und / oder href_quality_ Angaben zu mp4-videos -
#		im Listenformat, nicht m3u8-Format, die verlinkte master.m3u8 ist aber im 3u8-Format
#	2. Text-Seite mit rtmp-Streams (Listenformat ähnlich Zif. 1, rtmp-Pfade müssen zusammengesetzt
#		werden
#   ab 01.04.2017 mit Podcast-Erweiterung auch Verabeitung von Audio-Dateien
#	18.04.2017 die Podcasts von PodFavoriten enthalten in path bereits mp3-Links, parseLinks_Mp4_Rtmp entfällt
#
# path: z.B. https://classic.ardmediathek.de/play/media/11177770
def SingleSendung(path, title, thumb, duration, summary, tagline, ID, offset=0, Merk='false'):	
	PLog('SingleSendung:')						
	PLog('path: ' + path)			
	PLog('ID: ' + str(ID))
	PLog(thumb); PLog(summary); PLog(tagline);
	
	title = urllib2.unquote(title)
	title = UtfToStr(title); summary = UtfToStr(summary); tagline = UtfToStr(tagline)
	title_org=title; summary_org=summary; tagline_org=tagline	# Backup 
	
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)				# Home-Button
	# PLog(path)
	
	if ID == 'PODCAST':
		Format = 'Podcast-Format: MP3'					# Verwendung in summmary
	else:
		Format = 'Video-Format: MP4'
		
	mediatype=''						# Kennz. Video für Sofortstart, hier für dirID="SingleSendung"
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	# Bei Podcasts enthält path i.d.R. 1 Link zur Seite mit einer mp3-Datei, bei Podcasts von PodFavoriten 
	# wird der mp3-Link	direkt in path übergeben.
	if path.endswith('.mp3') == False:
		page, msg = get_page(path=path)				# Absicherung gegen Connect-Probleme. Page=Textformat
		if page == '':
			msg1 = 'Fehler:'
			msg2 = msg
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li
		link_path,link_img, m3u8_master, geoblock, sub_path = parseLinks_Mp4_Rtmp(page) # link_img kommt bereits mit thumb, außer Podcasts						
		PLog('m3u8_master: ' + m3u8_master); PLog(link_img); PLog(link_path); PLog(sub_path);
		if thumb == None or thumb == '': 
			thumb = link_img

		if link_path == []:	      		# keine Videos gefunden		
			PLog('link_path == []') 		 
			msg1 = 'keine Videoquelle gefunden. Seite:'
			msg2 = path
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		PLog('geoblock: ' + geoblock)
		if geoblock == 'true':			# Info-Anhang für summary 
			geoblock = ' | Geoblock!'
		else:
			geoblock = ''
	else:
		m3u8_master = False
		# Nachbildung link_path, falls path == mp3-Link:
		link_path = []; link_path.append('1|'  + path)	# Bsp.: ['1|http://mp3-download.ard.de/...mp3]
  
	# *.m3u8-Datei vorhanden -> auswerten, falls ladefähig. die Alternative 'Client wählt selbst' (master.m3u8)
	# stellen wir voran (WDTV-Live OK, VLC-Player auf Nexus7 'schwerwiegenden Fehler'), MXPlayer läuft dagegen
	summary=summary.replace('||', '\n')		
	summary_org = summary_org.replace('\n', '||')
	if m3u8_master:	 		 		  								# nicht bei rtmp-Links (ohne master wie m3u8)
		# Sofortstart - direkt, falls Listing nicht Playable:
		if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true': 
			PLog('Sofortstart: SingleSendung')
			PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
			# sub_path=''	# fehlt bei ARD - entf. ab 1.4.2019
			PlayVideo(url=m3u8_master, title=title_org, thumb=thumb, Plot=summary, sub_path=sub_path)
			return
			
		title = '1. Bandbreite und Auflösung automatisch' + geoblock			# master.m3u8
		m3u8_master = m3u8_master.replace('https', 'http')	# 26.06.2017: nun auch ARD mit https
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
			(urllib.quote_plus(m3u8_master), urllib.quote_plus(title_org), urllib.quote_plus(thumb), 
			urllib.quote_plus(summary_org), urllib.quote_plus(sub_path), Merk)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			mediatype=mediatype, tagline=tagline, summary=summary) 
						
		summary_org = summary_org.replace('\n', '||')
		summary = summary.replace('\n', '||')
		li = Parseplaylist(li, m3u8_master, thumb, geoblock='', tagline=tagline, summary=summary_org, descr=summary, 
			sub_path=sub_path)
		#del link_path[0]								# master.m3u8 entfernen, Rest bei m3u8_master: mp4-Links
		PLog(li)  										
	 
	# ab hier Auswertung der restlichen mp4-Links bzw. rtmp-Links (aus parseLinks_Mp4_Rtmp)
	# Format: 0|http://mvideos.daserste.de/videoportal/Film/c_610000/611560/format706220.mp4
	# 	oder: rtmp://vod.daserste.de/ardfs/mp4:videoportal/mediathek/...
	#	
	href_quality_S 	= ''; href_quality_M 	= ''; href_quality_L 	= ''; href_quality_XL 	= ''
	download_list = []		# 2-teilige Liste für Download: 'title # url'
	li_cnt = 1
	for i in range(len(link_path)):
		s = link_path[i]
		href = s.split('|')[1].strip() # Bsp.: auto|http://www.hr.. / 0|http://pd-videos.daserste.de/..
		PLog('s: ' + s)
		if s[0:4] == "auto":	# m3u8_master bereits entfernt. Bsp. hier: 	
			# http://tagesschau-lh.akamaihd.net/z/tagesschau_1@119231/manifest.f4m?b=608,1152,1992,3776 
			#	Platzhalter für künftige Sendungen, z.B. Tagesschau (Meldung in Original-Mediathek:
			# 	'dieser Livestream ist noch nicht verfügbar!'
			#	auto aber auch bei .mp4-Dateien beobachtet, Bsp.: http://www.ardmediathek.de/play/media/40043626
			# href_quality_Auto = s[2:]	
			href_quality_Auto = href	# auto auch bei .mp4-Dateien möglich (s.o.)
			title = 'Qualitaet AUTO'
			url = href_quality_Auto
			resolution = ''
		if s[0:1] == "0":			
			href_quality_S = href
			title = 'Qualitaet SMALL'
			url = href_quality_S
			resolution = 240
			download_list.append(title + '#' + url)
		if s[0:1] == "1":			
			href_quality_M = href
			title = 'Qualitaet MEDIUM'
			url = href_quality_M
			resolution = 480
			download_list.append(title + '#' + url)
		if s[0:1] == "2":			
			href_quality_L = href
			title = 'Qualitaet LARGE'
			url = href_quality_L
			resolution = 540
			download_list.append(title + '#' + url)
		if s[0:1] == "3":			
			href_quality_XL = href
			title = 'Qualitaet EXTRALARGE'
			url = href_quality_XL
			resolution = 720
			download_list.append(title + '#' + url)
			

		PLog('title: ' + title); PLog('url: ' + url);  PLog(summary)
		if url:
			if '.m3u8' in url:				# master.m3u8 überspringen, oben bereits abgehandelt
				continue
			if 'manifest.f4m' in url:		# manifest.f4m überspringen
				continue
						
			if url.find('rtmp://') >= 0:	# 2. rtmp-Links:	
				summary = Format + 'RTMP-Stream'	
				lable = "%s | %s" % (title, summary)				
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
					(urllib.quote_plus(url), urllib.quote_plus(title_org), urllib.quote_plus(thumb), 
					urllib.quote_plus(summary_org), urllib.quote_plus(sub_path), Merk)
				addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
					 mediatype=mediatype, tagline=tagline, summary=summary)
									
			else:
				summary = "%s\n%s" % (title, Format)		# 3. Podcasts mp3-Links, mp4-Links
				if ID == 'PODCAST':			# (noch) keine Header benötigt
					lable = "%s. %s | %s" % (str(li_cnt), title, summary)
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(url), 
						urllib2.quote(title_org), urllib2.quote(thumb), urllib.quote_plus(summary_org))
					addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams, 
						tagline=tagline, summary=summary, mediatype='music')
				else:
					# 26.06.2017: nun auch ARD mit https - aber: bei den mp4-Videos liefern die Server auch
					#	mit http, während bei m3u8-Url https durch http ersetzt werden MUSS. 
					url = url.replace('https', 'http')	
					lable = "%s. %s | %s" % (str(li_cnt), title, Format+geoblock)
					summ_lable=summary_org.replace('||', '\n')	
					summary_org = summary_org.replace('\n', '||')
					
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
						(urllib.quote_plus(url), urllib.quote_plus(title_org), urllib.quote_plus(thumb), 
						urllib.quote_plus(summary_org), urllib.quote_plus(sub_path), Merk)
					addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
						mediatype=mediatype, summary=summ_lable) 
			li_cnt=li_cnt+1
						
	PLog(download_list)
	if 	download_list:			
		# high=-1: letztes Video bisher höchste Qualität
		if summary_org == None:		# Absicherungen für MakeDetailText
			summary_org=''
		if tagline_org == None:
			tagline_org=''
		if thumb == None:
			thumb=''		
		PLog(title);PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=-1)  # Downloadbutton(s)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#-----------------------
# test_downloads: prüft ob curl/wget-Downloads freigeschaltet sind + erstellt den Downloadbutton
# high (int): Index für einzelne + höchste Video-Qualität in download_list
def test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high):  # Downloadbuttons (ARD + ZDF)
	PLog('test_downloads:')
	PLog('test_downloads: ' + summary_org)
	PLog('test_downloads: ' + title_org)
	PLog('tagline_org: ' + tagline_org)

	PLog(SETTINGS.getSetting('pref_use_downloads')) 	# Voreinstellung: False 
	if SETTINGS.getSetting('pref_use_downloads') == 'true' and SETTINGS.getSetting('pref_curl_path'):
		dest_path = SETTINGS.getSetting('pref_curl_download_path')
		if  os.path.isdir(dest_path) == False:
			msg1	= 'test_downloads'
			msg2 	= 'Downloadverzeichnis existiert nicht:'
			msg3 	= dest_path
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li				
		# PLog(SETTINGS.getSetting('pref_show_qualities'))
		if SETTINGS.getSetting('pref_show_qualities') == 'false':	# nur 1 (höchste) Qualität verwenden
			download_items = []
			download_items.append(download_list.pop(high))									 
		else:	
			download_items = download_list						# ganze Liste verwenden
		PLog(download_items)
		
		i=0
		for item in download_items:
			quality,url = item.split('#')
			PLog(url); PLog(quality); PLog(title_org)
			if url.find('.m3u8') == -1 and url.find('rtmp://') == -1:
				# detailtxt =  Begleitdatei mit Textinfos zum Video / Podcast:
				title_org = UtfToStr(title_org)
				summary_org = UtfToStr(summary_org)
				tagline_org = UtfToStr(tagline_org)
				thumb = UtfToStr(thumb)
				quality = UtfToStr(quality)
				url = UtfToStr(url)
				
				detailtxt = MakeDetailText(title=title_org,thumb=thumb,quality=quality,
					summary=summary_org,tagline=tagline_org,url=url)
				v = 'detailtxt'+str(i)
				vars()[v] = detailtxt
				Dict('store', v, vars()[v])		# detailtxt speichern 
				if url.endswith('.mp3'):
					Format = 'Podcast ' 			
				else:	
					Format = 'Video '			# .mp4 oder .webm  (ARD nur .mp4)
				lable = 'Download %s | %s' % (Format, quality)
				dest_path = SETTINGS.getSetting('pref_curl_download_path')
				tagline = Format + 'wird in ' + dest_path + ' gespeichert' 									
				summary = 'Sendung: %s' % title_org
				key_detailtxt='detailtxt'+str(i)
				fparams="&fparams={'url': '%s', 'title': '%s', 'dest_path': '%s', 'key_detailtxt': '%s'}" % \
					(urllib2.quote(url), urllib2.quote(title_org), dest_path, key_detailtxt)
				addDir(li=li, label=lable, action="dirList", dirID="DownloadExtern", fanart=R(ICON_DOWNL), 
					thumb=R(ICON_DOWNL), fparams=fparams, summary=summary, tagline=tagline, mediatype='')
				i=i+1					# Dict-key-Zähler
	
	return li
	
#-----------------------
def MakeDetailText(title, summary,tagline,quality,thumb,url):	# Textdatei für Download-Video / -Podcast
	PLog('MakeDetailText:')

	detailtxt = ''
	detailtxt = detailtxt + "%15s" % 'Titel: ' + "'"  + title + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Beschreibung1: ' + "'" + tagline + "'" + '\r\n' 
	if summary != tagline: 
		detailtxt = detailtxt + "%15s" % 'Beschreibung2: ' + "'" + summary + "'"  + '\r\n' 	
	
	detailtxt = detailtxt + "%15s" % 'Qualitaet: ' + "'" + quality + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Bildquelle: ' + "'" + thumb + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Adresse: ' + "'" + url + "'"  + '\r\n' 
	
	return detailtxt
	
####################################################################################################
# Verwendung von curl/wget mittels Phytons subprocess-Funktionen
# 30.08.2018:
# Zum Problemen "autom. Wiedereintritt" - auch bei PHT siehe Doku in LiveRecord.
# 20.12.2018 Problem "autom. Wiedereintritt" in Kodi nicht relevant.

def DownloadExtern(url, title, dest_path, key_detailtxt):  # Download mittels curl/wget
	PLog('DownloadExtern: ' + title)
	PLog(url); PLog(dest_path); PLog(key_detailtxt)
	url=UtfToStr(url);title=UtfToStr(title);dest_path=UtfToStr(dest_path);
	key_detailtxt=UtfToStr(key_detailtxt);
	
	PIDcurl =  Dict("load", 'PIDcurl') # PMS-Version benötigte Check auf Wiedereintritt
	PLog('PIDcurl: %s' % str(PIDcurl))
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	
	if 	SETTINGS.getSetting('pref_generate_filenames') == 'true':	# Dateiname aus Titel generieren
		dfname = make_filenames(title) 
	else:												# Bsp.: Download_2016-12-18_09-15-00.mp4  oder ...mp3
		now = datetime.datetime.now()
		mydate = now.strftime("%Y-%m-%d_%H-%M-%S")	
		dfname = 'Download_' + mydate 
	
	if url.endswith('.mp3'):
		suffix = '.mp3'		
		dtyp = 'Podcast '
	else:												# .mp4 oder .webm	
		dtyp = 'Video '
		if url.endswith('.mp4'):				
			suffix = '.mp4'		
		if url.endswith('.webm'):				
			suffix = '.webm'		
		
	title = dtyp + 'curl/wget-Download: ' + title
	textfile = dfname + '.txt'
	dfname = dfname + suffix							# suffix: '.mp4', '.webm', oder '.mp3'
	
	pathtextfile = os.path.join(dest_path, textfile)	# kompl. Speicherpfad für Textfile
	PLog(pathtextfile)
	detailtxt = Dict("load", key_detailtxt)				# detailtxt0, detailtxt1, ..
	detailtxt = UtfToStr(detailtxt)	
	PLog(detailtxt[:60])
	
	storetxt = 'Details zum ' + dtyp +  dfname + ':\r\n\r\n' + str(detailtxt)	
			
	PLog(sys.platform)
	try:
		PIDcurl = ''
		RSave(pathtextfile, storetxt)			# Text speichern
		
		AppPath = SETTINGS.getSetting('pref_curl_path')
		i = os.path.exists(AppPath)					# Existenz curl/wget prüfen
		PLog(AppPath); PLog(i)
		if AppPath == '' or i == False:
			msg1='Pfad zu curl/wget fehlt oder curl/wget nicht gefunden'
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return li
			
		# i = os.access(curl_dest_path, os.W_OK)		# Zielverz. prüfen - nicht relevant für curl/wget
														# 	Anwender muss Schreibrecht sicherstellen
		curl_fullpath = os.path.join(dest_path, dfname)	# kompl. Speicherpfad für Video/Podcast
		PLog(curl_fullpath)

		# 08.06.2017 wget-Alternative wg. curl-Problem auf Debian-System (Forum: 
		#	https://forums.plex.tv/discussion/comment/1454827/#Comment_1454827
		# 25.06.2018 Parameter -k (keine Zertifikateprüfung) erforderlich wg. curl-Problem
		#	mit dem Systemzertifikat auf manchen Systemen.
		# wartet nicht (ohne p.communicate())
		# 11.12.2018  Parameter -L follow redirects
		# Debug curl: --trace file anhängen. 
		#
		# http://stackoverflow.com/questions/3516007/run-process-and-dont-wait
		#	creationflags=DETACHED_PROCESS nur unter Windows
		if AppPath.find('curl') > 0:									# curl-Call
			PLog('%s %s %s %s %s %s' % (AppPath, url, "-o", curl_fullpath, "-k", "-L"))	
			sp = subprocess.Popen([AppPath, url, "-o", curl_fullpath, "-k", "-L"])	
			# sp = subprocess.Popen([AppPath, url, "-N", "-o", curl_fullpath])	# Buffering für curl abgeschaltet
		else:															# wget-Call
			PLog('%s %s %s %s %s %s' % (AppPath, "--no-use-server-timestamps", "-q", "-O", curl_fullpath, url))	
			sp = subprocess.Popen([AppPath, "--no-check-certificate", "--no-use-server-timestamps", "-q", "-O", curl_fullpath, url])
			
		PLog('sp = ' + str(sp))
	
		if str(sp).find('object at') > 0:  				# subprocess.Popen object OK
			PIDcurl = sp.pid							# PID speichern
			PLog('PIDcurl neu: %s' % PIDcurl)
			Dict('store', 'PIDcurl', PIDcurl)
			msg1 = 'curl/wget: Download erfolgreich gestartet'
			msg2 = 'PID: %s | Zusatz-Infos in Textdatei gespeichert: %s' % 	(str(PIDcurl), textfile)		
			msg3 = 'Ablage: ' + curl_fullpath
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li			
			
		else:
			raise Exception('Start von curl/wget fehlgeschlagen')
			
	except Exception as exception:
		PLog(str(exception))		
		msg1 ='Download fehlgeschlagen'
		msg2 = str(exception)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li					
	
#---------------------------
# Tools: Einstellungen,  Bearbeiten, Verschieben, Löschen
def DownloadsTools():
	PLog('DownloadsTools:');

	path = SETTINGS.getSetting('pref_curl_download_path')
	PLog(path)
	dirlist = []
	if os.path.isdir(path) == False:
		msg1='Hinweis:'
		if path == '':		
			msg2='Downloadverzeichnis noch nicht festgelegt.'
		else:
			msg2='Downloadverzeichnis nicht gefunden: '
		msg3=path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
	else:
		dirlist = os.listdir(path)						# Größe Inhalt? 		
			
	PLog(len(dirlist))
	mpcnt=0; vidsize=0
	for entry in dirlist:
		if entry.find('.mp4') > 0 or entry.find('.webm') > 0 or entry.find('.mp3') > 0:
			mpcnt = mpcnt + 1	
			fname = os.path.join(path, entry)					
			vidsize = vidsize + os.path.getsize(fname) 
	vidsize	= vidsize / 1000000
	title1 = 'Downloadverzeichnis: %s Download(s), %s MBytes' % (mpcnt, str(vidsize))
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)								# Home-Button
	
	path = SETTINGS.getSetting('pref_curl_path')			# Einstellungen: Pfad curl/wget
	title = 'Pfad zum Downloadprogramm curl/wget festlegen/aendern (%s)' % path
	tagline = 'Hier wird der Pfad zum Downloadprogramm curl/wget eingestellt.'
	fparams="&fparams={'settingKey': 'pref_curl_path', 'mytype': '1', 'heading': '%s', 'path': '%s'}" % (title, path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_CURLWGET), fparams=fparams, tagline=tagline)

	dlpath =  SETTINGS.getSetting('pref_curl_download_path')# Einstellungen: Pfad Downloaderz.
	title = 'Downloadverzeichnis festlegen/aendern: (%s)' % dlpath			
	tagline = 'Das Downloadverzeichnis muss für den Addon-Nutzer beschreibbar sein.'
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_curl_download_path', 'mytype': '0', 'heading': '%s', 'path': '%s'}" % (title, dlpath)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DOWNL_DIR), fparams=fparams, tagline=tagline)

	PLog(SETTINGS.getSetting('pref_VideoDest_path'))
	movie_path = SETTINGS.getSetting('pref_VideoDest_path')
	if SETTINGS.getSetting('pref_VideoDest_path') == '':# Vorgabe Medienverzeichnis (Movieverz), falls leer	
		pass
		# movie_path = xbmc.translatePath('library://video/')
		# PLog(movie_path)
				
	if os.path.isdir(movie_path)	== False:			# Sicherung gegen Fehleinträge
		movie_path = ''									# wird ROOT_DIRECTORY in DirectoryNavigator
	PLog(movie_path)	
	title = 'Zielverzeichnis zum Verschieben festlegen/aendern (%s)' % (movie_path)	
	tagline = 'Zum Beispiel das Medienverzeichnis.'
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_VideoDest_path', 'mytype': '0', 'heading': '%s', 'path': '%s'}" % (title, movie_path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_MOVEDIR_DIR), fparams=fparams, tagline=tagline)

	PLog(SETTINGS.getSetting('pref_podcast_favorits'))					# Pfad zur persoenlichen Podcast-Favoritenliste
	path =  SETTINGS.getSetting('pref_podcast_favorits')							
	title = 'Persoenliche Podcast-Favoritenliste festlegen/aendern (%s)' % path			
	tagline = 'Format siehe podcast-favorits.txt (Ressourcenverzeichnis)'
	# summary =    # s.o.
	fparams="&fparams={'settingKey': 'pref_podcast_favorits', 'mytype': '1', 'heading': '%s', 'path': '%s'}" % (title, path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_FAVORITS), fparams=fparams, tagline=tagline)
		
	if mpcnt > 0:																# Videos / Podcasts?
		title = 'Downloads bearbeiten: %s Download(s)' % (mpcnt)				# Button Bearbeiten
		summary = 'Downloads im Downloadverzeichnis ansehen, loeschen, verschieben'
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="DownloadsList", fanart=R(ICON_DOWNL_DIR), 
			thumb=R(ICON_DIR_WORK), fparams=fparams, summary=summary)

		if dirlist:
			dest_path = SETTINGS.getSetting('pref_curl_download_path') 
			if path and movie_path:												# Button Verschieben (alle)
				title = 'ohne Rückfrage! alle (%s) Downloads verschieben' % (mpcnt)	
				tagline = 'Verschieben erfolgt ohne Rueckfrage!' 
				summary = 'alle Downloads verschieben nach: %s'  % (movie_path)
				fparams="&fparams={'dfname': '', 'textname': '', 'dlpath': '%s', 'destpath': '%s', 'single': 'False'}" \
					% (dest_path, movie_path)
				addDir(li=li, label=title, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DOWNL_DIR), 
					thumb=R(ICON_DIR_MOVE_ALL), fparams=fparams, summary=summary, tagline=tagline)
			
			title = 'ohne Rückfrage! alle (%s) Downloads löschen' % (mpcnt)			# Button Leeren (alle)
			tagline = 'Löschen erfolgt ohne Rückfrage!'						
			summary = 'alle Dateien aus dem Downloadverzeichnis entfernen'
			fparams="&fparams={'dlpath': '%s', 'single': 'False'}" % dlpath
			addDir(li=li, label=title, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DOWNL_DIR), 
				thumb=R(ICON_DELETE), fparams=fparams, summary=summary, tagline=tagline)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#---------------------------
# Downloads im Downloadverzeichnis zur Bearbeitung listen	 	
def DownloadsList():			
	PLog('DownloadsList:')	
	path = SETTINGS.getSetting('pref_curl_download_path')
	
	dirlist = []
	if path == None or path == '':									# Existenz Verz. prüfen, falls vorbelegt
		msg1 = 'Downloadverzeichnis noch nicht festgelegt'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return
	else:
		if os.path.isdir(path)	== False:			
			msg1 =  'Downloadverzeichnis nicht gefunden: ' 
			msg2 =  path
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
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
	vidsize	= vidsize / 1000000
	title1 = 'Downloadverzeichnis: %s Download(s), %s MBytes' % (mpcnt, str(vidsize))
	
	if mpcnt == 0:
		msg1 = 'Kein Download vorhanden | Pfad:' 
		msg2 = dlpath
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
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
			if txt != None:			
				title = stringextract("Titel: '", "'", txt)
				tagline = stringextract("ung1: '", "'", txt)
				summary = stringextract("ung2: '", "'", txt)
				quality = stringextract("taet: '", "'", txt)
				thumb = stringextract("Bildquelle: '", "'", txt)
				httpurl = stringextract("Adresse: '", "'", txt)
				
				if tagline and quality:
#					tagline = "%s\n\n%s" % (tagline, quality)
					tagline = "%s | %s" % (tagline, quality)

			else:										# ohne Beschreibung
				# pass									# Plex brauchte hier die Web-Url	aus der Beschreibung
				title = fname
				httpurl = fname							# Berücksichtigung in VideoTools - nicht abspielbar
				summary = 'Download / Aufnahme ohne Beschreibung'
				#tagline = 'Beschreibung fehlt - Beschreibung gelöscht, Sammeldownload oder TVLive-Video'
				
			PLog(httpurl); PLog(tagline); PLog(quality); # PLog(txt); 			
			if httpurl.endswith('mp3'):
				oc_title = 'Bearbeiten: Podcast | ' + title
				thumb = R(ICON_NOTE)
			else:
				oc_title='Bearbeiten: ' + title
				if thumb == '':							# nicht in Beschreibung
					thumb = R(ICON_DIR_VIDEO)

			oc_title = UtfToStr(oc_title); summary = UtfToStr(summary); tagline = UtfToStr(tagline);
			fparams="&fparams={'httpurl': '%s', 'path': '%s', 'dlpath': '%s', 'txtpath': '%s', 'title': '%s','summary': '%s', \
				'thumb': '%s', 'tagline': '%s'}" % (urllib2.quote(httpurl), urllib2.quote(localpath), urllib2.quote(dlpath), 
				txtpath, urllib2.quote(title), urllib2.quote(summary), urllib2.quote(thumb), urllib2.quote(tagline))
			addDir(li=li, label=oc_title, action="dirList", dirID="VideoTools", fanart=thumb, 
				thumb=thumb, fparams=fparams, summary=summary, tagline=tagline)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#---------------------------
# Downloads im Downloadverzeichnis ansehen, löschen, verschieben
#	zum  Ansehen muss das Video  erneut angefordert werden - CreateVideoClipObject verweigert die Wiedergabe
#		lokaler Videos: networking.py line 224, in load ... 'file' object has no attribute '_sock'
#	httpurl=HTTP-Videoquelle, path=Videodatei (Name), dlpath=Downloadverz., txtpath=Textfile (kompl. Pfad)
#	
def VideoTools(httpurl,path,dlpath,txtpath,title,summary,thumb,tagline):
	PLog('VideoTools: ' + path)
	path = UtfToStr(path); dlpath = UtfToStr(dlpath); txtpath = UtfToStr(txtpath); title = UtfToStr(title);
	summary = UtfToStr(summary); thumb = UtfToStr(thumb); tagline = UtfToStr(tagline);

	title_org = title
	title = UtfToStr(title)
	
	sub_path=''# fehlt noch bei ARD
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	dest_path = SETTINGS.getSetting('pref_curl_download_path')
	fulldest_path = os.path.join(dest_path, path)
	if  os.access(dest_path, os.R_OK) == False:
		msg1 = 'Downloadverzeichnis oder Leserecht  fehlt'
		msg2 = dest_path
		PLog(msg1); PLog(msg2)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	
	if os.path.exists(fulldest_path) == False:	# inzw. gelöscht?
		msg1 = 'Datei nicht vorhanden:'
		msg2 = fulldest_path
		PLog(msg1); PLog(msg2)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
		

	if fulldest_path.endswith('mp4') or fulldest_path.endswith('webm'):# 1. Ansehen
		title = title_org 
		lable = "Ansehen | %s" % (title_org)
		fulldest_path = UtfToStr(fulldest_path)		
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(urllib.quote_plus(fulldest_path), urllib.quote_plus(title), urllib.quote_plus(thumb), 
			urllib.quote_plus(summary), urllib.quote_plus(sub_path))
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams,
			mediatype='video')
		
	else:										# 'mp3' = Podcast
		if fulldest_path.endswith('mp3'):		# Dateiname bei fehl. Beschreibung, z.B. Sammeldownloads
			title = title_org 											# 1. Anhören
			lable = "Anhören | %s" % (title_org)
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib2.quote(fulldest_path), 
				title, urllib2.quote(thumb), urllib.quote_plus(summary))
			addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, 
				fparams=fparams, mediatype='music') 
	
	lable = "Loeschen ohne Rückfrage | %s" % title_org 					# 2. Löschen
	tagline = 'Datei: ' + path 
	fparams="&fparams={'dlpath': '%s', 'single': 'True'}" % urllib2.quote(fulldest_path)
	addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
		thumb=R(ICON_DELETE), fparams=fparams, summary=summary, tagline=tagline)
	
	if SETTINGS.getSetting('pref_VideoDest_path'):	# 3. Verschieben nur mit Zielpfad, einzeln
		VideoDest_path = SETTINGS.getSetting('pref_VideoDest_path')
		textname = os.path.basename(txtpath)
		lable = "Verschieben | %s" % title_org									
		summary = "Ziel: %s" % VideoDest_path
		tagline = 'Das Zielverzeichnis kann im Menü Download-Tools geaendert werden'
		fparams="&fparams={'dfname': '%s', 'textname': '%s', 'dlpath': '%s', 'destpath': '%s', 'single': 'True'}" \
			% (urllib2.quote(path), urllib2.quote(textname), urllib2.quote(dlpath), urllib2.quote(VideoDest_path))
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DIR_MOVE_SINGLE), 
			thumb=R(ICON_DIR_MOVE_SINGLE), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#---------------------------
# Downloadverzeichnis leeren (einzeln/komplett)
def DownloadsDelete(dlpath, single):
	dlpath = UtfToStr(dlpath)
	PLog('DownloadsDelete: ' + dlpath)
	PLog('single=' + single)

	li = xbmcgui.ListItem()
	
	try:
		if single == 'False':
			for i in os.listdir(dlpath):		# Verz. leeren
				fullpath = os.path.join(dlpath, i)
				os.remove(fullpath)
			error_txt = 'Downloadverzeichnis geleert'
		else:
			txturl = os.path.splitext(dlpath)[0]  + '.txt' 
			if os.path.isfile(dlpath) == True:							
				os.remove(dlpath)				# Video löschen
			if os.path.isfile(txturl) == True:							
				os.remove(txturl)				# Textdatei löschen
			error_txt = 'Datei gelöscht: ' + dlpath
		PLog(error_txt)			 			 	 
		msg1 = 'Löschen erfolgreich'
		msg2 = error_txt
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
	except Exception as exception:
		PLog(str(exception))
		msg1 = 'Fehler | Löschen fehlgeschlagen'
		msg2 = str(exception)
		return li

#---------------------------
# dfname=Videodatei, textname=Textfile,  dlpath=Downloadverz., destpath=Zielverz.
#
def DownloadsMove(dfname, textname, dlpath, destpath, single):
	PLog('DownloadsMove: ');PLog(dfname);PLog(textname);PLog(dlpath);PLog(destpath);
	PLog('single=' + single)
	dfname=UtfToStr(dfname);textname=UtfToStr(textname);dlpath=UtfToStr(dlpath);
	destpath=UtfToStr(destpath);

	li = xbmcgui.ListItem()

	if  os.access(destpath, os.W_OK) == False:
		msg1 = 'Download fehlgeschlagen'
		msg2 = 'Kein Schreibrecht im Zielverzeichnis'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	

	try:
		cnt = 0
		if single == 'False':				# kompl. Verzeichnis
			for i in os.listdir(dlpath):
				src = os.path.join(dlpath, i)
				dest = os.path.join(destpath, i)							
				PLog(src); PLog(dest); 
				
				if os.path.isfile(src) == True:							
					shutil.copy(src, destpath)	# Datei kopieren	
					os.remove(src)				# Datei löschen
					cnt = cnt + 1
			error_txt = '%s Dateien verschoben nach: %s' % (cnt, destpath)		 			 	 
		else:
			textsrc = os.path.join(dlpath, textname)
			textdest = os.path.join(destpath, textname)	
			videosrc = os.path.join(dlpath, dfname)
			videodest = os.path.join(destpath, dfname)		
			PLog(videosrc); PLog(videodest);
					
			if os.path.isfile(textsrc) == True:	# Quelldatei testen						
				shutil.copy(textsrc, textdest)		
				os.remove(textsrc)				# Textdatei löschen
			if os.path.isfile(videosrc) == True:							
				shutil.copy(videosrc, videodest)				
				os.remove(videosrc)				# Videodatei dto.
			error_txt = 'Video + Textdatei verschoben: ' + 	dfname				 			 	 
		PLog(error_txt)			 			 	 		
		msg1 = 'Verschieben erfolgreich'
		msg2 = error_txt
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li

	except Exception as exception:
		PLog(str(exception))
		msg1 = 'Verschieben fehlgeschlagen'
		msg2 = str(exception)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
		
####################################################################################################
# Aufruf Main, Favoriten oder Merkliste anzeigen + auswählen
# mode = 'Favs' für Favoriten  oder 'Merk' für Merkliste
# 	Datenbasen (Einlesen in ReadFavourites (Modul util) :
#		Favoriten: special://profile/favourites.xml 
#		Merkliste: ADDON_DATA/merkliste.xml (WATCHFILE)
# 	Verarbeitung:
#		Favoriten: Kodi's Favoriten-Menü, im Addon_listing
#		Merkliste: zusätzl. Kontextmenmü (s. addDir Modul util) -> Watch
#	
#	Probleme:  	Kodi's Fav-Funktion übernimmt nicht summary, tagline, mediatype aus addDir-Call
#				Keine Begleitinfos, falls  summary, tagline od. Plot im addDir-Call fehlen.
#				gelöst mit Base64-kodierter Plugin-Url: 
#					Sonderzeichen nach doppelter utf-8-Kodierung
#
def ShowFavs(mode):							# Favoriten / Merkliste einblenden
	PLog('ShowFavs: ' + mode)				# 'Favs', 'Merk'
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)									# Home-Button
															
	my_items = ReadFavourites(mode)						# Addon-Favs / Merkliste einlesen
	PLog(len(my_items))
	CallFunctions = ["PlayVideo", "ZDF_getVideoSources", "resources.lib.zdfmobile.ShowVideo",
						"resources.lib.zdfmobile.PlayVideo", "SingleSendung", "ARDStartVideoStreams", 
						"ARDStartVideoMP4", ]	# ohne "SenderLiveResolution" (Resume aus)	

	if mode == 'Favs':														
		tagline = "Anzahl Addon-Favoriten: %s" % str(len(my_items)) 	# Info-Button
		s1 		= "Hier werden die ARDundZDF-Favoriten aus Kodi's Favoriten-Menü eingeblendet."
		s2		= "Favoriten entfernen: im Kodi's Favoriten-Menü oder am Ursprungsort im Addon (nicht hier!)."
		s3		= 'Favoriten enthalten nicht in allen Fällen Begleitinfos zu Inhalt, Länge usw.'
		summary	= "%s\n\n%s\n\n%s"		% (s1, s2, s3)
		label	= 'Infos zum Menü Favoriten'
	else:
		tagline = "Anzahl Merklisteneinträge: %s" % str(len(my_items)) 	# Info-Button
		s1 		= "Merkliste von ARDundZDF."
		s2		= "Einträge entfernen: via Kontextmenü hier oder am am Ursprungsort im Addon."
		s3		= "Die Merkliste wird nach hinzufügen/entfernen erneut aufgerufen."
		s4		= 'Einträge enthalten nicht in allen Fällen Begleitinfos zu Inhalt, Länge usw.'
		summary	= "%s\n\n%s\n\n%s"		% (s1, s2, s3)
		label	= 'Infos zum Menü Merkliste'
	
	fparams="&fparams={'mode': '%s'}"	% mode						# Info-Menü
	addDir(li=li, label=label, action="dirList", dirID="ShowFavs", 
		fanart=R(ICON_DIR_FAVORITS), thumb=R(ICON_INFO), fparams=fparams,
		summary=summary, tagline=tagline, cmenu=False) 	# ohne Kontextmenü)	
	
	for fav in my_items:
		fav = urllib.unquote_plus(fav)						# urllib2.unquote erzeugt + aus Blanks! 
		fav_org = fav										# für ShowFavsExec
		#PLog('fav_org: ' + fav_org)
		name=''; thumb=''; dirPars=''; fparams='';			
		name 	= re.search(' name="(.*?)"', fav) 			# name, thumb,Plot zuerst
		thumb 	= stringextract(' thumb="', '"',fav) 
		Plot_org = stringextract(' Plot="', '"',fav) 		# ilabels['Plot']
		Plot_org = Plot_org.replace(' Plot="', ' Plot=""')  # leer
		if name: 	name 	= name.group(1)
			
		if mode == 'Merk' and 'plugin://plugin' not in fav:	# Base64-kodierte Plugin-Url
			PLog('base64_fav')
			fav = fav.replace('10025,&quot;', '10025,"')	# Quotierung Anfang entfernen
			fav = fav.replace('&quot;,return', '",return')	# Quotierung Ende entfernen					
			p1, p2 	= fav.split('",return)</merk>')	# Endstück p2: &quot;,return)</merk>
			#PLog('p1: ' + p1)							
			#PLog('p2: ' + p2)
			p3, b64	=  p1.split('10025,"')					# p1=Startstück, b64=kodierter string
			#PLog('p3: ' + p3)
			#PLog('b64: ' + b64)
			b64_clean= convBase64(b64)						# Dekodierung mit oder ohne padding am Ende
			if b64_clean == False:							# skip fav
				msg1 = "Problem bei Base64-Dekodierung. Eintrag  nicht verwertbar."
				msg2 = "Eintrag: %s" % name
				xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, "") 
				continue
				
			b64_clean=urllib.unquote_plus(b64_clean)		# unquote aus addDir-Call
			b64_clean=urllib.unquote_plus(b64_clean)		# unquote aus Kontextmenü
			#PLog(b64_clean)
			fav		= p3 + '10025,"' + b64_clean + p2 

		fav = fav.replace('&quot;', '"')					# " am Ende fparams
		fav = fav.replace('&amp;', '&')						# Verbinder &
		PLog('fav_b64_clean: ' + fav)
		dirPars	= re.search('action=(.*?)&fparams',fav)		# dirList&dirID=PlayAudio&fanart..
		fparams = stringextract('&fparams={', '}',fav)
		fparams = urllib.unquote_plus(fparams)				# Parameter sind zusätl. quotiert
		PLog('fparams1: ' + fparams);
		
		try:
			dirPars = dirPars.group(1)
		except:
			dirPars = ''
		PLog('dirPars: ' + dirPars);
		mediatype=''										# Kennz. Videos im Listing
		CallFunction = stringextract("&dirID=", "&", dirPars) 
		PLog('CallFunction: ' + CallFunction)
		if CallFunction in CallFunctions:			# Parameter Merk='true' anhängen
			mediatype='video'
		
		dirPars = unescape(dirPars); 
		PLog(name); PLog(thumb); PLog(Plot_org); PLog(dirPars);  PLog(mediatype);
		PLog('fparams2: ' + fparams);
			
		# Begleitinfos aus fparams holen - Achtung Quotes!		# 2. fparams auswerten
		fpar_tag = stringextract("tagline': '", "'", fparams) 
		fpar_summ = stringextract("summ': '", "'", fparams)
		if fpar_summ == '':
			fpar_summ = stringextract("summary': '", "'", fparams)
		fpar_plot= stringextract("Plot': '", "'", fparams) 
		fpar_path= stringextract("path': '", "'", fparams) # PodFavoriten
		
		action=''; dirID=''; summary=''; tagline=''; Plot=''
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
		if summary == '':								# Begleitinfos aus fparams verwenden
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
						
		summary = urllib.unquote_plus(summary); tagline = urllib.unquote_plus(tagline); 
		Plot = urllib.unquote_plus(Plot)
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
		if mode == 'Favs':									# bereits quotiert
			fparams ="&fparams={%s}" % fparams	
		else:
			fparams ="&fparams={%s}" % urllib.quote_plus(fparams)			
		PLog('fparams3: ' + fparams)
		if mode == 'Favs':
			fanart = R(ICON_DIR_FAVORITS)
		else:
			fanart = R(ICON_DIR_WATCH)														
		
		summary = summary.replace('||', '\n')		# wie Plot	
		tagline = tagline.replace('||', '\n')
		
		addDir(li=li, label=name, action=action, dirID=dirID, fanart=fanart, thumb=thumb,
			summary=summary, tagline=tagline, fparams=fparams,mediatype=mediatype)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-------------------------------------------------------
# convBase64 dekodiert base64-String für ShowFavs bzw. gibt False zurück
#	Base64 füllt den String mittels padding am Ende (=) auf ein Mehrfaches von 4 auf.
# aus https://stackoverflow.com/questions/12315398/verify-is-a-string-is-encoded-in-base64-python	
def convBase64(s):
	PLog('convBase64:')
	try:
		if len(s.strip()) % 4 == 0:
			return base64.decodestring(s)
	except Exception:
		pass
	return False
			
####################################################################################################
# Addon-interne Merkliste : Hinzufügen / Löschen
#	unabhängig von der Favoritenverwaltung
#	base64-Kodierung benötigt für url-Parameter (nötig für router)
# 23.03.2019 zusätzliche base64- zu urllib-Kodierung (in Kombi ohne padding-Error) - s. addDir
# Ungelöstes Problem:
#	bisher kein Verbleib im akt. Verz. möglich (wie bei Favoriten). Nach add oder del wird Watch 
#	wiederholt aufgerufen - Lösung: Aufruf von ShowFavs.
#
def Watch(action, name, thumb='', Plot='', url=''):		
	PLog('Watch: ' + action)
	# CallFunctions: Funktionen, die Videos direkt oder indirekt (isPlayable) aufrufen.
	#	Ist eine der Funktionen in der Plugin-Url enthalten, wird der Parameter Merk='true'
	#	für PlayVideo bzw. zum Durchreichen angehängt
	CallFunctions = ["PlayVideo", "ZDF_getVideoSources", "resources.lib.zdfmobile.ShowVideo",
						"resources.lib.zdfmobile.PlayVideo", "SingleSendung", "ARDStartVideoStreams", 
						"ARDStartVideoMP4", "SenderLiveResolution"
					]
	
	url = urllib.unquote_plus(url)	
	PLog(urllib.unquote_plus(url)[100:])  			# url in fparams zusätzlich quotiert
	PLog(name); PLog(thumb); PLog(Plot);
	
	name = UtfToStr(name); thumb = UtfToStr(thumb); 
	Plot = UtfToStr(Plot); 
	url = UtfToStr(url)	

	fname = WATCHFILE		
	item_cnt = 0; 
	err_msg	= ''
	doppler = False
	
	if action == 'add':
		if 'plugin://plugin' not in url:				# Base64-kodierte Plugin-Url in ActivateWindow
			b64_clean= convBase64(url)					# Dekodierung mit oder ohne padding am Ende	
			b64_clean=urllib.unquote_plus(b64_clean)	# unquote aus addDir-Call
			b64_clean=urllib.unquote_plus(b64_clean)	# unquote aus Kontextmenü
			#PLog(b64_clean)
			CallFunction = stringextract("&dirID=", "&", b64_clean) 
			PLog('CallFunction: ' + CallFunction)
			if CallFunction in CallFunctions:			# Parameter Merk='true' anhängen
				new_url = b64_clean[:-1]				# cut } am Ende fparams
				new_url = "%s, 'Merk': 'true'}" % new_url
				PLog("CallFunction_new_url: " + new_url)
				url = urllib.quote_plus(new_url)
				url = base64.b64encode(url)			
			
		url = url.replace('&', '&amp;') # Anpassung an Favorit-Schema
		merk = '<merk name="%s" thumb="%s" Plot="%s">ActivateWindow(10025,&quot;%s&quot;,return)</merk>'  \
			% (name, thumb, Plot, url)
		PLog('merk: ' + merk)
		my_items = ReadFavourites('Merk')
		merkliste = ''
		for item in my_items:						# Liste -> String
			item = UtfToStr(item)	
			iname = stringextract('name="', '"', item) 
			# PLog('iname:' + iname)
			if iname == name:						# Doppler vermeiden
				doppler = True
				PLog('Doppler')
				break
			merkliste = merkliste + item + "\n"
			item_cnt = item_cnt + 1
		if doppler == False:
			msg1 = "Eintrag >%s< hinzugefügt" % name
			merkliste = merkliste + merk + "\n"
			item_cnt = item_cnt + 1			
			merkliste = "<merkliste>\n%s</merkliste>"	% merkliste
			err_msg = RSave(fname, merkliste)		# Merkliste speichern
			
		
	if action == 'del':
		my_items = ReadFavourites('Merk')
		merkliste = ''
		deleted = False
		for item in my_items:						# Liste -> String
			item = UtfToStr(item)	
			iname = stringextract('name="', '"', item) 
			# PLog('Name: %s, IName: %s' % (name, iname))
			if iname == name:						# skip Satz = löschen 
				deleted = True
				continue
			item_cnt = item_cnt + 1
			merkliste = merkliste + item + "\n"
		if deleted:
			PLog("Eintrag >%s< gelöscht" % name)
			err_msg = RSave(fname, merkliste)		# Merkliste speichern
		else:
			msg1 = "Eintrag >%s< nicht gefunden." % name
			PLog(msg1)
			# xbmcgui.Dialog().ok(ADDON_NAME, msg1, "", "") # ohne Info - stört bei Rücksprung hierher
							
	if err_msg:										# Info nur bei Save-Problem
		msg2 = 'Problem beim Speichern der Merkliste:'
		msg3 = err_msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3) 
	else:											# Liste wird anschl. geöffnet
		PLog("Anzahl der Einträge: %s" % str(item_cnt))		
	
	# Aufruf Merkliste - kein Verbleib im akt. Verz. möglich (s.o.)
	# Alternative: Sprung zum gewählten Verz. mittels getattr-Verfahren
	#	(s. func_pars_router-Call.txt)
	ShowFavs('Merk')
	xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=True, cacheToDisc=False)
				
####################################################################################################
# extrahiert aus Mediendatei (json) .mp3-, .mp4-, rtmp-Links + Untertitel (Aufrufer 
# 	SingleSendung). Bsp.: http://www.ardmediathek.de/play/media/35771780
# Untertitel in ARD-Neu gefunden siehe ARDStartSingle
def parseLinks_Mp4_Rtmp(page):		
	PLog('parseLinks_Mp4_Rtmp:')
	# PLog(page)	# Quellen im json-Format	
	
	if page.find('_previewImage') >= 0:
		#link_img = teilstring(page, 'http://www.ardmediathek.de/image', '\",\"_subtitleUrl')
		#link_img = stringextract('_previewImage\":\"', '\",\"_subtitle', page)
		link_img = stringextract('_previewImage\":\"', '\",', page) # ev. nur Mediatheksymbol
	else:
		link_img = ""

	link_path = []							# Liste nimmt Pfade und Quali.-Markierung auf
	m3u8_master = ''						# nimmt master.m3u8 zusätzlich auf	
	geoblock =  stringextract('_geoblocked":', '}', page)	# Geoblock-Markierung ARD
	sub_path = stringextract('_subtitleUrl":"', '"', page)
	
	if page.find('\"_quality\":') >= 0:
		s = page.split('\"_quality\":')	
		# PLog(s)							# nur bei Bedarf
		del s[0]							# 1. Teil entfernen - enthält img-Quelle (s.o.)
		
		for i in range(len(s)):
			s1 =  s[i]
			s2 = ''
			PLog(s1)						# Bsp.: 1,"_server":"","_cdn":"akamai","_stream":"http://avdlswr-..
				
			if s1.find('rtmp://') >= 0: # rtmp-Stream 
				PLog('s1: ' + s1)
				t1 = stringextract('server\":\"', '\",\"_cdn\"', s1) 
				t2 = stringextract( '\"_stream\":\"', '\"}', s1) 
				s2 = t1 + t2	# beide rtmp-Teile verbinden
				#PLog(s2)				# nur bei Bedarf
			else:						# http-Links, auch Links, die mit // beginnen
				s2 = stringextract('stream\":\"','\"', s1)
				if s2.startswith('//'):				# 12.09.2017: WDR-Links ohne http:
					s2 = 'http:' + s2
				if 'master.m3u8' in s1:
					m3u8_master = s2
			PLog(s2); PLog(len(s2))				
				
							
			if len(s2) > 9:						# schon url gefunden? Dann Markierung ermitteln
				if s1.find('auto') >= 0:
					mark = 'auto' + '|'					
				else:
					m = s1[0:1] 				# entweder Ziffern 0,1,2,3 
					mark = m + '|' 	
								
				link = mark + s2				# Qualität voranstellen			
				link_path.append(link)
				PLog(mark); PLog(s2); PLog(link); # PLog(link_path)
			
	link_path = list(set(link_path))			# Doppel entfernen (gesehen: 0, 1, 2 doppelt)
	link_path.sort()							# Sortierung - Original Bsp.: 0,1,2,0,1,2,3
	PLog(link_path); PLog(len(link_path)); PLog(sub_path)				
	return link_path, link_img, m3u8_master, geoblock, sub_path				 		
		
####################################################################################################
# Aufrufer SinglePage
def get_sendungen(li, sendungen, ID, mode): # Sendungen ausgeschnitten mit class='teaser', aus Verpasst + A-Z,
	# 										Suche, Einslike
	# Headline + subtitle sind nicht via xpath erreichbar, daher Stringsuche:
	# ohne linklist + subtitle weiter (teaser Seitenfang od. Verweis auf Serie, bei A-Z teaser-Satz fast identisch,
	#	nur linklist fehlt )
	# Die Rückgabe-Liste send_arr nimmt die Datensätze auf (path, headline usw.)
	# ab 02.04.2017: ID=PODCAST	- bei Sendereihen enthält der 1. Satz Bild + Teasertext
	PLog('get_sendungen:'); PLog(ID); PLog(mode); 

	img_src_header=''; img_alt_header=''; teasertext_header=''; teasertext=''
	if ID == 'PODCAST' and mode == 'Sendereihen':							# PODCAST: Bild + teasertext nur im Kopf vorhanden
		# PLog(sendungen[0])		# bei Bedarf
		if sendungen[0].find('urlScheme') >= 0:	# Bild ermitteln, versteckt im img-Knoten
			text = stringextract('urlScheme', '/noscript', sendungen[0])
			img_src_header, img_alt_header = img_urlScheme(text, 320, ID) # Format quadratisch bei Podcast
			teasertext_header = stringextract('<h4 class=\"teasertext\">', '</p>', sendungen[0])
		# del sendungen[0]						# Beiträge folgen dahinter - 11.01.2019: Beitrag hier möglich
			
	# send_arr nimmt die folgenden Listen auf (je 1 Datensatz pro Sendung)
	send_path = []; send_headline = []; send_subtitle = []; send_img_src = [];
	send_img_alt = []; send_millsec_duration = []; send_dachzeile = []; send_sid = []; 
	send_teasertext = []; 
	arr_ind = 0
	for s in sendungen:	
		# PLog('sendung: ' + s)	# bei Bedarf
		found_sendung = False
		if s.find('<div class="linklist">') == -1 or ID == 'PODCAST':  # PODCAST-Inhalte ohne linklistG::;
			if  s.find('subtitle') >= 0: 
				found_sendung = True
			if  s.find('dachzeile') >= 0: # subtitle in ARDThemen nicht vorhanden
				found_sendung = True
			if  s.find('<h4 class=\"headline\">') >= 0:  # in Rubriken weder subtitle noch dachzeile vorhanden
				found_sendung = True
				
		PLog(found_sendung)
		if found_sendung:				
			dachzeile = re.search("<p class=\"dachzeile\">(.*?)</p>\s+?", s)  # Bsp. <p class="dachzeile">Weltspiegel</p>
			if dachzeile:									# fehlt komplett bei ARD_SENDUNG_VERPASST
				dachzeile = dachzeile.group(1)
				dachzeile = dachzeile.replace('"', '*')		# "-Zeichen verhindert json.loads in router
			else:
				dachzeile = ''
				
			title = ''
			href = stringextract('<a href="', '"', s)	# Titel aus Ref-Link - Titel hier außerhalb des Blocks
			if href.startswith('/tv/'):					# Bsp. href="/tv/Morgenmagazin/Überzeugender-Start..
				title = href.split('/')[2]
				title = title.replace('-', ' ')

			headline = stringextract('<h4 class=\"headline\">', '</h4>', s)	
			# PLog("title: " + title); PLog("headline: " + headline)				
			headline = UtfToStr(headline)
			headline = unescape(headline)				# HTML-Escapezeichen  im Titel	
			headline=headline.replace('"', '*')			# "-Zeichen verhindert json.loads in router			
			if headline == '':
				continue
			if title:
				if 	(title.upper()==headline.upper()) == False : # gleich?
					headline = "%s | %s" % (title, headline)
		
			#if headline.find('- Hörfassung') >= 0:			# nicht unterdrücken - keine reine Hörfassung gesehen 
			#	continue
			if headline.find('Diese Seite benötigt') >= 0:	# Vorspann - irrelevant
				continue
			hupper = headline.upper()
			if hupper.find(str.upper('Livestream')) >= 0:			# Livestream hier unterdrücken (mehrfach in Rubriken)
				continue
			if s.find('subtitle') >= 0:	# nicht in ARDThemen
				subtitle = re.search("<p class=\"subtitle\">(.*?)</p>\s+?", s)	# Bsp. <p class="subtitle">25 Min.</p>
				if subtitle:
					subtitle = subtitle.group(1)
					subtitle = subtitle.replace('<br>', ' | ')				
					subtitle = UtfToStr(subtitle)
				else:
					subtitle = ""
			else:
				subtitle = ""
											
			subtitle = subtitle.replace('"', '*')			# "-Zeichen verhindert json.loads in router			
			subtitle = UtfToStr(subtitle)
			send_duration = subtitle						
			send_date = stringextract('class=\"date\">', '</span>', s) # auch Uhrzeit möglich
			PLog(subtitle)
			PLog(send_date)
			if send_date and subtitle:
				subtitle = send_date + ' Uhr | ' + subtitle				
				
			if send_duration.find('Min.') >= 0:			# Bsp. 20 Min. | UT
				send_duration = send_duration.split('Min.')[0]
				duration = send_duration.split('Min.')[0]
				PLog(duration)
				if duration.find('|') >= 0:			# Bsp. 17.03.2016 | 29 Min. | UT 
						duration = duration.split('|')[1]
				PLog(duration)
				millsec_duration = CalculateDuration(duration)
			else:
				millsec_duration = ''
			
			sid = ''
			if ID == 'PODCAST' and s.find('class=\"textWrapper\"') >= 0:	# PODCAST: textWrapper erst im 2. Durchlauf (Einzelseite)
				extr_path = stringextract('class=\"textWrapper\"', '</div>', s)
				id_path = stringextract('href=\"', '\"', extr_path)
			else:
				extr_path = stringextract('class=\"media mediaA\"', '/noscript', s)
				# PLog(extr_path)
				id_path = stringextract('href=\"', '\"', extr_path)
			id_path = UtfToStr(id_path)
			id_path = unescape(id_path)
			if id_path.find('documentId=') >= 0:		# documentId am Pfadende
				sid = id_path.split('documentId=')[1]	# ../Video-Podcast?bcastId=7262908&documentId=24666340
				
			PLog('sid: ' + sid)
			path = id_path	# korrigiert in SinglePage für Einzelsendungen in  '/play/media/' + sid
			PLog(path)
							
			if s.find('urlScheme') >= 0:			# Bild ermitteln, versteckt im img-Knoten
				text = stringextract('urlScheme', '/noscript', s)
				img_src, img_alt = img_urlScheme(text, 320, ID)
			else:
				img_src=''; img_alt=''	
			if ID == 'PODCAST' and img_src == '':		# PODCAST: Inhalte aus Episodenkopf verwenden
				if img_src_header and img_alt_header:
					img_src=img_src_header; img_alt=img_alt_header
				if teasertext_header:
					teasertext = teasertext_header
			 
			single_teasertext = stringextract('teasertext">', '</', s) 	# Priorität single_teasertext vor
			if single_teasertext:						# teasertext_header
				teasertext = single_teasertext
			teasertext = teasertext.replace('"', '*')	# "-Zeichen verhindert json.loads in router
						
			if path == '':								# Satz nicht verwendbar
					continue							
						
			PLog('neuer Satz')
			PLog(sid); PLog(id_path); PLog(path); PLog(img_src); PLog(img_alt); PLog(headline);  
			PLog(subtitle); PLog(send_duration); PLog(millsec_duration); 
			PLog(dachzeile); PLog(teasertext); 

			send_path.append(path)			# erst die Listen füllen
			send_headline.append(headline)
			send_subtitle.append(subtitle)
			send_img_src.append(img_src)
			send_img_alt.append(img_alt)
			send_millsec_duration.append(millsec_duration)
			send_dachzeile.append(dachzeile)		
			send_sid.append(sid)	
			send_teasertext.append(teasertext)	
			# break		# Debug 1 Satz					
											# dann der komplette Listen-Satz ins Array		
	send_arr = [send_path, send_headline, send_subtitle, send_img_src, send_img_alt, send_millsec_duration, 
		send_dachzeile, send_sid, send_teasertext]
	PLog(len(send_path))	 # Anzahl send_path = Anzahl Sätze		
	return send_arr
#-------------------
####################################################################################################
# LiveListe Vorauswahl - verwendet lokale Playlist
# 
def SenderLiveListePre(title, offset=0):	# Vorauswahl: Überregional, Regional, Privat
	title = urllib2.unquote(title)
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
		img = stringextract('<thumbnail>', '</thumbnail>', element) # channel-thumbnail in playlist
		if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		else:
			img = img
		PLog(name); PLog(img); # PLog(element);  # nur bei Bedarf
		
		fparams="&fparams={'title': '%s', 'listname': '%s', 'fanart': '%s'}" % (urllib2.quote(name), urllib2.quote(name), img)
		util.addDir(li=li, label=name, action="dirList", dirID="SenderLiveListe", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=img, fparams=fparams)

	title = 'EPG Alle JETZT'; summary='elektronischer Programmfuehrer'
	tagline = 'zeige die laufende Sendung für jeden Sender'
	fparams="&fparams={'title': '%s'}" % title
	util.addDir(li=li, label=title, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
		thumb=R('tv-EPG-all.png'), fparams=fparams, summary=summary, tagline=tagline)
							
	title = 'EPG Sender einzeln'; summary='elektronischer Programmfuehrer'
	tagline = 'Sendungen für Sender nach Wahl'								# EPG-Button Einzeln anhängen
	fparams="&fparams={'title': '%s'}" % title
	util.addDir(li=li, label=title, action="dirList", dirID="EPG_Sender", fanart=R(ICON_MAIN_TVLIVE), 
		thumb=R('tv-EPG-single.png'), fparams=fparams, summary=summary, tagline=tagline)	
		
	PLog(str(SETTINGS.getSetting('pref_LiveRecord')))
	if SETTINGS.getSetting('pref_LiveRecord'):		
		title = 'Recording TV-Live'													# TVLiveRecord-Button anhängen
		laenge = SETTINGS.getSetting('pref_LiveRecord_duration')
		if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
			laenge = "wird manuell eingegeben"
		summary = 'Sender wählen und aufnehmen.\nDauer: %s' % laenge
		tagline = 'Downloadpfad: %s' 	 % SETTINGS.getSetting('pref_curl_download_path') 				
		fparams="&fparams={'title': '%s'}" % title
		util.addDir(li=li, label=title, action="dirList", dirID="TVLiveRecordSender", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=R('icon-record.png'), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

	
#-----------------------------------------------------------------------------------------------------
# EPG SenderListe , EPG-Daten holen in Modul EPG.py, Anzeige in EPG_Show
def EPG_Sender(title):
	PLog('EPG_Sender:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	sort_playlist = get_sort_playlist()	
	# PLog(sort_playlist)
	
	for rec in sort_playlist:
		title = rec[0]
		title = UtfToStr(title)
		link = rec[3]
		ID = rec[1]
		if ID == '':				# ohne EPG_ID
			title = title + ': ohne EPG' 
			summ = 'weiter zum Livestream'
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': ''}" %\
				(urllib2.quote(link), urllib2.quote(title), urllib2.quote(R(rec[2])))
			addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
				thumb=R(rec[2]), fparams=fparams, summary=summ)
		else:
			summ = 'EPG verfuegbar'
			fparams="&fparams={'ID': '%s', 'name': '%s', 'stream_url': '%s', 'pagenr': %s}" % (ID, title, 
				urllib2.quote(link), '0')
			addDir(li=li, label=title, action="dirList", dirID="EPG_ShowSingle", fanart=R('tv-EPG-single.png'), thumb=R(rec[2]), 
				fparams=fparams, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------
#	Liste aller TV-Sender wie EPG_Sender, hier mit Aufnahme-Button
def TVLiveRecordSender(title):
	title = urllib2.unquote(title)
	PLog('TVLiveRecordSender')
	PLog(SETTINGS.getSetting('pref_LiveRecord_ffmpegCall'))
	# PLog('PID-Liste: %s' % Dict['PID'])		# PID-Liste, Initialisierung in Main
	
	# Test: Pfadanteil executable? 
	#	Bsp.: "/usr/bin/ffmpeg -re -i %s -c copy -t %s %s -nostdin"
	cmd = SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')	
	if cmd.strip() == '':
		msg1 = 'ffmpeg-Parameter fehlen in den Einstellungen!'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
	if os.path.exists(cmd.split()[0]) == False:
		msg1 = 'Pfad zu ffmpeg nicht gefunden.'
		msg2 = 'Bitte ffmpeg-Parameter in den Einstellungen prüfen, aktuell:'
		msg3 = 	SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)					# Home-Button
	
	duration = SETTINGS.getSetting('pref_LiveRecord_duration')
	duration, laenge = duration.split('=')
	duration = duration.strip()

	sort_playlist = get_sort_playlist()		# Senderliste
	PLog('Sender: ' + str(len(sort_playlist)))
	for rec in sort_playlist:
		title 	= rec[0]
		link 	= rec[3]
		title1 	= title + ': Aufnahme starten' 
		if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
			laenge = "wird manuell eingegeben"
		summ 	= 'Aufnahmedauer: %s' 	% laenge
		tag		= 'Zielverzeichnis: %s' % SETTINGS.getSetting('pref_curl_download_path')
		fparams="&fparams={'url': '%s', 'title': '%s', 'duration': '%s', 'laenge': '%s'}" \
			% (urllib2.quote(link), urllib2.quote(title), duration, laenge)
		addDir(li=li, label=title, action="dirList", dirID="LiveRecord", fanart=R(rec[2]), thumb=R(rec[2]), 
			fparams=fparams, summary=summ, tagline=tag)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#-----------------------------
# 30.08.2018 Start Recording TV-Live
#	Problem: autom. Wiedereintritt hier + erneuter Popen-call nach Rückkehr zu TVLiveRecordSender 
#		(Ergebnis-Button nach subprocess.Popen, bei PHT vor Ausführung des Buttons)
#		OS-übergreifender Abgleich der pid problematisch - siehe
#		https://stackoverflow.com/questions/4084322/killing-a-process-created-with-pythons-subprocess-popen
#		Der Wiedereintritt tritt sowohl unter Linux als auch Windows auf.
#		Ursach n.b. - tritt in DownloadExtern mit curl/wget nicht auf.
#	1. Lösung: Verwendung des psutil-Moduls (../Contents/Libraries/Shared/psutil ca. 400 KB)
#		und pid-Abgleich Dict['PID'] gegen psutil.pid_exists(pid) - s.u.
#		verworfen - Modul lässt sich unter Windows nicht laden. Linux OK
#	2. Lösung: Dict['PIDffmpeg'] wird nach subprocess.Popen belegt. Beim ungewollten Wiedereintritt
#		wird nach TVLiveRecordSender (Senderliste) zurück gesprungen und Dict['PIDffmpeg'] geleert.
#		Beim nächsten manuellen Aufruf wird LiveRecord wieder frei gegeben ("Türsteherfunktion").
#
#	PHT-Problem: wie in TuneIn2017 (streamripper-Aufruf) sprint PHT bereits vor dem Ergebnis-Buttons (DirectoryObject)
#		in LiveRecord zurück.
#		Lösung: Ersatz des Ergebnis-Buttons durch return ObjectContainer. PHT steigt allerdings danach mit 
#			"GetDirectory failed" aus (keine Abhilfe bisher). Der ungewollte Wiedereintritt findet trotzdem
#			statt.
#
# 20.12.2018 Plex-Probleme "autom. Wiedereintritt" in Kodi nicht beobachtet (Plex-Sandbox Phänomen?) - Code
#	entfernt.
# 29.04.0219 Erweiterung manuelle Eingabe der Aufnahmedauer

def LiveRecord(url, title, duration, laenge):
	PLog('LiveRecord:')
	PLog(url); PLog(title); 
	PLog('duration: %s, laenge: %s' % (duration, laenge))

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)					# Home-Button
	
	dest_path = SETTINGS.getSetting('pref_curl_download_path')
	msg1	= 'LiveRecord:'
	if  dest_path == None or dest_path.strip() == '':
		msg2 	= 'Downloadverzeichnis fehlt in Einstellungen'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(os.path.isdir(dest_path))			
	if  os.path.isdir(dest_path) == False:
		msg2 	= 'Downloadverzeichnis existiert nicht:'
		msg3	= dest_path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li		
		
	if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':	# Aufnahmedauer manuell
		duration = duration[:5]									# 01:00:00, für Dialog kürzen
		dialog = xbmcgui.Dialog()
		duration = dialog.input('Aufnahmedauer eingeben (HH:MM)', duration, type=xbmcgui.INPUT_TIME)
		PLog(duration)
		if duration == '' or duration == ' 0:00':
			msg1 = "Aufnahmedauer fehlt - Abbruch"
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return li	
		duration = "%s:00" % duration							# für ffmpeg wieder auffüllen
		laenge = "%s (Stunden:Minuten)" % duration[:5]			# Info nach Start, s.u.
		PLog('manuell_duration: %s, laenge: %s' % (duration, laenge))
		
	dest_path = dest_path  							# Downloadverzeichnis fuer curl/wget verwenden
	now = datetime.datetime.now()
	mydate = now.strftime("%Y-%m-%d_%H-%M-%S")		# Zeitstempel
	dfname = make_filenames(title)					# Dateiname aus Sendername generieren
	dfname = "%s_%s.mp4" % (dfname, mydate) 	
	dest_file = os.path.join(dest_path, dfname)
	if url.startswith('http') == False:				# Pfad bilden für lokale m3u8-Datei
		if url.startswith('rtmp') == False:
			url 	= os.path.join(Dict['R'], url)	# rtmp-Url's nicht lokal
			url 	= '"%s"' % url						# Pfad enthält Leerz. - für ffmpeg in "" kleiden						
	
	cmd = SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')	% (url, duration, dest_file)
	PLog(cmd); 
	
	PLog(sys.platform)
	if sys.platform == 'win32':							
		args = cmd
	else:
		args = shlex.split(cmd)							
	
	try:
		PIDffmpeg = ''
		sp = subprocess.Popen(args, shell=False)
		PLog('sp: ' + str(sp))

		if str(sp).find('object at') > 0:  			# subprocess.Popen object OK
			# PIDffmpeg = sp.pid					# PID speichern bei Bedarf
			PLog('PIDffmpeg neu: %s' % PIDffmpeg)
			Dict('store', 'PIDffmpeg', PIDffmpeg)
			msg1 = 'Aufnahme gestartet:'
			msg2 = dfname
			msg3 = "Aufnahmedauer: %s" % laenge
			PLog('Aufnahme gestartet: %s' % dfname)	
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li			
				
	
	except Exception as exception:
		msg = str(exception)
		PLog(msg)		
		msg1 = "Fehler: %s" % msg
		msg2 ='Aufnahme fehlgeschlagen'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			
		
#-----------------------------
def get_sort_playlist():						# sortierte Playliste der TV-Livesender
	PLog('get_sort_playlist:')
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	sort_playlist =  []
	for item in playlist:   
		rec = []
		title = stringextract('<title>', '</title>', item)
		# PLog(title)
		title = title.upper()										# lower-/upper-case für sort() relevant
		EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', item)
		img = 	stringextract('<thumbnail>', '</thumbnail>', item)
		link =  stringextract('<link>', '</link>', item)			# url für Livestreaming
		rec.append(title); rec.append(EPG_ID);						# Listen-Element
		rec.append(img); rec.append(link);
		sort_playlist.append(rec)									# Liste Gesamt
	
	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = sorted(sort_playlist,key=lambda x: x[0])		# Array-sort statt sort()
	return sort_playlist
	
#-----------------------------------------------------------------------------------------------------
# EPG: Daten holen in Modul EPG.py, Anzeige hier, Klick zum Livestream
def EPG_ShowSingle(ID, name, stream_url, pagenr=0):
	PLog('EPG_ShowSingle:'); 
#	ID = urllib2.unquote(ID); name = urllib2.unquote(name); stream_url = urllib2.unquote(stream_url);
	# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis, 7=today_human: 
	# Link zur Einzelanzeige href=rec[1] hier nicht verwendet - wenig zusätzl. Infos
	EPG_rec = EPG.EPG(ID=ID, day_offset=pagenr)		# Daten holen
	PLog(len(EPG_rec))
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	if len(EPG_rec) == 0:			# kann vorkommen, Bsp. SR
		msg1 = 'Sender %s:' % name 
		msg2 = 'keine EPG-Daten gefunden'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
		
	today_human = 'ab ' + EPG_rec[0][7]
			
	for rec in EPG_rec:
		href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];
		# PLog(img)
		if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
			img = R('icon-bild-fehlt.png')
		sname = UtfToStr(sname)
		sname = unescape(sname)
		title = sname
		summ = UtfToStr(summ)
		summ = unescape(summ)
		if 'JETZT' in title:			# JETZT-Markierung unter icon platzieren
			summ = "[COLOR red][B]LAUFENDE SENDUNG![/B][/COLOR]\n\n%s" % summ
			title='[COLOR red][B]%s[/B][/COLOR]' % sname
		PLog("title: " + title)
		tagline = 'Zeit: ' + vonbis
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s'}" % (urllib2.quote(stream_url), 
			urllib2.quote(title), urllib.quote_plus(img), urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-single.png'), 
			thumb=img, fparams=fparams, summary=summ, tagline=tagline)
			
	# Mehr Seiten anzeigen:
	max = 12
	pagenr = int(pagenr) + 1
	if pagenr < max: 
		summ = 'naechster Tag'
		fparams="&fparams={'ID': '%s', 'name': '%s', 'stream_url': '%s', 'pagenr': %s}" % (ID, urllib2.quote(name),
			urllib2.quote(stream_url), pagenr)
		addDir(li=li, label=summ, action="dirList", dirID="EPG_ShowSingle", fanart=R('tv-EPG-single.png'), 
		thumb=R(ICON_MEHR), fparams=fparams, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------------------------------------------------------------------------------
# EPG: aktuelle Sendungen aller Sender mode='allnow'
#	26.04.2019 Anzahl pro Seite auf 20 erhöht (Timeout bei Kodi kein Problem wie bei Plex)  

def EPG_ShowAll(title, offset=0):
	PLog('EPG_ShowAll:'); PLog(offset) 
	title = urllib2.unquote(title)
	title_org = title
	title2='Aktuelle Sendungen'
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = get_sort_playlist()	
	PLog(len(sort_playlist))
	PLog(sort_playlist)
	
	rec_per_page = 20								# Anzahl pro Seite (Plex: Timeout ab 15 beobachtet)
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
		img_playlist = R(rec[2])
		ID = rec[1]
		tagline = ''; summ = ''
		
		if ID == '':									# ohne EPG_ID
			tagline = 'weiter zum Livestream'
			title = title_playlist + ': ohne EPG | %s' % tagline
			img = img_playlist
			PLog("img: " + img)
		else:
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis: 
			rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
			# PLog(rec)	# bei Bedarf
			if len(rec) == 0:							# EPG-Satz leer?
				title = title_playlist + ': ohne EPG'
				tagline = 'weiter zum Livestream'
				img = img_playlist			
			else:	
				href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]
				if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
					img = R('icon-bild-fehlt.png')
				title 	= sname.replace('JETZT', title_playlist)		# JETZT durch Sender ersetzen
				# sctime 	= "[COLOR red] %s [/COLOR]" % stime			# Darstellung verschlechtert
				# sname 	= sname.replace(stime, sctime)
				tagline = 'Zeit: ' + vonbis
				
		title = UtfToStr(title)
		title = unescape(title)
		PLog("title: " + title)
					
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s'}" % (urllib2.quote(m3u8link), 
			urllib2.quote(title), urllib2.quote(img), urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-all.png'), 
			thumb=img, fparams=fparams, summary=summ, tagline=tagline)

	# Mehr Seiten anzeigen:
	# PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt 
		PLog(new_offset)
		summ = 'Mehr %s (insgesamt %s)' % (title2, str(max_len))
		fparams="&fparams={'title': '%s', 'offset': '%s'}"	% (title_org, new_offset)
		addDir(li=li, label=summ, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
			thumb=R(ICON_MEHR), fparams=fparams, summary=summ, tagline=title2)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------------------------------------------------------------------------------
# TV LiveListe - verwendet lokale Playlist livesenderTV.xml
# onlySender: Button nur für diesen Sender (z.B. ZDFSportschau Livestream für Menü
#	ZDFSportLive)
def SenderLiveListe(title, listname, fanart, offset=0, onlySender=''):			
	# SenderLiveListe -> SenderLiveResolution (reicht nur durch) -> Parseplaylist (Ausw. m3u8)
	#	-> CreateVideoStreamObject 
	PLog('SenderLiveListe:')
	PLog(title); PLog(listname)
	title = UtfToStr(title); listname = UtfToStr(listname)
			
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
	for i in range(len(playlist)):						# gewählte Channel extrahieren
		item = playlist[i] 
		name =  stringextract('<name>', '</name>', item)
		# PLog(name)
		if name == listname:							# Bsp. Überregional, Regional, Privat
			mylist =  playlist[i] 
			break
	
	mediatype='' 						# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	liste = blockextract('<item>', mylist)				# Details eines Senders
	PLog(len(liste));
	EPG_ID_old = ''											# Doppler-Erkennung
	sname_old=''; stime_old=''; summ_old=''; vonbis_old=''	# dto.
	summary_old=''; tagline_old=''
	for element in liste:							# EPG-Daten für einzelnen Sender holen 	
		link = stringextract('<link>', '</link>', element) 	# HTML.StringFromElement unterschlägt </link>
		link = unescape(link)						# amp; entfernen! Herkunft: HTML.ElementFromString bei &-Zeichen
		PLog('link: ' + link);
		
		# Bei link zu lokaler m3u8-Datei (Resources) reagieren SenderLiveResolution und ParsePlayList entsprechend:
		#	der erste Eintrag (automatisch) entfällt, da für die lokale Ressource kein HTTP-Request durchge-
		#	führt werden kann. In ParsePlayList werden die enthaltenen Einträge wie üblich aufbereitet
		#	
		# Spezialbehandlung für N24 in SenderLiveResolution - Test auf Verfügbarkeit der Lastserver (1-4)
		# EPG: ab 10.03.2017 einheitlich über Modul EPG.py (vorher direkt bei den Sendern, mehrere Schemata)
									
		title = stringextract('<title>', '</title>', element)
		if onlySender:									# Button nur für diesen Sender
			if title != onlySender:
				continue
			
		epg_schema=''; epg_url=''
		epg_date=''; epg_title=''; epg_text=''; summary=''; tagline='' 
		# PLog(SETTINGS.getSetting('pref_use_epg')) 	# Voreinstellung: EPG nutzen? - nur mit Schema nutzbar
		PLog('setting: ' + str(SETTINGS.getSetting('pref_use_epg')))
		if SETTINGS.getSetting('pref_use_epg') == 'true':
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis:
			EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', element)
			PLog(EPG_ID); PLog(EPG_ID_old);
			if  EPG_ID == EPG_ID_old:					# Doppler: EPG vom Vorgänger verwenden
				sname=sname_old; stime=stime_old; summ=summ_old; vonbis=vonbis_old
				summary=summary_old; tagline=tagline_old
				PLog('EPG_ID=EPG_ID_old')
			else:
				EPG_ID_old = EPG_ID
				try:
					rec = EPG.EPG(ID=EPG_ID, mode='OnlyNow')	# Daten holen - nur aktuelle Sendung
					if rec == '':								# Fehler, ev. Sender EPG_ID nicht bekannt
						sname=''; stime=''; summ=''; vonbis=''
					else:
						sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]	
				except:
					sname=''; stime=''; summ=''; vonbis=''						
				if sname:
					title = title + ': ' + sname
				if summ:
					summary = summ
				else:
					summary = ''
				if vonbis:
					tagline = 'Sendung: %s Uhr' % vonbis
				else:
					tagline = ''
				# Doppler-Erkennung:	
				sname_old=sname; stime_old=stime; summ_old=summ; vonbis_old=vonbis;
				summary_old=summary; tagline_old=tagline
		title = UtfToStr(title)
		title = unescape(title)	
		title = title.replace('JETZT:', '')					# 'JETZT:' hier überflüssig
		summary = UtfToStr(summary)
		summary = unescape(summary)	
						
		img = stringextract('<thumbnail>', '</thumbnail>', element) 
		if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
			
		geo = stringextract('<geoblock>', '</geoblock>', element)
		PLog('geo: ' + geo)
		if geo:
			tagline = 'Livestream nur in Deutschland zu empfangen! %s'	% tagline
			
		PLog(title); PLog(link); PLog(img); PLog(summary); PLog(tagline[0:80]);
		Resolution = ""; Codecs = ""; duration = ""
	
		# if link.find('rtmp') == 0:				# rtmp-Streaming s. CreateVideoStreamObject
		# Link zu master.m3u8 erst auf Folgeseite? - SenderLiveResolution reicht an  Parseplaylist durch
		descr = "%s | %s" % (tagline, summary)		# -> Plot (PlayVideo) 
		fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s', 'descr': '%s'}" % (urllib.quote_plus(link), 
			img, urllib.quote_plus(title), urllib.quote_plus(descr))
		util.addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=fanart, thumb=img, 
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
#	
def SenderLiveResolution(path, title, thumb, descr, Merk='false', Startsender=''):
	PLog('SenderLiveResolution:')
	PLog(SETTINGS.getSetting('pref_video_direct'))
	PLog(title)
	title = UtfToStr(title)

	page, msg = get_page(path=path)					# Verfügbarkeit des Streams testen
	if page == '':									# Fallback zum Classic-Sendername in Startsender
		PLog('Fallback Streams ARD-Start')
		path = 'https://classic.ardmediathek.de/tv/live'
		page, msg = get_page(path=path)	
		content = blockextract('class="teaser"', page)
		if len(content) > 0:
			playlist = RLoad(PLAYLIST)
			xml_sender = blockextract('<item>', playlist)	# Blöcke Sender	
			sender_url=''; classicsender=''
			for sender in xml_sender:						# Classic-Sendername ermitteln
				if Startsender:
					title_sender = stringextract('<hrefsender>', '</hrefsender>', sender)
					title_sender = title_sender.strip()
				else:
					title_sender = stringextract('<title>', '</title>', sender)
				# PLog('title: %s, title_sender: %s'  % (title, title_sender))
				# Bsp. title: Deutsche Welle <DW> - Die mediale Stimme Deutschlands
				if title_sender:
					if title_sender.upper() in title.upper():	# Classic-Sendername aus Playlist
						classicsender = stringextract('<hrefsender>', '</hrefsender>', sender)
						PLog('classicsender: ' + classicsender)
						break			
											
			for cont in content:							# Abgleich mit Classic-TV-Live
				startsender = stringextract('headline">', '</', cont)
				if classicsender in startsender:				# Classic-Sendername in Startsender?
					sender_url = BASE_URL + stringextract('href="', '"', cont)
					PLog('sender_url: ' + sender_url)			# Link des Classic-Senders
					break

			if sender_url:		# z.B. //classic.ardmediathek.de/tv/Deutsche-Welle/live?kanal=5876
				path = get_startsender(hrefsender=sender_url)	# Modul util	
				PLog('path: ' + path)				
		

	# direkter Sprung hier erforderlich, da sonst der Player mit dem Verz. SenderLiveResolution
	#	startet + fehlschlägt.
	if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: SenderLiveResolution')
		PlayVideo(url=path, title=title, thumb=thumb, Plot=descr, Merk=Merk)
		return
	
	title = UtfToStr(title); descr = UtfToStr(descr)
	url_m3u8 = path
	PLog(title); PLog(url_m3u8);

	li = xbmcgui.ListItem()
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
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib.quote_plus(url_m3u8), 
			urllib.quote_plus(title), urllib.quote_plus(thumb), urllib.quote_plus(descr))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title, mediatype='video')	
		
	if url_m3u8.find('rtmp') == 0:		# rtmp, nur 1 Videoobjekt
		summary = 'rtmp-Stream'
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib.quote_plus(url_m3u8), 
			urllib.quote_plus(title), urllib.quote_plus(thumb), urllib.quote_plus(descr))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title, mediatype='video')	
		
	# alle übrigen (i.d.R. http-Links), Videoobjekte für einzelne Auflösungen erzeugen
	# Für Kodi: m3u8-Links abrufen, speichern und die Datei dann übergeben - direkte
	#	Übergabe der Url nicht abspielbar
	# is_playable ist verzichtbar
	if url_m3u8.find('.m3u8') >= 0:				# häufigstes Format
		PLog(url_m3u8)
		if url_m3u8.startswith('http'):			# URL extern? (lokal entfällt Eintrag "autom.")	
			li = ParseMasterM3u(li, url_m3u8, thumb, title, tagline=title, descr=descr)	#  Download + Ablage master.m3u8
							
		# Auswertung *.m3u8-Datei  (lokal oder extern), Auffüllung Container mit Auflösungen. 
		# jeweils 1 item mit http-Link für jede Auflösung.
		
		# Parseplaylist -> CreateVideoStreamObject pro Auflösungstufe
		li = Parseplaylist(li, url_m3u8, thumb, geoblock='', tagline=title, descr=descr)	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)					
	else:	# keine oder unbekannte Extension - Format unbekannt
		msg1 = 'SenderLiveResolution: unbekanntes Format. Url:'
		msg2 = url_m3u8
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
		
#--------------------------------------------------------------------------------------------------
# Button für Einzelauflösungen für Streamlink url_m3u8
#	ID: Kennung für home
def show_single_bandwith(url_m3u8, thumb, title, descr, ID):
	PLog('show_single_bandwith:'); 
	
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)						# Home-Button
	
	li = Parseplaylist(li, url_m3u8, thumb, geoblock='', tagline=title, descr=descr)	
	
	xbmcplugin.endOfDirectory(HANDLE)

#-----------------------------
# Ablage master.m3u8, einschl. Behandlung relativer Links
#	Button für "Bandbreite und Aufloesung automatisch" (master.m3u8)
#	Die Ablage dient zur Auswertung der Einzelauflösungen, kann aber bei Kodi auch
#	zum Videostart verwendet werden. 
#   descr = Plot, wird zu PlayVideo durchgereicht.
def ParseMasterM3u(li, url_m3u8, thumb, title, descr, tagline='', sub_path=''):	
	PLog('ParseMasterM3u:'); 
	PLog(title); PLog(url_m3u8); PLog(thumb); PLog(tagline);
	 
	title = UtfToStr(title); descr = UtfToStr(descr); tagline = UtfToStr(tagline); 
	PLog(type(title))	
	
	sname = url_m3u8.split('/')[2]				# Filename: Servername.m3u8
	msg1 = "Datei konnte nicht "				# Vorgaben xbmcgui.Dialog
	msg2 = sname + ".m3u8"
	msg3 = "Details siehe Logdatei"
	
	page, msg = get_page(path=url_m3u8)			# 1. Inhalt m3u8 laden	
	PLog(len(page))
	if page == '':								# Fehlschlag
		msg1 = msg1 + "geladen werden." 
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
		
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
	fpath = os.path.join("%s/%s") % (M3U8STORE, fname)
	PLog('fpath: ' + fpath)
	msg = RSave(fpath, page)			# 3.  Inhalt speichern -> resources/m3u/
	if 'Errno' in msg:
		msg1 = msg1 + " gespeichert werden." # msg1 s.o.
		PLog(msg1); PLog(msg2)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
	else:				
		# Alternative: m3u8-lokal starten:
		# 	fparams="&fparams=url=%s, title=%s, is_playable=%s" % (sname + ".m3u8", title, True)
		# descr -> Plot	
		tagline	 = tagline.replace('||','\n')				# s. tagline in ZDF_get_content
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(urllib.quote_plus(url_m3u8), urllib.quote_plus(title), urllib.quote_plus(thumb), 
			urllib.quote_plus(descr), urllib.quote_plus(sub_path))	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			mediatype='video', tagline=tagline) 

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
			req = urllib2.Request(url_new)
			r = urllib2.urlopen(req)
			playlist = r.read()			
		except:
			playlist = ''
			
		PLog(playlist[:20])
		if 	playlist:	# playlist gefunden - diese url verwenden
			return url_new	
	
	return url_m3u8		# keine playlist gefunden, weiter mit Original-url
				  
####################################################################################################
# path = ARD_RadioAll = https://classic.ardmediathek.de/radio/live?genre=Alle+Genres&kanal=Alle
#	Bei Änderungen der Sender Datei livesenderRadio.xml anpassen (Sendernamen, Icons)
# 
def RadioLiveListe(path, title):
	PLog('RadioLiveListe:');
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	playlist = RLoad(PLAYLIST_Radio) 
	#PLog(playlist)					
	
	liste = blockextract('<item>', playlist)
	PLog(len(liste))
	
	# Unterschied zur TV-Playlist livesenderTV.xml: Liste  der Radioanstalten mit Links zu den Webseiten.
	#	Ab 11.10.2917: die Liste + Reihenfolge der Sender wird in der jew. Webseite ermittelt. Die Sender-Liste
	#		wird aus LivesenderRadio.xml geladen und gegen die Sendernamen abgeglichen. Die Einträge sind paarweise
	#		angelegt (Sendername:Icon).
	#		Ohne Treffer beim  Abgleich wird ein Ersatz-Icon verwendet (im Watchdog-PRG führt dies zur Fehleranzeige). 
	#		Die frühere Icon-Liste in <thumblist> entfällt.
	#	Nach Auswahl einer Station wird in RadioAnstalten der Audiostream-Link ermittelt.

	for s in liste:
		# PLog(s)					# bei Bedarf
		title = stringextract('<title>', '</title>', s)
		link = stringextract('<link>', '</link>', s) 	
		link = link.strip()							# Leerz. am Ende entfernen
		img = stringextract('<thumbnail>', '</thumbnail>', s) 
		if img.find('://') == -1:	# Logo lokal? -> wird aus Resources geladen, Unterverz. leider n.m.
			img = R(img)
		else:
			img = img
		PLog("img: " + img);
			
		sender = stringextract('<sender>', '</sender>', s)			# Auswertung sender + thumbs in RadioAnstalten
		sender = (sender.replace('\n', '').replace('\t', ''))
		PLog("sender: " + sender);
			
		PLog(title); PLog(link); PLog(img); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'sender': '%s', 'fanart': '%s'}" % (urllib2.quote(link), 
		urllib2.quote(title),  urllib2.quote(sender), img)		# fanart = Logo des Hauptsenders
		PLog('fparams RadioLiveListe: ' + fparams)
		addDir(li=li, label=title, action="dirList", dirID="RadioAnstalten", fanart=R(ICON_MAIN_RADIOLIVE), thumb=img, 
			fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------
def RadioAnstalten(path, title, sender, fanart):
	PLog('RadioAnstalten: ' + path); 
	# PLog(sender)
	entry_path = path	# sichern
	
	li = xbmcgui.ListItem()
	
	errmsg1 = 'RadioAnstalten | %s' % title			# Fehlermeldung xbmcgui.Dialog
	errmsg2 = 'Seite kann nicht geladen werden, Url:'
	errmsg3 = '%s' % (path)
		
	# header: chrome-dev-tools(curl-statements)	
	header = "{'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1', \
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', \
		'Accept-Language': 'de,en;q=0.9,fr;q=0.8,de-DE;q=0.7,da;q=0.6,it;q=0.5,pl;q=0.4,uk;q=0.3,en-US;q=0.2'}"	
	page, msg = get_page(path=path, header=header)				
	entries = blockextract('class="teaser"', page)
	if page == '' or len(entries) == 0:
		xbmcgui.Dialog().ok(ADDON_NAME, errmsg1, errmsg2, errmsg3)
		return li
	
	del entries[0:2]								# "Javascript-Fehler" überspringen (2 Elemente)
	PLog(len(entries))

	item_cnt = 0
	for element in entries:
		pos = element.find('class=\"socialMedia\"')			# begrenzen
		if pos >= 0:
			element = element[0:pos]
		# PLog(element[0:80])						#  nur bei Bedarf)	
		
		img_src = ""						
			
		headline = ''; subtitle = ''				# nicht immer beide enthalten
		if element.find('headline') >= 0:			# h4 class="headline" enthält den Sendernamen
			headline = stringextract('\"headline\">', '</h4>', element)
		if element.find('subtitle') >= 0:	
			subtitle = stringextract('\"subtitle\">', '</p>', element)
		PLog(headline); PLog(subtitle);				
			
		href = stringextract('<a href=\"', '\"', element)
		sid = href.split('documentId=')[1]
		
		path = BASE_URL + '/play/media/' + sid + '?devicetype=pc&features=flash'	# -> Textdatei mit Streamlink
		PLog('Streamlink: ' + path)
		path_content, msg = get_page(path)	
		if path_content == '':
			errmsg2 = 'Streamlink kann nicht geladen werden, Url:'
			xbmcgui.Dialog().ok(ADDON_NAME, errmsg1, errmsg2, path)
			return li			
		
		PLog(path_content[0:80])			# enthält nochmal Bildquelle + Auflistung Streams (_quality)
										# Streamlinks mit .m3u-Ext. führen zu weiterer Textdatei - Auswert. folgt 
		#slink = stringextract('_stream\":\"', '\"}', path_content) 		# nur 1 Streamlink? nicht mehr aktuell
		link_path,link_img, m3u8_master, geoblock, sub_path = parseLinks_Mp4_Rtmp(path_content)	# mehrere Streamlinks auswerten,
																						# geoblock hier nicht verwendet
		
		if headline:						# Zuordnung zu lokalen Icons, Quelle livesenderRadio.xml
			senderlist = sender.split('|')
			PLog("senderlist: " + str(senderlist)); 		# bei Bedarf
			for i in range (len(senderlist)):
				sname = ''; img = ''
				try:								# try gegen Schreibfehler in  livesenderRadio.xml
					pair =  mystrip(senderlist[i]) 	# mystrip wg. Zeilenumbrüchen in livesenderRadio.xml
					pair = pair.split(':')			# Paarweise, Bsp.: B5 aktuell:radio-b5-aktuell.png
					sname 	= pair[0].strip()
					img 	= pair[1].strip()
				except:
					break	
				headline = UtfToStr(headline)		
				sname 	 = UtfToStr(sname)
				PLog('headline: ' + headline.upper()); PLog(sname.upper());
				if sname.upper() in headline.upper():	# lokaler Name in <sender> muss in headline enthalten sein
					img = R(img)					# lokales Icon
					if os.path.exists(img):
						img_src = img
					else:
						img_src = link_img			# Fallback aus parseLinks_Mp4_Rtmp, ev. nur Mediathek-Symbol
					PLog("img_src: " + img_src)
					break

		PLog(link_path); PLog(link_img); PLog(img_src);PLog(m3u8_master); 
		headline_org =  headline	# sichern		
		for i in range(len(link_path)):
			s = link_path[i]
			PLog(s)
			mark = s[0]
			slink = s[2:]
			PLog(s); PLog(mark); PLog(slink); 
			PLog("m3u_Test:");
			if slink.find('.m3u') > 9:		# der .m3u-Link führt zu weiterer Textdatei, die den Streamlink enthält
				try:						# Request kann fehlschlagen, z.B. bei RBB, SR, SWR
					slink_content, msg = get_page(path=path)	
					if slink_content == '':
						errmsg1 = 'RadioAnstalten | %s' % headline		
						errmsg2 = '.m3u-Link kann nicht geladen werden, Url:'
						xbmcgui.Dialog().ok(ADDON_NAME, errmsg1, errmsg2, slink)
						return li
					z = slink_content.split()
					PLog(z)
					slink = z[-1]				# Link in letzter Zeile
				except:
					slink = ""
			
			PLog(img_src); PLog(headline); PLog(subtitle); PLog(sid); PLog(slink);	# Bildquelle: z.Z. verwenden wir nur img_src
			headline=UtfToStr(headline); subtitle=UtfToStr(subtitle); headline_org=UtfToStr(headline_org); 
			
			if subtitle == '':		
				subtitle = headline
			if mark == '0':						#  Titel kennz. (0=64kb, 1=128kb, 2=128kb), bisher nur diese gesehen
				headline = headline_org + ' (64 KByte)'
			if mark == '1' or mark == '2':					
				headline = headline_org + ' (128 KByte)'
			headline = "%s | %s" % (headline, subtitle)			# für kodi subtitle -> label
			headline = unescape(headline)
			headline = headline.replace('&quot;', '"')			# unescape erfolglos?
				
			if slink:						# normaler Link oder Link über .m3u ermittelt
				# msg = ', Stream ' + str(i + 1) + ': OK'		# Log in parseLinks_Mp4_Rtmp ausreichend
				msg = ''
				if img_src.find('http') >= 0:	# Bildquelle Web
					img_src = img_src.replace('https', 'http')	# Kodi: SSL-Problem bei Abruf
					thumb=img_src
				else:							# Bildquelle lokal
					thumb=R(img_src)
				
				# slink = slink.replace('https', 'http')		# hier sinnlos bei üblichen Redirects
				# url_template: ersetzt in PlayAudio https- durch http-Links 
				headline=repl_json_chars(headline)			# json-komp. für func_pars in router()
				subtitle=repl_json_chars(subtitle)			# dto.
				
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'url_template': '1', 'Plot': '%s'}" % \
					(urllib.quote_plus(slink), urllib.quote_plus(headline), urllib.quote_plus(img_src), 
					urllib.quote_plus(subtitle))
				PLog('fparams RadioAnstalten: ' + fparams)
				addDir(li=li, label=headline, action="dirList", dirID="PlayAudio", fanart=fanart, thumb=img_src, 
					fparams=fparams, mediatype='music')	
												 	
			else:
				msg = ' Stream ' + str(i + 1) + ': nicht verfügbar'	# einzelnen nicht zeigen - verwirrt nur
			item_cnt = item_cnt +1
	
	PLog('Anzahl: ' + str(item_cnt))
	if item_cnt < 1:	      		# keine Radiostreams gefunden		
		PLog('item_cnt = 0, keine Radiostreams gefunden') 		 
		line1 = '%s: keine Radiostreams gefunden / verfuegbar' % title
		line2 = 'URL:'
		line3 = '%s' % (path)
		xbmcgui.Dialog().ok(ADDON_NAME, line1, line2, line3)
		return li			
										
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

###################################################################################################
#									ZDF-Funktionen
###################################################################################################
# Startseite der ZDF-Mediathek 
#	show_stage (rekursiv): falls true, wird der Stage-Bereich mit den Highlights gelistet
#	Die Cluster haben dieselbe Struktur wie ZDF-Rubriken mit Besonderheit class="loader"
#		(Nachlade-Beiträge, escaped) - daher jeweils Buttons für ZDFRubrikSingle.
#	Rubriken enthalten zusätzl. Clusterung - Bearbeitung in Funktion ZDFRubriken.	
def ZDFStart(title, show_stage=''): 
	PLog('ZDFStart:'); 
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	path = ZDF_BASE
	page, msg = get_page(path=path)
	if page == '':
		msg1 = "ZDF-Startseite nicht im Web verfügbar."
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		
	stage = stringextract('class="sb-page">', 'data-module="clustersort"', page) # cut Stage 
	
	# 2. Durchlauf: Stage listen
	#	Inhaltstext im Voraus laden" in ZDF_get_content
	if show_stage:												# Liste Highlights / 
		li, page_cnt = ZDF_get_content(li=li, page=stage, ref_path=path, ID='ZDFStage')	
		xbmcplugin.endOfDirectory(HANDLE)						# Ende 2. Durchlauf	
	
	# 1. Durchlauf: Buttons Stage + Cluster 
	title = 'Highlights'
	href	= stringextract('href="', '"', stage)
	thumb	= stringextract('data-src="', '"', stage)			# img vom 1. Beitrag zeigen
	fparams="&fparams={'title': '%s', 'show_stage': 'true'}" % urllib2.quote(title)
	addDir(li=li, label=title, action="dirList", dirID="ZDFStart", fanart=thumb, 
		thumb=thumb, fparams=fparams)
		
	content =  blockextract('cluster-title"', page)				# 2.Cluster
	PLog('content: ' + str(len(content)))
	for rec in content:
		href	= stringextract('href="', '"', rec)
		title 	= stringextract('cluster-title" >', '<', rec)	# Ref. für ZDFRubrik
		thumb	= stringextract('data-src="', '"', rec)			# img vom 1. Beitrag zeigen
		PLog('Satz:')
		PLog(href); PLog(title); PLog(thumb); 

		# "Inhaltstext im Voraus laden" in ZDF_get_content (via ZDFRubrikSingle ->
		#	ZDF_Sendungen) - 
		if title == 'Rubriken':
			fparams="&fparams={'name': 'Rubriken'}"
			addDir(li=li, label="Rubriken", action="dirList", dirID="ZDFRubriken", fanart=R(ICON_ZDF_RUBRIKEN), 
				thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)
		
		# Begrenzung 'Alles auf einen Blick' -  Webseite enthält zusätzl.  A-Z, Verpasst, Bestbewertet,
		#	Livestreams Ausland, Barrierefrei
		elif title == 'Alles auf einen Blick':				# Livestreams
			title = 'ZDF Livestreams'
			fparams="&fparams={'title': '%s'}"	% title 
			addDir(li=li, label=title, action="dirList", dirID="ZDFStartLive", fanart=thumb, 
				thumb=thumb, fparams=fparams)	
				
		else:												# restl. Cluster	
			fparams="&fparams={'title': '%s', 'path': '%s',  'clus_title': '%s'}"	% (urllib2.quote(title), 
				urllib2.quote(path), urllib2.quote(title))
			addDir(li=li, label=title, action="dirList", dirID="ZDFRubrikSingle", fanart=thumb, 
				thumb=thumb, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE)	
#---------------------------------------------------------------------------------------------------
def ZDFStartLive(title): 										# ZDF-Livestreams von ZDFStart
	PLog('ZDFStartLive:'); 
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	path = 'https://www.zdf.de/live-tv'
	page, msg = get_page(path=path)
		
	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	content = blockextract('js-livetv-scroller-cell', page)		# Playerdaten einschl. apiToken
	for rec in content:
		geo=''; fsk=''
		title 		= stringextract('visuallyhidden">', '<', rec)
		apiToken	= stringextract('apiToken": "', '"', rec)
		href		= stringextract('"content": "', '"', rec)
		thumb 	= stringextract('data-src="', '"', rec)			# erstes img = größtes
		
		geo		= stringextract('geolocation="', '"', rec)
		if geo:
			geo = "Geoblock: %s" % geo
		fsk		= stringextract('-fsk="', '"', rec)
		if fsk:
			fsk = "FSK: %s" % fsk
			fsk = fsk.replace('none', 'ohne')
		tagline = "%s | %s" % (geo, fsk)
		
		PLog('Satz:')
		PLog(title); PLog(apiToken); PLog(href);  PLog(thumb);
		
		fparams="&fparams={'url': '%s', 'title': '%s', 'apiToken': '%s', 'thumb': '%s', 'tagline': '%s'}" %\
			(urllib2.quote(href), urllib2.quote(title), apiToken, thumb, urllib2.quote(tagline))	
		addDir(li=li, label=title, action="dirList", dirID="ZDFStartLiveSingle", fanart=thumb, thumb=thumb, 
			fparams=fparams, tagline=tagline, mediatype=mediatype)
		
	xbmcplugin.endOfDirectory(HANDLE)		
#---------------------------------------------------------------------------------------------------
def ZDFStartLiveSingle(url, title, apiToken, thumb, tagline, Merk='false'): 	# einzelner ZDF-Livestream
	PLog('ZDFStartLiveSingle:'); 

	li = xbmcgui.ListItem()

	header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken
	page, msg	= get_page(path=url, header=header, JsonPage=True)	
	PLog("player_json: " + page[:40])
	PLog(page)
	
	ptmd_player = 'ngplayer_2_3'											# aus get_formitaeten							
	videodat_url = stringextract('ptmd-template": "', '",', page)
	videodat_url = videodat_url.replace('{playerId}', ptmd_player) 			# ptmd_player injiziert 
	videodat_url = 'https://api.zdf.de' + videodat_url
	PLog('videodat_url: ' + videodat_url)
	
	page, msg	= get_page(path=videodat_url, header=header, JsonPage=True)
	PLog("videodat: " + page[:40])
	
	m3u8_url = stringextract('uri": "', '"', page)
	PLog("m3u8_url: " + m3u8_url)
	
	formitaeten = blockextract('formitaeten', page)		# Video-URL's ermitteln
	PLog('formitaeten: ' + str(len(formitaeten)))
	Plot_par=''; geoblock=''; sub_path=''
	only_list = ["h264_aac_ts_http_m3u8_http"]					# Video-Items erstellen: m3u8-Formate
	li, download_list = show_formitaeten(li=li, title_call=title, formitaeten=formitaeten, tagline=tagline,
		thumb=thumb, only_list=only_list,geoblock=geoblock, sub_path=sub_path, Merk=Merk)		

	xbmcplugin.endOfDirectory(HANDLE)		
####################################################################################################
# ZDF-Suche:
# 	Voreinstellungen: alle ZDF-Sender, ganze Sendungen, sortiert nach Datum
#	Anzahl Suchergebnisse: 25 - nicht beeinflussbar
#	Format Datum (bisher nicht verwendet)
#		..&from=2012-12-01T00:00:00.000Z&to=2019-01-19T00:00:00.000Z&..
#	ZDF_Search_PATH steht bei Rekursion nicht als glob. Variable zur Verfügung

def ZDF_Search(query=None, title='Search', s_type=None, pagenr=''):
	if 	query == '':	
		query = get_query(channel='ZDF')
	PLog(query)
	if  query == None or query.strip() == '':
		return ""
	name = 'Suchergebnis zu: ' + urllib2.unquote(query)

	PLog('ZDF_Search:'); PLog(query); PLog(pagenr); PLog(s_type)

	ID='Search'
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if s_type == 'Bilderserien':	# 'ganze Sendungen' aus Suchpfad entfernt:
		ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=&sortBy=date&page=%s'
		ID=s_type
	
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1

	path = ZDF_Search_PATH % (query, pagenr) 
	PLog(path)	
	page, msg = get_page(path=path)	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog(searchResult);
	
	# PLog(page)	# bei Bedarf		
	NAME = 'ZDF Mediathek'
	name = 'Suchergebnisse zu: %s (Gesamt: %s), Seite %s'  % (urllib.unquote(query), searchResult, pagenr)

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	# Der Loader in ZDF-Suche liefert weitere hrefs, auch wenn weitere Ergebnisse fehlen
	if searchResult == '0' or 'class="artdirect " >' not in page:
		query = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
		msg1 = 'Keine Ergebnisse (mehr) zu: %s' % query  
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
				
	# anders als bei den übrigen ZDF-'Mehr'-Optionen gibt der Sender Suchergebnisse bereits
	#	seitenweise aus, hier umgesetzt mit pagenr - offset entfällt	
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID=ID)
	PLog('li, page_cnt: %s, %s' % (li, page_cnt))
	
	if page_cnt == 'next':							# mehr Seiten (Loader erreicht)
		pagenr = int(pagenr) + 1
		query = query.replace('%252B', '+')				# # quotierten Suchbegriff korrigieren
		query = UtfToStr(query)
		path = ZDF_Search_PATH % (query, pagenr)
		PLog(pagenr); PLog(path)
		title = "Mehr Ergebnisse suchen zu: %s"  % query.replace('+', ' ')	
		fparams="&fparams={'query': '%s', 's_type': '%s', 'pagenr': '%s'}" % (urllib2.quote(query), s_type, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE)
	
#-------------------------
def ZDF_Verpasst(title, zdfDate):
	PLog('ZDF_Verpasst:'); PLog(title); PLog(zdfDate);

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	path = ZDF_SENDUNG_VERPASST % zdfDate
	page, msg = get_page(path)
	if page == '':
		msg1 = "Abruf fehlgeschlagen | %s" % title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg, '')
		return li 
	PLog(path);	PLog(len(page))

	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='VERPASST')
	PLog("page_cnt: " + str(page_cnt))
		
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
def ZDFSendungenAZ(name):						# name = "Sendungen A-Z"
	PLog('ZDFSendungenAZ:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	azlist = list(string.ascii_uppercase)
	azlist.append('0-9')

	# Menü A to Z
	for element in azlist:
		title='Sendungen mit ' + element
		fparams="&fparams={'title': '%s', 'element': '%s'}" % (title, element)
		addDir(li=li, label=title, action="dirList", dirID="ZDFSendungenAZList", fanart=R(ICON_ZDF_AZ), 
			thumb=R(ICON_ZDF_AZ), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
# Hier zeigt das ZDF die Sendereihen ohne offset
def ZDFSendungenAZList(title, element):			# ZDF-Sendereihen zum gewählten Buchstaben
	PLog('ZDFSendungenAZList:')
	PLog(title)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	group = element	
	if element == '0-9':
		group = '0+-+9'		# ZDF-Vorgabe
	azPath = ZDF_SENDUNGEN_AZ % group
	PLog(azPath);
	page, msg = get_page(path=azPath)	
	if page == '':
		msg1 = 'AZ-Beiträge können nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=azPath, ID='DEFAULT')
	PLog(page_cnt)  
	if page_cnt == 0:	# Fehlerbutton bereits in ZDF_get_content
		return li		
		
	# if offset: 	Code entfernt, in Kodi nicht nutzbar
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# 	wrapper für Mehrfachseiten aus ZDF_get_content (multi=True). Dort ist kein rekursiver Aufruf
#	möglich (Übergabe Objectcontainer in Callback nicht möglich - kommt als String an)
#	Hinw.: Drei-Stufen-Test - Genehmigungsverfahren für öffentlich-rechtliche Telemedienangebote
#		s.  https://www.zdf.de/zdfunternehmen/drei-stufen-test-100.html
# 	06.05.2019 Anpassung an ZDFRubrikSingle (neue ZDF-Struktur): Vorprüfung auf einz. Videobeitrag,
#		Durchreichen von tagline + thumb an ZDF_getVideoSources
#
def ZDF_Sendungen(url, title, ID, page_cnt=0, tagline='', thumb=''):
	PLog('ZDF_Sendungen:')
	PLog(title); PLog(ID); 
	title_org 	= title
	page_cnt_org= int(page_cnt)
	
	li = xbmcgui.ListItem()
				
	page, msg = get_page(path=url)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 

	if 	'class="artdirect " >' not in page:		# Vorprüfung auf einz. Videobeitrag	
		if page.find('class="b-playerbox') > 0 and page.find('class="item-caption') > 0:
			ZDF_getVideoSources(url=url, title=title, thumb=thumb, tagline=tagline)
		else:
			msg1 = 'Leider kein Video gefunden in:'
			msg2 = title
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
						
	li = home(li, ID='ZDF')						# Home-Button			
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=url, ID='VERPASST')

	PLog(page_cnt)
	if page_cnt == 0:	# Fehlerbutton bereits in ZDF_get_content
		return li
				
	if ID == 'ZDFSportLive':					# ohne zusätzliche Suche 
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
	# if offset:	Code entfernt, in Kodi nicht nutzbar
	title = UtfToStr(title)
	label = "Alle Beiträge zu >%s< suchen"  % title
	query = title.replace(' ', '+')	
	tagline = "zusätzliche Suche starten"
	summ 	= "suche alle Beiträge, die sich auf >%s< beziehen" % title
	fparams="&fparams={'query': '%s'}" % urllib2.quote(query)
	addDir(li=li, label=label, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams, tagline=tagline, summary=summ)
		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
  
####################################################################################################
def ZDFRubriken(name):								# ZDF-Bereich, Liste der Rubriken
	PLog('ZDFRubriken:')
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	# zuerst holen wir uns die Rubriken von einer der Rubrikseiten:
	path = 'https://www.zdf.de/doku-wissen'
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 						

	listblock =  stringextract('<li class=\"dropdown-block x-left\">', 'link js-track-click icon-104_live-tv', page)
	rubriken =  blockextract('class="dropdown-item', listblock)
	
	for rec in rubriken:											# leider keine thumbs enthalten
		path = stringextract('href="', '"', rec)
		path = ZDF_BASE + path
		title = stringextract('class="link-text">', '</span>', rec)
		title = mystrip(title)
		if title == "Sendungen A-Z":	# Rest nicht mehr relevant
			break
		fparams="&fparams={'title': '%s', 'path': '%s'}"	% (urllib2.quote(title), urllib2.quote(path))
		addDir(li=li, label=title, action="dirList", dirID="ZDFRubrikSingle", fanart=R(ICON_ZDF_RUBRIKEN), 
			thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-------------------------
# ZDF-Bereich, Sendungen einer Rubrik (unbegrenzt, anders als A-Z Beiträge)
#	Besonderheit: die Zielseiten enthalten class="loader" (Nachlade-Beiträge, 
#	escaped).
#	Aufruf auch aus ZDFStart (Struktur wie ZDF-Rubriken).
#	2-facher Aufruf - Unterscheidung nach Cluster-Titeln (clus_title):
#		1. Übersichtseite (Cluster)			- Rücksprung hierher
#		2. Zielseite (z.B. einzelne Serie) 	- Sprung -> ZDF_Sendungen
# 	ZDF_Sendungen macht eine Vorprüfung auf Einzelvideos vor Aufruf von
#		ZDF_get_content. Einzelvideos -> ZDF_getVideoSources
#
#	Hinw.: "Verfügbar bis" bisher nicht in Rubrikseiten gefunden (wie
#		teaserElement, s. get_teaserElement)
#
def ZDFRubrikSingle(title, path, clus_title=''):							
	PLog('ZDFRubrikSingle:'); PLog(title); PLog(clus_title)
	path_org = path
	title=UtfToStr(title); clus_title=UtfToStr(clus_title);
	
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 

	cluster =  blockextract('class="cluster-title"', page)
	PLog(len(cluster))
	if clus_title:								# Beiträge zu gesuchtem Cluster auswerten
		for clus in cluster:								
			clustertitle = stringextract('cluster-title" >', '</', clus)
			if clustertitle in clus_title:		# Cluster gefunden
				PLog('clustertitle gefunden: ' + clustertitle)
				break
		content =  blockextract('class="b-cluster-teaser', clus) # Beiträge des Clusters
		for rec in content:	
			title='';  clustertitle=''; lable=''
			if 'class="loader"' in rec:							# Nachlade-Beiträge, escaped
				rec = unescape(rec)
				PLog('loader_Beitrag')
				# PLog(rec); 	# bei Bedarf
				#	Auswertung + Rückgabe aller  Bestandteile
				sophId,path,title,descr,img_src,dauer,tag,NodePath = get_teaserElement(rec)
				lable = title
				
				if img_src == '':									# Fallback
					img_src = R('icon-bild-fehlt.png')
				if path == '':
					path	= "https://www.zdf.de%s/%s.html" % (NodePath, sophId)	
			
			else:
				img_src =  stringextract('data-srcset="', ' ', rec)	
				href = 	stringextract('<a href', '</a>', rec)	   # href + Titel	
				PLog("href: " + href)
				path = stringextract('="', '"', href)
				if path == '' or 'skiplinks' in path:
					continue
				if path.startswith('http') == False:		
					path = ZDF_BASE + path	
				title = stringextract('title="', '"', href)
				title = unescape(title)
				
				lable = stringextract('teaser-label">', '</div>', rec)
				lable = cleanhtml(lable)							# Bsp. <strong>2 Staffeln</strong>
				if lable == '':										# label nicht in Nachlade-Beiträgen
					lable = title
				else:
					if 'Folgen' in lable or 'Staffeln' in lable:		# Formatierung
						lable = lable.ljust(11) + "| %s" % title
					else:
						lable = "%s | %s" % (title, lable)
						
				dauer	= stringextract('teaser-info">', '<', page)	
				descr = stringextract('teaser-text" >', '</', rec)	# -> tagline + Param.
				
			if descr and dauer:
				descr = "%s | %s:\n\n%s" % (title, dauer, descr)
				if clustertitle:
					descr = "%s | %s" % (clustertitle, descr)
				
							
			descr=UtfToStr(descr); clustertitle=UtfToStr(clustertitle); title=UtfToStr(title);	
			lable=UtfToStr(lable);
			 		
			title = repl_json_chars(title)
			lable = unescape(lable)
			descr = unescape(descr)
			descr = repl_json_chars(descr)
			descr_par = ''					# n.b. in ZDF_Sendungen
			
			PLog('Satz:')
			PLog(title);PLog(path);PLog(img_src);PLog(descr);PLog(dauer);
			fparams="&fparams={'title': '%s', 'url': '%s', 'ID': '%s', 'tagline': '%s', 'thumb': '%s'}"	%\
				(urllib2.quote(title),  urllib2.quote(path), 'VERPASST', urllib2.quote(descr_par),
				urllib2.quote(img_src))
			addDir(li=li, label=lable, action="dirList", dirID="ZDF_Sendungen", fanart=img_src, 
				thumb=img_src, tagline=descr, fparams=fparams)
				

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
			
	else:										# nur Cluster listen, ohne Bilder
		for clus in cluster:					# Cluster				
			clustertitle = stringextract('cluster-title" >', '</', clus)
			PLog(clustertitle);
			clustertitle = UtfToStr(clustertitle); title = UtfToStr(title)
			img_src = R(ICON_DIR_FOLDER)
			fparams="&fparams={'title': '%s', 'path': '%s', 'clus_title': '%s'}" % (urllib2.quote(clustertitle),
				urllib2.quote(path), urllib2.quote(clustertitle))
			addDir(li=li, label=clustertitle, action="dirList", dirID="ZDFRubrikSingle", fanart=img_src, 
				thumb=img_src, fparams=fparams)				

	#if offset:	Code entfernt, in Kodi nicht nutzbar
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)


#-------------------------
# Ersatz für javascript: Ermittlung Icon + Sendedauer
#	die html-Seite des get_teaserElements wird aus TEXTSTORE 
#	geladen bzw. bei www.zdf.de/teaserElement abgerufen und
#	dann in TEXTSTORE gespeichert.
#	Hinw.: "Verfügbar bis" nicht im teaserElement enthalten
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
	sophoraId = urllib.quote_plus(sophoraId); teaserHeadline = urllib.quote_plus(teaserHeadline);
	teasertext = urllib.quote_plus(teasertext); contextStructureNodePath = urllib.quote_plus(contextStructureNodePath);
		
	path = "https://www.zdf.de/teaserElement?sophoraId=%s&style=m2&teaserHeadline=%s&teasertext=%s&reloadTeaser=true&filterReferenceId=%s&mainContent=false&sourceModuleType=cluster-s&highlight=false&contextStructureNodePath=%s&mostwatched=%s&recommended=%s&newest=%s" \
	% (sophoraId, teaserHeadline,teasertext,filterReferenceId,contextStructureNodePath,mostwatched,recommended,newest)

	fpath = os.path.join(TEXTSTORE, sophoraId)		# 1. teaserElement abrufen
	PLog('fpath: ' + fpath)
	if os.path.exists(fpath):						# Element lokal laden
		PLog('lade lokal:') 
		page =  RLoad(fpath, abs_path=True)	
	else:											#  von www.zdf.de/teaserElement laden
		page, msg = get_page(path=path)			
		if page:									# 	und in TEXTSTORE speichern
			msg = RSave(fpath, page)
		
	PLog(page[:100])
	if page:										# 2. teaserElement auswerten
		img_src =  stringextract('data-srcset="', ' ', page)
		title	= stringextract('plusbar-title="', '"', page)
		ctitle1 = stringextract('teaser-cat-category">', '<', page)  		# Bsp. Show | Bares für Rares
		ctitle2 = stringextract('teaser-cat-brand">', '<', page)  		# 
		tag 	= ctitle1.strip()										# -> tag
		if ctitle2:
			tag = "%s | %s" % (tag, ctitle2.strip())
		path	= stringextract('plusbar-url="', '"', page)
		if path.startswith('http') == False:
			path = ZDF_BASE + path
		dauer	= stringextract('teaser-info">', '<', page)	
		desrc	= stringextract('teaser-text" >', '<', page)
		
		# sophId s.o.
		return sophId, path, title, descr, img_src, dauer, tag, NodePath	
	else:									#  Fallback-Rückgaben, Bild + Dauer leer
		img_src=''; dauer=''; tag=''; NodePath=''
		return sophId, path, title, descr, img_src, dauer, tag, NodePath
	
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
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
		
	# unbegrenzt (anders als A-Z Beiträge):
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='MeistGesehen')
	
	PLog(page_cnt)
	# if offset:	Code entfernt, in Kodi nicht nutzbar
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
####################################################################################################
# ZDF Barrierefreie Angebote - Vorauswahl
# todo: Icons für UT + Gebärdensprache, vorhanden: ICON_ZDF_HOERFASSUNGEN
def BarriereArm(title):				
	PLog('BarriereArm:')
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')							# Home-Button

	path = ZDF_BARRIEREARM
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	Dict("store", 'BarriereArm', page)				# -> Cache für BarriereArmSingle
	
	# z.Z. 	>Die neuesten  Hörfassungen<
	#		>Die neuesten Videos mit Untertitel<
	#		>Die neuesten heute-journal-Videos mit Gebärdensprache<
	content = blockextract('class="b-content-teaser-list">', page)
	PLog(len(content))
	for rec in content:	
		title = stringextract('<h2 class="title"', '</h2>', rec)
		title = title.strip()
		title = (title.replace('>', '').replace('<', ''))
		PLog(title)
		if 'Hörfassung' in title or 'Audiodeskription' in title:			# Filter
			if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true' or \
				SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
				msg1 = 'Hinweis:'
				msg2 = 'Filter für Hörfassungen oder  Audiodeskription ist eingeschaltet!'
				xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, "")		
		
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (urllib2.quote(path), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="BarriereArmSingle", fanart=R(ICON_ZDF_BARRIEREARM), 
			thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------------------
# Aufrufer: BarriereArm,	ZDF Barrierefreie Angebote
#	path in BarriereArm geladen, wir laden  erneut
def BarriereArmSingle(path, title):
	PLog('BarriereArmSingle: ' + title)
	
	title = UtfToStr(title)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	page = Dict("load", 'BarriereArm')			# Seite aus Cache laden
	
	if page == False:							# Seite fehlt im Cache - path anfordern
		page, msg = get_page(path=path)			# path=ZDF_BARRIEREARM
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	content = blockextract('class="b-content-teaser-list">', page)
	PLog(len(content))
	for rec in content:	
		if title in rec:
			break
	
	li, page_cnt  = ZDF_get_content(li=li, page=rec, ref_path=path, ID='BARRIEREARM')
	
	PLog(page_cnt)
	# if offset:	Code entfernt, in Kodi nicht nutzbar
			
	xbmcplugin.endOfDirectory(HANDLE)
			
####################################################################################################
# Leitseite zdf-sportreportage - enthält Vorschau mit Links zu den Reportageseiten - Auswertung in
#	ZDFSportLiveSingle. 
#	Angefügt: Button für zurückliegende Sendungen der ZDF-Sportreportage.
#	Angefügt: Button für Sprung zum Livestream (unabhängig vom Inhalt)
# Bei aktivem Livestream wird der Link vorangestellt (Titel: rot/bold),
# Stream am 27.04.2019: 
#	http://zdf0304-lh.akamaihd.net/i/de03_v1@392855/master.m3u8
#		ohne Zusatz (Web-Url) ?b=0-776&set-segment-duration=quality
#  29.04.2019 Button für Livestream wieder entfernt (Streams wechseln), dto. Eintrag livesenderTV.xml
def ZDFSportLive(title):
	PLog('ZDFSportLive:'); 
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	path = 'https://www.zdf.de/sport/sport-im-zdf-livestream-live-100.html'	 # Leitseite		
	page, msg = get_page(path=path, header="{'Pragma': 'no-cache'}")		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	 	
	if '<strong>Jetzt live</strong>' in page:						# 1. LIVESTREAM läuft!
		mediatype='' 		
		if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
			mediatype='video'
		rec = stringextract('class="big-headline">Derzeit live</h2>', 'data-tracking="', page)
		href 	= stringextract('data-plusbar-url="', '"', rec)
		imgset 	= stringextract('data-zdfplayer-teaser-image=', '</div', rec)
		img		=  stringextract('www.zdf.de', '?', imgset)
		img		= 'https://www.zdf.de' + img.replace('\\', '')
		title	= "Jetzt live: " + stringextract('title="', '"', rec)
		title	= '[COLOR red][B]%s[/B][/COLOR]' % title
		descr = stringextract('item-description">', '</p>', rec) 
		descr = cleanhtml(descr); descr = mystrip(descr)
		PLog('Satz_Live:')
		PLog(href); PLog(img); PLog(title); PLog(descr); 
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s'}" % (urllib2.quote(href),
			urllib2.quote(title), img, urllib2.quote(descr))	
		addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=img, thumb=img, 
			fparams=fparams, summary=descr,  mediatype=mediatype)
		
	content =  blockextract('class="artdirect " >', page)
	PLog('content: ' + str(len(content)))	
	
	mediatype='' 		
	for rec in content:												# 2. redak. Beiträge (Vorschau)			
		href 	= stringextract('href="', '"', rec)
		href 	= ZDF_BASE + href
		
		img 	= stringextract('data-src="', '"', rec)
		title	= stringextract('title="', '"', rec)
		title	= "kommend: " + title
		descr	= stringextract('teaser-text" >', '</p>', rec)
		descr	= mystrip(descr); descr=unescape(descr); descr=repl_json_chars(descr);
		video	= stringextract('icon-301_clock icon">', '</dl>', rec)
		video	= mystrip(video); video=cleanhtml(video)
		if video:
			descr = "%s\n\n%s" % (descr, video)
		
		if '#skiplinks' in href or href == 'https://www.zdf.de/':
			continue
		PLog('Satz:')
		PLog(href); PLog(title); PLog(descr); PLog(video);
		fparams="&fparams={'title': '%s', 'path': '%s',  'img': '%s'}"	% (urllib2.quote(title), 
			urllib2.quote(href), urllib2.quote(img))
		addDir(li=li, label=title, action="dirList", dirID="ZDFSportLiveSingle", fanart=img, 
			thumb=img, fparams=fparams, tagline=descr )
			
	title = 'zurückliegende Sendungen'								# 3. weitere Sendungen
	url = 'https://www.zdf.de/sport/zdf-sportreportage'
	ID = 'ZDFSportLive'
	thumb=R("zdf-sportlive.png")
	fparams="&fparams={'url': '%s', 'title': '%s', 'ID': '%s'}" % (urllib2.quote(url), 
		urllib2.quote(title), ID)
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Sendungen", fanart=thumb, 
		thumb=thumb, fparams=fparams)
	
	#channel = 'Überregional'										# 4. zum Livestream - s.o.
	#onlySender = 'ZDFSportschau Livestream'	
	#img = R("zdf-sportlive.png")	
	#SenderLiveListe(title=channel, listname=channel, fanart=img, onlySender=onlySender)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#-------------------------
# holt von der aufgerufenen Seite den Titelbeitrag. Die restl. Videos der Seite
#	(Mehr Videos aus der Sendung) werden von ZDF_get_content ermittelt.
#	Abbruch, falls Titelbeitrag noch nicht verfügbar. 
def ZDFSportLiveSingle(title, path, img):
	PLog('ZDFSportLiveSingle:'); 
	title = UtfToStr(title)
	title_org = title
	ref_path = path

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
	videomodul = stringextract('class="b-video-module">', '</article>', page)
	if 'Beitragslänge:' not in videomodul:	 						# Titelvideo fehlt 
		descr = stringextract('"description": "', '"', page) 		# json-Abschnitt
		descr = unescape(descr)
		msg1 = 'Leider noch kein Video verfügbar. Vorabinfo:'
		msg2 = descr
		msg3 = ''
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 

	descr = stringextract('item-description" >', '</p>', videomodul) 
	descr = cleanhtml(descr); descr = mystrip(descr)
	descr = repl_json_chars(descr); 
	# Bsp.: datetime="2017-11-15T20:15:00.000+01:00">15.11.2017</time>
	datum_line =  stringextract('<time datetime="', '/time>', videomodul) 
	video_datum =  stringextract('">', '<', datum_line)
	video_time = datum_line.split('T')[1]
	video_time = video_time[:5]
	
	if video_datum and video_time:
		descr_display 	= "%s, %s Uhr \n\n%s" % (video_datum, video_time, descr)		
		descr 			= "%s, %s Uhr||||%s" % (video_datum, video_time, descr)		
	
	PLog('Satz:')
	PLog(path); PLog(title); PLog(descr); PLog(video_time);
	
	# 1. Titelbeitrag holen
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s'}" % (urllib2.quote(path),
		urllib2.quote(title), img, urllib2.quote(descr))	
	addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=img, thumb=img, 
		fparams=fparams, tagline=descr_display, mediatype=mediatype)
		
	# 2. restl. Videos holen (class="artdirect " >)
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=ref_path, ID='ZDFSportLive')	
	
	xbmcplugin.endOfDirectory(HANDLE)
	 			
####################################################################################################
def International(title):
	PLog('International:'); 
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	if title == 'ZDFenglish':
		path = 'https://www.zdf.de/international/zdfenglish'
	if title == 'ZDFarabic':
		path = 'https://www.zdf.de/international/zdfarabic'
		
	page, msg = get_page(path=path)		
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	 			
	li, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='International')
	
	PLog(page_cnt)
	# if offset:	Code entfernt, in Kodi nicht nutzbar
			
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
# Auswertung aller ZDF-Seiten
#	 
# 	ID='Search' od. 'VERPASST' - Abweichungen zu Rubriken + A-Z
#	Seiten mit Einzelvideos werden hier nicht erfasst - ev. vor
#		Aufruf Vorprüfung 'class="artdirect " >' durchführen
#	enthält "Inhaltstext im Voraus laden"

def ZDF_get_content(li, page, ref_path, ID=None):	
	PLog('ZDF_get_content:'); PLog(ID); PLog(ref_path)					
	PLog(len(page));
	# 09.01.2019 bis auf Weiteres enfernt (Probleme mit Rekursion):			
	# max_count = int(SETTINGS.getSetting('pref_maxZDFContent')) # max. Anzahl Elemente 
	max_count = 0
	PLog(max_count)
	page = UtfToStr(page)										# für Suche mit Umlauten
	
	Bilderserie = False	
	if ID == 'Bilderserien':									# Aufruf: ZDF_Search
		Bilderserie = True										# für Titelergänzung (Anz. Bilder)
		ID='DEFAULT'											# Sätze ohne aufnehmen														
	
	img_alt = teilstring(page, 'class=\"m-desktop', '</picture>') # Bildsätze für b-playerbox
		
	page_title = stringextract('<title>', '</title>', page)  # Seitentitel
	page_title = UtfToStr(page_title)
	page_title = page_title.strip()
	msg_notfound = ''
	if 'Leider kein Video verf' in page:					# Verfügbarkeit vor class="artdirect " >
		msg_notfound = 'Leider kein Video verfügbar'		# z.B. Ausblick auf Sendung
		if page_title:
			msg_notfound = 'Leider kein Video verfügbar zu: ' + page_title
						
	content =  blockextract('class="artdirect " >', page)
	if ID == 'NeuInMediathek':									# letztes Element entfernen (Verweis Sendung verpasst)
		content.pop()	
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
			# kann entfallen - Blockbildung mit class="content-box" inzw. möglich. Modul zdfneo.py entfernt.
			#	Zeilen hier ab 1.1.2018 löschen:
			#if ref_path.startswith('https://www.zdf.de/comedy/neo-magazin-mit-jan-boehmermann'): # neue ZDF-Seite
			#	import zdfneo
			#	items = zdfneo.neo_content(path=ref_path, ID=ID)		# Abschluss dort
			#	return li, page_cnt 		
	
	if msg_notfound:											# gesamte Seite nicht brauchbar		
		msg1 = msg_notfound
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li, 0
							
	if page.find('class="b-playerbox') > 0 and page.find('class="item-caption') > 0:  # mehrspaltig: Video gesamte Sendung?
		first_rec = img_alt +  stringextract('class="item-caption', 'data-tracking=', page) # mit img_alt
		content.insert(0, first_rec)		# an den Anfang der Liste
		# GNNPLog(content[0]) # bei Bedarf

	PLog(len(content))
	PLog("Mark1")

	mediatype=''									# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
			
	items_cnt=0									# listitemzähler
	for rec in content:	
		# loader:  enthält bei Suche Links auch wenn weiterer Inhalt fehlt. 
		#			Bei Verpasst u.a. enthält er keinen Link
		if 'class="loader"></span>Weitere laden' in rec: # Loader erreicht=Ende 
			href = stringextract('load-more-container">', 'class="loader">', rec)
			href = stringextract('href="', '"', href)
			PLog('href_loader:' + href)
			if href:
				return li, 'next'
		
		if 'data-module="plusbar"' not in rec:	
			pos = rec.find('</article>')		   	# Satz begrenzen - bis nächsten Satz nicht verwertbare 
			if pos > 0:								# 	Inhalte möglich
				rec = rec[0:pos]
			# PLog(rec)  # bei Bedarf
			
		if ID <> 'DEFAULT':					 			# DEFAULT: Übersichtsseite ohne Videos, Bsp. Sendungen A-Z
			if 'title-icon icon-502_play' not in rec :  # Videobeitrag? auch ohne Icon möglich
				if '>Videolänge:<' not in rec : 
					if '>Trailer<' not in rec : 		# Trailer o. Video-icon-502
						continue		
		multi = False			# steuert Mehrfachergebnisse 
				
		thumb 	= stringextract('data-src="', '"', rec)			# erstes img = größtes
		PLog('thumb: ' + thumb)
			
		if thumb.find('https://') == -1:	 # Bsp.: "./img/bgs/zdf-typical-fallback-314x314.jpg?cb=0.18.1787"
				thumb = ZDF_BASE + thumb[1:] # 	Fallback-Image  ohne Host
						
		teaser_label = stringextract('class=\"teaser-label\"', '</div>', rec)
		teaser_typ =  stringextract('<strong>', '</strong>', teaser_label)
		if teaser_typ == 'Beiträge':		# Mehrfachergebnisse ohne Datum + Uhrzeit
			multi = True
			summary = dt1 + teaser_typ 		# Anzahl Beiträge
		#PLog('teaser_typ: ' + teaser_typ)			
			
		subscription = stringextract('is-subscription=\"', '\"', rec)	# aus plusbar-Block	
		PLog(subscription)
		if subscription == 'true':						
			multi = True
			teaser_count = stringextract('</span>', '<strong>', teaser_label)	# bei Beiträgen
			stage_title = stringextract('class=\"stage-title\"', '</h1>', rec)  
			summary = teaser_count + ' ' + teaser_typ 

		# Titel	
		href_title = stringextract('<a href="', '>', rec)		# href-link hinter teaser-cat kann Titel enthalten
		href_title = stringextract('title="', '"', href_title)
		href_title = unescape(href_title)
		href_title = UtfToStr(href_title)
		PLog('href_title: ' + href_title)
		if 	href_title == 'ZDF Livestream' or href_title == 'Sendung verpasst':
			continue
			
		# Pfad				
		plusbar_title = stringextract('plusbar-title="', '"', rec)	# Bereichs-, nicht Einzeltitel, nachrangig
		# plusbar_path = stringextract('plusbar-path=\"', '\"', rec)    # path ohne http(s)
		path =  stringextract('plusbar-url="', '"', rec)				# plusbar nicht vorh.? - sollte nicht vorkommen
		PLog('path: ' + path); PLog('ref_path: %s' % ref_path)	
		
		if path == '' or path == ref_path:					# kein Pfad oder Selbstreferenz
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
							
		duration = stringextract('Videolänge:', 'Datum', rec) 		# Länge - 1. Variante 
		duration = stringextract('m-border">', '</', duration)		# Ende </dd> od. </dt>
		if duration == '':
			PLog("Videolänge:")
			duration = stringextract('Videolänge:', 'min', rec) 	# Länge - 2. Variante bzw. fehlend
			duration = "%s min" % mystrip(duration) 
		if 	'<strong>Livestream</strong>' in rec:
			duration = '[COLOR red]Livestream[/COLOR]'	
		PLog('duration: ' + duration);
		
		pic_cnt = stringextract('Anzahl Bilder:', '<dt class', rec)	# Bilderzahl bei Bilderserien
		pic_cnt = stringextract('">', '</', pic_cnt)				# Ende </dd> od. </dt>
		PLog('Bilder: ' + pic_cnt);
			
		title = href_title 
		if title == '':
			title = plusbar_title
		if Bilderserie == True and pic_cnt:
			title = title + " | %s"   % pic_cnt
		if title.startswith(' |'):
			title = title[2:]				# Korrektur
			
		category = stringextract('teaser-cat-category">', '</span>', rec)
		category = mystrip(category)
		brand = stringextract('teaser-cat-brand">', '</span>', rec)
		brand = mystrip(brand)	
			
		tagline = video_datum
		video_time = video_time.replace('00:00', '')		# ohne Uhrzeit
		if video_time:
			tagline = tagline + ' | ' + video_time
		if duration:
			tagline = tagline + ' | ' + duration
		if category:
			tagline = tagline + ' | ' + category
		if brand:
			tagline = tagline + ' | ' + brand
		if tagline.startswith(' |'):
			tagline = tagline[2:]			# Korrektur
			
		descr = stringextract('description">', '<', rec)
		if descr == '':
			descr = stringextract('teaser-text">', '<', rec)
		descr = mystrip(descr)
		# PLog('descr:' + descr)		# UnicodeDecodeError möglich
		if descr:
			summary = descr
		else:
			summary = href_title
			
		if 	'title-icon icon-502_play' in rec == False and 'icon-301_clock icon' in rec == False:
			PLog('icon-502_play und icon-301_clock nicht gefunden')
			if ID == 'Bilderserien': 	# aber Bilderserien aufnehmen
				PLog('Bilderserien')
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
		
		title = title.strip()
		title = unescape(title)	
		summary = unescape(summary)
		summary = cleanhtml(summary)		
		tagline = unescape(tagline)
		tagline = cleanhtml(tagline)
		
		title=repl_json_chars(title)						# json-komp. für func_pars in router()
		summary=repl_json_chars(summary)					# dto.
		tagline=repl_json_chars(tagline)					# dto.
		
		title = UtfToStr(title); summary = UtfToStr(summary); tagline = UtfToStr(tagline);
		if 'Hörfassung' in title or 'Audiodeskription' in title:				# Filter
			if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true':
				continue		
			if SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
				continue		
			
		PLog('neuer Satz')
		PLog(thumb);PLog(path);PLog(title);PLog(summary);PLog(tagline); PLog(multi);
		 
		if multi == True:
			fparams="&fparams={'url': '%s', 'title': '%s', 'ID': '%s'}" % (urllib2.quote(path), 
				urllib2.quote(title), ID)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Sendungen", fanart=thumb, 
				thumb=thumb, fparams=fparams, summary=summary, tagline=tagline)
		else:											# Einzelseite	
														# summary (Inhaltstext) im Voraus holen falls 
														#	 leer oder identisch mit title:	
			tag_par= "%s||||%s" % (tagline, summary)	# # -> ZDF_getVideoSources ohne Voraustext								
			if summary == '' or summary == title:	
				if SETTINGS.getSetting('pref_load_summary') == 'true':
					summ_txt = get_summary_pre(path, 'ZDF')
					if 	summ_txt:
						tag_par= "%s\n\n%s" % (tagline, summ_txt)
						tag_par = tag_par.replace('\n', '||')
						summary = summ_txt			
			
			PLog("summary: " + summary); PLog("tagline: " + tagline)
			tagline = UtfToStr(tagline)
			tagline=repl_json_chars(tagline)		# json-komp. für func_pars in router()	
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s'}" % (urllib2.quote(path),
				urllib2.quote(title), thumb, urllib2.quote(tag_par))	
			addDir(li=li, label=title, action="dirList", dirID="ZDF_getVideoSources", fanart=thumb, thumb=thumb, 
				fparams=fparams, summary=summary,  tagline=tagline, mediatype=mediatype)
				
		items_cnt = items_cnt+1
	
		'''' 09.01.2019 bis auf Weiteres enfernt (Probleme mit Rekursion)  - s.o.
		# Zahl der Seitenelemente nicht mehr berücksichtigt - nicht alle sind listenfähig
		if max_count:					# summary + tagline werden als Info-Items nicht mitgezählt
			# Mehr Seiten anzeigen:		# 'Mehr...'-Callback durch Aufrufer	
			PLog("items_cnt: "  + str(items_cnt))
			if items_cnt  >= max_count or items_cnt > len(content):	# Mehr, wenn max_count erreicht
				offset = offset + max_count-1
				break					# Schleife beenden
		''' 
		# break # Test 1. Satz
		
	return li, page_cnt 
	
#-------------
####################################################################################################
# Subtitles: im Kopf der videodat-Datei enthalten (Endung .vtt). Leider z.Z. keine Möglichkeit
#	bekannt, diese in Plex-Plugins einzubinden. Umsetzung in Kodi-Version OK (s. get_formitaeten).
# Ladekette für Videoquellen s. get_formitaeten
# 
def ZDF_getVideoSources(url, title, thumb, tagline, segment_start=None, segment_end=None, Merk='false'):
	PLog('ZDF_getVideoSources:'); PLog(url); PLog(tagline); 
	PLog(title)
				
	li = xbmcgui.ListItem()
	urlSource = url 		# für ZDFotherSources

	page, msg = get_page(url)
	if page == '':
		msg1 = 'ZDF_getVideoSources: Problem beim Abruf der Videoquellen.'
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
			
	# -- Start Vorauswertungen: Bildgalerie u.ä. 
	if segment_start and segment_end:				# Vorgabe Ausschnitt durch ZDF_get_content 
		pos1 = page.find(segment_start); pos2 = page.find(segment_end);  # bisher: b-group-persons
		PLog(pos1);PLog(pos2);
		page = page[pos1:pos2]
		li = ZDF_Bildgalerie(li=li, page=page, mode=segment_start, title=title)
		return li

	if page.find('data-module=\"zdfplayer\"') == -1:		# Vorprüfung auf Videos
		if page.find('class=\"b-group-contentbox\"') > 0:	# keine Bildgalerie, aber ähnlicher Inhalt
			li = ZDF_Bildgalerie(li=li, page=page, mode='pics_in_accordion-panels', title=title)		
			return li		
		if page.find('class=\"content-box gallery-slider-box') >= 0:		# Bildgalerie
			li = ZDF_Bildgalerie(li=li, page=page, mode='is_gallery', title=title)
			return li
		
	# ab 08.10.2017 dyn. ermitteln (wieder mal vom ZDF geändert)
	# 12.01.2018: ZDF verwendet nun 2 verschiedene Token - s. get_formitaeten: 1 x profile_url, 1 x videodat_url
	apiToken1 = stringextract('apiToken: \'', '\'', page) 
	apiToken2 = stringextract('"apiToken": "', '"', page)
	PLog('apiToken1: ' + apiToken1); PLog('apiToken2: ' + apiToken2)
					
	# -- Ende Vorauswertungen
			
	li = home(li, ID='ZDF')										# Home-Button - nach Bildgalerie 

	# key = 'page_GZVS'											# entf., in get_formitaeten nicht mehr benötigt
	# Dict[key] = page	
	sid = stringextract("docId: \'", "\'", page)				# Bereich window.zdfsite
	formitaeten,duration,geoblock, sub_path = get_formitaeten(sid, apiToken1, apiToken2)	# Video-URL's ermitteln
	# PLog(formitaeten)

	if formitaeten == '':										# Nachprüfung auf Videos
		msg1 = 'Video nicht vorhanden / verfügbar.'
		msg2 = 'Titel: %s' % urllib2.unquote(title)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, "")
		return li
				
	if tagline:
		if 'min' in tagline == False:	# schon enthalten (aus ZDF_get_content)?
			tagline = tagline + " | " + duration
	else:
		tagline = duration

	# Sofortstart: Behandlung in show_formitaeten
	only_list = ["h264_aac_ts_http_m3u8_http"]					# Video-Items erstellen: m3u8-Formate
	li, download_list = show_formitaeten(li=li, title_call=title, formitaeten=formitaeten, tagline=tagline,
		thumb=thumb, only_list=only_list,geoblock=geoblock, sub_path=sub_path, Merk=Merk)
	if 	download_list == '':	# Sofortstart erfolgt, raus
		return	  
		
	title_oc='weitere Video-Formate'							# Video-Items erstellen: weitere Formate
	if SETTINGS.getSetting('pref_use_downloads'):	
		title_oc=title_oc + ' und Download'
	PLog("title_oc: " + title_oc)
		
	PLog(title); PLog(title_oc); PLog(tagline); PLog(sid); 
	title = UtfToStr(title); tagline = UtfToStr(tagline); 
		
	if SETTINGS.getSetting('pref_video_direct') == 'false':	# ZDFotherSources nicht bei Sofortstart zeigen
		# li = Parseplaylist(li, videoURL, thumb)	# hier nicht benötigt - das ZDF bietet bereits 3 Auflösungsbereiche
		fparams="&fparams={'title': '%s', 'tagline': '%s', 'thumb': '%s', 'sid': '%s', 'apiToken1': '%s', 'apiToken2': '%s'}" \
			% (urllib2.quote(title), urllib2.quote(tagline), urllib2.quote(thumb), sid, apiToken1, apiToken2)
		addDir(li=li, label=title_oc, action="dirList", dirID="ZDFotherSources", fanart=thumb, thumb=thumb, fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#-------------------------
# weitere Videoquellen - Übergabe der Webseite in Dict[key]		
def ZDFotherSources(title, tagline, thumb, sid, apiToken1, apiToken2):
	PLog('ZDFotherSources:'); 
	title_org = title		# Backup für Textdatei zum Video
	summary_org = tagline	# Tausch summary mit tagline (summary erstrangig bei Wiedergabe)
	PLog(title_org)

	li = xbmcgui.ListItem()
	li = home(li,ID='ZDF')										# Home-Button
		
	formitaeten,duration,geoblock, sub_path = get_formitaeten(sid, apiToken1, apiToken2)	# Video-URL's ermitteln
	# PLog(formitaeten)
	
	if formitaeten == '':										# Nachprüfung auf Videos
		msg1 = 'Video nicht vorhanden / verfügbar'
		msg2 = 'Video: %s' % title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, "")
		return li

	if tagline:
		if 'min' in tagline == False:	# schon enthalten (aus ZDF_get_content)?
			tagline = tagline + " | " + duration
	else:
		tagline = duration

	only_list = ["h264_aac_mp4_http_na_na", "vp8_vorbis_webm_http_na_na", "vp8_vorbis_webm_http_na_na"]
	li, download_list = show_formitaeten(li=li, title_call=title_org, formitaeten=formitaeten, tagline=tagline,
		thumb=thumb, only_list=only_list, geoblock=geoblock, sub_path=sub_path)		  
					
	# high=0: 	1. Video bisher höchste Qualität:  [progressive] veryhigh
	li = test_downloads(li,download_list,title_org,summary_org,tagline,thumb,high=0)  # Downloadbutton(s)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
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
	PLog(apiToken1); PLog(apiToken2);
	title = UtfToStr(sid); title = UtfToStr(apiToken1); title = UtfToStr(apiToken2)
	
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
	if page == '':	# Abbruch - ev. Alternative ngplayer_2_3 versuchen
		PLog('profile_url: Laden fehlgeschlagen')
		return '', '', '', ''
	PLog("page_json: " + page[:40])
														# Videodaten ermitteln:
	pos = page.rfind('mainVideoContent')				# 'mainVideoContent' am Ende suchen
	page_part = page[pos:]
	PLog("page_part: " + page_part[:40])			# bei Bedarf
	# neu ab 20.1.2016: uurl-Pfad statt ptmd-Pfad ( ptmd-Pfad fehlt bei Teilvideos)
	# neu ab 19.04.2018: Videos ab heute auch ohne uurl-Pfad möglich, Code einschl. Abbruch entfernt - s.a. KIKA_und_tivi.
	# 18.10.2018: Code für old_videodat_url entfernt (../streams/ptmd":).
	
	ptmd_player = 'ngplayer_2_3'							
	videodat_url = stringextract('ptmd-template": "', '",', page_part)
	videodat_url = videodat_url.replace('{playerId}', ptmd_player) 				# ptmd_player injiziert 
	videodat_url = 'https://api.zdf.de' + videodat_url
	# videodat_url = 'https://api.zdf.de/tmd/2/portal/vod/ptmd/mediathek/'  	# unzuverlässig
	PLog('videodat_url: ' + videodat_url)	

	# apiToken2 aus ZDF_getVideoSources. header ohne quotes in get_page leer 
	# kompl. Header für Modul requests, für urllib2.urlopen reichen Api-Auth + Host
	#header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de', 'Accept-Encoding': 'gzip, deflate, sdch, br', \
	#	'Accept':'application/vnd.de.zdf.v1.0+json'}" % apiToken2
	header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken2
	page, msg	= get_page(path=videodat_url, header=header, JsonPage=True)
	PLog("request_json: " + page[:40])

	if page == '':	# Abbruch - ev. Alternative ngplayer_2_3 versuchen
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
		# sub_xml_path = stringextract('\"uri\": \"', '\"', sub_xml)# xml-Format
		sub_vtt_path = stringextract('\"uri\": \"', '\"', sub_vtt)	
		# PLog('Untertitel xml:'); PLog(sub_xml_path)
		PLog('Untertitel vtt:'); PLog(sub_vtt_path)
		
		# 20.01.2019 Pfad + Url in PlayVideo via listitem.setInfo direkt übergeben
		local_path = "%s/%s" % (SUBTITLESTORE, sub_vtt_path.split('/')[-1])
		local_path = local_path.replace('.vtt', '.sub')				# Endung für Kodi anpassen
		local_path = os.path.abspath(local_path)
		try:
			if os.path.isfile(local_path) == False:					# schon vorhanden?
				urllib.urlretrieve(sub_vtt_path, local_path)
		except Exception as exception:
			local_path = ''
			PLog(str(exception))
		sub_path = '%s|%s' % (local_path, sub_vtt_path)						
		PLog(sub_path)
				
	duration = stringextract('duration',  'fsk', page)	# Angabe im Kopf, sec/1000
	duration = stringextract('"value":',  '}', duration).strip()
	PLog(duration)	
	if duration:
		duration = (int(duration) / 1000) / 60			# Rundung auf volle Minuten reicht hier 
		duration = str(duration) + " min"	
	PLog('duration: ' + duration)
	PLog('page_formitaeten: ' + page[:100])		
	formitaeten = blockextract('formitaeten', page)		# Video-URL's ermitteln
	PLog('formitaeten: ' + str(len(formitaeten)))
	# PLog(formitaeten[0])								# bei Bedarf
				
	geoblock =  stringextract('geoLocation',  '}', page) 
	geoblock =  stringextract('"value": "',  '"', geoblock).strip()
	PLog('geoblock: ' + geoblock)
	if 	geoblock:								# i.d.R. "none", sonst "de" - wie bei ARD verwenden
		if geoblock == 'de':			# Info-Anhang für summary 
			geoblock = ' | Geoblock DE!'
		if geoblock == 'dach':			# Info-Anhang für summary 
			geoblock = ' | Geoblock DACH!'
	else:
		geoblock == ''

	PLog('Ende get_formitaeten:')
	return formitaeten, duration, geoblock, sub_path  

#-------------------------
# 	Ausgabe der Videoformate
#	
def show_formitaeten(li, title_call, formitaeten, tagline, thumb, only_list, geoblock, sub_path, Merk='false'):	
	PLog('show_formitaeten:')
	PLog(only_list); PLog(title_call); PLog(tagline)
	# PLog(formitaeten)		# bei Bedarf

	title_call = urllib2.unquote(title_call)
	title_call = UtfToStr(title_call); tagline = UtfToStr(tagline); geoblock = UtfToStr(geoblock)
	if 	title_call != tagline:		
		Plot	 = "%s\n\n%s" % (title_call, tagline)
		Plot_par = "%s||||%s" % (title_call, tagline)		# || Code für LF (\n scheitert in router)
	else:
		Plot	 = title_call
		Plot_par = title_call
	
	i = 0 	# Titel-Zähler für mehrere Objekte mit dem selben Titel (manche Clients verwerfen solche)
	download_list = []		# 2-teilige Liste für Download: 'summary # url'	
	for rec in formitaeten:									# Datensätze gesamt, Achtung unicode!
		# PLog(rec)		# bei Bedarf
		typ = stringextract('"type": "', '"', rec)
		typ = typ.replace('[]', '').strip()
		facets = stringextract('"facets": ', ',', rec)	# Bsp.: "facets": ["progressive"]
		facets = facets.replace('"', '').replace('\n', '').replace(' ', '') 
		PLog(typ); PLog(facets)
		
		# PLog(typ in only_list)
		if (typ in only_list) == True:								
			audio = blockextract('"audio":', rec)			# Datensätze je Typ
			# PLog(audio)	# bei Bedarf
			for audiorec in audio:					
				url = stringextract('"uri": "',  '"', audiorec)			# URL
				url = url.replace('https', 'http')
				quality = stringextract('"quality": "',  '"', audiorec)
				quality = UtfToStr(quality)
				PLog(url); PLog(quality)
				
				i = i +1
				if url:		
					if url.find('master.m3u8') > 0:			# m3u8 enthält alle Auflösungen
						if SETTINGS.getSetting('pref_video_direct') == 'true'or Merk == 'true':	# Sofortstart
							PLog('Sofortstart: show_formitaeten')
							PlayVideo(url=url, title=title_call, thumb=thumb, Plot=Plot_par, sub_path=sub_path, Merk=Merk)
							return li, ''	# sauber raus in ZDF_getVideoSources
						
						title = '%s. %s [m3u8] Bandbreite und Aufloesung automatisch | %s' % (str(i), quality, title_call)
						title = UtfToStr(title)

						#   "auto"-Button + Ablage master.m3u8:
						li = ParseMasterM3u(li=li, url_m3u8=url, thumb=thumb, title=title, tagline=tagline, descr=Plot_par,
							sub_path=sub_path)	
					else:									# m3u8 enthält Auflösungen high + med
						title = 'Qualitaet: ' + quality + ' | Typ: ' + typ + ' ' + facets 
						title = '%s. Qualitaet: %s | Typ: %s %s' % (str(i), quality, typ, facets)
						title = UtfToStr(title)
						download_list.append(title + '#' + url)				# Download-Liste füllen	
						tagline	 = tagline.replace('||','\n')				# s. tagline in ZDF_get_content
						fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
							(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(thumb), 
							urllib.quote_plus(Plot_par), urllib.quote_plus(sub_path), Merk)	
						addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
							mediatype='video', tagline=tagline) 
													
	return li, download_list
#-------------------------
def ZDF_Bildgalerie(li, page, mode, title):	# keine Bildgalerie, aber ähnlicher Inhalt
	PLog('ZDF_Bildgalerie:'); PLog(mode); PLog(title)
	title_org = title
	page = UtfToStr(page)
	
	# neue Listitems
	li = xbmcgui.ListItem()
	li = home(li, ID="ZDF")						# Home-Button
	
	if mode == 'is_gallery':							# "echte" Bildgalerie
		content =  stringextract('class=\"content-box gallery-slider-box', 'title=\"Bilderserie schließen\"', page)
		content =  blockextract('class=\"img-container', content)   					# Bild-Datensätze
	if mode == 'pics_in_accordion-panels':				# Bilder in Klappboxen	
		content =  stringextract('class=\"b-group-contentbox\"', '</section>', page)
		content =  blockextract('class=\"accordion-panel\"', content)
	if mode == '<article class="b-group-persons">':		# ZDF-Korrespondenten, -Mitarbeiter,...	
		content = page	
		content =  blockextract('guest-info m-clickarea', content)
			
	PLog(len(content))
	if len(content) == 0:										
		msg1 = 'Keine Bilder gefunden.'
		PLog(msg1)
		msg2 = 'ZDF_Bildgalerie, mode = %s' % mode
		msg3 = title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
	
	fname = make_filenames(title)			# Ablage: Titel + Bildnr
	fpath = '%s/%s' % (SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li	

	image = 0
	for rec in content:
		# PLog(rec)  # bei Bedarf
		summ = ''; 
		if mode == 'is_gallery':				# "echte" Bildgalerie
			img_src =  stringextract('data-srcset="', ' ', rec)			
			item_title = stringextract('class="item-title', 'class="item-description">', rec)  
			teaser_cat =  stringextract('class="teaser-cat">', '</span>', item_title)  
			teaser_cat = teaser_cat.strip()			# teaser_cat hier ohne itemprop
			if teaser_cat.find('|') > 0:  			# über 3 Zeilen verteilt
				tclist = teaser_cat.split('|')
				teaser_cat = str.strip(tclist[0]) + ' | ' + str.strip(tclist[1])			# zusammenführen
			#PLog(teaser_cat)					
			descript = stringextract('class=\"item-description\">', '</p', rec)
			pos = descript.find('<span')			# mögliche Begrenzer: '</p', '<span'
			if pos >= 0:
				descript = descript[0:pos]
			descript = descript.strip()
			#PLog(descript)					

			title_add = stringextract('data-plusbar-title=\"', ('\"'), rec)	# aus Plusbar - im Teaser schwierig
			title = teaser_cat
			if title_add:
				title = title + ' |' + title_add
			if title.startswith(' |'):
				title = title[2:]				# Korrektur
			if descript:		
				summ = descript
				
		if mode == 'pics_in_accordion-panels':				# Bilder in Klappboxen
			img_src =  stringextract('data-srcset=\"', ' ', rec)
			title =  stringextract('class=\"shorter\">', '<br/>', rec) 
			summ = stringextract('p class=\"text\">', '</p>', rec) 		
			summ = cleanhtml(summ)
		
		if mode == '<article class=\"b-group-persons\">':
			img_src = stringextract('data-src=\"', '\"', rec)
			
			guest_name =  stringextract('trackView\": true}\'>', '</button>', rec)
			guest_name = guest_name.strip()
			guest_title =  stringextract('guest-title\"><p>', '</p>', rec)
			guest_title = unescape(guest_title)
			title = guest_name + ': ' + guest_title						
			summ = stringextract('desc-text\">', '</p>', rec)
			summ = summ.strip()
			summ = cleanhtml(summ)
			
		if img_src == '':									# Sicherung			
			msg1 = 'Problem in Bildgalerie: Bild nicht gefunden'
			PLog(msg1)
					
		if img_src:
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			pic_name 	= 'Bild_%04d.jpg' % (image+1)		# Bildname
			local_path 	= "%s/%s" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d" % (image+1)
			PLog("Bildtitel: " + title)
			title = UtfToStr(title)
			title = unescape(title)
			
			thumb = ''
			local_path = os.path.abspath(local_path)
			if os.path.isfile(local_path) == False:			# schon vorhanden?
				try:
					urllib.urlretrieve(img_src, local_path)
					thumb = local_path
				except Exception as exception:
					PLog(str(exception))	
			else:		
				thumb = local_path
				
			title_org = UtfToStr(title_org)			
			tagline = unescape(title_org); tagline = cleanhtml(tagline)
			summ = unescape(summ)
			PLog('neu:');PLog(title);PLog(thumb);PLog(summ[0:40]);
			if thumb:
				fparams="&fparams={'path': '%s', 'single': 'True'}" % urllib2.quote(local_path)
				addDir(li=li, label=title, action="dirList", dirID="ZDFSlideShow", 
					fanart=thumb, thumb=thumb, fparams=fparams, summary=summ, tagline=tagline)

			image += 1
			
	if image > 0:		
		fparams="&fparams={'path': '%s'}" % urllib2.quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="ZDFSlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern
	
#-----------------------
#  PhotoObject fehlt in kodi - wir speichern die Bilder in SLIDESTORE und
#	übergeben an xbmc.executebuiltin('SlideShow..
#  ClearUp in SLIDESTORE s. Modulkopf
#  S.a. ARD_Bildgalerie/Hub + SlideShow
def ZDFSlideShow(path, single=None):
	PLog('SlideShow: ' + path)
	local_path = os.path.abspath(path)
	if single:							# Einzelbild	
		return xbmc.executebuiltin('ShowPicture(%s)' % local_path)
	else:
		PLog(local_path)
		return xbmc.executebuiltin('SlideShow(%s, %s)' % (local_path, 'notrandom'))
	 
####################################################################################################
def Parseplaylist(li, url_m3u8, thumb, geoblock, descr, tagline='', summary='', sub_path=''):	
#	# master.m3u8 auswerten, Url muss komplett sein. container muss nicht leer ein (siehe SingleSendung)
#  1. Besonderheit: in manchen *.m3u8-Dateien sind die Pfade nicht vollständig,
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
#  2. Besonderheit: fast identische URL's zu einer Auflösung (...av-p.m3u8, ...av-b.m3u8) Unterschied n.b.
#  3. Besonderheit: für manche Sendungen nur 1 Qual.-Stufe verfügbar (Bsp. Abendschau RBB)
#  4. Besonderheit: manche Playlists enthalten zusätzlich abgeschaltete Links, gekennzeichnet mit #. Fehler Webplayer:
#		 crossdomain access denied. Keine Probleme mit OpenPHT und VLC - betr. nur Plex.
#  10.08.2017 Filter für Video-Sofort-Format - wieder entfernt 17.02.2018
#
	PLog ('Parseplaylist: ' + url_m3u8)

	if SETTINGS.getSetting('pref_video_direct') == 'true':
		return li

	tagline=UtfToStr(tagline); summary=UtfToStr(summary); descr=UtfToStr(descr);
	playlist = ''
	# seit ZDF-Relaunch 28.10.2016 dort nur noch https
	if url_m3u8.find('http://') == 0 or url_m3u8.find('https://') == 0:		# URL oder lokale Datei?			
		playlist, msg = get_page(path=url_m3u8)								# URL
		if playlist == '':
			line1 = 'Playlist kann nicht geladen werden.'
			line2 = 'URL: %s '	% (url_m3u8)
			line3 = 'Fehler: %s'	% (msg)
			xbmcgui.Dialog().ok(ADDON_NAME, line1, line2, line3)
			return li			
	else:																	# lokale Datei	
		fname =  os.path.join(M3U8STORE, url_m3u8) 
		playlist = RLoad(fname, abs_path=True)					
	 
	PLog('playlist: ' + playlist[:100])		# bei Bedarf
	lines = playlist.splitlines()
	lines.pop(0)		# 1. Zeile entfernen (#EXTM3U)
	BandwithOld 	= ''	# für Zwilling -Test (manchmal 2 URL für 1 Bandbreite + Auflösung) 
	thumb_org		= thumb # sichern
	i = 0; li_cnt = 1
	#for line in lines[1::2]:	# Start 1. Element, step 2
	for line in lines:	
		line = lines[i].strip()
		# PLog(line)		# bei Bedarf
		if line.startswith('#EXT-X-STREAM-INF'):# tatsächlich m3u8-Datei?
			url = lines[i + 1].strip()	# URL in nächster Zeile
			PLog(url)
			Bandwith = GetAttribute(line, 'BANDWIDTH')
			Resolution = GetAttribute(line, 'RESOLUTION')
			try:
				BandwithInt	= int(Bandwith)
			except:
				BandwithInt = 0
			if Resolution:	# fehlt manchmal (bei kleinsten Bandbreiten)
				Resolution = 'Aufloesung ' + Resolution
			else:
				Resolution = 'Aufloesung unbekannt'	# verm. nur Ton? CODECS="mp4a.40.2"
			Codecs = GetAttribute(line, 'CODECS')
			# als Titel wird die  < angezeigt (Sender ist als thumb erkennbar)
			title='Bandbreite ' + Bandwith
			if url.find('#') >= 0:	# Bsp. SR = Saarl. Rundf.: Kennzeichnung für abgeschalteten Link
				Resolution = 'zur Zeit nicht verfügbar!'
			if url.startswith('http') == False:   		# relativer Pfad? 
				pos = url_m3u8.rfind('/')				# m3u8-Dateinamen abschneiden
				url = url_m3u8[0:pos+1] + url 			# Basispfad + relativer Pfad
			if Bandwith == BandwithOld:	# Zwilling -Test
				title = 'Bandbreite ' + Bandwith + ' (2. Alternative)'
				
			PLog(thumb); PLog(Resolution); PLog(BandwithInt); 
			Resolution=UtfToStr(Resolution); geoblock=UtfToStr(geoblock);
			thumb=thumb_org
			if BandwithInt and BandwithInt <=  100000: 		# vermutl. nur Audio (Bsp. ntv 48000, ZDF 96000)
				Resolution = Resolution + ' (vermutlich nur Audio)'
				thumb=R(ICON_SPEAKER)
				
			lable = Resolution+geoblock						# Kodi: statt summary + tagline in Plex
			title =  UtfToStr(title)
			lable = "%s. %s | %s" % (str(li_cnt), title, lable)
			
			# quote für url erforderlich wg. url-Inhalt "..sd=10&rebase=on.." - das & erzeugt in router
			#	neuen Parameter bei dict(parse_qsl(paramstring)
			Plot="%s||||%s" % (tagline, descr)
			descr=summary.replace('||', '\n')		
		
			if descr.strip() == '|':			# ohne EPG: EPG-Verbinder entfernen
				descr=''
			
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
				(urllib.quote_plus(url), title, urllib.quote_plus(thumb), urllib.quote_plus(Plot), 
				urllib.quote_plus(sub_path))
			addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
				mediatype='video', tagline=tagline, summary=descr) 
							
			BandwithOld = Bandwith												
		i = i + 1				# Index für URL
		li_cnt = li_cnt + 1  	# Listitemzähler
  	
	if i == 0:	# Fehler
		line1 = 'Kennung #EXT-X-STREAM-INF fehlt oder'
		line2 = 'den Pfaden fehlt http / https'
		xbmcgui.Dialog().ok(ADDON_NAME, line1, line2)			
	
	return li
		    
####################################################################################################
#						Hilfsfunktionen - für Kodiversion augelagert in Modul util.py
####################################################################################################
# Bsp. paramstring (ab /?action):
#	url: plugin://plugin.video.ardundzdf/?action=dirList&dirID=Main_ARD&
#	fanart=/resources/images/ard-mediathek.png&thumb=/resources/images/ard-mediathek.png&
#	params={&name=ARD Mediathek&sender=ARD-Alle:ard::ard-mediathek.png}
#---------------------------------------------------------------- 
def router(paramstring):
	# paramstring: Dictionary mit
	# {<parameter>: <value>} Elementen
	paramstring = urllib.unquote_plus(paramstring)
	PLog(' router_params1: ' + paramstring)
		
	if paramstring:		
		params = dict(parse_qsl(paramstring[1:]))
		PLog(' router_params_dict: ' + str(params))
		try:
			if params['content_type'] == 'video':		# Auswahl im Addon-Menü
				Main()
			PLog(' router action: ' + params['action']) # hier immer action="dirList"
			PLog(' router dirID: ' + params['dirID'])
			PLog(' router fparams: ' + params['fparams'])
		except Exception as exception:
			PLog(str(exception))

		if params['action'] == 'dirList':			# Aufruf Directory-Listing
			newfunc = params['dirID']
			func_pars = params['fparams']

			# Funktionsaufrufe + Parameterübergabe via Var's 
			#	s. 00_Migration_PLEXtoKodi.txt
			# Modulpfad immer ab resources - nicht verkürzen.
			if '.' in newfunc:						# Funktion im Modul, Bsp.:
				l = newfunc.split('.')				# Bsp. resources.lib.updater.update
				PLog(l)
				newfunc =  l[-1:][0]				# Bsp. updater
				dest_modul = '.'.join(l[:-1])
				PLog(' router dest_modul: ' + str(dest_modul))
				PLog(' router newfunc: ' + str(newfunc))
			
				func = getattr(sys.modules[dest_modul], newfunc)		
			else:
				func = getattr(sys.modules[__name__], newfunc)	# Funktion im Haupt-PRG OK		

			PLog(' router func_getattr: ' + str(func))		
			if func_pars != '""':		# leer, ohne Parameter?	
				# PLog(' router func_pars: Ruf mit func_pars')
				# func_pars = urllib.unquote_plus(func_pars)		# quotierte url auspacken - entf.
				PLog(' router func_pars unquote_plus: ' + str(func_pars))
				try:
					# Problem (spez. Windows): Parameter mit Escapezeichen (Windows-Pfade) müssen mit \\
					#	behandelt werden und werden dadurch zu unicode-Strings. Diese benötigen in den
					#	Funktionen eine UtfToStr-Behandlung.
					# Keine /n verwenden (json.loads: need more than 1 value to unpack)
					func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
					func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
					func_pars = func_pars.decode(encoding="utf-8")  
					
					PLog("json.loads func_pars: " + func_pars)
					PLog('json.loads func_pars type: ' + str(type(func_pars)))
					func_pars = func_pars.encode("utf-8")			# entf.
					mydict = json.loads(func_pars)
					PLog("mydict: " + str(mydict)); PLog(type(mydict))
				except:
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


PluginAbsPath = os.path.dirname(os.path.abspath(__file__))
PLog('PluginAbsPath: ' + PluginAbsPath)

PLog('Addon: Start')
if __name__ == '__main__':
	try:
		router(sys.argv[2])
	except Exception as e: 
		msg = str(e)
		PLog('network_error: ' + msg)
		# xbmcgui.Dialog().ok(ADDON_NAME, 'network_error', msg)

























