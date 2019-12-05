from population.household import HouseHold
from population.individual import Individual
from datetime import datetime
import csv

class DiseaseLogger:
    def __init__(self, config, global_config):
        self.__output_file = None
        self.__enabled = config.get("enabled", False)
        self.__output_file_name = config.get("file_name", None)
        self.__date_format = global_config.get("date_format", "%Y-%m-%d")
        self.__csv_writer = None

        if self.__enabled and self.__output_file_name:
            self.__output_file = open(self.__output_file_name, "w")
            self.__csv_writer = csv.writer(self.__output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def log(self, individual: Individual, date: datetime):
        if self.__enabled:
            date_formatted = date.strftime(self.__date_format)
            self.__csv_writer.writerow([date_formatted, individual.get_id()])

    def __del__(self):
        self.__output_file.close()