# ASIA-AQ satellite + aircraft evaluation with MELODIES MONET

Working code, control files and notebooks for evaluating CESM-SE / MUSICA against
TROPOMI and TEMPO satellite retrievals, DC-8 aircraft data, and Asian surface
networks, using [MELODIES MONET](https://github.com/NCAR/MELODIES-MONET).

This is the campaign-specific half of the work. The generic capability —
unstructured mesh support, conservative satellite regridding, along-track
pairing — was contributed upstream to MELODIES MONET; see
[Upstream features](#upstream-features).

> **No data is committed here.** All `.nc`, `.nc4`, `.csv`, `.ict` and figure
> output is excluded by `.gitignore`. Paths in the control files point at NCAR
> GLADE and will need repointing. See [Data provenance and contact](#data-provenance-and-contact).

---

## Contents

```
asiaaq_cs/                          ASIA-AQ campaign (Feb-Mar 2024)
├── pair_tropomi_day.py             TROPOMI pairing driver: 1 job = 1 day x 1 model x 1 product
├── submit_pair_tropomi_day.sh      its PBS submission
├── air_plot_driver.py              aircraft plotting driver
├── plot_dc8_overlay.ipynb          DC-8 / satellite co-location figures
└── asiaaq_cs_06082026/
    ├── control_air_full_camp_cesm-se.yaml    full-campaign aircraft control
    ├── control_sfc_full_camp_cesm-se.yaml    full-campaign surface control
    ├── control_airnow_cesm-se_20240101.yaml
    ├── output/
    │   ├── pair/control_tropomi_2024020*.yaml    15 per-day TROPOMI controls
    │   ├── pair/control_swath_{co,hcho,no2}_*.yaml   native-swath controls
    │   ├── dc8_yaml/, dc8_plot_yaml/             per-flight pairing + plotting
    │   └── montage_dc8.py
    └── write_met_data/
        ├── thai_to_airnow.ipynb          Thai network -> AirNow format
        ├── philippines_to_airnow.ipynb   Philippine network -> AirNow format
        ├── clean_airnow_files.ipynb       QC / gap handling
        ├── dc8_data.ipynb                DC-8 merge assembly
        ├── inspect_met_data.ipynb, qc_inspect_met_data.ipynb, merge.ipynb
        ├── batch_scripts/                per-flight pairing
        └── full_camp/                    whole-campaign drivers

jun_zhang_track/                    along-track (1x) CESM-SE vs DC-8
├── asia_aq_cs_jz_06152026.ipynb
├── control_jz_dc8_cesm.yaml
└── batch_scripts/

poster_figs/                        figure notebooks
├── plot_raw_sat.ipynb              raw L2 swaths
├── mesh_overlay.ipynb              unstructured mesh rendering
└── dc8_tropomi_overlay.ipynb       DC-8 track over TROPOMI
```

---

## 1. Surface obs: Asian networks -> AirNow format

MELODIES MONET reads surface point data through its AirNow reader, so the Thai
and Philippine national monitoring exports are reshaped to match that schema
rather than given a new reader. A control can then set `use_airnow: true` and
treat them like any other surface network.

- `write_met_data/thai_to_airnow.ipynb`
- `write_met_data/philippines_to_airnow.ipynb`

Supporting: `clean_airnow_files.ipynb` (QC, gaps), `inspect_met_data.ipynb` and
`qc_inspect_met_data.ipynb` (pre-pairing sanity checks), `merge.ipynb`
(combining networks into one obs file).

## 2. Aircraft obs: DC-8 merges

`write_met_data/dc8_data.ipynb` assembles the 1-second DC-8 merge from campaign
ICARTT (`.ict`) files. Two things that bite:

- **Limit-of-detection flags.** ICARTT headers declare `ULOD_FLAG: -777777` and
  `LLOD_FLAG: -888888`. These must become NaN or they dominate every statistic.
  Handle it with `nan_value` in the obs YAML block rather than in preprocessing.
- **Longitude convention.** DC-8 longitude is 0-360; the model mesh and the
  retrievals are -180..180. Everything downstream compares in -180..180.

## 3. Satellite pairing

### How the conservative regridding works

Genuinely area-weighted, not nearest-neighbour:

1. Build the source mesh from **L2 pixel corner bounds**
   (`uxarray_util.uxgrid_from_corner_bounds`) so each retrieval pixel is a real
   polygon.
2. Build the target from the model SCRIP file, **depadded** first
   (`clean_uxgrid_from_scrip`). SCRIP pads every cell to `grid_corners` by
   repeating corners, and ESMF refuses to build conservative weights on those
   degenerate polygons.
3. Generate ESMF/xregrid area-overlap weights and apply them.

Weights are rebuilt **per granule** because the swath moves — they cannot be
cached the way a fixed model-to-model regrid can.

Two things make it survivable at scale:

- **Crop to extent + mesh subset.** Building weights against a full 174k-face
  mesh per granule is what caused OOM. Cropping the granule to the model extent
  and subsetting the mesh to the granule footprint (`subset_model_source`) fixes it.
- **Streaming concat.** Accumulating granules pairwise is O(n^2) in memory.

Run **serial**. xregrid's Dask-parallel weight generation is broken for
unstructured sources — it chunks with `isel(n_face=slice(...))`, which uxarray's
`Grid.isel` rejects. There is an opt-in shim behind `MM_XREGRID_PARALLEL`, but
serial is the reliable configuration.

> **The 2x weight bug.** The installed xregrid's conservative weights row-sum to
> ~2 instead of 1, silently doubling every conservative product.
> `regrid_util._coverage_normalize` corrects it. Any conservative output produced
> before that fix is 2x too high and must be regenerated.

### Job granularity

TROPOMI pairing OOMs at 350 GB if both models load at once. The working
decomposition is **one job = one day x one model x one product**:

```bash
for d in $(seq -w 1 15); do
  for m in merra2 era5; do
    for p in tropomi_l2_no2 tropomi_l2_hcho tropomi_l2_co; do
      qsub -N p_${p#tropomi_l2_}_${m}_${d} \
           -v YMD=202402${d},PAIR_MODEL=${m},PAIR_OBS=${p} \
           -l select=1:ncpus=8:mem=100GB pair_tropomi_day.pbs
    done
  done
done
```

`pair_tropomi_day.py` prunes `control_dict["obs"]` and `["model"]` to a single
entry each from `PAIR_OBS`/`PAIR_MODEL`, then prunes each model's `mapping` to
the retained obs. That last step matters: `pair_data` iterates
`mod.mapping.keys()` and indexes `self.obs[key]`, so a mapping entry for a
dropped obs raises a `KeyError` that surfaces as the confusing
`'NoneType' object has no attribute 'to_dataframe'`.

Output names are `<prefix>_<obs>_<model>.nc4`, so day x product x model are all
encoded and jobs never collide.

### PBS gotchas

- `-J n-n` is rejected — a degenerate array range is an error, not a no-op.
- `-v` lists must have **no spaces**: `-v A=1, B=2` silently drops `B`.
- Memory scales with the target mesh, not the granule: mxcat ~150 GB,
  ne0CONUS ne30x8 200-400 GB for full-mesh runs.

### QA and screening

Filter **before** regridding via `data_proc.filter_dict` — far more robust than
post-hoc masking. Two reader keys are easy to get wrong:

| correct | not |
|---|---|
| `quality_flag_max` | `main_data_quality_flag_max` |
| `qa_thresh_min` | `qa_min` |

Cloud and solar-zenith screening are env-gated (`CLOUD_FILTER`, `SZA_FILTER`)
and tagged into the output path as `cld{0,1}sza{0,1}`, so a screening matrix can
be generated without editing controls. Per-product cloud variables differ: NO2
and HCHO use `cloud_fraction_crb`; **CO has none**.

Do **not** clip negative retrievals before averaging — negatives are part of the
retrieval noise distribution and clipping biases the mean high.

## 4. Known data issues

- **TROPOMI CO striping** is a retrieval artifact in the H1 product, not a
  pairing bug (it correlates r~+0.92 with observed texture). Pair the
  `_corrected` variable instead.
- **Diurnal plots from polar orbiters** are close to meaningless — TROPOMI
  samples a location roughly once per day. MELODIES MONET warns when a diurnal
  cycle has <=3 distinct hours.
- **MPAS output has no hybrid coefficients** (`hyam`/`hybm`/`P0`), so
  `pres_pa_mid` and `dz_m` cannot be derived. Surface comparisons are fine;
  anything pressure-dependent is not.

## 5. Output layout

`mm_paths.py` writes into `<run-slug>/<instrument>/<gridtype>/`, e.g.
`musicav0_conus_gra2pesv2/tempo_no2/model/`. Slugs identify the model run so
several runs share one master control via `make_controls.py`, with pair
relabelling enabling cross-run overlay plots.

---

## Upstream features

The generic capability this work depends on was contributed to MELODIES MONET:

| Area | What it added |
|---|---|
| Unstructured mesh + regrid engine | `util/uxarray_util.py`, `util/regrid_util.regrid()`, `plots/uxarray_render.py`, unstructured model loading for `cesm_se` / `mpas` |
| Satellite L2 conservative pairing | generic TROPOMI NO2/HCHO/CO pairing, TEMPO rework with scattering weights, native-swath plots |
| Along-track pairing | `util/track_pairing.py`, the `is_track` model option |
| obs2obs | `util/obs2obs_util.py`, multi-observation comparison after pairing |
| Plot + util fixes | wind barbs on unstructured meshes, solar-hour reduction, montage, regulatory extraction, longitude-wrap region selection |

Also in [monetio](https://github.com/noaa-oar-arl/monetio): the unstructured CAM
reader (`_cam_unstructured`) and propagating min/max QA screens for the
TEMPO/TROPOMI L2 readers.

## Data provenance and contact

Raw inputs are **not** in this repository. The Philippine (~2.7 GB) and Thai
(~134 MB) national network exports, the campaign ICARTT files, and the model
history archives all live on NCAR GLADE. The converted products are regenerable
from them.

Consequence worth stating plainly: `thai_to_airnow.ipynb` and
`philippines_to_airnow.ipynb` **cannot be re-run from a fresh clone** without
those inputs. They are kept here as the authoritative record of the conversion
logic.

For access to the raw national network data, the campaign archives, or questions
about the ASIA-AQ evaluation setup, contact **gaubert@ucar.edu**.

## Environment

Built against the `melodies-monet` conda environment on NCAR Casper, plus
`uxarray` and `xregrid`, which are optional MELODIES MONET dependencies:

```bash
pip install melodies-monet[unstructured]
```
