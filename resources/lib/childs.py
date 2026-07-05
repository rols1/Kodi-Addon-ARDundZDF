# -*- coding: utf-8 -*-
################################################################################
#				childs.py - Teil von Kodi-Addon-ARDundZDF
#		Rahmenmodul für Kinderprg div. Regionalsender von ARD und ZDF
#
#	02.11.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
################################################################################
#	
# 	<nr>45</nr>										# Numerierung für Einzelupdat1
#	Stand: 05.07.2026

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

import  json		
import os, sys
import ssl
import datetime, time
import re				# u.a. Reguläre Ausdrücke
import string

import ardundzdf					# -> SenderLiveResolution, transl_wtag, get_query, Audio_get_sendung, ..
from resources.lib.util import *


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

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('childs_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 				# hier nur DICTSTORE genutzt

NAME			= 'ARD und ZDF'

BASE_ZDF		= 'https://www.zdf.de'
BASE_KIKA 		= 'https://www.kika.de'
BASE_TIVI 		= 'https://www.zdf.de/kinder'

# Icons
ICON 			= 'icon.png'		# ARD + ZDF
ICON_CHILDS		= 'childs.png'			
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_MAIN_TVLIVE= 'tv-livestreams.png'
ICON_MEHR 		= "icon-mehr.png"
ICON_SEARCH 	= 'ard-suche.png'
ICON_ZDF_SEARCH = 'zdf-suche.png'
				
MAUSLIVE		= "https://www.wdrmaus.de//_teaserbilder/720913_512.jpg"
MAUSZOOM		= "https://www.wdrmaus.de//_teaserbilder/720893_512.jpg"
MAUSRELIVE		= "https://www.wdrmaus.de//_teaserbilder/721363_512.jpg"
MAUSHEAR		= "https://www1.wdr.de/mediathek/audio/sendereihen-bilder/maus_sendereihenbild_podcast-1-100~_v-original.jpg"

# ext. Icons zum Nachladen aus Platzgründen,externe Nutzung: 						
KIKA_START		= "https://www.kika.de/bilder/startseite-104_v-tlarge169_w-1920_zc-a4147743.jpg"	# ab 07.12.2022
KIKA_VIDEOS		= "https://www.kika.de/videos/bilder/videos-110_v-tlarge169_zc-cc2f4e31.jpg"		# - " -
KIKA_AD			= "https://www.kika.de/audiodeskription/ad-110_v-tlarge169_zc-cc2f4e31.jpg?version=6313"
KIKA_DGS		= "https://www.kika.de/gebaerdensprache/dgs-110_v-tlarge169_zc-cc2f4e31.jpg?version=58142"
KIKA_SERIES		= "https://www.kika.de/videos/serie-100_v-tlarge169_zc-cc2f4e31.jpg?version=16437"
KIKA_FILME		= "https://www.kika.de/videos/film-108_v-tlarge169_zc-cc2f4e31.jpg?version=4412"
KIKA_WISSEN		= "https://www.kika.de/videos/wissen-108_v-tlarge169_zc-cc2f4e31.jpg?version=11506"
KIKA_SHOWS		= "https://www.kika.de/videos/show-100_v-tlarge169_zc-cc2f4e31.jpg?version=3229"
KIKA_LIVE		= "https://www.kika.de/live/bilder/live-102_v-tlarge169_zc-cc2f4e31.jpg?version=32751"

GIT_AZ			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/icon-AZ.png?raw=true"
				# Einzelbuchstaben zu A-Z siehe Tivi_AZ
GIT_KANINCHEN	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaninchen.png?raw=true"
GIT_ZDFTIVI		= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-zdftivi.png?raw=true"
GIT_TIVIHOME	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/zdftivi-home.png?raw=true"
GIT_DGS			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaDGS.png?raw=true"
GIT_AD			= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-kikaAD.png?raw=true"
GIT_ARD_KINDER	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/tv-ard_kinder-familie.png?raw=true"

# 14.12.2022 1024x1024:
GIT_KIKALIVE	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_KIKALIVE.png?raw=true"
GIT_MAUSLIVE	= "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/GIT_MAUSLIVE.png?raw=true"


KikaCacheTime = 1*3600					# Addon-Cache für A-Z-Seiten: 1 Stunde
KIKA_HEADERS	="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', \
		'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate, br', 'Cache-Control': 'max-age=0'}"


# ----------------------------------------------------------------------			
def Main_childs():
	PLog('Main_childs:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)			# Home-Button
		
	title = "ARD - Kinder und Familie"
	tag = u"Märchen, Spielfilme, Serien, Wissen und Dokus - hier gibt's unterhaltsame und "
	tag = u"%s%s" % (tag, u"spannende Videos für Kinder und die ganze Familie!")
	img = GIT_ARD_KINDER
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/kinderfamilie?embedded=true"
	ID = "Main_childs"
	fparams="&fparams={'path': '%s', 'title': '%s', 'widgetID': '', 'ID': '%s'}" %\
		(quote(path), quote(title), ID)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", 
		fanart=R(ICON_CHILDS), thumb=img, tagline=tag, fparams=fparams)

	title = u"ZDFtivi für Kinder"
	fparams="&fparams={'title': '%s'}" % "tivi"
	addDir(li=li, label= title, action="dirList", dirID="resources.lib.childs.Main_TIVI", 
		fanart=R(ICON_CHILDS), thumb=GIT_ZDFTIVI, fparams=fparams)

	# Historie KiKA + KiKANiNCHEN: de.wikipedia.org/wiki/KiKA
	title='KiKA_Sendungen A-Z | 0-9'
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KiKA_AZ",
		fanart=R(ICON_CHILDS), thumb=KIKA_START, tagline=title, fparams=fparams)

	title='KiKA Live gucken'
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_Live", 
		fanart=R(ICON_CHILDS), thumb=GIT_KIKALIVE, tagline='KIKA TV-Live', fparams=fparams)
	
	title='KiKANiNCHEN'
	tag = u"für Kleinkinder (3-6 Jahre) und Grundschulkinder (6-12 Jahre)"
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_Menu", 
		fanart=R(ICON_CHILDS), thumb=GIT_KANINCHEN, tagline=tag, fparams=fparams)

	title=u'Maus hören'										# TV-Live nur SO (DAS ERSTE, KiKA)
	tag = u"%s\n\nDer Kinderradiokanal des WDR  (Nachfolgeseite für [B]KiRaKa[/B])" % title
	img = GIT_MAUSLIVE
	fparams="&fparams={}" 
	addDir(li=li, label=title , action="dirList", dirID="resources.lib.childs.MausLive",
		fanart=R(ICON_CHILDS), thumb=img, tagline=tag, fparams=fparams)

	title = u"Hörspaß für Kinder | ARD sounds"						# neu ab 15.05.2026
	path = "https://www.ardsounds.de/rubrik/fuer-kinder-100/"
	img = "https://api.ardmediathek.de/image-service/images/urn:ard:image:a35d70a04d27e46d?ch=1781783569070&w=640"
	tag = u"Geschichten, Hörspiele und Wissen für Kinder: Entdecke die Kinder-"
	tag = u"%sPodcasts – spannend, lustig und lehrreich. Mit Checker Tobi, dem" % tag
	tag = u"%s Ohrenbär und der Maus." % tag
	title = py2_encode(title); path = py2_encode(path)
	fparams="&fparams={'title': '%s', 'path': '%s', 'rubrik_title': '%s','homeID': '%s'}" %\
		(quote(title), quote(path), quote(title), "Kinderprogramme")
	addDir(li=li, label=title, action="dirList", dirID="Audio_get_rubriken_web", 
		fanart=R(ICON_CHILDS), thumb=img, tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
# ----------------------------------------------------------------------
# 23.07.2024 tivi_Verpasst abgeschaltet wg. Ausfall cdn-api
#			
def Main_TIVI(title=''):
	PLog('Main_TIVI:')
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
			
	if SETTINGS.getSetting('pref_use_mvw') == 'true':
		title = 'Suche auf MediathekViewWeb.de'
		tag = "Extrem schnelle Suche im Datenbestand von MediathekView."
		summ = 'gesucht wird in [B]ZDF-tivi[/B]'
		title=py2_encode(title);
		func = "resources.lib.childs.Main_TIVI"
		fparams="&fparams={'title': '%s','sender': '%s' ,'myfunc': '%s'}" % \
			(quote(title), "ZDF-tivi", quote(func))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.yt.MVWSearch", fanart=GIT_ZDFTIVI, 
			thumb=R("suche_mv.png"), tagline=tag, summary=summ, fparams=fparams)

	title='tivi_Startseite'												# HBBTV
	coll_id = "06b4a744-3a6a-4a49-9eaf-4c6a4b59d0dc"
	fparams="&fparams={'coll_id': '%s', 'homeID': '%s'}" % (coll_id,'Kinderprogramme')
	addDir(li=li, label=title , action="dirList", dirID="ardundzdf.ZDF_Start", fanart=GIT_ZDFTIVI, 
		thumb=GIT_TIVIHOME, tagline=title, fparams=fparams)	
					
	# 07.06.2026 Tivi_Search entfernt (wie ZDF-Web und HBBTV).						
	# 29.01.2026 Menü tivi_Verpasst entfernt - beim ZDF nicht mehr verfügbar
	#title = 'tivi_Verpasst' 	# ZDF_VerpasstWoche -> tivi_Verpasst
	
	title='tivi_Sendungen A-Z | 0-9'									# Graphql
	fparams="&fparams={}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ", fanart=GIT_ZDFTIVI, 
		thumb=GIT_AZ, tagline=title, fparams=fparams)

	title='tivi_ZDFchen'												# HBBTV
	tag = u"Für Kinder bis 6 Jahre"
	thumb = "https://www.zdf.de/assets/zdfchen-buehne-m-song-100~936x520?cb=1658852787035"		
	coll_id = "4a232aa9-93ee-4eb8-8028-acc0580e709f"
	fparams="&fparams={'coll_id': '%s', 'homeID': '%s'}" % (coll_id,'Kinderprogramme')
	addDir(li=li, label=title , action="dirList", dirID="ardundzdf.ZDF_Start", fanart=GIT_ZDFTIVI, 
		thumb=thumb, tagline=title, fparams=fparams)	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 26.06.2026 neu: Serien via ARD-HBBTV, Kikaninchen Schnipselwelt herausgehoben
