# LogiStat — Analyse statistique et prédiction des retards de livraison

[![CI](https://github.com/ORGANISATION/logistat/actions/workflows/ci.yml/badge.svg)](https://github.com/ORGANISATION/logistat/actions/workflows/ci.yml)

LogiStat aide un responsable d'exploitation ou un analyste de performance logistique à
comprendre quels facteurs sont associés aux retards de livraison et à estimer la
probabilité qu'une commande arrive en retard.

> Projet de session — INF-5103 Concepts statistiques pour la science des données,
> Université du Québec en Outaouais, automne 2026.

## Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre dans le navigateur à l'adresse http://localhost:8501.
Les données préparées sont incluses dans le dépôt : aucun téléchargement n'est nécessaire.

## Installation (une seule fois)

Prérequis : Python 3.10 ou plus récent ([python.org](https://www.python.org/downloads/)).

```bash
git clone https://github.com/ORGANISATION/logistat.git
cd logistat
python -m venv .venv
```

| Système | Activer l'environnement |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

```bash
pip install -r requirements.txt
```

## Fonctionnalités

| Onglet | Contenu |
|---|---|
| Vue d'ensemble | Nombre de commandes, taux de retard, écart moyen au délai promis, évolution mensuelle |
| Facteurs de retard | Taux de retard selon le mode d'expédition, le marché, la région, le segment… |
| Prédiction | Probabilité de retard d'une commande décrite par l'utilisateur |
| Performance du modèle | Exactitude, précision, rappel, F1, ROC-AUC, matrice de confusion, courbe ROC sur des commandes postérieures à l'apprentissage |
| Données | Table filtrée, export CSV, dictionnaire des variables |

Filtres communs : période, marché, mode d'expédition.

## Données

DataCo Smart Supply Chain (Constante, Silva et Pereira, 2019, licence CC BY 4.0) :
65 752 commandes de 2015 à 2018. Détails, licence et régénération : [`data/README.md`](data/README.md) ;
dictionnaire des variables : [`docs/donnees.md`](docs/donnees.md).

## Architecture

```
app.py                      Interface Streamlit (bloc 1)
src/logistat/
├── config.py               Chemins, graine, date de coupure
├── donnees/                Contrat de données, préparation, chargement
├── analyse/                Statistiques descriptives et tests (bloc 2)
├── modele/                 Contrat modèle, découpage, métriques, stockage (bloc 3)
└── ui/graphiques.py        Graphiques Plotly
scripts/preparer_donnees.py CSV d'origine → data/prepare/
scripts/creer_issues.py     Crée les tâches B1.1 … B3.5 sur GitHub
modeles/                    Modèles entraînés (.joblib) livrés par le bloc 3
tests/                      Tests pytest (contrats, calculs, lancement de l'interface)
```

Contrats entre les blocs et choix communs : [`docs/architecture.md`](docs/architecture.md).

## Développement

```bash
pip install -r requirements-dev.txt
pre-commit install          # vérifications automatiques avant chaque commit
pytest                      # tests
ruff check . && ruff format .
```

Règles de travail en équipe : [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Équipe

| Membre | Bloc |
|---|---|
| Hermann Blondel Njeutsa | à confirmer |
| Moïse Armand Massack | à confirmer |
| Élisée Bertrand Lele Simo | Bloc 1 — Application, intégration et qualité |

## Licence

Code : MIT — voir [LICENSE](LICENSE). Données : CC BY 4.0, voir [`data/README.md`](data/README.md).
