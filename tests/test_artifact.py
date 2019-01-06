from incense.artifact import PNGArtifact, CSVArtifact


def test_png_artifacts(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['confusion_matrix'], PNGArtifact)


def test_csv_artifacts(loader):
    exp = loader.find_by_id(3)
    assert isinstance(exp.artifacts['predictions'], CSVArtifact)
