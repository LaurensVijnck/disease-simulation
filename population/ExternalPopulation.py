import csv
import mysql.connector

from collections import defaultdict
from events.ExternalEvent import EventHandler
from population.household import HouseHold
from population.individual import Individual


class ExternalPopulation:
    """
    Population class built on top of an SQL connection.

    WARNING: DECOMMISSIONED
    """
    __con = None

    def __init__(self, config, reporter):
        connector_config = config.get("connector")
        self.__con = mysql.connector.connect(
            host=connector_config.get("host"),
            user=connector_config.get("user"),
            passwd=connector_config.get("password"),
            database=connector_config.get("database"),
            auth_plugin='mysql_native_password',
        )

        # Enable auto-commit
        self.__con.autocommit = True
        self.__reporter = reporter

        # Initialize events log reading
        pop_csv = open(config.get("event_log"), mode='r')
        self.__event_reader = csv.DictReader(pop_csv)
        self.__next_event = next(self.__event_reader)

        # Parse configuration
        self.__date_format = config.get("date_format", "%Y-%m-%d")

        # Migrate and load data
        self.__migrate()
        self.__load_data(config.get("initial_population", None))
        self.__initial_summary = None
        self.__initial_summary = self.get_disease_summary()

    def household_gen(self, curr_date):
        """
        Generator to iterate the different households in the population.

        :param curr_date: (date) current date according to the simulation
        :return: (generator) household generator

        # TODO, this buffering should not be required.
        """
        sql = "SELECT DISTINCT HH_ID from population"
        cursor = self.__con.cursor(buffered=True)
        cursor.execute(sql)

        for household in cursor:
            yield self.get_household(household[0], curr_date)

    def random_gen(self, amount):
        """
        Function to retrieve a number of random individuals from the population.

        :param amount: (number) number of individuals to retrieve.
        :return: (generator) individual generator
        """
        sql = "SELECT * FROM population WHERE disease_state='SUS' ORDER BY RAND() LIMIT %s"
        val = (amount,)
        cursor = self.__con.cursor(buffered=True)
        cursor.execute(sql, val)

        for mem in cursor:
            yield Individual(mem[0], mem[1], mem[2], mem[3], mem[4], mem[5], mem[6], mem[7])

    def get_cursor(self):
        """
        Function to retrieve a cursor to the population SQL table.

        :return: (mysql.connector.cursor) Database cursor
        """
        return self.__con.cursor()

    def __migrate(self):
        """
        Function to migrate the underlaying SQL database.
        """
        dbcusor = self.__con.cursor()
        dbcusor.execute("DROP TABLE IF EXISTS population")
        dbcusor.execute("CREATE TABLE population (ID INT PRIMARY KEY, birth_date DATE NOT NULL, sex INT NOT NULL, disease_state VARCHAR(3) NOT NULL DEFAULT 'SUS', population_age_group INT NOT NULL, household_age_group INT NOT NULL, HH_ID INT NOT NULL, HH_position VARCHAR(16) NOT NULL)")
        dbcusor.execute("CREATE INDEX household_index ON population(HH_ID)")

    def __load_data(self, population_csv):
        """
        Function to pre-load the population with an initial sample.

        :param population_csv: (str) Population csv path.
        """
        pop_ins = "INSERT INTO population (id, birth_date, sex, population_age_group, household_age_group, HH_ID, HH_position) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = []

        with open(population_csv, mode='r') as pop_csv:
            csv_reader = csv.DictReader(pop_csv)
            for row in csv_reader:
                if csv_reader.line_num == 0:
                    continue

                # TODO: Insert correct population and household age_groups
                values.append([row["ID"], row["birth_date"], row["sex"], 1, 1, row["HH_ID"], row["hh_position"]])
            self.__reporter.log(f'Added {csv_reader.line_num - 1} individuals to initial population.')

        self.__con.cursor().executemany(pop_ins, values)

    # FUTURE: Move to a separate class.
    def evolve(self, max_date):
        """
        Function to evolve the population up to the specified date.

        :param max_date: (date) date to evolve the population to.
        """
        while self.__next_event and self.__parse_date(self.__next_event["event_date"]) <= max_date:
            try:
                EventHandler.construct(self, self.__next_event).process()
                self.__reporter.add_event(self.__next_event["event_type"])
            except Exception as e:
                self.__reporter.add_error(str(e))
                self.__reporter.add_error(self.__next_event["event_type"])

            # Fetch next events
            self.__next_event = next(self.__event_reader)

    def dissolve(self):
        """
        Function to dissolve the population, i.e., terminate
        connection with the database.
        """
        self.__con.close()

    def get_disease_summary(self):
        """
        Function to get a global summary of the disease, i.e., list the number of
        individuals per disease state, for each population age group.

        :return: (dict) population disease summary
        """
        sql = "SELECT disease_state, population_age_group, count(*) as count FROM population GROUP BY disease_state, population_age_group  ORDER BY disease_state, population_age_group"
        cursor = self.__con.cursor(buffered=True)
        cursor.execute(sql)
        return PopulationSummary(self.__initial_summary, cursor.fetchall())

    def get_household(self, household, curr_date):
        """
        Function to retrieve a household.

        :param household: (number) identifier of the household
        :param curr_date: (date) current date in the simulation
        :return: (HouseHold) household
        """

        ret = HouseHold(household, curr_date)
        sql = "SELECT * FROM population WHERE HH_ID = %s"
        cursor = self.__con.cursor(buffered=True)
        val = (household,)
        cursor.execute(sql, val)
        members = cursor.fetchall()

        # Add household members
        for mem in members:
            ret.add_member(Individual(mem[0], mem[1], mem[2], mem[3], mem[4], mem[5], mem[6], mem[7]))

        return ret


class PopulationSummary:
    def __init__(self, initial_summary, curr_summary):
        self.__state_per_age_group = defaultdict(int)
        self.__total_per_age_group = defaultdict(int)
        self.__initial_summary = initial_summary
        self.__parse_summary(curr_summary)

    def get_num_infected(self, age_group):
        return self.__state_per_age_group[('INF', age_group)]

    def get_total(self, age_group):
        return self.__total_per_age_group[age_group]

    def get_adjustment(self, age_group):
        return self.__initial_summary.get_total(age_group) / max(self.__total_per_age_group[age_group], 1)

    def __parse_summary(self, summary):
        idx = 0
        while idx < len(summary):
            self.__state_per_age_group[(summary[idx][0], summary[idx][1])] += summary[idx][2]
            self.__total_per_age_group[summary[idx][1]] += summary[idx][2]
            idx += 1
