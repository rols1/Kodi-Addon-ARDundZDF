# -*- coding: utf-8 -*-

################################################################################
#				slides.py - Teil von Kodi-Addon-ARDundZDF
#			  Slideshow i.V.m. laufendem Kodi-Musik-Player
#
#	Struktur und Codeanteile aus:
#	https://gitlab.com/ronie/screensaver.picture.slideshow/blob/master/
#		resources/lib/gui.py (GPL-Lizens siehe dort)
#	
# 	s.a. HOW-TO:Script addon (Test-Script, XML-Code für Window, doModal)
# 		https://kodi.wiki/view/HOW-TO:Script_addon
# 	Scan Keys + rechte Maustaste s. KeyListener
#	Auswertung Keys s. img_update
################################################################################
# 	<nr>0</nr>										# Numerierung für Einzelupdate
#	Stand: 28.01.2023


# Python3-Kompatibilität:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from kodi_six import xbmcgui, xbmcaddon
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

# Standard:
import sys, os, hashlib
import copy, threading
from threading import Timer

PYTHON2 = sys.version_info.major == 2		# bisher keine import-Anpassung erford.
PYTHON3 = sys.version_info.major == 3
if PYTHON3:
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass


# Addonmodule 
from resources.lib.util import *
PLog('lade_Modul_slides:')

ADDON_ID     = 'plugin.video.ardundzdf'
SETTINGS    	= xbmcaddon.Addon(id=ADDON_ID)
PLog(SETTINGS)
PLog(ADDON_ID)

CWD  		= SETTINGS.getAddonInfo('path')		# working dir
SKINDIR  	= xbmc.getSkinDir()
PLog("CWD: " + CWD)
PLog("SKINDIR: " + SKINDIR)

#CACHEFOLDER = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
CACHEFOLDER = xbmc.translatePath(SETTINGS.getAddonInfo('profile'))
CACHEFILE   = os.path.join(CACHEFOLDER, '%s')
POS_FILE  	= os.path.join(CACHEFOLDER, 'position')
ASFILE      = xbmc.translatePath('special://profile/advancedsettings.xml')
IMAGE_TYPES = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.gif', '.pcx', '.bmp', '.tga', '.ico')
PLog("POS_FILE: " + POS_FILE)

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA

# Anpassung Kodi 20 Nexus: "3.0.0" -> "3."
if 	check_AddonXml('"xbmc.python" version="3.'):						# ADDON_DATA-Verzeichnis anpasen
	PLog('slides_python_3.x.x')
	ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
WATCHFILE		= os.path.join(ADDON_DATA, "merkliste.xml") 

DICTSTORE 		= os.path.join(ADDON_DATA, "Dict") 
STOPFILE 		= os.path.join(DICTSTORE, 'stop_slides') # s.a. PlayAudio


