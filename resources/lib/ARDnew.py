# -*- coding: utf-8 -*-
################################################################################
#				ARD_NEW.py -	Part of Kodi-Addon-ARDundZD
#			neue Version der ARD Mediathek, Start Beta Sept. 2018
################################################################################
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.ardmediathek.de/,
#	Seiten werden im json-Format, teilweise html + json ausgeliefert

import string, re
import  json		
import os, sys
import urllib, urllib2
import datetime, time

import xbmc, xbmcgui, xbmcaddon, xbmcplugin

import ardundzdf					# -> SenderLiveResolution, Parseplaylist

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
ICON_MAIN_ARD 			= 'ard-mediathek.png'			
ICON_ARD_AZ 			= 'ard-sendungen-az.png'
ICON_ARD_VERP 			= 'ard-sendung-verpasst.png'			
ICON_ARD_RUBRIKEN 		= 'ard-rubriken.png' 
			
ICON_SEARCH 			= 'ard-suche.png'						
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_SPEAKER 			= "icon-speaker.png"
ICON_MEHR 				= "icon-mehr.png"

BETA_BASE_URL	= 'https://www.ardmediathek.de'

ARDSender = ['ARD-Alle:ard::ard-mediathek.png:ARD-Alle', 'Das Erste:daserste:208:tv-das-erste.png:Das Erste', 
	'BR:br:2224:tv-br.png:BR Fernsehen', 'MDR:mdr:1386804:tv-mdr-sachsen.png:MDR Fernsehen', 
	'NDR:ndr:5898:tv-ndr-niedersachsen.png:NDR Fernsehen', 'Radio Bremen:radiobremen::tv-bremen.png:Radio Bremen TV', 
	'RBB:rbb:5874:tv-rbb-brandenburg.png:rbb Fernsehen', 'SR:sr:5870:tv-sr.png:SR Fernsehen', 
	'SWR:swr:5310:tv-swr.png:SWR Fernsehen', 'WDR:wdr:5902:tv-wdr.png:WDR Fernsehen',
	'ONE:one:673348:tv-one.png:ONE', 'ARD-alpha:alpha:5868:tv-alpha.png:ARD-alpha', 'KiKA::::KiKA']

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])
FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

ARDStartCacheTime = 300						# 5 Min.	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA

DEBUG			= SETTINGS.getSetting('pref_info_debug')
NAME			= 'ARD und ZDF'

#----------------------------------------------------------------
# sender neu belegt in Senderwahl
def Main_NEW(name, CurSender=''):
	PLog('Main_NEW:'); 
	PLog(name); PLog(CurSender)
			
	if ':' not in CurSender:			# '', False od. 'False'
		CurSender = ARDSender[0]
	
	CurSender = UtfToStr(CurSender)	
	Dict('store', "CurSender", CurSender)
	PLog('sender: ' + CurSender); 
	
	sendername, sender, kanal, img, az_sender = CurSender.split(':')	# sender -> Menüs
		
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	PLog("li:" + str(li))						
			
	title="Suche in ARD-Mediathek"
	fparams="&fparams={'title': '%s', 'sender': '%s' }" % (urllib2.quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", fanart=R(ICON_MAIN_ARD), 
		thumb=R(ICON_SEARCH), fparams=fparams)
		
	title = 'Start | Sender: %s' % sendername	
	fparams="&fparams={'title': '%s', 'sender': '%s'}" % (urllib2.quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", fanart=R(ICON_MAIN_ARD), thumb=R(img), 
		fparams=fparams)

	# title = 'Sendung verpasst | Sender: %s' % sendername
	title = 'Sendung verpasst | Sender: %s' % sendername
	fparams="&fparams={'title': 'Sendung verpasst', 'CurSender': '%s'}" % (urllib2.quote(CurSender))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasst", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_VERP), fparams=fparams)
	
	title = 'Sendungen A-Z | Sender: %s' % sendername
	fparams="&fparams={'name': 'Sendungen A-Z', 'ID': 'ARD'}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_AZ), fparams=fparams)
						
	title = 'ARD Sportschau'
	fparams="&fparams={'title': '%s'}"	% title
	addDir(li=li, label=title, action="dirList", dirID="ARDSport", 
		fanart=R("tv-ard-sportschau.png"), thumb=R("tv-ard-sportschau.png"), fparams=fparams)
						

	title 	= 'Wählen Sie Ihren Sender | aktuell: %s' % sendername				# Senderwahl
	fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", fanart=R(ICON_MAIN_ARD), 
		thumb=R('tv-regional.png'), fparams=fparams) 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		 		
#---------------------------------------------------------------- 

# Startseite der Mediathek - passend zum ausgewählten Sender -
#		Hier wird die HTML-Seite geladen. Sie enthält Highlights + die ersten beiden Rubriken. 
#		Der untere json-Abschnitt enthält die WidgetID's mit Links zu den restlichen Rubriken
#		(nur Titel, ohne Bild, ohne Beschreibung) - diese werden erst beim Scrolling geladen.
#		Verarbeitung der Links zu den restlichen Rubriken in ARDStartRubrik. 	
#	
#		Um horizontales Scrolling (Nachladen innerhalb einer Rubrik) zu vermeiden, fordern
#			wir via pageSize am path-Ende alle verfügbaren Beiträge an.
def ARDStart(title, sender, widgetID=''): 
	PLog('ARDStart:'); 
	
	CurSender = Dict("load", 'CurSender')		
	CurSender = UtfToStr(CurSender)
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	title2 = "Sender: %s" % sendername
	title2 = title2.decode(encoding="utf-8")		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	# RSave('/tmp/x.html', page) 							# Debug

	path = BETA_BASE_URL + "/%s/" % sender
	# Seite aus Cache laden
	page = Dict("load", 'ARDStartNEW_%s' % sendername, CacheTime=ARDStartCacheTime)					
	if page == False:											# nicht vorhanden oder zu alt
		page, msg = get_page(path=path)							# vom Sender holen
	
		if 'APOLLO_STATE__' not in page:						# Fallback: Cache ohne CacheTime
			page = Dict("load", 'ARDStartNEW_%s' % sendername)					
			msg1 = "Startseite nicht im Web verfuegbar."
			PLog(msg1)
			msg3=''
			if page:
				msg2 = "Seite wurde aus dem Addon-Cache geladen."
				msg3 = "Seite ist älter als %s Minuten (CacheTime)" % str(CacheTime/60)
			else:
				msg2='Startseite nicht im Cache verfuegbar.'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)	
		else:	
			Dict("store", 'ARDStartNEW_%s' % sendername, page) 	# Seite -> Cache: aktualisieren	
	PLog(len(page))
	
	# möglich: 	swiper-stage, swiper-container, swiper-wrapper, swiper-slide								
	if 'class="swiper-' in page:						# Highlights im Wischermodus
		swiper 	= stringextract('>Stage ARD<', 'gridlist', page)
		title 	= 'Highlights'
		# 14.11.2018 Bild vom 1. Beitrag befindet sich im json-Abschnitt,
		#	wird mittels href_id ermittelt:
		# 	href_id =  stringextract('/player/', '/', swiper) # Bild vom 1. Beitrag wie Highlights
		# 	img, sender = img_via_id(href_id, page)
		# 02.08.2019 href_id klappt für stage-Bilder nicht mehr - wieder im html-Abschnitt
		#	ermitteln (dto. in ARDStartRubrik):
		img		= stringextract('<img src="', '"', swiper) 
		summ = 'Highlights' 
		
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
			(urllib2.quote(path), urllib2.quote(title), 'Swiper')
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams)													

	widget_range= stringextract('APOLLO_STATE__', '"tracking"', page)	# Bereich WidgetID's ausschneiden 
	widget_list	= blockextract ('"id":"Widget:', widget_range)
	widget_list	= widget_list[1:]										# skip Stage (Swiper Block)
	PLog(len(widget_list))

	for grid in widget_list:
		wid = stringextract('"Widget:', '"', grid)	# "id":"58mGm6b0Wi4FSIcQ5TkPuq","type":"gridlist","title":...
		item	= stringextract('"id":"%s"' %  wid,  '{"id":', page)
		# PLog(item)
		title 	= stringextract('"title":"', '"', item)
		title 	= title.decode(encoding="utf-8")
		
		pageSize 	= stringextract('"pageSize":', ',', item)
		# pageSize stimmt nicht mit tats. Anzahl überein! Wir wiederholen statdessen den Titel, um
		#	im Webplayer die Ansicht Details zu erzwingen.
		# summ 	= "Beiträge: %s".decode(encoding="utf-8") % pageSize 
		widgetID = "%s|%s" % (wid, pageSize)
		offset = "pageNumber=0&pageSize=%s" % pageSize				# Verzicht auf horiz. Scrolling - alle zeigen
		path = 'http://page.ardmediathek.de/page-gateway/widgets/ard/editorials/%s?%s' % (wid, offset)
		img = R(ICON_DIR_FOLDER)
		
		if 'Livestream' in title:
			ID = 'Livestream'
		else:
			ID = 'ARDStart'			
		
		PLog('Satz:');
		title = UtfToStr(title);  
		PLog(title); PLog(widgetID); PLog(img); PLog(path)
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
			(urllib2.quote(path), urllib2.quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams)													

	xbmcplugin.endOfDirectory(HANDLE)

