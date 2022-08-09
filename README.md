## Space Monitoring Utility

This repo contains instruction and utilities for monitoring space
usage in `/projects/karsanlab/`.

### Dependencies
* Python3 
* Python module: [humanfriendly](https://pypi.org/project/humanfriendly/)
* Python module: [ijson](https://github.com/isagalaev/ijson)
* Git repository: [ncdu-export](https://github.com/wodny/ncdu-export) tools

A conda environment has been created with the required dependencies
and the scripts sym-linked into the bin directory.
Activate with: 
```
cd /projects/karsanlab/space_monitoring
eval "$(/projects/karsanlab/software/linux-x86_64-centos7/anaconda3/bin/conda shell.bash hook)"
conda activate ./env_space_monitoring
```

### Summary

The steps outlined below will run as a cron job (`cron_jobs/report_space_cron.sh`) each week, generating summary files of:
* `<DATE>_ncdu.flat.json.summary.tsv` - The total space consumed in `/projects/karsanlab` 
* `<DATE>_ncdu.flat.json.large_files.tsv` - Files greater than 10 GB
* `<DATE>_ncdu.flat.json.old_intermediate_files_for_possible_deletion.tsv` - Files suffixed with `.sam`, `.fq`, `.fastq`, `.mpileup`
that have not been modified in over 30 days.
* `<DATE>_ncdu.flat.json.files_set_to_user_group.tsv` - Files that are set to the group owner `user`

A change in space consumption from the previous week is appended to the file:
`/projects/karsanlab/space_monitoring/on_going_space_report.tsv`
which is a table with the format:

|Date|Space Total|Change From Previous Week|
|----|-----------|-------------------------|
|2020-02-24|16.29 TiB|N/A|
|2020-03-07|16.71 TiB|431GB|


### Detailed Instructions

#### Set-up
Source python virtual environment with the installed dependencies:
```
cd /projects/karsanlab/space_monitoring
conda activate ./env_space_monitoring
```

#### Run ncdu 

Run `ncdu` to generate a JSON:
```
ncdu -0 -r -x -e --exclude /projects/karsanlab/.snapshot -o - /projects/karsanlab | gzip > /projects/karsanlab/space_monitoring/ncdu_jsons/<DATE>_ncdu.json.gz
```

#### Format ncdu JSON
Remove non UTF-8 characters:
```
zcat /projects/karsanlab/space_monitoring/ncdu_jsons/<DATE>_ncdu.json.gz | iconv -f utf-8 -t utf-8 -c - > /projects/karsanlab/space_monitoring/ncdu_jsons/<DATE>_ncdu.iconv.json
```

Flatten the JSON with [ncdu-export](https://github.com/wodny/ncdu-export):
``` 
python /projects/karsanlab/space_monitoring/ncdu-export/flatten.py \
--dirs array /projects/karsanlab/space_monitoring/<DATE>_ncdu.iconv.json > /projects/karsanlab/space_monitoring/<DATE>_ncdu.flat.json
```

#### Parse the JSON to get information
```
python scripts/parse_ncdu_json.py -i /projects/karsanlab/space_monitoring/ncdu_jsons/<DATE>_ncdu.flat.json
```
See **Summary** section for the output files returned.


#### Get change in space consumption from a previous time
``` 
bash scripts/get_delta_space_consumption.sh \
<CURRENT_DATE>_ncdu.flat.json.summary.tsv <PREVIOUS_DATE>_ncdu.flat.json.summary.tsv 
```

