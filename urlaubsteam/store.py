"""Lokale JSON-Ablage. Alle Daten liegen in ./data, Digests in ./digests."""
import json
import uuid
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DIGESTS = ROOT / "digests"

STATUS = ["Idee", "Recherche", "Beobachten", "Buchungsreif", "Gebucht"]
REISEARTEN = ["Strand", "Städtetrip", "Natur/Aktiv", "Rundreise", "Skifahren", "Wellness", "Sonstiges"]
UNTERKUNFT = ["Hotel", "Ferienwohnung/-haus", "Resort"]
VERPFLEGUNG = ["egal", "Frühstück", "Halbpension", "Vollpension", "All-inclusive", "Selbstversorger"]
ANREISE = ["Flug", "Bahn", "Auto"]
FLUGHAEFEN = ["Köln/Bonn (CGN)", "Düsseldorf (DUS)", "Frankfurt (FRA)", "Weeze (NRN)", "Dortmund (DTM)"]
BEZIEHUNG = ["Familie", "Kind", "Freunde", "Sonstige"]
BUDGET_MODI = {
    "fest": "Festes Budget",
    "richtwert": "Richtwert (darf abweichen, wenn es sich lohnt)",
    "offen": "Offen – überrasch uns, Budget richtet sich nach dem Angebot",
}


def _path(name: str) -> Path:
    return DATA / f"{name}.json"


def load(name: str, default):
    p = _path(name)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save(name: str, obj) -> None:
    DATA.mkdir(exist_ok=True)
    p = _path(name)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(p)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def today() -> str:
    return date.today().isoformat()


def now() -> str:
    return datetime.now().isoformat(timespec="minutes")


# ---------- Mitreisende ----------
def travelers() -> list[dict]:
    return load("travelers", [])


def save_traveler(t: dict) -> None:
    items = travelers()
    for i, x in enumerate(items):
        if x["id"] == t["id"]:
            items[i] = t
            break
    else:
        items.append(t)
    save("travelers", items)


def delete_traveler(tid: str) -> None:
    save("travelers", [t for t in travelers() if t["id"] != tid])


def traveler_name(tid: str) -> str:
    return next((t["name"] for t in travelers() if t["id"] == tid), tid)


# ---------- Reisen ----------
def trips() -> list[dict]:
    return load("trips", [])


def save_trip(t: dict) -> None:
    t["geaendert"] = now()
    items = trips()
    for i, x in enumerate(items):
        if x["id"] == t["id"]:
            items[i] = t
            break
    else:
        t.setdefault("erstellt", now())
        items.append(t)
    save("trips", items)


def delete_trip(tid: str) -> None:
    save("trips", [t for t in trips() if t["id"] != tid])


def blank_trip() -> dict:
    return {
        "id": new_id("trip"), "titel": "", "status": "Idee",
        "zeitraum": {"fruehester_start": None, "spaetester_rueckflug": None,
                     "dauer_min": 7, "dauer_max": 14, "flex_tage": 0},
        "ziele": {"modus": "offen", "text": ""},
        "reiseart": [],
        "budget": {"modus": "offen", "gesamt": None, "pro_person_max": None},
        "unterkunft": {"typ": [], "min_sterne": 0, "min_bewertung": 0.0, "verpflegung": "egal"},
        "anreise": {"modi": ["Flug"], "direktflug": False, "max_reisezeit_h": None,
                    "abflughaefen": ["Köln/Bonn (CGN)", "Düsseldorf (DUS)"]},
        "muss": [], "nogos": [],
        "mitreisende": [],
        "gruppe": {"aktiv": False, "haushalte": []},
        "beobachten": {"checks_pro_woche": 2, "schwelle_prozent": 10},
        "notizen": "",
    }


# ---------- Ideen & Vorschläge ----------
def ideas() -> list[dict]:
    return load("ideas", [])


def save_idea(i: dict) -> None:
    items = ideas()
    for k, x in enumerate(items):
        if x["id"] == i["id"]:
            items[k] = i
            break
    else:
        items.append(i)
    save("ideas", items)


def rate(idea_id: str, rating: str | None) -> None:
    """rating: 'up' | 'down' | None. Aktualisiert danach die gelernten Präferenzen."""
    items = ideas()
    for x in items:
        if x["id"] == idea_id:
            x["bewertung"] = rating
    save("ideas", items)
    update_preferences()


def update_preferences() -> dict:
    """Zählt Daumen pro Tag (Reiseart, Region, Klima, ...) und speichert das Profil."""
    score: dict[str, int] = {}
    for x in ideas():
        w = {"up": 1, "down": -1}.get(x.get("bewertung"), 0)
        for tag in x.get("tags", []):
            score[tag] = score.get(tag, 0) + w
    prefs = {
        "aktualisiert": now(),
        "mag": sorted([k for k, v in score.items() if v > 0], key=lambda k: -score[k]),
        "mag_nicht": sorted([k for k, v in score.items() if v < 0], key=lambda k: score[k]),
        "scores": score,
    }
    save("preferences", prefs)
    return prefs


# ---------- Preise & Digests ----------
def prices(trip_id: str | None = None) -> list[dict]:
    items = load("price_history", [])
    return [p for p in items if trip_id is None or p["trip_id"] == trip_id]


def latest_digest(trip_id: str | None = None) -> tuple[str, str] | None:
    files = sorted(DIGESTS.glob("*.md"), reverse=True)
    for f in files:
        if trip_id is None or trip_id in f.name:
            return f.name, f.read_text(encoding="utf-8")
    return None
