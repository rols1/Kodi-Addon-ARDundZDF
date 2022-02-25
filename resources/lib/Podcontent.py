# -*- coding: utf-8 -*-
# Podcontent.py	- Aufruf durch PodFavoritenListe 
#
# Die Funktionen dienen der Auswertung von Radio-Podcasts der Regionalsender. 
# Ab 19.06.2019 Umstellung auf die zentrale ARD-Audiothek
#
#	Die Sammlung der Ergebnisse in 2-dim-Record entfällt (war vorher aufgrund der
#	versch. Sender-Schemata erforderlich).
#
# Die angezeigten Dateien stehen für Downloads zur Verfügung (einzeln und gesamte Liste)
#
# Basis ist die Liste podcast-favorits.txt (Default/Muster im Ressourcenverzeichnis), die
# 	Liste enthält weitere  Infos zum Format und zu bereits unterstützten Podcast-Seiten
# 	- siehe nachfolgende Liste Podcast_Scheme_List
#
#	04.11.2019 Migration Python3
#	21.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
# 	<nr>1</nr>								# Numerierung für Einzelupdate
#	Stand: 23.02.2022


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
import ardundzdf					# -> thread_getfile 
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

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 

ICON_MAIN_POD			= 'radio-podcasts.png'
ICON_MEHR 				= "icon-mehr.png"
ICON_DOWNL 				= "icon-downl.png"
ICON_NOTE 				= "icon-note.png"
ICON_STAR 				= "icon-star.png"

ARD_AUDIO_BASE = 'https://api.ardaudiothek.de/'
####################################################################################################

# Aufrufer: PodFavoritenListe (Haupt-PRG)
# Bsp. path: www.ardaudiothek.de/quarks-hintergrund/53095244
#	hier Abruf im json-Format, aber nicht komp. mit AudioContentJSON
#
# xml-format verworfen, da Dauer des mp3 fehlt.
# 30.07.2021 Anpassung an renovierte Audiothek (alte Links -> neue api-Calls) 
# 23.02.2022 dto - akt. Sammeldownloads deaktiviert, da mp3_urls nur in Webpage vorh., 
#	api-pages aber zum Blättern notwendig.
# 
def PodFavoriten(title, path):
	PLog('PodFavoriten:'); PLog(path);	
	title_org = title
	base = "https://api.ardaudiothek.de/"
	
	if '//www.ardaudiothek.de/' in path:			#  alte Links -> neue api-Calls
		href_add = "?offset=0&limit=20"
		url_id 	= path.split('/')[-1]
		path = ARD_AUDIO_BASE + "programsets/%s/%s" % (url_id, href_add)
		#path = "https://api.ardaudiothek.de/search?query=%s" 					
	path = path.replace('/items', '')				# aus Cluster-Suche entf. (key-error Audio_get_json_single)
	 
	li = xbmcgui.ListItem()
	#li = home(li, ID='ARD Audiothek')				# Home-Button
		
	ardundzdf.Audio_get_sendung_api(path, title)	# -> DownloadMultiple
	
	'''	
	# Rückgabe reaktivieren (cnt, downl_list)
	PLog("Laenge: %d" % len(downl_list))																# Sammel-Download-Button?				
	if SETTINGS.getSetting('pref_use_downloads') == 'true':
		if len(downl_list) > 1:
			#downl_list=downl_list[:1]	# Debug
			# Sammel-Downloads - alle angezeigten Favoriten-Podcasts downloaden?
			#	für "normale" Podcasts erfolgt die Abfrage in SinglePage
			title=u'[B]Download! Alle angezeigten %d Podcasts speichern?[/B]' % len(downl_list)	
			summ = u'Download von insgesamt %s Podcasts' % len(downl_list)	
			Dict("store", 'downl_list', downl_list) 
			Dict("store", 'URL_rec', downl_list) 

			fparams="&fparams={'key_downl_list': 'downl_list', 'key_URL_rec': 'downl_list'}" 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.DownloadMultiple", 
				fanart=R(ICON_DOWNL), thumb=R(ICON_DOWNL), fparams=fparams, summary=summ)
	'''

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
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

