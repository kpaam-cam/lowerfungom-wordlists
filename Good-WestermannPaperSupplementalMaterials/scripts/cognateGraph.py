# generates a network file to be used in R to generate lexical network graph

from lingpy import Wordlist

# Storage folders
analysesFolder = "../analyses"
filePrefix = "kplfSubset"


# SCA and LexStat similarity thresholds
SCAthreshold = 0.45

wl = Wordlist(analysesFolder + "/" + filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognates" + ".tsv")
cogType = "scaid" # Pick cogtype to use (e.g., SC vs. LexStat)
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


# Now make a shared cognate network across varieties data object to create a network structure
netFile = open(analysesFolder+"/"+filePrefix + "-" + str(SCAthreshold) + "_thresholds" + "-cognates-Network" + ".tsv", "w")

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