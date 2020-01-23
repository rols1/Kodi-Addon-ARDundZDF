# -*- coding: utf-8 -*-
################################################################################
#				Phoenix.py - Teil von Kodi-Addon-ARDundZDF
#				benötigt Modul yt.py (Youtube-Videos)
#		Videos der Phoenix_Mediathek auf https://www.phoenix.de/ 
################################################################################
#	Stand: 23.01.2020
#
#	30.12.2019 Kompatibilität Python2/Python3: Modul future, Modul kodi-six
#	

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

import json		
import os, sys
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke
import string

import ardundzdf					# -> get_query,test_downloads,get_zdf_search 
import resources.lib.util as util	# (util_imports.py)
PLog=util.PLog; home=util.home; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
getDirZipped=util.getDirZipped; Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
addDir=util.addDir; get_page=util.get_page; img_urlScheme=util.img_urlScheme; 
R=util.R; RLoad=util.RLoad; RSave=util.RSave; GetAttribute=util.GetAttribute; repl_dop=util.repl_dop; 
repl_char=util.repl_char; repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract; blockextract=util.blockextract; 
teilstring=util.teilstring; cleanhtml=util.cleanhtml; decode_url=util.decode_url; 
unescape=util.unescape; transl_doubleUTF8=util.transl_doubleUTF8; make_filenames=util.make_filenames; 
transl_umlaute=util.transl_umlaute; transl_json=util.transl_json; humanbytes=util.humanbytes; 
CalculateDuration=util.CalculateDuration; time_translate=util.time_translate; seconds_translate=util.seconds_translate; 
get_keyboard_input=util.get_keyboard_input; transl_wtag=util.transl_wtag; xml2srt=util.xml2srt; 
ReadFavourites=util.ReadFavourites; get_summary_pre=util.get_summary_pre; get_playlist_img=util.get_playlist_img; 
get_startsender=util.get_startsender; PlayVideo=util.PlayVideo; PlayAudio=util.PlayAudio; up_low=util.up_low; 


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
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_PHOENIX	= 'https://www.phoenix.de'
PLAYLIST 		= 'livesenderTV.xml'	  	# enth. Link für phoenix-Live											

# Icons
ICON 			= 'icon.png'				# ARD + ZDF
ICON_PHOENIX	= 'phoenix.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MEHR 		= "icon-mehr.png"
ICON_ZDF_SEARCH = 'zdf-suche.png'				
				
