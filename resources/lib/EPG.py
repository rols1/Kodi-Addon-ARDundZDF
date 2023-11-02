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
# 	<nr>15</nr>										# Numerierung für Einzelupdate
#	Stand: 02.11.2023
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
if "'context'" in str(sys.argv):									# Aufruf Kontextmenü
	from util import *
	msg = "callfrom_context"
else:
	from resources.lib.util import *
	msg = "callfrom_router"
PLog(msg)

ADDON_ID 	= 'plugin.video.ardundzdf'
SETTINGS 	= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH	= SETTINGS.getAddonInfo('path')
EPG_BASE 	= "http://www.tvtoday.de"

########################################################################
# thread_getepg: EPG im Hintergrund laden - Aufruf Haupt-PRG (
#	Kopfbereich) abhängig von Setting pref_epgpreload + Abwesenheit 
#		von EPGACTIVE (Setting "Recording TV-Live"/"EPG im Hintergrund 
#		laden ..") 
#	Startverzögerung 10 sec, 2 sec-Ladeintervall 
#	Aktiv-Signal EPGACTIVE wird nach 12 Std. von
#	 Haupt-PRG wieder entfernt.
#	Dateilock nicht erf. - CacheTime hier und in EPG identisch
# 26.10.2020 Update der Datei livesenderTV.xml hinzugefügt - entf. ab
#	09.10.2021 siehe update_single
#
def thread_getepg(EPGACTIVE, DICTSTORE, PLAYLIST):
	PLog('thread_getepg:')
	CacheTime = 43200								# 12 Std.: (60*60)*12 wie EPG s.u.
	
	open(EPGACTIVE, 'w').close()					# Aktiv-Signal setzen (DICT "EPGActive")
	xbmc.sleep(1000 * 10)							# verzög. Start	
	icon = R('tv-EPG-all.png')
	xbmcgui.Dialog().notification("EPG-Download", "gestartet",icon,3000)
	
	
	sort_playlist = get_sort_playlist(PLAYLIST)	
	PLog(len(sort_playlist))
	
	for i in range(len(sort_playlist)):
		rec = sort_playlist[i]
		title = rec[0]			# Debug
		ID = rec[1]
		
		fname = os.path.join(DICTSTORE, "EPG_%s" % ID)
		if os.path.exists(fname):					# n.v. oder soeben entfernt?
			os.remove(fname)						# entf. -> erneuern								
		rec = EPG(ID=ID, load_only=True)			# Seite laden + speichern
		xbmc.sleep(1000)							# Systemlast verringern
		
	xbmcgui.Dialog().notification("EPG-Download", "abgeschlossen",icon,3000)
	
	return

