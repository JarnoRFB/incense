# -*- coding: future_fstrings -*-
import numbers
from functools import _lru_cache_wrapper, lru_cache
from typing import *

import gridfs
from pymongo import MongoClient

from .experiment import Experiment
from .query_set import QuerySet

MAX_CACHE_SIZE = 32


class ExperimentLoader:
    """Loads artifacts related to experiments."""

    def __init__(self, mongo_uri=None, db_name="sacred"):
        client = MongoClient(mongo_uri)
        self._database = client[db_name]
        self._runs = self._database.runs
        self._grid_filesystem = gridfs.GridFS(self._database)

    def find_by_ids(self, experiment_ids: Iterable[int]) -> QuerySet:
        """
        Find experiments based on a collection of ids.

        Args:
            experiment_ids: Iterable of experiment ids.

        Returns:
            The experiments corresponding to the ids.
        """
        experiments = [self.find_by_id(experiment_id) for experiment_id in experiment_ids]

        return QuerySet(experiments)

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
    def find_by_name(self, name: str) -> QuerySet:
        """
        Find experiments based on regex search against its name.

        A partial match between experiment name and regex is enough
        to find the experiment.

        Args:
            name: Regex that is matched against the experiment name.

        Returns:
            The matched experiments.
        """
        return self.find_by_key("experiment.name", name)

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_config_key(self, key: str, value: Union[str, numbers.Real, tuple]) -> QuerySet:
        """
        Find experiments based on search against a configuration value.

        A partial match between configuration value and regex is enough
        to find the experiment.

        Args:
            key: Configuration key to search on.
            value: Value that is matched against the experiment's configuration.
                   Can be either a string which is  then interpreted as a regex or a number.

        Returns:
            The matched experiments.
        """
        key = f"config.{key}"
        cursor = self._search_collection(key, value)
        experiments = [self._make_experiment(experiment) for experiment in cursor]
        return QuerySet(experiments)

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_by_key(self, key: str, value: Union[str, numbers.Real]) -> QuerySet:
        """
        Find experiments based on search against a value stored in the database.

        A partial match between the value and the regex is enough
        to find the experiment.

        Args:
            key: Key to search on.
            value: Value that is matched against the experiment's information.
                   Can be either a string which is  then interpreted as a regex or a number.

        Returns:
            The matched experiments.
        """
        cursor = self._search_collection(key, value)
        experiments = [self._make_experiment(experiment) for experiment in cursor]
        return QuerySet(experiments)

    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def find_all(self) -> QuerySet:
        """
        Find all experiments stored in the database.

        Returns:
            All experiments.
        """
        cursor = self._runs.find()
        return QuerySet([self._make_experiment(experiment) for experiment in cursor])

    def find(self, query: dict) -> QuerySet:
        """Find experiments based on a mongo query.

        Args:
            An arbitrary mongo query.

        Returns:
            The matched experiments.
        """
        cursor = self._runs.find(query)
        experiments = [self._make_experiment(experiment) for experiment in cursor]
        return QuerySet(experiments)

    def cache_clear(self):
        """Clear all caches of all find functions.

        Useful when you want to see the updates to your database."""
        self.find_all.cache_clear()
        self.find_by_key.cache_clear()
        self.find_by_config_key.cache_clear()
        self.find_by_id.cache_clear()
        self.find_by_name.cache_clear()

    def _find_experiment(self, experiment_id: int):
        run = self._runs.find_one({"_id": experiment_id})
        if run is None:
            raise ValueError(f'Experiment with id {experiment_id} does not exist in database "{self._database.name}".')
        return run

    def _make_experiment(self, experiment) -> Experiment:
        return Experiment.from_db_object(self._database, self._grid_filesystem, experiment, loader=self)

    def _search_collection(self, key, value):
        if isinstance(value, str):
            cursor = self._runs.find({key: {"$regex": rf"{value}"}})
        elif isinstance(value, numbers.Real):
            cursor = self._runs.find({key: value})
        return cursor
