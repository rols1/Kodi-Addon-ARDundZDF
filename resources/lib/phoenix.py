# -*- coding: utf-8 -*-
################################################################################
#				phoenix.py - Teil von Kodi-Addon-ARDundZDF
#				benötigt Modul yt.py (Youtube-Videos)
#		Videos der Phoenix_Mediathek auf https://www.phoenix.de/ 
#
#	30.12.2019 Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	
################################################################################
# 	<nr>8</nr>										# Numerierung für Einzelupdate
#	Stand: 29.05.2022

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

import json		
import os, sys
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke
import string

import ardundzdf					# -> get_query,test_downloads,get_zdf_search 
from resources.lib.util import *
import resources.lib.yt	as yt		# Rahmen für pytube, mögl. Dev.-Problem s. dort

# Globals
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

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 				# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_PHOENIX	= 'https://www.phoenix.de'
PLAYLIST 		= 'livesenderTV.xml'	  	# enth. Link für phoenix-Live											

# Icons
ICON 			= 'icon.png'				# ARD + ZDF
ICON_PHOENIX	= 'phoenix.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MEHR 		= "icon-mehr.png"
ICON_ZDF_SEARCH = 'zdf-suche.png'
ICON_ARD_SEARCH = 'ard-suche.png'						
				
				
# Github-Icons zum Nachladen aus Platzgründen
ICON_DISKUSS	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/phoenix.png?raw=true'			
ICON_TVLIVE		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/tv-livestreams.png?raw=true'			
ICON_SEARCH		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/icon-search.png?raw=true'			
ICON_SENDUNGEN	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Sendungen.png?raw=true'			
ICON_DOSSIERS	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Themen_Dossiers.png?raw=true'			
ICON_RUBRIKEN	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Themen_Rubriken.png?raw=true'			
ICON_VERPASST	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Verpasst.png?raw=true'
		
# ----------------------------------------------------------------------			
def Main_phoenix():
	PLog('Main_phoenix:')
	
	li = xbmcgui.ListItem()
	liICON_TVLIVE = home(li, ID=NAME)			# Home-Button

	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'Sender: [B]alle Sender des ARD[/B] (nicht in phoenix allein)' 
		title=py2_encode(title); 
		func = "resources.lib.phoenix.Main_phoenix"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ARD", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=R(ICON_PHOENIX), 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)

	title="Suche auf phoenix"
	tag = "Suche Themen, Sendungen und Videos in phoenix"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Search", fanart=R(ICON_PHOENIX), 
		thumb=ICON_SEARCH, fparams=fparams, tagline=tag)
	# ------------------------------------------------------
			
	tag='[B]Phoenix Livestream[/B]'
	title,subtitle,vorspann,descr,href,sender,icon = get_live_data()
	title = '[B]LIVE: %s[/B]' % title
	
	if sender:
		tag = "%s | Herkunft: %s" % (tag, sender)
	summ = descr
	if subtitle:
		summ = '%s\n%s' % (subtitle, summ)
	if vorspann:
		summ = '%s\n%s' % (vorspann, summ)
	thumb = icon
	if icon == '':	
		thumb = ICON_TVLIVE
		
	title=py2_encode(title); href=py2_encode(href); tag=py2_encode(tag);
	fparams="&fparams={'href': '%s', 'title': '%s', 'Plot': '%s'}" % (quote(href), quote(title), quote(tag))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Live", fanart=R(ICON_PHOENIX),
		thumb=thumb, fparams=fparams, tagline=tag, summary=summ)
	# ------------------------------------------------------
	title = 'Sendung verpasst'
	tag=u"[B]Hinweis:[/B] Viele Sendungen existieren nicht in der phoenix-Mediathek, sondern nur bei den Partnersendern "
	tag=u"%sARD und ZDF (z.B. Dokus).\nDas Addon bietet in solchen Fällen eine weiterführende Suche an." % tag 
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Verpasst", 
		fanart=R(ICON_PHOENIX), thumb=ICON_VERPASST, tagline=tag, fparams=fparams)

	title="Themen: Rubriken (alle)"
	fparams="&fparams={'ID': 'Rubriken'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Themen", fanart=R(ICON_PHOENIX), 
		thumb=ICON_RUBRIKEN, fparams=fparams)
	
	title="Themen: Dossiers (alle)"
	fparams="&fparams={'ID': 'Dossiers'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Themen", fanart=R(ICON_PHOENIX), 
		thumb=ICON_DOSSIERS, fparams=fparams)
	
	title="Sendungen"
	fparams="&fparams={'ID': 'Sendungen'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.Themen", fanart=R(ICON_PHOENIX), 
		thumb=ICON_SENDUNGEN, fparams=fparams)
	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
			
