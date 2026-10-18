#!/usr/bin/env python3
"""Prüft die gespiegelten Daten: valides JSON, keine verwaisten Verweise, Pflichtfelder, BACKLOG.md passend zu backlog.json,
keine Dokumentnummern-Felder. Aufruf: python3 qa/check_daten.py [Projektordner]"""
import json, os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data')
fehler, hinweise = [], []
def lade(n, default):
    p = os.path.join(D, n)
    if not os.path.exists(p): fehler.append('fehlt: data/' + n); return default
    try: return json.load(open(p, encoding='utf-8'))
    except Exception as e: fehler.append('ungültiges JSON %s: %s' % (n, e)); return default
trips, leute, backlog, preise = (lade(n, []) for n in ('trips.json', 'travelers.json', 'backlog.json', 'price_history.json'))
tid = {t['id'] for t in trips}; pid = {p['id'] for p in leute}
BL_TYPEN = {'Link', 'Idee', 'Artikel', 'Video', 'Unterkunft', 'Restaurant', 'Aktivität', 'Aufgabe', 'Notiz'}; BL_STATUS = {'neu', 'geprüft', 'übernommen', 'verworfen'}
STATUS = {'Idee', 'Recherche', 'Beobachten', 'Buchungsreif', 'Gebucht'}
for t in trips:
    if t.get('status') not in STATUS: fehler.append('Reise %s: Status %r' % (t['id'], t.get('status')))
    if not t.get('titel'): fehler.append('Reise %s ohne Titel' % t['id'])
    for m in t.get('mitreisende', []):
        if m not in pid: fehler.append('Reise %s: Mitreisende %s existiert nicht' % (t['id'], m))
    z = t.get('zeitraum') or {}
    if z.get('fruehester_start') and z.get('spaetester_rueckflug') and z['fruehester_start'] > z['spaetester_rueckflug']: fehler.append('Reise %s: Zeitraum verkehrt' % t['id'])
for p in leute:
    if p.get('beziehung') == 'Kind' and p.get('alter') is None and not p.get('geburt_monat'): fehler.append('Kind %s ohne Alter' % p['id'])
    for k in p:
        if re.search(r'nummer|passnr|iban|karte|passwort|password', k, re.I): fehler.append('Person %s: verbotenes Feld %s' % (p['id'], k))
for r in preise:
    if r.get('trip') not in tid: fehler.append('Preis %s: Reise %s existiert nicht' % (r['id'], r.get('trip')))
    if not r.get('datum') or not (r.get('quelle') or r.get('link')): fehler.append('Preis %s ohne Datum oder Quelle' % r['id'])
    if r.get('preis_pp') is not None and not isinstance(r['preis_pp'], (int, float)): fehler.append('Preis %s: preis_pp keine Zahl' % r['id'])
for b in backlog:
    if b.get('typ') not in BL_TYPEN: fehler.append('Backlog %s: Typ %r' % (b['id'], b.get('typ')))
    if b.get('status') not in BL_STATUS: fehler.append('Backlog %s: Status %r' % (b['id'], b.get('status')))
    for x in b.get('trips', []):
        if x not in tid: fehler.append('Backlog %s: Reise %s existiert nicht' % (b['id'], x))
    if b.get('url') and not re.match(r'^https?://', b['url']): fehler.append('Backlog %s: URL ohne http(s)' % b['id'])
pd = os.path.join(D, 'plans')
if os.path.isdir(pd):
    for fn in os.listdir(pd):
        pl = json.load(open(os.path.join(pd, fn), encoding='utf-8'))
        if fn[:-5] not in tid: fehler.append('Plan %s ohne Reise' % fn)
        for i, d in enumerate(pl.get('tage', [])):
            for e in d.get('eintraege', []):
                for x in e.get('teilnehmer', []):
                    if x not in pid: fehler.append('Plan %s Tag %d: Teilnehmer %s existiert nicht' % (fn, i + 1, x))
md = open(os.path.join(ROOT, 'BACKLOG.md'), encoding='utf-8').read() if os.path.exists(os.path.join(ROOT, 'BACKLOG.md')) else ''
for b in backlog:
    erwartet = max(1, len(b.get('trips', [])))
    if md.count('**%s**' % b['titel']) != erwartet: fehler.append('BACKLOG.md: „%s“ %d× statt %d×' % (b['titel'], md.count('**%s**' % b['titel']), erwartet))
print('Geprüft: %d Reisen, %d Personen, %d Preise, %d Backlog-Einträge' % (len(trips), len(leute), len(preise), len(backlog)))
print('FEHLER (%d):' % len(fehler) if fehler else 'Keine Fehler.', *fehler, sep='\n  ' if fehler else '')
sys.exit(1 if fehler else 0)
