"""Urlaubs-Team – lokale Eingabemaske. Start: streamlit run app.py"""
from datetime import date

import pandas as pd
import streamlit as st

from urlaubsteam import store as s

st.set_page_config(page_title="Urlaubs-Team", page_icon="🌴", layout="wide")

PAGES = ["Reisen", "Mitreisende", "Ideen-Pool", "Preise & Digest", "Team & Anleitung"]
page = st.sidebar.radio("Bereich", PAGES)
st.sidebar.caption("Daten liegen lokal in ./data. Gebucht wird nur nach deiner Freigabe.")


def lines(text: str) -> list[str]:
    return [x.strip() for x in text.replace(",", "\n").splitlines() if x.strip()]


def d(v):
    return date.fromisoformat(v) if v else None


# ======================================================== Mitreisende
def page_travelers():
    st.header("Mitreisende")
    people = s.travelers()
    for t in people:
        age = f"{t['alter']} J." if t.get("alter") is not None else "Alter offen"
        with st.expander(f"{t['name']} · {t['beziehung']} · {age}"):
            traveler_form(t)
    st.subheader("Neue Person")
    traveler_form(None)


def traveler_form(t):
    new = t is None
    t = t or {"id": s.new_id("p"), "name": "", "beziehung": "Familie", "alter": None,
              "ernaehrung": "", "mobilitaet": "", "allergien": "", "interessen": "",
              "wunsch_veto": "", "dokument_gueltig_bis": None}
    with st.form(f"tf_{t['id']}", clear_on_submit=new):
        c = st.columns(3)
        t["name"] = c[0].text_input("Name", t["name"])
        t["beziehung"] = c[1].selectbox("Beziehung", s.BEZIEHUNG, s.BEZIEHUNG.index(t["beziehung"]))
        has_age = c[2].number_input("Alter (Pflicht bei Kindern)", 0, 120, t["alter"] or 0)
        t["geburt_monat"] = st.text_input("Geburtsmonat (JJJJ-MM, optional)", t.get("geburt_monat", ""))
        t["ernaehrung"] = st.text_input("Ernährung", t["ernaehrung"])
        c = st.columns(2)
        t["mobilitaet"] = c[0].text_input("Mobilität", t["mobilitaet"])
        t["allergien"] = c[1].text_input("Allergien", t["allergien"])
        t["interessen"] = st.text_input("Interessen", t["interessen"])
        t["wunsch_veto"] = st.text_input("Wunsch / Veto zur Reise (optional)", t["wunsch_veto"])
        t["dokument_gueltig_bis"] = _opt_date(st, "Reisedokument gültig bis (nur Hinweis, keine Nummern!)",
                                              t["dokument_gueltig_bis"])
        ok = st.form_submit_button("Speichern")
        delete = False if new else st.form_submit_button("Löschen")
    if ok:
        if not t["name"]:
            st.error("Name fehlt.")
        elif t["beziehung"] == "Kind" and not has_age:
            st.error("Bei Kindern ist das Alter Pflicht.")
        else:
            t["alter"] = int(has_age) if (has_age or t["beziehung"] == "Kind") else t["alter"]
            s.save_traveler(t)
            st.rerun()
    if delete:
        s.delete_traveler(t["id"])
        st.rerun()


def _opt_date(container, label, value):
    r = container.date_input(label, d(value), format="DD.MM.YYYY")
    return r.isoformat() if r else None


# ======================================================== Reisen
def page_trips():
    st.header("Reisen")
    items = s.trips()
    if items:
        df = pd.DataFrame([{
            "Titel": t["titel"], "Status": t["status"],
            "Start ab": t["zeitraum"]["fruehester_start"], "Rückflug bis": t["zeitraum"]["spaetester_rueckflug"],
            "Ziel": t["ziele"]["text"] or t["ziele"]["modus"],
            "Budget": s.BUDGET_MODI[t["budget"]["modus"]].split(" – ")[0].split(" (")[0],
        } for t in items])
        st.dataframe(df, hide_index=True, width="stretch")
    options = {t["titel"] or t["id"]: t["id"] for t in items}
    choice = st.selectbox("Reise bearbeiten", ["➕ Neue Reise"] + list(options))
    trip = s.blank_trip() if choice.startswith("➕") else next(t for t in items if t["id"] == options[choice])
    trip_form(trip, new=choice.startswith("➕"))


