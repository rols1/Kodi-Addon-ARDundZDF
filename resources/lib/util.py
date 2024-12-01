# -*- coding: utf-8 -*-
###################################################################################################
#							 util.py - Hilfsfunktionen Kodiversion
#	Modulnutzung: 
#					import resources.lib.util as util
#					PLog=util.PLog;  home=util.home; ...  (manuell od.. script-generiert)
#
#	convert_util_imports.py generiert aus util.py die Zuordnungen PLog=util.PLog; ...
####################################################################################################
# 
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
# 	
# 	<nr>115</nr>										# Numerierung für Einzelupdate
#	Stand: 01.12.2024

# Python3-Kompatibilität:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

# Standard:
import os, sys, subprocess
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:					
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve 
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse , urlsplit, parse_qs
	LOG_MSG = xbmc.LOGNOTICE 				# s. PLog
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	LOG_MSG = xbmc.LOGINFO 					# s. PLog
	try:									
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

	
import time, datetime
from time import sleep  # PlayVideo

from threading import Thread	
from threading import Timer	# KeyListener


import glob, shutil
from io import BytesIO	# Python2+3 -> get_page (compressed Content), Ersatz für StringIO
import gzip, zipfile
import base64 			# url-Kodierung für Kontextmenüs
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import string, textwrap

import shlex			# Parameter-Expansion für subprocess.Popen (os != windows)
	
# Globals
PYTHON2 = sys.version_info.major == 2	# Stammhalter Pythonversion 
PYTHON3 = sys.version_info.major == 3

NAME			= 'ARD und ZDF'
KODI_VERSION 	= xbmc.getInfoLabel('System.BuildVersion')
KODI_MAJOR 		= int(re.search(r'(\d+)', KODI_VERSION).group(1))	


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
ICON_TOOLS 				= "icon-tools.png"
ICON_WARNING 			= "icon-warning.png"

# Github-Icons zum Nachladen aus Platzgründen
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'

ARDStartCacheTime = 300						# 5 Min.

#---------------------------------------------------------------- 
# prüft addon.xml auf mark - Rückgabe True, False
#	benötigt u.a. für Check der python-Version - falls
#	3.x.x wird global ADDON_DATA (Modul-Kopf) neu
#	gesetzt - s. check_DataStores
# ADDON_DATA 3.x.x (Kodi 19 Matrix, 20 Nexus):
#	../.kodi/userdata/addon_data/plugin.video.ardundzdf
# ADDON_DATA 2.25.0 (Kodi 18 Leia):
#	../.kodi/userdata/ardundzdf_data
# Aufruf von allen Modulen.Köpfen einschl. Haupt-PRG
# 15.05.2020 Codec-Error beim Einlesen in Matrix - Austausch
#	open/read gegen xbmcvfs.File/read
# LOG_MSG s. Modulkopf
#
def check_AddonXml(mark):
	ADDON_XML		= os.path.join(ADDON_PATH, "addon.xml")
	xbmc.log("%s --> %s" % ('ARDundZDF', 'check_AddonXml:'), LOG_MSG)
	f = xbmcvfs.File(ADDON_XML)		# Byte-Puffer
	xml_content	= f.readBytes()
	f.close()
	if mark in str(xml_content):
		ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
		return True
	else:
		return False

#---------------------------------------------------------------- 
	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)

M3U8STORE 		= os.path.join(ADDON_DATA, "m3u8") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
TEMP_ADDON		= xbmc.translatePath("special://temp")			# Backups
FLAG_OnlyUrl	= os.path.join(ADDON_DATA, "onlyurl")			# Flag PlayVideo_Direct -> strm-Modul
STRM_URL		= os.path.join(ADDON_DATA, "strmurl")			# Ablage strm-Url (PlayVideo_Direct)	
PLAYLIST_ALIVE 	= os.path.join(ADDON_DATA, "playlist_alive")	# Lebendsignal für PlayMonitor (leer)

PLAYLIST 		= 'livesenderTV.xml'		# TV-Sender-Logos erstellt von: Arauco (Plex-Forum). 											
ICON_MAIN_AUDIO	= 'ard-audiothek.png'
ICON_MAIN_ZDFMOBILE	= 'zdf-mobile.png'
ICON_PHOENIX	= 'phoenix.png'			
ICON_ARTE		= 'arte_Mediathek.png'			

# Github-Icons zum Nachladen aus Platzgründen
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'
BASE_URL 		= 'https://classic.ardmediathek.de'

STARTLIST		= os.path.join(ADDON_DATA, "startlist") 

#----------------------------------------------------------------
# Kodi Matrix: Wechsel   xbmc.LOGNOTICE -> xbmc.LOGINFO - siehe
#	https://forum.kodi.tv/showthread.php?tid=353818&pid=2943669#pid2943669,
#	https://github.com/xbmc/xbmc/compare/master@%7B1day%7D...master
#	https://github.com/i96751414/script.logviewer/blob/matrix/resources/lib/utils.py
# 10.05.2020 Rückwechsel zu LOGNOTICE - LOGINFO klappt nicht mit akt. 
#			Matrix-Build 
# 14.05.2020 dummy = fehlerhafter PLog-Call z.B. pytube-Modul (helpers.py, mixins.py,
#			gefixt). dummy-Ausgabe vorerst belassen (Debug)
# Bei Änderungen check_AddonXml berücksichtigen (xbmc.log direkt)
# 13.09.2020 LOGNOTICE/LOGINFO in  Abhängigkeit von PY2/PY3 gesetzt:
#	https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?postID=606035
#	LOG_MSG - s. Modulkopf
#
def PLog(msg, dummy=''):
	if DEBUG == 'false':
		return
	
	xbmc.log("%s --> %s" % ('ARDundZDF', msg), LOG_MSG)
	if dummy:		# Debug (s.o.)
		xbmc.log("%s --> %s" % ('PLog_dummy', dummy), LOG_MSG)
		
#---------------------------------------------------------------- 
# 08.04.2020 Konvertierung 3-zeiliger Dialoge in message (Multiline)
#  	Anlass: 23-03-2020 Removal of deprecated features (PR) - siehe:
#	https://forum.kodi.tv/showthread.php?tid=344263&pid=2933596#pid2933596
#	https://github.com/xbmc/xbmc/blob/master/xbmc/interfaces/legacy/Dialog.h
# ok triggert Modus: Dialog().ok, Dialog().yesno()
#
def MyDialog(msg1, msg2='', msg3='', ok=True, cancel='Abbruch', yes='JA', heading='', autoclose=0):
	PLog('MyDialog:')
	
	msg = msg1
	if msg2:							# 3 Zeilen -> Multiline
		msg = "%s\n%s" % (msg, msg2)
	if msg3:
		msg = "%s\n%s" % (msg, msg3)
	if heading == '':
		heading = ADDON_NAME
	
	if ok:								# ok-Dialog
		if PYTHON2:
			return xbmcgui.Dialog().ok(heading=heading, line1=msg)
		else:							# Matrix: line1 -> message
			return xbmcgui.Dialog().ok(heading=heading, message=msg)

	else:								# yesno-Dialog
		if PYTHON2:
			ret = xbmcgui.Dialog().yesno(heading=heading, line1=msg, nolabel=cancel, yeslabel=yes,\
				autoclose=autoclose)
		else:							# Matrix: line1 -> message
			ret = xbmcgui.Dialog().yesno(heading=heading, message=msg, nolabel=cancel, yeslabel=yes,\
				autoclose=autoclose)
		return ret

#----------------------------------------------------------------
# get_list_indices: Umkehrung von get_items_from_list
#	gleicht die Elemente my_items mit my_list ab
#	und speichert den jew. Index in index_list
#	Rückgabe: Liste der Indices od. []
# Bsp. dialog.multiselect in FilterToolsWork
#
def get_list_indices(my_items, my_list):
	PLog('get_list_indices:')
	
	index_list = []
	for item in my_items:
		if item in my_list:
			index_list.append(my_list.index(item))
	return index_list	
#----------------------------------------------------------------
# get_items_from_list: Umkehrung von get_list_indices
#	ermittelt die items in my_list passend zum
#	jew. Index
#	Rückgabe: Liste der items od. []
# Bsp. dialog.multiselect in FilterToolsWork
#
def get_items_from_list(my_indices, my_list):
	PLog('get_items_from_list:')
	PLog(my_indices)
	
	item_list = []
	for i in my_indices:
		try:
			if my_list[i]:
				item_list.append(my_list[i])
		except:
			pass
	return item_list	
#---------------------------------------------------------------- 
# Home-Button, Aufruf: item = home(item=item, ID=NAME)
#	Liste item von Aufrufer erzeugt
# 27.06.2022 filterstatus hier und in addDir entfernt (obsolet, da  Home-
#	Button optional)
# 16.03.2023 optionaler Param ltitle, Bsp. Arte (übersetzt) 
#
def home(li, ID, ltitle=""):												
	PLog('home: ' + ID)	
	FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
		
	if SETTINGS.getSetting('pref_nohome') == 'true':	# keine Homebuttons
		return li
	if ID == 'ARD Neu':									# 15.06.2022 Zusatz Neu entfernt
		ID = 'ARD'
			
	# Position 1 bei aufst. Sortierung:					# ZERO WIDTH SPACE u"\u200B" wirkt nicht mit Color
	Home = " Home: "									#	getestet: 2000 - 202F (invisible-characters-ascii)
	title = u' Zurück zum Hauptmenü %s' % ID
	if ltitle:											# Übersetzung (außer für 'ARD und ZDF')
		title=ltitle
	
	tag = "Status [B]Ausschluss-Filter[/B]: AUS"		# nur Untermenüs ARD, ZDF + Audiothek, nicht Module
	if SETTINGS.getSetting('pref_usefilter') == 'true':	
		tag = tag.replace('AUS','[COLOR blue]EIN[/COLOR]')										
		page = RLoad(FILTER_SET, abs_path=True)			# akt. Filter laden, [Errno 2] möglich
		tag = "%s \nFilter [B]aktuell[/B]:\n%s" % (tag, page)
		
	summ = "Status [B]Sofortstart[/B]: AUS\nStatus [B]Downloads[/B]: EIN"
	if SETTINGS.getSetting('pref_video_direct') == 'true':	
		summ = "Status [B]Sofortstart[/B]: EIN\nStatus [B]Downloads[/B]: AUS"	

	if ID == NAME:		# 'ARD und ZDF'
		name = Home + NAME
		fparams="&fparams={}"
		img = R('icon.png') 
		name = ' Home: ARD und ZDF'
		addDir(li=li, label=name, action="dirList", dirID="Main", fanart=img, 
			thumb=img, tagline='', summary=summ, fparams=fparams)
		
	if ID == 'ARD':			
		img = R('ard-mediathek.png') 
		name = Home + "ARD Mediathek"
		fparams="&fparams={'name': '%s'}"	% quote(name)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", 
			fanart=img, thumb=img, tagline=tag, summary=summ, fparams=fparams)
			
	if ID == 'ZDF' or ID == 'ZDFStart' or ID == 'ZDFfunkStart':
		title = u' Zurück zum Hauptmenü ZDF'
		img = R('zdf-mediathek.png')
		name = Home + "ZDF Mediathek"
		fparams="&fparams={'name': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="Main_ZDF", fanart=img, 
			thumb=img, tagline=tag, summary=summ, fparams=fparams)
		
	if ID == 'ZDFmobile':
		img = R('zdf-mobile.png')
		name = Home + "ZDFmobile"
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=img, thumb=img, summary=summ, fparams=fparams)
	
	# 	03.06.2021 ARD-Podcasts (Classic) entfernt		
			
	if ID == 'ARD Audiothek':
		img = R(ICON_MAIN_AUDIO)
		name = Home + "ARD Audiothek"
		fparams="&fparams={'title': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="AudioStart", fanart=img, 
			thumb=img, tagline=tag, summary=summ, fparams=fparams)
			
	if ID == '3Sat':
		img = R('3sat.png')
		name = Home + "3Sat"
		fparams="&fparams={'name': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Main_3Sat", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)

	if ID == 'Kinderprogramme':
		img = R('childs.png')
		name = Home + ID
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Main_childs", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)

	if ID == 'TagesschauXL':
		img = ICON_MAINXL		# github
		name = Home + ID
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.Main_XL", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)
			
	if ID == 'phoenix':
		img = R(ICON_PHOENIX)
		name = Home + ID
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Main_phoenix", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)

	if ID == 'arte':
		img = R(ICON_ARTE)
		name = Home + ID
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.arte.Main_arte", fanart=img, 
			thumb=img, summary=summ, fparams=fparams)

	return li
	 
#---------------------------------------------------------------- 
#   Leia-Version: data-Verzeichnis liegt 2 Ebenen zu hoch, funktioniert aber.
#	03.04.2019 data-Verzeichnis des Addons:
#  		Check /Initialisierung / Migration
# 	27.05.2019 nur noch Check (s. Forum:
#		www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?pageNo=23#post528768
#	Die Funktion checkt bei jedem Aufruf des Addons data-Verzeichnis einschl. Unterverzeichnisse 
#		auf Existenz und legt bei Bedarf neu an. User-Info nur noch bei Fehlern (Anzeige  
#		beschnittener Verzeichnispfade im Kodi-Dialog nur verwirrend).
#	13.03.2020 abhängig von check_AddonXml wird bei der Matrix-Version des Addons
#		das data-Verzeichnis für Kodi korrekt angelegt im Verz.:
#		../.kodi/userdata/addon_data/plugin.video.ardundzdf/
#	05.05.2020 zusätzlich wird die Filterliste angelegt falls noch nicht existent 
#				(mit den beiden bisher verwendeten Begriffen) - korresp. Datei:
#				filter_set (FILTER_SET).  
#
def check_DataStores():
	PLog('check_DataStores:')
	store_Dirs = ["Dict", "slides", "subtitles", "Inhaltstexte", 
				"m3u8"]
	filterfile = os.path.join(ADDON_DATA, "filter.txt") 
	filter_pat =  "<filter>\nhörfassung\naudiodeskription\nuntertitel\ngebärdensprache\n</filter>\n"
				
	# Check 
	#	falls ein Unterverz. fehlt, erzeugt make_newDataDir alle
	#	Datenverz. oder einzelne fehlende Verz. neu.
	ok=True	
	for Dir in store_Dirs:						# Check Unterverzeichnisse
		Dir_path = os.path.join(ADDON_DATA, Dir)
		if os.path.isdir(Dir_path) == False:	
			PLog('Datenverzeichnis fehlt: %s' % Dir_path)
			ok = False
			break
	
	if ok and os.path.isfile(filterfile):
		return 'OK %s '	% ADDON_DATA			# Verz. + Filterdatei existieren - OK
	else:
		# neues leeres Verz. mit Unterverz. anlegen / einzelnes fehlendes 
		#	Unterverz. anlegen / Filterdatei anlegen
		ret = make_newDataDir(store_Dirs, filterfile, filter_pat)	
		if ret == True:						# ohne Dialog
			msg1 = 'Datenverzeichnis angelegt - Details siehe Log'
			msg2=''; msg3=''
			PLog(msg1)
			# MyDialog(msg1, msg2, msg3)  # OK ohne User-Info
			return 	'OK - %s' % msg1
		else:
			msg1 = "Fehler beim Anlegen des Datenverzeichnisses:" 
			msg2 = ret
			msg3 = 'Bitte Kontakt zum Entwickler aufnehmen'
			PLog("%s\n%s" % (msg2, msg3))	# Ausgabe msg1 als exception in make_newDataDir
			MyDialog(msg1, msg2, msg3)
			return 	'Fehler: Datenverzeichnis konnte nicht angelegt werden'
				
#---------------------------
# ab Version 1.5.6
# 	erzeugt neues leeres Datenverzeichnis oder fehlende Unterverzeichnisse
def  make_newDataDir(store_Dirs, filterfile, filter_pat):
	PLog('make_newDataDir:')
				
	if os.path.isdir(ADDON_DATA) == False:		# erzeugen, falls noch nicht vorh.
		try:  
			os.mkdir(ADDON_DATA)
		except Exception as exception:
			ok=False
			PLog(str(exception))
			return str(exception)		
				
	ok=True
	for Dir in store_Dirs:						# Unterverz. erzeugen
		Dir_path = os.path.join(ADDON_DATA, Dir)	
		if os.path.isdir(Dir_path) == False:	
			try:  
				os.mkdir(Dir_path)
			except Exception as exception:
				ok=False
				PLog(str(exception))
				break
	if ok:										# Abschluss: Filterliste speichern
		if os.path.isfile(filterfile) == False:
			err_msg = RSave(filterfile, filter_pat)
			if err_msg == '':
				PLog("Fehler beim Anlegen der Filterliste") # ohne Dialog	
		return True
	else:
		return str(exception)
		
#---------------------------
# sichert Verz. für check_DataStores für Daten-Migration 
#	Leia->Matrix. Wegen Problemen auf verschied. Systemen
# nicht mehr genutzt . s. changelog V1.5.6
# 
def getDirZipped(path, zipf):
	PLog('getDirZipped:')	
	for root, dirs, files in os.walk(path):
		for file in files:
			zipf.write(os.path.join(root, file)) 
#----------------------------------------------------------------  
# Die Funktion Dict speichert + lädt Python-Objekte mittels Pickle.
#	Um uns das Handling mit keys zu ersparen, erzeugt die Funktion
#	trotz des Namens keine dicts. Aufgabe ist ein einfacher
#	persistenter Speicher. Der Name Dict lehnt sich an die
#	allerdings wesentlich komfortablere Dict-Funktion in Plex an.
#
#	Falls (außerhalb von Dict) nötig, kann mit der Zusatzfunktion 
#	name() ein Variablenname als String zurück gegeben werden.
#	
#	Um die Persistenz-Variablen von den übrigen zu unterscheiden,
#	kennzeichnen wir diese mit vorangestelltem Dict_ (ist aber
#	keine Bedingung).
#
# Zuweisungen: 
#	Bsp. für Speichern:
#		 Dict('store', "Dict_name", value)
#			Dateiname: 		"Dict_name"
#			Wert in:		value
#	Bsp. für Laden:
#		CurSender = Dict("load", "CurSender")
#
#	CacheTime: Dauer in sec (60=1 min, 3600=1 std, 86400=1 tag)
#   Bsp. für CacheTime: 5*60 (5min) - Verwendung bei "load", Prüfung mtime 
#	ev. ergänzen: OS-Verträglichkeit des Dateinamens

def Dict(mode, Dict_name='', value='', CacheTime=None):
	PLog('Dict: ' + mode)
	PLog('Dict: ' + str(Dict_name))
	PLog('Dict: ' + str(type(value)))
	dictfile = os.path.join(DICTSTORE, str(Dict_name))
	PLog("dictfile: " + dictfile)
	
	if mode == 'store':	
		try:					# try wg. ukrain. Schrift 
			with open(dictfile, 'wb') as f: pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
			f.close
			return True
		except:	
			PLog("store_Problem")
			return False
	if mode == 'remove':		# einzelne Datei löschen
		try:
			 os.remove(dictfile)
			 return True
		except:	
			return False
			
	if mode == 'ClearUp':			# Files im Dictstore älter als maxdays löschen
		maxdays = int(Dict_name)
		return ClearUp(DICTSTORE, maxdays*86400) # 1 Tag=86400 sec
			
	if mode == 'load':	
		try:						# try wg. ukrain. Schrift 		
			if os.path.exists(dictfile) == False:
				PLog('Dict: %s nicht gefunden' % dictfile)
				return False
		except:	
			PLog("load_Problem")
			return False
		if CacheTime:
			mtime = os.path.getmtime(dictfile)	# modified-time
			now	= time.time()
			CacheLimit = now - CacheTime		# 
			PLog("now %d, mtime %d, CacheLimit: %d, CacheTime: %d" % (now, mtime, CacheLimit, CacheTime))
			if CacheLimit > mtime:
				PLog('Cache miss: CacheLimit > mtime')
				return False
			else:
				PLog('Cache hit: load')	
		try:			
			with open(dictfile, 'rb')  as f: data = pickle.load(f)
			f.close
			PLog('load from Cache')
			return data
		# Exception  ausführlicher: s.o.
		except Exception as e:	
			PLog('UnpicklingError' + str(e))
			return False

#-------------------------
# Zusatzfunktion für Dict - gibt Variablennamen als String zurück
# Aufruf: name(var=var) - z.Z. nicht genutzt
def name(**variables):				
	s = [x for x in variables]
	return s[0]
#----------------------------------------------------------------
# Dateien löschen älter als seconds - nicht rekursiv
#		directory 	= os.path.join(path)
#		seconds		= int (1 Tag=86400, 1 Std.=3600)
# Ältere enthaltene Ordner werden ohne Leertest entfernt 
#	(nur 1 Ebene!)
def ClearUp(directory, seconds, keep_dirs=False):	
	PLog('ClearUp: %s, sec: %s' % (directory, seconds))	
	PLog('älter als: ' + seconds_translate(seconds, days=True))
	PLog("keep_dirs: " + str(keep_dirs))
	now = time.time()
	cnt_files=0; cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 		# leer, fehlend -> leere Liste
		PLog("ClearUp: globFiles " + str(len(files)))
		# PLog(" globFiles: " + str(files))
		for f in files:
			#PLog(f)
			#PLog(os.stat(f).st_mtime)
			#PLog(now - seconds)
			if os.stat(f).st_mtime < (now - seconds):
				if os.path.isfile(f):	
					PLog('entfernte_Datei: ' + f)
					os.remove(f)
					cnt_files = cnt_files + 1
				if os.path.isdir(f):		# Verz. ohne Leertest entfernen
					if keep_dirs:
						PLog('entferntes Verz.: ' + f)
						shutil.rmtree(f, ignore_errors=True)
						cnt_dirs = cnt_dirs + 1
		PLog("ClearUp: entfernte Dateien %s, entfernte Ordner %s" % (str(cnt_files), str(cnt_dirs)))	
		return True
	except Exception as exception:	
		PLog(str(exception))
		return False

#---------------------------------------------------------------- 
# u.a. für AddonInfos
# raw=False: Rückgabe humanbytes,  sonst Bytes
def get_dir_size(directory, raw=False):
	PLog('get_dir_size: ' + str(raw))
	size=0

	for dirpath, dirnames, filenames in os.walk(directory):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			# skip symbolic link
			if not os.path.islink(fp):
				size += os.path.getsize(fp)
	if raw:
		return size
	else:
		return humanbytes(size)	
#---------------------------------------------------------------- 
# checkt Existenz + Größe Datei fpath
# Rückgabe True falls > 2 Byte
def check_file(fpath):
	PLog('check_file:')
	if os.path.exists(fpath):
		s = os.path.getsize(fpath)
		PLog(u"Länge: %d" % s)
		if s > 2:				# min: \n\r
			return True
			
	return False
#---------------------------------------------------------------- 
# leere Verz. rekursiv löschen, z.B. SLIDESTORE
# Aufrufer: Bildershow-Funktionen
def DelEmptyDirs(directory):
	PLog('DelEmptyDirs:')
	cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 
		for f in files:
			if os.path.isdir(f):
				if len(os.listdir(f)) == 0:
					shutil.rmtree(f)				# leeres Verz. löschen
					cnt_dirs = cnt_dirs + 1
		PLog("DelEmptyDirs: entfernte Ordner %s" % str(cnt_dirs))
		return True
	except Exception as exception:	
		PLog("DelEmptyDirs_error: " + str(exception))
		return False
	
#---------------------------------------------------------------- 
# liest Setting direkt aus setting.xml 
# hier: .kodi/userdata/addon_data/plugin.video.ardundzdf/settings.xml
# für Problemfälle (z.Z. Monitor in epgRecord)
def get_Setting(ID):
	PLog('get_Setting:')
	USERDATA	= xbmc.translatePath("special://userdata")
	SETTINGS_XML= os.path.join(USERDATA, "addon_data", ADDON_ID, "settings.xml")
	
	page = RLoad(SETTINGS_XML, abs_path=True)
	lines = page.splitlines()
	for line in lines:
		if ID in line:
			val = stringextract('>', '<', line)
			return val
			
	return ''
	
#---------------------------------------------------------------- 
# checkt url auf Vorkommen in skip_list (nur html-Links)
# Aufrufer prüft auf leere Url! 
# wg. abweichenden Url's bei identischem Ziel wird nur
# 	der letzte Teil der Url geprüft (zwischen / und .html)
def check_urlend(url, skip_list):
	PLog('check_urlend:')
	url_org=url	
	if ".html" in url_org:
		url_org = url_org.split(".html")[0]		# Bsp. doku-reportage-portraet-100
	url_org = url_org.split("/")[-1]
	
	for url in skip_list:
		if ".html" in url:
			url = url.split(".html")[0]
		url = url.split("/")[-1]
		PLog("url_org: %s, url: %s" % (url_org, url))
		if url in url_org:
			return True
			
	return False
	
#----------------------------------------------------------------  
# Listitems verlangen encodierte Strings auch bei Umlauten. Einige Quellen liegen in unicode 
#	vor (s. json-Auswertung in get_page) und müssen rückkonvertiert  werden.
# Hinw.: Teilstrings in unicode machen str-Strings zu unicode-Strings.
# für Python2	
# 19.11.2019 abgelöst durch py2_encode aus Kodi-six
def UtfToStr(line):
	PLog('UtfToStr:')
	return py2_encode(line)			# wirkt nur in Python2: Unicode -> str
	
