"""Point d'entrée unique pour obtenir les données dans l'application, les notebooks
et les modèles : ``charger_commandes()``.

Ordre de recherche :
1. data/prepare/commandes.parquet (jeu complet, produit par scripts/preparer_donnees.py) ;
2. data/echantillon/commandes_echantillon.csv (versionné, sert aux tests et à la CI).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from logistat.config import FICHIER_COMMANDES, FICHIER_ECHANTILLON
from logistat.donnees.preparation import ErreurContrat, valider


@dataclass(frozen=True)
class JeuDeDonnees:
    commandes: pd.DataFrame
    source: Path
    complet: bool  # False si l'on travaille sur l'échantillon


def lire_commandes_csv(chemin: str | Path) -> pd.DataFrame:
    df = pd.read_csv(chemin, parse_dates=["date_commande", "date_expedition"])
    for col in ("en_retard", "annulee"):
        df[col] = df[col].astype(bool)
    return df


def charger_commandes(fichier: Path | None = None, echantillon: Path | None = None) -> JeuDeDonnees:
    fichier = fichier or FICHIER_COMMANDES
    echantillon = echantillon or FICHIER_ECHANTILLON
    if fichier.exists():
        return JeuDeDonnees(valider(pd.read_parquet(fichier)), fichier, True)
    if echantillon.exists():
        return JeuDeDonnees(valider(lire_commandes_csv(echantillon)), echantillon, False)
    raise ErreurContrat(
        "Aucune donnée trouvée. Lancez : python scripts/preparer_donnees.py (voir data/README.md)."
    )
