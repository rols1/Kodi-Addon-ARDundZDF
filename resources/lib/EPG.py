# -*- coding: utf-8 -*-
# EPG, Daten von tvtoday.de 
#	URL-Schema: http://www.tvtoday.de/programm/standard/sender/%s.html  %s=ID, z.B. ard oder ARD
#	Datumsbereich: 12 Tage, Bsp. MO - FR
#	Zeitbereich	5 Uhr - 5 Uhr Folgetag
#		Einteilung (tvtoday.de): 5-11, 11-14, 14-18, 18-20, 20-00, 00-05 Uhr  (hier nicht verwendet)
#	Struktur:
#		Container: class="tv-show-container..
#		Blöcke: <a href=" .. </a>
#		Sendezeit: data-start-time="", data-end-time=""
#
#	20.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#	ab Okt. 2025 Webseite geändert, TV-Daten im json-Format nur für 1 Tag
#
# 	<nr>37</nr>										# Numerierung für Einzelupdate
#	Stand: 20.11.2025
#	
 
from kodi_six import xbmc, xbmcgui, xbmcaddon
from kodi_six.utils import py2_encode, py2_decode
 
import os, sys
import time
import datetime
from datetime import date

PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib2 import urlopen
elif PYTHON3:
	from urllib.request import urlopen


# für Python 2.* muss der  Aufruf Kontextmenü unterdrückt
#	werden, sonst öffnet das Modul bei jedem Menüwechsel
#	 ein leeres textviewer-Fenster
if "'context'" in str(sys.argv) or "ShowSumm" in str(sys.argv):
	from util import *									# Aufruf Kontextmenü
	msg = "callfrom_context"
else:
	from resources.lib.util import *
	msg = "callfrom_router"
PLog(msg)

# EPGCacheTime wie Haupt-PRG:
eci = SETTINGS.getSetting('pref_epg_intervall')
eci = re.search(r'(\d+) ', eci).group(1)  				# "12 Std.|1 Tag|5 Tage|10 Tage"
eci = int(eci)
PLog("eci: %d" % eci)
if eci == 12:											# 12 Std.
	EPGCacheTime = 43200
else:
	EPGCacheTime = eci * 86400 							# 1-10 Tage

ADDON_ID 	= 'plugin.video.ardundzdf'
SETTINGS 	= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH	= SETTINGS.getAddonInfo('path')
EPG_BASE 	= "http://www.tvtoday.de"

########################################################################
# thread_getepg: EPG im Hintergrund laden - Aufruf Haupt-PRG (
#	Kopfbereich) abhängig von Setting pref_epgpreload + Abwesenheit 
#		von EPGACTIVE (Setting "Recording TV-Live"/"EPG im Hintergrund 
#		laden ..") 
#	Startverzögerung 10 sec
#	Aktiv-Signal EPGACTIVE wird abhängig von pref_epg_intervall im
#	 Haupt-PRG wieder entfernt.
#	Dateilock nicht erf.
# 26.10.2020 Update der Datei livesenderTV.xml hinzugefügt - entf. ab
#	09.10.2021 siehe update_single
# 21.05.2024 Nutzung concurrent.futures. Aufruf als Thread (ohne: Klemmer)
#
def thread_getepg(EPGACTIVE, DICTSTORE, PLAYLIST):
	PLog('thread_getepg:')
	
	open(EPGACTIVE, 'w').close()						# Aktiv-Signal setzen (DICT "EPGActive")
	icon = R('tv-EPG-all.png')
	xbmcgui.Dialog().notification("EPG-Download", "gestartet",icon,3000)
	xbmc.sleep(1000)									# Klemmer bei sleep vor Notification	
	
	sort_playlist = get_sort_playlist(PLAYLIST)	
	PLog("Sender: %d" % len(sort_playlist))
	ID_list=[]
	for i in range(len(sort_playlist)):
		rec = sort_playlist[i]
		ID = rec[1]	
		if ID:											# Senderliste mit tvtoday-ID
			ID_list.append(ID)
			fname = os.path.join(DICTSTORE, "EPG_%s" % ID)
			if os.path.exists(fname):					# n.v. oder soeben entfernt?
				os.remove(fname)						# entf. -> erneuern								

	PLog("ID_list: " + str(ID_list))
	for ID in ID_list:
		EPG(ID=ID, load_only=True)						# EPG-Seite laden + speichern	

	xbmcgui.Dialog().notification("EPG-Download", "fertig: %d Sender" % len(sort_playlist),icon,3000)
	
	return

