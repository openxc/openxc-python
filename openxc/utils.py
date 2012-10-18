class Range(object):
    def __init__(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    def within_range(self, value):
        return value >= self.min and value <= self.max

    @property
    def spread(self):
        return self.max - self.min
