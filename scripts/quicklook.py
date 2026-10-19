"""First-pass band significance for a transmission spectrum, or list JWST obs of K2-18."""
import argparse
import datetime as dt
import numpy as np

# band centres/widths in micron; CH4 and DMS overlap near 3.3-3.4 so 3.4 alone can't establish DMS
BANDS = {"H2O_1.4": (1.40, .10), "H2O_1.9": (1.90, .10), "CH4_2.3": (2.30, .10),
         "CH4_3.3": (3.30, .10), "DMS_3.4": (3.42, .08), "CO2_4.3": (4.30, .12),
         # MIRI/LRS: approximate band centres, widths wide enough for R~70 bins (>=2 per band)
         "H2O_6.3": (6.30, .30), "DMS_6.9": (6.90, .30), "CH4_7.7": (7.70, .35), "NH3_10.5": (10.5, .45)}


def band_table(wl, d, e, inflate=1.0):
    e = e * inflate
    rows = []
    for name, (c, w) in BANDS.items():
        m = np.abs(wl - c) < w
        o = (np.abs(wl - c) > w) & (np.abs(wl - c) < 4 * w)  # local continuum
        if m.sum() < 2 or o.sum() < 2:
            rows.append((name, None, None, "no coverage"))
            continue
        wi, wo = 1 / e[m] ** 2, 1 / e[o] ** 2
        mi, mo = np.average(d[m], weights=wi), np.average(d[o], weights=wo)
        err = np.hypot(wi.sum() ** -.5, wo.sum() ** -.5)
        rows.append((name, mi - mo, err, f"{(mi - mo) / err:.1f} sigma"))
    return rows


def load(path):
    """Accept wavelength_um,depth_ppm,err_ppm or Zenodo-style wavelength,dppm,dppm_err[_neg,_pos]."""
    if not path.endswith(".csv"):  # Schmidt/Madhusudhan .dat/.txt: wl, half-width, depth, err; depth as a fraction
        rows = [l.split() for l in open(path) if l.strip() and not (l.lstrip()[0] == "#" or l.lstrip()[0].isalpha())]
        t = np.array(rows, float)
        k = 1e6 if t[:, 2].max() < 1 else 1
        return t[:, 0], t[:, 2] * k, t[:, 3] * k
    t = np.genfromtxt(path, delimiter=",", names=True)
    n = t.dtype.names
    wl = t["wavelength_um" if "wavelength_um" in n else "wavelength"]
    d = t["depth_ppm" if "depth_ppm" in n else "dppm"]
    if "err_ppm" in n: e = t["err_ppm"]
    elif "dppm_err" in n: e = t["dppm_err"]
    else: e = (t["dppm_err_neg"] + t["dppm_err_pos"]) / 2  # asymmetric errors averaged
    return wl, d, e


def scoreboard(paths):
    """Markdown table: per band, the range of sigma across all spectra."""
    res = {b: [] for b in BANDS}
    for p in paths:
        for n, dd, ee, _ in band_table(*load(p)):
            if dd is not None:
                res[n].append(dd / ee)
    rows = [f"_Generated {dt.date.today()} from {len(paths)} spectra by `scripts/quicklook.py`._", "",
            "| gas | band | spectra | range (sigma) | spectra >= 2 sigma | verdict |", "|---|---|---:|---|---:|---|"]
    for n, v in res.items():
        if not v:
            continue
        lo, hi = min(v), max(v)
        word = "noise" if hi < 1 else "weak" if hi < 2 else "hint" if hi < 3 else "interesting" if hi < 5 else "strong"
        k = min(10, max(0, round(hi)))
        gas, um = n.split("_")
        rows.append(f"| {gas} | {um} um | {len(v)} | {lo:.1f} to {hi:.1f} | {sum(x >= 2 for x in v)} | "
                    f"`{'#' * k}{'.' * (10 - k)}` {word}{' (pipelines disagree)' if hi - lo > 2 else ''} |")
    return "\n".join(rows)


def splice(path, md):
    a, b = "<!-- scoreboard:start -->", "<!-- scoreboard:end -->"
    t = open(path).read()
    open(path, "w").write(t.split(a)[0] + a + "\n" + md + "\n" + b + t.split(b)[1])


def list_mast():
    from astroquery.mast import Observations
    t = Observations.query_criteria(objectname="K2-18", radius="0.01 deg", obs_collection="JWST")
    t["proposal_id", "instrument_name", "filters", "t_min", "t_obs_release"].pprint(max_lines=-1, max_width=-1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="*")
    p.add_argument("--scoreboard", action="store_true")
    p.add_argument("--into", help="splice the scoreboard into this markdown file")
    p.add_argument("--inflate", type=float, default=1.0)
    p.add_argument("--list-mast", action="store_true")
    a = p.parse_args()
    if a.list_mast:
        list_mast()
    elif a.scoreboard:
        md = scoreboard(a.files)
        splice(a.into, md) if a.into else print(md)
    elif a.files:
        wl, d, e = load(a.files[0])
        for n, dd, ee, s in band_table(wl, d, e, a.inflate):
            print(f"{n:10s} {'' if dd is None else f'{dd:8.1f} +/- {ee:.1f} ppm':22s} {s}")
    else:
        p.print_help()
