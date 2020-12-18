from abc import ABC
from datetime import datetime
from disease.disease_state import DiseaseStateEnum
from population.individual import Individual
import numpy as np


class DiseaseStateFSMNode(ABC):
    """
    Class to represent a node in the FSM.
    """
    def __init__(self, state: DiseaseStateEnum):
        self.__disease_State = state

    def get_disease_state(self):
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

    def is_end_state(self):
        """
        Function dictates whether the current node is a terminal
        node of the FSM.
        """
        ...


class ExposedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the exposed disease state.
    """
    def __init__(self, state: DiseaseStateEnum, exposed_duration_days: int):
        super().__init__(state)
        self.__exposed_duration_days = exposed_duration_days

    def get_next_state(self, individual: Individual, current_date: datetime):
        # amount_of_days = np.random.normal(4, 1, 1)[0]
        # return DiseaseStateEnum.STATE_INFECTED, self.__infection_duration_days
        #
        # if individual.get_household().size() > 10:
        #     amount_of_days = np.random.normal(5, 1, 1)[0]
        #     return DiseaseStateEnum.STATE_DIED, amount_of_days

        return DiseaseStateEnum.STATE_INFECTED, self.__exposed_duration_days

    def is_end_state(self):
        return False


class InfectedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the infected disease state.
    """
    def __init__(self, state: DiseaseStateEnum, infection_duration_days: int):
        super().__init__(state)
        self.__infection_duration_days = infection_duration_days

    def get_next_state(self, individual: Individual, current_date: datetime):

        # if older_than_x_years and certain_prob:
        #     return DiseaseStateEnum.STATE_DIED, x

        return DiseaseStateEnum.STATE_RECOVERED, self.__infection_duration_days

    def is_end_state(self):
        return False


class RecoveredDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the recovered disease state.
    """
    def __init__(self, state: DiseaseStateEnum, recovered_duration_days: int):
        super().__init__(state)
        self._recovered_duration_days = recovered_duration_days

    def is_end_state(self):
        return False

    def get_next_state(self, individual: Individual, current_date: datetime):
        return DiseaseStateEnum.STATE_DIED, self._recovered_duration_days


class DiedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the died disease state.
    """
    def __init__(self, state: DiseaseStateEnum):
        super().__init__(state)

    def is_end_state(self):
        return True


class DiseaseFSM:
    """
    Class to group the disease states.
    """
    def __init__(self):
        self._nodes = {}
        self.__create_nodes()

    def __create_nodes(self):
        self._nodes[DiseaseStateEnum.STATE_EXPOSED] = ExposedDiseaseStateFSMNode(DiseaseStateEnum.STATE_EXPOSED, 2)
        self._nodes[DiseaseStateEnum.STATE_INFECTED] = InfectedDiseaseStateFSMNode(DiseaseStateEnum.STATE_INFECTED, 2)
        self._nodes[DiseaseStateEnum.STATE_RECOVERED] = RecoveredDiseaseStateFSMNode(DiseaseStateEnum.STATE_RECOVERED, 4)
        self._nodes[DiseaseStateEnum.STATE_DIED] = DiedDiseaseStateFSMNode(DiseaseStateEnum.STATE_DIED)

    def get_start_node(self):
        return self._nodes[DiseaseStateEnum.STATE_EXPOSED]

    def get_node_for_type(self, state: DiseaseStateEnum):
        return self._nodes[state]