# -*- coding: utf-8 -*-
###################################################################################################
#							 epgRecord.py - Teil von Kodi-Addon-ARDundZDF
#							Aufnahmefunktionen für Sendungen in EPG-Menüs
#							Verzicht auf sqlite3, Verwaltung + Steuerung
#									nur mittels Dateifunktionen
#
####################################################################################################
#	01.07.2020 Start
# 	<nr>3</nr>								# Numerierung für Einzelupdate
#	Stand: 16.08.2024

# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys, subprocess, signal 
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse, urlsplit, parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

import time, datetime
import glob
from threading import Thread	
import random						# Zufallswerte für JobID

from resources.lib.util import *
import resources.lib.EPG as EPG

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('epgRecord_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 

JOBFILE			= os.path.join(ADDON_DATA, "jobliste.xml") 		# Jobliste für epgRecord
JOBFILE_LOCK	= os.path.join(ADDON_DATA, "jobliste.lck") 		# Lockfile für Jobliste
JOB_STOP		= os.path.join(ADDON_DATA, "job_stop") 			# Stopfile für JobMonitor
MONITOR_ALIVE 	= os.path.join(ADDON_DATA, "monitor_alive")		# Lebendsignal für JobMonitor (leer, mtime-Abgleich)
DL_CHECK 		= os.path.join(ADDON_DATA, "dl_check_alive") 	# Anzeige Downloads (Thread-Lockdatei)
DL_CNT 			= os.path.join(ADDON_DATA, "dl_cnt") 			# Anzeige Downloads (Zähler)

JOBLINE_TEMPL	= "<startend>%s</startend><title>%s</title><descr>%s</descr><sender>%s</sender><url>%s</url><status>%s</status><pid>%s</pid><JobID>%s</JobID>"
JOB_TEMPL		= "<job>%s</job>"
JOBLIST_TEMPL	= "<jobliste>\n%s\n</jobliste>"
JOBDELAY 		= 60	# Sek.=1 Minute

ICON_DOWNL_DIR	= "icon-downl-dir.png"
MSG_ICON 		= R("icon-record.png")

##################################################################
#---------------------------------------------------------------- 
# Problem: Verwendung der Settings als Statuserkennung unzuverlässig -
#	daher Verwendung von JOB_STOP + MONITOR_ALIVE ähnlich FILTER_SET
#	in FilterTools(). 
#	06.07.2020 zusätzl. direkter Zugriff auf settings.xml via
#		get_Setting (util).
# Abbruch Kodi: 	abortRequested 
# Abbruch intern: 	1. Datei JOB_STOP (fehlendes JOBFILE: kein Abbruch)
#					2. Setting pref_epgRecord (direkt)						
# Lock: wegen mögl. konkur. Zugriffe auf die Jobdatei wird eine Lock-
#	datei verwendet (JobMain, Monitor)
# Job-Bereich: Aufnahme-Jobs (ffmpeg, m3u8) - Erzeugung: K-Menü 
#	EPG_ShowSingle -> ProgramRecord -> JobMain.
# Aufnahmestart nach Zeitabgleich mit Call LiveRecord:
#	1. ffmpeg-Verfahren via LiveRecord, hier Ablage PIDffmpeg im Job
#	2. m3u8-Verfahren via LiveRecord (-> direkt m3u8.Main_m3u8, hier 
#		 Ablage Thread_JobID als PIDffmpeg im Job)
#	 
# Verfahren Recording-TV-Live-Jobs: LiveRecord erzeugt Job via JobMain +
#	startet direkt ffmpeg oder m3u8-Verfahren (je nach Setting) 
# 30.08.2020 experimentelles m3u8-Verfahren entf.
# 19.07.2021 Aufschlag Sommerzeit in JobMonitor, Funktion get_summer_unix_time -
# 	entf. mit Anpassung JOBDELAY

def JobMonitor():
	PLog("JobMonitor:")
	pre_rec  = SETTINGS.getSetting('pref_pre_rec')			# Vorlauf (Bsp. 00:15:00 = 15 Minuten)
	post_rec = SETTINGS.getSetting('pref_post_rec')			# Nachlauf (dto.)
	pre_rec = re.search('= (\d+) Min', pre_rec).group(1)
	post_rec = re.search('= (\d+) Min', post_rec).group(1)
	if pre_rec == '0':
		pre_rec = JOBDELAY/60								# Ausgleich Intervall 
		
	if os.path.exists(JOB_STOP):							# Ruine?		
		os.remove(JOB_STOP)	
	
	old_age=0
	if os.path.exists(JOBFILE):	
		jobs = ReadJobs()										# s. util
		old_age = os.stat(JOBFILE).st_mtime						# Abgleich in Monitor (z.Z. n.verw.)
	else:
		jobs = []
	PLog("JOBFILE_old_age: %d" % old_age)
	
	i=0
	monitor = xbmc.Monitor()
	while not monitor.abortRequested():
		i=i+1
		PLog("Monitor_Lauf: %d" % i)
		
		if get_Setting('pref_epgRecord') == 'false':		# direkter Zugriff (s.o.)
			PLog("Monitor: pref_epgRecord false - stop")
			xbmcgui.Dialog().notification("Aufnahme-Monitor:","gestoppt",MSG_ICON,3000)
			break
		
		open(MONITOR_ALIVE, 'w').close()					# Lebendsignal - Abgleich mtime in JobMain

		xbmc.sleep(JOBDELAY * 1000)							# Pause
		# xbmc.sleep(2000)	# Debug
		if os.path.exists(JOB_STOP): 
			PLog("Monitor: JOB_STOP gefunden - stop")
			xbmcgui.Dialog().notification("Aufnahme-Monitor:","gestoppt",MSG_ICON,3000)
			break
				
		if os.path.exists(JOBFILE):							# bei jedem Durchgang neu einlesen
			jobs = ReadJobs()
		else:
			jobs = []
			
		now = EPG.get_unixtime(onlynow=True)
		now = int(now)
		now_human = date_human("%Y.%m.%d_%H:%M:%S", now='')			# Debug	
		
		#---------------------------------------------------		# Schleife Jobliste		
		PLog("scan_jobs:")
		newjob_list = []; cnt=0; job_changed = False				# newjob_list: Liste nach Änderungen
		for cnt in range(len(jobs)):
			myjob = jobs[cnt]
			PLog(myjob[:80])			
			status 	= stringextract('<status>', '</status>', myjob)
			PLog("scan_Job %d status: %s" % (cnt+1, status))			
												
			start_end 	= stringextract('<startend>', '</startend>', myjob)
			start, end = start_end.split('|')						# 1593627300|1593633300
			start = int(start); end = int(end);
				
			#start = get_summer_unix_time(start)					# entf. mit Anpassung JOBDELAY 
			#end = get_summer_unix_time(end)
			PLog("end - start1: %d" % (end-start))

			start 	= start - (int(pre_rec) * 60)						# Vorlauf (Min -> Sek) abziehen
			end 	= end + (int(post_rec) * 60)						# Nachlauf (Min -> Sek) aufschlagen 
			PLog("end - start2: %d" % (end-start))
			
			start_human = date_human("%Y.%m.%d_%H:%M:%S", now=start)
			mydate = date_human("%Y%m%d_%H%M%S", now=now)			# Zeitstempel für titel in LiveRecord	
			end_human= date_human("%Y.%m.%d_%H:%M:%S", now=end)			
			
			duration = end - start									# in Sekunden für ffmpeg

			diff = start - now
			vorz=''
			if diff < 0: 
				vorz = "minus "
			diff = seconds_translate(diff)	
			
			laenge = ""; PIDffmpeg=''								# laenge entfällt hier
			# PLog("now %s, start %s, end %s" % (now, start, end))  # Debug
			PLog("now %s, start %s, end %s, start-now: %s, dur: %s" % (now_human,start_human,end_human,diff,duration))
			
			#---------------------------------------------------	# 1 Job -> Aufnahme		
			if (now >= start and now <= end) and status == 'waiting':	# Job ist aufnahmereif
				PLog("Job ready: " + start_end)	
				duration = end - now								# Korrektur, falls start schon überschritten
				url = stringextract('<url>', '</url>', myjob)
				JobID = stringextract('<JobID>', '</JobID>', myjob)
				sender = stringextract('<sender>', '</sender>', myjob)
				title = stringextract('<title>', '</title>', myjob)
				title = "%s: %s" % (sender, title)					# Titel: Sender + Sendung
				descr = stringextract('<descr>', '</descr>', myjob)
				
				started = date_human("%Y.%M.D_%H:%M:%S", now=start)
				dfname = make_filenames(title.strip()) 				# Name aus Titel
																	# Textdatei
				txttitle = "%s_%s" % (mydate, dfname)				# Zeitstempel wie inLiveRecord  
				detailtxt = MakeDetailText(title=txttitle,thumb='',quality='Livestream',
					summary=descr,tagline='',url=url)
				detailtxt=py2_encode(detailtxt); txttitle=py2_encode(txttitle);		
				storetxt = 'Details zur Aufnahme ' +  txttitle + ':\r\n\r\n' + detailtxt
				dest_path = SETTINGS.getSetting('pref_download_path')
				textfile = txttitle + '.txt'
											
				dfname = dfname + '.mp4'							# LiveRecord ergänzt Zeitstempel 
				textfile = py2_encode(textfile)	 
				pathtextfile = os.path.join(dest_path, textfile)
				storetxt = py2_encode(storetxt)
				RSave(pathtextfile, storetxt)						# Begleitext speichern				
						
				# duration = "00:00:10"	# Debug: 10 Sec.
				PLog("Satz:")
				PLog(url); PLog(title); PLog(duration); PLog(detailtxt); PLog(started);
								
				myjob = myjob.replace('<status>waiting', '<status>gestartet')
				PLog("Job %d started" % cnt)
				job_changed = True
				
				PIDffmpeg = LiveRecord(url, title, duration, laenge='', epgJob=mydate, JobID=JobID) # Aufnehmen
				myjob = myjob.replace('<pid></pid>', '<pid>%s</pid>' % PIDffmpeg)

			#---------------------------------------------------	# Job zurück in Liste		
			jobs[cnt] = JOB_TEMPL % myjob							# Job -> Listenelement
			PLog("Job %d PIDffmpeg: %s" % (cnt+1, PIDffmpeg))
			cnt=cnt+1												# und nächster Job
			
		#---------------------------------------------------		# Jobliste speichern, falls geändert	
		if job_changed:											
			newjobs = "\n".join(jobs)					
			page = JOBLIST_TEMPL % newjobs							# Jobliste -> Marker
			page = py2_encode(page)
			PLog(u"geänderte Jobliste speichern:")
			PLog(page[:80])
			open(JOBFILE_LOCK, 'w').close()							# Lock ein				
			err_msg = RSave(JOBFILE, page)							# Jobliste speichern
			xbmc.sleep(500)
			if os.path.exists(JOBFILE_LOCK):						# Lock aus
				os.remove(JOBFILE_LOCK)	
						
	if os.path.exists(MONITOR_ALIVE):								# Aufräumen nach Monitor-Ende
		os.remove(MONITOR_ALIVE)
		
	return
	
#---------------------------------------------------
# timecode: Unix-Zeit in sec
# Aufschlag 1 Std. während der Sommerzeit
# Sommerzeit jährlich aktualisieren (www.ptb.de)
# 23.07.2021 z.Z. nicht genutzt
def get_summer_unix_time(timecode):
	PLog("get_summer_unix_time:")
	PLog(timecode); 
	summ_start 	= 1616893200									# Sommerzeit 2021 Unix Start	
	summ_end 	= 1635642000									# Sommerzeit 2021 Unix Ende	
	timecode = int(timecode)
	if (timecode > summ_start) and (timecode < summ_end):		# add 1 Std.
		PLog(datetime.datetime.fromtimestamp(float(timecode)))	# Debug
		PLog("add_1_Std")
		timecode = timecode + 3600

	PLog(timecode); 
	PLog(datetime.datetime.fromtimestamp(float(timecode)))		# Debug
	return timecode

######################################################################## 
# 
# Aufrufer:
#	action init: bei jedem Start ardundzdf.py (bei Setting pref_epgRecord)
# 	action stop: DownloadTools
#	action setjob: ProgramRecord, LiveRecord (ohne EPG)
# 
# Checks auf ffmpegCall + download_path in ProgramRecord
# Problem : bei Abstürzen (network error) kann das Lebendsignal
#	MONITOR_ALIVE als Ruine stehenbleiben. Lösung: falls mtime
#	mehr als JOBDELAY zurückliegt, gilt Monitor als tot - init ist 
#	wieder möglich.
# 	threading.enumerate() hier nicht geeignet (liefert nur MainThread)
#	
def JobMain(action, start_end='', title='', descr='',  sender='', url='', setSetting='', PIDffmpeg=''):
	PLog("JobMain:")
	PLog(action); PLog(sender); PLog(title);  
	PLog(descr); PLog(start_end); PLog(PIDffmpeg);	
	
	# mythreads = threading.enumerate()								# liefert in Kodi nur MainThread
	status = os.path.exists(MONITOR_ALIVE)
	PLog("MONITOR_ALIVE pre: " + str(status))						# Eingangs-Status	
	now = EPG.get_unixtime(onlynow=True)				
	
	#------------------------
	if action == 'init':											# bei jedem Start ardundzdf.py
		if setSetting:												# Aufruf: DownloadTools
			SETTINGS.setSetting('pref_epgRecord', 'true')
			xbmcgui.Dialog().notification("Aufnahme-Monitor:","Start veranlasst",MSG_ICON,3000) 
			xbmc.executebuiltin('Container.Refresh')
			return
			
		if os.path.exists(MONITOR_ALIVE):							# check Lebendsignal
			mtime = os.stat(MONITOR_ALIVE).st_mtime
			diff = int(now) - mtime
			PLog("now: %s, mtime: %d, diff: %d" % (now, mtime, diff))

			if diff > JOBDELAY:										# Monitor tot? 
				PLog("alive_veraltet: force init")					# abhängig von JOBFILE, s.u.
				os.remove(MONITOR_ALIVE)
			else:
				PLog("alive_aktuell: return")		
				return
		else:
			PLog("alive_fehlt: force init")							# dto.
				
		if check_file(JOBFILE) == False:							# JOBFILE leer/fehlt - kein Hindernis
			PLog("Aufnahmeliste leer")
			
		if os.path.exists(MONITOR_ALIVE) == False:					# JobMonitor läuft bereits?
			bg_thread = Thread(target=JobMonitor,					# sonst Thread JobMonitor starten
				args=())
			bg_thread.start()
			xbmcgui.Dialog().notification("Aufnahme-Monitor:","gestartet",MSG_ICON,3000)
		else:
			PLog("running - skip init")
		return		
					
	#------------------------
	if action == 'stop':											# DownloadTools <-
		jobs = ReadJobs()											# s. util
		now = EPG.get_unixtime(onlynow=True)
		job_active = False
		PLog('Mark0')
		for job in jobs:
			start_end 	= stringextract('<startend>', '</startend>', job)
			start, end = start_end.split('|')						# 1593627300|1593633300					
			if int(start) > int(now):
				job_active = True
				break

		if job_active:
			title = 'Aufnahme-Monitor stoppen'					
			msg1 = "Mindestens ein Aufnahmejob ist noch aktiv!"
			msg2 = "Aufnahme-Monitor trotzdem stoppen?"
			ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
			if ret !=1:
				return
			
		open(JOB_STOP, 'w').close()	# STOPFILE anlegen				
		SETTINGS.setSetting('pref_epgRecord', 'false')				# Setting muss manuell wieder eingeschaltet werden
		PLog("JOB_STOP set")										# Status
		xbmc.executebuiltin('Container.Refresh')
		xbmcgui.Dialog().notification("Aufnahme-Monitor:","Stop veranlasst",MSG_ICON,3000) # Notification im Monitor
		# test_jobs		# Debug
		return
		
	#------------------------
	# die für Recording Live (LiveRecord) erzeugten Jobs werden nicht im JobMonitor
	# 	abgearbeitet, sondern direkt in m3u8.Main_m3u8 - entfallen mit Ende des 
	#   experimentellen m3u8-Aufnahmeverfahrens 30.08.2020
	if action == 'setjob':							# neuen Job an Aufnahmeliste anhängen + Bereinigung: Doppler
													# 	verhindern, Einträge auf pref_max_reclist beschränken
		title = cleanmark(title)					# Farbe/fett aus ProgramRecord
		block = '4Yp2C09aF1k5YC3d'
		JobID = ''.join(random.choice(block) for i in range(len(block)))  # 16 stel. Job-ID
		if "Recording Live" in descr:				# Aufruf: LiveRecord, Start ohne EPG
			status = 'gestartet'					# -> <status>,  für JobMonitor tabu 
			pid = "Thread_%s" % JobID				# -> KillFile (JobRemove) - wie JobMonitor
		else:
			status = 'waiting'	
			if 	PIDffmpeg:							# Aufruf: LiveRecord via ffmpeg
				status = 'gestartet'				# -> <status>,  für JobMonitor tabu 
			pid = PIDffmpeg							# aus LiveRecord direkt oder via JobMonitor	
		
		job_line = JOBLINE_TEMPL % (start_end,title,descr,sender,url,status,pid,JobID)
		new_job = JOB_TEMPL % job_line
		PLog(new_job[:80])
		jobs = ReadJobs()											# s. util
	
		job_list = []; cnt=0										# Neubau Jobliste
		# Kontrolle erweitern, falls startend + sender nicht eindeutig genug:
		for job in jobs:
			list_startend 	= stringextract('<startend>', '</startend>', job)
			list_sender 	= stringextract('<sender>', '</sender>', job)
			if list_startend == start_end and list_sender == sender:	# Kontrolle Doppler
				msg1 = "%s: %s\nStart/Ende (Unix-Format): %s" % (sender, title, start_end)
				msg2 = "Sendung ist bereits in der Jobliste - Abbruch"
				MyDialog(msg1, msg2, '')
				PLog("%s\n%s" % (msg1, msg2))
				return												# alte Liste unverändert
			else:
				job_list.append(JOB_TEMPL % job)					# job -> Marker
				cnt=cnt+1
		
		new_job = py2_encode(new_job)											
		job_list.append(new_job)									# neuen Job anhängen
		maxlen = int(SETTINGS.getSetting('pref_max_reclist'))
		if len(job_list) > maxlen: 
			while len(job_list) > maxlen: 
				del job_list[0]											# 1. Satz entf.
				PLog('%d/%d, Job entfernt: %s' % (maxlen, len(job_list), job_list[0]))
		jobs = "\n".join(job_list)					
		page = JOBLIST_TEMPL % jobs									# Jobliste -> Marker
		page = py2_encode(page)
		PLog(page[:80])
			
		open(JOBFILE_LOCK, 'w').close()								# Lock ein				
		err_msg = RSave(JOBFILE, page)								# Jobliste speichern
		if os.path.exists(JOBFILE_LOCK):							# Lock aus
			os.remove(JOBFILE_LOCK)	
		
		xbmcgui.Dialog().notification("Aufnahme-Monitor:", "Job hinzugefügt",MSG_ICON,3000)
		PLog("JobID: %s" % JobID)
		if "ffmpeg-recording" in descr:								# LiveRecord ffmpeg  
			return JobID
		else:			
			if os.path.exists(MONITOR_ALIVE) == False:				# JobMonitor läuft bereits?
				bg_thread = Thread(target=JobMonitor,				# sonst Thread JobMonitor starten
					args=())
				bg_thread.start()
		return
	#------------------------
	if action == 'listJobs':										# Liste, Job-Status, Jobs löschen
		JobListe()
		return	

	#------------------------
	if action == 'deljob':											# Job aus Aufnahmeliste entfernen
		JobRemove()
		return	
		
	#------------------------
	if action == 'test_jobs':										# Testfunktion
		test_jobs()
		return	

##################################################################
#---------------------------------------------------------------- 
# 31.12.2023 Bereinigung KillFile-Ruinen entfernt (obsolet)
# 13.08.2024 Button "abgelaufene Jobs löschen"  ergänzt, Liste der 
#	zu löschenden in JobID_list -> JobRemoveExp.
# 
def JobListe():														# Liste, Job-Status, Jobs löschen
	PLog("JobListe:")
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)											# Home-Button
	
	if os.path.exists(JOBFILE):	
		jobs = ReadJobs()											# s. util
		if len(jobs) == 0:
			xbmcgui.Dialog().notification("Jobliste:", "keine Aufnahme-Jobs vorhanden",MSG_ICON,3000)	
	else:
		xbmcgui.Dialog().notification("Jobliste:", "nicht gefunden",MSG_ICON,3000)
		
	now = EPG.get_unixtime(onlynow=True)
	now = int(now)
	
	now_human = date_human("%d.%m.%Y, %H:%M", now='')
	pre_rec  = SETTINGS.getSetting('pref_pre_rec')					# Vorlauf (Bsp. 00:15:00 = 15 Minuten)
	post_rec = SETTINGS.getSetting('pref_post_rec')					# Nachlauf (dto.)
	pre_rec = re.search('= (\d+) Min', pre_rec).group(1)
	post_rec = re.search('= (\d+) Min', post_rec).group(1)
	anz_jobs = len(jobs)
	jobs.sort()
		
	exp_cnt=0; JobID_list=[]
	for cnt in range(len(jobs)):
			myjob = jobs[cnt]
			PLog(myjob[:80])			
			status 	= stringextract('<status>', '</status>', myjob)
			status_real = status									# wird aktualisiert s.u.
			PLog("JobListe_Job %d status: %s" % (cnt+1, status))			
																		
			start_end	= stringextract('<startend>', '</startend>', myjob)
			start, end 	= start_end.split('|')						# 1593627300|1593633300	
			start = int(start); end = int(end)	
			descr = stringextract('<descr>', '</descr>', myjob)
			PLog(descr)
			if 	"Recording Live" in descr == False:					# Vor- und Nachlauf entfallen
				pass
			else:	
				start 		= int(start) - int(pre_rec) * 60		# Vorlauf (Min -> Sek) abziehen
				end 		= int(end) + int(post_rec) * 60			# Nachlauf (Min -> Sek) aufschlagen 
			mydate = date_human("%Y%m%d_%H%M%S", now=start)			# Zeitstempel für titel in LiveRecord	
			start_human = date_human("%d.%m.%Y, %H:%M", now=start)
			end_human = date_human("%d.%m.%Y, %H:%M", now=end)
			
			pid = stringextract('<pid>', '</pid>', myjob)
			title = stringextract('<title>', '</title>', myjob)
			job_title = title										# Abgleich in JobRemove alt
			JobID = stringextract('<JobID>', '</JobID>', myjob)		# Abgleich in JobRemove neu
			sender = stringextract('<sender>', '</sender>', myjob)
			dfname = title.strip()									# Recording Live: ohne Sender
			if sender:
				dfname = "%s: %s" % (sender, title)					# Titel: Sender + Sendung (mit Mark.)
			dfname = make_filenames(dfname.strip()) + ".mp4"		# Name aus Titel
			dfname = "%s_%s" % (mydate, dfname)						# wie LiveRecord
			dest_path = SETTINGS.getSetting('pref_download_path')
			video =  os.path.join(dest_path, dfname)
			PLog("video: " + video)
			status_add = ""
			if os.path.exists(video):
				status_add = " | Video vorhanden: %s.." % dfname[:28] 	# für Infobereich begrenzen
			else:
				status_add = " | Video fehlt: %s.." % dfname[:28]		# dto.
			
			title = cleanmark(title)
			title = title.replace("JETZT: ", '')
			
			img = MSG_ICON										# rot
			PLog(" end %s, now %s" % (end, now))
			job_active = False
			if end < now:										# abgelaufen
				img = R("icon-record-grey.png")					# grau
				if status == "gestartet":
					status_real = "[B] Jobstatus: Aufnahme wurde gestartet [/B]" + status_add
				else:
					status_real = "[B] Jobstatus: Aufnahme wurde nicht gestartet [/B] - Ursache nicht bekannt"
				JobID_list.append(JobID)						# 	
				exp_cnt=exp_cnt+1
			else:												# noch aktiv
				img = MSG_ICON									# grau
				job_active = True
				status_real = "Aufnahme geplant: %s" % start_human
				
			label = u'Job löschen: %s'	% title 
			if job_active:
				label = u'Job stoppen / löschen: %s'	% title 				
			tag = u'Start: [B]%s[/B], Ende: [I][B]%s[/B][/I]' % (start_human, end_human)
			tag = u'%s\n%s' % (tag, status_real)
			
			max_reclist = SETTINGS.getSetting('pref_max_reclist')
			summ = u'[B]Anzahl Jobs[/B] in der Aufnahmeliste: %s' % (anz_jobs)
			summ = u"%s\n[B]Settings[/B]:\n[B]max. Größe der Aufnahmeliste:[/B] %s Jobs," % (summ, max_reclist)
			summ = u"%s[B]Vorlauf:[/B] %s Min., [B]Nachlauf:[/B] %s Min." % (summ, pre_rec, post_rec)
			fparams="&fparams={'sender':'%s','job_title':'%s','start_end':'%s','job_active':'%s','pid':'%s','JobID':'%s'}" %\
				(sender, job_title, start_end, job_active, pid, JobID)
			addDir(li=li, label=label, action="dirList", dirID="resources.lib.epgRecord.JobRemove", fanart=R(ICON_DOWNL_DIR), 
				thumb=img, fparams=fparams, tagline=tag, summary=summ)
	
	if exp_cnt > 0:		
		label = u'abgelaufene Jobs [B](%d)[/B] ohne Rückfrage löschen.' % exp_cnt
		tag = u"nicht beendete und künftige Jobs bleiben erhalten."
		Dict("store", "JobID_list", JobID_list)
		fparams="&fparams={'Dict_ID':'%s'}" % "JobID_list"
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.epgRecord.JobRemoveExp", fanart=R("icon-delete.png"), 
			thumb=R("icon-delete.png"), fparams=fparams, tagline=tag)
				

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#----------------------------------------------------------------
# Aufrufer: JobListe
# Ablauf: Liste einlesen, Einträge in Schleife abgleichen, gefundenen
#			Satz verwerfen, verkleinerte Liste mit Lock speichern
# job_title: unbehandelt, mit ev. Mark.
# title + start_end: als ID nur noch aus Kompat. verwenden(Kodier-
#			Problem möglich)
# 13.07.2020 JobID als eindeutige ID ergänzt
#
def JobRemove(sender, job_title, start_end, job_active, pid, JobID):
	PLog("JobRemove:")
	PLog(pid); PLog(JobID); PLog(job_active), PLog(start_end)
		
	if job_active == 'True':									# Abzweig Stoppen
		heading	= u"Job stoppen / löschen"
		msg1 	= "Job nur stoppen?"
		msg2 	= "Job verbleibt in der Liste, kann aber nicht mehr gestartet werden"
		ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel=u'Nein - löschen', 
			yes='JA - nur stoppen', heading=heading)
		if ret ==1:
			JobStop(sender, job_title, start_end, job_active, pid, JobID)
			return
		
	if sender:													# fehlt beim Recording
		msg1 = "%s: %s" % (sender, job_title)
	else:
		msg1 = job_title

	heading = u"Job aus Aufnahmeliste löschen"
	pidtxt=''
	if pid:
		pidtxt = " (PID %s) " % pid
	if job_active == 'True' and pid:
		msg2 = u"Job %s tatsächlich abbrechen und löschen?" % pidtxt
		heading = u"aktiven (!) %s!" % heading
		icon = MSG_ICON
	else:
		msg2 = u"Job tatsächlich löschen?" 
		heading = "abgelaufenen %s" % heading
		icon = R("icon-record-grey.png")
		
	ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=heading)
	if ret !=1:
		return
	
	if job_active == 'True' and pid != '':
		PLog("kill_pid: %s" % str(pid))
		os.kill(int(pid), signal.SIGTERM)						# auch Windows10 OK (aber Teilvideo beschäd.)
	
	jobs = ReadJobs()											# s. util
	newjob_list = []; 											# newjob_list: Liste nach Änderungen
	job_title=py2_encode(job_title); 							# type kann vom code-Format in jobs abweichen
	for job in jobs:
		my_start_end 	= stringextract('<startend>', '</startend>', job)
		my_title 		= stringextract('<title>', '</title>', job)
		my_JobID 		= stringextract('<JobID>', '</JobID>', job)
		if JobID:												# neuer Abgleich
			if JobID == my_JobID:
				PLog('JobID_OK: %s' % JobID)
				continue
		else:													# alter Abgleich
			if start_end == my_start_end and job_title == my_title: 
				PLog('start_end_title_OK: %s' % start_end)
				continue
		newjob_list.append(JOB_TEMPL % job)						# job -> Marker
		
	save_Joblist(jobs, newjob_list, "Jobliste:", u"Job gelöscht")	
	return
	
