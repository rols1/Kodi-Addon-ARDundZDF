# -*- coding: utf-8 -*-
################################################################################
#				strm.py - Teil von Kodi-Addon-ARDundZDF
#			 Erzeugung von strm-Dateien für Kodi's Medienverwaltung
################################################################################
# 	<nr>14</nr>										# Numerierung für Einzelupdate
#	Stand: 06.01.2024
#

from __future__ import absolute_import
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys 
import glob, shutil
import re				
import json	
import time	
import datetime		
	
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus
	from urlparse import parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, parse_qs
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

from resources.lib.util import *

NAME			= 'ARD und ZDF'
HANDLE			= int(sys.argv[1])
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
STRMSTORE 		= os.path.join(ADDON_DATA, "strm") 						# Default-Verz. strm
FLAG_OnlyUrl	= os.path.join(ADDON_DATA, "onlyurl")					# Flag PlayVideo_Direct	-> strm-Modul
																		# 	Mitnutzung ZDF_getStrmList
STRM_URL		= os.path.join(ADDON_DATA, "strmurl")					# Ablage strm-Url (PlayVideo_Direct)	
STRM_SYNCLIST	= os.path.join(ADDON_DATA, "strmsynclist")				# strm-Liste für Synchronisierung	
STRM_CHECK 		= os.path.join(ADDON_DATA, "strm_check_alive") 			# strm-Synchronisierung (Lockdatei)
STRM_TOOLS_SET	= os.path.join(ADDON_DATA, "strmtoolset")				# Settings der stm-Tools	
STRM_LOGLIST 	= os.path.join(ADDON_DATA, "strmloglist") 				# strm-LOG-Datei 
MAX_LOGLINES	= 200													# max. Anzahl Zeilen strm-LOG-Datei 
	
ICON 			= 'icon.png'		# ARD + ZDF
ICON_DIR_STRM	= "Dir-strm.png"
PLog('Script strm.py geladen')

# Basis Template, für Ausbau siehe
# 	https://kodi.wiki/view/NFO_files/Templates
# 	nicht genutzt: "Album|album"
STRM_TYPES		= ["Film|movie", "TV-Show|tvshow", "Episode|episodedetails",  
					"Musik-Video|musicvideo" 
				] 
NFO1 = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'		# nfo-Template, 
NFO2 = '<movie>\n<title>%s</title>\n<uniqueid type="tmdb" default="true"></uniqueid>\n'
NFO3 = '<thumb spoof="" cache="" aspect="poster">%s</thumb>\n'
NFO4 = '<plot>%s</plot>\n<weburl>%s</weburl>\n</movie>'					# Tag weburl (inoff.) für Abgleich
NFO = NFO1+NFO2+NFO3+NFO4												#	 vorh. / nicht mehr vorh.
									