#-----------------------------------------------------------------------
# img_via_id: ermittelt im json-Teil (ARD-Neu) img + sender via href_id
def img_via_id(href_id, page):
	PLog("img_via_id: " + href_id)
	if href_id == '':
		img = R('icon-bild-fehlt.png')
		return img, ''									# Fallback bei fehlender href_id
		
	#item	= stringextract('Link:%s' %  href_id,  'idth}', page)
	item	= stringextract('%s.images.aspect16x9' %  href_id,  'idth}', page)
	# PLog('item: ' + item)
	
	img = ''
	if '16x9' in item:
		img =  stringextract('src":"', '16x9', item)	# Endung ../16x9/{w.. oder  /16x9/
	if '?w={w' in item:
		img =  stringextract('src":"', '?', item)		# Endung ..16-9.jpg?w={w..
		
	if img == '':										# Fallback bei fehlendem Bild
		img = R('icon-bild-fehlt.png')
	else:
		if img.endswith('.jpg') == False:
			img = img + '16x9/640.jpg'		
	
	# Y3JpZDovL2JyLmRlL3ZpZGVvL2YwMTIxM2RjLTAyYzgtNDZhYi1hZjEyLWM3YTFhYTRkMGVkOQ.publicationService":{"name":"
	sender	= stringextract('%s.publicationService":{"name":"' %  href_id,  '"', page)
	if sender == '':
		pos = page.rfind(href_id)
		PLog(pos)
		pos = page.find('publicationService', pos)
		PLog(pos)
		item= page[pos:pos+100]
		PLog(item)
		sender = stringextract('name":"', '"', item)
	PLog('img: ' + img)	
	PLog('sender: ' + sender)	
	return img, sender
	
#---------------------------------------------------------------------------------------------------
# Auflistung einer Rubrik aus ARDStart - geladen wird das json-Segment für die Rubrik, z.B.
#		page.ardmediathek.de/page-gateway/widgets/ard/editorials/5zY7iWtNzGagawo0A86Y6U?pageNumber=0&pageSize=12
#		path enthält entweder den Link zur html-Seite www.ardmediathek.de (ID=Swiper) oder den Link
#		zur json-Seite der gewählten Rubrik (früherer Abgleich html-Titel / json-Titel entfällt).
#		Die json-Seite kann Verweise zu weiteren Rubriken enthalten, z.B. bei Staffeln / Serien - Trigger hier
#			 mehrfach=True
# A-Z-Seiten werden in SendungenAZ_ARDnew vorbehandelt, die gefundenen Rubriken dannn hier. 
#		
#		Verzicht auf Vertikales Scrolling: wir laden den kompl. Inhalt - die Anzahl der Beiträge entnehmen
#		wir der Variablen pageSize (stimmt leider nicht mit der tats. Anzahl überein, ist immer größer).

def ARDStartRubrik(path, title, widgetID='', ID='', img=''): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title); PLog(path)	
	title = UtfToStr(title)
	title_org = title
			
	CurSender = Dict("load", 'CurSender')			
	CurSender = UtfToStr(CurSender)
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	page = False
	if 	ID == 'ARDStart':								# Startseite laden	
		page = Dict("load", 'ARDStartNEW_%s', CacheTime=ARDStartCacheTime)	# Seite aus Cache laden		

	if page == False:									# keine Startseite od. Cache miss								
		page, msg = get_page(path=path, GetOnlyRedirect=True)
		path = page
		page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	page = page.replace('\\"', '*')							# quotiere Marks entf.

	# Auswertung der Einzelbeiträge aus Highlights: Startseite ohne zusätzl. json-Seiten 
	if ID == 'Swiper':										# vorangestellte Highlights
		grid = stringextract('class="swiper-stage"', 'gridlist', page)
		sendungen = blockextract('class="_focusable', grid)
		for s in sendungen:
			href 	= stringextract('href="', '"', s) 
			if href.startswith('http') == False:
				href = BETA_BASE_URL + href
			
			title 	= stringextract('title="', '"', s)
			title	= unescape(title)
			title 	= title.decode(encoding="utf-8")
			# href_id =  stringextract('/player/', '/', s) # Bild via id 
			# img, sender = img_via_id(href_id, page)		 # Sender hier unteranderer ID
			# 02.08.2019 Swiper-img aus html-bereich (s. ARDStart) 
			img		= stringextract('<img src="', '"', s) 

			sender	= stringextract('subline">', '</h4>', s)
			sender	= unescape(sender) ;sender	= cleanhtml(sender)
			sender	= repl_json_chars(sender)
				
			duration= stringextract('duration">', '</div>', s)
			if sender:
				duration = '%s | %s' % (sender, duration)
			if duration == '':
				duration = 'Dauer unbekannt' 
			summ = ''	
			if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen,
				summ = get_summary_pre(href, 'ARDnew')
				if 	summ:
					if 	duration:
						summ = "%s\n\n%s" % (duration, summ)
			else:
				summ = duration
			PLog(title); PLog(href)	
						
			PLog('summ: ' + summ)		
			title = UtfToStr(title); summ = UtfToStr(summ); href = UtfToStr(href);
			duration = UtfToStr(duration); ID = UtfToStr(ID);
			title = repl_json_chars(title); summ = repl_json_chars(summ); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
				(urllib2.quote(href), urllib2.quote(title), duration, ID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, summary=summ)																										
		xbmcplugin.endOfDirectory(HANDLE)							# Ende Swiper

	mehrfach = False; mediatype=''
	if 'Livestream' in ID:
		gridlist = blockextract('"broadcastedOn"', page)
		if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
			mediatype='video'
	else:
		# die Seiten mit Videolinks (availableTo) können zusätzl. Beiträge enthalten
		#	('"images":') - z.Z. nicht berücksichtigt. Falls doch geplant, müssten sie
		#	unterhalb der Buttons Streaming-Formate +  MP4-Formate gelistet werden.
		#	Bsp.: BR/Serienhighlights (jew. 1 Video, mehrere Beitrag-Links).
		if 'target":{"id":"' in page:
			gridlist = blockextract('"availableTo"', page)	# Sendungen, json-key "teasers"	
		else:
			gridlist = blockextract('id":"Link:', page)		# deckt auch Serien in Swiper ab	
	if len(gridlist) == 0:	
		gridlist = blockextract( '"images":', page) 		# Fallback, ev. fehlt 1 Beitrag 			
		if len(gridlist) > 0:
			mehrfach = True
			PLog('weitere Rubriken')		
		
	if len(gridlist) == 0:				
		msg1 = 'keine Beiträge zu %s gefunden'  % title
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
	PLog('gridlist: ' + str(len(gridlist)))	
	
	if ID == 'A-Z':											# Button-rel. Titel Sendereihe holen
		title_pre = stringextract('"title":"', '"', page)
	
	cnt=0	
	for s  in gridlist:
		targetID=''
		if 'target":{"id":"' in s:
			targetID= stringextract('target":{"id":"', '"', s)	 	# targetID
		else:
			targetID= stringextract('id":"Link:', '"', s)			# Serie in Swiper via ARDStartSingle 
		
		PLog('targetID: ' + targetID)
		if targetID == '':										# keine Videos, skip
			continue
		href 	= 'https://www.ardmediathek.de/%s/live/%s' % (sender, targetID)
		
		if mehrfach == True:									# targetID von grouping-Url 
			groupingID= stringextract('/ard/grouping/', '"', s)	# leer bei Beiträgen von A-Z-Seiten
			if groupingID != '':
				targetID = groupingID
			href = 'http://page.ardmediathek.de/page-gateway/pages/%s/grouping/%s'  % (sender, targetID)
			if '/compilation/' in s:							# Bsp.: Filme nach Rubriken - keine grouping-Url
				hreflist = blockextract('"href":"', s)
				for h in hreflist:
					if '/compilation/' in h:
						href = stringextract('"href":"', '"', h)
						break
		
		if ID == 'A-Z' and title_pre:							# Button-relevanter Titel
			title 	= title_pre + ' | ' + stringextract('"title":"', '"', s)
		else:
			title 	= stringextract('"longTitle":"', '"', s)
		if title == '':
			title 	= stringextract('"title":"', '"', s)
		title 	= title.replace('- Standbild', '')	
		title	= unescape(title)
		title 	= title.decode(encoding="utf-8")
		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640')
		summ 	= stringextract('synopsis":"', '"', s)	
		summ 	= summ.decode(encoding="utf-8")
		
		duration= stringextract('"duration":', ',', s)			# Sekunden
		PLog('duration: ' + duration)
		duration = seconds_translate(duration)
		if duration :						# für Staffeln nicht geeignet
			duration = 'Dauer %s' % duration
		maturitytRating = stringextract('maturityContentRating":"', '"', page) # "FSK16"
		PLog('maturitytRating: ' + maturitytRating)				# außerhalb Block!
		if 	maturitytRating:
			duration = "%s | %s" % (duration, maturitytRating)	
			
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		if pubServ:
			if duration:
				duration = "%s | Sender: %s" % (duration, pubServ)
			else:
				duration = "Sender: %s" % (pubServ)
				
		title=UtfToStr(title); 
		if 'Hörfassung' in title or 'Audiodeskription' in title:				# Filter
			if SETTINGS.getSetting('pref_filter_hoerfassung') == 'true':
				continue		
			if SETTINGS.getSetting('pref_filter_audiodeskription') == 'true':
				continue		

		if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
			summ = get_summary_pre(href, 'ARDnew')
			if 	summ:
				if 	duration:
					summ 	= "%s\n\n%s" % (duration, summ)	
			
		# playlist_img = get_playlist_img hier entfernt - Verzicht auf ivesenderTV.xml
		
		PLog('Satz:');
		PLog(mehrfach); PLog(title); PLog(href); PLog(img); PLog(summ); PLog(duration); PLog(ID)
		title=UtfToStr(title); href=UtfToStr(href); img=UtfToStr(img); duration=UtfToStr(duration); 
		summ=UtfToStr(summ); ID=UtfToStr(ID);		
		title = repl_json_chars(title); summ = repl_json_chars(summ); 
		
		if mehrfach:
			fparams="&fparams={'path': '%s', 'title': '%s'}" % (urllib2.quote(href), urllib2.quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, mediatype=mediatype)																			
		else:
			tag = ''
			if duration not in summ:	# Doppler vermeiden
				tag = duration
			fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
				(urllib2.quote(href), urllib2.quote(title), duration, ID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ)	
		cnt=cnt+1																		
	
	if 	'AutoCompilationWidget'	in page:				# z.B. Scroll-Beiträge zu Rubriken
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		pageNumber, pageSize, totalElements, next_path = get_compilation(page)	# Basis 0
		# summ = "insgesamt: %s Beiträge" % totalElements # stimmt nicht mit Anz. Videos überein
		# summ = summ.decode(encoding="utf-8")
		tag = "weiter zu Seite 2" 
		PLog("cnt: " + str(cnt))
		if (cnt) < int(totalElements):	
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s'}" %\
				(urllib2.quote(title_org), urllib2.quote(next_path), pageNumber, pageSize)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDCompilation", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE)
