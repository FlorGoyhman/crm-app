import pandas as pd
import streamlit as st
import logging
import config  # Importamos tu config.py

# 1. Configuración de seguridad para el Logger (evita el error 'name logger is not defined')
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
        apply_partner_filter,
        create_status_filter,
        apply_status_filter
    )
except ImportError:
    st.error("❌ No se pudieron importar los filtros desde 'utils/filters.py'.")

st.set_page_config(page_title="Órdenes - CRM", page_icon="📦")
st.title("📦 Orders")

# --- FUNCIÓN PARA CARGAR LAS ÓRDENES ---
@st.cache_data(ttl=300)
def load_orders_data():
    try:
        # BUSCA EN GOOGLE SHEETS
        # Cambiá "Orders" por "Payments" si querés leer la pestaña que ya tenés creada
        if get_gsheet_data:
            df = get_gsheet_data("Python", "Orders")
            if df is not None and not df.empty:
                return df
        
        # PLAN B: BUSCA EN SQL LOCAL
        if query:
            return query("SELECT * FROM Orders")
            
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando Órdenes: {e}")
        return pd.DataFrame()

# --- FUNCIÓN PARA CARGAR LOS CLIENTES (Para usar en los filtros) ---
@st.cache_data(ttl=300)
def load_partners_data():
    try:
        if get_gsheet_data:
            df = get_gsheet_data("Python", "Partners")
            if df is not None and not df.empty:
                return df
        if query:
            return query("SELECT * FROM Partners")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando Partners para filtros: {e}")
        return pd.DataFrame()

# --- EJECUCIÓN PRINCIPAL ---
try:
    df_orders = load_orders_data()
    df_partners = load_partners_data()
    
    if df_orders.empty:
        st.warning("⚠️ No se pudieron cargar las órdenes de la pestaña 'Orders'.")
        st.info("💡 REVISÁ ESTO: En tu archivo 'Python', la pestaña de órdenes debe llamarse exactamente Orders. Si querés usar los datos existentes, cambiá el nombre de tu pestaña 'Payments' a 'Orders', o modificá la línea 32 del código por 'Payments'.")
    else:
        # Limpieza de columnas de forma segura
        if clean_dataframe_columns:
            df_orders = clean_dataframe_columns(df_orders)
            if not df_partners.empty:
                df_partners = clean_dataframe_columns(df_partners)
        
        # Asegurar formato texto para evitar caídas del filtro .str
        for col in df_orders.columns:
            df_orders[col] = df_orders[col].astype(str).str.strip()
            
        if not df_partners.empty:
            for col in df_partners.columns:
                df_partners[col] = df_partners[col].astype(str).str.strip()
        
        # --- DISEÑO DE FILTROS EN PANTALLA ---
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_partners.empty and 'nombre' in df_partners.columns:
                partner_seleccionado = create_partner_filter(df_partners, column_name="nombre")
                df_orders = apply_partner_filter(df_orders, partner_seleccionado, df_partners)
            else:
                st.caption("Filtro por Cliente no disponible (falta tabla Partners)")
        
        with col2:
            # Busca automáticamente si la columna de estado se llama 'status' o 'estado'
            status_col = 'status' if 'status' in df_orders.columns else ('estado' if 'estado' in df_orders.columns else None)
            if status_col and not df_orders.empty:
                status_seleccionado = create_status_filter(df_orders, column=status_col, key="orders_status", label="Filtrar estado")
                df_orders = apply_status_filter(df_orders, status_seleccionado, column=status_col)
        
        # --- TABLA DE RESULTADOS ---
        st.subheader(f"📋 Órdenes ({len(df_orders)} registros)")
        st.dataframe(df_orders, use_container_width=True)
        
        # Métrica lateral o inferior
        st.markdown("---")
        st.metric("Total Órdenes Registradas", len(df_orders))

except Exception as e:
    st.error(f"❌ Error crítico en la página de Órdenes: {e}")
