"""Weekly check of every host star with JWST spectra in the NASA Exoplanet Archive.
Per system: MAST, Exoplanet Archive, arXiv -> reports/systems/<slug>/{state,history}.json + DASHBOARD.md.
Overall: reports/INDEX.md + reports/index_history.json."""
import datetime as dt, json, pathlib, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

R = pathlib.Path(__file__).parent.parent / "reports"
SYS, INDEX, IHIST = R / "systems", R / "INDEX.md", R / "index_history.json"
SRC = ("mast", "archive", "arxiv")
SPARK = "▁▂▃▄▅▆▇█"
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode()


def tap(q):
    return json.loads(get(TAP + urllib.parse.urlencode({"query": q, "format": "json"})))


def hosts():
    q = ("select distinct p.hostname from pscomppars p, spectra s "
         "where p.pl_name = s.pl_name and s.facility like '%JWST%'")
    return sorted({r["hostname"] for r in tap(q)}, key=str.lower)


def mast(host):
    from astroquery.mast import Observations
    t = Observations.query_criteria(objectname=host, radius="0.01 deg", obs_collection="JWST")
    return {str(r["obs_id"]): f'{r["proposal_id"]} {r["instrument_name"]} release {r["t_obs_release"]}' for r in t}


def archive(host):
    q = ("select pl_name,pl_rade,pl_bmasse,pl_eqt,st_teff,st_rad,pl_rade_reflink from pscomppars "
         f"where hostname='{host.replace(chr(39), chr(39) * 2)}'")
    return {f"{r['pl_name']}.{k}": v for r in tap(q) for k, v in r.items() if k != "pl_name"}


def arxiv(host):
    time.sleep(3)  # arXiv API etiquette: one request per 3 s
    q = urllib.parse.urlencode({"search_query": f'all:"{host}" AND (all:JWST OR all:atmosphere)',
                                "sortBy": "submittedDate", "max_results": 25})
    ns = {"a": "http://www.w3.org/2005/Atom"}
    return {re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1]): " ".join(e.find("a:title", ns).text.split())
            for e in ET.fromstring(get("http://export.arxiv.org/api/query?" + q)).findall("a:entry", ns)}


def spark(xs):
    lo, hi = min(xs), max(xs)
    return "".join(SPARK[0 if hi == lo else round((x - lo) / (hi - lo) * 7)] for x in xs)


def bar(n, tot, w=20):
    k = round(n / tot * w) if tot else 0
    return "█" * k + "░" * (w - k)


def mjd(x):
    try:
        return dt.date(1858, 11, 17) + dt.timedelta(days=int(float(x)))
    except ValueError:
        return None  # masked/unknown release date


def slug(h):
    return re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")