#---------------------------------------------------------------------------------------------------
# ermittelt aus page die Parameter für AutoCompilationWidget (z.B. weitere Seiten für Rubriken)
#	pageNumber, pageSize, totalElements: Basis 0
def get_compilation(page):
	PLog("get_compilation:")
	
	widget 	= stringextract('AutoCompilationWidget', '"type"', page)
	widgetID= stringextract('Widget:', '"', widget)
	pageNumber 	= stringextract('pageNumber":', ',"', widget)
	pageSize 	= stringextract('pageSize":', ',"', widget)
	totalElements 	= stringextract('totalElements":', '},', widget)
	href	=  "http://page.ardmediathek.de/page-gateway/widgets/ard/compilation"
	next_path = ''
	if int(pageNumber) + 1 <= int(pageSize):
		pN = int(pageNumber) + 1
		next_path = "%s/%s?pageNumber=%d&pageSize=%s" % (href, widgetID, pN, pageSize)
	PLog(widget);PLog(widgetID);PLog(pageNumber);PLog(pageSize);PLog(totalElements);
	PLog(next_path)	
	
	return pageNumber, pageSize, totalElements, next_path
#---------------------------------------------------------------------------------------------------
# 1. Aufrufer: ARDStartRubrik mit pageNumber='1' - Seite 0 bereits ausgewertet
#	dann rekursiv (Mehr-Button) mit den ermittelten Werten pageNumber + pageSize
# Neuer Pfad wird hier mit den ermittelten Werten pageNumber + pageSize zusammengesetzt, Bsp.: 
#	http://page.ardmediathek.de/page-gateway/widgets/ard/compilation/3lCyQCGpIIkaos2EQqIu6q?pageNumber=0&pageSize=24
# Alternative: api-Call via get_api_call (für compilationId vorbereitet,
#	 myhash=0aa6f77b1d2400b94b9f92e6dbd0fabf652903ecf7c9e74d1367458d079f0810).
def ARDCompilation(title, path, pageNumber, pageSize, mediatype=''): 
	PLog('ARDCompilation:')
	PLog(path)
	
	title_org 	= title 
	title 		= title.decode(encoding="utf-8")		
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDCompilation: %s"	% title
		msg2=msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))	
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	
	li = get_comp_content(li, page, ID='ARDCompilation', mediatype=mediatype)
	
	if 	'AutoCompilationWidget'	in page:				# z.B. Scroll-Beiträge zu Rubriken
		title = "Mehr zu >%s<" % title_org		# Mehr-Button	 # ohne Pfad
		pageNumber, pageSize, totalElements, next_path  = get_compilation(page)
		
		# Mehr-Button, falls noch nicht alle Sätze ausgegeben		
		maxlen = (int(pageNumber) +1) * int(pageSize)		# Seitenzahl=Basis 0
		PLog("maxlen: " + str(maxlen)); 
		if maxlen < int(totalElements):
			# summ = "insgesamt: %s Beiträge" % totalElements # stimmt nicht mit Anz. Videos überein
			# summ = summ.decode(encoding="utf-8")	
			tag = "weiter zu Seite %d " % (int(pageNumber) + 2)
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s'}" %\
				(urllib2.quote(title_org), urllib2.quote(next_path), pageNumber, pageSize)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDCompilation", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE)
	
#---------------------------------------------------------------------------------------------------
# Auswertung für ARDCompilation 
def get_comp_content(li, page, ID, mediatype): 
	PLog('get_comp_content: ' + ID)
	
	CurSender = Dict("load", 'CurSender')					# Debug, Seite bereits senderspez.
	CurSender = UtfToStr(CurSender)
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)											#-> href
	
	# images + mediumTitle zu weit in Satz für gridlist
	gridlist = blockextract( 'availableTo":', page) 		# ARDCompilation  
	PLog('gridlist: ' + str(len(gridlist)))

	for s  in gridlist:
		targetID= stringextract('target":{"id":"', '"', s)	 	# targetID
		PLog(targetID)
		if targetID == '':													# keine Video
			continue
		href 	= 'https://www.ardmediathek.de/%s/live/%s' % (sender, targetID)
			
		if 'longTitle":"' in s:
			title 	= stringextract('longTitle":"', '"', s)
		if title == '':
				title 	= stringextract('mediumTitle":"', '"', s)		
	
		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640')
		summ 	= stringextract('synopsis":"', '"', s)	
		summ 	= summ.decode(encoding="utf-8")
			
		duration= stringextract('"duration":', ',', s)			# Sekunden
		duration = seconds_translate(duration)
		if duration :						# für Staffeln nicht geeignet
			duration = 'Dauer %s' % duration
		maturitytRating = stringextract('maturityContentRating":"', '"', page) # "FSK16"
		PLog('maturitytRating: ' + maturitytRating)				# außerhalb Block!
		if 	maturitytRating:
			duration = "%s | %s" % (duration, maturitytRating)	
			
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		if pubServ:
			if duration:
				duration = "%s | Sender: %s" % (duration, pubServ)
			else:
				duration = "Sender: %s" % (pubServ)

		summ = UtfToStr(summ); title = UtfToStr(title); duration = UtfToStr(duration);
		
		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(duration);
		fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
			(urllib2.quote(href), urllib2.quote(title), duration, ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, summary=summ, tagline=duration, mediatype=mediatype)	
	
	return li
