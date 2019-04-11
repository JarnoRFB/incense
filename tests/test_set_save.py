# -*- coding: future_fstrings -*-
import os


def test_single_save(loader, tmpdir):
    exp_ids = [1, 2, 3]
    exps = loader.find_by_ids(exp_ids)
    exps.artifacts["confusion_matrix"].save(to_dir=tmpdir)
    for exp_id in exp_ids:
        filepath = tmpdir / f"{exp_id}_confusion_matrix.png"
        assert os.path.isfile(str(filepath))


def test_glob_save(loader, tmpdir):
    exp_ids = [1, 2, 3]
    exps = loader.find_by_ids(exp_ids)
    exps.artifacts["confusion_matrix*"].save(to_dir=tmpdir)
    for exp_id in exp_ids:
        filepath = tmpdir / f"{exp_id}_confusion_matrix.png"
        assert os.path.isfile(str(filepath))
        filepath = tmpdir / f"{exp_id}_confusion_matrix.pdf"
        assert os.path.isfile(str(filepath))
