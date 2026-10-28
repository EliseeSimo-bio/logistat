"""Test de fumée : l'application démarre et chaque onglet s'affiche sans exception."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.mark.slow
def test_app_demarre():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    assert len(at.tabs) == 5
    assert any("Taux de retard" in m.label for m in at.metric)
    assert any("ROC-AUC" in m.label for m in at.metric)


@pytest.mark.slow
def test_app_filtres_et_variable():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    marche = next(w for w in at.multiselect if w.label == "Marché")
    marche.set_value(["Europe"]).run()
    assert not at.exception, at.exception
    at.selectbox(key="facteur").set_value("marche").run()
    assert not at.exception, at.exception