######################################################################## 
# todo Tools : Lock entfernen (Monitor-Reset), synclist teilw. od. ganz löschen,
#			sync_hour  festlegen
#			Option: Monitor neu starten (nach Änd. sync_hour obligatorisch)
#			Log für Sync-Läufe
#			Bereinigen (nicht mehr verfügb. löschen)
# 
def strm_tools():
	PLog("strm_strm_tools:")
	icon = R("icon-strmtools.png")
	from ardundzdf import InfoAndFilter			# z.Z. nicht für Return genutzt
	
	if os.path.exists("strmsync_stop"):						# Stop-Flag als Leiche?
		now = time.time()
		mtime = os.stat("strmsync_stop").st_mtime
		diff = int(now) - mtime
		if diff > 10:										# entf. wenn älter als 10 sec	
			os.remove("strmsync_stop")
			PLog("strmsync_stop, age: %d sec" % diff)
	
		
	while(1):
		add_log=''	
		msg1 = u'Monitorreset'
		msg2 = u"für strm-Tools"
		sync_hour = strm_tool_set(mode="load")			# Setting laden
		PLog("sync_hour: " + sync_hour)	
		
		# Tools verlassen: Haupt-PRG startet Monitor neu
		tmenu = [ u"Abgleichintervall | %s Stunden | Tools verlassen" % sync_hour,
					 u"Liste anzeigen", u"Listeneintrag löschen", u"Monitor-Reset | Tools verlassen", 
					u"strm-Log anzeigen", u"sofortigen Abgleich einer Liste erzwingen",
					u"unterstützte Sender / Beiträge", u"zu einem strm-Verzeichnis wechseln | 1 Beitrag ansehen"
				]
		next_strm_sync = Dict("load", "next_strm_sync")
		if next_strm_sync == False:
			head = "es existiert noch keine Abgleichliste"
		else:
			head = u"strm-Tools | nächster Abgleich: %s Uhr" % next_strm_sync
		ret = xbmcgui.Dialog().select(head, tmenu)
		PLog("tools_ret: " + str(ret))	
		if ret == None or ret == -1:
			return #InfoAndFilter()						# -> InfoAndFilter, kompl. Liste
			
		if ret == 0:									# Zeitintervall
			PLog("set_val")
			valmenu = ["6", "12", "24", "36",]
			head = "Zeitintervall in Stunden"
			ret0 = xbmcgui.Dialog().select(head, valmenu)
			PLog(ret)	
			if ret0 >= 0:							
				sync_hour = valmenu[ret0]
				PLog("sync_hour: " +  sync_hour)
				strm_tool_set(mode="save", index=0, val=sync_hour)	# Index 0: sync_hour
				xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
				if os.path.exists('strmsync_stop') == False:		# Stop-Flag für Monitor
					open('strmsync_stop', 'w').close()
					
				add_log = "%6s | %15s | %s" % ("TIME", "strm-Tools", "Intervall: %s Stunden" % sync_hour)
				PLog("add_log: " +  add_log)
				
														# Liste anzeigen / löschen / abgleichen / zum Verzeichnis wechseln
		if ret == 1 or  ret == 2 or  ret == 5 or ret == 7:
			PLog("show_list")
			title = u"strm-Listen im Abgleich"
			synclist=[]; mylist1=[]; mylist2=[]			# 2 Listen: textviewer, select
			if os.path.exists(STRM_SYNCLIST):
				PLog(os.path.getsize(STRM_SYNCLIST))
				if os.path.getsize(STRM_SYNCLIST) > 10:	
					synclist = strm_synclist(mode="load")
					PLog("synclist: %d" % len(synclist))
					for line in synclist:
						line = py2_decode(line)
						list_title,strmpath,list_path,strm_type = line.split("##")
						# mylist1: akt. Liste , mylist2: Löschliste
						mylist1.append(u"%20s.. | %40s.. | %s" % (list_title[:20], strmpath[:40], strm_type))
						mylist2.append(u"%30s | %s" % (list_title[:30], strm_type))
			if len(synclist) == 0:
				msg1 = u'Liste fehlt'
				msg2 = u"keine Abgleichliste gefunden"
				xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
				continue
				
			if ret == 1:								# Liste anzeigen
				mylist1 =  "\n".join(mylist1)
				xbmcgui.Dialog().textviewer(title, mylist1,usemono=True)
					
			if ret == 2:								# Listeneinträge löschen
				title = u"Listeneintrag löschen"
				ret1 = xbmcgui.Dialog().select(title, mylist2)
				PLog(ret1)
				if ret1 >= 0:
					del_item = mylist2[ret1]
					del_item = del_item.strip()
					msg1 = u"Eintrag aus Abgleichliste wirklich entfernen und Synchronisation damit einstellen?"
					msg2 = "[B]%s[/B]" % del_item
					ret2 = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
					if ret2 == 1:
						item = synclist[ret1]
						synclist.remove(item)
						synclist =  "\n".join(synclist)
						msg = RSave(STRM_SYNCLIST, py2_encode(synclist))
						
						path = item.split("##")[1]; 	# dazugehörigen Beiträge löschen?
						msg = path
						if len(msg) > 54:				# dialogbegrenzt
							msg = ".." + msg
						#verz = os.path.split(path)[1]	# 0 head, 1 tail
						msg1 = u"sollen auch die dazugehörigen Beiträge gelöscht werden?"
						msg2 = u"Damit würde dieses Verzeichnis mit den strm-, nfo- und jpeg-Dateien entfernt:"
						msg3 = "[B]%s[/B]" % msg[:54]
						r = MyDialog(msg1=msg1, msg2=msg2, msg3=msg3, ok=False, cancel='Abbruch', yes='JA', heading=title)
						
						msg1 = u"Listeneintrag"
						msg2 = u"gelöscht"
						if r == 1:
							shutil.rmtree(path, ignore_errors=True)
							msg2 = u"und Verzeichnis gelöscht"						
						
						msg=''
						if msg == '':
							xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
							add_log = "%6s | %15s | %s" % ("DELETE", "strm-Tools", del_item[:40])

			if ret == 7:								# zu einem strm-Verzeichnis wechseln, Liste mylist2
				title = u"strm-Verzeichnis  wählen"
				ret7 = xbmcgui.Dialog().select(title, mylist2)
				if ret7 >= 0:
					item = synclist[ret7]
					strmpath = item.split("##")[1]
					# Warten auf ret_flag unterdrückt Tools während der Beitrags-Liste: 
					ret_flag = show_strm_element(strmpath)
					PLog("ret_flag: " + str(ret_flag))
					# ext. Aufruf verhindert nicht Rückspr. in Loop
					# s. Doku start_script
				else:
					ret = 1										# in Tools bleiben					
			
		if ret == 3:											# Monitorreset			
			PLog("set_reset")
			if os.path.exists('strmsync_stop') == False:		# Stop-Flag für Monitor
				open('strmsync_stop', 'w').close()
			xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
			add_log = "%6s | %15s | %s" % ("RESET", "strm-Tools", "Monitor-Reset")
			
		if ret == 4:											# strm-Log anzeigen			
			PLog("strm_log_show")
			log_show(MAX_LOGLINES)
						
		if ret == 5:											# einzelne Liste abgleichen
			PLog("strm_run_sync")
			title = u"einzelne Liste jetzt abgleichen"
			ret5 = xbmcgui.Dialog().select(title, mylist2)
			PLog(ret5)
			if ret5 >= 0:
				msg1 = u"Abgleich jetzt starten?"
				msg2 = "[B]%s[/B]" % mylist2[ret5]
				ret6 = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
				if ret6 == 1:
					item = synclist[ret5]
					PLog("strm_run_sync: " + item)
					list_title, strmpath, list_path, strm_type= item.split("##")
					if "//zdf-cdn" in list_path or "mediathekV2" in list_path:		# ZDF-Sync
						do_sync(list_title, strmpath, list_path, strm_type)
					else:
						do_sync_ARD(list_title, strmpath, list_path, strm_type)		# ARD-Sync
					log_show(MAX_LOGLINES)				# Log anzeigen
			

		if ret == 6:									# unterstützte Sender/Beiträge
			msg1 = u"[B]ARD- und ZDF-Serien[/B], die für die Auswahl geeignete Merkmale aufweisen -"
			msg1 = u'%s erkennbar am Button:\n[B]strm-Dateien für die komplette Liste erzeugen[/B]' %msg1
			MyDialog(msg1, msg2='', msg3='')
			

		#-----------------								# Aktualisierung strm-Log
		PLog("strm_log_update")
		if add_log:										# z.B.: "RESET"		
			log_update(add_log)							# Log aktualisieren

		if ret == 0 or ret == 3:# or ret == 7:			# Tools sicher verlassen
			return 										# Intervall, Reset, Beitrag ansehen
		if ret == 7:									# Overlay Tools verhindern in Beitrag ansehen
			sleep(2)
			return
				
				
	return	
# ----------------------------
# Anzeige strm-Log 
def log_show(max_loglines):	
	PLog("log_show:")
	dt = datetime.datetime.now()
	now_time = dt.strftime("%Y-%m-%d_%H-%M-%S")
	if os.path.exists(STRM_LOGLIST):
		loglist = RLoad(STRM_LOGLIST, abs_path=True)
		loglist = loglist.splitlines()
		mylist=[]
		for line in loglist:
			mylist.append(u"%s..." % line[:80])				
		mylist.sort(reverse=True)				# absteigend
		PLog("len_mylist: %d, max_loglines: %d" % (len(mylist), max_loglines))
							
		mylist =  "\n".join(mylist)
		xbmcgui.Dialog().textviewer("strm-Log (max. %d Zeilen)" % max_loglines, mylist,usemono=True)	
	return	
		
# ----------------------------
# Update strm-Log mit line (Aufrufer füllt line)
# Bsp. für line:
# 	"%6s | %15s | %s" % ("ERR", list_title[:15], msg[:45])
# hier wird der Zeitstempel logtime in line vorangestellt
#
def log_update(line):
	PLog("log_update:")
	
	loglist=''
	if os.path.exists(STRM_LOGLIST):			# Log laden (Textformat)
		loglist = RLoad(STRM_LOGLIST, abs_path=True)
		loglist = loglist.strip()
	
	dt = datetime.datetime.now()
	logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
	line = "%s | %s" % (logtime, line)
	PLog("line: " + line)
	loglist =  "%s\n%s" % (loglist, line)
	
	loglist = loglist.split("\n")
	PLog("max_line_check: len_loglist: %d,max_loglines: %d" % (len(loglist), MAX_LOGLINES))
	if len(loglist) > MAX_LOGLINES:
		loglist = loglist[-MAX_LOGLINES:]
		PLog(len(loglist))
	loglist = "\n".join(loglist)
	
	log_save(loglist)
	return
	