#	aus Serien für Kleinkinder, KikaninchenLieder weiterhin aus liederkikaninchen100.json
#	(umfangreicher als Lieder der Schnipselwelt 46 / 13)
#
def Kikaninchen_Menu():
	PLog('Kikaninchen_Menu:')
	li = xbmcgui.ListItem()
	homeID = 'Kinderprogramme'
	li = home(li, ID=homeID)			# Home-Button
	
	# Serien für Grundschulkinder Cluster 22
	img = "https://api.ardmediathek.de/image-service/images/urn:ard:image:db05866cfd75ff60?ch=19571067c4577f13&w=640"
	title = u'Serien für Grundschulkinder'
	tag = 'für Kinder 6-12 Jahre'
	fparams="&fparams={ 'title': '%s'}" % (title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_HBBTV_Cluster", 
		fanart=GIT_KANINCHEN, thumb=img, tagline=tag, fparams=fparams)

	# Serien für Kleinkinder Cluster 21
	img = "https://api.ardmediathek.de/image-service/images/urn:ard:image:e06f802f9d91f5bb?ch=098fed94dde53a80&w=640"
	title = u'Serien für Kleinkinder'
	tag = 'für Kinder 3-6 Jahre'
	fparams="&fparams={ 'title': '%s'}" % (title)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kika_HBBTV_Cluster", 
		fanart=GIT_KANINCHEN, thumb=img, tagline=tag, fparams=fparams)

	title='Kikaninchen Singen und Tanzen'
	img = "https://api.ardmediathek.de/image-service/images/urn:ard:image:7ccf56d919c2961e?w=640&ch=932484bd5a8ad1c4"
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KikaninchenLieder", 
		fanart=GIT_KANINCHEN, thumb=img, tagline='für Kinder 3-6 Jahre', fparams=fparams)
	
	title='Kikaninchen Schnipselwelt'		
	ardpath="https://api.ardmediathek.de/page-gateway/widgets/ard/asset/%s?pageNumber=1&pageSize=24"
	path = "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/kikaninchen-schnipselwelt?embedded=true&mcV6=true"
	thumb="https://www.kika.de/kikaninchen-schnipselwelt/bilder/kikaninchen-schnipselwelt-150-resimage_v-tsquare11_w-1024.jpg?version=11459"
	img = "https://api.ardmediathek.de/image-service/images/urn:ard:image:a713f99e2ad4acda?w=640&ch=a8d7977d31e9a0df"
	tag = "In der Schnipselwelt erleben Kikaninchen, Anni und Christian jeden Tag ein neues Abenteuer" 
	path = py2_encode(path)
	fparams="&fparams={'li': '', 'path': '%s', 'homeID': '%s'}" % (quote(path), homeID)
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDRubriken",
		fanart=GIT_KANINCHEN, thumb=img, tagline=tag, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# 24.06.2026 Neu 
