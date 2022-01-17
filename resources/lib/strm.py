# -*- coding: utf-8 -*-
################################################################################
#				strm.py - Teil von Kodi-Addon-ARDundZDF
#			 Erzeugung von strm-Dateien für Kodi's Medienverwaltung
################################################################################
# 	<nr>2</nr>										# Numerierung für Einzelupdate
#	Stand: 17.01.2022
#

from __future__ import absolute_import

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys 
import re				
import json	
	
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus
	from urlparse import parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, parse_qs
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

from resources.lib.util import *

HANDLE			= int(sys.argv[1])
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
STRMSTORE 		= os.path.join(ADDON_DATA, "strm") 						# Default-Verz. strm
FLAG_OnlyUrl	= os.path.join(ADDON_DATA, "onlyurl")					# Flag PlayVideo_Direct	-> strm-Modul

ICON 			= 'icon.png'		# ARD + ZDF
ICON_DIR_STRM	= "Dir-strm.png"
PLog('Script strm.py geladen')

# Basis Template, für Ausbau siehe
# 	https://kodi.wiki/view/NFO_files/Templates
# 	nicht genutzt: "Album|album"
STRM_TYPES		= ["Film|movie", "TV-Show|tvshow", "Episode|episodedetails",  
					"Musik-Video|musicvideo" 
				] 
NFO1 = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
NFO2 = '<movie>\n<title>%s</title>\n<uniqueid type="tmdb" default="true"></uniqueid>\n'
NFO3 = '<thumb spoof="" cache="" aspect="poster">%s</thumb>\n'
NFO4 = '<plot>%s</plot>\n</movie>'
NFO = NFO1+NFO2+NFO3+NFO4													# nfo-Template

######################################################################## 			
def unpack(add_url):
	PLog("unpack:")
	add_url = unquote_plus(add_url)
	PLog(add_url[:100])
	
	dirID 	= stringextract('dirID=', '&', add_url)
	fanart 	= stringextract('fanart=', '&', add_url)
	thumb	= stringextract('thumb=', '&', add_url)
	fparams = add_url.split('fparams')[-1]
	fparams = unquote_plus(fparams)
	fparams	= fparams[1:]					# ={'url':..
	
	PLog("unpack_done")
	PLog("dirID: %s\n fanart: %s\n thumb: %s\n fparams:%s" % (dirID, fanart, thumb, fparams))
	return dirID, fanart, thumb, fparams

