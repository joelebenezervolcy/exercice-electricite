from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(
    page_title="L'électricité dans 12 quartiers",
    page_icon="⚡",
    layout="wide",
)

st.title("L'électricité dans 12 quartiers")
st.caption(
    "Relevés mensuels de janvier 2024 à décembre 2025. Données fictives."
)


@st.cache_data
def charger():
    return pd.read_csv(
        DOSSIER / "consommation_propre.csv"
    )


donnees = charger()

st.write(
    "La compagnie suit 12 quartiers de Port-au-Prince, Delmas, Pétion-Ville et Cap-Haïtien."
)

st.write(
    "Question du directeur : la consommation suit-elle la chaleur, ou les heures de courant ?"
)

toutes_communes = sorted(
    donnees["commune"].unique()
)

communes = st.sidebar.multiselect(
    "Communes",
    toutes_communes,
    default=toutes_communes,
)

annees = sorted(
    donnees["annee"].unique()
)

annee = st.sidebar.selectbox(
    "Année",
    annees,
    index=len(annees) - 1,
)

if not communes:
    st.warning(
        "Choisissez au moins une commune dans la barre latérale."
    )
    st.stop()

vue = donnees[
    (donnees["commune"].isin(communes))
    &
    (donnees["annee"] == annee)
]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Consommation totale",
    f"{vue['kwh'].sum()/1e6:.2f} millions de kWh"
)

col2.metric(
    "Par abonné",
    f"{vue['kwh_par_abonne'].mean():.1f} kWh"
)

col3.metric(
    "Courant par jour",
    f"{vue['heures_courant'].mean():.1f} heures"
)

onglet1, onglet2, onglet3, onglet4, onglet5 = st.tabs(
    [
        "Quartiers",
        "Communes",
        "Chaleur ou courant ?",
        "Coupures",
        "Relevés à part",
    ]
)

with onglet1:
    classement = (
        vue.groupby("quartier")["kwh_par_abonne"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(classement)

    st.write(
        f"{classement.index[0]} consomme le plus par abonné : {classement.iloc[0]:.1f} kWh par mois."
    )

with onglet2:
    par_mois = vue.pivot_table(
        index="mois",
        columns="commune",
        values="kwh_par_abonne",
        aggfunc="mean",
    )

    st.line_chart(par_mois)

    total_commune = (
        vue.groupby("commune")["kwh"]
        .sum()
    )

    st.write(
        f"{total_commune.idxmax()} totalise le plus : {total_commune.max()/1e6:.2f} millions de kWh en {annee}."
    )

with onglet3:
    resid = donnees[
        donnees["type"] == "Résidentiel"
    ]

    st.scatter_chart(
        resid,
        x="heures_courant",
        y="kwh_par_abonne"
    )

    r_courant = resid["kwh_par_abonne"].corr(
        resid["heures_courant"]
    )

    r_temp = resid["kwh_par_abonne"].corr(
        resid["temperature_c"]
    )

    st.write(
        f"Corrélation avec les heures de courant : {r_courant:.2f} ; avec la température : {r_temp:.2f}."
    )

with onglet4:
    mediane = (
        vue.groupby("commune")["heures_courant"]
        .median()
    )

    st.bar_chart(mediane)

    courts = vue[
        vue["heures_courant"] < 8
    ]

    st.write(
        f"{mediane.idxmin()} a les coupures les plus longues (médiane {mediane.min():.1f} h). {len(courts)} relevés sont sous 8 heures de courant."
    )

with onglet5:
    top = vue.nlargest(
        3,
        "kwh"
    )[
        [
            "mois",
            "quartier",
            "type",
            "kwh"
        ]
    ]

    st.dataframe(
        top,
        hide_index=True
    )

    st.write(
        f"Le plus gros relevé : {top.iloc[0]['quartier']} en {top.iloc[0]['mois']} ({top.iloc[0]['kwh']:,.0f} kWh)."
    )

st.markdown(
    """
### Conclusion

Dans les quartiers résidentiels, la consommation par abonné suit davantage les heures de courant (corrélation de 0.76) que la température (-0.15). Une corrélation ne démontre toutefois pas une relation de cause à effet. Cette étude est basée sur 279 relevés fictifs.
"""
)

with st.expander(
    "Voir les données filtrées"
):
    st.dataframe(
        vue,
        hide_index=True
    )