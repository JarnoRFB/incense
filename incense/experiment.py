# -*- coding: future_fstrings -*-
import json
from typing import *

import jsonpickle
from pyrsistent import freeze, thaw

from incense.artifact import Artifact, content_type_to_artifact_cls
import pandas as pd


class Experiment:
    def __init__(self, id_, database, grid_filesystem, data, artifact_links, loader):
        self.id = id_
        self._data = data
        self._artifacts_links = artifact_links
        self._database = database
        self._grid_filesystem = grid_filesystem
        self._loader = loader
        self._artifacts = None
        self._metrics = None

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.experiment.name})"

    def __getattr__(self, item):
        """Try to relay attribute access to easy dict, to allow dotted access."""
        return getattr(self._data, item)

    @classmethod
    def from_db_object(cls, database, grid_filesystem, experiment_data: dict, loader,
                       unpickle: bool = True):
        if unpickle:
            experiment_data['info'] = jsonpickle.loads(
                json.dumps(experiment_data['info']))
        data = freeze(experiment_data)

        artifacts_links = experiment_data["artifacts"]
        id_ = experiment_data["_id"]
        return cls(id_, database, grid_filesystem, data, artifacts_links, loader)

    @property
    def artifacts(self) -> Dict[str, Artifact]:
        """
        The artifacts belonging to the experiment.

        Returns:
            A mapping from artifact names to artifact objects, that
            belong to the experiment.
        """
        if self._artifacts is None:
            self._artifacts = self._load_artifacts()

        return self._artifacts

    @property
    def metrics(self) -> Dict[str, pd.Series]:
        """
        The metrics belonging to the experiment.

        Returns:
            A mapping from metric names to pandas Series objects, that
            belong to the experiment.
        """
        if self._metrics is None:
            self._metrics = self._load_metrics()

        return self._metrics

    def to_dict(self) -> dict:
        """Convert the experiment to a dictionary.

        Returns:
            A dict with all data from the sacred data model.
        """
        return thaw(self._data)

    def delete(self, confirmed: bool = False):
        """Delete run together with its artifacts and metrics.

        Args:
            confirmed: Whether to skip the confirmation prompt.
        """
        if not confirmed:
            confirmed = input(
                f"Are you sure you want to delete {self}? [y/N]") == "y"
        if confirmed:
            self._delete()

    def _load_artifacts(self) -> Dict[str, Artifact]:
        artifacts = {}
        for artifact_link in self._artifacts_links:
            artifact_file = self._grid_filesystem.get(artifact_link["file_id"])
            name = artifact_link["name"]

            try:
                content_type = artifact_file.content_type
                artifact_type = content_type_to_artifact_cls[content_type]
                artifacts[name] = artifact_type(
                    name, artifact_file, content_type=content_type)
            except KeyError:
                artifact_type = Artifact
                artifacts[name] = artifact_type(name, artifact_file)

        return artifacts

    def _delete(self):
        self._delete_artifacts()
        self._delete_metrics()
        self._database.runs.delete_one({"_id": self.id})
        self._loader.cache_clear()

    def _load_metrics(self) -> Dict[str, pd.Series]:
        metrics = {}
        metric_db_entries = self._database.metrics.find({"run_id": self.id})
        for metric_db_entry in metric_db_entries:
            metrics[metric_db_entry["name"]] = pd.Series(
                data=metric_db_entry["values"],
                index=pd.Index(metric_db_entry["steps"], name="step"),
                name=metric_db_entry["name"],
            )
        return metrics

    def _delete_metrics(self):
        self._database.metrics.delete_many({"run_id": self.id})

    def _delete_artifacts(self):
        for artifact_link in self._artifacts_links:
            self._grid_filesystem.delete(artifact_link["file_id"])
