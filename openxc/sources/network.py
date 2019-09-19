"""A network socket data source."""


import logging
import socket

from .base import DataSourceError
from .socket import SocketDataSource

LOG = logging.getLogger(__name__)


class NetworkDataSource(SocketDataSource):
    """A data source reading from a network socket, as implemented
    in the openxc-vehicle-simulator .
    """
    DEFAULT_PORT = 50001

    def __init__(self, host=None, port=None, **kwargs):
        """Initialize a connection to the network socket.

        Kwargs:
            host - optionally override the default network host (default is local machine)
            port - optionally override the default network port (default is 50001)
            log_mode - optionally record or print logs from the network source

        Raises:
            DataSourceError if the socket connection cannot be opened.
        """
        super(NetworkDataSource, self).__init__(**kwargs)
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
