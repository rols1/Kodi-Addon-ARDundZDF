# -*- coding: utf-8 -*-
################################################################################
#				zdfmobile.py -  - Teil von Kodi-Addon-ARDundZDF
#						mobile Version der ZDF Mediathek
################################################################################
# 	dieses Modul nutzt nicht die Webseiten der Mediathek ab https://www.zdf.de/,
#	sondern die Seiten ab https://zdf-cdn.live.cellular.de/mediathekV2 - diese
#	Seiten werden im json-Format ausgeliefert

import  json		
import os, sys
import urllib, urllib2
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke

import xbmc, xbmcgui, xbmcaddon, xbmcplugin

# import ardundzdf					# -> ZDF_get_content - nicht genutzt
import resources.lib.util as util	# (util_imports.py)
PLog=util.PLog; home=util.home; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
getDirZipped=util.getDirZipped; Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
UtfToStr=util.UtfToStr; addDir=util.addDir; get_page=util.get_page; img_urlScheme=util.img_urlScheme; 
R=util.R; RLoad=util.RLoad; RSave=util.RSave; GetAttribute=util.GetAttribute; repl_dop=util.repl_dop; 
repl_char=util.repl_char; repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract; blockextract=util.blockextract; 
teilstring=util.teilstring; cleanhtml=util.cleanhtml; decode_url=util.decode_url; 
unescape=util.unescape; transl_doubleUTF8=util.transl_doubleUTF8; make_filenames=util.make_filenames; 
transl_umlaute=util.transl_umlaute; transl_json=util.transl_json; humanbytes=util.humanbytes; 
CalculateDuration=util.CalculateDuration; time_translate=util.time_translate; seconds_translate=util.seconds_translate; 
get_keyboard_input=util.get_keyboard_input; transl_wtag=util.transl_wtag; xml2srt=util.xml2srt; 
ReadFavourites=util.ReadFavourites; get_summary_pre=util.get_summary_pre; get_playlist_img=util.get_playlist_img; 
get_startsender=util.get_startsender; PlayVideo=util.PlayVideo; PlayAudio=util.PlayAudio; 



# Globals
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
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt

ICON 					= 'icon.png'		# ARD + ZDF
ICON_MAIN_ZDFMOBILE		= 'zdf-mobile.png'			
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_SPEAKER 			= "icon-speaker.png"
imgWidth		= 840			# max. Breite Teaserbild
imgWidthLive	= 1280			# breiter für Videoobjekt
NAME			= 'ARD und ZDF'
ZDFNAME			= "ZDFmobile"

def Main_ZDFmobile():
	PLog('zdfmobile_Main_ZDF:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD und ZDF')		# Home-Button
	
	# Suche bleibt abgeschaltet - bisher keine Suchfunktion bei zdf-cdn.live.cellular.de gefunden.
	# Web-Player: folgendes DirectoryObject ist Deko für das nicht sichtbare InputDirectoryObject dahinter:
	#fparams="&fparams={'name': '%s'}" % name
	#addDir(li=li, label='Suche: im Suchfeld eingeben', action="dirList", dirID="Main_ZDFmobile", 
	#	fanart=R(ICON_SEARCH), thumb=R(ICON_SEARCH), fparams=fparams)
		
	title = 'Startseite'
	fparams="&fparams={'ID': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.Hub", fanart=R(ICON_MAIN_ZDFMOBILE), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'ID': 'Kategorien'}"
	addDir(li=li, label="Kategorien", action="dirList", dirID="resources.lib.zdfmobile.Hub", fanart=R(ICON_MAIN_ZDFMOBILE), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'ID': 'Sendungen A-Z'}"
	addDir(li=li, label="Sendungen A-Z", action="dirList", dirID="resources.lib.zdfmobile.Hub", fanart=R(ICON_MAIN_ZDFMOBILE), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'ID': 'Sendung verpasst'}"
	addDir(li=li, label="Sendung verpasst", action="dirList", dirID="resources.lib.zdfmobile.Hub", fanart=R(ICON_MAIN_ZDFMOBILE), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'ID': 'Live TV'}"
	addDir(li=li, label='Live TV', action="dirList", dirID="resources.lib.zdfmobile.Hub", fanart=R(ICON_MAIN_ZDFMOBILE), 
	thumb=R(ICON_DIR_FOLDER), fparams=fparams, summary='nur in Deutschland zu empfangen!')

	xbmcplugin.endOfDirectory(HANDLE)
		
