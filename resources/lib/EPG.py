# -*- coding: utf-8 -*-
# EPG, Daten von tvtoday.de 
#	URL-Schema: http://www.tvtoday.de/programm/standard/sender/%s.html  %s=ID, z.B. ard oder ARD
#	Datumsbereich: 12 Tage, Bsp. MO - FR
#	Zeitbereich	5 Uhr - 5 Uhr Folgetag
#		Einteilung (tvtoday.de): 5-11, 11-14, 14-18, 18-20, 20-00, 00-05 Uhr  (hier nicht verwendet)
#	Struktur:
#		Container: tv-show-container js-tv-show-container
#		Blöcke: <a href=" .. </a>
#		Sendezeit: data-start-time="", data-end-time=""
#
#	20.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#		
 
import time
import datetime
from datetime import date

import resources.lib.util as util
R=util.R; RLoad=util.RLoad; RSave=util.RSave;Dict=util.Dict; PLog=util.PLog; 
addDir=util.addDir; get_page=util.get_page;
stringextract=util.stringextract; blockextract=util.blockextract; 
transl_wtag=util.transl_wtag; cleanhtml=util.cleanhtml; home=util.home

EPG_BASE =  "http://www.tvtoday.de"

# PREFIX = '/video/ardmediathek2016'			
# @route(PREFIX + '/EPG')		# EPG-Daten holen
# 	mode: 		falls 'OnlyNow' dann JETZT-Sendungen
# 	day_offset:	1,2,3 ... Offset in Tagen (Verwendung zum Blättern in EPG_ShowSingle)
def EPG(ID, mode=None, day_offset=None):
	PLog('EPG ID: ' + ID)
	PLog(mode)
	url="http://www.tvtoday.de/programm/standard/sender/%s.html" % ID
	PLog(url)

	page, msg = get_page(path=url)				# Absicherung gegen Connect-Probleme
	# PLog(page[:500])	# bei Bedarf
	if msg:
		return ''	# Verarbeitung in SenderLiveListe (rec = EPG.EPG..)
	PLog(len(page))

	pos = page.find('tv-show-container js-tv-show-container')	# ab hier relevanter Inhalt
	page = page[pos:]
	PLog(len(page))

	liste = blockextract('href=\"', page)  
	PLog(len(liste));	

	# today.de verwendet Unix-Format, Bsp. 1488830442
	now,today,today_5Uhr,nextday,nextday_5Uhr = get_unixtime(day_offset)# lokale Unix-Zeitstempel holen + Offsets
	now_human = datetime.datetime.fromtimestamp(int(now))				# Debug: Übereinstimmung mit UTC, Timezone?	
	now_human =  now_human.strftime("%d.%m.%Y, %H:%M:%S")				# deutsches Format
	today_human = datetime.datetime.fromtimestamp(int(today_5Uhr))
	today_human =  today_human.strftime("%d.%m.%Y, %H:%M Uhr")			# deutsches Format mit Offset (Datumanzeige ab ...)
	
	PLog('EPGSatz:')
	PLog(now); PLog(now_human); PLog(today_human);
	# PLog(today); PLog(today_5Uhr); PLog(nextday); PLog(nextday_5Uhr)	# bei Bedarf

	# Ausgabe: akt. Tag ab 05 Uhr(Start) bis nächster Tag 05 Uhr (Ende)
	#	
	# PLog("neuer Satz:")
	EPG_rec = []
	for i in range (len(liste)):		# ältere + jüngere Sendungen in Liste - daher Schleife + Zeitabgleich	
		# PLog(liste[i])					# bei Bedarf
		rec = []
		starttime = stringextract('data-start-time=\"', '\"', liste[i]) # Sendezeit, Bsp. "1488827700" (UTC)
		if starttime == '':									# Ende (Impressum)
			break
		endtime = stringextract('data-end-time=\"', '\"', liste[i])	 	# Format wie starttime
		href = stringextract('href=\"', '\"', liste[i])					# wenig zusätzl. Infos
		img = stringextract('srcset="', '"', liste[i])
		img = img.replace('159.', '640.')								# Format ändern "..4415_159.webp"
		
		sname = stringextract('class=\"h7 name\">', '</p>', liste[i])
		stime = stringextract('class=\"h7 time\">', '</p>', liste[i])   # Format: 06:00
		stime = stime.strip()
		summ = get_summ(liste[i])								# Beschreibung holen
		
		sname = stime + ' | ' + sname							# Titel: Bsp. 06:40 | Nachrichten

		s_start = 	datetime.datetime.fromtimestamp(int(starttime))	# Zeit-Konvertierung UTC-Startzeit
		s_startday =  s_start.strftime("%A") 					# Locale’s abbreviated weekday name
		
		von = stime
		bis = datetime.datetime.fromtimestamp(int(endtime))
		bis = bis.strftime("%H:%M") 
		vonbis = von + '-' + bis
		
		# Auslese - nur akt. Tag 05 Uhr (einschl. Offset in Tagen ) + Folgetag 05 Uhr:
		if starttime < today_5Uhr:				# ältere verwerfen
			# PLog(starttime); PLog(nextday_5Uhr)
			continue
		if starttime > nextday_5Uhr:			# jüngere verwerfen
			# PLog(starttime); PLog(nextday_5Uhr)
			continue
						
		if now >= starttime and now < endtime:
			# PLog(now); PLog(starttime); PLog(endtime)	# bei Bedarf
			sname = "JETZT: " + sname
			# PLog(sname); PLog(img)				# bei Bedarf
			if mode == 'OnlyNow':				# aus EPG_ShowAll - nur aktuelle Sendung
				rec = [starttime,href,img,sname,stime,summ,vonbis]  # Index wie EPG_rec
				# PLog(rec)
				PLog('EPG_EndOnlyNow')
				return rec						# Rest verwerfen - Ende		
		
		iWeekday = transl_wtag(s_startday)
		sname = iWeekday[0:2] + ' | ' + sname	# Wochentag voranstellen

		# Indices EPG_rec: 0=starttime, 1=href, 2=img, 3=sname, 4=stime, 5=summ, 6=vonbis, 7=today_human:  
		# Link href zum einzelnen Satz hier nicht verwendet - wenig zusätzl. Infos
		rec.append(starttime);rec.append(href); rec.append(img); rec.append(sname);	# Listen-Element
		rec.append(stime); rec.append(summ); rec.append(vonbis); rec.append(today_human);
		EPG_rec.append(rec)											# Liste Gesamt (2-Dim-Liste)
	
	EPG_rec.sort()						# Sortierung	
	PLog(len(EPG_rec)); PLog('EPG_End')
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

