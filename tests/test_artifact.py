import imghdr
import os
import pickle

import IPython
import pandas as pd
import pytest
from IPython.display import HTML
from pytest import raises

from incense import artifact


def test_repr(loader):
    exp = loader.find_by_id(3)
    csv_artifact = exp.artifacts["predictions"]
    assert repr(csv_artifact) == "CSVArtifact(name=predictions)"
    mp4_artifact = exp.artifacts["accuracy_movie"]
    assert repr(mp4_artifact) == "MP4Artifact(name=accuracy_movie)"


def test_png_artifact_render(loader):
    exp = loader.find_by_id(3)
    png_artifact = exp.artifacts["confusion_matrix"]
    assert isinstance(png_artifact, artifact.ImageArtifact)
    assert isinstance(png_artifact.render(), IPython.core.display.Image)


def test_png_artifact_save(loader, tmpdir):
    exp = loader.find_by_id(3)
    exp.artifacts["confusion_matrix"].save(to_dir=tmpdir)
    filepath = str(tmpdir / "3_confusion_matrix.png")
    assert os.path.isfile(filepath)
    assert imghdr.what(filepath) == "png"


def test_csv_artifact_render(loader):
    exp = loader.find_by_id(3)
    csv_artifact = exp.artifacts["predictions"]
    assert isinstance(csv_artifact, artifact.CSVArtifact)
    assert isinstance(csv_artifact.render(), pd.DataFrame)


def test_csv_artifact_render_warning(loader):
    exp = loader.find_by_id(3)
    csv_artifact = exp.artifacts["predictions"]
    assert isinstance(csv_artifact, artifact.CSVArtifact)
    with pytest.deprecated_call():
        assert isinstance(csv_artifact.show(), pd.DataFrame)


def test_mp4_artifact_save(loader, tmpdir):
    exp = loader.find_by_id(2)
    exp.artifacts["accuracy_movie"].save(to_dir=tmpdir)
    filepath = str(tmpdir / "2_accuracy_movie.mp4")
    assert os.path.isfile(filepath)


def test_mp4_artifact_render(loader):
    exp = loader.find_by_id(2)
    mp4_artifact = exp.artifacts["accuracy_movie"]
    assert isinstance(mp4_artifact, artifact.MP4Artifact)
    assert isinstance(mp4_artifact.render(), HTML)
    os.remove("2_accuracy_movie.mp4")


def test_csv_artifact_save(loader, tmpdir):
    exp = loader.find_by_id(3)
    exp.artifacts["predictions"].save(to_dir=tmpdir)
    filepath = str(tmpdir / "3_predictions.csv")
    assert os.path.isfile(filepath)
    assert isinstance(pd.read_csv(filepath), pd.DataFrame)


def test_pickle_artifact_render(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts["predictions_df"], artifact.Artifact)
    pickle_artifact = exp.artifacts["predictions_df"].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact, artifact.PickleArtifact)
    # Check that unpickling works.
    assert isinstance(pickle_artifact.render(), pd.DataFrame)


def test_pickle_artifact_save(loader, tmpdir):
    exp = loader.find_by_id(3)
    pickle_artifact = exp.artifacts["predictions_df"].as_type(artifact.PickleArtifact)
    pickle_artifact.save(to_dir=tmpdir)
    filename = str(tmpdir / "3_predictions_df.pickle")
    assert os.path.isfile(filename)
    assert isinstance(pickle.load(open(filename, "rb")), pd.DataFrame)


def test_pdf_artifact_save(loader, tmpdir):
    exp = loader.find_by_id(2)
    pdf_artifact = exp.artifacts["confusion_matrix.pdf"]
    pdf_artifact.save(to_dir=tmpdir)
    filepath = str(tmpdir / "2_confusion_matrix.pdf")
    assert os.path.isfile(filepath)


def test_as_type(loader):
    """Check that as_type can be used more than once."""
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts["predictions_df"], artifact.Artifact)
    # Use as_type for the first time.
    pickle_artifact1 = exp.artifacts["predictions_df"].as_type(artifact.PickleArtifact)
    # Use as_type for the second time.
    pickle_artifact2 = exp.artifacts["predictions_df"].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact2.render(), pd.DataFrame)


def test_as_content_type(loader):
    exp = loader.find_by_id(2)
    assert isinstance(exp.artifacts["history"], artifact.Artifact)
    text_artifact_as_csv = exp.artifacts["history"].as_content_type("text/csv")
    assert isinstance(text_artifact_as_csv.render(), pd.DataFrame)


def test_as_content_type_with_unkwown_content_type(loader):
    exp = loader.find_by_id(2)
    assert isinstance(exp.artifacts["history"], artifact.Artifact)
    with raises(ValueError):
        text_artifact_as_something_strange = exp.artifacts["history"].as_content_type("something/strange")


def test_artifact_render_with_unknown_content_type(loader):
    exp = loader.find_by_id(3)
    with raises(NotImplementedError):
        exp.artifacts["predictions_df"].render()


def test_artifact_save_with_unknown_content_type(loader, tmpdir):
    exp = loader.find_by_id(3)
    exp.artifacts["predictions_df"].save(to_dir=tmpdir)
    filepath = str(tmpdir / "3_predictions_df")
    assert os.path.isfile(filepath)
