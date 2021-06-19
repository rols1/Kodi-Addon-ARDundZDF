# -*- coding: utf-8 -*-
################################################################################
#				playlist.py - Teil von Kodi-Addon-ARDundZDF
#			 			Verwaltung der PLAYLIST
#	Kontextmenü s. addDir (Modul util)
################################################################################
#	Stand: 18.02.2021

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
import resources.lib.EPG as EPG


HANDLE			= int(sys.argv[1])
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLAYFILE		= os.path.join(ADDON_DATA, "playlist") 
STARTLIST		= os.path.join(ADDON_DATA, "startlist") 		# Videoliste mit Datum ("Zuletzt gesehen")

PLAYLIST_ALIVE 	= os.path.join(ADDON_DATA, "playlist_alive")	# Lebendsignal für PlayMonitor (leer)
COUNT_STOP 	= os.path.join(ADDON_DATA, "count_stop")			# Stopsignal für Countdown-Thread (leer)
MENU_STOP		= os.path.join(ADDON_DATA, "menu_stop") 		# Stopsignal für Tools-Menü (Haupt-PRG)


ICON 			= 'icon.png'			# ARD + ZDF
ICON_PLAYLIST	= R("icon-playlist.png")

PLAY_TEMPL 		= u"%s###%s###%s###%s###%s"	#  % (title, url, thumb, Plot, status)

maxvideos = 100							# z.Z. noch fester Wert
PTITLE = "PLAYLIST ARDundZDF"
PLog('Script playlist.py geladen')

# ----------------------------------------------------------------------
def get_playlist():
	PLAYLIST=[]
	if os.path.exists(PLAYFILE):			# PLAYLIST laden
		PLAYLIST = RLoad(PLAYFILE, abs_path=True)
		PLAYLIST = py2_encode(PLAYLIST)		
		PLAYLIST = PLAYLIST.strip().splitlines()
	PLog(len(PLAYLIST))
	
	new_list=[]; 							# Bereinigung + Formatcheck: vor V3.6.0 fehlt status
	save_new = False						#	in den Zeilen
	for item in PLAYLIST:	
		if '###neu' in item:
			new_list.append(item)
		else:
			save_new = True
	
	if save_new:							# altes Format überschreiben
		new_list= "\n".join(new_list)
		RSave(PLAYFILE, new_list)
			
	PLAYLIST = new_list
	return PLAYLIST
# ----------------------------------------------------------------------
#	Aufruf K-Menü (fparams_playlist_add, fparams_playlist_rm)
#	url, title, thumb + Plot in fparams zusätzlich quotiert
#	14.01.2021 playlist_play (Start außerhalb Tools-Menü)
#
def items_add_rm(action, url='', title='', thumb='', Plot=''):		
	PLog('items_add_rm: ' + action)
	url = unquote_plus(url); title = unquote_plus(title);  			
	thumb = unquote_plus(thumb); Plot = unquote_plus(Plot);
	PLog(action); PLog(url); PLog(title); PLog(thumb); PLog(Plot); 
	
	PLAYLIST = get_playlist()
	new_url = str(url)
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
		new_list = "\n".join(PLAYLIST)				# für schnellen Doppler-Check

		Plot=Plot.replace('\n', '||')
		new_line = PLAY_TEMPL % (title, url, thumb, Plot, 'neu')
		new_line = py2_encode(new_line)				# 'ascii' codec error ohne
		new_line = str(new_line)					# 	encode + str
		PLog("new_line: " + new_line)
		PLAYLIST.append(new_line)
		
		startlist=[]; check_exit=False
		check_startlist = SETTINGS.getSetting('pref_check_with_startlist')
		if check_startlist == 'true':
			if os.path.exists(STARTLIST):			# Startlist laden
				startlist= RLoad(STARTLIST, abs_path=True)		
				startlist=py2_encode(startlist)
				startlist= startlist.strip().splitlines()
				PLog(len(startlist))
		
		if new_url in new_list:						# 1. Prio Doppler-Check 
			PLAYLIST.remove(new_line)
			msg2 = u"existiert bereits, Anzahl %s"
			PLog("Doppler url: %s, new_url: %s" % (url, new_url))
			check_exit = True
			
		# Bsp. Live: zdf-hls-17.akamaized.net/hls/live/2016500/de/high/master.m3u8:
		if ".m3u8" in new_url and "/live/" in new_url:	# 2. Prio Livestream-Check 
			PLAYLIST.remove(new_line)
			msg2 = u"Livestream verweigert, Anzahl %s"
			PLog("Livestream_url: %s" % (new_url))
			check_exit = True
				
		if check_startlist == 'true' and check_exit == False: # Abgleich mit <Zuletzt gesehen>-Liste			
			for start_item in startlist:
				ts, title, start_url, thumb, Plot = start_item.split('###')
				if start_url == new_url:
					ts = datetime.datetime.fromtimestamp(float(ts))
					ts = ts.strftime("%d.%m.%Y, %H:%M Uhr")
					g1 = u"bereits gesehen am %s" % ts
					g2 = u"trotzdem hinzufügen?"
					PLog("url in <Zuletzt gesehen>-Liste: %s, Datum: %s" % (url, ts))
					PLog("new_url %s" % (new_url))
					ret = MyDialog(msg1=g1, msg2=g2, msg3='', ok=False, cancel='Abbrechen', yes='JA', heading=PTITLE)
					PLog("ret: " + str(ret))
					if ret != 1: 
						PLAYLIST.remove(new_line)
						msg2 = u"Einfügen abgebrochen, Anzahl %s"
					else:
						pass					# msg2 wie eingangs
					break						# stop Abgleich immer
		
		cnt = len(PLAYLIST)		
		new_list = "\n".join(PLAYLIST)
		RSave(PLAYFILE, new_list)
		msg2 = msg2 % str(cnt)
		PLog(msg2)	
		xbmcgui.Dialog().notification(PTITLE,msg2,ICON_PLAYLIST,3000)

	#------------------
	if action == 'playlist_rm':
		msg2 = u"Eintrag gelöscht, Anzahl %s"
		deleted = False
			
		for item in PLAYLIST:
			title, url, thumb, Plot, status = item.split('###')
			if url in new_url:						# Fundstelle entfernen
				PLAYLIST.remove(item)
				deleted = True
				break
				
		if deleted:
			new_list = "\n".join(PLAYLIST)
			RSave(PLAYFILE, new_list)		
		else:
			msg2 = u"Eintrag nicht gefunden, Anzahl %s"
	
		cnt = len(PLAYLIST)	
		msg2 = msg2 % str(cnt)
		PLog(msg2)	
		xbmcgui.Dialog().notification(PTITLE,msg2,ICON_PLAYLIST,3000)

