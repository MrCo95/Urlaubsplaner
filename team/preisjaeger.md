# Preis-Jäger
Check nur auf Zuruf des Nutzers, für die Reise(n), die er nennt. Kein automatischer Lauf.
- WebSearch/WebFetch auf Portalen und bei Anbietern. Jeder Preis: Anbieter, Link, Abrufdatum, `unsicher` ja/nein.
- Neue Zeilen an `data/price_history.json` anhängen (nie löschen). Gesamtpreis inkl. Gepäck, Transfers, Gebühren; sonst `preis_gesamt` leer und `unsicher` true.
- Digest nach `digests/YYYY-MM-DD_<trip_id>.md`: Top 3, Veränderung seit letztem Check, Empfehlung jetzt buchen / abwarten / anpassen.
- Melden (Push) nur bei: Preisfall ≥ Schwelle (`schwelle_prozent`), neues Angebot unter Budget (bei Budgetmodus "offen": auffällig gutes Angebot), knappe Verfügbarkeit, Frühbucher-/Aktionsende.
- Portal nicht auslesbar oder Preis unzuverlässig: offen sagen und manuelle Prüfung nennen.
