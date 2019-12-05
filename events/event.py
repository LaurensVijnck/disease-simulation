from population.individual import Individual
from population.population import Population


class EventHandler:
    """
    Abstract class responsible for spawning events handlers.
    """
    def __init__(self, population: Population, event, date_format):
        self._population = population
        self._event = event
        self._date_format = date_format

    @staticmethod
    def construct(population, event, date_format):
        type = event["event_type"]

        if type == 'birth' or type == 'immigration':
            return AddToPopEventHandler(population, event, date_format)

        elif type == 'death' or type == 'emigration':
            return RemoveFromPopEventHandler(population, event, date_format)

        elif type == 'hh_transition':
            return HHTransitionEventHandler(population, event, date_format)

        elif type == 'age_group_transition':
            return AGTransitionEventHandler(population, event, date_format)

        raise ValueError("Invalid events type!", type)

    def process(self):
        ...


class AddToPopEventHandler(EventHandler):
    """
    Handler responsible for adding an individual to the population.
    """
    def process(self):
        individual = Individual.create(self._event, self._date_format)
        self._population.add(individual, individual.get_hh_id())


class RemoveFromPopEventHandler(EventHandler):
    """
    Handler responsible for removing an individual to the population.
    """
    def process(self):
        individual = self._population.get(int(self._event["ID"]))
        self._population.delete(individual)


class AGTransitionEventHandler(EventHandler):
    """
    Handler responsible for modifying the age group if an individual.
    """
    def process(self):
        individual = self._population.get(int(self._event["ID"]))
        individual.set_population_age_group(int(self._event["age_group_pop"]))
        individual.set_household_age_group(int(self._event["age_group_hh"]))


class HHTransitionEventHandler(EventHandler):
    """
    Handler responsible for modifying the household of an individual.
    """
    def process(self):
        individual = self._population.get(int(self._event["ID"]))

        if not self._event["HH_ID_target"] == 'NA':
            # Individual changed household
            self._population.remove_from_household(individual)
            self._population.add_to_household(individual, int(self._event["HH_ID_target"]))

        # Individual changed solely household position
        individual.set_hh_position(self._event["hh_position_target"])