"""Couche modèle : contrat avec le bloc 3, découpage, métriques et stockage."""

from logistat.modele.contrat import (
    ErreurModele,
    PredicteurRetard,
    envelopper,
    probabilite_retard,
    verifier_modele,
    verifier_variables,
)
from logistat.modele.decoupage import Decoupage, decoupage_chronologique
from logistat.modele.evaluation import courbe_roc, evaluer, matrice_confusion

__all__ = [
    "Decoupage",
    "ErreurModele",
    "PredicteurRetard",
    "courbe_roc",
    "decoupage_chronologique",
    "envelopper",
    "evaluer",
    "matrice_confusion",
    "probabilite_retard",
    "verifier_modele",
    "verifier_variables",
]
