import base64
from collections import namedtuple
import sys
from typing import Any, Dict
from django.conf import settings
from pathlib import Path
#from flask import Flask, request, jsonify

from cassis import *

import spacy
from spacy.tokens import Doc

# Types

JsonDict = Dict[str, Any]

PredictionRequest = namedtuple("PredictionRequest", ["layer", "feature", "projectId", "document", "typeSystem"])
PredictionResponse = namedtuple("PredictionResponse", ["document"])
Document = namedtuple("Document", ["xmi", "documentId", "userId"])

# Constants

SENTENCE_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
TOKEN_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
IS_PREDICTION = "inception_internal_predicted"



def inception_predict(request, project, pipeline):

    project = Project.objects.get(id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language)
    nlp = spacy.load(path, disable=['parser'])
    if request.method == "POST":

        json_data = request.get_json()

        prediction_request = parse_prediction_request(json_data)

        if pipeline == 'ner':
            prediction_response = predict_ner(prediction_request)
        if pipeline == 'pos':
            prediction_response = predict_pos(prediction_request)

        result = jsonify(document=prediction_response.document)

        return result

    
def inception_train(request, project, pipeline):
    return "#TODO Add train view"
