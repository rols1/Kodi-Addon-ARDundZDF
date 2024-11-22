# -*- coding: utf-8 -*-
################################################################################
#				ARDnew.py - Teil von Kodi-Addon-ARDundZDF
#			neue Version der ARD Mediathek, Start Beta Sept. 2018
#
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.ardmediathek.de/
#	bzw. den eingebetteten json-Code und die verknüpften api-Calls.
#
#	04.11.2019 Migration Python3
#	21.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
#
################################################################################
# 	<nr>91</nr>										# Numerierung für Einzelupdate
#	Stand: 07.11.2024

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
ICON					= "icon.png"
ICON_MAIN_ARD 			= 'ard-mediathek.png'			
ICON_ARD_AZ 			= 'ard-sendungen-az.png'
ICON_ARD_VERP 			= 'ard-sendung-verpasst.png'			
ICON_ARD_RUBRIKEN 		= 'ard-rubriken.png' 
ICON_ARD_BARRIEREARM 	= 'ard-barrierearm.png'
			
ICON_SEARCH 			= 'ard-suche.png'						
ICON_ZDF_SEARCH 		= 'zdf-suche.png'				
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_DIR_STRM			= "Dir-strm.png"
ICON_SPEAKER 			= "icon-speaker.png"
ICON_MEHR 				= "icon-mehr.png"
ICON_INFO 				= "icon-info.png"

ARDSender = ['ARD-Alle:ard::ard-mediathek.png:ARD-Alle', 'Das Erste:daserste:208:tv-das-erste.png:Das Erste', 
	'BR:br:2224:tv-br.png:BR Fernsehen', 'HR:hr:5884:tv-hr.png:HR Fernsehen', 'MDR:mdr:1386804:tv-mdr-sachsen.png:MDR Fernsehen', 
	'NDR:ndr:5898:tv-ndr-niedersachsen.png:NDR Fernsehen', 'Radio Bremen:radiobremen::tv-bremen.png:Radio Bremen TV', 
	'RBB:rbb:5874:tv-rbb-brandenburg.png:rbb Fernsehen', 'SR:sr:5870:tv-sr.png:SR Fernsehen', 
	'SWR:swr:5310:tv-swr.png:SWR Fernsehen', 'WDR:wdr:5902:tv-wdr.png:WDR Fernsehen',
	'ONE:one:673348:tv-one.png:ONE', 'arte:arte::arte_Mediathek.png:arte', 
	'funk:funk::ard-funk.png:funk', 'KiKA:KiKA::ard-kika.png:KiKA', '3sat:3sat::3sat.png:3sat', 
	'ARD-alpha:alpha:5868:tv-alpha.png:ARD-alpha', 'tagesschau24:tagesschau24::tv-tagesschau24.png:tagesschau24', 
	'phoenix:phoenix::tv-phoenix.png:phoenix', 
	]

ARDheaders="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
	'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}"

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

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):				# ADDON_DATA-Verzeichnis anpasen
	PLog('ARDnew_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
SLIDESTORE 		= os.path.join(ADDON_DATA, "slides") 
SUBTITLESTORE 	= os.path.join(ADDON_DATA, "subtitles") 
TEXTSTORE 		= os.path.join(ADDON_DATA, "Inhaltstexte")

# Ort FILTER_SET wie filterfile (check_DataStores):
FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()						# gesetzte Filter initialiseren 

DEBUG			= SETTINGS.getSetting('pref_info_debug')
NAME			= 'ARD und ZDF'

#-------------------
def ARD_CurSender():
	PLog("ARD_CurSender:")
	fname = os.path.join(DICTSTORE, 'CurSender')			 # init CurSender (aktueller Sender)
	CurSender=""
	if os.path.exists(fname):								 # kann fehlen (Aufruf Merkliste)
		CurSender = Dict('load', "CurSender")
	PLog(fname); PLog(CurSender)
	if CurSender == '' or up_low(str(CurSender)) == "FALSE": # Ladefehler?
		CurSender = ARDSender[0]
			
	return CurSender
#-------------------

CURSENDER = ARD_CurSender()
PLog("ARDnew_loaded")

#----------------------------------------------------------------
# CURSENDER neu in Senderwahl
def Main_NEW(name=''):
	PLog('Main_NEW:'); 
	PLog(name);
			
	CURSENDER = ARD_CurSender()
	sendername, sender, kanal, img, az_sender = CURSENDER.split(':')	# sender -> Menüs
	PLog("sendername %s, sender %s, kanal %s, img %s, az_sender %s" % (sendername, sender, kanal, img, az_sender))
	sender_summ = 'Sender: [B]%s[/B] (unabhängig von der Senderwahl)' % "ARD-Alle"
	summ=""
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	def_tag = 'Sender: [B]%s[/B]' % sendername
	
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'Sender: [B]alle Sender des ARD[/B]' 
		title=py2_encode(title); sender="ARD"
		func = "resources.lib.ARDnew.Main_NEW"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARD", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_MAIN_ARD), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)
		
	title = 'Suche in ARD-Mediathek'
	tag = def_tag + " (Suchbereich)"
	title=py2_encode(title);
	fparams="&fparams={'title': '%s', 'homeID': 'ARD'}" % quote(title) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
		fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag, 
		fparams=fparams)
	
	title = 'Startseite [B]%s[/B]' % az_sender
	tag = def_tag
	title=py2_encode(title);
	fparams="&fparams={'title': '%s', 'sender': '%s'}" % (quote(title), sender)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", fanart=R(ICON_MAIN_ARD), thumb=R(img), 
		tagline=tag, fparams=fparams)

	# Retro-Version ab 12.11.2020, V3.5.4
	# 16.06.2021 auch erreichbar via ARD-Startseite/Premium_Teaser_Themenwelten	
	# 07.04.2023 Web-Call -> api-Call	
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/retro?embedded=false" 
	title = "ARD Mediathek RETRO"
	erbe = u"[COLOR darkgoldenrod]%s[/COLOR]" % "UNESCO Welttag des Audiovisuellen Erbes"
	tag = u'Die ARD Sender öffneten zum %s ihre Archive und stellen zunehmend zeitgeschichtlich relevante Videos frei zugänglich ins Netz' % erbe
	tag = u"%s\n\nDeutsche Geschichte und Kultur nacherleben: Mit ARD Retro können Sie in die Zeit der 1950er und frühen 1960er Jahre eintauchen. Hier stoßen Sie auf spannende, informative und auch mal kuriose Sendungen aus den Anfängen der Fernsehgeschichte des öffentlich-rechtlichen Rundfunks." % tag
	tag = u"%s\n\nMehr: NDR ardretro100.html" % tag
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'title': '%s', 'sender': '%s', 'path': '%s'}" % (quote(title), sender, quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", fanart=R(ICON_MAIN_ARD), 
		thumb=R('ard-mediathek-retro.png'), tagline=tag, fparams=fparams)

	# 07.04.2023 Web-Call -> api-Call	
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/entdecken?embedded=false" 
	title = "ARD Mediathek Entdecken"
	tag = 'Inhalte der ARD-Seite [B]%s[/B]' % "ENTDECKEN"
	summ = sender_summ	
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'title': '%s', 'sender': '%s', 'path': '%s'}" % (quote(title), sender, quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStart", 
		fanart=R(ICON_MAIN_ARD), thumb=R('ard-entdecken.png'), tagline=tag, summary=summ, fparams=fparams)

	# 23.12.2023 "Unsere Region" als eigenständiges Menü. Bei der ARD nur in Startseite für ARD-Alle
	# 	errreichbar (skipped in ARDStart).
	rname = "Berlin"; partner = "rbb"				# Default
	items = Dict("load", 'ARD_REGION')				# Bsp.: by|Bayern|br
	rname = "Berlin"; partner = "rbb"				# path s. ARDStartRegion
	if "|" in str(items):
		region,rname,partner = items.split("|")
	title = "Unsere Region" 
	tag = u"aktuelle Region: [B]%s[/B]" % rname
	tag = u"%s\n\nDie Auswahl ist unabhängig von der Senderwahl ([B]%s[/B])" % (tag, sendername)
	summ = u"Partnersender: [B]%s[/B]" % partner
	path=py2_encode(path); title=py2_encode(title); 
	fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s','homeID': '%s'}" %\
		(quote(path), quote(title), "Main_NEW", 'ARD Neu')
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRegion",
		fanart=R(ICON_MAIN_ARD), thumb=R("ard-unsereRegion.png"), tagline=tag, summary=summ, fparams=fparams)
	
	# 25.12.2021 als eigenständiges Menü (zusätzl. zum Startmenü) - wie Web:
	#	href wie get_ARDstreamlinks
	title = 'Livestreams'
	tag = "Die [B]Livestreams[/B] der ARD"
	summ = 'Sender: [B]%s[/B] (unabhängig von der Senderwahl)' % "ARD-Alle"
	summ = "%s\n\n Fehlende regionale Sender, z.B. BR-Nord, finden sich im Hauptmenü TV-Livestreams" % summ
	img = R("ard-livestreams.png")
	ID = 'Livestream'
	href = 'https://api.ardmediathek.de/page-gateway/widgets/ard/editorials/4hEeBDgtx6kWs6W6sa44yY?pageNumber=0&pageSize=24'
	href=py2_encode(href); title=py2_encode(title); 
	fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
		(quote(href), quote(title), ID)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag, summary=summ)																							

	s = ["KiKA", "funk"]		# ohne Verpasst (wie Web), s.a. Button Senderwahl
	if sendername not in s:			
		title = 'Sendung verpasst'
		tag = def_tag + u"\nHinweis: keine Anzeige für ARD-Alle."
		fparams="&fparams={'title': 'Sendung verpasst'}"
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasst", 
			fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_VERP), tagline=tag, fparams=fparams)
	
	title = 'Sendungen A-Z'
	tag = def_tag
	fparams="&fparams={'title': 'Sendungen A-Z'}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ", 
		fanart=R(ICON_MAIN_ARD), thumb=R(ICON_ARD_AZ), tagline=tag, fparams=fparams)
						
	# 07.04.2023 Web-Call -> api-Call, 14.04.2023 ARDStart -> ARDRubriken	
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/sport?embedded=false" 
	title = 'ARD Sport'
	summ = sender_summ	
	img = R("ard-sport.png")
	fparams="&fparams={}"
	title=py2_encode(title); path=py2_encode(path);
	fparams="&fparams={'li': '', 'path': '%s'}" % quote(path)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDRubriken", 
		fanart=img, thumb=img, summary=summ, fparams=fparams)
			
	# ARD Sportschau nach Web-Änderung abgeschaltet - s. Forum Post vom 12.06.2022
	#	Ausgesuchte Inhalte sportschau.de in ARDSportWDR
	title = u"ARD sportschau.de (WDR)"					# Button WDR sportschau.de -> Hapt_PRG
	tag = u"Auszüge - einschließlich Audio Event Streams"
	img = R("ard-sportschau.png")
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="ardundzdf.ARDSportWDR", fanart=img, thumb=img, 
		fparams=fparams, tagline=tag)	
			
	# 27.11.2021 als eigenständiges Menü (vorher an wechselnden Pos. im Startmenü):
	title = 'Barrierearm'
	tag = "Barrierefreie Inhalte in der ARD Mediathek"
	summ = sender_summ	
	img = R(ICON_ARD_BARRIEREARM)
	href = 'https://api.ardmediathek.de/page-gateway/pages/ard/editorial/barrierefrei?embedded=true'
	href=py2_encode(href); title=py2_encode(title); 
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", 
		fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ)																							

	title = 'Bildgalerien Das Erste'	
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="BilderDasErste", fanart=R(ICON_MAIN_ARD),
		thumb=R('ard-bilderserien.png'), fparams=fparams)

	fparams="&fparams={}"												# ab V 4.8.1
	tag = u"Quelle: ARD Text HbbTV | Federführung: RBB"
	addDir(li=li, label="Teletext ARD", action="dirList", dirID="resources.lib.ARDnew.ARD_Teletext", 
		fanart=R("teletext_ard.png"), thumb=R("teletext_ard.png"), tagline=tag, fparams=fparams)
	
	title 	= u'Wählen Sie Ihren Sender | aktuell: [B]%s[/B]' % sendername	# Senderwahl
	tag = "die Senderwahl ist wirksam in [B]%s[/B], [B]%s[/B] und [B]%s[/B]" % ("ARD Mediathek", "A-Z", "Sendung verpasst")
	s = ["KiKA", "funk"]		# ohne Verpasst (wie Web)
	if sendername in s:			
		tag = "die Senderwahl ist wirksam in [B]%s[/B] und [B]%s[/B] (nicht in Verpasst)" % ("ARD Mediathek", "A-Z")
	title=py2_encode(title);
	fparams="&fparams={'title': '%s'}" % quote(title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", fanart=R(ICON_MAIN_ARD), 
		thumb=R('tv-regional.png'), tagline=tag, fparams=fparams) 

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
# 30.09.2021 Sonderbehdl. spaltenübergreifender Titel mit Breitbild (Auswert. descr, skip Bild)
# 29.06.2022 Abzweig ARDStartRegion für neuen Cluster "Unsere Region" 
# 07.04.2023 Wechsel Web-Call (ardmediathek.de) -> api-Call (api.ardmediathek.de) - embedded
#	json identisch
# Links des api-Calls für ard=ARD-Alle funktionieren nicht mehr (HTTP ERROR 404). Beim neuen
#	api-Call erfordert das Merkmal personalized eine Authentifizierung bei den Folgecalls.
#	Merkmal hier entfernt (entfällt so autom. bei den Folgecalls).
# 07.11.2024 Mitnutzung Startseite durch arte, funk, KiKA, 3sat nach Aufnahme in Senderwahl.
#
def ARDStart(title, sender, widgetID='', path='', homeID=''): 
	PLog('ARDStart: ' + title); PLog(sender); PLog(homeID)

	CurSender = ARD_CurSender()
	if homeID:												# CurSender in sender (Bsp. phoenix-Calls)
		CurSender=sender
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	senderimg = img
	PLog(sender); PLog(img)	
	summ = 'Mediathek des Senders [B] %s [/B]' % sendername
		
	if sender == "ard":
		base = "https://api.ardmediathek.de/page-gateway/pages/ard/home?embedded=true"    # true: Variante mit Teasern
		#base = "https://api.ardmediathek.de/page-gateway/pages/ard/home?embedded=false"  # kl. Variante o. Bilder
	else:
		base = "https://api.ardmediathek.de/page-gateway/pages/%s/home?embedded=true" % sender

	if path == '':
		path = base
	DictID = "ARDStart_%s" % sendername
	page=""
	if title != "Startseite":								# Cache nur für Startseite, nicht Retro u.a.
		page, msg = get_page(path, header=ARDheaders)	
	else:
		page = Dict("load",DictID,CacheTime=ARDStartCacheTime)	# Cache: 5 min
		if not page:											# nicht vorhanden oder zu alt -> vom					
			page, msg = get_page(path, header=ARDheaders)			# 	Sender holen		
			if page:
				icon = R(ICON_MAIN_ARD)
				xbmcgui.Dialog().notification("Cache %s:" % DictID,"Haltedauer 5 Min",icon,3000,sound=False)
				Dict('store', DictID, page)						# json-Datei -> Dict, 1 - 2,5 MByte mit Teasern,
																#	je nach Sender
	if page == "":
		msg1 = 'Fehler in ARDStart:'
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return
			
	PLog(len(page))
	page = page.replace('\\"', '*')							# quotierte Marks entf.
	
	li = xbmcgui.ListItem()
	if not homeID:
		li = home(li, ID='ARD Neu')							# Home-Button
	else:
		li = home(li, ID=homeID)

	container = blockextract ('compilationType":', page)  	# widgets-Container json (Swiper + Rest)
	PLog(len(container))
	title_list=[]											# für Doppel-Erkennung
	skip_list = [u"Empfehlungen für Sie", u"Weiterschauen",	# personalierte Inhalte
			u"Meine Merkliste", u"Ist Ihre App bereit",
			u"Login-Promo"]

	cnt=0
	for cont in container:
		tag=""; summ=""; skip_title=False
		descr =  stringextract('"description":"', '"', cont)
		ID	= stringextract('"id":"', '"', cont)			# id vor pagination
		pos = cont.find('"pagination"')						# skip ev. spaltenübergreifendes Bild mit 
		if pos > 0:											# descr (Bsp. Bundestagswahl 2021)
			cont = cont[pos:]
			
		title 	= stringextract('"title":"', '"', cont)
		if title in title_list:								# Doppel? - s.o.
			break
		title_list.append(title)
		title = repl_json_chars(title)
				
		ID	= stringextract('"id":"', '"', cont)
		anz= stringextract('"totalElements":', '}', cont)
		anz= mystrip(anz)
		PLog("anz: " + anz)
		if anz == '1':
			tag = u"%s Beitrag" % anz
		else:
			if anz == "null": anz='mehrere'					# continue 0 s.u.
			tag = u"%s Beiträge" % anz
		if descr:
			tag = "%s\n\n%s" % (tag, descr)
			
		for item in skip_list:								# skip personalierte Inhalte
			if item in title:
				skip_title=True
				break
		if 	skip_title:
			PLog("skip_list: %s" % title)
			continue
		ctaLabel = stringextract('"ctaLabel":"', '"', cont)# skip Anmelde-Links
		if ctaLabel:
			PLog("skip_ctaLabel: %s" % ctaLabel)
			continue

		path 	= stringextract('"href":"', '"', cont)
		path = path.replace('&embedded=false', '')			# bzw.  '&embedded=true'
		partner=""											# Abgleich Region
		if "/region/" in path and '{regionId}' in path:		# Bild Region laden, Default Berlin
			region="be"; rname="Berlin"; partner="rbb"		# Default-Region, Änderung in ARDStartRegion
			path = path.replace('{regionId}', region)

		if '"images":' in cont:								# Teaser mit Bildern vorhanden
			img = img_load(title, cont)
		else:												# Teaser fehlt -> im Voraus laden
			img_path = path.split("pageSize")[0] + "pageSize=1"	# 1. Beitrag reicht
			img = img_preload(ID, img_path, title, 'ARDStart')
		
		if anz == "0" and "/region/" not in path:			# skip 0 Inhalte
			PLog("skip_anz_0: %s" % title)
			continue	

		if 'Livestream' in title or up_low('Live') in up_low(title):
			if 'Konzerte' not in title:						# Corona-Zeit: Live-Konzerte (keine Livestreams)
				ID = 'Livestream'
		else:
			ID = 'ARDStart'			

		# Menü "Unsere Region" verlagert zu Main_NEW (-> ARDStartRegion).
		#	Hier skipped für ARD-Alle:
		if "Unsere Region" in title:
				continue

		# Ersetzung kann entfallen, wenn personalized bereits im Aufruf-Call fehlt
		path = path.replace("userId=personalized&", "")	# 17.08.2023 personalized erfordert Authentif.	
		label = title										# Anpassung phoenix ("Stage Widget händisch")
		if title.startswith("Stage") or title.startswith("Die besten Videos"):
			label = "[B]Highlights[/B]"	
		
		func = "ARDStartRubrik"
		PLog(path); PLog(img); PLog(title); PLog(ID); PLog(anz); 
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s','homeID': '%s'}" %\
			(quote(path), quote(title), ID, homeID)
		addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.%s" % func, fanart=img, 
			thumb=img, tagline=tag, summary=summ, fparams=fparams)
		cnt=cnt+1	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
				
