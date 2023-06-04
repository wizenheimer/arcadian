import spacy
from django.core.management.base import BaseCommand

# Models tuned for accuracy
SPANISH_MODEL_AC = "es_dep_news_trf"
ENGLISH_MODEL_AC = "en_core_web_trf"
FRENCH_MODEL_AC = "fr_dep_news_trf"

# Models tuned for efficiency
SPANISH_MODEL_EF = "es_core_news_md"
ENGLISH_MODEL_EF = "en_core_web_sm"
FRENCH_MODEL_EF = "fr_core_news_sm"


class Command(BaseCommand):
    help = "Loads the spacy models"

    def add_arguments(self, parser):
        parser.add_argument(
            "mode",
            type=str,
            help="Indicates the mode of inference",
        )

    def handle(self, *args, **kwargs):
        mode = kwargs["mode"]
        if mode == "accuracy":
            spacy.cli.download(SPANISH_MODEL_AC)
            spacy.cli.download(ENGLISH_MODEL_AC)
            spacy.cli.download(FRENCH_MODEL_AC)
        elif mode == "efficiency":
            spacy.cli.download(SPANISH_MODEL_EF)
            spacy.cli.download(ENGLISH_MODEL_EF)
            spacy.cli.download(FRENCH_MODEL_EF)
