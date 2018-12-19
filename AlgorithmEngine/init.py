# coding=utf-8
"""
init.py
    系统部署完成之后，进行的初始化工作
"""


def call():
    # type: () -> None
    """
    call
        复制配置文件至指定目录
        向MySQL中建立数据表
        向WebAccountTable中加入管理员账户
    """
    import os, shutil
    import package_config
    if os.path.exists(package_config.config_file):
        print 'config file is exists', package_config.config_file
    else:
        config_path = os.path.abspath(os.path.join(package_config.config_file, '..'))
        try:
            os.makedirs(config_path)
        except OSError:
            pass
        shutil.copy('config.json', package_config.config_file)

    from Common.Dao import DataItemDao, DBDataDao, TradeRecordDao
    from _mysql_exceptions import ProgrammingError
    try:
        DBDataDao().create()
        DataItemDao().create()
        TradeRecordDao().create()
    except ProgrammingError as e:
        pass

    from Tables import WebAccountTable
    at = WebAccountTable.create()
    import package_config
    at.insert_user(package_config.WEB_ADMIN, package_config.WEB_PASSWORD, at.admin)


if __name__ == '__main__':
    call()
