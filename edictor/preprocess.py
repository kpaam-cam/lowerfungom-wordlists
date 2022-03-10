from lingpy import *
from collections import defaultdict

def run(wordlist):

    D = {0: wordlist.columns}

    concepts = sorted(
            wordlist.rows, 
            key=lambda x: len(wordlist.get_list(row=x, flat=True)),
            reverse=True)[:140]
    for idx in wordlist:
        if wordlist[idx, "concept"] in concepts:
            D[idx] = wordlist[idx]
    lex = LexStat(D)
    lex.cluster(method="sca", ref="cogid", threshold=0.45)
    alm = Alignments(lex, ref="cogid")
    alm.align()
    return alm
