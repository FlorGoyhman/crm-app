import pandas as pd
import streamlit as st
import config

st.set_page_config(page_title="Órdenes - CRM", page_icon="📦")
st.title("📦 Órdenes de Venta (SQL Server)")

query_func = getattr(config, 'query', None)
clean_func = getattr(config, 'clean_dataframe_columns', None)

if not query_func:
    st.error("❌ No se encontró la función 'query' en config.py.")
else:
    try:
        # Consulta limpia a SQL Server
        df_orders = query_func("SELECT * FROM Orders")
        
        if df_orders is None or df_orders.empty:
            st.warning("⚠️ La consulta devolvió una tabla vacía o no se pudo conectar.")
        else:
            if clean_func:
                df_orders = clean_func(df_orders)
                
            for col in df_orders.columns:
                df_orders[col] = df_orders[col].astype(str).str.strip()

            st.subheader(f"📋 Lista de Órdenes ({len(df_orders)} registros)")
            st.dataframe(df_orders, use_container_width=True)
            
            st.markdown("---")
            st.metric("Total Órdenes", len(df_orders))
            
    except Exception as e:
        st.error(f"❌ Error en la ejecución de la página: {e}")
