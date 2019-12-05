import random
from population.household import HouseHold
from population.individual import Individual


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
        self.remove_from_household(individual)
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

        household = self.__households[hh_id]
        household.add_member(individual)
        individual.set_household(household)

    def remove_from_household(self, individual: Individual):
        """
        Function to remove the given individual from their household.

        :param individual: (individual) the individual to remove
        """
        household = individual.get_household()

        if household is not None:
            self.__households[household.get_id()].remove_member(individual)
            individual.set_household(None)

            if self.__households[household.get_id()].get_size() == 0:
                # TODO Should this happen? What in case if events get out of order?
                del self.__households[household.get_id()]

    def get(self, individual_id):
        """
        Function to retrieve a specific individual from the population.

        :param individual_id: (number) id of the individual
        :return: (Individual) individual
        """
        return self.__population[individual_id]

    def get_household(self, hh_id):
        """
        Function to retrieve a specific household from the population.

        :param hh_id: (number) id of the household to retrieve
        :return: (HouseHold) household
        """
        return self.__households[hh_id]

    def size(self):
        """
        Function to retrieve the size of the population, i.e.,
        the number of individuals.

        :return: (number) number of individuals in the population
        """
        return len(self.__population)
