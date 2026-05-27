import pandas as pd
import streamlit as st
import logging
import config

# Configuración del Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

get_gsheet_data = getattr(config, 'get_gsheet_data', None)
clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
query = getattr(config, 'query', None)

try:
    from utils.filters import (
        create_partner_filter,
        apply_partner_filter
    )
except ImportError:
    st.error("❌ No se encontró el archivo 'utils/filters.py'.")

st.set_page_config(page_title="Productos - CRM", page_icon="👤")
st.title("👤 Productos / Clientes")

@st.cache_data(ttl=300)
def load_data():
    try:
        # Forzamos a que busque la pestaña real "Products"
        if get_gsheet_data:
            df = get_gsheet_data("Python", "Products")
            if df is not None and not df.empty:
                return df
        if query:
            return query("SELECT * FROM Products")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error en carga de Products: {e}")
        return pd.DataFrame()

try:
    df_products = load_data()

    if df_products.empty:
        st.warning("⚠️ No se encontraron datos en la pestaña 'Products'. Verificá que la hoja no esté completamente vacía.")
    else:
        if clean_dataframe_columns:
            df_products = clean_dataframe_columns(df_products)
        
        for col in df_products.columns:
            df_products[col] = df_products[col].astype(str).str.strip()

        # Buscamos de forma flexible si hay columna de nombre para filtrar
        nombre_col = 'product_name' if 'product_name' in df_products.columns else ('name' if 'name' in df_products.columns else None)
        
        if nombre_col:
            seleccion = create_partner_filter(df_products, column_name=nombre_col)
            df_display = apply_partner_filter(df_products, seleccion, df_products)
        else:
            df_display = df_products.copy()

        st.subheader(f"📋 Lista de registros ({len(df_display)})")
        st.dataframe(df_display, use_container_width=True)
        
        st.markdown("---")
        st.metric("Total Productos", len(df_products))

except Exception as e:
    st.error(f"❌ Error crítico en la página: {e}")
