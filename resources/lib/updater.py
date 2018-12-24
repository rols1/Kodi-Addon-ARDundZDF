# -*- coding: utf-8 -*-
################################################################################
import re, os, sys
import shutil						# Dir's löschen
import requests, zipfile, StringIO

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
################################################################################

# This gets the release name
def get_latest_version():
	PLog('get_latest_version:')
	try:
		# https://github.com/rols1/ARDundZDF/releases.atom
		# releases.atom liefert Releases-Übersicht als xml-Datei 
		release_feed_url = ('https://github.com/{0}/releases.atom'.format(GITHUB_REPOSITORY))
		PLog(release_feed_url)
		
		r = requests.get(release_feed_url, stream=True)
		page = r.content	
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
		msg1 = 'Plugin Update auf  Version {0}'.format(ver)
		msg2 = 'Update erfolgreich - weiter zum aktuellen Plugin'  # Kodi: kein Neustart notw.
		try:
			r 			= requests.get(url, stream=True)
			zip_data	= zipfile.ZipFile(StringIO.StringIO(r.content))
			dest_path 	= xbmc.translatePath("special://home/addons/")
			PLog(dest_path)
			PLog(ADDON_PATH)
			shutil.rmtree(ADDON_PATH)		# hier Verzicht auf ignore_errors=True
			zip_data.extractall(dest_path)	
		except Exception as exception:
			msg1 = 'Update fehlgeschlagen'
			msg2 = 'Error: ' + str(exception)		
					
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
	else:
		return ObjectContainer(header='Update fehlgeschlagen', message='Version ' + ver + 'nicht gefunden!')
		msg1 = 'Update fehlgeschlagen'
		msg2 =  'Version ' + ver + 'nicht gefunden!'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

################################################################################
	
# clean tag names based on your release naming convention
def cleanSummary(summary):
	summary = summary.replace('/li','')
	summary = summary.replace('/ul','')
	summary = summary.replace('li','')
	summary = summary.replace('&amp;','&')
	summary = summary.replace('&gt;','')
	summary = summary.replace('&lt;','')
	summary = summary.replace('&lt;','')

	# summary = summary.replace('\n',' ')
	summary = summary.replace('ul','')
	summary = summary.replace('/h3','')
	
	return summary.lstrip()
