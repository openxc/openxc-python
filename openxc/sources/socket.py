from __future__ import absolute_import

from .base import BytestreamDataSource, DataSourceError

# TODO can we get rid of this?
import socket


class SocketDataSource(BytestreamDataSource):
    def read(self):
        try:
            line = ""
            while '\x00' not in line:
                # TODO this is fairly inefficient
                line += self.socket.recv(1)
        except (OSError, socket.error, IOError) as e:
            raise DataSourceError("Unable to read from socket connection at  "
                    "%s:%s: %s" % (self.host,self.port, e))
        if not line:
            raise DataSourceError("Unable to read from socket connection at  "
                    "%s:%s" % (self.host,self.port))
        return line

    def write_bytes(self, data):
        return self.socket.send(data)
