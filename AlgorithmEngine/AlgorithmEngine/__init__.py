import sys

class Watcher(object):
    @classmethod
    def find_module(cls, name, path, target=None):
        ds = name.split('.')
        if 'AlgorithmEngine' in ds:
            return cls
        return None

    @classmethod
    def load_module(cls, name):
        ds = name.split('.')
        ds[ds.index('AlgorithmEngine')] = 'TradeEngine'
        p = '.'.join(ds)
        __import__(p)
        m = sys.modules[p]
        sys.modules[name] = sys.modules[p]
        return m

sys.meta_path.append(Watcher)
