import random
from typing import Generator, Any

def get_word(length: int | None = None) -> str:
    """get a word with specified lenght"""
    if length is None:
        length = random.randint(5,15)
    
    word = "foobar"

    return word

def color_for_guess(
        guess: str | tuple[str] | list[str], 
        word: str | tuple[str] | list[str]
        ) -> Generator[int, Any, Any]:
    """get the integer representing the status"""
    if len(guess) > len(word):
        pass # TODO
    elif len(guess) < len(word):
        pass # TODO
    else:
        for g_letter, w_letter in zip(guess,word):
            yield _get_color_code(g_letter, w_letter, word)

def _get_color_code(guess_letter: str, word_letter: str, word: str) -> int:

    '''
    - ❤️  for wrong letter (4)
    - 💛  for correct letter, wrong position (1)
    - 💚  for correct letter, correct location (0)
    - 💙  for deviated letter, correct position (2)
    - 💜  for deviated letter, wrong position (3)
    '''
    # A = 65
    # Z = 90
    guess_ascii = ord(guess_letter)
    word_ascii = ord(word_letter)

    if guess_letter == word_letter:
        return 0
    
    if guess_letter in word:
        return 1
    
    if abs(guess_ascii - word_ascii) < 4:
        return 2
    
    if any(map(lambda x: abs(guess_ascii - ord(x)) < 4, word)):
        return 3
    
    return 4

    