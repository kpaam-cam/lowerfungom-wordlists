# This makes maps of the cognates

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os
import shutil
from math import sqrt
import statistics
import math
import re

#from pyglottolog import Glottolog

analysesFolder = "../analyses"
analysesSubfolder = "segments"
filePrefix = "grol"
phontyp = "unusuallyfrequent"
mapFolder = "."


# Mapping to regular language names is in a difference CLDF file
languageFile = "../cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

# initalize glottolog
#glottolog = Glottolog('/Users/jcgood/gitrepos/glottolog')



localtoGlotto = { }
nametoCoords = { }
for index, row in languageDF.iterrows():

	localname = row["ID"]
	
	# No glottoname in CLDF, fetch via pyglottlog
	glottocode = row["Glottocode"]
	glottoname = row["Glottolog_Name"]
	
	latitude = row["Latitude"]
	longitude = row["Longitude"]
	
	nametoCoords[localname] = [latitude, longitude]

	localtoGlotto[localname] = glottoname



rMapFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + phontyp + "-segmentmap" + ".r"
rMapFile = open(rMapFileName, "w")
rMapFile.write("library(lingtypology)\n")
rMapFile.write("library(mapview)\n")
rMapFile.write("library(dplyr) # for magrittr function\n")
rMapFile.write("source(\"/Users/jcgood/gitrepos/tls/scripts/labelMaps.R\") # Custom function based on lingtypology for label maps\n")
rMapFile.write("\n")

	
segmentFile = "../analyses/segments/highestSalienceScores-Grollemund.tsv"
segmentStatsDF = pd.read_csv(segmentFile, header=0, sep="\t")


docus = [ ]
glottos = [ ]
segs = [ ]
zscores = [ ]
saliences = [ ]
popups = [ ]	
lats = [ ]
longs = [ ]
for index, segz in segmentStatsDF.iterrows():

	docu = segz["Doculect"]
	seg = segz["Segment"]
	zscore = segz["Zscore"]

	salience = segz["SalienceScore"]
	# For mapping, square root to minimize range to get better color visualization
	salience = round(math.sqrt(salience))

	docus.append(docu)	
	segs.append(seg)
	zscores.append(str(zscore))
	saliences.append(str(salience))
	
	#popups.append(docu + "<br/>" + str(zscore))
	popups.append(docu + "<br/>" + str(salience))
	
	glotto = localtoGlotto[docu]
	glottos.append(glotto)
			
	lat, long = nametoCoords[docu]
	lats.append(str(lat))
	longs.append(str(long - .001)) # general shift left factor

#jitterLat = .1 # rough estimates
#jitterLong = .1

#jitterLat = 0 # rough estimates
#jitterLong = 0

comment = "# Map of segments with highest zscore for Grollemund data \n"
# linebreaks added because really long lines broke R, would try to pretty print, but don't think that would work easily here due to mixing of spaces inside quotations
langsvariable = "langs = " + "c(\"" + "\",\n \"".join(glottos) + "\")" + "\n"
labelsvariable = "labels = " + "c(\"" + "\",\n \"".join(segs) + "\")" + "\n"
popupsvariable = "popups = " + "c(\"" + "\",\n \"".join(popups) + "\")" + "\n"
#featsvariable = ("feats = " + "c(" + ", ".join(zscores) + ")" + "\n")
featsvariable = ("feats = " + "c(" + ", ".join(saliences) + ")" + "\n")
latsvariable = "lats = " + "c(" + ",\n".join(lats) + ")" + "\n"
longsvariable = "longs = " + "c(" + ",\n".join(longs) + ")" + "\n"
#jitterlat = "lats" + " = jitter(" + "lats, amount = " + str(jitterLat) +  ")\n"
#jitterlong = "longs" + " = jitter(" + "longs, amount = " + str(jitterLong) +  ")\n"
makemap = ("map = " +
			"map.feature.label(languages = " +
			"langs, label = " +
			"labels, features = " +
			"feats, popup = " +
			"popups, latitude = " +
			"lats, longitude = " +
			"longs, " +	
			"label.hide = FALSE, color=\"magma\"" + ")\n")
savepdf = "mapshot(" + "map, " +  "file = \"" + mapFolder + "/" + "HighestZMap.pdf\")" + "\n"
savehtml = "mapshot(" + "map, " +  "url = \"" + mapFolder + "/" + "HighestZMap.html\")" + "\n\n"




rMapFile.write(comment)
rMapFile.write(langsvariable)
rMapFile.write(labelsvariable)
rMapFile.write(featsvariable)
rMapFile.write(popupsvariable)
rMapFile.write(latsvariable)
rMapFile.write(longsvariable)
#rMapFile.write(jitterlat)
#rMapFile.write(jitterlong)
rMapFile.write(makemap)
#rMapFile.write(savepdf)
#rMapFile.write(savehtml)

rMapFile.close()	
