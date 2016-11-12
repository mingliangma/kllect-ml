import json

import numpy as np
import scipy
from pandas.io.json import json_normalize
from scipy.sparse import hstack
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import *
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import normalize
import src.paths as paths
import os.path
from src.labels import inv_labels as predefined_labels
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_selection import SelectKBest, chi2
import src.utils.serialize as serialize
import csv
import collections


labeled_data_filename = os.path.join(paths.MODELING_DATA_SUBDIR, 'mturk_data_160728_cleaned_restrict.json')
subdir = '160728'
model_subdir = 'LR-unigram-no-extraction-method'
result_subdir = os.path.join(paths.MODELING_RESULTS_SUBDIR, subdir, model_subdir)
if not os.path.exists(result_subdir):
    os.mkdir(result_subdir)

binary_model_subdir = os.path.join(paths.MODElS_SUBDIR, 'Technology', subdir)
if not os.path.exists(binary_model_subdir):
    os.mkdirs(binary_model_subdir)


MIN_POS_CNT = 10
def classifier(label, performance_fout):
    video_info = []
    pos_cnt = 0
    with open (labeled_data_filename, 'r') as input_file:
        for line in input_file:
            dic = {}
            r = json.loads(line)
            if label in r['ml_label']:   # classify for this category
                dic['ml_label'] = 1
                pos_cnt += 1
            else:
                dic['ml_label'] = 0

            dic['title'] = r['title']
            dic['description'] = r['description']
            dic['extraction_method'] = r['extraction_method']
            dic['id'] = r['id']
            dic['raw_tags'] = r['raw_tags']
            video_info.append(dic)

    if pos_cnt < MIN_POS_CNT:
        return

    normalized_video_info = json_normalize(video_info)
    # print normalized_article_content

    tfidf_title_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
    tfidf_title = tfidf_title_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['title'])

    tfidf_description_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
    tfidf_description = tfidf_description_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['description'])

    # tfidf_extraction_method_vectorizer = TfidfVectorizer()
    # tfidf_extraction_method = tfidf_extraction_method_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['extraction_method'])

    tfidf_raw_tag_vectorizer = TfidfVectorizer(ngram_range=(1, 1))
    tfidf_raw_tag = tfidf_raw_tag_vectorizer.fit_transform(' '.join(x) for x in normalized_video_info['raw_tags'])

    binary_fname_title = os.path.join(binary_model_subdir, 'TfidfVectorizer_restrict_title_%s.dat' % label)
    serialize.saveData(tfidf_title_vectorizer, binary_fname_title)
    binary_fname_content = os.path.join(binary_model_subdir, 'TfidfVectorizer_restrict_description_%s.dat' % label)
    serialize.saveData(tfidf_description_vectorizer, binary_fname_content)
    # binary_fname_excerpt =  os.path.join(binary_model_subdir, 'TfidfVectorizer_restrict_extraction_method_%s.dat' % label)
    # serialize.saveData(tfidf_extraction_method_vectorizer, binary_fname_excerpt)
    binary_fname_excerpt = os.path.join(binary_model_subdir, 'TfidfVectorizer_restrict_raw_tags_%s.dat' % label)
    serialize.saveData(tfidf_raw_tag_vectorizer, binary_fname_excerpt)

    w1 = 1
    w2 = 1
    w3 = 1
    w4 = 1

    matrix = scipy.sparse.hstack([w1*tfidf_title, w2*tfidf_description, #w3*tfidf_extraction_method,
                                  w4*tfidf_raw_tag])
    norm_matrix = matrix.tocsr()
    #norm_matrix = normalize(matrix, norm='l2', axis=1)

    label_list = []
    for i in video_info:
        label_list.append(i['ml_label'])

    labels = np.array(label_list)
    # matrix_train, matrix_test, label_train, label_test = \
    #     train_test_split(norm_matrix, categories, test_size=0.2)

    _cross_validation(label, labels, norm_matrix, pos_cnt, performance_fout)


    # train the whole thing
    clf = LogisticRegression(class_weight='balanced'). \
        fit(norm_matrix, labels)
    binary_fname_classifier = os.path.join(binary_model_subdir, 'label_classifier_restrict_%s.dat' % label)
    serialize.saveData(clf, binary_fname_classifier)


