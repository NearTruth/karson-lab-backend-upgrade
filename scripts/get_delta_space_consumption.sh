#!/usr/bin/env bash

# First argument is current time period .summary.tsv file
# Second argument is previous time period .summary.tsv. file
# Third argument is the on-going reporting table of space and delta change

set -e

CURRENT_SUMMARY=$1
OLD_SUMMARY=$2
TRACKING_TABLE=$3

CURRENT_DATE=$(echo $( basename ${CURRENT_SUMMARY}) | cut -d'_' -f1)
OLD_DATE=$(echo $( basename ${OLD_SUMMARY}) | cut -d'_' -f1)
CURRENT_SPACE=$(cat ${CURRENT_SUMMARY} | cut -f2 | sed 's/ //g' | numfmt --from=iec-i --suffix=B | sed 's/B//g')
OLD_SPACE=$(cat ${OLD_SUMMARY} | cut -f2 | sed 's/ //g' | numfmt --from=iec-i --suffix=B | sed 's/B//g')
DELTA=$( expr ${CURRENT_SPACE} - ${OLD_SPACE} | numfmt --to=iec --suffix=B )

echo Change in space consumption from ${CURRENT_DATE} to ${OLD_DATE} is ${DELTA}.

# Make third argument optional
if [ ! -z ${TRACKING_TABLE} ]
    then
        echo -e "${CURRENT_DATE}\t$(cat ${CURRENT_SUMMARY} | cut -f2)\t${DELTA}" >> ${TRACKING_TABLE}
fi
