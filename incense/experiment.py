import pandas as pd
from typing import *

from incense import artifact
from incense.artifact import Artifact, content_type_to_artifact_cls


class Experiment:

    def __init__(self, id_, database, grid_filesystem, config, artifact_links):
        self.id = id_
        self.config = config
        self._artifacts_links = artifact_links
        self._database = database
        self._grid_filesystem = grid_filesystem
        self._artifacts = None
        self._metrics = None

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'

    @classmethod
    def from_db_object(cls, database, grid_filesystem, experiment_data: dict):
        config = experiment_data['config']
        artifacts_links = experiment_data['artifacts']
        id_ = experiment_data['_id']
        return cls(id_, database, grid_filesystem, config, artifacts_links)

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

    def _load_artifacts(self) -> Dict[str, Artifact]:
        artifacts = {}
        for artifact_link in self._artifacts_links:
            artifact_file = self._grid_filesystem.get(artifact_link['file_id'])
            try:
                artifact_type = content_type_to_artifact_cls[artifact_file.content_type]
            except KeyError:
                # TODO: Should be removed once PR is merged.
                try:
                    artifact_type = content_type_to_artifact_cls[artifact_file.metadata['content-type']]
                except (KeyError, TypeError):
                    artifact_type = Artifact

            name = artifact_link['name']
            artifacts[name] = artifact_type(name, artifact_file)
        return artifacts

    def _load_metrics(self) -> Dict[str, pd.Series]:
        metrics = {}
        metric_db_entries = self._database.metrics.find({'run_id': self.id})
        for metric_db_entry in metric_db_entries:
            metrics[metric_db_entry['name']] = pd.Series(data=metric_db_entry['values'],
                                                         index=pd.Index(metric_db_entry['steps'], name='step'),
                                                         name=metric_db_entry['name'])
        return metrics
