from abc import ABC
from datetime import datetime
from disease.disease_state import DiseaseStateEnum
from population.individual import Individual
import numpy as np
import math


class DiseaseStateFSMNode(ABC):
    """
    Class to represent a node in the FSM.
    """
    def __init__(self, state: DiseaseStateEnum):
        self.__disease_State = state

    def get_disease_state(self) -> DiseaseStateEnum:
        """
        Function to determine the disease state that is represented by
        the current node in the FSM.
        """
        return self.__disease_State

    def get_next_state(self, individual: Individual, current_date: datetime):
        """
        Function to determine the next disease state and the number of days
        until the next disease state becomes active.

        :param: individual (Individual) for which to fetch the next date
        :param: current_date (datetime) current date according to the simulation
        """
        ...

    def is_end_state(self) -> bool:
        """
        Function dictates whether the current node is a terminal
        node of the FSM.
        """
        ...


class ExposedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the exposed disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # Compute duration of the incubation period
        incubation_duration = max(2, np.random.lognormal(mean=1.43, sigma=0.66, size=None)) # Can we seed numpy randoms?

        # Compute duration of the pre-symptomatic period
        pre_symptomatic_duration = min(incubation_duration, np.random.choice(np.arange(1, 7), p=[0.45, 0.31, 0.16, 0.06, 0.015, 0.005]))
        # pre_symptomatic_duration = min(incubation_duration, np.random.gamma(shape=20.52, scale=1.59, size=None))

        # Commute exposed duration
        exposed_period = max(1, round(incubation_duration - pre_symptomatic_duration))

        # Compute duration of pre-symptomatic period
        individual.pre_symptomatic_duration = math.ceil(pre_symptomatic_duration) # FUTURE: Variables specific to the disease model should be stored elsewhere

        # Compute duration of (a)symptomatic period
        remaining_time_infected = round(max(0, np.random.normal(loc=6, scale=1, size=None) - pre_symptomatic_duration))
        individual.remaining_time_infected = remaining_time_infected

        return DiseaseStateEnum.STATE_INFECTED, exposed_period

    def is_end_state(self) -> bool:
        return False


class InfectedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the infected (pre-symptomatic) disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # If remaining time of infectious period is zero (pre-symptomatic period equals infectious period) go directly to 'recovered'
        if individual.remaining_time_infected == 0:
            return DiseaseStateEnum.STATE_RECOVERED, individual.pre_symptomatic_duration

        # By means of an example; we can perform any kind of computation to decide upon this.
        # SM 13/1/2021: The probability to be symptomatic follows this age distribution:
        # age-groups=[0-19, 20-29, 30-39, 40-49, 50-59, 60+]
        # probability= [0.07, 0.17, 0.42, 0.54, 0.83, 0.94]
        # SM 26/1/2021: For now I have just used an 'If' function but I guess you'll have a more efficient approach

        #becomes_symptomatic = random.choice([True, False])

        if individual.get_age(current_date) < 20:
            becomes_symptomatic = np.random.choice([True, False], p=[0.07, (1-0.07)])
        elif 20 <= individual.get_age(current_date) <= 29:
            becomes_symptomatic = np.random.choice([True, False], p=[0.17, (1-0.17)])
        elif 30 <= individual.get_age(current_date) <= 39:
            becomes_symptomatic = np.random.choice([True, False], p=[0.42, (1-0.42)])
        elif 40 <= individual.get_age(current_date) <= 49:
            becomes_symptomatic = np.random.choice([True, False], p=[0.54, (1-0.54)])
        elif 50 <= individual.get_age(current_date) <= 59:
            becomes_symptomatic = np.random.choice([True, False], p=[0.83, (1-0.83)])
        else:
            becomes_symptomatic = np.random.choice([True, False], p=[0.94, (1-0.94)])

        if becomes_symptomatic:
            return DiseaseStateEnum.STATE_SYMPTOMATIC, individual.pre_symptomatic_duration

        return DiseaseStateEnum.STATE_ASYMPTOMATIC, individual.pre_symptomatic_duration

    def is_end_state(self) -> bool:
        return False


class AsymptomaticDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the asymptomatic disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # Determine number of days, be careful with negative state durations.
        # FUTURE: Extract logic below into .csv provided matrices - LVI
        asymptomatic_duration = individual.remaining_time_infected #round(max(0, np.random.normal(loc=6, scale=1, size=None) - individual.pre_symptomatic_duration))

        if individual.get_age(current_date) < 25 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.0, 1])
        if individual.get_age(current_date) < 25 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.000011, (1-0.000011)])
        if 25 <= individual.get_age(current_date) <= 44 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.00021, (1-0.00021)])
        if 25 <= individual.get_age(current_date) <= 44 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.00014, (1-0.00014)])
        if 45 <= individual.get_age(current_date) <= 64 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.0029, (1-0.0029)])
        if 45 <= individual.get_age(current_date) <= 64 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.0014, (1-0.0014)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.017, (1-0.017)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0074, (1-0.0074)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.653, (1-0.653)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.563, (1-0.563)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0367, (1-0.0367)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0173, (1-0.0173)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.467, (1-0.467)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.228, (1-0.228)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0434, (1-0.0434)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0145, (1-0.0145)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.5995, (1-0.5995)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.325, (1-0.325)])

        if individual_dies:
            days_until_demise = np.random.lognormal(mean=2.4531093, sigma=0.8371099, size=None)

            if days_until_demise > asymptomatic_duration:

                # FUTURE: Move hospitalized duration elsewhere.
                individual.hospitalized_duration = max(1, round(days_until_demise - asymptomatic_duration))
                return DiseaseStateEnum.STATE_HOSPITALIZED, asymptomatic_duration

            return DiseaseStateEnum.STATE_DIED, days_until_demise

        return DiseaseStateEnum.STATE_RECOVERED, asymptomatic_duration

    def is_end_state(self) -> bool:
        return False


class SymptomaticDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the symptomatic disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # Determine number of days, be careful with negative state durations.
        symptomatic_duration = individual.remaining_time_infected #round(max(0, np.random.normal(loc=6, scale=1, size=None) - individual.pre_symptomatic_duration))

        # FUTURE: Extract logic below into .csv provided matrices
        if individual.get_age(current_date) < 25 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.0, 1])
        if individual.get_age(current_date) < 25 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.000011, (1-0.000011)])
        if 25 <= individual.get_age(current_date) <= 44 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.00021, (1-0.00021)])
        if 25 <= individual.get_age(current_date) <= 44 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.00014, (1-0.00014)])
        if 45 <= individual.get_age(current_date) <= 64 and individual.get_sex() is False:
            individual_dies = np.random.choice([True, False], p=[0.0029, (1-0.0029)])
        if 45 <= individual.get_age(current_date) <= 64 and individual.get_sex():
            individual_dies = np.random.choice([True, False], p=[0.0014, (1-0.0014)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.017, (1-0.017)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0074, (1-0.0074)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.653, (1-0.653)])
        if 65 <= individual.get_age(current_date) <= 74 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.563, (1-0.563)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0367, (1-0.0367)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0173, (1-0.0173)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.467, (1-0.467)])
        if 75 <= individual.get_age(current_date) <= 84 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.228, (1-0.228)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() is False and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0434, (1-0.0434)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() and individual.get_nursing_home() is False:
            individual_dies = np.random.choice([True, False], p=[0.0145, (1-0.0145)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() is False and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.5995, (1-0.5995)])
        if individual.get_age(current_date) >= 85 and individual.get_sex() and individual.get_nursing_home():
            individual_dies = np.random.choice([True, False], p=[0.325, (1-0.325)])

        if individual_dies:
            days_until_demise = np.random.lognormal(mean=2.4531093, sigma=0.8371099, size=None)

            if days_until_demise > symptomatic_duration:

                # FUTURE: Move hospitalized duration elsewhere.
                individual.hospitalized_duration = max(1, round(days_until_demise - symptomatic_duration))
                return DiseaseStateEnum.STATE_HOSPITALIZED, symptomatic_duration

            return DiseaseStateEnum.STATE_DIED, days_until_demise

        return DiseaseStateEnum.STATE_RECOVERED, symptomatic_duration

    def is_end_state(self) -> bool:
        return False


class HospitalizedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the hospitalized disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # Duration to remain hospitalized is established in the previous node
        # return DiseaseStateEnum.STATE_DIED, individual.hospitalized_duration
        return DiseaseStateEnum.STATE_DIED, individual.hospitalized_duration

    def is_end_state(self) -> bool:
        return False


class RecoveredDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the recovered disease state.
    """
    def is_end_state(self):
        return True


class DiedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the died disease state.

    TODO: Currently people that died are still part of the population. Do we need to exclude these? - LVI
    """
    def is_end_state(self) -> bool:
        return True


class DiseaseFSM:
    """
    Class to group the disease states.
    """
    def __init__(self):
        self._nodes = {}
        self._create_nodes()

        # TODO Seed the generator numpy.random.seed - LVI
        # TODO Disease deque should be managed at _this_ level - LVI

    def _create_nodes(self):
        """
        Function to register the disease states in the state machine.
        """

        # FUTURE: The following nodes can be generated according to a configuration.
        self._nodes[DiseaseStateEnum.STATE_EXPOSED] = ExposedDiseaseStateFSMNode(DiseaseStateEnum.STATE_EXPOSED)
        self._nodes[DiseaseStateEnum.STATE_INFECTED] = InfectedDiseaseStateFSMNode(DiseaseStateEnum.STATE_INFECTED)
        self._nodes[DiseaseStateEnum.STATE_ASYMPTOMATIC] = AsymptomaticDiseaseStateFSMNode(DiseaseStateEnum.STATE_ASYMPTOMATIC)
        self._nodes[DiseaseStateEnum.STATE_SYMPTOMATIC] = SymptomaticDiseaseStateFSMNode(DiseaseStateEnum.STATE_SYMPTOMATIC)
        self._nodes[DiseaseStateEnum.STATE_HOSPITALIZED] = HospitalizedDiseaseStateFSMNode(DiseaseStateEnum.STATE_HOSPITALIZED)
        self._nodes[DiseaseStateEnum.STATE_RECOVERED] = RecoveredDiseaseStateFSMNode(DiseaseStateEnum.STATE_RECOVERED)
        self._nodes[DiseaseStateEnum.STATE_DIED] = DiedDiseaseStateFSMNode(DiseaseStateEnum.STATE_DIED)

    def get_start_node(self) -> DiseaseStateFSMNode:
        """
        Function to extract the start node form the state machine.
        """
        return self._nodes[DiseaseStateEnum.STATE_EXPOSED]

    def get_node_for_type(self, state: DiseaseStateEnum) -> DiseaseStateFSMNode:
        """
        Function to retrieve the specified node from the state machine.
        """
        return self._nodes[state]