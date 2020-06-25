# -*- coding: utf-8 -*-
################################################################################
#				ARD_NEW.py - Teil von Kodi-Addon-ARDundZDF
#			neue Version der ARD Mediathek, Start Beta Sept. 2018
#
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.ardmediathek.de/,
#	Seiten werden im json-Format, teilweise html + json ausgeliefert
#	04.11.2019 Migration Python3
#	21.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#
################################################################################
#	Stand 25.06.2020

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
	'BR:br:2224:tv-br.png:BR Fernsehen', 'MDR:mdr:1386804:tv-mdr-sachsen.png:MDR Fernsehen', 
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

DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA

# Ort FILTER_SET wie filterfile (check_DataStores):
FILTER_SET 	= os.path.join("%s/filter_set") % ADDON_DATA
AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()					# gesetzte Filter initialiseren 

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
		
	title = 'Start'	
	tag = 'Sender: [COLOR red] %s [/COLOR]' % sendername
	title=py2_encode(title);
	fparams="&fparams={'title': '%s', 'sender': '%s'}" % (quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", fanart=R(ICON_MAIN_ARD), thumb=R(img), 
		tagline=tag, fparams=fparams)

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
	
	if '__PRELOADED_STATE__ ' not in page:						# Fallback: Cache ohne CacheTime
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
	# RSave('/tmp/x.html', page, withcodec=True) 			# Debug
	
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
			tag = u"%s Beiträge" % anz
		img		= stringextract('"src":"', '"', cont)		# Bild 1. Beitrag, Bsp.: ..r.jpg?w={width}
		img 	= img.replace('{width}', '720')
		if img  == '':
			img = R(ICON_DIR_FOLDER)
		path 	= stringextract('"href":"', '"', cont)
		
		if 'Livestream' in title or up_low('Live') in up_low(title):
			ID = 'Livestream'
		else:
			ID = 'ARDStart'			
		
		PLog('Satz_cont:');
		PLog(title); PLog(ID); PLog(anz); PLog(img); 
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
			(quote(path), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			tagline=tag, fparams=fparams)
			

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

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
#
# Aufrufe: Rubriken aus ARDStart, Sendereihen aus A-Z-Seiten, Mehrfachbeiträge aus ARDSearchnew
# 28.05.2020 getrennte Swiper-Auswertung entfällt nach Änderung der ARD-Seiten
#		
def ARDStartRubrik(path, title, widgetID='', ID='', img=''): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title); PLog(path)	
	title_org = title
			
	CurSender = Dict("load", 'CurSender')			
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')							# Home-Button

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
	page = page.replace('\\"', '*')						# quotiere Marks entf.

	mehrfach=False; mediatype=''
	if 'Livestream' in ID:
		gridlist = blockextract('"broadcastedOn"', page)
			
	mark=''
	if ID == 'Search_Webcheck':
		mark = title
	li = get_page_content(li, page, ID, mark)			# Auswertung Rubriken																	
	
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
# Alternative: api-Call via get_api_call (für compilationId vorbereitet,
#	 myhash=0aa6f77b1d2400b94b9f92e6dbd0fabf652903ecf7c9e74d1367458d079f0810).
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
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	
	
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
	