# ----------------------------------------------------------------------
# Aufruf Kontextmenü, abhängig von SETTINGS.getSetting('pref_strm')
# 	Param. siehe addDir, mediatype == "video"
def do_create(label, add_url):
	PLog("do_create: " + label)
	PLog(SETTINGS.getSetting('pref_strm_uz'))
	PLog(SETTINGS.getSetting('pref_strm_path'))
	icon = R(ICON_DIR_STRM)

	dirID, fanart, thumb_org, fparams = unpack(add_url)				# Params Kontextmenü auspacken
	if get_Source_Funcs_ID(add_url) == '':							# Zielfunktion unterstützt?
		msg1 = u'nicht unterstützt'
		msg2 = u'Videoquelle nicht für strm geeignet'
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=True)
		return	
			
	strm_type = get_strm_types()									# Genre-Auswahl
	if strm_type == '':
		return
	#------------------------------									# Abfrage Zielverz. != Filme/Serien
	strmpath = STRMSTORE											# Default
	choose_path = False
	if strm_type == "movie":
		verz = SETTINGS.getSetting('pref_strm_film_path')
		if verz != '' and verz != None:	
			strmpath = verz
			choose_path = False
	else:
		verz = SETTINGS.getSetting('pref_strm_series_path')
		if verz != '' and verz != None:	
			heading = u"Ablage festlegen/ändern: %s" % verz
			newdir = DirectoryNavigator(settingKey='',mytype=0, heading=verz, shares='files', path=verz)
			PLog("newdir: " + str(newdir))
			strmpath = newdir										# Abbruch-Behandl. entf., bei Titelwahl möglich
		else:
			strmpath = STRMSTORE									# strm-Verzeichnis in userdata
			if os.path.isdir(strmpath) == False:
				try:
					os.mkdir(strmpath)
				except Exception as exception:
					PLog(str(exception))
					msg1 = u'strm-Verzeichnis konnte nicht angelegt werden:'
					msg2 = str(exception)
					MyDialog(msg1, msg2, '')
					return

	if strmpath == STRMSTORE:			
		msg1 = u'Die Ablage erfolgt im Datenverzeichnis des Addons, Unterverzeichnis: strm'
		msg2 = u'Ein anderes Verzeichnis kann in den Settings festgelegt werden.'
		MyDialog(msg1, msg2, '')
	PLog("strmpath: " + strmpath)		
		
	#------------------------------							
	title	= stringextract("title': '", "'", fparams) 				# fparams json-Format
	url	= stringextract("url': '", "'", fparams) 
	thumb	= stringextract("thumb': '", "'", fparams) 
	Plot	= get_Plot(fparams)
		
	if title == '' or "| auto" in title or u"| Auflösung" in title:	# Anwahl Streaming-/MP4-Formate
		if Plot.startswith("Title: "):
			title = Plot
		else:
			title = label
	if thumb == '':
		thumb = thumb_org	
	PLog("title: %s\n thumb: %s\n url: %s\n Plot:%s" % (title, thumb, url, Plot))
	
	formats = [".m3u8", "mp4", ".mp3", ".webm"]						# Url-Test
	my_ext = url.split(".")[-1]
	url_test = False
	for f in formats:
		if f in my_ext:
			url_test = True
	if url_test == False:
		msg1 = u'ermittle Streamurl'
		msg2 = title
		xbmcgui.Dialog().notification(msg1,msg2,icon,1000,sound=False)
					
		url = get_streamurl(add_url)								# Streamurl ermitteln
		if url == '':												# Url fehlt/falsch: Abbruch	
			msg1 = u"die erforderliche Stream-Url fehlt für"
			msg2 = title									
			MyDialog(msg1, msg2, "Abbruch")
			return

	fname = make_filenames(title)
	PLog("fname: " + fname)
	
	#------------------------------									# Abfrage Dateiname
	new_name = get_keyboard_input(line=fname, head="Dateiname übernehmen / eingeben")
	PLog("new_name: " + new_name)
	if new_name.strip() == '':
		return
	#------------------------------									# strm-, nfo-, jpeg-Dateien anlegen
	ret = xbmcvfs_store(strmpath, url, thumb, fname, title, Plot, strm_type)
	msg1 = u'STRM-Datei angelegt'
	if ret ==  False:
		msg1 = u'STRM-Datei fehlgeschlagen'
	msg2 = title
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000)
									
	return
# ----------------------------------------------------------------------
def get_strm_types():
	PLog("get_strm_types:")
	strm_type=''
	
	head = u"bitte Genre auswählen"
		
	ret = xbmcgui.Dialog().select(head, STRM_TYPES)
	if ret == None or ret == -1:							
		return strm_type
	PLog("ret: %d" % ret)
	strm_type = STRM_TYPES[ret]							# "Film|movie"
	strm_type = strm_type.split('|')[-1]
	PLog("strm_type: " + strm_type)
	
	return strm_type

# ----------------------------------------------------------------------
def get_Plot(fparams):
	PLog("get_Plot:")
	Plot=''

	Plot	= stringextract("Plot': '", "'", fparams)
	if Plot == '':													# Plot + Altern.
		 Plot = stringextract("summary': '", "'", fparams)
	if Plot == '':
		 Plot = stringextract("summ': '", "'", fparams)
	 
	if "'dauer'" in fparams:
		dauer = stringextract("dauer': '", "'", fparams)
		Plot = "%s\n\n%s" % (dauer, Plot)

	return Plot
