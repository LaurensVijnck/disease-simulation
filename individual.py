from datetime import datetime
from dateutil.relativedelta import relativedelta


class Individual:
    """
    Class that represents an individual in the population.
    """
    def __init__(self, ID, birth_date: datetime, sex, disease_state, population_age_group, household_age_group, HH_ID, HH_position):
        self.__ID = ID
        self.__birth_date = birth_date
        self.__disease_state = disease_state
        self.__sex = sex
        self.__population_age_group = population_age_group
        self.__household_age_group = household_age_group
        self.__HH_ID = HH_ID
        self.__HH_position = HH_position

    def get_disease_sate(self):
        return self.__disease_state

    def set_disease_state(self, disease_state):
        self.__disease_state = disease_state

    def get_id(self):
        return self.__ID

    def get_birth_date(self):
        return self.__birth_date

    def get_sex(self):
        return self.__sex

    def get_population_age_group(self):
        return self.__population_age_group

    def get_household_age_group(self):
        return self.__household_age_group

    def set_population_age_group(self, pop_age_group):
        self.__population_age_group = pop_age_group

    def set_household_age_group(self, hh_age_group):
        self.__household_age_group = hh_age_group

    def set_hh_position(self, hh_position):
        self.__HH_position = hh_position

    def get_hh_id(self):
        return self.__HH_ID

    def set_hh_id(self, hh_id):
        self.__HH_ID = hh_id

    def get_hh_position(self):
        return self.__HH_position

    def is_infected(self):
        return self.__disease_state == 'INF'

    def is_recovered(self):
        return self.__disease_state == 'REC'

    def is_susceptible(self):
        return self.__disease_state == "SUS"

    def is_child(self, current_date: datetime):
        return relativedelta(current_date, self.__birth_date).years < 18

    @staticmethod
    def create(event, date_format):
        """
        Function to create an individual from a dictionary.

        :param event: (dict) event to parse to an individual
        :param date_format: (string) date format to use when parsing dates
        :return: (individual) as specified in the events
        """
        id = int(event["ID"])
        hh_id = int(event["HH_ID"])
        sex = 1 if event["sex"] != "M" else 2
        return Individual(id, datetime.strptime(event["birth_date"], date_format), sex, 'SUS', int(event["age_group_pop"]), int(event["age_group_hh"]), hh_id, event["hh_position"])
