"""
Try to make network for LexStat to compare with SCA
"""

from lingpy import Wordlist


# Storage folders
#analysesFolder = "../analyses"
#analysesSubfolder = "Phase3a-Fall2023"
#filePrefix = "kplfSubset"

analysesFolder = "../grollemund-wordlists/analyses"
analysesSubfolder = "8May-WorkingSetWellCoveredConcepts98Threshold"
filePrefix = "grollemund"




# SCA and LexStat similarity thresholds
SCAthreshold = 0.45
LSthreshold = 0.55

wl = Wordlist(analysesFolder + "/" + analysesSubfolder + "/" + filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + "_thresholds" + "-cognates" + ".tsv")
#cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
cogType = "lexstatid" # Pick cogtype to use (e.g., SC vs. LexStat)
etd = wl.get_etymdict(ref=cogType)

doculectCognateDict = { }
cogids = []
for id, reflexes in etd.items():
	for reflex in reflexes:
		if reflex:
			doculect = wl[reflex[0], 'doculect']
			concept= wl[reflex[0], 'concept']
			cogid = wl[reflex[0], cogType]
			try: doculectCognateDict[doculect].append(cogid)
			except: doculectCognateDict[doculect] = [cogid]
		else:
			pass
	# build up a list of cognate ids
	cogids.append(id)

cogids.sort()


# Now make a shared cognate across varieties data object to create a network structure
netFile = open(analysesFolder+"/"+analysesSubfolder+"/"+filePrefix + "-" + str(SCAthreshold) + str(LSthreshold) + cogType + "_thresholds" + "-cognates-Network" + ".tsv", "w")

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