def up_low(line, mode='up'):
	try:
		if PYTHON2:	
			if isinstance(line, unicode):
				line = line.encode('utf-8')
		if mode == 'up':
			return line.upper()
		else:
			return line.lower()
	except Exception as exception:	
		PLog('up_low: ' + str(exception))
	return up_low

#----------------------------------------------------------------  
# In Kodi fehlen die summary- und tagline-Zeilen der Plexversion. Diese ersetzen wir
#	hier einfach durch infoLabels['Plot'], wobei summary und tagline durch 
#	2 Leerzeilen getrennt werden (Anzeige links unter icon).
#
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen) - hier erfolgt die Umsetzung li.setInfo(type="video").
#		Die Kontextmenü-Einträge zum Video (z.B.: bei .. fortsetzen) übernimmt dann Kodi mit
#		Eintrag in die Datenbank MyVideos116.db (Tabs u.a. bookmark, files).s
#		Mehr s. PlayVideo
#
#	Kontextmenüs (Par. cmenu): base64-Kodierung wurde 2019 benötigt für url-Parameter (nötig für
#		router) und als Prophylaxe gegen durch doppelte utf-8-Kodierung erzeugte Sonderzeichen.
#		Dekodierung erfolgt in Watch + ShowFavs. Nicht mehr benötigt, falls nochmal: s. Commit
#		9137781 on 16 Oct 2019.
#		cmenu triggert Kontextmenü, weitere Param. dessen Eigenschaften (Bsp. start_end für 
#			K-Menü "Sendung aufnehmen" <- EPG_ShowSingle).
#
#		Kodi-Problem: werden für eine Liste verschiedene Kontext-Einträge angelegt, verwendet
#			Kodi alle definierten Einträge. Unpassende Kontext-Einträge lassen sich nur durch
#			zusätl. Listenelemente erreichen, z.B. 1 Element für Folgebeiträge und 1 Element
#			für Einzelvideos, z.B. li2=xbmcgui.ListItem() in get_json_content (ARDnew).
#
#	Sortierung: i.d.R. unsortiert (Reihenfolge wie Web), erford. für A-Z-Seiten (api/podcasts)
#		Hinw.: bei Sortierung auf Homebutton verzichten 
#
#	21.03.2020 Coding-Phänomen Merkliste: Param action + dirID mutieren zu unicode, wenn in thumb-url 
#		ein unbekanntes Zeichen auftritt - Bsp. persÃ¶nlich, Ursache: fehlerhaftes unquote_plus
#		unter python2. Workaround: py2_encode für action + dirID (addDir OK, aber falsche thumb-url)
#		und Erweiterung von decode_url
#
# 	31.03.2020 merkname ersetzt label im Kontextmenü Merkliste (label kann Filter-Prefix enthalten). 
#	30.06.2020 Hinw.: im Kontextmenü für fparam verwendete Params müssen identisch encodiert sein,
#		sonst schlägt die json-Dekodierung in router fehl.
#
# 	04.07.2020 Erweiterung Kontextmenüs "Sendung aufnehmen" (EPG_ShowSingle)
# 	08.07.2020 Erweiterung Kontextmenüs "Recording TV-Live" (EPG_ShowAll)  
# 	18.04.2022 Erweiterung Kontextmenüs "Abgleich Videotitel mit Medienbibliothek" 
#	05.02.2023 Erweiterung Kontextmenüs EPG (Menü TV-Livestreams)
#	10.11.2023 ShowFavs verhindert "Hinzufügen" im Kontextmenü
#
def addDir(li, label, action, dirID, fanart, thumb, fparams, summary='', tagline='', mediatype='',\
		cmenu=True, merkname='', start_end='', EPG_ID='', ShowFavs=''):
	PLog('addDir:');
	label_org=label				# s. 'Job löschen' in K-Menüs
	label=py2_encode(label)
	PLog('addDir_label: {0}, action: {1}, dirID: {2}'.format(label[:100], action, dirID))
	PLog(mediatype);
	action=py2_encode(action); dirID=py2_encode(dirID); 
	summary=py2_encode(summary); tagline=py2_encode(tagline); 
	fparams=py2_encode(fparams); fanart=py2_encode(fanart); thumb=py2_encode(thumb);
	merkname=py2_encode(merkname); start_end=py2_encode(start_end);
	PLog('addDir_summary: {0}, tagline: {1}, mediatype: {2}, cmenu: {3}'.format(summary[:80], tagline[:80], mediatype, cmenu))

	li.setLabel(label)			# Kodi Benutzeroberfläche: Arial-basiert für arabic-Font erf.
	# PLog('summary, tagline: {0}, {1}'.format(summary, tagline))
	Plot = ''
	if tagline:								
		Plot = tagline
	if summary:	
		Plot = Plot +"\n\n" + summary
		
	# ListItem.setInfo() deprecated -> [Nexus] API changes to VideoStreamDetail and InfoTagVideo API's
	#	s. forum.kodi.tv/showthread.php?tid=370707 und
	#	codedocs.xyz/AlwinEsch/kodi/group__python__xbmcgui__listitem.html
	#	KODI_VERSION s. Main()
	PLog("KODI_MAJOR: %d" % KODI_MAJOR)
	if KODI_MAJOR >=20:
		videoinfo = li.getVideoInfoTag()
	if mediatype == 'video': 	# "video", "music" setzen: List- statt Dir-Symbol
		if KODI_MAJOR >=20:
			videoinfo.setTitle(label); videoinfo.setPlot(Plot); videoinfo.setMediaType("video")
		else:
			li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot, "mediatype": "video"})	
		isFolder = False		# nicht bei direktem Player-Aufruf - OK mit setResolvedUrl
		li.setProperty('IsPlayable', 'true')					
	else:
		if KODI_MAJOR >=20:
			videoinfo.setPlot(Plot); videoinfo.setTitle(label); 
		else:
			li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot})	
		li.setProperty('IsPlayable', 'false')
		isFolder = True	

	li.setArt({'thumb':thumb, 'icon':thumb, 'fanart':fanart})
	if SETTINGS.getSetting('pref_sort_label') == 'true':			# Testaddon: Sortierung 
		# kein Unterschied zw. SORT_METHOD_LABEL / SORT_METHOD_LABEL_IGNORE_THE
		xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
		xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL)		# od. SORT_METHOD_TITLE
		# xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)		# falls für "verfügbar bis" möglich
	PLog('PLUGIN_URL: ' + PLUGIN_URL)	# plugin://plugin.video.ardundzdf/
	PLog('HANDLE: %s' % HANDLE)
	
	PLog("fparams: " + unquote(fparams)[:200] + "..")
	if thumb == None:
		thumb = ''
		
	add_url = PLUGIN_URL+"?action="+action+"&dirID="+dirID+"&fanart="+fanart+"&thumb="+thumb+quote(fparams)
	PLog("addDir_url: " + unquote(add_url)[:200])		
	
	
	# -------------------------------								# Kontextmenüs
	if cmenu:														# default: True
		Plot = Plot.replace('\n', '||')								# || Code für LF (\n scheitert in router)
		# PLog('Plot: ' + Plot)
		fparams_folder=''; fparams_filter=''; fparams_delete=''; 
		fparams_change=''; fparams_record=''; fparams_recordLive='';
		fparams_setting_sofortstart=''; fparams_sorting=''; 
		fparams_do_folder=''; fparams_rename=''; 
		fparams_playlist_add=''; fparams_playlist_rm='';fparams_playlist_play=''
		fparams_strm=''; fparams_exist_inlib=''; fparams_EPG='';
		fparams_ShowSumm=""
		
		if EPG_ID:														# EPG für Sender zeigen
			EPG_ID = py2_encode(EPG_ID)
			fp = {'title': label, 'ID': EPG_ID, 'mode': 'context'}
			fparams_EPG = "&fparams={0}".format(fp)
			PLog("fparams_EPG: " + fparams_EPG[:80])
				
		if mediatype == "video":										# Inhaltstext für Video zeigen
			items = ["api.ardmediathek|ARD", "zdf-prod-futura|ZDF",		# unterstützte Sender
					"www.3sat.de|3sat"]
			org_id=""
			for item in items:
				org, org_id  = item.split("|")
				if org in fparams:
					break
			if org_id and EPG_ID == "":									# nicht bei Livestreams
				try:
					s = fparams.split("&fparams=")[1]
					json_string = s.replace("'", "\"")
					f = json.loads(json_string)
					path = f["path"]
					title = f["title"]
					path=py2_encode(path); title=py2_encode(title)		# PY2
				except Exception as exception:
					PLog("fparams_error: " +  str(exception))
					path=""
				
				if path:												# sinnlos ohne path
					fp = {'title': title, 'path': path, 'ID': org_id, 'mode': 'ShowSumm'}
					fparams_ShowSumm = "&fparams={0}".format(fp)
					PLog("fparams_ShowSumm: " + fparams_ShowSumm[:80])											

		if SETTINGS.getSetting('pref_exist_inlib') == 'true':			# Abgleich Medienbibliothek
			if mediatype == "video":
				fp = {'title': label}									# Videotitel							
				fparams_exist_inlib = "&fparams={0}".format(fp)
				PLog("fparams_existinlib: " + fparams_exist_inlib[:80])
				fparams_exist_inlib = quote_plus(fparams_exist_inlib)
				
		if SETTINGS.getSetting('pref_strm') == 'true':					# strm-Datei für Video erzeugen
			if mediatype == "video":
				fp = {'label': label, 'add_url': quote_plus(add_url)}	# extract -> strm-Modul							
				fparams_strm = "&fparams={0}".format(fp)
				PLog("fparams_strm: " + fparams_strm[:100])
				fparams_strm = quote_plus(fparams_strm)

		if SETTINGS.getSetting('pref_video_direct') == 'true':			# ständig: Umschalter Sofortstart 
			menu_entry = "Sofortstart AUS / Downl. EIN"
			msg1 = "Sofortstart ist AUS"
			msg2 = "Downloads sind EINgeschaltet"
			ID = 'pref_video_direct,false|pref_use_downloads,true'
		else:
			menu_entry = "Sofortstart EIN / Downl. AUS"
			msg1 = "Sofortstart ist EIN"
			msg2 = "Downloads sind AUSgeschaltet"
			ID = 'pref_video_direct,true|pref_use_downloads,false'
		icon = R(ICON_TOOLS) 
		fp = {'ID': ID, 'msg1': msg1,\
			'msg2': msg2, 'icon': quote_plus(icon), 'delay': '5000'} 
		fparams_setting_sofortstart = "&fparams={0}".format(fp)
		PLog("fparams_setting_sofortstart: " + fparams_setting_sofortstart[:100])
		fparams_setting_sofortstart = quote_plus(fparams_setting_sofortstart)

		#--------------
		
		if SETTINGS.getSetting('pref_sort_label') == 'true':	# ständig: Umschalter Sortierung 
			menu_entry_sort = u"Sortierung ermöglichen: AUS"
			msg1_sort = "Sortierung AUS"
			msg2_sort = "globale Sortierung ausgeschaltet"
			ID = 'pref_sort_label,false'
		else:
			menu_entry_sort = u"Sortierung ermöglichen: EIN"
			msg1_sort = "Sortierung EIN"
			msg2_sort = "globale Sortierung eingeschaltet"
			ID = 'pref_sort_label,true'
		icon = R(ICON_TOOLS) 
		fp = {'ID': ID, 'msg1': msg1_sort,\
			'msg2': msg2_sort, 'icon': quote_plus(icon), 'delay': '3000'} 
		fparams_sorting = "&fparams={0}".format(fp)
		PLog("fparams_sorting: " + fparams_sorting[:100])
		fparams_sorting = quote_plus(fparams_sorting)
						
		
		if merkname:												# Aufrufer ShowFavs (Settings: Ordner .. verwenden)
			if SETTINGS.getSetting('pref_watchlist') == 'true':		# Merkliste verwenden 
				label = merkname
				# Param name reicht für folder, filter, rename		
				fp = {'action': 'rename', 'name': quote_plus(label),'thumb': quote_plus(thumb),\
					'Plot': quote_plus(Plot),'url': quote_plus(add_url)}	
				fparams_rename = "&fparams={0}".format(fp)
				PLog("fparams_rename: " + fparams_rename[:100])
				fparams_rename = quote_plus(fparams_rename)			# Umbenennen				
																	# Ordner ändern / Filtern:
				fp = {'action': 'folder', 'name': quote_plus(label),'thumb': quote_plus(thumb),\
					'Plot': quote_plus(Plot),'url': quote_plus(add_url)}	
				fparams_folder = "&fparams={0}".format(fp)
				PLog("fparams_folder: " + fparams_folder[:100])
				fparams_folder = quote_plus(fparams_folder)			# Ordner-Zuordnung ändern
				
				fp = {'action': 'filter', 'name': quote_plus(label)} 
				fparams_filter = "&fparams={0}".format(fp)
				fparams_filter = quote_plus(fparams_filter)			# Filtern
 
				fp = {'action': 'filter_delete', 'name': quote_plus(label)} 
				fparams_delete = "&fparams={0}".format(fp)
				fparams_delete = quote_plus(fparams_delete) 		# Filter entfernen

				fp = {'action': 'filter_folder', 'name': quote_plus(label)} 
				fparams_do_folder = "&fparams={0}".format(fp)
				fparams_do_folder = quote_plus(fparams_do_folder)	# Merklisten-Ordner bearbeiten (add/remove)
				
		fp = {'action': 'state_change'} 							# Ausschluss-Filter EIN/AUS
		fparams_change = "&fparams={0}".format(fp)
		fparams_change = quote_plus(fparams_change)					# Filtern
			

		# Recording:
		# unterschiedl. Parameterquellen: EPG_ShowSingle, EPG_ShowAll - bei
		#	title + descr sind hier die Codier.-Behandl. zu wiederholen:
		if start_end:												# Unix-Time-Format od. "Recording.."
			PLog("start_end: " + start_end)
			f = unquote(fparams)									# Param. extrahieren 
			f = f.replace("': '", "':'")
			# PLog(f)		# Debug
			Sender = stringextract("Sender':'", "'", f) 			# Bsp. 'ARTE'
			url = stringextract("path':'", "'", f) 					# Stream-Url
			# title mit Markierung übernehmen
			title = stringextract("title':'", "'", f) 				# Bsp. 'Mi | 01:45 | Dick und nun?'
			title = py2_decode(title)
			title = repl_json_chars(title)
			PLog("title: " + title)
			descr = "%s\n\n%s" % (tagline, summary)
			descr = descr.replace('\n','||')
			descr = py2_decode(descr)
			descr = repl_json_chars(descr)
			
			if "Recording TV-Live" in start_end:					# K-Menü in EPG_ShowAll -> LiveRecord
				Sender = cleanmark(title)
				Sender = Sender.split("|")[0]						# "Sender | EPG"
				duration = SETTINGS.getSetting('pref_LiveRecord_duration')
				duration, laenge = duration.split('=')
				duration = duration.strip()
				if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':
					laenge = "wird manuell eingegeben"
				duration=py2_encode(duration); laenge=py2_encode(laenge);
				Sender=py2_encode(Sender); url=py2_encode(url);
				fp = {'url': quote_plus(url), 'title': quote_plus(Sender),\
					'duration': quote_plus(duration), 'laenge': quote_plus(laenge)} 
				fparams_recordLive = "&fparams={0}".format(fp)
				PLog("fparams_recordLive: " + fparams_recordLive[:100])
				fparams_recordLive = quote_plus(fparams_recordLive)			
			else:													# K-Menü in EPG_ShowSingle	
				title=py2_encode(title); descr=py2_encode(descr)
				fp = {'url': quote_plus(url), 'sender': quote_plus(Sender),\
					'title': quote_plus(title), 'descr': quote_plus(descr), 'start_end': start_end} 
				fparams_record = "&fparams={0}".format(fp)
				PLog("fparams_record: " + fparams_record[:100])
				fparams_record = quote_plus(fparams_record)	
									
		# für PLAYLIST direkte PlayVideo-Calls seit Umstellung auf HLS_List,MP4_List nicht
		#	mehr geeignet. Neu: Nutzung der Funktionen für HLS_List,MP4_List - s. playlist.py,
		#	add_url ersetzt frühere direkte Stream-Url
		if SETTINGS.getSetting('pref_playlist') == 'true':	# PLAYLIST gewählt?
			PLog("pref_playlist_true, mediatype: " + mediatype)
			if mediatype == 'video':	
				# Änderungen mit get_Source_Funcs_ID (strm) abgleichen:	
				Source_Funcs = [u"ARDStartSingle|ARDnew.py",		# Funktionen + ID's
								u"ZDF_getVideoSources|ardundzdf.py",
								u"ZDF_getApiStreams|ardundzdf.py",
								u"SingleBeitrag|3sat", 
								u'XLGetSourcesPlayer|TagesschauXL.py',
								u"dirID=SenderLiveResolution|ARD",
								u"arte.SingleVideo|arte"
								]
				do_playlist=False
				for item in Source_Funcs:
					dest_func, modul = item.split("|")
					#PLog("dest_func: " + dest_func)
					if dest_func in dirID:
						PLog("dest_func: " + dest_func)
						do_playlist = True
						break
				PLog("do_playlist: " + str(do_playlist))
				
				if do_playlist: 
					PLog("start_end: " + start_end)
					f = unquote(fparams)											# Param. extrahieren (s. PlayVideo)
					f = f.replace("': '", "':'")									# json-Blanks
					title = label
					Plot = Plot.replace('\n', '||')									# Plot hier : tagline+summary
					
					# Abfrage PLAYFILE) hier nicht mögl. (USERDATA fehlt in util)
					fp = {'action': 'playlist_play'} 								# action reicht
					fparams_playlist_play = "&fparams={0}".format(fp)
					fparams_playlist_play = quote_plus(fparams_playlist_play)		# Playlist direkt abspielen
							
					fp = {'action': 'playlist_rm', 'add_url': quote_plus(add_url)} 	# action + Url reichen
					fparams_playlist_rm = "&fparams={0}".format(fp)
					fparams_playlist_rm = quote_plus(fparams_playlist_rm) 			# Eintrag Playlist löschen
							
					# Verwendung fparams_playlist_add auch für Ziel	playlist_tools
					fp = {'action': 'playlist_add', 'title': quote_plus(title), 'add_url': quote_plus(add_url),\
						'thumb': quote_plus(thumb), 'Plot': quote_plus(Plot)} 
					fparams_playlist_add = "&fparams={0}".format(fp)
					fparams_playlist_add = quote_plus(fparams_playlist_add) 		# Eintrag Playlist hinzufügen
					
					fp = {'action': 'playlist_add', 'title': quote_plus(title), 'add_url': quote_plus(add_url),\
						'thumb': quote_plus(thumb), 'Plot': quote_plus(Plot)} 
					fparams_playlist_tools = "&fparams={0}".format(fp)
					fparams_playlist_tools = quote_plus(fparams_playlist_tools) 	# Playlist-Tools
			
		fp = {'action': 'add', 'name': quote_plus(label),'thumb': quote_plus(thumb),\
			'Plot': quote_plus(Plot),'url': quote_plus(add_url)}	
		fparams_add = "&fparams={0}".format(fp)
		PLog("fparams_add: " + fparams_add[:100])
		fparams_add = quote_plus(fparams_add)						# -> Watch_items

		fp = {'action': 'del', 'name': quote_plus(label)}			# name reicht für del
		fparams_del = "&fparams={0}".format(fp)
		PLog("fparams_del: " + fparams_del[:100])
		fparams_del = quote_plus(fparams_del)						# -> Watch_items
		
		# --------------------------------------------------------- Scipt-Defs:
		commands = []
		if SETTINGS.getSetting('pref_watchlist') == 'true':			# Merkliste verwenden 
			# Script: This behaviour will be removed - siehe https://forum.kodi.tv/showthread.php?tid=283014
			# kodi.wiki/view/List_of_built-in_functions: RunScript(script[,args]*) using sys.argv
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/resources/lib/merkliste.py' % (ADDON_ID))
			if ShowFavs =="":										# Hinzufügen nicht in Merkliste
				commands.append(('Zur Merkliste hinzufügen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
						% (MY_SCRIPT, HANDLE, fparams_add)))
			commands.append(('Aus Merkliste entfernen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_del)))
		
			if fparams_folder or fparams_rename:					# Aufrufer ShowFavs s.o.
				PLog('set_folder_context: ' + merkname)
				commands.append(('Merklisten-Eintrag umbenennen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_rename)))
				commands.append(('Merklisten-Eintrag zuordnen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_folder)))
				commands.append(('Merkliste filtern', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_filter)))
				commands.append(('Filter der  Merkliste entfernen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_delete)))
				commands.append(('Merklisten-Ordner bearbeiten', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MY_SCRIPT, HANDLE, fparams_do_folder)))
				
		if fparams_change or fparams_record or fparams_recordLive:	# Ausschluss-Filter EIN/AUS, ProgramRecord
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
			if fparams_change:										# Aufrufer home s.o. -> FilterToolsWork
				commands.append(('Ausschluss-Filter EIN/AUS', 'RunScript(%s, %s, ?action=dirList&dirID=resources.lib.tools.FilterToolsWork%s)' \
					% (MY_SCRIPT, HANDLE, fparams_change)))
			if fparams_record:										# Aufrufer EPG_ShowSingle -> ProgramRecord
				commands.append(('diese Sendung aufnehmen', 'RunScript(%s, %s, ?action=dirList&dirID=ProgramRecord%s)' \
					% (MY_SCRIPT, HANDLE, fparams_record)))
			if fparams_recordLive:									# Aufrufer EPG_ShowAll -> LiveRecord
				commands.append(('Recording TV-Live', 'RunScript(%s, %s, ?action=dirList&dirID=LiveRecord%s)' \
					% (MY_SCRIPT, HANDLE, fparams_recordLive)))
		
		if fparams_setting_sofortstart:
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
			commands.append((menu_entry, 'RunScript(%s, %s, ?action=dirList&dirID=switch_Setting%s)' \
				% (MY_SCRIPT, HANDLE, fparams_setting_sofortstart)))
				
		if fparams_sorting:
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
			commands.append((menu_entry_sort, 'RunScript(%s, %s, ?action=dirList&dirID=switch_Setting%s)' \
				% (MY_SCRIPT, HANDLE, fparams_sorting)))
			
		# Playlist	
		if fparams_playlist_play or fparams_playlist_rm or fparams_playlist_add:	
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
			dirID = "resources.lib.playlist.items_add_rm"
			commands.append(('PLAYLIST direkt starten', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_playlist_play)))
			commands.append(('Zur PLAYLIST hinzufügen', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_playlist_add)))
			commands.append(('Aus PLAYLIST entfernen', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_playlist_rm)))
			dirID = "resources.lib.playlist.playlist_tools"	# Parameter wie items_add_rm
			commands.append(('PLAYLIST-Tools', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_playlist_add)))
		
		if fparams_strm:																# strm-Datei für Video erzeugen
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
			PLog("MY_SCRIPT_strm:" + MY_SCRIPT)		
			dirID = "resources.lib.strm.do_create"
			commands.append(('STRM-Datei erzeugen', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_strm)))		
			
		if fparams_exist_inlib:															# Abgleich mit Medienbibliothek
				MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % (ADDON_ID))
				PLog("MY_SCRIPT_inlib:" + MY_SCRIPT)		
				dirID = "resources.lib.strm.exist_in_library"
				commands.append(('Abgleich mit Medienbibliothek', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
						% (MY_SCRIPT, HANDLE, dirID, fparams_exist_inlib)))		

		if fparams_EPG:																	# EPG für Sender anzeigen
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/resources/lib/EPG.py' % (ADDON_ID))
			PLog("MY_SCRIPT_EPG:" + MY_SCRIPT)		
			dirID = "resources.lib.EPG.EPG"
			commands.append(('EPG zeigen', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_EPG)))

		if fparams_ShowSumm:															# Inhaltstext für Video zeigen
			MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/resources/lib/EPG.py' % (ADDON_ID))
			PLog("MY_SCRIPT_ShowSumm:" + MY_SCRIPT)		
			dirID = "resources.lib.EPG.EPG"
			commands.append((u'Inhaltstext für Video zeigen', 'RunScript(%s, %s, ?action=dirList&dirID=%s%s)' \
					% (MY_SCRIPT, HANDLE, dirID, fparams_ShowSumm)))
		
		li.addContextMenuItems(commands)				
	
	xbmcplugin.addDirectoryItem(handle=HANDLE,url=add_url,listitem=li,isFolder=isFolder)
	PLog('addDir_End')		
	return	

