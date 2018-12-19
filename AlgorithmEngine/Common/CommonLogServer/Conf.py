from Common.Dao.ConfigDao import ConfigDao
# HTTP_DB
POST_WEB = '/logs'
API_VERSION = 'v1.0'
DB_PATH = './logs.db'
LOG_NAME = 'LOG.DBServer'
# REDIS_FILE

SYSTEM_NAME = 'RedisLogService'
DEBUG = False

try:
    import package_config
    import os
    if os.path.exists(package_config.config_file):
        import json
        with open(package_config.config_file) as f:
            config = json.load(f)
        SERVICE_HOST = config['redis_host']
        REDIS_HOST = config['redis_host']
        REDIS_PORT = config['redis_port']
        REDIS_DB = config['redis_logging']['redis_db']
        LOG_PATH = config['redis_logging']['log_path']
        print SYSTEM_NAME, 'Load config from:', package_config.config_file
        dao = ConfigDao()
        dao.set(SYSTEM_NAME, 'SERVICE_HOST', SERVICE_HOST)
        dao.set(SYSTEM_NAME, 'REDIS_HOST', REDIS_HOST)
        dao.set(SYSTEM_NAME, 'REDIS_PORT', REDIS_PORT)
        dao.set(SYSTEM_NAME, 'REDIS_DB', REDIS_DB)
        dao.set(SYSTEM_NAME, 'LOG_PATH', LOG_PATH)
        print SYSTEM_NAME, 'config update to ConfigDao'
    else:
        raise Exception('config file not found')
except Exception as e:
    print SYSTEM_NAME, 'load from config file:', package_config.config_file, str(e)
    dao = ConfigDao()
    print SYSTEM_NAME, 'Load config from ConfigDao'
    SERVICE_HOST = dao.get(SYSTEM_NAME, 'SERVICE_HOST')
    REDIS_HOST = dao.get(SYSTEM_NAME, 'REDIS_HOST')
    REDIS_PORT = int(dao.get(SYSTEM_NAME, 'REDIS_PORT'))
    REDIS_DB = int(dao.get(SYSTEM_NAME, 'REDIS_DB'))
    LOG_PATH = dao.get(SYSTEM_NAME, 'LOG_PATH')


def get_key(pk, name):
    return '%s.LOG_MSG.%s' % (pk, name)

tags_start = 0x1
