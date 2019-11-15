# -*- coding: utf-8 -*-
################################################################################
#				3Sat.py - Teil von Kodi-Addon-ARDundZDF
#							Start Juni 2019
#			Migriert von Plex-Plugin-3Sat_Mediathek, V0.5.9
################################################################################
# 	dieses Modul nutzt die Webseiten der Mediathek ab https://www.3sat.de,
#	Seiten werden im html-format, teils. json ausgeliefert
#	04.11.2019 Migration Python3

# Python3-Kompatibilität:
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range

# Python
import string, re
import  json		
import os, sys
import datetime, time

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, ssl
from urllib.parse import quote, unquote, quote_plus, unquote_plus	# save space

# XBMC
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

# Addonmodule + Funktionsziele (util_imports.py)
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
BytesToUnicode=util.BytesToUnicode


# Globals
ICON_TV3Sat 			= 'tv-3sat.png'
ICON_MAIN_ARD 			= 'ard-mediathek.png'			
ICON_MAIN_TVLIVE 		= 'tv-livestreams.png'		
			
ICON_SEARCH 			= 'ard-suche.png'						
ICON_DIR_FOLDER			= "Dir-folder.png"
ICON_SPEAKER 			= "icon-speaker.png"
ICON_MEHR 				= "icon-mehr.png"

DreiSat_BASE 	= 'https://www.3sat.de'
DreiSat_AZ 		= "https://www.3sat.de/sendungen-a-z"
DreiSat_Verpasst= "https://www.3sat.de/programm?airtimeDate=%s"   		# Format %s: 2019-05-22 (Y-m-d) 
DreiSat_Suche	= "https://www.3sat.de/suche?q=%s&synth=true&attrs=&contentTypes=episode" 	# ganze Sendungen

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
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
SUBTITLESTORE 	= os.path.join("%s/subtitles") % ADDON_DATA
TEXTSTORE 		= os.path.join("%s/Inhaltstexte") % ADDON_DATA

DEBUG			= SETTINGS.getSetting('pref_info_debug')
NAME			= 'ARD und ZDF'

#----------------------------------------------------------------
# Aufrufer: Haupt-PRG, Menü Main
#
def Main_3Sat(name):
	PLog('Main_3Sat:'); 
	PLog(name)
				
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
	PLog("li:" + str(li))						
			
	title="Suche in 3Sat-Mediathek"		
	fparams="&fparams={'first': 'True','path': ''}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
		thumb=R('zdf-suche.png'), fparams=fparams)
			
	epg = get_epg()
	if epg:
		epg = 'Jetzt in 3sat: ' + epg
	epg = UtfToStr(epg)
	title = '3Sat-Livestream'
	fparams="&fparams={'name': '%s', 'epg': '%s'}" % (quote(title), quote(epg))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Live", 
		fanart=R('3sat.png'), thumb=R(ICON_MAIN_TVLIVE), tagline=epg, fparams=fparams)
	
	title = 'Verpasst'
	summ = 'aktuelle Beiträge eines Monats - nach Datum geordnet'
	fparams="&fparams={'title': 'Sendung verpasst'}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Verpasst", 
		fanart=R('3sat.png'), thumb=R('zdf-sendung-verpasst.png'), summary=summ, fparams=fparams)
	
	title = "Sendungen A-Z | 0-9"	
	summ = "Sendereihen - alphabetisch geordnet"	
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(DreiSat_AZ))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZlist", 
		fanart=R('3sat.png'), thumb=R('zdf-sendungen-az.png'), fparams=fparams)
												
	title = "Rubriken"
	path = 'https://www.3sat.de/themen'
	summ = "Sendereihen - alphabetisch geordnet"
	fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(path))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubriken", 
		fanart=R('3sat.png'), thumb=R('zdf-rubriken.png'), summary=summ, fparams=fparams)


	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		 		
####################################################################################################
# Hinweis: wir suchen in 3Sat_XML_FULL = alle Mediathekinhalte
#	Die Sucheingabe kann mehrere Wörter enthalten, getrennt durch Blanks (ODER-Suche) 
#	Gesucht wird in Titel + Beschreibung
#
# Suche - Verarbeitung der Eingabe. Mediathek listet Suchergebnisse tageweise
def Search(first, path, query=''):
	PLog('Search:'); PLog(first);	
	if 	query == '':	
		query = ardundzdf.get_query(channel='ZDF')
	if  query == None or query.strip() == '':
		return ""
		
	query=BytesToUnicode(query)		# decode, falls erf. (1. Aufruf)
	PLog(query)

	name = 'Suchergebnis zu: ' + unquote(query)
		
	if first == 'True':								# query nur beim 1. Aufruf injizieren, nicht bei 'mehr' 
		path =  DreiSat_Suche % quote(query)
		path = path + "&page=1"
	PLog(path); 										# Bsp. https://www.3sat.de/suche?q=brexit&synth=true&attrs=&page=2
	page, msg = get_page(path=path)	
	if page == '':			
		msg1 = "Fehler in Search"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	rubriken =  blockextract('<picture class="">', page)	
	cnt = stringextract('class="search-number">', '<', page) # Anzahl Treffer
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button

	query_unqoute = (query.replace('%252B', ' ').replace('+', ' ')) # quotiertes ersetzen 
	if len(rubriken) == 0 or cnt == '':						# kein Treffer
		msg1 = 'Leider kein Treffer (mehr) zu '  + unquote(query)
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
	
	new_title = "%s Treffer zu >%s<" % (cnt, query)
	li = Sendereihe_Sendungen(li, path=path, title=new_title)
	
	# auf mehr prüfen:
	if test_More(page=page):						# Test auf weitere Seiten (class="loader)
		plist = path.split('&page=')
		pagenr = int(plist[-1])
		new_path = plist[0] + '&page=' + str(pagenr + 1)
		title = "Mehr zu: %s" %  unquote(query)
		summary='Mehr...'
		PLog(new_path)
		
		title=UtfToStr(title); summary=UtfToStr(summary);
		fparams="&fparams={'first': 'False', 'path': '%s', 'query': '%s'}" % (quote(new_path), 
			quote(query))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Search", fanart=R('3sat.png'), 
			thumb=R(ICON_MEHR), summary='Mehr...', fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
