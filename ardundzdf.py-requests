# -*- coding: utf-8 -*-
# XBM
import xbmc	
import xbmcaddon
import xbmcplugin		
import xbmcgui

# Python
import string
import random			# Zufallswerte für rating_key
import urllib			# urllib.quote()
from urlparse import parse_qsl
from urllib import urlencode
import urllib2			# urllib2.Request
import requests			# urllib2.Request: bei kodi manchmal errno(0) (https)
import ssl				# HTTPS-Handshake
import os, subprocess 	# u.a. Behandlung von Pfadnamen
import shlex			# Parameter-Expansion für subprocess.Popen (os != windows)
import sys				# Plattformerkennung
import shutil			# Dateioperationen
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import datetime, time
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte

# Pluginmodule + Funktionsziele
import resources.lib.util as util
PLog=util.PLog;  home=util.home;  Dict=util.Dict;  name=util.name; 
UtfToStr=util.UtfToStr;  addDir=util.addDir;  get_page=util.get_page; 
img_urlScheme=util.img_urlScheme;  R=util.R;  RLoad=util.RLoad;  RSave=util.RSave; 
GetAttribute=util.GetAttribute;  NotFound=util.NotFound;  CalculateDuration=util.CalculateDuration;  
teilstring=util.teilstring; repl_dop=util.repl_dop;  repl_char=util.repl_char;  mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract;  blockextract=util.blockextract; 
teilstring=util.teilstring;  repl_dop=util.repl_dop; cleanhtml=util.cleanhtml;  decode_url=util.decode_url;  
unescape=util.unescape;  mystrip=util.mystrip; make_filenames=util.make_filenames;  transl_umlaute=util.transl_umlaute;  
humanbytes=util.humanbytes;  time_translate=util.time_translate; get_keyboard_input=util.get_keyboard_input; 
ClearUp=util.ClearUp; repl_json_chars=util.repl_json_chars; seconds_translate=util.seconds_translate;


import resources.lib.updater 			as updater		
import resources.lib.zdfmobile
import resources.lib.EPG				as EPG	
import resources.lib.Podcontent 		as Podcontent
# import resources.lib.ARD_Bildgalerie 	as ARD_Bildgalerie	# 10.12.2018 nicht mehr verfügbar

# +++++ ARDundZDF - Plugin Kodi-Version, migriert von der Plexmediaserver-Version +++++

VERSION =  '0.5.4'		 
VDATE = '23.12.2018'

# 
#	

# (c) 2018 by Roland Scholz, rols1@gmx.de
# 
#     Functions -> README.md
# 
# 	Licensed under MIT License (MIT)
# 	(previously licensed under GPL 3.0)
# 	A copy of the License you find here:
#		https://github.com/rols1/Plex-Plugin-ARDMediathek2016/blob/master/LICENSE.md

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
											# 	vom Plugin ermittelt
											# Radio-Sender-Logos erstellt von: Arauco (Plex-Forum). 
FAVORITS_Pod 	= 'podcast-favorits.txt' 	# Lesezeichen für Podcast-Erweiterung 
FANART					= 'fanart.png'		# ARD + ZDF - breit
ART 					= 'art.png'			# ARD + ZDF
ICON 					= 'icon.png'		# ARD + ZDF
ICON_SEARCH 			= 'ard-suche.png'						
ICON_ZDF_SEARCH 		= 'zdf-suche.png'						

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



# 01.12.2018 	Änderung der BASE_URL von www.ardmediathek.de zu classic.ardmediathek.de
BASE_URL 		= 'https://classic.ardmediathek.de'
BETA_BASE_URL	= 'https://beta.ardmediathek.de'
ARD_VERPASST 	= '/tv/sendungVerpasst?tag='								# ergänzt mit 0, 1, 2 usw.
ARD_AZ 			= 'https://beta.ardmediathek.de/ard/shows'					# ARDneu, komplett (#, A-Z)
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

# Relaunch der Mediathek beim ZDF ab 28.10.2016: xml-Service abgeschaltet
ZDF_BASE				= 'https://www.zdf.de'
# ZDF_Search_PATH: siehe ZDF_Search, ganze Sendungen, sortiert nach Datum, bei Bilderserien ohne ganze Sendungen
ZDF_SENDUNG_VERPASST 	= 'https://www.zdf.de/sendung-verpasst?airtimeDate=%s'  # Datumformat 2016-10-31
ZDF_SENDUNGEN_AZ		= 'https://www.zdf.de/sendungen-a-z?group=%s'			# group-Format: a,b, ... 0-9: group=0+-+9
ZDF_WISSEN				= 'https://www.zdf.de/doku-wissen'						# Basis für Ermittlung der Rubriken
ZDF_SENDUNGEN_MEIST		= 'https://www.zdf.de/meist-gesehen'
ZDF_BARRIEREARM			= 'https://www.zdf.de/barrierefreiheit-im-zdf'

ARDSender = ['ARD-Alle:ard::ard-mediathek.png', 'Das Erste:daserste:208:tv-das-erste.png', 'BR:br:2224:tv-br.png', 
			'MDR:mdr:1386804:tv-mdr-sachsen.png', 'NDR:ndr:5898:tv-ndr-niedersachsen.png', 
			'Radio Bremen:radiobremen::tv-bremen.png', 'RBB:rbb:5874:tv-rbb-brandenburg.png', 
			'SR:sr:5870:tv-sr.png', 'SWR:swr:5310:tv-swr.png', 'WDR:wdr:5902:tv-wdr.png',
			'ONE:one:673348:tv-one.png', 'ARD-alpha:alpha:5868:tv-alpha.png']

REPO_NAME		 	= 'Kodi-Addon-ARDundZDF'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME
myhost			 	= 'http://127.0.0.1:32400'



PLog('Plugin: lade Code')
PluginAbsPath = os.path.dirname(os.path.abspath(__file__))				# abs. Pfad für Dateioperationen
DICTSTORE 		= os.path.join("%s/resources/data/Dict") % PluginAbsPath
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]
HANDLE			= int(sys.argv[1])

#FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
#ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')
#FANART = R(FANART)
ICON = R(ICON)
PLog("ICON: " + ICON)
SLIDESTORE 		= os.path.join("%s/resources/data/slides") % ADDON_PATH
SUBTITLESTORE 	= os.path.join("%s/resources/data/subtitles") % ADDON_PATH


from platform import system, architecture, machine, release, version	# Debug
OS_SYSTEM = system()
OS_ARCH_BIT = architecture()[0]
OS_ARCH_LINK = architecture()[1]
OS_MACHINE = machine()
OS_RELEASE = release()
OS_VERSION = version()
OS_DETECT = OS_SYSTEM + '-' + OS_ARCH_BIT + '-' + OS_ARCH_LINK
OS_DETECT += ' | host: [%s][%s][%s]' %(OS_MACHINE, OS_RELEASE, OS_VERSION)

#Dict['ARDSender'] 	= ARDSender[0]	# 1. Element in ARDSender
# Dict: Simpler Ersatz für Dict-Modul aus Plex-Framework
Dict('ClearUp', '3')			# Dictstore bereinigen (Dateien älter als 3 Tage)	
Dict_ARDSender 		= ARDSender
Dict('store', "Dict_ARDSender", Dict_ARDSender)
Dict_CurSender 		= Dict_ARDSender[0]
days = int(SETTINGS.getSetting('pref_UT_store_days'))
ClearUp(SUBTITLESTORE, days*86400)	# SUBTITLESTORE bereinigen	
days = int(SETTINGS.getSetting('pref_SLIDES_store_days'))
ClearUp(SLIDESTORE, days*86400)	# SUBTITLESTORE bereinigen

#----------------------------------------------------------------  
																	
def Main():
	PLog('Main:'); 
	PLog('Plugin-Version: ' + VERSION); PLog('Plugin-Datum: ' + VDATE)	
	PLog(OS_DETECT)	
	PLog('Plugin-Python-Version: %s'  % sys.version)
			
	PLog(PluginAbsPath)	
	PLog(Dict_CurSender)	

	icon = R(ICON_MAIN_ARD)
	label 		= NAME
	li = xbmcgui.ListItem()
	
	title = "ARD Mediathek"
	fparams='&fparams=name=%s, sender=%s' % (title, Dict_CurSender)
	PLog(fparams)	
	addDir(li=li, label=title, action="dirList", dirID="Main_ARD", fanart=R(FANART), 
		thumb=R(ICON_MAIN_ARD), fparams=fparams)
	
	if SETTINGS.getSetting('pref_use_zdfmobile') == 'true':
		PLog('zdfmobile_set: ')
		fparams='&fparams=""'
		addDir(li=li, label="ZDFmobile", action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=R(FANART), thumb=R(ICON_MAIN_ZDFMOBILE), fparams=fparams)
	else:
		fparams='&fparams=name="ZDF Mediathek"'
		addDir(li=li, label="ZDF Mediathek", action="dirList", dirID="Main_ZDF", fanart=R(FANART), 
			thumb=R(ICON_MAIN_ZDF), fparams=fparams)
																																			
	fparams='&fparams=title="TV-Livestreams"'
	addDir(li=li, label='TV-Livestreams', action="dirList", dirID="SenderLiveListePre", 
		fanart=R(FANART), thumb=R(ICON_MAIN_TVLIVE), fparams=fparams)
	
	fparams='&fparams=path=ARD_RadioAll, title="Radio-Livestreams"'
	addDir(li=li, label='Radio-Livestreams', action="dirList", dirID="RadioLiveListe", 
		fanart=R(FANART), thumb=R(ICON_MAIN_RADIOLIVE), fparams=fparams)
		
	if SETTINGS.getSetting('pref_use_podcast') ==  'true':	# ARD-Radio-Podcasts
		summary = 'ARD-Radio-Podcasts suchen, hören und herunterladen'
		fparams='&fparams=name="PODCAST"'
		addDir(li=li, label='Radio-Podcasts', action="dirList", dirID="Main_POD", fanart=R(FANART), 
			thumb=R(ICON_MAIN_POD), fparams=fparams)								
	if SETTINGS.getSetting('pref_use_downloads') ==  'true':	# Download-Tools. zeigen
		summary = 'Download-Tools: Verschieben, Loeschen, Ansehen, Verzeichnisse bearbeiten'
		fparams='&fparams=""'
		addDir(li=li, label='Download-Tools', action="dirList", dirID="DownloadsTools", 
			fanart=R(FANART), thumb=R(ICON_DOWNL_DIR), fparams=fparams)		
								
	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if SETTINGS.getSetting('pref_info_update') == 'true': # Updatehinweis beim Start des Plugins 
		ret = updater.update_available(VERSION)
		int_lv = ret[0]			# Version Github
		int_lc = ret[1]			# Version aktuell
		latest_version = ret[2]	# Version Github, Format 1.4.1
		
		if int_lv > int_lc:								# Update-Button "installieren" zeigen
			call_update = True
			title = 'neues Update vorhanden - jetzt installieren'
			summary = 'Plugin aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
			# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
			url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
			fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(FANART), 
				thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
			
	if call_update == False:							# Update-Button "Suche" zeigen	
		title = 'Plugin-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summary='Suche nach neuen Updates starten'
		tagline='Bezugsquelle: ' + repo_url			
		fparams='&fparams=title="Plugin-Update"'
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(FANART), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams) # summary=summary, tagline=tagline)

	# Menü Einstellungen (obsolet) ersetzt durch Info-Button
	#	freischalten nach Posting im Kodi-Forum
	#summary = 'Störungsmeldungen an Forum oder rols1@gmx.de'
	#tagline = 'Forum: https://forums.plex.tv/t/rel-ardundzdf/309751'
	#fparams='&fparams=""'
	#addDir(li=li, label='Info', action="dirList", dirID="Main", fanart=R(FANART), thumb=R(ICON_INFO), 
	#	fparams=fparams, summary=summary, tagline=tagline)
					
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#----------------------------------------------------------------
# sender neu belegt in Senderwahl
def Main_ARD(name, sender=''):
	PLog('Main_ARD:'); 
	PLog(name); PLog(sender)
	Dict_CurSender = sender				# neu belegen nach Senderwahl
	Dict('store', "Dict_CurSender", Dict_CurSender)
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	PLog("li:" + str(li))						
			
	title="Suche in ARD-Mediathek"
	fparams='&fparams=channel=ARD, query='', title=%s' % title
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_ARD), 
		thumb=R(ICON_SEARCH), fparams=fparams)
		
	if sender == '':
		sender = ARDSender[0]	
	PLog('sender: ' + sender); 
	sendername, sender, kanal, img = sender.split(':')	# gewählter Sender für ARDStart Startbutton
	title = 'Start | Sender: %s' % sendername	
	fparams="&fparams={'title': '%s'}" % (urllib2.quote(title))
	addDir(li=li, label=title, action="dirList", dirID="ARDStart", fanart=R(ICON_MAIN_ARD), thumb=R(img), 
		fparams=fparams)

	title = 'Sendung verpasst (1 Woche)'
	fparams='&fparams=name=ARD, title=Sendung verpasst'
	addDir(li=li, label='Sendung verpasst', action="dirList", dirID="VerpasstWoche", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_VERP), fparams=fparams)
	
	title = 'Sendungen A-Z'
	fparams='&fparams=name=Sendungen A-Z, ID=ARD'
	addDir(li=li, label='Sendungen A-Z', action="dirList", dirID="SendungenAZ", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_AZ), fparams=fparams)
						
	fparams='&fparams=name=Barrierearm'
	addDir(li=li, label="Barrierearm", action="dirList", dirID="BarriereArmARD", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_BARRIEREARM), fparams=fparams)

	# 10.12.2018 nicht mehr verfügbar:
	#	www.ard.de/home/ard/23116/index.html?q=Bildergalerie
	#title = 'Bilderserien'	
	#fparams='&fparams=query=%s, channel=ARD, s_type=%s, title=%s' % (title,title,title)
	#addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_ARD),
	#	thumb=R('ard-bilderserien.png'), fparams=fparams)

	title 	= 'Wählen Sie Ihren Sender | aktuell: %s' % sendername				# Senderwahl
	fparams='&fparams=title=%s' % title
	addDir(li=li, label=title, action="dirList", dirID="Senderwahl", fanart=R(ICON_MAIN_ARD), 
		thumb=R('tv-regional.png'), fparams=fparams) 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		 		