#---------------------------------------------------------------- 
# Update einzelner, aktualisierter Bestandteile des Addons vom Github-Repo
# Hinw.: NICHT für neu ins Repo eingefügte Module (lokale Datei fehlt für
#	den Abgleich).
# Ablösung der vorherigen Funktion update_tvxml
# Aufruf: InfoAndFilter
#
# Details Commits (json):
# 	https://api.github.com/repos/rols1/Kodi-Addon-ARDundZDF/commits?&page=1&per_page=1 
# Details Einzeldatei (json, letzter Commit: committer["date"]):
#	https://api.github.com/repos/rols1/Kodi-Addon-ARDundZDF/commits?path=ARDnew.py&page=1&per_page=1 
# 11.11.2024 Anpassung für Windows an wechselnde Slashes in Dateipfaden in SINGLELIST,
#	Bsp.: ..\\addons\\plugin.video.ardundzdf/resources/livesenderTV.xml
# 02.09.2025 Github-Änderung Webformat - Verzicht auf Download neuer Module, RepoList
#	entfällt, nur noch direkter Abgleich Datei lokal / Datei Repo.
#
def update_single(PluginAbsPath):
	PLog('update_single:')
	import glob	
	GIT_BASE = "https://github.com/rols1/Kodi-Addon-ARDundZDF/blob/master"
	icon = R("icon-update-einzeln.png")
		
	# SINGLELIST enthält die Module in resources/lib im Addon,		# 1. Erstellung Liste lokal
	# zusätzliche Dateien:	
	# nicht verwenden: addon.xml + settings.xml (CAddonSettings-error),
	#	changelog.txt, slides.xml, ca-bundle.pem, Icons
	SINGLELIST = ["%s/%s" % (PluginAbsPath, "resources/livesenderTV.xml"),
				"%s/%s" % (PluginAbsPath, "resources/settings.xml"),
				"%s/%s" % (PluginAbsPath, "resources/arte_lang.json"),
				"%s/%s" % (PluginAbsPath, "resources/UT_Styles_ARD"),
				"%s/%s" % (PluginAbsPath, "ardundzdf.py")
		]
	selected=[0,1,2]												# Auswahl-Default: alle, weiter s.u.

	globFiles = "%s/%s/*py" % (PluginAbsPath, "resources/lib")
	files = glob.glob(globFiles) 									# Module -> SINGLELIST 
	files = sorted(files,key=lambda x: x.upper())
	#PLog(files)			# Debug
	for f in files:
		if "__init__.py" in f or ".pem" in f:						# skip PY2, Zertif. 
			continue
		SINGLELIST.append(f)
	PLog("SINGLELIST: " + str(SINGLELIST))		# Debug
	#-------------													# 2.  Erstellung Liste Github
	
	RepoList=[]	
	for item in SINGLELIST:
		f = item.replace(PluginAbsPath, "https://github.com/rols1/Kodi-Addon-ARDundZDF/tree/master/")
		RepoList.append(f)
	PLog("RepoList: %d" % len(RepoList))

	#-------------													# 3. Dialoge Auswahl + Start

	title = u"Einzelupdate - eigene Auswahl oder Liste?"
	msg1 = u"Vor Einzelupdate eigene Auswahl vornehmen?"
	msg2 = u"Ohne eigene Auswahl wird die  komplette Liste abgeglichen (%s Dateien)" % len(SINGLELIST)
	ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False,  yes='eigene Auswahl', cancel='komplette Liste', 
		heading=title)												# False: ESC, komplette Liste
	single = ret													# True = eigene Auswahl	
	PLog("single: " + str(single))		
	
	textlist=[]; ret_list=[]; cnt=0
	for local_file in SINGLELIST:
		local_file = local_file.split(PluginAbsPath)[-1]			# cut bis einschl. plugin.video.ardundzdf
		if "\\" in local_file:
			local_file = local_file.split("\\")[-1]					# Windows
		else:
			local_file = local_file.split("/")[-1]	
		PLog(local_file)		
		textlist.append(local_file)									# nur Dateinamen
		ret_list.append(cnt)										# Listen-Index, default: alle ausgewählt
		cnt=cnt+1
	
	if single:
		selected=[]
		title = u"Einzelupdate - eigene Auswahl vornehmen:"
		ret_list = xbmcgui.Dialog().multiselect(title, textlist, preselect=selected)
		PLog("ret_list: %s" % str(ret_list))
		if ret_list ==  None or len(ret_list) <= 0:					# ohne Auswahl
			return
	
	title = "Einzelupdate starten (eigene Auswahl)"
	if len(ret_list) == len(SINGLELIST):
		title = "Einzelupdate starten (komplette Liste)"
	msg1 = u"Einzelupdate ersetzt lokale Dateien nach Abgleich mit den entsprechenden Dateien im Github-Repo" 
	msg1 = u"%s (Abgleich: [B]%d[/B] von [B]%d[/B] Dateien)" % (msg1, len(ret_list), len(SINGLELIST))
	msg2 = u"Einzelupdate starten?"
	ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
	if ret != 1:
		return

	#-------------													# 4. Abgleich / Update
	
	result_list=[]; 												# Ergebnisliste für textviewer
	cnt=-1		
	for local_file in SINGLELIST:
		cnt=cnt+1
		PLog("cnt=%d, %s" % (cnt, str(cnt in ret_list)) )
		if cnt in ret_list:											# in Auswahlliste?	
			# Bsp.: ../.kodi/addons/plugin.video.ardundzdf/resources/livesenderTV.xml
			lpage = RLoad(local_file, abs_path=True)				# lokale Updatedatei 
			nr_local= stringextract('<nr>', '</nr>', lpage)			# nr = Dateiversion lokal
			if nr_local.isdigit() == False:
				nr_local = "0"
			updated	= False
			if nr_local:		
				try:
					fname = local_file.split(PluginAbsPath)[-1]		# Bsp.: /resources/lib/ARDnew.py
					# Bsp.: ../github.com/rols1/Kodi-Addon-ARDundZDF/blob/master/resources/livesenderTV.xml?raw=true
					remote_file = "%s%s?%s" % (GIT_BASE, fname, "raw=true")
					remote_file = remote_file.replace('\\', '/')
					PLog('lade %s' % remote_file)
					
					r = urlopen(remote_file)						# Updatedatei auf Github 
					page = r.read()
					if PYTHON3:										# vermeide Byte-Error bei py2_decode			
						page = page.decode("utf-8")
					PLog(page[:80])

					nr_remote	= stringextract('<nr>', '</nr>', page)
					if nr_remote.isdigit() == False:
						nr_remote = "0"
					PLog("nr_local: %s, nr_remote: %s" % (nr_local, nr_remote))
					if int(nr_remote) > int(nr_local):
						page = py2_encode(page)
						RSave(local_file, page)
						PLog("aktualisiert: %s" % local_file)
						updated	= True
					else:
						PLog("noch aktuell: %s" % fname)
				except Exception as exception:	
					PLog("exept_update_single: %s" % str(exception))

				if "\\" in fname:									# Dateiname -> result_list
					fname = fname.split("\\")[-1]					# Windows 
				else:
					fname = fname.split("/")[-1]					# Unixe
 
				msg2 = "noch aktuell"
				if updated:											# Notification bei Update
					fname = "[B]%s[/B]" % fname								
					msg2 = "aktualisiert"
					xbmcgui.Dialog().notification(fname,msg2,icon,1000)
				else:
					# time < 1000 offensichtlich ignoriert:			# Notification ohne Update, kein Sound
					x=xbmcgui.Dialog().notification("Einzelupdate",fname,icon,1000, False)
					 	
				result_list.append("%14s: %s" % (msg2, fname)) 
				xbmc.sleep(1000)									# ohne Pause nachlaufende notifications
			else:
				PLog("nr_local fehlt in %s" % local_file)

	#-------------													# 5. Ergebnisliste

	# xbmc.executebuiltin('Dialog.Close(all,true)')					# verhindert nicht Nachlaufen 
	result_list = "\n".join(result_list)							# Ergebnisliste
	title = u"Einzelupdate - Abgleich von %d Dateien | Ergebnis:" % len(ret_list)
	textviewer(title, result_list,usemono=True)						# util
	
	return