# ----------------------------------------------------------------------
# die json-Seite enthält ca. 4 Tage EPG - 1. Beitrag=aktuell
# 15.08.2020 Verwendung ZDFstreamlinks (util) für href (master.m3u8)
#
def get_live_data():
	PLog('get_live_data:')
	path = "https://www.phoenix.de/response/template/livestream_json"
	page, msg = get_page(path=path)			
	if page == '':	
		msg1 = "get_live_data:"
		msg2 = msg
		# MyDialog(msg1, msg2, '')
		PLog("%s | %s" % (msg1, msg2))	
	PLog(len(page))			
	
	title='';subtitle='';vorspann='';descr='';href='';sender='';thumb=''
	if page:
		# Kurzf. möglich: {"title":"tagesschau","subtitel":"mit Geb\u00e4rdensprache",
		#	"typ":"","vorspann":""}
		if '":"' in page:					# möglich: '":"', '": "'
			page = page.replace('":"', '": "')
		page = page.replace('\\"', '*')	
		page = 	transl_json(page)					
		PLog(page[:80])
		title 	= stringextract('"titel": "', '"', page)		# titel!
		subtitle= stringextract('"subtitel": "', '"', page)
		vorspann= stringextract('"vorspann": "', '"', page)
		descr	= stringextract('"text": "', '"', page)			# html als Text
		sender	= stringextract('sender": "', '"', page)
		icon	= stringextract('bild_l": "', '"', page)		# bild_s winzig
		if icon == '':
			icon = stringextract('bild_m": "', '"', page)
		PLog("icon: " + icon)
		if icon != '' and icon.startswith('http') == False:
			icon = BASE_PHOENIX + icon

		title=transl_json(title); subtitle=transl_json(subtitle); 
		vorspann=transl_json(vorspann); 
		descr=cleanhtml(descr); descr=transl_json(descr)
		descr=unescape(descr); descr=descr.replace("\\r\\n", "\n")
		
	zdf_streamlinks = get_ZDFstreamlinks(skip_log=True)
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	href=''
	for line in zdf_streamlinks:
		webtitle, href, thumb, tagline = line.split('|')
		if up_low('phoenix') in up_low(webtitle): 
			href = href
			break
	
	PLog("Satz6:")
	PLog(title); PLog(subtitle); PLog(vorspann); PLog(descr); PLog(href);
	PLog(sender); PLog(icon);					
	return title,subtitle,vorspann,descr,href,sender,icon
