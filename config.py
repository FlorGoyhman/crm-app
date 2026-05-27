import pandas as pd

def query(sql_expression):
    sql_expression_clean = sql_expression.strip().lower()
    if "from partners" in sql_expression_clean:
        return pd.DataFrame({
            "partner_id": [1, 2, 3, 4, 5],
            "name": ["Distribuidora Alvear", "Logística Sur S.A.", "Comercializadora del Plata", "Mundo Retail", "Global Trading Inc"],
            "country": ["Argentina", "Argentina", "Uruguay", "Chile", "Brasil"],
            "status": ["Activo", "Activo", "Inactivo", "Activo", "Pendiente"]
        })
    elif "from orders" in sql_expression_clean:
        return pd.DataFrame({
            "order_id": [101, 102, 103, 104, 105],
            "product": ["Laptop Core i7", "Mouse Inalámbrico", "Monitor 24'", "Teclado Mecánico", "Impresora Láser"],
            "amount": [1200.50, 25.00, 300.75, 70.00, 180.00]
        })
    return pd.DataFrame()

def clean_dataframe_columns(df):
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

# --- SIMULACIÓN AVANZADA PARA EVITAR EL ERROR '.cursor()' ---
class CursorSimulado:
    def execute(self, *args, **kwargs): return True
    def commit(self): pass
    def close(self): pass

class ConexionSimulada:
    def cursor(self): return CursorSimulado()
    def commit(self): pass
    def close(self): pass

def get_conn():
    return ConexionSimulada()

def insert_into_table(query_string, data_tuple):
    return True
