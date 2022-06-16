"""
Run cognate analyses of wordlists and produce associated outputs
"""

from lingpy import *
from lexibank_kpaamcamlowerfungom import Dataset
from lingpy.evaluate.acd import bcubes
from lingpy.convert.tree import *
from lingpy.convert.plot import plot_heatmap
from lingpy.convert.strings import write_nexus
import pandas
import os


def run(args):
    
    # To be implemented later?
    # coverageLimit = 37 # How many wordlists the concept needs to be in

	# SCA and LexStat similarity thresholds
	SCAthreshold = 0.45
	LSthreshold = 0.55

    # default import of data with lingpy
	KPLF = Dataset()
    
    # Code from Robert Forkel to handle cases where CLDF contains multiple forms for same
    # concept. Not using now since that filtering is happening at CLDF creation stage
	# D = {0: ['concept', 'doculect', 'value', 'tokens']}
	# 
	# for i, ((concept, doculect), forms) in enumerate(itertools.groupby(
	# 	sorted(cldf['FormTable'], key=lambda f: (f['Parameter_ID'], f['Language_ID'])),
	# 	lambda f: (f['Parameter_ID'], f['Language_ID']),
	# ), start=1):
	# 	for form in forms:
	# 		D[i] = [concept, doculect, form['Form'], form['Segments']]
	# 		break  # We only take the first form variant per concept/doculect pair.

    
	lex = LexStat.from_cldf(
            KPLF.cldf_dir.joinpath("cldf-metadata.json")
            )
    
    # Get SCA alignments
	lex.cluster(method="sca", ref="scaid", threshold=SCAthreshold)
	alm = Alignments(lex, ref="scaid")
	alm.align()
	alm.output(
            "tsv", 
            filename=KPLF.dir.joinpath(
                "analyses", "Phase3-Summer2022", "kplf-SCA-"+str(SCAthreshold)+"_threshold-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
	# This broke with the new orthographic mapping designed to not use tone in the comparison
	#alm.output('html',
    #	filename=KPLF.dir.joinpath(
    #           "analyses", "Phase3-Summer2022", "kplf-SCA-"+str(SCAthreshold)+"_threshold-aligned").as_posix()
    #            )
    
    # Get SCA distances and tree        
	lex.calculate('tree', ref='scaid')
	tm, tree_taxa = nwk2tree_matrix(lex.tree)
	SCAmatrix = make_matrix('scaid', lex, lex.tree, tree_taxa)
	plot_heatmap(lex, ref='scaid',
		filename=KPLF.dir.joinpath(
                "analyses", "Phase3-Summer2022", "kplf-SCA"+str(SCAthreshold)+"_threshold-heatmap").as_posix(),
		vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)


    # Get LexStat alignments
	lex.get_scorer(runs=10000, restricted_chars='_')
	lex.cluster(method='lexstat', threshold=LSthreshold, restricted_chars='_',
 		ref='lexstatid', cluster_method='infomap')
	alm = Alignments(lex, ref="lexstatid")
	alm.align()
	alm.output(
            "tsv", 
            filename=KPLF.dir.joinpath(
                "analyses", "Phase3-Summer2022", "kplf-LS-"+str(LSthreshold)+"_threshold-aligned").as_posix(),
            ignore="all",
            prettify=False
            )
	# This broke with the new orthographic mapping designed to not use tone in the comparison
	#alm.output('html',
    #	filename=KPLF.dir.joinpath(
    #            "analyses", "Phase3-Summer2022", "kplf-LS-"+str(LSthreshold)+"_threshold-aligned").as_posix()
    #            )

    # Get LexStat distances and tree        
	lex.calculate('tree', ref='lexstatid')
	tm, tree_taxa = nwk2tree_matrix(lex.tree)
	LSmatrix = make_matrix('lexstatid', lex, lex.tree, tree_taxa)
	plot_heatmap(lex, ref='lexstatid',
		filename=KPLF.dir.joinpath(
                "analyses", "Phase3-Summer2022", "kplf-LS"+str(LSthreshold)+"_threshold-heatmap").as_posix(),
		vmax=1,
		tree=lex.tree, colorbar_label='lexical cognates',
		normalized='swadesh', steps = 45,
		)


	# Some comparisons (but I don't recall if I'm using these at all)
	p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=True)


	# To do: Can I fix the HTML output (maybe with different orth profile?)
	# Add in code to write matrix and nexus files
	# Write in the diff heatmap matrix code
	# Two above should be straightforward but need to adjust directory issues
	# Build in logic to specify concept coverage threshold for analysis based on earlier code
	# Build in functions for assessing concept stability
	# Clean things?
	# Add new wordlists?


	args.log.info("[i] computed alignments and wrote them to file along with other analytical outputs")



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

# By me originally to create a SplitsTree file, but there's a built-in function for this.
# So, I've adapted this to make a file to load into R as a matrix
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