# Github-Icons zum Nachladen aus Platzgründen
ICON_DISKUSS	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/phoenix.png?raw=true'			
ICON_TVLIVE		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/tv-livestreams.png?raw=true'			
ICON_SEARCH		= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/icon-search.png?raw=true'			
ICON_SENDUNGEN	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Sendungen.png?raw=true'			
ICON_DOSSIERS	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Themen_Dossiers.png?raw=true'			
ICON_RUBRIKEN	= 'https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/Phoenix/Themen_Rubriken.png?raw=true'			

		
# ----------------------------------------------------------------------			
def Main_phoenix():
	PLog('Main_phoenix:')
	
	li = xbmcgui.ListItem()
	liICON_TVLIVE = home(li, ID=NAME)			# Home-Button

	title="Suche auf phoenix"
	tag = "Suche Themen, Sendungen und Videos in phoenix"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Search", fanart=R(ICON_PHOENIX), 
		thumb=ICON_SEARCH, fparams=fparams, tagline=tag)
	# ------------------------------------------------------
			
	title='Phoenix Livestream'
	title_epg,subtitle,vorspann,descr,href = get_live_data()
	if title_epg:
		title = 'Live: %s' % title_epg
	if subtitle:
		title = '%s | %s' % (title, subtitle)
	
	tag=''
	if vorspann and descr: 
		tag = "%s | %s\n\n%s" % (subtitle, vorspann, descr)
		if vorspann:
			tag = vorspann
		if descr:
			tag = "%s\n\n%s" % (tag, descr)
		
	title=py2_encode(title); href=py2_encode(href); tag=py2_encode(tag);
	PLog(title); PLog(subtitle); PLog(vorspann); PLog(descr); PLog(href)
	fparams="&fparams={'href': '%s', 'title': '%s', 'Plot': '%s'}" % (quote(href), quote(title), quote(tag))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Live", fanart=R(ICON_PHOENIX),
		thumb=ICON_TVLIVE, fparams=fparams, tagline=tag)
	# ------------------------------------------------------
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
def get_live_data():
	PLog('get_live_data:')
	path = "https://www.phoenix.de/response/template/livestream_json"
	page, msg = get_page(path=path)			
	if page == '':	
		msg1 = "get_live_data:"
		msg2 = msg
		# xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		PLog("%s | %s" % (msg1, msg2))	
	PLog(len(page))			
	
	title='';subtitle='';vorspann='';descr='';href=''
	if page:
		# Kurzf. möglich: {"title":"tagesschau","subtitel":"mit Geb\u00e4rdensprache",
		#	"typ":"","vorspann":""}
		if '":"' in page:					# möglich: '":"', '": "'
			page = page.replace('":"', '": "')
		PLog(page[:80])
		title 	= stringextract('"titel": "', '"', page)
		PLog(title);
		subtitle= stringextract('"subtitel": "', '"', page)
		vorspann= stringextract('"vorspann": "', '"', page)
		descr	= stringextract('"text":"', '"', page)
		title=transl_json(title)
		subtitle=transl_json(subtitle); vorspann=transl_json(vorspann);
		descr=cleanhtml(descr); descr=unescape(descr);
	
	playlist = RLoad(PLAYLIST)	# lokale XML-Datei (Pluginverz./Resources)
	liste = blockextract('<channel>', playlist)
	href=''
	for element in liste:
		name = stringextract('<name>', '</name>', element)
		if name == 'phoenix':
			href = stringextract('<link>', '</link>', element)
			break
	if 	href == '':		# Fallback
		href = 'https://zdfhls19-i.akamaihd.net/hls/live/744752/de/high/master.m3u8'			
	
	return title,subtitle,vorspann,descr,href
# ----------------------------------------------------------------------
# path via chrome-tools ermittelt. Ergebnisse im json-Format
#
def phoenix_Search(query='', nexturl=''):
	PLog("phoenix_Search:")
	if 	query == '':	
		query = ardundzdf.get_query(channel='phoenix')
	PLog(query)
	if  query == None or query == '':
		return ""
		
	query=py2_encode(query);
	if nexturl == '':
		path = 'https://www.phoenix.de/response/template/suche_select_json/term/%s/sort/online' % quote(query)
	else:
		path = nexturl
	PLog('Mark1')
	PLog(path)
	page, msg = get_page(path=path)	
	if page == '':						
		msg1 = 'Fehler in Suche: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
				
	if page.find('hits":0,') >= 0:
		msg1 = 'Leider kein Treffer.'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
		
	jsonObject = json.loads(page)
	search_cnt = jsonObject["content"]['hits']
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button

	items = jsonObject["content"]['items']
	PLog(len(items))
	li = GetContent(li, items)						
		
	nexturl = jsonObject["content"]["next"]					# letzte Seite: ""
	if nexturl:
		nexturl = BASE_PHOENIX + nexturl
		PLog("nexturl: " + nexturl)	
		img = R(ICON_MEHR)
		title = u"Weitere Beiträge"
		tag = u"Beiträge gezeigt: %s, gesamt: %s" % (len(items), search_cnt)

		nexturl=py2_encode(nexturl); query=py2_encode(query); 
		fparams="&fparams={'nexturl': '%s', 'query': '%s'}" %\
			(quote(nexturl), quote(query))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.phoenix_Search", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# GetContent: Auswertung der json-Datensätzen in items