# Aufruf Kikaninchen_Menu (Serien für Grundschulkinder / Kleinkinder)
#
def Kika_HBBTV_Cluster(title): 
	PLog('Kika_HBBTV_Cluster: %s' % title)
	
	icon = KIKA_START
	path = "https://tv.ardmediathek.de/dyn/get?id=editorial:ard:kinderfamilie"		
	DictID =  "ARD_kinderfamilie" 
	page = Dict("load", DictID, CacheTime=KikaCacheTime)	# 1 Std.			
	if not page:												# nicht vorhanden oder zu alt						
		xbmcgui.Dialog().notification("Cache:","Haltedauer 1 Stunde",icon,3000,sound=False)
		page, msg = get_page(path)								# vom Sender holen			
		if page:
			Dict('store', DictID, page)
	PLog(str(page)[:80])
			
	try:
		objs = json.loads(page)
		mycluster=[]
		cluster = objs["elems"]
		PLog("cluster: %d" % len(cluster))
		cnt=0
		for item in cluster:
			PLog("cnt: %d | %s" % (cnt, str(item)[:80]))
			if "message" in item["type"]:								# Message-cluster vor Inhalt-cluster
				if title in item["title"]:
					mycluster = cluster[cnt+1]							# nächster Cluster
					break
			if "covers" in item["type"]:								# akt. Cluster
				if title in item["cpixTitle"]:
					mycluster = cluster[cnt]
					break
			cnt=cnt+1
	except Exception as exception:
		PLog("Kika_HBBTV_Cluster_error: " + str(exception))
		xbmcgui.Dialog().notification("leider nicht gefunden:", title,icon,3000,sound=True)
		
	elems = mycluster["elems"]
	PLog("%s | elems: %d, index: %d" % (title, len(elems), cnt))
	ARD_getHBBTV_content(title, elems)									# Ausgabe
	return
	
