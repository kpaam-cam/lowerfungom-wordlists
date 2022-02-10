from lingpy import *
from collections import defaultdict
import pprint
import numpy
from math import log, e
import pandas


# Adapted from https://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python
# We'll use entropy to get a calculation of the coherence of a list
# It will be normalized by maximum possible entropy of list of same length
# We'll subtract from one to get a "coherence" score
def cogEntropy(cogs):
	
	numCogs = len(cogs)
	if numCogs <= 1:
		return 1
	
	uniques,counts = numpy.unique(cogs, return_counts=True)
	
	probs = counts / numCogs
	
	# While the count_nonzero function is used, there are, in actuality, never any zeros in the data; so this is just a regular count
	classes = numpy.count_nonzero(probs)
	if classes <= 1:
		return 1
	
	ent = 0.
	# Compute entropy
	base = e
	for x in probs:
		ent -= x * log(x, base)

	# Get entropy of a maximally informative list of same size
	# This reduces to the log of size of the list (see https://math.stackexchange.com/questions/395121/how-entropy-scales-with-sample-size)
	maxEnt = log(numCogs)
	normalizedEnt = ent/maxEnt
	stability = round((1 - normalizedEnt), 10)

	return stability
	
filePath = "../analyses/Phase2-NewLists/"
wl = Wordlist(filePath + 'AllAvailableNew-37coverage.tsv-cognates-0.45_0.55thresholds.tsv')
langs = csv2list('../cldf/languages.csv', sep=",")

# make dictionary to get the groups quickly from a language name
lang2group = {k[0]: k[2] for k in langs[1:]}


# Using SCAID for this
etd = wl.get_etymdict(ref="scaid")

stabilityDict = { }
conceptStabilityDict = { }
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			# Using SCAID for this
			cogid = wl[reflex[0], 'scaid']
			variety = lang2group[wl[reflex[0], 'doculect']]
			
			if variety in stabilityDict:
				varietyStability = stabilityDict[variety]
				if concept in varietyStability:
					cogList = varietyStability[concept]
					cogList.append(cogid)
					varietyStability[concept] = cogList
				else:
					varietyStability[concept] = [cogid]
			else:
				varietyStability = { }
				varietyStability[concept] = [cogid]
				stabilityDict[variety] = varietyStability
				
			if concept in conceptStabilityDict:
				conceptCogList = conceptStabilityDict[concept]
				conceptCogList.append(cogid)
				conceptStabilityDict[concept] = conceptCogList
			else:
				conceptStabilityDict[concept] = [cogid]
				
#print(stabilityDict)

#varietiesStability = 
varietyStabilities = [ ]
for variety in stabilityDict:
	varietyStability = stabilityDict[variety]
	for concept in varietyStability:
		cogList = varietyStability[concept]
		if len(cogList) == 4:
			# Who knows how to calculate this? I'm just guessing
			# cogSet = set(cogList)
			# stability = (len(cogList)-len(cogSet))/(len(cogList)-1)
			#print(variety,concept,stability, sep="\t")
			stability = cogEntropy(cogList) # trying an entropy-based approach	
			varietyStability_forDf = { }
			varietyStability_forDf['Variety'] = variety
			varietyStability_forDf['Concept'] = concept
			varietyStability_forDf['Stability'] = stability
			varietyStabilities.append(varietyStability_forDf)
varietyStabilities_df = pandas.DataFrame(varietyStabilities).sort_values(['Stability', 'Variety'], ascending=[False, True])
#print(varietyStabilities_df)
varietyStabilities_df.to_csv(filePath + "ConceptStabilityByVariety.tsv", sep="\t", index=False,)		
			
#print(conceptStabilityDict)

conceptStabilities = [ ]
for concept in conceptStabilityDict:
	cogList = conceptStabilityDict[concept]
	stability = cogEntropy(cogList)
	#print(concept,stability, sep="\t")
	conceptStability_forDf = { }
	conceptStability_forDf['Concept'] = concept
	conceptStability_forDf['Stability'] = stability
	conceptStabilities.append(conceptStability_forDf)
conceptStabilities_df = pandas.DataFrame(conceptStabilities).sort_values(['Stability', 'Concept'], ascending=[False, True])
conceptStabilities_df.to_csv(filePath + "ConceptStabilityByConcept.tsv", sep="\t", index=False,)		