#-----------------------
# 	mode: 		falls 'OnlyNow' dann JETZT-Sendungen
# 	day_offset:	1,2,3 ... Offset in Tagen (Verwendung zum Blättern in EPG_ShowSingle,
#		Umrechnung in get_unixtime)
# 	Aufruf: EPG_ShowAll (Haupt-PRG), thread_getepg
#	30.10.2023 neues Konzept: Cacheablage 2-dim-EPG-Array pro Sender 
#		statt Webseite, Tage-Offset (2-12) durch kompl. 12-Tage-Erfassung 
#		gewährleistet. thread_getepg löscht die Array-Datei im Dict und
#		stößt die Neuerfassung in EPG() an.
#		EPG() entscheidet anhand des Formats der Dict-Datei die Auswertung
#		als Array (type 'list') oder als Textdatei in get_api_data (soll
#		korrekte Behandlung alter Cache-Dateien im Webformat verhindern).
#	01.10.2025 Webseite geändert, auch Zeitformat 
#	
def EPG(ID, mode=None, day_offset=None, load_only=False):
	PLog('EPG_ID: ' + ID)
	PLog(mode); PLog(day_offset); PLog(load_only);

	Dict_ID = "EPG_%s" % ID
	if ID == "dummy":
		return []
	
	EPG_dict = Dict("load", Dict_ID, CacheTime=EPGCacheTime)
	if EPG_dict == False or len(EPG_dict) == 0:							# Cache miss - vom Server holen
		EPG_dict = get_api_data(Dict_ID)								# Api -> 2-dim-Array EPG_rec -> Dict					 
	PLog("EPG_dict: %d" % len(str(EPG_dict)))	

	# today.de verwendet Unix-Format, Bsp. 1488830442
	now,today,today_5Uhr,nextday,nextday_5Uhr = get_unixtime(day_offset)# lokale Unix-Zeitstempel holen + Offsets
	now_human = datetime.datetime.fromtimestamp(int(now))				# Debug: Übereinstimmung mit UTC, Timezone?	
	now_human =  now_human.strftime("%d.%m.%Y, %H:%M:%S")				# deutsches Format
	day_human = datetime.datetime.fromtimestamp(int(today_5Uhr))
	day_human =  day_human.strftime("%d.%m.%Y")							# deutsches Datumformat für Offset
	
	PLog('EPG_date_formats:')
	PLog(now); PLog(now_human); PLog(day_human);
	# PLog(today); PLog(today_5Uhr); PLog(nextday); PLog(nextday_5Uhr)	# bei Bedarf
	today_5Uhr=int(today_5Uhr); nextday_5Uhr=int(nextday_5Uhr)
	now=int(now)

	date_format = "%Y-%m-%dT%H:%M:%S"
	# Ausgabe: akt. Tag ab 05 Uhr(Start) bis nächster Tag 05 Uhr (Ende)
	EPG_rec=[]															# -> gefilterte Aufbereitung (Zeit, JETZT-Mark.)
	for i in range (len(EPG_dict)):		# ältere + jüngere Sendungen in Liste - daher Schleife + Zeitabgleich	
		rec = []
		r = EPG_dict[i]
		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime,  
		#			5=summ, 6=vonbis, 7=today_human, 8=endtime:  
		s_start=r[0]; href=r[1]; img=r[2]; sname=r[3];					# href=r[1] nicht verwendet
		stime=r[4]; summ=r[5]; vonbis=r[6];today_human=r[7]; 			# today_human=r[7] noch leer
		s_end=r[8];
		
		summ = summ.replace("None", "?")
		
		starttime = time.mktime(s_start.timetuple())					# -> unix
		starttime = int(starttime)
		endtime = time.mktime(s_end.timetuple())
		endtime = int(endtime)
		
		s_startday =  s_start.strftime("%A") 							# Locale’s abbreviated weekday name
		iWeekday = transl_wtag(s_startday)
		today_human = iWeekday + ', ' + day_human						# Wochentag + Datum -> tagline
		diff = starttime - endtime
		# PLog("diff_%d: %s, %d-%d" % (i, now, starttime, endtime))		# bei Bedarf
		
		# Auslese - nur akt. Tag 05 Uhr (einschl. Offset in Tagen ) + Folgetag 05 Uhr:
		if starttime < today_5Uhr:										# ältere verwerfen
			#PLog("too_old")
			#diff = today_5Uhr -starttime
			#PLog("s_start: %s | today_5Uhr-starttime: %d-%d, diff: %d" % (s_start, today_5Uhr, starttime, diff))
			continue
		if starttime > nextday_5Uhr:									# jüngere verwerfen
			#PLog("too_young")
			#diff = starttime-nextday_5Uhr
			#PLog("s_start: %s | starttime-nextday_5Uhr: %d-%d, diff: %d" % (s_start, starttime, nextday_5Uhr, diff))
			continue	
				
		summ = 	repl_json_chars(summ)
		if now >= starttime and now < endtime:
			PLog("diffnow_%d: %s, %s-%s" % (i, now, starttime, endtime))
			# Farb-/Fettmarkierung bleiben im Kontextmenü erhalten (addDir):
			sname = "[B]JETZT: %s[/B]" % sname						# JETZT: fett 
			PLog("JETZT: %s, %s" % (sname, img))
			if mode == 'OnlyNow':										# Call EPG_ShowAll: nur aktuelle Sendung
				rec = [starttime,href,img,sname,stime,summ,vonbis]  	# Index wie EPG_rec
				#PLog(rec)
				PLog('EPG_EndOnlyNow')
				return rec												# Rest verwerfen - Ende
				break		

		if endtime < now:												# vergangenes: grau markieren
			sname = "[COLOR grey][B]%s[/B][/COLOR]" % sname

		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis, 
		#			7=today_human, 8=endtime:  
		# Link href zum einzelnen Satz hier nicht verwendet - wenig zusätzl. Infos
		rec.append(starttime);rec.append(href); rec.append(img); rec.append(sname);	# Listen-Element
		rec.append(stime); rec.append(summ); rec.append(vonbis); rec.append(today_human);
		rec.append(endtime)
		EPG_rec.append(rec)												# Liste Gesamt (2-Dim-Liste)
	
	PLog(len(EPG_rec)); PLog('EPG_End:')								# Sortierung <- get_api_data
	if mode == 'OnlyNow' and len(EPG_rec) > 7:
		PLog("OnlyNow_rec_len_to_big")
		EPG_rec=[]
	return EPG_rec