# ----------------------------------------------------------------------
# Auswertung json-Inhalt ARD-HBBTV
# Aufruf: Kika_HBBTV_Cluster
#
def ARD_getHBBTV_content(wtitle, elems):
	PLog('ARD_getHBBTV_content:')
	PLog(wtitle)
	PLog(str(elems)[:60])
	
	# HBBTV-Alternative: https://tv.ardmediathek.de/dyn/get?id=link_id
	# base_video 	"ttyp": "t01", "t03"	-> ARDStartSingle
	# base_rubrik 	"ttyp": "t05" 	-> ARDStartRubrik (embedded=true: vollständig),
	# base_serie 	"ttyp": "t02"	-> ARDStartRubrik -> heroImage_detect
	base_video = "https://api.ardmediathek.de/page-gateway/pages/ard/item/%s?embedded=true"	
	base_rubrik= "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/%s?embedded=true&mcV6=true"	
	base_serie = "https://api.ardmediathek.de/page-gateway/pages/ard/grouping/%s?embedded=true&seasoned=true"

	homeID="Kinderprogramme"	
	li = xbmcgui.ListItem(); li2 = xbmcgui.ListItem()
	li = home(li, ID=homeID)		# Home-Button			
	mediatype=''												# Kennz. Video für Sofortstart
	if SETTINGS.getSetting('pref_video_direct') == 'true':
		mediatype='video'

	cnt=0; fcnt=0;												# fcnt: Filterzähler
	for item in elems:
		typ="";title="";tag="";summ="";img="";
		try:
			cnt=cnt+1
			ttyp = item["ttyp"]									# 
			title = item["cpixTitle"]
			title  = repl_json_chars(title)
			
			img = item["imgHi"]									# w=640
			link = item["link"]
			link_type = link["type"]
			link_id = link["id"]
			
			label=title
		except Exception as exception:
			PLog("ARD_getHBBTV_content_error: " + str(exception))
			msg1 = "Fehler in ARD_getHBBTV_content:"
			msg2 = str(exception) 
			MyDialog(msg1, msg2, '')	
			return											

		PLog('Satz3:'); 
		PLog(title); PLog(ttyp); PLog(link_type); PLog(link_id);PLog(img)
		title=py2_encode(title);
		img=py2_encode(img); title=py2_encode(title);

		if "video" in link_type:								# ttyp t01, t03
			ID="ARD_getHBBTV_content"
			tag="Vdeo"
			link_id = link_id.split("video:")[-1]
			path = base_video % link_id
			PLog("path: " + path)
			
			title=py2_encode(title); path=py2_encode(path);
			fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s','homeID': '%s'}" %\
				(quote(path), quote(title), ID, homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartSingle", 
				fanart=img, thumb=img, fparams=fparams, tagline=tag, mediatype=mediatype)

		else:													# ttyp	t02, t05 (t04 nicht gesehen)										
			tag="Folgeseiten"
			if "t02" in ttyp:
				link_id = link_id.split("grouping:")[-1]
				path = base_serie % link_id
			else:
				link_id = link_id.split("editorial:ard:")[-1]
				path = base_rubrik % link_id
				
			PLog("path: " + path)
			title=py2_encode(title); path=py2_encode(path);
			if "t02" in ttyp: 
				fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", 
					fanart=img, thumb=img, tagline=tag, fparams=fparams)
			else:
				fparams="&fparams={'li': '', 'path': '%s', 'homeID': '%s'}" % (quote(path), homeID)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDRubriken", 
					fanart=img, thumb=img, tagline=tag, fparams=fparams)				
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# 27.06.2026 neu
# Step 1: Button-Link-Liste, Step2: Beiträge pro Button
# ARD-Api-Link in Links|target|href -> ARDStartRubrik (Serienerkenung)
# 
def KiKA_AZ(button="", href=""):
	PLog('KiKA_AZ: %s' % href)
	
	icon = KIKA_START
	DictID = "KiKA_AZ"
	page = Dict("load", DictID, CacheTime=KikaCacheTime)	# Linkliste stündlich erneuern
	if not page:
		path = "https://api.ardmediathek.de/page-gateway/pages/kika/editorial/experiment-a-z?embedded=false"
		page, msg = get_page(path)	
		if page:
			Dict("store", DictID, page)

	try:
		objs = json.loads(page)
		widgets = objs["widgets"]				# Buchstaben-widgets nur, falls Beiträge vorhanden
		PLog("widgets: %d" % len(widgets))			
	except Exception as exception:
		PLog("KiKA_AZ_error1: " + str(exception))
		xbmcgui.Dialog().notification("KiKA_AZ Fehler:", "leider nichts gefunden",icon,3000,sound=True)
		return
		
	homeID="Kinderprogramme"
	li = xbmcgui.ListItem()
	li = home(li, ID=homeID)			# Home-Button
	#--------------------------------------------------------------		# Step 1 Buchstaben + Linkliste
	if not href:
		for item in widgets:
			links = item["links"]["self"]
			href = links["href"] 
			button = links["title"] 
			if button == "#":
				button = "0-9"					# Anpas. img-Name
			img = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
			title = "Sendungen mit " + button

			PLog("Satz2:"); PLog(title); PLog(img); PLog(href)
			href=py2_encode(href); 		
			fparams="&fparams={'button': '%s', 'href': '%s'}" % (button, quote(href))
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.KiKA_AZ", fanart=R(ICON_DIR_FOLDER), 
				thumb=img, fparams=fparams, tagline=title)

		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
			
	else:		
	#--------------------------------------------------------------		# Step 2 Beiträge
		base_rubrik= "https://api.ardmediathek.de/page-gateway/pages/ard/editorial/%s?embedded=true&mcV6=true"	
		href = href.replace("embedded=false", "embedded=true")
		page, msg = get_page(href)
		try:
			objs = json.loads(page)
			teasers = objs["teasers"]				# Buchstaben-widgets nur, falls Beiträge vorhanden
			PLog("teasers: %d" % len(widgets))			
		except Exception as exception:
			PLog("KiKA_AZ_error2: " + str(exception))
			xbmcgui.Dialog().notification("KiKA_AZ Fehler: ", "Buchstabe %s" % button,icon,3000,sound=True)
			return

		ID = "KiKA_AZ"
		for item in teasers:
			# typ = item["coreAssetType"]			# kann fehlen, nicht benötigt
			sid = item["id"]
			title = item["longTitle"]
			title = repl_json_chars(title)
			
			links = item["links"]
			path = links["target"]["href"]
			
			
			img_cont= item["images"]["aspect16x9"]
			img 	= img_cont["src"]
			img 	= img.replace('{width}', '640')
			img_alt	= img_cont["alt"]
			img_alt = decode_url(img_alt)
			
			tag = "Folgeseiten\nBild: %s" % img_alt
			path=py2_encode(path); title=py2_encode(title); 	

			fparams="&fparams={'path': '%s', 'title': '%s', 'ID': '%s', 'homeID': '%s'}" %\
				(quote(path), quote(title), ID, homeID)
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARDnew.ARDStartRubrik", 
				fanart=img, thumb=img, tagline=tag, fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# 25.06.2020 Nutzung neue Funktion get_ZDFstreamlinks
