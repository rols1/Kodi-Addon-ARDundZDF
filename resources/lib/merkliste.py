# -*- coding: utf-8 -*-
################################################################################
#				merkliste.py - Teil von Kodi-Addon-ARDundZDF
#			 Hinzufügen + Löschen von Einträgen der Merkliste
#	aus Haupt-PRG hierher verlagert, da sonst kein Verbleib im akt. Listing
#	möglich.
#	Listing der Einträge weiter in ShowFavs (Haupt-PRG)
# 	Funktions-Calls via Auswertung sys.argv s. Modulende
################################################################################
# 	<nr>9</nr>										# Numerierung für Einzelupdate
#	Stand: 11.05.2024
#

from __future__ import absolute_import

from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import base64 			# url-Kodierung für Kontextmenüs
import os, sys, subprocess 
import re				
import json	
import datetime, time
	
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

try:											
	from util import *						# Aufruf Kontextmenü
	err="callfrom_context"
except Exception as exception:
	err=str(exception) 
	err= "%s | callfromstart_script" % err
	from resources.lib.util import *		# Aufruf start_script (Haupt-PRG)
PLog(err)


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('merkliste_python_3.x.x')
	ADDON_DATA	= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 
DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
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
					"Nachrichten", "Kinder/ZDFtivi", "Krimi", "Kultur" "TV-Livestreams",  
					"Politik/Gesellschaft", "Serien", "Sport",  "Talk", "Verbraucher"
					]