#---------------------------------------------------------------- 
def Main_ZDF(name):
	PLog('Main_ZDF:'); PLog(name)
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	title="Suche in ZDF-Mediathek"
	fparams='&fparams=query='', title=%s' % title
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
		thumb=R(ICON_ZDF_SEARCH), fparams=fparams)

	fparams='&fparams=name=%s, title=Sendung verpasst' % name
	addDir(li=li, label='Sendung verpasst', action="dirList", dirID="VerpasstWoche", fanart=R(ICON_ZDF_VERP), 
		thumb=R(ICON_ZDF_VERP), fparams=fparams)	

	fparams='&fparams=name=Sendungen A-Z'
	addDir(li=li, label="Sendungen A-Z", action="dirList", dirID="ZDFSendungenAZ", fanart=R(ICON_ZDF_AZ), 
		thumb=R(ICON_ZDF_AZ), fparams=fparams)

	fparams='&fparams=name=Rubriken'
	addDir(li=li, label="Rubriken", action="dirList", dirID="Rubriken", fanart=R(ICON_ZDF_RUBRIKEN), 
		thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)

	fparams='&fparams=name=Meist gesehen'
	addDir(li=li, label="Meist gesehen (1 Woche)", action="dirList", dirID="MeistGesehen", 
		fanart=R(ICON_ZDF_MEIST), thumb=R(ICON_ZDF_MEIST), fparams=fparams)

	fparams='&fparams=name=Neu in der Mediathek'
	addDir(li=li, label="Neu in der Mediathek", action="dirList", dirID="NeuInMediathek", 
		fanart=R(ICON_ZDF_NEWCONTENT), thumb=R(ICON_ZDF_NEWCONTENT), fparams=fparams)
		
	fparams='&fparams=title=Barrierearm'
	addDir(li=li, label="Barrierearm", action="dirList", dirID="BarriereArm", fanart=R(ICON_ZDF_BARRIEREARM), 
		thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)

	fparams='&fparams=title=ZDFenglish'
	addDir(li=li, label="ZDFenglish", action="dirList", dirID="International", fanart=R('ZDFenglish.png'), 
		thumb=R('ZDFenglish.png'), fparams=fparams)

	fparams='&fparams=title=ZDFarabic'
	addDir(li=li, label="ZDFarabic", action="dirList", dirID="International", fanart=R('ZDFarabic.png'), 
		thumb=R('ZDFarabic.png'), fparams=fparams)

	fparams='&fparams=s_type=Bilderserien, title=Bilderserien, query=Bilderserien'
	addDir(li=li, label="Bilderserien", action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_BILDERSERIEN), 
		thumb=R(ICON_ZDF_BILDERSERIEN), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#----------------------------------------------------------------
def Main_POD(name):
	PLog('Main_POD:')
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

		
	title="Suche Podcasts in ARD-Mediathek"
	fparams='&fparams=channel=PODCAST, query='', title=%s' % title
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_POD), 
		thumb=R(ICON_SEARCH), fparams=fparams)	

	title = 'Sendungen A-Z'
	fparams='&fparams=name=%s, ID=PODCAST'	% title
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
	fparams='&fparams=query=%s, channel=PODCAST' % query
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MAIN_POD), thumb=R(ICON_POD_REFUGEE), 
		fparams=fparams)

	title="Podcast-Favoriten"; 
	fparams='&fparams=title=%s' % title
	addDir(li=li, label=title, action="dirList", dirID="PodFavoritenListe", fanart=R(ICON_MAIN_POD), 
		thumb=R(ICON_POD_FAVORITEN), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

################################################################
	
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
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Plugin vorher sichern!)			
		title = 'Update vorhanden - jetzt installieren'
		summary = 'Plugin aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
		tagline = cleanhtml(summ)
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary, 
			tagline=cleanhtml(summ))
			
		title = 'Update abbrechen'
		summary = 'weiter im aktuellen Plugin'
		thumb = R(ICON_UPDATER_NEW)
		fparams='&fparams=""'
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_UPDATER_NEW), 
			thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
	else:	
		title = 'Plugin ist aktuell | weiter zum aktuellen Plugin'
		summary = 'Plugin Version ' + VERSION + ' ist aktuell (kein Update vorhanden)'
		summ = summ.splitlines()[0]		# nur 1. Zeile changelog
		tagline = "%s | Mehr in changelog.txt" % summ
		thumb = R(ICON_OK)
		fparams='&fparams=title=Update Plugin'
		addDir(li=li, label=title, action="dirList", dirID="updater.menu", fanart=R(ICON_OK), 
			thumb=R(ICON_OK), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
#									beta.ardmediathek.de
#
#					zusätzliche Funktionen für die Betaphase ab Sept. 2018
#
#  	Funktion VerpasstWoche (weiter verwendet) bisher in beta.ardmediathek nicht vorhanden. 
#	Funktion 
####################################################################################################

# Startseite der Mediathek - passend zum ausgewählten Sender.
#def ARDStart(title, sender): 
def ARDStart(title): 
	PLog('ARDStart:'); 
	
	Dict_CurSender = Dict("load", 'Dict_CurSender')
	sendername, sender, kanal, img = Dict_CurSender.split(':')
	PLog(sender)	
	title2 = "Sender: %s" % sendername
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')									# Home-Button

	path = BETA_BASE_URL + "/%s/" % sender
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}"
	headers=urllib2.quote(headers)					# headers ohne quotes in get_page leer 
	page, msg = get_page(path=path, header=headers)	
	if page == '':	
		msg1 = "Fehler in ARDStart: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	if 'class="swiper-stage"' in page:						# Higlights im Wischermodus
		swiper 	= stringextract('class="swiper-stage"', 'gridlist', page)
		title 	= 'Higlights'
		# 14.11.2018 Bild vom 1. Beitrag befindet sich im json-Abschnitt,
		#	wird mittels href_id ermittelt:
		href_id =  stringextract('/player/', '/', swiper) # Bild vom 1. Beitrag wie Higlights
		img 	= img_via_id(href_id, page) 
			
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'ID': 'Swiper'}" % (urllib2.quote(path), 
			urllib2.quote(title), urllib2.quote(img))
		addDir(li=li, label=title, action="dirList", dirID="ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams)
								
	gridlist = blockextract('class="gridlist"', page)		# Rubriken
	PLog(len(gridlist))
	for grid in gridlist:
		# Formen: <h2 class=" hidden">Titel</h2>, <h2 class=" ">Titel/h2>
		title 	= stringextract('<h2', '<div', grid)
		title 	= stringextract('>', '<', title)
		title_oc= unescape(title)						# nur für Button, title ist Referenz
		noContent=stringextract('noContent">', '<', grid)	
		if noContent:
			title = "%s | % s" % (title, noContent)
		href_id =  stringextract('/player/', '/', grid)		# Bild vom 1. Beitrag
		img 	= img_via_id(href_id, page) 	
		
		ID 		= 'ARDStart'
		if 'teaser live' in grid:						# eigenes Icon für Live-Beitrag 
			href 	= stringextract('href="', '"', grid)
			img = R(ICON_MAIN_TVLIVE)
		# PLog(title); PLog(ID);  PLog(img); 
		title = UtfToStr(title)	
		fparams="&fparams={'path': '%s', 'title': '%s', 'img': '%s', 'ID': '%s'}" % (urllib2.quote(path), 
			urllib2.quote(title), urllib2.quote(img), ID)
		addDir(li=li, label=title_oc, action="dirList", dirID="ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE)
#---------------------------------------------------------------------------------------------------
def img_via_id(href_id, page):
	PLog("img_via_id:")
	item	= stringextract('Link:%s' %  href_id,  'idth}', page)
	# PLog('item: ' + item)
	img =  stringextract('src":"', '{w', item)
	img = img.replace('?w=', '')			# Endung .jpg?w={w
	img = img.replace('{w', '')				# Endung /16x9/{w
	if img.endswith('.jpg') == False:
		img = img + '640.jpg'
	return img
	
#---------------------------------------------------------------------------------------------------
# Auflistung einer Rubrik aus ARDStart - title (ohne unescape) ist eindeutige Referenz 
def ARDStartRubrik(path, title, img, ID=''): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title)
	title_org 	= title 								# title ist Referenz zur Rubrik
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')								# Home-Button

	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}"
	headers=urllib2.quote(headers)					# headers ohne quotes in get_page leer 
	page, msg = get_page(path=path, header=headers)	
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	if ID == 'Swiper':										# vorangestellte Higlights
		grid = stringextract('class="swiper-stage"', 'gridlist', page)
	else:
		gridlist = blockextract('class="gridlist"', page)	# Rubriken
		PLog(len(gridlist))
		for grid in gridlist:
			title 	= stringextract('<h2', '<div', grid)
			title 	= stringextract('>', '<', title)
			# PLog(title); PLog(title_org); 
			if title == title_org:							# Referenz-Rubrik gefunden
				# PLog(grid)
				break
			
	sendungen = blockextract('class="_focusable', grid)
	PLog(len(sendungen))
	for s in sendungen:
		href 	= BETA_BASE_URL + stringextract('href="', '"', s)
		title 	= stringextract('title="', '"', s)
		title	= unescape(title)
		href_id =  stringextract('/player/', '/', s) # Bild via id 
		img 	= img_via_id(href_id, page) 
			
		duration= stringextract('duration">', '</div>', s)
		if duration == '':
			duration = 'Dauer unbekannt'
		if	'class="day">Live</p>' in s:
			ID = 'Livestream'
			hrefsender = title.strip()
			title = "Live: %s"	% title
			duration = 'zu den Streaming-Formaten'
			# hrefsender = href.split('/')[-1]			# 20.12.2018 geändert
			# todo: get_playlist_img mit EPG erweitern
			playlist_img = get_playlist_img(hrefsender) # Icon aus livesenderTV.xml holen
			PLog('Livestream:')		
			if playlist_img:
				img = playlist_img
				# PLog(title); PLog(hrefsender); PLog(img)
			else:
				img = R(ICON_MAIN_TVLIVE)
				
		headline=UtfToStr(title); duration=UtfToStr(duration);	
		PLog("title: " + title); PLog("headline: " + headline); PLog(href)			
		fparams='&fparams=path=%s, title=%s, duration=%s, ID=%s' \
			% (urllib2.quote(href), urllib2.quote(title), duration, ID)
		addDir(li=li, label=headline, action="dirList", dirID="ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, summary=duration)
			
	xbmcplugin.endOfDirectory(HANDLE)
						
#---------------------------------------------------------------------------------------------------
# Ermittlung der Videoquellen für eine Sendung - hier Aufteilung Formate Streaming + MP4
# Videodaten in json-Abschnitt __APOLLO_STATE__ enthalten.
# Bei Livestreams (m3u8-Links) verzweigen wir direkt zu SenderLiveResolution.
# Videodaten unterteilt in _plugin":0 und _plugin":1,
#	_plugin":0 enthält manifest.f4m-Url und eine mp4-Url, die auch in _plugin":1
#	vorkommt.
# Parameter duration (müsste sonst aus json-Daten neu ermittelt werden, Bsp. _duration":5318.
# Falls path auf eine Rubrik-Seite zeigt, wird zu ARDStartRubrik zurück verzweigt.
def ARDStartSingle(path, title, duration, ID=''): 
	PLog('ARDStartSingle: %s' % ID);
	title_org 	= title 
	
	li = xbmcgui.ListItem()
	# li = home(li, ID='ARD')									# Home-Button

	page, msg = get_page(path)	
	if page == '':
		msg1 = "Fehler in ARDStartSingle: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
							
	PLog(len(page))
	VideoUrls = blockextract('_quality', page)					# Videoquellen vorhanden?
	if len(VideoUrls) == 0:	
		gridlist = blockextract('class="gridlist"', page)		# Test auf Rubriken
		if len(gridlist) > 0:
			PLog('%s Rubrik(en) -> ARDStartRubrik' % len(gridlist))
			return ARDStartRubrik(path, title, duration)		# zurück zu ARDStartRubrik
		
		msg1 = 'keine Videoquelle gefunden - Abbruch. Seite: ' + path
		PLog(msg1)
		msg2 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(VideoUrls))	
	
	summ 		= stringextract('synopsis":"', '"', page)
	img 		= stringextract('_previewImage":"', '"', page)
	geoblock 	= stringextract('geoblocked":', ',', page)
	if geoblock == 'true':										# Geoblock-Anhang für title, summary
		geoblock = ' | Geoblock: JA'
		title = title + geoblock
	else:
		geoblock = ' | Geoblock: nein'
	
	# Livestream-Abzweig, Bsp. tagesschau24:	
	# 	Kennzeichnung Livestream: 'class="day">Live</p>' in ARDStartRubrik.
	if ID	== 'Livestream':									
		VideoUrls = blockextract('json":["', page)				# 
		href = stringextract('json":["', '"', VideoUrls[-1])	# master.m3u8-Url
		if href.startswith('//'):
			href = 'http:' + href
		PLog(href)
		# bis auf weiteres Web-Icons verwenden (16:9-Format OK hier für Webplayer + PHT):
		#playlist_img = get_playlist_img(hrefsender) # Icon aus livesenderTV.xml holen
		#if playlist_img:
		#	img = playlist_img
		#	PLog(title); PLog(hrefsender); PLog(img)
		return SenderLiveResolution(path=href, title=title, thumb=img)	

	title = UtfToStr(title); summ = UtfToStr(summ); 
	summ = repl_json_chars(summ)
	PLog(title); PLog(summ[:60]);
	title_new 	= "Streaming-Formate | %s" % title
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'img': '%s', 'geoblock': '%s'}" \
		% (urllib2.quote(path), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(img), geoblock)
	addDir(li=li, label=title_new, action="dirList", dirID="ARDStartVideoStreams", fanart=img, thumb=img, 
		fparams=fparams, summary=summ, tagline=duration)		
					
	title_new = "MP4-Formate und Downloads | %s" % title	
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'img': '%s', 'geoblock': '%s'}" \
		% (urllib2.quote(path), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(img), geoblock)
	addDir(li=li, label=title_new, action="dirList", dirID="ARDStartVideoMP4", fanart=img, thumb=img, 
		fparams=fparams, summary=summ, tagline=duration)		
					
	xbmcplugin.endOfDirectory(HANDLE)
		
