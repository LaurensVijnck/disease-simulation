import csv

from datetime import datetime
from events.event import EventHandler
from population.individual import Individual
from population.population import Population
from reporter import Reporter


class EventLogPlayer:
    """
    Class to process a given event log.
    """
    def __init__(self, config, global_config, population: Population, reporter: Reporter):
        self.__reporter = reporter
        self.__population = population

        # Initialize the reader
        pop_csv = open(config.get("event_log"), mode='r')
        self.__event_reader = csv.DictReader(pop_csv)
        self.__next_event = next(self.__event_reader)
        self.__date_format = global_config.get("date_format", "%Y-%m-%d")

        # Load initial population
        self._load_initial(config.get("initial_population"))

    def fast_forward(self, max_date: datetime):
        """
        Function to fast forward the population up to the specified date. For each of the events
        in the event log, there exists a corresponding EventHandler.

        :param max_date: (datetime) date to evolve the population to
        """
        while self.__next_event and self.__parse_date(self.__next_event["event_date"]) <= max_date:
            try:
                EventHandler.construct(self.__population, self.__next_event, self.__date_format).process()
                self.__reporter.add_event(self.__next_event["event_type"])
            except Exception as e:
                self.__reporter.add_error(str(e) + f"(individual id: {self.__next_event['ID']})")
                self.__reporter.add_error(self.__next_event["event_type"])

            # Fetch next event
            self.__next_event = next(self.__event_reader)

    def _load_initial(self, population_csv):
        """
        Function to load an initial, csv-formatted population.

        :param population_csv: (string) path to the csv file
        """
        num = 0
        with open(population_csv, mode='r') as pop_csv:
            csv_reader = csv.DictReader(pop_csv)
            for row in csv_reader:
                if csv_reader.line_num == 0:
                    continue

                individual = Individual.create(row, self.__date_format)
                num += 1
                self.__population.add(individual, individual.get_hh_id())
        self.__reporter.info(f"Pre-loaded population with {num} individuals.")

    def __parse_date(self, date_str):
        """
        Function to parse the given date string, according to the specified date format.

        :param date_str: (string) date string to parse
        """
        return datetime.strptime(date_str, self.__date_format)