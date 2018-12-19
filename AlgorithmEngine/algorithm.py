#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
algorithm.py
    系统打包综合程序
"""

import argparse
import os
import signal
import sys
from subprocess import Popen

root = os.path.abspath(os.path.join(__file__, '..'))

__all__ = ['args_parse_and_run']

cmd_init = 'init'
cmd_make = 'make'
cmd_mkdata = 'mkdata'
cmd_redis_log = 'log'
cmd_flask_web = 'web'
cmd_ctp_data = 'ctpdata'
cmd_data_resample = 'dataresample'
cmd_launcher = 'launcher'
cmd_strategy_launcher = 'strategy'
cmd_sysopr = 'sysopr'
cmd_cache_tick = 'cachetick'
cmd_day_data_update = 'daydata'
cmd_net_data_service = 'netdataservice'

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


def _init(args):
    from init import call
    if not os.path.exists(pids_dir):
        os.mkdir(pids_dir)
    call()


@standardrun('REDISLOG.pid')
def _redis_log_service(args):
    from Common import RedisLogMain
    RedisLogMain.run()


def _start_mkdata(args):
    if 'subrun' in args.action:
        from MarketDataServer.CTPClient import CTPClientRun
        standardrun('MKDATA.pid')(lambda x: CTPClientRun.main(get_config()['mk_configs']))(args)
    else:
        env = {'LD_LIBRARY_PATH': "{}/lib".format(root)}
        env.update(os.environ)
        Popen(['python2'] + sys.argv + ['subrun'], env=env).wait()


@standardrun('FLASKWEB.pid')
def _flask_web(args):
    from FlaskWeb import StartServer
    StartServer.main()


@standardrun('DATARESAMPLE.pid')
def _data_resample(args):
    from MarketDataServer import MarketDataMain
    MarketDataMain.main()


def _sys_opr(args):
    from ExternalProgramma.sysopr import opr_home
    opr_home()


def _launcher(args):
    if 'subrun' in args.action:
        import Launcher
        Launcher.stop(args.action)
        if not args.stop:
            Launcher.run(args.action)
    else:
        env = {'LD_LIBRARY_PATH': "{}/lib".format(root)}
        env.update(os.environ)
        Popen(['python2'] + sys.argv + ['subrun'], env=env).wait()


def _make(args):
    os.system("cd MarketDataServer/CTPClient && make clean && make && make install && make clean")
    os.system("cd TradeEngine/CTPTradeEngineOS && make clean && make && make install && make clean")

def _strategy_launcher(args):
    import StrategyLauncher
    StrategyLauncher.start(args.publishkey, args.action, args.stop)


@standardrun('CATCHETICK.pid')
def _cache_tick(args):
    from Common.Dao.TickDataDao import TickDataDao
    TickDataDao().start_update_redis_wait()


def _day_data_update(args):
    if 'subrun' in args.action:
        from ExternalProgramma.DayDataUpdate import daydatesaveoper
        standardrun('DAYDATAUPDATE.pid')(lambda x: daydatesaveoper.main())(args)
    else:
        env = {'LD_LIBRARY_PATH': "{}/lib".format(root)}
        env.update(os.environ)
        Popen(['python'] + sys.argv + ['subrun'], env=env).wait()


def _net_data_service(args):
    from ExternalProgramma.DataService import start_data_service
    start_data_service()


_action_table = {

}


def _run_cmd(args):
    for cmd in _action_table:
        if getattr(args, cmd):
            _action_table[cmd](args)
            break


def args_parse_and_run(args):
    """
    :param args:
    :return:
    :tip: 修改时区
    """
    parser = argparse.ArgumentParser(description="AlgorithmEngine 综合程序")

    def add_service(cmd, help, target, short=None):
        if not short:
            parser.add_argument('--{}'.format(cmd), action='store_true', default=False, help=help)
        else:
            parser.add_argument(short, '--{}'.format(cmd), action='store_true', default=False, help=help)
        _action_table[cmd] = target

    add_service(cmd_make, "编译", _make)
    add_service(cmd_init, "部署之后初始化", _init)
    add_service(cmd_mkdata, "对MarketDataService操作，stop标识可用", _start_mkdata)
    add_service(cmd_net_data_service, "对NetDataService操作", _net_data_service)
    add_service(cmd_data_resample, "对DataResample操作，stop标识可用", _data_resample)
    add_service(cmd_cache_tick, "对CacheTickService操作，stop标识可用", _cache_tick)
    add_service(cmd_day_data_update, "对DayDataUpdateService操作，stop标识可用", _day_data_update)
    add_service(cmd_flask_web, "对WebService操作，stop标识可用", _flask_web)
    add_service(cmd_redis_log, "对LogService操作，stop标识可用", _redis_log_service)
    add_service(cmd_launcher, "对Launcher操作", _launcher, '-l')
    add_service(cmd_strategy_launcher, "对StrategyLauncher操作", _strategy_launcher, '-s')
    add_service(cmd_sysopr, "配置操作", _sys_opr)

    parser.add_argument('--stop', action='store_true', default=False, help="停止标志,没有此标识默认为启动/重启")
    parser.add_argument('-k', '--publishkey', help="系统代号(仅对-s标识有效)")

    parser.add_argument('action', nargs='*')

    _run_cmd(parser.parse_args(args))


if __name__ == '__main__':
    args_parse_and_run(sys.argv[1:])
