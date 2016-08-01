from flask import Flask, request, render_template
from flask_json import json_response
from flask_cors import CORS
from microservice_configs import *
from utils.utils import parse_request_params
from classification.content import labels
from classification.content.classifier_taxonomy import taxonomy
import file_paths
import os.path
import traceback


app = Flask(__name__)
app.config['JSON_ADD_STATUS'] = False
CORS(app)

print 'Initializing classifier...'
category2classifier = {}
for category in labels.labels:
    model_subdir = file_paths.model_subdir[category]
    classifier = taxonomy[category](model_subdir=model_subdir, default_return='Others')
    category2classifier[category] = classifier


print 'Finished initialization!'

@app.route("/")
def main():
    return render_template('index.html')


@app.route('/' + CONTENT_CLASSIFICATION_ROUTE, methods = ['POST'])
def classify_video_contents():
    #print request
    request_body = {}
    try:
        request_body = request.get_json()
        #print request_body

    except Exception, e:
        #traceback.print_exc()
        return json_response({'error' : 'Cannot parse the input json request.'})

    #print request_body

    category = parse_request_params(request_body, argument='category', default=None)
    allowed_categories = labels.labels.keys()
    if category not in allowed_categories:
        return json_response(error = 'Currently not supporting the specified category "%s".' % category, status_=500)

    data = parse_request_params(request_body, argument='data', default=[])

    try:
        classifier = category2classifier[category]
        result = classifier.predict(data)
        #print result
        return json_response(results = result, status_=200)
    except Exception, e:
        #traceback.print_exc()
        return json_response(error = 'Unable to make predictions.', status_=500)

