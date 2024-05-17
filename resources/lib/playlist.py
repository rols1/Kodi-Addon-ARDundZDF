# -*- coding: utf-8 -*-
################################################################################
#				playlist.py - Teil von Kodi-Addon-ARDundZDF
#			 			Verwaltung der PLAYLIST
#	Kontextmenü s. addDir (Modul util)
################################################################################
# 	<nr>8</nr>										# Numerierung für Einzelupdate
#	Stand: 17.05.2024
#

from __future__ import absolute_import

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
import datetime, time
from threading import Thread	
import glob
	
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
from resources.lib.strm import get_streamurl					# s. PlayMonitor
import resources.lib.EPG as EPG


HANDLE			= int(sys.argv[1])
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('playlist_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLAYFILE		= os.path.join(ADDON_DATA, "playlist.xml") 
STARTLIST		= os.path.join(ADDON_DATA, "startlist") 		# Videoliste mit Datum ("Zuletzt gesehen")

PLAYLIST_ALIVE 	= os.path.join(ADDON_DATA, "playlist_alive")	# Lebendsignal für PlayMonitor (leer)
COUNT_STOP 	= os.path.join(ADDON_DATA, "count_stop")			# Stopsignal für Countdown-Thread (leer)
MENU_STOP		= os.path.join(ADDON_DATA, "menu_stop") 		# Stopsignal für Tools-Menü (Haupt-PRG)


ICON 			= 'icon.png'			# ARD + ZDF
ICON_PLAYLIST	= R("icon-playlist.png")

PLAY_TEMPL 		= u"<play>%s###%s###%s###%s###%s###%s</play>\n"	#  % (timestamp, title, add_url, thumb, Plot, status)

maxvideos = 100													# z.Z. noch fester Wert, nicht genutzt
PTITLE = "PLAYLIST ARDundZDF"
PLog('Script playlist.py geladen')

# ----------------------------------------------------------------------
def get_playlist():
	PLAYLIST=""
	if os.path.exists(PLAYFILE):			# PLAYLIST laden
		PLAYLIST = RLoad(PLAYFILE, abs_path=True)
		PLAYLIST = py2_encode(PLAYLIST.strip())
		
	new_list=[]; save_new = False
	for item in PLAYLIST.splitlines():
		if "###delete" in item:
			save_new = True
			continue
		else:
			new_list.append(item)
	
	new_list= "\n".join(new_list)
	if save_new:
		RSave(PLAYFILE, new_list)
	
	PLAYLIST = new_list
	PLog(len(PLAYLIST))		
	return PLAYLIST							# als string 
# ----------------------------------------------------------------------
#	Aufruf K-Menü (fparams_playlist_add, fparams_playlist_rm)
#	add_url, title, thumb + Plot in fparams zusätzlich quotiert
#	14.01.2021 playlist_play (Start außerhalb Tools-Menü)
# 	add_url wird weiter gereicht wie in addDir übergeben (quote_plus)
#
def items_add_rm(action, add_url='', title='', thumb='', Plot=''):		
	PLog('items_add_rm: ' + action)
	title = unquote_plus(title); thumb = unquote_plus(thumb); 
	Plot = unquote_plus(Plot);
	
	PLog(title); PLog(unquote_plus(add_url)[:80]); PLog(thumb); 
	PLog(Plot); 

	PLAYLIST = get_playlist()						# string
	new_url = add_url								# Abgleich mit STARTLIST
	msg2 = u"Eintrag hinzugefügt, Anzahl %s"
	#------------------
	if action == 'playlist_play':
		if len(PLAYLIST) > 0:
			play_list(u'PLAYLIST Direktstart')
		else:
			msg2 = u"keine Einträge gefunden"
			xbmcgui.Dialog().notification(msg1,msg2,ICON_PLAYLIST,3000)
			
		
	#------------------
	# Default: hinzufügen - bei Bedarf in Checks wieder entfernen.
	#	Die Liste wird immer neu gespeichert (delete-Bereinigung in
	#	get_playlist.
	if action == 'playlist_add':
		Plot=Plot.replace('\n', '||')
		timestamp = int(time.time())
		new_line = PLAY_TEMPL % (timestamp, title, new_url, thumb, Plot, 'neu')
		new_line = py2_encode(new_line)				# ohne: 'ascii' codec error 
		new_line = str(new_line)					# encode + str
		PLog("new_line: " + new_line)
		
		startlist=[]; check_exit=False; check_startlist=''
		if SETTINGS.getSetting('pref_check_with_startlist') == 'true':
			check_startlist = 'true'
			if os.path.exists(STARTLIST):			# Startlist laden
				check_exit=True
				startlist= RLoad(STARTLIST, abs_path=True)		
				startlist=py2_encode(startlist)
				startlist= startlist.strip().splitlines()
				PLog(len(startlist))
		
		do_add=True	
		if PLAYLIST.find(new_url) > 0:						# 1. Prio Doppler-Check 
			msg2 = u"existiert bereits, Anzahl %s"
			PLog("Beitrag doppelt: %s" % (new_url[:200]))
			do_add = False
			
		# Bsp. Live: zdf-hls-17.akamaized.net/hls/live/2016500/de/high/master.m3u8:
		if ".m3u8" in new_url and "/live/" in new_url:	# 2. Prio Livestream-Check 
			msg2 = u"Livestream verweigert, Anzahl %s"
			PLog("Livestream_url: %s" % (new_url))
			do_add = False
			
		if check_startlist == 'true' and do_add == True: # Abgleich mit <Zuletzt gesehen>-Liste			
			for start_item in startlist:
				if start_item.find(title) > 0:											# Abgleich mit titel in Plugin-Url
					ts, old_title, add_url, thumb, Plot = start_item.split('###')[:5]	# neues Format ab V 4.9.5
					ts = datetime.datetime.fromtimestamp(float(ts))
					ts = ts.strftime("%d.%m.%Y, %H:%M Uhr")
					g1 = u"[B]%s[/B]\nbereits gesehen am %s" % (title[:40], ts)
					g2 = u"trotzdem hinzufügen?"
					PLog("Beitrag in <Zuletzt gesehen>-Liste: %s, Datum: %s" % (title, ts))
					PLog("new_line %s" % (new_line[:80]))
					ret = MyDialog(msg1=g1, msg2=g2, msg3='', ok=False, cancel='Abbrechen', yes='JA', heading=PTITLE)
					PLog("ret: " + str(ret))
					if ret != 1: 
						do_add = False
						msg2 = u"Einfügen abgebrochen, Anzahl %s"
					else:
						pass					# msg2 wie eingangs
					break						# stop Abgleich immer
		
		if do_add:
			PLog("Mark0")
			PLog(len(PLAYLIST.splitlines()))
			if len(PLAYLIST.splitlines()) == 0:
				PLAYLIST = new_line				# add Beitrag
			else: 
				PLAYLIST = u"%s\n%s" % (PLAYLIST, new_line)		
			PLog(PLAYLIST[:40])
			RSave(PLAYFILE, PLAYLIST)
		
		cnt = len(PLAYLIST.splitlines())
		msg1 = PTITLE
		msg2 = msg2 % str(cnt)
		PLog(msg2)	
		xbmcgui.Dialog().notification(msg1,msg2,ICON_PLAYLIST,3000)

	#------------------
	if action == 'playlist_rm':
		PLog('playlist_rm:')
		msg2 = u"Eintrag gelöscht, Anzahl %s"
		deleted = False
			
		new_list=[]
		PLog(type(PLAYLIST))
		PLAYLIST = PLAYLIST.splitlines()
		for item in PLAYLIST:
			if item == '':								# sollte nicht vorkommen
				continue
			timestamp, title, add_url, thumb, Plot, status = item.split('###')
			if add_url in new_url:						# Fundstelle entfernen
				deleted = True
				continue
			new_list.append(item)
				
		new_list = "\n".join(new_list)			
		if deleted:
			RSave(PLAYFILE, new_list)		
		else:
			msg2 = u"Eintrag nicht gefunden, Anzahl %s"
	
		cnt = len(new_list.splitlines()) 
		msg2 = msg2 % str(cnt)
		PLog(msg2)	
		xbmcgui.Dialog().notification(PTITLE,msg2,ICON_PLAYLIST,3000)

# ----------------------------------------------------------------------
# Aufruf K-Menü (fparams_playlist_add), action nicht verwendet
# add_add_url, title, thumb + Plot in fparams zusätzlich quotiert
# 17.01.2020 MENU_STOP zur Verhind. von Rekursion nach zusätzl. Aufruf 
#	via Button im Info-Menü.
# 
def playlist_tools(action, add_url, title='', thumb='', Plot='', menu_stop=''):		
	PLog('playlist_tools:')
	add_url = unquote_plus(add_url); title = unquote_plus(title);  			
	thumb = unquote_plus(thumb); Plot = unquote_plus(Plot);
	# PLog(add_url); PLog(title); PLog(thumb); PLog(Plot);
	PLog(menu_stop) 
	PLAYLIST = get_playlist()
	
	if menu_stop == 'true':								# verhindert Rekurs. in start_script (Haupt-PRG)
		if os.path.exists(MENU_STOP):	
			return
		else:
			open(MENU_STOP, 'w').close()				# Entfernung in InfoAndFilter (Haupt-PRG)

	dialog = xbmcgui.Dialog()
	# bei Bedarf ergänzen: u"Liste endlos abspielen", u"Liste zufallgesteuert abspielen"
	#	(mode="endless", mode="random"):
	select_list = [	u"Liste abspielen", u"Liste abspielen ab .. (Startposition wählen)", 
					u"Liste zeigen", u"Liste komplett löschen", 
					u"einzelne Titel löschen", u"Abspielstatus in kompletter Liste auf >neu< setzen", 
					u"Liste ins Archiv verschieben", 
					u"Liste aus Archiv wiederherstellen", u"PLAYLIST-Tools verlassen"
				]

	if len(PLAYLIST) == 0:
		xbmcgui.Dialog().notification("PLAYLIST: ","noch leer",ICON_PLAYLIST,2000)
		# return											# Verbleib in Tools für get_archiv
	
	playing=False											# Flag							
	title = u"PLAYLIST-Tools"
	ret = dialog.select(title, select_list)					# Auswahl Tools
	PLog("ret: %d" % ret)
	if ret == -1 or ret == len(select_list):				# Tools-Menü verlassen
		return
		
	elif ret == 0 and len(PLAYLIST) > 0:
		playing =  play_list(title)							# PLAYLIST starten / Titel abspielen
	elif ret == 1 and len(PLAYLIST) > 0:
		playing =  play_list(title, mode="play_pos")		# PLAYLIST starten ab..
		
	elif ret == 2 and len(PLAYLIST) > 0:
		play_list(title, mode="show")						# PLAYLIST zeigen	
	elif ret == 3 and len(PLAYLIST) > 0:					# PLAYLIST kompl. löschen
		msg1 = u"PLAYLIST mit %d Titel(n) wirklich löschen?" % len(PLAYLIST.splitlines()) 
		ret4 = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbrechen', yes='JA', heading=title)
		if ret4 == 1:
			os.remove(PLAYFILE)	
			xbmcgui.Dialog().notification("PLAYLIST: ","gelöscht",ICON_PLAYLIST,2000)
	elif ret == 4 and len(PLAYLIST) > 0:
		play_list(title, mode="del_single")					# PLAYLIST Auswahl löschen
	elif ret == 5 and len(PLAYLIST) > 0:
		play_list(title, mode="set_status")					# Status auf >neu< setzen
	elif ret == 6 and len(PLAYLIST) > 0:
		play_list(title, mode="push_archiv")				# Liste in PLAYLIST-Archiv verschieben
	elif ret == 7:
		play_list(title, mode="get_archiv")					# Liste aus PLAYLIST-Archiv wiederherstellen
	elif ret == 8:											# Abbruch Liste
		return	

	if playing:												# return: Toolsliste ist modal (Vordergrund)
		return												# PlayMonitor startet nach Ende Tools neu											
		
	PLog("back_to_tools")
	playlist_tools(action='play_list', add_url='')			# zurück zu Tools

# ----------------------------------------------------------------------
def play_list(title, mode=''):		
	PLog('play_list:')
	PLog(mode)
	dialog = xbmcgui.Dialog()
	PLAYLIST = get_playlist()
	
	
	#----------------------------------------						# Beginn Abspielen	
	if mode == '' or  mode == 'play_pos':
		startpos=0

		if '###neu' not in PLAYLIST:
			msg1 = u"Alle Titel haben den Status >gesehen<."
			msg2 = u"Bitte neue Titel einfügen oder den Status auf >neu< setzen."
			MyDialog(msg1, msg2, '')
			return
		if SETTINGS.getSetting('pref_inputstream') == 'false':
			if "HLS" in SETTINGS.getSetting('pref_direct_format'):
				msg1 = u"Beim Videoformat HLS kann die letzte Abspielposition"
				msg2 = u"nur mit aktiviertem inputstream.adaptiv-Addon wiederhergestellt werden."
				MyDialog(msg1, msg2, '')
				
		if mode == 'play_pos':										# PLAYLIST starten ab Auswahlposition
			PLog('play_pos:')
			title_org = u"Abspielen - bitte die Startposition wählen:" 
			new_list = build_textlist(PLAYLIST, cut_title=60)				
			new_list = new_list.splitlines()						# Textliste zur Auswahl
			dial_ret = dialog.select(title_org, new_list)
			PLog(dial_ret)
			if dial_ret > -1:										# auch Pos. 0 erlaubt
				startpos = dial_ret
			else:
				return False
				
		if os.path.exists(PLAYLIST_ALIVE) == False:					# PlayMonitor läuft bereits?
			PLog('startpos: %d' % startpos)
			bg_thread = Thread(target=PlayMonitor,					# sonst Thread PlayMonitor starten
				args=[startpos])									# []: iterable
			bg_thread.start()
			xbmcgui.Dialog().notification("PLAYLIST: ","gestartet",ICON_PLAYLIST,3000)
		else:
			msg1 = u"PLAYLIST scheint bereits gestartet."
			msg2 = u"Signal entfernen und neu starten?"
			ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbrechen', yes='NEUSTART', heading=title)
			if ret ==1:
				if os.path.exists(PLAYLIST_ALIVE):					# Lebendsignal aus
					os.remove(PLAYLIST_ALIVE)
					play_list(title, mode='')						# neuer Startversuch
		return True
	#----------------------------------------						# Ende Abspielen	


	# alternativ als Kodi-Liste zeigen (dirID="PlayVideo")
	if mode == 'show':												# PLAYLIST zeigen
		PLog('show:')
		title_org = u"%s: aktuelle Liste" % title
		my_list = build_textlist(PLAYLIST)							# string
		dialog.textviewer(title_org, my_list, usemono=True)

	if mode == 'del_single':										# PLAYLIST Auswahl löschen
		PLog('del_single:')
		title_org = u"%s: einzelne Titel löschen" % title
		new_list = build_textlist(PLAYLIST, cut_title=60)				
		new_list = new_list.splitlines()							# Textliste zur Auswahl
		ret_list = dialog.multiselect(title_org, new_list)
		if ret_list !=  None:
			PLAYLIST = PLAYLIST.splitlines()
			if len(ret_list) > 0:									# gewählte Indices
				PLog(ret_list)
				ret_list = get_items_from_list(ret_list, PLAYLIST)	# Indices -> Listenelemente
				msg1 = u"Auswahl (%d Titel) wirklich löschen?" % len(ret_list)
				ret = MyDialog(msg1=msg1, msg2='', msg3='', ok=False,\
					cancel='Abbrechen', yes=u'LÖSCHEN', heading=title_org)
				if ret == 1:
					for item in ret_list:
						PLAYLIST.remove(item)
					new_cnt = len(PLAYLIST)
					new_list = "\n".join(PLAYLIST)
					RSave(PLAYFILE, new_list)					# geänderte PLAYLIST speichern		
					msg2 = u"gelöscht: %d, verbleibend: %d" % (len(ret_list), new_cnt)					
					xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,3000)

	# set_status löscht ev. vorh. Pos.-Angabe (sec)
	if mode == 'set_status':										# Status auf >neu< setzen
		PLog('set_status:')
		new_list = []
		PLAYLIST = PLAYLIST.splitlines()
		for item in PLAYLIST:
			pos = item.find("###neu ")								# Monitor:  "neu ab seek-Position" 
			if pos > 0:
				item = "%s%s</play>" % (item[:pos], "###neu")
				PLog(item)	
			new_list.append(item)		

		new_list = "\n".join(new_list)
		RSave(PLAYFILE, new_list)
		msg2 = u"Status auf >neu< gesetzt"					
		xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,3000)
	
	if mode == 'push_archiv':										# Liste in PLAYLIST-Archiv verschieben
		PLog('push_archiv:')
		msg1 = u"Soll die PLAYLIST wirklich ins Archiv verschoben werden?"
		ret = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbrechen',\
			yes='VERSCHIEBEN', heading=title)
		if ret == 1:
			query = get_keyboard_input(head=u'Bitte Dateinamen für diese PLAYLIST vergeben:') 
			if query == None or query.strip() == '': 				# None bei Abbruch
				pass
			else:
				valid_name = make_filenames(query)
				playfile = PLAYFILE.split(".xml")[0]				# Ext. entf.
				fname = "%s_%s" % (playfile, valid_name)			
				if os.path.exists(fname):
					msg1 = "%s existiert schon!" % valid_name
					xbmcgui.Dialog().notification("PLAYLIST: ",msg1,ICON_PLAYLIST,3000)	
				else:
					os.rename(PLAYFILE, fname)	
					msg1 = u"neu im Archiv: %s" % valid_name
					xbmcgui.Dialog().notification("PLAYLIST: ",msg1,ICON_PLAYLIST,3000)
		
	if mode == 'get_archiv':										# Liste aus PLAYLIST-Archiv wiederherstellen
		PLog('get_archiv:')
		archiv = get_archiv()
		PLog(archiv)
		if len(archiv) == 0:
			msg2 = u"PLAYLIST-Archiv noch leer"					
			xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,3000)
		else:
			my_list = []
			playfile = PLAYFILE.split(".xml")[0]	# Ext. entf.
			for item in archiv:
				sp = "%s_" % playfile				# Archivname abtrennen
				my_list.append(item.split(sp)[1])	#	Bsp.: ..data/playlist_mylist2
			title = u"Liste zur Wiederherstellung auswählen"
			ret = dialog.select(title, my_list)
			PLog(ret)
			if ret != -1:
				my_index=[]; my_index.append(ret)
				ret_list = get_items_from_list(my_index, archiv) # hier nur 1 Element
				PLog(ret_list)
				if len(ret_list) > 0:
					fname  = ret_list[0]
					if os.path.exists(PLAYFILE):	# alte PLAYLIST entf. 
						os.remove(PLAYFILE)
					try:
						os.rename(fname, PLAYFILE)
						msg1 = u"ist wiederhergestellt"
						xbmcgui.Dialog().notification("PLAYLIST:",msg1,ICON_PLAYLIST,3000)
					except Exception as exception:	
						PLog(str(exception))
						MyDialog("Dateifehler bei Wiederherstellung", str(exception), '')

	return		
		
