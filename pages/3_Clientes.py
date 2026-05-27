import pandas as pd
import streamlit as st
from config import query, get_conn
import logging

logger = logging.getLogger(__name__)

# Intentar importar filtros de forma segura
try:
    from utils.filters import (
        clean_dataframe_columns,
        create_partner_filter,
        apply_partner_filter
    )
except ImportError as e:
    st.error(f"❌ Error de importación: {e}")

st.title("👤 Clientes")

# --- LOAD DATA ---
@st.cache_data(ttl=300)
def load_partners_data():
    try:
        df = query("SELECT * FROM Partners")
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Partners en página clientes: {e}")
        return pd.DataFrame()

try:
    # Cargar datos de partners
    df_partners = load_partners_data()
    
    # CONTROL CRÍTICO: Si la tabla viene vacía por error de credenciales, frena limpiamente acá
    if df_partners.empty:
        st.warning("⚠️ No se pudieron cargar los datos de los clientes. Revisá la configuración de las credenciales de Google Sheets en los Secrets de Streamlit.")
    else:
        # Limpiar columnas
        df_partners = clean_dataframe_columns(df_partners)
        
        # Asegurar tipo string antes de aplicar filtros para evitar errores de .str accessor
        for col in df_partners.columns:
            if col in ['nombre', 'estado', 'status'] or 'id' in col:
                df_partners[col] = df_partners[col].astype(str).str.strip()
        
        # --- FILTROS ---
        if 'nombre' in df_partners.columns:
            partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
            df_filtered = apply_partner_filter(df_partners, partner_seleccionado, df_partners)
        else:
            df_filtered = df_partners.copy()
            st.info("Columna 'nombre' no encontrada para filtrar.")
            
        # --- MOSTRAR RESULTADOS ---
        st.subheader(f"📋 Lista de Clientes ({len(df_filtered)} registros)")
        st.dataframe(df_filtered, use_container_width=True)
        
        # --- MÉTRICAS ---
        st.markdown("---")
        st.metric(label="Total Clientes Registrados", value=len(df_partners))

except Exception as e:
    st.error(f"❌ Error inesperado en la página: {str(e)}")
    logger.error(f"Error general en página clientes: {e}")