ORDNER_INFO		= [	u'# Ordner dienen der Sortierung und Filterung der Merkliste.',
					u'# Nutzung der Ordner:',
					u'# in Settings "Ordner für Merkliste verwenden" wählen.',
					u'#',
					u'# Regeln:', 
					u'# Ordnernamen dürfen keine Kommentarzeichen (#) enthalten. Auch Leerzeichen', 
					u'# und die meisten Sonderzeichen sind nicht erlaubt.',
					u'# Für zusammengesetzte Begriffe ist das "&"- oder "/"-Zeichen zu verwenden', 
					u'#',
					u'# Die Ordnerliste kann auch mit einem Editor geändert werden:',
					u'# Die einzelnen Begriffe sind im Editor mit einem Leerzeichen zu trennen.', 
					u'# Zeilenumbrüche sind beim Eingeben möglich - sie werden vom Addon wieder entfernt',
					] 

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
# 16.05.2020 Code für add/del/folder vereinheitlicht (gemeinsame  
#	Nutzung von save_merkliste)
#	
def Watch_items(action, name, thumb='', Plot='', url=''):		
	PLog('Watch_items: ' + action)
	
	url = unquote_plus(url)	
	PLog(unquote_plus(url)[100:])  			# url in fparams zusätzlich quotiert
	PLog(name); PLog(thumb); PLog(Plot);
	
	item_cnt = 0; 
	err_msg	= ''
	doppler = False

	# Umschaltung intern/extern + Dateicheck auch in ReadFavourites + save_merkliste,
	#	hier nur Dateicheck relevant:
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
		my_ordner = check_ordnerlist(my_ordner)			
		merkliste = ''
		if len(my_items):
			PLog('my_items: ' + my_items[0])			# 1. Eintrag
			for item in my_items:						# Liste -> String
				iname = stringextract('name="', '"', item) 
				name = py2_decode(name); iname = py2_decode(iname)
				PLog('Name: %s, IName: %s' % (name, iname))
				if iname == name:						# Doppler vermeiden, hier cleanmark unnötig
					doppler = True
					msg1 = u"Eintrag existiert bereits - neuen Eintrag umbenennen?"
					msg2 = u"Info:\nin der Merkliste lassen sich alle Einträge via"
					msg3 = u"Kontextmenü nachträglich umbenennen."
					head = "Merkliste: neuer Eintrag"
					ret = MyDialog(msg1=msg1, msg2=msg2, msg3=msg3, ok=False, cancel='Abbruch', yes='UMBENENNEN', heading=head)
					if ret == 1:
						new_name = get_new_name(iname, add='')	# <- neue Bez. oder iname
						if new_name != iname:					# alte -> neue Bez. 
							name = new_name
							doppler = False
					if doppler == True:
						PLog('Doppler')
						break
				merkliste = merkliste + item + "\n"
				item_cnt = item_cnt + 1
		else:	
			item = ''
		
		ordner=''
		if SETTINGS.getSetting('pref_merkordner') == 'true':		# Ordner-Auswahl
			if doppler == False:
				if len(my_ordner) == 0:								# leer: Initialisierung
					my_ordner = ORDNER
				my_ordner.insert(0, u"*ohne Zuordnung*")
				my_ordner=sorted(my_ordner)							# Problem mit key=str.lower in PY2
				
				ret = xbmcgui.Dialog().select(u'Ordner wählen (Abbrechen: ohne Zuordnung)', my_ordner, preselect=0)
				if ret > 0:
					ordner = my_ordner[ret]
				else:
					ordner = ''										# ohne Zuordnung=leer
				del my_ordner[0]
		
		# Neuer Eintrag:		
		url = url.replace('&', '&amp;') 							# Anpassung an Favorit-Schema
		merk = '<merk name="%s" ordner="%s" thumb="%s" Plot="%s">ActivateWindow(10025,&quot;%s&quot;,return)</merk>'  \
			% (name, ordner, thumb, Plot, url)
		PLog('merk: ' + merk)
				
		item_cnt = item_cnt + 1		
		if doppler == False:
			merkliste = py2_decode(merkliste) + merk + "\n"
			#item_cnt = item_cnt + 1
			
			# Merkliste + Ordnerinfo + Ordner + Ordnerwahl:	
			ret, err_msg = save_merkliste(merkliste, my_ordner)
			msg1 = u"Eintrag hinzugefügt" 
			if ret == False:
				PLog(err_msg)
				msg1 = u"Problem Merkliste"
		else:
			msg1 = u"Eintrag schon vorhanden"
		
	#------------------
	if action == 'del':
		my_items, my_ordner = ReadFavourites('Merk')					# 'utf-8'-Decoding in ReadFavourites
		my_ordner = check_ordnerlist(my_ordner)
		if len(my_items):
			PLog('my_items: ' + my_items[-1])
		merkliste = ''
		deleted = False
		for item in my_items:											# Liste -> String
			iname = stringextract('name="', '"', item) 					# unicode
			iname = iname.replace("–", "-")								# selten: &#8211; -> &#45;
			iname = py2_encode(iname)
			name = py2_encode(name)		
			PLog('Name: %s, IName: %s' % (name, iname))
			if name in cleanmark(iname):								# wie ShowFavs (cleanmark für Titel)
				deleted = True											# skip Satz = löschen 
				continue
			item_cnt = item_cnt + 1
			merkliste = py2_decode(merkliste) + py2_decode(item) + "\n"
			
		if deleted:
			# Merkliste + Ordnerinfo + Ordner + Ordnerwahl:	
			ret, err_msg = save_merkliste(merkliste, my_ordner)
			msg1 = u"Eintrag gelöscht"
			if ret == False:
				PLog(err_msg)
				msg1 = u"Problem Merkliste"
		else:
			msg1 = "Eintrag nicht gefunden." 
			err_msg = u"Merkliste unverändert."
			PLog(msg1)	
							
	#------------------
	if action == 'rename':
		my_items, my_ordner = ReadFavourites('Merk')					# 'utf-8'-Decoding in ReadFavourites
		my_ordner = check_ordnerlist(my_ordner)
		if len(my_items):												# Debug: letzter Eintrag
			PLog('my_items: ' + my_items[-1])
		merkliste = ''
		renamed = False
		for item in my_items:											# Liste -> String
			iname = stringextract('name="', '"', item) 					# unicode
			iname = iname.replace("–", "-")								# selten: &#8211; -> &#45;
			iname = py2_decode(iname)
			iname = cleanmark(iname)
			name = py2_decode(name)	
			PLog('Name: %s, IName: %s' % (name, iname))
		
			if name.strip() == iname.strip():							# unterschiedl. Leerz. möglich
				new_name = get_new_name(iname, add='')					# <- neue Bez. oder iname
				if new_name != iname:
					insert = 'name="%s"' % new_name
					if exist_in_list(insert, my_items) == False:		 
						item = item.replace('name="%s"' % py2_encode(iname), 'name="%s"' % py2_encode(new_name))
						renamed = True
					else:
						msg1 = ">%s< existiert bereits - Abbruch" % new_name 				
						MyDialog(msg1, '', '')
			item_cnt = item_cnt + 1
			merkliste = py2_decode(merkliste) + py2_decode(item) + "\n"
			
		if renamed:														# nur nach Ändern speichern
			# Merkliste + Ordnerinfo + Ordner + Ordnerwahl:	
			ret, err_msg = save_merkliste(merkliste, my_ordner)
			msg1 = u"Eintrag umbenannt"
			if ret == False:
				PLog(err_msg)
				msg1 = u"Problem Merkliste"
		else:
			msg1 = u"Eintrag nicht geändert." 
			err_msg = u"Merkliste unverändert."
			PLog(msg1)	
							
	#------------------
	if action == 'folder':												# Ordner ändern
		my_items, my_ordner = ReadFavourites('Merk')					# 'utf-8'-Decoding in ReadFavourites
		my_ordner = check_ordnerlist(my_ordner)
		
		merkliste=''; ordner=''; oldordner=''
		ret = True
		for item in my_items:						# Liste -> String
			iname = stringextract('name="', '"', item) # unicode
			iname = iname.replace("–", "-")								# selten: &#8211; -> &#45;
			
			iname = py2_decode(iname); name = py2_decode(name)
			iname = cleanmark(iname)									# Fett-/Farbe entfernen		
			PLog('Name: %s, IName: %s' % (name, iname))		
			if name == iname:
				if SETTINGS.getSetting('pref_merkordner') == 'true':	# Ordner eingeschaltet?
					oldordner = stringextract('ordner="', '"', item) 
					if len(my_ordner) == 0:								# leer: Initialisierung
						my_ordner = ORDNER
					my_ordner.insert(0, u"*ohne Zuordnung*")
					head = u'Ordner wählen für: %s' % (name)
					ret = xbmcgui.Dialog().select(head, my_ordner, preselect=0)
					ordner=oldordner									# Fallback: vorh. Ordner
					if ret >= 0:
						ordner = my_ordner[ret]
						if ret == 0:									# ohne Zuordnung=leer
							ordner = ''; oldordner = 'dummy'			# dummy ->  ''
					PLog("ordner: %s, oldordner: %s" % (ordner, oldordner))
					del my_ordner[0]									# "ohne Zuordnung" löschen
					
					if ordner != oldordner:
						# Ordner im Eintrag aktualisieren:
						PLog("url: " + url[:100])
						url = get_plugin_url(url)						# url aus ev. Base64-Kodierung		
						PLog("url: " + url[:100])
						url = url.replace('&', '&amp;') 				# Anpassung an Favorit-Schema
						merk = '<merk name="%s" ordner="%s" thumb="%s" Plot="%s">ActivateWindow(10025,&quot;%s&quot;,return)</merk>'  \
							% (name, ordner, thumb, Plot, url)
						PLog('merk: ' + merk)
						item = merk
				
			item_cnt = item_cnt + 1
			merkliste = py2_decode(merkliste) + py2_decode(item) + "\n"
		
		if ordner != oldordner:
			ret, err_msg = save_merkliste(merkliste, my_ordner)
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
# neuen Merklisteneintrag abfragen, Vorlage: iname)
#	Rückgabe new_name oder iname (Blank: iname) 
#	add: z.B. _alt
def get_new_name(iname, add=''):
	PLog("get_new_name:")
	
	line = iname
	if add:
		line = iname + add
	new_name = get_keyboard_input(line=line, head=u'Merklisten-Eintrag umbenennen')
	if new_name.strip() != '':
		return new_name
	else:
		return iname
	
