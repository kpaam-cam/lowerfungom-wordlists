# This is to see how cognates group with respect to doculects

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os
import shutil
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
    
# Gather data as needed
conceptToCogs = { }
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType] # actually same as ID, fix later
			
			# some clean up for R compatibility
			concept = concept.replace(",", "")
			concept = concept.replace("-", "")
			concept = concept.replace(" ", "_")

			glotto = localtoGlotto[doculect]
			
			try: conceptToCogs[concept].append([glotto, cogid])
			except: conceptToCogs[concept] = [ [glotto, cogid] ]
		else:
			pass


# Write out to R
# Overwrite folder if it exists
mapFolder = filePrefix + "-" + cogType + "-maps"
mapFolderPath = analysesFolder + "/" + analysesSubfolder + "/" + mapFolder
if os.path.exists(mapFolderPath):
    shutil.rmtree(mapFolderPath)
os.makedirs(mapFolderPath)

rMapFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-makemaps" + ".r"
rMapFile = open(rMapFileName, "w")
rMapFile.write("library(lingtypology)\n")
rMapFile.write("library(mapview)\n")
rMapFile.write("\n")
for concept in conceptToCogs:

	#print(concept)
	glottocogs = conceptToCogs[concept]
	
	glottos = [ ]
	cogs = [ ]		
	for glotto, cog in glottocogs:
		glottos.append(glotto)
		cogs.append(str(cog))
		pass

	comment = "# Map of detected cognates for " + concept + "\n"
	langsvariable = concept+"_langs = " + "c(\"" + "\", \"".join(glottos) + "\")" + "\n"
	featsvariable = concept+"_feats = " + "c(\"" + "\", \"".join(cogs) + "\")" + "\n"
	makemap = concept+"_map = " + "map.feature(languages = " + concept+"_langs, features = " + concept+"_feats )" + "\n"
	savemap = "mapshot(" + concept+"_map, " +  "file = \"" + mapFolder + "/" + concept + ".png\")" + "\n\n"

	rMapFile.write(comment)
	rMapFile.write(langsvariable)
	rMapFile.write(featsvariable)
	rMapFile.write(makemap)
	rMapFile.write(savemap)

rMapFile.close()	
