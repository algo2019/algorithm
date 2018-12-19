import time


class Handler(object):
    def process(self, system, key, state, timestamp):
        print '{} {} {}: {:f}'.format(system, key, state, timestamp)

    def __call__(self, *args, **kwargs):
        self.process(*args, **kwargs)


class Config(object):
    TimeProfile = False
    Sys = 'None'
    Handler = Handler()


class Filter(object):
    def process(self, strategy, name, item):
        return True

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)

_filters = []


def add_filter(filter):
    _filters.append(filter)


def _check(strategy, name, item):
    for f in _filters:
        if not f(strategy, name, item):
            return False
    return True


def time_profile_init(strategy, name, item, time_=None):
    if Config.TimeProfile:
        if not _check(strategy, name, item):
            return
        key = _key(strategy, name, item)
        Config.Handler(Config.Sys, key, 'start', time_ or time.time())


def time_profile_end(strategy, name, item, time_=None):
    if Config.TimeProfile:
        if not _check(strategy, name, item):
            return
        key = _key(strategy, name, item)
        Config.Handler(Config.Sys, key, 'end', time_ or time.time())


def time_profile(strategy, name, item, state, time_=None):
    if Config.TimeProfile:
        if not _check(strategy, name, item):
            return
        key = _key(strategy, name, item)
        Config.Handler(Config.Sys, key, state, time_ or time.time())


def _key(strategy, name, item):
    return '{}.{}.{}'.format(strategy, name, item)
