from population.individual import Individual
from datetime import datetime
import csv


class DiseaseLogger:
    def __init__(self, config, global_config):
        # Parsing config
        self.__output_file = None
        self.__enabled = config.get("enabled", False)
        self.__output_file_name = config.get("file_name", None)
        self.__date_format = global_config.get("date_format", "%Y-%m-%d")
        self.__csv_writer = None

        # Cols to write
        cols = ["date_infected", "influx", "id", "HH_ID", "sex", "age", "num_infected_hh", "hh_size"]

        # Create file
        if self.__enabled and self.__output_file_name:
            self.__output_file = open(self.__output_file_name, "w")
            self.__csv_writer = csv.DictWriter(self.__output_file, fieldnames=cols)
            self.__csv_writer.writeheader()

    def log(self, individual: Individual, date: datetime, influx):
        if self.__enabled:
            date_formatted = date.strftime(self.__date_format)
            household = individual.get_household()

            self.__csv_writer.writerow({
                "date_infected": date_formatted,
                "influx": influx,
                "id": individual.get_id(),
                "HH_ID": household.get_id(),
                "sex": individual.get_sex(),
                "age": individual.get_age(date),
                "num_infected_hh": household.get_num_infected(),
                "hh_size": household.get_size()
            })

    def __del__(self):
        self.__output_file.close()