#-----------------------------------------------------------------------
# 17.08.2023 img-Link für Startseite aus Block item ermitteln
#
def img_load(title, item, icon=ICON_MAIN_ARD):
	PLog("img_load: " + title)
	leer_img = R(ICON_DIR_FOLDER)
	
	img = stringextract('src":"', '"', item)			# Pfad zum 1. img
	PLog(img)
	if img == '':
		return leer_img									# Fallback 
	else:
		img = img.replace('{width}', '720')
		return img	

#-----------------------------------------------------------------------
# 19.10.2020 Ablösung img_via_id durch img_preload nach Änderung 
#	der ARD-Startseite: lädt das erste img ermittelt in geladener
#	Seite oder ID.img aus dem Cache - Löschfrist: Setting Slide Shows)
#
def img_preload(ID, path, title, caller, icon=ICON_MAIN_ARD):
	PLog("img_preload: " + title)
	PLog(caller); PLog(path)

	if caller == 'ARDStart' or  caller == 'ARDRubriken':
		leer_img = R(ICON_DIR_FOLDER)
	else:
		leer_img = R("icon-bild-fehlt_wide.png")

	img=''
	oname = os.path.join(SLIDESTORE, "ARDNeu_Startpage")
	fname = os.path.join(oname, ID)
	# PLog(fname)
	
	if os.path.isdir(oname) == False:
		try:  
			os.mkdir(oname)								# UZ-Verz. ARDNeu_Startpage erzeugen
		except OSError as exception:
			msg = str(exception)
			PLog(msg)
			
	if os.path.exists(fname):							# img aus Cache laden
		PLog('img_cache_load: ' + fname)	
		return fname
	else:
		PLog('img_cache_leer')	
		path=path.replace("%3A", ":")					# ARD-Problem
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
		
	PLog('img_cache_fill: ' + fname)	
	return fname										# lokaler img-Pfad
	
#---------------------------------------------------------------------------------------------------
# Auflistung der Rubriken in json-Inhalt page (json bei html-Seite
#	in script id="fetchedContextValue")
# Hinw.: vorerst Verzicht auf ev. Topnavigation (Submenüs), außer 
#	Sportseite
#
def ARDRubriken(li, path="", page="", homeID=""): 
	PLog('ARDRubriken:')
	li_org=li

	if page == '':
		skip_subs=False
		page, msg = get_page(path)
	else:
		skip_subs=True									# Subrubriken nicht erneut listen					
	PLog(len(page))
	page = page.replace('\\"', '*')						# quotierte Marks entf.

	if li == "":
		li = xbmcgui.ListItem()
		if homeID:
			li = home(li, ID=homeID)
		else:	
			li = home(li, ID='ARD Neu')					# Home-Button		

	try:
		obs = json.loads(page)
		PLog(str(obs)[:80])
		widgets = obs["widgets"]						# "teasers" hier leer			
	except Exception as exception:
		PLog(str(exception))
		return
	PLog(len(widgets))	

	for s in widgets:	
		PLog(str(s)[:60])	
		img_alt=""; anz="null"
		
		typ = s["type"]
		title = s["title"]
		if title.startswith("Subrubriken"):					# wurde hier bereits gelistet, s.o.
			if skip_subs:
				continue
		if title == "Rubriken":								# rekursiv zur Startseite
			continue
		title  = repl_json_chars(title)
		ID = s["id"]

		if "links" in s:
			path = s["links"]["self"]["href"]
			path = path.replace('&embedded=false', '')		# bzw. true
			
		try:
			if "images" in s:
				img_cont= s["images"]["aspect16x9"]
				img 	= img_cont["src"]
				img 	= img.replace('{width}', '640')
				img_alt	= img_cont["alt"]
			else:
				if "teasers" in s:							# Icon fehlt, aus 1. Teaser holen
					img_cont 	= s["teasers"][0]["images"]["aspect16x9"]
					img 	= img_cont["src"]
					img = img.replace('{width}', '640')
					img_alt = img_cont["alt"]
		except Exception as exception:
			PLog("img_error: " + str(exception))
			img=""
		if img == "":										# Fallback: mit Titel auf kompl. Seite suchen
			img = img_preload(ID, path, title, 'ARDRubriken')			
		
		tag = "Folgeseiten"
		if 	img_alt:
			tag =  u"%s\nBild: %s" % (tag, img_alt)
		
		ID = 'ARDStartRubrik'
		PLog('Satz_cont2:');
		PLog(title); PLog(ID); PLog(anz); PLog(img); PLog(path);
		path=py2_encode(path); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s', 'homeID': '%s'}" %\
			(quote(path), quote(title), ID, homeID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", 
			fanart=img, thumb=img, tagline=tag, fparams=fparams)
			
	if li_org == "":
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:	
		return

###################################################			
#---------------------------------------------------------------------------------------------------
# 29.06.2022 Auswertung Cluster "Unsere Region"
# Default-Region: Berlin (wie Web), ID=change: Wechsel
# widgetID transportiert hier region-Triple (Bsp. be|Berlin|rbb)
# 21.12.2023 Auswertung regio_kat von ARDStart verlagert, Katalog 
#	an api-Url's angepasst (früher Web).
#
def ARDStartRegion(path, title, widgetID='', ID='', homeID=""): 
	PLog('ARDStartRegion:')
	PLog(widgetID)
	PLog(ID)	
	title_org = title
	base = "https://api.ardmediathek.de/page-gateway/widgets/"

	if widgetID:											# frisch gewechselt
		region,rname,partner = widgetID.split("|")
		Dict("store", 'ARD_REGION', "%s|%s|%s" % (region,rname,partner)) 
	else:
		region=""; rname=""; partner=""; 					# region -> Abgleich reg_kat
		page = Dict("load", 'ARD_REGION')
		try:
			region,rname,partner = page.split("|")
		except Exception as exception:
			PLog(str(exception))
			region=""
	if region == "": 										# Default-Region
		region="be"; rname="Berlin"; partner="rbb"
	PLog("region: %s, rname: %s, partner: %s" % (region, rname, partner))
	
	path = base + "ard/region/1FdQ5oz2JK6o2qmyqMsqiI:-947156297680186331/%s?pageNumber=0&pageSize=100&embedded=true" % region
	page, msg = get_page(path=path)
	if page == '':	
		msg1 = "Fehler in ARDStartRegion: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
		
	li = xbmcgui.ListItem()
	if homeID:											# phoenix
		li = home(li, homeID)
	else:
		li = home(li, ID='ARD Neu')						# Home-Button
	regions = stringextract('regions":', '"links"', page)
	PLog(len(regions))
	
	#------------------------							# Änderungsliste Region
	if "change" in ID:
		PLog("do_change:")
		PLog(regions[:60])
		img = R(ICON_DIR_FOLDER)
		items = blockextract('"id"', regions)			# Liste in jeder api-region-Seite
		for item in items:
			region = stringextract('id":"', '"', item)
			rname = stringextract('name":"', '"', item)
			partner = stringextract('partner":"', '"', item)
			
			widgetID = "%s|%s|%s" % (region,rname,partner)
			title = u"Region: [B]%s[/B]" % rname
			tag = u"Partnersender: [B]%s[/B]" % partner
		
			title=py2_encode(title); widgetID=py2_encode(widgetID);
			fparams="&fparams={'path': '', 'title': '%s', 'widgetID': '%s', 'ID': '', 'homeID': '%s'}" %\
				(quote(title), quote(widgetID), homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRegion", 
				fanart=img, thumb=img, tagline=tag, fparams=fparams)
	
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return
	
	#------------------------							# Auswertung Region
	# Regionen mit Partnersendern am Kopf jeder Region-Seite, region-id abweichend von sender.
	#	Bayern=by,  Berlin=be, Brandenburg=bb, Hessen=he, Mecklenburg-Vorpommern=mv, 
	#	Niedersachsen=ni, NW=nw, R-Pfalz=rp, Saarland=sl, Sachsen=sn, Sachsen-Anhalt=st, 
	# 	"Schleswig-Holstein=sh, Thüringen=th
	PLog("regio_check: %s" % partner)					# spez. Inhalte voranstellen
	regio_kat = [										# nach Bedarf ergänzen
		"by|Unter unserem Himmel|https://api.ardmediathek.de/page-gateway/pages/ard/grouping/Y3JpZDovL2JyLmRlL2Jyb2FkY2FzdFNlcmllcy9icm9hZGNhc3RTZXJpZXM6L2JyZGUvZmVybnNlaGVuL2JheWVyaXNjaGVzLWZlcm5zZWhlbi9zZW5kdW5nZW4vdW50ZXItdW5zZXJlbS1oaW1tZWw|https://api.ardmediathek.de/image-service/images/urn:ard:image:af246683efe842f0?w=640&ch=fcad9e13605d8eb0"
		,"by|Blickpunkt Sport|https://api.ardmediathek.de/page-gateway/pages/ard/grouping/Y3JpZDovL2JyLmRlL2Jyb2FkY2FzdFNlcmllcy9icm9hZGNhc3RTZXJpZXM6L2JyZGUvZmVybnNlaGVuL2JheWVyaXNjaGVzLWZlcm5zZWhlbi9zZW5kdW5nZW4vYmxpY2twdW5rdC1zcG9ydA|https://api.ardmediathek.de/image-service/images/urn:ard:image:47139d13d3483f29?w=640&ch=9d54ad9bea96ef5b"
		,"he|Heimat Hessen|https://api.ardmediathek.de/page-gateway/pages/ard/grouping/Y3JpZDovL2hyLW9ubGluZS8zODIxMDI4MQ|https://api.ardmediathek.de/image-service/images/urn:ard:image:f049db09043c494c?w=640&ch=c8f27b2223dbd951"
		,"he|Sport im hr|https://api.ardmediathek.de/page-gateway/pages/hr/editorial/hr-sport-hessen|https://api.ardmediathek.de/image-service/images/urn:ard:image:728fab9db02e4bae?ch=011a995a203e585a&w=640"
		,"sl|Sport im SR|https://api.ardmediathek.de/page-gateway/widgets/sr/editorials/E7IQVqrZXqK24ieYwG8kO%3A-115180639807314065|https://api.ardmediathek.de/image-service/images/urn:ard:image:1c772b30babcd252?ch=5266a5922c5f86f0&w=640"
		,"sn|MDR+|https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL21kci5kZS9tZHJwbHVz?pageNumber=0&pageSize=48|https://api.ardmediathek.de/image-service/images/urn:ard:image:eab36fa8ffdb27da?w=640&ch=4bc0c7d930d596d9"
		,"sn|Sport im Osten|https://api.ardmediathek.de/page-gateway/widgets/ard/asset/Y3JpZDovL21kci5kZS9zZW5kZXJlaWhlbi82ODlhYzU5My1mOWFkLTQ3MTAtOTczMS1lMTNiZTEwODZkMGM?pageNumber=0&pageSize=48|https://api.ardmediathek.de/image-service/images/urn:ard:image:4b8aeaada557019e?w=1600&ch=50fb95aed76b8244&imwidth=1600"
		,"nw|Sportclub Story|https://api.ardmediathek.de/page-gateway/compilations/ard/2odyJaRzcJftj4uaJcwNYQ?pageNumber=0&pageSize=12&embedded=true|https://api.ardmediathek.de/image-service/images/urn:ard:image:0480dc9eb73502e2?w=640&ch=cd45598f741bf56c"
		]
	for item in regio_kat:
		region_kat, reg_title, reg_path, reg_img= item.split("|")
		PLog("region: %s, region_kat: %s" % (region, region_kat))
		ID="ARDStartRegion"
		if region == region_kat:
			if reg_img == "":
				reg_img = R(ICON_DIR_FOLDER)
			reg_tag = "besondere regionale Inhalte des %s" % up_low(partner)
			reg_path=py2_encode(reg_path); reg_title=py2_encode(reg_title); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
				(quote(reg_path), quote(reg_title), ID)
			addDir(li=li, label=reg_title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik",
				fanart=reg_img, thumb=reg_img, tagline=reg_tag, fparams=fparams)
	
	PLog("do_region:")
	ID = "ARDStartRubrik"
	mark=''	
	li = get_json_content(li, page, ID, mark)			# Auswertung Rubriken + Live-/Eventstreams
	icon = R(ICON_DIR_FOLDER)
	img = icon
	msg1 = "Region"
	msg2 = rname										# Dateiname bei ARD neu nichtssagend
	xbmcgui.Dialog().notification(msg1,msg2,icon,2000, sound=False)	 
	
																	
	if 	'"pagination":'	in page:						# Scroll-Beiträge
		PLog('pagination_Rubrik:')
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
		pages, pN, pageSize, totalElements, next_path = get_pagination(page)	# Basis 0		
		
		if next_path:	
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements)
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % str(pN)
			PLog(summ); PLog(next_path)

			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s','homeID': '%s'}" %\
					(quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark), homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDPagination", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	

	label = u"Region ändern"
	tag = u"aktuelle Region: [B]%s[/B]" % rname
	path=py2_encode(path); title=py2_encode(title); 
	fparams="&fparams={'path': '%s', 'title': '%s', 'ID': 'change','homeID': '%s'}" %\
		(quote(path), quote(title_org), homeID)
	addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.ARDStartRegion", 
		 fanart=img, thumb=img, tagline=tag, fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

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
# 18.04.2023 Cache für Startseite entfällt (obsolet - api-Call)
#		
def ARDStartRubrik(path, title, widgetID='', ID='', img='', homeID=""): 
	PLog('ARDStartRubrik: %s' % ID); PLog(title); PLog(path)
	# Titel-Anpassung für phoenix ("Stage Widget händisch"):
	if title.startswith("Stage") or title.startswith("Die besten Videos"):
		title = "[B]Highlights[/B]"
	title_org = title
	
	CurSender = ARD_CurSender()								# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)	
		
	li = xbmcgui.ListItem()
	if homeID:											# phoenix
		li = home(li, ID=homeID)
	else:
		if ID == "ARDRetroStart":
			li = home(li, ID=NAME)						# Home-Button -> Hauptmenü
		else:
			li = home(li, ID='ARD Neu')					# Home-Button

	if "sportschau.de" in path:							# nach Olympia 2024 wieder entfernen (html-Seiten)
		msg1 = "ARDStartRubrik: diese Seite ist hier nicht auswertbar:"
		msg2 = path
		PLog("%s %s" % (msg1, msg2))
		MyDialog(msg1, msg2, "")	
		return li
		
	path=path.replace("%3A", ":")
	page, msg = get_page(path=path, GetOnlyRedirect=True, header=ARDheaders, do_safe=True)
	path = page
	page, msg = get_page(path=path, header=ARDheaders, do_safe=True)	
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
		PLog("ARDStartRubrik_more_container")
		ARDRubriken(li, page=page, homeID=homeID)		# direkt
	else:												# detect Staffeln/Folgen
		# cnt = page.count(u'"Folge ')					# falsch positiv für "alt":"Folge 9"
		if 'hasSeasons":true' in page and '"heroImage":' in page:
			PLog('Button_FlatListARD')					# Button für flache Liste
			label = u"komplette Liste: %s" % title
			tag = u"Liste aller verfügbaren Folgen"
			if SETTINGS.getSetting('pref_usefilter') == 'false':
				add = u"Voreinstellung: Normalversion.\nFür Hörfassung und weitere Versionen "
				add = u'%sbitte das Setting <Beiträge filtern / Ausschluss-Filter> einschalten' % add
				tag = u"%s\n\n%s" % (tag, add)
			title=py2_encode(title); path=py2_encode(path)			
			fparams="&fparams={'path': '%s', 'title': '%s'}"	% (quote(path), quote(title))						
			addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.ARD_FlatListEpisodes", 
				fanart=ICON, thumb=R(ICON_DIR_FOLDER), tagline=tag, fparams=fparams)
		
		if ID != "Livestream":	
			ID = "ARDStartRubrik"	
		if "Subrubriken" in title_org:				# skip Subrubrik Übersicht
			mark="Subrubriken"
		li = get_json_content(li, page, ID, mark, homeID=homeID)																