# ----------------------------------------------------------------------
# path via chrome-tools ermittelt. Ergebnisse im json-Format
# 25.05.2021 Suchlink an phoenix-Änderung angepasst
# 28.06.2021 erneut angepasst
# 09.11.2021 wegen key-Problem ("0", "1"..) Wechsel json -> string-Auwertung,
#	s. GetContent + ThemenListe
def phoenix_Search(query='', nexturl=''):
	PLog("phoenix_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='phoenix')
	PLog(query)
	if  query == None or query == '':
		return ""
		
	query=py2_encode(query);
	if nexturl == '':
		# path = 'https://www.phoenix.de/suche.html?vt=%s' % quote(query)
		path = "https://www.phoenix.de/response/template/suche_select_json/term/%s/sort/online" % quote(query)
	else:
		path = nexturl
	PLog(path)
	page, msg = get_page(path=path)	
	if page == '':						
		msg1 = 'Fehler in Suche: %s' % query
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
				
	if page.find('hits":0,') >= 0:
		msg1 = 'Leider kein Treffer.'
		MyDialog(msg1, '', '')
		return
		
	page = page.replace('\\/', '/')		# json-raw Links
	page = page.replace('\\"', '*')		# "-Zeichen ersetzen
	search_cnt = stringextract('hits":', ',', page)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button

	li = GetContent(li, page)						
		
	if '"next":' in page:				# Mehr-Seiten, hier "next" statt "next_url"
		next_url	= stringextract('next":"', '"', page)
		if next_url:
			li = xbmcgui.ListItem()		# Kontext-Doppel verhindern
			next_url = BASE_PHOENIX + next_url
			skipcnt =  stringextract('skip/', '/', next_url)
			PLog("next_url: %s, skipcnt: %s" % (next_url, skipcnt))	
			img = R(ICON_MEHR)
			title = u"Weitere Beiträge"
			tag = u"Beiträge gezeigt: %s, gesamt: %s" % (skipcnt, search_cnt)

			next_url=py2_encode(next_url); query=py2_encode(query); 
			fparams="&fparams={'nexturl': '%s', 'query': '%s'}" %\
				(quote(next_url), quote(query))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Search", fanart=img, 
				thumb=img, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# GetContent: Auswertung der json-Datensätzen in items
#	base_img = Kopfbild
# turn_title: veranlasst Tausch Titel/Subtitel
# 29.01.2020 mediatype=video: Video lässt sich beim Autostart
#	nicht mehr abschalten - auf '' gesetzt
# 09.11.2021 wegen key-Problem ("0", "1"..) Wechsel json -> string-Auwertung,
#	s.a. ThemenListe
# 15.04.2022 ID: skip vinhalt + Zukunft bei ID="Verpasst"
def GetContent(li, page, base_img=None, turn_title=True, get_single='', ID=''):
	PLog('GetContent:')

	mediatype=''			# Kennzeichn. als Playable hier zu unsicher (Bsp. Plenarwochen)	
	if not base_img:
		base_img = R(ICON_PHOENIX)		# Ergebnisseite ohne Bilder, Phoenix-Bild verwenden	

	items = blockextract('{"link":',  page)
	if len(items) == 0:					# Folgeseiten aus BeitragsListe
		items = blockextract('"link":',  page)
	PLog(len(items))
	for item in items:	
		vorspann=''; tag=''; summ=''; summ_par=''; subtitel=''; online=''
		single = False; video='false'

		img		= stringextract('"bild_m":"', '"', item)	# 31.12.2021 Reihenfolge wg. fehlender Bilder
		if img == '':										#	gedreht: medium, medium_large, large
			img	= stringextract('"bild_ml":"', '"', item)
		if img == '':	
			img	= stringextract('"bild_l":"', '"', item)	# nachrangig, da falsche Url mögl.
		if img.startswith('http') == False:
			img = BASE_PHOENIX + img
		if img == '' or 'placeholder' in img:
			img = base_img				
		if '%' in img:								# Dekodierung  quotierte img-url's
			#img = decode_url(img)					# Bsp.: ..17-3083922,(ap,XAZ109,A15_11_2017),russisches..
			PLog("decode_img: " + img)				# für Kodi Dekodierung nicht erforderl.
			
		# "inhalt_video":true muss nicht stimmen, Bsp.: 
		#	https://www.phoenix.de/response/template/suche_select_json/term/dialog/sort/score
		#if "inhalt_video" in item:
		#	video = item["inhalt_video"]	# false, true
		
		url	= stringextract('link":"', '"', item)
		PLog('url: ' + url)
		if url == '':		
			if  ID != "Verpasst":					# z.B. bei Tagesschau leer
				continue
		url	= BASE_PHOENIX + url 					# Bsp. augstein-und-blome-s-121540.html	
		html_ref = "Link: .." + url.split('-')[-1]	# 121540.html	

		title= stringextract('titel":"', '"', item)
		subtitel = stringextract('subtitel":"', '"', item)
		vorspann = stringextract('vorspann":"', '"', item)
		typ	= stringextract('typ":"', '"', item)	# Artikel, Doku, Ereignis..
		if typ == '':
			if  ID != "Verpasst":					# z.B. bei Tagesschau leer
				continue
		
		# Formate Sendezeit: "2017-02-26 21:45:00", "2018-01-27 00:30"
		if "online" in item:	
			datestamp = stringextract('datestamp":"', '"', item)
			online = getOnline(datestamp)
		if online == '':						# vorh. bei Suche, nicht in response-Beiträgen
			if "sendung" in item:
				datestamp = stringextract('sendezeit":"', '"', item)
				online = getOnline(datestamp)	
		if online == '':						# Beiträge aus BeitragsListe im 2. Durchlauf
			datestamp = stringextract('online":"', '"', item)
			online = getOnline(datestamp)	
		if online == '':						# vorh. bei Suche, nicht in response-Beiträgen
			online = "Sendezeit fehlt"
			# trotz Sendezeit kann Video fehlen - Nachprüfung in SingleBeitrag
		else:
			if "inhalt_video" in item:			# trotz False Videos möglich (Bsp. Plenarwochen)
				single = True
		if get_single:							# Zwangsvorgabe aus BeitragsListe (2. Durchlauf)
			single = True
		PLog("typ: %s, %s" % (typ, online))
		PLog('single: ' + str(single))	
		# Link kann trotz VIDEO-Kennz. mehrere Beiträge enthalten - Nachprüfung in
		#	SingleBeitrag
		if single:							# Typ-Angabe (Artikel, Doku..) nicht bei Videos
			tag = u"VIDEO | %s" % online
		else:
			tag = u"%s | Folgeseiten | %s"	% (typ, html_ref)
			
		if SETTINGS.getSetting('pref_only_phoenix_videos') == 'true': 
			if ID != "Verpasst":
				vinhalt = stringextract('inhalt_video":', ',', item)
				PLog('vinhalt: ' + str(vinhalt))
				if vinhalt == 'false':					# false, wenn z.Z. kein phoenix-Video vorhanden 
					continue		
				if not single or 'Zukunft' in online:	# skip Beiträge ohne Videos, künftige Videos
					continue
				
		if turn_title and subtitel:
			t = title
			title = subtitel; subtitel = t
		
		if subtitel:		
			summ = subtitel	
		if vorspann:
			summ = u"[B]%s[/B]\n\n%s" % (summ, vorspann)
			summ_par = summ.replace('\n', '||')
			
		title = transl_json(title); summ = transl_json(summ); 
		summ = repl_json_chars(summ);  title = repl_json_chars(title);

		PLog('Satz1:')
		PLog(url); PLog(img); PLog(title); PLog(subtitel); PLog(summ[:80]); PLog(tag)
		url=py2_encode(url); title=py2_encode(title); img=py2_encode(img); summ_par=py2_encode(summ_par);
		tag=py2_encode(tag);
		if single:
			fparams="&fparams={'title': '%s', 'path': '%s', 'html_url': '%s', 'tagline': '%s', 'summary': '%s', 'thumb': '%s'}" %\
				(quote(title), quote(url), quote(url), quote(tag), quote(summ_par), quote(img))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.SingleBeitrag", fanart=img, 
				thumb=img, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)				
		else:
			fparams="&fparams={'path': '%s', 'html_url': '%s', 'title': '%s'}" %\
				(quote(url), quote(url), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.BeitragsListe", fanart=img, 
				thumb=img, fparams=fparams, summary=summ, tagline=tag, mediatype='')

	return li

