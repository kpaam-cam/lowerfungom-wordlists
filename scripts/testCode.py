from lingpy import *
from lingpy.compare.partial import Partial

import sys
sys.path.append(r'/Users/jcgood/Box/KPAAMCAM-Databases/SSML2tests/lftest_wordlist/')
from lexibank_lf import Dataset

wl = Wordlist.from_cldf(Dataset().cldf_dir.joinpath('cldf-metadata.json'))

lex = Partial(wl, check=True)
lex.get_partial_scorer(runs=1000)
lex.partial_cluster(method="lexstat", threshold=0.55, ref="cogids",
        cluster_method="upgma")

alm = Alignments(lex, ref='cogids')
alm.align()
alm.output('tsv', filename=Dataset().dir.joinpath('scripts',
    "KPAAMCAM-aligned").as_posix())

lex.calculate('tree', ref='cogids')
print(lex.tree.asciiArt())
