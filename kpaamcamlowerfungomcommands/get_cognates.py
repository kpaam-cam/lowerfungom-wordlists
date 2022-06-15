"""
Compute cognates and alignments from the data.
"""
from lingpy import *
from lexibank_kpaamcamlowerfungom import Dataset

def run(args):
    
    # default import of data with lingpy
    KPLF = Dataset()
    lex = LexStat.from_cldf(
            KPLF.cldf_dir.joinpath("cldf-metadata.json")
            )
    lex.cluster(method="sca", ref="cogid", threshold=0.45)
    alm = Alignments(lex, ref="cogid")
    alm.align()
    alm.output(
            "tsv", 
            filename=KPLF.dir.joinpath(
                "analyses", "kplf-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
    args.log.info("[i] computed alignments and wrote them to file")

