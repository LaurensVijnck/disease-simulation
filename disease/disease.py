import datetime as dt
from datetime import datetime
from disease.logger import DiseaseLogger
from population.individual import Individual
from population.population import Population
from population.summary import PopulationSummary
from reporter import Reporter
from disease.transmission import Transmission
from disease.state_machine import DiseaseStateEnum, DiseaseFSM
from disease.rolling_deque import RollingDeque

"""
Disease related mortality:

1. Is fixed infection duration sufficient? 
        - otherwise draw from distribution, in this case maintain priority queue for recovery
2. Model for determining disease related deaths, i.e., concrete formula to derrive probability based on attributes of 'individual/household' (Signe)
        - Write dead log record for death
        - Add to summary
        - Q: How to process deaths? deleted vs. add new disease state, i.e., 'death'
        - Check program crashes when events for death individual are encounter
"""


class Disease:
    def __init__(self, config, global_config, population: Population, reporter: Reporter):
        self.__population = population
        self.__reporter = reporter
        self.__infection_duration = config.get("infection_duration", 3)

        # Create disease logger
        logger_config = config.get("logger")
        self.__disease_logger = DiseaseLogger(logger_config, global_config)

        # Initialize Transmission model
        transmission_config = config.get("transmission")
        self.__transmission = Transmission(transmission_config, global_config)

        # Initialize the disease automaton
        self.__disease_fsm = DiseaseFSM()

        # Recovery queue
        self.__disease_deque = RollingDeque()

    # FUTURE: Parallelize this loop.
    def spread_disease(self, curr_date: datetime):
        """
        Function to apply the disease model on the population as-is. The population
        and recovery queue is updated accordingly.
        """
        summary = PopulationSummary(self.__population, self.__population.get_base_distribution())
        self.__reporter.set_population_summary(summary)
        self.__disease_logger.log_summary(curr_date, summary)
        self.__process_disease_deque(curr_date)

        for household in self.__population.household_gen():
            household.compute_metrics(curr_date, self.__population.get_age_child_limit())
            for individual in household.member_gen():

                if individual.get_disease_sate() == DiseaseStateEnum.STATE_SUSCEPTIBLE:

                    transmission_occurs, hh_trans, pop_trans = self.__transmission.occurs(individual, household, summary)
                    if transmission_occurs:
                        self.transmit(individual, curr_date, False, hh_trans, pop_trans)

    def transmit(self, individual: Individual, date: datetime, influx=False, hh_trans=0, pop_trans=0):
        """
        Function to call when disease is transmitted to an individual.
        """
        self.__disease_logger.log_transmission(individual, date, influx, hh_trans, pop_trans)
        self.__add_to_disease_deque(individual, date, self.__disease_fsm.get_start_node().get_disease_state())

    def get_num_infected(self):
        """
        Function to retrieve the number of infected individuals

        :return: (num) number of infected individuals
        """
        return self.__disease_deque.get_num_elements()

    def __add_to_disease_deque(self, individual: Individual, date: datetime, disease_state: DiseaseStateEnum):
        """
        Function to add to the disease queue.
        """

        # Log entry
        self.__disease_logger.log_disease_state_change(individual, date, disease_state)

        # Set disease state for the individual
        individual.set_disease_state(disease_state)

        # Resolve state to FSM node
        next_node = self.__disease_fsm.get_node_for_type(disease_state)

        if not next_node.is_end_state():

            # Determine next state and days until next state
            next_state, days_offset = next_node.get_next_state(individual, date)

            # Push onto disease deque
            self.__disease_deque.put_element(date + dt.timedelta(self.__infection_duration), (next_state, individual))

    def __process_disease_deque(self, curr_date: datetime):
        """
        Function to process the disease deque for the current date.
        """
        # Process disease deque up to current date
        for next_state, individual in self.__disease_deque.get_elements_for_date(curr_date):
            self.__add_to_disease_deque(individual, curr_date, next_state)