#---------------------------------------------------------------------------------------------------
#	Wiedergabe eines Videos aus ARDStart, hier Streaming-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
#	HTML-Seite mit json-Inhalt
def ARDStartVideoStreams(title, path, summ, img, geoblock): 
	PLog('ARDStartVideoStreams:'); 
	title_org = title	
	geoblock = UtfToStr(geoblock)
	li = xbmcgui.ListItem()
	li = home(li,  ID='ARD')								# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoStreams: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	Plugin1	= Plugins[0]							
	VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))
	
	href = ''
	for video in  VideoUrls:
		# PLog(video)
		q = stringextract('_quality":"', '"', video)	# Qualität (Bez. wie Original)
		if q == 'auto':
			href = stringextract('json":["', '"', video)	# Video-Url
			quality = 'Qualität: automatische'
			PLog(quality); PLog(href)	 
			break

	if 'master.m3u8' in href == False:						# möglich: ../master.m3u8?__b__=200
		msg = 'keine Streamingquelle gefunden - Abbruch' 
		PLog(msg)
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		return li
	if href.startswith('http') == False:
		href = 'http:' + href
	href = href.replace('https', 'http')					# Plex: https: crossdomain access denied
		
	lable = 'Bandbreite und Auflösung automatisch ' 		# master.m3u8
	lable = lable + geoblock
	title_org 	= UtfToStr(title_org)
	href 		= UtfToStr(href)
	fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib.quote_plus(href), urllib.quote_plus(title_org))
	addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams) 
				
	li = Parseplaylist(li, href, img, geoblock)	# einzelne Auflösungen 		
			
	xbmcplugin.endOfDirectory(HANDLE)
#---------------------------------------------------------------------------------------------------
#@route(PREFIX + '/ARDStartVideoMP4')	
#	Wiedergabe eines Videos aus ARDStart, hier MP4-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
def ARDStartVideoMP4(title, path, summ, img, geoblock): 
	PLog('ARDStartVideoMP4:'); 
	title_org=title; summary_org=summ; thumb=img; tagline_org=''	# Backup 
	geoblock = UtfToStr(geoblock)

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')									# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoMP4: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	Plugin1	= Plugins[0]							
	VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))
	
	href = ''
	download_list = []		# 2-teilige Liste für Download: 'title # url'
	Format = 'Video-Format: MP4'
	for video in  VideoUrls:
		href = stringextract('json":["', '"', video)	# Video-Url
		if href == '' or href.endswith('mp4') == False:
			continue
		if href.startswith('http') == False:
			href = 'http:' + href
		q = stringextract('_quality":"', '"', video)	# Qualität (Bez. wie Original)
		if q == '0':
			quality = 'Qualität: niedrige'
		if q == '1':
			quality = 'Qualität: mittlere'
		if q == '2':
			quality = 'Qualität: hohe'
		if q == '3':
			quality = 'Qualität: sehr hohe'
			
		lable 	= quality	+ geoblock
		title 	= UtfToStr(title)
		href 	= UtfToStr(href)
		title_org = UtfToStr(title_org)

		download_title = "%s | %s" % (quality, title)	# download_list stellt "Download Video" voran 
		download_list.append(download_title + '#' + href)	

		
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib.quote_plus(href), urllib.quote_plus(title_org))
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams) 
		
	PLog(download_list[:80])
	if 	download_list:	
		title = " | %s"				
		PLog(title);PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=-1)  # Downloadbutton(s)		
	
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
# Auflistung der A-Z-Buttons bereits in SendungenAZ
def SendungenAZ_ARDnew(title, path, button): 
	PLog('SendungenAZ_ARDnew:'); 
	PLog('button: ' + button)

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')									# Home-Button
	
	page, msg = get_page(path)					
	if page == '':
		msg1 = "Fehler in SendungenAZ_ARDnew: %s"	% title
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
							
	PLog(len(page))
	gridlist = blockextract('"mediumTitle":', page)	# A-Z, 0-9
	PLog(len(gridlist))
	
	sendungen = []
	cnt_item = 0
	for grid in gridlist:			
		mediumTitle = stringextract('"mediumTitle":', ',', grid)
		mediumTitle = mediumTitle.replace('"', '').strip()
		# PLog(mediumTitle)
		if mediumTitle[0:1] == button:				# Match: Anfangbuchstabe mit Button
			cnt_item = cnt_item +1
			# PLog('button: %s, cnt_item: %s' % (button,cnt_item))
			sendungen.append(grid)
	
	PLog(len(sendungen))
	PLog(sendungen[0])
	if len(sendungen) == 0:	
		msg1 = "SendungenAZ_ARDnew: Keine Sendungen gefunden."
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
	
	CB = 'ARDnew_Sendungen'							# page: img's außerhalb der Blöcke
	li = ARDnew_Content(li=li, Blocklist=sendungen, CB=CB, page=page)	
	
	return li 
#---------------------------------------------------------------------------------------------------
def ARDnew_Sendungen(title, path, img): 	# Seite mit mehreren Sendungen
	PLog('ARDnew_Sendungen:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')									# Home-Button

	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDnew_Sendungen: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
	
	sendungen = blockextract('class="teaser broadcast"', page)
	if len(sendungen) == 0:	
		msg1 = 'keine Inhalte gefunden - Abbruch' 
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
		
	CB = 'ARDStartSingle'
	li = ARDnew_Content(li=li, Blocklist=sendungen, CB=CB)
	
	return li
#---------------------------------------------------------------------------------------------------
# Extrahiert Sendungen aus Block in DirectoryObjects (zunächst nur für SendungenAZ_ARDnew).
# Nicht geeignet für die Start-Inhalte.
# 05.11.2018 Webseite geändert: redakt. Inhalt im json-Format - siehe SendungenAZ
def ARDnew_Content(li, Blocklist, CB, page): 		
	PLog('ARDnew_Content:')
	PLog('CB: ' + CB)
	
	if CB == 'ARDStartSingle':
		for sendung in Blocklist:
			href 		= BETA_BASE_URL + stringextract('href="', '"', sendung)
			img 		= stringextract('src="', '"', sendung)
			duration 	= stringextract('class="duration">', '</', sendung)
			headline 	= stringextract('class="headline', '</', sendung)
			headline = UtfToStr(headline)
			duration = UtfToStr(duration)
			headline	 = headline.replace('">', '')
			headline	= unescape(headline)
			
			if duration:
				headline	= headline + " | " + duration
			subline 	= stringextract('class="subline">', '</', sendung)
			if subline:
				subline = UtfToStr(subline)
				subline = subline.replace('<!-- -->', '')
				summary	= unescape(subline)
			else:
				summary = duration
				
			PLog(href); PLog(img); PLog(headline); PLog(subline);
				
			headline = UtfToStr(headline); duration = UtfToStr(duration);	
			fparams='&fparams=path=%s, title=%s, duration=%s, ID=ARDnew_Content' \
				% (urllib2.quote(href), urllib2.quote(headline), duration)
			addDir(li=li, label=headline, action="dirList", dirID="ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, summary=summary)
						
	if CB == 'ARDnew_Sendungen':
		for sendung in Blocklist:
			headline = stringextract('mediumTitle":', ',', sendung)
			headline = headline.replace('"', '').strip()
			sid 	= stringextract('"id":"$Teaser:', '.', sendung)
			img		= img_via_id(sid, page)
			sname 	= (headline.replace('#', '').replace(' ', '-').replace('(', '').replace(')', '')
				.replace(':', ' '))
			sname	= transl_umlaute(sname)
			href 	= 'https://beta.ardmediathek.de/ard/shows/%s/%s' % (sid, sname)
			
			PLog(href); PLog(img); PLog(headline); PLog(sid);		
			headline = UtfToStr(headline); 	
			fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" \
				% (urllib2.quote(headline), urllib2.quote(href), urllib2.quote(img))
			addDir(li=li, label=headline, action="dirList", dirID="ARDnew_Sendungen", fanart=img, thumb=img, 
				fparams=fparams)								
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#---------------------------------------------------------------------------------------------------
# Icon aus livesenderTV.xml holen
# Bei Bedarf erweitern für EPG (s. SenderLiveListe)
def get_playlist_img(hrefsender):
	PLog('get_playlist_img:'); 
	playlist_img = ''
	playlist = RLoad(PLAYLIST)		
	playlist = blockextract('<item>', playlist)
	for p in playlist:
		s = stringextract('hrefsender>', '</hrefsender', p)
		# PLog(hrefsender); PLog(s); 
		if s:									# skip Leerstrings
			if s.upper() in hrefsender.upper():
				playlist_img = stringextract('thumbnail>', '</thumbnail', p)
				playlist_img = R(playlist_img)
				break
	return playlist_img
#---------------------------------------------------------------------------------------------------

####################################################################################################
# 	Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
#	ID = PODCAST, ARD
def SendungenAZ(name, ID):		
	PLog('SendungenAZ: ' + name)
	PLog(ID)
	
	sendername, sender, kanal, img = Dict_CurSender.split(':')
	PLog(sender)	
	title2 = name + ' | aktuell: %s' % sendername
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)								# Home-Button
		
	azlist = list(string.ascii_uppercase)				# A - Z
	if ID == 'ARD':						# ARD-neu
		azlist.insert(0,'#')							# früher 0-9
	else:
		azlist.append('0-9')						# PODCAST
		next_cbKey = 'PageControl'		# SinglePage zeigt die Sendereihen, PageControl 
										#	 dann die weiteren Seiten
	
	# Die einzelnen Kanal-Seiten müssen leider auch einzeln geladen werden. Die Alle-Seite 
	# enthält zwar sämtliche Links, jedoch jweils mit der Url /ard/shows.. statt /{kanal}/shows..
	# 05.11.2018 Webseite geändert: redakt. Inhalt im json-Format, Ziel-Url's werden von der ARD 
	#	Hintergrund über ID's ermittelt, ledigl. img-Urls im Klartext vorhanden.
	# 	Kein Merkmal mehr für Inaktive Buchstaben vorhanden - Kennz. entfällt.
													
	for button in azlist:	
		# PLog(button)
		title = "Sendungen mit " + button
		#if button in inactive_char:	
		#	continue
		if ID == 'PODCAST':
			azPath = POD_AZ + button
			mode = 'Sendereihen'
			fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': '%s', 'mode': '%s', 'ID': '%s'}" \
				% (urllib2.quote(title), urllib2.quote(azPath), next_cbKey, mode, ID)
			addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=R(ICON_ARD_AZ), 
				thumb=R(ICON_ARD_AZ), fparams=fparams)

		else:
			path = BETA_BASE_URL + "/%s/shows" % sender
			summ = 'Gezeigt wird der Inhalt für %s' % sendername
			summ = summ
			# PLog(summ)
			fparams="&fparams={'title': '%s', 'path': '%s', 'button': '%s'}" \
				% (urllib2.quote(title), urllib2.quote(path), button)
			addDir(li=li, label=title, action="dirList", dirID="SendungenAZ_ARDnew", fanart=R(ICON_ARD_AZ), 
				thumb=R(ICON_ARD_AZ), fparams=fparams, summary=summ)
										
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------

####################################################################################################
	# Suche - Verarbeitung der Eingabe
	# Vorgabe UND-Verknüpfung (auch Podcast)
	# offset: verwendet nur bei Bilderserien (Funktionen s. ARD_Bildgalerie.py)
def Search(title='Suche', query='', s_type='', channel='ARD', offset=0, path=None):
	PLog('Search:'); PLog(query); PLog(channel); PLog(str(offset))
	if query == '':
		query = get_keyboard_input() 
		query = query.replace(' ', '+')			# Leer-Trennung = UND-Verknüpfung bei Podcast-Suche 
		# query = urllib2.quote(query, "utf-8")
		PLog(query)

	name = 'Suchergebnis zu: ' + urllib2.unquote(query)
	li = xbmcgui.ListItem()
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
			
	if channel == 'ARD':
		if s_type == 'Bilderserien':
			# 10.12.2018 nicht mehr verfügbar
			if path == None:			# path belegt bei offset > 0
				path = 'http://www.ard.de/home/ard/23116/index.html?q=Bildergalerie'
		else:
			path =  BASE_URL +  ARD_Suche 
			path = path % query
		ID='ARD'
	if channel == 'PODCAST':	
		path =  BASE_URL  + POD_SEARCH
		path = path % query
		ID=channel
		
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
	else:
		if s_type == 'Bilderserien':
			li = home(li, ID='ARD')										# Home-Button
			entries = blockextract('class="entry">',  page)
			if offset:		# 5 Seiten aus vorheriger Liste abziehen
				entries = entries[4:]
			PLog(len(entries))
			if len(entries) == 0:
				msg1 = 'keine weitere Bilderserie gefunden'
				xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
				return li
						
			page_high = re.findall('ctype="nav.page">(\d+)', page)[-1]	# letzte NR der nächsten Seiten
			PLog(page_high)
			href_high = blockextract('class="entry">',  page)[-1]		# letzter Pfad der nächsten Seiten
			href_high = 'http://www.ard.de' + stringextract('href="', '"', href_high)
			PLog(href_high)
			
			if offset == 0:
				title = "Weiter zu Seite 1"						# 1. Link fehlt in entries
				fparams="&fparams={'name': '%s', 'path': '%s', 'offset': '0'}" % (urllib2.quote(title), urllib2.quote(href_high))			
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARD_Bildgalerie.page", fanart=R(ICON_NEXT), 
					thumb=R(ICON_NEXT), fparams=fparams)
					
			for rec in entries:
				href =  'http://www.ard.de' + stringextract('href="', '"', rec)
				PLog(href[:60])
				pagenr = re.search('ctype="nav.page">(\d+)', rec).group(1)
				title = "Weiter zu Seite %s" % pagenr
				title2 = name="Seite: %s " %(pagenr)
				fparams="&fparams={'name': '%s', 'path': '%s', 'offset': '0'}" % (urllib2.quote(title2), urllib2.quote(href))			
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARD_Bildgalerie.page", fanart=R(ICON_NEXT), 
					thumb=R(ICON_NEXT), fparams=fparams)
					
			# Mehr Seiten Bilderserien anzeigen:
			#	Ablauf im Web (Klick auf die höchste Seite): Paging zeigt 4 vorige und 5 nächste Seiten, 
			#	Bsp. Seite 10: 6 -9, 11 - 15
			#	Hier zeigen wir nur die nächsten 5, um Wiederholungen zu vermeiden
			PLog('page_high: ' + page_high)
			title = 'Mehr Bilderserien'						
			fparams='&fparams=query=%s, channel=ARD, offset=%s, path=%s' % (query, page_high, href_high)
			fparams="&fparams={'query': '%s', 'channel': 'ARD', 'offset': '%s', 'path': '%s'}" \
				% (urllib2.quote(query), urllib2.quote(page_high),  urllib2.quote(href_high))			
			addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), fparams=fparams)
		else:	
			li = PageControl(title=name, path=path, cbKey=next_cbKey, mode='Suche', ID=ID) 	# wir springen direkt
	 
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

