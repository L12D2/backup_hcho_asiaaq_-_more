# ASIA-AQ / MELODIES-MONET Reference

**As of July 29, 2026**

## Repositories

### MELODIES-MONET

Use the **`asia_aq_cs`** branch.

https://github.com/L12D2/mm_uxarray/tree/asia_aq_cs/docs/examples/ungridded_support/unstructured_grid_read_uxarray/hcho_ben_gaubert_cs

### MONETIO

https://github.com/L12D2/monetio_uxarray

---

The base quality flag is applied by default, unless `NO_QA=on`.

# TEMPO

## Model mesh (filtered)

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N ts_${RUN}_${P}_cld1sza1 -o ts_${RUN}_${P}_cld1sza1.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=model,CLOUD_FILTER=on,SZA_FILTER=on \
      submit_pair_tempo_native.sh
  done
done
```

---

## Native swath (filtered)

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N ts_${RUN}_${P}_cld1sza1 -o ts_${RUN}_${P}_cld1sza1.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,CLOUD_FILTER=on,SZA_FILTER=on \
      submit_pair_tempo_native.sh
  done
done
```

---

## Native swath (raw + diagnostics)

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N ts_${RUN}_${P}_cld0sza0sv -o ts_${RUN}_${P}_cld0sza0sv.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,NO_QA=on,SAVE_DIAG=on \
      submit_pair_tempo_native.sh
  done
done
```

---

## Native swath (SZA only)

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N ts_${RUN}_${P}_cld0sza1 -o ts_${RUN}_${P}_cld0sza1.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,SZA_FILTER=on \
      submit_pair_tempo_native.sh
  done
done
```

---

## Model mesh (SZA only)

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N tm_${RUN}_${P}_cld0sza1 -o tm_${RUN}_${P}_cld0sza1.log \
      -l select=1:ncpus=8:mem=400GB -l walltime=04:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=model,SZA_FILTER=on \
      submit_pair_tempo_native.sh
  done
done
```

---

# TROPOMI

## NO₂ / HCHO (filtered)

Runs both **model** and **swath** targets.

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in no2 hcho; do
    for TGT in model swath; do
      qsub -N tr_${RUN}_${P}_${TGT}_cld1sza1 -o tr_${RUN}_${P}_${TGT}_cld1sza1.log \
        -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
        -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,CLOUD_FILTER=on,SZA_FILTER=on \
        submit_pair_tropomi_native.sh
    done
  done
done
```

---

## CO (SZA only)

Runs both **model** and **swath** targets.

```bash
for RUN in mxcat grapes biog nonbiog; do
  for TGT in model swath; do
    qsub -N tr_${RUN}_co_${TGT}_cld0sza1 -o tr_${RUN}_co_${TGT}_cld0sza1.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TROPOMI_PRODUCTS=co,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,SZA_FILTER=on \
      submit_pair_tropomi_native.sh
  done
done
```

---

## Raw swath + diagnostics

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in no2 hcho co; do
    qsub -N tr_${RUN}_${P}_swath_cld0sza0sv -o tr_${RUN}_${P}_swath_cld0sza0sv.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,NO_QA=on,SAVE_DIAG=on \
      submit_pair_tropomi_native.sh
  done
done
```

---

## NO₂ / HCHO (SZA only)

Runs both **model** and **swath** targets.

```bash
for RUN in mxcat grapes biog nonbiog; do
  for P in no2 hcho; do
    for TGT in model swath; do
      qsub -N tr_${RUN}_${P}_${TGT}_cld0sza1 -o tr_${RUN}_${P}_${TGT}_cld0sza1.log \
        -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
        -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,SZA_FILTER=on \
        submit_pair_tropomi_native.sh
    done
  done
done
```

---

# Filename conventions

### City products

```text
{city}_{restag}_{method}_{ymd}_{obs}_{model}_{target}.nc4
```

### Full model mesh products

```text
model_{method}_{ymd}_{obs}_{model}.nc4
```

---

# Environment variables

| Variable           | Values                               |
| ------------------ | ------------------------------------ |
| `RUN`              | `mxcat`, `grapes`, `biog`, `nonbiog` |
| `CITY`             | City name (city products only)       |
| `REGRID_TARGET`    | `model`, `swath`, `obs`              |
| `REGRID_METHOD`    | `conservative`                       |
| `TEMPO_PRODUCTS`   | `hcho`, `no2`                        |
| `TROPOMI_PRODUCTS` | `no2`, `hcho`, `co`                  |
| `OBS_GRID_RES`     | TEMPO: `0.03`, TROPOMI: `0.05`       |
| `YMD`              | Derived from PBS array index         |
