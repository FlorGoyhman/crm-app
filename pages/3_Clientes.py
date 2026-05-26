import streamlit as st
from config import query

st.title("🧑 Clientes")

df = query("SELECT * FROM Partners")

st.dataframe(df, use_container_width=True)