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
#	Stand '27.02.2020'

# Python3-Kompatibilität:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

# Standard:
import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:					
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve 
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse , urlsplit, parse_qs 
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	
# import requests		# kein Python-built-in-Modul, urllib2 verwenden
import datetime as dt	# für xml2srt
import time, datetime
from time import sleep  # PlayVideo

import glob, shutil
from io import BytesIO	# Python2+3 -> get_page (compressed Content), Ersatz für StringIO
import gzip, zipfile
import base64 			# url-Kodierung für Kontextmenüs
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import string, textwrap
	
# Globals
PYTHON2 = sys.version_info.major == 2	# Stammhalter Pythonversion 
PYTHON3 = sys.version_info.major == 3

NAME			= 'ARD und ZDF'
KODI_VERSION 	= xbmc.getInfoLabel('System.BuildVersion')

ADDON    		= xbmcaddon.Addon()
ADDON_ID      	= ADDON.getAddonInfo('id')	# plugin.video.ardundzdf
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

ARDStartCacheTime = 300						# 5 Min.	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA
WATCHFILE		= os.path.join("%s/merkliste.xml") % ADDON_DATA
TEMP_ADDON		= xbmc.translatePath("special://temp")			# Backups

PLAYLIST 		= 'livesenderTV.xml'		# TV-Sender-Logos erstellt von: Arauco (Plex-Forum). 											
ICON_MAIN_POD	= 'radio-podcasts.png'
ICON_MAIN_AUDIO	= 'ard-audiothek.png'
ICON_MAIN_ZDFMOBILE	= 'zdf-mobile.png'
ICON_PHOENIX	= 'phoenix.png'			

# Github-Icons zum Nachladen aus Platzgründen
ICON_MAINXL 	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/TagesschauXL/tagesschau.png?raw=true'
BASE_URL 		= 'https://classic.ardmediathek.de'

#----------------------------------------------------------------  
def PLog(msg, loglevel=xbmc.LOGDEBUG):
	if DEBUG == 'false':
		return
	#if isinstance(msg, str):		# entf. mit six
	#	msg = msg.encode('utf-8')
		
	loglevel = xbmc.LOGNOTICE
	# PLog('loglevel: ' + str(loglevel))
	if loglevel >= 2:
		xbmc.log("%s --> %s" % ('ARDundZDF', msg), level=loglevel)
#---------------------------------------------------------------- 

# Home-Button, Aufruf: item = home(item=item, ID=NAME)
#	Liste item von Aufrufer erzeugt
def home(li, ID):												
	PLog('home: ' + ID)	
	if SETTINGS.getSetting('pref_nohome') == 'true':	# keine Homebuttons
		return li
		
	title = u'Zurück zum Hauptmenü %s' % ID
	summary = title
	
	CurSender = Dict("load", 'CurSender')		
	PLog(CurSender)	

	if ID == NAME:		# 'ARD und ZDF'
		name = 'Home : ' + NAME
		fparams="&fparams={}"
		addDir(li=li, label=name, action="dirList", dirID="Main", fanart=R('home.png'), 
			thumb=R('home.png'), fparams=fparams)
			
	if ID == 'ARD':
		if SETTINGS.getSetting('pref_use_classic') == 'false':	# Umlabeln ür ARD-Suche (Classic)
			ID ='ARD Neu'
					
	if ID == 'ARD':
		name = 'Home: ' + "ARD Mediathek Classic"
		# CurSender = Dict("load", "CurSender")	# entf.  bei Classic
		fparams="&fparams={'name': '%s', 'sender': '%s'}"	% (quote(name), '')
		addDir(li=li, label=title, action="dirList", dirID="Main_ARD", fanart=R('home-ard-classic.png'), 
			thumb=R('home-ard-classic.png'), fparams=fparams)
		
	if ID == 'ARD Neu':
		name = 'Home: ' + "ARD Mediathek"
		CurSender = Dict("load", "CurSender")
		fparams="&fparams={'name': '%s', 'CurSender': '%s'}"	% (quote(name), quote(CurSender))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", 
			fanart=R('home-ard.png'), thumb=R('home-ard.png'), fparams=fparams)
			
	if ID == 'ZDF':
		name = 'Home: ' + "ZDF Mediathek"
		fparams="&fparams={'name': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="Main_ZDF", fanart=R('home-zdf.png'), 
			thumb=R('home-zdf.png'), fparams=fparams)
		
	if ID == 'ZDFmobile':
		name = 'Home :' + "ZDFmobile"
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.Main_ZDFmobile", 
			fanart=R(ICON_MAIN_ZDFMOBILE), thumb=R(ICON_MAIN_ZDFMOBILE), fparams=fparams)
			
	if ID == 'PODCAST':
		name = 'Home :' + "Radio-Podcasts"
		fparams="&fparams={'name': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="Main_POD", fanart=R(ICON_MAIN_POD), 
			thumb=R(ICON_MAIN_POD), fparams=fparams)
			
	if ID == 'ARD Audiothek':
		name = 'Home :' + "ARD Audiothek"
		fparams="&fparams={'title': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="AudioStart", fanart=R(ICON_MAIN_AUDIO), 
			thumb=R(ICON_MAIN_AUDIO), fparams=fparams)
			
	if ID == '3Sat':
		name = 'Home :' + "3Sat"
		fparams="&fparams={'name': '%s'}" % quote(name)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Main_3Sat", fanart=R('3sat.png'), 
			thumb=R('3sat.png'), fparams=fparams)
			
	if ID == 'FUNK':
		name = 'Home :' + "FUNK"
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Main_funk", fanart=R('funk.png'), 
			thumb=R('funk.png'), fparams=fparams)
			
	if ID == 'Kinderprogramme':
		name = 'Home :' + ID
		thumb = R('childs.png')
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Main_childs", fanart=thumb, 
			thumb=thumb, fparams=fparams)

	if ID == 'TagesschauXL':
		name = 'Home :' + ID
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.TagesschauXL.Main_XL", fanart=ICON_MAINXL, 
			thumb=ICON_MAINXL, fparams=fparams)
			
	if ID == 'phoenix':
		name = 'Home :' + ID
		thumb = R(ICON_PHOENIX)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Main_phoenix", fanart=thumb, 
			thumb=thumb, fparams=fparams)

	return li
	 
