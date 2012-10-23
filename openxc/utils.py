"""Data containers and other utilities."""
import time

class Range(object):
    """Encapsulates a ranged defined by a min and max numerical value."""
    def __init__(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    def within_range(self, value):
        """Returns True if the value is between this Range, inclusive."""
        return value >= self.min and value <= self.max

    @property
    def spread(self):
        """Returns the spread between this Range's min and max."""
        return self.max - self.min


class AgingData(object):
    """Mixin to associate a class with a time of birth."""

    def __init__(self):
        self.created_at = time.time()

    @property
    def age(self):
        """Return the age of the data in seconds."""
        return time.time() - self.created_at