# ----------------------------------------------------------------------
# url aus ev. Base64-Kodierung ermitteln
# url = Param. Watch_items
def get_plugin_url(url):
	PLog("get_plugin_url:")
	url_org = url

	# Base64-Kodierung wird nicht mehr verwendet (addDir in Modul util), Code verbleibt 
	#	hier bis auf Weiteres
	if 'plugin://plugin' not in url:				# Base64-kodierte Plugin-Url in ActivateWindow
		b64_clean= convBase64(url)					# Dekodierung mit oder ohne padding am Ende	
		if b64_clean == False:						# Fehler, Orig.-Url zurück
			return url
		try:
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
		except Exception as exception:
			PLog(str(exception))
			url = url_org	
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
	
	# 1. Vorprüfung: Setting Sync / externe Merkliste
	if SETTINGS.getSetting('pref_merksync') == 'false' or SETTINGS.getSetting('pref_merkextern') == 'false':	
		PLog("Sync_OFF")
		return
	# 2. Vorprüfung: externe Merkliste ist gleichzeitig interne Merkliste?
	if src_file == WATCHFILE: 
		PLog("Sync_Block_WATCHFILE")
		return
	
	f = xbmcvfs.File(src_file)
	s1 = f.size(); f.close()
	ret1=False; ret2=False
	if s1 > 100:							# Mindestbreite bis dirID=, Eintrag immer > 100 Zeichen
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
		PLog("Sync_Error, s1: %d" % s1)
	return
	