#------------ 
# A-Z Liste der Buchstaben (mit Markierung 'ohne Beiträge')
def SendungenAZlist(name, path):				# 
	PLog('SendungenAZlist: ' + name)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button

	page, msg = get_page(path)						
	if page == '':			
		msg1 = "Fehler in SendungenAZlist"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
	
	liste = blockextract('<ul class="letter-list"', page)  # 1 x
	content = blockextract('class="item', liste[0])
	
	PLog(len(content))
	for rec in content:
		title	= stringextract('title="', '"', rec)
		href	= stringextract('href="', '"', rec)
		href	= DreiSat_BASE + href
		PLog(title)
		if 'link is-disabled' in rec:							# Button inaktiv
			letter = stringextract('true">', '<', rec)
			title= "Sendungen mit " + letter + ' | ' + u'ohne Beiträge'
			title=UtfToStr(title);
			fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(DreiSat_AZ))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZlist", 
				fanart=R('3sat.png'), thumb=R('zdf-sendungen-az.png'), fparams=fparams)			
		else:
			title=UtfToStr(title);	
			fparams="&fparams={'name': '%s', 'path': '%s'}"	% (quote(title), quote(href))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenAZ", 
				fanart=R('3sat.png'), thumb=R('Dir-folder.png'), fparams=fparams)			
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------ 
# A-Z Liste der Beiträge
#	-> Sendereihe_Sendungen -> get_zdfplayer_content
def SendungenAZ(name, path): 
	PLog('SendungenAZ: ' + name)

	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in SendungenAZ"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	content = blockextract('<picture class="">', page)
	PLog(len(content))
	
	for rec in content:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		rubrik 	= stringextract('<span>', '</span>', rec)
		sub_rubrik = stringextract('ellipsis" >', '<', rec)
		title	= stringextract('clickarea-link">', '</p>', rec)
		href	= stringextract('href="', '"', rec)
		href	= DreiSat_BASE + href
		descr	= stringextract('clickarea-link" >', '<', rec)
		tag 	= rubrik
		if sub_rubrik:
			tag = "%s | %s" % (tag, sub_rubrik)
		tag = cleanhtml(tag)

		title = repl_json_chars(title); descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
		
		PLog('Satz:')
		PLog(img_src); PLog(rubrik); PLog(title);  PLog(href); PLog(descr);
			
		# Aufruf Sendereihe_Sendungen hier ohne Listitem					
		title=UtfToStr(title); descr=UtfToStr(descr); tag=UtfToStr(tag);
		fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
			 quote(href), quote(img_src))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
			fanart=R('3sat.png'), thumb=img_src, summary=descr, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------
# 25.05.2019 more-Links nicht mehr verfügbar (javascript-generiert) -
#	more-Links müssem vom Aufrufer (z.B. Search) generiert werden.
def test_More(page):						# Test auf weitere Seiten
	PLog('test_More:')
	if page.find('class="loader"') > 0:		# 2. Seite (z.Z. Seite 1: 0-9, A-K, Seite 2: Rest)
		PLog('True')
		return True	
	else:
		PLog('False')
		return False	
	
	