def trip_form(t, new):
    people = {p["id"]: p["name"] for p in s.travelers()}
    z, b, u, a, bo = t["zeitraum"], t["budget"], t["unterkunft"], t["anreise"], t["beobachten"]
    with st.form(f"trip_{t['id']}"):
        c = st.columns([3, 2])
        t["titel"] = c[0].text_input("Titel der Reise", t["titel"], placeholder="z. B. Sommer 2027")
        t["status"] = c[1].selectbox("Status", s.STATUS, s.STATUS.index(t["status"]))

        st.subheader("Zeitraum")
        c = st.columns(5)
        z["fruehester_start"] = _opt_date(c[0], "Frühester Start", z["fruehester_start"])
        z["spaetester_rueckflug"] = _opt_date(c[1], "Spätester Rückflug", z["spaetester_rueckflug"])
        z["dauer_min"] = c[2].number_input("Dauer von (Tage)", 1, 90, z["dauer_min"])
        z["dauer_max"] = c[3].number_input("Dauer bis (Tage)", 1, 90, z["dauer_max"])
        z["flex_tage"] = c[4].number_input("Flexibilität ± Tage", 0, 30, z["flex_tage"])

        st.subheader("Reiseziele & Art")
        c = st.columns([1, 3])
        modi = ["konkret", "Region", "offen"]
        t["ziele"]["modus"] = c[0].radio("Ziele", modi, modi.index(t["ziele"]["modus"]) if t["ziele"]["modus"] in modi else 2)
        t["ziele"]["text"] = c[1].text_input("Wohin? (bei „offen“ liefert das Team Vorschläge)", t["ziele"]["text"])
        t["reiseart"] = st.multiselect("Reiseart", s.REISEARTEN, t["reiseart"])

        st.subheader("Budget")
        bm = list(s.BUDGET_MODI)
        b["modus"] = st.radio("Budget-Modus", bm, bm.index(b["modus"]), format_func=s.BUDGET_MODI.get)
        c = st.columns(2)
        b["gesamt"] = c[0].number_input("Budget gesamt (€) – 0 = keins", 0, 200000, int(b["gesamt"] or 0), step=250) or None
        b["pro_person_max"] = c[1].number_input("Max. pro Person (€) – 0 = keins", 0, 50000,
                                                int(b["pro_person_max"] or 0), step=100) or None

        st.subheader("Unterkunft")
        c = st.columns(4)
        u["typ"] = c[0].multiselect("Typ", s.UNTERKUNFT, u["typ"])
        u["min_sterne"] = c[1].slider("Mindest-Sterne", 0, 5, u["min_sterne"])
        u["min_bewertung"] = c[2].slider("Mindest-Bewertung (von 10)", 0.0, 10.0, float(u["min_bewertung"]), 0.1)
        u["verpflegung"] = c[3].selectbox("Verpflegung", s.VERPFLEGUNG, s.VERPFLEGUNG.index(u["verpflegung"]))

        st.subheader("Anreise")
        c = st.columns(4)
        a["modi"] = c[0].multiselect("Verkehrsmittel", s.ANREISE, a["modi"])
        a["abflughaefen"] = c[1].multiselect("Abflughäfen", s.FLUGHAEFEN, a["abflughaefen"])
        a["direktflug"] = c[2].checkbox("Nur Direktflug", a["direktflug"])
        a["max_reisezeit_h"] = c[3].number_input("Max. Reisezeit (Std.) – 0 = egal", 0, 48, int(a["max_reisezeit_h"] or 0)) or None

        st.subheader("Kriterien")
        c = st.columns(2)
        t["muss"] = lines(c[0].text_area("Muss-Kriterien (eins pro Zeile)", "\n".join(t["muss"]), placeholder="Pool\nStrandnähe\nKinderclub"))
        t["nogos"] = lines(c[1].text_area("No-Gos (eins pro Zeile)", "\n".join(t["nogos"]), placeholder="Umstiege"))

        st.subheader("Mitreisende")
        t["mitreisende"] = st.multiselect("Wer fährt mit?", list(people), t["mitreisende"], format_func=people.get)
        g = t["gruppe"]
        g["aktiv"] = st.checkbox("Gruppenreise (mehrere Haushalte, getrennte Budgets)", g["aktiv"])
        if g["aktiv"]:
            raw = "\n".join(f"{h['name']} | {h.get('personen', '')} | {h.get('budget') or ''}" for h in g["haushalte"])
            txt = st.text_area("Haushalte: „Name | Personen | Budget €“ (eine Zeile pro Haushalt)", raw,
                               placeholder="Familie Reichel | 2 Erw. + 1 Kind (5) | 5000\nFreunde Müller | 2 Erw. | 3000")
            g["haushalte"] = []
            for ln in txt.splitlines():
                p = [x.strip() for x in ln.split("|")]
                if p and p[0]:
                    bud = "".join(ch for ch in (p[2] if len(p) > 2 else "") if ch.isdigit())
                    g["haushalte"].append({"name": p[0], "personen": p[1] if len(p) > 1 else "",
                                           "budget": int(bud) if bud else None})
            t["notizen_gruppe"] = st.text_input("Gemeinsame Wünsche der Gruppe", t.get("notizen_gruppe", ""))

        st.subheader("Beobachtung")
        c = st.columns(2)
        bo["checks_pro_woche"] = c[0].number_input("Preis-Checks pro Woche (bei Status „Beobachten“)", 1, 14, bo["checks_pro_woche"])
        bo["schwelle_prozent"] = c[1].number_input("Meldeschwelle Preisfall (%)", 1, 50, bo["schwelle_prozent"])

        t["notizen"] = st.text_area("Notizen", t["notizen"])
        c = st.columns([1, 1, 6])
        ok = c[0].form_submit_button("Speichern", type="primary")
        rm = False if new else c[1].form_submit_button("Löschen")
    if ok:
        if not t["titel"]:
            st.error("Bitte einen Titel vergeben.")
        elif z["fruehester_start"] and z["spaetester_rueckflug"] and z["fruehester_start"] > z["spaetester_rueckflug"]:
            st.error("Frühester Start liegt nach dem spätesten Rückflug.")
        elif z["dauer_min"] > z["dauer_max"]:
            st.error("Dauer „von“ ist größer als „bis“.")
        else:
            s.save_trip(t)
            kids = [p for p in s.travelers() if p["id"] in t["mitreisende"] and p["beziehung"] == "Kind"]
            st.success("Gespeichert." + (" Kinderalter fließt in die Suche ein." if kids else ""))
    if rm:
        s.delete_trip(t["id"])
        st.rerun()


