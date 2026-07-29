#!/bin/bash -l

#PBS -N plot_air_data
#PBS -A P19010000
#PBS -q casper
#PBS -l select=1:ncpus=4:mem=80GB
#PBS -l walltime=01:00:00
#PBS -j oe
#PBS -o air_plot.log

# One-time air plot job 

cd /glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs

module load conda
conda activate melodies-monet   

: "${YMD:?set -v YMD=YYYYMMDD}"
: "${SAT:?set -v SAT=no2|hcho|co}"
export REGRID_TARGET="${REGRID_TARGET:-swath}"
export PAIR_MODEL="${PAIR_MODEL:-}"        # unset pair all models in the control

echo "== air_plot_driver: YMD=$YMD SAT=$SAT PAIR_MODEL=${PAIR_MODEL:-<all>} REGRID_TARGET=$REGRID_TARGET =="

python air_plot_driver.py

# # # swath pairing loop 
# OUT=/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output
# MODELS="cam-chem-se-era5 cam-chem-se-merra2"

# for YMD in 20240202 20240206 20240207 20240211 20240215; do
#   for m in $MODELS; do
#     for SAT in no2 hcho co; do
#       qsub -N sw_${SAT}_${m#cam-chem-se-}_${YMD} \
#            -o ${OUT}/sw_${SAT}_${m#cam-chem-se-}_${YMD}.log \
#            -l select=1:ncpus=1:mem=150GB \
#            -l walltime=01:00:00 \
#            -v YMD=${YMD},SAT=${SAT},PAIR_MODEL=${m},REGRID_TARGET=swath \
#            submit_air_plot.sh
#     done
#   done
# done

# OUT=/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output
# MODELS="cam-chem-se-era5 cam-chem-se-merra2"

# for YMD in 20240211; do
#   for m in $MODELS; do
#     for SAT in no2 hcho co; do
#       qsub -N sw_${SAT}_${m#cam-chem-se-}_${YMD} \
#            -o ${OUT}/sw_${SAT}_${m#cam-chem-se-}_${YMD}.log \
#            -l select=1:ncpus=1:mem=350GB \
#            -l walltime=01:00:00 \
#            -v YMD=${YMD},SAT=${SAT},PAIR_MODEL=${m},REGRID_TARGET=swath \
#            submit_air_plot.sh
#     done
#   done
# done
