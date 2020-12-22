from enum import Enum


class DiseaseStateEnum(Enum):
    STATE_SUSCEPTIBLE = 1 # Default state
    STATE_EXPOSED = 2
    STATE_INFECTED = 3
    STATE_SYMPTOMATIC = 4
    STATE_ASYMPTOMATIC = 5
    STATE_HOSPITALIZED = 6
    STATE_RECOVERED = 7
    STATE_DIED = 8