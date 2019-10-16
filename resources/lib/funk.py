# -*- coding: utf-8 -*-
################################################################################
#				funk.py - Teil von Kodi-Addon-ARDundZDF
#				Kanäle und Serien von https://www.funk.net/
################################################################################
# 	Credits: cemrich (github) für die wichtigsten api-Calls
#	
#	

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

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA			# hier nur DICTSTORE genutzt

ICON 			= 'icon.png'		# ARD + ZDF
ICON_FUNK		= 'funk.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_SPEAKER 	= "icon-speaker.png"
ICON_MEHR 		= "icon-mehr.png"
NAME			= 'ARD und ZDF'
MNAME			= "FUNK"

FUNKCacheTime = 300
AUTH = "authorization, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnROYW1lIjoid2ViYXBwLXYzMSIsInNjb3BlIjoic3RhdGljLWNvbnRlbnQtYXBpLGN1cmF0aW9uLWFwaSxuZXh4LWNvbnRlbnQtYXBpLXYzMSx3ZWJhcHAtYXBpIn0.mbuG9wS9Yf5q6PqgR4fiaRFIagiHk9JhwoKES7ksVX4"


def Main_funk():
	PLog('Main_funk:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
	
	# todo: Suche, playlists, Caching
	title = 'CHANNELS'
	fparams="&fparams={'title': '%s'}" % title
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
		thumb=R(ICON_DIR_FOLDER), fparams=fparams)
		
	#title = 'PLAYLISTS'
	#fparams="&fparams={'title': '%s'}" % title
	#addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.Channels", fanart=R(ICON_FUNK), 
	#	thumb=R(ICON_DIR_FOLDER), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE)
		
# ----------------------------------------------------------------------			
# alle Channels: https://www.funk.net/api/v4.0/channels/ - s. Search
#
def Channels(title, next_path=''):
	PLog('Channels:')
	PLog(next_path)
	title_org = title
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)			# Home-Button
	
	
	
	pagenr = stringextract('page=', '&', next_path)		
	if title == 'CHANNELS': 	# CHANNELS
		jsonKey = "channelDTOList"
		if next_path == '':
			next_path = 'https://www.funk.net/api/v4.0/channels/?size=50' 
			pagenr 		= "0"
	else:						# PLAYLISTS
		jsonKey = "playlistDTOList"
		if next_path == '':
			next_path = 'https://www.funk.net/api/v4.0/playlists/?size=50'
			pagenr 		= "0"	
		
	storeId = 'channels_page%s' % pagenr
	# page = Dict("load", storeId, CacheTime=FUNKCacheTime)					
	# if page == False:											# nicht vorhanden oder zu alt
	page = loadPage(next_path, AUTH)

	if len(page) == 0 or str(page).startswith('Fehler'):
		xbmcgui.Dialog().ok(ADDON_NAME, 'Fehler beim Abruf von:', next_path, '')
		xbmcplugin.endOfDirectory(HANDLE)
		
	jsonObject = json.loads(page)
	# Debug:
	#RSave("/tmp/x_channels.json", json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))
	#Dict('store', 'channels', jsonObject)
	#jsonObject = Dict('load', storeId)

	if("_embedded" in jsonObject):
		PLog('channels jsonKey')
		for stageObject in jsonObject["_embedded"][jsonKey]:
			typ,title,alias,descr,img,date,entityGroup,entityId = extract_channels(stageObject) 
			if typ =='':		# Sicherung
				continue
			if alias:			# Subtitel
				title = '%s | %s' % (title,alias)
			date = time_translate(date)

			# path = 'stage|%d' % i
			fparams="&fparams={'title': '%s', 'jsonKey': '%s', 'entityId': '%s'}"  % (title, jsonKey, entityId)
			PLog(title); PLog(entityId); 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ChannelSingle", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=descr, summary=date, fparams=fparams)					
		
	pN,pageSize,totalPages,totalElements,next_path = get_pagination(jsonObject)	# Mehr?		
	if next_path:	
		summ = "insgesamt: %s Seite(n) , %s Beiträge" % (totalPages, totalElements)
		pN = int(pN)								# nächste pageNumber, Basis 0
		tag = "weiter zu Seite %s" % str(pN)
		fparams="&fparams={'title': '%s','next_path': '%s'}" % (urllib2.quote(title_org), urllib2.quote(next_path))
		addDir(li=li, label=title_org, action="dirList", dirID="resources.lib.funk.Channels", 
			fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ, tagline=tag, fparams=fparams)	
	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# zeigt alle Videos eines Channels
