from django.core.management.base import BaseCommand, CommandError
from cadet_app.models import *
from cadet_app.utils import update_spacy_langs
import spacy
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = "Setup script for fresh project. Adds spaCy languages and annotation types to the database"

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        update_spacy_langs()

        a_types = ["token", "span", "sent"]
        [AnnotationType.objects.update_or_create(name=a_type) for a_type in a_types]

        # TODO create setup for label groups
        TEI = LabelSet.objects.update_or_create(title='TEI P5')
        # UD
        UD, create = LabelSet.objects.update_or_create(title='Universal Dependencies V2')
        UD.groups.update_or_create(title='FORM', explain="Word form or punctuation symbol.")
        UD.groups.update_or_create(title='UPOS', explain="Universal part-of-speech tag.")
        UD.groups.update_or_create(title='XPOS', explain="Language-specific part-of-speech tag; underscore if not available.")
        UD.groups.update_or_create(title='FEATS', explain="List of morphological features from the universal feature inventory or from a defined language-specific extension; underscore if not available.")
        UD.groups.update_or_create(title='HEAD', explain="Head of the current word, which is either a value of ID or zero (0).")
        UD.groups.update_or_create(title='DEPREL', explain="Universal dependency relation to the HEAD (root iff HEAD = 0) or a defined language-specific subtype of one.")
        UD.groups.update_or_create(title='DEPS', explain="Enhanced dependency graph in the form of a list of head-deprel pairs.")
        UD.groups.update_or_create(title='MISC', explain="Any other annotation.")
                
        UPOS = UD.groups.get(title='UPOS') 
        UPOS.labels.update_or_create(name='ADJ', human_name='adjective', explain_link='https://universaldependencies.org/u/pos/all.html#adj-adjective')
        UPOS.labels.update_or_create(name='ADP', human_name='adposition', explain_link='https://universaldependencies.org/u/pos/all.html#adp-adposition')
        UPOS.labels.update_or_create(name='ADV', human_name='adverb', explain_link='https://universaldependencies.org/u/pos/all.html#adv-adverb')
        UPOS.labels.update_or_create(name='AUX', human_name='auxiliary', explain_link='https://universaldependencies.org/u/pos/all.html#aux-auxiliary')
        UPOS.labels.update_or_create(name='CCONJ', human_name='coordinating conjunction', explain_link='https://universaldependencies.org/u/pos/all.html#cconj-coordinating-conjunction')
        UPOS.labels.update_or_create(name='DET', human_name='determiner', explain_link='https://universaldependencies.org/u/pos/all.html#det-determiner')
        UPOS.labels.update_or_create(name='INTJ', human_name='interjection', explain_link='https://universaldependencies.org/u/pos/all.html#intj-interjection')
        UPOS.labels.update_or_create(name='NOUN', human_name='noun', explain_link='https://universaldependencies.org/u/pos/all.html#noun-noun')
        UPOS.labels.update_or_create(name='NUM', human_name='numeral', explain_link='https://universaldependencies.org/u/pos/all.html#num-numeral')
        UPOS.labels.update_or_create(name='PART', human_name='particle', explain_link='https://universaldependencies.org/u/pos/all.html#part-particle')
        UPOS.labels.update_or_create(name='PRON', human_name='pronoun', explain_link='https://universaldependencies.org/u/pos/all.html#pron-pronoun')
        UPOS.labels.update_or_create(name='PROPN', human_name='proper noun', explain_link='https://universaldependencies.org/u/pos/all.html#propn-proper-noun')
        UPOS.labels.update_or_create(name='PUNCT', human_name='PUNCT: punctuation', explain_link='https://universaldependencies.org/u/pos/all.html#punct-punctuation')
        UPOS.labels.update_or_create(name='SCONJ', human_name='subordinating conjunction', explain_link='https://universaldependencies.org/u/pos/all.html#sconj-subordinating-conjunction')
        UPOS.labels.update_or_create(name='SYM', human_name='symbol', explain_link='https://universaldependencies.org/u/pos/all.html#sym-symbol')
        UPOS.labels.update_or_create(name='VERB', human_name='verb', explain_link='https://universaldependencies.org/u/pos/all.html#verb-verb')
        UPOS.labels.update_or_create(name='X', human_name='other', explain_link='https://universaldependencies.org/u/pos/all.html#adj-adjective')
        
        FEATS = UD.groups.get(title='FEATS') 
        FEATS.labels.update_or_create(name='Abbr', human_name='abbreviation', explain_link='https://universaldependencies.org/u/feat/Abbr.html')
        FEATS.labels.update_or_create(name='AbsErgDatNumber', human_name='number agreement with absolutive/ergative/dative argument', explain_link='https://universaldependencies.org/u/feat/AbsErgDatNumber.html')
        FEATS.labels.update_or_create(name='AbsErgDatPerson', human_name='person agreement with absolutive/ergative/dative argument', explain_link='https://universaldependencies.org/u/feat/AbsErgDatPerson.html')
        FEATS.labels.update_or_create(name='AbsErgDatPolite', human_name='politeness agreement with absolutive/ergative/dative argument', explain_link='https://universaldependencies.org/u/feat/AbsErgDatPolite.html')
        FEATS.labels.update_or_create(name='AdpType', human_name='adposition type', explain_link='https://universaldependencies.org/u/feat/AdpType.html')
        FEATS.labels.update_or_create(name='AdvType', human_name='adverb type', explain_link='https://universaldependencies.org/u/feat/AdvType.html')
        FEATS.labels.update_or_create(name='Animacy', human_name='animacy', explain_link='https://universaldependencies.org/u/feat/Animacy.html')
        FEATS.labels.update_or_create(name='Aspect', human_name='aspect', explain_link='https://universaldependencies.org/u/feat/Aspect.html')
        FEATS.labels.update_or_create(name='Case', human_name='case', explain_link='https://universaldependencies.org/u/feat/Case.html')
        FEATS.labels.update_or_create(name='Clusivity', human_name='clusivity', explain_link='https://universaldependencies.org/u/feat/Clusivity.html')
        FEATS.labels.update_or_create(name='ConjType', human_name='conjunction type', explain_link='https://universaldependencies.org/u/feat/ConjType.html')
        FEATS.labels.update_or_create(name='Definite', human_name='definiteness or state', explain_link='https://universaldependencies.org/u/feat/Definite.html')
        FEATS.labels.update_or_create(name='Degree', human_name='degree of comparison', explain_link='https://universaldependencies.org/u/feat/Degree.html')
        FEATS.labels.update_or_create(name='Echo', human_name='is this an echo word or a reduplicative?', explain_link='https://universaldependencies.org/u/feat/Echo.html')
        FEATS.labels.update_or_create(name='ErgDatGender', human_name='gender agreement with ergative/dative argument', explain_link='https://universaldependencies.org/u/feat/ErgDatGender.html')
        FEATS.labels.update_or_create(name='Evident', human_name='evidentiality', explain_link='https://universaldependencies.org/u/feat/Evident.html')
        FEATS.labels.update_or_create(name='Foreign', human_name='is this a foreign word?', explain_link='https://universaldependencies.org/u/feat/Foreign.html')
        FEATS.labels.update_or_create(name='Gender', human_name='gender', explain_link='https://universaldependencies.org/u/feat/Gender.html')
        FEATS.labels.update_or_create(name='Hyph', human_name='hyphenated compound or part of it', explain_link='https://universaldependencies.org/u/feat/Hyph.html')
        FEATS.labels.update_or_create(name='Mood', human_name='mood', explain_link='https://universaldependencies.org/u/feat/Mood.html')
        FEATS.labels.update_or_create(name='NameType', human_name='type of named entity', explain_link='https://universaldependencies.org/u/feat/NameType.html')
        FEATS.labels.update_or_create(name='NounClass', human_name='noun class', explain_link='https://universaldependencies.org/u/feat/NounClass.html')
        FEATS.labels.update_or_create(name='NounType', human_name='noun type', explain_link='https://universaldependencies.org/u/feat/NounType.html')
        FEATS.labels.update_or_create(name='NumForm', human_name='numeral form', explain_link='https://universaldependencies.org/u/feat/Number.html')
        FEATS.labels.update_or_create(name='NumType', human_name='numeral type', explain_link='https://universaldependencies.org/u/feat/NumForm.html')
        FEATS.labels.update_or_create(name='NumValue', human_name='numeric value', explain_link='https://universaldependencies.org/u/feat/NumType.html')
        FEATS.labels.update_or_create(name='Number', human_name='number', explain_link='https://universaldependencies.org/u/feat/NumValue.html')
        FEATS.labels.update_or_create(name='PartType', human_name='particle type', explain_link='https://universaldependencies.org/u/feat/PartType.html')
        FEATS.labels.update_or_create(name='Person', human_name='person', explain_link='https://universaldependencies.org/u/feat/Person.html')
        FEATS.labels.update_or_create(name='Polarity', human_name='polarity', explain_link='https://universaldependencies.org/u/feat/Polarity.html')
        FEATS.labels.update_or_create(name='Polite', human_name='politeness', explain_link='https://universaldependencies.org/u/feat/Polite.html')
        FEATS.labels.update_or_create(name='Poss', human_name='possessive', explain_link='https://universaldependencies.org/u/feat/Poss.html')
        FEATS.labels.update_or_create(name='PossGender', human_name='possessor’s gender', explain_link='https://universaldependencies.org/u/feat/PossedNumber.html')
        FEATS.labels.update_or_create(name='PossNumber', human_name='possessor’s number', explain_link='https://universaldependencies.org/u/feat/PossGender.html')
        FEATS.labels.update_or_create(name='PossPerson', human_name='possessor’s person', explain_link='https://universaldependencies.org/u/feat/PossNumber.html')
        FEATS.labels.update_or_create(name='PossedNumber', human_name='possessed object’s number', explain_link='https://universaldependencies.org/u/feat/PossPerson.html')
        FEATS.labels.update_or_create(name='Prefix', human_name='Word functions as a prefix in a compund construction', explain_link='https://universaldependencies.org/u/feat/Prefix.html')
        FEATS.labels.update_or_create(name='PrepCase', human_name='case form sensitive to prepositions', explain_link='https://universaldependencies.org/u/feat/PrepCase.html')
        FEATS.labels.update_or_create(name='PronType', human_name='pronominal type', explain_link='https://universaldependencies.org/u/feat/PronType.html')
        FEATS.labels.update_or_create(name='PunctSide', human_name='which side of paired punctuation is this?', explain_link='https://universaldependencies.org/u/feat/PunctSide.html')
        FEATS.labels.update_or_create(name='PunctType', human_name='punctuation type', explain_link='https://universaldependencies.org/u/feat/PunctType.html')
        FEATS.labels.update_or_create(name='Reflex', human_name='reflexive', explain_link='https://universaldependencies.org/u/feat/Reflex.html')
        FEATS.labels.update_or_create(name='Style', human_name='style or sublanguage to which this word form belongs', explain_link='https://universaldependencies.org/u/feat/Style.html')
        FEATS.labels.update_or_create(name='Subcat', human_name='subcategorization', explain_link='https://universaldependencies.org/u/feat/Subcat.html')
        FEATS.labels.update_or_create(name='Tense', human_name='tense', explain_link='https://universaldependencies.org/u/feat/Tense.html')
        FEATS.labels.update_or_create(name='Typo', human_name='is this a misspelled word?', explain_link='https://universaldependencies.org/u/feat/Typo.html')
        FEATS.labels.update_or_create(name='VerbForm', human_name='form of verb or deverbative', explain_link='https://universaldependencies.org/u/feat/VerbForm.html')
        FEATS.labels.update_or_create(name='VerbType', human_name='verb type', explain_link='https://universaldependencies.org/u/feat/VerbType.html')
        FEATS.labels.update_or_create(name='Voice', human_name='voice', explain_link='https://universaldependencies.org/u/feat/Voice.html')



        # Clone custom_languages 
        custom_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY)
        if not custom_path.exists():
            from git import Repo
            git_url = "https://github.com/standoff-nlp/custom_languages.git"
            Repo.clone_from(git_url, custom_path)

        # Clone spaCy models 
        models_path = custom_path / 'core_models'
        if not models_path.exists():
            from git import Repo
            git_url = "https://github.com/explosion/spacy-models.git"
            Repo.clone_from(git_url, models_path)

        # change permissions on custom_languages to www-data
        spacy_path = Path(spacy.__file__.replace('__init__.py',''))
        print('[*] remember to run $ sudo chown -R www-data:www-data {}'.format(spacy_path))
        print('[*] also run $ sudo chown -R www-data:www-data {}'.format(custom_path))
        print('[*] also run $ sudo chown -R www-data:www-data {}'.format(models_path))
        
        self.stdout.write(self.style.SUCCESS("Done!"))