#------------
def Verpasst(title):	# je 1 Tag - passend zum Webdesign
	PLog('Verpasst:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
		
	wlist = list(range(0,30))					# Abstand 1 Tage
	now = datetime.datetime.now()
	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		iDate = rdate.strftime("%d.%m.%Y")		# Formate s. man strftime (3)
		SendDate = rdate.strftime("%Y-%m-%d")	# 3Sat-Format 2019-05-22 (Y-m-d)  	
		iWeekday =  rdate.strftime("%A")
		punkte = '.'
		if nr == 0:
			iWeekday = 'Heute'	
		if nr == 1:
			iWeekday = 'Gestern'	
		iWeekday = transl_wtag(iWeekday)
		iPath = DreiSat_Verpasst % SendDate

		# PLog(iPath); PLog(iDate); PLog(iWeekday);
		title =	"%s | %s" % (iDate, iWeekday)
		title =	iDate + ' | ' + iWeekday
		
		PLog('Satz:')	
		PLog(SendDate); PLog(title); 
		title=UtfToStr(title);
		fparams="&fparams={'SendDate': '%s', 'title': '%s'}" % (SendDate, quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SendungenDatum", 
			fanart=R('3sat.png'), thumb=R(ICON_DIR_FOLDER), fparams=fparams)
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------

# Liste Sendungen gewählter Tag
def SendungenDatum(SendDate, title):	
	PLog('SendungenDatum: ' + SendDate)
	title_org = UtfToStr(title)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button
		
	path =  DreiSat_Verpasst % SendDate
	page, msg = get_page(path=path)	
	
	content = blockextract('<picture class="">', page)
	PLog(len(content))
			
	if len(content) == 0:			
		msg1 = u'leider kein Treffer im ausgewählten Zeitraum'
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
		
	for rec in content:
		img_src =  stringextract('data-srcset="', ' ', rec)	
		href	= stringextract('href="', '"', rec)
		if href == '' or '#skiplinks' in href:
			continue
		href	= DreiSat_BASE + href
		sendung	= stringextract('level-6', '</', rec)
		sendung	= sendung.replace('">', ''); sendung = sendung.strip()
		descr	= stringextract('teaser-epg-text">', '</p>', rec)		# mehrere Zeilen
		PLog(descr)
		descr	= cleanhtml(descr); 
		zeit	= stringextract('class="time">', '</', rec)
		dauer	= stringextract('class="label">', '</', rec)
		
		sendung = zeit  + ' | ' + sendung
		tagline = title_org +  ' | ' + zeit
		if dauer:
			tagline = tagline + ' | ' + dauer
					
		title = repl_json_chars(title);
		sendung = repl_json_chars(sendung)
		descr	= unescape(descr);  
		descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	

		PLog('Satz:')
		PLog(img_src);  PLog(href); PLog(sendung); PLog(tagline); PLog(descr); PLog(dauer);
			 
		sendung=UtfToStr(sendung); descr=UtfToStr(descr); tagline=UtfToStr(tagline)	
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s', 'duration': ''}" %\
			(quote(sendung), quote(href), quote(img_src), quote(descr_par), quote(dauer))
		addDir(li=li, label=sendung, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, summary=descr, tagline=tagline, fparams=fparams)
			 					 	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
#------------
def transl_month(shortmonth):	# Monatsbez. (3-stellig) -> Zahl 
	month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	val = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
	
	mval = shortmonth
	for i in range (len(month)):
		m = month[i]
		if m == shortmonth:
			mval = val[i]
			break
	return mval

#------------
# Aufrufer: Main_3Sat - Liste der 3Sat-Rubriken (wie Webseite)
# 	
def Rubriken(name, path):
	PLog('Rubriken:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in Rubriken"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	rubriken =  blockextract('class="dropdown-link js-rb-click js-track-click"', page)
	PLog(len(rubriken))
	
	i=0; rubrik=[]; 							
	for rec in rubriken:					# Rubriken sammeln	
		title	= stringextract('title="', '"', rec)
		if 'A-Z' in title:
			continue
		href	= DreiSat_BASE + stringextract('href="', '"', rec)
		line 	= title + "|" + href	
		rubrik.append(line)
		i=i+1
	
	rubrik.sort()							# Rubriken sortieren
	img_src = R('Dir-folder.png')
	for rec in rubrik:
		title, href = rec.split('|')
		title=UtfToStr(title);				
		fparams="&fparams={'name': '%s', 'path': '%s'}" % (quote(title), quote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubrik_Single", 
			fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#------------
# Aufrufer: Rubrik - Liste der Themen einer 3Sat-Rubrik, z.B. Film
# rekursiv: zweiter Durchlauf mit thema listet die Sendereihen dieser Rubrik
#			dritter Durchlauf nach thema 'Mehr' (Sendereihe, keine Einzelbeiträge) -	
#				Liste der Sendereihen beim 2. Durchlauf.
def Rubrik_Single(name, path, thema=''):	# Liste der Einzelsendungen zu Sendereihen
	PLog('Rubrik_Single: '+ name)
	PLog("thema: " + thema)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')										# Home-Button		
	
	page, msg = get_page(path)	
	if page == '':			
		msg1 = "Fehler in Rubrik_Single"
		msg2 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li	
		
	themen =  blockextract('is-uppercase ">', page)	
	PLog(len(themen))											
	
	if thema == '':									# 1. Durchlauf: Themen der Rubrik name	
		PLog('1. Durchlauf, thema: %s' % thema)						
		img_src = R('Dir-folder.png')			
		for rec in themen:
			title	= stringextract('is-uppercase ">', '<', rec)	
			PLog(title)
			# ausschließen: Ende Themen, Mehr, Rechtliches, ..
			if title == '':
				PLog('Ende Themen')
				break
				
			title	= title.upper()
			summ = "Folgeseiten"
			if 'VIDEOTIPP' in title:
				summ = 'Videotipp(s) der Redaktion'
			title = repl_json_chars(title)			
			PLog('Satz: %s' % title)
			
			title =UtfToStr(title); summ =UtfToStr(summ);  		
			fparams="&fparams={'name': '%s', 'path': '%s', 'thema': '%s'}" % (quote(title),
				 quote(path), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubrik_Single", 
				fanart=R('3sat.png'), thumb=img_src, summary=summ, fparams=fparams)
				
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# Ende 1. Durchlauf
	
	PLog('2. Durchlauf, thema: %s' % thema)	
	content =  blockextract('is-uppercase ">', page)	
	for rec in content:										# 2. Durchlauf: Beiträge zu Thema thema		
		title	= stringextract('is-uppercase ">', '<', rec)
		title 	= repl_json_chars(title)					# dto. 1. Durchlauf
		title	= title.upper()
		PLog(title)
		if 	name in title:									# Bsp. VIDEOTIPP "SEIDENSTRASSE"
			PLog('Thema gefunden: %s' % name)
			page = rec
			PLog(len(rec))
			break											# -> Sendereihe_Sendungen	
	
	if "Videotipp".upper() in title:						# 1 oder mehrere Videos am Kopf
		if 'video-carousel-item">' in rec:
			li, cnt = get_video_carousel(li, rec) 			# mehrere Videos am Kopf
		else:									
			li, cnt = get_zdfplayer_content(li, content)	# 1 Video
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
	# Auswertung weiterer Inhalte (page = rec)				
	# Kennzeichnungen: Mehr, MEHR, ZUM STöBERN
	# Blockmerkmal'<picture class=""> entscheidet über Ziel:
	#	mit 	-> Rubrik_Single (nur 'ZUM STöBERN', Bsp. Kultur) oder Sendereihe_Sendungen
	#	ohne 	-> Sendereihe_Sendungen ('is-medium lazyload'), Bsp. Rubrik Wissen
	if name.upper() == 'MEHR' or name == 'ZUM STöBERN': 	# Zusätze Mehr/MEHR oder ZUM STöBERN
		rubriken =  blockextract('<picture class="">', page)
		PLog(len(rubriken))
		if len(rubriken) > 0:
			for rec in rubriken:
				img_src =  stringextract('data-srcset="', ' ', rec)	
				title	= stringextract('clickarea-link">', '</p>', rec)
				href	= stringextract('href="', '"', rec)
				if href.startswith('http') == False:
					href	= DreiSat_BASE + href
				descr	= stringextract('clickarea-link" >', '<', rec)
				
				title = repl_json_chars(title); descr = repl_json_chars(descr); 					
				PLog('Satz:')
				PLog(img_src); PLog(title);  PLog(href); PLog(descr);
				
				title = UtfToStr(title); descr = UtfToStr(descr)					
				if name == 'ZUM STöBERN':					# ähnlich mehr, aber Auswertung als Rubrik
					fparams="&fparams={'name': '%s', 'path': '%s'}" % (quote(title), quote(href))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Rubrik_Single", 
						fanart=R('3sat.png'), thumb=img_src, summary='Folgeseiten', fparams=fparams)

				else:										# Mehr: Sendereihen -> Sendereihe_Sendungen"									
					fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
						 quote(href), quote(img_src))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
						fanart=R('3sat.png'), thumb=img_src, summary=descr, fparams=fparams)
				
			xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
				
	# Übergabe Seitenausschnitt rec in page, Reihenfolge in Sendereihe_Sendungen:
	#	 <picture class=""> (hier nicht enthalten), 'is-medium lazyload'
	PLog(len(page))

	li = Sendereihe_Sendungen(li, path, title, page=page)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#------------
