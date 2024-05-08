# This is to see how cognates group with respect to doculects

from lingpy import Wordlist
import pandas as pd
import numpy as np
import networkx
import os
from math import sqrt
import statistics

# See: https://rpy2.github.io/doc/v3.3.x/html/pandas.html
import rpy2
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

#analysesFolder = "../grollemundTest/analyses"
#analysesSubfolder = ""
#filePrefix = "grollemund"


# SCA and LexStat similarity thresholds, needed for field names
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")

cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)


# Gather the relevant information from the cognates table
cogidtoDoculects = { }
cogidtoConcept= { }
concepttoCogid = { }
for id, reflexes in etd.items():
	for reflex in reflexes:

		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType] # actually same as ID, fix later
			cogidtoConcept[cogid] = [ concept + "_" + str(cogid), concept ]

			try: cogidtoDoculects[cogid].append(doculect)
			except: cogidtoDoculects[cogid] = [doculect]

			try: concepttoCogid[concept].add(cogid)
			except: concepttoCogid[concept] = { cogid }

		else:
			pass




# Distributions within cognates
# I seem to now collect the matches as pairss.
# Now I need to collect them and turn them into a matrix, cycle through and set up chisqure
crossCogs = { }
for firstconcept in concepttoCogid.keys():

	firstcogids = concepttoCogid[firstconcept]

	for secondconcept in concepttoCogid.keys():

		if firstconcept == secondconcept:
			continue
		elif secondconcept + "_" + firstconcept in crossCogs:
			continue

		secondcogids = concepttoCogid[secondconcept]

		for firstcogid in firstcogids:
			
			firstcogidDoculects = cogidtoDoculects[firstcogid]
			firstconceptID, firstconcept = cogidtoConcept[firstcogid]
			
			for secondcogid in secondcogids:

				secondcogidDoculects = cogidtoDoculects[secondcogid]
				secondconceptID, secondconcept = cogidtoConcept[secondcogid]

				docIntersection = list(set(firstcogidDoculects) & set(secondcogidDoculects))
				#print(firstconceptID, secondconceptID, len(docIntersection))
				
				try: crossCogs[firstconcept + "_" + secondconcept].append([firstconceptID, secondconceptID, len(docIntersection)])
				except: crossCogs[firstconcept + "_" + secondconcept] = [ [firstconceptID, secondconceptID, len(docIntersection)] ]

		#print("")

header = ["CognateA", "CognateB", "Overlap" ]
chisqs = [ ]

# Need concept-level metric, and compare with entropy
# Here we look to see which concepts show how inter-concept correlation via chi-square
# Set up plot by p-value similarity. Making this all up as I go along
chisqsbyconcept = { }
for crossCog in crossCogs:
	
	intersections = crossCogs[crossCog]
	firstconcept, secondconcept = crossCog.split("_")

	intersectionsDF = pd.DataFrame(intersections, columns = header)
	#print(intersectionsDF.to_csv(sep="\t"))
	
	# Turning the overlaps into a cross-tab for chi-square
	# An aggfunc is required, but the data doesn't need one since each pairing is unique (due the data creation). Mean is just a placeholder
	intersectionsCT = pd.crosstab(intersectionsDF["CognateA"], intersectionsDF["CognateB"], values = intersectionsDF["Overlap"], aggfunc='mean')
	#print(intersectionsCT.to_csv(sep="\t"))
	
	# This is rpy2 code to get ready to send calculates to R, which has a better chisq.test for this data (simulated p value possible)
	with localconverter(ro.default_converter + pandas2ri.converter):
		intersectionsR_df = ro.conversion.py2rpy(intersectionsCT)
	
	# Working with R
	rdatamatrix = ro.r['data.matrix']
	rchisquare = ro.r['chisq.test']
	intersectionsMatrix = rdatamatrix(intersectionsR_df)
	
	intersectionchisq = rchisquare(intersectionsMatrix, simulate_p_value=True, B=1000)
	
	# Getting data out of R
	chisqvalue = intersectionchisq[0][0] # Worked out these by trial and error. Maybe a better way exists
	dfvalue = intersectionchisq[1][0]
	pvalue = intersectionchisq[2][0]
	
	# Hack to exclude NaN's, some chisq's can't be done since expected value is 0
	# Make the NaN's "in the middle" (otherwise they become "0")
	if pvalue != pvalue:
		pvalue = .05
		
	#print(firstconcept, secondconcept, pvalue, sep="\t")
	# A few concepts with low chisq values, mostly cases where one cognate dominates the data, skew the 
	# cluster viewing. I'm using square root to adjust that. No idea if that's the right approach,
	# but it helps with visualization
	chisqs.append([firstconcept, secondconcept, sqrt(pvalue)]) # trying sqrt to deal with scaling
	try:
		chisqsbyconcept[firstconcept].append(pvalue)
		chisqsbyconcept[secondconcept].append(pvalue)
	except:
		chisqsbyconcept[firstconcept] = [ pvalue ]
		chisqsbyconcept[secondconcept] = [ pvalue ]
		
			
chisqGraph = networkx.Graph()
for i in range(len(chisqs)):
    chisqGraph.add_edge(chisqs[i][0], chisqs[i][1], weight=chisqs[i][2])

chisqGraphDF = networkx.to_pandas_adjacency(chisqGraph)
chisqFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + "chisq" + ".tsv"
chisqFile = open(chisqFilename, "w")
chisqFile.write(chisqGraphDF.to_csv(sep="\t"))
chisqFile.close()

# Averaging p-values for each concept as a kind of summary
for chisqbyconcept in chisqsbyconcept:
	pvalues = chisqsbyconcept[chisqbyconcept]
	print(chisqbyconcept, statistics.mean(pvalues), sep="\t")
	


"""
# Do some similarity metrics across cognates
lowerThreshold = 10
upperThreshold = 300

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
				adjustedDistance = (len(cogIntersection) * cogDistance) / 100
	
				if len(seconddoculects) > 1 and len(cogIntersection) > 0:
	
					if not(secondconceptID + "_" + firstconceptID in seenPairs):
	
						cognetworkFile.write("\t".join((firstconceptID, secondconceptID, str(adjustedDistance))))
						cognetworkFile.write("\n")
						cogDistances.append([firstconceptID, secondconceptID, len(cogIntersection), cogDistance, adjustedDistance])
						print(firstconceptID, secondconceptID, len(cogIntersection), cogDistance, adjustedDistance, sep="\t")
						seenPairs.append(firstconceptID + "_" + secondconceptID)
cognetworkFile.close()

#distanceDF = pd.DataFrame(cogDistances)			
#distanceDF.columns = ["ConceptID1","ConceptID2","Intersection","Distance","NormDistance"]

# abandoning weighted distance since that seems to distort data
distanceGraph = networkx.Graph()
for i in range(len(cogDistances)):
    distanceGraph.add_edge(cogDistances[i][0], cogDistances[i][1], weight=cogDistances[i][3])

distanceDF = networkx.to_pandas_adjacency(distanceGraph)
distanceFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + "cogdistances" + ".tsv"
distanceFile = open(distanceFilename, "w")
distanceFile.write(distanceDF.to_csv(sep="\t"))
distanceFile.close()




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