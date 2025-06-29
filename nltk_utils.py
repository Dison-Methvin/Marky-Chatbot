import numpy as np
import nltk
import html
# nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

def tokenize(sentence):
    """
    split sentence into array of words/tokens
    a token can be a word or punctuation character, or number
    """
    return word_tokenize(sentence)

def stem(word):
    """
    stemming = find the root form of the word
    """
    return stemmer.stem(word.lower())

def decode_html_entities(text):
    """
    Decodes HTML entities in the text to ensure proper rendering of symbols and emojis.
    """
    return html.unescape(text)

def bag_of_words(tokenized_sentence, words):
   
    # stem each word
    sentence_words = [stem(word) for word in tokenized_sentence]
    # initialize bag with 0 for each word
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words: 
            bag[idx] = 1

    return bag
