import lingpy
from lingpy import *
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
import pandas
import os


wordlists = pandas.read_csv("../cldf/forms.csv", ) 
entries = wordlists.to_dict(orient='records')
outputFileName = "WordlistStats"
outputFile = open("../analyses/" + outputFileName + ".tsv", "w")
header = "Concept\tDensity"
outputFile.write(header + "\n")

from lingpy.compare.sanity import mutual_coverage_check
wl = Wordlist('test_data/KSL.qlc")
for i in range(wl.height, 1, -1):
        if mutual_coverage_check(wl, i):
            print('mutual coverage is {0}'.format(i))
            break