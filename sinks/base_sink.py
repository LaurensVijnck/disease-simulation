class BaseSink:
    def __init__(self, config):
        pass

    def initialize(self):
        ...

    def close(self):
        ...

    def write(self, message):
        ...