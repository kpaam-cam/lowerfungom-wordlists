# This script produces a series out outputs for examining the ways in which cognates
# bundle/group/etc with each other across doculects. That is, it "flips" the
# language-cognate relationship in comparison to the usual approach and is more like
# dialectology in some ways

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
base = importr('base')

# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

#analysesFolder = "../grollemund-wordlists/analyses"
#analysesSubfolder = ""
#filePrefix = "grollemund"

# Thresholds for for size of cognates sets to consider for some analyses since the numbers can be unwieldy
# This is to focus on cognate sets which match a minimum number of doculects but
# also do not match too many to get a kind of maximum possibility of interesting correlation
lowerThreshold = 0 # LF
upperThreshold = 53
#lowerThreshold = 20 # Grollemund
#upperThreshold = 400 # 282 corresponds to the doculects with 90 or more forms



# SCA and LexStat similarity thresholds, needed for file names, based on earlier lingpy
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")
cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
#cogType = "lexstatid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)


# Gather various kinds of information from the cognates table for later use
cogidtoDoculects = { }
cogidtoConcept= { }
concepttoCogid = { }
doculecttoCogids = { }
cogid_set = set()
doculect_set = set()
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

			try: doculecttoCogids[doculect].add(concept + "_" + str(cogid))
			except: doculecttoCogids[doculect] = { concept + "_" + str(cogid) }

			cogid_set.add(concept + "_" + str(cogid)) # get a big set of cogids for making a binary grid
			doculect_set.add(doculect)

		else:
			pass


# Find the ways that different cognates, across concepts, overlap with each other
# This is a lot of pairs, and, for each one, their overlap is stored
# Once these are collected, there is additional analysis
# crossCogs is for data tom make crosstables for cognates across concept pairs
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
				
				try: crossCogs[firstconcept + "_" + secondconcept].append([firstconceptID, secondconceptID, len(docIntersection)])
				except: crossCogs[firstconcept + "_" + secondconcept] = [ [firstconceptID, secondconceptID, len(docIntersection)] ]


###########################################################
### Create a large, binary coded cognate matrix ###
###########################################################

# Commented out since it was really slow for the Grollemund
"""
binMatrixFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-"+ "binMatrix" + ".tsv"
binMatrixFile = open(binMatrixFilename, "w")

coglist = list(cogid_set)
coglist.sort()
doculist = list(doculect_set)
doculist.sort()
headerstring = ""
outputstring = ""
for doculect in doculist:

	docCogIds = doculecttoCogids[doculect]

	outputstring = outputstring + "\n" + doculect
	for cogid in coglist:	

		headerstring = headerstring + "\t" + cogid 

		if cogid in docCogIds: presence = "1"
		else: presence = "0"
		
		outputstring = outputstring + "\t" + presence

outputstring = headerstring + outputstring
binMatrixFile.write(outputstring)
"""
			


#########################################################
### Concept-by-concept analysis using chi-square area ###
#########################################################