#----------------------------------------
	
	# 24.08.2019 Erweiterung auf pagination, bisher nur AutoCompilationWidget
	#	pagination mit Basispfad immer vorhanden, Mehr-Button abhängig von Anz. der Beiträge
	if 	'"pagination":'	in page:						# Scroll-Beiträge
		PLog('pagination_Rubrik:')
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
		pages, pN, pageSize, totalElements, next_path = get_pagination(page)	# Basis 0		
		
		if next_path:	
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements)
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % str(pN)
			PLog(summ); PLog(next_path)
			
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s','homeID': '%s'}" %\
					(quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark), homeID)
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
	if pageSize == '' or totalElements == '' or totalElements == 'null':	# Sicherung 
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
def ARDPagination(title, path, pageNumber, pageSize, ID, mark, homeID=""): 
	PLog('ARDPagination: ' + ID)
	PLog(path)
	path =  unquote(path)									# quotierter Doppelpunkt möglich
	PLog(path)
	
	title_org 	= title 
	
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
	else:
		li = home(li, ID='ARD Neu')							# Home-Button

	page, msg = get_page(path)					
	if page == '':	
		msg1 = "Fehler in ARDPagination: %s"	% title
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	page = page.replace('\\"', '*')							# quotierte Marks entf.
	
	
	li = get_json_content(li, page, ID, mark)
	
	if 	'"pagination":'	in page:				# z.B. Scroll-Beiträge zu Rubriken
		title = "Mehr zu >%s<" % title_org		# Mehr-Button	 # ohne Pfad
		li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
		pages, pN, pageSize, totalElements, next_path  = get_pagination(page)
		
		# Mehr-Button, falls noch nicht alle Sätze ausgegeben		
		if next_path:
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements) 
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % pN	
			
			PLog(summ); PLog(next_path)
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s','homeID': '%s'}" %\
					(quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark), homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDPagination", 
				fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
	
	xbmcplugin.endOfDirectory(HANDLE)
	
