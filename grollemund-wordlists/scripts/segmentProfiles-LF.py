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
segDists = pairwise_distances(docSegCountsDF, metric="cosine")
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

# Make a file of zscores that exceed the absolute value for 2
compiledzscores = ""
highestsaliencescores = "Doculect\tSegment\tZscore\tNormedcount\tSalienceScore\n"
allsaliencescores = "Doculect\tSegment\tZscore\tNormedcount\tSalienceScore\n"
for doculect, segzscores in segszscores.iterrows():

	compiledzscores += doculect + "\n"
	compiledzscores += "Segment\tZscore\tNormedcount\tSalienceScore\n"

	highzscores = [ ]
	for seg, zscore in segzscores.items():

		normedSegCount = normedSegCountsDF[seg][doculect]
		salienceScore = zscore * normedSegCount # I am making this up
		segmentInfo = [ seg, round(zscore, 2), normedSegCount, round(salienceScore) ]
		allsaliencescores += doculect + "\t" + "\t".join(map(str, segmentInfo)) + "\n" # this repeats some code below, not ideal
		
		# For tracking high salience segments, make a special file
		if abs(zscore) > 2:
			highzscores.append(segmentInfo)

	# Sort by last element of list, salienceScore
	highzscores.sort(key=lambda x: abs(x[3]), reverse=True)

	for segmentInfo in highzscores:
		compiledzscores += "\t".join(map(str, segmentInfo)) + "\n"
	compiledzscores += "\n"

	# Get highest for this doculect
	highestsaliencescore = "\t".join(map(str, highzscores[0]))
	highestsaliencescore = doculect + "\t" + highestsaliencescore + "\n"
	highestsaliencescores += highestsaliencescore

print(compiledzscores, file=open("../analyses/segments/segmentZScores-LF.tsv", "w"))
print(highestsaliencescores, file=open("../analyses/segments/highestSalienceScores-LF.tsv", "w"))
print(allsaliencescores, file=open("../analyses/segments/allSalienceScores-LF.tsv", "w"))


# Make a file of segment with highest z-score for each language (partly redundant with above for readability)
## Made unnecessary by adjustments to above code done for other reasons
# highestzscores = "Doculect\tSegment\tZscore\n"
# for doculect, segzscores in segszscores.iterrows():
# 	compiledzscores += doculect + "\n"
# 	highestzscore = 0
# 	workingzscore = 0 # keep the sign
# 	for seg, zscore in segzscores.items():
# 		if abs(zscore) > highestzscore:
# 			highestzscore = abs(zscore)
# 			workingzscore = zscore # keep the sign
# 			highestseg = seg
# 	highestzscores += "\t".join([ doculect, highestseg, str(round(workingzscore, 2)) ] ) + "\n"
# print(highestzscores, file=open("../analyses/segments/highestZScores-LF.tsv", "w"))
