# -*- coding: future_fstrings -*-
from collections import OrderedDict, UserList, defaultdict
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from fnmatch import fnmatch
from functools import reduce
from typing import *

import pandas as pd

ReducerT = Callable[[pd.Series], Any]
StrOrTupleT = Union[str, tuple]


class QuerySet(UserList):
    def __repr__(self):
        return f"QuerySet({repr(self.data)})"

    def project(
        self, on: List[Union[StrOrTupleT, Dict[StrOrTupleT, ReducerT]]], rename="last", on_missing: str = "raise"
    ) -> pd.DataFrame:
        """Project a set of experiments onto a dataframe.

        Parameters
        ----------
        on: List of dot separated paths that point to values in the experiment model. Instead of a dot separated path
            passing a tuple is also possible. This allows for pointing to path in the model that contain dots themself.
            Additionally, a dict of a path mapping to function applied to the
            values in the experiment model can be used inplace of a path. This is useful for summarizing metrics.
        rename: The renaming strategy used to create the column names. Either "last" to take the last element in each
                path as a column name or None to use the complete paths as column names.
        on_missing: {"raise", "ignore"} Whether to raise an error when missing value is encountered or replace it with 
                    a missing value. 

        Returns
        -------
        A dataframe containing the projected values with the experiment id set as index.
        """
        on = self._stratify_mapping(on)

        # TODO introduce possibility to pass a list to `rename` once we don't need to support 3.5 any longer.
        rename_mapping = self._make_rename_mapping(on, rename)

        projected = defaultdict(list)
        for exp in self.data:
            projected["exp_id"].append(exp.id)
            for path, reducer in on.items():
                projected[path].append(self._extract(exp, path, reducer, on_missing))

        return pd.DataFrame(projected).set_index("exp_id").rename(columns=rename_mapping)

    def delete(self, confirmed: bool = False):
        """Delete all experiments together with their% artifacts and metrics.

        Args:
            confirmed: Whether to skip the confirmation prompt.
        """
        if not confirmed:
            confirmed = input(f"Are you sure you want to delete {self}? [y/N]") == "y"
        if confirmed:
            for exp in self.data:
                exp.delete(confirmed=True)
            print(f"Deleted {len(self.data)} experiments")
            self.data = []
        else:
            print("Deletion aborted")

    def _make_rename_mapping(self, on, rename):
        rename_mapping = {}
        for path, reducer_or_path in on.items():
            if rename == "last":
                str_path = path[-1]
            elif rename is None:
                str_path = ".".join(path)

            if callable(reducer_or_path):
                rename_mapping[path] = f"{str_path}_{reducer_or_path.__name__}"
            else:
                rename_mapping[path] = str_path
        return rename_mapping

    def _stratify_mapping(self, on):
        stratified_on = OrderedDict()
        for path in on:
            if isinstance(path, dict):
                stratified_on.update(path)
            else:
                stratified_on[path] = path
        on = stratified_on

        for path, value in copy(on).items():
            del on[path]
            if isinstance(path, str):
                path = tuple(path.split("."))
            on[path] = value

        return on

    def _extract(self, exp, path, name, on_missing):
        extracted = reduce(lambda x, y: self._get(x, y, on_missing), path, exp)
        if isinstance(name, str):
            return extracted
        elif callable(name):
            return name(extracted)

    def _get(self, o, name, on_missing):
        """Try getattr and getitem."""
        try:
            try:
                return getattr(o, name)
            except AttributeError:
                return o[name]
        except KeyError as exc:
            if on_missing == "ignore":
                return None
            else:
                raise exc

    @property
    def artifacts(self):
        return ArtifactIndexer(self)


class ArtifactIndexer:
    def __init__(self, experiments: QuerySet):
        self._experiments = experiments

    def filter(self, pattern):
        """
        Get all artifacts that match a name of pattern.

        This method does not indicate whether the requested artifacts could be found
        only on some artifacts.

        Args:
            pattern: glob pattern, that is matched against artifact name.

        Returns:

        """
        return ArtifactSet(
            artifact
            for exp in self._experiments
            for artifact_name, artifact in exp.artifacts.items()
            if fnmatch(artifact_name, pattern)
        )

    def __getitem__(self, item):
        return ArtifactSet(exp.artifacts[item] for exp in self._experiments)


class ArtifactSet(UserList):
    def save(self, to_dir, n_threads=None):
        with ThreadPoolExecutor(max_workers=n_threads) as executer:
            for artifact in self.data:
                executer.submit(artifact.save, to_dir=to_dir)
