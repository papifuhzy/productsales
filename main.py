import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

# ===============================
# LOAD DATA DARI HASIL HADOOP TXT
# ===============================

def load_salesproduct_txt(path):
    rows = []

    with open(path) as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts_tab = line.split("\t")

            if len(parts_tab) != 4:
                continue

            key, qty, revenue, profit = parts_tab
            dims = key.split("|")

            if len(dims) != 7:
                continue

            rows.append({
                "Year": dims[0],
                "Region": dims[1],
                "State": dims[2],
                "Category": dims[3],
                "Sub_Category": dims[4],
                "Product_Name": dims[5],
                "Customer_Name": dims[6],
                "Quantity": int(qty),
                "Revenue": float(revenue),
                "Profit": float(profit)
            })

    return pd.DataFrame(rows)

df = load_salesproduct_txt("SalesProduct.txt")

# ===============================
# SIDEBAR NAVIGATION
# ===============================
with st.sidebar:
    selected = option_menu(
        "Analysis Dashboard",
        [
            "Top Categories & Sub-Categories (Last 12 Months)",
            "Regional & Provincial Profit Analysis",
            "Top 10 Most Profitable Products",
            "Category Popularity Across Regions",
            "Top Customers by Revenue Contribution",
            "Revenue Trend: 2023 vs 2024"
        ],
        default_index=0
    )

# ===============================
# TOP CATEGORY & SUBCATEGORY
# ===============================
if selected == "Top Categories & Sub-Categories (Last 12 Months)":
    st.title("Category & Sub-Category Terlaris (1 Tahun Terakhir)")

    # agregasi data
    top_cat = (
        df.groupby(["Category", "Sub_Category"])
        .agg({
            "Quantity": "sum",
            "Revenue": "sum"
        })
        .sort_values("Quantity", ascending=False)
        .head(5)
        .reset_index()
    )

    labels = top_cat["Category"] + " | " + top_cat["Sub_Category"]

    # ===============================
    # GRAFIK 1 — QUANTITY
    # ===============================
    st.subheader("Top 5 Category & Sub-Category Berdasarkan Quantity")

    fig1, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(labels, top_cat["Quantity"])
    ax1.set_xlabel("Category | Subcategory")
    ax1.set_ylabel("Total Quantity Terjual")
    ax1.set_title("Top 5 Category & Subcategory Paling Banyak Dibeli")
    plt.xticks(rotation=25, ha="right")

    st.pyplot(fig1)

    # ===============================
    # GRAFIK 2 — REVENUE
    # ===============================
    st.subheader("Revenue dari Top 5 Category & Sub-Category")

    fig2, ax2 = plt.subplots(figsize=(9, 5))
    ax2.bar(labels, top_cat["Revenue"])
    ax2.set_xlabel("Category | Subcategory")
    ax2.set_ylabel("Total Revenue")
    ax2.set_title("Revenue dari 5 Category & Subcategory Terlaris")
    plt.xticks(rotation=25, ha="right")

    st.pyplot(fig2)

    # ===============================
    # TABEL DATA
    # ===============================
    st.subheader("Ringkasan Data")
    st.dataframe(top_cat)