# ----------------------------------------------------------------------
# Aufruf K-Menü (fparams_playlist_add), action nicht verwendet
# url, title, thumb + Plot in fparams zusätzlich quotiert
# 17.01.2020 MENU_STOP zur Verhind. von Rekursion nach zusätzl. Aufruf 
#	via Button im Info-Menü.
# 
def playlist_tools(action, url, title='', thumb='', Plot='', menu_stop=''):		
	PLog('playlist_tools:')
	url = unquote_plus(url); title = unquote_plus(title);  			
	thumb = unquote_plus(thumb); Plot = unquote_plus(Plot);
	# PLog(url); PLog(title); PLog(thumb); PLog(Plot);
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
	select_list = [	u"Liste abspielen", u"Liste zeigen", u"Liste komplett löschen", 
					u"einzelne Titel löschen", u"Status in kompletter Liste auf >neu< setzen", 
					u"Liste ins Archiv verschieben", 
					u"Liste aus Archiv wiederherstellen", u"Abbrechen"
				]

	if len(PLAYLIST) == 0:
		xbmcgui.Dialog().notification("PLAYLIST: ","noch leer",ICON_PLAYLIST,2000)
		# return											# Verbleib in Tools für get_archiv
	
	noloop=True
	title = u"PLAYLIST-Tools"
	ret = dialog.select(title, select_list)					# Auswahl Tools
	PLog("ret: %d" % ret)
	if ret == -1 or ret == len(select_list):				# Tools-Menü verlassen
		return
		
	elif ret == 0 and len(PLAYLIST) > 0:
		play_list(title)									# PLAYLIST starten / Titel abspielen
		return												# Tools-Menü verlassen
		
	elif ret == 1 and len(PLAYLIST) > 0:
		play_list(title, mode="show")						# PLAYLIST zeigen
	elif ret == 2 and len(PLAYLIST) > 0:					# PLAYLIST kompl. löschen
		msg1 = u"PLAYLIST mit %d Titel(n) wirklich löschen?" % len(PLAYLIST) 
		ret4 = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbrechen', yes='JA', heading=title)
		if ret4 == 1:
			os.remove(PLAYFILE)	
			xbmcgui.Dialog().notification("PLAYLIST: ","gelöscht",ICON_PLAYLIST,2000)
	elif ret == 3 and len(PLAYLIST) > 0:
		play_list(title, mode="del_single")					# PLAYLIST Auswahl löschen
	elif ret == 4 and len(PLAYLIST) > 0:
		play_list(title, mode="set_status")					# Status auf >neu< setzen
	elif ret == 5 and len(PLAYLIST) > 0:
		play_list(title, mode="push_archiv")				# Liste in PLAYLIST-Archiv verschieben
	elif ret == 6:
		play_list(title, mode="get_archiv")					# Liste aus PLAYLIST-Archiv wiederherstellen
	elif ret == 7:											# Abbruch Liste
		return	

	playlist_tools(action='play_list', url='')				# wieder zur Liste, auch nach PlayMonitor

