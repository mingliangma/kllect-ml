from flask import Flask, request, render_template
from flask_cors import CORS
from flask_json import json_response

import file_paths
from classification.content.labels import labels as content_tags
from classification.content.classifier_taxonomy import taxonomy
from classification.category.classifier import CategoryClassifier
from microservice_configs import *
from utils.utils import parse_request_params
import template as t
from copy import deepcopy
import collections


app = Flask(__name__)
app.config['JSON_ADD_STATUS'] = False
CORS(app)

print 'Initializing classifier...'
topic_classifier = CategoryClassifier(model_subdir=file_paths.topic_models_subdir,
                                      default_return=t.DEFAULT_PREDICTION,
                                      id_field=t.ID_FIELD,
                                      predictions_field=t.CATEGORY_PREDICTIONS_FIELD)

category2classifier = {}
for category in content_tags:
    model_subdir = file_paths.model_subdir[category]
    classifier = taxonomy[category](model_subdir=model_subdir,
                                    default_return=t.DEFAULT_PREDICTION,
                                    id_field=t.ID_FIELD,
                                    predictions_field=t.CONTENT_TAG_PREDICTIONS_FIELD)
    category2classifier[category] = classifier

print 'Finished initialization!'


@app.route("/")
def main():
    return render_template('index.html')


@app.route('/' + CATEGORY_CLASSIFICATION_ROUTE, methods = ['POST'])
def classify_video_categories():
    try:
        request_body = request.get_json()
        # print request_body

    except Exception, e:
        # traceback.print_exc()
        return json_response({'error': 'Cannot parse the input json request.'})

    # print request_body

    data = parse_request_params(request_body, argument=t.INPUT_DATA_FIELD, default=[])

    try:
        result = topic_classifier.predict(data)
        # print result
        return json_response(results=result, status_=200)
    except Exception, e:
        # traceback.print_exc()
        return json_response(error='Unable to make predictions.', status_=500)


@app.route('/' + CONTENT_CLASSIFICATION_ROUTE, methods = ['POST'])
def classify_video_contents():
    print request
    request_body = {}
    try:
        request_body = request.get_json()
        print request_body

    except Exception, e:
        #traceback.print_exc()
        return json_response({'error' : 'Cannot parse the input json request.'})

    print request_body

    category = parse_request_params(request_body, argument=t.INPUT_CATEGORY_FIELD, default=None)
    allowed_categories = content_tags.keys()
    if category not in allowed_categories:
        return json_response(error = 'Currently not supporting the specified category "%s".' % category, status_=500)

    data = parse_request_params(request_body, argument=t.INPUT_DATA_FIELD, default=[])

    try:
        classifier = category2classifier[category]
        result = classifier.predict(data)
        #print result
        return json_response(results = result, status_=200)
    except Exception, e:
        #traceback.print_exc()
        return json_response(error = 'Unable to make predictions.', status_=500)


@app.route('/' + FULL_CLASSIFICATION_ROUTE, methods = ['POST'])
def classify_video_categories_and_contents():
    print request
    request_body = {}
    try:
        request_body = request.get_json()
        print request_body

    except Exception, e:
        #traceback.print_exc()
        return json_response({'error' : 'Cannot parse the input json request.'})

    print request_body

    allowed_categories = content_tags.keys()

    data = parse_request_params(request_body, argument='data', default=[])
    id2data = {d[t.ID_FIELD] : deepcopy(d) for d in data}

    try:
        # First-level category classification
        topic_results = topic_classifier.predict(data)

        id2topic = collections.defaultdict(list)
        category2input_data = collections.defaultdict(list)

        for prediction in topic_results:
            d_id = prediction[t.ID_FIELD]
            category_predictions = prediction[t.CATEGORY_PREDICTIONS_FIELD]

            id2topic[d_id] = category_predictions

            for category in category_predictions:
                if category != t.DEFAULT_PREDICTION and category in allowed_categories:
                    d_copy = deepcopy(id2data[d_id])
                    d_copy[t.INPUT_CATEGORY_FIELD] = category
                    category2input_data[category].append(d_copy)

        # Second-level tag classification
        # Note that a video might have multiple predicted category in the first pass
        id2tags = {}
        for category in category2input_data:
            classifier = category2classifier[category]
            category_input_data = category2input_data[category]

            tag_results = classifier.predict(category_input_data)

            for prediction in tag_results:
                d_id = prediction[t.ID_FIELD]
                if d_id not in id2tags:
                    id2tags[d_id] = collections.defaultdict(list)

                tag_prediction = prediction[t.CONTENT_TAG_PREDICTIONS_FIELD]

                id2tags[d_id][category] = tag_prediction

        # Organize output results
        result = []
        for (i, d) in enumerate(data):
            d_id = d[t.ID_FIELD]

            category_predictions = id2topic[d_id]

            r = {
                t.ID_FIELD: d_id,
                t.SINGLE_CATEGORY_FIELD: None,
                t.CONTENT_TAG_PREDICTIONS_FIELD: []
            }

            if len(category_predictions):
                category = category_predictions[0]

                if d_id in id2tags:
                    category2tags = id2tags[d_id]
                    tags = category2tags[category]
                else:
                    tags = []

                r[t.SINGLE_CATEGORY_FIELD] = category
                r[t.CONTENT_TAG_PREDICTIONS_FIELD] = tags

            result.append(r)

            # pred = {category : [] for category in category_predictions}
            #
            # if d_id in id2tags:
            #     category2tags = id2tags[d_id]
            #
            #     for category in category2tags:
            #         pred[category] = category2tags[category]
            #
            #
            #
            # result.append({
            #     t.ID_FIELD : d_id,
            #     t.FULL_PREDICTIONS_FIELD : [{t.SINGLE_CATEGORY_FIELD : x,
            #                                  t.CONTENT_TAG_PREDICTIONS_FIELD : pred[x]}
            #                                 for x in pred]
            # })

        return json_response(results = result, status_=200)
    except Exception, e:
        # import traceback
        # traceback.print_exc()
        return json_response(error = 'Unable to make predictions.', status_=500)
