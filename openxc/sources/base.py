
"""
@file    openxc-python\openxc\sources\base.py Base Sources Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Abstract base interface for vehicle data sources."""

import threading

from openxc.formats.json import JsonFormatter


class DataSource(threading.Thread):
    """Interface for all vehicle data sources. This inherits from Thread and
    when a source is added to a vehicle it attempts to call the ``start()``
    method if it exists. If an implementer of DataSource needs some background
    process to read data, it's just a matter of defining a ``run()`` method.

    A data source requires a callback method to be specified. Whenever new data
    is received, it will pass it to that callback.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var callback
    # The callback function to use.
    ## @var daemon
    # Boolean value representing if the datasource operates like a daemon.
    
    def __init__(self, callback=None):
        """Construct a new DataSource.

        By default, DataSource threads are marked as ``daemon`` threads, so they
        will die as soon as all other non-daemon threads in the process have
        quit.

        Kwargs:
            callback - function to call with any new data received
        @param callback function to call with any new data received.
        """
        super(DataSource, self).__init__()
        self.callback = callback
        self.daemon = True

    def _read(self, timeout=None):
        """Read data from the source.

        Kwargs:
            timeout (float) - if the source implementation could potentially
                block, timeout after this number of seconds.
        @param timeout if the source implementation could potentially block, 
        timeout after this number of seconds.
        """
        raise NotImplementedError("Don't use DataSource directly")


class BytestreamDataSource(DataSource):
    """A source that receives data is a series of bytes, with discrete 
    messages separated by a newline character.

    Subclasses of this class need only to implement the ``_read`` method.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var bytes_received
    # The number of bytes received.
    ## @var corrupted_messages
    # The number of corrupted messages received.
    
    def __init__(self, callback=None):
        """Initialization Routine
        @param callback The callback function name."""
        super(BytestreamDataSource, self).__init__(callback)
        self.bytes_received = 0
        self.corrupted_messages = 0

    def run(self):
        """Continuously read data from the source and attempt to parse a valid
        message from the buffer of bytes. When a message is parsed, passes it
        off to the callback if one is set.
        """
        message_buffer = b""
        while True:
            message_buffer += self._read()
            while True:
                message, message_buffer, byte_count = self._parse_message(
                        message_buffer)
                if message is None:
                    break
                if not hasattr(message, '__iter__') or not (
                        ('name' in message and 'value' in message) or (
                        'id' in message and 'data' in message)):
                    self.corrupted_messages += 1
                    break

                self.bytes_received += byte_count
                if self.callback is not None:
                    self.callback(message,
                            data_remaining=len(message_buffer) > 0)

    def _parse_message(self, message_buffer):
        """If a message can be parsed from the given buffer, return it and
        remove it.

        Returns the message if one could be parsed, otherwise None, and the
        remainder of the buffer.
        
        @param message_buffer The message_buffer object instance.
        """
        if not isinstance(message_buffer, bytes):
            message_buffer = message_buffer.encode("utf-8")
        parsed_message = None
        remainder = message_buffer
        message = ""
        if b"\n" in message_buffer:
            message, _, remainder = message_buffer.partition(b"\n")
            try:
                parsed_message = JsonFormatter.deserialize(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                pass
        return parsed_message, remainder, len(message)


class DataSourceError(Exception):
    """Data Source Error Exception Class
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    pass
