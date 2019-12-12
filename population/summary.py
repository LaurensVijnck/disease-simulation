from collections import defaultdict
from population.population import Population


class PopulationSummary:
    def __init__(self, population: Population, initial_summary):
        self._initial_summary = initial_summary
        self._population = population
        self._num_susceptible = 0
        self._num_infected = 0
        self._num_recovered = 0
        self._num_susceptible_per_age_group = defaultdict(int)
        self._num_infected_per_age_group = defaultdict(int)
        self._num_recovered_per_age_group = defaultdict(int)
        self._total_per_age_group = defaultdict(int)
        self._prepare()

    def infected_gen(self):
        for age_group in self._num_infected_per_age_group:
            yield (age_group, self._num_infected_per_age_group[age_group])

    def get_num_susceptible(self, age_group):
        return self._num_susceptible_per_age_group[age_group]

    def get_total_susceptible(self):
        return self._num_susceptible

    def get_num_infected(self, age_group):
        return self._num_infected_per_age_group[age_group]

    def get_total_infected(self):
        return self._num_infected

    def get_num_recovered(self, age_group):
        return self._num_recovered_per_age_group[age_group]

    def get_total_recovered(self):
        return self._num_recovered

    def get_total(self, age_group):
        return self._total_per_age_group[age_group]

    def get_adjustment(self, age_group):
        return self._initial_summary[age_group-1] / max(self._total_per_age_group[age_group], 1)

    def _prepare(self):
        for individual in self._population.individual_gen():
            self._total_per_age_group[individual.get_population_age_group()] += 1

            if individual.is_susceptible():
                self._num_susceptible += 1
                self._num_susceptible_per_age_group[individual.get_population_age_group()] += 1

            if individual.is_infected():
                self._num_infected += 1
                self._num_infected_per_age_group[individual.get_population_age_group()] += 1

            if individual.is_recovered():
                self._num_recovered += 1
                self._num_recovered_per_age_group[individual.get_population_age_group()] += 1