#	base_img = Kopfbild
# turn_title: veranlasst Tausch Titel/Subtitel
def GetContent(li, items, base_img=None, turn_title=True ):
	PLog('GetContent:')

	mediatype=''	
	if SETTINGS.getSetting('pref_video_direct') == 'true': 
		mediatype='video'

	if not base_img:
		base_img = R(ICON_PHOENIX)		# Ergebnisseite ohne Bilder, Phoenix-Bild verwenden
	
	for item in items:
		# PLog(item)					# bei Bedarf
		vorspann=''; tag=''; summ=''; summ_par=''; subtitel=''; online=''
		single = False; video='false'
		try:
			img = item["bild_m"]
		except:
			img = ''
		if img == '':
			try:
				img = item["bild_l"]
			except:
				img = ''
		if img == '':
			img = base_img			
			
		if img == '' or 'placeholder' in img:
			img = base_img							# Fallback lokal
		else:
			if img.startswith('http') == False:
				img = BASE_PHOENIX + img
			
		# "inhalt_video":true muss nicht stimmen, Bsp.: 
		#	https://www.phoenix.de/response/template/suche_select_json/term/dialog/sort/score
		#if "inhalt_video" in item:
		#	video = item["inhalt_video"]	# false, true
		
		if "link" in item:					# Bsp. ../lindholz-am-05062018-a-262217.html, 
			url	= BASE_PHOENIX + item["link"] # 	augstein-und-blome-s-121540.html	
			PLog('url: ' + url)
			html_ref = "Link: .." + url.split('-')[-1]	# 121540.html	
		else:
			continue
		
		subtitel=''
		title 	= item["titel"]
		if "subtitel" in item:
			subtitel= item["subtitel"]
		if '"vorspann"' in item:
			vorspann= item["vorspann"]
		typ 	= item["typ"]				# Artikel, Doku, Ereignis..
		
		# Formate Sendezeit: "2017-02-26 21:45:00", "2018-01-27 00:30"
		if "online" in item:	
			datestamp= item["online"]			# Formate wie sendezeit 
			online = getOnline(datestamp)
		if online == '':						# vorh. bei Suche, nicht in response-Beiträgen
			if "sendung" in item:
				datestamp= item["sendung"]["sendezeit"]
				online = getOnline(datestamp)	
		if online == '':						# vorh. bei Suche, nicht in response-Beiträgen
			online = "Sendezeit fehlt"
			# trotz Sendezeit kann Video fehlen - Nachprüfung in SingleBeitrag
		else:
			if "inhalt_video" in item:			# trotz Sendezeit kann Video fehlen
				single = True
		PLog("typ: %s, %s" % (typ, online))
		PLog('single: ' + str(single))	
		
		# Link kann trotz VIDEO-Kennz. mehrere Beiträge enthalten - Nachprüfung in
		#	SingleBeitrag
		if single:							# Typ-Angabe (Artikel, Doku..) nicht bei Videos
			tag = "VIDEO | %s" % online
		else:
			tag = "%s | Folgeseiten | %s"	% (typ, html_ref)
			
		if SETTINGS.getSetting('pref_only_phoenix_videos') == 'true': 
			vinhalt = item["inhalt_video"] 			# false, wenn z.Z. kein phoenix-Video vorhanden 
			PLog('vinhalt: ' + str(vinhalt))
			if vinhalt == False:
				continue		
			if not single or 'Zukunft' in online:	# skip Beiträge ohne Videos, künftige Videos
				continue
				
		if turn_title and subtitel:
			t = title
			title = subtitel; subtitel = t
		
		if subtitel:		
			summ = subtitel	
		if vorspann:
			summ = "%s\n\n" % (summ, vorspann)
			summ_par = summ.replace('\n', '||')
			
		title = cleanhtml(title); title = repl_json_chars(title);

		PLog('Satz:')
		PLog(url); PLog(img); PLog(title); PLog(summ[:80]); PLog(tag)
		url=py2_encode(url); title=py2_encode(title); img=py2_encode(img); summ_par=py2_encode(summ_par);
		tag=py2_encode(tag);
		if single:
			fparams="&fparams={'title': '%s', 'path': '%s', 'html_url': '%s', 'tagline': '%s', 'summary': '%s', 'thumb': '%s'}" %\
				(quote(title), quote(url), quote(url), quote(tag), quote(summ_par), quote(img))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.SingleBeitrag", fanart=img, 
				thumb=img, fparams=fparams, summary=summ, tagline=tag)				
		else:
			fparams="&fparams={'path': '%s', 'html_url': '%s', 'title': '%s'}" %\
				(quote(url), quote(url), quote(title))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.BeitragsListe", fanart=img, 
				thumb=img, fparams=fparams, summary=summ, tagline=tag, mediatype=mediatype)

	return li

