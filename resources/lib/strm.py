# -*- coding: utf-8 -*-
################################################################################
#				strm.py - Teil von Kodi-Addon-ARDundZDF
#			 Erzeugung von strm-Dateien für Kodi's Medienverwaltung
################################################################################
# 	<nr>9</nr>										# Numerierung für Einzelupdate
#	Stand: 30.01.2022
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

HANDLE			= int(sys.argv[1])
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
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
NFO4 = '<plot>%s</plot>\n<weburl>%s</weburl>\n</movie>'					#Tag weburl (inoff.) für Abgleich
NFO = NFO1+NFO2+NFO3+NFO4												#	 vor./nicht mehr vorh.
									

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
		
	while(1):
		add_log=''	
		msg1 = u'Monitorreset'
		msg2 = u"für strm-Tools"
		sync_hour = strm_tool_set(mode="load")	# Setting laden
		
		# Tools verlassen: Haupt-PRG startet Monitor neu
		tmenu = [ u"Abgleichintervall | %s Stunden | Tools verlassen" % sync_hour, u"Liste anzeigen", 
					u"Listeneinträge löschen", u"Monitor-Reset | Tools verlassen", 
					u"strm-Log anzeigen", u"einzelne Liste jetzt abgleichen",
					u"unterstützte Sender / Beiträge",
				]
		head = "strm-Tools"
		ret = xbmcgui.Dialog().select(head, tmenu)
		PLog(ret)	
		if ret == None or ret == -1:
			InfoAndFilter()							# provoz. network_error (return -> ..) 							
			
		if ret == 0:								# Zeitintervall
			PLog("set_val")
			valmenu = ["6", "12", "24", "36",]
			head = "Zeitintervall in Stunden"
			ret0 = xbmcgui.Dialog().select(head, valmenu)
			PLog(ret)	
			if ret0 >= 0:							
				dt = datetime.datetime.now()
				logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
				sync_hour = valmenu[ret]
				strm_tool_set(mode="save", index=0, val=sync_hour)
				if os.path.exists(STRM_CHECK):
					os.remove(STRM_CHECK)			# Monitorreset
				xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
				add_log = "%s | %6s | %15s | %s" % (logtime, "TIME", "strm-Tools", "Intervall: %s Stunden" % sync_hour)
			
				
		if ret == 1 or  ret == 2 or  ret == 5:		# Liste anzeigen / löschen / abgleichen
			PLog("show_list")
			title = u"zum Abgleich gewählte strm-Listen"
			if os.path.exists(STRM_SYNCLIST):		# Listenabgleich
				mylist1=[]; mylist2=[]				# 2 Listen (textviewer, select)
				synclist = strm_synclist(mode="load")
				for line in synclist:
					list_title,strmpath,list_path,strm_type = line.split("##")
					mylist1.append(u"%15s | %40s... | %s" % (list_title, strmpath[:60], strm_type))
					mylist2.append(u"%15s | %s" % (list_title, strm_type))
			else:
				msg1 = u'Liste fehlt'
				msg2 = u"keine Abgleichliste gefunden"
				xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
				continue
				
			if ret == 1:							# Liste anzeigen
				mylist1 =  "\n".join(mylist1)
				xbmcgui.Dialog().textviewer(title, mylist1,usemono=True)	
			if ret == 2:							# Listeneinträge löschen
				title = u"Listeneintrag löschen"
				ret1 = xbmcgui.Dialog().select(title, mylist2)
				PLog(ret1)
				if ret1 >= 0:
					msg1 = u"Eintrag aus Abgleichliste wirklich entfernen?"
					msg2 = mylist2[ret1]
					ret2 = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
					if ret2 == 1:
						item = synclist[ret1]
						synclist.remove(item)
						synclist =  "\n".join(synclist)
						msg = RSave(STRM_SYNCLIST, py2_encode(synclist))
						msg=''
						if msg == '':
							dt = datetime.datetime.now()
							logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
							msg1 = u"Listeneintrag"
							msg2 = u"gelöscht"
							xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
							add_log = "%s | %6s | %15s | %s" % (logtime, "DELETE", "strm-Tools", item[:15])

			
		if ret == 3:								# Monitorreset			
			PLog("set_reset")
			dt = datetime.datetime.now()
			logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
			if os.path.exists(STRM_CHECK):
				os.remove(STRM_CHECK)			
			xbmcgui.Dialog().notification(msg1,msg2,icon,2000,sound=True)
			add_log = "%s | %6s | %15s | %s" % (logtime, "RESET", "strm-Tools", "Monitor-Reset")
			
		if ret == 4:								# strm-Log anzeigen			
			PLog("strm_log_show")
			log_show()
						
		if ret == 5:								# einzelne Liste abgleichen
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
					do_sync(list_title, strmpath, list_path, strm_type)
					log_show()						# Log anzeigen
			

		if ret == 6:								# unterstützte Sender/Beiträge
			msg1 = u"zur Zeit werden nur ZDF-Serien für strm-Listen unterstützt"
			msg2 = u'erkennbar am Button:\n[B]strm-Dateien für die komplette Liste erzeugen[/B]'
			MyDialog(msg1, msg2, msg3='')
			

		#-----------------							# Aktualisierung strm-Log
		PLog("strm_log_update")
		save_log=False
		max_lines = 100
		dt = datetime.datetime.now()
		logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
		loglist=[]
		if os.path.exists(STRM_LOGLIST):			# Log laden
			loglist = RLoad(STRM_LOGLIST, abs_path=True)
			loglist = loglist.splitlines()
			if len(loglist) >= max_lines:
				loglist = loglist[max_lines-1]
				save_log=True

		loglist =  "\n".join(loglist)
		if add_log:									# z.B.: "RESET"		
			loglist = "%s\n%s" % (loglist, add_log)
			save_log=True
		if save_log:								# Log aktualisieren
			log_save(loglist.strip())
		if ret == 3 or ret == 0:
			InfoAndFilter()
				
	return	