def dashboard(host, state, hist, errors):
    today = dt.date.today()
    m, a, x = state["mast"], state["archive"], state["arxiv"]
    obs = []
    for oid, v in m.items():
        prog, inst, rel = re.match(r"(\S+) (.+?) release (\S+)", v).groups()
        obs.append((mjd(rel), prog, inst, oid))
    obs.sort(key=lambda o: o[0] or dt.date.max)
    insts = {}
    for _, _, i, _ in obs:
        insts[i.split("/")[0]] = insts.get(i.split("/")[0], 0) + 1
    last = {s: next((h["date"] for h in reversed(hist) if h["new"][s]), "never") for s in SRC}
    ok = lambda s: "● FAIL" if s in errors else "● ok"
    L = ["```", "╔══════════════════════════════════════════════╗",
         f"║   {host[:30].upper()}  ·  JWST WATCH".ljust(47) + "║",
         f"║   checked {today}   ·   {len(hist)} run-days logged".ljust(47) + "║",
         "╚══════════════════════════════════════════════╝", "```", "[← all systems](../../INDEX.md)", "",
         "## ▌ Status", "", "| source | status | total | new today | last change |", "|---|---|---:|---:|---|"]
    n_pl = len({k.rsplit(".", 1)[0] for k in a})
    for s, tot in (("mast", len(m)), ("archive", n_pl), ("arxiv", len(x))):
        L.append(f"| {s} | {ok(s)} | {tot}{' planets' if s == 'archive' else ''} | {len(hist[-1]['new'][s])} | {last[s]} |")
    L += [f"\n> ⚠ {s} failed: {e} (showing previous data)" for s, e in errors.items()]
    L += ["", "## ▌ Trend (per run-day, oldest → newest)", "", "```"]
    h = hist[-24:]
    L += [f"MAST   {spark([e['mast_n'] for e in h])}  {h[-1]['mast_n']}", f"arXiv  {spark([e['arxiv_n'] for e in h])}  {h[-1]['arxiv_n']}", "```"]
    if insts:
        L += ["", "## ▌ JWST coverage by instrument", "", "```"]
        L += [f"{i:8s} {bar(n, len(obs))} {n}" for i, n in sorted(insts.items())]
        L += ["```", "", "## ▌ JWST observations", "", "| release | status | program | instrument | obs id |", "|---|---|---|---|---|"]
        for d, prog, inst, oid in obs[-40:]:
            L.append(f"| {d or '?'} | {'◉ public' if d and d <= today else '○ proprietary' if d else '? unknown'} | {prog} | {inst} | `{oid}` |")
        if len(obs) > 40:
            L.append(f"\n_Showing the 40 latest of {len(obs)}; full list in `state.json`._")
    L += ["", "## ▌ Planets (NASA Exoplanet Archive)", "", "| planet | radius (R⊕) | mass (M⊕) | Teq (K) |", "|---|---:|---:|---:|"]
    for pl in sorted({k.rsplit(".", 1)[0] for k in a}):
        L.append(f"| {pl} | {a.get(pl + '.pl_rade')} | {a.get(pl + '.pl_bmasse')} | {a.get(pl + '.pl_eqt')} |")
    st = next((k.rsplit(".", 1)[0] for k in a), None)
    if st:
        L.append(f"\nStar: Teff {a.get(st + '.st_teff')} K, radius {a.get(st + '.st_rad')} R☉")
    L += ["", "## ▌ Latest papers (arXiv)", ""]
    L += [f"- [`{k}`](https://arxiv.org/abs/{k})  {t}" for k, t in list(x.items())[:8]] or ["_none found_"]
    L += ["", "## ▌ History", "", "```", "date         MAST  arXiv  new  changes"]
    for e in reversed(hist[-15:]):
        n = sum(len(v) for v in e["new"].values())
        L.append(f"{e['date']}   {e['mast_n']:4d}  {e['arxiv_n']:5d}  {n:3d}  {'●' * min(n, 12) or '·'}")
    L += ["```", "", "<sub>Auto-generated by `scripts/weekly_check.py`. \"new\" = not seen in the previous run.</sub>", ""]
    return "\n".join(L)


