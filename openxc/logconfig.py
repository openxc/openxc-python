import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Null Handler Class"""
        def emit(self, record):
            """Emit Routine"""
            pass

logging.getLogger("openxc").addHandler(NullHandler())