#-----------------------
def get_summ(block):		# Beschreibung holen
	summ = ''
	descr_list = blockextract('small-meta description', block)	# 1-2 mal vorhanden
	i = 0
	for item in descr_list:
		descr = stringextract('small-meta description\">', '</p>', item)
		if descr:
			if summ:
				summ = summ  + ' | ' + descr
			else:
				summ = descr
		i = i + 1
			
	childinfo = stringextract('children-info\">', '</p>', block)
	if childinfo:
		summ = summ + ' | ' + childinfo	
	return summ

#-----------------------
# Funktion get_sort_playlist aus Haupt-PRG (hier nicht importierbar)
#
def get_sort_playlist(PLAYLIST):				# sortierte Playliste der TV-Livesender
	PLog('get_sort_playlist:')
	
	playlist = RLoad(PLAYLIST)					# lokale XML-Datei (Pluginverz./Resources)
	stringextract('<channel>', '</channel>', playlist)	# ohne Header
	playlist = blockextract('<item>', playlist)
	sort_playlist =  []
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)				# skip_log: Log-Begrenzung
	
	for item in playlist:   
		rec = []
		title = stringextract('<title>', '</title>', item)
		# PLog(title)
		title = up_low(title)										# lower-/upper-case für sort() relevant
		EPG_ID = stringextract('<EPG_ID>', '</EPG_ID>', item)
		img = 	stringextract('<thumbnail>', '</thumbnail>', item)
		link =  stringextract('<link>', '</link>', item)			# url für Livestreaming
		if "<reclink>" in item:
			link =  stringextract('<reclink>', '</reclink>', item)	# abw. Link, zum Aufnehmen geeignet
		
		if 'ZDFsource' in link:
			title_sender = stringextract('<hrefsender>', '</hrefsender>', item)	
			link=''										# Reihenfolge an Playlist anpassen
			# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
			for line in zdf_streamlinks:
				items = line.split('|')
				# Bsp.: "ZDFneo " in "ZDFneo Livestream":
				if up_low(title_sender) in up_low(items[0]): 
					link = items[1]
			if link == '':
				PLog('%s: Streamlink fehlt' % title_sender)			
		
		rec.append(title); rec.append(EPG_ID);						# Listen-Element
		rec.append(img); rec.append(link);
		sort_playlist.append(rec)									# Liste Gesamt
	
	# Zeilen-Index: title=rec[0]; EPG_ID=rec[1]; img=rec[2]; link=rec[3];	
	sort_playlist = sorted(sort_playlist,key=lambda x: x[0])		# Array-sort statt sort()
	return sort_playlist
	