#---------------------------------------------------------------------------------------------------
# Ähnlich ZDF_FlatListEpisodes, flache Liste aller Folgen
#	ohne Zusätze (Teaser usw.)
# Aufruf ARDStartRubrik ('hasSeasons":true')
#
def ARD_FlatListEpisodes(path, title):
	PLog('ARD_FlatListEpisodes:')
	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = u"Fehler in ARD_FlatListEpisodes: %s"	% title
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page))
	page = page.replace('\\"', '*')						# quotierte Marks entf.

	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)									# Home-Button -> HauptmenüARDStartSingle:

	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
		mediatype='video'
		
	versions = [u'Normalfassung', u'Hörfassung', u'Originalversion (OV)']
	if page.find(u'(OV)') < 0 and page.find(u'(Originalversion)') < 0: 	# Varianten OV
		versions.remove(u'Originalversion (OV)')
	if page.find(u'Hörfassung') < 0:
		versions.remove(u'Hörfassung')
	PLog("versions" + str(versions))

	vers='Normalfassung'								# Default: Normalfassung
	if u'Hörfassung' in page or u'(OV)' in page or 'Originalfassung' in page or '(Originalversion)' in page:	
		if SETTINGS.getSetting('pref_usefilter') == 'true':	# Abfrage Audiodeskription / Originalfassung
			head = u"bitte Filter wählen"
			ret = xbmcgui.Dialog().select(head, versions)
			if ret < 0:
				PLog("Abbruch")
				#return  crasht Addon nach Video, Liste wird erneut durchlaufen - nach Filterwahl OK 
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)					
			v = versions[ret]; 
			vers = py2_decode(v)
			
	#---------------------										# Button strm-Dateien gesamte Liste
	if SETTINGS.getSetting('pref_strm') == 'true':
		img = R(ICON_DIR_STRM)
		title = u"strm-Dateien für die komplette Liste erzeugen / aktualisieren"
		tag = u"Verwenden Sie das Kontextmenü, um strm-Dateien für [B]einzelne Videos[/B] zu erzeugen"
		summ = u"[B]strm-Dateien (strm-Bündel)[/B] sparen Platz und lassen sich auch in die Kodi-Bibliothek integrieren."
		summ = u"%s\n\nEin strm-Bündel in diesem Addon besteht aus der strm-Datei mit der Streamurl, einer jpeg-Datei" % summ
		summ = u"%s\nmit dem Bild zum Video und einer nfo-Datei mit dem Begleittext." % summ
		url = path
		url=py2_encode(url); title=py2_encode(title); 
		fparams="&fparams={'path': '%s', 'title': '%s'}" %\
			(quote(url), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARD_getStrmList", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ)

		title = u"strm-Tools"									# Button für strm-Tools
		tag = "Abgleichintervall in Stunden\nListen anzeigen\nListeneinträge löschen\n"
		tag = "%sMonitorreset\nstrm-Log anzeigen\nAbgleich einer Liste erzwingen\n" % tag
		tag = "%sunterstützte Sender/Beiträge\nzu einem strm-Verzeichnis wechseln" % tag
		myfunc="resources.lib.strm.strm_tools"
		fparams_add = quote('{}')

		fparams="&fparams={'myfunc': '%s', 'fparams_add': '%s'}"  %\
			(quote(myfunc), quote(fparams_add))			
		addDir(li=li, label=title, action="dirList", dirID="start_script",\
			fanart=R(FANART), thumb=R("icon-strmtools.png"), tagline=tag, fparams=fparams)	

	#---------------------
	
	items = blockextract('availableTo":', page)					# Videos
	PLog("items_list: %d" % len(items))
	for item in items:
		if "Folge " in item == False:
			continue
		title, url, img, tag, summ, season, weburl, ID = ARD_FlatListRec(item, vers) # Datensatz
		if title == '':											# skipped
			continue
		summ_par = summ.replace('\n', '||')
		if SETTINGS.getSetting('pref_usefilter') == 'true':		# Filter
			filtered=False
			for fil in AKT_FILTER: 
				if up_low(fil) in py2_encode(up_low(str(item))):
					filtered = True
					break		
			if filtered:
				PLog('filtered_6: <%s> in %s ' % (item, title))
				continue		
		
		url=py2_encode(url); title=py2_encode(title); summ_par=py2_encode(summ_par);
		fparams="&fparams={'path': '%s', 'title': '%s', 'summary': '%s', 'ID': '%s'}" %\
			(quote(url), quote(title), quote(summ_par), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
			fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------
# holt Details für item
# Aufrufer: ARD_FlatListEpisodes, ARD_getStrmList
# Titel enthält Staffel-/Folgen-Kennz., Bsp.: Folge 1: Das Seil <S01/E01>
# vers: Version, z.B. Hörfassung
#
def ARD_FlatListRec(item, vers):
	PLog('ARD_FlatListRec: ' + vers)
	vers_list=[]	 
	if 'Original' in vers:
		vers_list = [u'(OV)', u'(Original']
	if u'Hörfassung' in vers:
		vers_list = [u'Hörfassung']

	title='';url='';img='';tag='';summ='';
	season='';episode='';descr='';weburl=''; ID=''
	
	title = stringextract('"longTitle":"', '"', item)
	if title == "":
		title =  stringextract('"mediumTitle":"', '"', item)
	PLog("title: " + title)
	title_org=title
	
	if 'Normal' in vers:								# Version berücksichtigen?
		if u'Hörfassung' in title or u'(OV)' in title or u'Original' in title or u'Trailer:' in title:
			PLog("skip_title: " + title)	
			return '', url, img, tag, summ, season, weburl, ID
	else:
		skip=True
		v=''
		for v in vers_list:
			PLog(title.find(v))
			if title.find(v) >= 0:
				skip=False; break
		if skip == True:
			PLog("skip: %s" % v)	
			return '', url, img, tag, summ, season, weburl, ID
	
	#---------------------								# Staffel-/Folge-Erkennung
	se=''
	try:												# hinter Folge in Titel kann ":" fehlen
		se = title
		if ":" in se:
			se = se.split(":")[-1]						# manchmal zusätzl. im Titel: ..(6):.. 
		se = re.search(r'\((.*?)\)', se).group(1)		# Bsp. (S03/E12)
		season = re.search(r'S(\d+)', se).group(1)
		episode = re.search(r'E(\d+)', se).group(1)
	except Exception as exception:
		PLog(str(exception))
	if season == '' and episode == '':					# Alternative: ohne Staffel, nur Folgen
		try: 
			episode = re.search(r'\((\d+)\)', title).group(1)									
			season = "0"
		except Exception as exception:
			PLog(str(exception))	
	PLog(season); PLog(episode)
	
	if episode == '':
		title=''
		PLog("no_episode")	
		return '', url, img, tag, summ, season, weburl, ID	
	
	if title.startswith("Folge "):						# Austausch "Folge 1" -> S01E01
		if ":" in title:								# mögl. Titel: "Folge 28 (S03/E12)"
			pos = title.find(":")
			if pos > 0:
				title = title[pos+1:]
			title = "S%02dE%02d %s" % (int(season), int(episode), title)
		else:
			title = "S%02dE%02d Folge %02d Staffel %s" % (int(season), int(episode), int(episode), season)
	else:
		title = "S%02dE%02d %s" % (int(season), int(episode), title)

	if u"Hörfassung" in title_org and title.find(u"Hörfassung") < 0:
		title = u"%s - %s" % (title, u"Hörfassung")	
	
	producer =  stringextract('"producerName":"', '"', item)
	descr =  stringextract('"synopsis":"', '"', item)
	web = stringextract('"homepage"', '"hasSeasons"', item)
	weburl =  stringextract('"href":"', '"', web) # für Abgleich vor./nicht mehr vorh. 
	fsk =  stringextract('Rating":"', '"', item)
	if up_low(fsk) == "NONE":
		fsk = "ohne"
	end =  stringextract('availableTo":"', '"', item)
	end = time_translate(end, day_warn=True)
	end = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % end
	# geo =  stringextract('Rating":"', '"', item)		# Geo fehlt
	dauer = stringextract('"duration":', ',', item)
	dauer = seconds_translate(dauer)
	Type =  stringextract('groupingType":"', '"', item)	
	
	img = stringextract('"aspect16x9"', '"title"', item)		# Bild
	# PLog(img)	# Debug
	img =  stringextract('"src":"', '"', img)
	img = img.replace('{width}', '720')
	
	target =  stringextract('"target":', '}', item)	# Ziel-Url mit Streamquellen
	url =  stringextract('"href":"', '"', target)	
	ID =  stringextract('"id":"', '"', target)
	
	tag = u"Staffel: %s | Folge: %s\nDauer: %s | FSK: %s | %s | Hersteller: %s | %s" %\
		(season, episode, dauer, fsk, end, producer, Type)
	
	title = unescape(title)
	summ = repl_json_chars(descr)
	PLog('Satz3:');
	PLog(title); PLog(url); PLog(img); PLog(tag); PLog(summ[:80]);
	PLog(season); PLog(weburl);

	return title, url, img, tag, summ, season, weburl, ID
		
#----------------------------------------------
# wie ZDF_getStrmList
# erzeugt / aktualsiert strm-Dateien für die komplette Liste 
# Ermittlung Streamquellen für api-call
# Ablauf: Seite path laden, Blöcke wie ARD_FlatListEpisodes
#	iterieren -> ZDF_FlatListRec -> ZDF_getApiStreams (Streamquelle 
#	ermitteln -> 
# Nutzung strm-Modul: get_strm_path, xbmcvfs_store
# Cache-Verzicht, um neue Folgen nicht zu verpassen.
#
def ARD_getStrmList(path, title, ID="ARD"):
	PLog("ARD_getStrmList:")
	title_org = title
	list_path = path
	icon = R(ICON_DIR_STRM)
	FLAG_OnlyUrl	= os.path.join(ADDON_DATA, "onlyurl")
	import resources.lib.strm as strm
	
	page, msg = get_page(path=path)
	if page == '':
		msg1 = "Fehler in ARD_getStrmList:"
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return

	pos = page.find("synopsis")							# Serien-Titel (vorgegeben)
	list_title =  stringextract('"title":"', '"', page[pos:])			
	list_title = transl_json(list_title)
	PLog("list_title: " + list_title)
	
	#---------------------								# wie ZDF_getStrmList
	strm_type = strm.get_strm_genre()					# Genre-Auswahl
	if strm_type == '':
		return
	strmpath = strm.get_strm_path(strm_type)			# Abfrage Zielverz. != Filme
	if os.path.isdir(strmpath) == False:
		msg1 = "Zielverzeichnis existiert nicht."
		msg2 = u"Bitte Settings überprüfen."
		MyDialog(msg1, msg2, '')
		return
	
	#---------------------								# Abfrage Version
	versions = [u'Normalfassung', u'Hörfassung', u'Originalversion (OV)']
	if page.find(u'(OV)') < 0 and page.find(u'(Originalversion)') < 0: 	# Varianten OV
		versions.remove(u'Originalversion (OV)')
	if page.find(u'Hörfassung') < 0:
		versions.remove(u'Hörfassung')

	vers='Normalfassung'								# Default: Normalfassung
	if u'Hörfassung' in page or u'(OV)' in page or 'Originalfassung' in page or '(Originalversion)' in page:	
		if SETTINGS.getSetting('pref_usefilter') == 'true':	# Abfrage Audiodeskription / Originalfassung
			head = u"bitte Filter wählen"
			ret = xbmcgui.Dialog().select(head, versions)
			if ret < 0:
				PLog("Abbruch")
				return							
			v = versions[ret]; 
			vers = py2_decode(v)	
	#---------------------										
		
	fname = make_filenames(list_title)					# Abfrage Unterverzeichnis Serie
	strmpath = os.path.join(strmpath, fname)
	PLog("list_strmpath: " + strmpath)		
	head = u"Unterverzeichnis für die Serie"
	msg1 = u"Das Addon legt für die Serie folgendes Unterverzeichnis an:"
	if os.path.isdir(strmpath):		
		msg1 = u"Das Addon verwendet für die Serie folgendes Unterverzeichnis:"
	msg2 = u"[B]%s[/B]" % fname
	msg3 = u"Ein vorhandenes Verzeichnis wird überschrieben."
	ret = MyDialog(msg1, msg2, msg3, ok=False, cancel='Abbruch', yes='OK', heading=head)
	if ret != 1:
		return
	if os.path.isdir(strmpath) == False:
		os.mkdir(strmpath)								# Verz. erzeugen, falls noch nicht vorh.
		list_exist=False
	else:
		list_exist=True

	#---------------------
	cnt=0; skip_cnt=0
	items = blockextract('availableTo":', page)					# Videos
	for item in items:
		if "Folge " in item == False:
			continue
		title, url, img, tag, summ, season, weburl, ID = ARD_FlatListRec(item, vers) # Datensatz
		if title == '':											# skipped
			continue
	
		fname = make_filenames(title)							# Zieldatei hier ohne Dialog
		PLog("fname: " + fname)
		if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
			f = os.path.join(strmpath, fname, "%s.nfo" % fname)
		else:
			f = os.path.join(strmpath, "%s.nfo" % fname)
		PLog("f: " + f)
		if os.path.isfile(f):									# skip vorh. strm-Bundle
			msg1 = u'schon vorhanden:'
			msg2 = title
			xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
			PLog("skip_bundle: " + f)
			skip_cnt=skip_cnt+1
			continue
		else:
			msg1 = u'neues strm-Bündel:'
			msg2 = title
			PLog("%s %s" % (msg1, msg2))
			xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
					
		Plot = "%s\n\n%s" % (tag, summ)
		msg1 = u'Suche Streamquellen'
		msg2 = title
		xbmcgui.Dialog().notification(msg1,msg2,icon,500,sound=False)
		open(FLAG_OnlyUrl, 'w').close()							# Flag PlayVideo_Direct: kein Videostart
		ARD_get_strmStream(url, title, img, Plot) 				# Streamlisten bauen, Ablage Url
		url = RLoad(STRM_URL, abs_path=True)					# abgelegt von PlayVideo_Direct
		PLog("strm_Url: " + str(url))
		
		Plot = "%s\n\n%s" % (tag, summ)
		ret = strm.xbmcvfs_store(strmpath, url, img, fname, title, Plot, weburl, strm_type)
		if ret:
			cnt=cnt+1


	#------------------
	PLog("strm_cnt: %d" % cnt)		
	msg1 = u'%d neue STRM-Datei(en)' % cnt
	if cnt == 0:
		msg1 = u'STRM-Liste fehlgeschlagen'
		if list_exist == True:
			msg1 = u'STRM-Liste unverändert'
	msg2 = list_title
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		
	#------------------													# Liste synchronisieren?
	# Format: Listen-Titel ## lokale strm-Ablage ##  ext.Url ## strm_type
	item = "%s##%s##%s##%s"	% (list_title, strmpath, list_path, strm_type)
	PLog("item: " + item)
	synclist = strm.strm_synclist(mode="load")							# "strm_synclist"
	if exist_in_list(item, synclist) == True:	
		msg1 = "Synchronsisation läuft"
		msg2 = list_title
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		PLog(msg1)
	else:
		if cnt > 0:
			sync_hour = strm.strm_tool_set(mode="load")	# Setting laden
			head = u"Liste synchronisieren"
			msg1 = u"Soll das Addon diese Liste regelmäßig abgleichen?"
			msg2 = u"Intervall: %s Stunden" % sync_hour	
			ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Nein', yes='OK', heading=head)
			if ret == 1:												# Liste neu aufnehmen
				strm.strm_synclist(mode="save", item=item)
				line = "%6s | %15s | %s..." % ("NEU", list_title[:15], "Liste neu aufgenommen")
				strm.log_update(line)
				line = "strm-Serie|%s|%s" % (list_title, vers)
				Dict("store", 'strmListVersion_%s' % list_title, line) # load: do_sync_ARD 

	return
		
#----------------------------------------------
# Ermittlung Streamquellen für ARD_getStrmList
#	ähnlich ZDF_getApiStreams
# Ablauf: Seite url laden, HLS_List + MP4_List
#	bauen, strm-Url via PlayVideo_Direct ermitteln
#	(dort Abgleich Settings pref_direct_format +
#	pref_direct_quality, Ablage STRM_URL)
# Plot: tag + summ von Aufrufer zusammengelegt
# 17.05.2024 Angleichung Web-api in ARDStartSingle
#
def ARD_get_strmStream(url, title, img, Plot):
	PLog('ARD_get_strmStream:'); 
	
	page, msg = get_page(url + "&mcV6=true")				# wie ARDStartSingle
	if page == '':	
		msg1 = "Fehler in ARD_get_strmStream: %s"	% title
		PLog("%s | %s" % (msg1, msg))	
		return
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Python3 geändert
	page= page.replace('+++\\n', '+++ ')					# Zeilentrenner ARD Neu
			
	# -----------------------------------------				# Extrakt Videoquellen
	PLog(page[:80])								
	elements = page.count('"availableTo":')					# möglich: Mehrfachbeiträge, Bsp. Hörfassung, Teaser
	PLog('elements: %d' % elements)	
	page = json.loads(page)
	mediaCollection = page["widgets"][0]["mediaCollection"]

	try:													# StreamArray
		PLog("get_StreamArrays")
		slen = len(mediaCollection["embedded"]["streams"])
		PLog("StreamArrays: %d" % slen)
		StreamArray_0=[]; StreamArray_1=[]					
		StreamArray_0 = mediaCollection["embedded"]["streams"][0]		# "kind": "main", "kindName": "Normal",
		if slen > 1:
			StreamArray_1 = mediaCollection["embedded"]["streams"][1]	# "kind": "sign-language", "kindName": "DGS", 						
		PLog(str(StreamArray_0)[:80])								
		PLog(str(StreamArray_1)[:80])								
	except Exception as exception:
		PLog(str(exception))
		msg1 = u'keine Videoquellen gefunden'
		PLog(msg1)
		# MyDialog(msg1, '', '')										# hier ohne Dialog
		return	
	
	# Formate siehe StreamsShow								# HLS_List + MP4_List anlegen, ohne HBBTV
	#	generisch: "Label |  Auflösung | Bandbreite | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	call = "ARD_get_strmStream"
	HBBTV_List=''											# nur ZDF
	HLS_List = ARDStartVideoHLSget(title, StreamArray_0, call, StreamArray_1)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = ARDStartVideoMP4get(title, StreamArray_0, call, StreamArray_1)	# MP4
	PLog("MP4_List: " + str(MP4_List)[:80])

	# Abgleich Settings, Ablage STRM_URL
	thumb = img
	PlayVideo_Direct(HLS_List, MP4_List, title, thumb, Plot) 
	
	return
	
#---------------------------------------------------------------------------------------------------
# Hinw.: in textviewer für monospaced Font die Kodi-Einstellung
#	"Standardwert des Skins" wählen
# Quelle: https://www.ard-text.de/index.php?page=100
# 22.08.2023 Umstellung auf HBBTV-Variante, Quellen:
#	vtx.ard.de/app/index.html?html5=1 -> index.php ->
#	vtx.ard.de/data/ard/100.json
#
def ARD_Teletext(path=""):
	PLog('ARD_Teletext:')
	
	base = "http://vtx.ard.de/data/ard/%s.json"
	if path == "":
		path = base % "100"
	aktpg = re.search(r'data/ard/(.*?).json', path).group(1)
	PLog("aktpg: %s" % aktpg)
	
	img = R(ICON_MAIN_ARD)
	thumb = R("teletext_ard.png")
	Seiten = ["Startseite|100", "Nachrichten|101", "Sport|200",
			"Programm|300", "Kultur|400", "Wetter|171", "Inhalt A-Z|790",
		]

	page, msg = get_page(path=path)	
	if "Error 404" in msg:										# hier bei Fehler Seitenkorrektur
		msg1 = u'Seite %s' % aktpg
		msg2 = u'nicht verfügbar'
		icon = thumb		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("coreccted: %s -> %s" % (aktpg, "100"))
		path = base % "100"
		aktpg = "100"
		page, msg = get_page(path=path)	
	PLog(len(page))
		
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')			# Home-Button

	#------------------------------------------------			# Body
	PLog("get_content:")
	ARD_Teletext_extract(page, aktpg)	
	
	#------------------------------------------------------	
		
	prevpg = int(aktpg) - 1										# vorwärts/rückwärts
	nextpg = int(aktpg) + 1
	if prevpg < 100:
		prevpg = 899
	if nextpg > 899:
		nextpg = 100
	
	title = u"rückwärts zu [B]%s[/B]"	% prevpg
	thumb = R("icon-previos.png")
	href = base % prevpg
	fparams="&fparams={'path': '%s'}" % quote(href)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARD_Teletext", 
		fanart=img, thumb=thumb, fparams=fparams)			
			
	title = u"vorwärts zu [B]%s[/B]"	% nextpg
	thumb = R("icon-next.png")
	href = base % nextpg
	fparams="&fparams={'path': '%s'}" % quote(href) 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARD_Teletext", 
		fanart=img, thumb=thumb, fparams=fparams)
		
	#------------------------------------------------------		# prominente Seiten
	thumb = R("teletext_ard.png")
	for item in Seiten:
		title, pgnr = item.split("|")
		title = "[B]Direkt %s[/B]: %s" % (pgnr, title)	
		href = base % pgnr
		fparams="&fparams={'path': '%s'}" % quote(href) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARD_Teletext", 
			fanart=img, thumb=thumb, fparams=fparams)
	#------------------------------------------------------		# manuelle Eingabe
	title = u"Seitenzahl manuell eingeben"
	basepath = base 
	func = "resources.lib.ARDnew.ARD_Teletext" 
	fparams="&fparams={'func': '%s', 'basepath': '%s'}" % (func, quote(basepath))
	addDir(li=li, label=title, action="dirList", dirID="ZDF_Teletext_setPage", 
		fanart=img, thumb=thumb, fparams=fparams)	
							
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------------------------
# Bsp.:
# 	716 Kurse: 		mehrere Tabellen (Unterseiten, hier zusammengefasst) 
#	173 Wetter D:	Text + Tabelle 
#	182,175 Wetter: Tabellen 
#	176 Wetter:		Image
#
def ARD_Teletext_extract(page, aktpg):
	PLog('ARD_Teletext_extract: '+ aktpg)
	
	base = "http://vtx.ard.de/data/ard/%s.json"
	thumb = R("teletext_ard.png")
	img = R(ICON_MAIN_ARD)
	PLog(page[:220])
	try:
		atoz=False
		obj = json.loads(page)
		refTitle = obj["refTitle"]
		subs = obj["sub"]
		PLog("subs: %d" % len(subs))							# sub häufig 1x
	except Exception as exception:
		PLog("json_error: " + str(exception))

	PLog(str(subs[0])[:80])
	max_length=50												# ähnlich Original (abhäng. vom Font)
	add_header=""												# Zusatztitel textviewer
	
	#---------------------------------------------------
	if 'ctype":"image' in page:									# Bilder: Wetter, Trends, ..
			PLog("get_image")
			img = subs[0]["c"][0]["img"]
			img = img[3:]										# "../images/..
			img = "http://vtx.ard.de/" + img
			fname = os.path.join("%s/teletext.png") % DICTSTORE	
			PLog("fname: " + fname)
			urlretrieve(img, fname)
			ardundzdf.ZDF_SlideShow(fname, single="True")	
			return	
		
	#---------------------------------------------------
	if 'ctype":"atoz' in page:									# abweichend A-Z	
		PLog("get_atoz")
		new_lines=[]											# Sammler für textviewer									
		items = subs[0]["c"][0]["items"]
		for item in items:
			links = item["links"]								# skip Gruppenheader wie WXYZ
			PLog("links: %d" % len(links))
			for  linkitem in links:
				txtRight=""
				link  = linkitem["link"]
				myline = link["t"]
				if "pg" in link:
					pg = link["pg"]								# Pagenr			
					txtRight = str(pg)							# txtRight nicht in link
				else:
					myline = "** %s" % myline				#Index-Zeile kennzeichnen (ohne Link)
				
				myline = cleanhtml(myline)											
				new_lines = ARD_Teletext_Wrap(new_lines, myline, max_length, txtRight)
				
		txt =  "\n".join(new_lines)								# Ausgabe Textviewer
		PLog(txt)
		if txt:		
			title = "Seite %s | %s" % (aktpg, refTitle)
			if add_header:
				title = "%s\n%s\n" % (title, add_header)	
			xbmcgui.Dialog().textviewer(title, txt, usemono=True)
		return	
	
	#---------------------------------------------------

	sub_cnt=0
	new_lines=[]												# Sammler für textviewer									
	for sub in subs:											# Text, Link, Tabelle
		PLog("getsubs")
		PLog("sub_cnt: %d" % sub_cnt)
		header = sub["header"]
		css = sub["css"]
		PLog("css: %s" % css)
		clines = sub["c"]							
		PLog("clines: %d" % len(clines))
		for cline in clines:
			ctype = cline["ctype"]
			myline=""; txtRight=""
			if ctype == "table":								# Tabelle zeilenweise hier auswerten
				trs = cline["tr"] 
				PLog("trs: %d" % len(trs))
				for tr in trs:
					myline="";
					tds = tr["td"]; 								# Spalten, z.B.: Ort, Wetter, Temp
					
					td_list=[]; td_anz=len(tds); 
					td_width = int(max_length/len(tds))				# Spaltenbreite abh. von Anz. Spalten
					
					for td in tds:									# Spalten -> 1 Zeile
						td_list.append(td["t"])

					if td_list[-1] == "°C":							# Temp 2-stellig mögl., Bsp. 182	
						td_list[-2] = td_list[-2] + td_list[-1]		# -> 21 + °C
						td_list.pop()								# remove last lement
						td_width=int(max_length/(len(tds)-1))		# Spaltenbreite anpassen
						PLog("td_width_new: %d" % td_width)	

					for td in td_list:
						td = "%*s" % (td_width, td[:td_width])
						myline = "%s %s" % (myline, td)
					#PLog("tr_line: %s" % myline)
					myline = cleanhtml(myline); myline = unescape(myline)
					new_lines.append(myline)
					
			else:													# keine Tabelle
				myline, txtRight = ARD_Teletext_get_cline(cline, ctype, max_length)	
			PLog("myline: %s, txtRight: %s" % (myline, txtRight))
			myline = cleanhtml(myline); myline = unescape(myline)
			if myline.startswith("\n"):							# LF nach oben
				new_lines.append("")
				myline = myline.replace("\n", "")	
		
			if  "table" not in ctype: 							# Tabellenzeile ohne ARD_Teletext_Wrap
				new_lines = ARD_Teletext_Wrap(new_lines, myline, max_length, txtRight)
			if myline.endswith("\n"):							# LF nach unten
				new_lines.append("")
				myline = myline.replace("\n", "")
					
		sub_cnt=sub_cnt+1
		if sub_cnt < len(subs):									# LF für Unterseiten in selben Textviewer
			new_lines.append("")
													

	#---------------------------------------------------
	
	txt =  "\n".join(new_lines)									# Ausgabe Textviewer
	PLog(txt)
	if txt:		
		title = "Seite %s | %s" % (aktpg, header)
		if add_header:
			title = "%s\n%s\n" % (title, add_header)	
		xbmcgui.Dialog().textviewer(title, txt, usemono=True)
	else:
		msg1 = u'Seite %s' % aktpg
		msg2 = u'Inhalt nicht darstellbar'
		icon = thumb		
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
		PLog("%s: %s" % (msg1, msg2))
					
	return

