# Données

## Source

**DataCo Smart Supply Chain for Big Data Analysis** — Constante F., Silva F., Pereira A.
(2019). Mendeley Data, version 5. https://doi.org/10.17632/8gx2fvg2k6.5
Licence **CC BY 4.0** : réutilisation et redistribution autorisées avec citation de la source.

Commandes d'une entreprise fictive d'articles de sport (DataCo Global), de janvier 2015
à janvier 2018, livrées dans 164 pays.

## Fichiers

| Dossier | Contenu | Versionné ? |
|---|---|---|
| `brut/` | `DataCoSupplyChainDataset.csv` d'origine (95 Mo, latin-1) | **non** (trop lourd pour GitHub) |
| `prepare/lignes.parquet` | 180 519 articles, colonnes du schéma, sans données personnelles | oui |
| `prepare/commandes.parquet` | 65 752 commandes (unité de modélisation) | oui |
| `echantillon/commandes_echantillon.csv` | 3 000 commandes tirées au hasard (graine 42), pour les tests et la CI | oui |

Les fichiers préparés suffisent pour lancer l'application. Pour les régénérer :

1. télécharger l'archive depuis la page Mendeley ci-dessus ;
2. placer `DataCoSupplyChainDataset.csv` dans `data/brut/` ;
3. lancer `python scripts/preparer_donnees.py`.

## Fichiers de l'archive non utilisés

- `DescriptionDataCoSupplyChain.csv` : dictionnaire d'origine (repris et traduit dans
  `docs/donnees.md`).
- `tokenized_access_logs.csv` : journaux de navigation du site web (produit consulté,
  heure, adresse IP). Aucune clé ne les relie aux commandes ; non utilisés.
