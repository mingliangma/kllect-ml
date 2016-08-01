import os.path
import time
import traceback

import utils.serialize as serialize
import config
from pandas.io.json import json_normalize


class BaseClassifier(object):
    def __init__(self, content_category,
                 content_tags,
                 feature_fields,
                 model_dir,
                 prob_thresholds = None,
                 debug = False,
                 return_most_likely_prediction = False,
                 default_return = None):
        self.content_category = content_category
        self.content_tags = content_tags
        self.feature_fields = feature_fields
        self.model_dir = model_dir
        self.classifiers = {}
        self.vectorizers = {}
        self.id_field = 'id'
        self.predictions_field = 'predictions'

        self.prob_thresholds = {tag : 0.50 for tag in self.content_tags}
        if prob_thresholds:
            for tag in prob_thresholds:
                if tag in self.content_tags:
                    self.prob_thresholds[tag] = prob_thresholds[tag]

        self.debug = debug
        self.return_most_likely_prediction = return_most_likely_prediction
        self.default_return = default_return

        start_time = time.time()

        print 'Initializing classification component for category "%s"...' % self.content_category
        print 'Total tags for this category: %d\n' % len(self.content_tags)

        self._load_classifiers()
        self._load_vectorizers()

        print 'Finished initialization in %.1f seconds.' % (time.time() - start_time)

    def _load_classifiers(self):
        print 'Loading classifiers for each tag...'
        start_time = time.time()

        for tag in self.content_tags:
            binary_classifier_path = os.path.join(self.model_dir,
                                                  '%s%s%s' % (config.classifier_binary_file_prefix,
                                                              tag,
                                                              config.classifier_binary_file_extension))
            if not os.path.exists(binary_classifier_path):
                print 'ERROR: Unable to load binary classifier for tag "%s": ' % tag + \
                    'filename "%s" does not exist!' % binary_classifier_path
            else:
                try:
                    self.classifiers[tag] = serialize.loadData(binary_classifier_path)
                except Exception, e:
                    if self.debug:
                        traceback.print_exc()

                    print 'ERROR: Unable to load binary classifier for tag "%s"!' % tag

        end_time = time.time()
        print 'Finished loading classifiers in %.1f seconds.\n' % (end_time - start_time)

    def _load_vectorizers(self):
        print 'Loading vectorizers for each tag...'
        start_time = time.time()

        for tag in self.content_tags:
            self.vectorizers[tag] = {}

            for feature_field in self.feature_fields:
                binary_vectorizer_path = os.path.join(self.model_dir,
                                                      '%s%s_%s%s' % (config.vectorizer_binary_file_prefix,
                                                                     feature_field,
                                                                     tag,
                                                                     config.vectorizer_binary_file_extension))

                if not os.path.exists(binary_vectorizer_path):
                    print 'ERROR: Unable to load binary "%s" vectorizer for tag "%s": ' % (feature_field, tag) + \
                          '"filename "%s" does not exist!' % binary_vectorizer_path
                else:
                    try:
                        self.vectorizers[tag][feature_field] = serialize.loadData(binary_vectorizer_path)
                    except Exception, e:
                        if self.debug:
                            traceback.print_exc()

                        print 'ERROR: Unable to load binary "%s" vectorizer for tag "%s"!' % (feature_field, tag)

        end_time = time.time()
        print 'Finished loading vectorizers in %.1f seconds.\n' % (end_time - start_time)

    def _transform_data(self, data):
        raise NotImplementedError()

    def _predict_for_each_tag(self, tag, data_df):
        raise NotImplementedError()

    def _predict_transformed_data(self, clean_data):
        data_df = json_normalize(clean_data)
        # print data_df

        predictions = [[] for x in xrange(data_df.shape[0])]
        most_likely_predictions = [None] * data_df.shape[0]

        for tag in self.content_tags:
            # for tag in ['Smartphones']:
            # print tag
            tag_predictions = self._predict_for_each_tag(tag, data_df)
            #print tag, tag_predictions
            for i, pred in enumerate(tag_predictions):
                if pred >= self.prob_thresholds[tag]:
                    predictions[i].append(tag)

                if most_likely_predictions[i] is None or \
                    pred > most_likely_predictions[i][0]:
                    most_likely_predictions[i] = (pred, tag)

        if self.return_most_likely_prediction or self.default_return:
            for i in xrange(data_df.shape[0]):
                if not predictions[i]:
                    # Backfill empty predictions to the most likely predictions
                    if self.return_most_likely_prediction and most_likely_predictions[i]:
                        predictions[i].append(most_likely_predictions[i][1])

                    # Backfill to the default return value
                    elif self.default_return:
                        predictions[i].append(self.default_return)
                #print i, predictions[i], most_likely_predictions[i]

        results = []
        for (i, prediction) in enumerate(predictions):
            results.append({
                self.id_field : clean_data[i][self.id_field],
                self.predictions_field : prediction
            })
        # for i, data_tags in enumerate(predictions):
        #     print i, data_tags

        return results

    def predict(self, data):
        # Assume data is a list of dictionary
        clean_data = []
        for d in data:
            if isinstance(d, dict) and self.id_field in d:
                clean_data.append(d)

        #print clean_data
        transformed_data = self._transform_data(clean_data)

        return self._predict_transformed_data(transformed_data)