# ----------------------------------------------------------------------
# BeitragsListe: Liste der json-Datensätze in url
#	Aufrufer: GetContent (Mehrfach-Beiträge)
# 09.11.2021 wegen key-Problem ("0", "1"..) Wechsel json -> 
#	string-Auwertung, Erzwingung von Einzelbeiträgen in
#	GetContent (get_single) 
#
def BeitragsListe(path, html_url, title, skip_sid=False):
	PLog('BeitragsListe:')
	
	# ev. für sid split-Variante aus phoenix_Search verwenden
	if skip_sid == False:				# weitergeleitete bereits mit response-url
		sid 	= re.search(u'\-(\d+)\.html', path).group(1)	# Bsp. ../russland-r-252413.html
		url 	= 'https://www.phoenix.de/response/id/'	+ sid
	else:
		url = path
	PLog('url: ' + url)
	PLog('html_url: ' + html_url)	
	
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in BeitragsListe: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	page = page.replace('\\/', '/')		# json-raw Links
	page = page.replace('\\"', '*')		# "-Zeichen ersetzen
	page = page.replace('": "', '":"')  # Blank entf. (komp. mit GetContent)
	
	base_img = ICON_PHOENIX				# Fallback
	if 'bild_l' in page:
		base_img	= BASE_PHOENIX + stringextract('"bild_l":"', '"', page)
		

	if '"sendungen":' in page:
		pos = page.find('"sendungen":')
		page = page[pos:]
		PLog(pos)
	PLog(len(page))
	PLog(page[:200])
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
		
	li = GetContent(li, page, base_img=base_img, turn_title=True, get_single=True)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
####################################################################################################
# wie Webseite: Themen: Rubriken,  Themen: Dossiers - zusätzlich auch Sendungen (Struktur identisch)
#	 				
def Themen(ID):							# Untermenüs zu ID
	PLog('Themen, ID: ' + ID)
		
	if ID == 'Rubriken':
		url = 'https://www.phoenix.de/response/template/rubrik_overview_json'
	if ID == 'Dossiers':
		url = 'https://www.phoenix.de/response/template/dossier_overview_json'
	if ID == 'Sendungen':
		url = 'https://www.phoenix.de/response/template/sendungseite_overview_json'
		
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in Themen: %s' % ID
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return 
	PLog(len(page))
	
	jsonObject = json.loads(page)
	search_cnt = jsonObject["content"]['hits']
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
	
	items = jsonObject["content"]['items']
	PLog(len(items))
	for item in items:
		# img 	=  BASE_PHOENIX + item["icon"]		# diese svg-Grafik in Plex nicht darstellbar
		img 	=  BASE_PHOENIX + item["bild_m"]	
		url 	= BASE_PHOENIX + item["link"]		# Bsp. ../russland-r-252413.html
		title 	= item["titel"]
		typ		= item["typ"]
		
		title = cleanhtml(title); title = mystrip(title);
		title = repl_json_chars(title)
	
		PLog('Satz2:')
		PLog(url); PLog(img); PLog(title)
		url=py2_encode(url); title=py2_encode(title);
		fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" %\
			(quote(url), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.ThemenListe", fanart=img, 
			thumb=img, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 07.11.2020 Hinweis: Datumsangaben für "online" / "sendezeit" können 
#	vor den Datumsangaben im "subtitel" liegen (Bsp. Rubriken/Bundestag,
#	sowohl Web- als auch json-Quellen).
# 09.11.2021 wegen key-Problem ("0", "1"..) Wechsel json -> string-Auwertung,
#	Berücksicht. weiterer Seiten (next_url)
#
def ThemenListe(title, ID, path, next_url=''):				# Liste zu einzelnem Untermenü
	PLog('ThemenListe: ' + title)
	PLog('ID: ' + ID)
	PLog('next_url: ' + next_url)
	title_org = title	
	
	if next_url == '':										# 1. Aufruf
		sid 	= re.search(u'\-(\d+)\.html', path).group(1)	# Bsp. ../russland-r-252413.html
		url 	= 'https://www.phoenix.de/response/id/'	+ sid
	else:
		url = next_url
	PLog('url: ' + url)

	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in ThemenListe: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return 
	PLog(len(page))
	page = page.replace('\\/', '/')		# json-raw Links
	page = page.replace('\\"', '*')		# "-Zeichen ersetzen
	
	base_img = ICON_PHOENIX				# Fallback
	if 'bild_l' in page:
		base_img	= BASE_PHOENIX + stringextract('"bild_l":"', '"', page)
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
		
	li = GetContent(li, page, base_img=base_img, turn_title=True)
	
	if '"next_url":' in page:			# Mehr-Seiten
		next_url	= stringextract('next_url":"', '"', page)
		if next_url:
			li = xbmcgui.ListItem()		# Kontext-Doppel verhindern
			next_url = BASE_PHOENIX + next_url
			PLog("next_url: " + next_url)	
			img = R(ICON_MEHR)
			title = u"Weitere Beiträge"
			tag = "%s zu: [B]%s[/B]" % (title, title_org)
			# tag = u"Beiträge gezeigt: %s, gesamt: %s" % (len(items), search_cnt) # nicht verfügbar
			
			title_org=py2_encode(title_org); ID=py2_encode(ID);  
			path=py2_encode(path); next_url=py2_encode(next_url);  
			fparams="&fparams={'title': '%s', 'ID': '%s', 'path': '%s', 'next_url': '%s'}" %\
				(quote(title_org), quote(ID), quote(path), quote(next_url))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.ThemenListe", fanart=img, 
				thumb=img, fparams=fparams, tagline=tag)
		
				
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 15.04.2022 Verpasst Woche - Liste Wochentage
#
def Verpasst():
	PLog('Verpasst:')

	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')					# Home-Button

	wlist = list(range(0,7))
	now = datetime.datetime.now()

	for nr in wlist:
		rdate = now - datetime.timedelta(days = nr)
		startDate = rdate.strftime("%Y-%m-%dT03:30:00.000Z")
		myDate  = rdate.strftime("%d.%m.")		# Formate s. man strftime (3)
		
		rdate2 = now - datetime.timedelta(days = nr-1)

		iWeekday = rdate.strftime("%A")
		iWeekday = transl_wtag(iWeekday)
		iWeekday = iWeekday[:2].upper()
		if nr == 0:
			iWeekday = 'HEUTE'	
		if nr == 1:
			iWeekday = 'GESTERN'	
		title =	"%s %s" % (iWeekday, myDate)	# DI 09.04.
		day = nr								# VerpasstContent: 0days, -1days usw
		
		PLog("Satz7:")
		PLog(title); PLog(nr); PLog(iWeekday)
		fparams="&fparams={'title': '%s', 'nr': '%d'}" % (title, nr)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.VerpasstContent", fanart=ICON_VERPASST, 
			thumb=ICON_VERPASST, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 15.04.2022 Inhalt des gewählten Tages <- Verpasst