def _cross_validation(label, labels, norm_matrix, pos_cnt, performance_fout):
    for (fold, (train, test)) in enumerate(StratifiedKFold(labels, n_folds=5)):
        X_train = norm_matrix[train]
        X_test = norm_matrix[test]
        y_train = labels[train]
        y_test = labels[test]

        # ch2 = SelectKBest(chi2, k=10000)
        # X_train = ch2.fit_transform(X_train, y_train)
        # X_test = ch2.transform(X_test)

        clf = LogisticRegression(class_weight='balanced').\
            fit(X_train, y_train)

        #for step in [10]:
        for step in xrange(21):
            threshold = step * 0.05

            predictions = []
            for prob in clf.predict_proba(X_test)[ : , 1]:
                if prob >= threshold:
                    predictions.append([1])
                else:
                    predictions.append([0])

            #y_pred = clf.predict(X_test)

            # print confusion_matrix(label_test, predictions)
            # print classification_report(label_test, predictions)
            # print 'accuracy', accuracy_score(label_test, predictions)
            # print 'f1', f1_score(label_test, predictions)

            precision = precision_score(y_test, predictions)
            recall = recall_score(y_test, predictions)

            performance_fout.write('%s\t%d\t%.2f\t%d\t%.4f\t%.4f\t%.4f\t%.4f\n' % (label, pos_cnt, threshold, fold,
                                                                                   accuracy_score(y_test, predictions),
                                                                                   precision, recall,
                                                                                   f1_score(y_test, predictions)))


def find_optimal_threshold():
    performance_fname = os.path.join(result_subdir, 'performance_summary.txt')
    tag2threshold_preformances = {}
    metrics = ['ACCURACY', 'PRECISION', 'RECALL', 'F1']
    with open(performance_fname) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = '\t')

        for row in csv_reader:
            tag = row['LABEL']
            threshold = float(row['THRESHOLD'])
            #fold = row['FOLD']
            if tag not in tag2threshold_preformances:
                tag2threshold_preformances[tag] = collections.defaultdict(dict)

            tag_performances = tag2threshold_preformances[tag]
            if threshold not in tag_performances:
                tag_performances[threshold] = {x : [] for x in metrics}

            for metric in metrics:
                tag_performances[threshold][metric].append(float(row[metric]))

    predefined_technology_labels = predefined_labels['Technology']
    performance_summary_fname = os.path.join(result_subdir, 'performance_summary_thresholds.txt')
    objective_metric = 'F1'
    tag2optimal_threshold = {}
    with open(performance_summary_fname, 'w') as fout:
        fout.write('LABEL\tTHRESHOLD\t%s\n' % '\t'.join(metrics))
        for tag in predefined_technology_labels:
            if tag not in tag2threshold_preformances:
                continue

            tag_performances = tag2threshold_preformances[tag]

            threshold2objective_metric = {}
            for threshold, performances in sorted(tag_performances.iteritems(), key = lambda x : x[0]):
                fout.write('%s\t%.2f' % (tag, threshold))

                for metric in metrics:
                    scores = performances[metric]
                    avg_score = sum(scores) * 1.0 / len(scores)
                    fout.write('\t%.4f' % avg_score)

                    if metric == objective_metric:
                        threshold2objective_metric[threshold] = avg_score

                fout.write('\n')

            for threshold, score in sorted(threshold2objective_metric.iteritems(),
                                           key=lambda x : (x[1], -x[0]), reverse = True)[ : 1]:
                tag2optimal_threshold[tag] = (threshold, score)

    with open(os.path.join(result_subdir, 'optimal_thresholds.txt'), 'w') as fout:
        fout.write('LABEL\tOPTIMAL_THRESHOLD\t%s\n' % '\t'.join(metrics))
        for tag in predefined_technology_labels:
            if tag not in tag2optimal_threshold:
                continue

            threshold = tag2optimal_threshold[tag][0]
            fout.write('%s\t%s' % (tag, threshold))
            for metric in metrics:
                scores = tag2threshold_preformances[tag][threshold][metric]
                avg_score = sum(scores) * 1.0 / len(scores)
                fout.write('\t%.4f' % avg_score)
            fout.write('\n')


def label_stats():
    label2cnt = {'Others' : 0}
    for label in predefined_labels['Technology']:
        label2cnt[label] = 0

    with open(labeled_data_filename, 'r') as input_file:
        for line in input_file:
            r = json.loads(line)
            for label in r['ml_label']:  # classify for this category
                label2cnt[label] += 1

    for label, cnt in sorted(label2cnt.iteritems(), key=lambda x : x[1], reverse=True):
        print label, cnt



if __name__ == '__main__':
    predefined_technology_labels = predefined_labels['Technology']

    label_list = [#'Others'
                  ]
    for i in predefined_technology_labels:
        label_list.append(i)
    # print label_list

    with open(os.path.join(result_subdir, 'performance_summary.txt'), 'w') as performance_fout:
        performance_fout.write('LABEL\tPOS_CNT\tTHRESHOLD\tFOLD\tACCURACY\tPRECISION\tRECALL\tF1\n')
        for label in label_list:
            print 'Training for "%s"...' % label
            classifier(label, performance_fout)

    find_optimal_threshold()
