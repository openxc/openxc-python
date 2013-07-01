
"""
@file    openxc-python\openxc\sinks\uploader.py Uploader Sinks Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Uploader Sinks Script."""

from threading import Thread
import time
import logging
import requests

from openxc.formats import JsonFormatter
from .queued import QueuedSink

## @var LOG
# The logging object instance.
LOG = logging.getLogger(__name__)


class UploaderSink(QueuedSink):
    """Uploads all incoming vehicle data to a remote web application via HTTP.
    
    TODO document service side format
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4
    @todo document service side format."""
    
    ## @var UPLOAD_BATCH_SIZE
    # The upload batch size setting.
    UPLOAD_BATCH_SIZE = 25
    ## @var HTTP_TIMEOUT
    # The HTTP Timeout Settings in Seconds.
    HTTP_TIMEOUT = 5000
    ## @var recorder
    # The recorder object instance.
    
    def __init__(self, url):
        """Args:
            url (str) - the URL to send an HTTP POST request with vehicle data
        @param url the URL to send an HTTP POST request with vehicle data.
        """
        super(UploaderSink, self).__init__()
        self.recorder = self.Uploader(self.queue, url)

    class Uploader(Thread):
        """ The Uploader Class
        @author  Christopher Peplin github@rhubarbtech.com
        @date    June 25, 2013
        @version 0.9.4"""
        
        ## @var daemon
        # Boolean representing if this datasource operates like a daemon.
        ## @var queue
        # The queue object instance.
        ## @var records
        # List object containing the records related to this class instance.
        ## @var url
        # The uploader URL setting.
        
        def __init__(self, queue, url):
            """Initialization Routine
            @param queue The queue object instance.
            @param url The url for this upload."""
            super(UploaderSink.Uploader, self).__init__()
            self.daemon = True
            self.queue = queue
            self.records = []
            self.url = url
            self.start()

        @classmethod
        def _upload(cls, url, records):
            """Upload Routine
            @param url The url setting for the upload.
            @param records The records to upload."""
            payload = JsonFormatter.serialize(records)
            response = requests.post(url, data=payload)

            if response.status_code != requests.codes.created:
                LOG.warn("Unable to upload %d records, received %d status "
                        "from %s", len(records), response.status_code, url)
            else:
                LOG.debug("Uploaded %d records (status %d)", len(records),
                        response.status_code)

        def run(self):
            """Run Routine."""
            while True:
                message, _ = self.queue.get()

                message['timestamp'] = time.time()
                self.records.append(message)
                if len(self.records) > UploaderSink.UPLOAD_BATCH_SIZE:
                    self._upload(self.url, self.records)

                self.queue.task_done()
