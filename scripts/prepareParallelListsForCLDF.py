import pandas
from lingpy import *
from clldutils.misc import slug

speakerInfos = [
			[	"NVB-Abar-7", "abar1239"	],
			[	"ECL-Abar-8", "abar1239"	],
 			[	"NMA-Abar-1", "abar1239"	],
			[	"NAC-Abar-2", "abar1239"	],
			[	"NEM-Ajumbu-9", "mbuu1238"	],
			[	"NVI-Ajumbu-1", "mbuu1238"	],
			[	"KMN-Ajumbu-2", "mbuu1238"	],
			[	"KDC-Ajumbu-10", "mbuu1238"	],
			[	"ENB-BIYA-1", "biya1235"	],
			[	"ICN-BIYA-2", "biya1235"	],
			[	"NNB-Buu-3", "buuu1246"	],
			[	"MNJ-Buu-4", "buuu1246"	],
			[	"KEM-Buu-1", "buuu1246"	],
			[	"KCY-Buu-2", "buuu1246"	],
			[	"KHK-FANG-12", "fang1248"	],
			[	"DPN-FANG-13", "fang1248"	],
			[	"KDV-Fang-1", "fang1248"	],
			[	"KJS-Fang-2", "fang1248"	],
			[	"JGY-Koshin-3", "kosh1246"	],
			[	"TEL-Koshin-4", "kosh1246"	],
			[	"DPJ-Koshin-1", "kosh1246"	],
			[	"MRY-Koshin-2", "kosh1246"	],
			[	"KCS-Kung-3", "kung1260"	],
			[	"NJS-Kung-4", "kung1260"	],
			[	"ZKG-Kung-1", "kung1260"	],
			[	"BNM-Kung-2", "kung1260"	],
			[	"NMN-Mundabli-3", "mund1340"	],
			[	"CEN-Mundabli-2", "mund1340"	],
			[	"LFN-Mundabli-1", "mund1340"	],
			[	"NIN-Mundabli-4", "mund1340"	],
			[	"NGT-Munken-3", "munk1244"	],
			[	"NUN-Munken-4", "munk1244"	],
			[	"NEA-Munken-1", "munk1244"	],
			[	"TNT-Munken-2", "munk1244"	],
			[	"MCA-Ngun-3", "ngun1279"	],
			[	"KBM-Ngun-4", "ngun1279"	],
 			[	"WCA-Ngun-1", "ngun1279"	],
			[	"AOM-Ngun-2", "ngun1279"	],
			[	"APB-Mumfu-1", "mufu1234"	],
 			[	"DNM-Mumfu-2", "mufu1234"	],
 			[	"BKB-Mashi-2", "naki1238"	],
 			[	"KFK-Mashi-1", "naki1238"	],
 			[	"ABS-Missong-1", "miss1255"	],
 			[	"AGA-Missong-2", "miss1255"	],
			]	



wordlists =	[
	#"parallel_lists_all13",
	#"parallel_lists-long10",
	#"parallel_lists_removeFormsTest",
	#"parallel_lists-LeftJoin",
	#"parallel_lists_allavailable",
	"all_available_wordlists_duplicatesAdjusted",
	]

for wordlist in wordlists:

	wordlists = pandas.read_csv("../raw/" + wordlist + ".csv", ) 
	entries = wordlists.to_dict(orient='records')
	newTable = { }

	outputFile = open("../raw/" + wordlist + "-oneEntryPerRow.tsv", "w")
	header = "ID\tConcept\tDoculect\tValue"
	outputFile.write(header + "\n")

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
