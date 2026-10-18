# Urlaubs-Team

Lokale Eingabemaske (Streamlit) plus ein Team aus vier Rollen. Daten liegen als JSON im Ordner `data/`.

## Starten und Stoppen der App
```
pip install -r requirements.txt
streamlit run app.py        # öffnet http://localhost:8501
```
Stoppen: `Strg+C` im Terminal.

## Arbeiten mit dem Team
Im Projektordner `claude` starten und z. B. sagen:
- „Scout, 3 neue Vorschläge für diesen Monat“
- „Preis-Jäger, Check für Sommer 2027“
- „Planer, Ablauf und Einreisehinweise für <Reise>“
- „Buchungs-Assistent, bereite <Reise> vor“

Ergebnisse erscheinen in der App (Ideen-Pool, Preise & Digest).

## Suche nur auf Zuruf
Es läuft nichts automatisch. Recherche, Preis-Checks und Vorschläge starten nur, wenn du das Team in einer Sitzung beauftragst („Preis-Jäger, Check für <Reise>“). Es gibt keinen Cron und keine geplante Aufgabe.

## Grenzen
Portale lassen sich per Websuche nur eingeschränkt auslesen; Preise ohne festes Datum sind Richtwerte und als „unsicher“ markiert. Verlässlich ist die manuelle Prüfung mit festen Daten.
