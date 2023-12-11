# Takes three sets of doculects and returns those at the intersection of all three sets
# and set1 and set2 and set2 and set3. Outputs stabilities alongside those, too
# Used now for Abar, Buu, and Munfabli


from lingpy import Wordlist
import pandas
import os

   
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

# load concept stabilities
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


# For Buu-Abar-Munfabli network
docSet1 = [	"ECLAbar8",
			"NACAbar2",
			"NMAAbar1",
			"NVBAbar7",
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
# #				"ABSMissong1",
# #				"AGAMissong2",
# #				"NDNMissong5",
# #				"NMSMissong4",
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





# Here, we get intersections of the cognates across varieties of a languoid

# First collect the cognates for each set of doculects
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

# For now output just goes to console, maybe can upgrade at some point but not needed now

# Note: The 12 and 23 intersections include the 123 intersections since I have not
# specifically filtered them out of 12 and 23

# Find the intersections of cognates across all of the considered doculects
list123 = [ ]
for doculect in set1cogs:
	list123.append(set1cogs[doculect])
for doculect in set2cogs:
	list123.append(set2cogs[doculect])
for doculect in set3cogs:
	list123.append(set3cogs[doculect])
int123 = set.intersection(*map(set,list123))
print("123")
for cog in int123:
	print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
int123weight = len(int123)
print("\n")

# Find the intersections of cognates across set1 and set2
list12 = [ ]
for doculect in set1cogs:
	list12.append(set1cogs[doculect])
for doculect in set2cogs:
	list12.append(set2cogs[doculect])
int12 = set.intersection(*map(set,list12))
print("12")
for cog in int12:
	print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
int12weight = len(int12)
print("\n")

# Find the intersections of cognates across set1 and set2
list23 = [ ]
for doculect in set2cogs:
	list23.append(set2cogs[doculect])
for doculect in set3cogs:
	list23.append(set3cogs[doculect])
int23 = set.intersection(*map(set,list23))
print("23")
for cog in int23:
	print(cog, cogidConceptDict[cog], stabilitiesForNetwork[cogidConceptDict[cog]], sep="\t")
int23weight = len(int23)