# -*- coding: utf-8 -*-
################################################################################
#				funk.py - Teil von Kodi-Addon-ARDundZDF
#				Kanäle und Serien von https://www.funk.net/
################################################################################
# 	Credits: cemrich (github) für die wichtigsten api-Calls
#	Stand: 15.12.2019
#
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
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

import  json		
import os, sys
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke

# import ardundzdf					# -> ZDF_get_content - nicht genutzt
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
get_startsender=util.get_startsender; PlayVideo=util.PlayVideo; PlayAudio=util.PlayAudio; 



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

ICON 			= 'icon.png'		# ARD + ZDF
ICON_FUNK		= 'funk.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_SPEAKER 	= "icon-speaker.png"
ICON_SEARCH 	= 'ard-suche.png'						
ICON_MEHR 		= "icon-mehr.png"
NAME			= 'ARD und ZDF'
MNAME			= "FUNK"

FUNKCacheTime = 300
MAXLINES = 50

def Main_funk():
	PLog('Main_funk:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
	
	title = "Suche VIDEOS"
	fparams="&fparams={'title': '%s' }" % title
	tag = "Suche Videos"
	summ= "gesucht wird in Titel und Beschreibung"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Search", fanart=R(ICON_FUNK), 
		thumb=R(ICON_SEARCH), tagline=tag, summary=summ, fparams=fparams)
		
	title = "Suche KANÄLE und SERIEN"
	fparams="&fparams={'title': '%s' }" % title
	tag = "Suche [COLOR red]KANÄLE[/COLOR], [COLOR green]WEITERERE KANÄLE[/COLOR] und [COLOR darkgoldenrod]SERIEN[/COLOR]"
	summ= "gesucht wird in Titel und Beschreibung"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Search", fanart=R(ICON_FUNK), 
		thumb=R(ICON_SEARCH), tagline=tag, summary=summ, fparams=fparams)
		
	title = "Suche PLAYLISTS"	
	fparams="&fparams={'title': '%s' }" % title
	tag = "Suche [COLOR blue]PLAYLISTS[/COLOR]"
	summ= "gesucht wird in Titel und Beschreibung"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Search", fanart=R(ICON_FUNK), 
		thumb=R(ICON_SEARCH), tagline=tag, summary=summ, fparams=fparams)
	#---------------------------------------------
	
	fparams="&fparams={'title': '%s'}" % "KANÄLE"
	addDir(li=li, label= "KANÄLE", action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)
		
	fparams="&fparams={'title': '%s'}" % "SERIEN"
	addDir(li=li, label= "SERIEN", action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'title': '%s'}" % "PLAYLISTS"
	addDir(li=li, label= "PLAYLISTS", action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'title': '%s'}" % "WEITERE KANÄLE"
	addDir(li=li, label= "WEITERE KANÄLE", action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	fparams="&fparams={'title': '%s', 'typ': '', 'entityId': ''}"  % "NEUESTE VIDEOS"
	addDir(li=li, label= "NEUESTE VIDEOS", action="dirList", dirID="resources.lib.funk.ChannelSingle", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE)
		
# ----------------------------------------------------------------------			
# Channelformat: Playlists, KANÄLEN und SERIE
# Videosuche: static/search?=%s
#
def Search(title):
	PLog('Search:')
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)			# Home-Button	

	query = get_keyboard_input() 
	if query == None or query.strip() == '': # None bei Abbruch
		return	
	query = query.strip();
	query_org = query
	query = query.lower()

	if 'PLAY' in title:	
		path = "https://www.funk.net/api/v4.0/playlists/"		# Playlists
	if 'SERIEN' in title:										# KANÄLEN und SERIEN
		path = "https://www.funk.net/data/static/channels"		# Gesamtliste mit Kurzbeschreibungen
	if 'VIDEOS' in title:										# VIDEOS
		path = "https://www.funk.net/data/search?q=%s"  % quote(py2_encode(query_org))
		
	page = loadPage(path)
	if page.startswith('Fehler'):
		msg1 = 'Verbindungsproblem'
		msg2 = page
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	jsonObject = json.loads(page)
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	i=0	# Zähler Listitems
	is_channel = True
	if("list" in jsonObject):											# Gesamtliste
		listObject = jsonObject["list"]
	if ("_embedded" in jsonObject):										# Playlist
		listObject = jsonObject["_embedded"]["playlistDTOList"]
	if("videos" in jsonObject):											# Videos
		is_channel = False
		listObject = jsonObject["videos"]["list"]
		for stageObject in listObject:
			title,alias,descr,img,date,dur,cr,entityId = extract_videos(stageObject['value'])
			date = time_translate(date)
			dur = seconds_translate(dur)
			tag = "%s | %s" % (date, dur)
			if alias:			# hier channelAlias
				tag = '%s | %s' % (alias,tag)
			if cr:
				tag = "%s | Copyright: %s" % (tag, cr)
			# Probleme mit zahlreichen /r/n
			descr_par = descr.replace('\n', '||'); descr_par = descr_par.replace('\r', '')  # \r\n\r\n
			descr_par = repl_json_chars(descr_par); 
			title = repl_json_chars(title)
			title = unescape(title)
			
			PLog(title); PLog(entityId); 
			title=py2_encode(title); img=py2_encode(img); descr_par=py2_encode(descr_par);
			fparams="&fparams={'title': '%s', 'img': '%s', 'descr': '%s', 'entityId': '%s'}"  %\
				(quote(title), quote(img), quote(descr_par), entityId)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ShowVideo", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)					
			i=i+1
		PLog('Search videos: ' + str(i))
	
	if is_channel:
		for stageObject in listObject:
			typ,title,alias,descr,img,date,entityGroup,entityId = extract_channels(stageObject) 
			if typ =='':					# Sicherung
				continue
			if title == 'Neueste Videos':	# skip - funktioniert nicht in ChannelSingle, 
				continue					#	eigenes Menü in Main_funk
			PLog(type(query)); PLog(type(title)); PLog(type(descr));
			if query in title.lower() or  query in descr.lower():
				title = repl_json_chars(title)
				title = unescape(title)
				tag=''											# typ farbig markieren
				isPlaylist=''
				if typ == "format":			# KANÄLE
					tag = u"[COLOR red]KANAL[/COLOR]" 
				if typ == "series":			# SERIEN
					tag = u"[COLOR darkgoldenrod]SERIE[/COLOR]"
				if typ == "archiveformat":	# WEITERE KANÄLE
					tag = u"[COLOR green]WEITERER KANAL[/COLOR]" 
				if typ == "default":		# PLAYLISTS	-> Channel 
					isPlaylist = 'True'
					next_path = "https://www.funk.net/api/v4.0/playlists/%s" % entityId
					tag = u"[COLOR darkgoldenrod]PLAYLIST[/COLOR]"
					
					title=py2_encode(title); next_path=py2_encode(next_path);
					fparams="&fparams={'title': '%s','next_path': '%s'}" % (quote(title), quote(next_path))
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Channels", 
						fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
					
				else:
					title=py2_encode(title); 
					fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s', 'isPlaylist': '%s'}"  %\
						(quote(title), typ, entityId, isPlaylist)
					addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
						fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
				i=i+1
		PLog('Search channels: ' + str(i))
			
	if i == 0:
		msg1 = 'Suche nach <%s>:' % query_org
		msg2 = 'leider nichts gefunden'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------			
