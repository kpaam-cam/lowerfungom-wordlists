import pathlib
import collections

from clldutils.misc import slug
from pylexibank import FormSpec
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar
from pylexibank import Language

from lingpy import Wordlist

import attr

#Something in the code that reads languages expects a subgroup.
#This causes an error, so this attribute gets specified for the Language class
@attr.s
class CustomLanguage(Language):
    Variety = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    language_class = CustomLanguage # See note above for why this is here
    id = "LowerFungomIndividualWordlists v2.1"

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-", "ø", "øø", "ø / ø", "nan", "NULL", "0 / 0", "0"),  # characters that denote missing data. If missing singular, forces use of plural
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # This facilitates LingPy processing and is needed unless we can start properly annotating forms for grammatical info, etc.
        replacements=[(' ', '_'), ('\u0300m', 'm')],  # replacements with spaces
        normalize_unicode = 'NFD'
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        # This reads a sources.bib file if it exists
        args.writer.add_sources()
        
        # Add in doculects and languages
        languages = args.writer.add_languages(lookup_factory='Name')
		
        concepts = {}
        for concept in self.concepts:
            idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept['ENGLISH'],
                    )
            concepts[concept['ENGLISH']] = idx

        # Write forms
        wl = Wordlist(self.raw_dir.joinpath('AllWordlists-OneEntryPerRow-wNewLists-noDPJ.tsv').as_posix())
        for idx in progressbar(wl):
            #print(languages[wl[idx, 'doculect']])
            args.writer.add_forms_from_value(
                    Value=wl[idx, 'value'],
                    Language_ID=languages[wl[idx, 'doculect']],
                    Parameter_ID=concepts[wl[idx, 'concept']],
                    Source=['Tschonghongei:2022']
                    )


