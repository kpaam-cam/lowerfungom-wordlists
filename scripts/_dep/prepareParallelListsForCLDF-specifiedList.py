import pandas
from lingpy import *
from clldutils.misc import slug

wordlists = pandas.read_csv("../raw/parallel_lists_all13.csv", ) 
entries = wordlists.to_dict(orient='records')
newTable = { }

speakerInfos = [
			[	"NVB-Abar-7", "abar1239"	],
			[	"ECL-Abar-8", "abar1239"	],
			[	"NEM-Ajumbu-9", "mbuu1238"	],
			[	"KDC-Ajumbu-10", "mbuu1238"	],
			[	"ENB-BIYA-1", "biya1235"	],
			[	"ICN-BIYA-2", "biya1235"	],
			[	"NNB-Buu-3", "buuu1246"	],
			[	"MNJ-Buu-4", "buuu1246"	],
			[	"KHK-FANG-12", "fang1248"	],
			[	"DPN-FANG-13", "fang1248"	],
			[	"JGY-Koshin-3", "kosh1246"	],
			[	"TEL-Koshin-4", "kosh1246"	],
			[	"KCS-Kung-3", "kung1260"	],
			[	"NJS-Kung-4", "kung1260"	],
			[	"NMN-Mundabli-3", "mund1340"	],
			[	"CEN-Mundabli-2", "mund1340"	],
			[	"NGT-Munken-3", "munk1244"	],
			[	"NUN-Munken-4", "munk1244"	],
			[	"MCA-Ngun-3", "ngun1279"	],
			[	"KBM-Ngun-4", "ngun1279"	],
			[	"APB-Mumfu-1", "mufu1234"	],
			[	"DNM-Mumfu-2", "mufu1234"	],
			[	"BKB-Mashi-2", "naki1238"	],
			[	"KFK-Mashi-1", "naki1238"	],
			[	"ABS-Missong-1", "miss1255"	],
			[	"AGA-Missong-2", "miss1255"	],
			]	


outputFile = open("../raw/oneEntryPerRow-wordlist.tsv", "w")
header = "ID\tConcept\tDoculect\tValue"
outputFile.write(header + "\n")

ID = 1
for entry in entries:

	OrderingID = entry["OrderingID"]
	Concept = entry["Concept"]
	
	for speakerInfo in speakerInfos:

		speakerID, glottocode = speakerInfo
		
		# Only write out a line if there is a column for a given speaker
		try: entry[speakerID]
		except: continue

		s = "\t"
		output = s.join([str(ID),str(Concept),str(speakerID),str(entry[speakerID])])
		outputFile.write(output + "\n")
		ID = ID + 1

outputFile.close()


# Generate auxiliary files in the raw folder for CLDF processing
wl = Wordlist('../raw/oneEntryPerRow-wordlist.tsv')
with open('../etc/languages.tsv', 'w', encoding='utf8') as f:
    f.write('ID\tName\tGlottocode\tSubGroup\tLatitude\tLongitude\n')
    for doculect in wl.cols:
    	print(doculect)
    	glottocode = ""
    	for speakerInfo in speakerInfos:
    		# Since speakerID is also doculect ID, we use this to get the right glottolog linked to the speaker using list above
    		speakerID, glottocode = speakerInfo
    		if speakerID == doculect:
    			f.write(slug(doculect, lowercase=False) + '\t' + doculect +'\t' + glottocode + '\t\t\n')

with open('../etc/concepts.tsv', 'w', encoding='utf8') as f:
    f.write('NUMBER\tENGLISH\tPOS\n')
    cmap = {}
    for idx, concept in wl.iter_rows('concept'):
        if concept in cmap:
            pass
        cmap[concept] = "N/A" #hack for no POS
    for i, (concept, pos) in enumerate(sorted(cmap.items())):
        f.write(str(i+1)+'\t'+concept+'\t'+pos+'\n')