# ----------------------------
# Speichern strm-Log mit Lock 
# loglist: Textformat
# maxloops bei Bedarf erhöhen 
def log_save(loglist):	
	PLog("log_save:")
	maxloops	= 4				# 2 sec bei 4x xbmc.sleep(500)	
	
	lockfile = os.path.join(ADDON_DATA, "strmloglock")
	PLog(lockfile) 
	i=0
	while os.path.exists(lockfile):	
		i=i+1
		if i >= maxloops:		# Lock brechen, vermutl. Ruine
			os.remove(lockfile)
			PLog("doLock_break: " + lockfile)
			break
		xbmc.sleep(500)	
	
	if os.path.exists(lockfile) == False:
		open(lockfile, 'w').close()
	RSave(STRM_LOGLIST, loglist.strip())
	try:
		os.remove(lockfile)
	except Exception as exception:
		PLog(str(exception))
	return
	
# ----------------------------------------------------------------------
def unpack(add_url):
	PLog("unpack:")
	add_url = unquote_plus(add_url)
	PLog(add_url[:100])
	
	dirID 	= stringextract('dirID=', '&', add_url)
	fanart 	= stringextract('fanart=', '&', add_url)
	thumb	= stringextract('thumb=', '&', add_url)
	fparams = add_url.split('fparams')[-1]					#/?action=dirList&dirID= ..
	fparams = unquote_plus(fparams)
	fparams	= fparams[1:]									# ={'url':..
	
	PLog("unpack_done")
	PLog("dirID: %s\n fanart: %s\n thumb: %s\n fparams: %s" % (dirID, fanart, thumb, fparams))
	return dirID, fanart, thumb, fparams

# ----------------------------------------------------------------------
# Aufruf Kontextmenü, abhängig von SETTINGS.getSetting('pref_strm')
# 	Param. siehe addDir, mediatype == "video"
def do_create(label, add_url):
	PLog("do_create: " + label)
	PLog(SETTINGS.getSetting('pref_strm_uz'))
	PLog(SETTINGS.getSetting('pref_strm_path'))
	icon = R(ICON_DIR_STRM)

	dirID, fanart, thumb_org, fparams = unpack(add_url)				# Params Kontextmenü auspacken
	if get_Source_Funcs_ID(add_url) == '':							# Zielfunktion unterstützt?
		msg1 = u'nicht unterstützt'
		msg2 = u'Videoquelle nicht für strm geeignet'
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		return	
			
	strm_type = get_strm_genre()									# Genre-Auswahl
	if strm_type == '':
		return
	#------------------------------									# Abfrage Zielverz. != Filme/Serien
	strmpath = get_strm_path(strm_type)
		
	#------------------------------							
	title	= stringextract("title': '", "'", fparams) 				# fparams json-Format
	url	= stringextract("url': '", "'", fparams) 
	if url == '':
		url	= stringextract("path': '", "'", fparams)				# Livestream  SenderLiveResolution
	thumb	= stringextract("thumb': '", "'", fparams) 
	Plot	= get_Plot(fparams)
		
	if title == '' or "| auto" in title or u"| Auflösung" in title:	# Anwahl Streaming-/MP4-Formate
		if Plot.startswith("Title: "):
			title = Plot
		else:
			title = label
	if thumb == '':
		thumb = thumb_org	
	PLog("title: %s\n thumb: %s\n url: %s\n Plot:%s" % (title, thumb, url, Plot))
	
	formats = [".m3u8", ".mp4", ".mp3", ".webm"]					# Url-Test
	my_ext = url.split(".")[-1]
	url_found = False										
	for f in formats:
		if f in url:
			url_found = True										# True: PlayVideo bei Einzelauflösung
	PLog("url_found: " + str(url_found))
	if url_found == False and dirID != "PlayVideo":	
		msg1 = u'ermittle Streamurl'
		msg2 = title
		xbmcgui.Dialog().notification(msg1,msg2,icon,1000,sound=False)
					
		url = get_streamurl(add_url)								# Streamurl ermitteln
		if url == '':												# Url fehlt/falsch: Abbruch	
			msg1 = u"die erforderliche Stream-Url fehlt für"
			msg2 = title									
			MyDialog(msg1, msg2, "Abbruch")
			return
	
	#------------------------------									# Abfrage Dateiname
	fname = make_filenames(title)									# sichere Dateinamen für Video
	new_name = get_keyboard_input(line=fname, head=u"Dateiname übernehmen / eingeben")
	PLog("new_name: " + new_name)
	if new_name.strip() == '':
		return
	fname = make_filenames(new_name)								# nochmal, falls geändert
	PLog("dest_fname: " + fname)
	#------------------------------									# strm-, nfo-, jpeg-Dateien anlegen
	weburl	= ''													# nur bei Serien
	ret = xbmcvfs_store(strmpath, url, thumb, fname, title, Plot, weburl, strm_type)
	msg1 = u'STRM-Datei angelegt'
	if ret ==  False:
		msg1 = u'STRM-Datei fehlgeschlagen'
	msg2 = fname
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
									
	return
# ----------------------------------------------------------------------
def get_strm_path(strm_type):
	PLog("get_strm_path:")
	
	strmpath = STRMSTORE											# Default
	choose_path = False
	if strm_type == "movie":
		verz = SETTINGS.getSetting('pref_strm_film_path')
		if verz != '' and verz != None:	
			strmpath = verz
			choose_path = False
	
	else:
		verz = SETTINGS.getSetting('pref_strm_series_path')
		if verz != '' and verz != None:	
			heading = u"Ablage festlegen/ändern: %s" % verz
			newdir = DirectoryNavigator(settingKey='',mytype=0, heading=verz, shares='files', path=verz)
			PLog("newdir: " + str(newdir))
			strmpath = newdir										# Abbruch-Behandl. entf., bei Titelwahl möglich
		else:
			strmpath = STRMSTORE									# strm-Verzeichnis in userdata
			if os.path.isdir(strmpath) == False:
				try:
					os.mkdir(strmpath)
				except Exception as exception:
					PLog(str(exception))
					msg1 = u'strm-Verzeichnis konnte nicht angelegt werden:'
					msg2 = str(exception)
					MyDialog(msg1, msg2, '')
					return
					
	if strmpath == STRMSTORE:			
		msg1 = u'Die Ablage erfolgt im Datenverzeichnis des Addons, Unterverzeichnis: strm'
		msg2 = u'Ein anderes Verzeichnis kann in den Settings festgelegt werden.'
		MyDialog(msg1, msg2, '')
		
		if os.path.isdir(strmpath) == False:
			try:
				os.mkdir(strmpath)
			except Exception as exception:
				PLog(str(exception))
				msg1 = u'strm-Verzeichnis konnte nicht angelegt werden:'
				msg2 = str(exception)
				MyDialog(msg1, msg2, '')
				strmpath=''
		
	PLog("strmpath: " + strmpath)		
	return strmpath