# ----------------------------------------------------------------------
# BeitragsListe: Liste der json-Datensätzen in url
#	Aufrufer: GetContent, SingleBeitrag (recursiv) 
#	bisher nicht benötigt
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
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
	
	
	jsonObject = json.loads(page)
	# search_cnt = jsonObject["content"]['hits']# fehlt hier	
	items = jsonObject["related"]['sendungen']
	PLog(len(items))
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
		
	li = GetContent(li, items, turn_title=True)	
	
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
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
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
		
		title = cleanhtml(title)
	
		PLog('Satz:')
		PLog(url); PLog(img); PLog(title)
		url=py2_encode(url); title=py2_encode(title);
		fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s'}" %\
			(quote(url), quote(title), ID)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.phoenix.ThemenListe", fanart=img, 
			thumb=img, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
def ThemenListe(title, ID, path):				# Liste zu einzelnem Untermenü
	PLog('ThemenListe: ' + title)
	PLog('ID: ' + ID)	
		
	sid 	= re.search(u'\-(\d+)\.html', path).group(1)	# Bsp. ../russland-r-252413.html
	url 	= 'https://www.phoenix.de/response/id/'	+ sid
	PLog('url: ' + url)

	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in ThemenListe: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return 
	PLog(len(page))
	
	jsonObject = json.loads(page)
	# search_cnt = jsonObject["content"]['hits']
	items = jsonObject["content"]['items']		
	PLog(len(items))						
	
	base_img = ICON_PHOENIX				# Fallback
	if 'bild_l' in jsonObject:
		base_img = BASE_PHOENIX + jsonObject["bild_l"]
	
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
		
	li = GetContent(li, items, base_img=base_img, turn_title=True)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# Ermittlung der Videoquellen ähnlich ZDF-Mediathek:
