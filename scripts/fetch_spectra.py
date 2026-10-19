"""Fetch published spectra into data/external/ (small files only; zips are read via HTTP range requests)."""
import io, os, pathlib, re, urllib.request, zipfile

OUT = pathlib.Path(__file__).parent.parent / "data" / "external"


class Remote(io.RawIOBase):
    """Seekable read-only view of a URL so zipfile can pull single members out of a huge zip."""
    def __init__(s, u):
        s.u, s.pos = u, 0
        s.n = int(urllib.request.urlopen(urllib.request.Request(u, headers={"Range": "bytes=0-0"})).headers["Content-Range"].split("/")[1])
    seekable = readable = lambda s: True
    def tell(s): return s.pos
    def seek(s, o, w=0):
        s.pos = o if w == 0 else s.pos + o if w == 1 else s.n + o
        return s.pos
    def readinto(s, b):
        end = min(s.pos + len(b) - 1, s.n - 1)
        if s.pos > end: return 0
        d = urllib.request.urlopen(urllib.request.Request(s.u, headers={"Range": f"bytes={s.pos}-{end}"})).read()
        b[:len(d)] = d; s.pos += len(d); return len(d)


def save(folder, name, data):
    d = OUT / folder; d.mkdir(parents=True, exist_ok=True)
    (d / os.path.basename(name)).write_bytes(data)  # basename only: never trust paths inside archives
    print("saved", folder, os.path.basename(name), len(data))


# Schmidt+2025, zenodo 10.5281/zenodo.14735689 (CC-BY-4.0): R100/R200 spectra only
z = zipfile.ZipFile(io.BufferedReader(Remote("https://zenodo.org/api/records/14735689/files/K2-18_reanalysis_data.zip/content"), 1 << 20))
for i in z.infolist():
    if re.search(r"/(NIRISS|NIRSpec) Spectra/.*_R(100|200)\.dat$", i.filename):
        save("schmidt2025", i.filename, z.read(i))

# Madhusudhan+2025 MIRI, https://osf.io/gmhw3/
for name, fid in (("K2-18b_miri_lrs_jexores.txt", "w8qtb"), ("K2-18b_miri_lrs_jexopipe.txt", "6pev4"), ("Readme.txt", "u3krx")):
    save("madhusudhan2025", name, urllib.request.urlopen(f"https://osf.io/download/{fid}/").read())