#----------------------------------------------------------------
# Aufrufer: JobListe
# Ablauf: löscht aus der Jobliste die Jobs, die mit den via Dict_ID
#	übergebenen JobID's übereinstimmen 
#
def JobRemoveExp(Dict_ID):
	PLog("JobRemoveExp: " + Dict_ID)
	JobID_list = Dict("load", Dict_ID)
	PLog("JobID_list: " + str(JobID_list))
	
	jobs = ReadJobs()
	jobs.sort()
	PLog("jobs: %d" % len(jobs))
	
	newjob_list=[]; del_cnt=0
	for job in jobs:
		JobID = stringextract('<JobID>', '</JobID>', job)
		PLog("JobID: " + JobID)
		if JobID in JobID_list:											# Satz verwerfen
			del_cnt=del_cnt+1
		else:
			job = JOB_TEMPL % job										# <job>%s</job>
			newjob_list.append(job)

	PLog("newjob_list: %d" % len(newjob_list))
	save_Joblist(jobs, newjob_list, "Jobliste:", "")					# -> JOBLIST_TEMPL, ohne notification dort
	icon = MSG_ICON
	xbmcgui.Dialog().notification("Jobliste:",u"%d Job(s) gelöscht." % del_cnt,icon,3000)
	
	return			

#----------------------------------------------------------------
# wie JobRemove - nur stoppen, ohne Änderung der Jobliste
# Aufruf: Kontextmenü Jobliste
#
def JobStop(sender, job_title, start_end, job_active, pid, JobID):
	PLog("JobStop:")
	PLog(pid); PLog(JobID); PLog(job_active), PLog(start_end)

	if sender:													# fehlt beim Recording
		msg1 = "%s: %s" % (sender, job_title)
	else:
		msg1 = job_title

	PLog("kill_pid: %s" % str(pid))
	if pid:														# int-error falls leer
		os.kill(int(pid), signal.SIGTERM)						# auch Windows10 OK (aber Teilvideo beschäd.)
		icon = MSG_ICON
		xbmcgui.Dialog().notification("Jobliste:", u"Job wird gestoppt",icon,3000)

	now = EPG.get_unixtime(onlynow=True)
	jobs = ReadJobs()											# s. util
	newjob_list = []; 											# newjob_list: Liste nach Änderungen
	job_title=py2_encode(job_title); 							# type kann vom code-Format in jobs abweichen
	for job in jobs:
		my_JobID = stringextract('<JobID>', '</JobID>', job)
		if JobID in my_JobID:									# sonst unverändert
			my_start_end = stringextract('<startend>', '</startend>', job)
			start, end = my_start_end.split('|')	
			end = int(now)-1 									# end anpassen (Job abgelaufen)
			new_start_end = "%s|%d"	% (start, end)
			job = job.replace(my_start_end, new_start_end)		# job: <startend></startend> ändern
			PLog(my_start_end); PLog(new_start_end);	
				
		newjob_list.append(JOB_TEMPL % job)						# job -> Marker
		
	save_Joblist(jobs, newjob_list, "Jobliste:", "")			# ohne notification
	return
