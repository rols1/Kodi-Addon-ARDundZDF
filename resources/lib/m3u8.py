# -*- coding: utf-8 -*-

###################################################################################################
#							 m3u8.py - Teil von Kodi-Addon-ARDundZDF
#							ersetzt ffmpeg für Recording- und Aufnahme-
#							funktionen im Addon.
#							Lokale Testumgebung: ../Codestuecke/m3u8_download
#
####################################################################################################
#	Start 16.07.2020 
#	Stand 06.08.2020


# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import urlretrieve
	from urllib2 import Request, urlopen 
elif PYTHON3:
	from urllib.request import Request, urlopen, urlretrieve

import time, datetime
import ssl, re

from resources.lib.util import *
import resources.lib.EPG as EPG

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA

# Hinw.: auch bei exakten ts-Reihenfolgen können im zusammengesetzten Video Zeitfehler
#	auftauchen (Bsp.: AddData - messy timestamps, increasing interval for measuring 
#	average error to 6000 ms). Kodi "glättet die Ausgabe, VLC 3.0.11 nicht.
#
#----------------------------------------------------------------  
def get_m3u8_body(m3u8_url):											# Master m3u8
	PLog('hole Inhalt m3u8-Datei: ' + m3u8_url)
	req = Request(m3u8_url, headers={'user-agent': 'Mozilla/5.0'})
	r = urlopen(req)	
	new_url = r.geturl()										# follow redirects
	PLog("new_url: " + new_url)									# -> msg s.u.
	page = r.read()
	return page.decode('utf-8'),new_url							# 'utf-8' für python3 erf.
	
#----------------------------------------------------------------  
def get_url_list(m3u8_url, body):									# Url-Liste für Einzelauflösungen
	PLog("get_url_list: " + m3u8_url)
	
	pos=m3u8_url.rfind('/')
	host=m3u8_url[:pos]
	PLog("host: " + host)							
	
	lines = body.split('\n')
	ts_url_list = []
	cnt=0;
	for cnt in range(len(lines)):
		line = lines[cnt]
		bw='0'
		if line.startswith('#EXT-X-STREAM-INF'):
			bw = re.search('BANDWIDTH=(\d+)', line).group(1)
			url= lines[cnt+1]									# nächste Zeile
			PLog("%s|%s" % (bw, url))
			if url.startswith('http'):
				ts_url_list.append("%s|%s" % (bw, url))
			else:
				if '/' in url:									 # normaler Pfad			
					ts_url_list.append('%s|%s/%s' % (bw, host, url))
				else:											# rel. Pfad: url anpassen
					url_m3u8_path = m3u8_url.split('/')[-1]		# Bsp.: ..de/master.m3u8 -> ..de/master_320.m3u8
					url = m3u8_url.replace(url_m3u8_path, url)
					url = "%s|%s" % (bw, url)
					ts_url_list.append(url)
		cnt=cnt+1
	ts_url_list.sort(key=lambda x:int(x.split('|')[0]))			# sortiert nach BANDWIDTH aufsteigend
	return ts_url_list

#----------------------------------------------------------------  
def download_ts_file(ts_url):									# TS-Listen für Einzelauflösungen
	PLog('hole Inhalt ts-Datei: ' + ts_url)
	
	req = Request(ts_url, headers={'user-agent': 'Mozilla/5.0'})
	r = urlopen(req)	
	new_url = r.geturl()									# follow redirects
	PLog("new_url: " + new_url)								# -> msg s.u.
	page = r.read()
	PLog("len(page): " + str(len(page)))
	return page.decode('utf-8')								# 'utf-8' für python3 erf.
	
#----------------------------------------------------------------  
# get_ts_startpos
#	ts-Liste muss bereinigt sein (nur ts-Pfade)
# 	Bsp.-Berechnung: Länge ts-Liste=720, ts_dur=4
#		60/4=15 (Puffer/ts_dur), 720-15=705,
#		neue Startposition: 705 - es werden 15 ts-Segmente mit
#		je 4 sec Dauer geladen, bevor die nächste ts-Liste 
#		nachgeladen wird - gilt nur beim 1. Durchlauf.
#
def get_ts_startpos(ts_list, last_ts_path, ts_dur):			# neue Startpos. (von unten)
	PLog('get_ts_startpos')
	ts_dur = int(ts_dur)
	puffer = 60												# Puffer 60 sec / 1 min
	ts_startpos = 4											# Fallback
	
	if ts_dur > 0 and ts_dur <= puffer:						# i.d.R. zw. 4 und 10 (3sat: 2)
		ts_startpos = int(puffer / ts_dur)
		ts_startpos = len(ts_list) - ts_startpos			# Puffer-Start
		ts_startpos = max(ts_startpos, 0)					# Sicherung gegen < 0
	if last_ts_path == '':									# beim Downloadstart
		PLog("Start: ts_startpos=%d" % ts_startpos)
		return ts_startpos
	else:													# Folgedurchläufe
		cnt=0; found=False									# Fallback: Startpos=Listen-Anfang
		for line in ts_list:								# Abgleich letzte geladene ts-url 
			if last_ts_path in line:						#	(last_ts_path)
				PLog("last_ts_path in neuer ts-list, pos %d von %d lines" % (cnt, len(ts_list)))
				ts_startpos = cnt+1	
				found=True						
				break
			cnt = cnt+1	
		if found == False:									# neue Liste startet vermutl. direkt mit Folgepfad
			PLog("last_ts_path fehlt in neuer ts-list: %s" % last_ts_path)
			PLog("verwende Index 0: %s" % ts_list[0])
			# PLog(ts_list)		# Debug
			ts_startpos = 0								
	return ts_startpos
	
