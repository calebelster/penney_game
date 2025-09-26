import time
import tracemalloc
from functools import wraps

class Debugger:
    @staticmethod
    def debug(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            print(f"Function `{func.__name__}` executed in {end_time - start_time:.6f} seconds")
            print(f"Peak memory usage: {peak / 1024:.2f} KiB")
            return result
        return wrapper