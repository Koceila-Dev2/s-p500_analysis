import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Exoplanètes — biais du catalogue", layout="wide")

DATA_PATH = "data/projet_E_dataset_exoplanets.csv"

TYPE_BINS = [0, 1.5, 2.5, 6, np.inf]
TYPE_LABELS = ["Rocheuse", "Super-Terre", "Neptunienne", "Géante gazeuse"]
UNMEASURED_LABEL = "Rayon non mesuré"
TYPE_LABELS_ALL = TYPE_LABELS + [UNMEASURED_LABEL]
TYPE_COLORS = {
    "Rocheuse": "#e74c3c",
    "Super-Terre": "#f39c12",
    "Neptunienne": "#3498db",
    "Géante gazeuse": "#9b59b6",
}
METHOD_COLORS = {
    "Transit": "#2980b9",
    "Radial Velocity": "#c0392b",
    "Microlensing": "#27ae60",
    "Imaging": "#f39c12",
}


@st.cache_data
def load_data(path):
    df_raw = pd.read_csv(path, comment="#")
    df = df_raw[df_raw["default_flag"] == 1].copy()
    df["pl_type"] = pd.cut(df["pl_rade"], bins=TYPE_BINS, labels=TYPE_LABELS)
    df["pl_type"] = df["pl_type"].cat.add_categories([UNMEASURED_LABEL]).fillna(UNMEASURED_LABEL)
    df["mass_is_minimal"] = df["pl_bmassprov"].isin(["Msini", "Msin(i)/sin(i)"])
    df["habitable_zone"] = df["pl_insol"].between(0.32, 1.78)
    df["hz_rocky"] = df["habitable_zone"] & (df["pl_rade"] < 1.8)
    return df


df = load_data(DATA_PATH)

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Filtres")

methods = sorted(df["discoverymethod"].dropna().unique())
default_methods = [m for m in ["Transit", "Radial Velocity", "Microlensing", "Imaging"] if m in methods]
sel_methods = st.sidebar.multiselect("Méthode de découverte", methods, default=default_methods)

year_min, year_max = int(df["disc_year"].min()), int(df["disc_year"].max())
sel_years = st.sidebar.slider("Année de découverte", year_min, year_max, (year_min, year_max))

sel_types = st.sidebar.multiselect(
    "Type planétaire", TYPE_LABELS_ALL, default=TYPE_LABELS_ALL,
    help=f"'{UNMEASURED_LABEL}' regroupe les planètes sans rayon mesuré (ex: vitesse radiale, microlensing) — "
         "à garder coché par défaut pour ne pas fausser les KPIs de biais instrumental.",
)

mask = (
    df["discoverymethod"].isin(sel_methods)
    & df["disc_year"].between(*sel_years)
    & df["pl_type"].isin(sel_types)
)
dff = df[mask]

# ---------------------------------------------------------------- header
st.title("🔭 Le catalogue d'exoplanètes est un miroir déformé par nos instruments")
st.caption(
    f"{dff['pl_name'].nunique()} planètes affichées (sur {df['pl_name'].nunique()} au total, "
    "après filtre `default_flag == 1` pour ne garder qu'une mesure de référence par planète)."
)

# ---------------------------------------------------------------- KPIs
transit_share = (dff["discoverymethod"] == "Transit").mean() * 100 if len(dff) else 0
hz_rocky_n = int(dff["hz_rocky"].sum())
insol_coverage = dff["pl_insol"].notna().mean() * 100 if len(dff) else 0
med_period_transit = dff.loc[dff["discoverymethod"] == "Transit", "pl_orbper"].median()
med_mass_rv = dff.loc[dff["discoverymethod"] == "Radial Velocity", "pl_bmasse"].median()

k1, k2, k3 = st.columns(3)
k1.metric("Détectées par transit", f"{transit_share:.0f} %", help="Favorise les grosses planètes proches — biais géométrique du transit.")
k2.metric("Candidates rocheuses en zone habitable", f"{hz_rocky_n}", help=f"Sur seulement {insol_coverage:.0f} % de planètes avec insolation mesurée : un repérage, pas une statistique représentative.")
k3.metric(
    "Période médiane (transit) vs Masse médiane (vitesse radiale)",
    f"{med_period_transit:.0f} j  /  {med_mass_rv:.0f} M⊕" if pd.notna(med_period_transit) and pd.notna(med_mass_rv) else "n/a",
    help="Deux méthodes, deux populations complètement différentes : preuve du biais instrumental.",
)

st.divider()