# ----------------------------------------------------------------------			
# ID = Dict-Parameter und title2 für ObjectContainer 
def Hub(ID):
	PLog('Hub, ID: %s' % ID)
	li = xbmcgui.ListItem()
	li = home(li, ID=ZDFNAME)				# Home-Button
	
	if ID=='Startseite':
		# lokale Testdatei:
		# path = '/daten/entwicklung/Plex/Codestuecke/ZDF_JSON/ZDF_start-page.json'
		# page = Resource.Load(path)
		path = 'https://zdf-cdn.live.cellular.de/mediathekV2/start-page'
	
	if ID=='Kategorien':
		path = 'https://zdf-cdn.live.cellular.de/mediathekV2/categories'
		
	if ID=='Sendungen A-Z':
		path = 'https://zdf-cdn.live.cellular.de/mediathekV2/brands-alphabetical'
		
	if ID=='Sendung verpasst':
		li = Verpasst(DictID='Verpasst')	
		return li		# raus - jsonObject wird in Verpasst_load geladen	

	if ID=='Live TV':
		now 	= datetime.datetime.now()
		datum 	= now.strftime("%Y-%m-%d")	
		path = 'https://zdf-cdn.live.cellular.de/mediathekV2/live-tv/%s' % datum	

	page = loadPage(path)

	if len(page) == 0 or str(page).startswith('Fehler'):
		xbmcgui.Dialog().ok(ADDON_NAME, 'Fehler beim Abruf von:', path, '')
		xbmcplugin.endOfDirectory(HANDLE)
		
	jsonObject = json.loads(page)	
	
	if ID=='Startseite':
		v = 'Startpage' 		# speichern
		vars()[v] = jsonObject
		Dict('store', v, vars()[v])
		li = PageMenu(li,jsonObject,DictID='Startpage')		
	if ID=='Kategorien':
		v = 'Kategorien'
		vars()['Kategorien'] = jsonObject
		Dict("store", v, vars()[v])
		li = PageMenu(li,jsonObject,DictID='Kategorien')		
	if ID=='Sendungen A-Z':
		v = 'A_Z'
		vars()['A_Z'] = jsonObject
		Dict("store", v, vars()[v])
		li = PageMenu(li,jsonObject,DictID='A_Z')		
	if ID=='Live TV':
		v = 'Live'
		vars()['Live'] = jsonObject
		Dict("store", v, vars()[v])
		li = PageMenu(li,jsonObject,DictID='Live')	

	return li

# ----------------------------------------------------------------------
def Verpasst(DictID):					# Wochenliste
	PLog('Verpasst')
	
	li = xbmcgui.ListItem()
	# li = home(li, ID=ZDFNAME)				# Home-Button - s. Hub
		
	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%Y-%m-%d")		# ZDF-Format 	
		display_date = rdate.strftime("%d-%m-%Y") 	# Formate s. man strftime(3)
		iWeekday =  rdate.strftime("%A")
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)		# -> ARD Mediathek
		path = 'https://zdf-cdn.live.cellular.de/mediathekV2/broadcast-missed/%s' % iDate
		title =	"%s | %s" % (display_date, iWeekday)
		PLog(title); PLog(path);
		fparams="&fparams={'path': '%s', 'datum': '%s'}" % (path, display_date)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.Verpasst_load", fanart=R(ICON_MAIN_ZDFMOBILE), 
			thumb=R(ICON_DIR_FOLDER), fparams=fparams)
	xbmcplugin.endOfDirectory(HANDLE)
# ----------------------------------------------------------------------
# lädt json-Datei für gewählten Wochtentag:
def Verpasst_load(path, datum):		# 5 Tages-Abschnitte in 1 Datei, path -> DictID 
	PLog('Verpasst_load:' + path)
	li = xbmcgui.ListItem()
	
	page = loadPage(path)		
	if page.startswith('Fehler') or page == '':
		xbmcgui.Dialog().ok(ADDON_NAME, 'Fehler beim Abruf von:', path, '')
		xbmcplugin.endOfDirectory(HANDLE)
	PLog(len(page))
	
	jsonObject = json.loads(page)
	path = path.split('/')[-1]			# Pfadende -> Dict-ID
	v = path
	vars()[path] = jsonObject
	Dict("store", v, vars()[v])
	li = PageMenu(li,jsonObject,DictID=path)
	xbmcplugin.endOfDirectory(HANDLE)
				
# ----------------------------------------------------------------------
# Bisher nicht genutzt
def ZDFmSearch(query, title='Suche', offset=0):
	PLog('ZDFmSearch')
	PLog('query: %s' % query)
	li = xbmcgui.ListItem()
	xbmcplugin.endOfDirectory(HANDLE)