#
def Kika_Live():
	PLog('Kika_Live:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	import resources.lib.EPG as EPG
	zdf_streamlinks = get_ZDFstreamlinks()
	# Zeile zdf_streamlinks: "webtitle|href|thumb|tagline"
	m3u8link=''
	for line in zdf_streamlinks:
		PLog(line)
		webtitle, href, thumb, tagline = line.split('|')
		# Bsp.: "ZDFneo " in "ZDFneo Livestream":
		if up_low('KiKA') in up_low(webtitle): 	# Sender mit Blank!
			m3u8link = href
			break
	if m3u8link == '':
		PLog('%s: Streamlink fehlt' % 'KiKA ')
	
	ID = 'KIKA'
	title = 'KIKA TV-Live'
	Merk = ''
	
	rec = EPG.EPG(ID=ID, mode='OnlyNow')		# Daten holen - nur aktuelle Sendung
	PLog(rec)	# bei Bedarf
	if len(rec) == 0:							# EPG-Satz leer?
		title = 'EPG nicht gefunden'
		summ = ''
		tagline = ''
	else:	
		href=rec[1]; img=rec[2]; sname=rec[3]; stime=rec[4]; summ=rec[5]; vonbis=rec[6]
		if img.find('http') == -1:	# Werbebilder today.de hier ohne http://
			img = R('tv-kika.png')
		title 	= sname.replace('JETZT', ID)		# JETZT durch Sender ersetzen
		# sctime 	= "[COLOR red] %s [/COLOR]" % stime			# Darstellung verschlechtert
		# sname 	= sname.replace(stime, sctime)
		tagline = 'Zeit: ' + vonbis
				
	title = unescape(title); title = repl_json_chars(title)
	summ = unescape(summ); summ = repl_json_chars(summ)
	summ_par= summ.replace('\n', '||')
	PLog("title: " + title); PLog(summ)
	title=py2_encode(title); m3u8link=py2_encode(m3u8link);
	img=py2_encode(img); summ_par=py2_encode(summ_par);			
	fparams="&fparams={'path': '%s', 'title': '%s', 'thumb': '%s', 'descr': '%s', 'Merk': '%s'}" %\
		(quote(m3u8link), quote(title), quote(img), quote_plus(summ_par), Merk)
	addDir(li=li, label=title, action="dirList", dirID="ardundzdf.SenderLiveResolution", fanart=GIT_KIKALIVE, 
		thumb=img, fparams=fparams, summary=summ, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------
# 04.07.2021 Aus WDR5 KiRaKa wird MausLive - Infoseite:
#	kinder.wdr.de/radio/kiraka/mauslive-160.html 
# Aufruf: Main_KIKA	
def MausLive():
	PLog('MausLive:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	#---------------------						# Live Start: akt. Audiostream + PRG-Hinweis
	path = "https://kinder.wdr.de/radio/player/radioplayer-die-maus-100~_layout-popupVersion.html"
	page1, msg = get_page(path)	
	pos = page1.find('wdrrCurrentShowTitleTitle')
	mp3_img = MAUSHEAR
	if pos < 0:
		sendung = "Maus-Stream abspielen"
	else:
		sendung = stringextract('wdrrCurrentShowTitleTitle">', '</', page1[pos:])
		sendung = unescape(sendung)
	
	mediaObj = stringextract('mediaObj":{"url":"', '"', page1) # -> deviceids-medp.wdr.de (json)
	PLog("mediaObj: " + mediaObj)
	page2, msg = get_page(mediaObj)							
	if page2 == '':	
		msg1 = "Fehler in MausLive"
		msg2=msg
		MyDialog(msg1, msg2, '')	
		return
	PLog(len(page2))
	page2 = page2.replace('" : "', '":"')				# Formatänderung Sender
	PLog("page2: "  + page2)
	
	mp3_url = stringextract('audioURL":"', '"', page2)	# .m3u8
	if mp3_url.startswith("http") == False:
		mp3_url = "https:" + mp3_url
	PLog("mp3_url: " + mp3_url)
	
	title = u'MausLive hören: [B]%s[/B]' % sendung
	tag = u"aktuelle Sendung: [B]%s[/B]" % sendung
	summ = u'MausLive ab 19:04 Uhr live hören - Montag bis Freitag und Sonntag'
	Plot = "%s||||%s" % (tag, summ)
	mp3_url=py2_encode(mp3_url); title=py2_encode(title);
	mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
	fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
		quote(title), quote(mp3_img), quote_plus(Plot))
	addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSLIVE, thumb=mp3_img, fparams=fparams, 
		tagline=tag, mediatype='music')	
	
	#---------------------						#  Live Ende
	title = u'MausZoom - Kindernachrichten'
	tag = u"Nachrichten gehen schnell ins Ohr und sind oft schnell wieder weg. Um sie richtig zu verstehen braucht man"
	tag = "%s Zeit. Die Maus nimmt sich diese und schaut im MausZoom auf ein Thema wie eine Kamera, die sich" % tag
	tag = "%s langsam reinzoomt und immer mehr Details entdeckt." % tag
	url = "https://kinder.wdr.de/radio/diemaus/audio/maus-zoom/maus-zoom-106.podcast"
	title=py2_encode(title); url=py2_encode(url);
	fparams="&fparams={'title': '%s', 'url': '%s'}" % (quote(title), quote(url))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Maus_Audiobooks", fanart=MAUSLIVE, 
		thumb=MAUSZOOM, fparams=fparams, tagline=tag)
		
	title = u'MausLive zum Nachhören'
	tag = u"Hier kannst du die Sendungen noch mal anhören."
	url = "https://www.wdrmaus.de/hoeren/MausLive/nachhoeren.php5"
	title=py2_encode(title); url=py2_encode(url);
	fparams="&fparams={'title': '%s', 'url': '%s'}" % (quote(title), quote(url))
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Maus_MediaObjects", fanart=MAUSLIVE, 
		thumb=MAUSRELIVE, fparams=fparams, tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 05.07.2021 - Auswertung podcast-Seite (url)