#	1. Die Url der Homepage der Sendung enthält am Ende die Sendungs-ID (../am-05062018-a-262217.html).
#
#	2. www.phoenix.de/response/id/xxx liefert die Youtube-ID + Infos zu relevanten Webseiten
#		der Umweg über die frühere Ladekette  (../beitrags_details.php, ../vod/ptmd/phoenix) ist
#		entfallen.
#
def SingleBeitrag(title, path, html_url, summary, tagline, thumb):	
	PLog('SingleBeitrag: ' + title);
	PLog(summary); PLog(tagline); 
	
	# ev. für sid split-Variante aus phoenix_Search verwenden
	sid 	= re.search(u'-(\d+)\.html', path).group(1)
	url 	= 'https://www.phoenix.de/response/id/'	+ sid
	PLog('url: ' + url)
	PLog('html_url: ' + html_url)	
	

	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in SingleBeitrag: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return 
	PLog(len(page))
		
	# Nachprüfung auf Mehrfachbeiträge - s. GetContent
	# 17.01.2020 abgeschaltet - wirkt bei fehlenden Videos
	#	wie Rekursion
	'''
	items=[]
	try:
		jsonObject = json.loads(page)
		# search_cnt = jsonObject["content"]['hits']# fehlt hier	
		items = jsonObject["related"]['sendungen']
		PLog(len(items))
	except Exception as exception:
		PLog(str(exception))
	if len(items) >= 1:
		if 'typ":"video-' not in page:
			PLog('Weiterleitung -> BeitragsListe')
			return BeitragsListe(path=url, html_url=html_url, title=title, skip_sid=True)
	'''	
		
	li = xbmcgui.ListItem()
	li = home(li, ID='phoenix')			# Home-Button
	
	items = blockextract('typ":"video-',  page)						# kann fehlen z.B. bei Phoenix_Suche 
	if len(items) == 0:
		if 'text":"<div><strong>' in page or 'text":"<p><strong>':	# Suchtexte
			t = u"Kein phoenix-Video zu >%s< gefunden.\nFundstellen beim Partnersender ZDF möglich.\nDort suchen?" % title
			dialog = xbmcgui.Dialog()
			ret = dialog.yesno('Weiterleitung?', t)
			PLog(ret)
			if ret:
				get_zdf_search(li,page,title)
		else:
			msg1 = 'Kein phoenix-Video zu >%s< gefunden.' % title
			msg2 = 'Ursache unbekannt'
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
		
	PLog(len(items))
	for item in items:
		# PLog(item)		# bei Bedarf
		typ 	= stringextract('typ":"', '"', item)		
		PLog("videotyp: " + typ)
		vid=''
		if typ == "video-youtube":
			vid		= stringextract('id":"', '"', item)
			PLog('youtube vid:' + vid)
			if vid:
				# Import beim Pluginstart stellt nicht alle Funktionen zur Verfügung			
				import resources.lib.yt	as yt		# Rahmen für pytube
				li =  yt.yt(li=li, url=url, vid=vid, title=title, tag=tagline, summ=summary, thumb=thumb)
			else:
				PLog('SingleBeitrag: vid nicht gefunden')	
		if typ == "video-smubl":
			content_id = stringextract('basename": ', ',', item)		# Bsp. "basename": 253381, "bild_l":
			PLog(content_id); PLog(title); PLog(tagline); PLog(thumb); 
			vid=content_id; 
			li = get_formitaeten(li,content_id,title,tagline,thumb)
			if li == '':
				msg1 = '%s | Problem beim Laden der Videodaten' % title
				PLog(msg)
								
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# Quersuche beim ZDF - Aufrufer SingleBeitrag
# Dokus: Suche mit Title und Subtitel (Achtung: gedreht in GetContent
#	für Download + Merkliste)
# phoenix history: Suchbuttons erstellen mit Titeln aus 1. Satz der Beschreibung
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
	stitle_org = stringextract('subtitel": "', '"', page)	# hier mit Blank
	tag = "Suche phoenix-Beitrag auf Partnersender ZDF"
	
	if "phoenix history" not in title: 					# Dokus mit Titel + Subtitel suchen 
		query = stitle_org
		title = "1. ZDFSuche (Titel): %s" % query	
		tag = tag + " | Suche mit Titel des Beitrags"	
		summ = stringextract('text":"', '"}', page)
		summ = summ.replace('\\r\\n', ' ')
		summ = cleanhtml(summ); summ = unescape(summ);
		summ = repl_json_chars(summ) 
		PLog("Satz:"); PLog(title); PLog(stitle_org);PLog(query); PLog(summ[:80]); 
		query=py2_encode(query); title=py2_encode(title);
		# return ardundzdf.ZDF_Search(query=query, title=title)	# Altern.: Direktsprung nur mit Subtitel
		query=py2_encode(query); title=py2_encode(title); 	# Suche mit Titel
		fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
			thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)
		
		query = title_org
		title = "2. ZDFSuche (Subtitel): %s" % query	 	# Suche mit Subtitel
		tag = tag.replace('Titel', 'Subtitel')	
		query=py2_encode(query); title=py2_encode(title);
		fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
		addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
			thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)

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
			PLog("Satz:"); PLog(title); PLog(stitle);PLog(query); PLog(summ[:80]); 
			
			query=py2_encode(query); title=py2_encode(title);
			fparams="&fparams={'query': '%s', 'title': '%s'}" % (quote_plus(query), quote_plus(title))
			addDir(li=li, label=title, action="dirList", dirID="ZDF_Search", fanart=R(ICON_ZDF_SEARCH), 
				thumb=R(ICON_ZDF_SEARCH), tagline=tag, summary=summ, fparams=fparams)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
