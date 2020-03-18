import base64
from collections import namedtuple
import sys
from typing import Any, Dict
from django.conf import settings
from pathlib import Path
#from flask import Flask, request, jsonify
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import json 

from cadet_app.models import Project
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


@csrf_exempt 
def inception_predict(request, project, pipeline):

    project = Project.objects.get(project_slug=project)
    language = project.spacy_language.slug.replace('-','_')
    path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/models/' + language)
    nlp = spacy.load(path, disable=['parser'])
    if request.method == "POST":

        json_data = json.loads(str(request.body, encoding='utf-8'))

        prediction_request = parse_prediction_request(json_data)

        if pipeline == 'ner':
            prediction_response = predict_ner(prediction_request, nlp)
        if pipeline == 'pos':
            prediction_response = predict_pos(prediction_request, nlp)

        result = JsonResponse({'document':prediction_response.document})

        return result
    else:
        return HttpResponse("this view talks to INCEpTION POST requests")
        

@csrf_exempt    
def inception_train(request, project, pipeline):
    return "#TODO Add train view"


def parse_prediction_request(json_object: JsonDict) -> PredictionRequest:
    metadata = json_object["metadata"]
    document = json_object["document"]

    layer = metadata["layer"]
    feature = metadata["feature"]
    projectId = metadata["projectId"]

    xmi = document["xmi"]
    documentId = document["documentId"]
    userId = document["userId"]
    typesystem = json_object["typeSystem"]

    return PredictionRequest(layer, feature, projectId, Document(xmi, documentId, userId), typesystem)



def predict_pos(prediction_request: PredictionRequest, nlp) -> PredictionResponse:
    # Load the CAS and type system from the request
    typesystem = load_typesystem(prediction_request.typeSystem)
    cas = load_cas_from_xmi(prediction_request.document.xmi, typesystem=typesystem)
    AnnotationType = typesystem.get_type(prediction_request.layer)

    # Extract the tokens from the CAS and create a spacy doc from it
    tokens = list(cas.select(TOKEN_TYPE))
    words = [cas.get_covered_text(token) for token in tokens]
    doc = Doc(nlp.vocab, words=words)

    # Do the tagging
    nlp.tagger(doc)

    # For every token, extract the POS tag and create an annotation in the CAS
    for token in doc:
        fields = {'begin': tokens[token.i].begin,
                  'end': tokens[token.i].end,
                  IS_PREDICTION: True,
                  prediction_request.feature: token.pos_}
        annotation = AnnotationType(**fields)
        cas.add_annotation(annotation)

    xmi = cas.to_xmi()
    return PredictionResponse(xmi)


def predict_ner(prediction_request: PredictionRequest, nlp) -> PredictionResponse:
    # Load the CAS and type system from the request
    typesystem = load_typesystem(prediction_request.typeSystem)
    cas = load_cas_from_xmi(prediction_request.document.xmi, typesystem=typesystem)
    AnnotationType = typesystem.get_type(prediction_request.layer)

    # Extract the tokens from the CAS and create a spacy doc from it
    tokens = list(cas.select(TOKEN_TYPE))
    words = [cas.get_covered_text(token) for token in tokens]
    doc = Doc(nlp.vocab, words=words)

    # Find the named entities
    nlp.entity(doc)

    # For every entity returned by spacy, create an annotation in the CAS
    for ent in doc.ents:
        fields = {'begin': tokens[ent.start].begin,
                  'end': tokens[ent.end - 1].end,
                  IS_PREDICTION: True,
                  prediction_request.feature: ent.label_}
        annotation = AnnotationType(**fields)
        cas.add_annotation(annotation)

    xmi = cas.to_xmi()
    return PredictionResponse(xmi)