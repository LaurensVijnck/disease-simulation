from datetime import datetime
from dateutil.relativedelta import relativedelta
from disease.disease_state import DiseaseStateEnum


class Individual:
    """
    Class that represents an individual in the population.
    """
    def __init__(self, ID: int, birth_date: datetime, sex: bool, disease_state: DiseaseStateEnum, population_age_group: int, household_age_group: int, HH_position: str):
        self.__ID = ID
        self.__birth_date = birth_date
        self.__disease_state = disease_state
        self.__sex = sex
        self.__population_age_group = population_age_group
        self.__household_age_group = household_age_group
        self.__household = None
        self.__HH_position = HH_position

        # Parameters specific to the disease model, ideally they should be moved elsewhere.
        self.pre_symptomatic_duration = None

    def get_disease_sate(self) -> DiseaseStateEnum:
        return self.__disease_state

    def set_disease_state(self, disease_state):
        self.__disease_state = disease_state

    def get_id(self) -> int:
        return self.__ID

    def get_birth_date(self) -> datetime:
        return self.__birth_date

    def get_sex(self) -> bool:
        return self.__sex

    def get_population_age_group(self) -> int:
        return self.__population_age_group

    def get_household_age_group(self) -> int:
        return self.__household_age_group

    def set_population_age_group(self, pop_age_group):
        self.__population_age_group = pop_age_group

    def set_household_age_group(self, hh_age_group):
        self.__household_age_group = hh_age_group

    def set_hh_position(self, hh_position):
        self.__HH_position = hh_position

    def get_household(self):
        return self.__household

    def set_household(self, household):
        self.__household = household

    def get_hh_position(self) -> str:
        return self.__HH_position

    def get_age(self, current_date: datetime) -> int:
        return relativedelta(current_date, self.__birth_date).years

    def is_child(self, current_date: datetime, max_child_age) -> bool:
        return relativedelta(current_date, self.__birth_date).years < max_child_age

    @staticmethod
    def create(event, date_format):
        """
        Function to create an individual from a dictionary.

        :param event: (dict) event to parse to an individual
        :param date_format: (string) date format to use when parsing dates
        :return: (individual) as specified in the events
        """
        id = int(event["ID"])
        sex = True if event["sex"] != "M" else False
        return Individual(id, datetime.strptime(event["birth_date"], date_format), sex, DiseaseStateEnum.STATE_SUSCEPTIBLE, int(event["age_group_pop"]), int(event["age_group_hh"]), event["hh_position"])