#---------------------------------------------------------------------------------------------------
# Auswertung für ARDStartRubrik + ARDPagination + ARDSearchnew 
#	Mehrfach- und Einzelsätze
# mark: farbige Markierung in title (z.B. query aus ARDSearchnew) 
# Seiten sind hier bereits senderspezifisch.
# Aufrufe Direktsprünge
#	
def get_page_content(li, page, ID, mark=''): 
	PLog('get_page_content: ' + ID); PLog(mark)
	
	CurSender = Dict("load", 'CurSender')					# Debug, Seite bereits senderspez.
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)												#-> href
	
	mediatype=''; pagetitle=''
	pagination	= stringextract('pagination":', '"type"', page)
	pagetitle 	= stringextract('title":"', '"', pagination)
	PLog(pagetitle)
	page = page.replace('\\', '')								# Quotierung vor " entfernen, Bsp. \"query\"
	
	
	if 'Livestream' in ID or 'EPG' in ID:
		gridlist = blockextract('"broadcastedOn"', page)
	else:
		if  ID == 'Search_api':									# Search_api immer Einzelbeiträge
			mehrfach = False
			gridlist = blockextract( '"ondemand"', page)				
		else:
			if 'target":{"id":"' in page:
				gridlist = blockextract('"availableTo"', page)	# Sendungen, json-key "teasers"	
			else:
				gridlist = blockextract('id":"Link:', page)		# deckt auch Serien in Swiper ab
					
		if 'ARDStart' in ID:									# zusätzl. Beiträge ganz links
			decorlist = blockextract( '{"decor":', page)
			PLog('decorlist: ' + str(len(decorlist)))
			gridlist = decorlist + gridlist
			
		if len(gridlist) == 0:									# Fallback (außer Livestreams)
			gridlist = blockextract( '"images":', page) 		# geändert 20.09.2019 
							
		
	if len(gridlist) == 0:				
		msg1 = 'keine Beiträge gefunden'
		PLog(msg1)
		MyDialog(msg1, '', '')	
	PLog('gridlist: ' + str(len(gridlist)))	

	for s  in gridlist:
		PLog("Mark10")
		if 'EPG' not in ID:								# decor im 1. Drittel
			pos = s.find('"decor"',100)							# möglich: Block reicht in Folgeblock
			if pos > 100:										# eigenes decor zw. broadcastedOn + duration
				s = s[:pos]
		
		mehrfach = True											# Default weitere Rubriken
		if 'target":{"id":"' in s:
			targetID= stringextract('target":{"id":"', '"', s)	# targetID
		else:
			targetID= stringextract('id":"Link:', '"', s)		# Serie in Swiper via ARDStartSingle 
		if ID == 'Search_api':
			target 	= stringextract('target":{"href":"', '"', s)
			targetID = target.split('/')[-1]
		PLog(targetID)
		if targetID == '':										# kein Video
			continue			

		PLog('"availableTo":null' in s)							# kein Einzelbetrag
		if '"availableTo":"' in s or '"duration":' in s or 'Livestream' in ID:	# Einzelbetrag
			if not '"availableTo":null' in s:					# u.a. Bsp. "show":null 
				mehrfach = False
		if '/compilation/' in s or '/grouping/' in s:			# Serie Vorrang vor z.B. Teaser 
			mehrfach = True
		if ID == 'EPG':
			mehrfach = False
					
		
		if mehrfach == True:									# Pfad für Mehrfachbeiträge ermitteln 						
			url_parts = ['/grouping/', '/compilation/']
			hreflist = blockextract('"href":"', s)
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

		if mark:
			PLog(title); PLog(mark)
			title = title.strip() 
			title = make_mark(mark, title, "red")	# farbige Markierung
	
		img 	= stringextract('src":"', '"', s)	
		img 	= img.replace('{width}', '640'); 
		img= img.replace('u002F', '/')
		summ 	= stringextract('synopsis":"', '"', s)	
			
		duration = stringextract('"duration":', ',', s)			# Sekunden
		duration = seconds_translate(duration)
		if duration :						# für Staffeln nicht geeignet
			duration = 'Dauer %s' % duration
		maturitytRating = stringextract('maturityContentRating":"', '"', page) # "FSK16"
		PLog('maturitytRating: ' + maturitytRating)				# außerhalb Block!
		if 	maturitytRating:
			duration = u"%s | %s" % (duration, maturitytRating)	
			
		tag = duration	
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		# Filterung nach Sendern entfällt - s.o.
		#if sender != 'ard':							# Alle (ard) oder filtern
		#	if sender not in pubServ.lower():
		#		continue		
		
		broadcast = stringextract('"broadcastedOn":"', '"', s)	# Sendedatum
		PLog(broadcast)
		if broadcast and ID != 'Livestream':					# enth. unsinnige Werte
			broadcast = time_translate(broadcast)				#  + 2 Std.
			tag = u"%s\nSendedatum: [COLOR blue]%s Uhr[/COLOR]" % (tag, broadcast)
			
		availableTo = stringextract('"availableTo":"', '"', s)	# availableTo
		PLog(availableTo)
		if availableTo:											# möglich: availableTo":null
			availableTo = time_translate(availableTo)
			tag = u"%s\n\n[B]Verfügbar bis: [COLOR darkgoldenrod]%s[/COLOR][/B]" % (tag, availableTo)
		
		if pubServ:
			tag = u"%s\nSender: %s" % (tag, pubServ)

		title = repl_json_chars(title); summ = repl_json_chars(summ); 
		
		PLog('Satz:');
		PLog(mehrfach); PLog(title); PLog(href); PLog(img); PLog(summ); PLog(duration); PLog(ID)
		
		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					continue		
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
				# skip availableTo + (hier in tag)
				summ_new = get_summary_pre(path=href, ID='ARDnew', skip_verf=True, skip_pubDate=True) 
				if 	summ_new:
					summ = summ_new
			
			href=py2_encode(href); title=py2_encode(title); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'duration': '%s', 'ID': '%s'}" %\
				(quote(href), quote(title), duration, ID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)	
	
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
# 28.05.2020 Stream-Bezeichner durch ARD geändert
#
def ARDStartSingle(path, title, duration, ID=''): 
	PLog('ARDStartSingle: %s' % ID);
	title_org 	= title 
	
	page, msg = get_page(path)
	if page == '':	
		msg1 = "Fehler in ARDStartRubrik: %s"	% title
		msg2=msg
		MyDialog(msg1, msg2, '')	
		xbmcplugin.endOfDirectory(HANDLE)
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Pyton3 geändert

	elements = blockextract('availableTo":', page)			# möglich: Mehrfachbeiträge? z.B. + Hörfassung
	if len(elements) > 1:
		if '_quality"' not in page:							# bei Streamlinks bleiben wir hier
			PLog('%s Elemente -> ARDStartRubrik' % str(len(elements)))
			return ARDStartRubrik(path,title,ID='ARDStartSingle')
			
	if len(elements) == 0:									# möglich: keine Video (dto. Web)
		msg1 = 'keine Beiträge zu %s gefunden'  % title
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)	
	PLog('elements: ' + str(len(elements)))	
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	summ 		= stringextract('synopsis":"', '"', page)		# mit verfügbar wie	get_summary_pre
	verf=''
	if u'verfügbar bis:' in page:								# html mit Uhrzeit									
		verf = stringextract(u'verfügbar bis:', '</p>', page)	
		verf = cleanhtml(verf)
	if verf:													# Verfügbar voranstellen
		summ = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s" % (verf, summ)
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
		return ardundzdf.SenderLiveResolution(path=href, title=title, thumb=img, descr=summ, Startsender='true')
	
	mediatype='							'# Kennz. Video für Sofortstart 
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'
	
	summ = repl_json_chars(summ)
	summ_lable = summ
	summ = summ.replace('\n','||')

	if duration == None or duration.strip() == '':
		duration = stringextract('_duration":', ',', page)	# Sekunden
		duration = 'Dauer %s' % seconds_translate(duration)	
	tagline = duration
	# tagline=transl_doubleUTF8(tagline)		# Bsp. â<U+0088><U+0099> (a mit Circumflex)
	
	PLog('Satz:')
	PLog(title); PLog(summ[:60]); PLog(tagline); PLog(img); PLog(path); PLog(sub_path);
	title_new 	= u"[COLOR blue]Streaming-Formate[/COLOR] | " + title
	title_new=repl_json_chars(title_new); summ=repl_json_chars(summ); 
		
	path=py2_encode(path); title=py2_encode(title); summ=py2_encode(summ); tagline=py2_encode(tagline);
	img=py2_encode(img); geoblock=py2_encode(geoblock); sub_path=py2_encode(sub_path);
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'tagline': '%s', 'img': '%s', 'geoblock': '%s', 'sub_path': '%s'}" \
		% (quote(path), quote(title), quote(summ), quote(tagline), quote(img), quote(geoblock), quote(sub_path))
	addDir(li=li, label=title_new, action="dirList", dirID="resources.lib.ARDnew.ARDStartVideoStreams", fanart=img, thumb=img, 
		fparams=fparams, summary=summ_lable, tagline=tagline, mediatype=mediatype)		
					
	if SETTINGS.getSetting('pref_use_downloads'):	
		title_new = "[COLOR blue]MP4-Formate und Downloads[/COLOR] | " + title
	else:	
		title_new = "[COLOR blue]MP4-Formate[/COLOR] | " + title
	path=py2_encode(path); title=py2_encode(title); summ=py2_encode(summ); tagline=py2_encode(tagline);
	img=py2_encode(img); geoblock=py2_encode(geoblock); sub_path=py2_encode(sub_path);
	fparams="&fparams={'path': '%s', 'title': '%s', 'summ': '%s', 'tagline': '%s',  'img': '%s', 'geoblock': '%s', 'sub_path': '%s'}" \
		% (quote(path), quote(title), quote(summ), quote(tagline), quote(img), quote(geoblock), quote(sub_path))
	addDir(li=li, label=title_new, action="dirList", dirID="resources.lib.ARDnew.ARDStartVideoMP4", fanart=img, thumb=img, 
		fparams=fparams, summary=summ_lable, tagline=tagline, mediatype=mediatype)	
	
	gridlist=''	
	# zusätzl. Videos zur Sendung (z.B. Clips zu einz. Nachrichten). gridlist enthält 
	#	die Links zu den Sendungen
	if 	ID == 'mehrzS':											# nicht nochmal "mehr" zeigen
		xbmcplugin.endOfDirectory(HANDLE)	
	if 	'>Mehr aus der Sendung<' in page: 						# z.B. in Verpasst-Seiten
		gridlist = blockextract( 'class="_focusable', page) 	# HTML-Bereich
	#if len(gridlist) == 0:										# Alternative - meist identisch,
	#	gridlist = blockextract( 'class="button _focusable"', page)	# kann aber Senderlsite enthalten 
	if len(gridlist) > 0:
		PLog('gridlist_more: ' + str(len(gridlist)))	
		li = get_ardsingle_more(li,gridlist,page)				# mediatype=video hier vermeiden			
					
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
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

		title = stringextract('aria-label="', '"', s) 
		title = unescape(title)	
		title = repl_json_chars(title)		
		title	= u"Mehr: " + title
		
		tag = stringextract('class="subline">', '</h4>', s)
		tag = cleanhtml(tag) 		        
		img, sender = img_via_id(href_id, page)
		if 'duration' in s:
			duration = stringextract('class="duration">', '<', s)
			summ = 	"%s | Mehr aus der Sendung " % duration

		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); 

		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					continue		
			if filtered:
				# PLog('filtered: ' + title)
				continue		
		 								 
		href=py2_encode(href); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'duration': ' ', 'ID': 'mehrzS'}" %\
			(quote(href), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, summary=summ,  tagline=tag, mediatype=mediatype)	
																			
	return li
		
