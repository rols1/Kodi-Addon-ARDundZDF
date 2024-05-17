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
#	13.04.2020 Aktualisierung adjust_AddonXml
# 	28.01.2023 Aktualisierung adjust_line für Kodi 20 Nexus
################################################################################
# 	<nr>3</nr>								# Numerierung für Einzelupdate
#	Stand: 17.05.2024

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
import shutil						# Dir's löschen
import zipfile, re
import io 							# Python2+3 -> update() io.BytesIO für Zipfile

from resources.lib.util import *
 
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')

FEED_URL = 'https://github.com/{0}/releases.atom'

################################################################################
TITLE = 'ARD und ZDF'
REPO_NAME		 	= 'Kodi-Addon-ARDundZDF'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME

RESSOURCES_DIR		= os.path.join(ADDON_PATH, "resources") 

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
		
		#PLog("content: "  + content)
		# PLog(link); PLog(title); PLog(summary); PLog(tag);  
		return (py2_encode(title), py2_encode(summary), py2_encode(tag))
	except Exception as exception:
		PLog(str(exception))
		return ('', '', '')

################################################################################
# Abgleich Github-tag mit Addon-Version 
def update_available(VERSION):
	PLog('update_available:')
	
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
												
		MyDialog(msg1, msg2, '')
	else:
		msg1 = 'Update fehlgeschlagen'
		msg2 =  'Version ' + ver + 'nicht gefunden!'
		MyDialog(msg1, msg2, '')

################################################################################
# adjust_AddonXml:  Anpassung der python-Version in der neu installierten 
#	addon.xml an die akt. Kodi-Version. Passende addon.xml bleibt unver-
#	ändert. Da Kodi die addon.xml erst bei Neustart od. Addon-Installation
#	prüft, muss die Änderung nicht bereits vor dem Speichern im zip erfolgen.
#
#   Voraussetzung: die Einträge für "addon id" und "import addon" müssen
#		sich jeweils in einer zeile befinden.

##	Python-Versionen s. https://kodi.wiki/view/Addon.xml#Dependency_versions
#		Leia / Matrix		version="2.25.0" / version="3.0.0"
#	Addon-Version (Bsp.):	version="2.8.5" /  version="2.8.5+matrix"
# 
# Nach Beendigung des Updates wird bei jedem Laden des Moduls util
#	in check_AddonXml das Verzeichnis ADDON_DATA angepasst (s. dort)
#  
def adjust_AddonXml():
	PLog('adjust_AddonXml:')
	
	path = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/addon.xml')
	PLog(path)
	page = RLoad(path, abs_path=True)
	change = False
	new_lines = []
	lines = page.splitlines()
	
	for line in lines:
		new_line = line
		# PLog(line)		# Debug
		if 'addon="xbmc.python"' in line or 'addon id=' in line:
			new_line = adjust_line(line)
			if new_line != line:
				change = True
				PLog('adjust_AddonXml_oldline: %s' % line)
				PLog('adjust_AddonXml_newline: %s' % new_line)
				new_line = line.replace(line, new_line)
		new_lines.append(new_line)	
	
	if change == False:
		PLog(u'adjust_AddonXml: addon.xml unverändert')
	else:
		page = '\n'.join(new_lines)
		RSave(path, page)		
	return	

#------------------------------
# 12.02.2023 Punkt in re.search(u'(\d+).' enfernt (ValueError)
def adjust_line(line):
	PLog('adjust_line:')
	KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')
	PLog(KODI_VERSION)
	new_line = line

	try:
		vers = re.search(r'(\d+)', KODI_VERSION).group(0)
	except Exception as exception:
		PLog(str(exception))
		vers = "19"														# Default Matrix
	vers = int(vers)
	PLog("vers: %d" % vers)
	
	if vers < 19:														# Leia, Krypton, ..
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '2.25.0')				
		if 'addon id=' in line:
			new_line = line.replace('+matrix', '')						# ev. Downgrade				
			new_line = line.replace('+nexus', '')						# ev. Downgrade
	
	if 	vers == 19:														# Matrix
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '3.0.0')
		if 'addon id=' in line:
			addon_ver = stringextract('version="', '"', line)
			if 'matrix' not in line:									
				new_line = line.replace(addon_ver, '%s+matrix' % addon_ver)	
	if 	vers == 20:														# Nexus
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '3.0.1')
		if 'addon id=' in line:
			addon_ver = stringextract('version="', '"', line)
			if 'nexus' not in line:									
				new_line = line.replace(addon_ver, '%s+nexus' % addon_ver)	
				
								
	return new_line													

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