# ----------------------------------------------------------------------	
# Übergabe jsonObject hier direkt, DictID: Zuordnung zum gespeicherten 
#	 jsonObject (Laden durch SingleRubrik + ShowVideo).		
def PageMenu(li,jsonObject,DictID):										# Start- + Folgeseiten
	PLog('PageMenu:, DictID: ' + DictID)
		
	mediatype=''													# Kennz. Videos im Listing
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	PLog('mediatype: ' + mediatype); 
		
	if("stage" in jsonObject):
		PLog('PageMenu stage')
		i=0
		for stageObject in jsonObject["stage"]:
			if(stageObject["type"]=="video"):							# Videos am Seitenkopf
				typ,title,subTitle,descr,img,date,dauer = Get_content(stageObject,imgWidth) 

				if subTitle:
					title = '%s | %s' % (title,subTitle)

				date = '%s |  Laenge: %s' % (date, dauer)
				path = 'stage|%d' % i
				PLog(path)
				fparams="&fparams={'path': '%s', 'DictID': '%s'}" % (path, DictID)	
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.ShowVideo", fanart=img, thumb=img, 
					fparams=fparams, summary=descr, tagline=date, mediatype=mediatype)
						
			i=i+1							
	if("cluster" in jsonObject):		# Bsp- A-Z Leitseite -> SingleRubrik
		PLog('PageMenu cluster')
		for counter, clusterObject in enumerate(jsonObject["cluster"]):	# Bsp. "name":"Neu in der Mediathek"
			if "teaser" in clusterObject and "name" in clusterObject:
				path = "cluster|%d|teaser" % counter
				title = clusterObject["name"]
				if title == '':
					title = 'ohne Titel'
				title = title.encode("utf-8")
				path = path.encode("utf-8")
				PLog('Mark1')
				title = repl_json_chars(title)
				fparams="&fparams={'path': '%s', 'title': '%s', 'DictID': '%s'}"  % (path, title, DictID)
				PLog(title); PLog(path);  PLog(fparams); 
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.SingleRubrik", 				
					fanart=R(ICON_MAIN_ZDFMOBILE), thumb=R(ICON_DIR_FOLDER), fparams=fparams)
								
	if("broadcastCluster" in jsonObject):								# 
		PLog('PageMenu broadcastCluster')
		for counter, clusterObject in enumerate(jsonObject["broadcastCluster"]):
			if clusterObject["type"].startswith("teaser") and "name" in clusterObject:
				path = "broadcastCluster|%d|teaser" % counter
				title = clusterObject["name"]
				title = title.encode("utf-8")
				path = path.encode("utf-8")
				fparams="&fparams={'path': '%s', 'title': '%s', 'DictID': '%s'}" % (path, title, DictID)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.SingleRubrik", 
				fanart=R(ICON_MAIN_ZDFMOBILE), thumb=R(ICON_DIR_FOLDER), fparams=fparams)
								
	if("epgCluster" in jsonObject):
		PLog('PageMenu epgCluster')
		for counter, epgObject in enumerate(jsonObject["epgCluster"]):	# Livestreams
			if("liveStream" in epgObject and len(epgObject["liveStream"]) >= 0):
				path = "epgCluster|%d|liveStream" % counter
				title = epgObject["name"] + ' Live'
				title = title.encode("utf-8")
				path = path.encode("utf-8")
				fparams="&fparams={'path': '%s', 'DictID': '%s'}" % (urllib2.quote(path), DictID)	
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.ShowVideo", 
					fanart=R(ICON_MAIN_ZDFMOBILE), thumb=R(ICON_DIR_FOLDER), fparams=fparams, 
					tagline=title, mediatype=mediatype)
					
	xbmcplugin.endOfDirectory(HANDLE)				
				
# ----------------------------------------------------------------------	
def Get_content(stageObject, maxWidth):
	PLog('Get_content:')
	# PLog(str(stageObject))
	
	title=stageObject["headline"]
	subTitle=stageObject["titel"]
	
	if(len(title)==0):
		title = subTitle
		subTitle = ""
		
	teaser_nr=''			# wie Serien in ZDF_get_content
	if ("episodeNumber" in stageObject):	
		teaser_nr = "Episode %s | " % stageObject["episodeNumber"]
	descr=''	
	if("beschreibung" in stageObject):
		descr = teaser_nr + stageObject["beschreibung"]
			
	typ=''	
	if("type" in stageObject):
		typ = stageObject["type"]

	dauer=''
	if("length" in stageObject):
		sec = stageObject["length"]
		if sec:
			dauer = time.strftime('%H:%M:%S', time.gmtime(sec))	
		
	img="";
	if("teaserBild" in stageObject):
		for width,imageObject in list(stageObject["teaserBild"].items()):
			if int(width) <= maxWidth:
				img=imageObject["url"];
	date=''	
	if("visibleFrom" in stageObject):
		date = stageObject["visibleFrom"]
	else:
		if("visibleFrom" in stageObject):
			date = stageObject["date"]
			#now = datetime.datetime.now()
			#date = now.strftime("%d.%m.%Y %H:%M")
		
	typ=UtfToStr(typ); title=UtfToStr(title); subTitle=UtfToStr(subTitle); descr=UtfToStr(descr); 
	title=repl_json_chars(title) 		# json-komp. für func_pars in router()
	subTitle=repl_json_chars(subTitle) 	# dto
	descr=repl_json_chars(descr) 		# dto
	
	img=UtfToStr(img);	date=UtfToStr(date); dauer=UtfToStr(dauer);
	PLog('Get_content: %s | %s |%s | %s | %s | %s | %s' % (typ, title,subTitle,descr,img,date,dauer) )		
	return typ,title,subTitle,descr,img,date,dauer