# ----------------------------------------------------------------------
# Speichert die Merkliste, zusammen mit Ordnerinfo + Ordner 
#	merkliste, my_ordner: mit ReadFavourites eingelesen,
#	 	Formate: merkliste=string, my_ordner=list
#	
def save_merkliste(merkliste, my_ordner):
	PLog('save_merkliste:')
	
	fname = WATCHFILE		
	if SETTINGS.getSetting('pref_merkextern') == 'true':	# externe Merkliste gewählt?
		fname = SETTINGS.getSetting('pref_MerkDest_path')
		if fname == '' or xbmcvfs.exists(fname) == False:
			PLog("merkextern: %s, %d" % (fname, xbmcvfs.exists(fname)))
			msg1 = u"Merkliste nicht gefunden\nBitte Settings überprüfen"
			return False, err_msg	
	PLog(fname)

	# Merkliste + Ordnerinfo + Ordner:
	my_ordner = sorted(my_ordner)								# Problem mit key=str.lower in PY2
	err_msg = ''												# gefüllt von Aufrufer 
	if my_ordner == '' or my_ordner == []:						# Fallback Basis-Ordner-Liste
		my_ordner = ORDNER
	my_ordner = " ".join(my_ordner)
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
			f = xbmcvfs.File(fname, 'w')							
			if PYTHON2:
				ret=f.write(merkliste); f.close()			
			else:												# Python3: Bytearray
				buf = bytearray()
				buf.extend(merkliste.encode())
				ret=f.write(buf); f.close()			
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
# Aufrufer Kontextmenü	
# ohne Param delete:	-> Merkliste mit Ordner als Filter	
#	Filter wird in MERKFILTER dauerhaft gespeichert
# mit Param delete: 	-> Löschen der Filterdatei MERKFILTER
# merkliste.xml bleibt unverändert
#			
def watch_filter(delete=''):
	PLog("watch_filter:")
	
	if delete:
		icon = R(ICON_DIR_WATCH)
		PLog('watch_filter: entferne_Filter')
		msg1 = 'Filter entfernen:'
		if os.path.isfile(MERKFILTER):		
			os.remove(MERKFILTER)
			if os.path.isfile(MERKACTIVE) == True:		# Merkliste aktiv?
				xbmc.executebuiltin('Container.Refresh')
			msg2 = "Filter wurde entfernt"	
		else:
			msg2 = "kein Filter gefunden"
			
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		return
		
	my_items, my_ordner = ReadFavourites('Merk')	# Ordnerliste holen	
	my_ordner = check_ordnerlist(my_ordner)
	my_ordner.insert(0, u"*ohne Zuordnung*")
	my_ordner=sorted(my_ordner)						# Problem mit key=str.lower in PY2
	
	preselect = 0									# Vorauswahl
	if os.path.isfile(MERKFILTER) == True:	
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
# gibt die Basis-Ordner-Liste sortiert zurück, falls my_ordner leer od. 
#	fehlerh. (geladen mit ReadFavourites)
# Check entfällt, falls Ordner abgewählt
#	
def check_ordnerlist(my_ordner):
	PLog("check_ordnerlist: %d" % len(my_ordner))
	PLog(my_ordner)
	
	if SETTINGS.getSetting('pref_merkordner') == 'true':
		if len(my_ordner)  == 0:
			heading = "Problem mit der Ordnerliste"
			msg1 = "Die Ordnerliste ist leer oder fehlerhaft."
			msg2 = "Es wird die Basis-Ordner-Liste verwendet."
			msg3 = u"Die Ordnerliste wird nach Einfügen oder Löschen erneuert."
			MyDialog(msg1, msg2, msg3, heading=heading)
			my_ordner = ORDNER
	return sorted(my_ordner)						# Problem mit key=str.lower in PY2
			