#---------------------------------------------------------------- 
# 01.08.2024 Kopfdoku seit 2018 entfernt - siehe Archiv
# 05.08.2024 Auswertung PDF-Format entfernt - nicht mehr gesehen	
# 
def get_page(path, header='', cTimeout=None, JsonPage=False, GetOnlyRedirect=False, do_safe=True, decode=True):
	PLog('get_page:'); PLog("path: " + path); PLog("do_safe: " + str(do_safe)); 

	if header:									# dict auspacken
		header = unquote(header);  
		header = header.replace("'", "\"")		# json.loads-kompatible string-Rahmen
		header = json.loads(header)
		PLog("header: " + str(header)[:100]);
		
	path_org=path
	# path = transl_umlaute(path)				# Umlaute z.B. in Podcast "Bäckerei Fleischmann"
	# path = unquote(path)						# scheitert bei quotierten Umlauten, Ersatz replace				
	path = path.replace('https%3A//','https://')# z.B. https%3A//classic.ardmediathek.de
	path = path.replace('zdf-cdn.live.cellular.de','zdf-prod-futura.zdf.de')	# neue api-Adresse ZDF
	
	
	path = py2_encode(path)
	if do_safe:									# never quoted: Letters, digits, and the characters '_.-' 
		path = quote(path, safe="#@:?,&=/")	# s.o.
	PLog("safe_path: " + path)

	msg=''; page=''; compressed=''	
	new_url=path													# dummy
	UrlopenTimeout = 10


	try:															# 1. Versuch ohne SSLContext 
		PLog("get_page1:")
		if GetOnlyRedirect:											# nur Redirect anfordern - hier nur dummy
			PLog('GetOnlyRedirect: ' + str(GetOnlyRedirect))
			page, msg = getRedirect(path, header)
			return page, msg

		if header:
			req = Request(path, headers=header)	
		else:
			req = Request(path)
		
		r = urlopen(req, timeout=UrlopenTimeout)					# float-Werte möglich
		new_url = r.geturl()										# follow redirects
		PLog("new_url: " + new_url)									# -> msg s.u.
		# PLog("headers: " + str(r.headers))
		
		compressed = r.info().get('Content-Encoding') == 'gzip'
		PLog("compressed: " + str(compressed))
		page = r.read()
		r.close()			
		PLog(len(page))
		msg = new_url		
	except Exception as exception:									# s.o.
		msg = str(exception)
		PLog("page1_error: " + msg)
		if msg.find("HTTP Error") >= 0:								# ab 26.06.2023
			PLog("return_HTTP Error: " + msg)
			page=""
			#return page, msg


	if page == '':
		# wie url_check (o. header ssl-Error bei Windows10 möglich)
		header={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
			'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}
		import ssl
		try:
			PLog("get_page2:")											# 2. Versuch mit SSLContext
			if header:
				req = Request(path, headers=header)	
			else:
				req = Request(path)	
			gcontext = ssl.create_default_context()
			gcontext.check_hostname = False
			r = urlopen(req, context=gcontext, timeout=UrlopenTimeout)
			
			compressed = r.info().get('Content-Encoding') == 'gzip'
			PLog("compressed: " + str(compressed))
			page = r.read()
			r.close()
			PLog(len(page))
		except Exception as exception:									# s.o.
			msg = str(exception)
			PLog("page2_error: " + msg)
			PLog(msg)						


	if page == '':
		try:
			PLog("get_page3:")											# 3. Versuch mit requests
			import requests												# kann fehlen 
			if header:
				r = requests.get(path, headers=header, timeout=UrlopenTimeout)	
			else:
				r = requests.get(path, timeout=UrlopenTimeout)
			PLog(r.status_code)
			page = r.content
			PLog(len(page))
			compressed=False
		except Exception as exception:
			PLog(str(exception))
			msg = str(exception)
			PLog("page3_error: " + msg)
			page=""	

	# PLog(page[:100]) - 06.08.2024 Ausgabe kann hier in Leia an "string with null bytes" 
	#	scheitern, falls get_page2 durchlaufen wird.
	if page:															
		PLog(type(page))
		if decode:														# Decodierung - Default
			PLog("decode_page: %s" % str(type(page)))
			try:
				if compressed:
					buf = BytesIO(page)
					f = gzip.GzipFile(fileobj=buf)
					page = f.read()
					PLog(len(page))
				if PYTHON2:			
					page = py2_decode(page)								# erzeugt bei PY3 Bytestrings (ARD)
				else:
					page = page.decode('utf-8')
			except Exception as exception:
				msg = str(exception)
				PLog("decode_error: " + msg)

	PLog(page[:100])
	PLog("get_page_exit")
	return page, msg
# ----------------------------------------------------------------------
def getHeaders(response):						# z.Z.  nicht genutzt
	PLog('getHeaders:')
	item_headers = ''
	
	if PYTHON2:						# PYTHON2
		dict_headers = response.headers.dict
		if 'item' in dict_headers:
			item_headers = dict_headers['item']
	else:  							# PYTHON3
		dict_headers = dict(response.info())
		if 'item' in dict_headers:
			item_headers = dict_headers['item']
		
	txt_headers = response.info()
	PLog(dict_headers)
	PLog(item_headers)

	headers=''
	if is_empty(dict_headers) is False:
		headers = dict_headers
	elif item_headers and is_empty(item_headers) is False:
		headers = item_headers
	else:
		if headers:
			headers = parse_headers(str(response.info()))
		
	return headers
# ----------------------------------------------------------------------
# 02.11.2024 für PYTHON2 bei Redirect-Errors unveränderte Rückgabe (neuer
#	Versuch in get_page (get_page3) mit requests (falls vorh.)
#   Für PYTHON3 bei Redirect-Errors Umstellung auf httplib2.
#	Debug 308_Error: www.ardaudiothek.de/rubrik/42914694 (ohne /-Ende)
#	
def getRedirect(path, header=""):		
	PLog('getRedirect: '+ path)
	page=""; msg=""
	parsed = urlparse(path)

	try:
		if header:
			req = Request(path, headers=header)	
		else:
			req = Request(path)
		r = urlopen(req)
		new_url = r.geturl()
		if new_url.startswith("http") == False:						# z.B. /rubrik/sportschau/..
			new_url = 'https://%s%s' % (parsed.netloc, new_url) 	# Serveradr. ergänzen
		PLog("new_url: " + new_url)
		return new_url, msg
	except Exception as e:
		PLog("redirect_error: "  + str(e))
		try:
			if "308:" in str(e) or "307:" in str(e) or "301:" in str(e):	# Permanent-Redirect-Url
				if PYTHON2:											# -> get_page (s.o.)
					return path, msg
				else:
					# https://httplib2.readthedocs.io/en/latest/libhttplib2.html
					import httplib2
					h = httplib2.Http()								# class httplib2.Http, Cache nicht erford.
					h.follow_all_redirects = True
					r = h.request(path, "GET")[0]
					new_url = r['content-location']
					PLog("httplib2_url: " + new_url)
					parsed = urlparse(path)
					if new_url.startswith("http") == False:			# s.o.
						new_url = 'https://%s%s' % (parsed.netloc, new_url)
						PLog("HTTP308_301_new_url: " + new_url)
					if path.find(new_url) == 0:		# Debug
						PLog("same_new_url_path: " + new_url) 
					return new_url, msg

		except Exception as e:
			PLog("r_error: "  + str(e))
			PLog(str(e))
			page=path, msg=str(e)									# Fallback

	return page, msg	
	
# ----------------------------------------------------------------------
# iteriert durch das Objekt	und liefert Restobjekt ab path
# bei leerem Pfad wird jsonObject unverändert zurückgegeben
# index error möglich bei veralteten Indices z.B. aus
#	Merkliste (Startpage wird aus Cache geladen).
# 23.04.2023 Rückgabe mit error-Text
def GetJsonByPath(path, jsonObject):		
	PLog('GetJsonByPath: '+ path)
	PLog(type(jsonObject))
	if not path or not jsonObject:
		msg = "GetJsonByPath: param_error"
		return "", msg
		
	path = path.split('|')
	i = 0; msg=""
	
	try:									# index error möglich
		index=0
		while(i < len(path)):
			if(isinstance(jsonObject,list)):
				index = int(path.pop(0))
			else:
				index = path.pop(0)
			PLog('i=%s, index=%s' % (i,index))
			jsonObject = jsonObject[index]
	except Exception as exception:
		msg = "json_error: " + str(exception)
		jsonObject=""
		PLog(msg)
		
	# PLog(jsonObject)
	return jsonObject, msg

#---------------------------------------------------------------- 
# img_urlScheme: img-Url ermitteln für get_sendungen, ARDRubriken. text = string, dim = Dimension
def img_urlScheme(text, dim, ID=''):
	PLog('img_urlScheme: ' + text[0:60])
	PLog(dim)
	
	pos = 	text.find('class="mediaCon">')			# img erst danach
	if pos >= 0:
		text = text[pos:]
	img_src = stringextract('img.ardmediathek.de', '##width', text)
		
	img_alt = stringextract('title="', '"', text)
	if img_alt == '':
		img_alt = stringextract('alt="', '"', text)
	img_alt = img_alt.replace('- Standbild', '')
	img_alt = 'Bild: ' + img_alt
	
		
	if img_src and img_alt:
		if img_src.startswith('http') == False:			#
			img_src = 'https://img.ardmediathek.de' + img_src 
		img_src = img_src + str(dim)					# dim getestet: 160,265,320,640
		if ID == 'PODCAST':								# Format Quadrat klappt nur bei PODCAST,
			img_src = img_src.replace('16x9', '16x16')	# Sender liefert Ersatz, falls n.v.
		if '?mandant=ard' in text:						# Anhang bei manchen Bildern
			img_src =img_src + '?mandant=ard' 
		PLog('img_urlScheme: ' + img_src)
		img_alt = py2_encode(img_alt)
		PLog('img_urlScheme: ' + img_alt[0:40])
		return img_src, img_alt
	else:
		PLog('img_urlScheme: leer')
		return '', ''		
	
#---------------------------------------------------------------- 
# ermittelt sqlite-DB passend zur Kodi Version + stellt Verbindung her
# Rückgabe cur
# Aufrufer: show_strm_element (strm-Modul)
# db=DB-Name ohne Nr, Bsp.: MyVideos (bei Bedarf erweitern: 
#	Addons*, MyMusic*)
# MyVideos-Felder s. kodi.wiki/view/Databases/MyVideos, Achtung: 
#	abweichende Feldnamen möglich, Kontrolle SQLiteStudio
def get_sqlite_Cursor(kodi_db):
	PLog('get_sqlite_Cursor: %s' % kodi_db)

	import sqlite3
	# DB-Version wählen, Format "Kodi_Version|MyVideos_Nr"
	if kodi_db == "MyVideos":
		db_list = ["17|107", "18|116", "19|119", "20|121", "21|121"]
		my_db = "MyVideos119.db" 					# Default Matrix
	for line in db_list:
		km, nr = line.split("|")
		if km == str(KODI_MAJOR):
			my_db = "%s%s" % (kodi_db, nr)
	PLog("my_db: " + my_db)
			
	db_path =  xbmc.translatePath('special://database/%s.db' % my_db)
	PLog("db_path: " + db_path)
	conn = sqlite3.connect(db_path)					# ohne error
	cur = conn.cursor()
	PLog(cur)
	return cur

#---------------------------------------------------------------- 
# Ersetzt R-Funktion von Plex (Pfad zum Verz. Resources, hier zusätzl. Unterordner möglich) 
# Falls abs_path nicht gesetzt, wird der Pluginpfad zurückgegeben, sonst der absolute Pfad
# für lokale Icons üblicherweise PluginAbsPath.
def R(fname, abs_path=False):	
	PLog('R(fname): %s' % fname); # PLog(abs_path)
	# PLog("ADDON_PATH: " + ADDON_PATH)
	if abs_path:
		try:
			# fname = '%s/resources/%s' % (PluginAbsPath, fname)
			path = os.path.join(ADDON_PATH,fname)
			return path
		except Exception as exception:
			PLog(str(exception))
	else:
		if fname.endswith('png'):	# Icons im Unterordner images
			fname = '%s/resources/images/%s' % (ADDON_PATH, fname)
			fname = os.path.abspath(fname)
			# PLog("fname: " + fname)
			return os.path.join(fname)
		else:
			fname = "%s/resources/%s" % (ADDON_PATH, fname)
			fname = os.path.abspath(fname)
			return fname 
#----------------------------------------------------------------  
# ersetzt Resource.Load von Plex 
# abs_path s.o.	R()	
def RLoad(fname, abs_path=False): # ersetzt Resource.Load von Plex 
	if abs_path == False:
		fname = '%s/resources/%s' % (ADDON_PATH, fname)
	path = os.path.join(fname) # abs. Pfad
	PLog('RLoad: %s' % str(fname))
	try:
		if PYTHON2:
			with open(path,'r') as f:
				page = f.read()		
		else:
			with open(path,'r', encoding="utf-8") as f:
				page = f.read()		
	except Exception as exception:
		PLog(str(exception))
		page = ''
	return page
#----------------------------------------------------------------
# Gegenstück zu RLoad - speichert Inhalt page in Datei fname im  
#	Dateisystem. PluginAbsPath muss in fname enthalten sein,
#	falls im Pluginverz. gespeichert werden soll 
#  Migration Python3: immer utf-8 - Alt.: xbmcvfs.File mit
#		Bytearray (s. merkliste.py)
#  05.07.2020 erweitert für Lock-Nutzung (für Monitor in epgRecord).
#
def RSave(fname, page, withcodec=False): 
	PLog('RSave: %s' % str(fname))
	PLog(withcodec)
	path = os.path.join(fname) # abs. Pfad
	msg = ''					# Rückgabe leer falls OK
	maxLockloops	= 10		# 1 sec bei 10 x xbmc.sleep(100)
	max_length=255				# Länge Filename 
	
	LOCK = fname[:max_length-4] + ".lck"
	i=0
	while os.path.exists(LOCK):	
		i=i+1
		if i >= maxLockloops:		# Lock brechen, vermutl. Ruine
			os.remove(LOCK)
			PLog("break " + LOCK)
			break
		xbmc.sleep(100)		
	
	try:
		if PYTHON2:
			if withcodec:		# 14.11.0219 Kompat.-Maßnahme
				import codecs	#	für DownloadExtern
				with codecs.open(path,'w', encoding='utf-8') as f:
					f.write(page)	
			else:
				with open(path,'w') as f:
					f.write(page)		
		else:
			with open(path,'w', encoding="utf-8") as f:
				f.write(page)
		
	except Exception as exception:
		msg = str(exception)
		PLog('RSave_Exception: ' + msg)
	return msg
#----------------------------------------------------------------  
# Holt Bandwith, Codecs + Resolution aus m3u8-Datei
# Bsp.: #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=61000,CODECS="mp4a.40.2"
def GetAttribute(text, attribute, delimiter1 = '=', delimiter2 = ','):
	PLog('GetAttribute:')
	if attribute == 'CODECS':	# Trenner = Komma, nur bei CODEC ist Inhalt 'umrahmt' 
		delimiter1 = '="'
		delimiter2 = '"'
	x = text.find(attribute)
	if x > -1:
		y = text.find(delimiter1, x + len(attribute)) + len(delimiter1)
		z = text.find(delimiter2, y)
		if z == -1:
			z = len(text)
		return text[y:z].strip()
	else:
		return ''
#----------------------------------------------------------------  
def repl_dop(liste):	# Doppler entfernen, im Python-Script OK, Problem in Plex - s. PageControl
	mylist=liste
	myset=set(mylist)
	mylist=list(myset)
	mylist.sort()
	return mylist
#----------------------------------------------------------------  
def repl_char(cut_char, line):	# problematische Zeichen in Text entfernen, wenn replace nicht funktioniert
	line_ret = line				# return line bei Fehlschlag
	pos = line_ret.find(cut_char)
	while pos >= 0:
		line_l = line_ret[0:pos]
		line_r = line_ret[pos+len(cut_char):]
		line_ret = line_l + line_r
		pos = line_ret.find(cut_char)
		#PLog(cut_char); PLog(pos); PLog(line_l); PLog(line_r); PLog(line_ret)	# bei Bedarf	
	return line_ret
#----------------------------------------------------------------
# für json.loads (z.B.. in router) json-Zeichen in line entfernen, insbesondere
#	Hochkommata (Problem bei Dictbildung)
#	doppelte utf-8-Enkodierung führt an manchen Stellen zu Sonderzeichen
#  	14.04.2019 entfernt: (':', ' ')
# 	07.11.2024 entfernt html-utf-8-Icons (Symbole Popcorn, TV usw)
def repl_json_chars(line):	
	line_ret = line
	#PLog(type(line_ret))
	for r in	((u'"', u''), (u'\\', u''), (u'\'', u''), (u'%5C', u'')
		, (u'&', u'und'), ('(u', u'<'), (u'(', u'<'),  (u')', u'>'), (u'∙', u'|')
		, (u'„', u'>'), (u'“', u'<'), (u'”', u'>'),(u'°', u' Grad'), (u'u00b0', u' Grad')
		, (u'\r', u''), (u'#', u'*'), (u'u003e', u''), (u'❤', u'love'), (u'%C3%A9', u'é')		# u'u003e' 	-> u'®'
		, (u'uD83C', u''), (u'uDF7F', u''), (u'uD63D', u''), (u'uDF7A', u'')					# 🍿,  📺
		):
		line_ret = line_ret.replace(*r)
	
	return line_ret
#----------------------------------------------------------------
# Verwendung bei übergroßen Mengen an Spezialzeichen in Titel + Info-Text
#	(Performance), um replace-Aufwand zu reduzieren - Bsp. funk (Hex-Colours 🤯, 
#	u.a. ✈, 😱, ..).
# valid_chars: Umlaute plus routerkompatible Zeichen, auch einige der in unescape
#	übersetzte Zeichen (hier ab &)
# S. docs.python.org/3/library/string.html
#
def valid_title_chars(line):
	#PLog("valid_title_chars:")

	printable = string.printable
	#  cut ab &: &\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c
	printable = printable.split('&')[0]
	valid_chars = u' üöäÜÖÄß%s&()*+,-.:<=>?_|~' % printable
	line_ret = ''.join(c for c in line if c in valid_chars)
	
	# Hochkommata, dto urlkodiert - nicht erfasst in valid_chars: 
	line_ret = (line_ret.replace(u'"', '').replace(u"'", '')\
	.replace(u"%27", '').replace(u"%22", '').replace(u"%5B", '')\
	 .replace(u"%5D", '').replace(u"&", '+'))

	return line_ret
#---------------------------------------------------------------- 
# statt json.dumps: 
# {'id': 'x', 'title': 'x'} -> {"id":"x", "title":"x"} ohne LF's,
# 	Hochkommata -> *, sächs. Genitiv 's -> Blank
# line=Dict
# 18.09.2024 replacing umgestellt auf json.dumps (utf-8-codiert für PY2)
def my_jsondump(line):
	PLog("my_jsondump:")
	try:
		if PYTHON2:					
			s=json.dumps(line, indent=None, separators=(",",":"), ensure_ascii=False).encode('utf-8')
		else:
			s=json.dumps(line, indent=None, separators=(",",":"), ensure_ascii=False)
	except Exception as exception:
		s=""
		PLog("my_jsondump_error: " + str(exception))

	return s		
#---------------------------------------------------------------- 
# strip-Funktion, die auch Zeilenumbrüche innerhalb des Strings entfernt
#	\s [ \t\n\r\f\v - s. https://docs.python.org/3/library/re.html
def mystrip(line):	
	line_ret = line	
	line_ret = re.sub(r"\s+", " ", line)	# Alternative für strip + replace
	# PLog(line_ret)		# bei Bedarf
	return line_ret
#----------------------------------------------------------------  	
# DirectoryNavigator - Nutzung des Kodi-builtin, der Code der PMS-Version kann entfallen
# S. http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmcgui.html
# settingKey: z.B. "pref_download_path"
# mytype: 	0 : ShowAndGetDirectory, 1 : ShowAndGetFile, 2
# mask: 	nicht brauchbar bei endungslosen Dateien, Bsp. curl
def DirectoryNavigator(settingKey, mytype, heading, shares='files', useThumbs=False, \
	treatAsFolder=False, path=''):
	PLog('DirectoryNavigator:')
	PLog(settingKey); PLog(mytype); PLog(heading); PLog(path);
	
	dialog = xbmcgui.Dialog()
	d_ret = dialog.browseSingle(int(mytype), heading, shares, '', False, False, path)	
	PLog('d_ret: ' + str(d_ret))
	
	if settingKey:
		SETTINGS.setSetting(settingKey, d_ret)	
	return d_ret
	
#----------------------------------------------------------------  
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	#pos2 = mString.find(mSecondChar, pos1 + ind+1)		
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
		
	#PLog(mString); PLog(mFirstChar); PLog(mSecondChar); 	# bei Bedarf
	#PLog(pos1); PLog(ind); PLog(pos2);  PLog(rString); 
	return rString
#---------------------------------------------------------------- 
# extrahiert Blöcke aus mString: Startmarke=blockmark, Endmarke=blockendmark 
def blockextract(blockmark, mString, blockendmark=''):  	
	#	blockmark bleibt Bestandteil der Rückgabe - im Unterschied zu split()
	#	Block wird durch blockendmark begrenzt, falls belegt, sonst reicht 
	#		 letzter Block bis Ende mString (undefinierte Länge). 
	#	Rückgabe in Liste.
	#	Verwendung, wenn xpath nicht funktioniert 
	rlist = []				
	if 	blockmark == '' or 	mString == '':
		PLog('blockextract: blockmark or mString leer')
		return rlist
	
	pos = mString.find(blockmark)
	if 	mString.find(blockmark) == -1:
		PLog('blockextract: blockmark <%s> nicht in mString enthalten' % blockmark)
		# PLog(pos); PLog(blockmark);PLog(len(mString));PLog(len(blockmark));
		return rlist
		
	pos2 = 1
	while pos2 > 0:
		pos1 = mString.find(blockmark)						
		ind = len(blockmark)
		pos2 = mString.find(blockmark, pos1 + ind)		
		
		if blockendmark:
			# PLog(blockendmark)
			pos3 = mString.find(blockendmark, pos1 + ind)
			# PLog("pos3: %d" % pos3)
			if pos3 > 0:
				ind_end = len(blockendmark)
				block = mString[pos1:pos3+ind_end]	# extrahieren einschl.  blockmark + blockendmark
			else:
				block = mString[pos1:]				# Block von blockmark bis Ende mString
			# PLog(block)			
		else:
			block = mString[pos1:pos2]			# extrahieren einschl.  blockmark
			# PLog(block)		
		mString = mString[pos2:]	# Rest von mString, Block entfernt
		rlist.append(block)
	return rlist  
#----------------------------------------------------------------  
def teilstring(zeile, startmarker, endmarker):  		
	# rfind: endmarker=letzte Fundstelle, return '' bei Fehlschlag
	# die übergebenen Marker bleiben Bestandteile der Rückgabe (werden nicht abgeschnitten)
	pos2 = zeile.find(endmarker, 0)
	pos1 = zeile.rfind(startmarker, 0, pos2)
	if pos1 & pos2:
		teils = zeile[pos1:pos2+len(endmarker)]	# 
	else:
		teils = ''
	#PLog(pos1) PLog(pos2) 
	return teils 
# ----------------------------------------------------------------------
def my_rfind(left_pattern, start_pattern, line):  # sucht ab start_pattern rückwärts + erweitert 
#	start_pattern nach links bis left_pattern.
#	Rückgabe: Position von left_pattern und String ab left_pattern bis einschl. start_pattern	
#	Mit Python's rfind-Funktion nicht möglich

	# PLog(left_pattern); PLog(start_pattern); 
	if left_pattern == '' or start_pattern == '' or line.find(start_pattern) == -1:
		return -1, ''
	startpos = line.find(start_pattern)
	# Log(startpos); Log(line[startpos-10:startpos+len(start_pattern)]); 
	i = 1; pos = startpos
	while pos >= 0:
		newline = line[pos-i:startpos+len(start_pattern)]	# newline um 1 Zeichen nach links erweitern
		# Log(newline)
		if newline.find(left_pattern) >= 0:
			leftpos = pos						# Position left_pattern in line
			leftstring = newline
			# Log(leftpos);Log(newline)
			return leftpos, leftstring
		i = i+1				
	return -1, ''								# Fehler, wenn Anfang line erreicht
#----------------------------------------------------------------
# prüft Vorkommen von String insert in Liste my_items
# Rückgabe False/True
#  	
def exist_in_list(insert, my_items):
	PLog("exist_in_list:")
	insert = py2_encode(insert);	
	try:
		for item in my_items:
			if insert in py2_encode(item):
				return True
	except Exception as exception:
		PLog(str(exception))
		
	return False		
#---------------------------------------------------------------- 
# Dialog mit FSK-Hinweis in page 	
def dialog_fsk(page):
	PLog('dialog_fsk:')
	fsk = stringextract('Einige Folgen sind FSK 16 und', ')</', page)
	if fsk:
		msg1 = "FSK-Hinweis:"
		msg2 = 'Einige Folgen sind FSK 16 und %s'	% (fsk)
		MyDialog(msg1, msg2, '')
	
	return
#----------------------------------------------------------------  	
# make_mark: farbige Markierung plus fett (optional	
# Groß-/Kleinschreibung egal
# bei Fehlschlag mString unverändert zurück
#
# title=' Aussteiger: *Identitäre* wollen Bürgerkrieg gegen'
def make_mark(mark, mString, color='red', bold=''):	
	PLog("make_mark:")	
	mark=py2_decode(mark); mString=py2_decode(mString)
	mS = up_low(mString); ma = up_low(mark)
	if ma in mS or mark == mString:
		pos1 = mS.find(ma)
		pos2 = pos1 + len(ma)		
		ms = mString[pos1:pos2]		# Mittelstück mark unverändert
		s1 = mString[:pos1]; s2 = mString[pos2:];
		if bold and color == '':
			rString= u"%s[B]%s[/B]%s" % (s1, ms, s2)
		elif color and bold:
			rString= u"%s[COLOR %s][B]%s[/B][/COLOR]%s"	% (s1, color, ms, s2)
		else:
			rString= u"%s[COLOR %s]%s[/COLOR]%s"	% (s1, color, ms, s2)
		return rString
	else:
		return mString		# Markierung fehlt, mString unverändert zurück
#----------------------------------------------------------------  
def cleanmark(line): # entfernt Farb-/Fett-Markierungen
	# PLog(type(line))
	cleantext = py2_decode(line)
	cleantext = re.sub(r"\[/?[BI]\]", '', cleantext, flags=re.I)
	cleantext = re.sub(r"\[/?COLOR.*?\]", '', cleantext, flags=re.I)
	return cleantext
#----------------------------------------------------------------  
# Migration PY2/PY3: py2_decode aus kodi-six
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	# PLog(type(line))
	cleantext = py2_decode(line)
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#---------------------------------------------------------------- 
# in URL kodierte Umlaute und & wandeln, Bsp. f%C3%BCr -> für, 	&amp; -> & 	
# Migration PY2/PY3: py2_decode aus kodi-six
# Einzelersetzung deutsche Umlaute unter python2
#	Bsp. python2:  unquote('%C3%BC') -> '\xc3\x9f' statt 'ü'
def decode_url(line):	
	line = py2_decode(line)
	unquote_plus(line)
	line = line.replace(u'&amp;', u'&')
	line = line.replace(u'&quot;', u'"')

	line = line.replace(u'%C3%BC', u'ü')
	line = line.replace(u'%C3%B6', u'ö')
	line = line.replace(u'%C3%A4', u'ä')
	line = line.replace(u'%C3%9F', u'ß')
	line = line.replace(u'%C3%9C', u'Ü')
	line = line.replace(u'%C3%96', u'Ö')
	line = line.replace(u'%C3%84', u'Ã')
	line = line.replace(u'%C4%87', u'Ä')
	
	line = line.replace(u'%20', u' ')
	line = line.replace(u'%22', u'"')
	line = line.replace(u'%2F', u'/')
	line = line.replace(u'%2C', u',')
	line = line.replace(u'%3A', u':')
	line = line.replace(u'%3F', u'?')
	
	line = line.replace(u'%28', u'(')		
	line = line.replace(u'%29', u')')	
	line = line.replace(u'%7C', u'|')
	
	line = line.replace(u'%E2%80%93', u'–')		# 27.07.2022
	
	
	return line
#----------------------------------------------------------------  	
# Migration PY2/PY3: py2_decode aus kodi-six
def unescape(line):
# HTML-Escapezeichen in Text entfernen, bei Bedarf erweitern. ARD auch &#039; statt richtig &#39;	
#					# s.a.  ../Framework/api/utilkit.py
#					# Ev. erforderliches Encoding vorher durchführen - Achtung in Kodis 
#					#	Python-Version v2.26.0 'ascii'-codec-Error bei mehrfachem decode
#
	# PLog(type(line))
	if line == None or line == '':
		return ''	
	line = py2_decode(line)
	for r in	((u"&amp;", u"&"), (u"&lt;", u"<"), (u"&gt;", u">")
		, (u"&#39;", u"'"), (u"&acute;", u"'"), (u"&#039;", u"'"), (u"&quot;", u'"'), (u"&#x27;", u"'")
		, (u"&ouml;", u"ö"), (u"&auml;", u"ä"), (u"&uuml;", u"ü"), (u"&szlig;", u"ß")
		, (u"&Ouml;", u"Ö"), (u"&Auml;", u"Ä"), (u"&Uuml;", u"Ü"), (u"&apos;", u"'")
		, (u"&nbsp;|&nbsp;", u""), (u"&nbsp;", u" "), (u"&bdquo;", u""), (u"&ldquo;", u""),
		# Spezialfälle:
		#	https://stackoverflow.com/questions/20329896/python-2-7-character-u2013
		#	"sächsischer Genetiv", Bsp. Scott's
		#	Carriage Return (Cr)
		(u"–", u"-"), (u"&#x27;", u"'"), (u"&#xD;", u""), (u"\xc2\xb7", u"-"),
		(u'undoacute;', u'o'), (u'&eacute;', u'e'), (u'&oacute;', u'o'), (u'&egrave;', u'e'),
		(u'&atilde;', u'a'), (u'quot;', u' '), (u'&#10;', u'\n'),
		(u'&#8222;', u' '), (u'&#8220;', u' '), (u'&#034;', u' '),
		(u'&copy;', u' | '), (u'&middot;', u'|'), (u'&ndash;', u'-'),
		(u'&deg;', u'°')):
		line = line.replace(*r)
	return line
#----------------------------------------------------------------  
# Migration PY2/PY3: py2_decode aus kodi-six
def transl_doubleUTF8(line):	# rückgängig: doppelt kodiertes UTF-8 
	# Vorkommen: Merkliste (Plot)
	# bisher nicht benötigt: ('Ã<U+009F>', 'ß'), ('ÃŸ', 'ß')

	line = py2_decode(line)
	for r in ((u'Ã¤', u"ä"), (u'Ã„', u"Ä"), (u'Ã¶', u"ö")		# Umlaute + ß
		, (u'Ã–', u"Ö"), (u'Ã¼', u"ü"), (u'Ãœ', u'Ü')
		, (u'Ã', u'ß')
		, (u'\xc3\xa2', u'*')):	# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2

		line = line.replace(*r)
	return line	
#---------------------------------------------------------------- 
# Dateinamen für Downloads + Bilderserien 
# erzeugt - hoffentlich - sichere Dateinamen (ohne Extension)
# zugeschnitten auf Titelerzeugung in meinen Plugins 
# Migration PY2/PY3: py2_decode aus kodi-six
# 24.04.2020 Entf. von Farb- und Fettmarkierungen (z.B. 
#	Downloads aus Suchbeiträgen) - ähnlich clean_Plot (merkliste)
# 
def make_filenames(title, max_length=255):
	PLog('make_filenames:')
	
	title = py2_decode(title)
	title = cleanmark(title)

	title = title.replace(u'|', ' ') 
	title = title.replace(u':', ' ')
	title = title.replace(u'/', ' ')					# mögl. Serienkennung 1/8, 2/8, ..
	
	fname = transl_umlaute(title)						# Umlaute
	
	valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
	fname = ''.join(c for c in fname if c in valid_chars)
	fname = fname.replace(u' ', u'_')
	fname = fname.replace(u'___', u'_')
	return fname[:max_length]
#---------------------------------------------------------------- 
def valid_string(s):
	
	valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
	ret = ''.join(c for c in s if c in valid_chars)
	return ret
	 
#----------------------------------------------------------------  
# Umlaute übersetzen, wenn decode nicht funktioniert
# Migration PY2/PY3: py2_decode aus kodi-six
def transl_umlaute(line):	
	line= py2_decode(line)	
	line_ret = line
	line_ret = line_ret.replace(u"Ä", u"Ae", len(line_ret))
	line_ret = line_ret.replace(u"ä", u"ae", len(line_ret))
	line_ret = line_ret.replace(u"Ü", u"Ue", len(line_ret))
	line_ret = line_ret.replace(u'ü', u'ue', len(line_ret))
	line_ret = line_ret.replace(u"Ö", u"Oe", len(line_ret))
	line_ret = line_ret.replace(u"ö", u"oe", len(line_ret))
	line_ret = line_ret.replace(u"ß", u"ss", len(line_ret))	
	return line_ret
#---------------------------------------------------------------- 
# Zeilenumbrüche bei Erhalt von Newlines
# Pythons textwrap kümmert sich nicht um \n
# http://code.activestate.com/recipes/148061-one-liner-word-wrap-function/
# reduce wurde in python3 nach functools verlagert
def wrap_old(text, width):		# 15.02.2020 abgelöst durch wrap s.u.
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )
#  wrap-Funktion ohne reduce:                
def wrap(text, width):
	text = text.strip()
	lines = text.splitlines()
	newtxt = []
	for line in lines:
		newline = textwrap.fill(line, width)
		newline = newline.strip()
		newtxt.append(newline)
		
	return "\n".join(newtxt)