# ----------------------------------------------------------------------	
			
# einzelne Rubrik mit Videobeiträgen, alles andere wird ausgefiltert	
def SingleRubrik(path, title, DictID):	
	PLog('SingleRubrik: %s' % path); PLog(DictID)
	path_org = path
	
	jsonObject = Dict("load", DictID)
	jsonObject = GetJsonByPath(path, jsonObject)
	if jsonObject == '':					# index error
		xbmcplugin.endOfDirectory(HANDLE)
		
	PLog('jsonObjects: ' + str(len(jsonObject)))	
	# Debug:
	# RSave("/tmp/x_SingleRubrik.json", json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))

	li = xbmcgui.ListItem()
	li = home(li, ID=ZDFNAME)				# Home-Button
	
	i=0
	for entry in jsonObject:
		path = path_org + '|%d' % i
		date=''; title=''; descr=''; img=''
		# PLog(entry)	# bei Bedarf
		PLog("entry_type: " + entry["type"])
		mediatype=''
		if entry["type"] == 'video':		# Kennz. Video nur bei Sofortstart in ShowVideo
			if SETTINGS.getSetting('pref_video_direct') == 'true':
				mediatype='video'
				
		# Alle genannten types laufen über ShowVideo - nur video wird dort endverarbeitet.
		# 	Die types video, brand, category, topic kehren mit dem neuen jsonObject wieder
		#	zum PageMenu zurück und werden neu verteilt (SingleRubrik od. ShowVideo).
		# Alle anderen möglichen entry-types (?) werden übersprungen. 				
		if entry["type"] == "video" or entry["type"] == "brand"  or entry["type"] == "category" or entry["type"] == "topic":
			typ,title,subTitle,descr,img,date,dauer = Get_content(entry,imgWidth)
			if subTitle: 
				# title = '%s | %s' % (title,subTitle)
				title = '%s | %s' % (subTitle, title ) 	# subTitle = Sendungstitel
			tagline=''
			if date:
				tagline = '%s' % (date)
				if tagline and dauer:
					tagline = '%s |  %s' % (tagline, dauer)
			title = repl_json_chars(title)
			# PLog('video-content: %s |  %s |  %s |  %s | ' % (title,subTitle,descr,img))
			
			fparams="&fparams={'path': '%s', 'DictID': '%s'}" % (path, DictID)
			PLog("fparams: " + fparams)	
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.ShowVideo", fanart=img, 
				thumb=img, fparams=fparams, summary=descr, tagline=tagline, mediatype=mediatype)
								
				
		i=i+1
		# break		# Test Einzelsatz
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# iteriert durch das Objekt	und liefert Restobjekt ab path
# bei leerem Pfad wird jsonObject unverändert zurückgegeben
def GetJsonByPath(path, jsonObject):		
	PLog('GetJsonByPath: '+ path)
	if path == '':
		return jsonObject
	path = path.split('|')
	i = 0
	while(i < len(path)):
		if(isinstance(jsonObject,list)):
			index = int(path.pop(0))
		else:
			index = path.pop(0)
		PLog('i=%s, index=%s' % (i,index))
		try:							# index error möglich
			jsonObject = jsonObject[index]
		except Exception as exception:
			PLog(repr(exception))
			return ''			# Aufrufer muss beenden
	#PLog(jsonObject)
	return jsonObject	