########################################################################
# Auswertung der Webseite für EPG(), jeweils einzeln für 1 Sender 
# today.de verwendet Unix-Format, Bsp. 1488830442
# 01.10.2025 Webseite geändert (json eingebettet), auch Zeitformat
# 11.10.2025 nur noch 3 Tage EPG (tvtoday liefert nur noch 1 Tag pro
#	Zugriff)
def get_api_data(Dict_ID):
	PLog("get_api_data:")	
	
	sid = Dict_ID.split("EPG_")[-1]
	img_base = "https://img.tvspielfilm.de"
	api_base = "https://www.tvtoday.de/api/broadcasts?channelId[]=%s&dates[]=%s&timeFrame=day&limit=9999&offset=0&orderBy=channel&sortDirection=asc"
	now,today,today_5Uhr,nextday,nextday_5Uhr = get_unixtime()		# lokale Unix-Zeitstempel, ohne Offset
	# wlist = list(range(0,8))										# ca. 35 sec. bei 100  Mbit
	wlist = list(range(0,3))										# ca. 13 sec
	now = datetime.datetime.now()
	data_list=[]

	try:
		cnt=0; data_len=0
		for nr in wlist:
			rdate = now + datetime.timedelta(days = nr)
			rday = rdate.strftime("%Y-%m-%d")
			url = api_base % (sid, rday)
			page, msg = get_page(url)
			if page:													# json-mapping via ** klappt nicht
				data_list.append(page)
				data_len = data_len + len(page)							# -> Gesamtlänge
			cnt=cnt+1 
	except Exception as exception:
		data_items=[]
		PLog("data_load_error: " + str(exception))
	
	PLog("data_loaded: %d in %d Listen" % (data_len, len(data_list)))

	#url = api_base % (sid, "2025-10-11")								# Debug single page
	#page, msg = get_page(url)
	#data_list.append(page)
	
	# ältere + jüngere Sendungen in Liste, Zeitabgleich in EPG()
	EPG_rec = []
	for data in data_list:												# data = 1 Tag
		PLog("get_data: %d" % len(data))
		try:
			jsonObject = json.loads(data)
			objs = jsonObject["items"]
			PLog("records_objs: %d" % len(objs))
			i=0

			for obj in objs:											# obj = ca. 30 Sendungen		
				# rec: akt. Tag ab 05 Uhr(Start) bis nächster Tag 05 Uhr (Ende):	
				rec = []
				summ=""; summ1=""; summ2=""; summ3="";
				img=""

				starttime = obj["startDate"]
				endtime = obj["endDate"]	
				href = obj["url"]											# PRG-Seite nicht verwendet	
				if "images" in obj:
					img = img_base + obj["images"][0]["path"]				# max-Größe
				
				stitle = obj["title"]
				sub = obj["subtitle"]
				stitle = unescape(stitle); stitle = stitle.replace('\"', '*')		
				if sub:
					stitle = "%s: %s" % (stitle, sub)						# Hubert ohne Staller: Bauernregel

				genre = obj["genre"]
				prodyear = obj["productionYear"]
				descr = obj["showTopics"]
				country = obj["publicationCountryId"]
				summ3 = "%s, %s, %s" % (genre, country, prodyear)			# wie tvtoday: Nachrichten, D, 2025

				channelId = obj["channelId"]
				comment = obj["showCommentator"]
				gast = obj["studioGuest"]
				host = obj["showHost"]
				summ2 = channelId
				if comment:
					summ2 = "%s | Kommentator: %s" % (summ2, comment)
				if gast:
					summ2 = "%s | Gast: %s" % (summ2, gast)
				if host:
					summ2 = "%s | Host: %s" % (summ2, host)

				if descr:
					summ = descr
				if summ1:
					summ = "%s\n%s" % (summ, summ1)
				if summ2:
					summ = "%s\n%s" % (summ, summ2)
				summ = "%s\n%s" % (summ, summ3)
				summ = unescape(summ)
				
				# date-Format: 2025-10-01T05:00:00+02:00
				date_format = "%Y-%m-%dT%H:%M:%S"
				starttime=starttime[:19]; endtime=endtime[:19]
				
				s_start=datetime.datetime.fromtimestamp(time.mktime(time.strptime(starttime, date_format)))
				s_startday =  s_start.strftime("%A") 						# Locale’s abbreviated weekday name
				stime = s_start.strftime("%H:%M")
				sname = "%s | %s" % (stime, stitle)							# Titel: Bsp. 06:40 | Nachrichten
				if i == 0 or i == len(objs)-1:								# erster / letzter Satz
					PLog("Start: %s, End: %s | stime: %s, sname: %s" % (starttime, endtime, stime, sname))		
			
				von = stime
				s_end=datetime.datetime.fromtimestamp(time.mktime(time.strptime(endtime, date_format)))
				bis = s_end.strftime("%H:%M") 
				vonbis = von + ' - ' + bis
			
				# Indices EPG_rec: 0=s_start, 1=href, 2=img, 3=sname, 4=stime,  
				#			5=summ, 6=vonbis, 7=today_human, 8=s_end:  
				# Link href zum einzelnen Satz hier nicht verwendet - wenig zusätzl. Infos
				today_human=""												# gesetzt in EPG()
				rec.append(s_start);rec.append(href); rec.append(img); rec.append(sname);	# Listen-Element
				rec.append(stime); rec.append(summ); rec.append(vonbis); rec.append(today_human);
				rec.append(s_end)
				EPG_rec.append(rec)											# Liste Gesamt (2-Dim-Liste)
				i=i+1				
		
		except Exception as exception:
			EPG_rec=[]
			PLog("data_extract_error: " + str(exception))
	
	EPG_rec.sort()														# Sortierung (-> zeitl. Folge)
	# PLog(str(EPG_rec))	
	Dict("store", Dict_ID, EPG_rec)										# Daten -> Cache: aktualisieren	
	PLog("records: %d" % len(EPG_rec)); PLog('get_api_data_End')
	return EPG_rec
	
