import toml
import os


# Create dir
outputdir = "./generated/configs/"
if not os.path.exists(os.path.dirname(outputdir)):
    try:
        os.makedirs(os.path.dirname(outputdir))
    except:
        pass

seeds = [30, 40, 50] # put your seeds here

for seed in seeds:
    config = {
      "global": {
        "seed": seed,
        "date_format": "%Y-%m-%d",
        "disease_states": [
          "Susceptible",
          "Infected",
          "Recovered"
        ],
        "num_age_groups_pop": 4,
        "num_age_groups_hh": 4
      },
      "simulation": {
        "start_date": "2002-1-1",
        "end_date": "2002-1-2",
        "initial_influx": 100,
        "influx_period_in_days": 2,
        "num_influx_per_period": 0,
        "terminate_on_zero_infected": True,
        "reporter": {
          "enabled": True,
          "report_period_in_days": 2,
          "line_length": 80,
          "sink": "file",
          "log_level": [
            "error",
            "info"
          ],
          "sinks": {
            "file": {
              "output_file_name": "./output/seed-{}/reporter_output_seed-{}.txt".format(seed, seed)
            }
          }
        },
        "disease": {
          "infection_duration": 4,
          "age_child_limit": 18,
          "logger": {
            "enabled": True,
            "inf_log_file_name": "./output/seed-{}/infection_log_seed-{}.csv".format(seed, seed),
            "sim_log_file_name": "./output/seed-{}/simulation_log_seed-{}.csv".format(seed, seed)
          },
          "transmission": {
            "pop_matrix": "./input/pop_contact.csv",
            "hh_matrix": "./input/hh_contact_no_children.csv",
            "hh_matrix_children": "./input/hh_contact_children.csv",
            "beta_household": 0.05,
            "beta_population": 0.6
          }
        },
        "log_player": {
          "initial_population": "./input/pop.csv",
          "event_log": "./input/event_log.csv"
        }
      }
    }

    toml_config = toml.dumps(config)

    with open(os.path.join(outputdir, "settings_seed-{}.toml".format(seed)), 'w') as target:
        target.write(toml_config)