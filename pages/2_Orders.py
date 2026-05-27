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
        create_status_filter,
        apply_status_filter
    )
except ImportError:
    st.error("❌ No se pudieron importar los filtros.")

st.set_page_config(page_title="Pagos - CRM", page_icon="📦")
st.title("📦 Payments / Orders")

@st.cache_data(ttl=300)
def load_payments_data():
    try:
        # Forzamos a que busque tu pestaña real "Payments"
        if get_gsheet_data:
            df = get_gsheet_data("Python", "Payments")
            if df is not None and not df.empty:
                return df
        if query:
            return query("SELECT * FROM Payments")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando Payments: {e}")
        return pd.DataFrame()

try:
    df_payments = load_payments_data()
    
    if df_payments.empty:
        st.warning("⚠️ No se pudieron cargar los datos de la pestaña 'Payments'.")
    else:
        if clean_dataframe_columns:
            df_payments = clean_dataframe_columns(df_payments)
        
        for col in df_payments.columns:
            df_payments[col] = df_payments[col].astype(str).str.strip()
        
        # Filtro inteligente usando la columna 'status' que se ve en tu Sheets
        status_col = 'status' if 'status' in df_payments.columns else None
        
        if status_col and not df_payments.empty:
            status_seleccionado = create_status_filter(df_payments, column=status_col, key="payments_status", label="Filtrar por Estado de Pago")
            df_payments_filtered = apply_status_filter(df_payments, status_seleccionado, column=status_col)
        else:
            df_payments_filtered = df_payments.copy()
        
        st.subheader(f"📋 Lista de Pagos ({len(df_payments_filtered)} registros)")
        st.dataframe(df_payments_filtered, use_container_width=True)
        
        st.markdown("---")
        st.metric("Total Transacciones", len(df_payments))

except Exception as e:
    st.error(f"❌ Error crítico en la página de Pagos: {e}")