####################################################################################################
# Liste der Wochentage
	# Ablauf (ARD): 	
	#		2. PageControl: Liste der Rubriken des gewählten Tages
	#		3. SinglePage: Sendungen der ausgewählten Rubrik mit Bildern (mehrere Sendungen pro Rubrik möglich)
	#		4. Parseplaylist: Auswertung m3u8-Datei (verschiedene Auflösungen)
	#		5. CreateVideoClipObject: einzelnes Video-Objekt erzeugen mit Bild + Laufzeit + Beschreibung
	# Funktion VerpasstWoche bisher in beta.ardmediathek nicht vorhanden, aber Senderwahl bisher via kanal 
	#	im Pfad möglich (umstellen ab Integration Verpasst in neue Mediathek).
	#
	# ZDF:
	#	Wochentag-Buttons -> ZDF_Verpasst
	#
def VerpasstWoche(name, title):		# Wochenliste zeigen, name: ARD, ZDF Mediathek
	PLog('VerpasstWoche:')
	PLog(name);PLog(title);  
	sendername, sender, kanal, img = Dict_CurSender.split(':')	
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
		iPath = BASE_URL + ARD_VERPASST + str(nr)
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
		if name.find('ARD') == 0 :
			summ = 'Gezeigt wird der Inhalt für %s' % sendername
			if kanal == '' and sendername != 'ARD-Alle': # Sender noch ohne Kanalnummer? 
				summ = 'Gezeigt wird der Inhalt für %s - Seite für %s fehlt!' % ('ARD-Alle', sendername)
			fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': 'SinglePage', 'mode': 'Verpasst', 'ID': 'ARD'}" \
				% (title,  urllib2.quote(iPath))
			addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_VERP), 
				thumb=R(ICON_ARD_VERP), fparams=fparams, summary=summ)

		else:
			fparams='&fparams=title=%s, zdfDate=%s' % (title, urllib2.quote(zdfDate))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Verpasst", fanart=R(ICON_ZDF_VERP), 
				thumb=R(ICON_ZDF_VERP), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#------------
def transl_wtag(tag):	# Wochentage engl./deutsch wg. Problemen mit locale-Setting 
	wt_engl = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	wt_deutsch = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
	
	wt_ret = tag
	for i in range (len(wt_engl)):
		el = wt_engl[i]
		if el == tag:
			wt_ret = wt_deutsch[i]
			break
	return wt_ret