#
def Channels(title, next_path=''):
	PLog('Channels:')
	PLog(next_path)

	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)			# Home-Button	

	if next_path =='':	
		next_path = "https://www.funk.net/data/static/channels"		# Gesamtliste mit Kurzbeschreibungen
		if title_org.startswith("PLAY"):							# Playlists nicht in Gesamtliste
			next_path = "https://www.funk.net/api/v4.0/playlists/?size=%s" % MAXLINES
	page = loadPage(next_path)
	if page.startswith('Fehler'):
		msg1 = 'Verbindungsproblem'
		msg2 = page
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	jsonObject = json.loads(page)

	
	if("list" in jsonObject):											# Gesamtliste
		listObject = jsonObject["list"]
	if ("_embedded" in jsonObject):										# Playlists
		listObject = jsonObject["_embedded"]["playlistDTOList"]
	
	try:
		# todo: Direktaufruf (noch 2 Klicks erforderlich) Bsp. Trend
		if jsonObject['type'] == "default":								# einz. Playlist direkt
			listObject = [0]
			listObject[0] = jsonObject
	except Exception as exception:
		PLog(str(exception))
				
		
	for stageObject in listObject:
		typ,title,alias,descr,img,date,entityGroup,entityId = extract_channels(stageObject) 
		if typ =='':		# Sicherung
			continue
		if title == 'Neueste Videos':	# skip - funktioniert nicht in ChannelSingle, 
			continue					#	eigenes Menü in Main_funk
			
		date = time_translate(date)
		tag = date
		if alias:			# zusätzl.  Kennung (byChannelAlias, byChannelId)
			tag = '%s | %s' % (alias, date)

		if title_org.startswith("KAN") and typ == "format":			# KANÄLE
			title=py2_encode(title); 
			fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s'}"  %\
				(quote(title), typ, entityId)
			tag = "[COLOR red]KANAL[/COLOR] %s" % tag
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
		if title_org.startswith("SER") and typ == "series":			# SERIEN
			title=py2_encode(title); 
			fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s'}"  %\
				(quote(title), typ, entityId)
			tag = "[COLOR darkgoldenrod]SERIE[/COLOR] %s" % tag
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
				
		if  typ == "default":							# PLAYLISTS
			title=py2_encode(title); 
			fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s', 'isPlaylist': '%s'}"  %\
				(quote(title), typ, entityId, 'True')
			tag = "[COLOR blue]PLAYLIST[/COLOR] %s" % tag
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
		if title_org.startswith("WEI") and typ == "archiveformat":	# WEITERE KANÄLE
			title=py2_encode(title); 
			fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s'}"  %\
				(quote(title), typ, entityId)
			tag = "[COLOR green]WEITERER KANAL[/COLOR] %s" % tag
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)
							
		
	pN,pageSize,totalPages,totalElements,next_path = get_pagination(jsonObject)	# Mehr?		
	if next_path:	
		summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (totalPages, totalElements)
		pN = int(pN)								# nächste pageNumber, Basis 0
		tag = "weiter zu Seite %s" % str(pN)
		title_org=py2_encode(title_org); next_path=py2_encode(next_path); 
		fparams="&fparams={'title': '%s','next_path': '%s'}" % (quote(title_org), quote(next_path))
		addDir(li=li, label=title_org, action="dirList", dirID="resources.lib.funk.Channels", 
			fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# zeigt alle Videos eines Channels, einr Playlist
#	Alternative: byChannelAlias
def ChannelSingle(title, typ, entityId, next_path='', isPlaylist=''):
	PLog('ChannelSingle: ' + title)
	PLog(entityId); PLog(typ); 
	title_org=title; entityId_org=entityId
	
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)				# Home-Button
		
	if next_path =='':	
		if title == "NEUESTE VIDEOS":						# Aufruf: Hauptmenü 
			next_path = "https://www.funk.net/data/static/latestVideos"
		else:												#  Aufruf: Channels
			next_path = "https://www.funk.net/api/v4.0/videos/byChannelId/%s?size=%s" % (entityId, MAXLINES)
		if isPlaylist == 'True':
			next_path = "https://www.funk.net/api/v4.0/videos/byPlaylistId/%s?size=%s" % (entityId, MAXLINES)		
	page = loadPage(next_path)
	if page.startswith('Fehler'):
		msg1 = 'Verbindungsproblem'
		msg2 = page
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	jsonObject = json.loads(page)
	
	#Dict('store',store_id , jsonObject)
	# Debug:
	# RSave("/tmp/x_%s.json" % store_id, json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))

	if("list" in jsonObject):								# Gesamtliste, latestVideos
		videoObject = jsonObject["list"]
	if("_embedded" in jsonObject):							# Standard-Videoliste
		videoObject = jsonObject["_embedded"]["videoDTOList"]
	PLog('channel %s' % title) 
	
	mediatype=''
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'

	for stageObject in videoObject:
		title,alias,descr,img,date,dur,cr,entityId = extract_videos(stageObject) 
		date = time_translate(date)
		dur = seconds_translate(dur)
		tag = "%s | %s" % (date, dur)
		if alias:			# hier channelAlias
			tag = '%s | %s' % (alias,tag)
		if cr:
			tag = "%s | Copyright: %s" % (tag, cr)
		# Probleme mit zahlreichen /r/n
		descr_par = descr.replace('\n', '||'); descr_par = descr_par.replace('\r', '')  # \r\n\r\n
		descr_par = repl_json_chars(descr_par); 
		title = repl_json_chars(title)
		title = unescape(title)

		PLog(title); PLog(entityId); 
		title=py2_encode(title); img=py2_encode(img); descr_par=py2_encode(descr_par);
		fparams="&fparams={'title': '%s', 'img': '%s', 'descr': '%s', 'entityId': '%s'}"  %\
			(quote(title), quote(img), quote(descr_par), entityId)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ShowVideo", 				
			fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams, mediatype=mediatype)					
	
	pN,pageSize,totalPages,totalElements,next_path = get_pagination(jsonObject)	# Mehr?		
	if next_path:	
		summ = u"insgesamt: %s Seite(n) , %s Beiträge" % (totalPages, totalElements)
		pN = int(pN)								# nächste pageNumber, Basis 0
		tag = "weiter zu Seite %s" % str(pN)
		title_org=py2_encode(title_org); typ=py2_encode(typ); 
		entityId_org=py2_encode(entityId_org); next_path=py2_encode(next_path);
		fparams="&fparams={'title': '%s', 'typ': '%s', 'entityId': '%s','next_path': '%s'}" %\
			(quote(title_org), quote(typ), quote(entityId_org), quote(next_path))
		addDir(li=li, label=title_org, action="dirList", dirID="resources.lib.funk.ChannelSingle", 
			fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# Rückgabe: pN, pageSize, totalPages, totalElements, href_next
def get_pagination(jsonObject):
	PLog("get_pagination:")

	pageNumber=''; pageSize=''; totalPages=''; totalElements=''; pN=''
	if "page" in jsonObject:
		pageObject = jsonObject["page"]
		
		pageNumber	= pageObject["number"]
		pageSize	= pageObject["size"]
		if pageObject["totalPages"]:
			totalPages	= pageObject["totalPages"]
		totalElements	= pageObject["totalElements"]
	
	next_path=''		
	if "_links" in jsonObject:
		linksObject 	= jsonObject["_links"]
		try:
			next_path		= linksObject["next"]["href"]
		except:
			pass	
					
	next_path = next_path.replace('.net/v4.0/', '.net/api/v4.0/') # falls api fehlt
	PLog('next_path: %s' % next_path)
	PLog('pageNumber: %s, pageSize: %s, totalPages:%s, totalElements: %s ' % (pageNumber, pageSize, totalPages, totalElements))
	if next_path == '':							# reicht 
		return "", "", "", "", ""
	
	if pageNumber != '':		
		pN = int(pageNumber) + 2				# nächste pageNumber (Basis 0)
		
	return str(pN), pageSize, totalPages, totalElements, next_path
# ----------------------------------------------------------------------			
#	Inhalte der Channel-Liste
#	Rückgabe: typ,title,alias,descr,img,date,entityGroup,entityId = Get_content(stageObject) 
def extract_channels(stageObject):
	PLog('extract_channels:')
	base = "https://www.funk.net/api/v4.0/thumbnails/"
	# PLog(str(stageObject))

	title=stageObject["title"]						# konstante Details 
	alias=stageObject["alias"]
	entityId = stageObject["entityId"]
			
	descr=''										# variable Details 
	if("description" in stageObject):
		descr = stageObject["description"]
	else:
		if("shortDescription" in stageObject):
			descr = stageObject["shortDescription"]
			
	typ=''	
	if("type" in stageObject):
		typ = stageObject["type"]
		
	# ohne "Url" im key nur 5d8b99a78e80cc0001d70f9f (Bsp)
	img="";	# weitere: imageUrlLandscape, imageUrlOrigin
			#	imageUrlSquare 
	if("imageUrlSquare" in stageObject):
		img = stageObject["imageUrlSquare"]
	if img == '':
		if "imageUrlLandscape" in stageObject:
			img = stageObject["imageUrlLandscape"]
	if img == '':
		if "imageUrlPortrait" in stageObject:
			img = stageObject["imageUrlPortrait"]
	if img == '':
		if "imageSquare" in stageObject:  # ohne Url
			img = stageObject["imageSquare"]
		if img == '':
			if "imageLandscape" in stageObject:
				img = stageObject["imageLandscape"]
		if img:
			img = base + img
	if img == '' or img == None:		# Falback
		img = R(ICON_DIR_FOLDER) 

	date=''	
	if("publicationDate" in stageObject):
		date = stageObject["publicationDate"]
	else:
		if("updateDate" in stageObject):
			date = stageObject["updateDate"]
	
	entityGroup='';
	if("entityGroup" in stageObject):
		entityGroup = stageObject["entityGroup"]
		
	entityGroup=str(entityGroup); entityId=str(entityId); 
	
	date=date; typ=typ; img=img; 

	title=repl_json_chars(title) 		# json-komp. für func_pars in router()
	alias=repl_json_chars(alias) 		# dto
	descr=repl_json_chars(descr) 		# dto
	
	PLog('extract_channels: %s | %s |%s | %s | %s | %s | %s | %s' % (typ, title,alias,descr[:60],img,date,entityGroup,entityId) )		
	return typ,title,alias,descr,img,date,entityGroup,entityId
# ----------------------------------------------------------------------	
#	Videos eines Channels
#	Rückgabe: title,alias,descr,img,date,dur,cr,genre,entityId = Get_content(stageObject) 
def extract_videos(stageObject):
	PLog('extract_videos:')
	base = "https://www.funk.net/api/v4.0/thumbnails/"
	# PLog(stageObject)
											# konstante Details 
	title=stageObject["title"]
	PLog(title)
	alias=stageObject["channelAlias"]		# statt alias (ähnlich title)

	entityId = stageObject["entityId"]		# int
	channelId = stageObject["channelId"]	# int
	dur = stageObject["duration"]			# int
						
											# variable Details 
	img=''; date=''; entityGroup=''; cr=''; genre=''; descr='';
	myhash='';
	if "hash" in stageObject:		
		myhash = stageObject["hash"]	
	if("description" in stageObject):
		descr = stageObject["description"]
	if descr == '':	
		if "shortDescription" in stageObject:
			descr = stageObject["shortDescription"]	
		
	if("copyright" in stageObject):
		cr = stageObject["copyright"]
	if("genre" in stageObject):
		genre = stageObject["genre"]
	if("secondGenre" in stageObject):
		genre = "%s | %s" % (genre, stageObject["secondGenre"])
		
		# weitere: imageUrlLandscape, imageUrlOrigin
			#	imageUrlSquare
	if("imageUrlSquare" in stageObject):
		img = stageObject["imageUrlSquare"]
	if img == '':
		if "imageUrlLandscape" in stageObject:
			img = stageObject["imageUrlLandscape"]
	if img == '':
		if "imageUrlPortrait" in stageObject:
			img = stageObject["imageUrlPortrait"]
	if img == '':
		if "imageSquare" in stageObject:  # ohne Url
			img = stageObject["imageSquare"]
		if img == '':
			if "imageLandscape" in stageObject:
				img = stageObject["imageLandscape"]
		if img:
			img = base + img
	if img == '':		# Falback
		img = R(ICON_DIR_FOLDER) 
		
	if("publicationDate" in stageObject):
		date = stageObject["publicationDate"]
	else:
		if("updateDate" in stageObject):
			date = stageObject["updateDate"]
	
	if("entityGroup" in stageObject):
		entityGroup = stageObject["entityGroup"]
		
	dur=str(dur); entityId=str(entityId); channelId=str(channelId); 
	entityGroup=str(entityGroup); entityId=str(entityId); 
	
	title=repl_json_chars(title) 		# json-komp. für func_pars in router()
	alias=repl_json_chars(alias) 		# dto
	descr=repl_json_chars(descr) 		# dto
	
	PLog('extract_videos: %s | %s |%s | %s | %s | %s | %s | %s |%s' % (title,alias,descr[:60],img,date,dur,cr,genre,entityId) )		
	return title,alias,descr,img,date,dur,cr,entityId

# ----------------------------------------------------------------------
# lädt Video-Objekt von Funk, Session- und Metadaten von nexx.cloud
#	und baut 1 Stream-Url und die verfügbaren MP4-Url's.
#	Bei Einstellung Sofortstart wird PlayVideo direkt aufgerufen,
#	sonst werden die Buttons für Stream- und MP$-Url's gelistet. 	
# Problem geschützte Videos: die Streamurl's funktionierten am
#		20.10.2019 einige Stunden, dann nicht mehr (Player-Error:
#		missing root node - Abhilfe bisher nicht möglich - aus-
#		kommentiert.
# Sofortstart: i.Z.m. den geschützte Videos und auch häufigem 
#	"Stottern" bei ungeschützten Streams wird im Modul das größte
#		MP4-Video verwendet (Vorgabe in Settings)
#
def ShowVideo(title, img, descr, entityId, Merk='false'):
	PLog('ShowVideo:'); PLog(title); PLog(entityId)
	
	path = "https://www.funk.net/api/v4.0/videos/%s" % entityId
	page = loadPage(path)
	if page.startswith('Fehler'):
		msg1 = 'Verbindungsproblem'
		msg2 = page
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
	jsonObject = json.loads(page)
	
	store_id = 'video_%s' % entityId
	# Dict('store',store_id , jsonObject) 
	# Debug:
	# RSave("/tmp/x_%s.json" % store_id, json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))
	# jsonObject = Dict('load',store_id)
		
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)							# Home-Button
			
														# 1. Session-Objekt
	path = "https://api.nexx.cloud/v3/741/session/init" # init-Session
	data = 'nxp_devh=4"%"3A1500496747"%"3A178989'		# Post request
	page = loadPage(path, data=data)
	PLog(page[:80]) 
	if page.startswith('Fehler'):
		msg1 = 'Verbindungsproblem'
		msg2 = page
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		xbmcplugin.endOfDirectory(HANDLE)
		
	jsonObject = json.loads(page)
	x_cid 	= jsonObject["result"]["general"]["cid"]
	geo 	= jsonObject["result"]["general"]["geocode"]
	# x-request-token nicht im jsonObject
	PLog("cid: " + x_cid); PLog("geo: " + geo); 
	geoblock=''
	if geo:
		geoblock =  " | Geoblock: %s"	% geo
														# 2. Video-Metadaten
	x_cid	= "x-request-cid,%s" % x_cid							# x-request-cid
	x_token = "x-request-token,f058a27469d8b709c3b9db648cae47c2"	# x-request-token
	data = 'addStatusDetails=1&addStreamDetails=1&addFeatures=1&addCaptions=1&addBumpers=1&captionFormat=data'
	path = "https://api.nexx.cloud/v3/741/videos/byid/%s" % entityId
	page = loadPage(path, x_cid=x_cid, x_token=x_token, data=data)
	PLog(page[:80]) 
	jsonObject = json.loads(page)
	# RSave("/tmp/x_videometa_protec.json", json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))
	
	protected=False; tokenHLS=''; tokenDASH=''			# 3. Stream-Url 
	server = jsonObject["result"]["streamdata"]["cdnShieldProgHTTPS"]
	if server == '':	# i.d.R. funk-01dd.akamaized.net
		# 				# protected: nx-t09.akamaized.net	
		# token-Lösung von realvito (kodinerds, s. Post vom 20.10.2019)		
		server = jsonObject["result"]["streamdata"]["cdnShieldHTTPS"]	# endet mit /
		tokenHLS = jsonObject["result"]["protectiondata"]["tokenHLS"]
		tokenDASH= jsonObject["result"]["protectiondata"]["tokenDASH"]
		protected = True
		
	PLog("server: "+ server)
	PLog("tokenHLS: "+ tokenHLS); PLog("tokenDASH: "+ tokenDASH);
	locator	 = jsonObject["result"]["streamdata"]["azureLocator"]	
	distrib  = jsonObject["result"]["streamdata"]["azureFileDistribution"]
	
	if protected:
		stream_url = "https://%s%s/%s_src.ism/Manifest(format=mpd-time-cmaf)?hdnts=%s"	% (server,locator,entityId, tokenHLS)
		# Header Referer von  Kodi nicht verwendet/erkannt - weiterhin Player-Error (s.o.)
		#h1='cors'
		#h2='https://www.funk.net/channel/doctor-who-1164/boeser-wolf-133317/doctor-who-staffel-1-1290'
		#stream_url = "%s|Sec-Fetch-Mode=%s&Referer=%s" % (stream_url, urllib2.quote(h1), urllib2.quote(h2))
	else:
		stream_url = "https://%s%s/%s_src.ism/Manifest(format=mpd-time-cmaf)"	% (server,locator,entityId)
	PLog("stream_url: "+ stream_url)
															# Video-Details
	title 	= jsonObject["result"]["general"]["title"]
	stitle 	= jsonObject["result"]["general"]["subtitle"]
	dur		= jsonObject["result"]["general"]["runtime"]

	width		= jsonObject["result"]["features"]["width"] # Details für stream_url
	height		= jsonObject["result"]["features"]["height"]
	fps			= jsonObject["result"]["features"]["fps"]
	aspect		= jsonObject["result"]["features"]["aspectRatio"]
	orientation	= jsonObject["result"]["features"]["orientation"]
	
	forms = get_forms(distrib)								# Details für mp4_url's 
	mp4_urls = []
	for form in forms:
		# leerer hdnts-Zusatz bei nicht geschützten Videos stört nicht.
 		# https://funk-01.akamaized.net/59536be8-46cc-4d1e-83b7-d7bab4b3eb5d/1633982_src_1920x1080_6000.mp4
		mp4_urls.append("https://%s%s/%s_src_%s.mp4?hdnts=%s"	% (server,locator,entityId,form,tokenDASH))
	PLog("mp4_urls: "+ str(mp4_urls))	
	
	title = repl_json_chars(title)
	title_org = title
	
	if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart MP4 (s.o.)
		PLog('Sofortstart: funk (ShowVideo)')
		prev_bandw = SETTINGS.getSetting('pref_funk_bandw')
		prev_bandw = prev_bandw.split(':')[0]			# 400:320x180	
		myform = get_forms(distrib,prev_bandw )			# passende form-Bandweite suchen 
		if  len(myform) == 0:							# Sicherung: kleinste 
			mp4_url = mp4_urls[0]
		else:											# tokenDASH leer falls Server funk-01.akamaized
			mp4_url = "https://%s%s/%s_src_%s.mp4?hdnts=%s"	% (server,locator,entityId,myform,tokenDASH)
	
		tag_add = ''
		if protected:
			tag_add = "geschützt"
		tag = "MP4 %s | %s" % (tag_add, re.search("_src_(.*?).mp4", mp4_url).group(1))	# 1920x1080_6000
		tag = tag + geoblock
		descr_par = "%s||||%s" % (tag, descr)
		PlayVideo(url=mp4_url, title=title_org, thumb=img, Plot=descr_par, Merk=Merk)
		return
		
	descr_par = descr
	descr = descr_par.replace('||', '\n')
		
	if protected == False:								# nicht funktionierenden Stream ausblenden
		title = "STREAM | %s" % title_org	
		tag = "STREAM %s x %s | fps %s | %s | %s" % (width, height, fps, aspect, orientation)
		tag = tag + geoblock
		title=py2_encode(title); stream_url=py2_encode(stream_url);
		img=py2_encode(img); descr_par=py2_encode(descr_par);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
			(quote(stream_url), quote(title), quote_plus(img), quote_plus(descr_par), Merk)	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag, summary=descr, mediatype='video')	
	
	title = "MP4 | %s" % title_org							# einzelne MP4-Url
	for mp4_url in mp4_urls:
		tag 	= "MP4 | %s" % re.search("_src_(.*?).mp4", mp4_url).group(1)	# 1920x1080_6000
		tag = tag + geoblock
		# PLog("mp4_url: "+ mp4_url)  s.o.
		title=py2_encode(title); mp4_url=py2_encode(mp4_url);
		img=py2_encode(img); descr_par=py2_encode(descr_par);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
			(quote(mp4_url), quote(title), quote_plus(img), quote_plus(descr_par), Merk)	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag, summary=descr, mediatype='video')	

	xbmcplugin.endOfDirectory(HANDLE)
				