# Aufrufer: SendungenAZ mit path aber ohne Listitem, Rubrik_Single mit 
#	page (Seitenausschnitt)
#	Search + Rubrik_Single jew. mit Listitem
#	rekursiv möglich - s. is-clickarea-action (keine Rubriken, aber
#		weiterführender Link.
#
# Achtung: hier wird (nochmal) auf video-carousel-item	+ o--stage-brand
#	geprüft - page ev. vorher begrenzen.
#
def Sendereihe_Sendungen(li, path, title, img='', page=''):		# Liste der Einzelsendungen zu Sendereihen
	PLog('Sendereihe_Sendungen: ' + path)
	PLog(len(page))
	title_org = title
	got_page = False
	if page:
		got_page = True
	
	ret = False									# Default Return  o. endOfDirectory
	if not li:
		ret = True
		li = xbmcgui.ListItem()
		li = home(li, ID='3Sat')										# Home-Button
	
	if page == '':								# Seitenausschnitt vom Aufrufer?
		page, msg = get_page(path=path)	
	
	# 1. Strukturen am Seitenanfang (1 Video doppelt möglich):	
	if 'video-carousel-item' in page:		# Bsp. www.3sat.de/kultur/kulturzeit
		# video-carousel-item-Beiträge auswerten, html-Format, Seitenkopf
		PLog('Struktur video-carousel-item')
		content =  blockextract('video-carousel-item">', page)
		PLog(len(content))
		li, cnt = get_zdfplayer_content(li, content=content)
		
	if 'o--stage-brand' in page:		# Bsp. www.3sat.de/wissen/netz-natur (1 Beitrag)
		# "o--stage-brand-Beiträge auswerten, html-Format, Seitenkopf
		PLog('Struktur o--stage-brand')
		content =   stringextract('o--stage-brand">', '</article>', page)	# ausschneiden
		content =  blockextract('class="artdirect">', page)
		PLog(len(content))
		li, cnt = get_zdfplayer_content(li, content=content)		
	
	# 2. Strukturen nach Seitenanfang (1 Video doppelt möglich)
	PLog('Sendereihe_Sendungen2:')	
	rubriken =  blockextract('<picture class="">', page)
	PLog(len(rubriken))
	
	 									# kein Einzelbeitrag, weiterführender Link?
	# Bsp.: Rubriken/Kabarett/35 JAHRE 3SAT - JUBILÄUMSPROGRAMM
	#	-> rekursiv
	if len(rubriken) == 0 and got_page == True:		
		if 'class="is-clickarea-action' in page:
			PLog('is-clickarea-action:')
			img_src = stringextract('data-srcset="', ' ', page)	
			title 	= stringextract('title="', '"', page)	
			title	= unescape(title)
			href	= stringextract('href="', '"', page)
			if href.startswith('http') == False:
				href	= DreiSat_BASE + href
			descr	= stringextract('paragraph-large ">', '</p>', page)
			
			title=UtfToStr(title); descr=UtfToStr(descr);
			fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
				 quote(href), quote(img_src))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
				fanart=R('3sat.png'), thumb=img_src, summary=descr, fparams=fparams)

								
	for rec in rubriken:
		if 'data-playlist-toggle' not in rec:
			continue
		img_src =  stringextract('data-srcset="', ' ', rec)	
		rubrik 	= stringextract('<span>', '</span>', rec)
		rubrik	= cleanhtml(rubrik); rubrik = mystrip(rubrik)
		sub_rubrik = stringextract('ellipsis" >', '<', rec)
		sub_rubrik = mystrip(sub_rubrik)
		title	= stringextract('clickarea-link">', '</p>', rec)
		
		href	= stringextract('href="', '"', rec)
		if href.startswith('http') == False:
			href	= DreiSat_BASE + href
		descr	= stringextract('clickarea-link" >', '<', rec)
		tagline = rubrik + ' | ' +sub_rubrik
		dauer	= stringextract('class="label">', '<', rec)		# label">2 min</span>
		if dauer:
			tagline = tagline + ' | ' + dauer
		duration = ' '				
			
		title = repl_json_chars(title); descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
				
		PLog('Satz:')
		PLog(img_src); PLog(rubrik); PLog(title);  PLog(href); PLog(tagline); PLog(descr);
		PLog(dauer); PLog(duration);
				
		title=UtfToStr(title); descr=UtfToStr(descr); tagline=UtfToStr(tagline); 
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s', 'duration': '%s'}" %\
			(quote(title), quote(href), quote(img_src), quote(descr_par), quote(dauer), quote(duration))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, summary=descr, tagline=tagline, fparams=fparams)

	if 'is-medium lazyload' in page:							# Test auf Loader-Beiträge, escaped
		li, cnt = get_lazyload(li=li, page=page, ref_path=path)
				

	if ret == True:
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	else:
		return li	
	