#------------
# 	Sender-Wahl für ARD
#	Für ARDnew gilt die Sender-Wahl für alle Inhalte, sonst nur für Verpasst.
#	Für ARDnew  verzichten wir auf die mehrfachen Regionalsender (wie beta.ardmediathek.de)
#	Bei Verpasst wird kanal Bestandteil der Url - entfällt bei ARDnew.
#	Falls die Kanäle sich ändern, von
#	Verpasst-Seite (BASE_URL + ARD_VERPASST) neu holen (1. Block class="entryGroup").
# 	ARDnew: Bremen ohne Kanal, tagesschau24 n.v.
def Senderwahl(title):	
	PLog('Senderwahl:'); 
	# entries = Sendername : Sender (Pfadbestandteil): Kanal : Icon
			
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	for entry in ARDSender:								# entry -> Dict_CurSender in Main_ARD
		PLog(entry)
		sendername, sender, kanal, img = entry.split(':')
		PLog('sendername: %s, sender: %s, kanal: %s, img: %s'	% (sendername, sender, kanal, img))
		title = 'Sender: %s' % sendername
			
		fparams='&fparams=name=ARD Mediathek, sender=%s' % entry
		addDir(li=li, label=title, action="dirList", dirID="Main_ARD", fanart=R(img), thumb=R(img), 
			fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
	
####################################################################################################
# Dachfunktion für 'Ausgewählte Filme' .. 'am besten bewertet' bis einschl. 'Rubriken'
# ab 06.04.2017 auch Podcasts: 'Rubriken' .. 'Meist abgerufen'
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
			PLog('Mark1')
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
	fname =  SETTINGS.getSetting('pref_pref_podcast_favorits')
	PLog(fname)
	if os.path.isfile(fname) == False:
		PLog('persoenliche Datei %s nicht gefunden' % fname)					
		Inhalt = RLoad(FAVORITS_Pod)		# Default-Datei
	else:										
		try:
			Inhalt = RLoad(fnameabs_path=True)	# pers. Datei verwenden (Name ebenfalls podcast-favorits.txt)	
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
	li = home(li,ID='PODCAST')				# Home-Button

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
		
		PLog(title); PLog(path)
		title=title
		title = UtfToStr(title)
		summary='Favoriten: ' + title
		fparams="&fparams={'title': '%s', 'path': '%s', 'offset': '0'}" % \
			(urllib2.quote(title), urllib2.quote(path))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFavoriten", 
			fanart=R(ICON_STAR), thumb=R(ICON_STAR), fparams=fparams, summary=summary, 
			tagline=path)
				
	
	# Mehr Seiten anzeigen:
	PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt + int(offset)
		PLog(new_offset)
		summ = 'Mehr (insgesamt ' + str(max_len) + ' Favoriten)'
		fparams='&fparams=title=%s, offset=%s' % (urllib2.quote(title_org), new_offset)
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

	title = 'Hörfassungen'
	title = UtfToStr(title)
	query = urllib2.quote(title, "utf-8")
	path = BASE_URL + ARD_Suche	%  query	
	
	
	next_cbKey = 'SinglePage'	# cbKey = Callback für Container in PageControl
	fparams="&fparams={'title': '%s', 'path': '%s', 'cbKey': '%s', 'mode': 'Suche', 'ID': 'ARD'}" \
		% (urllib2.quote(title), urllib2.quote(path), next_cbKey)
	addDir(li=li, label=title, action="dirList", dirID="PageControl", fanart=R(ICON_ARD_HOERFASSUNGEN), 
		thumb=R(ICON_ARD_HOERFASSUNGEN), fparams=fparams)

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
	
	page, msg = get_page(path=path)	
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
		if len(oc) == 1:								# 1 = Home
			msgH = 'Error'; msg = 'Keine Inhalte gefunden.'		
			return ObjectContainer(header=msgH, message=msg)		
		return oc																				

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
		fparams="&fparams={'title': '%s', 'path': '%s', 'next_cbKey': 'SingleSendung', 'mode': '%s', 'ID': '%s'}" \
			% (urllib2.quote(title), urllib2.quote(path_page1), mode, ID)	
		addDir(li=li, label=title, action="dirList", dirID="SinglePage", fanart=ICON, thumb=ICON, fparams=fparams)
	else:	# Folgeseite einer Mehrfachseite - keine Liste mehr notwendig
		PLog(first_site)													# wir springen wieder direkt:
		li = SinglePage(title=title, path=path, next_cbKey='SingleSendung', mode=mode, ID=ID)
		
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
	
	send_arr = get_sendungen(li, sendungen, ID, mode)	# send_arr enthält pro Satz 9 Listen 
	# Rückgabe send_arr = (send_path, send_headline, send_img_src, send_millsec_duration)
	#PLog(send_arr); PLog('Länge send_arr: ' + str(len(send_arr)))
	send_path = send_arr[0]; send_headline = send_arr[1]; send_subtitle = send_arr[2];
	send_img_src = send_arr[3]; send_img_alt = send_arr[4]; send_millsec_duration = send_arr[5]
	send_dachzeile = send_arr[6]; send_sid = send_arr[7]; send_teasertext = send_arr[8]

	#PLog(send_path); #PLog(send_arr)
	PLog(len(send_path));
	for i in range(len(send_path)):					# Anzahl in allen send_... gleich
		path = send_path[i]
		headline = send_headline[i]
		headline = UtfToStr(headline)
		headline = unescape(headline)				# HTML-Escapezeichen  im Titel	
		subtitle = send_subtitle[i]
		subtitle = UtfToStr(subtitle)
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
		summary = ''
		if send_teasertext[i] != "":				# teasertext z.B. bei Podcast
			summary = send_teasertext[i]
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
		PLog('neuer Satz'); PLog('path: ' + path); PLog(title); PLog(img_src); PLog(millsec_duration);
		PLog('next_cbKey: ' + next_cbKey); PLog('summary: ' + summary);
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
				
				fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'duration': '%s', 'summary': '%s', 'tagline': '%s', 'ID': '%s', 'offset': '%s'}" \
					% (urllib2.quote(path), urllib2.quote(headline), urllib2.quote(img_src), 
					millsec_duration, urllib2.quote(summary),  urllib2.quote(subtitle), ID, offset)				
				addDir(li=li, label=headline, action="dirList", dirID="SingleSendung", fanart=img_src, thumb=img_src, 
					fparams=fparams, summary=summary, tagline=subtitle)
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
				addDir(li=li, label=headline, action="dirList", dirID="SinglePage", fanart=img_src, thumb=Rimg_src, 
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
# einzelne Sendung, path in neuer Mediathekführt zur 
# Quellenseite (verschiedene Formate -> 
#	1. Text-Seite mit Verweis auf .m3u8-Datei und / oder href_quality_ Angaben zu mp4-videos -
#		im Listenformat, nicht m3u8-Format, die verlinkte master.m3u8 ist aber im 3u8-Format
#	2. Text-Seite mit rtmp-Streams (Listenformat ähnlich Zif. 1, rtmp-Pfade müssen zusammengesetzt
#		werden
#   ab 01.04.2017 mit Podcast-Erweiterung auch Verabeitung von Audio-Dateien
#	18.04.2017 die Podcasts von PodFavoriten enthalten in path bereits mp3-Links, parseLinks_Mp4_Rtmp entfällt

def SingleSendung(path, title, thumb, duration, summary, tagline, ID, offset=0):	# -> CreateVideoClipObject
	PLog('SingleSendung:')						# z.B. https://classic.ardmediathek.de/play/media/11177770
	PLog('path: ' + path)
	PLog('ID: ' + str(ID))
	PLog(thumb)
	
	title = urllib2.unquote(title)
	title_org=title; summary_org=summary; tagline_org=tagline	# Backup 

	
	li = xbmcgui.ListItem()
	li = home(li, ID=ID)				# Home-Button
	# PLog(path)
	
	if ID == 'PODCAST':
		Format = 'Podcast-Format: MP3'					# Verwendung in summmary
	else:
		Format = 'Video-Format: MP4'

	# Bei Podcasts enthält path i.d.R. 1 Link zur Seite mit einer mp3-Datei, bei Podcasts von PodFavoriten 
	# wird der mp3-Link	direkt in path übergeben.
	if path.endswith('.mp3') == False:
		page, msg = get_page(path=path)				# Absicherung gegen Connect-Probleme. Page=Textformat
		if page == '':
			msg1 = 'Fehler:'
			msg2 = msg
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li
		link_path,link_img, m3u8_master, geoblock = parseLinks_Mp4_Rtmp(page) # link_img kommt bereits mit thumb, außer Podcasts						
		PLog('m3u8_master: ' + m3u8_master); PLog(link_img); PLog(link_path); 
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
	if m3u8_master:	  		  								# nicht bei rtmp-Links (ohne master wie m3u8)
		title = '1. Bandbreite und Auflösung automatisch' + geoblock			# master.m3u8
		m3u8_master = m3u8_master.replace('https', 'http')	# 26.06.2017: nun auch ARD mit https
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(m3u8_master), title)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams) 
						
		li = Parseplaylist(li, m3u8_master, thumb, geoblock='')
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
			

		PLog('title: ' + title); PLog('url: ' + url); 
		if url:
			if '.m3u8' in url:				# master.m3u8 überspringen, oben bereits abgehandelt
				continue
			if 'manifest.f4m' in url:		# manifest.f4m überspringen
				continue
						
			if url.find('rtmp://') >= 0:	# 2. rtmp-Links:	
				summary = Format + 'RTMP-Stream'	
				lable = "%s | %s" % (title, summary)
				fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(url), title)
				addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
					summary=summary)
									
			else:
				summary = Format			# 3. Podcasts mp3-Links, mp4-Links
				if ID == 'PODCAST':			# (noch) keine Header benötigt
					lable = "%s. %s | %s" % (str(li_cnt), title, summary)
					fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(url), title)
					addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams, 
						summary=summary)
				else:
					# 26.06.2017: nun auch ARD mit https - aber: bei den mp4-Videos liefern die Server auch
					#	mit http, während bei m3u8-Url https durch http ersetzt werden MUSS. 
					url = url.replace('https', 'http')	
					summary=summary+geoblock
					lable = "%s. %s | %s" % (str(li_cnt), title, summary)
					fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(url), title)
					addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams) 
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
					thumb=R(ICON_DOWNL), fparams=fparams, summary=summary, tagline=tagline)
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
			PLog(msg)
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
		if path == '':		
			msg1='Downloadverzeichnis noch nicht festgelegt.'
		else:
			msg1='Downloadverzeichnis nicht gefunden: '
		msg2=path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
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
	fparams='&fparams=settingKey=pref_curl_path, mytype=1, heading=%s, path=%s' % (title, path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_CURLWGET), fparams=fparams, tagline=tagline)

	dlpath =  SETTINGS.getSetting('pref_curl_download_path')# Einstellungen: Pfad Downloaderz.
	title = 'Downloadverzeichnis festlegen/aendern: (%s)' % dlpath			
	tagline = 'Das Downloadverzeichnis muss für Plex beschreibbar sein.'
	# summary =    # s.o.
	fparams='&fparams=settingKey=pref_curl_download_path, mytype=0, heading=%s, path=%s' % (title, dlpath)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DOWNL_DIR), fparams=fparams, tagline=tagline)

	PLog(SETTINGS.getSetting('pref_VideoDest_path'))
	movie_path = SETTINGS.getSetting('pref_VideoDest_path')
	if SETTINGS.getSetting('pref_VideoDest_path') == '':# Vorgabe Medienverzeichnis (Movieverz), falls leer	
		pass
		# movie_path = xbmc.translatePath('library://video/')
		# PLog(movie_path)
				
	if os.path.isdir(movie_path)	== False:			# Sicherung gegen Fehleinträge
		movie_path = ''								# wird ROOT_DIRECTORY in DirectoryNavigator
	PLog(movie_path)	
	title = 'Zielverzeichnis zum Verschieben festlegen/aendern (%s)' % (movie_path)	
	tagline = 'Zum Beispiel das Medienverzeichnis.'
	# summary =    # s.o.
	fparams='&fparams=settingKey=pref_VideoDest_path, mytype=0, heading=%s, path=%s' % (title, movie_path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_MOVEDIR_DIR), fparams=fparams, tagline=tagline)

	PLog(SETTINGS.getSetting('pref_podcast_favorits'))					# Pfad zur persoenlichen Podcast-Favoritenliste
	path =  SETTINGS.getSetting('pref_podcast_favorits')							
	title = 'Persoenliche Podcast-Favoritenliste festlegen/aendern (%s)' % path			
	tagline = 'Format siehe podcast-favorits.txt (Ressourcenverzeichnis)'
	# summary =    # s.o.
	fparams='&fparams=settingKey=pref_podcast_favorits, mytype=1, heading=%s, path=%s' % (title, path)
	addDir(li=li, label=title, action="dirList", dirID="DirectoryNavigator", fanart=R(ICON_DOWNL_DIR), 
		thumb=R(ICON_DIR_FAVORITS), fparams=fparams, tagline=tagline)
		
	if mpcnt > 0:																# Videos / Podcasts?
		title = 'Downloads bearbeiten: %s Download(s)' % (mpcnt)				# Button Bearbeiten
		summary = 'Downloads im Downloadverzeichnis ansehen, loeschen, verschieben'
		fparams='&fparams=""'
		addDir(li=li, label=title, action="dirList", dirID="DownloadsList", fanart=R(ICON_DOWNL_DIR), 
			thumb=R(ICON_DIR_WORK), fparams=fparams, summary=summary)

		if dirlist:
			dest_path = SETTINGS.getSetting('pref_curl_download_path') 
			if path and movie_path:												# Button Verschieben (alle)
				title = 'ohne Rückfrage! alle (%s) Downloads verschieben' % (mpcnt)	
				tagline = 'Verschieben erfolgt ohne Rueckfrage!' 
				summary = 'alle Downloads verschieben nach: %s'  % (movie_path)
				fparams='&fparams=dfname="", textname="", dlpath=%s, destpath=%s, single=False' % (dest_path, movie_path)
				addDir(li=li, label=title, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DOWNL_DIR), 
					thumb=R(ICON_DIR_MOVE_ALL), fparams=fparams, summary=summary, tagline=tagline)
			
			title = 'ohne Rückfrage! alle (%s) Downloads loeschen' % (mpcnt)			# Button Leeren (alle)
			tagline = 'Loeschen erfolgt ohne Rueckfrage!'						
			summary = 'alle Dateien aus dem Downloadverzeichnis entfernen'
			fparams='&fparams=dlpath=%s, single=False' % dlpath
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
		title1 = 'Downloadverzeichnis noch nicht festgelegt'
	else:
		if os.path.isdir(path)	== False:			
			msg='Downloadverzeichnis nicht gefunden: ' + path
			return ObjectContainer(header='Error', message=msg)
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
		msg='Kein Download vorhanden | Pfad: %s' % (dlpath)
		return ObjectContainer(header='Error', message=msg)
		
		
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
				quality = stringextract("tät: '", "'", txt)
				thumb = stringextract("Bildquelle: '", "'", txt)
				httpurl = stringextract("Adresse: '", "'", txt)
				
				if tagline == '':
					tagline = quality
				else:
					if len(quality.strip()) > 0:
						tagline = quality + ' | ' + tagline
			else:										# ohne Beschreibung
				pass									# Plex brauchte hier die Web-Url	aus der Beschreibung
				#title = fname
				#httpurl = fname							# Berücksichtigung in VideoTools - nicht abspielbar
				#summary = 'Beschreibung fehlt - Abspielen nicht möglich'
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

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	
	dest_path = SETTINGS.getSetting('pref_curl_download_path')
	fulldest_path = os.path.join(dest_path, path)
	if  os.access(dest_path, os.R_OK) == False:
		msg1 = 'Downloadverzeichnis oder Leserecht  fehlt'
		msg2 = dest_path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	if fulldest_path.endswith('mp4') or fulldest_path.endswith('webm'):# 1. Ansehen
		title = title_org 
		lable = "Ansehen | %s" % (title_org)
		fulldest_path = UtfToStr(fulldest_path)		
		fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib.quote_plus(fulldest_path), urllib.quote_plus(title))	
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams)
		
	else:										# 'mp3' = Podcast
		if fulldest_path.endswith('mp3'):		# Dateiname bei fehl. Beschreibung, z.B. Sammeldownloads
			title = title_org 											# 1. Anhören
			lable = "Anhören | %s" % (title_org)
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib2.quote(fulldest_path), title)
			addDir(li=li, label=lable, action="dirList", dirID="PlayAudio", fanart=thumb, thumb=thumb, fparams=fparams) 
	
	lable = "Loeschen ohne Rückfrage | %s" % title_org 					# 2. Löschen
	tagline = 'Datei: ' + path 
	fparams='&fparams=dlpath=%s, single=True' % urllib2.quote(fulldest_path)
	addDir(li=li, label=lable, action="dirList", dirID="DownloadsDelete", fanart=R(ICON_DELETE), 
		thumb=R(ICON_DELETE), fparams=fparams, summary=summary, tagline=tagline)
	
	if SETTINGS.getSetting('pref_VideoDest_path'):	# 3. Verschieben nur mit Zielpfad, einzeln
		VideoDest_path = SETTINGS.getSetting('pref_VideoDest_path')
		textname = os.path.basename(txtpath)
		lable = "Verschieben | %s" % title_org									
		summary = "Ziel: %s" % VideoDest_path
		tagline = 'Das Zielverzeichnis kann im Menü Download-Tools geaendert werden'
		fparams='&fparams=dfname=%s, textname=%s, dlpath=%s, destpath=%s, single=True' \
			% (urllib2.quote(path), urllib2.quote(textname), urllib2.quote(dlpath), urllib2.quote(VideoDest_path))
		addDir(li=li, label=lable, action="dirList", dirID="DownloadsMove", fanart=R(ICON_DIR_MOVE_SINGLE), 
			thumb=R(ICON_DIR_MOVE_SINGLE), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#---------------------------
# Downloadverzeichnis leeren (einzeln/komplett)
def DownloadsDelete(dlpath, single):
	PLog('DownloadsDelete: ' + dlpath)
	PLog('single=' + single)
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

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
		msg1 = 'Loeschen erfolgreich'
		msg2 = error_txt
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
	except Exception as exception:
		PLog(str(exception))
		msg1 = 'Fehler | Loeschen fehlgeschlagen'
		msg2 = str(exception)
		return li

#---------------------------
# dfname=Videodatei, textname=Textfile,  dlpath=Downloadverz., destpath=Zielverz.
#
def DownloadsMove(dfname, textname, dlpath, destpath, single):
	PLog('DownloadsMove: ');PLog(dfname);PLog(textname);PLog(dlpath);PLog(destpath);
	PLog('single=' + single)

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

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
def parseLinks_Mp4_Rtmp(page):		# extrahiert aus Mediendatei (json) .mp3-, .mp4- und rtmp-Links (Aufrufer 
									# SingleSendung). Bsp.: http://www.ardmediathek.de/play/media/35771780
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
			PLog(s2); PLog(len(s2))				# nur bei Bedarf
				
							
			if len(s2) > 9:						# schon url gefunden? Dann Markierung ermitteln
				if s1.find('auto') >= 0:
					mark = 'auto' + '|'					
				else:
					m = s1[0:1] 				# entweder Ziffern 0,1,2,3 
					mark = m + '|' 	
								
				link = mark + s2				# Qualität voranstellen			
				link_path.append(link)
				PLog(mark); PLog(s2); PLog(link); # PLog(link_path)
			
	#PLog(link_path)				
	link_path = list(set(link_path))			# Doppel entfernen (gesehen: 0, 1, 2 doppelt)
	link_path.sort()							# Sortierung - Original Bsp.: 0,1,2,0,1,2,3
	PLog(link_path); PLog(len(link_path))					
		
	return link_path, link_img, m3u8_master, geoblock				 		
		
####################################################################################################
def get_sendungen(li, sendungen, ID, mode): # Sendungen ausgeschnitten mit class='teaser', aus Verpasst + A-Z,
	# 										Suche, Einslike
	# Headline + subtitle sind nicht via xpath erreichbar, daher Stringsuche:
	# ohne linklist + subtitle weiter (teaser Seitenfang od. Verweis auf Serie, bei A-Z teaser-Satz fast identisch,
	#	nur linklist fehlt )
	# Die Rückgabe-Liste send_arr nimmt die Datensätze auf (path, headline usw.)
	# ab 02.04.2017: ID=PODCAST	- bei Sendereihen enthält der 1. Satz Bild + Teasertext
	PLog('get_sendungen'); PLog(ID); PLog(mode); 

	img_src_header=''; img_alt_header=''; teasertext_header=''; teasertext=''
	if ID == 'PODCAST' and mode == 'Sendereihen':							# PODCAST: Bild + teasertext nur im Kopf vorhanden
		# PLog(sendungen[0])		# bei Bedarf
		if sendungen[0].find('urlScheme') >= 0:	# Bild ermitteln, versteckt im img-Knoten
			text = stringextract('urlScheme', '/noscript', sendungen[0])
			img_src_header, img_alt_header = img_urlScheme(text, 320, ID) # Format quadratisch bei Podcast
			teasertext_header = stringextract('<h4 class=\"teasertext\">', '</p>', sendungen[0])
		del sendungen[0]						# nicht mehr benötigt, Beiträge folgen dahinter
			
	# send_arr nimmt die folgenden Listen auf (je 1 Datensatz pro Sendung)
	send_path = []; send_headline = []; send_subtitle = []; send_img_src = [];
	send_img_alt = []; send_millsec_duration = []; send_dachzeile = []; send_sid = []; 
	send_teasertext = []; 
	arr_ind = 0
	for s in sendungen:	
		found_sendung = False
		if s.find('<div class="linklist">') == -1 or ID == 'PODCAST':  # PODCAST-Inhalte ohne linklistG::;
			if  s.find('subtitle') >= 0: 
				found_sendung = True
			if  s.find('dachzeile') >= 0: # subtitle in ARDThemen nicht vorhanden
				found_sendung = True
			if  s.find('<h4 class=\"headline\">') >= 0:  # in Rubriken weder subtitle noch dachzeile vorhanden
				found_sendung = True
				
		PLog(found_sendung)
		# PLog(s)				# bei Bedarf
		if found_sendung:				
			dachzeile = re.search("<p class=\"dachzeile\">(.*?)</p>\s+?", s)  # Bsp. <p class="dachzeile">Weltspiegel</p>
			if dachzeile:									# fehlt komplett bei ARD_SENDUNG_VERPASST
				dachzeile = dachzeile.group(1)
			else:
				dachzeile = ''
			headline = stringextract('<h4 class=\"headline\">', '</h4>', s)
			PLog(headline)				# bei Bedarf
			headline = UtfToStr(headline)
			if headline == '':
				continue
		
			#if headline.find('- Hörfassung') >= 0:			# nicht unterdrücken - keine reine Hörfassung gesehen 
			#	continue
			if headline.find('Diese Seite benötigt') >= 0:	# Vorspann - irrelevant
				continue
			hupper = headline.upper()
			if hupper.find(str.upper('Livestream')) >= 0:			# Livestream hier unterdrücken (mehrfach in Rubriken)
				continue
			if s.find('subtitle') >= 0:	# nicht in ARDThemen
				subtitle = re.search("<p class=\"subtitle\">(.*?)</p>\s+?", s)	# Bsp. <p class="subtitle">25 Min.</p>
				subtitle = subtitle.group(1)
				subtitle = subtitle.replace('<br>', ' | ')				
				subtitle = UtfToStr(subtitle)
			else:
				subtitle =""
								
			PLog(headline)
			
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
			
											# dann der komplette Listen-Satz ins Array		
	send_arr = [send_path, send_headline, send_subtitle, send_img_src, send_img_alt, send_millsec_duration, 
		send_dachzeile, send_sid, send_teasertext]
	PLog(len(send_path))	 # Anzahl send_path = Anzahl Sätze		
	return send_arr
#-------------------
####################################################################################################
# LiveListe Vorauswahl - verwendet lokale Playlist
# xbmcswift2: Request for "/SenderLiveListePre/TV-Livestreams" matches .."
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
		
		fparams='&fparams=title=%s, listname=%s, fanart=%s' % (urllib2.quote(name), urllib2.quote(name), img)
		util.addDir(li=li, label=name, action="dirList", dirID="SenderLiveListe", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=img, fparams=fparams)

	title = 'EPG Alle JETZT'; summary='elektronischer Programmfuehrer'
	fparams='&fparams=title=%s' % title
	util.addDir(li=li, label=title, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
		thumb=R('tv-EPG-all.png'), fparams=fparams)
							
	title = 'EPG Sender einzeln'; summary='elektronischer Programmfuehrer'
	tagline = 'Sendungen für ausgewaehlten Sender'									# EPG-Button Einzeln anhängen
	fparams='&fparams=title=%s' % title
	util.addDir(li=li, label=title, tagline=tagline, action="dirList", dirID="EPG_Sender", fanart=R(ICON_MAIN_TVLIVE), 
		thumb=R('tv-EPG-single.png'), fparams=fparams)	
		
	PLog(str(SETTINGS.getSetting('pref_LiveRecord')))
	if SETTINGS.getSetting('pref_LiveRecord'):		
		title = 'Recording TV-Live'													# TVLiveRecord-Button anhängen
		duration = SETTINGS.getSetting('pref_LiveRecord_duration')
		duration, laenge = duration.split('=')
		tagline = SETTINGS.getSetting('pref_curl_download_path') 				
		fparams='&fparams=title=%s' % title
		util.addDir(li=li, label=title, action="dirList", dirID="TVLiveRecordSender", fanart=R(ICON_MAIN_TVLIVE), 
			thumb=R('icon-record.png'), fparams=fparams, properties={'Dauer': duration, 'Downloadpfad': tagline})

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
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" % (link, title, R(rec[2]))
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
		summ 	= 'Aufnahmedauer: %s' 	% laenge
		tag		= 'Zielverzeichnis: %s' % SETTINGS.getSetting('pref_curl_download_path')
		fparams='&fparams=url=%s, title=%s, duration=%s,laenge=%s' \
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

def LiveRecord(url, title, duration, laenge):
	PLog('LiveRecord:')
	PLog(url); PLog(title); 
	PLog('duration: %s, laenge: %s' % (duration, laenge))

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)					# Home-Button
	
	dest_path = SETTINGS.getSetting('pref_curl_download_path')
	if  dest_path == None or dest_path.strip() == '':
		msg1	= 'LiveRecord:'
		msg2 	= 'Downloadverzeichnis fehlt in Einstellungen'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			
		
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
			PLog('Aufnahme gestartet: %s' % dfname)	
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
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
	PLog('get_sort_playlist')
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	sort_playlist =  []
	for item in playlist:   
		rec = []
		title = stringextract('<title>', '</title>', item)
		title = title.upper()										# lower-/upper-case für sort() relevant
		EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', item)
		img = 	stringextract('<thumbnail>', '</thumbnail>', item)
		link =  stringextract('<link>', '</link>', item)			# url für Livestreaming
		rec.append(title); rec.append(EPG_ID);						# Listen-Element
		rec.append(img); rec.append(link);
		sort_playlist.append(rec)									# Liste Gesamt
	
	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist.sort()	
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
		title=sname