#----------------------------------------------------------------
# duration: Dauer des gesamten Videos.
# TARGETDURATION gilt, falls > als duration (sonst müssten wir 
#	das geladene Segment framegenau kürzen).
#
# In den Tests war die TARGETDURATION-Pause (ts_dur) zu
#	lang. Um ein "Enteilen" der ts-Listen zu verhindern 
#	(ges. bei ServusTV), wird die Pause um 0,1 sec reduziert. 
# threadID: Verwendung für KillFile, da für threads kein 
#	sicheres Stop-Verfahren existiert (JobRemove erzeugt).
# 
def download_ts(host, ts_page, dest_video, duration, ts_dur, JobID):	
	PLog('download_ts, Video: ' + dest_video)
	duration = int(duration)
	lines = ts_page.splitlines()
	
	KillFile = os.path.join("%s/ThreadKill_%s") % (ADDON_DATA, JobID)	# Stopfile, gesetzt in JobRemove
	PLog("KillFile: %s" % KillFile)
	# if 'PROGRAM-DATE-TIME:' in ts_page:					# Abgleich Zeitmarken entfällt
	new_lines=[]											# ts-Pfad Zeilen sammeln + Startmarke suchen
	for line in lines:										# bereinigen
		if line.startswith('#') or line == '':
			continue
		new_lines.append(line)
	
	cnt_line=0; cnt_ts=1									# Pos. in ts-Liste; ts-Zähler
	last_ts_path=''
	ts_startpos = get_ts_startpos(new_lines, last_ts_path, ts_dur)	# Startpos. am Anfang ca. 1 Minute 
	PLog("startpos: %d, new_lines: %d" % (ts_startpos, len(new_lines)))
	lines = new_lines										# weiter mit  bereinigter Liste
	cnt_line = ts_startpos					

	#-----------------------------	
	dt = datetime.datetime.now()							# s. EPG get_unixtime 
	now = time.mktime(dt.timetuple())							
	start = str(now).split('.')[0]
	f = open(dest_video, 'wb')
	while True:
		if cnt_line >= len(lines):							# Sicherung
			cnt_line = len(lines)-1
		line = lines[cnt_line]
		# PLog("line %d: %s" % (cnt_line, line))  # Debug
		if line.startswith('http'):
			ts_url = line
		else:
			ts_url = "%s/%s" % (host, line)
		PLog("ts_url: " + ts_url)
		
		req = Request(ts_url, headers={'user-agent': 'Mozilla/5.0'})
		gcontext = ssl.create_default_context()
		gcontext.check_hostname = False
		r = urlopen(req, context=gcontext, timeout=3)
		new_url = r.geturl()				# follow redirects
		meta = r.info()
		PLog("%d. ts-file, Zeile %d, Video %s, ts: %s" % (cnt_ts, cnt_line, dest_video, ts_url))
		cnt_ts=cnt_ts+1						# ts-Zähler
		file_size_dl = 0
		block_sz = 8192
		cnt_line=cnt_line+1					# Pos. in ts-Liste
		while True:							# Puffer füllen	- Checks nach Schreiben
			buffer = r.read(block_sz)
			if not buffer:
				break
			file_size_dl += len(buffer)
			f.write(buffer)
			
		dt = datetime.datetime.now()						# s. EPG get_unixtime 
		now = time.mktime(dt.timetuple())							
		now = str(now).split('.')[0]								
		diff = int(now) - int(start)
		PLog("now: %s, diff: %d, duration: %d, ts_dur: %d" % (now, diff, duration, int(ts_dur))) 
		PLog("exists: %s | %s" % (KillFile, str(os.path.exists(KillFile))))
		if diff > duration or os.path.exists(KillFile):		# Check: Gesamtdauer erreicht ?
			PLog("closing: %s" % dest_video)
			f.close()
			if os.path.exists(KillFile):
				PLog("entferne: %s" % KillFile)
				os.remove(KillFile)	
			break
		
		#-----------------------------	
		if cnt_line >= len(lines)-1:						# rechtz. nachladen (Bsp. ServusTV)
			last_ts_path = line								
			cnt_load=1
			while True:
				PLog("lade ts neu, cnt_line: %d, last_ts_path: %s" % (cnt_line, last_ts_path))
				ts_page = download_ts_file(SESSION_TS_URL)
				new_lines=[]
				lines = ts_page.splitlines()											
				for line in lines:							# ts-Liste bereinigen
					if line.startswith('#') or line == '':
						continue
					new_lines.append(line)
				
				ts_startpos = get_ts_startpos(new_lines, last_ts_path, ts_dur=ts_dur)					
				lines = new_lines
				cnt_line = ts_startpos
				PLog("new_startpos: %d, lines: %d, last_ts_path %s" % (ts_startpos, len(lines), last_ts_path))
				PLog(lines[-3:])							# letzte 3 Zeilen
				if ts_startpos < len(lines):				# OK, Folge-ts vorhanden				
					break
				else:										# Rettung: Folge-ts fehlt noch
					"ts_startpos=len(lines): delay %s" % cnt_load
					time.sleep(1)
					cnt_load=cnt_load+1				
					if cnt_load >= ts_dur:					# wenn Folge-ts immer noch fehlt, weiter mit 1. akt.
						break								# 	ts, Video fehlerhaft
															
		# die Pause richtet sich nach EXT-X-TARGETDURATION. Problem: bei int-Werten kann die Synchr. mit
		# 	 den ts-Listen verlorengehen (Bsp. ServusTV). Abzug 0.1 war bisher ausreichend.
		# time.sleep(ts_dur)							
		s = float(ts_dur - 0.1)
		PLog("sleep: %s sec" % str(s))
		time.sleep(s)		
	f.close()
	return				
