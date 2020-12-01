# -*- coding: utf-8 -*-
################################################################################
#				playlist.py - Teil von Kodi-Addon-ARDundZDF
#			 			Verwaltung der PLAYLIST
#	Kontextmenü s. addDir (Modul util)
################################################################################
#	Stand: 30.11.2020

from __future__ import absolute_import

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
import datetime, time
from threading import Thread	
import random						# Zufallswerte für PLAYLIST
	
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
PLAYFILE		= os.path.join(ADDON_DATA, "playlist") 
PLAYLIST_ALIVE 	= os.path.join(ADDON_DATA, "playlist_alive")	# Lebendsignal für PlayMonitor (leer)
COUNT_STOP 	= os.path.join(ADDON_DATA, "count_stop")		# Stopsignal für Countdown-Thread (leer)

ICON 			= 'icon.png'			# ARD + ZDF
ICON_PLAYLIST	= R("icon-playlist.png")

PLAY_TEMPL 		= u"%s###%s###%s###%s###%s"	#  % (title, url, thumb, Plot, status)

PLog('Script playlist.py geladen')
PLAYLIST=[]

if os.path.exists(PLAYFILE):			# PLAYLIST laden
	PLAYLIST = RLoad(PLAYFILE, abs_path=True)
	PLAYLIST = PLAYLIST.strip().splitlines()
PLog(len(PLAYLIST))
maxvideos = 100							# wie Video-Startlist
msg1 = "PLAYLIST ARDundZDF"

# ----------------------------------------------------------------------
#	Aufruf K-Menü (fparams_playlist_add, fparams_playlist_rm)
#	url, title, thumb + Plot in fparams zusätzlich quotiert
#
def items_add_rm(action, url, title='', thumb='', Plot=''):		
	PLog('items_add_rm: ' + action)
	url = unquote_plus(url); title = unquote_plus(title);  			
	thumb = unquote_plus(thumb); Plot = unquote_plus(Plot);
	PLog(action); PLog(url); PLog(title); PLog(thumb); PLog(Plot); 
	
	new_url = url
	doppler = False
	msg2 = u"Eintrag hinzugefügt, Anzahl %s"
	#------------------
	if action == 'playlist_add':
		Plot=Plot.replace('\n', '||')
		new_line = PLAY_TEMPL % (title, url, thumb, Plot, 'neu')
		new_line = py2_encode(new_line)
		PLog("new_line: " + new_line)
		PLAYLIST.append(new_line)
		
		for i in range(len(PLAYLIST)-1):			# Doppler-Check
			item = PLAYLIST[i]
			title, url, thumb, Plot, status = item.split('###')	# Status: neu, gesehen
			if url in new_url:
				PLAYLIST.remove(new_line)
				doppler = True
				msg2 = u"existiert bereits, Anzahl %s"
				PLog("Doppler url: %s, new_url: %s" % (url, new_url))
				break
		
		cnt = len(PLAYLIST)		
		new_list = "\n".join(PLAYLIST)
		RSave(PLAYFILE, new_list)		
		msg2 = msg2 % cnt
		PLog(msg2)	
		xbmcgui.Dialog().notification(msg1,msg2,ICON_PLAYLIST,3000)

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
		msg2 = msg2 % cnt
		PLog(msg2)	
		xbmcgui.Dialog().notification(msg1,msg2,ICON_PLAYLIST,3000)

# ----------------------------------------------------------------------
#	Aufruf K-Menü (fparams_playlist_add), action nicht verwendet
#	url, title, thumb + Plot in fparams zusätzlich quotiert
#
def playlist_tools(action, url, title='', thumb='', Plot=''):		
	PLog('playlist_tools:')
	url = unquote_plus(url); title = unquote_plus(title);  			
	thumb = unquote_plus(thumb); Plot = unquote_plus(Plot);
	# PLog(url); PLog(title); PLog(thumb); PLog(Plot); 

	dialog = xbmcgui.Dialog()
	# bei Bedarf ergänzen: u"Liste endlos abspielen", u"Liste zufallgesteuert abspielen"
	#	(mode="endless", mode="random"):
	select_list = [	u"Liste abspielen", u"Liste zeigen", u"Liste komplett löschen", 
					u"einzelne Titel löschen", u"Status in kompletter Liste auf >neu< setzen", 
					u"Abbrechen"
				]

	if len(PLAYLIST) == 0:
		xbmcgui.Dialog().notification("PLAYLIST: ","noch leer",ICON_PLAYLIST,2000)
		return

	title = u"PLAYLIST-Tools"
	ret = dialog.select(title, select_list)					# Auswahl Filterliste
	PLog(ret)
	if ret == -1 or ret == 6:
		return
	elif ret == 0:
		play_list(title)									# PLAYLIST starten
	elif ret == 1:
		play_list(title, mode="show")						# PLAYLIST zeigen
	elif ret == 2:
		play_list(title, mode="del_all")					# PLAYLIST kompl. löschen
		msg1 = u"PLAYLIST mit %d Titel(n) wirklich löschen?" % len(PLAYLIST) 
		ret4 = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbrechen', yes='JA', heading=title)
		if ret4 == 1:
			os.remove(PLAYFILE)	
			xbmcgui.Dialog().notification("PLAYLIST: ","gelöscht",ICON_PLAYLIST,2000)
	elif ret == 3:
		play_list(title, mode="del_single")					# PLAYLIST Auswahl löschen
	elif ret == 4:
		play_list(title, mode="set_status")					# Status auf >neu< setzen
	return	
		
