# K2-18 b biosignature check

Public JWST data, open tools, reproducible constraints on CH4, CO2, H2O, NH3, CO, DMS, DMDS. Constraints, not claims of life. Full plan: [PLAN.md](PLAN.md).

## Setup
    python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt  # pin with pip freeze once stable

## Phase 1
    python scripts/quicklook.py --list-mast          # JWST obs of K2-18 -> fill data/manifest.csv
    python scripts/quicklook.py data/published/X.csv # bands; CSV cols: wavelength_um,depth_ppm,err_ppm
                                                     # add --inflate 1.5 for error inflation

## Weekly check
`scripts/weekly_check.py` (MAST, NASA Exoplanet Archive, arXiv) runs Mondays 03:30 UTC via
`.github/workflows/weekly.yml`, writes `reports/YYYY-MM-DD.md` and `reports/state.json`, commits both.
Public repos: scheduled runs pause after 60 days of no activity (the weekly commit counts as activity).

Raw data stays out of git; record checksums in `data/manifest.csv`.
