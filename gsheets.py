import pandas as pd
import gspread
import logging
import streamlit as st
from config import get_gsheet_client

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache 5 minutos
def get_gsheet(sheet_name, worksheet_name):
    """
    Obtiene datos de Google Sheets (cacheado)
    
    Args:
        sheet_name: Nombre del Google Sheet
        worksheet_name: Nombre de la pestaña
    
    Returns:
        DataFrame con los datos
    """
    try:
        client = get_gsheet_client()
        sheet = client.open(sheet_name).worksheet(worksheet_name)
        data = sheet.get_all_records()
        
        if not data:
            logger.warning(f"No hay datos en {sheet_name}/{worksheet_name}")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        logger.info(f"Cargados {len(df)} registros de {worksheet_name}")
        return df
    
    except Exception as e:
        logger.error(f"Error obteniendo {worksheet_name}: {e}")
        return pd.DataFrame()

def refresh_gsheet_cache():
    """Limpia el caché de Google Sheets manualmente"""
    get_gsheet.clear()
    logger.info("Caché de Google Sheets limpiado")
