# XXX describe me once I understand

from lingpy import Wordlist
import pandas
import os


# for Symmetric Difference of sets for cognate difference across sets
# Taken from https://stackoverflow.com/questions/27321536/how-can-the-symmetric-difference-between-two-lists-of-two-element-sublists-be-ob
# Symmetric difference equals the set of elements *not* in intersection
# Returns the distinct items in each set of cognates
# The "^" is the xor infix operator in Python which, for sets, calculates the symmetric difference
def getDifference(cogs1,cogs2):
    symDiff = set(cog for cog in cogs1) ^ set(cog for cog in cogs2)
    return [cog for cog in cogs1 if cog in symDiff], [cog for cog in cogs2 if cog in symDiff]
    
   
# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

# SCA and LexStat similarity thresholds
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")

cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)

# load concept stabilities if needed
stabilitiesFile = analysesFolder + os.sep + analysesSubfolder + os.sep + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-conceptStabilityByConcept" + ".tsv"

conceptStabilities = pandas.read_csv(stabilitiesFile,sep="\t")

# Make dictionary for them for later, when needed
stabilitiesForNetwork = { }
for index, row in conceptStabilities.iterrows():
	concept = row["Concept"]
	stability = row["Stability"]
	stabilitiesForNetwork[concept] = stability


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



docSet1 = [
				"ECLAbar8",
				"NACAbar2",
				"NMAAbar1",
				"NVBAbar7",
				"AOMNgun2",
				"KBMNgun4",
				"MCANgun3",
				"WCANgun1",
 				"NEAMunken1",
 				"NGTMunken3",
 				"NUNMunken4",
 				"TNTMunken2",
#				"ABSMissong1",
#				"AGAMissong2",
#				"NDNMissong5",
#				"NMSMissong4",
				"ENBBiya1",
				"FBCBiya8",
				"ICNBiya2",
				"NFKBiya7",
				"NJNBiya6",
				"NSFBiya5",
				]


docSet2 = [
				"ABSMissong1",
				"AGAMissong2",
				"NDNMissong5",
				"NMSMissong4",
				]
				

# Keeping for cutting and pasting
# Working to see shared cognates, etc., across a set of varieties
# 	docSet1 = [	#"ECLAbar8",
# 				#"NACAbar2",
# 				#"NMAAbar1",
# 				#"NVBAbar7",
# 				#"JGYKoshin3",
# 				#"MRYKoshin2",
# 				#"TELKoshin4",
# 				#"DPNFang13",
#  				#"KDVFang1",
#  				#"KHKFang12",
#  				#"KJSFang2",
#  				"BNMKung2",
# 				"KCSKung3",
# 				"NJSKung4",
# 				"ZKGKung1",
# 
# 				]
# 
# 	docSet2 = [	"KCYBuu2",
# 				"KEMBuu1",
# 				"MNJBuu4",
# 				"NNBBuu3", ]
# 				
# 	docSet3 = [	"APBMumfu1",
# 				"DNMMumfu2",
# 				"MEAMumfu3",
# 				"NCCMumfu4",
# 				"CENMundabli2",
# 				"LFNMundabli1",
# 				"NINMundabli4",
# 				"NMNMundabli3", ]

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




# First get self-intersection within each doculect set
set1docs = { } # storing sets of cognates shared within a set
set2docs = { }
for doculect in sorted(doculectCognateDict.keys()):
	cogs = doculectCognateDict[doculect]
	if doculect in docSet1:
		set1docs[doculect] = cogs
	elif doculect in docSet2:
		set2docs[doculect] = cogs

# Create lists of cogsets for each doculect in a variety
varCogs1 = [ ]
varCogs2 = [ ]
for doculect in set1docs:
	varCogs1.append(set1docs[doculect])
for doculect in set2docs:
	varCogs2.append(set2docs[doculect])

# Relaxed conditions on docset1 so that if a concept equivalent is missing in some doculect, it's still OK for this analysis

# This would impose a strict condition on docset1 presence of the cognate, but notusing for now
#set1docsInt = set.intersection(*map(set,varCogs1))

# This code is for the relaxed condition to create the intersection dictionary
set1docsIntDict = { }
for cogList in varCogs1:
	for cogid in cogList:
		concept = cogidConceptDict[cogid]
		
		# If we've already encountered the cogId, we do nothing
		try: foundCogId = set1docsIntDict[concept]
		
		# Otherwise, we add it and set it to found
		except:
			set1docsIntDict[concept] = cogid
			foundCogId = set1docsIntDict[concept]

		# We want to check to see if an existing cogId for the concept in the set
		# is the same as the one already stored. If so, we're fine.
		if cogid == foundCogId: pass
		
		# If not, we set the concept to "MIXED", which we'll use as a filter for later
		else: set1docsIntDict[concept] = "MIXED"

set1docsInt = set()
for concept in set1docsIntDict:
	coherence = set1docsIntDict[concept]
	if coherence == "MIXED":
		pass
	# Only concepts all in same similarity set should have made it to this stage
	# So, we can add them
	else:
		set1docsInt.add(coherence)


# For set2, we maintain strict conditions where all must have the relevant "cognate"
# This trick from: https://stackoverflow.com/questions/3852780/python-intersection-of-multiple-lists
# Turn each item in the list of lists to a set via map, the "*" seems to unpack the
# items in map function, which appears to be an iterator, producing a set of sets,
# then we get the intersection of cognateIDs found in all the doculect cognate sets
set2docsInt = set.intersection(*map(set,varCogs2))
#print(set2docsInt)

# Get the set of cogIDs in set1 not on set2 and vice versa
set1only, set2only = getDifference(set1docsInt,set2docsInt)

# Make a dictionary of cognates associated with the concepts

# First build the matching dictionary for set1
matchedConcepts = { }
for cogid in set1only:
	concept = cogidConceptDict[cogid]
	matchedConcepts[concept] = [cogid]

# Now built if for set2; in this case we need to see if there's already a cognate
# in there from set1. If so, we append the new one to the existing one.
for cogid in set2only:
	concept = cogidConceptDict[cogid]
	try:
		cogList = matchedConcepts[concept]
		cogList.append(cogid)
		matchedConcepts[concept] = cogList
	except:
		pass

# Now we filter the dictionary for cases where the entry is list of >1 (i.e., 2 in this case)
# If so, we have a case of cognate mismatches across the two docsets, and we print those out
# We get IDs that need to be looked up with in the other LingPy outputs, I use the
# HTML version for this
for concept in matchedConcepts:
	cogList = matchedConcepts[concept]
	if len(cogList) > 1:
		print(concept, matchedConcepts[concept])