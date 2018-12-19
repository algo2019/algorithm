# coding=utf-8
import os, sys

import signal

from Tables import PublishKeyTable, StrategyTable
import time
import atexit
import multiprocessing

logger = None
publish_key = None


def _run_strategy(publish_key, strategy):
    _record_pid(publish_key, strategy)

    from TradeEngine.GlobleConf import Sys
    import signal

    def s(*args, **kwargs):
        _remove_pid(publish_key, strategy)
        Sys.Stoped = True

    signal.signal(signal.SIGRTMAX - 10, s)

    from TradeEngine import CoreEngine
    CoreEngine.run(publish_key, strategy)


def _pid_file(publish_key, strategy):
    dp = 'pids'
    if not os.path.exists(dp):
        os.mkdir(dp)

    return os.path.join(dp, 'StrategyLauncher.{}.{}.pid'.format(publish_key, strategy))


def _exists_pid_file(publish_key, strategy):
    return os.path.exists(_pid_file(publish_key, strategy))


def _record_pid(publish_key, strategy):
    if _exists_pid_file(publish_key, strategy):
        raise Exception('pid file:{} exists!'.format(_pid_file(publish_key, strategy)))

    with open(_pid_file(publish_key, strategy), 'w') as f:
        f.write('{}'.format(os.getpid()))


def _remove_pid(publish_key, strategy):
    p = _pid_file(publish_key, strategy)
    if os.path.exists(p):
        os.remove(p)


def _strategy_list_check(publish_key, strategy_list):
    st = StrategyTable.create()
    if strategy_list is None or len(strategy_list) == 0:
        return st.get_strategy_of_sys(publish_key)
    return strategy_list


def run(publish_key, strategy_list=None):
    strategy_list = _strategy_list_check(publish_key, strategy_list)
    for strategy in strategy_list:
        multiprocessing.Process(target=_run_strategy, args=(publish_key, strategy)).start()


def _wait_for_pid_file_remove(publish_key, strategy):
    for i in xrange(10):
        if not _exists_pid_file(publish_key, strategy):
            return True
        time.sleep(0.1)
    return False


def _wait_for_pid_file_make(publish_key, strategy):
    for i in xrange(10):
        if _exists_pid_file(publish_key, strategy):
            return True
        time.sleep(0.1)
    return False


def stop(publish_key, strategy_list=None):
    strategy_list = _strategy_list_check(publish_key, strategy_list)
    failed = []
    successful = []
    no_pid_file = []
    for strategy in strategy_list:
        if not _exists_pid_file(publish_key, strategy):
            no_pid_file.append(strategy)
            continue

        with open(_pid_file(publish_key, strategy)) as f:
            pid = int(f.readline().strip())
        try:
            os.kill(pid, signal.SIGRTMAX - 10)
        except OSError:
            _remove_pid(publish_key, strategy)

        if _wait_for_pid_file_remove(publish_key, strategy):
            successful.append(strategy)
        else:
            failed.append(strategy)
    print 'stop strategy', publish_key, strategy_list
    print 'success:', len(successful), ' '.join(successful)
    print 'fail:', len(failed), ' '.join(failed)
    print 'no pid file:', len(no_pid_file), ' '.join(no_pid_file)

    if len(failed):
        raise Exception('there has some strategy stop action failed')


def _check(strategy_set):
    import psutil
    failed = []
    successful = []
    no_pid_file = []

    need_remove = []
    for strategy in strategy_set:
        if not _wait_for_pid_file_make(publish_key, strategy):
            no_pid_file.append(strategy)
            need_remove.append(strategy)
            continue
        with open(_pid_file(publish_key, strategy)) as f:
            pid = int(f.readline().strip())

        pids = psutil.pids()
        if pid in pids:
            successful.append(strategy)
            need_remove.append(strategy)
        else:
            failed.append(strategy)
            need_remove.append(strategy)
    for s in need_remove:
        strategy_set.remove(s)

    return successful, failed, no_pid_file


def check(publish_key, strategy_list=None, retry_times=0, max_retry_times=3):
    strategy_set = set(_strategy_list_check(publish_key, strategy_list))
    if len(strategy_set) > 0:
        successful, failed, no_pid_file = _check(strategy_set)

        print 'stop strategy', publish_key, strategy_list
        print 'success:', len(successful), ' '.join(successful)
        print 'fail:', len(failed), ' '.join(failed)
        print 'no pid file:', len(no_pid_file), ' '.join(no_pid_file)

        if len(failed) > 0:
            logger.error('check for start:{} failed!\nremain retry times:{}'.format(
                ' '.join(failed), max_retry_times - retry_times))
            if retry_times < max_retry_times:
                run(publish_key, failed)
                check(publish_key, failed, retry_times + 1)


def start(_publish_key, strategy_list, is_stop):
    global logger
    global publish_key
    publish_key = _publish_key
    from Common.CommonLogServer.RedisLogService import Logger
    logger = Logger(publish_key, 'StrategyLauncher', 'start', 'logger')
    try:
        stop(publish_key, strategy_list)
        if PublishKeyTable.create().get_state(publish_key) == '1':
            print 'System of {} state is 1, it should be stopped!'
        elif not is_stop:
            run(publish_key, strategy_list)
            check(publish_key, strategy_list)
    except:
        import traceback
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    import getopt

    opts, args = getopt.getopt(sys.argv[1:], "sk:")
    stop_flag = False
    for f, v in opts:
        if f == '-k':
            publish_key = v
        if f == '-s':
            stop_flag = True

    if publish_key is None:
        print '-k is need'
        sys.exit(0)

    start(publish_key, args, stop_flag)
