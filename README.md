# Disease simulation

Highly-configurable application to simulate infections diseases.

## Installation

To install the package locally on your machine, make sure you are in the folder
where the `disease-simulation` is located. Enter the following command in the terminal 
to install the package:

```bash
pip install .
```

## Running the simulation

The simulation can be started by executing the command below (and referencing a _valid_ configuration file).

```bash
python3 main.py --conf config/settings.toml
```

## Disease Simulation Concepts

Within the sections below, we'll briefly cover the different concepts involved. Refer 
to `doc/disease_model.png` for a schematic overview.

![alt text](https://github.com/LaurensVijnck/disease-simulation/blob/master/doc/disease_model.png?raw=true)

### Configuration TOML

The entire simulation is configured by means of a simple `.toml` file. The configuration is dispatched
to the various components throughout the application, e.g., the population and transmission model. An 
example can be found below:

```toml
# ----------------------------------------------------------------------------------------------------------------------
[global]
    seed = 453                                                      # seed value to yield reproducable results
    date_format = "%Y-%m-%d"                                        # date format used globally
    num_age_groups_pop = 4                                          # number of population age groups
    num_age_groups_hh = 4                                           # number of household age groups

# ----------------------------------------------------------------------------------------------------------------------
[simulation]
start_date = "2010-1-1"                                             # start date simulation
end_date = "2010-12-31"                                             # end date simulation

initial_influx = 10                                                 # initial influx
influx_period_in_days = 2                                           # influx every x days
num_influx_per_period = 0                                           # daily influx

terminate_on_zero_infected = true                                   # terminate if num. infected reaches zero

    # ------------------------------------------------------------------------------------------------------------------
    [simulation.reporter]
    enabled = true                                                  # whether to report while running
    report_period_in_days = 2                                       # report every x days
    line_length = 100                                               # line length for formatting

    sink = "console"                                                # sink for writing reporter data
    log_level = ["error", "info"]                                   # types of logs to show, i.e., debug, info, error

        [simulation.reporter.sinks]                                 # sink specific settigs

            # File sink
            [simulation.reporter.sinks.file]                        # file sink specific settings
            output_file_name = "./output/reporter_output.txt"       # name of the output file in-case file sink is used
    # ------------------------------------------------------------------------------------------------------------------
    [simulation.disease]

        [simulation.disease.logger]
            enabled = true                                          # enable log creation of infection
            tans_log_file_name = "./output/transmission_log.csv"    # file to write transmission log to
            sim_log_file_name = "./output/simulation_log.csv"       # file to write simulation log to
            disease_log_file_name = "./output/disease_log.csv"      # file to write disease log to, i.e., changes in the disease state

        [simulation.disease.transmission]
        pop_matrix = "./input/pop_contact.csv"                      # location population contact matrix
        hh_matrix = "./input/hh_contact_no_children.csv"            # location household contact matrix
        hh_matrix_children = "./input/hh_contact_children.csv"      # location household with children contact matrix

        # beta_household = 0.05                                     # beta household (Deprecated, currently specified in the transmission model)
        # beta_population = 0.95                                    # beta population (Deprecated, currently specified in the transmission model)
    # ------------------------------------------------------------------------------------------------------------------
    [simulation.population]
        age_child_limit = 13                                        # maximum age till individual is considered to be a child (exclusive!)

    # ------------------------------------------------------------------------------------------------------------------
    [simulation.log_player]
    base_population = "./input/pop_sample_NH.csv"                   # Base population is used to compute base age distribution (used to compute adjustment in disease model)
    initial_population = "./input/pop_sample_NH.csv"                # location initial population csv
    event_log = "./input/event_log_sample_NH.csv"                   # location demographic events log
# ----------------------------------------------------------------------------------------------------------------------
```

### Event Log

The most prevalent concept is that of an event log. The event log is an input log file that contains logs
representing demographic events, e.g., births, deaths, etc.

Recall that this simulation executes on a discrete, day-to-day fashion. On each iteration, the `EventLogPlayer`
plays the events for the specific day and updates the population accordingly. The disease model
is subsequently invoked to simulate the transmission for the iteration. 

### Transmission model

The application currently leverages a two-level mixing model. This implies that
the logic distinguishes between transmission internal to or external from a specific household. 
The probability of getting infected is hence based on age- and sex-specific
contact matrices and a snapshot of the population/household respectively. 

### Disease state machine

The stages of the disease are expressed by means of a state 
machine, e.g., infected, hospitalized, etc. The machine describes
the various states of the disease and rules for transitioning between
these states.

