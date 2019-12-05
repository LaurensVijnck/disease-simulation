from collections import defaultdict
from population.individual import Individual


class HouseHold:
    """
    Class that represents a household.
    """
    def __init__(self, hh_id):
        self.__hh_id = hh_id
        self.__num_children = 0
        self.__num_infected = 0
        self.__num_infected_per_ag = defaultdict(int)
        self.__num_infected_per_ag_per_sex = defaultdict(int)
        self.__members = []

    def get_id(self):
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

    def has_children(self):
        """
        Function to check whether there are children in the household.

        :return: (bool) representing whether the household has children.
        """
        return self.__num_children > 0

    def get_size(self):
        """
        Function to retrieve the size of the household.

        :return: (number) size of the household
        """
        return len(self.__members)

    def get_num_infected(self):
        return self.__num_infected

    def get_num_infected_ag_sex(self, hh_age_group, sex):
        """
        Function to retrieve the number of infected people, per household
        age group and per sex, in the household.

        :param hh_age_group: (number) household age group
        :param sex: (sex) sex of individuals
        :return: (number) number of infected people
        """
        return self.__num_infected_per_ag_per_sex[(hh_age_group, sex)]

    def infected_by_sex_gen(self):
        """
        Function to retrieve the number of infected people, per household
        age group and per sex, in the household.

        :return: (generator) through infected by sex
        """
        for (age_group, sex) in self.__num_infected_per_ag_per_sex:
            yield (age_group, sex, self.__num_infected_per_ag_per_sex[(age_group, sex)])

    def get_num_infected_ag(self, hh_age_group):
        """
        Function to retrieve the number of infected people, per household
        age group in the household.

        :param hh_age_group: (number) household age group
        :return: (number) number of infected people
        """
        return self.__num_infected_per_ag[hh_age_group]

    def compute_metrics(self, curr_date, max_child_age):
        """
        Function to compute the metrics of the household for the given date.
        """
        self.__num_children = 0
        self.__num_infected = 0
        self.__num_infected_per_ag = defaultdict(int)
        self.__num_infected_per_ag_per_sex = defaultdict(int)

        for ind in self.__members:
            if ind.is_infected():
                self.__num_infected += 1
                self.__num_infected_per_ag[ind.get_household_age_group()] += 1
                self.__num_infected_per_ag_per_sex[(ind.get_household_age_group(), ind.get_sex())] += 1

            if ind.is_child(curr_date, max_child_age):
                self.__num_children += 1
