import random
from dataclasses import dataclass
from typing import Final

import nltk
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import Synset, Lemma


@dataclass
class Word:
    word: str
    definition: str
    synonyms: set[str]
    usages: list[str]


class WordGenerator:
    CORPORA_WORDNET: Final[str] = 'corpora/wordnet'
    WORDNET: Final[str] = 'wordnet'

    WORD_LENGTH_MIN: Final[int] = 5
    WORD_LENGTH_MAX: Final[int] = 10

    def __init__(self) -> None:
        self.synsets: list[Synset] = list(wordnet.all_synsets())

    @classmethod
    def download_corpus(cls) -> None:
        try:
            nltk.data.find(cls.CORPORA_WORDNET)
        except LookupError:
            nltk.download(cls.WORDNET)

    def _random_word_in_synset(self) -> tuple[str, Synset]:
        synset: Synset = random.choice(self.synsets)
        lemma: Lemma = random.choice(synset.lemmas())
        return lemma.name(), synset

    def is_valid(self, word: str) -> bool:
        return (
            '-' in word
            or '_' in word
            or len(word) <= self.WORD_LENGTH_MIN
            or len(word) >= self.WORD_LENGTH_MAX
        )

    def random(self) -> Word:
        word, synset = self._random_word_in_synset()
        while not self.is_valid(word):
            word, synset = self._random_word_in_synset()
        return Word(
            word=word,
            definition=synset.definition(),
            synonyms=set(map(lambda lm: lm.name(), synset.lemmas())),
            usages=synset.examples(),
        )
