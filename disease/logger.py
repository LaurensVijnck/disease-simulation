from population.individual import Individual
from datetime import datetime
import csv

from population.summary import PopulationSummary


def serialize_age_distribution(inf_age_distribution):
    """
    Function to serialize age distribution to string format.

    :param inf_age_distribution:
    :return: (string) serialized age distribution
    """
    dist = ""
    first = True
    for key in sorted(inf_age_distribution):
        if not first:
            dist += "|"
        dist += str(key) + "-" + str(inf_age_distribution[key])
        first = False

    return dist


class DiseaseLogger:
    def __init__(self, config, global_config):
        # Parsing config
        self.__enabled = config.get("enabled", False)
        self.__inf_output_file = None
        self.__sim_out_file = None
        self.__inf_log_file_name = config.get("inf_log_file_name", None)
        self.__sim_log_file_name = config.get("sim_log_file_name", None)
        self.__date_format = global_config.get("date_format", "%Y-%m-%d")
        self.__inf_log = None
        self.__sim_log = None

        # Cols to write
        inf_cols = [
            "date_infected",
            "influx",
            "id",
            "HH_ID",
            "sex",
            "age",
            "inf_age_distribution",
            "num_infected_hh",
            "hh_size"
        ]

        sim_cols = [
            "iteration",
            "num_susceptible",
            "num_infected",
            "num_recovered"
        ]

        # Create file
        if self.__enabled and self.__inf_log_file_name:
            self.__inf_output_file = open(self.__inf_log_file_name, "w")
            self.__inf_log = csv.DictWriter(self.__inf_output_file, fieldnames=inf_cols)
            self.__inf_log.writeheader()

        if self.__enabled and self.__sim_log_file_name:
            self.__sim_output_file = open(self.__sim_log_file_name, "w")
            self.__sim_log = csv.DictWriter(self.__sim_output_file, fieldnames=sim_cols)
            self.__sim_log.writeheader()

    def log_infection(self, individual: Individual, date: datetime, influx):
        if self.__enabled:
            date_formatted = date.strftime(self.__date_format)
            household = individual.get_household()

            self.__inf_log.writerow({
                "date_infected": date_formatted,
                "influx": int(influx),
                "id": individual.get_id(),
                "HH_ID": household.get_id(),
                "sex": individual.get_sex(),
                "age": individual.get_age(date),
                "inf_age_distribution": serialize_age_distribution(household.get_infected_age_distribution()),
                "num_infected_hh": household.get_num_infected(),
                "hh_size": household.get_size()
            })

    def log_summary(self, date: datetime, summary: PopulationSummary):
        if self.__enabled:
            date_formatted = date.strftime(self.__date_format)

            self.__sim_log.writerow({
                "iteration": date_formatted,
                "num_susceptible": summary.get_total_susceptible(),
                "num_infected": summary.get_total_infected(),
                "num_recovered": summary.get_total_recovered()
            })

    def __del__(self):
        if self.__enabled and self.__inf_log_file_name:
            self.__inf_output_file.close()

        if self.__enabled and self.__sim_log_file_name:
            self.__sim_output_file.close()