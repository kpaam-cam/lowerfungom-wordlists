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

cogType = "lexstatid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)

# Mapping to regular language names is in a difference CLDF file
languageFile = "../../../gitrepos/grollemundbantu/cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

localtoGlotto = { }
nametoCoords = { }
for index, row in languageDF.iterrows():

	localname = row["ID"]
	glottoname = row["Glottolog_Name"]

	latitude = row["Latitude"]
	longitude = row["Longitude"]

	nametoCoords[localname] = [latitude, longitude]
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
			
			try: conceptToCogs[concept].append([doculect, cogid])
			except: conceptToCogs[concept] = [ [doculect, cogid] ]

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
	docucogs = conceptToCogs[concept]
	
	docus = [ ]
	glottos = [ ]
	cogs = [ ]		
	lats = [ ]
	longs = [ ]
	for docu, cog in docucogs:

		docus.append(docu)
		cogs.append(str(cog))
		
		glotto = localtoGlotto[docu]
		glottos.append(glotto)
				
		lat, long = nametoCoords[docu]
		lats.append(str(lat))
		longs.append(str(long))
		
		pass

	jitterLat = .1 # rough estimates
	jitterLong = .1
	
	comment = "# Map of detected cognates for " + concept + "\n"
	langsvariable = concept+"_langs = " + "c(\"" + "\", \"".join(glottos) + "\")" + "\n"
	labelsvariable = concept+"_labels = " + "c(\"" + "\", \"".join(docus) + "\")" + "\n"
	featsvariable = concept+"_feats = " + "c(\"" + "\", \"".join(cogs) + "\")" + "\n"
	latsvariable = concept+"_lats = " + "c(" + ", ".join(lats) + ")" + "\n"
	longsvariable = concept+"_longs = " + "c(" + ", ".join(longs) + ")" + "\n"
	jitterlat = concept+"_lats" + " = jitter(" + concept+"_lats, amount = " + str(jitterLat) +  ")\n"
	jitterlong = concept+"_longs" + " = jitter(" + concept+"_longs, amount = " + str(jitterLong) +  ")\n"
	makemap = (concept+"_map = " +
				"map.feature(languages = " +
				concept+"_langs, label = " +
				concept+"_labels, features = " +
				concept+"_feats, latitude = " +
				concept+"_lats, longitude = " +
				concept+"_longs " +				
				")\n")
	savemap = "mapshot(" + concept+"_map, " +  "file = \"" + mapFolder + "/" + concept + ".png\")" + "\n\n"

	rMapFile.write(comment)
	rMapFile.write(langsvariable)
	rMapFile.write(labelsvariable)
	rMapFile.write(featsvariable)
	rMapFile.write(latsvariable)
	rMapFile.write(longsvariable)
	rMapFile.write(jitterlat)
	rMapFile.write(jitterlong)
	rMapFile.write(makemap)
	rMapFile.write(savemap)

rMapFile.close()	
