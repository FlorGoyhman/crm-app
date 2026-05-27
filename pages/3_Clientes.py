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

st.set_page_config(page_title="Clientes - CRM", page_icon="👤")
st.title("👤 Clientes y Partners (SQL Server)")

def load_sql_data():
    if not query:
        st.error("❌ No se encontró la función 'query' en config.py para conectar a SQL Server.")
        return pd.DataFrame()
    try:
        # Consulta directa a la tabla de SQL Server
        df = query("SELECT * FROM Partners")
        return df
    except Exception as e:
        st.error(f"❌ Error al consultar la tabla Partners en SQL Server: {e}")
        return pd.DataFrame()

# Ejecución de la carga
df_partners = load_sql_data()

if df_partners.empty:
    st.warning("⚠️ No se pudieron recuperar datos desde SQL Server o la tabla 'Partners' está vacía.")
else:
    if clean_dataframe_columns:
        df_partners = clean_dataframe_columns(df_partners)
        
    # Limpieza básica de strings
    for col in df_partners.columns:
        df_partners[col] = df_partners[col].astype(str).str.strip()

    st.subheader(f"📋 Lista de Clientes ({len(df_partners)} registros)")
    st.dataframe(df_partners, use_container_width=True)
    
    st.markdown("---")
    st.metric("Total Clientes", len(df_partners))
