import pandas as pd
import streamlit as st
import logging
import config

# Configuración del Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Traemos la función de consulta SQL pura de config
query = getattr(config, 'query', None)
clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)

st.set_page_config(page_title="Órdenes - CRM", page_icon="📦")
st.title("📦 Órdenes de Venta (SQL Server)")

def load_orders_data():
    if not query:
        st.error("❌ No se encontró la función 'query' en config.py para conectar a SQL Server.")
        return pd.DataFrame()
    try:
        # Consulta directa a la tabla de SQL Server
        df = query("SELECT * FROM Orders")
        return df
    except Exception as e:
        st.error(f"❌ Error al consultar la tabla Orders en SQL Server: {e}")
        return pd.DataFrame()

# Ejecución de la carga
df_orders = load_orders_data()

if df_orders.empty:
    st.warning("⚠️ No se pudieron recuperar datos desde SQL Server o la tabla 'Orders' está vacía.")
else:
    if clean_dataframe_columns:
        df_orders = clean_dataframe_columns(df_orders)
        
    for col in df_orders.columns:
        df_orders[col] = df_orders[col].astype(str).str.strip()

    st.subheader(f"📋 Lista de Órdenes ({len(df_orders)} registros)")
    st.dataframe(df_orders, use_container_width=True)
    
    st.markdown("---")
    st.metric("Total Órdenes", len(df_orders))