#---------------------------------------------------------------------------------------------------
#	Wiedergabe eines Videos aus ARDStart, hier Streaming-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
#	HTML-Seite mit json-Inhalt
#	28.05.2020 nur noch json-Seite, Stream-Bezeichner durch ARD geändert
def ARDStartVideoStreams(title, path, summ, tagline, img, geoblock, sub_path='', Merk='false'): 
	PLog('ARDStartVideoStreams:'); 
	
	title_org = title	
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoStreams: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Pyton3 geändert
	
	href = ''; VideoUrls = []
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	if len(Plugins) > 0:
		Plugin1	= Plugins[0]							
		VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))
	
	if len(VideoUrls) > 0:									# nur 1 m3u8-Link möglich
		for video in  VideoUrls:							#	bei Jugemdschutz ges.
			# PLog(video)
			if '"auto"' in video:
				href = stringextract('stream":"', '"', video)	# Video-Url
				quality = u'Qualität: automatische'
				PLog(quality); PLog(href)	 
				break
	else:
		href = stringextract('assetid":"', '"', page)

	if 'master.m3u8' not in href:							# möglich: ../master.m3u8?__b__=200
		msg = 'keine Streamingquelle gefunden - Abbruch' 	# auch möglich: nur .mp3-Quelle
		PLog(msg)
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		MyDialog(msg1, '', '')	
		return li
	if href.startswith('http') == False:
		href = 'http:' + href
	href = href.replace('https', 'http')					# Plex: https: crossdomain access denied
		
	lable = u'Bandbreite und Auflösung automatisch ' 		# master.m3u8
	lable = lable + geoblock
	
	Plot = "%s||||%s" % (tagline, summ)					# || Code für LF (\n scheitert in router)
	if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: ARDStartVideoStreams')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot, sub_path=sub_path, Merk=Merk)
		return
		
		
	title=repl_json_chars(title); title_org=repl_json_chars(title_org); lable=repl_json_chars(lable); 
	summ=repl_json_chars(summ); tagline=repl_json_chars(tagline); 
	summ_lable = summ.replace('||', '\n')
	
	href=py2_encode(href); title_org=py2_encode(title_org);  img=py2_encode(img);
	Plot=py2_encode(Plot); sub_path=py2_encode(sub_path); 
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s', 'Merk': '%s'}" %\
		(quote_plus(href), quote_plus(title_org), quote_plus(img), quote_plus(Plot), 
		quote_plus(sub_path), quote_plus(Merk))
	addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
		mediatype='video', tagline=tagline, summary=summ_lable) 
	
	li = ardundzdf.Parseplaylist(li, href, img, geoblock, descr=Plot, sub_path=sub_path)	# einzelne Auflösungen 		
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#---------------------------------------------------------------------------------------------------
#	Wiedergabe eines Videos aus ARDStart, hier MP4-Formate
#	Die Live-Funktion ist völlig getrennt von der Funktion TV-Livestreams - ohne EPG, ohne Private..
#	28.05.2020 nur noch json-Seite, Stream-Bezeichner durch ARD geändert (_plugin fehlt)
#
def ARDStartVideoMP4(title, path, summ, tagline, img, geoblock, sub_path='', Merk='false'): 
	PLog('ARDStartVideoMP4:'); 
	title_org=title; summary_org=summ; thumb=img; tagline_org=tagline	# Backup 

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button
	
	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDStartVideoMP4: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Pyton3 geändert
	
	Plugins = blockextract('_plugin', page)	# wir verwenden nur Plugin1 (s.o.)
	if len(Plugins) == 0:
		msg1 = "keine .mp4-Quelle gefunden zu: %s" % title_org
		MyDialog(msg1, '', '')	
		return li
	Plugin1	= Plugins[0]							
	VideoUrls = blockextract('_quality', Plugin1)
	PLog(len(VideoUrls))

	# Format Downloadliste "Qualität: niedrige | Titel#https://pdvideosdaserste.."
	download_list = ARDStartVideoMP4get(title,VideoUrls)	# holt Downloadliste mit mp4-videos
	PLog(len(download_list))
	PLog(download_list[:1])									# 1. Element
	
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
		PLog(href); PLog(quality); PLog(tagline); PLog(summary_org); 

		summ_lable = summary_org.replace('||', '\n')		
		Plot = "%s||||%s" % (tagline, summary_org)				# || Code für LF (\n scheitert in router)
		
		sub_path=''# fehlt noch bei ARD
		href=py2_encode(href); title_org=py2_encode(title_org);  img=py2_encode(img);
		Plot=py2_encode(Plot); sub_path=py2_encode(sub_path); 
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '%s'}" %\
			(quote_plus(href), quote_plus(title_org), quote_plus(img), 
			quote_plus(Plot), quote_plus(sub_path))
		addDir(li=li, label=lable, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
			mediatype='video', tagline=tagline, summary=summ_lable) 
		
	if download_list:	
		PLog(title_org);PLog(summary_org);PLog(tagline);PLog(thumb);
		li = ardundzdf.test_downloads(li,download_list,title_org,summary_org,tagline,thumb,high=-1)  # Downloadbutton(s)		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------------------------
