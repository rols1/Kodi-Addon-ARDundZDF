Kodi-Addon-ARDundZDF
===================

Addon für Kodi / XBMC (Kodi-Version von Plex-Plugin ARDundZDF).<br>
Ab Version 2.2.5 für Kodi-Krypton, -Leia, -Matrix und -Nexus  geeignet (Python2- / Python3-kompatibel).<br>
Mit Inhalten der Mediatheken von ARD und ZDF, 3Sat, funk, phoenix, KIKA und ZDFtivi, tageschau.de, Arte-Kategorien,
einschließlich Live-TV mit Aufnahmefunktion (ffmpeg erforderlich), Live-Radio, Podcasts.<br>

Download aktuelle Version: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest
![Downloads](https://img.shields.io/github/downloads/rols1/Kodi-Addon-ARDundZDF/total.svg "Downloads")
<b>(Kodi Matrix)</b> oder [kodinerds-Repo](https://repo.kodinerds.net) <b>(Kodi-Krypton, -Leia, -Matrix und -Nexus)</b> - siehe INSTALLATION.

Plex hat die Unterstützung für Plugins in seinen Client-Softwarepaketen eingestellt. Die Repos für die Plex-Versionen [Plex-Plugin-ARDMediathek2016](https://github.com/rols1/Plex-Plugin-ARDMediathek2016) und [ARDundZDF](https://github.com/rols1/ARDundZDF) habe ich im März 2022 gelöscht (dto. FlickrExplorer, TuneIn2017, Shoutcast2017).<br>

<b>Classic-Version der ARD Mediathek</b>: seit Juni 2021 sind die Classic-Links nicht mehr erreichbar. Der Code im Addon wurde entfernt; im Addon ist das Menü <b>ARD Mediathek Neu</b> voreingestellt (Details siehe Funktionen).<br>
Die Radio-Podcasts der Classic-Version wurden durch die neue Audiothek abgelöst.<br>

#### Rückmeldungen willkommen:
Im Forum: https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/  
direkt: rols1@gmx.de 

#### statt Handbuch: [Einstellungen des Addons - Wicki](https://github.com/rols1/Kodi-Addon-ARDundZDF/wiki)
  
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
- ARD Sport
- ARD sportschau.de (WDR)
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
- Sendung Verpasst (Sendungen der letzten 30 Tage)
- Sendungen A-Z
- Themen
- Rubriken
- Bildgalerien 3sat

#### ARD-Audiothek:
- Suche
- Livestreams, einschl. ARD Audio Event Streams, Audio- und Netcastaudio-Streams der sportschau.de
- Entdecken (wie Webseite)
- Rubriken
- Sport
- Sender (Sendungen einzelner Radiosender)
- funk: Das Content-Netzwerk von ARD und ZDF
- Podcasts der Platform www.podcast.de


#### TV-Live-Streams mit Aufnahmefunktion: 
- ARD- und ZDF-Sender überregional (13) und regional (13 plus WDR Lokalzeitsender), einige ausgewählte Privatsender
- für die Aufnahmefunktion (mit oder ohne EPG) ist eine [ffmpeg-Installation](https://ffmpeg.org/download.html) erforderlich 

#### Radio-Live-Streams der ARD:
- alle Radiosender von Bayern, HR, mdr, NDR, Radio Bremen, RBB, SR, SWR, WDR, Deutschlandfunk. Insgesamt 10 Stationen, 65 Sender
 
#### Videobehandlung (Setting: Sofortstart AUS):
- Livestreams: Auflistung der verfügbaren Angebote an Bandbreiten + Auflösungen (falls verfügbar: Audio ohne Video)
- Videoclips: Auflistung der verfügbaren Angebote an Qualitätstufen sowie zusätzlich verfügbarer Videoformate (Bsp. UHD) 

#### Downloadoption (ab Version 2.6.8 ohne cURL/wget)
- Download von Videos im ARD-Bereich
- Download von Videos im ZDF-Bereich
- Download von Videos in den Modulen arte, 3Sat, TagesschauXL, phoenix, Kinderprogramme
- Download von Podcasts - bei Podcast-Favoriten zusätzlich Sammeldownloads (angezeigte Liste der Beiträge)

#### Addon-Tools
- Addon-Infos mit Angaben zum System, Cache, zu Dateipfaden und Modulen
- "Zuletzt gesehen"-Liste
- Tools zum Bearbeiten von Ausschluss-Filtern (ARD, ZDF)
- Bereinigung der Merkliste
- Tools zum Bearbeiten von Suchwörtern (ARD, ZDF)
- Tools zum Bearbeiten des Download-Verzeichnisses (Verzeichnisse festlegen, Verschieben, Löschen)
- Tools zum Bearbeiten von strm-Listen für Serien (ARD, ZDF), einschl. autom. Überwachung im Hintergrund
- Tools zum Bearbeiten der addon-internen Playlist
- Kodis Thumbnails-Ordner bereinigen
- Settings inputstream.adaptive-Addon öffnen (Bandbreite, Auflösung und weitere Einstellungen)
- Einzelupdate für einzelne Dateien und Module im Addon - siehe auch Updates

#### Favoriten, Merkliste, strm-Dateien
- Kodi-Favoriten lassen sich einblenden und im Addon aufrufen
- interne Merkliste mit Ordnerverwaltung und Filterfunktion - optional: netzwerkweit mit lokaler Synchronisation
- strm-Dateien für einzelne Videos und Serien (einschl. Serienüberwachung für die meisten ARD- und ZDF-Serien)

#### Updates
- entweder mit dem integrierten <b>Updatemodul (autom. Anpassung an Kodi-Version)</b> oder via <b>kodinerds-Repo</b>
- Updates einzelner Bestandteile des  Addons (Einzelupdate) zwischen den regulären  Updates - Näheres siehe [Startpost im kodinerds-Forum](https://www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?postID=502022#post502022) 

#### weitere Module (optional)
- ~~ZDFmobile~~ - entfernt ab Juni 2023 (obsolet)
- 3Sat
- ~~funk~~ - entfernt ab Mai 2023 (Videos in ZDF-funk, Podcasts in der ARD-Audiothek verfügbar)
- Kinderprogramme (KIKA, ZDFtivi, MausLive u.a.)
- TagesschauXL (https://www.tagesschau.de/ und https://www.ardmediathek.de/tagesschau24)
- phoenix (https://www.phoenix.de/ und https://www.ardmediathek.de/phoenix)
- Arte-Kategorien
- "Zuletzt gesehen"-Funktion (im Tools-Menü)
- Video-Playlist einschl. Archiv-Funktion (im Tools-Menü)
- strm-Modul, einschließlich Serien-Überwachung
- Suche im Datenbestand von MediathekView (s. Credits)


INSTALLATION:
===================  
### Hinweis für ältere Kodi-Versionen (Leia, Krypton): für die Erstinstallation muss die [Krypton-Version](https://repo.kodinerds.net/index.php?action=list&scope=all&version=krypton/) auf kodinerds.net verwendet werden. Dies gilt auch für ein Downgrade einer Kodi-Matrix-Version zu Leia, Krypton.

- <b>Nexus-Version:</b> Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo, im Tab Kodi-Version Kodi 20 (Nexus) auswählen](https://repo.kodinerds.net/index.php?action=list&scope=all&version=nexus/) 
- <b>Matrix-Version:</b>Download der zip-Datei [aktuelles Release](https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/latest) oder Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo, im Tab Kodi-Version Kodi 19 (Matrix) auswählen](https://repo.kodinerds.net/index.php?action=list&scope=all&version=matrix/)
- <b>Leia-Version:</b> Download der aktuellen zip-Datei ARDundZDF im [kodinerds-Repo, im Tab Kodi-Version Kodi 17 (Krypton) auswählen](https://repo.kodinerds.net/index.php?action=list&scope=all&version=krypton/) 
- zip-Datei mittels Kodi-Menü Addons/Addon-Browser installieren
- nur falls die Abhängigkeit zum Modul kodi-six bemängelt wird: Download und Installation des Moduls [script.module.kodi-six.zip](https://github.com/romanvm/kodi.six/releases)
- Addon öffen und Addon-Einstellungen anpassen
- [Empfehlenswert: Kodi Anleitung & Beschreibung von Rene8001](https://www.kodinerds.net/index.php/Thread/47479-Hilfe-f%C3%BCr-Neulinge-Kodi-Anleitung-Einstellungen-GooglePlay-FireTV/?pageNo=1)

SUPPORT:
=================== 
Um die Community des <b>[kodinerds-Forums](https://www.kodinerds.net/)</b> zu beteiligen, bitte vorrangig den <b>[Support-Thread des Addons](https://www.kodinerds.net/thread/64244-release-kodi-addon-ardundzdf/)</b> verwenden.<br>
Der <b>[Startpost](https://www.kodinerds.net/thread/64244-release-kodi-addon-ardundzdf/?pageNo=1#post502022)</b> enthält Hinweise zum nächsten Update und zu geänderten Dateien des Addons, die als Einzelupdate mit dem Addon-Tool <b>Infos+Tools -> Einzelupdate..</b> bereits vor dem regulären Update installiert werden können.


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

Videoformate Arte Mediathek:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Videoformate_Arte_Mediathek.png)

TV Livesender Vorauswahl:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/TV_Livesender_Vorauswahl.png)

TV Livesender mit EPG (Kontextmenü: Tages-EPG):
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/TV_Livesender_EPG.png)

Merkliste (mit Filter):
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Settings/Merkliste_Kontext_filtered.png)

Audiothek:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Audiothek.png)

Audiothek Livestreams:
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Radio_Livesender.png)

Aufnahmemöglichkeiten (ffmpeg erforderlich):
===================  
![img](https://github.com/rols1/PluginPictures/blob/master/Kodi/ARDundZDF/Settings/Menu_TV-Livestreams.png)

#### weitere Screenshots: https://github.com/rols1/PluginPictures/tree/master/Kodi/ARDundZDF