#		title = UtfToStr(title)
		summ = UtfToStr(summ)
		summ = unescape(summ)
		PLog("title: " + title)
		tagline = 'Zeit: ' + vonbis
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" % (urllib2.quote(stream_url), 
			urllib2.quote(title), img)
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
# Todo: Sammelabruf in EPG-Modul integrieren - der ständige Wechsel in der Schleife hier ist 
#		sehr zeitaufwendig

def EPG_ShowAll(title, offset=0):
	PLog('EPG_ShowAll:')
	title = urllib2.unquote(title)
	title_org = title
	title2='Aktuelle Sendungen'
		
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = get_sort_playlist()	
	PLog(len(sort_playlist))
	
	rec_per_page = 10								# Anzahl pro Seite (Timeout ab 15 beobachtet)
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

		title_playlist = rec[0]
		m3u8link = rec[3]
		img_playlist = R(rec[2])
		ID = rec[1]
		if ID == '':									# ohne EPG_ID
			title = title_playlist + ': ohne EPG | weiter zum Livestream'
			tagline = ''
			img = img_playlist
			PLog("img: " + img)
		else:
			# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis: 
			rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
			# PLog(rec)	# bei Bedarf
			if len(rec) == 0:							# Satz leer?
				title = title_playlist + ': ohne EPG'
				summ = 'weiter zum Livestream'
				tagline = ''
				img = img_playlist			
			else:	
				href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]
				if img.find('http') == -1:	# Werbebilder today.de hier ohne http://, Ersatzbild einfügen
					img = R('icon-bild-fehlt.png')
				sname = sname.replace('JETZT', title_playlist)			# JETZT durch Sender ersetzen
				tagline = 'Zeit: ' + vonbis
				
		title = UtfToStr(sname)
		title = unescape(title)
		PLog("title: " + title)
					
		fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s'}" % (urllib2.quote(m3u8link), urllib2.quote(title), img)
		addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=R('tv-EPG-all.png'), 
			thumb=img, fparams=fparams, summary=summ, tagline=tagline)

	# Mehr Seiten anzeigen:
	# PLog(offset); PLog(cnt); PLog(max_len);
	if (int(cnt) +1) < int(max_len): 						# Gesamtzahl noch nicht ereicht?
		new_offset = cnt 
		PLog(new_offset)
		summ = 'Mehr %s (insgesamt %s)' % (title2, str(max_len))
		fparams='&fparams=title=%s, offset=%s'	% (title_org, new_offset)
		addDir(li=li, label=summ, action="dirList", dirID="EPG_ShowAll", fanart=R('tv-EPG-all.png'), 
			thumb=R(ICON_MEHR), fparams=fparams, summary=summ, tagline=title2)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------------------------------------------------------------------------------
# LiveListe - verwendet lokale Playlist
def SenderLiveListe(title, listname, fanart, offset=0):			
	# SenderLiveListe -> SenderLiveResolution (reicht nur durch) -> Parseplaylist (Ausw. m3u8)
	#	-> CreateVideoStreamObject 
	PLog('SenderLiveListe:')
	PLog(title); PLog(listname)
			
	title2 = 'Live-Sender ' + title
	title2 = title2
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
			
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
		epg_schema=''; epg_url=''
		epg_date=''; epg_title=''; epg_text=''; summary=''; tagline='' 
		# PLog(SETTINGS.getSetting('pref_use_epg')) 	# Voreinstellung: EPG nutzen? - nur mit Schema nutzbar
		PLog('setting: ' + str(SETTINGS.getSetting('pref_use_epg')))
		if SETTINGS.getSetting('pref_use_epg'):
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
		fparams="&fparams={'path': '%s', 'thumb': '%s', 'title': '%s'}" % (urllib.quote_plus(link), 
			img, urllib.quote_plus(title))
		
		util.addDir(li=li, label=title, action="dirList", dirID="SenderLiveResolution", fanart=fanart, thumb=img, 
			fparams=fparams)		
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#-----------------------------------------------------------------------------------------------------
#	17.02.2018 Video-Sofort-Format wieder entfernt (V3.1.6 - V3.5.0)
#		Forum:  https://forums.plex.tv/discussion/comment/1606010/#Comment_1606010
#		Funktionen: remoteVideo, Parseplaylist, SenderLiveListe, TestOpenPort
#-----------------------------------------------------------------------------------------------------
			
###################################################################################################
# Auswahl der Auflösungstufen des Livesenders
def SenderLiveResolution(path, title, thumb):
	PLog('SenderLiveResolution:')
	title=urllib2.unquote(title); path=urllib2.unquote(path); thumb=urllib2.unquote(thumb)
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
		fparams="&fparams=url=%s, title=%s" % (urllib.quote_plus(url_m3u8), title)	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title)	
		
	if url_m3u8.find('rtmp') == 0:		# rtmp, nur 1 Videoobjekt
		summary = 'rtmp-Stream'
		fparams="&fparams=url=%s, title=%s" % (urllib.quote_plus(url_m3u8), title)	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
			summary=summary, tagline=title)	
		
	# alle übrigen (i.d.R. http-Links), Videoobjekte für einzelne Auflösungen erzeugen
	# Für Kodi: m3u8-Links abrufen, speichern und die Datei dann übergeben - direkte
	#	Übergabe der Url nicht abspielbar
	# is_playable ist verzichtbar
	if url_m3u8.find('.m3u8') >= 0:				# häufigstes Format
		PLog(url_m3u8)
		if url_m3u8.startswith('http'):			# URL extern? (lokal entfällt Eintrag "autom.")	
			PLog('Listitem li: ' + str(li));
			li = ParseMasterM3u(li, url_m3u8, thumb, title)	#  Download + Ablage master.m3u8
							
		# Auswertung *.m3u8-Datei  (lokal oder extern), Auffüllung Container mit Auflösungen. 
		# jeweils 1 item mit http-Link für jede Auflösung.
		
		PLog('Listitem li: ' + str(li)); 	
		li = Parseplaylist(li, url_m3u8, thumb, geoblock='')	# (-> CreateVideoStreamObject pro Auflösungstufe)
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)					
	else:	# keine oder unbekannte Extension - Format unbekannt
		msg1 = 'SenderLiveResolution: unbekanntes Format. Url:'
		msg2 = url_m3u8
		PLog(msg)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
		
#-----------------------------
# Download + Ablage master.m3u8, einschl. Behandlung relativer Links
#	Die Ablage dient zur Auswertung der Einzelauflösungen, kann aber bei Kodi auch
#	zum Videostart verwendet werden. 
def ParseMasterM3u(li, url_m3u8, thumb, title):	
	PLog('ParseMasterM3u:'); 
	PLog(title); PLog(url_m3u8); PLog(thumb); 
	 
	title = UtfToStr(title)
	PLog(type(title))	
	
	sname = url_m3u8.split('/')[2]				# Filename: Servername.m3u8
	msg1 = "Datei konnte nicht "					# Vorgaben xbmcgui.Dialog
	msg2 = sname + ".m3u8"
	msg3 = "Details siehe Logdatei"
	
	page, msg = get_page(path=url_m3u8)			# 1. Inhalt m3u8 laden	
	PLog(len(page))
	if page == '':
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
	fpath = fname = '%s/resources/data/m3u8/%s' % (PluginAbsPath, fname)
	PLog('fpath: ' + fpath)
	msg = RSave(fpath, page)			# 3.  Inhalt speichern -> resources/m3u/
	if 'Errno' in msg:
		msg1 = msg1 + " gespeichert werden." 
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
	else:			
		# Hier Umlaute bisher nicht möglich (getestet: utf-8-Kodierung, urllib.quote)
		
		# Alternative: m3u8-lokal starten
		# 	fparams="&fparams=url=%s, title=%s, is_playable=%s" % (sname + ".m3u8", title, True)	
		fparams="&fparams=url=%s, title=%s" % (urllib.quote_plus(url_m3u8), title)	
		PLog('fparams ParseMasterM3u: ' + fparams)
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams) 

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
			# playlist = HTTP.Request(url).content   # wird abgewiesen
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
# PlayVideo: 
#	abs. Pfad in url erforderlich
# 	setProperty mit inputstreamaddon und inputstream.adaptive.manifest_type verursacht Klemmer
#
def PlayVideo(url, title, **kwargs):	
	PLog('PlayVideo:'); PLog(url); PLog(title)		
	
	# # SSL-Problem bei Kodi V17.6:  ERROR: CCurlFile::Stat - Failed: SSL connect error(35)
	url = url.replace('https', 'http')  

	li = xbmcgui.ListItem(path=url)
	li.setProperty('IsPlayable', 'true')

	xbmcplugin.setResolvedUrl(HANDLE, succeeded=(url != None), listitem=li)
	return
	
#---------------------------------------------------------------- 
# SSL-Probleme in Kodi mit https-Code 302 (Adresse verlagert) - Lösung:
#	 Redirect-Abfrage vor Abgabe an Kodi-Player
# Kommt vor: Kodi kann lokale Audiodatei nicht laden - Kodi-Neustart ausreichend.
# OK: BR, Bremen, SR, Deutschlandfunk
def PlayAudio(url, title, header=None,**kwargs):
	PLog('PlayAudio:'); PLog(title)
# todo: Abruf der https-Sender (geht nicht z.B. NJoy, od. dauert) 
#	Versuch mit lokaler ffmpeg-Installation
	
	page, msg = get_page(path=url, GetOnlyRedirect=True)  # Weiterleitung - Wiederherstellung https!
	PLog('PlayAudio Redirect_Url:' + page)
	if page:
		url = page

	if header:
		# PLog(header)
		url = '%s|%s' % (url, header) 

	if url.startswith('http') == False:		# lokale Datei
		url = os.path.abspath(url)
	PLog('PlayAudio Player_Url: ' + url)
	
	li = xbmcgui.ListItem(path=url)		# ListItem + Player reicht für BR
	li.setContentLookup(False)
	xbmc.Player().play(url, li, False)	# Player nicht mehr spezifizieren (0,1,2 - deprecated)

   
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
	#	Nach Auswahl einer Station wird in RadioLiveSender der Audiostream-Link ermittelt.

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
	li = home(li, ID=NAME)				# Home-Button	
	
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
		link_path,link_img, m3u8_master, geoblock = parseLinks_Mp4_Rtmp(path_content)	# mehrere Streamlinks auswerten,
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
					break								# dann bleibt es bei img_src (Fallback)
				PLog('headline: ' + headline.upper()); PLog(sname.upper());
				if sname.upper() == headline.upper():	# lokaler Sendername in  <sender> muss Sendernahme aus headline entspr.
					img = R(img)
					if os.path.exists(img):
						img_src = img
					else:
						img_src = link_img	# Fallback aus parseLinks_Mp4_Rtmp, ev. nur Mediathek-Symbol
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
			if mark == '1' or mark == '2':					
				subtitle = unescape(subtitle)
			headline = "%s | %s" % (headline, subtitle)			# für kodi subtitle -> label
				
			if slink:						# normaler Link oder Link über .m3u ermittelt
				# msg = ', Stream ' + str(i + 1) + ': OK'		# Log in parseLinks_Mp4_Rtmp ausreichend
				msg = ''
				if img_src.find('http') >= 0:	# Bildquelle Web
					img_src = img_src.replace('https', 'http')	# Kodi: SSL-Problem bei Abruf
					thumb=img_src
				else:							# Bildquelle lokal
					thumb=R(img_src)
				
				# slink = slink.replace('https', 'http')		# nicht i.V.m. https.replace in PlayAudio
				headline = headline.replace('"', '')			# json-komp. für func_pars in router()
				# Kodi Header: als Referer slink injiziert
				header='Accept-Encoding=identity;q=1, *;q=0&Accept-Language=de,en;q=0.9,fr;q=0.8,de-DE;q=0.7,da;q=0.6,it;q=0.5,pl;q=0.4,uk;q=0.3,en-US;q=0.2&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&Accept=*/*&Referer=%s&Connection=keep-alive&Range=bytes=0-' % slink
				# header=''
				fparams="&fparams={'url': '%s', 'title': '%s', 'header': '%s'}" % (urllib.quote_plus(slink), 
					urllib.quote_plus(headline), urllib.quote_plus(header))
				 # Alternativer Zusatz: 'is_playable': %s} % True
				PLog('fparams RadioAnstalten: ' + fparams)
				addDir(li=li, label=headline, action="dirList", dirID="PlayAudio", fanart=fanart, thumb=img_src, 
					fparams=fparams)	
												 	
			else:
				msg = ' Stream ' + str(i + 1) + ': nicht verfügbar'	# einzelnen nicht zeigen - verwirrt nur
			item_cnt = item_cnt +1
	
	PLog('Anzahl: ' + str(item_cnt))
	if item_cnt < 1:	      		# keine Radiostreams gefunden		
		PLog('oc = 0, keine Radiostreams gefunden') 		 
		line1 = '%s: keine Radiostreams gefunden / verfuegbar' % title
		line2 = 'URL:'
		line3 = '%s' % (path)
		xbmcgui.Dialog().ok(ADDON_NAME, line1, line2, line3)
		return li			
								
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	

