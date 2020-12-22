from abc import ABC
from datetime import datetime
from disease.disease_state import DiseaseStateEnum
from population.individual import Individual
import numpy as np
import math
import random


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
        pre_symptomatic_duration = min(incubation_duration, np.random.gamma(shape=20.52, scale=1.59, size=None))

        # Commute exposed duration
        exposed_period = math.floor(incubation_duration - pre_symptomatic_duration)

        individual.pre_symptomatic_duration = math.ceil(pre_symptomatic_duration) # FUTURE: Variables specific to the disease model should be stored elsewhere

        return DiseaseStateEnum.STATE_INFECTED, exposed_period

    def is_end_state(self) -> bool:
        return False


class InfectedDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the infected (pre-symptomatic) disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # By means of an example; we can perform any kind of computation to decide upon this.
        becomes_symptomatic = random.choice([True, False])

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
        asymptomatic_duration = math.floor(max(0, np.random.normal(loc=6, scale=1, size=None) - individual.pre_symptomatic_duration))

        return DiseaseStateEnum.STATE_RECOVERED, asymptomatic_duration

    def is_end_state(self) -> bool:
        return False


class SymptomaticDiseaseStateFSMNode(DiseaseStateFSMNode):
    """
    FSM Node to representing the symptomatic disease state.
    """
    def get_next_state(self, individual: Individual, current_date: datetime) -> (DiseaseStateFSMNode, int):

        # Determine number of days, be careful with negative state durations.
        symptomatic_duration = math.floor(max(0, np.random.normal(loc=6, scale=1, size=None) - individual.pre_symptomatic_duration))

        # By means of an example; we can perform any kind of computation to decide upon this.
        individual_dies = random.choice([True, False])

        if individual_dies:
            days_until_demise = np.random.uniform(low=0, high=50, size=None)

            if days_until_demise > symptomatic_duration:

                # FUTURE: Move hospitalized duration elsewhere.
                individual.hospitalized_duration = days_until_demise - symptomatic_duration
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