from ruamel.yaml import YAML
import os
from .schema import StrategySchema

def load_strategy(path: str) -> StrategySchema:
    yaml = YAML(typ='safe')
    with open(path, 'r') as f:
        data = yaml.load(f)
    return StrategySchema(**data)
