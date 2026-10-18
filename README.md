# Urlaubs-Team

Online-App für Reisen als Kacheln, mit Eingabemaske, Angebote, Reiseplan und Backlog. Läuft als privater Link auf claude.ai, auch mobil: https://claude.ai/artifact/92MSpqUCs1n142JsRGzEZZ

## Nutzung
- **Reisen:** Kachel-Startseite mit Filter, Suche und Sortierung. „+ Neue Reise“ öffnet die Eingabemaske. Jede Kachel hat ein Menü (Öffnen, Optimieren, Duplizieren, Archivieren).
- **Detailansicht:** Übersicht, Angebote (Digest, Preisverlauf), Reiseplan (Tage, Drag & Drop, Kosten-Ampel, Packliste, Dokument-Checkliste, Export .ics und Kurzversion), Backlog, Verlauf mit „Rückgängig“.
- **Mitreisende:** wiederverwendbare Personenliste.
- **Backlog:** Links, Ideen und Fundstücke einwerfen, global oder je Reise.

## Das Team arbeitet nur auf Zuruf
Die App legt Aufträge ab, zum Beispiel über „Optimieren“. Im Chat mit Claude Code sagst du dann: „Optimiere Sommer 2027“, „Preis-Jäger, Check für Sommer 2027“, „Prüfe den Backlog“ oder „Planer, Entwurf für <Reise>“. Es läuft nichts automatisch.

## Dateien
- `app/urlaubs-team.html`: Quelle der App
- `CLAUDE.md`: Regeln und Datenstruktur für Claude
- `BACKLOG.md`, `data/`: lesbarer Spiegel der Daten, aktualisiert mit `python3 scripts/spiegel.py <Exportordner>`
- `legacy/`: erster Streamlit-Prototyp (nicht mehr in Gebrauch)

## Grenzen
- Portale lassen sich per Websuche nur eingeschränkt auslesen. Preise ohne festes Datum sind Richtwerte und als „unsicher“ markiert. Verlässlich ist die manuelle Prüfung mit festen Daten.
- Die App kann keine Webseiten selbst abrufen und kein PDF erzeugen. Titel und Kurzfassung neuer Links holt das Team auf Zuruf. Exportiert wird als Kalenderdatei (.ics) und als Markdown-Kurzversion.
- Bilder: Farbverlauf mit Emoji. Eigene Uploads und lizenzfreie Quellen sind noch nicht angebunden.
