# MELODIES MONET Pairing Guide

**Contact:** liam.thompson@utah.edu

- Please do not hesitate to reach out.

# 1. How to run from scratch

- I recommend creating a new environment EVEN if you are an existing MELODIES MONET user

```bash
conda create --name melodies-monet python=3.11
conda activate melodies-monet

conda install -y -c conda-forge pyyaml pandas=2 monet monetio "netcdf4<1.7" "setuptools<70" "dask>=2024.2.1" wrf-python "cartopy=0.24" metpy windrose statannotations typer pooch jupyterlab

conda remove --force-remove -y monetio

git clone -b asia_aq_cs https://github.com/L12D2/mm_uxarray.git

git clone https://github.com/L12D2/monetio_uxarray.git

pip install --no-deps -e ./monetio_uxarray -e ./mm_uxarray

python -c "import monetio, melodies_monet; print(monetio.__file__); print(melodies_monet.__file__)"

```

- This installs the asia_aq_cs branch of my MELODIES MONET work: https://github.com/L12D2/mm_uxarray/tree/asia_aq_cs
- `-e` installs an editable version of my branch to your own environment
  - Why use `-e`?
    - As of July 31, 2026, this code has not been PR’d by the MELODIES MONET team. By using this branch, you have access to all the features and updates I made in Summer 2026. `-e` will allow you to scale this existing code to meet your needs as ingesting PRs can take considerable time.

---

# 2. How to pair AFTER Step 1

At this step, **all the files you will need** can be located here for ease of viewing and in-depth documentation of what each file does:

https://github.com/L12D2/backup_hcho_asiaaq_-_more/tree/main/hcho_cs/batch_scripts

**https://github.com/L12D2/backup_hcho_asiaaq_-_more/tree/main/hcho_cs/batch_scripts** **IS NOT A MELODIES MONET ENVIRONMENT.**

It is simply where documented copies to run pairing are stored. You can download them directly and place them in a folder of your choice within the MELODIES MONET environment you created in Step 1. Alternatively, just work in the batch_scripts file path on the asia_aq_cs branch and refer to the following files that you need to run pairing. 

You can also find copies of them in the `asia_aq_cs` branch and use them directly there.

> **NOTE:** Documentation for those files **ONLY EXISTS HERE**:

https://github.com/L12D2/backup_hcho_asiaaq_-_more/tree/main/hcho_cs/batch_scripts

> **DO NOT FORK:**

https://github.com/L12D2/backup_hcho_asiaaq_-_more/tree/main/hcho_cs/batch_scripts

## To run pairing for TEMPO

You need these files:

1. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/control_tempo_native.yaml
2. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tempo_native.py
3. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/submit_pair_tempo_native.sh
4. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/mm_paths.py

## To run pairing for TROPOMI

You need these files:

1. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tropomi_native.py
2. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/submit_pair_tropomi_native.sh
3. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/mm_paths.py
4. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/control_tempo_native.yaml
5. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tempo_native.py

Either keep these in the `batch_scripts` directory or move them to fit your own organization method.

**THE IMPORTANT PIECE IS THAT THE MELODIES MONET ENVIRONMENT YOU CREATED IN STEP 1 MUST BE ACTIVATED.**

---

# 3. Run

In your terminal:

```bash
module load conda/latest
conda activate melodies-monet
```

`cd` to where you have these files located.

## To run pairing for TEMPO

You need these files:

1. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/control_tempo_native.yaml
2. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tempo_native.py
3. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/submit_pair_tempo_native.sh
4. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/mm_paths.py

## To run pairing for TROPOMI

You need these files:

1. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tropomi_native.py
2. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/submit_pair_tropomi_native.sh
3. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/mm_paths.py
4. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/control_tempo_native.yaml
5. https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/hcho_cs/batch_scripts/pair_tempo_native.py

Once you are in that folder, copy and paste the block below:

**TEMPO** 
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

**TROPOMI** 
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

- In the submit_pair_tempo_native.sh and submit_pair_tropomi_native.sh files make sure to **change cd /glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/hcho_ben_gaubert_cs/batch_scripts to YOUR own directory**.
- In mm_paths.py **change ROOT = os.environ.get("MM_OUTPUT_ROOT", "/glade/work/lcthompson/mm_output_v2")** to directory of your choice
- Each qsub submits a 30-element job array — one element per day of June 2024, 6 running at a time. As written, the TEMPO block submits 240 jobs and the TROPOMI block submits 480. Add -J 1-1 to the qsub line for a single-day test first. The idea is **1 job for 1 day of pairing for 1 satellite product.**

---

# 4. Additional documentation

To view additional loops you can run, see:

https://github.com/L12D2/backup_hcho_asiaaq_-_more/blob/main/submit_job_native_mod_grid.md

MELODIES MONET Read the Docs (plotting):

https://melodies-monet.readthedocs.io/en/develop/

In-depth documentation for pairing using the `asia_aq_cs` branch:

https://github.com/L12D2/backup_hcho_asiaaq_-_more
