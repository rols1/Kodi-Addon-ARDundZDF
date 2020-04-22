# -*- coding: utf-8 -*-
################################################################################
#				merkliste.py - Teil von Kodi-Addon-ARDundZDF
#			 Hinzufügen + Löschen von Einträgen der Merkliste
#	aus Haupt-PRG hierher verlagert, da sonst kein Verbleib im akt. Listing
#	möglich.
#	Listing der Einträge weiter in ShowFavs (Haupt-PRG)
################################################################################
#	Stand: 21.04.2020

from __future__ import absolute_import

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import base64 			# url-Kodierung für Kontextmenüs
import os, sys, subprocess 
import re				
import json		
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus
	from urlparse import parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, parse_qs

from util import PLog, stringextract, ReadFavourites, RSave, R, check_AddonXml,\
					MyDialog, RLoad, blockextract


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

if 	check_AddonXml('"xbmc.python" version="3.0.0"'):
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join("%s/merkliste.xml") % ADDON_DATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
# Marker: ShowFavs(Merkliste) ist aktiv, gesetzt in ShowFavs, 
#	gelöscht bei jedem Start des Haupt-PRG's
MERKACTIVE 		= os.path.join(DICTSTORE, 'MerkActive') 
MERKFILTER 		= os.path.join(DICTSTORE, 'Merkfilter') 

ICON 			= 'icon.png'		# ARD + ZDF
ICON_DIR_WATCH	= "Dir-watch.png"
PLog('Script merkliste.py geladen')

# Basis-Ordner-Liste (wird in Merkliste eingefügt, falls noch ohne Ordnerliste,
#	einschl. ORDNER_INFO - Quelle ZDF-Rubriken +Audio+Talk):
ORDNER			= ["Audio", "Bilderserien", "Comedy/Show", "Doku/Wissen", "Filme", "Geschichte", 
					"Nachrichten", "Kinder/ZDFtivi", "Krimi", "Kultur",  
					"Politik/Gesellschaft", "Serien", "Sport",  "Talk", "Verbraucher"]
ORDNER_INFO		= [u"# die folgende Ordnerliste kann mit einem Editor geändert werden.",
					u'Nutzung: in Settings "Ordner für Merkliste verwenden wählen."',
					u"# Regeln:", 
					u"# Sie darf keine Kommentarzeichen (#) enthalten.", 
					u"# Die einzelnen Begriffe sind mit einem Leerzeichen zu trennen.", 
					u'# Für zusammengesetzte Begriffe ist das "&"- oder "/"-Zeichen zu verwenden', 
					u"# Zeilenumbrüche sind beim Eingeben möglich - sie werden vom Addon wieder entfernt"] 

# CallFunctions: Funktionen, die Videos direkt oder indirekt (isPlayable) aufrufen.
#	Ist eine der Funktionen in der Plugin-Url enthalten, wird der Parameter Merk='true'
#	für PlayVideo bzw. zum Durchreichen angehängt.
#	Funktioniert nicht mit Modul funk
CallFunctions = ["PlayVideo", "ZDF_getVideoSources", "resources.lib.zdfmobile.ShowVideo",
					"resources.lib.zdfmobile.PlayVideo", "SingleSendung", "ARDStartVideoStreams", 
					"ARDStartVideoMP4", "SenderLiveResolution", "resources.lib.phoenix.SingleBeitrag"
				]
