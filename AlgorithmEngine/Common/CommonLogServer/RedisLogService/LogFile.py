import datetime
import glob
import os

from Common.CommonLogServer import Conf


class LogFile(object):
    def __init__(self):
        self.__files = {}
        self.__log_path = Conf.LOG_PATH

    @staticmethod
    def __makedir(path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def __close(self):
        for key in self.__files:
            self.__files[key].close()

    def get_file_path(self, pk, level, filename):
        if level in ['DEBUG', 'WARN', 'INFO', 'ERR']:
            level = 'LEVEL_LOG'
        return os.path.join(self.__log_path, pk, level, filename)

    def get_file(self, pk, level, name):
        pk_path = os.path.join(self.__log_path, pk)
        date = str(datetime.datetime.now().date())

        if level in ['DEBUG', 'WARN', 'INFO', 'ERR']:
            level = 'LEVEL_LOG'
        file_key = '{}.{}.{}'.format(pk, name, level)
        file_path = os.path.join(self.__makedir(os.path.join(pk_path, level)), '%s.%s' % (name, date))
        if not self.__files.get(file_key) or not os.path.exists(file_path):
            self.__files[file_key] = (date, open(file_path, 'a'))
        if self.__files[file_key][0] != date:
            try:
                self.__files[file_key][1].close()
            except:
                pass
            self.__files[file_key] = (date, (open(file_path, 'a')))
        return self.__files[file_key][1]

    def get_file_list(self, pk, level, name):
        pk_path = os.path.join(self.__log_path, pk)
        if level in ['DEBUG', 'WARN', 'INFO', 'ERR']:
            level = 'LEVEL_LOG'
        path = os.path.join(pk_path, level, '{}*'.format(name))
        file_list = [os.path.basename(i) for i in glob.glob(path)]
        file_list.sort(reverse=True)
        return file_list
