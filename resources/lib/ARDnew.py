# -*- coding: utf-8 -*-
################################################################################
#				ARDnew.py - Teil von Kodi-Addon-ARDundZDF
#			neue Version der ARD Mediathek, Start Beta Sept. 2018
#
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.ardmediathek.de/,
#	Seiten werden im json-Format, teilweise html + json ausgeliefert
#	04.11.2019 Migration Python3
#	21.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#
################################################################################
#	Stand 10.07.2021

# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys, subprocess
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

# Python
import string, re
import  json		
import datetime, time
import math							# für math.ceil (aufrunden)


# Addonmodule + Funktionsziele (util_imports.py)
import ardundzdf					# -> SenderLiveResolution, Parseplaylist, BilderDasErste, BilderDasErsteSingle
from resources.lib.util import *


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
	'BR:br:2224:tv-br.png:BR Fernsehen', 'HR:hr:5884:tv-hr.png:HR Fernsehen', 'MDR:mdr:1386804:tv-mdr-sachsen.png:MDR Fernsehen', 
	'NDR:ndr:5898:tv-ndr-niedersachsen.png:NDR Fernsehen', 'Radio Bremen:radiobremen::tv-bremen.png:Radio Bremen TV', 
	'RBB:rbb:5874:tv-rbb-brandenburg.png:rbb Fernsehen', 'SR:sr:5870:tv-sr.png:SR Fernsehen', 
	'SWR:swr:5310:tv-swr.png:SWR Fernsehen', 'WDR:wdr:5902:tv-wdr.png:WDR Fernsehen',
	'ONE:one:673348:tv-one.png:ONE', 'ARD-alpha:alpha:5868:tv-alpha.png:ARD-alpha', 
	'tagesschau24:tagesschau24::tv-tagesschau24.png:tagesschau24', 'phoenix:phoenix::tv-phoenix.png:phoenix', 
	'KiKA::::KiKA']

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])
FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

ARDStartCacheTime = 300						# 5 Min.	
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	PLog('Matrix-Version')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")

# Ort FILTER_SET wie filterfile (check_DataStores):
FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()					# gesetzte Filter initialiseren 

fname = os.path.join(DICTSTORE, 'CurSender')			# init CurSender (aktueller Sender)
if os.path.exists(fname) == False:						# kann fehlen (Aufruf Merkliste)
	Dict('store', "CurSender", ARDSender[0])			# Default: ARD-Alle

DEBUG			= SETTINGS.getSetting('pref_info_debug')
NAME			= 'ARD und ZDF'

#----------------------------------------------------------------
# sender neu belegt in Senderwahl
def Main_NEW(name, CurSender=''):
	PLog('Main_NEW:'); 
	PLog(name); PLog(CurSender)
			
	if ':' not in CurSender:			# '', False od. 'False'
		CurSender = ARDSender[0]
	
	Dict('store', "CurSender", CurSender)
	PLog('sender: ' + CurSender); 
	CurSender=py2_encode(CurSender);
	
	sendername, sender, kanal, img, az_sender = CurSender.split(':')	# sender -> Menüs
		
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
			
	title = 'Suche in ARD-Mediathek'
	tag = 'Sender: [COLOR red] %s [/COLOR]' % sendername
	title=py2_encode(title);
	fparams="&fparams={'title': '%s', 'sender': '%s' }" % (quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", fanart=R(ICON_MAIN_ARD), 
		thumb=R(ICON_SEARCH), tagline=tag, fparams=fparams)
		
	title = 'Startseite'	
	tag = 'Sender: [COLOR red] %s [/COLOR]' % sendername
	summ = "[COLOR red] barrierefreie Angebote[/COLOR] im Untermenü <Genrezugänge>"
	title=py2_encode(title);
	fparams="&fparams={'title': '%s', 'sender': '%s'}" % (quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", fanart=R(ICON_MAIN_ARD), thumb=R(img), 
		tagline=tag, summary=summ, fparams=fparams)

	# Retro-Version ab 12.11.2020, V3.5.4
	# 16.06.2021 auch erreichbar via ARD-Startseite/Premium_Teaser_Themenwelten		
	title = "ARD Mediathek RETRO"
	erbe = u"[COLOR darkgoldenrod]%s[/COLOR]" % "UNESCO Welttag des Audiovisuellen Erbes"
	tag = u'Die ARD Sender öffneten zum %s ihre Archive und stellen zunehmend zeitgeschichtlich relevante Videos frei zugänglich ins Netz' % erbe
	tag = u"%s\n\nDeutsche Geschichte und Kultur nacherleben: Mit ARD Retro können Sie in die Zeit der 1950er und frühen 1960er Jahre eintauchen. Hier stoßen Sie auf spannende, informative und auch mal kuriose Sendungen aus den Anfängen der Fernsehgeschichte des öffentlich-rechtlichen Rundfunks." % tag
	tag = u"%s\n\nMehr: NDR ardretro100.html" % tag
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDRetro", fanart=R(FANART), 
		thumb=R('ard-mediathek-retro.png'), tagline=tag, fparams=fparams)

	title = 'Sendung verpasst'
	tag = 'Sender: [COLOR red] %s [/COLOR]' % sendername
	fparams="&fparams={'title': 'Sendung verpasst', 'CurSender': '%s'}" % (quote(CurSender))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasst", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_VERP), tagline=tag, fparams=fparams)
	
	title = 'Sendungen A-Z'
	tag = 'Sender: [COLOR red] %s [/COLOR]' % sendername
	fparams="&fparams={'name': 'Sendungen A-Z', 'ID': 'ARD'}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_AZ), tagline=tag, fparams=fparams)
						
	title = 'ARD Sportschau'
	fparams="&fparams={'title': '%s'}"	% title
	addDir(li=li, label=title, action="dirList", dirID="ARDSport", 
		fanart=R("tv-ard-sportschau.png"), thumb=R("tv-ard-sportschau.png"), fparams=fparams)
						
	title = 'Bildgalerien Das Erste'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="BilderDasErste", fanart=R(ICON_MAIN_ARD),
		thumb=R('ard-bilderserien.png'), fparams=fparams)

	title 	= u'Wählen Sie Ihren Sender | aktuell: [COLOR red]%s[/COLOR]' % sendername	# Senderwahl
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", fanart=R(ICON_MAIN_ARD), 
		thumb=R('tv-regional.png'), fparams=fparams) 

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		 		
#---------------------------------------------------------------- 
# Startseite der Mediathek - passend zum ausgewählten Sender -
# 27.10.2019 Laden aus Cache nur noch bei Senderausfall - vorheriges Laden mit ARDStartCacheTime
#	als 1. Stufe störte beim Debugging
#
# 27.05.2020 ARD hat das Seitenlayout geändert:
#	der Scrollmechanismus entfällt. Aufrufer ohne aktiv. Java-Script erhalten eine kompl. Startseite.
#	Für die Auswertung geeignet ist nur der untere Teil. Er enthält ab window.__FETCHED_CONTEXT__
#	die json-Inhalte.
#	Wir extrahieren in ARDStart die Container, jeweils mit den Bildern des 1. Beitrags.
#	Weiterverarbeitung in ARDStartRubrik (path -> json-Seite)
#	Frühere Kopf-Doku entfernt - siehe commits zu V<=3.0.3
#	Problem Stringauswertung: die ersten 4 Container folgen doppelt (bei jedem Sender) - Abhilfe: 
#		Abgleich mit Titelliste. Wg. Performance Verzicht auf json-/key-Auswertung.
#
def ARDStart(title, sender, widgetID=''): 
	PLog('ARDStart:'); 
	
	CurSender = Dict("load", 'CurSender')		
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	tagline = 'Mediathek des Senders [COLOR red] %s [/COLOR]' % sendername
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	path = BETA_BASE_URL + "/%s/" % sender
	page, msg = get_page(path=path)			# vom Sender holen
	
	if '"widgets":' not in page:								# Fallback: Cache ohne CacheTime
		page = Dict("load", 'ARDStartNEW_%s' % sendername)					
		msg1 = "Startseite nicht im Web verfuegbar."
		PLog(msg1)
		msg3=''
		if page:
			msg2 = "Seite wurde aus dem Addon-Cache geladen."
			msg3 = "Seite ist älter als %s Minuten (CacheTime)" % str(ARDStartCacheTime/60)
		else:
			msg2='Startseite nicht im Cache verfuegbar.'
		MyDialog(msg1, msg2, msg3)	
	else:	
		Dict("store", 'ARDStartNEW_%s' % sendername, page) 	# Seite -> Cache: aktualisieren	
	PLog(len(page))
	page = page.replace('\\"', '*')							# quotierte Marks entf.
	
	
	container = blockextract ('compilationType":', page)  	# Container json-Bereich (Swiper + Rest)
	PLog(len(container))
	title_list=[]											# für Doppel-Erkennung

	for cont in container:
		title 	= stringextract('"title":"', '"', cont)
		if title in title_list:								# Doppel? - s.o.
			break
		title_list.append(title)
		
		ID	= stringextract('"id":"', '"', cont)
		anz= stringextract('"totalElements":', '}', cont)
		anz= mystrip(anz)
		PLog("anz: " + anz)
		if anz == '1':
			tag = u"%s Beitrag" % anz
		else:
			if anz == "null": anz='mehrere'
			tag = u"%s Beiträge" % anz

		path 	= stringextract('"href":"', '"', cont)
		path = path.replace('&embedded=false', '')			# bzw.  '&embedded=true'
		img = img_preload(ID, path, title, 'ARDStart')
		
		if 'Livestream' in title or up_low('Live') in up_low(title):
			if 'Konzerte' not in title:						# Corona-Zeit: Live-Konzerte (keine Livestreams)
				ID = 'Livestream'
		else:
			ID = 'ARDStart'			
		
		PLog('Satz_cont1:');
		PLog(title); PLog(ID); PLog(anz); PLog(img); 
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
			(quote(path), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			tagline=tag, fparams=fparams)
			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#-----------------------------------------------------------------------
