from concurrent.futures import ThreadPoolExecutor

import numpy as np, logging

from qswift.compiler import Compiler
import time


class QSwiftExecutor:
    def __init__(self):
        self.logger = logging.getLogger("qswift.executor.QSwiftExecutor")

    def execute(self, compiler: Compiler, swift_channels):
        strings = []
        start = time.time()
        for swift_channel in swift_channels:
            string = compiler.to_string(swift_channel)
            strings.extend(string)
        middle = time.time()
        self.logger.debug(f"to_string ({len(swift_channels)}): {middle - start}")
        values = []
        for j, string in enumerate(strings):
            value = compiler.evaluate(string)
            values.append(value)
            if j % 1000 == 0:
                logging.info(f"{j}")
        self.logger.debug(f"evaluate ({len(swift_channels)}): {time.time() - middle}")
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
