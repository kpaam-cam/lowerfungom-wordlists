# Step 1 to prepare new wordlists for analysis
# To be used with prepareParallelListsForCLDF-wNewWordlists.py
# Maybe combine these?

import pandas
import math


outputFilePathName = "../raw/" + "OneEntryPerRow.tsv"
outputFile = open(outputFilePathName, "w")
header = "ID\tConcept\tDoculect\tValue"
outputFile.write(header + "\n")
outputFile.close()	

# Make concept dictionary
conceptFilePathName = "../raw/ConceptList.csv"
conceptList = pandas.read_csv(conceptFilePathName) 
concepts = conceptList.to_dict(orient='records')
conceptDict = { }
for concept in concepts:
	OrderingID = concept["OrderingID"]
	ConceptLabel = concept["Concept"]
	conceptDict[OrderingID] = ConceptLabel


# hack to work with legacy process
wordlistFile = "Grollemund-cognates.csv"


wordlists = pandas.read_csv("../raw/" + wordlistFile, header=0)
wordlists = wordlists.fillna('')

headernames = wordlists.columns.values.tolist()

# get rid of non-data headers
concepts = [ ]
for header in headernames:
	if header == "Language":
		pass
	elif header == "Sources":
		pass
	elif "Unnamed" in header:
		pass
	else:
		concepts.append(header)

FormsByLanguage = { }
for index, entry in wordlists.iterrows():

	language = entry["Language"]
	language = language.replace("*", "STAR_")
	
	# run through the row
	forms = { }
	for concept in concepts:
		form = entry[concept]
		# data cleaning
		form = form.replace("\n", " ")
		form = form.replace("\t", " ")
		forms[concept] = form
	FormsByLanguage[language] = forms


# Count up the forms per language to filter
formCounts = { }
for language in FormsByLanguage.keys():
	formCount = 0
	forms = FormsByLanguage[language]
	for concept in concepts:
		form = forms[concept]
		if form != "?":
			formCount = formCount + 1
	formCounts[language] = formCount


ID = 1
outputFile = open(outputFilePathName, "a")

for language in FormsByLanguage.keys():
	numberOfForms = formCounts[language]
	if numberOfForms >= 98:	
		forms = FormsByLanguage[language]
		for concept in concepts:
			form = forms[concept]
			joinChar = "\t"
			entry = joinChar.join([str(ID),str(concept),str(language),str(form)])
			outputFile.write(entry + "\n")
			ID = ID + 1
	else:
		pass
outputFile.close()	



"""
	concept = entry["Concept"]
	print(concept)
	
	for speakerID in speakerIDs:
		try:
			entry[speakerID]
			#print(entry[speakerID])
		except: continue

		if concept == concept: # Hack to ignore NaN concepts, NaN won't return true here
			
			ConceptLabel =  conceptDict[int(concept)]
			joinChar = "\t"
			output = joinChar.join([str(ID),ConceptLabel,str(speakerID),str(entry[speakerID])])			
			outputFile.write(output + "\n")

			ID = ID + 1

outputFile.close()	
"""

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