# ----------------------------------------------------------------------
# Markierungen "Ordner:" + "Modul:" aus tagline + summary der akt. 
#	Anzeige entfernen. Die Markierungen gehören nicht zum Datensatz 
#	des Eintrags
# ähnlich make_filenames (dort fett+farbig getrennt).
# 			
def clean_Plot(Plot):
	PLog("clean_Plot:")
	# PLog(Plot)	# Debug
	if '[COLOR' in Plot:				# Mark. hier immer fett+farbig
		items = blockextract('[B]', Plot, '[/B]')
		for item in items:
			if 'Ordner: ' in item or 'Modul: ' in item:
				Plot = Plot.replace(item, '')
				
	Plot = Plot.replace('||||||||', '')	# LF-Ruinen entfernen (4 Zeilen-Mark.)		
	Plot = Plot.replace('||||||', '')	# LF-Ruinen entfernen (3 Zeilen-Mark.)		
	# PLog(Plot)	# Debug
	return Plot	

# ----------------------------------------------------------------------
# Verwaltung Merklisten-Ordner (Komfort-Lösung, früher manuell via Editor)
#
def do_folder():
	PLog("do_folder:")

	dialog = xbmcgui.Dialog()
	head = 'Merklisten-Ordner bearbeiten'
	slist = [	u'INFO: aktuelle Liste der Merklisten-Ordner',
				u'INFO: Regeln für neue Merklisten-Ordner',
				u'Ordner entfernen (nur möglich, wenn nicht verknüpft)',
				u'Neuen Ordner hinzufügen (bitte die Regeln beachten - s.o.)',
				u'[COLOR red]RESET:[/COLOR] Basis-Ordnerliste wiederherstellen'] 
	while 1:													# Dauerschleife bis Abbruch
		ret = xbmcgui.Dialog().select(head, slist)
		PLog("ret: %d" % ret)
		if ret == -1 or ret == None:
			break
			
		icon = R(ICON_DIR_WATCH)
		my_items, my_ordner_list = ReadFavourites('Merk')		
		my_ordner_list = check_ordnerlist(my_ordner_list)		# Fallback Basis-Ordner-Liste
		my_ordner_list = sorted(my_ordner_list)
		merkliste = " ".join(my_items)							# speichern als String
		merkliste = py2_decode(merkliste) 
		
		#-----------------------------------------------------	# Ordner listen
		if ret == 0:											
			my_ordner_list = "\n".join(my_ordner_list)
			ret1 = dialog.textviewer(slist[0], my_ordner_list)
			if ret1 == None:							
				continue
			PLog("ret1: %d" % ret1)

		#-----------------------------------------------------	# Regeln für neue Ordner listen
		if ret == 1:											
			my_info_list = "\n".join(ORDNER_INFO)
			ret2 = dialog.textviewer(slist[1], my_info_list)
			if ret2 == None:							
				continue
			PLog("ret2: %d" % ret2)

		#-----------------------------------------------------	# Ordner entfernen
		if ret == 2:	
			ret3 = xbmcgui.Dialog().select(slist[2], my_ordner_list)
			PLog("ret3: %d" % ret3)
			if ret3 == -1:										# Abbruch, Esc
				continue
				
			ordner=''
			ordner = my_ordner_list[ret3]
			PLog("ordner: " + ordner)
			msg1 = u"Ordner [COLOR red]%s[/COLOR] wirklich löschen?" % ordner 
			ret4 = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbruch', yes='JA', heading=slist[1])
			PLog("ret4: %d" % ret4)
			if ret4 == 1:
				exist, link_cnt = check_ordner(ordner, my_ordner_list, my_items) # Abgleich Ordner mit Ordnerliste
				if link_cnt > 0:
					msg2=''; msg3=''
					msg1 = u"Ordner [COLOR red]%s[/COLOR] ist bereits verknüpft." % ordner
					if link_cnt:
						msg2 = u"Anzahl der Verknüpfungen: %d" % link_cnt
						msg3 = u"Ordner kann nicht  entfernt werden." 
					MyDialog(msg1, msg2, msg3)
				else:
					my_ordner_list.remove(ordner)
					ret, err_msg = save_merkliste(merkliste, my_ordner_list)
					# PLog(my_ordner_list)	# Debug
					msg1 = u'Merklisten-Ordner:'
					msg2 = u"[COLOR red]%s[/COLOR] entfernt" % ordner 
					if ret == False:
						msg2 = err_msg
					xbmcgui.Dialog().notification(msg1,msg2,icon,5000)

		#-----------------------------------------------------	# Ordner hinzufügen
		if ret == 3:											
			new = get_keyboard_input('', head='Neuer Ordner')	# Modul util
			if  new == None or new.strip() == '':
				continue
			new_org = py2_decode(new)	
			PLog(new)
			
			# kein 100%iger Schutz erforderlich:
			no_chars = [u'#',u' ',u'*',u'+',u'|',u',',u'!',u'"',u'$',u'%',u'(',u')',
						u'?',u'\\',u'~',u'\'',u';',u':',u'.',u'^',u'°']
			notsafe=False
			for char in no_chars:
				if char in new:
					if char == ' ':
						char = 'Leerzeichen'
					notsafe=True
					msg1 = u'unerlaubtes Zeichen: [COLOR red]%s[/COLOR]' % char
					MyDialog(msg1, '', '')
					break
			if notsafe:	
				continue
					
			msg1 = u'Merklisten-Ordner:'
			if exist_in_list(new, my_ordner_list) == False:		
				my_ordner_list.append(new)
				ret, err_msg = save_merkliste(merkliste, my_ordner_list)
				#PLog(my_ordner_list)	# Debug
				msg2 = u"[COLOR red]%s[/COLOR] hinzugefügt" % new 
				if ret == False:
					msg2 = err_msg
			else:
				msg2 = u"[COLOR red]%s[/COLOR] existiert bereits" % new 
			xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
			
		#-----------------------------------------------------	# Basis-Ordnerliste wiederherstellen
		if ret == 4:											
			msg1 = u"Basis-Ordnerliste wirklich wiederherstellen?"
			msg2 = u"Eigene Ordner und das Filtern damit entfallen."
			msg3 = u"Verknüpfungen mit diesen Ordnern bleiben aber erhalten."
			ret5 = MyDialog(msg1, msg2, msg3, ok=False, cancel='Abbruch', yes='JA', heading=slist[4])
			PLog("ret5: %d" % ret5)
			
			if ret5 == 1:
				my_ordner_list=[]
				ret, err_msg = save_merkliste(merkliste, my_ordner_list)
				#PLog(my_ordner_list)	# Debug
				msg1 = u'Merklisten-Ordner:'
				msg2 = u"Basis-Ordnerliste wiederhergestellt"
				if ret == False:
					msg2 = err_msg
				xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		
	return
				