#---------------------------------------------------------------- 
#   data-Verzeichnis liegt 2 Ebenen zu hoch, funktioniert aber.
#	03.04.2019 data-Verzeichnis des Addons:
#  		Check /Initialisierung / Migration
# 	27.05.2019 nur noch Check (s. Forum:
#		www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?pageNo=23#post528768
#	Die Funktion checkt bei jedem Aufruf des Addons data-Verzeichnis einschl. Unterverzeichnisse 
#		auf Existenz und bei Bedarf neu an. User-Info nur noch bei Fehlern (Anzeige beschnittener 
#		Verzeichnispfade im Kodi-Dialog nur verwirend).
#	 
def check_DataStores():
	PLog('check_DataStores:')
	store_Dirs = ["Dict", "slides", "subtitles", "Inhaltstexte", 
				"merkliste", "m3u8"]
				
	# Check 
	#	falls ein Unterverz. fehlt, erzeugt make_newDataDir alle
	#	Datenverz. oder einzelne fehlende Verz. neu.
	ok=True	
	for Dir in store_Dirs:						# Check Unterverzeichnisse
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)
		if os.path.isdir(Dir_path) == False:	
			PLog('Datenverzeichnis fehlt: %s' % Dir_path)
			ok = False
			break
	
	if ok:
		return 'OK %s '	% ADDON_DATA			# Verz. existiert - OK
	else:
		# neues leeres Verz. mit Unterverz. anlegen / einzelnes fehlendes 
		#	Unterverz. anlegen 
		ret = make_newDataDir(store_Dirs)	
		if ret == True:						# ohne Dialog
			msg1 = 'Datenverzeichnis angelegt - Details siehe Log'
			msg2=''; msg3=''
			PLog(msg1)
			# xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)  # OK ohne User-Info
			return 	'OK - %s' % msg1
		else:
			msg1 = "Fehler beim Anlegen des Datenverzeichnisses:" 
			msg2 = ret
			msg3 = 'Bitte Kontakt zum Entwickler aufnehmen'
			PLog("%s\n%s" % (msg2, msg3))	# Ausgabe msg1 als exception in make_newDataDir
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return 	'Fehler: Datenverzeichnis konnte nicht angelegt werden'
				
#---------------------------
# ab Version 1.5.6
# 	erzeugt neues leeres Datenverzeichnis oder fehlende Unterverzeichnisse
def  make_newDataDir(store_Dirs):
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
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)	
		if os.path.isdir(Dir_path) == False:	
			try:  
				os.mkdir(Dir_path)
			except Exception as exception:
				ok=False
				PLog(str(exception))
				break
	if ok:
		return True
	else:
		return str(exception)
		
#---------------------------
# sichert Verz. für check_DataStores
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
#   Bsp. für CacheTime: 5*60 (5min) - Verwendung bei "load", Prüfung mtime 
#	ev. ergänzen: OS-Verträglichkeit des Dateinamens

def Dict(mode, Dict_name='', value='', CacheTime=None):
	PLog('Dict: ' + mode)
	PLog('Dict: ' + str(Dict_name))
	PLog('Dict: ' + str(type(value)))
	dictfile = "%s/%s" % (DICTSTORE, Dict_name)
	PLog("dictfile: " + dictfile)
	
	if mode == 'store':	
		with open(dictfile, 'wb') as f: pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
		f.close
		return True
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
		if os.path.exists(dictfile) == False:
			PLog('Dict: %s nicht gefunden' % dictfile)
			return False
		if CacheTime:
			mtime = os.path.getmtime(dictfile)	# modified-time
			now	= time.time()
			CacheLimit = now - CacheTime		# 
			# PLog("now %d, mtime %d, CacheLimit: %d" % (now, mtime, CacheLimit))
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
# Dateien löschen älter als seconds
#		directory 	= os.path.join(path)
#		seconds		= int (1 Tag=86400, 1 Std.=3600)
# leere Ordner werden entfernt
def ClearUp(directory, seconds):	
	PLog('ClearUp: %s, sec: %s' % (directory, seconds))	
	PLog('älter als: ' + seconds_translate(seconds, days=True))
	now = time.time()
	cnt_files=0; cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 
		PLog("ClearUp: globFiles " + str(len(files)))
		# PLog(" globFiles: " + str(files))
		for f in files:
			#PLog(os.stat(f).st_mtime)
			#PLog(now - seconds)
			if os.stat(f).st_mtime < (now - seconds):
				if os.path.isfile(f):	
					PLog('entfernte Datei: ' + f)
					os.remove(f)
					cnt_files = cnt_files + 1
				if os.path.isdir(f):		# Verz. ohne Leertest entf.
					PLog('entferntes Verz.: ' + f)
					shutil.rmtree(f, ignore_errors=True)
					cnt_dirs = cnt_dirs + 1
		PLog("ClearUp: entfernte Dateien %s, entfernte Ordner %s" % (str(cnt_files), str(cnt_dirs)))	
		return True
	except Exception as exception:	
		PLog(str(exception))
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
		
# def BytesToUnicode(line) - ersetzt durch py2_decode
	
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
#	

