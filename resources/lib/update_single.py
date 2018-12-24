################################################################################
#				update_single.py - Part of Pex-Plugin-ARDMediathek2016
#							Update von Einzeldateien
################################################################################
#import  urllib, os		# bereits geladen

PREFIX 			= '/video/ardundzdf'			
REPO_BASE 		= 'https://raw.githubusercontent.com/rols1/Plex-Plugin-ARDMediathek2016/master'
Plugin_FILE		= '/Contents/Resources/update_single_files'

################################################################################
# Aufruf: 	wie Plugin-Update - bei Pluginstart oder manuell (Einstellungen)
# Ablauf:		mode: check:
#			1. Repo_FILE holen, HISTORY holen 
#			2. je Zeile: Zeitstempel Repo_FILE gegen LOCAL_FILE  vergleichen
#			2.1 Repo_FILE fehlt/leer: Abbruch - kein Austausch - Cancelsignal für laufende Single-Updates
#			2.2 Zeitstempel fehlt oder jünger: Rückgabe 1 = Austauschsignal
#
#				mode replace:
#			1., 2. wie check_repo 
#			3. update_single_files im  Plugin: altes Format/fehlt/leer: Austausch aller gelisteten Dateien
#			4. Zeile: lokaler Zeitstempel ist jünger: Austausch der dazu gehörigen Datei
#			5. Abschluss: Austausch update_single_files + HISTORY im Plugin gegen die Repo-Version
#			6. Hinweis: Plugin neu starten | betroffene Dateien 
#
# 03.12.2018 Formatwechsel: jede Zeile mit Dateistempel + Datei
#
# Austausch erfolgt auch, wenn update_single_files: fehlt/leer/im alten Format
# Für jede Datei existiert eine Zeile (ermöglicht inkrementelles Update)
# Beim Versions-Update ist update_single_files manuell zu löschen, um Inkonsistenzen zu verhindern.
# HISTORY enthält für jede hier geänderte Datei einen Eintrag zu aktuellen Version
#
# Format File:			Datum | UTC-Sekunden | File1
#				inkrementell: neue Update-Dateien (innerhalb einer Version) werden jeweils 
#				angehängt - das alte Format verhinderte ein Update, wenn Nutzer Updates übersprangen.
# Format Zeitstempel: 	Datum | UTC-Sekunden (Konsole: date, date +"%s")
#				Bsp.: So 17. Dez 22:32:12 CET 2017 | 1513546328 | ./Contents/Resources/ZDFarabic.png
#				Die UTC-Sekunden ersparen hier Zeitfunktionen (einfacher int-Vergleich)
################################################################################