#---------------------------------------------------------------------------------------------------
# Ermittlung der Videoquellen für eine Sendung - hier Aufteilung Formate Streaming + MP4
# Videodaten in json-Abschnitt __APOLLO_STATE__ enthalten.
# Bei Livestreams (m3u8-Links) verzweigen wir direkt zu SenderLiveResolution.
# Videodaten unterteilt in _plugin":0 und _plugin":1,
#	_plugin":0 enthält manifest.f4m-Url und eine mp4-Url, die auch in _plugin":1
#	vorkommt.
# Parameter duration (müsste sonst aus json-Daten neu ermittelt werden, Bsp. _duration":5318.
# Falls path auf eine Rubrik-Seite zeigt, wird zu ARDStartRubrik zurück verzweigt.
# 02.05.2019 erweitert: zusätzl. Videos zur Sendung angehängt - s.u.
#
def ARDStartSingle(path, title, duration, ID=''): 
	PLog('ARDStartSingle: %s' % ID);
	title = UtfToStr(title);  
	title_org 	= title 
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2=msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	page= page.replace('\u002F', '/')						# 25.07.2019: Slashes neuerdings quotiert
	
	elements = blockextract('availableTo":', page)			# möglich: Mehrfachbeiträge? 
	if len(elements) > 1:
		PLog('%s Elemente -> ARDStartRubrik' % str(len(elements)))
		return ARDStartRubrik(path,title)
	if len(elements) == 0:									# möglich: keine Video (dto. Web)
		msg1 = 'keine Beiträge zu %s gefunden'  % title
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)	
	PLog('elements: ' + str(len(elements)))	
		
	summ 		= stringextract('synopsis":"', '"', page)		# mit verfügbar wie	get_summary_pre
	verf=''
	if 'verfügbar bis:' in page:								# html mit Uhrzeit									
		verf = stringextract('verfügbar bis:', '</p>', page)	
		verf = cleanhtml(verf)
	if verf:													# Verfügbar voraanstellen
		summ = "[B]Verfügbar bis %s[/B]\n\n%s" % (verf, summ)
	img 		= stringextract('src":"', '"', page)
	
	img 		= img.replace('{width}', '640')
	sub_path	= stringextract('_subtitleUrl":"', '"', page)
	geoblock 	= stringextract('geoblocked":', ',', page)
	if geoblock == 'true':										# Geoblock-Anhang für title, summary
		geoblock = ' | Geoblock: JA'
		title = title + geoblock
	else:
		geoblock = ' | Geoblock: nein'
		
					
	# Livestream-Abzweig, Bsp. tagesschau24:	
	# 	Kennzeichnung Livestream: 'class="day">Live</p>' in ARDStartRubrik.
	if ID	== 'Livestream':									# Livestreams -> SenderLiveResolution		
		VideoUrls = blockextract('json":["', page)				# 
		href = stringextract('json":["', '"', VideoUrls[-1])	# master.m3u8-Url
		if href.startswith('//'):
			href = 'http:' + href
		PLog(href)
		# bis auf weiteres Web-Icons verwenden (16:9-Format OK hier für Webplayer + PHT):
		#playlist_img = get_playlist_img(hrefsender) # Icon aus livesenderTV.xml holen
		#if playlist_img:
		#	img = playlist_img
		#	PLog(title); PLog(hrefsender); PLog(img)
		return ardundzdf.SenderLiveResolution(path=href, title=title, thumb=img, descr=summ, Startsender='true')
	
	mediatype='							'# Kennz. Video für Sofortstart 
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	summ = repl_json_chars(summ)
	summ_lable = summ
	summ = summ.replace('\n','||')

	if duration == None or duration.strip() == '':
		duration = stringextract('_duration":', ',', page)	# Sekunden
		duration = 'Dauer %s Std.' % seconds_translate(duration)	
	tagline = duration
	# tagline=transl_doubleUTF8(tagline)		# Bsp. â<U+0088><U+0099> (a mit Circumflex)

	title=UtfToStr(title); summ=UtfToStr(summ); tagline=UtfToStr(tagline); 
	path=UtfToStr(path);						# Path kann Umlaute enthalten
	
	PLog(title); PLog(summ[:60]); PLog(tagline); PLog(img); PLog(path); PLog(sub_path);
	title_new 	= "[COLOR blue]Streaming-Formate[/COLOR] | %s" % title
	title_new = repl_json_chars(title_new); summ = repl_json_chars(summ); 
	
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'tagline': '%s', 'img': '%s', 'geoblock': '%s', 'sub_path': '%s'}" \
		% (urllib2.quote(path), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(tagline), urllib2.quote(img), 
			urllib2.quote(geoblock), urllib2.quote(sub_path))
	addDir(li=li, label=title_new, action="dirList", dirID="resources.lib.ARDnew.ARDStartVideoStreams", fanart=img, thumb=img, 
		fparams=fparams, summary=summ_lable, tagline=tagline, mediatype=mediatype)		
					
	title_new = "[COLOR blue]MP4-Formate und Downloads[/COLOR] | %s" % title	
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'tagline': '%s',  'img': '%s', 'geoblock': '%s', 'sub_path': '%s'}" \
		% (urllib2.quote(path), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(tagline), urllib2.quote(img), 
			urllib2.quote(geoblock), urllib2.quote(sub_path))
	addDir(li=li, label=title_new, action="dirList", dirID="resources.lib.ARDnew.ARDStartVideoMP4", fanart=img, thumb=img, 
		fparams=fparams, summary=summ_lable, tagline=tagline, mediatype=mediatype)	
		
	# zusätzl. Videos zur Sendung (z.B. Clips zu einz. Nachrichten).
	if 	ID == 'mehrzS':											# nicht nochmal "mehr" zeigen
		xbmcplugin.endOfDirectory(HANDLE)	
	if 	'>Mehr aus der Sendung<' in page: 						# z.B. in Verpasst-Seiten
		gridlist = blockextract( 'class="_focusable', page) 	# HTML-Bereich
	if len(gridlist) == 0:
		gridlist = blockextract( 'class="button _focusable"', page)	# Alternative - meist identisch
	if len(gridlist) > 0:
	 	PLog('gridlist_more: ' + str(len(gridlist)))	
		li = get_ardsingle_more(li,gridlist,page)				# mediatype=video hier vermeiden			
					
	xbmcplugin.endOfDirectory(HANDLE)
#----------------------------------------------------------------
# 										Mehr zur Sendung (Inhalte der Programmseite ARD-Neu)
#	Aufruf: ARDStartSingle
#	25.07.2019 mediatype hier nicht mit 'video' belegen (ARDStartSingle startet Player mit 
#		Addon-Url, falls Sofortstart EIN).
def get_ardsingle_more(li, gridlist, page, mediatype=''):				
	PLog('get_ardsingle_more:')
			
	for s  in gridlist:
		# PLog(s)
		if '/ard/player' in s == False:		# kein Beitrag
			continue
		summ = ''
		# href-Bsp. /ard/player/Y3JpZDovL ... 0NDM4NQ/wir-in-bayern-oder-16-04-2019
		href = BETA_BASE_URL + stringextract('href="', '"', s)		
		if href == '':											# skip
			continue
		href_id = stringextract('/player/', '/', href)	 	# href_id in player-Link

		title = stringextract('title="', '"', s) 			
		title	= "Mehr: %s" % unescape(title)
		tag = stringextract('class="subline">', '</h4>', s)
		tag = cleanhtml(tag) 		        
		img, sender = img_via_id(href_id, page)
		if 'duration' in s:
			duration = stringextract('class="duration">', '<', s)
			summ = 	"%s | Mehr aus der Sendung " % duration

		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); 
		 								 
		fparams="&fparams={'path': '%s', 'title': '%s', 'duration': ' ', 'ID': 'mehrzS'}" %\
			(urllib2.quote(href), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, summary=summ,  tagline=tag, mediatype=mediatype)	
																			
	return li
		