def addDir(li, label, action, dirID, fanart, thumb, fparams, summary='', tagline='', mediatype='', cmenu=True):
	PLog('addDir:')
	PLog(type(label))
	label=py2_encode(label)
	PLog('addDir - label: {0}, action: {1}, dirID: {2}'.format(label, action, dirID))
	PLog(type(summary)); PLog(type(tagline));
	summary=py2_encode(summary); tagline=py2_encode(tagline); 
	fparams=py2_encode(fparams); fanart=py2_encode(fanart); thumb=py2_encode(thumb);
	PLog('addDir - summary: {0}, tagline: {1}, mediatype: {2}, cmenu: {3}'.format(summary, tagline, mediatype, cmenu))
		
	li.setLabel(label)			# Kodi Benutzeroberfläche: Arial-basiert für arabic-Font erf.
	# PLog('summary, tagline: {0}, {1}'.format(summary, tagline))
	Plot = ''
	if tagline:								
		Plot = tagline
	if summary:	
		Plot = Plot +"\n\n" + summary
		
	if mediatype == 'video': 	# "video", "music" setzen: List- statt Dir-Symbol
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot, "mediatype": "video"})	
		isFolder = False		# nicht bei direktem Player-Aufruf - OK mit setResolvedUrl
		li.setProperty('IsPlayable', 'true')					
	else:
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot})	
		li.setProperty('IsPlayable', 'false')
		isFolder = True	
	
	li.setArt({'thumb':thumb, 'icon':thumb, 'fanart':fanart})
	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	PLog('PLUGIN_URL: ' + PLUGIN_URL)	# plugin://plugin.video.ardundzdf/
	PLog('HANDLE: %s' % HANDLE)
	
	PLog(fparams)
	if thumb == None:
		thumb = ''
	url = PLUGIN_URL+"?action="+action+"&dirID="+dirID+"&fanart="+fanart+"&thumb="+thumb+quote(fparams)
	PLog("addDir_url: " + unquote(url))		
	
	if SETTINGS.getSetting('pref_watchlist') ==  'true':	# Merkliste verwenden 
		if cmenu:											# Kontextmenüs Merkliste hinzufügen
			Plot = Plot.replace('\n', '||')		# || Code für LF (\n scheitert in router)
			# PLog('Plot: ' + Plot)
			fp = {'action': 'add', 'name': quote_plus(label),'thumb': quote_plus(thumb),\
				'Plot': quote_plus(Plot),'url': quote_plus(url)}	
			fparams_add = "&fparams={0}".format(fp)
			PLog("fparams_add: " + fparams_add)
			fparams_add = quote_plus(fparams_add)

			fp = {'action': 'del', 'name': quote_plus(label)}	# name reicht für del
			fparams_del = "&fparams={0}".format(fp)
			PLog("fparams_del: " + fparams_del)
			fparams_del = quote_plus(fparams_del)	

			# Script: This behaviour will be removed - siehe https://forum.kodi.tv/showthread.php?tid=283014
			MERK_SCRIPT=xbmc.translatePath('special://home/addons/%s/resources/lib/merkliste.py' % (ADDON_ID) )
			li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MERK_SCRIPT, HANDLE, fparams_add)),
				 ('Aus Merkliste entfernen', 'RunScript(%s, %s, ?action=dirList&dirID=Watch%s)' \
					% (MERK_SCRIPT, HANDLE, fparams_del))])
		else:
			pass											# Kontextmenü entfernen klappt so nicht
			#li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunAddon(%s, ?action=dirList&dirID=dummy)' \
			#	% (ADDON_ID))], replaceItems=True)
		
	xbmcplugin.addDirectoryItem(handle=HANDLE,url=url,listitem=li,isFolder=isFolder)
	
	PLog('addDir_End')		
	return	