# ----------------------------
# Anzeige strm-Log 
def log_show():	
	PLog("log_show:")
	if os.path.exists(STRM_LOGLIST):
		loglist = RLoad(STRM_LOGLIST, abs_path=True)
		loglist = loglist.splitlines()
		mylist=[]
		for line in loglist:
			mylist.append(u"%s..." % line[:80])
		mylist.sort(reverse=True)			# absteigend				
		mylist =  "\n".join(mylist)
		xbmcgui.Dialog().textviewer("strm-Log", mylist,usemono=True)	
	return	
		
# ----------------------------
# Speichern strm-Log mit Lock 
# loglist: Textformat
def log_save(loglist):	
	PLog("log_save:")
	maxloops	= 10				# 1 sec bei 10 x xbmc.sleep(100)	
	
	lockfile = os.path.join(ADDON_DATA, "strmloglock")
	PLog(lockfile) 
	while os.path.exists(lockfile):	
		i=i+1
		if i >= maxloops:		# Lock brechen, vermutl. Ruine
			os.remove(lockfile)
			PLog("doLock_break: " + lockfile)
			break
		xbmc.sleep(100)	
	
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
def xbmcvfs_store(strmpath, url, thumb, fname, title, Plot, weburl, strm_type, gui=True):
	PLog("xbmcvfs_store:")
	PLog("strmpath: " + strmpath)
	
	if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
		strmpath = os.path.join(strmpath, fname)	# STRMSTORE + fname
		if os.path.isdir(strmpath) == False:		# Verz. erzeugen, falls noch nicht vorh.
			os.mkdir(strmpath)
	
	if thumb:
		xbmcvfs_icon = os.path.join(strmpath, "%s.jpeg" % fname)
		PLog("xbmcvfs_icon: " + xbmcvfs_icon)
		urlretrieve(thumb, xbmcvfs_icon)

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
#
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
	PLog("strm_HLS_List: " + str(HLS_List[:100]))
	MP4_List =  Dict("load", "%s_MP4_List" % ID)
	PLog("strm_MP4_List: " + str(MP4_List[:100]))
	
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
	Source_Funcs = [u"dirID=ZDF|ZDF", u"ARDnew.ARDStartSingle|ARDNEU",	# Funktionen + ID's
					u"my3Sat.SingleBeitrag|3sat", u'.XLGetSourcesPlayer|TXL',
					u"dirID=PlayVideo|PlayVideo"
					]
	ID=''												# derzeit nicht ermittelbar
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
	PLog("get_strm_synclist:")	
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
	PLog("get_strm_tool_set:")
	sync_hour = "12"						# Default Intervall in Std.	
	
	toolset = RLoad(STRM_TOOLS_SET, abs_path=True)
	PLog(toolset[:60])
	toolset = toolset.splitlines()
	if len(toolset) == 0:					# Init mit Default sync_hour
		toolset.append(sync_hour)
	
	if mode == "load":
		sync_hour = toolset[0]
		sync_hour = sync_hour.strip()			# manuell geändert?
		return sync_hour

	if mode == "save":
		PLog(index); PLog(val)
		if val:
			toolset[index] = val
		toolset = "\n".join(toolset)
		RSave(STRM_TOOLS_SET, toolset)
		
	return
