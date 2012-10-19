class DataSink(object):
    def receive(self, message, **kwargs):
        raise NotImplementedError("Don't use DataSink directly")