# Auswertung -> GetContent wie phoenix_Search
#
def VerpasstContent(title, nr):
	PLog('VerpasstContent: ' + title)
	base = "https://www.phoenix.de/response/template/tvprogramm_tag_json/datum/"
	
	if nr == "0":
		day = "0days"
	else:
		day = "-%sdays" % nr
	path = base + day
	page, msg = get_page(path)
	if page == '':	
		msg1 = 'Fehler in VerpasstContent'
		msg2=msg
		MyDialog(msg1, msg2, "")	
		return
	PLog(len(page))
	
	page = page.replace('\\/', '/')		# json-raw Links
	page = page.replace('\\"', '*')		# "-Zeichen ersetzen
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
	
	msg1 = title
	msg2 = "phoenix"
	icon = ICON_VERPASST
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=False)	

	li = GetContent(li, page, ID="Verpasst")						
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

####################################################################################################
# Ermittlung der Videoquellen ähnlich ZDF-Mediathek:
#	1. Die Url der Homepage der Sendung enthält am Ende die Sendungs-ID (../am-05062018-a-262217.html).
#	2. www.phoenix.de/response/id/xxx liefert die Youtube-ID + Infos zu relevanten Webseiten
#		der Umweg über die frühere Ladekette  (../beitrags_details.php, ../vod/ptmd/phoenix) ist
#		entfallen.
#	3. Erweiterung: Auswertung ev. weiterer vorh. Einzelbeiträge (Bsp. Bundestag/Plenarwoche,
#		i.d.R. Beiträge für 2 Tage, Youtube-/Normal-Videos gemischt) - json-Seiten, Videoquellen
#		fehlen hier. Auswertung: Schleife über die Beiträge, einz. Beitrag -> SingleBeitragVideo 
#		Direktsprung bei nur 1 Video -> skip SingleBeitragVideo
#		
def SingleBeitrag(title, path, html_url, summary, tagline, thumb):	
	PLog('SingleBeitrag: ' + title);
	PLog(summary); PLog(tagline); 
	title_org = title
	tag_org = tagline
	summ_org = summary
	
	# ev. für sid split-Variante aus phoenix_Search verwenden
	try:								# url: leer möglich bei Verpasst-Beiträgen
		sid 	= re.search(u'-(\d+)\.html', path).group(1)
		url 	= 'https://www.phoenix.de/response/id/'	+ sid
	except:
		sid=''; url=''
	PLog('url: ' + url)
	PLog('html_url: ' + html_url)	

	page=''; msg=''
	msg1 = u"Kein phoenix-Video zu >%s< gefunden." % title
	if url:
		page, msg = get_page(path=url)	
		msg1 = 'Fehler in SingleBeitrag: %s' % title
	if page == '':						
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return 
	PLog(len(page))
	page = page.replace('\\"', '*')									# "-Zeichen ersetzen
		
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'	
	
	items = blockextract('typ":"video-',  page)						# kann fehlen z.B. bei Phoenix_Suche 
	PLog(len(items))
	if len(items) == 0:
		if 'text":"<div><strong>' in page or 'text":"<p><strong>':	# Suchtexte
			msg1 = u"Kein phoenix-Video zu >%s< gefunden.\nFundstellen bei den Partnersendern möglich.\nDort suchen?" % title
			ret=MyDialog(msg1, '', '', ok=False, yes='OK', heading='Weiterleitung?')
			PLog(ret)
			if ret:
				get_zdf_search(li,page,title)
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	# endOfDirectory für get_zdf_search erford.
			else:
				return												# Directory-Error, erspart aber Klick  
		else:
			msg1 = 'Kein phoenix-Video zu >%s< gefunden.' % title
			msg2 = 'Ursache unbekannt'
			MyDialog(msg1, msg2, '')
			return													# Directory-Error, erspart aber Klick  

		
	PLog(len(items))		
	s1 		= stringextract('titel": "', '"', page)				# Seiten-Titel + -Subtitel: Leitthema
	s2 		= stringextract('subtitel": "', '"', page)			
	tag 	= "Leitthema: [COLOR red]%s[/COLOR]" % (s1)
	if s2:														# Subtitel kann fehlen
		tag 	= "Leitthema: [COLOR red]%s | %s[/COLOR]" % (s1, s2)
	
	for item in items:
		#PLog(item)		# bei Bedarf
		typ 	= stringextract('typ":"', '"', item)		
		PLog("videotyp: " + typ)
		title 	= stringextract('titel":"', '"', item)	
		img		= stringextract('"bild_l": "', '"', item)
		if img == '':	
			img	= stringextract('"bild_m": "', '"', item)
		if img.startswith('http') == False:
			img = BASE_PHOENIX + img
		
		vid=''; summ=''; 
		# youtube: 	text -> Title (eigener Titel fehlt)
		# smubl:	text entf. (ident. mit "titel")
		if typ == "video-youtube":
			vid	= stringextract('id":"', '"', item)
			title 	= stringextract('text":"', '"', item)		# entspr. bei smubl dem Titel
			if 'o:OfficeDocumentSettings' in title:				# Fliesstext enthält vorwiegend Formatierung
				title = ''
			title = cleanhtml(title);title = unescape(title);   # title kann fehlen - Ersatz s.u.
			title = title.replace('\\r\\n', ''); title = title.strip()
			summ = "Youtube-Video" 
		else:	# typ "video-smubl"
			if '<basename>' in item:							# xml, Bsp. <basename> 210829_1200_fruehschoppen
				vid = stringextract('<basename>', '</', item)
			else:												# json-Formate	
				vid = stringextract('basename": ', ',', item)	# json,  ev. nicht mehr relevant
				if vid == '':										
					vid = stringextract('content": ', ',', item)# json, Bsp. "content": 2339044, 
			summ = "phoenix-Video" 
			
		PLog('typ %s, vid %s' % (typ, vid))
		if title == '':
			title='%s | %s' % (s1, s2)							# Seiten-Titel + -Subtitel aus Leitthema (s.o.)
		title = repl_json_chars(title)
		if vid:
			PLog('Satz3:')
			PLog(vid); PLog(title); PLog(url); PLog(tag[:80]); PLog(summ[:80]); PLog(img); 
			title=py2_encode(title); url=py2_encode(url);
			vid=py2_encode(vid); tag=py2_encode(tag); tag_org=py2_encode(tag_org);
			img=py2_encode(img); summ=py2_encode(summ); summ_org=py2_encode(summ_org);
			tag_par = summ.replace('\n', '||')					# || Code für LF (\n scheitert in router)

			if 	typ == 'video-smubl':
				fparams="&fparams={'content_id': '%s', 'title': '%s', 'tagline': '%s', 'thumb': '%s'}" %\
					(quote_plus(vid), quote_plus(title), quote_plus(tag_org), quote_plus(img))	
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.get_formitaeten", 
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)	
					
			if typ == 'video-youtube':
				fparams="&fparams={'url': '%s','vid': '%s', 'title': '%s', 'tag': '%s', 'summ': '%s', 'thumb': '%s'}" %\
					(quote_plus(url), quote_plus(vid), quote_plus(title), quote_plus(tag_org), 
					quote_plus(summ_org), quote_plus(img))	
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.yt_get", 
					fanart=img, thumb=img, fparams=fparams, tagline=tag, summary=summ, mediatype=mediatype)	
				
		else:
			PLog('vid fehlt: %s' % title)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