#	Alternative: byChannelAlias
def ChannelSingle(title, jsonKey, entityId):
	PLog('ChannelSingle: ' + jsonKey)
	PLog(entityId)
	jsonKey = UtfToStr(jsonKey)
	title_org = title
	
	li = xbmcgui.ListItem()
	li = home(li, ID=MNAME)				# Home-Button
		
	store_id = 'channel_%s' % entityId
	path = "https://www.funk.net/api/v4.0/videos/byChannelId/%s" % entityId
	if 'playlist' in jsonKey:
		path = "https://www.funk.net/api/v4.0/playlists/%s" % entityId
		store_id = 'playlist%s' % entityId
		
	page = loadPage(path, AUTH)
	jsonObject = json.loads(page)
	
	#Dict('store',store_id , jsonObject)
	# Debug:
	# RSave("/tmp/x_%s.json" % store_id, json.dumps(jsonObject, sort_keys=True, indent=2, separators=(',', ': ')))

	if("_embedded" in jsonObject):
		PLog('channels %s' % jsonKey)
		for stageObject in jsonObject["_embedded"]["videoDTOList"]:
			title,alias,descr,img,date,dur,cr,entityId = extract_videos(stageObject) 
			if alias:			# hier channelAlias
				title = '%s | %s' % (alias, title)
			date = time_translate(date)
			dur = seconds_translate(dur)
			tag = "%s | %s" % (date, dur)
			if cr:
				tag = "%s | %s | Copyright: %s" % (date, dur, cr)
			# Probleme mit zahlreichen /r/n
			descr_par = descr.replace('\n', '||'); descr_par = descr_par.replace('\r', '')  # \r\n\r\n
			descr_par = repl_json_chars(descr_par); 
			title = repl_json_chars(title)

			fparams="&fparams={'title': '%s', 'img': '%s', 'descr': '%s', 'entityId': '%s'}"  %\
				(urllib2.quote(title), urllib2.quote(img), urllib2.quote(descr_par), entityId)
			PLog(title); PLog(entityId); 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.funk.ShowVideo", 				
				fanart=R(ICON_FUNK), thumb=img, tagline=tag, summary=descr, fparams=fparams)					
	
	pN,pageSize,totalPages,totalElements,next_path = get_pagination(jsonObject)	# Mehr?		
	if next_path:	
		summ = "insgesamt: %s Seite(n) , %s Beiträge" % (totalPages, totalElements)
		pN = int(pN)								# nächste pageNumber, Basis 0
		tag = "weiter zu Seite %s" % str(pN)
		fparams="&fparams={'next_path': '%s'}" % (urllib2.quote(next_path))
		addDir(li=li, label=title_org, action="dirList", dirID="resources.lib.funk.Channels", 
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
	# PLog(str(stageObject))

	title=stageObject["title"]						# konstante Details 
	alias=stageObject["alias"]
	entityId = stageObject["entityId"]
	PLog(entityId)
			
	descr=''										# variable Details 
	if("description" in stageObject):
		descr = stageObject["description"]
	else:
		if("shortDescription" in stageObject):
			descr = stageObject["shortDescription"]
			
	typ=''	
	if("type" in stageObject):
		typ = stageObject["type"]
		
	img="";	# weitere: imageUrlLandscape, imageUrlOrigin
			#	imageUrlSquare
	if("imageUrlSquare" in stageObject):
		img = stageObject["imageUrlSquare"]
	if img == '':
		if "imageUrlLandscape" in stageObject:
			img = stageObject["imageUrlLandscape"]
	if img == '':		# Falback
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
		
	title=title.encode("utf-8"); alias=alias.encode("utf-8"); descr=descr.encode("utf-8");
	entityGroup=str(entityGroup); entityId=str(entityId); 
	entityGroup=entityGroup.encode("utf-8"); entityId=entityId.encode("utf-8");
	date=date.encode("utf-8"); typ=typ.encode("utf-8"); img=img.encode("utf-8"); 
	
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
	# PLog(str(stageObject))
											# konstante Details 
	title=stageObject["title"]
	alias=stageObject["channelAlias"]		# statt alias (ähnlich title)
	myhash = stageObject["hash"]	

	entityId = stageObject["entityId"]		# int
	channelId = stageObject["channelId"]	# int
	dur = stageObject["duration"]			# int
						
											# variable Details 
	img=""; date=''; entityGroup=''; cr=''; genre=''; descr=''
	if("description" in stageObject):
		descr = stageObject["description"]	
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
	if img == '':		# Falback
		img = R(ICON_DIR_FOLDER) 
		
	if("publicationDate" in stageObject):
		date = stageObject["publicationDate"]
	else:
		if("updateDate" in stageObject):
			date = stageObject["updateDate"]
	
	if("entityGroup" in stageObject):
		entityGroup = stageObject["entityGroup"]
		
	title=title.encode("utf-8"); alias=alias.encode("utf-8"); descr=descr.encode("utf-8");
	dur=str(dur); entityId=str(entityId); channelId=str(channelId); 
	entityGroup=entityGroup.encode("utf-8"); entityId=entityId.encode("utf-8");
	date=date.encode("utf-8"); img=img.encode("utf-8");
	dur=UtfToStr(dur); cr=UtfToStr(cr);genre=UtfToStr(genre);
	
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
# todo: Videoobjekt aus Videoliste in ChannelSingle extrahieren	
#		loadPageCalls absichern
#
def ShowVideo(title, img, descr, entityId):
	PLog('ShowVideo:'); PLog(title); PLog(entityId)
	
	path = "https://www.funk.net/api/v4.0/videos/%s" % entityId
	page = loadPage(path, AUTH)
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
	jsonObject = json.loads(page)
	x_cid 	= jsonObject["result"]["general"]["cid"]
	# x-request-token nicht im jsonObject
	PLog("cid: " + x_cid)	
														# 2. Video-Metadaten
	x_cid	= "x-request-cid,%s" % x_cid							# x-request-cid
	x_token = "x-request-token,f058a27469d8b709c3b9db648cae47c2"	# x-request-token
	data = 'addStatusDetails=1&addStreamDetails=1&addFeatures=1&addCaptions=1&addBumpers=1&captionFormat=data'
	path = "https://api.nexx.cloud/v3/741/videos/byid/%s" % entityId
	page = loadPage(path, x_cid=x_cid, x_token=x_token, data=data)
	PLog(page[:80]) 
	jsonObject = json.loads(page)	
														# 3. Stream-Url 
	server = jsonObject["result"]["streamdata"]["cdnShieldProgHTTPS"]
	locator = jsonObject["result"]["streamdata"]["azureLocator"]	
	distrib  = jsonObject["result"]["streamdata"]["azureFileDistribution"]
	
	server = jsonObject["result"]["streamdata"]["cdnShieldProgHTTPS"]
	locator = jsonObject["result"]["streamdata"]["azureLocator"]	
	stream_url = "https://%s/%s/%s_src.ism/Manifest(format=mpd-time-cmaf)"	% (server,locator,entityId)
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
	tag = "%s x %s | fps %s | %s | %s" % (width, height, fps, aspect, orientation)
	
	title=UtfToStr(title);
	title = repl_json_chars(title)
	title_org = title
	
	PLog('Mark1')
	Merk='false'
	if SETTINGS.getSetting('pref_video_direct') == 'true':	# Sofortstart
		PLog('Sofortstart: funk (ShowVideo)')
		PlayVideo(url=stream_url, title=title_org, thumb=img, Plot=descr, Merk=Merk)
		return
		
	PLog('Mark2')
	stream_url=UtfToStr(stream_url); img=UtfToStr(img);  descr=UtfToStr(descr); 
	Merk=UtfToStr(Merk); tag=UtfToStr(tag);
	descr_par = descr
	descr = descr_par.replace('||', '\n')
	descr_par=UtfToStr(descr_par);
	
	PLog('Mark3')
	title = "STREAM | %s" % title_org	
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
		(urllib2.quote(stream_url), urllib2.quote(title), urllib.quote_plus(img), urllib.quote_plus(descr_par), Merk)	
	addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
		thumb=img, fparams=fparams, tagline=tag, summary=descr, mediatype='video')	
	
	PLog('Mark4')
	title = "MP4 | %s" % title_org							# einzelne MP4-Url
	for form in forms:
 		tag 	= "MP4 | %s" % form
		mp4_url = "https://%s/%s/%s_src_%s.mp4"	% (server,locator,entityId,form)
		mp4_url=UtfToStr(mp4_url); tag=UtfToStr(tag);
		PLog("mp4_url: "+ mp4_url)
		# https://funk-01.akamaized.net/59536be8-46cc-4d1e-83b7-d7bab4b3eb5d/1633982_src_1920x1080_6000.mp4
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'Merk': '%s'}" % \
			(urllib2.quote(mp4_url), urllib2.quote(title), urllib.quote_plus(img), urllib.quote_plus(descr_par), Merk)	
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img, 
			thumb=img, fparams=fparams, tagline=tag, summary=descr, mediatype='video')	

	xbmcplugin.endOfDirectory(HANDLE)
				