#----------------------------------------------------------------  
# https://kodi.wiki/view/WindowXML
class Slideshow(xbmcgui.WindowXMLDialog):
	def __init__( self, *args, **kwargs ):
		PLog(args, kwargs)
		pass

	def onInit(self):
		PLog('onInit')
		self._get_vars()
		self._get_settings()
		self._get_items()			# Bildverz. lesen
		self._get_offset()
		PLog('Pos.: %s' % str(self.pos))
		if self.items:
			# hide startup splash
			self._set_prop('Splash', 'hide')
			# start slideshow
			self._start_show(copy.deepcopy(self.items))
		else:
			_exit()

	def _get_vars(self):
		PLog('_get_vars')
		# get the slideshow window id
		self.winid    = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
		PLog('self.winid: ' + str(self.winid))
		self.pos	= 0
		self.stop   	= False

	def _get_settings(self):
		PLog('_get_settings')
		# read addon settings
		self.slides_type   = '2'
		self.slides_path   = SETTINGS.getSetting('pref_slides_path')
		PLog(self.slides_path)
		self.slides_time   = int(SETTINGS.getSetting('pref_slides_time'))
		PLog("slideshow_time: %d sec" % self.slides_time)								
		self.slides_name 	= '0'				# Anzeige Bildname/Ordner
		self.slides_music	= 'true'			# Player: Logo, Musik, Artist
		self.slides_bg 		= 'false'			# Hintergrund nicht zeigen
		# select image controls from the xml
		# 	hier ohne Skalierung
		self.image1 = self.getControl(1)
		self.getControl(99).setVisible(True) # mit Ordner-/Dateiname
		self.namelabel = self.getControl(99)	
		# Player: Logo, Musik, Artist
		if self.slides_music == 'true':
			self._set_prop('Music', 'show')

	def _start_show(self, items):
		PLog('_start_show')
		# we need to start the update thread after the deep copy of self.items finishes
		thread = img_update(data=self._get_items)
		thread.start()
		# start with image 1
		cur_img = self.image1
		order = [1,2]

		texturecache = False						# ohne bg n.b.
		# Schleife Bilder bis stop
		while os.path.exists(STOPFILE) == False:
			# iterate through all the images
			self.new_pos = self.pos
			for img in items[self.pos:]:
				#PLog("Bild: " + (img[0]))			# Debug
				if not xbmcvfs.exists(img[0]):		# vorsichtshalber
					continue
				# add image to gui
				cur_img.setImage(img[0],texturecache)
				
				ROOT, FOLDER = os.path.split(os.path.dirname(img[0]))
				# PLog("ROOT, FOLDER: %s, %s" % (ROOT, FOLDER))			# Debug
				FILE, EXT = os.path.splitext(os.path.basename(img[0]))
				NAME = FOLDER + ' | ' + FILE
				self.namelabel.setLabel(NAME)
                    
				# give xbmc some time to load the image
				xbmc.sleep(200) 
								
				# Schätzwert - mit den zusätzl. Timern 
				# KeyListener + img_update nicht exakt möglich:
				count = self.slides_time * 3  
				# display the image for the specified amount of time
				while os.path.exists(STOPFILE) == False and count > 0:
					count -= 1
					xbmc.sleep(200)
				# break out of the for loop if onScreensaverDeactivated is called
				if  os.path.exists(STOPFILE):
					PLog('stop_start_show')
					self.stop = True
					self._exit()			# bereinigen + Main()
					xbmc.executebuiltin('Container.NextSortMethod') # OK s.o.
					break
				self.new_pos += 1
			self.pos = 0			
			items = copy.deepcopy(self.items)

	def _get_items(self, update=False):
		PLog('_get_items')
		hexfile = checksum(self.slides_path) 
		PLog('image path: %s' % self.slides_path)
		PLog('update: %s' % update)
		# check: Verz. geändert?
		if (not xbmcvfs.exists(CACHEFILE % hexfile)) or update: # create a new cache 
			PLog('create cache')
			create_cache(self.slides_path, hexfile)
		self.items = self._read_cache(hexfile)
		PLog('items: %s' % len(self.items))
		if not self.items:
			# delete empty cache file
			if xbmcvfs.exists(CACHEFILE % hexfile):
				xbmcvfs.delete(CACHEFILE % hexfile)

	def _get_offset(self):							# Pos. holen	
		PLog('_get_offset')
		try:
			offset = xbmcvfs.File(POS_FILE)
			self.pos = int(offset.read())
			offset.close()
		except Exception as exception:
			PLog("_get_offset:" + str(exception))
			self.offset = 0

	def _save_offset(self):							# Pos. sichern	
		PLog('_save_offset')
		if not xbmcvfs.exists(CACHEFOLDER):
			xbmcvfs.mkdir(CACHEFOLDER)
		try:
			offset = xbmcvfs.File(POS_FILE, 'w')
			offset.write(str(self.new_pos))
			offset.close()
			PLog('Pos.: %s' % str(self.new_pos))
		except Exception as exception:
			PLog("_save_offset:" + str(exception))

	def _read_cache(self, hexfile):
		images = ''
		try:
			cache = xbmcvfs.File(CACHEFILE % hexfile)
			images = eval(cache.read())
			cache.close()
		except:
			pass
		return images

	def _set_prop(self, name, value):
		self.winid.setProperty('SlideView.%s' % name, value)

	def _clear_prop(self, name):
		self.winid.clearProperty('SlideView.%s' % name)

	def _exit(self):
		PLog('_exit')
		# on STOPFILE exit
		self.stop = True
		self._save_offset()
		# Eigenschaften der Controls löschen
		self._clear_prop('Music')
		self._clear_prop('Splash')
		self.close()
		del self
		PLog("_exit_done")


class img_update(threading.Thread):					# Bildverz. aktualisieren
	def __init__( self, *args, **kwargs ):
		self._get_items =  kwargs['data']
		threading.Thread.__init__(self)
		
	def run(self):
		while os.path.exists(STOPFILE) == False:
			PLog('run_Update_Bildverz.')
			self._get_items(True)
			count = 0
			while count <= 1000: # Check Bildverz.
				xbmc.sleep(300) # höher Werte begünstigen Kodi-Klemmer bei Abbruch
				#PLog('Sleep %d' % count)
				count += 1
				pressed_key = KeyListener.record_key()	# string
				# PLog(xbmc.Player().isPlaying())		# Debug
				if xbmc.Player().isPlaying() == 0:		# Ende Player = ESC
					pressed_key = "61467"
				#PLog("pressed_Key: "+  pressed_key)
				# Bildsteuerung entfällt - Kodi reicht Keys hier weiter
				#	an Player: 	61570=Pfeil links (seek step back), 
				#				61571=Pfeil rechts (seek step forward),
				#				61472=Blank (Pause/Weiter)
				#				61591=F8 (Mute)
				#				61568=Pfeil hoch (Seek step forward 10min)
				#				61569=Pfeil runter (Seek step back 10min)
				#				61952/61532=AltGr/Backslash (Schalter Fullscreen/Window)
				if pressed_key==None or pressed_key in ['61570','61571','61472','61591','61568','61569','61952','61532']:
					continue
				else:									# 61467=ESC od. andere	
					PLog("stop_run_pressed_Key: "+ pressed_key)	
					self.stop=True
					with open(STOPFILE, 'w'):	
						pass				
						return

	def _exit(self):	# exit bei STOPFILE
		with open(STOPFILE, 'w'):	# STOPFILE erneut anlegen, verhind. Rekursion 
			pass				
		self.stop = True