# ----------------------------------------------------------------------
# 02.04.2020 erweitert für Share-Zugriffe - hier Schreiben via 
#	xbmcvfs.File (für Python3 mittels Bytearray).
#	Lesen der Merkliste in ReadFavourites (Modul util).
#			
def Watch_items(action, name, thumb='', Plot='', url=''):		
	PLog('Watch: ' + action)
	
	url = unquote_plus(url)	
	PLog(unquote_plus(url)[100:])  			# url in fparams zusätzlich quotiert
	PLog(name); PLog(thumb); PLog(Plot);
	
	item_cnt = 0; 
	err_msg	= ''
	doppler = False

	fname = WATCHFILE		
	if SETTINGS.getSetting('pref_merkextern') == 'true':	# externe Merkliste gewählt?
		fname = SETTINGS.getSetting('pref_MerkDest_path')
		if fname == '' or xbmcvfs.exists(fname) == False:
			PLog("merkextern: %s, %d" % (fname, xbmcvfs.exists(fname)))
			msg1 = u"Merkliste nicht gefunden"
			err_msg = u"Bitte Settings überprüfen"
			return msg1, err_msg, str(item_cnt)	
	#------------------
	if action == 'add':
		url = get_plugin_url(url)									# url aus ev. Base64-Kodierung
		my_items, my_ordner = ReadFavourites('Merk')				# 'utf-8'-Decoding in ReadFavourites			
		merkliste = ''
		if len(my_items):
			PLog('my_items: ' + my_items[0])			# 1. Eintrag
			for item in my_items:						# Liste -> String
				iname = stringextract('name="', '"', item) 
				PLog('Name: %s, IName: %s' % (py2_decode(name), py2_decode(iname)))
				if py2_decode(iname) == py2_decode(name):# Doppler vermeiden
					doppler = True
					PLog('Doppler')
					break
				merkliste = merkliste + item + "\n"
				item_cnt = item_cnt + 1
		else:	
			pass
		
		ordner=''
		if SETTINGS.getSetting('pref_merkordner') == 'true':		# Ordner-Auswahl
			if doppler == False:
				oldordner = stringextract('ordner="', '"', item) 
				if len(my_ordner) == 0:								# leer: Initialisierung
					my_ordner = ORDNER
				my_ordner=sorted(my_ordner, key=str.lower)
				ret = xbmcgui.Dialog().select(u'Ordner wählen', my_ordner, preselect=0)
				if ret >= 0:
					ordner = my_ordner[ret]
				else:
					ordner = oldordner
				PLog("ordner: " + ordner)
		
		# Neuer Eintrag:		
		url = url.replace('&', '&amp;') 							# Anpassung an Favorit-Schema
		merk = '<merk name="%s" ordner="%s" thumb="%s" Plot="%s">ActivateWindow(10025,&quot;%s&quot;,return)</merk>'  \
			% (name, ordner, thumb, Plot, url)
		PLog('merk: ' + merk)
				
		item_cnt = item_cnt + 1		
		if doppler == False:
			msg1 = u"Eintrag hinzugefügt" 
			PLog(type(merkliste)); PLog(type(merk));
			merkliste = py2_decode(merkliste) + merk + "\n"
			#item_cnt = item_cnt + 1
			
			# Merkliste + Ordnerinfo + Ordner + Ordnerwahl:	
			my_ordner = " ".join(my_ordner)
			if my_ordner == '':
				my_ordner = ORDNER
			ordner_info = "\n".join(ORDNER_INFO)	
			merkliste = "<merkliste>\n%s</merkliste>\n\n%s\n\n<ordnerliste>%s</ordnerliste>\n"	%\
				(merkliste, ordner_info, my_ordner)		
			try:
				if '//' not in fname:
					err_msg = RSave(fname, merkliste, withcodec=True)	# Merkliste speichern
				else:
					PLog("xbmcvfs_fname: " + fname)
					f = xbmcvfs.File(fname, 'w')						# extern - Share		
					if PYTHON2:
						f = xbmcvfs.File(fname, 'w')
						ret=f.write(merkliste); f.close()			
					else:												# Python3: Bytearray
						buf = bytearray()
						buf.extend(merkliste.encode())
						ret=f.write(buf); f.close()			
					PLog("xbmcvfs_ret: " + str(ret))
					if ret:
						sync_list_intern(src_file=fname, dest_file=WATCHFILE)# Synchronisation
			except Exception as exception:
				PLog(str(exception))
				msg1 = u"Problem Merkliste"
				err_msg = str(exception)
				return msg1, err_msg, str(item_cnt)		
		else:
			msg1 = u"Eintrag schon vorhanden"
			
	#------------------
	if action == 'del':
		my_items, my_ordner = ReadFavourites('Merk')					# 'utf-8'-Decoding in ReadFavourites
		if len(my_items):
			PLog('my_items: ' + my_items[-1])
		merkliste = ''
		deleted = False
		for item in my_items:						# Liste -> String
			iname = stringextract('name="', '"', item) # unicode
			iname = py2_decode(iname)
			name = py2_decode(name)		
			PLog('Name: %s, IName: %s' % (name, iname))		
			if name == iname:
				deleted = True						# skip Satz = löschen 
				continue
			item_cnt = item_cnt + 1
			merkliste = py2_decode(merkliste) + py2_decode(item) + "\n"
			
		if deleted:
			# Merkliste + Ordnerinfo + Ordner + Ordnerwahl:	
			my_ordner = " ".join(my_ordner)
			if my_ordner == '':
				my_ordner = ORDNER
			ordner_info = "\n".join(ORDNER_INFO)	
			merkliste = "<merkliste>\n%s</merkliste>\n\n%s\n\n<ordnerliste>%s</ordnerliste>\n"	%\
				(merkliste, ordner_info, my_ordner)		
			try:
				msg1 = u"Eintrag gelöscht"
				if '//' not in fname:
					err_msg = RSave(fname, merkliste, withcodec=True)	# Merkliste speichern
					PLog(msg1)
					if err_msg:
						ret = False
					else:
						ret = True
				else:
					PLog("xbmcvfs_fname: " + fname)
					f = xbmcvfs.File(fname, 'w')						# extern - Share		
					ret = f.write(merkliste); f.close()			
					PLog("xbmcvfs_ret: " + str(ret))
				if ret:
					sync_list_intern(src_file=fname, dest_file=WATCHFILE)# Synchronisation

			except Exception as exception:
				PLog(str(exception))
				msg1 = u"Problem Merkliste"
				err_msg = str(exception)
				return msg1, err_msg, str(item_cnt)	
		else:
			msg1 = "Eintrag nicht gefunden." 
			err_msg = u"Merkliste unverändert."
			PLog(msg1)	
							
	#------------------
	if action == 'folder':												# Ordner wählen / ändern
		my_items, my_ordner = ReadFavourites('Merk')					# 'utf-8'-Decoding in ReadFavourites
		merkliste = ''
		ret = True
		for item in my_items:						# Liste -> String
			iname = stringextract('name="', '"', item) # unicode
			iname = py2_decode(iname); name = py2_decode(name)		
			PLog('Name: %s, IName: %s' % (name, iname))		
			if name == iname:
				if SETTINGS.getSetting('pref_merkordner') == 'true':	# Ordner-Auswahl
					oldordner = stringextract('ordner="', '"', item) 
					if len(my_ordner) == 0:								# leer: Initialisierung
						my_ordner = ORDNER
					my_ordner=sorted(my_ordner, key=str.lower)
					ret = xbmcgui.Dialog().select(u'Ordner wählen', my_ordner, preselect=0)
					ordner=oldordner									# Fallback: vorh. Ordner
					if ret >= 0:
						ordner = my_ordner[ret]
					PLog("ordner: " + ordner)
					
					if ordner != oldordner:
						# Ordner im Eintrag aktualisieren:
						PLog("url: " + url)
						url = get_plugin_url(url)						# url aus ev. Base64-Kodierung		
						PLog("url: " + url)
						url = url.replace('&', '&amp;') 				# Anpassung an Favorit-Schema
						merk = '<merk name="%s" ordner="%s" thumb="%s" Plot="%s">ActivateWindow(10025,&quot;%s&quot;,return)</merk>'  \
							% (name, ordner, thumb, Plot, url)
						PLog('merk: ' + merk)
						item = merk		
				
			item_cnt = item_cnt + 1
			merkliste = py2_decode(merkliste) + py2_decode(item) + "\n"
		
		if ordner != oldordner:
			ret, err_msg = save_merkliste(fname, merkliste, my_ordner)
		if ret:															# Merkliste gespeichert
			if ordner == oldordner:
				msg1 = u"Ordner unverändert" 
			else:
				msg1 = u"Ordner geändert" 
			err_msg = u"gewählter Ordner: %s" % ordner
		else:															# Problem beim Speichern
			msg1 = "Problem Merkliste"									# err_msg s. save_merkliste
	
	return msg1, err_msg, str(item_cnt)	