# ----------------------------------------------------------------------
# Check1: neue Folgen aufnehmen
# Aufrufer: Monitor strm_sync
# strmpath: lokale strm-Ablage
# import ZDF_FlatListRec + ZDF_getApiStreams hier wg. Rekursion im Modul-
#	kopf (Thread strm_sync)
#
def do_sync(list_title, strmpath, list_path, strm_type):
	PLog("do_sync:")
	PLog("synchronisiere: %s" % list_title)
	from ardundzdf import ZDF_FlatListRec, ZDF_getApiStreams
	
	loglist = RLoad(STRM_LOGLIST, abs_path=True)
	
	dt = datetime.datetime.now()
	logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")
	page, msg = get_page(path=list_path)
	if page == '':
		line = "%s | %6s | %15s | %s" % (logtime, "ERR", list_title, msg[:45])
		loglist = "%s\n%s" % (loglist, line)
		PLog(line)
		log_save(loglist.strip())
		return
		
	#-------------													# Blockmerkmale wie ZDF_FlatListEpisodes
	staffel_list = blockextract('"name":"Staffel ', page)			# Staffel-Blöcke
	staffel_list = staffel_list + blockextract('"name":"Alle Folgen', page, '"profile":')	
	if len(staffel_list) == 0:										# ohne Staffel-Blöcke
		staffel_list = blockextract('"headline":"', page)
	PLog("staffel_list: %d" % len(staffel_list))
	
	cnt=0; skip_cnt=0;
	for staffel in 	staffel_list:
		folgen = blockextract('"headline":"', staffel)				# Folgen-Blöcke	
		PLog("sync_Folgen: %d" % len(folgen))
		for folge in folgen:
			folge = folge.replace('\\/','/')
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
				line = "%s | %6s | %15s | %s..." % (logtime, "NEU", list_title, title[:45])
				loglist = "%s\n%s" % (loglist, line)
	
	line = "%s | %6s | %15s | %s" % (logtime, "CHECK1", list_title, strm_type)
	loglist = "%s\n%s" % (loglist, line)
	log_save(loglist.strip())
		
	clear_cnt = do_clear(list_title, strmpath, strm_type, page)			# Check entfallene Folgen	
		
	return

# ----------------------------------------------------------------------
# Check2: prüft auf entfallene Folgen
#
def do_clear(list_title, strmpath, strm_type, page):
	PLog("do_clear: " + list_title)
	
	loglist = RLoad(STRM_LOGLIST, abs_path=True)
	dt = datetime.datetime.now()
	logtime = dt.strftime("%Y-%m-%d_%H-%M-%S")

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
					line = "%s |  %6s | %15s | %s" % (logtime, "CLEAR",  list_title, title[:45])
					loglist = "%s\n%s" % (loglist, line)
					PLog(line)

	if cnt == 0:
		line = "%s | %6s | %15s | %s" % (logtime, "CHECK2", list_title, strm_type)
		loglist = "%s\n%s" % (loglist, line)
		PLog(line)
		
	log_save(loglist.strip())
				
	return	

######################################################################## 			
# Monitoring strm-Verzeichnisse via Verzeichnisliste
# Verzeichnisliste: STRM_SYNCLIST (strmsynclist)
# Setting sync_hour: STRM_TOOLS_SET (strmtoolset)
# Aufruf beim Start Haupt-PRG (nach EPG + DL_CHECK), Lockdatei 
#	STRM_CHECK (strm_check_alive)	
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
	
	monitor = xbmc.Monitor()
	i=0
	while not monitor.abortRequested():			# Abbruch durch Kodi
		if os.path.exists(STRM_CHECK) == False:	# Abbruch durch Addon (Lock fehlt)
			break
			
		now = int(time.time()); checking=False
		if now >= next_sync:
			dt = datetime.datetime.fromtimestamp(int(now))
			PLog("strm_%d. %s" % (i+1, dt.strftime("%Y-%m-%d_%H-%M-%S")))
			next_sync = int(time.time()) + sync_sec	# nächster Abgleich ab hier
			if os.path.exists(STRM_SYNCLIST):	# Listenabgleich
				synclist = strm_synclist(mode="load")				
				for item in synclist:
					# checking = True
					PLog("item: " + item)
					# Format: Listen-Titel ## lokale strm-Ablage ##  ext.Url ## strm_type
					list_title, strmpath, list_path, strm_type= item.split("##")
					do_sync(list_title, strmpath, list_path, strm_type)
				# checking=False					# interner Lock, nicht genutzt
					
			#os.remove(STRM_CHECK)	# Debug-Stop		
			i=i+1
		xbmc.sleep(2000)						# > 2sec: Entfernung Lock nicht sicher 
		# PLog("strm_sync_running")	# Debug-Ping	

	PLog('strm_sync_stop:')
	#--------------------------					# Abbruch durch Addon oder Kodi
	if os.path.exists(STRM_CHECK):		
		os.remove(STRM_CHECK)					# Lock strm_check_alive entfernen
		PLog("strm_check_alive_entfernt")

	return
# ----------------------------------------------------------------------
