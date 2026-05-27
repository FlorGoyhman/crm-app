import pandas as pd
import streamlit as st
# Cambiamos 'query' por las funciones de gsheets
from config import get_gsheet_data, clean_dataframe_columns 
import logging

logger = logging.getLogger(__name__)

try:
    from utils.filters import (
        create_partner_filter,
        apply_partner_filter
    )
except ImportError as e:
    st.error(f"❌ Error de importación: {e}")

st.title("👤 Clientes")

# --- LOAD DATA DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=300)
def load_partners_data():
    try:
        # Reemplazá "CON_EL_NOMBRE_EXACTO_DE_TU_PLANILLA" por el nombre de tu archivo de Sheets
        df = get_gsheet_data("CON_EL_NOMBRE_EXACTO_DE_TU_PLANILLA", "Partners") 
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Partners desde GSheets: {e}")
        return pd.DataFrame()

try:
    df_partners = load_partners_data()
    
    if df_partners.empty:
        st.warning("⚠️ No se pudieron cargar los datos de los clientes. Comprobá que el nombre de la planilla sea el correcto y que esté compartida con el mail de la cuenta de servicio.")
    else:
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