@route(PREFIX + '/check_repo')
# mode = check oder replace
# Rückgabe: 
#	Fehler: 0, info-string (exception-string)
#	Erfolg: 1, info-string (ausgetauschte Dateien)
def check_repo(mode=''):
	Log('update_single: check_repo')
	Log('mode: ' + mode)
	
	repo_cont = ''; hist_cont = ''
	try:									# Repo_FILE laden
		repo_cont = HTTP.Request(REPO_BASE + Plugin_FILE, cacheTime=1).content
		# repo_cont = Core.storage.load('/tmp/update_single_files')	# Test lokal
		repo_cont = repo_cont.strip()
		hist_cont = HTTP.Request(REPO_BASE + '/HISTORY', cacheTime=1).content	
	except Exception as exception:
		Log(str(exception))
		return 0, str(exception) + ' (Github: update_single_files)'		
	Log('repo_cont: ' + repo_cont)
	Log('hist_cont: ' + hist_cont[:40])
	
	# Hinw.: storage.join_path erwartet Liste der Pfadelemente - anders als os.path.join
	LOCAL_FILE = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources', 'update_single_files')
	Log(LOCAL_FILE)
	plugin_cont = ''; 
	Log(os.path.exists(LOCAL_FILE))
	if os.path.exists(LOCAL_FILE):
		try:								# Plugin_FILE laden		
			plugin_cont = 	Core.storage.load(LOCAL_FILE)
		except Exceptionn as exception:			
			Log(str(exception))

	repo_lines	 = repo_cont.splitlines()
	plugin_lines = plugin_cont.splitlines()

	if repo_cont == '':						# leere Datei: kein Austausch, mode egal
		Log('Repo update_single_files: leer')
		return 0, 'alles aktuell'
		
	force_replace = False
	if plugin_cont.count('|') <= 1:			# Test auf altes Format: nur 1 x '|' in gesamter Datei
		force_replace = True
		Log('Plugin update_single_files: altes Format/fehlt/leer')
		
	to_replace = []
	for line in repo_lines:					# Abgleich Repo_FILE mit Plugin_FILE
		if line.strip() == '' or '|' in line == False:	# leer, Format falsch?
			continue
		line_date, line_stamp, line_file = line.split('|') 					# Zeile  Repo_FILE lesen
		Log('repo: date|stamp|file'); Log(line_date); Log(line_stamp); Log(line_file);
		line_stamp = int(line_stamp.strip())
		line_file = line_file.strip()
		line_file = line_file.replace('./', '/')	# ls-Ausgabe bereinigen
		
		if  force_replace == True:					# Austausch erzwingen (plugin_cont leer oder altes Format)
			to_replace.append(line_file)
		else:
			if plugin_lines:
				for p_line in plugin_lines:
					if p_line.strip() == '' or '|' not in p_line:	# leer, Format falsch?
						continue
					# Log(p_line)
					p_line_date, p_line_stamp, p_line_file = p_line.split('|') # Zeile  Plugin_FILE lesen
					p_line_stamp = int(p_line_stamp.strip())
					p_line_file = p_line_file.strip()
					p_line_file = p_line_file.replace('./', '/')	# ls-Ausgabe bereinigen
					if p_line_file == line_file:					# Dateiname stimmt überein
						Log('line_stamp: ' + str(line_stamp)); Log('p_line_stamp: ' + str(p_line_stamp)); 
						if line_stamp > p_line_stamp:				# Repo_Datei ist jünger
							to_replace.append(line_file)
							Log('to_replace: ' + line_file)
			
	if mode == 'check':
		if len(to_replace) == 0:
			Log('Abgleich: alles aktuell')
			return 0, 'alles aktuell'
		else:		
			Log("Einzeldatei(en): " + ', '.join(to_replace))
			return 1, "Einzeldatei(en): " + ', '.join(to_replace)
			
# ----------------------------------------------------------------------			
# ab hier wird ersetzt (mode=replace):
	cnt = 0
	for line in to_replace:					# Bsp. /Contents/Resources/ZDFarabic.png
		try:
			repo_url = REPO_BASE + line
			cont = HTTP.Request(repo_url).content
			plugin_path = os.path.join(Core.bundle_path + line)
			Log(plugin_path)
			# Log(cont[2000:3000])
			Core.storage.save(plugin_path, cont)	# verwendet temp-File: ..s/._file
		except Exception as exception:			
			msg = str(exception)
			Log(msg)
			return ObjectContainer(header=L('Fehler'), message=msg)						
		cnt = cnt + 1

	# zum Schluß neues update_single_files + neues HISTORY (hist_cont)speichern:
	plugin_file = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources', 'update_single_files')
	hist_file = Core.storage.join_path(Core.bundle_path, 'HISTORY')
	try:							
		Core.storage.save(plugin_file, repo_cont)	
		Core.storage.save(hist_file, hist_cont)	
	except Exception as exception:
		msg =  str(exception) + ' (Plugin: update_single_files)'
		Log(msg)
		return ObjectContainer(header=L('Fehler'), message=msg)			
	
	msg = 'Update erfolgreich - Plugin bitte neu starten |\r\n'		
	msg = msg + '%s Datei(en) erneuert | %s'	% (cnt, ', '.join(repo_lines))
	return ObjectContainer(header=L('Info'), message=msg)			
	
# ----------------------------------------------------------------------			