#---------------------------------------------------------------- 
# holt kontrolliert raw-Content, cTimeout für cacheTime
# 02.09.2018	erweitert um 2. Alternative mit urllib2.Request +  ssl.SSLContext
#	Bei Bedarf get_page in EPG-Modul nachrüsten.
#	s.a. loadPage in Modul zdfmobile.
# 11.10.2018 HTTP.Request (Plex) ersetzt durch urllib2.Request
# 	03.11.2018 requests-call vorangestellt wg. Kodi-Problem: 
#	bei urllib2.Requests manchmal errno(0) (https) - Verwend. installierter Zertifikate erfolglos
# 07.11.2018 erweitert um Header-Anfrage GetOnlyRedirect zur Auswertung von Redirects (http error 302).
# Format header dict im String: "{'key': 'value'}" - Bsp. Search(), get_formitaeten()
# 23.12.2018 requests-call vorübergehend auskommentiert, da kein Python-built-in-Modul (bemerkt beim 
#	Test in Windows7
# 13.01.2019 erweitert für compressed-content (get_page2)
# 25.01.2019 Hinweis auf Redirects (get_page2)
#
def get_page(path, header='', cTimeout=None, JsonPage=False, GetOnlyRedirect=False):	
	PLog('get_page:'); PLog("path: " + path); PLog("JsonPage: " + str(JsonPage)); 

	if header:									# dict auspacken
		header = unquote(header);  
		header = header.replace("'", "\"")		# json.loads-kompatible string-Rahmen
		header = json.loads(header)
		PLog("header: " + str(header)[:80]);

	path = transl_umlaute(path)					# Umlaute z.B. in Podcast "Bäckerei Fleischmann"
	# path = unquote(path)						# scheitert bei quotierten Umlauten, Ersatz replace				
	path = path.replace('https%3A//','https://')# z.B. https%3A//classic.ardmediathek.de
	msg = ''; page = ''	
	UrlopenTimeout = 10
	
	'''
	try:
		import requests															# 1. Versuch mit requests
		PLog("get_page1:")
		...
	'''
	
	if page == '':
		try:															# 2. Versuch ohne SSLContext 
			PLog("get_page2:")
			if GetOnlyRedirect:						# nur Redirect anfordern
				# Alt. hier : new_url = r.geturl()
				# bei Bedarf HttpLib2 mit follow_all_redirects=True verwenden
				PLog('GetOnlyRedirect: ' + str(GetOnlyRedirect))
				r = urlopen(path)
				page = r.geturl()
				PLog(page)			# Url
				return page, msg					

			if header:
				req = Request(path, headers=header)	
			else:
				req = Request(path)
								
			r = urlopen(req)	
			new_url = r.geturl()											# follow redirects
			PLog("new_url: " + new_url)
			# PLog("headers: " + str(r.headers))
			
			compressed = r.info().get('Content-Encoding') == 'gzip'
			PLog("compressed: " + str(compressed))
			page = r.read()
			PLog(len(page))
			if compressed:
				buf = BytesIO(page)
				f = gzip.GzipFile(fileobj=buf)
				page = f.read()
				PLog(len(page))
			r.close()
			PLog(page[:100])
		except URLError as exception:
			msg = str(exception)
			PLog(msg)
				
	
	if page == '':
		import ssl
		try:
			PLog("get_page3:")											# 3. Versuch mit SSLContext
			if header:
				req = Request(path, headers=header)	
			else:
				req = Request(path)														
			# gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
			gcontext = ssl.create_default_context()
			gcontext.check_hostname = False
			# gcontext.verify_mode = ssl.CERT_REQUIRED
			r = urlopen(req, context=gcontext, timeout=UrlopenTimeout)
			# r = urllib2.urlopen(req)
			# PLog("headers: " + str(r.headers))
			page = r.read()
			PLog('Mark3')
			r.close()
			PLog(len(page))
		except URLError as exception:
			msg = str(exception)
			PLog(msg)						
			
	if page == '':
		# error_txt = 'Seite nicht erreichbar oder nicht mehr vorhanden'
		error_txt = msg
		if 'classic.ardmediathek.de' in path:
			msg1 = 'Die ARD-Classic-Mediathek ist vermutlich nicht mehr verfügbar.'	
			msg2 = 'Bitte in den Einstellungen abschalten, um das Modul'
			msg3 = 'ARD-Neu zu aktivieren.'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)		 			 	 
		msg = error_txt + ' | %s' % msg
		PLog(msg)
		return page, msg
		
	if page:				
		page = page.decode('utf-8')	
	if JsonPage:
		PLog('json_load: ' + str(JsonPage))
		PLog(len(page))
		page = page.replace('\\/', '/')									# für Python3 erf.
		try:
			request = json.loads(page)
			# 23.11.2019: Blank hinter separator : entfernt - wird in Python nicht beachtet.
			#	Auswirkung in get_formitaeten (extract videodat_url)
			request = json.dumps(request, sort_keys=True, indent=2, separators=(',', ':'))  # sortierte Ausgabe
			page = (page.replace('" : "', '":"').replace('" :', '":'))	# für Python3 erf.
			PLog("jsonpage: " + page[:100]);
		except Exception as exception:
			msg = str(exception)
			PLog(msg)

	return page, msg	
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
		img_alt = UtfToStr(img_alt)
		PLog('img_urlScheme: ' + img_alt[0:40])
		return img_src, img_alt
	else:
		PLog('img_urlScheme: leer')
		return '', ''		
	
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
			fname = "%s/resources/%s" % (ADDON_NAME, fname)
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
			with open(path,'r', encoding="utf8") as f:
				page = f.read()		
	except Exception as exception:
		PLog(str(exception))
		page = ''
	return page
#----------------------------------------------------------------
# Gegenstück zu RLoad - speichert Inhalt page in Datei fname im  
#	Dateisystem. PluginAbsPath muss in fname enthalten sein,
#	falls im Pluginverz. gespeichert werden soll 
#  Migration Python3: immer utf8
# 
def RSave(fname, page, withcodec=False): 
	PLog('RSave: %s' % str(fname))
	PLog(withcodec)
	path = os.path.join(fname) # abs. Pfad
	msg = ''					# Rückgabe leer falls OK
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
			with open(path,'w', encoding="utf8") as f:
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
#	doppelte utf-8-Enkodierung führt an manchen Stellen zu Sonderzeichen
#  	14.04.2019 entfernt: (':', ' ')
# 	todo: decode('utf-8') hier  wie unescape ff.
def repl_json_chars(line):	# für json.loads (z.B.. in router) json-Zeichen in line entfernen
	line_ret = line
	#PLog(type(line_ret))
	for r in	((u'"', u''), (u'\\', u''), (u'\'', u'')
		, (u'&', u'und'), ('(u', u'<'), (u'(', u'<'),  (u')', u'>'), (u'∙', u'|')
		, (u'„', u'>'), (u'“', u'<'), (u'”', u'>'),(u'°', u' Grad')
		, (u'\r', u''), (u'#', u'*')):			
		line_ret = line_ret.replace(*r)
	
	return line_ret
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
# mytype: 	0 : ShowAndGetDirectory, 1 : ShowAndGetFile, 2
# mask: 	nicht brauchbar bei endungslosen Dateien, Bsp. curl
def DirectoryNavigator(settingKey, mytype, heading, shares='files', useThumbs=False, \
	treatAsFolder=False, path=''):
	PLog('DirectoryNavigator:')
	PLog(settingKey); PLog(mytype); PLog(heading); PLog(path);
	
	dialog = xbmcgui.Dialog()
	d_ret = dialog.browseSingle(int(mytype), heading, shares, '', False, False, path)	
	PLog('d_ret: ' + d_ret)
	
	SETTINGS.setSetting(settingKey, d_ret)	
	return 
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
def blockextract(blockmark, mString):  	# extrahiert Blöcke begrenzt durch blockmark aus mString
	#	blockmark bleibt Bestandteil der Rückgabe - im Unterschied zu split()
	#	Rückgabe in Liste. Letzter Block reicht bis Ende mString (undefinierte Länge),
	#		Variante mit definierter Länge siehe Plex-Plugin-TagesschauXL (extra Parameter blockendmark)
	#	Verwendung, wenn xpath nicht funktioniert (Bsp. Tabelle EPG-Daten www.dw.com/de/media-center/live-tv/s-100817)
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
	
		block = mString[pos1:pos2]	# extrahieren einschl.  1. blockmark
		rlist.append(block)
		# reststring bilden:
		mString = mString[pos2:]	# Rest von mString, Block entfernt	
	return rlist  
