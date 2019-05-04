# -*- coding: utf-8 -*-
# Podcontent.py	- Aufruf durch __init__.py/PodFavoritenListe 
#
# Die Funktionen dienen der Auswertung von Radio-Podcasts der Regionalsender. Zusätzlich
#	stehen die angezeigten Dateien für Downloads zur Verfügung (einzeln und gesamte Liste)
# Basis ist die Liste podcast-favorits.txt (Default/Muster im Ressourcenverzeichnis), die
# 	Liste enthält weitere  Infos zum Format und zu bereits unterstützten Podcast-Seiten
# 	- siehe nachfolgende Liste Podcast_Scheme_List
#
# Die Kurzform 'Podcast-Suche' deckt auch www.ardmediathek.de/radio ab - diese Funktion
#	macht die Radio-Podcasts aus dem Hauptmenü für Downloads verfügbar. Ein Beispiel
#	ist in der podcast-favorits.txt enthalten (s. Podcast-Suche: Quarks - Wissenschaft und mehr).

import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import sys, os, subprocess, urllib2, datetime, time
import json, re

import resources.lib.util as util
PLog=util.PLog;  home=util.home;  Dict=util.Dict;  name=util.name; 
UtfToStr=util.UtfToStr;  addDir=util.addDir;  get_page=util.get_page; 
img_urlScheme=util.img_urlScheme;  R=util.R;  RLoad=util.RLoad;  RSave=util.RSave; 
GetAttribute=util.GetAttribute; CalculateDuration=util.CalculateDuration;  
teilstring=util.teilstring; repl_char=util.repl_char;  mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract;  blockextract=util.blockextract; 
teilstring=util.teilstring;  repl_dop=util.repl_dop; cleanhtml=util.cleanhtml;  decode_url=util.decode_url;  
unescape=util.unescape;  mystrip=util.mystrip; make_filenames=util.make_filenames;  transl_umlaute=util.transl_umlaute;  
humanbytes=util.humanbytes;  time_translate=util.time_translate; get_keyboard_input=util.get_keyboard_input; 


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA

ICON_MAIN_POD			= 'radio-podcasts.png'
ICON_MEHR 				= "icon-mehr.png"
ICON_DOWNL 				= "icon-downl.png"
ICON_NOTE 				= "icon-note.png"
ICON_STAR 				= "icon-star.png"

BASE_URL				= 'https://classic.ardmediathek.de'
POD_SEARCH 				= '/suche?source=radio&sort=date&searchText=%s&pod=on&playtime=all&words=and&to=all='
####################################################################################################
Podcast_Scheme_List = [		# Liste vorhandener Auswertungs-Schemata
# fehlendes http / https wird in Auswertungsschemata ersetzt
	'http://www.br-online.de', 'https://www.br.de',  
	'http://www.deutschlandfunk.de', 'http://mediathek.rbb-online.de',
	'//www.ardmediathek.de', 'http://www1.wdr.de/mediathek/podcast',
	'www1.wdr.de/mediathek/audio', 'http://www.ndr.de',
	'www.swr3.de', 'Podcast-Suche:']	

