# QA-Bericht Urlaubs-Team

Stand 18.10.2026. Geprüft gegen `urlaubs-team-prompt.md` (nachträglich aus dem Chat angelegt, da die Datei fehlte) und den Prüfprompt.

> **Gesamtampel: GELB (nutzbar mit bekannten Lücken)**

Hinweis zur Unabhängigkeit: Der Prüfer ist dasselbe Modell, das die App gebaut hat. Gegengewicht sind automatisierte Browser-Tests mit Prüfdaten (`qa/harness/test_app.py`), die auch Fehler im eigenen Bau gefunden haben.

## Zahlen

| Anforderungen gesamt | Erfüllt | Teilweise | Fehlt | Nicht prüfbar |
|---|---|---|---|---|
| 137 | 121 | 14 | 0 | 2 |

Browser-Tests: 151 Prüfungen, 150 bestanden, 1 durchgefallen (die eine offene ist A-098, Grenze der Plattform). Konsolenfehler: keine.

## Was geprüft wurde und wie

- **Browser-Tests (Playwright, Chromium)** gegen die echte App-Datei mit einer Attrappe für Datenbank, Nutzer und Downloads: Kacheln, Filter, Maske, Validierung, Optimieren, Plan inkl. Drag & Drop, Ausgabe .ics, .pdf und Markdown, Backlog, Mitreisende, Responsive (1440, 820, 390 px), Dunkelmodus, Tastatur, 20 Reisen. Screenshots in `qa/screens/`.
- **Live-Datenbank** (`ArtifactData`): Testreise `[TEST] Sommer 2027` mit Martin, Kristina, Matteo und einer befreundeten Familie, Optimieren-Lauf mit 3 Vorschlägen, Plan-Entwurf, Digest, Preise, 7 Backlog-Einträge. Lesen als Admin und als reine Ansicht.
- **Daten und Sicherheit:** `qa/check_daten.py`, Suche nach Geheimnissen und Zahlungsdaten, Netzwerkaufrufe in der App, Injektionstest mit lokaler Testseite, geplante Aufgaben.
- **Nicht geprüft werden konnte:** die veröffentlichte App im echten Claude-Viewer (Rahmen, CSP, Drag & Drop, Downloads). Dafür steht ein 10-Minuten-Klicktest in `qa/regressionstests.md`.

## Gefundene Mängel

| Nr. | Prio | Beschreibung | Behoben | Retest |
|---|---|---|---|---|
| M-01 | P2 | A-054: Datum in der Vergangenheit wurde nicht gemeldet. | ja (Schleife 1) | bestanden |
| M-02 | P2 | A-092: PDF-Export fehlte. Jetzt als PDF 1.4 aus dem Plan, gelesen mit pypdf. | ja (Schleife 1) | bestanden |
| M-03 | P2 | A-108: Doppelte Links wurden doppelt angelegt. Jetzt Erkennung, in der Reise Zuordnung. | ja (Schleife 1) | bestanden |
| M-04 | P2 | A-125: Änderungen am Reiseplan wurden nicht versioniert. Jetzt mit Verlauf und Rückgängig, die letzten 20 bleiben. | ja (Schleife 1) | bestanden |
| M-05 | P2 | A-011/A-114: Digests lagen nur in der Datenbank, nicht in `digests/`. `spiegel.py` schreibt sie jetzt. | ja (Schleife 3) | bestanden |
| M-06 | P3 | A-056: Sehr langer Titel sprengte die Detailansicht. | ja (Schleife 1) | bestanden |
| M-07 | P3 | A-131: Kontrast im Hellmodus unter 4,5:1 bei Hilfstext auf weicher Fläche (4,36) und Akzent auf Akzentfläche (4,11). Farben angepasst. | ja (Schleife 2) | berechnet, alle Paare ≥ 4,5 |
| M-08 | P3 | Kachel „Neue Reise“ war auf dem Handy riesig, Mini-Kurve hing lose neben dem Trend. | ja (Schleife 2) | Screenshot geprüft |
| M-09 | P3 | Links mit Status „nicht abrufbar“ wurden als „geprüft“ angezeigt. | ja (Schleife 3) | bestanden |
| M-11 | P2 | A-136: Nach dem Absenden der Suchleiste öffnete sich die Reise nicht, weil der Cursor in der Eingabe blieb und die Ansicht zurückgehalten wurde. Von den neuen Tests gefunden, behoben. | ja (Schleife 3) | bestanden |
| M-10 | P3 | A-104: Tote Links konnten nicht markiert werden. Feld `link_status` mit Anzeige ergänzt. | ja (Schleife 3) | bestanden |

Mehrere Fehlschläge im ersten Lauf lagen am Test selbst (Großschreibung in Tabellenköpfen, falsche Erwartung bei der Preissortierung, Neuladen löschte die Attrappe). Sie sind korrigiert und zählen nicht als Mängel der App.

## Offene Punkte mit Lösungsvorschlag

