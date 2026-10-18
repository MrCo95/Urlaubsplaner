#!/usr/bin/env python3
"""Browser-Tests der Urlaubs-Team-App mit Test-Attrappe für die Artifact-Datenbank.

Start:  python3 qa/harness/make_page.py && python3 qa/harness/test_app.py
Ausgabe: qa/ergebnisse.json (Anforderungs-IDs mit bestanden/durchgefallen) und Screenshots in qa/screens/.
"""
import glob, json, os, re, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.dirname(HERE)
PAGE = 'file://' + os.path.join(HERE, 'page.html')
SHOTS = os.path.join(QA, 'screens')
RES = []
ERRS = []


def ok(ids, cond, msg):
    ids = ids if isinstance(ids, list) else [ids]
    RES.append({'ids': ids, 'ok': bool(cond), 'msg': msg})
    print(('PASS ' if cond else 'FAIL ') + ','.join(ids) + ' ' + msg)


def new_page(b, w=1440, h=900, scheme='light', init=None, seed=None):
    ctx = b.new_context(viewport={'width': w, 'height': h}, color_scheme=scheme)
    ctx.route(re.compile(r'^https?://'), lambda r: r.abort())  # kein Netz: Schrift fällt auf Systemschrift zurück
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: ERRS.append(str(e)))
    pg.on('console', lambda m: ERRS.append(m.text) if m.type == 'error' and 'ERR_FAILED' not in m.text and 'Failed to load resource' not in m.text else None)
    if init:
        pg.add_init_script(init)
    pg.goto(PAGE)
    pg.wait_for_function('window.__db !== undefined')
    if seed:
        pg.evaluate('(s) => window.__db._seed(s)', seed)
    pg.wait_for_timeout(250)
    return ctx, pg


def toast(pg):
    return pg.evaluate("() => { const t = document.querySelector('#toast'); return t && !t.hidden ? t.textContent : '' }")


def dump(pg):
    return pg.evaluate('() => window.__db._dump()')


def docs(pg, col):
    d = dump(pg)
    return {k.split('/')[-1]: v for k, v in d.items() if k.rsplit('/', 1)[0] == col}


TRAV = {
    'travelers/p_martin': {'name': 'Martin', 'beziehung': 'Familie', 'alter': 40},
    'travelers/p_kristina': {'name': 'Kristina', 'beziehung': 'Familie', 'alter': 40},
    'travelers/p_matteo': {'name': 'Matteo', 'beziehung': 'Kind', 'alter': 5, 'geburt_monat': '2021-06'},
    'travelers/p_anna': {'name': 'Anna Freund', 'beziehung': 'Freunde', 'alter': 38},
    'travelers/p_lea': {'name': 'Lea Freund', 'beziehung': 'Kind', 'alter': 4},
    'travelers/p_kind0': {'name': 'Kind ohne Alter', 'beziehung': 'Kind', 'alter': None},
}


def trip_doc(titel, status='Idee', **kw):
    t = {'titel': titel, 'status': status, 'archiviert': False, 'ziel': {'modus': 'offen', 'text': ''}, 'reiseart': ['Strand'],
         'zeitraum': {'fruehester_start': '2027-07-19', 'spaetester_rueckflug': '2027-08-31', 'dauer_min': 7, 'dauer_max': 14, 'flex_tage': 3},
         'budget': {'gesamt': None, 'pro_person_max': None}, 'unterkunft': {'typ': [], 'min_sterne': 0, 'min_bewertung': 0, 'verpflegung': 'egal'},
         'anreise': {'modi': ['Flug'], 'abflughaefen': ['Köln/Bonn (CGN)'], 'direktflug': False, 'max_reisezeit_h': None},
         'muss': [], 'nogos': [], 'mitreisende': ['p_martin', 'p_kristina', 'p_matteo'], 'gruppe': {'aktiv': False, 'haushalte': [], 'wuensche': ''},
         'beobachten': {'checks_pro_woche': 2, 'schwelle_prozent': 10}, 'notizen': '', 'erstellt': '2026-10-01T10:00:00Z', 'geaendert': '2026-10-01T10:00:00Z'}
    t.update(kw)
    return t


def fill_trip(pg, **v):
    pg.wait_for_selector('#mf')
    for k, val in v.items():
        if k in ('mit', 'art'):
            for cb in pg.query_selector_all(f'input[name={k}]'):
                cb.set_checked(cb.get_attribute('value') in val)
        elif k in ('gaktiv',):
            pg.set_checked('input[name=gaktiv]', val)
        elif k in ('status', 'zmodus', 'direkt'):
            pg.select_option(f'select[name={k}]', val)
        else:
            sel = f'[name={k}]'
            pg.fill(sel, str(val))


