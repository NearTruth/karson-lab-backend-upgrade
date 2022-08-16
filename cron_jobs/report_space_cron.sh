#!/usr/bin/env bash

# Generates the NCDU json, parses it, and reports the change
# in space consumption fom the previous time this job was run.


set -e

SPACE_MONITORING_DIRECTORY=/projects/karsanlab/space_monitoring
PARSED_DATA_DIRECTORY=parsed_data
NCDU_JSONS_DIRECTORY=ncdu_jsons
NCDU_EXPORT_REPO=git_repos/ncdu-export
KARSANLAB_BITBUCKET_REPO=git_repos/KARSANBIO-2205_space_monitoring
TRACKING_TABLE=on_going_space_report.tsv
EXCLUDE_DIRECTORY=/projects/karsanlab/.snapshot
DIRECTORY_ROOT=/projects/karsanlab/

DATE=$(date --iso-8601)

echo Started space audit at $(date -Iseconds)

cd ${SPACE_MONITORING_DIRECTORY}
eval "$(/projects/karsanlab/software/linux-x86_64-centos7/anaconda3/bin/conda shell.bash hook)"
conda activate ./env_space_monitoring
mkdir -p ${PARSED_DATA_DIRECTORY}/${DATE}
ncdu -0 -x -e -r --exclude ${EXCLUDE_DIRECTORY} -o -${DIRECTORY_ROOT}  | gzip > ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.json.gz
zcat ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.json.gz | iconv -f utf-8 -t utf-8 -c - > ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.iconv.json
python ${NCDU_EXPORT_REPO}/flatten.py --dirs array ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.iconv.json > ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.flat.json
python ${KARSANLAB_BITBUCKET_REPO}/scripts/parse_ncdu_json.py --input ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.flat.json
mv ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.flat.json.*.tsv ${PARSED_DATA_DIRECTORY}/${DATE}

# Get previous run and compare
PREVIOUS_DATE=$(ls -ltr ${PARSED_DATA_DIRECTORY} | egrep '^d' | tail -n2 | head -n1 | tr -s ' ' | rev | cut -d' ' -f1 | rev)
bash ${KARSANLAB_BITBUCKET_REPO}/scripts/get_delta_space_consumption.sh \
${PARSED_DATA_DIRECTORY}/${DATE}/${DATE}_ncdu.flat.json.summary.tsv \
${PARSED_DATA_DIRECTORY}/${PREVIOUS_DATE}/${PREVIOUS_DATE}_ncdu.flat.json.summary.tsv \
${SPACE_MONITORING_DIRECTORY}/${TRACKING_TABLE}

# Remove intermediate .iconv.json and .flat.json files
rm ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.iconv.json
rm ${NCDU_JSONS_DIRECTORY}/${DATE}_ncdu.flat.json

echo Completed space audit at $(date -Iseconds)