#-------------
# Loader-Beitrag auswerten, json-Format, 
# keys: style, sourceModuleType, teaserImageId, clusterType, clusterTitle,
#	teasertext, sophoraId, moduleId
# Die Pfade zu den Loader-Beiträgen  werden in einer Json-Beitragsliste außerhalb
#	der Loader-Beiträge ermittelt (mittels sophId).
#
def get_lazyload(li, page, ref_path):
	PLog('get_lazyload:')
	content =  blockextract('is-medium lazyload', page)		# Test auf Loader-Beiträge, escaped
	PLog(len(content))
	dauer	= stringextract('duration": "', '"', page)		# gilt für folgende oader-Beiträge
	img_pre = stringextract('data-srcset="', ' ', page)		# dto.
	PLog("dauer %s, img_pre: %s " % (dauer, img_pre))	
	
	cnt=0
	for rec in content:	
		rec = unescape(rec)
		PLog('loader_Beitrag')
		PLog(rec[:60]); 	
	
		# Ersatz für javascript: Auswertung + Rückgabe aller  
		#	Bestandteile:
		sophId,path,title,descr,img_src,dauer,tag,isvideo = get_teaserElement(rec)
		
		if img_src == '':										
			if img_pre:
				img_src = img_pre								# Fallback 1: Rubrikbild
			else:
				img_src = R('icon-bild-fehlt.png')				# Fallback 2: Leer-Bild 
		if path == '':
			path	= "%s/%s.html" % (DreiSat_BASE, sophId)		# Zielpfad bauen
			
		tag = tag.strip()
		if tag:
			descr = "%s\n\n%s"   % (tag, descr)
				
		title = repl_json_chars(title); descr = repl_json_chars(descr); 
		descr_par =	descr.replace('\n', '||')	
		
		cnt = cnt+1	
		PLog('Satz: %d' % cnt)
		PLog(sophId); PLog(path); PLog(title);PLog(descr); PLog(img_src); PLog(dauer); PLog(tag); 
		
		title=UtfToStr(title); descr=UtfToStr(descr); dauer=UtfToStr(dauer);	
		if isvideo == 'true':											#  page enthält data-playlist
			fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '%s', 'dauer': '%s', 'duration': ''}" %\
				(quote(title), quote(path), quote(img_src), quote(descr_par), quote(dauer))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
				thumb=img_src, summary=descr, tagline=dauer, fparams=fparams)
		else:
			fparams="&fparams={'li': '', 'title': '%s', 'path': '%s', 'img': '%s'}" % (quote(title),
				 quote(path), quote(img_src))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.Sendereihe_Sendungen", 
				fanart=R('3sat.png'), thumb=img_src, summary=descr, fparams=fparams)

	return li, cnt
	
#------------
# Ersatz für javascript: Ermittlung Icon + Sendedauer
#	rec hier bereits unescaped durch get_lazyload
# Aus Performancegründen (Anzahl der Elemente manchmal 
#	> 30) werden die Elemente in TEXTSTORE gecached, 
#	unabhängig von SETTINGS('pref_load_summary').
def get_teaserElement(rec):
	PLog('get_teaserElement:')
	# Reihenfolge Ersetzung: sophoraId, teaserHeadline, teasertext, clusterTitle
	
	sophoraId = stringextract('"sophoraId": "', '"', rec)
	teaserHeadline = stringextract('teaserHeadline": "', ',', rec)
	teaserHeadline = teaserHeadline.replace('"', '')
	teasertext = stringextract('"teasertext": "', '",', rec)
	clusterTitle = stringextract('clusterTitle": "', ',', rec)
		
	sophoraId = transl_json(sophoraId); teaserHeadline = transl_json(teaserHeadline);
	teasertext = transl_json(teasertext); clusterTitle = transl_json(clusterTitle);
	
	sophId = sophoraId; title = teaserHeadline; ctitle = clusterTitle;  # Fallback-Rückgaben
	descr = teasertext; isvideo=''	
	
	sophoraId = quote(sophoraId); teaserHeadline = quote(teaserHeadline);
	teasertext = quote(teasertext); clusterTitle = quote(clusterTitle);
	
	path = "https://www.3sat.de/teaserElement?sophoraId=%s&style=m2&moduleId=mod-2&teaserHeadline=%s&teasertext=%s&clusterTitle=%s&clusterType=Cluster_S&sourceModuleType=cluster-s" % (sophoraId, teaserHeadline,teasertext,clusterTitle)
	PLog(path)
	
	fpath = os.path.join(TEXTSTORE, sophoraId)
	PLog('fpath: ' + fpath)
	if os.path.exists(fpath):				# teaserElement lokal laden
		page =  RLoad(fpath, abs_path=True)
	else:
		page, msg = get_page(path)			# teaserElement holen
		if page:							# 	und in TEXTSTORE speichern
			msg = RSave(fpath, page)
	PLog(page[:100])
	
	if page:								# 2. teaserElement auswerten
		img_src =  stringextract('data-srcset="', ' ', page)	
		title	= stringextract('clickarea-link">', '</p>', page)
		title	= unescape(title); 
		title	= transl_json(title); 
		ctitle = stringextract('ellipsis" >', '<', page)  		# -> tag
		tag 	= stringextract('<span>', '</span>', page)
		dauer	= stringextract('class="label">', '</', page)
		path	= stringextract('href="', '"', page)
		if path.startswith('http') == False:
			path = DreiSat_BASE + path
		descr	= stringextract('clickarea-link" >', '<', page)
		if ctitle:
			tag = tag + " | " + ctitle
			
		tag = cleanhtml(tag); descr = unescape(descr)
		if "data-playlist" in page:			# Videobeitrag? - Folgeseiten möglich
			isvideo = 'true'
		
		# sophId s.o.
		return sophId, path, title, descr, img_src, dauer, tag, isvideo	
	else:									#  Fallback-Rückgaben, Bild + Dauer leer
		img_src=''; dauer=''; tag=''; isvideo=''
		return sophId, path, title, descr, img_src, dauer, tag, isvideo
	