#----------------------------------------------
# Auswertung Text, EPG, Tabelle, getrennte Rückgabe
#	Zeile und pagenr
# bei Bedarf Zeilenumbruch nach oben / nach unten einfügen
#
def ARD_Teletext_get_cline(cline, ctype, max_length):
	PLog('ARD_Teletext_get_cline: ' + ctype)
	txtRight=""; myline=""
	
	if ctype == "text":
		myline = cline["t"]									# einf. Textzeile
		return myline, txtRight
			
	if ctype == "spacer":							# Trennzeile
		myline = ""
	if ctype == "title":							# auch als Trennzeile gesehen 171
		myline = cline["t"]
	if ctype == "text":	
		myline = cline["t"]
		myline = myline.replace("<br/>", "\n")		#  LF nach unten
	if ctype == "epglink":
		epg = cline["epg"][0]
		t = epg["t"]
		if t.strip().startswith("Jetzt im"):		# LF nach oben
			myline ="\n%s" % myline
		tim = epg["tim"]
		t = "%s " % t
		myline = "%s%s %s" % (myline, tim, t)		# optisch fehlt hier ein spacer
		if "pg" in cline:
			pg = cline["pg"]							# Pagenr			
			txtRight = str(pg)						# txtRight nicht in epglink
	if ctype == "link":
		link = cline["link"]
		t = link["t"]
		myline = t
		myline = myline.replace("<br/>", "\n")		#  LF nach unten
		if "pg" in link:
			pg = link["pg"]							# Pagenr
			# txtRight = link["txtRight"]			# txtRight kann fehlen
			txtRight = str(pg)
	if ctype == "list":	
		clist = cline["li"]
		for c in clist:								# Bsp. mehrz. EPG-Texte zu Sendung
			myline = "%s%s" % (myline, c)
	
	return myline, txtRight
										
#----------------------------------------------
# Zeilenumbruch + pagenr rechtsbündig einfügen
#
def ARD_Teletext_Wrap(new_lines, myline, max_length, txtRight):
	PLog('ARD_Teletext_Wrap: ')
	txtRight=str(txtRight)
	mylen=max_length
	if txtRight:
		mylen = max_length-len(txtRight)-1			# max-Länge ohne txtRight
	#PLog("new_lines: %d" % len(new_lines)); PLog("txtRight: %s" % txtRight); 
	#PLog("max_length: %d" % max_length); PLog("mylen: %d" % mylen);
	#("myline %d: %s" % (len(myline), myline))
	
	if len(myline) == 0:							# Spacer, LF
		new_lines.append(myline)
		return new_lines
	
	
	if len(myline) <= mylen:
		newline = myline
	else:
		words = myline.split()
		newline=""
		for word in words:
			if len(newline) + len(word) + 1 > mylen:	# 1 Blank
				new_lines.append(newline.strip())
				newline=""
			newline = "%s %s" % (newline, word)
			newline = newline.strip()
	
	#PLog("newline: " + newline)		
	if txtRight:									# letzte Zeile: pagenr rechtsbündig
		fill_len = (max_length - len(newline)) 		# Anzahl Blanks zur rechtsbündigen Pagenr txtRight
		PLog("fill_len: %d, max_length %d-%d myline +4=%d" % (fill_len, max_length, len(myline), max_length-len(myline)+4))
		newline = "%s %s" % (newline, txtRight.rjust(fill_len))
		
	new_lines.append(newline)	
	return new_lines
	
####################################################################################################
#							ARD Retro www.ardmediathek.de/ard/retro/
#				als eigenst. Menü, Inhalte auch via Startseite/Menü/Retro erreichbar
# 07.04.2023 Direkt-Call in Main_NEW, ARDRetro() nach Wechsel zu api-Call entfernt
####################################################################################################

####################################################################################################
#						ARD Sport (neu) www.ardmediathek.de/ard/sport/
#				als eigenst. Menü, Inhalte auch via Startseite/Menü/Sport erreichbar
# 07.04.2023 Direkt-Call in Main_NEW, ARDSportneu() nach Wechsel zu api-Call entfernt
####################################################################################################

#---------------------------------------------------------------------------------------------------
# Auswertung für ARDStartRubrik + ARDPagination + ARDSearchnew 
#	Mehrfach- und Einzelsätze
# mark: farbige Markierung in title (z.B. query aus ARDSearchnew) 
# Seiten sind hier bereits senderspezifisch.
# Aufrufe Direktsprünge
# 07.04.2023 skip Subrubrik Übersicht (aktuelle Seite)
# 14.04.2023 get_page_content -> get_json_content 
# gelöscht: def get_page_content(li, page, ID, mark='', mehrzS=''): 
#		
#---------------------------------------------------------------------------------------------------
# 14.04.2023 get_page_content -> get_json_content
# 06.12.2023 Auswertung EPG in ARDVerpasst_get_json
#
def get_json_content(li, page, ID, mark='', mehrzS='', homeID=""): 
	PLog('get_json_content: ' + ID); PLog(mark)
	ID_org=ID; PLog(type(page)); 
	PLog(str(py2_encode(page))[:80])

	CurSender = ARD_CurSender()									# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)												#-> href
	mediatype=''; pagetitle=''
	li2 = xbmcgui.ListItem()									# mediatype='video': eigene Kontextmenüs in addDir							
	
	if "dict" not in str(type(page)):
		page_obs = json.loads(page)
	else:
		page_obs = page

	try:
		if "teasers" in page_obs:
			obs =page_obs["teasers"]
		if "widgets" in page_obs:
			obs =page_obs["widgets"][0]["teasers"]
	except Exception as exception:
		PLog("teasers_not_found: " + str(exception))			# notification s.u.
		obs=[]	
	PLog("obs: %d" % len(obs))
	
	# typ-Info Einzelbeträge: ["live", "event", "broadcastMainClip",
	#				"ondemand", "poster"]
	cnt=0	
	for s in obs:
		PLog("Mark10")
		PLog(str(s)[:60])
		uhr=''; ID=ID_org; duration='';	summ=''; availableTo='';
		matRat="Ohne"
		typ = s["type"]
		if "availableTo" in s:
			availableTo = s["availableTo"]

		typ = s["type"]
		if "duration" in s or "broadcastedOn" in s:				# broadcastedOn: Livestream
			mehrfach = False									# Default Einzelbetrag
		else:
			mehrfach = True										# Default weitere Rubriken		

		try:
			imgsrc 	= s["images"]["aspect16x9"]
			img 	= imgsrc["src"]
			img = img.replace('{width}', '640')
			img_alt = 	imgsrc["alt"]
		except:
			img = R(ICON_DIR_FOLDER)							# Bsp.: Subrubriken
		
		title = s["longTitle"]
		title = repl_json_chars(title)
		if mark:												# Markierung Suchbegriff 						
			PLog(title); PLog(mark)
			title = title.strip() 
			title = make_mark(mark, title, "", bold=True)		# -> util
			
		if mehrzS:												# Setting pref_more
			title = u"[B]Mehr[/B]: %s" % title	
		if mark == "Subrubriken":
			if title.startswith(u"Übersicht"):					# skip Subrubrik Übersicht (rekursiv, o. Icons) 
				PLog("skip_Übersicht")
				continue				
		
		href = 	s["links"]["target"]["href"]
		if ID != "Livestream" and mehrfach == False:			# Einzelbeiträge außer Live
			PLog("eval_video:")	
			if "publicationService" in s:
				pubServ = s["publicationService"]["name"]
			else:
				pubServ = s["show"]["publisher"]["name"]
			if "maturityContentRating" in s:
				matRat = s["maturityContentRating"]
				matRat = matRat.replace('NONE', 'Ohne')
			if "duration" in s:
				duration = s["duration"]						# sec-Wert
				duration = seconds_translate(duration)			# 0:15
			if duration and pubServ:										
				duration = u'Dauer %s | [B]%s[/B]' % (duration, pubServ)
			if 	matRat:
				if duration == '':
					duration = "Dauer unbekannt"
				duration = u"%s | FSK: %s\n" % (duration, matRat)
			
			# synopsis, shortSynopsis, longSynopsis häufig identisch
			if "show" in s:		
				if s["show"]:									# null?
					summ = s["show"]["synopsis"]				# Zusammenfassung
					pagetitle = s["show"]["title"]				# -> full_shows
			PLog(summ[:60])	
			if summ == None:
				summ = ""
			summ = repl_json_chars(summ)
				
			verf = availableTo									# s.o.
			if "live" not in typ:								# nicht in Livestreams
				if verf == None:
					verf=""
				verf = time_translate(verf, day_warn=True)
				if verf:
					summ = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s" % (verf, summ)
				if "broadcastedOn" in s:
					pubDate = s["broadcastedOn"]
					pubDate = time_translate(pubDate)
					pubDate = u" | Sendedatum: [COLOR blue]%s Uhr[/COLOR]\n\n" % pubDate	
					if u'erfügbar bis' in summ:	
						summ = summ.replace('\n\n', pubDate)	# zwischen Verfügbar + summ  einsetzen
					else:
						summ = "%s%s" % (pubDate[3:], summ)
				if duration and summ:
					summ = "%s\n%s" % (duration, summ)	
		else:
			summ = title
			
		if "Sendedatum:" in summ:	
			uhr = summ.split(' ')[-2]
		summ = repl_json_chars(summ)	
			
		# ARDVerpasstContent: Zeit im Titel, Langfass. tagline:
		if 'broadcast' in typ and uhr:							# EPG: broadcastMainClip								
			title = "[COLOR blue]%s[/COLOR] | %s" % (uhr, title) 			
			pubServ = s["publicationService"]["name"]							# publicationService (Sender)
			if pubServ:
				summ = "%sSender: %s" % (summ, pubServ)		
	
		PLog('Satz:');
		PLog(mehrfach); PLog(typ); PLog(title); PLog(href); PLog(img); 
		PLog(summ[:60]); PLog(duration); PLog(availableTo);
		
		if mehrfach:
			summ = "Folgeseiten"
			href=py2_encode(href); title=py2_encode(title); 
			fparams="&fparams={'path': '%s', 'title': '%s', 'homeID': '%s'}" % (quote(href), quote(title), homeID)
			addDir(li=li2, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", \
				fanart=img, thumb=img, fparams=fparams, summary=summ, mediatype='')	
			cnt=cnt+1
		else:
			PLog("eval_settings:")	
			if pagetitle == '':									# pagetitle -> title_samml
				if "homepage" in s:								# Home-Titel kann fehlenden Sendungstitel enthalten
					pagetitle = s["homepage"]
					pagetitle = stringextract('"title":"', '"', pagetitle)
			title_samml = "%s|%s" % (title, pagetitle)			# Titel + Seitentitel (A-Z, Suche)
			if SETTINGS.getSetting('pref_mark_full_shows') == 'true':
				if ID != "Search":								# Vorrang Suchmarkierung vor full_shows					
					if "duration" in s:
						dur = seconds_translate(s["duration"])	# 27.06.2023
						title = ardundzdf.full_shows(title, title_samml, summ, dur, "full_shows_ARD")	

			# 01.10.2024 s.o. synopsis, aber anders als beim ZDF Inhaltstext beim den Quellen (api):
			if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
				summ_new = get_summary_pre(path=href, ID='ARDnew', duration=duration)  # Modul util
				if 	summ_new:
					summ = summ_new
					
			if SETTINGS.getSetting('pref_usefilter') == 'true':		# Ausschluss-Filter
				filtered=False
				for item in AKT_FILTER: 
					if up_low(item) in py2_encode(up_low(str(s))):
						filtered = True
						break		
				if filtered:
					PLog('filtered_7: <%s> in %s ' % (item, title))
					continue								
					
			if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
				li=li2												# eigene Kontextmenüs
				mediatype='video'
			
			if typ == "live"  or typ == "event" :					# Livestream in Stage od. ARD Sport
				ID = "Livestream"								
				summ = "%s | [B]Livestream[/B]" % summ
			else:
				ID=ID_org
			PLog("Satz_cont3: typ: %s, ID: %s" % (typ, ID))
			
			summ_par = summ.replace('\n', '||')
			href=py2_encode(href); title=py2_encode(title); summ_par=py2_encode(summ_par);
			fparams="&fparams={'path': '%s', 'title': '%s', 'summary': '%s', 'ID': '%s','homeID': '%s'}" %\
				(quote(href), quote(title), quote(summ_par), ID, homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, thumb=img, 
				fparams=fparams, summary=summ, mediatype=mediatype)	
			cnt=cnt+1
	
	if cnt == 0:
		msg1 = 	"Nichts gefunden:"							# notification, hier ohne Sender
		msg2 = "weder Folgeseiten noch Videos."	
		icon = R(ICON_INFO)
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000, sound=False)			
		
	return

