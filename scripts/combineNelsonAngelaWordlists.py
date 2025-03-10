# Step 1 to prepare new wordlists for analysis
# To be used with prepareParallelListsForCLDF-wNewWordlists.py
# Maybe combine these?

import pandas
import math
import shutil

speakerIDs = [
 			"NGT-Abar-3-ANT",
 			]

wordlists =	[
	"KPAAM-CAM-IDPNgongGastonTembe-AbarReduced",
	]

# New Biya editing
# Changed "cow" to "cow, cattle"
# Deleted bush and bush-cow since empty
# Change "bamboo" to "raffia bamboo" (294)
# Change eder to "elder (birth)" (24)
# Change hot (solid) to 890
# Change kernel bark to 269
# Change bed bug to 815
# Deleted mat (but in earlier list)
# metal-ankle-rattles for men or women?
# changed palm nut pestle to 268
# change ram (male sheep) to 685
# changed water-frog (green, variegated) to 735 (but not data anyway...)
# How did "cotton-palm" get added to earlier list? Was Biya re-entered? (Deleted on the new lists, will need for old)

# Seem to be two hand (plantain), needs rectified


shutil.copyfile("../raw/AllWordlists-OneEntryPerRow-wNewLists-withDPJ.tsv", "../raw/AllWordlists-OneEntryPerRow-wNewLists-withDPJ-withAngela.tsv")


outputFilePathName = "../raw/" + "AllWordlists-OneEntryPerRow-wNewLists-withDPJ-withAngela.tsv"
#outputFile = open(outputFilePathName, "a")
#header = "ID\tConcept\tDoculect\tValue"
#outputFile.write(header + "\n")
#outputFile.close()	

# Make concept dictionary
conceptFilePathName = "../raw/ConceptList.csv"
conceptList = pandas.read_csv(conceptFilePathName) 
concepts = conceptList.to_dict(orient='records')
conceptDict = { }
for concept in concepts:
	OrderingID = concept["OrderingID"]
	ConceptLabel = concept["Concept"]
	conceptDict[OrderingID] = ConceptLabel

# Need to be able set the counter properly
# See https://stackoverflow.com/questions/845058/how-to-get-the-line-count-of-a-large-file-cheaply-in-python
ID = sum(1 for _ in open(outputFilePathName)) # Not sure why I don't need ot subtract one for the header...mysteries


# Now process wordlists
for wordlist in wordlists:

	outputFile = open(outputFilePathName, "a")
	#print("WL:", wordlist)

	wordlistExcel = pandas.ExcelFile("../raw/" + wordlist + ".xlsx" )
	wordlists = wordlistExcel.parse(0)
	entries = wordlists.to_dict(orient='records')

	for entry in entries:

		concept = entry["Concept"]
		#print(concept)
				
		for speakerID in speakerIDs:
			try:
				entry[speakerID]
				#print(entry[speakerID])
			except:
				print("Expected speaker ID missing: ", speakerID)

		for speakerID in speakerIDs:
			try:
				ConceptLabel =  conceptDict[int(concept)]
			except:
				print("No concept entry found for: ", concept)
				ConceptLabel = None


			if concept == concept and ConceptLabel: # Hack to ignore NaN concepts, NaN won't return true here; for Angela ignore missing concepts
				
				joinChar = "\t"
				output = joinChar.join([str(ID),ConceptLabel,str(speakerID),str(entry[speakerID])])			
				outputFile.write(output + "\n")

				ID = ID + 1
	
	outputFile.close()	

"""
outputFilePathName = "../raw/" + "AllWordlists" + "-OneEntryPerRow.tsv"
outputFile = open(outputFilePathName, "w")
header = "ID\tConcept\tDoculect\tValue"
outputFile.write(header + "\n")
outputFile.close()	


	entries = wordlists.to_dict(orient='records')

	outputFile = open(outputFilePathName, "a")


	ID = 1
	for entry in entries:

		OrderingID = entry["OrderingID"]
		Concept = entry["Concept"]
				
		for speakerInfo in speakerInfos:
			speakerID, glottocode = speakerInfo
			
			# clean up Fang and Biya capitalization issue; this is a messy solution. Maybe fix in database instead?
			# Note partial code repetition in the languages output below
			printID = ""
			if speakerID == "KHK-FANG-12":
				printID = "KHK-Fang-12"
			elif speakerID == "DPN-FANG-13":
				printID = "DPN-Fang-13"
			elif speakerID == "ENB-BIYA-1":
				printID = "ENB-Biya-1"
			elif speakerID == "ICN-BIYA-2":
				printID = "ICN-Biya-2"
			else: printID = speakerID
						
			# Only write out a line if there is a column for a given speaker
			try: entry[speakerID]
			except: continue
			
			s = "\t"
			output = s.join([str(ID),str(Concept),str(printID),str(entry[speakerID])])
			outputFile.write(output + "\n")

			ID = ID + 1
	
	outputFile.close()	


	# Generate auxiliary files in the raw folder for CLDF processing
	# We'll use the existing ones for now since we don't want to overwrite these for
	# in each case. New code will probably be needed to create these moving forward.
	wl = Wordlist("../raw/" + wordlist + "-oneEntryPerRow.tsv")
	with open('../etc/languages.tsv', 'w', encoding='utf8') as f:
		f.write('ID\tName\tGlottocode\tSubGroup\tLatitude\tLongitude\n')
		for doculect in wl.cols:
			glottocode = ""
			for speakerInfo in speakerInfos:
				# Since speakerID is also doculect ID, we use this to get the right glottolog linked to the speaker using list above
				speakerID, glottocode = speakerInfo
				# clean up Fang and Biya capitalization issue; this is a messy solution. Maybe fix in database instead?
				printID = ""
				if speakerID == "KHK-FANG-12":
					printID = "KHK-Fang-12"
				elif speakerID == "DPN-FANG-13":
					printID = "DPN-Fang-13"
				elif speakerID == "ENB-BIYA-1":
					printID = "ENB-Biya-1"
				elif speakerID == "ICN-BIYA-2":
					printID = "ICN-Biya-2"
				else: printID = speakerID

				if printID == doculect:
					f.write(slug(printID, lowercase=False) + '\t' + printID +'\t' + glottocode + '\t\t\n')

	with open('../etc/concepts.tsv', 'w', encoding='utf8') as f:
		f.write('NUMBER\tENGLISH\tPOS\n')
		cmap = {}
		for idx, concept in wl.iter_rows('concept'):
			if concept in cmap:
				pass
			cmap[concept] = "N/A" #hack for no POS
		for i, (concept, pos) in enumerate(sorted(cmap.items())):
			f.write(str(i+1)+'\t'+concept+'\t'+pos+'\n')

"""