#------------------------	
def PodFavoriten(title, path, offset=0):
	PLog('PodFavoriten:'); PLog(path); PLog(offset)
			
	rec_per_page = 24							# Anzahl pro Seite (www.br.de 24, ndr 10)
	title_org = title
	
	Scheme = ''
	for s in Podcast_Scheme_List:				# Prüfung: Schema für path vorhanden?
		PLog(s); PLog(path[:80])
		if path.find(s) >= 0 or s == 'Podcast-Suche:':
			Scheme = s
			PLog(Scheme)
			break			
	if Scheme == '':			
		msg1='Auswertungs-Schema fehlt für Url'
		PLog(msg1)
		msg2=path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		
	# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
	#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild	, 9. Tagline
	#			10. PageControl
	POD_rec = get_pod_content(url=path, rec_per_page=rec_per_page, baseurl=Scheme, offset=offset)
	if POD_rec == None:
		msg1 = 'Auswertung fehlgeschlagen:'
		msg2 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		
	PLog(len(POD_rec))
	if len(POD_rec) == 0:					# z.B. Fehlschlag bei Podcast-Suche 
		msg1='Leider kein Treffer.'	
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
	if 'Seite nicht' in POD_rec:			# error_txt aus get_page, einschl. path
		msg1=POD_rec	
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
	
	rec_cnt = len(POD_rec)							# Anzahl gelesener Sätze
	start_cnt = int(offset) + 1						# Startzahl diese Seite
	end_cnt = int(start_cnt) + int(rec_per_page)-1	# Endzahl diese Seite

	PLog(POD_rec[0][0])								# Gesamtzahl (0 bei Seitenkontrolle, außer br-online)
	if POD_rec[0][0] == 0:
		title2 = title
	else:
		title2 = "%s (gesamt: %s Podcasts)"	% (title, POD_rec[0][0])
		
	li = xbmcgui.ListItem()
	li = home(li, ID='PODCAST')			# Home-Button
	
	if rec_cnt == 0:			
		msg1='Keine Podcast-Daten gefunden.'
		msg2=path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
				
	url_list = []									# url-Liste für Sammel-Downloads (Dict['url_list'])	
	DLMultiple = True
	PLog("mark1")
	for rec in POD_rec:
		max_len=rec[0]
		url=rec[1]; summ=rec[3]; tagline=rec[9]; title=rec[7];
		if url == '':								# skip Satz ohne url - kann vorkommen
			continue
		if  url.endswith('.mp3') == False:			# Sammel-Downloads abschalten, falls Mehrfachseiten folgen
			DLMultiple = False
			
		title = UtfToStr(title)
		title = title.replace('"', '*')		# "-Zeichen verhindert json.loads in router
		title = unescape(title)
		url_list.append(url)
		img = R(ICON_NOTE)	
		
		if POD_rec[0][5]:	# Kodi: Dauer anhängen (summary + tagline nicht verfügbar)
			d = POD_rec[0][5]
			d =  UtfToStr(d)	
			title = "%s | %s"   % (title, d)
		title = UtfToStr(title); summ = UtfToStr(summ); tagline = UtfToStr(tagline)
		PLog('neuer_Satz')
		PLog(title); PLog(summ[:40]); PLog(url); PLog(DLMultiple); PLog(rec[10]); # bei Bedarf
		if rec[8]:
			img = rec[8]
		if rec[10]:										# Schemata mit Seitenkontrolle?
			if rec[10] == 'htmlpages':					# Bsp. RBB u.a. - versch. Formate:
				pagepos = url.find('page')				# 	..page-1.html, ..page1.html, ..mcontent=page.1
				page = url[pagepos:]
				pagenr = (page.replace('-', '').replace('.', '').replace('html', '').replace('page', ''))
				
			if 'jsonpages' in rec[10]:					# Bsp. jsonpages|53|3.0|24|1 (total,pages,items,current)
				current = rec[10].split('|')[-1]
				pagenr = current			
			PLog('pagenr: %s' % pagenr) 
			fparams="&fparams={'title': '%s', 'path': '%s', 'offset': '%s'}" % \
				(urllib2.quote(title), urllib2.quote(url), pagenr)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFavoriten", 
			fanart=R(ICON_STAR), thumb=R(ICON_STAR), fparams=fparams, summary=path, tagline=summ)
		else:
			# nicht direkt zum TrackObject, sondern zu SingleSendung, um Downloadfunktion zu nutzen
			# oc.add(CreateTrackObject(url=url, title=title, summary=summ, fmt='mp3', thumb=img))
			# Für SingleSendung summary + tagline hier nicht benötigt - falls doch: ev. Hochkommata
			#	für json.loads func_pars entfernen.
			fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'duration': '%s', 'summary': '%s', 'tagline': '%s', 'ID': '%s'}" % \
				(urllib2.quote(url), urllib2.quote(title),  img, 'duration', 'summary',  'tagline', 'PODCAST')
				
			addDir(li=li, label=title, action="dirList", dirID="SingleSendung", fanart=img, 
				thumb=img, fparams=fparams, summary=summ)
		
	# Mehr Seiten anzeigen:					
	if rec[10] == '' and rec[11] == '':		# nur bei Podcasts ohne Seitenkontrolle (rec[11]='skip_more')	
		PLog(rec_cnt);PLog(offset);PLog(max_len)
		if (rec_cnt + int(offset)) < int(max_len): 
			new_offset = rec_cnt + int(offset)
			PLog(new_offset); PLog(path)
			summ = 'Mehr (insgesamt ' + str(max_len) + ' Podcasts)'
			fparams="&fparams={'title': '%s', 'path': '%s', 'offset': '%s'}" % \
				(urllib2.quote(title), urllib2.quote(path), new_offset)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.PodFavoriten", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), fparams=fparams, summary=summ, tagline='Favoriten')
			
	if DLMultiple == True and len(url_list) > 1:			# True z.B. bei "Weiter zu Seite 1"
		# Sammel-Downloads - alle angezeigten Favoriten-Podcasts downloaden?
		#	für "normale" Podcasts erfolgt die Abfrage in SinglePage
		title='Download! Alle angezeigten Podcasts ohne Rückfrage speichern?'
		summ = 'Download von insgesamt %s Podcasts' % len(POD_rec)	
		Dict("store", 'url_list', url_list) 
		Dict("store", 'POD_rec', POD_rec) 	
		fparams="&fparams={'key_url_list': 'url_list', 'key_POD_rec': 'POD_rec'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.Podcontent.DownloadMultiple", 
			fanart=R(ICON_DOWNL), thumb=R(ICON_DOWNL), fparams=fparams, summary=summ)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#------------------------	
