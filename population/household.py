from collections import defaultdict
from population.individual import Individual
from disease.disease_state import DiseaseStateEnum


class HouseHold:
    """
    Class that represents a household.
    """
    def __init__(self, hh_id: int):
        self.__is_nursing_home = None # TODO Extract from event log
        self.__hh_id = hh_id
        self.__num_children = 0

        self._num_per_disease_state = defaultdict(int)
        self._num_per_disease_state_per_age_group = defaultdict(lambda: defaultdict(int))
        self._num_per_disease_state_per_age_group_per_sex = defaultdict(lambda: defaultdict(int))
        self.__members = []

    def get_id(self) -> int:
        """
        Function to retrieve the identifier of the household.

        :return: (number) identifier of the household
        """
        return self.__hh_id

    def member_gen(self):
        """
        Function to produce a generator over the members of the household.

        :return: (generator) individual iterator
        """
        for member in self.__members:
            yield member

    def add_member(self, individual: Individual):
        """
        Function to add a member to the household.

        :param individual: (Individual) individual to add to the household
        """
        self.__members.append(individual)

    def remove_member(self, individual: Individual):
        """
       Function to remove a member from the household.

       :param individual: (Individual) individual to add to the household
       """
        self.__members.remove(individual)

    def has_children(self) -> bool:
        """
        Function to check whether there are children in the household.

        :return: (bool) representing whether the household has children.
        """
        return self.__num_children > 0

    def get_size(self) -> int:
        """
        Function to retrieve the size of the household.

        :return: (number) size of the household
        """
        return len(self.__members)

    def get_total_for_disease_state(self, disease_state: DiseaseStateEnum) -> int:
        """
        Function to retrieve the number of people in given state in the household.

        :return: (number) number of infected people
        """
        return self._num_per_disease_state[disease_state]

    def get_num_for_disease_state(self, disease_state: DiseaseStateEnum, age_group: int) -> int:
        """
        Function to retrieve the number of people in given state, for the given age group, in the household.

        :return: (number) number of infected people
        """
        return self._num_per_disease_state_per_age_group[disease_state][age_group]

    def get_num_for_disease_state_by_ag_by_sex(self, disease_state: DiseaseStateEnum, hh_age_group: int, sex: bool):
        """
        Function to retrieve the number of people in given state, for the given age group and sex, in the household.

        :return: (number) number of infected people
        """
        return self._num_per_disease_state_per_age_group_per_sex[disease_state][(hh_age_group, sex)]

    def get_num_for_disease_state_gen(self, disease_state: DiseaseStateEnum):
        """
        Function to retrieve the number of people in the givne state, per household
        age group and per sex, in the household.

        :return: (generator) through infected by sex
        """
        for (age_group, sex) in self._num_per_disease_state_per_age_group_per_sex[disease_state]:
            yield (age_group, sex, self._num_per_disease_state_per_age_group_per_sex[disease_state][(age_group, sex)])


    # def get_infected_age_distribution(self):
    #     """
    #     Function to retrieve an age distribution of infected
    #     individuals in the household.
    #
    #     :return: (defaultdict) age distribution
    #     """
    #     return self.__age_distribution_inf

    def compute_metrics(self, curr_date, max_child_age):
        """
        Function to compute the metrics of the household for the given date.
        """
        self._num_per_disease_state = defaultdict(int)
        self._num_per_disease_state_per_age_group = defaultdict(lambda: defaultdict(int))
        self._num_per_disease_state_per_age_group_per_sex = defaultdict(lambda: defaultdict(int))

        for individual in self.__members:

            self._num_per_disease_state[individual.get_disease_sate()] += 1
            self._num_per_disease_state_per_age_group[individual.get_disease_sate()][individual.get_household_age_group()] += 1
            self._num_per_disease_state_per_age_group_per_sex[individual.get_disease_sate()][(individual.get_household_age_group(), individual.get_sex())] += 1

            if individual.is_child(curr_date, max_child_age):
                self.__num_children += 1
