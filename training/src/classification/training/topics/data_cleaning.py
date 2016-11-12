import json
from nltk.corpus import stopwords
import collections
from nltk.stem.snowball import SnowballStemmer
import nltk
import os.path


en_stopwords = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')

def stemming(content):
    content = content.lower()
    new_content = []
    for word in nltk.word_tokenize(content):
        if word not in en_stopwords and word.isalpha():
            new_content.append(stemmer.stem(word))
    return new_content

def extraction_method_cleaning(content):
    content = content.lower()
    new_content = content.strip().split('_')
    return stemming(' '.join(new_content))


input_data_filename = '160731_tech_and_non_tech.json'
cleaned_data_filename = '160731_tech_and_non_tech_cleaned.json'

# print stemming('He is going.')
def clean_data():
    with open (cleaned_data_filename, 'w') as output_file:
        with open (input_data_filename, 'r') as input_file:
            for line in input_file:
                dic = {}
                r = json.loads(line)

                dic['id'] = r['_id']
                dic['category'] = r['category']

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

                if 'raw_tags' in r:
                    if r['raw_tags']:
                        dic['raw_tags'] = stemming(' '.join(r['raw_tags']))
                    else:
                        dic['raw_tags'] = []
                else:
                    dic['raw_tags'] = []

                output_file.write(u'%s\n' % json.dumps(dic))


if __name__ == '__main__':
    clean_data()