# ----------------------------------------------------------------------
# Textliste der PLAYLIST erzeugen (string)
def build_textlist(PLAYLIST, cut_title=0):
	PLog('build_textlist:')
	
	new_list=[]
	cnt=1
	for item in PLAYLIST.splitlines():
		item = (item.replace("<play>", "").replace("</play>", ""))
		if item  == "":
			continue
		#PLog(item)		# Debug
		if u"###neu ab " in item:								# Seek-Sekunden -> Std.
			seekTime = re.search(r'###neu ab (\d+) sec', item).group(1)
			PLog(seekTime)
			if int(seekTime) > 3600:							# erst ab 1 Std.
				seekTime = seconds_translate(seekTime)
				pos = item.find("###neu ab")
				item = item[:pos] + "###neu ab %s Std." % seekTime
		
		timestamp, title, add_url, thumb, Plot, status = item.split('###')
		Plot=py2_decode(Plot); title=py2_decode(title); 
		
		PLog(title)
		if len(title) > 80:
			title = "%s.." % title[:80]
		my_line = u"[B]%s.[/B] %s" % (str(cnt).zfill(3), title) 
		if Plot:
			if len(Plot) > 80:
				title = "%s.." % Plot[:80]
			my_line = u"%s | %s" % (my_line, Plot)
		my_line = "%s | Status: %s" % (my_line, status) 
		my_line = my_line.replace('||||', ' | ')
		my_line = my_line.replace('| |', ' | ')
		
		if cut_title:											# Titel begrenzen (Auswahllisten)
			my_line = "%s.." % my_line[:cut_title]
			
		new_list.append(my_line)
		cnt = cnt+1
		
	new_list= "\n".join(new_list)
	new_list = py2_encode(new_list)
	return new_list