# ----------------------------------------------------------------------
# 07.10.2019 Stringauswertung get_formitaeten2 für neue 
#	formitaeten-Variante hinzugefügt	
#		
def ShowVideo(path, DictID, Merk='false'):
	PLog('ShowVideo:'); PLog(path); PLog(DictID)
	PLog(Merk)
	
	jsonObject = Dict("load", DictID)
	videoObject = GetJsonByPath(path,jsonObject)
	# Debug:
	# RSave("/tmp/x_ShowVideo.json", json.dumps(videoObject, sort_keys=True, indent=2, separators=(',', ': ')))
	
		
	li = xbmcgui.ListItem()
	li = home(li, ID=ZDFNAME)							# Home-Button
														# Mehrfachbeiträge nachladen:
	if videoObject["type"] == 'brand' or videoObject["type"] == "category"  or videoObject["type"] == "topic":
		PLog('Mehrfachbeiträge')
		streamApiUrl, jsonurl, htmlurl = get_video_urls(videoObject)
		PLog("streamApiUrl: %s, jsonurl: %s, htmlurl: %s" % (streamApiUrl, jsonurl, htmlurl))
		
		page = loadPage(jsonurl)
		if len(page) == 0 or str(page).startswith('Fehler'):
			xbmcgui.Dialog().ok(ADDON_NAME, 'Fehler beim Abruf von:', url, '')
			xbmcplugin.endOfDirectory(HANDLE)
		jsonObject = json.loads(page)							# neues json-Objekt 
		
		# Debug:
		# RSave("/tmp/x_ShowVideo_multi.json", json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))
		Dict("store", 'ShowVideo_multi', jsonObject)
		li = PageMenu(li,jsonObject,DictID='ShowVideo_multi')	# Rubrik o.ä. (key "cluster")	
		return li
	
	PLog('Einzelbeitrag')								# Einzelbeitrag
	typ,title,subTitle,descr,img,date,dauer = Get_content(videoObject,imgWidthLive)
	typ=UtfToStr(typ); title=UtfToStr(title); subTitle=UtfToStr(subTitle); descr=UtfToStr(descr);
	if subTitle:
		title = '%s | %s' % (title,subTitle)
	title_org = UtfToStr(title)	
	PLog(title_org)	

	streamApiUrl, jsonurl, htmlurl = get_video_urls(videoObject)		# json- und html-Quellen bestimmen
	PLog(streamApiUrl); PLog(jsonurl); PLog(htmlurl)

	formitaeten=''; streamApiUrl=''; bandbreite=''
	if("formitaeten" in videoObject):
		PLog('formitaeten in videoObject')				# OK - videoObject hat bereits Videoquellen
		formitaeten = get_formitaeten(videoObject)		# json-Ausw. Formitäten
		PLog(len(formitaeten))					
	else:
		PLog('formitaeten fehlen, lade jsonurl')		# 1. Videoquellen in json-Seite suchen
		try:										
			page = loadPage(jsonurl)					# jsonurl aus get_video_urls
			videoObject = json.loads(page)
			page = json.dumps(videoObject, sort_keys=True, indent=2, separators=(',', ': '))
			# Debug:
			# RSave("/tmp/x_ShowVideo2.json", page)
			# streamApiUrl = videoObject["streamApiUrlAndroid"]					# json-key-error möglich	
			streamApiUrl = stringextract('streamApiUrlAndroid": "', '"', page)		
			PLog(streamApiUrl)	
			formitaeten = get_formitaeten(videoObject) # Json-Ausw. Formitäten
		except Exception as exception:
			PLog(repr(exception))
			PLog('Abruf formitaeten jsonurl fehlgeschlagen')			
		
		# Fallback:
		if "formitaeten" not in videoObject:			# 2. Videoquellen via Web/apiToken suchen
			streamApiUrl, jsonurl, htmlurl = get_video_urls(videoObject) # neu holen	
			PLog('formitaeten fehlen, lade htmlurl')
			PLog('htmlurl: ' + htmlurl)					# Webseite mit apiToken
			page = loadPage(htmlurl)				
		
			apiToken = stringextract('apiToken": "', '"', page) # apiToken: Webseite
			PLog("apiToken: " + apiToken)
			PLog('url2: ' + streamApiUrl)
			page = loadPage(streamApiUrl, apiToken=apiToken)	
			# Debug:
			# RSave("/tmp/x_cco.json", page)		# Debug	

			# neue Auswertung (Webseite kann von jsonObject abweichen) - 
			#	Bsp. countdown-copenhagen-102 / countdown-copenhagen-118.html							
			if '"attributes"' in page and '"formitaeten"' in page:
				PLog('lade formitaeten attr')				# Videoquellen
				formitaeten = get_formitaeten2(page) 		# String-Ausw. Formitäten

	descr_local=''										# Beschreibung zusammensetzen
	if date and dauer:
		descr_local = "%s | %s\n\n%s" % (date, dauer, descr) # Anzeige Listing 
		descr 		= "%s | %s||||%s" % (date, dauer, descr) # -> PlayVideo
	descr=repl_json_chars(descr) 				# json-komp. für func_pars in router()

	i=0
	for detail in formitaeten:	
		PLog("Mark4")
		i = i + 1
		quality = detail[0]				# Bsp. auto [m3u8]
		hd = 'HD: ' + str(detail[1])	# False bei mp4-Dateien, s.u.
		hd = hd.replace('true', 'ja'); hd = hd.replace('false', 'nein');
		url = detail[2]
		url = url.replace('https', 'http')
		typ = detail[3]
		codec = detail[4]
		geo = detail[5]
		PLog(geo)
		geoblock =  "mit Geoblock"
		if geo == 'none':
			geoblock = "ohne Geoblock"
		else:
			geoblock =  "mit Geoblock %s" % geo
		if url.endswith('mp4'):
			try:
				bandbreite = url.split('_')[-2]		# Bsp. ../4/170703_despot1_inf_1496k_p13v13.mp4
				hd = bandbreite
			except:
				bandbreite = ''
				
		title_org=UtfToStr(title_org);
		title_org=unescape(title_org); 	
		title_org=repl_json_chars(title_org) 		# json-komp. für func_pars in router()
		
		quality=UtfToStr(quality); typ=UtfToStr(typ); codec=UtfToStr(codec);
					
		PLog("url: " + url)	
		if Merk == 'true':
			PLog('Sofortstart Merk: ZDF Mobile (ShowVideo)')
			PlayVideo(url=url, title=title_org, thumb=img, Plot=descr, Merk=Merk)
			return
	
		if url.find('master.m3u8') > 0:		# 
			if 'auto' in quality:			# speichern für ShowSingleBandwidth
				if SETTINGS.getSetting('pref_video_direct') == 'true':	     # Sofortstart
					PLog('Sofortstart: ZDF Mobile (ShowVideo)')
					PlayVideo(url=url, title=title_org, thumb=img, Plot=descr, Merk=Merk)
					return
				url_auto = url
			title=str(i) + '. ' + quality + ' [m3u8]' + ' | ' + geoblock	# Einzelauflösungen
			PLog("title: " + title)
			tagline = '%s\n\n' % title_org + 'Qualitaet: %s | Typ: %s' % (quality, '[m3u8-Streaming]')
			tagline = UtfToStr(tagline);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
				(urllib2.quote(url), urllib2.quote(title_org), urllib.quote_plus(img), urllib.quote_plus(descr), Merk)	
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
				thumb=img, fparams=fparams, tagline=descr_local, summary =tagline, mediatype='video')	
		else:
			title=str(i) + '. %s [%s] | %s'  % (quality, hd, geoblock)
			PLog("title: " + title)
			tagline = '%s\n\n' % title_org + 'Qualitaet: %s | Typ: %s | Codec: %s' % (quality, typ, codec)
			if bandbreite:
				bandbreite=UtfToStr(bandbreite);
				tagline = '%s | %s'	% (tagline, bandbreite)		
			tagline = UtfToStr(tagline);
			fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
				(urllib2.quote(url), urllib2.quote(title_org), urllib.quote_plus(img), urllib.quote_plus(descr), Merk)	
			addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
				thumb=img, fparams=fparams, tagline=descr_local, summary =tagline, mediatype='video')	
	
	'''
	# einzelne Auflösungen anbieten:	# bei zdfMobile überflüssig - Varianten von low - veryhigh vorh.
	title = 'einzelne Bandbreiten/Aufloesungen zu auto [m3u8]'
	fparams="&fparams={'title': '%s', 'url_m3u8': '%s', 'thumb': '%s', 'descr': '%s'}" % (urllib2.quote(title_org), 
		urllib2.quote(url_auto), urllib2.quote(img), urllib.quote_plus(descr))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.zdfmobile.ShowSingleBandwidth", fanart=img, 
		thumb=img, fparams=fparams, summary=descr, mediatype='')
	'''
	xbmcplugin.endOfDirectory(HANDLE)
				
