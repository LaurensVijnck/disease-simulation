from sinks.base_sink import BaseSink

class ConsoleSink(BaseSink):
    def __init__(self, config):
        pass

    def initialize(self):
        pass

    def close(self):
        pass

    def write(self, message):
        print(message)