#----------------------------------------------------------------  
def teilstring(zeile, startmarker, endmarker):  		# rfind: endmarker=letzte Fundstelle, return '' bei Fehlschlag
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
		if bold:
			rString= u"%s[COLOR %s][B]%s[/B][/COLOR]%s"	% (s1, color, ms, s2)
		else:
			rString= u"%s[COLOR %s]%s[/COLOR]%s"	% (s1, color, ms, s2)
		return rString
	else:
		return mString		# Markierung fehlt, mString unverändert zurück
#----------------------------------------------------------------  
# Migration PY2/PY3: py2_decode aus kodi-six
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	# PLog(type(line))
	cleantext = py2_decode(line)
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#----------------------------------------------------------------  	
# Migration PY2/PY3: py2_decode aus kodi-six
def decode_url(line):	# in URL kodierte Umlaute und & wandeln, Bsp. f%C3%BCr -> für, 	&amp; -> &
	line = py2_decode(line)
	unquote(line)
	line = line.replace(u'&amp;', u'&')
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
		, (u"&#39;", u"'"), (u"&#039;", u"'"), (u"&quot;", u'"'), (u"&#x27;", u"'")
		, (u"&ouml;", u"ö"), (u"&auml;", u"ä"), (u"&uuml;", u"ü"), (u"&szlig;", u"ß")
		, (u"&Ouml;", u"Ö"), (u"&Auml;", u"Ä"), (u"&Uuml;", u"Ü"), (u"&apos;", u"'")
		, (u"&nbsp;|&nbsp;", u""), (u"&nbsp;", u" "), (u"&bdquo;", u""), (u"&ldquo;", u""),
		# Spezialfälle:
		#	https://stackoverflow.com/questions/20329896/python-2-7-character-u2013
		#	"sächsischer Genetiv", Bsp. Scott's
		#	Carriage Return (Cr)
		(u"–", u"-"), (u"&#x27;", u"'"), (u"&#xD;", u""), (u"\xc2\xb7", u"-"),
		(u'undoacute;', u'o'), (u'&eacute;', u'e'), (u'&egrave;', u'e'),
		(u'&atilde;', u'a'), (u'quot;', u' '), (u'&#10;', u'\n'),
		(u'&#8222;', u' '), (u'&#8220;', u' '), (u'&#034;', u' ')):
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
# Migration PY2/PY3: py2_decode aus kodi-six
def make_filenames(title, max_length=255):
	PLog('make_filenames:')
	# erzeugt - hoffentlich - sichere Dateinamen (ohne Extension)
	# zugeschnitten auf Titelerzeugung in meinen Plugins 
	
	title = py2_decode(title)
	fname = transl_umlaute(title)		# Umlaute	
	
	valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
	fname = ''.join(c for c in fname if c in valid_chars)
	fname = fname.replace(u' ', u'_')
	return fname[:max_length]
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
	# Recherche Bsp.: https://www.compart.com/de/unicode/U+00BA
	# 
	line=py2_decode(line)
	#PLog(line)
	for r in ((u'\\u00E4', u"ä"), (u'\\u00C4', u"Ä"), (u'\\u00F6', u"ö"), (u'u002F', u"/")		
		, (u'\\u00C6', u"Ö"), (u'\\u00D6', u"Ö"),(u'\\u00FC', u"ü"), (u'\\u00DC', u'Ü')
		, (u'\\u00DF', u'ß'), (u'\\u0026', u'&'), (u'\\u00AB', u'"')
		, (u'\\u00BB', u'"')
		, (u'\xc3\xa2', u'*')			# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2
		, (u'u00B0', u' Grad')		# u00BA -> Grad (3Sat, 37 Grad)	
		, (u'u00EA', u'e')			# 3Sat: Fête 
		, (u'u00E9', u'e')			# 3Sat: Fabergé
		, (u'u00E6', u'ae')):			# 3Sat: Kjaerstad

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
def CalculateDuration(timecode):				# 3 verschiedene Formate (s.u.)
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
					
	if len(timecode) == 9:						# Formate: '00:30 min'	
		d = re.search('([0-9]{1,2}):([0-9]{1,2}) MIN', timecode)	# 2. Format: '00:30 min' 	
		if(None != d):
			hours = int( d.group(1) )
			minutes = int( d.group(2) )
			Log(minutes)
						
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
#		oder:		0h, 0d				
def seconds_translate(seconds, days=False):
	#PLog('seconds_translate:')
	#PLog(seconds)
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
		return  "%d:%02d" % (hour, minutes)		
#----------------------------------------------------------------  	
# Format timecode 	2018-11-28T23:00:00Z (ARDNew, broadcastedOn)
#					y-m-dTh:m:sZ 	ISO8601 date
# Rückgabe:			28.11.2018, 23:00 Uhr   (Sekunden entfallen)
#					bzw. '' bei Fehlschlag
# funktioniert in Kodi nur 1 x nach Neustart - s. transl_pubDate
# 26.08.2019 OK mit Lösung von BJ1 aus
#		https://www.kodinerds.net/index.php/Thread/50284-Python-Problem-mit-strptime/?postID=284746#post284746
#
# stackoverflow.com/questions/214777/how-do-you-convert-yyyy-mm-ddthhmmss-000z-time-format-to-mm-dd-yyyy-time-format
# stackoverflow.com/questions/7999935/python-datetime-to-string-without-microsecond-component
# stackoverflow.com/questions/13685201/how-to-add-hours-to-current-time-in-python
#
# ARD-Zeit + 2 Stunden
# s.a. addHour (ARDnew) - Stringroutine für ARDVerpasstContent
# Rückgabe timecode im Fehlerfall
#
def time_translate(timecode, add_hour=2):
	PLog("time_translate: " + timecode)

	if timecode.strip() == '':
		return ''
		
	# Bsp.: Funk: 			2019-09-30T12:59:27.000+0000,
	# 		ARDNew Live: 	2019-12-12T06:16:04.413Z
	if timecode.find('.') == 19:			# Zielformat 2018-11-28T23:00:00Z			
		timecode = timecode.split('.')[0]
		timecode = timecode + "Z"
	PLog(timecode)
	
	if timecode[10] == 'T' and timecode[-1] == 'Z':  # Format OK?
		try:
			date_format = "%Y-%m-%dT%H:%M:%SZ"
			# ts = datetime.strptime(timecode, date_format)  # None beim 2. Durchlauf       
			ts = datetime.datetime.fromtimestamp(time.mktime(time.strptime(timecode, date_format)))
			PLog(ts)
			new_ts = ts + datetime.timedelta(hours=add_hour)	
			ret_ts = new_ts.strftime("%d.%m.%Y %H:%M")
			return ret_ts
		except Exception as exception:
			PLog(str(exception))
			return timecode
	else:
		return timecode
		
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
def get_keyboard_input():
	kb = xbmc.Keyboard('', 'Bitte Suchwort(e) eingeben')
	kb.doModal() # Onscreen keyboard
	if kb.isConfirmed() == False:
		return ""
	inp = kb.getText() # User Eingabe
	return inp	
