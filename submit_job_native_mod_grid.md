
As of July 29, 2026: use asia_aq_cs branch 
MELODIES MONET
https://github.com/L12D2/mm_uxarray/tree/asia_aq_cs/docs/examples/ungridded_support/unstructured_grid_read_uxarray/hcho_ben_gaubert_cs 

MONETIO
https://github.com/L12D2/monetio_uxarray 

# Submit a job for tempo on the native model grid 
for RUN in mxcat grapes biog nonbiog; do
  for P in hcho no2; do
    qsub -N ts_${RUN}_${P}_cld1sza1 -o ts_${RUN}_${P}_cld1sza1.log \
      -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
      -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=model,CLOUD_FILTER=on,SZA_FILTER=on \
      submit_pair_tempo_native.sh
  done
done

# TEMPO swath, FILTERED (cld1sza1) — light, 250 is plenty
for RUN in mxcat grapes biog nonbiog; do for P in hcho no2; do
  qsub -N ts_${RUN}_${P}_cld1sza1 -o ts_${RUN}_${P}_cld1sza1.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,CLOUD_FILTER=on,SZA_FILTER=on \
    submit_pair_tempo_native.sh
done; done

# TEMPO swath, RAW + all diagnostics saved (cld0sza0sv) — the useful "raw" product
for RUN in mxcat grapes biog nonbiog; do for P in hcho no2; do
  qsub -N ts_${RUN}_${P}_cld0sza0sv -o ts_${RUN}_${P}_cld0sza0sv.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,NO_QA=on,SAVE_DIAG=on \
    submit_pair_tempo_native.sh
done; done

# TROPOMI no2/hcho, FILTERED (cld1sza1), model+swath
for RUN in mxcat grapes biog nonbiog; do for P in no2 hcho; do for TGT in model swath; do
  qsub -N tr_${RUN}_${P}_${TGT}_cld1sza1 -o tr_${RUN}_${P}_${TGT}_cld1sza1.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,CLOUD_FILTER=on,SZA_FILTER=on \
    submit_pair_tropomi_native.sh
done; done; done

# TROPOMI co, cld0sza1 (no cloud var), model+swath
for RUN in mxcat grapes biog nonbiog; do for TGT in model swath; do
  qsub -N tr_${RUN}_co_${TGT}_cld0sza1 -o tr_${RUN}_co_${TGT}_cld0sza1.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TROPOMI_PRODUCTS=co,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,SZA_FILTER=on \
    submit_pair_tropomi_native.sh
done; done

# TROPOMI raw swath + saved diagnostics (cld0sza0sv) 
for RUN in mxcat grapes biog nonbiog; do for P in no2 hcho co; do
  qsub -N tr_${RUN}_${P}_swath_cld0sza0sv -o tr_${RUN}_${P}_swath_cld0sza0sv.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,NO_QA=on,SAVE_DIAG=on \
    submit_pair_tropomi_native.sh
done; done   
# TEMPO swath, cld0sza1 
for RUN in mxcat grapes biog nonbiog; do for P in hcho no2; do
  qsub -N ts_${RUN}_${P}_cld0sza1 -o ts_${RUN}_${P}_cld0sza1.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=swath,SZA_FILTER=on \
    submit_pair_tempo_native.sh
done; done

# TROPOMI no2/hcho, cld0sza1, model + swath 
for RUN in mxcat grapes biog nonbiog; do for P in no2 hcho; do for TGT in model swath; do
  qsub -N tr_${RUN}_${P}_${TGT}_cld0sza1 -o tr_${RUN}_${P}_${TGT}_cld0sza1.log \
    -l select=1:ncpus=8:mem=250GB -l walltime=03:00:00 \
    -v RUN=$RUN,TROPOMI_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=$TGT,SZA_FILTER=on \
    submit_pair_tropomi_native.sh
done; done; done

# TEMPO model with no cloud filtering
for RUN in mxcat grapes biog nonbiog; do for P in hcho no2; do
  qsub -N tm_${RUN}_${P}_cld0sza1 -o tm_${RUN}_${P}_cld0sza1.log \
    -l select=1:ncpus=8:mem=400GB -l walltime=04:00:00 \
    -v RUN=$RUN,TEMPO_PRODUCTS=$P,REGRID_METHOD=conservative,REGRID_TARGET=model,SZA_FILTER=on \
    submit_pair_tempo_native.sh
done; done   