# Sammeldownload lädt alle angezeigten Podcasts herunter.
# Im Gegensatz zum Einzeldownload wird keine Textdatei zum Podcast angelegt.
# DownloadExtern kann nicht von hier aus verwendet werden, da der wiederholte Einzelaufruf 
# 	von Curl kurz hintereinander auf Linux Prozessleichen hinterlässt: curl (defunct)
# Zum Problem command-line splitting (curl-Aufruf) und shlex-Nutzung siehe:
# 	http://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex
# Das Problem >curl "[Errno 36] File name too long"< betrifft die max. Pfadlänge auf verschiedenen
#	Plattformen (Posix-Standard 4096). Teilweise ist die Pfadlänge manuell konfigurierbar.
#	Die hier gewählte platform-abhängige Variante funktioniert unter Linux + Windows (Argumenten-Länge
#	bis ca. 4 KByte getestet) 
# Rücksprung-Problem: der Button DownloadsTools ruft zwar die Funktion DownloadsTools auf, führt aber vorher
#	noch einmal den Curl-Aufruf aus mit kompl. Download - keine Abhilfe mit no_cache=True im ObjectContainer
#	oder Parameter time=time.time() für dem Callback DownloadsTools.
#
#	01.09.2018: s.a. Doku in LiveRecord. Die Lösungen / Anpassungen für PHT  wurden hier analog umgesetzt. 
#		PHT: bei Plugin-Timeout zeigt PHT zuerst den Callback-Button und sprint anschließend wieder zum 
#			Funktionskopf.
#		
def DownloadMultiple(key_url_list, key_POD_rec):						# Sammeldownloads
	PLog('DownloadMultiple:'); 
	import shlex											# Parameter-Expansion
	
	url_list =  Dict("load", "url_list")
	# POD_rec = Dict[key_POD_rec]
	POD_rec =  Dict("load", key_POD_rec)
	# PLog('PIDcurlPOD: %s' % POD_rec)
	# PLog('url_list: %s' % url_list)

	li = xbmcgui.ListItem()
	li = home(li, ID='PODCAST')								# Home-Button
	
	rec_len = len(POD_rec)
	AppPath = SETTINGS.getSetting('pref_curl_path')
	AppPath = UtfToStr(AppPath) 
	AppPath = os.path.abspath(AppPath)
	dest_path = SETTINGS.getSetting('pref_curl_download_path')
	dest_path = UtfToStr(dest_path)
	curl_param_list = '-k '									# schaltet curl's certificate-verification ab

	PLog(AppPath)
	if os.path.exists(AppPath)	== False:					# Existenz Curl prüfen
		msg1='curl nicht gefunden'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')		
	if os.path.isdir(dest_path)	== False:			
		msg1='Downloadverzeichnis nicht gefunden:'	# Downloadverzeichnis prüfen
		msg2=path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')		
	
	i = 0
	for rec in POD_rec:										# Parameter-Liste für Curl erzeugen
		i = i + 1
		#if  i > 2:											# reduz. Testlauf
		#	break
		url = rec[1]; title = rec[7]
		title = UtfToStr(title); url = UtfToStr(url)
		title = unescape(title)								# schon in PodFavoriten, hier erneut nötig 
		if 	SETTINGS.getSetting('pref_generate_filenames'):	# Dateiname aus Titel generieren
			dfname = make_filenames(title) + '.mp3'
		else:												# Bsp.: Download_2016-12-18_09-15-00.mp4  oder ...mp3
			now = datetime.datetime.now()
			mydate = now.strftime("%Y-%m-%d_%H-%M-%S")	
			dfname = 'Download_' + mydate + '.mp3'

		# Parameter-Format: -o Zieldatei_kompletter_Pfad Podcast-Url -o Zieldatei_kompletter_Pfad Podcast-Url ..
		curl_fullpath = os.path.join(dest_path, dfname)		 
		curl_fullpath = os.path.abspath(curl_fullpath)		# os-spezischer Pfad
		PLog("Mark3")
		curl_param_list = curl_param_list + ' -o '  + curl_fullpath + ' ' + url
		
	cmd = AppPath + ' ' + curl_param_list
	PLog(len(cmd))
	
	PLog(sys.platform)
	if sys.platform == 'win32':								# s. Funktionskopf
		args = cmd
	else:
		args = shlex.split(cmd)								# ValueError: No closing quotation (1 x, Ursache n.b.)
	PLog(len(args))											# hier Ende Log-Ausgabe bei Plugin-Timeout, Download
															#	läuft aber weiter.
	try:
		PIDcurlPOD = ''
		sp = subprocess.Popen(args, shell=False)			# shell=True entf. hier nach shlex-Nutzung	
		output,error = sp.communicate()						#  output,error = None falls Aufruf OK
		PLog('call = ' + str(sp))	
		if str(sp).find('object at') > 0:  				# Bsp.: <subprocess.Popen object at 0x7fb78361a210>
			PIDcurlPOD = sp.pid							# PID zum Abgleich gegen Wiederholung sichern
			PLog('PIDcurlPOD neu: %s' % PIDcurlPOD)
			msg1 = 'curl: Download erfolgreich gestartet'
			msg2 = 'Anzahl der Podcast: %s' % rec_len
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li				
		else:
			raise Exception('Start von curl fehlgeschlagen')			
	except Exception as exception:
		PLog(str(exception))		
		msg1='Download fehlgeschlagen'
		msg2 = str(exception)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li				
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