# ----------------------------------------------------------------------
def get_strm_genre():
	PLog("get_strm_genre:")
	strm_type=''
	
	head = u"bitte Genre auswählen"
		
	ret = xbmcgui.Dialog().select(head, STRM_TYPES)
	if ret == None or ret == -1:							
		return strm_type
	PLog("ret: %d" % ret)
	strm_type = STRM_TYPES[ret]							# "Film|movie"
	strm_type = strm_type.split('|')[-1]
	PLog("strm_type: " + strm_type)
	
	return strm_type

# ----------------------------------------------------------------------
def get_Plot(fparams):
	PLog("get_Plot:")
	Plot=''
	fparams = transl_doubleUTF8(fparams)
	PLog(fparams)	# Debug

	Plot	= stringextract("Plot': '", "'", fparams)
	if Plot == '':										# Plot + Altern.
		 Plot = stringextract("summary': '", "'", fparams)
	if Plot == '':
		 Plot = stringextract("summ': '", "'", fparams)
	if "'tag'" in fparams:
		tag = stringextract("tag': '", "'", fparams)
		Plot = "%s\n\n%s" % (tag, Plot)

	 
	if "'dauer'" in fparams:
		dauer = stringextract("dauer': '", "'", fparams)
		Plot = "%s\n\n%s" % (dauer, Plot)

	Plot = Plot.replace("||", "\n")						# Rückübersetzung			

	return Plot
# ----------------------------------------------------------------------
#
# strm-, nfo-, jpeg-Dateien anlegen
# 	strmpath=strm-Verzeichnis, fname=Dateiname ohne ext.
# 	url=Video-Url, thumb=thumb-Url
# gui=False: ohne Gui, z.B. für ZDF_getStrmList
# 
def xbmcvfs_store(strmpath, url, thumb, fname, title, Plot, weburl, strm_type, gui=True):
	PLog("xbmcvfs_store:")
	PLog("strmpath: " + strmpath)
	PLog(url)
	
	if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
		strmpath = os.path.join(strmpath, fname)	# STRMSTORE + fname
		if os.path.isdir(strmpath) == False:		# Verz. erzeugen, falls noch nicht vorh.
			os.mkdir(strmpath)
	
	if thumb:
		if thumb.startswith("http"):					# Server / lokal?
			xbmcvfs_icon = os.path.join(strmpath, "%s.jpeg" % fname)
			urlretrieve(thumb, xbmcvfs_icon)
		else:
			xbmcvfs_icon = os.path.join(strmpath, "%s.png" % fname)
			shutil.copy(thumb, xbmcvfs_icon)			# Kopie von lokalem Icon (TV-Livestreams)	
		PLog("xbmcvfs_icon: " + xbmcvfs_icon)

	xbmcvfs_fname = os.path.join(strmpath, "%s.strm" % fname)
	PLog("xbmcvfs_fname: " + xbmcvfs_fname)
	f = xbmcvfs.File(xbmcvfs_fname, 'w')							
	if PYTHON2:
		ret1=f.write(url); f.close()			
	else:												# Python3: Bytearray
		buf = bytearray()
		buf.extend(url.encode())
		ret1=f.write(buf); f.close()			
	PLog("strm_ret: " + str(ret1))										
	
	xbmcvfs_fname = os.path.join(strmpath, "%s.nfo" % fname)
	PLog("xbmcvfs_fname: " + xbmcvfs_fname)
	
	PLog("strm_type: " + strm_type)
	nfo = NFO.replace("<movie>", "<%s>" % strm_type); 	# Anpassung Template
	nfo = nfo.replace("</movie>", "</%s>" % strm_type)
	
	nfo = nfo % (title, thumb, Plot, weburl)
	f = xbmcvfs.File(xbmcvfs_fname, 'w')							
	if PYTHON2:
		ret2=f.write(nfo); f.close()			
	else:												# Python3: Bytearray
		buf = bytearray()
		buf.extend(nfo.encode())
		ret2=f.write(buf); f.close()			
	PLog("nfo_ret: " + str(ret2))
	
	if ret1 == False or ret2 == False:
		if gui:
			msg1 = u"Erzeugung strm-Datei oder nfo-Datei fehlgeschlagen."
			msg2 = u"Bitte überprüfen"									
			MyDialog(msg1, msg2, "Abbruch")
		return False

	return True

# ----------------------------------------------------------------------
# Ermittlung Streamquelle (falls noch nicht gefunden, s. url_found).
# plugin-Script add_url ausführen -> HLS_List, MP4_List bauen,
# HLS_List, MP4_List durch PlayVideo_Direct auwerten lassen, Flag +
# 	Param-Austausch via Dict
#
def get_streamurl(add_url):
	PLog("get_streamurl:")
	streamurl=''; ID=''
	PLog(add_url[:100])
		
	ID = get_Source_Funcs_ID(add_url)
	if ID == '' or ID == "PlayVideo":					# PlayVideo: Url liegt schon vor
		return ''
		
	pos = add_url.find('/?action=')
	MY_SCRIPT_fparams = add_url[pos+1:]
	PLog("MY_SCRIPT_fparams: " + MY_SCRIPT_fparams)
	
	# Ermittlung Streamquelle + Start PlayVideo bis 'PlayVideo_Start: listitem'.
	# Bei Bedarf den Flag FLAG_OnlyUrl hierher verlegen und in PlayVideo beachten.
	# Hinw.: True für blocking call zur Erzeugung der HLS_List + MP4_List durch 
	#	MY_SCRIPT
	MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % ADDON_ID) 
	xbmc.executebuiltin('RunScript(%s, %s, %s)'  % (MY_SCRIPT, HANDLE, MY_SCRIPT_fparams), True)
	
	hls_list = os.path.join(DICTSTORE, "%s_HLS_List" % ID)
	mp4_list = os.path.join(DICTSTORE, "%s_MP4_List" % ID)
	max_cnt=0
	while(1):											# file_event: für die schwachbrüstigen Clients
		sleep(1)
		max_cnt = max_cnt + 1
		PLog("waiting: %d" % max_cnt)
		if os.path.exists(mp4_list) or os.path.exists(hls_list) or max_cnt > 3:
			break
			
	PLog("strm_ID: " + ID)
	HLS_List =  Dict("load", "%s_HLS_List" % ID)
	PLog("strm_HLS_List: " + str(HLS_List))
	MP4_List =  Dict("load", "%s_MP4_List" % ID)
	PLog("strm_MP4_List: " + str(MP4_List))
	
	# todo: Dateiflag urlonly setzen/löschen - Übergabe via script unsicher
	#	ev. auch Rückgabe via Datei
	
														# Url entspr. Settings holen:
	title_org=''; img=''; Plot='';						# hier nicht benötigt 
	
	# s. Beachte im Log: es überschneiden sich MY_SCRIPT und PlayVideo_Direct: 
	open(FLAG_OnlyUrl, 'w').close()						# Flag PlayVideo_Direct	-> strm-Modul		
	streamurl = PlayVideo_Direct(HLS_List, MP4_List, title_org, img, Plot)
	PLog("streamurl: " + streamurl)	
	return streamurl
	
