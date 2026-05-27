import os
import subprocess
import sys

# Forzamos a la nube a instalar gspread si o si al arrancar
try:
    import gspread
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread"])
import streamlit as st
from config import query
import logging

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="CRM App",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 CRM Dashboard")

try:
    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df_clientes = query("SELECT COUNT(*) as total FROM Partners")
        total_clientes = df_clientes.iloc[0, 0]
        st.metric("👥 Total Clientes", total_clientes)
    
    with col2:
        df_orders = query(
            "SELECT COUNT(*) as total FROM Orders WHERE status != 'Completado'"
        )
        total_pendientes = df_orders.iloc[0, 0] if not df_orders.empty else 0
        st.metric("📦 Órdenes Pendientes", total_pendientes)
    
    with col3:
        df_payments = query(
            "SELECT SUM(CAST(amount AS FLOAT)) as total FROM Payments WHERE status = 'Completado'"
        )
        total_pagos = df_payments.iloc[0, 0] if not df_payments.empty else 0
        st.metric("💰 Total Pagos", f"${total_pagos:,.2f}")
    
    # --- SEPARADOR ---
    st.markdown("---")
    
    # --- INFORMACIÓN ---
    st.info("📌 Usa el menú lateral para acceder a las diferentes secciones de la aplicación")
    
    # --- ESTADÍSTICAS ADICIONALES ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Últimas Órdenes")
        df_last_orders = query("SELECT TOP 5 * FROM Orders ORDER BY order_id DESC")
        st.dataframe(df_last_orders, use_container_width=True)
    
    with col2:
        st.subheader("💳 Últimos Pagos")
        df_last_payments = query("SELECT TOP 5 * FROM Payments ORDER BY payment_id DESC")
        st.dataframe(df_last_payments, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar dashboard: {str(e)}")
    logger.error(f"Dashboard error: {e}")