#----------------------------------------------------------------   
# Migration PY2/PY3: py2_decode aus kodi-six
def transl_json(line):	# json-Umlaute übersetzen
	# Vorkommen: Loader-Beiträge ZDF/3Sat (ausgewertet als Strings)
	# Recherche Bsp.: https://www.compart.com/de/unicode/U+00BA,
	# 	https://html.spec.whatwg.org/multipage/named-characters.html
	line=py2_decode(line)
	#PLog(line)
	for r in ((u'\\u00E4', u"ä"), (u'\\u00C4', u"Ä"), (u'\\u00F6', u"ö"), (u'u002F', u"/")		
		, (u'\\u00C6', u"Ö"), (u'\\u00D6', u"Ö"),(u'\\u00FC', u"ü"), (u'\\u00DC', u'Ü')
		, (u'\\u00e4', u"ä"), (u'\\u00c4', u"Ä"), (u'\\u00f6', u"ö"), (u'u002f', u"/")	
		, (u'\\u00c6', u"Ö"), (u'\\u00d6', u"Ö"),(u'\\u00fc', u"ü"), (u'\\u00dc', u'Ü')
		, (u'\\u00DF', u'ß'), (u'\\u00df', u'ß'), (u'\\u0026', u'&'), (u'\\u00AB', u'"')
		, (u'\\u00BB', u'"')
		, (u'\\u00b7', u'·')		# Trenner: "S01 F01 · 47 min · Serien"
		, (u'\xc3\xa2', u'*')		# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2
		, (u'u00B0', u' Grad')		# u00BA -> Grad (3Sat, 37 Grad)	
		, (u'u00EA', u'e')			# 3Sat: Fête 
		, (u'u00E9', u'e')			# 3Sat: Fabergé
		, (u'u00E6', u'ae')			# 3Sat: Kjaerstad
		, (u'\\u00e7', u'ç')		# Arte: ç c mit Cedille
		, (u'\\u00e9', u'e')		# Arte: Frédéric
		, (u'\\u00e0', u'a')		# Arte: agrave
		, (u'\\u200e', u'')			# Left-to-Right Mark 
		, (u'\\u201e', u'*')		# Arte: doublequote tief
		, (u'\\u201c', u'*')		# Arte: doublequote hoch
		, (u'\\u2013', u'-')		# Arte: -
		, (u'\\u2014', u'-')		# Arte: -
		, (u'\\u2019', u'*')		# Arte: '
		, (u'\\u2019', u'*')
		, (u'\\u00f8', u'ø')		# ø Kleinbuchstabe o mit Strich,
		, (u'\\u00e5', u'å')		# å Kleinbuchstabe a mit Ring,
		, (u'\\u00c5', u'Å')		# Å Groß A mit Ring
		, (u'\\u00ab', u'«')		# Anführungszeichen links «
		, (u'\\u0160', u'Š')		# AudioPodcastDe: Šuma Covjek
		, (u'\\u0161', u'š')		# AudioPodcastDe: Ringišpil
		, (u'\\u2026', u'...')		# ...
		, (u'\\u26bd', u'<Ball-emoji>')	# Ball-emoji
		, (u'\\ufe0f', u'')			#  Nonspacing Mark
		, (u'\\u00a0', u' ')):		# NO-BREAK SPACE

		line = line.replace(*r)
	#PLog(line)
	return line	
#----------------------------------------------------------------  
def humanbytes(B):
	'Return the given bytes as a human friendly KB, MB, GB, or TB string'
	# aus https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776

	if B < KB:
	  return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
	elif KB <= B < MB:
	  return '{0:.2f} KB'.format(B/KB)
	elif MB <= B < GB:
	  return '{0:.2f} MB'.format(B/MB)
	elif GB <= B < TB:
	  return '{0:.2f} GB'.format(B/GB)
	elif TB <= B:
	  return '{0:.2f} TB'.format(B/TB)
#---------------------------------------------------------------- 
# 3 verschiedene Formate (s.u.) - Rückgabe in milliseconds
#	  Eingaben aus xbmcgui.INPUT_TIME (Recording): Format '00:00:05'
def CalculateDuration(timecode):				
	PLog("CalculateDuration:")
	timecode = up_low(timecode)	# Min -> min
	milliseconds = 0
	hours        = 0
	minutes      = 0
	seconds      = 0

	if timecode.find('P0Y0M0D') >= 0:			# 1. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
		d = re.search('T([0-9]{1,2})H([0-9]{1,2})M([0-9]{1,2}).([0-9]{1,3})S', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
			seconds = int ( d.group(3) )
			milliseconds = int ( d.group(4) )
					
	if len(timecode) == 8:						# Eingaben xbmcgui.INPUT_TIME
		d = re.search('([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})', timecode)	# 2. Format: '00:00:05'	
		if(None != d):
			hours = int( d.group(1) )
			minutes = int( d.group(2) )
			seconds = int ( d.group(3) )
			PLog(seconds)
			
						
	if len(timecode) == 9:					
		d = re.search('([0-9]{1,2}):([0-9]{1,2}) MIN', timecode)	# 2. Format: '00:30 min' 	
		if(None != d):
			hours = int( d.group(1) )
			minutes = int( d.group(2) )
			PLog(minutes)
						
	if len(timecode) == 11:											# 3. Format: '1:50:30.000'
		d = re.search('([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).([0-9]{1,3})', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
			seconds = int ( d.group(3) )
			milliseconds = int ( d.group(4) )
	
	milliseconds += hours * 60 * 60 * 1000
	milliseconds += minutes * 60 * 1000
	milliseconds += seconds * 1000
	
	return milliseconds
#---------------------------------------------------------------- 
# Format seconds	86400	(String, Int, Float)
# Rückgabe:  		1d, 0h, 0m, 0s	(days=True)
#		oder:		0h:0d:0s			
def seconds_translate(seconds, days=False):
	#PLog('seconds_translate:')
	#PLog(seconds)
	seconds = str(seconds)
	
	if "." in str(seconds):					# Ausschluss Basis 1000
		seconds = seconds.split(".")[0] 
	if seconds == '' or seconds == 0  or seconds == 'null':
		return ''
	if int(seconds) < 60:
		return "%s sec" % seconds
	seconds = float(seconds)
	day = seconds / (24 * 3600)	
	time = seconds % (24 * 3600)
	hour = time / 3600
	time %= 3600
	minutes = time / 60
	time %= 60
	seconds = time
	if days:
		#PLog("%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds))
		return "%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds)
	else:
		#PLog("%d:%02d" % (hour, minutes))
		return  "%02d:%02d:%02d" % (hour, minutes, seconds)		
#----------------------------------------------------------------  	
# Formate timecode 	ISO8601 date y-m-dTh:m:sZ 
# Varianten:	ARDNew			2018-11-28T23:00:00Z
#  				Funk: 			2019-09-30T12:59:27.000+0000  mit sec/1000 	UTC-Delta 0
# 				ARDNew Live: 	2019-12-12T06:16:04.413Z					UTC-Delta 0
#				ZDF:			2021-03-03T17:20:00+01:00					UTC-Delta + 1 Std.
#				ZDF:			2020-06-15T22:51:28.328+02:00 mit sec/1000 	UTC-Delta + 2 Std.
#				Audiothek:		2020-11-08T11:04:14.000+0100  z.Z. nicht genutzt (Verpasst fehlt)
#					
# Rückgabe:		28.11.2018, 23:00 Uhr   (Sekunden entfallen)
#				bzw. timecode (unverändert) bei Fehlschlag
# funktioniert in Kodi nur 1 x nach Neustart - s. transl_pubDate
# 26.08.2019 OK mit Lösung von BJ1 aus
#		https://www.kodinerds.net/index.php/Thread/50284-Python-Problem-mit-strptime/?postID=284746#post284746
#
# stackoverflow.com/questions/214777/how-do-you-convert-yyyy-mm-ddthhmmss-000z-time-format-to-mm-dd-yyyy-time-format
# stackoverflow.com/questions/7999935/python-datetime-to-string-without-microsecond-component
# stackoverflow.com/questions/13685201/how-to-add-hours-to-current-time-in-python
# https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
# https://de.wikipedia.org/wiki/ISO_8601#Zeitzonen
#
# s.a. convHour (ARDnew) - Auswertung für html-Quelle mit PM/AM
# Max. Datumsbereich:  ZDF_VerpasstWoche bis einschl. 2016
#
# 22.06.2020 Anpassung an 29-stel. ZDF-Format
# 06.11.2020 Berücksichtigung Sommerzeit für Timecodes ohne UTC-Delta
# 10.11.2020 Anpassung Tab. summer_time an Hinweis schubeda (UTC: -1 für MEZ, -2 für MESZ):
#	https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?postID=613709#post613709
#	Korr.-Faktor hour_info entfällt. add_hour jetzt Flag für Abgleich mit Tab. summer_time (False
#	bei "Verfügbar bis..")
# 11.10.2023 Mitnutzung durch ShowSeekPos (add_hour_only=True)
#
def time_translate(timecode, add_hour=True, day_warn=False, add_hour_only=""):
	PLog("time_translate: " + timecode)
	
	# summer_time aus www.ptb.de, konvertiert zum date_format (s.u.):
	#	Aktualisierung jeweils 29.01.
	summer_time = [	
					"2022-03-27T01:00:00Z|2022-10-30T01:00:00Z",
					"2023-03-26T01:00:00Z|2023-10-29T01:00:00Z",
					"2024-03-31T01:00:00Z|2024-10-27T01:00:00Z",
					"2025-03-30T01:00:00Z|2025-10-26T01:00:00Z",
				]

	if timecode.strip() == '' or len(timecode) < 19 or timecode[10] != 'T':
		return ''
	timecode = py2_encode(timecode)
		
	# Zielformat 2018-11-28T23:00:00Z
	day, hour_info 	= timecode.split('T')			# Datum / Uhrzeit trennen
	hour	 		= hour_info[:8]
	
	timecode = "%sT%sZ" % (day, hour)	
	PLog(timecode); PLog(add_hour);
	if timecode[10] == 'T' and timecode[-1] == 'Z': # Format OK?
		date_format = "%Y-%m-%dT%H:%M:%SZ"
		if add_hour:								# Abgleich summer_time (nicht bei Verfügbar bis)
			start=''
			try:									
				for timerange in summer_time:
					if timecode[:4] == timerange[:4]:
						start,end = timerange.split('|')
						PLog("summer_time: %s | %s" % (start,end))
						break
				if start:
					start_ts = datetime.datetime.fromtimestamp(time.mktime(time.strptime(start, date_format)))	
					end_ts = datetime.datetime.fromtimestamp(time.mktime(time.strptime(end, date_format)))	
					ts = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timecode, date_format)))
					add_hour = 1					# Default
					#PLog("ts: %s, start_ts: %s , end_ts: %s" % (ts, start_ts, end_ts))
					if ts > start_ts and ts < end_ts:	# Timecode liegt in Sommerzeit
						add_hour = 2
					PLog("add_hour: %s" % add_hour)
			except Exception as exception:
				PLog(str(exception))
				return timecode

			if add_hour_only:								# -> ShowSeekPos
				PLog("add_hour_only: %d" % add_hour)
				return add_hour
		try:
			# ts = datetime.strptime(timecode, date_format)  # None beim 2. Durchlauf (s.o. 26.08.2019)      
			ts = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timecode, date_format)))
			new_ts = ts + datetime.timedelta(hours=add_hour) # add-Faktor addieren
			ret_ts = new_ts.strftime("%d.%m.%Y %H:%M")
			PLog(ret_ts)

			if day_warn:									# Info, Bsp.: NOCH 5 TAGE
				today = datetime.datetime.today() 
				sday = new_ts
				dif  = str(sday-today)						# 18 days, 15:33:08.596024
				PLog(new_ts); 
				PLog("sday-today: %s" % dif)
				if dif.startswith("-") == False:			# -1 day, 23:48:12.503288 (Startzeit überschritten)
					try:
						if "day" in dif:	
							day = re.search(r'(\d+) day', dif).group(1)
							PLog("day: %s" % str(day))
							if  int(day) <= 7:					# erst ab 1 Woche warnen
								ret_ts = "%s | NOCH %s TAG(E)!" % (ret_ts, day)
						else:									# nur noch Stunden: 16:32:05.225575
							std = dif.split(".")[0]				# cut .225575
							ret_ts = "%s | NOCH %s Stunden!" % (ret_ts, std)
							
					except Exception as exception:
						PLog("day_warn_error: " + str(exception))
						ret_ts=""
					
			return ret_ts
		except Exception as exception:
			PLog(str(exception))
			return timecode
	else:
		return timecode

#---------------------------------------------------------------- 
# wandelt time_str (Formate 1:45, 00:30) in Minuten
def time_to_minutes(time_str):
	PLog('time_to_minutes:')
	
	minutes=""
	if len(time_str) > 5:	# ab V 4.9.5 möglich: 01:26:40
		time_str = time_str[:5]
		
	if ":" in time_str:	
		h, m = time_str.split(':')
		minutes = int(h) * 3600 + int(m)
	PLog(minutes)
	return str(minutes)
#---------------------------------------------------------------- 
# Format timecode 	Fri, 06 Jul 2018 06:58:00 GMT (ARD Audiothek , xml-Ausgaben)
# Rückgabe:			06.07.2018, 06:58 Uhr   (Sekunden entfallen)
# funktioniert nicht in Kodi, auch nicht der Workaround in
#	https://forum.kodi.tv/showthread.php?tid=112916 bzw.
#	https://www.kodinerds.net/index.php/Thread/50284-Python-Problem-mit-strptime
def transl_pubDate(pubDate):
	PLog('transl_pubDate:')	
	pubDate_org = pubDate		
	if pubDate == '':
		return ''
		
	if ',' in pubDate:
		pubDate = pubDate.split(',')[1]		# W-Tag abschneiden
	pubDate = pubDate.replace('GMT', '')	# GMT entf.
	pubDate = pubDate.strip()
	PLog(pubDate)
	try:
		datetime_object = datetime.strptime(pubDate, '%d %b %Y %H:%M:%S')		
		PLog(datetime_object)
		new_date = datetime_object.strftime("%d.%m.%Y %H:%M")
		PLog(new_date)
	except Exception as exception:			# attribute of type 'NoneType' is not callable
		PLog(str(exception))
		new_date = pubDate_org				# unverändert zurück
	return new_date	
#---------------------------------------------------------------- 	
# Holt User-Eingabe für Suche ab
#	s.a. get_query (für Search , ZDF_Search)
def get_keyboard_input(line='', head=''):
	PLog("get_keyboard_input: " + line)
	if head == '':
		head = 'Bitte Suchwort(e) eingeben'
	kb = xbmc.Keyboard(line, head)
	kb.doModal() # Onscreen keyboard
	if kb.isConfirmed() == False:
		return ""
	inp = kb.getText() # User Eingabe
	return inp	
#----------------------------------------------------------------  
# getOnline: 1. Ausstrahlung
# Format datestamp: "2017-02-26 21:45:00", 2018-05-24T16:50:00 19-stel.
#	05.06.2020 hinzugefügt: 2018-05-24T16:50:00Z (Z wird hier entfernt)
#	beim Menü Sendungen auch  2018-01-20 00:30 16 stel.
# time_state checkt auf akt. Status, Zukunft und jetzt werden rot gekennzeichnet
def getOnline(datestamp, onlycheck=False):
	PLog("getOnline: " + datestamp)
	PLog(len(datestamp))
	if datestamp == '' or '/' in datestamp:
		return '' 

	if datestamp.endswith('Z'):							# s.o.
		datestamp = datestamp[:len(datestamp)-1]
	
		
	online=''; check_state=''
	if len(datestamp) == 19 or len(datestamp) == 16:
		senddate = datestamp[:10]
		year,month,day = senddate.split('-')
		sendtime = datestamp[11:]
		if len(sendtime) > 5:
			sendtime = sendtime[:5]
		
		checkstamp = "%s %s" % (senddate, sendtime)
		check_state= time_state(checkstamp)
		if check_state:									# Kennz. nur Zukunft und jetzt
			check_state = " (%s)" % check_state
		
		online = "Online%s: %s.%s.%s, %s Uhr"	% (check_state, day, month, year, sendtime)	
	
	if onlycheck == True:
		return check_state
	else:
		return online
	
# ----------------------------------------------------------------------
# Prüft datestamp auf Vergangenheit, Gegenwart, Zukunft
#	Format datestamp: "2020-01-26 11:15:00" 19 stel., in
#	getOnline auf 16 Stellen reduz. (o. Sek.)
def time_state(checkstamp):
	PLog("time_state: " + checkstamp)		
	date_format = "%Y-%m-%d %H:%M"

	start = datetime.datetime.fromtimestamp(time.mktime(time.strptime(checkstamp, date_format)))
	# PLog(start)
	now = datetime.datetime.now()
	# PLog(now)
	if start < now:
		check_state = '' 	# 'Vergangenheit'
	elif start > now:
		check_state = "[B][COLOR red]%s[/COLOR][/B]" % 'Zukunft'
	else:
		check_state = 'jetzt'
	
	return check_state
