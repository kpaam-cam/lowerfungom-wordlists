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


def viladj(doculect):

	# village-specific adjustments
	vils = {
		"Abar": [ 0, 0 ],
		"Ajumbu": [.001, -.001 ],
		"Buu":	[0, 0],
		"Biya": [.001, 0 ],
		"Fang": [ 0, 0 ],
		"Koshin": [.001, 0 ],
		"Kung": [.001, 0],
		"Mashi": [0, -.001 ],
		"Missong": [0, 0],
		"Mumfu": [0, 0],
		"Mundabli": [0, -.001],
		"Munken": [0, 0],
		"Ngun": [0, 0],
		}

	match = re.search(r'[A-Z]{3}([A-Z][a-z]+)\d', doculect)
	village = match.group(1)
	vilshift = vils[village]
	return(vilshift)


# We'll jitter the doculects by hand to give them a consistent position
latjit = .0035 # adjust for amount for jitter desired
longjit = .0055 # adjust for amount for jitter desired
jits = {
	"ECLAbar8":			[ latjit, 0 ],
	"NACAbar2":			[ -latjit, 0 ],
	"NMAAbar1":			[ 0, longjit ],
	"NVBAbar7":			[ 0, -longjit ],
	"KDCAjumbu10":		[ latjit, 0 ],
	"KMNAjumbu2":		[ 0, longjit ],
	"NEMAjumbu9":		[ 0, -longjit ],
	"NVIAjumbu1":		[ -latjit, 0 ],
	"ENBBiya1":			[ latjit, longjit ],
	"FBCBiya8":			[ -latjit, longjit ],
	"ICNBiya2":			[ -latjit, -longjit ],
	"NFKBiya7":			[ latjit, -longjit ],
	"NJNBiya6":			[ latjit*1.5, 0 ],
	"NSFBiya5":			[ -latjit*1.5, 0 ],
	"KCYBuu2":			[ latjit, 0 ],
	"KEMBuu1":			[ -latjit, 0 ],
	"MNJBuu4":			[ 0, longjit ],
	"NNBBuu3":			[ 0, -longjit ],
	"DPNFang13":		[ latjit, 0 ],
	"KDVFang1":			[ -latjit, 0 ],
	"KHKFang12":		[ 0, longjit ],
	"KJSFang2":			[ 0, -longjit ],
	"JGYKoshin3":		[ latjit, 0 ],
	"MRYKoshin2":		[ -latjit, longjit ],
	"TELKoshin4":		[ -latjit, -longjit ],
	"BNMKung2":			[ latjit, 0 ],
	"KCSKung3":			[ -latjit, 0 ],
	"NJSKung4":			[ 0, longjit ],
	"ZKGKung1":			[ 0, -longjit ],
	"ABSMissong1":		[ latjit, 0 ],
	"AGAMissong2":		[ -latjit, 0 ],
	"NDNMissong5":		[ 0, longjit ],
	"NMSMissong4":		[ 0, -longjit ],
	"APBMumfu1":		[ latjit, 0 ],
	"DNMMumfu2":		[ -latjit, 0 ],
	"MEAMumfu3":		[ 0, longjit ],
	"NCCMumfu4":		[ 0, -longjit ],
	"CENMundabli2":		[ latjit, 0 ],
	"LFNMundabli1":		[ -latjit, 0 ],
	"NINMundabli4":		[ 0, longjit ],
	"NMNMundabli3":		[ 0, -longjit ],
	"NEAMunken1":		[ latjit, 0 ],
	"NGTMunken3":		[ -latjit, 0 ],
	"NUNMunken4":		[ 0, longjit ],
	"TNTMunken2":		[ 0, -longjit ],
	"BAAMashi4":		[ latjit, 0 ],
	"BKBMashi2":		[ -latjit, 0 ],
	"KFKMashi1":		[ 0, longjit ],
	"NCMMashi5":		[ 0, -longjit ],
	"AOMNgun2":			[ latjit, 0 ],
	"KBMNgun4":			[ -latjit, 0 ],
	"MCANgun3":			[ 0, longjit ],
	"WCANgun1":			[ 0, -longjit ],
	"NGTAbar3ANT": [0, 0],
	"NGTMissong3ANT": [0, 0],
	"NVBMunken7ANT": [0, 0],
	"NVBMissong7ANT": [0, 0],
	"NVBNgun7ANT": [0, 0],
	"AOMAbar2ANT": [0, 0],
	"AOMNgun2ANT": [0, 0],
	"AOMMunken2ANT": [0, 0],
	}	
	
localtoGlotto = { }
nametoCoords = { }
for index, row in languageDF.iterrows():

	localname = row["ID"]
	
	# No glottoname in CLDF, fetch via pyglottlog
	glottocode = row["Glottocode"]
	glottoname = row["Glottolog_Name"]
	
	latitude = row["Latitude"]
	longitude = row["Longitude"]

	# Basic jitter
	jitlat, jitlong = jits[localname]
	adjlat = latitude + jitlat
	adjlong = longitude + jitlong
	
	# village-specific shifts
	latshift, longshift = viladj(localname)
	adjlat = adjlat + latshift
	adjlong = adjlong + longshift
	
	nametoCoords[localname] = [adjlat, adjlong]

	localtoGlotto[localname] = glottoname



rMapFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + phontyp + "-segmentmap" + ".r"
rMapFile = open(rMapFileName, "w")
rMapFile.write("library(lingtypology)\n")
rMapFile.write("library(mapview)\n")
rMapFile.write("library(dplyr) # for magrittr function\n")
rMapFile.write("source(\"/Users/jcgood/gitrepos/tls/scripts/labelMaps.R\") # Custom function based on lingtypology for label maps\n")
rMapFile.write("\n")

	
segmentFile = "../analyses/segments/highestSalienceScores-LF.tsv"
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
	#salience = round(math.sqrt(salience))
	# variant is log, trying natural for now, used log 10 for TLS
	salience = math.log(salience)

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

comment = "# Map of segments with highest zscore for TLS data \n"
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
