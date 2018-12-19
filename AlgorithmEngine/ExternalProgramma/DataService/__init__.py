def Client():
    import client
    return client.Client()


def DataService():
    import dataserice
    return dataserice.DataService()


def start_data_service():
    import dataserice
    return dataserice.start()