# 19.10.2020 Ablösung img_via_id durch img_preload nach Änderung 
#	der ARD-Startseite: lädt das erste img ermittelt in geladener
#	Seite oder ID.img aus dem Cache - Löschfrist: Setting Slide Shows)
#
def img_preload(ID, path, title, caller, icon=ICON_MAIN_ARD):
	PLog("img_preload: " + title)
	PLog(caller); PLog(path)

	if caller == 'ARDStart':
		leer_img = R(ICON_DIR_FOLDER)
	else:
		leer_img = R(icon-bild-fehlt.png)

	img=''
	oname = os.path.join(SLIDESTORE, "ARDNeu_Startpage")
	fname = os.path.join(oname, ID)
	PLog(fname)
	
	if os.path.isdir(oname) == False:
		try:  
			os.mkdir(oname)
		except OSError as exception:
			msg = str(exception)
			PLog(msg)
			
	if os.path.exists(fname):							# img aus Cache laden
		return fname
	else:
		page, msg = get_page(path=path)					# ganze Seite von Sender laden	
		if page=='':
			return leer_img								# Fallback 
	
	img = stringextract('src":"', '"', page)			# Pfad zum 1. img
	if img == '':
		return leer_img									# Fallback 
	
	img = img.replace('{width}', '720')
	urlretrieve(img, fname)								# img -> Cache
	icon = R(icon)
	msg1 = "Lade Bild"
	msg2 = title										# Dateiname bei ARD neu nichtssagend
	xbmcgui.Dialog().notification(msg1,msg2,icon,2000, sound=False)	 
		
	PLog('img: ' + fname)	
	return fname										# lokaler img-Pfad
	
#---------------------------------------------------------------------------------------------------
# Auflistung der Rubriken in json-Seite page
def ARDRubriken(li, page): 
	PLog('ARDRubriken:')

	container = blockextract ('compilationType":', page)  	# Test auf Rubriken
	PLog(len(container))
	title_list=[]
	for cont in container:
		title 	= stringextract('"title":"', '"', cont)		
		if title in title_list:								# Doppel? - s.o.
			break
		title_list.append(title)

		ID	= stringextract('"id":"', '"', cont)
		anz= stringextract('"totalElements":', '}', cont)
		anz= mystrip(anz)
		PLog("anz: " + anz)
		if anz == '1':
			tag = u"%s Beitrag" % anz
		else:
			if anz == "null": anz='mehrere'
			tag = u"%s Beiträge" % anz

		path 	= stringextract('"href":"', '"', cont)
		path = path.replace('&embedded=false', '')			# bzw.  '&embedded=true'
		img 	= stringextract('"src":"', '"', cont)		# mehrere Formate möglich, 1. Treffer
		img 	= img.replace('{width}', '640'); 
		if img == '':
			img = img_preload(ID, path, title, 'ARDStart')# kann dauern..
		if img == '':
			img = R(ICON_DIR_FOLDER)

		ID = 'ARDStartRubrik'
		PLog('Satz_cont2:');
		PLog(title); PLog(ID); PLog(anz); PLog(img); 
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
			(quote(path), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			tagline=tag, fparams=fparams)
			
	return

###################################################			

#---------------------------------------------------------------------------------------------------
# Auflistung einer Rubrik aus ARDStart - geladen wird das json-Segment für die Rubrik, z.B.
#		page.ardmediathek.de/page-gateway/widgets/ard/editorials/5zY7iWtNzGagawo0A86Y6U?pageNumber=0&pageSize=12
#		path enthält entweder den Link zur html-Seite www.ardmediathek.de (ID=Swiper) oder den Link
#		zur json-Seite der gewählten Rubrik (früherer Abgleich html-Titel / json-Titel entfällt).
#		Die json-Seite kann Verweise zu weiteren Rubriken enthalten, z.B. bei Staffeln / Serien - Trigger hier
#			 mehrfach=True
#
# Aufrufe: Rubriken aus ARDStart, Sendereihen aus A-Z-Seiten, Mehrfachbeiträge aus ARDSearchnew
# 28.05.2020 getrennte Swiper-Auswertung entfällt nach Änderung der ARD-Seiten
#		
def ARDStartRubrik(path, title, widgetID='', ID='', img=''): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title); PLog(path)	
	title_org = title
	
	CurSender = Dict("load", 'CurSender')				# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
		
	li = xbmcgui.ListItem()
	if ID == "ARDRetroStart":
		li = home(li, ID=NAME)							# Home-Button -> Hauptmenü
	else:
		if ID != 'Livestream':							# ohne home - Nutzung durch Classic
			li = home(li, ID='ARD Neu')					# Home-Button

	page = False
	if 	'/editorials/' in path == False:				# nur kompl. Startseite aus Cache laden (nicht Rubriken) 
		if ID != 'ARDStartSingle':	
			page = Dict("load", 'ARDStartNEW_%s' % sendername, CacheTime=ARDStartCacheTime)	# Seite aus Cache laden		

	if page == False:									# keine Startseite od. Cache miss								
		page, msg = get_page(path=path, GetOnlyRedirect=True)
		path = page
		page, msg = get_page(path=path)	
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	page = page.replace('\\"', '*')						# quotierte Marks entf.

#----------------------------------------
	mark=''
	container = blockextract ('compilationType":', page)# Test auf Rubriken
	PLog(len(container))
	if len(container) > 1:
		ARDRubriken(li, page)							# direkt
	else:
		li = get_page_content(li, page, ID, mark)		# Auswertung Rubriken																	
