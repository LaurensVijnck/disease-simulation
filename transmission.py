import csv
import random

from household import HouseHold
from individual import Individual
from population.summary import PopulationSummary


class Transmission:
    """
    Class that represents the transmission model.
    """
    def __init__(self, config):
        self.__num_pop_ag = config.get("num_age_groups_pop")
        self.__num_hh_ag = config.get("num_age_groups_household")
        self.__beta_pop = config.get("beta_population")
        self.__beta_household = config.get("beta_household")

        self.__pop_contact = self.__parse_simple_contact_matrix(config.get("pop_matrix", None), self.__beta_pop)
        self.__hh_contact = self.__parse_nested_contact_matrix(config.get("hh_matrix", None))
        self.__hh_contact_children = self.__parse_nested_contact_matrix(config.get("hh_matrix_children", None))

    def occurs(self, individual: Individual, household: HouseHold, summary: PopulationSummary):
        """
        Function that determines whether infection occurs for the specific individual.

        :param individual: (individual) individual to consider
        :param household: (household) household to which the individual belongs
        :param summary: (PopulationSummary) summary of the population
        :return: (boolean) whether disease transmission occurs for the given individual
        """
        p = random.uniform(0, 1)
        p_inf = 1 - self.__compute_hh_infection_escape_prob(individual, household) * self.__compute_pop_infection_escape_prob(individual, summary)
        return p < p_inf

    def __compute_hh_infection_escape_prob(self, individual: Individual, household: HouseHold):
        """
        Function to compute the probability of escaping from infection within the household.

        :param individual: (individual) individual to compute household contacts for
        :param household: (household) household of the individual
        :return: (float) probability of escaping household disease transmission
        """
        contacts = 0
        contact_matrix = self.__hh_contact_children if household.has_children() else self.__hh_contact

        for (age_group, sex, num) in household.infected_by_sex_gen():
            contacts += num * contact_matrix[individual.get_household_age_group()-1][age_group-1][individual.get_sex()-1][sex-1]

        return (1 - self.__beta_household) ** contacts

    def __compute_pop_infection_escape_prob(self, individual: Individual, summary: PopulationSummary):
        """
        Function to escape the probability of escaping from infection by population external to the household.

        :param individual: (individual) to compute external contacts for
        :return: (float) probability of escaping external disease transmission
        """
        escape_prob = 1
        for (age_group, num_infected) in summary.infected_gen():
            beta_pop = self.__pop_contact[individual.get_population_age_group()-1][age_group-1]
            escape_prob *= (1 - beta_pop * summary.get_adjustment(age_group)) ** num_infected

        return escape_prob

    @staticmethod
    def __parse_simple_contact_matrix(matrix_location, beta):
        """
        Function to read a csv-formatted probability matrix in memory, matrix is adjusted with the specified beta.

        :matrix_location matrix: (str) location of the matrix
        :return: (matrix): contact matrix
        """
        with open(matrix_location) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            matrix = []
            for csv_line in csv_reader:
                row = []
                for el in csv_line:
                    row.append(beta * float(el))
                matrix.append(row)

        return matrix

    @staticmethod
    def __print_nested_matrix(dual_matrix, dimension):
        """
        Function to print a nested matrix, i.e., a matrix of matrices.

        :param dual_matrix: (matrix) matrix to print
        :param dimension: (number) dimension of the matrix
        """
        for i in range(dimension):
            for j in range(dimension):
                print(i, j, "\t", end="")
                for k in [0, 1]:
                    for l in [0, 1]:
                        print(dual_matrix[i][j][k][l], end=" : ")
                print()

    @staticmethod
    def __parse_nested_contact_matrix(matrix_location):
        """
        Function to read a csv-formatted, dual probability matrix in memory. Matrix entries
        are formatted 'F:F:M:M' or are solely valued, indicating that the value should be repeated.

        :param matrix_location:
        :return: (matrix): dual contact matrix
        """
        with open(matrix_location) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            matrix = []
            for csv_line in csv_reader:
                row = []
                for el in csv_line:
                    if ':' in el:
                        row.append(Transmission.__construct_nested_cel(el.split(":")))
                    else:
                        row.append(Transmission.__construct_nested_cel([el] * 4))
                matrix.append(row)

        return matrix

    @staticmethod
    def __construct_nested_cel(arr):
        """
        Function to parse a 2-by-2 dual matrix to a native representation.

        :param arr:
        :return: 2 by 2 matrix;
        """
        cell = []
        for i in [0, 1]:
            row = []
            for j in [0, 1]:
                row.append(float(arr[i * 2 + j]))
            cell.append(row)

        return cell

