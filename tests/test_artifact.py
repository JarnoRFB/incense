import os
import imghdr
import pickle

import pandas as pd
import matplotlib
from IPython.display import HTML

from incense import artifact


def test_png_artifact_show(loader):
    exp = loader.find_by_id(3)
    png_artifact = exp.artifacts['confusion_matrix']
    assert isinstance(png_artifact, artifact.PNGArtifact)
    assert isinstance(png_artifact.show(), matplotlib.figure.Figure)


def test_png_artifact_save(loader):
    exp = loader.find_by_id(3)
    exp.artifacts['confusion_matrix'].save()
    filename = '3_confusion_matrix.png'
    assert os.path.isfile(filename)
    assert (imghdr.what(filename) == 'png')
    os.remove(filename)


def test_csv_artifact_show(loader):
    exp = loader.find_by_id(3)
    csv_artifact = exp.artifacts['predictions']
    assert isinstance(csv_artifact, artifact.CSVArtifact)
    assert isinstance(csv_artifact.show(), pd.DataFrame)


def test_mp4_artifact_save(loader):
    exp = loader.find_by_id(2)
    exp.artifacts['accuracy_movie'].save()
    filename = '2_accuracy_movie.mp4'
    assert os.path.isfile(filename)
    os.remove(filename)


def test_mp4_artifact_show(loader):
    exp = loader.find_by_id(2)
    mp4_artifact = exp.artifacts['accuracy_movie']
    assert isinstance(mp4_artifact, artifact.MP4Artifact)
    assert isinstance(mp4_artifact.show(), HTML)
    os.remove('2_accuracy_movie.mp4')


def test_csv_artifact_save(loader):
    exp = loader.find_by_id(3)
    exp.artifacts['predictions'].save()
    filename = '3_predictions.csv'
    assert os.path.isfile(filename)
    assert (isinstance(pd.read_csv(filename), pd.DataFrame))
    os.remove(filename)


def test_pickle_artifact_show(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions_df'], artifact.Artifact)
    pickle_artifact = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact, artifact.PickleArtifact)
    # Check that unpickling works.
    assert isinstance(pickle_artifact.show(), pd.DataFrame)


def test_pickle_artifact_save(loader):
    exp = loader.find_by_id(3)
    pickle_artifact = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    pickle_artifact.save()
    filename = '3_predictions_df.pickle'
    assert os.path.isfile(filename)
    assert (isinstance(pickle.load(open(filename, 'rb')), pd.DataFrame))
    os.remove(filename)


def test_as_type(loader):
    """Check that as_type can be used more than once."""
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions_df'], artifact.Artifact)
    pickle_artifact1 = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    pickle_artifact2 = exp.artifacts['predictions_df'].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact2.show(), pd.DataFrame)
