import pandas as pd
import pytest

from conftest import brut_minimal
from logistat.config import FICHIER_COMMANDES
from logistat.donnees import (
    COLONNES_COMMANDES,
    ErreurContrat,
    agreger_commandes,
    charger_commandes,
    population_modelisation,
    preparer_lignes,
    schema,
    valider,
)


def test_preparation_renomme_et_supprime_donnees_personnelles():
    lignes = preparer_lignes(brut_minimal())
    assert list(lignes.columns) == [c.nom for c in schema.COLONNES]
    for interdit in (
        "Customer Email",
        "Customer Fname",
        "Customer Lname",
        "Customer Password",
        "Customer Street",
        "email",
        "nom_client",
    ):
        assert interdit not in lignes.columns


def test_preparation_types_et_derivees():
    lignes = preparer_lignes(brut_minimal())
    assert pd.api.types.is_datetime64_any_dtype(lignes["date_commande"])
    assert lignes["en_retard"].dtype == bool
    row = lignes.set_index("id_ligne").loc[1]
    assert row["ecart_jours"] == 1
    assert not row["annulee"]
    assert lignes.set_index("id_ligne").loc[3, "annulee"]


def test_preparation_colonne_manquante():
    with pytest.raises(ErreurContrat, match="Shipping Mode"):
        preparer_lignes(brut_minimal().drop(columns=["Shipping Mode"]))


def test_agregation_par_commande():
    cmd = agreger_commandes(preparer_lignes(brut_minimal())).set_index("id_commande")
    assert list(cmd.reset_index().columns) == list(COLONNES_COMMANDES)
    c100 = cmd.loc[100]
    assert c100["nb_articles"] == 2
    assert c100["quantite"] == 3
    assert c100["total_commande"] == pytest.approx(290.0)
    assert c100["taux_remise"] == pytest.approx(10 / 300)
    assert c100["categorie_principale"] == "Golf Balls"  # article au montant le plus élevé
    assert c100["profit_commande"] == pytest.approx(60.0)


def test_agregation_tri_chronologique():
    cmd = agreger_commandes(preparer_lignes(brut_minimal()))
    assert cmd["date_commande"].is_monotonic_increasing


def test_validation_detecte_incoherence():
    cmd = agreger_commandes(preparer_lignes(brut_minimal()))
    valider(cmd)
    casse = cmd.copy()
    casse.loc[casse["annulee"], "en_retard"] = True
    with pytest.raises(ErreurContrat, match="annulées et en retard"):
        valider(casse)
    with pytest.raises(ErreurContrat, match="Doublons"):
        valider(pd.concat([cmd, cmd]))


def test_population_exclut_annulees():
    cmd = agreger_commandes(preparer_lignes(brut_minimal()))
    assert len(population_modelisation(cmd)) == 1
    assert len(population_modelisation(cmd, exclure_annulees=False)) == 2


def test_echantillon_respecte_le_contrat(commandes):
    valider(commandes)
    assert len(commandes) == 3000


def test_chargement_repli_sur_echantillon(tmp_path):
    jeu = charger_commandes(fichier=tmp_path / "absent.parquet")
    assert not jeu.complet
    assert len(jeu.commandes) == 3000


def test_chargement_sans_donnees(tmp_path):
    with pytest.raises(ErreurContrat, match="preparer_donnees"):
        charger_commandes(fichier=tmp_path / "a.parquet", echantillon=tmp_path / "b.csv")


@pytest.mark.donnees_completes
@pytest.mark.skipif(not FICHIER_COMMANDES.exists(), reason="jeu complet non préparé")
def test_jeu_complet():
    jeu = charger_commandes()
    assert jeu.complet
    assert len(jeu.commandes) == 65_752
