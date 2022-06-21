# Makes a second orthography file that doesn't clobber tones
# This is good if one wants to analyze impacts of tone correspondence and
# should also help with certain kinds of data parsing (tbd)

import pandas
import math
import re

# Make orthography dictionary
tonelessOrthography = "../etc/orthography-toneless.tsv"
orthList = pandas.read_csv(tonelessOrthography, sep="\t") 
orths = orthList.to_dict(orient='records')

outputFilePathName = "../etc/" + "orthography-toned.tsv"
outputFile = open(outputFilePathName, "w")
header = "Grapheme\tIPA\tFREQUENCY\tCODEPOINTS\tNOTES"
outputFile.write(header + "\n")

orthDict = [ ]
for orth in orths:
	Grapheme = orth["Grapheme"]
	
	# Maybe I am reading vis Pandas wrong, but blank things were NaN, and that cause problems
	IPA = orth["IPA"]
	try:
		math.isnan(IPA)
		IPA = "NULL"
	except: pass

	Freq = orth["FREQUENCY"]
	try:
		math.isnan(Freq)
		Freq = ""
	except: pass

	Codepoints = orth["CODEPOINTS"]
	try:
		math.isnan(Codepoints)
		Codepoints = ""
	except: pass

	Notes = orth["NOTES"]
	try:
		math.isnan(Notes)
		Notes = ""
	except: pass
	
	if IPA == "NULL":
		tonedIPA = IPA
	elif re.search("/", IPA):
		tonedIPA, tonelessIPA = re.split("/", IPA)
	else: tonedIPA = IPA
	#print(IPA, tonedIPA)
	
	tab = "\t"
	outputFile.write(tab.join([Grapheme, tonedIPA, Freq, Codepoints, Notes]) + "\n")

outputFile.close()	

