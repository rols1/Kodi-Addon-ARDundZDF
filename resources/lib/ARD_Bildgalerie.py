# -*- coding: utf-8 -*-
################################################################################
#			ARD_Bildgalerie.py - Part of ARDundZDF - Plugin Kodi-Version
#
################################################################################
	
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import sys, os, subprocess, urllib, urllib2, datetime, time
import json, re

import resources.lib.util as util	# (util_imports.py)
PLog=util.PLog; home=util.home; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
getDirZipped=util.getDirZipped; Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
UtfToStr=util.UtfToStr; addDir=util.addDir; get_page=util.get_page; img_urlScheme=util.img_urlScheme; 
R=util.R; RLoad=util.RLoad; RSave=util.RSave; GetAttribute=util.GetAttribute; repl_dop=util.repl_dop; 
repl_char=util.repl_char; repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; 
DirectoryNavigator=util.DirectoryNavigator; stringextract=util.stringextract; blockextract=util.blockextract; 
teilstring=util.teilstring; cleanhtml=util.cleanhtml; decode_url=util.decode_url; 
unescape=util.unescape; transl_doubleUTF8=util.transl_doubleUTF8; make_filenames=util.make_filenames; 
transl_umlaute=util.transl_umlaute; transl_json=util.transl_json; humanbytes=util.humanbytes; 
CalculateDuration=util.CalculateDuration; time_translate=util.time_translate; seconds_translate=util.seconds_translate; 
get_keyboard_input=util.get_keyboard_input; transl_wtag=util.transl_wtag; xml2srt=util.xml2srt; 
ReadFavourites=util.ReadFavourites; get_summary_pre=util.get_summary_pre; get_playlist_img=util.get_playlist_img; 
get_startsender=util.get_startsender; PlayVideo=util.PlayVideo; PlayAudio=util.PlayAudio; 


ADDON_ID      	= 'plugin.video.ardundzdf'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%sardundzdf_data") % USERDATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
ClearUp(SLIDESTORE, 86400)	# Files + Verz. im SLIDESTORE älter als 1 Tag löschen

# ----------------------------------------------------------------------
# Aufrufer: Search - path=eine der Folgeseiten	
def page(name, path, offset):		
	PLog('page ARD_Bildgalerie:');
	li = xbmcgui.ListItem()
	li = home(li, ID='ARD')				# Home-Button
	
	page, msg = get_page(path=path)	
	if page == '':						
		msg1 = 'Fehler in Suche: %s' % title
		msg2 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
	PLog(len(page))
				
	entries = blockextract('div class="teaser',  page)
	PLog(len(entries))
	if len(entries) == 0:
		msg1 = 'keine weitere Bilderserie gefunden'
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
					
	for rec in entries:
		headline =  stringextract('class="headline">', '</h3>', rec)
		href =  stringextract('href="', '"', headline)
		title =  cleanhtml(headline)
		PLog(href[:44])
		teasertext =  stringextract('class="teasertext">', '</a></p>', rec)
		# PLog(teasertext)
		teasertext = cleanhtml(teasertext)
		teasertext = unescape(teasertext)
		teasertext = teasertext.replace('Bild lädt...', '')
		summ = teasertext
		title = cleanhtml(title)
		# PLog(teasertext); PLog(title)
		tag = ''
		if 'zur  Bildergalerie' in teasertext:
			summ = teasertext.split('zur  Bildergalerie')[0]
			tag = teasertext.split('zur  Bildergalerie')[1]
				
		title = UtfToStr(title)
		summ = UtfToStr(summ)
		tag = UtfToStr(tag)
		
		PLog(title); PLog(summ); PLog(tag) 
		fparams="&fparams={'title': '%s', 'path': '%s'}" % (urllib2.unquote(title), urllib2.unquote(href))
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARD_Bildgalerie.Hub", 
			fanart=R('ard-bilderserien.png'), thumb=R('ard-bilderserien.png'), fparams=fparams, summary=summ, tagline=tag)

	# xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	xbmcplugin.endOfDirectory(HANDLE)
