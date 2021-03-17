import datetime as dt
from datetime import datetime

from disease.disease import Disease
from population.population import Population
from reporter import Reporter
from events.log import EventLogPlayer
from dateutil.relativedelta import relativedelta


class Simulation:
    """
    Class that represents the disease simulation.
    """
    def __init__(self, config, global_config):
        # Parse configuration
        self.date_format = global_config.get("date_format", "%Y-%m-%d")
        self.simulation_start = datetime.strptime(config.get("start_date"), self.date_format)
        self.simulation_end = datetime.strptime(config.get("end_date"), self.date_format)
        self.initial_influx = config.get("initial_influx", 0)
        self.num_influx_per_period = config.get("num_influx_per_period", 0)
        self.influx_period_in_days = config.get("influx_period_in_days", 1)
        self.terminate_prematurely = config.get("terminate_on_zero_infected", False)

        # Initialize Reporter
        reporter_config = config.get("reporter")
        self.reporter = Reporter(reporter_config, global_config)

        # Initialize Population
        population_config = config.get("population")
        self.population = Population(population_config, global_config)

        # Initialize EventLogPlayer
        player_config = config.get("log_player")
        self.log_player = EventLogPlayer(player_config, global_config, self.population, self.reporter)

        # Initialize disease
        disease_config = config.get("disease")
        self.disease = Disease(disease_config, global_config, self.population, self.reporter)

    def run(self):
        """
        Function responsible for delegating the simulation.
        """
        simulation_curr = self.simulation_start
        terminated_prematurely = False
        self.reporter.init(simulation_curr)
        self.disease_influx(self.initial_influx, simulation_curr)
        self.reporter.info(f"Initial influx of {self.initial_influx} individuals.")

        while simulation_curr <= self.simulation_end:
            # Set iteration for reporter
            self.reporter.set_iteration(simulation_curr)

            # Check whether influx should occur
            if self.num_influx_per_period > 0 \
                    and relativedelta(self.simulation_start, simulation_curr).days % self.influx_period_in_days == 0:
                self.reporter.info(f"Influxed {self.num_influx_per_period} individuals.")
                self.disease_influx(self.num_influx_per_period, simulation_curr)

            # Disease model
            self.disease.spread_disease(simulation_curr)
            if self.terminate_prematurely and self.disease.get_num_infected() == 0:
                self.reporter.info("Prematurely terminating simulation, number of infected individuals reached zero.")
                terminated_prematurely = True
                break

            # Fast forward
            self.log_player.fast_forward(simulation_curr)

            # Prepare next iteration
            simulation_curr += dt.timedelta(days=1)

        if not terminated_prematurely:
            self.reporter.info(f"Simulation reached end date '{self.simulation_end.strftime(self.date_format)}', terminating...")
            self.reporter.final_report()

        self.reporter.teardown()

    def disease_influx(self, amount, curr_date: datetime):
        """
        Function to infect a number of random individuals.

        :param amount: (number) number of people to infect
        :param curr_date: (datetime) date at which people are infected
        """
        for individual in self.population.random_gen(amount):

            # TODO: What happens when individual is already in the disease state machine? Should we ignore? - LVI
            individual.index_case = True
            self.disease.transmit(individual, curr_date, influx=True)


