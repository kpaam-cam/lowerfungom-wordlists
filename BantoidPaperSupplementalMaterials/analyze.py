"""
Run cognate analyses of wordlists and produce associated outputs
"""

from lingpy import *
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
from lingpy.convert.strings import write_nexus
import pandas
import numpy
from math import log, e
import os
from pathlib import Path


def run():
    
	# Storage folders
	analysesFolder = "analyses"
	analysesSubfolder = ""
	filePrefix = "kplfSubset"

	# SCA similarity threshold, following Hantgan and List
	SCAthreshold = 0.45
     
	dir_ = Path(__file__).parent

	origLex = LexStat.from_cldf("../cldf/cldf-metadata.json")
      
	# Find out the total number of doculects to base the filledness percentage on
	numDoculects = len(origLex.cols)
	filledFraction = 0.75  # Adjust this as desired

	# Dump the concepts that are filled enough into a new file to be loaded for analysis
	outputFile = open(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-filled" + str(filledFraction) + ".tsv", "w")
	header = "ID\tConcept\tDoculect\tValue\tTokens"
	outputFile.write(header + "\n")

	# Get the data for the relevant concepts and write out in new file
	# This is an inefficient algorithm since it repeats a lot of calculations for each entry
	selectedConcepts = {}
	for idx in origLex:
		concept = origLex[idx, "concept"]
		numForms = len(origLex.get_list(row=concept, flat=True))
		filledness = numForms / numDoculects
		if filledness >= filledFraction:
			try:
				selectedConcepts[concept] = selectedConcepts[concept] + 1
			except: selectedConcepts[concept] = 1
			s = "\t"
			output = s.join([str(idx),str(origLex[idx, 'concept']),str(origLex[idx, 'doculect']),str(origLex[idx, 'value']),str(origLex[idx, 'tokens'])])
			outputFile.write(output + "\n")
	outputFile.close()

	outputFile = open(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-ConceptSummary" + ".tsv", "w")
	header = "Concept\tNumDoculects\tPct"
	outputFile.write(header + "\n")
	for conceptNumPair in sorted(selectedConcepts.items(), key = lambda kv: (-kv[1], kv[0])): # sort by numeric value, the alphabetically by key
		concept, numForms = conceptNumPair
		percentageCoverage = round(numForms / numDoculects, 2)
		s = "\t"
		output = s.join([concept,str(numForms),str(percentageCoverage)])
		outputFile.write(output + "\n")
	outputFile.close()

	# Get SCA alignments
	lex = LexStat(dir_.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-filled" + str(filledFraction) + ".tsv").as_posix())

	lex.cluster(method="sca", ref="scaid", threshold=SCAthreshold)
	alm = Alignments(lex, ref="scaid")
	alm.align()
	alm.output(
            "tsv", 
            filename=dir_.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
	# This broke with the new orthographic mapping designed to not use tone in the comparison
	alm.output('html',
    	filename=dir_.joinpath(
               analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold-aligned").as_posix()
                )
    
    # Get SCA distances and tree        
	lex.calculate('tree', ref='scaid')
	tm, tree_taxa = nwk2tree_matrix(lex.tree)
	SCAmatrix = make_matrix('scaid', lex, lex.tree, tree_taxa)
	plot_heatmap(lex, ref='scaid',
		filename=dir_.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold" + "-heatmap").as_posix(),
		vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)
	write_nexus(lex, mode="splitstree", ref="scaid", filename=dir_.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold) + "_threshold" + ".nexus").as_posix())

	print("Completed SCA analysis")

	SCdistFilename= analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold" + "-heatmap.matrix"
	
	# JG: Adding this for 2023 analyses
	get_distances(SCdistFilename)
	print("Created distance file for SC method")


	# Output some files for later analysis, if needed
	lex.output('tsv', filename = dir_.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognates").as_posix(), ignore='all')
	

	# Load stored cognates to calculate stabilities
	wl = Wordlist(dir_.joinpath(
               		analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognates" + ".tsv").as_posix())
	
	# make dictionary to get the groups quickly from a language name
	langs = csv2list(dir_.joinpath("..", "cldf",  "languages.csv"), sep=",")
	lang2group = {k[0]: k[2] for k in langs[1:]}


	# To do: ADD COGTYPE to all filenames for clarity
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
	varietyStabilities_df.to_csv(dir_.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-" + cogType + "-" + str(SCAthreshold) + "_threshold" + "-conceptStabilityByVariety" + ".tsv").as_posix(),
					sep="\t", index=False,)
			
	
	# Do the entry calculations by concept across varieties
	conceptStabilities = [ ]
	for concept in conceptStabilityDict:
		cogList = conceptStabilityDict[concept]
		stability = cogEntropy(cogList)
		
		# Create a dictionary that will be used to create a data frame for export via Pandas
		conceptStability_forDf = { }
		conceptStability_forDf['Concept'] = concept
		conceptStability_forDf['Stability'] = stability
		conceptStabilities.append(conceptStability_forDf)
	
	conceptStabilities_df = pandas.DataFrame(conceptStabilities).sort_values(['Stability', 'Concept'], ascending=[False, True])
	conceptStabilities_df.to_csv(dir_.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-" + cogType +  "-" + str(SCAthreshold) + "_threshold" + "-conceptStabilityByConcept" + ".tsv").as_posix(),
					sep="\t", index=False,)		

	print("Calculated cognate homogeneities")



	

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
	
run()
