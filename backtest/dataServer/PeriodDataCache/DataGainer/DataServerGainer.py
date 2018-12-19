from .BaseDataGainer import DataGainer


class DataServerGainer(DataGainer):

    def get_data(self, conf):
        import dataServer
        d = dataServer.dataServer()
        d.start()
        rt = d.wmm(conf, False)
        d.stop()
        return rt