# ----------------------------------------------------------------------
# Aufrufer: do_folder
# checkt zu löschenden Ordner auf Existenz und Verknüpfungen mit
#	Einträgen der Merkliste (my_items)
# Rückabe: exist  (bool), link_cnt (int) - ev. mit Rückgabe
#	link_list erweitern
#
def check_ordner(ordner, my_ordner_list, my_items):
	PLog("check_ordner:")

	exist=False; link_cnt=0
	if ordner in my_ordner_list == False:		# Ordner ist nicht vorh. + nicht verknüpft
		return exist, link_cnt
	else:
		exist=True; link_list=[]				# link_list bisher nicht genutzt
		for item in my_items:
			oname = stringextract('ordner="', '"', item)
			if oname == ordner:
				iname = stringextract('name="', '"', item)
				link_cnt = link_cnt + 1
				link_list.append(iname)
		# PLog(link_list)	# Debug
		return exist, link_cnt
		
# ----------------------------------------------------------------------
# Aufruf InfoAndFilter -> start_script (import util mit Pfad, s.o.)
# endet mit network_error zum Verbleib in InfoAndFilter
# Dialog().multiselect leider ohne usemono (korr. Spalten nicht möglich)
#
def clear_merkliste():
	PLog("clear_merkliste:")
	my_items, my_ordner = ReadFavourites('Merk')
	if len(my_items) == 0:
		msg1 = u'Keine Einträge gefunden.'
		MyDialog(msg1, '', '')		
		return	

	title = u"Bereinigung Merkliste | Backup empfohlen"
	msg1 = u"[B]Einträge (%d)[/B] einzeln überprüfen und nicht erreichbare Einträge zum Löschen vorschlagen?" % len(my_items)
	msg2 = u"Dauer nicht kalkulierbar."
	ret = MyDialog(msg1, msg2, msg3="", ok=False, cancel='Abbruch', yes='JA', heading=title)
	if ret == False:
		return
		
	tsecs = 3												# Timeout urlopen 	
	templ = "%03d | %15s | %36s"							# "Index | Fehler | Name "
	name_len = 30

	dirID_list = ["ZDF_Search", "SearchARDundZDFnew", "AudioSearch", "AudioSearch_cluster",
				"arte_Search", "Kika_Search", "Tivi_Search", "Search", "phoenix_Search",
				"XL_Search", "MVWSearch", "ARDSearchnew", "BilderDasErste",
				"resources.lib.my3Sat.Bilder3sat", "PodFavoritenListe"
			]
	
	my_list=[]; selected=[]; cnt=-1; note_cnt=0
	icon = R(ICON_DIR_WATCH)
	msg1 = u"%d Einträge" % len(my_items)
	msg2 = "Check ab Nr. %d" % 1
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000,sound=False)
	for item in my_items:
		cnt=cnt+1
		note_cnt=note_cnt+1
		if note_cnt > 10: 									# Notification: Einträge ab
			msg2 = "Check ab Nr. %d" % cnt
			xbmcgui.Dialog().notification(msg1,msg2,icon,5000,sound=False)
			note_cnt=0
		#if cnt > 10:				# Debug
		#	break
		item = unquote_plus(item)		
		PLog(item[:60])										# Bsp.: <merk name="HR-FERNSEHEN ..
		
		line=""
		name = stringextract('merk name="', '"', item)
		name = py2_decode(name)								# Leia
		dirID = stringextract('dirID=', '&amp', item)
		if dirID in dirID_list:								# Suchen durchwinken
			line = templ % (cnt+1, u"OK - verfügbar", name[:name_len])
			my_list.append(line)
			PLog("dirID_hit: " + line)
			continue
			
		fparams = stringextract('fparams={', '}',item)
		fparams = unquote_plus(fparams)						# Parameter sind zusätzl. quotiert
		if fparams == "":									# ev. alter Base64-kodierter Eintrag
			line = templ % (cnt+1, "Daten fehlen ", name[:name_len])
			my_list.append(line)
			selected.append(cnt)
			PLog(line)
			continue
		path= stringextract("path': '", "'", fparams)		# 1. Altern. Web-Url
		if path == '':
			path= stringextract("url': '", "'", fparams)	# 2. Altern. Web-Url
		if path == '':
			path= stringextract("img': '", "'", fparams)	# 3. Altern.: Bild
		if path == '':
			path= stringextract("img':'", "'", fparams)		# 4. Altern.: Bild (o.Blank, Arte)
		if path == '':
			path= stringextract("thumb': '", "'", fparams)	# 5. Altern.: Bild phoenix
		if path == '':
			path= stringextract("thumb=", "&amp", fparams)	# 6. Altern.: Bild außerhalb fparams (Layout Button)
		if path == "":
			line = templ % (cnt+1, "Web-Url fehlt ", name[:name_len])
			my_list.append(line)
			selected.append(cnt)
			PLog(line)
			continue

		if "//www.ardaudiothek" in path:					# Pfadergänzung "/" gegen Error HTTP308_301
			if path.endswith("/") == False:
				path = path + "/"
			
		try:												# Link-Test - nicht via get_page (Performance)
			err=""
			PLog("getpath: " + path)
			r = urlopen(path, timeout=tsecs)
			url = r.geturl()
			PLog("url_OK: " + url)
		except Exception as e:
			PLog(str(e))
			err = str(e)
			try:
				if "308:" in str(e) or "301:" in str(e):	# Permanent-Redirect-Url
					new_url = e.hdrs.get("Location")
					parsed = urlparse(path)
					if new_url.startswith("http") == False:	# Serveradr. vorh.?
						new_url = 'https://%s%s/' % (parsed.netloc, new_url)
					PLog("HTTP308_301_new_url: " + new_url)
					r.close()
					r = urlopen(new_url, timeout=tsecs)		# Link-Test mit new_url
			except Exception as e:
				PLog(str(e))
				err = str(e)
			
			err_msg = "Url unbekannt"						# Default-Error
			if "operation timed out" in err:				# Hinw. auf Bedeutung Timeout im Button-Info
				err_msg = "HTTP Timeout"
			line = templ % (cnt+1, err_msg, name[:name_len])
			my_list.append(line)
			selected.append(cnt)
			PLog(line)
			continue			
			
		line = templ % (cnt+1, u"OK - verfügbar", name[:name_len])
		PLog(line)
		my_list.append(line)
	
			
	title = u"Ausgewählte Einträge löschen? Auswahl bei Bedarf ändern"
	ret_ind = xbmcgui.Dialog().multiselect(title, my_list, preselect=selected, useDetails=False)
	PLog("Mark0")
	PLog(str(ret_ind))										# 0,3,9,.. 
		
	heading = u'Bereinigung Merkliste'
	if ret_ind:
		for index in sorted(ret_ind, reverse=True):			# rückwärts (Löschen aktualisiert Index in my_list)
			del my_items[index]
	
		merkliste = "\n".join(my_items)						# speichern als String
		merkliste = py2_decode(merkliste) 	
		ret, err_msg = save_merkliste(merkliste, my_ordner)
		msg1 = u'Einträge gelöscht: %d' % len(ret_ind)
		msg2 = u'verbleibende Einträge: %d' % len(my_items)
		if ret == False:									# Wahrscheinlichkeit erhöht bei ext. Liste
			msg2 = u'Fehler beim Speichern | Merkliste unverändert.'
			msg3 = err_msg
		else:
			msg3 = u'Merkliste erfolgreich gespeichert.'
			PLog("%s | %s" % (msg2, msg3))
	else:
		msg1 = u'keine Einträge zum Löschen ausgewählt.'
		msg2 = u'Merkliste bleibt unverändert.' 
		msg3 = ''
	MyDialog(msg1, msg2, msg3, heading=heading)
	return # -> network_error s.u.

