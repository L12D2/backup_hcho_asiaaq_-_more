# MELODIES MONET Pairing Guide

---

# Contact
Please do not hesitate to reach out.

**Liam Thompson**  
Email: <liam.thompson@utah.edu>

## 1. Create a New Environment

I recommend creating a new environment even if you are an existing MELODIES MONET user.

```bash
conda create --name melodies-monet python=3.11
conda activate melodies-monet

conda install -y -c conda-forge pyyaml pandas=2 monet monetio \
  "netcdf4<1.7" "setuptools<70" "dask>=2024.2.1" wrf-python \
  "cartopy=0.24" metpy windrose statannotations \
  typer pooch jupyterlab

pip install --no-deps -e \
https://github.com/L12D2/mm_uxarray/archive/asia_aq_cs.zip
```

### Why use `-e`?

As of July 31, 2026, this code has not been merged into the official MELODIES MONET repository. Installing this branch gives you access to the Summer 2026 features while allowing you to modify the package locally.

---

## 2. Obtain the Pairing Scripts

Documentation and downloadable copies of the scripts are available here:

<https://github.com/L12D2/backup_hcho_asiaaq_-_more/tree/main/hcho_cs/batch_scripts>

> **Note**
> This repository is **not** a MELODIES MONET environment. It only stores documented copies of the pairing scripts.

Do **not** fork this repository.

### TEMPO

Required files:

1. `control_tempo_native.yaml`
2. `pair_tempo_native.py`
3. `submit_pair_tempo_native.sh`

### TROPOMI

Required files:

1. `pair_tropomi_native.py`
2. `submit_pair_tropomi_native.sh`