# ----------------------------------------------------------------------
# Quersuche beim ZDF - Aufrufer SingleBeitrag
# Dokus: Suche mit Title und Subtitel (Achtung: gedreht in GetContent
#	für Download + Merkliste)
# phoenix history: Suchbuttons erstellen mit Titeln aus 1. Satz der Beschreibung
# 15.04.2022 erweitert für ARD-Suche
#
def get_zdf_search(li, page, title):
	PLog('get_zdf_search:')
	PLog(title)
	title_call = title
	
	pos = page.find('"related"')		# Hinw. relevante Beiträge abschneiden
	page = page[:pos]
	page = page.replace('\\/', '/')	
	PLog(page[:100])

	title_org = stringextract('titel": "', '"', page)  		# hier mit Blank
	PLog(title_org)
	stitle_org = stringextract('subtitel": "', '"', page)	# hier mit Blank
	tag_org = "Suche phoenix-Beitrag beim Partnersender %s"
	summ = stringextract('text":"', '"}', page)
	summ = summ.replace('\\r\\n', ' ')
	summ = cleanhtml(summ); summ = unescape(summ);
	summ = repl_json_chars(summ) 
	PLog("Satz4:"); 
	PLog(title); PLog(stitle_org); PLog(summ[:80]); 
	
	if "phoenix history" not in title_org: 					# Dokus mit Titel + Subtitel suchen 
		if stitle_org:
			query = stitle_org				
			title = "1. ZDFSuche (Titel): %s" % query
			tag = tag_org % "ZDF"	
			query=py2_encode(query); title=py2_encode(title);
			# return ardundzdf.ZDF_Search(query=query, title=title)	# Altern.: Direktsprung nur mit Subtitel
			query=py2_encode(query); title=py2_encode(title); 	# Suche mit Titel
			fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
				thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)
		
		if title_org:
			query = title_org
			title = "2. ZDFSuche (Subtitel): %s" % query	 	# Suche mit Subtitel
			tag = tag_org % "ZDF"	
			query=py2_encode(query); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
				thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)

		if stitle_org:
			query = stitle_org
			title = "3. ARDSuche (Titel): %s" % query	 	# ARD-Suche mit Titel
			tag = tag_org % "ARD"	
			query=py2_encode(query); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s', 'sender': 'ARD' }" % (quote(query), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
				fanart=R(ICON_ARD_SEARCH), thumb=R(ICON_ARD_SEARCH), tagline=tag, summary=summ, fparams=fparams)

		if title_org:
			query = title_org
			title = "4. ARDSuche (Subtitel): %s" % query	 	# ARD-Suche mit Subtitel
			tag = tag_org % "ARD"	
			query=py2_encode(query); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s', 'sender': 'ard' }" % (quote(query), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDSearchnew", 
				fanart=R(ICON_ARD_SEARCH), thumb=R(ICON_ARD_SEARCH), tagline=tag, summary=summ, fparams=fparams)

	else:
		items = blockextract('text":"<div><strong>',  page)	
		if len(items) == 0:
			items = blockextract('text":"<p><strong>',  page)		
		PLog(len(items))
		title_old=''
		for item in items:
			PLog(item[:100])
			query_lable = stringextract('text":"<div><strong>', '</strong>', item)
			if query_lable == '':
				query_lable = stringextract('text":"<p><strong>', '</strong>', item)
			query_lable = query_lable[:100]				# begrenzen
			query_lable = cleanhtml(query_lable); query_lable = unescape(query_lable)
			query = query_lable.replace('+', ' ')
			title = "ZDFSuche: %s" % query_lable.strip()
			if title == title_old:			# Doppel vermeiden (hier ev. Extrakt erweitern)
				continue
			title_old = title
			
			summ = stringextract('text":"', '"}', item)
			summ = summ.replace('\\r\\n', ' ')
			summ = cleanhtml(summ); summ = unescape(summ);
			summ = repl_json_chars(summ) 
			PLog("Satz5:"); PLog(title); PLog(query); PLog(summ[:80]); 
			
			query=py2_encode(query); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
				thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# beitrags_details 	-> xml-format, 06/2021 Umstellung auf json (s. basename)
