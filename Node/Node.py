from RoundCoordinator import RoundCoordinator


class Node:
    def start(self, config_manager):
        round_coordinator = RoundCoordinator(config_manager)
        round_coordinator.perform_round()
