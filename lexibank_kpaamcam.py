import pathlib
import collections

from clldutils.misc import slug
from pylexibank import FormSpec
from pylexibank import Dataset as BaseDataset

speakerInfos = collections.OrderedDict([
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
])


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "LowerFungomIndividualWordlists"

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-", "ø"),  # characters that denote missing data. If missing singular, forces use of plural
        strip_inside_brackets=True,  # do you want data removed in brackets?
        replacements=[(' ', '_'), ('\u0300m', 'm')],  # replacements with spaces
        normalize_unicode = 'NFD'
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        args.writer.add_sources()

        concepts = {}
        for concept in self.concepts:
            idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
            similarity = int(concept['SIMILARITY'] or 4)
            args.writer.add_concept(
                ID=idx,
                Name=concept['ENGLISH'],
                Concepticon_ID=concept['CONCEPTICON_ID'] if similarity <= 2 else None,
                Concepticon_Gloss=concept['CONCEPTICON_GLOSS'] if similarity <= 2 else None,
            )
            concepts[concept['ENGLISH']] = idx

        for i, entry in enumerate(self.raw_dir.read_csv('parallel_lists.csv', dicts=True)):
            for lid, glottocode in speakerInfos.items():
                if i == 0:
                    args.writer.add_language(ID=lid, Name=lid, Glottocode=glottocode)
                if not entry[lid].strip():
                    continue
                r = args.writer.add_forms_from_value(
                    Value=entry[lid],
                    Language_ID=lid,
                    Parameter_ID=concepts[entry['Concept']],
                    Source=[]
                )
