from concurrent.futures import ThreadPoolExecutor

import numpy as np, logging

from qswift.compiler import Compiler


class QSwiftExecutor:
    def execute(self, compiler: Compiler, swift_channels):
        strings = []
        for swift_channel in swift_channels:
            string = compiler.to_string(swift_channel)
            strings.append(string)
        values = []
        for j, string in enumerate(strings):
            value = compiler.evaluate(string)
            values.append(value)
            if j % 1000 == 0:
                logging.info(f"{j}")
        return np.sum(values)


class ThreadPoolQSwiftExecutor(QSwiftExecutor):
    def __init__(self, max_workers, chunk_size):
        self.max_workers = max_workers
        self.chunk_size = chunk_size

    def execute(self, compiler: Compiler, swift_channels):
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            for index, codes in enumerate(self.split(swift_channels)):
                futures.append(e.submit(self.val, compiler, codes, index))
        result = 0
        count = 0
        for future in futures:
            result += future.result()
            count += self.chunk_size
        value = result
        return value

    def val(self, compiler, codes, index):
        result = 0
        count = 0
        for code in codes:
            v = compiler.evaluate(code)
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
