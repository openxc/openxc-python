import logging
from logging import NullHandler

logging.getLogger("openxc").addHandler(NullHandler())
