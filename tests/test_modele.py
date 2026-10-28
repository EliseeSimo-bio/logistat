import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from logistat.donnees import FACTEURS_COMMANDES, FUITES_COMMANDES, population_modelisation
from logistat.modele import (
    ErreurModele,
    courbe_roc,
    decoupage_chronologique,
    envelopper,
    evaluer,
    matrice_confusion,
    probabilite_retard,
    stockage,
    verifier_modele,
    verifier_variables,
)
from logistat.modele.integration import ModeleFactice


# ------------------------------------------------------------------ contrat
def test_aucune_fuite_dans_les_facteurs():
    assert not set(FACTEURS_COMMANDES) & set(FUITES_COMMANDES)
    for interdit in ("en_retard", "id_commande", "delai_reel_jours", "statut_livraison"):
        assert interdit not in FACTEURS_COMMANDES


@pytest.mark.parametrize("v", FUITES_COMMANDES + ["en_retard", "id_commande", "profit_commande"])
def test_variables_interdites_refusees(v):
    with pytest.raises(ErreurModele):
        verifier_variables(["mode_expedition", v])


def test_variable_inconnue_refusee():
    with pytest.raises(ErreurModele, match="inconnues"):
        verifier_variables(["n_existe_pas"])


def test_objet_sans_contrat_refuse():
    with pytest.raises(ErreurModele):
        verifier_modele(LogisticRegression())


def test_pipeline_sklearn_enveloppe(commandes):
    """Exemple de ce que livrera le bloc 3 : un Pipeline scikit-learn enveloppé."""
    variables = ["mode_expedition", "marche", "nb_articles"]
    prep = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), ["mode_expedition", "marche"])],
        remainder="passthrough",
    )
    modele = envelopper(make_pipeline(prep, LogisticRegression(max_iter=500)), "Essai", variables)
    pop = population_modelisation(commandes)
    modele.fit(pop[variables], pop["en_retard"])
    p = probabilite_retard(verifier_modele(modele), pop)
    assert p.shape == (len(pop),)
    assert ((p >= 0) & (p <= 1)).all()


def test_predict_proba_mal_formee(commandes):
    class Casse(ModeleFactice):
        def predict_proba(self, X):
            return np.ones(len(X))

    m = Casse().fit(commandes[["mode_expedition"]], commandes["en_retard"])
    with pytest.raises(ErreurModele, match=r"\(n, 2\)"):
        probabilite_retard(m, commandes)


# ------------------------------------------------------------------ découpage
def test_decoupage_chronologique_sans_chevauchement(commandes):
    d = decoupage_chronologique(commandes, "2017-01-01")
    assert d.apprentissage["date_commande"].max() < d.test["date_commande"].min()
    assert not set(d.apprentissage["id_commande"]) & set(d.test["id_commande"])
    assert len(d.apprentissage) + len(d.test) == len(commandes)
    assert set(d.resume().index) == {"apprentissage", "test"}


def test_decoupage_date_hors_donnees(commandes):
    with pytest.raises(ValueError, match="ensemble vide"):
        decoupage_chronologique(commandes, "2030-01-01")


# ------------------------------------------------------------------ métriques
def test_metriques_valeurs_connues():
    y = [True, True, False, False]
    p = [0.9, 0.4, 0.6, 0.1]
    m = evaluer(y, p)
    assert m["exactitude"] == pytest.approx(0.5)
    assert m["precision"] == pytest.approx(0.5)
    assert m["rappel"] == pytest.approx(0.5)
    assert m["roc_auc"] == pytest.approx(0.75)
    cm = matrice_confusion(y, p)
    assert cm.to_numpy().tolist() == [[1, 1], [1, 1]]
    assert courbe_roc(y, p)["rappel"].iloc[-1] == 1.0


# ------------------------------------------------------------------ stockage
def test_sauvegarde_et_liste(tmp_path, commandes):
    m = ModeleFactice().fit(commandes[["mode_expedition"]], commandes["en_retard"])
    chemin = stockage.sauvegarder(m, tmp_path)
    assert chemin.name == "factice_taux_moyen.joblib"
    assert stockage.lister(tmp_path) == {"Factice (taux moyen)": chemin}
    recharge = stockage.charger(chemin)
    np.testing.assert_allclose(
        probabilite_retard(recharge, commandes), probabilite_retard(m, commandes)
    )


def test_nom_de_fichier_sans_accents():
    assert stockage._nom_fichier("Régression logistique (L2)") == "regression_logistique_l2.joblib"


def test_fichier_abime_ignore(tmp_path):
    (tmp_path / "abime.joblib").write_bytes(b"pas un modele")
    assert stockage.lister(tmp_path) == {}


def test_indicateurs(commandes):
    from logistat.analyse.indicateurs import evolution_mensuelle, resume_global, taux_retard_par

    r = resume_global(commandes)
    assert r["commandes"] == len(commandes)
    t = taux_retard_par(commandes, "mode_expedition")
    assert t["commandes"].sum() == (~commandes["annulee"]).sum()
    assert t["taux_retard"].is_monotonic_decreasing
    e = evolution_mensuelle(commandes)
    assert isinstance(e["mois"].iloc[0], pd.Timestamp)
