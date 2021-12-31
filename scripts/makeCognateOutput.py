import lingpy
from lingpy import *
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
from lingpy.convert.strings import write_nexus
import pandas
import os


# Parameters for file to open
coverageLimit = 33
SCAthreshold = 0.45
LSthreshold = 0.55

outputFileName = "AllAvailable-" + str(coverageLimit) + "coverage"
thresholdStr = "-" + str(f'{(SCAthreshold):g}') + "_" + str(f'{(LSthreshold):g}') + "thresholds"

try:
	#If the LexStat calculations have been done already use those
	lex = LexStat("../analyses/" + outputFileName + ".tsv.bin.tsv")
except:
	raise ValueError("Can't find file.")

lex.cluster(method='sca', threshold=SCAthreshold, ref='scaid', restricted_chars='_')
lex.calculate('tree', ref='scaid')

#alm = Alignments(lex, ref='lexstatid')
#alm.align()
#alm.output('usetex', filename="../analyses/" + outputFileName + thresholdStr + #"-LSCognateAlignments")

alm = Alignments(lex, ref='scaid')
alm.align()
alm.output('tsv', filename="../analyses/" + outputFileName + thresholdStr + "-SCACognateAlignments")