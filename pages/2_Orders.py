import pandas as pd
import streamlit as st
from config import query
import logging

logger = logging.getLogger(__name__)

# Importación de filtros
try:
    from utils.filters import (
        clean_dataframe_columns,
        create_partner_filter,
        apply_partner_filter,
        create_status_filter,
        apply_status_filter
    )
except ImportError:
    st.error("❌ No se pudo importar el módulo 'utils.filters'. Revisá que la carpeta exista.")

st.title("📦 Orders")

# --- LOAD DATA WITH CACHE ---
@st.cache_data(ttl=300)
def load_orders():
    try:
        df = query("SELECT * FROM Orders")
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Orders: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_partners():
    try:
        df = query("SELECT * FROM Partners")
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"Error cargando Partners: {e}")
        return pd.DataFrame()

try:
    # Cargar datos
    df_orders = load_orders()
    df_partners = load_partners()
    
    # CONTROL CRÍTICO: Si los datos vienen vacíos por falta de conexión, frenamos acá de forma limpia
    if df_orders.empty:
        st.warning("⚠️ No hay órdenes disponibles. Revisá la conexión a la base de datos o las credenciales en los logs.")
    else:
        # Limpiar columnas de forma segura
        df_orders = clean_dataframe_columns(df_orders)
        
        if not df_partners.empty:
            df_partners = clean_dataframe_columns(df_partners)
            
            # Forzar tipo string en columnas de cruce para evitar errores de .str accessor
            for col in df_orders.columns:
                if col in ['status', 'estado', 'nombre'] or 'id' in col:
                    df_orders[col] = df_orders[col].astype(str).str.strip()
            
            for col in df_partners.columns:
                if col in ['status', 'estado', 'nombre'] or 'id' in col:
                    df_partners[col] = df_partners[col].astype(str).str.strip()
        
        # --- FILTROS ---
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_partners.empty and 'nombre' in df_partners.columns:
                partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
                df_orders = apply_partner_filter(
                    df_orders, 
                    partner_seleccionado, 
                    df_partners
                )
            else:
                st.caption("Filtro de clientes no disponible (tabla de Partners vacía)")
        
        with col2:
            if "status" in df_orders.columns and not df_orders.empty:
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
            c1, c2 = st.columns(2)
            
            with c1:
                status_counts = df_orders["status"].value_counts()
                st.bar_chart(status_counts)
            
            with c2:
                st.metric("Total Órdenes", len(df_orders))

except Exception as e:
    st.error(f"❌ Error en la ejecución de la página: {str(e)}")
    logger.error(f"Error general en página orders: {e}")