# ----------------------------------------------------------------------
# url aus ev. Base64-Kodierung ermitteln
# url = Param. Watch_items
def get_plugin_url(url):
	PLog("get_plugin_url:")
		
	# Base64-Kodierung wird nicht mehr verwendet (addDir in Modul util), Code verbleibt 
	#	hier bis auf Weiteres
	if 'plugin://plugin' not in url:				# Base64-kodierte Plugin-Url in ActivateWindow
		b64_clean= convBase64(url)					# Dekodierung mit oder ohne padding am Ende	
		b64_clean=unquote_plus(b64_clean)			# unquote aus addDir-Call
		b64_clean=unquote_plus(b64_clean)			# unquote aus Kontextmenü
		#PLog(b64_clean)
		CallFunction = stringextract("&dirID=", "&", b64_clean) 
		PLog('CallFunction: ' + CallFunction)
		if CallFunction in CallFunctions:			# Parameter Merk='true' anhängen
			new_url = b64_clean[:-1]				# cut } am Ende fparams
			new_url = "%s, 'Merk': 'true'}" % new_url
			PLog("CallFunction_new_url: " + new_url)
			url = quote_plus(new_url)
			url = base64.b64encode(url)			
	return url
# -------------------------
# aus Haupt-PRG, hier nicht importierbar
def convBase64(s):
	PLog('convBase64:')
	PLog(s[:80])
	try:
		if len(s.strip()) % 4 == 0:
			if PYTHON2:					
				s = base64.decodestring(s)
			else:
				s =  base64.b64decode(s)
				s = s.decode("utf-8") 
			return unquote_plus(s)		
	except Exception as exception:
		PLog(str(exception))
	return False
	