# ----------------------------------------------------------------------
#
# strm-, nfo-, jpeg-Dateien anlegen
# 	strmpath=strm-Verzeichnis, fname=Dateiname ohne ext.
# 	url=Video-Url, thumb=thumb-Url
def xbmcvfs_store(strmpath, url, thumb, fname, title, Plot, strm_type):
	PLog("xbmcvfs_store:")
	PLog("strmpath: " + strmpath)
	
	if SETTINGS.getSetting('pref_strm_uz') == "true":	# Für jede strm-Datei ein Unterverzeichnis
		strmpath = os.path.join(strmpath, fname)	# STRMSTORE + fname
		if os.path.isdir(strmpath) == False:		# Verz. erzeugen, falls noch nicht vorh.
			os.mkdir(strmpath)
	
	if thumb:
		xbmcvfs_icon = os.path.join(strmpath, "%s.jpeg" % fname)
		PLog("xbmcvfs_icon: " + xbmcvfs_icon)
		urlretrieve(thumb, xbmcvfs_icon)

	xbmcvfs_fname = os.path.join(strmpath, "%s.strm" % fname)
	PLog("xbmcvfs_fname: " + xbmcvfs_fname)
	f = xbmcvfs.File(xbmcvfs_fname, 'w')							
	if PYTHON2:
		ret1=f.write(url); f.close()			
	else:												# Python3: Bytearray
		buf = bytearray()
		buf.extend(url.encode())
		ret1=f.write(buf); f.close()			
	PLog("strm_ret: " + str(ret1))										
	
	xbmcvfs_fname = os.path.join(strmpath, "%s.nfo" % fname)
	PLog("xbmcvfs_fname: " + xbmcvfs_fname)
	
	PLog("strm_type: " + strm_type)
	nfo = NFO.replace("<movie>", "<%s>" % strm_type); 	# Anpassung Template
	nfo = nfo.replace("</movie>", "</%s>" % strm_type)
	
	nfo = nfo % (title, thumb, Plot)
	f = xbmcvfs.File(xbmcvfs_fname, 'w')							
	if PYTHON2:
		ret2=f.write(nfo); f.close()			
	else:												# Python3: Bytearray
		buf = bytearray()
		buf.extend(nfo.encode())
		ret2=f.write(buf); f.close()			
	PLog("nfo_ret: " + str(ret2))
	
	if ret1 == False or ret2 == False:
			msg1 = u"Erzeugung strm-Datei oder nfo-Datei fehlgeschlagen."
			msg2 = u"Bitte überprüfen"									
			MyDialog(msg1, msg2, "Abbruch")
			return False

	return True

# ----------------------------------------------------------------------
#
# plugin-Script add_url ausführen -> HLS_List, MP4_List bauen,
# HLS_List, MP4_List durch PlayVideo_Direct auwerten lassen, Flag +
# 	Param-Austausch via Dict
#
def get_streamurl(add_url):
	PLog("get_streamurl:")
	streamurl=''; ID=''
		
	ID = get_Source_Funcs_ID(add_url)
	if ID == '':
		return ''
	params = add_url.split("%s/" % ADDON_ID)[-1]		# ADDON_ID von Params trennen

	MY_SCRIPT=xbmc.translatePath('special://home/addons/%s/ardundzdf.py' % ADDON_ID) 
	xbmc.executebuiltin('RunScript(%s, %s, %s)'  % (MY_SCRIPT, HANDLE, params)) # Hinw.: blocking call o. Wirkung
			
	PLog("ID: " + ID)
	HLS_List =  Dict("load", "%s_HLS_List" % ID)
	PLog("HLS_List: " + str(HLS_List[:100]))
	MP4_List =  Dict("load", "%s_MP4_List" % ID)
	PLog("MP4_List: " + str(MP4_List[:100]))
	
	# todo: Dateiflag urlonly setzen/löschen - Übergabe via script unsicher
	#	ev. auch Rückgabe via Datei
	
														# Url entspr. Settings holen:
	title_org=''; img=''; Plot='';						# hier nicht benötigt 
	
	open(FLAG_OnlyUrl, 'w').close()						# Flag PlayVideo_Direct	-> strm-Modul		
	streamurl = PlayVideo_Direct(HLS_List, MP4_List, title_org, img, Plot)
	PLog("streamurl: " + streamurl)	
	return streamurl
	
# ----------------------------------------------------------------------
#
# Test auf unterstützte Zielfunktion 
#
def get_Source_Funcs_ID(add_url):
	PLog("get_Source_Funcs_ID:")	
	
	PLog(unquote_plus(add_url[:100]))
	
	# nachrüsten (abweichende Streamermittlung): funk, arte, 
	#	phoenix (einsch. Youtube-Videos), TagesschauXL, zdfmobile
	#u"funk.ShowVideo|", u"|KIKA", u"|", u"|",
	Source_Funcs = [u"dirID=ZDF|ZDF", u"ARDnew.ARDStartSingle|ARDNEU",	# Funktionen + ID's
					u"my3Sat.SingleBeitrag|3sat",
					]
	ID=''												# derzeit nicht ermittelbar
	for item in Source_Funcs:
		dest_func, sid = item.split("|")
		PLog(dest_func); PLog(sid)
		if 	dest_func in add_url:
			ID = sid
			break
	PLog("ID: " + ID)	
	return ID	
	
######################################################################## 			
