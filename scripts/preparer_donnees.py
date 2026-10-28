"""Prépare le jeu DataCo pour LogiStat (commande unique, reproductible).

    python scripts/preparer_donnees.py

Entrée  : data/brut/DataCoSupplyChainDataset.csv (à télécharger, voir data/README.md)
Sorties : data/prepare/lignes.parquet       (1 ligne = 1 article)
          data/prepare/commandes.parquet    (1 ligne = 1 commande)
          data/echantillon/commandes_echantillon.csv (3 000 commandes, pour tests et CI)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from logistat.config import (
    FICHIER_BRUT,
    FICHIER_COMMANDES,
    FICHIER_ECHANTILLON,
    FICHIER_LIGNES,
    GRAINE,
)
from logistat.donnees import agreger_commandes, lire_brut, preparer_lignes, valider

TAILLE_ECHANTILLON = 3_000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--brut", type=Path, default=FICHIER_BRUT, help="CSV DataCo d'origine")
    args = parser.parse_args()

    print(f"Lecture de {args.brut} …")
    brut = lire_brut(args.brut)
    lignes = valider(preparer_lignes(brut), niveau="lignes")
    commandes = valider(agreger_commandes(lignes), niveau="commandes")

    FICHIER_LIGNES.parent.mkdir(parents=True, exist_ok=True)
    lignes.to_parquet(FICHIER_LIGNES, index=False)
    commandes.to_parquet(FICHIER_COMMANDES, index=False)

    echantillon = commandes.sample(TAILLE_ECHANTILLON, random_state=GRAINE).sort_values(
        ["date_commande", "id_commande"]
    )
    FICHIER_ECHANTILLON.parent.mkdir(parents=True, exist_ok=True)
    echantillon.to_csv(FICHIER_ECHANTILLON, index=False)

    print(f"  {len(brut):>7} lignes lues")
    print(f"  {len(lignes):>7} articles  → {FICHIER_LIGNES}")
    print(f"  {len(commandes):>7} commandes → {FICHIER_COMMANDES}")
    print(f"  {len(echantillon):>7} commandes → {FICHIER_ECHANTILLON}")
    print(f"  Taux de retard (commandes) : {commandes['en_retard'].mean():.1%}")


if __name__ == "__main__":
    main()