# ----------------------------------------------------------------------
# zerteilt den Distribution-string (azureFileDistribution) in einzelne 
#	Auflösungen, passend für die Video-Url's
#	Bsp. 0400:320x180,0700:640x360,1500:1024x576,2500:1280x720,6000:1920x1080
#
def get_forms(distrib):
	PLog('get_forms: ' + distrib)
	forms=[]
	
	records = distrib.split(',')
	for rec in records:
		bandw, res = rec.split(':')		# 0400:320x180
		if bandw.startswith('0'):
			bandw = bandw[1:]	
		form = "%s_%s" % (res, bandw)	# 320x180_400
		forms.append(form)
	PLog('forms: ' + str(forms))
	return forms		

####################################################################################################
#									Hilfsfunktionen
####################################################################################################
#----------------------------------------------------------------  			
def loadPage(url, auth='', x_cid='', x_token='', data='', maxTimeout = None):
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
		if auth:
			PLog(auth)
			aname, avalue = auth.split(',')	# Liste auth: "Name, Wert"
			req.add_header(aname, avalue) 	
		if x_cid:
			PLog(x_cid)
			aname, avalue = x_cid.split(',')	# Liste x_cid: "Name, Wert"
			req.add_header(aname, avalue) 	
		if x_token:
			PLog(x_token)
			aname, avalue = x_token.split(',')	# Liste x_token: "Name, Wert"
			req.add_header(aname, avalue) 	

		if data:
			req.add_data(data)
			
		if maxTimeout == None:
			maxTimeout = 60;
		# r = urllib2.urlopen(req, timeout=maxTimeout, context=gcontext) # s.o.
		r = urllib2.urlopen(req, timeout=maxTimeout)
		# PLog("headers: " + str(r.headers))
		doc = r.read()
		PLog(len(doc))	
		#if '<!DOCTYPE html>' not in doc:	# Webseite nicht encoden (code-error möglich)
		#	doc = doc.encode('utf-8')		
		return doc
		
	except Exception as exception:
		msg = 'Fehler: ' + str(exception)
		msg = msg + '\r\n' + safe_url			 			 	 
		msg =  msg
		PLog(msg)
		return msg

#---------------------------------------------------------------- 