#---------------------------------------------------------------- 
# Update einzelner, aktualisierter Bestandteile des Addons vom Github-Repo
# Hinw.: NICHT für neu ins Repo eingefügte Module (lokale Datei fehlt für
#	den Abgleich).
# Ablösung der vorherigen Funktion update_tvxml
#
# Details Commits (json):
# 	https://api.github.com/repos/rols1/Kodi-Addon-ARDundZDF/commits?&page=1&per_page=1 
# Details Einzeldatei (json, letzter Commit: committer["date"]):
#	https://api.github.com/repos/rols1/Kodi-Addon-ARDundZDF/commits?path=ARDnew.py&page=1&per_page=1 
#
def update_single(PluginAbsPath):
	PLog('update_single:')
	import glob	
	GIT_BASE = "https://github.com/rols1/Kodi-Addon-ARDundZDF/blob/master"
	icon = R("icon-update-einzeln.png")
		
	# Dateiliste SINGLELIST für Einzelupdate:						# 1. Erstellung Liste
	# nicht verwenden: addon.xml + settings.xml (CAddonSettings-error),
	#	changelog.txt, slides.xml, ca-bundle.pem, Icons
	SINGLELIST = ["%s/%s" % (PluginAbsPath, "resources/livesenderTV.xml"),
				"%s/%s" % (PluginAbsPath, "resources/podcast-favorits.txt"),
				"%s/%s" % (PluginAbsPath, "resources/settings.xml"),
				"%s/%s" % (PluginAbsPath, "resources/arte_lang.json"),
				"%s/%s" % (PluginAbsPath, "ardundzdf.py")
		]
	selected=[0,1,2]												# Auswahl-Default: alle, weiter s.u.

	globFiles = "%s/%s/*py" % (PluginAbsPath, "resources/lib")
	files = glob.glob(globFiles) 									# Module -> SINGLELIST 
	files = sorted(files,key=lambda x: x.upper())
	#PLog(files)			# Debug
	for f in files:
		if "__init__.py" in f or ".pem" in f:						# PY2, Zertif.
			continue
		SINGLELIST.append(f)
	#PLog(str(SINGLELIST))		# Debug
	
	#-------------													# 2. Ergänzung ev. neue Module im Repo
	path = "https://github.com/rols1/Kodi-Addon-ARDundZDF/tree/master/resources/lib" # html-Seite, ca. 140 KByte
	cacheID = "GitRepo"
	CacheTime = 60*5										# 5 min.
	page = Dict("load", cacheID, CacheTime=CacheTime)
	if page == False or page == '':							# Cache miss 
		page, msg = get_page(path=path)
		if page:
			Dict("store", cacheID, page) 					# Cache: aktualisieren
			
	RepoList=[]	
	items = blockextract('href="/rols1/Kodi-Addon-ARDundZDF/blob/master/', page)
	PLog("RepoFiles: %d" % len(items))
	for item in items:
		f = stringextract('href="', '"', item)
		f = f.split("blob/master/")[-1]						# Bsp.: resources/lib/ARDnew.py
		if f.endswith("init__.py") or f.endswith(".pem"):	# skip PY2- + Repo-Leichen
			continue
		RepoList.append(f)
	PLog("ModuleRepo: " + str(RepoList))					# Liste github-Module
	
	add_list=[]												# Abgleich Repo/lokal
	for item in RepoList:
		found=False
		#PLog("item: " + item)
		for f in SINGLELIST:								# skip lokale Files, Haupt-PRG, Leichen	
			if f.endswith(item):
				if f.endswith("ardundzdf.py") == False and f.endswith("init__.py") == False:
					#PLog("f: " + f)
					found=True
				break
		if found == False:						# add github-Modul
			add_list.append(item)
	
	PLog("add_list_modules: " + str(add_list))	
	if len(add_list) > 0:
		msg1 = 'NEU und automatisch mit installiert:'
		msg2 = "\n".join(add_list)
		MyDialog(msg1, msg2, '')
		
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
		local_file = local_file.split(PluginAbsPath)[-1]		
		textlist.append(local_file[1:])								# ohne führ. /	(wie Ergebnisliste)
		ret_list.append(cnt)										# default: alle ausgewählt
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

				fname = fname[1:]									# fname ohne führ. /	
				msg2 = "noch aktuell"
				if updated:											# Notification bei Update
					fname = "[B]%s[/B]" % fname								
					msg2 = "aktualisiert"
					xbmcgui.Dialog().notification(fname,msg2,icon,1000)
				else:
					# time < 1000 offensichtlich ignoriert:			# Notification ohne Update
					x=xbmcgui.Dialog().notification("Einzelupdate",fname,icon,1000, False)
					 
				result_list.append("%14s: %s" % (msg2, fname)) 
				xbmc.sleep(1000)									# ohne Pause nachlaufende notifications
			else:
				PLog("nr_local fehlt in %s" % local_file)
	
	#-------------													# 5. Ergänzung ev. neue Module im Repo
	if len(add_list) > 0:
		for item in add_list:
			local_file = "%s/%s" % (PluginAbsPath, item)
			remote_file = "%s/%s?%s" % (GIT_BASE, item, "raw=true")
			remote_file = remote_file.replace('\\', '/')
			PLog('lade %s' % remote_file) 
			try:
				r = urlopen(remote_file)							# Updatedatei auf Github 
				page = r.read()
				if PYTHON3:											# vermeide Byte-Error bei py2_decode			
					page = page.decode("utf-8")
				page = py2_encode(page)
				RSave(local_file, page)
				PLog("NEU: %s" % local_file)
				result_list.append("%14s: %s" % ("Modul NEU", item))
			except Exception as exception:	
				PLog("exept_update_NEU: %s" % str(exception))
			
	#-------------													# 6. Ergebnisliste

	# xbmc.executebuiltin('Dialog.Close(all,true)')					# verhindert nicht Nachlaufen 
	result_list = "\n".join(result_list)							# Ergebnisliste
	title = u"Einzelupdate - Abgleich von %d Dateien | Ergebnis:" % len(ret_list)
	xbmcgui.Dialog().textviewer(title, result_list,usemono=True)
	
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
#		als Array (type 'list') oder als Textdatei in get_data_web (soll
#		korrekte Behandlung alter Cache-Dateien im Webformat verhindern).
#	
def EPG(ID, mode=None, day_offset=None, load_only=False):
	PLog('EPG_ID: ' + ID)
	PLog(mode)
	CacheTime = 43200								# 12 Std.: (60*60)*12
	url="http://www.tvtoday.de/programm/standard/sender/%s.html" % ID
	Dict_ID = "EPG_%s" % ID
	PLog(url)
	
	page = Dict("load", Dict_ID, CacheTime=CacheTime)
	PLog(type(page))
	if page == False or len(page) == 0:									# Cache miss - vom Server holen
		page, msg = get_page(path=url)				
	if 'str' in str(type(page)):										# Webseite
		EPG_dict = get_data_web(page, Dict_ID)							# Web -> 2-dim-Array EPG_rec -> Dict					 
	else:																# EPG_rec = type list 
		EPG_dict = page	
	PLog(len(page))

	# today.de verwendet Unix-Format, Bsp. 1488830442
	now,today,today_5Uhr,nextday,nextday_5Uhr = get_unixtime(day_offset)# lokale Unix-Zeitstempel holen + Offsets
	now_human = datetime.datetime.fromtimestamp(int(now))				# Debug: Übereinstimmung mit UTC, Timezone?	
	now_human =  now_human.strftime("%d.%m.%Y, %H:%M:%S")				# deutsches Format
	day_human = datetime.datetime.fromtimestamp(int(today_5Uhr))
	day_human =  day_human.strftime("%d.%m.%Y")							# deutsches Datumformat für Offset
	PLog('EPG_date_formats:')
	PLog(now); PLog(now_human); PLog(day_human);
	# PLog(today); PLog(today_5Uhr); PLog(nextday); PLog(nextday_5Uhr)	# bei Bedarf

	# Ausgabe: akt. Tag ab 05 Uhr(Start) bis nächster Tag 05 Uhr (Ende)
	EPG_rec=[]															# -> gefilterte Aufbereitung (Zeit, JETZT-Mark.)
	for i in range (len(EPG_dict)):		# ältere + jüngere Sendungen in Liste - daher Schleife + Zeitabgleich	
		rec = []
		r = EPG_dict[i]
		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime,  
		#			5=summ, 6=vonbis, 7=today_human, 8=endtime:  
		starttime=r[0]; href=r[1]; img=r[2]; sname=r[3];				# href=r[1] nicht verwendet
		stime=r[4]; summ=r[5]; vonbis=r[6];today_human=r[7]; 			# today_human=r[8] noch leer
		endtime=r[8];
		
		s_start = 	datetime.datetime.fromtimestamp(int(starttime))		# Zeit-Konvertierung UTC-Startzeit
		s_startday =  s_start.strftime("%A") 							# Locale’s abbreviated weekday name
		iWeekday = transl_wtag(s_startday)
		today_human = iWeekday + ', ' + day_human						# Wochentag + Datum -> tagline
		# PLog("diff_%d: %s, %s-%s" % (i, now, starttime, endtime))		# bei Bedarf
		
		# Auslese - nur akt. Tag 05 Uhr (einschl. Offset in Tagen ) + Folgetag 05 Uhr:
		if starttime < today_5Uhr:										# ältere verwerfen
			# PLog(starttime); PLog(nextday_5Uhr)
			continue
		if starttime > nextday_5Uhr:									# jüngere verwerfen
			# PLog(starttime); PLog(nextday_5Uhr)
			continue	
				
		summ = 	repl_json_chars(summ)
		sname_org = sname	
		if now >= starttime and now < endtime:
			# PLog("diffnow_%d: %s, %s-%s" % (i, now, starttime, endtime))	# bei Bedarf
			# Farb-/Fettmarkierung bleiben im Kontextmenü erhalten (addDir):
			sname = "[B]JETZT: %s[/B]" % sname_org						# JETZT: fett 
			PLog("JETZT: %s, %s" % (sname, img))
			if mode == 'OnlyNow':										# aus EPG_ShowAll - nur aktuelle Sendung
				rec = [starttime,href,img,sname,stime,summ,vonbis]  	# Index wie EPG_rec
				# PLog(rec)
				PLog('EPG_EndOnlyNow')
				return rec												# Rest verwerfen - Ende		

		if endtime < now:												# vergangenes: grau markieren
			sname = "[COLOR grey][B]%s[/B][/COLOR]" % sname_org

		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis, 
		#			7=today_human, 8=endtime:  
		# Link href zum einzelnen Satz hier nicht verwendet - wenig zusätzl. Infos
		rec.append(starttime);rec.append(href); rec.append(img); rec.append(sname);	# Listen-Element
		rec.append(stime); rec.append(summ); rec.append(vonbis); rec.append(today_human);
		rec.append(endtime)
		EPG_rec.append(rec)												# Liste Gesamt (2-Dim-Liste)
	
	PLog(len(EPG_rec)); PLog('EPG_End:')								# Sortierung <- get_data_web
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
def get_data_web(page, Dict_ID):
	PLog("get_data_web:")
	
	# today.de verwendet Unix-Format, Bsp. 1488830442
	now,today,today_5Uhr,nextday,nextday_5Uhr = get_unixtime()# lokale Unix-Zeitstempel, ohne Offset
	
	page  = stringextract('class="tv-show-container', 'id="module-footer"', page)
	liste = blockextract('href="', page)  
	PLog(len(liste));	
	
	EPG_rec = []
	# ältere + jüngere Sendungen in Liste, Zeitabgleich in EPG() bei hier Abruf
	for i in range (len(liste)):		
		# rec: akt. Tag ab 05 Uhr(Start) bis nächster Tag 05 Uhr (Ende):	
		rec = []
		starttime = stringextract('data-start-time=\"', '\"', liste[i]) # Sendezeit, Bsp. "1488827700" (UTC)
		if starttime == '':												# Ende (Impressum)
			break
		endtime = stringextract('data-end-time=\"', '\"', liste[i])	 	# Format wie starttime
		href = stringextract('href=\"', '\"', liste[i])					# wenig zusätzl. Infos
		img = stringextract('srcset="', '"', liste[i])
		img = img.replace('159.', '640.')								# Format ändern "..4415_159.webp"
		
		sname = stringextract('class=\"h7 name\">', '</p>', liste[i])
		sname = unescape(sname); sname = sname.replace('\"', '*')
		stime = stringextract('class=\"h7 time\">', '</p>', liste[i])   # Format: 06:00
		stime = stime.strip()
		summ = get_summ(liste[i])										# Beschreibung holen
		summ = unescape(summ)
		
		sname = "%s | %s" % (stime, sname)								# Titel: Bsp. 06:40 | Nachrichten
		s_start = 	datetime.datetime.fromtimestamp(int(starttime))		# Zeit-Konvertierung UTC-Startzeit
		s_startday =  s_start.strftime("%A") 							# Locale’s abbreviated weekday name
	
		von = stime
		bis = datetime.datetime.fromtimestamp(int(endtime))
		bis = bis.strftime("%H:%M") 
		vonbis = von + ' - ' + bis
	
		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime,  
		#			5=summ, 6=vonbis, 7=today_human, 8=endtime:  
		# Link href zum einzelnen Satz hier nicht verwendet - wenig zusätzl. Infos
		today_human=""													# gesetzt in EPG()
		rec.append(starttime);rec.append(href); rec.append(img); rec.append(sname);	# Listen-Element
		rec.append(stime); rec.append(summ); rec.append(vonbis); rec.append(today_human);
		rec.append(endtime)
		EPG_rec.append(rec)												# Liste Gesamt (2-Dim-Liste)
	
	EPG_rec.sort()														# Sortierung (-> zeitl. Folge)
	Dict("store", Dict_ID, EPG_rec)										# Daten -> Cache: aktualisieren	
	PLog(len(EPG_rec)); PLog('get_data_web_End')
	return EPG_rec
	
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
		