# ----------------------------------------------------------------------
# ermittelt aus url + sharingUrl die json- und html-Quelle, Bsp.:
# 	"streamApiUrlAndroid": "https://api.zdf.de/tmd/2/android_native_1/vod/ptmd/mediathek/171013_tag_acht_cco"
#	"url": "https://zdf-cdn.live.cellular.de/mediathekV2/document/callin-mr-brain-130"
#	"sharingUrl": "https://www.zdf.de/wissen/callin-mr-brain/callin-mr-brain-130.html"
#	Stringsuche bei htmlurl unischer
#
def get_video_urls(videoObject):
	PLog("get_video_urls:")
	v = json.dumps(videoObject, sort_keys=True, indent=2, separators=(',', ': '))
	
	try:
		streamApiUrl = re.search('api.zdf.de/tmd/2/android_native_1(\S+)cco"', v).group(1)
	except:
		streamApiUrl=''
	if streamApiUrl:
		streamApiUrl = 'https://api.zdf.de/tmd/2/android_native_1' + streamApiUrl + 'cco'

	try:
		jsonurl = re.search('https://zdf-cdn.live.cellular.de(\S+)"', v).group(1)
	except:
		jsonurl=''
	if jsonurl:
		jsonurl = 'https://zdf-cdn.live.cellular.de' + jsonurl 

	try:
		htmlurl = re.search('https:(\S+).html"', v).group(1)
	except:
		htmlurl=''
	if htmlurl:
		htmlurl = 'https:' + htmlurl + '.html'
	
	return streamApiUrl, jsonurl, htmlurl
