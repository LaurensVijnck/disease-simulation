# File is deprecated, kept in for future purposes.
class EventHandler:
    pop_cursor = None
    event = None

    @staticmethod
    def construct(population, event):
        type = event["event_type"]

        if type == 'birth' or type == 'immigration':
            return AddToPopEventHandler(population, event)

        elif type == 'death' or type == 'emigration':
            return RemoveFromPopEventHandler(population, event)

        elif type == 'hh_transition':
            return HHTransitionEventHandler(population, event)

        elif type == 'age_group_transition':
            return AGTransitionEventHandler(population, event)

        elif type == 'disease_state_change':
            return DiseaseStateChangedHandler(population, event)

        raise ValueError("Invalid events type!", type)

    def __init__(self, population, event):
        self.pop_cursor = population.get_cursor()
        self.event = event

    def process(self):
        ...


# Handler to add an individual to the population
class AddToPopEventHandler(EventHandler):
    def process(self):
        pop_ins = "INSERT INTO population (id, birth_date, sex population_age_group, household_age_group, HH_ID, hh_position, NH) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (self.event["ID"], self.event["birth_date"], self.event["sex"], self.event["age_group_pop"], min(int(self.event["age_group_hh"]), 4), int(self.event["HH_ID"]), self.event["hh_position"], self.event["NH"])
        self.pop_cursor.execute(pop_ins, val)


# Handler to remove an individual to the population
class RemoveFromPopEventHandler(EventHandler):
    def process(self):
        pop_del = "DELETE FROM population WHERE ID = %s"
        val = (self.event["ID"], )
        self.pop_cursor.execute(pop_del, val)


# Handler to process a household transition
class HHTransitionEventHandler(EventHandler):
    def process(self):
        pop_upd = "UPDATE population SET HH_ID = %s, HH_position = %s WHERE ID = %s"

        if self.event["HH_ID_target"] == 'NA':
            self.event["HH_ID_target"] = int(self.event["HH_ID"])

        val = (int(self.event["HH_ID_target"]), self.event["hh_position_target"], self.event["ID"])
        self.pop_cursor.execute(pop_upd, val)


# Handler to process age group transitions
class AGTransitionEventHandler(EventHandler):
    def process(self):
        pop_upd = "UPDATE population SET population_age_group = %s, household_age_group = %s WHERE ID = %s"
        val = (self.event["age_group_pop"], min(int(self.event["age_group_hh"]), 4), self.event["ID"])
        self.pop_cursor.execute(pop_upd, val)


# Handler to change disease state
class DiseaseStateChangedHandler(EventHandler):
    def process(self):
        pop_upd = "UPDATE population SET disease_state = %s WHERE ID = %s"
        val = (self.event["disease_state"], self.event["ID"])
        self.pop_cursor.execute(pop_upd, val)