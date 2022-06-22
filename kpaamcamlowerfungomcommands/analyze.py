"""
Run cognate analyses of wordlists and produce associated outputs
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
	analysesSubfolder = "Phase3-Summer2022"
	filePrefix = "kplfSubset"

	# SCA and LexStat similarity thresholds
	SCAthreshold = 0.45
	LSthreshold = 0.55
 
     # default import of data with lingpy
	KPLF = Dataset()
     
    # Code from Robert Forkel to handle cases where CLDF contains multiple forms for same
    # concept. Not using now since that filtering is happening at CLDF creation stage
 	# D = {0: ['concept', 'doculect', 'value', 'tokens']}
 	# 
 	# for i, ((concept, doculect), forms) in enumerate(itertools.groupby(
 	# 	sorted(cldf['FormTable'], key=lambda f: (f['Parameter_ID'], f['Language_ID'])),
 	# 	lambda f: (f['Parameter_ID'], f['Language_ID']),
 	# ), start=1):
 	# 	for form in forms:
 	# 		D[i] = [concept, doculect, form['Form'], form['Segments']]
 	# 		break  # We only take the first form variant per concept/doculect pair.
 
     
     # This is the original CLDF that we'll subset following a specified threshold
	origLex = LexStat.from_cldf(
             KPLF.cldf_dir.joinpath("cldf-metadata.json")
             )
      
	# Find out the total number of doculects to base the filledness percentage on
	numDoculects = len(origLex.cols)
	filledFraction = 0.90  # Adjust this as desired

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

	
	# Now load the subsetted data. Maybe this can be done more efficiently than writing and loading a file...

	#If the LexStat calculations have been done already use those
	try:
		lex = LexStat(KPLF.dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-filled" + str(filledFraction) + ".tsv.bin.tsv").as_posix())
	except:
		lex = LexStat(KPLF.dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-filled" + str(filledFraction) + ".tsv").as_posix())
		lex.get_scorer(runs=10000, restricted_chars='_')
		lex.output('tsv', filename = KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, lex.filename+'.bin').as_posix(), ignore='')
       
    # Get SCA alignments
	lex.cluster(method="sca", ref="scaid", threshold=SCAthreshold)
	alm = Alignments(lex, ref="scaid")
	alm.align()
	alm.output(
            "tsv", 
            filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
	# This broke with the new orthographic mapping designed to not use tone in the comparison
	#alm.output('html',
    #	filename=KPLF.dir.joinpath(
    #           analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold-aligned").as_posix()
    #            )
    
    # Get SCA distances and tree        
	lex.calculate('tree', ref='scaid')
	tm, tree_taxa = nwk2tree_matrix(lex.tree)
	SCAmatrix = make_matrix('scaid', lex, lex.tree, tree_taxa)
	plot_heatmap(lex, ref='scaid',
		filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold" + "-heatmap").as_posix(),
		vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)
	write_nexus(lex, mode="splitstree", ref="scaid", filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold) + "_threshold" + ".nexus").as_posix())

	args.log.info("Completed SCA analysis")


    # Get LexStat alignments
	# lex.get_scorer(runs=10000, restricted_chars='_')
	lex.cluster(method='lexstat', threshold=LSthreshold, restricted_chars='_',
 		ref='lexstatid', cluster_method='infomap')
	alm = Alignments(lex, ref="lexstatid")
	alm.align()
	alm.output(
            "tsv", 
            filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
	# This broke with the new orthographic mapping designed to not use tone in the comparison
	#alm.output('html',
    #	filename=KPLF.dir.joinpath(
    #            analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold-aligned").as_posix()
    #            )

    # Get LexStat distances and tree        
	lex.calculate('tree', ref='lexstatid')
	tm, tree_taxa = nwk2tree_matrix(lex.tree)
	LSmatrix = make_matrix('lexstatid', lex, lex.tree, tree_taxa)
	plot_heatmap(lex, ref='lexstatid',
		filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold" + "-heatmap").as_posix(),
		vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)
	write_nexus(lex, mode="splitstree", ref="lexstatid", filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold) + "_threshold" + ".nexus").as_posix())

	args.log.info("Completed LexStat analysis")

	# Output some files for later analysis, if needed
	lex.output('tsv', filename = KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates").as_posix(), ignore='all')
	

	# Make the diff heatmap matrix
	_, matrix1 = load_matrix(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-LS-" + str(LSthreshold) + "_threshold" + "-heatmap" +  ".matrix")
	_, matrix2 = load_matrix(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-SCA-" + str(SCAthreshold) + "_threshold" + "-heatmap" +  ".matrix")

	new_matrix = [[0 for x in range(len(matrix1[0]))] for y in
			range(len(matrix1))]
	for _i in range(len(matrix1)):
		for _j in range(len(matrix1)):
			new_matrix[_i][_j] = 0.5 + (matrix2[_i][_j] - matrix1[_i][_j])
	plot_heatmap(lex, matrix=new_matrix, tree=lex.tree,
			colorbar_label='differences (inferred cognates)',
			filename=KPLF.dir.joinpath(
                analysesFolder, analysesSubfolder, filePrefix + "-LSSCAdiffs-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-heatmap").as_posix(),
			vmax=0.7, vmin=0.3, steps = 45)

	args.log.info("Calculated difference heatmaps")


	# Some comparisons (but I don't know how to interpret them...)
	p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=True)


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
