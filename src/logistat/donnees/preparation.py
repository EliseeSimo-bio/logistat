"""Préparation reproductible : CSV DataCo → tables ``lignes`` et ``commandes``.

Version de départ écrite par le bloc 1 pour fixer le format d'échange. Le bloc 2 la
complète (valeurs aberrantes, exclusions, variables dérivées) en gardant le même
schéma de sortie ; chaque règle ajoutée est documentée dans docs/donnees.md.

Unité d'analyse
---------------
DataCo contient une ligne par ARTICLE commandé (180 519), mais le mode d'expédition,
les délais et la cible sont identiques pour tous les articles d'une même commande
(65 752 commandes). La table ``commandes`` est donc l'unité recommandée pour la
modélisation : sinon, des articles d'une même commande se retrouvent à la fois en
apprentissage et en test.
"""

from __future__ import annotations

from pathlib import Path
from typing import IO

import numpy as np
import pandas as pd

from logistat.config import ENCODAGE_BRUT
from logistat.donnees import schema


class ErreurContrat(ValueError):
    """Les données ne respectent pas le contrat défini dans schema.py."""


# Colonnes identiques d'une ligne à l'autre au sein d'une commande
CONSTANTES_COMMANDE: tuple[str, ...] = (
    "id_client",
    "date_commande",
    "mode_expedition",
    "delai_prevu_jours",
    "type_paiement",
    "segment_client",
    "pays_client",
    "marche",
    "region_commande",
    "pays_commande",
    "ville_commande",
    "latitude_magasin",
    "longitude_magasin",
    "delai_reel_jours",
    "date_expedition",
    "statut_livraison",
    "statut_commande",
    "ecart_jours",
    "annulee",
    "en_retard",
)


# --------------------------------------------------------------------------- lecture
def lire_brut(source: str | Path | IO) -> pd.DataFrame:
    """Lit le CSV DataCo d'origine (encodage latin-1)."""
    try:
        return pd.read_csv(source, encoding=ENCODAGE_BRUT, low_memory=False)
    except FileNotFoundError as exc:
        raise ErreurContrat(
            f"Fichier introuvable : {source}. Placez DataCoSupplyChainDataset.csv dans data/brut/."
        ) from exc


# --------------------------------------------------------------------------- lignes
def preparer_lignes(brut: pd.DataFrame) -> pd.DataFrame:
    """Renomme, type et filtre les colonnes selon le schéma ; ajoute les colonnes dérivées."""
    brut = brut.rename(columns=lambda c: c.strip())
    manquantes = [s for s in schema.RENOMMAGE if s not in brut.columns]
    if manquantes:
        raise ErreurContrat("Colonnes absentes du CSV d'origine : " + ", ".join(manquantes))

    df = brut[list(schema.RENOMMAGE)].rename(columns=schema.RENOMMAGE)
    for col in ("date_commande", "date_expedition"):
        df[col] = pd.to_datetime(df[col], format="%m/%d/%Y %H:%M")
    df["ecart_jours"] = df["delai_reel_jours"] - df["delai_prevu_jours"]
    df["annulee"] = df["statut_livraison"].eq("Shipping canceled")
    df["en_retard"] = df["en_retard"].astype(bool)
    df["produit_indisponible"] = df["produit_indisponible"].astype(bool)
    df = df.sort_values(["date_commande", "id_commande", "id_ligne"]).reset_index(drop=True)
    return df[[c.nom for c in schema.COLONNES]]