#------------
# video-carousel-item-Beiträge auswerten, html-Format, Seitenkopf
def get_video_carousel(li, page):
	PLog('get_video_carousel:')
	content =  blockextract('video-carousel-item">', page)
	PLog(len(content))
	cnt=0
	for rec in content:	
		if 'data-module="zdfplayer"' not in rec:		# redakt. Beitrag o. Video
			continue
		videoinfos = stringextract("video-infos='{", '}', rec)
		videoinfos = unescape(videoinfos)
		title 	= stringextract('title":', '",', videoinfos)
		title 	= (title.replace('\\"', '').replace('"', ''))
		dauer 	= stringextract('duration": "', '"', videoinfos)	# 2 min
		path	= stringextract('embed_content": "', '"', rec)
		path 	= "%s%s.html" % (DreiSat_BASE, path)
		img_src	= stringextract('image="{', '}', rec)	# data-zdfplayer-teaser-image=
		img_src	= stringextract('768xauto&quot;:&quot;', '&quot', rec)	# 768xauto	
		img_src	= unescape(img_src); img_src = img_src.replace('\\', '')
	
		tagline = dauer
		subtitle	= stringextract('brand-subtitle">', '<', rec)
		if not subtitle:
			subtitle	= stringextract('subheadline level-7 " >', '<', rec)
		if subtitle:
			tagline = "%s | %s" % (dauer, subtitle)
		descr 	= stringextract('paragraph-large ">', '<', rec)
		descr 	= unescape(descr)
		descr = transl_json(descr); 

		descr = transl_json(descr); 
		PLog('Satz:')
		PLog(img_src); PLog(title); PLog(dauer); PLog(path); 
		title=UtfToStr(title); tagline=UtfToStr(tagline);			 
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s', 'duration': ''}" %\
			(quote(title), quote(path), quote(img_src), quote(dauer))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, tagline=tagline, fparams=fparams)			 
			 
		cnt=cnt+1
	return li, cnt

#------------
# ideo-carousel-item- und o--stage-brand-Beiträge auswerten,
#	html-Format, Seitenkopf - Doppel zu Folgebeiträgen möglich
def get_zdfplayer_content(li, content):
	PLog('get_zdfplayer_content:')
	
	cnt=0
	for rec in content:	
		tag=''; 
		if 'data-module="zdfplayer"' not in rec:		# redakt. Beitrag ohne Video
			continue
		videoinfos = stringextract("video-infos='{", '}', rec)
		videoinfos = unescape(videoinfos)
		title 	= stringextract('title":', '",', videoinfos)
		title 	= (title.replace('\\"', '').replace('"', ''))

		dauer 	= stringextract('duration": "', '"', videoinfos)	# Bsp. 2 min
		path	= stringextract('embed_content": "', '"', rec)
		path 	= DreiSat_BASE + path + ".html"
		img_src	= stringextract('data-srcset="', '"', rec)			
		img_src	= img_src.split(' ')[0]								# kann mit Blank enden
		
		tagline = dauer
		subtitle	= stringextract('brand-subtitle">', '<', rec)
		if subtitle:
			tag = dauer + ' | ' + subtitle

		descr 	= stringextract('paragraph-large ">', '<', rec)
		descr 	= unescape(descr)
		descr = transl_json(descr); 
		title = transl_json(title); 
	
		PLog('Satz:')
		PLog(img_src); PLog(title); PLog(path); 
		title=UtfToStr(title); descr=UtfToStr(descr);			 
		fparams="&fparams={'title': '%s', 'path': '%s', 'img_src': '%s', 'summ': '', 'dauer': '%s', 'duration': ''}" %\
			(quote(title), quote(path), quote(img_src), quote(dauer))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.my3Sat.SingleBeitrag", fanart=R('3sat.png'), 
			thumb=img_src, summary=descr, fparams=fparams)
			 	
		cnt=cnt+1

	PLog("Anzahl Beiträge: %s" % cnt)
	return li, cnt

#------------