###################################################################################################
#									ZDF-Funktionen
#
# 	Voreinstellungen: alle ZDF-Sender, ganze Sendungen, sortiert nach Datum
#	Anzahl Suchergebnisse: 25 - nicht beeinflussbar
# def ZDF_Search(query=None, title=L('Search'), s_type=None, pagenr='', **kwargs):
def ZDF_Search(query=None, title='Search', s_type=None, pagenr='', **kwargs):
	if query == '':
		query = get_keyboard_input() 

	query = query.strip()
	query = query.replace(' ', '+')		# Leer-Trennung bei ZDF-Suche mit +
	query = urllib2.quote(query, "utf-8")
	PLog('ZDF_Search'); PLog(query); PLog(pagenr); PLog(s_type)

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
	li = home(li, ID='ZDF')									# Home-Button

	if searchResult == '0':
		msg1 = 'Kein Ergebnis für >%s<' % query
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
				
	# offset=0: anders als bei den übrigen ZDF-'Mehr'-Optionen gibt der Sender Suchergebnisse bereits
	#	seitenweise aus, hier umgesetzt mit pagenr - offset entfällt	
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID=ID, offset=0)
	PLog('li, offset, page_cnt: %s, %s, %s' % (li, offset, page_cnt))
	
	# auf mehr prüfen (Folgeseite auf content-link = Ausschlusskriterum prüfen):
	#	im Gegensatz zu anderen ZDF-Seiten gibt  der Sender hier die Resultate seitenweise aus.
	# 	Daher entfällt die offset-Variante wiez.B. in BarriereArmSingle.
	pagenr = int(pagenr) + 1
	path = ZDF_Search_PATH % (query, pagenr)
	PLog(pagenr); PLog(path)
	page, msg = get_page(path=path)	
	content =  blockextract('class="artdirect"', page)
	if len(content) > 0:
		title = "Weitere Beiträge"
		fparams='&fparams=query=%s, s_type=%s, pagenr=%s' % (urllib2.quote(query), s_type, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
 
	xbmcplugin.endOfDirectory(HANDLE)
	
#-------------------------
def ZDF_Verpasst(title, zdfDate, offset=0):
	PLog('ZDF_Verpasst:'); PLog(title); PLog(zdfDate)

	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button

	path = ZDF_SENDUNG_VERPASST % zdfDate
	page, msg = get_page(path)
	if page == '':
		msg1 = "Abruf fehlgeschlagen | %s" % title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg, '')
		return li 
	PLog(path);	PLog(len(page))

	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='VERPASST', offset=offset)
	PLog("page_cnt: " + str(page_cnt))
		
	label = 'Mehr zu >Verpasst<, Gesamt: %s' % page_cnt
	PLog(offset)
	if offset:
		fparams='&fparams=title=%s, zdfDate=%s, offset=%s' % (title, zdfDate, offset)
		addDir(li=li, label=label, action="dirList", dirID="ZDF_Verpasst", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)

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
		fparams='&fparams=title=%s, element=%s' % (title, element)
		addDir(li=li, label=title, action="dirList", dirID="SendungenAZList", fanart=R(ICON_ZDF_AZ), 
			thumb=R(ICON_ZDF_AZ), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
def SendungenAZList(title, element, offset=0):	# Sendungen zm gewählten Buchstaben
	PLog('SendungenAZList:')
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
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=azPath, ID='DEFAULT', offset=offset)
	PLog(page_cnt)  
	if page_cnt == 0:	# Fehlerbutton bereits in ZDF_get_content
		return li
		
	title = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
	title = UtfToStr(title)
	if offset:
		fparams="&fparams={'title': '%s', 'element': '%s', 'offset': '%s'}" % (urllib2.quote(title_org), element, offset)
		addDir(li=li, label=title, action="dirList", dirID="SendungenAZList", fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), 
			fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# 	wrapper für Mehrfachseiten aus ZDF_get_content (multi=True). Dort ist kein rekursiver Aufruf
#	möglich (Übergabe Objectcontainer in Callback nicht möglich - kommt als String an)
#	Hinw.: Drei-Stufen-Test - Genehmigungsverfahren für öffentlich-rechtliche Telemedienangebote
#		s.  https://www.zdf.de/zdfunternehmen/drei-stufen-test-100.html
def ZDF_Sendungen(url, title, ID, offset=0):
	PLog('ZDFSendungen')
	PLog(title)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
				
	page, msg = get_page(path=url)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 						
					
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=url, ID='VERPASST', offset=offset)

	PLog(offset)
	if offset:
		title = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams="&fparams={'url': '%s', 'title': '%s', 'ID': '%s', 'offset': '0'}" \
			% (urllib2.quote(url), urllib2.quote(title), ID)
		addDir(li=li, label=title_org, action="dirList", dirID="ZDF_Sendungen", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
  
####################################################################################################
def Rubriken(name):
	PLog('Rubriken')
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
	rubriken =  blockextract('class=\"dropdown-item', listblock)
	
	for rec in rubriken:											# leider keine thumbs enthalten
		path = stringextract('href=\"', '\"', rec)
		path = ZDF_BASE + path
		title = stringextract('class=\"link-text\">', '</span>', rec)
		title = mystrip(title)
		if title == "Sendungen A-Z":	# Rest nicht mehr relevant
			break
		fparams='&fparams=title=%s, path=%s'	% (urllib2.quote(title), urllib2.quote(path))
		addDir(li=li, label=title, action="dirList", dirID="RubrikSingle", fanart=R(ICON_ZDF_RUBRIKEN), 
			thumb=R(ICON_ZDF_RUBRIKEN), fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-------------------------
def RubrikSingle(title, path, offset=0):
	PLog('RubrikSingle'); 
	
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
								
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='Rubriken', offset=offset)
	
	PLog(offset)
	if offset:
		title = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams='&fparams=title=%s, path=%s, offset=%s'	% (urllib2.quote(title), urllib2.quote(path), offset)
		addDir(li=li, label=title, action="dirList", dirID="RubrikSingle", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
def MeistGesehen(name, offset=0):
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
		
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='MeistGesehen', offset=offset)
	
	PLog("Mark2")
	PLog(offset)
	if offset:
		# PLog(name); PLog(page_cnt)
		title = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams="&fparams={'title': '%s', 'path': '%s', 'offset': '%s'}" % (urllib2.quote(title_org), 
			urllib2.quote(path), offset)
		addDir(li=li, label=title, action="dirList", dirID="RubrikSingle", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		
####################################################################################################
def NeuInMediathek(name, offset=0):
	PLog('NeuInMediathek:'); 
	title_org = name
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	path = ZDF_BASE
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Beitrag kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	#  1. Block extrahieren (Blöcke: Neu, Nachrichten, Sport ...)
	page = stringextract('>Neu in der Mediathek<','<h2 class="cluster-title"', page)
	PLog(len(page))
	 			
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='NeuInMediathek', offset=offset)
	
	PLog(offset)
	if offset:
		title = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams='&fparams=title=%s, path=%s, offset=%s'	% (urllib2.quote(title_org), urllib2.quote(path), offset)
		addDir(li=li, label=title, action="dirList", dirID="RubrikSingle", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE)
		
####################################################################################################
# ZDF Barrierefreie Angebote - Vorauswahl
# todo: Icons für UT + Gebärdensprache, vorh.: ICON_ZDF_HOERFASSUNGEN
def BarriereArm(title):				
	PLog('BarriereArm:')
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')										# Home-Button

	path = ZDF_BARRIEREARM
	page, msg = get_page(path=path)	
	if page == '':
		msg1 = 'Seite kann nicht geladen werden.'
		msg2, msg3 = msg.split('|')
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li 
	PLog(len(page))
	page = UtfToStr(page)
	
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
		fparams='&fparams=path=%s, title=%s' % (urllib2.quote(path), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="BarriereArmSingle", fanart=R(ICON_ZDF_BARRIEREARM), 
			thumb=R(ICON_ZDF_BARRIEREARM), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#-------------------------
# Aufrufer: BarriereArm
#	path in BarriereArm geladen, wir laden  erneut
def BarriereArmSingle(path, title, offset=0):
	PLog('BarriereArmSingle: ' + title)
	PLog(offset)
	
	title = UtfToStr(title)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID='ZDF')						# Home-Button
	
	page, msg = get_page(path=path)				# path=ZDF_BARRIEREARM
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
	
	li, offset, page_cnt  = ZDF_get_content(li=li, page=rec, ref_path=path, ID='BARRIEREARM', offset=offset)
	
	PLog(offset)
	if offset:
		label = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams="&fparams={'path': '%s', 'title': '%s', 'offset': '%s'}" \
			% (urllib2.quote(path), urllib2.quote(title_org), offset)
		addDir(li=li, label=label, action="dirList", dirID="BarriereArmSingle", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE)
			
####################################################################################################
def International(title, offset=0):
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
	 			
	li, offset, page_cnt = ZDF_get_content(li=li, page=page, ref_path=path, ID='International', offset=offset)
	
	PLog(offset);PLog(page_cnt)
	if offset:
		label = 'Mehr zu >%s<, Gesamt: %s' % (title_org, page_cnt)
		fparams="&fparams={'title': '%s', 'offset': '%s'}" % (urllib2.quote(title_org), offset)
		addDir(li=li, label=label, action="dirList", dirID="International", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
# Auswertung aller ZDF-Seiten
#	 
#	offset: für übergroße Seiten, die nicht wie die Suchergebn. als Folgeseiten mit pagenr organisiert sind.
#		Bsp. für übergroße Seite: Hörfassungen (145 am 28.9.2017)
#
# 	ID='Search' od. 'VERPASST' - Abweichungen zu Rubriken + A-Z

def ZDF_get_content(li, page, ref_path, offset=0, ID=None):	
	PLog('ZDF_get_content:'); PLog(ID); PLog(ref_path); PLog(offset)					
	PLog(len(page));			
	max_count = int(SETTINGS.getSetting('pref_maxZDFContent')) # max. Anzahl Elemente 
	PLog(max_count)
	offset = int(offset)
	page = UtfToStr(page)
	
	Bilderserie = False	
	if ID == 'Bilderserien':									# Aufruf: ZDF_Search
		Bilderserie = True										# für Titelergänzung (Anz. Bilder)
		ID='DEFAULT'											# Sätze ohne aufnehmen														
	
	img_alt = teilstring(page, 'class=\"m-desktop', '</picture>') # Bildsätze für b-playerbox
	title = ''
	if page.find('class=\"content-box gallery-slider-box') >= 0: 	# Bildgalerie (hier aus Folgeseiten)
		title = stringextract('\"big-headline\"  itemprop=\"name\" >', '</h1>', page)
		title = unescape(title)
		PLog(title)
		li, page_cnt = ZDF_Bildgalerie(li=li, page=page, mode='is_gallery', title=title)
		return li, offset, page_cnt # page_cnt: Bildzähler
	if page.find('name headline mainEntityOfPage') >= 0:  # spez. Bildgalerie, hier Bares für Rares
		headline = stringextract('name headline mainEntityOfPage\" >', '</h1>', page)
		if headline[0:7] == 'Objekte':		# Bsp.: Objekte vom 6. Dezember 2016
			li, page_cnt = ZDF_Bildgalerie(li=li, page=page, mode='pics_in_accordion-panels', title=headline)
			return li, offset, page_cnt # page_cnt: Bildzähler
		
	page_title = stringextract('<title>', '</title>', page)  # Seitentitel
	page_title = UtfToStr(page_title)
	page_title = page_title.strip()
	msg_notfound = ''
	if 'Leider kein Video verf' in page:					# Verfügbarkeit vor class="artdirect"
		msg_notfound = 'Leider kein Video verfügbar'		# z.B. Ausblick auf Sendung
		if page_title:
			msg_notfound = 'Leider kein Video verfügbar zu: ' + page_title
		
	pos = page.find('class="content-box"')					# ab hier verwertbare Inhalte 
	PLog('pos: ' + str(pos))
	if pos >= 0:
		page = page[pos:]
				
	page = UtfToStr(page)										# für Suche mit Umlauten
	content =  blockextract('class="artdirect"', page)
	if ID == 'NeuInMediathek':									# letztes Element entfernen (Verweis Sendung verpasst)
		content.pop()	
	page_cnt = len(content)
	PLog('content_Blocks: ' + str(page_cnt));
	
	if page_cnt == 0:											# kein Ergebnis oder allg. Fehler
		s = 'Es ist leider ein Fehler aufgetreten.'				# ZDF-Meldung Server-Problem
		if page.find('\"title\">' + s) >= 0:
			msg_notfound = s + ' Bitte versuchen Sie es später noch einmal.'
		else:
			msg_notfound = 'Leider keine Inhalte verfügbar.' 	# z.B. bei A-Z für best. Buchstaben 
			if page_title:
				msg_notfound = 'Leider keine Inhalte verfügbar zu: ' + page_title
			
		PLog('msg_notfound: ' + str(page_cnt))
		# kann entfallen - Blockbildung mit class="content-box" inzw. möglich. Modul zdfneo.py entfernt.
		#	Zeilen hier ab 1.1.2018 löschen:
		#if ref_path.startswith('https://www.zdf.de/comedy/neo-magazin-mit-jan-boehmermann'): # neue ZDF-Seite
		#	import zdfneo
		#	items = zdfneo.neo_content(path=ref_path, ID=ID)		# Abschluss dort
		#	return li , offset, page_cnt 		
		
	if msg_notfound:											# gesamte Seite nicht brauchbar		
		msg1 = msg_notfound
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
		
	if page.find('class="b-playerbox') > 0 and page.find('class="item-caption') > 0:  # mehrspaltig: Video gesamte Sendung?
		first_rec = img_alt +  stringextract('class="item-caption', 'data-tracking=', page) # mit img_alt
		content.insert(0, first_rec)		# an den Anfang der Liste
		# GNNPLog(content[0]) # bei Bedarf
					
	if 	max_count:								# 0 = 'Mehr..'-Option ausgeschaltet
		delnr = min(page_cnt, offset)
		del content[:delnr]						# Sätze bis offset löschen (bzw. bis Ende records)
	PLog(len(content))
	PLog("Mark1")

	items_cnt=0									# listitemzähler
	for rec in content:	
		if 'class="loader"></span>Weitere laden' in rec: # Loader erreicht=Ende 
			return li, 0, page_cnt
			
		pos = rec.find('</article>')		   # Satz begrenzen - bis nächsten Satz nicht verwertbare Inhalte möglich
		if pos > 0:
			rec = rec[0:pos]
		# PLog(rec)  # bei Bedarf
			
		if ID <> 'DEFAULT':					 			# DEFAULT: Übersichtsseite ohne Videos, Bsp. Sendungen A-Z
			if 'title-icon icon-502_play' not in rec:  	# Videobeitrag?
				continue		
		multi = False			# steuert Mehrfachergebnisse 
		
		meta_image = stringextract('<meta itemprop=\"image\"', '>', rec)
		#PLog('meta_image: ' + meta_image)
		# thumb  = stringextract('class=\"m-8-9\"  data-srcset=\"', ' ', rec)    # 1. Bild im Satz m-8-9 (groß)
		thumb_set = stringextract('class=\"m-8-9\"  data-srcset=\"', '/>', rec) 
		thumb_set = thumb_set.split(' ')		
		
		for thumb in thumb_set:				# kleine Ausgabe 240x270 suchen
			if thumb.find('240x270') >= 0:
				break		
		# PLog(thumb_set); PLog(thumb)

		if thumb == '':											# 1. Fallback thumb	
			thumb  = stringextract('class=\"b-plus-button m-small', '\"', meta_image)
		if thumb == '':											# 2. Fallback thumb (1. Bild aus img_alt)
			thumb = stringextract('data-srcset=\"', ' ', img_alt) 	# img_alt s.o.	
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
		PLog('href_title: ' + href_title)
		if 	href_title == 'ZDF Livestream' or href_title == 'Sendung verpasst':
			continue
			
		# Pfad				
		plusbar_title = stringextract('plusbar-title=\"', '\"', rec)	# Bereichs-, nicht Einzeltitel, nachrangig
		# plusbar_path = stringextract('plusbar-path=\"', '\"', rec)    # path ohne http(s)
		path =  stringextract('plusbar-url=\"', '\"', rec)				# plusbar nicht vorh.? - sollte nicht vorkommen
		PLog('path: ' + path); PLog('ref_path: %s' % ref_path)	
		if path == '' or path == ref_path:					# kein Pfad oder Selbstreferenz
			continue
		
		# Datum, Uhrzeit Länge	
		if 'icon-301_clock icon' in rec:						# Uhrsymbol  am Kopf mit Datum/Uhrzeit
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
		duration = stringextract('m-border">', '</', duration)			# Ende </dd> od. </dt>
		if duration == '':
			PLog("%s" % 'Videolänge:')
			duration = stringextract('Videolänge:', '</dl>', rec) # Länge - 2. Variante bzw. fehlend
			duration = stringextract('">', '</', duration)			
		PLog('duration: ' + duration);
		
		pic_cnt = stringextract('Anzahl Bilder:', '<dt class', rec)	# Bilderzahl bei Bilderserien
		pic_cnt = stringextract('">', '</', pic_cnt)				# Ende </dd> od. </dt>
		PLog('Bilder: ' + pic_cnt);
			
		title = href_title 
		if title == '':
			title = plusbar_title
		if Bilderserie == True:
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
			
		PLog('neuer Satz')
		PLog(thumb);PLog(path);PLog(title);PLog(summary);PLog(tagline); PLog(multi);
		 
		if multi == True:
			fparams='&fparams=url=%s, title=%s, ID=%s, offset=0' % (urllib2.quote(path), 
				urllib2.quote(title), ID)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Sendungen", fanart=thumb, 
				thumb=thumb, fparams=fparams, summary=summary)
		else:							
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'tagline': '%s'}" % (urllib2.quote(path),
				urllib2.quote(title), thumb, tagline)	
			addDir(li=li, label=title, action="dirList", dirID="GetZDFVideoSources", fanart=thumb, thumb=thumb, 
				fparams=fparams, tagline=tagline)
				
		items_cnt = items_cnt+1
		if max_count:					# summary + tagline werden als Info-Items nicht mitgezählt
			# Mehr Seiten anzeigen:		# 'Mehr...'-Callback durch Aufrufer	
			cnt = items_cnt + offset		
			PLog('Mehr-Test: cnt %d, items_cnt %d, offset %d, max_count %d, page_cnt %d' \
				% (cnt, items_cnt, offset,max_count, page_cnt)) 
			if cnt > page_cnt:			# Gesamtzahl erreicht - Abbruch
				offset=0
				break					# Schleife beenden
			elif items_cnt >= max_count:	# Mehr, wenn max_count erreicht
				offset = offset + max_count-1
				break					# Schleife beenden
		# break # Test 1. Satz
		
	return li, offset, page_cnt 
	