#---------------------------------------------------------------- 
def save_Joblist(jobs, newjob_list, header, msg):
	PLog("save_Joblist")
	
	PLog(len(jobs))			
	jobs = "\n".join(newjob_list)
	page = JOBLIST_TEMPL % jobs									# Jobliste -> Marker
	page = py2_encode(page)
	if doLock(JOBFILE_LOCK):									
		err_msg = RSave(JOBFILE, page)							# Jobliste speichern
		xbmc.sleep(500)
	doLock(JOBFILE_LOCK, remove=True)
	if err_msg == '':
		if msg:													# ohne notification bei Stoppen (msg='')
			icon = R("icon-record-grey.png")
			xbmcgui.Dialog().notification(header,msg,icon,3000)
	else:
		icon = MSG_ICON
		xbmcgui.Dialog().notification(header,u"Problem beim Speichern",icon,3000)
	return
#---------------------------------------------------------------- 
# simpler Lock-Mechanismus
#	Aufrufer: 	1. checkLock (remove=False)
#				2. Datei speichern
#				3. checkLock (remove=True)
#	checkLock sorgt für Verzögerung (maxLockloops),
#		räumt eine ev. Ruine ab + setzt Lockfile 
#	mit Param. remove entfernt checkLock das Lock
#		sofort (i.d.R. nach dem Speichern)
# Bei Bedarf mit Modul Lockfile erweitern:
#	https://pypi.org/project/lockfile/
#
def doLock(lockfile, remove=False):
	PLog("doLock: " + str(remove))
	maxloops	= 10				# 1 sec bei 10 x xbmc.sleep(100)	

	if remove:
		if os.path.exists(lockfile):
			os.remove(lockfile)
			return True
			
	while os.path.exists(lockfile):	
		i=i+1
		if i >= maxloops:		# Lock brechen, vermutl. Ruine
			os.remove(lockfile)
			PLog("doLock_break: " + lockfile)
			break
		xbmc.sleep(100)	
	
	try:							# Lock setzen
		open(JOBFILE_LOCK, 'w').close()
	except Exception as exception:
		msg = str(exception)
		PLog('doLock_Exception: ' + msg)
		return False
			
	return True
