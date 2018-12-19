# coding=utf-8
import os
import re
import datetime

root = os.path.abspath(os.path.join(__file__, '..'))
pids_dir = '{}/pids'.format(root)
__conf = None


def get_config():
    global __conf
    if __conf is None:
        import package_config
        import json
        with open(package_config.config_file, 'r') as f:
            __conf = json.load(f)
    return __conf


def _stop_pid_file(pid_file):
    if not os.path.exists(pid_file):
        return
    with open(pid_file) as f:
        try:
            os.kill(int(f.readline().strip()), signal.SIGKILL)
        except OSError:
            pass
    os.remove(pid_file)


def _start_pid_file(pid_file, target, args=tuple()):
    with open(pid_file, 'w') as f:
        f.write('{}'.format(os.getpid()))
    target(*args)


# 服务单进程启动，防止同一服务器启动多次
def standardrun(pid_file_name):
    pid_file = os.path.join(pids_dir, pid_file_name)

    def drt(func):
        def rt(args):
            if args.stop:
                _stop_pid_file(pid_file)
            else:
                _stop_pid_file(pid_file)
                _start_pid_file(pid_file, func, (args,))

        return rt

    return drt


# 时间格式化
def format_to_datetime(dt, time=True, date=True, ms=True):
    ds = re.match(r'\s*(?:(\d{4})[\:\-\/]?(\d{2})[\:\-\/]?(\d{2}))?\s?(?:(\d{2}):?(\d{2}):?(\d{2})\.?(\d+)?)?\s*', str(dt))
    if ds is not None:
        if not time:
            return datetime.date(*map(int, ds.groups(default=0)[:3]))
        if not date:
            if not ms:
                return datetime.time(*map(int, ds.groups(default=0)[3:6]))
            return datetime.time(*map(int, ds.groups(default=0)[3:]))
        if not ms:
            return datetime.datetime(*map(int, ds.groups(default=0)[:6]))
        return datetime.datetime(*map(int, ds.groups(default=0)))
    else:
        raise Exception('format_to_datetime: can not format {} to datetime'.format(dt))

