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

from itertools import combinations, product
from sklearn.metrics.cluster import normalized_mutual_info_score

def pairs(*lists):
    for t in combinations(lists, 2):
        for pair in product(*t):
            #Don't output pairs containing duplicated elements 
            if pair[0] != pair[1]:
                yield pair
def run(args):
    
	# Storage folders
	analysesFolder = "analyses"
	analysesSubfolder = "Phase3a-Fall2023"
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
	stabilitiesForNetwork = { }
	for concept in conceptStabilityDict:
		cogList = conceptStabilityDict[concept]
		stability = cogEntropy(cogList)
		stabilitiesForNetwork[concept] = stability
		# Create a dictionary that will be used to create a data frame for export via Pandas
		conceptStability_forDf = { }
		conceptStability_forDf['Concept'] = concept
		conceptStability_forDf['Stability'] = stability
		conceptStabilities.append(conceptStability_forDf)
	
	conceptStabilities_df = pandas.DataFrame(conceptStabilities).sort_values(['Stability', 'Concept'], ascending=[False, True])
	conceptStabilities_df.to_csv(KPLF.dir.joinpath(analysesFolder, analysesSubfolder, filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-conceptStabilityByConcept" + ".tsv").as_posix(),
					sep="\t", index=False,)		

	args.log.info("Calculating cognate homogeneities")


	# Mutual information of cognate distribution
	seenPairs = [ ]
	for conceptA in conceptStabilityDict.keys():
		for conceptB in conceptStabilityDict.keys():
			if conceptB + conceptA in seenPairs:
				pass
			elif len(conceptStabilityDict[conceptA]) == 54 and len(conceptStabilityDict[conceptB]) == 54:
				MI = normalized_mutual_info_score(conceptStabilityDict[conceptA], conceptStabilityDict[conceptB])
				seenPairs.append(conceptA+conceptB)
				print(conceptA, conceptB, MI, sep="\t")
			#except:
				#print(conceptA, conceptB, "different sizes")
			#	pass

	# Make a "turned" table for analysis of cognate predicatability of languoid
	# First, get a dictionary that takes a doculect and links to all cogids associated with the doculect
	doculectCognateDict = { }
	cogidConceptDict = { }
	cogids = []
	for id, reflexes in etd.items():
		for reflex in reflexes:
			if reflex:
				doculect = wl[reflex[0], 'doculect']
				concept= wl[reflex[0], 'concept']
				cogid = wl[reflex[0], cogType] # actually same as ID, fix later
				try: doculectCognateDict[doculect].append(cogid)
				except: doculectCognateDict[doculect] = [cogid]
				# Kind of messy, but easy
				cogidConceptDict[cogid] = concept
			else:
				pass
		# build up a list of cognate ids
		cogids.append(id)
	
	cogids.sort()
	
	# Working to see shared cognates, etc., across a set of varieties
	docSet1 = [	#"ECLAbar8",
				#"NACAbar2",
				#"NMAAbar1",
				#"NVBAbar7",
				#"JGYKoshin3",
				#"MRYKoshin2",
				#"TELKoshin4",
				#"DPNFang13",
 				#"KDVFang1",
 				#"KHKFang12",
 				#"KJSFang2",
 				"BNMKung2",
				"KCSKung3",
				"NJSKung4",
				"ZKGKung1",

				]

	docSet2 = [	"KCYBuu2",
				"KEMBuu1",
				"MNJBuu4",
				"NNBBuu3", ]
				
	docSet3 = [	"APBMumfu1",
				"DNMMumfu2",
				"MEAMumfu3",
				"NCCMumfu4",
				"CENMundabli2",
				"LFNMundabli1",
				"NINMundabli4",
				"NMNMundabli3", ]

# 	docSet1 = [	"ECLAbar8",
# 				"NACAbar2",
# 				"NMAAbar1",
# 				"NVBAbar7", ]
# 
# 	docSet2 = [	"ABSMissong1",
# 				"AGAMissong2",
# 				"NDNMissong5",
# 				"NMSMissong4", ]
# 				
# 	docSet3 = [	"APBMumfu1",
# 				"DNMMumfu2",
# 				"MEAMumfu3",
# 				"NCCMumfu4",
# 				"CENMundabli2",
# 				"LFNMundabli1",
# 				"NINMundabli4",
# 				"NMNMundabli3", ]


# 	docSet2 = [	"ABSMissong1",
# 				"AGAMissong2",
# 				"NDNMissong5",
# 				"NMSMissong4", ]
				
# 	docSet3 = [	"APBMumfu1",
# 				"DNMMumfu2",
# 				"MEAMumfu3",
# 				"NCCMumfu4",
# 				"CENMundabli2",
# 				"LFNMundabli1",
# 				"NINMundabli4",
# 				"NMNMundabli3", ]


# 	docSet1 = [
# 				"ECLAbar8",
# 				"NACAbar2",
# 				"NMAAbar1",
# 				"NVBAbar7",
#				"ABSMissong1",
#				"AGAMissong2",
#				"NDNMissong5",
# 				"NMSMissong4",
# 				"AOMNgun2",
# 				"KBMNgun4",
# 				"MCANgun3",
# 				"WCANgun1",
# 				"ENBBiya1",
# 				"FBCBiya8",
# 				"ICNBiya2",
# 				"NFKBiya7",
# 				"NJNBiya6",
# 				"NSFBiya5",
# 				"NEAMunken1",
# 				"NGTMunken3",
# 				"NUNMunken4",
# 				"TNTMunken2",

				#"BNMKung2",
				#"KCSKung3",
				#"NJSKung4",
				#"ZKGKung1",

# 				"APBMumfu1",
# 				"DNMMumfu2",
# 				"MEAMumfu3",
# 				"NCCMumfu4",
# 				"CENMundabli2",
# 				"LFNMundabli1",
# 				"NINMundabli4",
# 				"NMNMundabli3",
# 
# 				"BAAMashi4",
# 				"BKBMashi2",
# 				"KFKMashi1",
# 				"NCMMashi5",

				#"DPJKoshin1",
#				"JGYKoshin3",
#				"MRYKoshin2",
#				"TELKoshin4",
#				]

# 	docSet2 = [	
# 				"NEAMunken1",
# 				"NGTMunken3",
# 				"NUNMunken4",
# 				"TNTMunken2",
# 				 ]
# 
# 	docSet3 = [
# 				"BAAMashi4",
# 				"BKBMashi2",
# 				"KFKMashi1",
# 				"NCMMashi5",
# 				]


# 	docSet2 = [	"KCYBuu2",
#  				"KEMBuu1",
#  				"MNJBuu4",
#  				"NNBBuu3", ]
# 
# 
# 	docSet3 = [
# 				"DPNFang13",
# 				"KDVFang1",
# 				"KHKFang12",
# 				"KJSFang2",
# 				]



	
	# Now make a shared cognate across varieties data object to create a network structure
	netFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognateSelection-Network" + ".tsv", "w")

	netFile.write("Doculect1\tDoculect2\tweight\tcolor\n")

	calculatedDoculects = set()
	doculectSelection = docSet1 + docSet2 + docSet3
	for doculectMain in sorted(doculectCognateDict.keys()):
		docCogsMain = doculectCognateDict[doculectMain]
		for doculectComp in sorted(doculectCognateDict.keys()):
			if doculectComp == doculectMain: pass
			elif doculectComp in calculatedDoculects: pass
			else:
				docCogsComp = doculectCognateDict[doculectComp]
				overlap = sum(1 for element in docCogsMain if element in docCogsComp)
				if doculectMain in doculectSelection and doculectComp in doculectSelection:
					if doculectMain in docSet1:
						if doculectComp in docSet3:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
						elif doculectComp in docSet2:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "blue" + "\n")
						elif doculectComp in docSet1:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + "grey75" + "\n")
					elif doculectMain in docSet2:
						if doculectComp in docSet3:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
						elif doculectComp in docSet1:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "blue" + "\n")
						elif doculectComp in docSet2:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + "grey75" + "\n")
					elif doculectMain in docSet3:
						if doculectComp in docSet2:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
						elif doculectComp in docSet1:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
						elif doculectComp in docSet3:
							netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + "grey75" + "\n")
				else:
					# igraph requires a positive edge weight. So, I use .01 rather than 0
					netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + "transparent" + "\n")
					
		calculatedDoculects.add(doculectMain)

	args.log.info("Created network file for each doculect")

	
	#netFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates-Network" + ".tsv", "w")

	#netFile.write("Doculect1\tDoculect2\tSharedCognateCount\n")

	# Get intersections
	set1cogs = { }
	set2cogs = { }
	set3cogs = { }
	for doculect in sorted(doculectCognateDict.keys()):
		cogs = doculectCognateDict[doculect]
		if doculect in docSet1:
			set1cogs[doculect] = cogs
		elif doculect in docSet2:
			set2cogs[doculect] = cogs
		elif doculect in docSet3:
			set3cogs[doculect] = cogs
	
	list123 = [ ]
	for doculect in set1cogs:
		list123.append(set1cogs[doculect])
	for doculect in set2cogs:
		list123.append(set2cogs[doculect])
	for doculect in set3cogs:
		list123.append(set3cogs[doculect])
	int123 = set.intersection(*map(set,list123))
	#print("123")
	for cog in int123:
		#print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
		pass
	int123weight = len(int123)
	#print("\n")

	list12 = [ ]
	for doculect in set1cogs:
		list12.append(set1cogs[doculect])
	for doculect in set2cogs:
		list12.append(set2cogs[doculect])
	int12 = set.intersection(*map(set,list12))
	#print("12")
	for cog in int12:
		#print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
		pass
	int12weight = len(int12)
	#print("\n")

	list23 = [ ]
	for doculect in set2cogs:
		list23.append(set2cogs[doculect])
	for doculect in set3cogs:
		list23.append(set3cogs[doculect])
	int23 = set.intersection(*map(set,list23))
	#print("23")
	for cog in int23:
		#print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
		pass
	int23weight = len(int23)
	#print("\n")

	# Edges for all shared
	color123 = "purple"
	seenBis = [ ]
	for doculect1 in sorted(set1cogs.keys()):
		#for doculect2 in sorted(set2cogs.keys()):
		#	print(doculect1, doculect2, int123weight, color123, sep='\t')
		for doculect3 in sorted(set3cogs.keys()):
			#print(doculect1, doculect3, int123weight, color123, sep='\t')
			pass
