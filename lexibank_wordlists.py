from pathlib import Path

import pylexibank
from clldutils.misc import slug


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "wordlists"

    # define the way in which forms should be handled
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,~",  # characters that split forms e.g. "a, b".
        missing_data=('?', '-'),  # characters that denote missing data.
        strip_inside_brackets=True   # do you want data removed in brackets or not?
    )

    def cmd_download(self, args):
        pass

    def cmd_makecldf(self, args):
        data = self.raw_dir.read_csv('Ajumbu.csv', dicts=True)
        doculects, concepts = set(), set()

        for row in data:
            doculect_id = 'Ajumbu_{}'.format(row['speaker_name'])
            if doculect_id not in doculects:
                args.writer.add_language(
                    ID=doculect_id, Glottocode='mbuu1238', Name='Ajumbu')
                doculects.add(doculect_id)
            concept_id = slug(row['concept'])
            if concept_id not in concepts:
                args.writer.add_concept(
                    ID=concept_id,
                    Name=row['concept'],
                )
                concepts.add(concept_id)
            lex = args.writer.add_forms_from_value(
                Language_ID=doculect_id,
                Parameter_ID=concept_id,
                Value=row['citation'],
                Source=[],
            )
