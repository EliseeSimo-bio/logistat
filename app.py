"""LogiStat — point d'entrée de l'application.

Lancement :  streamlit run app.py

Coquille d'intégration (bloc 1, tâche B1.1) : chaque onglet est branché sur les
contrats du projet. Le bloc 2 enrichit « Facteurs de retard » avec ses analyses ;
le bloc 3 dépose ses modèles dans modeles/, qui apparaissent dans « Prédiction » et
« Performance » sans modifier ce fichier.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permet de lancer l'application même si le paquet n'a pas été installé (pip install -e .)
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from logistat import __version__
from logistat.analyse.indicateurs import evolution_mensuelle, resume_global, taux_retard_par
from logistat.config import DATE_COUPURE, EXCLURE_ANNULEES
from logistat.donnees import (
    FACTEURS_COMMANDES,
    ROLES_COMMANDES,
    ErreurContrat,
    charger_commandes,
    population_modelisation,
)
from logistat.modele import (
    courbe_roc,
    decoupage_chronologique,
    evaluer,
    matrice_confusion,
    probabilite_retard,
    stockage,
)
from logistat.modele.integration import ModeleFactice
from logistat.ui import graphiques

st.set_page_config(page_title="LogiStat", page_icon="📦", layout="wide")

LIBELLES = {
    "mode_expedition": "Mode d'expédition",
    "marche": "Marché",
    "region_commande": "Région de destination",
    "pays_commande": "Pays de destination",
    "segment_client": "Segment client",
    "type_paiement": "Type de paiement",
    "categorie_principale": "Catégorie principale",
    "departement_principal": "Rayon principal",
    "nb_articles": "Nombre d'articles",
    "pays_client": "Pays du client",
}


# ------------------------------------------------------------------ cache
@st.cache_data(show_spinner="Chargement des données…")
def donnees():
    jeu = charger_commandes()
    return jeu.commandes, str(jeu.source.name), jeu.complet


@st.cache_resource
def modele_disponible(chemin: str):
    return stockage.charger(Path(chemin))


@st.cache_resource(show_spinner="Entraînement du modèle factice…")
def modele_factice(_app: pd.DataFrame, cle: str):
    return ModeleFactice().fit(_app[ModeleFactice.variables], _app["en_retard"])


def pct(x: float, d: int = 1) -> str:
    return f"{x:.{d}%}".replace(".", ",")


def nombre(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")


# ------------------------------------------------------------------ données et filtres
try:
    commandes, source, complet = donnees()
except ErreurContrat as err:
    st.error(str(err))
    st.stop()

with st.sidebar:
    st.title("📦 LogiStat")
    st.caption(f"Analyse et prédiction des retards de livraison · v{__version__}")
    if not complet:
        st.warning("Échantillon de 3 000 commandes : lancez scripts/preparer_donnees.py.")

    st.header("Filtres")
    dmin, dmax = commandes["date_commande"].min().date(), commandes["date_commande"].max().date()
    periode = st.date_input("Période de commande", (dmin, dmax), min_value=dmin, max_value=dmax)
    marches = st.multiselect("Marché", sorted(commandes["marche"].unique()))
    modes = st.multiselect("Mode d'expédition", sorted(commandes["mode_expedition"].unique()))

filtre = commandes
if isinstance(periode, tuple) and len(periode) == 2:
    debut, fin = pd.Timestamp(periode[0]), pd.Timestamp(periode[1]) + pd.Timedelta(days=1)
    filtre = filtre[(filtre["date_commande"] >= debut) & (filtre["date_commande"] < fin)]
if marches:
    filtre = filtre[filtre["marche"].isin(marches)]
if modes:
    filtre = filtre[filtre["mode_expedition"].isin(modes)]

st.title("Retards de livraison")
st.caption(f"{nombre(len(filtre))} commandes sélectionnées sur {nombre(len(commandes))} · {source}")
if filtre.empty:
    st.info("Aucune commande ne correspond aux filtres.")
    st.stop()

onglets = st.tabs(
    ["Vue d'ensemble", "Facteurs de retard", "Prédiction", "Performance du modèle", "Données"]
)

# ------------------------------------------------------------------ Vue d'ensemble
with onglets[0]:
    r = resume_global(filtre)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Commandes", nombre(r["commandes"]))
    k2.metric("Taux de retard", pct(r["taux_retard"]), help="Parmi les commandes non annulées.")
    k3.metric("Écart moyen au délai promis", f"{r['ecart_moyen_jours']:+.2f} j".replace(".", ","))
    k4.metric("Commandes annulées", nombre(r["annulees"]))
    st.plotly_chart(graphiques.evolution_retard(evolution_mensuelle(filtre)), width="stretch")

# ------------------------------------------------------------------ Facteurs
with onglets[1]:
    c1, c2 = st.columns([1, 3])
    variable = c1.selectbox(
        "Variable", list(LIBELLES), format_func=lambda v: LIBELLES[v], key="facteur"
    )
    table = taux_retard_par(filtre, variable)
    with c2:
        st.plotly_chart(
            graphiques.taux_par_modalite(table, variable, LIBELLES[variable]), width="stretch"
        )
    st.caption("Emplacement réservé aux analyses du bloc 2 (distributions, tests, corrélations).")

# ------------------------------------------------------------------ Modèles disponibles
pop = population_modelisation(commandes, EXCLURE_ANNULEES)
decoupage = decoupage_chronologique(pop, DATE_COUPURE)
disponibles = {nom: str(chemin) for nom, chemin in stockage.lister().items()}
if not disponibles:
    disponibles = {ModeleFactice.nom + " — intégration": "__factice__"}


def obtenir_modele(nom: str):
    chemin = disponibles[nom]
    if chemin == "__factice__":
        return modele_factice(decoupage.apprentissage, source)
    return modele_disponible(chemin)


# ------------------------------------------------------------------ Prédiction
with onglets[2]:
    if "__factice__" in disponibles.values():
        st.info(
            "Aucun modèle dans modeles/ : le modèle factice d'intégration est utilisé. "
            "Le bloc 3 y dépose ses modèles avec logistat.modele.stockage.sauvegarder()."
        )
    nom = st.selectbox("Modèle", list(disponibles), key="modele_prediction")
    modele = obtenir_modele(nom)
    st.markdown("**Caractéristiques de la commande**")
    saisie = {}
    cols = st.columns(3)
    for i, v in enumerate(modele.variables):
        col = cols[i % 3]
        serie = commandes[v]
        if pd.api.types.is_numeric_dtype(serie):
            saisie[v] = col.number_input(v, value=float(serie.median()), key=f"in_{v}")
        else:
            saisie[v] = col.selectbox(v, sorted(serie.dropna().unique()), key=f"in_{v}")
    p = float(probabilite_retard(modele, pd.DataFrame([saisie]))[0])
    st.plotly_chart(graphiques.jauge_probabilite(p), width="stretch")

# ------------------------------------------------------------------ Performance
with onglets[3]:
    nom_perf = st.selectbox("Modèle", list(disponibles), key="modele_perf")
    modele_p = obtenir_modele(nom_perf)
    seuil = st.slider("Seuil de décision", 0.05, 0.95, 0.50, 0.05)
    st.dataframe(decoupage.resume(), width="stretch")
    test = decoupage.test
    proba = probabilite_retard(modele_p, test)
    m = evaluer(test["en_retard"], proba, seuil)
    a, b, c, d, e = st.columns(5)
    a.metric("Exactitude", pct(m["exactitude"]))
    b.metric("Précision", pct(m["precision"]))
    c.metric("Rappel", pct(m["rappel"]))
    d.metric("F1", f"{m['f1']:.3f}".replace(".", ","))
    e.metric("ROC-AUC", f"{m['roc_auc']:.3f}".replace(".", ","))
    g1, g2 = st.columns(2)
    g1.dataframe(matrice_confusion(test["en_retard"], proba, seuil), width="stretch")
    g2.plotly_chart(
        graphiques.courbe_roc(courbe_roc(test["en_retard"], proba), m["roc_auc"]), width="stretch"
    )

# ------------------------------------------------------------------ Données
with onglets[4]:
    st.dataframe(filtre, width="stretch", hide_index=True)
    st.download_button(
        "Télécharger la sélection (CSV)",
        filtre.to_csv(index=False).encode("utf-8"),
        file_name="logistat_commandes.csv",
    )
    with st.expander("Dictionnaire des variables"):
        st.dataframe(
            pd.DataFrame(
                {"variable": list(ROLES_COMMANDES), "rôle": list(ROLES_COMMANDES.values())}
            ).assign(utilisable_dans_un_modele=lambda d: d["variable"].isin(FACTEURS_COMMANDES)),
            hide_index=True,
            width="stretch",
        )