# 28.05.2020 json-Formate durch ARD geändert
#
def ARDStartVideoMP4get(title, VideoUrls):	# holt Downloadliste mit mp4-videos für ARDStartVideoMP4
	PLog('ARDStartVideoMP4get:'); 
			
	href = ''
	download_list = []		# 2-teilige Liste für Download: 'title # url'
	Format = 'Video-Format: MP4'
	for video in  VideoUrls:
		
		PLog(video)
		href = stringextract('stream":"', '"', video)	# Video-Url
		if href == '' or href.endswith('mp4') == False:
			continue
		if href.startswith('http') == False:
			href = 'http:' + href
		q = stringextract('_quality":', ',', video)	# Qualität (Bez. wie Original)
		if q == '0':
			quality = u'Qualität: niedrige'
		if q == '1':
			quality = u'Qualität: mittlere'
		if q == '2':
			quality = u'Qualität: hohe'
		if q == '3':
			quality = u'Qualität: sehr hohe'
		
		PLog(quality)
		download_title = "%s | %s" % (quality, title)	# download_list stellt "Download Video" voran 
		download_list.append(download_title + '#' + href)	
	return download_list			
	
####################################################################################################
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
# 10.11.2019 Verzicht auf Abgleich Button/Webseite (Performance, lange Ladezeit).
# 28.05.2020 ARD-Änderungen - s. SendungenAZ_ARDnew
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
	li = home(li, ID='ARD Neu')								# Home-Button
		
	azlist = list(string.ascii_uppercase)				# A - Z
																
	azlist.insert(0,'#')							# früher 0-9	
	for button in azlist:	
		# PLog(button)
		title = "Sendungen mit " + button
		summ = u'Gezeigt wird der Inhalt für %s' % sendername
		fparams="&fparams={'title': '%s', 'button': '%s'}" % (title, button)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ_ARDnew", fanart=R(ICON_ARD_AZ), 
			thumb=R(ICON_ARD_AZ), fparams=fparams, summary=summ)																	
										
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
#		

