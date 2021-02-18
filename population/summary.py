from collections import defaultdict
from population.population import Population
from disease.disease_state import DiseaseStateEnum


class PopulationSummary:
    """
    Class that summarize some of the most prevalent metrics of the population, class
    is leveraged as a cache to avoid repeated computation.
    """
    def __init__(self, population: Population, initial_summary):
        self._initial_summary = initial_summary
        self._population = population
        self._num_susceptible = 0

        self._num_per_disease_state = defaultdict(int)
        self._num_per_disease_state_per_age_group = defaultdict(lambda: defaultdict(int))
        self._total_per_age_group = defaultdict(int)
        self._prepare()

    def num_for_disease_state_gen(self, disease_state: DiseaseStateEnum):
        for age_group in self._num_per_disease_state_per_age_group[disease_state]:
            yield (age_group, self._num_per_disease_state_per_age_group[disease_state][age_group])

    def get_num_for_disease_state_per_ag(self, disease_state: DiseaseStateEnum, age_group: int) -> int:
        return self._num_per_disease_state_per_age_group[disease_state][age_group]

    def get_total_for_disease_state(self, disease_state: DiseaseStateEnum) -> int:
        return self._num_per_disease_state[disease_state]

    def get_total(self, age_group):
        return self._total_per_age_group[age_group]

    def get_adjustment(self, age_group):
        return self._initial_summary[age_group-1] / max(self._total_per_age_group[age_group], 1)

    def _prepare(self):
        for individual in self._population.individual_gen():

            self._total_per_age_group[individual.get_population_age_group()] += 1

            # Increment number with disease state
            self._num_per_disease_state[individual.get_disease_sate()] += 1

            # Increment number with disease state, grouped by age group
            self._num_per_disease_state_per_age_group[individual.get_disease_sate()][individual.get_population_age_group()] += 1