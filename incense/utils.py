# -*- coding: future_fstrings -*-
from functools import reduce
from operator import and_, or_
from typing import *

from incense.experiment import Experiment


def find_differing_config_keys(experiments: Iterable[Experiment]) -> set:
    """Find the config keys that were assigned to different values in a cohort of experiments."""
    config_values = []
    configs = []
    for experiment in experiments:
        config_values.append(set(str(v) for v in experiment.config.values()))
        configs.append(experiment.config)

    differing_config_values = reduce(or_, config_values) ^ reduce(and_, config_values)
    differing_config_keys = set()
    for config in configs:
        for key, value in config.items():
            if str(value) in differing_config_values:
                differing_config_keys.add(key)

    return differing_config_keys


def format_config(exp: Experiment, *config_keys) -> str:
    return " | ".join(f"{key}={exp.config[key]}" for key in config_keys)
