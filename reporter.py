import datetime as dt
from datetime import datetime
import time
import glob
import importlib
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from population.summary import PopulationSummary
import os

class Reporter:
    def __init__(self, config):
        self._start_time = 0
        self._end_time = 0
        self._event_count = 0
        self._error_count = 0
        self._event_count_per_type = defaultdict(int)
        self._error_count_per_type = defaultdict(int)

        self._initial_iteration = None
        self._iteration = None
        self._population_summary = None

        # Initialize sink
        sink_name = config.get("sink", "console")
        sink_config = config.get("sinks").get(sink_name)
        sink_config = sink_config if sink_config else {}
        self._sink = get_sink_module(sink_name)(sink_config)
        self._sink.initialize()

        # Reporting
        self._enabled = config.get("enabled", True)
        self._reporting_period_in_days = config.get("report_period_in_days")
        self._log_level = config.get("log_level", [])
        self._line_length = config.get("line_length", 80)

        # Disease
        self._disease_states = config.get("disease_states", [])
        self.num_pop_age_groups = config.get("num_age_groups_pop", 0)

    def init(self, curr_date: datetime):
        self._start_time = time.time()
        self._initial_iteration = curr_date

    def error(self, message):
        if "error" in self._log_level:
            self._sink.write("[ERROR] " + message)

    def info(self, message):
        if "info" in self._log_level:
            self._sink.write("[INFO] " + message)

    def set_population_summary(self, summary: PopulationSummary):
        self._population_summary = summary

    def set_iteration(self, curr_date: datetime):
        self._iteration = curr_date

        if curr_date != self._initial_iteration and \
                relativedelta(self._initial_iteration, self._iteration).days % self._reporting_period_in_days == 0:
            self.report()

    def add_event(self, event_type):
        self._event_count += 1
        self._event_count_per_type[event_type] += 1

    def add_error(self, event_type):
        self._error_count += 1
        self._error_count_per_type[event_type] += 1

    def final_report(self):
        self.report(True)

    def teardown(self):
        self._sink.close()

    def report(self, force=False):
        if force or self._enabled:
            self._end_time = time.time()
            elapsed_time = self._end_time - self._start_time
            elapsed_time_formatted = str(dt.timedelta(seconds=elapsed_time))
            iteration = self._iteration.strftime('%Y-%m-%d')

            msg = "\n"
            msg += "=" * self._line_length + "\n"
            msg += f"Iteration: {iteration} \n"
            msg +=  "=" * self._line_length + "\n"
            msg += "Population: Current distribution" + "\n"
            msg += '=' * self._line_length + "\n"

            msg += self._pad("Age group", 12) + " "
            for state in self._disease_states:
                msg += self._pad(state, 12) + " "

            msg += "\n"
            msg += '-' * self._line_length + "\n"

            for ag in range(self.num_pop_age_groups):
                msg += self._pad(str(ag), 12) + " "
                msg += self._pad(str(self._population_summary.get_num_susceptible(ag)), 12) + " "
                msg += self._pad(str(self._population_summary.get_num_infected(ag)), 12) + " "
                msg += self._pad(str(self._population_summary.get_num_recovered(ag)), 12) + "\n"

            msg += '-' * self._line_length + "\n"
            msg += self._pad("total", 12) + " "
            msg += self._pad(str(self._population_summary.get_total_susceptible()), 12) + " "
            msg += self._pad(str(self._population_summary.get_total_infected()), 12) + " "
            msg += self._pad(str(self._population_summary.get_total_recovered()), 12) + "\n"

            msg += "=" * self._line_length + "\n"

            msg += f"Log: Processed {self._event_count} events in {elapsed_time}s.\n"
            msg += '-' * self._line_length + "\n"

            for event_type in self._event_count_per_type:
                msg += f"\tProcessed {self._event_count_per_type[event_type]} {event_type} events.\n"

            msg += "-" * self._line_length + "\n"
            msg += f"Elapsed Time: {elapsed_time_formatted}\n"
            msg += '-' * self._line_length + "\n"
            msg += f"Total events: {self._event_count}\n"
            msg += f"Total errors: {self._error_count}\n"

            for event_type in self._error_count_per_type:
                msg += f"\t {self._error_count_per_type[event_type]} errors in {event_type} events.\n"

            msg += "=" * self._line_length + "\n"

            self._sink.write(msg)

    def _pad(self, target_str, dest_len):
        return target_str + " " * max(0,  dest_len - len(target_str))


def get_sink_module(sink_name):
    return get_module("sinks/", "*_sink.py", sink_name)


def get_module(path, name_regex, module_name):
    """
    Dynamically locates module name and returns the class. Goal of this function is to decouple statically imported
    sources and sinks.

    Resources:
    - (1) https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    - (2) https://stackoverflow.com/questions/14050281/how-to-check-if-a-python-module-exists-without-importing-it

    :param path: (str) Path to the modules (eg "sinks/").
    :param name_regex: (str) Regex expression of modules (eg "*_sink.py").
    :param module_name: (str) Requested class name (eg "console").
    :return: (Class) Found class.
    """
    modules = glob.glob(os.path.join(path,name_regex))  # Retrieves all files found in specified path (eg sinks/*_sink.py)
    module_class = None

    for module in modules:  # Iterate each found file to see if specified module can be found (eg pubsub)
        if module[len(path):].startswith(module_name):  # Checks if module starts with requested module name
            import_path = module.replace("/", ".").replace("\\", ".").replace(".py", "")  # Transforms to lib path (eg "sinks.pubsub_sink")
            module_spec = importlib.import_module(import_path)  # See (2)
            for obj in dir(module_spec):  # Iterate module candidates objects (eg __init__, PubSubSink, ...)
                # Check if module obj if it matches request module name (eg pubsubsink.startswith(pubsub))
                if obj.lower().startswith(module_name):
                    temp_module_class = getattr(module_spec, obj)  # Check if candidate class is the right class
                    if "initialize" in dir(temp_module_class):  # The correct module contains a function "initialize"
                        module_class = temp_module_class
                        # TODO if found go out of all for loops (eg break or continue)
                        break

    return module_class