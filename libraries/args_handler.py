import argparse
import os
import toml

from libraries.deep_dict import DeepDict


class ConfigHandler:
    """
    Load configuration from arguments
    """
    def __init__(self):
        self.simulation_config = None
        self.global_config = None
        self.config = None

    def load_from_args(self):
        args = self.process_args_as_dict()
        config = get_config(args.get("conf"))
        self.config = DeepDict(config)
        self._parse_config()

    def _parse_config(self):
        # Parse elements in the config file
        self.simulation_config = self.config.deep_get("simulation")
        self.global_config = self.config.deep_get("global")

    def get_simulation_config(self):
        return self.simulation_config

    def get_global_config(self):
        return self.global_config

    @staticmethod
    def process_args_as_dict():
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--conf", "--config",
            help="Location of the config file or just the name, with or without the extension",
            required=True)

        return vars(parser.parse_args())  # Convert args to dict


def get_config(config_path):
    """
    Get safely the configuration file.

    :param config_path: (str) Configuration path.
    :return: (dict) Configuration dictionary.
    """
    # Try to get specified config
    if os.path.isfile(config_path):  # Check if config exists
        # Load specified config
        with open(config_path) as fp:
            config = toml.load(fp)
    else:
        raise ValueError(f"Configuration '{config_path}' does not exist.")

    return config