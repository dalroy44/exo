# K2-18 b Biosignature Project Plan

Goal: constrain CH4, CO2, H2O, NH3, CO, DMS, DMDS in K2-18 b from public JWST data (NIRISS, NIRSpec, MIRI) with honest uncertainties. Output is limits or detections, not a claim of life.

## Phases
1. **Setup and inventory**: repo, env, `quicklook.py --list-mast`, fill `data/manifest.csv`, snapshot NASA Exoplanet Archive parameters.
2. **First pass**: published spectra as CSV (`wavelength_um,depth_ppm,err_ppm`); run quicklook per instrument and combined, with/without error inflation.
3. **Independent reduction**: JWST pipeline + Eureka!/exoTEDRF, per-bin transit fits, at least two reduction choices; compare to published.
4. **Retrieval**: free chemistry (petitRADTRANS/POSEIDON/TauREx + dynesty/MultiNest). Baseline H2O+CH4+CO2, add NH3, CO, DMS, DMDS, CS2 one at a time, Bayes factors. Test T-profile, clouds, stellar contamination.
5. **Validation**: injection/recovery, null tests (scrambled/shifted bands), second retrieval code cross-check.
6. **Write-up**: paper, public release with DOI, preprint.

Pick one primary angle after Phase 3: independent end-to-end reduction; joint 3-instrument fit with offsets; systematic DMS/DMDS vs alternatives; newly released observations.

## Evaluation rules (fixed before seeing final results)
- Detected only if Bayes factor is decisive under several model setups.
- Must appear across independent reductions and, where possible, instruments.
- CH4 and DMS overlap at 3.3-3.4 um; that region alone cannot establish DMS.
- Report credible intervals; say "consistent with" / "not ruled out", never "evidence of life".
- State which abiotic explanations the data can and cannot exclude.

## Risks
Correlated noise (inflate errors, report effect); model dependence (multiple model families, report spread); reduction disagreements (document); scope creep (one claim per paper); compute (coarse bins, few live points first); moving target (weekly check).

## Success
Reproducible spectra and retrievals from a clean env; validated false-alarm rates per gas; clear statement of what the data do and don't support; public release and preprint.

## Weekly check (automated)
GitHub Actions, Mondays 03:30 UTC: MAST, NASA Exoplanet Archive, arXiv -> `reports/`. Heavy work (reductions, retrievals) runs locally/cluster.

Defaults chosen for the open decisions (change freely): all three checks; committed report file; Mondays 03:30 UTC; quicklook re-run on new spectra NOT automated; repo visibility is your call (public = unlimited free minutes).