# ----------------------------------------------------------------------
# Test auf unterstützte Zielfunktion 
#
def get_Source_Funcs_ID(add_url):
	PLog("get_Source_Funcs_ID:")	
	
	PLog(unquote_plus(add_url[:100]))
	
	# nachrüsten (abweichende Streamermittlung): funk, arte, 
	#	phoenix (einsch. Youtube-Videos), TagesschauXL, zdfmobile
	# PlayVideo: Einzelauflösung - ohne Ermittlung der Quellen, s. url_test
	Source_Funcs = [u"ARDnew.ARDStartSingle|ARDNEU",					# Funktionen + ID's
					u"my3Sat.SingleBeitrag|3sat", u'.XLGetSourcesPlayer|TXL',
					u"dirID=PlayVideo|PlayVideo",u"dirID=SenderLiveResolution|ARD",
					u"arte.SingleVideo|arte", u"ZDF_getVideoSources|ZDF"
					]
	ID=''																# derzeit nicht ermittelbar
	for item in Source_Funcs:
		dest_func, sid = item.split("|")
		PLog(dest_func); PLog(sid)
		if 	dest_func in add_url:
			ID = sid
			break
	PLog("ID: " + ID)	
	return ID	
	
# ----------------------------------------------------------------------
# holt strm-Liste STRM_SYNCLIST (strmsynclist)
# title: Titel der Liste aus ZDF_getStrmList
# Format: Listen-Titel ## lokale strm-Ablage ##  ext.Url ## strm_type
def strm_synclist(mode="load", item=''):
	PLog("strm_synclist:")	
	icon = R(ICON_DIR_STRM)
	
	synclist = RLoad(STRM_SYNCLIST, abs_path=True)
	synclist = synclist.strip()
	synclist = synclist.splitlines()
	
	if mode == "load":
		if synclist == '':
			return []
		PLog(len(synclist))	
		return synclist
	
	if mode == "save":							# falls fehlend neu aufnehmen
		title = "%s" % item.split("##")[0]
		msg1 = "Liste aufgenommen"
		msg2 = title
		if exist_in_list(item, synclist) == False:
			synclist.append(item)
			synclist =  "\n".join(synclist)
			msg = RSave(STRM_SYNCLIST, py2_encode(synclist))
			if msg:
				msg1 = "Syncliste fehlgeschlagen" 
				msg2 = msg
			xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		else:
			msg1 = "Liste schon vorhanden"
			xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)		
		
	PLog(len(synclist))	
	return	
# ----------------------------------------------------------------------
# holt Settings der stm-Tools (Datei strmtoolset)
# bei Bedarf erweitern
# mode: load / save /set 
#	set i.V.m. index, val
def strm_tool_set(mode="load", index=0, val=''):
	PLog("strm_tool_set: " + mode)
	sync_hour = "12"						# Default Intervall in Std.	
	
	toolset = RLoad(STRM_TOOLS_SET, abs_path=True)
	PLog(toolset[:60])
	toolset = toolset.splitlines()
	save_init=False
	if len(toolset) == 0:					# Init mit Default sync_hour
		toolset.append(sync_hour)
		index=0; val=sync_hour
		save_init=True
	
	if mode == "save" or save_init:
		PLog(index); PLog(val)
		if val:
			toolset[index] = val
		toolset = "\n".join(toolset)
		RSave(STRM_TOOLS_SET, toolset)
		
	if mode == "load":
		sync_hour = toolset[0]
		sync_hour = sync_hour.strip()			# manuell geändert?
		return sync_hour

	return
# ----------------------------------------------------------------------
# neue Folgen aufnehmen (Log: Check1)
# Aufrufer: Monitor strm_sync
# strmpath: lokale strm-Ablage
# import ZDF_FlatListRec + ZDF_getApiStreams hier wg. Rekursion im Modul-
#	kopf (Thread strm_sync)
# 02.05.2023 json-Auswertung (Anpass. an ZDF_FlatListEpisodes)
#
def do_sync(list_title, strmpath, list_path, strm_type):
	PLog("do_sync:")
	PLog("synchronisiere: %s, %s" % (list_title, strmpath))
	
	from ardundzdf import ZDF_FlatListRec, ZDF_getApiStreams
	icon = R("icon-strmtools.png")
	
	err=''
	page, msg = get_page(path=list_path)
	if page == '':
		err = msg
	if os.path.exists(strmpath) == False:
		err = "Zielverzeichnis fehlt"
	if err:
		msg1 = u"Abgleich fehlgeschlagen"
		msg2 = err
		line = "%6s | %15s | %s" % ("ERR", list_title[:15], err[:45])
		PLog(line)
		log_update(line)
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		return
		
	#-------------													# Blockmerkmale wie ZDF_FlatListEpisodes
	jsonObject = json.loads(page)
	PLog(str(jsonObject)[:80])
	season_id 	= jsonObject["document"]["id"]
	staffel_list = jsonObject["cluster"]							# Staffel-Blöcke
	PLog("staffel_list: %d" % len(staffel_list))
	
	cnt=0; skip_cnt=0;
	for staffel in 	staffel_list:
		if 	staffel["name"] == "":									# Teaser u.ä.
			continue							
		folgen = staffel["teaser"]									# Folgen-Blöcke	
		PLog("sync_Folgen: %d" % len(folgen))
		for folge in folgen:
			scms_id = folge["id"]
			try:
				brandId = folge["brandId"]
			except:
				brandId=""
			if season_id != brandId:
				PLog("skip_no_brandId: " + str(folge)[:60])
				continue
			title, url, img, tag, summ, season, weburl = ZDF_FlatListRec(folge) # Datensatz
			if season == '':
				continue
	
			fname = make_filenames(title)							# Zieldatei hier ohne Dialog
			PLog("fname: " + fname)
			if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
				f = os.path.join(strmpath, fname, "%s.nfo" % fname)
			else:
				f = os.path.join(strmpath, "%s.nfo" % fname)
			PLog("f: " + f)
			if os.path.isfile(f):									# skip vorh. strm-Bundle
				PLog("skip_bundle: " + f)
				skip_cnt=skip_cnt+1
				continue
			else:
				PLog('strm_Bündel_neu:')
				
			open(FLAG_OnlyUrl, 'w').close()							# Flag PlayVideo_Direct: kein Videostart
			ZDF_getApiStreams(url, title, img, tag,  summ, gui=False) # Streamlisten bauen, Ablage Url
			url = RLoad(STRM_URL, abs_path=True)					# abgelegt von PlayVideo_Direct
			PLog("strm_Url: " + str(url))
			
			Plot = "%s\n\n%s" % (tag, summ)
			ret = xbmcvfs_store(strmpath, url, img, fname, title, Plot, weburl, strm_type)
			if ret:
				cnt=cnt+1
				line = "%6s | %15s | %s..." % ("NEU", list_title[:15], title[:45])
				log_update(line)
	
	line = "%6s | %15s | %s" % ("CHECK1", list_title[:15], strm_type)
	log_update(line)	
	clear_cnt = do_clear(list_title, strmpath, strm_type, page)			# Check entfallene Folgen	
		
	return

