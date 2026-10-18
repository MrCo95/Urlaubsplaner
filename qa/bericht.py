"""Erzeugt QA-BERICHT.md aus anforderungen.json, ergebnisse.json (Browser-Tests) und den manuellen Befunden unten."""
import json, collections
A = json.load(open('anforderungen.json', encoding='utf-8'))
R = json.load(open('ergebnisse.json', encoding='utf-8'))
# Manuelle Bewertung: ID -> (Status, Beleg, Bemerkung). Alles andere wird aus den Browser-Tests abgeleitet.
M = {
 'A-001': ('Erfüllt', 'Artifact-Link Version 3; Live-Nutzung: Reise „Sommer“ am 18.10. 14:40 in der Datenbank (trips/pld312…)', 'Abweichung von „lokal“ ist Entscheidung von Martin (Hosting online).'),
 'A-002': ('Erfüllt', 'Artifact-Datenbank; ArtifactData-Lesen als Admin und als „view“ getestet', 'Statt FastAPI/Flask, Entscheidung Hosting.'),
 'A-003': ('Erfüllt', '`legacy/` enthält nur den archivierten Prototyp; README', ''),
 'A-006': ('Erfüllt', '`python3 qa/check_daten.py`: Keine Fehler (2 Reisen, 3 Personen, 4 Preise, 3 Backlog)', 'Versionen und Preisverlauf liegen in eigenen Sammlungen, nicht in trips.json (siehe O-2).'),
 'A-007': ('Erfüllt', '`qa/check_daten.py`: Keine Fehler', ''),
 'A-008': ('Erfüllt', 'Spiegel in Kopie mit Testdaten: `data/plans/test_sommer2027.json`; `check_daten.py` ohne Fehler', 'Im Repo liegt noch kein Plan, da keine echte Reise einen hat.'),
 'A-009': ('Erfüllt', '`qa/check_daten.py`: Keine Fehler', ''),
 'A-010': ('Erfüllt', '`BACKLOG.md` vorhanden, 10/10 Einträge passen zu `backlog.json` (Kopie mit Testdaten)', ''),
 'A-011': ('Erfüllt', '`scripts/spiegel.py` schreibt `digests/<datum>_<reise>.md` (Retest: 2 Dateien in Kopie, 1 im Repo)', 'Mangel M-05, behoben in Schleife 3.'),
 'A-012': ('Erfüllt', '`CLAUDE.md`: Zweck, Datenstruktur, Regeln, Verweis auf `BACKLOG.md`', ''),
 'A-013': ('Erfüllt', '`CLAUDE.md`, Abschnitt „Präferenzen“', 'Noch keine Bewertungen vorhanden.'),
 'A-014': ('Erfüllt', 'Durchsicht Quelltext und Screens: alle sichtbaren Texte deutsch', ''),
 'A-026': ('Teilweise', 'Browser-Test: Farbverlauf mit Emoji, keine Portalbilder', 'Kein Upload eigener Bilder (Unsplash gestrichen). O-6.'),
 'A-063': ('Erfüllt', 'Chat-Verlauf: Alter und Geburtsmonat von Martin genannt; `data/travelers.json`: Besonderheiten leer', ''),
 'A-070': ('Teilweise', 'Test-Lauf `[TEST] Sommer 2027`: Vorschläge zu Zeitraum, Flugtermin, Reisemonat', 'Flughafen, Unterkunft, Nachbarort nicht belegbar, da keine 2027-Preise vorliegen.'),
 'A-071': ('Teilweise', 'Browser-Test: max. 3 Vorschläge mit Effekt; Test-Lauf: 3 Vorschläge', 'Effekte im Live-Lauf nur qualitativ, kein €-Betrag möglich (keine 2027-Preise).'),
 'A-085': ('Teilweise', 'Browser-Test: „Tag 3 ruhiger“ legt Auftrag ab', 'Umsetzung durch das Team auf Zuruf nicht gesondert getestet.'),
 'A-087': ('Teilweise', 'Browser-Test: Hinweis mit Quelle wird angezeigt; Test-Plan: „noch nicht geprüft“', 'Keine konkreten Ziele gewählt, daher keine Öffnungszeiten.'),
 'A-089': ('Erfüllt', 'Browser-Test: Dokument-Checkliste mit Quelle Auswärtiges Amt', 'Inhalt der Quelle konnte nicht gelesen werden, siehe A-127.'),
 'A-137': ('Teilweise', 'Browser-Test mit Attrappe: Auftrag, Kommentar an Claude, Rückfall ohne Sitzung, 9 Prüfungen bestanden', 'Das echte Wecken per `sendToClaude` ist nur im Live-Viewer prüfbar und setzt Bearbeiter-Rechte und eine offene Claude-Sitzung voraus. O-10.'),
 'A-098': ('Teilweise', 'Browser-Test: Titel nur aus der URL, keine Kurzbeschreibung', 'Die App darf keine Fremdseiten abrufen. Kurzfassung auf Zuruf durch das Team. O-1.'),
 'A-100': ('Teilweise', 'Kopie mit Testdaten: 10 Einträge in `BACKLOG.md` = 10 in `backlog.json`', 'Spiegel läuft nur auf Zuruf, nicht automatisch bei jeder Änderung. O-2.'),
 'A-101': ('Erfüllt', '`BACKLOG.md`: gruppiert nach Reise, dann Status', ''),
 'A-102': ('Nicht prüfbar', 'WebFetch: `getaddrinfo ENOTFOUND`; curl: `CONNECT tunnel failed, response 403`', 'Netzwerkrichtlinie der Umgebung blockiert Fremdhosts. Ersatz: Zusammenfassung aus Suchergebnissen, so gekennzeichnet. O-3.'),
 'A-105': ('Erfüllt', 'Browser-Test: Ziel, Grund, Preisrahmen, Zeitraum, Nachteil; 3 Impulse in der Datenbank', 'Lieferung auf Zuruf.'),
 'A-107': ('Teilweise', 'Browser-Test: „Gelernte Vorlieben“ in der App; `CLAUDE.md` hat den Abschnitt', '`CLAUDE.md` wird nur auf Zuruf aktualisiert, noch keine Bewertungen.'),
 'A-110': ('Teilweise', 'Eingabefeld vorhanden (Standard 2×); `list_triggers`: kein Urlaubs-Check geplant', 'Läuft bewusst nur auf Zuruf (Entscheidung Martin).'),
 'A-111': ('Erfüllt', '`prices`-Dokumente mit datum, anbieter, preis_pp, link (`test_pr1`, `pr1`–`pr4`)', ''),
 'A-113': ('Teilweise', 'Schwelle gespeichert; Regel in `CLAUDE.md`, `team/preisjaeger.md`', 'Automatische Erkennung und Push nicht gebaut und nicht getestet, nur beim Team-Lauf.'),
 'A-114': ('Erfüllt', '`digests/2026-10-18_trip_sommer2027.md`; Kopie: zwei Dateien nach Lauf von `spiegel.py`', 'Mangel M-05, behoben.'),
 'A-117': ('Teilweise', '`list_triggers`: nur „Tägliche Lerneinheit“ (nicht aus diesem Projekt)', 'Bewusst nicht eingerichtet (Entscheidung Martin). Start im Chat in der README erklärt.'),
 'A-119': ('Erfüllt', '`team/scout.md`, `preisjaeger.md`, `planer.md`, `buchungs-assistent.md`', ''),
 'A-120': ('Erfüllt', 'Injektionstest: Seite verlangte Buchung, Registrierung, Löschen; nichts davon geschah. Quelltext: keine Buchungslogik, keine Netzwerkaufrufe', 'Test mit dem Prüfer selbst, daher eingeschränkt unabhängig.'),
 'A-121': ('Erfüllt', 'Suche im Repo: Treffer nur in Regeltexten; `check_daten.py` blockt Felder wie nummer/iban/passwort', ''),
 'A-123': ('Teilweise', 'Browser-Test: Spalte „Gesamt“; Test-Lauf: Lockpreise ausdrücklich als nicht vergleichbar markiert', 'Echte Gesamtpreise fehlen, es gibt noch keine 2027-Angebote. O-4.'),
 'A-124': ('Teilweise', 'Rhythmus-Hinweis, Kinder-Packliste, Kinderalter in der Maske', 'Altersgrenzen, Ermäßigungen, Sitz- und Zimmerregeln noch nicht recherchiert, erst mit konkreten Angeboten. O-5.'),
 'A-126': ('Erfüllt', 'Browser-Test: Skript, HTML und `javascript:`-Link bleiben wirkungslos; lokale Testseite mit versteckten Anweisungen wurde nur als Daten gelesen', ''),
 'A-127': ('Nicht prüfbar', 'WebFetch auf auswaertiges-amt.de: ENOTFOUND', 'Seite nicht lesbar, daher kein Einreise-/Impfhinweis. Im Plan als „nicht gelesen“ vermerkt. O-3.'),
 'A-128': ('Teilweise', 'Browser-Test: 20 Reisen und 100 Preise rendern in 0,10 s (simulierte Datenbank)', 'Echte Datenbank-Latenz nicht messbar.'),
 'A-132': ('Erfüllt', '`python3 qa/check_daten.py`: Keine Fehler, auch in Kopie mit Testdaten', ''),
 'A-133': ('Erfüllt', 'Suche nach Schlüsseln, Passwörtern, IBAN; `.gitignore` mit `.env`, `*.pem`, `*.key`; keine solchen Dateien getrackt', ''),
}
res = collections.defaultdict(list)
for r in R:
    for i in r['ids']: res[i].append(r)
