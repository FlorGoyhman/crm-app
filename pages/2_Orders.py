import streamlit as st
from config import query

st.title("📦 Orders")

df = query("SELECT * FROM Orders")

# 👇 PEGÁS ESTO ACÁ
if "status" in df.columns:
    filtro = st.selectbox(
        "Filtrar estado",
        ["Todos"] + list(df["status"].unique())
    )

    if filtro != "Todos":
        df = df[df["status"] == filtro]
else:
    st.warning("La tabla no tiene columna 'status'")

st.dataframe(df, use_container_width=True)