# ----------------------------------------------------------------------
# prüft auf entfallene Folgen (Log: Check2)
# für ARD und ZDF (do_sync, do_sync_ARD)
def do_clear(list_title, strmpath, strm_type, page):
	PLog("do_clear: " + list_title)
	
	dirs = next(os.walk(strmpath))[1]
	cnt=0
	for d in dirs:
		nfo =  os.path.join(strmpath, d, "%s.nfo" % d)		# Bsp. S03_F05_Kiezliebe/S03_F05_Kiezliebe.nfo
		PLog("nfo: " + nfo)
		if os.path.exists(nfo):
			nfo_page = RLoad(nfo, abs_path=True)
			weburl = stringextract('<weburl>', '</weburl>', nfo_page)
			title = d.split("/")[-1]						# Bsp. S03_F05_Kiezliebe
			if len(weburl) and weburl.startswith("http"):
				webid = weburl.split("/")[-1]				# Bsp. kiezliebe-100.html
				PLog("webid: " + webid)
				if page.find(webid) < 0:
					rm_strmdir = os.path.join(strmpath, d)
					PLog('rm_strmdir: ' + rm_strmdir)
					shutil.rmtree(rm_strmdir, ignore_errors=True)
					cnt=cnt+1
					line = "%6s | %15s | %s" % ("CLEAR",  list_title[:15], title[:45])
					log_update(line)

	if cnt == 0:
		line = "%6s | %15s | %s" % ("CHECK2", list_title[:15], strm_type)
		log_update(line)
		
	return	
		
# ----------------------------------------------------------------------
# neue Folgen aufnehmen (Log: Check1) - ähnlich do_sync für ZDF
# Aufrufer: Monitor strm_sync
# strmpath: lokale strm-Ablage
# import ARD_FlatListRec + ARD_get_strmStream hier wg. Rekursion im Modul-
#	kopf (Thread strm_sync)
#
def do_sync_ARD(list_title, strmpath, list_path, strm_type):
	PLog("do_sync_ARD:")
	PLog("synchronisiere: %s" % list_title)
	from resources.lib.ARDnew import ARD_FlatListRec, ARD_get_strmStream
	icon = R("icon-strmtools.png")
	
	page, msg = get_page(path=list_path)
	if page == '':
		msg1 = u"Abgleich fehlgeschlagen"
		msg2 = msg
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		line = "%6s | %15s | %s" % ("ERR", list_title[:15], msg[:45])
		log_update(line)
		return
		
	#-------------												# Versionserkenung
	line = Dict("load", 'strmListVersion_%s' % list_title)		# stored: ARD_getStrmList
	vers='' 						
	if line != False:
		Dict("store", 'strmListVersion_%s' % list_title, line)	# Schutz vor Cache-Bereinigung
		vers = line.split("|")[-1]
	else: 
		err = "Liste fehlt im Cache"
		line = "%6s | %15s | %s" % ("ERR", list_title[:15], err[:45])
		log_update(line)
		return	
	PLog("versions_detect: " + vers)							# Default: Normalfassung
	
	#-------------												# Blockmerkmale != ZDF_FlatListEpisodes
	cnt=0; skip_cnt=0;
	items = blockextract('availableTo":', page)					# Videos
	for item in items:
		if "Folge " in item == False:
			continue
		title, url, img, tag, summ, season, weburl, ID = ARD_FlatListRec(item, vers) # Datensatz
		if title == '':											# skipped
			continue
		
		fname = make_filenames(title)							# Zieldatei hier ohne Dialog
		PLog("fname: " + fname)
		if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
			f = os.path.join(strmpath, fname, "%s.nfo" % fname)
		else:
			f = os.path.join(strmpath, "%s.nfo" % fname)
		PLog("f: " + f)
		if os.path.isfile(f):									# skip vorh. strm-Bundle
			PLog("skip_bundle: " + f)
			skip_cnt=skip_cnt+1
			continue
		else:
			PLog('strm_Bündel_neu:')
				
		Plot = "%s\n\n%s" % (tag, summ)
		open(FLAG_OnlyUrl, 'w').close()							# Flag PlayVideo_Direct: kein Videostart
		ARD_get_strmStream(url, title, img, Plot) 				# Streamlisten bauen, Ablage Url
		url = RLoad(STRM_URL, abs_path=True)					# abgelegt von PlayVideo_Direct
		PLog("strm_Url: " + str(url))
		
		ret = xbmcvfs_store(strmpath, url, img, fname, title, Plot, weburl, strm_type)
		if ret:
			cnt=cnt+1
			line = "%6s | %15s | %s..." % ("NEU", list_title[:15], title[:45])
			log_update(line)
	
	line = "%6s | %15s | %s" % ("CHECK1", list_title[:15], strm_type)
	log_update(line)	
	clear_cnt = do_clear(list_title, strmpath, strm_type, page)			# Check entfallene Folgen	
		
	return