#---------------------------------------------------------------------------------------------------
# Ermittlung der Videoquellen für eine Sendung - hier Aufteilung Formate Streaming + MP4
# Bei Livestreams (m3u8-Links) verzweigen wir direkt zu SenderLiveResolution.
# Videodaten unterteilt in _plugin":0 und _plugin":1,
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
# 14.02.2023 HBBTV-Quellen (http://tv.ardmediathek.de/dyn/get?id=video%3A..)
# 14.05.2024 Nutzung api-Web-Quellen für alle Streams (bisher nur vtt-Datei) -
#	ARDStartVideoWebUTget entfernt,
#
def ARDStartSingle(path, title, summary, ID='', mehrzS='', homeID=''): 
	PLog('ARDStartSingle: %s' % ID);
	PLog(path)
	title_org=title;
	icon = R("ard-mediathek.png")

	headers=''
	# Header für Verpasst-Beiträge (ARDVerpasstContent -> get_json_content)
	if ID == 'EPG' or ID == 'A-Z':											
		headers = "{'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma':'no-cache',\
			'Expires': '0'}"

	path = path + "&mcV6=true"								# api-Web-Quelllen
	page, msg = get_page(path, header=headers)
	if page == '':	
		msg1 = "Fehler in ARDStartSingle: %s"	% title
		msg2=msg
		MyDialog(msg1, msg2, '')	
		xbmcplugin.endOfDirectory(HANDLE)
	PLog(len(page))
	page= page.replace('\\u002F', '/')						# 23.11.2019: Ersetzung für Python3 geändert
	page= page.replace('+++\\n', '+++ ')					# Zeilentrenner ARD Neu

	elements = page.count('"availableTo":')					# möglich: Mehrfachbeiträge, Bsp. Hörfassung, Teaser
	PLog('elements: %d' % elements)	

	IsPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)') # 'true' / 'false'
	PLog("IsPlayable: %s" % IsPlayable)	
	if elements > 0:
		if page.find('"durationSeconds"') == 0:				# ohne Länge keine Quellen -> Abbruch
			msg1 = u"[B]%s[/B] enthält keine Videoquellen"	% cleanmark(title)
			msg2 = u"Mögliche Ursache: Altersbeschränkung"
			msg3 = u"Eine Suche in MediathekViewWeb könnte helfen."
			MyDialog(msg1, msg2, msg3)	
			return											# hebt IsPlayable auf (Player-Error: skipping ..)			
			
	if elements == 0:										# möglich: kein Video (dto. Web)
		msg1 = u'keine Beiträge zu %s gefunden'  % title
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)	
	PLog("anz_plugin: %d" % page.count("_plugin"))			# todo: Relevanz _plugin=2 prüfen
	
	page = json.loads(page)
	PLog(str(page)[:80])								
	try:													# img, geoblock + Untertitel
		PLog("get_img")
		image =  page["widgets"][0]["image"]
		img = image["src"]
		img_alt = image["alt"]								# n.v.
		img = img.replace('{width}', '640')
		geoblock = page["widgets"][0]["geoblocked"]			# false, true
		if geoblock:										# Geoblock-Anhang für title, summary
			geoblock = ' | Geoblock: JA'
			title = title + geoblock
		else:
			geoblock = ' | Geoblock: nein'
		PLog("geoblock: %s, img: %s" % (geoblock, img))	
		
		PLog("get_subtitles")
		mediaCollection = page["widgets"][0]["mediaCollection"]
		subtitles = mediaCollection["embedded"]["subtitles"]
		PLog(str(subtitles)[:80])								
		if subtitles:										# leer od. >= 1, 0: normal
			sources = subtitles[0]["sources"]				# normal
			if len(sources) > 1:				
				sub_path = sources[1]["url"]				# 1: vtt
			else:
				sub_path = sources[0]["url"]				# 0: xml
		else:
			sub_path=""	
	except Exception as exception:
		PLog(str(exception))
		sub_path=""
	PLog("sub_path: " + sub_path)
	
	try:
		PLog("get_features")								# DGS, AD, ..
		features = page["widgets"][0]["binaryFeatures"]
		PLog(features)
		if features:
			msg1 = u"weitere Formate" 
			msg2 = " | ".join(features)
			xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)			
			
	except Exception as exception:
		PLog(str(exception))
		PLog("no_features_found")
		features=""
			
	try:													# StreamArray
		PLog("get_StreamArrays")
		slen = len(mediaCollection["embedded"]["streams"])
		PLog("StreamArrays: %d" % slen)
		StreamArray_0=[]; StreamArray_1=[]					
		StreamArray_0 = mediaCollection["embedded"]["streams"][0]		# "kind": "main", "kindName": "Normal",
		if slen > 1:
			StreamArray_1 = mediaCollection["embedded"]["streams"][1]	# "kind": "sign-language", "kindName": "DGS", 						
		PLog(str(StreamArray_0)[:80])								
		PLog(str(StreamArray_1)[:80])								
	except Exception as exception:
		PLog(str(exception))
		msg1 = u'keine Videoquellen gefunden'
		PLog(msg1)
		MyDialog(msg1, '', '')
		return	
	
	li = xbmcgui.ListItem()
	if ID == "ARDRetroStart":
		li = home(li, ID=NAME)								# Home-Button -> Hauptmenü
	else:
		if ID != 'Livestream':								# ohne home - Nutzung durch Classic
			if homeID:
				li = home(li, ID=homeID)
			else:
				li = home(li, ID='ARD Neu')						# Home-Button
			
	# Livestream-Abzweig, Bsp. tagesschau24:					# entf. mit Umstellung auf api-Web	
	#	json-Struktur wie Videos	
	# -----------------------------------------			# Extrakt Videoquellen
	# 17.02.2023 Umstellung string -> json
	# Formate siehe StreamsShow							# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Auflösung | Bandbreite | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	call = "ARDStartSingle"
	HLS_List = ARDStartVideoHLSget(title, StreamArray_0, call, StreamArray_1)	# Extrakt HLS
	PLog("HLS_List: " + str(HLS_List)[:80])
	HBBTV_List = ARDStartVideoHBBTVget(title, path)								# HBBTV (MP4), eigene Quellen
	PLog("HBBTV_List: " + str(HBBTV_List)[:80])
	MP4_List = ARDStartVideoMP4get(title, StreamArray_0, call, StreamArray_1)	# MP4
	Dict("store", 'ARDNEU_HLS_List', HLS_List) 
	Dict("store", 'ARDNEU_HBBTV_List', HBBTV_List) 
	Dict("store", 'ARDNEU_MP4_List', MP4_List) 
	PLog("download_list: " + str(MP4_List)[:80])
	
	if len(HLS_List) == 0 and len(HBBTV_List) == 0 and len(MP4_List) == 0:
		msg1 = "keine Streamingquelle gefunden: %s"	% title
		PLog(msg1)
		MyDialog(msg1, '', '')	
		return li	
	#----------------------------------------------- 							# Livestream-Abzweig, Bsp. tagesschau24:
	if "LIVESTREAM" in page["coreAssetType"]:
		href = HLS_List[0].split("**")[-1]										# Das Erste#https://...master.m3u8
		href = href.split("#")[-1]
		PLog('Livestream_Abzweig: ' + href)
		return PlayVideo(href, title, img, summary, sub_path=sub_path, live="true")		
	
	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	PLog('Lists_ready:');
	Plot = "Titel: %s\n\n%s" % (title_org, summary)				# -> build_Streamlists_buttons
	PLog('Plot:' + Plot)
	thumb = img; ID = 'ARDNEU';
		
	HOME_ID = "ARD Neu"
	if homeID:
		HOME_ID = homeID
	played_direct = ardundzdf.build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)

	# -----------------------------------------		# mehr (Videos) zur Sendung,
	if mehrzS or played_direct:						# skip bei direktem Aufruf
		return										# 13.11.2021 notw. für Rückspr. z. Merkliste
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

	PLog('Serien_Mehr_Test')
	# zusätzl. Videos zur Sendung (z.B. Clips zu einz. Nachrichten). 
	# 23.04.2024 Serienhinweis, falls Beitrag Bestandteil einer Serie ist
	#	(availableSeasons)
	if SETTINGS.getSetting('pref_more') == 'true':
		VideoObj = page["widgets"][0]				# 
		if "show" in VideoObj: 						# Serienhinweis?
			PLog("show_detect")
			if "availableSeasons" in VideoObj["show"]:
				PLog("serie_detect: %s" % str(VideoObj["show"])[:80])
				sid = VideoObj["show"]["id"]
				title =  "[B]Serie[/B]: %s" % VideoObj["show"]["title"]
				img =  VideoObj["show"]["image"]["src"]
				img = img.replace('{width}', '640')
				alt =  VideoObj["show"]["image"]["alt"]
				anz = VideoObj["show"]["availableSeasons"]
				if anz:								# None, "1", "2",..
					typ = VideoObj["show"]["coreAssetType"]
					tag = u"Serie | Staffeln: %s" % len(anz)
					summ = VideoObj["synopsis"]
					path = "https://api.ardmediathek.de/page-gateway/pages/daserste/grouping/%s" % sid
					PLog("serie: %s, path: %s" % (title, path))
					path=py2_encode(path); title=py2_encode(title); 
					fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': 'ARDStartSingle'}" %\
						(quote(path), quote(title))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik",\
						fanart=img, thumb=img, tagline=tag, summary=summ, fparams=fparams)
				else:
					PLog("serie_anz_fehlt")
	
		if len(page["widgets"]) > 1:
			VideoObj = page["widgets"][1]					# Mehr-Beiträge hinter den Daten zum gewählten Video
			if "teasers" in VideoObj:						# Teasers-extrakt in get_json_content
				PLog('Teasers: ' + str(len(VideoObj["teasers"])))
				get_json_content(li, VideoObj, ID=ID, mehrzS=True, mark='')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#----------------------------
# auto-Stream master.m3u8 aus VideoUrls ermitteln, 
#	via Parseplaylist in Einzelauflösungen zerlegen
# Aufrufer ARDStartSingle (Länge VideoUrls > 0) und
# 	ARD_get_strmStream
# StreamArray_0 (StreamArray): mediaCollection["embedded"]["streams"][0]
#	StreamArray_1: DGSStreams (werden angehängt)
#
def ARDStartVideoHLSget(title, StreamArray, call="", StreamArray_1=""): 
	PLog('ARDStartVideoHLSget: ' + call); 
	PLog(str(StreamArray)[:100])
	
	HLS_List=[]; Stream_List=[]; href=""
	title = py2_decode(title)
	
	Arrays=[]
	Arrays.append(StreamArray)
	if StreamArray_1:										# StreamArrays verbinden
		Arrays.append(StreamArray_1)
	PLog("Arrays: %d" % len(Arrays))
	
	skip_list=[]
	for array in Arrays:
		kind  = array["kindName"]
		PLog("kind: " + kind)
		for stream in  array["media"]:				
			#PLog(str(stream)[:100])
			if stream["mimeType"] == "application/vnd.apple.mpegurl":	# 1x:  master.m3u8
				href =  stream["url"]	# Video-Url
				if href.startswith('http') == False:
					href = 'https:' + href

				qual = stream["forcedLabel"]
				aspect = stream["aspectRatio"]
				audio_kind = stream["audios"][0]["kind"]
				audio_lang = stream["audios"][0]["languageCode"]
				details = "%s, %s, %s, audio: %s/%s" % (kind, qual, aspect, audio_kind, audio_lang)
				if details in skip_list:								# Doppel ausfiltern
					continue
				skip_list.append(details)

				quality = u'automatisch'
				HLS_List.append(u'HLS [B]%s[/B] ** auto ** auto ** %s#%s' % (details, title,href))
			
	if "audio-description/deu" in HLS_List[0]:				# Pos-Wechsel mit standard/deu
		PLog("swap_new_0: " + HLS_List[0])					# Debug: standard/deu?
		HLS_List[0], HLS_List[1] = HLS_List[1], HLS_List[0]
	
	PLog("Streams: %d" % len(HLS_List))
	PLog(HLS_List)
	return HLS_List

#----------------------------
# HBBTV-Quellen laden 
# json-Quelle:	tv.ardmediathek.de/..
# Aufrufer ARDStartSingle
# 16.05.2024 Auswertung Bitraten entfernt (unsicher)
#
def ARDStartVideoHBBTVget(title, path): 
	PLog('ARDStartVideoHBBTVget:'); 
	PLog(path)

	base = "http://tv.ardmediathek.de/dyn/get?id=video%3A"
	HBBTV_List=[];
	title = py2_decode(title)
	
	if "?devicetype=" in path:					# ID ermitteln
		path = path.split("?devicetype=")[0]
	ID = path.split("/")[-1]
	path = base + ID + "&client=ard"
		
	page, msg = get_page(path, do_safe=False)					
	if page == '':	
		PLog(msg)
		return HBBTV_List

	try:
		page = json.loads(page)
		
		streams = page["video"]["streams"][0]
		PLog("streams0: %d" % len(streams))
		PLog(str(streams)[:80])
	except Exception as exception:
		PLog(str(exception))
		return HBBTV_List
	
	for stream in streams["media"]:
		PLog(str(stream)[:80])
		if "dash" in stream["mimeType"]:		# 16.05.2024 ../tagesschau_1.mpd läuft nicht
			continue
		quality = stream["forcedLabel"]
		w = stream["maxHResolutionPx"] 
		h = stream["maxVResolutionPx"]
		res = "%sx%s" % (str(w),str(h))	
		href = stream["url"]
		if "_internationalerton_" in href:		# vermutl. identisch mit "_sendeton_"-Url
			continue
		
		PLog("hbbtv_res: %s" % res) 
		title_url = u"%s#%s" % (title, href)
		item = u"MP4: [B]%s[/B] ** Auflösung %s ** %s" % (quality, res, title_url)
		if "3840x" in res:
			item = item.replace("MP4", "UHD_MP4")
		item = py2_decode(item)
		HBBTV_List.append(item)

	PLog(HBBTV_List)
	return HBBTV_List

#----------------------------
# holt Downloadliste mit MP4-Videos
# altes Format: "Qualität: niedrige | Titel#https://pdvideosdaserste.."
# neues Format:	"MP4 Qualität: Full HD ** Auflösung ** Bandbreite ** Titel#Url"
# Format ähnlich ARDStartVideoHBBTVget (Label abweichend)
# StreamArray_0 (StreamArray): mediaCollection["embedded"]["streams"][0]
#	StreamArray_1: DGSStreams (werden angehängt)
# 16.05.2024 Auswertung Bitraten entfernt (unsicher)
def ARDStartVideoMP4get(title, StreamArray, call="", StreamArray_1=""):	
	PLog('ARDStartVideoMP4get:'); 
			
	href=''; quality=''
	title = py2_decode(title)
	download_list = []	
	# 2-teilige Liste für Download: 'title # url'
	
	Arrays=[]
	Arrays.append(StreamArray)
	if StreamArray_1:										# StreamArrays verbinden
		Arrays.append(StreamArray_1)
	PLog("Arrays: %d" % len(Arrays))

	for array in Arrays:
		kind  = array["kindName"]
		for stream in array["media"]:
			PLog(str(stream)[:80])
			if stream["mimeType"] == "video/mp4":					# HLS ausschließen
				if "maxHResolutionPx" in stream and "maxVResolutionPx" in stream: 
					w = stream["maxHResolutionPx"] 
					h = stream["maxVResolutionPx"]
					res = "%sx%s" % (str(w),str(h))
				else:
					PLog("res_missing")
					res = "0x0"
				PLog("mp4_res: %s" % res) 
				href = stream["url"]
				
				qual = stream["forcedLabel"]
				aspect = stream["aspectRatio"]
				audio_kind = stream["audios"][0]["kind"]
				audio_lang = stream["audios"][0]["languageCode"]
				details = "%s, %s, %s, audio: %s/%s" % (kind, qual, aspect, audio_kind, audio_lang)
				
				title_url = u"%s#%s" % (title, href)
				item = u"MP4: [B]%s[/B] ** Auflösung %s ** %s" % (details, res, title_url)
				if "3840x" in res:
					item = item.replace("MP4", "UHD_MP4")
				item = py2_decode(item)
				download_list.append(item)
	
	PLog(download_list)
	return download_list			
			