#-----------------------
# 02.09.2018 SSL-Fehler mit HTTP.Request - Umstellung auf get_page mit urllib2.Request.
#	Dafür get_page um Alternative mit urllib2.Request + SSLContext erweitert.
#  PhotoObject fehlt in kodi - wir speichern die Bilder in SLIDESTORE und
#	übergeben an xbmc.executebuiltin('SlideShow..
#  ClearUp in SLIDESTORE s. Modulkopf
def Hub(title, path):		
	PLog('Hub: %s' % path)
	li = xbmcgui.ListItem()
	
	page, msg = get_page(path)						# Seite laden	
	if page == '':	
		xbmcgui.Dialog().ok(ADDON_NAME, msg, '', '')
		return li							
	PLog(len(page))
	
	if '//www.hessenschau.de' in path:			# Schema Hessenschau
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_hessenschau(page)
	if '//www.ard.de' or '//www.tagesschau.de' in path:					# Schema ARD
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_ard(page)
	if '//www.br.de' in path:					# Schema BR
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_br(page)
	if '//www.radiobremen.de' in path:			# Schema Bremen
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_bremen(page)
	if 'swr.de' in path:						# Schema Südwestfunk	//www.swr.de, //swr.de
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_swr(page)
	if '//www.daserste.de' in path:			# Schema Das Erste
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_daserste(page)
	if '//www.tagesschau.de' in path:			# Schema Das Erste
		href_rec, summ_rec, picnr_rec, cr_rec = get_pics_tagesschau(page)
		
		
	PLog('Bilder: ' + str(len(href_rec)))
	if len(href_rec) == 0:
		msg1 = 'keine Bilder gefunden zu:'
		msg2 = title
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
			
	fname = path.split('/')[-1]				# Ablage: Bildname = Pfadende + Bildnr
	fname = make_filenames(fname)
	fpath = '%s/%s' % (SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = 'Bildverzeichnis konnte nicht erzeugt werden:'
			msg2 = "%s/%s" % (SLIDESTORE, fname)
			PLog(msg1); PLog(msg2); 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li	
		
	for i in range (len(href_rec)):
		href=href_rec[i]; summ=summ_rec[i]; picnr=picnr_rec[i]; cr=cr_rec[i]							
		# PLog(href); PLog(summ); PLog(picnr); PLog(cr)
		if href:
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			pic_name 	= 'Bild_%04d.jpg' % (i+1)	# Bildname
			local_path 	= "%s/%s" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d | %s" % (i+1, summ)
			PLog("Bildtitel: " + title)
			title = unescape(title)
			title = UtfToStr(title)
			
			thumb = ''
			local_path = os.path.abspath(local_path)
			if os.path.isfile(local_path) == False:			# schon vorhanden?
				try:
					urllib.urlretrieve(href, local_path)
					thumb = local_path
				except Exception as exception:
					PLog(str(exception))			
			else:		
				thumb = local_path
				
			if thumb:
				fparams="&fparams={'path': '%s', 'single': 'True'}" % urllib2.quote(local_path)
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.ARD_Bildgalerie.SlideShow", 
					fanart=thumb, thumb=thumb, fparams=fparams)
				i=i+1
			
	if i > 0:		
		fparams="&fparams={'path': '%s'}" % urllib2.quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="resources.lib.ARD_Bildgalerie.SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern

#-----------------------
def SlideShow(path, single=None):
	PLog('SlideShow: ' + path)
	local_path = os.path.abspath(path)
	if single:							# Einzelbild	
		return xbmc.executebuiltin('ShowPicture(%s)' % local_path)
	else:
		PLog(local_path)
		return xbmc.executebuiltin('SlideShow(%s, %s)' % (local_path, 'notrandom'))
	 