# ----------------------------------------------------------------------
# beitrags_details 	-> xml-format
# ngplayer_2_3		-> json-Format
def get_formitaeten(li,content_id,title,tagline,thumb):
	PLog('get_formitaeten')
	PLog('content_id: ' + content_id)
	if content_id == '':							# sollte nicht vorkommen
		msg = '%s | content_id fehlt' % title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
	
	url = 'https://www.phoenix.de/php/mediaplayer/data/beitrags_details.php?ak=web&ptmd=true&id=' + content_id
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in get_formitaeten: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
	
	basename = stringextract('<basename>', '</basename>', page)#	 Bsp. <basename>180605_phx_runde</basename>
	#if basename == '':
	#	continue
	url = 'https://tmd.phoenix.de/tmd/2/ngplayer_2_3/vod/ptmd/phoenix/' + basename
	page, msg = get_page(path=url)	
	if page == '':						
		msg1 = 'Fehler in get_formitaeten: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
	
	formitaeten = blockextract('"formitaeten"',  page)		# Video-URL's ermitteln - wie ZDF-Mediathek
	# PLog(formitaeten)
	geoblock =  stringextract('geoLocation',  '}', page) 
	geoblock =  stringextract('"value": "',  '"', geoblock).strip()
	PLog('geoblock: ' + geoblock)						# i.d.R. "none", sonst "de"
	if geoblock == 'de':			# Info-Anhang für summary 
		geoblock = ' | Geoblock!'
	else:
		geoblock = ''		
			
	download_list = []		# 2-teilige Liste für Download: 'Titel # url'
	title_call = title
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
			url = url.replace('https', 'http')			# im Plugin kein Zugang mit https!
			quality = stringextract('"quality" : "',  '"', audiorec)
			if quality == 'high':						# high bisher identisch mit auto 
				continue
 
			PLog(url); PLog(quality); PLog(tagline); 
			if url:
				if url.endswith('master.m3u8'):
					if SETTINGS.getSetting('pref_video_direct') == 'true': # or Merk == 'true':	# Sofortstart
						PLog('Sofortstart: phoenix get_formitaeten')
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
			
	return li
	
####################################################################################################
# Phoenix - TV-Livestream mit EPG
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
	
	li =  ardundzdf.Parseplaylist(li, href, img, geoblock='', descr=Plot)	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
					
	return oc