# ----------------------------------------------------------------------
def play_list(title, mode=''):		
	PLog('play_list:')
	PLog(mode)
	dialog = xbmcgui.Dialog()
	PLAYLIST = get_playlist()
	
	if mode == '':													# PLAYLIST starten
		new_list = "\n".join(PLAYLIST)
		if '###neu' not in new_list:
			msg1 = u"Alle Titel haben den Status >gesehen<."
			msg2 = u"Bitte neue Titel aufnehmen oder den Status auf >neu< setzen."
			MyDialog(msg1, msg2, '')
			return
		
		if os.path.exists(PLAYLIST_ALIVE) == False:					# PlayMonitor läuft bereits?
			bg_thread = Thread(target=PlayMonitor,					# sonst Thread PlayMonitor starten
				args=())
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
		return

	# alternativ als Kodi-Liste zeigen (dirID="PlayVideo")
	if mode == 'show':												# PLAYLIST zeigen
		PLog('show:')
		title_org = u"%s: aktuelle Liste" % title
		new_list = []
		my_list = build_textlist(PLAYLIST)
		my_list = my_list.splitlines()								# Seek-Sekunden übersetzen
		for item in my_list:
			if "Status: neu ab" in item:
				seekTime = re.search(u'Status: neu ab (\d+) sec', item).group(1)
				if int(seekTime) > 3600:							# erst ab 1 Std.
					seekTime = seconds_translate(seekTime)
					pos = item.find("Status: neu ab")
					item = item[:pos] + "Status: neu ab %s" % seekTime
			new_list.append(item)
			 
		new_list= "\n".join(new_list)
		dialog.textviewer(title_org, new_list,usemono=True)

	# Param. "del_single" passt nicht mehr, bleibt aber unverändert 
	if mode == 'del_single':										# PLAYLIST Auswahl löschen
		PLog('del_single:')
		title_org = u"%s: einzelne Titel löschen" % title
		new_list = build_textlist(PLAYLIST)				
		new_list = new_list.splitlines()							# Textliste zur Auswahl
		ret_list = dialog.multiselect(title_org, new_list)
		if ret_list !=  None:
			if len(ret_list) > 0:									# gewählte Indices
				PLog(ret_list)
				ret_list = get_items_from_list(ret_list, PLAYLIST)	# Indices -> Listenelemente
				msg1 = u"Auswahl (%d Titel) wirklich löschen?" % len(ret_list)
				ret = MyDialog(msg1=msg1, msg2='', msg3='', ok=False,\
					cancel='Abbrechen', yes=u'LÖSCHEN', heading=title_org)
				if ret == 1:
					for item in ret_list:
						PLAYLIST.remove(item)
					new_list = "\n".join(PLAYLIST)
					RSave(PLAYFILE, new_list)						# geänderte PLAYLIST speichern		

	# ab V3.7.4 entfällt gesehen - set_status löscht ev. vorh. Pos.-Angabe (sec)
	if mode == 'set_status':										# Status auf >neu< setzen
		PLog('set_status:')
		new_list = []
		for item in PLAYLIST:
			pos = item.find("###neu ")								# Eintrag mit Pos.
			if pos > 0:
				item = item[:pos + len("###neu")]	
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
				fname = "%s_%s" % (PLAYFILE, valid_name)
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
			for item in archiv:
				sp = "%s_" % PLAYFILE				# Archivname abtrennen
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
					try:
						os.rename(fname, PLAYFILE)
						msg1 = u"ist wiederhergestellt"
						xbmcgui.Dialog().notification("PLAYLIST:",msg1,ICON_PLAYLIST,3000)
					except Exception as exception:	
						PLog(str(exception))
						MyDialog("Dateifehler bei Wiederherstellung", str(exception), '')

	return		
		