#---------------------------------------------------------------------------------------------------
#	Wiedergabe eines Videos aus ARDStart, hier Streaming-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
#	HTML-Seite mit json-Inhalt
def ARDStartVideoStreams(title, path, summ, tagline, img, geoblock, sub_path='', Merk='false'): 
	PLog('ARDStartVideoStreams:'); 
	
	title_org = title	
	geoblock = UtfToStr(geoblock)
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoStreams: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	page= page.replace('\u002F', '/')						# 25.07.2019: Slashes neuerdings quotiert
	
	href = ''; VideoUrls = []
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	if len(Plugins) > 0:
		Plugin1	= Plugins[0]							
		VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))
	
	if len(VideoUrls) > 0:									# nur 1 m3u8-Link möglich
		for video in  VideoUrls:							#	bei Jugemdschutz ges.
			# PLog(video)
			q = stringextract('_quality":"', '"', video)	# Qualität (Bez. wie Original)
			if q == 'auto':
				href = stringextract('json":["', '"', video)	# Video-Url
				quality = 'Qualität: automatische'
				PLog(quality); PLog(href)	 
				break
	else:
		href = stringextract('assetid":"', '"', page)

	if 'master.m3u8' not in href:							# möglich: ../master.m3u8?__b__=200
		msg = 'keine Streamingquelle gefunden - Abbruch' 	# auch möglich: nur .mp3-Quelle
		PLog(msg)
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		return li
	if href.startswith('http') == False:
		href = 'http:' + href
	href = href.replace('https', 'http')					# Plex: https: crossdomain access denied
		
	lable = 'Bandbreite und Auflösung automatisch ' 		# master.m3u8
	lable = lable + geoblock
	title 	= UtfToStr(title); title_org = UtfToStr(title_org); href = UtfToStr(href)
	img 	= UtfToStr(img); lable = UtfToStr(lable); summ	= UtfToStr(summ)
	tagline	= UtfToStr(tagline)
	
	Plot = "%s||||%s" % (tagline, summ)					# || Code für LF (\n scheitert in router)
	if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: ARDStartVideoStreams')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot, sub_path=sub_path, Merk=Merk)
		return
		
	title=repl_json_chars(title); title_org=repl_json_chars(title_org); lable=repl_json_chars(lable); 
	summ=repl_json_chars(summ); tagline=repl_json_chars(tagline); 
	summ_lable = summ.replace('||', '\n')
	
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
		(urllib.quote_plus(href), urllib.quote_plus(title_org), urllib.quote_plus(img), urllib.quote_plus(Plot), 
		urllib.quote_plus(sub_path), Merk)
	addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
		mediatype='video', tagline=tagline, summary=summ_lable) 
	
	li = ardundzdf.Parseplaylist(li, href, img, geoblock, tagline=tagline, descr=summ, sub_path=sub_path)	# einzelne Auflösungen 		
			
	xbmcplugin.endOfDirectory(HANDLE)
#---------------------------------------------------------------------------------------------------
#	Wiedergabe eines Videos aus ARDStart, hier MP4-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
def ARDStartVideoMP4(title, path, summ, tagline, img, geoblock, sub_path='', Merk='false'): 
	PLog('ARDStartVideoMP4:'); 
	title_org=title; summary_org=summ; thumb=img; tagline_org=tagline	# Backup 
	geoblock = UtfToStr(geoblock)	

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoMP4: %s"	% title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	page= page.replace('\u002F', '/')			# 25.07.2019: Slashes neuerdings quotiert
	
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	if len(Plugins) == 0:
		msg1 = "keine .mp4-Quelle gefunden zu: %s" % title_org
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
		return li
	Plugin1	= Plugins[0]							
	VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))

	# Format Downloadliste "Qualität: niedrige | Titel#https://pdvideosdaserste.."
	download_list = ARDStartVideoMP4get(title,VideoUrls)	# holt Downloadliste mit mp4-videos
	PLog(len(download_list))
	PLog(download_list[:1])									# 1. Element
	
	title 	= UtfToStr(title); title_org = UtfToStr(title_org); summary_org= UtfToStr(summary_org)
	tagline= UtfToStr(tagline); img = UtfToStr(img)
	title=repl_json_chars(title); title_org=repl_json_chars(title_org); summary_org=repl_json_chars(summary_org); 
	tagline=repl_json_chars(tagline); 

	# Sofortstart mit letzter=höchster Qualität	
	Plot = "%s||||%s" % (tagline, summary_org)		# || Code für LF (\n scheitert in router)
	if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart
		PLog('Sofortstart: ARDStartVideoMP4')
		video = download_list[-1]				# letztes Element = höchste Qualität
		meta, href = video.split('#')
		PLog(meta); PLog(href);
		quality 	= meta.split('|')[0]		# "Qualität: sehr hohe | Titel.."
		PLog(quality);
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot, sub_path=sub_path, Merk=Merk)
		return
		
	for video in  download_list:
		PLog(video);
		meta, href = video.split('#')
		quality 	= meta.split('|')[0]
		lable = quality	+ geoblock;	
		lable = UtfToStr(lable)
		PLog(href); PLog(quality); PLog(tagline); PLog(summary_org); 

		summ_lable = summary_org.replace('||', '\n')		
		Plot = "%s||||%s" % (tagline, summary_org)				# || Code für LF (\n scheitert in router)
		sub_path=''# fehlt noch bei ARD
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(urllib.quote_plus(href), urllib.quote_plus(title_org), urllib.quote_plus(img), 
			urllib.quote_plus(Plot), urllib.quote_plus(sub_path))
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype='video', tagline=tagline, summary=summ_lable) 
		
	if 	download_list:	
		title = " | %s"				
		PLog(title);PLog(summary_org);PLog(tagline);PLog(thumb);
		li = ardundzdf.test_downloads(li,download_list,title_org,summary_org,tagline,thumb,high=-1)  # Downloadbutton(s)		
	
	xbmcplugin.endOfDirectory(HANDLE)

#----------------------------------------------------------------
def ARDStartVideoMP4get(title, VideoUrls):	# holt Downloadliste mit mp4-videos für ARDStartVideoMP4
	PLog('ARDStartVideoMP4get:'); 
	title= UtfToStr(title)
			
	href = ''
	download_list = []		# 2-teilige Liste für Download: 'title # url'
	Format = 'Video-Format: MP4'
	for video in  VideoUrls:
		video= UtfToStr(video)
		href = stringextract('json":["', '"', video)	# Video-Url
		if href == '' or href.endswith('mp4') == False:
			continue
		if href.startswith('http') == False:
			href = 'http:' + href
		q = stringextract('_quality":"', '"', video)	# Qualität (Bez. wie Original)
		if q == '0':
			quality = 'Qualität: niedrige'
		if q == '1':
			quality = 'Qualität: mittlere'
		if q == '2':
			quality = 'Qualität: hohe'
		if q == '3':
			quality = 'Qualität: sehr hohe'
		
		PLog(quality)
		quality= UtfToStr(quality); href= UtfToStr(href);
		download_title = "%s | %s" % (quality, title)	# download_list stellt "Download Video" voran 
		download_list.append(download_title + '#' + href)	
	return download_list			
	
####################################################################################################
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
# in den vergangenen Monaten mehrfache Änderungen durch die ARD.
# Stand März 2019:
#	Scroll-Mechanismus für die Startseite A-Z (java-script-gesteuert). 
#	Die Plugin-Lösung ähnelt der Lösung für die Startseite. Bei Wahl eines Buttons 
#	werden die Links für die relevanten Beiträgen im json-Teil der html-Seite A-Z
#	ermittelt und einzeln in Schleife abgerufen (Begrenzung auf 20 Seiten wg. der 
#	langen Ladezeit).
# Stand April 2019:
#	Wegen der langen Ladezeit der einzelnen Beiträge Verwendung eines api-Calls
#	und sha256Hashes (beides undokum.) - diese liefern die Leitseiten für einz.
#	Buttons - s. SendungenAZ_ARDnew (Alle laden, nach Sender filtern).
#	Vorher laden wir hier mit api-Call die A-Z-Leitseite für den gewählten Sender
#	und ermitteln die unbelegten Buttons. Diese A-Z-Leitseite enthält keine Beiträge,
#	sondern die grouping-Links. 
#	Die grouping-Links werden in SendungenAZ_ARDnew bei Fehlschlag als Fallback 
#	verwendet - dazu wird die url_api übergeben.
			