#---------------------------------------------------------------- 
# gibt Unixzeit im lesbaren Format myformat zurück.
#	Formate s. https://strftime.org/
# falls now leer, wird die akt. Zeit ermittelt (lokal)
#
def date_human(myformat, now=''):
	PLog("date_human:")

	if now == '':
		now = EPG.get_unixtime(onlynow=True)
	
	s = datetime.datetime.fromtimestamp(float(now))
	date_human = s.strftime(myformat)	
	return date_human
	
##################################################################
#---------------------------------------------------------------- 
# nur Debug: Jobliste mit ausgewähltenJobs, Startzeit: jetzt + 1 Min.,
#		Aufnahmezeit 10 Sec. (Endzeit: Startzeit + 10 Sec.)
#		Ablage: direkt als JOBFILE nach ADDON_DATA (ohne Warnung!)
#				
def test_jobs():	
	PLog("test_jobs:")
	# "Das Erste|https://mcdn.daserste.de/daserste/de/master.m3u8"  - funkt. nicht
	mylist = [ 		"Das Erste|https://derste247livede.akamaized.net/hls/live/658317/daserste_de/profile1/1.m3u8",
					"BR Fernsehen-Nord|http://brlive-lh.akamaihd.net/i/bfsnord_germany@119898/master.m3u8", 
					"hr-fernsehen|https://hrlive1-lh.akamaihd.net/i/hr_fernsehen@75910/master.m3u8",
					"MDR Sachsen|https://mdrsnhls-lh.akamaihd.net/i/livetvmdrsachsen_de@513998/master.m3u8",
					"Radio Bremen|https://rbfs-lh.akamaihd.net/i/rb_fs@438960/master.m3u8", 
					"NDR Niedersachsen|https://ndrfs-lh.akamaihd.net/i/ndrfs_nds@430233/master.m3u8", 
					"NDR Hamburg|https://ndrfs-lh.akamaihd.net/i/ndrfs_hh@430231/master.m3u8", 
					"SR Fernsehen|https://srlive24-lh.akamaihd.net/i/sr_universal02@107595/master.m3u8",
					"Tagesschau24|http://tagesschau-lh.akamaihd.net/i/tagesschau_1@119231/master.m3u8",
					"Deutsche Welle|https://dwstream72-lh.akamaihd.net/i/dwstream72_live@123556/master.m3u8", 
					"One|http://onelivestream-lh.akamaihd.net/i/one_livestream@568814/master.m3u8",
				]
	add_sec = 10
	
	now = EPG.get_unixtime(onlynow=True)
	now = int(now)
	end = now + 2*add_sec
	now = now + add_sec

	job_list = []; i=0
	for item in mylist:
		i=i+1
		sender, url = item.split('|') 
		PLog("job %s" % str(i))
		end = now + 2*add_sec
		now = now + add_sec
		title = "Testjob %s" % str(i)
		start_end = "%s|%s" % (str(now), str(end))
		descr = u"Debug: Jobliste mit ausgewählten Jobs, Startzeit: jetzt + 10 Sec., Aufnahmezeit 10 Sec. (Endzeit: Startzeit + 10 Sec.)"
		status = "waiting"
		pid = ''
		block = '4Yp2C09aF1k5YC3d'
		JobID = ''.join(random.choice(block) for i in range(len(block)))  # 16 stel. Job-ID
		
		job = JOBLINE_TEMPL % (start_end,title,descr,sender,url,status,pid,JobID)
		job_list.append(JOB_TEMPL % job)					# job -> Marker
	
	jobs = "\n".join(job_list)	
	page = JOBLIST_TEMPL % jobs								# Jobliste -> Marker
	page = py2_encode(page)
	PLog(page[:80])
	
	err_msg = RSave(JOBFILE, page)							# Jobliste -> Livesystem
	return
	