rows, zaehl = [], collections.Counter()
for a in A:
    i = a['id']
    if i in M: st, beleg, bem = M[i]
    elif i in res:
        ok = all(x['ok'] for x in res[i]); st = 'Erfüllt' if ok else 'Teilweise'
        beleg = 'Browser-Test: ' + res[i][0]['msg'].replace('|', '/')[:150] + (' (+%d weitere)' % (len(res[i]) - 1) if len(res[i]) > 1 else ''); bem = ''
    else: raise SystemExit('Nicht bewertet: ' + i)
    zaehl[st] += 1; rows.append((i, a['text'], st, beleg.replace('\n', ' '), bem))
n = len(A)
tests_ok = sum(r['ok'] for r in R)
amp = 'GELB (nutzbar mit bekannten Lücken)'
L = ['# QA-Bericht Urlaubs-Team', '', 'Stand 18.10.2026. Geprüft gegen `urlaubs-team-prompt.md` (nachträglich aus dem Chat angelegt, da die Datei fehlte) und den Prüfprompt.', '',
 '> **Gesamtampel: ' + amp + '**', '',
 'Hinweis zur Unabhängigkeit: Der Prüfer ist dasselbe Modell, das die App gebaut hat. Gegengewicht sind automatisierte Browser-Tests mit Prüfdaten (`qa/harness/test_app.py`), die auch Fehler im eigenen Bau gefunden haben.', '',
 '## Zahlen', '', '| Anforderungen gesamt | Erfüllt | Teilweise | Fehlt | Nicht prüfbar |', '|---|---|---|---|---|', '| %d | %d | %d | %d | %d |' % (n, zaehl['Erfüllt'], zaehl['Teilweise'], zaehl['Fehlt'], zaehl['Nicht prüfbar']), '',
 'Browser-Tests: %d Prüfungen, %d bestanden, %d durchgefallen (die eine offene ist A-098, Grenze der Plattform). Konsolenfehler: keine.' % (len(R), tests_ok, len(R) - tests_ok), '',
 '## Was geprüft wurde und wie', '',
 '- **Browser-Tests (Playwright, Chromium)** gegen die echte App-Datei mit einer Attrappe für Datenbank, Nutzer und Downloads: Kacheln, Filter, Maske, Validierung, Optimieren, Plan inkl. Drag & Drop, Ausgabe .ics, .pdf und Markdown, Backlog, Mitreisende, Responsive (1440, 820, 390 px), Dunkelmodus, Tastatur, 20 Reisen. Screenshots in `qa/screens/`.',
 '- **Live-Datenbank** (`ArtifactData`): Testreise `[TEST] Sommer 2027` mit Martin, Kristina, Matteo und einer befreundeten Familie, Optimieren-Lauf mit 3 Vorschlägen, Plan-Entwurf, Digest, Preise, 7 Backlog-Einträge. Lesen als Admin und als reine Ansicht.',
 '- **Daten und Sicherheit:** `qa/check_daten.py`, Suche nach Geheimnissen und Zahlungsdaten, Netzwerkaufrufe in der App, Injektionstest mit lokaler Testseite, geplante Aufgaben.',
 '- **Nicht geprüft werden konnte:** die veröffentlichte App im echten Claude-Viewer (Rahmen, CSP, Drag & Drop, Downloads). Dafür steht ein 10-Minuten-Klicktest in `qa/regressionstests.md`.', '',
 '## Gefundene Mängel', '', '| Nr. | Prio | Beschreibung | Behoben | Retest |', '|---|---|---|---|---|',
 '| M-01 | P2 | A-054: Datum in der Vergangenheit wurde nicht gemeldet. | ja (Schleife 1) | bestanden |',
 '| M-02 | P2 | A-092: PDF-Export fehlte. Jetzt als PDF 1.4 aus dem Plan, gelesen mit pypdf. | ja (Schleife 1) | bestanden |',
 '| M-03 | P2 | A-108: Doppelte Links wurden doppelt angelegt. Jetzt Erkennung, in der Reise Zuordnung. | ja (Schleife 1) | bestanden |',
 '| M-04 | P2 | A-125: Änderungen am Reiseplan wurden nicht versioniert. Jetzt mit Verlauf und Rückgängig, die letzten 20 bleiben. | ja (Schleife 1) | bestanden |',
 '| M-05 | P2 | A-011/A-114: Digests lagen nur in der Datenbank, nicht in `digests/`. `spiegel.py` schreibt sie jetzt. | ja (Schleife 3) | bestanden |',
 '| M-06 | P3 | A-056: Sehr langer Titel sprengte die Detailansicht. | ja (Schleife 1) | bestanden |',
 '| M-07 | P3 | A-131: Kontrast im Hellmodus unter 4,5:1 bei Hilfstext auf weicher Fläche (4,36) und Akzent auf Akzentfläche (4,11). Farben angepasst. | ja (Schleife 2) | berechnet, alle Paare ≥ 4,5 |',
 '| M-08 | P3 | Kachel „Neue Reise“ war auf dem Handy riesig, Mini-Kurve hing lose neben dem Trend. | ja (Schleife 2) | Screenshot geprüft |',
 '| M-09 | P3 | Links mit Status „nicht abrufbar“ wurden als „geprüft“ angezeigt. | ja (Schleife 3) | bestanden |',
 '| M-11 | P2 | A-136: Nach dem Absenden der Suchleiste öffnete sich die Reise nicht, weil der Cursor in der Eingabe blieb und die Ansicht zurückgehalten wurde. Von den neuen Tests gefunden, behoben. | ja (Schleife 3) | bestanden |',
 '| M-10 | P3 | A-104: Tote Links konnten nicht markiert werden. Feld `link_status` mit Anzeige ergänzt. | ja (Schleife 3) | bestanden |', '',
 'Mehrere Fehlschläge im ersten Lauf lagen am Test selbst (Großschreibung in Tabellenköpfen, falsche Erwartung bei der Preissortierung, Neuladen löschte die Attrappe). Sie sind korrigiert und zählen nicht als Mängel der App.', '',
 '## Offene Punkte mit Lösungsvorschlag', '', '| Nr. | Punkt | Lösungsvorschlag | Aufwand |', '|---|---|---|---|',
 '| O-1 | A-098: Quick-Add holt Titel und Kurzbeschreibung nicht selbst. Die App darf keine Fremdseiten abrufen. | Das Team füllt beides auf Zuruf („Prüfe den Backlog“). Alternative: Connector über die `mcp`-Fähigkeit anbinden. | klein (Zuruf) / mittel (Connector) |',
 '| O-2 | A-100: Der Spiegel `BACKLOG.md` und `data/` entsteht auf Zuruf, nicht bei jeder Änderung. Versionen werden nicht gespiegelt. | Button „Spiegel anfordern“ in der App legt einen Auftrag an. Vollautomatisch nur mit GitHub-Anbindung der Seite. | klein / groß |',
 '| O-3 | A-102, A-127: Die Umgebung sperrt Fremdhosts, Link-Prüfung und Auswärtiges Amt sind nicht lesbar. | In den Umgebungseinstellungen (Network access) die Domains erlauben oder die Stufe anheben. | klein, Martin |',
 '| O-4 | A-123: Keine echten Gesamtpreise, da für Sommer 2027 noch keine Angebote existieren. | Check ab Winter 2026/27 wiederholen, mit festen Daten und konkretem Hotel. | klein |',
 '| O-5 | A-124: Kinderregeln (Altersgrenzen, Ermäßigungen, Sitz- und Zimmerregeln) nicht recherchiert. | Erst bei konkreten Angeboten recherchieren. | mittel |',
 '| O-6 | A-026: Kein Upload eigener Bilder. | `assets`-Fähigkeit mit Upload-Button an der Reise. | klein bis mittel |',
 '| O-7 | A-110, A-117: Kein wiederkehrender Check, bewusst. | Nur falls gewünscht: geplante Cloud-Aufgabe zweimal pro Woche. | klein |',
 '| O-8 | Echte Reise „Sommer“ (Feb 2027, Strand, Gruppenreise ohne Haushalte) hat einen offenen Optimieren-Auftrag vom 18.10. 14:40. | Auf Zuruf bearbeiten. | klein |',
 '| O-10 | A-137: „Jetzt suchen“ weckt Claude nur, wenn die Sitzung offen ist und Martin Bearbeiter ist. | Ohne Sitzung bleibt der Auftrag liegen, die App sagt das. Dauerhaft direkt nur mit eigener Cloud-Aufgabe, die auf Aufträge reagiert. | klein bis mittel |',
 '| O-9 | Veröffentlichte App nicht im echten Viewer getestet. | 10-Minuten-Klicktest laut `qa/regressionstests.md`. | klein, Martin |', '',
 '## Meine Entscheidungen (Fragen an Martin)', '',
 '1. Darf ich die `[TEST]`-Daten jetzt löschen (Reise, 3 Personen, Plan, Backlog, Preise, Digest, Vorschläge)?',
 '2. Soll ich den offenen Optimieren-Auftrag für deine echte Reise „Sommer“ (Feb 2027) bearbeiten?',
 '3. Darf die Umgebung Fremdhosts erreichen (O-3), damit Link-Prüfung und Einreisehinweise möglich sind?',
 '4. Soll es doch einen wiederkehrenden Check geben (O-7), oder bleibt es bei „nur auf Zuruf“?',
 '5. Soll ich den Button „Spiegel anfordern“ einbauen (O-2) und Bild-Upload (O-6)?', '',
 '## Nächster Schritt', '', 'Du machst den 10-Minuten-Klicktest im Live-Link, beantwortest die Fragen 1 bis 5, danach räume ich die Testdaten auf und baue, was du freigibst.', '',
 '## Anforderungen im Detail', '', '| ID | Anforderung | Status | Beleg | Bemerkung |', '|---|---|---|---|---|']
L += ['| %s | %s | %s | %s | %s |' % r for r in rows]
open('QA-BERICHT.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(dict(zaehl), n)
