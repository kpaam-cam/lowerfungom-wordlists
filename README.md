# CLDF dataset derived from Tschonghongei's Wordlists Collected for the KPAAM-CAM Project (last updated 2024)

## How to cite

If you use these data please cite
- the original source
  > Tschonghongei, Nelson C. Wordlist collected for the KPAAM-CAM project. 2024.
- the derived dataset using the DOI of the [particular released version](../../releases/) you were using

## Description


## Notes

## Export data to EDICTOR

```
$ pip install pyedictor
$ edictor wordlist --name edictor/kpaamcam-edictor --preprocessing=raw/preprocess.py
```

This creates the file `edictor/kpaamcam-edictor.tsv`, which can be browed with https://lingulist.de/edictor/ and alignments can be investigated. From EDICTOR, nexus files can be exported to load data into SplitsTree.



Name | GitHub user | Description | Role
--- | --- | --- | ---
Jeff Good | @jcgood | maintainer | Other
Nelson C. Tschonghongei | | data collector | Author



## CLDF Datasets

The following CLDF datasets are available in [cldf](cldf):

- CLDF [Wordlist](https://github.com/cldf/cldf/tree/master/modules/Wordlist) at [cldf/cldf-metadata.json](cldf/cldf-metadata.json)