#----------------------------------------
	
	# 24.08.2019 Erweiterung auf pagination, bisher nur AutoCompilationWidget
	#	pagination mit Basispfad immer vorhanden, Mehr-Button abhängig von Anz. der Beiträge
	if 	'"pagination":'	in page:						# Scroll-Beiträge
		PLog('pagination_Rubrik:')
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		pages, pN, pageSize, totalElements, next_path = get_pagination(page)	# Basis 0		
		
		if next_path:	
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements)
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % str(pN)
			PLog(summ); PLog(next_path)
			
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s'}" % (quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDPagination", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#---------------------------------------------------------------------------------------------------
# ermittelt aus page die Parameter für pagination oder AutoCompilationWidget (Scroll-Seiten Rubriken)
# Rückgabe: Pfad mit inkrementierter pageNumber oder  leerer Pfad', falls Beiträge für weitere
#	Seiten fehlen. 
# Nicht für ARDSearchnew - eigene Scrollverwaltung (Parameterbez., Pfad bleibt api-Call)
# Bsp. nur pagination: 				Startseite/Tatort & Polizeiruf
# Bsp. AutoCompilationWidget:	Startseite/Filme nach Rubriken/Alle Filme
# Bsp. Pfade (Auszug): 	/page-gateway/widgets/ard/compilation/, /page-gateway/widgets/ard/asset/,
#						/page-gateway/widgets/ard/editorials/
# pageNumber, pageSize, totalElements: Basis 0
#
def get_pagination(page):
	PLog("get_pagination:")

	pagination	= stringextract('pagination":', '"type"', page)
	pageNumber 	= stringextract('pageNumber":', ',"', pagination)
	pageSize 	= stringextract('pageSize":', ',"', pagination)
	totalElements 	= stringextract('totalElements":', '},', pagination)
	href 		= stringextract('href":"', '"', pagination)	# akt. Pfad mit widgetID
	if '?' in href:
		href		= href.split('?')[0]					# trennt pageNumber + pageSize ab
		
	if 'AutoCompilationWidget' in page:
		PLog('AutoCompilationWidget')
		widget 	= stringextract('AutoCompilationWidget', '"type"', page)
		widgetID= stringextract('Widget:', '"', widget)
		href = href.replace('pages/ard', 'widgets/ard')		# leicht verändert!
		PLog(widget[:100]);PLog(widgetID)
	
	href = href.replace('{', '')							# { statt " möglich		
	PLog('href_akt: %s' % href)
	PLog('pageNumber: %s, pageSize: %s, totalElements:%s ' % (pageNumber, pageSize, totalElements))
	if pageSize == '' or totalElements == '':				# Sicherung 
		return "", "", "", "", ""
	
	next_path=''; pN=''
	pages = float(totalElements) / float(pageSize)
	pages = int(math.ceil(pages))					# aufrunden für Seitenrest
	
	
	pN = int(pageNumber) + 1			# nächste pageNumber 
	if pN < int(pages):
		next_path = "%s?pageNumber=%d&pageSize=%s" % (href, pN, pageSize)
	PLog(pN);PLog(pageSize);PLog(totalElements);PLog(pages);
	PLog(next_path)
	
	return pages, pN, pageSize, totalElements, next_path
#---------------------------------------------------------------------------------------------------
# 1. Aufrufer: ARDStartRubrik mit pageNumber='1' - Seite 0 bereits ausgewertet
#	dann rekursiv (Mehr-Button) mit den ermittelten Werten pageNumber + pageSize
# Neuer Pfad wird hier mit den ermittelten Werten pageNumber + pageSize zusammengesetzt, Bsp.: 
#	http://page.ardmediathek.de/page-gateway/widgets/ard/compilation/3lCyQCGpIIkaos2EQqIu6q?pageNumber=0&pageSize=24
# Alternative: api-Call via get_api_call 
#	 27.06.2020 Alternative entfällt nach ARD-Änderungen - s. ARDSearchnew,
#		get_api_call entfernt
#
def ARDPagination(title, path, pageNumber, pageSize, ID, mark): 
	PLog('ARDPagination: ' + ID)
	PLog(path)
	
	title_org 	= title 
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDPagination: %s"	% title
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	page = page.replace('\\"', '*')							# quotierte Marks entf.
	
	
	li = get_page_content(li, page, ID, mark)
	
	if 	'"pagination":'	in page:				# z.B. Scroll-Beiträge zu Rubriken
		title = "Mehr zu >%s<" % title_org		# Mehr-Button	 # ohne Pfad
		pages, pN, pageSize, totalElements, next_path  = get_pagination(page)
		
		# Mehr-Button, falls noch nicht alle Sätze ausgegeben		
		if next_path:
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements) 
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % pN	
			
			PLog(summ); PLog(next_path)
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s'}" % (quote(title_org), quote(next_path), pN, pageSize, ID, quote(mark))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDPagination", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE)
	
####################################################################################################
#							ARD Retro www.ardmediathek.de/ard/retro/
#					vorerst Heimat im Modul ARDnew - bei Bedarf auslagern
####################################################################################################
def ARDRetro(): 
	PLog('ARDRetro:'); 
	
	sendername = "ARD-Alle"
	title2 = "Sender: ARD-Alle"
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)									# Home-Button -> Hauptmenü

	path = "https://www.ardmediathek.de/ard/retro/" 
	# Seite aus Cache laden
	page = Dict("load", 'ARDRetro', CacheTime=ARDStartCacheTime)
	if page == False:										# nicht vorhanden oder zu alt
		page, msg = get_page(path=path)						# vom Sender holen
		if page == '':	
			msg1 = "Fehler Startseite ARDRetro"
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
		else:	
			Dict("store", 'ARDRetro', page) 				# Seite -> Cache: aktualisieren		
	PLog(len(page))
	RSave('/tmp/x.html', py2_encode(page))	# Debug			
	
	# json:
	page = stringextract('<body', '</body>', page)
	# Rubriken: 
	ARDRubriken(li, page)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------------------------------------------