#----------------------------------------------------------------  	
def DownloadMultiple(key_downl_list, key_URL_rec):			# Sammeldownloads
	PLog('DownloadMultiple:'); 
	import shlex											# Parameter-Expansion
	
	downl_list =  Dict("load", "downl_list")
	# PLog('downl_list: %s' % downl_list)

	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')							# Home-Button
	
	rec_len = len(downl_list)
	dest_path = SETTINGS.getSetting('pref_download_path')
			
	path_url_list = []									# für int. Download									

	if os.path.isdir(dest_path)	== False:				# Downloadverzeichnis prüfen		
		msg1='Downloadverzeichnis nicht gefunden:'	
		msg2=path
		MyDialog(msg1, msg2, '')		
		return
		
	msg1 = 'Starte Download im Hintergrund'		
	msg2 = 'Anzahl der Dateien: %s' % len(downl_list)
	msg3 = 'Ablage: ' + SETTINGS.getSetting('pref_download_path')
	ret=MyDialog(msg1, msg2, msg3, ok=False, yes='OK')
	if ret  == False:
		return		
	
	i = 0
	for rec in downl_list:									# Parameter-Liste erzeugen
		i = i + 1
		#if  i > 2:											# reduz. Testlauf
		#	break
		title, url = rec.split('#')
		title = unescape(title)								# schon in PodFavoriten, hier erneut nötig 
		if 	SETTINGS.getSetting('pref_generate_filenames'):	# Dateiname aus Titel generieren
			dfname = make_filenames(py2_encode(title)) + '.mp3'
			PLog(dfname)
		else:												# Bsp.: Download_2016-12-18_09-15-00.mp4  oder ...mp3
			now = datetime.datetime.now()
			mydate = now.strftime("%Y-%m-%d_%H-%M-%S")	
			dfname = 'Download_' + mydate + '.mp3'

		# Parameter-Format: -o Zieldatei_kompletter_Pfad Podcast-Url -o Zieldatei_kompletter_Pfad Podcast-Url ..
		# path_url_list (int. Download): Zieldatei_kompletter_Pfad|Podcast, Zieldatei_kompletter_Pfad|Podcast ..
		fullpath = os.path.join(dest_path, dfname)
		fullpath = os.path.abspath(fullpath)		# os-spezischer Pfad
		path_url_list.append('%s|%s' % (fullpath, url))
		
	PLog(sys.platform)
	from threading import Thread	# thread_getfile
	textfile='';pathtextfile='';storetxt='';url='';fulldestpath=''
	now = datetime.datetime.now()
	timemark = now.strftime("%Y-%m-%d_%H-%M-%S")
	background_thread = Thread(target=ardundzdf.thread_getfile,
		args=(textfile,pathtextfile,storetxt,url,fulldestpath,path_url_list,timemark))
	background_thread.start()
		
	# return li						# Kodi-Problem: wartet bis Ende Thread			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	return							# hier trotz endOfDirectory erforderlich

#---------------------------------------------------------------- 
#	lokale Dateiverzeichnisse /Shares in	podcast-favorits.txt
#		Audiodateien im Verz. mit Abspielbutton listen 
#		Browser zeigen, falls keine Dateien im Verz.
# 	library://music/ funktioniert nicht - Kodi-Player kann die
#		Dateiquelle zur Browserausgabe nicht auflösen (Bsp.:
#		 audio_path: musicdb://sources/1/788/931/?albumartistsonly=
#			false&artistid=788&sourceid=1/4393.mp3
 
