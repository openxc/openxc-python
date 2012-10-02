from __future__ import absolute_import

import logging

from .base import DataSource

LOG = logging.getLogger(__name__)

class TraceDataSource(DataSource):
    DEFAULT_PORT = "/dev/ttyUSB0"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, callback, filename=None):
        super(TraceDataSource, self).__init__(callback)
        try:
            self.trace_file = open(filename, "r")
        except IOError as e:
            raise DataSourceError("Unable to open trace file %s" % filename, e)
        else:
            LOG.debug("Opened trace file %s", filename)

    def start(self):
        super(TraceDataSource, self).start()
        self.trace_file.close()

    def read(self):
        # TODO play back in proper time by checking timestamp
        return self.trace_file.readline()

    def _write(self, message):
        raise NotImplementedError("Can't send commands to a trace file")