# ----------------------------------------------------------------------
########################################################################		
# ----------------------------------------------------------------------
# listet die Beiträge eines strm-Verzeichnisses:
# Aufruf strm_tools (7)
# strm-Bündel je nach Setting mit/ohne Unterverzeichnis in
#	strmpath
# mediatype="video" hier unabhängig vom Setting (nur 1 Url in strm)
# Rückkehr zur Liste nach play oder Rückkehr zu Info/strm-Tools
# 12.03.2022 Abgleich Video mit MyVideos*.db + ggfls. Kennzeichnung
#	 (Setting pref_skip_played_strm)
# 06.01.2024  DB-Connect ausgelagert (util)
#
def show_strm_element(strmpath):
	PLog('show_strm_element: ' + strmpath)

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)						# Home-Button

	dir_cnt = sum([len(dirs) for root, dirs, files in os.walk(strmpath)])
	file_cnt = sum([len(files) for root, dirs, files in os.walk(strmpath)])
	PLog("dir_cnt: %d, file_cnt: %d" % (dir_cnt, file_cnt))

	# json_rpc- Altern. für sqlite3 (s. Funktion json_rpc) - Test OK,
	#	nicht genutzt: 
	'''
	params = {"filter": {"field": "playcount", "operator": "is", "value": "0"}, "limits": { "start" : 0, "end": 1000 }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"]}
	obj = json_rpc("VideoLibrary.GetMovies", params)
	PLog(type(obj))
	PLog(str(obj)[:400])
	movie = obj["movies"][0]
	PLog(movie)
	'''
	cur = get_sqlite_Cursor("MyVideos")				# DB-Connect
	
	strm_files=[]
	# Anzahl Unterverzeichnissen abhängig von Setting pref_strm_uz
	#	(0 falls AUS):
	for root, dirs, files in os.walk(strmpath, topdown=True):
		for f in files:
			fname = os.path.join(root, f)
			strm_files.append(fname)
	strm_files.sort(reverse=True)					# absteigend wie abgelegt
			
	max_len =  len(strm_files)
	PLog("strm_files: %d" % max_len)		
	for i in range(0,max_len, 3):					# Bündel abklappern
		dir_list=[]
		dir_list.append(strm_files[i]); 
		dir_list.append(strm_files[i+1]); 
		dir_list.append(strm_files[i+2]); 
		PLog(dir_list); 
		url=''; img=''; title=''; tag=''; Plot=''; fname_strm=''
		for fname in dir_list:						# 1 Bündel auswerten
			PLog("fname: " + fname)
			if fname.endswith(".strm"):
				url = RLoad(fname, abs_path=True)
				fname_strm = fname
			if fname.endswith(".nfo"):
				page = RLoad(fname, abs_path=True)
				title = stringextract('<title>', '</title>', page)
				tag = stringextract('<plot>', '</plot>', page)
				Plot = tag.replace("\n", "||")		
			if fname.endswith(".jpeg"):
				img = fname
				
		#--------------------	
		if SETTINGS.getSetting('pref_skip_played_strm') == 'true':	# Abgleich PlayCount in Video-DB
			# Tabs/Felder MyVideos*.db: kodi.wiki/view/Databases/MyVideos
			surl = quote_plus(url)						
			try:
				cur.execute("SELECT strFilename, PlayCount FROM files WHERE strFilename like ?", ('%'+surl+'%',))
				rows = cur.fetchall()
			except Exception as exception:
				rows=[]
				PLog("cursor_exception: " + str(exception))
			PLog("db_rows: %d" % len(rows))
			
			playcount=""
			# Abgleich img-Pfad - Video kann mehrfach abgelegt sein, dirID=PlayVideo zählt
			for row in rows:
				action = unquote_plus(row[0])			# Plugin-Call
				playcount = row[1]						# None, 1,2..
				if "dirID=PlayVideo" in action and img in action:
					PLog(action)
					PLog("playcount: " + str(playcount))
					break
			if playcount:
				PLog("skip: %s | %s" % (title, fname_strm))
				continue
		#--------------------		
			
		PLog("Satz:")
		PLog(title); PLog(img); PLog(url); PLog(tag[:80]);
		title=py2_encode(title); img=py2_encode(img); 
		tag=py2_encode(tag);  url=py2_encode(url); 
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
			(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
			thumb=img, fparams=fparams, mediatype="video", tagline=tag) 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

######################################################################## 			
# Monitoring strm-Verzeichnisse via Verzeichnisliste
# Verzeichnisliste: STRM_SYNCLIST (strmsynclist)
# Setting sync_hour: STRM_TOOLS_SET (strmtoolset)
# Aufruf beim Start Haupt-PRG (nach EPG + DL_CHECK), Lockdatei 
#	STRM_CHECK (strm_check_alive) - kann nach Kodi-Ende stehenbleiben,
#	Leichen-Behandl. durch Haupt-PRG.	
#
def strm_sync():
	PLog('strm_sync:')
	xbmc.sleep(1000)							# Pause für Datei-OP durch Haupt-PRG		
			
	open(STRM_CHECK, 'w').close()				# Lock strm_check_alive anlegen
	PLog("strm_check_alive_angelegt")
	icon = R(ICON_DIR_STRM)
	sync_hour = strm_tool_set(mode="load")		# Setting laden (Default 12 Std.)
	PLog("sync_hour: %s Std." % sync_hour)
	sync_sec = int(sync_hour) * 60 * 60			# * min * sec
	# sync_sec = 60 * 5	# Debug	5min
	
	next_sync = int(time.time()) + sync_sec		# erster Abgleich ab hier
	dt = datetime.datetime.now()
	PLog("strm_sync_started: %s" % dt.strftime("%Y-%m-%d_%H-%M-%S"))
	PLog("sync_sec: %d sec" % sync_sec)
	
	dt = datetime.datetime.fromtimestamp(int(next_sync)) # Ablage next_sync für Tools
	next_strm_sync = dt.strftime("%d.%m.%Y, %H:%M:%S")
	Dict("store", "next_strm_sync", next_strm_sync)

	
	monitor = xbmc.Monitor()
	i=0
	while not monitor.abortRequested():			# Abbruch durch Kodi
		if os.path.exists(STRM_CHECK) == False:	# Kodi-Abbruch od. Leiche entfernt
			PLog("strm_check_alive_stop")
			break
		if os.path.exists('strmsync_stop') == True:	# Tools-Abbruch 
			PLog("strmsync_stop_from_tools")
			break
			
		now = int(time.time()); checking=False
		if now >= next_sync:
			dt = datetime.datetime.fromtimestamp(int(now))
			PLog("sync_strm_%d. %s" % (i+1, dt.strftime("%Y-%m-%d_%H-%M-%S")))
			next_sync = int(time.time()) + sync_sec	# nächster Abgleich ab hier
			
			dt = datetime.datetime.fromtimestamp(int(next_sync)) # Ablage next_sync für Tools
			next_strm_sync = dt.strftime("%d.%m.%Y, %H:%M:%S")
			Dict("store", "next_strm_sync", next_strm_sync)
			
			if os.path.exists(STRM_SYNCLIST):	# Listenabgleich
				synclist = strm_synclist(mode="load")				
				for item in synclist:
					# checking = True
					PLog("sync_item: " + item)
					# Format: Listen-Titel ## lokale strm-Ablage ##  ext.Url ## strm_type
					list_title, strmpath, list_path, strm_type= item.split("##")
					if "//zdf-cdn" in list_path or "mediathekV2" in list_path:		# ZDF-Sync
						do_sync(list_title, strmpath, list_path, strm_type)
					else:
						do_sync_ARD(list_title, strmpath, list_path, strm_type)		# ARD-Sync
				# checking=False					# interner Lock, nicht genutzt
					
			#os.remove(STRM_CHECK)	# Debug-Stop		
			i=i+1
		xbmc.sleep(2000)						# > 2sec: Entfernung Lock nicht sicher 
		if os.path.exists(STRM_CHECK) == True: 	# Aktualisierung (nur falls strm_tools nicht entfernt),
			open(STRM_CHECK, 'w').close()		#	exist-Check für langsame Systeme erforderl.
		# PLog("strm_sync_running")	# Debug-Ping
	

	PLog('strm_sync_stop')
	#--------------------------					# Abbruch durch Addon oder Kodi
	if os.path.exists(STRM_CHECK):		
		os.remove(STRM_CHECK)					# Lock strm_check_alive entfernen
		PLog("strm_check_alive_entfernt")
	if os.path.exists('strmsync_stop'):			# Stop-Flag strmsync_stop entfernen
		os.remove('strmsync_stop')	
		PLog("strmsync_stop_entfernt")

	return