# Auswertung für ARDStartRubrik + ARDPagination + ARDSearchnew 
#	Mehrfach- und Einzelsätze
# mark: farbige Markierung in title (z.B. query aus ARDSearchnew) 
# Seiten sind hier bereits senderspezifisch.
# Aufrufe Direktsprünge
#	
def get_page_content(li, page, ID, mark='', mehrzS=''): 
	PLog('get_page_content: ' + ID); PLog(mark)
	ID_org=ID
	
	CurSender = Dict("load", 'CurSender')					# Debug, Seite bereits senderspez.
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)												#-> href
	
	mediatype=''; pagetitle=''
	pagination	= stringextract('pagination":', '"type"', page)
	pagetitle 	= stringextract('title":"', '"', pagination)	# bei Suche: SearchCompilationWidget:..
	PLog(pagetitle)
	page = page.replace('\\"', '*')								# quotierte Marks entf., Bsp. \"query\"
	
	if 'Livestream' in ID or 'EPG' in ID:
		gridlist = blockextract('"broadcastedOn"', page)
	else:
		if  ID == 'Search':										# Search immer Einzelbeiträge
			mehrfach = False
			gridlist = blockextract( '"ondemand"', page)				
		else:
			if 'target":{"id":"' in page:
				gridlist = blockextract('"availableTo"', page)	# Sendungen, json-key "teasers"	
			else:
				gridlist = blockextract('id":"Link:', page)		# deckt auch Serien in Swiper ab
					
		if 'ARDStart' in ID:									# zusätzl. Beiträge ganz links, Livestream 
			decorlist = blockextract( '"decor":', page)		# 	möglich, s.u.
			PLog('decorlist: ' + str(len(decorlist)))
			gridlist = decorlist
			
		if len(gridlist) == 0:									# Fallback (außer Livestreams)
			gridlist = blockextract( '"images":', page) 		# geändert 20.09.2019 
							
		
	if len(gridlist) == 0:		
		msg1 = 'keine Beiträge gefunden'
		PLog(msg1)
		MyDialog(msg1, '', '')	
	PLog('gridlist: ' + str(len(gridlist)))	

	for s  in gridlist:
		uhr=''
		PLog("Mark10")
		if 'EPG' not in ID:										# decor im 1. Drittel
			pos = s.find('"decor"',100)							# möglich: Block reicht in Folgeblock
			if pos > 100:										# eigenes decor zw. broadcastedOn + duration
				s = s[:pos]
		
		mehrfach = True											# Default weitere Rubriken
		if 'target":{"id":"' in s:
			targetID= stringextract('target":{"id":"', '"', s)	# targetID, auch Search
		else:
			targetID= stringextract('id":"Link:', '"', s)		# Serie in Swiper via ARDStartSingle 
		PLog(targetID)
		if targetID == '':										# kein Video
			continue			

		PLog('"availableTo":null' in s)							# kein Einzelbetrag
		if '/compilation/' in s or '/grouping/' in s:			# Serie Vorrang vor z.B. Teaser 
			mehrfach = True
		if ID == 'EPG':
			mehrfach = False
		# if '"availableTo":"' in s or '"duration":' in s or 'Livestream' in ID:	# Einzelbetrag
		if '"duration":' in s or 'Livestream' in ID or 'type":"live"' in s:			# Einzelbetrag, Livestream
			#if s.find('"availableTo":null') < 0:				# auch bei  vorh. Videos möglich
			mehrfach = False
					
		href=''
		if mehrfach == True:									# Pfad für Mehrfachbeiträge ermitteln 						
			url_parts = ['/grouping/', '/compilation/', '/editorial/']
			hreflist = blockextract('"href":"', s)
			#PLog("hreflist: " + str (hreflist))
			for h in hreflist:
				for u in url_parts:
					if u in h:
						href = stringextract('"href":"', '"', h)
						break
		else:
			hreflist = blockextract('"href":"', s)
			for h in hreflist:
				if 'embedded=true' in h:
					href = stringextract('"href":"', '"', h)
					break
		# PLog("href: " + str (href))	
								
		title=''	
		if 'longTitle":"' in s:
			title 	= stringextract('longTitle":"', '"', s)
		if title == '':
				title 	= stringextract('mediumTitle":"', '"', s)
		if title == '':
				title 	= stringextract('shortTitle":"', '"', s)
		title = transl_json(title)					# <1u002F2> =  <1/2>
		title = unescape(title); 
		title = repl_json_chars(title)	
		
		if mehrzS:
			title = u"Mehr: %s" % title	

		if mark:
			PLog(title); PLog(mark)
			title = title.strip() 
			title = make_mark(mark, title, "red")	# farbige Markierung
	
		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640'); 
		img= img.replace('u002F', '/')
		summ=''
		if ID != 'Livestream':
			PLog("pre: %s" % s[:80])				# Verfügbar + Sendedatum aus s laden (nicht Zielseite) 
			summ = get_summary_pre(path='dummy', ID='ARDnew', skip_verf=False, skip_pubDate=False, page=s)
		else:
			summ = title
		if "Sendedatum:" in summ:									# aus Rückabe get_summary_pre
			uhr = summ.split(' ')[-2]
	
		title = repl_json_chars(title); summ = repl_json_chars(summ);
		# ARDVerpasstContent: Zeit im Titel, Langfass. tagline:
		if ID == 'EPG' and uhr:									
			title = "[COLOR blue]%s[/COLOR] | %s" % (uhr, title) 			
			pubServ = stringextract('publicationService":{"name":"', '"', s)	# publicationService (Sender)
			if pubServ:
				summ = "%sSender: %s" % (summ, pubServ)
				
		PLog("full_shows")									# full_show im Titel: ganze Sendungen rot+fett
		if ID != 'EPG' and SETTINGS.getSetting('pref_mark_full_shows') == 'true':
			fname = SETTINGS.getSetting('pref_fullshows_path')
			if fname == '':
				fname = '%s/resources/%s' % (ADDON_PATH, "full_shows_ARD")
			else:
				fname = "%s/full_shows_ARD" % SETTINGS.getSetting('pref_mark_full_shows')
			shows = ReadTextFile(fname)
			PLog('full_shows_lines: %d' % len(shows))
				
			for show in shows:
				sd, md = show.split("|")
				sd = u'title":"%s' % sd						# Bsp. 'title":"Querbeet|40'
				#PLog(sd); PLog(md); PLog(up_low(sd) in up_low(s));
				if up_low(sd) in up_low(s):					# Show in Datensatz?
					md_rec = stringextract('duration":', ',', s)
					PLog("md_rec: " + md_rec)
					if md_rec:
						md_rec = seconds_translate(md_rec)
						PLog("md_rec2: " + md_rec)
						if md_rec.endswith("sec"): 			# Korr. sec < 60 -> 1 min
							md_rec = "0:01"
						md_rec = time_to_minutes(md_rec)
						if int(md_rec) >= int(md):
							title = "[B][COLOR red]%s[/COLOR][/B]" % title
					break		
		
		PLog('Satz:');
		PLog(mehrfach); PLog(title); PLog(href); PLog(img); PLog(summ[:60]); PLog(ID)
		
		if href == '':
			continue
		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					break		
			if filtered:
				# PLog('filtered: ' + title)
				continue		
		
		if mehrfach:
			summ = "Folgeseiten"
			href=py2_encode(href); title=py2_encode(title); 
			fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, mediatype='')																							
		else:
			if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
				summ_new = get_summary_pre(path=href, ID='ARDnew')  # s.o. pre:
				if 	summ_new:
					summ = summ_new
					
			if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
				mediatype='video'
			
			if '"type":"live"' in s:								# Livestream im Stage-Bereich
				ID = "Livestream"
			else:
				ID=ID_org

			summ_par = summ.replace('\n', '||')
			href=py2_encode(href); title=py2_encode(title); summ_par=py2_encode(summ_par);
			fparams="&fparams={'path': '%s', 'title': '%s', 'summary': '%s', 'ID': '%s'}" %\
				(quote(href), quote(title), quote(summ_par), ID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, mediatype=mediatype)	
	
	return li
		
