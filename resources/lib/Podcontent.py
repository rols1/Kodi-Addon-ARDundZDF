# -*- coding: utf-8 -*-
# Podcontent.py	- ab V4.9.0 nur noch für Sammeldownload (DownloadMultiple)
#					vormals für PodFavoritenListe (obsolet durch Merkliste) 
#
#	04.11.2019 Migration Python3
#	21.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
# 	<nr>4</nr>								# Numerierung für Einzelupdate
#	Stand: 14.11.2023


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

# Python
import sys, os, subprocess 
import json, re
import datetime, time

# Addonmodule + Funktionsziele 
import ardundzdf					# -> thread_getfile, AudioWebMP3 
from resources.lib.util import *
 

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('Podcontent_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 

ICON_MAIN_POD			= 'radio-podcasts.png'
ICON_MEHR 				= "icon-mehr.png"
ICON_DOWNL 				= "icon-downl.png"
ICON_NOTE 				= "icon-note.png"
ICON_STAR 				= "icon-star.png"

ARD_AUDIO_BASE = 'https://api.ardaudiothek.de/'
####################################################################################################	
#----------------------------------------------------------------  
# Sammeldownload lädt alle angezeigten Podcasts herunter.
# Im Gegensatz zum Einzeldownload wird keine Textdatei zum Podcast angelegt.
# DownloadExtern kann nicht von hier aus verwendet werden, da der wiederholte Einzelaufruf 
# 	von Curl kurz hintereinander auf Linux Prozessleichen hinterlässt: curl (defunct)
# Zum Problem command-line splitting (curl-Aufruf) und shlex-Nutzung siehe:
# 	http://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex
# Das Problem >curl "[Errno 36] File name too long"< betrifft die max. Pfadlänge auf verschiedenen
#	Plattformen (Posix-Standard 4096). Teilweise ist die Pfadlänge manuell konfigurierbar.
#	Die hier gewählte platform-abhängige Variante funktioniert unter Linux + Windows (Argumenten-Länge
#	bis ca. 4 KByte getestet) 
#
# Rücksprung-Problem: unter Kodi keine wie unter Plex beoachtet.
# Bei Sammeldownload wird mit path_url_list zu thread_getfile verzweigt.
# 27.02.2020 Code für curl/wget-Download entfernt
# 23.02.2022 Sammeldownload deaktiviert: bei den api-Calls für die 
#	PodFavoriten enthalten die json-Seiten keine Download-Url 
# 25.03.2022 Sammeldownload reaktiviert: Buttons + Dict-Ablage 
#	in Audio_get_sendung + Audio_get_sendung_api. Hier Auswertung
#	der Quelle bei Web-Urls (www.ardaudiothek.de) in AudioWebMP3 (no_gui) 	
#
#----------------------------------------------------------------  	
def DownloadMultiple(key):									# Sammeldownloads
	PLog('DownloadMultiple:'); 
	import shlex											# Parameter-Expansion
	
	downl_list =  Dict("load", key)
	# PLog('downl_list: %s' % downl_list)

	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')							# Home-Button
	
	rec_len = len(downl_list)
	dest_path = SETTINGS.getSetting('pref_download_path')
			
	path_url_list = []										# für int. Download									

	if os.path.isdir(dest_path)	== False:					# Downloadverzeichnis prüfen		
		msg1='Downloadverzeichnis nicht gefunden:'	
		msg2=dest_path
		MyDialog(msg1, msg2, '')		
		return
		
	#---------------------------							# 1. Schritt: Auswahl
	if 	SETTINGS.getSetting('pref_check_podlist') == 'true':
		tlist=[]											# Titel-Liste
		for item in downl_list:
			tlist.append(item.split("#")[0])
		
		title = u"Unerwünschte Podcasts anklicken. OK nach Auswahl:"
		if PYTHON2:											
			selected = range(0, len(tlist))
		else:												# PY3: range=iterator
			selected = list(range(0, len(tlist)))
		tlist = xbmcgui.Dialog().multiselect(title, tlist, preselect=selected)
		PLog("tlist: %s" % str(tlist))
		if tlist ==  None or len(tlist) == 0:				# ohne Auswahl
			return
		
		new_downl_list=[]									# Auswahl auf downl_list anwenden
		for i in tlist:	
			new_downl_list.append(downl_list[i])				

	#---------------------------							# 2. Schritt: Serien-Check / Frage Dateimuster
	new_downl_list = episode_check(new_downl_list)
	PLog(new_downl_list[0])
		
	#---------------------------							# 3. Schritt: mp3-Quellen + Dateinamen ermitteln	
	msg1 = "Fertige Dateinamen für die Podcasts"
	if "www.ardaudiothek.de" in str(new_downl_list):
		msg1 = "%s und ermittle die mp3-Quellen" % msg1
	msg2 = 'Anzahl der Dateien: %s' % len(new_downl_list)
	ret=MyDialog(msg1, msg2, msg3="", ok=False, yes='OK')
	if ret  == False:
		return
				
	i = 0
	for rec in new_downl_list:								# Parameter für path_url_list erzeugen
		i = i + 1
		#if  i > 2:											# reduz. Testlauf
		#	break
		title, url = rec.split('#')
		title = unescape(title)								# schon in PodFavoriten, hier erneut nötig 
		
		if "www.ardaudiothek.de" in url:					# mp3-Quelle ermitteln bei Webquellen
			url = ardundzdf.AudioWebMP3(url, title="", thumb="", Plot="", ID="", no_gui="true")			
			
		if 	SETTINGS.getSetting('pref_generate_filenames'):	# Dateiname aus Titel generieren
			dfname = make_filenames(py2_encode(title)) + '.mp3'
			PLog(dfname)
		else:												# Bsp.: Download_2016-12-18_09-15-00.mp3
			now = datetime.datetime.now()
			mydate = now.strftime("%Y-%m-%d_%H-%M-%S")	
			dfname = 'Download_' + mydate + '.mp3'

		# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Podcast, Zieldatei_kompletter_Pfad|Podcast ..
		fullpath = os.path.join(dest_path, dfname)
		fullpath = os.path.abspath(fullpath)		# os-spezischer Pfad
		path_url_list.append('%s|%s' % (fullpath, url))		
	
	#---------------------------							# 3. Schritt: Download	
	PLog(sys.platform)
	from threading import Thread							# Dialog +  Abbruchmögl. in thread_getfile
	textfile='';pathtextfile='';storetxt='';url='';fulldestpath=''
	now = datetime.datetime.now()
	timemark = now.strftime("%d.%m.%Y, %H:%M:%S Uhr")
	background_thread = Thread(target=ardundzdf.thread_getfile,
		args=(textfile,pathtextfile,storetxt,url,fulldestpath,path_url_list,timemark))
	background_thread.start()
		
	# return li						# Kodi-Problem: wartet bis Ende Thread			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	return							# hier trotz endOfDirectory erforderlich

#---------------------------------------------------------------- 
# detektiert / konvertiert Serienkennzeichungen in der Downloadliste
# Aufruf: DownloadMultiple
# Rückgabe: Liste mit geänderten Titeln od. downl_list unverändert  (je
#	nach Setting) 
# 15.08.2022 re.search statt string-funcs
#
def episode_check(downl_list):
	PLog("episode_check:")
	
	PLog(SETTINGS.getSetting('pref_check_episode'))
	if SETTINGS.getSetting('pref_check_episode') == 'false':
		return downl_list			# Liste unverändert
	
	pat1 = r'<\d+/\d+>'				# Der Raub des Goldes <1/16> 
	pat2 = r' Folge \d+/\d+'		# Väter und Söhne. Folge 22/24
	newlist=[]
	i=0				# Zähler konvertierte Zeilen
	for rec in downl_list:		
		title, url = rec.split('#')
		PLog(title)
		try:
			match = re.search(pat1, title)
			if match == None:
				match = re.search(pat2, title)
			if match:
				s = match.group()
			else:
				s = "#|#"										# Auschluss-Muster
				
			if s and title.find(s) > 0:							# Muster am Anfang: unverändert
				PLog("match: %s, pos: %d" % (s, title.find(s)))
				title = title.replace(s, "")					# Muster entfernen
				
				vals = re.search(r'(\d+/\d+)', s).group(0)		# '22/24' 
				val1, val2 = vals.split("/")
																# Numerierung voranstellen:
				new_line = "%02d_%02d_%s#%s" % (int(val1), int(val2), title, url) 
				newlist.append(new_line)
				i=i+1
			else:
				PLog("ohne Konv.")
				newlist.append(rec)								# Zeile unverändert (ohne Serienkennz.) 
				
		except Exception as exception:
				err = str(exception)
				PLog(err)
				PLog("Exception - ohne Konv.")
				newlist.append(rec)			# Zeile unverändert (ohne Serienkennz.) 			
	
	PLog("konvertiert: %d" % i)			
	PLog(newlist[0])
	return newlist