#------------------------	
def get_pod_content(url, rec_per_page, baseurl, offset):
	PLog('get_pod_content:'); PLog(url); PLog(rec_per_page); PLog(baseurl); PLog(offset);

	if int(offset) == 0:
		if 'Podcast-Suche:' in baseurl:				# Kurzform Podcast-Suche -> Link erzeugen
			query = url.split(':')[1]				# Bsp. Podcast-Suche: Quarks-Wissenschaft-und-mehr
			query = query.strip()
			query = query.replace(' ', '+')			# Leer-Trennung = UND-Verknüpfung bei Podcast-Suche 
			query = urllib2.quote(query, "utf-8")
			PLog('query: %s' %  query)
			path =  BASE_URL  + POD_SEARCH % query
			url = path
			PLog(url)
			baseurl = BASE_URL						# 'http://www.ardmediathek.de'
		
	url = UtfToStr(url)
	url = unescape(url)							# einige url enthalten html-escapezeichen
	if baseurl == 'https://www.br.de':			# Umlenkung auf API-Seite beim
		if int(offset) == 0:					# 	ersten Aufruf - Erzeugung Seiten-Urls in Scheme_br_online
			ID = url.split('/')[-1]				# ID am Pfadende
			url = baseurl + '/mediathek/podcast/api/podcasts/%s/episodes?items_per_page=24&page=1'	% ID
	
	page, err = get_page(path=url)				# Absicherung gegen Connect-Probleme
	if page == '':
		PLog(err)
		return err
	PLog(len(page))

	# baseurl aus Podcast_Scheme_List (PodFavoriten)
	if baseurl == 'https://www.br.de':
		return Scheme_br_online(page, rec_per_page, offset, page_href=url)
	if 'www.swr3.de' in baseurl:
		return Scheme_swr3(page, rec_per_page, offset)
	if baseurl == 'http://www.deutschlandfunk.de':
		return Scheme_deutschlandfunk(page, rec_per_page, offset)
	if baseurl == 'http://mediathek.rbb-online.de':
		sender = ''								# mp3-url mittels documentId zusammensetzen
		if url.find('documentId=24906530') > 0:
			sender = 'Fritz'					# mp3-url auf Ziel-url ermitteln
		return Scheme_rbb(page, rec_per_page, offset, sender, baseurl)
		
	if baseurl == 'http://www1.wdr.de/mediathek/podcast' or baseurl == 'www1.wdr.de/mediathek/audio':
		return Scheme_wdr(page, rec_per_page, offset)
	if baseurl == 'http://www.ndr.de':
		return Scheme_ndr(page, rec_per_page, offset)
	
	# vor Mediathek-Neu www.ardmediathek.de	
	if '//classic.ardmediathek.de' in baseurl or 'Podcast-Suche:' in baseurl:
		if 'Podcast-Suche:' in baseurl:
			baseurl = BASE_URL
		return Scheme_ARD(page, rec_per_page, offset, baseurl)
	
#------------------------
def Scheme_br_online(page, rec_per_page, offset, page_href=None):	# Schema www.br-online.de, ab Mai 2018 json-format
# 	Aufruf von get_pod_content - Umsetzung auf API-Call dort
	PLog('Scheme_br_online:'); PLog(offset); PLog(len(page)); 
	jsonObject = json.loads(page)
	max_len = jsonObject["result"]["meta"]["episodes"]["total"]
	PLog(max_len)
	tagline = ''; pagecontrol= '';img=''
	
	max_len 		= jsonObject["result"]["meta"]["episodes"]["total"]
	page_cnt		= jsonObject["result"]["meta"]["episodes"]["pages"]
	items_per_page 	= jsonObject["result"]["meta"]["episodes"]["items_per_page"]
	current			= jsonObject["result"]["meta"]["episodes"]["current_page"]
	# Bsp. jsonpages|53|3.0|24|1 (total,pages,items,current):
	pagecontrol = 'jsonpages|%s|%s|%s|%s' % (max_len,page_cnt,items_per_page,current)	
	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	
	if int(offset) == 0:							# 1. Durchlauf - Seitenkontrolle 
		pages = int(page_cnt)						# 3.0 -> 3
		PLog(pages)	
		pagenr = 1									# Start
		for i in range(1, pages+1):
			single_rec = []							# Datensatz einzeln (2. Dim.)
			PLog(page_href); 	
			# max_len = 0							# br_online: Gesamt in title2 in PodFavoriten zeigen
			url = page_href.split('&page=')			# Part mit Seitennr. entfernen
			url = url[0]
			url = url + "&page=%s"	% pagenr
									
			title = 'Weiter zu Seite %s' % pagenr
			dach = jsonObject["result"]["episodes"][0]["podcast"]["title"]	# Titel Sendereihe
			summ = dach; title_org = ''; datum = ''; dauer = ''; groesse = ''; 
			pagenr = pagenr + 1
			
			PLog(title); PLog(url); 			
			# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
			#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
			#			10. PageControl, 11. 'skip_more' oder leer
			single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
			single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
			single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
			single_rec.append(tagline); single_rec.append(pagecontrol);single_rec.append('');
			POD_rec.append(single_rec)
		return POD_rec	
	
	pagecontrol = ''				# überspringt Seitenkontrolle in PodFavoriten
	for i, episodes in enumerate(jsonObject["result"]["episodes"]):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:			# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:			# Anzahl pro Seite überschritten?
			break

		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = episodes["title"]
		summ = episodes["podcast"]["summary"]
		url = episodes["enclosure"]["url"]
		img =  episodes["image"]
		
		poddatum = episodes["publication_date"]		#Bsp.  "2018-05-09T14:35:00Z"
		PLog(poddatum)
		# datum = datetime.datetime.strptime(poddatum, "%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y, %H:%M Uhr")
		# in Plex OK, in Kodi 'module' object is not callable. 
		#	s. https://bugs.python.org/issue27400 (klappt hier auch nicht)
		#	Fix: time_translate
		datum = time_translate(poddatum)		
		dauer = episodes["duration"]
		groesse = episodes["enclosure"]["length"]
		
		title = '%s | %s' % (datum, title_org)
		if groesse:
			groesse = humanbytes(groesse)
			title = '%s | %s' % (title, groesse)
		
		PLog(title); PLog(summ[:80]); PLog(url); PLog(pagecontrol); 		
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('skip_more');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec
	
