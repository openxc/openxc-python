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
    DEFAULT_PORT = 50001

    def __init__(self, callback=None, host=None, port=None, log_mode=None):
        """Initialize a connection to the network socket.

        Kwargs:
            host - optionally override the default network host (default is local machine)
            port - optionally override the default network port (default is 50001)
            log_mode - optionally record or print logs from the network source

        Raises:
            DataSourceError if the socket connection cannot be opened.
        """
        super(NetworkDataSource, self).__init__(callback, log_mode)
        self.host = host or socket.gethostbyname(socket.gethostname())
        self.port = port or self.DEFAULT_PORT
        self.port = int(self.port)

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except (OSError, socket.error) as e:
            raise DataSourceError("Unable to open socket connection at  "
                    "%s:%s: %s" % (self.host,self.port, e))
        else:
            LOG.debug("Opened socket connection at %s:%s", self.host, self.port)

    def read(self):
        try:
            line = ""
            while '\x00' not in line:
                # TODO this is fairly inefficient
                line += self.socket.recv(1)
        except (OSError, socket.error) as e:
            raise DataSourceError("Unable to read from socket connection at  "
                    "%s:%s: %s" % (self.host,self.port, e))
        if not line:
            raise DataSourceError("Unable to read from socket connection at  "
                "%s:%s" % (self.host,self.port))
        return line
