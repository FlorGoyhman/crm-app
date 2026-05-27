import pandas as pd
import streamlit as st
import config

st.set_page_config(page_title="Productos - CRM", page_icon="👤")
st.title("👤 Productos / Clientes")

def load_data_direct():
    get_gsheet_data = getattr(config, 'get_gsheet_data', None)
    clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
    
    if not get_gsheet_data:
        st.error("❌ No se encontró la función 'get_gsheet_data' en config.py.")
        return pd.DataFrame()
        
    try:
        # Llamamos directo a la pestaña real
        df = get_gsheet_data("Python", "Products")
        
        if df is None or df.empty:
            return pd.DataFrame()
            
        if clean_dataframe_columns:
            df = clean_dataframe_columns(df)
            
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"❌ Error al procesar Google Sheets: {e}")
        return pd.DataFrame()

# Ejecución
df_products = load_data_direct()

if df_products.empty:
    st.warning("⚠️ No se pudieron recuperar datos de la pestaña 'Products'.")
else:
    st.subheader(f"📋 Lista de registros ({len(df_products)})")
    st.dataframe(df_products, use_container_width=True)
    
    st.markdown("---")
    st.metric("Total Productos", len(df_products))
