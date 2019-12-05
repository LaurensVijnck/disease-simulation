from population.household import HouseHold
from population.individual import Individual
from datetime import datetime


class DiseaseLogger:
    def __init__(self, config, global_config):
        self.__output_file = None
        self.__enabled = config.get("enabled", False)
        self.__output_file_name = config.get("file_name", None)
        self.__date_format = global_config.get("date_format", "%Y-%m-%d")

        if self.__enabled and self.__output_file_name:
            self.__output_file = open(self.__output_file_name, "w")

    def log(self, individual: Individual, household: HouseHold, date: datetime):
        if self.__enabled:
            date_formatted = date.strftime(self.__date_format)
            pass

    def __del__(self):
        self.__output_file.close()