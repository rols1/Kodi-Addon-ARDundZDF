# -*- coding: utf-8 -*-
################################################################################
#			updater.py - Teil von Kodi-Addon-ARDundZDF
#
################################################################################
#	16.01.2019 erweitert mit Backup-Funktion für Addon-Cache.
#	03.05.2019 Backup-Funktion wieder entfernt, data-Verzeichnis ab
#		V1.4.0 im Kodi-Verzeichnis .kodi/userdata/addon_data/ardundzdf_data
#	31.10.2019 Migration Python3 Modul future
#	17.11.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
# 	18.03.2020 adjust_AddonXml: Anpassung python-Version an Kodi-Version
################################################################################

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

# Standard:
import shutil						# Dir's löschen
import zipfile, re
import io 							# Python2+3 -> update() io.BytesIO für Zipfile

# Addonmodule + Funktionsziele (Script util_imports.py):
import resources.lib.util as util
PLog=util.PLog; get_page=util.get_page; stringextract=util.stringextract;
cleanhtml=util.cleanhtml; RLoad=util.RLoad; RSave=util.RSave; 
 
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')

FEED_URL = 'https://github.com/{0}/releases.atom'

################################################################################
TITLE = 'ARD und ZDF'
REPO_NAME		 	= 'Kodi-Addon-ARDundZDF'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME

BACKPUP_DIR			= "data"		# Cache: zu sichern vor Update / zu restaurieren nach Update
RESSOURCES_DIR		= os.path.join("%s/resources") % ADDON_PATH

################################################################################

# This gets the release name
def get_latest_version():
	PLog('get_latest_version:')
	try:
		# https://github.com/rols1/Kodi-Addon-ARDundZDF/releases.atom
		# releases.atom liefert Releases-Übersicht als xml-Datei 
		release_feed_url = ('https://github.com/{0}/releases.atom'.format(GITHUB_REPOSITORY))
		PLog(release_feed_url)
			
		r = urlopen(release_feed_url)
		page = r.read()					
		page=page.decode('utf-8')				
		PLog(len(page))
		# PLog(page[:800])

		link	= stringextract('<link rel', '"/>', page)			# ../releases/tag/0.2.9"/
		tags 	= link.split('/')
		tag = tags[-1]												# 0.2.9
		title	= stringextract('<title>', '</title>', page)		# 
		content	= stringextract('li&gt;', '</content>', page)
		summary = cleanSummary(content)
		# PLog("content: "  + content)
		# PLog(link); PLog(title); PLog(summary); PLog(tag);  
		return (title, summary, tag)
	except Exception as exception:
		PLog(str(exception))
		return ('', '', '')

################################################################################
# decode latest_version (hier bytestring) erforderlich für Pfad-Bau in 
def update_available(VERSION):
	PLog('update_available:')

	# save_restore('save')					# Test-Session save_restore
	# save_restore('restore')
	# return (False, '', '', '', '', '')
	
	try:
		title, summ, tag = get_latest_version()
		PLog(tag); 	# PLog(latest_version_str); PLog(summ);
		
		if tag:
			# wir verwenden auf Github die Versionierung nicht im Plugin-Namen
			# latest_version  = title 
			latest_version  = tag		# Format hier: '1.4.1'

			current_version = VERSION
			int_lv = tag.replace('.','')
			int_cv = current_version.replace('.','')
			PLog('Github: ' + latest_version); PLog('lokal: ' + current_version); 
			# PLog(int_lv); PLog(int_cv)
			return (int_lv, int_cv, latest_version, summ, tag)
	except Exception as exception:	
		PLog(str(exception))
	return (False, '', '', '', '', '')
            
################################################################################
def update(url, ver):
	PLog('update:')	
	
	if ver:		
		msg1 = 'Addon Update auf  Version {0}'.format(ver)
		msg2 = 'Update erfolgreich - weiter zum aktuellen Addon'  	# Kodi: kein Neustart notw.
		try:
			dest_path 	= xbmc.translatePath("special://home/addons/")
			r 			= urlopen(url)
			PLog('Mark1')
			zip_data	= zipfile.ZipFile(io.BytesIO(r.read()))
			PLog('Mark2')
			
			# save_restore('save')									# Cache sichern - entfällt, s.o.
			
			PLog(dest_path)
			PLog(ADDON_PATH)
			shutil.rmtree(ADDON_PATH)		# remove addon, Verzicht auf ignore_errors=True
			PLog('Mark3')
			zip_data.extractall(dest_path)
				
			# save_restore('restore')								# Cache sichern	 - entfällt, s.o.
			PLog('Mark4')
			adjust_AddonXml()										# addon.xml an Kodi-Verson anpassen
					
		except Exception as exception:
			msg1 = 'Update fehlgeschlagen'
			msg2 = 'Error: ' + str(exception)
												
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
	else:
		msg1 = 'Update fehlgeschlagen'
		msg2 =  'Version ' + ver + 'nicht gefunden!'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

################################################################################
# adjust_AddonXml:  Anpassung der python-Version in der neu installierten 
#	addon.xml an die akt. Kodi-Version. Passende addon.xml bleibt unver-
#	ändert. Da Kodi die addon.xml erst bei Neustart od. Addon-Installation
#	prüft, muss die Änderung nicht bereits vor dem Speichern erfolgen.
# 
# Voraussetzung für replace: die Einträge in addon.xml entsprechen exakt 
#	den Marken repl_leia + repl_matrix
# 
# Nach Beendigung des Updates wird bei jedem Laden des Moduls util
#	in check_AddonXml das Verzeichnis ADDON_DATA angepasst (s. dort)
#
def adjust_AddonXml():
	PLog('adjust_AddonXml:')
	repl_leia 	= 'addon="xbmc.python" version="2.25.0"'
	repl_matrix = 'addon="xbmc.python" version="3.0.0"'
	KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')
	path = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/addon.xml')
	PLog(KODI_VERSION); PLog(path)
	
	page = RLoad(path, abs_path=True)
	change = False
	if KODI_VERSION.startswith('19.'):					# Kodi Matrix
		if repl_leia in page:
			page = page.replace(repl_leia, repl_matrix)
			page = py2_encode(page)
			PLog('adjust_AddonXml: ersetze %s durch %s' % (repl_leia, repl_matrix))
			RSave(path, page)
			change = True	
	else:												# Kodi <= Leia
		if repl_matrix in page:
			page = page.replace(repl_matrix, repl_leia)
			page = py2_encode(page)
			PLog('adjust_AddonXml: ersetze %s durch %s' % (repl_matrix, repl_leia))
			RSave(path, page)		
			change = True	
	if change == False:
		PLog(u'adjust_AddonXml: addon.xml unverändert')
	return	

################################################################################
# save_restore:  Cache sichern / wieder herstellen
#	funktioniert nicht unter Windows im updater-Modul - daher hierher verlagert
#	Aufrufer update (vor + nach Austausch)
# Windows-Problem: ohne Dir-Wechsel aus RESSOURCES_DIR Error 32 (belegter Prozess)
# 03.05.2019 Funktion wieder entfernt - s.o.
	
################################################################################# 
# clean tag names based on your release naming convention
def cleanSummary(summary):
	
	summary = (summary.replace('&lt;','').replace('&gt;','').replace('/ul','')
		.replace('/li','').replace('\n', ' | '))
	summary =  (summary.replace('| ul |', ' | ').replace('/h3', '')
		.replace('&quot;', '"').replace('| li', '| ').replace('-&amp;gt;', '->'))
		
	return summary.lstrip()
