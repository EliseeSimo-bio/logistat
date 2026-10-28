# Dictionnaire des données

Généré à partir de `src/logistat/donnees/schema.py` (la référence) ; à régénérer si le
schéma change.

## Rôles

| Rôle | Signification | Dans un modèle ? |
|---|---|---|
| identifiant | clé technique | non |
| temps | date de la commande | via des variables dérivées (mois, jour…) décidées par le bloc 3 |
| facteur | connu au moment de la commande | **oui** |
| autre | conservé pour l'analyse, statut à discuter | non par défaut |
| fuite | connu seulement après l'expédition | **jamais** (contrôlé par un test) |
| cible | `en_retard` | c'est la variable à prédire |

## Pourquoi ces fuites

`en_retard` vaut 1 exactement quand `delai_reel_jours > delai_prevu_jours` (hors
annulations). Toute variable qui révèle le délai réel donne donc la réponse au modèle :
`delai_reel_jours`, `date_expedition` (date de commande + délai réel dans 97 % des cas),
`statut_livraison` (« Late delivery » ⇔ retard), `ecart_jours`. `statut_commande` est
classé en fuite par prudence : il évolue après la commande (annulation, fraude suspectée).

## Table `lignes` (1 ligne = 1 article)

Colonnes supprimées à la préparation : courriel, prénom, nom, mot de passe masqué,
rue, code postal et ville/État du client, image et description du produit (vide),
code postal de destination (86 % manquant), et cinq colonnes en double exact
(`Order Customer Id`, `Order Item Cardprod Id`, `Product Category Id`,
`Sales per customer`, `Benefit per order`), ainsi que `Category Id`, `Department Id`,
`Product Price` et `Order State`.

| Variable (lignes) | Colonne DataCo | Rôle | Type | Description |
|---|---|---|---|---|
| `id_commande` | Order Id | identifiant | entier | Numéro de la commande |
| `id_ligne` | Order Item Id | identifiant | entier | Numéro de la ligne (article) |
| `id_client` | Customer Id | identifiant | entier | Numéro du client |
| `id_produit` | Product Card Id | identifiant | entier | Numéro du produit |
| `date_commande` | order date (DateOrders) | temps | date | Date et heure de la commande |
| `mode_expedition` | Shipping Mode | facteur | texte | Standard Class, Second Class, First Class, Same Day |
| `delai_prevu_jours` | Days for shipment (scheduled) | facteur | entier | Délai de livraison promis (jours) |
| `type_paiement` | Type | facteur | texte | DEBIT, TRANSFER, PAYMENT, CASH |
| `segment_client` | Customer Segment | facteur | texte | Consumer, Corporate, Home Office |
| `pays_client` | Customer Country | facteur | texte | Pays du client (EE. UU., Puerto Rico) |
| `marche` | Market | facteur | texte | Africa, Europe, LATAM, Pacific Asia, USCA |
| `region_commande` | Order Region | facteur | texte | Région de destination |
| `pays_commande` | Order Country | facteur | texte | Pays de destination |
| `ville_commande` | Order City | facteur | texte | Ville de destination |
| `departement` | Department Name | facteur | texte | Rayon du magasin |
| `categorie` | Category Name | facteur | texte | Catégorie du produit |
| `produit` | Product Name | facteur | texte | Nom du produit |
| `prix_unitaire` | Order Item Product Price | facteur | reel | Prix avant remise ($) |
| `quantite` | Order Item Quantity | facteur | entier | Quantité commandée |
| `remise` | Order Item Discount | facteur | reel | Montant de la remise ($) |
| `taux_remise` | Order Item Discount Rate | facteur | reel | Remise en proportion |
| `ventes` | Sales | facteur | reel | Montant avant remise ($) |
| `total_ligne` | Order Item Total | facteur | reel | Montant après remise ($) |
| `latitude_magasin` | Latitude | facteur | reel | Latitude du magasin |
| `longitude_magasin` | Longitude | facteur | reel | Longitude du magasin |
| `profit_commande` | Order Profit Per Order | autre | reel | Profit ($) ; peut dépendre d'événements postérieurs (fraude, annulation) |
| `ratio_profit` | Order Item Profit Ratio | autre | reel | Profit / ventes |
| `produit_indisponible` | Product Status | autre | booleen | 1 = produit indisponible (toujours 0 dans DataCo) |
| `delai_reel_jours` | Days for shipping (real) | fuite | entier | Délai réel de livraison (jours) |
| `date_expedition` | shipping date (DateOrders) | fuite | date | Date d'expédition |
| `statut_livraison` | Delivery Status | fuite | texte | Advance shipping, Late delivery, Shipping on time, Shipping canceled |
| `statut_commande` | Order Status | fuite | texte | COMPLETE, PENDING, CANCELED, SUSPECTED_FRAUD… |
| `ecart_jours` | (dérivée) | fuite | entier | delai_reel_jours − delai_prevu_jours |
| `annulee` | (dérivée) | fuite | booleen | statut_livraison = Shipping canceled |
| `en_retard` | Late_delivery_risk | cible | booleen | 1 si la livraison est en retard (délai réel > délai prévu, hors annulation) |

## Table `commandes` (1 ligne = 1 commande, unité de modélisation)

Mode d'expédition, délais, destination, client et cible sont identiques pour tous les
articles d'une commande (vérifié sur les 65 752 commandes). Règles d'agrégation :

| Variable | Règle |
|---|---|
| colonnes constantes dans la commande | première valeur |
| `quantite`, `ventes`, `remise`, `total_commande`, `profit_commande` | somme des articles |
| `categorie_principale`, `departement_principal` | ceux de l'article au montant le plus élevé |
| `nb_articles`, `nb_produits_distincts` | comptes |
| `taux_remise` | `remise / ventes` |

## Journal des règles de préparation

| Date | Règle | Auteur | Bloc |
|---|---|---|---|
| 2026-10-28 | Lecture latin-1, renommage, suppression des données personnelles et des doublons | Bloc 1 | B1.1 |
| 2026-10-28 | Agrégation au niveau commande | Bloc 1 | B1.1 |
| | *(ajouter ici chaque règle de nettoyage du bloc 2)* | | |
