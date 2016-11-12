from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from sklearn.cross_validation import StratifiedKFold, cross_val_score, train_test_split
import json
from pandas.io.json import json_normalize
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
import scipy
from sklearn.preprocessing import normalize
from scipy.sparse import hstack
from sklearn.svm import SVC, LinearSVC
from sklearn import linear_model
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
import collections
import src.utils.serialize as serialize
from datetime import datetime
import src.paths as paths
import os.path
from scipy.stats import randint as sp_randint


def classifier(label):
    video_info = []
    with open (os.path.join(paths.MODELING_DATA_SUBDIR, '160731_tech_and_non_tech_cleaned.json'), 'r') as input_file:
        for line in input_file:
            dic = {}
            r = json.loads(line)
            dic['category'] = r['category']
            dic['title'] = r['title']
            dic['description'] = r['description']
            dic['extraction_method'] = r['extraction_method']
            dic['id'] = r['id']
            dic['raw_tags'] = r['raw_tags']
            video_info.append(dic)

    normalized_video_info = json_normalize(video_info)
    # print normalized_article_content

    tfidf_title_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_title = tfidf_title_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['title'])

    tfidf_description_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_description = tfidf_description_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['description'])

    # tfidf_extraction_method_vectorizer = TfidfVectorizer()
    # tfidf_extraction_method = tfidf_extraction_method_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['extraction_method'])

    tfidf_raw_tag_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_raw_tag = tfidf_raw_tag_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['raw_tags'])

    model_subdir = os.path.join(paths.MODElS_SUBDIR, label, '160812')
    binary_fname_title = os.path.join(model_subdir, 'TfidfVectorizer_restrict_title_%s.dat' % label)
    serialize.saveData(tfidf_title_vectorizer, binary_fname_title)
    binary_fname_content = os.path.join(model_subdir, 'TfidfVectorizer_restrict_description_%s.dat' % label)
    serialize.saveData(tfidf_description_vectorizer, binary_fname_content)
    #binary_fname_excerpt = 'TfidfVectorizer_restrict_extraction_method_%s.dat' % label
    #serialize.saveData(tfidf_extraction_method_vectorizer, binary_fname_excerpt)
    binary_fname_excerpt = os.path.join(model_subdir, 'TfidfVectorizer_restrict_raw_tag_%s.dat' % label)
    serialize.saveData(tfidf_raw_tag_vectorizer, binary_fname_excerpt)

    w1 = 1
    w2 = 1
    w3 = 1
    w4 = 1

    norm_matrix = scipy.sparse.hstack([w1*tfidf_title, w2*tfidf_description, #w3*tfidf_extraction_method,
                                  w4*tfidf_raw_tag]).tocsr()

    #norm_matrix = normalize(matrix, norm='l2', axis=1)

    category_list = []
    for i in video_info:
        if i['category'] == 'tech':
            i['category'] = 1
        else:
            #print i['category'], i['title']
            i['category'] = 0
        category_list.append(i['category'])

    categories = np.array(category_list)

    label_classifier = linear_model.LogisticRegression(class_weight='balanced').\
            fit(norm_matrix, categories)
    binary_fname_classifier = os.path.join(model_subdir, 'label_classifier_restrict_%s.dat' % label)
    serialize.saveData(label_classifier, binary_fname_classifier)


    # cross validation


    ### parameter tuning ###
    # pipeline_lr = Pipeline([
    #     ('classifier', linear_model.LogisticRegression()),  # <== change model here
    # ])
    #
    # param_lr = {'classifier__C': [1, 10, 100, 1000],
    #             'classifier__solver' : ['newton-cg', 'lbfgs', 'liblinear', 'sag'],
    #             'classifier__class_weight': ['balanced', None]}
    # # pipeline_svc = Pipeline([
    # #     ('classifier', SVC()),  # <== change model here
    # # ])
    # # param_svc = [
    # #     {'classifier__C': [1, 10, 100, 1000], 'classifier__kernel': ['linear']},
    # #     {'classifier__C': [1, 10, 100, 1000], 'classifier__gamma': [0.001, 0.0001], 'classifier__kernel': ['rbf']},
    # # ]
    #
    #
    # grid_lr = GridSearchCV(
    #     pipeline_lr,  # pipeline from above
    #     param_grid=param_lr,  # parameters to tune via cross validation
    #     refit=True,  # fit using all data, on the best detected classifier
    #     # n_jobs=-1,  # number of cores to use for parallelization; -1 for "all cores"
    #     scoring='precision',  # what score are we optimizing?
    #     cv=StratifiedKFold(categories, n_folds=5),  # what type of cross validation to use
    # )
    #
    # lr_classifier = grid_lr.fit(norm_matrix, categories)
    # print lr_classifier.grid_scores_
    # ### parameter tuning ###


    for (fold, (train, test)) in enumerate(StratifiedKFold(categories, random_state = 2, n_folds=5)):
        matrix_train = norm_matrix[train, :]
        matrix_test = norm_matrix[test, :]
        category_train = categories[train]
        category_test = categories[test]

        category_classifier = linear_model.LogisticRegression(class_weight='balanced').\
            fit(matrix_train, category_train)

        predictions = category_classifier.predict(matrix_test)
        print classification_report(category_test, predictions)

        if fold == 4:
            print
            train_titles = [video_info[t]['title'] for t in train]
            test_titles = [video_info[t]['title'] for t in test]

            print 'train titles:'
            for title in train_titles:
                print title

            print '\n\ntest titles:'
            for title in test_titles:
                print title

        print confusion_matrix(category_test, predictions)
        print 'accuracy', accuracy_score(category_test, predictions)
        print 'f1', f1_score(category_test, predictions)


if __name__ == '__main__':
    classifier(label = 'Technology')