def SendungenAZ_ARDnew(title, button): 
	PLog('SendungenAZ_ARDnew:')
	PLog('button: ' + button); 
	title = title	
	title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')								# Home-Button

	CurSender = Dict("load", 'CurSender')		
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
	
	base = "https://page.ardmediathek.de/page-gateway/compilations/%s/shows/" % sender
	path = base + "%s?pageNumber=0&pageSize=200&embedded=true" % button
	path = path.replace('#', '%23')						# quote
	page, msg = get_page(path)		
	if page == '':	
		msg1 = "Fehler in SendungenAZ_ARDnew: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	
	gridlist = blockextract( '"images":', page)			# Beiträge? 
	PLog('gridlist: ' + str(len(gridlist)))			
	if len(gridlist) == 0:				
		msg1 = 'Keine Beiträge gefunden zu %s' % button	
		MyDialog(msg1, '', '')					
		return li
			
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
			title 	= stringextract('"mediumTitle":"', '"', s)					
		
		title 	= title.replace('- Standbild', '')	
		title	= unescape(title)
		if title.startswith('#') == False:
			title = repl_json_chars(title)
		img	= stringextract('"src":"', '"', s)		
		img = img.replace('{width}', '720')
		summ 	= stringextract('synopsis":"', '"', s)	
		pubServ = stringextract('"name":"', '"', s)		# publicationService (Sender)
		tagline = "Sender: %s" % pubServ		
		PLog(az_sender); PLog(pubServ)
		if sender != 'ard':								# Alle (ard) oder filtern
			if az_sender != pubServ:
				continue
				
		if SETTINGS.getSetting('pref_usefilter') == 'true':			# Filter
			filtered=False
			for item in AKT_FILTER: 
				if up_low(item) in py2_encode(up_low(s)):
					filtered = True
					continue		
			if filtered:
				# PLog('filtered: ' + title)
				continue		

		PLog('Satz:');
		PLog(title); PLog(href); PLog(img); PLog(summ); PLog(tagline);
		summ = "%s\n\n%s" % (tagline, summ)
		href=py2_encode(href); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" % (quote(href), quote(title), 'A-Z')
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
			fparams=fparams, summary=summ)													

	xbmcplugin.endOfDirectory(HANDLE)