"""
# First, we'll look at the distributions across cognates across a pair of concepts
# We'll see which ones show significant imbalances following a chi-square test, and
# then use the p-values and other values to look for correlations, etc.
# For now, this is done via clustering in R

# File output for concept pairs with significant chi-square results
sigFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-"+ "sigChiSq" + ".tsv"
sigFile = open(sigFilename, "w")
sigFile.write("ConceptA\tConceptB\tChisqPvalue\n")

# File output for residuals within chi-square tables that are themselves significant
# to see which cells seem to be contributing (using a 2 threshold)
sigCogResidualsFileName = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-"+ "sigCogRes" + ".tsv"
sigCogResidualsFile = open(sigCogResidualsFileName, "w")
sigCogResidualsFile.write("ConceptA\tConceptB\tChisqResidual\tNumForms\n")

# Run through the paired cognate sets and start gathering reports

# The first set of analyses and reports focusing on a chi-square analysis of
# cognate distribution across cognate pairs. This helps look for imbalances in this
# patterns and hopefully find "bundled" cognates

header = ["CognateA", "CognateB", "Overlap" ]
chisqs = [ ]
chisqsbyconcept = { }
for crossCog in crossCogs:
	
	intersections = crossCogs[crossCog]
	firstconcept, secondconcept = crossCog.split("_")

	intersectionsDF = pd.DataFrame(intersections, columns = header)
	
	# Turn the overlaps in list form into a cross-tab for chi-square
	# An aggfunc is required by the method, but the data doesn't need one
	# since each pairing is unique (due the data creation).
	# mean is used as the function just for a placeholder.
	# It's vacuous as a mean of a set of one item.
	intersectionsCT = pd.crosstab(intersectionsDF["CognateA"], intersectionsDF["CognateB"], values = intersectionsDF["Overlap"], aggfunc='mean')
	
	# This is rpy2 code to get ready to send data to R,
	# which has a better chisq.test for this data (simulated p value possible)
	# This makes things more complicated, but we need that functionality for this data
	with localconverter(ro.default_converter + pandas2ri.converter):
		intersectionsR_df = ro.conversion.py2rpy(intersectionsCT)
	
	# Send the cross-tab to R and do a chi-square test
	rdatamatrix = ro.r['data.matrix']
	rchisquare = ro.r['chisq.test']
	intersectionsMatrix = rdatamatrix(intersectionsR_df)
	# The main part of the analysis
	intersectionchisq = rchisquare(intersectionsMatrix, simulate_p_value=True, B=2000)

	# Getting data out of R
	# Worked out these by trial and error
	# In R, one can play with indices of the object to see where the data is
	# but R's object is one-indexed, not zero-indexed. So, adjustment needed
	# I did not know how to access information through named categories in R via rpy2
	chisqvalue = intersectionchisq[0][0]
	dfvalue = intersectionchisq[1][0]
	pvalue = intersectionchisq[2][0]

	# Hacky code to get the residuals table, including the column and row names
	# Could not find better solution vis rpy2 interface
	# Found the private methods via python code to print out available methods rather than
	# actual documentation
	residuals = intersectionchisq[7]
	residuals_numbers = np.asarray(intersectionchisq[7])
	
	# Had an issue when there was only one cognate set (e.g., lexstat 'ear')
	try: residuals_columns =  residuals._Matrix__colnames_get()
	except:
		print("Skipping pair due to lack of cognate variation: ", crossCog)
		continue
	
	residuals_rows = residuals._Matrix__rownames_get()
	residuals_rows_df = pd.DataFrame(data=residuals_numbers, index=residuals_rows, columns=residuals_columns)
	
	# Report out which chisqs are above .05 significance for later examination
	if pvalue <= .05:
		sigFile.write(firstconcept + "\t" + secondconcept + "\t" + str(pvalue) + "\n")
		
		# If the chi square is signficant, see what cells might be contributing
		# Could not find a way to get all relevant information from data frame without
		# cycling through each cell
		for res_row in residuals_rows:
			for res_column in residuals_columns:
				cell = residuals_rows_df.loc[res_row, res_column]
				if abs(cell) >= 2: # Using +2 or -2 as a quasi-standard cut off
					numofForms = intersectionsCT.loc[res_row, res_column]
					sigCogResidualsFile.write(res_row + "\t" + res_column + "\t" + str(cell) + "\t" + str(numofForms) + "\n")


	# Hack to exclude NaN's from clustering analysis,
	# some chisq's can't be done since expected value is 0
	# Make the NaN's "in the middle" (otherwise they become "0")
	if pvalue != pvalue:
		pvalue = 0.0078 # Rough average of non-NaN values for Grollemund; have yet to test LF (will need adjustment)
	else: pass
			
	# A few concepts with very low chisq p-values, mostly cases where one cognate dominates the data, skew the 
	# cluster viewing. I'm using square root to adjust that. No idea if that's the right approach,
	# but it helps with visualization
	chisqs.append([firstconcept, secondconcept, sqrt(pvalue)])

	# Some dictionaries to create reports further down in the code
	try: chisqsbyconcept[firstconcept].append(pvalue)
	except: chisqsbyconcept[firstconcept] = [ pvalue ]
	try: chisqsbyconcept[secondconcept].append(pvalue)
	except: chisqsbyconcept[secondconcept] = [ pvalue ]

sigFile.close()
sigCogResidualsFile.close()



# Turn all of the paired ConceptA, ConceptB, chisq lists into a matrix
# First create a graph, and then use that to create an adjacency matrix via Pandas
# This idea came somewhere (unrecorded) from Stack Overflow
chisqGraph = networkx.Graph()
for i in range(len(chisqs)):
    chisqGraph.add_edge(chisqs[i][0], chisqs[i][1], weight=chisqs[i][2])
chisqGraphDF = networkx.to_pandas_adjacency(chisqGraph)

# Write out the adjacency matrix for R processing later on
chisqFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-" + "chisq" + ".tsv"
chisqFile = open(chisqFilename, "w")
chisqFile.write(chisqGraphDF.to_csv(sep="\t"))
chisqFile.close()

# Report average p-values for each concept as a kind of global summary
pValueFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + "-" +  "crossCogPValues" + ".tsv"
pValueFile = open(pValueFilename, "w")
pValueFile.write("Concept\tAverageChisqPvalue\n")
for chisqbyconcept in chisqsbyconcept:
	pvalues = chisqsbyconcept[chisqbyconcept]
	pValueFile.write(chisqbyconcept + "\t" + str(statistics.mean(pvalues)) + "\n")
pValueFile.close()
	
###################################
### Cognate by cognate analysis ###
###################################


# File for creating report of network of cognate overlaps
cognetworkFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + str(lowerThreshold) + str(upperThreshold) + "-" + "cognetwork" + ".tsv"
cognetworkFile = open(cognetworkFilename, "w")
cognetworkFile.write("\t".join(("Cognate1", "Cognate1", "Weight")))
cognetworkFile.write("\n")

"""