| Nr. | Punkt | Lösungsvorschlag | Aufwand |
|---|---|---|---|
| O-1 | A-098: Quick-Add holt Titel und Kurzbeschreibung nicht selbst. Die App darf keine Fremdseiten abrufen. | Das Team füllt beides auf Zuruf („Prüfe den Backlog“). Alternative: Connector über die `mcp`-Fähigkeit anbinden. | klein (Zuruf) / mittel (Connector) |
| O-2 | A-100: Der Spiegel `BACKLOG.md` und `data/` entsteht auf Zuruf, nicht bei jeder Änderung. Versionen werden nicht gespiegelt. | Button „Spiegel anfordern“ in der App legt einen Auftrag an. Vollautomatisch nur mit GitHub-Anbindung der Seite. | klein / groß |
| O-3 | A-102, A-127: Die Umgebung sperrt Fremdhosts, Link-Prüfung und Auswärtiges Amt sind nicht lesbar. | In den Umgebungseinstellungen (Network access) die Domains erlauben oder die Stufe anheben. | klein, Martin |
| O-4 | A-123: Keine echten Gesamtpreise, da für Sommer 2027 noch keine Angebote existieren. | Check ab Winter 2026/27 wiederholen, mit festen Daten und konkretem Hotel. | klein |
| O-5 | A-124: Kinderregeln (Altersgrenzen, Ermäßigungen, Sitz- und Zimmerregeln) nicht recherchiert. | Erst bei konkreten Angeboten recherchieren. | mittel |
| O-6 | A-026: Kein Upload eigener Bilder. | `assets`-Fähigkeit mit Upload-Button an der Reise. | klein bis mittel |
| O-7 | A-110, A-117: Kein wiederkehrender Check, bewusst. | Nur falls gewünscht: geplante Cloud-Aufgabe zweimal pro Woche. | klein |
| O-8 | Echte Reise „Sommer“ (Feb 2027, Strand, Gruppenreise ohne Haushalte) hat einen offenen Optimieren-Auftrag vom 18.10. 14:40. | Auf Zuruf bearbeiten. | klein |
| O-10 | A-137: „Jetzt suchen“ weckt Claude nur, wenn die Sitzung offen ist und Martin Bearbeiter ist. | Ohne Sitzung bleibt der Auftrag liegen, die App sagt das. Dauerhaft direkt nur mit eigener Cloud-Aufgabe, die auf Aufträge reagiert. | klein bis mittel |
| O-9 | Veröffentlichte App nicht im echten Viewer getestet. | 10-Minuten-Klicktest laut `qa/regressionstests.md`. | klein, Martin |

## Meine Entscheidungen (Fragen an Martin)

1. Darf ich die `[TEST]`-Daten jetzt löschen (Reise, 3 Personen, Plan, Backlog, Preise, Digest, Vorschläge)?
2. Soll ich den offenen Optimieren-Auftrag für deine echte Reise „Sommer“ (Feb 2027) bearbeiten?
3. Darf die Umgebung Fremdhosts erreichen (O-3), damit Link-Prüfung und Einreisehinweise möglich sind?
4. Soll es doch einen wiederkehrenden Check geben (O-7), oder bleibt es bei „nur auf Zuruf“?
5. Soll ich den Button „Spiegel anfordern“ einbauen (O-2) und Bild-Upload (O-6)?

## Nächster Schritt

Du machst den 10-Minuten-Klicktest im Live-Link, beantwortest die Fragen 1 bis 5, danach räume ich die Testdaten auf und baue, was du freigibst.

## Anforderungen im Detail