#---------------------------
# Anzeige laufender Downloads einschl. Bilder
# Setting "Download Einstellungen"/"laufende Downloads anzeigen"
# Aufruf beim Start Haupt-PRG (nach EPG)
# threading.active_count() funktioniert in der Kodi-Umgebung nicht zuverl.,
#	daher Kommunikation via Datei dl_cnt
#
def get_active_dls():
	PLog('get_active_dls_start:')
	import threading
			
	xbmc.sleep(1000)							# Pause für Datei-OP durch Haupt-PRG		
			
	open(DL_CHECK, 'w').close()					# Lock dl_check_alive anlegen
	PLog("dl_check_alive_angelegt")
		
	icon = R('icon-downl.png')
	monitor = xbmc.Monitor()
	i=0
	while not monitor.abortRequested():			# Abbruch durch Kodi
		if os.path.exists(DL_CHECK) == False:	# Abbruch durch Addon 
			break
		if SETTINGS.getSetting('pref_dl_cnt') == 'false': # dopp. Sicherung
			break	
		
		if os.path.exists(DL_CNT):
			with open(DL_CNT,'r') as f: 
				line=f.read()
				cnt, new_len = line.split("|")
				if new_len == '0' or  new_len == '':
					new_len = u"Größe unbekannt"
				else:
					new_len = humanbytes(new_len)
		else:
			cnt=''	
		# PLog("%d.dlcnt: %s" %  (i, cnt)) # Debug
		if cnt != '' and cnt != '0':
			msg1 = "Downloads"
			msg2 = "Anzahl: %s | %s" % (cnt, new_len)
			PLog("get_active_dls_update: %s" % msg2)
			xbmcgui.Dialog().notification(msg1,msg2,icon,2000)
		i=i+1
		xbmc.sleep(2000)

	PLog('get_active_dls_stop:')
	#--------------------------					# Abbruch durch Addon oder Kodi
	if os.path.exists(DL_CHECK):		
		os.remove(DL_CHECK)						# Lock dl_check_alive entfernen
		PLog("dl_check_alive_entfernt")
	if os.path.exists(DL_CNT):
		os.remove(DL_CNT)						# Zähler dl_cnt entfernen
		PLog("dl_cnt_entfernt")
	
	return
#--------------------------	
