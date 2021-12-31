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

conceptIndex = { }
for entry in entries:

	Concept = entry["Parameter_ID"]
	Doculect = entry["Language_ID"]
	
	try:
		conceptIndex[Concept] = conceptIndex[Concept] + 1
	except:
		conceptIndex[Concept] = 1

for concept in conceptIndex:
	density = round(conceptIndex[concept]/44,2)
	s = "\t"
	output = s.join([str(concept),str(density)])
	outputFile.write(output + "\n")

outputFile.close()