########################################################################
# 16.06.2024 Aufruf Haupt-PRG, aktualisiert die TV-Livestream-Quellen
#	für Cache im Hintergrund -> util.refresh_streamlinks
def thread_getstreamlinks():
	PLog("thread_getstreamlinks:")
	
	xbmc.sleep(2000)	
	refresh_streamlinks()
	return

####################################################################################################
#									Hilfsfunktionen
####################################################################################################
# get_unixtime() ermittelt 'jetzt', 'nächster Tag' und 'nächster Tag, 5 Uhr 'im Unix-Format
#	tvtoday.de verwendet Unix-Format: data-start-time, data-end-time (beide ohne Sekunden)
# 	day_offset:	1,2,3 ... Offset in Tagen
#	Rückgabe today: today + Offset
#	Unix-Sommerzeit für Folgejahre anpassen
def get_unixtime(day_offset=None, onlynow=False):
	dt = datetime.datetime.now()								# Format 2017-03-09 22:04:19.044463
	now = time.mktime(dt.timetuple())							# Unix-Format 1489094334.0
	now = str(now).split('.')[0]								# .0 kappen (tvtoday.de ohne .0)
	
	if onlynow:
		return now
	
	dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)  # auf 0 Uhr setzen: 2017-03-09 00:00:00
	today = time.mktime(dt.timetuple())							# Unix-Format 1489014000.0
	# today = time.mktime(d.timetuple()) 						# Ergebnis wie oben
		
	if day_offset:
		today = today + (int(day_offset) * 86400)				# Zuschlag in ganzen Tagen (1 Tag = 86400 sec)
	nextday = today + 86400										# nächster Tag 			(+ 86400 sec = 24 x 3600)
	today_5Uhr = today + 18000									# today+Offset, 05 Uhr  (+ 18000 sec = 5 x 3600)
	nextday_5Uhr = nextday + 18000								# nächster Tag, 05 Uhr 
	
	today = str(today).split('.')[0]
	nextday = str(nextday).split('.')[0]
	nextday_5Uhr = str(nextday_5Uhr).split('.')[0]
	today_5Uhr = str(today_5Uhr).split('.')[0]
	
	# Bei Bedarf Konvertierung 'Human-like':
	# nextday_str = datetime.datetime.fromtimestamp(int(nextday))
	# nextday_str = nextday.strftime("%Y%m%d")	# nächster Tag, Format 20170331
		
	return now,today,today_5Uhr,nextday,nextday_5Uhr
