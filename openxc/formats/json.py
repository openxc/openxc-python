
"""
@file    openxc-python\openxc\formats\json.py JsonFormatter Class Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   JSON formatting utilities.
"""

from __future__ import absolute_import

import json

class JsonFormatter(object):
    """Json Formatter Class
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    @classmethod
    def deserialize(cls, message):
        """Deserialize Routine
        @param cls the object class instance.
        @param message the message to deserialize.
        @return Decoded JSON Message in UTF-8 format."""
        return json.loads(message.decode("utf-8"))

    @classmethod
    def serialize(cls, data):
        """Serialize Routine
        @param cls the object class instance.
        @param data the data to serialize.
        @return Serialized version of the JSON data message."""
        return json.dumps(data)
