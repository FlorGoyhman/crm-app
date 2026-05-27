import pandas as pd
import streamlit as st
import config

st.set_page_config(page_title="Productos - CRM", page_icon="👤")
st.title("👤 Productos / Clientes")

# --- FUNCIÓN DE CARGA DIRECTA DESDE GSHEETS ---
def load_data_direct():
    # Traemos la función de config de forma segura
    get_gsheet_data = getattr(config, 'get_gsheet_data', None)
    clean_dataframe_columns = getattr(config, 'clean_dataframe_columns', None)
    
    if not get_gsheet_data:
        st.error("❌ No se encontró la función 'get_gsheet_data' en config.py.")
        return pd.DataFrame()
        
    try:
        # LLAMADO EXCLUSIVO A GOOGLE SHEETS
        df = get_gsheet_data("Python", "Products")
        
        if df is None or df.empty:
            return pd.DataFrame()
            
        # Limpieza de columnas si la función existe
        if clean_dataframe_columns:
            df = clean_dataframe_columns(df)
            
        # Forzar formato texto string para evitar errores visuales
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        # Si Google Sheets falla, queremos ver el error real en rojo
        st.error(f"❌ Error de conexión con Google Sheets: {e}")
        return pd.DataFrame()

# --- EJECUCIÓN ---
df_products = load_data_direct()

if df_products.empty:
    st.warning("⚠️ No se pudieron recuperar datos de la pestaña 'Products'.")
    st.info("💡 Asegurate de que en config.py la función get_gsheet_data use 'sheet.get_all_values()' y no un método viejo.")
else:
    st.subheader(f"📋 Lista de registros ({len(df_products)})")
    st.dataframe(df_products, use_container_width=True)
    
    st.markdown("---")
    st.metric("Total Productos", len(df_products))
