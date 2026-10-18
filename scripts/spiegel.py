#!/usr/bin/env python3
"""Spiegelt die Artifact-Datenbank in lesbare Dateien: data/*.json und BACKLOG.md.

Ablauf: Claude liest die Sammlungen mit ArtifactData (out_dir=<Ordner>) und ruft dann
    python3 scripts/spiegel.py <Ordner>
auf. Quelle der Wahrheit bleibt die Datenbank der App, die Dateien sind der lesbare Spiegel.
"""
import json, os, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lade(ordner, sammlung):
    pfad = os.path.join(ordner, sammlung)
    out = []
    if os.path.isdir(pfad):
        for fn in sorted(os.listdir(pfad)):
            if fn.endswith('.json'):
                d = json.load(open(os.path.join(pfad, fn), encoding='utf-8'))
                d['id'] = fn[:-5]
                out.append(d)
    return out


def schreibe(name, obj):
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def backlog_md(items, trips):
    namen = {t['id']: t['titel'] for t in trips}
    L = ['# Backlog', '', 'Automatisch aus der App gespiegelt (`scripts/spiegel.py`), Stand %s. Bitte nicht von Hand bearbeiten, Änderungen in der App machen.' % date.today().isoformat(), '']
    gruppen = {}
    for b in items:
        for tid in (b.get('trips') or [None]):
            gruppen.setdefault(namen.get(tid, 'Ohne Reise'), []).append(b)
    for gname in sorted(gruppen, key=lambda x: (x == 'Ohne Reise', x)):
        L += ['## ' + gname, '']
        for st in ['neu', 'geprüft', 'übernommen', 'verworfen']:
            es = [b for b in gruppen[gname] if b.get('status') == st]
            if not es:
                continue
            L += ['### ' + st, '']
            for b in sorted(es, key=lambda x: x.get('datum') or ''):
                kopf = '- **%s** (%s, Priorität %s, %s)' % (b.get('titel'), b.get('typ'), b.get('prio', 'mittel'), b.get('datum', ''))
                if b.get('url'):
                    kopf += ' <%s>' % b['url']
                L.append(kopf)
                if b.get('zusammenfassung'):
                    L.append('  - ' + b['zusammenfassung'])
                if b.get('impuls'):
                    L.append('  - Warum: %s Preisrahmen: %s Zeitraum: %s Nachteil: %s' % (b.get('warum', ''), b.get('preisrahmen', ''), b.get('zeitraum', ''), b.get('risiko', '')))
                    if b.get('bewertung'):
                        L.append('  - Bewertung: ' + ('Daumen hoch' if b['bewertung'] == 'up' else 'Daumen runter'))
                if b.get('notiz'):
                    L.append('  - Notiz: ' + b['notiz'])
                if b.get('tags'):
                    L.append('  - Tags: ' + ', '.join(b['tags']))
            L.append('')
    if not items:
        L.append('Der Backlog ist leer.')
    return '\n'.join(L).rstrip() + '\n'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ordner = sys.argv[1]
    trips, leute, backlog, preise = (lade(ordner, s) for s in ('trips', 'travelers', 'backlog', 'prices'))
    schreibe('trips.json', trips)
    schreibe('travelers.json', leute)
    schreibe('backlog.json', backlog)
    schreibe('price_history.json', preise)
    for t in trips:
        plan = os.path.join(ordner, 'plans', t['id'] + '.json')
        if os.path.exists(plan):
            os.makedirs(os.path.join(ROOT, 'data', 'plans'), exist_ok=True)
            with open(plan, encoding='utf-8') as f, open(os.path.join(ROOT, 'data', 'plans', t['id'] + '.json'), 'w', encoding='utf-8') as g:
                g.write(f.read())
    with open(os.path.join(ROOT, 'BACKLOG.md'), 'w', encoding='utf-8') as f:
        f.write(backlog_md(backlog, trips))
    print('Gespiegelt: %d Reisen, %d Personen, %d Backlog-Einträge, %d Preise' % (len(trips), len(leute), len(backlog), len(preise)))


if __name__ == '__main__':
    main()