if "'context'" in str(sys.argv):									# Aufruf Kontextmenü
	params = str(sys.argv)
	PLog("context_params: " + params)
	title =  stringextract("title': '", "'", params)
	ID =  stringextract("ID': '", "'", params)
	PLog("title: %s, ID: %s" % (title, ID))
	EPG_rec = EPG(ID, day_offset=0)

	cnt=0
	for rec in EPG_rec:
		sname=rec[3]
		if 'JETZT' in sname:
			PLog(str(rec))
			break
		cnt=cnt+1
	EPG_rec = EPG_rec[cnt:]
	PLog(str(EPG_rec[cnt:]))

	lines=[]
	for rec in EPG_rec:
		try:
			sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6];	# alle Indices s. EPG
			if sname.count("|") > 1:
				sname = sname.split("|")[2]							# So | JETZT: 15:55 | Weltcup-Skispringen
			sname = sname.replace("[/B]", "")
			sname = "%s | %s" % (vonbis,sname)
			lines.append("[B]%s[/B]\n%s\n" % (sname, summ))
		except Exception as exception:
			PLog("EPG_rec_error: " + str(exception))	

	if len(lines) == 0:
		title = "%s | keine EPG-Daten gefunden"	% title
	lines =  "\n".join(lines)
	xbmcgui.Dialog().textviewer(title , lines ,usemono=True)
		
		
		
		
		
		
		
		
		