# 16.05.2017: Design neu, Videoquellen nicht mehr auf der Webseite vorhanden - (Ladekette ähnlich ZDF-Mediathek)
# 22.05.2019: Design neu, Ladekette noch ähnlich ZDF-Mediathek, andere Parameter, Links + zusätzl. apiToken
#
# SingleBeitrag für Verpasst + A-Z
#	hier auch m3u8-Videos verfügbar. 
def SingleBeitrag(title, path, img_src, summ, dauer, duration, Merk='false'):
	PLog('Funktion SingleBeitrag: ' + title)
	PLog(dauer);PLog(duration);PLog(summ);PLog(path)
	
	Plot	 = title
	Plot_par = summ										# -> PlayVideo
	if Plot_par == '':			
		Plot_par = title
	tag_org = dauer
	thumb	= img_src; title_org = title

	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')							# Home-Button
			
	page, msg = get_page(path=path)						# 1. Basisdaten von Webpage holen
	if page == '':			
		msg1 = "SingleBeitrag1: Abruf fehlgeschlagen"
		msg2 = msg
		msg3=path
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li	
	
	content = stringextract('window.zdfsite', 'tracking', page)  			
	content = stringextract('data-module="zdfplayer"', 'teaser-image=', page)  			
	appId	= stringextract('zdfplayer-id="', '"', content)
	apiToken= stringextract('apiToken": "', '"', content)
	profile_url= stringextract('content": "', '"', content)		# profile_url
	PLog(appId); PLog(profile_url); PLog("apiToken: " + apiToken); 
	
	if 	apiToken == '' or profile_url == '':
		if '<time datetime="' in page:
			termin = stringextract('<time datetime="', '"', page)
			termin = time_translate(termin)
			msg1 = "(noch) kein Video gefunden, Sendetermin: " + termin
		else:
			msg1 = "keine Videoquelle gefunden. Seite:\n" + path
			PLog(msg1)
			PLog(apiToken)		# zur Kontrolle
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	
	
	headers = "{'Api-Auth': 'Bearer %s','Host': 'api.zdf.de'}" % apiToken 
	page,msg = get_page3sat(path=profile_url, apiToken=apiToken)	# 2. Playerdaten mit neuer Video-ID	
	if page == '':			
		msg1 = "SingleBeitrag2: Abruf fehlgeschlagen"
		msg2 = msg
		msg3=path
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li	
	
	page = page.replace('\\', '')
	PLog(page[:100])

	videodat	= blockextract('ptmd-template":"',page)		# mehrfach möglich
	videodat	= videodat[-1]								# letzte ist relevant
	videodat_url= stringextract('ptmd-template":"', '"', videodat)
	video_ID = videodat_url.split('/')[-1]					#  ID z.B. 190521_sendung_nano
	videodat_url = 'https://api.3sat.de/tmd/2/ngplayer_2_3/vod/ptmd/3sat/' + video_ID
	PLog("videodat_url: " + videodat_url)
	page,msg = get_page3sat(path=videodat_url, apiToken=apiToken)
	if page == '':			
		msg1 = "SingleBeitrag3: Abruf fehlgeschlagen"
		PLog(msg1); PLog(msg)
		msg2 = msg
		
	if page == '':											# Alternative mediathek statt 3sat
		videodat_url = 'https://api.3sat.de/tmd/2/ngplayer_2_3/vod/ptmd/mediathek/' + video_ID
		try:
			page = get_page3sat(path=videodat_url, apiToken=apiToken)
		except Exception as exception:
			PLog(str(exception))
			page = ""
	
	if 	'formitaeten' not in page:
		msg1 = "keine Videoquelle gefunden. Seite:\n" + path
		PLog(msg1)
		PLog(videodat_url)		# zur Kontrolle
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li	

	if page:
		formitaeten = blockextract('formitaeten', page)		# 4. einzelne Video-URL's ermitteln 
		geoblock =  stringextract('geoLocation',  '}', page) 
		geoblock =  stringextract('"value" : "',  '"', geoblock).strip()
		PLog('geoblock: ' + geoblock);
		if 	geoblock == 'none':								# i.d.R. "none", sonst "de" - wie bei ARD verwenden
			geoblock = ' | ohne Geoblock'
		else:
			if geoblock == 'de':			# Info-Anhang für summary 
				geoblock = ' | Geoblock DE!'
			if geoblock == 'dach':			# Info-Anhang für summary 
				geoblock = ' | Geoblock DACH!'
			
	download_list = []
	tagline = title + " | " + dauer + " " + geoblock
	Plot_par = tagline + "||||" + Plot_par
	
	thumb=img_src
	for rec in formitaeten:									# Datensätze gesamt
		# PLog(rec)		# bei Bedarf
		typ = stringextract('\"type\" : \"', '\"', rec)
		facets = stringextract('\"facets\" : ', ',', rec)	# Bsp.: "facets": ["progressive"]
		facets = facets.replace('\"', '').replace('\n', '').replace(' ', '')  
		PLog('typ: ' + typ); PLog('facets: ' + facets)
		if typ == "h264_aac_f4f_http_f4m_http":				# manifest.f4m auslassen
			continue
		audio = blockextract('\"audio\" :', rec)			# Datensätze je Typ
		# PLog(audio)	# bei Bedarf
		
		for audiorec in audio:					
			url = stringextract('\"uri\" : \"',  '\"', audiorec)			# URL
			quality = stringextract('\"quality\" : \"',  '\"', audiorec)
			if quality == 'high':							# high bisher identisch mit auto 
				continue
			quality=UtfToStr(quality);
			PLog(url); PLog(quality); 
			Plot_par=UtfToStr(Plot_par);
			
			PLog('Mark0')
			if url:		
				if url.find('master.m3u8') > 0:			# m3u8 enthält alle Auflösungen					
					title = quality + ' [m3u8]'
					# Sofortstart - direkt, falls Listing nicht Playable			
					if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true': 
						PLog('Sofortstart: SingleBeitrag')
						PLog(xbmc.getInfoLabel('ListItem.Property(IsPlayable)')) 
						# sub_path=''	# fehlt bei ARD - entf. ab 1.4.2019
						PlayVideo(url=url, title=title_org, thumb=thumb, Plot=Plot_par, sub_path='')
						return									

					#  "auto"-Button + Ablage master.m3u8:
					# Da 3Sat 2 versch. m3u8-Qualitäten zeigt,verzichten wir (wie bei ZDF_getVideoSources)
					#	auf Einzelauflösungen via Parseplaylist
					#	
					li = ardundzdf.ParseMasterM3u(li=li, url_m3u8=url, thumb=thumb, title=title, descr=Plot_par)
			
				else:									# m3u8 enthält Auflösungen high + med
					title = 'Qualitaet: ' + quality + ' | Typ: ' + typ + ' ' + facets 

					download_list.append(title + '#' + url)			# Download-Liste füllen	
					tagline	= tagline.replace('||','\n')			# s. tagline in ZDF_get_content				
					summ	= summ.replace('||','\n')				# 
					summ=UtfToStr(summ);tagline=UtfToStr(tagline); 	
					tag	= 	tagline + '\n\n' + summ	
					
					title=UtfToStr(title); tag=UtfToStr(tag);
					fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': ''}" %\
						(quote_plus(url), quote_plus(title), quote_plus(thumb), quote_plus(Plot_par))	
					addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
						mediatype='video', tagline=tag) # summary=summ) 
												
	if SETTINGS.getSetting('pref_use_downloads'):
		# high=0: 	1. Video bisher höchste Qualität:  [progressive] veryhigh
		tagline=tag_org
		li = ardundzdf.test_downloads(li,download_list,title_org,Plot_par,tag,thumb,high=0)  # Downloadbutton(s)
					
	xbmcplugin.endOfDirectory(HANDLE)

