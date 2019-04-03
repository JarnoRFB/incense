from ._version import get_versions
from .experiment_loader import ExperimentLoader

__version__ = get_versions()["version"]
del get_versions