#----------------------------------------------------------------  
#################################################################  
# 11.06.2025 Erweiterung Radio-EPG (Kontextmenü, Button für gesamtes
#	Radio-EPG in AudioStartLive
		
params = unquote(str(sys.argv))
PLog("context_params: " + params)

if "'context'" in str(sys.argv):										# Kontextmenü: EPG im textviewer
	PLog("EPG_context:")
	
	if "pub_id" in params:												# Radio-EPG einzelner Sender
		PLog("get_Radio-EPG")
	
		base = "https://programm-api.ard.de/radio/api/publisher?publisher="
		lines=[]
		pub_id = stringextract("pub_id': '", "'", params)				# urn:ard:publisher:c4a9cee041835529
		sender = stringextract("sender': '", "'", params)				# Sender-Titel -> textviewer
		PLog("sender: %s, pub_id: %s" % (sender, pub_id))
		path = base + pub_id
		page, msg = get_page(path)
		PLog(page[:80])
		if page:
			try:
				objs = json.loads(page)								
				for obj in objs:
					stitle=""; artist=""
					start = obj["start"]; end = obj["end"]
					start = start[11:11+5]; end = end[11:11+5]
					title = obj["title"] 
					if "subTitle" in obj:
						stitle = obj["subTitle"];
					line = "%s - %s | %s" % (start, end, title)
					if stitle:
						line = "%s | %s" % (line, stitle)
					if line not in lines:								# mehrfach mit verschied. livestreamId's
						lines.append(line)
						
					if "clip" in obj:									# Beitrag mit Details ergänzen
						clip = obj["clip"]
						start = clip["start"]; end = clip["end"]
						start = start[11:11+5]; end = end[11:11+5]
						if "artist" in clip:
							artist = clip["artist"]
						title = clip["title"]
						typ = clip["type"]
						line = "%s - %s | %s | %s" % (start, end, typ, title)
						if artist:
							line = "%s | %s" % (line, artist)
						if line not in lines:							# mehrfach wie oben
							lines.append(line)						
					
			except Exception as exception:
				lines=[]; sender="Radio-EPG"
				PLog(obj)
				PLog("pub_id_error: " + str(exception))			
		title = sender
	else:																# TV-EPG einzelner Sender (K-Menü)
		title =  stringextract("title': '", "'", params)
		ID =  stringextract("ID': '", "'", params)
		PLog("title: %s, ID: %s" % (title, ID))
		EPG_rec = EPG(ID, day_offset=0)
		PLog("EPG_rec: %s" % str(EPG_rec))

		cnt=0
		for rec in EPG_rec:
			sname=rec[3]				
			if 'JETZT' in sname:										# vorherige Verwerfen
				PLog("context_now: " + str(rec))
				break
			cnt=cnt+1
		EPG_rec = EPG_rec[cnt:]
		# PLog("EPG_rec: %s" % str(EPG_rec))

		lines=[]
		for rec in EPG_rec:
			try:
				sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];	# alle Indices s. EPG
				if sname.count("|") > 1:
					sname = sname.split("|")[2]							# So | JETZT: 15:55 | Weltcup-Skispringen
				sname = sname.replace("[/BEPG_rec:]", "")
				sname = "%s | %s" % (vonbis,sname)
				lines.append("[B]%s[/B]\n%s\n" % (sname, summ))
			except Exception as exception:
				PLog("EPG_rec_error: " + str(exception))	

	# ------------------------------------								# Ausgabe
	#PLog(lines)		# Debug
	if len(lines) == 0:
		icon = R('tv-EPG-all.png')
		title = ID
		xbmcgui.Dialog().notification(title, "keine EPG-Daten vorhanden",icon,3000)	
	else:
		lines =  "\n".join(lines)
		PLog("title: " + title)
		title = title.replace('", "', ',')
		textviewer(title, lines, usemono=True)							# util

