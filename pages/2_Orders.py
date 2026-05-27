import pandas as pd
import streamlit as st
from config import query
import logging

logger = logging.getLogger(__name__)

# Importación correcta desde tu carpeta utils
from utils.filters import (
    clean_dataframe_columns,
    create_partner_filter,
    apply_partner_filter,
    create_status_filter,
    apply_status_filter
)

st.title("📦 Orders")

# --- LOAD DATA WITH CACHE ---
@st.cache_data(ttl=300)
def load_orders():
    try:
        return query("SELECT * FROM Orders")
    except Exception as e:
        logger.error(f"Error cargando Orders: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_partners():
    try:
        return query("SELECT * FROM Partners")
    except Exception as e:
        logger.error(f"Error cargando Partners: {e}")
        return pd.DataFrame()

try:
    # Cargar datos
    df_orders = load_orders()
    df_partners = load_partners()
    
    # Limpiar columnas
    df_orders = clean_dataframe_columns(df_orders)
    df_partners = clean_dataframe_columns(df_partners)
    
    if df_orders.empty:
        st.warning("⚠️ No hay órdenes para mostrar")
    else:
        # --- FILTROS ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por cliente
            partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
            df_orders = apply_partner_filter(
                df_orders, 
                partner_seleccionado, 
                df_partners
            )
        
        with col2:
            # Filtro por estado de la orden
            if "status" in df_orders.columns:
                status_seleccionado = create_status_filter(
                    df_orders,
                    column="status",
                    key="orders_status",
                    label="Filtrar estado"
                )
                df_orders = apply_status_filter(
                    df_orders,
                    status_seleccionado,
                    column="status"
                )
        
        # --- MOSTRAR RESULTADOS ---
        st.subheader(f"📋 Órdenes ({len(df_orders)} registros)")
        st.dataframe(df_orders, use_container_width=True)
        
        # --- ESTADÍSTICAS ---
        if "status" in df_orders.columns and not df_orders.empty:
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df_orders["status"].value_counts()
                st.bar_chart(status_counts)
            
            with col2:
                st.metric("Total Órdenes", len(df_orders))

except Exception as e:
    st.error(f"❌ Error al cargar órdenes: {str(e)}")
    logger.error(f"Error en página orders: {e}")