#---------------------------------------------------------------------------------------------------
# Ermittlung der Videoquellen für eine Sendung - hier Aufteilung Formate Streaming + MP4
# Videodaten in json-Abschnitt __APOLLO_STATE__ enthalten.
# Bei Livestreams (m3u8-Links) verzweigen wir direkt zu SenderLiveResolution.
# Videodaten unterteilt in _plugin":0 und _plugin":1,
#	_plugin":0 enthält manifest.f4m-Url und eine mp4-Url, die auch in _plugin":1
#	vorkommt.
# Falls path auf eine Rubrik-Seite zeigt, wird zu ARDStartRubrik zurück verzweigt 
#	(sofern keine Streams vorhanden)
# 02.05.2019 erweitert: zusätzl. Videos zur Sendung angehängt - s.u.
# 28.05.2020 Stream-Bezeichner durch ARD geändert
# 19.10.2020 Mehr-Auswertung an ARD-Änderungen angepasst: get_ardsingle_more entfällt,
#	Auswertung durch get_page_content nach entfernung des 1. elements und 
#	page="\n".join(gridlist). mehrzS verhindert Rekursion.	
# 13.11.2020 Anpassung an ARDRetro: Switch Home-Button via ID=ARDRetroStart (dto. in
#	ARDStartVideoStreams + ARDStartVideoMP4, Änderung mehrzS (ID -> Flag, Rekurs.-Stop)
# 05.01.2021 Anpassung für Sofortstart-Format: HLS_List + MP4_List -> PlayVideo_Direct
#	(Streamwahl -> PlayVideo)
# 21.01.2021 Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
# 25.01.2021 no-cache-Header für Verpasst- und A-Z-Beiträge
#
def ARDStartSingle(path, title, summary, ID='', mehrzS=''): 
	PLog('ARDStartSingle: %s' % ID);
	title_org = title

	headers=''
	# Header für Verpasst-Beiträge (ARDVerpasstContent -> get_page_content)
	if ID == 'EPG' or ID == 'A-Z':											
		headers = "{'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma':'no-cache',\
			'Expires': '0'}"		

	page, msg = get_page(path, header=headers)
	if page == '':	
		msg1 = "Fehler in ARDStartSingle: %s"	% title
		msg2=msg
		MyDialog(msg1, msg2, '')	
		xbmcplugin.endOfDirectory(HANDLE)
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Python3 geändert
	page= page.replace('+++\\n', '+++ ')					# Zeilentrenner ARD Neu

	elements = blockextract('"availableTo":', page)			# möglich: Mehrfachbeiträge? z.B. + Hörfassung
	IsPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)') # 'true' / 'false'
	PLog("IsPlayable: %s" % IsPlayable)	
	if len(elements) > 1:
		if '_quality"' not in page:							# bei Streamlinks bleiben wir hier
			if IsPlayable == "false":						# IsPlayable-Einträge nur mit Video-Quellen auswerten
				PLog('%s Elemente -> ARDStartRubrik' % str(len(elements)))
				return ARDStartRubrik(path,title,ID='ARDStartSingle')
			else:
				msg1 = u">%s< enthält Folgebeiträge."	% title
				msg2 = u"Anzeige mit Sofortstart nicht möglich."
				MyDialog(msg1, msg2, '')	
				return										# hebt IsPlayable auf (Player-Error: skipping ..)
			
			
	if len(elements) == 0:									# möglich: keine Video (dto. Web)
		msg1 = u'keine Beiträge zu %s gefunden'  % title
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)	
	PLog('elements: ' + str(len(elements)))	
		
	li = xbmcgui.ListItem()
	if ID == "ARDRetroStart":
		li = home(li, ID=NAME)								# Home-Button -> Hauptmenü
	else:
		if ID != 'Livestream':								# ohne home - Nutzung durch Classic
			li = home(li, ID='ARD Neu')						# Home-Button

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
		VideoUrls = blockextract('_quality', page)				# 2 master.m3u8-Url (1 x UT)
		PLog(len(VideoUrls))
		for video in VideoUrls:
			href = stringextract('stream":"', '"', video)	
			if SETTINGS.getSetting('pref_UT_ON') == 'true':		# UT-Stream filtern, bisher nur ARD, HR
				if '_ut_' in href or '_sub' in href:
					break
			else:
				break
		if href.startswith('//'):
			href = 'http:' + href
		PLog('Livestream_Abzweig: ' + href)
		return ardundzdf.SenderLiveResolution(path=href, title=title, thumb=img, descr=summary)
		
	# -----------------------------------------			# Extrakt Videoquellen
	Plugins = blockextract('_plugin', page)				# wir verwenden nur Plugin1 (s.o.)
	if len(Plugins) > 0:
		Plugin1	= Plugins[0]							
		VideoUrls = blockextract('_quality', Plugin1, "publicationService")
	PLog(len(VideoUrls))
	
	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	HBBTV_List=''										# nur ZDF
	HLS_List = ARDStartVideoHLSget(title, VideoUrls)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = ARDStartVideoMP4get(title, VideoUrls)	# Extrakt MP4
	Dict("store", 'ARDNEU_HLS_List', HLS_List) 
	Dict("store", 'ARDNEU_MP4_List', MP4_List) 
	PLog("download_list: " + str(MP4_List)[:80])
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_ready:');
	# summ = get_summary_pre(path, ID='ARDnew', page=page)	# entfällt mit summary aus get_page_content 
	Plot = "Titel: %s\n\n%s" % (title_org, summary)				# -> build_Streamlists_buttons
	PLog('Plot:' + Plot)
	thumb = img; ID = 'ARDNEU'; HOME_ID = "ARD Neu"
	ardundzdf.build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)
	
	# -----------------------------------------		# mehr (Videos) zur Sendung
	if mehrzS:										# nicht nochmal "mehr" zeigen
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

	PLog('Mehr_Test')
	# zusätzl. Videos zur Sendung (z.B. Clips zu einz. Nachrichten). element enthält 
	#	Sendungen ab dem 2. Element (1. die Videodaten)
	# 19.10.2020 Funktion get_ardsingle_more entfällt
	if len(elements) > 1 and SETTINGS.getSetting('pref_more') == 'true':
		gridlist = elements[1:]						# hinter den Videodaten (1. Element)
		PLog('gridlist_more: ' + str(len(gridlist)))	
		page  = "\n".join(gridlist)					# passend für get_page_content 
		PLog(page[:1000])
		get_page_content(li, page, ID=ID, mehrzS=True, mark='')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------
# auto-Stream master.m3u8 aus VideoUrls ermitteln, 
#	via li in Einzelauflösungen zerlegen
# Aufrufer ARDStartSingle (Länge VideoUrls > 0)
#
def ARDStartVideoHLSget(title, VideoUrls): 
	PLog('ARDStartVideoHLSget:'); 
	PLog(str(VideoUrls)[:100])
	
	HLS_List=[]; Stream_List=[];
	title = py2_decode(title)
	href=''
	for video in  VideoUrls:				
		# PLog(video)
		if 'u"auto"' in video or  u'master.m3u8' in video:	# master.m3u8
			href = stringextract('stream":"', '"', video)	# Video-Url
			if href.startswith('http') == False:
				href = 'https:' + href
			quality = u'automatisch'
			HLS_List.append(u'HLS automatische Anpassung ** auto ** auto ** %s#%s' % (title,href))
			break
			
	li=''; img=''; geoblock=''; descr='';					# für Stream_List n.b.
	if href:
		Stream_List = ardundzdf.Parseplaylist(li, href, img, geoblock, descr, stitle=title, buttons=False)
		if type(Stream_List) == list:						# Fehler Parseplaylist = string
			HLS_List = HLS_List + Stream_List
		else:
			HLS_List=[]
	#PLog(Stream_List)
	
	return HLS_List

#----------------------------
# holt Downloadliste mit MP4-Videos
# altes Format: "Qualität: niedrige | Titel#https://pdvideosdaserste.."
# neues Format:	"MP4 Qualität: Full HD ** Bandbreite ** Auflösung ** Titel#Url"
#
def ARDStartVideoMP4get(title, VideoUrls):	
	PLog('ARDStartVideoMP4get:'); 
			
	href=''; quality=''
	title = py2_decode(title)
	download_list = []		# 2-teilige Liste für Download: 'title # url'
	Format = 'Video-Format: MP4'
	for video in  VideoUrls:
		PLog(video[:100])
		if 'stream":["' in video:							# mögliche: 2 Url's in Liste, Unterschied n.b.
			href = stringextract('stream":["', '"', video)
		else:
			href = stringextract('stream":"', '"', video)	# Video-Url
		if href == '' or 'm3u8' in href:		
			continue
		if '.mp4' not in href:							# funk-Beiträge: ..src_1024x576_1500.mp4?fv=1
			continue
		if href.startswith('http') == False:
			href = 'https:' + href
		q = stringextract('_quality":', ',', video)		# Qualität (Bez. wie Original)
		q = str(q).strip()
		PLog("q: " + q)

		w=''; h=''; bitrate=0
		if '0' in q:
			quality = u'niedrige'
			bitrate = u"256312"
			if "_width" not in video:
				w = "480"; h = "270"					# Probeentnahme							
		if '1' in q:
			quality = u'mittlere'
			bitrate = "1024321"
			if "_width" not in video:
				w = "640"; h = "360"					# Probeentnahme							
		if '2' in q:
			quality = u'hohe'
			bitrate = u"1812067"
			if "_width" not in video:
				w = "960"; h = "540"					# Probeentnahme							
		if '3' in q:
			quality = u'sehr hohe'
			bitrate = u"3621101"
			if "_width" not in video:
				w = "1280"; h = "720"					# Probeentnahme							
		if '4' in q:
			quality = u'Full HD'
			bitrate = u"6501324"
			if "_width" not in video:
				w = "1920"; h = "1080"					# Probeentnahme							

		#if int(q) >= 2:								# Auflösung auswerten (ab hohe Qual.) - nicht sicher
		if "_width" in video:							# Proben überschreiben
			w = stringextract('_width":', ',', video)
			h = stringextract('_height":', ',', video)
		if w and h:
			res = "%sx%s" % (w,h)
		else:
			res = u"Auflösung ?"
		
		PLog(bitrate); PLog(res); 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4 Qualität: %s ** Bitrate %s ** Auflösung %s ** %s" % (quality, bitrate, res, title_url)
		download_list.append(item)
	
	return download_list			
			
