import datetime as dt
from datetime import datetime
from collections import deque
from individual import Individual
from population.population import Population
from population.summary import PopulationSummary
from reporter import Reporter
from transmission import Transmission


class Disease:
    def __init__(self, config, population: Population, reporter: Reporter):
        self.population = population
        self.reporter = reporter
        self.infection_duration = config.get("infection_duration", 3)

        # Compute initial summary
        self.initial_summary = PopulationSummary(population)

        # Initialize Transmission model
        transmission_config = config.get("transmission")
        self.transmission = Transmission(transmission_config)

        # Recovery queue
        self.recovery_queue = deque()

    # FUTURE: Parallelize this loop.
    def apply_disease_model(self, curr_date: datetime):
        """
        Function to apply the disease model on the population as-is. The population
        and recovery queue is updated accordingly.
        """
        summary = PopulationSummary(self.population, self.initial_summary)
        num_infected = 0
        self.reporter.set_population_summary(summary)
        self.process_recovery_queue(curr_date)
        for household in self.population.household_gen():
            household.compute_metrics(curr_date)
            for individual in household.member_gen():

                if individual.is_infected() or individual.is_recovered():
                    continue

                if self.transmission.occurs(individual, household, summary):
                    self.set_infected(individual, curr_date)
                    num_infected += 1

        return len(self.recovery_queue) > 0

    def process_recovery_queue(self, max_date: datetime):
        """
        Function to recover individuals in recovery queue up to the specified
        date. Both the recovery queue population is updated accordingly.

        :param max_date: (date) date up to which to process the recovery queue
        """
        num_cured = 0
        while len(self.recovery_queue) > 0 and self.recovery_queue[0][0] <= max_date:
            (date, individual) = self.recovery_queue.popleft()
            individual.set_disease_state('REC')
            num_cured += 1

    def set_infected(self, individual: Individual, date: datetime):
        """
        Function to infect a specific individual, both the recovery
        queue and the population are updated accordingly.

        :param individual: (number) individual to infect
        :param date: (number) date of infection
        """
        individual.set_disease_state('INF')
        self.recovery_queue.append((date + dt.timedelta(self.infection_duration), individual))
