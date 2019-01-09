from incense import artifact


def test_png_artifacts(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['confusion_matrix'], artifact.PNGArtifact)


def test_csv_artifacts(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions'], artifact.CSVArtifact)


def test_pickle_artifact(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions_pickle'], artifact.Artifact)
    pickle_artifact = exp.artifacts['predictions_pickle'].as_type(artifact.PickleArtifact)
    assert isinstance(pickle_artifact, artifact.PickleArtifact)

# TODO check that astype works not just once.
