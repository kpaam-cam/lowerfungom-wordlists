## Export data to EDICTOR

```
$ pip install pyedictor
$ edictor wordlist --name edictor/kpaamcam-edictor --preprocessing=raw/preprocess.py
```

This creates the file `edictor/kpaamcam-edictor.tsv`, which can be browed with https://lingulist.de/edictor/ and alignments can be investigated. From EDICTOR, nexus files can be exported to load data into SplitsTree.
