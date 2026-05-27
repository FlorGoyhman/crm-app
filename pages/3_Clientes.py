import pandas as pd
import streamlit as st
import config

st.set_page_config(page_title="Clientes - CRM", page_icon="👤")
st.title("👤 Clientes y Partners (SQL Server)")

# Traemos la función de consulta de forma segura
query_func = getattr(config, 'query', None)
clean_func = getattr(config, 'clean_dataframe_columns', None)

if not query_func:
    st.error("❌ No se encontró la función 'query' en config.py.")
else:
    try:
        # Consulta limpia a SQL Server
        df_partners = query_func("SELECT * FROM Partners")
        
        if df_partners is None or df_partners.empty:
            st.warning("⚠️ La consulta devolvió una tabla vacía o no se pudo conectar.")
        else:
            if clean_func:
                df_partners = clean_func(df_partners)
                
            for col in df_partners.columns:
                df_partners[col] = df_partners[col].astype(str).str.strip()

            st.subheader(f"📋 Lista de Clientes ({len(df_partners)} registros)")
            st.dataframe(df_partners, use_container_width=True)
            
            st.markdown("---")
            st.metric("Total Clientes", len(df_partners))
            
    except Exception as e:
        st.error(f"❌ Error en la ejecución de la página: {e}")