# ----------------------------------------------------------------------
# Liste der Archiv-Dateien
def get_archiv():
	PLog('get_archiv:')
	
	playfile = PLAYFILE.split(".xml")[0]				# Ext. entf.
	globPat = '%s_*' % playfile
	file_list = glob.glob(globPat)
	if PLAYLIST_ALIVE in file_list:
		file_list.remove(PLAYLIST_ALIVE)				# Lebendsignal (Ruine) ausschließen
	return file_list 									# leer falls keine Archivdateien vorh.
	
# ----------------------------------------------------------------------
# Thread für PLAYLIST, Aufruf play_list(mode='')
# Problem: beim direkten Aufruf von playlist_tools via Button puffert
#	das 1. Video fortlaufend und zeigt keine Bedienelemente, unabhängig
#	vom Param. windowed. OK beim Aufruf aus K-Menü. Gelöst mit vorge-
#	schalteter Startfunktion start_script (Haupt-PRG)
#
def PlayMonitor(startpos):
	PLog('PlayMonitor: ' + str(startpos))
	PLAYLIST = get_playlist()
	PLAYLIST = PLAYLIST.splitlines()	
		
	mtitle 		= u"PLAYLIST-Tools"
	PLAYDELAY 	= 10									# Sek.
	open(PLAYLIST_ALIVE, 'w').close()					# Lebendsignal ein - Abgleich play_list
	xbmc.sleep(1000)									# Start-Info abwarten
	monitor 	= xbmc.Monitor()
	player		= xbmc.Player()			
		
	del_val = SETTINGS.getSetting('pref_delete_viewed')	# default 75%
	del_val = re.search(r'(\d+)', del_val).group(1)
	del_val = int(del_val)
	PLog("del_val: %d" % del_val)
	
	cnt=0
	for cnt in range(len(PLAYLIST) - startpos):
		play_cnt = cnt + startpos
		item = PLAYLIST[play_cnt]				
		PLog(item[:80])
		seekTime = 0
									# Video seek-Point 
		item = py2_decode(item)
		if '###gesehen' in item:
			msg1 = "Titel %d schon gespielt" % play_cnt
			xbmcgui.Dialog().notification("PLAYLIST: ",msg1,ICON_PLAYLIST,2000)
			continue

		timestamp, title, add_url, thumb, Plot, status = item.split('###')
		if "neu ab" in status:
			seekTime = re.search(r'neu ab (\d+) sec', status).group(1)		# Seek-Pos. aus Playlist übernehmen
		PLog("Nr.: %s | %s | ab %s sec" % (play_cnt+1, title[:80], seekTime))
		msg2 = "Titel %d von %d" % (play_cnt+1, len(PLAYLIST))
		xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,2000)
		start_time = int(seekTime)
		
		# seek-Problem bei HLS-Streams o. EXT-X-ENDLIST tag- s. github.com/xbmc/xbmc/issues/18415
		#	(kein Problem mit inputstream.adaptiv-Addon)
		# Exception-Behandl. für nicht verfügb. Videos:
		timestamp, title, add_url, thumb, Plot, status = item.split('###')
		streamurl = get_streamurl(add_url)								# Streamurl ermitteln (strm-Modul)
		PLog("streamurl: " + streamurl)
		try:															#  playlist="true" = skip Startliste:
			play_time,video_dur = PlayVideo(streamurl, title, thumb, Plot, playlist="true", seekTime=seekTime)
		except Exception as exception:
			PLog(str(exception))
			continue
		percent=0; 														# noch nichts abgespielt
		
		while not monitor.waitForAbort(2):
			# Notification ev. ergänzen: player.getTotalTime(),
			if player.isPlaying():
				try:
					play_time = player.getTime()
				except:
					pass
			else:
				percent=0
				if play_time > 0 and video_dur > 0:
					play_time = play_time + 2			# Ausgleich Pause
					percent = 100 * (float(play_time) / float(video_dur))
					percent = int(round(percent))
				break
			xbmc.sleep(1000)

		PLog("start_time %d, play_time %d, video_dur %d, percent %d" %\
			(start_time,play_time,video_dur,percent))
														# Prozentabgleich mit Setting
		if percent >= del_val:							# mark: löschen							
			item = item.replace("###neu", "###delete")
			PLog('mark_delete: ' + item[:80])		
		else:											# mark: seek-Pos. (play_time)
			pos = item.find("###neu")
			play_time = max(0, (play_time-4))			# 4 sec Wiederholzeit
			item = item[:pos] + "###neu ab %d sec</play>" % play_time
			PLog('mark_gesehen: ' + item[:80])
		
		PLog(u"aktualisiere_item: %d, %s" % (play_cnt, title))
		PLAYLIST[play_cnt] = py2_encode(item)
		new_list = "\n".join(PLAYLIST)
		RSave(PLAYFILE, new_list)						# Lock erford. falls auf Share

		if play_cnt+2 > len(PLAYLIST):
			break

		msg1 = u"nächster PLAYLIST-Titel: %d von %d" % (play_cnt+2, len(PLAYLIST)) 
		msg2 = u"startet automatisch in %d sec." % PLAYDELAY
		msg3 = u"STOP beendet die PLAYLIST"
		PLog(msg1)
	
		sec=PLAYDELAY; title="PLAYLIST:"; icon=ICON_PLAYLIST
		bg_thread = Thread(target=CountDown, args=(sec, title, icon))# Notification-CountDown
		bg_thread.start()
		
		ret = MyDialog(msg1=msg1, msg2=msg2, msg3=msg3, ok=False, cancel='Weiter', \
			yes='STOP', heading=mtitle,autoclose=PLAYDELAY*1000)
		PLog("ret: %d" % ret)
		open(COUNT_STOP, 'w').close()
		if ret == 1:		# autoclose, cancel: 0
			player.stop()
			break
			
	xbmcgui.Dialog().notification("PLAYLIST: ","beendet",ICON_PLAYLIST,2000)					
	if os.path.exists(PLAYLIST_ALIVE):					# Lebendsignal aus
		os.remove(PLAYLIST_ALIVE)
		
	return playlist_tools(action='play_list', add_url='')			# zurück zu Tools

# ----------------------------------------------------------------------
# Notification-CountDown
def CountDown(sec, title, icon): 
	PLog('CountDown:')

	if os.path.exists(COUNT_STOP):						# gesetzt: PlayMonitor (break)
		os.remove(COUNT_STOP)
	cnt = int(sec)
	while sec:
		msg2 = "noch %d Sekunden" % sec
		xbmcgui.Dialog().notification(title,msg2,icon,1000)
		xbmc.sleep(1000)
		sec = sec-1
		if os.path.exists(COUNT_STOP):
			break
		
	return
# ----------------------------------------------------------------------





