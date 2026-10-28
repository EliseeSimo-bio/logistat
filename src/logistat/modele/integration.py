"""Modèle FACTICE servant uniquement à tester l'intégration de bout en bout.

Il prédit pour chaque commande le taux de retard observé en apprentissage, quelle que
soit la commande. Ce n'est PAS le modèle de référence du projet : le choix du modèle
de référence et du modèle avancé revient au bloc 3 (tâche B3.2).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class ModeleFactice:
    nom = "Factice (taux moyen)"
    variables = ["mode_expedition"]  # une variable autorisée, pour exercer le contrat

    def fit(self, X: pd.DataFrame, y: pd.Series) -> ModeleFactice:
        self.taux_ = float(np.mean(y))
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        p = np.full(len(X), self.taux_)
        return np.column_stack([1 - p, p])