# ----------------------------------------------------------------------
# synchronisiert die interne Merkliste durch Überschreiben mit der
#	der externen Merkliste - Abbruch bei Abwahl von Synchronisieren 
#	oder externer Merkliste.
# ohne Rückgabe, nur Log
#
def sync_list_intern(src_file, dest_file):
	PLog('sync_list_intern:')
	
	# Vorprüfung Setting Sync / externe Merkliste
	if SETTINGS.getSetting('pref_merksync') == 'false' or SETTINGS.getSetting('pref_merkextern') == 'false':	
		PLog("Sync_OFF")
		return
	
	f = xbmcvfs.File(src_file)
	s1 = f.size(); f.close()
	if s1 > 100:							# Mindestbreite bis dirID=, Eintrag immer größer
		ret1 = xbmcvfs.delete(dest_file)
		PLog('xbmcvfs.delete: ' + str(ret1))
		ret2 = xbmcvfs.copy(src_file, dest_file)
		PLog('xbmcvfs.copy: ' + str(ret2))
		f = xbmcvfs.File(dest_file)
		s2 = f.size(); f.close()			# Größenvergleich
		PLog("s1: %d, s2: %d" % (s1, s2))
	
	if ret1 and ret2 and s2 == s1:			# ohne Rückgabe
		PLog("Sync_OK")
	else:
		PLog("Sync_Error")
	return
	
# ----------------------------------------------------------------------
# Speichert die Merkliste, zusammen mit Ordnerinfo + Ordner 
#	ordner: mit ReadFavourites eingelesene Ordner
#
def save_merkliste(fname, merkliste, my_ordner):
	PLog('save_merkliste:')
	
	# Merkliste + Ordnerinfo + Ordner:	
	err_msg = ''												# gefüllt von Aufrufer 
	my_ordner = " ".join(my_ordner)
	if my_ordner == '':
		my_ordner = ORDNER
	ordner_info = "\n".join(ORDNER_INFO)	
	merkliste = "<merkliste>\n%s</merkliste>\n\n%s\n\n<ordnerliste>%s</ordnerliste>\n"	%\
		(merkliste, ordner_info, my_ordner)		
	try:
		if '//' not in fname:
			err_msg = RSave(fname, merkliste, withcodec=True)	# Merkliste speichern
			if err_msg:
				ret = False
			else:
				ret = True
		else:
			PLog("xbmcvfs_fname: " + fname)
			f = xbmcvfs.File(fname, 'w')						# extern - Share		
			ret = f.write(merkliste); f.close()			
			PLog("xbmcvfs_ret: " + str(ret))
		if ret:
			sync_list_intern(src_file=fname, dest_file=WATCHFILE)# Synchronisation
		return ret, err_msg
		
	except Exception as exception:
		ret = False
		PLog(str(exception))
		err_msg = str(exception)
		return ret, err_msg	
	
# ----------------------------------------------------------------------			
# Aufruf Merkliste mit Ordner als Filter
#	Merkliste bleibt unverändert
#	Filter wird in MERKFILTER dauerhaft gespeichert
#			
def watch_filter():
	PLog("watch_filter:")
	my_items, my_ordner = ReadFavourites('Merk')	# Ordnerliste holen	
	my_ordner=sorted(my_ordner, key=str.lower)
	my_ordner.insert(0, u"*ohne Zuordnung*")
	
	preselect = 0									# Vorauswahl
	if os.path.exists(MERKFILTER) == True:	
		myfilter = RLoad(MERKFILTER,abs_path=True)
		PLog('myfilter: ' + myfilter)
		if myfilter:								# leer möglich
			preselect = my_ordner.index(myfilter)
	
	ret = xbmcgui.Dialog().select(u'Ordner wählen (Abbrechen = ohne Filter)', my_ordner, preselect=preselect)
	ordner=''
	if ret >= 0:
		ordner = my_ordner[ret]
	PLog("ordner: " + ordner)
	
	# RunScript + RunPlugin hier fehlgeschlagen, daher 
	#	Filterung via Triggerdatei MERKFILTER 
	err_msg = RSave(MERKFILTER, ordner, withcodec=True)
	xbmc.executebuiltin('Container.Refresh')

