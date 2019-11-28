import random
from household import HouseHold
from individual import Individual


class Population:
    def __init__(self):
        self.__population = dict()
        self.__households = dict()

    # TODO: Seed this?
    def random_gen(self, amount):
        """
        Generator to retrieve a number of random individuals in the population.

        :param amount: (number) number of individuals to sample
        :return: (generator) random individuals generator
        """
        individuals = random.sample(list(self.__population.values()), amount)
        for ind in individuals:
            yield ind

    def individual_gen(self):
        """
        Generator to iterate individuals in the population.

        :return: (generator) individuals in the population
        """
        for individual in self.__population:
            yield self.__population[individual]

    def household_gen(self):
        """
        Generator to iterate the households in the population.

        :return: (generator) households in the population
        """
        for household in self.__households:
            yield self.__households[household]

    def delete(self, individual: Individual):
        """
        Function to delete an individual from the population, the
        household index is updated accordingly.

        :param individual: (individual) the individual to remove
        """
        self.remove_from_household(individual, individual.get_hh_id())
        del self.__population[individual.get_id()]

    def add(self, individual: Individual, hh_id):
        """
        Function to add an individual to the population, the household index
        is updated accordingly.

        :param individual: (individual) to add to the population
        :param hh_id: (number) household to which the individual belongs
        """
        self.__population[individual.get_id()] = individual
        self.add_to_household(individual, hh_id)

    def add_to_household(self, individual: Individual, hh_id):
        """
        Function to add the given individual to the specified hh_id

        :param individual: (individual) the individual to add
        :param hh_id: (number) id of the household to add the individual to
        """
        if hh_id not in self.__households:
            self.__households[hh_id] = HouseHold(hh_id)
        self.__households[hh_id].add_member(individual)

    def remove_from_household(self, individual: Individual, hh_id):
        """
        Function to remove the given individual from the specified hh_id

        :param individual: (individual) the individual to remove
        :param hh_id: (number) id of the household to remove the individual from
        """
        self.__households[hh_id].remove_member(individual)

        if self.__households[hh_id].get_size() == 0:
            del self.__households[hh_id]

    def get(self, individual_id):
        """
        Function to retrieve a specific individual from the population.

        :param individual_id: (number) id of the individual
        :return: (Individual) individual
        """
        return self.__population[individual_id]

    def size(self):
        """
        Function to retrieve the size of the population, i.e.,
        the number of individuals.

        :return: (number) number of individuals in the population
        """
        return len(self.__population)
