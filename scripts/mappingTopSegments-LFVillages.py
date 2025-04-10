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
filePrefix = "LF"
phontyp = "unusuallyfrequent"
mapFolder = "."


# Mapping to regular language names is in a difference CLDF file
languageFile = "../cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

# initalize glottolog
#glottolog = Glottolog('/Users/jcgood/gitrepos/glottolog')


nametoCoords = {
	"Abar": [ 6.577583, 10.237533 ],
	"Ajumbu": [ 6.5391, 10.238567 ],
	"Buu":	[ 6.56465, 10.25515 ],
	"Biya": [ 6.592167, 10.205533 ],
	"Fang": [ 6.549667, 10.279017 ],
	"Koshin": [ 6.58815, 10.281317 ],
	"Kung": [ 6.561033,	10.220383 ],
	"Mashi": [ 6.600783, 10.265667 ],
	"Missong": [ 6.59745, 10.24715 ],
	"Mumfu": [ 6.612433, 10.257167 ],
	"Mundabli": [ 6.606933, 10.2733 ],
	"Munken": [ 6.5953, 10.223467 ],
	"Ngun": [ 6.5814, 10.212583 ],
	}

localtoGlotto = {
	"Abar": "Mungbam",
	"Ajumbu": "Ajumbu",
	"Buu":	"Buu",
	"Biya": "Mungbam",
	"Fang": "Fang (Cameroon)",
	"Koshin": "Koshin",
	"Kung": "Kung",
	"Mashi": "Naki",
	"Missong": "Mungbam",
	"Mumfu": "Mundabli-Mufu",
	"Mundabli": "Mundabli-Mufu",
	"Munken": "Mungbam",
	"Ngun": "Mungbam",
	}



rMapFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + phontyp + "-segmentmapByVillage" + ".r"
rMapFile = open(rMapFileName, "w")
rMapFile.write("library(lingtypology)\n")
rMapFile.write("library(mapview)\n")
rMapFile.write("library(dplyr) # for magrittr function\n")
rMapFile.write("source(\"/Users/jcgood/gitrepos/tls/scripts/labelMaps.R\") # Custom function based on lingtypology for label maps\n")
rMapFile.write("\n")

	
segmentFile = "../analyses/segments/highestSalienceScores-LFbyVillage.tsv"
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
	if salience >= 0:
		salience = round(math.sqrt(salience))
	else: # handle negative salience (but check to see if I actually outputted that or not)
		salience = -round(math.sqrt(-salience))

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

comment = "# Map of segments with highest zscore for LF by village \n"
langsvariable = "langs = " + "c(\"" + "\", \"".join(glottos) + "\")" + "\n"
# linebreaks added because really long lines broke R, would try to pretty print, but don't think that would work easily here due to mixing of spaces inside quotations
labelsvariable = "labels = " + "c(\"" + "\",\n \"".join(segs) + "\")" + "\n"
popupsvariable = "popups = " + "c(\"" + "\",\n \"".join(popups) + "\")" + "\n"
#featsvariable = ("feats = " + "c(" + ", ".join(zscores) + ")" + "\n")
featsvariable = ("feats = " + "c(" + ", ".join(saliences) + ")" + "\n")
latsvariable = "lats = " + "c(" + ", ".join(lats) + ")" + "\n"
longsvariable = "longs = " + "c(" + ", ".join(longs) + ")" + "\n"
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