# ----------------------------------------------------------------------
def get_epg_ARD(epg_url, listname):					# EPG-Daten ermitteln für SenderLiveListe, ARD
	PLog('get_epg_ARD: ' + listname)
	epg_date = ''; epg_title=''; epg_text=''

	page = HTTP.Request(epg_url, cacheTime=1, timeout=float(3)).content # ohne xpath, Cache max. 3 sec
	# PLog(page)		# nur bei Bedarf		
	liste = blockextract('class=\"sendungslink\"', '', page)  
	PLog(len(liste));	# bei Bedarf
	if len(liste) == 0: # Sicherung
		return 'weiter zum Live-Stream','Keine EPG-Daten gefunden','Keine EPG-Daten gefunden'
	
	now = datetime.datetime.now()		# akt. Zeit
	nowtime = now.strftime("%H:%M")		# ARD: <span class="date"> \r 00:15 \r <div class="icons">
	
	for i in range (len(liste)):		# ältere Sendungen enthalten - daher Schleife + Zeitabgleich	
		starttime = stringextract('<span class=\"date\">', '<', liste[i]) # aktuelle Sendezeit
		starttime = mystrip(starttime)
		try:
			endtime = stringextract('<span class=\"date\">', '<', liste[i+1])		# nächste Sendezeit		
			endtime = mystrip(endtime)
		except:
			endtime = '23:59'			# Listenende

		#PLog('starttime ' + starttime); PLog('endtime ' + endtime); PLog('nowtime ' + nowtime);	# bei Bedarf
		epg_date = ''
		if nowtime >= starttime and nowtime < endtime:
			epg_date = stringextract('<span class=\"date\">', '<', liste[i])
			epg_date = mystrip(epg_date) + ' - ' + endtime
			
			epg_title = stringextract('<span class=\"titel\">', '<',  liste[i])
			epg_title = mystrip(epg_title)
			epg_title = unescape(epg_title)			
					
			epg_text = stringextract('<span class=\"subtitel\">', '<',  liste[i])
			epg_text = mystrip(epg_text)
			epg_text = unescape(epg_text)
			
			# weitere Details via eventid z.Z. nicht verfügbar - beim Abruf klemmt Plex ohne Fehlermeldung:
			#eventid = stringextract('data-eventid=\"', '\"', liste[i])	# Bsp. 	2872518888223822
			#details_url = "http://programm.ard.de/?sendung=" + eventid
			#page = HTTP.Request(details_url, cacheTime=1, timeout=float(10)).content # ohne xpath, Cache max. 1 sec
			#epg_details = stringextract('name=\"description\" content="', '\" />', page)
			#epg_text = unescape(epg_text[0:80])
			
			break
	
	if epg_date == '':					# Sicherung
		return '','','Problem mit EPG-Daten'	
			
	epg_text = epg_text.decode(encoding="utf-8", errors="ignore") # möglich: UnicodeDecodeError: 'utf8' codec can't decode byte 0xc3 ...
	PLog(epg_date); PLog(epg_title); PLog(epg_text[0:80]); 	
	return epg_date, epg_title, epg_text

# ----------------------------------------------------------------------
# getOnline: 1. Ausstrahlung
# Format datestamp: "2017-02-26 21:45:00", 2018-05-24T16:50:00 19-stel.
#	beim Menü Sendungen auch  2018-01-20 00:30 16 stel.
# time_state checkt auf akt. Status, Zukunft und jetzt werden rot gekennzeichnet
def getOnline(datestamp):
	PLog("getSendezeit: " + datestamp)
	PLog(len(datestamp))
	if datestamp == '' or '/' in datestamp:
		return '' 

	online = ''
	if len(datestamp) == 19 or len(datestamp) == 16:
		senddate = datestamp[:10]
		year,month,day = senddate.split('-')
		sendtime = datestamp[11:]
		if len(sendtime) == 5:							# auffüllen: 17:00 -> 17:00:00
			sendtime = "%s:00" % sendtime
		
		checkstamp = "%s %s" % (senddate, sendtime)
		check_state= time_state(checkstamp)
		if check_state:									# Kennz. nur Zukunft und jetzt
			check_state = " (%s)" % check_state
		
		online = "Online%s: %s.%s.%s, %s Uhr"	% (check_state, day, month, year, sendtime)	
	return online
	
# ----------------------------------------------------------------------
# Prüft datestamp auf Vergangenheit, Gegenwart, Zukunft
#	Format datestamp: "2020-01-26 11:15:00" 19 stel.
def time_state(checkstamp):
	PLog("time_state: " + checkstamp)		
	date_format = "%Y-%m-%d %H:%M:%S"

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