# --------------------------------------------------------------------------- commandes
def agreger_commandes(lignes: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par commande.

    Règles (à valider par le bloc 2) :
    - colonnes constantes dans la commande : première valeur ;
    - montants, quantités et profit : somme ;
    - catégorie et rayon : ceux de l'article au montant le plus élevé ;
    - nombre d'articles et de produits distincts ajoutés comme facteurs.
    """
    g = lignes.groupby("id_commande", sort=False)
    constantes = g[list(CONSTANTES_COMMANDE)].first()
    sommes = g[["quantite", "ventes", "remise", "total_ligne", "profit_commande"]].sum()
    sommes = sommes.rename(columns={"total_ligne": "total_commande"})
    principal = lignes.loc[g["total_ligne"].idxmax(), ["id_commande", "categorie", "departement"]]
    principal = principal.set_index("id_commande").rename(
        columns={"categorie": "categorie_principale", "departement": "departement_principal"}
    )
    comptes = pd.DataFrame(
        {"nb_articles": g.size(), "nb_produits_distincts": g["id_produit"].nunique()}
    )
    cmd = constantes.join([sommes, principal, comptes]).reset_index()
    with np.errstate(divide="ignore", invalid="ignore"):
        cmd["taux_remise"] = np.where(cmd["ventes"] > 0, cmd["remise"] / cmd["ventes"], 0.0)
    cmd = cmd.sort_values(["date_commande", "id_commande"]).reset_index(drop=True)
    return cmd[list(COLONNES_COMMANDES)]


# Ordre et rôle des colonnes de la table commandes
ROLES_COMMANDES: dict[str, schema.Role] = {
    "id_commande": "identifiant",
    "id_client": "identifiant",
    "date_commande": "temps",
    "mode_expedition": "facteur",
    "delai_prevu_jours": "facteur",
    "type_paiement": "facteur",
    "segment_client": "facteur",
    "pays_client": "facteur",
    "marche": "facteur",
    "region_commande": "facteur",
    "pays_commande": "facteur",
    "ville_commande": "facteur",
    "latitude_magasin": "facteur",
    "longitude_magasin": "facteur",
    "categorie_principale": "facteur",
    "departement_principal": "facteur",
    "nb_articles": "facteur",
    "nb_produits_distincts": "facteur",
    "quantite": "facteur",
    "ventes": "facteur",
    "remise": "facteur",
    "taux_remise": "facteur",
    "total_commande": "facteur",
    "profit_commande": "autre",
    "delai_reel_jours": "fuite",
    "date_expedition": "fuite",
    "statut_livraison": "fuite",
    "statut_commande": "fuite",
    "ecart_jours": "fuite",
    "annulee": "fuite",
    "en_retard": "cible",
}
COLONNES_COMMANDES: tuple[str, ...] = tuple(ROLES_COMMANDES)
FACTEURS_COMMANDES: list[str] = [c for c, r in ROLES_COMMANDES.items() if r == "facteur"]
FUITES_COMMANDES: list[str] = [c for c, r in ROLES_COMMANDES.items() if r == "fuite"]


# --------------------------------------------------------------------------- validation
def valider(df: pd.DataFrame, niveau: str = "commandes") -> pd.DataFrame:
    """Vérifie le contrat ; lève ErreurContrat avec un message clair sinon."""
    attendues = COLONNES_COMMANDES if niveau == "commandes" else [c.nom for c in schema.COLONNES]
    manquantes = [c for c in attendues if c not in df.columns]
    if manquantes:
        raise ErreurContrat(f"Colonnes manquantes ({niveau}) : " + ", ".join(manquantes))
    cle = "id_commande" if niveau == "commandes" else "id_ligne"
    if df[cle].duplicated().any():
        raise ErreurContrat(f"Doublons dans {cle}.")
    if not pd.api.types.is_datetime64_any_dtype(df["date_commande"]):
        raise ErreurContrat("date_commande doit être de type date.")
    if df["date_commande"].isna().any():
        raise ErreurContrat("date_commande contient des valeurs manquantes.")
    if not df["en_retard"].isin([True, False]).all():
        raise ErreurContrat("en_retard doit valoir vrai ou faux.")
    if (df["delai_prevu_jours"] < 0).any() or (df["delai_reel_jours"] < 0).any():
        raise ErreurContrat("Les délais doivent être positifs ou nuls.")
    incoherent = df["en_retard"] & df["annulee"]
    if incoherent.any():
        raise ErreurContrat(f"{int(incoherent.sum())} commandes à la fois annulées et en retard.")
    return df


def population_modelisation(commandes: pd.DataFrame, exclure_annulees: bool = True) -> pd.DataFrame:
    """Commandes retenues pour entraîner et évaluer un modèle."""
    return commandes[~commandes["annulee"]] if exclure_annulees else commandes