# Umsetzung java-Code loadAudiobooks, z.B. in wdrmaus.de/hoeren/mauszoom.php5	
# Aufruf: MausLive	
def Maus_Audiobooks(title, url):
	PLog('Maus_Audiobooks:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(url)	
	if page == '':	
		msg1 = "Fehler in Maus_Audiobooks"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract("<item>", page)
	PLog(len(items))
	if len(items) == 0:
		msg1 = title
		msg2 = "leider keine Sendung gefunden"							
		icon = MAUSZOOM
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000, sound=True)			
		return
		
	
	for item in items:
		title = stringextract("<title>", "</title>", item)
		mp3_url = stringextract('<enclosure url="', '"', item)
		mp3_img = stringextract('href="', '"', item)			# itunes:image href="..
		if mp3_img == '':										# kann fehlen
			mp3_img = MAUSZOOM
		dur = stringextract("duration>", "</", item)
		descr = stringextract("summary>", "</", item)
		
		start = stringextract("visibleFrom>", "</", item)
		start = time_translate(start)
		start =  u"Sendedatum: [COLOR blue]%s Uhr[/COLOR]" % start
		end = stringextract("visibleUntil>", "</", item)
		end = time_translate(end)
		end = u"[B]Verfügbar bis [COLOR darkgoldenrod]%s[/COLOR][/B]" % end
		
		author = stringextract("author>", "</itunes:author>", item)
		
		title = repl_json_chars(title)
		descr = repl_json_chars(descr)
		tag = "Dauer: %s | Autor: %s | %s | %s" % (dur, author, start, end)
		
		Plot= "%s||||%s" % (tag, descr)
	
		PLog('Satz11:')		
		PLog(title);PLog(mp3_url);PLog(mp3_img);
		PLog(dur); PLog(tag);PLog(descr[:60]);
		
		mp3_url=py2_encode(mp3_url); title=py2_encode(title);
		mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(mp3_img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSZOOM, thumb=mp3_img, fparams=fparams, 
			tagline=tag, summary=descr, mediatype='music')	
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------
# 05.07.2021 - Auswertung Seite (url) mit mehreren 'mediaObj'	
# Aufruf: MausLive	
#
def Maus_MediaObjects(title, url):
	PLog('Maus_MediaObjects:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	page, msg = get_page(url)	
	if page == '':	
		msg1 = "Fehler in Maus_MediaObjects"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
	PLog(len(page))	
	
	items = blockextract('class="audioButton"', page)
	PLog(len(items))
	
	for item in items:
		mediaObj = stringextract("'url': '", "'", item) # -> ..-hoeren-104.assetjsonp (MausLive abwei.)
		PLog("mediaObj: " + mediaObj)

		page, msg = get_page(mediaObj)
		if page == '':
			continue
		mp3_url = stringextract('audioURL" : "', '"', page)	# .mp3
		PLog("mp3_url1: " + mp3_url)
		if mp3_url.startswith("http") == False:
			mp3_url = "https:" + mp3_url
		PLog("mp3_url2: " + mp3_url)

		title = stringextract('ClipTitle" : "', '"', page)
		pubDate = stringextract('AirTime" : "', '"', page)
		Plot  = "%s||||gesendet: %s" % (title, pubDate)
		tag = Plot.replace("||", "\n")
		mp3_img = MAUSRELIVE							# json- und html-Seite ohne Kontext-Bild
		
		mp3_url=py2_encode(mp3_url); title=py2_encode(title);
		mp3_img=py2_encode(mp3_img); Plot=py2_encode(Plot);
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s'}" % (quote(mp3_url), 
			quote(title), quote(mp3_img), quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio", fanart=MAUSLIVE, thumb=MAUSRELIVE, 
			fparams=fparams, tagline=tag, mediatype='music')	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)		
	
