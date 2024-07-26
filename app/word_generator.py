import secrets
from dataclasses import dataclass
from typing import Final

import nltk
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import Lemma, Synset


@dataclass
class Word:
    """The dataclass for a Word."""

    word: str
    definition: str
    synonyms: set[str]
    usages: list[str]


class WordGenerator:
    """The class for generating a random word between 5 to 10 chars."""

    CORPORA_WORDNET: Final[str] = "corpora/wordnet"
    WORDNET: Final[str] = "wordnet"

    WORD_LENGTH_MIN: Final[int] = 5
    WORD_LENGTH_MAX: Final[int] = 15

    def __init__(self) -> None:
        self.download_corpus()
        self.synsets: list[Synset] = []
        self.mp_len_words: dict[int, list[str]] = {}
        self.mp_len_synsets: dict[int, list[Synset]] = {}
        self.separate_lengths()

    def separate_lengths(self) -> None:
        """Populate the wordnet data for each length."""
        for synset in wordnet.all_synsets():
            word = synset.name().split(".", 1)[0]
            if not self.is_valid(word):
                continue
            self.synsets.append(synset)
            word_length = len(word)
            self.mp_len_words.setdefault(word_length, [])
            self.mp_len_words[word_length].append(word)
            self.mp_len_synsets.setdefault(word_length, [])
            self.mp_len_synsets[word_length].append(synset)

    @classmethod
    def download_corpus(cls) -> None:
        """Ensure the wordnet corpus is downloaded."""
        try:
            nltk.data.find(cls.CORPORA_WORDNET)
        except LookupError:
            nltk.download(cls.WORDNET)

    def _random_word_in_synset(self) -> tuple[str, Synset]:
        synset: Synset = secrets.choice(self.synsets)
        lemma: Lemma = secrets.choice(synset.lemmas())
        return lemma.name(), synset

    def is_valid(self, word: str) -> bool:
        """Validate the word."""
        return (
            "-" not in word
            and "_" not in word
            and self.WORD_LENGTH_MIN <= len(word) <= self.WORD_LENGTH_MAX
        )

    def random(self, length: int | None = None) -> Word:
        """Randomizes a word from the synset."""
        dataset: list[Synset] = (
            self.synsets
            if (
                length is None
                or length < self.WORD_LENGTH_MIN
                or length > self.WORD_LENGTH_MAX
            )
            else self.mp_len_synsets[length]
        )
        synset = secrets.choice(dataset)
        return Word(
            word=synset.name(),
            definition=synset.definition(),
            synonyms={lm.name() for lm in synset.lemmas()},
            usages=synset.examples(),
        )

    def __str__(self) -> str:
        bank_stat = " | ".join(
            [
                f"Len {length}: {len(words)}"
                for length, words in sorted(self.mp_len_words.items())
            ]
        )
        return (
            "<WordGenerator"
            f" {bank_stat}"
            f" | MinLength = {self.WORD_LENGTH_MIN}"
            f" | MaxLength = {self.WORD_LENGTH_MAX}"
            ">"
        )


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    wordgen = WordGenerator()
    logger.info(wordgen)
