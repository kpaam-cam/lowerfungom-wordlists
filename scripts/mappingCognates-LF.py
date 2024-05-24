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
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

#analysesFolder = "../grollemund-wordlists/analyses"
#analysesSubfolder = ""
#filePrefix = "grollemund"


# SCA and LexStat similarity thresholds, needed for field names
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")

cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)

# Mapping to regular language names is in a difference CLDF file
languageFile = "../cldf/languages.csv"
languageDF = pd.read_csv(languageFile)

# We'll jitter the doculects by hand to give them a consistent positio
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
	}	

nametoCoords = { }
nametoGlotto = { }
for index, row in languageDF.iterrows():
	
	localname = row["ID"]
	glottoname = row["Glottolog_Name"]
	
	latitude = row["Latitude"]
	longitude = row["Longitude"]
	
	jitlat, jitlong = jits[localname]
	adjlat = latitude + jitlat
	adjlong = longitude + jitlong
	
	nametoCoords[localname] = [adjlat, adjlong]
	nametoGlotto[localname] = glottoname


# Gather data as needed
conceptToCogs = { }
cogidCount = { }
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:

			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType] # actually same as ID, fix later
			form = wl[reflex[0], 'ipa']
			
			# some clean up for R compatibility
			concept = concept.replace(",", "")
			concept = concept.replace("-", "")
			concept = concept.replace(" ", "_")
			concept = concept.replace(")", "")
			concept = concept.replace("(", "")

			#glotto = localtoGlotto[doculect]
			
			try: conceptToCogs[concept].append([doculect, cogid, form])
			except: conceptToCogs[concept] = [ [doculect, cogid, form] ]

			# Keep track of number of forms in each id for legend
			try: cogidCount[cogid] = cogidCount[cogid] + 1
			except: cogidCount[cogid] = 1
			
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

	# Idea here was to sort the output by highest number of cognates
	# R did not respect that, but we can use this sorting to create a levels
	# feature to get the sorting right
	docucogs.sort(key=lambda docucog: -cogidCount[docucog[1]] )
	
	docus = [ ]
	glottos = [ ]
	cogs = [ ]	
	forms = [ ]
	popups = [ ]	
	lats = [ ]
	longs = [ ]
	for docu, cog, form in docucogs:
	
		docus.append(docu)
		
		cog = concept + "_" + str(cog) + " (" + str(cogidCount[cog]) + ")"
		cogs.append(cog)
		
		forms.append(form)
		
		popups.append(docu + "<br/>" + form)
		
		glotto = nametoGlotto[docu]
		glottos.append(glotto)
				
		lat, long = nametoCoords[docu]
		lats.append(str(lat))
		longs.append(str(long))
		
		pass

	# The cogs are now ordered properly (hopefully) due to sorting above
	# Make a new list getting rid of duplicte (can't use set()), doesn't maintain order)
	levels = [ ]
	for cog in cogs:
		if cog in levels: pass
		else: levels.append(cog)

	#jitterLat = .003
	#jitterLong = .003
	
	comment = "# Map of detected cognates for " + concept + "\n"
	langsvariable = concept+"_langs = " + "c(\"" + "\", \"".join(glottos) + "\")" + "\n"
	labelsvariable = concept+"_labels = " + "c(\"" + "\", \"".join(forms) + "\")" + "\n"
	popupsvariable = concept+"_popups = " + "c(\"" + "\", \"".join(popups) + "\")" + "\n"
	featsvariable = (concept+"_feats = " + "factor(c(\"" + "\", \"".join(cogs) + "\"), " +
					 "levels = c(\"" + "\", \"".join(levels) + "\"))" + "\n")
	latsvariable = concept+"_lats = " + "c(" + ", ".join(lats) + ")" + "\n"
	longsvariable = concept+"_longs = " + "c(" + ", ".join(longs) + ")" + "\n"
	#jitterlat = concept+"_lats" + " = jitter(" + concept+"_lats, amount = " + str(jitterLat) +  ")\n"
	#jitterlong = concept+"_longs" + " = jitter(" + concept+"_longs, amount = " + str(jitterLong) +  ")\n"
	makemap = (concept+"_map = " +
				"map.feature(languages = " +
				concept+"_langs, label = " +
				concept+"_labels, features = " +
				concept+"_feats, popup = " +
				concept+"_popups, latitude = " +
				concept+"_lats, longitude = " +
				concept+"_longs " +				
				")\n")
	savepdf = "mapshot(" + concept+"_map, " +  "file = \"" + mapFolder + "/" + concept + ".pdf\")" + "\n"
	savehtml = "mapshot(" + concept+"_map, " +  "url = \"" + mapFolder + "/" + concept + ".html\")" + "\n\n"

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

"""
Notes on improving the maps for special cases
This is the R code

library(khroma)
#bright is a good color scheme, but only goes to 7 features, not good for all maps
bright <- color("bright")

# the color feature is the new addition here
chief_map = map.feature(languages = chief_langs, label = chief_labels, features = chief_feats, popup = chief_popups, latitude = chief_lats, longitude = chief_longs, color=c(bright(length(unique(chief_feats)))))

# Here we can add a tile that makes things clearer. Code is awkward, but it works for now
cm = chief_map %>% addTiles("https://{s}.tile.jawg.io/jawg-sunny/{z}/{x}/{y}{r}.png?access-token=qb42hbh4cIbpH5UKqERfDH0MSxvPgVQNKmWgpmQMiUsPNZAPxBxNo2iXOb6lhUFm")


"""
