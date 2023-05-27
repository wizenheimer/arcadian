from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

# For Presidio
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# For extracting text
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

# For updating the PDF
from pikepdf import Pdf, AttachedFileSpec, Name, Dictionary, Array

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

DEFAULT_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [
        {
            "lang_code": "en",
            "model_name": "en_core_web_lg",
        }
    ],
}


def identify(
    path,
    configuration=DEFAULT_CONFIG,
):
    """
    Identify PII in a given document
    """
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=[
            "en",
        ],
    )

    analyzed_character_sets = []

    for page_layout in extract_pages(path):
        for text_container in page_layout:
            if isinstance(text_container, LTTextContainer):
                # The element is a LTTextContainer, containing a paragraph of text.
                text_to_anonymize = text_container.get_text()

                # Analyze the text using the analyzer engine
                analyzer_results = analyzer.analyze(
                    text=text_to_anonymize, language="en"
                )

                # if text_to_anonymize.isspace() == False:
                #     print(text_to_anonymize)
                #     print(analyzer_results)

                characters = list([])

                # Grab the characters from the PDF
                for text_line in filter(
                    lambda t: isinstance(t, LTTextLine), text_container
                ):
                    for character in filter(lambda t: isinstance(t, LTChar), text_line):
                        characters.append(character)

                # Slice out the characters that match the analyzer results.
                for result in analyzer_results:
                    start = result.start
                    end = result.end
                    analyzed_character_sets.append(
                        {"characters": characters[start:end], "result": result}
                    )

    return analyzed_character_sets


# Combine the bounding boxes into a single bounding box.
def combine_rect(
    rectA,
    rectB,
):
    a, b = rectA, rectB
    startX = min(a[0], b[0])
    startY = min(a[1], b[1])
    endX = max(a[2], b[2])
    endY = max(a[3], b[3])
    return (startX, startY, endX, endY)


def redact_processor(
    analyzed_character_sets,
):
    analyzed_bounding_boxes = []

    # For each character set, combine the bounding boxes into a single bounding box.
    for analyzed_character_set in analyzed_character_sets:
        character_set = analyzed_character_set["characters"]

        if len(character_set) > 0:
            completeBoundingBox = character_set[0].bbox

            for character in character_set:
                if character.bbox:
                    completeBoundingBox = combine_rect(
                        completeBoundingBox, character.bbox
                    )

            analyzed_bounding_boxes.append(
                {
                    "boundingBox": completeBoundingBox,
                    "result": analyzed_character_set["result"],
                }
            )


def redact(
    path,
    analyzed_bounding_boxes,
    output_path,
):
    pdf = Pdf.open(path)

    annotations = []

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

        annotations.append(highlight)

    # Add the annotations to the PDF.
    pdf.pages[0].Annots = pdf.make_indirect(annotations)

    # And save.
    pdf.save(output_path)