# ----------------------------------------------------------------------
# 15.05.2026 Kiraka, Kiraka_pods, Kiraka_klick, Kiraka_shows, Kiraka_get_mp3 
#	entfernt - Inhalte in anderen Menüs mit Anbindung an ARD Sounds enthalten. 
#
# ----------------------------------------------------------------------
# 26.06.2026 nach KiKA-Bereinigung nur noch genutzt von KikaninchenLieder
#
def Kikaninchen_VideoSingle(path, title, assets_url=''):	
	PLog('Kikaninchen_VideoSingle: ' + path)
	PLog(title)
	title_org=title

	#-------------------------------------------------		# 1. Assets-Url ermittlen -> xml-Datei
	if assets_url == "":
		if "_zc-" in path:									# Format vor 01.06.2023
			try:
				path = path.split("_zc-")[0]					# Bsp.: ../video52242_zc-b799b903_zs-8eedf79c.html
				assets_url = path + "-avCustom.xml"				# Bsp.: ../videos/video52242-avCustom.xml		
			except Exception as exception:
				PLog(str(exception))
				assets_url=""
		else:
			assets_url = path.replace(".html", "-avCustom.xml")		# ab 01.06.2023

	#-------------------------------------------------		# 2. Videodetails aus xml-Datei holen
	page=""
	if assets_url:
		page, msg = get_page(path=assets_url)
	if page == '':	
		msg1 = "Leider finde ich den Weg zum Video nicht."
		msg2 = "Fehler in Kikaninchen_VideoSingle."
		MyDialog(msg1, msg2, '')	
		return
	
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	title = stringextract("<headline>", "</headline>", page)
	top = stringextract("<topline>", "</topline>", page)
	summ1 = stringextract("<title>", "</title>", page)
	summ2 = stringextract("<teaserText>", "</teaserText>", page)
	dur = stringextract("<duration>", "</duration>", page)
	
	img_src = stringextract("<teaserimage>", "</teaserimage>", page)
	img = stringextract("<url>", "</url>", img_src)
	variant = stringextract("<large>", "</large>", img_src)
	if variant == "":
		variant = stringextract("<small>", "</small>", img_src)
	img = img.replace("**aspectRatio**", variant)
	img = img.replace("**width**", "1024")
	
	tag = "Dauer: %s | %s" % (dur, top)
	summ = "%s\n%s" % (summ1, summ2)
	Plot = "%s\n\n%s" % (tag, summ)
	assets = blockextract('<asset>', page)
	
	title = valid_title_chars(title)
	summ = valid_title_chars(summ)
	
	PLog("Satz1:")
	PLog(len(assets)); PLog(title); PLog(summ); PLog(img); 
	
	#-------------------------------------------------		# 3. Bau HLS_List + Stream_List, ähnl. Kika_SingleBeitrag
	# Formate siehe StreamsShow								# HLS_List + MP4_List anlegen
	#	generisch: "Label |  Bandbreite | Auflösung | Titel#Url"
	#	fehlende Bandbreiten + Auflösungen werden ergänzt
	asset=""
	for asset in assets:
		if "Web XL|" in asset:								# größte HLS-Quelle verwenden, Altern.: "MP4 Web L"
			break
		
	url_m3u8 = stringextract('<csmilHlsStreamingRedirectorUrl>', '</', asset)
	if url_m3u8 == "":
		url_m3u8 = stringextract('<adaptiveHttpStreamingRedirectorUrl>', '</', asset)
	PLog("url_m3u8: " + url_m3u8)
	# sub_path = stringextract('"webvttUrl":"', '"', page)	# Altern.: subtitle-Url tt:style, fehlen hier
	sub_path=""; geoblock=''; descr='';	
	href = url_m3u8
	HBBTV_List=''											# nur ZDF
	HLS_List=[]; Stream_List=[];
	
	#'''
	quality = u'automatisch'
	HLS_List.append('HLS automatische Anpassung ** auto ** auto ** %s#%s' % (title,url_m3u8))
	Stream_List = ardundzdf.Parseplaylist(li, href, img, geoblock, descr, stitle=title, buttons=False)
	if type(Stream_List) == list:					# Fehler Parseplaylist = string
		HLS_List = HLS_List + Stream_List
	else:
		HLS_List=[]
	#'''
		
	PLog("HLS_List: inputstream.adaptive returned bad status Permanent failure..")
	PLog("HLS_List: " + str(HLS_List)[:80])
	MP4_List = Kika_VideoMP4getXML(title, assets)
	PLog("download_list: " + str(MP4_List)[:80])
	Dict("store", 'KIKA_HLS_List', HLS_List) 
	Dict("store", 'KIKA_MP4_List', MP4_List) 
	
	if not len(HLS_List) and not len(MP4_List):
		msg1 = "Leider finde ich keine Videodaten."
		msg2 = "Fehler in Kikaninchen_VideoSingle."
		MyDialog(msg1, msg2, '')	
		return li

	#----------------------------------------------- 
	# Nutzung build_Streamlists_buttons (Haupt-PRG), einschl. Sofortstart
	# 
	thumb = img; ID = 'KIKA'; HOME_ID = "Kinderprogramme"
	PLog('childs_Lists_ready: ID=%s, HOME_ID=%s' % (ID, HOME_ID));
	Plot = "Titel: %s\n\n%s" % (title_org, summ)				# -> build_Streamlists_buttons
	Plot = Plot.replace("\n", "||")
	PLog('Plot: ' + Plot)
	ardundzdf.build_Streamlists_buttons(li,title_org,thumb,geoblock,Plot,sub_path,\
		HLS_List,MP4_List,HBBTV_List,ID,HOME_ID)	
		
	if SETTINGS.getSetting('pref_video_direct') == 'true': 		# Verbleib in Liste	
		return	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
