from .BaseCache import Cacher
import os
import traceback
import cPickle
import platform


class FileCache(Cacher):
    def __init__(self, data_path):
        self._data_path = data_path
        self.form_str = '%Y%m%d%H%M%S'
        self.pickle_protocol = None
        self._init_for_system_platform()

    def _init_for_system_platform(self):
        if platform.system() == 'Windows':
            self.pickle_protocol = 0
        else:
            self.pickle_protocol = 2
        self.file_name_lambda = lambda args: '.'.join(map(str, args))

    def cache_data(self, conf, data):
        fp = self._get_file_for_write(conf)
        cPickle.dump(data, fp, self.pickle_protocol)
        fp.close()

    def _get_file_for_write(self, conf):
        file_path = self.get_file_path(conf)
        try:
            return open(file_path, 'w')
        except:
            print traceback.format_exc()
            raise Exception('file open err:%s' % file_path)

    def _get_file_for_read(self, conf):
        file_path = self.get_file_path(conf)
        if not os.path.exists(file_path):
            return None
        try:
            return open(file_path, 'r')
        except:
            return None

    def get_file_path(self, conf):
        file_name = self.file_name_lambda(conf.values())
        return os.path.join(self._data_path, file_name)

    def get_data(self, conf):
        fp = self._get_file_for_read(conf)
        if fp is None:
            return None
        rt = cPickle.load(fp)
        fp.close()
        return rt
