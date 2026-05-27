import pandas as pd
import streamlit as st
import logging
import config  # Importamos tu config.py

# 1. Configuración de seguridad para el Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Traemos las funciones de config de forma segura
get_gsheet_data = getattr(config, 'get_gsheet_data', None)
clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
query = getattr(config, 'query', None)

# 3. Intentamos traer los filtros de la carpeta utils
try:
    from utils.filters import (
        create_partner_filter,
        apply_partner_filter
    )
except ImportError:
    st.error("❌ No se encontró el archivo 'utils/filters.py'.")

st.set_page_config(page_title="Clientes - CRM", page_icon="👤")
st.title("👤 Clientes")

# --- FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data(ttl=300)
def load_data():
    try:
        # BUSCA EN GOOGLE SHEETS
        # Cambiá "Partners" por el nombre exacto de la pestaña donde están tus clientes
        if get_gsheet_data:
            df = get_gsheet_data("Python", "Partners")
            if df is not None and not df.empty:
                return df
        
        # SI FALLA GSHEETS, BUSCA EN SQL LOCAL (PLAN B)
        if query:
            return query("SELECT * FROM Partners")
            
        return pd.DataFrame()
    except Exception as e:
        # Ahora el logger está definido, así que no dará error
        logger.error(f"Error en carga de clientes: {e}")
        return pd.DataFrame()

# --- EJECUCIÓN PRINCIPAL ---
try:
    df_partners = load_data()

    if df_partners.empty:
        st.warning("⚠️ No se encontraron datos en la pestaña 'Partners'.")
        st.info("💡 REVISÁ ESTO: En tu Google Sheets 'Python', la pestaña debe llamarse exactamente Partners. Si se llama 'Hoja 1' o 'Clientes', renombrala o cambiá el nombre en el código.")
    else:
        # Limpieza de columnas
        if clean_dataframe_columns:
            df_partners = clean_dataframe_columns(df_partners)
        
        # Formateo de texto para evitar errores
        for col in df_partners.columns:
            df_partners[col] = df_partners[col].astype(str).str.strip()

        # Aplicar filtros si existe la columna 'nombre'
        if 'nombre' in df_partners.columns:
            seleccion = create_partner_filter(df_partners, column_name="nombre")
            df_display = apply_partner_filter(df_partners, seleccion, df_partners)
        else:
            df_display = df_partners.copy()

        # Mostrar Tabla
        st.subheader(f"📋 Lista de registros ({len(df_display)})")
        st.dataframe(df_display, use_container_width=True)
        
        # Métrica
        st.markdown("---")
        st.metric("Total Clientes", len(df_partners))

except Exception as e:
    st.error(f"❌ Error crítico en la página: {e}")
