import lingpy
from lingpy import *
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
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
def get_distances(fname):
	
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

	dstdf = pandas.DataFrame(dsts)
	dstdf = dstdf.set_index(sims.index) 

	dstdf.to_csv(outputfileName, header=None, sep = '\t')

	line_prepender(outputfileName,str(len(sims.index)))

# Because I'm adapting code from the Hantgan and List paper, I'll take the
# CLDF version and turn it into a version for this script
wordlists = pandas.read_csv("../cldf/forms.csv", ) 
entries = wordlists.to_dict(orient='records')
outputFile = open("../analyses/LowerFungom-FormsForLexstat.tsv", "w")
header = "ID\tConcept\tDoculect\tValue\tTokens"
outputFile.write(header + "\n")
ID = 1
for entry in entries:
	Concept = entry["Parameter_ID"]
	Form = entry["Value"]
	Segments = entry["Segments"]
	Doculect = entry["Language_ID"]
	s = "\t"
	output = s.join([str(ID),str(Concept),str(Doculect),str(Form),str(Segments)])
	outputFile.write(output + "\n")
	ID = ID + 1
outputFile.close()

# Main part of script
try:
	#If the LexStat calculations have been done already use those
	lex = LexStat('../analyses/LowerFungom-FormsForLexstat.tsv.bin.tsv')
except:
	lex = LexStat('../analyses/LowerFungom-FormsForLexstat.tsv')
	lex.get_scorer(runs=10000, restricted_chars='_')
	lex.output('tsv', filename=lex.filename+'.bin', ignore='')

lex.cluster(method='sca', threshold=0.45, ref='scaid', restricted_chars='_')
lex.calculate('tree', ref='scaid')

lex.cluster(method='lexstat', threshold=0.55, restricted_chars='_',
 		ref='lexstatid', cluster_method='infomap')
p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=False)

print('SuSe {0:.2f} {1:.2f} {2:.2f}'.format(p, r, f))
 
lex.output('tsv', filename=lex.filename+'-cognates', ignore='all')
lex.calculate('tree', ref='lexstatid')
 
tm, tree_taxa = nwk2tree_matrix(lex.tree)
matrix1 = make_matrix('lexstatid', lex, lex.tree, tree_taxa)
matrix2 = make_matrix('scaid', lex, lex.tree, tree_taxa)

plot_heatmap(lex, ref='scaid', filename='../analyses/LowerFungom-SCA', vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh'
		)

plot_heatmap(lex, ref='lexstatid', filename='../analyses/LowerFungom-LexStat', vmax=1,
            tree=lex.tree, colorbar_label='lexical cognates',
            normalized='swadesh',
            )

_, matrix1 = load_matrix('../analyses/LowerFungom-LexStat.matrix')
_, matrix2 = load_matrix('../analyses/LowerFungom-SCA.matrix')

new_matrix = [[0 for x in range(len(matrix1[0]))] for y in
		range(len(matrix1))]
for _i in range(len(matrix1)):
	for _j in range(len(matrix1)):
		new_matrix[_i][_j] = 0.5 + (matrix2[_i][_j] - matrix1[_i][_j])
plot_heatmap(lex, matrix=new_matrix, tree=lex.tree,
		colorbar_label='differences (inferred cognates)', filename='../analyses/LowerFungom-SCALexStatDifferences',
		vmax=0.7, vmin=0.3)
		
# Calling plot_heatmap in this way produces an empty matrix file; delete it to keep things clean
os.remove('../analyses/LowerFungom-SCALexStatDifferences.matrix')

		
get_distances('../analyses/LowerFungom-LexStat.matrix')
get_distances('../analyses/LowerFungom-SCA.matrix')


alm = Alignments(lex, ref='scaid')
alm.align()
alm.output('html', filename="../analyses/LowerFungom-CognateAlignments")

#etd = lex.get_etymdict(ref='lexstatid')
#for k, vals in etd.items():
#	print(k, vals)