# ------------------------
def Scheme_swr3(page, rec_per_page, offset):	# Schema SWR
	PLog('Scheme_swr3')
	sendungen = blockextract('class="audio-list-item', page)
	max_len = len(sendungen)					# Gesamtzahl gefundener Sätze
	PLog(max_len)
	tagline = ''; pagecontrol= '';
	
	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	for i in range(len(sendungen)):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:			# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:			# Anzahl pro Seite überschritten?
			break
		s = sendungen[cnt]
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('content="', '"', s)
		title = title_org 
		url = stringextract('<source src="', '"', s) 
		img =  stringextract('contentUrl" href="', '"', s) 				# contentUrl" href="https://static..
		PLog("contentUrl: " + img)
		img_alt =  stringextract('alt="', '"', s) 						# Bildbeschr. - nicht verwendet
		
		datum = stringextract('datePublished">', '</time>', s) 			# im Titel ev. bereits vorhanden
		dauer = stringextract('<time datetime=', '/time>', s) 			# "P0Y0M0DT0H0M34.000S">0:34</div>
		dauer = stringextract('>', '<', dauer) 
		groesse = stringextract('data-ati-size="', '"', s)
		groesse = float(int(groesse)) / 1000000						# Konvert. nach MB, auf 2 Stellen gerundet
		groesse = '%.2f MB' % groesse
		
		title = ' %s | %s' % (title, datum)
		summ = ' Dauer %s | Größe %s' % (dauer, groesse)
		
		PLog(title); PLog(summ); PLog(img); PLog(url); 
		
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('skip_more');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec
		
# ------------------------
def Scheme_deutschlandfunk(page, rec_per_page, offset):		# Schema www.deutschlandfunk.de, XML-Format
	PLog('Scheme_deutschlandfunk')
	sendungen = blockextract('<item>', page)
	max_len = len(sendungen)								# Gesamtzahl gefundener Sätze
	PLog(max_len)
	tagline = ''; pagecontrol= '';
	
	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	for i in range(len(sendungen)):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:			# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:			# Anzahl pro Seite überschritten?
			break
		s = sendungen[cnt]
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('<title>', '</title>', s) 
		title = title_org.strip()
		summ = stringextract('vspace="4"/>', '<br', s) 			# direkt nach Bildbeschreibung
		summ = summ.strip()
		url = stringextract('<enclosure url="', '"', s) 
		img =  stringextract('<img src="', '\"', s) 
		img_alt =  stringextract('alt="', '\"', s) 						# 
		
		author = stringextract('itunes:author>', '</itunes:author>', s) 
		datum = stringextract('<pubDate>', '</pubDate>', s)
		datum = datum.replace('+0200', '')	
		dauer = stringextract('duration>', '</itunes', s) 
		groesse = stringextract('length="', '"', s) 
		groesse = float(int(groesse)) / 1000000						# Konvert. nach MB, auf 2 Stellen gerundet
		groesse = '%.2f MB' % groesse
		
		title = ' %s | %s' % (title, datum)
		summ = ' Autor %s | Datum %s | Größe %s' % (author, datum, groesse)
		
		PLog(title); PLog(summ); PLog(url); 		
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('skip_more');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec
		
