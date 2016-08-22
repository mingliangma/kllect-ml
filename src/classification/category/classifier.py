import os.path
import time
import traceback

import utils.serialize as serialize
import config
from pandas.io.json import json_normalize
from utils.text_cleaning import stemming
import scipy
import labels


class CategoryClassifier(object):
    def __init__(self, model_subdir,
                 prob_thresholds = None,
                 debug = False,
                 return_most_likely_prediction = False,
                 default_return = None,
                 id_field = 'id',
                 predictions_field = 'categories'):
        self.categories = labels.labels
        self.model_dir = model_subdir
        self.feature_fields = config.FEATURE_FIELDS
        self.classifiers = {}
        self.vectorizers = {}
        self.id_field = id_field
        self.predictions_field = predictions_field

        self.prob_thresholds = {tag : 0.50 for tag in self.categories}
        if prob_thresholds:
            for category in prob_thresholds:
                if category in self.categories:
                    self.prob_thresholds[category] = prob_thresholds[category]

        self.debug = debug
        self.return_most_likely_prediction = return_most_likely_prediction
        self.default_return = default_return

        start_time = time.time()

        print 'Initializing classification component...'
        print 'Total category labels: %d\n' % len(self.categories)

        self._load_classifiers()
        self._load_vectorizers()

        print 'Finished initialization in %.1f seconds.' % (time.time() - start_time)

    def _load_classifiers(self):
        print 'Loading classifiers for each category label...'
        start_time = time.time()

        for category in self.categories:
            binary_classifier_path = os.path.join(self.model_dir,
                                                  '%s%s%s' % (config.classifier_binary_file_prefix,
                                                              category,
                                                              config.classifier_binary_file_extension))
            if not os.path.exists(binary_classifier_path):
                print 'ERROR: Unable to load binary classifier for category label "%s": ' % category + \
                    'filename "%s" does not exist!' % binary_classifier_path
            else:
                try:
                    self.classifiers[category] = serialize.loadData(binary_classifier_path)
                except Exception, e:
                    if self.debug:
                        traceback.print_exc()

                    print 'ERROR: Unable to load binary classifier for category label "%s"!' % category

        end_time = time.time()
        print 'Finished loading classifiers in %.1f seconds.\n' % (end_time - start_time)

    def _load_vectorizers(self):
        print 'Loading vectorizers for each category label...'
        start_time = time.time()

        for category in self.categories:
            self.vectorizers[category] = {}

            for feature_field in self.feature_fields:
                binary_vectorizer_path = os.path.join(self.model_dir,
                                                      '%s%s_%s%s' % (config.vectorizer_binary_file_prefix,
                                                                     feature_field,
                                                                     category,
                                                                     config.vectorizer_binary_file_extension))

                if not os.path.exists(binary_vectorizer_path):
                    print 'ERROR: Unable to load binary "%s" vectorizer for category label "%s": ' % (feature_field, category) + \
                          '"filename "%s" does not exist!' % binary_vectorizer_path
                else:
                    try:
                        self.vectorizers[category][feature_field] = serialize.loadData(binary_vectorizer_path)
                    except Exception, e:
                        if self.debug:
                            traceback.print_exc()

                        print 'ERROR: Unable to load binary "%s" vectorizer for category label "%s"!' % (feature_field, category)

        end_time = time.time()
        print 'Finished loading vectorizers in %.1f seconds.\n' % (end_time - start_time)

    def _transform_field(self, data_df, tag, field):
        vectorizer = self.vectorizers[tag][field]

        data_df_col = [' '.join(x) for x in data_df[field]]

        return vectorizer.transform(data_df_col)

    def _transform_data(self, data):
        for d in data:
            # print d

            for field in self.feature_fields:
                raw_field_data = d[field] if field in d else None

                if raw_field_data:
                    if field == config.RAW_TAG_FIELD:
                        d[field] = stemming(' '.join(raw_field_data))
                    else:
                        # print field, raw_field_data
                        d[field] = stemming(raw_field_data)
                else:
                    d[field] = []

        return data

    def _predict_for_each_category(self, category, data_df):
        tfidf_title = self._transform_field(data_df, category, config.TITLE_FIELD)

        tfidf_description = self._transform_field(data_df, category, config.DESCRIPTION_FIELD)

        tfidf_raw_tag = self._transform_field(data_df, category, config.RAW_TAG_FIELD)

        w1 = 1
        w2 = 1
        w4 = 1

        matrix = scipy.sparse.hstack(
            [w1 * tfidf_title, w2 * tfidf_description,
             w4 * tfidf_raw_tag]).tocsr()

        tag_classifier = self.classifiers[category]
        predicted_probs = tag_classifier.predict_proba(matrix)[:, 1]

        return predicted_probs

    def _predict_transformed_data(self, clean_data):
        data_df = json_normalize(clean_data)
        # print data_df

        predictions = [[] for x in xrange(data_df.shape[0])]
        most_likely_predictions = [None] * data_df.shape[0]

        for category in self.categories:
            # for tag in ['Smartphones']:
            # print tag
            tag_predictions = self._predict_for_each_category(category, data_df)
            #print tag, tag_predictions
            for i, pred in enumerate(tag_predictions):
                if pred >= self.prob_thresholds[category]:
                    predictions[i].append(category)

                if most_likely_predictions[i] is None or \
                    pred > most_likely_predictions[i][0]:
                    most_likely_predictions[i] = (pred, category)

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
        # for data in transformed_data:
        #     print data

        return self._predict_transformed_data(transformed_data)