# ---------------------------------------------------------------- tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["🎯 Biais de détection", "🪐 Typologie planétaire", "🌍 Zone habitable", "📈 Évolution temporelle"]
)

with tab1:
    st.subheader("Chaque méthode de découverte voit une population différente")
    d = dff.dropna(subset=["pl_orbper", "pl_rade"]).copy()
    d["log_orbper"] = np.log10(d["pl_orbper"])
    fig = px.scatter(
        d, x="log_orbper", y="pl_rade", color="discoverymethod",
        color_discrete_map=METHOD_COLORS, opacity=0.5,
        labels={"log_orbper": "Période orbitale (log10, jours)", "pl_rade": "Rayon (R⊕)", "discoverymethod": "Méthode"},
        title="Seul le transit couvre les courtes périodes / petits rayons",
    )
    st.plotly_chart(fig, use_container_width=True)

    counts = dff["discoverymethod"].value_counts().reset_index()
    counts.columns = ["Méthode", "Nombre"]
    fig2 = px.bar(counts, x="Méthode", y="Nombre", color="Méthode", color_discrete_map=METHOD_COLORS,
                  title="Répartition des découvertes par méthode (sélection filtrée)")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Quatre familles de planètes, validées par leur densité")
    type_counts = dff["pl_type"].value_counts().reindex(TYPE_LABELS).reset_index()
    type_counts.columns = ["Type", "Nombre"]
    fig3 = px.bar(type_counts, x="Type", y="Nombre", color="Type", color_discrete_map=TYPE_COLORS,
                  title="Combien de planètes de chaque type")
    st.plotly_chart(fig3, use_container_width=True)

    d = dff.dropna(subset=["pl_rade", "pl_bmasse"]).copy()
    d = d[(d["pl_rade"] > 0) & (d["pl_bmasse"] > 0)]
    d["log_rade"] = np.log10(d["pl_rade"])
    d["log_bmasse"] = np.log10(d["pl_bmasse"])
    fig4 = px.scatter(
        d, x="log_rade", y="log_bmasse", color="pl_type", color_discrete_map=TYPE_COLORS, opacity=0.4,
        labels={"log_rade": "Rayon (log10, R⊕)", "log_bmasse": "Masse (log10, M⊕)", "pl_type": "Type"},
        title="Relation masse-rayon : les familles s'enchaînent des rocheuses aux géantes",
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Des candidates à l'habitabilité, mais sur un échantillon partiel")
    d = dff.dropna(subset=["pl_insol", "pl_rade"]).copy()
    d["log_insol"] = np.log10(d["pl_insol"].where(d["pl_insol"] > 0))
    fig5 = px.scatter(
        d, x="log_insol", y="pl_rade", color="hz_rocky",
        color_discrete_map={True: "#27ae60", False: "#bdc3c7"},
        labels={"log_insol": "Insolation reçue (log10, S⊕)", "pl_rade": "Rayon (R⊕)", "hz_rocky": "Candidate habitable rocheuse"},
        title="Zone habitable optimiste (0.32-1.78 S⊕) et rayon < 1.8 R⊕",
    )
    fig5.add_vrect(x0=np.log10(0.32), x1=np.log10(1.78), fillcolor="#27ae60", opacity=0.1, line_width=0)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("**Candidates rocheuses en zone habitable (sélection filtrée)**")
    cols = ["pl_name", "hostname", "pl_rade", "pl_insol", "pl_eqt", "discoverymethod"]
    st.dataframe(
        dff.loc[dff["hz_rocky"], cols].sort_values("pl_insol"),
        use_container_width=True, hide_index=True,
    )

with tab4:
    st.subheader("Le rythme des découvertes suit les missions spatiales, pas la nature")
    piv = (
        dff.pivot_table(index="disc_year", columns="discoverymethod", values="pl_name", aggfunc="count")
        .fillna(0)
    )
    piv = piv[[c for c in METHOD_COLORS if c in piv.columns] + [c for c in piv.columns if c not in METHOD_COLORS]]
    fig6 = px.area(
        piv, x=piv.index, y=piv.columns, color_discrete_map=METHOD_COLORS,
        labels={"disc_year": "Année", "value": "Découvertes", "variable": "Méthode"},
        title="Découvertes par méthode et par année (pics Kepler 2014-2016, TESS dès 2018)",
    )
    fig6.update_layout(legend_title_text="Méthode")
    st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.caption(
    "Source : NASA Exoplanet Archive (Projet_E_dataset_exoplanets.csv), filtré sur `default_flag == 1`. "
    "Les masses issues de vitesse radiale (Msini) sont des bornes minimales, pas des mesures directes."
)
