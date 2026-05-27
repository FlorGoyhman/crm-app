import pandas as pd
import streamlit as st
import logging

# CONFIGURACIÓN DEL LOGGER (Faltaba esto y por eso caía en el cartel amarillo)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config

get_gsheet_data = getattr(config, 'get_gsheet_data', None)
clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
query = getattr(config, 'query', None)

try:
    from utils.filters import (
        create_partner_filter,
        apply_partner_filter
    )
except ImportError as e:
    st.error(f"❌ Error de importación de filtros: {e}")

st.title("👤 Clientes")

@st.cache_data(ttl=300)
def load_partners_data():
    try:
        if get_gsheet_data is not None:
            df = get_gsheet_data("Python", "Products")
        elif query is not None:
            df = query("SELECT * FROM Partners")
        else:
            st.error("❌ No se encontró ninguna función de consulta en config.py")
            return pd.DataFrame()
            
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Partners: {e}")
        return pd.DataFrame()

try:
    df_partners = load_partners_data()
    
    if df_partners.empty:
        st.warning("⚠️ No se pudieron cargar los datos. Esto puede pasar si el archivo 'Python' en Google Sheets no tiene una pestaña llamada 'Partners' o si falta compartirlo con el mail de la cuenta de servicio.")
    else:
        if clean_dataframe_columns is not None:
            df_partners = clean_dataframe_columns(df_partners)
        
        for col in df_partners.columns:
            if col in ['nombre', 'estado', 'status'] or 'id' in col:
                df_partners[col] = df_partners[col].astype(str).str.strip()
        
        if 'nombre' in df_partners.columns:
            partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
            df_filtered = apply_partner_filter(df_partners, partner_seleccionado, df_partners)
        else:
            df_filtered = df_partners.copy()
            
        st.subheader(f"📋 Lista de Clientes ({len(df_filtered)} registros)")
        st.dataframe(df_filtered, use_container_width=True)
        
        st.markdown("---")
        st.metric(label="Total Clientes Registrados", value=len(df_partners))

except Exception as e:
    st.error(f"❌ Error inesperado en la página: {str(e)}")
