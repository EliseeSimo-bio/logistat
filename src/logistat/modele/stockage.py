"""Sauvegarde et chargement des modèles entraînés (dossier modeles/).

Le bloc 3 entraîne un modèle puis appelle ``sauvegarder(modele)``. L'application
affiche automatiquement tous les modèles présents dans modeles/, sans modification
de son code.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import joblib

from logistat.config import DOSSIER_MODELES
from logistat.modele.contrat import PredicteurRetard, verifier_modele


def _nom_fichier(nom: str) -> str:
    sans_accents = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", sans_accents.lower()).strip("_")
    return f"{slug or 'modele'}.joblib"


def sauvegarder(modele: PredicteurRetard, dossier: Path = DOSSIER_MODELES) -> Path:
    verifier_modele(modele)
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / _nom_fichier(modele.nom)
    joblib.dump(modele, chemin)
    return chemin


def charger(chemin: Path) -> PredicteurRetard:
    return verifier_modele(joblib.load(chemin))


def lister(dossier: Path = DOSSIER_MODELES) -> dict[str, Path]:
    """Modèles disponibles : {nom affiché: chemin}."""
    if not dossier.exists():
        return {}
    out: dict[str, Path] = {}
    for chemin in sorted(dossier.glob("*.joblib")):
        try:
            out[charger(chemin).nom] = chemin
        except Exception:  # noqa: BLE001 — un fichier abîmé ne doit pas bloquer l'interface
            continue
    return out
