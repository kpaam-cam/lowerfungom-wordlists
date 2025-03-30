import pandas as pd
import os
#from collections import defaultdict
  
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from scipy import stats

 
# Storage folders
cldfFolder = "../cldf"
file= "forms.csv"


allforms = pd.read_csv(cldfFolder + os.sep + file)
forms = allforms # default

# Get list of all segments and doculects
segmentSet = set()
doculectSet = set()
for index, row in forms.iterrows():
	doculect = row["Language_ID"]
	segments = row["Segments"]	
	segmentList = segments.split(" ")
	
	for segment in segmentList:
		segmentSet.add(segment)
		
	doculectSet.add(doculect)

allSegments = sorted(list(segmentSet)) # types not tokens
allDoculects = sorted(list(doculectSet))
totalDoculects = len(allDoculects)


# Initialize 0 seg counts across all segments to fill out values
# This step is needed since we are working with phones rather than phonemes and want to track missing phones in a doculect
# Useful side effect is that keys are ordered
docSegCounts = { }
for doculect in allDoculects:
	segCounts = { }
	for segment in allSegments:
		segCounts[segment] = 0
	docSegCounts[doculect] = segCounts

# Get segment counts for each doculect
totalSegs = 0 # track all segs in dataset for normalization, tokens not types
for index, row in forms.iterrows():
	doculect = row["Language_ID"]
	segments = row["Segments"]	
	segmentList = segments.split(" ")
	for segment in segmentList:
		docSegCounts[doculect][segment] += 1
		totalSegs += 1

# Create dataframe of counts		
segDocCountsDF = pd.DataFrame(docSegCounts)
docSegCountsDF = segDocCountsDF.T


# Create normalized dataframe, expressed as numbers of segments
segSums = docSegCountsDF.sum(axis=1) # sum across rows
normedSegCountsDF = docSegCountsDF.div(segSums, axis=0) # divide rows by sums (I can't wrap my head around axis)
normedSegCountsDF = normedSegCountsDF.mul(totalSegs/totalDoculects, axis=0) # normalize
normedSegCountsDF = normedSegCountsDF.round(0).astype(int) # clean up

# To check distributions
normedSegCountsDF.T.to_csv("../analyses/segments/normedSegmentCounts-LF.tsv", sep="\t")

# Preparatory work is done, now make calculations

# Cosine similarity
segDists = 1-pairwise_distances(docSegCountsDF, metric="cosine")
segDistsDF = pd.DataFrame(segDists, columns=allDoculects, index=allDoculects)
segDistsDF.to_csv("../analyses/segments/segmentProfiles-LF.tsv", sep="\t", float_format='%.9f' ) # had some weird floating point issue where 1 == .99999

# Write it out in a three-column format to see which are most similar/different and how much
doculectPairs = [ ]
for i in range(len(segDistsDF.columns)):
    for j in range(i + 1, len(segDistsDF.columns)):
        doculectPairs.append([segDistsDF.index[i], segDistsDF.columns[j], segDistsDF.iloc[i, j]])
doculectPairsDF = pd.DataFrame(doculectPairs, columns=['Doculect1', 'Doculect2', 'cosDistance']).sort_values(by='cosDistance', ascending=False)
doculectPairsDF.to_csv("../analyses/segments/segmentProfilesByPair-LF.tsv", sep="\t", float_format='%.9f' )


# Find distinctive segments
segvariances = normedSegCountsDF.var()
segstdevs = normedSegCountsDF.std().round().astype(int)
segszscores = normedSegCountsDF.apply(stats.zscore)

# segstdevs is a Series object; do some manipulations for the output
segstdevs = segstdevs.sort_values(ascending=False)
segstdevsDF = pd.DataFrame({"Segment": segstdevs.index, "STDev": segstdevs.values})
segstdevsDF.to_csv("../analyses/segments/segmentSTDevs-LF.tsv", sep="\t", index=False)

# Make a file of zscores
compiledzscores = ""
for doculect, segzscores in segszscores.iterrows():
	compiledzscores += doculect + "\n"
	for seg, zscore in segzscores.items():
		if abs(zscore) > 2:
			compiledzscores += "\t".join([ seg, str(round(zscore, 2)), str(normedSegCountsDF[seg][doculect]) ] ) + "\n"
	compiledzscores += "\n"
print(compiledzscores, file=open("../analyses/segments/segmentZScores-LF.tsv", "w"))