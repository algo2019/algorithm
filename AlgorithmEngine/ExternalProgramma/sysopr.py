# coding=utf-8
from Tables import PublishKeyTable, ConfTable
from pprint import pprint
import sys


def show_system():
    print '========================'
    print '0', '查看系统'
    print '1', '添加/修改系统'
    print '2', '移除系统'
    print '5', '帮助信息'
    print '9', '退出'
    print '========================'


def opr_sys():
    pt = PublishKeyTable.create()
    while 1:
        try:
            show_system()
            a = raw_input()
            if a == '0':
                print 'publisk_key', 'lab', 'state', 'type'
                print 0
                for line in pt.get_all_data():
                    for i in line:
                        print i,
                    print
            elif a == '1':
                print '请输入 系统代码 系统名称 系统状态 系统类别 [排序序号]'
                args = raw_input().split()
                pt.insert(*args)
            elif a == '2':
                print '请输入 系统代码'
                args = raw_input().split()
                pt.delete(*args)
            elif a == '5':
                print 'state: ', '0 已停用 1 正在运行'
                print 'type: ', 'user 可查看 1 user2 可查看2'
            elif a == '9':
                return
        except Exception as e:
            sys.stderr.write(str(e) + '\n')


def show_config():
    print '========================'
    print '0', '查看默认配置'
    print '1', '查看指定系统配置'
    print '2', '修改配置'
    print '9', '退出'
    print '========================'


def opr_config():
    ct = ConfTable.create()
    while 1:
        try:
            show_config()
            a = raw_input()
            if a == '0':
                pprint(ct.get_conf(ct.DEFAULT))
            elif a == '1':
                print '请输入：系统代码'
                pk = raw_input()
                pprint(ct.get_conf(pk))
            elif a == '2':
                print '请出入：系统代码 配置名称 值'
                args = raw_input().split()
                ct.set(*args)
            elif a =='9':
                return
        except Exception as e:
            sys.stderr.write(str(e) + '\n')


def show_home():
    print '========================'
    print '1', '系统操作'
    print '2', '配置操作'
    print '9', '退出'
    print '========================'


def opr_home():
    while 1:
        show_home()
        a = raw_input()
        if a == '9':
            return
        elif a == '1':
            return opr_sys()
        elif a == '2':
            return opr_config()


if __name__ == '__main__':
    opr_home()
