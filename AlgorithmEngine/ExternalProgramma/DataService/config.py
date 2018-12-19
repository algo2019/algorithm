from Common.Dao.ConfigDao import ConfigDao

__all__ = ['Port', 'Host']

dao = ConfigDao('Main')

s_name = 'DataService'

Host = dao.get(s_name, 'Host')
Port = int(dao.get(s_name, 'Port'))

if not Host or not Port:
    raise Exception('DataService Config Need Host And Port!')
