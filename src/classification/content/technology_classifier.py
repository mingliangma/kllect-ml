from base_classifier import BaseClassifier
from labels import labels
import scipy

from sklearn.preprocessing import normalize
import traceback
import config
from utils import text_cleaning


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
        #EXTRACTION_METHOD_FIELD,
        RAW_TAG_FIELD
    ]

    def __init__(self, model_subdir,
                 debug = False,
                 return_most_likely_prediction = False,
                 default_return = None,
                 id_field = 'id',
                 predictions_field = 'content_tags'):
        BaseClassifier.__init__(self,
                                content_category=TechologyClassifier.CONTENT_CATEGORY,
                                content_tags=TechologyClassifier.CONTENT_TAGS,
                                feature_fields=TechologyClassifier.FEATURE_FIELDS,
                                model_subdir=model_subdir,
                                prob_thresholds=TechologyClassifier.PROB_THRESHOLDS,
                                debug=debug,
                                return_most_likely_prediction=return_most_likely_prediction,
                                default_return=default_return,
                                id_field=id_field,
                                predictions_field=predictions_field
                                )

        # for feature in self.vectorizers['Smartphones'][TechologyClassifier.TITLE_FIELD].get_feature_names():
        #     print feature

    def _transform_field(self, data_df, tag, field):
        vectorizer = self.vectorizers[tag][field]

        # print field
        # print data_df[field]
        return vectorizer.transform(data_df[field])

    def _predict_for_each_tag(self, tag, data_df):
        tfidf_title_X = self._transform_field(data_df, tag, TechologyClassifier.TITLE_FIELD)
        #print data_df[TechologyClassifier.TITLE_FIELD]
        #print tfidf_title

        #print [' '.join(x) for x in data_df[TechologyClassifier.TITLE_FIELD]]
        #print tfidf_title

        tfidf_description_X = self._transform_field(data_df, tag, TechologyClassifier.DESCRIPTION_FIELD)

        #tfidf_extraction_method = self._transform_field(data_df, tag, TechologyClassifier.EXTRACTION_METHOD_FIELD)

        tfidf_raw_tag_X = self._transform_field(data_df, tag, TechologyClassifier.RAW_TAG_FIELD)

        matrix = scipy.sparse.hstack(
            [tfidf_title_X,
             tfidf_description_X,
             tfidf_raw_tag_X]).tocsr()

        tag_classifier = self.classifiers[tag]
        predicted_probs = tag_classifier.predict_proba(matrix)[ : , 1]

        return predicted_probs

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