# ----------------------------------------------------------------------
# Wochentage engl./deutsch wg. Problemen mit locale-Setting 
#	für VerpasstWoche, EPG	
def transl_wtag(tag):	
	wt_engl = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	wt_deutsch = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
	
	wt_ret = tag
	for i in range (len(wt_engl)):
		el = wt_engl[i]
		if el == tag:
			wt_ret = wt_deutsch[i]
			break
	return wt_ret
# ----------------------------------------------------------------------
# simpler XML-SRT-Konverter für ARD-Untertitel
#	pathname = os.path.abspath. 
#	vorh. Datei wird überschrieben
# 	Rückgabe outfile bei Erfolg, '' bei Fehlschlag
# https://knowledge.kaltura.com/troubleshooting-srt-files
# Wegen des strptime-Problems unter Kodi verzichten wir auf
#	korrekte Zeitübersetzung und ersetzen lediglich
#		1. den Zeitoffset 10 durch 00
#		2. das Sekundenformat 02.000 durch 02,00 (Verzicht auf die letzte Stelle)
# Problem mit dt.datetime.strptime (Kodi: attribute of type 'NoneType' is not callable):
# 	https://forum.kodi.tv/showthread.php?tid=112916
# Migration Python3: s. from __future__ import print_function
# 16.05.2020 Anpassung an Python3, try-except-Block für Einlesen der UT-Datei
# 25.02.2021 wg. Pyton3-Problemen (byte/str-error) Verzicht auf xbmc-File und
#	open(outfile, 'w') - akt. Verwendung RLoad + RSave - s.a.
#	https://github.com/romanvm/kodi.six#known-issues
def xml2srt(infile):
	PLog("xml2srt: " + infile)
	outfile = '%s.srt' % infile
		
	try:
		page = RLoad(infile, abs_path=True)
		page = page.replace('-1:', '00:') 		# xml-Fehler
		# 10-Std.-Offset simpel beseitigen (2 Std. müssten reichen):
		page = (page.replace('"10:', '"00:').replace('"11:', '"01:').replace('"12:', '"02:'))
		ps = blockextract('<tt:p', page)					
	except Exception as exception:
		PLog(str(exception))
		return ''				
		
	try:
		out = []											# Ausgabeliste
		for i, p in enumerate(ps):
			begin 	= stringextract('begin="', '"', p)		# "10:00:07.400"
			end 	= stringextract('end="', '"', p)		# "10:00:10.920"			
			ptext	=  blockextract('tt:span style=', p)	# kann fehlen,z.B. in xml:id="sub0"
			
			begin	= begin[:8] + ',' + begin[9:11]			# ""10:00:07,40"			
			end		= end[:8] + ',' + end[9:11]				# "10:00:10,92"

			out.append(str(i))
			out.append('%s --> %s' % (begin, end))
			for textline in ptext:
				text = stringextract('>', '<', textline) 	# style="S3">Willkommen zum großen</tt:span>
				out.append(text)
			out.append("")
			
		page = "\n".join(out)
		RSave(outfile, page)	
		os.remove(infile)									# Quelldatei entfernen
	except Exception as exception:
		PLog(str(exception))
		outfile = ''
			
	return outfile

#----------------------------------------------------------------
#	Favs / Merkliste dieses Addons einlesen
#	01.04.2020 Erweiterung ext. Merkliste (Netzwerk-Share).
#	18.04.2020 Erweiterung Ordner
#
def ReadFavourites(mode):	
	PLog('ReadFavourites:')
	if mode == 'Favs':
		fname = xbmc.translatePath('special://profile/favourites.xml')
	else:	# 'Merk'
		fname = WATCHFILE
		if SETTINGS.getSetting('pref_merkextern') == 'true':	# externe Merkliste gewählt?
			fname = SETTINGS.getSetting('pref_MerkDest_path')
			if fname == '' or xbmcvfs.exists(fname) == False:
				msg1 = u"externe Merkliste ist eingeschaltet, aber Dateipfad fehlt oder"
				msg2 = "Datei nicht gefunden"
				MyDialog(msg1, msg2, '')
				return []
			
	try:
		if '//' not in fname:
			page = RLoad(fname,abs_path=True)
		else:
			PLog("xbmcvfs_fname: " + fname)
			f = xbmcvfs.File(fname)		# extern - Share		
			page = f.read(); f.close()
			PLog(len(page))				
			page = py2_encode(page)		# für externe Datei erf.
	except Exception as exception:
		PLog(str(exception))
		return []
				
	if mode == 'Favs':
		favs = re.findall("<favourite.*?</favourite>", page)
	else:
		favs = re.findall("<merk.*?</merk>", page)
	# PLog(favs)
	my_favs = []
	for fav in favs:
		if mode ==  'Favs':
			if ADDON_ID not in fav: 	# skip fremde Addons, ID's in merk's wegen 	
				continue				# 	Base64-Kodierung nicht lesbar
		my_favs.append(fav) 
		
	my_ordner = []						# Ordner einlesen
	items = stringextract('<ordnerliste>', '</ordnerliste>', page)
	items =  items.split()
	for item in items:
		my_ordner.append(item.strip())
			
	PLog(len(my_favs)); PLog(len(my_ordner)); 
	return my_favs, my_ordner

#----------------------------------------------------------------
# Liest Textdateien, filtert Kommentarzeilen aus, Rückgabe: Liste
# fname: kompl. Pfad zur Datei (Kodierung Unicode utf-8)
# Bsp.: full_shows_ARD, full_shows_ZDF
#
def ReadTextFile(fname):
	PLog('ReadTextFile:')
	PLog(fname)
	try:
		PLog("xbmcvfs_fname: " + fname)
		f = xbmcvfs.File(fname)		# extern - Share		
		page = f.read(); f.close()
		PLog(len(page))				
	except Exception as exception:
		PLog(str(exception))
		return []
		
	newlist = []						# Ordner einlesen
	mylist = page.splitlines()
	for item in mylist:
		item = item.strip()
		if item and item.startswith('#') == False:
			newlist.append(item)
	
	return newlist
#----------------------------------------------------------------
#	Jobliste für Modul epgRecord einlesen
#
def ReadJobs():	
	PLog('ReadJobs:')

	JOBFILE			= os.path.join(ADDON_DATA, "jobliste.xml") 
	JOBFILE_LOCK	= os.path.join(ADDON_DATA, "jobliste.lck")  		# Lockfile für Jobliste
	maxLockloops	= 10		# 1 sec bei 10 x xbmc.sleep(100)	
		
	i=0
	while os.path.exists(JOBFILE_LOCK):	
		i=i+1
		if i >= maxLockloops:		# Lock brechen, vermutl. Ruine
			os.remove(JOBFILE_LOCK)
			PLog("break " + JOBFILE_LOCK)
			break
		xbmc.sleep(100)		
			
	try:
		PLog("xbmcvfs_fname: " + JOBFILE)
		f = xbmcvfs.File(JOBFILE)				
		page = f.read(); f.close()
		PLog(len(page))				
		page = py2_encode(page)		# für externe Datei erf.
	except Exception as exception:
		PLog(str(exception))
		return []
				
	jobs = re.findall("<job>(.*?)</job>", page)
	PLog(len(jobs))		
	return jobs

#----------------------------------------------------------------
# holt summary (Inhaltstext) für eine Sendung, abhängig von SETTINGS('pref_load_summary')
#	- Inhaltstext zu Video im Voraus laden. 
#	SETTINGS durch Aufrufer geprüft
#	ID: ARD, ZDF 
# Es wird nur die Webseite ausgewertet, nicht die json-Inhalte der Ladekette.
# Cache: 
#		html-Seite wird in TEXTSTORE gespeichert, Dateiname aus path generiert.
#
# Aufrufer: ZDF: 	ZDF_get_content (für alle ZDF-Rubriken)
#			ARD: 	ARDStart	-> ARDStartRubrik 
#					SendungenAZ, ARDSearchnew, 	ARDStartRubrik,
#					ARDPagination -> get_page_content
#					ARDStartRubrik (Swiper) 
#					ARDVerpasstContent
#			
# Aufruf erfolgt, wenn für eine Sendung kein summary (teasertext, descr, ..) gefunden wird.
#
# Nicht benötigt in ARD-Suche (Search -> SinglePage -> get_sendungen): Ergebnisse 
#	enthalten einen 'teasertext' bzw. 'dachzeile'. Dto. Sendung Verpasst
# 
# Nicht benötigt in ZDF-Suche (ZDF_Search -> ZDF_get_content): Ergebnisse enthalten
#	einen verkürzten 'teaser-text'.
#
# 21.06.2020 zusätzl. Sendedatum pubDate
#	in TEXTSTORE gespeichert wird die ges. html-Seite (vorher nur Text summ)
# 14.06.2021 Sendedatum pubDate für ZDF Sport unterdrückt (oft falsch bei Livestreams)
# 26.08.2021 Erweiterung für einzelnes Auswertungsmerkmal (pattern) 
# 11.05.2023 postcontent (ZDF, 3sat) hinzugefügt
# 08.10.2024 Änderung Cache-Format - nur noch Inhalt summary (Start mit "V5.1.2_summ:"),
#	Param page entfernt (obsolet)
#
def get_summary_pre(path,ID='ZDF',skip_verf=False,skip_pubDate=False,pattern='',duration=''):	
	PLog('get_summary_pre: ' + ID); PLog(path)
	PLog(skip_verf); PLog(skip_pubDate); PLog(duration); 
	duration_org=duration
	
	fname = path.split('/')[-1]
	fname = fname.replace('.html', '')				# .html bei ZDF-Links entfernen
	fname = fname.replace('?devicetype=pc', '')		# ARD-api-Zusatz
	fname = fname.replace('&embedded=true', '')		# ARD-api-Zusatz	
		
	fpath = os.path.join(TEXTSTORE, fname)
	PLog('fpath: ' + fpath)
	
	page=""; summ=''; pubDate=''
	save_new = False
	if os.path.exists(fpath):		# Text lokal laden + zurückgeben
		page=''
		PLog('lade_aus_Cache:') 
		page =  RLoad(fpath, abs_path=True)
		if page.startswith("V5.1.2_summ:"):		# neues Cache-Format?
			page = page.replace("V5.1.2_summ:", "")
			PLog('ret_page: ' + page[:80])
			return page				# summary
		else:
			save_new = True

	if page == '':
		PLog('lade_extern:') 
		page, msg = get_page(path)	# extern laden, HTTP Error 404 möglich
		save_new = True
	if page == '':
		return ''					# ohne pubdate (Aufrufer: summ.replace) 				
			
	# Decodierung plus bei Classic u-Kennz. vor Umlaut-strings (s.u.)
	page = py2_decode(page)
	PLog(skip_verf);PLog(skip_pubDate);
	if "zdf.de/sport/" in path:												# ZDF Sport: pubDate unterdrücken -
		skip_pubDate=True													#	bei Livestreams oft falsch
	verf='';
	
	if pattern: 
		ID=''																# einzelnes Auswertungsmerkmal
		pat1, pat2 = pattern.split('|')
		summ = stringextract(pat1, pat2, page)
		summ = repl_json_chars(summ)
					
	#-----------------	
	
	if 	ID == 'ZDF':
		teaserinfo = stringextract('teaser-info">', '<', page)
		summ = stringextract('class="item-description" >', '</p>', page)
		summ = mystrip(summ)
		if teaserinfo:
			summ = "%s | %s" % (teaserinfo, summ)
		summ = unescape(summ)
																			# 11.05.2023 neu 
		postcontent = stringextract('b-post-content">', '"b-post-footer"', page)
		if postcontent:
			addpost=[]
			items = blockextract("<p>", postcontent, "</p>")
			for item in items:
				s = stringextract("<p>", "</p>", item)
				s=unescape(s); s=cleanhtml(s); s=transl_json(s)
				if s:
					addpost.append(s)
			if len(addpost) > 0:
				summ = summ + " | " + " | ".join(addpost)
				summ = mystrip(summ)
		summ  = valid_title_chars(summ)										# s. changelog V4.7.4

		if skip_verf == False:
			if u'erfügbar bis' in page:										# enth. Uhrzeit									
				verf = stringextract(u'erfügbar bis ', '<', page)			# Blank bis <
			if verf == '':
				verf = stringextract('plusbar-end-date="', '"', page)
				verf = time_translate(verf, add_hour=0)
			if verf:														# Verfügbar voranstellen
				summ = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s\n" % (verf, summ)
		
		if skip_pubDate == False:		
			pubDate = stringextract('publicationDate" content="', '"', page)# Bsp. 2020-06-15T22:51:28.328+02:00
			if pubDate == '':
				pubDate = stringextract('<time datetime="', '"', page)		# Alternative wie oben
			if pubDate:
				pubDate = time_translate(pubDate)
				pubDate = " | Sendedatum: [COLOR blue]%s Uhr[/COLOR]\n\n" % pubDate	
				if u'erfügbar bis' in summ:	
					summ = summ.replace('\n\n', pubDate)					# zwischen Verfügbar + summ  einsetzen
				else:
					summ = "%s%s" % (pubDate[3:], summ)
					
	#-----------------	
	
	if 	ID == '3sat':
		summ = stringextract('name="description" content="', '"', page)
		summ = mystrip(summ)
		teaserinfo=""
		if teaserinfo:
			summ = "%s | %s" % (teaserinfo, summ)
		summ = unescape(summ)
	
	#-----------------	
				
	if 	ID == 'ARDnew':
		page = page.replace('\\"', '*')							# Quotierung vor " entfernen, Bsp. \"query\"
		page = page.replace('\\r\\n\\r\\n', " | ")				# CR+LF doppelt
		pubServ = stringextract('"name":"', '"', page)			# publicationService (Sender)
		if "FSK:" not in duration_org:							# bereits in Param?
			maturitytRating = stringextract('maturityContentRating":"', '"', page) # "FSK16"
			maturitytRating = maturitytRating.replace('NONE', 'Ohne')
		else:
			maturitytRating=""
		if duration == '':										# schon übergeben?
			duration = stringextract('"duration":', ',', page)	# Sekunden
			if duration == '0':									# auch bei Einzelbeitrag möglich
				duration=''
			duration = seconds_translate(duration)
			if duration and pubServ:										
				duration = u'Dauer %s | [B]%s[/B]' % (duration, pubServ)
		if 	maturitytRating:
			if duration == '':
				duration = "Dauer unbekannt"
			duration = u"%s | FSK: %s\n" % (duration, maturitytRating)	
		
		summ = stringextract('synopsis":"', '","', page)	
		summ = summ.replace('\\n\\n', " | ")					# LF doppelt, CR+LF s.o.
		summ = summ.replace('\\n', ". ")						# LF einzeln
		summ = repl_json_chars(summ)
		summ  = valid_title_chars(summ)							# s. changelog V4.7.4
			
		if skip_verf == False:
				verf = stringextract('availableTo":"', '","', page)
				if verf:
					verf = time_translate(verf)
					summ = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s" % (verf, summ)
		if skip_pubDate == False:		
			pubDate = stringextract('"broadcastedOn":"', '"', page)
			if pubDate:
				pubDate = time_translate(pubDate)
				pubDate = u" | Sendedatum: [COLOR blue]%s Uhr[/COLOR]\n\n" % pubDate	
				if u'erfügbar bis' in summ:	
					summ = summ.replace('\n\n', pubDate)		# zwischen Verfügbar + summ  einsetzen
				else:
					summ = "%s%s" % (pubDate[3:], summ)
					
		if duration and summ:
			summ = "%s\n%s" % (duration, summ)
			
	#-----------------	
	summ = summ.replace(' |  | ', '')							# Korrek. Leer
	PLog('summ: ' + summ[:80]); PLog(save_new)
	if summ and save_new:
		cont = "V5.1.2_summ:" + summ							# Erkennungsmerkmal neues Cache-Format
		msg = RSave(fpath, cont)
	# PLog(msg)
	return summ
	
#-----------------------------------------------
# aktualisiert die TV-Livestream-Quellen unabhängig
#	vom Setting
# Aufruf: InfoAndFilter
def refresh_streamlinks():
	PLog('refresh_streamlinks:')
	get_ARDstreamlinks(skip_log=False, force=True)
	get_ZDFstreamlinks(skip_log=False, force=True)
	get_IPTVstreamlinks(skip_log=False, force=True)
	return
#-----------------------------------------------
# ARD-Links s. get_ARDstreamlinks
# Sender: ZDF, ZDFneo, 3sat, Phoenix, KiKA, ZDFinfo.
#
# Aufruf get_sort_playlist (<- EPG_Sender, EPG_ShowAll,
#	TVLiveRecordSender), SenderLiveListe, get_live_data (Arte),
#	Live (3sat), Kika_Live, get_playlist_img
#
# ermittelt master.m3u8 für die ZDF-Sender (Kennz. ZDFsource in
#	livesenderTV.xml). Rückgabe Liste (Zeile: Sender|Url) -
#	Reihenfolge wie Web (www.zdf.de/live-tv).
# Cache 24 Stunden, Datei: zdf_streamlinks im Dict-Ordner - nur
#	außerhalb der Cachezeit wird www.zdf.de/live-tv neu geladen.
#
# Beachte: Blank hinter title_sender zur Abgrenz. der ZDF-Sender.
#	Abgleich kompl. Titel nicht sicher (Bsp. 2 Blanks bei Arte)
# 26.06.2020 skip_log hinzugefügt (True in get_sort_playlist
#	loop, Ausgabe der Liste in  "Überregional")
# Mehrkanal-Streamlinks seit Aug. 2020 - die enth. Audiolinks in 
#	Kodi nicht getrennt verwertbar. 
# 29.10.2023 force=True: InfoAndFilter -> refresh_streamlinks
#
#-----------------------------------------------
def get_ZDFstreamlinks(skip_log=False, force=False):
	PLog('get_ZDFstreamlinks:')
	PLog("skip_log: " + str(skip_log)); PLog("force: " + str(force))
	days = int(SETTINGS.getSetting('pref_tv_store_days'))
	PLog("days: %d" % days)
	CacheTime = days*86400						# Default 1 Tag
	#days=0	# Debug

	if days and force == False:					# skip CacheTime=0
		page = Dict("load", 'zdf_streamlinks', CacheTime=CacheTime)
		if len(str(page)) > 100:					# bei Error nicht leer od. False von Dict
			if skip_log == False:
				PLog(page)							# für IPTV-Interessenten
			return page.splitlines()

	icon = R(ICON_TOOLS)
	xbmcgui.Dialog().notification("Cache ZDFlinks:","wird erneuert",icon,3000)

	page, msg = get_page(path='https://www.zdf.de/live-tv')			# Links neu holen
	if page == '':
		PLog('get_ZDFstreamlinks: leer')
		return []

	page = page.replace('content": "', '"content":"')
	page = page.replace('apiToken": "', '"apiToken":"')
	content = blockextract('js-livetv-scroller-cell', page)			# Playerdaten einschl. apiToken
	PLog("len_content: %d" % len(content))
	apiToken = stringextract('"apiToken":"', '"', page)				# für alle identisch
	PLog("apiToken: " + apiToken[:80] + "..")
	header = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken
	
	zdf_streamlinks=[]
	for rec in content:												# Schleife  Web-Sätze		
		player2_url=''; assetid=''; videodat_url=''; apiToken=''; href=''
		title = stringextract('visuallyhidden">', '<', rec)
		title = title.replace('im Livestream', ''); title = title.strip()	# phoenix
		title = title.replace('Livestream', ''); title = title.strip()		# restl. sender
		PLog("Sender: " + title);
		# Bsp.: api.zdf.de/../zdfinfo-live-beitrag-100.json?profile=player2:
		player2_url = stringextract('"content":"', '"', rec)

		thumb 	= stringextract('data-src="', '"', rec)			# erstes img = größtes
		geo		= stringextract('geolocation="', '"', rec)
		if geo:
			geo = "Geoblock: %s" % geo
		fsk		= stringextract('-fsk="', '"', rec)
		if fsk:
			fsk = "FSK: %s" % fsk
			fsk = fsk.replace('none', 'ohne')
		tagline = "%s,  %s" % (geo, fsk)

		PLog("player2_url: " + player2_url)
		if player2_url:
			page, msg = get_page(path=player2_url, header=header)
			# Bsp.: 247onAir-203
			assetid = stringextract('assetid":"', '"', page)
			assetid = assetid.strip()
			
		PLog(assetid); 
		if assetid:
			videodat_url = "https://api.zdf.de/tmd/2/ngplayer_2_3/live/ptmd/%s" % assetid
			page, msg	= get_page(path=videodat_url, header=header)
			PLog("videodat: " + page[:40])
			#PLog(page) 	# Debug
		
			href = stringextract('"https://',  'master.m3u8', page) 	# 1.: auto
			if href:
				href = 	"https://" + href + "master.m3u8"
				# Zeile: "title_sender|href|thumb|tagline"
				zdf_streamlinks.append("%s|%s|%s|%s" % (title, href,thumb,tagline))	
	
	PLog("zdf_streamlinks: %d" % len(zdf_streamlinks))
	page = "\n".join(zdf_streamlinks)									# Ablage Cache
	#skip_log=False				# Debug
	if skip_log == False:
		PLog(page)														# für IPTV-Interessenten
	Dict("store", 'zdf_streamlinks', page)
	return zdf_streamlinks	
#-----------------------------------------------
# ZDF-Links s. get_ZDFstreamlinks
# Aufruf get_sort_playlist (<- EPG_Sender, EPG_ShowAll,
#	 TVLiveRecordSender), SenderLiveListe, get_playlist_img
# Die api-Url's der Senderliste (Block broadcastedOn) enthalten
#	nicht alle regionalen Sender (Bsp. BR Nord) - diese werden 
#	in get_IPTVstreamlinks  ermittelt (via Tag IPTVSource in 
#	livesenderTV.xml.
# 01.12.2021 erweitert um Liste für Untertitel-Links
# 17.02.2022 Auswertung publicationService/name statt
#	longTitle
# 29.10.2023 force=True: InfoAndFilter -> refresh_streamlinks
#
def get_ARDstreamlinks(skip_log=False, force=False):
	PLog('get_ARDstreamlinks:')
	PLog("skip_log: " + str(skip_log)); PLog("force: " + str(force))
	days = int(SETTINGS.getSetting('pref_tv_store_days'))
	PLog("days: %d" % days)
	CacheTime = days*86400							# Default 1 Tag
	#days=0	# Debug

	ID = "ard_streamlinks"
	if days and force == False:						# skip CacheTime=0
		page = Dict("load", ID, CacheTime=CacheTime)
		page = py2_encode(page)

		if len(str(page)) > 100:					# bei Error nicht leer od. False von Dict
			if skip_log == False:
				PLog(page)							# für IPTV-Interessenten
			return page.splitlines()
		
	icon = R(ICON_TOOLS)
	xbmcgui.Dialog().notification("Cache ARDlinks:","wird erneuert",icon,3000)
	
	# api_url wie Livestreams in Main_NEW
	api_url = "https://api.ardmediathek.de/page-gateway/widgets/ard/editorials/4hEeBDgtx6kWs6W6sa44yY?pageNumber=0&pageSize=24"
	page, msg = get_page(path=api_url)				# Links neu holen
	if page == '':
		PLog('get_ARDstreamlinks: leer')
		return []

	content = blockextract('"broadcastedOn":', page)
	PLog("Senderliste: %d" % len(content))	
	
	ard_streamlinks=[]
	for rec in content:												# Schleife  Web-Sätze		
		title=''; href=''; streamurl=''; thumb=''
		title = stringextract('name":"', '"', rec)					# publicationService":{"name -> livesenderTV.xml 
		href_list = blockextract('href":"', rec, '"type"')
		for h in href_list:
			if '?devicetype=pc' in h:								# Stream-Quellen
				href = stringextract('href":"', '"', h)
				break
		thumb = stringextract('src":"', '"', rec)
		thumb = thumb.replace('{width}', '720')					

		if href:
			PLog("lade_livelink: " + title)
			linkid = stringextract("item/", "?", href)				# für programm-api.ard (ShowSeekPos)

			page, msg = get_page(path=href)							# s.a. Livestream ARDStartSingle
			streamurl = stringextract('_stream":"', '"', page)		# ab Okt. 2022 keine UT-Links mehr gesehen	
			streamurl = streamurl.replace("index.m3u8", "master.m3u8")	# Fix ab 03.12.2022 (verhindert Startverzög. > 10sec)  
					
		PLog("Satz1:")
		PLog(title); PLog(href); PLog(streamurl); PLog(linkid);
		# Zeile: "title_sender|streamurl|thumb|linkid"
		ard_streamlinks.append("%s|%s|%s|%s" % (title, streamurl,thumb,linkid))	
	
	PLog("ard_streamlinks: %d" % len(ard_streamlinks))
	page = "\n".join(ard_streamlinks)									# Ablage Cache
	#skip_log=False				# Debug
	if skip_log == False:
		PLog(str(ard_streamlinks))										# Ausgabe im LOG für IPTV-Interessenten
	Dict("store", ID, page)
	return ard_streamlinks	
