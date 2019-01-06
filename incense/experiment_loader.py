from pymongo import MongoClient
import gridfs
from functools import lru_cache
from typing import *

from incense.experiment import Experiment

credentials = []

MAX_CACHE_SIZE = 32


class ExperimentLoader:
    """Loads artifacts related to experiments."""

    def __init__(self, mongo_uri=None, db_name='sacred'):
        client = MongoClient(mongo_uri)
        self._database = client[db_name]
        self._runs = self._database.runs
        self._grid_filesystem = gridfs.GridFS(self._database)

    def find_by_ids(self, experiment_ids: Iterable[int]) -> List[Experiment]:
        """
        Find experiments based on a collection of ids.

        Args:
            experiment_ids: Iterable of experiment ids.

        Returns:
            The experiments corresponding to the ids.
        """
        experiments = [self.find_by_id(experiment_id) for experiment_id in experiment_ids]

        return experiments

    # The cache makes sure that retrieval of the experiments
    # is not unnecessarily done more than once.
    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_id(self, experiment_id: int) -> Experiment:
        """
        Find experiment based on its id.

        Args:
            experiment_id: The id  of the experiment.

        Returns:
            The experiment corresponding to the id.
        """
        experiment = self._find_experiment(experiment_id)

        return self._make_experiment(experiment)

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_name(self, name: str) -> List[Experiment]:
        """
        Find experiments based on regex search against its name.

        A partial match between experiment name and regex is enough
        to find the experiment.

        Args:
            name: Regex that is matched against the experiment name.

        Returns:
            The matched experiments.
        """
        return self.find_by_key('experiment.name', name)

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_config_key(self, key: str, value: str) -> List[Experiment]:
        """
        Find experiments based on regex search against a configuration value.

        A partial match between configuration value and regex is enough
        to find the experiment.

        Args:
            key: Configuration key to search on.
            value: Regex that is matched against the experiment's configuration.

        Returns:
            The matched experiments.
        """
        cursor = self._runs.find({f'config.{key}': {'$regex': rf'{value}'}})
        experiments = [self._make_experiment(experiment) for experiment in cursor]
        return experiments

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_key(self, key: str, value: str) -> List[Experiment]:
        """
        Find experiments based on regex search against a value stored in the database.

        A partial match between the value and the regex is enough
        to find the experiment.

        Args:
            key: Key to search on.
            value: Regex that is matched against the experiment's configuration.

        Returns:
            The matched experiments.
        """
        cursor = self._runs.find({key: {'$regex': rf'{value}'}})
        experiments = [self._make_experiment(experiment) for experiment in cursor]
        return experiments

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def _find_experiment(self, experiment_id: int):
        return self._runs.find_one({'_id': experiment_id})

    def _make_experiment(self, experiment) -> Experiment:
        return Experiment.from_db_object(self._database, self._grid_filesystem, experiment)