# ----------------------------------------------------------------------
# 2 Varianten: 
#	single=True: 	1 Block formitaeten enthält die Videodetails
#	single=False: 	mehrere Blöcke enthalten die Videodetails
def get_formitaeten(jsonObject):
	PLog('get_formitaeten:')
	forms=[]
	# Debug
	# RSave("/tmp/x_forms.json", json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))

	try:
		formObject = jsonObject["document"]["formitaeten"]
		single = True
	except Exception as exception:
		PLog(repr(exception))
		single = False
	PLog(single)
	
	geoblock=''; fsk=''
	if single:	
		if 	"geoLocation" in formObject:
			geoblock = formObject["geoLocation"]								
		if 	"fsk" in formObject:				# z.Z n. verw.
			fsk = formObject["fsk"]								
		for formitaet in formObject:
			detail=[]
			url = formitaet["url"];
			quality = formitaet["quality"]
			hd = formitaet["hd"]
			typ = formitaet["type"]
			codec = formitaet["mimeType"]
			PLog("quality:%s hd:%s url:%s" % (quality,hd,url))
			detail.append(quality); detail.append(hd); 
			detail.append(url); detail.append(typ); detail.append(codec);
			detail.append(geoblock); 
			forms.append(detail)
		return forms	
	
	# single=False
	if 	"geoLocation" in jsonObject:
		geoblock = jsonObject["geoLocation"]								
	if 	"fsk" in jsonObject:				# z.Z n. verw.
		geoblock = jsonObject["fsk"]								
	for formitaet in jsonObject["formitaeten"]:	
		detail=[]
		url = formitaet["url"];
		quality = formitaet["quality"]
		hd = formitaet["hd"]
		typ = formitaet["type"]
		codec = ''
		if "mimeCodec" in formitaet:
			codec = formitaet["mimeCodec"]
		if "mimeType" in formitaet:
			codec = formitaet["mimeType"]
		PLog("quality:%s hd:%s url:%s" % (quality,hd,url))
		detail.append(quality); detail.append(hd); 
		detail.append(url); detail.append(typ); detail.append(codec); 
		detail.append(geoblock); 
		forms.append(detail)
	# PLog('forms: ' + str(forms))
	return forms		

# ----------------------------------------------------------------------
# json-Index-Probleme - daher stringextract
def get_formitaeten2(page):
	PLog('get_formitaeten2:')
	forms=[]
	records = blockextract('"formitaeten"', page)
	PLog(len(records))
	
	geoblock = stringextract('"geoLocation"', '},', page)
	geoblock = stringextract('"value" : "', '"', geoblock)
	fsk 	 = stringextract('"fsk"', '},', page)	# z.Z n. verw.
	fsk	 	 = stringextract('"value" : "', '"', fsk)
	
	for rec in records:
		detail=[]
		url 	= stringextract('"uri" : "', '"', rec)
		quality = stringextract('"quality" : "', '"', rec)
		hd 		= stringextract('"hd" : ', ',', rec)		# true / false
		typ 	= stringextract('"type" : "', '"', rec)
		codec	= stringextract('"mimeCodec" : "', '"', rec)
		PLog("quality: %s, hd: %s, typ: %s, codec: %s, url: %s" % (quality,hd,typ,codec,url))
		detail.append(quality); detail.append(hd); 
		detail.append(url); detail.append(typ);  detail.append(codec);
		detail.append(geoblock); 		 
		forms.append(detail)
	# PLog('forms: ' + str(forms))
	return forms		