def SendungenAZ(name, ID):		
	PLog('SendungenAZ: ' + name)
	PLog(ID)
	
	CurSender = Dict("load", 'CurSender')			
	CurSender = UtfToStr(CurSender)
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	title2 = name + ' | aktuell: %s' % sendername
	# no_cache = True für Dict-Aktualisierung erforderlich - Dict.Save() reicht nicht			 
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
		
	azlist = list(string.ascii_uppercase)				# A - Z
		
	myhash = 'fdbab76da7d6aeb1ae859e1758dd1db068824dbf1623c02bc4c5f61facb474c2' # A-Z-Leitseite
	url_api	= get_api_call('SendungenAZ', sender, myhash)

	page, msg = get_page(url_api, cTimeout=0)
	if page == '':	
		msg1 = "Fehler in SendungenAZ"
		msg2 = "Seite konnte nicht geladen werden:"
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, url_api)	
																
	azlist.insert(0,'#')							# früher 0-9	
	for button in azlist:	
		# PLog(button)
		title = "Sendungen mit " + button
		button 	= button.replace('#','09')
		show 	= 'shows%s":[]' % button			# Leerbutton
		if show in page:
			title = "keine Inhalte zu %s" % button
			summ = sendername
			fparams="&fparams={'name': '%s', 'ID': '%s'}" % ('Sendungen A-Z', 'ARD')
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ", fanart=R(ICON_ARD_AZ), thumb=R(ICON_ARD_AZ), 
				fparams=fparams, summary=summ)																	
		else:
			summ = 'Gezeigt wird der Inhalt für %s' % sendername
			summ = summ.decode(encoding="utf-8")				
			fparams="&fparams={'title': '%s', 'button': '%s', 'api_call': '%s'}" % (title, button, urllib2.quote(url_api))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ_ARDnew", fanart=R(ICON_ARD_AZ), thumb=R(ICON_ARD_AZ), 
				fparams=fparams, summary=summ)																	
										
	xbmcplugin.endOfDirectory(HANDLE)
####################################################################################################
# Auflistung der A-Z-Buttons bereits in SendungenAZ einschl. Kennz. "Keine Inhalte".
# Hinweise zu Änderungen durch die ARD (Scroll-Mechanismus) s. SendungenAZ.
#
# 04.04.2019 die vorherigen Mehr-Buttons entfallen - die einz. Beiträge brauchen
#	nicht mehr geladen zu werden. Statt dessen laden wir via api-Call die relevante
#	json-Seite für den gewählten Button (alle Sender) und filtern die Beiträge 
#	des aktuell gewählten Senders).
#	Die Hashes für den api-Call wurden via Chrome-Dev.-Tools ermittelt. Die hier
#	verwendeten gelten für den Senderbereich "Alle", für die einzelnen Sender 
#	existieren eigene Hashes, zusätzl. ein Hashwert für die A-Z-Leitseite, die 
#	in SendungenAZ für die Kennz. "Keine Inhalte" verwendet wird.
#	
#	Weiterverarbeitung in ARDStartRubrik.
#	Fallback - betrifft aktuell (06.04.2019) nur Button W (dto. Webseite):
#	Bei Fehlschlag (Sever-Error, leere Seite) laden wir die A-Z-Leitseite aus SendungenAZ
#	(url_api) und erstellen Buttons für die Beiträge zu den dort gelisteten grouping-Links.
#
# 	Merkmal A-Z-Seite: 'glossary":{"shows09' in page (ohne  pagination wie in ARDStartRubrik).
#
#		

def SendungenAZ_ARDnew(title, button, api_call): 
	PLog('SendungenAZ_ARDnew:')
	PLog('button: ' + button); 
	title = title	
	title_org = title
	url_api_org	= api_call	# speichern für Fehlschlag
		
	sha256Hashes_AZ = [		# dauerhafte Gültigkeit prüfen - Check 14.04.2019
					"09	56604d4f195e7eb318227fa01cdc424d5378d11b583d85c696d971ae19be2cf9",
					"A	3bfe84dc9887d0991263fb19dc4c5ba501bb5f27db0a06074b9b0e9ecf2c3c27",
					"B	557b3d0694f7d8d589e43c504a980f4090a025b8c2eefa6559b245f2f1a69e16",
					"C	4a35671fa57762f7e94a2aa79dc48f7fa9dde7c25387ecf9b722d37b26cc2d95",
					"D	f942fa0fe653a179d07349a907687544b090751deabe848919fc10949b3e05c6",
					"E	b7c5db273782bed01ae8ed000d7b5c7b6fdacad30b2d88690b1819c131439a61",
					"F	3fc33abce9a66d020a172a15268354acc4139652c4211be02f95ed470fc34962",
					"G	0ea25f94b3f8f4978bd55189392ed6a1874fe66c846a92734a50d3de37e4dad9",
					"H	fa55e3e6db3952d3cfb5a59fbfe413291fa11fdc07fac77b6f97d50478c9e201",
					"I	b5f9682e177cd52d7e1b02800271f0f2128ba738b58e3f8896b0bbfe925d4d72",
					"J	6da769a89ec95b2a50f4c751eb8935e42d826fa26946a2fa0e842e332883473f",
					"K	ac31e2cf0e381196de7e32ceeedfd1a53d67f5b926d86e37763bd00a6d825be3",
					"L	81668bf385abcf876495cdf4280a83431787c647fa42defb82d3096517578ab3",
					"M	7277a409abd703c9c2858834d93a18fdfce0ea0aee3a416a6bdea62a7ac73598",
					"N	dc8b7e99c2aa1397e658fb380fe96d7fb940d18b895c2336f3284751898d48c7",
					"O  5ad27bbec3d8fbc6ea7dc74f3cae088f2160120b4a7659ba5ed62e950301a0b6",
					"P	3a3c88b51baddc0e9a2d1bb7888e4d44ec8901d0f5f448ca477b36e77aac8efd",
					"Q	5ad27bbec3d8fbc6ea7dc74f3cae088f2160120b4a7659ba5ed62e950301a0b6",
					"R	7e8cd2c0c128019fe0885cc61b5320867ec211dcd2f0986238da07598d826587",
					"S	a56ae9754a77be068bc3d87c8bf0d8229a13bd570d4230776bfbb91c0496a022",
					"S	048cd18997a847069d006adf86879944e1b5069ff2258e5cb3c1a37d2265b91e",
					"T  048cd18997a847069d006adf86879944e1b5069ff2258e5cb3c1a37d2265b91e",
					"U  cc8ae75b395d3faa3b338e19815af7d6af4ad8c5f462e1163b2fa8bae5404a54",
					"V	a348091704377530f2b4db50cdf4287859424855aad21d99c64f8454c602698a",
					"W	1c8d95d7f0f74fe53f6021ef9146183f19ababd049b31e0b9eb909ffcf86d6c0",
					"X	unbelegt",
					"Y	8bc949cd1652c68b4ff28ac9d38c5450fe6e42783428135fe65af3f230414668",
					"Z	cc7a222db4cc330c2a5a74f8cd64157f255dcfec9272b7fe8f742d2e489aae8f"
				]

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	CurSender = Dict("load", 'CurSender')		
	CurSender = UtfToStr(CurSender)
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	
	myhash = ''
	for Hash in sha256Hashes_AZ:
		b, myhash = Hash.split()
		PLog(b); PLog(myhash)
		if b == button:
			break

	url_api	= get_api_call('SendungenAZ_ARDnew', 'ard', myhash) # ard: A-Z für alle laden, später filtern
	page, msg = get_page(url_api, cTimeout=0)					
	if page == '':	
		return 	Objget_api_callectContainer(header='Error', message=msg)						
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	# RSave('/tmp/x.html', page)							# Debug
	
	if page.startswith('{"errors":'):						# Seite Alle kann Fehler liefern, obwohl die
		msg = stringextract('message":"', '"', page)		# 	A-Z-Seite des Senders Daten enthält
		msg = "ARD Server-Error: %s" % msg
		PLog(msg)
		
	gridlist = blockextract( '"mediumTitle":', page) 		# Beiträge?
	PLog('gridlist: ' + str(len(gridlist)))			
	if len(gridlist) == 0:				
		msg = 'keine Beiträge zu %s gefunden, starte Fallback'.decode(encoding="utf-8")  % title
		PLog(msg)			
		page, msg = get_page(url_api_org, cTimeout=0)			# Fallback: grouping-Links aus SendungenAZ
		links = stringextract('"shows%s"' % button, 'hows', page) # 'hows' schließt auch Z bei "ShowsPage"ab
		glinks = blockextract('"id":',  links)
		if len(glinks) == 0:
			msg = 'Keine Beiträge gefunden zu %s' % button		# auch Fallback gescheitert
			xbmcgui.Dialog().ok(ADDON_NAME, msg, '', '')	
			
		i=0
		sender=UtfToStr(sender); button=UtfToStr(button); 
		for glink in glinks:									# Fallback-Listing
			i=i+1
			targetID = stringextract('id":"', '"', glink)
			href 	= 'http://page.ardmediathek.de/page-gateway/pages/%s/grouping/%s'  % (sender, targetID)	
			label 	= '%s. Gruppe Beiträge zu %s' % ( str(i), button)
			summ 	= 'Gezeigt wird der Inhalt für %s' % sendername
			tag	 	= 'lokale Beiträge (keine auf Alle-Seite gefunden)'
			img		= R(ICON_ARD_AZ)
			
			# Kennzeichnung ID='A-Z' für ARDStartRubrik
			PLog("Satz_glink:")
			href=UtfToStr(href); label=UtfToStr(label); 
			PLog(glink); PLog(href); PLog(label);
			fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" %\
				(urllib2.quote(href), urllib2.quote(label), 'A-Z')
			addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, tagline=tag)													
							
		xbmcplugin.endOfDirectory(HANDLE)							# Ende Fallback	
			
	# ab hier normale Auswertung	
	for s  in gridlist:
		targetID= stringextract('target":{"id":"', '"', s)	 	# targetID
		PLog(targetID)
		if targetID == '':													# keine Video
			continue
		groupingID= stringextract('/ard/grouping/', '"', s)	# leer bei Beiträgen von A-Z-Seiten
		if groupingID != '':
			targetID = groupingID
		href = 'http://page.ardmediathek.de/page-gateway/pages/%s/grouping/%s'  % (sender, targetID)

		title 	= stringextract('"longTitle":"', '"', s)
		if title == '':
			title 	= stringextract('"title":"', '"', s)
		title 	= title.replace('- Standbild', '')	
		title	= unescape(title)
		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640')
		summ 	= stringextract('synopsis":"', '"', s)	
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		tagline = "Sender: %s" % pubServ		
		PLog(az_sender); PLog(pubServ)
		if sender != 'ard':								# Alle (ard) oder filtern
			if az_sender != pubServ:
				continue

		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(tagline);
		summ = "%s\n\n%s" % (tagline, summ)
		fparams="&fparams={'path': '%s', 'title': '%s'}" %\
			(urllib2.quote(href), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams, summary=summ)													

	xbmcplugin.endOfDirectory(HANDLE)