# ----------------------------------------------------------------------
# json-rpc-Call - s. https://kodi.wiki/view/JSON-RPC_API/Examples,
# 					https://kodi.wiki/index.php?title=JSON-RPC_API#Examples
def json_rpc(method, params=''):
	PLog('json_rpc:')
	PLog(method); 

	request_data = {'jsonrpc': '2.0', 'method': method, 'id': 1,
					'params': params or {}}
	request = json.dumps(request_data)
	PLog("json_rpc_call: %s" % request)
	page = xbmc.executeJSONRPC(request)
	
	page = page.replace('\udcf6', '')		# isolated surrogate
	page = page.replace('\udcfc', '')		# isolated surrogate

	obj = json.loads(page)
	if 'error' in obj:
		raise IOError('json_rpc_error {}: {}' .format(page['error']['code'],
			page['error']['message']))
			
	return obj['result'] 
	
# ----------------------------------------------------------------------
# prüft Vorkommen von Titel in Medienbibliothek via rpc_json-Call
# Rückgabe: Dateiliste
# Altern.: sqlite3-Call MyVideos119.db (Matrix), Tab movie, Feld c00
# Hinw.: Anpassung des Titels (clear_titel) wegen mögl. Änderungen 
#	der Titel durch das Addon (z.B. bei Serien)
#	 
#  	
def exist_in_library(title):
	PLog("exist_in_library:")
	title_raw = title
	PLog("title_raw: %s" % title_raw)
	max_anz = 1000							# Anpassung s.u. 
	
	title = clear_titel(title)				# Markierungen entfernen
	PLog("title: %s" % title)

	#params = {"filter": {"field": "playcount", "operator": "is", "value": "0"}, "limits": { "start" : 0, "end": max_anz }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"]}
	params = {"limits": { "start" : 0, "end": max_anz }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"]}
	result = json_rpc("VideoLibrary.GetMovies", params)
	PLog(type(result))
	PLog(str(result)[:100])
	total = result["limits"]["total"]
	PLog("total: " + str(total))
	if total > max_anz:						# Anpassung an tats.  Umfang
		PLog("new_rpc_with_total: %d statt %d" % (total, max_anz))
		params = {"limits": { "start" : 0, "end": total }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"]}
		result = json_rpc("VideoLibrary.GetMovies", params)

	movies = result['movies']		# type list	
	PLog(str(movies)[:100])
	PLog("movies: %d" % len(movies))
	if 	len(movies) > 0:
		PLog(movies[0])
	#PLog(title in str(movies))		# Debug
	
	hit_list=[]
	for movie in movies:
		#if "Prima Klima" in str(movie):	# Debug
		#	PLog(str(movie))
		label = movie["label"]				# hier Markierungen beibehalten
		#PLog(label)	# Debug
		if title in label:
			playcount = movie["playcount"]
			path = movie["file"]
			line = "%s##%s##%s" % (title, playcount, path)
			hit_list.append(line)
			
	cnt = len(hit_list)
	PLog("cnt: %d" % cnt)
	if cnt == 0:							# Abgleich negativ: notification
		msg1 = "Abgleich Video"
		msg2 = "Video nicht in MyVideos-Datenbank"
		icon = R('Dir-video.png')
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		return

	# Verzicht auf playcount (hier nur relevant für Bibliothek, nicht für Abrufe im
	#	Internet)
	PLog(str(hit_list))						# Abgleich positiv: Liste zeigen mit File-Check
	my_list=[]
	for item in hit_list:
		title,playcount, path = item.split("##")
		fchk = "nein"
		if os.path.exists(path):
			fchk = "ja"
		#  line = "%74s | %d | %s" % (path[:60], int(playcount), fchk)
		line = "%74s | %s" % (path[:60],  fchk)
		my_list.append(line)
	header = "%s: Video existiert %d mal" % (title_raw[:50], len(my_list))
	textlist =  "\n".join(my_list)
	xbmcgui.Dialog().textviewer(header, textlist,usemono=True)
	return

# ----------------------------------------------------------------------
# entfernt Markierungen (fett, Color, Zeit, Serienmark.)
def clear_titel(title):
	title = cleanmark(title)				# Markierungen entf.
	pos = title.find("|")
	#PLog("pos: %d" % pos)
	if pos == 7:							# Serienmark. strm-Listen (ZDF-api)
		title = title[pos+2:]				# Bsp.: S02E10 | Prima Klima
	if pos == 10:							# Zeitangabe aus Verpasst entf.
		title = title[pos+2:]				# Bsp.: 20:15 Uhr | Heute 
		
	pos = title.find(" : ")					# Serienmark. ZDF-Beiträge (Web)
	if pos:									# Bsp.: Friesland : Krabbenkrieg
		title = title[pos+3:]
	#PLog(title)
	return title
	
# ----------------------------------------------------------------------


	