####################################################################################################
#									Hilfsfunktionen
####################################################################################################
# get_unixtime() ermittelt 'jetzt', 'nächster Tag' und 'nächster Tag, 5 Uhr 'im Unix-Format
#	tvtoday.de verwendet Unix-Format: data-start-time, data-end-time (beide ohne Sekunden)
# 	day_offset:	1,2,3 ... Offset in Tagen
#	Rückgabe today: today + Offset
def get_unixtime(day_offset=None):		
	dt = datetime.datetime.now()								# Format 2017-03-09 22:04:19.044463
	now = time.mktime(dt.timetuple())							# Unix-Format 1489094334.0
	dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)  # auf 0 Uhr setzen: 2017-03-09 00:00:00
	today = time.mktime(dt.timetuple())							# Unix-Format 1489014000.0
	# today = time.mktime(d.timetuple()) 						# Ergebnis wie oben
		
	if day_offset:
		today = today + (int(day_offset) * 86400)				# Zuschlag in ganzen Tagen (1 Tag = 86400 sec)
	nextday = today + 86400										# nächster Tag 			(+ 86400 sec = 24 x 3600)
	today_5Uhr = today + 18000									# today+Offset, 05 Uhr  (+ 18000 sec = 5 x 3600)
	nextday_5Uhr = nextday + 18000								# nächster Tag, 05 Uhr 
	
	now = str(now).split('.')[0]								# .0 kappen (tvtoday.de ohne .0)
	today = str(today).split('.')[0]
	nextday = str(nextday).split('.')[0]
	nextday_5Uhr = str(nextday_5Uhr).split('.')[0]
	today_5Uhr = str(today_5Uhr).split('.')[0]
	
	# Bei Bedarf Konvertierung 'Human-like':
	# nextday_str = datetime.datetime.fromtimestamp(int(nextday))
	# nextday_str = nextday.strftime("%Y%m%d")	# nächster Tag, Format 20170331
		
	return now,today,today_5Uhr,nextday,nextday_5Uhr
#----------------------------------------------------------------  

		
