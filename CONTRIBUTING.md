# Travailler sur LogiStat

## Branches et pull requests

- `main` est protégée : on n'y pousse jamais directement.
- Une branche par tâche, préfixée par son identifiant : `b2.2-valeurs-manquantes`,
  `b3.2-regression-logistique`, `b1.2-onglet-facteurs`.
- On fusionne par *pull request* une fois la CI verte et la relecture d'un autre membre
  faite. La relecture sert aussi la défense individuelle : chacun doit pouvoir expliquer
  tout le code.

```bash
git switch main && git pull
git switch -c b2.2-valeurs-manquantes
# … modifications …
pytest && ruff check .
git add -A && git commit -m "feat(donnees): exclut les commandes sans date"
git push -u origin b2.2-valeurs-manquantes
# Ouvrir la pull request sur GitHub et lier l'issue (« closes #7 »)
```

Préfixes de commit : `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, avec la zone
entre parenthèses : `(donnees)`, `(analyse)`, `(modele)`, `(ui)`.

## Où mettre son travail

| Bloc | Vous ajoutez… | Fichier | Test obligatoire |
|---|---|---|---|
| 2 | une règle de nettoyage | `src/logistat/donnees/preparation.py` + ligne dans `docs/donnees.md` | oui |
| 2 | une analyse (distribution, test, corrélation) | `src/logistat/analyse/<theme>.py` | oui |
| 2 | une exploration | `notebooks/` (ne fait pas partie de l'application) | non |
| 3 | un modèle | notebook ou `scripts/entrainer_<nom>.py`, puis `stockage.sauvegarder()` | le test de contrat suffit |
| 3 | une métrique | `src/logistat/modele/evaluation.py` | oui |
| 1 | un écran, un filtre, un graphique | `app.py`, `src/logistat/ui/graphiques.py` | le test de fumée doit passer |

Règles :

- **Aucun calcul dans `app.py`** : l'interface appelle des fonctions testées.
- **Aucune variable de fuite dans un modèle** : seules les colonnes de rôle « facteur »
  sont acceptées (`docs/donnees.md`). Le test de contrat bloque la CI sinon.
- **Changer un nom ou un rôle de colonne** = pull request relue par les trois membres :
  les trois blocs en dépendent.
- Paramètres partagés (date de coupure, graine, exclusion des annulées) : dans
  `src/logistat/config.py`, jamais en dur dans le code.

## Suivi des tâches

`python scripts/creer_issues.py --creer` crée une issue par tâche du plan (B1.1 à B3.5).
Ajoutez-les à un tableau GitHub Projects avec les colonnes À faire / En cours /
À valider / Terminé.

## Intelligence artificielle

Le plan de cours exige de déclarer en annexe toute génération de code ou aide à la
rédaction (outil, portion, raison). Notez-le dans la section prévue de chaque pull
request ; on compilera ces notes à la fin. L'analyse, l'interprétation et les
recommandations au client sont rédigées par l'équipe.