# s. https://forum.kodi.tv/showthread.php?tid=205339
#	https://codedocs.xyz/xbmc/xbmc/group__kodi__key__action__ids.html
# Auswertung rechte Maustaste: für Abbruch bei Raspi-Mausbedienung,
#	gegen übergeordneten Kodi-Klemmer (Klick -> PreviosMenu -> 
#	Rekursion des KeyListeners	
class KeyListener(xbmcgui.WindowXMLDialog):
	TIMEOUT = 1
	HEADING = 401
	ACTION_MOUSE_LEFT_CLICK = 100
	ACTION_MOUSE_RIGHT_CLICK = 101
	
	def __new__(cls):
		try: 
			version = xbmc.getInfoLabel('system.buildversion')
			if version[0:2] >= "17":
				return super(KeyListener, cls).__new__(cls, "DialogNotification.xml", "")
			else:
				return super(KeyListener, cls).__new__(cls, "DialogKaiToast.xml", "")
		except:
			PLog("NOTICE = KeyListener no found")

	def __init__(self):
		self.key = None

	def onInit(self):
		try:
			self.getControl(self.HEADING).addLabel("")
		except AttributeError:
			self.getControl(self.HEADING).setLabel("")

	def onAction(self, action):
		actionId = action.getId() 
		if actionId == self.ACTION_MOUSE_RIGHT_CLICK:
			self.key = "61467"				# rechte Maustaste = ESC
		else:		
			code = action.getButtonCode()
			self.key = None if code == 0 else str(code)
			self.close()

	@staticmethod
	def record_key():
		dialog = KeyListener()
		timeout = Timer(KeyListener.TIMEOUT, dialog.close)
		timeout.start()
		dialog.doModal()
		timeout.cancel()
		key = dialog.key		
		#klick = dialog.klick	# hier nicht verfügbar
		#PLog(klick)
		del dialog
		return key        
		
#---------------------------------------------------------------- 
# Bilder laden, Cache
#----------------------------------------------------------------  
def checksum(path):
	path = path.encode('utf-8')				# py_encode wirkt hier nicht in Matrix
	return hashlib.md5(path).hexdigest()

def create_cache(path, hexfile):
	images = walk(path)
	PLog("CACHEFOLDER: " + CACHEFOLDER)
	if not xbmcvfs.exists(CACHEFOLDER):
		xbmcvfs.mkdir(CACHEFOLDER)
	# remove old cache files
	dirs, files = xbmcvfs.listdir(CACHEFOLDER)
	for item in files:
		if item != 'settings.xml':
			xbmcvfs.delete(os.path.join(CACHEFOLDER,item))
	if images:
		# create index file
		try:
			cache = xbmcvfs.File(CACHEFILE % hexfile, 'w')
			cache.write(str(images))
			cache.close()
		except:
			PLog('failed to save cachefile')

def get_excludes():
	regexes = []
	if xbmcvfs.exists(ASFILE):
		try:
			tree = etree.parse(ASFILE)
			root = tree.getroot()
			excludes = root.find('pictureexcludes')
			if excludes is not None:
				for expr in excludes:
					regexes.append(expr.text)
		except:
			pass
	return regexes

def walk(path):
	images = []
	folders = []
	excludes = get_excludes()
	# multipath support
	if path.startswith('multipath://'):
		# get all paths from the multipath
		paths = path[12:-1].split('/')
		for item in paths:
			folders.append(urllib.unquote_plus(item))
	else:
		folders.append(path)
	for folder in folders:							# Verzeichnisse rekursiv
		if xbmcvfs.exists(xbmc.translatePath(folder)):
			# get all files and subfolders
			dirs,files = xbmcvfs.listdir(folder)
			# PLog(dirs)
			PLog('dirs: %s, files: %s' % (len(dirs), len(files)))
			# natural sort
			convert = lambda text: int(text) if text.isdigit() else text
			alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
			files.sort(key=alphanum_key)
			for item in files:
				#check pictureexcludes from as.xml
				fileskip = False
				if excludes:
					for string in excludes:
						regex = re.compile(string)
						match = regex.search(item)
						if match:
							fileskip = True
							break
				# filter out all images
				if os.path.splitext(item)[1].lower() in IMAGE_TYPES and not fileskip:
					images.append([os.path.join(folder,item), ''])
			for item in dirs:
				#check pictureexcludes from as.xml
				dirskip = False
				if excludes:
					for string in excludes:
						regex = re.compile(string)
						match = regex.search(item)
						if match:
							dirskip = True
							break
				# recursively scan all subfolders
				if not dirskip:
					images += walk(os.path.join(folder,item,'')) # make sure paths end with a slash
		else:
			PLog('Verz. %s nicht gefunden' % folder)
	return images
		
		
		
		