#-----------------------
# get_api_call erstellt API-Call für ARD A-Z, ARDSearchnew + ev. weitere Funkt.
#	Werte pageNumber, version als json-int einfügen.
#	22.08.2019 Reihenfolge pageNumber + text durch ARD geändert
def get_api_call(function, sender, myhash, pageNumber='', text='', clipId='', deviceType=''):
	PLog('get_api_call:');

	url_api 	= 'https://api.ardmediathek.de/public-gateway'
	variables 	= '{"client":"%s"}'	% sender
	
	if text:													# ARDSearchnew
		variables = '{"client":"%s","text":"%s","pageNumber":%s}'	% (sender, text, str(pageNumber))
		
	if clipId and deviceType:									# Einzelbeitrag (statt player-Url)
		variables = '{"client":"%s", "clipId":"%s","deviceType":"%s"}'	% (sender, clipId, deviceType)
			
	extensions	= '{"persistedQuery":{"version":1,"sha256Hash":"%s"}}' % myhash
	variables =  quote_plus(py2_encode(variables))                   	# & nicht codieren!
	extensions =  quote_plus(py2_encode(extensions))                	# & nicht codieren!
	url_api 	= "%s?variables=%s&extensions=%s"  % (url_api, variables, extensions)
	PLog('url_api %s: %s' % (function, url_api))
	PLog(variables)
	PLog(extensions)

	return url_api
	
