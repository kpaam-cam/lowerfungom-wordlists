# Given three sets of doculects, create graphs of shared cognates with one set as
# the "focus". This was originally used for the Abar-Buu-Munfabli subgraph
# This produces files to be read in R using iGraph, etc.

from lingpy import Wordlist
import os
    
   
# Storage folders
analysesFolder = "../analyses"
analysesSubfolder = "/Phase3a-Fall2023"
filePrefix = "kplfSubset"

# SCA and LexStat similarity thresholds
SCAthreshold = 0.45
LSthreshold = 0.55

# Load stored cognates to calculate stabilities
wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")
  
cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)


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


# For Buu-Abar-Munfabli network

# First comparison set
docSet1 = [	"ECLAbar8",
			"NACAbar2",
			"NMAAbar1",
			"NVBAbar7",
			]

# "Central" comparison set: docSet1 + docSet2 compared, then docSet2 + docSet 3
# Colors, in particular controlled by this
docSet2 = [	"KCYBuu2",
			"KEMBuu1",
			"MNJBuu4",
			"NNBBuu3", ]
			
# Third comparison set
docSet3 = [	"APBMumfu1",
			"DNMMumfu2",
			"MEAMumfu3",
			"NCCMumfu4",
			"CENMundabli2",
			"LFNMundabli1",
			"NINMundabli4",
			"NMNMundabli3", ]

# I leave these here for easy cut and paste
# 	docSet1 = [
# 				"ECLAbar8",
# 				"NACAbar2",
# 				"NMAAbar1",
# 				"NVBAbar7",
# 				"AOMNgun2",
# 				"KBMNgun4",
# 				"MCANgun3",
# 				"WCANgun1",
#  				"NEAMunken1",
#  				"NGTMunken3",
#  				"NUNMunken4",
#  				"TNTMunken2",
# 				"ABSMissong1",
# 				"AGAMissong2",
# 				"NDNMissong5",
# 				"NMSMissong4",
# 				"ENBBiya1",
# 				"FBCBiya8",
# 				"ICNBiya2",
# 				"NFKBiya7",
# 				"NJNBiya6",
# 				"NSFBiya5",
# 				]
# 
# 
# 	docSet2 = [
# #				"ABSMissong1",
# #				"AGAMissong2",
# #				"NDNMissong5",
# 				"NMSMissong4",
# 				]
# 				
# 	docSet3 = [ ]
# 

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




# Output file for the subgraph
netFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognateSelection-Network" + ".tsv", "w")

# The weight and color columns can be used directly by iGraph in R
netFile.write("Doculect1\tDoculect2\tweight\tcolor\n")

# The core work of the script is done here
# blue = cognate in set1 and set2
# red = cognate in set2 and set3
# purple = cognate in set1 and set3
samesetcolor = "grey30"
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
					# Note the logic: If it's shared in set1 and set3, we write to purple and don't connect to set2
					if doculectComp in docSet3:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
					elif doculectComp in docSet2:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "blue" + "\n")
					elif doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
				elif doculectMain in docSet2:
					if doculectComp in docSet3:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
					elif doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "blue" + "\n")
					elif doculectComp in docSet2:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
				elif doculectMain in docSet3:
					if doculectComp in docSet2:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
					elif doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
					elif doculectComp in docSet3:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
			else:
				# igraph requires a positive edge weight. So, I use .01 rather than 0
				netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + "grey90" + "\n")
				
	calculatedDoculects.add(doculectMain)

print("Created network file for subgraph")

# Output file for the vertices for formatting
vertexFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognateSelection-Vertices" + ".tsv", "w")

# The color columns will be used directly in iGraph
vertexFile.write("Vertex\tcolor\n")

# Make the vertex file for additional color coding
for doculectMain in sorted(doculectCognateDict.keys()):

	if doculectMain in docSet1:
		color = "black"
	elif doculectMain in docSet2:
		color = "black"
	elif doculectMain in docSet3:
		color = "black"
	else: color = "transparent"

	vertexFile.write(doculectMain + "\t" + color + "\n")

print("Created vertex file for subgraph")


## Keeping this code since I don't remember its point, but does nothing for now

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