# ------------------------
def Scheme_rbb(page, rec_per_page, offset,sender, baseurl):		# Schema mediathek.rbb-online.de
# 	Besonderheit: offset = Seitennummer
# 	1. Aufruf kommt mit ..&mcontent=page.1
	PLog('Scheme_rbb'); PLog(offset); PLog(sender)

	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	pages = blockextract('entry" data-ctrl-contentLoader-source', page)		# Seiten-Urls
	max_len = len(pages)
	PLog(max_len)
	page_href = baseurl + stringextract('href="', '">', pages[0])
	page_href = page_href.split('mcontent=')[0]		# Basis-url ohne Seitennummer
	tagline = ''; pagecontrol= '';
	
	if offset == '0':								# 1. Durchlauf - Seitenkontrolle 
		pagenr = 1
		for p in pages:
			single_rec = []							# Datensatz einzeln (2. Dim.)
			max_len = 0								# -> POD_rec[0][0] 	-> title2 in PodFavoriten
			url = page_href + 'mcontent=page.' + str(pagenr)	 # url mit Seitennr, ergänzen
			title = 'Weiter zu Seite %s' % pagenr
			img = '';					
			pagecontrol= 'htmlpages';			# 'PageControl' steuert 
			summ = ''; title_org = ''; datum = ''; dauer = ''; groesse = ''; 
			pagenr = pagenr + 1
			
			PLog(title); PLog(url); 			
			# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
			#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
			#			10. PageControl, 11. 'skip_more' oder leer
			single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
			single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
			single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
			single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('');
			POD_rec.append(single_rec)
		return POD_rec
	
	sendungen = blockextract('class="teaser"', page)  # Struktur wie ARD-Mediathek
	del sendungen[0]; del sendungen[1]			# Sätze 1 + 2 keine Podcasts
	max_len = len(sendungen)					# Gesamtzahl gefundener Sätze dieser Seite
	PLog(max_len)
	
	for i in range(len(sendungen)):
		cnt = int(i) 		# + int(offset) Offset entfällt (pro Seite Ausgabe aller Sätze)
		# PLog(cnt); PLog(i)
		#if int(cnt) >= max_len:		# Gesamtzahl überschritten? - entf. hier
		s = sendungen[cnt]
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('dachzeile">', '</p>', s) 
		summ = stringextract('subtitle">', '<', s) 		# Bsp.: Do 13.04.17 00:00 | 03:28 min	
		headline = stringextract('headline">', '</h4>', s)  # häufig mehr Beschreibung als Headline
		
		url_local = stringextract('<a href="', '"', s) 		# Homepage der Sendung
		url_local = baseurl + url_local
		url_local = decode_url(url_local)					# f%C3%BCr -> für, 	&amp; -> &
		PLog(url_local)
		try:												# mp3-url auf Ziel-url ermitteln
			url_local = unescape(url_local)
			page, err = get_page(path=url_local)			# Absicherung gegen Connect-Probleme
			url = stringextract('<div data-ctrl-ta-source', 'target="_blank"', page)
			url = stringextract('a href="', '"', url)
			PLog(url)		
		except:	
			url=''											

		if url.endswith('.mp3') == False:					# mp3-url mittels documentId zusammensetzen
			documentId =  re.findall("documentId=(\d+)", url_local)[0]
			url = baseurl + '/play/media/%s?devicetype=pc&features=hls' % documentId
			PLog('hlsurl: ' + url)
			try:
				url_content, err = get_page(path=url)				# Textdatei, Format ähnlich parseLinks_Mp4_Rtmp
				url = stringextract('stream":"', '"}', url_content) # geändert 24.01-2018	
			except:
				url=''
		PLog(url)
			
		text = stringextract('urlScheme', '/noscript', s)
		img, img_alt = img_urlScheme(text, 320, ID='PODCAST') # img_alt nicht verwendet
		
		author = ''	  										# fehlt
		groesse = ''	  										# fehlt
		datum = summ.split('|')[0]
		dauer = summ.split('|')[1]
				
		title = ' %s | %s  | %s' % (title_org, datum, dauer)
		summ = headline
		summ = unescape(summ)
		
		PLog(title); PLog(summ); PLog(url); 
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline);  single_rec.append(pagecontrol); single_rec.append('skip_more');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec
		
# ------------------------
def Scheme_wdr(page, rec_per_page, offset):		# Schema WDR, XML-Format
	PLog('Scheme_wdr')
	sendungen = blockextract('<item>', page)
	max_len = len(sendungen)									# Gesamtzahl gefundener Sätze
	PLog(max_len)
	title_channel = stringextract('<title>', '</title>', page)	# Channel-Titel
	tagline = ''; pagecontrol= '';
	
	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	for i in range(len(sendungen)):
		cnt = int(i) + int(offset)
		# PLog(cnt); PLog(i)
		if int(cnt) >= max_len:			# Gesamtzahl überschritten?
			break
		if i >= rec_per_page:			# Anzahl pro Seite überschritten?
			break
		s = sendungen[cnt]
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('<title>', '</title>', s) 
		title = title_org.strip()
		summ = stringextract('<description>', '</description>', s) 			
		summ = summ.strip()
		summ = unescape(summ)
		url = stringextract('<enclosure url="', '"', s) 
		img =  stringextract('<img src="', '\"', s) 
		img_alt =  stringextract('alt="', '\"', s) 						# 
		
		author = stringextract('itunes:author>', '</itunes:author>', s) 
		datum = stringextract('<pubDate>', '</pubDate>', s)
		datum = datum.replace('GMT', '')	
		dauer = stringextract('duration>', '</itunes', s) 
		groesse = stringextract('length="', '"', s) 					# fehlt
		#groesse = float(int(groesse)) / 1000000						# Konvert. nach MB, auf 2 Stellen gerundet
		#groesse = '%.2f MB' % groesse
		
		title = ' %s | %s'			% (title, datum)
		summ = ' Autor %s | %s' 	% (author, summ)
		
		PLog(title); PLog(summ); PLog(url); 
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec
		
