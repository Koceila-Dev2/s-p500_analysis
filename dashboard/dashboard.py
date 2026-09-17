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
NO_ANALOG_TYPES = ["Super-Terre", "Neptunienne"]  # tailles absentes du système solaire
HZ_ACCENT = "#27ae60"
MISSION_ACCENT = "#34495e"


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


def insight_card(kicker: str, stat: str, message: str, accent: str = "#2980b9"):
    """Bloc 'réponse d'abord' (pyramide de Minto) : un chiffre choc + sa lecture en une phrase."""
    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {accent};
            background: color-mix(in srgb, {accent} 10%, transparent);
            border-radius: 8px;
            padding: 0.9rem 1.3rem;
            margin: 0.3rem 0 1.1rem 0;
        ">
            <div style="font-size:0.75rem; letter-spacing:0.06em; text-transform:uppercase; opacity:0.75; font-weight:700;">
                {kicker}
            </div>
            <div style="font-size:2.3rem; font-weight:800; line-height:1.15; margin:0.15rem 0;">
                {stat}
            </div>
            <div style="font-size:0.97rem; opacity:0.92; max-width:70ch;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


df = load_data(DATA_PATH)

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Filtres")

methods = [m for m in METHOD_COLORS if m in df["discoverymethod"].unique()]
sel_methods = st.sidebar.multiselect(
    "Méthode de découverte", methods, default=methods,
    help="Limité aux 4 méthodes qui structurent l'analyse. Les méthodes marginales "
         "(quelques dizaines de planètes au total) sont écartées pour ne pas diluer le message.",
)

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
st.title("Le catalogue d'exoplanètes est un miroir déformé par nos instruments")
st.caption(
    f"{dff['pl_name'].nunique()} planètes affichées (sur {df['pl_name'].nunique()} au total, "
    "après filtre `default_flag == 1` pour ne garder qu'une mesure de référence par planète)."
)

# ---------------------------------------------------------------- KPIs (le message, en 3 chiffres)
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
    ["Biais de détection", "Typologie planétaire", "Zone habitable", "Évolution temporelle"]
)

# ============================================================ TAB 1 — Biais de détection
with tab1:
    st.subheader("Sous 2 rayons terrestres, il n'y a (presque) que le transit")

    d = dff.dropna(subset=["pl_orbper", "pl_rade"]).copy()
    small = d[d["pl_rade"] < 2]
    small_transit_pct = (small["discoverymethod"] == "Transit").mean() * 100 if len(small) else 0

    insight_card(
        "Preuve du biais géométrique",
        f"{small_transit_pct:.0f} %",
        f"Sur les {len(small)} planètes de la sélection plus petites que 2 rayons terrestres, "
        f"<b>{small_transit_pct:.0f} %</b> ont été détectées par transit. Les autres méthodes "
        "(vitesse radiale, imagerie…) ne voient quasiment que des planètes plus grosses : ce n'est pas "
        "que les petites planètes proches sont rares, c'est qu'on ne sait presque pas les voir autrement.",
        accent=METHOD_COLORS["Transit"],
    )

    d["log_orbper"] = np.log10(d["pl_orbper"])
    fig = px.scatter(
        d, x="log_orbper", y="pl_rade", color="discoverymethod",
        color_discrete_map=METHOD_COLORS, opacity=0.5,
        labels={"log_orbper": "Période orbitale (log10, jours)", "pl_rade": "Rayon (R⊕)", "discoverymethod": "Méthode"},
        title="Seul le transit couvre les courtes périodes / petits rayons",
    )
    if len(d):
        fig.add_hrect(y0=0, y1=2, fillcolor=METHOD_COLORS["Transit"], opacity=0.08, line_width=0)
        fig.add_annotation(
            x=d["log_orbper"].min(), y=2, text="↓ zone quasi exclusivement transit",
            showarrow=False, xanchor="left", yanchor="bottom",
            font=dict(size=12, color=METHOD_COLORS["Transit"]),
        )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Détail : répartition brute des découvertes par méthode"):
        counts = dff["discoverymethod"].value_counts().reset_index()
        counts.columns = ["Méthode", "Nombre"]
        fig2 = px.bar(counts, x="Méthode", y="Nombre", color="Méthode", color_discrete_map=METHOD_COLORS,
                      title="Répartition des découvertes par méthode (sélection filtrée)")
        st.plotly_chart(fig2, use_container_width=True)

# ============================================================ TAB 2 — Typologie planétaire
with tab2:
    st.subheader("La majorité des exoplanètes n'ont pas d'équivalent dans notre système solaire")

    measured = dff[dff["pl_type"] != UNMEASURED_LABEL]
    no_analog_pct = measured["pl_type"].isin(NO_ANALOG_TYPES).mean() * 100 if len(measured) else 0

    insight_card(
        "Aucun analogue chez nous",
        f"{no_analog_pct:.0f} %",
        f"Parmi les {len(measured)} planètes de la sélection dont la taille est mesurée, "
        f"<b>{no_analog_pct:.0f} %</b> sont des Super-Terres ou des Neptunes — des tailles intermédiaires "
        "qui n'existent pas dans notre système solaire, ni tout à fait rocheuses ni tout à fait gazeuses géantes.",
        accent="#f39c12",
    )

    type_counts = measured["pl_type"].value_counts().reindex(TYPE_LABELS).fillna(0).reset_index()
    type_counts.columns = ["Type", "Nombre"]
    fig3 = px.bar(type_counts, x="Type", y="Nombre", color="Type", color_discrete_map=TYPE_COLORS,
                  title="Combien de planètes de chaque type (rayon mesuré uniquement)")
    for trace in fig3.data:
        trace.marker.opacity = 1.0 if trace.name in NO_ANALOG_TYPES else 0.35
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("En couleur pleine : les deux types sans équivalent dans notre système solaire.")

    with st.expander("Détail : relation masse-rayon"):
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

