# Given three sets of doculects, create graphs of shared cognates with one set as
# the "focus". This was originally used for the Abar-Buu-Munfabli subgraph
# This produces files to be read in R using iGraph, etc.

# The network edge strength works as follows:
# (i) if shared between group 1 and 3, write out that connection and don't include in the sharing for group 1 and 2 and 2 and 3
# (ii) if only shared between 1 and 2, write a blue edge
# (iii) if only shared between 2 and 3 write a red eduge
# Other edge colors for formatting but not fully used now due to issues understanding the iGraph to ggnetwork transition

from lingpy import Wordlist
import os
    
   
# Storage folders
analysesFolder = "../analyses"
filePrefix = "kplfSubset"

# SCA and LexStat similarity thresholds
SCAthreshold = 0.45

# Load stored cognates to calculate stabilities
wl = Wordlist(analysesFolder + "/" + filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognates" + ".tsv")
  
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



# Output file for the subgraph
netFile = open(analysesFolder+"/"+filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognateSelection-Network" + ".tsv", "w")

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
						#netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + samesetcolor + "\n")
				elif doculectMain in docSet2:
					# Always do purple first, but maybe not a problem the way things are set up to check doculects looked at already?
					if doculectComp in docSet3 and doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
					elif doculectComp in docSet3:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
					elif doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "blue" + "\n")
					elif doculectComp in docSet2:
						#netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + samesetcolor + "\n")
				elif doculectMain in docSet3:
					# Always do purple first, but maybe not a problem the way things are set up to check doculects looked at already?
					if doculectComp in docSet1:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "purple" + "\n")
					elif doculectComp in docSet2:
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap) + "\t" + "red" + "\n")
					elif doculectComp in docSet3:
						#netFile.write(doculectMain + "\t" + doculectComp + "\t" + str(overlap/3) + "\t" + samesetcolor + "\n")
						netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + samesetcolor + "\n")
			else:
				# igraph requires a positive edge weight. So, I use .01 rather than 0
				netFile.write(doculectMain + "\t" + doculectComp + "\t" + ".01" + "\t" + "grey90" + "\n")
				
	calculatedDoculects.add(doculectMain)

print("Created network file for subgraph")