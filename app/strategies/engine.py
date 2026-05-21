from .loader import load_strategy
from .executor import StrategyExecutor

class StrategyEngine:
    def __init__(self):
        self.executor = StrategyExecutor()
        self.strategies = {}

    def start(self):
        # Stub for starting triggers
        pass
