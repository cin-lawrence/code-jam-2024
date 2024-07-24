from concurrent.futures import ThreadPoolExecutor
from functools import partial

import ollama


def llama_sum(input):
    executor = ThreadPoolExecutor(max_workers=3)
    func = partial(ollama.generate, model="llama3", prompt=input, stream=False)
    future = executor.submit(func)

    return future