#----------------------------------------------------------------  
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
#----------------------------------------------------------------  
# simpler XML-SRT-Konverter für ARD-Untertitel
#	pathname = os.path.abspath. 
#	vorh. Datei wird überschrieben
# 	Rückgabe outfile bei Erfolg, '' bei Fehlschlag
# https://knowledge.kaltura.com/troubleshooting-srt-files
# Wegen des strptime-Problems unter Kodi verzicht wir auf auf
#	korrekte Zeitübersetzung und ersetzen lediglich
#		1. den Zeitoffset 10 durch 00
#		2. das Sekundenformat 02.000 durch 02,00 (Verzicht auf die letzte Stelle)
# Problem mit dt.datetime.strptime (Kodi: attribute of type 'NoneType' is not callable):
# 	https://forum.kodi.tv/showthread.php?tid=112916
# Migration Python3: s. from __future__ import print_function
#
def xml2srt(infile):
	PLog("xml2srt: " + infile)
	outfile = '%s.srt' % infile

	with open(infile) as fin:
		text = fin.read()
		text = text.replace('-1:', '00:') 		# xml-Fehler
		# 10-Std.-Offset simpel beseitigen (2 Std. müssten reichen):
		text = (text.replace('"10:', '"00:').replace('"11:', '"01:').replace('"12:', '"02:'))
		ps = blockextract('<tt:p', text)
		
	try:
		with open(outfile, 'w') as fout:
			for i, p in enumerate(ps):
				begin 	= stringextract('begin="', '"', p)		# "10:00:07.400"
				end 	= stringextract('end="', '"', p)		# "10:00:10.920"			
				ptext	=  blockextract('tt:span style=', p)
				
				begin	= begin[:8] + ',' + begin[9:11]			# ""10:00:07,40"			
				end		= end[:8] + ',' + end[9:11]				# "10:00:10,92"

				print(i+1, file=fout)
				print('%s --> %s' % (begin, end), file=fout)
				# print >>fout, p.text
				for textline in ptext:
					text = stringextract('>', '<', textline) # style="S3">Willkommen zum großen</tt:span>
					print(text, file=fout)
				print(file=fout)
		os.remove(infile)									# Quelldatei entfernen
	except Exception as exception:
		PLog(str(exception))
		outfile = ''
			
	return outfile

#----------------------------------------------------------------
#	Favs / Merkliste dieses Addons einlesen
#
def ReadFavourites(mode):	
	PLog('ReadFavourites:')
	if mode == 'Favs':
		fname = xbmc.translatePath('special://profile/favourites.xml')
	else:	# 'Merk'
		fname = WATCHFILE
	try:
		page = RLoad(fname,abs_path=True)
	except Exception as exception:
		PLog(str(exception))
		return []
				
	if mode == 'Favs':
		favs = re.findall("<favourite.*?</favourite>", page)
	else:
		favs = re.findall("<merk.*?</merk>", page)
	# PLog(favs)
	my_favs = []; fav_cnt=0;
	for fav in favs:
		if mode ==  'Favs':
			if ADDON_ID not in fav: 	# skip fremde Addons, ID's in merk's wegen 	
				continue				# 	Base64-Kodierung nicht lesbar
		my_favs.append(fav) 
		
	# PLog(my_favs)
	return my_favs