#-----------------------
# get_api_call erstellt API-Call für ARD A-Z, ARDSearchnew + ev. weitere Funkt.
#	Werte pageNumber, version als json-int einfügen.
def get_api_call(function, sender, myhash, pageNumber='', text='', clipId='', deviceType=''):

	url_api 	= 'https://api.ardmediathek.de/public-gateway'
	variables 	= '{"client":"%s"}'	% sender
	
	if pageNumber and text:										# ARDSearchnew
		variables = '{"client":"%s","pageNumber":%s,"text":"%s"}'	% (sender, str(pageNumber), text)
		
	if clipId and deviceType:									# Einzelbeitrag (statt player-Url)
		variables = '{"client":"%s", "clipId":"%s","deviceType":"%s"}'	% (sender, clipId, deviceType)
		
	
	extensions	= '{"persistedQuery":{"version":1,"sha256Hash":"%s"}}' % myhash
	variables =  urllib.quote_plus(variables)                   # & nicht codieren!
	extensions =  urllib.quote_plus(extensions)                	# & nicht codieren!
	url_api 	= "%s?variables=%s&extensions=%s"  % (url_api, variables, extensions)
	PLog('url_api %s: %s' % (function, url_api))
	return url_api
	
#---------------------------------------------------------------- 
# Suche in beiden Mediatheken
#	Abruf jeweils der 1. Ergebnisseite
#	Ohne Ergebnis -> Button mit Rücksprung hierher
#	Ergebnis ZDF: -> ZDF_Search (erneuter Aufruf Seite 1, weitere Seiten dort rekursiv)
#		Ablage in Dict nicht erf., Kodi-Cache ausreichend.
#	Umlaute in Suche erzeugen unicode-Strings - UtfToStr-Behandl. jeweils in den Funktions-
#		ketten.
#
def SearchARDundZDFnew(title, query='', pagenr=''):
	PLog('SearchARDundZDFnew:');
	
	if query == '':
		query = ardundzdf.get_query(channel='ARDundZDF') 
	if  query == None or query.strip() == '':
		# return li														# getting plugin Error
		return ardundzdf.Main()
		
	PLog(query)
	query_ard = query.split('|')[0]
	query_zdf = query.split('|')[1]
	
	tag_negativ ='neue Suche in ARD und ZDF starten'					# ohne Treffer
	tag_positiv ='gefundene Beiträge zeigen'							# mit Treffer
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)												# Home-Button
	
	#------------------------------------------------------------------	# Suche ARD
	sendername, sender, kanal, img, az_sender = ARDSender[0].split(':') # in allen Sendern
	pageNumber = 1
	myhash = 'ebd79f9a91c559ec31363f2b6448fb489ddf4742c1ca911d3c16391e72d6bb18'  # Chrome-Dev.-Tools		
	url_api	= get_api_call('ARDSearchnew', 'ard', myhash, pageNumber, text=query_ard) 
	
	query_lable = query_ard.replace('+', ' ')
	page, msg = get_page(path=url_api)	
		
	vodTotal	= stringextract('"vodTotal":', ',', page)		# Beiträge?
	gridlist = blockextract( '"mediumTitle":', page) 			# Sicherung?
	if len(gridlist) == 0 or vodTotal == '0':				
		label = "ARD | nichts gefunden zu: %s | neue Suche" % query_lable
		title="Suche in ARD und ZDF"
		fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		title = "ARD: %s Video(s)  | %s" % (vodTotal, query_lable)
		PLog(query_ard)
		fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '0'}" %\
			(urllib2.quote(query_ard), urllib2.quote(title), sender)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
		
	#------------------------------------------------------------------	# Suche ZDF
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path_zdf = ZDF_Search_PATH % (urllib2.quote(query_zdf), pagenr) 
	page, msg = get_page(path=path_zdf)	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog(searchResult);
	
	query_lable = (query_zdf.replace('%252B', ' ').replace('+', ' ')) 	# quotiertes ersetzen 
	query_lable = urllib2.unquote(query_lable)
	if searchResult == '0' or 'class="artdirect " >' not in page:		# Sprung hierher
		label = "ZDF | nichts gefunden zu: %s | neue Suche" % query_lable
		title="Suche in ARD und ZDF"
		fparams="&fparams={'title': '%s'}" % urllib2.quote(title)
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		title = "ZDF: %s Video(s)  | %s" % (searchResult, query_lable)
		fparams="&fparams={'query': '%s', 'title': '%s', 'pagenr': '%s'}" % (urllib.quote_plus(query_zdf), 
			title, pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
				
	xbmcplugin.endOfDirectory(HANDLE)
	
#---------------------------------------------------------------- 
# Suche in Mediathek Neu 
# Statt des api-Calls funktioniert auch https://www.ardmediathek.de/ard/search/%s
# 	(Auswertung anpassen).
def ARDSearchnew(title, sender, offset=0, query=''):
	PLog('ARDSearchnew:');	
	PLog(sender); PLog(offset); PLog(query)
	sender = UtfToStr(sender)
	
	if query == '':
		query = get_keyboard_input() 
		if query == None:					# None bei Abbruch
			return
	query = query.strip()
	
	if int(offset) == 0:
		pageNumber = 1
	else:
		pageNumber=str(offset)
	myhash = 'ebd79f9a91c559ec31363f2b6448fb489ddf4742c1ca911d3c16391e72d6bb18'  # Chrome-Dev.-Tools
	url_api	= get_api_call('ARDSearchnew', 'ard', myhash, pageNumber, text=query) 

	page, msg = get_page(url_api)					
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	if page == '':	
		msg1 = "Fehler in ARDSearchnew, Suche: %s"	% query
		msg2=msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return li
	PLog(len(page))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	gridlist = blockextract( '"mediumTitle":', page) 		# Beiträge?
	if len(gridlist) == 0:				
		msg1 = 'keine Beiträge gefunden zu: %s'  % query
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)		
	PLog('gridlist: ' + str(len(gridlist)))	
	
	mediatype=''; ID='ARDSearchnew'
	for s  in gridlist:
		summ = ''
		target 	= stringextract('target":{"href":"', '"', s)	 	# target-Pfad
		targetID = target.split('/')[-1]						# ID abschneiden
		PLog(targetID)
		if targetID == '':													# keine Video
			continue
		href = "%s/ard/player/%s"  % (BETA_BASE_URL,targetID)

		if 'mediumTitle":"' in s:
			title 	= stringextract('mediumTitle":"', '"', s)
		if title == '':
				title 	= stringextract('shortTitle":"', '"', s)		

		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640')
		img_title = stringextract('"title":"', '"', s)

		duration= stringextract('"duration":', ',', s)			# Sekunden
		PLog('duration: ' + duration)
		duration = seconds_translate(duration)
		if duration:						# für Staffeln nicht geeignet
			duration = 'Dauer %s' % duration
		pubServ = stringextract('publicationService":{"name":"', '"', s)	# Sender
		tagline = "Sender: %s" % pubServ
		if 	duration:
			tagline = "%s | %s" % (tagline, duration)
		PLog("Mark2")
		
		if sender != 'ard':								# Alle (ard) oder filtern
			if sender not in pubServ.lower():
				continue		
		PLog("Mark3")

		summ 	= stringextract('synopsis":"', '"', s)	# descr scheint hier zu fehlen 
		if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
			if summ == '':										# 	falls leer
				summ = get_summary_pre(path=href, ID='ARDnew')
				if 	summ:
					if 	duration:
						summ = "%s\n\n%s" % (duration, summ)
				else:
					summ = 	duration
						
		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(duration); 
		title=UtfToStr(title); href=UtfToStr(href); duration=UtfToStr(duration); 
		title = repl_json_chars(title); summ = repl_json_chars(summ);
		 
		fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
			(urllib2.quote(href), urllib2.quote(title), duration, ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, tagline=tagline, summary=summ, mediatype=mediatype)	
			
	title = "Mehr zu >%s<" % urllib2.unquote(query)		# Mehr-Button
	offset = int(offset) +1
	# die Werte in vodTotal + vodPageSize stimmen nicht mit Anzal der
	#	Beiträge überein.
	#vodTotal	= stringextract('"vodTotal":', ',', page)
	#vodPageSize = stringextract('"vodPageSize":', ',', page)
	#tagline = "zu Seite %s (von %s)" % (str(offset+1), vodPageSize)	
	fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '%s'}" %\
		(urllib2.quote(query), urllib2.quote(title), sender, str(offset))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", fanart=R(ICON_MEHR), 
		thumb=R(ICON_MEHR), fparams=fparams)																	
	
	xbmcplugin.endOfDirectory(HANDLE)

