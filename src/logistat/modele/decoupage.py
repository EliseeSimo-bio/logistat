"""Découpage apprentissage / test commun à tout le projet.

Proposition du bloc 1, à valider par le bloc 3 : découpage CHRONOLOGIQUE.
Le modèle apprend sur les commandes passées avant ``date_coupure`` et il est évalué
sur les suivantes, comme il le serait en production. Comme la table est au niveau de
la commande, aucune commande ne peut se trouver des deux côtés.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from logistat.config import DATE_COUPURE


@dataclass(frozen=True)
class Decoupage:
    apprentissage: pd.DataFrame
    test: pd.DataFrame
    date_coupure: pd.Timestamp

    def resume(self) -> pd.DataFrame:
        lignes = []
        for nom, d in (("apprentissage", self.apprentissage), ("test", self.test)):
            lignes.append(
                {
                    "ensemble": nom,
                    "commandes": len(d),
                    "du": d["date_commande"].min(),
                    "au": d["date_commande"].max(),
                    "taux_retard": d["en_retard"].mean(),
                }
            )
        return pd.DataFrame(lignes).set_index("ensemble")


def decoupage_chronologique(
    commandes: pd.DataFrame, date_coupure: str | pd.Timestamp = DATE_COUPURE
) -> Decoupage:
    coupure = pd.Timestamp(date_coupure)
    avant = commandes["date_commande"] < coupure
    app, test = commandes[avant], commandes[~avant]
    if app.empty or test.empty:
        raise ValueError(
            f"La date de coupure {coupure:%Y-%m-%d} laisse un ensemble vide "
            f"(données du {commandes['date_commande'].min():%Y-%m-%d} "
            f"au {commandes['date_commande'].max():%Y-%m-%d})."
        )
    return Decoupage(app, test, coupure)