######################################################################## 
# Direkter Funktionscall aus Kontext-Menü bisher nicht möglich, daher			
# sys.argv-Verarbeitung wie in router (Haupt-PRG)
# Beim Menü Favoriten (add) endet json.loads in exception
# Aufrufe aus Haupt-PRG ohne fparams: clear_merkliste,
# 	do_folder - return via network_error.

PLog(str(sys.argv))
PLog(sys.argv[2])
paramstring = unquote_plus(sys.argv[2])
PLog('params: ' + paramstring)
params = dict(parse_qs(paramstring[1:]))
PLog('merk_params_dict: ' + str(params))

# ------------------------------------------------- # callfromstart_script (2 Varianten möglich):

if "'fparams_add': 'clear'" in str(params):			# 1. Aufruf InfoAndFilter -> start_script -> router
	clear_merkliste()
	ignore_this_network_error()						# network_error statt threading Exception	

if "'fparams_add': 'do_folder'" in str(params):		# 2. Aufruf InfoAndFilter -> router
	do_folder()
	PLog("exit_callfromstart_script")
	exit()

# ------------------------------------------------- # callfrom_context:

icon = R(ICON_DIR_WATCH)
PLog('action: ' + params['action'][0]) 				# context: immer action="dirList"
PLog('dirID: ' + params['dirID'][0])				# context: immer dirID="Watch"
# PLog('fparams: ' + params['fparams'][0])