####################################################################################################
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 
# 10.11.2019 Verzicht auf Abgleich Button/Webseite (Performance, lange Ladezeit).
# 28.05.2020 ARD-Änderungen - s. SendungenAZ_ARDnew
# 25.01.2021 Laden + Caching der Link-Übersicht, Laden der Zielseite in 
#	SendungenAZ_ARDnew
# 13.06.2023 Mitnutzung durch phoenix (CurSender, homeID)
# 06.11.2024 Mitnutzung durch funk (CurSender)
# 		
def SendungenAZ(title, CurSender="", homeID=''):		
	PLog('SendungenAZ: ' + title)
	
	if CurSender == "":
		CurSender = ARD_CurSender()						# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sender)
		
	title2 = title + ' | aktuell: %s' % sendername
	# no_cache = True für Dict-Aktualisierung erforderlich - Dict.Save() reicht nicht			 
	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
		icon = R("phoenix_az.png")
	else:
		li = home(li, ID='ARD Neu')					# Home-Button
		icon = R(ICON_ARD_AZ)
		
	# Link-Übersicht laden:
	# azlist = list(string.ascii_uppercase)			# 25.01.2021 A-Z - nicht mehr benötigt
	# azlist.insert(0,u'#')	
	path = 'https://api.ardmediathek.de/page-gateway/pages/%s/editorial/experiment-a-z?embedded=false' % sender
	page = Dict("load", 'ARDnew_AZ_%s' %sender, CacheTime=ARDStartCacheTime)
	if page == False:										# nicht vorhanden oder zu alt
		page, msg = get_page(path)		
		if page == '':	
			msg1 = u"Fehler in SendungenAZ:"
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
		button = stringextract('title":"', '"', grid)
		#if button == 'Z':	# Debug
		#	PLog(grid)
		if ' A-Z' in button:								# Gesamtlink
			continue
		if button == "":
			continue
			
		title = "Sendungen mit " + button
		anz = stringextract('totalElements":', '}', grid)
		href = stringextract('href":"', '"', grid)
		tag = u'Gezeigt wird der Inhalt für [B]%s[/B]' % sendername
		
		PLog('Satz1:');
		PLog(button); PLog(anz); PLog(href); 
		href=py2_encode(href); title=py2_encode(title); 	
		fparams="&fparams={'title': '%s', 'button': '%s', 'href': '%s', 'homeID': '%s'}" %\
			(title, button, quote(href), homeID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.SendungenAZ_ARDnew",\
			fanart=R(ICON_ARD_AZ), thumb=icon, tagline=tag, fparams=fparams)
	
	if not homeID:		
		title 	= u'Wählen Sie Ihren Sender | aktuell: [B]%s[/B]' % sendername	# Senderwahl
		title=py2_encode(title); caller='resources.lib.ARDnew.SendungenAZ'
		tag = "die Senderwahl ist wirksam in [B]%s[/B], [B]%s[/B] und [B]%s[/B]" %\
			("ARD Mediathek", "A-Z", "Sendung verpasst")
		fparams="&fparams={'title': '%s', 'caller': '%s'}" % (quote(title), caller)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", 
			fanart=R(ICON_MAIN_ARD), thumb=R('tv-regional.png'), tagline=tag, fparams=fparams)																	
										
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
def SendungenAZ_ARDnew(title, button, href, CurSender="", homeID=''): 
	PLog('SendungenAZ_ARDnew:')
	PLog('button: ' + button); 
	PLog(CurSender)

	title = title	
	title_org = title

	li = xbmcgui.ListItem()
	if homeID:
		li = home(li, ID=homeID)
	else:
		li = home(li, ID='ARD Neu')							# Home-Button

	
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
	page = page.replace('\\"', '*')						# quotierte Marks entf., Bsp. \"query\"
			
	ID = 'A-Z'
	li = get_json_content(li, page, ID, mark="", homeID=homeID)																	
			
	# 24.08.2019 Erweiterung auf pagination, bisher nur AutoCompilationWidget
	#	pagination mit Basispfad immer vorhanden, Mehr-Button abhängig von Anz. der Beiträge
	if 	'"pagination":'	in page:						# Scroll-Beiträge
		PLog('pagination_Rubrik:')
		title = "Mehr zu >%s<" % title_org				# Mehr-Button	 
		li = xbmcgui.ListItem()							# Kontext-Doppel verhindern
		pages, pN, pageSize, totalElements, next_path = get_pagination(page)	# Basis 0
		mark=''		
		if next_path:	
			summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (pages, totalElements)
			pN = int(pN)+1								# nächste pageNumber, Basis 0
			tag = "weiter zu Seite %s" % str(pN)
			PLog(summ); PLog(next_path)
			
			title_org=py2_encode(title_org); next_path=py2_encode(next_path); mark=py2_encode(mark);
			fparams="&fparams={'title': '%s', 'path': '%s', 'pageNumber': '%s', 'pageSize': '%s', 'ID': '%s', \
				'mark': '%s','homeID': '%s'}" %\
					(quote(title_org), quote(next_path), str(pN), pageSize, ID, quote(mark), homeID)
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
# 01.03.2023 ARD-Suchpfad wie SearchARDundZDFnew (page.ardmediathek -> api.ardmediathek)
# 21.07.2024 Nutzung für Suchen nur in ARD od. ZDF (Vermeidung Absturzproblem nach Abbruch) 
#
def SearchARDundZDFnew(title, query='', pagenr='', homeID=""):
	PLog('SearchARDundZDFnew:');
	PLog(title); PLog(homeID)
	title_org=title
	query_file 	= os.path.join(ADDON_DATA, "search_ardundzdf")
	
	if query == '':														# Liste letzte Sucheingaben
		query = ARDHandleRecents(title, mode="load", query=query)
	if  query == None or query.strip() == '':							# plugin Error vermeiden
		if "ARD und ZDF" in title:										
			return ardundzdf.Main()
		if 'Suche in ARD-Mediathek' in title:
			return Main_NEW()	
		if 'Suche in ZDF-Mediathek' in title:
			return ardundzdf.Main_ZDF()	
		
	query=py2_encode(query)		# decode, falls erf. (1. Aufruf)
	PLog(query)
	query_ard = query.split('|')[0]
	query_zdf = query.split('|')[1]
	
	tag_negativ =u'neue Suche in ARD und ZDF starten'					# ohne Treffer
	tag_positiv =u'gefundene Beiträge zeigen'							# mit Treffer
	store_recents = False												# Sucheingabe nicht speichern
	
	li = xbmcgui.ListItem()
	if homeID == "":
		li = home(li, ID=NAME)											# Home-Button
	else:
		li = home(li, ID=homeID)										# ARD od. ZDF
	
	#------------------------------------------------------------------	# 1. Suche ARD
	if 'Suche in ARD-Mediathek' in title or "ARD und ZDF" in title:	
		sendername, sender, kanal, img, az_sender = ARDSender[0].split(':') # in allen Sendern
		sender = 'ard'
		pageNumber = 0
		
		query_lable = query_ard.replace('+', ' ')
		path = 'https://api.ardmediathek.de/search-system/mediathek/%s/search/vods?query=%s&pageNumber=%s&pageSize=24' % (sender, query_ard, pageNumber)
		icon = R(ICON_SEARCH)
		xbmcgui.Dialog().notification("ARD-Suche",query_lable,icon,1000, sound=False)
		page, msg = get_page(path)					
			
		vodTotal =  stringextract('"totalElements":', '}', page)	# Beiträge?
		gridlist = blockextract( '"mediumTitle":', page) 			# Sicherung
		vodTotal=py2_encode(vodTotal); query_lable=py2_encode(query_lable);
		PLog(query_ard)
		if len(gridlist) == 0 or vodTotal == '0':
			label = "[B]ARD[/B] | nichts gefunden zu: %s | neue Suche" % query_lable
			title=py2_encode(title); 
			fparams="&fparams={'title': '%s'}" % quote(title_org)
			addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
				fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
		else:	
			store_recents = True											# Sucheingabe speichern
			PLog(type(vodTotal)); 	PLog(type(query_lable)); 			
			title = "[B]ARD[/B]: %s Video(s)  | %s" % (vodTotal, query_lable)
			query_ard=py2_encode(query_ard); title=py2_encode(title); 
			fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '0'}" %\
				(quote(query_ard), quote(title), sender)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
				fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
	
	#------------------------------------------------------------------	# 2. Suche ZDF
	if 'Suche in ZDF-Mediathek' in title or "ARD und ZDF" in title_org:	
		ZDF_Search_PATH	 = 'https://zdf-prod-futura.zdf.de/mediathekV2/search?profile=cellular-5&q=%s&page=%s'
		if pagenr == '':		# erster Aufruf muss '' sein
			pagenr = 1
			
		path_zdf = ZDF_Search_PATH % (quote(query_zdf), pagenr) 	
		path_zdf = transl_umlaute(path_zdf)
		
		query_lable = (query_zdf.replace('%252B', ' ').replace('+', ' ')) 	# quotiertes ersetzen 
		query = query.replace(' ', '+')	
		
		icon = R(ICON_ZDF_SEARCH)
		xbmcgui.Dialog().notification("ZDF-Suche",query_lable,icon,1000, sound=False)
		header = "{'Origin': 'https://www.zdf.de'}"
		page, msg = get_page(path_zdf, header=header, do_safe=False)							
		
		try:
			jsonObject = json.loads(page)
			searchResult = str(jsonObject["totalResultsCount"])
			nextUrl = str(jsonObject["nextPageUrl"])
			nextPage = str(jsonObject["nextPage"])
		except:
			searchResult=0; nextUrl=""; nextPage=""
		searchResult = str(searchResult)
		PLog("searchResult: "  + searchResult);
		PLog("nextPage: "  + nextPage);

		query_lable=py2_encode(query_lable); searchResult=py2_encode(searchResult);
		if searchResult == '0':												# Sprung hierher
			label = "[B]ZDF[/B] | nichts gefunden zu: %s | neue Suche" % query_lable
			title=py2_encode(title);
			fparams="&fparams={'title': '%s'}" % quote(title_org)
			addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
				fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)
		else:	
			store_recents = True											# Sucheingabe speichern
			title = "[B]ZDF[/B]: %s Video(s)  | %s" % (searchResult, query_lable)
			query_zdf=py2_encode(query_zdf); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s', 'pagenr': '%s'}" % (quote(query_zdf), 
				quote(title), pagenr)
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R('suche_ardundzdf.png'), 
				thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)
						
	#------------------------------------------------------------------	# 3. Suche Merkliste
	if "ARD und ZDF" in title_org:	
		PLog("search_merk: " + query_ard)
		my_items, my_ordner = ReadFavourites('Merk')
		if len(my_items) > 0:
			q_org = query_ard.replace('+', ' ')
			q=py2_decode(up_low(q_org))
			selected=""; cnt=0; found=0
			for item in my_items:
				name = stringextract('merk name="', '"', item)
				ordner = stringextract('ordner="', '"', item)
				Plot = stringextract('Plot="', '"', item)
				name=py2_decode(name); Plot=py2_decode(Plot)				# Abgleich Name + Plot
				ordner=py2_decode(ordner)
				if q in up_low(name) or q in up_low(Plot) or q in up_low(ordner):
					selected = 	"%s %s" % (selected,  str(cnt))				# Indices
					found=found+1	
				cnt=cnt+1
			PLog(selected)
				
			if len(selected) == 0:											# Sprung hierher
				label = "[B]Merkliste[/B] | nichts gefunden zu: %s | neue Suche" % q_org
				title="Suche in ARD und ZDF"
				title=py2_encode(title);
				fparams="&fparams={'title': '%s'}" % quote(title)
				addDir(li=li, label=label, action="dirList", dirID="resources.lib.ARDnew.SearchARDundZDFnew", 
					fanart=R('suche_ardundzdf.png'), thumb=R('suche_ardundzdf.png'), tagline=tag_negativ, fparams=fparams)		
			else:
				title = u"[B]Merkliste[/B]: %s Einträge  | %s" % (found, q_org)
				if len(selected) == 1:
					title = u"[B]Merkliste[/B]: %s Eintrag  | %s" % (found, q_org)
				q=py2_encode(q); title=py2_encode(title);
				fparams="&fparams={'mode': 'Merk', 'selected': '%s'}" % selected.strip()
				addDir(li=li, label=title, action="dirList", dirID="ShowFavs", fanart=R('suche_ardundzdf.png'), 
					thumb=R('suche_ardundzdf.png'), tagline=tag_positiv, fparams=fparams)	
	
	#-----------------------------------
	if 	store_recents:													# Sucheingabe speichern
		ARDHandleRecents(title_org, mode="store", query=query_ard)
			
	xbmcplugin.endOfDirectory(HANDLE)
	
#----------------------------------------------------------------
# Suchworte laden + speichern
# Länge begrenzt auf 24, Änderung angleichen -> tool.SearchWordWork
#
def ARDHandleRecents(title, mode="load", query=""):
	PLog('ARDHandleRecents: %s, %s' % (mode, title));	
	PLog(query)
	query_file 	= os.path.join(ADDON_DATA, "search_ardundzdf")

	query_recent = RLoad(query_file, abs_path=True)
	if mode == "load":													# laden
		if query_recent.strip():
			search_list = ['neue Suche']
			query_recent= query_recent.strip().splitlines()
			query_recent=sorted(query_recent, key=str.lower)
			search_list = search_list + query_recent
			ret = xbmcgui.Dialog().select('Sucheingabe', search_list, preselect=0)
			if ret == -1:
				PLog("abort_search_list")
				return None
			elif ret == 0:
				query = ''
			else:
				query = search_list[ret]
				query = "%s|%s" % (query,query)							# doppeln
						
		if query == '':
			query = ardundzdf.get_query(channel='ARDundZDF')			# Kodi-Suchdialog 
		if  query == None or query.strip() == '':
			return None

		PLog("query: " + str(query))
		return query

	else:																# speichern	
		query_recent= RLoad(query_file, abs_path=True)
		query_recent= query_recent.strip().splitlines()
		if len(query_recent) >= 24:										# 1. Eintrag löschen (ältester)
			del query_recent[0]
		query=py2_encode(query)
		if query not in query_recent:									# query_ard + query_zdf ident.
			query_recent.append(query)
			query_recent = "\n".join(query_recent)
			query_recent = py2_encode(query_recent)
			RSave(query_file, query_recent)								# withcodec: code-error		
	
		return
