#!/bin/bash -l
#PBS -A P19010000
#PBS -q casper
#PBS -l select=1:ncpus=8:mem=350GB
#PBS -l walltime=02:00:00
#PBS -j oe

cd /glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs

module load conda
conda activate melodies-monet
python pair_tropomi_day.py          # YMD from qsub -v

# MODELS="cam-chem-se-era5 cam-chem-se-merra2"
# PRODUCTS="tropomi_l2_no2 tropomi_l2_hcho tropomi_l2_co"   

# for d in $(seq -w 1 15); do
#   YMD=202402${d}
#   for m in $MODELS; do
#     for p in $PRODUCTS; do
#       qsub -N p_${p#tropomi_l2_}_${m}_${YMD} \
#            -v YMD=${YMD},PAIR_MODEL=${m},PAIR_OBS=${p} \
#            -l select=1:ncpus=8:mem=350GB \
#            -l walltime=02:00:00 \
#            submit_pair_tropomi_day.sh
#     done
#   done
# done


#SWATH pairing loop 
# OUT=/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output
# for YMD in 20240202 20240206 20240207 20240211 20240215; do
#   for SAT in no2 hcho co; do
#     qsub -N sw_${SAT}_${YMD} -o ${OUT}/sw_${SAT}_${YMD}.log \
#          -v YMD=${YMD},SAT=${SAT},REGRID_TARGET=swath \
#          submit_air_plot.sh
#   done
# done