####################################################################################################
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
# 10.11.2019 Verzicht auf Abgleich Button/Webseite (Performance, lange Ladezeit).
# 28.05.2020 ARD-Änderungen - s. SendungenAZ_ARDnew
# 25.01.2021 Laden + Caching der Link-Übersicht, Laden der Zielseite in 
#	SendungenAZ_ARDnew
# 		
def SendungenAZ(name, ID):		
	PLog('SendungenAZ: ' + name)
	PLog(ID)
	
	CurSender = Dict("load", 'CurSender')			
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	title2 = name + ' | aktuell: %s' % sendername
	# no_cache = True für Dict-Aktualisierung erforderlich - Dict.Save() reicht nicht			 
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')						# Home-Button
		
	# Link-Übersicht laden:
	# azlist = list(string.ascii_uppercase)			# 25.01.2021 A-Z - nicht mehr benötigt
	# azlist.insert(0,u'#')	
	path = 'https://api.ardmediathek.de/page-gateway/pages/%s/editorial/experiment-a-z?embedded=false' % sender
	page = Dict("load", 'ARDnew_AZ_%s' %sender, CacheTime=ARDStartCacheTime)					
	if page == False:										# nicht vorhanden oder zu alt
		page, msg = get_page(path)		
		if page == '':	
			msg1 = u"Fehler in SendungenAZ: %s"	% name
			msg2 = msg
			MyDialog(msg1, msg2, '')	
			return li
		else:	
			Dict("store", 'ARDnew_AZ_%s' %sender, page) 	# Seite -> Cache: aktualisieren	
	
	# Buchstabenblock: "title":"#","href":"https://api...
	pat = '"urlId":'									# Link-Blöcke (title":" 2x enth.)
	gridlist = blockextract(pat, page)	
	PLog('pat: %s, gridlist: %d' % (pat, len(gridlist)))			
	if len(gridlist) == 0:				
		msg1 = u'Keine Beiträge gefunden zu %s' % button	
		MyDialog(msg1, '', '')					
		return li	
							
	for grid in gridlist:
		tag=''
		button = stringextract('title":"', '"', grid)
		#if button == 'Z':	# Debug
		#	PLog(grid)
		if ' A-Z' in button:								# Gesamtlink
			continue
			
		title = "Sendungen mit " + button
		anz = stringextract('totalElements":', '}', grid)
		#if anz:											# falsch bei den Senderseiten
		#	tag = u"Beiträge: %s" % anz
		href = stringextract('href":"', '"', grid)
		summ = u'Gezeigt wird der Inhalt für %s' % sendername
		
		PLog('Satz1:');
		PLog(button); PLog(anz); PLog(href); 
		href=py2_encode(href); title=py2_encode(title); 	
		fparams="&fparams={'title': '%s', 'button': '%s', 'href': '%s'}" % (title, button, quote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ_ARDnew",\
			fanart=R(ICON_ARD_AZ), thumb=R(ICON_ARD_AZ), tagline=tag, fparams=fparams, summary=summ)																	
										
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
####################################################################################################
# Auflistung der A-Z-Buttons bereits in SendungenAZ einschl. Kennz. "Keine Inhalte".
#
# Weiterverarbeitung in ARDStartRubrik.
#
# 28.05.2020 ARD-Änderungen: 
#	Scroll-Mechanismus, Gruppen-Fallback + die bisherigen API-Calls entfallen.
#	Die kompl. Startseite wird auch nicht mehr benötigt, ist aber wie in ARDStart
#	erhältlich und enthält die gesamte Übersicht a-Z (ca. 2MByte).
#	Hier nutzen wir einen api-Call, jweils mit dem betref. Buchstaben 
#	Alternative: kompl. Startseite laden + ab window.__FETCHED_CONTEXT__ 
#				die Beitragstitel im json-Inhalt mit button abgleichen.
# 17.12.2020 Button '#' für ARD-Alle nicht mehr verfügbar - Umstellung
#	auf neuen api-Link (experiment-a-z). Die json-Seite enthält für den
#	gewählten Sender alle Beiträge A-Z, jeweils in Blöcken für einz.
#	Buchstaben.
#	Zusätzl. Cachenutzung (ARD_AZ_ard: 1,5 MByte)
# 25.01.2021 die grouping-Links funktionieren nicht mehr bei allen Beiträgen-
#	Umstellung auf "editorial"-Links (i.d.R. 2x vorh., Auswahl "embedded"),
#	Verzicht auf Laden + Caching der Gesamtseite, stattdessen in SendungenAZ
#	Laden der Link-Übersicht mit embedded-Zusatz und hier Laden der Zielseite
#
def SendungenAZ_ARDnew(title, button, href): 
	PLog('SendungenAZ_ARDnew:')
	PLog('button: ' + button); 
	title = title	
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	CurSender = Dict("load", 'CurSender')		
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)
	
	# der Link lädt die kompl. Beiträge A-Z, ausgewertet wird der passende Buchstabenblock
	# Alternative (vor V3.7.1): Link ohne Zusatz  lädt die kompl. Beiträge A-Z
	href = href.replace('&embedded=false', '')				# ohne entspr. Header nur leere Seite
	page, msg = get_page(href)		
	if page == '':	
		msg1 = u"Fehler in SendungenAZ_ARDnew: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
			
	gridlist = blockextract('"decor":', page)			# Beiträge im Block
	PLog(len(gridlist))
	if len(gridlist) == 0:				
		msg1 = u'Keine Beiträge gefunden zu %s' % button	
		MyDialog(msg1, '', '')					
		return li
			
	for s  in gridlist:
		href_list = blockextract('"href":"', s, '"')
		PLog(href_list); 
		for url in href_list:
			if 'embedded=true' in url:
				href = stringextract('"href":"', '"', url)
				break

		title 	= stringextract('"longTitle":"', '"', s)
		if title == '':
			title 	= stringextract('"mediumTitle":"', '"', s)					
		
		title 	= title.replace('- Standbild', '')	
		title	= unescape(title)
		if title.startswith('#') == False:
			title = repl_json_chars(title)
		img	= stringextract('"src":"', '"', s)		
		img = img.replace('{width}', '720')
		summ 	= stringextract('synopsis":"', '"', s)	
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		partner = stringextract('"partner":"', '"', s)
		tagline = "Sender: %s" % pubServ		
		PLog(az_sender); PLog(pubServ); PLog(partner);
		if pubServ  == '' and partner  == '':			# pubServ kann fehlen
			continue
				
		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					break		
			if filtered:
				# PLog('filtered: ' + title)
				continue		

		PLog('Satz2:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(tagline);
		ID = 'A-Z'
		summ = "%s\n\n%s" % (tagline, summ)
		href=py2_encode(href); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" % (quote(href), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams, summary=summ)	
			
	# 24.08.2019 Erweiterung auf pagination, bisher nur AutoCompilationWidget
	#	pagination mit Basispfad immer vorhanden, Mehr-Button abhängig von Anz. der Beiträge
	if 	'"pagination":'	in page:						# Scroll-Beiträge
		PLog('pagination_Rubrik:')
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		pages, pN, pageSize, totalElements, next_path = get_pagination(page)	# Basis 0
		mark=''		
		
		if next_path:	
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements)
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % str(pN)
			PLog(summ); PLog(next_path)
			
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s'}" % (quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDPagination", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
														

	xbmcplugin.endOfDirectory(HANDLE)	
#----------------------------------------------------------------

