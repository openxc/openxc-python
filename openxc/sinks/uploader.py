from threading import Thread
import time
import logging
import requests

from openxc.formats import JsonFormatter
from .queued import QueuedSink

LOG = logging.getLogger(__name__)


class UploaderSink(QueuedSink):
    """Uploads all incoming vehicle data to a remote web application via HTTP.

    TODO document service side format
    """
    UPLOAD_BATCH_SIZE = 25
    HTTP_TIMEOUT = 5000

    def __init__(self, url):
        """Args:
            url (str) - the URL to send an HTTP POST request with vehicle data
        """
        super(UploaderSink, self).__init__()
        self.recorder = self.Uploader(self.queue, url)

    class Uploader(Thread):
        def __init__(self, queue, url):
            super(UploaderSink.Uploader, self).__init__()
            self.daemon = True
            self.queue = queue
            self.records = []
            self.url = url
            self.start()

        @classmethod
        def _upload(cls, url, records):
            payload = JsonFormatter.serialize(records)
            response = requests.post(url, data=payload)

            if response.status_code != requests.codes.created:
                LOG.warning("Unable to upload %d records, received %d status "
                            "from %s", len(records), response.status_code, url)
            else:
                LOG.debug("Uploaded %d records (status %d)", len(records),
                        response.status_code)

        def run(self):
            while True:
                message, _ = self.queue.get()

                message['timestamp'] = time.time()
                self.records.append(message)
                if len(self.records) > UploaderSink.UPLOAD_BATCH_SIZE:
                    self._upload(self.url, self.records)

                self.queue.task_done()
