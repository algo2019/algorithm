# -*- coding: utf-8 -*-
"""
打包时配置
记录打包时需要写入程序的配置
"""
WEB_ADMIN = 'admin'
WEB_PASSWORD = '123456'
config_file = '/etc/algorithm_trade_platform/config.json'


def get_conf():
    import json
    with open(config_file, 'r') as f:
        return json.load(f)