#---------------------------------------------------------------- 
# Suche in beiden Mediatheken
#	Abruf jeweils der 1. Ergebnisseite
#	Ohne Ergebnis -> Button mit Rücksprung hierher
#	Ergebnis ZDF: -> ZDF_Search (erneuter Aufruf Seite 1, weitere Seiten dort rekursiv)
#		Ablage in Dict nicht erf., Kodi-Cache ausreichend.
# 22.08.2019 myhash und erste pageNumber geändert durch ARD (0, vorher 1) - dto. in ARDSearchnew
#
def SearchARDundZDFnew(title, query='', pagenr=''):
	PLog('SearchARDundZDFnew:');
	query_file 	= os.path.join("%s/search_ardundzdf") % ADDON_DATA
	
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
	# myhash vormals: ebd79f9a91c559ec31363f2b6448fb489ddf4742c1ca911d3c16391e72d6bb18
	myhash = '21f3cba7082cc35a5b7ce1c7901e46dbe7092c8c11d1e1a11d932fab55705fc1'  	# Chrome-Dev.-Tools
	url_api	= get_api_call('ARDSearchnew', 'ard', myhash, pageNumber, text=query_ard) 
	
	query_lable = query_ard.replace('+', ' ')
	page, msg = get_page(path=url_api)	
		
	vodTotal	= stringextract('"vodTotal":', ',', page)		# Beiträge?
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
		fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '0', 'Webcheck': 'False'}" %\
			(quote(query_ard), quote(title), sender)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
			fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
		
	#------------------------------------------------------------------	# Suche ZDF
	ZDF_Search_PATH	 = 'https://www.zdf.de/suche?q=%s&from=&to=&sender=alle+Sender&attrs=&contentTypes=episode&sortBy=date&page=%s'
	if pagenr == '':		# erster Aufruf muss '' sein
		pagenr = 1
	path_zdf = ZDF_Search_PATH % (quote(query_zdf), pagenr) 
	page, msg = get_page(path=path_zdf)	
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
#
def ARDSearchnew(title, sender, offset=0, query='', Webcheck=True):
	PLog('ARDSearchnew:');	
	PLog(sender); PLog(offset); PLog(query); PLog(Webcheck);
	
	if sender == '':											# Vorwahl vorhanden?
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
	# Check auf Sendereihe (Mehrfachbeiträge):
	if Webcheck:													# abgeschaltet bei SearchARDundZDFnew
		# path = BETA_BASE_URL + "/ard/search/%s" % query			# Suche im Web: alle Sender
		path = BETA_BASE_URL + "/%s/search/%s" % (sender, query)	# Suche im Web: gewählter Sender
		page, msg = get_page(path)					
		PLog(len(page))
		if page == '':											# ohne Dialog weiter mit api-Call
			PLog("ARDSearchnew (Webcheck) %s: error  get_page" % query)
		else:
			gridlist = blockextract( 'class="_focusable', page) # Sendungen im html-Teil
			if len(gridlist) > 0:
				for s  in gridlist:
					href  = stringextract('href="', '"', s)	
					#if href.startswith('http') == False:		# entf. hier
					#	href = BETA_BASE_URL + href
					title 	= stringextract('aria-label="', '"', s)
					title	= unescape(title)
					href_id =  stringextract('/shows/', '/', s) # Bild via id 
					img, pubServ = img_via_id(href_id, page)	# pubServ sollte sender entsprechen
					img=img.replace('\\u002F', '/')				# 23.11.2019: Ersetzung für Pyton3 geändert
					
					if pubServ:
						summ = "Sendungen | %s" % pubServ
					# grouping-path wie SendungenAZ_ARDnew
					href = 'http://page.ardmediathek.de/page-gateway/pages/%s/grouping/%s'  % (sender, href_id)
							
					PLog('Satz_Webcheck:')
					PLog(title); PLog(href);
					href=py2_encode(href); title=py2_encode(title); 
					fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" % (quote(href), 
						quote(title), 'Search_Webcheck')	# ID  sorgt für farbige Markierung von title
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
						fparams=fparams, summary=summ)																			
				xbmcplugin.endOfDirectory(HANDLE)				# raus, Einzelbeiträge verwerfen
			else:
				PLog("ARDSearchnew (Webcheck) %s: nichts gefunden, api-Suche folgt" % query)	
	
	# -----------------------------------------------------	# Einzelbeiträge mit api-Call suchen	
	pageNumber=str(offset)
	# myhash vormals: ebd79f9a91c559ec31363f2b6448fb489ddf4742c1ca911d3c16391e72d6bb18
	myhash = '21f3cba7082cc35a5b7ce1c7901e46dbe7092c8c11d1e1a11d932fab55705fc1'  		# Chrome-Dev.-Tools
	# url_api	= get_api_call('ARDSearchnew', 'ard', myhash, pageNumber, text=query) 	# alle Sender
	url_api	= get_api_call('ARDSearchnew', sender, myhash, pageNumber, text=query) 		# gewählter Sender

	page, msg = get_page(url_api)					
	page = page.replace('\\"', '*')							# quotiere Marks entf.
	if page == '':	
		msg1 = "Fehler in ARDSearchnew, Suche: %s"	% query
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))
	

	gridlist = blockextract( '"mediumTitle":', page) 		# Beiträge?
	if len(gridlist) == 0:				
		msg1 = u'keine Beiträge gefunden zu: %s'  % query
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)		
	PLog('gridlist: ' + str(len(gridlist)))	
	
	ID='Search_api' 	# mark für farbige Markierung
	li = get_page_content(li, page, ID, mark=unquote(query))																	
	
	# Mehr-Button - Scroll-Beiträge nicht vergleichbar mit ARDStartRubrik, keine
	#	pagination- oder AutoCompilationWidget-Markierung:
	# Bsp.: völklingen (69 Beiträge)
	title = "Mehr zu >%s<" % unquote(query)		
	offset = int(offset) +1
	# die Werte in vodTotal + vodPageSize stimmen nicht mit Anzahl der
	#	Beiträge überein.
	vodTotal	= stringextract('"vodTotal":', ',', page)
	vodPageSize = stringextract('"vodPageSize":', ',', page)
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
#	startDate = startDate.replace(':', '%3A'); endDate = endDate.replace(':', '%3A'); # quote ':'  # s. get_page
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
#	Offset für ARDVerpasstContent - aktuell 2 Stunden
#	string zeit, int offset - Bsp. 15:00, 2
# 	s.a. util.time_translate für ISO8601-Werte
#	21.11.2019 entfallen, ersetzt durch convHour
#		(Format durch ARD geändert)
# def addHour(zeit, offset):
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
		

