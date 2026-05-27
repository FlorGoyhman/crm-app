import pandas as pd
import gspread
import logging
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from oauth2client.service_account import ServiceAccountCredentials

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pyodbc may not be available in some cloud runtimes (Streamlit Cloud).
# Import lazily and handle absence so the module can be imported even when
# the DB driver isn't installed. Features that require DB will raise
# informative errors at runtime.
try:
    import pyodbc  # type: ignore
    HAS_PYODBC = True
except Exception:
    pyodbc = None
    HAS_PYODBC = False

# Cargar variables de entorno (si está disponible)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    logger.warning("python-dotenv no está instalado; omitiendo carga de .env")

# Variables de conexión desde .env
SQL_SERVER = os.getenv("SQL_SERVER", "DESKTOP-D5LVCOT\\SQLEXPRESS")
SQL_DATABASE = os.getenv("SQL_DATABASE", "BaseFlor")
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH", "credenciales.json")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# SQLAlchemy engine cache
_engine = None

def get_engine():
    """Devuelve un SQLAlchemy engine usando el driver ODBC configurado."""
    global _engine
    if not HAS_PYODBC:
        logger.error("pyodbc no está disponible en el entorno; no se puede crear engine.")
        raise RuntimeError("pyodbc no está disponible en el entorno; use Google Sheets o instale pyodbc en el runtime")

    if _engine is None:
        params = (
            f"DRIVER={{{{ODBC Driver 17 for SQL Server}}}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
        conn_str = "mssql+pyodbc:///?odbc_connect=" + quote_plus(params)
        _engine = create_engine(conn_str)
    return _engine

def get_conn():
    """Obtiene conexión a SQL Server"""
    if not HAS_PYODBC:
        logger.error("pyodbc no está disponible en el entorno; no se puede conectar a SQL Server.")
        raise RuntimeError("pyodbc no está disponible en el entorno; use Google Sheets o instale pyodbc en el runtime")

    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        logger.error(f"Error conectando a SQL Server: {e}")
        raise

def query(sql):
    """Ejecuta query y retorna DataFrame"""
    try:
        engine = get_engine()
        df = pd.read_sql(sql, engine)
        return df
    except Exception as e:
        logger.error(f"Error en query: {e}")
        raise

def get_gsheet_client():
    """Obtiene cliente autenticado de Google Sheets (cacheado en Streamlit)"""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        # Support credentials provided as JSON in env (GOOGLE_CREDS_JSON)
        if GOOGLE_CREDS_JSON:
            import json
            creds_dict = json.loads(GOOGLE_CREDS_JSON)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client

        # Fallback to credentials file path
        if not os.path.exists(GOOGLE_CREDS_PATH):
            logger.error(f"Archivo de credenciales no encontrado: {GOOGLE_CREDS_PATH}")
            raise FileNotFoundError(f"Credenciales no encontradas en {GOOGLE_CREDS_PATH}")

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_CREDS_PATH,
            scope
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Error autenticando Google Sheets: {e}")
        raise

def insert_into_table(table, columns, values):
    """Inserta un registro en la tabla"""
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        placeholders = ",".join(["?"] * len(values))
        col_str = ",".join(columns)
        
        cursor.execute(
            f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        logger.info(f"Registro insertado en {table}")
        return True
    except Exception as e:
        logger.error(f"Error insertando en {table}: {e}")
        raise
    finally:
        if conn:
            conn.close()
