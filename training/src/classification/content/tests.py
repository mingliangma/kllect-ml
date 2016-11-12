import unittest
import src.paths as paths
import os.path
from pymongo import MongoClient
from technology_classifier import TechologyClassifier
import src.config as config
import json


# class ContentClassifierTests(unittest.TestCase):
#     def test_technology_classifier(self):
#         model_subdir = os.path.join(paths.MODElS_SUBDIR, TechologyClassifier.CONTENT_CATEGORY)
#         classifier = TechologyClassifier(model_subdir=model_subdir)
#
#         uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
#                                                                       config.password,
#                                                                       config.mongodb_host,
#                                                                       config.mongodb_port,
#                                                                       config.db)
#
#         client = MongoClient(uri)
#         col = client[config.db][config.result_col]
#
#         video = col.find_one()
#         print video

from sklearn.metrics import *
def test_technology_classifier():
    model_subdir = os.path.join(paths.MODElS_SUBDIR, TechologyClassifier.CONTENT_CATEGORY, '160728')
    classifier = TechologyClassifier(model_subdir=model_subdir, default_return='Others')

    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)

    client = MongoClient(uri)
    col = client[config.db][config.result_col]

    i = 0
    batch_data = []
    labels = []
    batch_size = 100
    predictions = []
    for video in col.find({'ml_label' : {'$exists' : True}}):
        labels.append(video['ml_label'])
        batch_data.append(video)

        if len(batch_data ) == batch_size:
            print 'Predicting for group #%d...' % (i // batch_size)

            predictions.extend(classifier.predict(batch_data))
            batch_data = []

        i += 1

    if len(batch_data):
        predictions.extend(classifier.predict(batch_data))

    correct = 0
    misses = 0
    for (i, label) in enumerate(labels):
        if len(set(label).intersection(set(predictions[i]))) > 0:
            correct += 1
        else:
            misses += 1

    print 'Correct: %d' % correct
    print 'Misses: %d' % misses
    print 'Accuracy: %.1f%%' % (correct * 100.0 / (misses + correct))


if __name__ == '__main__':
    #unittest.main()
    test_technology_classifier()

