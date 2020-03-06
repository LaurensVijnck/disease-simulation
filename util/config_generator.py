import toml
import os
import copy

#
# Simple script to generate config files with different @{seeds}, based on the specified
# @{base_config}.
#
# Source: https://gist.github.com/pgilad/e8ffd8ce2bde81a1a375e86df77a34ab
#

# Settings
from libraries.deep_dict import DeepDict

base_config_file  = "base_config.toml"
output_dir = "./generated/configs/"
seeds = [4,7,9,16,232,234,453,548,909,988,2324,4649,7777,7879,24235,56777,463474,766666,11111111,34235236326]

# Open base config
with open(base_config_file) as source:
  base_config = toml.load(source)

# Create dir
if not os.path.exists(os.path.dirname(output_dir)):
    try:
        os.makedirs(os.path.dirname(output_dir))
    except:
        pass

# Generate
for seed in seeds:
    config = copy.deepcopy(base_config)
    deepDict = DeepDict(config)

    glob_config = deepDict.deep_get("global")
    glob_config["seed"] = seed

    reporter_config = deepDict.deep_get("simulation", "reporter", "sinks", "file")
    reporter_config["output_file_name"] = "./output/seed-{}/reporter_output_seed-{}.txt".format(seed, seed)

    logger_config = deepDict.deep_get("simulation", "disease", "logger")
    logger_config["inf_log_file_name"] = "./output/seed-{}/infection_log_seed-{}.csv".format(seed, seed)
    logger_config["sim_log_file_name"] = "./output/seed-{}/simulation_log_seed-{}.csv".format(seed, seed)
    toml_config = toml.dumps(deepDict)

    with open(os.path.join(output_dir, "settings_seed-{}.toml".format(seed)), 'w') as target:
        target.write(toml_config)