# ------------------------
def Scheme_ndr(page, rec_per_page, offset):		# Schema NDR - ab 05.2018 Verwendung der xml-Seiten
	PLog('Scheme_ndr'); PLog(offset);PLog(len(page))

	baseurl = 'http://www.ndr.de'
	POD_rec = []			# Datensaetze gesamt (1. Dim.)	
	tagline = ''; pagecontrol= '';	

	pages = stringextract('<div class="pagination">', 'googleoff:', page)	# Seiten-Urls für Seitenkontrolle
	if len(pages) > 0:							# Seite ohne Seitenkontrolle möglich
		page_href = baseurl + stringextract('href="', '-', pages)				# zum Ergänzen mit 1.html, 2.html usw.
		# PLog(page_href)	
		entry_type = '_page-'
		pages = pages.split(entry_type)				# .. href="/ndr2/programm/podcast2958_page-6.html" title="Zeige Seite 6">			
		# PLog(pages[1])
		page_nr = []
		for line in pages:	
			nr = re.search('(\d+)', line).group(1) # Bsp. 6.html
			page_nr.append(nr)	
		page_nr.sort()
		PLog(page_nr)
		page_nr = repl_dop(page_nr)					# Doppler entfernen (zurück-Seite, nächste-Seite)
		last_page = page_nr[-1]						# letzte Seite
		PLog(last_page)
		
		if offset == '0':							# 1. Durchlauf - Seitenkontrolle:
			pagenr = 0
			# PLog(last_page)
			for i in range(int(last_page)):
				title_org=''; 
				# max_len = last_page
				max_len = 0							# -> POD_rec[0][0] 	-> title2 in PodFavoriten
				single_rec = []						# Datensatz einzeln (2. Dim.)
				pagenr = i + 1
				if pagenr >= last_page:
					break
				url = page_href + '-' + str(pagenr) + '.html' 	# url mit Seitennr. ergänzen
				title = 'Weiter zu Seite %s' % pagenr
				img = '';						
				pagecontrol= 'htmlpages';					# 'PageControl' steuert in PodFavoriten
				summ = ''; title_org = ''; datum = ''; dauer = ''; groesse = ''; 
				
				PLog(title); PLog(url); PLog(pagenr); PLog(last_page)
				
				# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
				#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
				#			10. PageControl, 11. 'skip_more' oder leer
				single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
				single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
				single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
				single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('')
				POD_rec.append(single_rec)
			return POD_rec							# Rückkehr aus Seitenkontrolle
		
												# 2. Durchlauf - Inhalte der einzelnen Seiten:
	sendungen = blockextract('class="module list w100">', page) 
	if len(sendungen) > 1:
		if sendungen[2].find('urlScheme') >= 0:								# 2 = Episodendach
			text = stringextract('urlScheme', '/noscript', sendungen[2])
			img_src_header, img_alt_header = img_urlScheme(text, 320, ID='PODCAST') 
			teasertext = stringextract('class="teasertext">', '</p>', sendungen[2])
			PLog(img_src_header);PLog(img_alt_header);PLog(teasertext);
	
	
	max_len = len(sendungen)					# Gesamtzahl gefundener Sätze dieser Seite
	PLog(max_len)
	
	for i in range(len(sendungen)):
		# cnt = int(i) 		# + int(offset) Offset entfällt (pro Seite Ausgabe aller Sätze)
		# PLog(cnt); PLog(i)
		# if int(cnt) >= max_len:		# Gesamtzahl überschritten? - entf. hier
		# s = sendungen[cnt]
		s = sendungen[i]
		# PLog(s)
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('title="Zum Audiobeitrag: ', '"', s) 
		subtitle =  stringextract('subline">', '<', s)			# Bsp.: 06.04.2017 06:50 Uhr
		if subtitle == '':
			subtitle =  stringextract('subline date">', '<', s)	# Bsp.: date">18.05.2017 06:50 Uhr
		summ = stringextract('<p>', '<a title', s) 
		summ = summ.strip()			
		dachzeile = ''										# fehlt		
		headline = ''										# fehlt	
		
		pod = stringextract('podcastbuttons">', 'class="button"', s)
		pod = pod.strip()
		PLog(pod[40:])
		url = stringextract('href=\"', '\"', pod)		# kompl. Pfad
		if url == '':									# kein verwertbarer Satz 
			continue			
			
		img = ''											# fehlt	
		author = ''	  										# fehlt
		groesse = ''	  									# fehlt
		datum = subtitle
		dauer = stringextract('class="cta " >', '</a>', s) 
		
		title = '%s | %s' % (subtitle, title_org)
		tagline = '%s | %s' % (subtitle, dauer)
						
		PLog('neuer Satz:'); PLog(title); PLog(summ); PLog(tagline); PLog(url); 
		
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('skip_more')
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))	
	return POD_rec	
		
