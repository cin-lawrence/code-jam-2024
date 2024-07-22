import random

import nltk
from nltk.corpus import wordnet


def download_wordnet():
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet")


download_wordnet()


def random_word_gen():
    all_synsets = list(wordnet.all_synsets())
    word = None
    word_definition = None

    while (
        word is None or "-" in word or "_" in word or len(word) <= 5 or len(word) >= 10
    ):

        random_synset = random.choice(all_synsets)

        random_lemma = random.choice(random_synset.lemmas())

        word = random_lemma.name()

        word_definition = random_synset.definition()

    return word, word_definition
