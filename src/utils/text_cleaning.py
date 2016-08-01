from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import nltk

en_stopwords = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')


def stemming(content):
    if not content:
        return []

    content = content.lower()
    new_content = []
    for word in nltk.word_tokenize(content):
        if word not in en_stopwords:
            new_content.append(stemmer.stem(word))
    return new_content

