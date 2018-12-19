from DBApi.Tables import TradingDateTable, DomInfoTable, MinDataTable, DailyDataTable


def main():
    tdt = TradingDateTable()
    tdt.open()
    tdt.init_data()
    tdt.close()

    dit = DomInfoTable()
    dit.open()
    dit.init_data()
    dit.close()

    dmt = MinDataTable()
    dmt.open()
    dmt.init_data()
    dmt.close()

    ddt = DailyDataTable()
    ddt.open()
    ddt.init_data()
    ddt.close()


def update():
    di = DomInfoTable()
    di.open()
    update_date = di.update()
    di.close()

    dd = DailyDataTable()
    dd.open()
    dd.update(update_date)
    dd.close()

    md = MinDataTable()
    md.open()
    # all_ins_sql = 'select symbolcode from {} where enddate >= ? group by symbolcode'.format(di.name)
    # all_ins = map(lambda x: x[0], di.run_sqls(all_ins_sql, (update_date, )))
    # pprint(all_ins)
    # sql = 'delete from {} where date >= ?'
    # for period in md.periods:
    #     for ins in all_ins:
    #         di.run_sqls(sql.format(md._get_table_name(ins, period)), (update_date, ))

    md.update(update_date)
    md.close()

update()

