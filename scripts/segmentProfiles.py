import pandas as pd
import os
#from collections import defaultdict
  
import numpy as np
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine

 
# Storage folders
cldfFolder = "../cldf"
file= "forms.csv"


# Just what are we coding in this file?
forms = pd.read_csv(cldfFolder + os.sep + file)

segmentSet = set()
doculectSet = set()
for index, row in forms.iterrows():

	doculect = row["Language_ID"]

	segments = row["Segments"]	
	segmentList = segments.split(" ")
	
	for segment in segmentList:
		segmentSet.add(segment)
		
	doculectSet.add(doculect)

allSegments = sorted(list(segmentSet))
allDoculects = sorted(list(doculectSet))

# Initialize 0 seg counts across all segments
docSegCounts = { }
for doculect in allDoculects:
	segCounts = { }
	for segment in allSegments:
		segCounts[segment] = 0
	docSegCounts[doculect] = segCounts

for index, row in forms.iterrows():

	doculect = row["Language_ID"]

	segments = row["Segments"]	
	segmentList = segments.split(" ")
	
	for segment in segmentList:
		docSegCounts[doculect][segment] += 1	


# Double check ordering, but I think OK
segCountMatrix = [ ]
for doculect in docSegCounts.keys():
	segCountList = [ ]
	segCounts = docSegCounts[doculect]
	for segment in segCounts:
		segCount = segCounts[segment]
		segCountList.append(segCount)
	segCountMatrix.append(segCountList)

segCountArray = np.array(segCountMatrix)
segCountDF = pd.DataFrame(segCountArray, columns=allSegments, index=allDoculects)

segDists = 1-pairwise_distances(segCountArray, metric="cosine")
segDistsDF = pd.DataFrame(segDists, columns=allDoculects, index=allDoculects)

segDistsDF.to_csv("../analyses/Phase3a-Fall2023/segmentProfiles-LF.tsv", sep="\t" )

#print(docSegCounts)



#print(segmentList)

#for segment in segmentSet:
#	print(segment)		

#for doculect in doculectSet:
#	print(doculect)		
		