#-----------------------------------------------------------------------		
if "ShowSumm" in str(sys.argv):											# Kontextmenü: Video-Inhaltstext im textviewer
	PLog("EPG_ShowSumm:")
	icon = R('icon-info.png')
	title =  stringextract("title': '", "'", params)
	title = title.replace('"', "")
	path =  stringextract("path': '", "'", params)
	ID =  stringextract("ID': '", "'", params)
	if path.find("www.3sat.de") > 0:						# ID="ZDF" möglich in addDir
		ID = "3sat"	
	
	PLog("title: %s, path: %s, ID: %s" % (title, path, ID))

	msg1 = "Fehler beim Abruf der Videodaten:" 
	page, msg2 = get_page(path)
	if page == "":
		MyDialog(msg1, msg2, '')	
		exit()

	page = py2_encode(page)									# PY2
	PLog(str(page)[:80])
	summ1=""; summ2=""
	#---------------------									# ARD
	if ID == "ARD":
		PLog("extract_ARD")
		try:
			page_obs = json.loads(page)
			if "teasers" in page_obs:
				s =page_obs["teasers"]						# Objekte 1. Ebene
				PLog("teasers: " + str(s)[:80])
			if "widgets" in page_obs:
				s =page_obs["widgets"]
				PLog("widgets: " + str(s)[:80])

			summ1 = s[0]["synopsis"]						# Beschr. Einzelbeitrag oder Folge
			summ2 = s[1]["teasers"][0]["show"]["synopsis"]	# Beschr. Staffel/Reihe (in allen teasers identisch)
		except Exception as exception:
			PLog("summ_error:" + str(exception))
			
		PLog("summ1: " + summ1); PLog("summ2: " + summ2)
		summ = "%s\n\n%s" % (summ1, summ2)
	
	#---------------------									# ZDF
	if ID == "ZDF":
		# 20.03.2025 Korrektur sharingUrl nach ZDF-Relaunch (wie ZDF_get_content,
		#	ZDF_getApiStreams)
		PLog("extract_ZDF")
		PLog("path: " + path)
		summ=""
		try:
			page_obs = json.loads(page)
			path_org = page_obs["document"]["sharingUrl"]	# Beschr. erst in Webseite
			path, msg = getRedirect(path_org)
			if path == "":
				p = path_org.split("/")							# 
				if p[-1] == "/":
					del p[-1]
				del p[-1]										# letztes Element entfernen
				path = "/".join(p)
			PLog("sharingUrl: %s, corrected: %s" % (path_org, path))
			
			descr = page_obs["document"]["beschreibung"]
			PLog("descr_api: %d, %s" % (len(descr), descr[:80]))
		except Exception as exception:
			PLog("summ_error:" + str(exception))
			path=""
				
		if path:
			summ = get_summary_pre(path,ID,skip_verf=True,skip_pubDate=True,duration='dummy')
			PLog("check_len: descr %d, summ %d" % (len(descr), len(summ)))
			if len(descr) > len(summ):						# Abgleich
				summ = descr
			ind = summ.find("|")
			if ind > 0 and ind <= 9:						# Kennung mit Dauer: V5.1.2_summ:44 min | ..
				summ = summ[ind+2:]
			summ = summ.replace("|", "\n\n")
	
	#---------------------									# 3sat
	if ID == "3sat":
		PLog("extract_3sat")
		summ=""
		summ1 = stringextract('paragraph-large ">', "</", page)
		text_cells =  blockextract('class="cell large-8 large-offset-2">', page, "</div>")
		summ2=""
		for cells in text_cells:
			summ2  = summ2 + stringextract("<p>", "</p>", cells) + "\n\n"

		summ = "%s%s" % (summ1, summ2)
		summ = cleanhtml(summ)
		summ = unescape(summ)
		
		if "kika.de/_next-api" in path:						# KiKA: kika.de/_next-api/proxy/v1/videos/..
			PLog("extract_KiKA")

			btext=""; ttext=""; atext=""					# BrandText, TeaserText, altText
			brand = stringextract('"brandInfo":{', '}', page)
			PLog("brand: " + brand)
			if brand:
				btext = stringextract('descriptionTitle":"', '"', brand)
				btext = btext + stringextract('description":"', '"', brand)
				PLog("btext: " + btext)
			atext = stringextract('alt":"', '"', page)
			ttext = stringextract('teaserText":"', '"', page)
				
			summ2 = stringextract('description":"', '"', page)
			PLog("summ2: " + summ2)
			summ = summ2
			if ttext:
				summ = "%s\n\n%s" % (ttext, summ)
			if atext:
				summ = "%s\n\n%s" % (atext, summ)
			if btext:
				summ = "%s\n\n%s" % (btext, summ)

	#---------------------									# Ausgabe

	PLog("summ: " + summ)
	if summ.strip() == "":
		xbmcgui.Dialog().notification("suche Inhaltstext:", "leider ohne Ergebnis",icon,3000)	
	else:
		textviewer(title, summ, usemono=True)				# util
		
#-----------------------------------------------------------------------		
		
		
		
		
		












