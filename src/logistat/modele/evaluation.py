"""Métriques communes : le bloc 3 et l'application calculent exactement les mêmes."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn import metrics


def evaluer(y_vrai, proba_retard, seuil: float = 0.5) -> dict[str, float]:
    """Métriques de classification pour un seuil de décision donné."""
    y = np.asarray(y_vrai, dtype=bool)
    p = np.asarray(proba_retard, dtype=float)
    pred = p >= seuil
    deux_classes = len(np.unique(y)) == 2
    return {
        "exactitude": metrics.accuracy_score(y, pred),
        "precision": metrics.precision_score(y, pred, zero_division=0),
        "rappel": metrics.recall_score(y, pred, zero_division=0),
        "f1": metrics.f1_score(y, pred, zero_division=0),
        "roc_auc": metrics.roc_auc_score(y, p) if deux_classes else float("nan"),
        "brier": metrics.brier_score_loss(y, p),
    }


def matrice_confusion(y_vrai, proba_retard, seuil: float = 0.5) -> pd.DataFrame:
    y = np.asarray(y_vrai, dtype=bool)
    pred = np.asarray(proba_retard) >= seuil
    m = metrics.confusion_matrix(y, pred, labels=[False, True])
    return pd.DataFrame(
        m,
        index=pd.Index(["Réel : à temps", "Réel : en retard"]),
        columns=pd.Index(["Prédit : à temps", "Prédit : en retard"]),
    )


def courbe_roc(y_vrai, proba_retard) -> pd.DataFrame:
    fpr, tpr, seuils = metrics.roc_curve(np.asarray(y_vrai, dtype=bool), proba_retard)
    return pd.DataFrame({"taux_faux_positifs": fpr, "rappel": tpr, "seuil": seuils})