#-------------

####################################################################################################
# Subtitles: im Kopf der videodat-Datei enthalten (Endung .vtt). Leider z.Z. keine Möglichkeit
#	bekannt, diese einzubinden
# Ladekette für Videoquellen s. get_formitaeten
# 
def GetZDFVideoSources(url, title, thumb, tagline, segment_start=None, segment_end=None):
#	title = urllib2.unquote(title); tagline = urllib2.unquote(tagline)	
	PLog('GetZDFVideoSources:'); PLog(url); PLog(tagline); 
#	title = transl_umlaute(title)
	PLog(title)
				
	li = xbmcgui.ListItem()
	urlSource = url 		# für ZDFotherSources

	page, msg = get_page(url)
	if page == '':
		msg1 = 'GetZDFVideoSources: Problem beim Abruf der Videoquellen.'
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
#	apiToken1 = UtfToStr(apiToken1); apiToken2 = UtfToStr(apiToken1)
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

	only_list = ["h264_aac_ts_http_m3u8_http"]					# Video-Items erstellen: m3u8-Formate
	li, download_list = show_formitaeten(li=li, title_call=title, formitaeten=formitaeten, tagline=tagline,
		thumb=thumb, only_list=only_list,geoblock=geoblock)		  
		
	title_oc='weitere Video-Formate'							# Video-Items erstellen: weitere Formate
	if SETTINGS.getSetting('pref_use_downloads'):	
		title_oc=title_oc + ' und Download'
	PLog("title_oc: " + title_oc)
		
	PLog(title); PLog(title_oc); PLog(tagline); PLog(sid); 
	title = UtfToStr(title); tagline = UtfToStr(tagline); 
	
	# li = Parseplaylist(li, videoURL, thumb)	# hier nicht benötigt - das ZDF bietet bereits 3 Auflösungsbereiche
	fparams="&fparams={'title': '%s', 'tagline': '%s', 'thumb': '%s', 'sid': '%s', 'apiToken1': '%s', 'apiToken2': '%s'}" \
		% (urllib2.quote(title), urllib2.quote(tagline), urllib2.quote(thumb), sid, apiToken1, apiToken2)
	addDir(li=li, label=title_oc, action="dirList", dirID="ZDFotherSources", fanart=thumb, thumb=thumb, fparams=fparams)
	
	if sub_path:												# Info bei Untertitel
		if SETTINGS.getSetting('pref_UT_Info') == 'true':
			msg1 = 'Info: für dieses Video wurden Untertitel geladen.' 
			msg2 = 'Verfügbar im Pluginverzeichnis:'
			sub_path = sub_path.split(ADDON_ID)[-1]					# Pfad beschneiden
			msg3 = "..%s" % sub_path
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		
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
		thumb=thumb, only_list=only_list, geoblock=geoblock)		  
					
	# high=0: 	1. Video bisher höchste Qualität:  [progressive] veryhigh
	li = test_downloads(li,download_list,title_org,summary_org,tagline,thumb,high=0)  # Downloadbutton(s)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
#-------------------------
#	Ladekette für Videoquellen ab 30.05.2017:
#		1. Ermittlung der apiToken (in configuration.json), nur anfangs 2016 unverändert, Verwendung in header
#		2. Sender-ID sid ermitteln für profile_url (durch Aufrufer GetZDFVideoSources, ZDFotherSources)
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
	#	mittels chrome)	ab 08.10.2017 für ZDF in GetZDFVideoSources ermittelt + als Dict gespeichert + 
	#	hier injiziert (s.u.)
	# Header Api-Auth + Host reichen manchmal, aber nicht immer - gesetzt in get_page.
	# 15.10.2018 Requests ausgelagert nach get_page. 
	# Kodi-Version: Wegen Problemen mit dem Parameterhandling von Listen und Dicts wird hier
	#	 nur der Api-Auth Key übergeben (Rest in get_page). 
	#	
	if ID == 'NEO':
		header = {'Api-Auth': "Bearer d90ed9b6540ef5282ba3ca540ada57a1a81d670a",'Host':"api.zdf.de", 'Accept-Encoding':"gzip, deflate, sdch, br", 'Accept':"application/vnd.de.zdf.v1.0+json"}
	else:
		PLog(apiToken1)									# s. GetZDFVideoSources
		header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de', 'Accept-Encoding': 'gzip, deflate, sdch, br', \
			'Accept':'application/vnd.de.zdf.v1.0+json'}" % apiToken1
	
	page, msg	= get_page(path=profile_url, header=header, JsonPage=True)	
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

	# apiToken2 aus GetZDFVideoSources. header ohne quotes in get_page leer 
	header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de', 'Accept-Encoding': 'gzip, deflate, sdch, br', \
		'Accept':'application/vnd.de.zdf.v1.0+json'}" % apiToken2
	page, msg	= get_page(path=videodat_url, header=header, JsonPage=True)
	PLog("request_json: " + page[:40])

	if page == '':	# Abbruch - ev. Alternative ngplayer_2_3 versuchen
		PLog('videodat_url: Laden fehlgeschlagen')
		return '', '', ''
	PLog(page[:100])	# "{..attributes" ...
		
	# Kodi: https://kodi.wiki/view/Features_and_supported_formats#Audio_playback_in_detail 
	#	AQTitle, ASS/SSA, CC, JACOsub, MicroDVD, MPsub, OGM, PJS, RT, SMI, SRT, SUB, VOBsub, VPlayer
	#	Für Kodi eignen sich beide ZDF-Formate xml + vtt, umbenannt in *.sub oder *.srt
	#	VTT entspricht SubRip: https://en.wikipedia.org/wiki/SubRip
	subtitles = stringextract('\"captions\"', '\"documentVersion\"', page)	# Untertitel ermitteln, bisher in Plex-
	subtitles = blockextract('\"class\"', subtitles)						# Channels nicht verwendbar
	PLog('subtitles: ' + str(len(subtitles)))
	sub_path = ''
	if len(subtitles) == 2:
		# sub_xml = subtitles[0]									# xml-Format für Kodi ungeeignet
		sub_vtt = subtitles[1]	
		# PLog(sub_vtt)
		# sub_xml_path = stringextract('\"uri\": \"', '\"', sub_xml)# xml-Format
		sub_vtt_path = stringextract('\"uri\": \"', '\"', sub_vtt)	
		# PLog('Untertitel xml:'); PLog(sub_xml_path)
		PLog('Untertitel vtt:'); PLog(sub_vtt_path)
		
		local_path = "%s/%s" % (SUBTITLESTORE, sub_vtt_path.split('/')[-1])
		local_path = local_path.replace('.vtt', '.sub')				# Endung für Kodi anpassen
		local_path = os.path.abspath(local_path)
		PLog(local_path)
		try:
			if os.path.isfile(local_path) == False:					# schon vorhanden?
				urllib.urlretrieve(sub_vtt_path, local_path)
			sub_path = local_path									# für Info in GetZDFVideoSources
		except Exception as exception:
			PLog(str(exception))			

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
def show_formitaeten(li, title_call, formitaeten, tagline, thumb, only_list, geoblock):	
	PLog('show_formitaeten:')
	PLog(only_list); PLog(title_call)
	# PLog(formitaeten)		# bei Bedarf

	title_call = urllib2.unquote(title_call)
	title_call = UtfToStr(title_call); tagline = UtfToStr(tagline); geoblock = UtfToStr(geoblock)		
	
	
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
						PLog('encoding:')
						title = '%s. %s [m3u8] Bandbreite und Aufloesung automatisch | %s' % (str(i), quality, title_call)
						title = UtfToStr(title)

						#  Download + Ablage master.m3u8:
						li = ParseMasterM3u(li=li, url_m3u8=url, thumb=thumb, title=title)	
					else:									# m3u8 enthält Auflösungen high + med
						title = 'Qualitaet: ' + quality + ' | Typ: ' + typ + ' ' + facets 
						title = '%s. Qualitaet: %s | Typ: %s %s' % (str(i), quality, typ, facets)
						title = UtfToStr(title)
						download_list.append(title + '#' + url)					# Download-Liste füllen	
						fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib.quote_plus(url), urllib.quote_plus(title))
						addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams) 
													
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
			msg2 = "../resources/data/slides/%s" % fname
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
			title = unescape(title)
			title = UtfToStr(title)
			
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
				
			tagline = unescape(title_org); tagline = cleanhtml(tagline)
			summ = unescape(summ)
			PLog('neu');PLog(title);PLog(thumb);PLog(summ[0:40]);
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
#  PhotoObject fehlt in kodi - wir speichern die Bilder in resources/data/slides und
#	übergeben an xbmc.executebuiltin('SlideShow..
#  ClearUp in resources/data/slides s. Modulkopf
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
def Parseplaylist(li, url_m3u8, thumb, geoblock, **kwargs):	# master.m3u8 auswerten, Url muss komplett sein
#													# container muss nicht leer ein (siehe SingleSendung)
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
#		 crossdomain access denied. Keine Probleme mit OpenPHT und VLC
#  10.08.2017 Filter für Video-Sofort-Format - wieder entfernt 17.02.2018

	PLog ('Parseplaylist: ' + url_m3u8)
	playlist = ''
	# seit ZDF-Relaunch 28.10.2016 dort nur noch https
	if url_m3u8.find('http://') == 0 or url_m3u8.find('https://') == 0:		# URL oder lokale Datei?			
		playlist, msg = get_page(path=url_m3u8)	
		if playlist == '':
			line1 = 'Playlist kann nicht geladen werden.'
			line2 = 'URL: %s '	% (url_m3u8)
			line3 = 'Fehler: %s'	% (msg)
			xbmcgui.Dialog().ok(ADDON_NAME, line1, line2, line3)
			return li			
	else:													
		playlist = RLoad('/m3u8/%s' % url_m3u8) 
	 
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
			thumb=thumb_org
			if BandwithInt and BandwithInt <=  100000: 		# vermutl. nur Audio (Bsp. ntv 48000, ZDF 96000)
				Resolution = Resolution + ' (vermutlich nur Audio)'
				thumb=R(ICON_SPEAKER)
				
			lable = Resolution+geoblock						# Kodi: statt summary + tagline in Plex
			title =  UtfToStr(title)
			lable = "%s. %s | %s" % (str(li_cnt), title, lable)
			
			# quote für url erforderlich wg. url-Inhalt "..sd=10&rebase=on.." - das & erzeugt in router
			#	neuen Parameter bei dict(parse_qsl(paramstring)
			fparams="&fparams={'url': '%s', 'title': '%s'}" % (urllib.quote_plus(url), title)
			PLog('fparams Parseplaylist: ' + fparams)
			addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams) 
							
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
					func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
					PLog("json.loads func_pars: " + func_pars)
					PLog('json.loads func_pars type: ' + str(type(func_pars)))
					# func_pars = func_pars.encode("utf-8")			# entf.
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
PLog('PLUGIN_URL: ' + PLUGIN_URL)		# sys.argv[0], plugin://plugin.video.ardundzdf/
PLog('ADDON_ID: ' + ADDON_ID); PLog(SETTINGS); PLog(ADDON_NAME);PLog(SETTINGS_LOC);
PLog(ADDON_PATH);PLog(ADDON_VERSION);
PLog('HANDLE: ' + str(HANDLE))


PluginAbsPath = os.path.dirname(os.path.abspath(__file__))
PLog('PluginAbsPath: ' + PluginAbsPath)

PLog('Start_Plugin')
if __name__ == '__main__':
	try:
		router(sys.argv[2])
	except Exception as e: 
		msg = str(e)
		PLog('network_error: ' + msg)
		# xbmcgui.Dialog().ok(ADDON_NAME, 'network_error', msg)
#		Main()			

