# Suche in beiden Mediatheken
#	Abruf jeweils der 1. Ergebnisseite
#	Ohne Ergebnis -> Button mit Rücksprung hierher
#	Ergebnis ZDF: -> ZDF_Search (erneuter Aufruf Seite 1, weitere Seiten dort rekursiv)
#		Ablage in Dict nicht erf., Kodi-Cache ausreichend.
# 22.08.2019 myhash und erste pageNumber geändert durch ARD (0, vorher 1) - dto. in ARDSearchnew
# 27.06.2020 api-Codeanteile entfernt - s. SearchARDnew
#
def SearchARDundZDFnew(title, query='', pagenr=''):
	PLog('SearchARDundZDFnew:');
	query_file 	= os.path.join(ADDON_DATA, "search_ardundzdf")
	
	if query == '':														# Liste letzte Sucheingaben
		query_recent= RLoad(query_file, abs_path=True)
		if query_recent.strip():
			search_list = ['neue Suche']
			query_recent= query_recent.strip().splitlines()
			query_recent=sorted(query_recent, key=str.lower)
			search_list = search_list + query_recent
			ret = xbmcgui.Dialog().select('Sucheingabe', search_list, preselect=0)
			if ret == -1:
				PLog("Liste Sucheingabe abgebrochen")
				return ardundzdf.Main()
			elif ret == 0:
				query = ''
			else:
				query = search_list[ret]
				query = "%s|%s" % (query,query)							# doppeln			
	
	if query == '':
		query = ardundzdf.get_query(channel='ARDundZDF') 
	if  query == None or query.strip() == '':
		# return li														# getting plugin Error
		return ardundzdf.Main()
		
	query=py2_encode(query)		# decode, falls erf. (1. Aufruf)
	PLog(query)
	query_ard = query.split('|')[0]
	query_zdf = query.split('|')[1]
	
	tag_negativ =u'neue Suche in ARD und ZDF starten'					# ohne Treffer
	tag_positiv =u'gefundene Beiträge zeigen'							# mit Treffer
	store_recents = False												# Sucheingabe nicht speichern
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)												# Home-Button
	
	#------------------------------------------------------------------	# Suche ARD
	sendername, sender, kanal, img, az_sender = ARDSender[0].split(':') # in allen Sendern
	sender = 'ard'
	pageNumber = 0
	
	query_lable = query_ard.replace('+', ' ')
	path = 'https://page.ardmediathek.de/page-gateway/widgets/%s/search/vod?searchString=%s&pageNumber=%s' % (sender, query_ard, pageNumber)
	page, msg = get_page(path,JsonPage=True)					
		
	vodTotal =  stringextract('"totalElements":', '}', page)	# Beiträge?
	gridlist = blockextract( '"mediumTitle":', page) 			# Sicherung
	vodTotal=py2_encode(vodTotal); query_lable=py2_encode(query_lable);
	PLog(query_ard)
	if len(gridlist) == 0 or vodTotal == '0':
		label = "ARD | nichts gefunden zu: %s | neue Suche" % query_lable
		title="Suche in ARD und ZDF"
		title=py2_encode(title); 
		fparams="&fparams={'title': '%s'}" % quote(title)
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		store_recents = True											# Sucheingabe speichern
		PLog(type(vodTotal)); 	PLog(type(query_lable)); 			
		title = "ARD: %s Video(s)  | %s" % (vodTotal, query_lable)
		query_ard=py2_encode(query_ard); title=py2_encode(title); 
		fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '0'}" %\
			(quote(query_ard), quote(title), sender)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
		
	#------------------------------------------------------------------	# Suche ZDF
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path_zdf = ZDF_Search_PATH % (quote(query_zdf), pagenr) 
	page, msg = get_page(path=path_zdf, do_safe=False)	
	searchResult = stringextract('data-loadmore-result-count="', '"', page)	# Anzahl Ergebnisse
	PLog(searchResult);
	query_lable = (query_zdf.replace('%252B', ' ').replace('+', ' ')) 	# quotiertes ersetzen 
	query_lable = unquote(query_lable)
	query_lable=py2_encode(query_lable); searchResult=py2_encode(searchResult);
	
	if searchResult == '0' or 'class="artdirect"' not in page:		# Sprung hierher
		label = "ZDF | nichts gefunden zu: %s | neue Suche" % query_lable
		title="Suche in ARD und ZDF"
		title=py2_encode(title);
		fparams="&fparams={'title': '%s'}" % quote(title)
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
	else:	
		store_recents = True											# Sucheingabe speichern
		title = "ZDF: %s Video(s)  | %s" % (searchResult, query_lable)
		query_zdf=py2_encode(query_zdf); title=py2_encode(title);
		fparams="&fparams={'query': '%s', 'title': '%s', 'pagenr': '%s'}" % (quote(query_zdf), 
			quote(title), pagenr)
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R('suche_ardundzdf.png'), 
			thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
					
	if 	store_recents:													# Sucheingabe speichern
		query_recent= RLoad(query_file, abs_path=True)
		query_recent= query_recent.strip().splitlines()
		if len(query_recent) >= 24:										# 1. Eintrag löschen (ältester)
			del query_recent[0]
		query_ard=py2_encode(query_ard)
		if query_ard not in query_recent:								# query_ard + query_zdf ident.
			query_recent.append(query_ard)
			query_recent = "\n".join(query_recent)
			query_recent = py2_encode(query_recent)
			RSave(query_file, query_recent)								# withcodec: code-error
			
	xbmcplugin.endOfDirectory(HANDLE)
	
#---------------------------------------------------------------- 
# Suche in Mediathek Neu 
# Statt des api-Calls funktioniert auch https://www.ardmediathek.de/ard/search/%s
# 	(Auswertung anpassen).
# Scrollbeiträge hier leicht abweichend von ARDStartRubrik (s.u. Mehr-Button).
# 22.08.2019 myhash (sha256Hash) und erste pageNumber geändert durch ARD (0, vorher 1)
#	Suche im Web vorangestellt (Webcheck): Check auf Sendungen /Mehrfachbeiträge) - Auswertung 
#		 in ARDStartRubrik, einschl. Scroll-Beiträge 
# Webcheck: abgeschaltet bei SearchARDundZDFnew (nur Einzelbeiträge, wie ZDF-Suche)
# Die Suchfunktion arbeitet nur mit Einzelworten, Zusammensetzung möglich z.B. G7-Gipfel
# 27.06.2020 die Web-Url "www.ardmediathek.de/ard/suche/.." funktioniert nicht mehr -
#	Webcheck entfällt, gesamte Suchfunktion jetzt script-gesteuert. api-Call ebenfalls 
#	geändert - das Zusammensetzen mit extensions + variables entfällt.  
#
def ARDSearchnew(title, sender, offset=0, query=''):
	PLog('ARDSearchnew:');	
	PLog(sender); PLog(offset); PLog(query);
	
	if sender == '':											# Sender gewählt?
		sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)
	
	if query == '':
		query = get_keyboard_input() 
		if query == None or query.strip() == '': # None bei Abbruch
			return
	query = query.strip()
	query = query.replace(' ', '+')	# Aufruf aus Merkliste unbehandelt	
	query_org = query	
	query=py2_decode(query)		# decode, falls erf. (1. Aufruf)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	# -----------------------------------------------------
	path = 'https://page.ardmediathek.de/page-gateway/widgets/%s/search/vod?searchString=%s&pageNumber=%s' % (sender, query, offset)
	page, msg = get_page(path,JsonPage=True)					
	PLog(len(page))
	if page == '':											
		msg1 = "Fehler in ARDSearchnew, Suche: %s"	% query
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	gridlist = blockextract( '"mediumTitle":', page) 		# Beiträge?
	if len(gridlist) == 0:				
		msg1 = u'keine Beiträge gefunden zu: %s'  % query
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)		
	PLog('gridlist: ' + str(len(gridlist)))	
	
	ID='Search' 	# mark für farbige Markierung
	li = get_page_content(li, page, ID, mark=unquote(query))																	
	
															# Mehr-Button:
	title = "Mehr zu >%s<" % unquote(query)		
	offset = int(offset) +1
	vodTotal	= stringextract('"totalElements":', '}', page)
	vodPageSize = stringextract('"pageSize":', ',', page)
	pages = float(vodTotal) / float(vodPageSize)
	pages = int(math.ceil(pages))					# aufrunden für Seitenrest

	summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (str(pages), vodTotal) 
	tag = "weiter zu Seite %s" % str(offset+1)				# Basis 0
	PLog("vodTotal %s, vodPageSize %s" % (vodTotal, vodPageSize))
	PLog("offset %s, pages %s" % (str(offset),str(pages)))
	if int(offset) < int(pages):	
		query=py2_encode(query); title=py2_encode(title); 
		fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '%s'}" %\
			(quote(query), quote(title), quote(sender), str(offset))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)																	
				
	xbmcplugin.endOfDirectory(HANDLE)

