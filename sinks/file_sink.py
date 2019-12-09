from sinks.base_sink import BaseSink


class FileSink(BaseSink):
    def __init__(self, config):
        self.output_file = None
        self.ouput_file_name = config.get("output_file_name", None)

    def initialize(self):
        if self.ouput_file_name:
            self.output_file = open(self.ouput_file_name, "w")

    def close(self):
        self.output_file.close()

    def write(self, message):
        self.output_file.write(message + "\n")