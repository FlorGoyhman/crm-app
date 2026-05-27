import os
import pandas as pd
import pyodbc

def get_sql_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=TU_SERVIDOR_AQUÍ;'       # <-- Poné tu Servidor/IP real
            'DATABASE=TU_BASE_DE_DATOS;'     # <-- Poné tu Base de Datos real
            'UID=TU_USUARIO;'                # <-- Tu usuario
            'PWD=TU_CONTRASEÑA;'             # <-- Tu contraseña
            'Timeout=30;'
        )
        return conn
    except Exception as e:
        raise Exception(f"Fallo en la conexión física de red a SQL Server: {e}")

def query(sql_expression):
    conn = None
    try:
        conn = get_sql_connection()
        df = pd.read_sql(sql_expression, conn)
        return df
    except Exception as e:
        raise Exception(f"Fallo al procesar la query en la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def clean_dataframe_columns(df):
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
