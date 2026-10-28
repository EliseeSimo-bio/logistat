"""Graphiques Plotly de LogiStat.

Couleurs : bleu pour les séries neutres, rouge réservé au retard. Le retard est
toujours nommé en toutes lettres (légende, axe, infobulle), jamais signalé par la
couleur seule.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

BLEU = "#2a78d6"
ORANGE = "#eb6834"
RETARD = "#e34948"
GRIS = "#8a8984"

_MISE_EN_PAGE = dict(
    margin=dict(l=10, r=10, t=50, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
)


def _base(titre: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=dict(text=titre, x=0, font=dict(size=16)), **_MISE_EN_PAGE)
    return fig


def evolution_retard(df: pd.DataFrame) -> go.Figure:
    """Taux de retard mensuel (ligne) ; le volume de commandes est dans l'infobulle."""
    fig = _base("Taux de retard par mois")
    fig.add_scatter(
        x=df["mois"],
        y=df["taux_retard"],
        mode="lines+markers",
        line=dict(color=RETARD, width=2),
        marker=dict(size=6),
        name="Taux de retard",
        customdata=df["commandes"],
        hovertemplate="%{x|%b %Y}<br>Retard : %{y:.1%}<br>%{customdata} commandes<extra></extra>",
    )
    fig.update_yaxes(title_text="Commandes en retard", tickformat=".0%", rangemode="tozero")
    fig.update_xaxes(showgrid=False)
    fig.update_layout(showlegend=False, hovermode="x unified")
    return fig


def taux_par_modalite(df: pd.DataFrame, colonne: str, libelle: str, top: int = 20) -> go.Figure:
    d = df.head(top).iloc[::-1]
    fig = _base(f"Taux de retard selon : {libelle}")
    fig.add_bar(
        x=d["taux_retard"],
        y=d[colonne].astype(str),
        orientation="h",
        marker=dict(color=RETARD, line=dict(width=0)),
        customdata=d["commandes"],
        hovertemplate="%{y}<br>Retard : %{x:.1%}<br>%{customdata} commandes<extra></extra>",
        text=d["taux_retard"].map(lambda v: f"{v:.0%}"),
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_xaxes(title_text="Commandes en retard", tickformat=".0%", range=[0, 1.08])
    fig.update_yaxes(automargin=True)
    fig.update_layout(height=max(320, 26 * len(d) + 120), showlegend=False, bargap=0.25)
    return fig


def courbe_roc(df: pd.DataFrame, auc: float) -> go.Figure:
    fig = _base(f"Courbe ROC (AUC = {auc:.3f})")
    fig.add_scatter(
        x=df["taux_faux_positifs"],
        y=df["rappel"],
        mode="lines",
        line=dict(color=BLEU, width=2),
        name="Modèle",
        hovertemplate="Faux positifs %{x:.1%}<br>Rappel %{y:.1%}<extra></extra>",
    )
    fig.add_scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        line=dict(color=GRIS, width=1, dash="dash"),
        name="Hasard",
        hoverinfo="skip",
    )
    fig.update_xaxes(title_text="Taux de faux positifs", tickformat=".0%")
    fig.update_yaxes(title_text="Rappel (retards détectés)", tickformat=".0%")
    fig.update_layout(height=420, hovermode="closest")
    return fig


def jauge_probabilite(p: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=100 * p,
            number=dict(suffix=" %", valueformat=".0f"),
            title=dict(text="Probabilité de retard"),
            gauge=dict(
                axis=dict(range=[0, 100], ticksuffix=" %"),
                bar=dict(color=RETARD),
                steps=[dict(range=[0, 100], color="rgba(138,137,132,0.15)")],
            ),
        )
    )
    fig.update_layout(
        height=260, margin=dict(l=20, r=20, t=60, b=10), paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
