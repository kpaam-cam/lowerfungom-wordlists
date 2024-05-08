# This is to see how cognates group with respect to doculects

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os
from math import sqrt
import statistics

# See: https://rpy2.github.io/doc/v3.3.x/html/pandas.html
# import rpy2
# import rpy2.robjects as ro
# from rpy2.robjects.packages import importr
# from rpy2.robjects import pandas2ri
# from rpy2.robjects.conversion import localconverter

# Storage folders
#analysesFolder = "../analyses"
#analysesSubfolder = "/Phase3a-Fall2023"
#filePrefix = "kplfSubset"

analysesFolder = "../grollemundTest/analyses"
analysesSubfolder = ""
filePrefix = "grollemund"


# SCA and LexStat similarity thresholds, needed for field names
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")

cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)

# Mapping to regular language names is in a difference CLDF file
languageFile = "../../../gitrepos/grollemundbantu/cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

localtoGlotto = { }
for index, row in languageDF.iterrows():
    localname = row["ID"]
    glottoname = row["Glottolog_Name"]
    localtoGlotto[localname] = glottoname
    

# Make a "turned" table for analysis of cognate predicatability of languoid
# Getting there but need to work on the data structure needed

conceptToCogs = { }
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType] # actually same as ID, fix later
			
			concept = concept.replace(",", "")
			concept = concept.replace("-", "")
			concept = concept.replace(" ", "_")
			glotto = localtoGlotto[doculect]
			
			try: conceptToCogs[concept].append([glotto, cogid])
			except: conceptToCogs[concept] = [ [glotto, cogid] ]
		else:
			pass

for concept in conceptToCogs:

	#print(concept)
	glottocogs = conceptToCogs[concept]
	
	glottos = [ ]
	cogs = [ ]		
	for glotto, cog in glottocogs:
		glottos.append(glotto)
		cogs.append(str(cog))
		pass
	
	print(concept+"_langs = " + "c(\"" + "\", \"".join(glottos) + "\")")
	print(concept+"_feats = " + "c(\"" + "\", \"".join(cogs) + "\")")
	print(concept+"_map = " + "map.feature(languages = " + concept+"_langs, features = " + concept+"_feats )")
	print("mapshot(" + concept+"_map, " +  "file = \"~/Desktop/Rmaps/" + concept + ".png\")")
	print()