# ----------------------------------------------------------------------
# Textliste der PLAYLIST erzeugen
def build_textlist(PLAYLIST):
	PLog('build_textlist:')
	
	new_list = []
	cnt=1
	save_new = False											# altes Format überschreiben
	for item in PLAYLIST:
		title, url, thumb, Plot, status = item.split('###')
		Plot=py2_decode(Plot); title=py2_decode(title); 
		my_line = u"%s. %s.." % (str(cnt).zfill(3), title[:60]) # Color in Textviewer o. Wirkung
		if Plot:
			my_line = u"%s | %s.." % (my_line, Plot[:60])
		my_line = "%s | Status: %s" % (my_line, status) 
		my_line = my_line.replace('|||', ' | ')
		my_line = my_line.replace('| |', ' | ')
		my_line = cleanmark(my_line)
		new_list.append(my_line)
		cnt = cnt+1
		
	new_list= "\n".join(new_list)
	new_list = py2_encode(new_list)
	return new_list
# ----------------------------------------------------------------------
# Liste der Archiv-Dateien
def get_archiv():
	PLog('get_archiv:')
	
	globPat = '%s_*' % PLAYFILE
	file_list = glob.glob(globPat)
	if PLAYLIST_ALIVE in file_list:
		file_list.remove(PLAYLIST_ALIVE)	# Lebendsignal (Ruine) ausschließen
	return file_list 			# leer falls keine Archivdateien vorh.
	
# ----------------------------------------------------------------------
# Thread für PLAYLIST, Aufruf play_list(mode='')
# Problem: beim direkten Aufruf von playlist_tools via Button puffert
#	das 1. Video fortlaufend und zeigt keine Bedienelemente, unabhängig
#	vom Param. windowed. OK beim Aufruf aus K-Menü. Gelöst mit vorge-
#	schalteter Startfunktion start_script (Haupt-PRG)
#
def PlayMonitor(mode=''):
	PLog('PlayMonitor:')
	PLAYLIST = get_playlist()
	
	OSD = xbmcgui.Dialog()
	
	mtitle = u"PLAYLIST-Tools"
	PLAYDELAY 		= 10	# Sek.
	open(PLAYLIST_ALIVE, 'w').close()					# Lebendsignal ein - Abgleich play_list
	xbmc.sleep(1000)									# Start-Info abwarten
	monitor = xbmc.Monitor()
	player = xbmc.Player()			
			
	cnt=1
	for item in PLAYLIST:
		PLog(item)
		seekTime = 0									# seek-Point Video
		item = py2_decode(item)
		if '###gesehen' in item:
			msg1 = "Titel %d schon gespielt" % cnt
			xbmcgui.Dialog().notification("PLAYLIST: ",msg1,ICON_PLAYLIST,2000)
			cnt = cnt+1	
			continue

		title, url, thumb, Plot, status = item.split('###')
		if "neu ab" in status:
			seekTime = re.search(u'neu ab (\d+) sec', status).group(1)		# Startpos aus Playlist übernehmen
		PLog("Nr.: %s | %s | ab %s sec" % (cnt, title[:80], seekTime))
		msg2 = "Titel %d von %d" % (cnt, len(PLAYLIST))
		xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,2000)
		cnt = cnt+1	
		start_time = int(seekTime)
		
		# seek-Problem bei HLS-Streams - s. github.com/xbmc/xbmc/issues/18415
		# Exception-Behandl. für nicht verfügb. Videos:
		try:																#  playlist="true" = skip Startliste:
			play_time,video_dur = PlayVideo(url, title, thumb, Plot, playlist="true", seekTime=seekTime)
		except Exception as exception:
			PLog(str(exception))
			continue
		percent=0; 															# noch nichts abgespielt
		
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
		del_val = SETTINGS.getSetting('pref_delete_viewed')	# default 75%
		del_val = re.search(u'(\d+)', del_val).group(1)
		del_val = int(del_val)
		if percent >= del_val:							# Prozentabgleich mit Setting
			item = item.replace("###neu", "###delete")
			PLog('mark_delete: ' + item[:80])		
		else:
			pos = item.find("###neu")					# seekTime=play_time anhängen
			item = item[:pos] + "###neu ab %d sec" % play_time
			PLog('mark_gesehen: ' + item[:80])
		PLAYLIST[cnt-2] = py2_encode(item)
		new_list = "\n".join(PLAYLIST)
		RSave(PLAYFILE, new_list)						# Lock erf. falls auf Share

		if cnt > len(PLAYLIST):
			break
		msg1 = u"nächster PLAYLIST-Titel: %d von %d" % (cnt, len(PLAYLIST)) 
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
			break
			
	xbmcgui.Dialog().notification("PLAYLIST: ","beendet",ICON_PLAYLIST,2000)					
	if os.path.exists(PLAYLIST_ALIVE):					# Lebendsignal aus
		os.remove(PLAYLIST_ALIVE)
		
	return

# ----------------------------------------------------------------------
# Notification-CountDown
def CountDown(sec, title, icon): 
	PLog('PlayMonitor:')

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






