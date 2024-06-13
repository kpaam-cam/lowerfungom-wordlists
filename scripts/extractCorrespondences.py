# Takes two sets of doculects and finds which lexical items are distinctive in the second set (I think, maybe first, but probably second)

import pandas
import os
import re
    
   
# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"
threshold = "SCA-0.45"

# Load stored cognates to calculates to get some of the "etymological" stuff (I think--I've lost track)
alignmentsFile = analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + threshold + "_threshold" + "-aligned" + ".tsv"

alignments = pandas.read_csv(alignmentsFile, sep='\t')


# doculect list for use as needed
# 	'NVBAbar7',
# 	'ECLAbar8',
# 	'NMAAbar1',
# 	'NACAbar2',
# 	'NEMAjumbu9',
# 	'NVIAjumbu1',
# 	'KMNAjumbu2',
# 	'KDCAjumbu10',
#	'NFKBiya7',
#	'FBCBiya8',
#	'ENBBiya1',
#	'NSFBiya5',
#	'NJNBiya6',
#	'ICNBiya2',
# 	'NNBBuu3',
# 	'MNJBuu4',
# 	'KEMBuu1',
# 	'KCYBuu2',
# 	'KHKFang12',
# 	'DPNFang13',
# 	'KDVFang1',
# 	'KJSFang2',
# 	'JGYKoshin3',
# 	'TELKoshin4',
# 	'MRYKoshin2',
# 	'KCSKung3',
# 	'NJSKung4',
# 	'ZKGKung1',
# 	'BNMKung2',
# 	'NMNMundabli3',
# 	'CENMundabli2',
# 	'LFNMundabli1',
# 	'NINMundabli4',
# 	'NGTMunken3',
# 	'NUNMunken4',
# 	'NEAMunken1',
# 	'TNTMunken2',
# 	'MCANgun3',
# 	'KBMNgun4',
# 	'WCANgun1',
# 	'AOMNgun2',
# 	'APBMumfu1',
# 	'DNMMumfu2',
# 	'BKBMashi2',
# 	'KFKMashi1',
# 	'ABSMissong1',
# 	'AGAMissong2',
# 	'NCCMumfu4',
# 	'MEAMumfu3',
# 	'NMSMissong4',
# 	'NDNMissong5',
# 	'BAAMashi4',
# 	'NCMMashi5',



## Pick the doculects and sound correspondences
## "None" correspondences are always treated as "matching"

soundCorrespondences = {

	'NFKBiya7':	None ,
	'FBCBiya8': 'ə'	,
	'ENBBiya1': 'o'	,
	'NSFBiya5':	None ,
	'NJNBiya6':	None ,
	'ICNBiya2': None ,

	}


# Test example
# soundCorrespondences = {
# 
# 	'NFKBiya7':	'ɛ' ,
# 	'FBCBiya8': 'a?',
# 	'ENBBiya1': None,
# 	'NSFBiya5':	None,
# 	'NJNBiya6':	None,
# 	'ICNBiya2': None,
# 
# 	}


# Get the alignment information from the table
cogAlignments = { }
cogsToDoculects = { }
for index, row in alignments.iterrows():

	doculect = row["DOCULECT"]

	if doculect in soundCorrespondences.keys():
		
		if "SCA" in threshold:
			cogSet = row["SCAID"]
		elif "LS" in threshold:
			cogSet = row["LEXSTATID"]

		alignment = row["ALIGNMENT"]
		
		try:
			alignmentSet = cogAlignments[cogSet]
			alignmentSet.append([doculect, alignment])
			cogAlignments[cogSet] = alignmentSet

		except:
			cogAlignments[cogSet] = [ [doculect, alignment] ]
	
		# Keep track of which cogsets have which doculects to exclude printing out cases
		# where a crucial cognate is not found
		try:		
			doculectsForCog = cogsToDoculects[cogSet]
			doculectsForCog.append(doculect)
			cogsToDoculects[cogSet] = doculectsForCog
		except:
			cogsToDoculects[cogSet] = [ doculect ]
		

# Find all the forms with matches
matchGroups = { }
for cogSet in cogAlignments.keys():
	
	alignmentSet = cogAlignments[cogSet]

	for alignment in alignmentSet:
	
		[doculect, transcription] = alignment
		transcriptionList = transcription.split(" ")
		
		sound = soundCorrespondences[doculect]
		
		# If a sound correspondence is specified, get the matches.
		if sound:
		
			# list comprehension; enumerate returns index and element
			# Get list of all positions where the sound is found
			soundMatches = [i for i, e in enumerate(transcriptionList) if re.search(sound, e)]
			if soundMatches:
				try:
					matchTuple =  matchGroups[cogSet]
					matchTuple.append([doculect, soundMatches, transcription])
					matchGroups[cogSet] = matchTuple
				except:
					matchGroups[cogSet] = [ [doculect, soundMatches, transcription] ]
		
		#Otherwise, just add the transcription and move ahead
		#(since this is a "None" correspondence language)
		else:
			try:
				matchTuple =  matchGroups[cogSet]
				matchTuple.append([doculect, None, transcription])
				matchGroups[cogSet] = matchTuple
			except:
				matchGroups[cogSet] = [ [doculect, None, transcription] ]
					

for cogSet in matchGroups.keys():

	# Track this to exclude sets missing crucial doculects
	# We need it early in the processing
	# Code below could almost certainly be refactored successfully
	cogDoculects = [ ]
	for matchTuple in matchGroups[cogSet]:
		[doculect, soundMatches, transcription] = matchTuple
		cogDoculects.append(doculect)

	excludeFlag = False
	for doculect in soundCorrespondences.keys():
		if soundCorrespondences[doculect] and not(doculect in cogDoculects):
			excludeFlag = True

	if excludeFlag == True:
		continue

	matchLists = [ ]
	for matchTuple in matchGroups[cogSet]:
	
		[doculect, soundMatches, transcription] = matchTuple
	
		if soundMatches:
			matchLists.append(soundMatches)		
		
		
			
	# Do all cases, even if only matches across two of the set, change behavior later?
	allMatches = [ ]
	for matchList in matchLists:
		if matchList:
			allMatches.append(matchList)
	
	matchOverlap = None
	if allMatches:
		matchOverlap = set.intersection(*map(set,allMatches))
		strMatches = list(map(str, matchOverlap))
		strMatches = [int(x)+1 for x in strMatches] # adjust for zero indexing
		strMatches = ', '.join(str(e) for e in sorted(strMatches))
	
	if matchOverlap:
		print("CogId: ", cogSet)
		print("Matching position(s): ", strMatches)
		alignmentSet = cogAlignments[cogSet]
		for alignment in alignmentSet:
			[doculect, transcription] = alignment
			print(doculect, transcription)
		print()

		