# ======================================================== Ideen
def page_ideas():
    st.header("Ideen-Pool")
    with st.form("idea", clear_on_submit=True):
        text = st.text_area("Ziel, Artikel, Link, Zitat – Freitext oder URL")
        if st.form_submit_button("In den Pool") and text.strip():
            kind = "link" if text.strip().startswith("http") else "text"
            s.save_idea({"id": s.new_id("idea"), "quelle": "ich", "typ": kind, "inhalt": text.strip(), "datum": s.today(), "tags": []})
            st.rerun()

    st.subheader("Vorschläge vom Scout")
    props = [i for i in s.ideas() if i["quelle"] == "scout"]
    if not props:
        st.info("Noch keine Vorschläge. Der Scout liefert pro Monat 3 neue (Auftrag an Claude: „Scout, neue Vorschläge“).")
    for i in sorted(props, key=lambda x: x["datum"], reverse=True):
        r = i.get("bewertung")
        with st.container(border=True):
            c = st.columns([8, 1, 1])
            c[0].markdown(f"**{i['ziel']}** · {i['monat']}\n\n"
                          f"**Warum passend:** {i['warum']}\n\n"
                          f"**Preisrahmen:** {i['preisrahmen']} · **Bester Zeitraum:** {i['zeitraum']}\n\n"
                          f"**Risiko:** {i['risiko']}")
            if c[1].button("👍", key=f"u{i['id']}", type="primary" if r == "up" else "secondary"):
                s.rate(i["id"], None if r == "up" else "up"); st.rerun()
            if c[2].button("👎", key=f"d{i['id']}", type="primary" if r == "down" else "secondary"):
                s.rate(i["id"], None if r == "down" else "down"); st.rerun()

    st.subheader("Meine Einwürfe")
    for i in [i for i in s.ideas() if i["quelle"] == "ich"]:
        st.markdown(f"- {i['datum']}: {i['inhalt']}")

    prefs = s.load("preferences", None)
    if prefs and (prefs["mag"] or prefs["mag_nicht"]):
        st.subheader("Gelernte Präferenzen")
        st.write("Mag:", ", ".join(prefs["mag"]) or "–")
        st.write("Mag nicht:", ", ".join(prefs["mag_nicht"]) or "–")


# ======================================================== Preise
def page_prices():
    st.header("Preise & Digest")
    trips = s.trips()
    if not trips:
        st.info("Noch keine Reise angelegt.")
        return
    names = {t["titel"]: t["id"] for t in trips}
    sel = st.selectbox("Reise", list(names))
    tid = names[sel]
    dg = s.latest_digest(tid)
    if dg:
        st.caption(f"Letzter Digest: {dg[0]}")
        st.markdown(dg[1])
    else:
        st.info("Noch kein Digest. Check starten: Claude bitten „Preis-Jäger, Check für " + sel + "“.")
    rows = s.prices(tid)
    if rows:
        df = pd.DataFrame(rows)
        st.subheader("Preisverlauf")
        piv = df.pivot_table(index="datum", columns="anbieter", values="preis_pp", aggfunc="min")
        st.line_chart(piv)
        st.dataframe(df[["datum", "anbieter", "beschreibung", "preis_pp", "preis_gesamt", "unsicher", "link"]],
                     hide_index=True, width="stretch",
                     column_config={"link": st.column_config.LinkColumn("Link")})


# ======================================================== Anleitung
def page_help():
    st.header("Team & Anleitung")
    st.markdown((s.ROOT / "README.md").read_text(encoding="utf-8"))


{"Reisen": page_trips, "Mitreisende": page_travelers, "Ideen-Pool": page_ideas,
 "Preise & Digest": page_prices, "Team & Anleitung": page_help}[page]()
