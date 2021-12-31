from lingpy import *
from collections import defaultdict
from matplotlib import pyplot as plt
import colorsys
from sys import argv

ref = 'lexstatid'

wl = Wordlist('../analyses/AllAvailable-33coverage.tsv-cognates.tsv')
langs = csv2list('../cldf/languages.csv', sep=",")

# make dictionary to get the groups quickly from a language name
lang2group = {k[0]: k[2] for k in langs[1:]}

#print(lang2group)

patterns = {l: [] for l in lang2group}
allpats = defaultdict(list)

etd = wl.get_etymdict(ref=ref)
for k, vals in etd.items():
    idxs = [v[0] for v in vals if v and wl[v[0], 'doculect'] in lang2group]
    lngs = [wl[idx, 'doculect'] for idx in idxs]
    groups = defaultdict(list)
    for idx, lng in zip(idxs, lngs):
        groups[lang2group[lng]] += [lng]
    gstruc = ' '.join(['{0}:{1}'.format(y, len(groups[y])) for y in
        sorted(groups)])
    for idx, lng in zip(idxs, lngs):
        patterns[lng] += [(gstruc, idx)]
    allpats[gstruc] += [k]

#print(allpats)

bars1 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars2 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars3 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars4 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars5 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars6 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars7 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars8 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars9 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars10 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars11 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars12 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bars13 =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

with open('../analyses/cognatePatterns-{0}.tsv'.format(ref), 'w') as f:
    f.write('Pattern\tabar1239\tbiya1235\tbuuu1246\tfang1248\tkosh1246\tkung1260\tmbuu1238\tmiss1255\tmufu1234\tmund1340\tmunk1244\tnaki1238\tngun1279\tExamples\tCOGID\n')
    for k, v in allpats.items():
        nums = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
        grps = [ "abar1239", "biya1235", "buuu1246", "fang1248", "kosh1246", "kung1260", "mbuu1238", "miss1255", "mufu1234", "mund1340", "munk1244", "naki1238", "ngun1279", ]
        cncs = [wl[[y[0] for y in etd[cogid] if y][0], 'concept'] for cogid in
                v]
        for key in k.split():
            a, b = key.split(':')
            kidx = grps.index(a)
            nums[kidx] = b
        f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(k, '\t'.join(nums),
            len(v), ' '.join([str(x) for x in
            v]), ', '.join(cncs)))

        if 'abar1239' in k:
        	# numberfy the string numbers
            nums = [int(x) for x in nums]
            if nums.count(0) >= 11:	# Check these numbers. I think they need adjusted. Should be 11 for unique sharing
            ## Still don't understand what these charts mean exactly
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'abar1239':
                        this_lng = a
                        bars1[i] += len(v) # this is for roots shared with one other language
            elif nums.count(0) == 12:
                bars1[0] += len(v) # this is for unique roots in l. The column needs to be the "right" one here. This is a kind of awkward code design!
            else:
                bars1[-1] += len(v) # this is the wastebasket for things shared with 2+ languges

        if 'biya1235' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'biya1235':
                        this_lng = a
                        bars2[i] += len(v)
            elif nums.count(0) == 12:
                bars2[1] += len(v)
            else:
                bars2[-1] += len(v)

        if 'buuu1246' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'buuu1246':
                        this_lng = a
                        bars3[i] += len(v)
            elif nums.count(0) == 12:
                bars3[2] += len(v)
            else:
                bars3[-1] += len(v)
 
        if 'fang1248' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'fang1248':
                        this_lng = a
                        bars4[i] += len(v)
            elif nums.count(0) == 12:
                bars4[3] += len(v)
            else:
                bars4[-1] += len(v)

        if 'kosh1246' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'kosh1246':
                        this_lng = a
                        bars5[i] += len(v)
            elif nums.count(0) == 12:
                bars5[4] += len(v)
            else:
                bars5[-1] += len(v)

        if 'kung1260' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'kung1260':
                        this_lng = a
                        bars6[i] += len(v)
            elif nums.count(0) == 12:
                bars6[5] += len(v)
            else:
                bars6[-1] += len(v)

        if 'mbuu1238' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'mbuu1238':
                        this_lng = a
                        bars7[i] += len(v)
            elif nums.count(0) == 12:
                bars7[6] += len(v)
            else:
                bars7[-1] += len(v)

        if 'miss1255' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'miss1255':
                        this_lng = a
                        bars8[i] += len(v)
            elif nums.count(0) == 12:
                bars8[7] += len(v)
            else:
                bars8[-1] += len(v)

        if 'mufu1234' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'mufu1234':
                        this_lng = a
                        bars9[i] += len(v)
            elif nums.count(0) == 12:
                bars9[8] += len(v)
            else:
                bars9[-1] += len(v)

        if 'mund1340' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'mund1340':
                        this_lng = a
                        bars10[i] += len(v)
            elif nums.count(0) == 12:
                bars10[9] += len(v)
            else:
                bars10[-1] += len(v)

        if 'munk1244' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'munk1244':
                        this_lng = a
                        bars11[i] += len(v)
            elif nums.count(0) == 12:
                bars11[10] += len(v)
            else:
                bars11[-1] += len(v)

        if 'naki1238' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'naki1238':
                        this_lng = a
                        bars12[i] += len(v)
                        print("A", nums, v, k)
            elif nums.count(0) == 12:
                bars12[11] += len(v)
                print("B", nums, v, len(v), k)
            else:
                bars12[-1] += len(v)
                print("C", nums, v, len(v), k)

        if 'ngun1279' in k:
            nums = [int(x) for x in nums]
            if nums.count(0) == 11:
                for i, (a, b) in enumerate(zip(grps, nums)):
                    if b > 0 and a != 'ngun1279':
                        this_lng = a
                        bars13[i] += len(v)
            elif nums.count(0) == 12:
                bars13[12] += len(v)
            else:
                bars13[-1] += len(v)




plt.clf()
labels = grps + ['?']
explode = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.4]
plt.pie(bars1, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/abar1239-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars2, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/biya1235-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars3, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/buuu1246-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars4, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/fang1248-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars5, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/kosh1246-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars6, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/kung1260-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars7, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/mbuu1238-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars8, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/miss1255-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars9, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/mufu1234-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars10, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/mund1340-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars11, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/munk1244-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars12, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/naki1238-{0}.pdf'.format(ref))

plt.clf()
#explode = [0.2, 0.0, 0.0, 0.2, 0.2, 0.2]
plt.pie(bars13, explode=explode, labels=labels, shadow=True,
        startangle=140, autopct='%1.1f%%')
plt.axis('equal')
plt.savefig('../analyses/ngun1279-{0}.pdf'.format(ref))