#-----------------------------------------------
# ähnlich get_ZDFstreamlinks + get_ARDstreamlinks
# Aufruf get_sort_playlist (<- EPG_Sender, EPG_ShowAll,
#	 TVLiveRecordSender), SenderLiveListe, get_playlist_img
# holt Details von githubs iptv-Listen, falls
#	livesenderTV.xml den Tag IPTVSource enthält
# 29.10.2023 force=True: InfoAndFilter -> refresh_streamlinks
#
#
def get_IPTVstreamlinks(skip_log=False, force=False):
	PLog('get_IPTVstreamlinks:')
	PLog("skip_log: " + str(skip_log)); PLog("force: " + str(force))
	days = int(SETTINGS.getSetting('pref_tv_store_days'))
	PLog("days: %d" % days)
	CacheTime = days*86400							# Default 1 Tag
	#days=0	# Debug

	ID = "iptv_streamlinks"
	if days and force == False:						# skip CacheTime=0
		page = Dict("load", ID, CacheTime=CacheTime)
		page = py2_encode(page)

		if len(str(page)) > 100:					# bei Error nicht leer od. False von Dict
			if skip_log == False:
				PLog(page)							# für IPTV-Interessenten
			return page.splitlines()
		
	icon = R(ICON_TOOLS)
	xbmcgui.Dialog().notification("Cache IPTVlinks:","wird erneuert",icon,3000)
	
	# Url der IPTV-Liste in Tag link in livesenderTV.xml
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	PLog(len(playlist))
	
	iptv_streamlinks=[]; 
	for p in playlist:													# Schleife Sender
		list_url_old=''; page_org=''
		if "link>IPTVSource" in p:
			PLog(p[:60])	# Debug	
			list_url = stringextract('link>IPTVSource|', '</', p)  		# Link Github-Liste
			list_url = "https://github.com%s?raw=true" % list_url
			PLog(list_url); PLog(list_url == list_url_old)
			
			if list_url != list_url_old:								# schon geladen?
				page_org, msg = get_page(path=list_url)
				
			if page_org: 
				list_url_old = list_url
				thumb=''; streamurl=''
				play_sender = stringextract('<title>', '</title>', p)	# Abgleich SenderLiveListe
				tvg_name = stringextract('<tvg-name>', '</tvg-name>',p)	# Sendername
				play_sender = py2_decode(play_sender); tvg_name = py2_decode(tvg_name); 
				pos = page_org.find(tvg_name)
				if pos > 0:
					PLog("found: %s" % tvg_name)
					page = page_org[pos:]								# Page ab Fund
					item = stringextract(tvg_name, '#EXTINF', page)		# Satz ausschneiden
					PLog(item)
					if item:
						links = blockextract('http', item)				# Links Logo + Stream, http: mögl.
						if len(links) >= 1:
							thumb = stringextract('tvg-logo="', '"', item)
							streamurl = links[1]
							title = tvg_name						
						
							PLog("Satz2:")
							PLog(title); PLog(streamurl); PLog(thumb)
							# Zeile: "title_sender|streamurl|thumb|''"
							iptv_streamlinks.append("%s|%s|%s|%s" % (play_sender, streamurl,thumb,''))	

	PLog("iptv_streamlinks: %d" % len(iptv_streamlinks))
	page = "\n".join(iptv_streamlinks)									# Ablage Cache
	#skip_log=False				# Debug
	if skip_log == False:
		PLog(str(iptv_streamlinks))										# Ausgabe im LOG für IPTV-Interessenten
	Dict("store", ID, page)
	return iptv_streamlinks	

#-----------------------------------------------
# Untertitel-Streamlink aus master- od. index.m3u8 ermitteln
#  -> Liste (für li.setSubtitles)
# Aufruf: PlayVideo
def get_streamurl_ut(streamurl):
	PLog('get_streamurl_ut:')
	
	page, msg = get_page(path=streamurl)
	pos = page.find('GROUP-ID="subs",URI="')
	if pos < 0:
		PLog("streamurl_ut=streamurl_ut")
		return streamurl									# streamurl_ut = streamurl
	
	page = page[pos:]
	uri = stringextract('URI="', '"', page)					# Bsp.: master_subs_webvtt.m3u8
	PLog("URI: " + uri)
	if uri.startswith("https") and uri.endswith("m3u8"):	# kompl. UT-Link https://xx.akamaized.net/..
		streamurl_ut = uri
	else:
		streamurl_ut = streamurl.replace("master.m3u8", uri)
	PLog("streamurl_ut: " + streamurl_ut)
	return streamurl_ut	 
			
#---------------------------------------------------------------------------------------------------
# Aufruf: 
# Icon aus livesenderTV.xml holen
# 24.01.2019 erweitert um link
# 25.06.2020 für SenderLiveResolution um EPG_ID erweitert 
# 26.06.2020 Anpassung für ZDF-Sender (bei Classic-Livestreams: 
#	Arte, KiKA, 3sat)
# 11.04.2021 Anpassung für ARD-Classic-Sender
# 26.05.2022 Anpassung für IPTV-Sender
#
def get_playlist_img(hrefsender):
	PLog('get_playlist_img: ' + hrefsender); 
	playlist_img=''; link=''; EPG_ID=''; img_streamlink=''
	playlist = RLoad(PLAYLIST)		
	playlist = blockextract('<item>', playlist)
	for p in playlist:
		title_sender = stringextract('hrefsender>', '</hrefsender', p) 
		if title_sender == '':
			title_sender = stringextract('<title>', '</title>', p) 	# IPTVSource-Sender
		s = stringextract('title>', '</title', p)	# Classic-Version
		if s:									# skip Leerstrings
			# PLog(s); PLog(hrefsender);		# Debug
			if up_low(s) in up_low(hrefsender):
				PLog("Treffer:"); PLog(s); PLog(hrefsender);
				playlist_img = stringextract('thumbnail>', '</thumbnail', p)
				playlist_img = R(playlist_img)
				link =  stringextract('link>', '</link', p)
				
				if "ZDFsource" in link:								# Anpassung für ZDF-Sender
					zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
					link=''	
					# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
					for line in zdf_streamlinks:
						items = line.split('|')
						# Bsp.: "ZDFneo " in "ZDFneo Livestream":
						if up_low(title_sender) in up_low(items[0]): 
							link = items[1]
							if items[2]:							# Icon aus IPTVSource?
								img_streamlink = items[2]
							break
					if link == '':
						PLog('%s: ZDF-Streamlink fehlt' % title_sender)	
						
				if "ARDclassicSource" in link:						# Anpassung für ARD-Clasic-Sender
					ard_streamlinks = get_ARDstreamlinks(skip_log=True)
					link=''	
					# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
					for line in ard_streamlinks:
						items = line.split('|')
						if up_low(title_sender) in up_low(items[0]): 
							link = items[1]
							if items[2]:							# Icon aus IPTVSource?
								img_streamlink = items[2]
							break
					if link == '':
						PLog('%s: ARD-Streamlink fehlt' % title_sender)	
								
				if "IPTVSource" in link:							# Anpassung für IPTV-Sender
					iptv_streamlinks = get_IPTVstreamlinks()
					link=''	
					# Zeile ard_streamlinks: "webtitle|href|thumb|tagline"
					for line in iptv_streamlinks:
						items = line.split('|')
						if up_low(title_sender) in up_low(items[0]): 
							link = items[1]
							if items[2]:							# Icon aus IPTVSource?
								img_streamlink = items[2]
							break
					if link == '':
						PLog('%s: ARD-Streamlink fehlt' % title_sender)	
					
				EPG_ID =  stringextract('EPG_ID>', '</EPG_ID', p)
				PLog("EPG_ID für %s: %s" % (s, EPG_ID))
				break
	
	if img_streamlink:									# Vorrang Icon aus direkten Quellen	
		img = img_streamlink 
	
	if EPG_ID == '':
		PLog("%s: EPG_ID nicht gefunden/vorhanden" % s)
	PLog(playlist_img); PLog(link); 
	return playlist_img, link, EPG_ID

####################################################################################################
def MakeDetailText(title, summary,tagline,quality,thumb,url):	# Textdatei für Download-Video / -Podcast
	PLog('MakeDetailText:')
	title=py2_encode(title); summary=py2_encode(summary);
	tagline=py2_encode(tagline); quality=py2_encode(quality);
	thumb=py2_encode(thumb); url=py2_encode(url);
	
	summary=summary.replace('||', '\n'); tagline=tagline.replace('||', '\n');
	PLog(type(title)); PLog(type(summary)); PLog(type(tagline));
	detailtxt = ''
	detailtxt = detailtxt + "%15s" % 'Titel: ' + "'"  + title + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Beschreibung1: ' + "'" + tagline + "'" + '\r\n' 

	if summary != tagline: 
		detailtxt = detailtxt + "%15s" % 'Beschreibung2: ' + "'" + summary + "'"  + '\r\n' 	
	
	detailtxt = detailtxt + "%15s" % 'Qualitaet: ' + "'" + quality + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Bildquelle: ' + "'" + thumb + "'"  + '\r\n' 
	detailtxt = detailtxt + "%15s" % 'Adresse: ' + "'" + url + "'"  + '\r\n' 
	
	return detailtxt
		
#---------------------------------------------------------------------------------------------------
# 30.08.2018 Start Recording TV-Live
#	Kopfdoku + Code zu Plex-Problemen entfernt (bei Bedarf s. Github) -
#	unter Kodi nicht relevant
#
# Aufrufer: TVLiveRecordSender, JobMonitor (epgRecord), EPG_ShowAll via Kontextmenü
# 	Check auf ffmpeg-Settings bereits in TVLiveRecordSender, Check auf LiveRecord-Setting
# 		bereits in SenderLiveListePre
# Zur Arbeitsteilung JobMonitor / m3u8-Verfahren siehe Kopfdoku zu JobMonitor
#	
# 29.04.0219 Erweiterung manuelle Eingabe der Aufnahmedauer
# 04.07.2020 angepasst für epgRecord (Eingabe Dauer entf., Dateiname mit Datumformat 
#		geändert, Notification statt Dialog. epgJob enthält mydate (bereits für
#		detailtxt verwendet - Aufrufer: JobMonitor).
#		duration-Format: Sekunden (statt "00:00:00", für man. Eingaben konvertiert).
#  		Verlagert nach util (import aus  ardundzdf klappt nicht in epgRecord).
# 24.07.2020 Anpassung für Modul m3u8: JobID wird für KillFile verwendet, für
#	LiveRecording wird neuer Aufnahme-Job erzeugt (via JobMain 'setjob')
# 30.08.2020 experimentelles m3u8-Verfahren entf. - s. changelog.txt
# 12.03.2023 popen-Rückmeldung "None args" für LibreElec 11 ergänzt
# 17.04.2024 Ausfilterung spezieller Sender in TVLiveRecordSender
#
def LiveRecord(url, title, duration, laenge, epgJob='', JobID=''):
	PLog('LiveRecord:')
	PLog('url: %s, title: %s, duration: %s, laenge: %s' % (url, title, duration, laenge))
	
	icon = R("icon-record.png")
	sender=title
	
	import resources.lib.EPG as EPG					# -> now
	import resources.lib.epgRecord as epgRecord		# setjob in epgRecord.JobMain

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)							# Home-Button
	
	
	if epgJob == '':								# epgRecord: o. Eingabe Dauer
		if SETTINGS.getSetting('pref_LiveRecord_input') == 'true':	# Aufnahmedauer manuell
			duration = duration[:5]									# 01:00:00, für Dialog kürzen
			dialog = xbmcgui.Dialog()
			duration = dialog.input('Aufnahmedauer eingeben (HH:MM)', duration, type=xbmcgui.INPUT_TIME)
			PLog(duration)
			if duration == '' or duration == ' 0:00':
				msg1 = "Aufnahmedauer fehlt - Abbruch"
				PLog(msg1)
				MyDialog(msg1, '', '')
				return li	
			duration = "%s:00" % duration							# für ffmpeg wieder auffüllen
			laenge = "%s (Stunden:Minuten)" % duration[:5]			# Info nach Start, s.u.
			PLog('manuell_duration: %s, laenge: %s' % (duration, laenge))
			
	if ':' in str(duration):					# manu. Eingabe (TARGETDURATION gilt, falls größer)
		duration = CalculateDuration(duration)
		duration = int(duration / 1000)			
			
	dest_path = SETTINGS.getSetting('pref_download_path')
	dest_path = dest_path  							# Downloadverzeichnis fuer curl/wget verwenden
	now = datetime.datetime.now()
	mydate = now.strftime("%Y%m%d_%H%M%S")			# Zeitstempel
	dfname = make_filenames(title)					# Dateiname aus Sendername generieren
	if epgJob:										# vorgeplante Aufnahme
		dfname = "%s_%s.mp4" % (epgJob, dfname)
	else:
		dfname = "%s_%s.mp4" % (mydate, dfname)
	PLog("dfname: %s" % dfname) 	
	dest_file = os.path.join(dest_path, dfname)
	
	if ":" in sender:
		sender = sender.split(":")[0] 
	url = url_correction(url, sender)				# Url-Korrektur, z.B. für LEIPZIG_FERNSEHEN 
	
	if check_Setting('pref_LiveRecord_ffmpegCall') == False:	
		return
	cmd = SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')
	PLog("url: %s,  duration: %s, dest_file: %s" % (url, duration, dest_file))
	cmd = cmd % (url, duration, dest_file)
	PLog("cmd: " + cmd); 
	
	PLog(sys.platform)
	if sys.platform == 'win32':							
		args = cmd
	else:
		args = shlex.split(cmd)							

	try:
		PIDffmpeg = ''
		sp = subprocess.Popen(args, shell=False)
		PLog('sp: ' + str(sp))					# "None args" OK, da Call hier ohne wait

		# Popen: 'None args' bei LibreElec 11
		if str(sp).find('object at') > 0 or str(sp).find('None args') > 0:  # subprocess.Popen object OK
			PIDffmpeg = sp.pid					# PID speichern bei Bedarf
			PLog('PIDffmpeg neu: %s' % PIDffmpeg)
			Dict('store', 'PIDffmpeg', PIDffmpeg)
			msg1 = 'Aufnahme gestartet:'
			msg2 = dfname
			# msg3 = "Aufnahmedauer: %s" % laenge
			PLog('Aufnahme gestartet: %s' % dfname)	
			# MyDialog(msg1, msg2, msg3)
			# Kodi unterlässt notification bei minimiertem Fenster, daher 
			#	beim epgJob Austausch gegen Sprachdatei: "ARDundZDF informiert:
			#	die Aufnahme einer Sendung wurde gestartet"
			if epgJob:									# vorgeplante Aufnahme
				url = R('ttsMP3_Monitor_Aufnahme_gestartet.mp3')
				PlayAudio(url, title='', thumb='', Plot='')
			else:										# Job für Recording erzeugen (wie m3u8-Verfahren)
				action="setjob" 
				now = EPG.get_unixtime(onlynow=True)
				start_end = "%s|%d" % (now, (int(now) + int(duration)))
				descr = "ffmpeg-recording"				# JobMain -> return ohne thread-Start
				sender = ''; setSetting='';
				JobID = epgRecord.JobMain(action, start_end, title, descr, sender, url, setSetting, PIDffmpeg)
				
				xbmcgui.Dialog().notification(msg1, msg2,icon,3000)
			return PIDffmpeg			
				
	
	except Exception as exception:
		msg = str(exception)
		PLog(msg)		
		msg1 ='Aufnahme-Problem'
		msg2 = dfname
		# MyDialog(msg1, msg2, '')
		xbmcgui.Dialog().notification(msg1, msg2,icon,3000)
		return li	
		
#--------------------------------------------------
# Url-Korrektur für Url vonNimble Streamer , z.B. für LEIPZIG_FERNSEHEN
#	nur private Sender betroffen.
# ffmpeg: Input/output error - Header-Test, manuelle Zuordnung des 
#	ersten Streams, Veränd. ffmpeg-Param. o.Ergebnis.
# Austausch https -> http OK
# 
def url_correction(url, sender):
	PLog('url_correction:')
	if url.startswith('http') == False:				# lokale + rtmp unangetastet
		return url
	
	# OK BadenTV
	TV_Liste = ["münchen.tv", "Leipzig Fernsehen",
				"Rhein-Neckar Fernsehen", "Franken Fernsehen"]
	new_url = url
	for tv in TV_Liste:
		if up_low(sender) in up_low(tv):
			PLog("Url_Korrektur: %s" % sender)
			new_url = url.replace('https:', 'http:')
	
	return new_url

#---------------------------------------------------------------------------------------------------
def check_Setting(ID):
	PLog('check_Setting: ' + ID)
	
	if ID == 'pref_LiveRecord_ffmpegCall':
		PLog(SETTINGS.getSetting('pref_LiveRecord_ffmpegCall'))
		# Test: Pfadanteil executable? 
		#	Bsp.: "/usr/bin/ffmpeg -re -i %s -c copy -t %s %s -nostdin"
		cmd = SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')	
		if cmd.strip() == '' or cmd.count("%s") < 3:				# mind. 3: url, duration, dest_file
			msg1 = 'ffmpeg-Parameter fehlen in den Einstellungen!'
			msg2 = 'Siehe Addon-Wicki auf Github'
			MyDialog(msg1, msg2, '')
			return False
			
		if os.path.exists(cmd.split()[0]) == False:
			msg1 = 'Pfad zu ffmpeg nicht gefunden.'
			msg2 = u'Bitte ffmpeg-Parameter in den Einstellungen prüfen, aktuell:'
			msg3 = 	SETTINGS.getSetting('pref_LiveRecord_ffmpegCall')
			MyDialog(msg1, msg2, msg3)
			return False
		return True
		
	if ID == 'pref_download_path':
		dest_path = SETTINGS.getSetting('pref_download_path')
		msg1	= 'LiveRecord:'
		if  dest_path == None or dest_path.strip() == '':
			msg2 	= 'Downloadverzeichnis fehlt in den Einstellungen'
			MyDialog(msg1, msg2, '')
			return False
		PLog(os.path.isdir(dest_path))
					
		if  os.path.isdir(dest_path) == False:
			msg2 	= 'Downloadverzeichnis existiert nicht'
			msg3	= "Settings: " + dest_path
			MyDialog(msg1, msg2, msg3)
			return False
		return True		
		
	if ID == 'pref_use_downloads':
		# Test auf Existenz curl/wget in DownloadExtern
		if SETTINGS.getSetting('pref_use_downloads') == 'true':
			dest_path = SETTINGS.getSetting('pref_download_path')
			if  os.path.isdir(dest_path) == False:
				msg1	= u'test_downloads: Downloads nicht möglich'
				msg2 	= 'Downloadverzeichnis existiert nicht'
				msg3 	= "Settings: " + dest_path
				MyDialog(msg1, msg2, msg3)
				return False				
		else:
			return False
		return True
		
#---------------------------------------------------------------------------------------------------
# schaltet boolean-Setting ID um und gibt Notification aus
# Aufrufer: Kontextmenü (Umschalter Downloads/Sofortstart)
# Format ID, Bsp.: 'pref_video_direct,false|pref_use_downloads,true'
def switch_Setting(ID, msg1,msg2,icon,delay):
	PLog('switch_Setting:')
	PLog(ID)
	delay = int(delay)
	
	ID_list=[]
	if '|' in ID:
		ID_list = ID.split('|')
	else:
		ID_list.append(ID)

	for item in ID_list:
		ID, boolset = item.split(',')
		SETTINGS.setSetting(ID, boolset)

	xbmc.executebuiltin('Container.Refresh')
	xbmcgui.Dialog().notification(msg1,msg2,icon,delay)
	return
		
####################################################################################################
# PlayVideo_Direct ruft PlayVideo abhängig von den Settings pref_direct_format + 
# pref_direct_quality auf.
# Listen-Formate:
#		"HLS Einzelstream ## Bandbreite ## Auflösung ## Titel#Url"
#		"MP4 Qualität: Full HD ## Bandbreite ## Auflösung ## Titel#Url"
# Auflösung/Bitrate In beiden Listen wg. re.search-Sortierung erford.!
# Aufrufer: build_Streamlists_buttons (Sofortstart), get_streamurl
# 20.05.2023 Verschmelzung MP4_List + HBBTV_List, Abgleich nach Auflösung
#	(Abgleich nach Bitrate entfällt)
# 18.05.2024 
#
def PlayVideo_Direct(HLS_List, MP4_List, title, thumb, Plot, sub_path=None, playlist='', HBBTV_List='', ID=''):	
	PLog('PlayVideo_Direct:')
	PLog(title); PLog(ID)
	PLog(len(HLS_List)); PLog(len(MP4_List)); PLog(len(HBBTV_List));
	#PLog(str(HLS_List)); PLog(str(MP4_List)); PLog(str(HBBTV_List)); # Debug
	myform = SETTINGS.getSetting('pref_direct_format')
	myqual = SETTINGS.getSetting('pref_direct_quality')
	PLog("myform: %s, myqual: %s" % (myform, myqual))
	icon = R(ICON_WARNING)
	
	for item in HLS_List:							# Audiostream entfernen
		if "vermutl. Audio" in item:
			HLS_List.remove(item)
			PLog(item)		
	
	msg1=''; msg2=''
	mode_hls=False; mode=''
	if 'HLS' in myform and  ID != "MVW":			# Austausch bei leeren Listen, bei MVW nur MP4-Quellen
		Stream_List = HLS_List
		if len(Stream_List) == 0:
			msg1 = u"HLS-Quellen fehlen"
			Stream_List = MP4_List
			msg2 = "verwende MP4"
			if len(Stream_List) == 0:
				Stream_List = HBBTV_List
				msg2 = "verwende HBBTV (MP4)"
				
			if str(MP4_List).find("//funk") > 0:	# ZDF-Funk immer ohne HLS-Quellen
				msg1=''; msg2=''
		else:
			mode_hls=True			
	else:
		myform = 'MP4'								# enth. auch Webm, VP8/Vorbis, VP9/Opus
		Stream_List = MP4_List
		PLog(Stream_List)
		PLog(HBBTV_List)
		if 'auto' in myqual:						# Sicherung gegen falsches MP4-Setting:
			myqual = '960x544'						# 	Default, falls 'auto' gesetzt
		if ID != "Arte" and len(HBBTV_List) > 0:
			Stream_List = Stream_List + HBBTV_List	# in HBBTV_List immer MP4 (Arte-HBBTV -> HLS)
		
		if len(Stream_List) == 0:
			msg1 = u"MP4-Quellen fehlen"
			Stream_List = HLS_List
			msg2 = "verwende HLS"
			mode_hls=True			

	if len(Stream_List) == 0:						# alle Listen leer		
			msg1 = u"Video-Quellen fehlen"
			msg2 = u"nicht verfügbar: HLS, MP4"
			icon = R(ICON_WARNING)
			xbmcgui.Dialog().notification(msg1,msg2,icon,4000)	
	else:	
		if msg1 and msg2:								# Hinweis zu Austausch
			if "/live/" in Stream_List[0] or 'ivestream' in Stream_List[0]:	
				PLog("is_Livestream")					# 	entf. bei Kennz. als Livestream
			else:
				xbmcgui.Dialog().notification(msg1,msg2,icon,4000)	
		
	Default_Url=''
	PLog("mode_hls: " + str(mode_hls))
	PLog(myqual)
	PLog(Stream_List)
	if mode_hls:				
		if myqual.find('auto') >= 0:
			mode = 'Sofortstart: HLS/auto'
			Default_Url = Stream_List[0].split('#')[-1]		# master.m3u8 Pos. 1
			PLog("Default_Url1: %s" % Default_Url)
		else:
			mode = 'HLS/Einzelstream'
			if "** auto **" in Stream_List[0]:				# sonst sort_error für Auflösung 
				if len(Stream_List) == 1:
					Default_Url = Stream_List[0].split('#')[-1]	# einzigen Stream bewahren
				del Stream_List[0]
	else: 
		mode = 'MP4'
	PLog("mode: " + mode)
	
	if Default_Url == '':								# besetzt: HLS/auto
		# Sortierung Stream_List wieder nach Auflösung (verlässlicher) - wie StreamsShow
		# höchste Auflös. nach unten, x-Param.: Auflösung
		try:
			if u"Auflösung" in str(Stream_List):
				Stream_List = sorted(Stream_List,key=lambda x: int(re.search(r'sung (\d+)x', x).group(1)))	
		except Exception as exception:					# bei HLS/"auto", problemlos da vorsortiert durch Sender
			PLog("sort_error: " + str(exception))
			myqual = "auto"								# verwende Default_Url - kein Abgleich mit width

		if len(Stream_List) > 0:						# Default: höchste Url
			Default_Url = Stream_List[-1].split('#')[-1]	# Fallback: master.m3u8 Pos. 1
			PLog("Default_Url2: %s" % Default_Url)
	
	PLog("Default_Url3: %s" % Default_Url)
	url = Default_Url 
	PLog(str(Stream_List)[:80])
	
		
	if 'auto' not in myqual:							# Abgleich width mit Setting
		mywidth = myqual.split('x')[0]
		for item in Stream_List:			
			width="320"									# Default (u.a. für LibreElec 20.0-ALPHA1
			res = item.split('**')[2]
			if '0x0' in res:							# Auflösung 0x0 (vermutl. Audio)
				continue
				
			PLog("item: " + item)
			try:
				width = re.search(r'sung (\d+)x', item).group(1)
			except Exception as exception:
				PLog("search_error: " + str(exception))
				#continue
			
			if "** veryhigh **" in item:			# Rückübersetzung HLS-Qualitäten
				width = "1280"						#	bei ZDF-Api-Streams
			if "** high **" in item:
				width = "960"
			if "** med **" in item:
				width = "640"
			if "** low **" in item:
				width = "480"
			
			PLog("width %s, mywidth %s" % (width, mywidth))
			if int(width) >= int(mywidth):
				PLog("set_width:" + width)
				url = item.split('#')[-1]
				mode = '%s | width %s (Setting: %s)' % (mode, width, mywidth)
				break


	# Beachte im Log: beim Aufruf aus strm-Modul (Kontext-Thread): läuft noch
	#	MY_SCRIPT aus get_streamurl. PlayVideo wird gestartet + stoppt bei
	#	'PlayVideo_Start: listitem'. Im Log wirkt es, als führe
	#	Kodi sowohl if- als auch else-Statement aus. Das Log für den Thread 
	#	kann sich zeitlich weiter vorn befinden (s. FLAG_OnlyUrl).
	PLog('Direct: %s | %s' % (mode, url))
	PLog(FLAG_OnlyUrl)								# Flagdatei
	if os.path.isfile(FLAG_OnlyUrl):				# Rückgabe Url -> strm-Modul, kein Start
		PLog("FLAG_OnlyUrl")
		os.remove(FLAG_OnlyUrl)						# zusätzl. Leichenbehandl. im Haupt-PRG
		RSave(STRM_URL, url)						# indirekte Rückgabe 	-> 
		return url									# direkte Rückgabe 		-> strm-Modul
		exit(0)
	else:											# default
		PlayVideo(url, title, thumb, Plot, sub_path)
	return ''