# ngplayer_2_3		-> json-Format
def get_formitaeten(content_id,title,tagline,thumb):
	PLog('get_formitaeten')
	PLog('content_id: ' + content_id)
	if content_id == '':							# sollte nicht vorkommen
		msg1 = '%s | content_id fehlt' % title
		MyDialog(msg1, '', '')
		return li
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
	
	url = 'https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?ak=web&ptmd=true&id=' + content_id
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in get_formitaeten: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
	
	basename = stringextract('assetid":"',  '"', page) 			# Bsp. "assetid":"210416_phx_doku_awri_5"
	#if basename == '':
	#	continue
	url = 'https://tmd.phoenix.de/tmd/2/ngplayer_2_3/vod/ptmd/phoenix/' + basename
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in get_formitaeten: %s' % title
		msg2 = msg
		MyDialog(msg1, msg2, '')
		return li
	PLog(len(page))
	
	formitaeten = blockextract('"formitaeten"',  page)		# Video-URL's ermitteln - wie ZDF-Mediathek
	# PLog(formitaeten)
	geoblock =  stringextract('geoLocation',  '}', page) 
	geoblock =  stringextract('"value" : "',  '', geoblock).strip()
	PLog('geoblock: ' + geoblock)						# i.d.R. "none", sonst "de"
	if geoblock == 'de':			# Info-Anhang für summary 
		geoblock = ' | Geoblock!'
	else:
		geoblock = ''	

	duration =  stringextract('duration',  '}', page) 
	# PLog('duration: ' + duration)						
	try:													# Bsp.: "value" : 4943000 
		duration = re.search(u'value" : (\d+)', duration).group(1)
	except:
		duration = ''
	if duration:											# wie yt_init.millisecs (yt_get) 
		duration = seconds_translate(int(int(duration) / 1000))
	PLog('duration: ' + duration)						
			
			
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	title_call = title
	if duration:
		tagline = "%s | %s\n\nSendung: %s"	% (duration, tagline, title_call)
	else:
		tagline = "%s\n\nSendung: %s"	% (tagline, title_call)

	Plot_par = tagline.replace('\n', '||')
	for rec in formitaeten:									# Datensätze gesamt
		# PLog(rec)		# bei Bedarf
		typ = stringextract('"type" : "', '"', rec)
		facets = stringextract('"facets" : ', ',', rec)	# Bsp.: "facets": ["progressive"]
		facets = facets.replace('"', '').replace('\n', '').replace(' ', '')  
		if  facets == '[]':
			facets = ''
		PLog('typ: ' + typ); PLog('facets: ' + facets)
		if typ == "h264_aac_f4f_http_f4m_http":				# manifest.fm auslassen
			continue
		audio = blockextract('"audio" :',  rec)				# Datensätze je Typ
		PLog(len(audio))
		# PLog(audio)	# bei Bedarf
		for audiorec in audio:		
			url = stringextract('"uri" : "',  '"', audiorec)			# URL
			quality = stringextract('"quality" : "',  '"', audiorec)
			if quality == 'high':						# high bisher identisch mit auto 
				continue
 
			PLog(url); PLog(quality); PLog(tagline); 
			if url:
				if url.endswith('master.m3u8'):
					if SETTINGS.getSetting('pref_video_direct') == 'true': 	# or Merk == 'true':	# Sofortstart
						PLog('Sofortstart: phoenix get_formitaeten')
						li.setProperty('IsPlayable', 'false')				# verhindert wiederh. Starten nach Stop
						PlayVideo(url=url, title=title_call, thumb=thumb, Plot=Plot_par)
						return
				
				title = u'Qualität: ' + quality + ' | Typ: ' + typ + ' ' + facets 
				if 'mp4' in typ:
					download_list.append(title + '#' + url)	# Download-Liste füllen	
						
				title_call=py2_encode(title_call)
				title=py2_encode(title); url=py2_encode(url);
				thumb=py2_encode(thumb); Plot_par=py2_encode(Plot_par); 
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" %\
					(quote_plus(url), quote_plus(title_call), quote_plus(thumb), quote_plus(Plot_par))	
				addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=thumb, thumb=thumb, fparams=fparams, 
					mediatype='video', tagline=tagline) 
					
	if 	download_list:	# Downloadbutton(s), high=0: 1. Video = höchste Qualität	
		# Qualitäts-Index high: hier Basis Bitrate (s.o.)
		title_org = title_call
		summary_org = ''
		tagline_org = repl_json_chars(tagline)
		# PLog(summary_org);PLog(tagline_org);PLog(thumb);
		li = ardundzdf.test_downloads(li,download_list,title_org,summary_org,tagline_org,thumb,high=0)  
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# Phoenix - TV-Livestream mit EPG
# 23.04.2022 Parseplaylist entfernt (ungeeignet für Mehrkanal-Streams)
# 
def phoenix_Live(href, title, Plot):	
	PLog('phoenix_Live:')

	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button

	img = ICON_TVLIVE
	if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true'	# Sofortstart
		PLog('Sofortstart: phoenix_Live')
		PlayVideo(url=href, title=title, thumb=img, Plot=Plot)
		return	
							
	Plot_par = Plot.replace('\n', '||')
	title=py2_encode(title); href=py2_encode(href); img=py2_encode(img);
	Plot_par=py2_encode(Plot_par);
	label = title.replace('Live', 'auto')
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': 'false'}" %\
		(quote_plus(href), quote_plus(title), quote_plus(img), quote_plus(Plot_par))
	addDir(li=li, label=label, action="dirList", dirID="PlayVideo", fanart=img, thumb=img, 
		fparams=fparams, mediatype='video', tagline=Plot) 		
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# getOnline: 1. Ausstrahlung
# Format datestamp: "2017-02-26 21:45:00", 2018-05-24T16:50:00 19-stel.
#	05.06.2020 hinzugefügt: 2018-05-24T16:50:00Z (Z wird hier entfernt)
#	beim Menü Sendungen auch  2018-01-20 00:30 16 stel.
# time_state checkt auf akt. Status, Zukunft und jetzt werden rot gekennzeichnet
def getOnline(datestamp, onlycheck=False):
	PLog("getOnline: " + datestamp)
	PLog(len(datestamp))
	if datestamp == '' or '/' in datestamp:
		return '' 

	if datestamp.endswith('Z'):							# s.o.
		datestamp = datestamp[:len(datestamp)-1]
	
		
	online=''; check_state=''
	if len(datestamp) == 19 or len(datestamp) == 16:
		senddate = datestamp[:10]
		year,month,day = senddate.split('-')
		sendtime = datestamp[11:]
		if len(sendtime) > 5:
			sendtime = sendtime[:5]
		
		checkstamp = "%s %s" % (senddate, sendtime)
		check_state= time_state(checkstamp)
		if check_state:									# Kennz. nur Zukunft und jetzt
			check_state = " (%s)" % check_state
		
		online = "Online%s: %s.%s.%s, %s Uhr"	% (check_state, day, month, year, sendtime)	
	
	if onlycheck == True:
		return check_state
	else:
		return online
	
# ----------------------------------------------------------------------
# Prüft datestamp auf Vergangenheit, Gegenwart, Zukunft
#	Format datestamp: "2020-01-26 11:15:00" 19 stel., in
#	getOnline auf 16 Stellen reduz. (o. Sek.)
def time_state(checkstamp):
	PLog("time_state: " + checkstamp)		
	date_format = "%Y-%m-%d %H:%M"

	start = datetime.datetime.fromtimestamp(time.mktime(time.strptime(checkstamp, date_format)))
	# PLog(start)
	now = datetime.datetime.now()
	# PLog(now)
	if start < now:
		check_state = '' 	# 'Vergangenheit'
	elif start > now:
		check_state = "[B][COLOR red]%s[/COLOR][/B]" % 'Zukunft'
	else:
		check_state = 'jetzt'
	
	return check_state
# ----------------------------------------------------------------------











