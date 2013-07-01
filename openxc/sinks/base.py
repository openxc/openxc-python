
"""
@file    openxc-python\openxc\sinks\base.py Base Sinks Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Common operations for all vehicle data sinks."""

class DataSink(object):
    """A base interface for all data sinks. At the minimum, a data sink must
    have a :func:`receive` method.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""

    def receive(self, message, **kwargs):
        """Handle an incoming vehicle data message.

        Args:
            message (dict) - a new OpenXC vehicle data message

        Kwargs:
           data_remaining (bool) - if the originating data source can peek ahead
               in the data stream, this argument will True if there is more data
               available.
        
        @param message a new OpenXC vehicle data message.
        @param kwargs Additional inputs. 
        """
        raise NotImplementedError("Don't use DataSink directly")
