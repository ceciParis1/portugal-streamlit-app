
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ This must be the FIRST Streamlit command
st.set_page_config(page_title="Economic Analysis Portugal", layout="wide")

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv("data_eurostat_clean.csv")
    return df

df = load_data()

st.title("📊 Regional Economic Analysis of Portugal (2000 - 2022)")

st.markdown("""
This interactive application allows you to explore the evolution of regional economic indicators in Portugal from 2000 to 2022.  
Use the filters on the left to analyze trends, compare regions, and strengthen your thesis with interactive visualizations.
""")

# Filters
st.sidebar.header("🔹 Filters")
regions = sorted(df["Region"].unique())
selected_regions = st.sidebar.multiselect("Select regions:", regions, default=regions[:3])

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())
year_range = st.sidebar.slider("Select time range:", min_value=min_year, max_value=max_year, value=(2010, 2022))

# Data filtering
filtered = df[
    (df["Region"].isin(selected_regions)) &
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

# Line chart
st.subheader("🔄 Economic Indicator Trends")
fig, ax = plt.subplots(figsize=(10, 5))
for region in selected_regions:
    data = filtered[filtered["Region"] == region]
    ax.plot(data["Year"], data["Value"], marker='o', label=region)

ax.set_xlabel("Year")
ax.set_ylabel("Economic Value (Index)")
ax.set_title("Regional Trends")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Compute CAGR (Compound Annual Growth Rate)
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

st.subheader("📈 Compound Annual Growth Rate (CAGR)")
for region, value in cagr.items():
    st.markdown(f"- **{region}**: {value} % per year")

# Auto-generated interpretation
st.subheader("💬 Automated Interpretation")
for region in selected_regions:
    region_data = filtered[filtered["Region"] == region].sort_values("Year")
    if not region_data.empty:
        v0 = region_data.iloc[0]["Value"]
        v1 = region_data.iloc[-1]["Value"]
        diff = round(v1 - v0, 2)
        trend = "increased" if diff > 0 else "decreased"
        st.markdown(f"Between {year_range[0]} and {year_range[1]}, the region **{region}** has {trend} by {abs(diff)} index points.")

# Export
with st.expander("📂 Download filtered data"):
    st.dataframe(filtered)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_portugal_data.csv", "text/csv")
