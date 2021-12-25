Kodi-Addon-ARDundZDF
===================

Addon für Kodi / XBMC (Kodi-Version von [Plex-Plugin ARDundZDF](https://github.com/rols1/ARDundZDF)).<br>
Ab Version 2.2.5 für Kodi Matrix vorbereitet (Python2- / Python3-kompatibel).<br>
Mit Inhalten der Mediatheken von ARD und ZDF, 3Sat, funk, phoenix, KIKA und ZDFtivi, tageschau.de, Arte-Kategorien,
einschließlich Live-TV mit Aufnahmefunktion (ffmpeg erforderlich), Live-Radio, Podcasts.<br>

Für die ZDF Mediathek kann wahlweise die kompakte Version ZDFmobile genutzt werden. 

Download aktuelle Version: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest
![Downloads](https://img.shields.io/github/downloads/rols1/Kodi-Addon-ARDundZDF/total.svg "Downloads")
<b>(Kodi Leia)</b> oder [kodinerds-Repo](https://repo.kodinerds.net) <b>(Kodi Leia, Kodi Matrix)</b> - siehe INSTALLATION.

Die Plex-Versionen [Plex-Plugin-ARDMediathek2016](https://github.com/rols1/Plex-Plugin-ARDMediathek2016) und [ARDundZDF](https://github.com/rols1/ARDundZDF) werden nicht mehr gepflegt - Plex hat die Unterstützung für Plugins in seinen Client-Softwarepaketen eingestellt.

<b>Classic-Version der ARD Mediathek</b>: seit Juni 2021 sind die Classic-Links nicht mehr erreichbar. Der Code im Addon wurde entfernt; im Addon ist die neue ARD Mediathek weiterhin verfügbar (siehe Funktionen).

#### Rückmeldungen willkommen:
Im Forum: https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/  
direkt: rols1@gmx.de 

#### statt Handbuch: [Einstellungen des Addons](https://github.com/rols1/Kodi-Addon-ARDundZDF/wiki)
  
Funktionen: 
===================

#### ARD Mediathek (Classic-Version): seit Juni 2021 entfallen  

#### ARD Mediathek (neue Version):  
- Suche nach Sendungen
- Startseite (wie Webseite)
- Sendung Verpasst
- Sendungen A-Z
- ARD Sportschau
- Senderwahl
- barrierefreie Angebote finden sich im Startmenü bei Rubriken oder Genrezugängen

#### ZDF Mediathek: 
- Suche nach Sendungen
- Startseite (wie Webseite, einschl. funk-Inhalte)
- Sendung Verpasst (Sendungen der letzten 7 Tage)
- Sendungen A-Z
- Sendungen A-Z Neu: funk
- Rubriken
- MeistGesehen (1 Woche)
- Sport Live im ZDF
- Barrierearm (Hörfassungen, Untertitel, Gebärdensprache)
- ZDFenglish
- ZDFarabic
- Bilderserien

#### 3Sat Mediathek:
- Suche nach Sendungen
- 3Sat-Livestream
- Sendung Verpasst (Sendungen der letzten 30 Tage
- Sendungen A-Z
- Rubriken

#### Radio-Podcasts:
- Sendungen A-Z
- Rubriken
- Radio-Feature
- Radio-Tatort
- Neueste Audios
- Meist abgerufen
- Refugee-Radio

#### ARD-Audiothek Neu:
- Highlights
- Unsere Favoriten
- Sammlungen
- Meistgehört
- Ausgewählte Sendungen
- Themen
- Sendungen A-Z (alle Radiosender)
- Podcast-Favoriten (manuell erweiterbar)
- Livestreams (einschl. Die Fußball-Bundesliga im ARD-Hörfunk) 

#### TV-Live-Streams (30.08.2018: 33 Sender), Aufnahmefunktion: 
- ARD- und ZDF-Sender überregional und regional, einige ausgewählte Privatsender
- für die Aufnahmefunktion (mit oder ohne EPG) ist eine [ffmpeg-Installation](https://ffmpeg.org/download.html) erforderlich 

#### Radio-Live-Streams der ARD:
- alle Radiosender von Bayern, HR, mdr, NDR, Radio Bremen, RBB, SR, SWR, WDR, Deutschlandfunk. Insgesamt 10 Stationen, 63 Sender
 
#### Videobehandlung ARD Mediathek und ZDF Mediathek:
- Videostreams: Auflistung der verfügbaren Angebote an Bandbreiten + Auflösungen (falls verfügbar: Audio ohne Video)
- Videoclips: Auflistung der verfügbaren Angebote an Qualitätstufen sowie zusätzlich verfügbarer Videoformate (Ausnahme HDS + SMIL) 

#### Downloadoption (ab Version 2.6.8 ohne cURL/wget)
- Download von Videos im ARD-Bereich
- Download von Videos im ZDF-Bereich
- Download von Videos in den Modulen 3Sat, funk, Kinderprogramme
- Download von Podcasts - bei Podcast-Favoriten zusätzlich Sammeldownloads 
- Tools zum Bearbeiten des Download-Verzeichnisses (Verzeichnisse festlegen, Verschieben, Löschen)

#### Favoriten, Merkliste
- Kodi-Favoriten lassen sich einblenden und im Addon aufrufen
- interne Merkliste mit Ordnerverwaltung und Filterfunktion - optional: netzwerkweit mit lokaler Synchronisation 

#### Updates
- entweder mit dem integrierten <b>Updatemodul (autom. Anpassung an Kodi-Version)</b> oder via <b>kodinerds-Repo</b>

#### weitere Module (optional)
- ZDFmobile
- 3Sat
- funk
- Kinderprogramme (z.Z. KIKA und ZDFtivi)
- TagesschauXL (https://www.tagesschau.de/)
- phoenix (https://www.phoenix.de/)
- Arte-Kategorien
- "Zuletzt gesehen"-Funktion 
- Video-Playlist einschl. Archiv-Funktion


INSTALLATION:
===================  
### Hinweis für Kodi-Matrix-Nutzer: für die Erstinstallation muss die [Matrix-Version](https://repo.kodinerds.net) auf kodinerds.net verwendet werden. Dies gilt auch für ein Upgrade einer älteren Kodi-Version zu Matrix.

- <b>Leia-Version:</b> Download der zip-Datei [aktuelles Release](https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest) 
- <b>Matrix-Version:</b> Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo, im Tab Kodi-Version Kodi 19 auswählen](https://repo.kodinerds.net)
- zip-Datei mittels Kodi-Menü Addons/Addon-Browser installieren
- nur falls die Abhängigkeit zum Modul kodi-six bemängelt wird: Download und Installation des Moduls [script.module.kodi-six.zip](https://github.com/romanvm/kodi.six/releases)
- Addon öffen und Addon-Einstellungen anpassen
- [bebilderte Anleitung](https://www.kodinerds.net/index.php/Thread/14234-Wie-installiert-man-Addons-die-nicht-über-den-Addon-Browser-verfügbar-sind/?page=Thread&threadID=14234)

Credits:
===================  
- Credits to [coder-alpha](https://forums.plex.tv/discussion/166602/rel-ccloudtv-channel-iptv/p1): (Channel updater, based on Channel updater by sharkone/BitTorrent.bundle)
- Credits to [Arauco](https://forums.plex.tv/profile/Arauco): processing of Logos and Icons (Plex-Plugin ARDundZDF)
- Credits to [romanv](https://github.com/romanvm) for his script.module.kodi-six
- Credits to all the members of Forum Kodinerds who help to make this addon better

Hauptmenü:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Hauptmenue.png)

Hauptmenü ARD Neu:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Hauptmenue_ARD-Neu.png)

Hauptmenü ZDF:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Hauptmenue_ZDF.png)

Sucheingabe:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Suche_Eingabe.png)

Suchergebnis:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Suche_Ergebnis.png)

Videoformate ZDF Mediathek 1:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Videoformate_ZDF_Mediathek-1.png)

Videoformate ZDF Mediathek 2:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Videoformate_ZDF_Mediathek-2.png)

TV Livesender Vorauswahl:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/TV_Livesender_Vorauswahl.png)

Merkliste (mit Filter):
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Settings/Merkliste_Kontext_filtered.png)

Audiothek:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Audiothek.png)

Audiothek Livestreams:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Radio_Livesender.png)

Podcast-Favoriten:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Podcast-Favoriten.png)

Aufnahmemöglichkeiten (ffmpeg erforderlich):
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Settings/Menu_TV-Livestreams.png)

#### weitere Screenshots: https://github.com/rols1/PluginPictures/tree/master/Kodi/ARDundZDF
