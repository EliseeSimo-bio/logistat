"""Indicateurs de base, nécessaires à la coquille de l'interface (bloc 1).

Le bloc 2 ajoute ici ses analyses (distributions, tests, corrélations) en suivant la
même forme : une fonction pure, documentée et testée.
"""

from __future__ import annotations

import pandas as pd


def resume_global(commandes: pd.DataFrame) -> dict[str, float]:
    livrees = commandes[~commandes["annulee"]]
    return {
        "commandes": len(commandes),
        "annulees": int(commandes["annulee"].sum()),
        "taux_retard": float(livrees["en_retard"].mean()) if len(livrees) else float("nan"),
        "ecart_moyen_jours": float(livrees["ecart_jours"].mean()) if len(livrees) else float("nan"),
    }


def taux_retard_par(commandes: pd.DataFrame, colonne: str) -> pd.DataFrame:
    """Nombre de commandes livrées et proportion en retard, par modalité de ``colonne``."""
    livrees = commandes[~commandes["annulee"]]
    out = livrees.groupby(colonne, observed=True)["en_retard"].agg(
        commandes="size", taux_retard="mean"
    )
    return out.sort_values("taux_retard", ascending=False).reset_index()


def evolution_mensuelle(commandes: pd.DataFrame) -> pd.DataFrame:
    livrees = commandes[~commandes["annulee"]]
    mois = livrees["date_commande"].dt.to_period("M").dt.to_timestamp()
    out = livrees.groupby(mois)["en_retard"].agg(commandes="size", taux_retard="mean")
    out.index.name = "mois"
    return out.reset_index()
