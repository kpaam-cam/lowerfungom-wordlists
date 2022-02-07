import lingpy
from lingpy import *
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
from lingpy.convert.strings import write_nexus
import pandas
import os

# From Hantgan and List paper
def make_matrix(ref, wordlist, tree, tree_taxa):
    
    matrix = [[1 for i in tree_taxa] for j in tree_taxa]
    for i, tA in enumerate(tree_taxa):
        for j, tB in enumerate(tree_taxa):
            if i < j:
                cogsA = wordlist.get_dict(col=tA, entry=ref)
                cogsB = wordlist.get_dict(col=tB, entry=ref)
                shared, slots = 0, 0
                for key in set([k for k in cogsA] + [k for k in cogsB]):
                    if key in cogsB and key in cogsA:
                        if [c for c in cogsA[key] if c in cogsB[key]]:
                            shared += 1
                        slots += 1

                matrix[i][j] = shared / slots
                matrix[j][i] = shared / slots
    return matrix

# From Hantgan and List paper
def load_matrix(fname):
    data = csv2list(fname)
    taxa = [line[0].strip() for line in data]
    matrix = [[0 for i in taxa] for j in taxa]
    for i in range(len(taxa)):
        for j in range(1, len(taxa)+1):
            matrix[i][j-1] = float(data[i][j])
    return taxa, matrix

# By me to create a SplitsTree file
# I've adapted this to make a file to load into R as a matrix
def get_distances(fname):
	
	# I don't need this for the current implementation, but I kept it around for future reference
	def line_prepender(filename, line):
		with open(filename, 'r+') as f:
			content = f.read()
			f.seek(0, 0)
			f.write(line.rstrip('\r\n') + '\n' + content)
				
	inputfileName = fname
	outputfileName = fname + ".dst"
	
	sims = pandas.read_csv(inputfileName, sep = '\t', index_col=0, header=None) 
	
	dsts = sims.values
	dsts = 1 - sims.values
	dsts = dsts.round(decimals=2)

	dstdf = pandas.DataFrame(dsts)

	newcols = sims.index
	newcols = newcols.str.replace(' ', '')

	dstdf = dstdf.set_index(newcols) 

	dstdf.to_csv(outputfileName, sep = '\t', header=False)
	
	
	newheader = "Variety"
	for newcol in newcols:
		newheader = newheader + "\t" + newcol

	line_prepender(outputfileName,newheader)
	


# Because I'm adapting code from the Hantgan and List paper, I'll take the
# CLDF version and turn it into a version for this script
wordlists = pandas.read_csv("../cldf/forms.csv", ) 
entries = wordlists.to_dict(orient='records')

coverageLimit = 37
#outputFileName = "AllAvailableNew-" + str(coverageLimit) + "coverage"

# Original thresholds
SCAthreshold = 0.45
LSthreshold = 0.55

# Experimental thresholds
#SCAthreshold = 0.7
#LSthreshold = 0.7

SCAthreshStr = str(f'{(SCAthreshold):g}')
LSthreshStr = str(f'{(LSthreshold):g}')

outputFileName = "AllAvailableNew-" + str(coverageLimit) + "coverage"
thresholdStr = "-" + str(f'{(SCAthreshold):g}') + "_" + str(f'{(LSthreshold):g}') + "thresholds"


filePath = "../analyses/Phase2-NewLists/"
outputFile = open(filePath + outputFileName + ".tsv", "w")
header = "ID\tConcept\tDoculect\tValue\tTokens"
outputFile.write(header + "\n")

# This make an index that helps exclude words that are not well represented in the lists
conceptIndex = { }
for entry in entries:

	Concept = entry["Parameter_ID"]
	Doculect = entry["Language_ID"]
	
	try:
		conceptIndex[Concept] = conceptIndex[Concept] + 1
	except:
		conceptIndex[Concept] = 1

