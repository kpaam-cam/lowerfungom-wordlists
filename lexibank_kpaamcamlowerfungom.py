from pathlib import Path
from clldutils.misc import slug
from pylexibank import FormSpec, Lexeme, Concept, Language
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar
from lingpy import *
import attr


@attr.s
class CustomLanguage(Language):
    Variety = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "kpaamcamlowerfungom"
    language_class = CustomLanguage

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-", "ø", "øø", "ø / ø", "nan", "NULL", "0 / 0", "0"),  # characters that denote missing data. If missing singular, forces use of plural
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # We ignore all the plural forms
        replacements=[(' ', '_'), ('\u0300m', 'm')],  # replacements with spaces
        normalize_unicode = 'NFD'
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """

        # Write source
        args.writer.add_sources()

        # Write languages
        languages = args.writer.add_languages(lookup_factory='Name')



        # Write forms
        wl = Wordlist(self.raw_dir.joinpath('AllWordlists-OneEntryPerRow-wNewLists-noDPJ.tsv').as_posix())

        # select valid concepts already here
        best_140 = sorted(
                wl.rows,
                key=lambda x: len(wl.get_list(row=x, flat=True)),
                reverse=True)[:140]

        # Write concepts
        concepts = {}
        for concept in self.concepts:
            if concept["ENGLISH"] in best_140:
                idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
                args.writer.add_concept(
                        ID=idx,
                        Name=concept['ENGLISH'],
                        )
                concepts[concept['ENGLISH']] = idx

        for idx in progressbar(wl):
            if wl[idx, "concept"] in best_140:
                args.writer.add_forms_from_value(
                        Value=wl[idx, 'value'],
                        Language_ID=languages[wl[idx, 'doculect']],
                        Parameter_ID=concepts[wl[idx, 'concept']],
                        Source=[]
                        )