# ----------------------------------------------------------------------
# Markierungen "Ordner:" + "Modul:" aus akt. Anzeige entfernen
#	die Markierungen gehören nicht zum Datensatz des Eintrags
# 			
def clean_Plot(Plot):
	PLog("clean_Plot:")
	# PLog(Plot)	# Debug
	if '[COLOR' in Plot:				# Mark. immer farbig
		items = blockextract('[B]', Plot, '[/B]')
		for item in items:
			if 'Ordner: ' in item or 'Modul: ' in item:
				Plot = Plot.replace(item, '')
				
	Plot = Plot.replace('||||||||', '')	# LF-Ruinen entfernen (4 Zeilen-Mark.)		
	Plot = Plot.replace('||||||', '')	# LF-Ruinen entfernen (3 Zeilen-Mark.)		
	# PLog(Plot)	# Debug
	return Plot	
# ----------------------------------------------------------------------			
# argv-Verarbeitung wie in router (Haupt-PRG)
# Beim Menü Favoriten (add) endet json.loads in exception

PLog(str(sys.argv))
PLog(sys.argv[2])
paramstring = unquote_plus(sys.argv[2])
# PLog('params: ' + paramstring)
params = dict(parse_qs(paramstring[1:]))
PLog('merk_params_dict: ' + str(params))

PLog('action: ' + params['action'][0]) # hier immer action="dirList"
PLog('dirID: ' + params['dirID'][0])
# PLog('fparams: ' + params['fparams'][0])

func_pars = params['fparams'][0]
PLog("func_pars: " + func_pars)
name = stringextract("'name': ", ',', func_pars)	# für exceptions s.u.
name = name.replace("'", "")

try:
	func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
	func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
	mydict = json.loads(func_pars)
except Exception as exception:						# Bsp. Hinzufügen von Favoriten
	err_msg = str(exception)
	msg3=''
	if name:
		msg3 = "Eintrag >%s<" % name
	msg1 = "dieser Eintrag kann nicht verarbeitet werden."
	msg2 = "Fehler: %s" % err_msg
	heading='Fehler Merkliste'
	xbmcgui.Dialog().ok(heading, msg1, msg2, msg3)
	exit()
	

action = mydict['action']	# action + name immmer vorh., Rest fehlt bei action=del
name = mydict['name']
thumb=''; Plot=''; url=''
if 'thumb' in mydict:		# thumb, Plot, url fehlen bei action del (s. addDir)
	thumb = mydict['thumb']
if 'Plot' in mydict:
	Plot = mydict['Plot']
if 'url' in mydict:
	url = mydict['url']
PLog(action); PLog(name); PLog(thumb); PLog(Plot); PLog(url); 

if action == 'filter':													# Aufrufer ShowFavs (Settings: Ordner)
	watch_filter()														# Einträge unbearbeitet
else:
	# Markierungen "Ordner:" + "Modul:" aus akt. Anzeige entfernen
	#	Altern.: Merkliste einlesen + Satz suchen (zeitaufwändiger)
	Plot = clean_Plot(Plot) 
	msg1, err_msg, item_cnt = Watch_items(action,name,thumb,Plot,url)	# Einträge add / del / folder
	msg2 = err_msg
	if item_cnt:
		msg2 = "%s\n%s" % (msg2, u"Einträge: %s" % item_cnt)
		if action == 'del' or action == 'folder':							# Refresh Liste nach Löschen
			# MERKACTIVE ersetzt hier Ermitteln von Window + Control
			# bei Verzicht würde jede Liste refresht (stört bei großen Listen)
			if os.path.exists(MERKACTIVE) == True:		# Merkliste aktiv?
				xbmc.executebuiltin('Container.Refresh')

	# 01.02.2029 Dialog ersetzt durch notification 
	icon = R(ICON_DIR_WATCH)
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
	# exit()		# thread.lock-Error in Kodi-Matrix

