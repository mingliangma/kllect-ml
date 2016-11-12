from base_classifier import BaseClassifier
from labels import labels
import numpy as np
import scipy

from sklearn.preprocessing import normalize
from src.utils.text_cleaning import stemming
import traceback


class TechologyClassifier(BaseClassifier):
    CONTENT_CATEGORY = 'Technology'
    CONTENT_TAGS = labels[CONTENT_CATEGORY].keys()
    PROB_THRESHOLDS = labels[CONTENT_CATEGORY]

    TITLE_FIELD = 'title'
    DESCRIPTION_FIELD = 'description'
    EXTRACTION_METHOD_FIELD = 'extraction_method'
    RAW_TAG_FIELD = 'raw_tags'

    FEATURE_FIELDS = [
        TITLE_FIELD,
        DESCRIPTION_FIELD,
        EXTRACTION_METHOD_FIELD,
        RAW_TAG_FIELD
    ]

    def __init__(self, model_subdir,
                 prob_thresholds = None,
                 debug = False,
                 return_most_likely_prediction = False,
                 default_return = None):
        BaseClassifier.__init__(self,
                                content_category=TechologyClassifier.CONTENT_CATEGORY,
                                content_tags=TechologyClassifier.CONTENT_TAGS,
                                feature_fields=TechologyClassifier.FEATURE_FIELDS,
                                model_dir=model_subdir,
                                prob_thresholds=TechologyClassifier.PROB_THRESHOLDS,
                                debug=debug,
                                return_most_likely_prediction=return_most_likely_prediction,
                                default_return=default_return
                                )

        # for feature in self.vectorizers['Smartphones'][TechologyClassifier.TITLE_FIELD].get_feature_names():
        #     print feature

    def _transform_field(self, data_df, tag, field):
        vectorizer = self.vectorizers[tag][field]

        data_df_col = [' '.join(x) for x in data_df[field]]
        return vectorizer.transform(data_df_col)

    def _predict_for_each_tag(self, tag, data_df):
        tfidf_title = self._transform_field(data_df, tag, TechologyClassifier.TITLE_FIELD)
        #print data_df[TechologyClassifier.TITLE_FIELD]
        #print tfidf_title

        #print [' '.join(x) for x in data_df[TechologyClassifier.TITLE_FIELD]]
        #print tfidf_title

        tfidf_description = self._transform_field(data_df, tag, TechologyClassifier.DESCRIPTION_FIELD)

        tfidf_extraction_method = self._transform_field(data_df, tag, TechologyClassifier.EXTRACTION_METHOD_FIELD)

        tfidf_raw_tag = self._transform_field(data_df, tag, TechologyClassifier.RAW_TAG_FIELD)

        w1 = 1
        w2 = 1
        w3 = 1
        w4 = 1

        matrix = scipy.sparse.hstack(
            [w1 * tfidf_title, w2 * tfidf_description, w3 * tfidf_extraction_method, w4 * tfidf_raw_tag])

        #print matrix
        test_data = normalize(matrix, norm='l2', axis=1)

        tag_classifier = self.classifiers[tag]
        predicted_probs = tag_classifier.predict_proba(test_data)[ : , 1]

        return predicted_probs

    def _transform_data(self, data):
        for d in data:
            for field in TechologyClassifier.FEATURE_FIELDS:
                raw_field_data = d[field] if field in d else None

                if raw_field_data:
                    if field == TechologyClassifier.EXTRACTION_METHOD_FIELD:
                        d[field] = stemming(' '.join(raw_field_data.strip().split('_')))
                    elif field == TechologyClassifier.RAW_TAG_FIELD:
                        d[field] = stemming(' '.join(raw_field_data))
                    else:
                        #print field, raw_field_data
                        d[field] = stemming(raw_field_data)
                else:
                    d[field] = []

        return data



