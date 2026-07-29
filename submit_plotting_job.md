# Plotting 
python make controls.py

# v2 conservative TEMPO — model space
for RUN in nonbiog_cons biog_cons grapes_cons mxcat_cons; do
  for ONLY in grp1 grp5 grp6 grp7 grp8; do          # <-- match your master's actual group names
    qsub -N pc_${RUN}_${ONLY} -o pc_${RUN}_${ONLY}.log \
      -l select=1:ncpus=1:mem=48GB -l walltime=02:00:00 \
      -v MM_CONTROL=$PWD/control_${RUN}.yaml,PLOT_GRID=model,PLOT_ONLY=$ONLY \
      submit_plot_sat.sh
  done
done

# v2 conservative TROPOMI — model space
for RUN in nonbiog_tropomi_cons biog_tropomi_cons grapes_tropomi_cons mxcat_tropomi_cons; do
  for ONLY in grp1 grp5 grp6 grp7 grp8; do
    qsub -N pc_${RUN}_${ONLY} -o pc_${RUN}_${ONLY}.log \
      -l select=1:ncpus=1:mem=48GB -l walltime=02:00:00 \
      -v MM_CONTROL=$PWD/control_${RUN}.yaml,PLOT_GRID=model,PLOT_ONLY=$ONLY \
      submit_plot_sat.sh
  done
done