####################################################################################################
# 3Sat - TV-Livestream mit EPG
#	summ = epg (s. Main_3Sat)
def Live(name, epg='', Merk='false'):	
	PLog('Live: ' + name)
	title2 = name
	
	li = xbmcgui.ListItem()
	li = home(li, ID='3Sat')						# Home-Button
	
	url = 'https://zdfhls18-i.akamaihd.net/hls/live/744751/dach/high/master.m3u8'
	# epg_url = 'https://programm.ard.de/TV/ARD-Mediathek/Programmkalender/?sender=28007'	# entf. 
	epgname = 'ARD'; listname = '3sat'
	summary = u'automatische Auflösung';				
	title = 'Bandbreite und Auflösung automatisch'
	img	= R(ICON_TV3Sat)
	
	if not epg:
		epg = get_epg()

	if SETTINGS.getSetting('pref_video_direct') == 'true' or Merk == 'true':	# Sofortstart
		PLog('Sofortstart: SenderLiveResolution')
		Plot	 = 'Live: ' + name + '\n\n' + epg + '\n\n' + summary
		PlayVideo(url=url, title='3Sat Live TV', thumb=img, Plot=Plot, Merk=Merk)
		return	
							
	Plot	 = 'Live: ' + name + '\n\n' + epg
	Plot_par = Plot.replace('\n', '||')
	title=UtfToStr(title); Plot=UtfToStr(Plot);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': 'false'}" %\
		(quote_plus(url), quote_plus(title), quote_plus(img), quote_plus(Plot_par))
	addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, fparams=fparams, 
		mediatype='video', tagline=Plot) 		
	
	li =  ardundzdf.Parseplaylist(li, url, img, geoblock='', descr=Plot)	
	
	xbmcplugin.endOfDirectory(HANDLE)
	
#-----------------------------
def get_epg():		# akt. PRG-Hinweis von 3Sat-Startseite holen
	PLog('get_epg')
	# 03.08-2017: get_epg_ARD entfällt - akt. PRG-Hinweis auf DreiSat_BASE eingeblendet
	# epg_date, epg_title, epg_text = get_epg_ARD(epg_url, listname)
	page, msg = get_page(path=DreiSat_BASE)	
	if page == '':	
		msg1 = "Fehler in get_epg:"
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
		return ''
	
	epg = stringextract('>Jetzt live<', '</div>', page)
	epg = stringextract("class='time'>", '</h3>', epg)
	epg = epg.replace('</span>', ' | ')		# Bsp.: class='time'>10:15</span> Kölner Treff</h3>
	epg = cleanhtml(epg)		
	PLog(epg)
	return epg
	

####################################################################################################
#	Hilfsfunktonen
#----------------------------------------------------------------  

def CalculateDuration(timecode):				# 3 verschiedene Formate (s.u.)
	timecode = timecode.upper()	# Min -> min
	milliseconds = 0
	hours        = 0
	minutes      = 0
	seconds      = 0

	if timecode.find('P0Y0M0D') >= 0:			# 1. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
		d = re.search('T([0-9]{1,2})H([0-9]{1,2})M([0-9]{1,2}).([0-9]{1,3})S', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
			seconds = int ( d.group(3) )
			milliseconds = int ( d.group(4) )
					
	if len(timecode) == 9:						# Formate: '00:30 min'	
		d = re.search('([0-9]{1,2}):([0-9]{1,2}) MIN', timecode)	# 2. Format: '00:30 min' 	
		if(None != d):
			hours = int( d.group(1) )
			minutes = int( d.group(2) )
			PLog(minutes)
						
	if len(timecode) == 11:											# 3. Format: '1:50:30.000'
		d = re.search('([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).([0-9]{1,3})', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
			seconds = int ( d.group(3) )
			milliseconds = int ( d.group(4) )
	
	milliseconds += hours * 60 * 60 * 1000
	milliseconds += minutes * 60 * 1000
	milliseconds += seconds * 1000
	
	return milliseconds
#----------------------------------------------------------------
# 1. Format timecode '01:30' oder '00:30', Rest (Min, min o.ä.) wird abgeschnitten
# 2. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
def HourToMinutes(timecode):	
	if timecode.find('P0Y0M0D') >= 0:			# 1. Format: 'P0Y0M0DT5H50M0.000S', T=hours, H=min, M=sec
		d = re.search('T([0-9]{1,2})H([0-9]{1,2})M([0-9]{1,2}).([0-9]{1,3})S', timecode)
		if(None != d):
			hours = int ( d.group(1) )
			minutes = int ( d.group(2) )
	else:
		timecode =  timecode[0:5]
		if timecode.find(':') < 0:
			return timecode
		t =  timecode.split(':')
		hours = int(t[0])
		minutes = int(t[1])
	
	if hours > 0:
		minutes = (hours * 60) + minutes
	
	return str(minutes)
#----------------------------------------------------------------  
# nur für Anford. Videodaten mittels apiToken 	
def get_page3sat(path, apiToken):
	PLog("get_page3sat: " + path) 
	msg=''
	try:
		PLog(type(path))	
		path = BytesToUnicode(path) 
		PLog(type(path))	
		req = urllib.request.Request(path)
		req.add_header('Api-Auth', 'Bearer ' + apiToken)
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
		gcontext.check_hostname = False	# bzw. False
		r = urllib.request.urlopen(req, context=gcontext)
		page = r.read()
		PLog(page[:100])
	except Exception as exception:
		page = ''
		msg = str(exception)
		PLog(msg)
	PLog(len(page))
	return page, msg


