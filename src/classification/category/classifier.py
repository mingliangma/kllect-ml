import os.path
import time
import traceback

import utils.serialize as serialize
import config
from pandas.io.json import json_normalize
from utils import text_cleaning
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

    def _load_vectorizer(self, binary_vectorizer_path, category):
        if not os.path.exists(binary_vectorizer_path):
            print 'ERROR: Unable to load binary vectorizer for category label "%s": ' % category + \
                  '"filename "%s" does not exist!' % binary_vectorizer_path
        else:
            try:
                return serialize.loadData(binary_vectorizer_path)
            except Exception, e:
                if self.debug:
                    traceback.print_exc()

                print 'ERROR: Unable to load binary vectorizer for category label "%s"!' % category

    def _load_vectorizers(self):
        print 'Loading vectorizers for each category label...'
        start_time = time.time()

        for category in self.categories:
            self.vectorizers[category] = {}

            for feature_field in [config.TITLE_FIELD, config.DESCRIPTION_FIELD, config.RAW_TAG_FIELD#, config.MAIN_TITLE_FIELD
                                  ]:
                self.vectorizers[category][feature_field] = self._load_vectorizer(os.path.join(self.model_dir,
                                                                                               '%s%s_%s%s' % (config.tf_idf_vectorizer_binary_file_prefix,
                                                                                                              feature_field,
                                                                                                              category,
                                                                                                              config.tf_idf_vectorizer_binary_file_extension)),
                                                                                  category)

            self.vectorizers[category][config.DICT_VECTORIZER_FIELD] = self._load_vectorizer(os.path.join(self.model_dir,
                                                                                                          '%s%s%s' % (config.dict_vectorizer_binary_file_prefix,
                                                                                                                      category,
                                                                                                                      config.tf_idf_vectorizer_binary_file_extension)),
                                                                                             category)

        end_time = time.time()
        print 'Finished loading vectorizers in %.1f seconds.\n' % (end_time - start_time)

    def _transform_field(self, data_df, tag, field):
        # print field, data_df[field]
        vectorizer = self.vectorizers[tag][field]

        return vectorizer.transform(data_df[field])

    def extract_meta_features(self, video):
        vec = {}

        # if video.get(config.PUBLISHER_FIELD):
        #     vec[config.PUBLISHER_FIELD] = video.get(config.PUBLISHER_FIELD).lower()

        # if video.get(config.DURATION_FIELD):
        #     vec[config.DURATION_FIELD] = video.get(config.DURATION_FIELD) // 60

        title = video.get(config.TITLE_FIELD)
        if title:
            title_words = title.split()
            # print 'title words:', title_words
            cc_num = len([x for x in title_words if x == text_cleaning.NUM_REPLACEMENT])
            total_words = len(title_words)
            vec['title_words'] = total_words
            vec['title_num_words'] = cc_num
            vec['title_num_word_ratio'] = float(cc_num) / total_words if total_words > 0 else 0.0

        description = video.get(config.DESCRIPTION_FIELD)
        if description:
            cc_num = 0
            total_words = 0
            for d_sent in description.split('\n'):
                # print 'description sent:', d_sent
                cc_num += len([x for x in d_sent if x == text_cleaning.NUM_REPLACEMENT])
                total_words += len(d_sent)

            vec['description_words'] = total_words
            vec['description_num_words'] = cc_num
            vec['description_num_word_ratio'] = float(cc_num) / total_words if total_words > 0 else 0.0

        raw_tags_str = video.get(config.RAW_TAG_FIELD)
        if raw_tags_str:
            raw_tags = raw_tags_str.split('\n')
            # print 'raw_tags:', raw_tags
            vec['raw_tags'] = len(raw_tags)
            num_word_tags = 0
            for tag in raw_tags:
                if text_cleaning.NUM_REPLACEMENT in tag.split():
                    num_word_tags += 1

            vec['num_word_raw_tags'] = num_word_tags
            vec['num_word_raw_tags_ratio'] = float(num_word_tags) / len(raw_tags) if len(raw_tags) > 0 else 0.0

        # print vec
        return vec

    def _transform_data(self, data):
        for d in data:
            # print d

            d[config.TITLE_FIELD] = text_cleaning.process_text(d.get(config.TITLE_FIELD))
            # print 'title:', d[config.TITLE_FIELD]

            # main_title = (d.get(config.TITLE_FIELD) or '').split('|')[0]
            # d[config.MAIN_TITLE_FIELD] = ' '.join(text_cleaning.process_text(main_title))

            d[config.DESCRIPTION_FIELD] = '\n'.join(text_cleaning.process_description(d.get(config.DESCRIPTION_FIELD)))

            # print 'description:', d[config.DESCRIPTION_FIELD]

            out_raw_tags = []
            # for tag in d.get(config.RAW_TAG_FIELD) or []:
            #     out_raw_tags.append(text_cleaning.process_text(tag))
            d[config.RAW_TAG_FIELD] = '\n'.join(out_raw_tags)
            #
            # print 'raw tags:', d[config.RAW_TAG_FIELD]
            # print

        return data

    def _predict_for_each_category(self, category, clean_data):
        data_df = json_normalize(clean_data)

        tfidf_title_X = self._transform_field(data_df, category, config.TITLE_FIELD)

        # tfidf_main_title_X = self._transform_field(data_df, category, config.MAIN_TITLE_FIELD)

        tfidf_description_X = self._transform_field(data_df, category, config.DESCRIPTION_FIELD)

        tfidf_raw_tag_X = self._transform_field(data_df, category, config.RAW_TAG_FIELD)

        other_data = []
        for d in clean_data:
            vec = self.extract_meta_features(d)

            other_data.append(vec)

        other_X = self.vectorizers[category][config.DICT_VECTORIZER_FIELD].transform(other_data)

        matrix = scipy.sparse.hstack(
            [tfidf_title_X, #tfidf_main_title_X,
             tfidf_description_X,
             tfidf_raw_tag_X,
             other_X]).tocsr()

        tag_classifier = self.classifiers[category]
        predicted_probs = tag_classifier.predict_proba(matrix)[:, 1]

        # predicted_probs = tag_classifier.predict(matrix)
        # print predicted_probs

        return predicted_probs

    def _predict_transformed_data(self, clean_data):
        # print data_df

        predictions = [[] for x in xrange(len(clean_data))]
        # prediction_probs = [[] for x in xrange(len(clean_data))]

        most_likely_predictions = [None] * len(clean_data)

        for category in self.categories:
            # for tag in ['Smartphones']:
            # print tag
            tag_predictions = self._predict_for_each_category(category, clean_data)
            for i, pred in enumerate(tag_predictions):
                # prediction_probs[i].append(pred)

                if pred >= self.prob_thresholds[category]:
                    predictions[i].append(category)

                if most_likely_predictions[i] is None or \
                    pred > most_likely_predictions[i][0]:
                    most_likely_predictions[i] = (pred, category)

        if self.return_most_likely_prediction or self.default_return:
            for i in xrange(len(clean_data)):
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
                self.predictions_field : prediction,
                # 'probs' : prediction_probs[i]
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
