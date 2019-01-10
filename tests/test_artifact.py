import pandas as pd
import matplotlib
from incense import artifact


def test_png_artifacts(loader):
    exp = loader.find_by_id(3)
    png_artifact = exp.artifacts['confusion_matrix']
    assert isinstance(png_artifact, artifact.PNGArtifact)
    assert isinstance(png_artifact.show(), matplotlib.figure.Figure)


def test_csv_artifacts(loader):
    exp = loader.find_by_id(3)
    csv_artifact = exp.artifacts['predictions']
    assert isinstance(csv_artifact, artifact.CSVArtifact)
    assert isinstance(csv_artifact.show(), pd.DataFrame)


def test_pickle_artifact(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions_df'], artifact.Artifact)
    pickle_artifact = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact, artifact.PickleArtifact)
    # Check that unpickling works.
    assert isinstance(pickle_artifact.show(), pd.DataFrame)


def test_as_type(loader):
    """Check that as_type can be used more than once."""
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions_df'], artifact.Artifact)
    pickle_artifact1 = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    pickle_artifact2 = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact2.show(), pd.DataFrame)
