class BaseSink:
    def __init__(self, config):
        ...

    def initialize(self):
        ...

    def close(self):
        ...

    def write(self, message):
        ...