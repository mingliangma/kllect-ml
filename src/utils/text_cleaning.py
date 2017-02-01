import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
from unidecode import unidecode
import string


exclusion = set(string.punctuation)#.difference({'.'})
en_stopwords = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')
http_pattern = re.compile(r'https?:\/\/.*[\r\n]*', re.MULTILINE)
NUM_REPLACEMENT = 'NUM'
ordinal_pattern = re.compile(r'[0-9/]+(?:st|nd|rd|th)', re.I)
MAX_TOKEN_LEN = 20


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


def process_description(description):
    # remove links

    sentences = []

    if description:
        description = remove_http_links(description)
        for sent in nltk.sent_tokenize(description):
            processed_sent = process_text(sent)
            if processed_sent:
                sentences.append(processed_sent)

    return sentences


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_ordinal(s):
    if ordinal_pattern.match(s):
        return True

    return False


def process_word(token):
    if not token:
        return ''

    token = token.lower()
    if is_number(token):
        return NUM_REPLACEMENT
    elif token not in en_stopwords:
        stem = stemmer.stem(token)
        clean_stem = ''.join([x for x in stem if x not in exclusion])

        if clean_stem != '':
            if is_number(clean_stem):
                return NUM_REPLACEMENT
            else:
                if is_ordinal(clean_stem) or len(clean_stem) >= MAX_TOKEN_LEN:
                    return ''
                else:
                    return clean_stem

    return None


def process_text(text):
    tokens = []
    if text:
        for token in nltk.word_tokenize(unidecode(text)):
            clean_token = process_word(token)
            if clean_token:
                tokens.append(clean_token)

    return ' '.join(tokens)


def remove_http_links(text):
    clean_text = re.sub(http_pattern, '', text)
    return clean_text.strip()