# ===============================
# PROFIT REGION & PROVINCE
# ===============================
elif selected == "Regional & Provincial Profit Analysis":
    st.title("Wilayah & Provinsi Paling Menguntungkan")

    col1, col2 = st.columns(2)

    # =========================
    # PROFIT PER REGION
    # =========================
    with col1:
        profit_region = (
            df.groupby("Region")["Profit"]
            .sum()
            .sort_values(ascending=False)
        )

        st.subheader("Total Profit per Region")
        st.bar_chart(profit_region)

        # TABEL DESKRIPSI
        st.dataframe(
            profit_region
            .reset_index()
            .rename(columns={"Profit": "Total_Profit"})
        )

        top_region = profit_region.index[0]
        st.info(f"Region dengan profit tertinggi: **{top_region}**")

    # =========================
    # PROFIT PER PROVINSI (REGION TERBAIK)
    # =========================
    with col2:
        st.subheader(f"Total Profit per Provinsi di Region {top_region}")

        df_top_region = df[df["Region"] == top_region]

        profit_state = (
            df_top_region.groupby("State")["Profit"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(profit_state)

        # TABEL DESKRIPSI
        st.dataframe(
            profit_state
            .reset_index()
            .rename(columns={"Profit": "Total_Profit"})
        )


# ===============================
# TOP 10 PROFITABLE PRODUCTS
# ===============================
elif selected == "Top 10 Most Profitable Products":
    st.title("Top 10 Most Profitable Products")

    # Top 10 berdasarkan total profit
    top_products = (
        df.groupby("Product_Name")["Profit"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.subheader(" Total Profit per Produk")
    st.bar_chart(top_products)

    # Detail tambahan: quantity vs profit
    top10_detail = (
        df[df["Product_Name"].isin(top_products.index)]
        .groupby("Product_Name")
        .agg(
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum")
        )
        .sort_values("Total_Profit", ascending=False)
    )

    st.subheader(" Detail Profit & Quantity")
    st.dataframe(top10_detail.reset_index())

    # Insight: kontribusi Top 10 terhadap total profit
    total_profit = df["Profit"].sum()
    top10_profit = top_products.sum()
    contribution = (top10_profit / total_profit) * 100

    st.metric(
        label="Kontribusi Top 10 Produk terhadap Total Profit",
        value=f"{contribution:.2f}%"
    )

    st.caption(
        "Insight: Konsentrasi profit pada beberapa produk utama dapat menjadi "
        "indikasi peluang optimalisasi margin maupun risiko ketergantungan produk."
    )


# ===============================
# CATEGORY POPULARITY PER REGION
# ===============================
elif selected == "Category Popularity Across Regions":
    st.title("Popularitas Kategori Produk di Setiap Wilayah")

    # =================================================
    # AGREGASI DATA
    # =================================================
    category_region = (
        df.groupby(["Region", "Category"])["Revenue"]
        .sum()
        .reset_index()
    )

    # =================================================
    # VISUALISASI 1 — DISTRIBUSI KATEGORI PER WILAYAH
    # (GROUPED + WARNA CATEGORY + JARAK RAPI)
    # =================================================
    st.subheader("Distribusi Revenue Kategori di Setiap Wilayah")

    category_region = (
        df.groupby(["Region", "Category"])["Revenue"]
        .sum()
        .reset_index()
    )

    regions = category_region["Region"].unique()
    categories = category_region["Category"].unique()

    # warna konsisten per category
    color_map = {
        "Accessories": "#1f77b4",        # biru
        "Electronics": "#d62728",        # merah
        "Clothing & Apparel": "#2ca02c", # hijau
        "Furniture": "#9467bd",          # ungu
        "Office Supplies": "#ff7f0e"     # oranye
    }

    import numpy as np

    x = np.arange(len(regions))          # posisi region
    bar_width = 0.15                     # lebar bar
    offset = -(len(categories) / 2) * bar_width

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, category in enumerate(categories):
        values = []

        for region in regions:
            val = category_region[
                (category_region["Region"] == region) &
                (category_region["Category"] == category)
            ]["Revenue"]

            values.append(val.values[0] if not val.empty else 0)

        ax.bar(
            x + offset + i * bar_width,
            values,
            width=bar_width,
            label=category,
            color=color_map.get(category, "#7f7f7f")
        )

    ax.set_xlabel("Region")
    ax.set_ylabel("Total Revenue")
    ax.set_title("Distribusi Popularitas Kategori per Wilayah")

    ax.set_xticks(x)
    ax.set_xticklabels(regions)

    # legend di bawah
    ax.legend(
        title="Category",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3
    )

    plt.tight_layout()
    st.pyplot(fig)


    # =========================
    # TABEL 1 — DETAIL DISTRIBUSI
    # =========================
    st.subheader("Tabel Revenue Kategori per Wilayah")

    st.dataframe(
        category_region
        .sort_values(["Region", "Revenue"], ascending=[True, False])
    )

    st.divider()

    # =================================================
    # VISUALISASI 2 — KATEGORI DOMINAN PER WILAYAH
    # =================================================
    st.subheader("Kategori Paling Populer di Setiap Wilayah")

    top_category_per_region = (
        category_region
        .sort_values(["Region", "Revenue"], ascending=[True, False])
        .groupby("Region")
        .head(1)
        .reset_index(drop=True)
    )

    fig2, ax2 = plt.subplots(figsize=(9, 5))

    labels = (
        top_category_per_region["Region"]
        + " | "
        + top_category_per_region["Category"]
    )

    ax2.bar(labels, top_category_per_region["Revenue"])
    ax2.set_xlabel("Region | Category")
    ax2.set_ylabel("Total Revenue")
    ax2.set_title("Kategori Terpopuler di Tiap Wilayah")
    plt.xticks(rotation=25, ha="right")

    st.pyplot(fig2)

    # =========================
    # TABEL 2 — KATEGORI DOMINAN
    # =========================
    st.subheader("Tabel Kategori Terpopuler per Wilayah")

    st.dataframe(top_category_per_region)

    # =========================
    # VISUALISASI 2:
    # TABEL DESKRIPTIF
    # =========================


# ===============================
# REVENUE 2023 vs 2024
# ===============================
elif selected == "Revenue Trend: 2023 vs 2024":
    st.title("Perbandingan Pendapatan 2023 vs 2024")

    import matplotlib.pyplot as plt

    # ===============================
    # Total Revenue per Tahun
    # ===============================
    revenue_year = (
        df[df["Year"].isin(["2023", "2024"])]
        .groupby("Year")["Revenue"]
        .sum()
        .sort_index()
    )

    st.subheader(" Total Revenue per Tahun")
    st.bar_chart(revenue_year)
    st.dataframe(revenue_year.reset_index())

    # ===============================
    # Revenue Growth
    # ===============================
    if set(["2023", "2024"]).issubset(revenue_year.index):
        rev_2023 = revenue_year.loc["2023"]
        rev_2024 = revenue_year.loc["2024"]

        growth = ((rev_2024 - rev_2023) / rev_2023) * 100

        st.metric(
            label=" Revenue Growth (2023 → 2024)",
            value=f"{growth:.2f}%"
        )

    # ===============================
    # Breakdown Revenue per Category
    # ===============================
    st.subheader(" Breakdown Revenue per Category")

    category_year = (
        df[df["Year"].isin(["2023", "2024"])]
        .groupby(["Year", "Category"], as_index=False)["Revenue"]
        .sum()
    )

    st.dataframe(category_year)

    # ===============================
    # Pie Chart Revenue per Category
    # ===============================
    st.subheader(" Distribusi Revenue per Category (Persentase)")

    col1, col2 = st.columns(2)

    for year, col in zip(["2023", "2024"], [col1, col2]):
        data_year = (
            category_year[category_year["Year"] == year]
            .set_index("Category")["Revenue"]
        )

        with col:
            st.markdown(f"**Tahun {year}**")
            fig, ax = plt.subplots()
            ax.pie(
                data_year,
                labels=data_year.index,
                autopct="%1.1f%%",
                startangle=90
            )
            ax.axis("equal")
            st.pyplot(fig)

    st.caption(
        "Insight: Pie chart menunjukkan kontribusi masing-masing kategori "
        "terhadap total revenue pada tahun 2023 dan 2024. "
        "Perubahan proporsi mengindikasikan pergeseran kontribusi kategori."
    )