func_pars = params['fparams'][0]					# fparams s. addDir
PLog("func_pars: " + func_pars)
name = stringextract("'name': ", ',', func_pars)	# für exceptions s.u.
name = name.replace("'", "")

try:
	func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
	func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
	mydict = json.loads(func_pars)
	PLog("merk_mydict: " + str(mydict))
except Exception as exception:						# Bsp. Hinzufügen von Favoriten
	err_msg = str(exception)
	PLog("mydict_error: " + err_msg)
	msg1 = u"Eintrag nicht verwendbar!"
	msg2 = u"Fehler: %s.." % err_msg[:40]
	heading='Fehler Merkliste'
	# 26.03.2024 Dialog ersetzt durch notification 
	icon = R(ICON_DIR_WATCH)
	xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
	exit()
	
# ----------------------------------------------------------------------
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

if 'filter' in action:													# Filter-Aktionen:
	if action == 'filter':												# Aufrufer ShowFavs (Settings: Ordner)
		watch_filter()													# Filter setzen
	if action == 'filter_delete':
		watch_filter(delete=True)										# Filter (MERKFILTER) löschen
	if action == 'filter_folder':										# Merklisten-Ordner bearbeiten (add/remove)
		do_folder()
else:																	# Merklisten-Aktionen:	
	Plot = clean_Plot(Plot) 
	msg1, err_msg, item_cnt = Watch_items(action,name,thumb,Plot,url)	# Einträge add / del / folder / rename
	msg2 = err_msg
	PLog("item_cnt: %s, action: %s, MERKACTIVE: %s" % (item_cnt, action, os.path.isfile(MERKACTIVE)))
	if item_cnt:
		msg2 = "%s\n%s" % (msg2, u"Einträge: %s" % item_cnt)
		if action == 'del' or action == 'folder' or action == 'rename':	# Refresh Liste nach Löschen
			# MERKACTIVE ersetzt hier Ermitteln von Window + Control
			# bei Verzicht würde jede Liste refresht (stört bei großen Listen)
			if os.path.isfile(MERKACTIVE) == True:						# Merkliste aktiv?
				xbmc.executebuiltin('Container.Refresh')

	xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
	# exit()		# thread.lock-Error in Kodi-Matrix