def submit(pg):
    pg.click('#mf button[type=submit]')
    pg.wait_for_timeout(250)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome')[0], args=['--no-sandbox'])

        # ---------- Leere Startseite, Fehlerzustände, Nur-Lesen ----------
        ctx, pg = new_page(b)
        txt = pg.inner_text('#main')
        ok(['A-016', 'A-130'], 'Noch keine Reise' in txt, 'Leere Startseite zeigt verständlichen Leerzustand')
        ok('A-031', pg.query_selector('.new-card') is not None and 'Neue Reise' in txt, 'Kachel „+ Neue Reise“ ist die erste Kachel')
        first = pg.evaluate("() => document.querySelector('#grid .grid').firstElementChild.className")
        ok('A-031', 'new-card' in first, 'Erste Kachel im Raster ist „Neue Reise“ (Klasse %s)' % first)
        pg.screenshot(path=os.path.join(SHOTS, '01-leer-desktop.png'))
        ctx.close()
        ctx, pg = new_page(b, init='window.__QA_NODB__=true')
        pg.wait_for_timeout(300)
        ok('A-130', 'Anmeldung nötig' in pg.inner_text('#main'), 'Fehlerzustand ohne Datenbank: „Anmeldung nötig“ auf Deutsch')
        ctx.close()
        ctx, pg = new_page(b, init='window.__QA_RO__=true', seed={**TRAV, 'trips/t1': trip_doc('[TEST] Nur Lesen')})
        pg.wait_for_timeout(300)
        ok('A-134', pg.query_selector('.new-card') is None and pg.query_selector('[data-act=edit]') is None, 'Nur-Lesen: keine Schreib-Bedienelemente')
        ctx.close()

        # ---------- Eingabemaske und Validierung ----------
        ctx, pg = new_page(b, seed=TRAV)
        pg.click('[data-act=neu]'); pg.wait_for_selector('#mf')
        form_txt = pg.inner_text('#mf')
        for lab, ids in [('Titel der Reise', 'A-039'), ('Frühester Start', 'A-040'), ('Spätester Rückflug', 'A-040'), ('Dauer von', 'A-040'), ('Flexibilität', 'A-040'), ('Budget gesamt', 'A-043'), ('Maximal pro Person', 'A-043'), ('Mindest-Sterne', 'A-044'), ('Verpflegung', 'A-044'), ('Direktflug', 'A-045'), ('Max. Reisezeit', 'A-045'), ('Muss-Kriterien', 'A-046'), ('No-Gos', 'A-046'), ('Alarm ab Preisfall', 'A-047'), ('Checks pro Woche', 'A-048'), ('Notizen', 'A-049'), ('Status', 'A-049')]:
            ok(ids, lab in form_txt, 'Eingabemaske hat Feld „%s“' % lab)
        arten = [c.get_attribute('value') for c in pg.query_selector_all('input[name=art]')]
        ok('A-042', arten == ['Strand', 'Städtetrip', 'Natur/Aktiv', 'Rundreise', 'Skifahren', 'Wellness', 'Sonstiges'], 'Alle 7 Reisearten: %s' % arten)
        ok('A-041', pg.eval_on_selector('select[name=zmodus]', 'e => [...e.options].map(o=>o.value).join()') == 'konkret,Region,offen', 'Ziele konkret/Region/offen')
        ok('A-044', [c.get_attribute('value') for c in pg.query_selector_all('input[name=utyp]')] == ['Hotel', 'Ferienwohnung/-haus', 'Resort'], 'Unterkunftstypen')
        ok('A-045', [c.get_attribute('value') for c in pg.query_selector_all('input[name=amodi]')] == ['Flug', 'Bahn', 'Auto'], 'Verkehrsmittel Flug/Bahn/Auto')
        ok('A-015', pg.eval_on_selector_all('input[name=aflug]:checked', 'e => e.map(x=>x.value)') == ['Köln/Bonn (CGN)', 'Düsseldorf (DUS)'], 'Standard-Abflughäfen CGN und DUS')
        ok(['A-047', 'A-048'], pg.input_value('input[name=schw]') == '10' and pg.input_value('input[name=cpw]') == '2', 'Standard Schwelle 10 %, 2 Checks pro Woche')
        ok('A-058', 'Dokumentnummer' not in form_txt, 'Maske fragt keine Dokumentnummern ab')
        pg.screenshot(path=os.path.join(SHOTS, '02-eingabemaske.png'))
        # Pflichtfeld Titel
        pg.click('#mf button[type=submit]'); pg.wait_for_timeout(200)
        ok(['A-039', 'A-134'], pg.query_selector('#mf') is not None and not dump(pg).get('trips'), 'Leerer Titel wird nicht gespeichert')
        # Rückreise vor Hinreise
        fill_trip(pg, titel='[TEST] Sommer 2027', start='2027-08-10', ende='2027-08-01'); submit(pg)
        ok('A-050', 'Rückflug' in toast(pg) and not docs(pg, 'trips'), 'Rückreise vor Hinreise abgelehnt: „%s“' % toast(pg))
        # Dauer von > bis
        fill_trip(pg, start='2027-07-19', ende='2027-08-31', dmin='20', dmax='10'); submit(pg)
        ok('A-051', 'Dauer' in toast(pg) and not docs(pg, 'trips'), 'Dauer von > bis abgelehnt: „%s“' % toast(pg))
        # Kind ohne Alter
        fill_trip(pg, dmin='7', dmax='14', mit=['p_kind0']); submit(pg)
        ok('A-052', 'Alter' in toast(pg) and not docs(pg, 'trips'), 'Kind ohne Alter abgelehnt: „%s“' % toast(pg))
        # Vergangenheit
        fill_trip(pg, start='2020-01-01', ende='2020-01-10', mit=['p_martin']); submit(pg)
        t = docs(pg, 'trips')
        ok('A-054', ('Vergangenheit' in toast(pg)) or not t, 'Datum in der Vergangenheit gemeldet oder abgelehnt (Toast: „%s“, gespeichert: %d)' % (toast(pg), len(t)))
        if pg.query_selector('#mf') and t:
            pass
        # Dialog ggf. schließen
        if pg.query_selector('#dlg[open]'):
            pg.keyboard.press('Escape')
        for k in list(docs(pg, 'trips')):
            pg.evaluate(f"window.__db.doc('trips/{k}').delete()")
        pg.wait_for_timeout(200)
        # Lange Titel und Sonderzeichen
        lang = '[TEST] <img src=x onerror="window.__xss=1"> "Anführung" \' & ' + 'Wort' * 60
        pg.click('[data-act=neu]'); pg.wait_for_selector('#mf')
        fill_trip(pg, titel=lang, start='2027-07-19', ende='2027-08-31', dmin='7', dmax='14', mit=['p_martin', 'p_kristina', 'p_matteo', 'p_anna', 'p_lea'], art=['Strand'], gaktiv=True,
                  haus='Familie Reichel | 2 Erw. + 1 Kind | 5000\nFamilie Freund | 1 Erw. + 1 Kind | 3000', gwunsch='Pool und Kinderclub', ziel='Mallorca', zmodus='Region')
        submit(pg)
        trips = docs(pg, 'trips')
        ok('A-055', len(trips) == 1, 'Gültige Reise wird gespeichert')
        tid = next(iter(trips)) if trips else None
        ok('A-056', pg.evaluate('window.__xss') is None, 'Sonderzeichen werden nicht als HTML ausgeführt')
        pg.wait_for_timeout(300)
        if pg.query_selector('#dlg[open]'):
            pg.keyboard.press('Escape')
        det = pg.inner_text('#main')
        ok('A-053', 'Offen: Budget richtet sich nach dem Angebot' in det, 'Reise ohne Budget zeigt „Offen: Budget richtet sich nach dem Angebot“')
        ok(['A-064', 'A-065', 'A-066', 'A-067'], 'familie reichel' in det.lower() and '5.000' in det and 'familie freund' in det.lower() and 'pool und kinderclub' in det.lower() and 'anteil nach budget' in det.lower(), 'Gruppenreise: Haushalte, Budgets, Wünsche, Kostenaufteilung sichtbar')
        ok('A-036', [t.strip() for t in pg.eval_on_selector_all('#dtabs button', 'e=>e.map(x=>x.innerText)')][:5] == ['Übersicht', 'Angebote', 'Reiseplan', 'Backlog', 'Verlauf'], 'Detail-Tabs: %s' % pg.eval_on_selector_all('#dtabs button', 'e=>e.map(x=>x.innerText.trim())'))
        ok('A-056', pg.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"), 'Langer Titel erzeugt kein horizontales Scrollen (Detail)')
        pg.screenshot(path=os.path.join(SHOTS, '03-detail.png'))

        # Bearbeiten + Verlauf + Rückgängig
        pg.click('[data-act=edit]'); pg.wait_for_selector('#mf')
        pg.fill('input[name=bgesamt]', '4000'); pg.fill('textarea[name=notizen]', 'geändert'); submit(pg)
        ok('A-055', docs(pg, 'trips')[tid]['budget']['gesamt'] == 4000, 'Bearbeiten speichert Budget')
        pg.click('[data-act=tab][data-v=verlauf]'); pg.wait_for_timeout(300)
        vers = [v for k, v in dump(pg).items() if k.startswith(f'trips/{tid}/versions/')]
        ok(['A-074', 'A-125'], len(vers) >= 2 and all(v.get('wer') and v.get('was') and v.get('datum') for v in vers), 'Versionen mit Wer/Was/Wann: %d' % len(vers))
        pg.click('[data-act=undo] >> nth=0'); pg.wait_for_timeout(300)
        ok(['A-075', 'A-125'], docs(pg, 'trips')[tid]['budget']['gesamt'] is None, 'Rückgängig stellt Budget „offen“ wieder her')
        pg.screenshot(path=os.path.join(SHOTS, '04-verlauf.png'))
        # Optimieren aus Detail
        pg.click('[data-act=tab][data-v=uebersicht]'); pg.wait_for_timeout(200)
        before = json.dumps(docs(pg, 'trips')[tid], sort_keys=True)
        pg.click('#dhead [data-act=optimieren]'); pg.wait_for_selector('#mf')
        pg.fill('textarea[name=w]', 'günstiger und weniger Fahrtzeit'); submit(pg)
        au = docs(pg, 'auftraege')
        ok(['A-068', 'A-069'], any(a['art'] == 'optimieren' and a['trip'] == tid and a['status'] == 'offen' for a in au.values()), 'Optimieren legt Auftrag für genau diese Reise ab')
        ok('A-073', json.dumps(docs(pg, 'trips')[tid], sort_keys=True) == before, 'Optimieren ändert die Reise nicht ohne Okay')
        pg.fill('#frei-t', 'mehr Ruhe für Matteo'); pg.click('#frei button[type=submit]'); pg.wait_for_timeout(300)
        ok('A-076', any(a['art'] == 'freitext' and 'Matteo' in a['text'] for a in docs(pg, 'auftraege').values()), 'Freitext-Wunsch wird als Auftrag abgelegt')
        # Vorschläge (so legt sie das Team ab)
        pg.evaluate(f"""() => {{ const d=window.__db; d.doc('vorschlaege/v1').set({{trip:'{tid}',titel:'Abflug Düsseldorf',effekt:'−240 € p. P.',begruendung:'Gleicher Flug ab DUS',quelle:'Test',stand:'2026-10-18',status:'offen',aenderung:{{budget:{{gesamt:3800,pro_person_max:null}}}}}});
          d.doc('vorschlaege/v2').set({{trip:'{tid}',titel:'Bessere Bewertung',effekt:'+60 €',status:'offen'}}); d.doc('vorschlaege/v3').set({{trip:'{tid}',titel:'Später ansehen',effekt:'±0',status:'offen'}}); }}""")
        pg.wait_for_timeout(400)
        n_vs = pg.eval_on_selector_all('#u-opt [data-act=vs][data-v=angenommen]', 'e=>e.length')
        ok(['A-071', 'A-072'], n_vs == 3 and pg.eval_on_selector_all('#u-opt [data-act=vs][data-v=abgelehnt]', 'e=>e.length') == 3 and pg.eval_on_selector_all('#u-opt [data-act=vs][data-v=spaeter]', 'e=>e.length') == 3 and '−240' in pg.inner_text('#u-opt'), '3 Vorschläge mit Effekt und Annehmen/Ablehnen/Später')
        pg.click('[data-act=vs][data-id=v1][data-v=angenommen]'); pg.wait_for_timeout(400)
        ok(['A-072', 'A-073', 'A-074'], docs(pg, 'trips')[tid]['budget']['gesamt'] == 3800 and docs(pg, 'vorschlaege')['v1']['status'] == 'angenommen', 'Annehmen setzt Änderung um (Budget 3800) und merkt Status')
        pg.click('[data-act=vs][data-id=v2][data-v=abgelehnt]'); pg.wait_for_timeout(300)
        pg.click('[data-act=vs][data-id=v3][data-v=spaeter]'); pg.wait_for_timeout(300)
        ok('A-072', docs(pg, 'vorschlaege')['v2']['status'] == 'abgelehnt' and docs(pg, 'vorschlaege')['v3']['status'] == 'spaeter', 'Ablehnen und Später speichern Status')
        pg.click('[data-act=tab][data-v=verlauf]'); pg.wait_for_timeout(300)
        pg.click('[data-act=undo] >> nth=0'); pg.wait_for_timeout(300)
        ok('A-075', docs(pg, 'trips')[tid]['budget']['gesamt'] is None, 'Angenommenen Vorschlag per Rückgängig zurücknehmen')

        # ---------- Reiseplan ----------
        pg.click('[data-act=tab][data-v=plan]'); pg.wait_for_timeout(300)
        ok('A-077', 'Noch kein Reiseplan' in pg.inner_text('#p-body'), 'Plan: Leerzustand mit nächster Aktion')
        ok('A-083', pg.query_selector('[data-act=planwunsch]') is not None, 'Plan: „Entwurf vom Team“ legt Auftrag an')
        pg.click('[data-act=planwunsch] >> nth=0'); pg.wait_for_timeout(250)
        ok('A-083', any(a['art'] == 'plan' for a in docs(pg, 'auftraege').values()), 'Plan-Entwurf-Auftrag abgelegt')
        for _ in range(3):
            pg.click('[data-act=addtag] >> nth=0'); pg.wait_for_timeout(250)
        ok('A-077', pg.eval_on_selector_all('.day', 'e=>e.length') == 3, 'Drei Tage angelegt')
        # Einträge
        def add_ent(day, titel, zeit='', kat='Aktivität', kosten='', dauer='', status='offen', ort='', link=''):
            pg.click(f'[data-act=addent][data-day="{day}"]'); pg.wait_for_selector('#mf')
            pg.fill('input[name=titel]', titel); pg.fill('input[name=zeit]', zeit) if zeit else None
            pg.select_option('select[name=kat]', kat); pg.select_option('select[name=st]', status)
            if kosten: pg.fill('input[name=kosten]', str(kosten))
            if dauer: pg.fill('input[name=dauer]', str(dauer))
            if ort: pg.fill('input[name=ort]', ort)
            if link: pg.fill('input[name=link]', link)
            submit(pg); pg.wait_for_timeout(250)
        add_ent(0, 'Anreise Flug CGN', '08:00', 'Anreise', 600, 240, 'gebucht')
        add_ent(0, 'Hotel Check-in', '14:00', 'Check-in')
        add_ent(1, 'Strandtag', '10:00', 'Aktivität', 0, 180, 'offen', 'Cala Millor Strand')
        add_ent(1, 'Aquapark', '15:00', 'Aktivität', 120, 180, 'reserviert', '', 'https://example.org/aquapark')
        add_ent(1, 'Ausflug Höhlen', '17:30', 'Aktivität', 90)
        add_ent(2, 'Mittagsruhe', '13:00', 'Pause')
        pl = docs(pg, 'plans')[tid]
        ents = [e for d in pl['tage'] for e in d['eintraege']]
        ok(['A-078', 'A-079', 'A-080', 'A-081'], len(ents) == 6 and {'Anreise', 'Check-in', 'Aktivität', 'Pause'} <= {e['kategorie'] for e in ents} and {'gebucht', 'reserviert', 'offen'} <= {e['status'] for e in ents} and all(e.get('teilnehmer') for e in ents), 'Einträge mit Typ, Status, Teilnehmer gespeichert')
        ok('A-079', any(e.get('ort') for e in ents) and any(e.get('link') for e in ents) and 'maps' in pg.inner_html('#p-body'), 'Ort wird zum Kartenlink, Link vorhanden')
        ok('A-082', 'Viel für einen Tag' in pg.inner_text('#p-body'), 'Hinweis bei mehr als 2 festen Programmpunkten (Tag 2 hat 3)')
        ok(['A-090', 'A-091'], 'offen' not in pg.inner_text('.ampel') and pg.query_selector('.ampel .dot') is not None and '810' in pg.inner_text('.ampel').replace('.', '').replace(' ', ''), 'Kostensumme 810 € sichtbar: „%s“' % pg.inner_text('.ampel').replace('\n', ' ')[:80])
        # Ampel mit Budget
        pg.evaluate(f"window.__db.doc('trips/{tid}').update({{budget:{{gesamt:1000}}}})"); pg.wait_for_timeout(300)
        amp_knapp = pg.eval_on_selector('.ampel .dot', 'e => e.className')
        pg.evaluate(f"window.__db.doc('trips/{tid}').update({{budget:{{gesamt:700}}}})"); pg.wait_for_timeout(300)
        amp_drueber = pg.eval_on_selector('.ampel .dot', 'e => e.className')
        pg.evaluate(f"window.__db.doc('trips/{tid}').update({{budget:{{gesamt:5000}}}})"); pg.wait_for_timeout(300)
        amp_ok = pg.eval_on_selector('.ampel .dot', 'e => e.className')
        ok('A-091', 'warn' in amp_knapp and 'bad' in amp_drueber and 'ok' in amp_ok, 'Ampel: knapp=%s, drüber=%s, im Rahmen=%s' % (amp_knapp, amp_drueber, amp_ok))
        # Drag & Drop Tag 2 -> Tag 3
        pg.drag_and_drop('.ent[data-d="1"][data-e="2"]', '.day[data-day="2"] .day-h'); pg.wait_for_timeout(400)
        pl = docs(pg, 'plans')[tid]
        ok('A-084', len(pl['tage'][1]['eintraege']) == 2 and any(e['titel'] == 'Ausflug Höhlen' for e in pl['tage'][2]['eintraege']), 'Drag & Drop verschiebt Eintrag in anderen Tag')
        ok('A-082', 'Viel für einen Tag' not in pg.inner_text('.day[data-day="1"]'), 'Hinweis verschwindet nach dem Verschieben')
        # Freitext
        pg.click('[data-act=ruhiger][data-day="2"]'); pg.wait_for_timeout(250)
        ok('A-085', any(a['art'] == 'plan-freitext' and 'Tag 3' in a['text'] for a in docs(pg, 'auftraege').values()), '„Tag 3 ruhiger“ als Auftrag abgelegt')
        # Packliste / Dokumente
        pg.click('[data-act=packvor]'); pg.click('[data-act=dokvor]'); pg.wait_for_timeout(400)
        pl = docs(pg, 'plans')[tid]; pk = [x['text'] for x in pl['packliste']]
        ok('A-088', 'Sonnencreme (Kinder-LSF)' in pk and 'Lieblingskuscheltier' in pk, 'Packliste nach Reiseart (Strand) und Kind: %d Einträge' % len(pk))
        ok('A-089', any('Einreisehinweise' in x['text'] and 'Auswärtigen Amt' in x['text'] for x in pl['dokumente']), 'Dokument-Checkliste nennt Quelle Auswärtiges Amt')
        pg.fill('[data-form=chkadd][data-k=packliste] input', 'Regenjacke Test'); pg.press('[data-form=chkadd][data-k=packliste] input', 'Enter'); pg.wait_for_timeout(300)
        ok('A-088', 'Regenjacke Test' in [x['text'] for x in docs(pg, 'plans')[tid]['packliste']], 'Packlisten-Punkt hinzufügen')
        pg.screenshot(path=os.path.join(SHOTS, '05-reiseplan.png'), full_page=True)
        # Exporte
        pg.click('[data-act=ics]'); pg.wait_for_timeout(300)
        pg.click('[data-act=kurz]'); pg.wait_for_timeout(300)
        saved = pg.evaluate('window.__downloads.saved')
        ics = next((s for s in saved if s['filename'].endswith('.ics')), None)
        kurz = next((s for s in saved if s['filename'].endswith('.md')), None)
        ok('A-093', ics and ics['data'].count('BEGIN:VEVENT') == 6 and ics['data'].startswith('BEGIN:VCALENDAR') and 'DTSTART:20270719T080000' in ics['data'], '.ics: %s Termine, gültiger Aufbau' % (ics['data'].count('BEGIN:VEVENT') if ics else 0))
        ok('A-094', kurz and 'Tag 1' in kurz['data'] and 'Anreise Flug CGN' in kurz['data'], 'Kurzversion enthält Tage und Einträge')
        ok('A-092', pg.query_selector('[data-act=pdf]') is not None, 'PDF-Export-Schaltfläche vorhanden')
        if pg.query_selector('[data-act=pdf]'):
            pg.click('[data-act=pdf]'); pg.wait_for_timeout(400)
            pdf = next((s for s in pg.evaluate('window.__downloads.saved') if s['filename'].endswith('.pdf')), None)
            good = False; info = ''
            if pdf is not None:
                import io
                from pypdf import PdfReader
                rd = PdfReader(io.BytesIO(bytes(pdf['data'])))
                txt = '\n'.join(pg_.extract_text() for pg_ in rd.pages)
                good = len(rd.pages) >= 1 and 'Anreise Flug CGN' in txt and 'Tag 1' in txt and 'Ausflug' in txt
                info = '%d Seite(n), %d Zeichen' % (len(rd.pages), len(txt))
            ok('A-092', good, 'PDF wird erzeugt und mit pypdf gelesen: ' + info)

        pg.click('[data-act=tab][data-v=verlauf]'); pg.wait_for_timeout(300)
        pv = [v for k, v in dump(pg).items() if k.startswith(f'plans/{tid}/versions/')]
        ok('A-125', len(pv) >= 8 and all(v.get('wer') and v.get('was') for v in pv) and 'Reiseplan' in pg.inner_text('#v-body'), 'Reiseplan-Änderungen werden versioniert (%d Versionen) und im Verlauf angezeigt' % len(pv))
        n_before = sum(len(d['eintraege']) for d in docs(pg, 'plans')[tid]['tage'])
        pg.click('[data-act=undoplan] >> nth=0'); pg.wait_for_timeout(400)
        n_after = len(docs(pg, 'plans')[tid]['packliste'])
        ok('A-125', 'Regenjacke Test' not in [x['text'] for x in docs(pg, 'plans')[tid]['packliste']] and n_after == len(pl['packliste']), 'Rückgängig für Reiseplan entfernt den letzten Listenpunkt (Packliste %d, vorher 13)' % n_after)
        pg.evaluate(f"""window.__db.doc('plans/{tid}').update({{hinweise:[{{text:'Wetter Palma Juli 29,7 °C',quelle:'mallorca.com'}},{{text:'Öffnungszeiten nicht geprüft',quelle:'offen'}}]}})"""); pg.click('[data-act=tab][data-v=plan]'); pg.wait_for_timeout(400)
        hp = pg.inner_text('#p-body')
        ok(['A-086', 'A-087'], 'Wetter Palma Juli' in hp and 'Quelle: mallorca.com' in hp and 'Öffnungszeiten nicht geprüft' in hp, 'Wetter- und Öffnungszeiten-Hinweise werden mit Quelle im Plan angezeigt')
        # Backlog-Eintrag in den Plan übernehmen
        pg.evaluate("window.__db.doc('backlog/ip1').set({typ:'Restaurant',titel:'Restaurant Hafen',url:'https://example.org/r',notiz:'Kinderstühle',tags:[],trips:['"+tid+"'],prio:'mittel',status:'neu',datum:'2026-10-18'})"); pg.click('[data-act=tab][data-v=backlog]'); pg.wait_for_selector('[data-act=inplan]'); pg.wait_for_timeout(300)
        pg.click('[data-id=ip1][data-act=inplan]'); pg.wait_for_selector('#mf select[name=tag]'); pg.select_option('select[name=tag]', '1'); submit(pg); pg.wait_for_timeout(400)
        ok('A-103', any(e['titel'] == 'Restaurant Hafen' and e['kategorie'] == 'Restaurant' for e in docs(pg, 'plans')[tid]['tage'][1]['eintraege']) and docs(pg, 'backlog')['ip1']['status'] == 'übernommen', 'Backlog-Eintrag wird in Tag 2 des Plans übernommen, Status „übernommen“')
        pg.evaluate("window.__db.doc('backlog/ip1').delete()"); pg.wait_for_timeout(200)
        # ---------- Backlog ----------
        pg.click('[data-act=tab][data-v=backlog]'); pg.wait_for_selector('#qa')
        ok('A-099', 'Backlog' in pg.inner_text('#dtabs') and pg.query_selector('#qa-t') is not None, 'Backlog-Tab mit Quick-Add')
        ok('A-130', 'Der Backlog ist leer' in pg.inner_text('#b-list'), 'Leerer Backlog zeigt Leerzustand')
        links = ['https://www.holidaycheck.de/hi/hotel-a/1', 'https://www.tripadvisor.de/Hotel_Review-g1', 'https://www.booking.com/hotel/es/x.de.html', 'https://example.org/artikel/strand-tipps', 'https://dead.invalid/seite-404']
        for l in links:
            pg.fill('#qa-t', l); pg.press('#qa-t', 'Enter'); pg.wait_for_timeout(250)
        pg.fill('#qa-t', 'Restaurant am Hafen ausprobieren'); pg.press('#qa-t', 'Enter'); pg.wait_for_timeout(250)
        bl = docs(pg, 'backlog')
        ok('A-097', len(bl) == 6 and all(v['status'] == 'neu' for v in bl.values()), '5 Links und 1 Text per Quick-Add: %d Einträge' % len(bl))
        ok('A-099', all(tid in v['trips'] for v in bl.values()), 'Quick-Add im Reise-Tab ordnet der Reise zu')
        n0 = len(bl)
        pg.fill('#qa-t', links[0]); pg.press('#qa-t', 'Enter'); pg.wait_for_timeout(300)
        ok('A-108', len(docs(pg, 'backlog')) == n0, 'Duplikat-Link wird nicht doppelt angelegt (Toast: „%s“)' % toast(pg))
        ok('A-098', all(v.get('zusammenfassung') for v in docs(pg, 'backlog').values()), 'Titel und Kurzbeschreibung automatisch gefüllt')
        # XSS in Backlog
        pg.evaluate("window.__db.doc('backlog/x1').set({typ:'Notiz',titel:'<script>window.__xss2=1</script><b>fett</b>',url:'javascript:alert(1)',notiz:'\"><img src=x onerror=window.__xss3=1>',tags:['<i>t</i>'],trips:[],prio:'mittel',status:'neu',datum:'2026-10-18'})"); pg.wait_for_timeout(300)
        pg.click('[data-act=nav][data-v=backlog]'); pg.wait_for_selector('#b-list'); pg.wait_for_timeout(300)
        ok(['A-126', 'A-134'], pg.evaluate('window.__xss2') is None and pg.evaluate('window.__xss3') is None and pg.query_selector('#b-list a[href^="javascript"]') is None, 'Backlog: Skript, HTML und javascript:-Link in Einträgen bleiben wirkungslos')
        pg.evaluate("window.__db.doc('backlog/l1').set({typ:'Link',titel:'Toter Link',url:'https://dead.invalid/x',tags:[],trips:[],prio:'mittel',status:'neu',datum:'2026-10-18',link_status:'tot',link_geprueft:'2026-10-18'})")
        pg.evaluate("window.__db.doc('backlog/l2').set({typ:'Link',titel:'Nicht abrufbar',url:'https://x.example/y',tags:[],trips:[],prio:'mittel',status:'neu',datum:'2026-10-18',link_status:'nicht abrufbar',link_geprueft:'2026-10-18'})"); pg.wait_for_timeout(300)
        bt = pg.inner_text('#b-list')
        ok('A-104', 'Link tot' in bt and 'Link nicht abrufbar' in bt and 'Link geprüft' not in bt, 'Tote und nicht abrufbare Links werden unterschiedlich markiert')
        pg.evaluate("window.__db.doc('backlog/l1').delete(); window.__db.doc('backlog/l2').delete()"); pg.wait_for_timeout(300)
        ok('A-099', pg.eval_on_selector_all('#b-list .prop', 'e=>e.length') == 7, 'Globale Ansicht zeigt alle Einträge (%d)' % pg.eval_on_selector_all('#b-list .prop', 'e=>e.length'))
        ok('A-095', pg.eval_on_selector('#b-typ', 'e => [...e.options].slice(1).map(o=>o.text).join()') == 'Link,Idee,Artikel,Video,Unterkunft,Restaurant,Aktivität,Aufgabe,Notiz', 'Backlog-Typen vollständig')
        pg.click('[data-act=bedit] >> nth=0'); pg.wait_for_selector('#mf')
        lab = pg.inner_text('#mf').lower()
        ok('A-096', all(x.lower() in lab for x in ['Titel', 'URL', 'Notiz', 'Tags', 'Zuordnung zu Reisen', 'Priorität', 'Status']), 'Backlog-Felder: Titel, URL, Notiz, Tags, Reisen, Priorität, Status')
        pg.fill('input[name=url]', 'ftp://bad'); submit(pg)
        ok('A-134', 'http' in toast(pg) and pg.query_selector('#mf'), 'Ungültige URL wird mit Meldung abgelehnt: „%s“' % toast(pg))
        pg.keyboard.press('Escape')
        # Status ändern, In Plan
        pg.select_option('[data-act=bset] >> nth=0', 'geprüft'); pg.wait_for_timeout(300)
        ok('A-096', any(v['status'] == 'geprüft' for v in docs(pg, 'backlog').values()), 'Status ändern im Backlog')
        pg.evaluate("window.__db.doc('backlog/imp1').set({typ:'Idee',titel:'Impuls A',impuls:true,status:'neu',prio:'mittel',datum:'2026-10-18',tags:['Strand'],trips:[],warum:'w',preisrahmen:'p',zeitraum:'z',risiko:'r',bewertung:null})"); pg.wait_for_timeout(300)
        pg.click('[data-act=rate][data-id=imp1][data-v=up]'); pg.wait_for_timeout(300)
        ok('A-106', docs(pg, 'backlog')['imp1']['bewertung'] == 'up' and 'Strand' in pg.inner_text('#b-pref'), 'Daumen hoch speichert Bewertung und zeigt gelernte Vorlieben')
        ok('A-105', all(x in pg.inner_text('#b-list') for x in ['Warum', 'Preisrahmen', 'Zeit', 'Nachteil']), 'Impuls zeigt Ziel, Grund, Preisrahmen, Zeitraum, Nachteil')
        pg.screenshot(path=os.path.join(SHOTS, '06-backlog.png'), full_page=True)
        # Backlog global suche/filter
        pg.fill('#b-q', 'tripadvisor'); pg.wait_for_timeout(200)
        ok('A-099', pg.eval_on_selector_all('#b-list .prop', 'e=>e.length') == 1, 'Backlog-Suche filtert')
        ctx.close()

        # ---------- Suchleiste und „Jetzt suchen“ ----------
        ctx, pg = new_page(b, seed=TRAV)
        ok('A-136', pg.query_selector('#sb-t') is not None and 'bis 3.000' in pg.get_attribute('#sb-t', 'placeholder'), 'Startseite hat die Suchleiste mit Beispiel im Platzhalter')
        pg.click('#sb-go'); pg.wait_for_timeout(200)
        ok('A-136', 'Schreib kurz' in toast(pg) and not docs(pg, 'trips'), 'Leere Eingabe legt nichts an und erklärt, was zu tun ist')
        pg.fill('#sb-t', 'Mallorca, 2 Erw. + 1 Kind, Juli 2027, bis 3.000 €'); pg.press('#sb-t', 'Enter'); pg.wait_for_selector('#dtabs'); pg.wait_for_timeout(400)
        msg0 = toast(pg); tt = docs(pg, 'trips'); tid2, t2 = next(iter(tt.items())) if tt else (None, {})
        ok(['A-136', 'A-137'], len(tt) == 1 and t2['titel'] == 'Mallorca 2027' and t2['budget']['gesamt'] == 3000 and t2['status'] == 'Recherche' and t2['ziel']['text'] == 'Mallorca' and 'p_matteo' in t2['mitreisende'], 'Suchleiste legt Reise an: Titel „%s“, Budget %s, Status %s' % (t2.get('titel'), t2.get('budget', {}).get('gesamt'), t2.get('status')))
        ok('A-137', any(a['art'] == 'suche' and a['trip'] == tid2 and a['status'] == 'offen' and 'Mallorca' in a['text'] for a in docs(pg, 'auftraege').values()), 'Suchauftrag liegt mit Reise-ID und Wunschtext vor')
        sent = pg.evaluate('window.__sent || []')
        ok('A-137', len(sent) == 1 and 'Jetzt suchen' in sent[0]['text'] and tid2 in sent[0]['text'], 'Claude wird per Kommentar geweckt: „%s“' % (sent[0]['text'][:90] if sent else ''))
        ok('A-137', 'Suche gestartet' in msg0, 'Rückmeldung an Martin: „%s“' % msg0)
        ok('A-137', 'Suche angefragt' in pg.inner_text('#u-opt'), 'Übersicht zeigt „Suche angefragt“ mit Uhrzeit')
        # Jetzt suchen im Detail (nachdem das Team den ersten Auftrag erledigt hat)
        for k_, v_ in docs(pg, 'auftraege').items(): pg.evaluate("([k, v]) => window.__db.doc('auftraege/' + k).update({status: 'erledigt'})", [k_, v_])
        pg.wait_for_timeout(300)
        pg.click('#dhead [data-act=suche]'); pg.wait_for_timeout(400)
        ok('A-137', len(pg.evaluate('window.__sent')) == 2 and sum(1 for a in docs(pg, 'auftraege').values() if a['art'] == 'suche') == 2, '„Jetzt suchen“ im Detail legt Auftrag an und weckt Claude')
        pg.click('#dhead [data-act=suche]'); pg.wait_for_timeout(300)
        ok('A-137', 'läuft schon' in toast(pg) and len(pg.evaluate('window.__sent')) == 2 and sum(1 for a in docs(pg, 'auftraege').values() if a['art'] == 'suche') == 2, 'Erneutes „Jetzt suchen“ bei offenem Auftrag legt keinen Doppelauftrag an (Toast: „%s“)' % toast(pg))
        # Optimieren weckt ebenfalls
        pg.click('#dhead [data-act=optimieren]'); pg.wait_for_selector('#mf'); submit(pg); pg.wait_for_timeout(300)
        ok('A-137', len(pg.evaluate('window.__sent')) == 3, 'Optimieren weckt Claude ebenfalls')
        # Kachelmenü (Team hat zuvor alle Aufträge erledigt)
        for k_ in list(docs(pg, 'auftraege')): pg.evaluate("(k) => window.__db.doc('auftraege/' + k).update({status: 'erledigt'})", k_)
        pg.wait_for_timeout(300)
        pg.click('[data-act=nav][data-v=reisen]'); pg.wait_for_selector('#grid .card'); pg.click('[data-act=menu][data-id="%s"]' % tid2); pg.click('.menu button:has-text("Jetzt suchen")'); pg.wait_for_timeout(400)
        ok('A-137', len(pg.evaluate('window.__sent')) == 4, '„Jetzt suchen“ im Kachelmenü weckt Claude')
        # XSS im Suchtext
        pg.fill('#sb-t', '<img src=x onerror="window.__xss9=1"> Rom'); pg.press('#sb-t', 'Enter'); pg.wait_for_selector('#dtabs'); pg.wait_for_timeout(400)
        ok(['A-126', 'A-137'], pg.evaluate('window.__xss9') is None, 'Suchtext mit HTML wird nicht ausgeführt')
        ctx.close()
        # Ohne offene Sitzung: Rückfall auf Auftrag
        ctx, pg = new_page(b, init='window.__QA_NOSESSION__=true', seed=TRAV)
        pg.fill('#sb-t', 'Rom 2027, Städtetrip'); pg.press('#sb-t', 'Enter'); pg.wait_for_selector('#dtabs'); pg.wait_for_timeout(300)
        ok('A-137', 'Sag im Chat' in toast(pg) and not pg.evaluate('window.__sent') and any(a['art'] == 'suche' for a in docs(pg, 'auftraege').values()) and len(docs(pg, 'trips')) == 1, 'Ohne Sitzung: Reise und Auftrag angelegt, Hinweis „Sag im Chat“, kein Absturz (Toast: „%s“)' % toast(pg))
        ctx.close()
        # Nur lesen: keine Suchleiste
        ctx, pg = new_page(b, init='window.__QA_RO__=true', seed=TRAV)
        ok('A-137', pg.query_selector('#sb') is None, 'Nur-Lesen-Konto sieht keine Suchleiste')
        ctx.close()

        # ---------- Mitreisende ----------
        ctx, pg = new_page(b, seed=TRAV)
        pg.click('[data-act=nav][data-v=leute]'); pg.wait_for_selector('#l-body .box')
        ok(['A-057', 'A-062'], {'Martin', 'Kristina', 'Matteo'} <= set(pg.eval_on_selector_all('#l-body .box b', 'e=>e.map(x=>x.innerText)')), 'Personenliste mit Martin, Kristina, Matteo')
        pg.click('[data-act=newp]'); pg.wait_for_selector('#mf')
        pg.fill('input[name=name]', '[TEST] Kind neu'); pg.select_option('select[name=bez]', 'Kind'); submit(pg)
        ok('A-058', 'Alter' in toast(pg) and '[TEST] Kind neu' not in json.dumps(dump(pg)), 'Kind ohne Alter wird abgelehnt: „%s“' % toast(pg))
        pg.fill('input[name=alter]', '3'); pg.fill('input[name=ern]', 'vegetarisch'); pg.fill('input[name=all]', 'Nüsse'); pg.fill('input[name=int]', 'Tiere'); pg.fill('input[name=veto]', 'kein Skifahren'); pg.fill('input[name=dok]', '2029-05-01'); submit(pg)
        pe = next((v for v in docs(pg, 'travelers').values() if v['name'] == '[TEST] Kind neu'), None)
        ok(['A-058', 'A-059', 'A-060', 'A-061'], pe and pe['alter'] == 3 and pe['ernaehrung'] == 'vegetarisch' and pe['allergien'] == 'Nüsse' and pe['wunsch_veto'] == 'kein Skifahren' and pe['dokument_gueltig_bis'] == '2029-05-01' and not any('nummer' in k for k in pe), 'Person mit Besonderheiten, Veto und Ablaufdatum gespeichert, keine Nummernfelder')
        ctx.close()

        # ---------- Startseite: Kachelinhalt, Filter, Menü, Preise ----------
        seed = dict(TRAV)
        seed['trips/ta'] = trip_doc('[TEST] Sommer 2027', 'Beobachten', ziel={'modus': 'Region', 'text': 'Mallorca'}, geaendert='2026-10-18T10:00:00Z')
        seed['trips/tb'] = trip_doc('[TEST] Städtetrip Rom', 'Idee', mitreisende=['p_martin', 'p_kristina'], reiseart=['Städtetrip'], geaendert='2026-10-17T10:00:00Z', zeitraum={'fruehester_start': '2027-03-01', 'spaetester_rueckflug': '2027-03-10', 'dauer_min': 3, 'dauer_max': 4, 'flex_tage': 1})
        seed['trips/tc'] = trip_doc('[TEST] Skiurlaub', 'Gebucht', mitreisende=['p_martin'], reiseart=['Skifahren'], geaendert='2026-10-16T10:00:00Z', zeitraum={'fruehester_start': '2027-01-05', 'spaetester_rueckflug': '2027-01-12', 'dauer_min': 7, 'dauer_max': 7, 'flex_tage': 0})
        seed['prices/p1'] = {'trip': 'ta', 'datum': '2026-10-10', 'anbieter': 'TUI', 'ziel': 'Mallorca', 'beschreibung': 'x', 'preis_pp': 800, 'preis_gesamt': 2400, 'link': 'https://a.example/1', 'unsicher': False, 'quelle': 'tui.com'}
        seed['prices/p2'] = {'trip': 'ta', 'datum': '2026-10-18', 'anbieter': 'TUI', 'ziel': 'Mallorca', 'beschreibung': 'x', 'preis_pp': 700, 'preis_gesamt': 2100, 'link': 'https://a.example/2', 'unsicher': True, 'quelle': 'tui.com'}
        seed['prices/p3'] = {'trip': 'ta', 'datum': '2026-10-18', 'anbieter': 'Check24', 'ziel': 'Mallorca', 'beschreibung': 'y', 'preis_pp': 900, 'preis_gesamt': None, 'link': 'https://a.example/3', 'unsicher': True, 'quelle': 'check24.de'}
        seed['prices/p4'] = {'trip': 'tb', 'datum': '2026-10-10', 'anbieter': 'X', 'ziel': 'Rom', 'beschreibung': 'z', 'preis_pp': 300, 'preis_gesamt': None, 'link': '', 'unsicher': False, 'quelle': 'x'}
        seed['prices/p5'] = {'trip': 'tb', 'datum': '2026-10-17', 'anbieter': 'X', 'ziel': 'Rom', 'beschreibung': 'z', 'preis_pp': 350, 'preis_gesamt': None, 'link': '', 'unsicher': False, 'quelle': 'x'}
        seed['digests/d1'] = {'trip': 'ta', 'datum': '2026-10-18', 'empfehlung': 'abwarten', 'markdown': '**Empfehlung: abwarten.**\n\n### Top 3\n| Ziel | Preis |\n|---|---|\n| Mallorca | 700 € |\n\n[Quelle](https://a.example/2) <script>window.__xss4=1</script>'}
        ctx, pg = new_page(b, seed=seed)
        ca = pg.inner_text('.card:has([data-id=ta])')
        ok(['A-016', 'A-018', 'A-019', 'A-020'], pg.eval_on_selector_all('#grid .grid > .card', 'e=>e.length') == 4 and '[TEST] Sommer 2027' in ca and 'Mallorca' in ca and '19.7.' in ca, 'Raster mit 4 Karten; Titel, Ziel, Zeitraum auf Kachel')
        ok('A-021', pg.eval_on_selector_all('.card:has([data-id=ta]) .av', 'e=>e.length') == 3, 'Avatare der Mitreisenden (3)')
        ok('A-022', 'Beobachten' in ca, 'Status-Badge')
        ok('A-023', 'ab 700' in ca and 'p. P.' in ca and '2.100' in ca, 'Bestpreis „ab 700 € p. P. · 2.100 € gesamt“: %s' % ca.replace('\n', ' ')[:140])
        ok('A-024', '↓' in ca and '↑' in pg.inner_text('.card:has([data-id=tb])'), 'Trend: Tal ↓ (800→700), Rom ↑ (300→350)')
        ok('A-025', 'Letzter Check' in ca and '2026' in ca, 'Datum des letzten Checks')
        ok('A-037', pg.query_selector('.card:has([data-id=ta]) svg.spark') is not None, 'Preisverlauf-Kurve in der Kachel')
        ok(['A-017', 'A-135'], pg.eval_on_selector('.card .img', 'e => getComputedStyle(e).borderRadius') in ('16px',) and pg.eval_on_selector('.card .img', 'e=>e.getBoundingClientRect().height/e.getBoundingClientRect().width') > 0.7, 'Abgerundete Bildfläche 4:3 mit 16px Radius')
        tr0 = pg.eval_on_selector('.card:has([data-id=tb])', 'e=>getComputedStyle(e).transform')
        pg.hover('.card:has([data-id=tb]) .img'); pg.wait_for_timeout(350)
        tr1 = pg.eval_on_selector('.card:has([data-id=tb])', 'e=>getComputedStyle(e).transform')
        ok('A-017', tr0 != tr1, 'Hover-Effekt hebt Kachel an (%s → %s)' % (tr0, tr1))
        ok('A-026', pg.query_selector('.card img') is None and 'linear-gradient' in pg.eval_on_selector('.card:has([data-id=ta]) .img', 'e=>e.style.background') and ('🏖' in pg.inner_text('.card:has([data-id=ta]) .img')), 'Ohne Bild: Farbverlauf mit Emoji, keine Portalbilder')
        pg.screenshot(path=os.path.join(SHOTS, '07-startseite-desktop.png'))
        # Filter
        pg.click('[data-act=fstatus][data-v=Gebucht]'); pg.wait_for_timeout(200)
        ok('A-027', pg.eval_on_selector_all('#grid .grid > .card:not(.new-card)', 'e=>e.length') == 1, 'Filter Status „Gebucht“ → 1 Kachel')
        pg.click('[data-act=fstatus][data-v=""]'); pg.select_option('#f-person', 'p_matteo'); pg.wait_for_timeout(200)
        ok('A-028', pg.eval_on_selector_all('#grid .grid > .card:not(.new-card)', 'e=>e.length') == 1, 'Filter Mitreisende „Matteo“ → 1 Kachel')
        pg.select_option('#f-person', ''); pg.fill('#f-q', 'rom'); pg.wait_for_timeout(200)
        ok('A-029', pg.eval_on_selector_all('#grid .grid > .card:not(.new-card)', 'e=>e.length') == 1, 'Suche „rom“ → 1 Kachel')
        pg.fill('#f-q', ''); pg.select_option('#f-sort', 'preis'); pg.wait_for_timeout(200)
        order = pg.eval_on_selector_all('#grid .c-title', 'e=>e.map(x=>x.innerText)')
        ok('A-030', order[0] == '[TEST] Städtetrip Rom' and order[1] == '[TEST] Sommer 2027' and order[2] == '[TEST] Skiurlaub', 'Sortierung nach Preis: %s' % order)
        pg.select_option('#f-sort', 'datum'); pg.wait_for_timeout(200)
        order2 = pg.eval_on_selector_all('#grid .c-title', 'e=>e.map(x=>x.innerText)')
        ok('A-030', order2[0] == '[TEST] Skiurlaub', 'Sortierung nach Reisedatum: %s' % order2)
        pg.select_option('#f-sort', 'updated'); pg.wait_for_timeout(200)
        ok('A-030', pg.eval_on_selector_all('#grid .c-title', 'e=>e.map(x=>x.innerText)')[0] == '[TEST] Sommer 2027', 'Sortierung nach zuletzt aktualisiert')
        pg.reload(); pg.wait_for_function('window.__db !== undefined'); pg.evaluate('(s) => window.__db._seed(s)', seed); pg.wait_for_timeout(300)
        ok('A-130', pg.input_value('#f-sort') == 'updated' and pg.eval_on_selector_all('#f-status .chip[aria-pressed=true]', 'e=>e.map(x=>x.innerText)') == ['Alle'], 'Filter und Sortierung werden nach dem Neuladen gemerkt')
        # Kachelmenü
        pg.click('[data-act=menu][data-id=tb]'); pg.wait_for_timeout(150)
        items = pg.eval_on_selector_all('.menu button', 'e=>e.map(x=>x.innerText)')
        ok(['A-032', 'A-033', 'A-034', 'A-035'], items == ['Öffnen', 'Jetzt suchen', 'Optimieren', 'Duplizieren', 'Archivieren'], 'Kachelmenü: %s' % items)
        pg.screenshot(path=os.path.join(SHOTS, '08-kachelmenue.png'))
        pg.click('.menu button:has-text("Optimieren")'); pg.wait_for_selector('#mf'); submit(pg); pg.wait_for_timeout(200)
        ok('A-033', any(a['trip'] == 'tb' and a['art'] == 'optimieren' for a in docs(pg, 'auftraege').values()), 'Optimieren aus dem Kachelmenü legt Auftrag an')
        pg.click('[data-act=menu][data-id=tb]'); pg.click('.menu button:has-text("Duplizieren")'); pg.wait_for_timeout(400)
        tt = docs(pg, 'trips')
        ok('A-034', sum(1 for v in tt.values() if v['titel'] == '[TEST] Städtetrip Rom (Kopie)') == 1 and any(v['titel'] == '[TEST] Städtetrip Rom (Kopie)' and v['status'] == 'Idee' for v in tt.values()), 'Duplizieren erzeugt „(Kopie)“ mit Status Idee')
        pg.click('[data-act=menu][data-id=tc]'); pg.click('.menu button:has-text("Archivieren")'); pg.wait_for_timeout(400)
        ok('A-035', docs(pg, 'trips')['tc']['archiviert'] is True and pg.query_selector('[data-act=open][data-id=tc]') is None, 'Archivieren blendet Kachel aus')
        pg.check('#f-archiv'); pg.wait_for_timeout(300)
        ok('A-035', pg.query_selector('[data-act=open][data-id=tc]') is not None, 'Archiv-Ansicht zeigt die Kachel')
        pg.click('[data-act=menu][data-id=tc]'); pg.click('.menu button:has-text("Wiederherstellen")'); pg.wait_for_timeout(300)
        ok('A-035', docs(pg, 'trips')['tc']['archiviert'] is False, 'Wiederherstellen')
        pg.uncheck('#f-archiv')
        pg.click('[data-act=open][data-id=tc]'); pg.wait_for_selector('#dtabs'); pg.click('[data-act=tab][data-v=angebote]'); pg.wait_for_timeout(300)
        ok(['A-118', 'A-130'], 'Noch kein Digest' in pg.inner_text('#a-body') and 'Noch keine Angebote erfasst' in pg.inner_text('#a-body') and 'Das Team recherchiert nur auf Zuruf' in pg.inner_text('#a-body'), 'Reise ohne Angebote: verständlicher Leerzustand mit nächstem Schritt')
        pg.click('[data-act=nav][data-v=reisen]'); pg.wait_for_selector('#grid .card')
        # Angebote-Tab
        pg.click('[data-act=open][data-id=ta]'); pg.wait_for_selector('#dtabs'); pg.click('[data-act=tab][data-v=angebote]'); pg.wait_for_timeout(300)
        ang = pg.inner_text('#a-body'); ang_l = ang.lower()
        ok(['A-109', 'A-122'], 'quelle' in ang_l and 'unsicher' in ang_l and 'stand' in ang_l, 'Angebote zeigen Stand-Datum, Quelle und „unsicher“')
        ok(['A-112', 'A-038'], pg.query_selector('#a-body svg[role=img]') is not None, 'Preisverlauf-Kurve im Tab Angebote')
        ok(['A-115', 'A-116'], 'abwarten' in ang and 'Top 3' in ang and pg.evaluate('window.__xss4') is None, 'Digest in der App (Empfehlung, Top 3), Skript im Digest wirkungslos')
        ok('A-123', 'Gesamt' in ang and '2.100' in ang, 'Gesamtpreis-Spalte vorhanden')
        pg.screenshot(path=os.path.join(SHOTS, '09-angebote.png'), full_page=True)
        ctx.close()

        # ---------- Responsive, Dunkelmodus, Tastatur ----------
        for name, w, h, scheme in [('desktop', 1440, 900, 'light'), ('tablet', 820, 1100, 'light'), ('handy', 390, 844, 'light'), ('handy-dunkel', 390, 844, 'dark'), ('desktop-dunkel', 1440, 900, 'dark')]:
            ctx, pg = new_page(b, w, h, scheme, seed=seed)
            pg.wait_for_timeout(300)
            hs = pg.evaluate('() => document.documentElement.scrollWidth - document.documentElement.clientWidth')
            ok('A-129', hs <= 0, '%s (%d px): horizontales Überlaufen %d px' % (name, w, hs))
            cols = pg.evaluate("() => new Set([...document.querySelectorAll('#grid .grid > .card')].map(c=>Math.round(c.getBoundingClientRect().left))).size")
            if name == 'handy': ok('A-004', cols == 1, 'Handy: Kacheln einspaltig (%d Spalte)' % cols)
            if name == 'desktop': ok('A-016', cols >= 3, 'Desktop: %d Spalten' % cols)
            bg = pg.evaluate("() => getComputedStyle(document.body).backgroundColor")
            if 'dunkel' in name: ok('A-005', bg != 'rgb(255, 255, 255)' and int(re.findall(r'\d+', bg)[0]) < 60, 'Dunkelmodus folgt System (%s)' % bg)
            pg.screenshot(path=os.path.join(SHOTS, f'10-start-{name}.png'), full_page=True)
            if name == 'handy':
                pg.click('[data-act=open][data-id=ta]'); pg.wait_for_selector('#dtabs')
                ok('A-129', pg.evaluate('() => document.documentElement.scrollWidth - document.documentElement.clientWidth') <= 0, 'Handy: Detailansicht ohne horizontales Scrollen')
                pg.click('[data-act=tab][data-v=plan]'); pg.wait_for_timeout(250)
                ok('A-129', pg.evaluate('() => document.documentElement.scrollWidth - document.documentElement.clientWidth') <= 0, 'Handy: Reiseplan ohne horizontales Scrollen')
                pg.screenshot(path=os.path.join(SHOTS, '11-detail-handy.png'), full_page=True)
                pg.click('[data-act=nav][data-v=reisen]'); pg.wait_for_selector('#grid .card')
                pg.click('[data-act=neu]'); pg.wait_for_selector('#mf')
                ok('A-129', pg.evaluate('() => document.querySelector("#dlg").scrollWidth <= document.querySelector("#dlg").clientWidth + 1'), 'Handy: Eingabemaske ohne horizontales Scrollen')
                pg.screenshot(path=os.path.join(SHOTS, '12-maske-handy.png'))
            ctx.close()
        # Tastatur
        ctx, pg = new_page(b, seed=seed)
        pg.keyboard.press('Tab'); pg.keyboard.press('Tab'); pg.keyboard.press('Tab')
        foc = pg.evaluate("() => document.activeElement.tagName + ':' + (document.activeElement.getAttribute('data-act')||document.activeElement.id||'')")
        pg.focus('[data-act=open][data-id=ta]'); pg.keyboard.press('Enter'); pg.wait_for_selector('#dtabs')
        ok('A-131', 'BUTTON' in foc or 'SELECT' in foc or 'INPUT' in foc, 'Tab erreicht Bedienelemente (%s); Enter öffnet Kachel' % foc)
        pg.focus('[data-act=tab][data-v=angebote]'); pg.keyboard.press('Shift+Tab'); pg.keyboard.press('Tab')
        outline = pg.evaluate("() => { const e=document.activeElement; const c=getComputedStyle(e); return c.outlineStyle + ' ' + c.outlineWidth }")
        ok('A-131', not outline.startswith('none'), 'Fokusrahmen sichtbar bei Tastaturbedienung (%s)' % outline)
        pg.click('[data-act=nav][data-v=reisen]'); pg.click('[data-act=menu][data-id=ta]'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok('A-131', pg.query_selector('.menu') is None, 'Escape schließt das Kachelmenü')
        ctx.close()

        # ---------- Leistung mit 20 Reisen ----------
        big = dict(TRAV)
        for i in range(20):
            big[f'trips/t{i:02d}'] = trip_doc(f'[TEST] Reise {i}', ['Idee', 'Recherche', 'Beobachten', 'Buchungsreif', 'Gebucht'][i % 5], geaendert=f'2026-10-{(i % 28) + 1:02d}T10:00:00Z')
            for j in range(5):
                big[f'prices/p{i:02d}_{j}'] = {'trip': f't{i:02d}', 'datum': f'2026-10-{10 + j}', 'anbieter': 'A', 'ziel': 'Z', 'beschreibung': 'b', 'preis_pp': 700 + j * 10 + i, 'preis_gesamt': None, 'link': '', 'unsicher': False, 'quelle': 'q'}
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}); ctx.route(re.compile(r'^https?://'), lambda r: r.abort()); pg = ctx.new_page()
        pg.add_init_script('window.__SEED__=' + json.dumps(big))
        t0 = time.time(); pg.goto(PAGE); pg.wait_for_function('window.__db !== undefined')
        pg.evaluate('window.__db._seed(window.__SEED__)')
        pg.wait_for_function("document.querySelectorAll('#grid .grid > .card:not(.new-card)').length === 20", timeout=10000)
        dt = time.time() - t0
        ok('A-128', dt < 2.0, 'Startseite mit 20 Reisen und 100 Preisen: %.2f s (Lokaltest ohne Netz, Datenbankzugriff simuliert)' % dt)
        ctx.close()

        b.close()
    ok('A-134', not ERRS, 'Keine JavaScript-Fehler in der Konsole: %s' % ERRS[:3])
    json.dump(RES, open(os.path.join(QA, 'ergebnisse.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nErgebnis: %d bestanden, %d durchgefallen' % (sum(r['ok'] for r in RES), sum(not r['ok'] for r in RES)))


if __name__ == '__main__':
    main()
