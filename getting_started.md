# Getting started: conservative satellite pairing onto the model mesh

Pair TEMPO or TROPOMI L2 against the CESM-SE unstructured mesh using true area-weighted (conservative) regridding, with the **satellite regridded onto the model mesh**.

> `REGRID_TARGET=model` puts the satellite on the model mesh.
> `REGRID_TARGET=swath` does the opposite—the model is sampled onto the native L2 satellite pixels. Pick deliberately; they answer different questions.

Individual files that you may need can be found in `hcho_cs/batch_scripts/`.

## The script

`pair_daily_sat.py` pairs one day per invocation and is driven entirely by environment variables. Its base control is `../control_tempo_l2_hcho_cesm_se.yaml`; per-run model paths, mesh files, and output directories come from the `RUNS` dict at the top of the script.

| Variable        | Default        | Meaning                                                               |
| --------------- | -------------- | --------------------------------------------------------------------- |
| `RUN`           | `nonbiog`      | Emissions run: `nonbiog`, `biog`, `grapes`, `mxcat`                   |
| `YMD`           | **required**   | Day to pair, e.g. `20240608`                                          |
| `REGRID_TARGET` | `model`        | `model` = onto the unstructured mesh; `swath` = onto native L2 pixels |
| `REGRID_METHOD` | `conservative` | `conservative` or `radius_mean`                                       |
| `OBS_GROUP`     | all            | Restrict to one product, e.g. `tempo_l2_hcho`                         |

Model-space conservative is the **default**, so the minimal invocation is just `RUN` + `YMD`. The examples below set the variables explicitly for clarity.

## Step 1 — Smoke test one day interactively

Confirm the mesh, SCRIP file, and granule glob all resolve before committing a month of queue time:

```bash
cd hcho_cs/batch_scripts
module load conda && conda activate melodies-monet

export RUN=nonbiog
export YMD=20240608
export REGRID_TARGET=model
export REGRID_METHOD=conservative
export OBS_GROUP=tempo_l2_hcho
export HOURS='1[5-7]'          # only 15–17 UTC granules: minutes, not hours

python pair_daily_sat.py
```

`HOURS` is the fastest way to confirm the pipeline works end to end. Drop it for a real run.

## Step 2 — One day as a batch job

```bash
qsub -N pd_nonbiog_0608 -o pd_nonbiog_0608.log \
     -v RUN=nonbiog,YMD=20240608,REGRID_TARGET=model,REGRID_METHOD=conservative \
     submit_pair_day.sh
```

`submit_pair_day.sh` requests `1:ncpus=1:mem=150GB` with 6 h walltime, and asserts `YMD` is set so an unset value cannot silently become `20240600`.

> **Note:** No spaces in the `-v` list. `-v A=1, B=2` silently drops `B`.

## Step 3 — A full month

`submit_pair_month.sh` is a PBS job array, one element per June day (`#PBS -J 1-30%6`, six concurrent), deriving `YMD` from `PBS_ARRAY_INDEX`:

```bash
for RUN in nonbiog biog grapes mxcat; do
  qsub -N ptm_${RUN} -o ptm_${RUN}.log \
       -v RUN=$RUN,REGRID_TARGET=model,REGRID_METHOD=conservative \
       submit_pair_month.sh
done
```

Split by product when memory is tight, one product per job:

```bash
for RUN in nonbiog biog grapes mxcat; do
  for P in tempo_l2_no2 tempo_l2_hcho; do
    qsub -N ptm_${RUN}_${P} -o ptm_${RUN}_${P}.log \
         -v RUN=$RUN,OBS_GROUP=$P,REGRID_TARGET=model,REGRID_METHOD=conservative \
         submit_pair_month.sh
  done
done
```

Final sizing likely needs requests on orders of 250Gb+. Though, 3hr walltime is sufficient per day. 

> **Note:** `-J 1-30%6` needs a real range—a degenerate `-J n-n` is rejected by `qsub`.

## Step 4 — Audit before plotting

Conservative jobs killed partway by OOM leave netCDFs that look fine but are truncated. `check_work_mm.py` exits non-zero on any failure, so chain it:

```bash
python check_work_mm.py "$OUT/202406*_tempo_l2_hcho_cam-chem-se*.nc4" --days 30 \
  && qsub -v RUN=nonbiog,PLOT_GRID=model submit_plot_sat.sh
```

## Step 5 — Plot

```bash
python make_controls.py nonbiog

export MM_CONTROL=$PWD/control_nonbiog.yaml
export PLOT_GRID=model
export PLOT_ONLY=grp6

qsub -N p_nonbiog_grp6 -o p_nonbiog_grp6.log \
     -l select=1:ncpus=1:mem=48GB -V submit_plot_sat.sh
```

`PLOT_GRID=model` selects the model-mesh paired files; `PLOT_ONLY` restricts to one plot group so a failure in one does not cost the whole set.

## Where the output lands

`mm_paths.py` defines the layout:

```text
$MM_OUTPUT_ROOT/<run-slug>/tempo/model/
```

A model-space TEMPO run for `nonbiog` writes to:

```text
<root>/nonbiog_refera5_dust/tempo/model/
```

Add a run by adding one entry to `RUN_SLUG` in `mm_paths.py`; the pairing scripts import `paired_dir` from there so the scheme is defined in exactly one place.

## Optional QA screens

```bash
export CLOUD_FILTER=on    # cloud fraction screen (NO2/HCHO only; CO has none)
export SZA_FILTER=on      # solar zenith angle screen
export SAVE_VARS=on       # also save SZA, cloud, QA and AMF diagnostics
```

The base quality flag is always applied. `filter_tag` / `save_suffix` in `mm_paths.py` encode the combination into the output filename as `cld{0,1}sza{0,1}`, so a screening matrix can be produced without editing any control file.

---


