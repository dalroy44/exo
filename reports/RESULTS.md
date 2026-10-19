# What the quick-look results mean

Commentary written 2026-10-19. The scoreboard table below is regenerated on every quick-look run; the text around it is not, so recheck it after new data arrive.

## The one-minute version

```
 Is there evidence of life on K2-18 b in this data?        NO
 Is there a solid detection of any single gas here?         NOT YET
 Is DMS (the "life gas") detected?                          NO  (best case 2.5 sigma, and it varies by pipeline)
 Is CH4 (methane) there?                                    POSSIBLE; the hint depends on the pipeline
```

This is a first-pass screen, not a retrieval. It can only say "worth a closer look" or "nothing here".

## How to read the numbers

Each line in the report is `band   excess +/- error   N sigma`. It asks: *is the signal inside this gas's wavelength window higher than the nearby baseline?*

| sigma | plain meaning |
|---|---|
| under 1 | noise |
| 1 to 2 | nothing to see; happens by chance all the time |
| 2 to 3 | a hint; needs confirming; do not quote as a finding |
| 3 to 5 | interesting; must survive other pipelines and models |
| 5+ | the usual bar for a detection |

A **negative** sigma means the window sits *below* the baseline. Absorption by a gas raises the apparent planet size, so a dip is noise or a baseline problem, not a gas.

## Scoreboard (auto-generated)

<!-- scoreboard:start -->
<!-- scoreboard:end -->

## What stands out

1. **Methane is the only gas with a repeated hint, at 3.3 um.** Five of nine spectra reach 2 sigma or more, but the exoTEDRF reduction of the same data gives about zero. When the answer depends on who reduced the data, the detection is not secure yet.
2. **DMS fails at 3.4 um.** Every spectrum is below 1.5 sigma. Methane also absorbs there, so even a bump would not prove DMS.
3. **DMS at 6.9 um is the one to watch, not to celebrate.** Spectra of the *same* MIRI observation give 0.8 to 2.5 sigma depending on the pipeline. Nobody reaches 3. This matches the published disagreement: one team sees a hint, others see insufficient evidence.
4. **NH3 at 10.5 um (up to 3.1 sigma) is probably an edge effect.** It sits at the long-wavelength end of MIRI where errors are large and the baseline exists on one side only. Treat as unverified.
5. **CO2 and H2O are weakly positive everywhere.** Consistent sign across pipelines is mildly encouraging, but the values are too small to call.

## Why you should not over-read this

- **Spectra are not independent.** Several rows are the same telescope data reduced by different teams, so ten spectra is not ten confirmations.
- **Crude method.** Flat local baseline, no real molecular line shapes, no stellar-contamination model, and the NRS1/NRS2 detector offset is ignored.
- **Approximate bands.** MIRI band centres (6.3, 6.9, 7.7, 10.5 um) are from memory and need checking against line lists.
- **Averaged errors.** Where a file has asymmetric errors the two sides are averaged.

## What would change the picture

| to believe a gas is real | what we need |
|---|---|
| same sign and size in every pipeline | independent reduction (Phase 3) |
| holds under different model assumptions | retrieval with Bayes factors (Phase 4) |
| not caused by clouds, haze or star spots | model-dependence tests (Phase 4) |
| the method does not cry wolf | injection and null tests (Phase 5) |

## Next step

Phase 4: a free-chemistry retrieval on a joint NIRISS + NIRSpec + MIRI set, adding each candidate gas one at a time and comparing Bayes factors.
