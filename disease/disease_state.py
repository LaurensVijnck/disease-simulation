from enum import Enum


class DiseaseStateEnum(Enum):
    STATE_SUSCEPTIBLE = 1 # Default state
    STATE_EXPOSED = 2
    STATE_INFECTED = 3
    STATE_RECOVERED = 4
    STATE_DIED = 5