#----------------------------------------------------------------
# holt summary (Inhaltstext) für eine Sendung, abhängig von SETTINGS('pref_load_summary')
#	- Inhaltstext zu Video im Voraus laden. 
#	SETTINGS durch Aufrufer geprüft
#	ID: ARD, ZDF - Podcasts entspr. ARD
# Es wird nur die Webseite ausgewertet, nicht die json-Inhalte der Ladekette.
# Cache: 
#		Text wird in TEXTSTORE gespeichert, Dateiname aus path generiert.
#
# Aufrufer: ZDF: 	ZDF_get_content (für alle ZDF-Rubriken)
#			ARD: 	ARDStart	-> ARDStartRubrik 
#					SendungenAZ, ARDSearchnew, 	ARDStartRubrik,
#					ARDPagination -> get_page_content
#					ARDStartRubrik (Swiper) 
#					ARDVerpasstContent
#				
#	Aufruf erfolgt, wenn für eine Sendung kein summary (teasertext, descr, ..) gefunden wird.
#
# Nicht benötigt in ARD-Suche (Search -> SinglePage -> get_sendungen): Ergebnisse 
#	enthalten einen 'teasertext' bzw. 'dachzeile'. Dto. Sendung Verpasst
# 
# Nicht benötigt in ZDF-Suche (ZDF_Search -> ZDF_get_content): Ergebnisse enthalten
#	einen verkürzten 'teaser-text'.
#
def get_summary_pre(path, ID='ZDF', skip_verf=False):	
	PLog('get_summary_pre: ' + ID)
	
	if 'Video?bcastId' in path:					# ARDClassic
		fname = path.split('=')[-1]				# ../&documentId=31984002
		fname = "ID_%s" % fname
	else:	
		fname = path.split('/')[-1]
		fname.replace('.html', '')				# .html bei ZDF-Links abschneiden
		
	fpath = os.path.join(TEXTSTORE, fname)
	PLog('fpath: ' + fpath)
	
	summ = ''
	if os.path.exists(fpath):		# Text lokal laden + zurückgeben
		PLog('lade lokal:') 
		summ =  RLoad(fpath, abs_path=True)
		return summ					# ev. leer, falls in der Liste eine Serie angezeigt wird 
	
	page, msg = get_page(path)		# extern laden
	if page == '' or 'APOLLO_STATE__ = {}' in page:
		return ''
	
	verf=''	
	if 	ID == 'ZDF':
		summ = stringextract('description" content="', '"', page)
		summ = mystrip(summ)
		#if 'title="Untertitel">UT</abbr>' in page:	# stimmt nicht mit get_formitaeten überein
		#	summ = "UT | " + summ
		if u'erfügbar bis' in page:										# enth. Uhrzeit									
			verf = stringextract(u'erfügbar bis ', '<', page)			# Blank bis <
		if verf:														# Verfügbar voraanstellen
			summ = u"[B]Verfügbar bis %s[/B]\n\n%s\n" % (verf, summ)
		
	if 	ID == 'ARDnew':
		page = page.replace('\\"', '*')									# Quotierung vor " entfernen, Bsp. \"query\"
		if '/ard/player/' in path or '/ard/live/' in path:				# json-Inhalt
			summ = stringextract('synopsis":"', '","', page)
		else:									# HTML-Inhalt
			summ = stringextract('synopsis":"', '"', page)
		summ = repl_json_chars(summ)
		if skip_verf == False:
			if u'verfügbar bis:' in page:								# html mit Uhrzeit									
				verf = stringextract(u'verfügbar bis:', '</p>', page)	# 
				verf = cleanhtml(verf)
			if verf:													# Verfügbar voranstellen
				summ = u"[B]Verfügbar bis %s[/B]\n\n%s" % (verf, summ)
			
	if 	ID == 'ARDClassic':
		# summ = stringextract('description" content="', '"', page)		# geändert 23.04.2019
		summ = stringextract('itemprop="description">', '<', page)
		if u'Verfügbar bis' in page:										
			verf = stringextract(u'Verfügbar bis ', ' ', page)			# Blank bis Blank
		if len(verf) == 10:												# Verfügbar voraanstellen
			summ = u"[B]Verfügbar bis %s[/B]\n\n%s" % (verf, summ)
		 	
	summ = unescape(summ)			# Text speichern
	summ = cleanhtml(summ)	
	summ = repl_json_chars(summ)
	# PLog('summ:' + summ)
	if summ:
		msg = RSave(fpath, summ)
	# PLog(msg)
	return summ
	
#---------------------------------------------------------------------------------------------------
# Icon aus livesenderTV.xml holen
# 24.01.2019 erweitert um link
# Bei Bedarf erweitern für EPG (s. SenderLiveListe)
def get_playlist_img(hrefsender):
	PLog('get_playlist_img: ' + hrefsender); 
	playlist_img=''; link='';
	playlist = RLoad(PLAYLIST)		
	playlist = blockextract('<item>', playlist)
	for p in playlist:
		s = stringextract('hrefsender>', '</hrefsender', p) 
		#s = stringextract('title>', '</title', p)	# Classic-Version
		PLog(hrefsender); PLog(s); 
		if s:									# skip Leerstrings
			PLog(type(s)); PLog(type(hrefsender));
			if up_low(s) in up_low(hrefsender):
				playlist_img = stringextract('thumbnail>', '</thumbnail', p)
				playlist_img = R(playlist_img)
				link =  stringextract('link>', '</link', p)
				break
	PLog(playlist_img); PLog(link); 
	return playlist_img, link

#---------------------------------------------------------------------------------------------------
# Link für TV-Livesender aus ARD-Start holen - z.Z. nur Classic
#	Aufrufer: ARDStartRubrik, SenderLiveResolution (Fallback für
#		 Link in livesenderTV.xml)
def get_startsender(hrefsender):
	PLog('get_startsender: ' + hrefsender); 
	page, msg = get_page(path=hrefsender)	
	config_id =  stringextract('/play/config/', '&', page)
	# Altern.: /play/media/35283076?devicetype=phone&features=hls (weniger Inhalt)
	json_url = BASE_URL + '/play/config/%s?devicetype=phone' % config_id
	
	page, msg = get_page(path=json_url)
	href = 'https:' + stringextract('clipUrl":"', '"', page)	
	return href
	
