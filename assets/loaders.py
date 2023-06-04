# For Presidio
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# For console output
from pprint import pprint

# For extracting text
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

# For updating the PDF
from pikepdf import Pdf, AttachedFileSpec, Name, Dictionary, Array
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# For anonymization pipeline
import spacy_transformers
from faker import Faker


class Processor:
    def __init__(
        self,
        spanish_model,
        english_model,
        french_model,
    ):
        # Create configuration containing engine name and models
        self.configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "es", "model_name": f"{spanish_model}"},
                {"lang_code": "en", "model_name": f"{english_model}"},
                {"lang_code": "fr", "model_name": f"{french_model}"},
            ],
        }

        # Create configration for anonymizer
        fake = Faker(locale=["en_US", "en_GB", "en_CA", "fr_FR"])
        self.operators = {
            "PERSON": OperatorConfig("custom", {"lambda": lambda x: fake.name()}),
            "PHONE_NUMBER": OperatorConfig(
                "custom", {"lambda": lambda x: fake.phone_number()}
            ),
            "EMAIL_ADDRESS": OperatorConfig(
                "custom", {"lambda": lambda x: fake.email()}
            ),
            "LOCATION": OperatorConfig("replace", {"new_value": "USA"}),
            "DEFAULT": OperatorConfig(
                operator_name="mask",
                params={
                    "chars_to_mask": 10,
                    "masking_char": "*",
                    "from_end": False,
                },
            ),
        }

    def get_analyzer(self, supported_languages=["en", "es", "fr"]):
        provider = NlpEngineProvider(nlp_configuration=self.configuration)
        nlp_engine_multilingual = provider.create_engine()

        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine_multilingual,
            supported_languages=supported_languages,
        )

        return analyzer

    def get_anonymizer(self, supported_languages=["en", "es", "fr"]):
        anonymizer = AnonymizerEngine()
        return anonymizer

    # Combine the bounding boxes into a single bounding box.
    def combine_rect(self, rectA, rectB):
        a, b = rectA, rectB
        startX = min(a[0], b[0])
        startY = min(a[1], b[1])
        endX = max(a[2], b[2])
        endY = max(a[3], b[3])
        return (startX, startY, endX, endY)

    def redact_bounding_boxes(self, analyzed_bounding_boxes, path, output_path):
        pdf = Pdf.open(path)

        annotations_dict = {}

        # 'page_number': [1,2,3,4,5]

        # Create a highlight annotation for each bounding box.
        for analyzed_bounding_box in analyzed_bounding_boxes:
            boundingBox = analyzed_bounding_box["boundingBox"]

            # Create the annotation.
            # We could also create a redaction annotation if the ongoing workflows supports them.
            highlight = Dictionary(
                Type=Name.Annot,
                Subtype=Name.Highlight,
                QuadPoints=[
                    boundingBox[0],
                    boundingBox[3],
                    boundingBox[2],
                    boundingBox[3],
                    boundingBox[0],
                    boundingBox[1],
                    boundingBox[2],
                    boundingBox[1],
                ],
                Rect=[boundingBox[0], boundingBox[1], boundingBox[2], boundingBox[3]],
                C=[0, 0, 0],
                CA=1,
                T=analyzed_bounding_box["result"].entity_type,
            )

            page_number = analyzed_bounding_box["pageid"]

            if page_number in annotations_dict:
                annotations_dict[page_number].append(highlight)
            else:
                annotations_dict[page_number] = list(
                    highlight,
                )

        # Add the annotations to the PDF.
        for pageid in annotations_dict.keys():
            pdf.pages[pageid].Annots = pdf.make_indirect(annotations_dict[pageid])

        # And save.
        pdf.save(output_path)

    def process(self, path, output_path):
        analyzed_bounding_boxes = []
        # holds the anonymized texts as lists
        anonymized_texts = []
        anonymizer = self.get_anonymizer()
        analyzer = self.get_analyzer()

        for page_layout in extract_pages(path):
            analyzed_character_sets = []

            for text_container in page_layout:
                if isinstance(text_container, LTTextContainer):
                    # The element is a LTTextContainer, containing a paragraph of text.
                    text_to_anonymize = text_container.get_text()

                    # Analyze the text using the analyzer engine
                    analyzer_results = analyzer.analyze(
                        text=text_to_anonymize, language="en"
                    )

                    # Anonymize the analyzed text
                    anonymized_results = anonymizer.anonymize(
                        text=text_to_anonymize,
                        analyzer_results=analyzer_results,
                        operators=self.operators,
                    )
                    anonymized_texts.append(anonymized_results.text)

                    characters = list([])

                    # Grab the characters from the PDF
                    for text_line in filter(
                        lambda t: isinstance(t, LTTextLine), text_container
                    ):
                        for character in filter(
                            lambda t: isinstance(t, LTChar), text_line
                        ):
                            characters.append(character)

                    # Slice out the characters that match the analyzer results.
                    for result in analyzer_results:
                        start = result.start
                        end = result.end
                        analyzed_character_sets.append(
                            {"characters": characters[start:end], "result": result}
                        )

            # For each character set, combine the bounding boxes into a single bounding box.
            for analyzed_character_set in analyzed_character_sets:
                completeBoundingBox = analyzed_character_set["characters"][0].bbox

                for character in analyzed_character_set["characters"]:
                    completeBoundingBox = self.combine_rect(
                        completeBoundingBox, character.bbox
                    )

                analyzed_bounding_boxes.append(
                    {
                        "boundingBox": completeBoundingBox,
                        "result": analyzed_character_set["result"],
                        "pageid": page_layout.pageid - 1,
                    }
                )

        self.redact_bounding_boxes(analyzed_bounding_boxes, path, output_path)

        processor_results = {
            "anonymized_texts": anonymized_texts,
            "analyzed_bounding_boxes": analyzed_bounding_boxes,
        }

        return processor_results