#---------------------------------------------------------------- 
# Verpasst Mediathek Neu - Liste Wochentage
# 29.05.2020 Änderung der Webseite durch die ARD. HTML steht nicht mehr
#	zur Verfügung, Ermittlung der timeline-Sender im Web entfällt.
#	Statt dessen forder wir mit dem gewählten Sender die entspr. 
#	json-Seite an. Verarbeitung in ARDVerpasstContent 	
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
		startDate = rdate.strftime("%Y-%m-%dT03:30:00.000Z")
		myDate  = rdate.strftime("%d.%m.")		# Formate s. man strftime (3)
		
		rdate2 = now - datetime.timedelta(days = nr-1)
		endDate = rdate2.strftime("%Y-%m-%dT03:29:59.000Z")

		iWeekday = rdate.strftime("%A")
		iWeekday = transl_wtag(iWeekday)
		iWeekday = iWeekday[:2].upper()
		if nr == 0:
			iWeekday = 'HEUTE'	
		if nr == 1:
			iWeekday = 'GESTERN'	
		title =	"%s %s" % (iWeekday, myDate)	# DI 09.04.
		tagline = "Sender: %s" % sendername	
		
		PLog(title); PLog(startDate); PLog(endDate)
		CurSender=py2_encode(CurSender); 
		fparams="&fparams={'title': '%s', 'startDate': '%s', 'endDate': '%s','CurSender': '%s'}" %\
			(title,  startDate, endDate, quote(CurSender))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasstContent", fanart=R(ICON_ARD_VERP), 
			thumb=R(ICON_ARD_VERP), fparams=fparams, tagline=tagline)
			
	title 	= u'Wählen Sie Ihren Sender | aktuell: [COLOR red]%s[/COLOR]' % sendername	# Senderwahl
	title=py2_encode(title); caller='resources.lib.ARDnew.ARDVerpasst'
	fparams="&fparams={'title': '%s', 'caller': '%s'}" % (quote(title), caller)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", fanart=R(ICON_MAIN_ARD), 
		thumb=R('tv-regional.png'), fparams=fparams) 
	
	
	xbmcplugin.endOfDirectory(HANDLE)

#---------------------------------------------------------------- 
# ARDVerpasstContent Mediathek Neu - Inhalt des gewählten Tages
#	Seite html (Uhrzeit, Titel, Link) / json (Blöcke "shortTitle") 
# Ablauf: 	1. Senderliste (Aufruf ohne timeline_sender od. /ard/ im Pfad)
#			2. Einzelsender (Aufruf mit timeline_sender)
# 28.08.2019 timeline_sender nicht mehr auf den Datumsseiten verfügbar,
#	nur noch auf der Einstiegsseite ../ard/program/
# 02.03.2020 wieder leere html-Seite bei Zusatz ?devicetype=pc (nur Heute),
#	geändert in ?devicetype=mobile. Header: vermutl. cache-control
#	entscheident (nicht geklärt).
# 29.05.2020 Änderung der Webseite durch die ARD - s. ARDVerpasst,
#	der 2-fache Durchlauf (Senderliste / Sendungen) entfällt
# 
def ARDVerpasstContent(title, startDate, endDate, CurSender):
	PLog('ARDVerpasstContent:');
	PLog(title);  PLog(startDate); PLog(endDate); PLog(CurSender);
	
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sendername); PLog(sender); 
	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')							# Home-Button

	base = "https://page.ardmediathek.de/page-gateway/compilations/ard/pastbroadcasts"
	base = base.replace('/ard/', '/%s/' % sender)
	path = base + "?startDateTime=%s&endDateTime=%s&pageNumber=0&pageSize=100" % (startDate, endDate)
	
	page, msg = get_page(path)
	if page == '':	
		msg1 = 'Fehler in ARDVerpasstContent'
		msg2=msg
		msg3=path
		MyDialog(msg1, msg2, msg3)	
		return li
	PLog(len(page))
									
	gridlist = blockextract( 'broadcastedOn', page) 
	if len(gridlist) == 0:				
		msg1 = u'keine Beiträge gefunden zu:'
		msg2 = '%s | %s'  % (title, sendername)
		PLog("%s | %s" % (msg1, msg2))
		MyDialog(msg1, msg2, '')
		return li
			
	PLog('gridlist: ' + str(len(gridlist)))	
	li = get_page_content(li, page, ID='EPG', mark='')
																	
	
	xbmcplugin.endOfDirectory(HANDLE)
	
#----------------------------------------------------------------
# convHour z.Z. nicht genutzt
#	string zeit, int offset - Bsp. 15:00, 2
# 	s.a. util.time_translate für ISO8601-Werte
#	21.11.2019 entfallen, ersetzt durch convHour
#		(Format durch ARD geändert)
# convHour - Format zeit: 2:10 PM od. 5:40 AM,
#	ohne Zeitversatz
def convHour(zeit):	
	PLog('convHour: ' + zeit);
	zeit, tz = zeit.split(' ')
	hour, minutes = zeit.split(':')

	if tz.strip() == 'PM':			# Nachmittagszeit
		hour = int(hour) + 12
		hour = str(hour)
		PLog(hour)
		PLog(type(hour));
		if hour == "24":
			hour = "00"	

	zeit = "%02s:%s" % (hour, minutes)
	PLog(zeit)
	return zeit

####################################################################################################
# Senderformat Sendername:Sender (Pfadbestandteil):Kanal:Icon
#	Bsp.: 'ARD-Alle:ard::ard-mediathek.png', Rest s. ARDSender[]
# caller ARDVerpasst, sonst Main_NEW
# 		
def Senderwahl(title, caller=''):	
	PLog('Senderwahl:'); PLog(caller)
	
	PLog(SETTINGS.getSetting('pref_disable_sender'))	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')							# Home-Button
	
	if caller == '':
		caller = "resources.lib.ARDnew.Main_NEW"
	
	for entry in ARDSender:								# entry -> CurSender in Main_ARD
		if 'KiKA' in entry:								# bisher nicht in Base- und AZ-URL enthalten
			continue
		sendername, sender, kanal, img, az_sender = entry.split(':')
		PLog(entry)
		tagline = 'Mediathek des Senders [COLOR red] %s [/COLOR]' % sendername
		PLog('sendername: %s, sender: %s, kanal: %s, img: %s, az_sender: %s'	% (sendername, sender, kanal, img, az_sender))
		if SETTINGS.getSetting('pref_disable_sender') == 'true':
			title = '%s' % sendername
		else:
			title = 'Sender: %s' % sendername
		entry=py2_encode(entry); 			
		if 'ARDVerpasst' in caller:
			fparams="&fparams={'title': 'Sendung verpasst', 'CurSender': '%s'}" % quote(entry)
		else:	
			fparams="&fparams={'name': 'ARD Mediathek', 'CurSender': '%s'}" % quote(entry)
		addDir(li=li, label=title, action="dirList", dirID="%s" % caller, fanart=R(img), thumb=R(img), 
			tagline=tagline, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
		