# ----------------------------------------------------------------------
# zerteilt den Distribution-string (azureFileDistribution) in einzelne 
#	Auflösungen, passend für die Video-Url's
#	Bsp. 0400:320x180,0700:640x360,1500:1024x576,2500:1280x720,6000:1920x1080
#
def get_forms(distrib, prev_bandw=''):
	PLog('get_forms: ' + distrib)
	forms=[]
	
	records = distrib.split(',')
	records = sorted(records, reverse=True)		# absteigend
	bandw_old = '0'
	for rec in records:
		bandw, res = rec.split(':')		# 0400:320x180
		if bandw.startswith('0'):
			bandw = bandw[1:]	
		form = "%s_%s" % (res, bandw)	# 320x180_400
		if prev_bandw:					# Abgleich mit Settings
			#PLog(form); PLog(prev_bandw);  PLog(bandw);  PLog(bandw_old);
			#PLog(forms)
			if (int(prev_bandw) > int(bandw)) and (int(prev_bandw) <= int(bandw_old)):
				PLog(forms[-1])
				return forms[-1]
				
		forms.append(form)
		bandw_old = bandw
		
	if prev_bandw:						# Sicherung 	
		forms=[]	
	PLog('forms: ' + str(forms))
	return forms		

####################################################################################################
#									Hilfsfunktionen
####################################################################################################
# 17.10.2019 auth nicht mehr benötigt
#----------------------------------------------------------------  			
def loadPage(url, auth='', x_cid='', x_token='', data='', maxTimeout = None):
	try:
		safe_url = url.replace( " ", "%20" ).replace("&amp;","&")
		if data:
			safe_url="%s?%s" % (safe_url, data)
		PLog("loadPage: " + safe_url);

		req = Request(safe_url)
		
		# gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)		# 07.10.2019: Abruf mit SSLContext klemmt häufig - bei
		# 	Bedarf mit Prüfung auf >'_create_unverified_context' in dir(ssl)< nachrüsten:

		req.add_header('User-Agent', 'Mozilla/5.0 (Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36')
		req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
		req.add_header('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
		# hier nicht verwenden: 'Accept-Charset', 'utf-8' | 'Accept-Encoding', 'gzip, deflate, br'
		if auth:
			PLog(auth)
			aname, avalue = auth.split(',')		# Liste auth: "Name, Wert"
			req.add_header(aname, avalue) 	
		if x_cid:
			PLog(x_cid)
			aname, avalue = x_cid.split(',')	# Liste x_cid: "Name, Wert"
			req.add_header(aname, avalue) 	
		if x_token:
			PLog(x_token)
			aname, avalue = x_token.split(',')	# Liste x_token: "Name, Wert"
			req.add_header(aname, avalue) 	

		''' 25.11.2019 POST-data funktionieren hier nicht, Schwenk zu GET - s.o. 
		if data:
			data = urlencode(data)
			data = data.encode("utf-8")
			json.dumps(data).encode('utf8')
			PLog(data)
			req.data(data)						# ab Python 3.4
			req.add_data(data)					# Python 2.7 - 3.3
		'''
			
		if maxTimeout == None:
			maxTimeout = 60;
		# r = urlopen(req, timeout=maxTimeout, context=gcontext) # s.o.
		r = urlopen(req, timeout=maxTimeout)
		# PLog("headers: " + str(r.headers))
		doc = r.read()
		PLog(len(doc))	
		doc = doc.decode('utf-8')		
		return doc
		
	except Exception as exception:
		msg = 'Fehler: ' + str(exception)
		msg = msg + ': ' + safe_url			 			 	 
		PLog(msg)
		return msg

#---------------------------------------------------------------- 



