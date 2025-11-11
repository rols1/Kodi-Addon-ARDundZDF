# -*- coding: utf-8 -*-
################################################################################
#			tools.py - Teil von Kodi-Addon-ARDundZDF
#
################################################################################
#	aus Haupt-PRG verlagerte Tools (Menü InfoAndFilter), z.B.: 
#		Filterliste, Suchwortliste
 
################################################################################
# 	<nr>16</nr>								# Numerierung für Einzelupdate
#	Stand: 12.11.2025

# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:					
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve 
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse , urlsplit, parse_qs 
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

# Standard:
import time, datetime

# Addonmodule:
from resources.lib.util import *
import resources.lib.EPG as EPG

# Globals
ICON_FILTER		= 'icon-filter.png'
ICON_DIR_FOLDER	= "Dir-folder.png"
ICON_INFO 		= "icon-info.png"

MAX_LEN 		= 24	

ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
EPGACTIVE = os.path.join(DICTSTORE, 'EPGActive') 		# Marker thread_getepg aktiv
PLAYLIST 		= 'livesenderTV.xml'					# TV-Sender-Logos 											

HEADERS="{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',\
	'Referer': '%s', 'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'application/json, text/plain, */*'}"

FILTER_SET 	= os.path.join(ADDON_DATA, "filter_set")
AKT_FILTER	= ''
if os.path.exists(FILTER_SET):	
	AKT_FILTER	= RLoad(FILTER_SET, abs_path=True)
AKT_FILTER	= AKT_FILTER.splitlines()					# gesetzte Filter initialiseren 
THUMBNAIL_CHECK = os.path.join(ADDON_DATA, "thumbnail_check")

################################################################################

#----------------------------------------------------------------
# Aufruf InfoAndFilter
# Menüs für SearchWordWork 
def SearchWordTools():
	PLog('SearchWordTools:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
		
	searchwordfile = os.path.join(ADDON_DATA, "search_ardundzdf") 
	searchwords = RLoad(searchwordfile, abs_path=True)				# Liste laden
	searchwords = searchwords.splitlines()
	PLog(len(searchwords))

	icon = R("icon_searchwords.png")
	if len(searchwords) == 0:	
		msg1 = "Problem Suchwortliste"
		msg2 = 'Liste fehlt oder ist noch leer'				
		PLog(msg2)
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
												
	summ = u"Suchwörter für die Suche in ARD Mediathek und ZDF Mediathek"	

	title = u"alle Suchwörter [B]zeigen[/B] (%d)" % len(searchwords)
	fparams="&fparams={'action': 'show_list'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.SearchWordWork", fanart=R(FANART), 
		thumb=R('icon_searchwords.png'), summary=summ, fparams=fparams)				
		
	if 	len(searchwords) > 0:		
		title = u"Suchwort [B]löschen[/B]"
		tag = u"ein Suchwort aus der Liste [B]löschen[/B]" 
		fparams="&fparams={'action': 'delete'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.SearchWordWork", fanart=R(FANART), 
			thumb=R('icon_searchwords.png'), tagline=tag, summary=summ, fparams=fparams)		
		
	title = u"Suchwort [B]hinzufügen[/B]"
	tag = u"ein Suchwort der Liste [B]hinzufügen[/B] (max. %d)" % MAX_LEN 
	fparams="&fparams={'action': 'add'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.SearchWordWork", fanart=R(FANART), 
		thumb=R('icon_searchwords.png'), tagline=tag, summary=summ, fparams=fparams)		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#----------------------------------------------------------------