# ============================================================ TAB 3 — Zone habitable
with tab3:
    st.subheader("18 candidates, sur un radar encore très incomplet")

    n_total = len(dff)
    n_covered = int(dff["pl_insol"].notna().sum())
    coverage_pct = (n_covered / n_total * 100) if n_total else 0
    hz_rocky_n_tab = int(dff["hz_rocky"].sum())

    insight_card(
        "Un repérage, pas une conclusion",
        f"{hz_rocky_n_tab} planète(s)",
        f"Sur {n_total} planètes de la sélection, seules {n_covered} ({coverage_pct:.0f} %) ont une "
        "insolation mesurée assez précisément pour juger de leur habitabilité. Parmi elles, "
        f"<b>{hz_rocky_n_tab}</b> sont à la fois rocheuses et dans la zone habitable optimiste — "
        "un échantillon trop partiel pour estimer la fréquence des Terres jumelles dans la galaxie.",
        accent=HZ_ACCENT,
    )

    d = dff.dropna(subset=["pl_insol", "pl_rade"]).copy()
    d = d[d["pl_insol"] > 0]
    d["log_insol"] = np.log10(d["pl_insol"])
    fig5 = px.scatter(
        d, x="log_insol", y="pl_rade", color="hz_rocky",
        color_discrete_map={True: HZ_ACCENT, False: "#bdc3c7"},
        labels={"log_insol": "Insolation reçue (log10, S⊕)", "pl_rade": "Rayon (R⊕)", "hz_rocky": "Candidate habitable rocheuse"},
        title="Zone habitable optimiste (0.32-1.78 S⊕) et rayon < 1.8 R⊕",
    )
    fig5.add_vrect(x0=np.log10(0.32), x1=np.log10(1.78), fillcolor=HZ_ACCENT, opacity=0.1, line_width=0)
    if len(d):
        fig5.add_annotation(
            x=(np.log10(0.32) + np.log10(1.78)) / 2, y=d["pl_rade"].max(),
            text="Zone habitable optimiste", showarrow=False, yanchor="bottom",
            font=dict(size=12, color=HZ_ACCENT),
        )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("**Candidates rocheuses en zone habitable (sélection filtrée)**")
    cols = ["pl_name", "hostname", "pl_rade", "pl_insol", "pl_eqt", "discoverymethod"]
    st.dataframe(
        dff.loc[dff["hz_rocky"], cols].sort_values("pl_insol"),
        use_container_width=True, hide_index=True,
    )

# ============================================================ TAB 4 — Évolution temporelle
with tab4:
    st.subheader("Les pics de découvertes sont des évènements de publication, pas des vagues naturelles")

    piv = (
        dff.pivot_table(index="disc_year", columns="discoverymethod", values="pl_name", aggfunc="count")
        .fillna(0)
    )
    piv = piv[[c for c in METHOD_COLORS if c in piv.columns] + [c for c in piv.columns if c not in METHOD_COLORS]]

    kepler_mask = dff["disc_facility"].isin(["Kepler", "K2"])
    kepler_pct = kepler_mask.mean() * 100 if len(dff) else 0
    yearly_totals = piv.sum(axis=1)
    peak_year = int(yearly_totals.idxmax()) if len(yearly_totals) else None
    peak_year_n = int(yearly_totals.max()) if len(yearly_totals) else 0

    insight_card(
        "Une seule mission, la moitié du catalogue",
        f"{kepler_pct:.0f} %",
        f"<b>{kepler_pct:.0f} %</b> des planètes de la sélection ont été révélées par un seul télescope spatial, "
        f"Kepler (missions Kepler puis K2)." + (
            f" Le pic de {peak_year} ({peak_year_n} planètes) correspond à la publication d'un lot de "
            "candidats validés d'un coup, pas à une accélération soudaine de la découverte."
            if peak_year is not None else ""
        ),
        accent=MISSION_ACCENT,
    )

    fig6 = px.area(
        piv, x=piv.index, y=piv.columns, color_discrete_map=METHOD_COLORS,
        labels={"disc_year": "Année", "value": "Découvertes", "variable": "Méthode"},
        title="Découvertes par méthode et par année (pics Kepler 2014-2016, TESS dès 2018)",
    )
    fig6.update_layout(legend_title_text="Méthode")
    if peak_year is not None:
        fig6.add_annotation(
            x=peak_year, y=peak_year_n, text=f"Lot Kepler validé en {peak_year}",
            showarrow=True, arrowhead=2, ax=40, ay=-40,
            font=dict(size=12, color=MISSION_ACCENT),
        )
    st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.caption(
    "Source : NASA Exoplanet Archive (Projet_E_dataset_exoplanets.csv), filtré sur `default_flag == 1`. "
    "Les masses issues de vitesse radiale (Msini) sont des bornes minimales, pas des mesures directes."
)
