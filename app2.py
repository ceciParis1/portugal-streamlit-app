import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ✅ Doit être la première commande Streamlit
st.set_page_config(page_title="Economic Analysis Portugal", layout="wide")

# Charger les données
@st.cache_data
def load_data():
    df = pd.read_csv("data_eurostat_clean.csv")
    return df

df = load_data()

# Ajout de coordonnées approximatives pour chaque région
coords = {
    "Norte": (41.5, -8.5),
    "Centro": (40.3, -7.9),
    "Área Metropolitana de Lisboa": (38.7, -9.1),
    "Alentejo": (38.0, -7.9),
    "Algarve": (37.0, -8.0),
    "Região Autónoma dos Açores": (38.7, -27.2),
    "Região Autónoma da Madeira": (32.7, -17.0)
}
df["lat"] = df["Region"].map(lambda x: coords.get(x, (0, 0))[0])
df["lon"] = df["Region"].map(lambda x: coords.get(x, (0, 0))[1])

# Titre
st.title("📊 Regional Economic Analysis of Portugal (2000 - 2022)")

st.markdown("""
This interactive app lets you explore regional economic trends in Portugal.  
Use the filters to compare regions, view trends, and export data.
""")

# --- SIDEBAR ---
st.sidebar.header("🔹 Filters")

regions = sorted(df["Region"].unique())
default_regions = regions[:3]

if st.sidebar.button("🔄 Reset Filters"):
    selected_regions = default_regions
    year_range = (2010, 2022)
else:
    selected_regions = st.sidebar.multiselect("Select regions:", regions, default=default_regions)
    year_range = st.sidebar.slider("Time range:", int(df["Year"].min()), int(df["Year"].max()), value=(2010, 2022))

# Filtrage
filtered = df[
    (df["Region"].isin(selected_regions)) &
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

# --- GRAPHIQUE ---
st.subheader("🔄 Regional Trends")
fig, ax = plt.subplots(figsize=(10, 5))
for region in selected_regions:
    data = filtered[filtered["Region"] == region]
    ax.plot(data["Year"], data["Value"], marker='o', label=region)
ax.set_xlabel("Year")
ax.set_ylabel("Economic Value (Index)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- STATISTIQUES ---
st.subheader("📌 Summary Statistics")
stats = filtered.groupby("Region")["Value"].agg(["mean", "std", "min", "max"]).round(2)
st.dataframe(stats)

# --- CALCUL CAGR ---
def compute_cagr(region_df):
    df_grouped = region_df.groupby("Region")
    cagr_results = {}
    for region, group in df_grouped:
        group = group.sort_values("Year")
        val_start = group.iloc[0]["Value"]
        val_end = group.iloc[-1]["Value"]
        n = group.iloc[-1]["Year"] - group.iloc[0]["Year"]
        if val_start > 0 and n > 0:
            cagr = ((val_end / val_start) ** (1 / n) - 1) * 100
            cagr_results[region] = round(cagr, 2)
    return cagr_results

cagr = compute_cagr(filtered)

st.subheader("📈 CAGR (Compound Annual Growth Rate)")
for region, value in cagr.items():
    st.markdown(f"- **{region}**: {value} % per year")

# --- INTERPRETATION ---
st.subheader("💬 Automated Interpretation")
for region in selected_regions:
    region_data = filtered[filtered["Region"] == region].sort_values("Year")
    if not region_data.empty:
        v0 = region_data.iloc[0]["Value"]
        v1 = region_data.iloc[-1]["Value"]
        diff = round(v1 - v0, 2)
        trend = "increased" if diff > 0 else "decreased"
        st.markdown(f"Between {year_range[0]} and {year_range[1]}, **{region}** has {trend} by {abs(diff)} index points.")

# --- CARTE INTERACTIVE ---
st.subheader("🗺️ Geographic Visualization")
map_data = filtered[["Region", "Value", "lat", "lon"]].groupby("Region", as_index=False).mean()
map_data["lat"] = map_data["Region"].map(lambda x: coords.get(x, (0, 0))[0])
map_data["lon"] = map_data["Region"].map(lambda x: coords.get(x, (0, 0))[1])
map_data["Value"] = map_data["Value"].round(1)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_radius=20000,
    get_fill_color='[200, 30, 0, 160]',
    pickable=True
)

view_state = pdk.ViewState(latitude=39.5, longitude=-8.0, zoom=5.5)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "{Region}\nValue: {Value}"}
))

# --- EXPORT ---
with st.expander("📂 Download filtered data"):
    st.dataframe(filtered)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_portugal_data.csv", "text/csv")