def SearchWordWork(action):
	PLog('SearchWordWork:') 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button

	icon = R("icon_searchwords.png")
	dialog = xbmcgui.Dialog()
		
	searchwordfile = os.path.join(ADDON_DATA, "search_ardundzdf") 
	searchwords = RLoad(searchwordfile, abs_path=True)				# Liste laden
	searchwords = searchwords.splitlines()
	searchwords=sorted(searchwords, key=str.lower)
	PLog(len(searchwords))

	if searchwords == '':
		msg1 = "Problem Suchwortliste"
		msg2 = 'Liste fehlt oder ist noch leer'				
		dialog.notification(msg1,msg2,icon,5000)
		PLog(msg2); 
		return
												
	if action == 'show_list':										# Liste zeigen
		PLog("do: " + action)
		title = u"aktuelle Liste der Suchwörter (+ steht für Leerzeichen)"
		searchwords = "\n".join(searchwords)
		textviewer(title, searchwords, usemono=True)
		
	if action == 'delete':
		PLog("do: " + action)
		title = u"Suchwort löschen"
		ret = dialog.select(title, searchwords)
		PLog(ret)
		if ret > -1:
			msg1 = u"Suchwort [B]%s[/B] wirklich löschen?" % searchwords[ret]
			del_ret = MyDialog(msg1=msg1, msg2='', msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
			PLog(del_ret)
			if del_ret:
				item = searchwords[ret]
				searchwords.remove(item)
				msg1 = title
				msg2 = u"gelöscht: [B]%s[/B] " % item
				searchwords = "\n".join(searchwords)
				err_msg =  RSave(searchwordfile, searchwords)	# speichern
				if err_msg:										# RSave-Problem?
					msg1 = u"Fehler beim Speichern der Suchwortliste"
					PLog(msg1)	
					msg2 = err_msg
				dialog.notification(msg1,msg2,icon,3000)
				PLog(msg2)

	if action == 'add':
		PLog("do: " + action)
		
		if len(searchwords) >= MAX_LEN:
			msg1 = "Suchwortliste"
			msg2 = u'maximale Länge bereits erreicht: [B]%d[/B] ' % max_len
			MyDialog(msg1, msg2, '')
			return
					
		title = u'Suchwort hinzufügen (Groß/klein egal)'
		ret = dialog.input(title, type=xbmcgui.INPUT_ALPHANUM)	# Eingabe Suchwort
		PLog(ret)
		if ret.strip() == '':
			return

		ret = py2_encode(ret)
		ret = ret.strip(); ret = ret.replace(" ", "+")		# Innen-Blank -> + 
		for item in searchwords:							# Check: vorhanden?
			PLog(up_low(ret));PLog(up_low(item)); 
			if up_low(ret) in up_low(item):				
				msg1 = "Suchwortliste"
				msg2 = u'existiert schon: [B]%s[/B] ' % ret
				PLog(msg2)		
				double=False
				dialog.notification(msg1,msg2,icon,5000)
				return

		msg1 = "Suchwortliste"
		msg2 = u'neu: [B]%s[/B]' % ret		
		searchwords.append(ret)							# Suchwort hinzufügen
		searchwords = "\n".join(searchwords)
		searchwords = py2_encode(searchwords)
		err_msg =  RSave(searchwordfile, searchwords)	# speichern
		if err_msg:										# RSave-Problem?
			msg1 = "Fehler beim Speichern der Suchwortliste" 
			PLog(msg1)	
			msg2 = err_msg
		dialog.notification(msg1,msg2,icon,5000)
		PLog(msg2)
		 
	xbmc.executebuiltin('Container.Refresh')
	return
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# Menüs für FilterToolsWork 
def FilterTools():
	PLog('FilterTools:'); 
	li = xbmcgui.ListItem()
	li = home(li, ID=NAME)				# Home-Button
		
	filterfile = os.path.join(ADDON_DATA, "filter.txt") 		# init: check_DataStores
	filter_page = RLoad(filterfile, abs_path=True)				# Filterliste laden

	if filter_page == '' or len(filter_page) <= 20:
		msg1 = "Problem Filterliste"
		msg2 = 'Liste kann nicht geladen werden'				# -> nur Button Hinzufügen
		PLog(msg2); PLog(filter_page)
		filter_page=''											# fehlerhaft=leer
		icon = R(ICON_FILTER)
		xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		
	akt_filter=''; 
	if os.path.isfile(FILTER_SET):
		page = RLoad(FILTER_SET, abs_path=True)
		page = page.strip()
		akt_filter = page.splitlines()
	PLog(akt_filter)
												
	summ = u"Ausschluss-Filter für Beiträge von ARD und ZDF."
	summ = u"%s\n\nWirkung: Einzelbeiträge, die einen gesetzten Filter in Titel, Subtitel oder Beschreibung enthalten, werden aussortiert." % summ 
	
	if filter_page:
		if akt_filter:
			title = u"aktuell gesetzte(n) Filter zeigen (%d)" %  len(akt_filter)
			fparams="&fparams={'action': 'show_set'}" 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterToolsWork", fanart=R(FANART), 
				thumb=R(ICON_FILTER), summary=summ, fparams=fparams)		

		title = u"alle Filterwörter zeigen" 
		fparams="&fparams={'action': 'show_list'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), summary=summ, fparams=fparams)				
	
		title = u"Filter [COLOR blue]setzen (aktuell: %d)[/COLOR]" % len(akt_filter)
		tag = u"ein oder mehrere Filterworte [COLOR blue]setzen[/COLOR]" 
		fparams="&fparams={'action': 'set'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)
					
		title = u"Filterwort [B]löschen[/B]"
		tag = u"ein Filterwort aus der Ausschluss-Liste [COLOR red]löschen[/COLOR]" 
		fparams="&fparams={'action': 'delete'}" 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterToolsWork", fanart=R(FANART), 
			thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)		
		
	title = u"Filterwort [COLOR green]hinzufügen[/COLOR]"
	tag = u"ein Filterwort der Ausschluss-Liste [COLOR green]hinzufügen[/COLOR]" 
	fparams="&fparams={'action': 'add'}" 
	addDir(li=li, label=title, action="dirList", dirID="resources.lib.tools.FilterToolsWork", fanart=R(FANART), 
		thumb=R(ICON_FILTER), tagline=tag, summary=summ, fparams=fparams)		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#----------------------------------------------------------------
