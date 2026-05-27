import pandas as pd
import streamlit as st
import logging

# CONFIGURACIÓN DEL LOGGER
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config

get_gsheet_data = getattr(config, 'get_gsheet_data', None)
clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
query = getattr(config, 'query', None)

try:
    from utils.filters import (
        create_partner_filter,
        apply_partner_filter,
        create_status_filter,
        apply_status_filter
    )
except ImportError as e:
    st.error(f"❌ Error de importación de filtros: {e}")

st.title("📦 Orders")

@st.cache_data(ttl=300)
def load_orders_data():
    try:
        if get_gsheet_data is not None:
            df = get_gsheet_data("Python", "Orders")
        elif query is not None:
            df = query("SELECT * FROM Orders")
        else:
            return pd.DataFrame()
            
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Orders: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_partners_data():
    try:
        if get_gsheet_data is not None:
            df = get_gsheet_data("Python", "Partners")
        elif query is not None:
            df = query("SELECT * FROM Partners")
        else:
            return pd.DataFrame()
            
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Partners en Orders: {e}")
        return pd.DataFrame()

try:
    df_orders = load_orders_data()
    df_partners = load_partners_data()
    
    if df_orders.empty:
        st.warning("⚠️ No se pudieron cargar las órdenes. Comprobá que la pestaña 'Orders' exista en tu archivo de Google Sheets.")
    else:
        if clean_dataframe_columns is not None:
            df_orders = clean_dataframe_columns(df_orders)
            df_partners = clean_dataframe_columns(df_partners)
        
        # Forzar strings para evitar errores de formato
        for col in df_orders.columns:
            if col in ['status', 'estado', 'nombre'] or 'id' in col:
                df_orders[col] = df_orders[col].astype(str).str.strip()
        
        if not df_partners.empty:
            for col in df_partners.columns:
                if col in ['status', 'estado', 'nombre'] or 'id' in col:
                    df_partners[col] = df_partners[col].astype(str).str.strip()
        
        # Filtros en pantalla
        col1, col2 = st.columns(2)
        with col1:
            if not df_partners.empty and 'nombre' in df_partners.columns:
                partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
                df_orders = apply_partner_filter(df_orders, partner_seleccionado, df_partners)
            else:
                st.caption("Filtro de clientes no disponible")
        
        with col2:
            if "status" in df_orders.columns and not df_orders.empty:
                status_seleccionado = create_status_filter(df_orders, column="status", key="orders_status", label="Filtrar estado")
                df_orders = apply_status_filter(df_orders, status_seleccionado, column="status")
        
        st.subheader(f"📋 Órdenes ({len(df_orders)} registros)")
        st.dataframe(df_orders, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error inesperado en la página: {str(e)}")
