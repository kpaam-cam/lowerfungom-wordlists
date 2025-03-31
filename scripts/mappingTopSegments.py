# This makes maps of the cognates

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os
import shutil
from math import sqrt
import statistics

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

# We'll jitter the doculects by hand to give them a consistent position
jit = .003 # adjust for amount for jitter desired
jits = {
	"ECLAbar8":			[ jit, 0 ],
	"NACAbar2":			[ -jit, 0 ],
	"NMAAbar1":			[ 0, jit ],
	"NVBAbar7":			[ 0, -jit ],
	"KDCAjumbu10":		[ jit, 0 ],
	"KMNAjumbu2":		[ 0, jit ],
	"NEMAjumbu9":		[ 0, -jit ],
	"NVIAjumbu1":		[ -jit, 0 ],
	"ENBBiya1":			[ jit, jit ],
	"FBCBiya8":			[ -jit, jit ],
	"ICNBiya2":			[ -jit, -jit ],
	"NFKBiya7":			[ jit, -jit ],
	"NJNBiya6":			[ jit*1.5, 0 ],
	"NSFBiya5":			[ -jit*1.5, 0 ],
	"KCYBuu2":			[ jit, 0 ],
	"KEMBuu1":			[ -jit, 0 ],
	"MNJBuu4":			[ 0, jit ],
	"NNBBuu3":			[ 0, -jit ],
	"DPNFang13":		[ jit, 0 ],
	"KDVFang1":			[ -jit, 0 ],
	"KHKFang12":		[ 0, jit ],
	"KJSFang2":			[ 0, -jit ],
	"JGYKoshin3":		[ jit, 0 ],
	"MRYKoshin2":		[ -jit, jit ],
	"TELKoshin4":		[ -jit, -jit ],
	"BNMKung2":			[ jit, 0 ],
	"KCSKung3":			[ -jit, 0 ],
	"NJSKung4":			[ 0, jit ],
	"ZKGKung1":			[ 0, -jit ],
	"ABSMissong1":		[ jit, 0 ],
	"AGAMissong2":		[ -jit, 0 ],
	"NDNMissong5":		[ 0, jit ],
	"NMSMissong4":		[ 0, -jit ],
	"APBMumfu1":		[ jit, 0 ],
	"DNMMumfu2":		[ -jit, 0 ],
	"MEAMumfu3":		[ 0, jit ],
	"NCCMumfu4":		[ 0, -jit ],
	"CENMundabli2":		[ jit, 0 ],
	"LFNMundabli1":		[ -jit, 0 ],
	"NINMundabli4":		[ 0, jit ],
	"NMNMundabli3":		[ 0, -jit ],
	"NEAMunken1":		[ jit, 0 ],
	"NGTMunken3":		[ -jit, 0 ],
	"NUNMunken4":		[ 0, jit ],
	"TNTMunken2":		[ 0, -jit ],
	"BAAMashi4":		[ jit, 0 ],
	"BKBMashi2":		[ -jit, 0 ],
	"KFKMashi1":		[ 0, jit ],
	"NCMMashi5":		[ 0, -jit ],
	"AOMNgun2":			[ jit, 0 ],
	"KBMNgun4":			[ -jit, 0 ],
	"MCANgun3":			[ 0, jit ],
	"WCANgun1":			[ 0, -jit ],
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

	jitlat, jitlong = jits[localname]
	adjlat = latitude + jitlat
	adjlong = longitude + jitlong
	
	nametoCoords[localname] = [adjlat, adjlong]

	localtoGlotto[localname] = glottoname



rMapFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + phontyp + "-segmentmap" + ".r"
rMapFile = open(rMapFileName, "w")
rMapFile.write("library(needs labelMaps.R modified from lingtypology)\n")
rMapFile.write("library(mapview)\n")
rMapFile.write("\n")

	
segmentFile = "../analyses/segments/highestZScores-LF.tsv"
segmentStatsDF = pd.read_csv(segmentFile, header=0, sep="\t")


docus = [ ]
glottos = [ ]
segs = [ ]
zscores = [ ]
popups = [ ]	
lats = [ ]
longs = [ ]
for index, segz in segmentStatsDF.iterrows():

	docu = segz["Doculect"]
	seg = segz["Segment"]
	zscore = segz["Zscore"]

	docus.append(docu)	
	segs.append(seg)
	zscores.append(str(zscore))
	
	popups.append(docu + "<br/>" + str(zscore))
	
	glotto = localtoGlotto[docu]
	glottos.append(glotto)
			
	lat, long = nametoCoords[docu]
	lats.append(str(lat))
	longs.append(str(long))

#jitterLat = .1 # rough estimates
#jitterLong = .1

#jitterLat = 0 # rough estimates
#jitterLong = 0

comment = "# Map of segments with highest zscore for TLS data \n"
langsvariable = "langs = " + "c(\"" + "\", \"".join(glottos) + "\")" + "\n"
# linebreaks added because really long lines broke R, would try to pretty print, but don't think that would work easily here due to mixing of spaces inside quotations
labelsvariable = "labels = " + "c(\"" + "\",\n \"".join(segs) + "\")" + "\n"
popupsvariable = "popups = " + "c(\"" + "\",\n \"".join(popups) + "\")" + "\n"
featsvariable = ("feats = " + "c(" + ", ".join(zscores) + ")" + "\n")
latsvariable = "lats = " + "c(" + ", ".join(lats) + ")" + "\n"
longsvariable = "longs = " + "c(" + ", ".join(longs) + ")" + "\n"
#jitterlat = "lats" + " = jitter(" + "lats, amount = " + str(jitterLat) +  ")\n"
#jitterlong = "longs" + " = jitter(" + "longs, amount = " + str(jitterLong) +  ")\n"
makemap = ("map = " +
			"map.feature(languages = " +
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
rMapFile.write(savepdf)
rMapFile.write(savehtml)

rMapFile.close()	