#-----------------------------------------------------------------------
# nur in Testumgebung (ohne ZDF-Sender) - holt die ts-Listen
#	aller Sender, Code in ../resources/livesenderTV.xml:
# def get_all_tsfiles():									
#-----------------------------------------------------------------------
# threadID: "%Y%m%d_%H%M%S" aus LiveRecord - in download_ts
#	für KillFile verwendet (gesetzt durch JobRemove in epgRecord).
#
def Main_m3u8(m3u8_url, dest_video, duration, JobID):
	PLog("Main_m3u8:")
	PLog(m3u8_url); PLog(dest_video);PLog(duration);

	global SESSION_TS_URL
	SESSION_TS_URL=''
	 
	body, new_url  = get_m3u8_body(m3u8_url)					# gesamte m3u8-Seite 
	# PLog(body)
	if '#EXT-X-TARGETDURATION' in body:							# reclink in livesenderTV.xml (DasErste)
		PLog('reclink, ohne master.m3u8')						#	master.m3u8 entfällt
		ts_page = body	
		ts_url = m3u8_url
	else:
		ts_url_list= get_url_list(new_url, body)				# alle TS-Listen, abst. sortiert
		# PLog(ts_url_list)	# Debug 
		# exit()
		# todo: Auswahl ermöglichen (optional)
		ts_url = ts_url_list[-1]								# 1. Qual. (Liste aufst. sortiert)
		#   ts_url = ts_url_list[0]								# Debug kleinste Qual.
		bw, ts_url = ts_url.split('|')
		PLog('Anzahl ts-Quellen: %d' % len(ts_url_list))
		PLog("BANDWIDTH: %s" % bw)
		ts_page = download_ts_file(ts_url)						# nur 1. Liste (höchste Qual.)
	SESSION_TS_URL= ts_url										# zum Nachladen ts_file in download_ts

	try:
		ts_dur = re.search('TARGETDURATION:(\d+)', ts_page).group(1)
		ts_dur = int(ts_dur)
	except Exception as exception:	
		PLog(str(exception))
		ts_dur=4												# Default ARD & Co
	PLog("TARGETDURATION: %s, SESSION_TS_URL: %s" % (ts_dur, SESSION_TS_URL))
	#with open("/tmp/ts_liste.txt",'w') as f:					# Debug
	#	f.write(ts_page)
	
	pos=ts_url.rfind('/')
	host=ts_url[:pos]
	PLog("host: " + host)	
							
	from threading import Thread	
	background_thread = Thread(target=download_ts, args=(host, ts_page, dest_video, duration, ts_dur, JobID))
	background_thread.start()									# ts-Dateien laden + verketten	
	#return														# verhindert hier Thread-Modus
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#-----------------------------------------------------------------------