#---------------------------------------------------------------- 
# Verpasst Mediathek Neu - Liste Wochentage
#
def ARDVerpasst(title, CurSender):
	PLog('ARDVerpasst:');
	PLog(CurSender)
	
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		ardDate = rdate.strftime("%Y-%m-%d")
		myDate  = rdate.strftime("%d.%m.")		# Formate s. man strftime (3)
		# path- Bsp.: https://www.ardmediathek.de/br/program/2019-04-15	
		if  nr == 0:							# Heute mit Datum: leere Seite
			path = "%s/%s/program/" % (BETA_BASE_URL, sender)
		else:
			path = "%s/%s/program/%s" % (BETA_BASE_URL, sender, ardDate)
		
		iWeekday = rdate.strftime("%A")
		iWeekday = transl_wtag(iWeekday)
		iWeekday = iWeekday[:2].upper()
		if nr == 0:
			iWeekday = 'HEUTE'	
		if nr == 1:
			iWeekday = 'GESTERN'	
		title =	"%s %s" % (iWeekday, myDate)	# DI 09.04.
		tagline = "Sender: %s" % sendername	
		
		PLog(title); PLog("path: " + path)
		fparams="&fparams={'title': '%s', 'path': '%s', 'CurSender': '%s'}" % (title,  urllib2.quote(path), urllib2.quote(CurSender))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasstContent", fanart=R(ICON_ARD_VERP), 
			thumb=R(ICON_ARD_VERP), fparams=fparams, tagline=tagline)
	
	xbmcplugin.endOfDirectory(HANDLE)

#---------------------------------------------------------------- 
# ARDVerpasstContent Mediathek Neu - Inhalt des gewählten Tages
#	Seite html (Urhzeit, Titel, Link) / json (Blöcke "shortTitle") 
def ARDVerpasstContent(title, path, CurSender, timeline_sender=''):
	PLog('ARDVerpasstContent:');
	PLog(title); PLog(timeline_sender);
	title = UtfToStr(title); timeline_sender = UtfToStr(timeline_sender)
	
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	
	page, msg = get_page(path)
	if page == '':	
		msg1 = 'Fehler in ARDVerpasstContent'
		msg2=msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, path)	
		return li
	PLog(len(page))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	if 'ardmediathek.de/ard/' in path:			# ARD-Alle: erst Senderliste zeigen
		if timeline_sender == '':						#	nur beim 1. Aufruf
			slist =  re.findall('id="timeline-(.*?)"', page)
			PLog("timelines: " + str(slist))
			if slist:
				for s in slist:
					label = "Sender: %s" % s.upper()
					PLog(label); 
					fparams="&fparams={'title': '%s', 'path': '%s', 'CurSender': '%s', 'timeline_sender': '%s'}" \
						% (title,  urllib2.quote(path), urllib2.quote(CurSender), s)
					addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasstContent", 
						fanart=R(ICON_DIR_FOLDER), thumb=R(ICON_DIR_FOLDER), fparams=fparams, tagline=title)
			xbmcplugin.endOfDirectory(HANDLE)
	else:
		timeline_sender	= stringextract('ardmediathek.de/', '/', path)		
	
	if timeline_sender:										# timeline auch in einz. Senderseite 
		gridlist = blockextract('id="timeline-', page)	
		for s in gridlist:
			timeline_sender=UtfToStr(timeline_sender)
			if "timeline-%s" % timeline_sender in s:		# Block gefunden
				PLog("timeline gefunden: %s" %  timeline_sender)
				page = s
				break 						

	gridlist = blockextract( 'class="link _focusable"', page) # HTML-Bereich
	if len(gridlist) == 0:				
		msg1 = 'keine Beiträge gefunden zu: %s'  % title
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
	PLog('gridlist: ' + str(len(gridlist)))	
	
	mediatype=''; ID='ARDVerpasst'
	img = R(ICON_DIR_FOLDER)								# PRG-seiten ohne Icons
	for s  in gridlist:
		summ = ''
		# href-Bsp. /ard/player/Y3JpZDovL ... 0NDM4NQ/wir-in-bayern-oder-16-04-2019
		href = BETA_BASE_URL + stringextract('href="', '"', s)		
		if href == '':											# skip
			continue
		href_id = stringextract('/player/', '/', href)	 	# href_id hier in href

		title = stringextract('headline">', '<', s) 			
		# title = stringextract('title="', '"', s) 				# enthält Zeit - 2 Std.
		title	= unescape(title)
		title = repl_json_chars(title)
		title = title.replace('| Kategorie', '')
		# title = "%s | %s"  % (sender, title)         
		zeit = stringextract('time">', '<', s)					# Sendezeit
		zeit = addHour(zeit, 2)
		title = "%s | %s"  % (zeit, title)
		if sender: 			
			zeit = "%s Uhr | Sender: %s" % (zeit, sender)
		else:
			zeit = "%s Uhr | Sender: %s" % (zeit, sendername)
		zeit=UtfToStr(zeit); 
		

		if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
			if summ == '':										# 	falls leer
				summ = get_summary_pre(path=href, ID='ARDnew')
				if 	summ:
					if 	zeit:
						summ = "%s\n\n%s" % (zeit, summ)
				else:
					summ = 	zeit
		else:
			summ = 	zeit

		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(zeit); 
		title=UtfToStr(title); href=UtfToStr(href); summ=UtfToStr(summ);  
		title = repl_json_chars(title); summ = repl_json_chars(summ);
		 
		fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
			(urllib2.quote(href), urllib2.quote(title), '', ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, summary=summ, mediatype=mediatype)																			
	
	xbmcplugin.endOfDirectory(HANDLE)
	
#----------------------------------------------------------------
#	Offset für ARDVerpasstContent - aktuell 2 Stunden
#	string zeit, int offset - Bsp. 15:00, 2
def addHour(zeit, offset):
	PLog('addHour:');
	hour, minutes = zeit.split(':') 
	hour = int(hour)
	hour = hour + offset
	
	if hour >= 24:
		hour = hour - 24

	zeit = "%02d:%s" % (hour, minutes)
	PLog(zeit)
	return zeit

####################################################################################################
def Senderwahl(title):	
	PLog('Senderwahl:'); 
	# Senderformat Sendername:Sender (Pfadbestandteil):Kanal:Icon
	#	Bsp.: 'ARD-Alle:ard::ard-mediathek.png', Rest s. ARDSender[]
	# 		
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')							# Home-Button
	
	for entry in ARDSender:								# entry -> CurSender in Main_ARD
		if 'KiKA' in entry:								# bisher nicht in Base- und AZ-URL enthalten
			continue
		sendername, sender, kanal, img, az_sender = entry.split(':')
		PLog(entry)
		PLog('sendername: %s, sender: %s, kanal: %s, img: %s, az_sender: %s'	% (sendername, sender, kanal, img, az_sender))
		title = 'Sender: %s' % sendername
			
		fparams="&fparams={'name': 'ARD Mediathek', 'CurSender': '%s'}" % urllib2.quote(entry)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Main_NEW", fanart=R(img), thumb=R(img), 
			fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		