#---------------------------------------------------------------------------------------------------
# PlayVideo: 
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Dasselbe gilt für TV-Livestreams.
#		Param. Merk (added in Watch): True=Video aus Merkliste  
#
# 	Aufruf indirekt (Kennz. Playable): 	
#		SenderLiveListe
#		ARD_FlatListEpisodes, get_json_content 
#		ZDF_Live, ZDF_get_content 
#		ARDSportVideo, ARDSportMedia, ARDSportSliderSingle, AddonStartlist,
#		WDRstream, VideoTools (Downloads)
#							
#	Aufruf direkt: 
#		ARDStartVideoStreams, ARDStartVideoMP4,
#		SingleSendung (m3u8_master), SenderLiveResolution 
#		ZDF_Live, show_formitaeten (ZDF)
#		
#		PlayMonitor (Modul Playlist, Param. playlist='true'), 
#		PlayVideo_Direct, ARD_get_strmStream
#		WDRstream
#
#	Format sub_path s. https://alwinesch.github.io/group__python__xbmcgui__listitem.html#ga24a6b65440083e83e67e5d0fb3379369
#	Die XML-Untertitel der ARD werden gespeichert + nach SRT konvertiert (einschl. minus 10-Std.-Offset)
#	Resume-Funktion Kodi-intern  DB MyVideos107.db (107-121), Tab files (idFile, playCount, lastPlayed) + (via key idFile),
#		bookmark (idFile, timelnSeconds, totalTimelnSeconds) - s. kodi.wiki/view/Databases/MyVideos,
#		kodi.wiki/view/Databases (107.db-121.db)
#
#	Untertitel bei Livestreams: ab Okt. 2022 keine getrennten Livestream-Link für UT mehr.
#		ARD-Sender: die in get_streamurl_ut ermittelten Links (z.B. ../master_subs_webvtt.m3u8) 
#		funktionieren weder in Kodi (IA: Unable to create subtitle parser) noch im  VLC 
#		- neue Funktion get_streamurl_ut z.Z. noch nutzlos + stillgelegt
#		ZDF-Sender: funktionieren inzwischen. Mehrkanal-Url's für HLS. Die master.m3u8-Dateien 
#		enthalten jeweils 2 Untertitel-Links (../8.m3u8) für die webvtt-Segmente. 
#		- neue Funktion get_streamurl_ut z.Z. noch nutzlos + stillgelegt
#		30.01.2023 Problem beim Team inputstream.adaptive in Bearbeitung:
#			https://github.com/xbmc/inputstream.adaptive/issues/1109
#
#	01.02.2023 seek für ARD-Livestream bei Nutzung inputstream.adaptive kann entfallen, Stream
#		startet korrekt (Leia, Matrix, Nexus), Issue geschlossen:
#		https://github.com/rols1/Kodi-Addon-ARDundZDF/issues/19
#
def PlayVideo(url, title, thumb, Plot, sub_path=None, playlist='', seekTime=0, Merk="", live=""):	
	PLog('PlayVideo:'); PLog(url); PLog(title);	 PLog(Plot[:100]); 
	PLog(sub_path); PLog(seekTime); PLog("live: " + live); PLog(playlist)
	import sqlite3										# Abfrage MyVideos*.db

	Plot=transl_doubleUTF8(Plot)
	Plot=(Plot.replace('[B]', '').replace('[/B]', ''))	# Kodi-Problem: [/B] wird am Info-Ende platziert
	url=url.replace('\\u002F', '/')						# json-Pfad noch unbehandelt

	li = xbmcgui.ListItem(path=url)		
	# li.setArt({'thumb': thumb, 'icon': thumb})
	li.setArt({'poster': thumb, 'banner': thumb, 'thumb': thumb, 'icon': thumb, 'fanart': thumb})	
	
	Plot=Plot.replace('||', '\n')				# || Code für LF (\n scheitert in router)
	#li.setProperty('IsPlayable', 'true')		# hier unwirksam
	li.setInfo(type="video", infoLabels={"Title": title, "Plot": Plot, "mediatype": "video"}) # s.u.
	
	sub_list=[]
	PLog("pref_UT_ON: " + SETTINGS.getSetting('pref_UT_ON'))	
	if SETTINGS.getSetting('pref_UT_ON') == 'true':
		if sub_path:								# Konvertierung ARD-UT, Pfade -> Liste 
			sub_list = sub_path_conv(sub_path)
			li.setSubtitles(sub_list)
			# xbmc.Player().showSubtitles(True)		# hier unwirksam, s.u. (isPlaying)
		else:
			#if "mcdn.daserste.de" in url and url.endswith("master.m3u8"):
			# experimentelle Funktion thread_getsubtitles einschl. vtt_convert archiviert
			#	in ../m3u8_download,Untertitel/Untertitel/thread_getsubtitles.py
			# s.a. https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?postID=697102#post697102 ff.			
			pass
			# z.Z. get_streamurl_ut nutzlos, da weder für IA noch Kodi-Player nutzbar - s.o.
			#if url.endswith(".m3u8"):				# UT-Link aus Inhalt master.m3u8 ermitteln
			#	sub_path = get_streamurl_ut(url)
			#	sub_list.append(sub_path); sub_list.append(sub_path)
			#	li.setSubtitles(sub_list)
			
	PLog('sub_list: ' + str(sub_list));				# s. get_subtitles
		
	# Abfrage: ist gewähltes ListItem als Video deklariert? - Falls ja,	
	#	erfolgt der Aufruf indirekt (setResolvedUrl). Falls nein,
	#	wird der Player direkt aufgerufen. Direkter Aufruf ohne IsPlayable-Eigenschaft 
	#	verhindert Resume-Funktion.
	# Mit xbmc.Player() ist  die Unterscheidung Kodi V18/V17 nicht mehr erforderlich,
	#	xbmc.Player().updateInfoTag bei Kodi V18 entfällt. 
	# Die Player-Varianten PlayMedia + XBMC.PlayMedia scheitern bei Kommas in Url.	
	# 29.01.2020 sleep verhindert selbständige Restarts nach Stop - Bsp. phoenix/
	#	Sendungen/"Armes Deutschland? Deine Kinder" 
	IsPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)') # 'true' / 'false'
	PLog("IsPlayable: %s" % IsPlayable)								# IsPlayable: "false" / "true" !
	PLog("kodi_version: " + KODI_VERSION)							# Debug
	# kodi_version = re.search('(\d+)', KODI_VERSION).group(0) 		# Major-Version reicht hier - entfällt
	
	play_time=0; video_dur=0										# hier dummies (rel. -> PlayMonitor) 		
	url = url_check(url, caller='PlayVideo')						# Url-Check: False oder Redirect-Url
	if url:
		
		# Zuletzt-gesehen-Liste (STARTLIST) verwenden, Live-Streams
		# werden später ausgeschlossen (s. prepare_resume), Aktualiserung
		# der Liste in monitor_resume:
		startlist = SETTINGS.getSetting('pref_startlist')
		maxvideos = SETTINGS.getSetting('pref_max_videos_startlist')
		if  startlist=='true' and playlist  !='true':				# Startlist  (true: skip bei playlist-Url)
			if not live:											# Live für Video-Startlist ausschließen
				PLog("maxvideos: %s, STARTLIST: %s" % (maxvideos, STARTLIST))
				started_videos=""
				if os.path.exists(STARTLIST):
					started_videos= RLoad(STARTLIST, abs_path=True)		# Video-Startlist laden
					started_videos=py2_encode(started_videos)
					started_videos= started_videos.splitlines()
				if started_videos == "":
					started_videos=[]
				PLog("started_videos: %d" % len(started_videos))
				if len(started_videos) >= int(maxvideos)-1:				# ältesten Eintrag löschen (Basis 0)
					del started_videos[0]
					v = started_videos[0]
					PLog("delete_video_0: " + v[:40])
				
				dt = datetime.datetime.now()							# Format 2017-03-09 22:04:19.044463
				now = time.mktime(dt.timetuple())						# Unix-Format 1489094334.0 -> Sortiermerkmal
				Plot=Plot.replace('\n', '||')
				if 'gestartet: [COLOR darkgoldenrod]' in Plot: 			# Video aus Startlist:
					mark = '[/COLOR]||||'								# 	Datum/Zeit lokal entfernen
					pos = Plot.find(mark) + len(mark)
					Plot = Plot[pos:]
					
				new_line = u"%s###%s###%s###%s###%s###sub_path:%s###" % (now, title, url, thumb, Plot, sub_path) 
				new_line = py2_encode(new_line)
				PLog("new_line: " + new_line)

				new_list=[]	
				try:					
					for item in started_videos:							# umkopieren
						item = py2_encode(item)
						if py2_encode(url) not in item:					# skip Einträge mit gleicher Url
							new_list.append(item)	
				except Exception as exception:
					PLog("util_error: " + str(exception))
					PLog(item); PLog(url)

				new_list.append(new_line)								# neuer Satz, Ergänzung s. monitor_resume
				PLog(len(new_list))							
		
		#-------------------------------------------------------# Play		
		# playlist: Start aus Modul Playlist (s.o.)
		player = xbmc.Player()
		try:
			from platform import release						# für Verhind. Rekursion 
			OS_RELEASE = release()
		except:
			OS_RELEASE =''
		PLog("OS_RELEASE: " + OS_RELEASE)		

		# Check auf inputstream.adaptive (IA) nicht erforderlich
		# s. https://github.com/xbmc/inputstream.adaptive,
		# 	https://github.com/xbmc/inputstream.adaptive/wiki/Integration
		# ab Kodi 20 Auswahl von Streams + -Eigenschaften
		# IA funktioniert nicht mit lokalen m3u8-Dateien ( 
		#	relativ + absolut, s.a.:
		# 	https://github.com/xbmc/inputstream.adaptive/issues/701)
		if url.endswith('.m3u8') or url.endswith('.mpd'):	# SetInputstreamAddon HLS/Dash
			if SETTINGS.getSetting('pref_inputstream') == 'true':
				PLog("SetInputstreamAddon:")
				li.setMimeType('application/vnd.apple.mpegurl')
				if PYTHON2:
					li.setProperty('inputstreamaddon', 'inputstream.adaptive')
				else:
					# Kodi-Debug Matrix: depricated, use
					#	 #KODIPROP:inputstream=inputstream.adaptive', 'inputstream.adaptive'
					li.setProperty('inputstream', 'inputstream.adaptive')
				if url.endswith('.m3u8'):
					li.setProperty('inputstream.adaptive.manifest_type', 'hls')
				else:		
					li.setProperty('inputstream.adaptive.manifest_type', 'mpd')	
					li.setMimeType('application/dash+xml')	
				li.setContentLookup(False)

					# für Tests mit inputstream.ffmpegdirect - siehe
					#	https://github.com/xbmc/inputstream.ffmpegdirect
				#li.setProperty('inputstream', 'inputstream.ffmpegdirect')
				#li.setProperty('inputstream.ffmpegdirect.manifest_type', 'hls')				
				#li.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'timeshift')				
				#li.setProperty('inputstream.ffmpegdirect.stream_mode', 'true')				
				#li.setContentLookup(False)
	

		PLog("url: " + url); PLog("playlist: %s" % playlist)
		if IsPlayable == 'true' and playlist !='true':			# true - Call via listitem
			PLog('PlayVideo_Start: listitem')
			xbmcplugin.setResolvedUrl(HANDLE, True, li)			# indirekt

		else:													# false, None od. Blank - Playlist
			PLog('PlayVideo_Start: direkt, playlist: %s' % playlist)
			line = Dict("load", 'Rekurs_check', CacheTime=10)	# Dict-Abgleich url/Laufzeit
			# Rekursion unter Nexus nicht mehr beobachtet - mit Auslaufen von Matrix entfernen
			PLog(line)
			oldurl='' 
			if line != False:									# Rekursions-Check erforderlich
				oldurl, old_dur, old_now = line.split('||')
				if oldurl and oldurl in url:
					now = time.time(); 
					now=int(now); old_now=int(float(old_now)); old_dur=int(float(old_dur))
					PLog("now - old_now: %d,  old_dur %d" % (now-old_now, old_dur))
					if (now - old_now) < old_dur + 5:					# erneuter Aufruf vor regul. Videoende?
						#if SETTINGS.getSetting('pref_nohome') == 'true': 12.06.2023 gelöst vom Status pref_nohome
						msg1 = "Videoabbruch"; msg2 = "wegen vermutl. Rekursion"
						icon = R(ICON_WARNING)
						xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
						PLog("Rekursions_exit")
						return

			player.play(url, li, windowed=False) 					# direkter Start
			xbmc.sleep(200)
			
			if playlist == "":										# Verhind. Rekursion (ohne Homebutton)
				if SETTINGS.getSetting('pref_nohome') == 'true':
					PLog("pref_nohome=true")
					if "-tegra-" in OS_RELEASE == False:			# ev. prüfen: "-tegra-" in OS_RELEASE +
						exit(0)										#	nicht bei Shield + FT1-Stick.				

		while 1:													# seekTime setzen
			if player.isPlaying():
				xbmc.sleep(500)										# für Raspi erforderl.
				seekTime = float(str(seekTime))						# OK für PY2 + PY3
				video_dur = player.getTotalTime()
				PLog("check_seekTime %s, video_dur %s" % (str(seekTime), str(video_dur)))
				if 	seekTime > video_dur:							# Sicherung
					seekTime = 0	
				if seekTime > 0:
					PLog("set_seekTime %s" % str(seekTime))	
					player.seekTime(seekTime) 						# Startpos aus PlayMonitor (HLS o. Wirkung)
				play_time = player.getTime()						# Resume-Check verschoben -> monitor_resume
				xbmc.sleep(500)										# für Raspi erforderl., sonst 0 möglich
				video_dur = player.getTotalTime()
				now = time.time()
				line = "%s||%s||%s" % (url, str(video_dur), now)
				Dict("store", 'Rekurs_check', line) 
				break
			xbmc.sleep(200)

		# waitForAbort für Player-Warteschleife statt while(1) - hilft gegen Buffern:
		# UT Livestreams: falls sub_path und sub_list leer, bezieht Kodi die UT aus
		#	der m3u8-Datei											
		monitor = xbmc.Monitor(); i=0; max_secs=5 					# showSubtitles setzen, sobald Player spielt
		player_detect=False
		PLog("Subtitles: wait_for_Player(%d sec), sub_path: %s" % (max_secs, sub_path))
		while 1:
			xbmc.sleep(1000)
			i=i+1
			if player.isPlaying():
					PLog("player_isPlaying: %d sec" % i)
					if SETTINGS.getSetting('pref_UT_ON') == 'true':
							if len(sub_list) > 0:				# für Livestreams
								PLog("Player_Subtitles: %s" % sub_list[0])
								xbmc.Player().setSubtitles(sub_list[0])
					else:  										# Freeze in Windows bei späterem Einschalten 
							if sub_path:						# Abschalten nur mit sub_path, i.d.R. nicht bei Live
								PLog("Player_Subtitles: off")
								xbmc.Player().showSubtitles(False)
					player_detect=True
					break
			if i >= max_secs:
					PLog("Subtitles: abort_player_detect")
					player_detect=False
					break

		# Streamuhrzeit entspr. Setting + Status Player: 
		PLog("player_detect: %s, live: %s" % (str(player_detect), live))
		if SETTINGS.getSetting('pref_inputstream') == 'true':
			if SETTINGS.getSetting('pref_streamtime') == 'true':
				if live:											# ShowSeekPos nur bei Live-Streams
					if player_detect:
						xbmc.sleep(2000)
						PLog("Thread_ShowSeekPos_start:")			# Github-issue #30: Seek-Pos. -> Streamuhrzeit
						bg_thread = Thread(target=ShowSeekPos, args=(player, url))
						bg_thread.start()
						return

		# Monitoring player.getTime für STARTLIST - Livestreams ausgenommen
		# Issue: Kodi startet monitor_resume bei playlist=='true'
		if startlist == 'true':						# Resume-Monitor Startlist (pref_startlist)
			PLog("prepare_resume")
			if "/live/" not in url:					# Streams wdrlokalzeit ohne live-Kennung in WDRstream						
				PLog("/live/ not in url")
				if playlist != 'true':				# zuständig: Modul playlist -> PlayMonitor
					PLog('playlist != true') 
					if not live:					# Sicherung, z.B. für Streams von ARDSportLiga3
						PLog('not_live')									
						xbmc.sleep(2000)
						PLog("call_monitor_resume")
						PLog("playlist: " + playlist)
						video_dur = player.getTotalTime()
						bg_thread = Thread(target=monitor_resume, args=(player, new_list, video_dur, seekTime))
						bg_thread.start()
						return						# ohne return startet Kodi monitor_resume, ohne zutreffende
													#	if-condition
	PLog("leave_PlayVideo")	
	return play_time, video_dur						# -> PlayMonitor
	xbmcplugin.endOfDirectory(HANDLE)

#-------------------------------------
# Monitoring player.getTime für STARTLIST - bisher nutzlos
# Problem: Blockaden möglich bei Direktstart mediatype="", 
#	daher in AddonStartlist mediatype auf "video" gesetzt.
#	Leider springt Kodi dann nach Playerende zurück in
#	AddonStartlist - STARTLIST bleibt unbearbeitet.
#	
def monitor_resume(player, new_list, video_dur, seekTime):
	PLog("monitor_resume:")
	PLog(video_dur); PLog(seekTime) 

	if os.path.exists(PLAYLIST_ALIVE):						# Beendet Kodis Fehl-Call (s. call_monitor_resume)
		PLog("detect_running_playlist")
		return

	monitor = xbmc.Monitor()
	if seekTime > 0 and seekTime < video_dur:				# seekTime größer als Vidoelänge möglich
		cnt=0
		while 1:
			play_time = player.getTime()						# Resume-Check
			PLog("play_time %d, video_dur %d, seekTime: %d" % (play_time, video_dur, seekTime))
			xbmc.sleep(1000)
			cnt=cnt+1
			if (cnt > 2) or (play_time > seekTime):
				break
	
		if play_time < seekTime:
			icon = R("Dir-video.png")
			msg1 = "Resume-Check:"
			msg2 = "Vorspulen leider gescheitert"
			xbmcgui.Dialog().notification(msg1, msg2, icon, 3000, sound=False)
		else:
			PLog("Resume-Check: OK")
	#---------------------------------------
	
	p_list=[]; play_time_last=0
	while 1:
		try:
			play_time = player.getTime()
			PLog(play_time)									# -> ab hier Zwangs-Ende bei Playerende möglich (s.o.)
		except Exception as exception:
			PLog("player_exception: " + str(exception))
			break
			
		p_list.append(play_time)							# Sync-Error-Liste, ähnlich ShowSeekPos
		if len(p_list) >= 3:
			diff = max(p_list) - min(p_list)
			if max(p_list) < 1 or diff <=1 :				# nach 3 sec: Sync-Error, ca. 2 noch OK
				PLog("p_list_syncfail: %s, diff: %d" % (str(p_list), diff))
				break
			p_list=[]						
		xbmc.sleep(1000)
	
	#---------------------------------------
	PLog("monitor_resume_stop")	
	del_val=75												# bei Bedarf Setting pref_delete_viewed verwenden
	seekPos=video_dur										# Default: kein Resume
	percent=0
	if int(play_time) > 0 and int(video_dur) > 0:
		try:												# Abgleich 75% Spielzeit
			percent = 100 * (float(play_time) / float(video_dur))	# Division / 0 möglich
			percent = int(round(percent))
			if percent < del_val:
				seekPos = play_time							# Resume-Position
		except Exception as exception:
			PLog("monitor_resume_exception: " + str(exception))
	else:
		PLog("play_time_and_seekPos_0")
		
	if seekPos < 10:										# 10 sec Mindestlänge für Resume
		seekPos=0

	line = new_list[-1]										# letzte Zeile ergänzen
	PLog("line: " + line)												
	if "###seekPos:" in line:
		line = line.split("###seekPos:")[0]					# alte Werte löschen
	# sub_path, seekPos, video_dur -> AddonStartlist
	line = "%s###seekPos:%s###video_dur:%s###" % (line, seekPos, video_dur)
	PLog("video_dur: %d, play_time: %d, seekPos: %d, percent: %d" %\
		(video_dur, play_time, seekPos, percent))
	PLog("line_completed: " + line)												
	new_list[-1] = line
	
	try:													# Korrektur früheres Format: jüngster zuletzt
		sorted(new_list, key=lambda x: re.search(r'(\d+).', x).group(1))
	except Exception as exception:
		PLog("sorted_error: " + str(exception))
	
	new_list = "\n".join(new_list)
	RSave(STARTLIST, new_list)
		
	PLog("Leave_monitor_resume")
	return

#-------------------------------------
# ARD-Untertitel konvertieren
# ARD-UT, ZDF-UT u.a. -> xml2srt ->
# 	Liste (für li.setSubtitles)
# 12.04.2024 Berücksichtigung vtt-Format
#	
def sub_path_conv(sub_path):
	PLog("sub_path_conv:")
	sub_path_org=sub_path
	
	sub_list=[]
	if 'ardmediathek.de' in sub_path or 'tagesschau.de' in sub_path:
		# ARD-Untertitel speichern
		local_path = "%s/%s" % (SUBTITLESTORE, sub_path.split('/')[-1])
		local_path = os.path.abspath(local_path)
		local_path = local_path.replace(':', '_')# Bsp. ../subtitles/urn:ard:subtitle:..
		try:
			urlretrieve(sub_path, local_path)
		except Exception as exception:
			PLog(str(exception))
			local_path = ''
		if 	local_path:							
			if sub_path.endswith(".vtt") == False:	# o. extension: xml-Format?
				sub_path = xml2srt(local_path)		# Konvertierung, Endung .srt, falls erfolgreich
			else:									# .vtt-Datei mit Styles ergänzen
				try:
					styles_path = '%s/resources/%s' % (ADDON_PATH, "UT_Styles_ARD")
					styles = RLoad(styles_path, abs_path=True)
					if styles == "":				# Ladeproblem?
						styles = "WEBVTT"
					vtt = RLoad(local_path, abs_path=True)
					vtt = vtt.replace("WEBVTT", styles)	# WEBVTT durch Styles-Defs ersetzen					
					RSave(local_path, py2_encode(vtt), withcodec=False)
				except Exception as exception:
					PLog("styles_error: " + str(exception))
				sub_path = local_path				# ohne Styles bei Exception
								
		sub_list.append(sub_path) 					# subtitleFiles: tuple or list
		if PYTHON3:
			sub_list.append(sub_path) 				# Matrix erwartet UT-Paar (kostete Lebenszeit..)
	else:
		if '|' in sub_path:							# ZDF 2 Links: .sub, .vtt
			sub_list = 	sub_path.split('|')											
		else:										# != ARD, ZDF
			sub_list.append(sub_path) 
			
	PLog("sub_path_conv_end: " + str(sub_list))		
	return sub_list
	
