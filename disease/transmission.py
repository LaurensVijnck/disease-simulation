import csv
import random
import math

from datetime import datetime
from population.household import HouseHold
from population.individual import Individual
from population.summary import PopulationSummary
from disease.disease_state import DiseaseStateEnum


def _pad_centered(target_str, dest_len):
    len_diff = max(0, dest_len - len(target_str))
    return " " * math.ceil(len_diff/2) + target_str + " " * math.floor(len_diff/2)


class Transmission:
    """
    Class that represents the transmission model.
    """
    def __init__(self, config, global_config):
        random.seed(global_config["seed"])
        self.__num_pop_ag = global_config.get("num_age_groups_pop")
        self.__num_hh_ag = global_config.get("num_age_groups_hh")

        # FUTURE: Remove following parameters, as these are now specified for each disease state;
        #self.__beta_pop = config.get("beta_population")
        # self.__beta_household = config.get("beta_household")

        # TODO: Allow supplying the following probabilities via config
        self.__beta_pop = {
            DiseaseStateEnum.STATE_INFECTED: 5,
            DiseaseStateEnum.STATE_SYMPTOMATIC: 10,
            DiseaseStateEnum.STATE_ASYMPTOMATIC: 20,
        }

        # TODO: Allow supplying the following probabilities via config
        self.__beta_household = {
            DiseaseStateEnum.STATE_INFECTED: 10,
            DiseaseStateEnum.STATE_SYMPTOMATIC: 20,
            DiseaseStateEnum.STATE_ASYMPTOMATIC: 30,
        }

        self.__pop_contact = self.__parse_simple_contact_matrix(config.get("pop_matrix", None))
        self.__hh_contact = self.__parse_nested_contact_matrix(config.get("hh_matrix", None))
        self.__hh_contact_children = self.__parse_nested_contact_matrix(config.get("hh_matrix_children", None))

        #print("\nHousehold with children: \n")
        self.__print_nested_matrix(self.__hh_contact_children, self.__num_hh_ag)

        #print("\nHousehold without children: \n")
        self.__print_nested_matrix(self.__hh_contact, self.__num_hh_ag)

    def occurs(self, individual: Individual, household: HouseHold, summary: PopulationSummary, date: datetime):
        """
        Function that determines whether infection occurs for the specific individual.

        :param individual: (individual) individual to consider
        :param household: (household) household to which the individual belongs
        :param summary: (PopulationSummary) summary of the population
        :return: (boolean) whether disease transmission occurs for the given individual
        """
        p = random.uniform(0, 1)
        hh_trans = self.__compute_hh_infection_escape_prob(individual, household)
        pop_trans = self.__compute_pop_infection_escape_prob(individual, summary)

        # TODO Make this following more flexible by allowing it to be injected via the config
        susceptibility_adjustment = 0.5 if individual.is_child(date, summary._population.get_age_child_limit()) else 1

        p_inf = susceptibility_adjustment * (1 - hh_trans * pop_trans)
        return p < p_inf, hh_trans, pop_trans

    def __compute_hh_infection_escape_prob(self, individual: Individual, household: HouseHold):
        """
        Function to compute the probability of escaping from infection within the household.

        :param individual: (individual) individual to compute household contacts for
        :param household: (household) household of the individual
        :return: (float) probability of escaping household disease transmission
        """
        inf_contacts = 0
        asymp_contacts = 0
        symp_contacts = 0
        contact_matrix = self.__hh_contact_children if household.has_children() else self.__hh_contact

        # FUTURE: This may need some improvement code-wise.
        for (age_group, sex, num) in household.get_num_for_disease_state_gen(DiseaseStateEnum.STATE_INFECTED):
            inf_contacts += num * contact_matrix[individual.get_household_age_group()-1][age_group-1][individual.get_sex()-1][sex-1]

        for (age_group, sex, num) in household.get_num_for_disease_state_gen(DiseaseStateEnum.STATE_ASYMPTOMATIC):
            asymp_contacts += num * contact_matrix[individual.get_household_age_group()-1][age_group-1][individual.get_sex()-1][sex-1]

        for (age_group, sex, num) in household.get_num_for_disease_state_gen(DiseaseStateEnum.STATE_SYMPTOMATIC):
            symp_contacts += num * contact_matrix[individual.get_household_age_group()-1][age_group-1][individual.get_sex()-1][sex-1]

        return (1 - self.__beta_household[DiseaseStateEnum.STATE_INFECTED]) ** inf_contacts * (1 - self.__beta_household[DiseaseStateEnum.STATE_ASYMPTOMATIC]) ** asymp_contacts * (1 - self.__beta_household[DiseaseStateEnum.STATE_SYMPTOMATIC]) ** symp_contacts

    def __compute_pop_infection_escape_prob(self, individual: Individual, summary: PopulationSummary):
        """
        Function to escape the probability of escaping from infection by population external to the household.

        :param individual: (individual) to compute external contacts for
        :return: (float) probability of escaping external disease transmission
        """
        escape_prob = 1

        for (age_group, num) in summary.num_for_disease_state_gen(DiseaseStateEnum.STATE_INFECTED):
            beta_pop = self.__pop_contact[individual.get_population_age_group()-1][age_group-1] * self.__beta_pop[DiseaseStateEnum.STATE_INFECTED]
            escape_prob *= (1 - beta_pop * summary.get_adjustment(age_group)) ** num

        for (age_group, num) in summary.num_for_disease_state_gen(DiseaseStateEnum.STATE_ASYMPTOMATIC):
            beta_pop = self.__pop_contact[individual.get_population_age_group()-1][age_group-1] * self.__beta_pop[DiseaseStateEnum.STATE_ASYMPTOMATIC]
            escape_prob *= (1 - beta_pop * summary.get_adjustment(age_group)) ** num

        for (age_group, num) in summary.num_for_disease_state_gen(DiseaseStateEnum.STATE_SYMPTOMATIC):
            beta_pop = self.__pop_contact[individual.get_population_age_group()-1][age_group-1] * self.__beta_pop[DiseaseStateEnum.STATE_SYMPTOMATIC]
            escape_prob *= (1 - beta_pop * summary.get_adjustment(age_group)) ** num

        return escape_prob

    @staticmethod
    def __parse_simple_contact_matrix(matrix_location):
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
                    row.append(float(el))
                matrix.append(row)

        return matrix

    @staticmethod
    def __print_nested_matrix(dual_matrix, dimension):
        """
        Function to print a nested matrix, i.e., a matrix of matrices.

        :param dual_matrix: (matrix) matrix to print
        :param dimension: (number) dimension of the matrix
        """
        print("  ", end=" ")
        for i in range(dimension):
            for sex in ['F', 'M']:
                print(_pad_centered(sex, 7), end=" ")
        print()
        print("  +" + ("-" * 15 + "+") * dimension)

        for i in range(dimension):
            for j, sex in enumerate(['F', 'M']):
                print(sex, end=" | ")
                for k in range(dimension):
                    for l in [0, 1]:
                        print("{0:.4f}".format(dual_matrix[i][k][j][l]), end=" ")
                    print("| ", end="")
                print()
            print("  +" + ("-" * 15 + "+") * dimension)

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