# removing BIS for now since did not calculate inter-group weights! Maybe better visually?
# 		for doculect1bis in sorted(set1cogs.keys()):
# 			if doculect1bis in seenBis: pass
# 			elif doculect1bis == doculect1: pass
# 			else:
# 				seenBis.append(doculect1)
# 				print(doculect1, doculect1bis, int123weight, color123, sep='\t')

	seenBis = [ ]
#	for doculect2 in sorted(set2cogs.keys()):
#		for doculect3 in sorted(set3cogs.keys()):
#			print(doculect2, doculect3, int123weight, color123, sep='\t') # JG: This may be an error?
# 		for doculect2bis in sorted(set2cogs.keys()):
# 			if doculect2bis in seenBis: pass
# 			elif doculect2bis == doculect2: pass
# 			else:
# 				seenBis.append(doculect2)
# 				print(doculect2, doculect2bis, int123weight, color123, sep='\t')

# 	seenBis = [ ]
# 	for doculect3 in sorted(set3cogs.keys()):
# 		for doculect3bis in sorted(set3cogs.keys()):
# 			if doculect3bis in seenBis: pass
# 			elif doculect3bis == doculect3: pass
# 			else:
# 				seenBis.append(doculect3)
# 				print(doculect3, doculect3bis, int123weight, color123, sep='\t')
	
