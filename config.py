import os
import logging
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración básica del Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. PRIMERO DECLARAMOS EL CLIENTE ---
def get_gsheet_client():
    """Inicializa y devuelve el cliente de Google Sheets usando los Secrets de Streamlit"""
    try:
        import streamlit as st
        # Cargamos las credenciales desde los secrets de Streamlit Cloud
        creds_dict = st.secrets["gcs_connections"]["gspreadsheet"]
        
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Error crítico al autenticar en Google Sheets: {e}")
        raise e

# --- 2. SEGUNDO DECLARAMOS LA FUNCIÓN QUE USA AL CLIENTE ---
def get_gsheet_data(spreadsheet_name, sheet_name):
    """Obtiene datos de una pestaña de Google Sheets convirtiendo celdas puras a DataFrame"""
    try:
        # Ahora sí encuentra la función porque está declarada arriba
        client = get_gsheet_client()
        sheet = client.open(spreadsheet_name).worksheet(sheet_name)
        
        # Traemos todas las celdas de la hoja como una lista de listas
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) == 0:
            logger.warning(f"La pestaña '{sheet_name}' está vacía.")
            return pd.DataFrame()
            
        # La primera fila contiene los encabezados reales (product_id, name, etc.)
        headers = [str(h).strip() for h in all_values[0]]
        rows = all_values[1:]
        
        # Creamos el DataFrame de forma segura
        df = pd.DataFrame(rows, columns=headers)
        return df
        
    except Exception as e:
        logger.error(f"Error en get_gsheet_data al leer {sheet_name}: {e}")
        return pd.DataFrame()

# --- 3. FUNCIONES AUXILIARES DE LIMPIEZA ---
def clean_dataframe_columns(df):
    """Limpia los espacios y pasa a minúsculas los nombres de las columnas"""
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
