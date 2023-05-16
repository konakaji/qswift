from concurrent.futures import ThreadPoolExecutor

import numpy as np

from qswiftencoder.compiler import Compiler


class QSwiftExecutor:
    def __init__(self, compiler: Compiler):
        self.compiler = compiler

    def execute(self, swift_channels):
        strings = []
        for swift_channel in swift_channels:
            strings.append(self.compiler.to_string(swift_channel))
        values = []
        for string in strings:
            values.append(self.compiler.evaluate(string))
        return np.sum(values)


class ThreadPoolQSwiftExecutor(QSwiftExecutor):
    def __init__(self, compiler: Compiler, max_workers, chunk_size):
        super().__init__(compiler)
        self.max_workers = max_workers
        self.chunk_size = chunk_size

    def execute(self, swift_channels):
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            for index, codes in enumerate(self.split(swift_channels)):
                futures.append(e.submit(self.val, codes, index))
        result = 0
        count = 0
        for future in futures:
            result += future.result()
            count += self.chunk_size
        value = result
        return value

    def val(self, codes, index):
        result = 0
        count = 0
        for code in codes:
            v = self.compiler.evaluate(code)
            result += v
            count += 1
        print(f"{self.chunk_size * (index + 1)}")
        return result

    def split(self, codes):
        chunks = []
        chunk = []
        chunks.append(chunk)
        for c in codes:
            if len(chunk) == self.chunk_size:
                chunk = []
                chunks.append(chunk)
            chunk.append(c)
        return chunks