| ID | Anforderung | Status | Beleg | Bemerkung |
|---|---|---|---|---|
| A-001 | Die App ist im Browser erreichbar und ohne Programmierkenntnisse nutzbar (Vorgabe: lokal, Entscheidung: privater Artifact-Link). | Erfüllt | Artifact-Link Version 3; Live-Nutzung: Reise „Sommer“ am 18.10. 14:40 in der Datenbank (trips/pld312…) | Abweichung von „lokal“ ist Entscheidung von Martin (Hosting online). |
| A-002 | Frontend in HTML mit Backend-Speicher (Vorgabe: FastAPI/Flask, Entscheidung: Artifact-Datenbank). | Erfüllt | Artifact-Datenbank; ArtifactData-Lesen als Admin und als „view“ getestet | Statt FastAPI/Flask, Entscheidung Hosting. |
| A-003 | Kein Streamlit im Betrieb. | Erfüllt | `legacy/` enthält nur den archivierten Prototyp; README |  |
| A-004 | Die Oberfläche ist responsive und mobil nutzbar. | Erfüllt | Browser-Test: Handy: Kacheln einspaltig (1 Spalte) |  |
| A-005 | Hell- und Dunkelmodus sind vorhanden. | Erfüllt | Browser-Test: Dunkelmodus folgt System (rgb(22, 21, 20)) (+1 weitere) |  |
| A-006 | `data/trips.json` ist vorhanden und valide. | Erfüllt | `python3 qa/check_daten.py`: Keine Fehler (2 Reisen, 3 Personen, 4 Preise, 3 Backlog) | Versionen und Preisverlauf liegen in eigenen Sammlungen, nicht in trips.json (siehe O-2). |
| A-007 | `data/travelers.json` ist vorhanden und valide. | Erfüllt | `qa/check_daten.py`: Keine Fehler |  |
| A-008 | `data/plans/<reise-id>.json` wird für Reisepläne geschrieben. | Erfüllt | Spiegel in Kopie mit Testdaten: `data/plans/test_sommer2027.json`; `check_daten.py` ohne Fehler | Im Repo liegt noch kein Plan, da keine echte Reise einen hat. |
| A-009 | `data/backlog.json` ist vorhanden und valide. | Erfüllt | `qa/check_daten.py`: Keine Fehler |  |
| A-010 | `BACKLOG.md` ist im Projektroot vorhanden. | Erfüllt | `BACKLOG.md` vorhanden, 10/10 Einträge passen zu `backlog.json` (Kopie mit Testdaten) |  |
| A-011 | `digests/` enthält Check-Berichte als Markdown. | Erfüllt | `scripts/spiegel.py` schreibt `digests/<datum>_<reise>.md` (Retest: 2 Dateien in Kopie, 1 im Repo) | Mangel M-05, behoben in Schleife 3. |
| A-012 | `CLAUDE.md` enthält Zweck, Datenstruktur, Regeln und Verweis auf `BACKLOG.md`. | Erfüllt | `CLAUDE.md`: Zweck, Datenstruktur, Regeln, Verweis auf `BACKLOG.md` |  |
| A-013 | `CLAUDE.md` hat den Abschnitt „Präferenzen“. | Erfüllt | `CLAUDE.md`, Abschnitt „Präferenzen“ | Noch keine Bewertungen vorhanden. |
| A-014 | Alle sichtbaren Texte der App sind deutsch. | Erfüllt | Durchsicht Quelltext und Screens: alle sichtbaren Texte deutsch |  |
| A-015 | Neue Reisen starten mit den Abflughäfen Köln/Bonn und Düsseldorf. | Erfüllt | Browser-Test: Standard-Abflughäfen CGN und DUS |  |
| A-016 | Die Startseite zeigt ein Raster, eine Kachel je Reise. | Erfüllt | Browser-Test: Leere Startseite zeigt verständlichen Leerzustand (+2 weitere) |  |
| A-017 | Kachel: große Bildfläche oben, abgerundete Ecken, Hover-Effekt. | Erfüllt | Browser-Test: Abgerundete Bildfläche 4:3 mit 16px Radius (+1 weitere) |  |
| A-018 | Kachel zeigt den Titel. | Erfüllt | Browser-Test: Raster mit 4 Karten; Titel, Ziel, Zeitraum auf Kachel |  |
| A-019 | Kachel zeigt das Ziel. | Erfüllt | Browser-Test: Raster mit 4 Karten; Titel, Ziel, Zeitraum auf Kachel |  |
| A-020 | Kachel zeigt den Zeitraum. | Erfüllt | Browser-Test: Raster mit 4 Karten; Titel, Ziel, Zeitraum auf Kachel |  |
| A-021 | Kachel zeigt Avatare der Mitreisenden. | Erfüllt | Browser-Test: Avatare der Mitreisenden (3) |  |
| A-022 | Kachel zeigt ein Status-Badge (Idee, Recherche, Beobachten, Buchungsreif, Gebucht). | Erfüllt | Browser-Test: Status-Badge |  |
| A-023 | Kachel zeigt den aktuellen Bestpreis („ab … pro Person / gesamt“). | Erfüllt | Browser-Test: Bestpreis „ab 700 € p. P. · 2.100 € gesamt“: 🏖️ Beobachten [TEST] Sommer 2027 Mallorca · 19.7. – 31.8. M K M ab 700 € p. P. · 2.100 € gesamt · Richtwe |  |
| A-024 | Kachel zeigt einen Trendpfeil (günstiger/teurer seit letztem Check). | Erfüllt | Browser-Test: Trend: Tal ↓ (800→700), Rom ↑ (300→350) |  |
| A-025 | Kachel zeigt das Datum des letzten Checks. | Erfüllt | Browser-Test: Datum des letzten Checks |  |
| A-026 | Bilder nur lizenzfrei oder eigene Uploads, sonst Farbverlauf mit Emoji, keine Portalbilder. | Teilweise | Browser-Test: Farbverlauf mit Emoji, keine Portalbilder | Kein Upload eigener Bilder (Unsplash gestrichen). O-6. |
| A-027 | Filter nach Status. | Erfüllt | Browser-Test: Filter Status „Gebucht“ → 1 Kachel |  |
| A-028 | Filter nach Mitreisenden. | Erfüllt | Browser-Test: Filter Mitreisende „Matteo“ → 1 Kachel |  |
| A-029 | Suche. | Erfüllt | Browser-Test: Suche „rom“ → 1 Kachel |  |
| A-030 | Sortierung nach Datum, Preis und zuletzt aktualisiert. | Erfüllt | Browser-Test: Sortierung nach Preis: ['[TEST] Städtetrip Rom', '[TEST] Sommer 2027', '[TEST] Skiurlaub'] (+2 weitere) |  |
| A-031 | Die erste Kachel ist „+ Neue Reise“ und öffnet die Eingabemaske. | Erfüllt | Browser-Test: Kachel „+ Neue Reise“ ist die erste Kachel (+1 weitere) |  |
| A-032 | Kachelmenü: Öffnen. | Erfüllt | Browser-Test: Kachelmenü: ['Öffnen', 'Jetzt suchen', 'Optimieren', 'Duplizieren', 'Archivieren'] |  |
| A-033 | Kachelmenü: Optimieren. | Erfüllt | Browser-Test: Kachelmenü: ['Öffnen', 'Jetzt suchen', 'Optimieren', 'Duplizieren', 'Archivieren'] (+1 weitere) |  |
| A-034 | Kachelmenü: Duplizieren. | Erfüllt | Browser-Test: Kachelmenü: ['Öffnen', 'Jetzt suchen', 'Optimieren', 'Duplizieren', 'Archivieren'] (+1 weitere) |  |
| A-035 | Kachelmenü: Archivieren (und Wiederherstellen). | Erfüllt | Browser-Test: Kachelmenü: ['Öffnen', 'Jetzt suchen', 'Optimieren', 'Duplizieren', 'Archivieren'] (+3 weitere) |  |
| A-036 | Detailansicht mit den Tabs Übersicht, Angebote, Reiseplan, Backlog, Verlauf. | Erfüllt | Browser-Test: Detail-Tabs: ['Übersicht', 'Angebote', 'Reiseplan', 'Backlog', 'Verlauf'] |  |
| A-037 | Preisverlauf als kleine Kurve in der Kachel. | Erfüllt | Browser-Test: Preisverlauf-Kurve in der Kachel |  |
| A-038 | Preisverlauf als Kurve im Tab „Angebote“. | Erfüllt | Browser-Test: Preisverlauf-Kurve im Tab Angebote |  |
| A-039 | Feld Titel (Pflicht). | Erfüllt | Browser-Test: Eingabemaske hat Feld „Titel der Reise“ (+1 weitere) |  |
| A-040 | Zeitraum: frühester Start, spätester Rückflug, Dauer von/bis, Flexibilität ± Tage. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Frühester Start“ (+3 weitere) |  |
| A-041 | Reiseziele: konkret, Region oder „offen“. | Erfüllt | Browser-Test: Ziele konkret/Region/offen |  |
| A-042 | Reiseart mit allen 7 Optionen. | Erfüllt | Browser-Test: Alle 7 Reisearten: ['Strand', 'Städtetrip', 'Natur/Aktiv', 'Rundreise', 'Skifahren', 'Wellness', 'Sonstiges'] |  |
| A-043 | Budget gesamt und maximal pro Person. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Budget gesamt“ (+1 weitere) |  |
| A-044 | Unterkunft: Typ, Mindeststandard (Sterne/Bewertung), Verpflegung. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Mindest-Sterne“ (+2 weitere) |  |
| A-045 | Anreise: Flug/Bahn/Auto, Direktflug, maximale Reisezeit. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Direktflug“ (+2 weitere) |  |
| A-046 | Muss-Kriterien und No-Gos. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Muss-Kriterien“ (+1 weitere) |  |
| A-047 | Preisalarm-Schwelle, Standard 10 %. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Alarm ab Preisfall“ (+1 weitere) |  |
| A-048 | Check-Rhythmus, Standard 2× pro Woche. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Checks pro Woche“ (+1 weitere) |  |
| A-049 | Status und Notizen. | Erfüllt | Browser-Test: Eingabemaske hat Feld „Notizen“ (+1 weitere) |  |
| A-050 | Validierung: Rückreise liegt nicht vor der Hinreise. | Erfüllt | Browser-Test: Rückreise vor Hinreise abgelehnt: „Der früheste Start liegt nach dem spätesten Rückflug.“ |  |
| A-051 | Validierung: Dauer „von“ nicht größer als „bis“. | Erfüllt | Browser-Test: Dauer von > bis abgelehnt: „Dauer „von“ ist größer als „bis“.“ |  |
| A-052 | Validierung: Kind ohne Alter wird abgelehnt. | Erfüllt | Browser-Test: Kind ohne Alter abgelehnt: „Bei Kindern ist das Alter Pflicht: Kind ohne Alter“ |  |
| A-053 | Reise ohne Budget ist möglich und wird verständlich angezeigt. | Erfüllt | Browser-Test: Reise ohne Budget zeigt „Offen: Budget richtet sich nach dem Angebot“ |  |
| A-054 | Datum in der Vergangenheit wird erkannt und gemeldet. | Erfüllt | Browser-Test: Datum in der Vergangenheit gemeldet oder abgelehnt (Toast: „Das Datum liegt in der Vergangenheit. Bitte einen künftigen Zeitraum wählen.“, gespeichert |  |
| A-055 | Bearbeiten speichert Änderungen. | Erfüllt | Browser-Test: Gültige Reise wird gespeichert (+1 weitere) |  |
| A-056 | Sehr lange Titel und Sonderzeichen brechen das Layout nicht und werden nicht als HTML ausgeführt. | Erfüllt | Browser-Test: Sonderzeichen werden nicht als HTML ausgeführt (+1 weitere) |  |
| A-057 | Wiederverwendbare Personenliste, pro Reise auswählbar. | Erfüllt | Browser-Test: Personenliste mit Martin, Kristina, Matteo |  |
| A-058 | Felder Name, Beziehung, Alter; bei Kindern Alter zwingend. | Erfüllt | Browser-Test: Maske fragt keine Dokumentnummern ab (+2 weitere) |  |
| A-059 | Besonderheiten: Ernährung, Mobilität, Allergien, Interessen. | Erfüllt | Browser-Test: Person mit Besonderheiten, Veto und Ablaufdatum gespeichert, keine Nummernfelder |  |
| A-060 | Wunsch oder Veto zur Reise (optional). | Erfüllt | Browser-Test: Person mit Besonderheiten, Veto und Ablaufdatum gespeichert, keine Nummernfelder |  |
| A-061 | Reisedokument nur als Ablaufdatum, keine Dokumentnummern. | Erfüllt | Browser-Test: Person mit Besonderheiten, Veto und Ablaufdatum gespeichert, keine Nummernfelder |  |
| A-062 | Martin, Kristina und Matteo sind vorbefüllt. | Erfüllt | Browser-Test: Personenliste mit Martin, Kristina, Matteo |  |
| A-063 | Alter und Besonderheiten wurden erst nach Rückfrage bei Martin eingetragen. | Erfüllt | Chat-Verlauf: Alter und Geburtsmonat von Martin genannt; `data/travelers.json`: Besonderheiten leer |  |
| A-064 | Gruppenreise: mehrere Haushalte. | Erfüllt | Browser-Test: Gruppenreise: Haushalte, Budgets, Wünsche, Kostenaufteilung sichtbar |  |
| A-065 | Gruppenreise: getrennte Budgets je Haushalt. | Erfüllt | Browser-Test: Gruppenreise: Haushalte, Budgets, Wünsche, Kostenaufteilung sichtbar |  |
| A-066 | Gruppenreise: gemeinsame Wünsche. | Erfüllt | Browser-Test: Gruppenreise: Haushalte, Budgets, Wünsche, Kostenaufteilung sichtbar |  |
| A-067 | Gruppenreise: Kostenaufteilung als einfache Übersicht. | Erfüllt | Browser-Test: Gruppenreise: Haushalte, Budgets, Wünsche, Kostenaufteilung sichtbar |  |
| A-068 | Button „Optimieren“ auf Kachel und in der Detailansicht. | Erfüllt | Browser-Test: Optimieren legt Auftrag für genau diese Reise ab |  |
| A-069 | Der Button startet einen Auftrag für genau diese Reise. | Erfüllt | Browser-Test: Optimieren legt Auftrag für genau diese Reise ab |  |
| A-070 | Das Team sucht Alternativen: Zeitraum ± Flexibilität, Flughafen, ähnliche Unterkunft, Nachbarort. | Teilweise | Test-Lauf `[TEST] Sommer 2027`: Vorschläge zu Zeitraum, Flugtermin, Reisemonat | Flughafen, Unterkunft, Nachbarort nicht belegbar, da keine 2027-Preise vorliegen. |
| A-071 | Höchstens 3 Vorschläge, jeder mit konkretem Effekt. | Teilweise | Browser-Test: max. 3 Vorschläge mit Effekt; Test-Lauf: 3 Vorschläge | Effekte im Live-Lauf nur qualitativ, kein €-Betrag möglich (keine 2027-Preise). |
| A-072 | Jeder Vorschlag hat Annehmen, Ablehnen, Später. | Erfüllt | Browser-Test: 3 Vorschläge mit Effekt und Annehmen/Ablehnen/Später (+2 weitere) |  |
| A-073 | Ohne Okay ändert sich nichts an der Reise. | Erfüllt | Browser-Test: Optimieren ändert die Reise nicht ohne Okay (+1 weitere) |  |
| A-074 | Jede Änderung speichert eine Version mit Wer, Was, Wann. | Erfüllt | Browser-Test: Versionen mit Wer/Was/Wann: 2 (+1 weitere) |  |
| A-075 | Rückgängig ist jederzeit möglich. | Erfüllt | Browser-Test: Rückgängig stellt Budget „offen“ wieder her (+1 weitere) |  |
| A-076 | Freitextfeld „Verbessere diese Reise: …“. | Erfüllt | Browser-Test: Freitext-Wunsch wird als Auftrag abgelegt |  |
| A-077 | Tagesansicht Tag 1 bis n. | Erfüllt | Browser-Test: Plan: Leerzustand mit nächster Aktion (+1 weitere) |  |
| A-078 | Eintragstypen Anreise, Check-in, Aktivität, Restaurant, Pause, Rückreise. | Erfüllt | Browser-Test: Einträge mit Typ, Status, Teilnehmer gespeichert |  |
| A-079 | Eintragsfelder: Titel, Uhrzeit, Dauer, Ort mit Kartenlink, Kosten, Link, Notiz. | Erfüllt | Browser-Test: Einträge mit Typ, Status, Teilnehmer gespeichert (+1 weitere) |  |
| A-080 | Buchungsstatus offen, reserviert, gebucht. | Erfüllt | Browser-Test: Einträge mit Typ, Status, Teilnehmer gespeichert |  |
| A-081 | Teilnehmer je Eintrag. | Erfüllt | Browser-Test: Einträge mit Typ, Status, Teilnehmer gespeichert |  |
| A-082 | Kinderrhythmus: Hinweis bei mehr als 2 festen Programmpunkten pro Tag. | Erfüllt | Browser-Test: Hinweis bei mehr als 2 festen Programmpunkten (Tag 2 hat 3) (+1 weitere) |  |
| A-083 | Das Team erstellt einen Entwurf aus Ziel, Zeitraum, Mitreisenden und Backlog. | Erfüllt | Browser-Test: Plan: „Entwurf vom Team“ legt Auftrag an (+1 weitere) |  |
| A-084 | Verschieben per Drag & Drop. | Erfüllt | Browser-Test: Drag & Drop verschiebt Eintrag in anderen Tag |  |
| A-085 | Änderung per Freitext („Tag 3 ruhiger“). | Teilweise | Browser-Test: „Tag 3 ruhiger“ legt Auftrag ab | Umsetzung durch das Team auf Zuruf nicht gesondert getestet. |
| A-086 | Wetter-/Saisonhinweis mit Quelle. | Erfüllt | Browser-Test: Wetter- und Öffnungszeiten-Hinweise werden mit Quelle im Plan angezeigt |  |
| A-087 | Öffnungszeiten und Ruhetage mit Quelle. | Teilweise | Browser-Test: Hinweis mit Quelle wird angezeigt; Test-Plan: „noch nicht geprüft“ | Keine konkreten Ziele gewählt, daher keine Öffnungszeiten. |
| A-088 | Packliste nach Reiseart und Personen. | Erfüllt | Browser-Test: Packliste nach Reiseart (Strand) und Kind: 12 Einträge (+1 weitere) |  |
| A-089 | Dokument-Checkliste (Pässe, Versicherung, Einreisehinweise mit Quelle). | Erfüllt | Browser-Test: Dokument-Checkliste mit Quelle Auswärtiges Amt | Inhalt der Quelle konnte nicht gelesen werden, siehe A-127. |
| A-090 | Kostenübersicht: Summe der Posten gegen Budget. | Erfüllt | Browser-Test: Kostensumme 810 € sichtbar: „810 € Kein festes Budget hinterlegt Tag Plan vom Team Kalender (.ics) PDF Kurzve“ |  |
| A-091 | Kostenampel: im Rahmen, knapp, drüber. | Erfüllt | Browser-Test: Kostensumme 810 € sichtbar: „810 € Kein festes Budget hinterlegt Tag Plan vom Team Kalender (.ics) PDF Kurzve“ (+1 weitere) |  |
| A-092 | Export als PDF. | Erfüllt | Browser-Test: PDF-Export-Schaltfläche vorhanden (+1 weitere) |  |
| A-093 | Export als .ics. | Erfüllt | Browser-Test: .ics: 6 Termine, gültiger Aufbau |  |
| A-094 | Teilbare Kurzversion. | Erfüllt | Browser-Test: Kurzversion enthält Tage und Einträge |  |
| A-095 | Eintragstypen: Link, Idee, Artikel, Video, Unterkunft, Restaurant, Aktivität, Aufgabe, Notiz. | Erfüllt | Browser-Test: Backlog-Typen vollständig |  |
| A-096 | Felder: Titel, URL, Notiz, Tags, Zuordnung zu Reisen, Priorität, Status, Datum. | Erfüllt | Browser-Test: Backlog-Felder: Titel, URL, Notiz, Tags, Reisen, Priorität, Status (+1 weitere) |  |
| A-097 | Quick-Add für Link oder Text. | Erfüllt | Browser-Test: 5 Links und 1 Text per Quick-Add: 6 Einträge |  |
| A-098 | Quick-Add holt Titel und Kurzbeschreibung automatisch. | Teilweise | Browser-Test: Titel nur aus der URL, keine Kurzbeschreibung | Die App darf keine Fremdseiten abrufen. Kurzfassung auf Zuruf durch das Team. O-1. |
| A-099 | Ansicht global und pro Reise. | Erfüllt | Browser-Test: Backlog-Tab mit Quick-Add (+3 weitere) |  |
| A-100 | `data/backlog.json` und `BACKLOG.md` bleiben nach jeder Änderung synchron. | Teilweise | Kopie mit Testdaten: 10 Einträge in `BACKLOG.md` = 10 in `backlog.json` | Spiegel läuft nur auf Zuruf, nicht automatisch bei jeder Änderung. O-2. |
| A-101 | `BACKLOG.md` ist nach Reise und Status gruppiert. | Erfüllt | `BACKLOG.md`: gruppiert nach Reise, dann Status |  |
| A-102 | Team prüft neue Links, fasst in 2 Sätzen zusammen, notiert Preis und Verfügbarkeit. | Nicht prüfbar | WebFetch: `getaddrinfo ENOTFOUND`; curl: `CONNECT tunnel failed, response 403` | Netzwerkrichtlinie der Umgebung blockiert Fremdhosts. Ersatz: Zusammenfassung aus Suchergebnissen, so gekennzeichnet. O-3. |
| A-103 | Team schlägt passende Reise vor und übernimmt Einträge in den Reiseplan. | Erfüllt | Browser-Test: Backlog-Eintrag wird in Tag 2 des Plans übernommen, Status „übernommen“ |  |
| A-104 | Tote oder veraltete Links werden markiert. | Erfüllt | Browser-Test: Tote und nicht abrufbare Links werden unterschiedlich markiert |  |
| A-105 | Monatlich 3 Impulse mit Ziel, Grund, Preisrahmen, bestem Zeitraum und einem Nachteil. | Erfüllt | Browser-Test: Ziel, Grund, Preisrahmen, Zeitraum, Nachteil; 3 Impulse in der Datenbank | Lieferung auf Zuruf. |
| A-106 | Daumen hoch/runter bei Impulsen. | Erfüllt | Browser-Test: Daumen hoch speichert Bewertung und zeigt gelernte Vorlieben |  |
| A-107 | Lerneffekt wird in `CLAUDE.md` unter „Präferenzen“ festgehalten. | Teilweise | Browser-Test: „Gelernte Vorlieben“ in der App; `CLAUDE.md` hat den Abschnitt | `CLAUDE.md` wird nur auf Zuruf aktualisiert, noch keine Bewertungen. |
| A-108 | Duplikate werden erkannt. | Erfüllt | Browser-Test: Duplikat-Link wird nicht doppelt angelegt (Toast: „Das ist schon im Backlog.“) |  |
| A-109 | Jeder Preis hat Quelle und Abrufdatum. | Erfüllt | Browser-Test: Angebote zeigen Stand-Datum, Quelle und „unsicher“ |  |
| A-110 | Der Check läuft für „Beobachten“ im eingestellten Rhythmus (Entscheidung: nur auf Zuruf). | Teilweise | Eingabefeld vorhanden (Standard 2×); `list_triggers`: kein Urlaubs-Check geplant | Läuft bewusst nur auf Zuruf (Entscheidung Martin). |
| A-111 | Preisverlauf wird gespeichert (Datum, Anbieter, Preis, Link). | Erfüllt | `prices`-Dokumente mit datum, anbieter, preis_pp, link (`test_pr1`, `pr1`–`pr4`) |  |
| A-112 | Preisverlauf wird in der App angezeigt. | Erfüllt | Browser-Test: Preisverlauf-Kurve im Tab Angebote |  |
| A-113 | Meldung nur bei Relevantem (Schwelle, Angebot unter Budget, Verfügbarkeit, Aktionsende). | Teilweise | Schwelle gespeichert; Regel in `CLAUDE.md`, `team/preisjaeger.md` | Automatische Erkennung und Push nicht gebaut und nicht getestet, nur beim Team-Lauf. |
| A-114 | Digest als Markdown in `digests/`. | Erfüllt | `digests/2026-10-18_trip_sommer2027.md`; Kopie: zwei Dateien nach Lauf von `spiegel.py` | Mangel M-05, behoben. |
| A-115 | Digest in der App sichtbar. | Erfüllt | Browser-Test: Digest in der App (Empfehlung, Top 3), Skript im Digest wirkungslos |  |
| A-116 | Digest: Top 3, Veränderung seit letztem Check, Empfehlung jetzt buchen/abwarten/anpassen. | Erfüllt | Browser-Test: Digest in der App (Empfehlung, Top 3), Skript im Digest wirkungslos |  |
| A-117 | Wiederkehrender Lauf eingerichtet und Start/Stopp erklärt (Entscheidung: bewusst nicht eingerichtet). | Teilweise | `list_triggers`: nur „Tägliche Lerneinheit“ (nicht aus diesem Projekt) | Bewusst nicht eingerichtet (Entscheidung Martin). Start im Chat in der README erklärt. |
| A-118 | Ehrliche Hinweise bei nicht lesbaren Portalen oder unsicheren Preisen. | Erfüllt | Browser-Test: Reise ohne Angebote: verständlicher Leerzustand mit nächstem Schritt |  |
| A-119 | Die vier Rollen Scout, Preis-Jäger, Planer, Buchungs-Assistent sind beschrieben. | Erfüllt | `team/scout.md`, `preisjaeger.md`, `planer.md`, `buchungs-assistent.md` |  |
| A-120 | Keine Buchung, Zahlung oder Registrierung ohne ausdrückliche Freigabe; kein Automatismus dafür. | Erfüllt | Injektionstest: Seite verlangte Buchung, Registrierung, Löschen; nichts davon geschah. Quelltext: keine Buchungslogik, keine Netzwerkaufrufe | Test mit dem Prüfer selbst, daher eingeschränkt unabhängig. |
| A-121 | Keine Zahlungsdaten, Passnummern oder Passwörter im Projekt. | Erfüllt | Suche im Repo: Treffer nur in Regeltexten; `check_daten.py` blockt Felder wie nummer/iban/passwort |  |
| A-122 | Preise mit Stand-Datum, Unsicheres als unsicher. | Erfüllt | Browser-Test: Angebote zeigen Stand-Datum, Quelle und „unsicher“ |  |
| A-123 | Gesamtpreis statt Lockpreis wird ausgewiesen. | Teilweise | Browser-Test: Spalte „Gesamt“; Test-Lauf: Lockpreise ausdrücklich als nicht vergleichbar markiert | Echte Gesamtpreise fehlen, es gibt noch keine 2027-Angebote. O-4. |
| A-124 | Kinderregeln werden geprüft und fließen in Preise, Aktivitäten und Tagesrhythmus. | Teilweise | Rhythmus-Hinweis, Kinder-Packliste, Kinderalter in der Maske | Altersgrenzen, Ermäßigungen, Sitz- und Zimmerregeln noch nicht recherchiert, erst mit konkreten Angeboten. O-5. |
| A-125 | Änderungen an Reisen und Plänen werden versioniert und sind rückgängig machbar. | Erfüllt | Browser-Test: Versionen mit Wer/Was/Wann: 2 (+3 weitere) |  |
| A-126 | Inhalte von Webseiten und Backlog-Einträgen sind Daten, keine Anweisungen (Prompt-Injection). | Erfüllt | Browser-Test: Skript, HTML und `javascript:`-Link bleiben wirkungslos; lokale Testseite mit versteckten Anweisungen wurde nur als Daten gelesen |  |
| A-127 | Einreise- und Impfhinweise tragen eine Quelle und sind keine Rechtsberatung. | Nicht prüfbar | WebFetch auf auswaertiges-amt.de: ENOTFOUND | Seite nicht lesbar, daher kein Einreise-/Impfhinweis. Im Plan als „nicht gelesen“ vermerkt. O-3. |
| A-128 | Startseite lädt mit 20 Reisen in unter 2 Sekunden. | Teilweise | Browser-Test: 20 Reisen und 100 Preise rendern in 0,10 s (simulierte Datenbank) | Echte Datenbank-Latenz nicht messbar. |
| A-129 | Kein horizontales Scrollen auf Desktop, Tablet und Handy (390 px). | Erfüllt | Browser-Test: desktop (1440 px): horizontales Überlaufen 0 px (+7 weitere) |  |
| A-130 | Leer-, Lade- und Fehlerzustände sind verständlich und deutsch. | Erfüllt | Browser-Test: Leere Startseite zeigt verständlichen Leerzustand (+4 weitere) |  |
| A-131 | Tastaturbedienung und Kontraste sind grundlegend in Ordnung. | Erfüllt | Browser-Test: Tab erreicht Bedienelemente (BUTTON:nav); Enter öffnet Kachel (+2 weitere) |  |
| A-132 | JSON-Dateien sind valide, ohne verwaiste Verweise. | Erfüllt | `python3 qa/check_daten.py`: Keine Fehler, auch in Kopie mit Testdaten |  |
| A-133 | Keine Zugangsdaten oder API-Schlüssel im Repo, `.gitignore` korrekt. | Erfüllt | Suche nach Schlüsseln, Passwörtern, IBAN; `.gitignore` mit `.env`, `*.pem`, `*.key`; keine solchen Dateien getrackt |  |
| A-134 | Ungültige Eingaben führen zu Fehlermeldungen, nicht zu Abstürzen oder Dateizugriff außerhalb des Projekts. | Erfüllt | Browser-Test: Nur-Lesen: keine Schreib-Bedienelemente (+4 weitere) |  |
| A-135 | Airbnb-Anmutung: Weißraum, abgerundete Ecken, ruhige Typografie, konsistente Abstände. | Erfüllt | Browser-Test: Abgerundete Bildfläche 4:3 mit 16px Radius |  |
| A-136 | Die Startseite hat eine Eingabeleiste für einen freien Reisewunsch; sie legt die Reise an. | Erfüllt | Browser-Test: Startseite hat die Suchleiste mit Beispiel im Platzhalter (+2 weitere) |  |
| A-137 | „Jetzt suchen“ (Suchleiste, Detail, Kachelmenü, Optimieren) legt einen Auftrag an und weckt Claude sofort, sonst Rückfall auf den Auftrag mit Hinweis. | Erfüllt | Live am 18.10. 15:22: Suchleiste „Asien“ legte Reise und Auftrag an, der Kommentar „Jetzt suchen“ weckte die Sitzung, Ergebnis (3 Impulse, Digest) und Antwort im Kommentar-Thread folgten; plus 9 Browser-Prüfungen | Wecken nur bei offener Sitzung und Bearbeiter-Rechten, sonst Rückfall auf den Auftrag. O-10. |