####################################################################################################
# PlayVideo aktuell 23.03.2019: 
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Dasselbe gilt für TV-Livestreams.
#		Param. Merk (added in Watch): True=Video aus Merkliste  
#
# 	Aufruf indirekt (Kennz. Playable): 	
#		ARDStartRubrik, ARDStartSingle, SinglePage (Ausnahme Podcasts),
#		SingleSendung (außer m3u8_master), SenderLiveListe, 
#		ZDF_get_content, 
#		Modul zdfMobile: PageMenu, SingleRubrik
#							
#	Aufruf direkt: 
#		ARDStartVideoStreams, ARDStartVideoMP4,
#		SingleSendung (m3u8_master), SenderLiveResolution 
#		show_formitaeten (ZDF),
#		Modul zdfMobile: ShowVideo
#
#	Format sub_path s. https://alwinesch.github.io/group__python__xbmcgui__listitem.html#ga24a6b65440083e83e67e5d0fb3379369
#	Die XML-Untertitel der ARD werden gespeichert + nach SRT konvertiert (einschl. minus 10-Std.-Offset)
#	Resume-Funktion Kodi-intern  DB MyVideos107.db, Tab files (idFile, playCount, lastPlayed) + (via key idFile),
#		bookmark (idFile, timelnSeconds, totalTimelnSeconds)
#
def PlayVideo(url, title, thumb, Plot, sub_path=None, Merk='false'):	
	PLog('PlayVideo:'); PLog(url); PLog(title);	 PLog(Plot); 
	PLog(sub_path);
	
	Plot=transl_doubleUTF8(Plot)
	Plot=(Plot.replace('[B]', '').replace('[/B]', ''))	# Kodi-Problem: [/B] wird am Info-Ende platziert
	url=url.replace('\\u002F', '/')						# json-Pfad noch unbehandelt
	
	li = xbmcgui.ListItem(path=url)		
	# li.setArt({'thumb': thumb, 'icon': thumb})
	li.setArt({'poster': thumb, 'banner': thumb, 'thumb': thumb, 'icon': thumb, 'fanart': thumb})	
	
	Plot=Plot.replace('||', '\n')				# || Code für LF (\n scheitert in router)
	# li.setProperty('IsPlayable', 'true')		# hier unwirksam
	# li.setInfo(type="video", infoLabels={"Title": title, "Plot": Plot, "mediatype": "video"}) # s.u.

	infoLabels = {}
	infoLabels['title'] = title
	infoLabels['sorttitle'] = title
	#infoLabels['genre'] = genre
	#infoLabels['plot'] = Plot
	#infoLabels['plotoutline'] = Plot
	infoLabels['tvshowtitle'] = Plot
	infoLabels['tagline'] = Plot
	infoLabels['mediatype'] = 'video'
	li.setInfo(type="Video", infoLabels=infoLabels)
	
	# Info aus GetZDFVideoSources hierher verlagert - wurde von Kodi nach Videostart 
	#	erneut gezeigt - dto. für ARD (parseLinks_Mp4_Rtmp, ARDStartSingle)
	if sub_path:							# Vorbehandlung ARD-Untertitel
		if 'ardmediathek.de' in sub_path:	# ARD-Untertitel speichern + Endung -> .sub
			local_path = "%s/%s" % (SUBTITLESTORE, sub_path.split('/')[-1])
			local_path = os.path.abspath(local_path)
			try:
				urlretrieve(sub_path, local_path)
			except Exception as exception:
				PLog(str(exception))
				local_path = ''
			if 	local_path:
				sub_path = xml2srt(local_path)	# leer bei Fehlschlag

	PLog('sub_path: ' + str(sub_path));		
	if sub_path:							# Untertitel aktivieren, falls vorh.	
		if SETTINGS.getSetting('pref_UT_Info') == 'true':
			msg1 = 'Info: für dieses Video stehen Untertitel zur Verfügung.' 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			
		if SETTINGS.getSetting('pref_UT_ON') == 'true':
			sub_path = 	sub_path.split('|')											
			li.setSubtitles(sub_path)
			xbmc.Player().showSubtitles(True)		
		
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
	PLog("IsPlayable: %s, Merk: %s" % (IsPlayable, Merk))
	PLog("kodi_version: " + KODI_VERSION)							# Debug
	# kodi_version = re.search('(\d+)', KODI_VERSION).group(0) # Major-Version reicht hier - entfällt
	
	if url_check(url, caller='PlayVideo'):
		if IsPlayable == 'true':								# true - Call via listitem
			PLog('PlayVideo_Start: listitem')
			xbmcplugin.setResolvedUrl(HANDLE, True, li)			# indirekt
		else:													# false, None od. Blank
			PLog('PlayVideo_Start: direkt')
			xbmc.Player().play(url, li, windowed=False) 		# direkter Start
			sleep(50 / 100)
			return

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
#				Code für beides entfernt. Hilft ab er nur bei wenigen Sendern.
#				Neue Kodivers. ansch. nicht betroffen, Kodi 18.2. OK
#			
def PlayAudio(url, title, thumb, Plot, header=None, url_template=None, FavCall=''):
	PLog('PlayAudio:'); PLog(title); PLog(FavCall); 
	Plot=transl_doubleUTF8(Plot)
				
	if url.startswith('http') == False:		# lokale Datei
		url = os.path.abspath(url)
				
	#if header:							
	#	Kodi Header: als Referer url injiziert - z.Z nicht benötigt	
	# 	header='Accept-Encoding=identity;q=1, *;q=0&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&Accept=*/*&Referer=%s&Connection=keep-alive&Range=bytes=0-' % slink	
	#	# PLog(header)
	#	url = '%s|%s' % (url, header) 
	
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
				PLog('Starte Screensaver1: %s' % path)
				# Konfig: Kodi Player-Einstellungen / Bilder
				xbmc.sleep(200)
				xbmc.Player().play(url, li, False)
				return
			if slide_mode == "Addon":								# Slideshow Addon
				xbmc.Player().play(url, li, False)					# vor modaler Slideshow			
				import resources.lib.slides as slides
				PLog('Starte Screensaver2: %s' % path)
				CWD = ADDON.getAddonInfo('path').decode("utf-8") # working dir
				screensaver_gui = slides.Slideshow('script-python-slideshow.xml', CWD, 'default')
				screensaver_gui.doModal()
				xbmc.Player().stop()					
				del screensaver_gui
				return
	else:			
		xbmc.Player().play(url, li, False)						# ohne Slideshow 

#---------------------------------------------------------------- 
# Aufruf: PlayVideo
def url_check(url, caller=''):
	PLog('url_check:')
	if url.startswith('http') == False:		# lokale Datei - kein Check
		return True
		
	UrlopenTimeout = 6
	# Tests:
	# url='http://104.250.149.122:8012'	# Debug: HTTP Error 401: Unauthorized
	# url='http://feeds.soundcloud.com/x'	# HTTP Error 400: Bad Request
	
	req = Request(url)
	try:
		r = urlopen(req, timeout=UrlopenTimeout)
		PLog('Status: ' + str(r.getcode()))
		return True
	except Exception as exception:
		err = str(exception)
		msg1= '%s: Seite nicht erreichbar - Url:' % caller
		msg2 = url
		msg3 = 'Fehler: %s' % err
		PLog(msg3)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)		 			 	 
		return False
	
####################################################################################################

