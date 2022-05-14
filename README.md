Kodi-Addon-ARDundZDF
===================

Addon für Kodi / XBMC (Kodi-Version von [Plex-Plugin ARDundZDF](https://github.com/rols1/ARDundZDF)).<br>
Ab Version 2.2.5 für Kodi-Leia und -Matrix geeignet (Python2- / Python3-kompatibel).<br>
Mit Inhalten der Mediatheken von ARD und ZDF, 3Sat, funk, phoenix, KIKA und ZDFtivi, tageschau.de, Arte-Kategorien,
einschließlich Live-TV mit Aufnahmefunktion (ffmpeg erforderlich), Live-Radio, Podcasts.<br>

Für die ZDF Mediathek kann wahlweise die kompakte Version ZDFmobile genutzt werden. 

Download aktuelle Version: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest
![Downloads](https://img.shields.io/github/downloads/rols1/Kodi-Addon-ARDundZDF/total.svg "Downloads")
<b>(Kodi Leia)</b> oder [kodinerds-Repo](https://repo.kodinerds.net) <b>(Kodi Leia, Kodi Matrix)</b> - siehe INSTALLATION.

Plex hat die Unterstützung für Plugins in seinen Client-Softwarepaketen eingestellt. Die Repos für die Plex-Versionen [Plex-Plugin-ARDMediathek2016](https://github.com/rols1/Plex-Plugin-ARDMediathek2016) und [ARDundZDF](https://github.com/rols1/ARDundZDF) habe ich im März 2022 gelöscht (dto. FlickrExplorer, TuneIn2017, Shoutcast2017).<br>

<b>Classic-Version der ARD Mediathek</b>: seit Juni 2021 sind die Classic-Links nicht mehr erreichbar. Der Code im Addon wurde entfernt; im Addon ist das Menü <b>ARD Mediathek Neu</b> voreingestellt (Details siehe Funktionen).<br>
Damit entfallen auch die Radio-Podcasts der Classic-Version. Sie werden durch die neue Audiothek abgelöst.<br>

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
- ARD Mediathek RETRO
- ARD Mediathek Entdecken
- Livestreams
- Sendung Verpasst
- Sendungen A-Z
- ARD Sport (neu)
- ARD Sportschau (sportschau.de)
- Barrierearm
- Bildgalerien Das Erste
- Senderwahl

#### ZDF Mediathek: 
- Suche nach Sendungen
- Startseite (wie Webseite)
- ZDF-funk (https://www.zdf.de/funk)
- Sendung Verpasst (Sendungen der letzten 7 Tage)
- Sendungen A-Z
- Rubriken
- ZDF-sportstudio
- Barrierearm (Hörfassungen, Untertitel, Gebärdensprache)
- ZDFinternational
- Bilderserien

#### 3Sat Mediathek:
- Suche nach Sendungen
- 3Sat-Livestream
- Startseite (wie Webseite)
- Sendung Verpasst (Sendungen der letzten 30 Tage
- Sendungen A-Z
- Themen
- Rubriken
- Bildgalerien 3sat

#### ARD-Audiothek Neu (Stand 25.02.2022) mit Podcast-Favoriten:
- Suche
- Livestreams, einschl. "ARD Audio Event Streams", "Livestreams der sportschau.de" 
- Entdecken (wie Webseite)
- Rubriken
- Sport
- Sender (Sendungen einzelner Radiosender)
- FUNK-Podcasts - Pop und Szene
- Podcast-Favoriten (manuell erweiterbar)

#### TV-Live-Streams (30.08.2018: 33 Sender), Aufnahmefunktion: 
- ARD- und ZDF-Sender überregional und regional, einige ausgewählte Privatsender
- für die Aufnahmefunktion (mit oder ohne EPG) ist eine [ffmpeg-Installation](https://ffmpeg.org/download.html) erforderlich 

#### Radio-Live-Streams der ARD:
- alle Radiosender von Bayern, HR, mdr, NDR, Radio Bremen, RBB, SR, SWR, WDR, Deutschlandfunk. Insgesamt 10 Stationen, 63 Sender
 
#### Videobehandlung ARD Mediathek und ZDF Mediathek:
- Livestreams: Auflistung der verfügbaren Angebote an Bandbreiten + Auflösungen (falls verfügbar: Audio ohne Video)
- Videoclips: Auflistung der verfügbaren Angebote an Qualitätstufen sowie zusätzlich verfügbarer Videoformate (Ausnahme HDS + SMIL) 

#### Downloadoption (ab Version 2.6.8 ohne cURL/wget)
- Download von Videos im ARD-Bereich
- Download von Videos im ZDF-Bereich
- Download von Videos in den Modulen 3Sat, funk, Kinderprogramme
- Download von Podcasts - bei Podcast-Favoriten zusätzlich Sammeldownloads 
- Tools zum Bearbeiten des Download-Verzeichnisses (Verzeichnisse festlegen, Verschieben, Löschen)

#### Favoriten, Merkliste, strm-Dateien
- Kodi-Favoriten lassen sich einblenden und im Addon aufrufen
- interne Merkliste mit Ordnerverwaltung und Filterfunktion - optional: netzwerkweit mit lokaler Synchronisation
- strm-Dateien für einzelne Videos und Serien (einschl. Serienüberwachung für die meisten ARD- und ZDF-Serien)

#### Updates
- entweder mit dem integrierten <b>Updatemodul (autom. Anpassung an Kodi-Version)</b> oder via <b>kodinerds-Repo</b>
- Updates einzelner Bestandteile des  Addons (Einzelupdate) zwischen den regulären  Updates - Näheres siehe [Startpost im kodinerds-Forum](https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?postID=502022#post502022) 

#### weitere Module (optional)
- ZDFmobile (gedacht als Alternative bei Ausfall der Webseite)
- 3Sat
- funk
- Kinderprogramme (z.Z. KIKA und ZDFtivi)
- TagesschauXL (https://www.tagesschau.de/)
- phoenix (https://www.phoenix.de/)
- Arte-Kategorien
- "Zuletzt gesehen"-Funktion 
- Video-Playlist einschl. Archiv-Funktion
- strm-Modul
- Suchfunktion für MediathekView (s. Credits)


INSTALLATION:
===================  
### Hinweis für ältere Kodi-Versionen (Leia, Krypton): für die Erstinstallation muss die [Krypton-Version](https://repo.kodinerds.net) auf kodinerds.net verwendet werden. Dies gilt auch für ein Downgrade einer Kodi-Matrix-Version zu Leia, Krypton.

- <b>Matrix-Version:</b>Download der zip-Datei [aktuelles Release](https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest) oder Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo](https://repo.kodinerds.net)
- <b>Leia-Version:</b> Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo, im Tab Kodi-Version Kodi 17 (Krypton) auswählen](https://repo.kodinerds.net) 
- zip-Datei mittels Kodi-Menü Addons/Addon-Browser installieren
- nur falls die Abhängigkeit zum Modul kodi-six bemängelt wird: Download und Installation des Moduls [script.module.kodi-six.zip](https://github.com/romanvm/kodi.six/releases)
- Addon öffen und Addon-Einstellungen anpassen
- [Empfehlenswert: Kodi Anleitung & Beschreibung von Rene8001](https://www.kodinerds.net/index.php/Thread/47479-Hilfe-f%C3%BCr-Neulinge-Kodi-Anleitung-Einstellungen-GooglePlay-FireTV/?pageNo=1)

Credits:
===================
- Credits to [bagbag](https://github.com/bagbag): [MediathekViewWeb with API](https://github.com/mediathekview/mediathekviewweb/) 
- Credits to all the members of Forum Kodinerds who help to make this addon better
- Credits to [coder-alpha](https://forums.plex.tv/discussion/166602/rel-ccloudtv-channel-iptv/p1): Channel updater, based on Channel updater by sharkone/BitTorrent.bundle
- Credits to [Arauco](https://forums.plex.tv/profile/Arauco): processing of Logos and Icons (Plex-Plugin ARDundZDF)
- Credits to [romanv](https://github.com/romanvm) for his script.module.kodi-six

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
