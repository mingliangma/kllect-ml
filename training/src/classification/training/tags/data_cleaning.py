import json
from nltk.corpus import stopwords
import collections
from nltk.stem.snowball import SnowballStemmer
import nltk
import src.classification.config as config
import os.path
import src.paths as paths
from src.labels import inv_labels as predefined_labels



en_stopwords = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')

def stemming(content):
    content = content.lower()
    new_content = []
    for word in nltk.word_tokenize(content):
        if word not in en_stopwords and word.isalpha():#(word.isalpha() or (word.isalnum() and not word.isdigit())):
            new_content.append(stemmer.stem(word))
    return new_content

def extraction_method_cleaning(content):
    content = content.lower()
    new_content = content.strip().split('_')
    return stemming(' '.join(new_content))


input_data_filename = os.path.join(paths.MODELING_DATA_SUBDIR, 'mturk_data_160715_restrict.json')
cleaned_data_filename = os.path.join(paths.MODELING_DATA_SUBDIR, 'mturk_data_160728_cleaned_restrict.json')

# print stemming('He is going.')
def clean_data():
    with open (cleaned_data_filename, 'w') as output_file:
        with open (input_data_filename, 'r') as input_file:
            for line in input_file:
                dic = {}
                r = json.loads(line)

                dic['id'] = r['_id']

                if 'description' in r:
                    dic['description'] = stemming(r['description'])
                else:
                    dic['description'] = []

                if 'title' in r:
                    dic['title'] = stemming(r['title'])
                else:
                    dic['title'] = []

                if 'description_contains_content' in r:
                    dic['description_contains_content'] = r['description_contains_content']
                else:
                    dic['description_contains_content'] = []

                if 'extraction_method' in r:
                    dic['extraction_method'] = extraction_method_cleaning(r['extraction_method'])
                else:
                    dic['extraction_method'] = []

                if 'ml_label' in r:
                    dic['ml_label'] = list(set([x if x in predefined_technology_labels else 'Others' for x in r['ml_label']]))
                else:
                    dic['ml_label'] = []
                if 'raw_tags' in r:
                    if r['raw_tags']:
                        dic['raw_tags'] = stemming(' '.join(r['raw_tags']))
                    else:
                        dic['raw_tags'] = []
                else:
                    dic['raw_tags'] = []

                output_file.write(u'%s\n' % json.dumps(dic))


# expanded_cleaned_data_filename = os.path.join(paths.MODELING_DATA_SUBDIR, 'mturk_data_160728_cleaned_restrict_expaned.json')
# def expand_data():
#     with open(expanded_cleaned_data_filename, 'w') as output_file:
#         with open(cleaned_data_filename, 'r') as input_file:
#             for line in input_file:
#                 dic = {}
#                 r = json.loads(line)
#                 if r['description_contains_content']:
#                     for i in r['ml_label']:
#                         dic['id'] = r['id']
#                         dic['description'] = r['description']
#                         dic['title'] = r['title']
#                         dic['extraction_method'] = r['extraction_method']
#                         dic['ml_label'] = i
#                         dic['raw_tags'] = r['raw_tags']
#                         output_file.write(u'%s\n' % json.dumps(dic))


predefined_technology_labels = predefined_labels['Technology']
labeled_data_filename = os.path.join(paths.MODELING_DATA_SUBDIR, 'mturk_data_160715_cleaned_restrict_expaned_label.json')
def label_cleaning():
    with open(labeled_data_filename, 'w') as output_file:
        with open(cleaned_data_filename, 'r') as input_file:
            for line in input_file:
                dic = {}
                r = json.loads(line)
                dic['id'] = r['id']
                dic['description'] = r['description']
                dic['title'] = r['title']
                dic['extraction_method'] = r['extraction_method']
                if r['ml_label'] in predefined_technology_labels:
                    dic['ml_label'] = r['ml_label']
                else:
                    dic['ml_label'] = 'Others'
                dic['raw_tags'] = r['raw_tags']
                output_file.write(u'%s\n' % json.dumps(dic))


if __name__ == '__main__':
    clean_data()
    #expand_data()
    #label_cleaning()