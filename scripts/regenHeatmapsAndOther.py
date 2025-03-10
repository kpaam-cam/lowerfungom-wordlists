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




# Storage folders
# Could not work out how to get path into python for the new commands, spent a lot of time since i can't figure out where and how that got specified, maybe a virtualenv issue?
#hacked a solution using a symbolic link
# need to hard code directories
#analysesFolder = "../grollemund-wordlists/analyses"
#analysesSubfolder = ""
#filePrefix = "grollemund"

analysesFolder = "../analyses"
analysesSubfolder = "Phase3a-Fall2023"
filePrefix = "kplfSubset"



# SCA and LexStat similarity thresholds
SCAthreshold = 0.45
LSthreshold = 0.55


# Hacked to minimize changes to lexibank code
dir = Path(__file__).parent

filledFraction = 0.75
lex = LexStat(dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-filled" + str(filledFraction) + ".tsv.bin.tsv").as_posix())

"""   
# Get SCA alignments
lex.cluster(method="sca", ref="scaid", threshold=SCAthreshold)
alm = Alignments(lex, ref="scaid")
alm.align()

# Get SCA distances and tree        
lex.calculate('tree', ref='scaid')
tm, tree_taxa = nwk2tree_matrix(lex.tree)
SCAmatrix = make_matrix('scaid', lex, lex.tree, tree_taxa)
plot_heatmap(lex, ref='scaid',
	filename=dir.joinpath(
			analysesFolder, analysesSubfolder, filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold" + "-heatmap").as_posix(),
	vmax=1,
	tree=lex.tree, colorbar_label='lexical cognates',
	normalized='swadesh', steps = 50, # change for number of languages
	)
"""






"""
SCdistFilename= analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-SCA-" + str(SCAthreshold)+"_threshold" + "-heatmap.matrix"
LSdistFilename= analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-LS-" + str(LSthreshold)+"_threshold" + "-heatmap.matrix"

# JG: Adding this for 2023 analyses
get_distances(SCdistFilename)
args.log.info("Created distance file for SC method")


# to do: why not do above? for LS, too? didn't do it since wasn't a focus, but would be good to consider
"""


# Get LexStat alignments
# I was not really using LexStat, which is why I think this was commented out
# Some adjustment will need to be done to do proper LS analysis
lex.get_scorer(runs=10000, restricted_chars='_')
lex.cluster(method='lexstat', threshold=LSthreshold, restricted_chars='_',
	ref='lexstatid', cluster_method='infomap')
alm = Alignments(lex, ref="lexstatid")
alm.align()
#alm.output(
#		"tsv", 
#		filename=KPLF.dir.joinpath(
#			analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold-aligned").as_posix(),
#		ignore="all",
#		prettify=False
#		)
#This broke with the new orthographic mapping designed to not use tone in the comparison
alm.output('html',
filename=dir.joinpath(
		   analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold-aligned").as_posix()
		   )


"""
# Get LexStat distances and tree        
lex.calculate('tree', ref='lexstatid')
tm, tree_taxa = nwk2tree_matrix(lex.tree)
LSmatrix = make_matrix('lexstatid', lex, lex.tree, tree_taxa)
plot_heatmap(lex, ref='lexstatid',
	filename=KPLF.dir.joinpath(
			analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold)+"_threshold" + "-heatmap").as_posix(),
	vmax=1,
	tree=lex.tree, colorbar_label='lexical cognates',
	normalized='swadesh', steps = 100,
	)
write_nexus(lex, mode="splitstree", ref="lexstatid", filename=KPLF.dir.joinpath(
			analysesFolder, analysesSubfolder, filePrefix + "-LS-" + str(LSthreshold) + "_threshold" + ".nexus").as_posix())

args.log.info("Completed LexStat analysis")

# Output some files for later analysis, if needed
lex.output('tsv', filename = KPLF.dir.joinpath(
			analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates").as_posix(), ignore='all')

get_distances(LSdistFilename)
args.log.info("Created distance file for LS method")


# Make the diff heatmap matrix
_, matrix1 = load_matrix(analysesFolder + "/" + filePrefix + "-LS-" + str(LSthreshold) + "_threshold" + "-heatmap" +  ".matrix")
_, matrix2 = load_matrix(analysesFolder + "/" + filePrefix + "-SCA-" + str(SCAthreshold) + "_threshold" + "-heatmap" +  ".matrix")

new_matrix = [[0 for x in range(len(matrix1[0]))] for y in
		range(len(matrix1))]
for _i in range(len(matrix1)):
	for _j in range(len(matrix1)):
		new_matrix[_i][_j] = 0.5 + (matrix2[_i][_j] - matrix1[_i][_j])
plot_heatmap(lex, matrix=new_matrix, tree=lex.tree,
		colorbar_label='differences (inferred cognates)',
		filename=KPLF.dir.joinpath(
			analysesFolder, analysesSubfolder, filePrefix + "-LSSCAdiffs-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-heatmap").as_posix(),
		vmax=0.7, vmin=0.3, steps = 100)

args.log.info("Calculated difference heatmaps")


# Some comparisons (but I don't know how to interpret them...)
#p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=True)


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
	
	# Create a dictionary that will be used to create a data frame for export via Pandas
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
	
"""