def index(rows, ih):
    today = dt.date.today()
    tot_obs, tot_pap = sum(r["obs"] for r in rows), sum(r["papers"] for r in rows)
    news = [r for r in rows if r["new"]]
    L = ["```", "╔══════════════════════════════════════════════╗",
         "║   JWST EXOPLANET WATCH  ·  ALL SYSTEMS       ║",
         f"║   checked {today}".ljust(47) + "║",
         "╚══════════════════════════════════════════════╝", "```", "",
         "## ▌ At a glance", "", "| systems | planets | JWST observations | papers | systems with news |", "|---:|---:|---:|---:|---:|",
         f"| {len(rows)} | {sum(r['planets'] for r in rows)} | {tot_obs} | {tot_pap} | {len(news)} |", "",
         "## ▌ Trend (per run-day)", "", "```"]
    h = ih[-24:]
    L += [f"JWST obs  {spark([e['obs'] for e in h])}  {h[-1]['obs']}", f"papers    {spark([e['papers'] for e in h])}  {h[-1]['papers']}",
          f"news      {spark([e['news'] for e in h])}  {h[-1]['news']}", "```", "", "## ▌ Most JWST data", "", "```"]
    top = sorted(rows, key=lambda r: -r["obs"])[:15]
    L += [f"{r['host'][:16]:16s} {bar(r['obs'], top[0]['obs'])} {r['obs']}" for r in top]
    L += ["```", "", "## ▌ All systems", "", "| system | planets | JWST obs | papers | new this run | last change |", "|---|---:|---:|---:|---:|---|"]
    for r in sorted(rows, key=lambda r: (-r["new"], r["host"].lower())):
        L.append(f"| [{r['host']}](systems/{slug(r['host'])}/DASHBOARD.md) | {r['planets']} | {r['obs']} | {r['papers']} | "
                 f"{r['new'] or '·'}{' ⚠' if r['errors'] else ''} | {r['last']} |")
    L += ["", "## ▌ History", "", "```", "date         systems   obs  papers  news"]
    for e in reversed(ih[-15:]):
        L.append(f"{e['date']}   {e['systems']:6d}  {e['obs']:4d}  {e['papers']:6d}  {e['news']:4d}")
    L += ["```", "", "<sub>⚠ = a source failed this run. List comes from the NASA Exoplanet Archive spectra table (JWST facility).</sub>", ""]
    return "\n".join(L)


def check(host):
    d = SYS / slug(host)
    d.mkdir(parents=True, exist_ok=True)
    sf, hf = d / "state.json", d / "history.json"
    old = json.loads(sf.read_text()) if sf.exists() else {}
    hist = json.loads(hf.read_text()) if hf.exists() else []
    new, news, errors = {}, {}, {}
    for name, fn in (("mast", mast), ("archive", archive), ("arxiv", arxiv)):
        o = old.get(name, {})
        try:
            new[name] = fn(host)
        except Exception as e:  # one failing source must not hide the others
            new[name], errors[name] = o, repr(e)
        news[name] = ([f"{k}: {a} -> {b}" for k, b in new[name].items() if (a := o.get(k)) != b]
                      if name == "archive" else [k for k in new[name] if k not in o])
    today = str(dt.date.today())
    if hist and hist[-1]["date"] == today:  # same-day rerun: merge so nothing is lost
        e = hist.pop()
        news = {s: e["new"][s] + [i for i in news[s] if i not in e["new"][s]] for s in SRC}
    hist.append({"date": today, "mast_n": len(new["mast"]), "arxiv_n": len(new["arxiv"]), "new": news})
    sf.write_text(json.dumps(new, indent=1, sort_keys=True))
    hf.write_text(json.dumps(hist, indent=1))
    (d / "DASHBOARD.md").write_text(dashboard(host, new, hist, errors))
    return {"host": host, "planets": len({k.rsplit(".", 1)[0] for k in new["archive"]}), "obs": len(new["mast"]),
            "papers": len(new["arxiv"]), "new": sum(len(v) for v in news.values()), "errors": bool(errors),
            "last": next((h["date"] for h in reversed(hist) if any(h["new"].values())), "never")}


if __name__ == "__main__":
    rows = []
    for host in hosts():
        rows.append(check(host))
        print(host, rows[-1]["obs"], "obs", rows[-1]["new"], "new", flush=True)
    ih = json.loads(IHIST.read_text()) if IHIST.exists() else []
    today = str(dt.date.today())
    ih = [e for e in ih if e["date"] != today] + [{"date": today, "systems": len(rows), "obs": sum(r["obs"] for r in rows),
         "papers": sum(r["papers"] for r in rows), "news": sum(1 for r in rows if r["new"])}]
    IHIST.write_text(json.dumps(ih, indent=1))
    INDEX.write_text(index(rows, ih))
