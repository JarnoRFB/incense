import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal


def test_projection_with_renaming(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {'exp_id': [1, 2, 3],
                               'epochs': [1, 3, 1],
                               'optimizer': ['sgd', 'sgd', 'adam']}
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", "config.optimizer"])

    assert_frame_equal(projected, expected_projected)


def test_projection_without_renaming(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {'exp_id': [1, 2, 3],
                               'config.epochs': [1, 3, 1],
                               'config.optimizer': ['sgd', 'sgd', 'adam']}
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", "config.optimizer"], rename=None)

    assert_frame_equal(projected, expected_projected)


def test_projection_with_aggregation(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {'exp_id': [1, 2, 3],
                               'epochs': [1, 3, 1],
                               'training_loss_mean': [0.6378391059716543,
                                                              0.425261557425393,
                                                              0.2187067011743784]}
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", {"metrics.training_loss": np.mean}])
    assert_frame_equal(projected, expected_projected)
