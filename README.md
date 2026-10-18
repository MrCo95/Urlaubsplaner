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

## Regelmäßiger Check (2x pro Woche)
Starten (macOS/Linux, Crontab `crontab -e`, Di und Fr 8:07 Uhr):
```
7 8 * * 2,5  cd ~/Urlaubsplaner && claude -p "$(cat team/check_prompt.md)" --permission-mode acceptEdits
```
Stoppen: Zeile aus der Crontab löschen. Der Rechner muss zur Zeit laufen. Das Intervall pro Reise stellst du in der Maske ein; der Check prüft, welche Reisen fällig sind.

## Grenzen
Portale lassen sich per Websuche nur eingeschränkt auslesen; Preise ohne festes Datum sind Richtwerte und als „unsicher“ markiert. Verlässlich ist die manuelle Prüfung mit festen Daten.