#-----------------------
def get_pics_hessenschau(page):		# extrahiert Bildergalerie aus Hessenschau-Seite
	PLog('get_pics_hessenschau')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]
	
	slider = stringextract('data-hr-slider-dynamic', '<div class', page)
	# PLog(slider)
	href_items =  stringextract('url":"', '"', slider)
	# PLog(href_items)
	try:
		inline = HTTP.Request(href_items).content		# Bildbeschreibungen ausgelagert, können fehlen
		inline_items = blockextract('gallery__imageHeadline', inline)
	except:
		inline_items = ''
	PLog(len(inline_items))
	
	href_next = '123'					#  href in control enthält Link der Folgeseite, Schluss: #
	i=0
	while href_next:					# 1. Seite + Folgeseiten auswerten
		control =  stringextract('gallery__control--right', '</div>', page)
		href_next =  stringextract('href="', '#', control)	# endet mit #
		PLog(href_next)
		# pic_16to9 	= stringextract('twitter:image" content="', '"', page)
		pic_pre		= stringextract('centerHorizontal--absolute" src="', '"', page)	# orig. Vorschau
		pic_retina	= ''
		data_set	= stringextract('data-srcset=', '</div>', page)		# dahinter mehr Sets (Verweise)
		data_set	= blockextract('http', data_set)
		pic_href = ''
		for pic in data_set:
			# Alternativen: "medium.jpg", "v-Xto9.jpg" 
			if "retina.jpg" in pic: 		# beste Darst. in  Webclient 2.7.0
				pic_href = pic.split(' ')[0]# Bsp. ..Xto9.jpg 646w
				PLog(pic_href)
				break
				
		if 	pic_href == '':
			pic_href = data_set[-1]			# Fallback: letztes Bild aus dem Set, Alternative:
			pic_href = pic_href.split(' ')[0]	#  twitter-pic aus head (meta)
			
		descr = inline_items[i]			# 4 Zeilen + Leerzeilen dazwischen
		# PLog(descr)
		pic_nr =  stringextract('headline">', '</h3>',descr)
		pic_nr = pic_nr.strip()
		summ   =  stringextract('copytext">', '</p>',descr)
		summ   =  cleanhtml(summ)
		summ   =  unescape(summ)
		cr = 'Bildrechte: ' + stringextract('&copy;', '</p>',descr)		# Copyright
								
		PLog(pic_nr); PLog(summ); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		if href_next == '':
			break
		page = HTTP.Request(href_next).content		# nächste Seite laden				
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec

#-----------------------
def get_pics_ard(page):		# extrahiert Bildergalerie aus ARD-Seite
	PLog('get_pics_ard')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]
	
	page =  stringextract('data-ctrl-slidable=', 'controls sliding',page)
	records = blockextract('img hideOnNoScript',  page)
	
	i=0
	for rec in records:	
		pic_href =  'http://www.ard.de'+ stringextract('img" src="', '"', rec)
		pic_href = pic_href.replace('/512', '/1024') # man. Anpassung möglich
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		summ   =  stringextract('alt="', '"',rec) 	 # cr in summ enthalten
		summ   =  unescape(summ)
		cr = summ							# Titel: "Bild %s | %s" % (picnr, cr)
								
		PLog(pic_nr); PLog(summ); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec

#-----------------------
def get_pics_br(page):		# extrahiert Bildergalerie aus Bayern-Seite
	PLog('get_pics_br')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]
	
	json_url = 'http://www.br.de' + stringextract('data-gallery-json-url="', '"', page)	
	page = HTTP.Request(json_url).content			# Bilder-Links von json-Seite laden
	records = blockextract('permalink":',  page)
	
	i=0
	for rec in records:	
		urls = 	blockextract('"url":',  rec)	# versch. Bildformate
		url  = 	urls[-1]						# größtes Format am Schluss
		pic_href =  'http:'+ stringextract('url": "', '"', url)	# Bsp. "url": "//www.br.de/presse/..
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		summ   =  stringextract('"textAlt": "', '"',rec)
		summ   =  unescape(summ)
		cr = summ							# Titel: "Bild %s | %s" % (picnr, cr),
								
		PLog(pic_nr); PLog(summ); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec
#-----------------------
def get_pics_bremen(page):		# extrahiert Bildergalerie aus Bremen-Seite
	PLog('get_pics_bremen')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]

	page =  stringextract('bildgalerie-scroll-box', '</ul>',page)
	records = blockextract('<li><img',  page)
	
	i=0
	for rec in records:	
		pic_href =  'http://www.radiobremen.de'+ stringextract('src="', '"', rec)
		pic_href = pic_href.replace('-bildergaleriethumb.jpg', '-slideshow.jpg') # s. id="grosses_bild"
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		summ   =  stringextract('alt="', '"',rec) 	 # cr in summ enthalten
		summ   =  unescape(summ)
		cr = summ							# Titel: "Bild %s | %s" % (picnr, cr)
								
		PLog(pic_nr); PLog(summ); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec

#-----------------------
def get_pics_swr(page):		# extrahiert Bildergalerie aus SWR-Seite
	PLog('get_pics_swr')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]

	page1 =  stringextract('bildgalerie-scroll-box', '</ul>',page)
	records = blockextract('<li><img',  page1)
	PLog('records: ' + str(len(records)))
	
	i=0
	for rec in records:	
		pic_href =  'http://www.swr.de'+ stringextract('src="', '"', rec)
		pic_href = pic_href.replace('-bildergaleriethumb.jpg', '-slideshow.jpg') # s. id="grosses_bild"
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		summ   =  stringextract('alt="', '"',rec) 	 # cr in summ enthalten
		summ   =  unescape(summ)
		cr = summ							# Titel: "Bild %s | %s" % (picnr, cr)
								
		PLog(pic_nr); PLog(summ); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
		
	if len(href_rec) == 0:						# 2. Variante, Blöcke data-ctrl-gallerylayoutable
		records = blockextract('data-ctrl-gallerylayoutable',  page)
		PLog('records: ' + str(len(records)))		
		for rec in records:	
			pics = stringextract('<img src', '>',rec)
			pics = blockextract('https', pics)			# Set verschied. Größen
			summ = ''
			try:
				PLog(pics[-1])							# letztes = größtes
				summ   =  stringextract('teasertext">', '</p>',rec) # kann fehlen, s.o. (alt)
				pic_href = re.search(r'https(.*)jpg',pics[-1]).group(0)
			except:
				continue
			
			pic_nr = "%s/%s" % (str(i+1), str(len(records)))
			if summ == '':
				summ   =  stringextract('alt="', '"', pics[-1]) 
			summ   =  unescape(summ)
			cr = summ							# Titel: "Bild %s | %s" % (picnr, cr)
									
			PLog(pic_nr); PLog(summ); PLog(pic_href);
			href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
			i=i+1	
			
	if len(href_rec) == 0:						# 3. Variante, Blöcke class="mediagallery-backlink"
		records = blockextract('class="mediagallery-backlink"',  page)
		PLog('records: ' + str(len(records)))
		for rec in records:	
			pic_href = stringextract('itemprop="url" href="', '"', rec)
			pic_nr = "%s/%s" % (str(i+1), str(len(records)))
			summ   =  stringextract('description">', '<',rec) 	
			summ   =  unescape(summ.strip())
			cr = summ							# Titel: "Bild %s | %s" % (picnr, cr)
									
			PLog(pic_nr); PLog(summ); PLog(pic_href);
			href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
			i=i+1		
						
	return href_rec, summ_rec, picnr_rec, cr_rec

#-----------------------
def get_pics_daserste(page):		# extrahiert Bildergalerie aus Das Erste-Seite
	PLog('get_pics_daserste')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]

	page =  stringextract('div data-ctrl-slidable=', 'id="footer">',page)
	records = blockextract('class="mediaLink',  page)
	
	i=0
	for rec in records:	
		pic_href =   'http://www.daserste.de' + stringextract("'xl':{'src':'", "'", rec)	# img data set
		PLog(pic_href)
		if  pic_href == 'http://www.daserste.de':
			pic_href =  'http://www.daserste.de' + stringextract('src="', '"', rec)
			pic_href = pic_href.replace('-bildergaleriethumb.jpg', '-slideshow.jpg') # s. id="grosses_bild"
		
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		summ   =  stringextract('teasertext">', '</p>',rec) # kann fehlen, s.o. (alt)
		summ   =  summ.strip()
		if summ == '':
			summ   =  stringextract('alt="', '"',rec) 	 
		summ   =  unescape(summ)
		cr = stringextract('title="', '"',rec) 					# Titel: "Bild %s | %s" % (picnr, cr)
								
		PLog(pic_nr); PLog(summ[:40]); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec
#-----------------------
def get_pics_tagesschau(page):		# extrahiert Bildergalerie aus www.tagesschau.de
	PLog('get_pics_tagesschau:')
	href_rec=[]; summ_rec=[]; picnr_rec=[]; cr_rec=[]

	page =  stringextract('mod modA modGallery', '<!-- con -->',page)
	records = blockextract('class="teaser">',  page)
	PLog(len(records))	
	
	i=0
	for rec in records:	
		pic_href =   stringextract('src="', '"', rec)
		if pic_href == '':
			continue	
		pic_href =   'http://www.tagesschau.de' + pic_href	
		# PLog(pic_href)	
		
		pic_nr = "%s/%s" % (str(i+1), str(len(records)))
		cr   =  stringextract('<img alt="', '"',rec) 	# hier Titel 
		cr   =  unescape(cr)
		summ = stringextract('teasertext colCnt">', '</p>',rec) # hier summary					
		summ   =  unescape(summ)
								
		PLog(pic_nr); PLog(cr);PLog(summ[:40]); PLog(pic_href);
		href_rec.append(pic_href); summ_rec .append(summ); picnr_rec.append(pic_nr); cr_rec.append(cr)
		i=i+1
	
	return href_rec, summ_rec, picnr_rec, cr_rec
