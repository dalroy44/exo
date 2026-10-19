"""Weekly check: MAST, NASA Exoplanet Archive, arXiv. Writes reports/<date>.md and reports/state.json."""
import datetime as dt, json, pathlib, re, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

R = pathlib.Path(__file__).parent.parent / "reports"
STATE = R / "state.json"


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode()


def mast():
    from astroquery.mast import Observations
    t = Observations.query_criteria(objectname="K2-18", radius="0.01 deg", obs_collection="JWST")
    return {str(r["obs_id"]): f'{r["proposal_id"]} {r["instrument_name"]} release {r["t_obs_release"]}' for r in t}


def archive():
    q = "select pl_name,pl_rade,pl_bmasse,pl_eqt,st_teff,st_rad,pl_rade_reflink,pl_bmasse_reflink from pscomppars where pl_name='K2-18 b'"
    rows = json.loads(get("https://exoplanetarchive.ipac.caltech.edu/TAP/sync?" +
                          urllib.parse.urlencode({"query": q, "format": "json"})))
    return rows[0] if rows else {}


def arxiv():
    q = urllib.parse.urlencode({"search_query": 'all:"K2-18" AND (all:JWST OR all:atmosphere)',
                                "sortBy": "submittedDate", "max_results": 25})
    ns = {"a": "http://www.w3.org/2005/Atom"}
    return {re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1]): " ".join(e.find("a:title", ns).text.split())
            for e in ET.fromstring(get("http://export.arxiv.org/api/query?" + q)).findall("a:entry", ns)}


if __name__ == "__main__":
    old = json.loads(STATE.read_text()) if STATE.exists() else {}
    new, out = {}, [f"# K2-18 weekly check {dt.date.today()}\n"]
    for name, fn in (("mast", mast), ("archive", archive), ("arxiv", arxiv)):
        try:
            new[name] = fn()
        except Exception as e:  # one failing source must not hide the others
            new[name] = old.get(name, {})
            out.append(f"## {name}\nFAILED: {e!r} (kept previous state)\n")
            continue
        o = old.get(name, {})
        if name == "archive":
            diff = {k: (o.get(k), v) for k, v in new[name].items() if o.get(k) != v}
            body = "\n".join(f"- {k}: {a} -> {b}" for k, (a, b) in diff.items()) or "no change"
        else:
            body = "\n".join(f"- NEW {k}: {v}" for k, v in new[name].items() if k not in o) or "no new items"
        out.append(f"## {name}\n{body}\n")
    R.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(new, indent=1, sort_keys=True))
    (R / f"{dt.date.today()}.md").write_text("\n".join(out))
    print("\n".join(out))