# ----------------------------------------------------------------------
def play_list(title, mode=''):		
	PLog('play_list:')
	PLog(mode)
	dialog = xbmcgui.Dialog()
	
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
	
	# alternativ als Kodi-Liste zeigen (dirID="PlayVideo")
	if mode == 'show':												# PLAYLIST zeigen
		PLog('show:')
		title_org = u"%s: aktuelle Liste" % title
		new_list = build_textlist()
		dialog.textviewer(title_org, new_list,usemono=True)

	if mode == 'del_single':										# PLAYLIST Auswahl löschen
		PLog('del_single:')
		title_org = u"%s: einzelne Titel löschen" % title
		new_list = build_textlist()				
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

	if mode == 'set_status':										# Status auf >neu< setzen
		PLog('set_status:')
		new_list = "\n".join(PLAYLIST)
		new_list = new_list.replace("###gesehen", "###neu")
		RSave(PLAYFILE, new_list)
		msg2 = u"Status auf >neu< gesetzt"					
		xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,3000)
		
	return		
		
# ----------------------------------------------------------------------
# Textliste der PLAYLIST erzeugen
def build_textlist():
	PLog('build_textlist:')
	
	new_list = []
	cnt=1
	for item in PLAYLIST:
		title, url, thumb, Plot, status = item.split('###')
		Plot=py2_decode(Plot); title=py2_decode(title); 
		my_line = u"%d. %s.." % (cnt, title[:60])
		if Plot:
			my_line = u"%s | %s.." % (my_line, Plot[:60])
		my_line = "%s | Status: %s" % (my_line, status) 
		my_line = my_line.replace('|||', ' | ')
		my_line = my_line.replace('| |', ' | ')
		my_line = cleanmark(my_line)
		new_list.append(my_line)
		cnt = cnt+1
		
	new_list= "\n".join(new_list)
	return new_list
# ----------------------------------------------------------------------
# Thread für PLAYLIST, Aufruf play_list(mode='')
# Problem: beim direkten Aufruf von playlist_tools via Button puffert
#	das 1. Video fortlaufend und zeigt keine Bedienelemente, unabhängig
#	vom Param. windowed. OK beim Aufruf aus K-Menü.
#
def PlayMonitor(mode=''):
	PLog('PlayMonitor:')
	
	mtitle = u"PLAYLIST-Tools"
	PLAYDELAY 		= 10	# Sek.
	open(PLAYLIST_ALIVE, 'w').close()					# Lebendsignal ein - Abgleich play_list
	xbmc.sleep(1000)									# Start-Info abwarten
	monitor = xbmc.Monitor()
	player = xbmc.Player()

	cnt=1
	for item in PLAYLIST:
		PLog(item)
		item = py2_decode(item)
		if '###gesehen' in item:
			msg1 = "Titel %d schon gespielt" % cnt
			xbmcgui.Dialog().notification("PLAYLIST: ",msg1,ICON_PLAYLIST,2000)
			cnt = cnt+1	
			continue

		title, url, thumb, Plot, status = item.split('###')
		PLog("Nr. %s | %s" % (cnt, title[:80]))
		msg2 = "Titel %d von %d" % (cnt, len(PLAYLIST))
		xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,2000)
		cnt = cnt+1	
		PlayVideo(url, title, thumb, Plot, playlist="true")
		
		while not monitor.waitForAbort(2):
			# Notification ev. ergänzen: player.getTotalTime(),
			#	player.getTime():
			if player.isPlaying():			
				xbmc.sleep(1000)
				# notification stört hier:
				# xbmcgui.Dialog().notification("PLAYLIST: ",msg2,ICON_PLAYLIST,2000) 				
			else:
				break
		
		item = item.replace("###neu", "###gesehen")
		PLAYLIST[cnt-2] = py2_encode(item)
		new_list = "\n".join(PLAYLIST)
		RSave(PLAYFILE, new_list)						# Lock erf. falls auf Share

		if cnt >= len(PLAYLIST):
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
		if ret == 1:		# autoclose, cancel: 0
			open(COUNT_STOP, 'w').close()
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






