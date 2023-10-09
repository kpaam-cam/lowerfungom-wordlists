"""
Testing script for some R analyses, copies, reduces, and extends analyze.py
"""

from lingpy import *
from lexibank_kpaamcamlowerfungom import Dataset
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
from lingpy.convert.strings import write_nexus
import pandas
import numpy
from math import log, e
import os


def run(args):
    
	# Storage folders
	analysesFolder = "analyses"
	analysesSubfolder = "Phase3a-Fall2023"
	filePrefix = "kplfSubset"

	# SCA and LexStat similarity thresholds
	SCAthreshold = 0.45
	LSthreshold = 0.55

	KPLF = Dataset()

	# Load stored cognates to calculate stabilities
	wl = Wordlist(KPLF.dir.joinpath(
               		analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv").as_posix())
	
	# make dictionary to get the groups quickly from a language name
	langs = csv2list(KPLF.dir.joinpath("cldf",  "languages.csv"), sep=",")
	lang2group = {k[0]: k[2] for k in langs[1:]}


	cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
	etd = wl.get_etymdict(ref=cogType)

	# Make two dictionaries, one for stability just for a concept, regardless of variety
	# The other does this within a variety, though this is less informative at the moment given how few doculects we have for each variety
	stabilityDict = { }
	conceptStabilityDict = { }
	for id, reflexes in etd.items():
		for reflex in reflexes:
			if reflex:
				doculect = wl[reflex[0], 'doculect']
				concept= wl[reflex[0], 'concept']
				cogid = wl[reflex[0], cogType]
				variety = lang2group[wl[reflex[0], 'doculect']]
			
				# Make the stability by variety dictionary
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
					
				# Make the stability by concept dictionary				
				if concept in conceptStabilityDict:
					conceptCogList = conceptStabilityDict[concept]
					conceptCogList.append(cogid)
					conceptStabilityDict[concept] = conceptCogList
				else:
					conceptStabilityDict[concept] = [cogid]
				

	# Do the entry calculations by concept within each variety
	varietyStabilities = [ ]
	for variety in stabilityDict:
		varietyStability = stabilityDict[variety]
		for concept in varietyStability:
			cogList = varietyStability[concept]
			
			# Only do this if we have at least four doculects for a variety
			if len(cogList) >= 4:
				stability = cogEntropy(cogList) # trying an entropy-based approach	
				# Create a dictionary that will be used to create a data fram for export via Pandas
				varietyStability_forDf = { }
				varietyStability_forDf['Variety'] = variety
				varietyStability_forDf['Concept'] = concept
				varietyStability_forDf['Stability'] = stability
				varietyStabilities.append(varietyStability_forDf)
	
	varietyStabilities_df = pandas.DataFrame(varietyStabilities).sort_values(['Stability', 'Variety'], ascending=[False, True])
	varietyStabilities_df.to_csv(KPLF.dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-conceptStabilityByVariety" + ".tsv").as_posix(),
					sep="\t", index=False,)
			
	
	# Do the entry calculations by concept across varieties
	conceptStabilities = [ ]
	for concept in conceptStabilityDict:
		cogList = conceptStabilityDict[concept]
		stability = cogEntropy(cogList)
		
		# Create a dictionary that will be used to create a data fram for export via Pandas
		conceptStability_forDf = { }
		conceptStability_forDf['Concept'] = concept
		conceptStability_forDf['Stability'] = stability
		conceptStabilities.append(conceptStability_forDf)
	
	conceptStabilities_df = pandas.DataFrame(conceptStabilities).sort_values(['Stability', 'Concept'], ascending=[False, True])
	conceptStabilities_df.to_csv(KPLF.dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-conceptStabilityByConcept" + ".tsv").as_posix(),
					sep="\t", index=False,)		

	args.log.info("Calculating cognate homogeneities")


	# To do: Can I fix the HTML output (maybe with different orth profile?)
	# Check duplicate for coffin and handle and delete
	# Clean things?
	# Change wordlist creation tool in Scripts to add variety to each doculect (e.g., Missong, Abar, etc., so that that goes into the CLDF, per Mattis's suggestion)
	# Map concepts with pysem someday
	# reimplement Forkel solution to grabbing first form only but CLDFing all forms?
	
	# clean up way concepts.tsv is made in /etc. Hacked now. Needs standardized. See "new" concepts added at end for senese of problem (triggered by new Biya lists); not sure why didn't happen before--or did I I forget?
	
	# Add information about the speakers!

	args.log.info("Computed alignments and wrote them to file along with other analytical outputs")


	# Make a "turned" table for analysis of cognate predicatability of languoid
	# First, get a dictionary that takes a doculect and links to all cogids associated with the doculect
	doculectCognateDict = { }
	cogids = []
	for id, reflexes in etd.items():
		for reflex in reflexes:
			if reflex:
				doculect = wl[reflex[0], 'doculect']
				concept= wl[reflex[0], 'concept']
				cogid = wl[reflex[0], cogType] # actually same as ID, fix later
				try: doculectCognateDict[doculect].append(cogid)
				except: doculectCognateDict[doculect] = [cogid]
			else:
				pass
		# build up a list of cognate ids
		cogids.append(id)
	
	cogids.sort()
	
	#make header
	rfoutput = ""
	rfheader = "Doculect\tCog"
	cogidString = [str(i) for i in cogids]
	rfheader += "\tCog".join(cogidString)
	rfoutput += rfheader + "\n"
	
	# run through each doculect and spit out presence/absence table
	counter = 1 # to create CSV that can be an R dataframe with an ID if needed
	for doculect in doculectCognateDict.keys():
		docCogs = doculectCognateDict[doculect]
		doculectLine = doculect
		for cogid in cogids:
			doculectLine += "\t"
			if cogid in docCogs:
				doculectLine += str(1) 
			else:
				doculectLine += str(0)
		doculectLine += "\n"
		rfoutput += doculectLine
		counter = counter + 1
	
	preAbsFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates-PresAbsence" + ".tsv", "w")
	preAbsFile.write(rfoutput)

	args.log.info("Created cognates presence/absence table for each doculect")


	# Now make a shared cognate across varieties data object to create a network structure
	netFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates-Network" + ".tsv", "w")

	netFile.write("Doculect1\tDoculect2\tSharedCognateCount\n")

	calculatedDoculects = set()
	for doculectMain in sorted(doculectCognateDict.keys()):
		docCogsMain = doculectCognateDict[doculectMain]
		for doculectComp in sorted(doculectCognateDict.keys()):
			if doculectComp == doculectMain: pass
			elif doculectComp in calculatedDoculects: pass
			else:
				docCogsComp = doculectCognateDict[doculectComp]
				overlap = sum(1 for element in docCogsMain if element in docCogsComp)
				netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\n")
		calculatedDoculects.add(doculectMain)

	args.log.info("Created network file for each doculect")



# Todo: 3.10.2023 Incorporate intom main analyze.py

# From Hantgan and List paper
def make_matrix(ref, wordlist, tree, tree_taxa):
    
    matrix = [[1 for i in tree_taxa] for j in tree_taxa]
    for i, tA in enumerate(tree_taxa):
        for j, tB in enumerate(tree_taxa):
            if i < j:
                cogsA = wordlist.get_dict(col=tA, entry=ref)
                cogsB = wordlist.get_dict(col=tB, entry=ref)
                shared, slots = 0, 0
                for key in set([k for k in cogsA] + [k for k in cogsB]):
                    if key in cogsB and key in cogsA:
                        if [c for c in cogsA[key] if c in cogsB[key]]:
                            shared += 1
                        slots += 1

                matrix[i][j] = shared / slots
                matrix[j][i] = shared / slots
    return matrix

# From Hantgan and List paper
def load_matrix(fname):
    data = csv2list(fname)
    taxa = [line[0].strip() for line in data]
    matrix = [[0 for i in taxa] for j in taxa]
    for i in range(len(taxa)):
        for j in range(1, len(taxa)+1):
            matrix[i][j-1] = float(data[i][j])
    return taxa, matrix

# By me originally to create a SplitsTree file, but there's a built-in function for this.
# So, I've adapted this to make a file to load into R as a matrix
def get_distances(fname):
	
	def line_prepender(filename, line):
		with open(filename, 'r+') as f:
			content = f.read()
			f.seek(0, 0)
			f.write(line.rstrip('\r\n') + '\n' + content)
				
	inputfileName = fname
	outputfileName = fname + ".dst"
	
	sims = pandas.read_csv(inputfileName, sep = '\t', index_col=0, header=None) 
	
	dsts = sims.values
	dsts = 1 - sims.values
	dsts = dsts.round(decimals=2)

	dstdf = pandas.DataFrame(dsts)

	newcols = sims.index
	newcols = newcols.str.replace(' ', '')

	dstdf = dstdf.set_index(newcols) 

	dstdf.to_csv(outputfileName, sep = '\t', header=False)
		
	newheader = "Variety"
	for newcol in newcols:
		newheader = newheader + "\t" + newcol

	line_prepender(outputfileName,newheader)
	

# Adapted from https://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python
# We'll use entropy to get a calculation of the homogeneity of a concept
# It will be normalized by maximum possible entropy of list of same length
# We'll subtract from one to get a "homogeneity" score
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
