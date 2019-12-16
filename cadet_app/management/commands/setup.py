from django.core.management.base import BaseCommand, CommandError
from cadet_app.models import *
from cadet_app.utils import update_spacy_langs


class Command(BaseCommand):
    help = 'Setup script for fresh project. Adds spaCy languages and annotation types to the database'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        update_spacy_langs()

        a_types = ['token','span','sent']
        [AnnotationType(name=a_type).save() for a_type in a_types]

        # TODO create setup for label groups
          # TEI
          # UD
          

        self.stdout.write(self.style.SUCCESS('Done!'))
