# coding=utf-8
import os
import time
import multiprocessing
import signal

from Tables import PublishKeyTable, ConfTable


def _pid_file(publish_key):
    dp = 'pids'
    if not os.path.exists(dp):
        os.mkdir(dp)

    return os.path.join(dp, 'Launcher.{}.pid'.format(publish_key))


def _exists_pid_file(publish_key):
    return os.path.exists(_pid_file(publish_key))


def _record_pid(publish_key):
    if _exists_pid_file(publish_key):
        raise Exception('pid file:{} exists!'.format(_pid_file(publish_key)))

    with open(_pid_file(publish_key), 'w') as f:
        f.write('{}'.format(os.getpid()))


def _remove_pid(publish_key):
    p = _pid_file(publish_key)
    if os.path.exists(p):
        os.remove(p)


def run_system(publish_key):
    _record_pid(publish_key)

    from TradeEngine import ServerApp, GlobleConf
    GlobleConf.init_conf(publish_key)

    from TradeEngine.GlobleConf import Sys
    import signal

    def s(*args, **kwargs):
        _remove_pid(publish_key)
        Sys.Stoped = True

    signal.signal(signal.SIGRTMAX - 10, s)

    ServerApp.start()
    ServerApp.register_web_action()

    import time
    while not Sys.Stoped:
        time.sleep(1)
    print 'stoped'


def run(publish_key_list=None):
    publish_table = PublishKeyTable.create()
    if publish_key_list is None or len(publish_key_list) == 0:
        publish_key_list = publish_table.select_all()

    for publish_key in publish_key_list:
        print publish_key
        if publish_table.get_state(publish_key) != '0':
            print publish_key, 'state is not 0, skip it.'
        else:
            multiprocessing.Process(target=run_system, args=(publish_key,)).start()


def _wait_for_pid_file_remove(publish_key):
    for i in xrange(10):
        if not _exists_pid_file(publish_key):
            return True
        time.sleep(0.1)
    return False


def _wait_for_pid_file_make(publish_key):
    for i in xrange(10):
        if _exists_pid_file(publish_key):
            return True
        time.sleep(0.1)
    return False


def _publish_key_list_check(publish_key_list):
    if publish_key_list is None or len(publish_key_list) == 0:
        publish_table = PublishKeyTable.create()
        return publish_table.select_all()
    return publish_key_list


def stop(publish_key_list=None):
    publish_key_list = _publish_key_list_check(publish_key_list)
    failed = []
    successful = []
    no_pid_file = []
    for publish_key in publish_key_list:
        if not _exists_pid_file(publish_key):
            no_pid_file.append(publish_key)
            continue

        with open(_pid_file(publish_key)) as f:
            pid = int(f.readline().strip())

        try:
            os.kill(pid, signal.SIGRTMAX - 10)
        except OSError:
            os.remove(_pid_file(publish_key))

        if _wait_for_pid_file_remove(publish_key):
            successful.append(publish_key)
        else:
            failed.append(publish_key)

    print 'stop system:', publish_key_list
    print 'success:', len(successful), ' '.join(successful)
    print 'fail:', len(failed), ' '.join(failed)
    print 'no pid file:', len(no_pid_file), ' '.join(no_pid_file)

    if len(failed):
        raise Exception('there has some system stop action failed')


def add_sys(publish_key):
    st = PublishKeyTable.create()
    if not st.exists():
        st.create()
    st.insert_sys(publish_key)


def set_sys_conf(publish_key, conf_name, conf_value):
    ct = ConfTable.create()
    ct.set(publish_key, conf_name, conf_value)


def show_sys_conf(publish_key=None):
    st = ConfTable.create()
    if publish_key is None:
        print st.select_all()
    else:
        print st.get_conf(publish_key)


def delete_sys(publish_key=None):
    pt = PublishKeyTable.create()
    st = ConfTable.create()
    if publish_key is None:
        pt.drop()
        st.drop()
    else:
        pt.delete(publish_key)
        st.delete(publish_key)


def delete_conf(publish_key, conf_name):
    st = ConfTable.create()
    st.delete(publish_key, conf_name)


if __name__ == '__main__':
    import sys, getopt

    opts, args = getopt.getopt(sys.argv[1:], "s")

    stop(args)
    for f, v in opts:
        if f == '-s':
            sys.exit(0)
    run(args)