# ----------------------------------------------------------------------			
# bei Wegfall der json-Quelle Umstellung auf Lieder der Schnipselwelt
#
def KikaninchenLieder():	
	PLog('KikaninchenLieder:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	path = 'https://www.kikaninchen.de/kikaninchen/lieder/liederkikaninchen100.json'	
	page, msg = get_page(path)	
	if page == '':	
		msg1 = "Fehler in KikaninchenLieder:"
		msg2 = msg
		MyDialog(msg1, msg2, '')	
		return li
			
	records = page.split('documentCanvasId')
	PLog(len(records))						
	
	mediatype='' 		
	if SETTINGS.getSetting('pref_video_direct') == 'true': # Kennz. Video für Sofortstart 
		mediatype='video'
	for rec in records:
		href = stringextract('avCustomUrl":"', '"', rec)
		if href == '':
			continue					
		img_src = stringextract('urlScheme":"', '**imageVariant**', rec)
		PLog(img_src)
		if img_src.startswith('http') == False:
			img_src = 'http://www.kikaninchen.de' + img_src
		img_src = img_src + 'ident.jpg'						# ident = 800x800
		title = stringextract('title":"', '"', rec)
		altText =  stringextract('altText":"', '"', rec)
		titleText =  stringextract('titleText":"', '"', rec)
		
		title = repl_json_chars(title)
		altText = unescape(altText)	
		altText = repl_json_chars(altText)	
		titleText = unescape(titleText)	
		titleText = repl_json_chars(titleText)	
		
		summ = ''
		if altText:
			summ = altText
		if summ == '':
			summ = titleText
										
		PLog(href); PLog(title); PLog(img_src); PLog(summ)
		href=py2_encode(href); title=py2_encode(title)
		fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(href), quote(title))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Kikaninchen_VideoSingle", fanart=img_src, 
			thumb=img_src, fparams=fparams, tagline=summ, mediatype=mediatype)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# 02.02.2026 frühere Tonschnipsel nicht mehr in der Mediathek verfügbar
#	Austausch gegen Schnipselwelt, Aufruf in Kikaninchen_Menu

# ######################################################################
# ----------------------------------------------------------------------			
#								tivi
# ----------------------------------------------------------------------
# 07.06.2026 Tivi_Search entfernt. Bei Bedarf umsetzen via Graphql 
#	(Test OK).			
# def Tivi_Search(query=None, title='Search', pagenr=''):
#
# ----------------------------------------------------------------------
# 29.01.2026 tivi_Verpasst entfernt - beim ZDF nicht mehr verfügbar
# def tivi_Verpasst(title, zdfDate, sfilter=""):

# ----------------------------------------------------------------------
# Auflistung 0-9 (1 Eintrag), A-Z (einzeln) 			
def Tivi_AZ():
	PLog('Tivi_AZ:')
	li = xbmcgui.ListItem()
	li = home(li, ID='Kinderprogramme')			# Home-Button
	
	azlist = list(string.ascii_uppercase)
	azlist.append('0 - 9')						# ZDF-Vorgabe (vormals '0+-+9')

	for element in azlist:	
		button = element
		if button == "0 - 9":
			button = "0-9"						# Anpas. img-Name
		title = "Sendungen mit " + element
		img_src = "https://github.com/rols1/PluginPictures/blob/master/ARDundZDF/KIKA_tivi/Buchstabe_%s.png?raw=true" % button
		
		PLog(button); PLog(img_src)
		button=py2_encode(button); title=py2_encode(title);		
		fparams="&fparams={'name': '%s', 'img': '%s', 'element': '%s'}" % (quote(title), quote(img_src), button)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.childs.Tivi_AZ_Sendungen", fanart=R(ICON_DIR_FOLDER), 
			thumb=img_src, fparams=fparams, tagline=title)
 
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

# ----------------------------------------------------------------------			
# Alle Sendungen, char steuert Auswahl 0-9, A-Z
# 12.12.2019 Nutzung ZDF_get_content statt get_tivi_details
# 26.04.2023 Umstellung www.zdf.de -> zdf-cdn -> futura
# 08.06.2026 Umstellung auf Graphql -> ardundzdf.ZDF_AZList
#
def Tivi_AZ_Sendungen(name, img, element=None):	
	PLog('Tivi_AZ_Sendungen:'); PLog(element)
	if "0-9" in element:
		element = "0 - 9"
	
	title=name; ID="Kinderprogramme"
	li = xbmcgui.ListItem()				# Home-Button in ZDF_AZList
	ardundzdf.ZDF_AZList(title, element, ID)
	
	return

# ----------------------------------------------------------------------			












