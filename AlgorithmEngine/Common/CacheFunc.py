import time


def cache(timeout=1):
    cache_data = {}

    def rt(func):
        def _func(*args, **kwargs):
            key = (func, str(args))
            if cache_data.get(key, (0, 0))[1] + timeout < time.time():
                cache_data[key] = (func(*args, **kwargs), time.time())
            return cache_data[key][0]
        return _func

    return rt
