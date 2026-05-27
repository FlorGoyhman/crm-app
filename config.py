import os
import logging
import pandas as pd
import pyodbc  # Importante para conectar a SQL Server

# Configuración básica del Logger para que no tire error de inicialización
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sql_connection():
    """Establece la conexión física con la base de datos SQL Server"""
    try:
        # Reemplazá estos valores con las credenciales reales de tu SQL Server
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=TU_SERVIDOR_AQUÍ;'       # <-- Poné tu Servidor/IP acá
            'DATABASE=TU_BASE_DE_DATOS;'     # <-- Poné el nombre de tu BD
            'UID=TU_USUARIO;'                # <-- Tu usuario de SQL
            'PWD=TU_CONTRASEÑA;'             # <-- Tu contraseña de SQL
            'Timeout=30;'
        )
        return conn
    except Exception as e:
        logger.error(f"Error crítico al conectar a SQL Server: {e}")
        raise e

def query(sql_expression):
    """Ejecuta una consulta SQL y devuelve un DataFrame de Pandas limpio"""
    conn = None
    try:
        conn = get_sql_connection()
        # Leemos la consulta directamente pasándole la conexión activa
        df = pd.read_sql(sql_expression, conn)
        return df
    except Exception as e:
        logger.error(f"Error al ejecutar la consulta SQL [{sql_expression}]: {e}")
        return pd.DataFrame()
    finally:
        # Nos aseguramos de cerrar siempre la conexión para no saturar el servidor
        if conn:
            conn.close()

def clean_dataframe_columns(df):
    """Limpia los espacios y pasa a minúsculas los nombres de las columnas"""
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
