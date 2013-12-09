"""A network socket data source."""
from __future__ import absolute_import

import logging
import socket
from .base import BytestreamDataSource, DataSourceError

LOG = logging.getLogger(__name__)


class NetworkDataSource(BytestreamDataSource):
    """A data source reading from a network socket, as implemented
    in the openxc-vehicle-simulator .
    """
    DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
    DEFAULT_PORT = 50001

    def __init__(self, callback=None, host=None, port=None):
        """Initialize a connection to the network socket.

        Kwargs:
            host - optionally override the default network host (default is local machine)
            port - optionally override the default network port (default is 50001)

        Raises:
            DataSourceError if the socket connection cannot be opened.
        """
        super(NetworkDataSource, self).__init__(callback)
        self.host = host or self.DEFAULT_HOST
        self.port = port or self.DEFAULT_PORT
        self.port = int(self.port)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host,self.port))
            self.stream = s.makefile("wb")
        except (OSError, socket.error) as e:
            raise DataSourceError("Unable to open socket connection at  "
                    "%s:%s: %s" % (self.host,self.port, e))
        else:
            LOG.debug("Opened socket connection at %s:%s", self.host, self.port)

    def _read(self):
        try:
            line = self.stream.readline()
        except (OSError, socket.error) as e:
            raise DataSourceError("Unable to read from socket connection at  "
                    "%s:%s: %s" % (self.host,self.port, e))
        if not line:
            raise DataSourceError("Unable to read from socket connection at  "
                "%s:%s" % (self.host,self.port))
        return line