#---------------------------------------------------------------- 
# Suche in Mediathek
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
# 26.09.2021 Suche nach Sendungen möglich aber verworfen, da zusätzl. Suche erforderlich
#	 (Suchstring: ../ard/search/grouping?searchString=..) 
# 14.03.2022 nach Sofortstart-Abbruch springt Kodi erneut nach get_keyboard_input - Addon-
#	Absturz bei Abbruch der Eingabe. Abhilfe: return ersetzt durch Aufruf Main_NEW. 
# 22.03.2023 api-Suche umgestellt page-gateway/widgets  -> search-system/mediathek, um
#	Videos von Sendereihen zu erfassen (Bsp. "2 für 300")
# 13.06.2023 Mitnutzung durch phoenix (sender, query, homeID)
#
def ARDSearchnew(title, sender, offset=0, query='', homeID=""):
	PLog('ARDSearchnew:');	
	PLog(title); PLog(sender); PLog(offset); 
	PLog(query); PLog(homeID);

	if sender == '':								# Sender gewählt?
		CurSender = ARD_CurSender()		
		sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog("sender: " + sender)
	
	if query == '':
		query = get_keyboard_input() 
		if query == None or query.strip() == '': 	# None bei Abbruch
			PLog(query)
			# return								# Absturz nach Sofortstart-Abbruch					
			Main_NEW(NAME)
			
	query = query.strip()
	query = query.replace(' ', '+')					# für Merkliste - 01.03.2023 nicht mehr relevant 	
	query_org = query	
	query=py2_decode(query)							# decode, falls erf. (1. Aufruf)
	
	li = xbmcgui.ListItem()
	if homeID:
		home(li, ID=homeID)
	else:
		li = home(li, ID='ARD Neu')					# Home-Button
	
	# ----------------------------------------------------- # Suchstring umgestellt, s.o.
	PLog(query)
	path = 'https://api.ardmediathek.de/search-system/mediathek/%s/search/vods?query=%s&pageNumber=%s&pageSize=24' % (sender, query, offset)

	page, msg = get_page(path)					
	PLog(len(page))
	if page == '':											
		msg1 = "Fehler in ARDSearchnew, Suche: %s"	% query
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return
	
	gridlist = blockextract( '"availableTo"', page) 		# Beiträge?
	if len(gridlist) == 0:				
		msg1 = u'keine Beiträge gefunden zu: %s'  % query
		PLog(msg1)
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE)		
	PLog('gridlist: ' + str(len(gridlist)))	
	
	ID='Search' 	# mark für farbige Markierung
	get_json_content(li, page, ID, mark=unquote(query))	
															# Mehr-Button:
	title = "Mehr zu >%s<" % unquote(query)		
	li = xbmcgui.ListItem()									# Kontext-Doppel verhindern
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
		fparams="&fparams={'query': '%s', 'title': '%s', 'sender': '%s','offset': '%s','homeID': '%s'}" %\
			(quote(query), quote(title), quote(sender), str(offset), homeID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", fanart=R(ICON_MEHR), 
			thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)																	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------- 
# ARDVerpasst - Liste Wochentage
# 29.05.2020 Änderung der Webseite durch die ARD. HTML steht nicht mehr
#	zur Verfügung, Ermittlung der timeline-Sender im Web entfällt.
#	Statt dessen forder wir mit dem gewählten Sender die entspr. 
#	json-Seite an. Verarbeitung in ARDVerpasstContent 	
# CurSender neubelegt in Senderwahl od. in Param (phoenix)
# 13.06.2023 Mitnutzung durch phoenix (CurSender, homeID)
# 06.12.2023 endDate entfällt mit neuem api-Link programm-api.ard.de
#
def ARDVerpasst(title, CurSender="", homeID=""):
	PLog('ARDVerpasst: ' + CurSender);
	PLog(homeID)

	if CurSender == "":
		CurSender = ARD_CurSender()						# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	
	li = xbmcgui.ListItem()
	if homeID:
		 home(li, ID=homeID)
	else:
		li = home(li, ID='ARD Neu')				# Home-Button

	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		startDate = rdate.strftime("%Y-%m-%d")
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
		tagline = "Sender: [B]%s[/B]" % sendername
		tagline = u"%s\nHinweis: keine Anzeige für ARD-Alle." % tagline	
		
		PLog(title); PLog(startDate); PLog(endDate)
		fparams="&fparams={'title': '%s', 'startDate': '%s', 'CurSender': '%s', 'homeID': '%s'}" %\
			(title,  startDate, CurSender, homeID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDVerpasstContent", 
			fanart=R(ICON_ARD_VERP), thumb=R(ICON_ARD_VERP), fparams=fparams, tagline=tagline)
	
	if not homeID:								# nicht bei phoenix	
		title 	= u'Wählen Sie Ihren Sender | aktuell: [B]%s[/B]' % sendername	# Senderwahl
		tag = "die Senderwahl ist wirksam in [B]%s[/B], [B]%s[/B] und [B]%s[/B]" % ("ARD Mediathek", "A-Z", "Sendung verpasst")
		tag = u"%s\nHinweis: keine Anzeige für ARD-Alle." % tag
		title=py2_encode(title); caller='resources.lib.ARDnew.ARDVerpasst'
		fparams="&fparams={'title': '%s', 'caller': '%s'}" % (quote(title), caller)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.Senderwahl", fanart=R(ICON_MAIN_ARD), 
			thumb=R('tv-regional.png'), tagline=tag, fparams=fparams) 
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------- 
# ARDVerpasstContent - Inhalt des gewählten Tages
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
# 06.12.2023 alter api-Link filtert nicht mehr nach Sendern, neuer Link
#	programm-api.ard.de, gecached (ca. 2 MB, enthält alle Sender).
# 21.04.2024 Programmliste ARD-Alle ermöglicht
#
def ARDVerpasstContent(title, startDate, CurSender="", homeID=""):
	PLog('ARDVerpasstContent:');
	PLog(title);  PLog(startDate); 
	
	headers="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}"

	if CurSender == "":
		CurSender = ARD_CurSender()				# init s. Modulkopf
	sendername, sender, kanal, img, az_sender = CurSender.split(':')
	PLog(sendername); PLog(sender); 
	
	li = xbmcgui.ListItem()
	if homeID  == "":			# Home-Button
		homeID='ARD Neu'
	home(li, ID=homeID)

	base = "https://programm-api.ard.de/program/api/program?day=%s" % startDate
	DictID = "ARD_PRG_%s" % startDate
	page = Dict("load",DictID,CacheTime=ARDStartCacheTime)	# Cache: 5 min
	if not page:											# nicht vorhanden oder zu alt -> vom					
		page, msg = get_page(base, header=headers)			# 	Sender holen		
		if page:
			icon = R(ICON_MAIN_ARD)
			xbmcgui.Dialog().notification("Cache Verpasst:" ,"Haltedauer 5 Min",icon,3000,sound=False)
			Dict('store', DictID, page)						# json-Datei -> Dict, ca. 2 MByte 	
	
	if page == '':	
		msg1 = 'Fehler in ARDVerpasstContent'
		msg2=msg
		msg3=path
		MyDialog(msg1, msg2, msg3)	
		return
	PLog(len(page))				
	
	# dateformat: 2022-05-23T03:30:00.000Z
	# Bereichsangabe (Datum, Uhrzeit) zu lang für notification:
	msg1 = "%s.%s.%s" % (startDate[8:10], startDate[5:7], startDate[0:4])
	msg2 = sendername
	icon = R(ICON_ARD_VERP)
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)
	
	try:
		obs = json.loads(page)
		channels = obs["channels"]
	except Exception as exception:
		channels=[]; channel=[]
		PLog("channels_error: " + str(exception))
	PLog("channels: %d" % len(channels))
	PLog("channels: " + str(channels)[:100])
	
	if sender == "ard":
		sender = sendername									# ARD-Alle
	PLog("extract_%s" % sender)
	ARDVerpasst_get_json(li, channels, homeID, sender)															
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# Auswertung timeSlots (Vormittags, Nachmittags, Abends), hier
#	zusammenhängend.
def ARDVerpasst_get_json(li, channels, homeID, sender):
	PLog('ARDVerpasst_get_json: ' + sender)
	PLog(len(channels))
	
	logo = R("icon-bild-fehlt_wide.png")						# ersetzt fehlendes img im EPG
	# targetbase (%s=sender, %s=urlId)
	tbase = "https://api.ardmediathek.de/page-gateway/pages/%s/item/%s?devicetype=pc&embedded=true" 
	mediatype=""
	li2 = xbmcgui.ListItem()									# mediatype='video': eigene Kontextmenüs in addDir							
	

	for i, channel in enumerate(channels):
		sid = channel["id"]
		if sender != "ARD-Alle":
			if sid != sender:
				continue
			PLog("sender_found: " + sender)
			

		slots = channel["timeSlots"]
		PLog("sender: %s, slots: %d, anz: %d" % (sid, i, len(slots)))
		for ii, slot in enumerate(slots):						# 3; vorm., nachm., abends	
			for s in slot:										# einz. Sendungen
				PLog(str(s)[:80])
							
				synopsis=""; availableTo=""; href=""; path=""		# path -> Video
				matRat=""; uhr=""; subline=""; summ="";
				pubServ=""; channel_id="";

				try:
					title = s["title"]
					duration = s["duration"]
					duration = seconds_translate(duration)			# 0:15
					# pubServ = s["channel"]["name"]				# Problem swrbw
					
					if "images" in s:
						img = s["images"]["aspect16x9"]["src"]
						img = img.replace('{width}', '720')
					else:
						img = logo
					
					
					if 	"channel" in s:								# kann fehlen
						channel_id = s["channel"]["id"]				# -> sender bei ARD-Alle
						pubServ = s["channel"]["name"]
					else:
						pubServ = sender 
						
					if "subline" in s:	
						subline = s["subline"]
						pubServ = "%s | %s" % (pubServ, subline)
					
					if "target" in s["links"]:						# target -> Video
						urlId = s["links"]["target"]["urlId"]
						path = tbase % (sender, urlId)
						if sender == "ARD-Alle":					# Sender-Korrektur: Verpasst ARD-Alle
							path = tbase % (channel_id, urlId) 

					if "maturityContentRating" in s:
						matRat= s["maturityContentRating"]
					

					if duration and pubServ:										
						duration = u'Dauer %s | [B]%s[/B]' % (duration, pubServ)
						
					if 	matRat:
						if duration == '':
							duration = "Dauer unbekannt"
						duration = u"%s | FSK: %s\n" % (duration, matRat)
					if "availableTo" in s:									# fehlt seit Api-Änderung, s.
						availableTo = s["availableTo"]						#	pref_load_summary
					
					if 	"synopsis" in s:
						summ =  s["synopsis"]
						
					verf = availableTo										# s.o.
					if verf == None:
						verf=""
					verf = time_translate(verf, day_warn=True)
						
					pubDate = s["broadcastedOn"]
					PLog("pubDate: " + pubDate)
					pubDate = time_translate(pubDate, add_hour=False, day_warn=True)
					uhr = pubDate[11:16]	
					pubDate = u"Sendedatum: [COLOR blue]%s Uhr[/COLOR]\n" % pubDate
					summ = "%s\n%s" % (pubDate, summ)

					if verf:
						summ = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]\n\n%s" % (summ, verf)
					if duration:
						summ = "%s\n%s" % (duration, summ)
					PLog("summ: " + summ)	
						
					if path == "":
						summ = "[B]NICHT in der Mediathek![/B]\n%s" % summ		
						title = "[COLOR grey]%s | %s[/COLOR]" % (uhr, title) 
					else:
						title = "[COLOR blue]%s[/COLOR] | %s" % (uhr, title) 			
					
				
					if SETTINGS.getSetting('pref_load_summary') == 'true':	# summary (Inhaltstext) im Voraus holen
						summ_new = get_summary_pre(path=path, ID='ARDnew', duration=duration)  # Modul util
						if 	summ_new:										# 
							summ = summ_new
					summ = repl_json_chars(summ)
			
					if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart?
						mediatype='video'
				except Exception as exception:
					PLog("Verpasst_json_error: " + str(exception))
					
				if SETTINGS.getSetting('pref_usefilter') == 'true':		# Filter
					filtered=False
					for fil in AKT_FILTER: 
						if up_low(item) in py2_encode(up_low(str(s))):
							filtered = True
							break		
					if filtered:
						PLog('filtered_8: <%s> in %s ' % (item, title))
						continue		
					
				PLog("Satz:")
				PLog(title); PLog(href); PLog(path); PLog(img); PLog(summ[:60]); 
				PLog(duration); PLog(availableTo);
						
				summ_par = summ.replace('\n', '||')
				ID = "ARDVerpasst_get_json"
				href=py2_encode(href); title=py2_encode(title); summ_par=py2_encode(summ_par);
				fparams="&fparams={'path': '%s', 'title': '%s', 'summary': '%s', 'ID': '%s','homeID': '%s'}" %\
					(quote(path), quote(title), quote(summ_par), ID, homeID)	
				if path:
					addDir(li=li2, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", fanart=img, 
						thumb=img, fparams=fparams, summary=summ, mediatype=mediatype)
				else:														# function dummy Haupt-PRG
					fparams="&fparams={'path': '', 'title': '', 'img': ''}"
					addDir(li=li, label=title, action="dirList", dirID="dummy", fanart=img, 
						thumb=img, fparams=fparams, summary=summ, mediatype=mediatype)
											
	return
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
# 26.09.2021 Settting pref_disable_sender entfernt - "Sender:" in 
#	Titel entfällt.
# 11.10.2023 eigene Funktion (ARD_CurSender_set) zum Setzen. Die frühere 
#	Rückgabe des Senders an caller wird durch das Return-Menü von Kodi
#	überschrieben
# 07.11.2024 Neuaufnahme (ARDSender) wie Web: arte, funk, KiKA, 3sat.
#
def Senderwahl(title, caller=''):	
	PLog('Senderwahl:'); PLog(caller)
	CurSender = ARD_CurSender()							# init s. Modulkopf
	PLog(CurSender.split(':')[0])						# akt. sendername

	li = xbmcgui.ListItem()
	li = home(li, ID='ARD Neu')							# Home-Button
	
	for entry in ARDSender:								# ARDSender s. Modulkopf
		#if 'KiKA' in entry:							# 05.11.2024 fehlt nur noch in Verpasst-Daten der ARD
		#	continue
		sendername, sender, kanal, img, az_sender = entry.split(':')
		PLog(entry)
		img = R(img)
		
		tagline = 'Mediathek des Senders [B] %s [/B]' % sendername
		PLog('sendername: %s, sender: %s, kanal: %s, img: %s, az_sender: %s'	% (sendername, sender, kanal, img, az_sender))
		title = sendername
		if CurSender.split(':')[0] == sendername:		# aktuelle Auswahl fett
			title = "[B]%s[/B]" % sendername
		fparams="&fparams={'entry': '%s', 'caller': '%s'}" % (entry, caller) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARD_CurSender_set", 
			fanart=img, thumb=img, tagline=tagline, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#----------------------------------------------------------------
# setzt entry als CurSender + ruft caller auf
# caller: ARDVerpasst, SendungenAZ oder Main_NEW 
def ARD_CurSender_set(entry, caller):
	PLog("ARD_CurSender_set:")
	PLog(entry); PLog(caller)
	
	fname = os.path.join(DICTSTORE, 'CurSender')			 # init CurSender (aktueller Sender)
	try:
		Dict('store', "CurSender", entry)
	except Exception as exception:
		PLog("store_error: " + str(exception))
	
	if caller == '':
		return Main_NEW()
	if "ARDVerpasst" in caller:								# resources.lib.ARDnew.ARDVerpasst
		return ARDVerpasst('Sendung verpasst')
	if "SendungenAZ" in caller:								# resources.lib.ARDnew.SendungenAZ
		return SendungenAZ('Sendungen A-Z')	
	
####################################################################################################






	
		

