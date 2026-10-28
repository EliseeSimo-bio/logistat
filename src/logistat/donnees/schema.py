"""Contrat de données de LogiStat (source : DataCo Smart Supply Chain).

Chaque colonne du jeu préparé a un nom canonique en français, un type et un RÔLE :

- ``identifiant`` : clé technique, jamais une variable explicative ;
- ``temps``       : date connue au moment de la commande ;
- ``facteur``     : connu au moment de la commande → peut entrer dans un modèle ;
- ``fuite``       : connu seulement APRÈS l'expédition → interdit dans un modèle,
                    autorisé dans les analyses descriptives ;
- ``cible``       : la variable à prédire ;
- ``autre``       : conservé pour l'analyse, hors modèle par défaut (à discuter).

Les colonnes du CSV d'origine absentes de ce schéma sont supprimées à la préparation :
données personnelles (courriel, nom, mot de passe masqué, adresse), doublons exacts
d'autres colonnes, colonne vide.

Ce fichier est la référence commune des trois blocs : toute nouvelle colonne passe
par lui (et par une pull request relue).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["identifiant", "temps", "facteur", "fuite", "cible", "autre"]


@dataclass(frozen=True)
class Colonne:
    nom: str  # nom canonique dans LogiStat
    source: str | None  # nom dans le CSV DataCo (None = colonne dérivée)
    role: Role
    type: Literal["entier", "reel", "texte", "date", "booleen"]
    description: str


COLONNES: tuple[Colonne, ...] = (
    # --- identifiants
    Colonne("id_commande", "Order Id", "identifiant", "entier", "Numéro de la commande"),
    Colonne("id_ligne", "Order Item Id", "identifiant", "entier", "Numéro de la ligne (article)"),
    Colonne("id_client", "Customer Id", "identifiant", "entier", "Numéro du client"),
    Colonne("id_produit", "Product Card Id", "identifiant", "entier", "Numéro du produit"),
    # --- temps
    Colonne(
        "date_commande", "order date (DateOrders)", "temps", "date", "Date et heure de la commande"
    ),
    # --- facteurs connus à la commande
    Colonne(
        "mode_expedition",
        "Shipping Mode",
        "facteur",
        "texte",
        "Standard Class, Second Class, First Class, Same Day",
    ),
    Colonne(
        "delai_prevu_jours",
        "Days for shipment (scheduled)",
        "facteur",
        "entier",
        "Délai de livraison promis (jours)",
    ),
    Colonne("type_paiement", "Type", "facteur", "texte", "DEBIT, TRANSFER, PAYMENT, CASH"),
    Colonne(
        "segment_client", "Customer Segment", "facteur", "texte", "Consumer, Corporate, Home Office"
    ),
    Colonne(
        "pays_client",
        "Customer Country",
        "facteur",
        "texte",
        "Pays du client (EE. UU., Puerto Rico)",
    ),
    Colonne("marche", "Market", "facteur", "texte", "Africa, Europe, LATAM, Pacific Asia, USCA"),
    Colonne("region_commande", "Order Region", "facteur", "texte", "Région de destination"),
    Colonne("pays_commande", "Order Country", "facteur", "texte", "Pays de destination"),
    Colonne("ville_commande", "Order City", "facteur", "texte", "Ville de destination"),
    Colonne("departement", "Department Name", "facteur", "texte", "Rayon du magasin"),
    Colonne("categorie", "Category Name", "facteur", "texte", "Catégorie du produit"),
    Colonne("produit", "Product Name", "facteur", "texte", "Nom du produit"),
    Colonne(
        "prix_unitaire", "Order Item Product Price", "facteur", "reel", "Prix avant remise ($)"
    ),
    Colonne("quantite", "Order Item Quantity", "facteur", "entier", "Quantité commandée"),
    Colonne("remise", "Order Item Discount", "facteur", "reel", "Montant de la remise ($)"),
    Colonne("taux_remise", "Order Item Discount Rate", "facteur", "reel", "Remise en proportion"),
    Colonne("ventes", "Sales", "facteur", "reel", "Montant avant remise ($)"),
    Colonne("total_ligne", "Order Item Total", "facteur", "reel", "Montant après remise ($)"),
    Colonne("latitude_magasin", "Latitude", "facteur", "reel", "Latitude du magasin"),
    Colonne("longitude_magasin", "Longitude", "facteur", "reel", "Longitude du magasin"),
    # --- autres (hors modèle par défaut)
    Colonne(
        "profit_commande",
        "Order Profit Per Order",
        "autre",
        "reel",
        "Profit ($) ; peut dépendre d'événements postérieurs (fraude, annulation)",
    ),
    Colonne("ratio_profit", "Order Item Profit Ratio", "autre", "reel", "Profit / ventes"),
    Colonne(
        "produit_indisponible",
        "Product Status",
        "autre",
        "booleen",
        "1 = produit indisponible (toujours 0 dans DataCo)",
    ),
    # --- connus après l'expédition : FUITE
    Colonne(
        "delai_reel_jours",
        "Days for shipping (real)",
        "fuite",
        "entier",
        "Délai réel de livraison (jours)",
    ),
    Colonne("date_expedition", "shipping date (DateOrders)", "fuite", "date", "Date d'expédition"),
    Colonne(
        "statut_livraison",
        "Delivery Status",
        "fuite",
        "texte",
        "Advance shipping, Late delivery, Shipping on time, Shipping canceled",
    ),
    Colonne(
        "statut_commande",
        "Order Status",
        "fuite",
        "texte",
        "COMPLETE, PENDING, CANCELED, SUSPECTED_FRAUD…",
    ),
    Colonne("ecart_jours", None, "fuite", "entier", "delai_reel_jours − delai_prevu_jours"),
    Colonne("annulee", None, "fuite", "booleen", "statut_livraison = Shipping canceled"),
    # --- cible
    Colonne(
        "en_retard",
        "Late_delivery_risk",
        "cible",
        "booleen",
        "1 si la livraison est en retard (délai réel > délai prévu, hors annulation)",
    ),
)

PAR_NOM: dict[str, Colonne] = {c.nom: c for c in COLONNES}
RENOMMAGE: dict[str, str] = {c.source: c.nom for c in COLONNES if c.source is not None}

CIBLE = "en_retard"
DATE = "date_commande"
CLE_COMMANDE = "id_commande"


def colonnes(role: Role) -> list[str]:
    return [c.nom for c in COLONNES if c.role == role]


FACTEURS: list[str] = colonnes("facteur")
FUITES: list[str] = colonnes("fuite")
