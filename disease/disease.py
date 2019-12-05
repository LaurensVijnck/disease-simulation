import datetime as dt
from datetime import datetime
from collections import deque
from disease.logger import DiseaseLogger
from population.individual import Individual
from population.population import Population
from population.household import HouseHold
from population.summary import PopulationSummary
from reporter import Reporter
from disease.transmission import Transmission


class Disease:
    def __init__(self, config, global_config, population: Population, reporter: Reporter):
        self.__population = population
        self.__reporter = reporter
        self.__infection_duration = config.get("infection_duration", 3)
        self.__age_child_limit = config.get("age_child_limit", 18)

        # Create disease logger
        logger_config = config.get("logger")
        self.__disease_logger = DiseaseLogger(logger_config, global_config)

        # Initialize Transmission model
        transmission_config = config.get("transmission")
        self.__transmission = Transmission(transmission_config)

        # Compute initial summary
        self.__initial_summary = PopulationSummary(self.__population)

        # Recovery queue
        self.__recovery_queue = deque()

    # FUTURE: Parallelize this loop.
    def apply_disease_model(self, curr_date: datetime):
        """
        Function to apply the disease model on the population as-is. The population
        and recovery queue is updated accordingly.
        """
        summary = PopulationSummary(self.__population, self.__initial_summary)
        self.__reporter.set_population_summary(summary)
        self.process_recovery_queue(curr_date)
        for household in self.__population.household_gen():
            household.compute_metrics(curr_date, self.__age_child_limit)
            for individual in household.member_gen():

                if individual.is_infected() or individual.is_recovered():
                    continue

                if self.__transmission.occurs(individual, household, summary):
                    self.set_infected(individual, curr_date)

        return len(self.__recovery_queue) > 0

    def process_recovery_queue(self, max_date: datetime):
        """
        Function to recover individuals in recovery queue up to the specified
        date. Both the recovery queue population is updated accordingly.

        :param max_date: (date) date up to which to process the recovery queue
        """
        while len(self.__recovery_queue) > 0 and self.__recovery_queue[0][0] <= max_date:
            (date, individual) = self.__recovery_queue.popleft()
            individual.set_disease_state('REC')

    def set_infected(self, individual: Individual, date: datetime):
        """
        Function to infect a specific individual, both the recovery
        queue and the population are updated accordingly.

        :param household: (HouseHold) household to which the individual belongs
        :param individual: (Individual) individual to infect
        :param date: (number) date of infection
        """
        individual.set_disease_state('INF')
        self.__disease_logger.log(individual, date)
        self.__recovery_queue.append((date + dt.timedelta(self.__infection_duration), individual))
