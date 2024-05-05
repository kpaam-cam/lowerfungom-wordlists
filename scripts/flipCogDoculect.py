# This is to see how cognates group with respect to doculects

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os

   
# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

# SCA and LexStat similarity thresholds, needed for field names
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")

cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)


# Make a "turned" table for analysis of cognate predicatability of languoid
# First, get a dictionary that takes a doculect and links to all cogids associated with the doculect
cogidtoDoculects = { }
cogidtoConcept= { }
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType] # actually same as ID, fix later
			cogidtoConcept[cogid] = [ concept + "_" + str(cogid), concept ]
			try: cogidtoDoculects[cogid].append(doculect)
			except: cogidtoDoculects[cogid] = [doculect]
		else:
			pass

# Issue: includes vacuous comparison of cognate sets associated with same concept
# Issue: Cognate sets of size 1 can be ignored
# Issue: The combinatorics are two large at 3890 cognates, need to halve in triangular form and filter as possible

lowerThreshold = 10
upperThreshold = 40

seenPairs = [ ]
cogDistances = [ ]
cognetworkFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + "cognetwork" + ".tsv"
cognetworkFile = open(cognetworkFilename, "w")
cognetworkFile.write("\t".join(("Cognate1", "Cognate1", "Weight")))
cognetworkFile.write("\n")
for firstcog in cogidtoDoculects.keys():

	firstconceptID, firstconcept = cogidtoConcept[firstcog]
	firstdoculects = cogidtoDoculects[firstcog]

	if len(firstdoculects) >= lowerThreshold and len(firstdoculects) <= upperThreshold:
	# Imposing some limits for manageability, also done below

		for secondcog in cogidtoDoculects.keys():
			secondconceptID, secondconcept = cogidtoConcept[secondcog]
			if firstconcept == secondconcept:
				continue
			seconddoculects = cogidtoDoculects[secondcog]

			if len(seconddoculects) >= lowerThreshold and len(seconddoculects) <= upperThreshold :
				cogIntersection = set(firstdoculects) & set(seconddoculects)
				cogUnion = set(firstdoculects) | set(seconddoculects)
				cogDistance = len(cogIntersection)/len(cogUnion)
				adjustedDistance = (len(cogIntersection) * cogDistance) / 53
	
				if len(seconddoculects) > 1 and len(cogIntersection) > 0:
	
					if not(secondconceptID + "_" + firstconceptID in seenPairs):
	
						cognetworkFile.write("\t".join((firstconceptID, secondconceptID, str(adjustedDistance))))
						cognetworkFile.write("\n")
						cogDistances.append([firstconceptID, secondconceptID, len(cogIntersection), cogDistance, adjustedDistance])
						seenPairs.append(firstconceptID + "_" + secondconceptID)
cognetworkFile.close()

#distanceDF = pd.DataFrame(cogDistances)			
#distanceDF.columns = ["ConceptID1","ConceptID2","Intersection","Distance","NormDistance"]

distanceGraph = networkx.Graph()
for i in range(len(cogDistances)):
    distanceGraph.add_edge(cogDistances[i][0], cogDistances[i][1], weight=cogDistances[i][4])

distanceDF = networkx.to_pandas_adjacency(distanceGraph)
distanceFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + "cogdistances" + ".tsv"
distanceFile = open(distanceFilename, "w")
distanceFile.write(distanceDF.to_csv(sep="\t"))
distanceFile.close()



"""
cogidDocSimilarity = { }
cogMileageChart = { }
for firstcog in cogidtoDoculects.keys():
	firstdoculects = cogidtoDoculects[firstcog]
	print("First:", firstdoculects)
	for secondcog in cogidtoDoculects.keys():
		seconddoculects = cogidtoDoculects[secondcog]
		overlap = len(list(set(firstdoculects) & set(seconddoculects)))
		print("Second:", seconddoculects, "Overlap: ", overlap)
		try:
			#print("Trying!")
			cogMileageLine = cogMileageChart[firstcog]
			cogMileageLine[secondcog] = overlap
			#print("Am I even trying?")
			#cogMileageChart[firstcog] = cogMileageLine
			print("MileageLine:", cogMileageLine)
		except: cogMileageChart[firstcog] = { firstcog : { secondcog: overlap} }
print(cogMileageChart)
"""