# Aufruf FilterTools
# Ausschluss-Filter Anzeigen/Setzen/Hinzufügen/Löschen
# 13.05.2020 'Container.Refresh' muss für LibreElec + Android vor 
#	notification erfolgen und cacheToDisc=False - sonst wirkungslos.
#
def FilterToolsWork(action):
	PLog('FilterToolsWork: ' + action) 
	dialog = xbmcgui.Dialog()

	filter_pat = "<filter>\n%s\n</filter>\n" 					# Rahmen Filterliste
	filterfile = os.path.join(ADDON_DATA, "filter.txt")			# init: check_DataStores
	page = RLoad(filterfile, abs_path=True)						# Filterliste laden
	filter_list = stringextract('<filter>', '</filter>', page)
	filter_list = filter_list.splitlines()
	filter_list.remove('')										# aus ev. Leerz.
	filter_list=sorted(filter_list, key=str.lower)
	PLog(filter_list)
	
	page = RLoad(FILTER_SET, abs_path=True)						# akt. Filter laden
	akt_filter = page.splitlines()
	akt_filter=sorted(akt_filter, key=str.lower)
	PLog(akt_filter)	

	if action == 'show_set':									# gesetzte Filter zeigen
		title = u"aktuell gesetzte(r) Filter"
		akt_filter = "\n".join(akt_filter)
		textviewer(title, akt_filter,usemono=True)
			
	if action == 'set':
		index_list = get_list_indices(akt_filter, filter_list)	# akt. Filter-Indices ermitteln
		PLog(index_list); 
		title = u"Filter setzen (grün: gesetzt)"
		ret = dialog.multiselect(title, filter_list, preselect=index_list)
		PLog(ret)												# ret hier Liste
		if ret !=  None:										# None bei Abbruch
			if len(ret) > 0:
				items = get_items_from_list(ret, filter_list)	# Indices -> Filter-items
				items = "\n".join(items) 
			else:
				items = ''
			RSave(FILTER_SET, items)
			msg1 = u"Filter setzen"
			msg2 = u"gesetzte Filter: %d" % len(ret)
			icon = R(ICON_FILTER)
			xbmc.executebuiltin('Container.Refresh')
			xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
		
	if action == 'add':
		title = u'Filterwort hinzufügen (Groß/klein egal)'
		ret = dialog.input(title, type=xbmcgui.INPUT_ALPHANUM)	# Eingabe Filterwort
		PLog(ret)
		if ret:
			ret = py2_encode(up_low(ret, mode='low'))
			if ret in filter_list:								# Check: vorhanden?
				msg1 = "Filterliste"
				msg2 = '%s existiert schon. Anzahl: %d' % (ret.strip(), len(filter_list))		
				icon = R(ICON_FILTER)
				xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
			else:	
				filter_list.append(ret.strip())					# Filterwort hinzufügen
				if '' in filter_list:
					filter_list.remove('')						# aus ev. Leerz.
				items = "\n".join(filter_list)
				items = py2_encode(items)
				filter_pat = filter_pat % items					# Filter -> xml-Rahmen
				PLog(filter_pat)
				err_msg = RSave(filterfile, filter_pat)			# speichern
				if err_msg:
					msg1 = "Fehler beim Speichern der Filterliste" 
					PLog(msg1)	
					MyDialog(msg1, '', '')
				else:
					msg1 = "Filterliste"
					msg2 = '%s hinzugefügt. Anzahl: %d' % (ret.strip(), len(filter_list))		
					icon = R(ICON_FILTER)
					xbmc.executebuiltin('Container.Refresh')					
					xbmcgui.Dialog().notification(msg1,msg2,icon,5000)
	
	if action == 'delete':
		title = u"Filterwort löschen (ev. gesetzter Filter wird mitgelöscht)"
		ret = dialog.select(title, filter_list)					# Auswahl Filterliste
		PLog(ret)
		if ret >= 0:
			ret = filter_list[ret]								# Index -> item
			item = py2_encode(ret)
			PLog(item)
			is_filter=False;
			if item in akt_filter:								# auch gesetzter Filter?
				is_filter=True
			msg2 = "[COLOR red]%s[/COLOR] ist kein gesetzter Filter." % ret
			if is_filter:	
				msg2 = "gesetzter Filter [COLOR red]%s[/COLOR] wird mitgelöscht" % ret
			msg1 = "Filterwort [COLOR red]%s[/COLOR] wirklich löschen?" % ret 

			ret = MyDialog(msg1=msg1, msg2=msg2, msg3='', ok=False, cancel='Abbruch', yes='JA', heading=title)
			PLog(ret)
			if ret == 1:
				filter_list.remove(item)						# Filterwort entfernen
				filter_len = len(filter_list)
				items = "\n".join(filter_list)
				items = py2_encode(items)
				filter_pat = filter_pat % items					# Filter -> xml-Rahmen
				PLog(filter_pat)
				err_msg1 = RSave(filterfile, filter_pat)			# speichern
				if is_filter:
					akt_filter.remove(item)
					items = "\n".join(akt_filter)
					err_msg2 = RSave(FILTER_SET, items)	

				if err_msg1 or err_msg2:
					if err_msg1:
						msg1 = "Fehler beim Speichern der Filterliste" 
						PLog(msg1)	
						MyDialog(msg1, '', '')
					if err_msg2:
						msg1 = "Fehler beim Speichern der aktuell gesetzten Filter" 
						PLog(msg1)	
						MyDialog(msg1, '', '')
				else:
					msg1 = "Filterliste"
					msg2 = u'%s gelöscht. Anzahl: %d' % (item, filter_len)		
					icon = R(ICON_FILTER)
					xbmc.executebuiltin('Container.Refresh')					
					xbmcgui.Dialog().notification(msg1,msg2,icon,5000)		
			
	if action == 'show_list':									# Filterliste zeigen
		title = u"Liste verfügbarer Filter"
		filter_list = "\n".join(filter_list)
		textviewer(title, filter_list,usemono=True)
		
	if action == 'state_change':								# aus Kontextmenü
		msg1 = "Ausschluss-Filter:"
		icon = R(ICON_FILTER)
		if SETTINGS.getSetting('pref_usefilter') == 'true':
			SETTINGS.setSetting('pref_usefilter','false')
			msg2 = u'AUSgeschaltet'		
		else:											
			SETTINGS.setSetting('pref_usefilter','true')
			msg2 = u'EINgeschaltet'		
		xbmc.executebuiltin('Container.Refresh')
		xbmcgui.Dialog().notification(msg1,msg2,icon,3000)		
								
	return
	
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# Kodis Thumbnails-Ordner bereinigen
# Hinw.: ClearUp (util) nicht geeignet (ohne Check einz. Dateien
#	in Unterverz.)
# 12/2024 autom. Bereinigung ergänzt (Tread-Start Haupt-PRG, 
#	Zeitstempel THUMBNAIL_CHECK). Setting pref_thumbnail_days ist
#	gleichzeitig Intervall und Löschalter (kleines Intervall=große
#	Löschmenge)
#
def ClearUpThumbnails(nogui=""):
	PLog('ClearUpThumbnails: ' + nogui) 
	thumb=R("icon-clear.png")
	notimsg1 = "Thumbnails-Bereinigung"
	
	now = time.time()											# Unix-Format 1735387316.4195263
	stamp = str(now).split('.')[0]								# Zeitstempel (int)
	PLog("stamp: " + stamp)
	
	THUMBNAILS = os.path.join(USERDATA, "Thumbnails") 
	directory = THUMBNAILS
	akt_size_raw = get_dir_size(directory, raw=True)
	akt_size = humanbytes(akt_size_raw)	

	if nogui == "":												# Start aus Menü
		li = xbmcgui.ListItem()
		li = home(li, ID=NAME)				# Home-Button
		dialog = xbmcgui.Dialog()

		#-------------------------------						# 1. Auswahl Lösch-Alter
		title = u"Bitte das Lösch-Alter in Tagen auswählen (Dateien älter als x Tage):"
		day_list = ["1","5","10","30","100"]
		sel = dialog.select(title, day_list)	
		if sel < 0:
			return
		sel = day_list[sel]
		
		title = u"Thumbnails-Bereinigung starten?"
		msg1 = u"Aktuelle Größe: [B]%s[/B] | löschen älter als: [B]%s[/B] Tag(e)" % (akt_size, sel)
		msg2 = u"Thumbnails-Bereinigung jetzt starten?"
		msg3 = u"Rückgängig nicht möglich!"
		ret = MyDialog(msg1, msg2, msg3, ok=False, cancel='Abbruch', yes='JA', heading=title)
		PLog(ret)
		if ret != 1:
			return	
		PLog("days_selected: " + sel)

	else:														# Start aus Haupt-PRG (Thread)
		sel = SETTINGS.getSetting('pref_thumbnail_days')		# Intervall + Lösch-Alter aus Setting
		if os.path.exists(THUMBNAIL_CHECK) == False:			# Zeitstempel noch nicht gesetzt,
			RSave(THUMBNAIL_CHECK, stamp)						# 	setzen und Ende
			return
		else:
			PLog("set_days: " + sel)
			last_check = RLoad(THUMBNAIL_CHECK, abs_path=True)
			last_check = last_check.strip()
			maxtime = int(last_check) + int(sel)*86400
			PLog("last_check: %s, maxtime: %d, now: %d" % (last_check, maxtime, now))
			diff = 	maxtime - now
			if now >= maxtime:									# Diff last_check / Tage-Auswahl erreicht?
				PLog("reach_day_limit: diff %d" % diff)			# -> Bereinigung
			else:
				remain = seconds_translate(diff)				# Tage-Auswahl noch nicht erreicht -> Ende
				PLog("reach_day_limit_in: %s (diff %d sec)" % (remain, diff))
				return		
	
	#-------------------------------							# 2. Bereinigung
	
	PLog("days_selected: " + sel)
	maxdays = int(sel)
	PLog("ClearUp_Start: %s | days: %d" % (directory, maxdays))
	max_secs = maxdays*86400 									# 1 Tag=86400 sec
	cnt=0; del_cnt=0; ok=True 
	try:
		for dirpath, dirnames, filenames in os.walk(directory):
			for f in filenames:
				fp = os.path.join(dirpath, f)					# Filepath
				#  PLog(fp)				# Debug
				# skip symbolic link:
				if not os.path.islink(fp):
					cnt = cnt+1
					if os.stat(fp).st_mtime < (now - max_secs):
						os.remove(fp)
						del_cnt = del_cnt+1
	except Exception as exception:
		ok=False
		msg2 = str(exception)	
		PLog("clearup_error " + msg2)		
	
	#-------------------------------							# 3. Abschluss-Info
	
	RSave(THUMBNAIL_CHECK, stamp)								# Zeitstempel aktualisieren
	new_size_raw = get_dir_size(directory, raw=True)
	new_size = humanbytes(new_size_raw)	
	win = akt_size_raw - new_size_raw
	PLog("del_cnt: %d, win: %d" % (del_cnt, win))
	if ok:
		msg1 = u"Fertig | Entfernte Thumbnails: [B]%s[/B]" % del_cnt
		msg2 = u"Größe vorher / nachher: %s / %s." % (akt_size, new_size)
		msg3 = "Speicherplatz unverändert."
		notimsg2 = u"vor/nach: %s/%s" % (akt_size, new_size)

		if win > 0:
			msg3 = "Speicherplatz freigegeben: [B]%s[/B]." % humanbytes(win)
			notimsg2 = "frei: [B]%s[/B]" % humanbytes(win)
	else:
		msg1 = "Problem in Bereinigung! Fehler:"
		msg3=""
		notimsg1 = "Bereinigungsproblem:"; notimsg2 = msg2
		
	if nogui == "":											# Start aus Menü
		MyDialog(msg1, msg2, msg3)
	else:													# Start aus Haupt-PRG
		xbmcgui.Dialog().notification(notimsg1,notimsg2,thumb,5000)	
			
	return														# Verbleib in Tools-Liste
	
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# gibt akt. Datum aus Startpost in kodinerds.net zurück
# 14.4.2023 Anpassung an Forum-Update
# 08.06.2023 ergänzt mit letztem Eintrag
#
def get_foruminfo():
	PLog('get_foruminfo:') 
	# return "",""		# Debug

	dt=''
	path = "https://www.kodinerds.net/index.php?thread/64244-release-kodi-addon-ardundzdf/"
	page, msg = get_page(path=path)
	
	dt = stringextract(u"Update (Stand ", u")", page)		# Stand: Datum, Uhrzeit
	if dt == "":
		dt = u"? - Forum nicht erreicht"
	PLog("dt: " + dt)
	
	items = stringextract(u"Probleme, Fixes:", u"####", page)	# Update-Infos
	items = blockextract(u'<li>', items, "</li>")
	PLog(len(items))
	
	if len(items) == 0:
		last_item="keine Einzelupdates gefunden"
	else:
		last_item = items[-1]
		last_item = cleanhtml(last_item)
		last_item = transl_json(last_item)
		last_item = unescape(last_item)
		last_item = last_item.replace('\\\"','*')				# z.B. Meldung \"Streamlink\" bei..
	PLog("last_item: " + last_item)
	
	return dt, last_item
	