# ----------------------------------------------------------------------:
def ShowSingleBandwidth(title,url_m3u8,thumb, descr):	# .m3u8 -> einzelne Auflösungen
	PLog('ShowSingleBandwidth:')
	
	playlist = loadPage(url_m3u8)
	if playlist.startswith('Fehler'):
		xbmcgui.Dialog().ok(ADDON_NAME, playlist, url_m3u8, '')
		
	li = xbmcgui.ListItem()
	li =  Parseplaylist(li, playlist=playlist, title=title, thumb=thumb, descr=descr)		
	
	xbmcplugin.endOfDirectory(HANDLE)

####################################################################################################
#									Hilfsfunktionen
####################################################################################################
def Parseplaylist(li, playlist, title, thumb, descr):	# playlist (m3u8, ZDF-Format) -> einzelne Auflösungen
	PLog ('Parseplaylist:')
	PLog(title)
	title = UtfToStr(title)
	title_org = title
  
	lines = playlist.splitlines()
	# PLog(lines)
	lines.pop(0)		# 1. Zeile entfernen (#EXTM3U)
	
	line_inf=[]; line_url=[]
	for i in range(0, len(lines),2):
		line_inf.append(lines[i])
		line_url.append(lines[i+1])
	# PLog(line_inf); PLog(line_url); 	
	
	i=0; Bandwith_old = ''
	for inf in line_inf:
		PLog(inf)
		url = line_url[i]
		i=i+1		
		Bandwith=''; Resolution=''; Codecs=''; 
		Bandwith = re.search('BANDWIDTH=(\d+)', inf).group(1)
		if 'RESOLUTION=' in inf:		# fehlt ev.
			Resolution = re.search('RESOLUTION=(\S+),CODECS', inf).group(1)
		Codecs = re.search(r'"(.*)"', inf).group(1)	# Zeichen zw. Hochkommata
		
		summ= 'Bandbreite: %s' % Bandwith 
		if Resolution:
			summ= 'Bandbreite %s | Auflösung: %s' % (Bandwith, Resolution)
		if Codecs:
			summ= '%s | Codecs: %s' % (descr, Codecs)
		summ = summ.replace('"', '')	# Bereinigung Codecs
			
		PLog(Bandwith); PLog(Resolution); PLog(Codecs); 
		tagline='m3u8-Streaming'
		title = '%s. %s' 	% (str(i), title_org)
		if 	Bandwith_old == Bandwith:
			title = '%s. %s | 2. Alternative' 	% (str(i), title_org)
		Bandwith_old = Bandwith
		if int(Bandwith) <=  100000: 		# Audio - PMS-Transcoder: Stream map '0:V:0' matches no streams 
			tagline = '%s | nur Audio'	% tagline
			thumb=R(ICON_SPEAKER)
		
		descr = UtfToStr(descr)		
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (urllib.quote_plus(url), 
			urllib.quote_plus(title_org), urllib.quote_plus(thumb), urllib.quote_plus(descr))			
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, 
			thumb=thumb, fparams=fparams, summary=summ, tagline=tagline, mediatype='video')	

	return li
		
#----------------------------------------------------------------  			
def loadPage(url, apiToken='', maxTimeout = None):
	try:
		safe_url = url.replace( " ", "%20" ).replace("&amp;","&")
		PLog("loadPage: " + safe_url); 

		req = urllib2.Request(safe_url)
		# gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)		# 07.10.2019: Abruf mit SSLContext klemmt häufig - bei
		# 	Bedarf mit Prüfung auf >'_create_unverified_context' in dir(ssl)< nachrüsten:

		req.add_header('User-Agent', 'Mozilla/5.0 (Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36')
		req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
		req.add_header('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
		# hier nicht verwenden: 'Accept-Charset', 'utf-8' | 'Accept-Encoding', 'gzip, deflate, br'
		if apiToken:
			PLog(apiToken)
			req.add_header("Api-Auth", "Bearer %s" % apiToken) 
			req.add_header("Origin", "https://www.zdf.de") 
			req.add_header("Sec-Fetch-Mode", "cors") 

		if maxTimeout == None:
			maxTimeout = 60;
		# r = urllib2.urlopen(req, timeout=maxTimeout, context=gcontext) # s.o.
		r = urllib2.urlopen(req, timeout=maxTimeout)
		# PLog("headers: " + str(r.headers))
		doc = r.read()
		PLog(len(doc))	
		if '<!DOCTYPE html>' not in doc:	# Webseite mit apiToken nicht encoden (code-error möglich)
			doc = doc.encode('utf-8')		
		return doc
		
	except Exception as exception:
		msg = 'Fehler: ' + str(exception)
		msg = msg + '\r\n' + safe_url			 			 	 
		msg =  msg
		PLog(msg)
		return msg

#---------------------------------------------------------------- 