ID = 1
analyzedConcepts = { }
for entry in entries:

	Concept = entry["Parameter_ID"]
	Form = entry["Value"]
	Segments = entry["Segments"]
	Doculect = entry["Language_ID"]
	
	#skip concepts that don't have a lot of coverage depending on where the threshold is set
	if conceptIndex[Concept] >= coverageLimit:
		#print(Concept, conceptIndex[Concept])
		pass
		try:
			analyzedConcepts[Concept] = analyzedConcepts[Concept] + 1
		except: analyzedConcepts[Concept] = 1
	else: continue
	
	s = "\t"
	output = s.join([str(ID),str(Concept),str(Doculect),str(Form),str(Segments)])
	outputFile.write(output + "\n")
	ID = ID + 1

outputFile.close()

# Main part of script
try:
	#If the LexStat calculations have been done already use those
	lex = LexStat(filePath + outputFileName + ".tsv.bin.tsv")
except:
	lex = LexStat(filePath + outputFileName + ".tsv")
	lex.get_scorer(runs=10000, restricted_chars='_')
	lex.output('tsv', filename=lex.filename+'.bin', ignore='')

# Use this line if not using LexStat
#lex = LexStat(filePath + outputFileName + ".tsv.bin.tsv")

lex.cluster(method='sca', threshold=SCAthreshold, ref='scaid', restricted_chars='_')
lex.calculate('tree', ref='scaid')


lex.cluster(method='lexstat', threshold=LSthreshold, restricted_chars='_',
 		ref='lexstatid', cluster_method='infomap')
p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=True)

#print('SuSe {0:.2f} {1:.2f} {2:.2f}'.format(p, r, f))

lex.output('tsv', filename=lex.filename+'-cognates' + thresholdStr, ignore='all')
lex.calculate('tree', ref='lexstatid')
 
tm, tree_taxa = nwk2tree_matrix(lex.tree)
matrix1 = make_matrix('lexstatid', lex, lex.tree, tree_taxa)
matrix2 = make_matrix('scaid', lex, lex.tree, tree_taxa)

plot_heatmap(lex, ref='scaid', filename=filePath + outputFileName + thresholdStr + '-SCA', vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)

plot_heatmap(lex, ref='lexstatid', filename=filePath + outputFileName + thresholdStr + '-LexStat', vmax=1,
            tree=lex.tree, colorbar_label='lexical cognates',
            normalized='swadesh', steps = 45,
            )

_, matrix1 = load_matrix(filePath + outputFileName + thresholdStr + '-LexStat.matrix')
_, matrix2 = load_matrix(filePath + outputFileName + thresholdStr + '-SCA.matrix')

new_matrix = [[0 for x in range(len(matrix1[0]))] for y in
		range(len(matrix1))]
for _i in range(len(matrix1)):
	for _j in range(len(matrix1)):
		new_matrix[_i][_j] = 0.5 + (matrix2[_i][_j] - matrix1[_i][_j])
plot_heatmap(lex, matrix=new_matrix, tree=lex.tree,
		colorbar_label='differences (inferred cognates)', filename=filePath + outputFileName + thresholdStr + '-SCALexStatDifferences',
		vmax=0.7, vmin=0.3, steps = 45,)

# Calling plot_heatmap in this way produces an empty matrix file; delete it to keep things clean
os.remove(filePath + outputFileName + thresholdStr + '-SCALexStatDifferences.matrix')


alm = Alignments(lex, ref='lexstatid')
alm.align()
alm.output('html', filename=filePath + outputFileName + thresholdStr + "-LSCognateAlignments")

alm = Alignments(lex, ref='scaid')
alm.align()
alm.output('html', filename=filePath + outputFileName + thresholdStr + "-SCACognateAlignments")


write_nexus(lex, mode="splitstree", ref="scaid", filename=filePath + outputFileName + thresholdStr + '-SCA.nex')
write_nexus(lex, mode="splitstree", ref="lexstatid", filename=filePath + outputFileName + thresholdStr + '-LexStat.nex')
		
get_distances(filePath + outputFileName + thresholdStr + '-LexStat.matrix')
get_distances(filePath + outputFileName + thresholdStr + '-SCA.matrix')


for analyzedConcept in analyzedConcepts:
	print(str(analyzedConcept) + "\t" + str(analyzedConcepts[analyzedConcept]))

#etd = lex.get_etymdict(ref='lexstatid')
#for k, vals in etd.items():
#	print(k, vals)