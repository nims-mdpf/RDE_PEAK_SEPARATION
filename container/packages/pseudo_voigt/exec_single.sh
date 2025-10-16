#!/bin/bash

#$ -S /bin/sh
#$ -cwd
#$ -V
#$ -q all.q
#$ -pe OpenMP 16

export LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}
export OMP_NUM_THREADS=$NSLOTS

date

if [ $# != 1 ]; then
    echo "Usage: $0 <csv_file>"
    exit 1
elif [ ! -s "$1" ]; then
    echo "Error. No data in $1"
    exit 1
fi

SCRIPT_DIR=$(cd $(dirname $0); pwd)
echo ${SCRIPT_DIR}

# If there is recipe.txt in $PWD, use it.
# Else, if there is recipe.txt in ${SCRIPT_DIR}, use it.
# Otherwise, not use recipe.txt.
#
# PWD_RECIPE="${PWD}/recipe.txt"
# if [ ! -f "${PWD_RECIPE}" ]; then
#     if [ -f "${SCRIPT_DIR}/recipe.txt" ]; then
#         echo "DEBUG:" "${SCRIPT_DIR}/recipe.txt" "${PWD_RECIPE}"
#         cp "${SCRIPT_DIR}/recipe.txt" "${PWD_RECIPE}"
#     fi
# fi

python3.7 ${SCRIPT_DIR}/automatic_xps_peak_separation_single.py -p "$1" >stdout.txt 2>stderr.txt

# rm -rf __pycache__

date