#---------------------------------------------------------------- 
# SSL-Probleme in Kodi mit https-Code 302 (Adresse verlagert) - Lösung:
#	 Redirect-Abfrage vor Abgabe an Kodi-Player
# Kommt vor: Kodi kann lokale Audiodatei nicht laden - Kodi-Neustart ausreichend.
# 30.12.2018  Radio-Live-Sender: bei den SSL-Links kommt der Kodi-Audio-Player auch bei der 
#	weiter geleiteten Url lediglich mit  BR, Bremen, SR, Deutschlandfunk klar. Abhilfe:
#	Wir ersetzen den https-Anteil im Link durch den http-Anteil, der auch bei tunein 
#	verwendet wird. Der Link wird bei addradio.de getrennt und mit dem http-template
#	verbunden. Der Sendername wird aus dem abgetrennten Teil ermittelt und im template
#	eingefügt.
# 	Bsp. (Sender=ndr):
#		template: 		dg-%s-http-fra-dtag-cdn.cast.addradio.de'	# %s -> sender	
#		redirect-Url: 	dg-ndr-https-dus-dtag-cdn.sslcast.addradio.de/ndr/ndr1niedersachsen/..
#		replaced-Url: 	dg-ndr-http-dus-dtag-cdn.cast.addradio.de/ndr/ndr1niedersachsen/..
# url_template gesetzt von RadioAnstalten (Radio-Live-Sender)
# 18.06.2019 Kodi 17.6:  die template-Lösung funktioniert nicht mehr - dto. Redirect - 
#				Code für beides entfernt.
#				Neue Kodivers. ansch. nicht betroffen, Kodi 18.2. OK
#			
def PlayAudio(url, title, thumb, Plot, header=None, FavCall=''):
	PLog('PlayAudio:'); PLog(url); PLog(title); PLog(FavCall); 
	title = cleanmark(title)					# Tags erscheinen im Titel des Player-Windows
	Plot=Plot.replace('||', '\n')				# || Code für LF (\n scheitert in router)
	
	if url.startswith('http') == False:			# lokale Datei
		if url.startswith('smb://') == False:	# keine Share
			url = os.path.abspath(url)
	else:										# 14.01.2022 Bsp. HTTP Error 404 NDR Schlager
		url = url_check(url, caller='PlayAudio')# False oder Redirect-Url
		if url == False:
			return
		
	
	# 1. Url einer Playlist auspacken, Bsp.: MDR-Sachsen Fußball-Livestream
	#	bei Bedarf ausbauen (s. get_m3u Tunein2017)
	if url.startswith('http') and url.endswith('.m3u'):  # Bsp.: avw.mdr.de/streams/284281-0_mp3_high.m3u
		page, msg = get_page(path=url)	
		if page:
			lines =page.splitlines()	
			for line in lines:
				if line.startswith('http'):
					url = line
	
	PLog('Player_Url: ' + url)

	li = xbmcgui.ListItem(path=url)				# ListItem + Player reicht für BR
	li.setArt({'thumb': thumb, 'icon': thumb})
	ilabels = ({'Title': title})
	ilabels.update({'Comment': '%s' % Plot})	# Plot im MusicPlayer nicht verfügbar
	li.setInfo(type="music", infoLabels=ilabels)							
	li.setContentLookup(False)
	
	# optionale Slideshow starten 
	path = SETTINGS.getSetting('pref_slides_path')
	PLog(path)
	slide_mode = SETTINGS.getSetting('pref_musicslideshow') 
	if "Kodi" in slide_mode:
		slide_mode = "Kodi"
	if "Addon" in slide_mode:				
		slide_mode = "Addon"
		
	if slide_mode != "Keine":
		if xbmcvfs.exists(path) == False:
			msg1 = 'Slideshow: %s' % slide_mode
			msg2 = 'Slideshow-Verzeichnis fehlt'
			xbmcgui.Dialog().notification(msg1,msg2,R('icon-stream.png'),4000)
		else:	
			if slide_mode == "Kodi":								# Slideshow Kodi
				xbmc.executebuiltin('SlideShow(%s, "recursive")' % path)
				PLog('Starte_SlideShow1: %s' % path)
				# Konfig: Kodi Player-Einstellungen / Bilder
				xbmc.sleep(200)
				xbmc.Player().play(url, li, False)
				return
			if slide_mode == "Addon":								# Slideshow Addon
				# Absicherung gegen Rekursion nach GetDirectory_Error 
				#	nach exit in SlideShow2 - exit falls STOPFILE 
				#	jünger als 4 sec:
				STOPFILE = os.path.join(DICTSTORE, 'stop_slides')
				if os.path.exists(STOPFILE):							
					now = time.time()
					PLog(now - os.stat(STOPFILE).st_mtime)
					if now - os.stat(STOPFILE).st_mtime < 4:	
						PLog("GetDirectory_Error_Rekursion")
						xbmc.executebuiltin("PreviousMenu")
						return
					else:
						os.remove(STOPFILE)							# Stopdatei entfernen	
				xbmc.Player().play(url, li, False)					# Start vor modaler Slideshow			
				import resources.lib.slides as slides
				PLog('Starte_SlideShow2: %s' % path)
				
				try:
					cnt = len(os.listdir(SETTINGS.getSetting('pref_slides_path')))
				except:
					cnt = 0
				if  cnt == 0:
					msg1 = u'Verzeichnis für Slideshow nicht gefunden oder leer.'
					msg2 = u'Bitte in den Settings überprüfen / einstellen.'
					MyDialog(msg1, msg2, '')
					return
									
				CWD = SETTINGS.getAddonInfo('path') 					# working dir
				DialogSlides = slides.Slideshow('slides.xml', CWD, 'default')
				DialogSlides.doModal()
				xbmc.Player().stop()					
				del DialogSlides
				PLog("del_DialogSlides")
				return
	else:			
		xbmc.Player().play(url, li, False)						# ohne Slideshow 					

#---------------------------------------------------------------- 
# Aufruf: PlayVideo
# 04.03.2022 Header für ZDF-Url erforderl. (Error "502 Bad Gateway")
# 21.01.2023 dialog optional für add_UHD_Streams (ohne Dialog)
# Rückage url oder False
def url_check(url, caller='', dialog=True):
	PLog('url_check:')

	if url.startswith('http') == False:		# lokale Datei
		if  os.path.exists(url):
			PLog("local_file")
			return url
		else:
			if dialog:
				msg2 = url
				if url == "":
					msg1= 'Video-Url fehlt!'
				else:
					msg1= 'Video fehlt! Datei:'
				MyDialog(msg1, msg2, "")		 			 	 
			return False
	#-----------------------------------------
	# hier bei Bedarf ein SessionTimeout verwenden, Bsp.
	#	blog.apify.com/python-requests-timeout/
	UrlopenTimeout = 2
	# Tests:
	# url='http://104.250.149.122:8012'			# Debug: urlopen error Connection refused
	# url='http://feeds.soundcloud.com/x'		# HTTP Error 405: Method Not Allowed

	header={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}

	page, msg = getRedirect(url, header)			
	if page:
		return page							# ermittelte Url	
	else:
		PLog("url_check_error: " + msg)
		msg1= '%s: Quelle nicht erreichbar - Url:' % caller
		msg2 = url
		msg3 = 'Fehler: %s' % msg
		PLog(msg3)
		if dialog:
			MyDialog(msg1, msg2, msg3)		 			 	 
		return False

#----------------------------------------------------------------
# z.Z. nur genutzt für Settings inputstream.adaptive-Addon
def open_addon(addon_id, cmd):
	PLog('open_addon:')

	if cmd == "openSettings":
		xbmcaddon.Addon(addon_id).openSettings()
	return
	
#----------------------------------------------------------------
# Zeigt bei Livestreams die Abspielposition von inputstream.adaptive 
#	als Zeitangabe
# Aufruf: PlayAudio (direkt, indirekt)
# Player vor Aufruf bereits aktiviert (s. PlayAudio->Player_Subtitles:)
# notification-Aufruf zu ungenau für float-Werte.
# ZDF-Werte beim Start: 
#		Pufferanzeige: Wert1 / Wert2 ->
#			1. 02:59:44 - 02:59:48
#			2. 03:00:00
#		TotalTime: 	10800 = 180 min = 3 Std. (akt. Maximum der Sender)
#		LastSeek: 	10786 = 179 min

# Der Abstand zwischen TotalTime und LastSeek (player.getTime) variiert
#	bei den Livestreams der Sender und schwankt im Verlauf zwischen 0 und 
#	10 (laut Tests).
#
# Warteschleife für Player auf Raspi & Co entfällt hier: bereits erledigt
#	 vor Aufruf ShowSeekPos in PlayVideo (s. showSubtitles).
#	
# Issues:
# 	Unterscheidung Live-/Videostream nicht via Url-Eigenschaften möglich - 
#		LastSeek bei Videos häufig 0, aber s. Sportschaustream
#	Background-Thread für Raspi und für einzelne Streams (LastSeek=0, s.u.)  
#		zwingend erforderlich (ohne Thread endloses Buffern)
#	Sportschaustream ../ardevent2.akamaized.net/hls/live/681512/ardevent2_geo/..
#		Start mit 2-4 absinkend auf Minuswerte
#	ZDF Event 9 (Olympia): Issue hier irrelevant - inputstream scheiter mit
#		"Segment download failed .. with error 404", Stream kommt hier nicht
#		an.
#	ZDF Event-Stream 01 und 02:  inputstream bricht nach Errors (Download failed 
#		with error 404) ab - startet hier mit LastSeek 0 und wird daher für 
#		die Stream-Uhrzeit verworfen. Um den Stream sichtbar zu machen, muss 
#		aber ein Wechsel in die Ansichtsoptionen erfolgen (Estuary, WideList).     
#	Livetreams von wdrlokalzeit.akamaized.net starten mit 1 od. 2 statt TotalTime 
#		und buffern endlos in der isPlaying-Schleife. Bei erzwungendem Seek auf
#		TotalTime blockiert inputstream mit Ladekreis, spielt aber den Stream.
#		Bei einer neueren inputstream-Verson (LibreElec, 20.3.9.1) starten
#		diese Streams korrekt am Pufferende, puffern dann aber in der 
#		waitForAbort-Schleife endlos. Dabei geben sie korrekte play_time- und
#		TotalTime-Werte zurück und verhindern so die Buffering-Erkennung.
#		Gibt man vor der Schleife einige Sek. Sync-Zeit, fallen sie auf 
#		TotalTime 1 od. 2 zurück - praktisch wird ein korrekter Start angetäuscht. 
#		Solche Streams hier beim Aufruf ausschließen (PlayVideo: live="").
#	Allgemeine Problemlage: inputstream hat mit einigen Streams Syncprobleme
#		(Video- und/oder Sound-Streams). Dies kann zu endlosem Bufern führen, 
#		wenn das Addon nach Playerstart Funktionen des Players abfragt (getTime,
#		getTotalTime). Dabei spielen Zeitverzögerungen (time.sleep, xbmx.sleep,
#		waitForAbort) offensichtlich keine Rolle.
#		Lösung: 2 Sync-Checks, einmal auf getTime<3 nach 3 Sek., sowie Test auf
# 			extrem Werte (<0 oder > TotalTime).
#	Infos zu inputstream.adaptive: https://github.com/xbmc/inputstream.adaptive/
#		(s. issues und wiki/Settings), Kodi-Forum zu [VideoPlayer InputStream]: 
#		https://forum.kodi.tv/forumdisplay.php?fid=312.
# 	Bisher keine Tests mit den unterschiedlichen Settings für inputstream -
#		getestet wurde mit den Defaultsettings.
#	Bisher keine ffmpeg-Analyse für Eignung/Nichteignung von Streams
#	monitor.waitForAbort() blockiert - für die while-Schleife sind mind. 1 sec
#		Timeout und "not" erforderlich. Siehe auch Monitoring für Startlist in
#		PlayVideo (keine blokierfreie Schleife für Videoplay gefunden).
# 15.01.2024 isPlaying-Abfrage für Player entfernt

def ShowSeekPos(player, url):							# "Streamuhrzeit"
	PLog('ShowSeekPos: ' + url)		
	import resources.lib.EPG as EPG

	# control-Test:
	#marks="0.00,6.66,6.66,13.2,19.8,19.8,27.4"			# @PvD  14.10.023
	#xbmcgui.Window(10000).setProperty("ardundzdf",marks)# control -> DialogSeekbar.xml
	#PLog(xbmcgui.Window(10000).getProperty("ardundzdf"))# OK
	
	icon=""												# -> Kodi's i-Symbol
	now = EPG.get_unixtime(onlynow=True)				# unix-sec passend zu TotalTime, LastSeek
	date_format = "%Y-%m-%dT%H:%M:%SZ";	
	MinusSeekMax = -10									# detect sync errors
	now_dt = datetime.datetime.fromtimestamp(int(now))
	StartTime = now_dt.strftime("%H:%M:%S")
		
	TotalTime = int(player.getTotalTime())    			# sec, float -> int, max. Puffergröße
	LastSeek = int(player.getTime())           		 	# Basis-Wert für akt. Uhrzeit	
	PLog("StartTime: %s, TotalTime: %d, LastSeek: %d" % (StartTime, TotalTime, LastSeek))
	if not TotalTime or LastSeek <= 3:					# Start am Pufferanfang -> Sync-Problem
		PLog("player_is_off or SyncProblem")
		xbmcgui.Dialog().notification("Stream-Uhrzeit: ", u"hier nicht möglich", icon,3000, sound=True)
		return
	
	# ----------------------------------				# ARD-Stream? -> EPG-Events laden
	
	linkid=""; buf_events=""; KeyListener_run=False
	pos=url.rfind("/"); url=url[:pos]					# Endung index.m3u8 statt master.m3u8 möglich
	ard_streamlinks = Dict("load", "ard_streamlinks")
	# Format ard_streamlinks s. get_ARDstreamlinks,
	# Ard-Sender s. Debuglog (ardline:)
	# hier bei Bedarf noch die ARD-Sender aus IPTV-Quellen ergänzen
	for link in ard_streamlinks.split("\n"):			# Abgleich ARD-Url, Zuordnung linkid
		PLog(link)
		if url in link:
			linkid = link.split("|")[-1]
			title_sender = link.split("|")[0]
			PLog("linkid_found: " + linkid)
			epg_url  = "https://programm-api.ard.de/nownext/api/channel?channel=%s&pastHours=5&futureEvents=1" % linkid
			break
			
	if linkid:											# Sendungsnavigation: ARD-EPG für Zeitstrahl laden
		buf_events, event_end = get_ARD_LiveEPG(epg_url, title_sender, date_format, now, TotalTime)
		event_end = int(event_end)
		txt = u"Liste: #-Taste, Maus-Taste rechts"
		header = "Anzahl Sendungen: %d" % len(buf_events)
		dur=10000
		if len(buf_events) == 0:
			header = u"Sendungen"
			txt = u"KEINE weitere Sendung"
			dur=5000
		xbmcgui.Dialog().notification(header, txt, icon,dur, sound=True)
		KeyListener_run=True
		
	PLog("buf_events: %d" % len(buf_events))	
	# ----------------------------------

	monitor = xbmc.Monitor()
	LastBufTime = StartTime											# detect sync errors direkt
	p_list=[]														# dto. im 3-sec-Rahmen 
	while not monitor.waitForAbort(1):
		show_time=False; syncfail=False
		try:
			play_time = player.getTime()							# akt. Pos im Puffer (0=Pufferstart)
		except:
			play_time=LastSeek
			break													# Livestream beendet
				
		p = int(play_time)
		#PLog("play_time_p: %d, LastSeek: %d" % (p, LastSeek)) 		# Debug
		
		# ----------------------------------						# Sync-Checks
		# sync-Check: Streampos. verharrt am Pufferanfang 
		#	Bsp. kika, phoenix, TSchauXL, wdrlokalzeit
		p_list.append(p)											# 3 sec sync-Check
		
		if len(p_list) >= 3:
			if max(p_list) < 1:										# nach 3 sec ist < 1 ein Sync-Error-Indiz
				PLog("p_list_syncfail: %d, %d" % (p_list[-1], p_list[0]))
				syncfail = True
			p_list=[]			
		
		# sync-Check: extreme Abweichungen
		# Bsp.: Sportschaustream: Start mit 2-4 absinkend auf Minuswerte - s.o.,
		if p < MinusSeekMax or p > TotalTime: # sync error? Bsp. LastSeek QVC: 1271296
			PLog("syncfail_extrem: %d, %d" % (p, TotalTime))
			syncfail = True
			  
		if syncfail:
			PLog("monitor_break_on_syncfail")
			xbmcgui.Dialog().notification("Stream-Uhrzeit: ", u"Sync-Error - Abbruch", icon,3000, sound=True)
			xbmc.sleep(2000)
			break													# verhind. Blockade durch Buffering
		# ----------------------------------
		
		# regelm. Schwankung bei Livestreams 6-10 (empirisch):
		if (LastSeek-p) > 10:										# rückwärts	im Puffer	
				show_time=True
		if p > LastSeek:											# vorwärts im Puffer
			if (p-LastSeek) > 10:	
				show_time=True
		
		if show_time:												# Ausgabe Uhrzeit für die neue Pufferpos.
			pos_sec = TotalTime - p									# je kleiner p desto größer der Zeitabzug
			now = EPG.get_unixtime(onlynow=True)
			time_sec = int(now) - pos_sec							# Pos-Sekunden von akt. Zeit abziehen
			new_dt = datetime.datetime.fromtimestamp(time_sec)
			t_string = new_dt.strftime("%H:%M:%S")
			
			PLog("LastSeek: %d, pos_sec: %d" % (LastSeek, pos_sec))
			PLog("new_t_string: " + t_string)
			
			if LastBufTime != new_dt:								# skip_sync_error
				LastBufTime=new_dt
				xbmcgui.Dialog().notification("Stream-Uhrzeit: ", t_string, icon,3000, sound=False)
			else:
				PLog("skip_sync_error")
				
		LastSeek=p
		
		# ----------------------------------						# Start Event-Auwahl bei ARD-Streams
		new_event=""
		if buf_events and KeyListener_run:
			now = int(EPG.get_unixtime(onlynow=True))
			PLog("now: %d, event_end: %d, dif: %d" % (now, event_end, event_end-now))
			if event_end < now:										# Events nachladen
				PLog("load_events: diff now - event_end: %d" % (now - event_end))
				buf_events, event_end = get_ARD_LiveEPG(epg_url, title_sender, date_format, now, TotalTime)
				event_end = int(event_end)
				
			key = KeyListener.record_key()							# pressed_key: string
			PLog("key: " + str(key))								# ev. pausieren mit Blank?
			if key == "61475" or key == "61467" or key == "61448":	# Taste #, r. Maustaste, Taste Back
				line=""												# Liste Events im Zeitpuffer	
				if len(buf_events) == 0:							# keine Events (mehr)
					xbmcgui.Dialog().notification("Zeitpuffer", "ohne weitere Sendung", icon,3000, sound=True)
					KeyListener_run=False							# Stop bis Streamende, kein re-init
					PLog("KeyListener_stopped")
					continue
				
				buf_events = sorted(buf_events, reverse=True)
				show_list=[]; 										# Liste ohne timestamp
				for item in buf_events:
					event_start, title, sD_uhr = item.split("|")
					show_list.append("%s | %s" % (sD_uhr, title))
				
				heading = "Sendungen im Zeitpuffer | Auswahl"
				ret = xbmcgui.Dialog().select(heading, show_list, preselect=0) # Dialog
				if ret >= 0:										# Auswahl?
					new_event = buf_events[ret]
					event_start = int(new_event.split("|")[0])
					new_event_line = show_list[ret]
						
					new_dt = datetime.datetime.fromtimestamp(event_start)
					t_string = new_dt.strftime("%H:%M:%S")
					PLog("new_event: %s | %d" % (t_string, event_start))# Start gewählter Event (unix-sec)
					PLog("new_event_line: %s" % new_event_line)		# gewählter Event

					# neue Seek-Position mit 6 sec-Schwankungszuschlag (s.o.)
					diff_event = now - event_start					# akt. Differenz zum Event (unix-sec)
					new_pos_sec = TotalTime - diff_event - 6		# -> Pos. im Zeitpuffer (0 bis TotalTime)
					PLog("diff_event: %d, new_pos_sec: %d" % (diff_event, new_pos_sec))
					
					sD_uhr, title = new_event_line.split("|") 
					player.seekTime(new_pos_sec)
					xbmcgui.Dialog().notification("Sendezeit: %s" % sD_uhr, title, icon,6000, sound=True)
							
		else:
			PLog("monitor_ShowSeekPos_stop")
			break
				
	return
#----------------------------------------------------------------
# KeyListener (ähnlich slides.py) für ShowSeekPos
#	Problem: alle Dialogvarianten blinken im Takt des Timeouts - 
#		self.getControl(401).setVisible(False) bleibt ohne Effekt
# 	Daher Verwendung von Pointer.xml  (Mauszeiger) - belegt eine kleine
#	Fläche i.d. linken oberen Ecke (statt DialogNotification.xml)	
# 14.1.2023 ohne Timer (Aufruf sekündlich durch ShowSeekPos) 
#
class KeyListener(xbmcgui.WindowXMLDialog):
	PLog("KeyListener: loaded")
	ACTION_MOUSE_LEFT_CLICK = 100
	ACTION_MOUSE_RIGHT_CLICK = 101

	def __new__(cls):
		try: 
			return super(KeyListener, cls).__new__(cls, "Pointer.xml", "")	# Mauszeiger
		except:
			PLog("NOTICE: KeyListener not found!")

	def __init__(self):
		self.key     = 0

	def onInit(self):
		try:
			self.getControl(1).setVisible(False)	 	# o. Wirkung (1=Pointer)
			self.getControl(1).setPosition(-100, -100)  # o. Wirkung
		except:
			PLog("NOTICE: Control_set_error!")

	def onAction(self, action):
		actionId = action.getId() 
		if actionId == self.ACTION_MOUSE_RIGHT_CLICK:
			self.key = "61467"							# hier für rechte Maustaste 
		else:		
			code = action.getButtonCode()
			PLog("code: " + str(code))					# Debug
			self.key = None if code == 0 else str(code)
			
		self.close()

	@staticmethod
	def record_key():
		dialog  = KeyListener()
		dialog.doModal()
		key = dialog.key
		del dialog
		return key
 
#----------------------------------------------------------------
# Aufrufer ShowSeekPos: zum Streamstart und jeweils zum Sendungsende
#	der letzten Sendung (vorher keine neuen Daten verfügbar). 
# 16.06.2024 +02:00 in datetime-Format für Sommerzeit statt 00Z,
#	s.u. date_format_adapted
#	
def get_ARD_LiveEPG(epg_url, title_sender, date_format, now, TotalTime):
	PLog("get_ARD_LiveEPG: " + title_sender)
	
	now=int(now); TotalTime=int(TotalTime)
	page, msg = get_page(path=epg_url)
	if page:
		epg = json.loads(page)
		epg_events = epg["events"]
		sD = epg_events[-1]["endDate"]			# Sendungsende letzter Event: Nachladetrigger
		PLog("sD: " + sD)
		if sD[-6] == "+":						# Sommerzeit enthalten 2024-06-16T12:45:00+02:00 
			PLog("date_format: " + date_format)	# Anpassung für %Y-%m-%dT%H:%M:%SZ
			date_format = "%Y-%m-%dT%H:%M:%S%z"
			PLog("date_format_adapted: " + date_format)		
			
		sD_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(sD, date_format)))
		event_end = time.mktime(sD_time.timetuple())
	else:
		PLog("epg_events_error: " + title_sender)
		xbmcgui.Dialog().notification("EPG-Events: ", u"Fehler für %s" % title_sender, icon,3000, sound=True)
	PLog("epg_events: %d, event_end: %d" % (len(epg_events), event_end))
	if len(epg_events) <= 1:					# Event-Liste nur mit mehr als 1 (aktuelle) Sendung 
		return [], 0							# return buf_events=[], event_end=0

	buf_events=[]; event_end=0
	for event in epg_events:					# events passend zum Zeitpuffer filtern
		stitle = event["title"]["short"]
		if "currentStartDate" in event:			# kann in future-events fehlen
			sD = event["currentStartDate"]		# kann leicht abweichen von startDate
		else:
			sD = event["startDate"]
		sD_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(sD, date_format)))
		event_start = time.mktime(sD_time.timetuple())
		
		if sD[-6] =="+":						# Sommerzeit bereits enthalten, s.o. 
			add_hour = 0
		else:
			add_hour = time_translate(sD, add_hour=True, day_warn=False, add_hour_only=True)
			if add_hour != sD:							# timecode bei exception
				add_hour = add_hour * 3600				# 2*3600
				event_start = event_start + add_hour 	# + 2 Std. bei Sommerzeit
							
		PLog("event_start: %s, %d, added: %d" % (str(sD), event_start, add_hour))
		BufStart = now - TotalTime					# akt. Pufferstart (unix-sec)
		PLog("BufStart: %d, now: %d, TotalTime: %d" % (BufStart, now, TotalTime))
		if event_start > BufStart and event_start < now:
			sD_uhr = datetime.datetime.fromtimestamp(event_start).strftime('%H:%M:%S')
			PLog("add_event: %d | %s | %s" % (event_start, sD_uhr, stitle))
			line = "%d|%s|%s" % (event_start, stitle, sD_uhr)	# 1696296600|Tagesschau|20:00:00
			buf_events.append(line)		
		
	return buf_events, event_end
#----------------------------------------------------------------





