# Next step: Make the graphs for the other weights!
	# Edges for all shared
	color12 = "red"
	seenBis = [ ]
	for doculect1 in sorted(set1cogs.keys()):
		for doculect2 in sorted(set2cogs.keys()):
			#print(doculect1, doculect2, int12weight, color12, sep='\t')
			pass
# 		for doculect1bis in sorted(set1cogs.keys()):
# 			if doculect1bis in seenBis: pass
# 			elif doculect1bis == doculect1: pass
# 			else:
# 				seenBis.append(doculect1)
# 				print(doculect1, doculect1bis, int12weight, color12, sep='\t')

	color23 = "blue"
	seenBis = [ ]
	for doculect2 in sorted(set2cogs.keys()):
		for doculect3 in sorted(set3cogs.keys()):
			#print(doculect2, doculect3, int23weight, color23, sep='\t')
			pass
# 		for doculect2bis in sorted(set2cogs.keys()):
# 			if doculect2bis in seenBis: pass
# 			elif doculect2bis == doculect2: pass
# 			else:
# 				seenBis.append(doculect2)
# 				print(doculect2, doculect2bis, int123weight, color123, sep='\t')

# 	seenBis = [ ]
# 	for doculect3 in sorted(set3cogs.keys()):
# 		for doculect3bis in sorted(set3cogs.keys()):
# 			if doculect3bis in seenBis: pass
# 			elif doculect3bis == doculect3: pass
# 			else:
# 				seenBis.append(doculect3)
# 				print(doculect3, doculect3bis, int123weight, color123, sep='\t')


# 	output = set(pairs(set1cogs.keys(), set3cogs.keys(), set3cogs.keys()))
# 	for pair in sorted(output):
# 		print(pair)
		
		#setName = doculect + "Set"
		#cogList = "<- c(" + ", ".join(map(str, cogs)) +")\n"
		#print(setName,cogList)
	args.log.info("Created network file for each doculect")
	
	
# https://stackoverflow.com/questions/35270766/python-getting-unique-pairs-from-multiple-lists-of-different-lengths
# def pairs(*lists):
# 	for t in combinations(lists, 2):
# 		for pair in product(*t):
# 			#Don't output pairs containing duplicated elements 
# 			if pair[0] != pair[1]:
# 				yield pair			


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
