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
    language_class = CustomLanguage
    id = "LowerFungomIndividualWordlists v2.1"

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-", "ø", "øø", "ø / ø", "ø /ø", "nan", "NULL", "0 / 0", "0"),  # characters that denote missing data. If missing singular, forces use of plural
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

        # Read forms
        wl = Wordlist(self.raw_dir.joinpath('AllWordlists-OneEntryPerRow-wNewLists-noDPJ.tsv').as_posix())

        # Keeping this code as an interesting example of how to do some filtering
        # of concepts for coverage. It didn't work for this data since the process through
        # which the raw dat is created contains NULL or nan entries for many forms and
        # these are not yet filtered and would get countered here.
        # Instead, filtering is now done at the analysis stage after the CLDF is created.
        #filledThreshold = 140 # This can be used to filter the forms before they go to CLDF to those with good coverage; for now, I'm trying to do that during analysis instead so the CLDF is richer. To activate replace None with an integer
        #mostFilled = sorted(
        #        wl.rows,
        #        key=lambda x: len(wl.get_list(row=x, flat=True)),
        #        reverse=True)[:filledThreshold]
        
        
        # Write concepts
        concepts = {}
        for concept in self.concepts:
            #if concept["ENGLISH"] in mostFilled: # We just do all now, see above comments on issue with this filtering strategy
                idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
                args.writer.add_concept(
                        ID=idx,
                        Name=concept['ENGLISH'],
                        )
                concepts[concept['ENGLISH']] = idx
        

        # Write concepts -- with mappings once these are available (adjust the score number?); for now using above simpler concept writer
        #concepts = {}
        #for concept in self.concepts:
        #   # if concept["ENGLISH"] in mostFilled: # We just do all now, see above comments on issue with this filtering strategy
        #        idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
        #        similarity = int(concept['SIMILARITY'] or 4)
        #        args.writer.add_concept(
        #                ID=idx,
        #                Name=concept['ENGLISH'],
        #                Concepticon_ID=concept['CONCEPTICON_ID'] if similarity <= 2 else None,
		#                Concepticon_Gloss=concept['CONCEPTICON_GLOSS'] if similarity <= 2 else None,
        #                )
        #        concepts[concept['ENGLISH']] = idx
               

        for idx in progressbar(wl):
           # if wl[idx, "concept"] in mostFilled: # We just do all now, see above comments on issue with this filtering strategy
                args.writer.add_forms_from_value(
                        Value=wl[idx, 'value'],
                        Language_ID=languages[wl[idx, 'doculect']],
                        Parameter_ID=concepts[wl[idx, 'concept']],
                        Source=["Tschonghongei:2022"]
                        )