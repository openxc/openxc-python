class Vehicle(object):

    def __init__(self, data_source=None):
        self.data_source = data_source

    def get(self, measurement_type):
        pass

    def listen(self, measurement_type, listener):
        pass