# ------------------------
def Scheme_ARD(page, rec_per_page, offset,baseurl):		# Schema ARD = www.ardmediathek.de
# 	Schema für die Podcastangebote der ARD-Mediathek
# 	1. Aufruf kommt mit ..&mcontents=page.1 (nicht ..content=..)
	PLog('Scheme_ARD'); PLog(offset);

	POD_rec = []			# Datensaetze gesamt (1. Dim.)
	
	# Bsp. ['"/suche?searchText=quarks+wissenschaft&amp;sort=date&amp;pod&amp;source=radio&amp;mresults']:
	pages =  re.findall(r'<a href=(.*?)=page.', page)
	max_len = len(pages)								# max_len=letzte Seitennr.							
	PLog(len(pages))
	if pages:	
		page_href = pages[0].replace('"', '')			# Pfad aus 1. Pagelink ermitteln
		page_href = page_href.replace('+', '%2B')		# ARD-Fehler in Links: %2B (Leerz.) wird durch + ersetzt
		PLog(page_href)

	if baseurl.startswith('http') == False:				# https ergänzen (http bei ard obsolet)
		baseurl = 'https:' + baseurl
		
	tagline = ''; pagecontrol= '';
	# für Seiten mit offset=0 aber ohne Seitenkontrolle direkt weiter bei sendungen
	if offset == '0' and pages:							# 1. Durchlauf - Seitenkontrolle
		pagenr = 1
		for p in pages:
			single_rec = []								# Datensatz einzeln (2. Dim.)
			max_len = 0									# -> POD_rec[0][0] 	-> title2 in PodFavoriten
			url = baseurl + page_href + "=page.%d" % pagenr	 # url mit Seitennr. ergänzen
			url = unescape(url)
			url = url.replace('+', '%2B')				# ARD-Fehler in Links: %2B (Leerz.) wird durch + ersetzt
			title = 'Weiter zu Seite %s' % pagenr
			img = '';						
			pagecontrol= 'htmlpages';				# 'PageControl' steuert 
			summ = ''; title_org = ''; datum = ''; dauer = ''; groesse = ''; 
			pagenr = pagenr + 1
			
			PLog(title); PLog('url: %s' % url); 
			# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
			#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
			#			10. PageControl, 11. 'skip_more' oder leer
			single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
			single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
			single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
			single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('');
			POD_rec.append(single_rec)
		return POD_rec							# Rückkehr aus Seitenkontrolle
		
												# 2. Durchlauf - bzw. ohne Seitenkontrolle direkt -
												# Inhalte der einzelnen Seiten:	
	sendungen = blockextract('class="teaser"', page)  # Struktur für Podcasts + Videos ähnlich
	img_src_header=''; img_alt_header=''; teasertext=''
	max_len = len(sendungen)					# Gesamtzahl gefundener Sätze dieser Seite
	#PLog('sendungen[0]: ' + sendungen[0])		# bei Bedarf
	if sendungen[0].find('urlScheme') >= 0:								# [0] = Episodendach
		text = stringextract('urlScheme', '/noscript', sendungen[0])
		img_src_header, img_alt_header = img_urlScheme(text, 320, ID='PODCAST') 
		teasertext = stringextract('class="teasertext">', '</p>', sendungen[0])
		max_len = str(max_len - 1)				# sonst klappt's nicht mit 'Mehr'-Anzeige
		PLog(img_src_header);PLog(img_alt_header);PLog(teasertext);
	
	PLog('max_len: ' + str(max_len))
	
	for i in range(len(sendungen)):
		s = sendungen[i]
		PLog(len(s));    # PLog(s)
		
		single_rec = []		# Datensatz einzeln (2. Dim.)
		title_org = stringextract('dachzeile">', '</p>', s) 
		subtitle =  stringextract('subtitle">', '<', s)		# Bsp.: 06.02.2017 | 1 Min.
		summ = stringextract('teasertext">', '<', s) 			
		dachzeile = stringextract('dachzeile">', '</p>', s)  # Sendereihe		
		headline = stringextract('headline">', '</h4>', s)  # Titel der einzelnen Sendung
		
		url_local = stringextract('<a href="', '"', s) 		# Homepage der Sendung
		if url_local == '' or url_local.find('documentId=') == -1:	# kein verwertbarer Satz 
			continue
		url_local = baseurl + url_local
		PLog('url_local: ' + url_local)
		documentId =  re.findall("documentId=(\d+)", url_local)[0]
		url = baseurl + '/play/media/%s?devicetype=pc&features=hls' % documentId 	# Quelldatei Podcast
		url_content, err = get_page(path=url)			# Textdatei, Format ähnlich parseLinks_Mp4_Rtmp
		PLog('url_content: ' + url_content[:60])
		if url_content == '':
			PLog('url_content leer')
			return err
		url = stringextract('stream":"', '"', url_content) # manchmal 2 identische url
		PLog('mp3-url: ' + url)	
			
		text = stringextract('urlScheme', '/noscript', s)
		img, img_alt = img_urlScheme(text, 320, ID='PODCAST') # img_alt nicht verwendet
		if img == '':										# Episodenbild 
			img =img_src_header 
		
		author = '';  groesse = ''  						# fehlen hier
		datum = '';  dauer = '';			
		if subtitle.find('|') > 0:
			datum = subtitle.split('|')[0]
			dauer = subtitle.split('|')[1]
		
		if dachzeile:
			title = ' %s | %s ' % (dachzeile, headline)
			summ =  ' %s | %s' % (datum, dauer)
		else:
			title = ' %s | %s | %s' % (headline, datum, dauer)
			if teasertext:
				summ = teasertext
		title = title.replace('|  |', '')						# Datum + Dauer können fehlen
				
		tagline = teasertext									# aus Episodendach, falls vorh.
		tagline = unescape(tagline)
		summ = unescape(summ)
		
		PLog(title); PLog(summ); PLog(url); 
		# Indices: 	0. Gesamtzahl, 1. Url, 2. Originaltitel, 3. Summary, 4. Datum,
		#			5. Dauer, 6. Größe, 7. Titel (zusammengesetzt), 8. Bild, 9. Tagline
		#			10. PageControl, 11. 'skip_more' oder leer
		single_rec.append(max_len); single_rec.append(url); single_rec.append(title_org); 
		single_rec.append(summ); single_rec.append(datum); single_rec.append(dauer); 
		single_rec.append(groesse); single_rec.append(title); single_rec.append(img);
		single_rec.append(tagline); single_rec.append(pagecontrol); single_rec.append('skip_more');
		POD_rec.append(single_rec)
		
	PLog(len(POD_rec))
	return POD_rec	
		
#----------------------------------------------------------------  
