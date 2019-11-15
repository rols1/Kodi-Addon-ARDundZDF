# -*- coding: utf-8 -*-
################################################################################
#			updater.py - Teil von Kodi-Addon-ARDundZDF
#
################################################################################
#	16.01.2019 erweitert mit Backup-Funktion für Addon-Cache.
#	03.05.2019 Backup-Funktion wieder entfernt, data-Verzeichnis ab
#		V1.4.0 im Kodi-Verzeichnis .kodi/userdata/addon_data/ardundzdf_data
#
################################################################################
import re, os, sys
import shutil						# Dir's löschen
import urllib2, zipfile, StringIO

import xbmc, xbmcgui, xbmcaddon

import resources.lib.util as util
PLog=util.PLog; get_page=util.get_page; stringextract=util.stringextract;
cleanhtml=util.cleanhtml;
 
ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')

ICON_OK = "icon-ok.png"				# gtk themes / Adwaita checkbox-checked-symbolic.symbolic.png
ICON_WARNING = "icon-warning.png"	# gtk themes / Adwaita dialog-warning-symbolic.symbolic.png
ICON_ERROR = "icon-error.png"		# gtk themes / Adwaita dialog-error.png
ICON_UPDATER = "icon-updater.png"	# gtk themes / Adwaita system-software-update.png
ICON_RELEASES = "icon-releases.png"	# gtk themes / Adwaita view-list-symbolic.symbolic.png
ICON_NEXT = "icon-next.png"			# gtk themes / Adwaita go-next-symbolic.symbolic.png 

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
			
		r = urllib2.urlopen(release_feed_url)
		page = r.read()					
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
		Log.Error('Suche nach neuen Versionen fehlgeschlagen: {0}'.format(repr(exception)))
		return ('', '', '')

################################################################################
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
	except:
		pass
	return (False, '', '', '', '', '')
            
################################################################################
def update(url, ver):
	PLog('update:')	
	
	if ver:		
		msg1 = 'Addon Update auf  Version {0}'.format(ver)
		msg2 = 'Update erfolgreich - weiter zum aktuellen Addon'  	# Kodi: kein Neustart notw.
		try:
			dest_path 	= xbmc.translatePath("special://home/addons/")
			PLog('Mark1')
			r 			= urllib2.urlopen(url)
			PLog('Mark2')
			zip_data	= zipfile.ZipFile(StringIO.StringIO(r.read()))
			PLog('Mark3')
			
			# save_restore('save')									# Cache sichern - entfällt, s.o.
			
			PLog(dest_path)
			PLog(ADDON_PATH)
			shutil.rmtree(ADDON_PATH)		# remove addon, Verzicht auf ignore_errors=True
			zip_data.extractall(dest_path)
				
			# save_restore('restore')								# Cache sichern	 - entfällt, s.o.
					
		except Exception as exception:
			msg1 = 'Update fehlgeschlagen'
			msg2 = 'Error: ' + str(exception)
												
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
	else:
		msg1 = 'Update fehlgeschlagen'
		msg2 =  'Version ' + ver + 'nicht gefunden!'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

################################################################################
# save_restore:  Cache sichern / wieder herstellen
#	funktioniert nicht unter Windows im updater-Modul - daher hierher verlagert
#	Aufrufer update (vor + nach Austausch)
# Windows-Problem: ohne Dir-Wechsel aus RESSOURCES_DIR Error 32 (belegter Prozess)
# 03.05.2019 Funktion wieder entfernt - s.o.

	
################################################################################# clean tag names based on your release naming convention
def cleanSummary(summary):
	
	summary = (summary.replace('&lt;','').replace('&gt;','').replace('/ul','')
		.replace('/li','').replace('\n', ' | '))
	summary =  (summary.replace('| ul |', ' | ').replace('/h3', '')
		.replace('&quot;', '"').replace('| li', '| ').replace('-&amp;gt;', '->'))
		
	return summary.lstrip()
