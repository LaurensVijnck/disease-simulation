import datetime as dt
from datetime import datetime
from collections import deque
from disease.logger import DiseaseLogger
from population.individual import Individual
from population.population import Population
from population.summary import PopulationSummary
from reporter import Reporter
from disease.transmission import Transmission


class Disease:
    def __init__(self, config, global_config, population: Population, reporter: Reporter):
        self.__population = population
        self.__reporter = reporter
        self.__infection_duration = config.get("infection_duration", 3)

        # Create disease logger
        logger_config = config.get("logger")
        self.__disease_logger = DiseaseLogger(logger_config, global_config)

        # Initialize Transmission model
        transmission_config = config.get("transmission")
        self.__transmission = Transmission(transmission_config, global_config)

        # Recovery queue
        self.__recovery_queue = deque()

    # FUTURE: Parallelize this loop.
    def apply_disease_model(self, curr_date: datetime):
        """
        Function to apply the disease model on the population as-is. The population
        and recovery queue is updated accordingly.
        """
        summary = PopulationSummary(self.__population, self.__population.get_base_distribution())
        self.__reporter.set_population_summary(summary)
        self.__disease_logger.log_summary(curr_date, summary)
        self.process_recovery_queue(curr_date)
        for household in self.__population.household_gen():
            household.compute_metrics(curr_date, self.__population.get_age_child_limit())
            for individual in household.member_gen():

                if individual.is_infected() or individual.is_recovered():
                    continue

                transmission_occurs, hh_trans, pop_trans = self.__transmission.occurs(individual, household, summary)
                if transmission_occurs:
                    self.set_infected(individual, curr_date, False, hh_trans, pop_trans)

    def get_num_infected(self):
        """
        Function to retrieve the number of infected individuals

        :return: (num) number of infected individuals
        """
        return len(self.__recovery_queue)

    def process_recovery_queue(self, max_date: datetime):
        """
        Function to recover individuals in recovery queue up to the specified
        date. Both the recovery queue population is updated accordingly.

        :param max_date: (date) date up to which to process the recovery queue
        """
        while len(self.__recovery_queue) > 0 and self.__recovery_queue[0][0] <= max_date:
            (date, individual) = self.__recovery_queue.popleft()
            individual.set_disease_state('REC')

    def set_infected(self, individual: Individual, date: datetime, influx=False, hh_trans_escp=0, pop_trans_escp=0):
        """
        Function to infect a specific individual, both the recovery
        queue and the population are updated accordingly.

        :param pop_trans_escp: (number) population transmission escape probability
        :param hh_trans_escp: (number) household transmission escape probability
        :param individual: (Individual) individual to infect
        :param date: (number) date of infection
        :param influx: (boolean) whether infection occurred due to influx
        """
        individual.set_disease_state('INF')
        self.__disease_logger.log_infection(individual, date, influx, hh_trans_escp, pop_trans_escp)
        self.__recovery_queue.append((date + dt.timedelta(self.__infection_duration), individual))
