"""

"""
import pathlib
import itertools

import pandas
from lingpy import LexStat, Alignments, csv2list
from lingpy.convert.plot import plot_heatmap
from lingpy.evaluate.acd import bcubes

from lexibank_kpaamcam import Dataset


def register(parser):
    pass


def run(args):
    ds = Dataset()
    cldf = ds.cldf_reader()

    def outpath(fname):
        return str(ds.dir / 'analyses' / fname)

    D = {0: ['concept', 'doculect', 'value', 'tokens']}

    for i, ((concept, doculect), forms) in enumerate(itertools.groupby(
        sorted(cldf['FormTable'], key=lambda f: (f['Parameter_ID'], f['Language_ID'])),
        lambda f: (f['Parameter_ID'], f['Language_ID']),
    ), start=1):
        for form in forms:
            D[i] = [concept, doculect, form['Form'], form['Segments']]
            break  # We only take the first form variant per concept/doculect pair.

    lex = LexStat(D)
    lex.get_scorer(runs=10000, restricted_chars='_')
    #lex.output('tsv', filename=lex.filename + '.bin', ignore='')

    lex.cluster(method='sca', threshold=0.45, ref='scaid', restricted_chars='_')
    lex.calculate('tree', ref='scaid')

    lex.cluster(method='lexstat', threshold=0.55, restricted_chars='_',
            ref='lexstatid', cluster_method='infomap')
    p, r, f = bcubes(lex, 'lexstatid', 'scaid', pprint=False)

    print('SuSe {0:.2f} {1:.2f} {2:.2f}'.format(p, r, f))

    lex.output('tsv', filename=outpath(lex.filename + '-cognates'), ignore='all')
    lex.calculate('tree', ref='lexstatid')

    plot_heatmap(lex, ref='scaid', filename=outpath('LowerFungom-SCA'), vmax=1,
             tree=lex.tree, colorbar_label='lexical cognates',
             normalized='swadesh'
             )

    plot_heatmap(lex, ref='lexstatid', filename=outpath('LowerFungom-LexStat'), vmax=1,
             tree=lex.tree, colorbar_label='lexical cognates',
             normalized='swadesh',
             )

    _, matrix1 = load_matrix(outpath('LowerFungom-LexStat.matrix'))
    _, matrix2 = load_matrix(outpath('LowerFungom-SCA.matrix'))

    new_matrix = [[0 for x in range(len(matrix1[0]))] for y in
              range(len(matrix1))]
    for _i in range(len(matrix1)):
        for _j in range(len(matrix1)):
            new_matrix[_i][_j] = 0.5 + (matrix2[_i][_j] - matrix1[_i][_j])
    plot_heatmap(lex, matrix=new_matrix, tree=lex.tree,
             colorbar_label='differences (inferred cognates)', filename=outpath('LowerFungom-SCALexStatDifferences'),
             vmax=0.7, vmin=0.3)

    # Calling plot_heatmap in this way produces an empty matrix file; delete it to keep things clean
    pathlib.Path(outpath('LowerFungom-SCALexStatDifferences.matrix')).unlink()

    get_distances(outpath('LowerFungom-LexStat.matrix'))
    get_distances(outpath('LowerFungom-SCA.matrix'))

    alm = Alignments(lex, ref='scaid')
    alm.align()
    alm.output('html', filename=outpath("LowerFungom-CognateAlignments"))


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
        for j in range(1, len(taxa) + 1):
            matrix[i][j - 1] = float(data[i][j])
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

    sims = pandas.read_csv(inputfileName, sep='\t', index_col=0, header=None)
    dsts = 1 - sims.values

    dstdf = pandas.DataFrame(dsts)
    dstdf = dstdf.set_index(sims.index)

    dstdf.to_csv(outputfileName, header=None, sep='\t')

    line_prepender(outputfileName, str(len(sims.index)))