# Get information to create a cognate-by-cognate network (across all concepts)
# This is such a large operation that some optimization was actually needed
seenPairs = [ ]
cogDistances = [ ]
for firstcog in cogidtoDoculects.keys():

	firstconceptID, firstconcept = cogidtoConcept[firstcog]
	firstdoculects = cogidtoDoculects[firstcog]

	# Imposing some limits for manageability, also done below
	if len(firstdoculects) >= lowerThreshold and len(firstdoculects) <= upperThreshold:

		for secondcog in cogidtoDoculects.keys():
			secondconceptID, secondconcept = cogidtoConcept[secondcog]
			if firstconcept == secondconcept: # this is a vacuous case, skip
				continue
			seconddoculects = cogidtoDoculects[secondcog]

			# Imposing some limits for manageability, also done above
			if len(seconddoculects) >= lowerThreshold and len(seconddoculects) <= upperThreshold :

				# Measure simularity using the simUI union/intersection calculation
				# Obviously there may be better metrics out there
				cogIntersection = set(firstdoculects) & set(seconddoculects)
				intersectionSize = len(cogIntersection) # we'll need this later
				cogUnion = set(firstdoculects) | set(seconddoculects)
				cogDistance = len(cogIntersection)/len(cogUnion)

				# Experimented with an adjusted distance to weight cases with a larger
				# intersction higher, but it resulted in different kinds of data being
				# grouped. So, I don't use this, but I like the idea of an adjusted
				# distance someday and am leaving this as a reminder
				adjustedDistance = (intersectionSize * cogDistance) / 100
	
				# Can't have a zero edge value for some purposes
				if intersectionSize > 0:
					pass
				else:
					#intersection = .00001 # small filler
					continue # (or we could skip this edge entirely)
				
				# Save time/space by not processing the reverse version of pairs already seen
				# All edge weights are symmetric
				if not(secondconceptID + "_" + firstconceptID in seenPairs):
					#cognetworkFile.write("\t".join((firstconceptID, secondconceptID, str(cogDistance))))
					#cognetworkFile.write("\n")
					cogDistances.append([firstconceptID, secondconceptID, intersectionSize, cogDistance, adjustedDistance])
					seenPairs.append(firstconceptID + "_" + secondconceptID)

cognetworkFile.close()

# Turn all of the paired ConceptA, ConceptB, distances lists into a matrix
# First create a graph, and then use that to create an adjacency matrix via Pandas
# This idea came somewhere (unrecorded) from Stack Overflow
# Using unweighted cog pair distance (position 4/index 3) of list created above
distanceGraph = networkx.Graph()
for i in range(len(cogDistances)):
    distanceGraph.add_edge(cogDistances[i][0], cogDistances[i][1], weight=cogDistances[i][4])

# Write out the adjacency matrix for R processing later on
distanceDF = networkx.to_pandas_adjacency(distanceGraph)
distanceFilename = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + cogType + str(lowerThreshold) + str(upperThreshold) + "-" +  "wghtdcogdistances" + ".tsv"
distanceFile = open(distanceFilename, "w")
distanceFile.write(distanceDF.to_csv(sep="\t"))
distanceFile.close()



"""
# Old code that didn't work but left it around in case I wanted to look at it again
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