#----------------------------------------------------------------
# Aufruf InfoAndFilter
# stößt die Aktualisierung des EPG an 
#
def refresh_epg():
	PLog('refresh_epg:') 
	
	EPG.thread_getepg(EPGACTIVE, DICTSTORE, PLAYLIST)
	return

#----------------------------------------------------------------
# Kontextmenü 
# Aufruf addDir -> RunScript
# bei Bedarf Sender-spez. Funktionen auslagern, hier verteilen
# 
def Context(title, path, img, mode):
	PLog('Context:'); 
	PLog(title);  PLog(path); PLog(img); PLog(mode);
	
	if "ShowSeason" not in mode:							# bisher..
		PLog("not_supported: " + mode) 
		return
	
	if "zdf-prod-futura" in path or "www.zdf.de" in path:
		page, msg = get_page(path=path, header=HEADERS)		# futura ZDF
		try:
			jsonObject = json.loads(page)
			PLog(str(jsonObject)[:80])
			# Bsp.: www.zdf.de/video/serien/the-rookie-100/the-hammer-100 ->
			#		www.zdf.de/video/serien/the-rookie-100:
			surl = jsonObject["document"]["sharingUrl"]	# Web-Url
			pos = surl.rfind("/")
			path = surl[:pos]
			new_url, msg = get_page(path, GetOnlyRedirect=True)				
			
			page, msg = get_page(path=new_url)				# nur für img
			imgset = stringextract("imageSrcSet=", '/>', page)
			imgset = blockextract("https", imgset)
			img = R(ICON_DIR_FOLDER)
			for item in imgset:
				PLog(item)
				if "1280w" in item:
					img = item.split(" ")[0]				# ..1280x720?cb=1743085107028 1280w
					break
		except Exception as exception:
			path=""
			msg = str(exception)
			PLog("ShowSeason_error_ZDF: " + msg)
		
		PLog("params_Context: "); PLog(path); PLog(img);
		if path and "-movie-" not in path:
			dirID = "ZDF_KatSeriePre"
			fparams="&fparams={'title': '%s', 'path': '%s', 'img': '%s'}" %\
				(quote(title), quote(path), quote(img))
			action="action=dirList&dirID=%s&fparams=%s"	% (dirID, fparams)
			PLog("action_Context: " + action)
			action=quote(action)
			xbmc.executebuiltin('RunAddon(%s, %s)'  % (ADDON_ID, action))
			exit()
	
	if "api.ardmediathek" in path:							# ARD
		# % (sender, urlId)
		base = "https://api.ardmediathek.de/page-gateway/pages/%s/grouping/%s?embedded=true"
		page, msg = get_page(path=path)
		
		# typ:  SEASON_SERIES, SINGLE, INFINITE_SERIES (z.B. Nachrichten, nicht verw.):
		typ = stringextract('coreAssetType":"', '"', page)	
		pub =  stringextract('publicationService":', 'logo"', page)
		sender = stringextract('name":"', '"', pub)
		show = stringextract('show":', 'image"', page)
		show_id = stringextract('id":"', '"', show)
		title = stringextract('title":"', '"', show)
		
		sender = sender.replace("Das Erste", "ard")
		surl = base % (sender, show_id)

		#  new_url, msg = get_page(path=surl, GetOnlyRedirect=True) # nicht nötig
		new_url = surl
		PLog("coreAssetType: %s, sender: %s, show_id: %s, new_url: %s" % (typ, sender, show_id, new_url))
		
		if new_url and "SEASON" in typ:
			dirID = "resources.lib.ARDnew.ARDStartRubrik"
			fparams="&fparams={'title': '%s', 'path': '%s'}" %\
				(quote(title), quote(new_url))
			action="action=dirList&dirID=%s&fparams=%s"	% (dirID, fparams)
			PLog("action_Context: " + action)
			action=quote(action)
			xbmc.executebuiltin('RunAddon(%s, %s)'  % (ADDON_ID, action))
			exit()		
		
	# -----------------------------------					# Fehlschlag
	icon = R(ICON_INFO)
	msg1 = "Suche Serie zum Video:"
	msg2 = 'keine Serie gefunden.'				
	PLog(msg2)
	xbmcgui.Dialog().notification(msg1,msg2,icon,3000)				
	
#----------------------------------------------------------------























