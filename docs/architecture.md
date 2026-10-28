# Architecture de LogiStat

## Vue en couches et responsabilités

```
                 ┌──────────────────── app.py (Streamlit) ── bloc 1 ─────────────────────┐
                 │ filtres · Vue d'ensemble · Facteurs · Prédiction · Performance · Données │
                 └───────┬───────────────────────┬───────────────────────┬──────────────┘
                         │                       │                       │
   ┌─────────────────────▼─────┐   ┌─────────────▼────────────┐   ┌──────▼──────────────┐
   │ donnees/   (bloc 2 + 1)    │   │ analyse/   (bloc 2)       │   │ modele/  (bloc 3 + 1)│
   │ schema.py  ← CONTRAT       │   │ indicateurs, tests,       │   │ contrat.py ← CONTRAT │
   │ preparation.py             │──►│ distributions…            │   │ decoupage, evaluation│
   │ chargement.py              │   └───────────────────────────┘   │ stockage → modeles/  │
   └────────────────────────────┘                                   └──────────────────────┘
          ▲                                                                   ▲
   scripts/preparer_donnees.py                                   notebooks / scripts du bloc 3
```

Règle : `app.py` n'effectue aucun calcul. Il appelle des fonctions de `analyse/` et
`modele/`, testées séparément.

## Contrat 1 — données (bloc 2 → blocs 1 et 3)

- Point d'entrée unique : `charger_commandes()` renvoie la table `commandes`
  (une ligne par commande), validée par `valider()`.
- Toute colonne a un **rôle** (`docs/donnees.md`). Seules les colonnes de rôle
  `facteur` peuvent entrer dans un modèle.
- Le bloc 2 peut ajouter des règles de nettoyage dans `preparation.py`, sans changer
  les noms ni les rôles existants sans accord de l'équipe (pull request relue).

## Contrat 2 — modèle (bloc 3 → bloc 1)

Un modèle est un objet avec :

| Élément | Exigence |
|---|---|
| `nom` | texte affiché dans l'interface |
| `variables` | liste de colonnes de `commandes`, toutes de rôle `facteur` |
| `fit(X, y)` | `X = commandes[variables]`, `y = commandes["en_retard"]` |
| `predict_proba(X)` | tableau `(n, 2)` ; colonne 1 = probabilité de retard |

Un `Pipeline` scikit-learn convient : `envelopper(pipeline, nom, variables)`. Le bloc 3
appelle `stockage.sauvegarder(modele)` ; le fichier `.joblib` apparaît dans `modeles/`
et l'application l'affiche dans « Prédiction » et « Performance », sans modification de code.

Exemple minimal (bloc 3) :

```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from logistat.donnees import charger_commandes, population_modelisation
from logistat.modele import decoupage_chronologique, envelopper, evaluer, probabilite_retard
from logistat.modele import stockage

pop = population_modelisation(charger_commandes().commandes)
d = decoupage_chronologique(pop)

variables = ["mode_expedition", "marche", "type_paiement", "nb_articles"]
prep = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), variables[:3])], remainder="passthrough"
)
modele = envelopper(
    make_pipeline(prep, LogisticRegression(max_iter=1000)), "Régression logistique", variables
)
modele.fit(d.apprentissage[variables], d.apprentissage["en_retard"])
print(evaluer(d.test["en_retard"], probabilite_retard(modele, d.test)))
stockage.sauvegarder(modele)
```

## Choix communs (à valider par l'équipe)

| Choix | Valeur proposée | Où le changer | Qui valide |
|---|---|---|---|
| Unité de modélisation | la commande | `preparation.agreger_commandes` | blocs 2 et 3 |
| Commandes annulées | exclues de la modélisation | `config.EXCLURE_ANNULEES` | blocs 2 et 3 |
| Découpage | chronologique, coupure au 2017-07-01 | `config.DATE_COUPURE` | bloc 3 |
| Seuil de décision | 0,5 par défaut, réglable dans l'interface | — | bloc 3 |

## Faits établis lors de la préparation (à interpréter par les blocs 2 et 3)

- 65 752 commandes, 2 855 annulées ; 57,3 % des commandes livrées sont en retard.
- Le délai prévu est entièrement déterminé par le mode d'expédition
  (Same Day 0 j, First Class 1 j, Second Class 2 j, Standard Class 4 j).
- Taux de retard des commandes livrées par mode : First Class 100 %, Second Class 80 %,
  Same Day 48 %, Standard Class 40 %.
- Rupture en octobre 2017 : les commandes ne contiennent plus qu'un article en moyenne
  (1,0 contre 3,0 de janvier 2015 à septembre 2017), et le nombre de commandes par mois
  passe d'environ 1 750 à 2 100. Avec la coupure au 2017-07-01, l'ensemble de test
  contient 4 mois de ce nouveau régime : à prendre en compte dans le choix de la date de
  coupure et des variables (`nb_articles`, `quantite`, montants).
- Les données s'arrêtent le 31 janvier 2018.
