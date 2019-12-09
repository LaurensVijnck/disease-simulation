from sinks.base_sink import BaseSink
import os


class FileSink(BaseSink):
    def __init__(self, config):
        self.output_file = None
        self.ouput_file_name = config.get("output_file_name", None)

    def initialize(self):
        if self.ouput_file_name:
            if not os.path.exists(os.path.dirname(self.ouput_file_name)):
                try:
                    os.makedirs(os.path.dirname(self.ouput_file_name))
                except:
                    pass

            self.output_file = open(self.ouput_file_name, "w")

    def close(self):
        self.output_file.close()

    def write(self, message):
        self.output_file.write(message + "\n")