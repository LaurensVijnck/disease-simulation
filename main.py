from libraries.args_handler import ConfigHandler
from simulation import Simulation


def main():
    config = ConfigHandler()
    config.load_from_args()
    simulation = Simulation(config.get_simulation_config(), config.get_global_config())
    simulation.run()


if __name__ == "__main__":
    main()
