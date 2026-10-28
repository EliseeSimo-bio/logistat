"""Crée sur GitHub une issue par tâche du plan de réalisation (B1.1 … B3.5).

Prérequis : GitHub CLI installé et connecté (https://cli.github.com, puis `gh auth login`).

    python scripts/creer_issues.py              # aperçu, ne crée rien
    python scripts/creer_issues.py --creer      # crée les étiquettes et les issues

Les issues créées peuvent ensuite être ajoutées à un tableau GitHub Projects.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess

BLOCS = {
    "bloc-1": ("Bloc 1 — Application, intégration et qualité", "1d76db"),
    "bloc-2": ("Bloc 2 — Données et analyse statistique", "0e8a16"),
    "bloc-3": ("Bloc 3 — Modélisation prédictive et validation", "d93f0b"),
}

# (identifiant, étiquette, titre, heures, échéance, critère de fin)
TACHES = [
    (
        "B1.1",
        "bloc-1",
        "Architecture, configuration GitHub et environnement Python",
        4,
        "2026-10-29",
        "Dépôt public, contrats de données et de modèle, CI verte",
    ),
    (
        "B1.2",
        "bloc-1",
        "Interface Streamlit, tableaux de bord, filtres et graphiques",
        12,
        "2026-11-05",
        "Tous les onglets alimentés par les données réelles",
    ),
    (
        "B1.3",
        "bloc-1",
        "Intégration des analyses et prédictions",
        6,
        "2026-11-08",
        "Analyses du bloc 2 et modèles du bloc 3 visibles dans l'application",
    ),
    (
        "B1.4",
        "bloc-1",
        "Tests, corrections, README et lancement local",
        6,
        "2026-11-12",
        "Lancement par commande unique vérifié sur une machine propre",
    ),
    (
        "B2.1",
        "bloc-2",
        "Recherche et sélection d'un jeu de données pertinent",
        5,
        "2026-10-29",
        "Source, licence et limites documentées dans data/README.md",
    ),
    (
        "B2.2",
        "bloc-2",
        "Nettoyage, valeurs manquantes et préparation",
        7,
        "2026-11-01",
        "Règles ajoutées à preparation.py, testées et listées dans docs/donnees.md",
    ),
    (
        "B2.3",
        "bloc-2",
        "Analyse descriptive, distributions et corrélations",
        8,
        "2026-11-04",
        "Fonctions dans src/logistat/analyse/, testées",
    ),
    (
        "B2.4",
        "bloc-2",
        "Visualisations et interprétation des résultats",
        5,
        "2026-11-06",
        "Graphiques intégrés à l'onglet Facteurs ; interprétation rédigée",
    ),
    (
        "B2.5",
        "bloc-2",
        "Rédaction des sections données et analyses",
        3,
        "2026-11-10",
        "Sections du rapport relues",
    ),
    (
        "B3.1",
        "bloc-3",
        "Définition de la cible et des variables prédictives",
        4,
        "2026-10-30",
        "Liste des variables validée (rôle « facteur » uniquement)",
    ),
    (
        "B3.2",
        "bloc-3",
        "Développement d'un modèle de référence et d'un modèle avancé",
        9,
        "2026-11-05",
        "Deux modèles sauvegardés dans modeles/ via stockage.sauvegarder()",
    ),
    (
        "B3.3",
        "bloc-3",
        "Évaluation, validation et comparaison des modèles",
        8,
        "2026-11-07",
        "Métriques sur le découpage chronologique ; comparaison justifiée",
    ),
    (
        "B3.4",
        "bloc-3",
        "Interprétation des performances et limites",
        4,
        "2026-11-09",
        "Limites et incertitudes rédigées",
    ),
    (
        "B3.5",
        "bloc-3",
        "Rédaction de la méthodologie prédictive",
        3,
        "2026-11-10",
        "Section du rapport relue",
    ),
]


def gh(*args: str) -> None:
    subprocess.run(["gh", *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--creer", action="store_true", help="créer réellement sur GitHub")
    args = parser.parse_args()

    for ident, _bloc, titre, heures, echeance, _fin in TACHES:
        print(f"[{ident}] {titre} — {heures} h — échéance {echeance}")
    if not args.creer:
        print("\nAperçu seulement. Relancez avec --creer pour créer les issues.")
        return
    if shutil.which("gh") is None:
        raise SystemExit("GitHub CLI (gh) introuvable : https://cli.github.com")

    for nom, (description, couleur) in BLOCS.items():
        gh("label", "create", nom, "--description", description, "--color", couleur, "--force")
    gh("label", "create", "tâche", "--color", "c5def5", "--force")

    for ident, bloc, titre, heures, echeance, fin in TACHES:
        corps = (
            f"**Bloc et identifiant** : {ident}\n\n"
            f"**Temps estimé** : {heures} h\n\n"
            f"**Échéance** : {echeance}\n\n"
            f"**Terminé quand**\n- [ ] {fin}\n\n"
            "**Responsable** : à assigner\n"
        )
        gh(
            "issue",
            "create",
            "--title",
            f"{ident} — {titre}",
            "--body",
            corps,
            "--label",
            bloc,
            "--label",
            "tâche",
        )


if __name__ == "__main__":
    main()