def PodFolder(title, path):
	PLog('PodFolder:'); PLog(path);
	allow = [".MIDI", ".AIFF", ".WAV", ".WAVE", ".AIFF", ".MP2", ".MP3", ".AAC", 
				".AAC", ".VORBIS", ".AC3", ".DTS", ".ALAC", ".AMR", ".FLAC"
			]
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARDaudio')							# Home-Button

	if 'library://music/' in path:							# Sound-Bibliothek
		msg1=u'Sound-Bibliothek nicht verfügbar:'	
		msg2=path
		MyDialog(msg1, msg2, '')		
		return li		

	path = xbmc.translatePath(path)
	PLog(path);
	if not xbmcvfs.exists(path):
		msg1='Verzeichnis nicht gefunden:'	
		msg2=path
		MyDialog(msg1, msg2, '')	
		return li		
	
	dirs, files = xbmcvfs.listdir(path)
	PLog('dirs: %s, files: %s' % (len(dirs), len(files)))

	dialog = xbmcgui.Dialog()
	mytype=0; heading='Audioverzeichnis wählen'
	d_ret = dialog.browseSingle(mytype, heading, 'music', '', False, False, path)	
	PLog('d_ret: ' + d_ret)
	dirs, files = xbmcvfs.listdir(d_ret)
	PLog(dirs);PLog(files[:3]);

	fstring = '\t'.join(files)							# schnelle Teilstringsuche in Liste
	# if '.mp3' not in fstring: return li
		
	cnt=0
	summ = d_ret
	PLog('title: %s, summ: %s' % (title, summ))		
	for audio in files:
		d_ret=py2_encode(d_ret)
		audio_path = os.path.join(d_ret, audio)
		PLog("audio_path: " + audio_path)
		ext = os.path.splitext(audio_path)[-1]
		if up_low(ext) not in allow:
			continue	
			
		title=py2_encode(title); audio=py2_encode(audio);
		summ=py2_encode(summ); audio_path=py2_encode(audio_path);
		thumb = R(ICON_NOTE)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
			(quote(audio_path), quote(title),  quote(thumb), quote(audio))
		addDir(li=li, label=audio, action="dirList", dirID="PlayAudio", fanart=R(ICON_NOTE), 
			thumb=R(ICON_NOTE), fparams=fparams, summary=summ, tagline=title, mediatype='music')
		cnt=cnt+1
			
	if cnt == 0:
		msg1='keine Audiodateien gefunden. Verzeichnis:'	
		msg2=d_ret
		MyDialog(msg1, msg2, '')	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#---------------------------------------------------------------- 
#	Fügt Audiothek-Suchergebnis der Datei podcast-favorits.txt
#		hinzu
#	Aufruf: AudioSearch -> AudioContentJSON
#	Mehrfachsätze (Folgebeiträge) werden abgelehnt
# 
def PodAddFavs(title, path, fav_path, mehrfach=''):
	PLog('PodAddFavs:')
	PLog(title); PLog(path); PLog(fav_path); 
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Audiothek')								# Home-Button

	if int(mehrfach) > 0:						# Vorab-Test auf Mehrfach-Sätze
		msg1=u'Nur Einzelbeiträge erlaubt! Folgebeiträge: %s' % mehrfach
		msg2=u'Verweise auf Folgebeiträge werden verworfen.' 
		msg3=u'Trotzdem übernehmen?'
		ret=MyDialog(msg1, msg2, msg3, ok=False)
		if ret  == False:
			return
		
	try:										# Vorab-Test auf korr. Datei
		Inhalt = RLoad(fav_path,abs_path=True)	# podcast-favorits.txt laden
	except:
		Inhalt = ''
	if  Inhalt is None or Inhalt == '' or 'podcast-favorits.txt' not in Inhalt:				
		msg1=u'Datei podcast-favorits.txt nicht gefunden, nicht lesbar oder falsche Datei.'
		msg2=u'Bitte Einstellungen prüfen.'
		MyDialog(msg1, msg2, '')
		return

	title=py2_encode(title); path=py2_encode(path);	
	PLog(type(title)); PLog(type(Inhalt));

	if title in Inhalt:
		msg1 = ">%s< ist bereits enthalten" % title
		msg2 = "Trotzdem übernehmen?"
		ret=MyDialog(msg1, msg2, '', ok=False)
		if ret  == False:
			return
		
	if ADDON_ID in fav_path:
		msg1=u'Diese Datei podcast-favorits.txt wird beim nächsten Update überschrieben!'
		msg2=u'Bitte eine Kopie außerhalb des Addons anlegen und in den Settings den Dateipfad anpassen.'
		MyDialog(msg1, msg2, '')
	
	line = "%s\t\t| %s\n" % (title, path)					# neue Zeile
	msg1 = 'podcast-favorits.txt'
	icon = R(ICON_STAR)
	try:
		f = open(fav_path, 'a')								# nur anhängen
		f.write(line)	
		f.close()
		msg2 = u'Eintrag hinzugefügt'
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)	# Fertig-Info

	except Exception as exception:
		msg2 = str(exception) 
		PLog(msg2)
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)	# Fehler-Hinweis
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)










